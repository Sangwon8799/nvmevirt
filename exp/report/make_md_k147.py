#!/usr/bin/env python3
"""Markdown result tables for the 2026-10-25 experiments (kernel 6.8.0-147), written into the hand-over log.

usage: python3 make_md_k147.py [DATE] [LOG.md]
  DATE   default 20261025
  LOG    default <repo>/EXPERIMENT_LOG_K147_ROCKSDB.md; the text between
         '<!-- BEGIN AUTO: tables -->' and '<!-- END AUTO: tables -->' is replaced (nothing else is touched).
reads   exp/results/{rand4x5,seq4x3,randbs,rand4x3}_k147_<D>/analysis/summary_runs.csv, rocksdb_ycsba_k147_<D>/analysis/
        and, for the kernel-142 comparison, exp/results/{main3x3,seq3x3,randbs}_20261008 (fio bandwidth logs)
"""
import csv
import re
import statistics
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
D = sys.argv[1] if len(sys.argv) > 1 else "20261025"
LOG = Path(sys.argv[2]) if len(sys.argv) > 2 else EXP.parent / "EXPERIMENT_LOG_K147_ROCKSDB.md"
BEGIN, END = "<!-- BEGIN AUTO: tables -->", "<!-- END AUTO: tables -->"


def kib(s):
    return int(str(s).rstrip("k").rstrip("K"))


def rows_of(path):
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def f(v, nd=1):
    if v in (None, ""):
        return "—"
    try:
        x = float(v)
    except ValueError:
        return str(v)
    if x != x:
        return "—"
    return f"{x:,.{nd}f}"


