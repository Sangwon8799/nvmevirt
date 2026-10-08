#!/usr/bin/env bash
# KSC2026: whole experiment in one command (build -> base 108 runs -> wbuffix 108 runs -> analysis).
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
