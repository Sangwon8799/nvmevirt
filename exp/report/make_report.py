#!/usr/bin/env python3
"""Build the KSC2026 NVMeVirt mapping-unit experiment record (.docx, Korean).

usage:  python3 exp/report/make_report.py exp/results/<EXP_NAME> [out.docx]

Everything is read from the repository: scripts (appendix), NVMeVirt diff, environment snapshots,
per-run results (exp/results/<EXP>/<variant>/...), analysis CSV/figures (exp/results/<EXP>/analysis/),
and the hand-written interpretation in exp/report/findings_ko.txt.
"""
import csv
import difflib
import json
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


def fnum(v, nd=1):
    if v is None or v == "" or v != v:
        return "–"
    if abs(v) >= 1000 and nd <= 1:
        return f"{v:,.0f}"
    return f"{v:,.{nd}f}"


# ---------------------------------------------------------------------------- inputs
EXP_DIR = Path(sys.argv[1]).resolve()
REPO = EXP_DIR.parents[2]
EXPD = REPO / "exp"
EXP = EXP_DIR.name
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else EXPD / "report" / "KSC2026_NVMeVirt_매핑단위_실험기록.docx"
AN = EXP_DIR / "analysis"
AGG = load_csv(AN / "summary_agg.csv")
RUNS = load_csv(AN / "summary_runs.csv")
ENV_B = EXP_DIR / "env_before"
FINDINGS = [ln.strip() for ln in read(EXPD / "report" / "findings_ko.txt").splitlines() if ln.strip() and not ln.startswith("#")]


def agg(variant, mp, bs):
    for a in AGG:
        if a["variant"] == variant and a["map"] == mp and a["bs"] == bs:
            return a
    return None


def matrix_rows(variant, metric, nd=1, with_std=True, mask_fn=None):
    rows = []
    for mp in SIZES:
        row = [f"{mp.upper()}"]
        for bs in SIZES:
            a = agg(variant, mp, bs)
            if a is None or f"{metric}_mean" not in a or a[f"{metric}_mean"] in ("", None):
                row.append("–")
                continue
            m = a[f"{metric}_mean"]
            s = a.get(f"{metric}_std", 0.0) or 0.0
            cell = f"{fnum(m, nd)}" + (f"\n±{fnum(s, nd)}" if with_std else "")
            if mask_fn and mask_fn(mp, bs):
                cell += " *"
            row.append(cell)
        rows.append(row)
    return rows


def run_window(variant):
    log = read(EXP_DIR / variant / "run.log")
    ts = re.findall(r"^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]", log, re.M)
    return (ts[0], ts[-1]) if ts else ("–", "–")


def dmesg_geometry():
    out = {}
    for mp in SIZES:
        txt = ""
        for v in VARIANTS:
            for bs in SIZES:
                txt = read(EXP_DIR / v / f"map{mp}_bs{bs}_r1" / "dmesg_load.txt")
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
HEAD = read(EXP_DIR / "base" / "git_head.txt").strip() or git("rev-parse", "HEAD")
n_runs = {v: sum(1 for r in RUNS if r["variant"] == v) for v in VARIANTS}

R.title("NVMeVirt FTL 매핑 단위 실험 기록서", "KSC 2026 · 매핑 단위(4–128 KiB) × fio 랜덤 쓰기 크기(4–128 KiB)")
R.table(["항목", "내용"], [
    ["실험 ID", EXP],
    ["작성일", "2026-10-08"],
    ["실험 수행", "Sangwon8799 (실험 서버 dccearth), 스크립트 작성·실행·기록: Claude Code (Claude Opus 5.5)"],
    ["저장소", "github.com/Sangwon8799/nvmevirt (main)\n로컬: /home/dccearth/jsw/KSC2026/nvmevirt"],
    ["실험 시 소스 커밋", HEAD],
    ["NVMeVirt 원본", f"github.com/snu-csl/nvmevirt @ {UPSTREAM[:7]} (2026-05-21)"],
    ["실행 횟수", f"base {n_runs['base']}회 + wbuffix {n_runs['wbuffix']}회 (각 60 초)"],
], widths=[3.5, 13.5], size=9)
R.p("이 문서는 실험 시작부터 결과를 얻기까지의 전 과정을 기록한다. 다른 사람이 같은 서버 구성에서 문서만 보고 같은 실험을 다시 할 수 있도록 "
    "환경·버전·바꾼 설정값·사용한 스크립트 전문·실행 순서·결과를 모두 적었다.", size=9.5)
R.toc()
R.page_break()

# ============================================================================ 1
R.h("1. 실험 개요")
R.h("1.1 목적", 2)
R.p("고용량 SSD 는 4 KiB 매핑을 유지하면 L2P(논리→물리) 매핑 표가 용량의 약 0.1 % 만큼 DRAM 을 차지한다(1 TB 에 약 1 GB). "
    "매핑 단위를 16 KiB 이상으로 키우면 DRAM 은 줄지만, 매핑 단위보다 작은 쓰기는 매핑 단위 전체를 새로 써야 하므로 성능이 떨어질 수 있다. "
    "이 실험은 NVMeVirt(커널 모듈 기반 NVMe SSD 에뮬레이터)의 conventional SSD 모델에서 FTL 매핑 단위를 4·8·16·32·64·128 KiB 로 바꾸고, "
    "fio 랜덤 쓰기 블록 크기 4–128 KiB 각각에 대해 대역폭(BW), IOPS, 완료 지연(clat)을 잰다. "
    "연구 계획(연구 계획 흐름.docx)의 「(4k mapping ssd) randwrite 4k–128k → BW, clat / (16k/32k mapping ssd) …」 를 매핑 단위 6개로 넓힌 것이다.")
