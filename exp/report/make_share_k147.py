#!/usr/bin/env python3
"""Copy of the 2026-10-25 results (kernel 6.8.0-147) as plain .csv / .json files, to hand to the senior.

usage: python3 make_share_k147.py [DATE]          (DATE default 20261025)

reads   exp/results/rocksdb_ycsba_k147_<D>/        (run dirs + analysis/summary_runs.csv from rocksdb/analyze_rocksdb.py)
        exp/results/rand4x5_k147_<D>/              (random write map 4 x bs 5 view; analysis/summary_runs.csv)
        exp/results/seq4x3_k147_<D>/               (sequential write wbuffix / merge; analysis/summary_runs.csv)
writes  exp/results/share_k147_<D>/                 README.md, summary tables, raw/ (per-run data converted to csv/json)
        ~/jsw/handoff/ksc2026_k147_share_<D>.zip    the same folder as one zip file
The original run directories are only read, never changed.
"""
import csv
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "rocksdb"))
import ycsb_parse as P  # noqa: E402

D = sys.argv[1] if len(sys.argv) > 1 else "20261025"
RES = EXP / "results"
OUT = RES / f"share_k147_{D}"
ZIP = Path.home() / "jsw" / "handoff" / f"ksc2026_k147_share_{D}.zip"
FIO_LOG_COLS = ["time_ms", "value", "direction", "block_size_bytes", "offset", "prio"]
BLK_COLS = ["epoch_s"] + P.BLK_FIELDS


def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def conv(v):
    if v in ("", None):
        return None
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def write_table(stem, rows, first=()):
    cols = [c for c in first if any(c in r for r in rows)]
    for r in rows:
        cols += [k for k in r if k not in cols]
    with (OUT / f"{stem}.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in cols})
    (OUT / f"{stem}.json").write_text(json.dumps([{k: r.get(k) for k in cols} for r in rows], indent=1, ensure_ascii=False) + "\n")


def meta_json(path):
    out = {}
    for line in path.read_text(errors="replace").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out.setdefault(k.strip(), v.strip())
    return out


def text_log_to_csv(src, dst, cols):
    rows = [ln.replace(" ", "").split(",") if "," in ln else ln.split() for ln in src.read_text().splitlines() if ln.strip()]
    n = max((len(r) for r in rows), default=0)
    with dst.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols[:n])
        w.writerows(rows)


# ------------------------------------------------------------------ RocksDB
RDB = RES / f"rocksdb_ycsba_k147_{D}"
RDB_FIRST = ["map_unit_KiB", "block_size_KiB", "wal", "tps_ops_s", "read_p99_us", "update_p99_us", "read_tps_ops_s",
             "update_tps_ops_s", "read_avg_us", "update_avg_us", "read_ops", "update_ops", "run_runtime_s"]


