#!/usr/bin/env python3
"""Build the KSC2026 NVMeVirt mapping-unit experiment record (.docx, Korean).

usage:  python3 exp/report/make_report.py exp/results/<PRIMARY_EXP> [--supp exp/results/<SUPP_EXP>]
                                        [--seq exp/results/<SEQ_EXP>] [--out out.docx]
        PRIMARY = final data set (main3x3_*), SUPP = first-design data set (main_*, partial),
        SEQ = sequential-write experiment (seq3x3_*, models wbuffix and merge)

Everything is read from the repository: scripts (appendix), NVMeVirt diff, environment snapshots,
per-run results (exp/results/<EXP>/<variant>/...), analysis CSV/figures (exp/results/<EXP>/analysis/),
and the hand-written interpretation in exp/report/findings_ko.txt (findings_seq_ko.txt for the sequential experiment).
"""
import csv
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_helpers import Report  # noqa: E402

SIZES = ["4k", "8k", "16k", "32k", "64k", "128k"]
VARIANTS = ["base", "wbuffix"]
VNAME = {"base": "base (요청 설정 그대로)", "wbuffix": "wbuffix (쓰기 버퍼 수정)"}
UPSTREAM = "61c90f7758cbd9545b4a4727e89377bf88eab060"


def kib(s):
    return int(s[:-1])


def read(p):
    p = Path(p)
    return p.read_text(errors="replace") if p.exists() else ""


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True).stdout.strip()


def load_csv(p):
    rows = []
    if not Path(p).exists():
        return rows
    with open(p) as f:
        for r in csv.DictReader(f):
            for k, v in list(r.items()):
                try:
                    r[k] = float(v) if v not in ("", None) and k not in ("variant", "map", "bs") else v
                except ValueError:
                    pass
            rows.append(r)
    return rows


def last_snapshot(text):
    """env files written by several collect_env.sh calls hold several snapshots in a row; keep the last one.
    Every snapshot of a file starts with the same first '$ command' line."""
    lines = text.splitlines()
    if not lines:
        return text
    starts = [i for i, ln in enumerate(lines) if ln == lines[0]]
    return "\n".join(lines[starts[-1]:]) + "\n"


def fnum(v, nd=1):
    if v is None or v == "" or v != v:
        return "–"
    if abs(v) >= 1000 and nd <= 1:
        return f"{v:,.0f}"
    return f"{v:,.{nd}f}"


# ---------------------------------------------------------------------------- inputs
import argparse  # noqa: E402

_ap = argparse.ArgumentParser()
_ap.add_argument("primary")
_ap.add_argument("--supp")
_ap.add_argument("--seq")
_ap.add_argument("--rbs", help="random-write bs 8k/64k runs (results/randbs_*)")
_ap.add_argument("--rview", help="combined view of the primary nodrop runs + --rbs runs (results/rand3x5_*, link_runs.py)")
_ap.add_argument("--out")
_args = _ap.parse_args()
EXP_DIR = Path(_args.primary).resolve()
REPO = EXP_DIR.parents[2]
EXPD = REPO / "exp"
EXP = EXP_DIR.name
OUT = Path(_args.out) if _args.out else EXPD / "report" / "KSC2026_NVMeVirt_매핑단위_실험기록.docx"
ENV_B = EXP_DIR / "env_before"
FINDINGS = [ln.strip() for ln in read(EXPD / "report" / "findings_ko.txt").splitlines() if ln.strip() and not ln.startswith("#")]
FINDINGS_SEQ = [ln.strip() for ln in read(EXPD / "report" / "findings_seq_ko.txt").splitlines() if ln.strip() and not ln.startswith("#")]


def load_ds(path):
    if not path:
        return None
    d = Path(path).resolve()
    an = d / "analysis"
    runs = load_csv(an / "summary_runs.csv")
    sizes = sorted({r["map"] for r in runs} | {r["bs"] for r in runs}, key=kib) or list(SIZES)
    return {"dir": d, "name": d.name, "an": an, "agg": load_csv(an / "summary_agg.csv"), "runs": runs,
            "failed": load_csv(an / "failed_runs.csv"), "cache": load_csv(an / "cache_compare.csv"),
            "variants": sorted({r["variant"] for r in runs}), "sizes": sizes,
            "maps": sorted({r["map"] for r in runs}, key=kib) or sizes, "bss": sorted({r["bs"] for r in runs}, key=kib) or sizes}


PRI = load_ds(EXP_DIR)
SUP = load_ds(_args.supp)
SEQ = load_ds(_args.seq)
RBS = load_ds(_args.rbs)
RV = load_ds(_args.rview)
FINDINGS_RBS = [ln.strip() for ln in read(EXPD / "report" / "findings_randbs_ko.txt").splitlines() if ln.strip() and not ln.startswith("#")]
RBS_N = str(8 + bool(SEQ))            # chapter of the random-write bs 8k/64k experiment
POST_N = str(8 + bool(SEQ) + bool(RBS))   # chapter "실험 후 상태와 정리"
AGG, RUNS, AN = PRI["agg"], PRI["runs"], PRI["an"]


def agg(variant, mp, bs, ds=None):
    for a in (ds or PRI)["agg"]:
        if a["variant"] == variant and a["map"] == mp and a["bs"] == bs:
            return a
    return None


def matrix_rows(variant, metric, nd=1, with_std=True, mask_fn=None, ds=None):
    ds = ds or PRI
    rows = []
    for mp in ds["maps"]:
        row = [f"{mp.upper()}"]
        for bs in ds["bss"]:
            a = agg(variant, mp, bs, ds)
            if a is None or f"{metric}_mean" not in a or a[f"{metric}_mean"] in ("", None):
                row.append("–")
                continue
            m = a[f"{metric}_mean"]
            s = a.get(f"{metric}_std", 0.0) or 0.0
            cell = f"{fnum(m, nd)}" + (f"\n±{fnum(s, nd)}" if with_std else "")
            if a.get("n", 3) and a.get("n", 3) < 3:
                cell += f" (n={int(a['n'])})"
            if mask_fn and mask_fn(mp, bs):
                cell += " *"
            row.append(cell)
        rows.append(row)
    return rows


def kst(utc_str):
    """'YYYY-MM-DD HH:MM:SS' from the server logs (UTC) -> KST (UTC+9) for the document."""
    import datetime as dt
    t = dt.datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S") + dt.timedelta(hours=9)
    return t.strftime("%Y-%m-%d %H:%M:%S")


def run_window(variant, ds=None):
    log = read((ds or PRI)["dir"] / variant / "run.log")
    ts = re.findall(r"^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]", log, re.M)
    return (kst(ts[0]), kst(ts[-1])) if ts else ("–", "–")


def dmesg_geometry():
    out = {}
    src = SUP or PRI
    for mp in src["sizes"]:
        txt = ""
        for v in src["variants"]:
            for bs in src["sizes"]:
                txt = read(src["dir"] / v / f"map{mp}_bs{bs}_r1" / "dmesg_load.txt")
                if txt:
                    break
            if txt:
                break
        g = {}
        m = re.search(r"mapping unit=(\d+) B, flash page=(\d+) B, oneshot page=(\d+) B, pgs_per_blk=(\d+), "
                      r"blks_per_pl=(\d+), write buffer=(\d+) B", txt)
        if m:
            g.update(dict(zip(["map", "flash", "oneshot", "pgs_per_blk", "blks_per_pl", "wbuf"], map(int, m.groups()))))
        m = re.search(r"blk-size\(MiB,KiB\)=(\d+),(\d+) line-size\(MiB,KiB\)=(\d+),(\d+)", txt)
        if m:
            g["blk_kib"], g["line_kib"] = int(m.group(2)), int(m.group(4))
        m = re.search(r"lines=(\d+)", txt)
        if m:
            g["lines"] = int(m.group(1))
        m = re.search(r"Init FTL instance with \d+ channels \((\d+) pages\)", txt)
        if m:
            g["tt_pgs"] = int(m.group(1))
        m = re.search(r"FTL physical space: (\d+), logical space: (\d+)", txt)
        if m:
            g["phys"], g["logical"] = int(m.group(1)), int(m.group(2))
        m = re.search(r"ns 0/1: size (\d+) MiB", txt)
        if m:
            g["ns_mib"] = int(m.group(1))
        out[mp] = g
    return out


def env_line(fname, pattern, group=1, default="–"):
    m = re.search(pattern, read(ENV_B / fname), re.M)
    return m.group(group).strip() if m else default


# ---------------------------------------------------------------------------- document
R = Report()
GEOM = dmesg_geometry()


def recorded_head(ds):
    """first commit recorded for the data set (git_head.txt lines: '<date> <hash>' or '<hash>')"""
    for v in ds["variants"]:
        t = read(ds["dir"] / v / "git_head.txt").split()
        if t:
            return t[1] if len(t) > 1 else t[0]
    return git("rev-parse", "HEAD")


# Commits recorded in the raw data that were later rewritten before the first push (code identical, only the
# hand-over log changed): 1d6cd03 -> a93ef76 (credential string, 16:04 KST), then a93ef76 -> e598e75 and
# 2a462a3 -> 949ae38 (an e-mail address removed from the log, 18:3x KST). See section 8.
REWRITTEN = {"1d6cd036893f06bfe8aa8f6bb4327239bc4b720f": "e598e75", "a93ef76bbf990eafd1d0a5a9484a27a1b709ed9d": "e598e75",
             "2a462a3a518915e37fa313716bc9721801501e28": "949ae38"}
HEAD_REC = recorded_head(PRI)
HEAD = git("rev-parse", REWRITTEN.get(HEAD_REC, HEAD_REC)) or HEAD_REC
HEAD_NOTE = (f" (원자료에 적힌 커밋 1d6cd03·a93ef76 은 같은 코드로 다시 만든 {HEAD[:7]} 이다 — " + POST_N + " 절)" if HEAD_REC in REWRITTEN else "")
PUSH_TAG = os.environ.get("KSC_PUSH_TAG", "")            # set once main and the tag are pushed
SUDOERS_REMOVED = os.environ.get("KSC_SUDOERS_REMOVED", "")   # "HH:MM" KST when /etc/sudoers.d/nvmevirt-exp was removed
SUP_HEAD = recorded_head(SUP) if SUP else ""
SEQ_HEAD = git("rev-parse", recorded_head(SEQ)) if SEQ else ""
SUDOERS_REMOVED2 = os.environ.get("KSC_SUDOERS_REMOVED2", "")  # "HH:MM" KST, removal after the sequential-write experiment
SUDOERS_REMOVED3 = os.environ.get("KSC_SUDOERS_REMOVED3", "")  # "HH:MM" KST, removal after the random-write bs 8k/64k experiment
RBS_HEAD = git("rev-parse", recorded_head(RBS)) if RBS else ""
n_rbs = sum(1 for r in RBS["runs"]) if RBS else 0
n_pri = {v: sum(1 for r in RUNS if r["variant"] == v) for v in PRI["variants"]}
n_sup = {v: sum(1 for r in SUP["runs"] if r["variant"] == v) for v in SUP["variants"]} if SUP else {}
if SEQ:   # original model first, then the merge model
    SEQ["variants"] = [v for v in ("wbuffix", "merge") if v in SEQ["variants"]] + [v for v in SEQ["variants"] if v not in ("wbuffix", "merge")]
n_seq = {v: sum(1 for r in SEQ["runs"] if r["variant"] == v) for v in SEQ["variants"]} if SEQ else {}

R.title("NVMeVirt FTL 매핑 단위 실험 기록서", "KSC 2026 · FTL 매핑 단위 × fio 쓰기 크기 · 랜덤 쓰기(OS 페이지 캐시 drop 비교)"
        + (" · 순차 쓰기(쓰기 버퍼 병합 모델)" if SEQ else "") + (" · 랜덤 쓰기 bs 8K·64K 추가" if RBS else ""))
R.table(["항목", "내용"], [
    ["주 데이터셋", f"{EXP} — 매핑 4K·16K·32K × bs 4K·16K·32K × 3 회 × 페이지 캐시 drop/no-drop, wbuffix 모델 "
     f"({' + '.join(f'{v} {n}회' for v, n in n_pri.items())})"],
    ["보조 데이터셋", (f"{SUP['name']} — 첫 설계(매핑 4–128K × bs 4–128K × 3 회 × base·wbuffix) 중 설계 변경 전까지 측정한 부분 "
                    f"({' + '.join(f'{v} {n}회' for v, n in n_sup.items())}, FAILED {len(SUP['failed'])}회)") if SUP else "–"],
    *([["추가 실험 (순차 쓰기)", f"{SEQ['name']} — 매핑 4K·16K·32K × bs 4K·16K·32K × 3 회, fio 순차 쓰기, 모델 wbuffix·merge, 페이지 캐시 그대로 "
         f"({' + '.join(f'{v} {n}회' for v, n in n_seq.items())}) — 8 절"]] if SEQ else []),
    *([["추가 실험 (랜덤 쓰기 bs 8K·64K)", f"{RBS['name']} — 매핑 4K·16K·32K × bs 8K·64K × 3 회, wbuffix, 페이지 캐시 그대로 ({n_rbs}회). "
         f"주 데이터셋 nodrop 의 bs 4K·16K·32K 와 합친 매핑 3 × bs 5 보기: {RV['name'] if RV else '–'} — {RBS_N} 절"]] if RBS else []),
    ["작성일 · 시각 기준", "2026-10-08 · 이 문서의 시각은 모두 KST (서버 시계와 원자료 로그는 UTC = KST − 9 시간)"],
    ["실험 수행", "Sangwon8799 (실험 서버 dccearth), 스크립트 작성·실행·기록: Claude Code (Claude Opus 5.5)"],
    ["저장소", "github.com/Sangwon8799/nvmevirt (main)\n서버: 실험 중 /home/dccearth/jsw/KSC2026/nvmevirt → 실험 후 /home/dccearth/jsw/nvmevirt 로 이동"],
    ["주 데이터셋 소스 커밋", HEAD + HEAD_NOTE],
    *([["순차 쓰기 소스 커밋", SEQ_HEAD + " (주 데이터셋 커밋 + 쓰기 버퍼 병합 모델·순차 쓰기 스크립트)"]] if SEQ else []),
    *([["랜덤 bs 8K·64K 소스 커밋", RBS_HEAD + " (wbuffix 모듈은 주 데이터셋과 같은 파일)"]] if RBS else []),
    ["NVMeVirt 원본", f"github.com/snu-csl/nvmevirt @ {UPSTREAM[:7]} (2026-05-21)"],
], widths=[3.6, 13.4], size=9)
R.p("이 문서는 실험 시작부터 결과를 얻기까지의 전 과정을 기록한다. 다른 사람이 같은 서버 구성에서 문서만 보고 같은 실험을 다시 할 수 있도록 "
    "환경·버전·바꾼 설정값·사용한 스크립트 전문·실행 순서·결과를 모두 적었다. 진행 중 실험 설계가 한 번 바뀌었으며(1.3 절), 바뀐 최종 설계의 결과가 주 데이터셋이다."
    + (" 그 뒤 같은 3 × 3 설계로 순차 쓰기를 추가로 측정했다(8 절)." if SEQ else "")
    + (f" 이어서 랜덤 쓰기에 bs 8K·64K 를 추가로 측정해 bs 를 5 단계로 넓혔다({RBS_N} 절)." if RBS else ""), size=9.5)
R.toc()
R.page_break()

# ============================================================================ 1
R.h("1. 실험 개요")
R.h("1.1 목적", 2)
R.p("고용량 SSD 는 4 KiB 매핑을 유지하면 L2P(논리→물리) 매핑 표가 용량의 약 0.1 % 만큼 DRAM 을 차지한다(1 TB 에 약 1 GB). "
    "매핑 단위를 16 KiB 이상으로 키우면 DRAM 은 줄지만, 매핑 단위보다 작은 쓰기는 매핑 단위 전체를 새로 써야 하므로 성능이 떨어질 수 있다. "
    "이 실험은 NVMeVirt(커널 모듈 기반 NVMe SSD 에뮬레이터)의 conventional SSD 모델에서 FTL 매핑 단위를 바꾸고, fio 랜덤 쓰기 블록 크기별로 "
    "대역폭(BW), IOPS, 완료 지연(clat)을 잰다. 연구 계획(연구 계획 흐름.docx)의 「(4k mapping ssd) randwrite … → BW, clat / (16k/32k mapping ssd) …」 를 따른다. "
    "또한 OS 페이지 캐시를 비우는 명령(echo 3 > /proc/sys/vm/drop_caches)을 실험 전에 실행하는지에 따라 결과가 달라지는지 확인한다."
    + (" 추가로 같은 매핑 단위·bs 조합에서 순차 쓰기를 측정한다. 이때 NVMeVirt 가 매핑 단위보다 작은 쓰기를 쓰기 버퍼에서 합치지 않는 한계가 결과를 좌우하므로, "
       "원래 모델(wbuffix)과 이 연구에서 추가한 쓰기 버퍼 병합 모델(merge)을 함께 잰다(8 절)." if SEQ else ""))