R.h("1.2 실험 행렬과 고정 조건", 2)
R.table(["구분", "값"], [
    ["변수 ① FTL 매핑 단위", "4K, 8K, 16K, 32K, 64K, 128K (모듈을 매핑 단위별로 따로 빌드)"],
    ["변수 ② fio 블록 크기(bs)", "4K, 8K, 16K, 32K, 64K, 128K"],
    ["반복", "조합마다 3 회 (회차마다 rmmod → insmod 로 장치 초기화)"],
    ["모델 변형", "base: 요청한 설정 그대로 / wbuffix: base + 쓰기 버퍼 계산 수정(5.4 절) — 각각 6 × 6 × 3 = 108 회"],
    ["NVMeVirt 모드", "Conventional SSD (SAMSUNG_970PRO 묶음)"],
    ["저장 용량", "예약 메모리 12 GiB (물리 주소 12–24 GiB), 호스트에 보이는 용량 11.21 GiB (OP 7 %)"],
    ["블록 크기", "2 MiB (BLKS_PER_PLN = 384)"],
    ["NVMeVirt CPU", "3 개: cpu3 = 디스패처, cpu4·cpu5 = I/O 워커 (isolcpus=3-5)"],
    ["fio", "ioengine=libaio, direct=1, rw=randwrite, iodepth=32, numjobs=1, runtime=60 s, ramp_time=0, 장치 전체"],
    ["측정값", "60 s 평균 BW·IOPS·clat(평균, p50, p99, p99.9), 0.5 s 간격 시계열(BW·IOPS·지연), 첫 GC 시각, 쓰기 증폭(WAF)"],
], widths=[4.5, 12.5], size=9, caption="실험 행렬과 고정 조건")
if FINDINGS:
    R.h("1.3 결과 요약", 2)
    R.bullets(FINDINGS[:8])

# ============================================================================ 2
R.h("2. 실험 환경")
R.h("2.1 하드웨어", 2)
dimm = read(ENV_B / "12_dimm.txt")
dimms = re.findall(r"Size: (\d+ GB)\nLocator: (\S+)\nType: (\S+)\nSpeed: ([^\n]+)\nManufacturer: (\S+)\nPart Number: (\S+)", dimm)
dimm_txt = "\n".join(f"{loc}: {sz} {ty}-{sp.split()[0]} {mf} {pn}" for sz, loc, ty, sp, mf, pn in dimms) or "–"
R.table(["항목", "값"], [
    ["서버(호스트명)", env_line("00_date.txt", r"^\$ hostname\n(.*)$")],
    ["메인보드", env_line("06_platform.txt", r"board_vendor:(.*)$") + " " + env_line("06_platform.txt", r"board_name:(.*)$")],
    ["BIOS", env_line("06_platform.txt", r"bios_version:(.*)$") + " (" + env_line("06_platform.txt", r"bios_date:(.*)$") + ")"],
    ["CPU", env_line("03_cpu.txt", r"^Model name:\s+(.*)$") + f"\nOS 에 보이는 CPU {env_line('03_cpu.txt', r'^CPU\(s\):\s+(\d+)')}개 "
     f"(코어당 스레드 {env_line('03_cpu.txt', r'^Thread\(s\) per core:\s+(\d+)')}), 최대 {env_line('03_cpu.txt', r'^CPU max MHz:\s+([\d.]+)')} MHz, "
     f"L3 {env_line('03_cpu.txt', r'^L3 cache:\s+(.*)$')}"],
    ["메모리", f"총 24 GB (DDR5)\n{dimm_txt}"],
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
     "e820 user map: [mem 0x0000000300000000-0x00000005ffffffff] reserved"],
    ["CPU 주파수", f"intel_pstate {env_line('04_cpufreq.txt', r'^(active|passive)')}, governor powersave, EPP balance_performance, "
     f"터보 켜짐(no_turbo={env_line('04_cpufreq.txt', r'^(?:active|passive)\n(\d)')}), 800–5100 MHz (모두 기본값, 바꾸지 않음)"],
    ["THP", env_line("05_memory.txt", r"^(always.*|.*\[madvise\].*)$")],
    ["콘솔 로그 레벨", "kernel.printk = 4 4 1 7 (기본값) — KERN_ERR 메시지는 tty0 콘솔에도 출력됨 (5.5 절 참고)"],
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
     "CONFIG_NVMEV_IO_WORKER_BY_SQ 로 큐 번호에 따라 워커를 고르므로 워커 0 만 쓰인다. /proc/irq/15/effective_affinity_list = 5, irqbalance 꺼짐"],
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
sudo apt install fio                    # fio 3.36 (Ubuntu 24.04 패키지)""")
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
    ["exp/analyze.py", "결과 집계(CSV)와 그림"],
    ["exp/run_all.sh", "빌드 → base 108 회 → wbuffix 108 회 → 분석을 한 번에"],
    ["exp/report/", "이 문서를 만드는 스크립트 (make_report.py, docx_helpers.py, findings_ko.txt)"],
    [f"exp/results/{EXP}/", "본 실험 결과 (변형/회차별 폴더, env_before·env_after, analysis/)"],
    ["exp/results/pre_*/", "사전 점검 결과 (스모크 테스트, GC_STATS 영향 확인)"],
], widths=[5.0, 12.0], size=8.5, caption="저장소 구성")
R.h("3.3 실행 권한 (sudoers)", 2)
R.p("insmod·rmmod·블록 장치에 대한 fio·dmesg 는 root 권한이 필요하다. 실험을 무인으로 돌리기 위해 필요한 명령만 비밀번호 없이 쓰도록 규칙을 추가했다. "
    "/dev/kmsg 쓰기는 회차의 시작·끝 표지를 커널 로그에 남겨 NVMeVirt 메시지와 같은 시계로 시간을 재기 위해 쓴다.")