def rocksdb_part():
    summ = RDB / "analysis" / "summary_runs.csv"
    if not summ.exists():
        print(f"skip RocksDB: {summ} missing (run rocksdb/analyze_rocksdb.py first)")
        return 0
    rows = [{k: conv(v) for k, v in r.items()} for r in read_csv(summ)]
    write_table("rocksdb_ycsba_results", rows, RDB_FIRST)
    # compact table for the senior: the requested values only, rounded; utf-8-sig so Excel opens it cleanly
    compact = [{"map_unit_KB": r["map_unit_KiB"], "block_size_KB": r["block_size_KiB"], "WAL": r["wal"],
                "TPS_ops_per_s": round(r["tps_ops_s"], 1), "READ_p99_us": r["read_p99_us"],
                "UPDATE_p99_us": r["update_p99_us"], "READ_avg_us": round(r["read_avg_us"], 1),
                "UPDATE_avg_us": round(r["update_avg_us"], 1), "READ_ops_per_s": round(r["read_tps_ops_s"], 1),
                "UPDATE_ops_per_s": round(r["update_tps_ops_s"], 1)} for r in rows]
    with (OUT / "rocksdb_ycsba_table.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(compact[0]))
        w.writeheader()
        w.writerows(compact)
    (OUT / "rocksdb_ycsba_table.json").write_text(json.dumps(compact, indent=1) + "\n")
    # pivot tables: rows = mapping unit, columns = WAL x block_size
    maps = sorted({r["map_unit_KiB"] for r in rows})
    blks = sorted({r["block_size_KiB"] for r in rows})
    for metric in ("tps_ops_s", "read_p99_us", "update_p99_us", "read_tps_ops_s", "update_tps_ops_s", "read_avg_us",
                   "update_avg_us"):
        piv = []
        for m in maps:
            row = {"map_unit_KiB": m}
            for wal in ("off", "on"):
                for b in blks:
                    hit = [r for r in rows if r["map_unit_KiB"] == m and r["block_size_KiB"] == b and r["wal"] == wal]
                    row[f"wal_{wal}_block_{b}KiB"] = hit[0][metric] if hit else None
            piv.append(row)
        write_table(f"rocksdb_pivot_{metric}", piv)
    failed = RDB / "analysis" / "failed_runs.csv"
    if failed.exists():
        shutil.copy2(failed, OUT / "rocksdb_failed_runs.csv")
    n = 0
    for vdir in sorted(p for p in RDB.iterdir() if p.is_dir() and p.name not in ("analysis",) and not p.name.startswith("env_")):
        for rdir in sorted(vdir.iterdir()):
            if not (rdir / "DONE").exists():
                continue
            dst = OUT / "raw" / "rocksdb" / rdir.name
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rdir / "result.json", dst / "result.json")
            (dst / "meta.json").write_text(json.dumps(meta_json(rdir / "meta.txt"), indent=1, ensure_ascii=False) + "\n")
            for ph in ("load", "run"):
                (dst / f"ycsb_{ph}_summary.json").write_text(
                    json.dumps(P.parse_summary(rdir / f"{ph}.txt"), indent=1) + "\n")
                st = P.parse_status(rdir / f"{ph}_status.txt")
                if st:
                    cols = []
                    for r in st:
                        cols += [k for k in r if k not in cols]
                    with (dst / f"ycsb_{ph}_status_1s.csv").open("w", newline="") as f:
                        w = csv.DictWriter(f, fieldnames=cols)
                        w.writeheader()
                        w.writerows(st)
            text_log_to_csv(rdir / "blkstat_1s.txt", dst / "device_blkstat_1s.csv", BLK_COLS)
            # phase boundaries (before_mkfs, before_load, after_load, before_run, after_run, after_umount) with the same counters
            text_log_to_csv(rdir / "blkstat_phases.txt", dst / "device_blkstat_phases.csv", ["phase"] + BLK_COLS)
            n += 1
    return n


# ------------------------------------------------------------------ fio
FIO_FIRST = ["workload", "variant", "map_KiB", "bs_KiB", "bw_MiBps", "iops", "clat_mean_us", "clat_p99_us", "waf_total",
             "runtime_s"]


def fio_part(name, exp_name, workload):
    edir = RES / exp_name
    summ = edir / "analysis" / "summary_runs.csv"
    if not summ.exists():
        print(f"skip {exp_name}: {summ} missing (run analyze.py first)")
        return 0
    rows = []
    for r in read_csv(summ):
        r = {k: conv(v) for k, v in r.items()}
        r["workload"] = workload
        r["map_KiB"], r["bs_KiB"] = int(r["map"][:-1]), int(r["bs"][:-1])
        rows.append(r)
    write_table(name, rows, FIO_FIRST)
    failed = edir / "analysis" / "failed_runs.csv"
    if failed.exists():
        shutil.copy2(failed, OUT / f"{name}_failed_runs.csv")
    n = 0
    for vdir in sorted(p for p in edir.iterdir() if p.is_dir() and p.name not in ("analysis", "plots") and not p.name.startswith("env_")):
        for rdir in sorted(vdir.iterdir()):
            if not re.match(r"^map\d+k_bs\d+k_r\d+$", rdir.name) or not (rdir / "DONE").exists():
                continue
            dst = OUT / "raw" / name / vdir.name / rdir.name
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rdir / "fio.json", dst / "fio.json")
            (dst / "meta.json").write_text(json.dumps(meta_json(rdir / "meta.txt"), indent=1, ensure_ascii=False) + "\n")
            for kind in ("bw", "iops", "clat", "lat"):
                src = rdir / f"fio_{kind}.1.log"
                if src.exists():
                    text_log_to_csv(src, dst / f"fio_{kind}_500ms.csv", FIO_LOG_COLS)
            n += 1
    return n


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    n_r = rocksdb_part()
    n_f1 = fio_part("fio_randwrite", f"rand4x5_k147_{D}", "randwrite")
    n_f2 = fio_part("fio_seqwrite", f"seq4x3_k147_{D}", "seqwrite")
    readme = EXP / "report" / "share_k147_README.md"
    if readme.exists():
        shutil.copy2(readme, OUT / "README.md")
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, Path(OUT.name) / f.relative_to(OUT))
    print(f"{OUT}: RocksDB {n_r} runs, fio random {n_f1} runs, fio sequential {n_f2} runs; zip {ZIP} "
          f"({ZIP.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
