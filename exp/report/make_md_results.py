#!/usr/bin/env python3
"""Fill the AUTO-RESULTS section of EXPERIMENT_LOG_FOR_CLAUDE.md with every number from an experiment.

usage: python3 exp/report/make_md_results.py exp/results/<EXP> [exp/results/<EXP2> ...]
       (the log is <repo>/EXPERIMENT_LOG_FOR_CLAUDE.md; the first experiment is the primary data set)

Written for another Claude, not for people: complete rather than pretty. Contents: run inventory, every aggregate
matrix (mean / std / min / max), the full per-run and aggregate CSVs, per-partition GC lines, a 1-s bandwidth
series for every run, the environment differences before/after, and the run.log tail.
"""
import csv
import difflib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import analyze as A  # noqa: E402

SIZES = list(A.SIZES)
EXP_DIRS = [Path(a).resolve() for a in sys.argv[1:]]
MD = EXP_DIRS[0].parents[2] / "EXPERIMENT_LOG_FOR_CLAUDE.md"
BEGIN, END = "<!-- AUTO-RESULTS-BEGIN -->", "<!-- AUTO-RESULTS-END -->"
METRICS = ["bw_MiBps", "iops", "clat_mean_us", "clat_p50_us", "clat_p99_us", "clat_p999_us", "lat_mean_us", "slat_mean_us",
           "bw_first10s_MiBps", "bw_last20s_MiBps", "gc_onset_s", "gc_onset_last_part_s", "bw_pre_gc_MiBps",
           "bw_post_gc_MiBps", "gc_cnt", "ftl_host_pgs", "ftl_gc_pgs", "waf_gc", "waf_total", "written_GiB",
           "fill_ratio", "chmodel_msgs", "kernel_warn"]


def kst(utc_str):
    """'YYYY-MM-DD HH:MM:SS' (server clock, UTC) -> same in KST (UTC+9)."""
    import datetime as dt
    t = dt.datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S") + dt.timedelta(hours=9)
    return t.strftime("%Y-%m-%d %H:%M:%S KST")


def kst_line(line):
    """Replace a leading '[YYYY-MM-DD HH:MM:SS]' (server log, UTC) by the KST time."""
    m = re.match(r"^(\s*)\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]", line)
    return f"{m.group(1)}[{kst(m.group(2))}]" + line[m.end():] if m else line


def g(v, nd=3):
    if v is None or v != v:
        return "NA"
    if isinstance(v, float):
        return f"{v:.{nd}f}" if abs(v) < 1e6 else f"{v:.0f}"
    return str(v)


