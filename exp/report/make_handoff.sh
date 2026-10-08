#!/usr/bin/env bash
# Build a self-contained hand-over bundle (.tgz) for a Claude that runs on another server and cannot
# see this machine. Entry point inside the bundle: EXPERIMENT_LOG_FOR_CLAUDE.md
#
# usage: bash exp/report/make_handoff.sh [LABEL]
#   OUT_DIR   (default ~/jsw/handoff)             where ksc2026_handoff_<KST stamp>[_LABEL].tgz is written
#   KSC_DIR   (default ~/jsw/KSC2026)             paper materials (PDFs, 산출물/)
#   TEXT_DIR  (default $OUT_DIR/_materials_text)  plain-text extracts of the materials (research plan redacted)
#
# Contents: the log, README_FIRST.txt, MANIFEST.txt (size + sha256 of every file), repo/ (working tree without
# .git, .venv, *.ko, gallery_*.html), repo.gitbundle (full git history), git_log.txt, materials/ (PDFs, 산출물/, text extracts),
# deliverables/ (the .docx record if it exists), server_state/ (progress and state at bundle time),
# claude_memory/ (this server's Claude memory notes).
# The research-plan .docx is never copied: it contains server credentials. Only the redacted text is included.
# Credential guard: patterns are read at run time from that .docx (IP, IP prefix, password token); nothing is stored.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="${OUT_DIR:-$HOME/jsw/handoff}"
KSC_DIR="${KSC_DIR:-$HOME/jsw/KSC2026}"
TEXT_DIR="${TEXT_DIR:-$OUT_DIR/_materials_text}"
LABEL="${1:-}"
STAMP="$(TZ=Asia/Seoul date +%Y%m%d_%H%M)"   # KST in the name (server clock stays UTC)
NAME="ksc2026_handoff_${STAMP}${LABEL:+_$LABEL}"
STAGE="$(mktemp -d)"
B="$STAGE/$NAME"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$B"/{materials,deliverables,server_state,claude_memory}

to_kst() {   # '[YYYY-MM-DD HH:MM:SS] ...' (server clock, UTC) -> same line with the KST time
	python3 -c '
import datetime as d, re, sys
for ln in sys.stdin:
    m = re.match(r"^(\s*)\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]", ln)
    if m:
        t = d.datetime.strptime(m.group(2), "%Y-%m-%d %H:%M:%S") + d.timedelta(hours=9)
        ln = m.group(1) + "[" + t.strftime("%Y-%m-%d %H:%M:%S") + " KST]" + ln[m.end():]
    sys.stdout.write(ln)'
}

# credential patterns are derived at run time from the research-plan .docx (which holds the server login and is
# never bundled), so neither this script nor the bundle contains them; CRED_PAT may also be given in the environment
CRED_PAT="${CRED_PAT:-$("$REPO/exp/.venv/bin/python" - "$KSC_DIR/연구 계획 흐름.docx" 2> /dev/null << 'PYCRED'
import re, sys, docx
t = "\n".join(p.text for p in docx.Document(sys.argv[1]).paragraphs)
pats = set()
for ip in re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", t):
    pats.add(re.escape(ip))
    pats.add(re.escape(".".join(ip.split(".")[:2])) + r"\.")
for tok in re.findall(r"비번\s*(\S+)", t):
    pats.add(re.escape(tok))
print("|".join(sorted(pats)))
PYCRED
)}"
[[ -n "$CRED_PAT" ]] || { echo "ERROR: no credential patterns (research-plan .docx not readable?) — bundle NOT written" >&2; exit 1; }
# --- guard 1: the git history that goes into repo.gitbundle must not contain credentials either
# (count with grep -c, which reads all of its input: 'git log | grep -q' under pipefail fails OPEN, because grep -q
#  exits at the first match, git dies of SIGPIPE and the pipeline status is then non-zero = "no match")
HIST="$STAGE/git_history.txt"
git -C "$REPO" log -p --all > "$HIST"
n_hist=$(grep -cE "$CRED_PAT" "$HIST" || true)
rm -f "$HIST"
if [[ ! "$n_hist" =~ ^[0-9]+$ ]] || (( n_hist > 0 )); then
	echo "ERROR: credential-looking strings in the git history ($n_hist line(s)) — rewrite those commits first; bundle NOT written" >&2
	exit 1
fi

# --- the log (entry point)
cp "$REPO/EXPERIMENT_LOG_FOR_CLAUDE.md" "$B/"

# --- repository working tree (what is on disk now, committed or not) + full history
rsync -a --exclude .git --exclude upstream_tmp --exclude 'exp/.venv' --exclude '*.ko' --exclude '*.o' \
	--exclude '*.mod' --exclude '*.mod.c' --exclude '.*.cmd' --exclude __pycache__ --exclude Module.symvers \
	--exclude modules.order --exclude 'gallery_*.html' "$REPO/" "$B/repo/"
git -C "$REPO" bundle create "$B/repo.gitbundle" --all 2> /dev/null
{
	echo "# git log --stat --all, dates in KST (TZ=Asia/Seoul --date=iso-local), at $(TZ=Asia/Seoul date '+%F %T') KST"
	echo "# HEAD $(git -C "$REPO" rev-parse HEAD)"
	echo "# remotes:"; git -C "$REPO" remote -v
	echo "# uncommitted (git status --porcelain):"; git -C "$REPO" status --porcelain
	echo
	TZ=Asia/Seoul git -C "$REPO" log --stat --date=iso-local --all
} > "$B/git_log.txt"

