#!/usr/bin/env python3
"""KSC2026 NVMeVirt mapping-unit experiment — plotting tool (reads the results directly, works on partial data).

usage (from exp/, with ./.venv/bin/python):
  python plot.py list                                   # finished runs, available metrics
  python plot.py bs      --metric bw_MiBps              # metric vs fio bs, one line per mapping unit (panel per variant)
  python plot.py map     --metric iops --logy           # metric vs mapping unit, one line per bs
  python plot.py heatmap --metric waf_total --variant wbuffix
  python plot.py ts      --maps 128k --bss 4k,128k      # 0.5 s time series (bw|iops|clat|lat), dashed = first GC
  python plot.py compare --metric bw_MiBps              # base vs wbuffix, one panel per mapping unit
  python plot.py all                                    # standard set -> results/<EXP>/plots/

common options:
  --exp results/main_20261008   experiment directory (default: newest results/main_*)
  --variant base,wbuffix        variants to include
  --maps 4k,8k  --bss 4k,128k   restrict mapping units / block sizes
  --reps 1,2,3                  repetitions (ts)
  --logy                        logarithmic y axis
  --out file.png                output file (default: results/<EXP>/plots/<auto>.png)
  --show                        also open a window (needs a display)
"""
import argparse
import sys
from pathlib import Path

import matplotlib

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402  (collect / aggregate / palette)