R.code(read(EXPD / "report" / "nvmevirt-exp.sudoers") or "(sudoers 파일 사본 없음)")
R.code("""# 설치 (문법 검사 후 설치)
sudo visudo -cf nvmevirt-exp.sudoers && sudo install -m 0440 -o root -g root nvmevirt-exp.sudoers /etc/sudoers.d/nvmevirt-exp
# 실험 후 제거
sudo rm /etc/sudoers.d/nvmevirt-exp""")
R.h("3.4 NVMeVirt 소스 수정 사항", 2)
R.p("원본(61c90f7) 대비 바꾼 것은 아래가 전부다. 전체 diff 는 부록 B 에 있다.")
R.table(["파일", "항목", "원본 값", "실험 값", "이유"], [
    ["Kbuild", "빌드 대상", "CONFIG_NVMEVIRT_NVM (Optane)", "CONFIG_NVMEVIRT_SSD\n(BASE_SSD=SAMSUNG_970PRO)", "conventional SSD(FTL·GC 모델) 사용"],
    ["Kbuild", "MAPPING_UNIT", "없음", "make 변수 (기본 4096)", "매핑 단위별 모듈을 한 소스에서 빌드"],
    ["ssd.c:73", "secs_per_pg", "4096 / LBA_SIZE", "MAPPING_UNIT / LBA_SIZE", "FTL 매핑 단위(= FTL page) 변경"],
    ["ssd_config.h", "BLKS_PER_PLN", "8192", "384", "블록 2 MiB: 12 GiB ÷ 4 파티션 ÷ (2 ch × 2 LUN × 1 plane) ÷ 384"],
    ["ssd_config.h", "FLASH_PAGE_SIZE", "KB(32)", "32 KiB (매핑 ≤ 32K)\n= 매핑 단위 (64K, 128K)", "FLASH_PAGE_SIZE % pgsz == 0 assert 통과"],
    ["ssd.c", "적재 로그", "–", "'KSC2026: mapping unit=…' 1 줄", "회차마다 매핑 단위 적용 확인"],
    ["conv_ftl.c/.h", "GC_STATS (선택)", "–", "base·wbuffix 모두 켬", "첫 GC 시각, 호스트/GC 페이지 수 기록 (관찰만, 영향 없음 — 5.3 절)"],
    ["conv_ftl.c", "WBUF_FIX (선택)", "–", "wbuffix 만 켬", "쓰기 버퍼 과다 반환 수정 (5.4 절)"],
], widths=[2.2, 2.6, 3.2, 3.8, 5.2], size=8, caption="NVMeVirt 수정 사항")
R.p("빌드 명령 (매핑 단위 하나):")
R.code("""cd nvmevirt
make clean
make MAPPING_UNIT=16384 GC_STATS=1              # base 변형
make MAPPING_UNIT=16384 GC_STATS=1 WBUF_FIX=1   # wbuffix 변형
# exp/build_modules.sh <변형> 이 6 개 매핑 단위를 차례로 빌드해 exp/modules/<변형>/ 에 보관한다""")
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
    ["매핑 단위", "4 → 8·16·32 KiB", "4·8·16·32·64·128 KiB", "64K·128K 는 flash page 도 같이 키움 (사용자 지정)"],
    ["fio 시간", "사전 채움 후 300 s", "포맷 직후 60 s, ramp_time 0, 3 회", "GC 이전 구간까지 함께 측정 (사용자 지정)"],
    ["fio 나머지", "libaio · randwrite · bs 4k–128k · QD 32 · jobs 1", "같음", "–"],
], widths=[3.0, 4.3, 4.7, 5.0], size=8, caption="설정조사 보고서 추천값과의 차이")
R.h("3.8 모듈 적재 파라미터", 2)
R.code("sudo insmod exp/modules/<변형>/nvmev_map<단위>.ko memmap_start=12G memmap_size=12G cpus=3,4,5")
R.p("memmap_start/size 는 GRUB 의 memmap=12G$12G 와 같은 영역이다. NVMeVirt 는 앞 1 MiB 를 큐 등에 쓰고 나머지 12,287 MiB 를 저장 공간으로 쓴다"
    "(dmesg 'Storage: 0x300100000-0x600000000 (12287 MiB)'). cpus 의 첫 값이 디스패처, 나머지가 I/O 워커다.", size=9)
R.h("3.9 fio 작업 파일", 2)
R.p("틀(exp/jobs/randwrite.fio.in)의 @값@ 을 회차마다 채워 회차 폴더에 job.fio 로 저장한다. 아래는 틀과 실제 예(매핑 4K, bs 4K, 1 회차)이다.")
R.code(read(EXPD / "jobs" / "randwrite.fio.in"))
R.code(read(EXP_DIR / "base" / "map4k_bs4k_r1" / "job.fio") or "(job.fio 없음)")
R.bullets([
    "filename 은 회차마다 모델명 CSL_Virt 로 찾은 장치다. 크기(11–12 GiB)·파티션 없음·마운트 안 됨·루트 디스크 아님을 확인한 뒤에만 쓴다.",
    "size 를 주지 않아 장치 전체(12,040,984,064 B)에 랜덤 쓰기를 한다. randrepeat=1(기본값)이라 회차·조합마다 같은 난수 순서를 쓴다.",
    "norandommap 은 기본값(0)이다: fio 가 한 바퀴 동안 같은 블록을 두 번 쓰지 않는다.",
    "write_bw_log/write_iops_log/write_lat_log 로 0.5 s 평균 시계열을 남긴다(fio_bw.1.log 등, 단위 KiB/s · IOPS · ns).",
])

