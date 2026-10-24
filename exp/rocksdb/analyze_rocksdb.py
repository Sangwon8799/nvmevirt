#!/usr/bin/env python3
"""KSC2026 RocksDB/YCSB-A experiment: one table and a few figures from the run directories of run_rocksdb_ycsb.sh.

usage: python3 analyze_rocksdb.py results/<EXP>

reads   results/<EXP>/<variant>/map<M>_blk<B>_wal<off|on>/ with a DONE marker (re-parsed with ycsb_parse.py)
writes  results/<EXP>/analysis/summary_runs.csv / summary_runs.json   one row per run (flat columns)
        results/<EXP>/analysis/failed_runs.csv                         runs with a FAILED marker (if any)
        results/<EXP>/analysis/fig_tps_heatmap.png, fig_read_p99_heatmap.png, fig_update_p99_heatmap.png,
        fig_tps_vs_block.png, fig_tps_timeseries.png
"""
import csv
import json
import re
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import ycsb_parse as P  # noqa: E402
import analyze as A  # noqa: E402  (palette and axis style of the fio figures)

RUN_RE = re.compile(r"^map(?P<map>\d+k)_blk(?P<blk>\d+k)_wal(?P<wal>off|on)$")
GB_RE = re.compile(r"([\d.]+) GB write, [\d.]+ MB/s write, ([\d.]+) GB read")


def kib(s):
    return int(s[:-1])


def window_mean(status, lo, hi):
    v = [r["ops_per_s"] for r in status if lo < r["t_s"] <= hi]
    return statistics.fmean(v) if v else None


def flat(res, rdir):
    r = {"run": res["run"], "variant": res["variant"], "map_unit": res["map_unit"], "map_unit_KiB": kib(res["map_unit"]),
         "block_size": res["block_size"], "block_size_KiB": kib(res["block_size"]), "wal": res["wal"],
         "recordcount": res["recordcount"], "threads": res["threads"],
         "tps_ops_s": res["tps_ops_s"], "run_runtime_s": res["run_runtime_s"]}
    for op in ("read", "update"):
        d = res[op]
        r[f"{op}_ops"] = d.get("ops")
        for k in ("avg_us", "p50_us", "p90_us", "p95_us", "p99_us", "p99.9_us", "p99.99_us", "min_us", "max_us"):
            r[f"{op}_{k}"] = d.get(k)
        r[f"{op}_not_ok"] = sum(v for k, v in d.get("return", {}).items() if k != "OK")
        r[f"{op}_tps_ops_s"] = d.get("tps_ops_s")   # this operation's completions / run time (read + update = tps_ops_s)
    status = [x for x in P.parse_status(rdir / "run_status.txt") if not x.get("final_partial")]
    end = status[-1]["t_s"] if status else 0
    r["tps_first60s"] = window_mean(status, 0, 60)
    r["tps_last60s"] = window_mean(status, end - 60, end)
    win = [window_mean(status, a, a + 60) for a in range(0, max(end - 59, 1), 60)]
    win = [w for w in win if w]
    r["tps_60s_windows_cv_pct"] = 100 * statistics.pstdev(win) / statistics.fmean(win) if len(win) > 1 else None
    ld = res["load"]
    r.update({"load_wall_s": ld.get("wall_s"), "load_tps_ops_s": ld.get("tps_ops_s"),
              "load_insert_avg_us": ld["insert"].get("avg_us"), "load_insert_p99_us": ld["insert"].get("p99_us")})
    r.update({"db_bytes_after_load": res.get("db_bytes_after_load"), "db_bytes_after_run": res.get("db_bytes_after_run"),
              "wal_file_bytes_after_run": res.get("wal_file_bytes_after_run"), "fs_used_after_run": res.get("fs_used_after_run")})
    bl = res["block_layer"]
    for ph in ("load", "run"):
        b = bl.get(ph, {})
        for k in ("read_bytes", "read_ios", "read_avg_req_KiB", "read_MiB_s", "write_bytes", "write_ios",
                  "write_avg_req_KiB", "write_MiB_s"):
            r[f"{ph}_dev_{k}"] = b.get(k)
    r["mkfs_write_bytes"] = bl.get("mkfs_write_bytes")
    r["session_write_bytes"] = bl.get("session_write_bytes")
    f = res["ftl"]
    r.update({"ftl_host_pgs": f.get("host_pgs"), "ftl_gc_pgs": f.get("gc_pgs"), "ftl_gc_cnt": f.get("gc_cnt"),
              "ftl_nand_write_bytes": f.get("nand_write_bytes"), "ftl_waf_gc": f.get("waf_gc"),
              "ftl_waf_session": f.get("waf_session"), "first_gc_phase": f.get("first_gc_phase"),
              "first_gc_s_after_phase_start": f.get("first_gc_s_after_phase_start")})
    for ph in ("load", "run"):   # from the EVENT_LOG_v1 records of that phase's LOG (complete up to DB close)
        ev = res.get(f"rocksdb_{ph}_events", {})
        for k in ("flush_write_bytes", "compaction_write_bytes", "compaction_read_bytes", "sst_write_bytes",
                  "flush_jobs", "compaction_jobs", "stall_msgs", "stop_msgs"):
            r[f"rocksdb_{ph}_{k}"] = ev.get(k)
    lg = res.get("rocksdb_log_last_dump", {})   # periodic stats dump: covers only up to the last dump before close
    m = GB_RE.search(lg.get("cumulative_compaction", ""))
    r["rocksdb_run_compaction_write_GB_at_last_dump"] = float(m.group(1)) if m else None
    r["rocksdb_run_compaction_read_GB_at_last_dump"] = float(m.group(2)) if m else None
    u = re.match(r"([\d.]+) total", lg.get("uptime", ""))
    r["rocksdb_last_dump_uptime_s"] = float(u.group(1)) if u else None
    for k, v in res.get("cpu", {}).items():
        r[k] = v
    r["chmodel_msgs"], r["kernel_warn"] = res.get("chmodel_msgs"), res.get("kernel_warn")
    r["start_utc"], r["end_utc"] = res.get("start"), res.get("end")
    return r