def grid(rows, rkey, ckey, vkey, rvals, cvals, nd=1, rlabel="", clabel=""):
    out = [f"| {rlabel} \\ {clabel} | " + " | ".join(str(c).upper() for c in cvals) + " |",
           "|---|" + "---:|" * len(cvals)]
    for rv in rvals:
        cells = []
        for cv in cvals:
            hit = [r for r in rows if r[rkey] == rv and r[ckey] == cv]
            cells.append(f(hit[0][vkey], nd) if hit and vkey in hit[0] else "—")
        out.append(f"| {str(rv).upper()} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def log_mean(rdir, t_max=60.0):
    """mean of the fio bandwidth log (0.5 s windows) over t <= t_max seconds, MiB/s"""
    p = rdir / "fio_bw.1.log"
    if not p.exists():
        return None
    v = []
    for line in p.read_text().splitlines():
        a = line.split(",")
        if len(a) >= 2 and int(a[0]) / 1000.0 <= t_max:
            v.append(float(a[1]) / 1024.0)
    return statistics.fmean(v) if v else None


def fio_section(title, exp_name, variants, note):
    rows = rows_of(RES / exp_name / "analysis" / "summary_runs.csv")
    if not rows:
        return f"### {title}\n\n(아직 결과 없음: results/{exp_name}/analysis/summary_runs.csv)\n"
    maps = sorted({r["map"] for r in rows}, key=kib)
    bss = sorted({r["bs"] for r in rows}, key=kib)
    parts = [f"### {title}\n", note, ""]
    for v in variants:
        vr = [r for r in rows if r["variant"] == v]
        if not vr:
            continue
        parts += [f"**{v}** — 120 초 평균 대역폭 (MiB/s), 행 = 매핑 단위, 열 = fio bs\n",
                  grid(vr, "map", "bs", "bw_MiBps", maps, bss, 1, "매핑", "bs"), "",
                  f"**{v}** — GC 이전 구간 평균 대역폭 (MiB/s)\n",
                  grid(vr, "map", "bs", "bw_pre_gc_MiBps", maps, bss, 1, "매핑", "bs"), "",
                  f"**{v}** — GC 이후 구간 평균 대역폭 (MiB/s)\n",
                  grid(vr, "map", "bs", "bw_post_gc_MiBps", maps, bss, 1, "매핑", "bs"), "",
                  f"**{v}** — 첫 GC 시각 (fio 시작 후 초)\n",
                  grid(vr, "map", "bs", "gc_onset_s", maps, bss, 2, "매핑", "bs"), "",
                  f"**{v}** — WAF_total (NAND 바이트 ÷ 호스트 바이트, 120 초 전체)\n",
                  grid(vr, "map", "bs", "waf_total", maps, bss, 2, "매핑", "bs"), "",
                  f"**{v}** — 평균 / p99 완료 지연 (µs)\n",
                  grid(vr, "map", "bs", "clat_mean_us", maps, bss, 0, "매핑", "bs"), "",
                  grid(vr, "map", "bs", "clat_p99_us", maps, bss, 0, "매핑", "bs"), ""]
        warn = [r for r in vr if r.get("kernel_warn") not in ("0", "", None) or r.get("chmodel_msgs") not in ("0", "", None)]
        parts.append(f"이상 신호: kernel_warn·chmodel_msgs 가 0 이 아닌 회차 {len(warn)} 개"
                     + (": " + ", ".join(f"map{r['map']}_bs{r['bs']}" for r in warn) if warn else "") + "\n")
    failed = rows_of(RES / exp_name / "analysis" / "failed_runs.csv")
    if failed:
        parts.append(f"FAILED 회차 {len(failed)} 개: " + ", ".join(f"{r['variant']}/map{r['map']}_bs{r['bs']}" for r in failed) + "\n")
    return "\n".join(parts)


def compare_142():
    """same (map, bs) on kernel 142 (60 s, 3 reps) and 147 (120 s, 1 run): first-60 s mean of the bandwidth log"""
    sets = [("랜덤 쓰기", "main3x3_20261008/wbuffix_nodrop", f"rand4x3_k147_{D}/wbuffix"),
            ("랜덤 쓰기 bs 8K·64K", "randbs_20261008/wbuffix", f"randbs_k147_{D}/wbuffix"),
            ("순차 쓰기 wbuffix", "seq3x3_20261008/wbuffix", f"seq4x3_k147_{D}/wbuffix"),
            ("순차 쓰기 merge", "seq3x3_20261008/merge", f"seq4x3_k147_{D}/merge")]
    out = ["| 실험 | 매핑 | bs | 142: 0–60 초 평균 (3 회 평균) | 147: 0–60 초 평균 (1 회) | 차이 % | 142 첫 GC (초) | 147 첫 GC (초) |",
           "|---|---|---|---:|---:|---:|---:|---:|"]
    diffs = []
    for name, old, new in sets:
        od, nd = RES / old, RES / new
        if not od.is_dir() or not nd.is_dir():
            continue
        new_gc = {(r["map"], r["bs"]): r for r in rows_of(nd.parent / "analysis" / "summary_runs.csv") if r["variant"] == nd.name}
        for rn in sorted(nd.glob("map*_bs*_r1"), key=lambda p: (kib(p.name.split("_")[0][3:]), kib(p.name.split("_")[1][2:]))):
            if not (rn / "DONE").exists():
                continue
            m = re.match(r"map(\d+k)_bs(\d+k)_r1", rn.name)
            mp, bs = m.group(1), m.group(2)
            olds = [log_mean(p) for p in sorted(od.glob(f"map{mp}_bs{bs}_r*")) if (p / "DONE").exists()]
            olds = [x for x in olds if x is not None]
            if not olds:
                continue
            o, n = statistics.fmean(olds), log_mean(rn)
            if n is None:
                continue
            dpc = 100 * (n - o) / o
            diffs.append(abs(dpc))
            og = statistics.fmean(float(r["gc_onset_s"]) for r in rows_of(od.parent / "analysis" / "summary_runs.csv")
                                  if r["variant"] == od.name and r["map"] == mp and r["bs"] == bs and r.get("gc_onset_s"))
            ng = new_gc.get((mp, bs), {}).get("gc_onset_s")
            out.append(f"| {name} | {mp.upper()} | {bs.upper()} | {f(o)} | {f(n)} | {dpc:+.2f} | {f(og, 2)} | {f(ng, 2)} |")
    if diffs:
        out.append(f"\n겹치는 {len(diffs)} 조합의 |차이|: 평균 {statistics.fmean(diffs):.2f} %, 최대 {max(diffs):.2f} %")
    return "\n".join(out)


def rocksdb_section():
    rows = rows_of(RES / f"rocksdb_ycsba_k147_{D}" / "analysis" / "summary_runs.csv")
    if not rows:
        return "### RocksDB / YCSB-A\n\n(아직 결과 없음)\n"
    maps = sorted({r["map_unit"] for r in rows}, key=kib)
    blks = sorted({r["block_size"] for r in rows}, key=kib)
    parts = ["### RocksDB / YCSB-A (32 회, 회차마다 1 회)\n",
             "행 = FTL 매핑 단위, 열 = RocksDB block_size. TPS = run 600 초의 YCSB `[OVERALL] Throughput`.\n"]
    for wal in ("off", "on"):
        wr = [r for r in rows if r["wal"] == wal]
        if not wr:
            continue
        parts += [f"**WAL {wal} — TPS (ops/s)**\n", grid(wr, "map_unit", "block_size", "tps_ops_s", maps, blks, 0, "매핑", "block"), "",
                  f"**WAL {wal} — READ p99 (µs)**\n", grid(wr, "map_unit", "block_size", "read_p99_us", maps, blks, 0, "매핑", "block"), "",
                  f"**WAL {wal} — UPDATE p99 (µs)**\n", grid(wr, "map_unit", "block_size", "update_p99_us", maps, blks, 0, "매핑", "block"), "",
                  f"**WAL {wal} — READ / UPDATE 평균 지연 (µs)**\n",
                  grid(wr, "map_unit", "block_size", "read_avg_us", maps, blks, 1, "매핑", "block"), "",
                  grid(wr, "map_unit", "block_size", "update_avg_us", maps, blks, 1, "매핑", "block"), "",
                  f"**WAL {wal} — run 동안 장치 읽기 MiB/s / 평균 읽기 요청 KiB / 장치 쓰기 MiB/s**\n",
                  grid(wr, "map_unit", "block_size", "run_dev_read_MiB_s", maps, blks, 1, "매핑", "block"), "",
                  grid(wr, "map_unit", "block_size", "run_dev_read_avg_req_KiB", maps, blks, 2, "매핑", "block"), "",
                  grid(wr, "map_unit", "block_size", "run_dev_write_MiB_s", maps, blks, 1, "매핑", "block"), "",
                  f"**WAL {wal} — 적재 시간 (초) / GC 횟수(세션 전체) / WAF(세션 전체)**\n",
                  grid(wr, "map_unit", "block_size", "load_wall_s", maps, blks, 1, "매핑", "block"), "",
                  grid(wr, "map_unit", "block_size", "ftl_gc_cnt", maps, blks, 0, "매핑", "block"), "",
                  grid(wr, "map_unit", "block_size", "ftl_waf_session", maps, blks, 2, "매핑", "block"), ""]
    # WAL on / off ratio
    ratio = []
    for r in rows:
        if r["wal"] != "on":
            continue
        off = [x for x in rows if x["wal"] == "off" and x["map_unit"] == r["map_unit"] and x["block_size"] == r["block_size"]]
        if off and float(off[0]["tps_ops_s"]):
            ratio.append({"map_unit": r["map_unit"], "block_size": r["block_size"],
                          "ratio": 100 * (float(r["tps_ops_s"]) / float(off[0]["tps_ops_s"]) - 1)})
    if ratio:
        parts += ["**WAL on 의 TPS 변화 (WAL off 대비 %)**\n", grid(ratio, "map_unit", "block_size", "ratio", maps, blks, 1, "매핑", "block"), ""]
    bad = [r for r in rows if r.get("read_not_ok") not in ("0", "") or r.get("update_not_ok") not in ("0", "")]
    parts.append(f"READ/UPDATE 가 OK 가 아닌 응답을 받은 회차: {len(bad)} 개. "
                 f"kernel_warn 이 0 이 아닌 회차: {sum(1 for r in rows if r.get('kernel_warn') not in ('0', '', None))} 개.\n")
    failed = rows_of(RES / f"rocksdb_ycsba_k147_{D}" / "analysis" / "failed_runs.csv")
    if failed:
        parts.append(f"FAILED 회차 {len(failed)} 개: " + ", ".join(r["run"] + " (" + r["reason"] + ")" for r in failed) + "\n")
    return "\n".join(parts)


def main():
    body = "\n".join([
        "## 6. 결과 표 (자동 생성: exp/report/make_md_k147.py — 손으로 고치지 말 것)\n",
        fio_section("fio 랜덤 쓰기 (rand4x5_k147: 매핑 4 × bs 5, wbuffix)", f"rand4x5_k147_{D}", ["wbuffix"],
                    "rand4x3_k147(bs 4/16/32K) 과 randbs_k147(bs 8/64K) 을 합친 보기. 블록 계층 병합은 커널 기본값."),
        fio_section("fio 순차 쓰기 (seq4x3_k147: 매핑 4 × bs 3 × 모델 2)", f"seq4x3_k147_{D}", ["wbuffix", "merge"],
                    "블록 계층 병합 끔(nomerges=2)."),
        "### 커널 142 결과와 비교 (같은 조합, 처음 60 초)\n",
        "142 는 60 초 × 3 회, 147 은 120 초 × 1 회라 전체 평균은 비교할 수 없다. 두 커널 모두 fio 대역폭 로그(0.5 초 평균)의 "
        "0–60 초 구간 평균으로 비교한다.\n",
        compare_142(), "",
        rocksdb_section(),
    ])
    text = LOG.read_text() if LOG.exists() else f"{BEGIN}\n{END}\n"
    if BEGIN not in text or END not in text:
        sys.exit(f"{LOG}: markers missing")
    a, rest = text.split(BEGIN, 1)
    _, b = rest.split(END, 1)
    LOG.write_text(a + BEGIN + "\n" + body + "\n" + END + b)
    print(f"tables written into {LOG}")


if __name__ == "__main__":
    main()