# ============================================================================ 4
R.h("4. 실험 절차")
R.h("4.1 회차 하나의 절차", 2)
R.numbered([
    "nvmev 모듈이 올라와 있으면 rmmod 로 내린다(이전 FTL 상태 제거).",
    "커널 로그를 끝까지 따라가며 기록하는 'sudo dmesg -W' 를 회차 폴더의 kernel.log 로 시작한다(채널 모델 오류 줄은 개수만 센다 — 5.4 절).",
    "커널 로그에 'KSC2026-MARK <회차> insmod' 표지를 남기고 insmod 한다(memmap_start=12G memmap_size=12G cpus=3,4,5).",
    "모델명 CSL_Virt_MN_01 인 블록 장치가 생길 때까지 기다리고, 적재 로그의 'KSC2026: mapping unit=<바이트> B' 로 매핑 단위가 맞는지 확인한다. 틀리면 실험을 멈춘다.",
    "장치 크기·파티션·마운트·루트 디스크 여부를 확인하고 job.fio 와 meta.txt 를 만든다.",
    "5 초 쉰 뒤 'fio-start' 표지를 남기고 fio 를 60 초 실행한다(JSON 결과 + 0.5 초 시계열).",
    "'fio-end', 'rmmod' 표지를 남기고 rmmod 한다 — 이때 GC 통계(파티션별 호스트/GC 페이지 수)가 로그에 찍힌다.",
    "커널 로그를 run 구간(dmesg_run.txt)과 rmmod 구간(dmesg_unload.txt)으로 나누고, 결과 파일 소유자를 사용자로 바꾼다.",
    "fio 종료 코드와 JSON 의 error 필드가 모두 0 이면 DONE 표지를, 아니면 FAILED 표지(원인 커널 줄 포함)를 만들고 다음 회차로 넘어간다. DONE·FAILED 회차는 다시 실행할 때 건너뛴다. "
    "fio 는 감시 타이머(60 s + 180 s 에 SIGTERM, 다시 60 s 뒤 SIGKILL) 아래에서 실행한다.",
])
R.h("4.2 실행 순서와 시간", 2)
wb, we = run_window("base")
fb, fe = run_window("wbuffix")
R.table(["변형", "회차 수", "순서", "시작", "끝"], [
    ["base", str(n_runs["base"]), "반복 1→3 바깥, 그 안에서 매핑 4K→128K, 그 안에서 bs 4K→128K", wb, we],
    ["wbuffix", str(n_runs["wbuffix"]), "같음", fb, fe],
], widths=[2.0, 1.6, 7.4, 3.0, 3.0], size=8.5, caption="실행 순서와 시각 (UTC)")
R.p("반복을 바깥 루프에 둬서 시간에 따른 서버 상태 변화가 특정 조합에 몰리지 않게 했다. 회차 하나는 적재·대기·측정·내림을 합쳐 약 70 초 걸린다.")
R.p("실제 실행 경과: run_all.sh(빌드 → base → wbuffix)로 05:20:28 에 시작했으나 base 21 번째 회차(매핑 32K·bs 16K)에서 가상 장치가 멈춰(5.6 절) "
    "당시 스크립트(커밋 5769378)가 실험을 중단했다(05:46:57). 실패 회차를 FAILED 로 남기고 계속하도록 스크립트를 고친 뒤(커밋 2a462a3) 05:49:13 에 "
    "wbuffix 108 회를 먼저, 이어서 base 의 나머지 회차를 실행했다. 모듈은 다시 빌드하지 않아 base 의 앞 20 회와 뒤 회차는 같은 바이너리다(SHA-256 확인). "
    "base 의 회차별 스크립트 커밋은 meta.txt 의 git_head(2a462a3 이후)와 base/git_head.txt 에 있다.", size=9.5)