# --- materials (no research-plan .docx: it holds credentials)
find "$KSC_DIR" -maxdepth 1 -type f -name '*.pdf' -exec cp {} "$B/materials/" \;
[[ -d "$KSC_DIR/산출물" ]] && cp -r "$KSC_DIR/산출물" "$B/materials/"
[[ -d "$TEXT_DIR" ]] && cp -r "$TEXT_DIR" "$B/materials/text"

# --- deliverables
for f in "$REPO"/exp/report/*.docx; do [[ -e "$f" ]] && cp "$f" "$B/deliverables/"; done

# --- server state at bundle time (the receiving Claude cannot look it up)
{
	echo "bundle created: $(TZ=Asia/Seoul date -Is) (KST) = $(date -u -Is) (UTC; server clock and raw logs are UTC)"
	echo "host: $(hostname)  kernel: $(uname -r)"
	echo "repo path on server: $REPO"
	echo "tmux sessions: $(tmux ls -F '#{session_name} created #{session_created}' 2> /dev/null \
		| while read -r n _ e; do echo "$n (created $(TZ=Asia/Seoul date -d "@$e" '+%F %T') KST)"; done || echo none)"
	echo "nvmev loaded: $(grep -c '^nvmev ' /proc/modules || true)"
	echo "sudoers rule present: $([[ -e /etc/sudoers.d/nvmevirt-exp ]] && echo yes || echo no)"
	for d in "$REPO"/exp/results/*/; do
		for v in "$d"*/; do
			[[ -d "$v" ]] || continue
			n_done=$(find -L "$v" -maxdepth 2 -name DONE | wc -l)   # -L: a combined view links to run directories
			n_fail=$(find -L "$v" -maxdepth 2 -name FAILED | wc -l)
			(( n_done + n_fail > 0 )) && echo "results $(basename "$d")/$(basename "$v"): DONE $n_done FAILED $n_fail"
		done
	done
	for l in "$REPO"/exp/results/run_all_*.log; do echo "--- tail $(basename "$l") (times converted to KST)"; tail -5 "$l" | to_kst; done
} > "$B/server_state/state.txt" 2>&1
for l in "$REPO"/exp/results/run_all_*.log; do   # full run logs with KST times (the originals in repo/ stay UTC)
	to_kst < "$l" > "$B/server_state/$(basename "${l%.log}").KST.log"
done
cp /proc/cmdline "$B/server_state/proc_cmdline.txt"
cp -r "$HOME/.claude/projects/-home-dccearth-jsw/memory/." "$B/claude_memory/" 2> /dev/null || true
python3 - "$B/claude_memory" << 'PY2'   # metadata 'modified: ...Z' (UTC) -> KST in the copies
import datetime as d, pathlib, re, sys
for f in pathlib.Path(sys.argv[1]).glob("*.md"):
    t = f.read_text()
    def k(m):
        u = d.datetime.strptime(m.group(1)[:19], "%Y-%m-%dT%H:%M:%S") + d.timedelta(hours=9)
        return "modified: " + u.strftime("%Y-%m-%d %H:%M:%S") + " KST"
    f.write_text(re.sub(r"modified: (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?)Z", k, t))
PY2

# --- guard: no credentials in the bundle
# --- guard 2: no credentials in any file of the bundle
if grep -rIlE "$CRED_PAT" "$B" > "$STAGE/cred_hits.txt"; then
	echo "ERROR: credential-looking strings found, bundle NOT written:" >&2
	cat "$STAGE/cred_hits.txt" >&2
	exit 1
fi

cat > "$B/README_FIRST.txt" << EOF
KSC2026 NVMeVirt 매핑 단위 실험 — 인계 묶음 $NAME (만든 시각 $(TZ=Asia/Seoul date "+%F %T") KST)
1. EXPERIMENT_LOG_FOR_CLAUDE.md 를 처음부터 끝까지 읽는다. 모든 지시·결정·측정·결과가 들어 있다.
   그 안의 「묶음 경로」는 이 폴더 기준이다(repo/…, materials/…, deliverables/…, server_state/…).
2. 실험 상태와 진행률(이 묶음을 만든 시점): server_state/state.txt
3. 코드·결과: repo/ (실험 서버의 저장소 작업 트리. exp/results/ 에 모든 원자료가 있다)
   git 이력: git clone repo.gitbundle repo_git   (또는 git_log.txt)
4. 논문 자료: materials/ (PDF, 산출물/, text/ = 텍스트 추출본. 연구 계획은 credential 을 지운 텍스트만 있다)
5. 최종 문서(.docx)가 만들어졌다면 deliverables/ 에 있다.
6. MANIFEST.txt: 모든 파일의 크기와 sha256
이 묶음을 받은 Claude 는 실험 서버(dccearth)에 접근할 수 없다. 서버 경로는 기록을 위한 것이다.
시각: 기록(.md, .docx)은 KST, 원자료(로그·meta.txt·kernel.log)는 서버 시계 UTC 그대로다(KST = UTC + 9 시간).
EOF
(cd "$B" && find . -type f ! -name MANIFEST.txt -print0 | sort -z | xargs -0 sha256sum | while read -r sum f; do
	printf '%s  %10d  %s\n' "$sum" "$(stat -c %s "$f")" "$f"; done) > "$B/MANIFEST.txt"

mkdir -p "$OUT_DIR"
tar -C "$STAGE" -czf "$OUT_DIR/$NAME.tgz" "$NAME"
ln -sfn "$NAME.tgz" "$OUT_DIR/LATEST.tgz"
echo "$OUT_DIR/$NAME.tgz  $(du -h "$OUT_DIR/$NAME.tgz" | cut -f1)  files: $(wc -l < "$B/MANIFEST.txt")"
