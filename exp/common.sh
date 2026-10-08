#!/usr/bin/env bash
# KSC2026 NVMeVirt mapping-unit experiment — common settings and helpers.
# Sourced by build_modules.sh, run_experiment.sh and collect_env.sh.
# Every value can be overridden from the environment (e.g. REPS=1 bash run_experiment.sh ...).

EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$EXP_DIR/.." && pwd)"
NVMEV_SRC="$REPO_DIR/nvmevirt"

# ---- NVMeVirt module parameters (insmod) ----
MEMMAP_START="${MEMMAP_START:-12G}"   # GRUB_CMDLINE_LINUX: memmap=12G$12G  (reserve 12 GiB starting at 12 GiB)
MEMMAP_SIZE="${MEMMAP_SIZE:-12G}"
CPUS="${CPUS:-3,4,5}"                 # first = dispatcher, the rest = I/O workers (GRUB: isolcpus=3-5)

# ---- experiment matrix ----
MAPS="${MAPS:-4k 8k 16k 32k 64k 128k}"   # FTL mapping unit (make MAPPING_UNIT=...)
BSS="${BSS:-4k 8k 16k 32k 64k 128k}"     # fio block size
REPS="${REPS:-3}"                        # repetitions per (mapping unit, bs)

# ---- fio ----
IODEPTH="${IODEPTH:-32}"
RUNTIME="${RUNTIME:-60}"      # seconds, time_based
RAMP="${RAMP:-0}"             # ramp_time 0: keep the pre-GC part of every run
LOG_MSEC="${LOG_MSEC:-500}"   # bw/iops/lat time-series averaging window (ms)
SETTLE_SEC="${SETTLE_SEC:-5}" # idle seconds between insmod and fio

# ---- OS page cache before each run ----
# nodrop: nothing / drop: sync; echo 3 > /proc/sys/vm/drop_caches right after insmod (before SETTLE_SEC)
# "nodrop drop": both, back to back for every (map, bs, rep); the order alternates with rep (odd: nodrop first)
CACHE_MODES="${CACHE_MODES:-nodrop}"

# Expected NVMeVirt logical capacity: (12 GiB - 1 MiB) * 100 / 107 (OP 7 %), with some slack
DEV_MIN_BYTES=$(( 11 * 1024**3 ))
DEV_MAX_BYTES=$(( 12 * 1024**3 ))

log() { echo "[$(date '+%F %T')] $*"; }
die() { echo "[$(date '+%F %T')] ERROR: $*" >&2; exit 1; }

to_bytes() {   # 4k -> 4096, 1m -> 1048576
	local v="${1,,}"
	case "$v" in
	*k) echo $(( ${v%k} * 1024 )) ;;
	*m) echo $(( ${v%m} * 1024 * 1024 )) ;;
	*) echo "$v" ;;
	esac
}

# Build variants -> extra make arguments (all variants: conventional SSD, BLKS_PER_PLN 384, MAPPING_UNIT per module)
#   base     requested configuration + GC statistics logging (observational only; does not change timing)
#   wbuffix  base + write buffer holds whole mapping units (fixes over-release when bs < mapping unit)
#   plain    requested configuration without GC statistics (used to check that GC_STATS has no effect)
variant_make_args() {
	case "$1" in
	base) echo "GC_STATS=1" ;;
	wbuffix) echo "GC_STATS=1 WBUF_FIX=1" ;;
	plain) echo "" ;;
	*) die "unknown VARIANT '$1'" ;;
	esac
}
