#!/usr/bin/env bash
# KSC2026 (first design, used for results/main_20261008): build -> base 6x6x3 -> wbuffix 6x6x3 -> analysis.
# usage: bash run_all.sh <EXP_NAME>        (run inside tmux; re-running resumes)
set -euo pipefail
cd "$(dirname "$0")"
EXP="${1:?usage: bash run_all.sh <EXP_NAME>}"
for v in base wbuffix; do
	bash build_modules.sh "$v"
done
for v in base wbuffix; do
	bash run_experiment.sh "$EXP" "$v"
done
./.venv/bin/python analyze.py "results/$EXP"
