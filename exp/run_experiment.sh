#!/usr/bin/env bash
# KSC2026: NVMeVirt FTL mapping unit x fio block size write experiment (random or sequential, WORKLOAD in common.sh).
#
# Every run:  (rmmod nvmev if loaded) -> insmod nvmev_map<MAP>.ko (fresh FTL state = formatted device)
#             -> fio <WORKLOAD> bs=<BS>, iodepth 32, 60 s, ramp_time 0 (pre-GC part included) -> rmmod nvmev
# Order:      for rep in 1..REPS; for MAP in MAPS; for BS in BSS; for cache mode in CACHE_MODES (order alternates by rep)
#
# usage:  bash run_experiment.sh <EXP_NAME> [VARIANT]
#   - runs as the normal user; privileged steps use 'sudo -n' (/etc/sudoers.d/nvmevirt-exp)
#   - modules must be built first:  bash build_modules.sh [VARIANT]
#   - results: exp/results/<EXP_NAME>/<VARIANT>/map<MAP>_bs<BS>_r<REP>/   (CACHE_MODES=nodrop, default)
#              exp/results/<EXP_NAME>/<VARIANT>_<nodrop|drop>/...          (any other CACHE_MODES)
#   - re-running the same command resumes: runs with a DONE or FAILED marker are skipped
#   - a run whose fio fails (I/O errors, watchdog) gets a FAILED marker and the experiment continues
#   - ONLY_BS_LT_MAP=1 runs only the (MAP, BS) pairs with BS < MAP
set -euo pipefail
source "$(dirname "$0")/common.sh"

EXP="${1:?usage: bash run_experiment.sh <EXP_NAME> [VARIANT]}"
VARIANT="${2:-base}"
ONLY_BS_LT_MAP="${ONLY_BS_LT_MAP:-0}"
OUT="$EXP_DIR/results/$EXP"
read -r -a CM_LIST <<< "$CACHE_MODES"
vout_of() {   # result directory for cache mode $1
	if [[ "$CACHE_MODES" == nodrop ]]; then echo "$OUT/$VARIANT"; else echo "$OUT/${VARIANT}_$1"; fi
}
VOUTS=()
for cm in "${CM_LIST[@]}"; do
	[[ "$cm" == nodrop || "$cm" == drop ]] || { echo "CACHE_MODES: unknown mode '$cm'" >&2; exit 1; }
	VOUTS+=("$(vout_of "$cm")")
done
MOD_DIR="$EXP_DIR/modules/$VARIANT"
JOB_TEMPLATE="$EXP_DIR/jobs/$WORKLOAD.fio.in"
[[ -f "$JOB_TEMPLATE" ]] || { echo "WORKLOAD: no job template $JOB_TEMPLATE" >&2; exit 1; }
[[ -z "$NOMERGES" || "$NOMERGES" =~ ^[012]$ ]] || { echo "NOMERGES must be empty, 0, 1 or 2" >&2; exit 1; }
UPSTREAM_COMMIT=61c90f7758cbd9545b4a4727e89377bf88eab060
FIO_GRACE="${FIO_GRACE:-180}"   # seconds allowed beyond RUNTIME before fio is stopped (nvme timeout 30 s + abort + reset)
read -r -a MAP_LIST <<< "$MAPS"
read -r -a BS_LIST <<< "$BSS"
ME="$(id -un)"
DEV=""