R.h("4.3 재현 명령", 2)
R.code(f"""git clone git@github.com:Sangwon8799/nvmevirt.git && cd nvmevirt
git checkout {HEAD[:7]}
cd exp
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
# (3.3 절 sudoers 설치, 3.1 절 GRUB 설정이 되어 있어야 한다)
tmux new -s ksc2026 'bash run_all.sh {EXP}'      # 빌드 → base 108 회 → wbuffix 108 회 → 분석 (약 4.3 시간)
# 일부만: REPS=1 MAPS="4k 16k" BSS="4k" bash run_experiment.sh test base
./.venv/bin/python report/make_report.py results/{EXP}   # 이 문서 생성""")
R.h("4.4 결과 파일", 2)
R.table(["파일 (회차 폴더 map<단위>_bs<크기>_r<회>/)", "내용"], [
    ["fio.json", "fio 결과 (JSON) — BW, IOPS, clat/slat/lat 통계, 백분위수"],
    ["fio_bw.1.log / fio_iops.1.log / fio_lat.1.log / fio_clat.1.log / fio_slat.1.log", "0.5 s 평균 시계열 (ms, 값, 방향, bs, offset)"],
    ["job.fio", "그 회차에 실제로 쓴 fio 작업 파일"],
    ["meta.txt", "변형·단위·bs·회차, 장치, 모듈 SHA-256, insmod 인자, 시작/끝, fio 종료 코드, 채널 모델 오류 수, 커널 경고 수"],
    ["dmesg_load.txt", "insmod 직후 커널 로그 (NVMeVirt 구성·파라미터)"],
    ["dmesg_run.txt", "fio 실행 중 커널 로그 (첫 GC 줄 포함, 채널 모델 오류 줄 제외)"],
    ["dmesg_unload.txt", "rmmod 시 커널 로그 (파티션별 GC 통계)"],
    ["kernel.log / chmodel_msgs.txt", "회차 전체 커널 로그 (채널 모델 오류는 처음 20 줄만) / 그 오류 줄 수"],
], widths=[7.0, 10.0], size=8, caption="회차 폴더의 파일")
R.h("4.5 지표 정의", 2)
R.bullets([
    [("BW, IOPS", "b"), ": fio JSON 의 60 s 평균 (bw 는 KiB/s → MiB/s)."],
    [("clat", "b"), ": 제출 후 완료까지 지연 (fio clat_ns). 평균과 p50/p99/p99.9."],
    [("첫 10 s / 마지막 20 s BW", "b"), ": 0.5 s 시계열에서 0–10 s, 40–60 s 구간 평균."],
    [("GC 시작 시각", "b"), ": 커널 로그의 'fio-start' 표지부터 첫 'KSC2026: first GC' 줄까지의 시간 (4 개 파티션 중 가장 이른 것)."],
    [("GC 전/후 BW", "b"), ": GC 시작 시각 이전/이후 시계열 구간의 평균."],
    [("WAF_GC", "b"), ": (호스트 페이지 쓰기 + GC 페이지 복사) ÷ 호스트 페이지 쓰기 — 매핑 단위 페이지 기준."],
    [("WAF_total", "b"), ": (호스트 + GC 페이지) × 매핑 단위 ÷ fio 가 쓴 바이트 — 매핑 단위보다 작은 쓰기의 증폭(매핑 단위/bs)까지 포함."],
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
                smoke.append([v, mp.upper(), bs.upper(), f"{w['bw'] / 1024:.1f}", f"{w['iops']:,.0f}", f"{w['clat_ns']['mean'] / 1e3:.1f}", cm.group(1) if cm else "–"])
if smoke:
    R.table(["변형", "매핑", "bs", "MiB/s", "IOPS", "clat 평균 µs", "채널 모델 오류"], smoke,
            widths=[2.2, 1.6, 1.6, 2.2, 2.6, 2.6, 3.2], size=8.5, caption="스모크 테스트 (각 10 s, 1 회)", align_right_from=3)
else:
    R.p("스모크 테스트(매핑 4K·128K × bs 4K·128K, 10 s)로 회차 절차·결과 파일·커널 로그 수집을 점검했다.")
R.p("10 초짜리 짧은 실행으로 회차 절차가 끝까지 도는지 확인했다. 이 과정에서 두 가지를 고쳤다: "
    "(1) dmesg 시각과 /proc/uptime 의 차이 때문에 시각으로 로그를 자르던 방법이 실패해 커널 로그 표지(/dev/kmsg) 방식으로 바꿨고, "
    "(2) base 의 매핑 128K·bs 4K 에서 NVMeVirt 가 10 초에 약 170 만 줄의 '[chmodel_request] Need to increase array size' 오류를 찍어 "
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
            caption="GC_STATS 계측 유무 비교 (매핑 4K, bs 4K, 20 s)", align_right_from=2)
R.p("GC 통계(첫 GC 시각, 호스트/GC 페이지 수)를 남기는 계측은 디스패처 스레드에서 정수 증가 몇 번과 첫 GC 때 printk 1 줄만 더한다. "
    "요청 수가 가장 많아 디스패처의 요청당 작업이 결과에 가장 잘 드러나는 4K/4K 에서 계측을 끈 빌드와 켠 빌드를 20 초씩 3 회 비교해 차이가 반복 간 편차(약 0.3 %) 안에 있음을 확인한 뒤 본 실험의 두 변형 모두에 켰다.")
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
    "코드 감사 에이전트 두 개가 독립적으로 같은 결론을 냈고(부록 E), 서로 다른 방식의 검증 에이전트가 이를 확인했다.",
])
R.p("수정(WBUF_FIX=1, wbuffix 변형): 할당량을 실제로 프로그램될 매핑 단위 페이지 수에 맞춘다. PCIe·펌웨어 전송 시간 계산에는 원래대로 요청 크기를 쓴다. "
    "bs ≥ 매핑 단위인 조합에서는 할당량이 원본과 같아서 결과가 바뀌지 않는다(실측으로도 확인 — 6.3 절).")
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
     "60 s 평균에 이 주기가 섞인다. 시계열(6.4 절)을 함께 봐야 한다. GC 구간은 정상 상태가 아니다."],
    ["GC 시작 시각 차이", "포맷 직후 60 s 라 조합마다 GC 이전 구간 비율이 다르다.", "60 s 평균과 함께 GC 전/후 BW, 시계열을 같이 본다."],
    ["randrepeat=1", "모든 회차가 같은 난수 순서를 쓴다.", "3 회 반복은 에뮬레이터 타이밍 편차만 담는다."],
], widths=[3.2, 7.6, 6.2], size=8, caption="해석 시 주의할 모델 특성")

