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

SIZES = ["4k", "8k", "16k", "32k", "64k", "128k"]   # replaced in main() by the sizes present in the results
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


def kernel_warnings(rdir):
    """Kernel log lines that look like problems, other than NVMeVirt's own channel-model messages."""
    log = rdir / "kernel.log"
    if not log.exists():
        return 0
    pat = re.compile(r"WARNING|almost full|timeout|reset|Oops|BUG|Disk read failed|I/O error", re.I)
    return sum(1 for ln in log.read_text(errors="replace").splitlines()
               if "[chmodel_request]" not in ln and "KSC2026" not in ln and pat.search(ln))


def collect(exp_dir):
    rows, series = [], {}
    for vdir in sorted(p for p in exp_dir.iterdir() if p.is_dir() and p.name not in ("analysis", "plots") and not p.name.startswith("env_")):
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
                "kernel_warn": kernel_warnings(rdir),
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


def collect_failed(exp_dir):
    """Runs with a FAILED marker (fio I/O errors / watchdog): kept out of the aggregates, reported separately."""
    out = []
    for vdir in sorted(p for p in exp_dir.iterdir() if p.is_dir() and p.name not in ("analysis", "plots") and not p.name.startswith("env_")):
        for rdir in sorted(vdir.iterdir()):
            m = RUN_RE.match(rdir.name)
            if not m or not (rdir / "FAILED").exists() or (rdir / "DONE").exists():
                continue
            row = {"variant": vdir.name, "map": m["map"], "bs": m["bs"], "rep": int(m["rep"])}
            first = (rdir / "FAILED").read_text(errors="replace").splitlines()[0]
            for k in ("fio_exit", "fio_json_error"):
                mm = re.search(rf"{k}=(\S+)", first)
                row[k] = mm.group(1) if mm else ""
            try:
                w = json.loads((rdir / "fio.json").read_text())["jobs"][0]["write"]
                row.update({"runtime_s": w["runtime"] / 1e3, "bw_MiBps": w["bw"] / 1024.0, "iops": w["iops"],
                            "written_GiB": w["io_bytes"] / 2**30})
            except (OSError, ValueError, KeyError, IndexError):
                pass
            meta = (rdir / "meta.txt").read_text() if (rdir / "meta.txt").exists() else ""
            cm = meta_value(meta, "chmodel_msgs")
            row["chmodel_msgs"] = int(cm.split()[0]) if cm and cm.split()[0].isdigit() else ""
            t0, marks = None, {}
            log = (rdir / "kernel.log").read_text(errors="replace") if (rdir / "kernel.log").exists() else ""
            for line in log.splitlines():
                mt = DMESG_TS.match(line)
                if not mt:
                    continue
                ts = float(mt.group(1))
                if "fio-start" in line and t0 is None:
                    t0 = ts
                for key, pat in (("t_gc_s", "KSC2026: first GC"), ("t_queue_full_warn_s", "__allocate_work_queue_entry"),
                                 ("t_nvme_timeout_s", "timeout, aborting"), ("t_reset_s", "reset controller"),
                                 ("t_disable_s", "disable controller"), ("t_first_io_error_s", "I/O error, dev")):
                    if pat in line and key not in marks:
                        marks[key] = ts
            for key, ts in marks.items():
                row[key] = round(ts - t0, 3) if t0 is not None else ""
            out.append(row)
    return out


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
            wr.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})   # full precision


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
    """One panel per mapping unit: every variant (or cache mode) against bs; shaded = bs < mapping unit."""
    variants = sorted({a["variant"] for a in agg})
    if len(variants) < 2:
        return
    maps = [mp for mp in SIZES if any(a["map"] == mp for a in agg)]
    fig, axes = plt.subplots(1, len(maps), figsize=(3.4 * len(maps) + 1, 3.8), facecolor=SURFACE, squeeze=False)
    for ax, mp in zip(axes[0], maps):
        style(ax)
        for vi, v in enumerate(variants):
            pts = [(SIZES.index(a["bs"]), a["bw_MiBps_mean"], a["bw_MiBps_std"])
                   for a in agg if a["variant"] == v and a["map"] == mp]
            if pts:
                xs, ys, es = zip(*sorted(pts))
                ax.errorbar(xs, ys, yerr=es, color=SERIES[vi], linewidth=2, marker="o", markersize=5,
                            capsize=3, label=v)
        ax.axvspan(-0.5, SIZES.index(mp) - 0.5, color="#f0efec", zorder=0)
        ax.set_xticks(range(len(SIZES)), [s.upper() for s in SIZES], fontsize=8)
        ax.set_title(f"map {mp.upper()}", color=INK, fontsize=10, loc="left")
        ax.set_xlabel("fio block size", color=INK2, fontsize=9)
    axes[0][0].set_ylabel("write bandwidth (MiB/s)", color=INK2)
    axes[0][0].legend(frameon=False, fontsize=8, labelcolor=INK2)
    fig.suptitle("Variants compared, mean ± std (shaded: bs < mapping unit)", color=INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-12:
            break
    return h


def t_two_sided_p(t, df):
    """Two-sided p-value of Student's t (regularized incomplete beta), no scipy needed."""
    import math
    if df <= 0 or t != t:
        return float("nan")
    x = df / (df + t * t)
    a, b = df / 2.0, 0.5
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) if 0 < x < 1 else (1.0 if x >= 1 else 0.0)
    if x == 0 or x == 1:
        return 0.0 if x == 0 else 1.0
    if x < (a + 1) / (a + b + 2):
        ib = front * _betacf(a, b, x) / a
    else:
        ib = 1 - front * _betacf(b, a, 1 - x) / b
    return ib


