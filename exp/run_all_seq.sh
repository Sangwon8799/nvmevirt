#!/usr/bin/env bash
# KSC2026 sequential-write experiment (results/seq3x3_*): mapping unit 4k/16k/32k x fio bs 4k/16k/32k x 3 reps,
# fio rw=write, page cache not dropped, two models:
#   wbuffix  the model of the random-write experiment (same module binaries as results/main3x3_*)
#   merge    wbuffix + write-buffer merge of writes smaller than the mapping unit (WBUF_MERGE=1)
# The two models alternate by repetition (rep 1 wbuffix, rep 1 merge, rep 2 wbuffix, ...).
# usage: bash run_all_seq.sh <EXP_NAME>        (run inside tmux; re-running resumes)
set -euo pipefail
cd "$(dirname "$0")"
EXP="${1:?usage: bash run_all_seq.sh <EXP_NAME>}"
export MAPS="4k 16k 32k" BSS="4k 16k 32k" CACHE_MODES=nodrop WORKLOAD=seqwrite
export NOMERGES="${NOMERGES:-2}"   # the device must see the fio bs: no block-layer merging of adjacent requests
for v in wbuffix merge; do   # .ko files are not in git: build what is missing
	ls modules/$v/nvmev_map{4k,16k,32k}.ko > /dev/null 2>&1 || bash build_modules.sh $v
done
for r in 1 2 3; do
	for v in wbuffix merge; do
		# runs with a DONE marker are skipped, so this adds repetition r (the "N runs" / "[i/N]" in the log count
		# repetitions 1..r, so each call ends at about [9/N] — expected)
		REPS=$r bash run_experiment.sh "$EXP" "$v"
	done
done
./.venv/bin/python analyze.py "results/$EXP"
