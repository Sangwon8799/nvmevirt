# NVMeVirt — FTL mapping-unit study (KSC 2026)

This is a fork of [snu-csl/nvmevirt](https://github.com/snu-csl/nvmevirt) (upstream commit `61c90f7`, 2026-05-21), set up to compare FTL mapping units under fio random writes.

| Path | Contents |
|---|---|
| [`nvmevirt/`](nvmevirt/) | NVMeVirt kernel module sources (upstream tree moved one level down, plus the changes listed below) |
| [`exp/`](exp/) | Experiment scripts, fio job template, analysis and plotting scripts |
| [`exp/results/`](exp/results/) | Raw results and analysis. `main3x3_20261008/` is the final data set. `main_20261008/` is the partial first design, and `pre_*/` holds the pre-checks |
| [`exp/report/`](exp/report/) | Experiment record (`KSC2026_NVMeVirt_매핑단위_실험기록.docx`, Korean), its generator, and the code-audit summary |
| [`EXPERIMENT_LOG_FOR_CLAUDE.md`](EXPERIMENT_LOG_FOR_CLAUDE.md) | Detailed hand-over log (Korean) |

## Changes to NVMeVirt (`nvmevirt/`)

| File | Change | Upstream |
|---|---|---|
| `Kbuild` | Builds the conventional SSD (`CONFIG_NVMEVIRT_SSD`, `BASE_SSD=SAMSUNG_970PRO`). Takes `MAPPING_UNIT` (bytes, default 4096) as a make variable, plus two optional switches that are off by default: `WBUF_FIX=1` and `GC_STATS=1` | NVM (Optane) target |
| `ssd.c` | `secs_per_pg = MAPPING_UNIT / LBA_SIZE`. Logs the mapping unit, flash page, oneshot page and write-buffer size at load time | `4096 / LBA_SIZE` |
| `ssd_config.h` | `BLKS_PER_PLN 384`, which gives 2 MiB blocks for 12 GiB of storage. `FLASH_PAGE_SIZE` equals the mapping unit when that is larger than 32 KiB | `8192`, `KB(32)` |
| `conv_ftl.c` | `WBUF_FIX=1`: a write takes whole mapping units from the write buffer, i.e. `(end_lpn - start_lpn + 1) * pgsz`, which matches what is released after programming. Upstream over-releases when the request is smaller than the mapping unit. `GC_STATS=1`: logs the first GC, and at rmmod prints per-partition counts of host pages, GC pages and victim lines | `buffer_allocate(wbuf, LBA_TO_BYTE(nr_lba))`, no statistics |
| `conv_ftl.h` | Adds `ksc_*` statistics fields to `struct conv_ftl` (only with `GC_STATS=1`) | — |

## Reproducing the final experiment

```bash
cd exp
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
bash build_modules.sh wbuffix          # make MAPPING_UNIT=<bytes> GC_STATS=1 WBUF_FIX=1 for each mapping unit
tmux new -s ksc2026 'bash run_all.sh main3x3_<date>'   # map 4k/16k/32k × bs 4k/16k/32k × 3 reps × page cache nodrop/drop
```

Prerequisites:

- GRUB `memmap=12G$12G isolcpus=3-5`.
- A sudoers rule like `exp/report/nvmevirt-exp.sudoers`, with the user name and the `chown` path changed to match your clone.
- fio, build-essential, linux-headers, python3-venv and tmux.

`exp/report/KSC2026_NVMeVirt_매핑단위_실험기록.docx` §3–4 has the full procedure and every setting.
