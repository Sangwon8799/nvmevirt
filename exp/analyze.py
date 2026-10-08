#!/usr/bin/env python3
"""KSC2026 NVMeVirt mapping-unit experiment: collect fio results into CSV tables and figures.

usage:  python3 analyze.py results/<EXP_NAME>

reads   results/<EXP>/<variant>/map<MAP>_bs<BS>_r<REP>/{fio.json, fio_bw.1.log, meta.txt, dmesg_*.txt}
writes  results/<EXP>/analysis/summary_runs.csv     one row per run
        results/<EXP>/analysis/summary_agg.csv      mean / std / min / max over repetitions
        results/<EXP>/analysis/fig_*.png
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

SIZES = ["4k", "8k", "16k", "32k", "64k", "128k"]
# categorical slots (fixed order) and chart chrome — light mode
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

RUN_RE = re.compile(r"^map(?P<map>\d+k)_bs(?P<bs>\d+k)_r(?P<rep>\d+)$")
DMESG_TS = re.compile(r"^\[\s*(\d+\.\d+)\]")
EARLY_S, LATE_S = 10.0, 20.0   # early window = first 10 s, late window = last 20 s


def kib(s):
    return int(s[:-1])


def meta_value(meta, key):
    m = re.search(rf"^{key}:\s*(.*)$", meta, re.M)
    return m.group(1).strip() if m else ""


def read_log(path):
    """fio log line: time(ms), value, direction, bs, offset[, prio]."""
    t, v = [], []
    if not path.exists():
        return np.array(t), np.array(v)
    for line in path.read_text().splitlines():
        p = line.split(",")
        if len(p) >= 2:
            t.append(int(p[0]) / 1000.0)
            v.append(float(p[1]))
    return np.array(t), np.array(v)


def gc_info(rdir):
    """KSC2026 GC instrumentation in dmesg: first GC time (relative to the fio-start marker), counters at rmmod."""
    out = {}
    run = rdir / "dmesg_run.txt"
    if run.exists():
        fio_start, firsts = None, []
        for line in run.read_text().splitlines():
            m = DMESG_TS.match(line)
            if not m:
                continue
            if "KSC2026-MARK" in line and "fio-start" in line and fio_start is None:
                fio_start = float(m.group(1))
            elif "KSC2026: first GC" in line:
                firsts.append(float(m.group(1)))
        if fio_start is not None and firsts:
            out["gc_onset_s"] = min(firsts) - fio_start
            out["gc_onset_last_part_s"] = max(firsts) - fio_start
    unload = rdir / "dmesg_unload.txt"
    if unload.exists():
        tot = {"host_pgs": 0, "gc_pgs": 0, "gc_cnt": 0}
        seen = False
        for line in unload.read_text().splitlines():
            m = re.search(r"KSC2026: stats part=\d+ host_pgs=(\d+) gc_pgs=(\d+) gc_cnt=(\d+)", line)
            if m:
                seen = True
                tot["host_pgs"] += int(m.group(1))
                tot["gc_pgs"] += int(m.group(2))
                tot["gc_cnt"] += int(m.group(3))
        if seen:
            out.update(tot)
    return out


def collect(exp_dir):
    rows, series = [], {}
    for vdir in sorted(p for p in exp_dir.iterdir() if p.is_dir() and p.name not in ("analysis",) and not p.name.startswith("env_")):
        for rdir in sorted(vdir.iterdir()):
            m = RUN_RE.match(rdir.name)
            if not m or not (rdir / "DONE").exists():
                continue
            j = json.loads((rdir / "fio.json").read_text())
            w = j["jobs"][0]["write"]
            meta = (rdir / "meta.txt").read_text()
            dev_size = int(re.search(r"size=(\d+) B", meta).group(1))
            pct = w["clat_ns"].get("percentile", {})
            t, bw = read_log(rdir / "fio_bw.1.log")
            bw = bw / 1024.0  # KiB/s -> MiB/s
            dur = t[-1] if len(t) else 0.0
            row = {
                "variant": vdir.name, "map": m["map"], "bs": m["bs"], "rep": int(m["rep"]),
                "bw_MiBps": w["bw"] / 1024.0,
                "iops": w["iops"],
                "written_GiB": w["io_bytes"] / 2**30,
                "fill_ratio": w["io_bytes"] / dev_size,
                "clat_mean_us": w["clat_ns"]["mean"] / 1e3,
                "clat_p50_us": pct.get("50.000000", float("nan")) / 1e3,
                "clat_p99_us": pct.get("99.000000", float("nan")) / 1e3,
                "clat_p999_us": pct.get("99.900000", float("nan")) / 1e3,
                "lat_mean_us": w["lat_ns"]["mean"] / 1e3,
                "slat_mean_us": w["slat_ns"]["mean"] / 1e3,
                "runtime_s": w["runtime"] / 1e3,
                "bw_first10s_MiBps": float(bw[t <= EARLY_S].mean()) if len(t) else float("nan"),
                "bw_last20s_MiBps": float(bw[t > dur - LATE_S].mean()) if len(t) else float("nan"),
                "dev_bytes": dev_size,
                "chmodel_msgs": int(meta_value(meta, "chmodel_msgs").split()[0]) if meta_value(meta, "chmodel_msgs") else 0,
                "kernel_warn": int(meta_value(meta, "kernel_warn").split()[0]) if meta_value(meta, "kernel_warn") else 0,
            }
            g = gc_info(rdir)
            if "gc_onset_s" in g:
                on = g["gc_onset_s"]
                row["gc_onset_s"] = on
                row["gc_onset_last_part_s"] = g["gc_onset_last_part_s"]
                row["bw_pre_gc_MiBps"] = float(bw[t <= on].mean()) if (t <= on).any() else float("nan")
                row["bw_post_gc_MiBps"] = float(bw[t > on].mean()) if (t > on).any() else float("nan")
            if "host_pgs" in g and g["host_pgs"]:
                pg = kib(m["map"]) * 1024
                row["gc_cnt"] = g["gc_cnt"]
                row["ftl_host_pgs"] = g["host_pgs"]
                row["ftl_gc_pgs"] = g["gc_pgs"]
                row["waf_gc"] = (g["host_pgs"] + g["gc_pgs"]) / g["host_pgs"]
                row["waf_total"] = (g["host_pgs"] + g["gc_pgs"]) * pg / w["io_bytes"]
            rows.append(row)
            series[(vdir.name, m["map"], m["bs"], int(m["rep"]))] = (t, bw, row.get("gc_onset_s"))
    return rows, series


def aggregate(rows):
    keys = [k for k in rows[0] if k not in ("variant", "map", "bs", "rep", "dev_bytes")]
    keys += sorted({k for r in rows for k in r} - set(keys) - {"variant", "map", "bs", "rep", "dev_bytes"})
    groups = {}
    for r in rows:
        groups.setdefault((r["variant"], r["map"], r["bs"]), []).append(r)
    agg = []
    for (v, mp, bs), rs in sorted(groups.items(), key=lambda x: (x[0][0], kib(x[0][1]), kib(x[0][2]))):
        a = {"variant": v, "map": mp, "bs": bs, "n": len(rs)}
        for k in keys:
            vals = [r[k] for r in rs if k in r and r[k] == r[k]]
            if not vals:
                continue
            a[f"{k}_mean"] = statistics.fmean(vals)
            a[f"{k}_std"] = statistics.stdev(vals) if len(vals) > 1 else 0.0
            a[f"{k}_min"] = min(vals)
            a[f"{k}_max"] = max(vals)
        agg.append(a)
    return agg


def write_csv(path, rows):
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with path.open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader()
        for r in rows:
            wr.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def line_vs_bs(agg, variant, metric, ylabel, title, path, logy=False):
    fig, ax = plt.subplots(figsize=(7.2, 4.2), facecolor=SURFACE)
    style(ax)
    x = np.arange(len(SIZES))
    for i, mp in enumerate(SIZES):
        pts = [(SIZES.index(a["bs"]), a[f"{metric}_mean"], a[f"{metric}_std"])
               for a in agg if a["variant"] == variant and a["map"] == mp and f"{metric}_mean" in a]
        if not pts:
            continue
        xs, ys, es = zip(*sorted(pts))
        ax.errorbar(xs, ys, yerr=es, color=SERIES[i], linewidth=2, marker="o", markersize=5,
                    capsize=3, label=f"map {mp.upper()}")
    ax.set_xticks(x, [s.upper() for s in SIZES])
    ax.set_xlabel("fio block size", color=INK2)
    ax.set_ylabel(ylabel, color=INK2)
    if logy:
        ax.set_yscale("log")
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=8, ncol=3, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def heatmap(agg, variant, metric, label, title, path):
    grid = np.full((len(SIZES), len(SIZES)), np.nan)
    for a in agg:
        if a["variant"] == variant and f"{metric}_mean" in a:
            grid[SIZES.index(a["map"]), SIZES.index(a["bs"])] = a[f"{metric}_mean"]
    if np.isnan(grid).all():
        return
    fig, ax = plt.subplots(figsize=(6.6, 4.8), facecolor=SURFACE)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seqblue", SEQ_BLUE)
    im = ax.imshow(grid, cmap=cmap, aspect="auto", origin="lower")
    vmax = np.nanmax(grid)
    for i in range(len(SIZES)):
        for k in range(len(SIZES)):
            if not np.isnan(grid[i, k]):
                ax.text(k, i, f"{grid[i, k]:.0f}", ha="center", va="center", fontsize=8,
                        color="#ffffff" if grid[i, k] > 0.55 * vmax else INK)
    ax.set_xticks(range(len(SIZES)), [s.upper() for s in SIZES])
    ax.set_yticks(range(len(SIZES)), [s.upper() for s in SIZES])
    ax.set_xlabel("fio block size", color=INK2)
    ax.set_ylabel("FTL mapping unit", color=INK2)
    ax.tick_params(colors=INK2, labelsize=9)
    cb = fig.colorbar(im, ax=ax)
    cb.set_label(label, color=INK2)
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def timeseries_grid(series, variant, path):
    fig, axes = plt.subplots(len(SIZES), len(SIZES), figsize=(16, 13), sharex=True, facecolor=SURFACE)
    ymax = {}
    for (v, mp, bs, r), (t, bw, on) in series.items():
        if v == variant and len(bw):
            ymax[mp] = max(ymax.get(mp, 0), float(bw.max()))
    for i, mp in enumerate(SIZES):
        for k, bs in enumerate(SIZES):
            ax = axes[i, k]
            style(ax)
            ax.tick_params(labelsize=7)
            for r in (1, 2, 3):
                key = (variant, mp, bs, r)
                if key not in series:
                    continue
                t, bw, on = series[key]
                ax.plot(t, bw, color=SERIES[r - 1], linewidth=1.0, label=f"rep {r}")
                if on is not None:
                    ax.axvline(on, color=SERIES[r - 1], linestyle="--", linewidth=0.8)
            if mp in ymax:
                ax.set_ylim(0, ymax[mp] * 1.08)
            if i == 0:
                ax.set_title(f"bs {bs.upper()}", color=INK, fontsize=10)
            if k == 0:
                ax.set_ylabel(f"map {mp.upper()}\nMiB/s", color=INK2, fontsize=9)
            if i == len(SIZES) - 1:
                ax.set_xlabel("time (s)", color=INK2, fontsize=9)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", frameon=False, fontsize=9, ncol=3)
    fig.suptitle(f"Write bandwidth over time ({variant}; dashed line = first GC, when recorded)",
                 color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def variant_compare(agg, path):
    variants = sorted({a["variant"] for a in agg})
    if len(variants) < 2:
        return
    maps = [mp for mp in SIZES[1:]]
    fig, axes = plt.subplots(1, len(maps), figsize=(16, 3.8), facecolor=SURFACE, sharey=False)
    for ax, mp in zip(axes, maps):
        style(ax)
        for vi, v in enumerate(variants):
            pts = [(SIZES.index(a["bs"]), a["bw_MiBps_mean"], a["bw_MiBps_std"])
                   for a in agg if a["variant"] == v and a["map"] == mp and kib(a["bs"]) < kib(mp)]
            if pts:
                xs, ys, es = zip(*sorted(pts))
                ax.errorbar(xs, ys, yerr=es, color=SERIES[vi], linewidth=2, marker="o", markersize=5,
                            capsize=3, label=v)
        ax.set_xticks(range(SIZES.index(mp)), [s.upper() for s in SIZES[:SIZES.index(mp)]])
        ax.set_title(f"map {mp.upper()} (bs < map)", color=INK, fontsize=10, loc="left")
        ax.set_xlabel("fio block size", color=INK2, fontsize=9)
    axes[0].set_ylabel("write bandwidth (MiB/s)", color=INK2)
    axes[0].legend(frameon=False, fontsize=8, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    exp_dir = Path(sys.argv[1]).resolve()
    out = exp_dir / "analysis"
    out.mkdir(exist_ok=True)
    rows, series = collect(exp_dir)
    if not rows:
        sys.exit(f"no finished runs under {exp_dir}")
    rows.sort(key=lambda r: (r["variant"], kib(r["map"]), kib(r["bs"]), r["rep"]))
    agg = aggregate(rows)
    write_csv(out / "summary_runs.csv", rows)
    write_csv(out / "summary_agg.csv", agg)
    for v in sorted({r["variant"] for r in rows}):
        line_vs_bs(agg, v, "bw_MiBps", "write bandwidth (MiB/s)",
                   f"Random-write bandwidth, 60 s from a fresh device ({v}; mean ± std, n=3)",
                   out / f"fig_bw_vs_bs_{v}.png")
        line_vs_bs(agg, v, "clat_mean_us", "mean completion latency (µs)",
                   f"Mean completion latency ({v}; mean ± std, n=3)", out / f"fig_clat_mean_vs_bs_{v}.png", logy=True)
        line_vs_bs(agg, v, "clat_p99_us", "p99 completion latency (µs)",
                   f"p99 completion latency ({v}; mean ± std, n=3)", out / f"fig_clat_p99_vs_bs_{v}.png", logy=True)
        line_vs_bs(agg, v, "bw_last20s_MiBps", "write bandwidth, last 20 s (MiB/s)",
                   f"Bandwidth in the last 20 s of the run ({v})", out / f"fig_bw_last20s_vs_bs_{v}.png")
        heatmap(agg, v, "bw_MiBps", "MiB/s", f"Mean write bandwidth, MiB/s ({v})", out / f"fig_bw_heatmap_{v}.png")
        heatmap(agg, v, "waf_total", "NAND bytes / host bytes",
                f"Total write amplification ({v})", out / f"fig_waf_heatmap_{v}.png")
        timeseries_grid(series, v, out / f"fig_timeseries_{v}.png")
    variant_compare(agg, out / "fig_variant_compare.png")
    print(f"{len(rows)} runs -> {out}")


if __name__ == "__main__":
    main()