R.h("1.2 최종 실험 행렬과 고정 조건 (주 데이터셋)", 2)
R.table(["구분", "값"], [
    ["변수 ① FTL 매핑 단위", "4K, 16K, 32K (매핑 단위별로 모듈을 따로 빌드)"],
    ["변수 ② fio 블록 크기(bs)", "4K, 16K, 32K"],
    ["변수 ③ OS 페이지 캐시", "nodrop: 그대로 / drop: insmod 직후 sync; echo 3 > /proc/sys/vm/drop_caches. 같은 (매핑, bs, 회차)에서 두 조건을 연달아 측정하며, 순서는 홀수 회차 nodrop→drop, 짝수 회차 drop→nodrop"],
    ["반복", "조합마다 3 회 (회차마다 rmmod → insmod 로 장치 초기화) — 9 × 2 × 3 = 54 회"],
    ["NVMeVirt 모델", "wbuffix = 요청 설정 + 쓰기 버퍼 계산 수정 1 줄 (5.4 절; 사용자 선택). 요청 설정 그대로인 base 의 결과는 보조 데이터셋(7 절)"],
    ["NVMeVirt 모드", "Conventional SSD (SAMSUNG_970PRO 묶음), 블록 2 MiB (BLKS_PER_PLN = 384), flash page 32 KiB"],
    ["저장 용량", "예약 메모리 12 GiB (물리 주소 12–24 GiB), 호스트에 보이는 용량 11.21 GiB (OP 7 %)"],
    ["NVMeVirt CPU", "3 개: cpu3 = 디스패처, cpu4·cpu5 = I/O 워커 (isolcpus=3-5)"],
    ["fio", "ioengine=libaio, direct=1, rw=randwrite, iodepth=32, numjobs=1, runtime=60 s, ramp_time=0, 장치 전체"],
    ["측정값", "60 s 평균 BW·IOPS·clat(평균, p50, p99, p99.9), 0.5 s 간격 시계열, 첫 GC 시각, GC 전/후 BW, 쓰기 증폭(WAF)"],
], widths=[4.5, 12.5], size=9, caption="최종 실험 행렬과 고정 조건")
R.h("1.3 실험 설계 변경 경위", 2)
R.table(["시각 (KST)", "내용"], [
    ["13:4x", "첫 지시: 매핑 4·8·16·32·64·128K, 64K 이상은 flash page = 매핑 단위, BLK 2 MiB, 3 회 반복, 60 s, ramp_time 0 등. bs 는 연구 계획에 따라 4–128K 로 정함"],
    ["13:49–15:22", "NVMeVirt 코드 감사(에이전트 51 개): 매핑 단위보다 작은 쓰기에서 쓰기 버퍼가 과다 반환되는 결함 발견(5.4 절)"],
    ["14:20–14:46", "첫 설계 6 × 6 × 3 × {base, wbuffix} 시작 → base 매핑 32K·bs 16K 에서 가상 장치 멈춤(5.6 절)으로 스크립트 중단"],
    ["14:49–15:51", "실패 회차를 기록하고 계속하도록 고친 뒤 wbuffix 부터 재개 (wbuffix 53 회 완료)"],
    ["15:5x", "선배 요청: 매핑·bs 를 4K·16K·32K 로 줄이고, drop_caches 사용 여부에 따른 차이를 확인 → 15:51:23 회차 경계에서 중단"],
    ["15:5x", "모델 선택: base·wbuffix 차이를 설명한 뒤 사용자가 wbuffix 만 선택, drop/no-drop 은 회차마다 교대로 측정하기로 함"],
    ["16:00:35–", "최종 설계(주 데이터셋) 실행 (17:03:57 완료)"],
    *([["19:53", "사용자 요청: 순차 쓰기도 같은 3 × 3 으로 측정. NVMeVirt 가 매핑 단위보다 작은 쓰기를 쓰기 버퍼에서 합치지 않는 한계(5.5 절)를 설명했고, "
        "사용자가 '원래 모델(wbuffix)과 병합 모델(merge) 둘 다 측정', '페이지 캐시 nodrop 만'을 골랐다"],
       ["19:58–20:13", "쓰기 버퍼 병합 모델(WBUF_MERGE) 작성(19:58–19:59) → 에이전트 5 개의 독립 코드 검토(20:01–20:13, 결함 없음, 8.2 절) → 커밋 66446ea, merge 모듈 빌드"],
       ["20:18–20:23", "사전 점검: 커널 기본 설정에서 블록 계층이 순차 4K 요청을 평균 약 120 KiB 로 합치는 것을 발견 → 순차 쓰기는 nomerges=2 로 측정 (8.3 절)"],
       ["20:23:24–21:26:45", "순차 쓰기 실험 실행 (8 절)"]] if SEQ else []),
    *([["22:08", "사용자 요청: 랜덤 쓰기에 8K·64K 도 측정. 사용자가 'bs 만 추가(매핑은 4K·16K·32K 그대로)', '새 조합만 측정하고 기존 bs 4K·16K·32K 값은 주 데이터셋 nodrop 값을 재사용'을 골랐다"],
       ["22:11:48–", f"랜덤 쓰기 bs 8K·64K 실험 실행 ({RBS_N} 절)"]] if RBS else []),
], widths=[2.8, 14.2], size=8.5, caption="설계 변경 경위")
if FINDINGS:
    R.h("1.4 결과 요약", 2)
    R.bullets(FINDINGS[:10])
if SEQ and FINDINGS_SEQ:
    R.h("1.5 순차 쓰기 추가 실험 결과 요약", 2)
    R.bullets(FINDINGS_SEQ[:6])
if RBS and FINDINGS_RBS:
    R.h("1.6 랜덤 쓰기 bs 8K·64K 추가 실험 결과 요약", 2)
    R.bullets(FINDINGS_RBS[:5])

# ============================================================================ 2
R.h("2. 실험 환경")
R.h("2.1 하드웨어", 2)
_dimm_src = ENV_B / "12_dimm.txt"
if not _dimm_src.exists() and SUP:
    _dimm_src = SUP["dir"] / "env_before" / "12_dimm.txt"   # recorded once (sudo dmidecode -t memory, 14:22 KST)
dimm = read(_dimm_src)
dimms = re.findall(r"Size: (\d+ GB)\nLocator: (\S+)\nType: (\S+)\nSpeed: ([^\n]+)\nManufacturer: (\S+)\nPart Number: (\S+)", dimm)
dimm_txt = "\n".join(f"{loc}: {sz} {ty}-{sp.split()[0]} {mf} {pn}" for sz, loc, ty, sp, mf, pn in dimms) or "–"
R.table(["항목", "값"], [
    ["서버(호스트명)", env_line("00_date.txt", r"^\$ hostname\n(.*)$")],
    ["메인보드", env_line("06_platform.txt", r"board_vendor:(.*)$") + " " + env_line("06_platform.txt", r"board_name:(.*)$")],
    ["BIOS", env_line("06_platform.txt", r"bios_version:(.*)$") + " (" + env_line("06_platform.txt", r"bios_date:(.*)$") + ")"],
    ["CPU", env_line("03_cpu.txt", r"^Model name:\s+(.*)$") + f"\nOS 에 보이는 CPU {env_line('03_cpu.txt', r'^CPU\(s\):\s+(\d+)')}개 "
     f"(코어당 스레드 {env_line('03_cpu.txt', r'^Thread\(s\) per core:\s+(\d+)')}), 최대 {env_line('03_cpu.txt', r'^CPU max MHz:\s+([\d.]+)')} MHz, "
     f"L3 {env_line('03_cpu.txt', r'^L3 cache:\s+(.*)$')}"],
    ["메모리", f"총 24 GB (DDR5-5600, 슬롯 4 개 중 2 개 사용, 최대 128 GB)\n{dimm_txt}\n(DIMMA1·DIMMB1 비어 있음; 출처 {_dimm_src.parent.parent.name}/env_before/12_dimm.txt, sudo dmidecode -t memory)"],
    ["NUMA", env_line("03_cpu.txt", r"^NUMA node\(s\):\s+(\d+)") + " 노드"],
    ["시스템 디스크", "Samsung SSD 980 PRO 500GB (/dev/nvme0n1, 루트 파일시스템) — 실험 대상 아님"],
    ["실험 대상 장치", "NVMeVirt 가상 NVMe (모델 CSL_Virt_MN_01, 적재 후 /dev/nvme1n1)"],
], widths=[3.5, 13.5], size=9, caption="하드웨어")
R.h("2.2 운영체제·커널·부팅 설정", 2)
R.table(["항목", "값"], [
    ["OS", env_line("01_os.txt", r'^PRETTY_NAME="(.*)"')],
    ["커널", env_line("01_os.txt", r"^Linux \S+ (\S+)") + "  (" + env_line("01_os.txt", r"^Linux version \S+ \S+ \((.*?)\) #") + ")"],
    ["커널 명령줄", env_line("02_boot.txt", r"^BOOT_IMAGE=.*?(memmap=.*)$")],
    ["/etc/default/grub", env_line("02_boot.txt", r'^(GRUB_CMDLINE_LINUX=".*")$')],
    ["격리 CPU", env_line("02_boot.txt", r"isolated\n(.*)$")],
    ["예약 메모리 확인", "/proc/iomem: 300000000-5ffffffff : Reserved (12.000–24.000 GiB, 12 GiB)\n"
     "e820 user map: [mem 0x0000000300000000-0x00000005ffffffff] reserved (스냅샷 아님 — 14:06 KST 에 sudo dmesg 로 직접 확인. "
     "env_before 의 dmesg e820 grep 은 커널 링 버퍼가 이미 덮여 비어 있다, 부록 C)"],
    ["CPU 주파수", f"intel_pstate {env_line('04_cpufreq.txt', r'^(active|passive)')}, governor powersave, EPP balance_performance, "
     f"터보 켜짐(no_turbo={env_line('04_cpufreq.txt', r'^(?:active|passive)\n(\d)')}), 800–5100 MHz (모두 기본값, 바꾸지 않음)"],
    ["THP", env_line("05_memory.txt", r"^(always.*|.*\[madvise\].*)$")],
    ["콘솔 로그 레벨", "kernel.printk = 4 4 1 7 (기본값) — KERN_ERR 메시지는 tty0 콘솔에도 출력됨 (5.4 절 참고)"],
    ["dmesg 제한", "kernel.dmesg_restrict = 1 → dmesg 는 sudo 로 읽음"],
], widths=[3.5, 13.5], size=9, caption="운영체제·커널·부팅 설정")
R.h("2.3 소프트웨어 버전", 2)
ver = read(ENV_B / "07_versions.txt")
pk = dict(re.findall(r"^(\S+?)(?::amd64)?\t(\S+)$", ver, re.M))
venv_req = dict(re.findall(r"^(\S+)==(\S+)$", read(EXPD / "requirements.txt"), re.M))
R.table(["소프트웨어", "버전", "비고"], [
    ["fio", env_line("07_versions.txt", r"^(fio-\S+)"), f"Ubuntu 패키지 {pk.get('fio', '–')}"],
    ["libaio", pk.get("libaio1t64", "–"), "ioengine=libaio"],
    ["gcc", env_line("07_versions.txt", r"^gcc \(.*\) (\S+)$"), f"패키지 gcc-13 {pk.get('gcc-13', '–')} (커널 빌드에 쓴 것과 같은 버전)"],
    ["make", env_line("07_versions.txt", r"^GNU Make (\S+)"), ""],
    ["커널 헤더", pk.get(f"linux-headers-{env_line('01_os.txt', r'^Linux \S+ (\S+)')}", "–"), "NVMeVirt 모듈 빌드용"],
    ["nvme-cli", env_line("07_versions.txt", r"^nvme version (\S+)"), "장치 정보 기록용"],
    ["util-linux (dmesg)", env_line("07_versions.txt", r"util-linux (\S+)"), ""],
    ["Python", env_line("07_versions.txt", r"^Python (\S+)"), "분석·문서 생성 (exp/.venv)"],
    ["numpy / matplotlib / python-docx", f"{venv_req.get('numpy', '–')} / {venv_req.get('matplotlib', '–')} / {venv_req.get('python-docx', '–')}", "exp/requirements.txt"],
    ["git", env_line("07_versions.txt", r"^git version (\S+)"), ""],
    ["bash", env_line("07_versions.txt", r"^GNU bash, version (\S+)"), ""],
], widths=[4.5, 4.5, 8.0], size=9, caption="소프트웨어 버전")
R.h("2.4 NVMeVirt 버전", 2)
R.table(["항목", "값"], [
    ["원본 저장소", "https://github.com/snu-csl/nvmevirt (branch main)"],
    ["원본 커밋", f"{UPSTREAM}\n2026-05-21 11:05:11 +0900 · Merge pull request #72 (zns append return slba)"],
    ["모듈 버전 문자열", "NVMeVirt: Version 1.10 for >> Samsung 970 Pro SSD <<  (적재 시 dmesg)"],
    ["실험용 포크", "https://github.com/Sangwon8799/nvmevirt (원본 이력 유지, 소스는 nvmevirt/ 하위 폴더로 이동)"],
    ["포크 커밋 (실험 시점)", git("log", "--format=%h %s", f"{UPSTREAM}..{HEAD}").replace("\n", "\n") or HEAD],
], widths=[3.5, 13.5], size=9, caption="NVMeVirt 버전")
R.h("2.5 CPU 배치", 2)
R.table(["CPU", "역할", "근거"], [
    ["cpu0–2", "운영체제, fio(고정하지 않음 — isolcpus 때문에 0–2 에서만 실행됨), dmesg 기록 프로세스", "isolcpus=3-5"],
    ["cpu3", "NVMeVirt 디스패처 (I/O 명령 처리, FTL, GC 를 모두 이 스레드가 수행)", "cpus= 의 첫 값 · dmesg 'nvmev_dispatcher started on cpu 3'"],
    ["cpu4", "NVMeVirt I/O 워커 0 (데이터 복사·완료 처리) — 실제로 모든 I/O 를 처리", "dmesg 'nvmev_io_worker_0 started on cpu 4'"],
    ["cpu5", "NVMeVirt I/O 워커 1 — I/O 는 받지 않고 폴링만 함. 가상 장치의 인터럽트(IRQ 15)가 이 CPU 로 전달되어 호스트 nvme 완료 처리가 여기서 실행됨",
     "가상 장치가 MSI-X 없이 레거시 IO-APIC IRQ 15 하나(nvme1q0·nvme1q1 공유)만 받아 I/O 큐가 1 개('1/0/0 default/read/poll queues'). "
     "CONFIG_NVMEV_IO_WORKER_BY_SQ 로 큐 번호에 따라 워커를 고르므로 워커 0 만 쓰인다. /proc/irq/15/effective_affinity_list = 5 (smp_affinity_list 0-5), irqbalance 미설치"],
], widths=[2.0, 8.0, 7.0], size=8.5, caption="CPU 배치")

# ============================================================================ 3
R.h("3. 실험 전 준비 (세팅)")
R.h("3.1 이 실험 이전에 해 둔 서버 설정", 2)
R.p("다음은 이 실험 세션 전에 이미 적용되어 있던 설정이다. 실험 전에 그대로인지 확인만 했다(2.2 절의 값).")
R.code("""# /etc/default/grub — NVMeVirt 저장 공간 예약(12 GiB, 물리 주소 12 GiB 부터)과 NVMeVirt 전용 CPU 격리
GRUB_CMDLINE_LINUX="memmap=12G\\\\\\$12G isolcpus=3-5"
sudo update-grub
sudo reboot
# 확인
cat /proc/cmdline                       # ... memmap=12G$12G isolcpus=3-5
sudo grep -i 'System RAM\\|Reserved' /proc/iomem   # 300000000-5ffffffff : Reserved
sudo apt install fio                    # fio 3.36 (Ubuntu 24.04 패키지)
# 모듈 빌드·분석·실행에 필요한 나머지 패키지 — 이 서버에는 이미 설치되어 있었다(버전은 표 5). 새 서버에서는 함께 설치한다.
sudo apt install build-essential linux-headers-$(uname -r) python3-venv tmux nvme-cli git
# irqbalance 는 설치되어 있지 않다(dpkg-query -W irqbalance → 없음). 설치된 서버라면 끄고 재부팅해 IRQ 위치를 고정한다.
# NVMeVirt 적재 후 확인: grep nvme1 /proc/interrupts; cat /proc/irq/<IRQ>/effective_affinity_list   # 이 서버: IRQ 15 → cpu5 (2.5 절)""")
R.h("3.2 저장소 준비 (fork → 하위 폴더 구성 → push)", 2)
R.p("원본 이력을 그대로 둔 채 모든 파일을 nvmevirt/ 하위 폴더로 옮기고(내용 변경 없음), 실험용 파일은 exp/ 에 두었다. "
    "GitHub 에는 사용자가 만든 빈 저장소 Sangwon8799/nvmevirt 에 올렸다(서버에는 GitHub 키가 없고, 사용자 PC 의 ssh-agent 를 SSH agent forwarding 으로 사용).")