R.h("5.6 발견 2 — base 에서 가상 장치가 멈추는 조합", 2)
FAILED_RUNS = load_csv(AN / "failed_runs.csv")
R.p("요청 설정 그대로인 base 의 bs < 매핑 단위 조합에서는 쓰기 버퍼가 호스트를 붙잡지 못해 NAND 작업 대기열이 계속 늘어난다. NVMeVirt 의 I/O 워커 작업 큐"
    "(워커당 16,384 항목)가 차면 io.c:302 의 WARN_ON_ONCE('IO queue is almost full')가 찍히고 이후 명령이 처리되지 않아, 리눅스 nvme 드라이버의 "
    "I/O 시간 초과(30 s) → 중단(abort) → 컨트롤러 리셋 → 장치 비활성화 → I/O 오류로 이어진다. 그런 회차는 FAILED 로 표시해 평균에서 빼고 아래에 따로 적었다. "
    "rmmod 는 매번 정상 처리되었고 다음 회차의 insmod 도 정상이었다.")
if FAILED_RUNS:
    R.table(["변형", "매핑", "bs", "회", "fio\n종료", "fio\n오류", "실행\n시간 s", "큐 포화\n경고 s", "nvme\n시간초과 s", "리셋 s", "비활성 s", "채널모델\n오류 줄"],
            [[r["variant"], r["map"].upper(), r["bs"].upper(), str(int(r["rep"])), str(r.get("fio_exit", "")), str(r.get("fio_json_error", "")),
              fnum(r.get("runtime_s"), 1), fnum(r.get("t_queue_full_warn_s"), 1), fnum(r.get("t_nvme_timeout_s"), 1), fnum(r.get("t_reset_s"), 1),
              fnum(r.get("t_disable_s"), 1), fnum(r.get("chmodel_msgs"), 0)] for r in FAILED_RUNS],
            widths=[1.4, 1.1, 1.1, 0.7, 1.1, 1.1, 1.4, 1.5, 1.6, 1.3, 1.4, 2.2], size=7, caption="실패(FAILED) 회차 — 시각은 fio 시작 기준", align_right_from=3)
else:
    R.p("(failed_runs.csv 없음)")
R.code("""# base map32k_bs16k_r1 의 kernel.log (fio-start = 62505.554)
[62511.194665] NVMeVirt: KSC2026: first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280      (+5.6 s)
[62530.521783] WARNING: CPU: 3 PID: 30089 at …/nvmevirt/io.c:302 __allocate_work_queue_entry+0x8a/0xb0 [nvmev]  (+25.0 s)
[62560.640166] nvme nvme1: I/O tag 192 (80c0) opcode 0x1 (I/O Cmd) QID 1 timeout, aborting req_op:WRITE(1) size:16384  (+55.1 s)
[62590.847614] nvme nvme1: I/O tag 192 (80c0) opcode 0x1 (I/O Cmd) QID 1 timeout, reset controller                    (+85.3 s)
[62652.289426] nvme nvme1: I/O tag 28 (301c) QID 0 timeout, disable controller                                        (+146.7 s)
[62652.306429] nvme nvme1: Disabling device after reset failure: -5
[62652.313386] I/O error, dev nvme1n1, sector 6011360 op 0x1:(WRITE) flags 0x8800 phys_seg 1 prio class 2
fio: io_u error on file /dev/nvme1n1: Input/output error: write offset=…, buflen=16384   → fio error 5 (EIO), 146.5 s""")

# ============================================================================ 6
R.h("6. 결과")
if not AGG:
    R.note("분석 결과(analysis/summary_agg.csv)가 아직 없다.")
