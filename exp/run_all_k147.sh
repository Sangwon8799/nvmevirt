#!/usr/bin/env bash
# KSC2026, 2026-10-25: re-measurement on kernel 6.8.0-147 (the earlier fio results were taken on 6.8.0-142)
# followed by the RocksDB/YCSB-A experiment. One run per case, every run on a fresh (empty) NVMeVirt device.
#
#   1. rand4x3_k147_<D>       fio random write      map 4/8/16/32K x bs 4/16/32K, wbuffix                      12 runs
#   2. seq4x3_k147_<D>        fio sequential write  map 4/8/16/32K x bs 4/16/32K x {wbuffix, merge}, nomerges=2  24 runs
#   3. randbs_k147_<D>        fio random write      map 4/8/16/32K x bs 8/64K, wbuffix                           8 runs
#      rand4x5_k147_<D>       view (symlinks) of 1 + 3: map 4 x bs 5
#   4. rocksdb_ycsba_k147_<D> YCSB-A on ext4, map 4/8/16/32K x RocksDB block_size 4/8/16/32K x WAL off/on    32 runs
#                             (3,000,000 records, 1 client thread, WAL without fsync, 600 s run phase)
# fio settings: 120 s time_based, iodepth 32, libaio, O_DIRECT, page cache not dropped (nodrop),
#               block-layer merging as before (random: kernel default, sequential: nomerges=2).
#
# usage: bash run_all_k147.sh [DATE]       (inside tmux; re-running resumes — finished runs are skipped)
set -euo pipefail
# the whole body is one { ... } block: bash parses it before running, so editing this file later
# cannot change the running instance
{
cd "$(dirname "$0")"
D="${1:-20261025}"
LOG="results/run_all_k147_$D.log"
mkdir -p results
exec > >(tee -a "$LOG") 2>&1
echo "[$(date '+%F %T')] run_all_k147.sh start (date tag $D, git $(git rev-parse --short HEAD))"
[[ "$(uname -r)" == 6.8.0-147-generic ]] || { echo "kernel is $(uname -r), expected 6.8.0-147-generic" >&2; exit 1; }
for v in wbuffix merge; do
	ls modules/$v/nvmev_map{4k,8k,16k,32k}.ko > /dev/null || { echo "modules/$v is incomplete — bash build_modules.sh $v" >&2; exit 1; }
done

analyze() {   # analysis never stops the measurements
	./.venv/bin/python analyze.py "$1" || echo "[$(date '+%F %T')] WARNING: analyze.py $1 failed"
}

export REPS=1 RUNTIME=120 CACHE_MODES=nodrop MAPS="4k 8k 16k 32k"

# 1. random write 4 x 3
WORKLOAD=randwrite NOMERGES= BSS="4k 16k 32k" bash run_experiment.sh "rand4x3_k147_$D" wbuffix
# 2. sequential write 4 x 3 x 2 models
WORKLOAD=seqwrite NOMERGES=2 BSS="4k 16k 32k" bash run_experiment.sh "seq4x3_k147_$D" wbuffix
WORKLOAD=seqwrite NOMERGES=2 BSS="4k 16k 32k" bash run_experiment.sh "seq4x3_k147_$D" merge
# 3. random write bs 8K / 64K
WORKLOAD=randwrite NOMERGES= BSS="8k 64k" bash run_experiment.sh "randbs_k147_$D" wbuffix

analyze "results/rand4x3_k147_$D"
analyze "results/seq4x3_k147_$D"
analyze "results/randbs_k147_$D"
./.venv/bin/python link_runs.py "results/rand4x5_k147_$D" "results/rand4x3_k147_$D/wbuffix" "results/randbs_k147_$D/wbuffix" \
	|| echo "[$(date '+%F %T')] WARNING: link_runs.py failed"
analyze "results/rand4x5_k147_$D"
echo "[$(date '+%F %T')] fio part finished"

# 4. RocksDB / YCSB-A 4 x 4 x WAL off/on
RDB_MAPS="4k 8k 16k 32k" RDB_BLOCKS="4k 8k 16k 32k" RDB_WALS="off on" RECORDS=3000000 RUN_SEC=600 THREADS=1 \
	bash run_rocksdb_ycsb.sh "rocksdb_ycsba_k147_$D"
./.venv/bin/python rocksdb/analyze_rocksdb.py "results/rocksdb_ycsba_k147_$D" \
	|| echo "[$(date '+%F %T')] WARNING: analyze_rocksdb.py failed"
echo "[$(date '+%F %T')] run_all_k147.sh finished"
exit 0
}