# ------------------------------------------------------------------ helpers
kmark() {   # write a marker line into the kernel log (same clock as NVMeVirt's messages)
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

queue_line() {   # block-layer settings of the NVMeVirt namespace
	local q="/sys/block/$1/queue"
	echo "nomerges=$(cat "$q/nomerges") scheduler=$(cat "$q/scheduler" | xargs) max_sectors_kb=$(cat "$q/max_sectors_kb") write_cache=$(cat "$q/write_cache" | xargs)"
}

blk_wr_stat() {   # /sys/block/<dev>/stat fields 5-7: write I/Os, write merges, write sectors
	awk '{ print $5, $6, $7 }' "/sys/block/$1/stat"
}

meminfo_line() { awk '/^(MemFree|Buffers|Cached|Dirty|Writeback):/ { printf "%s%s kB ", $1, $2 }' /proc/meminfo; }

run_one() {   # $1 = mapping unit, $2 = bs, $3 = repetition, $4 = cache mode (nodrop | drop)
	local map="$1" bs="$2" r="$3" cm="${4:-nodrop}" rdir size rc=0 tag_fio tag_un n_chm n_warn fio_pid waited=0 jerr
	local wr_ios0 wr_mrg0 wr_sec0 wr_ios1 wr_mrg1 wr_sec1
	rdir="$(vout_of "$cm")/map${map}_bs${bs}_r${r}"
	if [[ -f "$rdir/DONE" ]]; then log "skip (already done): $(basename "$rdir")"; return 0; fi
	if [[ -f "$rdir/FAILED" ]]; then log "skip (failed earlier, see FAILED): $(basename "$rdir")"; return 0; fi
	rm -rf "$rdir"
	mkdir -p "$rdir"
	log "=== [$((++RUN_IDX))/$N_RUNS] variant=$VARIANT cache=$cm map=$map bs=$bs rep=$r ==="

	unload_nvmev                     # rmmod: make sure no previous FTL state is left
	# Follow the kernel log for the whole run: NVMeVirt's '[chmodel_request] Need to increase array size'
	# error flood (bs < mapping unit, base variant) can overwrite the 256 KiB ring buffer. Those lines are
	# counted on the fly (first 20 kept) so kernel.log stays small.
	sudo -n dmesg -W 2>&1 > >(awk -v cnt="$rdir/chmodel_msgs.txt" '
		/\[chmodel_request\]/ { n++; if (n <= 20) print; next }
		{ print; fflush() }
		END { print n + 0 > cnt }' > "$rdir/kernel.log") &
	KLOG_PID=$!
	sleep 0.5
	load_nvmev "$map" "$rdir"        # insmod: fresh (empty) device
	size=$(check_target_dev "${DEV#/dev/}")
	if [[ -n "$NOMERGES" ]]; then
		echo "$NOMERGES" | sudo -n tee "/sys/block/${DEV#/dev/}/queue/nomerges" > /dev/null \
			|| die "could not set /sys/block/${DEV#/dev/}/queue/nomerges (sudoers rule?)"
	fi

	# OS page cache: the NVMeVirt device is used with O_DIRECT, so this only changes the host's memory state
	{ echo "cache_mode: $cm"; echo "before: $(meminfo_line)"; } > "$rdir/cache.txt"
	if [[ "$cm" == drop ]]; then
		sync
		echo 3 | sudo -n tee /proc/sys/vm/drop_caches > /dev/null
		echo "dropped: sync; echo 3 > /proc/sys/vm/drop_caches at $(date -Is)" >> "$rdir/cache.txt"
	fi
	echo "after:  $(meminfo_line)" >> "$rdir/cache.txt"

	sed -e "s|@DEV@|$DEV|g" -e "s|@BS@|$bs|g" -e "s|@IODEPTH@|$IODEPTH|g" \
		-e "s|@RUNTIME@|$RUNTIME|g" -e "s|@RAMP@|$RAMP|g" -e "s|@LOG_MSEC@|$LOG_MSEC|g" \
		-e "s|@LOG_PREFIX@|$rdir/fio|g" "$JOB_TEMPLATE" > "$rdir/job.fio"

	{
		echo "variant:      $VARIANT"
		echo "workload:     $WORKLOAD ($(grep -m1 '^rw=' "$rdir/job.fio"))"
		echo "cache_mode:   $cm"
		echo "map_unit:     $map ($(to_bytes "$map") B)"
		echo "bs:           $bs ($(to_bytes "$bs") B)"
		echo "rep:          $r"
		echo "device:       $DEV  size=$size B  model=$(cat "/sys/block/${DEV#/dev/}/device/model" | xargs)"
		echo "module:       $(cd "$MOD_DIR" && sha256sum "nvmev_map$map.ko")"
		echo "insmod:       insmod nvmev_map$map.ko memmap_start=$MEMMAP_START memmap_size=$MEMMAP_SIZE cpus=$CPUS"
		echo "fio:          fio --output-format=json --output=fio.json job.fio"
		echo "blk_queue:    $(queue_line "${DEV#/dev/}")"
		echo "loadavg:      $(cat /proc/loadavg)"
		echo "git_head:     $(git -C "$REPO_DIR" rev-parse HEAD)"
		echo "start:        $(date -Is)"
	} > "$rdir/meta.txt"

	sleep "$SETTLE_SEC"
	echo "pre_fio: $(meminfo_line)" >> "$rdir/cache.txt"
	tag_fio="$(basename "$rdir") fio-start $(date +%s%N)"
	read -r wr_ios0 wr_mrg0 wr_sec0 <<< "$(blk_wr_stat "${DEV#/dev/}")"
	kmark "$tag_fio"                 # GC onset is measured from this kernel-log timestamp
	sudo -n fio --output-format=json --output="$rdir/fio.json" "$rdir/job.fio" > "$rdir/fio_stdout.txt" 2>&1 &
	fio_pid=$!
	while kill -0 "$fio_pid" 2> /dev/null; do   # watchdog: fio must end within RUNTIME + FIO_GRACE
		sleep 1
		waited=$((waited + 1))
		if (( waited == RUNTIME + FIO_GRACE )); then
			echo "watchdog: SIGTERM to fio after ${waited} s" >> "$rdir/fio_stdout.txt"
			kill -TERM "$fio_pid" 2> /dev/null || true
		elif (( waited == RUNTIME + FIO_GRACE + 60 )); then
			echo "watchdog: SIGKILL to fio after ${waited} s" >> "$rdir/fio_stdout.txt"
			kill -KILL "$fio_pid" 2> /dev/null || true
		fi
	done
	wait "$fio_pid" || rc=$?
	kmark "$(basename "$rdir") fio-end"
	read -r wr_ios1 wr_mrg1 wr_sec1 <<< "$(blk_wr_stat "${DEV#/dev/}")"

	tag_un="$(basename "$rdir") rmmod $(date +%s%N)"
	kmark "$tag_un"
	unload_nvmev                     # rmmod right after the run (GC statistics are printed here)
	sleep 0.5
	kill "$KLOG_PID" 2> /dev/null || true
	wait "$KLOG_PID" 2> /dev/null || true
	KLOG_PID=""
	for _ in $(seq 120); do [[ -s "$rdir/chmodel_msgs.txt" ]] && break; sleep 0.5; done   # awk flushes at EOF
	sudo -n chown -R "$ME:$ME" "$rdir"

	# split the followed kernel log: run section (without channel-model overflow lines) / rmmod section
	awk -v a="KSC2026-MARK $tag_fio" -v b="KSC2026-MARK $tag_un" -v run="$rdir/dmesg_run.txt" -v un="$rdir/dmesg_unload.txt" '
		index($0, a) { s = 1 }
		index($0, b) { s = 2 }
		s == 1 && !/\[chmodel_request\]/ { print > run }
		s == 2 { print > un }' "$rdir/kernel.log"
	touch "$rdir/dmesg_run.txt" "$rdir/dmesg_unload.txt"
	n_chm=$(cat "$rdir/chmodel_msgs.txt" 2> /dev/null || echo NA)
	n_warn=$(grep -v -e KSC2026 -e '\[chmodel_request\]' "$rdir/kernel.log" \
		| grep -ciE 'WARNING|almost full|timeout|reset|Oops|BUG|I/O error|Disk read failed' || true)
	{
		echo "end:          $(date -Is)"
		echo "blk_writes:   ios=$((wr_ios1 - wr_ios0)) merges=$((wr_mrg1 - wr_mrg0)) sectors=$((wr_sec1 - wr_sec0))   (block layer, /sys/block/<dev>/stat during fio)"
		echo "fio_exit:     $rc"
		echo "chmodel_msgs: $n_chm   (NVMeVirt '[chmodel_request]' errors seen by dmesg -W: NAND backlog beyond the channel-model window)"
		echo "kernel_warn:  $n_warn   (kernel.log lines matching WARNING|almost full|timeout|reset|Oops|BUG|I/O error|Disk read failed, excluding chmodel/KSC2026 lines)"
	} >> "$rdir/meta.txt"

	jerr=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["jobs"][0]["error"])' "$rdir/fio.json" 2> /dev/null || echo NA)
	if [[ $rc -ne 0 || "$jerr" != 0 ]]; then
		{
			echo "fio_exit=$rc fio_json_error=$jerr kernel_warn=$n_warn chmodel_msgs=$n_chm"
			grep -v -e '\[chmodel_request\]' "$rdir/kernel.log" | grep -iE 'almost full|timeout|reset|disable|I/O error' | head -20
		} > "$rdir/FAILED"
		log "FAILED (fio exit $rc, json error $jerr) — kept as $rdir/FAILED, continuing"
		return 0
	fi
	if grep -v KSC2026 "$rdir/dmesg_run.txt" | grep -qiE 'error|bug|oops|warn'; then
		log "WARNING: kernel messages during the run — see $rdir/dmesg_run.txt"
	fi
	if [[ "$n_chm" != 0 ]]; then log "NOTE: $n_chm channel-model overflow messages (first 20 in kernel.log)"; fi
	if [[ "$n_warn" != 0 ]]; then log "NOTE: $n_warn kernel warning line(s) — see $rdir/kernel.log"; fi
	python3 - "$rdir/fio.json" <<'PY'
import json, sys
w = json.load(open(sys.argv[1]))["jobs"][0]["write"]
print(f"    -> {w['bw'] / 1024:.1f} MiB/s, {w['iops']:.0f} IOPS, clat mean {w['clat_ns']['mean'] / 1000:.1f} us")
PY
	touch "$rdir/DONE"
}

# ------------------------------------------------------------------ preflight
PRIV=(/usr/sbin/insmod /usr/sbin/rmmod /usr/bin/fio /usr/bin/dmesg "/usr/bin/tee /dev/kmsg")
[[ " ${CM_LIST[*]} " == *" drop "* ]] && PRIV+=("/usr/bin/tee /proc/sys/vm/drop_caches")
for c in "${PRIV[@]}"; do
	# shellcheck disable=SC2086
	sudo -n -l $c > /dev/null 2>&1 || die "'sudo -n $c' is not allowed — install /etc/sudoers.d/nvmevirt-exp first"
done
grep -qF "memmap=${MEMMAP_SIZE}\$${MEMMAP_START}" /proc/cmdline \
	|| die "kernel command line lacks memmap=${MEMMAP_SIZE}\$${MEMMAP_START}"
for m in "${MAP_LIST[@]}"; do
	[[ -f "$MOD_DIR/nvmev_map$m.ko" ]] || die "missing $MOD_DIR/nvmev_map$m.ko — run: bash build_modules.sh $VARIANT"
done
(cd "$MOD_DIR" && sha256sum -c --quiet SHA256SUMS) || die "module checksum mismatch in $MOD_DIR"

PAIRS=()
for m in "${MAP_LIST[@]}"; do
	for bs in "${BS_LIST[@]}"; do
		if [[ "$ONLY_BS_LT_MAP" == 1 ]] && (( $(to_bytes "$bs") >= $(to_bytes "$m") )); then continue; fi
		PAIRS+=("$m $bs")
	done
done
N_RUNS=$(( REPS * ${#PAIRS[@]} * ${#CM_LIST[@]} ))
RUN_IDX=0

mkdir -p "${VOUTS[@]}"
exec > >(tee -a "${VOUTS[@]/%//run.log}") 2>&1
KLOG_PID=""
trap '[[ -n "$KLOG_PID" ]] && kill "$KLOG_PID" 2> /dev/null; sudo -n chown -R "$ME:$ME" "$OUT" 2> /dev/null || true' EXIT

log "experiment=$EXP variant=$VARIANT maps=[$MAPS] bss=[$BSS] reps=$REPS cache_modes=[$CACHE_MODES] only_bs_lt_map=$ONLY_BS_LT_MAP"
log "fio: libaio $WORKLOAD iodepth=$IODEPTH runtime=${RUNTIME}s ramp_time=${RAMP}s log=${LOG_MSEC}ms; insmod memmap_start=$MEMMAP_START memmap_size=$MEMMAP_SIZE cpus=$CPUS"
log "block layer: nomerges=${NOMERGES:-kernel default}"
log "$N_RUNS runs, about $(( N_RUNS * (RUNTIME + SETTLE_SEC + 8) / 60 )) min"

[[ -d "$OUT/env_before" ]] || bash "$EXP_DIR/collect_env.sh" "$OUT/env_before"
MOVE_COMMIT=$(git -C "$REPO_DIR" log --format=%H --grep='^Move NVMeVirt sources into nvmevirt/' -1)
for VOUT in "${VOUTS[@]}"; do
	cp "$MOD_DIR/SHA256SUMS" "$VOUT/modules_SHA256SUMS"
	cp "$MOD_DIR/build_info.txt" "$VOUT/modules_build_info.txt"
	cp "$JOB_TEMPLATE" "$VOUT/"
	echo "$(date -Is) $(git -C "$REPO_DIR" rev-parse HEAD)" >> "$VOUT/git_head.txt"   # one line per invocation
	git -C "$REPO_DIR" diff "$MOVE_COMMIT" HEAD -- nvmevirt > "$VOUT/nvmevirt_vs_upstream.diff"   # upstream + pure rename -> HEAD
	git -C "$REPO_DIR" diff -- nvmevirt > "$VOUT/nvmevirt_uncommitted.diff"
done

for r in $(seq "$REPS"); do
	for p in "${PAIRS[@]}"; do
		read -r m bs <<< "$p"
		order=("${CM_LIST[@]}")
		if (( r % 2 == 0 )); then   # even repetitions: reversed order, so neither mode always runs first
			order=()
			for (( i = ${#CM_LIST[@]} - 1; i >= 0; i-- )); do order+=("${CM_LIST[i]}"); done
		fi
		for cm in "${order[@]}"; do run_one "$m" "$bs" "$r" "$cm"; done
	done
done

unload_nvmev
bash "$EXP_DIR/collect_env.sh" "$OUT/env_after_$VARIANT"
log "finished: ${VOUTS[*]}"