R.code("""cd /home/dccearth/jsw/KSC2026
git clone https://github.com/snu-csl/nvmevirt.git nvmevirt && cd nvmevirt   # 61c90f7
git remote rename origin upstream
mkdir nvmevirt
git ls-tree --name-only HEAD | while read f; do git mv "$f" nvmevirt/; done
git commit -m "Move NVMeVirt sources into nvmevirt/ subdirectory"
# (소스 수정 · exp/ 추가 후 커밋 — 3.4 절, 부록 A)
git remote add origin git@github.com:Sangwon8799/nvmevirt.git
git push -u origin main""")
R.table(["경로", "내용"], [
    ["nvmevirt/", "NVMeVirt 커널 모듈 소스 (원본 + 3.4 절 수정)"],
    ["exp/common.sh", "공통 설정값 (memmap, cpus, 매핑 단위·bs 목록, 반복 횟수, fio 값, 빌드 변형)"],
    ["exp/build_modules.sh", "매핑 단위별 nvmev.ko 빌드 → exp/modules/<변형>/nvmev_map<단위>.ko (+ SHA256SUMS)"],
    ["exp/run_experiment.sh", "회차 실행: rmmod → insmod → fio 60 s → rmmod, 커널 로그 기록, 이어서 하기 지원"],
    ["exp/collect_env.sh", "실험 전·후 환경 스냅샷"],
    ["exp/jobs/randwrite.fio.in", "fio 작업 파일 틀 (회차마다 값을 채워 job.fio 로 저장)"],
    ["exp/jobs/seqwrite.fio.in", "순차 쓰기 틀 (rw=write; 8 절)"],
    ["exp/analyze.py", "결과 집계(CSV), drop/no-drop 쌍 비교, 그림"],
    ["exp/plot.py", "그래프 도구 (bs/map/heatmap/ts/compare/all)"],
    ["exp/run_all.sh", "최종 설계: wbuffix 모듈 → 3×3×3×{nodrop, drop} → 분석"],
    ["exp/run_all_6x6.sh", "첫 설계: 빌드 → base 6×6×3 → wbuffix 6×6×3 → 분석 (보조 데이터셋에 사용)"],
    ["exp/run_all_seq.sh", "순차 쓰기: 3×3×3 × {wbuffix, merge}, nomerges=2 → 분석"],
    ["exp/make_gallery.py", "한 실험의 모든 그림을 HTML 한 파일로 모음"],
    ["exp/run_all_rand_bs.sh", "랜덤 쓰기 bs 8K·64K: 매핑 3 × bs 2 × 3 회 → 분석 → link_runs.py 로 합친 보기 → 분석"],
    ["exp/link_runs.py", "여러 데이터셋의 회차 폴더를 상대 심볼릭 링크로 모은 보기(view) 데이터셋을 만듦"],
    ["exp/report/", "이 문서·인계 기록 생성기 (make_report.py, docx_helpers.py, make_md_results.py, findings_ko.txt, findings_seq_ko.txt, make_handoff.sh), 감사 결과, sudoers 사본, 이 문서(.docx)"],
    [f"exp/results/{EXP}/", "주 데이터셋 (wbuffix_nodrop/, wbuffix_drop/, env_before·env_after, analysis/)"],
    [f"exp/results/{SUP['name'] if SUP else 'main_*'}/", "보조 데이터셋 (base/, wbuffix/, env_before·env_after_stop, analysis/)"],
    *([[f"exp/results/{SEQ['name']}/", "순차 쓰기 실험 (wbuffix/, merge/, env_before·env_after, analysis/)"]] if SEQ else []),
    *([[f"exp/results/{RBS['name']}/", "랜덤 쓰기 bs 8K·64K (wbuffix/, env_before·env_after, analysis/)"]] if RBS else []),
    *([[f"exp/results/{RV['name']}/", "합친 보기: wbuffix/ 아래 회차는 주 데이터셋 wbuffix_nodrop/ 과 " + (RBS['name'] if RBS else '') + "/wbuffix/ 로 가는 링크 (SOURCES.txt), analysis/·plots/"]] if RV else []),
    ["exp/results/pre_*/", "사전 점검 (스모크 테스트, GC_STATS 영향, 페이지 캐시 drop 시험, 순차 쓰기 점검 pre_seq_*·pre_rand_merge_check)"],
    ["EXPERIMENT_LOG_FOR_CLAUDE.md", "다른 Claude 에게 넘기는 상세 기록(모든 지시·결정·수치)"],
], widths=[5.4, 11.6], size=8, caption="저장소 구성")
R.h("3.3 실행 권한 (sudoers)", 2)
R.p("insmod·rmmod·블록 장치에 대한 fio·dmesg 는 root 권한이 필요하다. 실험을 무인으로 돌리기 위해 필요한 명령만 비밀번호 없이 쓰도록 규칙을 추가했다"
    "(14:06 KST 설치, 14:08 /dev/kmsg 추가, 15:55 drop_caches 추가, 18:33 제거" + (", 20:17 순차 쓰기 실험을 위해 다시 설치" if SEQ else "") + (f", {SUDOERS_REMOVED2} 제거" if SEQ and SUDOERS_REMOVED2 else "")
    + (", 22:11 랜덤 쓰기 bs 8K·64K 실험을 위해 다시 설치" if RBS else "") + (f", {SUDOERS_REMOVED3} 제거" if RBS and SUDOERS_REMOVED3 else "") + "). /dev/kmsg 쓰기는 회차의 시작·끝 표지를 커널 로그에 남겨 NVMeVirt 메시지와 같은 시계로 시간을 재기 위해, "
    "/proc/sys/vm/drop_caches 쓰기는 페이지 캐시 drop 조건에, /sys/block/nvme1n1/queue/nomerges 쓰기는 순차 쓰기 실험에서 블록 계층 요청 병합을 끄는 데(8.1 절) 쓴다.")
R.code(read(EXPD / "report" / "nvmevirt-exp.sudoers") or "(sudoers 파일 사본 없음)")
R.code("""# 설치 (저장소 최상위 디렉터리에서; 문법 검사 후 설치)
sudo visudo -cf exp/report/nvmevirt-exp.sudoers && sudo install -m 0440 -o root -g root exp/report/nvmevirt-exp.sudoers /etc/sudoers.d/nvmevirt-exp
# 실험 후 제거
sudo rm /etc/sudoers.d/nvmevirt-exp""")
R.p("위 규칙은 순차 쓰기 실험(8 절) 때 설치한 것이다(20:17 KST, 사용자가 직접 설치). 랜덤 쓰기 실험(주·보조 데이터셋) 때의 규칙에는 nomerges 항목이 없었고, "
    "마지막 chown 경로가 저장소를 옮기기 전 위치(/home/dccearth/jsw/KSC2026/nvmevirt/exp/*)였다(태그 ksc2026-final 의 같은 파일). "
    "chown 항목은 사용자(dccearth)와 저장소 위치에 묶여 있다. run_experiment.sh 는 회차마다 'sudo -n chown -R <사용자>:<사용자> <회차 폴더>' 를 실행하고, 이것이 실패하면 set -e 때문에 "
    "첫 회차의 rmmod 직후 DONE 표지 없이 멈춘다(사전 점검은 chown 을 확인하지 않는다). nomerges 항목은 이 서버의 NVMeVirt 장치 이름(nvme1n1)을 그대로 적었다"
    "(sudoers 인자의 * 는 공백과 / 까지 맞으므로 와일드카드를 쓰지 않았다). 다른 곳에 clone 했거나 장치 이름이 다르면 아래처럼 바꾼 규칙을 설치한다(4.3 절).", size=9.5)
R.code("""<USER> ALL=(root) NOPASSWD: /usr/sbin/insmod, /usr/sbin/rmmod, /usr/bin/fio, /usr/bin/dmesg, /usr/sbin/nvme, /usr/bin/cat /proc/iomem, /usr/bin/tee /dev/kmsg, /usr/bin/tee /proc/sys/vm/drop_caches, /usr/bin/tee /sys/block/<NVMeVirt 장치>/queue/nomerges, /usr/bin/chown -R <USER>\\:<USER> <REPO>/exp/*""")
R.h("3.4 NVMeVirt 소스 수정 사항", 2)
R.p("원본(61c90f7) 대비 바꾼 것은 아래가 전부다. 전체 diff 는 부록 B 에 있다.")
R.table(["파일", "항목", "원본 값", "실험 값", "이유"], [
    ["Kbuild", "빌드 대상", "CONFIG_NVMEVIRT_NVM (Optane)", "CONFIG_NVMEVIRT_SSD\n(BASE_SSD=SAMSUNG_970PRO)", "conventional SSD(FTL·GC 모델) 사용"],
    ["Kbuild", "MAPPING_UNIT", "없음", "make 변수 (기본 4096)", "매핑 단위별 모듈을 한 소스에서 빌드"],
    ["ssd.c:73", "secs_per_pg", "4096 / LBA_SIZE", "MAPPING_UNIT / LBA_SIZE", "FTL 매핑 단위(= FTL page) 변경"],
    ["ssd_config.h", "BLKS_PER_PLN", "8192", "384", "블록 2 MiB: 12 GiB ÷ 4 파티션 ÷ (2 ch × 2 LUN × 1 plane) ÷ 384"],
    ["ssd_config.h", "FLASH_PAGE_SIZE", "KB(32)", "32 KiB (매핑 ≤ 32K)\n= 매핑 단위 (64K, 128K)", "FLASH_PAGE_SIZE % pgsz == 0 assert 통과"],
    ["ssd.c", "적재 로그", "–", "'KSC2026: mapping unit=…' 1 줄", "회차마다 매핑 단위 적용 확인"],
    ["conv_ftl.c", "적재 로그", "–", "'KSC2026: WBUF_FIX=… GC_STATS=…' 1 줄 (#if 밖, 항상 출력)", "회차마다 빌드 변형(base/wbuffix) 확인"],
    ["conv_ftl.c/.h", "GC_STATS (선택)", "–", "base·wbuffix 모두 켬", "첫 GC 시각, 호스트/GC 페이지 수 기록 (관찰만, 영향 없음 — 5.3 절)"],
    ["conv_ftl.c", "WBUF_FIX (선택)", "–", "wbuffix 만 켬", "쓰기 버퍼 과다 반환 수정 (5.4 절)"],
    *([["conv_ftl.c/.h, Kbuild", "WBUF_MERGE (선택)", "–", "merge 만 켬 (순차 쓰기 실험)", "매핑 단위보다 작은 쓰기를 쓰기 버퍼에서 병합 (8.2 절)"]] if SEQ else []),
], widths=[2.2, 2.6, 3.2, 3.8, 5.2], size=8, caption="NVMeVirt 수정 사항")
R.p("빌드 명령 (매핑 단위 하나):")
R.code("""cd nvmevirt
make clean
make MAPPING_UNIT=16384 GC_STATS=1              # base 변형
make MAPPING_UNIT=16384 GC_STATS=1 WBUF_FIX=1   # wbuffix 변형
make MAPPING_UNIT=16384 GC_STATS=1 WBUF_FIX=1 WBUF_MERGE=1   # merge 변형 (순차 쓰기 실험, 커밋 66446ea 부터)
# exp/build_modules.sh <변형> 이 6 개 매핑 단위를 차례로 빌드해 exp/modules/<변형>/ 에 보관한다
# 빌드된 .ko 에는 소스의 절대 경로가 들어가므로, SHA-256 비교는 같은 경로에서 빌드한 경우에만 의미가 있다 (원본 값: 4.2 절)""")
R.h("3.5 매핑 단위별 FTL 파라미터 (적재 로그로 확인한 값)", 2)
geo_rows = []
for mp in SIZES:
    g = GEOM.get(mp, {})
    tt = g.get("tt_pgs")
    l2p = f"{tt * 4 * 8 / 2**20:.2f}" if tt else "–"
    geo_rows.append([mp.upper(), fnum(g.get("flash", 0) / 1024, 0) if g.get("flash") else "–",
                     fnum(g.get("pgs_per_blk"), 0) if g.get("pgs_per_blk") else "–",
                     f"{g.get('blk_kib', 0) // 1024} MiB" if g.get("blk_kib") else "–",
                     str(g.get("lines", "–")), fnum(tt * 4, 0) if tt else "–", l2p,
                     f"{g['wbuf'] // 2**20} MiB" if g.get("wbuf") else "–", str(g.get("ns_mib", "–"))])
R.table(["매핑\n단위", "flash\npage (KiB)", "블록당\n페이지", "블록", "파티션당\nline", "전체 FTL\n페이지", "L2P 표\n(MiB)", "쓰기\n버퍼", "호스트 용량\n(MiB)"],
        geo_rows, widths=[1.5, 1.7, 1.7, 1.5, 1.7, 2.3, 1.8, 1.6, 2.0], size=8, caption="매핑 단위별 파라미터 (dmesg 적재 로그)", align_right_from=1)
R.p("공통: 파티션 4 개(SSD_PARTITIONS), 파티션마다 채널 2 · 채널당 LUN 2 · LUN 당 plane 1, 파티션 물리 용량 3 GiB, line = 블록 4 개 = 8 MiB, "
    "물리 12,883,853,312 B / 논리 12,040,984,403 B (physical/logical × 100 = 107), 장치 크기 12,040,984,064 B. "
    "L2P 표 크기 = 전체 FTL 페이지 × 8 B (maptbl 항목 크기) — 매핑 단위가 커질수록 1/2 씩 줄어든다. "
    "쓰기 버퍼(GLOBAL_WB_SIZE)는 원본 식 '채널 × LUN × oneshot page × 2' 를 그대로 써서 flash page 가 커지는 64K·128K 에서 2·4 MiB 가 된다.", size=9)
R.h("3.6 바꾸지 않은 기본값 (970 Pro 묶음)", 2)
R.p("NVMeVirt 설정조사 보고서(산출물/NVMeVirt_설정조사_보고서.docx, 부록 A)가 정리한 기본값을 그대로 썼다.")
R.table(["항목", "값", "위치"], [
    ["NAND 채널 / 채널당 LUN / LUN 당 plane", "8 / 2 / 1 (총 16 die)", "ssd_config.h NAND_CHANNELS, LUNS_PER_NAND_CH, PLNS_PER_LUN"],
    ["SSD 파티션", "4 (채널을 4 등분, 파티션 = 독립 FTL 인스턴스, LPN % 4 로 분배)", "SSD_PARTITIONS"],
    ["셀 종류", "MLC", "CELL_MODE"],
    ["oneshot page", "flash page × 1", "ONESHOT_PAGE_SIZE"],
    ["읽기 지연 tR", "LSB 30.0 µs / MSB 42.0 µs (4 KiB 읽기 29.8 / 41.8 µs)", "NAND_READ_LATENCY_*, NAND_4KB_READ_LATENCY_*"],
    ["프로그램 지연 tPROG", "185 µs", "NAND_PROG_LATENCY"],
    ["지우기 지연 tBERS", "0", "NAND_ERASE_LATENCY"],
    ["펌웨어 지연", "4 KiB 읽기 21.5 µs, 읽기 30.49 µs, 쓰기 버퍼 4.0 µs + 0.46 µs/4 KiB, 채널 0", "FW_*"],
    ["채널 / PCIe 대역폭", "800 MB/s / 3,360 MB/s", "NAND_CHANNEL_BANDWIDTH, PCIE_BANDWIDTH"],
    ["채널 1 회 전송 최대", "16 KiB", "MAX_CH_XFER_SIZE"],
    ["OP 비율", "7 %", "OP_AREA_PERCENT"],
    ["쓰기 버퍼", "채널 × LUN × oneshot × 2 (1 MiB @ 32 KiB page)", "GLOBAL_WB_SIZE"],
    ["쓰기 조기 완료", "켬 (버퍼에 들어가면 완료 응답)", "WRITE_EARLY_COMPLETION 1"],
    ["MDTS", "6 (최대 전송 256 KiB → 128 KiB 요청은 나뉘지 않음)", "MDTS"],
    ["GC 문턱", "free line ≤ 2 이면 foreground GC (line 1 개씩)", "conv_ftl.c gc_thres_lines(_high) = 2"],
    ["GC 지연 모델", "켬", "enable_gc_delay = 1"],
    ["LBA 크기", "512 B", "LBA_BITS 9"],
], widths=[4.5, 6.5, 6.0], size=8, caption="유지한 NVMeVirt 기본값")
R.h("3.7 설정조사 보고서 추천값과 다른 점", 2)
R.table(["항목", "보고서 추천", "이번 실험", "이유"], [
    ["용량 · memmap", "64 GiB", "12 GiB (memmap=12G$12G)", "서버 메모리 24 GB 중 상위 12 GB 사용 (사용자 지정)"],
    ["블록", "2 MiB (BLKS_PER_PLN 2048 @ 64 GiB)", "2 MiB (BLKS_PER_PLN 384 @ 12 GiB)", "용량에 맞춰 같은 2 MiB 유지"],
    ["NVMeVirt CPU", "5 (디스패처 1 + 워커 4)", "3 (디스패처 1 + 워커 2)", "서버 CPU 6 개 (사용자 지정)"],
    ["매핑 단위", "4 → 8·16·32 KiB", "최종 4·16·32 KiB (첫 설계는 4–128 KiB, 64K·128K 는 flash page 도 같이 키움)", "사용자·선배 지정"],
    ["fio bs", "4k–128k", "최종 4·16·32 KiB (첫 설계는 4–128 KiB)", "선배 지정"],
    ["fio 시간", "사전 채움 후 300 s", "포맷 직후 60 s, ramp_time 0, 3 회", "GC 이전 구간까지 함께 측정 (사용자 지정)"],
    ["fio 나머지", "libaio · randwrite · QD 32 · jobs 1", "같음", "–"],
    ["OS 페이지 캐시", "언급 없음", "drop / no-drop 두 조건 측정", "선배 질문"],
], widths=[3.0, 4.3, 4.7, 5.0], size=8, caption="설정조사 보고서 추천값과의 차이")
R.h("3.8 모듈 적재 파라미터", 2)
R.code("sudo insmod exp/modules/<변형>/nvmev_map<단위>.ko memmap_start=12G memmap_size=12G cpus=3,4,5")
R.p("memmap_start/size 는 GRUB 의 memmap=12G$12G 와 같은 영역이다. NVMeVirt 는 앞 1 MiB 를 큐 등에 쓰고 나머지 12,287 MiB 를 저장 공간으로 쓴다"
    "(dmesg 'Storage: 0x300100000-0x600000000 (12287 MiB)'). cpus 의 첫 값이 디스패처, 나머지가 I/O 워커다.", size=9)