else:
    lt = lambda mp, bs: kib(bs) < kib(mp)  # noqa: E731
    for vi, v in enumerate(VARIANTS):
        R.h(f"6.{vi + 1} {VNAME[v]}", 2)
        if v == "base":
            R.p("표의 * 는 bs < 매핑 단위인 조합이다. base 에서 이 조합은 5.4 절의 문제로 타이밍 모델이 정상 범위를 벗어난 상태에서 잰 값이므로 "
                "wbuffix 결과와 함께 봐야 한다.", size=9)
        else:
            R.p("쓰기 버퍼 계산을 고친 변형이다. bs ≥ 매핑 단위인 조합은 base 와 같은 코드 경로이므로 두 변형의 차이는 반복 간 편차 수준이어야 한다.", size=9)
        hdr = ["매핑 \\ bs"] + [s.upper() for s in SIZES]
        W = [2.2] + [2.45] * 6
        mask = lt if v == "base" else None
        R.table(hdr, matrix_rows(v, "bw_MiBps", 1, True, mask), widths=W, size=8, caption=f"쓰기 대역폭 MiB/s, 60 s 평균 ± 표준편차 (n=3) — {v}", align_right_from=1, bold_first_col=True)
        R.table(hdr, matrix_rows(v, "iops", 1, False, mask), widths=W, size=8, caption=f"IOPS, 60 s 평균 (n=3 평균) — {v}", align_right_from=1, bold_first_col=True)
        R.table(hdr, matrix_rows(v, "clat_mean_us", 1, False, mask), widths=W, size=8, caption=f"평균 완료 지연 µs (n=3 평균) — {v}", align_right_from=1, bold_first_col=True)
        R.table(hdr, matrix_rows(v, "clat_p99_us", 0, False, mask), widths=W, size=8, caption=f"p99 완료 지연 µs (n=3 평균) — {v}", align_right_from=1, bold_first_col=True)
        R.table(hdr, matrix_rows(v, "gc_onset_s", 2, True, mask), widths=W, size=8, caption=f"첫 GC 시각 s (fio 시작 기준, 평균 ± 표준편차) — {v}", align_right_from=1, bold_first_col=True)
        R.table(hdr, matrix_rows(v, "bw_pre_gc_MiBps", 1, False, mask), widths=W, size=8, caption=f"GC 이전 구간 평균 대역폭 MiB/s — {v}", align_right_from=1, bold_first_col=True)
        R.table(hdr, matrix_rows(v, "bw_post_gc_MiBps", 1, False, mask), widths=W, size=8, caption=f"GC 이후 구간 평균 대역폭 MiB/s — {v}", align_right_from=1, bold_first_col=True)
        R.table(hdr, matrix_rows(v, "waf_total", 2, False, mask), widths=W, size=8, caption=f"전체 쓰기 증폭 WAF_total (NAND 바이트 ÷ 호스트 바이트) — {v}", align_right_from=1, bold_first_col=True)
        for fig, cap in ((f"fig_bw_vs_bs_{v}.png", f"bs 에 따른 쓰기 대역폭 (매핑 단위별, 평균 ± 표준편차) — {v}"),
                         (f"fig_bw_heatmap_{v}.png", f"매핑 단위 × bs 평균 대역폭 — {v}"),
                         (f"fig_clat_mean_vs_bs_{v}.png", f"평균 완료 지연 (로그 축) — {v}"),
                         (f"fig_clat_p99_vs_bs_{v}.png", f"p99 완료 지연 (로그 축) — {v}"),
                         (f"fig_waf_heatmap_{v}.png", f"전체 쓰기 증폭 — {v}")):
            if (AN / fig).exists():
                R.figure(AN / fig, cap, 15.5)
    R.h("6.3 base 와 wbuffix 비교", 2)
    rows = []
    for mp in SIZES:
        for bs in SIZES:
            a, b = agg("base", mp, bs), agg("wbuffix", mp, bs)
            if not a or not b:
                continue
            d = (b["bw_MiBps_mean"] - a["bw_MiBps_mean"]) / a["bw_MiBps_mean"] * 100 if a["bw_MiBps_mean"] else float("nan")
            rows.append([mp.upper(), bs.upper(), "예" if lt(mp, bs) else "", fnum(a["bw_MiBps_mean"]), fnum(b["bw_MiBps_mean"]), f"{d:+.1f} %",
                         fnum(a.get("chmodel_msgs_mean", 0), 0), fnum(b.get("chmodel_msgs_mean", 0), 0)])
    R.table(["매핑", "bs", "bs<매핑", "base MiB/s", "wbuffix MiB/s", "차이", "base 채널모델\n오류 줄(평균)", "wbuffix\n오류 줄"], rows,
            widths=[1.5, 1.5, 1.5, 2.3, 2.5, 1.8, 3.0, 2.4], size=7.5, caption="변형 간 평균 대역폭 비교", align_right_from=3)
    if (AN / "fig_variant_compare.png").exists():
        R.figure(AN / "fig_variant_compare.png", "bs < 매핑 단위 조합의 base / wbuffix 대역폭", 16.5)
    R.h("6.4 시간에 따른 대역폭", 2)
    R.p("각 칸은 (매핑 단위, bs) 조합 하나이며 3 회차를 겹쳐 그렸다. 점선은 그 회차의 첫 GC 시각이다.", size=9)
    for v in VARIANTS:
        if (AN / f"fig_timeseries_{v}.png").exists():
            R.figure(AN / f"fig_timeseries_{v}.png", f"0.5 s 평균 쓰기 대역폭 시계열 — {v}", 17.0)
    R.h("6.5 반복 간 편차", 2)
    cvs = []
    for v in VARIANTS:
        vals = [a["bw_MiBps_std"] / a["bw_MiBps_mean"] * 100 for a in AGG if a["variant"] == v and a["bw_MiBps_mean"]]
        if vals:
            worst = max((a for a in AGG if a["variant"] == v and a["bw_MiBps_mean"]), key=lambda a: a["bw_MiBps_std"] / a["bw_MiBps_mean"])
            cvs.append([v, f"{sum(vals) / len(vals):.2f} %", f"{max(vals):.2f} %", f"{worst['map'].upper()} / {worst['bs'].upper()}"])
    R.table(["변형", "평균 변동계수(CV)", "최대 CV", "최대 CV 조합 (매핑/bs)"], cvs, widths=[3.0, 4.0, 3.0, 7.0], size=8.5, caption="대역폭의 반복 간 변동계수")
    if FINDINGS:
        R.h("6.6 관찰", 2)
        R.bullets(FINDINGS)