def t_quantile_975(df):
    lo, hi = 0.0, 50.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if t_two_sided_p(mid, df) > 0.05:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cache_compare(rows, out):
    """Paired comparison of <v>_drop vs <v>_nodrop (same map, bs, rep). Writes cache_compare.csv / cache_pairs.csv."""
    import math
    by = {(r["variant"], r["map"], r["bs"], r["rep"]): r for r in rows}
    bases = sorted({r["variant"][: -len("_nodrop")] for r in rows if r["variant"].endswith("_nodrop")})
    metrics = ["bw_MiBps", "iops", "clat_mean_us", "clat_p99_us", "gc_onset_s", "bw_pre_gc_MiBps", "bw_post_gc_MiBps", "waf_total"]
    pair_rows, summ = [], []
    for b in bases:
        keys = sorted({(r["map"], r["bs"]) for r in rows if r["variant"] == f"{b}_nodrop"}, key=lambda k: (kib(k[0]), kib(k[1])))
        allrel = {m: [] for m in metrics}
        for mp, bs in keys:
            for m in metrics:
                diffs, rels, nd, dr = [], [], [], []
                for rep in (1, 2, 3, 4, 5):
                    a, c = by.get((f"{b}_nodrop", mp, bs, rep)), by.get((f"{b}_drop", mp, bs, rep))
                    if not a or not c or m not in a or m not in c:
                        continue
                    nd.append(a[m]); dr.append(c[m]); diffs.append(c[m] - a[m])
                    rel = (c[m] - a[m]) / a[m] * 100 if a[m] else float("nan")
                    rels.append(rel); allrel[m].append(rel)
                    if m == "bw_MiBps":
                        pair_rows.append({"variant": b, "map": mp, "bs": bs, "rep": rep, "nodrop_bw_MiBps": a[m], "drop_bw_MiBps": c[m], "diff_pct": rel})
                if len(diffs) < 2:
                    continue
                md, sd = statistics.fmean(diffs), statistics.stdev(diffs)
                t = md / (sd / math.sqrt(len(diffs))) if sd > 0 else float("inf") if md else 0.0
                summ.append({"variant": b, "map": mp, "bs": bs, "metric": m, "n_pairs": len(diffs),
                             "nodrop_mean": statistics.fmean(nd), "drop_mean": statistics.fmean(dr),
                             "mean_diff": md, "mean_diff_pct": statistics.fmean(rels), "sd_diff": sd,
                             "paired_t": t, "p_two_sided": t_two_sided_p(t, len(diffs) - 1) if sd > 0 else float("nan")})
        for m in metrics:
            v = [x for x in allrel[m] if x == x]
            if len(v) >= 2:
                mean, sd = statistics.fmean(v), statistics.stdev(v)
                half = t_quantile_975(len(v) - 1) * sd / math.sqrt(len(v))
                t = mean / (sd / math.sqrt(len(v))) if sd > 0 else float("nan")
                summ.append({"variant": b, "map": "ALL", "bs": "ALL", "metric": m, "n_pairs": len(v),
                             "mean_diff_pct": mean, "sd_diff": sd, "ci95_low_pct": mean - half, "ci95_high_pct": mean + half,
                             "paired_t": t, "p_two_sided": t_two_sided_p(t, len(v) - 1)})
    if summ:
        out.mkdir(parents=True, exist_ok=True)
        write_csv(out / "cache_compare.csv", summ)
        write_csv(out / "cache_pairs.csv", pair_rows)
    return summ


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
    global SIZES
    SIZES = sorted({r["map"] for r in rows} | {r["bs"] for r in rows}, key=kib)
    agg = aggregate(rows)
    write_csv(out / "summary_runs.csv", rows)
    write_csv(out / "summary_agg.csv", agg)
    failed = collect_failed(exp_dir)
    if failed:
        write_csv(out / "failed_runs.csv", failed)
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
    cache_compare(rows, out)
    print(f"{len(rows)} runs, {len(failed)} failed -> {out}")


if __name__ == "__main__":
    main()