R.h("3.9 fio 작업 파일", 2)
R.p("틀(exp/jobs/randwrite.fio.in)의 @값@ 을 회차마다 채워 회차 폴더에 job.fio 로 저장한다. 아래는 틀과 실제 예(매핑 4K, bs 4K, 1 회차)이다.")
R.code(read(EXPD / "jobs" / "randwrite.fio.in"))
R.code(read(EXP_DIR / "wbuffix_nodrop" / "map4k_bs4k_r1" / "job.fio") or read(EXP_DIR / "base" / "map4k_bs4k_r1" / "job.fio") or "(job.fio 없음)")
R.bullets([
    "filename 은 회차마다 모델명 CSL_Virt 로 찾은 장치다. 크기(11–12 GiB)·파티션 없음·마운트 안 됨·루트 디스크 아님을 확인한 뒤에만 쓴다.",
    "size 를 주지 않아 장치 전체(12,040,984,064 B)에 랜덤 쓰기를 한다. randrepeat=1(기본값)이라 회차·조합마다 같은 난수 순서를 쓴다.",
    "norandommap 은 기본값(0)이다: fio 가 한 바퀴 동안 같은 블록을 두 번 쓰지 않는다.",
    "write_bw_log/write_iops_log/write_lat_log 로 0.5 s 평균 시계열을 남긴다(fio_bw.1.log 등, 단위 KiB/s · IOPS · ns).",
])
if SEQ:
    R.p("순차 쓰기 실험(8 절)의 틀 exp/jobs/seqwrite.fio.in 은 위와 비교해 rw=write, randrepeat 줄 삭제, 작업 이름 [seqwrite] 만 다르다. "
        "time_based 라 장치 끝(12,040,984,064 B)에 닿으면 offset 0 으로 돌아가 계속 쓴다.", size=9.5)
    R.code(read(EXPD / "jobs" / "seqwrite.fio.in"))
R.h("3.10 OS 페이지 캐시 조건 (drop / nodrop)", 2)
R.p("drop 조건은 장치 확인 직후(5 초 대기 전) 다음을 실행한다. nodrop 조건은 아무것도 하지 않는다. 두 조건 모두 /proc/meminfo 의 MemFree·Buffers·Cached·Dirty·Writeback 을 "
    "drop 전, drop 후, fio 직전에 회차 폴더의 cache.txt 에 기록한다.")
R.code("""sync
echo 3 | sudo -n tee /proc/sys/vm/drop_caches > /dev/null      # 3 = page cache + dentries/inodes""")
R.p("fio 는 direct=1(O_DIRECT)로 블록 장치에 쓰므로 데이터 경로가 페이지 캐시를 거치지 않는다. NVMeVirt 저장 공간은 GRUB memmap 으로 커널 관리에서 뺀 메모리이고, "
    "회차마다 rmmod/insmod 로 장치를 새로 만든다. 따라서 이론상 영향이 없어야 하며, 이를 실측으로 확인하는 것이 이 조건의 목적이다.", size=9.5)

# ============================================================================ 4
R.h("4. 실험 절차")
R.h("4.1 회차 하나의 절차", 2)
R.numbered([
    "nvmev 모듈이 올라와 있으면 rmmod 로 내린다(이전 FTL 상태 제거).",
    "커널 로그를 끝까지 따라가며 기록하는 'sudo dmesg -W' 를 회차 폴더의 kernel.log 로 시작한다(채널 모델 오류 줄은 개수만 센다 — 5.4 절).",
    "커널 로그에 'KSC2026-MARK <회차> insmod' 표지를 남기고 insmod 한다(memmap_start=12G memmap_size=12G cpus=3,4,5).",
    "모델명 CSL_Virt_MN_01 인 블록 장치가 생길 때까지 기다리고, 적재 로그의 'KSC2026: mapping unit=<바이트> B' 로 매핑 단위가 맞는지 확인한다. 틀리면 실험을 멈춘다.",
    "장치 크기·파티션·마운트·루트 디스크 여부를 확인한다. 페이지 캐시 조건이 drop 이면 sync; echo 3 > /proc/sys/vm/drop_caches 를 실행하고, 두 조건 모두 meminfo 를 cache.txt 에 적는다(3.10 절). job.fio 와 meta.txt 를 만든다.",
    "5 초 쉰 뒤 'fio-start' 표지를 남기고 fio 를 60 초 실행한다(JSON 결과 + 0.5 초 시계열).",
    "'fio-end', 'rmmod' 표지를 남기고 rmmod 한다 — 이때 GC 통계(파티션별 호스트/GC 페이지 수)가 로그에 찍힌다.",
    "커널 로그를 run 구간(dmesg_run.txt)과 rmmod 구간(dmesg_unload.txt)으로 나누고, 결과 파일 소유자를 사용자로 바꾼다.",
    "fio 종료 코드와 JSON 의 error 필드가 모두 0 이면 DONE 표지를, 아니면 FAILED 표지(원인 커널 줄 포함)를 만들고 다음 회차로 넘어간다. DONE·FAILED 회차는 다시 실행할 때 건너뛴다. "
    "fio 는 감시 타이머(60 s + 180 s 에 SIGTERM, 다시 60 s 뒤 SIGKILL) 아래에서 실행한다.",
])
R.h("4.2 실행 순서와 시간", 2)
rows42 = []
for v in PRI["variants"]:
    a, b = run_window(v)
    rows42.append([f"주 · {v}", str(n_pri.get(v, 0)), "반복 1→3, 매핑 4K→32K, bs 4K→32K, (nodrop, drop) 연달아 — 짝수 반복은 drop 먼저", a, b])
if SUP:
    for v in SUP["variants"]:
        a, b = run_window(v, SUP)
        rows42.append([f"보조 · {v}", str(n_sup.get(v, 0)), "반복 1→3, 매핑 4K→128K, bs 4K→128K", a, b])
if SEQ:
    for v in SEQ["variants"]:
        a, b = run_window(v, SEQ)
        rows42.append([f"순차 · {v}", str(n_seq.get(v, 0)), "반복 r 마다 wbuffix 한 바퀴 → merge 한 바퀴 (바퀴 안: 매핑 4K→32K, bs 4K→32K)", a, b])
if RBS:
    for v in RBS["variants"]:
        a, b = run_window(v, RBS)
        rows42.append([f"랜덤 bs 8K·64K · {v}", str(n_rbs), "반복 1→3, 매핑 4K→32K, bs 8K→64K", a, b])
R.table(["데이터셋 · 변형", "완료 회차", "순서", "run.log 첫 시각", "마지막 시각"], rows42,
        widths=[2.8, 1.6, 6.6, 3.0, 3.0], size=8, caption="실행 순서와 시각 (KST)")
R.p("반복을 바깥 루프에 둬서 시간에 따른 서버 상태 변화가 특정 조합에 몰리지 않게 했다. 회차 하나는 적재·대기·측정·내림을 합쳐 약 70 초 걸린다.")
R.p("보조 데이터셋 경과: 당시의 exp/run_all.sh(커밋 5769378; 지금의 run_all_6x6.sh 와 주석 한 줄만 다른 같은 내용, 빌드 → base → wbuffix)로 14:20:28 에 시작했으나 "
    "base 21 번째 회차(매핑 32K·bs 16K)에서 가상 장치가 멈춰(5.6 절) 당시 스크립트가 실험을 중단했다(14:46:57). 실패 회차를 FAILED 로 남기고 계속하도록 고친 뒤"
    "(커밋 2a462a3 → push 전 949ae38 로 다시 만듦, " + POST_N + " 절) `bash run_experiment.sh main_20261008 wbuffix` 로 wbuffix 를 먼저 재개했고(run.log 첫 줄 14:49:14), "
    "15:51:23 에 설계 변경으로 회차 경계에서 멈췄다. 모듈은 14:20 에 한 번 빌드한 것을 끝까지(주 데이터셋 포함) 그대로 썼다(SHA-256 확인).", size=9.5)
_sums = dict((ln.split()[1], ln.split()[0]) for ln in read(EXP_DIR / (PRI["variants"][0] if PRI["variants"] else "") / "modules_SHA256SUMS").splitlines() if len(ln.split()) == 2)
if _sums:
    R.p("주 데이터셋에 쓴 wbuffix 모듈은 커밋 5769378 상태의 /home/dccearth/jsw/KSC2026/nvmevirt/nvmevirt 에서 make MAPPING_UNIT=<바이트> GC_STATS=1 WBUF_FIX=1 로 빌드했다"
        "(2026-10-08 14:20:45–14:21:02 KST, gcc 13.3.0, 커널 헤더 6.8.0-142). 쓴 모듈의 SHA-256: "
        + "; ".join(f"{k} {v}" for k, v in _sums.items() if any(f"map{m}.ko" in k for m in PRI["sizes"]))
        + ". 6 개 단위 전체와 base 값은 결과 폴더의 modules_SHA256SUMS 와 회차별 meta.txt 의 module 줄에 있다(.ko 는 git 에 넣지 않았다).", size=9)
R.h("4.3 재현 명령", 2)
_supname = SUP["name"] if SUP else "main_20261008"
R.code(f"""git clone https://github.com/Sangwon8799/nvmevirt.git nvmevirt && cd nvmevirt   # 공개 저장소 (SSH 키 불필요)
git checkout {PUSH_TAG or HEAD[:7]}   # 태그 = 실험 스크립트 {HEAD[:7]}""" + (f" + 순차 쓰기 스크립트·병합 모델 {SEQ_HEAD[:7]}" if SEQ else "") + f""" + 이 문서·생성기·결과
cd exp
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
bash build_modules.sh wbuffix   # make MAPPING_UNIT=<바이트> GC_STATS=1 WBUF_FIX=1 (매핑 단위 6 개; run_all.sh 도 없으면 빌드한다)
# 3.1 절 GRUB 설정·패키지가 있어야 한다. 3.3 절 sudoers 는 이 clone 의 경로와 내 사용자 이름으로 바꿔 설치한다:
sed -e "s|/home/dccearth/jsw/nvmevirt/exp/\\*|$(cd .. && pwd)/exp/*|" -e "s|dccearth|$(id -un)|g" report/nvmevirt-exp.sudoers > /tmp/nvmevirt-exp.sudoers   # 장치 이름이 nvme1n1 이 아니면 nomerges 경로도 바꾼다
sudo visudo -cf /tmp/nvmevirt-exp.sudoers && sudo install -m 0440 -o root -g root /tmp/nvmevirt-exp.sudoers /etc/sudoers.d/nvmevirt-exp
tmux new -s ksc2026 'bash run_all.sh {EXP} 2>&1 | tee -a results/run_all_{EXP}.log'   # 주 데이터셋 (약 65 분)
tmux new -s ksc6x6 'bash run_all_6x6.sh {_supname} 2>&1 | tee -a results/run_all_{_supname}.log'   # (선택) 첫 설계 6×6×3×{{base,wbuffix}} (약 4.3 시간 + base 실패 회차)
# 사전 점검 (5.2·5.3·5.7 절; 당시에는 대기 시간을 줄여 실행. 폴더 이름은 실험 후 pre_* 로 바꿈)
bash build_modules.sh base && MAPS=4k bash build_modules.sh plain
MAPS=128k BSS=4k REPS=1 RUNTIME=10 SETTLE_SEC=2 bash run_experiment.sh pre_smoke_test base                                   # 5.2
for v in plain base; do MAPS=4k BSS=4k REPS=3 RUNTIME=20 SETTLE_SEC=3 bash run_experiment.sh pre_gcstats_ab $v; done         # 5.3
MAPS="4k 16k" BSS=4k REPS=2 RUNTIME=8 SETTLE_SEC=2 CACHE_MODES="nodrop drop" bash run_experiment.sh pre_cache_test wbuffix   # 5.7
./.venv/bin/python plot.py all --exp results/{EXP}    # 그래프
""" + (f"""# 순차 쓰기 실험 (8 절): wbuffix 모듈(위에서 빌드) + merge 모듈, 3×3×3×2 = 54 회 (약 64 분)
MAPS="4k 16k 32k" bash build_modules.sh merge
tmux new -s ksc2026seq 'bash run_all_seq.sh {SEQ['name']} 2>&1 | tee -a results/run_all_{SEQ['name']}.log'
# 순차 쓰기 사전 점검 (8.3 절; 15 s 회차)
export REPS=1 RUNTIME=15 CACHE_MODES=nodrop
WORKLOAD=seqwrite NOMERGES= MAPS=16k BSS=4k bash run_experiment.sh pre_seq_blkmerge_default wbuffix
for v in wbuffix merge; do WORKLOAD=seqwrite NOMERGES=2 MAPS="16k 32k" BSS="4k 16k" bash run_experiment.sh pre_seq_check $v; done
for v in wbuffix merge; do WORKLOAD=randwrite NOMERGES= MAPS=16k BSS=4k bash run_experiment.sh pre_rand_merge_check $v; done
unset REPS RUNTIME CACHE_MODES
./.venv/bin/python plot.py all --exp results/{SEQ['name']}
""" if SEQ else "") + (f"""# 랜덤 쓰기 bs 8K·64K ({RBS_N} 절): wbuffix 모듈(위에서 빌드), 매핑 3 × bs 2 × 3 = 18 회 (약 21 분) → 주 데이터셋과 합친 보기
tmux new -s ksc2026rbs 'bash run_all_rand_bs.sh {RBS['name']} {EXP} {RV['name'] if RV else ''} 2>&1 | tee -a results/run_all_{RBS['name']}.log'
./.venv/bin/python plot.py all --exp results/{RV['name'] if RV else ''}
""" if RBS else "") + f"""./.venv/bin/python report/make_report.py results/{EXP} --supp results/{_supname}""" + (f" --seq results/{SEQ['name']}" if SEQ else "") + (f" --rbs results/{RBS['name']} --rview results/{RV['name']}" if RBS and RV else "") + """   # 이 문서 (선택 단계를 건너뛰었으면 해당 인자 생략)""")
R.p("위 sed 는 3.3 절 규칙의 chown 경로와 사용자 이름을 바꾼다. 5.2 절 스모크 테스트는 당시 매핑 4K·128K × bs 4K·128K 로도 돌렸지만 남은 결과는 128K/4K 1 회뿐이다(5.2 절).", size=9)
R.h("4.4 결과 파일", 2)
R.table(["파일 (회차 폴더 exp/results/<EXP>/<변형>_<nodrop|drop>/map<단위>_bs<크기>_r<회>/ — CACHE_MODES=nodrop 단독이면 <변형>/map…/)", "내용"], [
    ["fio.json", "fio 결과 (JSON) — BW, IOPS, clat/slat/lat 통계, 백분위수"],
    ["fio_stdout.txt", "fio 표준 출력·오류와 감시 타이머 기록 (정상 회차는 비어 있음; 실패 회차에는 I/O error 줄)"],
    ["fio_bw.1.log / fio_iops.1.log / fio_lat.1.log / fio_clat.1.log / fio_slat.1.log", "0.5 s 평균 시계열 (ms, 값, 방향, bs, offset)"],
    ["job.fio", "그 회차에 실제로 쓴 fio 작업 파일"],
    ["meta.txt", "변형·캐시 조건·단위·bs·회차, 장치, 모듈 SHA-256, insmod 인자, git 커밋, 시작/끝(UTC), fio 종료 코드, 채널 모델 오류 수, 커널 경고 수. "
     "순차 쓰기 실험부터: workload(rw), blk_queue(nomerges·스케줄러·max_sectors_kb·write_cache), blk_writes(fio 동안 블록 계층 쓰기 요청 수·합쳐진 수·섹터 수)"],
    ["cache.txt", "페이지 캐시 조건과 meminfo (drop 전/후, fio 직전)"],
    ["DONE / FAILED", "정상 종료 표지 / fio 실패 표지(원인 커널 줄 포함)"],
    ["dmesg_load.txt", "insmod 직후 커널 로그 (NVMeVirt 구성·파라미터)"],
    ["dmesg_run.txt", "fio 실행 중 커널 로그 (첫 GC 줄 포함, 채널 모델 오류 줄 제외)"],
    ["dmesg_unload.txt", "rmmod 시 커널 로그 (파티션별 GC 통계; merge 변형은 파티션별 병합 통계도)"],
    ["kernel.log / chmodel_msgs.txt", "회차 전체 커널 로그 (채널 모델 오류는 처음 20 줄만) / 그 오류 줄 수"],
], widths=[7.0, 10.0], size=8, caption="회차 폴더의 파일")
R.p("변형 폴더(<변형>_<nodrop|drop>/ 또는 <변형>/)에는 run.log, git_head.txt, modules_SHA256SUMS, modules_build_info.txt, job 틀 <WORKLOAD>.fio.in(랜덤 쓰기 randwrite.fio.in, 순차 쓰기 seqwrite.fio.in), "
    "nvmevirt_vs_upstream.diff, nvmevirt_uncommitted.diff 가 있다. 실험 폴더(exp/results/<EXP>/)에는 env_before/, env_after_<변형>/ (보조 데이터셋은 중단 후 만든 env_after_stop/), "
    "analysis/(analyze.py), plots/(plot.py) 가 있다. 원자료의 시각은 서버 시계 UTC 다.", size=9)
