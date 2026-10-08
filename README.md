# NVMeVirt — FTL mapping-unit study (KSC 2026)

This is a fork of [snu-csl/nvmevirt](https://github.com/snu-csl/nvmevirt) (upstream commit `61c90f7`, 2026-05-21), set up to compare FTL mapping units (4 KiB–128 KiB) under fio random writes.

| Directory | Contents |
|---|---|
| [`nvmevirt/`](nvmevirt/) | NVMeVirt kernel module sources (upstream tree moved one level down, plus the changes listed below) |
| [`exp/`](exp/) | Experiment scripts, fio job template, analysis script and results |

## Changes to NVMeVirt (`nvmevirt/`)

| File | Change | Upstream |
|---|---|---|
| `Kbuild` | Build the conventional SSD (`CONFIG_NVMEVIRT_SSD`, `BASE_SSD=SAMSUNG_970PRO`) and pass `MAPPING_UNIT` (bytes) as a make variable | NVM (Optane) target |
| `ssd.c` | `secs_per_pg = MAPPING_UNIT / LBA_SIZE`, and log the mapping unit, flash page, oneshot page and write buffer size at load time | `4096 / LBA_SIZE` |
| `ssd_config.h` | `BLKS_PER_PLN 384`, which gives 2 MiB blocks for 12 GiB of storage. `FLASH_PAGE_SIZE` equals the mapping unit when that is larger than 32 KiB | `8192`, `KB(32)` |

Build one module per mapping unit with `make MAPPING_UNIT=16384`. See [`exp/README.md`](exp/README.md) for the full procedure.