SIZES = A.SIZES
METRICS = {
    "bw_MiBps": "write bandwidth, 60 s mean (MiB/s)",
    "iops": "IOPS, 60 s mean",
    "clat_mean_us": "mean completion latency (us)",
    "clat_p50_us": "p50 completion latency (us)",
    "clat_p99_us": "p99 completion latency (us)",
    "clat_p999_us": "p99.9 completion latency (us)",
    "lat_mean_us": "mean total latency (us)",
    "bw_first10s_MiBps": "bandwidth, first 10 s (MiB/s)",
    "bw_last20s_MiBps": "bandwidth, last 20 s (MiB/s)",
    "gc_onset_s": "first GC after fio start (s)",
    "bw_pre_gc_MiBps": "bandwidth before first GC (MiB/s)",
    "bw_post_gc_MiBps": "bandwidth after first GC (MiB/s)",
    "waf_gc": "WAF (GC only, mapping-unit pages)",
    "waf_total": "WAF total (NAND bytes / host bytes)",
    "gc_cnt": "GC victim lines (all partitions)",
    "written_GiB": "host data written in 60 s (GiB)",
    "fill_ratio": "host bytes written / device size",
    "chmodel_msgs": "NVMeVirt channel-model overflow messages",
}
TS_LOGS = {"bw": ("fio_bw.1.log", 1 / 1024, "write bandwidth (MiB/s)"),
           "iops": ("fio_iops.1.log", 1, "IOPS"),
           "clat": ("fio_clat.1.log", 1 / 1000, "completion latency (us)"),
           "lat": ("fio_lat.1.log", 1 / 1000, "total latency (us)")}


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["list", "bs", "map", "heatmap", "ts", "compare", "all"])
    ap.add_argument("--exp")
    ap.add_argument("--variant", default="base,wbuffix")
    ap.add_argument("--metric", default="bw_MiBps")
    ap.add_argument("--ts-metric", default="bw", choices=list(TS_LOGS))
    ap.add_argument("--maps", default=",".join(SIZES))
    ap.add_argument("--bss", default=",".join(SIZES))
    ap.add_argument("--reps", default="1,2,3")
    ap.add_argument("--logy", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    if a.show:   # analyze.py selected Agg at import; switch to an interactive backend when a window is wanted
        import matplotlib.pyplot as plt
        try:
            plt.switch_backend("TkAgg")
        except Exception as e:  # noqa: BLE001
            print(f"--show unavailable ({e}); saving files only")
            a.show = False
    return a


def exp_dir(arg):
    if arg:
        return Path(arg).resolve()
    cands = sorted((HERE / "results").glob("main_*"))
    if not cands:
        sys.exit("no results/main_* directory; pass --exp")
    return cands[-1]


def split(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def finish(fig, out, show):
    import matplotlib.pyplot as plt
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=170, facecolor=A.SURFACE)
    print(f"wrote {out}")
    if show:
        plt.show()
    plt.close(fig)


def agg_lookup(agg):
    return {(a["variant"], a["map"], a["bs"]): a for a in agg}


def plot_lines(agg, variants, metric, x_axis, maps, bss, logy, out, show):
    import matplotlib.pyplot as plt
    look = agg_lookup(agg)
    fig, axes = plt.subplots(1, len(variants), figsize=(6.4 * len(variants), 4.4), facecolor=A.SURFACE, squeeze=False,
                             sharey=True)
    xs_lab = bss if x_axis == "bs" else maps
    series = maps if x_axis == "bs" else bss
    for ax, v in zip(axes[0], variants):
        A.style(ax)
        for i, s in enumerate(series):
            pts = []
            for k, x in enumerate(xs_lab):
                key = (v, s, x) if x_axis == "bs" else (v, x, s)
                a = look.get(key)
                if a and f"{metric}_mean" in a:
                    pts.append((k, a[f"{metric}_mean"], a.get(f"{metric}_std", 0.0)))
            if pts:
                xk, ys, es = zip(*pts)
                lab = f"map {s.upper()}" if x_axis == "bs" else f"bs {s.upper()}"
                ax.errorbar(xk, ys, yerr=es, color=A.SERIES[SIZES.index(s) % len(A.SERIES)], linewidth=2, marker="o",
                            markersize=5, capsize=3, label=lab)
        ax.set_xticks(range(len(xs_lab)), [x.upper() for x in xs_lab])
        ax.set_xlabel("fio block size" if x_axis == "bs" else "FTL mapping unit", color=A.INK2)
        ax.set_title(v, color=A.INK, fontsize=11, loc="left")
        if logy:
            ax.set_yscale("log")
    axes[0][0].set_ylabel(METRICS.get(metric, metric), color=A.INK2)
    axes[0][-1].legend(frameon=False, fontsize=8, labelcolor=A.INK2, ncol=2)
    fig.suptitle(f"{METRICS.get(metric, metric)} — mean ± std over repetitions", color=A.INK, x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    finish(fig, out, show)


def plot_heatmaps(agg, variants, metric, out, show):
    import matplotlib.pyplot as plt
    import numpy as np
    look = agg_lookup(agg)
    fig, axes = plt.subplots(1, len(variants), figsize=(6.2 * len(variants), 4.8), facecolor=A.SURFACE, squeeze=False)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seqblue", A.SEQ_BLUE)
    grids = []
    for v in variants:
        g = np.full((len(SIZES), len(SIZES)), np.nan)
        for i, mp in enumerate(SIZES):
            for k, bs in enumerate(SIZES):
                a = look.get((v, mp, bs))
                if a and f"{metric}_mean" in a:
                    g[i, k] = a[f"{metric}_mean"]
        grids.append(g)
    vmax = np.nanmax([np.nanmax(g) for g in grids if not np.isnan(g).all()] or [1])
    for ax, v, g in zip(axes[0], variants, grids):
        im = ax.imshow(g, cmap=cmap, aspect="auto", origin="lower", vmin=0, vmax=vmax)
        for i in range(len(SIZES)):
            for k in range(len(SIZES)):
                if not np.isnan(g[i, k]):
                    val = g[i, k]
                    txt = f"{val:.0f}" if val >= 100 else f"{val:.2f}" if val < 10 else f"{val:.1f}"
                    ax.text(k, i, txt, ha="center", va="center", fontsize=8, color="#ffffff" if val > 0.55 * vmax else A.INK)
        ax.set_xticks(range(len(SIZES)), [s.upper() for s in SIZES])
        ax.set_yticks(range(len(SIZES)), [s.upper() for s in SIZES])
        ax.set_xlabel("fio block size", color=A.INK2)
        ax.set_ylabel("FTL mapping unit", color=A.INK2)
        ax.set_title(v, color=A.INK, fontsize=11, loc="left")
        ax.tick_params(colors=A.INK2, labelsize=9)
    cb = fig.colorbar(im, ax=list(axes[0]))
    cb.set_label(METRICS.get(metric, metric), color=A.INK2)
    fig.suptitle(METRICS.get(metric, metric), color=A.INK, x=0.01, ha="left", fontsize=11)
    finish(fig, out, show)


def read_ts(rdir, kind):
    fname, scale, _ = TS_LOGS[kind]
    t, v = A.read_log(rdir / fname)
    return t, v * scale


def plot_ts(exp, variants, maps, bss, reps, kind, logy, out, show):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(len(maps), len(bss), figsize=(4.2 * len(bss) + 1, 2.8 * len(maps) + 1), squeeze=False,
                             facecolor=A.SURFACE, sharex=True)
    color_i = 0
    handles = {}
    for i, mp in enumerate(maps):
        for k, bs in enumerate(bss):
            ax = axes[i][k]
            A.style(ax)
            ax.tick_params(labelsize=7)
            for vi, v in enumerate(variants):
                for r in reps:
                    rdir = exp / v / f"map{mp}_bs{bs}_r{r}"
                    if not (rdir / "DONE").exists():
                        continue
                    t, y = read_ts(rdir, kind)
                    idx = (vi * len(reps) + reps.index(r)) % len(A.SERIES)
                    h, = ax.plot(t, y, color=A.SERIES[idx], linewidth=1.0)
                    handles[f"{v} rep{r}"] = h
                    on = A.gc_info(rdir).get("gc_onset_s")
                    if on is not None:
                        ax.axvline(on, color=A.SERIES[idx], linestyle="--", linewidth=0.8)
            if logy:
                ax.set_yscale("log")
            ax.set_title(f"map {mp.upper()} / bs {bs.upper()}", color=A.INK, fontsize=9, loc="left")
            if k == 0:
                ax.set_ylabel(TS_LOGS[kind][2], color=A.INK2, fontsize=8)
            if i == len(maps) - 1:
                ax.set_xlabel("time since fio start (s)", color=A.INK2, fontsize=8)
            color_i += 1
    if handles:
        fig.legend(list(handles.values()), list(handles.keys()), loc="upper right", frameon=False, fontsize=8,
                   ncol=min(6, len(handles)))
    fig.suptitle(f"{TS_LOGS[kind][2]} over time (0.5 s average); dashed = first GC", color=A.INK, x=0.01, ha="left",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    finish(fig, out, show)


def plot_compare(agg, metric, maps, logy, out, show):
    import matplotlib.pyplot as plt
    look = agg_lookup(agg)
    variants = sorted({a["variant"] for a in agg})
    fig, axes = plt.subplots(1, len(maps), figsize=(3.3 * len(maps) + 1, 3.8), facecolor=A.SURFACE, squeeze=False)
    for ax, mp in zip(axes[0], maps):
        A.style(ax)
        for vi, v in enumerate(variants):
            pts = [(k, look[(v, mp, bs)][f"{metric}_mean"], look[(v, mp, bs)].get(f"{metric}_std", 0.0))
                   for k, bs in enumerate(SIZES) if (v, mp, bs) in look and f"{metric}_mean" in look[(v, mp, bs)]]
            if pts:
                xk, ys, es = zip(*pts)
                ax.errorbar(xk, ys, yerr=es, color=A.SERIES[vi], linewidth=2, marker="o", markersize=4, capsize=3, label=v)
        ax.axvspan(-0.5, SIZES.index(mp) - 0.5, color="#f0efec", zorder=0)   # bs < mapping unit
        ax.set_xticks(range(len(SIZES)), [s.upper() for s in SIZES], fontsize=7)
        ax.set_title(f"map {mp.upper()}", color=A.INK, fontsize=10, loc="left")
        if logy:
            ax.set_yscale("log")
    axes[0][0].set_ylabel(METRICS.get(metric, metric), color=A.INK2)
    axes[0][0].legend(frameon=False, fontsize=8, labelcolor=A.INK2)
    fig.suptitle(f"{METRICS.get(metric, metric)}: variants compared (shaded = bs < mapping unit)", color=A.INK, x=0.01,
                 ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    finish(fig, out, show)


def main():
    a = parse_args()
    exp = exp_dir(a.exp)
    rows, _ = A.collect(exp)
    if not rows:
        sys.exit(f"no finished runs under {exp}")
    agg = A.aggregate(rows)
    variants = [v for v in split(a.variant) if any(r["variant"] == v for r in rows)]
    maps, bss, reps = split(a.maps), split(a.bss), [int(x) for x in split(a.reps)]
    pdir = exp / "plots"
    out = Path(a.out) if a.out else None

    if a.cmd == "list":
        print(f"experiment: {exp}")
        for v in sorted({r["variant"] for r in rows}):
            done = [r for r in rows if r["variant"] == v]
            print(f"  {v}: {len(done)} finished runs")
        print("metrics:", ", ".join(METRICS))
        print("time-series kinds (ts --ts-metric):", ", ".join(TS_LOGS))
        return
    if a.cmd == "bs":
        plot_lines(agg, variants, a.metric, "bs", maps, bss, a.logy, out or pdir / f"bs_{a.metric}.png", a.show)
    elif a.cmd == "map":
        plot_lines(agg, variants, a.metric, "map", maps, bss, a.logy, out or pdir / f"map_{a.metric}.png", a.show)
    elif a.cmd == "heatmap":
        plot_heatmaps(agg, variants, a.metric, out or pdir / f"heatmap_{a.metric}.png", a.show)
    elif a.cmd == "ts":
        plot_ts(exp, variants, maps, bss, reps, a.ts_metric, a.logy,
                out or pdir / f"ts_{a.ts_metric}_{'-'.join(maps)}_{'-'.join(bss)}.png", a.show)
    elif a.cmd == "compare":
        plot_compare(agg, a.metric, maps, a.logy, out or pdir / f"compare_{a.metric}.png", a.show)
    elif a.cmd == "all":
        for m, logy in (("bw_MiBps", False), ("iops", True), ("clat_mean_us", True), ("clat_p99_us", True),
                        ("bw_pre_gc_MiBps", False), ("bw_post_gc_MiBps", False), ("gc_onset_s", False), ("waf_total", True)):
            plot_lines(agg, variants, m, "bs", SIZES, SIZES, logy, pdir / f"bs_{m}.png", False)
            plot_lines(agg, variants, m, "map", SIZES, SIZES, logy, pdir / f"map_{m}.png", False)
        for m in ("bw_MiBps", "waf_total", "gc_onset_s", "bw_post_gc_MiBps"):
            plot_heatmaps(agg, variants, m, pdir / f"heatmap_{m}.png", False)
        for kind in ("bw", "clat"):
            plot_ts(exp, variants, SIZES, SIZES, [1], kind, kind == "clat", pdir / f"ts_{kind}_all_rep1.png", False)
        for m in ("bw_MiBps", "clat_mean_us", "waf_total"):
            plot_compare(agg, m, SIZES, m != "bw_MiBps", pdir / f"compare_{m}.png", False)


if __name__ == "__main__":
    main()