R.h("4.5 지표 정의", 2)
R.bullets([
    [("BW, IOPS", "b"), ": fio JSON 의 60 s 평균 (bw 는 KiB/s → MiB/s)."],
    [("clat", "b"), ": 제출 후 완료까지 지연 (fio clat_ns). 평균과 p50/p99/p99.9."],
    [("첫 10 s / 마지막 20 s BW", "b"), ": 0.5 s 시계열에서 0–10 s, 40–60 s 구간 평균."],
    [("GC 시작 시각", "b"), ": 커널 로그의 'fio-start' 표지부터 첫 'KSC2026: first GC' 줄까지의 시간 (4 개 파티션 중 가장 이른 것)."],
    [("GC 전/후 BW", "b"), ": GC 시작 시각 이전/이후 시계열 구간의 평균."],
    [("WAF_GC", "b"), ": (호스트 페이지 쓰기 + GC 페이지 복사) ÷ 호스트 페이지 쓰기 — 매핑 단위 페이지 기준."],
    [("WAF_total", "b"), ": (호스트 + GC 페이지) × 매핑 단위 ÷ fio 가 쓴 바이트 — 매핑 단위보다 작은 쓰기의 증폭(매핑 단위/bs)까지 포함."],
    *([[("블록 계층 요청 (순차 쓰기 실험)", "b"), ": fio 동안 /sys/block/<장치>/stat 의 쓰기 요청 수·합쳐진 수·평균 요청 크기(KiB)."],
       [("병합 통계 (merge 변형)", "b"), ": open = 부분 쓰기로 연 매핑 단위 수, merge = 열린 단위에 합류한 쓰기 수, full = 가득 차서 flash 에 쓴 단위 수, "
        "evict = 다른 부분 쓰기에 자리를 내주며 덜 찬 채 쓴 단위 수, direct = 단위 전체를 덮어 바로 쓴 수, still_open = rmmod 때 열려 있던 단위 수 (4 파티션 합)."]] if SEQ else []),
])

# ============================================================================ 5
R.h("5. 사전 점검과 발견 사항")
R.h("5.1 예약 메모리와 장치 확인", 2)
R.code("""$ sudo cat /proc/iomem    (4 GiB 위)
100000000-2ffffffff : System RAM      #  4 – 12 GiB
300000000-5ffffffff : Reserved        # 12 – 24 GiB  ← NVMeVirt 저장 공간
600000000-67f7fffff : System RAM      # 24 – 26 GiB (PCI hole 재배치분)
$ dmesg (insmod 직후, 매핑 4K)
NVMeVirt: Version 1.10 for >> Samsung 970 Pro SSD <<
NVMeVirt: Storage: 0x300100000-0x600000000 (12287 MiB)
NVMeVirt: Total Capacity(GiB,MiB)=3,3072 chs=2 luns=4 lines=384 blk-size(MiB,KiB)=2,2048 line-size(MiB,KiB)=8,8192
NVMeVirt: KSC2026: mapping unit=4096 B, flash page=32768 B, oneshot page=32768 B, pgs_per_blk=512, blks_per_pl=384, write buffer=1048576 B
NVMeVirt: FTL physical space: 12883853312, logical space: 12040984403 (physical/logical * 100 = 107)
NVMeVirt: ns 0/1: size 11483 MiB
NVMeVirt: nvmev_io_worker_0 started on cpu 4 (node 0)
NVMeVirt: nvmev_io_worker_1 started on cpu 5 (node 0)
NVMeVirt: nvmev_dispatcher started on cpu 3 (node 0)
nvme nvme1: 1/0/0 default/read/poll queues""")
R.p("매핑 단위 6 개 모두 init 단계의 assert 를 통과하고 블록은 정확히 2 MiB 가 된다(블록 원시 크기 2,096,982 B 가 oneshot page 단위로 올림되어 2,097,152 B). "
    "64K·128K 는 FLASH_PAGE_SIZE 를 그대로 32 KiB 로 두면 ssd.c:98 의 assert 로 적재가 실패한다(사용자가 지적한 대로 flash page 를 매핑 단위와 같게 함).")
R.h("5.2 스모크 테스트", 2)
smoke = []
for v in ("base", "wbuffix"):
    for mp in ("4k", "128k"):
        for bs in ("4k", "128k"):
            d = EXPD / "results" / "pre_smoke_test" / v / f"map{mp}_bs{bs}_r1"
            if (d / "fio.json").exists():
                w = json.loads(read(d / "fio.json"))["jobs"][0]["write"]
                cm = re.search(r"chmodel_msgs:\s*(\S+)", read(d / "meta.txt"))
                smoke.append([v, mp.upper(), bs.upper(), f"{w['bw'] / 1024:.1f}", f"{w['iops']:,.0f}", f"{w['clat_ns']['mean'] / 1e3:.1f}", f"{int(cm.group(1)):,}" if cm and cm.group(1).isdigit() else "–"])
if smoke:
    R.table(["변형", "매핑", "bs", "MiB/s", "IOPS", "clat 평균 µs", "채널 모델 오류"], smoke,
            widths=[2.2, 1.6, 1.6, 2.2, 2.6, 2.6, 3.2], size=8.5, caption="스모크 테스트 (10 s, 1 회, insmod 후 대기 2 s)", align_right_from=3)
else:
    R.p("스모크 테스트(매핑 4K·128K × bs 4K·128K, 10 s)로 회차 절차·결과 파일·커널 로그 수집을 점검했다.")
R.p("10 초짜리 짧은 실행으로 회차 절차가 끝까지 도는지 확인했다. 이 과정에서 두 가지를 고쳤다: "
    "(1) dmesg 시각과 /proc/uptime 의 차이 때문에 시각으로 로그를 자르던 방법이 실패해 커널 로그 표지(/dev/kmsg) 방식으로 바꿨고, "
    "(2) base 의 매핑 128K·bs 4K 에서 NVMeVirt 가 10 초에 약 186 만 줄(표의 회차; 결과를 남기지 않은 앞선 회차는 1,665,207 줄)의 '[chmodel_request] Need to increase array size' 오류를 찍어 "
    "256 KiB 커널 링 버퍼를 덮어써서, 커널 로그를 실시간으로 따라가며 그 줄은 개수만 세도록 했다.", size=9.5)
R.h("5.3 GC_STATS 계측의 영향 확인", 2)
ab = []
for v in ("plain", "base"):
    for r in (1, 2, 3):
        d = EXPD / "results" / "pre_gcstats_ab" / v / f"map4k_bs4k_r{r}"
        if (d / "fio.json").exists():
            w = json.loads(read(d / "fio.json"))["jobs"][0]["write"]
            ab.append([v + (" (GC_STATS 끔)" if v == "plain" else " (GC_STATS 켬)"), str(r), f"{w['bw'] / 1024:.1f}", f"{w['iops']:,.0f}", f"{w['clat_ns']['mean'] / 1e3:.1f}"])
if ab:
    R.table(["빌드", "회", "MiB/s", "IOPS", "clat 평균 µs"], ab, widths=[5.0, 1.5, 3.0, 3.5, 3.0], size=8.5,
            caption="GC_STATS 계측 유무 비교 (매핑 4K, bs 4K, 20 s, 3 회, insmod 후 대기 3 s)", align_right_from=2)
R.p("GC 통계(첫 GC 시각, 호스트/GC 페이지 수)를 남기는 계측은 디스패처 스레드에서 정수 증가 몇 번과 첫 GC 때 printk 1 줄만 더한다. "
    "요청 수가 가장 많아 디스패처의 요청당 작업이 결과에 가장 잘 드러나는 4K/4K 에서 계측을 끈 빌드와 켠 빌드를 20 초씩 3 회 비교했다. 평균 차이(+0.31 %, 계측을 켠 빌드가 오히려 빠름)가 반복 간 범위(끈 빌드 0.30 %, 켠 빌드 0.23 %)와 같은 수준이어서 계측 비용이 드러나지 않음을 확인한 뒤 본 실험의 두 변형 모두에 켰다.")
R.h("5.4 발견 1 — 매핑 단위보다 작은 쓰기에서 쓰기 버퍼가 과다 반환된다 (base)", 2)
R.p("NVMeVirt conventional SSD 의 conv_write() 는 요청 크기만큼 쓰기 버퍼를 할당하고(buffer_allocate(wbuf, LBA_TO_BYTE(nr_lba))), "
    "flash page(wordline)가 다 차서 프로그램될 때 'oneshot page 크기'만큼 반환한다(schedule_internal_operation(…, pgs_per_oneshotpg × pgsz)). "
    "bs ≥ 매핑 단위이면 둘이 같지만, bs < 매핑 단위이면 4 KiB 쓰기 하나가 매핑 단위 페이지 하나를 통째로 차지하므로 할당(bs)보다 반환(매핑 단위)이 많다. "
    "예: 매핑 128K·bs 4K 는 요청마다 4 KiB 할당, 124 KiB 초과 반환.")
R.bullets([
    "그 결과 버퍼의 남은 양이 끝없이 늘어 쓰기 버퍼가 호스트를 붙잡는 역할(back-pressure)을 못 한다. 쓰기 조기 완료(WRITE_EARLY_COMPLETION=1)라 NAND·GC 지연이 호스트에 전달되는 통로는 이 버퍼뿐이다.",
    "NAND 작업이 실제 시간보다 계속 앞서 쌓이고, 채널 모델의 시간 창(96K × 4 µs ≈ 393 ms)을 넘으면 NVMeVirt 가 채널 전송 시간을 0 으로 처리하고 요청마다 "
    "'[chmodel_request] Need to increase array size' 를 printk 한다(rate limit 없음). 콘솔 로그 레벨 4 라 이 오류는 tty0 콘솔과 systemd-journald 에도 기록된다.",
    "즉 base 의 bs < 매핑 단위 15 개 조합은 타이밍 모델이 정상 범위를 벗어난 상태에서 잰 값이다(5.2 절: 128K/4K 에서 10 초에 약 186 만 줄). "
    "채널 시간이 빠지는 쪽(빨라짐)과 printk 부담(느려짐)이 섞여 있어 해석하기 어렵다. 각 회차의 오류 줄 수는 meta.txt 의 chmodel_msgs 와 부록 D 에 있다.",
    "코드 감사 에이전트 세 개(쓰기 경로·버퍼, 초기화·기하, GC·타이밍 렌즈)가 모두 독립적으로 같은 결론을 냈고(부록 E), 반박을 시도한 검증 6 회가 모두 핵심을 확인했다(세 건은 세부 수치·범위만 정정).",
])
R.p("수정(WBUF_FIX=1, wbuffix 변형): 할당량을 실제로 프로그램될 매핑 단위 페이지 수에 맞춘다. PCIe·펌웨어 전송 시간 계산에는 원래대로 요청 크기를 쓴다. "
    "bs ≥ 매핑 단위인 조합에서는 할당량이 원본과 같아서 결과가 바뀌지 않는다(실측으로도 확인 — 7 절).")
R.code("""#if KSC_WBUF_FIX
\t/* KSC2026: a write occupies whole mapping units in the write buffer; this is also what
\t * schedule_internal_operation() releases once the flash page is programmed */
\twbuf_bytes = (end_lpn - start_lpn + 1) * spp->pgsz;
#else
\twbuf_bytes = LBA_TO_BYTE(nr_lba);
#endif
\tallocated_buf_size = buffer_allocate(wbuf, wbuf_bytes);
\tif (allocated_buf_size < wbuf_bytes)
\t\treturn false;""")
R.h("5.5 결과 해석 시 주의할 모델 특성", 2)
R.table(["특성", "내용", "영향"], [
    ["flash page 변경 (64K·128K)", "64K·128K 는 flash page 를 키웠는데 tPROG 는 185 µs 그대로라 die 당 프로그램 대역폭이 32K 대비 1.7·2.6 배가 되고, 쓰기 버퍼도 2·4 MiB 로 커진다.",
     "32K → 64K 경계의 차이는 매핑 단위만의 효과가 아니다. 64K·128K 의 큰 bs 결과는 더 빠른 NAND 의 영향을 받는다."],
    ["RMW 미모델", "매핑 단위보다 작은 쓰기도 옛 페이지를 읽지 않는다(read-modify-write 의 NAND 읽기 없음). 무효화 후 새 페이지 전체를 프로그램만 한다.",
     "작은 bs·큰 매핑 단위의 불이익이 실제보다 작게 나온다 (wbuffix 에서도)."],
    ["쓰기 조기 완료", "호스트 완료 시각은 쓰기 버퍼까지의 시간이다. NAND·GC 비용은 버퍼가 차서 막힐 때만 호스트에 보인다.", "GC 영향은 처리량 저하·지연 증가(큐 대기)로 나타난다."],
    ["지우기 지연 0", "tBERS = 0 (기본값).", "GC 비용이 실제보다 작다 (모든 조합에 같게 적용)."],
    ["매핑 표 = 호스트 메모리 배열", "DRAM 캐시(DFTL) 모델이 없다.", "매핑 표 크기 감소 효과는 성능에 나타나지 않는다 — 3.5 절의 L2P 크기로 따로 보고."],
    ["활성 I/O 워커 1 개", "I/O 큐가 1 개라 cpu4 워커만 일한다.", "논문에는 '디스패처 1 + 워커 2 (활성 1)' 로 적는 것이 정확하다."],
    ["GC 이전 처리량의 한계", "bs ≥ 매핑 단위이면 GC 전 처리량은 NAND 프로그램 한계(16 die 합 2,233 MiB/s @32K page, 64K 3,805, 128K 5,871) 또는 PCIe 한계(3,357 MiB/s)에 가깝다(4K/4K 실측 약 2,005 MiB/s = NAND 한계의 90 %). "
     "base 의 bs < 매핑 단위(매핑 ≤ 32K)는 GC 전에는 NAND 한계 × bs/매핑 수준(8K/4K 약 1,116 MiB/s)에 머물고, GC 이후에는 5.4 절의 문제로 에뮬레이터 산물이 된다.",
     "GC 전 구간은 NAND 모델을, GC 후 구간은 GC 모델을 반영한다 — 6 절의 GC 전/후 표로 나눠 본다."],
    ["fio randommap 주기 현상", "fio 기본값(norandommap=0)은 한 바퀴(11.21 GiB) 동안 같은 블록을 다시 쓰지 않는다. 첫 바퀴에는 무효 페이지가 없어 GC 가 시작되는 순간(둘째 바퀴 약 0.66 GiB 지점) 희생 line 에 유효 페이지가 거의 가득해 대역폭이 급락하고, "
     "둘째 바퀴가 진행될수록 회복하다가 끝 무렵 첫 바퀴의 line 이 모두 무효가 되며 치솟은 뒤 셋째 바퀴에서 다시 떨어진다.",
     "60 s 평균에 이 주기가 섞인다. 시계열(6.3 절)을 함께 봐야 한다. GC 구간은 정상 상태가 아니다."],
    ["GC 시작 시각 차이", "포맷 직후 60 s 라 조합마다 GC 이전 구간 비율이 다르다.", "60 s 평균과 함께 GC 전/후 BW, 시계열을 같이 본다."],
    ["randrepeat=1", "모든 회차가 같은 난수 순서를 쓴다.", "3 회 반복은 에뮬레이터 타이밍 편차만 담는다."],
    ["작은 쓰기 병합 없음", "매핑 단위보다 작은 쓰기는 명령마다 매핑 단위 페이지 하나를 새로 쓴다. 같은 단위로 이어서 오는 쓰기도 쓰기 버퍼에서 합치지 않는다(원본 동작, base·wbuffix 모두).",
     "랜덤 쓰기에서는 실제 SSD 도 단위를 새로 써야 하므로 영향이 작다(RMW 읽기만 빠짐). 순차 쓰기에서는 결과를 좌우한다 — 8 절에서 병합 모델(merge)과 함께 본다."],
    ["블록 계층 병합", "커널 기본(mq-deadline, nomerges=0)에서는 인접한 요청을 합친다.", "랜덤 쓰기는 합칠 요청이 거의 없다(15 s 동안 fio 쓰기 1,144,511 개 중 1 개, 8.3 절" + (f"; bs 8K·64K 회차는 요청의 0.054 % 이하, {RBS_N}.1 절" if RBS else "") + "). 순차 쓰기는 nomerges=2 로 끄고 측정했다."],
], widths=[3.2, 7.6, 6.2], size=8, caption="해석 시 주의할 모델 특성")

