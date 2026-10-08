#!/usr/bin/env bash
# Build nvmev.ko once per FTL mapping unit:
#   exp/modules/<VARIANT>/nvmev_map<MAP>.ko  (+ build_map<MAP>.log, SHA256SUMS, build_info.txt)
# usage: bash build_modules.sh [VARIANT]      (VARIANT: base | wbuffix | merge | plain, see common.sh)
set -euo pipefail
source "$(dirname "$0")/common.sh"

VARIANT="${1:-base}"
OUT="$EXP_DIR/modules/$VARIANT"
EXTRA_MAKE_ARGS="$(variant_make_args "$VARIANT")"
read -r -a MAP_LIST <<< "$MAPS"
mkdir -p "$OUT"

{
	echo "date:            $(date -Is)"
	echo "variant:         $VARIANT (extra make args: '${EXTRA_MAKE_ARGS}')"
	echo "kernel:          $(uname -r)"
	echo "compiler:        $(gcc --version | head -1)"
	echo "kernel built by: $(sed -E 's/.*\((x86_64-linux-gnu-gcc[^)]*\)).*/\1/' /proc/version)"
	echo "make:            $(make --version | head -1)"
	echo "git HEAD:        $(git -C "$REPO_DIR" rev-parse HEAD)"
	echo "git status (nvmevirt/): $(git -C "$REPO_DIR" status --porcelain -- nvmevirt | wc -l) modified file(s)"
	echo
} > "$OUT/build_info.txt"
: > "$OUT/SHA256SUMS"

for m in "${MAP_LIST[@]}"; do
	b=$(to_bytes "$m")
	log "build nvmev.ko  MAPPING_UNIT=$b ($m)  variant=$VARIANT"
	make -C "$NVMEV_SRC" clean > "$OUT/build_map$m.log" 2>&1
	# shellcheck disable=SC2086
	make -C "$NVMEV_SRC" MAPPING_UNIT="$b" $EXTRA_MAKE_ARGS >> "$OUT/build_map$m.log" 2>&1 \
		|| die "build failed — see $OUT/build_map$m.log"
	cp "$NVMEV_SRC/nvmev.ko" "$OUT/nvmev_map$m.ko"
	(cd "$OUT" && sha256sum "nvmev_map$m.ko" >> SHA256SUMS)
	{
		echo "## nvmev_map$m.ko  (make MAPPING_UNIT=$b $EXTRA_MAKE_ARGS)"
		modinfo "$OUT/nvmev_map$m.ko" | grep -E '^(srcversion|vermagic):'
	} >> "$OUT/build_info.txt"
done
make -C "$NVMEV_SRC" clean > /dev/null 2>&1
log "done -> $OUT"
cat "$OUT/SHA256SUMS"