# ============================================================================ 7
R.h("7. 실험 후 상태와 정리")
after_dirs = sorted(p for p in EXP_DIR.iterdir() if p.name.startswith("env_after"))
diff_rows = []
for ad in after_dirs:
    for f in sorted(ENV_B.glob("*.txt")):
        if f.name in ("00_date.txt", "12_dimm.txt"):
            continue
        a_txt, b_txt = read(f), read(ad / f.name)
        ign = re.compile(r"loadavg|^\d+\.\d+ \d+\.\d+|Mem:|Swap:|MemFree|MemAvailable|AnonHugePages|^\$ |^[0-9.]+ [0-9.]+ [0-9.]+ \d+/\d+")
        al = [ln for ln in a_txt.splitlines() if not ign.search(ln)]
        bl = [ln for ln in b_txt.splitlines() if not ign.search(ln)]
        changed = [ln for ln in difflib.unified_diff(al, bl, lineterm="", n=0) if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
        if changed:
            diff_rows.append([ad.name, f.name, "\n".join(changed[:6]) + ("\n…" if len(changed) > 6 else "")])
R.p("실험 전(env_before)과 각 변형이 끝난 뒤(env_after_*) 환경 스냅샷을 비교했다. 날짜·부하·여유 메모리처럼 늘 바뀌는 값은 빼고 달라진 줄만 적었다.")
if diff_rows:
    R.table(["스냅샷", "파일", "달라진 줄 (- 전 / + 후)"], diff_rows, widths=[3.2, 3.3, 10.5], size=7.5, caption="실험 전후 환경 차이")
else:
    R.p("커널 명령줄·CPU 주파수 설정·버전·블록 장치·모듈 목록 모두 실험 전과 같았다.")
R.table(["항목", "실험 전", "실험 중", "실험 후"], [
    ["GRUB / 커널 명령줄", "memmap=12G$12G isolcpus=3-5", "변경 없음", "변경 없음"],
    ["nvmev 모듈", "적재 안 됨", "회차마다 적재·내림", "적재 안 됨 (마지막 rmmod)"],
    ["/dev/nvme1n1", "없음", "회차마다 생겼다 사라짐", "없음"],
    ["/etc/sudoers.d/nvmevirt-exp", "없음", "설치 (3.3 절)", "실험 후 제거 (7 절 끝 명령)"],
    ["CPU governor / 터보", "powersave / 켬", "변경 없음", "변경 없음"],
    ["NVMeVirt 소스", f"원본 {UPSTREAM[:7]}", f"{HEAD[:7]} (3.4 절)", "GitHub main 에 push"],
    ["예약 메모리 내용", "–", "rmmod/insmod 는 FTL 상태만 초기화 (저장 데이터는 지우지 않음)", "이전 회차 데이터가 남아 있음 (쓰기 전용 실험이라 무관)"],
], widths=[4.0, 3.6, 5.0, 4.4], size=8, caption="실험 전·중·후 설정 상태")
R.code("""# 실험 후 정리
lsmod | grep nvmev || echo "nvmev not loaded"
sudo rm /etc/sudoers.d/nvmevirt-exp
git -C /home/dccearth/jsw/KSC2026/nvmevirt status""")

# ============================================================================ appendices
R.page_break()
R.h("부록 A. 스크립트 전문")
for rel in ("exp/common.sh", "exp/build_modules.sh", "exp/run_experiment.sh", "exp/collect_env.sh", "exp/jobs/randwrite.fio.in",
            "exp/run_all.sh", "exp/analyze.py", "exp/requirements.txt", "exp/.gitignore"):
    R.h(f"A. {rel}", 2)
    R.code(read(REPO / rel))
R.p("이 문서를 만드는 exp/report/make_report.py · docx_helpers.py 는 저장소에 있다(분량상 생략).", size=9)
R.page_break()
R.h("부록 B. NVMeVirt 변경 diff 전문 (원본 61c90f7 대비)")
MOVE = git("log", "--format=%H", "--grep=^Move NVMeVirt sources into nvmevirt/", "-1", HEAD)
R.p(f"원본 {UPSTREAM[:7]} 의 파일을 그대로 nvmevirt/ 로 옮긴 커밋({MOVE[:7]}, 내용 변경 없음) 이후의 변경이다: git diff {MOVE[:7]} {HEAD[:7]} -- nvmevirt", size=9)
R.code(git("diff", MOVE, HEAD, "--", "nvmevirt"))
R.page_break()
R.h("부록 C. 실험 전 환경 스냅샷 (env_before)")
for f in sorted(ENV_B.glob("*.txt")):
    R.h(f"C. {f.name}", 2)
    R.code(read(f), max_lines=160)
R.page_break()
R.h("부록 D. 회차별 원자료")
if RUNS:
    rows = []
    for r in RUNS:
        rows.append([r["variant"], r["map"].upper(), r["bs"].upper(), str(int(r["rep"])), fnum(r["bw_MiBps"]), fnum(r["iops"], 0),
                     fnum(r["clat_mean_us"]), fnum(r["clat_p99_us"], 0), fnum(r.get("gc_onset_s"), 2), fnum(r.get("waf_total"), 2),
                     fnum(r.get("chmodel_msgs", 0), 0)])
    R.table(["변형", "매핑", "bs", "회", "MiB/s", "IOPS", "clat\n평균 µs", "clat\np99 µs", "첫 GC s", "WAF\ntotal", "채널모델\n오류 줄"], rows,
            widths=[1.6, 1.2, 1.2, 0.8, 1.7, 1.9, 1.6, 1.7, 1.5, 1.5, 2.3], size=7, caption="회차별 결과 (exp/results/…/analysis/summary_runs.csv)", align_right_from=3)
audit = read(EXPD / "report" / "audit_summary_ko.txt")
if audit:
    R.page_break()
    R.h("부록 E. NVMeVirt 코드 감사 요약")
    R.p("실험 전에 에이전트 여러 개로 NVMeVirt 코드를 독립적으로 읽고(쓰기 경로·쓰기 버퍼 / 초기화·기하 구조 / GC·타이밍), "
        "중요 주장마다 반박 시도 2 개(코드 경로 추적, 수치 예시 대조)로 검증했다. 결과 요약:", size=9.5)
    R.code(audit)
R.save(OUT)
print(f"wrote {OUT}")