R.h("5.6 발견 2 — base 에서 가상 장치가 멈추는 조합", 2)
FAILED_RUNS = (SUP or PRI)["failed"]
R.p("요청 설정 그대로인 base 의 bs < 매핑 단위 조합에서는 쓰기 버퍼가 호스트를 붙잡지 못해 NAND 작업 대기열이 계속 늘어난다. NVMeVirt 의 I/O 워커 작업 큐"
    "(워커당 16,384 항목)가 차면 io.c:302 의 WARN_ON_ONCE('IO queue is almost full')가 찍히고 이후 명령이 처리되지 않아, 리눅스 nvme 드라이버의 "
    "I/O 시간 초과(30 s) → 중단(abort) → 컨트롤러 리셋 → 장치 비활성화 → I/O 오류로 이어진다. 그런 회차는 FAILED 로 표시해 평균에서 빼고 아래에 따로 적었다. "
    "rmmod 는 정상 처리되었고 다음 회차의 insmod 도 정상이었다.")
if FAILED_RUNS:
    R.table(["변형", "매핑", "bs", "회", "fio\n종료", "fio\n오류", "실행\n시간 s", "큐 포화\n경고 s", "nvme\n시간초과 s", "리셋 s", "비활성 s", "채널모델\n오류 줄"],
            [[r["variant"], r["map"].upper(), r["bs"].upper(), str(int(r["rep"])), (str(int(r["fio_exit"])) if r.get("fio_exit") not in ("", None) else "–"), (f"{int(r['fio_json_error'])} (EIO)" if r.get("fio_json_error") not in ("", None) and int(r["fio_json_error"]) == 5 else str(r.get("fio_json_error", "–"))),
              fnum(r.get("runtime_s"), 1), fnum(r.get("t_queue_full_warn_s"), 1), fnum(r.get("t_nvme_timeout_s"), 1), fnum(r.get("t_reset_s"), 1),
              fnum(r.get("t_disable_s"), 1), fnum(r.get("chmodel_msgs"), 0)] for r in FAILED_RUNS],
            widths=[1.4, 1.1, 1.1, 0.7, 1.1, 1.1, 1.4, 1.5, 1.6, 1.3, 1.4, 2.2], size=7, caption="실패(FAILED) 회차 — 시각은 fio 시작 기준 초", align_right_from=3)
R.code("""# base map32k_bs16k_r1 의 kernel.log (괄호 = fio 시작 기준; 이 회차는 14:44:22 KST 시작)
[62511.194665] NVMeVirt: KSC2026: first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280      (+5.6 s)
[62530.521783] WARNING: CPU: 3 PID: 30089 at …/nvmevirt/io.c:302 __allocate_work_queue_entry+0x8a/0xb0 [nvmev]  (+25.0 s)
[62560.640166] nvme nvme1: I/O tag 192 (80c0) opcode 0x1 (I/O Cmd) QID 1 timeout, aborting req_op:WRITE(1) size:16384  (+55.1 s)
[62590.847614] nvme nvme1: I/O tag 192 (80c0) opcode 0x1 (I/O Cmd) QID 1 timeout, reset controller                    (+85.3 s)
[62652.289426] nvme nvme1: I/O tag 28 (301c) QID 0 timeout, disable controller                                        (+146.7 s)
[62652.306429] nvme nvme1: Disabling device after reset failure: -5
[62652.313386] I/O error, dev nvme1n1, sector 6011360 op 0x1:(WRITE) flags 0x8800 phys_seg 1 prio class 2
fio: io_u error on file /dev/nvme1n1: Input/output error: write offset=…, buflen=16384   → fio error 5 (EIO), 146.5 s""")
R.h("5.7 페이지 캐시 drop 사전 시험", 2)
pc = []
for cmode in ("nodrop", "drop"):
    for mp in ("4k", "16k"):
        for r in (1, 2):
            d = EXPD / "results" / "pre_cache_test" / f"wbuffix_{cmode}" / f"map{mp}_bs4k_r{r}"
            if (d / "fio.json").exists():
                w = json.loads(read(d / "fio.json"))["jobs"][0]["write"]
                ct = read(d / "cache.txt")
                cb = re.search(r"before:.*?Cached:(\d+)", ct)
                ca = re.search(r"after:.*?Cached:(\d+)", ct)
                pc.append([cmode, mp.upper(), "4K", str(r), f"{w['bw'] / 1024:.1f}", f"{w['clat_ns']['mean'] / 1e3:.1f}",
                           f"{round(int(cb.group(1)) / 1024):,}" if cb else "–", f"{round(int(ca.group(1)) / 1024):,}" if ca else "–"])
if pc:
    R.table(["조건", "매핑", "bs", "회", "MiB/s", "clat 평균 µs", "Cached 전 (MiB)", "Cached 후 (MiB)"], pc,
            widths=[1.8, 1.5, 1.2, 1.0, 2.4, 2.6, 3.2, 3.3], size=8.5, caption="페이지 캐시 drop 사전 시험 (wbuffix, 8 s, 2 회, insmod 후 대기 2 s, 15:57–15:59 KST)", align_right_from=3)
R.p("본 실험 전에 drop 절차가 동작하는지 확인했다. 시험 직전 서버의 페이지 캐시는 약 10 GB(Cached 10,227,884 kB)였고 drop 후 약 240 MiB 로 줄었다. "
    "그 전 base 회차들이 쏟아낸 수천만 줄의 커널 오류 로그가 journald 파일로 디스크에 쓰이며 쌓인 것으로 보인다. 8 초 시험에서 drop/no-drop 차이는 조합별 평균으로 4K/4K −0.12 %, 16K/4K −0.005 % 였고, 회차별로는 최대 0.17 %(4K/4K 1 회차: 1553.2 → 1550.6 MiB/s)였다.", size=9.5)

# ============================================================================ 6
R.h("6. 결과 — 주 데이터셋 (" + EXP + ")")
if not AGG:
    R.note("분석 결과(analysis/summary_agg.csv)가 아직 없다.")
else:
    lt = lambda mp, bs: kib(bs) < kib(mp)  # noqa: E731
    hdr = ["매핑 \\ bs"] + [x.upper() for x in PRI["sizes"]]
    W = [2.6] + [round(14.4 / len(PRI["sizes"]), 2)] * len(PRI["sizes"])
    main_v = "wbuffix_nodrop" if "wbuffix_nodrop" in PRI["variants"] else PRI["variants"][0]
    R.h("6.1 성능 표 — 페이지 캐시 그대로 (" + main_v + ")", 2)
    R.p("모든 값은 3 회 평균이다(± 는 표본 표준편차). * 는 bs < 매핑 단위 조합이다. drop 조건의 값은 6.2 절과 부록 D 에 있다(조합별 3 회 평균의 차이: 대역폭·IOPS·평균 지연 0.4 % 이내, 첫 GC 시각·GC 이후/마지막 20 s 대역폭·WAF 0.7 % 이내, p99 지연 1 % 이내).", size=9)
    for metric, nd, std, cap in (("bw_MiBps", 1, True, "쓰기 대역폭 MiB/s, 60 s 평균"), ("iops", 0, False, "IOPS, 60 s 평균"),
                                 ("clat_mean_us", 1, True, "평균 완료 지연 µs"), ("clat_p99_us", 0, False, "p99 완료 지연 µs"),
                                 ("gc_onset_s", 2, True, "첫 GC 시각 s (fio 시작 기준)"), ("bw_pre_gc_MiBps", 1, False, "GC 이전 구간 평균 대역폭 MiB/s"),
                                 ("bw_post_gc_MiBps", 1, False, "GC 이후 구간 평균 대역폭 MiB/s"), ("bw_last20s_MiBps", 1, False, "마지막 20 s 평균 대역폭 MiB/s"),
                                 ("waf_gc", 2, False, "GC 쓰기 증폭 WAF_GC (매핑 단위 페이지 기준)"), ("waf_total", 2, False, "전체 쓰기 증폭 WAF_total (NAND 바이트 ÷ 호스트 바이트)")):
        R.table(hdr, matrix_rows(main_v, metric, nd, std, lt), widths=W, size=8.5, caption=f"{cap} — {main_v}", align_right_from=1, bold_first_col=True)
    for fig, cap in ((f"fig_bw_vs_bs_{main_v}.png", "bs 에 따른 쓰기 대역폭 (매핑 단위별, 평균 ± 표준편차)"),
                     (f"fig_bw_heatmap_{main_v}.png", "매핑 단위 × bs 평균 대역폭"),
                     (f"fig_clat_mean_vs_bs_{main_v}.png", "평균 완료 지연 (로그 축)"),
                     (f"fig_clat_p99_vs_bs_{main_v}.png", "p99 완료 지연 (로그 축)"),
                     (f"fig_waf_heatmap_{main_v}.png", "전체 쓰기 증폭")):
        if (AN / fig).exists():
            R.figure(AN / fig, f"{cap} — {main_v}", 14.5)
    R.h("6.2 OS 페이지 캐시 drop 의 영향", 2)
    R.p("같은 (매핑, bs, 회차)에서 연달아 잰 nodrop·drop 두 회차를 짝지어 차이(drop − nodrop)를 보았다. p 는 짝지은 t-검정(양측, 자유도 = 쌍 수 − 1)이다. "
        "맨 아래 '전체' 행은 9 조합 × 3 회 = 27 쌍의 상대 차이를 모은 평균과 95 % 신뢰구간이다.", size=9.5)
    cache = PRI["cache"]
    if cache:
        for metric, label in (("bw_MiBps", "대역폭"), ("clat_mean_us", "평균 완료 지연"), ("clat_p99_us", "p99 지연"), ("gc_onset_s", "첫 GC 시각")):
            rows62 = []
            for c in cache:
                if c["metric"] != metric:
                    continue
                if c["map"] == "ALL":
                    rows62.append(["전체", "", str(int(c["n_pairs"])), "–", "–", f"{c['mean_diff_pct']:+.3f} %",
                                   f"[{c.get('ci95_low_pct', float('nan')):+.3f}, {c.get('ci95_high_pct', float('nan')):+.3f}] %", f"{c['p_two_sided']:.3f}"])
                else:
                    rows62.append([c["map"].upper(), c["bs"].upper(), str(int(c["n_pairs"])), fnum(c["nodrop_mean"], 2), fnum(c["drop_mean"], 2),
                                   f"{c['mean_diff_pct']:+.3f} %", "", fnum(c.get("p_two_sided"), 3)])
            if rows62:
                R.table(["매핑", "bs", "쌍", "nodrop 평균", "drop 평균", "차이 (drop−nodrop)", "95 % CI", "p"], rows62,
                        widths=[1.4, 1.2, 1.0, 2.5, 2.5, 3.0, 3.6, 1.8], size=8, caption=f"페이지 캐시 drop 영향 — {label} ({metric})", align_right_from=2)
    else:
        R.p("(cache_compare.csv 없음)")
    if (AN / "fig_variant_compare.png").exists():
        R.figure(AN / "fig_variant_compare.png", "nodrop / drop 대역폭 비교 (회색 = bs < 매핑 단위)", 16.5)
    R.h("6.3 시간에 따른 대역폭", 2)
    R.p("각 칸은 (매핑 단위, bs) 조합 하나이며 3 회차를 겹쳐 그렸다. 점선은 그 회차의 첫 GC 시각이다. 대역폭이 GC 시작 직후 급락했다가 fio randommap 주기에 따라 "
        "회복·급등하는 모양(5.5 절)을 볼 수 있다.", size=9)
    for v in PRI["variants"]:
        if (AN / f"fig_timeseries_{v}.png").exists():
            R.figure(AN / f"fig_timeseries_{v}.png", f"0.5 s 평균 쓰기 대역폭 시계열 — {v}", 16.5)
    R.h("6.4 반복 간 편차", 2)
    cvs = []
    for v in PRI["variants"]:
        vals = [a["bw_MiBps_std"] / a["bw_MiBps_mean"] * 100 for a in AGG if a["variant"] == v and a["bw_MiBps_mean"]]
        if vals:
            worst = max((a for a in AGG if a["variant"] == v and a["bw_MiBps_mean"]), key=lambda a: a["bw_MiBps_std"] / a["bw_MiBps_mean"])
            cvs.append([v, f"{sum(vals) / len(vals):.2f} %", f"{max(vals):.2f} %", f"{worst['map'].upper()} / {worst['bs'].upper()}"])
    R.table(["변형", "평균 변동계수(CV)", "최대 CV", "최대 CV 조합 (매핑/bs)"], cvs, widths=[3.4, 4.0, 3.0, 6.6], size=8.5, caption="대역폭의 반복 간 변동계수")
    if FINDINGS:
        R.h("6.5 관찰", 2)
        R.bullets(FINDINGS)

# ============================================================================ 7
if SUP:
    R.h("7. 보조 데이터셋 — 첫 설계 (" + SUP["name"] + ", 부분)")
    R.p("첫 설계(매핑 4–128K × bs 4–128K × 3 회 × base·wbuffix)는 설계 변경으로 15:51:23 KST 에 멈췄다. 완료한 회차는 base " + str(n_sup.get("base", 0)) +
        " 회(+ FAILED " + str(len(SUP["failed"])) + " 회), wbuffix " + str(n_sup.get("wbuffix", 0)) + " 회다. 주 데이터셋과 같은 모듈 바이너리·절차이며 페이지 캐시는 그대로(nodrop)였다. "
        "칸의 (n=…) 는 완료 회차 수다.", size=9.5)
    lt = lambda mp, bs: kib(bs) < kib(mp)  # noqa: E731
    hdr7 = ["매핑 \\ bs"] + [x.upper() for x in SUP["sizes"]]
    W7 = [2.0] + [round(15.0 / len(SUP["sizes"]), 2)] * len(SUP["sizes"])
    for v in SUP["variants"]:
        R.table(hdr7, matrix_rows(v, "bw_MiBps", 1, True, lt, SUP), widths=W7, size=7.5, caption=f"쓰기 대역폭 MiB/s — 보조 · {v} (* bs < 매핑)",
                align_right_from=1, bold_first_col=True)
    rows7 = []
    for mp in SUP["sizes"]:
        for bs in SUP["sizes"]:
            a, b = agg("base", mp, bs, SUP), agg("wbuffix", mp, bs, SUP)
            if not a or not b:
                continue
            d = (b["bw_MiBps_mean"] - a["bw_MiBps_mean"]) / a["bw_MiBps_mean"] * 100 if a["bw_MiBps_mean"] else float("nan")
            rows7.append([mp.upper(), bs.upper(), "예" if lt(mp, bs) else "", fnum(a["bw_MiBps_mean"]), fnum(b["bw_MiBps_mean"]), f"{d:+.1f} %",
                          fnum(a.get("chmodel_msgs_mean", 0), 0), fnum(b.get("chmodel_msgs_mean", 0), 0)])
    if rows7:
        R.table(["매핑", "bs", "bs<매핑", "base MiB/s", "wbuffix MiB/s", "차이", "base 채널모델\n오류 줄", "wbuffix\n오류 줄"], rows7,
                widths=[1.5, 1.5, 1.5, 2.3, 2.5, 1.8, 3.0, 2.4], size=7.5, caption="보조 데이터셋 base / wbuffix 비교 (둘 다 완료한 조합)", align_right_from=3)
    R.p("bs ≥ 매핑 단위 조합에서는 두 변형의 차이가 반복 편차 수준이고(같은 코드 경로), bs < 매핑 단위 조합에서만 base 가 채널 모델 오류를 수백만 줄 내며 다른 값을 낸다(5.4 절). "
        "매핑 32K·bs 16K 의 base 는 장치가 멈췄다(5.6 절).", size=9.5)
    for fig, cap in (("fig_timeseries_wbuffix.png", "보조 · wbuffix 시계열 (6 × 6)"), ("fig_variant_compare.png", "보조 · base / wbuffix 대역폭 비교")):
        if (SUP["an"] / fig).exists():
            R.figure(SUP["an"] / fig, cap, 17.0)

# ============================================================================ 8 (sequential write)
def _merge_fn_src():
    m = re.search(r"static bool ksc_conv_write_merge\(.*?\n}\n", read(REPO / "nvmevirt" / "conv_ftl.c"), re.S)
    return m.group(0) if m else "(conv_ftl.c 에 ksc_conv_write_merge 없음)"


def _pre_row(d, label):
    """one pre-check run directory -> table row"""
    w = json.loads(read(d / "fio.json"))["jobs"][0]["write"]
    meta, un = read(d / "meta.txt"), read(d / "dmesg_unload.txt")
    mp = kib(re.search(r"map(\d+k)", d.name).group(1)) * 1024
    host = sum(int(x) for x in re.findall(r"host_pgs=(\d+)", un))
    gcp = sum(int(x) for x in re.findall(r"gc_pgs=(\d+)", un))
    bm = re.search(r"blk_writes:\s*ios=(\d+) merges=(\d+) sectors=(\d+)", meta)
    req = f"{int(bm.group(3)) * 512 / 1024 / int(bm.group(1)):.1f}" if bm and int(bm.group(1)) else "–"
    nm = re.search(r"nomerges=(\d)", meta)
    return [label, d.parent.name, re.sub(r"_r1$", "", d.name).replace("map", "").replace("_bs", " / ").upper(), nm.group(1) if nm else "–",
            f"{w['bw'] / 1024:,.1f}", f"{int(bm.group(2)):,}" if bm else "–", req,
            f"{host * mp / w['io_bytes']:.3f}" if host else "–", f"{(host + gcp) * mp / w['io_bytes']:.3f}" if host else "–"]