def section(EXP_DIR, num, out):
    global SIZES
    rows, series = A.collect(EXP_DIR)
    rows.sort(key=lambda r: (r["variant"], A.kib(r["map"]), A.kib(r["bs"]), r["rep"]))
    SIZES[:] = sorted({r["map"] for r in rows} | {r["bs"] for r in rows}, key=A.kib) or list(A.SIZES)
    A.SIZES = SIZES
    agg = A.aggregate(rows) if rows else []
    look = {(a["variant"], a["map"], a["bs"]): a for a in agg}
    variants = sorted({r["variant"] for r in rows})
    w = out.append
    w(f"## 11.{num} {EXP_DIR.name}  (묶음 경로 repo/exp/results/{EXP_DIR.name}/)")
    w("")
    w(f"### 11.{num}.1 회차 목록")
    for v in variants:
        vr = [r for r in rows if r["variant"] == v]
        log = (EXP_DIR / v / "run.log").read_text(errors="replace") if (EXP_DIR / v / "run.log").exists() else ""
        ts = re.findall(r"^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]", log, re.M)
        w(f"- {v}: 완료 회차 {len(vr)} (DONE 있음). run.log 첫 시각 {kst(ts[0]) if ts else 'NA'}, 마지막 시각 {kst(ts[-1]) if ts else 'NA'}. "
          f"chmodel 오류 줄 합계 {sum(int(r.get('chmodel_msgs', 0) or 0) for r in vr):,}. "
          f"chmodel>0 회차 {sum(1 for r in vr if (r.get('chmodel_msgs') or 0) > 0)}. kernel_warn>0 회차 {sum(1 for r in vr if (r.get('kernel_warn') or 0) > 0)}.")
        missing = [f"map{m}_bs{b}_r{k}" for m in SIZES for b in SIZES for k in (1, 2, 3)
                   if not (EXP_DIR / v / f"map{m}_bs{b}_r{k}" / "DONE").exists()]
        failed = [p.parent.name for p in sorted((EXP_DIR / v).glob("*/FAILED"))]
        if failed:
            w(f"  - FAILED: {' '.join(failed)}")
        w(f"  - 미완료/없음 {len(missing)}: {' '.join(missing) if missing else '-'}")
        notes = [ln for ln in log.splitlines() if re.search(r"NOTE|WARNING|ERROR", ln)]
        if notes:
            w(f"  - run.log NOTE/WARNING/ERROR 줄 {len(notes)}개 (원본 로그 인용, 시각은 KST 로 변환):")
            for ln in notes:
                w(f"    - `{kst_line(ln.strip())}`")
    w("")
    w(f"### 11.{num}.2 조합별 행렬 (행 = 매핑 단위, 열 = fio bs). 칸 = mean ± std [min..max], n = 그 조합의 완료 회차 수(보통 3)")
    for v in variants:
        for m in METRICS:
            if not any(f"{m}_mean" in a for a in agg if a["variant"] == v):
                continue
            w(f"#### {EXP_DIR.name} · {v} · {m}")
            w("| map\\bs | " + " | ".join(s.upper() for s in SIZES) + " |")
            w("|---|" + "---|" * len(SIZES))
            for mp in SIZES:
                cells = []
                for bs in SIZES:
                    a = look.get((v, mp, bs))
                    if not a or f"{m}_mean" not in a:
                        cells.append("NA")
                        continue
                    cells.append(f"{g(a[m + '_mean'])} ± {g(a[m + '_std'])} [{g(a[m + '_min'])}..{g(a[m + '_max'])}]")
                w(f"| {mp.upper()} | " + " | ".join(cells) + " |")
            w("")
    if "base" in variants and "wbuffix" in variants:
        w(f"### 11.{num}.3 변형 비교 (wbuffix − base) / base, 60 s 평균 대역폭")
        w("| map\\bs | " + " | ".join(s.upper() for s in SIZES) + " |")
        w("|---|" + "---|" * len(SIZES))
        for mp in SIZES:
            cells = []
            for bs in SIZES:
                a, b = look.get(("base", mp, bs)), look.get(("wbuffix", mp, bs))
                if a and b and a["bw_MiBps_mean"]:
                    cells.append(f"{(b['bw_MiBps_mean'] - a['bw_MiBps_mean']) / a['bw_MiBps_mean'] * 100:+.2f}% "
                                 f"({g(a['bw_MiBps_mean'], 1)}→{g(b['bw_MiBps_mean'], 1)})")
                else:
                    cells.append("NA")
            w(f"| {mp.upper()} | " + " | ".join(cells) + " |")
        w("")
    cmp = A.cache_compare(rows, EXP_DIR / "analysis") if any(v.endswith("_drop") for v in variants) else []
    if cmp:
        w(f"### 11.{num}.3b OS 페이지 캐시 drop vs nodrop (같은 map·bs·rep 쌍; diff = drop − nodrop)")
        w("| variant | map | bs | metric | n | nodrop mean | drop mean | mean diff % | paired t | p (two-sided) | 95% CI % |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for c in cmp:
            ci = f"[{g(c.get('ci95_low_pct'))}, {g(c.get('ci95_high_pct'))}]" if "ci95_low_pct" in c else ""
            w(f"| {c['variant']} | {c['map']} | {c['bs']} | {c['metric']} | {c['n_pairs']} | {g(c.get('nodrop_mean'))} | "
              f"{g(c.get('drop_mean'))} | {g(c.get('mean_diff_pct'))} | {g(c.get('paired_t'))} | {g(c.get('p_two_sided'), 4)} | {ci} |")
        w("")
    w(f"### 11.{num}.4 회차별 전체 (analysis/summary_runs.csv 와 같은 값)")
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    w("```csv")
    w(",".join(cols))
    for r in rows:
        w(",".join(g(r.get(c), 6) if isinstance(r.get(c), float) else str(r.get(c, "")) for c in cols))
    w("```")
    w("")
    w(f"### 11.{num}.5 조합별 집계 전체 (analysis/summary_agg.csv 와 같은 값)")
    acols = []
    for a in agg:
        acols += [k for k in a if k not in acols]
    w("```csv")
    w(",".join(acols))
    for a in agg:
        w(",".join(g(a.get(c), 6) if isinstance(a.get(c), float) else str(a.get(c, "")) for c in acols))
    w("```")
    w("")
    w(f"### 11.{num}.6 파티션별 GC 로그 (회차마다: 첫 GC 줄의 fio 시작 기준 시각·내용, rmmod 통계)")
    w("```")
    for r in rows:
        rdir = EXP_DIR / r["variant"] / f"map{r['map']}_bs{r['bs']}_r{r['rep']}"
        run = (rdir / "dmesg_run.txt").read_text(errors="replace") if (rdir / "dmesg_run.txt").exists() else ""
        un = (rdir / "dmesg_unload.txt").read_text(errors="replace") if (rdir / "dmesg_unload.txt").exists() else ""
        t0 = None
        lines = []
        for ln in run.splitlines():
            m = A.DMESG_TS.match(ln)
            if not m:
                continue
            if "fio-start" in ln and t0 is None:
                t0 = float(m.group(1))
            elif "first GC" in ln and t0 is not None:
                lines.append(f"+{float(m.group(1)) - t0:.3f}s " + ln.split("KSC2026: ", 1)[-1])
        stats = [ln.split("KSC2026: ", 1)[-1] for ln in un.splitlines() if "KSC2026: stats" in ln]
        other = [ln for ln in (run + un).splitlines() if "KSC2026" not in ln and ln.strip()]
        w(f"[{r['variant']} map{r['map']} bs{r['bs']} r{r['rep']}]")
        for ln in lines + stats:
            w("  " + ln)
        for ln in other[:8]:
            w("  (kernel) " + ln)
    w("```")
    w("")
    w(f"### 11.{num}.7 1 초 평균 대역폭 시계열 (MiB/s, t=1..60 s, fio_bw.1.log 의 0.5 s 값 두 개 평균)")
    w("형식: variant map bs rep | gc_onset_s | 값 60개 (공백 구분)")
    w("```")
    for key in sorted(series, key=lambda k: (k[0], A.kib(k[1]), A.kib(k[2]), k[3])):
        t, bw, on = series[key]
        vals = []
        for sec in range(1, 61):
            sel = bw[(t > sec - 1 + 1e-6) & (t <= sec + 1e-6)]
            vals.append(f"{sel.mean():.0f}" if len(sel) else "NA")
        w(f"{key[0]} {key[1]} {key[2]} r{key[3]} | {g(on, 3)} | " + " ".join(vals))
    w("```")
    w("")
    w(f"### 11.{num}.8 실험 전후 환경 차이 (env_before vs env_after_*; 날짜·부하·여유 메모리 줄 제외)")
    eb = EXP_DIR / "env_before"
    ign = re.compile(r"loadavg|Mem:|Swap:|MemFree|MemAvailable|AnonHugePages|^\$ date|^\d{4}-\d\d-\d\dT|^\d+\.\d+ \d+\.\d+ \d+\.\d+")
    for ad in sorted(p for p in EXP_DIR.iterdir() if p.name.startswith("env_after")):
        w(f"- {ad.name}:")
        any_diff = False
        for f in sorted(eb.glob("*.txt")):
            if f.name == "12_dimm.txt" or not (ad / f.name).exists():
                continue
            a = [ln for ln in f.read_text(errors="replace").splitlines() if not ign.search(ln)]
            b = [ln for ln in (ad / f.name).read_text(errors="replace").splitlines() if not ign.search(ln)]
            d = [ln for ln in difflib.unified_diff(a, b, lineterm="", n=0) if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
            if d:
                any_diff = True
                w(f"  - {f.name}:")
                for ln in d[:40]:
                    w(f"    `{ln}`")
        if not any_diff:
            w("  - 차이 없음")
    w("")
    w(f"### 11.{num}.9 run_all 로그 끝 40 줄 (원본 로그, 시각은 KST 로 변환)")
    ra = EXP_DIR.parent / f"run_all_{EXP_DIR.name}.log"
    w("```")
    if ra.exists():
        for ln in ra.read_text(errors="replace").splitlines()[-40:]:
            w(kst_line(ln))
    w("```")
    w("")
    return len(rows)


def main():
    out = ["(이 절의 시각은 모두 KST 다. 서버 로그의 UTC 시각을 +9 시간 변환했다.)",
           f"자동 생성: exp/report/make_md_results.py {' '.join('results/' + d.name for d in EXP_DIRS)} "
           f"(첫 번째 = 주 데이터셋)", ""]
    n = 0
    for i, d in enumerate(EXP_DIRS, 1):
        n += section(d, i, out)
    text = MD.read_text()
    i, j = text.index(BEGIN), text.index(END)
    MD.write_text(text[:i + len(BEGIN)] + "\n" + "\n".join(out) + "\n" + text[j:])
    print(f"updated {MD} ({n} runs)")


if __name__ == "__main__":
    main()
