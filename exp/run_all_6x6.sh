#!/usr/bin/env bash
# KSC2026 (first design, used for results/main_20261008): build -> wbuffix 6x6x3 -> analysis.
# (Until 2026-10-08 this script also ran the variant "base" first. base has the upstream write-buffer over-release
#  when bs < mapping unit; its results were removed at the user's request and it is no longer run.)
# usage: bash run_all_6x6.sh <EXP_NAME>        (run inside tmux; re-running resumes)
set -euo pipefail
cd "$(dirname "$0")"
EXP="${1:?usage: bash run_all_6x6.sh <EXP_NAME>}"
bash build_modules.sh wbuffix
bash run_experiment.sh "$EXP" wbuffix
./.venv/bin/python analyze.py "results/$EXP"