if SEQ:
    R.h("8. 추가 실험 — 순차 쓰기 (" + SEQ["name"] + ")")
    R.h("8.1 목적과 설계", 2)
    R.p("주 데이터셋과 같은 매핑 단위·bs 조합에서 랜덤 쓰기 대신 순차 쓰기를 쟀다(사용자 요청, 19:53 KST). 순차 쓰기에서는 같은 매핑 단위로 작은 쓰기가 연달아 오므로, "
        "실제 SSD 는 쓰기 버퍼에서 이를 합쳐 매핑 단위 페이지를 한 번만 쓴다. NVMeVirt 원래 모델은 합치지 않고 쓰기마다 페이지를 새로 쓴다(5.5 절). "
        "그래서 원래 모델(wbuffix, 주 데이터셋과 같은 모듈 파일)과, 이 연구에서 추가한 쓰기 버퍼 병합 모델(merge, 8.2 절)을 함께 쟀다(사용자 선택).", size=9.5)
    R.table(["구분", "값"], [
        ["변수", "매핑 단위 4K·16K·32K × fio bs 4K·16K·32K × 모델 {wbuffix, merge}"],
        ["반복", "조합마다 3 회 (회차마다 rmmod → insmod) — 9 × 2 × 3 = 54 회"],
        ["순서", "반복 r = 1, 2, 3 마다 wbuffix 9 조합 → merge 9 조합 (run_all_seq.sh)"],
        ["fio", "rw=write (순차, offset 0 부터, 장치 끝에서 0 으로 돌아감), 나머지는 주 데이터셋과 같음: libaio, direct=1, iodepth 32, numjobs 1, 60 s, ramp_time 0"],
        ["OS 페이지 캐시", "그대로 (nodrop) — 주 데이터셋에서 drop 영향이 없었음(6.2 절), 사용자 선택"],
        ["블록 계층", "회차마다 insmod 직후 echo 2 > /sys/block/nvme1n1/queue/nomerges (요청 병합 끔). 스케줄러는 커널 기본 mq-deadline"],
        ["모듈", "wbuffix: 주 데이터셋과 같은 .ko (SHA-256 같음) / merge: 커밋 66446ea 에서 make MAPPING_UNIT=<바이트> GC_STATS=1 WBUF_FIX=1 WBUF_MERGE=1"],
        ["그 밖", "장치·CPU·insmod 인자·SETTLE 5 s·결과 파일 구성은 주 데이터셋과 같음 (3–4 절)"],
    ], widths=[3.0, 14.0], size=8.5, caption="순차 쓰기 실험 설계")
    R.p("블록 계층 병합을 끈 이유: 커널 기본 설정(nomerges=0)에서는 fio 의 순차 4K 쓰기(QD 32)가 블록 계층에서 합쳐져 장치에 평균 약 120 KiB 요청으로 도착했다(8.3 절 표의 첫 줄). "
        "이 상태에서는 bs 축이 의미를 잃는다. 랜덤 쓰기는 인접한 요청이 거의 없어 영향이 없다(8.3 절).", size=9.5)

    R.h("8.2 쓰기 버퍼 병합 모델 (merge, WBUF_MERGE=1)", 2)
    R.bullets([
        "파티션(FTL 인스턴스 4 개)마다 '열린 매핑 단위' 하나를 둔다. 매핑 단위 일부만 덮는 쓰기가 오면 그 단위를 열고 쓰기 버퍼에서 매핑 단위 하나만큼을 잡는다.",
        "같은 단위로 다음 쓰기가 오면 버퍼를 더 잡지 않고 합류시킨다(섹터 비트맵). 단위의 모든 섹터가 채워지면 그때 매핑 단위 페이지 하나를 flash 에 쓴다(원본과 같은 쓰기 경로: 페이지 배정 → wordline 이 차면 프로그램 → 버퍼 반납).",
        "같은 파티션에 다른 단위의 부분 쓰기가 오면 열린 단위를 덜 찬 채로 쓰고(evict, 원본과 같이 옛 데이터 읽기는 모델링하지 않음) 새 단위를 연다.",
        "매핑 단위 전체를 덮는 쓰기는 원본(wbuffix)과 똑같이 바로 쓴다. 따라서 bs ≥ 매핑 단위이면 두 모델의 동작이 같다.",
        "버퍼 장부: 쓰는 페이지마다 매핑 단위 하나가 정확히 한 번 할당되어 반납과 맞는다. 계속 붙잡히는 양은 파티션당 열린 단위 1 개와 덜 찬 wordline 으로 128 KiB 이하다(버퍼 1 MiB).",
        "한계: 파티션마다 열린 단위가 1 개뿐이다(실제 SSD 는 버퍼 전체를 여러 단위에 쓸 수 있다). 하나의 순차 흐름에는 충분하다. FUA·FLUSH 는 원본처럼 열린 단위를 강제로 쓰지 않는다(이 장치는 VWC=0 이라 커널이 보내지 않음).",
        "WBUF_MERGE=0 빌드(base·wbuffix)는 이 변경 전과 같은 기계어다(디스어셈블리 비교로 확인).",
    ])
    R.p("코드 검토: 실행 전에 에이전트 4 개가 관점 하나씩(쓰기 버퍼 장부, FTL 상태, 실험에 맞는 모델 동작, 커널 안전성) 독립적으로 읽고, 지적마다 반박 검증 1 개를 두었다(20:01–20:13 KST). "
        "고칠 결함은 없었다. 장부 로직은 Python 으로 옮겨 무작위 명령 약 180 만 개(매핑 단위 3 종 × 시드 30 × 명령 2 만)로 퍼징했다(위반 없음). 지적 1 건(FUA/FLUSH 가 열린 단위를 내보내지 않음)은 원본과 같은 단순화로 판정되어 주석만 보강했다. "
        "rmmod 때 파티션마다 병합 통계(open·merge·full·evict·direct·still_open)를 찍는다.", size=9.5)
    R.code(_merge_fn_src())

    R.h("8.3 사전 점검", 2)
    pre = []
    for label, base in (("A. 블록 계층 기본값", "pre_seq_blkmerge_default"), ("B. 순차, 병합 끔", "pre_seq_check"), ("C. 랜덤 (주 데이터셋 설정)", "pre_rand_merge_check")):
        for v in ("wbuffix", "merge"):
            for d in sorted((EXPD / "results" / base / v).glob("map*_r1"), key=lambda x: (kib(re.search(r"map(\d+k)", x.name).group(1)), kib(re.search(r"bs(\d+k)", x.name).group(1)))):
                if (d / "fio.json").exists():
                    pre.append(_pre_row(d, label))
    if pre:
        R.table(["점검", "모델", "매핑 / bs", "nomerges", "MiB/s", "블록 계층\n합친 수", "평균 요청\nKiB", "호스트\nWAF", "WAF\ntotal"], pre,
                widths=[3.4, 1.6, 2.0, 1.4, 1.6, 1.9, 1.6, 1.6, 1.6], size=7.5,
                caption="순차 쓰기 사전 점검 (15 s, 1 회, 20:18–20:23 KST; 호스트 WAF = FTL 이 쓴 매핑 단위 페이지 × 매핑 단위 ÷ fio 바이트)", align_right_from=3)
    R.p("A: 커널 기본값에서는 순차 4K 쓰기가 평균 약 120 KiB 요청으로 합쳐졌다. B: 병합을 끄면 장치가 받는 요청이 fio 의 bs 와 같아진다. 이때 wbuffix 의 호스트 WAF 는 정확히 매핑/bs(4·8·2)이고, "
        "merge 는 1.000 이다(16K/4K 에서 단위마다 쓰기 4 개를 합쳐 한 번 씀). bs = 매핑이면 두 모델의 결과가 같다. "
        "C: 랜덤 쓰기에서는 합칠 쓰기가 거의 없어 두 모델이 같고(−0.7 %), 블록 계층 병합도 15 s 동안 1 건뿐이다. 따라서 주 데이터셋(블록 계층 기본값)도 병합 영향이 없다.", size=9.5)

    SA = SEQ["agg"]
    if SA:
        lt = lambda mp, bs: kib(bs) < kib(mp)  # noqa: E731
        hdr8 = ["매핑 \\ bs"] + [x.upper() for x in SEQ["sizes"]]
        W8 = [2.6] + [round(14.4 / len(SEQ["sizes"]), 2)] * len(SEQ["sizes"])
        R.h("8.4 결과 표", 2)
        R.p("모든 값은 3 회 평균(± 는 표본 표준편차)이다. * 는 bs < 매핑 단위 조합이다.", size=9)
        for metric, nd, std, cap in (("bw_MiBps", 1, True, "쓰기 대역폭 MiB/s, 60 s 평균"), ("iops", 0, False, "IOPS, 60 s 평균"),
                                     ("clat_mean_us", 1, False, "평균 완료 지연 µs"), ("clat_p99_us", 0, False, "p99 완료 지연 µs"),
                                     ("waf_total", 3, False, "전체 쓰기 증폭 WAF_total (NAND 바이트 ÷ 호스트 바이트)"),
                                     ("bw_post_gc_MiBps", 1, False, "GC 이후 구간 평균 대역폭 MiB/s")):
            for v in SEQ["variants"]:
                R.table(hdr8, matrix_rows(v, metric, nd, std, lt, SEQ), widths=W8, size=8.5, caption=f"{cap} — 순차 · {v}", align_right_from=1, bold_first_col=True)
        cmp8 = []
        for mp in SEQ["sizes"]:
            for bs in SEQ["sizes"]:
                a, b = agg("wbuffix", mp, bs, SEQ), agg("merge", mp, bs, SEQ)
                if not a or not b:
                    continue
                cmp8.append([mp.upper(), bs.upper(), "예" if lt(mp, bs) else "", fnum(a["bw_MiBps_mean"]), fnum(b["bw_MiBps_mean"]),
                             f"{(b['bw_MiBps_mean'] - a['bw_MiBps_mean']) / a['bw_MiBps_mean'] * 100:+.1f} %",
                             fnum(a.get("waf_total_mean"), 3), fnum(b.get("waf_total_mean"), 3)])
        if cmp8:
            R.table(["매핑", "bs", "bs<매핑", "wbuffix MiB/s", "merge MiB/s", "차이", "WAF_total\nwbuffix", "WAF_total\nmerge"], cmp8,
                    widths=[1.5, 1.5, 1.5, 2.6, 2.6, 2.0, 2.6, 2.7], size=8, caption="순차 쓰기 — 원래 모델(wbuffix)과 병합 모델(merge)", align_right_from=3)
        mg = [[a["map"].upper(), a["bs"].upper()] + [fnum(a.get(f"{k}_mean"), 0) for k in ("mg_open", "mg_merge", "mg_full", "mg_evict", "mg_direct", "mg_still_open")]
              for a in sorted((a for a in SA if a["variant"] == "merge"), key=lambda a: (kib(a["map"]), kib(a["bs"])))]
        if mg:
            R.table(["매핑", "bs", "open", "merge", "full", "evict", "direct", "still_open"], mg, widths=[1.5, 1.5, 2.4, 2.6, 2.4, 1.8, 2.4, 2.4], size=8,
                    caption="merge 모델의 병합 통계 (4 파티션 합, 3 회 평균)", align_right_from=2)
        blk = [r for r in SEQ["runs"] if r.get("blk_wr_ios") not in ("", None)]
        if blk:
            mx = max(r["blk_wr_merges"] for r in blk)
            dev = max(abs(r["blk_avg_req_KiB"] - kib(r["bs"])) for r in blk)
            R.p(f"블록 계층 확인: {len(blk)} 회차 모두 fio 동안 블록 계층이 합친 요청은 최대 {mx:,.0f} 건이고, 장치가 받은 평균 요청 크기와 bs 의 차이는 최대 {dev:.3f} KiB 다.", size=9.5)
        R.h("8.5 그림", 2)
        PL = SEQ["dir"] / "plots"
        for path, cap in ((PL / "compare_bw_MiBps.png", "순차 쓰기 대역폭 — wbuffix / merge (회색 = bs < 매핑 단위)"),
                          (PL / "compare_waf_total.png", "순차 쓰기 WAF_total — wbuffix / merge"),
                          (PL / "bs_bw_MiBps.png", "bs 에 따른 순차 쓰기 대역폭 (모델별 패널)"),
                          *[(SEQ["an"] / f"fig_timeseries_{v}.png", f"0.5 s 평균 순차 쓰기 대역폭 시계열 — {v} (점선 = 첫 GC)") for v in SEQ["variants"]]):
            if path.exists():
                R.figure(path, cap, 16.0)
        R.h("8.6 랜덤 쓰기와 비교", 2)
        main_v = "wbuffix_nodrop" if "wbuffix_nodrop" in PRI["variants"] else PRI["variants"][0]
        rows86 = []
        for mp in SEQ["sizes"]:
            for bs in SEQ["sizes"]:
                r_, w_, m_ = agg(main_v, mp, bs), agg("wbuffix", mp, bs, SEQ), agg("merge", mp, bs, SEQ)
                rows86.append([mp.upper(), bs.upper(), "예" if lt(mp, bs) else "", fnum(r_["bw_MiBps_mean"]) if r_ else "–", fnum(w_["bw_MiBps_mean"]) if w_ else "–",
                               fnum(m_["bw_MiBps_mean"]) if m_ else "–", fnum(r_.get("waf_total_mean"), 2) if r_ else "–", fnum(w_.get("waf_total_mean"), 2) if w_ else "–",
                               fnum(m_.get("waf_total_mean"), 2) if m_ else "–"])
        R.table(["매핑", "bs", "bs<매핑", "랜덤\nMiB/s", "순차 wbuffix\nMiB/s", "순차 merge\nMiB/s", "랜덤\nWAF", "순차 wbuffix\nWAF", "순차 merge\nWAF"], rows86,
                widths=[1.4, 1.3, 1.5, 1.9, 2.3, 2.2, 1.6, 2.4, 2.4], size=8, caption=f"60 s 평균 대역폭과 WAF_total — 랜덤({EXP} · {main_v}) / 순차({SEQ['name']})", align_right_from=3)
        R.h("8.7 반복 간 편차", 2)
        cvs8 = []
        for v in SEQ["variants"]:
            aa = [a for a in SA if a["variant"] == v and a["bw_MiBps_mean"]]
            if aa:
                worst = max(aa, key=lambda a: a["bw_MiBps_std"] / a["bw_MiBps_mean"])
                cvs8.append([v, f"{sum(a['bw_MiBps_std'] / a['bw_MiBps_mean'] for a in aa) / len(aa) * 100:.2f} %",
                             f"{worst['bw_MiBps_std'] / worst['bw_MiBps_mean'] * 100:.2f} %", f"{worst['map'].upper()} / {worst['bs'].upper()}"])
        R.table(["모델", "평균 변동계수(CV)", "최대 CV", "최대 CV 조합 (매핑/bs)"], cvs8, widths=[3.4, 4.0, 3.0, 6.6], size=8.5, caption="순차 쓰기 대역폭의 반복 간 변동계수")
        if FINDINGS_SEQ:
            R.h("8.8 관찰", 2)
            R.bullets(FINDINGS_SEQ)
    else:
        R.note("순차 쓰기 분석 결과(analysis/summary_agg.csv)가 아직 없다.")

