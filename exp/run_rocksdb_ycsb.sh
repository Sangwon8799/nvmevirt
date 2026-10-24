#!/usr/bin/env bash
# KSC2026 RocksDB/YCSB-A experiment on the NVMeVirt conventional SSD.
#
# Matrix:  FTL mapping unit (RDB_MAPS) x RocksDB block_size (RDB_BLOCKS) x WAL (RDB_WALS: off = rocksdb.disablewal=true)
# Every run starts from an empty device:
#   rmmod nvmev (if loaded) -> insmod nvmev_map<MAP>.ko (fresh FTL) -> mkfs.ext4 /dev/nvme1n1 -> mount /mnt/jsw_nvmevirt
#   -> YCSB load: RECORDS records of workloada, THREADS threads, same WAL setting as the run
#   -> YCSB run:  workloada (50 % read / 50 % update, zipfian), THREADS threads, stopped after RUN_SEC s
#   -> copy RocksDB LOG / OPTIONS -> umount -> rmmod (NVMeVirt prints its GC statistics at rmmod)
# Order:   for MAP; for BLOCK; for WAL  (WAL off and on of the same pair run back to back)
#
# usage:   bash run_rocksdb_ycsb.sh <EXP_NAME>        (run inside tmux; re-running resumes, DONE/FAILED runs are skipped)
# results: exp/results/<EXP_NAME>/<VARIANT>/map<MAP>_blk<BLOCK>_wal<off|on>/
#   meta.txt             settings, versions, phase times, block-layer counters
#   load.txt / run.txt   YCSB summary ([OVERALL] / [READ] / [UPDATE] / [INSERT] lines, hdrhistogram percentiles)
#   load_status.txt / run_status.txt   YCSB status lines, one per second (stderr of YCSB)
#   blkstat_1s.txt       /sys/block/<dev>/stat once per second during load and run
#   rocksdb/             LOG*, OPTIONS-* of the DB; db_files_*.txt directory listings
#   kernel.log, dmesg_load.txt, dmesg_unload.txt (GC statistics), mkfs.txt, rocksdb_options.ini
#   result.json          parsed summary (exp/rocksdb/ycsb_parse.py)
# Privileged steps use 'sudo -n' and must match /etc/sudoers.d/nvmevirt-exp exactly (exp/report/nvmevirt-exp.sudoers).
set -euo pipefail
# the whole body is one { ... } block: bash parses it before running, so editing this file during a run
# cannot change the running instance
{
source "$(dirname "$0")/common.sh"

EXP="${1:?usage: bash run_rocksdb_ycsb.sh <EXP_NAME>}"
VARIANT="${VARIANT:-wbuffix}"
RDB_MAPS="${RDB_MAPS:-4k 8k 16k 32k}"
RDB_BLOCKS="${RDB_BLOCKS:-4k 8k 16k 32k}"
RDB_WALS="${RDB_WALS:-off on}"
RECORDS="${RECORDS:-3000000}"          # YCSB recordcount (about 1.1 KB per record: 10 fields x 100 B + key)
RUN_SEC="${RUN_SEC:-600}"              # YCSB maxexecutiontime of the run phase
THREADS="${THREADS:-1}"                # YCSB client threads
OPCOUNT="${OPCOUNT:-1000000000}"       # run-phase operationcount: large, so the time limit ends the run
CPU_LIST="${CPU_LIST:-0-2}"            # YCSB + RocksDB (NVMeVirt uses the isolated CPUs 3-5)
YCSB_HOME="${YCSB_HOME:-$HOME/jsw/ycsb-dist/ycsb-rocksdb-binding-0.18.0-SNAPSHOT}"
YCSB_SRC="${YCSB_SRC:-$HOME/jsw/YCSB}"
MNT="/mnt/jsw_nvmevirt"                # fixed: the sudoers rule names it
DEV_EXPECTED="nvme1n1"                 # fixed: the sudoers rule names /dev/nvme1n1
LOAD_TIMEOUT="${LOAD_TIMEOUT:-5400}"   # seconds
RUN_GRACE="${RUN_GRACE:-900}"          # seconds allowed beyond RUN_SEC
OUT="$EXP_DIR/results/$EXP"
VOUT="$OUT/$VARIANT"
MOD_DIR="$EXP_DIR/modules/$VARIANT"
OPT_TEMPLATE="$EXP_DIR/rocksdb/options.ini.in"
PARSER="$EXP_DIR/rocksdb/ycsb_parse.py"
read -r -a MAP_LIST <<< "$RDB_MAPS"
read -r -a BLK_LIST <<< "$RDB_BLOCKS"
read -r -a WAL_LIST <<< "$RDB_WALS"
ME="$(id -un)"
DEV=""
YCSB_CMD=()
KLOG_PID=""
SAMPLER_PID=""

# ------------------------------------------------------------------ helpers (same as run_experiment.sh)
kmark() {   # marker line in the kernel log (same clock as NVMeVirt's messages)
	echo "KSC2026-MARK $1" | sudo -n tee /dev/kmsg > /dev/null
}

dmesg_after() {   # kernel messages from marker $1 (inclusive) to the end
	sudo -n dmesg | awk -v m="KSC2026-MARK $1" 'index($0, m) { found = 1 } found { print }'
}

find_nvmev_dev() {   # prints nvmeXnY of the NVMeVirt namespace (model CSL_Virt_MN_01), or nothing
	local m found=()
	for m in /sys/block/nvme*n*/device/model; do
		[[ -e "$m" ]] || continue
		if grep -q '^CSL_Virt' "$m"; then found+=("$(basename "$(dirname "$(dirname "$m")")")"); fi
	done
	(( ${#found[@]} <= 1 )) || die "more than one NVMeVirt namespace: ${found[*]}"
	echo "${found[0]:-}"
}

check_target_dev() {   # refuse anything that is not exactly the NVMeVirt namespace; prints its size
	local d="$1" size root_src
	[[ "$(cat "/sys/block/$d/device/model" 2>/dev/null)" == CSL_Virt* ]] || die "/dev/$d is not an NVMeVirt device"
	size=$(( $(cat "/sys/block/$d/size") * 512 ))
	(( size >= DEV_MIN_BYTES && size <= DEV_MAX_BYTES )) || die "/dev/$d size $size B is outside the expected range"
	if compgen -G "/sys/block/$d/${d}p*" > /dev/null; then die "/dev/$d has partitions — refusing"; fi
	if lsblk -nro MOUNTPOINT "/dev/$d" | grep -q .; then die "/dev/$d is mounted — refusing"; fi
	root_src="$(findmnt -n -o SOURCE /)"
	[[ "$root_src" != "/dev/$d"* ]] || die "/dev/$d holds the root file system — refusing"
	echo "$size"
}

unload_nvmev() {
	grep -qs '^nvmev ' /proc/modules || return 0
	local d; d="$(find_nvmev_dev)"
	if [[ -n "$d" ]] && lsblk -nro MOUNTPOINT "/dev/$d" | grep -q .; then die "/dev/$d is mounted"; fi
	sudo -n rmmod nvmev
	for _ in $(seq 30); do grep -qs '^nvmev ' /proc/modules || break; sleep 1; done
	if grep -qs '^nvmev ' /proc/modules; then die "rmmod nvmev failed"; fi
	sleep 2
}

load_nvmev() {   # $1 = mapping unit (4k ...), $2 = run dir  -> sets DEV
	local map="$1" rdir="$2" ko="$MOD_DIR/nvmev_map$1.ko" d="" tag
	tag="$(basename "$rdir") insmod $(date +%s%N)"
	kmark "$tag"
	sudo -n insmod "$ko" memmap_start="$MEMMAP_START" memmap_size="$MEMMAP_SIZE" cpus="$CPUS"
	for _ in $(seq 60); do
		d="$(find_nvmev_dev)"
		[[ -n "$d" && -b "/dev/$d" ]] && break
		sleep 0.5
	done
	[[ -n "$d" && -b "/dev/$d" ]] || die "NVMeVirt block device did not appear after insmod (check dmesg)"
	sleep 1
	dmesg_after "$tag" > "$rdir/dmesg_load.txt"
	grep -q "KSC2026: mapping unit=$(to_bytes "$map") B" "$rdir/dmesg_load.txt" \
		|| die "dmesg does not confirm mapping unit $(to_bytes "$map") B — see $rdir/dmesg_load.txt"
	DEV="/dev/$d"
}

queue_line() {
	local q="/sys/block/$1/queue"
	echo "nomerges=$(cat "$q/nomerges") scheduler=$(cat "$q/scheduler" | xargs) max_sectors_kb=$(cat "$q/max_sectors_kb") write_cache=$(cat "$q/write_cache" | xargs) logical_block_size=$(cat "$q/logical_block_size")"
}

blkstat() {   # label + the 17 fields of /sys/block/<dev>/stat
	echo "$1 $EPOCHREALTIME $(cat "/sys/block/${DEV#/dev/}/stat" | xargs)"
}

meminfo_line() { awk '/^(MemFree|Buffers|Cached|Dirty|Writeback):/ { printf "%s%s kB ", $1, $2 }' /proc/meminfo; }

umount_if_mounted() {
	if mountpoint -q "$MNT"; then
		sync
		sudo -n /usr/bin/umount "$MNT"
	fi
}

stop_bg() {
	if [[ -n "$SAMPLER_PID" ]]; then kill "$SAMPLER_PID" 2> /dev/null || true; wait "$SAMPLER_PID" 2> /dev/null || true; SAMPLER_PID=""; fi
	if [[ -n "$KLOG_PID" ]]; then kill "$KLOG_PID" 2> /dev/null || true; wait "$KLOG_PID" 2> /dev/null || true; KLOG_PID=""; fi
}

ycsb_cmd() {   # sets YCSB_CMD: $1 = -load | -t, $2 = disablewal (true|false), $3 = options file, rest = extra arguments
	local phase="$1" dis="$2" opt="$3"
	shift 3
	YCSB_CMD=(taskset -c "$CPU_LIST" java -cp "$YCSB_HOME/lib/*" site.ycsb.Client "$phase"
		-db site.ycsb.db.rocksdb.RocksDBClient -P "$YCSB_HOME/workloads/workloada"
		-p recordcount="$RECORDS" -p rocksdb.dir="$MNT/db" -p rocksdb.optionsfile="$opt"
		-p rocksdb.disablewal="$dis" -p rocksdb.sync=false
		-p measurementtype=hdrhistogram -p hdrhistogram.percentiles=50,90,95,99,99.9,99.99
		-threads "$THREADS" -s -p status.interval=1 "$@")
}

fail_run() {   # $1 = run dir, $2 = reason: keep everything, mark FAILED, clean up the device, continue
	local rdir="$1"
	echo "$2" > "$rdir/FAILED"
	log "FAILED: $2 — kept as $rdir/FAILED, continuing"
	stop_bg
	umount_if_mounted || true
	unload_nvmev || true
	sudo -n chown -R "$ME:$ME" "$rdir" 2> /dev/null || true
}

# ------------------------------------------------------------------ one run
run_one() {   # $1 = mapping unit, $2 = RocksDB block size, $3 = off | on
	local map="$1" blk="$2" wal="$3" rdir size dis tag rc t0 t1 bsz
	rdir="$VOUT/map${map}_blk${blk}_wal${wal}"
	if [[ -f "$rdir/DONE" ]]; then log "skip (already done): $(basename "$rdir")"; return 0; fi
	if [[ -f "$rdir/FAILED" ]]; then log "skip (failed earlier, see FAILED): $(basename "$rdir")"; return 0; fi
	rm -rf "$rdir"
	mkdir -p "$rdir/rocksdb"
	tag="$(basename "$rdir")"
	if [[ "$wal" == off ]]; then dis=true; else dis=false; fi
	bsz=$(to_bytes "$blk")
	log "=== [$((++RUN_IDX))/$N_RUNS] variant=$VARIANT map=$map block_size=$blk wal=$wal ==="

	umount_if_mounted
	unload_nvmev
	sudo -n dmesg -W 2>&1 > >(awk -v cnt="$rdir/chmodel_msgs.txt" '
		/\[chmodel_request\]/ { n++; if (n <= 20) print; next }
		{ print; fflush() }
		END { print n + 0 > cnt }' > "$rdir/kernel.log") &
	KLOG_PID=$!
	sleep 0.5
	load_nvmev "$map" "$rdir"
	size=$(check_target_dev "${DEV#/dev/}")
	[[ "$DEV" == "/dev/$DEV_EXPECTED" ]] || die "NVMeVirt appeared as $DEV; the sudoers rule allows mkfs/mount only for /dev/$DEV_EXPECTED"
	! mountpoint -q "$MNT" || die "$MNT is already mounted"

	# fresh ext4 on the empty device (reserved memory keeps old bytes across rmmod/insmod, so mkfs every run)
	blkstat before_mkfs > "$rdir/blkstat_phases.txt"
	kmark "$tag mkfs"
	sudo -n /usr/sbin/mkfs.ext4 -F -m 0 -E lazy_itable_init=0,lazy_journal_init=0 "/dev/$DEV_EXPECTED" > "$rdir/mkfs.txt" 2>&1 \
		|| { fail_run "$rdir" "mkfs.ext4 failed (see mkfs.txt)"; return 0; }
	sudo -n /usr/bin/mount -o noatime "/dev/$DEV_EXPECTED" "$MNT" || { fail_run "$rdir" "mount failed"; return 0; }
	sudo -n /usr/bin/chown "$ME:$ME" "$MNT"
	[[ "$(findmnt -n -o SOURCE,FSTYPE "$MNT" | xargs)" == "/dev/$DEV_EXPECTED ext4" ]] || die "unexpected mount: $(findmnt -n "$MNT")"
	mkdir "$MNT/db"
	sed -e "s|@BLOCK_SIZE@|$bsz|g" "$OPT_TEMPLATE" > "$rdir/rocksdb_options.ini"

	{
		echo "variant:      $VARIANT"
		echo "workload:     YCSB workloada (read 0.5 / update 0.5, zipfian), recordcount=$RECORDS, threads=$THREADS"
		echo "map_unit:     $map ($(to_bytes "$map") B)"
		echo "block_size:   $blk ($bsz B)"
		echo "wal:          $wal (rocksdb.disablewal=$dis, rocksdb.sync=false)"
		echo "run_sec:      $RUN_SEC (maxexecutiontime; operationcount=$OPCOUNT)"
		echo "device:       $DEV  size=$size B  model=$(cat "/sys/block/${DEV#/dev/}/device/model" | xargs)"
		echo "module:       $(cd "$MOD_DIR" && sha256sum "nvmev_map$map.ko")"
		echo "insmod:       insmod nvmev_map$map.ko memmap_start=$MEMMAP_START memmap_size=$MEMMAP_SIZE cpus=$CPUS"
		echo "mkfs:         mkfs.ext4 -F -m 0 -E lazy_itable_init=0,lazy_journal_init=0 /dev/$DEV_EXPECTED ($(head -1 "$rdir/mkfs.txt"))"
		echo "mount:        $(findmnt -n -o SOURCE,TARGET,FSTYPE,OPTIONS "$MNT")"
		echo "blk_queue:    $(queue_line "${DEV#/dev/}")"
		echo "cpus:         taskset -c $CPU_LIST (YCSB + RocksDB); NVMeVirt cpus=$CPUS"
		echo "ycsb:         $YCSB_HOME ($(git -C "$YCSB_SRC" rev-parse --short HEAD 2> /dev/null || echo '?') $(git -C "$YCSB_SRC" rev-parse --abbrev-ref HEAD 2> /dev/null || echo '?')); $(basename "$(ls "$YCSB_HOME"/lib/rocksdbjni-*.jar)")"
		echo "java:         $(java -version 2>&1 | head -1)"
		echo "kernel:       $(uname -r)"
		echo "loadavg:      $(cat /proc/loadavg)"
		echo "mem:          $(meminfo_line)"
		echo "git_head:     $(git -C "$REPO_DIR" rev-parse HEAD)"
		echo "start:        $(date -Is)"
	} > "$rdir/meta.txt"

	# block-layer counters once per second for the whole load + run
	( d="/sys/block/${DEV#/dev/}/stat"
	  while :; do read -r -a s < "$d"; echo "$EPOCHREALTIME ${s[*]}"; sleep 1; done ) > "$rdir/blkstat_1s.txt" &
	SAMPLER_PID=$!

	# ---- load
	blkstat before_load >> "$rdir/blkstat_phases.txt"
	kmark "$tag load-start"
	t0=$EPOCHREALTIME
	rc=0
	ycsb_cmd -load "$dis" "$rdir/rocksdb_options.ini"
	echo "load_cmd:     ${YCSB_CMD[*]}" >> "$rdir/meta.txt"
	timeout --kill-after=60 "$LOAD_TIMEOUT" "${YCSB_CMD[@]}" > "$rdir/load.txt" 2> "$rdir/load_status.txt" || rc=$?
	t1=$EPOCHREALTIME
	kmark "$tag load-end"
	blkstat after_load >> "$rdir/blkstat_phases.txt"
	{
		echo "load_exit:    $rc"
		echo "load_wall_s:  $(python3 -c "print(round($t1 - $t0, 3))")"
		echo "df_after_load: $(df -B1 --output=used,avail "$MNT" | tail -1 | xargs)"
		echo "db_after_load: $(du -sb "$MNT/db" | cut -f1) B"
	} >> "$rdir/meta.txt"
	ls -l --time-style=+%s "$MNT/db" > "$rdir/rocksdb/db_files_after_load.txt"
	if [[ $rc -ne 0 ]]; then fail_run "$rdir" "YCSB load exited with $rc (see load.txt, load_status.txt)"; return 0; fi

	# ---- run
	blkstat before_run >> "$rdir/blkstat_phases.txt"
	echo "mem_before_run: $(meminfo_line)" >> "$rdir/meta.txt"
	kmark "$tag run-start"
	t0=$EPOCHREALTIME
	rc=0
	ycsb_cmd -t "$dis" "$rdir/rocksdb_options.ini" -p operationcount="$OPCOUNT" -p maxexecutiontime="$RUN_SEC"
	echo "run_cmd:      ${YCSB_CMD[*]}" >> "$rdir/meta.txt"
	timeout --kill-after=60 "$((RUN_SEC + RUN_GRACE))" "${YCSB_CMD[@]}" > "$rdir/run.txt" 2> "$rdir/run_status.txt" || rc=$?
	t1=$EPOCHREALTIME
	kmark "$tag run-end"
	blkstat after_run >> "$rdir/blkstat_phases.txt"
	{
		echo "run_exit:     $rc"
		echo "run_wall_s:   $(python3 -c "print(round($t1 - $t0, 3))")"
		echo "df_after_run: $(df -B1 --output=used,avail "$MNT" | tail -1 | xargs)"
		echo "db_after_run: $(du -sb "$MNT/db" | cut -f1) B"
		echo "mem_after_run: $(meminfo_line)"
	} >> "$rdir/meta.txt"
	ls -l --time-style=+%s "$MNT/db" > "$rdir/rocksdb/db_files_after_run.txt"
	kill "$SAMPLER_PID" 2> /dev/null || true; wait "$SAMPLER_PID" 2> /dev/null || true; SAMPLER_PID=""
	cp "$MNT"/db/LOG* "$MNT"/db/OPTIONS-* "$rdir/rocksdb/" 2> /dev/null || true
	if [[ $rc -ne 0 ]]; then fail_run "$rdir" "YCSB run exited with $rc (see run.txt, run_status.txt)"; return 0; fi

	# ---- tear down: umount, rmmod (GC statistics)
	kmark "$tag umount"
	umount_if_mounted
	blkstat after_umount >> "$rdir/blkstat_phases.txt"
	kmark "$tag rmmod"
	unload_nvmev
	sleep 0.5
	stop_bg
	for _ in $(seq 120); do [[ -s "$rdir/chmodel_msgs.txt" ]] && break; sleep 0.5; done
	awk -v b="KSC2026-MARK $tag rmmod" 'index($0, b) { s = 1 } s { print }' "$rdir/kernel.log" > "$rdir/dmesg_unload.txt"
	{
		echo "chmodel_msgs: $(cat "$rdir/chmodel_msgs.txt" 2> /dev/null || echo NA)"
		echo "kernel_warn:  $(grep -v -e KSC2026 -e '\[chmodel_request\]' "$rdir/kernel.log" | grep -ciE 'WARNING|almost full|timeout|reset|Oops|BUG|I/O error|Disk read failed|EXT4-fs error' || true)"
		echo "end:          $(date -Is)"
	} >> "$rdir/meta.txt"
	sudo -n chown -R "$ME:$ME" "$rdir"

	# ---- parse + sanity checks (every read/update found its record, the run lasted RUN_SEC)
	if ! python3 "$PARSER" "$rdir" --min-run-s "$(( RUN_SEC * 95 / 100 ))" > "$rdir/parse_check.txt" 2>&1; then
		echo "result check failed: $(tail -3 "$rdir/parse_check.txt" | xargs)" > "$rdir/FAILED"
		log "FAILED: result check (see parse_check.txt), continuing"
		return 0
	fi
	log "    -> $(tail -1 "$rdir/parse_check.txt")"
	touch "$rdir/DONE"
}

# ------------------------------------------------------------------ preflight
command -v java > /dev/null || die "java not found"
command -v taskset > /dev/null || die "taskset not found"
ls "$YCSB_HOME"/lib/rocksdbjni-11.8.1.jar > /dev/null 2>&1 || die "YCSB package with rocksdbjni 11.8.1 not found in $YCSB_HOME"
[[ -f "$OPT_TEMPLATE" && -f "$PARSER" ]] || die "missing $OPT_TEMPLATE or $PARSER"
[[ -d "$MNT" ]] || die "$MNT does not exist (sudo mkdir -p $MNT)"
! mountpoint -q "$MNT" || die "$MNT is mounted — unmount it first"
# the sudoers rule must allow umount of $MNT without a password: expect umount's own 'not mounted' message
pre="$(sudo -n /usr/bin/umount "$MNT" 2>&1 || true)"
[[ "$pre" == *"not mounted"* ]] || die "sudo -n umount $MNT: '$pre' — install /etc/sudoers.d/nvmevirt-exp first"
grep -qF "memmap=${MEMMAP_SIZE}\$${MEMMAP_START}" /proc/cmdline || die "kernel command line lacks memmap=${MEMMAP_SIZE}\$${MEMMAP_START}"
for m in "${MAP_LIST[@]}"; do
	[[ -f "$MOD_DIR/nvmev_map$m.ko" ]] || die "missing $MOD_DIR/nvmev_map$m.ko — run: bash build_modules.sh $VARIANT"
	[[ "$(modinfo -F vermagic "$MOD_DIR/nvmev_map$m.ko" | awk '{print $1}')" == "$(uname -r)" ]] || die "nvmev_map$m.ko was not built for $(uname -r)"
done
(cd "$MOD_DIR" && sha256sum -c --quiet SHA256SUMS) || die "module checksum mismatch in $MOD_DIR"
for w in "${WAL_LIST[@]}"; do [[ "$w" == off || "$w" == on ]] || die "RDB_WALS: unknown '$w'"; done
if [[ -n "$(find_nvmev_dev)" && "$(find_nvmev_dev)" != "$DEV_EXPECTED" ]]; then die "NVMeVirt is loaded as $(find_nvmev_dev), not $DEV_EXPECTED"; fi
[[ ! -e "/dev/$DEV_EXPECTED" || -n "$(find_nvmev_dev)" ]] || die "/dev/$DEV_EXPECTED exists and is not NVMeVirt — refusing"

N_RUNS=$(( ${#MAP_LIST[@]} * ${#BLK_LIST[@]} * ${#WAL_LIST[@]} ))
RUN_IDX=0
mkdir -p "$VOUT"
exec > >(tee -a "$VOUT/run.log") 2>&1
trap 'stop_bg; pkill -u "$ME" -f "site.ycsb.Client" 2> /dev/null || true; umount_if_mounted 2> /dev/null || true; sudo -n chown -R "$ME:$ME" "$OUT" 2> /dev/null || true' EXIT

log "experiment=$EXP variant=$VARIANT maps=[$RDB_MAPS] blocks=[$RDB_BLOCKS] wals=[$RDB_WALS] records=$RECORDS run=${RUN_SEC}s threads=$THREADS"
log "insmod memmap_start=$MEMMAP_START memmap_size=$MEMMAP_SIZE cpus=$CPUS; YCSB on cpus $CPU_LIST; $N_RUNS runs"

[[ -d "$OUT/env_before" ]] || bash "$EXP_DIR/collect_env.sh" "$OUT/env_before"
cp "$MOD_DIR/SHA256SUMS" "$VOUT/modules_SHA256SUMS"
cp "$MOD_DIR/build_info.txt" "$VOUT/modules_build_info.txt"
cp "$OPT_TEMPLATE" "$VOUT/"
echo "$(date -Is) $(git -C "$REPO_DIR" rev-parse HEAD)" >> "$VOUT/git_head.txt"
git -C "$YCSB_SRC" log -1 --format='%H %ad %s' > "$VOUT/ycsb_commit.txt" 2> /dev/null || true
cp "$YCSB_HOME/workloads/workloada" "$VOUT/ycsb_workloada"

for m in "${MAP_LIST[@]}"; do
	for b in "${BLK_LIST[@]}"; do
		for w in "${WAL_LIST[@]}"; do run_one "$m" "$b" "$w"; done
	done
done

unload_nvmev
bash "$EXP_DIR/collect_env.sh" "$OUT/env_after_$VARIANT"
log "finished: $VOUT"
exit 0
}