def write_csv(path, rows):
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})


def grid_of(rows, wal, metric, maps, blks):
    g = np.full((len(maps), len(blks)), np.nan)
    for r in rows:
        if r["wal"] == wal and r.get(metric) is not None:
            g[maps.index(r["map_unit"]), blks.index(r["block_size"])] = r[metric]
    return g


def heatmaps(rows, metric, label, title, path, fmt="{:.0f}"):
    maps = sorted({r["map_unit"] for r in rows}, key=kib)
    blks = sorted({r["block_size"] for r in rows}, key=kib)
    wals = [w for w in ("off", "on") if any(r["wal"] == w for r in rows)]
    grids = [grid_of(rows, w, metric, maps, blks) for w in wals]
    if all(np.isnan(g).all() for g in grids):
        return
    vmin = np.nanmin([np.nanmin(g) for g in grids if not np.isnan(g).all()])
    vmax = np.nanmax([np.nanmax(g) for g in grids if not np.isnan(g).all()])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seqblue", A.SEQ_BLUE)
    fig, axes = plt.subplots(1, len(wals), figsize=(4.6 * len(wals) + 1.2, 4.4), facecolor=A.SURFACE, squeeze=False)
    im = None
    for ax, w, g in zip(axes[0], wals, grids):
        im = ax.imshow(g, cmap=cmap, aspect="auto", origin="lower", vmin=vmin, vmax=vmax)
        for i in range(len(maps)):
            for k in range(len(blks)):
                if not np.isnan(g[i, k]):
                    frac = (g[i, k] - vmin) / (vmax - vmin) if vmax > vmin else 0
                    ax.text(k, i, fmt.format(g[i, k]), ha="center", va="center", fontsize=8,
                            color="#ffffff" if frac > 0.55 else A.INK)
        ax.set_xticks(range(len(blks)), [s.upper() for s in blks])
        ax.set_yticks(range(len(maps)), [s.upper() for s in maps])
        ax.set_xlabel("RocksDB block_size", color=A.INK2)
        ax.set_ylabel("FTL mapping unit", color=A.INK2)
        ax.tick_params(colors=A.INK2, labelsize=9)
        ax.set_title(f"WAL {w}", color=A.INK, fontsize=10, loc="left")
    cb = fig.colorbar(im, ax=list(axes[0]))
    cb.set_label(label, color=A.INK2)
    fig.suptitle(title, color=A.INK, fontsize=11, x=0.01, ha="left")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def tps_vs_block(rows, path):
    maps = sorted({r["map_unit"] for r in rows}, key=kib)
    blks = sorted({r["block_size"] for r in rows}, key=kib)
    wals = [w for w in ("off", "on") if any(r["wal"] == w for r in rows)]
    fig, axes = plt.subplots(1, len(wals), figsize=(4.8 * len(wals), 3.8), facecolor=A.SURFACE, sharey=True, squeeze=False)
    for ax, w in zip(axes[0], wals):
        A.style(ax)
        for i, mp in enumerate(maps):
            pts = sorted((blks.index(r["block_size"]), r["tps_ops_s"]) for r in rows
                         if r["wal"] == w and r["map_unit"] == mp and r["tps_ops_s"] is not None)
            if pts:
                ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", markersize=5, linewidth=2,
                        color=A.SERIES[i % len(A.SERIES)], label=f"map {mp.upper()}")
        ax.set_xticks(range(len(blks)), [s.upper() for s in blks])
        ax.set_xlabel("RocksDB block_size", color=A.INK2)
        ax.set_title(f"WAL {w}", color=A.INK, fontsize=10, loc="left")
    axes[0][0].set_ylabel("YCSB-A throughput (ops/s)", color=A.INK2)
    axes[0][-1].legend(frameon=False, fontsize=8, labelcolor=A.INK2)
    rt = sorted({round(r["run_runtime_s"]) for r in rows if r.get("run_runtime_s")})
    fig.suptitle(f"YCSB-A throughput, {'/'.join(map(str, rt))} s run phase (single run each)", color=A.INK, fontsize=11,
                 x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def tps_timeseries(exp_dir, rows, path, smooth=10):
    maps = sorted({r["map_unit"] for r in rows}, key=kib)
    blks = sorted({r["block_size"] for r in rows}, key=kib)
    fig, axes = plt.subplots(len(maps), len(blks), figsize=(2.9 * len(blks) + 1, 2.0 * len(maps) + 0.8),
                             facecolor=A.SURFACE, sharex=True, sharey=True, squeeze=False)
    for r in rows:
        st = [x for x in P.parse_status(exp_dir / r["variant"] / r["run"] / "run_status.txt") if not x.get("final_partial")]
        if not st:
            continue
        t = np.array([x["t_s"] for x in st], dtype=float)
        v = np.array([x["ops_per_s"] for x in st], dtype=float)
        if len(v) >= smooth:   # moving average, normalised at the edges (no zero padding)
            k = np.ones(smooth) / smooth
            v = np.convolve(v, k, mode="same") / np.convolve(np.ones_like(v), k, mode="same")
        ax = axes[maps.index(r["map_unit"])][blks.index(r["block_size"])]
        ax.plot(t, v, linewidth=1.2, color=A.SERIES[0 if r["wal"] == "off" else 1], label=f"WAL {r['wal']}")
    for i, mp in enumerate(maps):
        for k, b in enumerate(blks):
            ax = axes[i][k]
            A.style(ax)
            ax.set_title(f"map {mp.upper()} · block {b.upper()}", color=A.INK2, fontsize=8, loc="left")
    axes[-1][0].set_xlabel("seconds into the run phase", color=A.INK2)
    axes[0][0].set_ylabel("ops/s", color=A.INK2)
    handles, labels = axes[0][0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", frameon=False, fontsize=8, labelcolor=A.INK2)
    fig.suptitle(f"YCSB-A throughput over time ({smooth} s moving average)", color=A.INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    exp_dir = Path(sys.argv[1]).resolve()
    out = exp_dir / "analysis"
    out.mkdir(exist_ok=True)
    rows, failed = [], []
    for vdir in sorted(p for p in exp_dir.iterdir() if p.is_dir() and p.name != "analysis" and not p.name.startswith("env_")):
        for rdir in sorted(vdir.iterdir()):
            if not RUN_RE.match(rdir.name):
                continue
            if (rdir / "DONE").exists():
                res = P.parse_run(rdir)
                rows.append(flat(res, rdir))
            elif (rdir / "FAILED").exists():
                failed.append({"variant": vdir.name, "run": rdir.name,
                               "reason": (rdir / "FAILED").read_text(errors="replace").strip().splitlines()[0]})
    if not rows:
        sys.exit(f"no finished runs under {exp_dir}")
    rows.sort(key=lambda r: (r["variant"], r["map_unit_KiB"], r["block_size_KiB"], r["wal"] != "off"))
    write_csv(out / "summary_runs.csv", rows)
    (out / "summary_runs.json").write_text(json.dumps(rows, indent=1) + "\n")
    if failed:
        write_csv(out / "failed_runs.csv", failed)
    heatmaps(rows, "tps_ops_s", "ops/s", "YCSB-A throughput (ops/s)", out / "fig_tps_heatmap.png")
    heatmaps(rows, "read_p99_us", "µs", "READ p99 latency (µs)", out / "fig_read_p99_heatmap.png")
    heatmaps(rows, "update_p99_us", "µs", "UPDATE p99 latency (µs)", out / "fig_update_p99_heatmap.png")
    tps_vs_block(rows, out / "fig_tps_vs_block.png")
    tps_timeseries(exp_dir, rows, out / "fig_tps_timeseries.png")
    print(f"{len(rows)} runs, {len(failed)} failed -> {out}")


if __name__ == "__main__":
    main()