# ============================================================================ random write, bs 8k/64k
if RBS:
    R.h(RBS_N + ". 추가 실험 — 랜덤 쓰기 bs 8K·64K (" + RBS["name"] + ")")
    R.h(RBS_N + ".1 목적과 설계", 2)
    R.p("주 데이터셋의 랜덤 쓰기(bs 4K·16K·32K)에 bs 8K 와 64K 를 더해, 매핑 단위 4K·16K·32K 에서 bs 를 5 단계로 본다(사용자 요청, 22:08 KST). "
        "사용자 선택에 따라 매핑 단위는 그대로 두고 bs 만 늘렸다. 새 조합(매핑 3 × bs 2)만 측정했고, bs 4K·16K·32K 는 주 데이터셋 nodrop 회차를 그대로 쓴다. "
        "두 데이터셋은 같은 wbuffix 모듈 파일(SHA-256 같음)·같은 fio 설정·같은 절차이며, 블록 계층 설정도 같다(커널 기본값).", size=9.5)
    R.table(["구분", "값"], [
        ["새로 잰 조합", f"매핑 단위 4K·16K·32K × fio bs 8K·64K × 3 회 = 18 회 ({RBS['name']}/wbuffix/)"],
        ["재사용한 조합", f"매핑 4K·16K·32K × bs 4K·16K·32K × 3 회 = 27 회 ({EXP}/wbuffix_nodrop/, 6 절)"],
        ["합친 보기", (f"{RV['name']}/wbuffix/ — 두 폴더의 회차를 상대 심볼릭 링크로 모은 것(exp/link_runs.py, SOURCES.txt). analyze.py·plot.py 가 보통 데이터셋처럼 읽는다" if RV else "–")],
        ["fio", "rw=randwrite, libaio, direct=1, iodepth 32, numjobs 1, 60 s, ramp_time 0, randrepeat=1 (주 데이터셋과 같음)"],
        ["모델·캐시·블록 계층", "wbuffix, 페이지 캐시 그대로(nodrop), nomerges 커널 기본값 (주 데이터셋과 같음)"],
        ["순서", "반복 1→3, 매핑 4K→32K, bs 8K→64K (run_all_rand_bs.sh)"],
    ], widths=[3.4, 13.6], size=8.5, caption="랜덤 쓰기 bs 8K·64K 실험 설계")
    blk = [r for r in RBS["runs"] if r.get("blk_wr_ios") not in ("", None)]
    if blk:
        R.p(f"블록 계층 확인: 새 {len(blk)} 회차에서 fio 동안 블록 계층이 합친 요청은 최대 {max(r['blk_wr_merges'] for r in blk):,.0f} 건이고, "
            f"장치가 받은 평균 요청 크기와 bs 의 차이는 최대 {max(abs(r['blk_avg_req_KiB'] - kib(r['bs'])) for r in blk):.3f} KiB 다.", size=9.5)
    D = RV or RBS
    if D and D["agg"]:
        lt = lambda mp, bs: kib(bs) < kib(mp)  # noqa: E731
        hdrR = ["매핑 \\ bs"] + [x.upper() + (" †" if x in ("8k", "64k") else "") for x in D["bss"]]
        WR = [2.4] + [round(14.6 / len(D["bss"]), 2)] * len(D["bss"])
        R.h(RBS_N + ".2 결과 표 (매핑 3 × bs 5)", 2)
        R.p("모든 값은 3 회 평균(± 는 표본 표준편차)이다. † 열(bs 8K·64K)이 이번에 잰 값이고, 나머지 열은 주 데이터셋 nodrop 회차(6.1 절 표와 같은 값)다. * 는 bs < 매핑 단위다.", size=9)
        v0 = D["variants"][0]
        for metric, nd, std, cap in (("bw_MiBps", 1, True, "쓰기 대역폭 MiB/s, 60 s 평균"), ("iops", 0, False, "IOPS, 60 s 평균"),
                                     ("clat_mean_us", 1, False, "평균 완료 지연 µs"), ("clat_p99_us", 0, False, "p99 완료 지연 µs"),
                                     ("waf_total", 2, False, "전체 쓰기 증폭 WAF_total"), ("gc_onset_s", 2, False, "첫 GC 시각 s"),
                                     ("bw_pre_gc_MiBps", 1, False, "GC 이전 구간 평균 대역폭 MiB/s"), ("bw_post_gc_MiBps", 1, False, "GC 이후 구간 평균 대역폭 MiB/s"),
                                     ("bw_last20s_MiBps", 1, False, "마지막 20 s 평균 대역폭 MiB/s")):
            R.table(hdrR, matrix_rows(v0, metric, nd, std, lt, D), widths=WR, size=8.5, caption=f"{cap} — 랜덤 · 매핑 3 × bs 5", align_right_from=1, bold_first_col=True)
        R.h(RBS_N + ".3 그림", 2)
        for path, cap in ((D["an"] / f"fig_bw_vs_bs_{v0}.png", "bs 에 따른 랜덤 쓰기 대역폭 (매핑 단위별, 평균 ± 표준편차)"),
                          (D["an"] / f"fig_bw_heatmap_{v0}.png", "매핑 단위 × bs 평균 대역폭"),
                          (D["an"] / f"fig_waf_heatmap_{v0}.png", "전체 쓰기 증폭 WAF_total"),
                          (D["an"] / f"fig_clat_mean_vs_bs_{v0}.png", "평균 완료 지연 (로그 축)"),
                          (D["an"] / f"fig_timeseries_{v0}.png", "0.5 s 평균 랜덤 쓰기 대역폭 시계열 (3 회 겹침, 점선 = 첫 GC)")):
            if path.exists():
                R.figure(path, cap, 16.0 if "timeseries" in path.name else 14.5)
        R.h(RBS_N + ".4 반복 간 편차", 2)
        cvr = []
        for label, ds in (("새로 잰 bs 8K·64K", RBS), ("합친 보기 전체", D)):
            aa = [a for a in ds["agg"] if a["bw_MiBps_mean"]]
            if aa:
                worst = max(aa, key=lambda a: a["bw_MiBps_std"] / a["bw_MiBps_mean"])
                cvr.append([label, f"{sum(a['bw_MiBps_std'] / a['bw_MiBps_mean'] for a in aa) / len(aa) * 100:.2f} %",
                            f"{worst['bw_MiBps_std'] / worst['bw_MiBps_mean'] * 100:.2f} %", f"{worst['map'].upper()} / {worst['bs'].upper()}"])
        R.table(["범위", "평균 변동계수(CV)", "최대 CV", "최대 CV 조합 (매핑/bs)"], cvr, widths=[3.6, 4.0, 3.0, 6.4], size=8.5, caption="대역폭의 반복 간 변동계수")
        if FINDINGS_RBS:
            R.h(RBS_N + ".5 관찰", 2)
            R.bullets(FINDINGS_RBS)
    else:
        R.note("랜덤 쓰기 bs 8K·64K 분석 결과가 아직 없다.")

# ============================================================================ 8
R.h(POST_N + ". 실험 후 상태와 정리")
diff_rows = []
for ds in [d for d in (PRI, SUP, SEQ, RBS) if d]:
    envb = ds["dir"] / "env_before"
    for ad in sorted(p for p in ds["dir"].iterdir() if p.name.startswith("env_after")):
        for f in sorted(envb.glob("*.txt")):
            if f.name in ("00_date.txt", "12_dimm.txt"):
                continue
            ign = re.compile(r"loadavg|^\d+\.\d+ \d+\.\d+|Mem:|Swap:|MemFree|MemAvailable|AnonHugePages|^\$ |^[0-9.]+ [0-9.]+ [0-9.]+ \d+/\d+")
            al = [ln for ln in read(f).splitlines() if not ign.search(ln)]
            bl = [ln for ln in last_snapshot(read(ad / f.name)).splitlines() if not ign.search(ln)]
            changed = [ln for ln in difflib.unified_diff(al, bl, lineterm="", n=0) if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
            if changed:
                diff_rows.append([f"{ds['name']}/{ad.name}", f.name, "\n".join(changed[:6]) + ("\n…" if len(changed) > 6 else "")])
R.p("실험 전(env_before)과 끝난 뒤(env_after_*) 환경 스냅샷을 비교했다. 날짜·부하·여유 메모리처럼 늘 바뀌는 값은 빼고 달라진 줄만 적었다.")
if diff_rows:
    R.table(["스냅샷", "파일", "달라진 줄 (- 전 / + 후)"], diff_rows, widths=[4.4, 3.0, 9.6], size=7.5, caption="실험 전후 환경 차이")
else:
    R.p("커널 명령줄·CPU 주파수 설정·버전·블록 장치·모듈 목록 모두 실험 전과 같았다.")
R.table(["항목", "실험 전", "실험 중", "실험 후"], [
    ["GRUB / 커널 명령줄", "memmap=12G$12G isolcpus=3-5", "변경 없음", "변경 없음"],
    ["nvmev 모듈", "적재 안 됨", "회차마다 적재·내림", "적재 안 됨 (마지막 rmmod)"],
    ["/dev/nvme1n1", "없음", "회차마다 생겼다 사라짐", "없음"],
    ["/etc/sudoers.d/nvmevirt-exp", "없음", "설치 (3.3 절)" + (" · 18:33 제거 후 순차 쓰기 실험용으로 20:17 다시 설치" if SEQ else "") + (" · 랜덤 bs 8K·64K 실험용으로 22:11 다시 설치" if RBS else ""),
     (f"제거함 ({SUDOERS_REMOVED} KST, sudo rm)" if SUDOERS_REMOVED else "아직 설치되어 있음 — 정리 단계에서 제거 예정")
     + ((f" · 순차 쓰기 실험 후 {SUDOERS_REMOVED2} KST 다시 제거" if SUDOERS_REMOVED2 else " · 순차 쓰기 실험 후 제거 예정") if SEQ else "")
     + ((f" · 22:11 다시 설치, 랜덤 bs 8K·64K 실험 후 {SUDOERS_REMOVED3} KST 제거" if SUDOERS_REMOVED3 else " · 22:11 다시 설치, 랜덤 bs 8K·64K 실험 후 제거 예정") if RBS else "")],
    *([["블록 장치 nomerges", "0 (커널 기본)", "순차 쓰기 회차마다 insmod 직후 2", "장치가 rmmod 로 사라져 설정도 없어짐"]] if SEQ else []),
    ["CPU governor / 터보", "powersave / 켬", "변경 없음", "변경 없음"],
    ["NVMeVirt 저장소 위치", "–", "/home/dccearth/jsw/KSC2026/nvmevirt", "/home/dccearth/jsw/nvmevirt 로 이동 (사용자 지시)"],
    ["이전 실험 폴더 /home/dccearth/jsw/exp", "있음 (이전 iodepth 시험 등)", "사용 안 함", "삭제 (사용자 지시; 수치는 인계 기록에 보존)"],
    ["NVMeVirt 소스·결과·문서", f"원본 {UPSTREAM[:7]}", f"{HEAD[:7]} (3.4 절)" + (f", 순차 쓰기 {SEQ_HEAD[:7]}" if SEQ else "") + (f", 랜덤 bs 8K·64K {RBS_HEAD[:7]}" if RBS else ""),
     (f"GitHub main 과 태그 {PUSH_TAG} 로 push (결과·문서·생성기 포함)" if PUSH_TAG else f"push 예정 (작성 시점 origin/main = {git('rev-parse', '--short', 'origin/main') or '–'})")],
    ["예약 메모리 내용", "–", "rmmod/insmod 는 FTL 상태만 초기화 (저장 데이터는 지우지 않음)", "이전 회차 데이터가 남아 있음 (쓰기 전용 실험이라 무관)"],
], widths=[4.0, 3.6, 5.0, 4.4], size=8, caption="실험 전·중·후 설정 상태")
R.p("커밋 재작성(모두 첫 push 전, 코드·스크립트는 그대로이고 인계 기록 파일 한 줄만 다름): "
    "① 16:04 KST, 커밋 1d6cd03 에 인계 기록 파일의 한 줄(sudo 비밀번호와 서버 IP 앞부분 문자열)이 들어가 있어 그 줄만 고쳐 a93ef76 으로 다시 만들었다. "
    "② 18:3x KST, 인계 기록 머리말에 들어간 사용자의 Claude 계정 이메일을 빼려고 2a462a3 → 949ae38, a93ef76 → e598e75 로 다시 만들었다. "
    "따라서 원자료에 적힌 커밋은 다음과 같이 읽는다: 주 데이터셋 처음 4 회차(map4k_bs4k_r1·map4k_bs16k_r1 의 nodrop·drop)의 meta.txt 와 wbuffix_*/git_head.txt·env_before 의 1d6cd03, "
    "나머지 50 회차의 a93ef76 = e598e75 / 보조 데이터셋 wbuffix 53 회차의 2a462a3 = 949ae38 / base 21 회차의 5769378 은 그대로.", size=9)
R.code("""# 실험 후 정리 (서버) — 실제로 실행한 명령
lsmod | grep nvmev || echo "nvmev not loaded"
sudo rm /etc/sudoers.d/nvmevirt-exp      # """ + POST_N + """ 절 표의 시각 (18:33)
""" + ("""# 순차 쓰기 실험(8 절): 20:17 사용자가 다시 설치(3.3 절 install 명령), 실험 후 사용자가 다시 제거
sudo rm /etc/sudoers.d/nvmevirt-exp      # """ + (SUDOERS_REMOVED2 or "–") + """ KST
""" if SEQ else "") + ("""# 랜덤 쓰기 bs 8K·64K 실험(""" + RBS_N + """ 절): 22:11 사용자가 다시 설치, 실험 후 사용자가 다시 제거
sudo rm /etc/sudoers.d/nvmevirt-exp      # """ + (SUDOERS_REMOVED3 or "–") + """ KST
""" if RBS else "") + """mv /home/dccearth/jsw/KSC2026/nvmevirt /home/dccearth/jsw/nvmevirt
rm -rf /home/dccearth/jsw/exp""")

# ============================================================================ appendices
R.page_break()
R.h("부록 A. 스크립트 전문")
for rel in ("exp/common.sh", "exp/build_modules.sh", "exp/run_experiment.sh", "exp/collect_env.sh", "exp/jobs/randwrite.fio.in",
            "exp/jobs/seqwrite.fio.in", "exp/run_all.sh", "exp/run_all_6x6.sh", "exp/run_all_seq.sh", "exp/run_all_rand_bs.sh",
            "exp/link_runs.py", "exp/analyze.py", "exp/plot.py", "exp/make_gallery.py", "exp/requirements.txt", "exp/.gitignore"):
    R.h(f"A. {rel}", 2)
    R.code(read(REPO / rel))
R.p("부록의 스크립트는 문서를 만든 시점의 작업 트리 내용이다. 랜덤 쓰기 실험 때의 run_experiment.sh·common.sh·analyze.py 는 커밋 " + HEAD[:7] + " 의 것이며, "
    "그 뒤 순차 쓰기용으로 WORKLOAD·NOMERGES·블록 계층 기록·merge 변형을 더했다(기본값은 이전 동작과 같다; git diff " + HEAD[:7] + " " + (SEQ_HEAD[:7] if SEQ else "HEAD") + " -- exp).", size=9)
R.p("이 문서와 인계 기록을 만드는 exp/report/ 의 make_report.py · docx_helpers.py · make_md_results.py · findings_ko.txt · findings_seq_ko.txt · make_handoff.sh 는 "
    + (f"태그 {PUSH_TAG} 의 커밋에 있다" if PUSH_TAG else "작업 트리에 있다(커밋 예정)") + "(분량상 생략).", size=9)
R.page_break()
R.h("부록 B. NVMeVirt 변경 diff 전문 (원본 61c90f7 대비)")
MOVE = git("log", "--format=%H", "--grep=^Move NVMeVirt sources into nvmevirt/", "-1", HEAD)
R.p(f"원본 {UPSTREAM[:7]} 의 파일을 그대로 nvmevirt/ 로 옮긴 커밋({MOVE[:7]}, 내용 변경 없음) 이후의 변경이다: git diff {MOVE[:7]} {HEAD[:7]} -- nvmevirt", size=9)
R.code(git("diff", MOVE, HEAD, "--", "nvmevirt"))
if SEQ and SEQ_HEAD and SEQ_HEAD != HEAD:
    R.h("B-2. 순차 쓰기 실험에서 더한 변경 (쓰기 버퍼 병합 모델, " + HEAD[:7] + " → " + SEQ_HEAD[:7] + ")", 2)
    R.p(f"git diff {HEAD[:7]} {SEQ_HEAD[:7]} -- nvmevirt. WBUF_MERGE=0 인 빌드(base·wbuffix)는 이 변경 전과 같은 코드가 된다(8.2 절).", size=9)
    R.code(git("diff", HEAD, SEQ_HEAD, "--", "nvmevirt"))
R.page_break()
R.h("부록 C. 실험 전 환경 스냅샷 (env_before)")
R.p("exp/results/" + EXP + "/env_before/ 의 원본 출력을 그대로 옮겼다. 출력 안의 시각은 서버 시계 UTC 다(KST = UTC + 9 시간; 예: 09_block.txt 의 ls 시각 "
    "'Oct  7 12:22' = 10 월 7 일 21:22 KST, 00_date.txt 의 07:00:35+00:00 = 10 월 8 일 16:00:35 KST).", size=9)
for f in sorted(ENV_B.glob("*.txt")):
    R.h(f"C. {f.name}", 2)
    R.code(read(f), max_lines=160)
R.page_break()
R.h("부록 D. 회차별 원자료")
for ds in [d for d in (PRI, SUP, SEQ, RBS) if d]:
    if not ds["runs"]:
        continue
    rows = []
    for r in ds["runs"]:
        rows.append([r["variant"], r["map"].upper(), r["bs"].upper(), str(int(r["rep"])), fnum(r["bw_MiBps"]), fnum(r["iops"], 0),
                     fnum(r["clat_mean_us"]), fnum(r["clat_p99_us"], 0), fnum(r.get("gc_onset_s"), 2), fnum(r.get("waf_total"), 2),
                     fnum(r.get("chmodel_msgs", 0), 0)])
    R.table(["변형", "매핑", "bs", "회", "MiB/s", "IOPS", "clat\n평균 µs", "clat\np99 µs", "첫 GC s", "WAF\ntotal", "채널모델\n오류 줄"], rows,
            widths=[3.0, 1.0, 1.0, 0.6, 1.6, 1.8, 1.5, 1.6, 1.3, 1.3, 2.3], size=6.5,
            caption=f"회차별 결과 — {ds['name']} (analysis/summary_runs.csv)", align_right_from=3)
audit = read(EXPD / "report" / "audit_summary_ko.txt")
if audit:
    R.page_break()
    R.h("부록 E. NVMeVirt 코드 감사 요약")
    R.p("실험 전에 에이전트 여러 개로 NVMeVirt 코드를 독립적으로 읽고(쓰기 경로·쓰기 버퍼 / 초기화·기하 구조 / GC·타이밍), "
        "중요 주장마다 반박 시도 2 개(코드 경로 추적, 수치 예시 대조)로 검증했다. 결과 요약:", size=9.5)
    R.code(audit)
import datetime as _dt  # noqa: E402
_cp = R.doc.core_properties
_cp.created = _cp.modified = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)   # stored as UTC (W3CDTF); Word shows local time
_cp.title = "NVMeVirt FTL 매핑 단위 실험 기록서"
_cp.author = _cp.last_modified_by = "Sangwon8799 / Claude Code"
_cp.comments = ""
R.save(OUT)
print(f"wrote {OUT}")
