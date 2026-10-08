#!/usr/bin/env bash
# KSC2026 random-write extension (results/randbs_*): fio bs 8k and 64k on mapping units 4k/16k/32k x 3 reps,
# wbuffix model, page cache not dropped, block-layer settings as in results/main3x3_* (kernel default).
# The 3x3 combinations (bs 4k/16k/32k) are not measured again: link_runs.py puts the new runs next to the
# nodrop runs of the primary data set in a combined view (results/rand3x5_*: mapping 3 x bs 5).
# usage: bash run_all_rand_bs.sh <EXP_NAME> [PRIMARY_EXP] [VIEW_NAME]     (run inside tmux; re-running resumes)
set -euo pipefail
cd "$(dirname "$0")"
EXP="${1:?usage: bash run_all_rand_bs.sh <EXP_NAME> [PRIMARY_EXP] [VIEW_NAME]}"
PRIMARY="${2:-main3x3_20261008}"
VIEW="${3:-rand3x5_${EXP##*_}}"
export MAPS="4k 16k 32k" BSS="8k 64k" REPS=3 CACHE_MODES=nodrop WORKLOAD=randwrite NOMERGES=
ls modules/wbuffix/nvmev_map{4k,16k,32k}.ko > /dev/null 2>&1 || bash build_modules.sh wbuffix   # .ko files are not in git
bash run_experiment.sh "$EXP" wbuffix
./.venv/bin/python analyze.py "results/$EXP"
./.venv/bin/python link_runs.py "results/$VIEW" "results/$PRIMARY/wbuffix_nodrop" "results/$EXP/wbuffix"
./.venv/bin/python analyze.py "results/$VIEW"
