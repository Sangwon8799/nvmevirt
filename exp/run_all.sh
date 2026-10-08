#!/usr/bin/env bash
# KSC2026 (final design, results/main3x3_*): mapping unit 4k/16k/32k x fio bs 4k/16k/32k x 3 reps,
# wbuffix model, OS page cache dropped (drop) or not (nodrop) before every run, the two back to back.
# usage: bash run_all.sh <EXP_NAME>        (run inside tmux; re-running resumes)
set -euo pipefail
cd "$(dirname "$0")"
EXP="${1:?usage: bash run_all.sh <EXP_NAME>}"
export MAPS="4k 16k 32k" BSS="4k 16k 32k" REPS=3 CACHE_MODES="nodrop drop"
ls modules/wbuffix/nvmev_map{4k,16k,32k}.ko > /dev/null 2>&1 || bash build_modules.sh wbuffix   # .ko files are not in git
bash run_experiment.sh "$EXP" wbuffix
./.venv/bin/python analyze.py "results/$EXP"
