# KSC2026 NVMeVirt FTL 매핑 단위 실험 — 전체 기록 (Claude 인계용)

이 파일은 다른 Claude 세션이 이 논문 실험의 진행 상황을 완전하고 정확하게 이해하도록 쓴 기록이다. 사람이 읽기 좋은 형식보다 정확성과 빠짐없음을 우선한다. 사실은 파일 경로·커밋·로그 줄·숫자로 근거를 붙였다. 「추정」으로 표시하지 않은 문장은 확인된 사실이다.

- 작성: Claude Code (모델 Claude Opus 5.5, 세션 ID 13edeb42-0011-48bf-800d-a7f7e0251b76). 작업 디렉터리 /home/dccearth/jsw. 서버 dccearth.
- 작성 시작: 2026-10-08 14:40 KST. **이 파일의 시각은 모두 KST(UTC+9)다.** 서버 시계와 원자료(run.log, meta.txt, kernel.log, 파일 시각)는 UTC 이므로 원자료를 볼 때는 9 시간을 더한다(사용자 지시 1.9). 마지막 갱신: 맨 아래 「갱신 이력」 참고.
- 사용자: GitHub 계정 Sangwon8799 (git user.email ekfghfl@naver.com). 사용자를 지칭할 때는 they/them.
- 사용자 선호: 2026-10-08 14:19경 「앞으로는 한국어로만 답변해주고 보고해줘.」 → 모든 응답·보고는 한국어. 메모리 파일 /home/dccearth/.claude/projects/-home-dccearth-jsw/memory/korean-only-replies.md 에 저장됨(묶음의 claude_memory/ 에 사본).

---------------------------------------------------------------------------------------------------

## H. 이 파일을 받은 Claude 에게 — 인계 묶음(.tgz) 사용법

- 너는 실험 서버(dccearth)와 다른 서버에 있으며, 실험 서버의 디렉터리를 직접 볼 수 없다. 사용자가 실험 서버에서 만든 인계 묶음 `ksc2026_handoff_<KST 시각>[_라벨].tgz` 를 너에게 전달한다. 이 파일은 그 묶음의 맨 위에 있는 EXPERIMENT_LOG_FOR_CLAUDE.md 다.
- 묶음은 그때까지의 전부를 담은 완결본이다. 이름의 시각이 가장 늦은 묶음이 최신이며 앞 묶음을 대체한다. 실험이 진행 중일 때 만든 묶음은 결과가 일부만 들어 있다(server_state/state.txt 에 진행률).
- 묶음 구조:
  - EXPERIMENT_LOG_FOR_CLAUDE.md — 이 파일(진입점)
  - README_FIRST.txt — 짧은 안내
  - MANIFEST.txt — 모든 파일의 sha256·크기
  - repo/ — 실험 서버 저장소의 작업 트리(묶음 시점, 커밋 안 된 것 포함). .git·exp/.venv·*.ko·gallery_*.html 은 빠져 있다.
    - repo/nvmevirt/ (NVMeVirt 소스), repo/exp/ (스크립트), repo/exp/results/ (모든 원자료·분석 CSV·그림), repo/exp/report/ (보고서 생성기, 감사 결과)
    - repo/exp/results/ 의 데이터셋: main3x3_20261008(랜덤 쓰기 주 데이터셋), main_20261008(첫 설계, 부분), seq3x3_20261008(순차 쓰기, wbuffix·merge), randbs_20261008(랜덤 쓰기 bs 8K·64K), rand3x5_20261008(랜덤 쓰기 매핑 3 × bs 5 보기), pre_*(사전 점검).
    - rand3x5_20261008/wbuffix/ 아래 회차 폴더 45 개는 상대 심볼릭 링크다(→ ../../main3x3_20261008/wbuffix_nodrop/… 와 ../../randbs_20261008/wbuffix/…; 목록은 SOURCES.txt). tar 를 그대로 풀면 링크가 유지된다.
      - 링크만 빠졌고 링크를 만들 수 있는 곳이라면 repo/exp 에서 `python3 link_runs.py results/rand3x5_20261008 results/main3x3_20261008/wbuffix_nodrop results/randbs_20261008/wbuffix` 로 다시 만든다.
      - 링크를 만들 수 없는 곳이라면 복사한다: `rm -rf results/rand3x5_20261008/wbuffix && mkdir -p results/rand3x5_20261008/wbuffix && cp -r results/main3x3_20261008/wbuffix_nodrop/map*_bs*_r* results/randbs_20261008/wbuffix/map*_bs*_r* results/rand3x5_20261008/wbuffix/`. analyze.py·plot.py 는 실제 폴더도 똑같이 읽는다.
    - 실험 서버의 results/<EXP>/gallery_<EXP>.html(그 실험의 모든 그림을 한 파일에 모은 것, 사람이 보기 위한 것)은 크기 때문에 git 과 묶음에 넣지 않았다. 같은 그림이 analysis/·plots/ 에 PNG 로 있고, `python3 make_gallery.py results/<EXP>` 로 다시 만들 수 있다.
  - repo.gitbundle — 전체 git 이력. `git clone repo.gitbundle repo_git` 으로 풀면 커밋·diff 를 볼 수 있다. git_log.txt 는 `git log --stat --all` 사본이다.
  - materials/ — 논문 PDF 4 개, 산출물/(NVMeVirt 설정조사 보고서 docx/pdf/pptx/csv), text/(모든 자료의 텍스트 추출본)
    - 연구 계획 흐름.docx 는 서버 로그인 정보가 들어 있어 넣지 않았다. 그 줄을 지운 텍스트본 materials/text/「연구 계획 흐름 (redacted).txt」만 있다.
  - deliverables/ — 실험 기록 Word 문서(KSC2026_NVMeVirt_매핑단위_실험기록.docx). 생성된 뒤의 묶음에만 있다.
  - server_state/ — 묶음 시점의 서버 상태: state.txt(tmux, 모듈, sudoers, 결과 폴더별 DONE/FAILED 수, 실행 로그 끝), proc_cmdline.txt
  - claude_memory/ — 실험 서버의 Claude 메모리 노트(사용자 선호 등)
- 서버 경로 → 묶음 경로:
  - `/home/dccearth/jsw/KSC2026/nvmevirt/` (실험 당시) = `/home/dccearth/jsw/nvmevirt/` (17:06 KST 이후) → `repo/`
  - `…/nvmevirt/exp/results/<EXP>/` → `repo/exp/results/<EXP>/`
  - `/home/dccearth/jsw/KSC2026/*.pdf`, `산출물/` → `materials/`
  - `/home/dccearth/.claude/projects/-home-dccearth-jsw/memory/` → `claude_memory/`
  - 감사 워크플로 기록(서버의 ~/.claude/…/workflows/…/journal.jsonl) → 묶음에는 원본이 없고 정리본 `repo/exp/report/audit_result.json`, `audit_summary_ko.txt` 가 있다.
  - Claude 세션의 scratchpad(`/tmp/claude-1000/…/scratchpad`) → 묶음에 없다(임시 파일). 필요한 것은 모두 repo/ 나 materials/text/ 로 옮겼다.
- 이 파일에 나오는 서버 경로와 명령(tmux, sudo, insmod 등)은 기록이자 실험 서버에서의 재현 방법이다. 너의 서버에서 실행하라는 뜻이 아니다. 단, 분석·그래프는 묶음만으로 다시 만들 수 있다:
  ```
  cd repo/exp && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  .venv/bin/python analyze.py results/main3x3_20261008        # CSV·그림 재생성
  .venv/bin/python plot.py all --exp results/main3x3_20261008  # 그래프 묶음 → results/main3x3_20261008/plots/
  .venv/bin/python analyze.py results/seq3x3_20261008          # 순차 쓰기 추가 실험 (wbuffix·merge)
  .venv/bin/python plot.py all --exp results/seq3x3_20261008
  python3 make_gallery.py results/seq3x3_20261008               # 모든 그림을 HTML 한 파일로
  .venv/bin/python analyze.py results/rand3x5_20261008          # 랜덤 쓰기 매핑 3 × bs 5 (주 데이터셋 nodrop + randbs_20261008, 심볼릭 링크 보기)
  .venv/bin/python plot.py all --exp results/rand3x5_20261008
  ```
- 원자료 읽는 법:
  - 회차 폴더 = repo/exp/results/<EXP>/<변형>/map<단위>_bs<크기>_r<회>/
  - fio.json = fio 결과
  - fio_*.1.log = 0.5 s 시계열
  - meta.txt / cache.txt / kernel.log / dmesg_*.txt
  - DONE = 정상 종료, FAILED = fio 실패(원인 줄 포함)
- 묶음 생성 스크립트: repo/exp/report/make_handoff.sh. 묶음마다 credential 문자열이 없는지(파일 전체와 git 이력) 검사한 뒤에만 쓴다. 검사 패턴은 실행할 때 서버의 연구 계획 .docx(묶음에는 넣지 않음)에서 뽑아 메모리에서만 쓰므로, 스크립트와 묶음에는 credential 이 없다(19 시경부터; 그 전 판의 문제는 「갱신 이력」 참고).

---------------------------------------------------------------------------------------------------

## 0. 현재 상태 요약 (STATUS)

- 묶음을 받았다면 먼저 server_state/state.txt 로 묶음 시점의 진행률을 확인한다. 이 절은 최종 갱신 시점의 요약이다.
- **추가 실험 2 — 랜덤 쓰기 bs 8K·64K (randbs_20261008 + 합친 보기 rand3x5_20261008; 22:08 KST 사용자 요청, 22:11 KST 시작)**. 지시는 1.20–1.23 절, 설계는 6.7 절, 해석은 8.8 절, 진행은 10.5 절, 수치는 11.4·11.5 절에 있다.
  - 설계: 매핑 4K·16K·32K × fio bs 8K·64K × 3 회 = 18 회, wbuffix, randwrite, nodrop, 블록 계층 커널 기본값(주 데이터셋과 같은 설정·같은 모듈 파일).
  - bs 4K·16K·32K 는 다시 재지 않고 주 데이터셋 nodrop 회차를 쓴다(사용자 선택). exp/link_runs.py 가 두 데이터셋의 회차를 results/rand3x5_20261008/wbuffix/ 에 상대 심볼릭 링크로 모으고(SOURCES.txt), analyze.py·plot.py 는 이 보기를 매핑 3 × bs 5 데이터셋처럼 읽는다.
  - 진행 상태: 22:11:48–22:32:55 KST 에 18/18 회 DONE 으로 끝났다. FAILED 0, chmodel 0, kernel_warn 0 이다. 블록 계층 merges 는 요청의 0.054 % 이하다. analyze.py(randbs·rand3x5), link_runs.py(45 회 링크), plot.py all, make_gallery.py 까지 마쳤다. 상세는 10.5 절, 해석은 8.8 절, 수치는 11.4·11.5 절에 있다.
  - **핵심 결과(3 회 평균, 랜덤 쓰기, 매핑 4K / 16K / 32K)**:
    - bs 8K 는 437.0 / 217.3 / 131.9 MiB/s(매핑 4K 대비 −50.3 / −69.8 %), bs 64K 는 486.3 / 486.4 / 447.1 MiB/s(+0.02 / −8.1 %)다.
    - 결과는 bs/매핑 비율로 거의 정해진다. 비율이 같으면 대역폭이 3 % 안에서 같고 WAF 도 같다(예: 16K/8K 217.3 vs 32K/16K 219.6 MiB/s, WAF 5.90 vs 5.96).
    - bs ≥ 매핑 10 조합은 416–486 MiB/s(매핑 4K 대비 −12.6 ~ +0.02 %), bs < 매핑 5 조합은 같은 매핑의 bs = 매핑 값의 0.16–0.52 배다.
  - sudoers 는 22:11 에 사용자가 다시 설치했고, 23:08 KST 에 사용자가 제거했다(10.5 절). 지금 서버에 sudoers 규칙은 없다.
  - 기록 검증(9.3 절)까지 마쳤다. 순차 쓰기와 이 실험의 결과·문서는 커밋 c9dfb23 = 태그 **ksc2026-v2** 에 있다. GitHub push 여부는 10.5 절 끝을 본다(23:22 KST 시도는 ssh-agent 가 없어 실패했고, 그때 GitHub main 은 cd1fe2b 였다). 랜덤 쓰기 주 데이터셋만 담은 앞선 태그는 ksc2026-final(c742c67)이다.
- **추가 실험 — 순차 쓰기 (seq3x3_20261008; 19:53 KST 사용자 요청, 20:23 KST 시작)**. 지시·결정은 1.13–1.18 절, 코드는 5.6 절, 설계는 6.6 절, 사전 점검은 7.1 절, 발견은 8.5–8.7 절, 코드 검토는 9.1 절, 진행은 10.4 절, 전체 수치는 11.3 절(자동 생성)에 있다.
  - 설계: 매핑 4K·16K·32K × fio bs 4K·16K·32K × 3 회 × 모델 {wbuffix, merge}. fio rw=write(순차), 페이지 캐시 nodrop 만, 블록 계층 병합 끔(nomerges=2). 54 회. 결과 폴더 `results/seq3x3_20261008/{wbuffix,merge}/`.
  - wbuffix = 랜덤 쓰기 주 데이터셋과 같은 모듈 파일(SHA-256 같음). merge = wbuffix + 쓰기 버퍼 병합(WBUF_MERGE=1, 이 세션에서 새로 만든 코드, 커밋 66446ea). 매핑 단위보다 작은 쓰기를 파티션마다 열린 매핑 단위 하나에 모았다가, 가득 차면 flash 에 쓴다.
  - 진행 상태: 20:23:24–21:26:45 KST 에 54/54 회 DONE 으로 끝났다. FAILED 0, chmodel 0, kernel_warn 0, 블록 계층 merges 0 이다. analyze.py, plot.py all, make_gallery.py 를 마쳤다(21:26:45–21:27:42 KST). 상세는 10.4 절, 해석은 8.7 절, 수치는 11.3 절에 있다.
  - **핵심 결과(3 회 평균, 순차 쓰기)**:
    - bs ≥ 매핑: 두 모델 모두 2,087–2,233 MiB/s 로 NAND 한계(2,233)에 닿는다. bs 4K 는 약 535 K IOPS 에서 멈춘다. WAF 는 1.000 이다.
    - 원래 모델(wbuffix)의 bs < 매핑: 16K/4K 334.9, 32K/4K 209.5, 32K/16K 369.0 MiB/s 다. 같은 bs 의 매핑 4K 대비 −84.0 / −90.0 / −83.5 % 이고, WAF 는 5.40 / 9.15 / 3.40 이다. NVMeVirt 가 작은 쓰기를 합치지 않기 때문이다.
    - 병합 모델(merge)의 bs < 매핑: 2,094.4 / 2,094.6 / 2,232.2 MiB/s 로, 매핑 4K 대비 +0.37 / +0.38 / −0.02 % 다. WAF 는 1.000 이다. 쓰기 버퍼가 작은 쓰기를 합치면 순차 쓰기에서 매핑 단위를 키워도 손실이 없다.
    - 랜덤 쓰기 대비 순차(merge)는 bs ≥ 매핑에서 4.6–5.3 배, bs < 매핑에서 10.2–30.7 배 빠르다. 랜덤 쓰기의 bs < 매핑 손실은 병합으로 줄지 않는다(merge −0.7 %, 7.1 절 C).
  - sudoers 규칙은 21:34 KST 에 사용자가 제거했다(10.4 절). 순차 쓰기 결과의 커밋(a86fc87, 403a6ae)·push·인계 묶음은 랜덤 bs 8K·64K 실험과 함께 처리했다(10.5 절 끝).
- **최종 상태(17:10 KST 이후)**:
  - 주 데이터셋 실험 완료: 16:00:35–17:03:57 KST, 54/54 회 DONE, FAILED 0. 분석·그래프 완료.
  - 실험 후 정리(사용자 지시 1.6):
    - 저장소를 /home/dccearth/jsw/KSC2026/nvmevirt → **/home/dccearth/jsw/nvmevirt** 로 옮겼다(17:06 KST).
    - /home/dccearth/jsw/exp 를 내용물째 삭제했다.
    - 저장소 안 upstream_tmp/ 를 지우고 exp/.venv 를 다시 만들었다.
    - KSC2026/EXPERIMENT_LOG_FOR_CLAUDE.md 는 ../nvmevirt/EXPERIMENT_LOG_FOR_CLAUDE.md 를 가리키는 링크로 바꿨다.
  - 이 파일의 서버 경로 중 「/home/dccearth/jsw/KSC2026/nvmevirt」 는 실험 당시 위치다. 지금은 /home/dccearth/jsw/nvmevirt 이고, 묶음에서는 repo/ 다.
  - 원자료(meta.txt, run.log 등)에 적힌 경로도 실험 당시 위치 그대로다.
- **진행 상태(17:24 KST 기준, 이후 경과는 10.3 절)**:
  - 실험·분석·그래프 완료.
  - 실험 기록 .docx 1 차본 완료: deliverables/ 와 repo/exp/report/, 63 쪽. LibreOffice 로 PDF 렌더링해 확인했다.
  - 문서 검증 워크플로(wf_7f78deeb-8ce, 17:09 시작)가 진행 중이다. 검증 결과로 .docx·이 파일이 고쳐질 수 있으니, 최종본은 다음 묶음(라벨 final)을 기준으로 한다.
  - (최종) 실험·분석·검증·문서·정리 모두 완료. 결과·문서는 GitHub main 과 태그 ksc2026-final 에 있다. sudoers 규칙은 18:33 KST 에 제거했다.
  - GitHub push: 처음 쓰던 SSH agent 소켓(/tmp/ssh-UN8QkXPn5f/agent.4695, 사용자 pts/0 세션)은 그 세션이 16:31 KST 에 끝나며 사라졌고, 17:09 KST 에 push 하려다 발견했다. 17:19 KST 에 사용자가 다시 접속해 새 소켓(/tmp/ssh-i3drMOKMuH/agent.76661)이 생겼다. 최종 push 결과는 10.3 절 끝에 적는다.
  - sudoers 규칙: 제거 시각과 확인은 10.3 절 끝에 적는다.
- **핵심 결과(주 데이터셋, 3 회 평균; 상세는 11 절, 근거 파일은 repo/exp/results/main3x3_20261008/analysis/*.csv)**:
  - 페이지 캐시 drop(sync; echo 3 > /proc/sys/vm/drop_caches)은 결과에 영향이 없다. 27 쌍(9 조합 × 3 회)의 대역폭 차이는 평균 +0.009 %(95 % CI −0.084 ~ +0.101 %, p = 0.85)이고, 조합별 차이도 −0.21 ~ +0.39 %(모든 p > 0.15)다. IOPS·평균/p99 지연·GC 전후 대역폭·WAF 도 유의한 차이가 없다.
  - drop 조건에서 일관되게 달라진 것은 fio 시작 표지부터 첫 GC 까지의 시간뿐이다. 23–36 ms(+0.51 %, p < 1e-12) 늦은데, 캐시를 비운 뒤 sudo·fio 실행 파일을 디스크에서 다시 읽느라 fio 시작이 늦어진 것으로 보인다. 장치 성능과는 무관하다.
  - bs ≥ 매핑 단위에서는 60 s 평균 대역폭이 416–482 MiB/s 로 매핑 단위에 따른 차이가 작다. bs 16K 는 매핑 4K 481.0, 16K 420.4 MiB/s(−12.6 %)이고, bs 32K 는 매핑 4K 482.3, 16K 441.6, 32K 424.6 MiB/s(−8.4 %, −11.9 %)다.
  - bs < 매핑 단위에서는 성능이 크게 떨어진다. 매핑 16K·bs 4K 는 129.7 MiB/s 로 매핑 4K·bs 4K(416.0) 대비 −68.8 %, 매핑 32K·bs 4K 는 68.3 MiB/s(−83.6 %), 매핑 32K·bs 16K 는 219.6 MiB/s 로 매핑 4K·bs 16K(481.0) 대비 −54.3 % 다.
  - 그 원인은 쓰기 증폭이다. WAF_total(NAND 바이트 ÷ 호스트 바이트)은 bs ≥ 매핑에서 3.1–3.5 인데, 16K/4K 8.8, 32K/4K 17.1, 32K/16K 6.0 이다. 이는 매핑 단위/bs 배의 부분 쓰기 증폭(4·8·2 배)에 GC 증폭(2.1–3.0)이 곱해진 값이다.
  - GC 이전 구간의 대역폭은 NAND 프로그램 한계로 정해진다. bs ≥ 매핑에서는 2,001–2,218 MiB/s 로, 16 die 합 한계 2,233 MiB/s 의 90–99 % 다. bs < 매핑에서는 그 한계 × bs/매핑에 가깝다(16K/4K 535.6 = 한계 × 1/4 의 96 %, 32K/4K 256.1 = × 1/8 의 92 %, 32K/16K 1,026.9 = × 1/2 의 92 %).
  - 장치가 빈 상태에서 시작하므로 모든 조합에서 첫 GC 는 5.7–6.3 s 에 시작한다(물리 공간의 380/384 line 이 찼을 때). 60 s 평균에는 GC 이전 약 6 s(약 2 GB/s)가 크게 반영된다. GC 이후 구간 평균은 bs ≥ 매핑에서 240–307 MiB/s, bs < 매핑에서 47–130 MiB/s 다.
  - GC 이후 대역폭은 fio 의 randommap 주기를 따라 출렁인다. bs ≥ 매핑에서는 GC 시작 직후 약 130 MiB/s 까지 떨어졌다가 회복하고, 장치를 한 바퀴 다 쓸 무렵(약 37–52 s) 1,500–1,900 MiB/s 로 치솟은 뒤 다시 떨어진다. bs < 매핑에서는 치솟지 않고 계속 떨어진다. 그래서 마지막 20 s 평균은 조합에 따라 순서가 바뀐다(예: bs 16K 에서 매핑 4K 244.8 < 매핑 16K 323.4 MiB/s). 결과를 비교할 때는 60 s 평균과 GC 이후 구간 평균을 함께 보아야 한다.
  - 평균 완료 지연은 IOPS 와 반비례한다(iodepth 32 고정, Little 의 법칙). 4K/4K 299 µs, 16K/4K 963 µs, 32K/4K 1,829 µs 다. p99 지연은 모든 조합에서 13–18 ms 로, GC 로 쓰기 버퍼가 막히는 구간이 결정한다.
  - 반복 간 대역폭 편차는 매우 작다. 변동계수 평균 0.15 %, 최대 0.37 %(4K/4K, nodrop; drop 은 0.35 %)다. fio 난수 순서가 고정이라(randrepeat=1) 1–3 회차의 시계열이 거의 겹친다.
  - L2P 매핑 표 크기(물리 12 GiB 의 전체 FTL 페이지 × 항목 8 B, NVMeVirt maptbl 기준)는 매핑 4K 24 MiB, 16K 6 MiB, 32K 3 MiB 로 매핑 단위에 반비례한다(논리 11.2 GiB 장치 기준으로 계산하면 22.4/5.6/2.8 MiB). 다만 NVMeVirt 에는 매핑 캐시(DRAM) 모델이 없어 이 이득은 성능 수치에 나타나지 않는다.
  - 보조 데이터셋에서 bs ≥ 매핑 단위 조합은 base 와 wbuffix 의 차이가 −0.5 ~ +1.2 % 로 반복 편차 수준이었다(같은 코드 경로). bs < 매핑 단위 조합은 wbuffix 가 base 보다 18.7–26.3 % 낮았는데(base 가 높게 나옴), 쓰기 버퍼 과다 반환으로 타이밍 모델이 정상 범위를 벗어난 값이다. base 의 매핑 32K·bs 16K 는 장치가 멈췄다.
  - 해석 시 한계: NVMeVirt 는 부분 쓰기의 read-modify-write(옛 데이터 읽기)를 모델링하지 않으므로, bs < 매핑 단위의 불이익은 실제 SSD 보다 작게 나올 수 있다. 쓰기 조기 완료라 NAND·GC 비용은 쓰기 버퍼가 찰 때만 호스트에 보인다. 지우기 지연은 0 이다.
- **최종 실험 설계(주 데이터셋)**: `results/main3x3_20261008/` — 선배의 요청(1.7 절)에 따라 바꾼 설계다.
  - 매핑 단위 {4k,16k,32k} × fio bs {4k,16k,32k} × 3 회
  - 모델은 wbuffix(쓰기 버퍼 수정)만 쓴다. 사용자 선택(1.7 절).
  - OS 페이지 캐시: 회차마다 drop(`sync; echo 3 > /proc/sys/vm/drop_caches`) / nodrop 을 연달아 측정한다. 순서는 반복마다 바뀐다.
  - 9 × 3 × 2 = 54 회. 결과 폴더는 `wbuffix_nodrop/`, `wbuffix_drop/`. 2026-10-08 16:00:35 KST 시작, 약 65 분.
- **첫 설계(보조 데이터셋, 미완료)**: `results/main_20261008/` — 매핑 6 × bs 6 × 3 회 × {base, wbuffix}.
  - 14:20–15:51 실행. 설계 변경으로 15:51:23 에 회차 경계에서 중단했다.
  - 남은 것: base 완료 20 + FAILED 1(map32k_bs16k_r1, 장치 멈춤), wbuffix 완료 53(rep1 36 개 전부 + rep2 17 개).
  - base 의 문제(8 절)를 보여 주는 근거이자 6×6 전체 경향 참고용이다.
- 사전 점검 결과: `results/pre_smoke_test/`, `pre_gcstats_ab/` (7 절), `pre_cache_test/` (1.7 절)
- 최종 산출물(완료 후):
  - 실험 기록 Word 문서: deliverables/ 와 repo/exp/report/
  - 결과 CSV: `repo/exp/results/main3x3_20261008/analysis/summary_runs.csv`(회차별), `summary_agg.csv`(조합별), `cache_compare.csv`(drop vs nodrop 쌍 비교), `cache_pairs.csv`
  - 그림: analysis/fig_*.png, plots/*.png
  - GitHub: git@github.com:Sangwon8799/nvmevirt.git main (사용자 저장소)
- 이 파일의 「11. 결과」에는 실험이 끝난 뒤 자동 생성한 전체 수치가 들어간다(AUTO-RESULTS 표지 사이).

---------------------------------------------------------------------------------------------------

## 1. 사용자 지시 원문과 이행 상태 (시간순, 이 세션)

### 1.1 첫 지시 (2026-10-08 13:4x KST) — 원문 그대로

```
논문에 작성할 실험 데이터를 쌓을거야. 논문에 대한 자세한 내용은 KSC2026 폴더의 자료들을 확인해. 우선 NVMeVirt를 GitHub에서 fork해와서 해당 폴더에 nvmevirt 라는 이름으로 둬. 그리고 내부 파일들을 다시 nvmevirt라는 서브 폴더를 만들어서(즉 동일한 이름의 폴더) 그 안에 전부 두고, 실험 환경 세팅용 폴더는 exp로 만들어서 둬줘. 이후 처음에 만든 nvmevirt 폴더를 내 GitHub repo에 올려줘(Sangwon8799). mapping size는 4k, 8k, 16k, 32k, 64k, 128k 단위로 실험을 진행할거고, 서버 RAM 크기가 24GB이고 하위 12GB부터 24GB까지 총 12GB를 NVMeVirt 용량으로 사용할거야. CPU는 1개를 dispatcher, 나머지 2개 총 3개를 사용할거야. ioengine은 libaio를 사용할거야. 매 실험마다 rmmod를 써서 NVMeVirt 스토리지를 초기화한 후 다시 진행하도록 하고, rand_time은 0으로 해서 GC가 실행되기 전 데이터도 함께 측정해줘. 각 실행 시간은 1분으로 해주고, 한 실험 당 3번씩 반복 진행해서 데이터를 쌓아줘. ssd_config.h에서 BLK 크기가 2MiB가 되도록 해줘(아마 384로 쓰면 됨). mapping size 64k 이후부터는 page 크기 때문에 assert 통과가 안 되므로 page 크기가 mapping size와 동일하도록 해줘. iodepth는 32로 해줘. 그 외에는 NVMeVirt 설정조사 자료들을 보고 해당 값들을 기본값으로 설정해줘. 실험의 시작부터 결과를 얻기 까지 전 과정을 기록해서 `.docx` 파일로 만들어줘. 서버의 환경, 어떤 버전, fio의 어떤 버전, NVMeVirt 무슨 버전을 사용하는지 등등 상세하게 기록해주고, 데이터를 얻을 때 사용한 스크립트가 있으면 해당 스크립트 코드 전문도 함께 적어줘. 실험 전 세팅과 실험 후 세팅과 같은 기록도 넣어줘. 즉 실험을 진행하면서 변경한 설정값, 데이터 등 모든 것을 기록해서 실험 환경을 다른 사람이 봐서 진행해도 동일하게 진행할 수 있으면 돼. 궁금한거 있으면 물어봐.
```

(지시와 함께 workflow-authoring 스킬이 호출되었고, 세션은 ultracode(워크플로 적극 사용) 모드다.)

지시별 해석과 이행:

| 지시 | 해석 / 이행 | 상태 |
|---|---|---|
| NVMeVirt fork → 「해당 폴더」에 nvmevirt 로 | 「해당 폴더」를 KSC2026 폴더로 해석했다. upstream snu-csl/nvmevirt 를 clone 해 /home/dccearth/jsw/KSC2026/nvmevirt 로 두고 원본 git 이력을 유지했다(remote upstream). GitHub 에서는 사용자가 빈 저장소 Sangwon8799/nvmevirt 를 직접 만들었다(1.3 의 답). GitHub의 'fork' 관계(네트워크)는 없지만 원본 이력이 그대로 들어 있다. | 완료 |
| 내부 파일을 nvmevirt/nvmevirt 서브폴더로 | 커밋 d508610 "Move NVMeVirt sources into nvmevirt/ subdirectory". `git mv` 만 했다(42 파일, 내용 변경 0). .gitignore 와 .clang-format 도 함께 옮겼다. | 완료 |
| 실험 세팅 폴더 exp | /home/dccearth/jsw/KSC2026/nvmevirt/exp (스크립트, fio 틀, 결과, 보고서 생성기) | 완료 |
| 처음 만든 nvmevirt 폴더를 GitHub 에 | origin = git@github.com:Sangwon8799/nvmevirt.git. 14:20 KST 에 main 을 5769378 까지 push 했다. 그 뒤 커밋(949ae38 = 옛 2a462a3, e598e75 = 옛 a93ef76)과 결과·문서·생성기 커밋은 실험·검증이 끝난 뒤 main 과 태그 ksc2026-final 로 push 했다(10.3 절 끝에 결과). | 10.3 절 |
| mapping size 4k–128k | `make MAPPING_UNIT=<bytes>` 로 매핑 단위별 모듈을 빌드한다. ssd.c 의 secs_per_pg = MAPPING_UNIT / LBA_SIZE. 6 종 모두 빌드했다(exp/modules/base, exp/modules/wbuffix). 측정은 1.7 의 설계 변경으로 주 데이터셋(main3x3_20261008)에서 4k·16k·32k 만 했다. 8k·64k·128k 는 보조 데이터셋(main_20261008)에만 있다: 8k 는 base rep1·wbuffix rep1–2, 64k·128k 는 wbuffix rep1 만 있다(base 의 32k/32k·64k·128k 는 32k/16k 실패 뒤 실행되지 않음). | 빌드 완료, 측정 범위는 1.7 에서 변경 |
| RAM 24GB, 상위 12–24GB 를 NVMeVirt 로 | GRUB memmap=12G$12G 는 이미 설정되어 있었다(이 세션 이전). insmod memmap_start=12G memmap_size=12G | 완료 |
| CPU 3 개 (디스패처 1 + 2) | isolcpus=3-5 는 이미 설정되어 있었다. insmod cpus=3,4,5 (첫 값 = 디스패처) | 완료 |
| ioengine libaio | fio 작업 파일 ioengine=libaio | 완료 |
| 매 실험마다 rmmod 로 초기화 | 회차마다 rmmod(있으면) → insmod → fio → rmmod | 완료 |
| 「rand_time」 0 | 오타로 보고 ramp_time=0 으로 해석했다. GC 이전 구간도 결과에 포함된다. | 완료 |
| 실행 1 분, 3 회 반복 | runtime=60, time_based=1, REPS=3 | 완료 |
| BLK 2MiB (384) | ssd_config.h BLKS_PER_PLN 8192 → 384. 블록이 정확히 2 MiB 인 것을 적재 로그로 확인했다. | 완료 |
| 64k 이상은 page = mapping size | ssd_config.h: MAPPING_UNIT > 32768 이면 FLASH_PAGE_SIZE = MAPPING_UNIT, 아니면 KB(32) | 완료 |
| iodepth 32 | iodepth=32 | 완료 |
| 그 외 설정조사 자료 기본값 | 970 Pro 묶음 기본값을 유지했다(설정조사 보고서 부록 A 와 일치하는지 확인). 보고서의 추천 중 용량 64 GiB, 코어 5, 300 s 사전 채움은 사용자 지시로 대체되었다. | 완료 |
| 전 과정 .docx 기록 | exp/report/make_report.py 가 결과로부터 docx 를 생성한다. 17:07 KST 1 차본, 17:08 LibreOffice 렌더링 확인(PDF 63 쪽), 17:09–18:25 검증 워크플로(지적 89 건 확인) → 18:2x–19 시경 반영해 최종본 생성(10.3 절). | 완료(10.3 절) |
| fio 블록 크기 | 지시에 명시되지 않았다. 처음에는 연구 계획 문서의 「randwrite 4k, 8k, 16k, 32k, 64k, 128k」에 따라 6 개 모두 측정하기로 정했다(묻지 않음). 1.7 의 설계 변경으로 주 데이터셋은 4k·16k·32k 로 바뀌었다. 6 개 bs 의 결과는 보조 데이터셋(main_20261008)에 일부만 있다. | 1.7 에서 변경 |

### 1.2 Claude 가 물은 것과 사용자의 답 (AskUserQuestion, 13:5x KST)

- Q1 sudo 방식 → 사용자 답: 「NOPASSWD 규칙 추가 (Recommended)」
- Q2 GitHub 인증(서버에 키·gh 없음) → 답 원문: 「ssh config에 agent forwarding으로 github 정보를 보내고 있어. 이거 활용할 수 있어?」
  - 확인 결과 /tmp/ssh-UN8QkXPn5f/agent.4695 (사용자의 pts/0 SSH 세션)에 ed25519 키 2 개가 있었다. 하나는 ekfghfl@naver.com, 다른 하나는 dccearth_gateway_key. `SSH_AUTH_SOCK=/tmp/ssh-UN8QkXPn5f/agent.4695 ssh -T git@github.com` → "Hi Sangwon8799! You've successfully authenticated". Claude 의 Bash 환경에는 SSH_AUTH_SOCK 이 없으므로 git 명령마다 SSH_AUTH_SOCK=<소켓> 을 붙여야 한다. 소켓 경로는 사용자가 다시 접속하면 바뀐다(`ls /tmp/ssh-*/agent.*` 로 찾는다).
- Q3 push 대상(공개 목록에 Sangwon8799/nvmevirt 없음) → 답 원문: 「nvmevirt 이름으로 새로 만들게. 이전 기록은 잊어.」 → 사용자가 빈 저장소를 만들었다. `git ls-remote` 결과가 비어 있어(exit 0) 빈 저장소임을 확인한 뒤 main 을 push 했다. 예전 저장소의 map4k–map128k 브랜치 이력(2.2 절)은 무시한다.

### 1.3 두 번째 메시지 (14:0x KST)

- 원문: 「sudo 비밀번호 줄테니 그냥 알아서 진행해. 비밀번호 <생략> 이야.」 — **비밀번호는 이 파일·저장소·인계 묶음·메모리 어디에도 기록하지 않는다**(예외였던 make_handoff.sh 의 쪼갠 검사 문자열은 18:2x KST 에 없앴다 — 「갱신 이력」). 사용처: sudoers 규칙 설치 3 번(14:06 최초 설치, 14:08 /dev/kmsg 추가, 15:55 drop_caches 추가 — 1.7 절), dmidecode(DIMM 정보 기록, 14:21–14:22), 그리고 실험 후 sudoers 제거(10.3 절). `sudo -S` 로 stdin 에 넘긴 뒤 바로 `sudo -k` 했다. 나머지 판단(base/wbuffix 두 변형 실행, GC_STATS 계측 사용)은 이 「알아서 진행」 지시에 따라 Claude 가 정했다.

### 1.4 세 번째 메시지 (14:19경)

- 원문: 「앞으로는 한국어로만 답변해주고 보고해줘.」 → 메모리에 저장했다.

### 1.5 네 번째 메시지 (14:3x KST) — 이 파일을 만든 계기

- 원문: 「그래프로 확인할 수 있도록 하는 코드도 만들어주고, 다른 Claude가 이 논문의 진행 상황을 완전하고 정확하게 이해할 수 있도록 아주 상세한 기록을 적은 `.md` 파일도 만들어줘. 길이 제한은 없고, 내가 지시한 것을 포함하여 실험의 시작과 끝까지 진행되면서 측정한 것, 설정을 바꾼 것, 결과 등등 모든 것들을 아주 상세히 기록해줘. 사람이 볼 게 아니기 때문에 가독성은 신경쓰지 말고 내용을 정확히 전달할 수 있도록 해줘.」
- 이행:
  - exp/plot.py — 명령줄 그래프 도구(12 절)
  - 이 파일 — /home/dccearth/jsw/KSC2026/nvmevirt/EXPERIMENT_LOG_FOR_CLAUDE.md, git 으로 관리하며 push 된다.

### 1.6 다섯 번째 메시지 (2026-10-08 15:42 KST, 본 실험 진행 중)

- 원문: 「실험이 끝나면 nvmevirt 폴더 위치를 ~/jsw로 옮겨주고 ~/jsw에 있는 ~/jsw/exp 폴더는 내용물을 포함해서 모두 삭제해줘.」
- 계획(실험 종료 후):
  - /home/dccearth/jsw/KSC2026/nvmevirt → /home/dccearth/jsw/nvmevirt 로 이동
  - /home/dccearth/jsw/exp(2.2 절의 이전 작업 폴더) 전체 삭제. 삭제 전에 그 안의 iodepth 결과 수치를 2.2 절에 옮겨 적는다.
  - 저장소 안 upstream_tmp/ 삭제, exp/.venv 재생성(절대경로), KSC2026/EXPERIMENT_LOG_FOR_CLAUDE.md 심볼릭 링크 갱신
  - 문서의 경로를 갱신하고 이동 사실을 기록한다.
- 이행 결과는 「갱신 이력」과 10.3 절에 적는다.

### 1.7 여섯 번째 메시지 (2026-10-08 15:5x KST) — 실험 설계 변경(선배 요청)

- 원문:
```
데이터 쌓는 중간에 미안한데 실험 내용 좀 조정할 수 있을까? 선배님한테 여쭤봤을 때 다음과 같이 실험 데이터 셋을 조정해달라고 하셨어.
* mapping size는 4k, 16k, 32k 단위로만 측정
* host의 block size도 마찬가지로 4k, 16k, 32k로 측정
* 선배님께서 echo 3 > cache drop 명령어를 사용했는지 안 했는지에 따라 결과 차이가 나는지 여쭤보셨어(NVMeVirt가 아닌 OS 자체의 Page Cache를 포맷하는 거라 결과에 영향이 있을 수 있다고 하시네).
```
- Claude 의 조치:
  - 15:51:23 진행 중이던 6×6 실험을 회차 경계에서 멈췄다(tmux kill 은 다음 회차의 '===' 줄이 나온 직후, insmod 전에 했다). 반쯤 만든 회차 폴더(wbuffix/map16k_bs128k_r2, kernel.log 만 있음)는 지웠다. run.log 에 STOPPED 줄을 남기고 env_after_stop 스냅샷을 찍었다.
  - 사용자에게 drop_caches 이론을 설명했다: fio direct=1(O_DIRECT)로 블록 장치에 쓰므로 데이터 경로가 페이지 캐시를 거치지 않는다. NVMeVirt 저장 공간은 memmap 으로 커널 관리에서 빠진 메모리이고, 회차마다 장치를 새로 만든다. 따라서 영향이 없어야 하며, 실측으로 확인하기로 했다.
- AskUserQuestion 1 차:
  - 변형 선택 → 사용자 답 「bs와 wbuffix의 차이가 뭐야?」. base 를 bs 로 오타 낸 것으로 보고 base vs wbuffix 차이를 설명했다.
    - 설명 내용: 쓰기 버퍼의 역할(조기 완료 + 프로그램 완료 시 반납 = NAND/GC 가 호스트에 보이는 유일한 통로), base 의 할당 bs·반납 매핑 단위 불균형(주차장 비유), 결과(채널 모델 오류 폭주·장치 멈춤), wbuffix 의 한 줄 수정, bs ≥ 매핑에서는 같음, 실측 예(16K/4K 1 회차 base 167.9 MiB/s·오류 676 만 줄 vs wbuffix 129.9 MiB/s·오류 0), RMW 미모델 한계.
  - drop 비교 방식 → 「회차마다 drop/no-drop 교대 (Recommended)」
- AskUserQuestion 2 차: 변형 → 「wbuffix만 (Recommended)」
- 15:55 sudoers 에 `/usr/bin/tee /proc/sys/vm/drop_caches` 를 추가했다(sudoers 설치 3 번째). 시험 drop 때 Cached 가 10,227,884 kB → 245,072 kB 로 줄었다. 그 전 base 회차들의 수천만 줄 오류 로그가 journald 파일로 디스크에 쓰이면서 페이지 캐시가 10 GB 쌓였던 것으로 추정한다.
- 15:57–15:59 사전 시험 `results/pre_cache_test/` (wbuffix, 매핑 4k·16k × bs 4k, 8 s, 2 회, drop/nodrop):
  - 4k/4k: nodrop 1553.2·1553.2, drop 1550.6·1552.2 MiB/s
  - 16k/4k: nodrop 431.4·430.8, drop 431.3·430.8 MiB/s
  - 차이 −0.12 % / −0.005 %
- 16:00 커밋 1d6cd03:
  - CACHE_MODES 구현
  - run_all.sh 를 새 설계로 바꾸고, 첫 설계는 run_all_6x6.sh 로 보존
  - analyze.py 에 쌍 비교(cache_compare.csv) 추가, plot.py 일반화
- 16:00:35 `bash run_all.sh main3x3_20261008` (tmux ksc2026). 모듈은 다시 빌드하지 않고 14:20 에 빌드한 exp/modules/wbuffix 를 쓴다(main_20261008 wbuffix 회차와 같은 바이너리).

### 1.8 일곱 번째 메시지 (2026-10-08 16:0x KST) — 인계 방식

- 원문: 「다른 클로드가 보는 설명서를 만들 때 해당 클로드는 다른 서버에 상주하고 있어서 현 서버의 실제 디렉토리 내부를 볼 수 없어. 다만 결과물을 만들어주면 전달하는 것은 가능해. 따라서 중간 중간 결과를 .tgz 파일로 복사해서 넣어주면 내가 그걸 전달할게. 그리고 그에 맞게 설명의 내용도 수정해줘.」
- 조치:
  - exp/report/make_handoff.sh 를 만들었다. 실험 서버의 `~/jsw/handoff/ksc2026_handoff_<시각>[_라벨].tgz` (이름의 시각은 KST. 16:03·16:05 KST 에 만든 첫 묶음 2 개(ksc2026_handoff_20261008_0703_mid.tgz, ksc2026_handoff_20261008_0705_mid.tgz)는 이름의 시각이 UTC 였고 지웠다) 와 `LATEST.tgz` 링크를 생성한다.
  - 이 파일에 H 절(묶음 사용법)을 추가하고 0 절을 묶음 기준으로 고쳤다.
  - 메모리 handoff-tgz-for-remote-claude.md 를 추가했다.
  - 묶음은 실험 진행 중(중간)과 끝난 뒤(최종)에 만든다.

### 1.9 여덟 번째 메시지 (2026-10-08 16:08 KST) — 시각 기준

- 원문: 「시간 계산은 KST로 변환해서 적용해줘. 그리고 보고 및 답변할 때도 KST를 기준으로 알려줘. 서버 시계 자체는 바꾸지말고 변환해서 알려주기만 해줘.」
- 조치:
  - 서버 시계·시간대는 그대로(UTC) 둔다.
  - 이 파일의 서술 부분 시각을 모두 KST 로 변환했다(UTC+9, 자동 변환 74 곳 + 손 검토). 원문 로그·파일 내용을 인용할 때도 시각은 KST 로 바꾸고 원문 UTC 표기를 함께 적는다(사용자 지시 1.10).
  - 자동 생성 결과 절(11)·docx·묶음 이름은 KST 로 쓰도록 생성기를 고쳤다.
  - 메모리 kst-times.md 를 추가했다.

### 1.10 아홉 번째 메시지 (2026-10-08 16:09 KST)

- 원문: 「handoff 파일에 쓰는 시간도 KST로 적어줘.」
- 조치(make_handoff.sh, make_md_results.py):
  - 묶음 이름·README·state.txt 의 시각을 KST 로 쓴다. tmux 생성 시각은 epoch 에서 KST 로 변환한다.
  - run_all 로그 끝부분은 KST 로 변환해 싣는다. 전체 로그의 KST 변환본은 server_state/run_all_<EXP>.KST.log 로 넣는다.
  - git_log.txt 는 `TZ=Asia/Seoul git log --date=iso-local` 로 만든다.
  - 이 파일 11 절의 run.log 인용 줄은 시각을 KST 로 바꾼다.
  - 메모리 노트의 시각도 KST 로 바꿨다.
  - repo/ 안의 원자료 파일(run.log, meta.txt, kernel.log, fio 로그)은 측정 기록이라 수정하지 않는다(UTC 그대로).
  - UTC 이름으로 만든 16:05 KST 묶음(ksc2026_handoff_20261008_0705_mid.tgz)은 지우고 KST 이름으로 다시 만들었다.

### 1.11 열 번째 메시지 (2026-10-08 17:23:50 KST)
- 원문: 「지금까지 나온 상태를 handoff 파일에 갱신해줘」
- 조치: 10.3 절 17:24 항목(postexp 묶음).

### 1.12 열한 번째 메시지 (18:24:04 KST)
- 원문: 「작업 현황 알려줘. 한국어로 해줘.」
- 배경: 그 전 보고 일부를 Claude 가 영어로 썼다(한국어 전용 지시 위반). 사과하고 한국어로 현황을 보고했다. 그 뒤 모든 응답은 한국어다.

### 1.13 열두 번째 메시지 (19:02:11 KST) — 그래프 위치
- 원문: 「실험 결과를 그래프로 모두 보고 싶은데 결과물 어디 있어?」
- 조치:
  - 위치를 안내했다. 주 데이터셋 그림은 results/main3x3_20261008/analysis/(analyze.py, 15 장)와 plots/(plot.py all, 25 장)에, 보조 데이터셋 그림은 results/main_20261008/ 의 같은 두 폴더에 있다.
  - exp/make_gallery.py 를 새로 만들었다. 한 실험의 모든 PNG 를 data URI 로 넣은 HTML 한 파일을 만든다(주제별 6 묶음, 그림마다 한국어 설명). 사용법: `python3 make_gallery.py results/<EXP> [out.html]`, 기본 출력은 results/<EXP>/gallery_<EXP>.html 이다.
  - main3x3(40 장, 6.6 MB)과 main(40 장, 10.4 MB)의 갤러리를 만들어 사용자에게 보냈다.
  - 갤러리 HTML 은 크고 PNG 와 내용이 겹쳐 git 에 넣지 않았다. 다만 묶음의 repo/ 는 작업 트리 전체라 들어간다.

### 1.14 열세–열여섯 번째 메시지 (19:10–19:17 KST) — base 와 wbuffix 의 차이를 다시 물음
- 원문(시간순):
  - 19:10:03 「base가 write buffer가 차기 전에 바로바로 보내는 거고 wbuffer가 write buffer가 모두 채워지면 보내는 거라고 했었지?」
  - 19:13:53 「뭔 소리야?」
  - 19:15:13 「그럼 내 말이 맞는거 아니야? base는 오면 바로바로 보내버리고 wbuffix는 다 찰 때까지 기다렸다 보내는거잖아?」
  - 19:17:34 「아니 왜 앞 뒤가 달라. 아까는 base가 4K가 들어와서 write buffer에 1칸 차면 나머지를 빈 값으로 채워서 4칸이 나간다고 말한다매. … 반면 wbuffix는 4K 쓰기를 16K가 다 채워 질때까지 기다렸다 나가는거니까 호스트가 기다려야 하는거고.」
- Claude 가 코드(conv_ftl.c, io.c, ssd.c)로 다시 확인해 설명한 사실이다. 다음 Claude 도 이렇게 설명할 것.
  - NAND 로 보내는 시점은 두 모델이 같다. 매핑 단위 페이지가 모여 oneshot page(32 KiB)가 차면 프로그램한다(conv_ftl.c 의 last_pg_in_wordline 분기). 호스트가 완료를 받는 시점도 같다(early completion: 버퍼에 들어가면 완료).
  - 매핑 16K 에서 4K 쓰기 하나가 오면 두 모델 모두 곧바로 16K 매핑 페이지 하나를 새로 배정해 통째로 쓴 것으로 계산한다. 다음 4K 가 같은 16K 단위로 와도 합치지 않는다. 이는 NVMeVirt 원본 동작이며 랜덤·순차 모두 같다.
  - 나머지 12K 는 「빈 칸」이 아니다. FTL 은 시간 모델이고, 데이터는 별도 메모리에 LBA 위치 그대로 저장된다. 실제 SSD 라면 나머지를 옛 데이터로 채우는 RMW 읽기가 필요하지만, 그 읽기는 모델에 없다.
  - 두 모델에서 다른 것은 쓰기 버퍼 장부뿐이다.
    - base 는 4K 를 쓰면 4K 를 할당하고, 16K 페이지가 프로그램되면 16K 를 반납한다. 장부상 빈자리가 쓸 때마다 늘어 버퍼가 차지 않으므로, 호스트를 기다리게 하지 못한다(back-pressure 없음).
    - wbuffix 는 처음부터 16K 를 할당하므로 장부가 맞는다. NAND 가 밀리면 버퍼(1 MiB)가 실제로 차고, 호스트가 기다린다.
  - 사용자의 이해 중 「wbuffix 는 호스트가 기다린다」는 맞다. 하지만 「버퍼(또는 16K)가 다 찰 때까지 모았다가 보낸다」는 틀리다. wbuffix 는 버퍼가 꽉 찼을 때 빌 때까지 기다리게 할 뿐이다.
  - 근거 실측: wbuffix 의 WAF_total 은 bs ≥ 매핑 3.1–3.5 인데, 16K/4K 8.8, 32K/4K 17.1 이다. wbuffix 가 4K 쓰기를 모아 보냈다면 이 칸도 3 근처여야 한다.
  - 앞선 설명의 주차장 비유(「들어올 때 1 칸, 나갈 때 4 칸으로 센다」)는 장부를 말한 것이었다. 그런데 실제 데이터를 빈 값으로 채워 내보낸다는 뜻으로 오해를 낳았다. 비유보다 위 사실로 설명하는 편이 낫다.

### 1.15 열일곱 번째 메시지 (19:20:15 KST) — base 를 왜 돌렸나
- 원문: 「그럼 base는 버그가 있는 버전 아니야? 이건 내가 실험에서 보려고 한게 아닌거 같은데 왜 돌린거야?」
- Claude 의 답:
  - 맞다, base 는 버그가 있는 버전이다.
  - 돌린 이유: 원본 코드에 지정 값만 바꾼 것을 「요청한 설정 그대로」로 보았다. 그래서 시뮬레이터 코드 수정을 혼자 결정하지 않으려고 두 변형을 모두 돌렸다.
  - 잘못: 실험 대상을 바꾸는 결정인데 시작 전에 묻지 않았다. 시작한 뒤 진행 보고(14:29 KST 「base 108 회 중 8 회째」)로만 알렸다.
  - 영향: 최종 결과(main3x3)에는 base 가 없다. base 는 보조 데이터셋의 21 회뿐이다(약 27 분, 14:20–14:47).
  - 처리 방안 두 가지를 제시했다: (1) 보조 자료로 남김(원본 NVMeVirt 버그의 근거), (2) 문서·저장소에서 빼거나 「사용하지 않음」으로 표시. 사용자는 아직 답하지 않았다. 그래서 지금은 보조 자료로 남아 있다.
- 다음 Claude 에게: 실험 대상·설계를 바꾸는 결정은 반드시 먼저 사용자에게 묻는다.

### 1.16 열여덟 번째 메시지 (19:53:01 KST) — 순차 쓰기 실험 요청
- 원문: 「sequential write를 할 때도 동일하게 mapping unit 4k, 16k, 32k, bs 4k, 16k, 32k로 나눠서 측정해볼 수 있어?」
- Claude 는 먼저 설계를 알렸다. 모델은 wbuffix 만, 매핑·bs 3×3·3 회, 나머지는 랜덤 쓰기와 같게 하고 fio 만 rw=write 로 바꾼다. 그리고 다음 세 가지를 물었다(AskUserQuestion; 19:54:53 KST 답).
  - 「bs < 매핑 단위인 순차 쓰기에서, NVMeVirt가 작은 쓰기를 합치지 않는 문제를 어떻게 할까요?」
    - 선택지: 현재 모델 그대로(추천) / 병합 기능 추가 / 둘 다 측정
    - 답: **둘 다 측정**
  - 「페이지 캐시 drop은 어떻게 할까요?」
    - 선택지: nodrop만(추천) / drop/nodrop 교대 / drop만
    - 답: **nodrop만**
  - 「sudo 규칙을 다시 설치해야 합니다. 앞서 알려주신 비밀번호로 다시 설치하고, 실험이 끝나면 지워도 될까요?」
    - 답: **그렇게 진행**
- 시간 안내 착오: 질문에 「nodrop 27 회 약 1 시간 5 분」이라고 적었다. 실제로는 회차당 약 71 s 라 27 회는 약 32 분, 두 모델 54 회는 약 64 분이다. 20:13 KST 보고에서 정정했다.

### 1.17 열아홉·스무 번째 메시지 (19:56:26 / 19:57:55 KST) — 에뮬레이터 한계 확인
- 원문:
  - 「NVMeVirt 에뮬레이터로는 순차 쓰기나 랜덤 쓰기나 동일하게 페이지를 안 채운다는거야? 그러니까 예를 들어 mapping unit을 16k로 설정하고 쓰기가 4k면 원래는 write buffer가 16k가 채워지면 비로소 페이지에 채워지는데, 에뮬레이터로는 4k가 들어오면 바로 새 페이지에 4k만큼 쓰고 나머지 12k를 빈 칸으로 채운다는거야?」
  - 「에뮬레이터의 한계라는거지?」
- 답:
  - 맞다. 순차·랜덤 모두 4K 가 오면 곧바로 16K 페이지 하나를 통째로 쓴 것으로 계산한다(1.14 절).
  - 실제 SSD 는 순차 쓰기에서 버퍼로 합친다. 랜덤 쓰기에서는 같은 16K 로 이어서 오는 쓰기가 없으므로, 실제 SSD 도 16K 를 새로 쓴다. 이때 RMW 읽기가 추가되는데, NVMeVirt 에는 이 읽기가 없다.
  - 그래서 NVMeVirt conventional 모델의 한계는 두 가지다. (1) 작은 쓰기 병합이 없다(순차 쓰기에 결정적). (2) RMW 읽기가 없다(랜덤 쓰기에서 불이익이 실제보다 조금 작다).
  - 원본은 매핑 4K 고정이라 쓰기가 매핑 단위보다 작을 일이 없었다. base 버그도 같은 이유로 생겼다.
  - 논문에는 모델 한계로 적고, merge 모델 결과를 함께 보이면 된다.

### 1.18 스물한 번째 메시지 (20:17:55 KST) — 「sudo 설치했어」
- 배경:
  - 20:0x KST 에 Claude 가 대화에 있던 비밀번호로 sudoers 를 설치하려 했다(`sudo -S install …`).
  - Claude Code 자동 모드 분류기가 [Credential Leakage] 로 막았다.
  - Claude 는 우회하지 않고 사용자에게 설치 명령을 요청했다: `sudo install -m 0440 -o root -g root /home/dccearth/jsw/nvmevirt/exp/report/nvmevirt-exp.sudoers /etc/sudoers.d/nvmevirt-exp`
- 결과:
  - 사용자가 설치했다. /etc/sudoers.d/nvmevirt-exp 파일 시각은 20:17 KST 다.
  - Claude 가 `sudo -n -l` 로 확인했다. 규칙의 10 개 명령 중 8 개(insmod, rmmod, fio, dmesg, tee /dev/kmsg, tee drop_caches, tee nomerges, chown)가 모두 허용된다. 나머지 nvme·cat /proc/iomem 도 env_before 수집(sudo -n nvme list, sudo -n cat /proc/iomem)에서 실행되었다.
- 규칙 내용은 6.4 절이다. 새 경로의 chown 과 `tee /sys/block/nvme1n1/queue/nomerges` 가 추가되었다.
- 실험이 끝나면 제거한다. `sudo rm` 은 규칙에 없으므로 사용자에게 요청해야 한다.

### 1.19 스물두 번째 메시지 (21:34:20 KST) — 「지웠어」
- 순차 쓰기 실험 후 sudoers 제거 요청(21:3x)에 대한 답이다. 10.4 절의 21:34:17 항목에 확인 결과가 있다.

### 1.20 스물세 번째 메시지 (22:08:06 KST) — 랜덤 쓰기 8K·64K 추가와 묶음 갱신
- 원문: 「randwrite에 대해 8k, 64k에 대한 실험도 함께 진행해서 마찬가지로 보고서도 작성하고, 클로드한테 전달할 LATEST.tgz도 계속 갱신해줘. 다 만들면 알려주고, 그러면 내가 클로드한테 전달할게.」
- Claude 는 정해 둔 설정을 먼저 알렸다. wbuffix 만 쓰고(base 는 버그, merge 는 랜덤에서 wbuffix 와 같음 −0.7 %), nodrop 만 쓰며, 나머지는 주 데이터셋과 같다. 그다음 다음 두 가지를 물었다(AskUserQuestion; 22:09:12 KST 답).
  - 「8K·64K를 어디에 추가할까요?」
    - 선택지: 매핑·bs 둘 다(추천, 5×5) / 매핑 단위만(5×3) / bs만(3×5)
    - 답: **bs만**
  - 「기존 3×3 조합(주 데이터셋 nodrop 값)은 어떻게 할까요?」
    - 선택지: 모두 새로 측정(추천) / 새 조합만 측정, 기존 값 재사용
    - 답: **새 조합만 측정, 기존 값 재사용**
- 결과적으로 매핑은 32K 까지라, 64K 매핑의 flash page 변화(8.2 절)는 이번 실험과 무관하다.
- 묶음: 사용자가 다른 Claude 에게 넘길 ~/jsw/handoff/LATEST.tgz 를 계속 갱신하고, 다 되면 알린다.

### 1.21 스물네·스물다섯 번째 메시지 (22:11:27 / 22:12:09 KST)
- 22:11:27 「sudo 규칙 다시 설치했어」: /etc/sudoers.d/nvmevirt-exp 파일 시각은 22:11:08 KST 다. Claude 가 sudo -n -l 로 확인한 뒤, 22:11:48 KST 에 실험을 시작했다.
- 22:12:09 「컴퓨터 잠깐 꺼야 하는데, 문제 있어?」
  - 이 메시지는 Claude 가 작업하는 도중에 왔다. Claude 는 22:16 KST 진행 보고 끝에 「PC 를 끄셨다가 다시 켜시면 push 를 위해 ssh -A 로 접속해 주세요」라고만 답했다. 「문제 있어?」에 대한 직접적인 답(실험은 서버 tmux 에서 계속되므로 사용자 PC 를 꺼도 괜찮다)은 하지 않았다.
  - 실제로 실험은 서버 tmux(ksc2026rbs)에서 22:32:55 KST 까지 중단 없이 돌았다.

### 1.22 스물여섯 번째 메시지 (22:36:14 KST) — 「켰어」
- 사용자가 PC 를 다시 켰다. 이때 서버에는 forwarded ssh-agent 소켓이 없었다(`ls /tmp/ssh-*/agent.*` 결과 없음, `who` 결과 없음). 앞의 소켓(/tmp/ssh-CpMF3ibMgI/agent.97990)은 사용자 SSH 세션이 끝나며 사라졌다.
- Claude 는 push 를 위해 `ssh -A` 접속과 sudoers 제거(`sudo rm /etc/sudoers.d/nvmevirt-exp`)를 요청했다(22:4x KST 보고).

### 1.23 스물일곱 번째 메시지 (23:08 KST) — 「지웠어」
- 사용자가 sudoers 규칙을 지웠고, 같은 때 `ssh -A` 로 접속했다(pts/0, 23:08 KST; agent 소켓 /tmp/ssh-WUnQXYwLiz/agent.172999). 확인 결과는 10.5 절에 있다.

---------------------------------------------------------------------------------------------------

## 2. 연구 배경과 사전 자료

### 2.1 KSC2026 폴더 (/home/dccearth/jsw/KSC2026)

- `연구 계획 흐름.docx`:
  - 배경: SSD 의 FTL 매핑(lpn→ppn)은 SRAM/DRAM 에 둔다. 매핑 단위는 512B → 4K → 16K(고용량 SSD)로 커져 왔다. 1TB SSD 는 DRAM 이 약 1GB 필요하다. 16/32/…/128/256TB 를 4k 매핑으로 유지하면 DRAM 이 256GB 까지 필요하고, 16K 매핑이면 64GB 로 줄어든다.
  - 활용: RocksDB(WAL = 16KB 미만 작은 IO, SST = blocksize 설정 4k→16k 로 쉽게 조정)
  - 수행: nvmevirt 설치 → 다른 논문들의 config 조사 → nvmevirt 에서 ftl mapping size 를 바꿀 수 있는지·기본값 확인 → fio(libaio) 로 성능 측정 「(4k mapping ssd) randwrite 4k, 8k, 16k, 32k, 64k, 128k → throughput(BW), clat」「(16k/32k mapping ssd) 같음」 → 중간에 넣은 config 값을 잘 적기.
  - 이 문서에는 서버 로그인 정보(IP, 계정, 비밀번호)가 적혀 있다. 이 파일에는 옮기지 않는다.
- 논문 PDF: atc24-hwang.pdf, FTL 매핑 단위에 따른 성능 분석 연구.pdf, Power_analysis.pdf, SFTL.pdf (배경 자료. 이 실험에서 직접 쓴 값은 없다).
- `산출물/` — 이 세션 이전(2026-10-07)에 만든 NVMeVirt 설정조사 결과물: NVMeVirt_설정조사_보고서.docx/.pdf, _요약.pptx, _데이터.csv, _데이터_상세.csv, backup-20261007-1113/. 핵심 내용:
  - NVMeVirt 를 쓴 논문 15 편을 조사했고, 매핑 단위를 바꾼 논문은 0 편이다(공개 수정본 5 개도 4 KB).
  - 추천 설정: 970 Pro 기본 묶음(채널 8 · LUN 2 · plane 1 · page 32 KB · tR 36 µs · tPROG 185 µs · tBERS 0 · 채널 800 MB/s · PCIe 3,360 MB/s · OP 7 % · 쓰기 버퍼 1 MiB · GC line ≤ 2) + 용량 64 GiB + 블록 2 MiB(BLKS_PER_PLN 2048) + 코어 5(디스패처 1 + 워커 4) + fio libaio randwrite bs 4k–128k QD32 jobs 1, 사전 채움 후 300 s + 커널 5.15 이상.
  - 매핑 단위를 바꾸는 자리: ssd.c 73 행 `secs_per_pg = 4096 / LBA_SIZE`. 4 KB 를 가정한 다른 자리: ssd.c 355(쓰기 버퍼 지연을 4 KB 단위로 계산), 394(NAND 읽기가 정확히 4096 B 일 때만 4 KB 읽기 지연), conv_ftl.c 867(4 KB 이하 읽기에만 4 KB 펌웨어 지연). 모델에 없는 것: 부분 쓰기의 RMW 읽기 지연, 지우기 지연(기본 0).
  - 보고서는 쓰기 버퍼 과다 반환 문제(8.1 절)는 다루지 않았다. 이 세션에서 새로 찾은 것이다.

### 2.2 이 세션 이전에 서버에 있던 작업 흔적 (참고만, 이번 실험에 쓰지 않음)

- /home/dccearth/jsw/before.txt, after.txt — insmod 전후 `ls -l /dev/nvme*` (after 에 /dev/nvme1, /dev/nvme1n1 이 생김). 2026-10-07 작성. 15:4x 확인 때 두 파일이 /home/dccearth/jsw 에 없었다(디렉터리 mtime 15:42). Claude 가 지운 것이 아니며 사용자가 정리한 것으로 보인다. 내용(세션 시작 때 읽음):
  - before.txt: /dev/nvme0 (241,0), /dev/nvme0n1 (259,0), nvme0n1p1 (259,1), nvme0n1p2 (259,2), /dev/nvme-fabrics (10,261) — 날짜 Sep 30/Oct 1
  - after.txt: 위 + /dev/nvme1 (241,1, Oct 7 21:28 KST), /dev/nvme1n1 (259,3, Oct 7 21:28 KST) (ls 시각을 KST 로 변환)
- /home/dccearth/jsw/exp/ (이전 실험 폴더, KSC2026 밖에 있었다. 이번 실험과 별개였고, 사용자 지시(1.6)로 17:06 KST 에 삭제했다 — 10.3 절):
  - jobs/randwrite.fio, results/iodepth_test/ (iodepth 1–128, 매핑 4K, bs 4K, ramp_time 10, runtime 60, 모듈 재적재 없이 연속 실행 → GC 정상 상태, filename=/dev/nvme1n1, 2026-10-08 11:33–11:41 KST). iodepth_summary.csv 에 따르면 QD32 에서 64,041 IOPS, 250.2 MiB/s, clat 평균 498.8 µs, p99 14,352 µs이고, QD 1–128 모두 약 59–66K IOPS 다. 이 폴더는 사용자 지시(1.6)로 17:06 KST 에 삭제했으므로, 삭제 전에 CSV 전문을 여기에 옮겨 두었다:
```
iodepth,n,iops,iops_std,bw_MiBps,bw_MiBps_std,clat_mean_us,clat_mean_us_std,clat_p99_us,clat_p99_us_std
1,1,63305.478242,0.0,247.28702354431152,0.0,14.575670484,0.0,9.024,0.0
2,1,58896.25754,0.0,230.06357097625732,0.0,32.815967144000005,0.0,80.384,0.0
4,1,66315.294745,0.0,259.04431533813477,0.0,59.271949227,0.0,173.056,0.0
8,1,63891.351441,0.0,249.57604694366455,0.0,124.220571154,0.0,236.544,0.0
16,1,64332.477792,0.0,251.2997179031372,0.0,247.75240136600002,0.0,11730.944,0.0
32,1,64040.532658,0.0,250.1603479385376,0.0,498.76462219800004,0.0,14352.384,0.0
64,1,64377.054098,0.0,251.4769687652588,0.0,993.2828929670001,0.0,15400.96,0.0
128,1,64931.726908,0.0,253.64782428741455,0.0,1970.194035148,0.0,16580.608,0.0
```
    그때 쓴 jobs/randwrite.fio: [global] filename=${DEV} ioengine=libaio direct=1 rw=randwrite time_based runtime=60 ramp_time=${RAMP_TIME} iodepth=${IODEPTH} numjobs=1 group_reporting=1 / [randwrite] bs=${BS} (JSON 의 job options: ramp_time 10).
  - run_mapunit_test.sh, patch_nvmevirt.sh, plot_mapunit.py, mapunit_exp.tar.gz — 예전 Claude 세션이 만든 매핑 단위 실험 스크립트(MAPS 4k 16k 32k, fob/steady 모드). 이번 실험에서는 쓰지 않았다(설계 참고만).
  - .venv (numpy, matplotlib)
- ~/.bash_history 기록(2026-10-06–07):
  - 사용자가 Sangwon8799/nvmevirt(예전 저장소)에 map4k·map8k·map16k·map32k·map64k·map128k 브랜치와 "init: Block Size = 2MiB (NVMeVirt Capacity = 12GiB)" 커밋을 만들었고, GRUB 를 memmap=12G$12G isolcpus=3-5 로 설정했다(update-grub, reboot). `sudo insmod ./nvmev.ko memmap_start=12G memmap_size=12G cpus=3,4,5` 로 시험했다.
  - 그 저장소는 이번 세션 시점에 공개 API 에서 보이지 않았고, 사용자 지시(「이전 기록은 잊어」)에 따라 새 저장소로 대체되었다. 예전 저장소의 로컬 사본(당시 경로 /home/dccearth/jsw/nvmevirt)도 이번 세션 시작 때 이미 없었다. 지금 같은 경로에 있는 것은 17:06 KST 에 /home/dccearth/jsw/KSC2026/nvmevirt 에서 옮겨 온 이번 실험 저장소(묶음의 repo/)이며, 예전 저장소와는 다르다.
  - ~/.ssh 의 jsw_github_key 는 사용자가 지웠다(현재 ~/.ssh 에는 authorized_keys, 빈 config, known_hosts 만 있다).

---------------------------------------------------------------------------------------------------

## 3. 서버 환경 (exp/results/main_20261008/env_before/ 스냅샷 근거)

- 호스트명 dccearth. 메인보드 Micro-Star International Co., Ltd. MAG B760M MORTAR (MS-7E01), BIOS M.30 (05/16/2023).
- CPU: 13th Gen Intel Core i5-13600K. OS 에 보이는 CPU 는 6 개(0–5), 코어당 스레드 1, 소켓 1, NUMA 노드 1. max 5100 MHz, min 800 MHz. L1d 288 KiB, L2 12 MiB, L3 24 MiB. 원래 13600K 는 P 6 + E 8 이지만 OS 에는 6 개만 보인다(BIOS 에서 E-core/HT 를 끈 것으로 추정 — 확인 안 함).
- 메모리: DDR5-5600. Controller0-DIMMA2 8 GB Samsung M323R1GB4DB0-CWMOL, Controller1-DIMMB2 16 GB Samsung M323R2GA3DB0-CWMOL (DIMMA1·DIMMB1 은 비어 있음). 합계 24 GB, 최대 128 GB, 슬롯 4. (sudo dmidecode -t memory, env_before/12_dimm.txt — 실험 시작 후 14:2x 에 기록. 정적 정보다.)
- free -h: total 11Gi (memmap 으로 12 GiB 가 빠짐), swap 8 GiB.
- 물리 주소 맵(/proc/iomem, 4 GiB 위): 100000000-2ffffffff System RAM (4–12 GiB) / **300000000-5ffffffff Reserved (12–24 GiB, NVMeVirt 저장 공간)** / 600000000-67f7fffff System RAM (24–25.99 GiB, PCI hole 재배치분). e820 user map: [mem 0x0000000300000000-0x00000005ffffffff] reserved (스냅샷 아님 — 14:06 KST 에 sudo dmesg 로 직접 확인; env_before/05_memory.txt 의 dmesg grep 은 링 버퍼가 덮여 비어 있음).
- OS Ubuntu 24.04.4 LTS (noble). 커널 6.8.0-142-generic (#142-Ubuntu SMP PREEMPT_DYNAMIC, 빌드 시각 2026-09-02 23:24:27 KST; /proc/version 원문 표기는 "Wed Sep 2 14:24:27 UTC 2026"), x86_64-linux-gnu-gcc-13 13.3.0 로 빌드됨.
- 커널 명령줄: `BOOT_IMAGE=/boot/vmlinuz-6.8.0-142-generic root=UUID=bb1b37f9-0806-4044-a2bf-5ff988ecb286 ro memmap=12G$12G isolcpus=3-5`
- /etc/default/grub: `GRUB_CMDLINE_LINUX="memmap=12G\\\$12G isolcpus=3-5"`, `GRUB_CMDLINE_LINUX_DEFAULT=""`. /sys/devices/system/cpu/isolated = 3-5.
- CPU 주파수: intel_pstate active(HWP), 모든 CPU 가 governor powersave · EPP balance_performance · no_turbo=0 (터보 켜짐), 800–5100 MHz. 바꾸지 않았다.
- THP: always [madvise] never. kernel.dmesg_restrict=1, kptr_restrict=1, numa_balancing=0, vm.swappiness=60. kernel.printk = 4 4 1 7 (콘솔 loglevel 4 → KERN_ERR 가 tty0 콘솔에 출력된다). /proc/consoles: tty0. systemd-journald 가 /dev/kmsg 를 읽는다.
- 시스템 디스크: /dev/nvme0n1 Samsung SSD 980 PRO 500GB (FW 3B2QGXA7). nvme0n1p1 1G /boot/efi, nvme0n1p2 464.7G / (루트). 실험 스크립트는 이 디스크에 절대 쓰지 않도록 검사한다.
- 소프트웨어 버전: fio-3.36 (deb 3.36-1ubuntu0.1), libaio1t64 0.3.113-6build1.1, gcc 13.3.0 (gcc-13 13.3.0-6ubuntu2~24.04.1), GNU Make 4.3 (4.3-4.1build2), linux-headers-6.8.0-142-generic 6.8.0-142.142, nvme-cli 2.8 (libnvme 1.8), util-linux 2.39.3, Python 3.12.3, git 2.43.0, GNU bash 5.2.21, awk = GNU Awk 5.2.1. 시스템 python3 에는 python-docx·pypdf 가 없다. exp/.venv 의 버전은 exp/requirements.txt: numpy 2.5.3, matplotlib 3.11.2, python-docx 1.2.0, lxml 6.1.3, pillow 12.3.0, contourpy 1.4.0, cycler 0.12.1, fonttools 4.66.1, kiwisolver 1.5.1, packaging 26.3, pyparsing 3.3.3, python-dateutil 2.9.0.post0, six 1.17.0, typing_extensions 4.16.0.
- 없는 도구: gh, pandoc, libreoffice/soffice, pdftoppm, node/npm. LibreOffice AppImage(still, 291 MB)를 scratchpad 에 받아 두었다: /tmp/claude-1000/-home-dccearth-jsw/13edeb42-0011-48bf-800d-a7f7e0251b76/scratchpad/lo/LibreOffice-still.AppImage (docx 렌더링 확인용).
- Claude Code 의 Bash 도구 셸에서는 `grep` 이 ugrep 래퍼 함수다(패턴이 '-' 로 시작하면 옵션으로 해석되어 실패한다). 스크립트(bash script.sh)에서는 /usr/bin/grep(GNU)이 쓰이므로 영향이 없다.

---------------------------------------------------------------------------------------------------

## 4. 저장소 (실험 당시 /home/dccearth/jsw/KSC2026/nvmevirt → 17:06 KST 이후 /home/dccearth/jsw/nvmevirt)

- remote: origin = git@github.com:Sangwon8799/nvmevirt.git (push 용), upstream = https://github.com/snu-csl/nvmevirt.git
- 커밋(시간순):
  - 61c90f7758cbd9545b4a4727e89377bf88eab060 — upstream main HEAD, 2026-05-21 11:05:11 +0900 "Merge pull request #72 from duckhanson/fix/zns-append-return-slba". 모듈 버전 문자열 "NVMeVirt: Version 1.10 for >> Samsung 970 Pro SSD <<". upstream 에는 multi-instance 브랜치도 있다(사용 안 함).
  - d5086101c43d0414aa073579dbae4c7516f832a1 — 2026-10-08 13:54:03 "Move NVMeVirt sources into nvmevirt/ subdirectory" (순수 rename)
  - c02b9fda3aefeaab306a3bd6f00853b240a04c6c — 14:20:15 "nvmevirt: KSC2026 mapping-unit configuration" (Kbuild, ssd.c, ssd_config.h, conv_ftl.c, conv_ftl.h)
  - 5769378d46821c45595585c932522e4f76538fc6 — 14:20:15 "exp: scripts for the KSC2026 mapping-unit experiment". 보조 데이터셋 main_20261008 의 모듈 빌드(14:20; 이 바이너리를 주 데이터셋까지 그대로 썼다)와 base 1–21 회차(DONE 20 + map32k_bs16k_r1 FAILED)는 이 커밋에서 실행되었다(exp/results/main_20261008/base/git_head.txt).
  - 949ae38 (원래 2a462a3a518915e37fa313716bc9721801501e28) — 14:49:13 "exp: keep going when a run fails; plot tool; report generators". main_20261008 wbuffix 53 회차는 이 커밋(옛 해시 2a462a3)에서 실행되었다(wbuffix/git_head.txt, 각 meta.txt 의 git_head).
  - e598e75 (원래 a93ef76bbf990eafd1d0a5a9484a27a1b709ed9d, 그 전 1d6cd036893f06bfe8aa8f6bb4327239bc4b720f) — 작성 16:00:07, 재작성 16:04:44 "exp: final 3x3 design with OS page-cache comparison". 주 데이터셋 main3x3_20261008 54 회차는 이 코드로 실행되었다(meta.txt: 처음 4 회 1d6cd03, 나머지 50 회 a93ef76).
  - 해시가 두 번 바뀐 이유(모두 첫 push 전, 코드는 같고 이 파일만 다름): 16:04 KST 1d6cd03 → a93ef76 (이 파일의 credential 문자열 줄), 18:3x KST 2a462a3 → 949ae38·a93ef76 → e598e75 (이 파일 머리말의 사용자 Claude 계정 이메일 제거). 「갱신 이력」 참고.
  - 그 뒤 결과·문서·생성기·analyze.py 수정 커밋과 태그 ksc2026-final 은 10.3 절 끝에 적는다.
- 커밋 작성자: Sangwon8799 <ekfghfl@naver.com> (전역 git config), 메시지 끝에 "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>".
- 저장소에 넣지 않는 것(exp/.gitignore): modules/*/*.ko (SHA256SUMS 는 넣음), .venv/, __pycache__/, results/*/gallery_*.html(make_gallery.py 결과; 커밋 a86fc87 부터). nvmevirt/.gitignore 는 원본 그대로(`.*`, *.ko, *.o 등). .git/info/exclude 에 upstream_tmp/ 를 넣었다.
- /home/dccearth/jsw/KSC2026/nvmevirt/upstream_tmp/ — 감사 워크플로가 읽은 원본 사본(커밋 61c90f7, 수정 없음). 저장소에는 넣지 않았고(.git/info/exclude), 17:06 KST 에 삭제했다(10.3 절).
- 서버에서 push 하려면 `SSH_AUTH_SOCK=$(ls /tmp/ssh-*/agent.* | head -1) git push origin main`. 사용자의 SSH 세션이 연결되어 있어야 한다.

---------------------------------------------------------------------------------------------------

## 5. NVMeVirt 수정 내역 (정확한 내용)

원본 대비 바뀐 파일은 nvmevirt/Kbuild, ssd.c, ssd_config.h, conv_ftl.c, conv_ftl.h 다섯 개다. 정확한 diff 는 `git diff d508610 5769378 -- nvmevirt` 로 볼 수 있다.

### 5.1 Kbuild
- `CONFIG_NVMEVIRT_NVM := y` → 주석 처리. `#CONFIG_NVMEVIRT_SSD := y` → `CONFIG_NVMEVIRT_SSD := y` (BASE_SSD=SAMSUNG_970PRO, ssd.o conv_ftl.o pqueue/pqueue.o channel_model.o)
- 추가:
```
MAPPING_UNIT ?= 4096
ccflags-$(CONFIG_NVMEVIRT_SSD) += -DMAPPING_UNIT=$(MAPPING_UNIT)
WBUF_FIX ?= 0
GC_STATS ?= 0
ccflags-$(CONFIG_NVMEVIRT_SSD) += -DKSC_WBUF_FIX=$(WBUF_FIX) -DKSC_GC_STATS=$(GC_STATS)
```
- `make MAPPING_UNIT=16384 GC_STATS=1 [WBUF_FIX=1]` 처럼 명령줄에서 준 값은 MAKEFLAGS 로 커널 빌드 하위 make 에 전달된다. 빌드 전에 매번 `make clean` 을 한다(build_modules.sh).

### 5.2 ssd_config.h (SAMSUNG_970PRO 블록 안)
```
#ifndef MAPPING_UNIT
#define MAPPING_UNIT (4096)
#endif
#if (MAPPING_UNIT > 32768)
#define FLASH_PAGE_SIZE (MAPPING_UNIT)
#else
#define FLASH_PAGE_SIZE KB(32)
#endif
#define ONESHOT_PAGE_SIZE (FLASH_PAGE_SIZE * 1)      (원본과 같은 식)
#define BLKS_PER_PLN (384)                            (원본 8192)
```
나머지는 원본 그대로다: NR_NAMESPACES 1, NS_SSD_TYPE_0 CONV, MDTS 6, CELL_MODE MLC, SSD_PARTITIONS 4, NAND_CHANNELS 8, LUNS_PER_NAND_CH 2, PLNS_PER_LUN 1, BLK_SIZE 0, MAX_CH_XFER_SIZE KB(16), WRITE_UNIT_SIZE 512, NAND_CHANNEL_BANDWIDTH 800, PCIE_BANDWIDTH 3360, NAND_4KB_READ_LATENCY_LSB/MSB 35760∓6000 ns, NAND_READ_LATENCY_LSB/MSB 36013∓6000 ns, NAND_PROG_LATENCY 185000 ns, NAND_ERASE_LATENCY 0, FW_4KB_READ_LATENCY 21500, FW_READ_LATENCY 30490, FW_WBUF_LATENCY0 4000, FW_WBUF_LATENCY1 460, FW_CH_XFER_LATENCY 0, OP_AREA_PERCENT 0.07, GLOBAL_WB_SIZE = NAND_CHANNELS*LUNS_PER_NAND_CH*ONESHOT_PAGE_SIZE*2, WRITE_EARLY_COMPLETION 1, LBA_BITS 9.

### 5.3 ssd.c
- 73 행 `spp->secs_per_pg = 4096 / LBA_SIZE; // pg == 4KB` → `spp->secs_per_pg = MAPPING_UNIT / LBA_SIZE;`
- ssd_init_params() 끝에 다음 로그를 추가했다. 회차마다 dmesg 로 매핑 단위가 실제로 적용됐는지 확인하는 데 쓴다.
```
NVMEV_INFO("KSC2026: mapping unit=%u B, flash page=%u B, oneshot page=%u B, pgs_per_blk=%u, blks_per_pl=%u, write buffer=%u B\n", spp->pgsz, FLASH_PAGE_SIZE, ONESHOT_PAGE_SIZE, spp->pgs_per_blk, spp->blks_per_pl, GLOBAL_WB_SIZE);
```

### 5.4 conv_ftl.c / conv_ftl.h (선택 스위치, 기본 0 이면 원본과 같은 동작)
- conv_init_namespace(): `NVMEV_INFO("KSC2026: WBUF_FIX=%d GC_STATS=%d\n", ...)` 1 줄 (항상)
- KSC_GC_STATS=1:
  - struct conv_ftl 에 ksc_part, ksc_gc_seen, ksc_host_pgs, ksc_gc_pgs, ksc_gc_cnt 를 추가했다. conv_init_namespace 에서 0 으로 초기화한다(kmalloc 메모리라 명시적으로 초기화).
  - conv_write 루프에서 LPN 하나를 쓸 때마다 ksc_host_pgs++ (매핑 단위 페이지 단위)
  - gc_write_page() 에서 ksc_gc_pgs++
  - do_gc() 에서 victim 선택 후 ksc_gc_cnt++ 하고, 파티션별 첫 GC 에서 한 번만 `NVMEV_INFO("KSC2026: first GC part=%u victim line=%d vpc=%d ipc=%d free_lines=%u host_pgs=%llu\n")` 를 출력한다.
  - conv_remove_namespace() (rmmod)에서 파티션마다 `KSC2026: stats part=%u host_pgs=%llu gc_pgs=%llu gc_cnt=%llu free_lines=%u` 를 출력한다.
  - 이 계측은 관찰만 하고 타이밍 모델은 바꾸지 않는다. 디스패처 스레드에서만 접근하므로 경쟁 조건도 없다. 성능 영향은 7.3 절의 A/B 로 확인했다(차이 없음).
- KSC_WBUF_FIX=1 (conv_write):
```
#if KSC_WBUF_FIX
	wbuf_bytes = (end_lpn - start_lpn + 1) * spp->pgsz;   /* 매핑 단위 페이지 수만큼 */
#else
	wbuf_bytes = LBA_TO_BYTE(nr_lba);                      /* 원본: 요청 바이트 */
#endif
	allocated_buf_size = buffer_allocate(wbuf, wbuf_bytes);
	if (allocated_buf_size < wbuf_bytes) return false;
```
  - ssd_advance_write_buffer(…, LBA_TO_BYTE(nr_lba)) (PCIe·펌웨어 전송 시간)는 원래대로 요청 바이트를 쓴다.
  - bs ≥ 매핑 단위이고 정렬된 요청이면 wbuf_bytes 가 원본과 같다. 따라서 그 조합에서 base 와 wbuffix 는 같은 동작이다.

### 5.5 빌드 변형 (exp/common.sh variant_make_args)
- base = `GC_STATS=1` — 사용자가 요청한 설정 + 관찰용 계측
- wbuffix = `GC_STATS=1 WBUF_FIX=1`
- plain = (추가 인자 없음) — GC_STATS 영향 확인용, 사전 점검에만 썼다
- merge = `GC_STATS=1 WBUF_FIX=1 WBUF_MERGE=1` — 순차 쓰기 실험(seq3x3_20261008)용. 20:13 KST 추가(커밋 66446ea), 5.6 절.
- 6 개 매핑 단위 모두 경고 없이 빌드된다. 경고는 "the compiler differs from the one used to build the kernel" 하나뿐이다. 커널은 x86_64-linux-gnu-gcc-13 13.3.0, 모듈은 gcc 13.3.0 으로, 바이너리 이름만 다르고 버전은 같다.
- 모듈과 SHA-256: exp/modules/<변형>/nvmev_map<단위>.ko, SHA256SUMS, build_info.txt (srcversion, vermagic "6.8.0-142-generic SMP preempt mod_unload modversions"). .ko 는 git 에 넣지 않는다. base 와 wbuffix 모듈은 run_all.sh 가 14:20:28 부터 다시 빌드했으므로, 결과 폴더의 modules_SHA256SUMS 를 참조한다.

### 5.6 WBUF_MERGE — 쓰기 버퍼 병합 모델 (merge 변형, 커밋 66446ea, 20:13 KST)
- 사용자 선택(1.16 「둘 다 측정」)에 따라 순차 쓰기 실험용으로 새로 만들었다. 기본값은 0 이고, WBUF_MERGE=0 인 빌드는 이전과 같다.
  - 코드 검토 워크플로(9.1 절)의 커널 렌즈가 확인했다. MU 16K, GC_STATS=1, WBUF_FIX=1 빌드에서 HEAD 와 작업 트리의 conv_ftl.o, io.o, main.o, admin.o, ssd.o, nvmev.ko 디스어셈블리가 같다.
  - wbuffix 모듈은 다시 빌드하지 않았다. 14:20 KST 에 빌드한 exp/modules/wbuffix/*.ko 를 그대로 썼다(주 데이터셋과 SHA-256 이 같다).
- Kbuild: `WBUF_MERGE ?= 0`, `ccflags-$(CONFIG_NVMEVIRT_SSD) += -DKSC_WBUF_MERGE=$(WBUF_MERGE)`. WBUF_FIX=0 과 함께 켜면 `#error` 가 난다.
- conv_ftl.h (struct conv_ftl, `#if KSC_WBUF_MERGE`), 파티션마다:
  - `ksc_open_lpn`: 열린 매핑 단위의 전역 lpn, 없으면 INVALID_LPN
  - `ksc_open_mask`: DECLARE_BITMAP(MAPPING_UNIT/LBA_SIZE). 열린 단위에서 지금까지 쓴 섹터
  - 카운터:
    - ksc_mg_open: 부분 쓰기로 연 단위 수
    - ksc_mg_merge: 열린 단위에 합류한 쓰기 수(lpn 단위로 셈)
    - ksc_mg_full: 가득 차서 flash 에 쓴 단위 수
    - ksc_mg_evict: 다른 부분 쓰기에 자리를 내주며 덜 찬 채 쓴 단위 수
    - ksc_mg_direct: 매핑 단위 전체를 덮는 쓰기로 바로 쓴 단위 수
  - conv_init_namespace 에서 INVALID_LPN·0 으로 초기화한다(kmalloc 메모리).
- conv_ftl.c:
  - `ksc_write_lpn()`: 원본 conv_write() 루프 본문(lpn 하나 쓰기)을 그대로 옮긴 함수다. 순서는 get_maptbl_ent → (mapped 면) mark_page_invalid·rmap INVALID → get_new_page(USER_IO) → maptbl·rmap → mark_page_valid → ksc_host_pgs++ → advance_write_pointer → last_pg_in_wordline 이면 ssd_advance_nand + schedule_internal_operation(pgs_per_oneshotpg × pgsz 반납) → consume_write_credit → check_and_refill_write_credit. 프로그램 완료 시각(없으면 0)을 돌려준다.
  - `ksc_conv_write_merge()`: WBUF_MERGE=1 이면 conv_proc_nvme_io_cmd 의 nvme_cmd_write 가 conv_write 대신 이 함수를 부른다.
    1. 할당량 계산(상태 변경 없음). sim_open[파티션] = 현재 열린 lpn 을 복사한다. 명령의 각 lpn 에 대해 sim_open 과 같으면 0 이다. 다르면 pgsz 를 더하고, 부분 쓰기면 sim_open = lpn 으로 둔다. 이는 아래 2 단계의 결정을 그대로 재현한 것이다. 할당량이 0 이 아니고 buffer_allocate 가 모자라면 false 를 돌려준다(디스패처가 나중에 다시 시도). 이때 FTL 상태는 바뀌지 않는다.
    2. ssd_advance_write_buffer(요청 바이트)를 적용하고 swr.stime 을 정한다(원본과 같음). 이어서 각 lpn(s,e = 그 lpn 안의 섹터 범위)에 대해:
       - 그 파티션의 열린 lpn 이면 마스크에 [s,e] 를 더하고 merge++ 한다. 마스크가 가득 차면 닫고 full++, ksc_write_lpn 한다.
       - 아니고 단위 전체를 덮으면 direct++, ksc_write_lpn 한다.
       - 아니면(부분 쓰기) 그 파티션에 열린 단위가 있을 때 먼저 닫고 evict++, ksc_write_lpn(옛 lpn) 한다. 그다음 이 lpn 을 열고(마스크 = [s,e]) open++ 한다.
    3. 완료 시각은 원본과 같다(FUA 또는 early completion 0 이면 nsecs_latest, 아니면 버퍼 전송 완료 시각).
  - rmmod 때 파티션마다 `KSC2026: merge part=%u open=%llu merge=%llu full=%llu evict=%llu direct=%llu still_open=%d` 를 찍는다.
  - 적재 때 `KSC2026: WBUF_MERGE=1 (one open mapping unit per partition merges writes smaller than %u B)` 를 찍는다.
- 의미와 한계:
  - 버퍼 장부: 단위를 열 때 pgsz 를 한 번 할당하고, 합류는 할당하지 않는다. flash 에 쓴 페이지마다 pgsz 가 정확히 한 번 할당되어 있어 반납과 맞는다.
  - 오래 붙잡히는 버퍼는 파티션당 열린 단위 1 개와 덜 찬 wordline 이다. 합쳐 4 × 32 KiB = 128 KiB 이하라, 1 MiB 버퍼에서 영구 대기가 없다(9.1 절).
  - 덜 찬 채 evict 되면 원본처럼 옛 데이터 읽기(RMW) 없이 매핑 단위 페이지 전체를 쓴다.
  - 파티션마다 열린 단위는 1 개뿐이다. 실제 SSD 는 버퍼 전체를 여러 단위에 쓸 수 있다. 하나의 순차 흐름에는 충분하지만, 여러 흐름이 섞이면 실제보다 evict 가 많다.
  - FUA 는 원본과 같이 이 명령이 일으킨 프로그램만 기다린다. FLUSH(conv_flush, 변경 없음)는 모든 파티션에 이미 예약된 NAND 작업이 끝날 때까지 기다린다. 둘 다 열린 단위나 덜 찬 wordline 을 flash 로 내보내지 않는다. 컨트롤러가 VWC=0 이라 커널은 FUA·FLUSH 를 보내지 않으므로 실험과 무관하다.
  - 순차 쓰기가 장치 끝에서 처음으로 돌아갈 때(time_based) 마지막 단위가 덜 찬 채 남았다가 다음 바퀴에 evict 된다. 바퀴마다 1 회 정도다.
- 검산 불변식(파티션마다, 사전 점검에서 확인): host_pgs == full + evict + direct, open == full + evict + still_open.

---------------------------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------

## 6. 실험 설계와 스크립트 동작 (정확한 사양)

### 6.1 matrix / 순서
- 첫 설계(main_20261008, run_all_6x6.sh):
  - MAPS = 4k 8k 16k 32k 64k 128k, BSS = 4k 8k 16k 32k 64k 128k, REPS = 3, 변형 = base, wbuffix(base 108 회 → wbuffix 108 회).
  - 순서: for rep in 1..3 { for map in MAPS { for bs in BSS } }. 반복을 가장 바깥에 둔다.
  - 회차 폴더: exp/results/main_20261008/<변형>/map<MAP>_bs<BS>_r<REP>/
  - 실제로는 10 절처럼 중단·재개·조기 종료되었다.
- 최종 설계(main3x3_20261008, run_all.sh):
  - MAPS = 4k 16k 32k, BSS = 4k 16k 32k, REPS = 3, 변형 = wbuffix, CACHE_MODES = "nodrop drop"
  - 순서: for rep { for map { for bs { for cache in (rep 홀수: nodrop, drop / 짝수: drop, nodrop) } } }
  - 회차 폴더: exp/results/main3x3_20261008/wbuffix_<nodrop|drop>/map<MAP>_bs<BS>_r<REP>/
  - run.log 는 두 폴더에 같은 내용이 들어간다(tee). 54 회.

### 6.2 회차 하나 (run_experiment.sh run_one)
1. DONE 이 있으면 건너뛴다(이어서 하기). 없으면 폴더를 지우고 다시 만든다.
2. nvmev 가 적재되어 있으면 rmmod(마운트 확인 후). 최대 30 s 기다리고 2 s 쉰다.
3. 커널 로그 기록을 시작한다: `sudo -n dmesg -W 2>&1 > >(awk … > kernel.log) &`. awk 는 '[chmodel_request]' 줄을 세고 처음 20 줄만 남긴다. 그 수는 END 에서 chmodel_msgs.txt 에 쓴다. 0.5 s 기다린다.
4. `echo "KSC2026-MARK <회차> insmod <ns>" | sudo -n tee /dev/kmsg` → `sudo -n insmod <ko> memmap_start=12G memmap_size=12G cpus=3,4,5`
5. (아래 6 단계 뒤, 최종 설계에서만) cache.txt 에 meminfo(MemFree/Buffers/Cached/Dirty/Writeback)를 적고, drop 모드면 `sync; echo 3 | sudo -n tee /proc/sys/vm/drop_caches` 후 다시 적는다. SETTLE 5 s 뒤 fio 직전에 pre_fio 줄을 하나 더 적는다. nodrop 모드는 적기만 한다. meta.txt 에 cache_mode 가 들어간다.
5'. /sys/block/nvme*n*/device/model 이 CSL_Virt 로 시작하는 장치를 최대 30 s(0.5 s × 60) 기다린다. 1 s 쉰 뒤, 표지 이후의 링 버퍼 dmesg 를 dmesg_load.txt 에 저장하고 "KSC2026: mapping unit=<bytes> B" 가 있는지 확인한다(없으면 die).
6. check_target_dev: 모델이 CSL_Virt*, 크기 11 GiB ≤ size ≤ 12 GiB, 파티션 없음, 마운트 없음, 루트 FS 장치 아님. 하나라도 어긋나면 die.
7. jobs/randwrite.fio.in 의 @DEV@ @BS@ @IODEPTH@ @RUNTIME@ @RAMP@ @LOG_MSEC@ @LOG_PREFIX@ 를 sed 로 채워 job.fio 를 만든다. meta.txt 를 쓴다.
8. SETTLE_SEC=5 s 쉬고, "KSC2026-MARK <회차> fio-start <ns>" 를 남긴 뒤 `sudo -n fio --output-format=json --output=fio.json job.fio`(stdout/stderr 는 fio_stdout.txt). 끝나면 "fio-end" 표지를 남긴다.
9. "KSC2026-MARK <회차> rmmod <ns>" 표지 → unload_nvmev(rmmod; GC 통계가 찍힌다) → 0.5 s → dmesg 기록 프로세스 kill → chmodel_msgs.txt 를 최대 60 s 기다림 → `sudo -n chown -R dccearth:dccearth <회차폴더>`
10. kernel.log 를 표지로 나눈다: fio-start ~ rmmod 표지 = dmesg_run.txt (chmodel 줄 제외), rmmod 표지 이후 = dmesg_unload.txt. meta.txt 에 end, fio_exit, chmodel_msgs, kernel_warn 을 더한다.
11. fio 종료 코드가 0 이고 fio.json jobs[0].error == 0 이면 결과 1 줄을 출력하고 DONE 을 만든다. 아니면 FAILED 표지를 만들고 계속한다(커밋 2a462a3 부터. 그 전 5769378 에서는 die 했다 — 10 절 첫 중단). fio 는 백그라운드로 실행하고 감시 타이머(RUNTIME+180 s SIGTERM, +60 s SIGKILL)가 지킨다.
- 시작할 때: sudo -n -l 로 insmod·rmmod·fio·dmesg·"tee /dev/kmsg" 권한 확인, /proc/cmdline 에 memmap=12G$12G 확인, 모든 .ko 존재 확인, sha256sum -c 확인. 그 뒤 env_before 스냅샷(없을 때만), modules_SHA256SUMS·modules_build_info.txt·randwrite.fio.in·git_head.txt·nvmevirt_vs_upstream.diff·nvmevirt_uncommitted.diff 를 <변형>/ 에 복사한다. 끝날 때: unload, env_after_<변형> 스냅샷.
- **알려진 결함 1 (커밋 2a462a3=949ae38, 14:49 에서 수정)**: 커밋 5769378 의 run_experiment.sh 는 `nvmevirt_vs_upstream.diff` 를 `git diff -M 61c90f7 HEAD -- nvmevirt` 로 만들어, pathspec 때문에 rename 을 찾지 못하고 모든 파일을 새 파일로 표시했다(수천 줄). 2a462a3 부터는 `git diff d508610 HEAD -- nvmevirt`(변수 MOVE_COMMIT)를 쓴다. main_20261008/wbuffix/ 와 main3x3_20261008/wbuffix_drop/, wbuffix_nodrop/ 의 nvmevirt_vs_upstream.diff(각 200 줄)는 올바르다. main_20261008/base/nvmevirt_vs_upstream.diff(12,840 줄, 14:21 KST 생성)만 옛 형식으로 남아 있다(base 는 14:49 이후 다시 실행되지 않았고, 이 파일은 다시 만들지 않았다). 올바른 diff 는 `git diff d508610 e598e75 -- nvmevirt` 다(200 줄).
- **알려진 결함 2 (커밋 2a462a3=949ae38 에서 수정, main_20261008/base 1–21 회 meta.txt 에만 해당)**: 커밋 5769378 의 run_experiment.sh 는 meta.txt 의 kernel_warn 을 셀 때 KSC2026 줄만 빼서, 처음 20 개 chmodel 표본 줄 중 "No free entry" 줄도 셌다. 22 회 이후 base·wbuffix 와 main3x3_20261008 의 meta.txt 는 chmodel 줄을 뺀 값이다. analyze.py 는 kernel.log 에서 '[chmodel_request]' 와 'KSC2026' 줄을 빼고 WARNING|almost full|timeout|reset|Oops|BUG|Disk read failed|I/O error 를 다시 센다. CSV 의 kernel_warn 은 이렇게 다시 센 값이다.

### 6.3 fio 작업 (exp/jobs/randwrite.fio.in → <회차>/job.fio)
```
[global]
filename=/dev/nvme1n1 (회차마다 찾음)
ioengine=libaio
direct=1
rw=randwrite
bs=<BS>
iodepth=32
numjobs=1
time_based=1
runtime=60
ramp_time=0
group_reporting=1
randrepeat=1
percentile_list=50:90:95:99:99.9:99.99
write_bw_log=<회차폴더>/fio
write_iops_log=<회차폴더>/fio
write_lat_log=<회차폴더>/fio
log_avg_msec=500
[randwrite]
```
- size 를 지정하지 않았으므로 장치 전체(12,040,984,064 B)를 대상으로 한다. norandommap 은 기본 0 이라 한 바퀴 동안 같은 블록을 다시 쓰지 않는다. 기본 random_generator 는 tausworthe, randrepeat=1 이라 모든 회차가 같은 난수 순서를 쓴다. 따라서 반복 간 차이는 에뮬레이터 타이밍 차이만 담는다.
- fio 를 특정 CPU 에 고정하지 않았다. isolcpus 때문에 CPU 0–2 에서만 돈다.
- 로그 파일: fio_bw.1.log(KiB/s), fio_iops.1.log, fio_lat.1.log, fio_clat.1.log, fio_slat.1.log(ns). 열은 ms, 값, 방향(1=write), bs, offset 이다.

### 6.4 권한 (/etc/sudoers.d/nvmevirt-exp, 0440 root:root) — 14:06 설치, 14:08 /dev/kmsg 추가, 15:55 drop_caches 추가
```
# KSC2026 NVMeVirt mapping-unit experiment — remove after the experiment:
#   sudo rm /etc/sudoers.d/nvmevirt-exp
dccearth ALL=(root) NOPASSWD: /usr/sbin/insmod, /usr/sbin/rmmod, /usr/bin/fio, /usr/bin/dmesg, /usr/sbin/nvme, /usr/bin/cat /proc/iomem, /usr/bin/tee /dev/kmsg, /usr/bin/tee /proc/sys/vm/drop_caches, /usr/bin/chown -R dccearth\:dccearth /home/dccearth/jsw/KSC2026/nvmevirt/exp/*
```
- 사본: exp/report/nvmevirt-exp.sudoers. insmod·fio 권한은 사실상 root 와 같다. 실험 후 지우기로 사용자에게 말했다(10.3 절).
- 마지막 chown 항목은 실험 당시 경로(/home/dccearth/jsw/KSC2026/nvmevirt/exp/*)와 사용자(dccearth)에 묶여 있다. 17:06 KST 이후 위치(/home/dccearth/jsw/nvmevirt)나 다른 clone 에서 재현하려면 `/usr/bin/chown -R <USER>\:<USER> <REPO>/exp/*` 로(맨 앞 사용자 이름도 <USER> 로) 바꿔 다시 설치해야 한다. 맞지 않으면 run_experiment.sh 가 첫 회차 끝의 `sudo -n chown` 에서 실패해(set -euo pipefail) DONE 없이 멈춘다. 사전 점검(PRIV)은 chown 을 검사하지 않고, `sudo -n -l` 은 `(ALL : ALL) ALL` 항목 때문에 성공하므로 미리 알 수 없다. docx 4.3 절에 바꾸는 sed 명령이 있다.
- **20:17 KST 다시 설치(순차 쓰기 실험용)**: 18:33 에 지웠던 규칙을 사용자가 직접 설치했다(1.18 절). 바뀐 점은 두 가지다. chown 경로를 옮긴 위치로 바꿨고, 블록 계층 병합을 끄는 tee 를 추가했다. 지금의 exp/report/nvmevirt-exp.sudoers 가 이 내용이다(커밋 66446ea; 위의 옛 내용은 c742c67 까지의 사본).
```
# (chown path = <clone>/exp/*; the nomerges rule names the NVMeVirt namespace of this server, nvme1n1)
dccearth ALL=(root) NOPASSWD: /usr/sbin/insmod, /usr/sbin/rmmod, /usr/bin/fio, /usr/bin/dmesg, /usr/sbin/nvme, /usr/bin/cat /proc/iomem, /usr/bin/tee /dev/kmsg, /usr/bin/tee /proc/sys/vm/drop_caches, /usr/bin/tee /sys/block/nvme1n1/queue/nomerges, /usr/bin/chown -R dccearth\:dccearth /home/dccearth/jsw/nvmevirt/exp/*
```
  - nomerges 규칙은 장치 경로를 nvme1n1 으로 고정했다. sudoers 인자 와일드카드는 공백과 / 도 맞아서, `nvme*n1/queue/nomerges` 같은 패턴은 다른 파일 쓰기를 허용할 수 있다.
- 그 뒤의 이력: 21:34:17 KST 사용자가 제거(순차 쓰기 실험 후, 10.4 절) → 22:11:08 KST 사용자가 다시 설치(랜덤 bs 8K·64K 실험용, 1.21 절; 파일 크기 538 B 로 exp/report/nvmevirt-exp.sudoers 와 같음) → 23:08:30 KST 사용자가 제거(10.5 절). 지금 서버에 규칙은 없다.

### 6.5 분석 (exp/analyze.py results/<EXP>)
- 회차별 지표: bw_MiBps(= fio write.bw/1024), iops, written_GiB, fill_ratio(= io_bytes/장치 크기), clat_mean/p50/p99/p999_us, lat_mean_us, slat_mean_us, runtime_s, bw_first10s_MiBps(t ≤ 10 s), bw_last20s_MiBps(t > 마지막 시각 − 20 s), dev_bytes, chmodel_msgs, kernel_warn.
- GC_STATS 가 있는 경우: gc_onset_s(fio-start 표지부터 4 개 파티션 중 가장 이른 "first GC" 줄까지), gc_onset_last_part_s, bw_pre_gc_MiBps(t ≤ onset), bw_post_gc_MiBps(t > onset), gc_cnt(4 개 파티션 합), ftl_host_pgs, ftl_gc_pgs, waf_gc = (host+gc)/host, waf_total = (host+gc)×매핑 단위 바이트 / fio io_bytes.
- 주의: ftl_host_pgs 에는 rmmod 직전까지 디스패처가 처리한 모든 쓰기가 들어간다. fio 가 끝난 뒤 udev 의 파티션 재검사 같은 읽기는 쓰기가 아니므로 포함되지 않는다.
- 집계: (variant, map, bs) 별 mean/std(표본 표준편차, n−1)/min/max/n.
- 그림: fig_bw_vs_bs_<v>, fig_clat_mean_vs_bs_<v>(log), fig_clat_p99_vs_bs_<v>(log), fig_bw_last20s_vs_bs_<v>, fig_bw_heatmap_<v>, fig_waf_heatmap_<v>, fig_timeseries_<v> (6×6, 3 회 겹침, 점선 = 첫 GC), fig_variant_compare.

### 6.6 순차 쓰기 실험 (seq3x3_20261008, exp/run_all_seq.sh, 커밋 66446ea)
- 스크립트 변경(랜덤 쓰기 결과에는 영향 없음, 기본값은 이전 동작):
  - common.sh:
    - `WORKLOAD` (기본 randwrite): job 틀 `jobs/<WORKLOAD>.fio.in` 을 고른다.
    - `NOMERGES` (기본 빈 값 = 커널 설정 그대로; 0/1/2): insmod 와 장치 확인 직후 `echo $NOMERGES | sudo -n tee /sys/block/<dev>/queue/nomerges` 를 실행한다.
    - variant `merge` 를 추가했다.
  - jobs/seqwrite.fio.in: randwrite.fio.in 과 비교해 바뀐 것은 rw=write, randrepeat 줄 삭제, 작업 이름 [seqwrite] 뿐이다. time_based 라 장치 끝에 닿으면 offset 0 으로 돌아가 계속 쓴다.
  - run_experiment.sh:
    - meta.txt 에 `workload:` 줄과 `blk_queue:` 줄(nomerges, scheduler, max_sectors_kb, write_cache)을 쓴다.
    - fio 앞뒤에 /sys/block/<dev>/stat 의 쓰기 I/O 수, 쓰기 merge 수, 쓰기 섹터 수를 읽어 차이를 `blk_writes: ios=… merges=… sectors=…` 로 쓴다(이번 실험부터 모든 회차).
    - job 틀은 변형 폴더에 그대로 복사한다.
  - analyze.py:
    - meta 의 blk_writes 에서 blk_wr_ios, blk_wr_merges, blk_avg_req_KiB 를 읽는다.
    - dmesg_unload 의 merge 줄에서 mg_open, mg_merge, mg_full, mg_evict, mg_direct, mg_still_open 을 읽는다(합계).
  - make_md_results.py(이 부분은 66446ea 뒤의 커밋 a86fc87 에 들어감):
    - 위 지표를 행렬에 넣고, 변형 비교 (merge − wbuffix)/wbuffix 를 대역폭과 WAF_total 로 만든다.
    - GC 로그 절에 merge 줄을 넣는다.
- run_all_seq.sh: `MAPS="4k 16k 32k" BSS="4k 16k 32k" CACHE_MODES=nodrop WORKLOAD=seqwrite NOMERGES=2`
  - 순서: for r in 1 2 3 { for v in wbuffix merge { REPS=$r run_experiment.sh <EXP> $v } }. DONE 이 있는 회차를 건너뛰므로, 반복 r 을 두 모델이 번갈아 한 바퀴씩 돈다. 각 바퀴 안의 순서는 매핑 4K→32K, bs 4K→32K 다.
  - 결과: results/seq3x3_20261008/{wbuffix,merge}/map<M>_bs<B>_r<R>/, env_before, env_after_<변형>(이 데이터셋은 당시 collect_env.sh 가 덧붙여 써서 호출 3 번의 스냅샷이 한 파일에 이어져 있다 — 10.4 절), 콘솔 로그 results/run_all_seq3x3_20261008.log(실행 중 이름은 seq3x3_20261008.console.log, 실험 후 이름을 바꿈 — 10.4 절).
  - 로그의 「N runs, about M min」과 「[i/N]」의 N 은 REPS=r 까지의 전체 회차 수(9/9/18/18/27/27)다. 이미 DONE 인 회차는 건너뛰므로, 각 호출은 실제로 9 회(약 10.5 분)만 돌고 [9/N] 근처에서 finished 로 끝난다. 정상이다.
  - 실행: `tmux new -d -s ksc2026seq "bash run_all_seq.sh seq3x3_20261008 2>&1 | tee -a results/seq3x3_20261008.console.log; echo SEQ-ALL-DONE >> results/seq3x3_20261008.console.log"`
- 랜덤 쓰기 실험과 다른 점: fio rw 와 nomerges=2 뿐이다. 장치, 모듈(wbuffix), insmod 인자, fio 의 나머지 값(libaio, direct, QD 32, 60 s, ramp 0, 0.5 s 로그), SETTLE 5 s, 회차마다 rmmod/insmod 는 같다.
- 스케줄러는 커널 기본 mq-deadline 그대로다(랜덤 쓰기 실험도 같았다). nomerges=2 라 요청을 합치지 않는다.

---------------------------------------------------------------------------------------------------

### 6.7 랜덤 쓰기 bs 8K·64K 실험 (randbs_20261008, exp/run_all_rand_bs.sh, 커밋 a86fc87)
- run_all_rand_bs.sh <EXP> [PRIMARY_EXP=main3x3_20261008] [VIEW=rand3x5_<EXP 의 날짜>]:
  - `MAPS="4k 16k 32k" BSS="8k 64k" REPS=3 CACHE_MODES=nodrop WORKLOAD=randwrite NOMERGES=` (NOMERGES 빈 값 = 커널 기본값, 주 데이터셋과 같음)
  - 순서는 `run_experiment.sh <EXP> wbuffix` → analyze.py → `link_runs.py results/<VIEW> results/<PRIMARY>/wbuffix_nodrop results/<EXP>/wbuffix` → analyze.py results/<VIEW> 다.
  - 실행: `tmux new -d -s ksc2026rbs "bash run_all_rand_bs.sh randbs_20261008 2>&1 | tee -a results/run_all_randbs_20261008.log; echo RBS-ALL-DONE >> results/run_all_randbs_20261008.log"`
- link_runs.py: DONE 이 있는 map*_bs*_r* 폴더마다 results/<VIEW>/<변형 이름, 기본 wbuffix>/ 아래에 상대 심볼릭 링크를 만든다. 같은 회차 이름이 두 곳에서 오면 멈춘다. SOURCES.txt 에 출처를 적는다. 링크라 묶음(tar)·git 에도 그대로 들어가고, 묶음 안에서도 repo/exp/results/ 기준으로 풀린다.
  - 23:1x KST 에 고친 판(9.3 절): 링크를 만들기 전에 모든 원본을 훑어 중복과 「링크 자리에 실제 폴더가 있음」을 먼저 검사하고, 문제가 있으면 아무것도 만들지 않는다. SOURCES.txt 는 보기 아래 실제 링크 전체(모든 변형)에서 만든다. 지금 보기(45 개 링크, SOURCES.txt)는 고친 판으로 다시 실행해도 바이트 단위로 같다.
  - run_all_rand_bs.sh 의 모듈 확인은 실험 때 `[[ -f modules/wbuffix/SHA256SUMS ]]` 였고, 23:1x 에 .ko 존재 검사로 바꿨다(이 서버에서는 두 조건 모두 「이미 있음」이라 동작이 같다).
- 축 분리(analyze.py·plot.py·make_md_results.py 는 커밋 a86fc87, make_report.py 는 커밋 403a6ae): 네 파일은 매핑 단위 목록(행)과 bs 목록(열)을 따로 쓴다. 그전에는 합집합 하나를 두 축에 썼는데, 3 × 5 보기에서는 빈 행이 생긴다. 정사각 데이터셋(main3x3, main, seq3x3)의 CSV 와 그림 내용은 같다. 다만 fig_timeseries_* 는 그림 크기가 격자 수에 맞게 바뀐다(예전에는 항상 2400×1950 px). 그래서 23:1x KST 에 main3x3·main 의 analyze.py 를 다시 돌려 그 PNG 4 개를 새 크기로 바꿨다(CSV 는 바이트 단위로 같음).
- analyze.py 그림 제목: meta.txt 에 `workload: seqwrite` 가 있으면 「Sequential-write」, 없으면 「Random-write」로 쓴다. 그전에는 seq3x3 의 fig_bw_vs_bs_* 제목이 「Random-write」로 잘못 나왔고, 실험 후 다시 만들었다(10.5 절).

---------------------------------------------------------------------------------------------------

## 7. 사전 점검 기록 (시간순, KST)

- 13:46 upstream clone → /home/dccearth/jsw/KSC2026/nvmevirt/upstream_tmp (감사용으로 그대로 둠)
- 13:49 감사 워크플로 시작(wf_b41bb861-a42; 9 절)
- 13:53 스테이징 clone(/home/dccearth/jsw/KSC2026/.nvmevirt_stage) → git mv → 13:54:03 커밋 d508610
- 13:5x 소스 수정. 6 개 매핑 단위 시험 빌드 모두 OK(경고는 compiler differs 하나). WBUF_FIX/GC_STATS 4 가지 조합 × 4K·128K 시험 빌드도 모두 OK.
- 14:06 sudoers 설치. 이때 /proc/iomem 과 e820 으로 예약 영역을 확인했다(3 절).
- 14:07 스테이징 저장소를 /home/dccearth/jsw/KSC2026/nvmevirt 로 옮겼다. 그래서 exp/.venv 를 다시 만들었다(venv 경로가 절대경로라).
- 14:07:51 스모크 테스트 1 차는 실패했다. 원인: dmesg 를 /proc/uptime 기준 시각으로 잘랐는데 printk 시계가 CLOCK_BOOTTIME 보다 약 1 s 이상 늦어서 적재 로그를 놓쳤다. 모듈 자체는 정상 적재되었다. → /dev/kmsg 표지 방식으로 바꾸고 sudoers 에 tee /dev/kmsg 를 추가했다(14:08).
- 14:08:48 스모크 테스트 2 차(base, 매핑 4k·128k × bs 4k·128k, 10 s, 1 회):
  - 4k/4k 1273.2 MiB/s 325,927 IOPS clat 97.2 µs
  - 4k/128k 1297.5 MiB/s 10,380 IOPS clat 3078.3 µs
  - 128k/4k 101.8 MiB/s 26,065 IOPS clat 1226.1 µs
  - 128k/128k 1481.2 MiB/s 11,850 IOPS clat 2696.6 µs
  - 128k/4k 회차의 dmesg_run 이 비어 있었다. 원인: '[chmodel_request] Need to increase array size' 오류가 넘쳐 256 KiB(CONFIG_LOG_BUF_SHIFT=18) 링 버퍼가 덮어쓰였다. → 회차마다 `dmesg -W` 로 실시간 기록하도록 바꿨다.
  - 이 스모크 결과의 GC 통계(rmmod 시): 4k/4k host_pgs ≈ 815K/파티션, gc_pgs ≈ 356K, 첫 GC 6.3 s(host_pgs=778240/파티션에서). 128k/128k 첫 GC 3.86 s(host_pgs 24320/파티션에서). 128k/4k host_pgs ≈ 65K/파티션(= 7.9 GiB/파티션 NAND 쓰기, 호스트 약 1 GiB) → 매핑 128K 에 4K 쓰기면 NAND 쓰기 32 배.
- 14:12–14:14 스모크 3 차(base·wbuffix 각 4 조합, 10 s, kernel.log 전체 저장 방식):
  - base: 4k/4k 1272.9, 4k/128k 1297.5, 128k/4k 101.6 (chmodel 오류 1,665,207 줄, kernel.log.gz 16 MB), 128k/128k 1482.0 MiB/s
  - wbuffix: 4k/4k 1272.4, 4k/128k 1297.5, 128k/4k 77.0 (19,724 IOPS, clat 1621.0 µs, 오류 0), 128k/128k 1482.3 MiB/s
  - → 60 s 실행이면 회차당 약 100 MB 가 되므로, awk 로 세기만 하고 20 줄만 남기도록 바꿨다(14:15).
- 14:15:12 스모크 4 차(base 128k/4k, 10 s): 101.6 MiB/s 26,006 IOPS clat 1227.9 µs, chmodel_msgs 1,859,673. kernel.log 는 79 줄(6.8 KB). systemd-journald: "/dev/kmsg buffer overrun, some messages lost. (Dropped 93506 similar message(s))". 첫 GC 는 2.2 s(host_pgs=24320/파티션에서). 이 결과가 exp/results/pre_smoke_test/ 에 남아 있다(앞선 스모크 결과는 지웠다. 수치는 위 기록이 전부다).
- 14:15:50–14:18:36 GC_STATS A/B(매핑 4k, bs 4k, 20 s, 3 회, SETTLE 3 s), exp/results/pre_gcstats_ab/:
  - plain(GC_STATS 끔): 724.1 / 721.9 / 722.1 MiB/s (185,361 / 184,807 / 184,868 IOPS, clat 171.6 / 172.1 / 172.1 µs)
  - base(GC_STATS 켬): 724.3 / 726.0 / 724.4 MiB/s (185,428 / 185,864 / 185,444 IOPS, clat 171.5 / 171.1 / 171.5 µs)
  - 평균 722.7 vs 724.9 (+0.3 %, 반복 편차 수준) → 계측 영향 없음
  - (첫 시도는 Claude 셸의 grep 래퍼 문제로 파이프가 끊겨 run.log 만 남았다. 지우고 다시 실행했다.)
- 14:20:15 커밋 c02b9fd, 5769378 → push(main, 신규 브랜치)
- 14:20:28 run_all.sh main_20261008 시작(tmux 세션 ksc2026, 로그 exp/results/run_all_main_20261008.log). 14:20:28–14:21:02 에 base 와 wbuffix 모듈 12 개를 빌드했다(base 6 개 14:20:28–14:20:45, wbuffix 6 개 14:20:45–14:21:02). 14:21:02 env_before 스냅샷, 1/108 회차 시작.

### 7.1 순차 쓰기 실험 사전 점검 (19:58–20:23 KST)
- 19:58–19:59 merge 코드 작성(conv_ftl.h·conv_ftl.c·Kbuild). 19:59 빌드 경고 없음(MU 16K; WBUF_FIX=0 과 함께 켜면 #error 확인). 20:00:53 코드 검토 워크플로 시작(9.1 절).
- 20:13 검토 결과 고칠 결함 없음 → FUA/FLUSH 주석만 보강. 커밋 66446ea(로컬). 그 커밋에서 수정 파일 0 개인 상태로 merge 모듈 3 개를 빌드했다(20:13:49 KST).
  - SHA-256: map4k 1287238c…, map16k 38b27bcc…, map32k 91563b73…
  - 전체 값은 exp/modules/merge/SHA256SUMS 에 있다. 커밋 전 작업 트리에서 빌드한 것과 같다.
- 20:0x sudoers 설치 시도가 자동 모드 분류기에 막혔다(1.18). 20:17 사용자가 설치했다.
- 20:18:20–20:22:59 사전 점검(15 s 회차, 그 밖은 본 실험과 같음; 스크립트는 scratchpad 의 pre_seq.sh, 로그는 results/pre_seq_all.log):
  - A. `results/pre_seq_blkmerge_default/` — 커널 기본(nomerges=0, mq-deadline), wbuffix, 16K/4K 순차
    - fio 는 4K 쓰기 3,592,598 개를 보냈다. 장치가 받은 쓰기는 119,696 개이고, 블록 계층이 3,472,902 번 합쳤다. 평균 요청은 28,740,784 섹터 × 512 / 119,696 ≈ 120 KiB 다.
    - 결과는 935.5 MiB/s 다. 「bs 4K 순차」가 사실상 약 120K 쓰기가 된다. 그래서 본 실험은 nomerges=2 로 한다(8.5 절).
  - B. `results/pre_seq_check/` — nomerges=2, 매핑 16K·32K × bs 4K·16K × {wbuffix, merge}. 모든 회차에서 blk merges 0, 장치 ios = fio ios, chmodel 0, kernel_warn 0.

| 매핑 / bs (15 s 순차) | wbuffix MiB/s | merge MiB/s | host WAF (= host_pgs×MU/io_bytes) wbuffix → merge | WAF_total wbuffix → merge | merge 카운터 (4 파티션 합) |
|---|---|---|---|---|---|
| 16K / 4K | 411.0 | 2,105.5 | 4.000 → 1.000 | 4.675 → 1.000 | open 2,021,471 · merge 6,064,375 · full 2,021,453 · evict 18 · direct 0 · still_open 0 |
| 16K / 16K | 2,231.8 | 2,232.6 | 1.000 → 1.000 | 1.000 → 1.000 | direct 2,143,481 (나머지 0) |
| 32K / 4K | 232.9 | 2,101.6 | 8.000 → 1.000 | 8.646 → 1.000 | open 1,008,838 · merge 7,061,859 · full 1,008,835 · evict 2 · still_open 1 |
| 32K / 16K | 654.6 | 2,232.5 | 2.000 → 1.000 | 2.761 → 1.000 | open 1,071,682 · merge 1,071,680 · full 1,071,680 · evict 2 |

    - merge 모델은 16K 단위마다 4K 쓰기 4 개(open 1 + merge 3)를 모아 한 번만 쓴다. evict 는 32K/4K·32K/16K 에서는 장치 끝에서 처음으로 돌아갈 때(덜 찬 끝 단위가 있는 파티션, 1–2 회)만 생겼다. 16K/4K 의 evict 18 개(파티션별 4·4·4·6)는 돌아간 횟수(2 회)보다 많고 모든 파티션에서 나왔다. 대부분 요청 순서가 바뀐 경우로 보인다(추정, 8.7 절). 불변식 host_pgs == full+evict+direct 와 open == full+evict+still_open 이 모든 회차에서 맞았다.
    - wbuffix 의 host WAF 는 정확히 매핑/bs(4·8·2)다. 4K 쓰기마다 16K 페이지 하나를 쓰기 때문이다.
    - 순차 쓰기 + merge 에서 GC 복사(gc_pgs)는 0 이다. 앞 바퀴의 line 이 통째로 무효가 되기 때문이다.
  - C. `results/pre_rand_merge_check/` — 랜덤 쓰기 실험과 같은 설정(nomerges 커널 기본), 16K/4K randwrite
    - wbuffix 297.9 MiB/s, merge 295.8 MiB/s(−0.7 %). merge 의 evict 1,136,674 = host_pgs, merge 3 이다. 랜덤에서는 거의 합칠 것이 없어 wbuffix 와 같은 동작이다.
    - 블록 계층 merges 는 두 회차 모두 1 이다. 랜덤 쓰기 주 데이터셋도 블록 계층 병합의 영향이 없었다는 근거다(그 데이터셋에는 blk 기록이 없음).
- 20:23:24 본 실험 시작(10.4 절).

---------------------------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------

## 8. 발견 사항과 모델 특성 (결과 해석에 필수)

### 8.1 쓰기 버퍼 과다 반환 (base 의 bs < 매핑 단위 15 개 조합)
- 코드(원본 61c90f7):
  - conv_write(): `allocated_buf_size = buffer_allocate(wbuf, LBA_TO_BYTE(nr_lba))` — 요청 바이트를 할당한다.
  - wordline(oneshot page)이 다 차면 `schedule_internal_operation(req->sq_id, nsecs_completed, wbuf, spp->pgs_per_oneshotpg * spp->pgsz)` 로 NAND 프로그램 완료 시각에 oneshot page 바이트를 반환한다. io.c 의 워커 완료 경로가 buffer_release(w->write_buffer, w->buffs_to_release) 를 호출한다.
  - buffer_release() 는 remaining += size 만 하고 상한을 두지 않는다(ssd.c 39–47).
  - bs < 매핑 단위면 요청 하나가 매핑 단위 페이지 하나를 통째로 쓴다. 그래서 할당은 bs, 반환은 매핑 단위가 되어 반환이 더 많다. 예: 매핑 128K·bs 4K 는 요청당 +124 KiB, 매핑 16K·bs 4K 는 wordline 32K 당 할당 8K·반환 32K.
- 결과:
  - 쓰기 버퍼가 호스트를 붙잡지 못한다. WRITE_EARLY_COMPLETION=1 이라 호스트 완료 시각은 nsecs_xfer_completed(버퍼+PCIe)이고, NAND·GC 지연이 호스트에 전달되는 통로는 버퍼가 찼을 때의 재시도뿐인데 그 통로가 사라진다.
  - LUN 의 next_lun_avail_time 이 실제 시간보다 계속 앞서 나간다. 채널 모델(channel_model.c)의 시간 창 NR_CREDIT_ENTRIES 96K × UNIT_TIME_INTERVAL 4 µs ≈ 393 ms 를 넘으면, `NVMEV_ERROR("[chmodel_request] Need to increase array size …")` 를 찍고 request_time 을 그대로 돌려준다(채널 전송 시간 0). 창이 꽉 차면 "No free entry" 오류도 난다.
  - 이 오류는 rate limit 없는 pr_err 다. 디스패처(cpu3) 핫패스에서 요청마다 찍히고, 콘솔 loglevel 4 라 tty0 콘솔과 journald 에도 간다. 측정값: 128k/4k 10 s 에 약 167–186 만 줄(스모크 3 차 1,665,207 줄, 4 차 1,859,673 줄), 8k/4k 60 s 에 8,242,206 줄.
  - 따라서 base 의 bs < 매핑 단위 결과는 「채널 시간이 빠져 빨라짐」과 「printk·콘솔 부담으로 느려짐」이 섞인 값이다. 타이밍 모델이 정상 범위를 벗어났다.
- 수정: WBUF_FIX=1 (5.4 절). 감사 에이전트 3 개(wbuf-write-path, geometry-init, gc-timing)가 모두 독립적으로 blocker 로 판정했고 같은 수정을 제안했다. 검증 에이전트도 확인했다(9 절).
- 스모크 비교(10 s, 128k/4k): base 101.6–101.8 MiB/s(오류 수십만~186 만 줄), wbuffix 77.0 MiB/s(오류 0). 감사의 시뮬레이션(ftlsim)은 수정 후 128k/4k 를 GC 전 약 43.5K IOPS(NAND 한계 47.0K pages/s)로 예측했다. GC 후에는 10 s 에 9.8K, 30 s 에 5.0K IOPS 로 떨어진다는 예측이다.

### 8.2 64K·128K 의 flash page 변경은 NAND 성능도 바꾼다 (사용자 지시에 따른 것, 바꾸지 않음)
- tPROG 는 185 µs 그대로이고 oneshot page 가 32K → 64K → 128K 로 커진다. 따라서 die 당 프로그램 주기는 (채널 전송 + tPROG) 223.9 µs(32K) → 262.8 µs(64K) → 340.6 µs(128K)다. die 당 대역폭은 139.6 → 237.8 → 367.0 MiB/s, 16 die 합은 2,233 → 3,805 → 5,871 MiB/s 로 1.7·2.6 배가 된다(감사 gc-timing 계산).
- 쓰기 버퍼 GLOBAL_WB_SIZE = 8×2×oneshot×2 = 1 MiB(≤32K) → 2 MiB(64K) → 4 MiB(128K).
- 그러므로 32K → 64K 경계의 성능 차이를 매핑 단위만의 효과로 보면 안 된다. 감사가 제안한 대안은 NAND_PROG_LATENCY = 185000 × FLASH_PAGE_SIZE/32K(64K 370 µs, 128K 740 µs)로 바이트당 비용을 일정하게 하는 것이다. 적용하지 않았다(사용자 지시 범위 밖). 후속 실험 후보다.

### 8.3 기타 모델 특성
- RMW 미모델: 부분 쓰기도 옛 페이지를 읽지 않고 무효화 + 새 페이지 프로그램만 한다. 데이터 무결성은 NVMeVirt 가 데이터를 논리 주소 그대로 예약 메모리에 저장하므로 문제없다. 성능 면에서는 작은 bs·큰 매핑의 불이익이 과소평가된다(wbuffix 도 마찬가지).
- 쓰기 조기 완료 + foreground GC:
  - GC 는 디스패처 스레드에서 동기로 실행된다(conv_write → check_and_refill_write_credit → foreground_gc → do_gc, line 1 개씩).
  - GC 의 NAND 비용은 LUN 시간만 점유하고, 호스트에는 버퍼가 찰 때만 보인다(GC 쓰기는 버퍼를 쓰지 않는다).
  - 지우기 지연은 0 이다. GC 읽기→쓰기 의존이 강제되지 않고, GC 는 '지금' 시각에 시작한다.
- 활성 I/O 워커 1 개: nvmev.h 의 `#define CONFIG_NVMEV_IO_WORKER_BY_SQ` 때문에 워커 = (sqid−1) % nr_io_workers 다. 가상 장치가 MSI-X 없이 레거시 IO-APIC IRQ 15 하나(/proc/interrupts: "15: … IR-IO-APIC 15-edge nvme1q0, nvme1q1")만 받아 I/O 큐가 1 개("nvme nvme1: 1/0/0 default/read/poll queues")다. 그래서 모든 요청이 sqid 1 → cpu4 의 워커 0 만 쓰이고, fio 가 어느 CPU 에 있든 같다. 워커 1(cpu5)은 I/O 없이 폴링만 한다. /proc/irq/15/effective_affinity_list = 5 (smp_affinity_list 0-5, irqbalance 미설치 — dpkg-query 결과 없음)라서 호스트 nvme 완료 인터럽트는 cpu5 에서 처리된다(15:2x 확인, IRQ 15 누적 112,040,881 회 전부 CPU5). 논문에는 「디스패처 1 + 워커 2(활성 1)」로 적는 것이 정확하다.
- 매핑 표가 호스트 메모리 배열(DFTL 캐시 모델 없음)이라 L2P 크기 효과는 성능에 나타나지 않는다. L2P 크기는 계산으로 따로 보고한다: 전체 FTL 페이지 × 8 B = 4K 24 MiB, 8K 12, 16K 6, 32K 3, 64K 1.5, 128K 0.75 MiB. rmap 도 같은 크기다.
- GC 문턱: free line ≤ 2 (gc_thres_lines = gc_thres_lines_high = 2). 쓰기 크레딧(pgs_per_line)을 다 쓸 때마다 검사한다. 처음 free line 은 파티션당 382 개(384 − 사용자·GC 쓰기 포인터 2). 첫 GC 는 파티션당 380 line = 장치 전체 12,160 MiB 의 페이지 쓰기 뒤에 온다. 측정에서도 첫 GC 시점의 host_pgs = 778,240/파티션(4K 매핑, = 380 × 2048) — 정확히 일치한다.
- fio randommap 의 주기 현상(14:3x 에 시계열로 확인):
  - 첫 바퀴(논리 11.21 GiB)는 모든 LBA 를 한 번씩 써서 무효 페이지가 없다. 물리 12 GiB 가 차는 순간(약 0.67 GiB 덮어쓰기 후) GC 가 시작되는데, 그때 victim line 에 무효 페이지가 거의 없어 대역폭이 크게 떨어진다(4k/4k: 약 2,000 → 120–250 MiB/s).
  - 둘째 바퀴가 진행될수록 무효 페이지가 늘어 서서히 회복된다.
  - 둘째 바퀴가 끝날 무렵에는 첫 바퀴에 쓴 line 이 모두 무효라 GC 비용이 0 에 가까워져 대역폭이 치솟는다(4k/4k 약 51 s 에 1,400 MiB/s, 4k/128k·8k/128k 약 36 s 에 1,700 MiB/s). 그 뒤 셋째 바퀴에서 다시 떨어진다.
  - 이 주기는 fio 의 randommap(norandommap=0)과 장치 크기로 정해지는 실험 특성이다. 60 s 평균에 그대로 섞이므로 해석에 반드시 고려해야 한다. 감사 C6 이 예측한 내용이다.
- 이전 iodepth 실험의 64K IOPS(250 MiB/s)는 재적재 없이 연속 실행한 GC 정상 상태 값이다. 이번 실험의 GC 이후 구간(약 120–250 MiB/s, 회복 구간 제외)과 같은 수준이다.
- GC 이전 처리량(감사 검증 단계의 정정, 실측과 일치):
  - bs ≥ 매핑 단위이면 NAND 프로그램 한계(16 die 합 2,233 MiB/s @32K page, 64K 3,805, 128K 5,871)나 PCIe 한계(3,357 MiB/s)에 가깝다. 실측 4k/4k GC 전 약 2,005–2,008 MiB/s(약 513K IOPS) = NAND 한계의 90 %, 4k/128k 약 2,230 MiB/s.
  - 즉 4K 쓰기도 GC 전에는 CPU 병목이 아니다. Claude 가 처음에 「4K 근처는 CPU 병목」이라고 적은 것은 틀렸다.
  - base 의 bs < 매핑 단위(매핑 ≤ 32K)는 GC 전에 NAND 한계 × bs/MAP 에 머문다(8k/4k 약 1,116–1,128, 16k/4k 약 558, 32k/4k 약 279, 16k/8k 약 1,120 MiB/s). io-worker 의 대기 항목 정렬 삽입(__insert_req_sorted, O(N))이 브레이크 역할을 하기 때문이다. GC 이후에는 백로그가 393 ms 창을 넘으면서 printk 폭주가 일어나 에뮬레이터 산물이 된다.
  - 매핑 64K/128K 의 bs < 매핑 단위는 GC 전에도 printk 에 묶인다(base 128k/4k 26K IOPS vs NAND 기준 47K).
- rmmod 때 파티션 읽기 실패(base 의 bs < 매핑 회차에서만 관찰): "ldm_validate_partition_table(): Disk read failed. / Dev nvme1n1: unable to read RDB block 0 / nvme1n1: unable to read partition table / partition table beyond EOD, truncated". fio 가 장치를 닫은 뒤 udev 가 파티션을 다시 읽는데, 그 읽기가 NVMeVirt 워커 큐의 미래 시각 작업 뒤에 밀려 있다가 rmmod 로 실패한 것이다. fio-end 표지 이후의 일이라 측정값에는 영향이 없다. analyze 의 kernel_warn 으로 센다.
- 반복 간 편차: 4k/4k 20 s A/B 에서 약 0.2–0.3 %(randrepeat=1 이므로 같은 주소 순서).

### 8.4 기하 구조 (감사 계산 + 적재 로그로 확인)
- storage_size = 12 GiB − 1 MiB = 12,883,853,312 B. 파티션 4 개, 파티션당 3,220,963,328 B, 채널 2 · LUN 2 → LUN 4. blk_size 원시값 = DIV_ROUND_UP(3,220,963,328, 384×4) = 2,096,982 B 가 oneshot page 단위로 올림되어 정확히 2 MiB 다. 파티션당 line 384 개, line = 블록 4 개 = 8 MiB, 물리 12 GiB(3,072 MiB × 4).
- OP: pba_pcent = (int)(1.07×100) = 107. 논리 = 12,883,853,312×100/107 = 12,040,984,403 B. nsze = 23,517,547 LBA → 장치 12,040,984,064 B = 11,483.18 MiB(dmesg "ns 0/1: size 11483 MiB"). 실효 OP 7.01 %.
- 매핑 단위별 (secs_per_pg | pgs_per_oneshotpg | pgs_per_blk | pgs_per_line | 파티션당 tt_pgs | GLOBAL_WB_SIZE):
  - 4K 8|8|512|2048|786,432|1 MiB
  - 8K 16|4|256|1024|393,216|1 MiB
  - 16K 32|2|128|512|196,608|1 MiB
  - 32K 64|1|64|256|98,304|1 MiB
  - 64K 128|1|32|128|49,152|2 MiB
  - 128K 256|1|16|64|24,576|4 MiB
- 채널 모델: NAND 채널 800 MB/s → max_credits 26/4 µs, tx 152 ns/128 B (≈793 MiB/s). PCIe 3360 → 110/4 µs, 36 ns/128 B (≈3,357 MiB/s). MDTS 6 + MPSMIN 0 → 256 KiB 이므로 128 KiB 요청은 명령 1 개다.
- 모델상 호스트 지연 하한(조기 완료): 4000 + 460×ceil(bs/4K) + 36×bs/128 ns → 4K 5.6 µs … 128K 55.6 µs. PCIe 한계 IOPS: 4K 859K … 128K 26.9K.

### 8.5 블록 계층이 순차 요청을 합친다 (순차 쓰기 실험에서 발견, 20:18 KST)
- NVMeVirt 장치(/dev/nvme1n1)의 큐 설정은 커널 기본값이다: scheduler mq-deadline, nomerges=0, max_sectors_kb=256, write_cache "write through".
- 이 설정에서 fio 의 순차 4K 쓰기(QD 32, libaio, direct)는 블록 계층에서 크게 합쳐진다. 사전 점검 A(7.1 절)에서 평균 요청이 약 120 KiB 였다. 그대로 두면 순차 쓰기의 bs 축이 의미를 잃는다.
- 그래서 순차 쓰기 실험은 회차마다 insmod 직후 nomerges=2 로 합치기를 끈다. 회차마다 meta.txt 의 blk_writes 로 합쳐진 수(0)를 확인한다.
- 랜덤 쓰기 실험(main3x3, main)은 커널 기본값으로 했다. 그래도 인접한 요청이 거의 없어 합쳐지지 않는다(사전 점검 C: 15 s 동안 fio 쓰기 요청 1,144,511 개 중 합쳐진 것 1 개, 장치가 받은 요청 1,144,510 개). 따라서 그 결과는 유효하다.

### 8.6 NVMeVirt 는 매핑 단위보다 작은 쓰기를 합치지 않는다 (모델 한계, 순차 쓰기에서 결정적)
- conv_write() 는 명령마다 그 명령이 걸친 lpn 을 각각 새 페이지에 쓴다. 매핑 16K 에서 같은 16K 단위로 4K 쓰기 4 개가 연달아 와도 16K 페이지를 4 번 쓴다. 쓸 때마다 앞의 것은 무효가 된다.
- 랜덤 쓰기에서는 다음 쓰기가 다른 단위로 가므로 실제 SSD 도 단위를 새로 써야 한다(RMW). 차이는 RMW 읽기가 없다는 것뿐이다.
- 순차 쓰기에서 실제 SSD 는 쓰기 버퍼에서 4 개를 합쳐 한 번 쓴다. wbuffix 모델은 합치지 않으므로, bs < 매핑 단위 순차 쓰기는 host WAF 가 매핑/bs 배(4·8·2)가 된다. GC 이전 구간의 대역폭은 NAND 한계 × bs/매핑으로 떨어지고, 여기에 GC 증폭이 더해져 60 s 평균은 merge 의 1/6.25·1/10.0·1/6.05 가 된다(7.1 절 B, 8.7 절).
- merge 변형(5.6 절)이 이 한계를 보완한 모델이다. 논문에는 「NVMeVirt 원래 모델(wbuffix)」과 「병합 모델(merge)」을 함께 보이고, 병합 모델은 이 연구에서 추가한 것임을 밝힌다.

### 8.7 순차 쓰기 결과 해석 (실험 후 작성)
(exp/report/findings_seq_ko.txt 와 같은 내용이며 docx 1.5·8.8 절에도 들어간다. 그 파일의 「8.3 절」은 docx 의 사전 점검 절이고, 여기서는 md 의 7.1 절로 바꿔 적었다. 근거 수치는 results/seq3x3_20261008/analysis/summary_agg.csv 다.)
- 순차 쓰기에서 bs ≥ 매핑 단위인 조합은 두 모델 모두 60 s 평균 2,087–2,233 MiB/s 다. bs 16K·32K 는 2,232.2–2,232.8 MiB/s 로, NAND 프로그램 한계(16 die 합 2,233 MiB/s)의 99.96 % 이상이다. bs 4K 는 매핑 4K(두 모델)와 병합 모델의 매핑 16K·32K 에서 약 535 K IOPS, 2,087–2,095 MiB/s(한계의 93.4–93.8 %)에서 멈춘다(요청 수 처리 쪽 한계로 보인다 — 추정). 이 조합들에서 두 모델의 차이는 최대 0.14 % 로, 반복 편차(변동계수 최대 0.40 %) 수준이다. 두 모델이 같은 코드 경로를 쓰기 때문이다.
- 원래 모델(wbuffix)에서 bs < 매핑 단위인 순차 쓰기는 크게 느려진다. 16K/4K 334.9, 32K/4K 209.5, 32K/16K 369.0 MiB/s 로, 같은 bs 의 매핑 4K 대비 −84.0 %, −90.0 %, −83.5 % 다. NVMeVirt 는 같은 매핑 단위로 이어지는 작은 쓰기를 합치지 않고 쓰기마다 매핑 단위 페이지를 새로 쓰기 때문이다. GC 이전 구간도 NAND 한계 × bs/매핑의 99.4–99.8 %(556.1, 278.5, 1,109.9 MiB/s)에 머문다.
- 쓰기 버퍼 병합 모델(merge)에서는 이 불이익이 사라진다. 16K/4K 2,094.4, 32K/4K 2,094.6, 32K/16K 2,232.2 MiB/s 로, 같은 bs 의 매핑 4K(2,086.7 / 2,086.7 / 2,232.7) 대비 +0.37 %, +0.38 %, −0.02 % 다. wbuffix 보다는 6.25 배, 10.00 배, 6.05 배 빠르다. 즉 순차 쓰기는 쓰기 버퍼가 작은 쓰기를 합치기만 하면 매핑 단위를 16K·32K 로 키워도 대역폭 손실이 없다.
- WAF_total 은 병합 모델에서 9 조합 모두 1.000 이다. 원래 모델은 bs ≥ 매핑에서 1.000, bs < 매핑에서 16K/4K 5.404, 32K/4K 9.155, 32K/16K 3.405 다. 원래 모델의 값은 부분 쓰기 증폭(매핑/bs = 4·8·2 배)과 GC 증폭(1.351, 1.144, 1.702)의 곱이다. GC 증폭은 매핑 단위마다 마지막 판 하나만 유효하게 남기 때문에 생긴다. 16K/4K·32K/4K 는 단순 계산 1/(1 − bs/매핑) = 1.333·1.143 과 거의 같고, 32K/16K 는 단순 계산 2.000 보다 작다.
- 랜덤 쓰기와 비교하면 같은 조합에서 순차 쓰기(merge)가 bs ≥ 매핑에서 4.6–5.3 배, bs < 매핑에서 10.2–30.7 배 빠르다. 랜덤 쓰기(주 데이터셋 nodrop)는 bs ≥ 매핑에서 GC 복사 때문에 416–482 MiB/s(WAF 3.1–3.5)다. 랜덤 쓰기의 bs < 매핑 손실(−54–84 %)은 다음 쓰기가 다른 매핑 단위로 가서 합칠 것이 없으므로 쓰기 버퍼 병합으로도 줄지 않는다(7.1 절 C: merge −0.7 %). 반면 순차 쓰기의 손실은 병합으로 없어진다.
- 병합 통계(3 회 평균)에서 열린 단위 하나당 합류 횟수는 16K/4K 3.000, 32K/4K 7.000, 32K/16K 1.000 으로 매핑/bs − 1 과 정확히 같다. 덜 찬 채 쓴 단위(evict)는 회차당 169·37·11 개로, 연 단위의 0.0003–0.002 % 뿐이다. 장치 끝에서 처음으로 돌아갈 때 생기고, 4K 에서 더 많은 것은 드물게 요청 순서가 바뀌기 때문으로 보인다(추정).
- 순차 쓰기에서는 GC 가 거의 비용 없이 일어난다. bs ≥ 매핑과 병합 모델에서 GC 는 회차당 victim line 약 14,100–15,200 개를 지우지만 옮긴 페이지는 0 이다. 앞 바퀴의 line 이 통째로 무효가 되기 때문이다. 첫 GC 는 5.69–5.93 s 에 시작한다. bs 16K·32K 는 GC 전후 대역폭이 같고(약 2,233 MiB/s), bs 4K 는 GC 이후 약 3 % 낮다(2,142–2,152 → 2,081–2,089 MiB/s). 60 s 동안 122–131 GiB, 장치를 약 11 바퀴 쓴다.
- 평균 완료 지연은 iodepth 32 ÷ IOPS 로 정해진다(bs 4K 약 59 µs, 16K 222.5 µs, 32K 446 µs). p99 는 bs ≥ 매핑과 병합 모델에서 453 µs 이하다. 원래 모델의 bs < 매핑은 16K/4K 3,643 µs, 32K/4K 2,256 µs, 32K/16K 8,356 µs 다. 랜덤 쓰기의 p99(13–18 ms)보다는 짧다.
- 반복 간 대역폭 편차는 매우 작다. 변동계수 평균은 0.067 %(wbuffix)·0.051 %(merge)이고, 최대는 0.40 %(wbuffix 4K/4K)다.
- 해석 시 주의할 점이 있다. 병합 모델은 이 연구에서 추가한 것이다. 파티션마다 열린 단위가 1 개이고, 덜 찬 단위의 RMW 읽기는 없으며, 하나의 순차 흐름을 가정한다. 따라서 이 결과는 병합이 잘 될 때의 상한에 가깝다. 여러 흐름이 섞이거나 쓰기 버퍼가 작으면 실제 SSD 의 이득은 이보다 작을 수 있다. 원래 NVMeVirt 모델(wbuffix)의 결과는 병합이 전혀 없는 SSD 의 하한으로 읽는다. 모든 순차 쓰기 결과는 블록 계층 병합을 끈 상태(nomerges=2)에서 쟀다. 커널 기본값이면 순차 요청이 블록 계층에서 합쳐져 bs 축이 의미를 잃는다(7.1 절 A, 8.5 절).

### 8.8 랜덤 쓰기 bs 8K·64K 결과 해석 (실험 후 작성)
(exp/report/findings_randbs_ko.txt 와 같은 내용이며, docx 1.6 절과 9.5 절에도 들어간다. 표기는 매핑/bs 다. 그 파일의 「5.5 절」은 docx 의 「결과 해석 시 주의할 모델 특성」 절이고, 여기서는 md 의 8.3 절로 바꿔 적었다. 근거 수치는 results/rand3x5_20261008/analysis/summary_agg.csv 와 randbs_20261008/analysis/ 다.)
- bs 8K 에서 대역폭은 매핑 4K 437.0, 16K 217.3, 32K 131.9 MiB/s 다. 매핑 4K 대비 −50.3 %, −69.8 % 다. bs 64K 에서는 486.3, 486.4, 447.1 MiB/s 로, 매핑 16K 는 4K 와 같고(+0.02 %) 32K 는 −8.1 % 다.
- 결과는 bs 의 절대 크기보다 bs/매핑 비율로 거의 정해진다. 비율이 같은 조합끼리는 대역폭이 3 % 안에서 같고 WAF_total 도 거의 같다(표기는 다른 곳과 같이 매핑/bs). 비율 1(4K/4K, 16K/16K, 32K/32K)은 416.0·420.4·424.6 MiB/s, WAF 3.12 다. 비율 2(4K/8K, 16K/32K, 32K/64K)는 437.0·441.6·447.1 MiB/s, WAF 3.31–3.32 다. 비율 4(4K/16K, 16K/64K)는 481.0·486.4 MiB/s 다. 비율 1/2(16K/8K, 32K/16K)은 217.3·219.6 MiB/s, WAF 5.90·5.96 이고, 비율 1/4(16K/4K, 32K/8K)은 129.7·131.9 MiB/s, WAF 8.82·8.97 이다. flash page 는 모든 조합에서 32 KiB 로 같다.
- bs ≥ 매핑인 10 조합은 416.0–486.4 MiB/s, WAF_total 3.12–3.55 다. 같은 bs 에서 매핑 4K 대비 차이는 −12.6 %(bs 16K, 매핑 16K)에서 +0.02 %(bs 64K, 매핑 16K) 사이다. 매핑 4K 는 bs 를 4K → 64K 로 키우면 416.0 → 486.3 MiB/s(+16.9 %)로 오른다.
- bs < 매핑인 5 조합의 대역폭은 같은 매핑에서 bs = 매핑일 때의 0.16–0.52 배로, 조합마다 bs/매핑(0.125–0.5)보다 조금 크다. WAF_total 은 부분 쓰기 증폭(매핑/bs = 2·4·8 배)과 GC 증폭(2.1–3.0)의 곱이다. 16K/8K 는 5.90 = 2 × 2.95, 32K/8K 는 8.97 = 4 × 2.243 이다.
- GC 이전 구간은 NAND 프로그램 한계로 정해진다. bs ≥ 매핑에서는 2,001–2,218 MiB/s 이고, bs < 매핑에서는 한계 × bs/매핑의 92–96 % 다(예: 16K/8K 1,072.0, 32K/8K 512.6 MiB/s). 첫 GC 는 모든 조합에서 5.69–6.32 s 에 시작한다. GC 이후 구간 평균은 bs ≥ 매핑에서 240–312 MiB/s, bs < 매핑에서 47–131 MiB/s 다.
- 평균 완료 지연은 iodepth 32 ÷ IOPS 로 정해진다. bs 64K 는 4.1–4.5 ms 다. p99 는 bs 가 커질수록 늘어, bs 4K 에서 13.3–14.5 ms, bs 64K 에서 19.0 ms(세 매핑 모두)다.
- 반복 간 대역폭 편차는 작다. 새로 잰 18 회의 6 조합은 변동계수 평균 0.083 %, 최대 0.280 %(4K/8K)다. 주 데이터셋 회차를 포함한 15 조합은 평균 0.123 %, 최대 0.375 %(4K/4K)다.
- 블록 계층 병합은 무시할 수 있다(커널 기본값, 주 데이터셋과 같은 설정). 새 회차에서 합쳐진 요청은 bs 8K 의 매핑 4K 에서 가장 많았는데, 회차당 약 1,800 건으로 요청의 0.054 % 다. 나머지 회차는 0–361 건(0.022 % 이하)이고, 장치가 받은 평균 요청 크기와 bs 의 차이는 최대 0.004 KiB 다.
- 해석: 랜덤 쓰기에서 매핑 단위를 키울 때의 손실은 호스트 쓰기가 매핑 단위보다 작을 때만 생기고, 그 크기는 bs/매핑 비율이 정한다. 쓰기 크기가 매핑 단위 이상이면 매핑 16K·32K 도 매핑 4K 와 비슷한 성능(최대 −12.6 %)을 낸다. 다만 NVMeVirt 는 부분 쓰기의 RMW 읽기를 모델링하지 않으므로, bs < 매핑의 불이익은 실제 SSD 보다 작게 나올 수 있다(8.3 절).

---------------------------------------------------------------------------------------------------

## 9. 감사 워크플로 (wf_b41bb861-a42) 요약

- 스크립트: /home/dccearth/.claude/projects/-home-dccearth-jsw-KSC2026-nvmevirt-upstream-tmp/13edeb42-0011-48bf-800d-a7f7e0251b76/workflows/scripts/ksc2026-nvmevirt-understand-audit-wf_b41bb861-a42.js. 기록은 /home/dccearth/.claude/projects/-home-dccearth-jsw/13edeb42-0011-48bf-800d-a7f7e0251b76/subagents/workflows/wf_b41bb861-a42/journal.jsonl 에 있다.
- 단계: Read(설정조사 보고서 → 설정 사양, 논문 → 연구 맥락) / Audit(렌즈 3 개: wbuf-write-path, geometry-init, gc-timing) / Verify(blocker·high·medium 주장마다 반박 시도 2 개: 코드 경로 추적, 수치 예시 대조).
- 주요 주장(심각도):
  - [blocker] 쓰기 버퍼 과다 반환(8.1) — 세 렌즈 모두 독립적으로 찾았다(검증 6 회 모두 핵심 확인).
  - [high] 그 결과로 NAND 대기열이 끝없이 늘어 io-worker 큐(16384) 고갈, 393 ms 채널 창 초과, O(N) 비용이 생긴다.
  - [high] 64K/128K flash page 변경에 따른 NAND 대역폭·버퍼 변화(8.2).
  - [high] 조기 완료 때문에 GC 가 버퍼 정체로만 보인다.
  - [high] 장치는 모델명으로 찾아야 한다(루트가 nvme0n1). 이미 반영했다.
  - [medium] RMW 미모델, DFTL 없음, 60 s 창에서 GC 시작 시점이 달라 GC 전후 구간이 섞임(시계열·GC 시각 기록으로 대응), 워커 1 개만 활성(fio 고정 권고 — 고정은 하지 않음. 큐가 1 개라 워커가 바뀌지 않는다), 64K/128K 에서 FLASH_PAGE_SIZE 를 안 바꾸면 assert(이미 반영).
  - [info] assert 전부 통과, 블록 2 MiB·용량·OP 가 모든 매핑에서 같음, MAX_CH_XFER_SIZE 는 쓰기에 무관, MDTS 로 128k 가 분할되지 않음, rmmod/insmod 가 FTL 을 완전히 초기화(저장 데이터는 남음), 4KB 전용 상수(ssd.c 394, conv_ftl.c 867)는 쓰기 전용 실험에 무관.
- 워크플로 완료: 15:22 KST, 에이전트 51 개(오류 0), 하위 에이전트 토큰 약 4.94 M, 소요 약 92 분.
  - 결과 원본: exp/report/audit_result.json (spec = 설정조사 보고서에서 뽑은 기본값 전체, ctx = 논문 맥락, audit = 렌즈별 주장·검증 판정)
  - 한국어 요약: exp/report/audit_summary_ko.txt (docx 부록 E)
- 검증 판정 요약: 핵심 주장은 하나도 뒤집히지 않았다. 「refuted」로 표시된 판정은 모두 세부 정정이다. 주요 정정:
  - (a) GC 전 4k/4k 는 CPU 병목이 아니라 NAND 한계의 90 %
  - (b) base 의 bs<MAP(MAP≤32K)는 GC 전에 NAND×bs/MAP 에 머문다
  - (c) 워커 선택은 큐가 1 개라 고정이다(IRQ 15 → cpu5)
  - (d) bs≥MAP 의 GC 영향은 버퍼 정체 재시도 + do_gc CPU 시간으로 나타난다
  - (e) randommap 주기: 둘째 바퀴 끝에 WA 약 1.5, bs<MAP 는 WA 7.6–8.4 까지 상승
  - (f) WB-2 의 「무한 증가」는 O(N) 브레이크 때문에 GC 전에는 제한된다

### 9.1 merge 코드 검토 워크플로 (wf_b32d4ebd-f50, 20:01–20:13 KST)
- 목적: 새 커널 코드(WBUF_MERGE)를 서버에서 돌리기 전에 독립적으로 검토한다.
- 구성: 검토자 4 명이 관점 하나씩 맡았다(쓰기 버퍼 장부·back-pressure / FTL 상태 정확성 / 실험에 맞는 모델 동작 / 커널 안전성·빌드). 지적마다 반박 검증자 1 명을 두었다. 에이전트 5 개, 오류 0.
- 결과: 고칠 결함 없음.
  - 버퍼: sim_open 재현이 실제 결정과 같고, 할당과 반납이 균형을 이룬다는 것을 귀납으로 증명했다. 할당·반납 로직을 Python 으로 옮겨 퍼징했다(MU 3 종 × 시드 30 × 명령 2 만, 정렬·비정렬·여러 단위·여러 파티션). 불변식 위반은 없었고, 오래 붙잡히는 버퍼는 128 KiB 이하였다.
    - MDTS 6(256 KiB)이라 한 명령의 최대 할당은 288 KiB 이고, NVMEV_ASSERT(size ≤ buf->size)에 걸리지 않는다.
  - FTL: ksc_write_lpn 은 원본 루프 본문과 의미가 같다. 열린 lpn 의 옛 복사본을 foreground GC 가 옮겨도 커밋할 때 maptbl 을 다시 읽으므로 일관성이 유지된다. 열린 lpn 을 읽으면 옛 페이지를 읽으며, crash 경로는 없다.
  - 모델: 순차 bs 4K·MU 16K(이 파일 표기 16K/4K) → 단위마다 open 1·merge 3·full 1, bs 4K·MU 32K(32K/4K) → open 1·merge 7·full 1, bs 16K·MU 32K(32K/16K) → open 1·merge 1·full 1. bs ≥ MU 이면 단위가 한 번도 열리지 않아 WBUF_FIX 와 같다. 랜덤 4K 는 쓰기마다 evict+open 이다.
  - 커널: 형식 지정자·타입·비트맵 범위(MU 128K 까지)·스택 사용에 문제가 없다. WBUF_MERGE=0 빌드는 디스어셈블리가 같다(5.6 절).
- 지적 1 건(모델 렌즈, minor): FUA/FLUSH 가 열린 단위를 flash 로 내보내지 않는다.
  - 검증자 판정: 원본 conv_write 도 FUA 때 이 명령이 일으킨 프로그램만 기다리고, conv_flush 도 덜 찬 wordline 을 쓰지 않는다. 그래서 원본과 같은 단순화이며 결함이 아니다(real=false).
  - VWC=0 이라 커널이 FUA·FLUSH 를 보내지 않으므로 실험과도 무관하다.
  - 조치: 코드 주석만 보강했다.
- 원본 journal: 서버의 ~/.claude/projects/-home-dccearth-jsw/13edeb42-…/subagents/workflows/wf_b32d4ebd-f50/journal.jsonl (묶음에는 없음).

### 9.2 순차 쓰기 기록 검증 워크플로 (wf_7abaf97b-cba, 21:3x–22:1x KST)
- 구성: 검사자 5 명(수치 / md 서술 / docx 서술·절 번호 / 재현성·스크립트 / 보안·KST), 검사자마다 반박 검증자 1 명. 에이전트 10 개, 오류 0.
- 지적 49 건(medium 11, low 38), 반박 검증 결과 39 건 확인, 10 건 기각. 확인된 것은 22:12–22:17 에 모두 고쳤다(커밋 a86fc87 뒤에 고쳤고, 커밋 403a6ae 에 들어갔다).
  - 수치: md 0 절 WAF 9.16/3.41 → 9.15/3.40(이중 반올림). findings 의 bs 4K 범위 문장이 대상 집합과 어긋난 것, 랜덤 416–482 MiB/s 에 「bs ≥ 매핑」 한정이 빠진 것. 사전 점검 C 의 「N 개 중 1 개」에서 N 을 fio 요청 수 1,144,511 로 고침.
  - md: 8.7 의 절 번호(docx 의 8.3 → md 의 7.1), 7.1 시각(19:58 작성, 20:00:53 검토 시작), 10.4 시각(analyze 21:26:45, plot·gallery 21:27:38–42, findings 21:29:43), 1.18 의 「8 개 명령」→ 10 개 중 8 개 확인, 5.6 의 FLUSH 설명(conv_flush 는 예약된 NAND 작업을 기다림), 6.6 의 결과·로그 이름·「[i/N]」 설명, 9.1 의 표기, 7.1 의 evict 설명(16K/4K 의 18 개는 순서 바뀜으로 추정).
  - docx: 3.3·10 절(검증 당시에는 9 절, 「실험 후 상태와 정리」) sudoers 이력에 제거 시각을 반영했다(KSC_SUDOERS_REMOVED2). push 예정 문구는 origin/main 을 읽어 쓰게 했다. 4.3 에 `bash build_modules.sh wbuffix` 줄을 추가하고 tee 로그 이름을 고쳤다. 4.4 job 틀 이름, 3.2·부록 A 의 findings_seq_ko.txt, 8.2 퍼징 규모(약 180 만 명령), 1.3 시각을 고쳤다. 원래부터 틀렸던 절 참조 세 곳(5.5→5.4, 6.3→7, 6.4→6.3)도 고쳤다.
  - 스크립트: build_modules.sh 사용법에 merge 를 추가했다. run_all_seq.sh 에 [i/N] 설명 주석을 달았다.
- 기각된 것: collect_env.sh 의 rm 범위, sudoers 와일드카드, git checkout 줄, env 비교 문단 등. 문서나 코드가 이미 맞았다.

### 9.3 랜덤 bs 8K·64K 기록 검증 워크플로 (wf_b166ccdc-994, 22:40–23:1x KST)
- 구성: 검사자 4 명(수치 / md 서술 / docx 서술·절 번호 / 스크립트·재현성·보안), 검사자마다 반박 검증자 1 명. 에이전트 8 개, 오류 0.
- 지적 33 건(high 1, medium 4, low 28), 반박 검증 결과 30 건 확인, 3 건 기각. 확인된 것은 23:1x KST 에 모두 고쳤다(다음 커밋에 들어감).
- 측정값은 틀린 것이 없었다. 수치 검사자가 randbs 18 회의 summary_runs.csv 모든 열을 원자료에서 다시 계산했고(불일치 0), rand3x5 의 15 조합이 주 데이터셋 9 조합·randbs 6 조합과 같음을 확인했다. md 11.4·11.5 절과 docx 9 장 표의 모든 칸도 CSV 와 맞았다.
- **보안(high) — make_handoff.sh 의 git 이력 credential 검사가 fail-open 이었다.**
  - 원인: `set -o pipefail` 아래에서 `if git log -p --all | grep -qE "$CRED_PAT"; then 차단`. 일치가 있으면 grep -q 가 첫 일치에서 끝나고, git 이 SIGPIPE(141)로 죽어 파이프라인 상태가 0 이 아니게 된다. 그래서 if 가 거짓이 되어 **이력에 credential 이 있을 때 오히려 통과**한다. 이 코드는 16:0x KST 부터 있었으므로, 그동안 만든 모든 묶음의 「git 이력 검사」는 실제로는 이력을 막지 못하는 상태였다.
  - 실제 피해는 없다. 검사자가 실행 시 뽑은 실제 패턴으로 `git log -p --all`·작업 트리·메모리 노트·docx 본문을 따로 검사해 0 건을 확인했다. 18:27 KST 에도 모든 git 객체를 검사했다(10.3 절). 묶음 파일 검사(guard 2)는 파이프가 아니라 영향이 없다.
  - 수정: 이력을 임시 파일에 쓴 뒤 `grep -c` 로 줄 수를 세어, 0 이 아니거나 숫자가 아니면 중단한다. 고친 뒤 만든 최종 묶음에서 이 검사가 통과했다(= 이력에 패턴 0 건).
- 재현성(medium) — docx 4.3 의 `git checkout e598e75` 로는 같은 블록의 순차·랜덤 bs 명령을 실행할 수 없었다(그 커밋에 스크립트가 없음).
  - 수정: 태그가 없을 때는 main 을, 최종본에서는 새 태그 ksc2026-v2 를 쓰고, 주석에 랜덤 bs 스크립트 커밋 a86fc87 을 넣었다. 태그에는 결과도 들어 있어 같은 실험 이름이면 DONE 회차를 건너뛴다는 안내 줄도 넣었다.
- 그 밖에 고친 것:
  - 스크립트: run_all.sh·run_all_seq.sh·run_all_rand_bs.sh 의 모듈 확인을 SHA256SUMS 존재가 아니라 .ko 파일 존재로 바꿨다(clone 에는 SHA256SUMS 만 있고 .ko 는 없어서, 예전 조건으로는 빌드를 건너뛰고 run_experiment.sh 가 「missing … .ko」로 멈춘다). link_runs.py 는 링크를 만들기 전에 모든 것을 검사하고(중복, 링크가 아닌 폴더), SOURCES.txt 를 보기 아래 실제 링크 전체에서 만든다.
  - 그림: 축 분리 때 fig_timeseries_* 의 크기 계산이 바뀌어, main3x3·main 의 저장된 PNG 4 개만 옛 크기로 남아 있었다. analyze.py 를 다시 돌려 맞췄다(CSV 는 같음).
  - docx: 1.3 표의 실험 끝 시각(22:32:55), 3.2·부록 A 목록의 findings_randbs_ko.txt, 부록 A 의 스크립트 변경 이력 문단, findings 의 「8.97 = 4 × 2.243」.
  - md: 0 절 절 번호(1.20–1.23), 8.8 의 절 번호(docx 5.5 → md 8.3), 10.5 의 끝 시각(22:32:58)과 커밋·docx 기록, 9.2 의 커밋 귀속과 docx 절 번호, 6.4 의 설치·제거 이력, 6.7 의 커밋 귀속, 4 절 .gitignore, H 절의 링크 복구 방법, 갱신 이력.
  - 산출물 사본: KSC2026/산출물/ 의 실험 기록 docx 가 18:35 KST 판으로 남아 있어 묶음의 materials/산출물/ 과 deliverables/ 에 서로 다른 판이 들어갔다. 최종 docx 를 산출물/ 에 다시 복사했다(10.5 절).
- 기각 3 건: 블록 계층 「0.054 %」 표현 2 건(가장 큰 회차의 값이라 맞음), 13 절 sudoers 줄(검사 도중 이미 고쳐짐).

---------------------------------------------------------------------------------------------------

## 10. 본 실험 진행 기록

### 10.1 첫 설계 main_20261008 (보조 데이터셋)

- 14:20:28 시작. base 1/108 14:21:02.
- base 첫 회차들(60 s): 4k/4k r1 418.4 MiB/s 107,109 IOPS clat 297.7 µs, 첫 GC 6.30 s, WAF_gc 3.14 / 4k/8k r1 433.6 MiB/s / 4k/128k r1 496.8 MiB/s 3,974 IOPS clat 8047.2 µs / 8k/4k r1 chmodel_msgs 8,242,206, kernel_warn 1(그 회차의 "No free entry" 표본 줄), rmmod 때 파티션 읽기 실패 4 줄.
- **14:44:22–14:46:57 첫 중단**: base 21/108 회차 map32k_bs16k_r1 에서 fio 가 I/O 오류(fio error 5 = EIO, exit 1)로 실패했다. run_experiment.sh(당시 커밋 5769378)가 die 하면서 run_all.sh(set -e)도 끝났고, tmux 세션 ksc2026 이 종료되었다.
  - 시간선(fio-start 표지 기준, 해당 회차 kernel.log 에서 추출):
    - +5.64 s 첫 GC
    - +24.97 s `WARNING: CPU: 3 PID: 30089 at …/nvmevirt/io.c:302 __allocate_work_queue_entry+0x8a/0xb0 [nvmev]` — "IO queue is almost full" WARN_ON_ONCE. 쓰기 버퍼 과다 반환으로 NAND 완료 시각이 먼 미래인 internal operation 이 io-worker 작업 큐(16384 항목)를 채운 것이다(감사 WB-2/C2 예측과 같음).
    - +55.09 s `nvme nvme1: I/O tag 192 … QID 1 timeout, aborting req_op:WRITE(1) size:16384` (커널 nvme 기본 io_timeout 30 s)
    - +85.29 s `timeout, reset controller` → Abort status 0x371
    - +146.74 s `I/O tag 28 (301c) QID 0 timeout, disable controller` → `Identify Controller failed (-4)` → `Disabling device after reset failure: -5`
    - +146.76 s 이후 `I/O error, dev nvme1n1 … op 0x1:(WRITE)` 10 줄 → fio 종료(runtime 146,507 ms, 그때까지 평균 114.4 MiB/s, 7,319 IOPS, 16.36 GiB). udev 의 파티션 읽기 Buffer I/O error / attempt to access beyond end of device.
    - rmmod 정상("Virtual NVMe device closed"). GC 통계: 파티션별 host_pgs 약 268K, gc_pgs 약 839K, gc_cnt 약 3,946. chmodel_msgs 10,038,918.
  - 판단: 요청 설정 그대로인 base 모델이 bs < 매핑 단위에서 무너지는 현상이므로 그 자체를 결과로 남긴다.
  - 조치(커밋 2a462a3, 14:49):
    - run_experiment.sh 가 fio 실패 회차에 FAILED 표지(첫 줄 `fio_exit=… fio_json_error=… kernel_warn=… chmodel_msgs=…`, 그 뒤 관련 커널 줄 최대 20 개)를 남기고 다음 회차로 넘어가도록 바꿨다. 다시 실행해도 FAILED 회차는 건너뛴다.
    - fio 감시 타이머: RUNTIME + FIO_GRACE(180 s) 에 SIGTERM, 60 s 뒤 SIGKILL. sudo 프로세스로 보내면 sudo 가 fio 에 전달한다.
    - meta.txt 에 git_head 를 추가했다. git_head.txt 는 실행마다 한 줄씩 덧붙인다(base 의 git_head.txt 첫 줄은 손으로 시각을 붙였다: 2026-10-08 14:21:02 KST (파일에는 "2026-10-08T05:21:02+00:00 5769378…" 로 UTC 표기)).
    - nvmevirt_vs_upstream.diff 를 rename 커밋 기준으로 고쳤다.
    - kernel_warn 집계에서 chmodel 표본 줄을 뺐다.
    - analyze.py 가 failed_runs.csv 를 쓰도록 했다(t_gc_s, t_queue_full_warn_s, t_nvme_timeout_s, t_reset_s, t_disable_s, t_first_io_error_s).
    - plot.py, 보고서 생성기, 이 파일도 같은 커밋에 넣었다.
  - map32k_bs16k_r1 은 손으로 FAILED 표지를 만들어 보존했다(첫 줄에 "marked by hand" 명시).
- **14:49:13 재개**(tmux ksc2026): `bash run_experiment.sh main_20261008 wbuffix` → 이어서 `bash run_experiment.sh main_20261008 base`(완료된 20 회와 FAILED 1 회는 건너뜀) → `analyze.py`. 로그는 같은 run_all_main_20261008.log 에 이어 쓴다.
  - 순서를 바꾼 이유: 유효한 데이터셋(wbuffix)을 먼저 확보하기 위해서다.
  - 모듈은 다시 빌드하지 않았다. 14:20 에 빌드한 exp/modules/{base,wbuffix} 를 그대로 써서 base 의 앞 20 회와 같은 바이너리다(sha256 검사).
  - 따라서 실제 실행은 run_all.sh(빌드 → base → wbuffix)와 다르다. base 는 1–20 회(DONE)와 21 번째 map32k_bs16k_r1(FAILED)만 커밋 5769378 스크립트로 실행되었다. 재개 계획이던 base 22–108 회는 wbuffix 도중 15:51:23 설계 변경(1.7)으로 실험을 멈춰 실행되지 않았다. wbuffix 1–53 회는 커밋 2a462a3(→ 18:3x 에 949ae38 로 다시 만듦) 스크립트로 실행되었다. NVMeVirt 소스와 모듈은 같고, 스크립트 차이는 실패 처리·기록 방식뿐이라 측정 절차는 같다.
- 15:51:23 설계 변경(1.7)으로 중단했다. wbuffix 53/108 회차까지 완료(map16k_bs128k_r2 직전). 남은 상태는 0 절과 같다.

### 10.2 최종 설계 main3x3_20261008 (주 데이터셋)
- 16:00:35 시작(tmux ksc2026, 로그 exp/results/run_all_main3x3_20261008.log, 커밋 1d6cd03).
- 16:00:35–17:03:57 KST 54 회 모두 DONE, FAILED 0, 채널 모델 오류 0, kernel_warn 0. 17:03:57 env_after_wbuffix 스냅샷, analyze.py 완료("54 runs, 0 failed").
- 처음 4 회차(map4k_bs4k_r1·map4k_bs16k_r1 의 nodrop·drop, 16:00:36–16:04:08 시작)는 meta.txt git_head 가 1d6cd03 이다. 16:04:44 의 커밋 재작성 뒤 5 번째 회차(wbuffix_nodrop/map4k_bs32k_r1, 16:05:18 시작)부터 50 회의 meta.txt git_head 는 a93ef76 이다. 두 커밋은 코드가 같다. a93ef76 은 18:3x KST 에 e598e75 로 다시 만들어졌다(「갱신 이력」).
- 실험 중 다른 작업(md 편집, 묶음 생성, 문서 생성기 수정)은 nice -n 19 / ionice -c3 로 낮은 우선순위로 했다. fio 는 CPU 0–2, NVMeVirt 는 CPU 3–5 다.

### 10.3 실험 후 정리 기록 (KST)
- 17:04 실험·분석 완료 확인(54/54, FAILED 0). nvmev 모듈은 내려가 있고 tmux 세션은 종료됨.
- 17:05 `plot.py all` 로 두 데이터셋의 표준 그림 25 장씩을 만들었다(results/<EXP>/plots/). findings_ko.txt(결과 해석)를 작성하고 수치를 CSV 와 하나씩 대조했다.
- 17:06 사용자 지시(1.6) 이행:
  - `rm -rf /home/dccearth/jsw/KSC2026/nvmevirt/upstream_tmp`
  - `mv /home/dccearth/jsw/KSC2026/nvmevirt /home/dccearth/jsw/nvmevirt`
  - `rm -rf /home/dccearth/jsw/exp` (180 MB: 이전 iodepth 결과, 예전 스크립트, .venv. 수치는 2.2 절에 보존)
  - `ln -sfn ../nvmevirt/EXPERIMENT_LOG_FOR_CLAUDE.md /home/dccearth/jsw/KSC2026/EXPERIMENT_LOG_FOR_CLAUDE.md`
  - exp/.venv 다시 만들기(requirements.txt)
  - 메모리의 저장소 경로 갱신
- 17:07 `make_report.py results/main3x3_20261008 --supp results/main_20261008` 로 .docx 를 생성했다(주 = main3x3, 보조 = main_20261008).
- 17:08 렌더링을 확인했다.
  - 서버에는 LibreOffice 가 없다. 그래서 LibreOffice AppImage 25.8(still)을 scratchpad 에 풀었다.
  - 모자란 라이브러리(libcairo2, libcups2t64, libx11-xcb1, libxinerama1, libpixman, libxcb-render/shm, libxrender, libavahi)와 fonts-nanum 은 `apt-get download` 로 받아 사용자 공간에 풀었다(시스템 변경 없음).
  - PDF 63 쪽을 그림으로 훑어보았다.
  - 고친 것: 감사 요약의 시각을 UTC → KST 로 바꾸고, 원자료 표의 변형 열 너비를 넓혔다.
  - 목차는 Word 필드라 Word 에서 '필드 업데이트' 를 해야 채워진다(LibreOffice 변환본에서는 빈칸).
- 17:09 검증 워크플로 wf_7f78deeb-8ce 를 시작했다.
  - 검사자 5 개: 수치, docx 서술, md 서술, 재현성, 보안·KST.
  - 각 지적마다 반박 검증 1 회를 거친다.
- 17:09 GitHub push 를 시도하기 전에 확인해 보니 /tmp/ssh-*/agent.* 소켓이 없었다(사용자 SSH 세션 종료로 추정). 사용자에게 `ssh -A` 로 다시 접속해 달라고 요청했다.
- 17:24 사용자 요청 「지금까지 나온 상태를 handoff 파일에 갱신해줘」 → 이 파일을 갱신하고 묶음(라벨 postexp)을 만들었다(검증 전 문서 포함).
- 18:25 검증 워크플로 완료(에이전트 98 개, 오류 0): 지적 93 건 중 89 건 확인(high 8, medium 24, low 57), 4 건 기각. 원본은 서버 scratchpad 의 verify_result.json 이다(묶음에는 없음).
  - 주요 확인 사항:
    - 수치: 반올림 −54.4→−54.3 %, CV 최대 0.38→0.37 %, WAF 범위 3.6→3.5. CSV 가 %.6g 라 일부 칸의 끝자리가 틀렸다.
    - 시각: sudoers 14:10→14:08 / 15:53→15:55, amend 16:06→16:04, 메시지 시각 몇 곳.
    - 낡거나 모순된 문장: base 22–108 회가 실행된 것처럼 쓴 문장, 이미 지운 폴더, 절 번호 참조.
    - 재현 단계: sudoers chown 경로가 옮기기 전 경로, 패키지 설치, https clone, 사전 점검 명령, tee 로그.
    - 보안: make_handoff.sh 검사 패턴에 쪼갠 비밀번호, .git 에 남은 옛 blob, 이 파일 머리말의 사용자 Claude 계정 이메일.
- 18:2x 보안 조치:
  - 16:10·17:24 KST 묶음을 지웠다. 그 안의 repo/exp/report/make_handoff.sh 에 sudo 비밀번호와 서버 IP 앞부분이 쪼갠 문자열로 들어 있었다.
  - make_handoff.sh 는 검사 패턴을 실행할 때 연구 계획 .docx 에서 뽑도록 바꿨다(스크립트·묶음에 credential 없음).
  - 18:27 KST 에 .git 의 옛 blob 0abc072 를 지웠다(resolve-undo 정리 → gc). 모든 git 객체를 검사해 credential 이 없음을 확인했다.
  - 18:3x KST 에 미push 커밋 2a462a3·a93ef76 을 머리말의 사용자 이메일 문구만 뺀 내용으로 다시 만들었다(plumbing: mktree/commit-tree, 원래 작성자·시각·메시지 유지).
    - 2a462a3 → 949ae38, a93ef76 → e598e75. 코드·스크립트는 같다.
    - 원자료(meta.txt·git_head.txt)의 옛 해시 대응은 4 절에 있다.
  - 사용자에게, 지운 묶음을 이미 전달했다면 서버 비밀번호를 바꾸라고 권했다.
- 18:3x 수정 반영:
  - analyze.py 가 CSV 를 최대 정밀도(repr)로 쓰게 하고 두 데이터셋 분석을 다시 돌렸다.
  - findings_ko.txt, make_report.py(위 지적 전부), audit_summary_ko.txt, 이 파일, README.md(GitHub 첫 화면: 존재하지 않는 exp/README.md 링크, 빌드 변형, results 설명)를 고쳤다.
- 18:33 KST sudoers 규칙 제거: `sudo rm /etc/sudoers.d/nvmevirt-exp`(비밀번호 사용). /etc/sudoers.d 에는 README 만 남았고 `sudo -n -l` 은 비밀번호를 요구한다.
- 18:3x 최종 .docx 를 생성했다(KSC_SUDOERS_REMOVED=18:33, KSC_PUSH_TAG=ksc2026-final). md 결과 절(11)과 plot.py 그림도 다시 만들었다. .docx 를 KSC2026/산출물/ 에 복사했다.
- 18:3x 결과(exp/results, 약 25 MB)·모듈 기록(exp/modules/*/SHA256SUMS·build_info·build 로그, .ko 제외)·문서·생성기를 커밋했다. 태그 ksc2026-final 을 붙여 main 과 함께 push 했다(새 agent 소켓 사용). 
- 18:35 KST push 확인: `git ls-remote https://github.com/Sangwon8799/nvmevirt.git` → refs/heads/main = c742c67a421cd81b3ca95adb15f84b045c8edba4. 태그 ksc2026-final(태그 객체 eb4e3d6)도 c742c67 을 가리킨다. 커밋 순서는 5769378 → 949ae38 → e598e75 → c742c67 이다.
  - docx 4.3 의 `git checkout ksc2026-final` 은 c742c67 이다: 실험 스크립트(e598e75 와 같음) + 결과 + 문서 + 생성기.
  - 그 뒤 main 에는 이 파일만 고친 커밋(push 결과·최종 묶음 기록)이 하나 더 있다.
- 18:3x 최종 인계 묶음(라벨 final)을 이 파일과 같은 내용으로 만들었다. 묶음 이름과 시각은 묶음의 README_FIRST.txt 첫 줄에 있다.

### 10.4 순차 쓰기 실험 seq3x3_20261008
- 20:23:24 KST 시작(tmux ksc2026seq, 커밋 66446ea, nomerges=2). 예상 소요 약 64 분(54 회 × 약 71 s).
- 진행(run_all 로그 results/run_all_seq3x3_20261008.log; 실행 중 이름은 seq3x3_20261008.console.log 였고 끝난 뒤 make_md_results.py·make_handoff.sh 가 찾는 run_all_<EXP>.log 로 바꿨다):
  - wbuffix r1 20:23:24–20:33:58 → merge r1 20:33:58–20:44:31 → wbuffix r2 –20:55:05 → merge r2 –21:05:38 → wbuffix r3 –21:16:12 → merge r3 –21:26:45 KST. 한 바퀴(9 회)는 약 10 분 33 초이고, 회차 하나는 약 70 s 다(fio 60 s + 적재·대기·내림).
  - 54/54 DONE, FAILED 0, NOTE/WARNING/ERROR 줄 0, chmodel_msgs 0, kernel_warn 0 이다. 모든 회차의 blk_writes merges 는 0 이고, 평균 요청 크기는 bs 와 같다.
  - 모든 회차의 meta.txt git_head 는 66446ea 이다(변형 폴더 git_head.txt 에 호출마다 한 줄씩, 3 줄).
  - 끝난 뒤 nvmev 는 내려가 있고 tmux 세션도 종료되었다.
  - **env_after 스냅샷 3 개 중복**: run_all_seq.sh 는 모델마다 run_experiment.sh 를 3 번 부른다. 그런데 당시 collect_env.sh 는 파일에 덧붙여 썼으므로(cap 의 `>>`), env_after_wbuffix·env_after_merge 의 각 파일에 바퀴마다 찍은 스냅샷 3 개가 이어져 있다(20:33·20:55·21:16 / 20:44·21:05·21:26 KST). 원자료는 그대로 둔다.
    - 21:3x 에 make_md_results.py·make_report.py 의 전후 비교가 마지막 스냅샷만 쓰도록 고쳤다(last_snapshot()).
    - collect_env.sh 는 앞으로 같은 폴더의 기존 스냅샷 파일을 지우고 새로 쓰도록 고쳤다. 주 데이터셋·보조 데이터셋은 호출이 한 번뿐이라 영향이 없다.
    - 마지막 스냅샷과 env_before 의 차이는 08_nvmevirt_git.txt 의 작업 트리 수정 표시(실험 중 Claude 가 문서를 편집함)와 09_block.txt 의 시스템 디스크 사용량(122.10 → 122.11 GB)뿐이다.
- 21:26:45 KST analyze.py(run_all_seq.sh 마지막 단계; "54 runs, 0 failed"). 21:27:38–21:27:42 plot.py all(25 장), make_gallery.py → results/seq3x3_20261008/gallery_seq3x3_20261008.html(40 장, 5.6 MB).
- 21:28–21:29 findings_seq_ko.txt 작성(파일 시각 21:29:43 KST). 수치는 summary_agg.csv 에서 다시 계산해 대조했다.
- 21:3x docx 생성(82 쪽)과 LibreOffice 렌더링 확인. 한글 글꼴은 scratchpad 의 fonts-nanum 을 FONTCONFIG_FILE 로 지정해 보였다. 문서 검증 워크플로 wf_7abaf97b-cba 를 시작했다(검사자 5 개: 수치, md, docx, 재현성, 보안·KST; 지적마다 반박 검증 1 개).
- 21:34:17 KST sudoers 제거: 사용자가 `sudo rm /etc/sudoers.d/nvmevirt-exp` 를 실행했다(/etc/sudoers.d 수정 시각 12:34:17 UTC). Claude 가 확인했다: /etc/sudoers.d 에는 README 만 남았고, `sudo -n -l /usr/sbin/insmod` 는 허용되지 않는다.

### 10.5 랜덤 쓰기 bs 8K·64K 실험 randbs_20261008
- 22:11:48 커밋 a86fc87(순차 쓰기 결과·문서 진행본, run_all_rand_bs.sh·link_runs.py, analyze.py·plot.py·make_md_results.py 축 분리; 순차 쓰기 기록 검증 반영 전). 그 커밋으로 실행했다.
- 22:11:48 KST 시작(tmux ksc2026rbs). 18 회, 예상 약 21 분.
- 진행(로그 results/run_all_randbs_20261008.log, UTC): 22:11:48 env_before → 18 회(반복 1→3 × 매핑 4K→32K × bs 8K→64K, 회차당 약 70 s) → 22:32:55 env_after_wbuffix, analyze.py("18 runs, 0 failed") → link_runs.py → results/rand3x5_20261008 에 45 회 링크(주 데이터셋 wbuffix_nodrop 27 + randbs 18, SOURCES.txt) → analyze.py("45 runs, 0 failed"). 22:32:58 KST 에 끝났다(RBS-ALL-DONE; rand3x5 의 summary_agg.csv 는 22:32:56).
  - 18/18 DONE, FAILED 0, NOTE/WARNING/ERROR 0, chmodel 0, kernel_warn 0. 모든 회차의 meta.txt git_head 는 a86fc87 이다. nvmev 는 내려가 있고 tmux 세션도 끝났다.
  - 블록 계층(nomerges 0, mq-deadline): 4K/8K 회차당 1,774–1,817 건(요청의 0.053–0.054 %), 16K/8K 288–361 건(0.017–0.022 %), 나머지 0–1 건이 합쳐졌다.
- 22:33–22:3x analyze.py results/seq3x3_20261008 다시 실행(그림 제목 수정; summary_agg.csv 는 바이트 단위로 같음). plot.py all(seq3x3·randbs·rand3x5 각 25 장), make_gallery.py(seq3x3 40 장, randbs·rand3x5 각 32 장). findings_randbs_ko.txt 작성.
- 22:37 docx 생성(--seq --rbs --rview; 91 쪽; 9 장 = 랜덤 bs 8K·64K, 10 장 = 실험 후 상태와 정리)과 렌더링 확인. 22:38:23 커밋 403a6ae(랜덤 bs 8K·64K 결과, rand3x5 보기, 순차 쓰기 기록 검증 반영 39 건, make_report.py 축 분리; 로컬). 22:38:37 검증 전 묶음 ksc2026_handoff_20261008_2238_seq_randbs_wip.tgz 를 만들어 구조를 확인했다(전달용 아님; 최종 묶음을 만든 뒤 지운다).
- 22:40 기록 검증 워크플로 wf_b166ccdc-994 시작(9.3 절).
- 23:08:30 KST sudoers 제거: 사용자가 `sudo rm /etc/sudoers.d/nvmevirt-exp` 를 실행했다(/etc/sudoers.d 수정 시각 14:08:30 UTC). Claude 가 확인했다: /etc/sudoers.d 에는 README 만 남았고, `sudo -n -l /usr/sbin/insmod` 는 허용되지 않는다.
- 23:10–23:2x 검증 워크플로 결과 반영(9.3 절): make_handoff.sh 이력 검사 수정, run_all*.sh 모듈 확인, link_runs.py, main3x3·main 의 fig_timeseries PNG 다시 생성, docx 생성기·findings·이 파일 수정.
  - 23:20 고친 make_handoff.sh 를 scratch 출력으로 시험했다. 실제 패턴으로는 통과했고(이력·파일 0 건), 이력에 실제로 있는 문자열을 패턴으로 주면 「2 line(s)」로 중단했다.
- 23:2x 최종 docx 생성: `KSC_PUSH_TAG=ksc2026-v2 KSC_SUDOERS_REMOVED=18:33 KSC_SUDOERS_REMOVED2=21:34 KSC_SUDOERS_REMOVED3=23:08 make_report.py results/main3x3_20261008 --supp results/main_20261008 --seq results/seq3x3_20261008 --rbs results/randbs_20261008 --rview results/rand3x5_20261008`. 92 쪽. 렌더링으로 4.3 절 재현 명령과 10 장 sudoers 이력을 확인했다. 같은 파일을 /home/dccearth/jsw/KSC2026/산출물/ 에 복사했다(18:35 KST 판을 덮어씀).
- 23:21 KST 커밋 c9dfb23(순차 쓰기·랜덤 bs 8K·64K 결과와 문서 최종본, 검증 반영)과 주석 태그 ksc2026-v2(→ c9dfb23)를 만들었다. 둘 다 로컬이다.
- 23:22 KST GitHub push 시도 실패: `git@github.com: Permission denied (publickey)`. forwarded ssh-agent 소켓이 없었다. 사용자의 23:08 SSH 세션(pts/0)은 접속 직후 끝났다(`last`: 14:08–14:08 UTC).
  - 이 시점 GitHub 상태(`git ls-remote https://github.com/Sangwon8799/nvmevirt.git`): main = cd1fe2b, 태그 ksc2026-final = c742c67. 즉 GitHub 에는 18:36 KST 상태(랜덤 쓰기 주 데이터셋)까지만 있고, 66446ea·a86fc87·403a6ae·c9dfb23 과 태그 ksc2026-v2 는 아직 없다.
  - docx 4.3 절의 `git checkout ksc2026-v2` 와 10 장 표의 「GitHub main 과 태그 ksc2026-v2 로 push」 문구는 push 직전에 만든 것이다. push 가 끝나기 전에는 사실이 아니다. push 결과는 이 항목 아래 줄에 적는다(줄이 없으면 아직 push 전이다).
  - 묶음의 repo.gitbundle 에는 위 커밋과 태그가 모두 들어 있으므로, 묶음을 받은 쪽은 GitHub 와 무관하게 전부 볼 수 있다.

---------------------------------------------------------------------------------------------------

## 11. 결과

<!-- AUTO-RESULTS-BEGIN -->
(이 절의 시각은 모두 KST 다. 서버 로그의 UTC 시각을 +9 시간 변환했다.)
자동 생성: exp/report/make_md_results.py results/main3x3_20261008 results/main_20261008 results/seq3x3_20261008 results/randbs_20261008 results/rand3x5_20261008 (첫 번째 = 주 데이터셋)

## 11.1 main3x3_20261008  (묶음 경로 repo/exp/results/main3x3_20261008/)

### 11.1.1 회차 목록
- wbuffix_drop: 완료 회차 27 (DONE 있음). run.log 첫 시각 2026-10-08 16:00:35 KST, 마지막 시각 2026-10-08 17:03:57 KST. chmodel 오류 줄 합계 0. chmodel>0 회차 0. kernel_warn>0 회차 0.
  - 미완료/없음 0: -
- wbuffix_nodrop: 완료 회차 27 (DONE 있음). run.log 첫 시각 2026-10-08 16:00:35 KST, 마지막 시각 2026-10-08 17:03:57 KST. chmodel 오류 줄 합계 0. chmodel>0 회차 0. kernel_warn>0 회차 0.
  - 미완료/없음 0: -

### 11.1.2 조합별 행렬 (행 = 매핑 단위, 열 = fio bs). 칸 = mean ± std [min..max], n = 그 조합의 완료 회차 수(보통 3)
#### main3x3_20261008 · wbuffix_drop · bw_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 417.603 ± 1.452 [415.944..418.642] | 480.826 ± 0.176 [480.630..480.972] | 482.302 ± 0.130 [482.184..482.441] |
| 16K | 129.852 ± 0.317 [129.584..130.202] | 420.331 ± 0.844 [419.476..421.164] | 440.637 ± 0.565 [440.205..441.276] |
| 32K | 68.256 ± 0.107 [68.141..68.352] | 219.511 ± 0.140 [219.352..219.610] | 424.263 ± 0.442 [423.780..424.648] |

#### main3x3_20261008 · wbuffix_drop · iops
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 106906.563 ± 371.717 [106481.802..107172.397] | 30772.891 ± 11.311 [30760.319..30782.244] | 15433.686 ± 4.154 [15429.895..15438.126] |
| 16K | 33242.094 ± 81.310 [33173.580..33331.945] | 26901.225 ± 54.054 [26846.441..26954.517] | 14100.404 ± 18.083 [14086.565..14120.865] |
| 32K | 17473.609 ± 27.370 [17444.046..17498.067] | 14048.746 ± 8.916 [14038.555..14055.110] | 13576.439 ± 14.149 [13560.992..13588.769] |

#### main3x3_20261008 · wbuffix_drop · clat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 298.296 ± 1.041 [297.548..299.484] | 1038.409 ± 0.373 [1038.101..1038.823] | 2071.488 ± 0.546 [2070.895..2071.971] |
| 16K | 961.535 ± 2.350 [958.946..963.535] | 1188.032 ± 2.378 [1185.685..1190.439] | 2267.517 ± 2.898 [2264.240..2269.740] |
| 32K | 1830.125 ± 2.882 [1827.564..1833.246] | 2276.245 ± 1.443 [2275.204..2277.892] | 2355.090 ± 2.454 [2352.962..2357.774] |

#### main3x3_20261008 · wbuffix_drop · clat_p50_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 69.803 ± 0.591 [69.120..70.144] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] |
| 16K | 254.976 ± 0.000 [254.976..254.976] | 246.101 ± 1.182 [244.736..246.784] | 464.896 ± 0.000 [464.896..464.896] |
| 32K | 569.344 ± 0.000 [569.344..569.344] | 536.576 ± 0.000 [536.576..536.576] | 526.336 ± 3.547 [522.240..528.384] |

#### main3x3_20261008 · wbuffix_drop · clat_p99_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 13391.189 ± 75.674 [13303.808..13434.880] | 17694.720 ± 0.000 [17694.720..17694.720] | 18219.008 ± 0.000 [18219.008..18219.008] |
| 16K | 14133.931 ± 75.674 [14090.240..14221.312] | 16711.680 ± 0.000 [16711.680..16711.680] | 18219.008 ± 0.000 [18219.008..18219.008] |
| 32K | 14396.075 ± 75.674 [14352.384..14483.456] | 17519.957 ± 151.349 [17432.576..17694.720] | 17519.957 ± 151.349 [17432.576..17694.720] |

#### main3x3_20261008 · wbuffix_drop · clat_p999_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 17170.432 ± 0.000 [17170.432..17170.432] | 18481.152 ± 0.000 [18481.152..18481.152] | 18743.296 ± 0.000 [18743.296..18743.296] |
| 16K | 15488.341 ± 75.674 [15400.960..15532.032] | 17956.864 ± 0.000 [17956.864..17956.864] | 18743.296 ± 0.000 [18743.296..18743.296] |
| 32K | 15400.960 ± 0.000 [15400.960..15400.960] | 17956.864 ± 0.000 [17956.864..17956.864] | 18219.008 ± 0.000 [18219.008..18219.008] |

#### main3x3_20261008 · wbuffix_drop · lat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 299.141 ± 1.042 [298.395..300.331] | 1039.624 ± 0.386 [1039.307..1040.054] | 2073.132 ± 0.551 [2072.538..2073.627] |
| 16K | 962.418 ± 2.355 [959.816..964.404] | 1189.281 ± 2.382 [1186.934..1191.695] | 2269.185 ± 2.899 [2265.905..2271.405] |
| 32K | 1831.100 ± 2.871 [1828.540..1834.204] | 2277.515 ± 1.437 [2276.490..2279.157] | 2356.773 ± 2.460 [2354.627..2359.458] |

#### main3x3_20261008 · wbuffix_drop · slat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.845 ± 0.004 [0.840..0.848] | 1.216 ± 0.013 [1.206..1.231] | 1.644 ± 0.012 [1.633..1.656] |
| 16K | 0.883 ± 0.024 [0.869..0.910] | 1.248 ± 0.009 [1.239..1.256] | 1.668 ± 0.004 [1.665..1.672] |
| 32K | 0.975 ± 0.015 [0.959..0.989] | 1.270 ± 0.014 [1.259..1.286] | 1.683 ± 0.017 [1.665..1.699] |

#### main3x3_20261008 · wbuffix_drop · bw_first10s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 1272.818 ± 0.972 [1272.012..1273.898] | 1288.350 ± 0.246 [1288.067..1288.509] | 1290.595 ± 0.034 [1290.572..1290.634] |
| 16K | 378.620 ± 0.125 [378.542..378.764] | 1279.583 ± 0.446 [1279.126..1280.017] | 1285.860 ± 0.011 [1285.853..1285.873] |
| 32K | 189.710 ± 0.044 [189.660..189.739] | 741.367 ± 0.178 [741.249..741.572] | 1278.176 ± 0.379 [1277.781..1278.536] |

#### main3x3_20261008 · wbuffix_drop · bw_last20s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 320.507 ± 4.618 [316.224..325.399] | 244.492 ± 0.419 [244.112..244.941] | 247.090 ± 0.147 [246.999..247.260] |
| 16K | 58.495 ± 0.750 [57.983..59.356] | 323.504 ± 0.632 [322.802..324.028] | 320.661 ± 1.819 [318.919..322.549] |
| 32K | 32.512 ± 0.230 [32.297..32.754] | 82.283 ± 0.537 [81.875..82.891] | 322.330 ± 2.498 [320.523..325.180] |

#### main3x3_20261008 · wbuffix_drop · gc_onset_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 6.340 ± 0.026 [6.313..6.366] | 5.723 ± 0.005 [5.719..5.729] | 5.726 ± 0.000 [5.725..5.726] |
| 16K | 5.947 ± 0.002 [5.945..5.949] | 5.957 ± 0.004 [5.954..5.961] | 5.875 ± 0.000 [5.875..5.875] |
| 32K | 6.094 ± 0.000 [6.094..6.094] | 6.092 ± 0.003 [6.090..6.096] | 6.123 ± 0.003 [6.122..6.127] |

#### main3x3_20261008 · wbuffix_drop · gc_onset_last_part_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 6.361 ± 0.026 [6.334..6.387] | 5.724 ± 0.005 [5.719..5.729] | 5.726 ± 0.000 [5.726..5.726] |
| 16K | 5.977 ± 0.002 [5.975..5.979] | 5.978 ± 0.004 [5.975..5.983] | 5.897 ± 0.000 [5.896..5.897] |
| 32K | 6.176 ± 0.000 [6.176..6.176] | 6.129 ± 0.003 [6.127..6.133] | 6.168 ± 0.003 [6.166..6.172] |

#### main3x3_20261008 · wbuffix_drop · bw_pre_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2004.864 ± 9.459 [1995.506..2014.421] | 2217.840 ± 0.267 [2217.666..2218.147] | 2217.771 ± 0.003 [2217.767..2217.773] |
| 16K | 535.554 ± 0.075 [535.467..535.598] | 2142.132 ± 1.408 [2140.533..2143.186] | 2173.059 ± 0.071 [2172.977..2173.102] |
| 32K | 256.096 ± 0.007 [256.090..256.104] | 1026.949 ± 0.057 [1026.883..1026.984] | 2033.002 ± 0.200 [2032.771..2033.119] |

#### main3x3_20261008 · wbuffix_drop · bw_post_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 241.354 ± 1.996 [239.555..243.502] | 305.689 ± 0.200 [305.472..305.864] | 307.212 ± 0.102 [307.126..307.325] |
| 16K | 88.928 ± 0.349 [88.617..89.305] | 246.676 ± 1.006 [245.693..247.704] | 265.947 ± 0.499 [265.588..266.516] |
| 32K | 47.396 ± 0.120 [47.263..47.497] | 129.860 ± 0.127 [129.714..129.947] | 245.601 ± 0.521 [245.058..246.097] |

#### main3x3_20261008 · wbuffix_drop · gc_cnt
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 8301.333 ± 89.646 [8199..8366] | 11270.667 ± 2.309 [11268..11272] | 11276.000 ± 0.000 [11276..11276] |
| 16K | 7078.333 ± 49.662 [7036..7133] | 8320.667 ± 49.085 [8270..8368] | 9408.000 ± 34.117 [9380..9446] |
| 32K | 7210.667 ± 30.105 [7177..7235] | 8279.000 ± 19.000 [8260..8298] | 8386.000 ± 24.637 [8360..8409] |

#### main3x3_20261008 · wbuffix_drop · ftl_host_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 6415070 ± 22088.189 [6389760..6430451] | 7386848 ± 2920.953 [7383584..7389216] | 7408787 ± 1469.048 [7407584..7410424] |
| 16K | 1994714 ± 4889.609 [1990448..2000050] | 1614315 ± 3042.678 [1611216..1617298] | 1692077 ± 2170.020 [1690416..1694532] |
| 32K | 1048556 ± 1654.195 [1046730..1049954] | 843073.333 ± 467.342 [842535..843375] | 814695.000 ± 884.595 [813768..815530] |

#### main3x3_20261008 · wbuffix_drop · ftl_gc_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 13706843 ± 161384.385 [13522725..13823810] | 18816276 ± 2221.160 [18813820..18818144] | 18804995 ± 1425.669 [18803408..18806168] |
| 16K | 2410153 ± 20549.725 [2392641..2432776] | 3426085 ± 22092.670 [3403230..3447327] | 3904995 ± 15225.395 [3892398..3921914] |
| 32K | 1187740 ± 6062.132 [1180946..1192596] | 1666757 ± 4488.712 [1662417..1671381] | 1722236 ± 5435.556 [1716494..1727302] |

#### main3x3_20261008 · wbuffix_drop · waf_gc
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 3.137 ± 0.018 [3.116..3.150] | 3.547 ± 0.001 [3.547..3.548] | 3.538 ± 0.001 [3.537..3.539] |
| 16K | 2.208 ± 0.007 [2.202..2.216] | 3.122 ± 0.010 [3.112..3.132] | 3.308 ± 0.006 [3.303..3.314] |
| 32K | 2.133 ± 0.004 [2.128..2.136] | 2.977 ± 0.004 [2.973..2.982] | 3.114 ± 0.004 [3.109..3.118] |

#### main3x3_20261008 · wbuffix_drop · waf_total
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 3.137 ± 0.018 [3.116..3.150] | 3.547 ± 0.001 [3.547..3.548] | 3.538 ± 0.001 [3.537..3.539] |
| 16K | 8.833 ± 0.029 [8.808..8.865] | 3.122 ± 0.010 [3.112..3.132] | 3.308 ± 0.006 [3.303..3.314] |
| 32K | 17.062 ± 0.032 [17.026..17.087] | 5.954 ± 0.009 [5.946..5.964] | 3.114 ± 0.004 [3.109..3.118] |

#### main3x3_20261008 · wbuffix_drop · written_GiB
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 24.472 ± 0.084 [24.375..24.530] | 28.179 ± 0.011 [28.166..28.188] | 28.262 ± 0.006 [28.258..28.269] |
| 16K | 7.609 ± 0.019 [7.593..7.630] | 24.632 ± 0.046 [24.585..24.678] | 25.819 ± 0.033 [25.794..25.857] |
| 32K | 4.000 ± 0.006 [3.993..4.005] | 12.865 ± 0.007 [12.857..12.869] | 24.863 ± 0.027 [24.834..24.888] |

#### main3x3_20261008 · wbuffix_drop · fill_ratio
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2.182 ± 0.008 [2.174..2.187] | 2.513 ± 0.001 [2.512..2.514] | 2.520 ± 0.000 [2.520..2.521] |
| 16K | 0.679 ± 0.002 [0.677..0.680] | 2.197 ± 0.004 [2.192..2.201] | 2.302 ± 0.003 [2.300..2.306] |
| 32K | 0.357 ± 0.001 [0.356..0.357] | 1.147 ± 0.001 [1.146..1.148] | 2.217 ± 0.002 [2.215..2.219] |

#### main3x3_20261008 · wbuffix_drop · chmodel_msgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### main3x3_20261008 · wbuffix_drop · kernel_warn
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### main3x3_20261008 · wbuffix_nodrop · bw_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 415.997 ± 1.559 [414.744..417.743] | 480.960 ± 0.088 [480.858..481.021] | 482.267 ± 0.176 [482.105..482.454] |
| 16K | 129.721 ± 0.035 [129.697..129.761] | 420.388 ± 1.287 [419.193..421.751] | 441.581 ± 1.301 [440.150..442.691] |
| 32K | 68.288 ± 0.048 [68.236..68.331] | 219.565 ± 0.381 [219.138..219.869] | 424.649 ± 0.173 [424.519..424.845] |

#### main3x3_20261008 · wbuffix_nodrop · iops
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 106495.339 ± 399.194 [106174.680..106942.443] | 30781.454 ± 5.676 [30774.953..30785.423] | 15432.564 ± 5.623 [15427.381..15438.542] |
| 16K | 33208.731 ± 8.874 [33202.647..33218.913] | 26904.846 ± 82.372 [26828.406..26992.085] | 14130.611 ± 41.620 [14084.818..14166.136] |
| 32K | 17481.884 ± 12.241 [17468.633..17492.769] | 14052.222 ± 24.404 [14024.843..14071.687] | 13588.795 ± 5.522 [13584.624..13595.057] |

#### main3x3_20261008 · wbuffix_nodrop · clat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 299.451 ± 1.126 [298.191..300.360] | 1038.121 ± 0.204 [1037.985..1038.356] | 2071.614 ± 0.780 [2070.787..2072.336] |
| 16K | 962.520 ± 0.259 [962.223..962.699] | 1187.876 ± 3.628 [1184.053..1191.271] | 2262.688 ± 6.689 [2256.993..2270.054] |
| 32K | 1829.245 ± 1.279 [1828.107..1830.630] | 2275.722 ± 3.928 [2272.597..2280.132] | 2352.950 ± 0.954 [2351.873..2353.692] |

#### main3x3_20261008 · wbuffix_nodrop · clat_p50_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 69.803 ± 0.591 [69.120..70.144] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] |
| 16K | 256.341 ± 1.182 [254.976..257.024] | 246.784 ± 0.000 [246.784..246.784] | 464.896 ± 0.000 [464.896..464.896] |
| 32K | 572.075 ± 4.730 [569.344..577.536] | 536.576 ± 0.000 [536.576..536.576] | 522.240 ± 0.000 [522.240..522.240] |

#### main3x3_20261008 · wbuffix_nodrop · clat_p99_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 13347.499 ± 75.674 [13303.808..13434.880] | 17694.720 ± 0.000 [17694.720..17694.720] | 18219.008 ± 0.000 [18219.008..18219.008] |
| 16K | 14046.549 ± 75.674 [13959.168..14090.240] | 16842.752 ± 113.512 [16711.680..16908.288] | 18219.008 ± 0.000 [18219.008..18219.008] |
| 32K | 14483.456 ± 0.000 [14483.456..14483.456] | 17607.339 ± 151.349 [17432.576..17694.720] | 17694.720 ± 0.000 [17694.720..17694.720] |

#### main3x3_20261008 · wbuffix_nodrop · clat_p999_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 16995.669 ± 151.349 [16908.288..17170.432] | 18481.152 ± 0.000 [18481.152..18481.152] | 18743.296 ± 0.000 [18743.296..18743.296] |
| 16K | 15313.579 ± 75.674 [15269.888..15400.960] | 17956.864 ± 0.000 [17956.864..17956.864] | 18743.296 ± 0.000 [18743.296..18743.296] |
| 32K | 15444.651 ± 75.674 [15400.960..15532.032] | 17956.864 ± 0.000 [17956.864..17956.864] | 18219.008 ± 0.000 [18219.008..18219.008] |

#### main3x3_20261008 · wbuffix_nodrop · lat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 300.298 ± 1.123 [299.041..301.202] | 1039.342 ± 0.194 [1039.208..1039.565] | 2073.270 ± 0.759 [2072.463..2073.970] |
| 16K | 963.389 ± 0.260 [963.090..963.567] | 1189.131 ± 3.645 [1185.275..1192.520] | 2264.343 ± 6.667 [2258.667..2271.686] |
| 32K | 1830.215 ± 1.276 [1829.076..1831.593] | 2276.968 ± 3.939 [2273.827..2281.388] | 2354.622 ± 0.953 [2353.546..2355.361] |

#### main3x3_20261008 · wbuffix_nodrop · slat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.848 ± 0.005 [0.842..0.851] | 1.221 ± 0.012 [1.208..1.232] | 1.656 ± 0.021 [1.635..1.676] |
| 16K | 0.869 ± 0.004 [0.867..0.874] | 1.255 ± 0.037 [1.222..1.295] | 1.655 ± 0.022 [1.632..1.674] |
| 32K | 0.970 ± 0.007 [0.964..0.978] | 1.246 ± 0.014 [1.230..1.256] | 1.672 ± 0.002 [1.670..1.673] |

#### main3x3_20261008 · wbuffix_nodrop · bw_first10s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 1272.909 ± 1.221 [1271.960..1274.286] | 1288.244 ± 0.341 [1287.867..1288.533] | 1290.717 ± 0.203 [1290.562..1290.947] |
| 16K | 378.912 ± 0.234 [378.643..379.058] | 1280.454 ± 0.119 [1280.323..1280.556] | 1285.856 ± 0.008 [1285.850..1285.865] |
| 32K | 189.793 ± 0.123 [189.655..189.894] | 741.172 ± 0.006 [741.166..741.178] | 1278.010 ± 0.243 [1277.778..1278.263] |

#### main3x3_20261008 · wbuffix_nodrop · bw_last20s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 321.959 ± 1.628 [320.716..323.802] | 244.833 ± 0.260 [244.565..245.084] | 247.153 ± 0.359 [246.785..247.503] |
| 16K | 58.226 ± 0.105 [58.143..58.343] | 323.407 ± 1.170 [322.718..324.757] | 321.431 ± 1.819 [319.397..322.904] |
| 32K | 32.631 ± 0.266 [32.324..32.785] | 82.161 ± 0.396 [81.830..82.599] | 322.791 ± 1.322 [321.330..323.905] |

#### main3x3_20261008 · wbuffix_nodrop · gc_onset_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 6.317 ± 0.035 [6.277..6.342] | 5.694 ± 0.002 [5.693..5.696] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.913 ± 0.002 [5.911..5.915] | 5.921 ± 0.000 [5.921..5.921] | 5.844 ± 0.001 [5.843..5.846] |
| 32K | 6.061 ± 0.000 [6.061..6.061] | 6.064 ± 0.000 [6.064..6.064] | 6.096 ± 0.000 [6.096..6.096] |

#### main3x3_20261008 · wbuffix_nodrop · gc_onset_last_part_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 6.338 ± 0.035 [6.298..6.362] | 5.694 ± 0.002 [5.693..5.697] | 5.693 ± 0.000 [5.693..5.694] |
| 16K | 5.943 ± 0.002 [5.941..5.945] | 5.943 ± 0.000 [5.943..5.943] | 5.866 ± 0.001 [5.865..5.867] |
| 32K | 6.144 ± 0.000 [6.144..6.144] | 6.101 ± 0.000 [6.101..6.101] | 6.141 ± 0.000 [6.140..6.141] |

#### main3x3_20261008 · wbuffix_nodrop · bw_pre_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2001.359 ± 12.555 [1992.749..2015.765] | 2217.592 ± 0.262 [2217.290..2217.750] | 2217.771 ± 0.003 [2217.767..2217.773] |
| 16K | 535.595 ± 0.017 [535.576..535.609] | 2143.200 ± 0.033 [2143.168..2143.233] | 2172.678 ± 0.558 [2172.034..2173.000] |
| 32K | 256.082 ± 0.007 [256.074..256.089] | 1026.858 ± 0.016 [1026.844..1026.875] | 2032.771 ± 0.005 [2032.766..2032.776] |

#### main3x3_20261008 · wbuffix_nodrop · bw_post_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 240.091 ± 2.885 [236.918..242.558] | 305.810 ± 0.086 [305.711..305.870] | 307.234 ± 0.180 [307.052..307.412] |
| 16K | 88.772 ± 0.036 [88.741..88.812] | 246.588 ± 1.450 [245.238..248.121] | 266.960 ± 1.475 [265.356..268.256] |
| 32K | 47.437 ± 0.054 [47.384..47.491] | 129.922 ± 0.412 [129.459..130.249] | 246.011 ± 0.174 [245.838..246.187] |

#### main3x3_20261008 · wbuffix_nodrop · gc_cnt
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 8204.667 ± 93.927 [8133..8311] | 11270.667 ± 2.309 [11268..11272] | 11276.000 ± 0.000 [11276..11276] |
| 16K | 7056.000 ± 4.583 [7052..7061] | 8319.667 ± 74.969 [8250..8399] | 9463.333 ± 65.248 [9392..9520] |
| 32K | 7222.667 ± 14.012 [7209..7237] | 8289.667 ± 45.829 [8241..8332] | 8409.000 ± 10.149 [8398..8418] |

#### main3x3_20261008 · wbuffix_nodrop · ftl_host_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 6390148 ± 24491.429 [6370587..6417616] | 7388821 ± 1073.948 [7387712..7389856] | 7409112 ± 2433.933 [7406624..7411488] |
| 16K | 1992601 ± 505.547 [1992192..1993166] | 1614479 ± 5060.688 [1609758..1619822] | 1695965 ± 4988.469 [1690488..1700248] |
| 32K | 1049105 ± 733.120 [1048380..1049846] | 843318.667 ± 1426.180 [841716..844448] | 815404.667 ± 313.002 [815091..815717] |

#### main3x3_20261008 · wbuffix_nodrop · ftl_gc_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 13533841 ± 167831.157 [13406435..13724008] | 18814517 ± 4586.611 [18809364..18818152] | 18804544 ± 2463.636 [18802256..18807152] |
| 16K | 2400837 ± 1819.679 [2399217..2402806] | 3425415 ± 33300.381 [3394501..3460675] | 3929382 ± 28415.406 [3898342..3954112] |
| 32K | 1190282 ± 2836.155 [1187519..1193186] | 1669245 ± 10323.704 [1658397..1678949] | 1727406 ± 2295.000 [1724901..1729407] |

#### main3x3_20261008 · wbuffix_nodrop · waf_gc
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 3.118 ± 0.018 [3.104..3.138] | 3.546 ± 0.001 [3.546..3.547] | 3.538 ± 0.001 [3.537..3.539] |
| 16K | 2.205 ± 0.001 [2.204..2.206] | 3.122 ± 0.014 [3.109..3.136] | 3.317 ± 0.010 [3.306..3.326] |
| 32K | 2.135 ± 0.002 [2.133..2.137] | 2.979 ± 0.009 [2.970..2.988] | 3.118 ± 0.002 [3.116..3.120] |

#### main3x3_20261008 · wbuffix_nodrop · waf_total
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 3.118 ± 0.018 [3.104..3.138] | 3.546 ± 0.001 [3.546..3.547] | 3.538 ± 0.001 [3.537..3.539] |
| 16K | 8.820 ± 0.002 [8.817..8.822] | 3.122 ± 0.014 [3.109..3.136] | 3.317 ± 0.010 [3.306..3.326] |
| 32K | 17.077 ± 0.015 [17.062..17.092] | 5.959 ± 0.018 [5.940..5.976] | 3.118 ± 0.002 [3.116..3.120] |

#### main3x3_20261008 · wbuffix_nodrop · written_GiB
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 24.376 ± 0.093 [24.302..24.481] | 28.186 ± 0.004 [28.182..28.190] | 28.264 ± 0.009 [28.254..28.273] |
| 16K | 7.601 ± 0.002 [7.600..7.603] | 24.635 ± 0.077 [24.563..24.717] | 25.878 ± 0.076 [25.795..25.944] |
| 32K | 4.002 ± 0.003 [3.999..4.005] | 12.868 ± 0.022 [12.844..12.885] | 24.884 ± 0.010 [24.875..24.894] |

#### main3x3_20261008 · wbuffix_nodrop · fill_ratio
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2.174 ± 0.008 [2.167..2.183] | 2.513 ± 0.000 [2.513..2.514] | 2.520 ± 0.001 [2.520..2.521] |
| 16K | 0.678 ± 0.000 [0.678..0.678] | 2.197 ± 0.007 [2.190..2.204] | 2.308 ± 0.007 [2.300..2.314] |
| 32K | 0.357 ± 0.000 [0.357..0.357] | 1.148 ± 0.002 [1.145..1.149] | 2.219 ± 0.001 [2.218..2.220] |

#### main3x3_20261008 · wbuffix_nodrop · chmodel_msgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### main3x3_20261008 · wbuffix_nodrop · kernel_warn
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

### 11.1.3b OS 페이지 캐시 drop vs nodrop (같은 map·bs·rep 쌍; diff = drop − nodrop)
| variant | map | bs | metric | n | nodrop mean | drop mean | mean diff % | paired t | p (two-sided) | 95% CI % |
|---|---|---|---|---|---|---|---|---|---|---|
| wbuffix | 4k | 4k | bw_MiBps | 3 | 415.997 | 417.603 | 0.387 | 2.024 | 0.1803 |  |
| wbuffix | 4k | 4k | iops | 3 | 106495.339 | 106906.563 | 0.387 | 2.024 | 0.1803 |  |
| wbuffix | 4k | 4k | clat_mean_us | 3 | 299.451 | 298.296 | -0.385 | -2.023 | 0.1804 |  |
| wbuffix | 4k | 4k | clat_p99_us | 3 | 13347.499 | 13391.189 | 0.328 | 1.000 | 0.4226 |  |
| wbuffix | 4k | 4k | gc_onset_s | 3 | 6.317 | 6.340 | 0.362 | 0.941 | 0.4462 |  |
| wbuffix | 4k | 4k | bw_pre_gc_MiBps | 3 | 2001.359 | 2004.864 | 0.178 | 0.405 | 0.7247 |  |
| wbuffix | 4k | 4k | bw_post_gc_MiBps | 3 | 240.091 | 241.354 | 0.532 | 0.897 | 0.4645 |  |
| wbuffix | 4k | 4k | waf_total | 3 | 3.118 | 3.137 | 0.602 | 1.817 | 0.2109 |  |
| wbuffix | 4k | 16k | bw_MiBps | 3 | 480.960 | 480.826 | -0.028 | -1.122 | 0.3786 |  |
| wbuffix | 4k | 16k | iops | 3 | 30781.454 | 30772.891 | -0.028 | -1.118 | 0.3797 |  |
| wbuffix | 4k | 16k | clat_mean_us | 3 | 1038.121 | 1038.409 | 0.028 | 1.098 | 0.3866 |  |
| wbuffix | 4k | 16k | clat_p99_us | 3 | 17694.720 | 17694.720 | 0.000 | 0.000 | NA |  |
| wbuffix | 4k | 16k | gc_onset_s | 3 | 5.694 | 5.723 | 0.513 | 8.900 | 0.0124 |  |
| wbuffix | 4k | 16k | bw_pre_gc_MiBps | 3 | 2217.592 | 2217.840 | 0.011 | 1.563 | 0.2586 |  |
| wbuffix | 4k | 16k | bw_post_gc_MiBps | 3 | 305.810 | 305.689 | -0.039 | -0.941 | 0.4461 |  |
| wbuffix | 4k | 16k | waf_total | 3 | 3.546 | 3.547 | 0.026 | 1.201 | 0.3527 |  |
| wbuffix | 4k | 32k | bw_MiBps | 3 | 482.267 | 482.302 | 0.007 | 0.322 | 0.7781 |  |
| wbuffix | 4k | 32k | iops | 3 | 15432.564 | 15433.686 | 0.007 | 0.321 | 0.7785 |  |
| wbuffix | 4k | 32k | clat_mean_us | 3 | 2071.614 | 2071.488 | -0.006 | -0.258 | 0.8203 |  |
| wbuffix | 4k | 32k | clat_p99_us | 3 | 18219.008 | 18219.008 | 0.000 | 0.000 | NA |  |
| wbuffix | 4k | 32k | gc_onset_s | 3 | 5.693 | 5.726 | 0.570 | 121.252 | 0.0001 |  |
| wbuffix | 4k | 32k | bw_pre_gc_MiBps | 3 | 2217.771 | 2217.771 | 0.000 | 0.000 | NA |  |
| wbuffix | 4k | 32k | bw_post_gc_MiBps | 3 | 307.234 | 307.212 | -0.007 | -0.218 | 0.8475 |  |
| wbuffix | 4k | 32k | waf_total | 3 | 3.538 | 3.538 | 0.005 | 0.259 | 0.8197 |  |
| wbuffix | 16k | 4k | bw_MiBps | 3 | 129.721 | 129.852 | 0.101 | 0.798 | 0.5086 |  |
| wbuffix | 16k | 4k | iops | 3 | 33208.731 | 33242.094 | 0.100 | 0.796 | 0.5095 |  |
| wbuffix | 16k | 4k | clat_mean_us | 3 | 962.520 | 961.535 | -0.102 | -0.813 | 0.5014 |  |
| wbuffix | 16k | 4k | clat_p99_us | 3 | 14046.549 | 14133.931 | 0.623 | 2.000 | 0.1835 |  |
| wbuffix | 16k | 4k | gc_onset_s | 3 | 5.913 | 5.947 | 0.578 | 21.889 | 0.0021 |  |
| wbuffix | 16k | 4k | bw_pre_gc_MiBps | 3 | 535.595 | 535.554 | -0.008 | -1.195 | 0.3546 |  |
| wbuffix | 16k | 4k | bw_post_gc_MiBps | 3 | 88.772 | 88.928 | 0.176 | 0.866 | 0.4778 |  |
| wbuffix | 16k | 4k | waf_total | 3 | 8.820 | 8.833 | 0.153 | 0.870 | 0.4758 |  |
| wbuffix | 16k | 16k | bw_MiBps | 3 | 420.388 | 420.331 | -0.013 | -0.092 | 0.9349 |  |
| wbuffix | 16k | 16k | iops | 3 | 26904.846 | 26901.225 | -0.013 | -0.093 | 0.9346 |  |
| wbuffix | 16k | 16k | clat_mean_us | 3 | 1187.876 | 1188.032 | 0.014 | 0.091 | 0.9361 |  |
| wbuffix | 16k | 16k | clat_p99_us | 3 | 16842.752 | 16711.680 | -0.775 | -2.000 | 0.1835 |  |
| wbuffix | 16k | 16k | gc_onset_s | 3 | 5.921 | 5.957 | 0.601 | 15.878 | 0.0039 |  |
| wbuffix | 16k | 16k | bw_pre_gc_MiBps | 3 | 2143.200 | 2142.132 | -0.050 | -1.337 | 0.3131 |  |
| wbuffix | 16k | 16k | bw_post_gc_MiBps | 3 | 246.588 | 246.676 | 0.037 | 0.132 | 0.9067 |  |
| wbuffix | 16k | 16k | waf_total | 3 | 3.122 | 3.122 | 0.022 | 0.093 | 0.9343 |  |
| wbuffix | 16k | 32k | bw_MiBps | 3 | 441.581 | 440.637 | -0.213 | -1.159 | 0.3661 |  |
| wbuffix | 16k | 32k | iops | 3 | 14130.611 | 14100.404 | -0.213 | -1.159 | 0.3661 |  |
| wbuffix | 16k | 32k | clat_mean_us | 3 | 2262.688 | 2267.517 | 0.214 | 1.154 | 0.3678 |  |
| wbuffix | 16k | 32k | clat_p99_us | 3 | 18219.008 | 18219.008 | 0.000 | 0.000 | NA |  |
| wbuffix | 16k | 32k | gc_onset_s | 3 | 5.844 | 5.875 | 0.531 | 35.510 | 0.0008 |  |
| wbuffix | 16k | 32k | bw_pre_gc_MiBps | 3 | 2172.678 | 2173.059 | 0.018 | 1.354 | 0.3086 |  |
| wbuffix | 16k | 32k | bw_post_gc_MiBps | 3 | 266.960 | 265.947 | -0.378 | -1.258 | 0.3353 |  |
| wbuffix | 16k | 32k | waf_total | 3 | 3.317 | 3.308 | -0.273 | -1.279 | 0.3291 |  |
| wbuffix | 32k | 4k | bw_MiBps | 3 | 68.288 | 68.256 | -0.048 | -0.960 | 0.4385 |  |
| wbuffix | 32k | 4k | iops | 3 | 17481.884 | 17473.609 | -0.047 | -0.947 | 0.4435 |  |
| wbuffix | 32k | 4k | clat_mean_us | 3 | 1829.245 | 1830.125 | 0.048 | 0.951 | 0.4420 |  |
| wbuffix | 32k | 4k | clat_p99_us | 3 | 14483.456 | 14396.075 | -0.603 | -2.000 | 0.1835 |  |
| wbuffix | 32k | 4k | gc_onset_s | 3 | 6.061 | 6.094 | 0.538 | 236.485 | 0.0000 |  |
| wbuffix | 32k | 4k | bw_pre_gc_MiBps | 3 | 256.082 | 256.096 | 0.006 | 3.995 | 0.0573 |  |
| wbuffix | 32k | 4k | bw_post_gc_MiBps | 3 | 47.437 | 47.396 | -0.086 | -1.022 | 0.4142 |  |
| wbuffix | 32k | 4k | waf_total | 3 | 17.077 | 17.062 | -0.086 | -1.374 | 0.3033 |  |
| wbuffix | 32k | 16k | bw_MiBps | 3 | 219.565 | 219.511 | -0.025 | -0.206 | 0.8558 |  |
| wbuffix | 32k | 16k | iops | 3 | 14052.222 | 14048.746 | -0.025 | -0.206 | 0.8560 |  |
| wbuffix | 32k | 16k | clat_mean_us | 3 | 2275.722 | 2276.245 | 0.023 | 0.192 | 0.8658 |  |
| wbuffix | 32k | 16k | clat_p99_us | 3 | 17607.339 | 17519.957 | -0.494 | -1.000 | 0.4226 |  |
| wbuffix | 32k | 16k | gc_onset_s | 3 | 6.064 | 6.092 | 0.463 | 15.803 | 0.0040 |  |
| wbuffix | 32k | 16k | bw_pre_gc_MiBps | 3 | 1026.858 | 1026.949 | 0.009 | 3.375 | 0.0777 |  |
| wbuffix | 32k | 16k | bw_post_gc_MiBps | 3 | 129.922 | 129.860 | -0.047 | -0.225 | 0.8426 |  |
| wbuffix | 32k | 16k | waf_total | 3 | 5.959 | 5.954 | -0.081 | -0.599 | 0.6099 |  |
| wbuffix | 32k | 32k | bw_MiBps | 3 | 424.649 | 424.263 | -0.091 | -2.190 | 0.1599 |  |
| wbuffix | 32k | 32k | iops | 3 | 13588.795 | 13576.439 | -0.091 | -2.189 | 0.1600 |  |
| wbuffix | 32k | 32k | clat_mean_us | 3 | 2352.950 | 2355.090 | 0.091 | 2.202 | 0.1586 |  |
| wbuffix | 32k | 32k | clat_p99_us | 3 | 17694.720 | 17519.957 | -0.988 | -2.000 | 0.1835 |  |
| wbuffix | 32k | 32k | gc_onset_s | 3 | 6.096 | 6.123 | 0.450 | 14.710 | 0.0046 |  |
| wbuffix | 32k | 32k | bw_pre_gc_MiBps | 3 | 2032.771 | 2033.002 | 0.011 | 1.999 | 0.1836 |  |
| wbuffix | 32k | 32k | bw_post_gc_MiBps | 3 | 246.011 | 245.601 | -0.167 | -2.038 | 0.1784 |  |
| wbuffix | 32k | 32k | waf_total | 3 | 3.118 | 3.114 | -0.144 | -3.253 | 0.0829 |  |
| wbuffix | ALL | ALL | bw_MiBps | 27 | NA | NA | 0.009 | 0.191 | 0.8497 | [-0.084, 0.101] |
| wbuffix | ALL | ALL | iops | 27 | NA | NA | 0.009 | 0.192 | 0.8495 | [-0.084, 0.101] |
| wbuffix | ALL | ALL | clat_mean_us | 27 | NA | NA | -0.008 | -0.188 | 0.8521 | [-0.101, 0.084] |
| wbuffix | ALL | ALL | clat_p99_us | 27 | NA | NA | -0.212 | -1.594 | 0.1231 | [-0.486, 0.061] |
| wbuffix | ALL | ALL | gc_onset_s | 27 | NA | NA | 0.512 | 13.134 | 0.0000 | [0.432, 0.592] |
| wbuffix | ALL | ALL | bw_pre_gc_MiBps | 27 | NA | NA | 0.019 | 0.465 | 0.6459 | [-0.066, 0.105] |
| wbuffix | ALL | ALL | bw_post_gc_MiBps | 27 | NA | NA | 0.002 | 0.026 | 0.9793 | [-0.174, 0.178] |
| wbuffix | ALL | ALL | waf_total | 27 | NA | NA | 0.025 | 0.378 | 0.7082 | [-0.110, 0.160] |

### 11.1.4 회차별 전체 (analysis/summary_runs.csv 와 같은 값)
```csv
variant,map,bs,rep,bw_MiBps,iops,written_GiB,fill_ratio,clat_mean_us,clat_p50_us,clat_p99_us,clat_p999_us,lat_mean_us,slat_mean_us,runtime_s,bw_first10s_MiBps,bw_last20s_MiBps,dev_bytes,chmodel_msgs,kernel_warn,gc_onset_s,gc_onset_last_part_s,bw_pre_gc_MiBps,bw_post_gc_MiBps,gc_cnt,ftl_host_pgs,ftl_gc_pgs,waf_gc,waf_total
wbuffix_drop,4k,4k,1,415.944336,106481.802426,24.375000,2.173614,299.484155,70.144000,13434.880000,17170.432000,300.330947,0.846792,60.008000,1272.544775,325.399072,12040984064,0,0,6.340591,6.361433,2004.665120,239.555384,8199,6389760,13522725,3.116312,3.116312
wbuffix_drop,4k,4k,2,418.641602,107172.397127,24.530224,2.187456,297.547593,70.144000,13434.880000,17170.432000,298.395443,0.847849,60.001000,1272.011865,316.223926,12040984064,0,0,6.366142,6.386889,1995.506104,243.501899,8366,6430451,13823810,3.149742,3.149742
wbuffix_drop,4k,4k,3,418.223633,107065.489085,24.509430,2.185602,297.855543,69.120000,13303.808000,17170.432000,298.695582,0.840040,60.010000,1273.897803,319.897852,12040984064,0,0,6.313434,6.334210,2014.421468,241.004150,8339,6425000,13773993,3.143812,3.143812
wbuffix_drop,4k,16k,1,480.629883,30760.319285,28.166138,2.511685,1038.823219,222.208000,17694.720000,18481.152000,1040.053931,1.230712,60.009000,1288.473193,244.111572,12040984064,0,0,5.722159,5.722374,2217.707120,305.471707,11268,7383584,18813820,3.548061,3.548061
wbuffix_drop,4k,16k,2,480.971680,30782.243551,28.187622,2.513601,1038.101158,222.208000,17694.720000,18481.152000,1039.307316,1.206158,60.012000,1288.066553,244.940918,12040984064,0,0,5.728957,5.729182,2217.666460,305.863684,11272,7389216,18816864,3.546531,3.546531
wbuffix_drop,4k,16k,3,480.875977,30776.111444,28.182007,2.513100,1038.301176,222.208000,17694.720000,18481.152000,1039.511291,1.210114,60.012000,1288.509229,244.424756,12040984064,0,0,5.719205,5.719417,2218.147461,305.732735,11272,7387744,18818144,3.547211,3.547211
wbuffix_drop,4k,32k,1,482.282227,15433.037797,28.260620,2.520110,2071.598068,444.416000,18219.008000,18743.296000,2073.230895,1.632827,60.004000,1290.579443,247.012134,12040984064,0,0,5.725743,5.725950,2217.772727,307.185206,11276,7408352,18805408,3.538406,3.538406
wbuffix_drop,4k,32k,2,482.441406,15438.126031,28.268524,2.520815,2070.895245,444.416000,18219.008000,18743.296000,2072.537858,1.642613,60.001000,1290.571875,247.260205,12040984064,0,0,5.725890,5.726097,2217.767045,307.325052,11276,7410424,18803408,3.537427,3.537427
wbuffix_drop,4k,32k,3,482.183594,15429.895017,28.257690,2.519849,2071.971445,444.416000,18219.008000,18743.296000,2073.627213,1.655768,60.010000,1290.634326,246.998950,12040984064,0,0,5.725342,5.725543,2217.772727,307.125770,11276,7407584,18806168,3.538772,3.538772
wbuffix_drop,16k,4k,1,129.768555,33220.755849,7.605148,0.678181,962.123925,254.976000,14221.312000,15532.032000,963.034422,0.910497,60.012000,378.764014,58.146509,12040984064,0,0,5.949480,5.979352,535.467330,88.861445,7066,1993644,2405043,2.206355,8.825421
wbuffix_drop,16k,4k,2,130.202148,33331.944537,7.629585,0.680360,958.946465,254.976000,14090.240000,15532.032000,959.815795,0.869330,60.004000,378.541699,59.356128,12040984064,0,0,5.947554,5.977397,535.596591,89.305431,7133,2000050,2432776,2.216358,8.865430
wbuffix_drop,16k,4k,3,129.583984,33173.580440,7.592957,0.677094,963.534877,254.976000,14090.240000,15400.960000,964.403761,0.868884,60.001000,378.553174,57.983398,12040984064,0,0,5.945426,5.975239,535.598011,88.617447,7036,1990448,2392641,2.202062,8.808246
wbuffix_drop,16k,16k,1,420.354492,26902.716214,24.634277,2.196735,1187.973868,246.784000,16711.680000,17956.864000,1189.212842,1.238974,60.010000,1279.126416,322.802271,12040984064,0,0,5.954927,5.976614,2142.676136,246.630268,8324,1614432,3427697,3.123160,3.123160
wbuffix_drop,16k,16k,2,419.475586,26846.440949,24.585205,2.192359,1190.438915,246.784000,16711.680000,17956.864000,1191.695231,1.256316,60.016000,1280.016553,323.681592,12040984064,0,0,5.953646,5.975280,2143.186346,245.692867,8270,1611216,3403230,3.112212,3.112212
wbuffix_drop,16k,16k,3,421.164062,26954.517425,24.678009,2.200635,1185.684693,244.736000,16711.680000,17956.864000,1186.933652,1.248959,60.001000,1279.605518,324.028271,12040984064,0,0,5.961075,5.982786,2140.532759,247.703689,8368,1617298,3447327,3.131535,3.131535
wbuffix_drop,16k,32k,1,440.430664,14093.781770,25.806915,2.301304,2268.572353,464.896000,18219.008000,18743.296000,2270.244161,1.671808,60.001000,1285.853125,318.918530,12040984064,0,0,5.875123,5.896678,2173.096591,265.588186,9398,1691282,3900672,3.306340,3.306340
wbuffix_drop,16k,32k,2,440.205078,14086.565224,25.793701,2.300126,2269.739746,464.896000,18219.008000,18743.296000,2271.405380,1.665634,60.001000,1285.853906,322.548633,12040984064,0,0,5.874799,5.896365,2172.977273,265.734999,9380,1690416,3892398,3.302627,3.302627
wbuffix_drop,16k,32k,3,441.276367,14120.864652,25.856506,2.305726,2264.239822,464.896000,18219.008000,18743.296000,2265.905181,1.665359,60.001000,1285.873096,320.516211,12040984064,0,0,5.875311,5.896829,2173.102273,266.516315,9446,1694532,3921914,3.314453,3.314453
wbuffix_drop,32k,4k,1,68.275391,17478.713655,4.001560,0.356835,1829.565709,569.344000,14352.384000,15400.960000,1830.554677,0.988967,60.015000,189.659619,32.754492,12040984064,0,0,6.093964,6.176249,256.089844,47.427933,7220,1048985,1189679,2.134124,17.072992
wbuffix_drop,32k,4k,2,68.140625,17444.046329,3.992958,0.356068,1833.245723,569.344000,14352.384000,15400.960000,1834.204401,0.958678,60.005000,189.731201,32.297266,12040984064,0,0,6.093524,6.175818,256.103516,47.263138,7177,1046730,1180946,2.128224,17.025793
wbuffix_drop,32k,4k,3,68.351562,17498.066796,4.005257,0.357164,1827.563631,569.344000,14483.456000,15400.960000,1828.540051,0.976420,60.004000,189.739062,32.485010,12040984064,0,0,6.094118,6.176477,256.094401,47.497242,7235,1049954,1192596,2.135855,17.086844
wbuffix_drop,32k,16k,1,219.610352,14055.110237,12.869339,1.147609,2275.204359,536.576000,17694.720000,17956.864000,2276.490396,1.286037,60.007000,741.280908,81.875391,12040984064,0,0,6.090182,6.127213,1026.983805,129.947293,8279,843375,1666474,2.975959,5.951705
wbuffix_drop,32k,16k,2,219.571289,14052.572819,12.868088,1.147498,2275.637864,536.576000,17432.576000,17956.864000,2276.897144,1.259279,60.012000,741.572217,82.082983,12040984064,0,0,6.095640,6.132565,1026.882812,129.917616,8298,843310,1671381,2.981930,5.963767
wbuffix_drop,32k,16k,3,219.351562,14038.555100,12.856537,1.146468,2277.891984,536.576000,17432.576000,17956.864000,2279.157114,1.265130,60.018000,741.249365,82.891113,12040984064,0,0,6.089876,6.126930,1026.980713,129.714410,8260,842535,1662417,2.973113,5.946008
wbuffix_drop,32k,32k,1,423.780273,13560.991868,24.834229,2.214566,2357.773717,528.384000,17694.720000,18219.008000,2359.458113,1.684396,60.008000,1278.212207,321.286157,12040984064,0,0,6.121849,6.166429,2033.119303,245.058241,8360,813768,1716494,3.109316,3.109316
wbuffix_drop,32k,32k,2,424.648438,13588.769474,24.888000,2.219361,2352.961947,522.240000,17432.576000,18219.008000,2354.627188,1.665241,60.015000,1277.781250,320.523315,12040984064,0,0,6.127057,6.171579,2032.770833,246.096906,8409,815530,1727302,3.118012,3.118012
wbuffix_drop,32k,32k,3,424.360352,13579.557007,24.865326,2.217339,2354.534489,528.384000,17432.576000,18219.008000,2356.233886,1.699396,60.001000,1278.535742,325.179907,12040984064,0,0,6.121575,6.166088,2033.116862,245.648067,8389,814787,1722911,3.114554,3.114554
wbuffix_nodrop,4k,4k,1,414.744141,106174.680422,24.301861,2.167092,300.359579,69.120000,13434.880000,16908.288000,301.201599,0.842020,60.001000,1274.286035,320.716162,12040984064,0,0,6.276949,6.297565,2015.765137,236.918231,8133,6370587,13406435,3.104427,3.104427
wbuffix_nodrop,4k,4k,2,415.502930,106368.893852,24.346313,2.171056,299.800560,70.144000,13303.808000,16908.288000,300.651257,0.850697,60.001000,1272.479395,323.801611,12040984064,0,0,6.341670,6.362200,1992.748698,240.795287,8170,6382240,13471081,3.110714,3.110714
wbuffix_nodrop,4k,4k,3,417.743164,106942.442926,24.481262,2.183090,298.191441,70.144000,13303.808000,17170.432000,299.041393,0.849952,60.010000,1271.960205,321.358008,12040984064,0,0,6.333402,6.354020,1995.562581,242.558205,8311,6417616,13724008,3.138490,3.138490
wbuffix_nodrop,4k,16k,1,480.999023,30783.988268,28.186401,2.513492,1038.022001,222.208000,17694.720000,18481.152000,1039.254059,1.232058,60.006000,1287.867432,245.083618,12040984064,0,0,5.696374,5.696590,2217.289773,305.847343,11268,7388896,18809364,3.545626,3.545626
wbuffix_nodrop,4k,16k,2,481.021484,30785.422673,28.190063,2.513819,1037.985228,222.208000,17694.720000,18481.152000,1039.207547,1.222319,60.011000,1288.532520,244.851978,12040984064,0,0,5.693162,5.693381,2217.735795,305.870359,11272,7389856,18816036,3.546198,3.546198
wbuffix_nodrop,4k,16k,3,480.858398,30774.952511,28.181885,2.513089,1038.356268,222.208000,17694.720000,18481.152000,1039.564602,1.208333,60.014000,1288.332617,244.564771,12040984064,0,0,5.693097,5.693314,2217.750000,305.711466,11272,7387712,18818152,3.547223,3.547223
wbuffix_nodrop,4k,32k,1,482.454102,15438.541528,28.272583,2.521177,2070.787029,444.416000,18219.008000,18743.296000,2072.462820,1.675792,60.008000,1290.641553,247.503369,12040984064,0,0,5.693038,5.693245,2217.772727,307.412378,11276,7411488,18802256,3.536907,3.536907
wbuffix_nodrop,4k,32k,2,482.242188,15431.768195,28.263947,2.520407,2071.719447,444.416000,18219.008000,18743.296000,2073.377194,1.657747,60.016000,1290.946875,247.171655,12040984064,0,0,5.693209,5.693420,2217.767045,307.238407,11276,7409224,18804224,3.537948,3.537948
wbuffix_nodrop,4k,32k,3,482.105469,15427.381190,28.254028,2.519523,2072.335555,444.416000,18219.008000,18743.296000,2073.970227,1.634673,60.012000,1290.562500,246.785425,12040984064,0,0,5.693451,5.693653,2217.772727,307.052331,11276,7406624,18807152,3.539234,3.539234
wbuffix_nodrop,16k,4k,1,129.705078,33204.632947,7.600571,0.677773,962.636117,257.024000,14090.240000,15269.888000,963.509758,0.873642,60.005000,379.058301,58.142700,12040984064,0,0,5.914784,5.944689,535.575994,88.762874,7055,1992444,2400489,2.204796,8.819185
wbuffix_nodrop,16k,4k,2,129.760742,33218.913018,7.603333,0.678019,962.223264,254.976000,13959.168000,15400.960000,963.090408,0.867144,60.001000,379.035547,58.343384,12040984064,0,0,5.911013,5.940904,535.598722,88.812070,7061,1993166,2402806,2.205522,8.822080
wbuffix_nodrop,16k,4k,3,129.697266,33202.646623,7.599609,0.677687,962.699315,257.024000,14090.240000,15269.888000,963.566723,0.867408,60.001000,378.642969,58.192456,12040984064,0,0,5.914207,5.944163,535.609375,88.740870,7052,1992192,2399217,2.204310,8.817241
wbuffix_nodrop,16k,16k,1,419.193359,26828.405720,24.562958,2.190375,1191.270901,246.784000,16711.680000,17956.864000,1192.519928,1.249026,60.002000,1280.556055,324.757324,12040984064,0,0,5.920972,5.942714,2143.232955,245.238210,8250,1609758,3394501,3.108703,3.108703
wbuffix_nodrop,16k,16k,2,420.218750,26894.047460,24.625519,2.195954,1188.302654,246.784000,16908.288000,17956.864000,1189.597476,1.294822,60.008000,1280.481250,322.744922,12040984064,0,0,5.920850,5.942568,2143.198864,246.406447,8310,1613858,3421069,3.119808,3.119808
wbuffix_nodrop,16k,16k,3,421.750977,26992.084784,24.716522,2.204069,1184.052978,246.784000,16908.288000,17956.864000,1185.275408,1.222431,60.011000,1280.323437,322.717505,12040984064,0,0,5.921050,5.942793,2143.167614,248.120655,8399,1619822,3460675,3.136454,3.136454
wbuffix_nodrop,16k,32k,1,440.150391,14084.817783,25.794800,2.300224,2270.053876,464.896000,18219.008000,18743.296000,2271.685656,1.631780,60.011000,1285.850000,319.397363,12040984064,0,0,5.843336,5.864878,2173.000000,265.355505,9392,1690488,3898342,3.306045,3.306045
wbuffix_nodrop,16k,32k,2,442.691406,14166.136208,25.943726,2.313504,2256.992831,464.896000,18219.008000,18743.296000,2258.667132,1.674301,60.011000,1285.865430,322.904028,12040984064,0,0,5.845501,5.867085,2172.034091,268.256209,9520,1700248,3954112,3.325609,3.325609
wbuffix_nodrop,16k,32k,3,441.902344,14140.878868,25.896606,2.309302,2261.016160,464.896000,18219.008000,18743.296000,2262.675991,1.659831,60.009000,1285.853125,321.991016,12040984064,0,0,5.843275,5.864806,2173.000000,267.268985,9478,1697160,3935692,3.318987,3.318987
wbuffix_nodrop,32k,4k,1,68.297852,17484.250525,4.001961,0.356871,1828.997847,577.536000,14483.456000,15400.960000,1829.975799,0.977952,60.002000,189.893750,32.784985,12040984064,0,0,6.061479,6.144004,256.082031,47.436044,7222,1049090,1190140,2.134450,17.075599
wbuffix_nodrop,32k,4k,2,68.236328,17468.632842,3.999252,0.356629,1830.629704,569.344000,14483.456000,15400.960000,1831.593495,0.963791,60.015000,189.828906,32.324097,12040984064,0,0,6.061112,6.143710,256.088542,47.383753,7209,1048380,1187519,2.132718,17.061745
wbuffix_nodrop,32k,4k,3,68.331055,17492.768595,4.004845,0.357128,1828.107287,569.344000,14483.456000,15532.032000,1829.075747,0.968460,60.016000,189.655078,32.785229,12040984064,0,0,6.061261,6.143886,256.074219,47.491310,7237,1049846,1193186,2.136534,17.092274
wbuffix_nodrop,32k,16k,1,219.137695,14024.842961,12.843765,1.145329,2280.131635,536.576000,17694.720000,17956.864000,2281.387771,1.256136,60.017000,741.178125,82.053955,12040984064,0,0,6.063629,6.100835,1026.854167,129.459084,8241,841716,1658397,2.970257,5.940423
wbuffix_nodrop,32k,16k,2,219.869141,14071.686857,12.885376,1.149040,2272.596578,536.576000,17694.720000,17956.864000,2273.826587,1.230009,60.011000,741.165625,82.599487,12040984064,0,0,6.064007,6.101138,1026.843750,130.249032,8332,844448,1678949,2.988221,5.976385
wbuffix_nodrop,32k,16k,3,219.689453,14060.135968,12.875443,1.148154,2274.438362,536.576000,17432.576000,17956.864000,2275.689247,1.250885,60.014000,741.171875,81.829932,12040984064,0,0,6.063796,6.100865,1026.875000,130.057310,8296,843792,1670390,2.979623,5.959154
wbuffix_nodrop,32k,32k,1,424.518555,13584.623590,24.874603,2.218166,2353.691890,522.240000,17694.720000,18219.008000,2355.361397,1.669507,60.001000,1277.778125,323.905225,12040984064,0,0,6.096136,6.140668,2032.765625,245.838406,8398,815091,1724901,3.116207,3.116207
wbuffix_nodrop,32k,32k,2,424.844727,13595.056749,24.893707,2.219870,2351.873088,522.240000,17694.720000,18219.008000,2353.546356,1.673268,60.001000,1277.990625,321.330151,12040984064,0,0,6.095870,6.140373,2032.770833,246.186614,8418,815717,1729407,3.120107,3.120107
wbuffix_nodrop,32k,32k,3,424.583984,13586.703324,24.884216,2.219023,2353.284186,522.240000,17694.720000,18219.008000,2354.957588,1.673402,60.015000,1278.262500,323.138062,12040984064,0,0,6.096105,6.140618,2032.776042,246.006664,8411,815406,1727911,3.119081,3.119081
```

### 11.1.5 조합별 집계 전체 (analysis/summary_agg.csv 와 같은 값)
```csv
variant,map,bs,n,bw_MiBps_mean,bw_MiBps_std,bw_MiBps_min,bw_MiBps_max,iops_mean,iops_std,iops_min,iops_max,written_GiB_mean,written_GiB_std,written_GiB_min,written_GiB_max,fill_ratio_mean,fill_ratio_std,fill_ratio_min,fill_ratio_max,clat_mean_us_mean,clat_mean_us_std,clat_mean_us_min,clat_mean_us_max,clat_p50_us_mean,clat_p50_us_std,clat_p50_us_min,clat_p50_us_max,clat_p99_us_mean,clat_p99_us_std,clat_p99_us_min,clat_p99_us_max,clat_p999_us_mean,clat_p999_us_std,clat_p999_us_min,clat_p999_us_max,lat_mean_us_mean,lat_mean_us_std,lat_mean_us_min,lat_mean_us_max,slat_mean_us_mean,slat_mean_us_std,slat_mean_us_min,slat_mean_us_max,runtime_s_mean,runtime_s_std,runtime_s_min,runtime_s_max,bw_first10s_MiBps_mean,bw_first10s_MiBps_std,bw_first10s_MiBps_min,bw_first10s_MiBps_max,bw_last20s_MiBps_mean,bw_last20s_MiBps_std,bw_last20s_MiBps_min,bw_last20s_MiBps_max,chmodel_msgs_mean,chmodel_msgs_std,chmodel_msgs_min,chmodel_msgs_max,kernel_warn_mean,kernel_warn_std,kernel_warn_min,kernel_warn_max,gc_onset_s_mean,gc_onset_s_std,gc_onset_s_min,gc_onset_s_max,gc_onset_last_part_s_mean,gc_onset_last_part_s_std,gc_onset_last_part_s_min,gc_onset_last_part_s_max,bw_pre_gc_MiBps_mean,bw_pre_gc_MiBps_std,bw_pre_gc_MiBps_min,bw_pre_gc_MiBps_max,bw_post_gc_MiBps_mean,bw_post_gc_MiBps_std,bw_post_gc_MiBps_min,bw_post_gc_MiBps_max,gc_cnt_mean,gc_cnt_std,gc_cnt_min,gc_cnt_max,ftl_host_pgs_mean,ftl_host_pgs_std,ftl_host_pgs_min,ftl_host_pgs_max,ftl_gc_pgs_mean,ftl_gc_pgs_std,ftl_gc_pgs_min,ftl_gc_pgs_max,waf_gc_mean,waf_gc_std,waf_gc_min,waf_gc_max,waf_total_mean,waf_total_std,waf_total_min,waf_total_max
wbuffix_drop,4k,4k,3,417.603190,1.451731,415.944336,418.641602,106906.562879,371.716847,106481.802426,107172.397127,24.471551,0.084260,24.375000,24.530224,2.182224,0.007514,2.173614,2.187456,298.295764,1.040631,297.547593,299.484155,69.802667,0.591207,69.120000,70.144000,13391.189333,75.674454,13303.808000,13434.880000,17170.432000,0.000000,17170.432000,17170.432000,299.140657,1.041688,298.395443,300.330947,0.844894,0.004237,0.840040,0.847849,60.006333,0.004726,60.001000,60.010000,1272.818148,0.972234,1272.011865,1273.897803,320.506950,4.617800,316.223926,325.399072,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.340056,0.026358,6.313434,6.366142,6.360844,0.026344,6.334210,6.386889,2004.864231,9.459254,1995.506104,2014.421468,241.353811,1.996357,239.555384,243.501899,8301.333333,89.645599,8199,8366,6415070,22088.188706,6389760,6430451,13706843,161384.385107,13522725,13823810,3.136622,0.017837,3.116312,3.149742,3.136622,0.017837,3.116312,3.149742
wbuffix_drop,4k,16k,3,480.825846,0.176327,480.629883,480.971680,30772.891427,11.311266,30760.319285,30782.243551,28.178589,0.011143,28.166138,28.187622,2.512795,0.000994,2.511685,2.513601,1038.408518,0.372807,1038.101158,1038.823219,222.208000,0.000000,222.208000,222.208000,17694.720000,0.000000,17694.720000,17694.720000,18481.152000,0.000000,18481.152000,18481.152000,1039.624179,0.385897,1039.307316,1040.053931,1.215662,0.013183,1.206158,1.230712,60.011000,0.001732,60.009000,60.012000,1288.349658,0.245838,1288.066553,1288.509229,244.492415,0.418792,244.111572,244.940918,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.723440,0.005001,5.719205,5.728957,5.723658,0.005007,5.719417,5.729182,2217.840347,0.266744,2217.666460,2218.147461,305.689375,0.199554,305.471707,305.863684,11270.666667,2.309401,11268,11272,7386848,2920.953269,7383584,7389216,18816276,2221.160057,18813820,18818144,3.547267,0.000767,3.546531,3.548061,3.547267,0.000767,3.546531,3.548061
wbuffix_drop,4k,32k,3,482.302409,0.130086,482.183594,482.441406,15433.686282,4.153649,15429.895017,15438.126031,28.262278,0.005604,28.257690,28.268524,2.520258,0.000500,2.519849,2.520815,2071.488253,0.546440,2070.895245,2071.971445,444.416000,0.000000,444.416000,444.416000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2073.131989,0.551372,2072.537858,2073.627213,1.643736,0.011512,1.632827,1.655768,60.005000,0.004583,60.001000,60.010000,1290.595215,0.034082,1290.571875,1290.634326,247.090430,0.147177,246.998950,247.260205,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.725658,0.000284,5.725342,5.725890,5.725863,0.000287,5.725543,5.726097,2217.770833,0.003280,2217.767045,2217.772727,307.212010,0.102309,307.125770,307.325052,11276.000000,0.000000,11276,11276,7408787,1469.047764,7407584,7410424,18804995,1425.669433,18803408,18806168,3.538202,0.000696,3.537427,3.538772,3.538202,0.000696,3.537427,3.538772
wbuffix_drop,16k,4k,3,129.851562,0.317332,129.583984,130.202148,33242.093609,81.309728,33173.580440,33331.944537,7.609230,0.018652,7.592957,7.629585,0.678545,0.001663,0.677094,0.680360,961.535089,2.350198,958.946465,963.534877,254.976000,0.000000,254.976000,254.976000,14133.930667,75.674454,14090.240000,14221.312000,15488.341333,75.674454,15400.960000,15532.032000,962.417993,2.355281,959.815795,964.403761,0.882904,0.023898,0.868884,0.910497,60.005667,0.005686,60.001000,60.012000,378.619629,0.125172,378.541699,378.764014,58.495345,0.749908,57.983398,59.356128,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.947487,0.002028,5.945426,5.949480,5.977329,0.002057,5.975239,5.979352,535.553977,0.075042,535.467330,535.598011,88.928108,0.348803,88.617447,89.305431,7078.333333,49.662192,7036,7133,1994714,4889.608982,1990448,2000050,2410153,20549.724726,2392641,2432776,2.208258,0.007336,2.202062,2.216358,8.833033,0.029342,8.808246,8.865430
wbuffix_drop,16k,16k,3,420.331380,0.844476,419.475586,421.164062,26901.224863,54.053670,26846.440949,26954.517425,24.632497,0.046428,24.585205,24.678009,2.196576,0.004140,2.192359,2.200635,1188.032492,2.377653,1185.684693,1190.438915,246.101333,1.182413,244.736000,246.784000,16711.680000,0.000000,16711.680000,16711.680000,17956.864000,0.000000,17956.864000,17956.864000,1189.280575,2.381512,1186.933652,1191.695231,1.248083,0.008704,1.238974,1.256316,60.009000,0.007550,60.001000,60.016000,1279.582829,0.445502,1279.126416,1280.016553,323.504045,0.631990,322.802271,324.028271,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.956549,0.003971,5.953646,5.961075,5.978227,0.004004,5.975280,5.982786,2142.131747,1.408066,2140.532759,2143.186346,246.675608,1.006178,245.692867,247.703689,8320.666667,49.084960,8270,8368,1614315,3042.677987,1611216,1617298,3426085,22092.669968,3403230,3447327,3.122302,0.009690,3.112212,3.131535,3.122302,0.009690,3.112212,3.131535
wbuffix_drop,16k,32k,3,440.637370,0.564766,440.205078,441.276367,14100.403882,18.083196,14086.565224,14120.864652,25.819041,0.033112,25.793701,25.856506,2.302385,0.002953,2.300126,2.305726,2267.517307,2.897781,2264.239822,2269.739746,464.896000,0.000000,464.896000,464.896000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2269.184907,2.899062,2265.905181,2271.405380,1.667600,0.003646,1.665359,1.671808,60.001000,0.000000,60.001000,60.001000,1285.860042,0.011311,1285.853125,1285.873096,320.661125,1.819385,318.918530,322.548633,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.875078,0.000259,5.874799,5.875311,5.896624,0.000237,5.896365,5.896829,2173.058712,0.070586,2172.977273,2173.102273,265.946500,0.498904,265.588186,266.516315,9408.000000,34.117444,9380,9446,1692077,2170.019662,1690416,1694532,3904995,15225.394883,3892398,3921914,3.307807,0.006047,3.302627,3.314453,3.307807,0.006047,3.302627,3.314453
wbuffix_drop,32k,4k,3,68.255859,0.106816,68.140625,68.351562,17473.608927,27.369626,17444.046329,17498.066796,3.999925,0.006310,3.992958,4.005257,0.356689,0.000563,0.356068,0.357164,1830.125021,2.882042,1827.563631,1833.245723,569.344000,0.000000,569.344000,569.344000,14396.074667,75.674454,14352.384000,14483.456000,15400.960000,0.000000,15400.960000,15400.960000,1831.099710,2.871238,1828.540051,1834.204401,0.974688,0.015219,0.958678,0.988967,60.008000,0.006083,60.004000,60.015000,189.709961,0.043774,189.659619,189.739062,32.512256,0.229828,32.297266,32.754492,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.093869,0.000308,6.093524,6.094118,6.176181,0.000335,6.175818,6.176477,256.095920,0.006961,256.089844,256.103516,47.396105,0.120254,47.263138,47.497242,7210.666667,30.105371,7177,7235,1048556,1654.194769,1046730,1049954,1187740,6062.132161,1180946,1192596,2.132735,0.004001,2.128224,2.135855,17.061876,0.032007,17.025793,17.086844
wbuffix_drop,32k,16k,3,219.511068,0.139510,219.351562,219.610352,14048.746052,8.916347,14038.555100,14055.110237,12.864655,0.007058,12.856537,12.869339,1.147192,0.000629,1.146468,1.147609,2276.244736,1.442932,2275.204359,2277.891984,536.576000,0.000000,536.576000,536.576000,17519.957333,151.348909,17432.576000,17694.720000,17956.864000,0.000000,17956.864000,17956.864000,2277.514885,1.436680,2276.490396,2279.157114,1.270149,0.014067,1.259279,1.286037,60.012333,0.005508,60.007000,60.018000,741.367497,0.177993,741.249365,741.572217,82.283162,0.536635,81.875391,82.891113,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.091899,0.003243,6.089876,6.095640,6.128903,0.003175,6.126930,6.132565,1026.949110,0.057436,1026.882812,1026.983805,129.859773,0.126760,129.714410,129.947293,8279.000000,19.000000,8260,8298,843073.333333,467.341774,842535,843375,1666757,4488.711656,1662417,1671381,2.977000,0.004500,2.973113,2.981930,5.953827,0.009068,5.946008,5.963767
wbuffix_drop,32k,32k,3,424.263021,0.442190,423.780273,424.648438,13576.439450,14.148789,13560.991868,13588.769474,24.862518,0.026996,24.834229,24.888000,2.217088,0.002407,2.214566,2.219361,2355.090051,2.453522,2352.961947,2357.773717,526.336000,3.547240,522.240000,528.384000,17519.957333,151.348909,17432.576000,17694.720000,18219.008000,0.000000,18219.008000,18219.008000,2356.773062,2.460182,2354.627188,2359.458113,1.683011,0.017120,1.665241,1.699396,60.008000,0.007000,60.001000,60.015000,1278.176400,0.378518,1277.781250,1278.535742,322.329793,2.497568,320.523315,325.179907,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.123494,0.003089,6.121575,6.127057,6.168032,0.003077,6.166088,6.171579,2033.002333,0.200488,2032.770833,2033.119303,245.601071,0.520925,245.058241,246.096906,8386.000000,24.637370,8360,8409,814695.000000,884.595388,813768,815530,1722236,5435.556304,1716494,1727302,3.113961,0.004378,3.109316,3.118012,3.113961,0.004378,3.109316,3.118012
wbuffix_nodrop,4k,4k,3,415.996745,1.559303,414.744141,417.743164,106495.339067,399.194326,106174.680422,106942.442926,24.376479,0.093427,24.301861,24.481262,2.173746,0.008331,2.167092,2.183090,299.450527,1.125654,298.191441,300.359579,69.802667,0.591207,69.120000,70.144000,13347.498667,75.674454,13303.808000,13434.880000,16995.669333,151.348909,16908.288000,17170.432000,300.298083,1.122574,299.041393,301.201599,0.847556,0.004809,0.842020,0.850697,60.004000,0.005196,60.001000,60.010000,1272.908545,1.220860,1271.960205,1274.286035,321.958594,1.628044,320.716162,323.801611,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.317340,0.035223,6.276949,6.341670,6.337928,0.035194,6.297565,6.362200,2001.358805,12.555328,1992.748698,2015.765137,240.090574,2.885271,236.918231,242.558205,8204.666667,93.927277,8133,8311,6390148,24491.429202,6370587,6417616,13533841,167831.156709,13406435,13724008,3.117877,0.018126,3.104427,3.138490,3.117877,0.018126,3.104427,3.138490
wbuffix_nodrop,4k,16k,3,480.959635,0.088390,480.858398,481.021484,30781.454484,5.676365,30774.952511,30785.422673,28.186117,0.004097,28.181885,28.190063,2.513467,0.000365,2.513089,2.513819,1038.121166,0.204433,1037.985228,1038.356268,222.208000,0.000000,222.208000,222.208000,17694.720000,0.000000,17694.720000,17694.720000,18481.152000,0.000000,18481.152000,18481.152000,1039.342069,0.194117,1039.207547,1039.564602,1.220903,0.011925,1.208333,1.232058,60.010333,0.004041,60.006000,60.014000,1288.244189,0.341248,1287.867432,1288.532520,244.833455,0.259919,244.564771,245.083618,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.694211,0.001873,5.693097,5.696374,5.694428,0.001872,5.693314,5.696590,2217.591856,0.261708,2217.289773,2217.750000,305.809723,0.085867,305.711466,305.870359,11270.666667,2.309401,11268,11272,7388821,1073.948478,7387712,7389856,18814517,4586.610659,18809364,18818152,3.546349,0.000809,3.545626,3.547223,3.546349,0.000809,3.545626,3.547223
wbuffix_nodrop,4k,32k,3,482.267253,0.175663,482.105469,482.454102,15432.563638,5.622529,15427.381190,15438.541528,28.263519,0.009285,28.254028,28.272583,2.520369,0.000828,2.519523,2.521177,2071.614010,0.779629,2070.787029,2072.335555,444.416000,0.000000,444.416000,444.416000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2073.270081,0.759390,2072.462820,2073.970227,1.656070,0.020611,1.634673,1.675792,60.012000,0.004000,60.008000,60.016000,1290.716976,0.202984,1290.562500,1290.946875,247.153483,0.359317,246.785425,247.503369,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.693233,0.000208,5.693038,5.693451,5.693439,0.000205,5.693245,5.693653,2217.770833,0.003280,2217.767045,2217.772727,307.234372,0.180057,307.052331,307.412378,11276.000000,0.000000,11276,11276,7409112,2433.933442,7406624,7411488,18804544,2463.636337,18802256,18807152,3.538030,0.001166,3.536907,3.539234,3.538030,0.001166,3.536907,3.539234
wbuffix_nodrop,16k,4k,3,129.721029,0.034614,129.697266,129.760742,33208.730863,8.873758,33202.646623,33218.913018,7.601171,0.001933,7.599609,7.603333,0.677826,0.000172,0.677687,0.678019,962.519565,0.258543,962.223264,962.699315,256.341333,1.182413,254.976000,257.024000,14046.549333,75.674454,13959.168000,14090.240000,15313.578667,75.674454,15269.888000,15400.960000,963.388963,0.260120,963.090408,963.566723,0.869398,0.003677,0.867144,0.873642,60.002333,0.002309,60.001000,60.005000,378.912272,0.233501,378.642969,379.058301,58.226180,0.104506,58.142700,58.343384,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.913335,0.002031,5.911013,5.914784,5.943252,0.002050,5.940904,5.944689,535.594697,0.017050,535.575994,535.609375,88.771938,0.036455,88.740870,88.812070,7056.000000,4.582576,7052,7061,1992601,505.546569,1992192,1993166,2400837,1819.679184,2399217,2402806,2.204876,0.000610,2.204310,2.205522,8.819502,0.002435,8.817241,8.822080
wbuffix_nodrop,16k,16k,3,420.387695,1.287151,419.193359,421.750977,26904.845988,82.372114,26828.405720,26992.084784,24.635000,0.077220,24.562958,24.716522,2.196800,0.006886,2.190375,2.204069,1187.875511,3.627871,1184.052978,1191.270901,246.784000,0.000000,246.784000,246.784000,16842.752000,113.511682,16711.680000,16908.288000,17956.864000,0.000000,17956.864000,17956.864000,1189.130937,3.644724,1185.275408,1192.519928,1.255426,0.036618,1.222431,1.294822,60.007000,0.004583,60.002000,60.011000,1280.453581,0.118751,1280.323437,1280.556055,323.406584,1.169856,322.717505,324.757324,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.920957,0.000101,5.920850,5.921050,5.942692,0.000114,5.942568,5.942793,2143.199811,0.032681,2143.167614,2143.232955,246.588437,1.449815,245.238210,248.120655,8319.666667,74.968882,8250,8399,1614479,5060.688227,1609758,1619822,3425415,33300.380719,3394501,3460675,3.121655,0.013967,3.108703,3.136454,3.121655,0.013967,3.108703,3.136454
wbuffix_nodrop,16k,32k,3,441.581380,1.300559,440.150391,442.691406,14130.610953,41.620237,14084.817783,14166.136208,25.878377,0.076118,25.794800,25.943726,2.307677,0.006788,2.300224,2.313504,2262.687622,6.689026,2256.992831,2270.053876,464.896000,0.000000,464.896000,464.896000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2264.342926,6.667421,2258.667132,2271.685656,1.655304,0.021619,1.631780,1.674301,60.010333,0.001155,60.009000,60.011000,1285.856185,0.008157,1285.850000,1285.865430,321.430802,1.819218,319.397363,322.904028,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.844037,0.001268,5.843275,5.845501,5.865590,0.001295,5.864806,5.867085,2172.678030,0.557668,2172.034091,2173.000000,266.960233,1.474794,265.355505,268.256209,9463.333333,65.248244,9392,9520,1695965,4988.468837,1690488,1700248,3929382,28415.406033,3898342,3954112,3.316880,0.009950,3.306045,3.325609,3.316880,0.009950,3.306045,3.325609
wbuffix_nodrop,32k,4k,3,68.288411,0.048064,68.236328,68.331055,17481.883987,12.240671,17468.632842,17492.768595,4.002019,0.002797,3.999252,4.004845,0.356876,0.000249,0.356629,0.357128,1829.244946,1.279234,1828.107287,1830.629704,572.074667,4.729653,569.344000,577.536000,14483.456000,0.000000,14483.456000,14483.456000,15444.650667,75.674454,15400.960000,15532.032000,1830.215014,1.275806,1829.075747,1831.593495,0.970068,0.007216,0.963791,0.977952,60.011000,0.007810,60.002000,60.016000,189.792578,0.123413,189.655078,189.893750,32.631437,0.266165,32.324097,32.785229,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.061284,0.000185,6.061112,6.061479,6.143867,0.000148,6.143710,6.144004,256.081597,0.007171,256.074219,256.088542,47.437036,0.053786,47.383753,47.491310,7222.666667,14.011900,7209,7237,1049105,733.120272,1048380,1049846,1190282,2836.154850,1187519,1193186,2.134567,0.001911,2.132718,2.136534,17.076539,0.015287,17.061745,17.092274
wbuffix_nodrop,32k,16k,3,219.565430,0.381168,219.137695,219.869141,14052.221929,24.404132,14024.842961,14071.686857,12.868195,0.021732,12.843765,12.885376,1.147507,0.001938,1.145329,1.149040,2275.722191,3.928159,2272.596578,2280.131635,536.576000,0.000000,536.576000,536.576000,17607.338667,151.348909,17432.576000,17694.720000,17956.864000,0.000000,17956.864000,17956.864000,2276.967868,3.939420,2273.826587,2281.387771,1.245677,0.013820,1.230009,1.256136,60.014000,0.003000,60.011000,60.017000,741.171875,0.006250,741.165625,741.178125,82.161125,0.395813,81.829932,82.599487,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.063811,0.000189,6.063629,6.064007,6.100946,0.000167,6.100835,6.101138,1026.857639,0.015912,1026.843750,1026.875000,129.921809,0.412038,129.459084,130.249032,8289.666667,45.829394,8241,8332,843318.666667,1426.179979,841716,844448,1669245,10323.704390,1658397,1678949,2.979367,0.008984,2.970257,2.988221,5.958654,0.017986,5.940423,5.976385
wbuffix_nodrop,32k,32k,3,424.649089,0.172557,424.518555,424.844727,13588.794554,5.522014,13584.623590,13595.056749,24.884176,0.009552,24.874603,24.893707,2.219020,0.000852,2.218166,2.219870,2352.949721,0.954416,2351.873088,2353.691890,522.240000,0.000000,522.240000,522.240000,17694.720000,0.000000,17694.720000,17694.720000,18219.008000,0.000000,18219.008000,18219.008000,2354.621780,0.952979,2353.546356,2355.361397,1.672059,0.002211,1.669507,1.673402,60.005667,0.008083,60.001000,60.015000,1278.010417,0.242793,1277.778125,1278.262500,322.791146,1.322125,321.330151,323.905225,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.096037,0.000145,6.095870,6.096136,6.140553,0.000158,6.140373,6.140668,2032.770833,0.005208,2032.765625,2032.776042,246.010561,0.174137,245.838406,246.186614,8409.000000,10.148892,8398,8418,815404.666667,313.002130,815091,815717,1727406,2295.000073,1724901,1729407,3.118465,0.002022,3.116207,3.120107,3.118465,0.002022,3.116207,3.120107
```

### 11.1.6 파티션별 GC 로그 (회차마다: 첫 GC 줄의 fio 시작 기준 시각·내용, rmmod 통계)
```
[wbuffix_drop map4k bs4k r1]
  +6.341s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.343s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.360s first GC part=3 victim line=194 vpc=1892 ipc=156 free_lines=2 host_pgs=778240
  +6.361s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1597461 gc_pgs=3381145 gc_cnt=2050 free_lines=2
  stats part=1 host_pgs=1597735 gc_pgs=3380899 gc_cnt=2050 free_lines=2
  stats part=2 host_pgs=1597469 gc_pgs=3389226 gc_cnt=2054 free_lines=2
  stats part=3 host_pgs=1597095 gc_pgs=3371455 gc_cnt=2045 free_lines=2
  (kernel) [67210.965607] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67211.032437] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs4k r2]
  +6.366s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.368s first GC part=2 victim line=340 vpc=1890 ipc=158 free_lines=2 host_pgs=778240
  +6.386s first GC part=3 victim line=194 vpc=1893 ipc=155 free_lines=2 host_pgs=778240
  +6.387s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1607664 gc_pgs=3452870 gc_cnt=2090 free_lines=3
  stats part=1 host_pgs=1607796 gc_pgs=3452779 gc_cnt=2090 free_lines=2
  stats part=2 host_pgs=1607727 gc_pgs=3466993 gc_cnt=2097 free_lines=2
  stats part=3 host_pgs=1607264 gc_pgs=3451168 gc_cnt=2089 free_lines=2
  (kernel) [68407.967322] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68408.035617] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs4k r3]
  +6.313s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.315s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.333s first GC part=3 victim line=194 vpc=1892 ipc=156 free_lines=2 host_pgs=778240
  +6.334s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1606313 gc_pgs=3445950 gc_cnt=2086 free_lines=2
  stats part=1 host_pgs=1606458 gc_pgs=3441754 gc_cnt=2084 free_lines=2
  stats part=2 host_pgs=1606306 gc_pgs=3452131 gc_cnt=2089 free_lines=2
  stats part=3 host_pgs=1605923 gc_pgs=3434158 gc_cnt=2080 free_lines=2
  (kernel) [69745.871919] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69745.938981] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs16k r1]
  +5.722s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.722s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.722s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.722s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1845896 gc_pgs=4703455 gc_cnt=2817 free_lines=2
  stats part=1 host_pgs=1845896 gc_pgs=4703455 gc_cnt=2817 free_lines=2
  stats part=2 host_pgs=1845896 gc_pgs=4703455 gc_cnt=2817 free_lines=2
  stats part=3 host_pgs=1845896 gc_pgs=4703455 gc_cnt=2817 free_lines=2
  (kernel) [67351.932797] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67352.001471] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs16k r2]
  +5.729s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.729s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.729s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.729s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1847304 gc_pgs=4704216 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1847304 gc_pgs=4704216 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1847304 gc_pgs=4704216 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1847304 gc_pgs=4704216 gc_cnt=2818 free_lines=2
  (kernel) [68548.916657] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68548.984246] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs16k r3]
  +5.719s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.719s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.719s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.719s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1846936 gc_pgs=4704536 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1846936 gc_pgs=4704536 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1846936 gc_pgs=4704536 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1846936 gc_pgs=4704536 gc_cnt=2818 free_lines=2
  (kernel) [69886.827189] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69886.895529] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs32k r1]
  +5.726s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.726s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.726s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.726s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852088 gc_pgs=4701352 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1852088 gc_pgs=4701352 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1852088 gc_pgs=4701352 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1852088 gc_pgs=4701352 gc_cnt=2819 free_lines=2
  (kernel) [67492.853264] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67492.920608] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs32k r2]
  +5.726s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.726s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.726s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.726s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852606 gc_pgs=4700852 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1852606 gc_pgs=4700852 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1852606 gc_pgs=4700852 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1852606 gc_pgs=4700852 gc_cnt=2819 free_lines=2
  (kernel) [68689.852628] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68689.919706] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map4k bs32k r3]
  +5.725s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.725s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.725s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.726s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1851896 gc_pgs=4701542 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1851896 gc_pgs=4701542 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1851896 gc_pgs=4701542 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1851896 gc_pgs=4701542 gc_cnt=2819 free_lines=2
  (kernel) [70027.734447] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70027.802898] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs4k r1]
  +5.949s first GC part=2 victim line=6 vpc=172 ipc=340 free_lines=2 host_pgs=194560
  +5.961s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.978s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.979s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497541 gc_pgs=598809 gc_cnt=1760 free_lines=2
  stats part=1 host_pgs=498557 gc_pgs=597295 gc_cnt=1759 free_lines=2
  stats part=2 host_pgs=499565 gc_pgs=609569 gc_cnt=1785 free_lines=2
  stats part=3 host_pgs=497981 gc_pgs=599370 gc_cnt=1762 free_lines=2
  (kernel) [67633.700023] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67633.727707] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs4k r2]
  +5.948s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.959s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.976s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.977s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=499164 gc_pgs=605805 gc_cnt=1777 free_lines=2
  stats part=1 host_pgs=500133 gc_pgs=605417 gc_cnt=1778 free_lines=2
  stats part=2 host_pgs=501180 gc_pgs=615638 gc_cnt=1800 free_lines=2
  stats part=3 host_pgs=499573 gc_pgs=605916 gc_cnt=1778 free_lines=2
  (kernel) [68830.770185] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68830.798021] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs4k r3]
  +5.945s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.957s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.974s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.975s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=496732 gc_pgs=596463 gc_cnt=1754 free_lines=2
  stats part=1 host_pgs=497751 gc_pgs=593955 gc_cnt=1751 free_lines=1
  stats part=2 host_pgs=498772 gc_pgs=605714 gc_cnt=1776 free_lines=1
  stats part=3 host_pgs=497193 gc_pgs=596509 gc_cnt=1755 free_lines=1
  (kernel) [70168.575760] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70168.603670] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs16k r1]
  +5.955s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.956s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.976s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.977s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=403651 gc_pgs=859917 gc_cnt=2087 free_lines=2
  stats part=1 host_pgs=403760 gc_pgs=859310 gc_cnt=2086 free_lines=2
  stats part=2 host_pgs=403724 gc_pgs=855816 gc_cnt=2079 free_lines=2
  stats part=3 host_pgs=403297 gc_pgs=852654 gc_cnt=2072 free_lines=2
  (kernel) [67774.479930] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67774.507678] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs16k r2]
  +5.954s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.955s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.975s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.975s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=402842 gc_pgs=852545 gc_cnt=2071 free_lines=2
  stats part=1 host_pgs=402977 gc_pgs=853962 gc_cnt=2074 free_lines=2
  stats part=2 host_pgs=402935 gc_pgs=849927 gc_cnt=2066 free_lines=2
  stats part=3 host_pgs=402462 gc_pgs=846796 gc_cnt=2059 free_lines=2
  (kernel) [68971.595949] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68971.623954] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs16k r3]
  +5.961s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.962s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.983s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.983s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=404414 gc_pgs=864271 gc_cnt=2097 free_lines=2
  stats part=1 host_pgs=404457 gc_pgs=865274 gc_cnt=2099 free_lines=3
  stats part=2 host_pgs=404408 gc_pgs=859203 gc_cnt=2087 free_lines=2
  stats part=3 host_pgs=404019 gc_pgs=858579 gc_cnt=2085 free_lines=2
  (kernel) [70309.330051] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70309.357946] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs32k r1]
  +5.875s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.875s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.897s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.897s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=422954 gc_pgs=976319 gc_cnt=2352 free_lines=2
  stats part=1 host_pgs=422954 gc_pgs=976319 gc_cnt=2352 free_lines=2
  stats part=2 host_pgs=422687 gc_pgs=974017 gc_cnt=2347 free_lines=2
  stats part=3 host_pgs=422687 gc_pgs=974017 gc_cnt=2347 free_lines=2
  (kernel) [67915.230966] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67915.258758] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs32k r2]
  +5.875s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.875s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.896s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.896s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=422750 gc_pgs=975003 gc_cnt=2349 free_lines=2
  stats part=1 host_pgs=422750 gc_pgs=975003 gc_cnt=2349 free_lines=2
  stats part=2 host_pgs=422458 gc_pgs=971196 gc_cnt=2341 free_lines=2
  stats part=3 host_pgs=422458 gc_pgs=971196 gc_cnt=2341 free_lines=2
  (kernel) [69112.345869] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69112.374182] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map16k bs32k r3]
  +5.875s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.875s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.897s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.897s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=423763 gc_pgs=981646 gc_cnt=2364 free_lines=2
  stats part=1 host_pgs=423763 gc_pgs=981646 gc_cnt=2364 free_lines=2
  stats part=2 host_pgs=423503 gc_pgs=979311 gc_cnt=2359 free_lines=2
  stats part=3 host_pgs=423503 gc_pgs=979311 gc_cnt=2359 free_lines=2
  (kernel) [70450.077391] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70450.105079] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs4k r1]
  +6.094s first GC part=0 victim line=8 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.131s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.154s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.176s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262618 gc_pgs=296286 gc_cnt=1802 free_lines=2
  stats part=1 host_pgs=262685 gc_pgs=302364 gc_cnt=1826 free_lines=1
  stats part=2 host_pgs=262145 gc_pgs=297762 gc_cnt=1806 free_lines=1
  stats part=3 host_pgs=261537 gc_pgs=293267 gc_cnt=1786 free_lines=2
  (kernel) [68055.993138] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68056.013857] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs4k r2]
  +6.094s first GC part=0 victim line=8 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.130s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.154s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.176s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262016 gc_pgs=294586 gc_cnt=1793 free_lines=2
  stats part=1 host_pgs=262111 gc_pgs=299091 gc_cnt=1811 free_lines=2
  stats part=2 host_pgs=261597 gc_pgs=295764 gc_cnt=1796 free_lines=2
  stats part=3 host_pgs=261006 gc_pgs=291505 gc_cnt=1777 free_lines=2
  (kernel) [69253.121868] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69253.142720] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs4k r3]
  +6.094s first GC part=0 victim line=6 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.131s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.154s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.176s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262880 gc_pgs=297330 gc_cnt=1807 free_lines=2
  stats part=1 host_pgs=262942 gc_pgs=302618 gc_cnt=1828 free_lines=1
  stats part=2 host_pgs=262387 gc_pgs=298836 gc_cnt=1811 free_lines=2
  stats part=3 host_pgs=261745 gc_pgs=293812 gc_cnt=1789 free_lines=2
  (kernel) [70590.852727] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70590.873557] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs16k r1]
  +6.090s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.115s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.126s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.127s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210841 gc_pgs=416435 gc_cnt=2069 free_lines=2
  stats part=1 host_pgs=210968 gc_pgs=417328 gc_cnt=2073 free_lines=1
  stats part=2 host_pgs=210946 gc_pgs=419142 gc_cnt=2080 free_lines=1
  stats part=3 host_pgs=210620 gc_pgs=413569 gc_cnt=2057 free_lines=2
  (kernel) [68196.726353] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68196.747099] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs16k r2]
  +6.096s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.121s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.132s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.133s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210829 gc_pgs=418740 gc_cnt=2078 free_lines=2
  stats part=1 host_pgs=210950 gc_pgs=418612 gc_cnt=2078 free_lines=1
  stats part=2 host_pgs=210931 gc_pgs=420167 gc_cnt=2084 free_lines=2
  stats part=3 host_pgs=210600 gc_pgs=413862 gc_cnt=2058 free_lines=2
  (kernel) [69393.883953] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69393.904772] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs16k r3]
  +6.090s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.115s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.126s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.127s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210623 gc_pgs=414844 gc_cnt=2062 free_lines=2
  stats part=1 host_pgs=210756 gc_pgs=417267 gc_cnt=2072 free_lines=2
  stats part=2 host_pgs=210759 gc_pgs=417277 gc_cnt=2072 free_lines=2
  stats part=3 host_pgs=210397 gc_pgs=413029 gc_cnt=2054 free_lines=2
  (kernel) [70731.608864] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70731.629824] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs32k r1]
  +6.122s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.145s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.166s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.166s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203544 gc_pgs=428509 gc_cnt=2088 free_lines=2
  stats part=1 host_pgs=203271 gc_pgs=428033 gc_cnt=2085 free_lines=1
  stats part=2 host_pgs=203606 gc_pgs=431003 gc_cnt=2098 free_lines=2
  stats part=3 host_pgs=203347 gc_pgs=428949 gc_cnt=2089 free_lines=2
  (kernel) [68337.496648] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68337.517128] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs32k r2]
  +6.127s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.150s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.171s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.172s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203957 gc_pgs=430917 gc_cnt=2099 free_lines=2
  stats part=1 host_pgs=203706 gc_pgs=430168 gc_cnt=2095 free_lines=2
  stats part=2 host_pgs=204070 gc_pgs=433880 gc_cnt=2111 free_lines=2
  stats part=3 host_pgs=203797 gc_pgs=432337 gc_cnt=2104 free_lines=2
  (kernel) [69534.631108] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69534.652062] NVMeVirt: Virtual NVMe device closed
[wbuffix_drop map32k bs32k r3]
  +6.122s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.145s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.166s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.166s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203777 gc_pgs=429829 gc_cnt=2094 free_lines=1
  stats part=1 host_pgs=203518 gc_pgs=430070 gc_cnt=2094 free_lines=3
  stats part=2 host_pgs=203875 gc_pgs=432518 gc_cnt=2105 free_lines=2
  stats part=3 host_pgs=203617 gc_pgs=430494 gc_cnt=2096 free_lines=2
  (kernel) [70872.377095] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70872.398116] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs4k r1]
  +6.277s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.279s first GC part=2 victim line=340 vpc=1890 ipc=158 free_lines=2 host_pgs=778240
  +6.296s first GC part=3 victim line=194 vpc=1892 ipc=156 free_lines=2 host_pgs=778240
  +6.298s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1592612 gc_pgs=3351083 gc_cnt=2033 free_lines=2
  stats part=1 host_pgs=1592973 gc_pgs=3350951 gc_cnt=2033 free_lines=2
  stats part=2 host_pgs=1592635 gc_pgs=3359213 gc_cnt=2037 free_lines=2
  stats part=3 host_pgs=1592367 gc_pgs=3345188 gc_cnt=2030 free_lines=2
  (kernel) [67140.460648] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67140.529053] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs4k r2]
  +6.342s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.344s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.361s first GC part=3 victim line=194 vpc=1893 ipc=155 free_lines=2 host_pgs=778240
  +6.362s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1595554 gc_pgs=3364734 gc_cnt=2041 free_lines=2
  stats part=1 host_pgs=1595898 gc_pgs=3366496 gc_cnt=2042 free_lines=2
  stats part=2 host_pgs=1595572 gc_pgs=3376919 gc_cnt=2047 free_lines=2
  stats part=3 host_pgs=1595216 gc_pgs=3362932 gc_cnt=2040 free_lines=2
  (kernel) [68478.392986] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68478.461462] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs4k r3]
  +6.333s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.335s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.353s first GC part=3 victim line=194 vpc=1893 ipc=155 free_lines=2 host_pgs=778240
  +6.354s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1604455 gc_pgs=3431525 gc_cnt=2078 free_lines=2
  stats part=1 host_pgs=1604663 gc_pgs=3429162 gc_cnt=2077 free_lines=2
  stats part=2 host_pgs=1604426 gc_pgs=3437602 gc_cnt=2081 free_lines=2
  stats part=3 host_pgs=1604072 gc_pgs=3425719 gc_cnt=2075 free_lines=2
  (kernel) [69675.373308] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69675.440673] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs16k r1]
  +5.696s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.696s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.697s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.697s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  stats part=1 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  stats part=2 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  stats part=3 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  (kernel) [67281.393642] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67281.461990] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs16k r2]
  +5.693s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  (kernel) [68619.388342] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68619.455881] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs16k r3]
  +5.693s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  (kernel) [69816.320560] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69816.387816] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs32k r1]
  +5.693s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  (kernel) [67422.380994] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67422.447910] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs32k r2]
  +5.693s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  (kernel) [68760.303887] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68760.372192] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map4k bs32k r3]
  +5.693s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.694s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.694s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.694s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  (kernel) [69957.284852] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69957.352073] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs4k r1]
  +5.915s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.926s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.944s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.945s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497230 gc_pgs=597554 gc_cnt=1757 free_lines=1
  stats part=1 host_pgs=498246 gc_pgs=596551 gc_cnt=1757 free_lines=1
  stats part=2 host_pgs=499280 gc_pgs=608304 gc_cnt=1782 free_lines=1
  stats part=3 host_pgs=497688 gc_pgs=598080 gc_cnt=1759 free_lines=1
  (kernel) [67563.295634] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67563.323382] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs4k r2]
  +5.911s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.940s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.941s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497426 gc_pgs=598400 gc_cnt=1759 free_lines=2
  stats part=1 host_pgs=498431 gc_pgs=597368 gc_cnt=1759 free_lines=2
  stats part=2 host_pgs=499452 gc_pgs=608601 gc_cnt=1783 free_lines=2
  stats part=3 host_pgs=497857 gc_pgs=598437 gc_cnt=1760 free_lines=2
  (kernel) [68901.156550] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68901.184548] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs4k r3]
  +5.914s first GC part=2 victim line=6 vpc=172 ipc=340 free_lines=2 host_pgs=194560
  +5.925s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.944s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497171 gc_pgs=597627 gc_cnt=1757 free_lines=1
  stats part=1 host_pgs=498188 gc_pgs=596061 gc_cnt=1756 free_lines=1
  stats part=2 host_pgs=499219 gc_pgs=607359 gc_cnt=1780 free_lines=1
  stats part=3 host_pgs=497614 gc_pgs=598170 gc_cnt=1759 free_lines=2
  (kernel) [70098.161111] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70098.188836] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs16k r1]
  +5.921s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.943s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=402514 gc_pgs=851867 gc_cnt=2069 free_lines=2
  stats part=1 host_pgs=402592 gc_pgs=851296 gc_cnt=2068 free_lines=2
  stats part=2 host_pgs=402576 gc_pgs=846185 gc_cnt=2058 free_lines=2
  stats part=3 host_pgs=402076 gc_pgs=845153 gc_cnt=2055 free_lines=2
  (kernel) [67704.063442] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67704.091003] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs16k r2]
  +5.921s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.942s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=403495 gc_pgs=857538 gc_cnt=2082 free_lines=2
  stats part=1 host_pgs=403619 gc_pgs=858429 gc_cnt=2084 free_lines=2
  stats part=2 host_pgs=403588 gc_pgs=854387 gc_cnt=2076 free_lines=2
  stats part=3 host_pgs=403156 gc_pgs=850715 gc_cnt=2068 free_lines=2
  (kernel) [69041.945393] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69041.973688] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs16k r3]
  +5.921s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.943s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=405037 gc_pgs=867257 gc_cnt=2104 free_lines=2
  stats part=1 host_pgs=405096 gc_pgs=866690 gc_cnt=2103 free_lines=2
  stats part=2 host_pgs=405065 gc_pgs=865195 gc_cnt=2100 free_lines=2
  stats part=3 host_pgs=404624 gc_pgs=861533 gc_cnt=2092 free_lines=2
  (kernel) [70238.949395] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70238.977171] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs32k r1]
  +5.843s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.843s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.865s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.865s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=422769 gc_pgs=976483 gc_cnt=2352 free_lines=2
  stats part=1 host_pgs=422769 gc_pgs=976483 gc_cnt=2352 free_lines=2
  stats part=2 host_pgs=422475 gc_pgs=972688 gc_cnt=2344 free_lines=2
  stats part=3 host_pgs=422475 gc_pgs=972688 gc_cnt=2344 free_lines=2
  (kernel) [67844.827448] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67844.855323] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs32k r2]
  +5.846s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.846s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.867s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.867s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=425136 gc_pgs=988954 gc_cnt=2381 free_lines=2
  stats part=1 host_pgs=425136 gc_pgs=988954 gc_cnt=2381 free_lines=2
  stats part=2 host_pgs=424988 gc_pgs=988102 gc_cnt=2379 free_lines=2
  stats part=3 host_pgs=424988 gc_pgs=988102 gc_cnt=2379 free_lines=2
  (kernel) [69182.714346] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69182.742224] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map16k bs32k r3]
  +5.843s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.843s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.865s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.865s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=424386 gc_pgs=985094 gc_cnt=2372 free_lines=2
  stats part=1 host_pgs=424386 gc_pgs=985094 gc_cnt=2372 free_lines=2
  stats part=2 host_pgs=424194 gc_pgs=982752 gc_cnt=2367 free_lines=2
  stats part=3 host_pgs=424194 gc_pgs=982752 gc_cnt=2367 free_lines=2
  (kernel) [70379.700715] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70379.728885] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs4k r1]
  +6.061s first GC part=0 victim line=6 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.099s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.122s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.144s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262646 gc_pgs=296766 gc_cnt=1804 free_lines=2
  stats part=1 host_pgs=262714 gc_pgs=302106 gc_cnt=1825 free_lines=1
  stats part=2 host_pgs=262172 gc_pgs=297736 gc_cnt=1806 free_lines=1
  stats part=3 host_pgs=261558 gc_pgs=293532 gc_cnt=1787 free_lines=2
  (kernel) [67985.618551] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67985.639448] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs4k r2]
  +6.061s first GC part=0 victim line=8 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.098s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.121s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.144s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262452 gc_pgs=295672 gc_cnt=1799 free_lines=2
  stats part=1 host_pgs=262533 gc_pgs=301755 gc_cnt=1823 free_lines=2
  stats part=2 host_pgs=262006 gc_pgs=297157 gc_cnt=1803 free_lines=2
  stats part=3 host_pgs=261389 gc_pgs=292935 gc_cnt=1784 free_lines=1
  (kernel) [69323.475405] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69323.496390] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs4k r3]
  +6.061s first GC part=0 victim line=8 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.098s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.122s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.144s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262850 gc_pgs=298109 gc_cnt=1810 free_lines=2
  stats part=1 host_pgs=262911 gc_pgs=302397 gc_cnt=1827 free_lines=2
  stats part=2 host_pgs=262363 gc_pgs=298831 gc_cnt=1811 free_lines=2
  stats part=3 host_pgs=261722 gc_pgs=293849 gc_cnt=1789 free_lines=2
  (kernel) [70520.457108] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70520.477622] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs16k r1]
  +6.064s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.089s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.100s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.101s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210418 gc_pgs=414554 gc_cnt=2060 free_lines=2
  stats part=1 host_pgs=210533 gc_pgs=415966 gc_cnt=2066 free_lines=2
  stats part=2 host_pgs=210575 gc_pgs=417709 gc_cnt=2073 free_lines=2
  stats part=3 host_pgs=210190 gc_pgs=410168 gc_cnt=2042 free_lines=1
  (kernel) [68126.345737] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68126.366307] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs16k r2]
  +6.064s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.089s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.100s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.101s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=211115 gc_pgs=419470 gc_cnt=2082 free_lines=2
  stats part=1 host_pgs=211238 gc_pgs=420384 gc_cnt=2086 free_lines=1
  stats part=2 host_pgs=211230 gc_pgs=422434 gc_cnt=2094 free_lines=1
  stats part=3 host_pgs=210865 gc_pgs=416661 gc_cnt=2070 free_lines=2
  (kernel) [69464.250543] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69464.271401] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs16k r3]
  +6.064s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.089s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.100s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.101s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210949 gc_pgs=416838 gc_cnt=2071 free_lines=1
  stats part=1 host_pgs=211076 gc_pgs=419523 gc_cnt=2082 free_lines=2
  stats part=2 host_pgs=211056 gc_pgs=419787 gc_cnt=2083 free_lines=2
  stats part=3 host_pgs=210711 gc_pgs=414242 gc_cnt=2060 free_lines=1
  (kernel) [70661.212390] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70661.233168] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs32k r1]
  +6.096s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.119s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.140s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.141s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203850 gc_pgs=430262 gc_cnt=2096 free_lines=2
  stats part=1 host_pgs=203598 gc_pgs=428726 gc_cnt=2089 free_lines=2
  stats part=2 host_pgs=203954 gc_pgs=433212 gc_cnt=2108 free_lines=2
  stats part=3 host_pgs=203689 gc_pgs=432701 gc_cnt=2105 free_lines=2
  (kernel) [68267.097035] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68267.118069] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs32k r2]
  +6.096s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.119s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.140s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.140s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=204011 gc_pgs=431643 gc_cnt=2102 free_lines=2
  stats part=1 host_pgs=203744 gc_pgs=430879 gc_cnt=2098 free_lines=2
  stats part=2 host_pgs=204115 gc_pgs=434591 gc_cnt=2114 free_lines=2
  stats part=3 host_pgs=203847 gc_pgs=432294 gc_cnt=2104 free_lines=2
  (kernel) [69604.999711] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69605.020648] NVMeVirt: Virtual NVMe device closed
[wbuffix_nodrop map32k bs32k r3]
  +6.096s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.119s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.140s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.141s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203929 gc_pgs=431205 gc_cnt=2100 free_lines=2
  stats part=1 host_pgs=203675 gc_pgs=430945 gc_cnt=2098 free_lines=2
  stats part=2 host_pgs=204034 gc_pgs=433652 gc_cnt=2110 free_lines=2
  stats part=3 host_pgs=203768 gc_pgs=432109 gc_cnt=2103 free_lines=3
  (kernel) [70801.976214] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70801.996911] NVMeVirt: Virtual NVMe device closed
```

### 11.1.7 1 초 평균 대역폭 시계열 (MiB/s, t=1..60 s, fio_bw.1.log 의 0.5 s 값 두 개 평균)
형식: variant map bs rep | gc_onset_s | 값 60개 (공백 구분)
```
wbuffix_drop 4k 4k r1 | 6.341 | 1999 1991 1998 2002 2000 2037 273 128 145 152 171 155 164 153 180 171 176 166 168 172 187 194 182 179 181 187 183 175 201 200 188 183 199 229 262 198 221 231 215 252 263 255 264 275 284 315 339 384 415 514 616 1314 121 134 145 161 178 167 175 191
wbuffix_drop 4k 4k r2 | 6.366 | 1995 1986 1980 1990 1992 2030 323 129 146 149 181 175 199 211 157 172 187 179 173 175 169 173 183 209 211 205 219 220 183 239 202 225 224 192 227 204 235 262 242 247 274 262 278 296 316 348 332 421 453 580 1326 119 133 136 166 174 175 198 169 168
wbuffix_drop 4k 4k r3 | 6.313 | 2011 2008 2007 2007 2003 2051 216 130 151 155 180 170 172 201 164 151 169 199 215 175 193 180 222 196 199 193 191 210 202 200 201 212 210 182 202 216 211 285 235 228 242 258 284 284 312 327 362 427 429 517 1234 396 132 144 152 155 182 199 200 159
wbuffix_drop 4k 16k r1 | 5.722 | 2235 2233 2233 2233 2228 1097 130 146 164 185 208 236 221 204 217 227 232 245 240 248 259 262 274 281 290 308 320 326 348 369 396 421 462 516 574 699 921 1510 126 140 157 178 200 225 245 200 210 221 231 237 245 245 246 263 270 283 289 301 310 328
wbuffix_drop 4k 16k r2 | 5.729 | 2234 2233 2227 2233 2233 1098 129 144 164 185 209 234 220 204 215 228 234 244 240 252 256 263 275 281 295 303 320 333 345 370 396 421 464 518 582 690 934 1495 127 140 156 177 204 225 241 200 215 223 231 238 246 246 248 262 269 279 296 300 310 330
wbuffix_drop 4k 16k r3 | 5.719 | 2235 2233 2233 2233 2233 1091 130 146 164 186 211 232 221 205 216 228 236 241 240 251 257 261 277 280 297 301 321 333 343 372 397 420 472 508 586 702 944 1466 127 141 159 179 202 226 239 201 215 222 231 235 246 246 246 263 269 282 289 301 311 326
wbuffix_drop 4k 32k r1 | 5.726 | 2234 2233 2233 2233 2233 1098 137 151 166 188 213 232 222 208 215 226 235 239 244 254 257 264 278 284 297 302 321 336 348 370 398 436 466 523 596 728 1006 1319 132 147 164 183 206 228 228 204 216 227 236 241 243 248 260 262 275 279 294 306 314 326
wbuffix_drop 4k 32k r2 | 5.726 | 2234 2233 2233 2233 2233 1098 137 148 168 188 215 231 222 208 215 224 237 239 244 250 258 265 280 284 299 295 318 337 351 373 397 431 472 523 599 731 1019 1289 133 147 161 185 207 228 227 204 215 228 239 242 244 250 256 264 275 278 296 304 318 325
wbuffix_drop 4k 32k r3 | 5.725 | 2234 2233 2233 2233 2233 1097 137 150 167 188 214 231 222 208 215 227 234 238 244 255 254 265 278 282 297 303 320 329 354 374 398 426 473 517 595 727 1003 1329 130 146 163 183 204 228 232 205 215 220 234 241 246 246 256 269 270 278 294 309 309 333
wbuffix_drop 16k 4k r1 | 5.949 | 536 533 538 536 535 430 180 160 175 165 151 140 141 133 118 123 109 116 106 104 102 99 95 90 94 85 81 81 80 78 79 72 75 74 71 77 67 67 62 66 61 71 61 58 59 57 57 59 57 54 57 58 54 56 59 57 55 55 59 58
wbuffix_drop 16k 4k r2 | 5.948 | 536 533 538 536 535 430 182 167 176 161 150 144 141 132 117 120 113 110 106 109 103 99 95 89 94 90 81 81 79 80 75 72 79 74 69 72 67 68 65 65 65 66 61 67 60 60 59 61 65 61 54 55 52 64 55 56 61 55 54 56
wbuffix_drop 16k 4k r3 | 5.945 | 536 533 538 536 535 430 178 161 174 164 153 139 144 132 121 125 105 112 106 107 101 96 93 90 90 89 81 81 81 78 76 75 73 71 70 71 73 66 65 64 62 63 62 66 61 62 65 57 62 55 57 56 58 56 57 52 54 55 54 47
wbuffix_drop 16k 16k r1 | 5.955 | 2141 2141 2143 2147 2140 1514 134 138 145 150 168 177 177 173 173 178 170 182 178 184 187 190 185 185 192 203 206 195 199 211 201 223 225 225 218 224 238 233 233 246 272 283 289 301 338 355 397 468 544 1074 652 132 148 152 158 170 177 176 168 179
wbuffix_drop 16k 16k r2 | 5.954 | 2140 2141 2143 2149 2140 1514 136 136 144 157 177 170 187 173 176 170 176 184 184 165 178 183 188 194 188 193 204 201 208 206 195 203 215 205 200 218 248 230 244 243 249 261 281 294 321 352 399 429 486 752 1188 131 135 148 151 175 176 182 190 172
wbuffix_drop 16k 16k r3 | 5.961 | 2137 2136 2141 2149 2135 1526 135 139 141 157 161 166 173 170 168 162 183 165 183 183 201 194 200 184 211 193 207 195 210 242 193 216 219 213 239 215 237 244 232 240 268 288 289 303 332 383 395 485 616 1283 351 133 146 156 156 177 185 185 178 172
wbuffix_drop 16k 32k r1 | 5.875 | 2177 2175 2169 2167 2173 1377 139 147 159 175 198 194 207 190 198 202 197 209 187 185 230 206 207 209 218 206 216 228 239 224 268 244 299 298 284 290 333 338 317 368 368 445 537 619 1385 379 141 157 170 174 183 201 196 200 183 200 202 213 212 213
wbuffix_drop 16k 32k r2 | 5.875 | 2177 2174 2169 2167 2174 1377 138 146 162 175 194 196 197 195 200 206 206 196 215 192 199 208 190 214 237 196 251 241 266 260 239 250 240 329 284 269 288 347 316 341 380 448 480 585 1184 669 142 155 170 178 199 197 188 196 196 203 202 193 209 214
wbuffix_drop 16k 32k r3 | 5.875 | 2177 2175 2169 2167 2173 1377 138 149 159 175 198 194 202 195 197 214 202 200 215 220 224 234 205 204 242 261 260 259 220 306 259 241 225 235 269 244 296 306 333 348 429 454 599 724 1412 135 146 162 165 178 189 204 203 199 199 208 193 204 194 214
wbuffix_drop 32k 4k r1 | 6.094 | 261 260 259 261 260 235 100 89 86 85 80 77 81 69 70 67 64 57 58 56 54 53 51 49 48 48 46 44 44 42 43 43 40 39 39 39 37 37 37 35 35 36 34 34 35 34 34 33 34 34 32 32 31 32 30 32 30 29 33 31
wbuffix_drop 32k 4k r2 | 6.094 | 261 260 259 261 260 235 100 90 88 84 82 80 81 68 70 64 63 57 55 59 51 55 51 48 48 48 44 45 43 44 42 44 40 40 39 38 41 37 36 34 35 36 34 35 35 33 35 32 33 33 30 31 31 32 31 30 31 30 29 29
wbuffix_drop 32k 4k r3 | 6.094 | 261 260 259 261 260 235 100 89 87 85 80 80 81 70 69 65 60 59 55 59 55 52 53 50 46 47 49 47 46 44 43 41 40 39 40 38 37 37 36 35 34 36 36 35 34 35 33 35 32 32 31 32 31 30 32 31 30 32 30 29
wbuffix_drop 32k 16k r1 | 6.090 | 1041 1042 1040 1042 1045 952 363 313 303 272 247 234 212 210 184 185 167 156 159 150 145 143 130 128 124 113 122 123 115 109 108 105 108 104 98 95 92 90 87 85 84 82 84 80 85 86 80 81 87 79 82 83 79 81 80 80 81 81 81 79
wbuffix_drop 32k 16k r2 | 6.096 | 1041 1042 1040 1042 1045 952 363 313 306 273 247 224 218 211 185 187 168 158 156 149 140 139 131 124 124 121 119 116 113 115 107 114 102 102 100 95 93 92 88 83 84 81 81 81 83 83 85 87 80 83 85 80 80 79 79 84 84 81 81 81
wbuffix_drop 32k 16k r3 | 6.090 | 1041 1042 1040 1042 1045 952 363 313 300 274 247 232 220 204 183 184 171 157 158 146 145 142 128 124 121 118 120 116 120 106 106 103 99 99 96 94 97 87 86 88 82 86 80 77 86 84 83 80 87 78 83 87 83 87 79 87 89 83 79 79
wbuffix_drop 32k 32k r1 | 6.122 | 2085 2079 2068 2079 2082 1805 138 143 149 154 162 174 168 176 186 177 175 181 202 193 191 199 192 199 198 197 215 213 218 210 205 219 245 218 233 249 254 257 248 265 280 294 324 361 368 434 480 560 1180 492 144 141 156 163 165 169 177 172 176 190
wbuffix_drop 32k 32k r2 | 6.127 | 2084 2079 2068 2079 2082 1804 138 143 145 155 164 173 174 186 171 181 173 188 187 187 196 211 197 198 199 191 215 211 218 212 237 230 241 231 226 247 248 259 270 277 292 303 311 348 369 436 497 632 1160 137 140 141 160 162 173 171 189 172 184 171
wbuffix_drop 32k 32k r3 | 6.122 | 2086 2079 2068 2079 2082 1805 138 143 149 157 162 176 177 178 184 182 172 189 188 183 191 183 197 192 204 200 202 207 219 210 212 228 233 233 222 229 239 271 249 264 293 307 317 334 382 456 439 637 1226 433 145 144 157 159 167 175 188 184 179 182
wbuffix_nodrop 4k 4k r1 | 6.277 | 2011 2012 1999 2009 2006 2057 208 130 151 159 173 173 170 194 170 152 179 172 167 165 171 176 188 182 226 196 221 173 210 190 175 199 213 194 207 206 209 215 244 221 231 246 256 266 292 305 346 358 431 483 571 1401 137 132 134 158 152 169 174 173
wbuffix_nodrop 4k 4k r2 | 6.342 | 1991 1987 1988 1985 1984 2020 335 128 147 159 166 159 161 187 178 166 174 178 169 178 176 185 182 205 174 179 194 197 183 186 212 216 193 212 210 235 214 218 234 222 230 263 259 272 282 312 326 353 403 505 661 1339 121 131 136 149 173 166 185 186
wbuffix_nodrop 4k 4k r3 | 6.333 | 1992 1988 1992 1986 1988 2028 321 130 144 152 168 166 169 209 168 181 164 179 181 169 204 184 174 181 223 222 208 215 199 198 205 188 194 207 201 233 237 218 229 250 239 256 272 283 310 328 375 419 459 476 787 896 129 137 155 179 164 199 181 184
wbuffix_nodrop 4k 16k r1 | 5.696 | 2234 2233 2233 2226 2233 1098 128 145 164 185 212 231 221 204 215 228 234 238 239 251 254 260 277 278 292 300 324 325 348 372 395 420 462 516 577 694 921 1532 124 140 158 178 200 226 246 201 211 223 232 242 243 244 253 261 270 284 288 301 310 330
wbuffix_nodrop 4k 16k r2 | 5.693 | 2234 2233 2233 2233 2233 1090 130 146 164 188 209 232 222 204 216 232 233 240 240 253 257 261 277 279 296 304 319 333 350 371 395 425 466 512 585 706 945 1454 127 141 159 179 202 226 239 201 215 223 232 237 247 244 248 263 270 283 288 303 311 328
wbuffix_nodrop 4k 16k r3 | 5.693 | 2234 2233 2233 2233 2233 1090 130 146 163 187 211 232 222 204 216 228 237 240 241 252 255 262 277 280 296 302 319 334 348 370 391 420 471 508 584 697 938 1481 127 141 157 176 205 226 240 200 211 227 232 236 242 247 247 260 274 278 294 301 310 329
wbuffix_nodrop 4k 32k r1 | 5.693 | 2234 2233 2233 2233 2233 1098 137 151 166 188 214 231 222 208 215 227 234 239 244 254 256 264 279 285 297 303 322 329 357 374 398 432 471 525 601 724 1023 1291 130 147 164 184 205 233 227 204 216 226 234 245 243 247 256 268 271 284 291 309 312 331
wbuffix_nodrop 4k 32k r2 | 5.693 | 2233 2233 2233 2233 2233 1098 137 151 169 188 211 231 222 208 215 225 236 238 244 250 260 264 280 283 296 303 322 331 357 371 400 425 474 514 604 726 1008 1312 130 147 164 184 205 228 232 204 216 228 233 243 244 248 256 266 271 276 295 304 315 332
wbuffix_nodrop 4k 32k r3 | 5.693 | 2234 2233 2233 2233 2233 1098 137 150 166 188 215 231 222 207 215 225 234 241 244 249 260 265 275 286 293 307 322 330 356 372 397 427 473 518 600 723 1008 1318 132 144 162 183 204 230 229 204 216 226 234 241 244 248 259 264 271 284 290 307 310 330
wbuffix_nodrop 16k 4k r1 | 5.915 | 536 533 538 536 535 430 179 162 175 166 152 144 139 131 119 123 111 118 104 101 103 97 91 92 95 88 80 86 79 81 76 72 75 69 76 68 66 67 65 64 66 61 60 62 60 60 57 59 57 58 57 58 56 61 56 59 56 53 57 51
wbuffix_nodrop 16k 4k r2 | 5.911 | 536 534 538 536 535 430 176 165 176 165 153 140 137 132 121 121 111 117 106 101 104 97 95 90 93 93 82 81 84 77 79 73 70 70 71 70 67 66 65 63 64 67 61 64 61 61 61 61 61 57 58 53 59 55 55 52 55 53 56 52
wbuffix_nodrop 16k 4k r3 | 5.914 | 536 533 538 536 535 430 176 163 176 163 152 145 141 133 118 126 105 110 104 102 100 97 93 87 93 93 83 83 80 82 76 73 73 75 68 71 66 65 72 65 66 63 62 63 58 61 57 58 57 59 62 55 54 56 53 59 56 54 57 53
wbuffix_nodrop 16k 16k r1 | 5.921 | 2141 2141 2143 2149 2140 1512 136 136 147 157 171 166 169 175 163 160 174 177 176 194 185 191 176 198 197 196 176 186 196 207 207 203 212 218 219 218 223 236 242 244 252 268 282 323 315 370 379 436 524 698 1201 130 139 147 155 172 178 174 183 170
wbuffix_nodrop 16k 16k r2 | 5.921 | 2141 2141 2143 2149 2140 1512 136 136 147 161 170 162 179 185 178 178 169 179 183 203 184 179 189 190 206 191 191 186 195 194 223 201 226 209 215 236 242 226 240 245 254 265 297 300 323 362 390 460 573 874 889 130 142 152 161 169 177 179 183 176
wbuffix_nodrop 16k 16k r3 | 5.921 | 2140 2141 2142 2149 2140 1512 136 136 149 158 176 173 186 178 192 168 173 182 177 185 187 196 183 189 193 207 209 205 201 204 209 203 212 219 234 231 224 242 254 259 257 270 288 311 347 387 413 532 675 1344 131 135 148 167 160 168 177 187 177 180
wbuffix_nodrop 16k 32k r1 | 5.843 | 2176 2175 2169 2167 2173 1377 138 148 159 175 198 194 202 195 198 214 202 200 220 215 219 227 212 219 230 234 256 213 232 232 261 244 254 232 279 264 293 300 328 399 417 426 491 598 1273 541 141 154 170 179 199 205 184 193 187 186 223 213 214 193
wbuffix_nodrop 16k 32k r2 | 5.846 | 2176 2175 2169 2167 2169 1382 138 146 162 175 194 198 207 190 194 212 200 214 191 209 223 212 194 225 224 192 234 239 249 234 254 269 273 290 264 285 315 311 346 408 399 533 740 875 1078 135 150 164 172 186 189 207 191 198 189 202 219 199 213 220
wbuffix_nodrop 16k 32k r3 | 5.843 | 2176 2175 2169 2167 2173 1379 139 146 159 175 198 194 207 190 198 210 197 205 181 205 220 217 189 235 213 240 240 222 223 247 244 261 287 230 299 296 288 348 349 389 378 471 531 776 1451 135 143 158 176 189 192 209 196 201 194 197 205 206 225 207
wbuffix_nodrop 32k 4k r1 | 6.061 | 261 260 259 261 260 235 101 89 88 85 81 78 81 71 69 64 62 59 55 58 53 53 49 51 47 47 46 45 43 44 41 40 43 40 37 37 39 38 36 36 37 36 36 34 34 35 33 32 34 33 32 30 32 30 31 34 31 32 30 29
wbuffix_nodrop 32k 4k r2 | 6.061 | 261 260 259 261 260 235 101 89 88 84 82 80 80 70 70 64 62 58 55 59 51 53 50 52 49 50 46 45 42 44 41 43 42 39 38 37 38 38 36 36 36 35 35 34 34 35 34 32 33 30 32 32 32 31 30 30 30 29 31 29
wbuffix_nodrop 32k 4k r3 | 6.061 | 261 260 259 261 260 235 101 89 86 84 81 80 82 70 70 64 63 57 57 57 53 52 51 52 47 48 47 45 44 43 42 41 40 39 39 37 38 37 37 35 34 35 34 35 33 36 33 34 34 33 33 31 30 32 32 33 32 31 30 31
wbuffix_nodrop 32k 16k r1 | 6.064 | 1041 1042 1040 1042 1045 952 363 313 302 273 240 234 216 207 185 189 166 157 157 148 139 131 126 138 128 115 119 115 109 111 105 104 98 103 102 95 95 90 92 88 82 83 82 80 83 82 84 85 82 82 83 82 78 82 84 84 80 82 83 78
wbuffix_nodrop 32k 16k r2 | 6.064 | 1041 1042 1040 1042 1044 952 363 313 301 274 243 230 214 216 191 182 170 157 156 149 138 142 139 132 116 125 127 119 120 108 105 102 99 103 99 92 92 96 86 83 84 80 83 81 80 84 84 81 86 84 85 82 84 82 80 82 82 81 83 86
wbuffix_nodrop 32k 16k r3 | 6.064 | 1041 1042 1040 1042 1045 952 363 314 302 272 243 228 219 211 181 184 168 157 159 146 146 140 131 125 122 122 124 120 113 112 113 104 106 99 101 96 97 89 90 87 83 79 83 82 82 89 78 81 84 84 84 80 86 80 81 82 81 81 79 79
wbuffix_nodrop 32k 32k r1 | 6.096 | 2084 2079 2068 2079 2082 1805 138 143 145 155 165 172 174 193 179 169 170 181 187 188 187 192 200 196 199 194 207 216 220 224 222 221 240 235 230 247 242 248 252 270 280 293 318 359 389 439 503 620 1426 184 141 148 154 163 172 176 174 180 177 183
wbuffix_nodrop 32k 32k r2 | 6.096 | 2084 2079 2068 2079 2082 1805 138 143 149 154 166 176 177 176 185 182 172 190 185 185 192 188 198 194 198 196 207 215 224 206 221 225 243 230 239 247 278 255 266 270 271 298 321 357 385 420 485 681 1398 131 136 149 162 166 176 179 182 174 181 174
wbuffix_nodrop 32k 32k r3 | 6.096 | 2084 2079 2068 2079 2082 1804 138 143 149 157 163 176 177 178 184 180 173 187 186 183 194 191 185 194 196 198 206 207 217 218 221 220 218 235 234 245 245 263 274 287 303 290 316 339 402 422 486 655 1439 140 139 150 159 163 168 182 186 181 173 170
```

### 11.1.8 실험 전후 환경 차이 (env_before vs env_after_* 의 마지막 스냅샷; 날짜·부하·여유 메모리 줄 제외)
- env_after_wbuffix:
  - 08_nvmevirt_git.txt:
    `-1d6cd036893f06bfe8aa8f6bb4327239bc4b720f`
    `+a93ef76bbf990eafd1d0a5a9484a27a1b709ed9d`
    `-1d6cd03 exp: final 3x3 design with OS page-cache comparison`
    `+a93ef76 exp: final 3x3 design with OS page-cache comparison`
    `+ M EXPERIMENT_LOG_FOR_CLAUDE.md`
    `+ M exp/analyze.py`
    `+ M exp/report/make_md_results.py`
    `+ M exp/report/make_report.py`
    `+?? exp/report/make_handoff.sh`
  - 09_block.txt:
    `-/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        121.44  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`
    `+/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        121.47  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`

### 11.1.9 run_all 로그 끝 40 줄 (원본 로그, 시각은 KST 로 변환)
```
    -> 424.8 MiB/s, 13595 IOPS, clat mean 2351.9 us
[2026-10-08 16:42:50 KST] === [37/54] variant=wbuffix cache=nodrop map=4k bs=4k rep=3 ===
    -> 417.7 MiB/s, 106942 IOPS, clat mean 298.2 us
[2026-10-08 16:44:00 KST] === [38/54] variant=wbuffix cache=drop map=4k bs=4k rep=3 ===
    -> 418.2 MiB/s, 107065 IOPS, clat mean 297.9 us
[2026-10-08 16:45:11 KST] === [39/54] variant=wbuffix cache=nodrop map=4k bs=16k rep=3 ===
    -> 480.9 MiB/s, 30775 IOPS, clat mean 1038.4 us
[2026-10-08 16:46:21 KST] === [40/54] variant=wbuffix cache=drop map=4k bs=16k rep=3 ===
    -> 480.9 MiB/s, 30776 IOPS, clat mean 1038.3 us
[2026-10-08 16:47:32 KST] === [41/54] variant=wbuffix cache=nodrop map=4k bs=32k rep=3 ===
    -> 482.1 MiB/s, 15427 IOPS, clat mean 2072.3 us
[2026-10-08 16:48:42 KST] === [42/54] variant=wbuffix cache=drop map=4k bs=32k rep=3 ===
    -> 482.2 MiB/s, 15430 IOPS, clat mean 2072.0 us
[2026-10-08 16:49:52 KST] === [43/54] variant=wbuffix cache=nodrop map=16k bs=4k rep=3 ===
    -> 129.7 MiB/s, 33203 IOPS, clat mean 962.7 us
[2026-10-08 16:51:03 KST] === [44/54] variant=wbuffix cache=drop map=16k bs=4k rep=3 ===
    -> 129.6 MiB/s, 33174 IOPS, clat mean 963.5 us
[2026-10-08 16:52:13 KST] === [45/54] variant=wbuffix cache=nodrop map=16k bs=16k rep=3 ===
    -> 421.8 MiB/s, 26992 IOPS, clat mean 1184.1 us
[2026-10-08 16:53:24 KST] === [46/54] variant=wbuffix cache=drop map=16k bs=16k rep=3 ===
    -> 421.2 MiB/s, 26955 IOPS, clat mean 1185.7 us
[2026-10-08 16:54:34 KST] === [47/54] variant=wbuffix cache=nodrop map=16k bs=32k rep=3 ===
    -> 441.9 MiB/s, 14141 IOPS, clat mean 2261.0 us
[2026-10-08 16:55:44 KST] === [48/54] variant=wbuffix cache=drop map=16k bs=32k rep=3 ===
    -> 441.3 MiB/s, 14121 IOPS, clat mean 2264.2 us
[2026-10-08 16:56:55 KST] === [49/54] variant=wbuffix cache=nodrop map=32k bs=4k rep=3 ===
    -> 68.3 MiB/s, 17493 IOPS, clat mean 1828.1 us
[2026-10-08 16:58:05 KST] === [50/54] variant=wbuffix cache=drop map=32k bs=4k rep=3 ===
    -> 68.4 MiB/s, 17498 IOPS, clat mean 1827.6 us
[2026-10-08 16:59:16 KST] === [51/54] variant=wbuffix cache=nodrop map=32k bs=16k rep=3 ===
    -> 219.7 MiB/s, 14060 IOPS, clat mean 2274.4 us
[2026-10-08 17:00:26 KST] === [52/54] variant=wbuffix cache=drop map=32k bs=16k rep=3 ===
    -> 219.4 MiB/s, 14039 IOPS, clat mean 2277.9 us
[2026-10-08 17:01:36 KST] === [53/54] variant=wbuffix cache=nodrop map=32k bs=32k rep=3 ===
    -> 424.6 MiB/s, 13587 IOPS, clat mean 2353.3 us
[2026-10-08 17:02:47 KST] === [54/54] variant=wbuffix cache=drop map=32k bs=32k rep=3 ===
    -> 424.4 MiB/s, 13580 IOPS, clat mean 2354.5 us
environment snapshot -> /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main3x3_20261008/env_after_wbuffix
[2026-10-08 17:03:57 KST] finished: /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main3x3_20261008/wbuffix_nodrop /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main3x3_20261008/wbuffix_drop
54 runs, 0 failed -> /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main3x3_20261008/analysis
```

## 11.2 main_20261008  (묶음 경로 repo/exp/results/main_20261008/)

### 11.2.1 회차 목록
- base: 완료 회차 20 (DONE 있음). run.log 첫 시각 2026-10-08 14:21:02 KST, 마지막 시각 2026-10-08 14:46:57 KST. chmodel 오류 줄 합계 41,107,393. chmodel>0 회차 5. kernel_warn>0 회차 2.
  - FAILED: map32k_bs16k_r1
  - 미완료/없음 88: map4k_bs4k_r2 map4k_bs4k_r3 map4k_bs8k_r2 map4k_bs8k_r3 map4k_bs16k_r2 map4k_bs16k_r3 map4k_bs32k_r2 map4k_bs32k_r3 map4k_bs64k_r2 map4k_bs64k_r3 map4k_bs128k_r2 map4k_bs128k_r3 map8k_bs4k_r2 map8k_bs4k_r3 map8k_bs8k_r2 map8k_bs8k_r3 map8k_bs16k_r2 map8k_bs16k_r3 map8k_bs32k_r2 map8k_bs32k_r3 map8k_bs64k_r2 map8k_bs64k_r3 map8k_bs128k_r2 map8k_bs128k_r3 map16k_bs4k_r2 map16k_bs4k_r3 map16k_bs8k_r2 map16k_bs8k_r3 map16k_bs16k_r2 map16k_bs16k_r3 map16k_bs32k_r2 map16k_bs32k_r3 map16k_bs64k_r2 map16k_bs64k_r3 map16k_bs128k_r2 map16k_bs128k_r3 map32k_bs4k_r2 map32k_bs4k_r3 map32k_bs8k_r2 map32k_bs8k_r3 map32k_bs16k_r1 map32k_bs16k_r2 map32k_bs16k_r3 map32k_bs32k_r1 map32k_bs32k_r2 map32k_bs32k_r3 map32k_bs64k_r1 map32k_bs64k_r2 map32k_bs64k_r3 map32k_bs128k_r1 map32k_bs128k_r2 map32k_bs128k_r3 map64k_bs4k_r1 map64k_bs4k_r2 map64k_bs4k_r3 map64k_bs8k_r1 map64k_bs8k_r2 map64k_bs8k_r3 map64k_bs16k_r1 map64k_bs16k_r2 map64k_bs16k_r3 map64k_bs32k_r1 map64k_bs32k_r2 map64k_bs32k_r3 map64k_bs64k_r1 map64k_bs64k_r2 map64k_bs64k_r3 map64k_bs128k_r1 map64k_bs128k_r2 map64k_bs128k_r3 map128k_bs4k_r1 map128k_bs4k_r2 map128k_bs4k_r3 map128k_bs8k_r1 map128k_bs8k_r2 map128k_bs8k_r3 map128k_bs16k_r1 map128k_bs16k_r2 map128k_bs16k_r3 map128k_bs32k_r1 map128k_bs32k_r2 map128k_bs32k_r3 map128k_bs64k_r1 map128k_bs64k_r2 map128k_bs64k_r3 map128k_bs128k_r1 map128k_bs128k_r2 map128k_bs128k_r3
  - run.log NOTE/WARNING/ERROR 줄 9개 (원본 로그 인용, 시각은 KST 로 변환):
    - `[2026-10-08 14:29:10 KST] NOTE: 8242206 channel-model overflow messages (first 20 in kernel.log)`
    - `[2026-10-08 14:29:10 KST] NOTE: 1 kernel warning line(s) — see /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main_20261008/base/map8k_bs4k_r1/kernel.log`
    - `[2026-10-08 14:36:09 KST] NOTE: 6757590 channel-model overflow messages (first 20 in kernel.log)`
    - `[2026-10-08 14:37:20 KST] NOTE: 9087642 channel-model overflow messages (first 20 in kernel.log)`
    - `[2026-10-08 14:37:20 KST] NOTE: 1 kernel warning line(s) — see /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main_20261008/base/map16k_bs8k_r1/kernel.log`
    - `[2026-10-08 14:43:09 KST] NOTE: 8233550 channel-model overflow messages (first 20 in kernel.log)`
    - `[2026-10-08 14:44:21 KST] NOTE: 8786405 channel-model overflow messages (first 20 in kernel.log)`
    - `[2026-10-08 14:44:21 KST] NOTE: 1 kernel warning line(s) — see /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main_20261008/base/map32k_bs8k_r1/kernel.log`
    - `[2026-10-08 14:46:57 KST] ERROR: fio failed (exit 1) — see /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main_20261008/base/map32k_bs16k_r1`
- wbuffix: 완료 회차 53 (DONE 있음). run.log 첫 시각 2026-10-08 14:49:14 KST, 마지막 시각 2026-10-08 15:51:36 KST. chmodel 오류 줄 합계 0. chmodel>0 회차 0. kernel_warn>0 회차 0.
  - 미완료/없음 55: map4k_bs4k_r3 map4k_bs8k_r3 map4k_bs16k_r3 map4k_bs32k_r3 map4k_bs64k_r3 map4k_bs128k_r3 map8k_bs4k_r3 map8k_bs8k_r3 map8k_bs16k_r3 map8k_bs32k_r3 map8k_bs64k_r3 map8k_bs128k_r3 map16k_bs4k_r3 map16k_bs8k_r3 map16k_bs16k_r3 map16k_bs32k_r3 map16k_bs64k_r3 map16k_bs128k_r2 map16k_bs128k_r3 map32k_bs4k_r2 map32k_bs4k_r3 map32k_bs8k_r2 map32k_bs8k_r3 map32k_bs16k_r2 map32k_bs16k_r3 map32k_bs32k_r2 map32k_bs32k_r3 map32k_bs64k_r2 map32k_bs64k_r3 map32k_bs128k_r2 map32k_bs128k_r3 map64k_bs4k_r2 map64k_bs4k_r3 map64k_bs8k_r2 map64k_bs8k_r3 map64k_bs16k_r2 map64k_bs16k_r3 map64k_bs32k_r2 map64k_bs32k_r3 map64k_bs64k_r2 map64k_bs64k_r3 map64k_bs128k_r2 map64k_bs128k_r3 map128k_bs4k_r2 map128k_bs4k_r3 map128k_bs8k_r2 map128k_bs8k_r3 map128k_bs16k_r2 map128k_bs16k_r3 map128k_bs32k_r2 map128k_bs32k_r3 map128k_bs64k_r2 map128k_bs64k_r3 map128k_bs128k_r2 map128k_bs128k_r3

### 11.2.2 조합별 행렬 (행 = 매핑 단위, 열 = fio bs). 칸 = mean ± std [min..max], n = 그 조합의 완료 회차 수(보통 3)
#### main_20261008 · base · bw_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 418.396 ± 0.000 [418.396..418.396] | 433.590 ± 0.000 [433.590..433.590] | 480.928 ± 0.000 [480.928..480.928] | 482.595 ± 0.000 [482.595..482.595] | 486.360 ± 0.000 [486.360..486.360] | 496.773 ± 0.000 [496.773..496.773] |
| 8K | 266.394 ± 0.000 [266.394..266.394] | 420.125 ± 0.000 [420.125..420.125] | 440.075 ± 0.000 [440.075..440.075] | 482.244 ± 0.000 [482.244..482.244] | 486.371 ± 0.000 [486.371..486.371] | 497.388 ± 0.000 [497.388..497.388] |
| 16K | 167.853 ± 0.000 [167.853..167.853] | 272.789 ± 0.000 [272.789..272.789] | 420.993 ± 0.000 [420.993..420.993] | 443.818 ± 0.000 [443.818..443.818] | 486.388 ± 0.000 [486.388..486.388] | 496.748 ± 0.000 [496.748..496.748] |
| 32K | 92.600 ± 0.000 [92.600..92.600] | 174.002 ± 0.000 [174.002..174.002] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · iops
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 107109.382 ± 0.000 [107109.382..107109.382] | 55499.542 ± 0.000 [55499.542..55499.542] | 30779.394 ± 0.000 [30779.394..30779.394] | 15443.059 ± 0.000 [15443.059..15443.059] | 7781.766 ± 0.000 [7781.766..7781.766] | 3974.191 ± 0.000 [3974.191..3974.191] |
| 8K | 68196.973 ± 0.000 [68196.973..68196.973] | 53776.037 ± 0.000 [53776.037..53776.037] | 28164.831 ± 0.000 [28164.831..28164.831] | 15431.838 ± 0.000 [15431.838..15431.838] | 7781.952 ± 0.000 [7781.952..7781.952] | 3979.103 ± 0.000 [3979.103..3979.103] |
| 16K | 42970.418 ± 0.000 [42970.418..42970.418] | 34917.104 ± 0.000 [34917.104..34917.104] | 26943.601 ± 0.000 [26943.601..26943.601] | 14202.206 ± 0.000 [14202.206..14202.206] | 7782.215 ± 0.000 [7782.215..7782.215] | 3973.991 ± 0.000 [3973.991..3973.991] |
| 32K | 23705.581 ± 0.000 [23705.581..23705.581] | 22272.277 ± 0.000 [22272.277..22272.277] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · clat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 297.725 ± 0.000 [297.725..297.725] | 575.365 ± 0.000 [575.365..575.365] | 1038.183 ± 0.000 [1038.183..1038.183] | 2070.202 ± 0.000 [2070.202..2070.202] | 4109.243 ± 0.000 [4109.243..4109.243] | 8047.197 ± 0.000 [8047.197..8047.197] |
| 8K | 467.307 ± 0.000 [467.307..467.307] | 593.818 ± 0.000 [593.818..593.818] | 1134.696 ± 0.000 [1134.696..1134.696] | 2071.723 ± 0.000 [2071.723..2071.723] | 4109.183 ± 0.000 [4109.183..4109.183] | 8037.268 ± 0.000 [8037.268..8037.268] |
| 16K | 742.770 ± 0.000 [742.770..742.770] | 914.359 ± 0.000 [914.359..914.359] | 1186.169 ± 0.000 [1186.169..1186.169] | 2251.226 ± 0.000 [2251.226..2251.226] | 4109.073 ± 0.000 [4109.073..4109.073] | 8047.680 ± 0.000 [8047.680..8047.680] |
| 32K | 1347.668 ± 0.000 [1347.668..1347.668] | 1434.271 ± 0.000 [1434.271..1434.271] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · clat_p50_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 70.144 ± 0.000 [70.144..70.144] | 120.320 ± 0.000 [120.320..120.320] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] | 897.024 ± 0.000 [897.024..897.024] | 1794.048 ± 0.000 [1794.048..1794.048] |
| 8K | 342.016 ± 0.000 [342.016..342.016] | 132.096 ± 0.000 [132.096..132.096] | 224.256 ± 0.000 [224.256..224.256] | 444.416 ± 0.000 [444.416..444.416] | 897.024 ± 0.000 [897.024..897.024] | 1794.048 ± 0.000 [1794.048..1794.048] |
| 16K | 684.032 ± 0.000 [684.032..684.032] | 692.224 ± 0.000 [692.224..692.224] | 246.784 ± 0.000 [246.784..246.784] | 464.896 ± 0.000 [464.896..464.896] | 897.024 ± 0.000 [897.024..897.024] | 1794.048 ± 0.000 [1794.048..1794.048] |
| 32K | 1236.992 ± 0.000 [1236.992..1236.992] | 1236.992 ± 0.000 [1236.992..1236.992] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · clat_p99_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 13303.808 ± 0.000 [13303.808..13303.808] | 16449.536 ± 0.000 [16449.536..16449.536] | 17694.720 ± 0.000 [17694.720..17694.720] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] | 20578.304 ± 0.000 [20578.304..20578.304] |
| 8K | 2473.984 ± 0.000 [2473.984..2473.984] | 15532.032 ± 0.000 [15532.032..15532.032] | 17432.576 ± 0.000 [17432.576..17432.576] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] | 20316.160 ± 0.000 [20316.160..20316.160] |
| 16K | 2768.896 ± 0.000 [2768.896..2768.896] | 3162.112 ± 0.000 [3162.112..3162.112] | 16908.288 ± 0.000 [16908.288..16908.288] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] | 20316.160 ± 0.000 [20316.160..20316.160] |
| 32K | 3784.704 ± 0.000 [3784.704..3784.704] | 4227.072 ± 0.000 [4227.072..4227.072] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · clat_p999_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 17170.432 ± 0.000 [17170.432..17170.432] | 17956.864 ± 0.000 [17956.864..17956.864] | 18481.152 ± 0.000 [18481.152..18481.152] | 18743.296 ± 0.000 [18743.296..18743.296] | 19529.728 ± 0.000 [19529.728..19529.728] | 38010.880 ± 0.000 [38010.880..38010.880] |
| 8K | 3457.024 ± 0.000 [3457.024..3457.024] | 17432.576 ± 0.000 [17432.576..17432.576] | 18481.152 ± 0.000 [18481.152..18481.152] | 18743.296 ± 0.000 [18743.296..18743.296] | 19529.728 ± 0.000 [19529.728..19529.728] | 38010.880 ± 0.000 [38010.880..38010.880] |
| 16K | 3915.776 ± 0.000 [3915.776..3915.776] | 4358.144 ± 0.000 [4358.144..4358.144] | 17956.864 ± 0.000 [17956.864..17956.864] | 18743.296 ± 0.000 [18743.296..18743.296] | 19529.728 ± 0.000 [19529.728..19529.728] | 38010.880 ± 0.000 [38010.880..38010.880] |
| 32K | 5079.040 ± 0.000 [5079.040..5079.040] | 5472.256 ± 0.000 [5472.256..5472.256] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · lat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 298.571 ± 0.000 [298.571..298.571] | 576.359 ± 0.000 [576.359..576.359] | 1039.409 ± 0.000 [1039.409..1039.409] | 2071.863 ± 0.000 [2071.863..2071.863] | 4111.872 ± 0.000 [4111.872..4111.872] | 8051.637 ± 0.000 [8051.637..8051.637] |
| 8K | 469.000 ± 0.000 [469.000..469.000] | 594.826 ± 0.000 [594.826..594.826] | 1135.912 ± 0.000 [1135.912..1135.912] | 2073.364 ± 0.000 [2073.364..2073.364] | 4111.809 ± 0.000 [4111.809..4111.809] | 8041.648 ± 0.000 [8041.648..8041.648] |
| 16K | 744.459 ± 0.000 [744.459..744.459] | 916.214 ± 0.000 [916.214..916.214] | 1187.410 ± 0.000 [1187.410..1187.410] | 2252.891 ± 0.000 [2252.891..2252.891] | 4111.606 ± 0.000 [4111.606..4111.606] | 8052.035 ± 0.000 [8052.035..8052.035] |
| 32K | 1349.624 ± 0.000 [1349.624..1349.624] | 1436.508 ± 0.000 [1436.508..1436.508] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · slat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 0.846 ± 0.000 [0.846..0.846] | 0.994 ± 0.000 [0.994..0.994] | 1.226 ± 0.000 [1.226..1.226] | 1.661 ± 0.000 [1.661..1.661] | 2.629 ± 0.000 [2.629..2.629] | 4.440 ± 0.000 [4.440..4.440] |
| 8K | 1.693 ± 0.000 [1.693..1.693] | 1.008 ± 0.000 [1.008..1.008] | 1.215 ± 0.000 [1.215..1.215] | 1.641 ± 0.000 [1.641..1.641] | 2.626 ± 0.000 [2.626..2.626] | 4.380 ± 0.000 [4.380..4.380] |
| 16K | 1.689 ± 0.000 [1.689..1.689] | 1.855 ± 0.000 [1.855..1.855] | 1.241 ± 0.000 [1.241..1.241] | 1.664 ± 0.000 [1.664..1.664] | 2.533 ± 0.000 [2.533..2.533] | 4.355 ± 0.000 [4.355..4.355] |
| 32K | 1.955 ± 0.000 [1.955..1.955] | 2.237 ± 0.000 [2.237..2.237] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · bw_first10s_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 1273.449 ± 0.000 [1273.449..1273.449] | 1285.086 ± 0.000 [1285.086..1285.086] | 1288.664 ± 0.000 [1288.664..1288.664] | 1290.947 ± 0.000 [1290.947..1290.947] | 1293.673 ± 0.000 [1293.673..1293.673] | 1299.198 ± 0.000 [1299.198..1299.198] |
| 8K | 814.963 ± 0.000 [814.963..814.963] | 1282.384 ± 0.000 [1282.384..1282.384] | 1285.951 ± 0.000 [1285.951..1285.951] | 1290.968 ± 0.000 [1290.968..1290.968] | 1293.673 ± 0.000 [1293.673..1293.673] | 1299.042 ± 0.000 [1299.042..1299.042] |
| 16K | 430.340 ± 0.000 [430.340..430.340] | 822.686 ± 0.000 [822.686..822.686] | 1278.891 ± 0.000 [1278.891..1278.891] | 1286.222 ± 0.000 [1286.222..1286.222] | 1293.667 ± 0.000 [1293.667..1293.667] | 1299.041 ± 0.000 [1299.041..1299.041] |
| 32K | 219.732 ± 0.000 [219.732..219.732] | 436.112 ± 0.000 [436.112..436.112] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · bw_last20s_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 320.740 ± 0.000 [320.740..320.740] | 321.295 ± 0.000 [321.295..321.295] | 244.569 ± 0.000 [244.569..244.569] | 243.187 ± 0.000 [243.187..243.187] | 254.762 ± 0.000 [254.762..254.762] | 275.073 ± 0.000 [275.073..275.073] |
| 8K | 131.900 ± 0.000 [131.900..131.900] | 323.431 ± 0.000 [323.431..323.431] | 320.270 ± 0.000 [320.270..320.270] | 246.913 ± 0.000 [246.913..246.913] | 254.503 ± 0.000 [254.503..254.503] | 276.863 ± 0.000 [276.863..276.863] |
| 16K | 86.197 ± 0.000 [86.197..86.197] | 133.554 ± 0.000 [133.554..133.554] | 322.791 ± 0.000 [322.791..322.791] | 318.064 ± 0.000 [318.064..318.064] | 254.826 ± 0.000 [254.826..254.826] | 275.170 ± 0.000 [275.170..275.170] |
| 32K | 49.795 ± 0.000 [49.795..49.795] | 85.395 ± 0.000 [85.395..85.395] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · gc_onset_s
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 6.302 ± 0.000 [6.302..6.302] | 5.745 ± 0.000 [5.745..5.745] | 5.697 ± 0.000 [5.697..5.697] | 5.696 ± 0.000 [5.696..5.696] | 5.698 ± 0.000 [5.698..5.698] | 5.699 ± 0.000 [5.699..5.699] |
| 8K | 5.685 ± 0.000 [5.685..5.685] | 5.821 ± 0.000 [5.821..5.821] | 5.782 ± 0.000 [5.782..5.782] | 5.696 ± 0.000 [5.696..5.696] | 5.698 ± 0.000 [5.698..5.698] | 5.698 ± 0.000 [5.698..5.698] |
| 16K | 5.668 ± 0.000 [5.668..5.668] | 5.666 ± 0.000 [5.666..5.666] | 5.924 ± 0.000 [5.924..5.924] | 5.846 ± 0.000 [5.846..5.846] | 5.690 ± 0.000 [5.690..5.690] | 5.697 ± 0.000 [5.697..5.697] |
| 32K | 5.636 ± 0.000 [5.636..5.636] | 5.639 ± 0.000 [5.639..5.639] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · gc_onset_last_part_s
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 6.323 ± 0.000 [6.323..6.323] | 5.764 ± 0.000 [5.764..5.764] | 5.697 ± 0.000 [5.697..5.697] | 5.697 ± 0.000 [5.697..5.697] | 5.698 ± 0.000 [5.698..5.698] | 5.699 ± 0.000 [5.699..5.699] |
| 8K | 5.691 ± 0.000 [5.691..5.691] | 5.862 ± 0.000 [5.862..5.862] | 5.783 ± 0.000 [5.783..5.783] | 5.696 ± 0.000 [5.696..5.696] | 5.699 ± 0.000 [5.699..5.699] | 5.698 ± 0.000 [5.698..5.698] |
| 16K | 5.684 ± 0.000 [5.684..5.684] | 5.697 ± 0.000 [5.697..5.697] | 5.946 ± 0.000 [5.946..5.946] | 5.868 ± 0.000 [5.868..5.868] | 5.690 ± 0.000 [5.690..5.690] | 5.697 ± 0.000 [5.697..5.697] |
| 32K | 5.682 ± 0.000 [5.682..5.682] | 5.673 ± 0.000 [5.673..5.673] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · bw_pre_gc_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 2008.176 ± 0.000 [2008.176..2008.176] | 2211.020 ± 0.000 [2211.020..2211.020] | 2217.722 ± 0.000 [2217.722..2217.722] | 2217.767 ± 0.000 [2217.767..2217.767] | 2217.883 ± 0.000 [2217.883..2217.883] | 2218.338 ± 0.000 [2218.338..2218.338] |
| 8K | 1115.468 ± 0.000 [1115.468..1115.468] | 2180.882 ± 0.000 [2180.882..2180.882] | 2198.648 ± 0.000 [2198.648..2198.648] | 2217.773 ± 0.000 [2217.773..2217.773] | 2217.882 ± 0.000 [2217.882..2217.882] | 2217.909 ± 0.000 [2217.909..2217.909] |
| 16K | 559.153 ± 0.000 [559.153..559.153] | 1117.982 ± 0.000 [1117.982..1117.982] | 2143.227 ± 0.000 [2143.227..2143.227] | 2173.074 ± 0.000 [2173.074..2173.074] | 2217.872 ± 0.000 [2217.872..2217.872] | 2217.932 ± 0.000 [2217.932..2217.932] |
| 32K | 280.505 ± 0.000 [280.505..280.505] | 561.263 ± 0.000 [561.263..561.263] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · bw_post_gc_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 241.841 ± 0.000 [241.841..241.841] | 254.313 ± 0.000 [254.313..254.313] | 305.714 ± 0.000 [305.714..305.714] | 307.251 ± 0.000 [307.251..307.251] | 311.737 ± 0.000 [311.737..311.737] | 323.185 ± 0.000 [323.185..323.185] |
| 8K | 181.225 ± 0.000 [181.225..181.225] | 243.286 ± 0.000 [243.286..243.286] | 263.453 ± 0.000 [263.453..263.453] | 307.144 ± 0.000 [307.144..307.144] | 311.706 ± 0.000 [311.706..311.706] | 323.794 ± 0.000 [323.794..323.794] |
| 16K | 128.885 ± 0.000 [128.885..128.885] | 188.075 ± 0.000 [188.075..188.075] | 247.764 ± 0.000 [247.764..247.764] | 269.453 ± 0.000 [269.453..269.453] | 311.848 ± 0.000 [311.848..311.848] | 323.166 ± 0.000 [323.166..323.166] |
| 32K | 73.927 ± 0.000 [73.927..73.927] | 135.522 ± 0.000 [135.522..135.522] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · gc_cnt
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 8345.000 ± 0.000 [8345..8345] | 9182.000 ± 0.000 [9182..9182] | 11272.000 ± 0.000 [11272..11272] | 11280.000 ± 0.000 [11280..11280] | 11344.000 ± 0.000 [11344..11344] | 11480.000 ± 0.000 [11480..11480] |
| 8K | 14444.000 ± 0.000 [14444..14444] | 8386.000 ± 0.000 [8386..8386] | 9460.000 ± 0.000 [9460..9460] | 11276.000 ± 0.000 [11276..11276] | 11344.000 ± 0.000 [11344..11344] | 11480.000 ± 0.000 [11480..11480] |
| 16K | 14419.000 ± 0.000 [14419..14419] | 15155.000 ± 0.000 [15155..15155] | 8352.000 ± 0.000 [8352..8352] | 9576.000 ± 0.000 [9576..9576] | 11348.000 ± 0.000 [11348..11348] | 11480.000 ± 0.000 [11480..11480] |
| 32K | 15473.000 ± 0.000 [15473..15473] | 15691.000 ± 0.000 [15691..15691] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · ftl_host_pgs
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 6426670 ± 0.000 [6426670..6426670] | 6660944 ± 0.000 [6660944..6660944] | 7387424 ± 0.000 [7387424..7387424] | 7412792 ± 0.000 [7412792..7412792] | 7471616 ± 0.000 [7471616..7471616] | 7632608 ± 0.000 [7632608..7632608] |
| 8K | 4091942 ± 0.000 [4091942..4091942] | 3226616 ± 0.000 [3226616..3226616] | 3379836 ± 0.000 [3379836..3379836] | 3703888 ± 0.000 [3703888..3703888] | 3735648 ± 0.000 [3735648..3735648] | 3820448 ± 0.000 [3820448..3820448] |
| 16K | 2578311 ± 0.000 [2578311..2578311] | 2095113 ± 0.000 [2095113..2095113] | 1616643 ± 0.000 [1616643..1616643] | 1704776 ± 0.000 [1704776..1704776] | 1868292 ± 0.000 [1868292..1868292] | 1908056 ± 0.000 [1908056..1908056] |
| 32K | 1422406 ± 0.000 [1422406..1422406] | 1336448 ± 0.000 [1336448..1336448] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · ftl_gc_pgs
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 13784996 ± 0.000 [13784996..13784996] | 15264468 ± 0.000 [15264468..15264468] | 18818284 ± 0.000 [18818284..18818284] | 18808928 ± 0.000 [18808928..18808928] | 18881152 ± 0.000 [18881152..18881152] | 18999456 ± 0.000 [18999456..18999456] |
| 8K | 12260041 ± 0.000 [12260041..12260041] | 6921205 ± 0.000 [6921205..6921205] | 7867608 ± 0.000 [7867608..7867608] | 9402992 ± 0.000 [9402992..9402992] | 9440736 ± 0.000 [9440736..9440736] | 9495600 ± 0.000 [9495600..9495600] |
| 16K | 5585060 ± 0.000 [5585060..5585060] | 6444990 ± 0.000 [6444990..6444990] | 3439890 ± 0.000 [3439890..3439890] | 3978204 ± 0.000 [3978204..3978204] | 4721904 ± 0.000 [4721904..4721904] | 4749968 ± 0.000 [4749968..4749968] |
| 32K | 2929163 ± 0.000 [2929163..2929163] | 3070857 ± 0.000 [3070857..3070857] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · waf_gc
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 3.145 ± 0.000 [3.145..3.145] | 3.292 ± 0.000 [3.292..3.292] | 3.547 ± 0.000 [3.547..3.547] | 3.537 ± 0.000 [3.537..3.537] | 3.527 ± 0.000 [3.527..3.527] | 3.489 ± 0.000 [3.489..3.489] |
| 8K | 3.996 ± 0.000 [3.996..3.996] | 3.145 ± 0.000 [3.145..3.145] | 3.328 ± 0.000 [3.328..3.328] | 3.539 ± 0.000 [3.539..3.539] | 3.527 ± 0.000 [3.527..3.527] | 3.485 ± 0.000 [3.485..3.485] |
| 16K | 3.166 ± 0.000 [3.166..3.166] | 4.076 ± 0.000 [4.076..4.076] | 3.128 ± 0.000 [3.128..3.128] | 3.334 ± 0.000 [3.334..3.334] | 3.527 ± 0.000 [3.527..3.527] | 3.489 ± 0.000 [3.489..3.489] |
| 32K | 3.059 ± 0.000 [3.059..3.059] | 3.298 ± 0.000 [3.298..3.298] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · waf_total
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 3.145 ± 0.000 [3.145..3.145] | 3.292 ± 0.000 [3.292..3.292] | 3.547 ± 0.000 [3.547..3.547] | 3.537 ± 0.000 [3.537..3.537] | 3.527 ± 0.000 [3.527..3.527] | 3.489 ± 0.000 [3.489..3.489] |
| 8K | 7.992 ± 0.000 [7.992..7.992] | 3.145 ± 0.000 [3.145..3.145] | 3.328 ± 0.000 [3.328..3.328] | 3.539 ± 0.000 [3.539..3.539] | 3.527 ± 0.000 [3.527..3.527] | 3.485 ± 0.000 [3.485..3.485] |
| 16K | 12.665 ± 0.000 [12.665..12.665] | 8.152 ± 0.000 [8.152..8.152] | 3.128 ± 0.000 [3.128..3.128] | 3.334 ± 0.000 [3.334..3.334] | 3.527 ± 0.000 [3.527..3.527] | 3.489 ± 0.000 [3.489..3.489] |
| 32K | 24.474 ± 0.000 [24.474..24.474] | 13.191 ± 0.000 [13.191..13.191] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · written_GiB
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 24.516 ± 0.000 [24.516..24.516] | 25.409 ± 0.000 [25.409..25.409] | 28.181 ± 0.000 [28.181..28.181] | 28.278 ± 0.000 [28.278..28.278] | 28.502 ± 0.000 [28.502..28.502] | 29.116 ± 0.000 [29.116..29.116] |
| 8K | 15.610 ± 0.000 [15.610..15.610] | 24.617 ± 0.000 [24.617..24.617] | 25.786 ± 0.000 [25.786..25.786] | 28.258 ± 0.000 [28.258..28.258] | 28.501 ± 0.000 [28.501..28.501] | 29.148 ± 0.000 [29.148..29.148] |
| 16K | 9.835 ± 0.000 [9.835..9.835] | 15.985 ± 0.000 [15.985..15.985] | 24.668 ± 0.000 [24.668..24.668] | 26.013 ± 0.000 [26.013..26.013] | 28.508 ± 0.000 [28.508..28.508] | 29.115 ± 0.000 [29.115..29.115] |
| 32K | 5.426 ± 0.000 [5.426..5.426] | 10.196 ± 0.000 [10.196..10.196] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · fill_ratio
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 2.186 ± 0.000 [2.186..2.186] | 2.266 ± 0.000 [2.266..2.266] | 2.513 ± 0.000 [2.513..2.513] | 2.522 ± 0.000 [2.522..2.522] | 2.542 ± 0.000 [2.542..2.542] | 2.596 ± 0.000 [2.596..2.596] |
| 8K | 1.392 ± 0.000 [1.392..1.392] | 2.195 ± 0.000 [2.195..2.195] | 2.299 ± 0.000 [2.299..2.299] | 2.520 ± 0.000 [2.520..2.520] | 2.542 ± 0.000 [2.542..2.542] | 2.599 ± 0.000 [2.599..2.599] |
| 16K | 0.877 ± 0.000 [0.877..0.877] | 1.425 ± 0.000 [1.425..1.425] | 2.200 ± 0.000 [2.200..2.200] | 2.320 ± 0.000 [2.320..2.320] | 2.542 ± 0.000 [2.542..2.542] | 2.596 ± 0.000 [2.596..2.596] |
| 32K | 0.484 ± 0.000 [0.484..0.484] | 0.909 ± 0.000 [0.909..0.909] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · chmodel_msgs
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 8K | 8242206 ± 0.000 [8242206..8242206] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 6757590 ± 0.000 [6757590..6757590] | 9087642 ± 0.000 [9087642..9087642] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 8233550 ± 0.000 [8233550..8233550] | 8786405 ± 0.000 [8786405..8786405] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · base · kernel_warn
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 8K | 1.000 ± 0.000 [1..1] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 1.000 ± 0.000 [1..1] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

#### main_20261008 · wbuffix · bw_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 418.567 ± 1.318 [417.635..419.499] | 438.651 ± 0.917 [438.003..439.300] | 480.902 ± 0.012 [480.894..480.911] | 482.331 ± 0.070 [482.281..482.380] | 486.268 ± 0.001 [486.267..486.269] | 496.842 ± 0.014 [496.832..496.852] |
| 8K | 216.667 ± 0.079 [216.611..216.723] | 418.468 ± 2.244 [416.882..420.055] | 437.914 ± 1.612 [436.773..439.054] | 482.307 ± 0.072 [482.256..482.357] | 486.373 ± 0.013 [486.363..486.382] | 496.721 ± 0.032 [496.698..496.743] |
| 16K | 129.806 ± 0.169 [129.687..129.926] | 217.784 ± 0.304 [217.569..217.999] | 420.513 ± 0.291 [420.308..420.719] | 442.190 ± 3.815 [439.492..444.888] | 486.312 ± 0.095 [486.245..486.380] | 496.938 ± 0.000 [496.938..496.938] |
| 32K | 68.268 ± 0.000 [68.268..68.268] | 131.701 ± 0.000 [131.701..131.701] | 219.313 ± 0.000 [219.313..219.313] | 424.493 ± 0.000 [424.493..424.493] | 446.665 ± 0.000 [446.665..446.665] | 496.671 ± 0.000 [496.671..496.671] |
| 64K | 47.054 ± 0.000 [47.054..47.054] | 93.271 ± 0.000 [93.271..93.271] | 175.157 ± 0.000 [175.157..175.157] | 285.618 ± 0.000 [285.618..285.618] | 645.083 ± 0.000 [645.083..645.083] | 665.964 ± 0.000 [665.964..665.964] |
| 128K | 28.134 ± 0.000 [28.134..28.134] | 56.112 ± 0.000 [56.112..56.112] | 110.900 ± 0.000 [110.900..110.900] | 204.969 ± 0.000 [204.969..204.969] | 340.655 ± 0.000 [340.655..340.655] | 837.771 ± 0.000 [837.771..837.771] |

#### main_20261008 · wbuffix · iops
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 107153.202 ± 337.477 [106914.570..107391.835] | 56147.404 ± 117.363 [56064.416..56230.392] | 30777.765 ± 0.780 [30777.213..30778.317] | 15434.597 ± 2.233 [15433.018..15436.176] | 7780.292 ± 0.026 [7780.274..7780.311] | 3974.738 ± 0.114 [3974.658..3974.819] |
| 8K | 55466.935 ± 20.092 [55452.728..55481.142] | 53563.986 ± 287.134 [53360.952..53767.021] | 28026.503 ± 103.184 [27953.540..28099.465] | 15433.837 ± 2.302 [15432.209..15435.465] | 7781.970 ± 0.209 [7781.822..7782.118] | 3973.771 ± 0.255 [3973.591..3973.951] |
| 16K | 33230.519 ± 43.171 [33199.993..33261.046] | 27876.480 ± 38.904 [27848.970..27903.989] | 26912.872 ± 18.572 [26899.740..26926.005] | 14150.089 ± 122.098 [14063.753..14236.425] | 7781.005 ± 1.522 [7779.929..7782.081] | 3975.507 ± 0.000 [3975.507..3975.507] |
| 32K | 17476.663 ± 0.000 [17476.663..17476.663] | 16857.783 ± 0.000 [16857.783..16857.783] | 14036.065 ± 0.000 [14036.065..14036.065] | 13583.792 ± 0.000 [13583.792..13583.792] | 7146.645 ± 0.000 [7146.645..7146.645] | 3973.374 ± 0.000 [3973.374..3973.374] |
| 64K | 12045.792 ± 0.000 [12045.792..12045.792] | 11938.856 ± 0.000 [11938.856..11938.856] | 11210.111 ± 0.000 [11210.111..11210.111] | 9139.800 ± 0.000 [9139.800..9139.800] | 10321.329 ± 0.000 [10321.329..10321.329] | 5327.718 ± 0.000 [5327.718..5327.718] |
| 128K | 7202.426 ± 0.000 [7202.426..7202.426] | 7182.418 ± 0.000 [7182.418..7182.418] | 7097.669 ± 0.000 [7097.669..7097.669] | 6559.014 ± 0.000 [6559.014..6559.014] | 5450.488 ± 0.000 [5450.488..5450.488] | 6702.178 ± 0.000 [6702.178..6702.178] |

#### main_20261008 · wbuffix · clat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 297.612 ± 0.944 [296.945..298.280] | 568.706 ± 1.167 [567.881..569.531] | 1038.234 ± 0.016 [1038.223..1038.246] | 2071.346 ± 0.295 [2071.137..2071.555] | 4110.090 ± 0.023 [4110.074..4110.106] | 8046.083 ± 0.151 [8045.976..8046.190] |
| 8K | 575.863 ± 0.210 [575.715..576.012] | 596.184 ± 3.206 [593.917..598.451] | 1140.297 ± 4.202 [1137.325..1143.268] | 2071.463 ± 0.297 [2071.253..2071.674] | 4109.205 ± 0.151 [4109.098..4109.312] | 8048.018 ± 0.497 [8047.666..8048.370] |
| 16K | 961.880 ± 1.245 [960.999..962.760] | 1146.631 ± 1.594 [1145.504..1147.758] | 1187.524 ± 0.828 [1186.938..1188.110] | 2259.628 ± 19.541 [2245.811..2273.445] | 4109.728 ± 0.808 [4109.157..4110.299] | 8044.570 ± 0.000 [8044.570..8044.570] |
| 32K | 1829.779 ± 0.000 [1829.779..1829.779] | 1896.882 ± 0.000 [1896.882..1896.882] | 2278.255 ± 0.000 [2278.255..2278.255] | 2353.817 ± 0.000 [2353.817..2353.817] | 4474.704 ± 0.000 [4474.704..4474.704] | 8049.000 ± 0.000 [8049.000..8049.000] |
| 64K | 2655.297 ± 0.000 [2655.297..2655.297] | 2678.985 ± 0.000 [2678.985..2678.985] | 2852.966 ± 0.000 [2852.966..2852.966] | 3499.234 ± 0.000 [3499.234..3499.234] | 3097.577 ± 0.000 [3097.577..3097.577] | 6001.689 ± 0.000 [6001.689..6001.689] |
| 128K | 4441.680 ± 0.000 [4441.680..4441.680] | 4453.995 ± 0.000 [4453.995..4453.995] | 4506.955 ± 0.000 [4506.955..4506.955] | 4876.811 ± 0.000 [4876.811..4876.811] | 5868.173 ± 0.000 [5868.173..5868.173] | 4770.301 ± 0.000 [4770.301..4770.301] |

#### main_20261008 · wbuffix · clat_p50_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 69.120 ± 0.000 [69.120..69.120] | 121.344 ± 0.000 [121.344..121.344] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] | 897.024 ± 0.000 [897.024..897.024] | 1794.048 ± 0.000 [1794.048..1794.048] |
| 8K | 151.552 ± 1.448 [150.528..152.576] | 133.120 ± 1.448 [132.096..134.144] | 224.256 ± 0.000 [224.256..224.256] | 444.416 ± 0.000 [444.416..444.416] | 897.024 ± 0.000 [897.024..897.024] | 1794.048 ± 0.000 [1794.048..1794.048] |
| 16K | 254.976 ± 0.000 [254.976..254.976] | 248.832 ± 0.000 [248.832..248.832] | 246.784 ± 0.000 [246.784..246.784] | 464.896 ± 0.000 [464.896..464.896] | 897.024 ± 0.000 [897.024..897.024] | 1794.048 ± 0.000 [1794.048..1794.048] |
| 32K | 569.344 ± 0.000 [569.344..569.344] | 561.152 ± 0.000 [561.152..561.152] | 536.576 ± 0.000 [536.576..536.576] | 528.384 ± 0.000 [528.384..528.384] | 978.944 ± 0.000 [978.944..978.944] | 1794.048 ± 0.000 [1794.048..1794.048] |
| 64K | 937.984 ± 0.000 [937.984..937.984] | 921.600 ± 0.000 [921.600..921.600] | 937.984 ± 0.000 [937.984..937.984] | 978.944 ± 0.000 [978.944..978.944] | 880.640 ± 0.000 [880.640..880.640] | 1597.440 ± 0.000 [1597.440..1597.440] |
| 128K | 2441.216 ± 0.000 [2441.216..2441.216] | 2441.216 ± 0.000 [2441.216..2441.216] | 2506.752 ± 0.000 [2506.752..2506.752] | 2899.968 ± 0.000 [2899.968..2899.968] | 7307.264 ± 0.000 [7307.264..7307.264] | 2244.608 ± 0.000 [2244.608..2244.608] |

#### main_20261008 · wbuffix · clat_p99_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 13500.416 ± 92.682 [13434.880..13565.952] | 16580.608 ± 0.000 [16580.608..16580.608] | 17694.720 ± 0.000 [17694.720..17694.720] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] | 20447.232 ± 185.364 [20316.160..20578.304] |
| 8K | 15007.744 ± 0.000 [15007.744..15007.744] | 15400.960 ± 0.000 [15400.960..15400.960] | 17432.576 ± 0.000 [17432.576..17432.576] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] | 20447.232 ± 185.364 [20316.160..20578.304] |
| 16K | 14090.240 ± 0.000 [14090.240..14090.240] | 16646.144 ± 92.682 [16580.608..16711.680] | 16809.984 ± 139.023 [16711.680..16908.288] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] | 20578.304 ± 0.000 [20578.304..20578.304] |
| 32K | 14483.456 ± 0.000 [14483.456..14483.456] | 15007.744 ± 0.000 [15007.744..15007.744] | 17432.576 ± 0.000 [17432.576..17432.576] | 17694.720 ± 0.000 [17694.720..17694.720] | 19005.440 ± 0.000 [19005.440..19005.440] | 20316.160 ± 0.000 [20316.160..20316.160] |
| 64K | 11337.728 ± 0.000 [11337.728..11337.728] | 11468.800 ± 0.000 [11468.800..11468.800] | 11862.016 ± 0.000 [11862.016..11862.016] | 12124.160 ± 0.000 [12124.160..12124.160] | 11993.088 ± 0.000 [11993.088..11993.088] | 22675.456 ± 0.000 [22675.456..22675.456] |
| 128K | 10158.080 ± 0.000 [10158.080..10158.080] | 10158.080 ± 0.000 [10158.080..10158.080] | 10289.152 ± 0.000 [10289.152..10289.152] | 12648.448 ± 0.000 [12648.448..12648.448] | 16711.680 ± 0.000 [16711.680..16711.680] | 11337.728 ± 0.000 [11337.728..11337.728] |

#### main_20261008 · wbuffix · clat_p999_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 17039.360 ± 185.364 [16908.288..17170.432] | 17825.792 ± 185.364 [17694.720..17956.864] | 18481.152 ± 0.000 [18481.152..18481.152] | 18743.296 ± 0.000 [18743.296..18743.296] | 19529.728 ± 0.000 [19529.728..19529.728] | 38010.880 ± 0.000 [38010.880..38010.880] |
| 8K | 17170.432 ± 0.000 [17170.432..17170.432] | 17432.576 ± 0.000 [17432.576..17432.576] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] | 19529.728 ± 0.000 [19529.728..19529.728] | 38010.880 ± 0.000 [38010.880..38010.880] |
| 16K | 15335.424 ± 92.682 [15269.888..15400.960] | 17694.720 ± 0.000 [17694.720..17694.720] | 17956.864 ± 0.000 [17956.864..17956.864] | 18743.296 ± 0.000 [18743.296..18743.296] | 19529.728 ± 0.000 [19529.728..19529.728] | 38010.880 ± 0.000 [38010.880..38010.880] |
| 32K | 15400.960 ± 0.000 [15400.960..15400.960] | 16056.320 ± 0.000 [16056.320..16056.320] | 17956.864 ± 0.000 [17956.864..17956.864] | 18219.008 ± 0.000 [18219.008..18219.008] | 19791.872 ± 0.000 [19791.872..19791.872] | 38010.880 ± 0.000 [38010.880..38010.880] |
| 64K | 11730.944 ± 0.000 [11730.944..11730.944] | 11862.016 ± 0.000 [11862.016..11862.016] | 12124.160 ± 0.000 [12124.160..12124.160] | 12386.304 ± 0.000 [12386.304..12386.304] | 12386.304 ± 0.000 [12386.304..12386.304] | 24510.464 ± 0.000 [24510.464..24510.464] |
| 128K | 16056.320 ± 0.000 [16056.320..16056.320] | 16580.608 ± 0.000 [16580.608..16580.608] | 16056.320 ± 0.000 [16056.320..16056.320] | 18219.008 ± 0.000 [18219.008..18219.008] | 18743.296 ± 0.000 [18743.296..18743.296] | 18219.008 ± 0.000 [18219.008..18219.008] |

#### main_20261008 · wbuffix · lat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 298.454 ± 0.940 [297.790..299.119] | 569.705 ± 1.191 [568.863..570.547] | 1039.453 ± 0.022 [1039.437..1039.468] | 2072.997 ± 0.311 [2072.777..2073.216] | 4112.692 ± 0.014 [4112.682..4112.701] | 8050.473 ± 0.123 [8050.386..8050.560] |
| 8K | 576.712 ± 0.213 [576.562..576.863] | 597.190 ± 3.204 [594.925..599.456] | 1141.530 ± 4.203 [1138.558..1144.502] | 2073.108 ± 0.305 [2072.892..2073.324] | 4111.809 ± 0.120 [4111.725..4111.894] | 8052.406 ± 0.488 [8052.061..8052.751] |
| 16K | 962.750 ± 1.249 [961.867..963.633] | 1147.683 ± 1.601 [1146.551..1148.815] | 1188.765 ± 0.828 [1188.180..1189.350] | 2261.291 ± 19.510 [2247.495..2275.087] | 4112.331 ± 0.815 [4111.755..4112.907] | 8049.002 ± 0.000 [8049.002..8049.002] |
| 32K | 1830.777 ± 0.000 [1830.777..1830.777] | 1897.970 ± 0.000 [1897.970..1897.970] | 2279.563 ± 0.000 [2279.563..2279.563] | 2355.495 ± 0.000 [2355.495..2355.495] | 4477.327 ± 0.000 [4477.327..4477.327] | 8053.294 ± 0.000 [8053.294..8053.294] |
| 64K | 2656.258 ± 0.000 [2656.258..2656.258] | 2680.070 ± 0.000 [2680.070..2680.070] | 2854.286 ± 0.000 [2854.286..2854.286] | 3500.922 ± 0.000 [3500.922..3500.922] | 3100.121 ± 0.000 [3100.121..3100.121] | 6005.981 ± 0.000 [6005.981..6005.981] |
| 128K | 4442.658 ± 0.000 [4442.658..4442.658] | 4455.064 ± 0.000 [4455.064..4455.064] | 4508.221 ± 0.000 [4508.221..4508.221] | 4878.453 ± 0.000 [4878.453..4878.453] | 5870.736 ± 0.000 [5870.736..5870.736] | 4774.283 ± 0.000 [4774.283..4774.283] |

#### main_20261008 · wbuffix · slat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 0.842 ± 0.004 [0.840..0.845] | 0.999 ± 0.024 [0.982..1.016] | 1.219 ± 0.006 [1.214..1.223] | 1.651 ± 0.016 [1.640..1.662] | 2.602 ± 0.009 [2.596..2.608] | 4.390 ± 0.028 [4.370..4.410] |
| 8K | 0.849 ± 0.003 [0.846..0.851] | 1.006 ± 0.002 [1.005..1.008] | 1.233 ± 0.001 [1.232..1.234] | 1.645 ± 0.008 [1.639..1.650] | 2.604 ± 0.032 [2.582..2.626] | 4.388 ± 0.009 [4.381..4.394] |
| 16K | 0.870 ± 0.004 [0.868..0.873] | 1.052 ± 0.007 [1.047..1.057] | 1.241 ± 0.001 [1.240..1.241] | 1.663 ± 0.030 [1.642..1.684] | 2.603 ± 0.007 [2.598..2.608] | 4.432 ± 0.000 [4.432..4.432] |
| 32K | 0.998 ± 0.000 [0.998..0.998] | 1.088 ± 0.000 [1.088..1.088] | 1.309 ± 0.000 [1.309..1.309] | 1.678 ± 0.000 [1.678..1.678] | 2.623 ± 0.000 [2.623..2.623] | 4.294 ± 0.000 [4.294..4.294] |
| 64K | 0.961 ± 0.000 [0.961..0.961] | 1.085 ± 0.000 [1.085..1.085] | 1.320 ± 0.000 [1.320..1.320] | 1.688 ± 0.000 [1.688..1.688] | 2.543 ± 0.000 [2.543..2.543] | 4.292 ± 0.000 [4.292..4.292] |
| 128K | 0.978 ± 0.000 [0.978..0.978] | 1.070 ± 0.000 [1.070..1.070] | 1.266 ± 0.000 [1.266..1.266] | 1.642 ± 0.000 [1.642..1.642] | 2.564 ± 0.000 [2.564..2.564] | 3.982 ± 0.000 [3.982..3.982] |

#### main_20261008 · wbuffix · bw_first10s_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 1273.020 ± 0.246 [1272.846..1273.194] | 1285.448 ± 0.533 [1285.072..1285.825] | 1288.553 ± 0.107 [1288.477..1288.629] | 1290.895 ± 0.090 [1290.831..1290.958] | 1293.670 ± 0.004 [1293.667..1293.673] | 1299.042 ± 0.002 [1299.041..1299.043] |
| 8K | 736.912 ± 0.314 [736.690..737.134] | 1280.858 ± 0.169 [1280.739..1280.977] | 1285.680 ± 0.264 [1285.493..1285.867] | 1290.772 ± 0.254 [1290.592..1290.952] | 1293.673 ± 0.000 [1293.673..1293.673] | 1299.022 ± 0.013 [1299.013..1299.031] |
| 16K | 378.772 ± 0.163 [378.657..378.887] | 736.149 ± 0.280 [735.951..736.347] | 1279.434 ± 0.531 [1279.058..1279.809] | 1285.664 ± 0.242 [1285.493..1285.834] | 1293.670 ± 0.004 [1293.667..1293.673] | 1299.043 ± 0.000 [1299.043..1299.043] |
| 32K | 189.590 ± 0.000 [189.590..189.590] | 376.970 ± 0.000 [376.970..376.970] | 741.204 ± 0.000 [741.204..741.204] | 1278.334 ± 0.000 [1278.334..1278.334] | 1286.819 ± 0.000 [1286.819..1286.819] | 1299.041 ± 0.000 [1299.041..1299.041] |
| 64K | 123.589 ± 0.000 [123.589..123.589] | 246.791 ± 0.000 [246.791..246.791] | 488.131 ± 0.000 [488.131..488.131] | 908.028 ± 0.000 [908.028..908.028] | 1403.948 ± 0.000 [1403.948..1403.948] | 1411.562 ± 0.000 [1411.562..1411.562] |
| 128K | 77.282 ± 0.000 [77.282..77.282] | 154.101 ± 0.000 [154.101..154.101] | 307.517 ± 0.000 [307.517..307.517] | 598.712 ± 0.000 [598.712..598.712] | 1051.298 ± 0.000 [1051.298..1051.298] | 1482.975 ± 0.000 [1482.975..1482.975] |

#### main_20261008 · wbuffix · bw_last20s_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 325.297 ± 2.059 [323.842..326.753] | 324.748 ± 5.081 [321.155..328.341] | 244.723 ± 0.162 [244.608..244.837] | 247.458 ± 0.242 [247.287..247.629] | 254.340 ± 0.022 [254.324..254.356] | 275.506 ± 0.088 [275.444..275.568] |
| 8K | 81.552 ± 0.580 [81.142..81.962] | 321.046 ± 0.336 [320.808..321.283] | 328.025 ± 6.901 [323.145..332.904] | 244.931 ± 3.597 [242.387..247.474] | 254.632 ± 0.175 [254.508..254.756] | 274.940 ± 0.156 [274.829..275.050] |
| 16K | 58.445 ± 0.272 [58.252..58.637] | 81.434 ± 0.259 [81.251..81.617] | 320.795 ± 1.884 [319.463..322.127] | 322.196 ± 7.249 [317.070..327.321] | 254.348 ± 0.227 [254.187..254.508] | 275.724 ± 0.000 [275.724..275.724] |
| 32K | 32.347 ± 0.000 [32.347..32.347] | 60.145 ± 0.000 [60.145..60.145] | 81.515 ± 0.000 [81.515..81.515] | 322.079 ± 0.000 [322.079..322.079] | 318.536 ± 0.000 [318.536..318.536] | 274.962 ± 0.000 [274.962..274.962] |
| 64K | 24.843 ± 0.000 [24.843..24.843] | 48.139 ± 0.000 [48.139..48.139] | 82.853 ± 0.000 [82.853..82.853] | 143.391 ± 0.000 [143.391..143.391] | 518.925 ± 0.000 [518.925..518.925] | 534.135 ± 0.000 [534.135..534.135] |
| 128K | 14.416 ± 0.000 [14.416..14.416] | 28.748 ± 0.000 [28.748..28.748] | 56.496 ± 0.000 [56.496..56.496] | 98.131 ± 0.000 [98.131..98.131] | 192.600 ± 0.000 [192.600..192.600] | 671.599 ± 0.000 [671.599..671.599] |

#### main_20261008 · wbuffix · gc_onset_s
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 6.304 ± 0.003 [6.302..6.306] | 5.745 ± 0.002 [5.743..5.746] | 5.693 ± 0.004 [5.690..5.696] | 5.696 ± 0.000 [5.696..5.696] | 5.693 ± 0.005 [5.690..5.697] | 5.697 ± 0.000 [5.697..5.697] |
| 8K | 5.814 ± 0.005 [5.811..5.817] | 5.821 ± 0.000 [5.821..5.821] | 5.777 ± 0.000 [5.777..5.777] | 5.696 ± 0.000 [5.696..5.696] | 5.697 ± 0.001 [5.697..5.697] | 5.697 ± 0.000 [5.697..5.697] |
| 16K | 5.919 ± 0.001 [5.918..5.920] | 5.908 ± 0.001 [5.907..5.909] | 5.924 ± 0.000 [5.924..5.924] | 5.846 ± 0.000 [5.846..5.847] | 5.697 ± 0.000 [5.697..5.697] | 5.694 ± 0.000 [5.694..5.694] |
| 32K | 6.067 ± 0.000 [6.067..6.067] | 6.070 ± 0.000 [6.070..6.070] | 6.069 ± 0.000 [6.069..6.069] | 6.099 ± 0.000 [6.099..6.099] | 5.978 ± 0.000 [5.978..5.978] | 5.698 ± 0.000 [5.698..5.698] |
| 64K | 3.675 ± 0.000 [3.675..3.675] | 3.671 ± 0.000 [3.671..3.671] | 3.675 ± 0.000 [3.675..3.675] | 3.684 ± 0.000 [3.684..3.684] | 3.874 ± 0.000 [3.874..3.874] | 3.881 ± 0.000 [3.881..3.881] |
| 128K | 2.476 ± 0.000 [2.476..2.476] | 2.474 ± 0.000 [2.474..2.474] | 2.477 ± 0.000 [2.477..2.477] | 2.477 ± 0.000 [2.477..2.477] | 2.474 ± 0.000 [2.474..2.474] | 3.867 ± 0.000 [3.867..3.867] |

#### main_20261008 · wbuffix · gc_onset_last_part_s
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 6.325 ± 0.003 [6.322..6.327] | 5.764 ± 0.002 [5.762..5.765] | 5.693 ± 0.004 [5.691..5.696] | 5.696 ± 0.000 [5.696..5.696] | 5.694 ± 0.005 [5.690..5.697] | 5.698 ± 0.000 [5.697..5.698] |
| 8K | 5.834 ± 0.005 [5.831..5.837] | 5.862 ± 0.000 [5.861..5.862] | 5.778 ± 0.000 [5.778..5.778] | 5.696 ± 0.000 [5.696..5.696] | 5.697 ± 0.001 [5.697..5.698] | 5.697 ± 0.000 [5.697..5.697] |
| 16K | 5.949 ± 0.001 [5.948..5.950] | 5.975 ± 0.001 [5.975..5.976] | 5.946 ± 0.000 [5.946..5.946] | 5.868 ± 0.000 [5.868..5.868] | 5.697 ± 0.000 [5.697..5.697] | 5.694 ± 0.000 [5.694..5.694] |
| 32K | 6.149 ± 0.000 [6.149..6.149] | 6.125 ± 0.000 [6.125..6.125] | 6.106 ± 0.000 [6.106..6.106] | 6.143 ± 0.000 [6.143..6.143] | 6.001 ± 0.000 [6.001..6.001] | 5.698 ± 0.000 [5.698..5.698] |
| 64K | 3.715 ± 0.000 [3.715..3.715] | 3.714 ± 0.000 [3.714..3.714] | 3.718 ± 0.000 [3.718..3.718] | 3.719 ± 0.000 [3.719..3.719] | 3.947 ± 0.000 [3.947..3.947] | 3.899 ± 0.000 [3.899..3.899] |
| 128K | 2.516 ± 0.000 [2.516..2.516] | 2.514 ± 0.000 [2.514..2.514] | 2.516 ± 0.000 [2.516..2.516] | 2.537 ± 0.000 [2.537..2.537] | 2.521 ± 0.000 [2.521..2.521] | 3.895 ± 0.000 [3.895..3.895] |

#### main_20261008 · wbuffix · bw_pre_gc_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 2007.669 ± 0.664 [2007.199..2008.138] | 2211.019 ± 0.005 [2211.016..2211.023] | 2217.943 ± 0.297 [2217.733..2218.153] | 2217.770 ± 0.004 [2217.767..2217.773] | 2217.878 ± 0.008 [2217.872..2217.883] | 2217.932 ± 0.000 [2217.932..2217.932] |
| 8K | 1091.777 ± 0.024 [1091.760..1091.793] | 2182.495 ± 0.091 [2182.430..2182.560] | 2200.607 ± 0.066 [2200.560..2200.653] | 2217.773 ± 0.000 [2217.773..2217.773] | 2217.883 ± 0.000 [2217.883..2217.883] | 2217.909 ± 0.000 [2217.909..2217.909] |
| 16K | 535.565 ± 0.005 [535.562..535.569] | 1071.577 ± 0.636 [1071.128..1072.027] | 2143.243 ± 0.022 [2143.227..2143.259] | 2172.983 ± 0.161 [2172.869..2173.097] | 2217.878 ± 0.008 [2217.872..2217.883] | 2217.932 ± 0.000 [2217.932..2217.932] |
| 32K | 255.990 ± 0.000 [255.990..255.990] | 512.569 ± 0.000 [512.569..512.569] | 1026.573 ± 0.000 [1026.573..1026.573] | 2032.771 ± 0.000 [2032.771..2032.771] | 2123.535 ± 0.000 [2123.535..2123.535] | 2217.932 ± 0.000 [2217.932..2217.932] |
| 64K | 219.240 ± 0.000 [219.240..219.240] | 438.600 ± 0.000 [438.600..438.600] | 876.518 ± 0.000 [876.518..876.518] | 1752.214 ± 0.000 [1752.214..1752.214] | 3350.387 ± 0.000 [3350.387..3350.387] | 3348.179 ± 0.000 [3348.179..3348.179] |
| 128K | 170.170 ± 0.000 [170.170..170.170] | 340.449 ± 0.000 [340.449..340.449] | 680.508 ± 0.000 [680.508..680.508] | 1359.062 ± 0.000 [1359.062..1359.062] | 2716.274 ± 0.000 [2716.274..2716.274] | 3357.214 ± 0.000 [3357.214..3357.214] |

#### main_20261008 · wbuffix · bw_post_gc_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 242.097 ± 1.600 [240.965..243.229] | 259.910 ± 0.886 [259.283..260.537] | 305.753 ± 0.038 [305.726..305.780] | 307.362 ± 0.071 [307.312..307.412] | 311.648 ± 0.014 [311.638..311.658] | 323.221 ± 0.069 [323.172..323.270] |
| 8K | 128.590 ± 0.327 [128.359..128.822] | 240.839 ± 2.935 [238.764..242.914] | 260.424 ± 2.204 [258.866..261.982] | 307.127 ± 0.322 [306.900..307.355] | 311.755 ± 0.064 [311.710..311.801] | 323.079 ± 0.078 [323.024..323.134] |
| 16K | 89.026 ± 0.395 [88.747..89.305] | 131.672 ± 0.284 [131.471..131.873] | 246.698 ± 0.325 [246.468..246.928] | 267.591 ± 4.161 [264.649..270.533] | 311.660 ± 0.081 [311.602..311.717] | 323.379 ± 0.000 [323.379..323.379] |
| 32K | 47.427 ± 0.000 [47.427..47.427] | 89.402 ± 0.000 [89.402..89.402] | 129.631 ± 0.000 [129.631..129.631] | 245.838 ± 0.000 [245.838..245.838] | 277.479 ± 0.000 [277.479..277.479] | 323.071 ± 0.000 [323.071..323.071] |
| 64K | 36.395 ± 0.000 [36.395..36.395] | 71.891 ± 0.000 [71.891..71.891] | 131.746 ± 0.000 [131.746..131.746] | 194.798 ± 0.000 [194.798..194.798] | 477.616 ± 0.000 [477.616..477.616] | 499.886 ± 0.000 [499.886..499.886] |
| 128K | 23.239 ± 0.000 [23.239..23.239] | 46.310 ± 0.000 [46.310..46.310] | 91.272 ± 0.000 [91.272..91.272] | 165.200 ± 0.000 [165.200..165.200] | 258.795 ± 0.000 [258.795..258.795] | 681.794 ± 0.000 [681.794..681.794] |

#### main_20261008 · wbuffix · gc_cnt
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 8359.000 ± 83.439 [8300..8418] | 9436.000 ± 45.255 [9404..9468] | 11272.000 ± 0.000 [11272..11272] | 11278.000 ± 2.828 [11276..11280] | 11344.000 ± 0.000 [11344..11344] | 11478.000 ± 2.828 [11476..11480] |
| 8K | 8049.500 ± 2.121 [8048..8051] | 8293.000 ± 131.522 [8200..8386] | 9352.000 ± 79.196 [9296..9408] | 11280.000 ± 0.000 [11280..11280] | 11346.000 ± 2.828 [11344..11348] | 11478.000 ± 2.828 [11476..11480] |
| 16K | 7073.500 ± 24.749 [7056..7091] | 8145.000 ± 35.355 [8120..8170] | 8326.500 ± 17.678 [8314..8339] | 9485.000 ± 190.919 [9350..9620] | 11344.000 ± 0.000 [11344..11344] | 11480.000 ± 0.000 [11480..11480] |
| 32K | 7217.000 ± 0.000 [7217..7217] | 7315.000 ± 0.000 [7315..7315] | 8250.000 ± 0.000 [8250..8250] | 8401.000 ± 0.000 [8401..8401] | 9540.000 ± 0.000 [9540..9540] | 11480.000 ± 0.000 [11480..11480] |
| 64K | 15486.000 ± 0.000 [15486..15486] | 15563.000 ± 0.000 [15563..15563] | 15734.000 ± 0.000 [15734..15734] | 16146.000 ± 0.000 [16146..16146] | 15930.000 ± 0.000 [15930..15930] | 16808.000 ± 0.000 [16808..16808] |
| 128K | 22262.000 ± 0.000 [22262..22262] | 22231.000 ± 0.000 [22231..22231] | 22202.000 ± 0.000 [22202..22202] | 22024.000 ± 0.000 [22024..22024] | 21712.000 ± 0.000 [21712..21712] | 21413.000 ± 0.000 [21413..21413] |

#### main_20261008 · wbuffix · ftl_host_pgs
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 6429836 ± 20856.822 [6415088..6444584] | 6737857 ± 14163.349 [6727842..6747872] | 7388264 ± 509.117 [7387904..7388624] | 7410644 ± 1159.655 [7409824..7411464] | 7470512 ± 113.137 [7470432..7470592] | 7633024 ± 859.842 [7632416..7633632] |
| 8K | 3327576 ± 724.077 [3327064..3328088] | 3214080 ± 16964.199 [3202084..3226075] | 3363460 ± 12066.070 [3354928..3371992] | 3704584 ± 1120.057 [3703792..3705376] | 3735968 ± 452.548 [3735648..3736288] | 3815488 ± 429.921 [3815184..3815792] |
| 16K | 1993962 ± 2449.418 [1992230..1995694] | 1672756 ± 2398.506 [1671060..1674452] | 1614880 ± 1114.400 [1614092..1615668] | 1698222 ± 14433.464 [1688016..1708428] | 1867628 ± 277.186 [1867432..1867824] | 1908784 ± 0.000 [1908784..1908784] |
| 32K | 1048792 ± 0.000 [1048792..1048792] | 1011585 ± 0.000 [1011585..1011585] | 842179.000 ± 0.000 [842179..842179] | 815109.000 ± 0.000 [815109..815109] | 857626.000 ± 0.000 [857626..857626] | 953880.000 ± 0.000 [953880..953880] |
| 64K | 722868.000 ± 0.000 [722868..722868] | 716403.000 ± 0.000 [716403..716403] | 672730.000 ± 0.000 [672730..672730] | 548451.000 ± 0.000 [548451..548451] | 619321.000 ± 0.000 [619321..619321] | 639422.000 ± 0.000 [639422..639422] |
| 128K | 432196.000 ± 0.000 [432196..432196] | 430981.000 ± 0.000 [430981..430981] | 425924.000 ± 0.000 [425924..425924] | 393613.000 ± 0.000 [393613..393613] | 327062.000 ± 0.000 [327062..327062] | 402191.000 ± 0.000 [402191..402191] |

#### main_20261008 · wbuffix · ftl_gc_pgs
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 13810204 ± 150179.581 [13704011..13916397] | 15708119 ± 78713.713 [15652460..15763778] | 18817590 ± 517.602 [18817224..18817956] | 18807072 ± 4491.542 [18803896..18810248] | 18882280 ± 124.451 [18882192..18882368] | 18994496 ± 4253.954 [18991488..18997504] |
| 8K | 6476546 ± 1402.900 [6475554..6477538] | 6838582 ± 117677.418 [6755371..6921792] | 7773333 ± 69068.776 [7724494..7822172] | 9406324 ± 1018.234 [9405604..9407044] | 9442464 ± 2443.761 [9440736..9444192] | 9498376 ± 2206.173 [9496816..9499936] |
| 16K | 2408458 ± 10179.509 [2401260..2415656] | 3278262 ± 15635.545 [3267206..3289318] | 3428498 ± 7935.859 [3422886..3434109] | 3938271 ± 83227.882 [3879420..3997122] | 4720564 ± 277.186 [4720368..4720760] | 4749232 ± 0.000 [4749232..4749232] |
| 32K | 1189155 ± 0.000 [1189155..1189155] | 1251473 ± 0.000 [1251473..1251473] | 1660230 ± 0.000 [1660230..1660230] | 1725664 ± 0.000 [1725664..1725664] | 1974722 ± 0.000 [1974722..1974722] | 2375124 ± 0.000 [2375124..2375124] |
| 64K | 1454598 ± 0.000 [1454598..1454598] | 1470904 ± 0.000 [1470904..1470904] | 1536469 ± 0.000 [1536469..1536469] | 1713443 ± 0.000 [1713443..1713443] | 1614792 ± 0.000 [1614792..1614792] | 1707056 ± 0.000 [1707056..1707056] |
| 128K | 1090213 ± 0.000 [1090213..1090213] | 1089448 ± 0.000 [1089448..1089448] | 1092651 ± 0.000 [1092651..1092651] | 1113559 ± 0.000 [1113559..1113559] | 1160138 ± 0.000 [1160138..1160138] | 1065766 ± 0.000 [1065766..1065766] |

#### main_20261008 · wbuffix · waf_gc
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 3.148 ± 0.016 [3.136..3.159] | 3.331 ± 0.007 [3.327..3.336] | 3.547 ± 0.000 [3.547..3.547] | 3.538 ± 0.000 [3.538..3.538] | 3.528 ± 0.000 [3.528..3.528] | 3.488 ± 0.000 [3.488..3.489] |
| 8K | 2.946 ± 0.000 [2.946..2.946] | 3.128 ± 0.025 [3.110..3.146] | 3.311 ± 0.012 [3.302..3.320] | 3.539 ± 0.001 [3.538..3.540] | 3.527 ± 0.000 [3.527..3.528] | 3.489 ± 0.000 [3.489..3.490] |
| 16K | 2.208 ± 0.004 [2.205..2.210] | 2.960 ± 0.007 [2.955..2.964] | 3.123 ± 0.003 [3.121..3.126] | 3.319 ± 0.029 [3.298..3.340] | 3.528 ± 0.001 [3.527..3.528] | 3.488 ± 0.000 [3.488..3.488] |
| 32K | 2.134 ± 0.000 [2.134..2.134] | 2.237 ± 0.000 [2.237..2.237] | 2.971 ± 0.000 [2.971..2.971] | 3.117 ± 0.000 [3.117..3.117] | 3.303 ± 0.000 [3.303..3.303] | 3.490 ± 0.000 [3.490..3.490] |
| 64K | 3.012 ± 0.000 [3.012..3.012] | 3.053 ± 0.000 [3.053..3.053] | 3.284 ± 0.000 [3.284..3.284] | 4.124 ± 0.000 [4.124..4.124] | 3.607 ± 0.000 [3.607..3.607] | 3.670 ± 0.000 [3.670..3.670] |
| 128K | 3.522 ± 0.000 [3.522..3.522] | 3.528 ± 0.000 [3.528..3.528] | 3.565 ± 0.000 [3.565..3.565] | 3.829 ± 0.000 [3.829..3.829] | 4.547 ± 0.000 [4.547..4.547] | 3.650 ± 0.000 [3.650..3.650] |

#### main_20261008 · wbuffix · waf_total
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 3.148 ± 0.016 [3.136..3.159] | 3.331 ± 0.007 [3.327..3.336] | 3.547 ± 0.000 [3.547..3.547] | 3.538 ± 0.000 [3.538..3.538] | 3.528 ± 0.000 [3.528..3.528] | 3.488 ± 0.000 [3.488..3.489] |
| 8K | 5.891 ± 0.000 [5.891..5.891] | 3.128 ± 0.025 [3.110..3.146] | 3.311 ± 0.012 [3.302..3.320] | 3.539 ± 0.001 [3.538..3.540] | 3.527 ± 0.000 [3.527..3.528] | 3.489 ± 0.000 [3.489..3.490] |
| 16K | 8.831 ± 0.014 [8.821..8.842] | 5.919 ± 0.013 [5.910..5.928] | 3.123 ± 0.003 [3.121..3.126] | 3.319 ± 0.029 [3.298..3.340] | 3.528 ± 0.001 [3.527..3.528] | 3.488 ± 0.000 [3.488..3.488] |
| 32K | 17.071 ± 0.000 [17.071..17.071] | 8.949 ± 0.000 [8.949..8.949] | 5.943 ± 0.000 [5.943..5.943] | 3.117 ± 0.000 [3.117..3.117] | 3.303 ± 0.000 [3.303..3.303] | 3.490 ± 0.000 [3.490..3.490] |
| 64K | 48.196 ± 0.000 [48.196..48.196] | 24.425 ± 0.000 [24.425..24.425] | 13.136 ± 0.000 [13.136..13.136] | 8.248 ± 0.000 [8.248..8.248] | 3.607 ± 0.000 [3.607..3.607] | 3.670 ± 0.000 [3.670..3.670] |
| 128K | 112.720 ± 0.000 [112.720..112.720] | 56.445 ± 0.000 [56.445..56.445] | 28.523 ± 0.000 [28.523..28.523] | 15.316 ± 0.000 [15.316..15.316] | 9.094 ± 0.000 [9.094..9.094] | 3.650 ± 0.000 [3.650..3.650] |

#### main_20261008 · wbuffix · written_GiB
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 24.528 ± 0.080 [24.472..24.584] | 25.703 ± 0.054 [25.665..25.741] | 28.184 ± 0.002 [28.183..28.185] | 28.269 ± 0.004 [28.266..28.272] | 28.498 ± 0.000 [28.497..28.498] | 29.118 ± 0.003 [29.115..29.120] |
| 8K | 12.697 ± 0.003 [12.695..12.699] | 24.521 ± 0.129 [24.430..24.613] | 25.661 ± 0.092 [25.596..25.726] | 28.264 ± 0.009 [28.258..28.270] | 28.503 ± 0.003 [28.501..28.506] | 29.110 ± 0.003 [29.108..29.112] |
| 16K | 7.606 ± 0.009 [7.600..7.613] | 12.763 ± 0.019 [12.750..12.776] | 24.641 ± 0.017 [24.629..24.653] | 25.913 ± 0.220 [25.757..26.069] | 28.498 ± 0.004 [28.495..28.501] | 29.126 ± 0.000 [29.126..29.126] |
| 32K | 4.001 ± 0.000 [4.001..4.001] | 7.718 ± 0.000 [7.718..7.718] | 12.851 ± 0.000 [12.851..12.851] | 24.875 ± 0.000 [24.875..24.875] | 26.173 ± 0.000 [26.173..26.173] | 29.110 ± 0.000 [29.110..29.110] |
| 64K | 2.758 ± 0.000 [2.758..2.758] | 5.466 ± 0.000 [5.466..5.466] | 10.265 ± 0.000 [10.265..10.265] | 16.737 ± 0.000 [16.737..16.737] | 37.800 ± 0.000 [37.800..37.800] | 39.027 ± 0.000 [39.027..39.027] |
| 128K | 1.649 ± 0.000 [1.649..1.649] | 3.288 ± 0.000 [3.288..3.288] | 6.499 ± 0.000 [6.499..6.499] | 12.012 ± 0.000 [12.012..12.012] | 19.962 ± 0.000 [19.962..19.962] | 49.096 ± 0.000 [49.096..49.096] |

#### main_20261008 · wbuffix · fill_ratio
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 2.187 ± 0.007 [2.182..2.192] | 2.292 ± 0.005 [2.289..2.295] | 2.513 ± 0.000 [2.513..2.513] | 2.521 ± 0.000 [2.521..2.521] | 2.541 ± 0.000 [2.541..2.541] | 2.597 ± 0.000 [2.596..2.597] |
| 8K | 1.132 ± 0.000 [1.132..1.132] | 2.187 ± 0.012 [2.179..2.195] | 2.288 ± 0.008 [2.283..2.294] | 2.520 ± 0.001 [2.520..2.521] | 2.542 ± 0.000 [2.542..2.542] | 2.596 ± 0.000 [2.596..2.596] |
| 16K | 0.678 ± 0.001 [0.678..0.679] | 1.138 ± 0.002 [1.137..1.139] | 2.197 ± 0.002 [2.196..2.198] | 2.311 ± 0.020 [2.297..2.325] | 2.541 ± 0.000 [2.541..2.542] | 2.597 ± 0.000 [2.597..2.597] |
| 32K | 0.357 ± 0.000 [0.357..0.357] | 0.688 ± 0.000 [0.688..0.688] | 1.146 ± 0.000 [1.146..1.146] | 2.218 ± 0.000 [2.218..2.218] | 2.334 ± 0.000 [2.334..2.334] | 2.596 ± 0.000 [2.596..2.596] |
| 64K | 0.246 ± 0.000 [0.246..0.246] | 0.487 ± 0.000 [0.487..0.487] | 0.915 ± 0.000 [0.915..0.915] | 1.493 ± 0.000 [1.493..1.493] | 3.371 ± 0.000 [3.371..3.371] | 3.480 ± 0.000 [3.480..3.480] |
| 128K | 0.147 ± 0.000 [0.147..0.147] | 0.293 ± 0.000 [0.293..0.293] | 0.580 ± 0.000 [0.580..0.580] | 1.071 ± 0.000 [1.071..1.071] | 1.780 ± 0.000 [1.780..1.780] | 4.378 ± 0.000 [4.378..4.378] |

#### main_20261008 · wbuffix · chmodel_msgs
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 8K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 64K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 128K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### main_20261008 · wbuffix · kernel_warn
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 8K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 64K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 128K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

### 11.2.3 변형 비교 (wbuffix − base) / base, 60 s 평균 대역폭
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | +0.04% (418.4→418.6) | +1.17% (433.6→438.7) | -0.01% (480.9→480.9) | -0.05% (482.6→482.3) | -0.02% (486.4→486.3) | +0.01% (496.8→496.8) |
| 8K | -18.67% (266.4→216.7) | -0.39% (420.1→418.5) | -0.49% (440.1→437.9) | +0.01% (482.2→482.3) | +0.00% (486.4→486.4) | -0.13% (497.4→496.7) |
| 16K | -22.67% (167.9→129.8) | -20.16% (272.8→217.8) | -0.11% (421.0→420.5) | -0.37% (443.8→442.2) | -0.02% (486.4→486.3) | +0.04% (496.7→496.9) |
| 32K | -26.28% (92.6→68.3) | -24.31% (174.0→131.7) | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

### 11.2.3w 변형 비교 (wbuffix − base) / base, WAF_total
| map\bs | 4K | 8K | 16K | 32K | 64K | 128K |
|---|---|---|---|---|---|---|
| 4K | +0.09% (3.145→3.148) | +1.21% (3.292→3.331) | -0.01% (3.547→3.547) | +0.01% (3.537→3.538) | +0.01% (3.527→3.528) | -0.02% (3.489→3.488) |
| 8K | -26.29% (7.992→5.891) | -0.55% (3.145→3.128) | -0.50% (3.328→3.311) | +0.01% (3.539→3.539) | +0.01% (3.527→3.527) | +0.11% (3.485→3.489) |
| 16K | -30.27% (12.665→8.831) | -27.39% (8.152→5.919) | -0.15% (3.128→3.123) | -0.44% (3.334→3.319) | +0.01% (3.527→3.528) | -0.04% (3.489→3.488) |
| 32K | -30.25% (24.474→17.071) | -32.16% (13.191→8.949) | NA | NA | NA | NA |
| 64K | NA | NA | NA | NA | NA | NA |
| 128K | NA | NA | NA | NA | NA | NA |

### 11.2.4 회차별 전체 (analysis/summary_runs.csv 와 같은 값)
```csv
variant,map,bs,rep,bw_MiBps,iops,written_GiB,fill_ratio,clat_mean_us,clat_p50_us,clat_p99_us,clat_p999_us,lat_mean_us,slat_mean_us,runtime_s,bw_first10s_MiBps,bw_last20s_MiBps,dev_bytes,chmodel_msgs,kernel_warn,gc_onset_s,gc_onset_last_part_s,bw_pre_gc_MiBps,bw_post_gc_MiBps,gc_cnt,ftl_host_pgs,ftl_gc_pgs,waf_gc,waf_total
base,4k,4k,1,418.395508,107109.381510,24.515800,2.186170,297.724553,70.144000,13303.808000,17170.432000,298.570561,0.846008,60.001000,1273.448535,320.739526,12040984064,0,0,6.301980,6.322915,2008.175944,241.840956,8345,6426670,13784996,3.144967,3.144967
base,4k,8k,1,433.589844,55499.541735,25.409485,2.265864,575.365254,120.320000,16449.536000,17956.864000,576.359217,0.993962,60.009000,1285.085596,321.294507,12040984064,0,0,5.745002,5.764206,2211.019886,254.313055,9182,6660944,15264468,3.291637,3.291637
base,4k,16k,1,480.927734,30779.394364,28.180786,2.512991,1038.183234,222.208000,17694.720000,18481.152000,1039.409494,1.226260,60.003000,1288.663867,244.568652,12040984064,0,0,5.697114,5.697334,2217.721591,305.714252,11272,7387424,18818284,3.547340,3.547340
base,4k,32k,1,482.594727,15443.059282,28.277557,2.521621,2070.201866,444.416000,18219.008000,18743.296000,2071.862536,1.660670,60.001000,1290.946875,243.187158,12040984064,0,0,5.696309,5.696514,2217.767045,307.250678,11280,7412792,18808928,3.537361,3.537361
base,4k,64k,1,486.360352,7781.766068,28.501953,2.541631,4109.243368,897.024000,19005.440000,19529.728000,4111.872378,2.629010,60.009000,1293.673291,254.762256,12040984064,0,0,5.697804,5.697992,2217.883256,311.736669,11344,7471616,18881152,3.527051,3.527051
base,4k,128k,1,496.773438,3974.190646,29.116089,2.596396,8047.197067,1794.048000,20578.304000,38010.880000,8051.636637,4.439570,60.017000,1299.198340,275.072583,12040984064,0,0,5.698692,5.698875,2218.337891,323.184606,11480,7632608,18999456,3.489248,3.489248
base,8k,4k,1,266.393555,68196.973485,15.609829,1.391990,467.306883,342.016000,2473.984000,3457.024000,469.000362,1.693479,60.003000,814.962646,131.899951,12040984064,8242206,1,5.685446,5.690782,1115.468040,181.224546,14444,4091942,12260041,3.996142,7.992127
base,8k,8k,1,420.125000,53776.037066,24.617126,2.195206,593.817559,132.096000,15532.032000,17432.576000,594.825788,1.008229,60.001000,1282.384033,323.431494,12040984064,0,0,5.820556,5.861563,2180.882369,243.286341,8386,3226616,6921205,3.145035,3.145035
base,8k,16k,1,440.075195,28164.830586,25.786102,2.299448,1134.696490,224.256000,17432.576000,18481.152000,1135.911940,1.215451,60.001000,1285.950635,320.270410,12040984064,0,0,5.781899,5.782728,2198.647727,263.452582,9460,3379836,7867608,3.327808,3.327808
base,8k,32k,1,482.244141,15431.837877,28.258423,2.519915,2071.723042,444.416000,18219.008000,18743.296000,2073.363979,1.640937,60.004000,1290.967676,246.913477,12040984064,0,0,5.696200,5.696348,2217.772727,307.144173,11276,3703888,9402992,3.538682,3.538682
base,8k,64k,1,486.371094,7781.951504,28.500732,2.541522,4109.183074,897.024000,19005.440000,19529.728000,4111.808720,2.625646,60.005000,1293.672510,254.503271,12040984064,0,0,5.698415,5.698556,2217.881836,311.705705,11344,3735648,9440736,3.527202,3.527202
base,8k,128k,1,497.387695,3979.102786,29.147705,2.599215,8037.267831,1794.048000,20316.160000,38010.880000,8041.648308,4.380477,60.008000,1299.041748,276.862988,12040984064,0,0,5.698204,5.698335,2217.909091,323.793972,11480,3820448,9495600,3.485468,3.485468
base,16k,4k,1,167.852539,42970.417653,9.835476,0.877068,742.769526,684.032000,2768.896000,3915.776000,744.458571,1.689045,60.002000,430.340381,86.196948,12040984064,6757590,0,5.668286,5.684406,559.152699,128.884702,14419,2578311,5585060,3.166170,12.664680
base,16k,8k,1,272.789062,34917.104145,15.984581,1.425408,914.358511,692.224000,3162.112000,4358.144000,916.213581,1.855069,60.003000,822.685986,133.554443,12040984064,9087642,1,5.665941,5.697156,1117.981534,188.074987,15155,2095113,6444990,4.076202,8.152333
base,16k,16k,1,420.993164,26943.600940,24.668015,2.199744,1186.169263,246.784000,16908.288000,17956.864000,1187.409869,1.240606,60.001000,1278.890625,322.791333,12040984064,0,0,5.923822,5.945612,2143.227273,247.764323,8352,1616643,3439890,3.127798,3.127798
base,16k,32k,1,443.818359,14202.206005,26.012817,2.319665,2251.226353,464.896000,18219.008000,18743.296000,2252.890533,1.664179,60.018000,1286.221875,318.064355,12040984064,0,0,5.846011,5.867525,2173.073864,269.453009,9576,1704776,3978204,3.333564,3.333564
base,16k,64k,1,486.387695,7782.215335,28.507874,2.542159,4109.072779,897.024000,19005.440000,19529.728000,4111.605658,2.532879,60.018000,1293.667041,254.825732,12040984064,0,0,5.689829,5.689950,2217.871893,311.847907,11348,1868292,4721904,3.527391,3.527391
base,16k,128k,1,496.748047,3973.990703,29.114624,2.596265,8047.679688,1794.048000,20316.160000,38010.880000,8052.035086,4.355398,60.017000,1299.040723,275.170215,12040984064,0,0,5.696911,5.697022,2217.931818,323.166284,11480,1908056,4749968,3.489428,3.489428
base,32k,4k,1,92.599609,23705.581388,5.426048,0.483862,1347.668431,1236.992000,3784.704000,5079.040000,1349.623930,1.955499,60.003000,219.731641,49.794604,12040984064,8233550,0,5.635585,5.682222,280.504972,73.926803,15473,1422406,2929163,3.059302,24.474413
base,32k,8k,1,174.001953,22272.277310,10.196289,0.909243,1434.271000,1236.992000,4227.072000,5472.256000,1436.508133,2.237133,60.005000,436.111719,85.395361,12040984064,8786405,0,5.638842,5.672789,561.262784,135.522262,15691,1336448,3070857,3.297775,13.191101
wbuffix,4k,4k,1,419.499023,107391.834694,24.584137,2.192264,296.944530,69.120000,13434.880000,17170.432000,297.789508,0.844979,60.010000,1272.846143,323.841602,12040984064,0,0,6.306407,6.327294,2007.199300,243.228706,8418,6444584,13916397,3.159394,3.159394
wbuffix,4k,4k,2,417.634766,106914.569514,24.471619,2.182230,298.279554,69.120000,13565.952000,16908.288000,299.119485,0.839931,60.002000,1273.193652,326.753247,12040984064,0,0,6.301740,6.322443,2008.138021,240.965468,8300,6415088,13704011,3.136216,3.136216
wbuffix,4k,8k,1,439.299805,56230.392320,25.741089,2.295434,567.880647,121.344000,16580.608000,17956.864000,568.862533,0.981886,60.002000,1285.824658,321.154883,12040984064,0,0,5.746240,5.765273,2211.022727,260.536814,9468,6747872,15763778,3.336111,3.336111
wbuffix,4k,8k,2,438.002930,56064.415593,25.664680,2.288620,569.531176,121.344000,16580.608000,17694.720000,570.546685,1.015509,60.001000,1285.071582,328.340552,12040984064,0,0,5.743215,5.762021,2211.015625,259.283483,9404,6727842,15652460,3.326520,3.326520
wbuffix,4k,16k,1,480.893555,30777.213123,28.185364,2.513400,1038.245655,222.208000,17694.720000,18481.152000,1039.468445,1.222790,60.017000,1288.477490,244.837354,12040984064,0,0,5.690366,5.690582,2218.153232,305.780211,11272,7388624,18817224,3.546783,3.546783
wbuffix,4k,16k,2,480.911133,30778.316586,28.182617,2.513155,1038.222883,222.208000,17694.720000,18481.152000,1039.437250,1.214367,60.009000,1288.629199,244.608203,12040984064,0,0,5.696107,5.696325,2217.732955,305.725774,11272,7387904,18817956,3.547131,3.547131
wbuffix,4k,32k,1,482.379883,15436.176417,28.272491,2.521169,2071.137088,444.416000,18219.008000,18743.296000,2072.777015,1.639927,60.017000,1290.958301,247.629443,12040984064,0,0,5.696178,5.696374,2217.767045,307.411554,11280,7411464,18810248,3.537994,3.537994
wbuffix,4k,32k,2,482.281250,15433.017862,28.266235,2.520611,2071.554523,444.416000,18219.008000,18743.296000,2073.216483,1.661960,60.016000,1290.831250,247.287500,12040984064,0,0,5.696014,5.696219,2217.772727,307.311676,11276,7409824,18803896,3.537698,3.537698
wbuffix,4k,64k,1,486.268555,7780.310605,28.498047,2.541283,4110.105730,897.024000,19005.440000,19529.728000,4112.701463,2.595732,60.012000,1293.673291,254.356152,12040984064,0,0,5.696560,5.696747,2217.883256,311.657522,11344,7470592,18882192,3.527536,3.527536
wbuffix,4k,64k,2,486.266602,7780.273617,28.497437,2.541228,4110.073581,897.024000,19005.440000,19529.728000,4112.681837,2.608257,60.011000,1293.667041,254.324487,12040984064,0,0,5.690118,5.690304,2217.871893,311.637857,11344,7470432,18882368,3.527614,3.527614
wbuffix,4k,128k,1,496.851562,3974.819185,29.115356,2.596331,8045.976356,1794.048000,20316.160000,38010.880000,8050.386183,4.409827,60.006000,1299.040820,275.568457,12040984064,0,0,5.697382,5.697563,2217.931818,323.172027,11476,7632416,18991488,3.488267,3.488267
wbuffix,4k,128k,2,496.832031,3974.657603,29.119995,2.596744,8046.189912,1794.048000,20578.304000,38010.880000,8050.559751,4.369839,60.018000,1299.043115,275.443921,12040984064,0,0,5.697290,5.697469,2217.931818,323.269818,11480,7633632,18997504,3.488659,3.488659
wbuffix,8k,4k,1,216.722656,55481.141981,12.698837,1.132405,575.715251,150.528000,15007.744000,17170.432000,576.561567,0.846317,60.001000,737.134473,81.962451,12040984064,0,0,5.810656,5.830705,1091.793324,128.821615,8051,3328088,6477538,2.946324,5.891168
wbuffix,8k,4k,2,216.611328,55452.727697,12.695084,1.132070,576.011732,152.576000,15007.744000,17170.432000,576.862725,0.850994,60.014000,736.689746,81.141699,12040984064,0,0,5.817261,5.837219,1091.759943,128.358793,8048,3327064,6475554,2.946327,5.891103
wbuffix,8k,8k,1,420.054688,53767.020550,24.612999,2.194838,593.917154,132.096000,15400.960000,17432.576000,594.924895,1.007740,60.001000,1280.739014,321.283423,12040984064,0,0,5.820870,5.861784,2182.430398,242.914298,8386,3226075,6921792,3.145577,3.145577
wbuffix,8k,8k,2,416.881836,53360.951873,24.429962,2.178516,598.450812,134.144000,15400.960000,17432.576000,599.455898,1.005086,60.008000,1280.977441,320.808276,12040984064,0,0,5.820506,5.861485,2182.559659,238.763950,8200,3202084,6755371,3.109680,3.109680
wbuffix,8k,16k,1,436.773438,27953.540302,25.596069,2.282502,1143.267720,224.256000,17432.576000,18219.008000,1144.501621,1.233901,60.009000,1285.493408,323.145312,12040984064,0,0,5.777140,5.777967,2200.559659,258.866023,9296,3354928,7724494,3.302432,3.302432
wbuffix,8k,16k,2,439.053711,28099.465009,25.726257,2.294111,1137.325377,224.256000,17432.576000,18219.008000,1138.557584,1.232207,60.001000,1285.867090,332.904102,12040984064,0,0,5.776931,5.777752,2200.653409,261.982413,9408,3371992,7822172,3.319748,3.319748
wbuffix,8k,32k,1,482.357422,15435.465058,28.269775,2.520927,2071.253005,444.416000,18219.008000,19005.440000,2072.892232,1.639227,60.014000,1290.591992,247.474438,12040984064,0,0,5.696251,5.696408,2217.772727,307.354967,11280,3705376,9405604,3.538367,3.538367
wbuffix,8k,32k,2,482.255859,15432.209463,28.257690,2.519849,2071.673549,444.416000,18219.008000,19005.440000,2073.323787,1.650238,60.001000,1290.951709,242.387354,12040984064,0,0,5.696278,5.696428,2217.772727,306.899740,11280,3703792,9407044,3.539841,3.539841
wbuffix,8k,64k,1,486.363281,7781.821818,28.500732,2.541522,4109.312070,897.024000,19005.440000,19529.728000,4111.893736,2.581666,60.006000,1293.673291,254.507666,12040984064,0,0,5.696513,5.696650,2217.883256,311.709853,11344,3735648,9440736,3.527202,3.527202
wbuffix,8k,64k,2,486.381836,7782.117506,28.505615,2.541958,4109.098033,897.024000,19005.440000,19529.728000,4111.724522,2.626490,60.014000,1293.673291,254.755591,12040984064,0,0,5.697459,5.697600,2217.883256,311.800835,11348,3736288,9444192,3.527694,3.527694
wbuffix,8k,128k,1,496.698242,3973.591256,29.112183,2.596048,8048.369670,1794.048000,20578.304000,38010.880000,8052.750543,4.380873,60.018000,1299.030615,275.050464,12040984064,0,0,5.697016,5.697147,2217.909091,323.134165,11480,3815792,9499936,3.489637,3.489637
wbuffix,8k,128k,2,496.743164,3973.951302,29.107544,2.595634,8047.666258,1794.048000,20316.160000,38010.880000,8052.060539,4.394281,60.003000,1299.012500,274.829297,12040984064,0,0,5.697135,5.697266,2217.909091,323.023536,11476,3815184,9496816,3.489216,3.489216
wbuffix,16k,4k,1,129.925781,33261.045649,7.612976,0.678879,960.999061,254.976000,14090.240000,15400.960000,961.866783,0.867723,60.001000,378.886572,58.637207,12040984064,0,0,5.918050,5.947975,535.561790,89.305176,7091,1995694,2415656,2.210434,8.841727
wbuffix,16k,4k,2,129.686523,33199.993334,7.599762,0.677701,962.760277,254.976000,14090.240000,15269.888000,963.633315,0.873038,60.007000,378.656641,58.252271,12040984064,0,0,5.919572,5.949622,535.568892,88.746712,7056,1992230,2401260,2.205313,8.821242
wbuffix,16k,8k,1,217.569336,27848.970137,12.749947,1.136963,1147.758286,248.832000,16580.608000,17694.720000,1148.815284,1.056998,60.008000,736.346631,81.250806,12040984064,0,0,5.907417,5.974808,1071.127841,131.471294,8120,1671060,3267206,2.955170,5.909982
wbuffix,16k,8k,2,217.999023,27903.989069,12.776413,1.139323,1145.503881,248.832000,16711.680000,17694.720000,1146.550501,1.046620,60.014000,735.950830,81.616895,12040984064,0,0,5.908649,5.976116,1072.026989,131.873468,8170,1674452,3289318,2.964415,5.928199
wbuffix,16k,16k,1,420.718750,26926.004933,24.653137,2.198417,1186.938444,246.784000,16711.680000,17956.864000,1188.179881,1.241437,60.004000,1279.809277,319.462915,12040984064,0,0,5.923905,5.945624,2143.227273,246.928254,8339,1615668,3434109,3.125504,3.125504
wbuffix,16k,16k,2,420.307617,26899.740017,24.629089,2.196273,1188.109951,246.784000,16908.288000,17956.864000,1189.350261,1.240310,60.004000,1279.057812,322.126978,12040984064,0,0,5.924007,5.945738,2143.258523,246.467971,8314,1614092,3422886,3.120626,3.120626
wbuffix,16k,32k,1,439.492188,14063.752854,25.757080,2.296860,2273.445374,464.896000,18219.008000,18743.296000,2275.087219,1.641845,60.013000,1285.834375,327.321289,12040984064,0,0,5.846146,5.867669,2173.096591,264.648688,9350,1688016,3879420,3.298213,3.298213
wbuffix,16k,32k,2,444.887695,14236.425452,26.068542,2.324634,2245.810777,464.896000,18219.008000,18743.296000,2247.495239,1.684462,60.002000,1285.492773,317.069824,12040984064,0,0,5.846779,5.868307,2172.869318,270.532800,9620,1708428,3997122,3.339649,3.339649
wbuffix,16k,64k,1,486.379883,7782.081195,28.500732,2.541522,4109.157031,897.024000,19005.440000,19529.728000,4111.755094,2.598063,60.004000,1293.667041,254.508154,12040984064,0,0,5.696652,5.696773,2217.871893,311.717093,11344,1867824,4720368,3.527202,3.527202
wbuffix,16k,64k,2,486.245117,7779.929343,28.494751,2.540989,4110.299103,897.024000,19005.440000,19529.728000,4112.907009,2.607906,60.008000,1293.673291,254.186914,12040984064,0,0,5.696702,5.696821,2217.883256,311.601912,11344,1867432,4720760,3.527942,3.527942
wbuffix,16k,128k,1,496.937500,3975.506940,29.125732,2.597256,8044.570397,1794.048000,20578.304000,38010.880000,8049.002266,4.431869,60.017000,1299.043408,275.724219,12040984064,0,0,5.693546,5.693662,2217.931818,323.379139,11480,1908784,4749232,3.488093,3.488093
wbuffix,32k,4k,1,68.267578,17476.662612,4.000824,0.356769,1829.778939,569.344000,14483.456000,15400.960000,1830.776979,0.998039,60.011000,189.589893,32.346509,12040984064,0,0,6.066725,6.149273,255.990234,47.426586,7217,1048792,1189155,2.133833,17.070664
wbuffix,32k,8k,1,131.701172,16857.783259,7.717781,0.688225,1896.881530,561.152000,15007.744000,16056.320000,1897.969709,1.088179,60.007000,376.969629,60.144629,12040984064,0,0,6.070340,6.125445,512.569010,89.402118,7315,1011585,1251473,2.237141,8.948563
wbuffix,32k,16k,1,219.313477,14036.065464,12.850830,1.145959,2278.254542,536.576000,17432.576000,17956.864000,2279.563145,1.308603,60.002000,741.204492,81.514575,12040984064,0,0,6.068833,6.105946,1026.572917,129.630760,8250,842179,1660230,2.971351,5.942609
wbuffix,32k,32k,1,424.493164,13583.791621,24.875153,2.218215,2353.817362,528.384000,17694.720000,18219.008000,2355.495204,1.677842,60.006000,1278.334375,322.079028,12040984064,0,0,6.098887,6.143369,2032.770833,245.838234,8401,815109,1725664,3.117096,3.117096
wbuffix,32k,64k,1,446.665039,7146.645112,26.172668,2.333920,4474.704193,978.944000,19005.440000,19791.872000,4477.327461,2.623268,60.002000,1286.819336,318.535962,12040984064,0,0,5.978449,6.000871,2123.535156,277.478695,9540,857626,1974722,3.302544,3.302544
wbuffix,32k,128k,1,496.670898,3973.374211,29.110107,2.595863,8049.000065,1794.048000,20316.160000,38010.880000,8053.293624,4.293558,60.017000,1299.040625,274.962500,12040984064,0,0,5.697746,5.697844,2217.931818,323.071325,11480,953880,2375124,3.489961,3.489961
wbuffix,64k,4k,1,47.053711,12045.792368,2.757523,0.245899,2655.297358,937.984000,11337.728000,11730.944000,2656.258098,0.960740,60.010000,123.588672,24.842725,12040984064,0,0,3.675038,3.715039,219.239955,36.395370,15486,722868,1454598,3.012259,48.196152
wbuffix,64k,8k,1,93.271484,11938.856114,5.465721,0.487400,2678.984933,921.600000,11468.800000,11862.016000,2680.069705,1.084772,60.006000,246.790625,48.139453,12040984064,0,0,3.671269,3.713761,438.600446,71.890565,15563,716403,1470904,3.053180,24.425437
wbuffix,64k,16k,1,175.157227,11210.111480,10.265045,0.915374,2852.966049,937.984000,11862.016000,12124.160000,2854.286160,1.320112,60.011000,488.131250,82.852856,12040984064,0,0,3.674823,3.718097,876.517857,131.745921,15734,672730,1536469,3.283931,13.135725
wbuffix,64k,32k,1,285.618164,9139.800357,16.737427,1.492542,3499.234243,978.944000,12124.160000,12386.304000,3500.922222,1.687979,60.007000,908.028125,143.391040,12040984064,0,0,3.683523,3.719467,1752.214286,194.797791,16146,548451,1713443,4.124150,8.248284
wbuffix,64k,64k,1,645.083008,10321.328578,37.800354,3.370806,3097.577347,880.640000,11993.088000,12386.304000,3100.120742,2.543395,60.004000,1403.947803,518.924536,12040984064,0,0,3.873841,3.946725,3350.386579,477.616375,15930,619321,1614792,3.607359,3.607359
wbuffix,64k,128k,1,665.963867,5327.717509,39.027222,3.480211,6001.688954,1597.440000,22675.456000,24510.464000,6005.981310,4.292356,60.009000,1411.562500,534.134814,12040984064,0,0,3.880566,3.898662,3348.178571,499.885578,16808,639422,1707056,3.669686,3.669686
wbuffix,128k,4k,1,28.133789,7202.426384,1.648697,0.147021,4441.680233,2441.216000,10158.080000,16056.320000,4442.658270,0.978037,60.007000,77.282422,14.416333,12040984064,0,0,2.475650,2.515920,170.169922,23.238997,22262,432196,1090213,3.522497,112.719896
wbuffix,128k,8k,1,56.112305,7182.418132,3.288124,0.293215,4453.994508,2441.216000,10158.080000,16580.608000,4455.064317,1.069809,60.005000,154.100781,28.747534,12040984064,0,0,2.474023,2.514367,340.449219,46.310336,22231,430981,1089448,3.527833,56.445328
wbuffix,128k,16k,1,110.900391,7097.668683,6.499084,0.579549,4506.955227,2506.752000,10289.152000,16056.320000,4508.221410,1.266183,60.009000,307.517187,56.495557,12040984064,0,0,2.476727,2.516406,680.507812,91.271686,22202,425924,1092651,3.565366,28.522929
wbuffix,128k,32k,1,204.968750,6559.014181,12.012115,1.071167,4876.810865,2899.968000,12648.448000,18219.008000,4878.452653,1.641788,60.011000,598.712500,98.130542,12040984064,0,0,2.477408,2.536558,1359.062500,165.200364,22024,393613,1113559,3.829071,15.316283
wbuffix,128k,64k,1,340.655273,5450.488285,19.962280,1.780115,5868.172732,7307.264000,16711.680000,18743.296000,5870.736389,2.563657,60.006000,1051.298486,192.600146,12040984064,0,0,2.474275,2.520778,2716.273682,258.794526,21712,327062,1160138,4.547150,9.094300
wbuffix,128k,128k,1,837.771484,6702.178007,49.095581,4.378046,4770.301241,2244.608000,11337.728000,18219.008000,4774.282822,3.981581,60.009000,1482.975000,671.598682,12040984064,0,0,3.866567,3.895296,3357.214286,681.794248,21413,402191,1065766,3.649900,3.649900
```

### 11.2.5 조합별 집계 전체 (analysis/summary_agg.csv 와 같은 값)
```csv
variant,map,bs,n,bw_MiBps_mean,bw_MiBps_std,bw_MiBps_min,bw_MiBps_max,iops_mean,iops_std,iops_min,iops_max,written_GiB_mean,written_GiB_std,written_GiB_min,written_GiB_max,fill_ratio_mean,fill_ratio_std,fill_ratio_min,fill_ratio_max,clat_mean_us_mean,clat_mean_us_std,clat_mean_us_min,clat_mean_us_max,clat_p50_us_mean,clat_p50_us_std,clat_p50_us_min,clat_p50_us_max,clat_p99_us_mean,clat_p99_us_std,clat_p99_us_min,clat_p99_us_max,clat_p999_us_mean,clat_p999_us_std,clat_p999_us_min,clat_p999_us_max,lat_mean_us_mean,lat_mean_us_std,lat_mean_us_min,lat_mean_us_max,slat_mean_us_mean,slat_mean_us_std,slat_mean_us_min,slat_mean_us_max,runtime_s_mean,runtime_s_std,runtime_s_min,runtime_s_max,bw_first10s_MiBps_mean,bw_first10s_MiBps_std,bw_first10s_MiBps_min,bw_first10s_MiBps_max,bw_last20s_MiBps_mean,bw_last20s_MiBps_std,bw_last20s_MiBps_min,bw_last20s_MiBps_max,chmodel_msgs_mean,chmodel_msgs_std,chmodel_msgs_min,chmodel_msgs_max,kernel_warn_mean,kernel_warn_std,kernel_warn_min,kernel_warn_max,gc_onset_s_mean,gc_onset_s_std,gc_onset_s_min,gc_onset_s_max,gc_onset_last_part_s_mean,gc_onset_last_part_s_std,gc_onset_last_part_s_min,gc_onset_last_part_s_max,bw_pre_gc_MiBps_mean,bw_pre_gc_MiBps_std,bw_pre_gc_MiBps_min,bw_pre_gc_MiBps_max,bw_post_gc_MiBps_mean,bw_post_gc_MiBps_std,bw_post_gc_MiBps_min,bw_post_gc_MiBps_max,gc_cnt_mean,gc_cnt_std,gc_cnt_min,gc_cnt_max,ftl_host_pgs_mean,ftl_host_pgs_std,ftl_host_pgs_min,ftl_host_pgs_max,ftl_gc_pgs_mean,ftl_gc_pgs_std,ftl_gc_pgs_min,ftl_gc_pgs_max,waf_gc_mean,waf_gc_std,waf_gc_min,waf_gc_max,waf_total_mean,waf_total_std,waf_total_min,waf_total_max
base,4k,4k,1,418.395508,0.000000,418.395508,418.395508,107109.381510,0.000000,107109.381510,107109.381510,24.515800,0.000000,24.515800,24.515800,2.186170,0.000000,2.186170,2.186170,297.724553,0.000000,297.724553,297.724553,70.144000,0.000000,70.144000,70.144000,13303.808000,0.000000,13303.808000,13303.808000,17170.432000,0.000000,17170.432000,17170.432000,298.570561,0.000000,298.570561,298.570561,0.846008,0.000000,0.846008,0.846008,60.001000,0.000000,60.001000,60.001000,1273.448535,0.000000,1273.448535,1273.448535,320.739526,0.000000,320.739526,320.739526,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.301980,0.000000,6.301980,6.301980,6.322915,0.000000,6.322915,6.322915,2008.175944,0.000000,2008.175944,2008.175944,241.840956,0.000000,241.840956,241.840956,8345.000000,0.000000,8345,8345,6426670,0.000000,6426670,6426670,13784996,0.000000,13784996,13784996,3.144967,0.000000,3.144967,3.144967,3.144967,0.000000,3.144967,3.144967
base,4k,8k,1,433.589844,0.000000,433.589844,433.589844,55499.541735,0.000000,55499.541735,55499.541735,25.409485,0.000000,25.409485,25.409485,2.265864,0.000000,2.265864,2.265864,575.365254,0.000000,575.365254,575.365254,120.320000,0.000000,120.320000,120.320000,16449.536000,0.000000,16449.536000,16449.536000,17956.864000,0.000000,17956.864000,17956.864000,576.359217,0.000000,576.359217,576.359217,0.993962,0.000000,0.993962,0.993962,60.009000,0.000000,60.009000,60.009000,1285.085596,0.000000,1285.085596,1285.085596,321.294507,0.000000,321.294507,321.294507,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.745002,0.000000,5.745002,5.745002,5.764206,0.000000,5.764206,5.764206,2211.019886,0.000000,2211.019886,2211.019886,254.313055,0.000000,254.313055,254.313055,9182.000000,0.000000,9182,9182,6660944,0.000000,6660944,6660944,15264468,0.000000,15264468,15264468,3.291637,0.000000,3.291637,3.291637,3.291637,0.000000,3.291637,3.291637
base,4k,16k,1,480.927734,0.000000,480.927734,480.927734,30779.394364,0.000000,30779.394364,30779.394364,28.180786,0.000000,28.180786,28.180786,2.512991,0.000000,2.512991,2.512991,1038.183234,0.000000,1038.183234,1038.183234,222.208000,0.000000,222.208000,222.208000,17694.720000,0.000000,17694.720000,17694.720000,18481.152000,0.000000,18481.152000,18481.152000,1039.409494,0.000000,1039.409494,1039.409494,1.226260,0.000000,1.226260,1.226260,60.003000,0.000000,60.003000,60.003000,1288.663867,0.000000,1288.663867,1288.663867,244.568652,0.000000,244.568652,244.568652,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.697114,0.000000,5.697114,5.697114,5.697334,0.000000,5.697334,5.697334,2217.721591,0.000000,2217.721591,2217.721591,305.714252,0.000000,305.714252,305.714252,11272.000000,0.000000,11272,11272,7387424,0.000000,7387424,7387424,18818284,0.000000,18818284,18818284,3.547340,0.000000,3.547340,3.547340,3.547340,0.000000,3.547340,3.547340
base,4k,32k,1,482.594727,0.000000,482.594727,482.594727,15443.059282,0.000000,15443.059282,15443.059282,28.277557,0.000000,28.277557,28.277557,2.521621,0.000000,2.521621,2.521621,2070.201866,0.000000,2070.201866,2070.201866,444.416000,0.000000,444.416000,444.416000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2071.862536,0.000000,2071.862536,2071.862536,1.660670,0.000000,1.660670,1.660670,60.001000,0.000000,60.001000,60.001000,1290.946875,0.000000,1290.946875,1290.946875,243.187158,0.000000,243.187158,243.187158,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.696309,0.000000,5.696309,5.696309,5.696514,0.000000,5.696514,5.696514,2217.767045,0.000000,2217.767045,2217.767045,307.250678,0.000000,307.250678,307.250678,11280.000000,0.000000,11280,11280,7412792,0.000000,7412792,7412792,18808928,0.000000,18808928,18808928,3.537361,0.000000,3.537361,3.537361,3.537361,0.000000,3.537361,3.537361
base,4k,64k,1,486.360352,0.000000,486.360352,486.360352,7781.766068,0.000000,7781.766068,7781.766068,28.501953,0.000000,28.501953,28.501953,2.541631,0.000000,2.541631,2.541631,4109.243368,0.000000,4109.243368,4109.243368,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4111.872378,0.000000,4111.872378,4111.872378,2.629010,0.000000,2.629010,2.629010,60.009000,0.000000,60.009000,60.009000,1293.673291,0.000000,1293.673291,1293.673291,254.762256,0.000000,254.762256,254.762256,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.697804,0.000000,5.697804,5.697804,5.697992,0.000000,5.697992,5.697992,2217.883256,0.000000,2217.883256,2217.883256,311.736669,0.000000,311.736669,311.736669,11344.000000,0.000000,11344,11344,7471616,0.000000,7471616,7471616,18881152,0.000000,18881152,18881152,3.527051,0.000000,3.527051,3.527051,3.527051,0.000000,3.527051,3.527051
base,4k,128k,1,496.773438,0.000000,496.773438,496.773438,3974.190646,0.000000,3974.190646,3974.190646,29.116089,0.000000,29.116089,29.116089,2.596396,0.000000,2.596396,2.596396,8047.197067,0.000000,8047.197067,8047.197067,1794.048000,0.000000,1794.048000,1794.048000,20578.304000,0.000000,20578.304000,20578.304000,38010.880000,0.000000,38010.880000,38010.880000,8051.636637,0.000000,8051.636637,8051.636637,4.439570,0.000000,4.439570,4.439570,60.017000,0.000000,60.017000,60.017000,1299.198340,0.000000,1299.198340,1299.198340,275.072583,0.000000,275.072583,275.072583,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.698692,0.000000,5.698692,5.698692,5.698875,0.000000,5.698875,5.698875,2218.337891,0.000000,2218.337891,2218.337891,323.184606,0.000000,323.184606,323.184606,11480.000000,0.000000,11480,11480,7632608,0.000000,7632608,7632608,18999456,0.000000,18999456,18999456,3.489248,0.000000,3.489248,3.489248,3.489248,0.000000,3.489248,3.489248
base,8k,4k,1,266.393555,0.000000,266.393555,266.393555,68196.973485,0.000000,68196.973485,68196.973485,15.609829,0.000000,15.609829,15.609829,1.391990,0.000000,1.391990,1.391990,467.306883,0.000000,467.306883,467.306883,342.016000,0.000000,342.016000,342.016000,2473.984000,0.000000,2473.984000,2473.984000,3457.024000,0.000000,3457.024000,3457.024000,469.000362,0.000000,469.000362,469.000362,1.693479,0.000000,1.693479,1.693479,60.003000,0.000000,60.003000,60.003000,814.962646,0.000000,814.962646,814.962646,131.899951,0.000000,131.899951,131.899951,8242206,0.000000,8242206,8242206,1.000000,0.000000,1,1,5.685446,0.000000,5.685446,5.685446,5.690782,0.000000,5.690782,5.690782,1115.468040,0.000000,1115.468040,1115.468040,181.224546,0.000000,181.224546,181.224546,14444.000000,0.000000,14444,14444,4091942,0.000000,4091942,4091942,12260041,0.000000,12260041,12260041,3.996142,0.000000,3.996142,3.996142,7.992127,0.000000,7.992127,7.992127
base,8k,8k,1,420.125000,0.000000,420.125000,420.125000,53776.037066,0.000000,53776.037066,53776.037066,24.617126,0.000000,24.617126,24.617126,2.195206,0.000000,2.195206,2.195206,593.817559,0.000000,593.817559,593.817559,132.096000,0.000000,132.096000,132.096000,15532.032000,0.000000,15532.032000,15532.032000,17432.576000,0.000000,17432.576000,17432.576000,594.825788,0.000000,594.825788,594.825788,1.008229,0.000000,1.008229,1.008229,60.001000,0.000000,60.001000,60.001000,1282.384033,0.000000,1282.384033,1282.384033,323.431494,0.000000,323.431494,323.431494,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.820556,0.000000,5.820556,5.820556,5.861563,0.000000,5.861563,5.861563,2180.882369,0.000000,2180.882369,2180.882369,243.286341,0.000000,243.286341,243.286341,8386.000000,0.000000,8386,8386,3226616,0.000000,3226616,3226616,6921205,0.000000,6921205,6921205,3.145035,0.000000,3.145035,3.145035,3.145035,0.000000,3.145035,3.145035
base,8k,16k,1,440.075195,0.000000,440.075195,440.075195,28164.830586,0.000000,28164.830586,28164.830586,25.786102,0.000000,25.786102,25.786102,2.299448,0.000000,2.299448,2.299448,1134.696490,0.000000,1134.696490,1134.696490,224.256000,0.000000,224.256000,224.256000,17432.576000,0.000000,17432.576000,17432.576000,18481.152000,0.000000,18481.152000,18481.152000,1135.911940,0.000000,1135.911940,1135.911940,1.215451,0.000000,1.215451,1.215451,60.001000,0.000000,60.001000,60.001000,1285.950635,0.000000,1285.950635,1285.950635,320.270410,0.000000,320.270410,320.270410,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.781899,0.000000,5.781899,5.781899,5.782728,0.000000,5.782728,5.782728,2198.647727,0.000000,2198.647727,2198.647727,263.452582,0.000000,263.452582,263.452582,9460.000000,0.000000,9460,9460,3379836,0.000000,3379836,3379836,7867608,0.000000,7867608,7867608,3.327808,0.000000,3.327808,3.327808,3.327808,0.000000,3.327808,3.327808
base,8k,32k,1,482.244141,0.000000,482.244141,482.244141,15431.837877,0.000000,15431.837877,15431.837877,28.258423,0.000000,28.258423,28.258423,2.519915,0.000000,2.519915,2.519915,2071.723042,0.000000,2071.723042,2071.723042,444.416000,0.000000,444.416000,444.416000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2073.363979,0.000000,2073.363979,2073.363979,1.640937,0.000000,1.640937,1.640937,60.004000,0.000000,60.004000,60.004000,1290.967676,0.000000,1290.967676,1290.967676,246.913477,0.000000,246.913477,246.913477,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.696200,0.000000,5.696200,5.696200,5.696348,0.000000,5.696348,5.696348,2217.772727,0.000000,2217.772727,2217.772727,307.144173,0.000000,307.144173,307.144173,11276.000000,0.000000,11276,11276,3703888,0.000000,3703888,3703888,9402992,0.000000,9402992,9402992,3.538682,0.000000,3.538682,3.538682,3.538682,0.000000,3.538682,3.538682
base,8k,64k,1,486.371094,0.000000,486.371094,486.371094,7781.951504,0.000000,7781.951504,7781.951504,28.500732,0.000000,28.500732,28.500732,2.541522,0.000000,2.541522,2.541522,4109.183074,0.000000,4109.183074,4109.183074,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4111.808720,0.000000,4111.808720,4111.808720,2.625646,0.000000,2.625646,2.625646,60.005000,0.000000,60.005000,60.005000,1293.672510,0.000000,1293.672510,1293.672510,254.503271,0.000000,254.503271,254.503271,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.698415,0.000000,5.698415,5.698415,5.698556,0.000000,5.698556,5.698556,2217.881836,0.000000,2217.881836,2217.881836,311.705705,0.000000,311.705705,311.705705,11344.000000,0.000000,11344,11344,3735648,0.000000,3735648,3735648,9440736,0.000000,9440736,9440736,3.527202,0.000000,3.527202,3.527202,3.527202,0.000000,3.527202,3.527202
base,8k,128k,1,497.387695,0.000000,497.387695,497.387695,3979.102786,0.000000,3979.102786,3979.102786,29.147705,0.000000,29.147705,29.147705,2.599215,0.000000,2.599215,2.599215,8037.267831,0.000000,8037.267831,8037.267831,1794.048000,0.000000,1794.048000,1794.048000,20316.160000,0.000000,20316.160000,20316.160000,38010.880000,0.000000,38010.880000,38010.880000,8041.648308,0.000000,8041.648308,8041.648308,4.380477,0.000000,4.380477,4.380477,60.008000,0.000000,60.008000,60.008000,1299.041748,0.000000,1299.041748,1299.041748,276.862988,0.000000,276.862988,276.862988,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.698204,0.000000,5.698204,5.698204,5.698335,0.000000,5.698335,5.698335,2217.909091,0.000000,2217.909091,2217.909091,323.793972,0.000000,323.793972,323.793972,11480.000000,0.000000,11480,11480,3820448,0.000000,3820448,3820448,9495600,0.000000,9495600,9495600,3.485468,0.000000,3.485468,3.485468,3.485468,0.000000,3.485468,3.485468
base,16k,4k,1,167.852539,0.000000,167.852539,167.852539,42970.417653,0.000000,42970.417653,42970.417653,9.835476,0.000000,9.835476,9.835476,0.877068,0.000000,0.877068,0.877068,742.769526,0.000000,742.769526,742.769526,684.032000,0.000000,684.032000,684.032000,2768.896000,0.000000,2768.896000,2768.896000,3915.776000,0.000000,3915.776000,3915.776000,744.458571,0.000000,744.458571,744.458571,1.689045,0.000000,1.689045,1.689045,60.002000,0.000000,60.002000,60.002000,430.340381,0.000000,430.340381,430.340381,86.196948,0.000000,86.196948,86.196948,6757590,0.000000,6757590,6757590,0.000000,0.000000,0,0,5.668286,0.000000,5.668286,5.668286,5.684406,0.000000,5.684406,5.684406,559.152699,0.000000,559.152699,559.152699,128.884702,0.000000,128.884702,128.884702,14419.000000,0.000000,14419,14419,2578311,0.000000,2578311,2578311,5585060,0.000000,5585060,5585060,3.166170,0.000000,3.166170,3.166170,12.664680,0.000000,12.664680,12.664680
base,16k,8k,1,272.789062,0.000000,272.789062,272.789062,34917.104145,0.000000,34917.104145,34917.104145,15.984581,0.000000,15.984581,15.984581,1.425408,0.000000,1.425408,1.425408,914.358511,0.000000,914.358511,914.358511,692.224000,0.000000,692.224000,692.224000,3162.112000,0.000000,3162.112000,3162.112000,4358.144000,0.000000,4358.144000,4358.144000,916.213581,0.000000,916.213581,916.213581,1.855069,0.000000,1.855069,1.855069,60.003000,0.000000,60.003000,60.003000,822.685986,0.000000,822.685986,822.685986,133.554443,0.000000,133.554443,133.554443,9087642,0.000000,9087642,9087642,1.000000,0.000000,1,1,5.665941,0.000000,5.665941,5.665941,5.697156,0.000000,5.697156,5.697156,1117.981534,0.000000,1117.981534,1117.981534,188.074987,0.000000,188.074987,188.074987,15155.000000,0.000000,15155,15155,2095113,0.000000,2095113,2095113,6444990,0.000000,6444990,6444990,4.076202,0.000000,4.076202,4.076202,8.152333,0.000000,8.152333,8.152333
base,16k,16k,1,420.993164,0.000000,420.993164,420.993164,26943.600940,0.000000,26943.600940,26943.600940,24.668015,0.000000,24.668015,24.668015,2.199744,0.000000,2.199744,2.199744,1186.169263,0.000000,1186.169263,1186.169263,246.784000,0.000000,246.784000,246.784000,16908.288000,0.000000,16908.288000,16908.288000,17956.864000,0.000000,17956.864000,17956.864000,1187.409869,0.000000,1187.409869,1187.409869,1.240606,0.000000,1.240606,1.240606,60.001000,0.000000,60.001000,60.001000,1278.890625,0.000000,1278.890625,1278.890625,322.791333,0.000000,322.791333,322.791333,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.923822,0.000000,5.923822,5.923822,5.945612,0.000000,5.945612,5.945612,2143.227273,0.000000,2143.227273,2143.227273,247.764323,0.000000,247.764323,247.764323,8352.000000,0.000000,8352,8352,1616643,0.000000,1616643,1616643,3439890,0.000000,3439890,3439890,3.127798,0.000000,3.127798,3.127798,3.127798,0.000000,3.127798,3.127798
base,16k,32k,1,443.818359,0.000000,443.818359,443.818359,14202.206005,0.000000,14202.206005,14202.206005,26.012817,0.000000,26.012817,26.012817,2.319665,0.000000,2.319665,2.319665,2251.226353,0.000000,2251.226353,2251.226353,464.896000,0.000000,464.896000,464.896000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2252.890533,0.000000,2252.890533,2252.890533,1.664179,0.000000,1.664179,1.664179,60.018000,0.000000,60.018000,60.018000,1286.221875,0.000000,1286.221875,1286.221875,318.064355,0.000000,318.064355,318.064355,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.846011,0.000000,5.846011,5.846011,5.867525,0.000000,5.867525,5.867525,2173.073864,0.000000,2173.073864,2173.073864,269.453009,0.000000,269.453009,269.453009,9576.000000,0.000000,9576,9576,1704776,0.000000,1704776,1704776,3978204,0.000000,3978204,3978204,3.333564,0.000000,3.333564,3.333564,3.333564,0.000000,3.333564,3.333564
base,16k,64k,1,486.387695,0.000000,486.387695,486.387695,7782.215335,0.000000,7782.215335,7782.215335,28.507874,0.000000,28.507874,28.507874,2.542159,0.000000,2.542159,2.542159,4109.072779,0.000000,4109.072779,4109.072779,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4111.605658,0.000000,4111.605658,4111.605658,2.532879,0.000000,2.532879,2.532879,60.018000,0.000000,60.018000,60.018000,1293.667041,0.000000,1293.667041,1293.667041,254.825732,0.000000,254.825732,254.825732,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.689829,0.000000,5.689829,5.689829,5.689950,0.000000,5.689950,5.689950,2217.871893,0.000000,2217.871893,2217.871893,311.847907,0.000000,311.847907,311.847907,11348.000000,0.000000,11348,11348,1868292,0.000000,1868292,1868292,4721904,0.000000,4721904,4721904,3.527391,0.000000,3.527391,3.527391,3.527391,0.000000,3.527391,3.527391
base,16k,128k,1,496.748047,0.000000,496.748047,496.748047,3973.990703,0.000000,3973.990703,3973.990703,29.114624,0.000000,29.114624,29.114624,2.596265,0.000000,2.596265,2.596265,8047.679688,0.000000,8047.679688,8047.679688,1794.048000,0.000000,1794.048000,1794.048000,20316.160000,0.000000,20316.160000,20316.160000,38010.880000,0.000000,38010.880000,38010.880000,8052.035086,0.000000,8052.035086,8052.035086,4.355398,0.000000,4.355398,4.355398,60.017000,0.000000,60.017000,60.017000,1299.040723,0.000000,1299.040723,1299.040723,275.170215,0.000000,275.170215,275.170215,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.696911,0.000000,5.696911,5.696911,5.697022,0.000000,5.697022,5.697022,2217.931818,0.000000,2217.931818,2217.931818,323.166284,0.000000,323.166284,323.166284,11480.000000,0.000000,11480,11480,1908056,0.000000,1908056,1908056,4749968,0.000000,4749968,4749968,3.489428,0.000000,3.489428,3.489428,3.489428,0.000000,3.489428,3.489428
base,32k,4k,1,92.599609,0.000000,92.599609,92.599609,23705.581388,0.000000,23705.581388,23705.581388,5.426048,0.000000,5.426048,5.426048,0.483862,0.000000,0.483862,0.483862,1347.668431,0.000000,1347.668431,1347.668431,1236.992000,0.000000,1236.992000,1236.992000,3784.704000,0.000000,3784.704000,3784.704000,5079.040000,0.000000,5079.040000,5079.040000,1349.623930,0.000000,1349.623930,1349.623930,1.955499,0.000000,1.955499,1.955499,60.003000,0.000000,60.003000,60.003000,219.731641,0.000000,219.731641,219.731641,49.794604,0.000000,49.794604,49.794604,8233550,0.000000,8233550,8233550,0.000000,0.000000,0,0,5.635585,0.000000,5.635585,5.635585,5.682222,0.000000,5.682222,5.682222,280.504972,0.000000,280.504972,280.504972,73.926803,0.000000,73.926803,73.926803,15473.000000,0.000000,15473,15473,1422406,0.000000,1422406,1422406,2929163,0.000000,2929163,2929163,3.059302,0.000000,3.059302,3.059302,24.474413,0.000000,24.474413,24.474413
base,32k,8k,1,174.001953,0.000000,174.001953,174.001953,22272.277310,0.000000,22272.277310,22272.277310,10.196289,0.000000,10.196289,10.196289,0.909243,0.000000,0.909243,0.909243,1434.271000,0.000000,1434.271000,1434.271000,1236.992000,0.000000,1236.992000,1236.992000,4227.072000,0.000000,4227.072000,4227.072000,5472.256000,0.000000,5472.256000,5472.256000,1436.508133,0.000000,1436.508133,1436.508133,2.237133,0.000000,2.237133,2.237133,60.005000,0.000000,60.005000,60.005000,436.111719,0.000000,436.111719,436.111719,85.395361,0.000000,85.395361,85.395361,8786405,0.000000,8786405,8786405,0.000000,0.000000,0,0,5.638842,0.000000,5.638842,5.638842,5.672789,0.000000,5.672789,5.672789,561.262784,0.000000,561.262784,561.262784,135.522262,0.000000,135.522262,135.522262,15691.000000,0.000000,15691,15691,1336448,0.000000,1336448,1336448,3070857,0.000000,3070857,3070857,3.297775,0.000000,3.297775,3.297775,13.191101,0.000000,13.191101,13.191101
wbuffix,4k,4k,2,418.566895,1.318229,417.634766,419.499023,107153.202104,337.477445,106914.569514,107391.834694,24.527878,0.079562,24.471619,24.584137,2.187247,0.007095,2.182230,2.192264,297.612042,0.944005,296.944530,298.279554,69.120000,0.000000,69.120000,69.120000,13500.416000,92.681900,13434.880000,13565.952000,17039.360000,185.363800,16908.288000,17170.432000,298.454497,0.940436,297.789508,299.119485,0.842455,0.003569,0.839931,0.844979,60.006000,0.005657,60.002000,60.010000,1273.019897,0.245727,1272.846143,1273.193652,325.297424,2.058844,323.841602,326.753247,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.304073,0.003300,6.301740,6.306407,6.324868,0.003430,6.322443,6.327294,2007.668660,0.663776,2007.199300,2008.138021,242.097087,1.600351,240.965468,243.228706,8359.000000,83.438600,8300,8418,6429836,20856.821618,6415088,6444584,13810204,150179.580829,13704011,13916397,3.147805,0.016390,3.136216,3.159394,3.147805,0.016390,3.136216,3.159394
wbuffix,4k,8k,2,438.651367,0.917029,438.002930,439.299805,56147.403956,117.363269,56064.415593,56230.392320,25.702885,0.054029,25.664680,25.741089,2.292027,0.004818,2.288620,2.295434,568.705911,1.167101,567.880647,569.531176,121.344000,0.000000,121.344000,121.344000,16580.608000,0.000000,16580.608000,16580.608000,17825.792000,185.363800,17694.720000,17956.864000,569.704609,1.190875,568.862533,570.546685,0.998698,0.023775,0.981886,1.015509,60.001500,0.000707,60.001000,60.002000,1285.448120,0.532505,1285.071582,1285.824658,324.747717,5.081035,321.154883,328.340552,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.744727,0.002139,5.743215,5.746240,5.763647,0.002300,5.762021,5.765273,2211.019176,0.005022,2211.015625,2211.022727,259.910149,0.886238,259.283483,260.536814,9436.000000,45.254834,9404,9468,6737857,14163.348827,6727842,6747872,15708119,78713.712668,15652460,15763778,3.331316,0.006782,3.326520,3.336111,3.331316,0.006782,3.326520,3.336111
wbuffix,4k,16k,2,480.902344,0.012430,480.893555,480.911133,30777.764855,0.780266,30777.213123,30778.316586,28.183990,0.001942,28.182617,28.185364,2.513277,0.000173,2.513155,2.513400,1038.234269,0.016102,1038.222883,1038.245655,222.208000,0.000000,222.208000,222.208000,17694.720000,0.000000,17694.720000,17694.720000,18481.152000,0.000000,18481.152000,18481.152000,1039.452848,0.022058,1039.437250,1039.468445,1.218579,0.005956,1.214367,1.222790,60.013000,0.005657,60.009000,60.017000,1288.553345,0.107274,1288.477490,1288.629199,244.722778,0.162034,244.608203,244.837354,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.693237,0.004060,5.690366,5.696107,5.693454,0.004061,5.690582,5.696325,2217.943093,0.297181,2217.732955,2218.153232,305.752992,0.038493,305.725774,305.780211,11272.000000,0.000000,11272,11272,7388264,509.116882,7387904,7388624,18817590,517.602164,18817224,18817956,3.546957,0.000246,3.546783,3.547131,3.546957,0.000246,3.546783,3.547131
wbuffix,4k,32k,2,482.330566,0.069744,482.281250,482.379883,15434.597140,2.233436,15433.017862,15436.176417,28.269363,0.004424,28.266235,28.272491,2.520890,0.000394,2.520611,2.521169,2071.345805,0.295171,2071.137088,2071.554523,444.416000,0.000000,444.416000,444.416000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2072.996749,0.310751,2072.777015,2073.216483,1.650944,0.015580,1.639927,1.661960,60.016500,0.000707,60.016000,60.017000,1290.894775,0.089838,1290.831250,1290.958301,247.458472,0.241790,247.287500,247.629443,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.696096,0.000116,5.696014,5.696178,5.696296,0.000110,5.696219,5.696374,2217.769886,0.004018,2217.767045,2217.772727,307.361615,0.070625,307.311676,307.411554,11278.000000,2.828427,11276,11280,7410644,1159.655121,7409824,7411464,18807072,4491.542274,18803896,18810248,3.537846,0.000209,3.537698,3.537994,3.537846,0.000209,3.537698,3.537994
wbuffix,4k,64k,2,486.267578,0.001381,486.266602,486.268555,7780.292111,0.026154,7780.273617,7780.310605,28.497742,0.000432,28.497437,28.498047,2.541256,0.000038,2.541228,2.541283,4110.089656,0.022733,4110.073581,4110.105730,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4112.691650,0.013877,4112.681837,4112.701463,2.601995,0.008856,2.595732,2.608257,60.011500,0.000707,60.011000,60.012000,1293.670166,0.004419,1293.667041,1293.673291,254.340320,0.022391,254.324487,254.356152,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.693339,0.004555,5.690118,5.696560,5.693526,0.004556,5.690304,5.696747,2217.877575,0.008035,2217.871893,2217.883256,311.647689,0.013906,311.637857,311.657522,11344.000000,0.000000,11344,11344,7470512,113.137085,7470432,7470592,18882280,124.450793,18882192,18882368,3.527575,0.000055,3.527536,3.527614,3.527575,0.000055,3.527536,3.527614
wbuffix,4k,128k,2,496.841797,0.013811,496.832031,496.851562,3974.738394,0.114256,3974.657603,3974.819185,29.117676,0.003280,29.115356,29.119995,2.596537,0.000292,2.596331,2.596744,8046.083134,0.151007,8045.976356,8046.189912,1794.048000,0.000000,1794.048000,1794.048000,20447.232000,185.363800,20316.160000,20578.304000,38010.880000,0.000000,38010.880000,38010.880000,8050.472967,0.122731,8050.386183,8050.559751,4.389833,0.028276,4.369839,4.409827,60.012000,0.008485,60.006000,60.018000,1299.041968,0.001623,1299.040820,1299.043115,275.506189,0.088060,275.443921,275.568457,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.697336,0.000065,5.697290,5.697382,5.697516,0.000066,5.697469,5.697563,2217.931818,0.000000,2217.931818,2217.931818,323.220923,0.069148,323.172027,323.269818,11478.000000,2.828427,11476,11480,7633024,859.841846,7632416,7633632,18994496,4253.954396,18991488,18997504,3.488463,0.000277,3.488267,3.488659,3.488463,0.000277,3.488267,3.488659
wbuffix,8k,4k,2,216.666992,0.078721,216.611328,216.722656,55466.934839,20.091933,55452.727697,55481.141981,12.696960,0.002654,12.695084,12.698837,1.132238,0.000237,1.132070,1.132405,575.863491,0.209644,575.715251,576.011732,151.552000,1.448155,150.528000,152.576000,15007.744000,0.000000,15007.744000,15007.744000,17170.432000,0.000000,17170.432000,17170.432000,576.712146,0.212951,576.561567,576.862725,0.848655,0.003307,0.846317,0.850994,60.007500,0.009192,60.001000,60.014000,736.912109,0.314469,736.689746,737.134473,81.552075,0.580359,81.141699,81.962451,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.813959,0.004670,5.810656,5.817261,5.833962,0.004606,5.830705,5.837219,1091.776634,0.023604,1091.759943,1091.793324,128.590204,0.327265,128.358793,128.821615,8049.500000,2.121320,8048,8051,3327576,724.077344,3327064,3328088,6476546,1402.899854,6475554,6477538,2.946325,0.000002,2.946324,2.946327,5.891136,0.000047,5.891103,5.891168
wbuffix,8k,8k,2,418.468262,2.243545,416.881836,420.054688,53563.986211,287.133915,53360.951873,53767.020550,24.521481,0.129427,24.429962,24.612999,2.186677,0.011541,2.178516,2.194838,596.183983,3.205780,593.917154,598.450812,133.120000,1.448155,132.096000,134.144000,15400.960000,0.000000,15400.960000,15400.960000,17432.576000,0.000000,17432.576000,17432.576000,597.190396,3.203903,594.924895,599.455898,1.006413,0.001877,1.005086,1.007740,60.004500,0.004950,60.001000,60.008000,1280.858228,0.168594,1280.739014,1280.977441,321.045850,0.335979,320.808276,321.283423,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.820688,0.000257,5.820506,5.820870,5.861635,0.000211,5.861485,5.861784,2182.495028,0.091402,2182.430398,2182.559659,240.839124,2.934739,238.763950,242.914298,8293.000000,131.521861,8200,8386,3214080,16964.198787,3202084,3226075,6838582,117677.417632,6755371,6921792,3.127628,0.025383,3.109680,3.145577,3.127628,0.025383,3.109680,3.145577
wbuffix,8k,16k,2,437.913574,1.612397,436.773438,439.053711,28026.502656,103.184350,27953.540302,28099.465009,25.661163,0.092057,25.596069,25.726257,2.288307,0.008209,2.282502,2.294111,1140.296549,4.201871,1137.325377,1143.267720,224.256000,0.000000,224.256000,224.256000,17432.576000,0.000000,17432.576000,17432.576000,18219.008000,0.000000,18219.008000,18219.008000,1141.529602,4.203069,1138.557584,1144.501621,1.233054,0.001198,1.232207,1.233901,60.005000,0.005657,60.001000,60.009000,1285.680249,0.264233,1285.493408,1285.867090,328.024707,6.900506,323.145312,332.904102,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.777035,0.000148,5.776931,5.777140,5.777860,0.000152,5.777752,5.777967,2200.606534,0.066291,2200.559659,2200.653409,260.424218,2.203621,258.866023,261.982413,9352.000000,79.195959,9296,9408,3363460,12066.070114,3354928,3371992,7773333,69068.776173,7724494,7822172,3.311090,0.012244,3.302432,3.319748,3.311090,0.012244,3.302432,3.319748
wbuffix,8k,32k,2,482.306641,0.071816,482.255859,482.357422,15433.837261,2.302053,15432.209463,15435.465058,28.263733,0.008545,28.257690,28.269775,2.520388,0.000762,2.519849,2.520927,2071.463277,0.297370,2071.253005,2071.673549,444.416000,0.000000,444.416000,444.416000,18219.008000,0.000000,18219.008000,18219.008000,19005.440000,0.000000,19005.440000,19005.440000,2073.108010,0.305155,2072.892232,2073.323787,1.644732,0.007786,1.639227,1.650238,60.007500,0.009192,60.001000,60.014000,1290.771851,0.254358,1290.591992,1290.951709,244.930896,3.597112,242.387354,247.474438,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.696265,0.000019,5.696251,5.696278,5.696418,0.000014,5.696408,5.696428,2217.772727,0.000000,2217.772727,2217.772727,307.127353,0.321894,306.899740,307.354967,11280.000000,0.000000,11280,11280,3704584,1120.057141,3703792,3705376,9406324,1018.233765,9405604,9407044,3.539104,0.001043,3.538367,3.539841,3.539104,0.001043,3.538367,3.539841
wbuffix,8k,64k,2,486.372559,0.013120,486.363281,486.381836,7781.969662,0.209083,7781.821818,7782.117506,28.503174,0.003453,28.500732,28.505615,2.541740,0.000308,2.541522,2.541958,4109.205051,0.151347,4109.098033,4109.312070,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4111.809129,0.119652,4111.724522,4111.893736,2.604078,0.031695,2.581666,2.626490,60.010000,0.005657,60.006000,60.014000,1293.673291,0.000000,1293.673291,1293.673291,254.631628,0.175309,254.507666,254.755591,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.696986,0.000669,5.696513,5.697459,5.697125,0.000672,5.696650,5.697600,2217.883256,0.000000,2217.883256,2217.883256,311.755344,0.064334,311.709853,311.800835,11346.000000,2.828427,11344,11348,3735968,452.548340,3735648,3736288,9442464,2443.761036,9440736,9444192,3.527448,0.000348,3.527202,3.527694,3.527448,0.000348,3.527202,3.527694
wbuffix,8k,128k,2,496.720703,0.031765,496.698242,496.743164,3973.771279,0.254591,3973.591256,3973.951302,29.109863,0.003280,29.107544,29.112183,2.595841,0.000292,2.595634,2.596048,8048.017964,0.497388,8047.666258,8048.369670,1794.048000,0.000000,1794.048000,1794.048000,20447.232000,185.363800,20316.160000,20578.304000,38010.880000,0.000000,38010.880000,38010.880000,8052.405541,0.487907,8052.060539,8052.750543,4.387577,0.009481,4.380873,4.394281,60.010500,0.010607,60.003000,60.018000,1299.021558,0.012809,1299.012500,1299.030615,274.939880,0.156389,274.829297,275.050464,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.697075,0.000084,5.697016,5.697135,5.697207,0.000084,5.697147,5.697266,2217.909091,0.000000,2217.909091,2217.909091,323.078851,0.078227,323.023536,323.134165,11478.000000,2.828427,11476,11480,3815488,429.920923,3815184,3815792,9498376,2206.173157,9496816,9499936,3.489426,0.000298,3.489216,3.489637,3.489426,0.000298,3.489216,3.489637
wbuffix,16k,4k,2,129.806152,0.169181,129.686523,129.925781,33230.519492,43.170506,33199.993334,33261.045649,7.606369,0.009344,7.599762,7.612976,0.678290,0.000833,0.677701,0.678879,961.879669,1.245368,960.999061,962.760277,254.976000,0.000000,254.976000,254.976000,14090.240000,0.000000,14090.240000,14090.240000,15335.424000,92.681900,15269.888000,15400.960000,962.750049,1.249126,961.866783,963.633315,0.870380,0.003759,0.867723,0.873038,60.004000,0.004243,60.001000,60.007000,378.771606,0.162586,378.656641,378.886572,58.444739,0.272191,58.252271,58.637207,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.918811,0.001076,5.918050,5.919572,5.948798,0.001165,5.947975,5.949622,535.565341,0.005022,535.561790,535.568892,89.025944,0.394894,88.746712,89.305176,7073.500000,24.748737,7056,7091,1993962,2449.417890,1992230,1995694,2408458,10179.509222,2401260,2415656,2.207873,0.003621,2.205313,2.210434,8.831485,0.014486,8.821242,8.841727
wbuffix,16k,8k,2,217.784180,0.303835,217.569336,217.999023,27876.479603,38.904260,27848.970137,27903.989069,12.763180,0.018715,12.749947,12.776413,1.138143,0.001669,1.136963,1.139323,1146.631083,1.594105,1145.503881,1147.758286,248.832000,0.000000,248.832000,248.832000,16646.144000,92.681900,16580.608000,16711.680000,17694.720000,0.000000,17694.720000,17694.720000,1147.682892,1.601443,1146.550501,1148.815284,1.051809,0.007338,1.046620,1.056998,60.011000,0.004243,60.008000,60.014000,736.148730,0.279873,735.950830,736.346631,81.433850,0.258864,81.250806,81.616895,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.908033,0.000871,5.907417,5.908649,5.975462,0.000925,5.974808,5.976116,1071.577415,0.635793,1071.127841,1072.026989,131.672381,0.284380,131.471294,131.873468,8145.000000,35.355339,8120,8170,1672756,2398.506202,1671060,1674452,3278262,15635.545146,3267206,3289318,2.959792,0.006537,2.955170,2.964415,5.919091,0.012881,5.909982,5.928199
wbuffix,16k,16k,2,420.513184,0.290715,420.307617,420.718750,26912.872475,18.572100,26899.740017,26926.004933,24.641113,0.017004,24.629089,24.653137,2.197345,0.001516,2.196273,2.198417,1187.524197,0.828381,1186.938444,1188.109951,246.784000,0.000000,246.784000,246.784000,16809.984000,139.022850,16711.680000,16908.288000,17956.864000,0.000000,17956.864000,17956.864000,1188.765071,0.827584,1188.179881,1189.350261,1.240874,0.000797,1.240310,1.241437,60.004000,0.000000,60.004000,60.004000,1279.433545,0.531366,1279.057812,1279.809277,320.794946,1.883777,319.462915,322.126978,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.923956,0.000072,5.923905,5.924007,5.945681,0.000081,5.945624,5.945738,2143.242898,0.022097,2143.227273,2143.258523,246.698112,0.325470,246.467971,246.928254,8326.500000,17.677670,8314,8339,1614880,1114.400287,1614092,1615668,3428498,7935.859405,3422886,3434109,3.123065,0.003449,3.120626,3.125504,3.123065,0.003449,3.120626,3.125504
wbuffix,16k,32k,2,442.189941,3.815200,439.492188,444.887695,14150.089153,122.097965,14063.752854,14236.425452,25.912811,0.220237,25.757080,26.068542,2.310747,0.019639,2.296860,2.324634,2259.628076,19.540611,2245.810777,2273.445374,464.896000,0.000000,464.896000,464.896000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2261.291229,19.510476,2247.495239,2275.087219,1.663153,0.030135,1.641845,1.684462,60.007500,0.007778,60.002000,60.013000,1285.663574,0.241549,1285.492773,1285.834375,322.195557,7.248880,317.069824,327.321289,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.846462,0.000448,5.846146,5.846779,5.867988,0.000451,5.867669,5.868307,2172.982955,0.160706,2172.869318,2173.096591,267.590744,4.160695,264.648688,270.532800,9485.000000,190.918831,9350,9620,1698222,14433.463618,1688016,1708428,3938271,83227.882359,3879420,3997122,3.318931,0.029300,3.298213,3.339649,3.318931,0.029300,3.298213,3.339649
wbuffix,16k,64k,2,486.312500,0.095294,486.245117,486.379883,7781.005269,1.521589,7779.929343,7782.081195,28.497742,0.004230,28.494751,28.500732,2.541256,0.000377,2.540989,2.541522,4109.728067,0.807567,4109.157031,4110.299103,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4112.331051,0.814527,4111.755094,4112.907009,2.602985,0.006960,2.598063,2.607906,60.006000,0.002828,60.004000,60.008000,1293.670166,0.004419,1293.667041,1293.673291,254.347534,0.227151,254.186914,254.508154,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.696677,0.000035,5.696652,5.696702,5.696797,0.000034,5.696773,5.696821,2217.877575,0.008035,2217.871893,2217.883256,311.659502,0.081445,311.601912,311.717093,11344.000000,0.000000,11344,11344,1867628,277.185858,1867432,1867824,4720564,277.185858,4720368,4720760,3.527572,0.000524,3.527202,3.527942,3.527572,0.000524,3.527202,3.527942
wbuffix,16k,128k,1,496.937500,0.000000,496.937500,496.937500,3975.506940,0.000000,3975.506940,3975.506940,29.125732,0.000000,29.125732,29.125732,2.597256,0.000000,2.597256,2.597256,8044.570397,0.000000,8044.570397,8044.570397,1794.048000,0.000000,1794.048000,1794.048000,20578.304000,0.000000,20578.304000,20578.304000,38010.880000,0.000000,38010.880000,38010.880000,8049.002266,0.000000,8049.002266,8049.002266,4.431869,0.000000,4.431869,4.431869,60.017000,0.000000,60.017000,60.017000,1299.043408,0.000000,1299.043408,1299.043408,275.724219,0.000000,275.724219,275.724219,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.693546,0.000000,5.693546,5.693546,5.693662,0.000000,5.693662,5.693662,2217.931818,0.000000,2217.931818,2217.931818,323.379139,0.000000,323.379139,323.379139,11480.000000,0.000000,11480,11480,1908784,0.000000,1908784,1908784,4749232,0.000000,4749232,4749232,3.488093,0.000000,3.488093,3.488093,3.488093,0.000000,3.488093,3.488093
wbuffix,32k,4k,1,68.267578,0.000000,68.267578,68.267578,17476.662612,0.000000,17476.662612,17476.662612,4.000824,0.000000,4.000824,4.000824,0.356769,0.000000,0.356769,0.356769,1829.778939,0.000000,1829.778939,1829.778939,569.344000,0.000000,569.344000,569.344000,14483.456000,0.000000,14483.456000,14483.456000,15400.960000,0.000000,15400.960000,15400.960000,1830.776979,0.000000,1830.776979,1830.776979,0.998039,0.000000,0.998039,0.998039,60.011000,0.000000,60.011000,60.011000,189.589893,0.000000,189.589893,189.589893,32.346509,0.000000,32.346509,32.346509,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.066725,0.000000,6.066725,6.066725,6.149273,0.000000,6.149273,6.149273,255.990234,0.000000,255.990234,255.990234,47.426586,0.000000,47.426586,47.426586,7217.000000,0.000000,7217,7217,1048792,0.000000,1048792,1048792,1189155,0.000000,1189155,1189155,2.133833,0.000000,2.133833,2.133833,17.070664,0.000000,17.070664,17.070664
wbuffix,32k,8k,1,131.701172,0.000000,131.701172,131.701172,16857.783259,0.000000,16857.783259,16857.783259,7.717781,0.000000,7.717781,7.717781,0.688225,0.000000,0.688225,0.688225,1896.881530,0.000000,1896.881530,1896.881530,561.152000,0.000000,561.152000,561.152000,15007.744000,0.000000,15007.744000,15007.744000,16056.320000,0.000000,16056.320000,16056.320000,1897.969709,0.000000,1897.969709,1897.969709,1.088179,0.000000,1.088179,1.088179,60.007000,0.000000,60.007000,60.007000,376.969629,0.000000,376.969629,376.969629,60.144629,0.000000,60.144629,60.144629,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.070340,0.000000,6.070340,6.070340,6.125445,0.000000,6.125445,6.125445,512.569010,0.000000,512.569010,512.569010,89.402118,0.000000,89.402118,89.402118,7315.000000,0.000000,7315,7315,1011585,0.000000,1011585,1011585,1251473,0.000000,1251473,1251473,2.237141,0.000000,2.237141,2.237141,8.948563,0.000000,8.948563,8.948563
wbuffix,32k,16k,1,219.313477,0.000000,219.313477,219.313477,14036.065464,0.000000,14036.065464,14036.065464,12.850830,0.000000,12.850830,12.850830,1.145959,0.000000,1.145959,1.145959,2278.254542,0.000000,2278.254542,2278.254542,536.576000,0.000000,536.576000,536.576000,17432.576000,0.000000,17432.576000,17432.576000,17956.864000,0.000000,17956.864000,17956.864000,2279.563145,0.000000,2279.563145,2279.563145,1.308603,0.000000,1.308603,1.308603,60.002000,0.000000,60.002000,60.002000,741.204492,0.000000,741.204492,741.204492,81.514575,0.000000,81.514575,81.514575,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.068833,0.000000,6.068833,6.068833,6.105946,0.000000,6.105946,6.105946,1026.572917,0.000000,1026.572917,1026.572917,129.630760,0.000000,129.630760,129.630760,8250.000000,0.000000,8250,8250,842179.000000,0.000000,842179,842179,1660230,0.000000,1660230,1660230,2.971351,0.000000,2.971351,2.971351,5.942609,0.000000,5.942609,5.942609
wbuffix,32k,32k,1,424.493164,0.000000,424.493164,424.493164,13583.791621,0.000000,13583.791621,13583.791621,24.875153,0.000000,24.875153,24.875153,2.218215,0.000000,2.218215,2.218215,2353.817362,0.000000,2353.817362,2353.817362,528.384000,0.000000,528.384000,528.384000,17694.720000,0.000000,17694.720000,17694.720000,18219.008000,0.000000,18219.008000,18219.008000,2355.495204,0.000000,2355.495204,2355.495204,1.677842,0.000000,1.677842,1.677842,60.006000,0.000000,60.006000,60.006000,1278.334375,0.000000,1278.334375,1278.334375,322.079028,0.000000,322.079028,322.079028,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.098887,0.000000,6.098887,6.098887,6.143369,0.000000,6.143369,6.143369,2032.770833,0.000000,2032.770833,2032.770833,245.838234,0.000000,245.838234,245.838234,8401.000000,0.000000,8401,8401,815109.000000,0.000000,815109,815109,1725664,0.000000,1725664,1725664,3.117096,0.000000,3.117096,3.117096,3.117096,0.000000,3.117096,3.117096
wbuffix,32k,64k,1,446.665039,0.000000,446.665039,446.665039,7146.645112,0.000000,7146.645112,7146.645112,26.172668,0.000000,26.172668,26.172668,2.333920,0.000000,2.333920,2.333920,4474.704193,0.000000,4474.704193,4474.704193,978.944000,0.000000,978.944000,978.944000,19005.440000,0.000000,19005.440000,19005.440000,19791.872000,0.000000,19791.872000,19791.872000,4477.327461,0.000000,4477.327461,4477.327461,2.623268,0.000000,2.623268,2.623268,60.002000,0.000000,60.002000,60.002000,1286.819336,0.000000,1286.819336,1286.819336,318.535962,0.000000,318.535962,318.535962,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.978449,0.000000,5.978449,5.978449,6.000871,0.000000,6.000871,6.000871,2123.535156,0.000000,2123.535156,2123.535156,277.478695,0.000000,277.478695,277.478695,9540.000000,0.000000,9540,9540,857626.000000,0.000000,857626,857626,1974722,0.000000,1974722,1974722,3.302544,0.000000,3.302544,3.302544,3.302544,0.000000,3.302544,3.302544
wbuffix,32k,128k,1,496.670898,0.000000,496.670898,496.670898,3973.374211,0.000000,3973.374211,3973.374211,29.110107,0.000000,29.110107,29.110107,2.595863,0.000000,2.595863,2.595863,8049.000065,0.000000,8049.000065,8049.000065,1794.048000,0.000000,1794.048000,1794.048000,20316.160000,0.000000,20316.160000,20316.160000,38010.880000,0.000000,38010.880000,38010.880000,8053.293624,0.000000,8053.293624,8053.293624,4.293558,0.000000,4.293558,4.293558,60.017000,0.000000,60.017000,60.017000,1299.040625,0.000000,1299.040625,1299.040625,274.962500,0.000000,274.962500,274.962500,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.697746,0.000000,5.697746,5.697746,5.697844,0.000000,5.697844,5.697844,2217.931818,0.000000,2217.931818,2217.931818,323.071325,0.000000,323.071325,323.071325,11480.000000,0.000000,11480,11480,953880.000000,0.000000,953880,953880,2375124,0.000000,2375124,2375124,3.489961,0.000000,3.489961,3.489961,3.489961,0.000000,3.489961,3.489961
wbuffix,64k,4k,1,47.053711,0.000000,47.053711,47.053711,12045.792368,0.000000,12045.792368,12045.792368,2.757523,0.000000,2.757523,2.757523,0.245899,0.000000,0.245899,0.245899,2655.297358,0.000000,2655.297358,2655.297358,937.984000,0.000000,937.984000,937.984000,11337.728000,0.000000,11337.728000,11337.728000,11730.944000,0.000000,11730.944000,11730.944000,2656.258098,0.000000,2656.258098,2656.258098,0.960740,0.000000,0.960740,0.960740,60.010000,0.000000,60.010000,60.010000,123.588672,0.000000,123.588672,123.588672,24.842725,0.000000,24.842725,24.842725,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3.675038,0.000000,3.675038,3.675038,3.715039,0.000000,3.715039,3.715039,219.239955,0.000000,219.239955,219.239955,36.395370,0.000000,36.395370,36.395370,15486.000000,0.000000,15486,15486,722868.000000,0.000000,722868,722868,1454598,0.000000,1454598,1454598,3.012259,0.000000,3.012259,3.012259,48.196152,0.000000,48.196152,48.196152
wbuffix,64k,8k,1,93.271484,0.000000,93.271484,93.271484,11938.856114,0.000000,11938.856114,11938.856114,5.465721,0.000000,5.465721,5.465721,0.487400,0.000000,0.487400,0.487400,2678.984933,0.000000,2678.984933,2678.984933,921.600000,0.000000,921.600000,921.600000,11468.800000,0.000000,11468.800000,11468.800000,11862.016000,0.000000,11862.016000,11862.016000,2680.069705,0.000000,2680.069705,2680.069705,1.084772,0.000000,1.084772,1.084772,60.006000,0.000000,60.006000,60.006000,246.790625,0.000000,246.790625,246.790625,48.139453,0.000000,48.139453,48.139453,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3.671269,0.000000,3.671269,3.671269,3.713761,0.000000,3.713761,3.713761,438.600446,0.000000,438.600446,438.600446,71.890565,0.000000,71.890565,71.890565,15563.000000,0.000000,15563,15563,716403.000000,0.000000,716403,716403,1470904,0.000000,1470904,1470904,3.053180,0.000000,3.053180,3.053180,24.425437,0.000000,24.425437,24.425437
wbuffix,64k,16k,1,175.157227,0.000000,175.157227,175.157227,11210.111480,0.000000,11210.111480,11210.111480,10.265045,0.000000,10.265045,10.265045,0.915374,0.000000,0.915374,0.915374,2852.966049,0.000000,2852.966049,2852.966049,937.984000,0.000000,937.984000,937.984000,11862.016000,0.000000,11862.016000,11862.016000,12124.160000,0.000000,12124.160000,12124.160000,2854.286160,0.000000,2854.286160,2854.286160,1.320112,0.000000,1.320112,1.320112,60.011000,0.000000,60.011000,60.011000,488.131250,0.000000,488.131250,488.131250,82.852856,0.000000,82.852856,82.852856,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3.674823,0.000000,3.674823,3.674823,3.718097,0.000000,3.718097,3.718097,876.517857,0.000000,876.517857,876.517857,131.745921,0.000000,131.745921,131.745921,15734.000000,0.000000,15734,15734,672730.000000,0.000000,672730,672730,1536469,0.000000,1536469,1536469,3.283931,0.000000,3.283931,3.283931,13.135725,0.000000,13.135725,13.135725
wbuffix,64k,32k,1,285.618164,0.000000,285.618164,285.618164,9139.800357,0.000000,9139.800357,9139.800357,16.737427,0.000000,16.737427,16.737427,1.492542,0.000000,1.492542,1.492542,3499.234243,0.000000,3499.234243,3499.234243,978.944000,0.000000,978.944000,978.944000,12124.160000,0.000000,12124.160000,12124.160000,12386.304000,0.000000,12386.304000,12386.304000,3500.922222,0.000000,3500.922222,3500.922222,1.687979,0.000000,1.687979,1.687979,60.007000,0.000000,60.007000,60.007000,908.028125,0.000000,908.028125,908.028125,143.391040,0.000000,143.391040,143.391040,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3.683523,0.000000,3.683523,3.683523,3.719467,0.000000,3.719467,3.719467,1752.214286,0.000000,1752.214286,1752.214286,194.797791,0.000000,194.797791,194.797791,16146.000000,0.000000,16146,16146,548451.000000,0.000000,548451,548451,1713443,0.000000,1713443,1713443,4.124150,0.000000,4.124150,4.124150,8.248284,0.000000,8.248284,8.248284
wbuffix,64k,64k,1,645.083008,0.000000,645.083008,645.083008,10321.328578,0.000000,10321.328578,10321.328578,37.800354,0.000000,37.800354,37.800354,3.370806,0.000000,3.370806,3.370806,3097.577347,0.000000,3097.577347,3097.577347,880.640000,0.000000,880.640000,880.640000,11993.088000,0.000000,11993.088000,11993.088000,12386.304000,0.000000,12386.304000,12386.304000,3100.120742,0.000000,3100.120742,3100.120742,2.543395,0.000000,2.543395,2.543395,60.004000,0.000000,60.004000,60.004000,1403.947803,0.000000,1403.947803,1403.947803,518.924536,0.000000,518.924536,518.924536,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3.873841,0.000000,3.873841,3.873841,3.946725,0.000000,3.946725,3.946725,3350.386579,0.000000,3350.386579,3350.386579,477.616375,0.000000,477.616375,477.616375,15930.000000,0.000000,15930,15930,619321.000000,0.000000,619321,619321,1614792,0.000000,1614792,1614792,3.607359,0.000000,3.607359,3.607359,3.607359,0.000000,3.607359,3.607359
wbuffix,64k,128k,1,665.963867,0.000000,665.963867,665.963867,5327.717509,0.000000,5327.717509,5327.717509,39.027222,0.000000,39.027222,39.027222,3.480211,0.000000,3.480211,3.480211,6001.688954,0.000000,6001.688954,6001.688954,1597.440000,0.000000,1597.440000,1597.440000,22675.456000,0.000000,22675.456000,22675.456000,24510.464000,0.000000,24510.464000,24510.464000,6005.981310,0.000000,6005.981310,6005.981310,4.292356,0.000000,4.292356,4.292356,60.009000,0.000000,60.009000,60.009000,1411.562500,0.000000,1411.562500,1411.562500,534.134814,0.000000,534.134814,534.134814,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3.880566,0.000000,3.880566,3.880566,3.898662,0.000000,3.898662,3.898662,3348.178571,0.000000,3348.178571,3348.178571,499.885578,0.000000,499.885578,499.885578,16808.000000,0.000000,16808,16808,639422.000000,0.000000,639422,639422,1707056,0.000000,1707056,1707056,3.669686,0.000000,3.669686,3.669686,3.669686,0.000000,3.669686,3.669686
wbuffix,128k,4k,1,28.133789,0.000000,28.133789,28.133789,7202.426384,0.000000,7202.426384,7202.426384,1.648697,0.000000,1.648697,1.648697,0.147021,0.000000,0.147021,0.147021,4441.680233,0.000000,4441.680233,4441.680233,2441.216000,0.000000,2441.216000,2441.216000,10158.080000,0.000000,10158.080000,10158.080000,16056.320000,0.000000,16056.320000,16056.320000,4442.658270,0.000000,4442.658270,4442.658270,0.978037,0.000000,0.978037,0.978037,60.007000,0.000000,60.007000,60.007000,77.282422,0.000000,77.282422,77.282422,14.416333,0.000000,14.416333,14.416333,0.000000,0.000000,0,0,0.000000,0.000000,0,0,2.475650,0.000000,2.475650,2.475650,2.515920,0.000000,2.515920,2.515920,170.169922,0.000000,170.169922,170.169922,23.238997,0.000000,23.238997,23.238997,22262.000000,0.000000,22262,22262,432196.000000,0.000000,432196,432196,1090213,0.000000,1090213,1090213,3.522497,0.000000,3.522497,3.522497,112.719896,0.000000,112.719896,112.719896
wbuffix,128k,8k,1,56.112305,0.000000,56.112305,56.112305,7182.418132,0.000000,7182.418132,7182.418132,3.288124,0.000000,3.288124,3.288124,0.293215,0.000000,0.293215,0.293215,4453.994508,0.000000,4453.994508,4453.994508,2441.216000,0.000000,2441.216000,2441.216000,10158.080000,0.000000,10158.080000,10158.080000,16580.608000,0.000000,16580.608000,16580.608000,4455.064317,0.000000,4455.064317,4455.064317,1.069809,0.000000,1.069809,1.069809,60.005000,0.000000,60.005000,60.005000,154.100781,0.000000,154.100781,154.100781,28.747534,0.000000,28.747534,28.747534,0.000000,0.000000,0,0,0.000000,0.000000,0,0,2.474023,0.000000,2.474023,2.474023,2.514367,0.000000,2.514367,2.514367,340.449219,0.000000,340.449219,340.449219,46.310336,0.000000,46.310336,46.310336,22231.000000,0.000000,22231,22231,430981.000000,0.000000,430981,430981,1089448,0.000000,1089448,1089448,3.527833,0.000000,3.527833,3.527833,56.445328,0.000000,56.445328,56.445328
wbuffix,128k,16k,1,110.900391,0.000000,110.900391,110.900391,7097.668683,0.000000,7097.668683,7097.668683,6.499084,0.000000,6.499084,6.499084,0.579549,0.000000,0.579549,0.579549,4506.955227,0.000000,4506.955227,4506.955227,2506.752000,0.000000,2506.752000,2506.752000,10289.152000,0.000000,10289.152000,10289.152000,16056.320000,0.000000,16056.320000,16056.320000,4508.221410,0.000000,4508.221410,4508.221410,1.266183,0.000000,1.266183,1.266183,60.009000,0.000000,60.009000,60.009000,307.517187,0.000000,307.517187,307.517187,56.495557,0.000000,56.495557,56.495557,0.000000,0.000000,0,0,0.000000,0.000000,0,0,2.476727,0.000000,2.476727,2.476727,2.516406,0.000000,2.516406,2.516406,680.507812,0.000000,680.507812,680.507812,91.271686,0.000000,91.271686,91.271686,22202.000000,0.000000,22202,22202,425924.000000,0.000000,425924,425924,1092651,0.000000,1092651,1092651,3.565366,0.000000,3.565366,3.565366,28.522929,0.000000,28.522929,28.522929
wbuffix,128k,32k,1,204.968750,0.000000,204.968750,204.968750,6559.014181,0.000000,6559.014181,6559.014181,12.012115,0.000000,12.012115,12.012115,1.071167,0.000000,1.071167,1.071167,4876.810865,0.000000,4876.810865,4876.810865,2899.968000,0.000000,2899.968000,2899.968000,12648.448000,0.000000,12648.448000,12648.448000,18219.008000,0.000000,18219.008000,18219.008000,4878.452653,0.000000,4878.452653,4878.452653,1.641788,0.000000,1.641788,1.641788,60.011000,0.000000,60.011000,60.011000,598.712500,0.000000,598.712500,598.712500,98.130542,0.000000,98.130542,98.130542,0.000000,0.000000,0,0,0.000000,0.000000,0,0,2.477408,0.000000,2.477408,2.477408,2.536558,0.000000,2.536558,2.536558,1359.062500,0.000000,1359.062500,1359.062500,165.200364,0.000000,165.200364,165.200364,22024.000000,0.000000,22024,22024,393613.000000,0.000000,393613,393613,1113559,0.000000,1113559,1113559,3.829071,0.000000,3.829071,3.829071,15.316283,0.000000,15.316283,15.316283
wbuffix,128k,64k,1,340.655273,0.000000,340.655273,340.655273,5450.488285,0.000000,5450.488285,5450.488285,19.962280,0.000000,19.962280,19.962280,1.780115,0.000000,1.780115,1.780115,5868.172732,0.000000,5868.172732,5868.172732,7307.264000,0.000000,7307.264000,7307.264000,16711.680000,0.000000,16711.680000,16711.680000,18743.296000,0.000000,18743.296000,18743.296000,5870.736389,0.000000,5870.736389,5870.736389,2.563657,0.000000,2.563657,2.563657,60.006000,0.000000,60.006000,60.006000,1051.298486,0.000000,1051.298486,1051.298486,192.600146,0.000000,192.600146,192.600146,0.000000,0.000000,0,0,0.000000,0.000000,0,0,2.474275,0.000000,2.474275,2.474275,2.520778,0.000000,2.520778,2.520778,2716.273682,0.000000,2716.273682,2716.273682,258.794526,0.000000,258.794526,258.794526,21712.000000,0.000000,21712,21712,327062.000000,0.000000,327062,327062,1160138,0.000000,1160138,1160138,4.547150,0.000000,4.547150,4.547150,9.094300,0.000000,9.094300,9.094300
wbuffix,128k,128k,1,837.771484,0.000000,837.771484,837.771484,6702.178007,0.000000,6702.178007,6702.178007,49.095581,0.000000,49.095581,49.095581,4.378046,0.000000,4.378046,4.378046,4770.301241,0.000000,4770.301241,4770.301241,2244.608000,0.000000,2244.608000,2244.608000,11337.728000,0.000000,11337.728000,11337.728000,18219.008000,0.000000,18219.008000,18219.008000,4774.282822,0.000000,4774.282822,4774.282822,3.981581,0.000000,3.981581,3.981581,60.009000,0.000000,60.009000,60.009000,1482.975000,0.000000,1482.975000,1482.975000,671.598682,0.000000,671.598682,671.598682,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3.866567,0.000000,3.866567,3.866567,3.895296,0.000000,3.895296,3.895296,3357.214286,0.000000,3357.214286,3357.214286,681.794248,0.000000,681.794248,681.794248,21413.000000,0.000000,21413,21413,402191.000000,0.000000,402191,402191,1065766,0.000000,1065766,1065766,3.649900,0.000000,3.649900,3.649900,3.649900,0.000000,3.649900,3.649900
```

### 11.2.6 파티션별 GC 로그 (회차마다: 첫 GC 줄의 fio 시작 기준 시각·내용, rmmod 통계)
```
[base map4k bs4k r1]
  +6.302s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.304s first GC part=2 victim line=340 vpc=1890 ipc=158 free_lines=2 host_pgs=778240
  +6.321s first GC part=3 victim line=194 vpc=1893 ipc=155 free_lines=2 host_pgs=778240
  +6.323s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1606708 gc_pgs=3447763 gc_cnt=2087 free_lines=2
  stats part=1 host_pgs=1606877 gc_pgs=3443562 gc_cnt=2085 free_lines=2
  stats part=2 host_pgs=1606769 gc_pgs=3455825 gc_cnt=2091 free_lines=2
  stats part=3 host_pgs=1606316 gc_pgs=3437846 gc_cnt=2082 free_lines=2
  (kernel) [61167.172638] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61167.240256] NVMeVirt: Virtual NVMe device closed
[base map4k bs8k r1]
  +5.745s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.745s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.764s first GC part=0 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  +5.764s first GC part=1 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1665151 gc_pgs=3811116 gc_cnt=2293 free_lines=2
  stats part=1 host_pgs=1665151 gc_pgs=3811116 gc_cnt=2293 free_lines=2
  stats part=2 host_pgs=1665321 gc_pgs=3821118 gc_cnt=2298 free_lines=2
  stats part=3 host_pgs=1665321 gc_pgs=3821118 gc_cnt=2298 free_lines=2
  (kernel) [61236.830850] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61236.897600] NVMeVirt: Virtual NVMe device closed
[base map4k bs16k r1]
  +5.697s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.697s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.697s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.697s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1846856 gc_pgs=4704571 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1846856 gc_pgs=4704571 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1846856 gc_pgs=4704571 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1846856 gc_pgs=4704571 gc_cnt=2818 free_lines=2
  (kernel) [61306.485193] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61306.551850] NVMeVirt: Virtual NVMe device closed
[base map4k bs32k r1]
  +5.696s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.697s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1853198 gc_pgs=4702232 gc_cnt=2820 free_lines=2
  stats part=1 host_pgs=1853198 gc_pgs=4702232 gc_cnt=2820 free_lines=2
  stats part=2 host_pgs=1853198 gc_pgs=4702232 gc_cnt=2820 free_lines=2
  stats part=3 host_pgs=1853198 gc_pgs=4702232 gc_cnt=2820 free_lines=2
  (kernel) [61376.151625] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61376.218308] NVMeVirt: Virtual NVMe device closed
[base map4k bs64k r1]
  +5.698s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.698s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.698s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.698s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867904 gc_pgs=4720288 gc_cnt=2836 free_lines=2
  stats part=1 host_pgs=1867904 gc_pgs=4720288 gc_cnt=2836 free_lines=2
  stats part=2 host_pgs=1867904 gc_pgs=4720288 gc_cnt=2836 free_lines=2
  stats part=3 host_pgs=1867904 gc_pgs=4720288 gc_cnt=2836 free_lines=2
  (kernel) [61445.836138] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61445.902774] NVMeVirt: Virtual NVMe device closed
[base map4k bs128k r1]
  +5.699s first GC part=0 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.699s first GC part=1 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.699s first GC part=2 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.699s first GC part=3 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1908152 gc_pgs=4749864 gc_cnt=2870 free_lines=2
  stats part=1 host_pgs=1908152 gc_pgs=4749864 gc_cnt=2870 free_lines=2
  stats part=2 host_pgs=1908152 gc_pgs=4749864 gc_cnt=2870 free_lines=2
  stats part=3 host_pgs=1908152 gc_pgs=4749864 gc_cnt=2870 free_lines=2
  (kernel) [61515.517735] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61515.584599] NVMeVirt: Virtual NVMe device closed
[base map8k bs4k r1]
  +5.685s first GC part=3 victim line=8 vpc=375 ipc=649 free_lines=2 host_pgs=389120
  +5.688s first GC part=0 victim line=2 vpc=355 ipc=669 free_lines=2 host_pgs=389120
  +5.691s first GC part=2 victim line=0 vpc=364 ipc=660 free_lines=2 host_pgs=389120
  +5.691s first GC part=1 victim line=11 vpc=376 ipc=648 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=1022622 gc_pgs=3063323 gc_cnt=3609 free_lines=2
  stats part=1 host_pgs=1023088 gc_pgs=3065941 gc_cnt=3612 free_lines=1
  stats part=2 host_pgs=1023126 gc_pgs=3065884 gc_cnt=3612 free_lines=1
  stats part=3 host_pgs=1023106 gc_pgs=3064893 gc_cnt=3611 free_lines=1
  (kernel) [61543.507167] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost. (Dropped 93650 similar message(s))
  (kernel) [61545.301839] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [61545.302903] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [61585.557539] ldm_validate_partition_table(): Disk read failed.
  (kernel) [61585.557542] Dev nvme1n1: unable to read RDB block 0
  (kernel) [61585.557546]  nvme1n1: unable to read partition table
  (kernel) [61585.557549] nvme1n1: partition table beyond EOD, truncated
  (kernel) [61585.609360] pci_bus 0001:10: busn_res: [bus 10-ff] is released
[base map8k bs8k r1]
  +5.821s first GC part=0 victim line=26 vpc=939 ipc=85 free_lines=2 host_pgs=389120
  +5.821s first GC part=1 victim line=84 vpc=939 ipc=85 free_lines=2 host_pgs=389120
  +5.841s first GC part=3 victim line=96 vpc=945 ipc=79 free_lines=2 host_pgs=389120
  +5.862s first GC part=2 victim line=95 vpc=942 ipc=82 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=806511 gc_pgs=1726898 gc_cnt=2093 free_lines=2
  stats part=1 host_pgs=806454 gc_pgs=1724947 gc_cnt=2091 free_lines=2
  stats part=2 host_pgs=806877 gc_pgs=1732637 gc_cnt=2099 free_lines=2
  stats part=3 host_pgs=806774 gc_pgs=1736723 gc_cnt=2103 free_lines=2
  (kernel) [61655.240057] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61655.280800] NVMeVirt: Virtual NVMe device closed
[base map8k bs16k r1]
  +5.782s first GC part=0 victim line=104 vpc=941 ipc=83 free_lines=2 host_pgs=389120
  +5.782s first GC part=1 victim line=104 vpc=941 ipc=83 free_lines=2 host_pgs=389120
  +5.783s first GC part=2 victim line=226 vpc=944 ipc=80 free_lines=2 host_pgs=389120
  +5.783s first GC part=3 victim line=226 vpc=944 ipc=80 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=845104 gc_pgs=1966795 gc_cnt=2365 free_lines=2
  stats part=1 host_pgs=845104 gc_pgs=1966795 gc_cnt=2365 free_lines=2
  stats part=2 host_pgs=844814 gc_pgs=1967009 gc_cnt=2365 free_lines=2
  stats part=3 host_pgs=844814 gc_pgs=1967009 gc_cnt=2365 free_lines=2
  (kernel) [61724.863874] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61724.904493] NVMeVirt: Virtual NVMe device closed
[base map8k bs32k r1]
  +5.696s first GC part=0 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=1 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=2 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=3 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=925972 gc_pgs=2350748 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=925972 gc_pgs=2350748 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=925972 gc_pgs=2350748 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=925972 gc_pgs=2350748 gc_cnt=2819 free_lines=2
  (kernel) [61794.501602] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61794.542592] NVMeVirt: Virtual NVMe device closed
[base map8k bs64k r1]
  +5.698s first GC part=0 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.698s first GC part=1 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.699s first GC part=2 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.699s first GC part=3 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  stats part=1 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  stats part=2 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  stats part=3 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  (kernel) [61864.108432] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61864.149122] NVMeVirt: Virtual NVMe device closed
[base map8k bs128k r1]
  +5.698s first GC part=0 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.698s first GC part=1 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.698s first GC part=2 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.698s first GC part=3 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=955112 gc_pgs=2373900 gc_cnt=2870 free_lines=2
  stats part=1 host_pgs=955112 gc_pgs=2373900 gc_cnt=2870 free_lines=2
  stats part=2 host_pgs=955112 gc_pgs=2373900 gc_cnt=2870 free_lines=2
  stats part=3 host_pgs=955112 gc_pgs=2373900 gc_cnt=2870 free_lines=2
  (kernel) [61933.739311] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [61933.780735] NVMeVirt: Virtual NVMe device closed
[base map16k bs4k r1]
  +5.668s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.673s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.684s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.684s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=644251 gc_pgs=1397218 gc_cnt=3606 free_lines=2
  stats part=1 host_pgs=644540 gc_pgs=1389794 gc_cnt=3592 free_lines=2
  stats part=2 host_pgs=645196 gc_pgs=1402940 gc_cnt=3619 free_lines=1
  stats part=3 host_pgs=644324 gc_pgs=1395108 gc_cnt=3602 free_lines=2
  (kernel) [61965.081395] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost. (Dropped 6330 similar message(s))
  (kernel) [61966.808829] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [61968.132131] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [62004.296160] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62004.323863] NVMeVirt: Virtual NVMe device closed
[base map16k bs8k r1]
  +5.666s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.676s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.676s first GC part=3 victim line=10 vpc=178 ipc=334 free_lines=2 host_pgs=194560
  +5.697s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=524049 gc_pgs=1610601 gc_cnt=3788 free_lines=2
  stats part=1 host_pgs=523663 gc_pgs=1607896 gc_cnt=3782 free_lines=2
  stats part=2 host_pgs=523873 gc_pgs=1614352 gc_cnt=3795 free_lines=1
  stats part=3 host_pgs=523528 gc_pgs=1612141 gc_cnt=3790 free_lines=2
  (kernel) [62028.442123] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost. (Dropped 2747 similar message(s))
  (kernel) [62029.513128] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [62029.515013] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [62075.039480] ldm_validate_partition_table(): Disk read failed.
  (kernel) [62075.039484] Dev nvme1n1: unable to read RDB block 0
  (kernel) [62075.039487]  nvme1n1: unable to read partition table
  (kernel) [62075.039491] nvme1n1: partition table beyond EOD, truncated
  (kernel) [62075.112067] pci_bus 0001:10: busn_res: [bus 10-ff] is released
[base map16k bs16k r1]
  +5.924s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.925s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.945s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.946s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=404231 gc_pgs=862454 gc_cnt=2093 free_lines=2
  stats part=1 host_pgs=404310 gc_pgs=862363 gc_cnt=2093 free_lines=2
  stats part=2 host_pgs=404261 gc_pgs=859375 gc_cnt=2087 free_lines=2
  stats part=3 host_pgs=403841 gc_pgs=855698 gc_cnt=2079 free_lines=2
  (kernel) [62144.723993] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62144.751549] NVMeVirt: Virtual NVMe device closed
[base map16k bs32k r1]
  +5.846s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.846s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.867s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.868s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=426259 gc_pgs=996022 gc_cnt=2397 free_lines=2
  stats part=1 host_pgs=426259 gc_pgs=996022 gc_cnt=2397 free_lines=2
  stats part=2 host_pgs=426129 gc_pgs=993080 gc_cnt=2391 free_lines=2
  stats part=3 host_pgs=426129 gc_pgs=993080 gc_cnt=2391 free_lines=2
  (kernel) [62214.339914] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62214.367809] NVMeVirt: Virtual NVMe device closed
[base map16k bs64k r1]
  +5.690s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.690s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.690s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.690s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=467073 gc_pgs=1180476 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=467073 gc_pgs=1180476 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=467073 gc_pgs=1180476 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=467073 gc_pgs=1180476 gc_cnt=2837 free_lines=2
  (kernel) [62283.956905] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62283.984629] NVMeVirt: Virtual NVMe device closed
[base map16k bs128k r1]
  +5.697s first GC part=0 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  +5.697s first GC part=1 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  +5.697s first GC part=2 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  +5.697s first GC part=3 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=477014 gc_pgs=1187492 gc_cnt=2870 free_lines=2
  stats part=1 host_pgs=477014 gc_pgs=1187492 gc_cnt=2870 free_lines=2
  stats part=2 host_pgs=477014 gc_pgs=1187492 gc_cnt=2870 free_lines=2
  stats part=3 host_pgs=477014 gc_pgs=1187492 gc_cnt=2870 free_lines=2
  (kernel) [62353.578854] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62353.606737] NVMeVirt: Virtual NVMe device closed
[base map32k bs4k r1]
  +5.636s first GC part=0 victim line=6 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +5.659s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +5.670s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +5.682s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=355557 gc_pgs=728946 gc_cnt=3855 free_lines=2
  stats part=1 host_pgs=356504 gc_pgs=743601 gc_cnt=3916 free_lines=2
  stats part=2 host_pgs=355413 gc_pgs=731391 gc_cnt=3864 free_lines=2
  stats part=3 host_pgs=354932 gc_pgs=725225 gc_cnt=3838 free_lines=2
  (kernel) [62377.652252] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost. (Dropped 4618 similar message(s))
  (kernel) [62379.791518] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [62381.035264] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [62424.743825] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62424.764682] NVMeVirt: Virtual NVMe device closed
[base map32k bs8k r1]
  +5.639s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +5.658s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +5.666s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +5.673s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=333894 gc_pgs=764658 gc_cnt=3910 free_lines=2
  stats part=1 host_pgs=334612 gc_pgs=777271 gc_cnt=3962 free_lines=1
  stats part=2 host_pgs=334004 gc_pgs=770953 gc_cnt=3935 free_lines=2
  stats part=3 host_pgs=333938 gc_pgs=757975 gc_cnt=3884 free_lines=2
  (kernel) [62448.331541] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost. (Dropped 3673 similar message(s))
  (kernel) [62450.007775] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [62451.097202] systemd-journald[350]: /dev/kmsg buffer overrun, some messages lost.
  (kernel) [62496.325173] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62496.346133] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs4k r1]
  +6.306s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.308s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.326s first GC part=3 victim line=194 vpc=1892 ipc=156 free_lines=2 host_pgs=778240
  +6.327s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1611157 gc_pgs=3480054 gc_cnt=2105 free_lines=2
  stats part=1 host_pgs=1611328 gc_pgs=3477894 gc_cnt=2104 free_lines=2
  stats part=2 host_pgs=1611255 gc_pgs=3490134 gc_cnt=2110 free_lines=2
  stats part=3 host_pgs=1610844 gc_pgs=3468315 gc_cnt=2099 free_lines=2
  (kernel) [62859.400181] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62859.468494] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs4k r2]
  +6.302s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.304s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.321s first GC part=3 victim line=194 vpc=1893 ipc=155 free_lines=2 host_pgs=778240
  +6.322s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1603803 gc_pgs=3423892 gc_cnt=2074 free_lines=2
  stats part=1 host_pgs=1604031 gc_pgs=3427756 gc_cnt=2076 free_lines=2
  stats part=2 host_pgs=1603793 gc_pgs=3434083 gc_cnt=2079 free_lines=2
  stats part=3 host_pgs=1603461 gc_pgs=3418280 gc_cnt=2071 free_lines=2
  (kernel) [65392.081236] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65392.148453] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs8k r1]
  +5.746s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.746s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.765s first GC part=0 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  +5.765s first GC part=1 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1687000 gc_pgs=3938806 gc_cnt=2366 free_lines=2
  stats part=1 host_pgs=1687000 gc_pgs=3938806 gc_cnt=2366 free_lines=2
  stats part=2 host_pgs=1686936 gc_pgs=3943083 gc_cnt=2368 free_lines=2
  stats part=3 host_pgs=1686936 gc_pgs=3943083 gc_cnt=2368 free_lines=2
  (kernel) [62929.815477] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [62929.882398] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs8k r2]
  +5.743s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.743s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.762s first GC part=0 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.762s first GC part=1 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1681930 gc_pgs=3911133 gc_cnt=2350 free_lines=2
  stats part=1 host_pgs=1681930 gc_pgs=3911133 gc_cnt=2350 free_lines=2
  stats part=2 host_pgs=1681991 gc_pgs=3915097 gc_cnt=2352 free_lines=2
  stats part=3 host_pgs=1681991 gc_pgs=3915097 gc_cnt=2352 free_lines=2
  (kernel) [65462.506154] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65462.573518] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r1]
  +5.690s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.690s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.691s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.691s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1847156 gc_pgs=4704306 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1847156 gc_pgs=4704306 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1847156 gc_pgs=4704306 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1847156 gc_pgs=4704306 gc_cnt=2818 free_lines=2
  (kernel) [63000.235680] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63000.302572] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r2]
  +5.696s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.696s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.696s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.696s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1846976 gc_pgs=4704489 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1846976 gc_pgs=4704489 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1846976 gc_pgs=4704489 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1846976 gc_pgs=4704489 gc_cnt=2818 free_lines=2
  (kernel) [65532.907080] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65532.974016] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r1]
  +5.696s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852866 gc_pgs=4702562 gc_cnt=2820 free_lines=2
  stats part=1 host_pgs=1852866 gc_pgs=4702562 gc_cnt=2820 free_lines=2
  stats part=2 host_pgs=1852866 gc_pgs=4702562 gc_cnt=2820 free_lines=2
  stats part=3 host_pgs=1852866 gc_pgs=4702562 gc_cnt=2820 free_lines=2
  (kernel) [63070.649752] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63070.717111] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r2]
  +5.696s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.696s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852456 gc_pgs=4700974 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1852456 gc_pgs=4700974 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1852456 gc_pgs=4700974 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1852456 gc_pgs=4700974 gc_cnt=2819 free_lines=2
  (kernel) [65603.344093] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65603.411815] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r1]
  +5.697s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.697s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.697s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.697s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867648 gc_pgs=4720548 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=1867648 gc_pgs=4720548 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=1867648 gc_pgs=4720548 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=1867648 gc_pgs=4720548 gc_cnt=2836 free_lines=3
  (kernel) [63141.074742] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63141.142177] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r2]
  +5.690s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.690s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.690s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.690s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867608 gc_pgs=4720592 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=1867608 gc_pgs=4720592 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=1867608 gc_pgs=4720592 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=1867608 gc_pgs=4720592 gc_cnt=2836 free_lines=3
  (kernel) [65673.702168] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65673.769400] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs128k r1]
  +5.697s first GC part=0 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.697s first GC part=1 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.698s first GC part=2 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.698s first GC part=3 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1908104 gc_pgs=4747872 gc_cnt=2869 free_lines=2
  stats part=1 host_pgs=1908104 gc_pgs=4747872 gc_cnt=2869 free_lines=2
  stats part=2 host_pgs=1908104 gc_pgs=4747872 gc_cnt=2869 free_lines=2
  stats part=3 host_pgs=1908104 gc_pgs=4747872 gc_cnt=2869 free_lines=2
  (kernel) [63211.504696] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63211.571966] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs128k r2]
  +5.697s first GC part=0 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.697s first GC part=1 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.697s first GC part=2 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  +5.697s first GC part=3 victim line=38 vpc=1848 ipc=200 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1908408 gc_pgs=4749376 gc_cnt=2870 free_lines=2
  stats part=1 host_pgs=1908408 gc_pgs=4749376 gc_cnt=2870 free_lines=2
  stats part=2 host_pgs=1908408 gc_pgs=4749376 gc_cnt=2870 free_lines=2
  stats part=3 host_pgs=1908408 gc_pgs=4749376 gc_cnt=2870 free_lines=2
  (kernel) [65744.124113] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65744.191402] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs4k r1]
  +5.811s first GC part=3 victim line=8 vpc=376 ipc=648 free_lines=2 host_pgs=389120
  +5.821s first GC part=0 victim line=2 vpc=355 ipc=669 free_lines=2 host_pgs=389120
  +5.831s first GC part=2 victim line=0 vpc=364 ipc=660 free_lines=2 host_pgs=389120
  +5.831s first GC part=1 victim line=11 vpc=376 ipc=648 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=831830 gc_pgs=1618840 gc_cnt=2012 free_lines=2
  stats part=1 host_pgs=832138 gc_pgs=1619514 gc_cnt=2013 free_lines=2
  stats part=2 host_pgs=831799 gc_pgs=1618832 gc_cnt=2012 free_lines=2
  stats part=3 host_pgs=832321 gc_pgs=1620352 gc_cnt=2014 free_lines=2
  (kernel) [63281.903543] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63281.945081] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs4k r2]
  +5.817s first GC part=3 victim line=8 vpc=376 ipc=648 free_lines=2 host_pgs=389120
  +5.827s first GC part=0 victim line=2 vpc=355 ipc=669 free_lines=2 host_pgs=389120
  +5.837s first GC part=2 victim line=0 vpc=364 ipc=660 free_lines=2 host_pgs=389120
  +5.837s first GC part=1 victim line=11 vpc=376 ipc=648 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=831598 gc_pgs=1620076 gc_cnt=2013 free_lines=1
  stats part=1 host_pgs=831918 gc_pgs=1621769 gc_cnt=2015 free_lines=2
  stats part=2 host_pgs=831536 gc_pgs=1614041 gc_cnt=2007 free_lines=1
  stats part=3 host_pgs=832012 gc_pgs=1619668 gc_cnt=2013 free_lines=2
  (kernel) [65814.529172] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65814.570130] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs8k r1]
  +5.821s first GC part=0 victim line=26 vpc=939 ipc=85 free_lines=2 host_pgs=389120
  +5.822s first GC part=1 victim line=84 vpc=939 ipc=85 free_lines=2 host_pgs=389120
  +5.842s first GC part=3 victim line=96 vpc=945 ipc=79 free_lines=2 host_pgs=389120
  +5.862s first GC part=2 victim line=95 vpc=942 ipc=82 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=806378 gc_pgs=1722965 gc_cnt=2089 free_lines=2
  stats part=1 host_pgs=806313 gc_pgs=1727120 gc_cnt=2093 free_lines=2
  stats part=2 host_pgs=806732 gc_pgs=1733804 gc_cnt=2100 free_lines=2
  stats part=3 host_pgs=806652 gc_pgs=1737903 gc_cnt=2104 free_lines=2
  (kernel) [63352.286335] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63352.327469] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs8k r2]
  +5.821s first GC part=0 victim line=26 vpc=939 ipc=85 free_lines=2 host_pgs=389120
  +5.821s first GC part=1 victim line=84 vpc=939 ipc=85 free_lines=2 host_pgs=389120
  +5.841s first GC part=3 victim line=96 vpc=945 ipc=79 free_lines=2 host_pgs=389120
  +5.861s first GC part=2 victim line=95 vpc=942 ipc=82 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=800432 gc_pgs=1683960 gc_cnt=2045 free_lines=2
  stats part=1 host_pgs=800383 gc_pgs=1686891 gc_cnt=2048 free_lines=2
  stats part=2 host_pgs=800604 gc_pgs=1689701 gc_cnt=2051 free_lines=2
  stats part=3 host_pgs=800665 gc_pgs=1694819 gc_cnt=2056 free_lines=2
  (kernel) [65884.886252] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65884.927324] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs16k r1]
  +5.777s first GC part=0 victim line=104 vpc=941 ipc=83 free_lines=2 host_pgs=389120
  +5.777s first GC part=1 victim line=104 vpc=941 ipc=83 free_lines=2 host_pgs=389120
  +5.778s first GC part=2 victim line=226 vpc=944 ipc=80 free_lines=2 host_pgs=389120
  +5.778s first GC part=3 victim line=226 vpc=944 ipc=80 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=838932 gc_pgs=1929943 gc_cnt=2323 free_lines=2
  stats part=1 host_pgs=838932 gc_pgs=1929943 gc_cnt=2323 free_lines=2
  stats part=2 host_pgs=838532 gc_pgs=1932304 gc_cnt=2325 free_lines=2
  stats part=3 host_pgs=838532 gc_pgs=1932304 gc_cnt=2325 free_lines=2
  (kernel) [63422.670094] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63422.711171] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs16k r2]
  +5.777s first GC part=0 victim line=104 vpc=941 ipc=83 free_lines=2 host_pgs=389120
  +5.777s first GC part=1 victim line=104 vpc=941 ipc=83 free_lines=2 host_pgs=389120
  +5.778s first GC part=2 victim line=226 vpc=944 ipc=80 free_lines=2 host_pgs=389120
  +5.778s first GC part=3 victim line=226 vpc=944 ipc=80 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=843177 gc_pgs=1953356 gc_cnt=2350 free_lines=2
  stats part=1 host_pgs=843177 gc_pgs=1953356 gc_cnt=2350 free_lines=2
  stats part=2 host_pgs=842819 gc_pgs=1957730 gc_cnt=2354 free_lines=2
  stats part=3 host_pgs=842819 gc_pgs=1957730 gc_cnt=2354 free_lines=2
  (kernel) [65955.275359] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65955.316708] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs32k r1]
  +5.696s first GC part=0 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=1 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=2 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=3 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=926344 gc_pgs=2351401 gc_cnt=2820 free_lines=2
  stats part=1 host_pgs=926344 gc_pgs=2351401 gc_cnt=2820 free_lines=2
  stats part=2 host_pgs=926344 gc_pgs=2351401 gc_cnt=2820 free_lines=2
  stats part=3 host_pgs=926344 gc_pgs=2351401 gc_cnt=2820 free_lines=2
  (kernel) [63493.018793] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63493.060429] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs32k r2]
  +5.696s first GC part=0 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=1 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=2 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  +5.696s first GC part=3 victim line=26 vpc=940 ipc=84 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=925948 gc_pgs=2351761 gc_cnt=2820 free_lines=2
  stats part=1 host_pgs=925948 gc_pgs=2351761 gc_cnt=2820 free_lines=2
  stats part=2 host_pgs=925948 gc_pgs=2351761 gc_cnt=2820 free_lines=2
  stats part=3 host_pgs=925948 gc_pgs=2351761 gc_cnt=2820 free_lines=2
  (kernel) [66025.654480] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66025.695561] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs64k r1]
  +5.697s first GC part=0 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.697s first GC part=1 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.697s first GC part=2 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.697s first GC part=3 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  stats part=1 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  stats part=2 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  stats part=3 host_pgs=933912 gc_pgs=2360184 gc_cnt=2836 free_lines=2
  (kernel) [63563.401470] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63563.442969] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs64k r2]
  +5.697s first GC part=0 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.698s first GC part=1 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.698s first GC part=2 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  +5.698s first GC part=3 victim line=103 vpc=938 ipc=86 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=934072 gc_pgs=2361048 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=934072 gc_pgs=2361048 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=934072 gc_pgs=2361048 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=934072 gc_pgs=2361048 gc_cnt=2837 free_lines=2
  (kernel) [66096.026595] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66096.068072] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs128k r1]
  +5.697s first GC part=0 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.697s first GC part=1 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.697s first GC part=2 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.697s first GC part=3 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=953948 gc_pgs=2374984 gc_cnt=2870 free_lines=2
  stats part=1 host_pgs=953948 gc_pgs=2374984 gc_cnt=2870 free_lines=2
  stats part=2 host_pgs=953948 gc_pgs=2374984 gc_cnt=2870 free_lines=2
  stats part=3 host_pgs=953948 gc_pgs=2374984 gc_cnt=2870 free_lines=2
  (kernel) [63633.778117] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63633.819758] NVMeVirt: Virtual NVMe device closed
[wbuffix map8k bs128k r2]
  +5.697s first GC part=0 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.697s first GC part=1 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.697s first GC part=2 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  +5.697s first GC part=3 victim line=38 vpc=924 ipc=100 free_lines=2 host_pgs=389120
  stats part=0 host_pgs=953796 gc_pgs=2374204 gc_cnt=2869 free_lines=2
  stats part=1 host_pgs=953796 gc_pgs=2374204 gc_cnt=2869 free_lines=2
  stats part=2 host_pgs=953796 gc_pgs=2374204 gc_cnt=2869 free_lines=2
  stats part=3 host_pgs=953796 gc_pgs=2374204 gc_cnt=2869 free_lines=2
  (kernel) [66166.394719] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66166.435897] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r1]
  +5.918s first GC part=2 victim line=6 vpc=172 ipc=340 free_lines=2 host_pgs=194560
  +5.929s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.947s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.948s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=498067 gc_pgs=602329 gc_cnt=1768 free_lines=2
  stats part=1 host_pgs=499054 gc_pgs=600320 gc_cnt=1766 free_lines=2
  stats part=2 host_pgs=500105 gc_pgs=611573 gc_cnt=1790 free_lines=2
  stats part=3 host_pgs=498468 gc_pgs=601434 gc_cnt=1767 free_lines=2
  (kernel) [63704.128751] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63704.156452] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r2]
  +5.920s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.931s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.949s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.950s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497178 gc_pgs=597630 gc_cnt=1757 free_lines=1
  stats part=1 host_pgs=498195 gc_pgs=597137 gc_cnt=1758 free_lines=1
  stats part=2 host_pgs=499228 gc_pgs=608304 gc_cnt=1782 free_lines=1
  stats part=3 host_pgs=497629 gc_pgs=598189 gc_cnt=1759 free_lines=2
  (kernel) [66236.750872] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66236.778614] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r1]
  +5.907s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.925s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.925s first GC part=3 victim line=10 vpc=178 ipc=334 free_lines=2 host_pgs=194560
  +5.975s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=417869 gc_pgs=816704 gc_cnt=2030 free_lines=1
  stats part=1 host_pgs=418039 gc_pgs=818048 gc_cnt=2033 free_lines=2
  stats part=2 host_pgs=417739 gc_pgs=818878 gc_cnt=2034 free_lines=2
  stats part=3 host_pgs=417413 gc_pgs=813576 gc_cnt=2023 free_lines=1
  (kernel) [63774.476325] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63774.503908] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r2]
  +5.909s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.926s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.926s first GC part=3 victim line=10 vpc=178 ipc=334 free_lines=2 host_pgs=194560
  +5.976s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=418708 gc_pgs=820934 gc_cnt=2040 free_lines=2
  stats part=1 host_pgs=418899 gc_pgs=823853 gc_cnt=2046 free_lines=1
  stats part=2 host_pgs=418579 gc_pgs=823136 gc_cnt=2044 free_lines=2
  stats part=3 host_pgs=418266 gc_pgs=821395 gc_cnt=2040 free_lines=2
  (kernel) [66307.077035] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66307.104883] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r1]
  +5.924s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.925s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.945s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.946s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=403961 gc_pgs=860651 gc_cnt=2089 free_lines=3
  stats part=1 host_pgs=404071 gc_pgs=862084 gc_cnt=2092 free_lines=2
  stats part=2 host_pgs=404028 gc_pgs=856503 gc_cnt=2081 free_lines=2
  stats part=3 host_pgs=403608 gc_pgs=854871 gc_cnt=2077 free_lines=2
  (kernel) [63844.823906] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63844.851609] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r2]
  +5.924s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.925s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.946s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.946s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=403560 gc_pgs=857982 gc_cnt=2083 free_lines=2
  stats part=1 host_pgs=403674 gc_pgs=858356 gc_cnt=2084 free_lines=2
  stats part=2 host_pgs=403645 gc_pgs=854344 gc_cnt=2076 free_lines=2
  stats part=3 host_pgs=403213 gc_pgs=852204 gc_cnt=2071 free_lines=2
  (kernel) [66377.436208] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66377.464362] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r1]
  +5.846s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.846s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.868s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.868s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=422172 gc_pgs=971490 gc_cnt=2341 free_lines=2
  stats part=1 host_pgs=422172 gc_pgs=971490 gc_cnt=2341 free_lines=2
  stats part=2 host_pgs=421836 gc_pgs=968220 gc_cnt=2334 free_lines=2
  stats part=3 host_pgs=421836 gc_pgs=968220 gc_cnt=2334 free_lines=2
  (kernel) [63915.161440] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63915.189295] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r2]
  +5.847s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.847s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.868s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.868s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=427184 gc_pgs=1000738 gc_cnt=2408 free_lines=2
  stats part=1 host_pgs=427184 gc_pgs=1000738 gc_cnt=2408 free_lines=2
  stats part=2 host_pgs=427030 gc_pgs=997823 gc_cnt=2402 free_lines=2
  stats part=3 host_pgs=427030 gc_pgs=997823 gc_cnt=2402 free_lines=2
  (kernel) [66447.788342] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66447.816226] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r1]
  +5.697s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.697s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.697s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.697s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=466956 gc_pgs=1180092 gc_cnt=2836 free_lines=2
  stats part=1 host_pgs=466956 gc_pgs=1180092 gc_cnt=2836 free_lines=2
  stats part=2 host_pgs=466956 gc_pgs=1180092 gc_cnt=2836 free_lines=2
  stats part=3 host_pgs=466956 gc_pgs=1180092 gc_cnt=2836 free_lines=2
  (kernel) [63985.515976] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [63985.543921] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r2]
  +5.697s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.697s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.697s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.697s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=466858 gc_pgs=1180190 gc_cnt=2836 free_lines=2
  stats part=1 host_pgs=466858 gc_pgs=1180190 gc_cnt=2836 free_lines=2
  stats part=2 host_pgs=466858 gc_pgs=1180190 gc_cnt=2836 free_lines=2
  stats part=3 host_pgs=466858 gc_pgs=1180190 gc_cnt=2836 free_lines=2
  (kernel) [66518.139529] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [66518.167430] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs128k r1]
  +5.694s first GC part=0 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  +5.694s first GC part=1 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  +5.694s first GC part=2 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  +5.694s first GC part=3 victim line=38 vpc=462 ipc=50 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=477196 gc_pgs=1187308 gc_cnt=2870 free_lines=2
  stats part=1 host_pgs=477196 gc_pgs=1187308 gc_cnt=2870 free_lines=2
  stats part=2 host_pgs=477196 gc_pgs=1187308 gc_cnt=2870 free_lines=2
  stats part=3 host_pgs=477196 gc_pgs=1187308 gc_cnt=2870 free_lines=2
  (kernel) [64055.859500] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64055.887251] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs4k r1]
  +6.067s first GC part=0 victim line=6 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.104s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.127s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.149s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262571 gc_pgs=297104 gc_cnt=1805 free_lines=2
  stats part=1 host_pgs=262639 gc_pgs=301910 gc_cnt=1824 free_lines=2
  stats part=2 host_pgs=262094 gc_pgs=297570 gc_cnt=1805 free_lines=2
  stats part=3 host_pgs=261488 gc_pgs=292571 gc_cnt=1783 free_lines=2
  (kernel) [64126.218024] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64126.238873] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs8k r1]
  +6.070s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.096s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +6.112s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +6.125s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=252597 gc_pgs=311430 gc_cnt=1822 free_lines=2
  stats part=1 host_pgs=253410 gc_pgs=318068 gc_cnt=1851 free_lines=2
  stats part=2 host_pgs=252532 gc_pgs=312770 gc_cnt=1827 free_lines=2
  stats part=3 host_pgs=253046 gc_pgs=309205 gc_cnt=1815 free_lines=2
  (kernel) [64196.546515] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64196.567589] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs16k r1]
  +6.069s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.094s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.105s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.106s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210528 gc_pgs=414177 gc_cnt=2059 free_lines=2
  stats part=1 host_pgs=210666 gc_pgs=416098 gc_cnt=2067 free_lines=2
  stats part=2 host_pgs=210677 gc_pgs=418891 gc_cnt=2078 free_lines=2
  stats part=3 host_pgs=210308 gc_pgs=411064 gc_cnt=2046 free_lines=2
  (kernel) [64266.885016] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64266.905847] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs32k r1]
  +6.099s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.122s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.143s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.143s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203856 gc_pgs=430769 gc_cnt=2098 free_lines=2
  stats part=1 host_pgs=203604 gc_pgs=429996 gc_cnt=2094 free_lines=2
  stats part=2 host_pgs=203957 gc_pgs=433473 gc_cnt=2109 free_lines=2
  stats part=3 host_pgs=203692 gc_pgs=431426 gc_cnt=2100 free_lines=2
  (kernel) [64337.207482] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64337.228116] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs64k r1]
  +5.978s first GC part=0 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.978s first GC part=1 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.001s first GC part=2 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.001s first GC part=3 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=214497 gc_pgs=495122 gc_cnt=2391 free_lines=2
  stats part=1 host_pgs=214497 gc_pgs=495122 gc_cnt=2391 free_lines=2
  stats part=2 host_pgs=214316 gc_pgs=492239 gc_cnt=2379 free_lines=2
  stats part=3 host_pgs=214316 gc_pgs=492239 gc_cnt=2379 free_lines=2
  (kernel) [64407.533944] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64407.554626] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs128k r1]
  +5.698s first GC part=0 victim line=38 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +5.698s first GC part=1 victim line=38 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +5.698s first GC part=2 victim line=38 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +5.698s first GC part=3 victim line=38 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=238470 gc_pgs=593781 gc_cnt=2870 free_lines=2
  stats part=1 host_pgs=238470 gc_pgs=593781 gc_cnt=2870 free_lines=2
  stats part=2 host_pgs=238470 gc_pgs=593781 gc_cnt=2870 free_lines=2
  stats part=3 host_pgs=238470 gc_pgs=593781 gc_cnt=2870 free_lines=2
  (kernel) [64477.885411] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64477.906308] NVMeVirt: Virtual NVMe device closed
[wbuffix map64k bs4k r1]
  +3.675s first GC part=1 victim line=3 vpc=33 ipc=95 free_lines=2 host_pgs=48640
  +3.689s first GC part=2 victim line=41 vpc=34 ipc=94 free_lines=2 host_pgs=48640
  +3.697s first GC part=3 victim line=47 vpc=34 ipc=94 free_lines=2 host_pgs=48640
  +3.715s first GC part=0 victim line=23 vpc=34 ipc=94 free_lines=2 host_pgs=48640
  stats part=0 host_pgs=181041 gc_pgs=366210 gc_cnt=3894 free_lines=1
  stats part=1 host_pgs=180556 gc_pgs=363486 gc_cnt=3869 free_lines=2
  stats part=2 host_pgs=181081 gc_pgs=365527 gc_cnt=3889 free_lines=2
  stats part=3 host_pgs=180190 gc_pgs=359375 gc_cnt=3834 free_lines=2
  (kernel) [64548.230513] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64548.247151] NVMeVirt: Virtual NVMe device closed
[wbuffix map64k bs8k r1]
  +3.671s first GC part=1 victim line=3 vpc=35 ipc=93 free_lines=2 host_pgs=48640
  +3.685s first GC part=2 victim line=41 vpc=35 ipc=93 free_lines=2 host_pgs=48640
  +3.691s first GC part=3 victim line=2 vpc=34 ipc=94 free_lines=2 host_pgs=48640
  +3.714s first GC part=0 victim line=23 vpc=28 ipc=100 free_lines=2 host_pgs=48640
  stats part=0 host_pgs=179054 gc_pgs=370626 gc_cnt=3913 free_lines=2
  stats part=1 host_pgs=179257 gc_pgs=371187 gc_cnt=3919 free_lines=2
  stats part=2 host_pgs=179413 gc_pgs=366676 gc_cnt=3885 free_lines=2
  stats part=3 host_pgs=178679 gc_pgs=362415 gc_cnt=3846 free_lines=2
  (kernel) [64618.555126] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64618.571686] NVMeVirt: Virtual NVMe device closed
[wbuffix map64k bs16k r1]
  +3.675s first GC part=1 victim line=3 vpc=34 ipc=94 free_lines=2 host_pgs=48640
  +3.685s first GC part=2 victim line=41 vpc=39 ipc=89 free_lines=2 host_pgs=48640
  +3.686s first GC part=3 victim line=8 vpc=37 ipc=91 free_lines=2 host_pgs=48640
  +3.718s first GC part=0 victim line=23 vpc=29 ipc=99 free_lines=2 host_pgs=48640
  stats part=0 host_pgs=168047 gc_pgs=388039 gc_cnt=3963 free_lines=2
  stats part=1 host_pgs=168049 gc_pgs=381763 gc_cnt=3914 free_lines=2
  stats part=2 host_pgs=168409 gc_pgs=385609 gc_cnt=3947 free_lines=2
  stats part=3 host_pgs=168225 gc_pgs=381058 gc_cnt=3910 free_lines=1
  (kernel) [64688.820981] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64688.837415] NVMeVirt: Virtual NVMe device closed
[wbuffix map64k bs32k r1]
  +3.684s first GC part=2 victim line=5 vpc=40 ipc=88 free_lines=2 host_pgs=48640
  +3.684s first GC part=1 victim line=3 vpc=41 ipc=87 free_lines=2 host_pgs=48640
  +3.695s first GC part=3 victim line=8 vpc=41 ipc=87 free_lines=2 host_pgs=48640
  +3.719s first GC part=0 victim line=15 vpc=41 ipc=87 free_lines=2 host_pgs=48640
  stats part=0 host_pgs=137080 gc_pgs=427825 gc_cnt=4032 free_lines=2
  stats part=1 host_pgs=136988 gc_pgs=428931 gc_cnt=4040 free_lines=1
  stats part=2 host_pgs=137159 gc_pgs=427862 gc_cnt=4033 free_lines=2
  stats part=3 host_pgs=137224 gc_pgs=428825 gc_cnt=4041 free_lines=1
  (kernel) [64759.159008] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64759.175253] NVMeVirt: Virtual NVMe device closed
[wbuffix map64k bs64k r1]
  +3.874s first GC part=0 victim line=217 vpc=112 ipc=16 free_lines=2 host_pgs=48640
  +3.894s first GC part=3 victim line=328 vpc=112 ipc=16 free_lines=2 host_pgs=48640
  +3.895s first GC part=1 victim line=267 vpc=112 ipc=16 free_lines=2 host_pgs=48640
  +3.947s first GC part=2 victim line=117 vpc=110 ipc=18 free_lines=2 host_pgs=48640
  stats part=0 host_pgs=154630 gc_pgs=404735 gc_cnt=3989 free_lines=2
  stats part=1 host_pgs=154960 gc_pgs=402100 gc_cnt=3971 free_lines=2
  stats part=2 host_pgs=154847 gc_pgs=404378 gc_cnt=3988 free_lines=2
  stats part=3 host_pgs=154884 gc_pgs=403579 gc_cnt=3982 free_lines=2
  (kernel) [64829.458191] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64829.474517] NVMeVirt: Virtual NVMe device closed
[wbuffix map64k bs128k r1]
  +3.881s first GC part=2 victim line=245 vpc=113 ipc=15 free_lines=2 host_pgs=48640
  +3.881s first GC part=3 victim line=245 vpc=113 ipc=15 free_lines=2 host_pgs=48640
  +3.899s first GC part=0 victim line=215 vpc=112 ipc=16 free_lines=2 host_pgs=48640
  +3.899s first GC part=1 victim line=215 vpc=112 ipc=16 free_lines=2 host_pgs=48640
  stats part=0 host_pgs=159978 gc_pgs=427787 gc_cnt=4211 free_lines=2
  stats part=1 host_pgs=159978 gc_pgs=427787 gc_cnt=4211 free_lines=2
  stats part=2 host_pgs=159733 gc_pgs=425741 gc_cnt=4193 free_lines=2
  stats part=3 host_pgs=159733 gc_pgs=425741 gc_cnt=4193 free_lines=2
  (kernel) [64899.782513] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64899.798866] NVMeVirt: Virtual NVMe device closed
[wbuffix map128k bs4k r1]
  +2.476s first GC part=1 victim line=8 vpc=12 ipc=52 free_lines=2 host_pgs=24320
  +2.477s first GC part=2 victim line=6 vpc=18 ipc=46 free_lines=2 host_pgs=24320
  +2.488s first GC part=3 victim line=48 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  +2.516s first GC part=0 victim line=40 vpc=14 ipc=50 free_lines=2 host_pgs=24320
  stats part=0 host_pgs=108009 gc_pgs=271088 gc_cnt=5542 free_lines=2
  stats part=1 host_pgs=108001 gc_pgs=270075 gc_cnt=5526 free_lines=2
  stats part=2 host_pgs=108164 gc_pgs=274967 gc_cnt=5605 free_lines=1
  stats part=3 host_pgs=108022 gc_pgs=274083 gc_cnt=5589 free_lines=2
  (kernel) [64970.092968] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [64970.106914] NVMeVirt: Virtual NVMe device closed
[wbuffix map128k bs8k r1]
  +2.474s first GC part=2 victim line=5 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  +2.482s first GC part=1 victim line=8 vpc=11 ipc=53 free_lines=2 host_pgs=24320
  +2.490s first GC part=3 victim line=23 vpc=17 ipc=47 free_lines=2 host_pgs=24320
  +2.514s first GC part=0 victim line=6 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  stats part=0 host_pgs=107676 gc_pgs=270848 gc_cnt=5533 free_lines=1
  stats part=1 host_pgs=107691 gc_pgs=269622 gc_cnt=5514 free_lines=2
  stats part=2 host_pgs=107905 gc_pgs=275287 gc_cnt=5606 free_lines=1
  stats part=3 host_pgs=107709 gc_pgs=273691 gc_cnt=5578 free_lines=2
  (kernel) [65040.420493] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65040.434824] NVMeVirt: Virtual NVMe device closed
[wbuffix map128k bs16k r1]
  +2.477s first GC part=2 victim line=5 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  +2.486s first GC part=1 victim line=8 vpc=11 ipc=53 free_lines=2 host_pgs=24320
  +2.493s first GC part=3 victim line=16 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  +2.516s first GC part=0 victim line=6 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  stats part=0 host_pgs=106247 gc_pgs=269523 gc_cnt=5490 free_lines=1
  stats part=1 host_pgs=106542 gc_pgs=271664 gc_cnt=5528 free_lines=2
  stats part=2 host_pgs=106611 gc_pgs=276587 gc_cnt=5606 free_lines=2
  stats part=3 host_pgs=106524 gc_pgs=274877 gc_cnt=5578 free_lines=2
  (kernel) [65110.744093] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65110.758254] NVMeVirt: Virtual NVMe device closed
[wbuffix map128k bs32k r1]
  +2.477s first GC part=2 victim line=5 vpc=18 ipc=46 free_lines=2 host_pgs=24320
  +2.480s first GC part=1 victim line=9 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  +2.499s first GC part=3 victim line=23 vpc=17 ipc=47 free_lines=2 host_pgs=24320
  +2.537s first GC part=0 victim line=9 vpc=13 ipc=51 free_lines=2 host_pgs=24320
  stats part=0 host_pgs=98515 gc_pgs=277003 gc_cnt=5486 free_lines=1
  stats part=1 host_pgs=98478 gc_pgs=281130 gc_cnt=5550 free_lines=2
  stats part=2 host_pgs=98332 gc_pgs=279098 gc_cnt=5516 free_lines=2
  stats part=3 host_pgs=98288 gc_pgs=276328 gc_cnt=5472 free_lines=2
  (kernel) [65181.077800] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65181.091839] NVMeVirt: Virtual NVMe device closed
[wbuffix map128k bs64k r1]
  +2.474s first GC part=2 victim line=4 vpc=17 ipc=47 free_lines=2 host_pgs=24320
  +2.485s first GC part=1 victim line=8 vpc=14 ipc=50 free_lines=2 host_pgs=24320
  +2.491s first GC part=3 victim line=8 vpc=16 ipc=48 free_lines=2 host_pgs=24320
  +2.521s first GC part=0 victim line=13 vpc=17 ipc=47 free_lines=2 host_pgs=24320
  stats part=0 host_pgs=81890 gc_pgs=291319 gc_cnt=5450 free_lines=2
  stats part=1 host_pgs=81618 gc_pgs=288646 gc_cnt=5404 free_lines=1
  stats part=2 host_pgs=81759 gc_pgs=290933 gc_cnt=5442 free_lines=2
  stats part=3 host_pgs=81795 gc_pgs=289240 gc_cnt=5416 free_lines=1
  (kernel) [65251.399561] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65251.414016] NVMeVirt: Virtual NVMe device closed
[wbuffix map128k bs128k r1]
  +3.867s first GC part=1 victim line=186 vpc=54 ipc=10 free_lines=2 host_pgs=24320
  +3.879s first GC part=2 victim line=354 vpc=53 ipc=11 free_lines=2 host_pgs=24320
  +3.881s first GC part=3 victim line=244 vpc=53 ipc=11 free_lines=2 host_pgs=24320
  +3.895s first GC part=0 victim line=157 vpc=54 ipc=10 free_lines=2 host_pgs=24320
  stats part=0 host_pgs=100632 gc_pgs=264619 gc_cnt=5326 free_lines=2
  stats part=1 host_pgs=100597 gc_pgs=266635 gc_cnt=5357 free_lines=2
  stats part=2 host_pgs=100488 gc_pgs=266227 gc_cnt=5349 free_lines=2
  stats part=3 host_pgs=100474 gc_pgs=268285 gc_cnt=5381 free_lines=3
  (kernel) [65321.717358] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [65321.731492] NVMeVirt: Virtual NVMe device closed
```

### 11.2.7 1 초 평균 대역폭 시계열 (MiB/s, t=1..60 s, fio_bw.1.log 의 0.5 s 값 두 개 평균)
형식: variant map bs rep | gc_onset_s | 값 60개 (공백 구분)
```
base 4k 4k r1 | 6.302 | 2007 2005 2002 2002 1997 2036 252 129 150 154 182 181 178 206 178 183 182 189 207 196 173 190 180 208 189 185 208 191 178 203 210 200 203 207 223 209 241 215 229 234 238 256 271 283 305 330 371 408 494 551 1031 534 131 140 159 181 173 203 173 181
base 4k 8k r1 | 5.745 | 2216 2212 2212 2215 2208 1186 128 139 157 178 181 179 237 181 152 210 154 190 193 220 190 207 194 253 190 199 270 208 168 196 258 274 300 311 269 236 233 257 271 362 361 324 398 411 501 742 1363 123 139 147 170 193 182 192 187 198 189 192 201 212
base 4k 16k r1 | 5.697 | 2234 2232 2233 2233 2233 1092 130 146 167 187 208 232 222 204 220 228 232 239 243 248 257 267 272 286 291 306 316 332 350 369 394 428 461 507 587 706 936 1472 127 140 158 179 201 226 240 204 211 222 231 236 246 244 250 262 268 286 288 302 315 322
base 4k 32k r1 | 5.696 | 2233 2233 2233 2233 2233 1098 137 151 169 188 211 231 222 207 217 227 232 239 245 253 256 270 272 288 292 304 314 336 358 368 401 432 465 526 598 735 1018 1291 133 147 164 184 205 228 228 204 218 230 234 241 243 253 256 261 277 278 298 304 316 330
base 4k 64k r1 | 5.698 | 2235 2233 2233 2231 2233 1104 144 156 174 193 214 236 221 212 217 225 238 237 251 257 268 270 276 289 302 310 322 345 363 393 405 447 490 558 650 817 1440 595 147 161 178 201 217 229 216 212 219 235 239 247 246 260 264 272 283 288 298 317 331 344
base 4k 128k r1 | 5.699 | 2235 2233 2233 2233 2233 1112 159 169 183 202 219 229 224 224 233 243 251 257 260 264 271 283 285 301 318 331 341 375 390 423 448 491 562 652 831 1422 676 159 170 188 208 220 226 226 229 231 239 248 254 258 259 278 278 294 304 313 331 347 372 387
base 8k 4k r1 | 5.685 | 1128 1116 1116 1116 1117 828 512 454 404 358 325 299 274 251 231 215 202 192 184 179 174 172 168 163 158 149 148 141 132 131 131 134 134 132 131 132 133 132 133 132 131 132 132 133 132 131 133 130 134 133 132 132 131 130 132 132 132 132 131 131
base 8k 8k r1 | 5.821 | 2176 2183 2182 2183 2176 1343 132 136 149 165 170 175 192 170 182 179 162 168 177 175 202 174 191 203 201 189 199 219 214 190 189 224 231 218 213 211 222 248 230 242 267 272 281 302 341 362 397 484 606 1102 567 124 141 148 162 178 189 175 170 161
base 8k 16k r1 | 5.782 | 2202 2192 2199 2201 2196 1258 130 142 161 179 197 221 204 188 187 202 208 190 199 217 225 198 247 239 195 227 256 212 251 231 203 259 255 238 295 307 314 335 340 436 390 527 494 663 1468 128 143 154 169 175 202 186 202 200 191 178 171 213 210 214
base 8k 32k r1 | 5.696 | 2234 2233 2233 2233 2233 1098 137 151 169 188 211 231 222 208 214 225 235 240 244 249 261 265 280 283 297 301 324 330 355 372 396 432 471 523 600 724 1013 1304 132 146 162 183 209 228 228 203 216 227 238 241 243 250 256 262 274 280 297 302 314 326
base 8k 64k r1 | 5.698 | 2235 2229 2233 2233 2233 1105 144 156 174 193 214 236 221 214 217 225 237 237 250 261 264 270 281 285 303 310 322 345 364 392 406 449 493 558 651 828 1454 565 147 161 179 202 217 229 218 208 222 233 238 247 247 258 260 273 284 287 300 314 328 346
base 8k 128k r1 | 5.698 | 2234 2233 2233 2233 2231 1113 157 171 183 202 219 227 226 224 234 245 253 256 258 268 265 282 293 299 318 325 349 360 385 413 448 498 556 656 821 1385 733 159 170 188 205 222 226 226 228 234 236 248 256 260 268 272 284 292 308 322 331 352 371 394
base 16k 4k r1 | 5.668 | 570 558 558 558 558 431 291 276 260 243 223 203 189 181 171 162 155 149 142 139 134 130 128 127 126 124 122 122 120 119 118 117 115 114 112 110 108 106 104 102 99 97 96 94 93 91 90 88 87 86 85 84 82 82 81 80 79 77 77 76
base 16k 8k r1 | 5.666 | 1138 1117 1116 1116 1115 849 526 468 429 378 331 304 277 259 251 244 238 231 223 214 200 188 176 164 152 144 138 136 135 135 134 133 133 133 133 133 134 134 134 133 134 134 135 134 133 134 133 134 134 133 133 133 134 133 134 134 134 134 133 133
base 16k 16k r1 | 5.924 | 2141 2141 2142 2149 2140 1512 136 136 144 148 167 180 188 168 177 179 164 173 188 188 192 190 196 193 186 202 190 207 218 209 199 214 237 217 237 218 241 237 249 240 265 266 286 312 314 352 393 454 660 1288 356 132 152 155 168 170 174 177 172 172
base 16k 32k r1 | 5.846 | 2177 2175 2169 2167 2174 1378 137 148 160 178 194 196 200 189 199 171 220 200 205 175 224 223 243 212 235 224 232 239 249 230 242 262 282 257 318 360 324 322 360 425 520 508 596 1222 645 139 155 164 182 201 204 208 193 200 183 219 188 198 210 224
base 16k 64k r1 | 5.690 | 2235 2233 2233 2233 2233 1101 144 156 174 193 216 234 221 214 217 225 237 237 251 261 264 270 280 286 303 310 322 345 364 392 406 449 493 560 651 834 1463 549 150 160 181 198 217 233 213 209 225 230 243 241 249 246 264 269 283 291 304 314 333 345
base 16k 128k r1 | 5.697 | 2234 2233 2233 2233 2233 1110 157 171 183 202 219 229 225 224 234 245 253 256 259 269 270 282 288 305 312 332 346 356 388 418 441 498 563 650 825 1399 716 159 174 185 209 223 222 227 228 237 235 244 258 256 267 276 280 286 303 312 336 347 370 389
base 32k 4k r1 | 5.636 | 291 279 278 280 278 224 153 145 138 131 120 110 102 99 95 92 90 89 88 86 85 83 83 81 80 77 77 74 73 71 69 67 65 63 63 62 60 60 58 57 56 55 54 54 53 52 52 51 50 49 49 48 48 47 47 47 47 46 46 45
base 32k 8k r1 | 5.639 | 582 557 557 559 557 446 300 284 267 250 228 208 197 190 182 178 175 173 170 167 164 162 156 150 147 142 137 132 129 126 123 119 116 112 110 107 105 104 102 100 98 96 94 92 91 90 89 88 87 85 84 83 82 81 81 79 78 78 77 76
wbuffix 4k 4k r1 | 6.306 | 2004 2001 2004 1995 1999 2040 258 129 146 152 176 176 204 211 167 177 177 198 206 186 175 191 193 171 177 198 196 204 197 194 209 198 192 240 231 209 212 221 250 234 245 284 279 292 347 344 348 414 495 728 1233 125 134 153 165 176 169 188 177 172
wbuffix 4k 4k r2 | 6.302 | 2006 1998 2002 1997 2003 2043 250 129 148 156 170 170 180 186 169 156 175 165 204 199 170 183 185 188 177 194 213 184 230 188 194 189 177 239 211 231 203 212 218 233 240 254 261 277 300 335 335 392 461 652 1105 627 125 136 160 180 160 183 178 173
wbuffix 4k 8k r1 | 5.746 | 2217 2210 2208 2214 2211 1188 126 144 160 179 182 180 236 175 178 207 213 195 154 154 195 232 247 228 186 255 229 271 237 287 250 245 254 216 222 263 348 289 351 416 324 360 581 717 1036 802 130 146 165 182 201 156 221 188 192 199 201 213 199 211
wbuffix 4k 8k r2 | 5.743 | 2217 2212 2212 2215 2210 1182 126 143 156 178 190 203 225 187 154 196 177 212 188 182 230 201 254 240 240 272 165 167 270 224 206 230 240 199 309 299 332 317 295 284 369 495 429 481 731 1435 124 134 152 161 194 206 242 192 203 219 169 196 158 235
wbuffix 4k 16k r1 | 5.690 | 2236 2233 2233 2233 2233 1090 130 145 162 189 208 232 226 204 216 228 233 244 240 247 262 261 277 280 292 305 321 329 347 371 397 422 466 516 586 693 940 1475 127 139 157 178 205 226 240 200 211 226 232 237 242 250 246 260 274 278 292 296 318 328
wbuffix 4k 16k r2 | 5.696 | 2234 2233 2233 2233 2233 1090 130 146 164 189 208 232 222 204 220 228 233 240 245 248 255 267 272 283 293 308 314 333 348 369 396 429 463 511 582 705 940 1467 127 141 158 179 201 226 240 205 211 222 231 240 243 242 247 265 270 283 287 302 312 328
wbuffix 4k 32k r1 | 5.696 | 2234 2233 2233 2233 2233 1098 137 151 169 188 211 231 222 208 215 224 237 238 244 254 256 266 280 282 296 303 320 337 350 370 399 426 475 516 606 719 1014 1313 133 144 164 184 205 232 233 210 216 227 236 242 243 250 256 263 276 278 299 305 315 330
wbuffix 4k 32k r2 | 5.696 | 2234 2233 2233 2233 2233 1098 137 148 169 190 212 231 222 208 214 224 235 240 244 249 260 264 274 289 290 308 323 329 356 373 400 427 468 520 595 726 1008 1324 132 147 164 184 205 228 228 205 215 232 232 240 242 250 258 264 275 277 298 300 317 333
wbuffix 4k 64k r1 | 5.697 | 2235 2233 2233 2233 2233 1101 144 156 174 193 214 235 221 210 220 225 238 237 251 256 269 270 276 290 303 310 322 345 364 384 413 448 494 547 652 830 1439 588 147 161 178 198 217 234 214 211 223 229 243 242 252 253 265 271 280 293 300 313 330 343
wbuffix 4k 64k r2 | 5.690 | 2235 2233 2233 2233 2233 1102 144 156 174 193 218 231 221 214 217 227 235 240 248 261 264 270 276 290 303 310 322 345 364 391 406 449 493 549 659 821 1449 578 147 161 178 198 221 230 214 212 222 229 243 242 252 253 265 272 278 292 300 314 329 344
wbuffix 4k 128k r1 | 5.697 | 2234 2233 2234 2232 2233 1111 157 171 183 202 219 226 228 224 233 245 254 256 260 266 267 281 295 300 315 319 347 368 389 404 451 485 556 636 819 1312 835 161 170 188 204 221 227 223 228 237 239 249 253 260 266 272 278 292 298 322 329 348 368 393
wbuffix 4k 128k r2 | 5.697 | 2234 2233 2233 2233 2233 1111 157 171 183 202 219 225 229 224 234 245 253 256 258 268 265 282 294 298 316 323 346 361 392 410 449 487 557 657 824 1386 740 160 170 188 204 222 227 228 228 231 238 246 253 258 262 276 279 287 304 312 338 352 369 394
wbuffix 8k 4k r1 | 5.811 | 1090 1092 1093 1091 1091 777 289 297 268 280 216 214 201 191 193 181 167 157 150 142 135 130 131 121 118 124 112 111 108 119 106 104 101 106 105 93 94 95 84 87 82 83 83 75 80 81 82 84 82 81 86 84 79 80 85 86 80 84 78 84
wbuffix 8k 4k r2 | 5.817 | 1090 1091 1093 1091 1092 777 291 297 263 282 215 212 202 191 200 179 167 156 151 141 139 133 124 123 120 123 111 109 103 126 118 103 104 95 105 94 92 95 85 94 88 82 82 82 78 82 82 82 83 75 81 80 84 82 77 86 80 76 78 83
wbuffix 8k 8k r1 | 5.821 | 2181 2187 2181 2182 2179 1328 130 138 143 158 174 177 199 172 178 180 175 159 176 180 180 196 192 196 202 187 201 208 190 203 222 240 213 198 211 220 228 252 247 263 260 271 297 301 335 362 399 472 575 1009 638 130 140 145 160 157 185 185 181 159
wbuffix 8k 8k r2 | 5.821 | 2180 2187 2181 2182 2180 1328 131 137 150 155 167 181 178 178 169 168 171 175 179 185 170 192 185 169 178 195 197 210 195 197 198 196 227 206 215 203 236 216 223 232 250 279 268 286 303 342 347 389 457 575 988 675 130 143 140 162 160 179 174 169
wbuffix 8k 16k r1 | 5.777 | 2202 2198 2204 2201 2197 1247 130 141 161 174 156 213 201 194 188 196 210 207 216 200 188 186 191 202 222 210 217 228 226 250 250 215 290 226 314 255 304 270 282 384 377 351 414 460 644 1168 603 134 150 171 174 201 200 220 186 212 197 184 206 211
wbuffix 8k 16k r2 | 5.777 | 2202 2198 2204 2202 2197 1247 132 141 158 173 194 221 200 182 184 187 196 186 227 184 208 235 207 183 245 248 212 176 217 236 247 259 345 241 222 272 279 262 319 305 367 421 476 647 855 1208 128 146 160 174 181 199 226 176 190 216 225 220 196 201
wbuffix 8k 32k r1 | 5.696 | 2234 2233 2233 2233 2233 1097 137 151 166 188 215 231 222 208 215 229 232 239 244 254 250 263 278 284 296 303 321 336 356 374 392 421 462 524 595 729 1010 1310 132 147 164 184 205 228 231 206 215 229 233 243 246 245 257 268 271 283 291 310 311 330
wbuffix 8k 32k r2 | 5.696 | 2234 2233 2233 2233 2233 1098 137 151 167 190 211 231 222 208 215 229 232 239 247 252 256 267 276 286 295 309 316 336 355 374 399 429 464 525 594 731 1013 1303 132 146 163 182 206 229 227 204 217 227 238 241 242 250 257 262 275 277 297 301 314 324
wbuffix 8k 64k r1 | 5.697 | 2235 2233 2233 2233 2233 1101 144 156 174 193 216 233 221 212 218 225 238 237 251 256 269 270 276 291 303 310 322 345 364 386 411 449 493 548 658 824 1449 578 147 161 178 198 221 229 215 211 222 233 238 245 249 258 260 273 282 290 300 314 328 346
wbuffix 8k 64k r2 | 5.697 | 2235 2233 2233 2233 2232 1103 144 156 174 193 218 231 221 214 217 229 233 239 248 261 264 270 278 288 303 310 322 345 364 392 406 449 494 553 656 820 1454 572 147 161 178 202 217 229 218 208 222 232 238 247 247 258 262 270 283 293 299 310 332 348
wbuffix 8k 128k r1 | 5.697 | 2234 2233 2233 2233 2233 1111 157 171 183 202 219 226 228 224 234 245 253 256 258 268 265 285 290 299 318 328 346 360 385 417 444 498 561 651 825 1389 726 159 170 188 205 223 226 227 225 235 238 244 253 256 267 281 280 286 300 315 336 341 373 390
wbuffix 8k 128k r2 | 5.697 | 2234 2233 2233 2233 2233 1111 157 171 183 202 219 229 225 224 234 245 253 256 258 271 268 282 288 305 312 332 346 357 386 419 441 498 563 650 825 1398 715 159 172 187 209 219 226 227 228 237 234 244 253 256 271 277 280 286 301 314 336 340 370 389
wbuffix 16k 4k r1 | 5.918 | 536 533 538 536 535 430 176 163 176 165 150 140 142 133 121 122 112 116 107 109 96 99 95 89 94 85 80 79 78 83 75 74 83 73 67 75 65 65 64 72 64 64 61 60 62 61 58 56 63 57 56 61 55 53 56 61 54 53 56 53
wbuffix 16k 4k r2 | 5.920 | 536 533 538 536 535 430 175 163 177 163 151 142 140 131 120 121 111 112 107 103 97 101 95 90 94 89 83 81 79 80 75 75 72 72 70 70 71 70 67 62 64 64 63 61 61 59 60 60 58 57 56 55 53 56 56 57 59 55 54 59
wbuffix 16k 8k r1 | 5.907 | 1071 1068 1075 1075 1072 837 324 287 287 268 243 228 209 205 190 177 180 154 152 143 144 134 127 125 113 112 129 115 109 115 109 115 92 99 95 89 99 90 93 85 82 80 82 80 81 80 80 78 89 85 84 80 80 85 82 79 78 80 78 80
wbuffix 16k 8k r2 | 5.909 | 1071 1071 1076 1075 1071 834 325 289 285 262 247 228 198 201 182 178 184 156 151 142 143 130 144 133 120 134 115 108 109 112 103 101 107 100 101 106 89 86 94 88 87 79 83 80 81 81 82 83 84 80 81 80 80 80 78 84 84 81 82 82
wbuffix 16k 16k r1 | 5.924 | 2141 2141 2143 2149 2140 1512 136 139 146 153 171 178 180 178 173 174 180 178 178 199 174 188 185 184 194 194 197 199 215 197 196 232 233 215 215 261 235 257 239 259 280 283 288 312 344 371 406 414 574 1234 416 128 144 154 165 175 171 177 182 169
wbuffix 16k 16k r2 | 5.924 | 2141 2141 2143 2149 2140 1512 136 131 146 153 181 163 173 173 186 170 170 181 184 192 186 190 195 188 199 185 201 196 205 200 219 218 227 202 222 204 222 247 246 263 266 273 284 301 336 346 383 442 606 957 784 129 144 152 150 177 183 178 180 173
wbuffix 16k 32k r1 | 5.846 | 2177 2175 2169 2167 2173 1378 139 148 159 175 198 192 198 194 200 206 206 215 182 200 206 216 220 193 224 193 246 225 270 226 223 264 236 232 318 243 325 271 327 324 383 468 508 567 837 1137 135 149 163 176 196 210 187 205 200 206 205 196 207 213
wbuffix 16k 32k r2 | 5.847 | 2176 2174 2169 2167 2174 1378 138 147 161 171 197 183 201 193 198 214 188 210 186 218 231 245 241 206 224 239 223 261 266 210 278 279 278 242 320 280 361 401 372 356 494 606 793 1438 135 143 162 173 185 192 205 192 197 183 203 228 198 201 202 213
wbuffix 16k 64k r1 | 5.697 | 2235 2233 2233 2233 2233 1101 144 156 174 193 216 234 221 214 217 225 238 237 251 257 268 270 276 290 303 310 322 345 364 392 406 449 493 552 657 821 1453 574 147 161 178 198 221 229 218 209 222 233 238 247 247 258 260 273 284 287 300 314 328 346
wbuffix 16k 64k r2 | 5.697 | 2235 2233 2233 2233 2233 1101 144 156 174 193 217 233 221 213 217 225 238 237 251 259 266 270 276 290 303 310 322 345 364 388 410 449 493 550 658 821 1450 578 147 161 178 198 221 229 214 212 221 231 245 242 246 252 264 275 278 291 308 312 327 341
wbuffix 16k 128k r1 | 5.694 | 2234 2233 2233 2233 2233 1110 157 171 183 202 219 229 225 224 234 245 253 256 258 268 265 286 290 299 318 328 346 360 385 419 442 497 554 654 758 1213 746 158 171 188 207 219 227 228 229 236 234 250 259 260 268 272 282 287 304 316 331 346 372 389
wbuffix 32k 4k r1 | 6.067 | 261 260 259 261 260 235 101 89 85 85 81 80 82 70 70 65 62 57 57 56 53 54 52 51 47 48 47 44 44 42 44 40 41 40 39 38 38 38 36 38 36 35 35 36 34 32 33 33 31 33 32 30 33 32 31 31 30 30 29 30
wbuffix 32k 8k r1 | 6.070 | 521 520 519 521 522 472 181 182 178 154 166 162 155 132 121 126 119 108 111 108 106 101 94 93 87 96 83 83 82 78 80 75 78 75 77 67 69 66 66 66 63 65 63 67 65 64 60 62 66 58 61 58 60 61 56 59 54 56 53 54
wbuffix 32k 16k r1 | 6.069 | 1039 1042 1040 1042 1044 952 364 314 303 272 245 229 218 211 185 180 168 155 155 147 136 138 132 120 128 125 117 116 116 115 106 109 107 104 100 93 95 92 93 81 83 81 82 81 84 81 80 81 81 80 78 79 83 85 79 85 83 79 83 81
wbuffix 32k 32k r1 | 6.099 | 2084 2079 2068 2079 2082 1804 138 143 149 157 160 175 179 178 186 179 174 184 190 189 188 191 196 190 195 203 213 212 210 203 232 229 249 231 231 237 262 255 258 269 281 298 305 337 374 406 468 599 1278 407 142 148 154 158 173 179 183 184 190 176
wbuffix 32k 64k r1 | 5.978 | 2130 2125 2115 2120 2120 1613 147 150 168 181 190 176 207 200 186 195 200 220 210 219 221 216 234 263 187 249 232 260 241 270 270 278 274 264 281 294 319 346 342 484 548 613 889 1241 142 149 166 165 194 208 192 205 176 196 203 222 200 215 210 237
wbuffix 32k 128k r1 | 5.698 | 2234 2233 2233 2232 2233 1112 157 171 183 202 219 229 225 224 234 245 253 256 259 269 267 286 290 303 315 332 346 362 389 401 446 492 568 646 827 1364 753 159 173 184 208 217 226 227 227 233 240 250 254 258 264 271 280 287 309 316 330 345 356 400
wbuffix 64k 4k r1 | 3.675 | 220 222 222 149 85 81 74 66 62 56 53 51 49 47 45 44 41 40 42 39 39 37 37 36 36 34 33 34 34 32 30 30 29 30 29 29 29 29 27 27 28 27 27 26 26 26 25 26 25 25 25 24 24 24 24 23 23 23 23 23
wbuffix 64k 8k r1 | 3.671 | 440 444 444 298 171 158 147 137 119 109 107 105 94 93 87 86 82 81 81 77 77 76 71 73 69 69 64 67 65 64 62 58 60 58 59 57 57 56 55 55 53 52 53 50 50 50 49 48 49 49 47 47 47 47 45 46 45 46 45 45
wbuffix 64k 16k r1 | 3.675 | 881 888 889 591 331 312 281 264 233 212 202 199 190 176 170 166 160 151 144 147 139 137 129 127 127 126 121 120 114 112 110 107 108 103 102 101 98 96 95 94 94 91 89 90 89 87 86 84 81 81 81 79 81 78 79 80 79 76 77 75
wbuffix 64k 32k r1 | 3.684 | 1764 1768 1772 1166 585 509 440 391 361 324 308 299 260 246 235 214 200 189 179 166 159 144 144 140 140 148 146 145 144 145 143 146 143 146 143 144 145 144 142 142 146 144 141 142 144 145 143 143 142 144 143 145 142 140 144 147 145 143 143 143
wbuffix 64k 64k r1 | 3.874 | 3353 3350 3346 2216 244 274 293 313 320 329 339 353 356 377 384 418 418 447 482 485 509 588 613 700 843 1273 1216 255 272 303 324 324 329 346 354 369 376 396 415 431 449 491 496 548 577 668 740 878 1970 265 262 294 300 322 326 330 343 355 370 394
wbuffix 64k 128k r1 | 3.881 | 3349 3346 3348 2228 266 272 308 331 331 337 348 370 384 399 421 441 457 490 523 568 634 695 741 1024 2043 272 270 297 318 339 342 346 368 381 392 405 436 454 489 516 562 586 670 748 890 1272 1288 260 284 308 331 342 338 357 371 374 392 409 440 457
wbuffix 128k 4k r1 | 2.476 | 170 171 99 66 58 51 45 40 38 35 33 31 29 27 27 25 25 24 23 22 22 20 20 21 20 19 19 19 18 18 17 17 17 17 16 16 16 16 16 16 15 15 15 15 15 15 15 14 15 14 15 14 14 14 14 14 14 14 13 14
wbuffix 128k 8k r1 | 2.474 | 340 341 196 133 118 100 89 80 74 70 64 62 59 55 54 52 48 48 46 45 43 42 40 41 40 39 37 37 35 36 35 35 34 34 33 32 32 32 32 31 31 30 31 31 30 29 29 29 30 29 29 28 28 28 28 28 28 28 27 27
wbuffix 128k 16k r1 | 2.477 | 680 681 391 265 235 200 175 162 149 137 130 121 113 107 106 100 94 95 89 88 83 82 78 79 76 75 72 71 71 69 69 67 66 67 66 64 63 62 62 62 58 60 59 59 59 58 59 57 57 58 55 55 55 55 54 54 54 55 55 53
wbuffix 128k 32k r1 | 2.477 | 1359 1359 767 508 443 384 333 305 277 252 236 223 208 198 190 180 166 167 164 158 153 145 140 138 133 130 129 128 125 122 121 116 116 113 112 111 109 107 106 105 102 101 104 100 96 100 94 97 98 98 101 104 94 95 98 95 95 98 97 97
wbuffix 128k 64k r1 | 2.474 | 2708 2724 1496 818 663 551 474 408 358 313 294 254 236 223 201 197 191 199 198 188 190 193 196 197 196 196 192 194 196 200 195 199 195 197 189 195 189 196 196 196 188 197 195 195 188 197 194 191 184 195 190 194 194 190 195 192 193 191 192 196
wbuffix 128k 128k r1 | 3.867 | 3358 3357 3357 2245 360 393 421 418 445 476 504 533 555 598 645 721 811 968 1350 2227 371 387 424 425 454 479 520 535 572 610 649 733 842 998 1358 2121 371 394 423 429 466 490 490 533 572 605 657 719 829 983 1332 2190 368 385 419 432 458 475 494 535
```

### 11.2.8 실험 전후 환경 차이 (env_before vs env_after_* 의 마지막 스냅샷; 날짜·부하·여유 메모리 줄 제외)
- env_after_stop:
  - 03_cpu.txt:
    `-CPU(s) scaling MHz:                      58%`
    `+CPU(s) scaling MHz:                      33%`
  - 08_nvmevirt_git.txt:
    `-5769378d46821c45595585c932522e4f76538fc6`
    `+2a462a3a518915e37fa313716bc9721801501e28`
    `+2a462a3 exp: keep going when a run fails; plot tool; report generators`
    `-f84fec2 admin: Support queues in device memory`
    `+ M EXPERIMENT_LOG_FOR_CLAUDE.md`
    `+ M exp/report/make_report.py`
    `+?? exp/report/audit_result.json`
    `+?? exp/report/audit_summary_ko.txt`
  - 09_block.txt:
    `-/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        101.15  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`
    `+/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        121.44  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`

### 11.2.9 run_all 로그 끝 40 줄 (원본 로그, 시각은 KST 로 변환)
```
[2026-10-08 15:29:06 KST] === [35/108] variant=wbuffix map=128k bs=64k rep=1 ===
    -> 340.7 MiB/s, 5450 IOPS, clat mean 5868.2 us
[2026-10-08 15:30:16 KST] === [36/108] variant=wbuffix map=128k bs=128k rep=1 ===
    -> 837.8 MiB/s, 6702 IOPS, clat mean 4770.3 us
[2026-10-08 15:31:26 KST] === [37/108] variant=wbuffix map=4k bs=4k rep=2 ===
    -> 417.6 MiB/s, 106915 IOPS, clat mean 298.3 us
[2026-10-08 15:32:37 KST] === [38/108] variant=wbuffix map=4k bs=8k rep=2 ===
    -> 438.0 MiB/s, 56064 IOPS, clat mean 569.5 us
[2026-10-08 15:33:47 KST] === [39/108] variant=wbuffix map=4k bs=16k rep=2 ===
    -> 480.9 MiB/s, 30778 IOPS, clat mean 1038.2 us
[2026-10-08 15:34:57 KST] === [40/108] variant=wbuffix map=4k bs=32k rep=2 ===
    -> 482.3 MiB/s, 15433 IOPS, clat mean 2071.6 us
[2026-10-08 15:36:08 KST] === [41/108] variant=wbuffix map=4k bs=64k rep=2 ===
    -> 486.3 MiB/s, 7780 IOPS, clat mean 4110.1 us
[2026-10-08 15:37:18 KST] === [42/108] variant=wbuffix map=4k bs=128k rep=2 ===
    -> 496.8 MiB/s, 3975 IOPS, clat mean 8046.2 us
[2026-10-08 15:38:29 KST] === [43/108] variant=wbuffix map=8k bs=4k rep=2 ===
    -> 216.6 MiB/s, 55453 IOPS, clat mean 576.0 us
[2026-10-08 15:39:39 KST] === [44/108] variant=wbuffix map=8k bs=8k rep=2 ===
    -> 416.9 MiB/s, 53361 IOPS, clat mean 598.5 us
[2026-10-08 15:40:49 KST] === [45/108] variant=wbuffix map=8k bs=16k rep=2 ===
    -> 439.1 MiB/s, 28099 IOPS, clat mean 1137.3 us
[2026-10-08 15:42:00 KST] === [46/108] variant=wbuffix map=8k bs=32k rep=2 ===
    -> 482.3 MiB/s, 15432 IOPS, clat mean 2071.7 us
[2026-10-08 15:43:10 KST] === [47/108] variant=wbuffix map=8k bs=64k rep=2 ===
    -> 486.4 MiB/s, 7782 IOPS, clat mean 4109.1 us
[2026-10-08 15:44:21 KST] === [48/108] variant=wbuffix map=8k bs=128k rep=2 ===
    -> 496.7 MiB/s, 3974 IOPS, clat mean 8047.7 us
[2026-10-08 15:45:31 KST] === [49/108] variant=wbuffix map=16k bs=4k rep=2 ===
    -> 129.7 MiB/s, 33200 IOPS, clat mean 962.8 us
[2026-10-08 15:46:41 KST] === [50/108] variant=wbuffix map=16k bs=8k rep=2 ===
    -> 218.0 MiB/s, 27904 IOPS, clat mean 1145.5 us
[2026-10-08 15:47:52 KST] === [51/108] variant=wbuffix map=16k bs=16k rep=2 ===
    -> 420.3 MiB/s, 26900 IOPS, clat mean 1188.1 us
[2026-10-08 15:49:02 KST] === [52/108] variant=wbuffix map=16k bs=32k rep=2 ===
    -> 444.9 MiB/s, 14236 IOPS, clat mean 2245.8 us
[2026-10-08 15:50:12 KST] === [53/108] variant=wbuffix map=16k bs=64k rep=2 ===
    -> 486.2 MiB/s, 7780 IOPS, clat mean 4110.3 us
[2026-10-08 15:51:23 KST] === [54/108] variant=wbuffix map=16k bs=128k rep=2 ===
[2026-10-08 15:51:36 KST] STOPPED by Claude at a run boundary (user changed the experiment design: maps/bs 4k,16k,32k + drop_caches comparison)
```

## 11.3 seq3x3_20261008  (묶음 경로 repo/exp/results/seq3x3_20261008/)

### 11.3.1 회차 목록
- merge: 완료 회차 27 (DONE 있음). run.log 첫 시각 2026-10-08 20:33:58 KST, 마지막 시각 2026-10-08 21:26:45 KST. chmodel 오류 줄 합계 0. chmodel>0 회차 0. kernel_warn>0 회차 0.
  - 미완료/없음 0: -
- wbuffix: 완료 회차 27 (DONE 있음). run.log 첫 시각 2026-10-08 20:23:24 KST, 마지막 시각 2026-10-08 21:16:12 KST. chmodel 오류 줄 합계 0. chmodel>0 회차 0. kernel_warn>0 회차 0.
  - 미완료/없음 0: -

### 11.3.2 조합별 행렬 (행 = 매핑 단위, 열 = fio bs). 칸 = mean ± std [min..max], n = 그 조합의 완료 회차 수(보통 3)
#### seq3x3_20261008 · merge · bw_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2086.665 ± 3.235 [2083.576..2090.029] | 2232.668 ± 0.087 [2232.570..2232.737] | 2232.757 ± 0.018 [2232.742..2232.776] |
| 16K | 2094.366 ± 5.324 [2089.913..2100.263] | 2232.558 ± 0.051 [2232.499..2232.594] | 2232.569 ± 0.063 [2232.498..2232.618] |
| 32K | 2094.615 ± 0.810 [2093.737..2095.334] | 2232.250 ± 0.039 [2232.209..2232.287] | 2232.258 ± 0.022 [2232.233..2232.272] |

#### seq3x3_20261008 · merge · iops
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 534186.464 ± 828.179 [533395.693..535047.566] | 142890.813 ± 5.574 [142884.552..142895.235] | 71448.237 ± 0.559 [71447.776..71448.859] |
| 16K | 536157.886 ± 1362.852 [535017.966..537667.422] | 142883.730 ± 3.269 [142879.985..142886.019] | 71442.209 ± 2.014 [71439.943..71443.793] |
| 32K | 536221.469 ± 207.414 [535996.817..536405.693] | 142864.008 ± 2.481 [142861.436..142866.386] | 71432.287 ± 0.704 [71431.476..71432.743] |

#### seq3x3_20261008 · merge · clat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 58.949 ± 0.092 [58.854..59.038] | 222.500 ± 0.023 [222.477..222.524] | 445.982 ± 0.023 [445.956..446.002] |
| 16K | 58.729 ± 0.149 [58.562..58.852] | 222.504 ± 0.015 [222.486..222.516] | 446.022 ± 0.037 [445.980..446.044] |
| 32K | 58.722 ± 0.022 [58.700..58.745] | 222.551 ± 0.008 [222.543..222.559] | 446.078 ± 0.015 [446.061..446.088] |

#### seq3x3_20261008 · merge · clat_p50_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 58.965 ± 0.296 [58.624..59.136] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] |
| 16K | 58.624 ± 0.000 [58.624..58.624] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] |
| 32K | 58.624 ± 0.000 [58.624..58.624] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] |

#### seq3x3_20261008 · merge · clat_p99_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 62.549 ± 0.296 [62.208..62.720] | 227.669 ± 1.182 [226.304..228.352] | 451.243 ± 2.365 [448.512..452.608] |
| 16K | 62.208 ± 0.000 [62.208..62.208] | 226.987 ± 1.182 [226.304..228.352] | 452.608 ± 0.000 [452.608..452.608] |
| 32K | 62.208 ± 0.000 [62.208..62.208] | 226.304 ± 0.000 [226.304..226.304] | 451.243 ± 2.365 [448.512..452.608] |

#### seq3x3_20261008 · merge · clat_p999_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 72.875 ± 0.591 [72.192..73.216] | 237.227 ± 1.182 [236.544..238.592] | 463.531 ± 2.365 [460.800..464.896] |
| 16K | 72.875 ± 1.564 [71.168..74.240] | 234.496 ± 0.000 [234.496..234.496] | 473.088 ± 0.000 [473.088..473.088] |
| 32K | 73.216 ± 1.024 [72.192..74.240] | 240.640 ± 0.000 [240.640..240.640] | 485.376 ± 0.000 [485.376..485.376] |

#### seq3x3_20261008 · merge · lat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 59.755 ± 0.093 [59.658..59.844] | 223.736 ± 0.008 [223.728..223.745] | 447.664 ± 0.004 [447.660..447.669] |
| 16K | 59.535 ± 0.152 [59.367..59.662] | 223.744 ± 0.005 [223.740..223.750] | 447.702 ± 0.015 [447.690..447.719] |
| 32K | 59.528 ± 0.023 [59.507..59.553] | 223.783 ± 0.001 [223.782..223.784] | 447.764 ± 0.005 [447.761..447.769] |

#### seq3x3_20261008 · merge · slat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.806 ± 0.002 [0.804..0.807] | 1.236 ± 0.015 [1.221..1.251] | 1.682 ± 0.028 [1.658..1.712] |
| 16K | 0.807 ± 0.004 [0.804..0.811] | 1.240 ± 0.013 [1.231..1.255] | 1.680 ± 0.035 [1.648..1.718] |
| 32K | 0.806 ± 0.003 [0.803..0.808] | 1.232 ± 0.008 [1.225..1.240] | 1.687 ± 0.013 [1.677..1.702] |

#### seq3x3_20261008 · merge · bw_first10s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2115.991 ± 3.662 [2112.255..2119.573] | 2233.111 ± 0.023 [2233.088..2233.133] | 2233.125 ± 0.027 [2233.094..2233.144] |
| 16K | 2123.641 ± 6.421 [2117.471..2130.287] | 2233.094 ± 0.044 [2233.051..2233.139] | 2233.073 ± 0.031 [2233.037..2233.091] |
| 32K | 2123.811 ± 0.955 [2122.938..2124.830] | 2233.047 ± 0.072 [2232.965..2233.098] | 2232.980 ± 0.232 [2232.719..2233.161] |

#### seq3x3_20261008 · merge · bw_last20s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2081.099 ± 3.548 [2078.226..2085.066] | 2232.911 ± 0.033 [2232.876..2232.942] | 2232.914 ± 0.011 [2232.901..2232.922] |
| 16K | 2088.704 ± 5.212 [2084.062..2094.343] | 2232.697 ± 0.051 [2232.639..2232.737] | 2232.710 ± 0.063 [2232.639..2232.757] |
| 32K | 2088.978 ± 0.657 [2088.225..2089.427] | 2232.312 ± 0.050 [2232.269..2232.367] | 2232.319 ± 0.051 [2232.261..2232.357] |

#### seq3x3_20261008 · merge · gc_onset_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 5.929 ± 0.011 [5.918..5.940] | 5.693 ± 0.000 [5.693..5.693] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.901 ± 0.018 [5.885..5.920] | 5.693 ± 0.000 [5.693..5.693] | 5.693 ± 0.000 [5.693..5.693] |
| 32K | 5.905 ± 0.003 [5.903..5.909] | 5.693 ± 0.000 [5.693..5.693] | 5.694 ± 0.001 [5.693..5.694] |

#### seq3x3_20261008 · merge · gc_onset_last_part_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 5.929 ± 0.011 [5.918..5.940] | 5.693 ± 0.000 [5.693..5.693] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.901 ± 0.018 [5.885..5.921] | 5.693 ± 0.000 [5.693..5.693] | 5.693 ± 0.000 [5.693..5.693] |
| 32K | 5.905 ± 0.003 [5.903..5.909] | 5.693 ± 0.000 [5.693..5.693] | 5.694 ± 0.001 [5.693..5.695] |

#### seq3x3_20261008 · merge · bw_pre_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2142.099 ± 4.363 [2137.440..2146.087] | 2233.046 ± 0.039 [2233.023..2233.091] | 2233.066 ± 0.028 [2233.034..2233.085] |
| 16K | 2152.276 ± 6.458 [2145.577..2158.462] | 2233.042 ± 0.055 [2233.003..2233.105] | 2233.011 ± 0.034 [2232.977..2233.045] |
| 32K | 2150.979 ± 1.220 [2149.599..2151.918] | 2232.967 ± 0.110 [2232.844..2233.054] | 2233.060 ± 0.119 [2232.977..2233.196] |

#### seq3x3_20261008 · merge · bw_post_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2081.382 ± 3.150 [2078.428..2084.697] | 2232.874 ± 0.089 [2232.772..2232.939] | 2232.954 ± 0.018 [2232.941..2232.974] |
| 16K | 2088.819 ± 5.262 [2084.587..2094.710] | 2232.748 ± 0.055 [2232.684..2232.785] | 2232.743 ± 0.059 [2232.677..2232.792] |
| 32K | 2089.222 ± 0.777 [2088.415..2089.966] | 2232.405 ± 0.025 [2232.381..2232.432] | 2232.393 ± 0.027 [2232.362..2232.409] |

#### seq3x3_20261008 · merge · gc_cnt
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 14132.000 ± 24.000 [14108..14156] | 15228.000 ± 0.000 [15228..15228] | 15228.000 ± 0.000 [15228..15228] |
| 16K | 14190.667 ± 41.053 [14156..14236] | 15227.667 ± 0.577 [15227..15228] | 15227.333 ± 1.155 [15226..15228] |
| 32K | 14190.667 ± 6.110 [14184..14196] | 15224.000 ± 0.000 [15224..15224] | 15224.000 ± 0.000 [15224..15224] |

#### seq3x3_20261008 · merge · ftl_host_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 32051722 ± 49691.574 [32004275..32103389] | 34294367 ± 1337.761 [34292864..34295428] | 34295725 ± 268.487 [34295504..34296024] |
| 16K | 8042596 ± 20440.689 [8025505..8065239] | 8573167 ± 196.167 [8572942..8573304] | 8573208 ± 241.669 [8572936..8573398] |
| 32K | 4021746 ± 1554.222 [4020064..4023129] | 4285997 ± 74.182 [4285920..4286068] | 4286009 ± 42.253 [4285960..4286036] |

#### seq3x3_20261008 · merge · ftl_gc_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · waf_gc
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 16K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 32K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |

#### seq3x3_20261008 · merge · waf_total
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 16K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 32K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |

#### seq3x3_20261008 · merge · written_GiB
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 122.268 ± 0.190 [122.087..122.465] | 130.823 ± 0.005 [130.817..130.827] | 130.828 ± 0.001 [130.827..130.829] |
| 16K | 122.719 ± 0.312 [122.458..123.064] | 130.816 ± 0.003 [130.813..130.818] | 130.817 ± 0.004 [130.813..130.820] |
| 32K | 122.733 ± 0.047 [122.682..122.776] | 130.798 ± 0.002 [130.796..130.800] | 130.799 ± 0.001 [130.797..130.799] |

#### seq3x3_20261008 · merge · fill_ratio
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 10.903 ± 0.017 [10.887..10.921] | 11.666 ± 0.000 [11.665..11.666] | 11.666 ± 0.000 [11.666..11.667] |
| 16K | 10.943 ± 0.028 [10.920..10.974] | 11.665 ± 0.000 [11.665..11.666] | 11.665 ± 0.000 [11.665..11.666] |
| 32K | 10.945 ± 0.004 [10.940..10.948] | 11.664 ± 0.000 [11.664..11.664] | 11.664 ± 0.000 [11.664..11.664] |

#### seq3x3_20261008 · merge · chmodel_msgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · kernel_warn
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · blk_wr_ios
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 32051722 ± 49691.574 [32004275..32103389] | 8573592 ± 334.440 [8573216..8573857] | 4286966 ± 33.561 [4286938..4287003] |
| 16K | 32170009 ± 81772.494 [32101613..32260583] | 8573167 ± 196.167 [8572942..8573304] | 4286604 ± 120.835 [4286468..4286699] |
| 32K | 32173824 ± 12445.076 [32160345..32184878] | 8571983 ± 148.843 [8571829..8572126] | 4286009 ± 42.253 [4285960..4286036] |

#### seq3x3_20261008 · merge · blk_wr_merges
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · blk_avg_req_KiB
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 4.000 ± 0.000 [4.000..4.000] | 16.000 ± 0.000 [16.000..16.000] | 32.000 ± 0.000 [32.000..32.000] |
| 16K | 4.000 ± 0.000 [4.000..4.000] | 16.000 ± 0.000 [16.000..16.000] | 32.000 ± 0.000 [32.000..32.000] |
| 32K | 4.000 ± 0.000 [4.000..4.000] | 16.000 ± 0.000 [16.000..16.000] | 32.000 ± 0.000 [32.000..32.000] |

#### seq3x3_20261008 · merge · mg_open
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 8042597 ± 20440.689 [8025506..8065240] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 4021747 ± 1554.126 [4020065..4023130] | 4285997 ± 74.661 [4285920..4286069] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · mg_merge
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 24127413 ± 61331.807 [24076107..24195343] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 28152078 ± 10890.956 [28140280..28161748] | 4285986 ± 74.182 [4285909..4286057] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · mg_full
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 8042426 ± 20447.979 [8025318..8065073] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 4021709 ± 1558.249 [4020020..4023091] | 4285986 ± 74.182 [4285909..4286057] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · mg_evict
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 169.333 ± 16.258 [155..187] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 37.333 ± 7.024 [30..44] | 11.000 ± 0.000 [11..11] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · merge · mg_direct
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 32051722 ± 49691.574 [32004275..32103389] | 34294367 ± 1337.761 [34292864..34295428] | 34295725 ± 268.487 [34295504..34296024] |
| 16K | 0.000 ± 0.000 [0..0] | 8573167 ± 196.167 [8572942..8573304] | 8573208 ± 241.669 [8572936..8573398] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 4286009 ± 42.253 [4285960..4286036] |

#### seq3x3_20261008 · merge · mg_still_open
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 1.000 ± 0.000 [1..1] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.667 ± 0.577 [0..1] | 0.333 ± 0.577 [0..1] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · wbuffix · bw_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2089.670 ± 8.381 [2081.111..2097.861] | 2232.405 ± 0.527 [2231.798..2232.731] | 2232.728 ± 0.034 [2232.699..2232.765] |
| 16K | 334.894 ± 0.510 [334.306..335.192] | 2232.519 ± 0.046 [2232.480..2232.569] | 2232.467 ± 0.209 [2232.228..2232.613] |
| 32K | 209.509 ± 0.003 [209.506..209.513] | 369.044 ± 0.017 [369.034..369.063] | 2232.158 ± 0.213 [2231.913..2232.298] |

#### seq3x3_20261008 · wbuffix · iops
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 534955.567 ± 2145.556 [532764.604..537052.632] | 142873.991 ± 33.695 [142835.119..142894.868] | 71447.298 ± 1.084 [71446.376..71448.493] |
| 16K | 85733.000 ± 130.444 [85582.381..85809.270] | 142881.230 ± 2.933 [142878.752..142884.469] | 71438.948 ± 6.671 [71431.309..71443.626] |
| 32K | 53634.553 ± 0.894 [53633.659..53635.447] | 23618.855 ± 1.055 [23618.246..23620.074] | 71429.065 ± 6.813 [71421.226..71433.559] |

#### seq3x3_20261008 · wbuffix · clat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 58.864 ± 0.237 [58.633..59.106] | 222.536 ± 0.063 [222.492..222.609] | 446.002 ± 0.023 [445.986..446.028] |
| 16K | 372.220 ± 0.571 [371.886..372.880] | 222.505 ± 0.014 [222.489..222.516] | 446.045 ± 0.043 [446.020..446.095] |
| 32K | 595.501 ± 0.015 [595.485..595.515] | 1353.368 ± 0.077 [1353.280..1353.416] | 446.095 ± 0.054 [446.046..446.153] |

#### seq3x3_20261008 · wbuffix · clat_p50_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 58.795 ± 0.296 [58.624..59.136] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] |
| 16K | 222.208 ± 0.000 [222.208..222.208] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] |
| 32K | 452.608 ± 0.000 [452.608..452.608] | 470.357 ± 2.365 [468.992..473.088] | 444.416 ± 0.000 [444.416..444.416] |

#### seq3x3_20261008 · wbuffix · clat_p99_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 62.549 ± 0.296 [62.208..62.720] | 226.987 ± 1.182 [226.304..228.352] | 452.608 ± 0.000 [452.608..452.608] |
| 16K | 3642.709 ± 18.919 [3620.864..3653.632] | 226.304 ± 0.000 [226.304..226.304] | 449.877 ± 2.365 [448.512..452.608] |
| 32K | 2255.531 ± 18.919 [2244.608..2277.376] | 8355.840 ± 0.000 [8355.840..8355.840] | 449.877 ± 2.365 [448.512..452.608] |

#### seq3x3_20261008 · wbuffix · clat_p999_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 73.899 ± 1.182 [73.216..75.264] | 238.592 ± 0.000 [238.592..238.592] | 464.896 ± 0.000 [464.896..464.896] |
| 16K | 14352.384 ± 0.000 [14352.384..14352.384] | 234.496 ± 0.000 [234.496..234.496] | 474.453 ± 2.365 [473.088..477.184] |
| 32K | 2342.912 ± 0.000 [2342.912..2342.912] | 8978.432 ± 0.000 [8978.432..8978.432] | 488.107 ± 4.730 [485.376..493.568] |

#### seq3x3_20261008 · wbuffix · lat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 59.670 ± 0.240 [59.436..59.915] | 223.763 ± 0.054 [223.727..223.825] | 447.671 ± 0.007 [447.663..447.678] |
| 16K | 373.072 ± 0.568 [372.739..373.728] | 223.748 ± 0.006 [223.741..223.753] | 447.724 ± 0.040 [447.695..447.770] |
| 32K | 596.429 ± 0.013 [596.414..596.437] | 1354.626 ± 0.066 [1354.549..1354.667] | 447.785 ± 0.045 [447.755..447.836] |

#### seq3x3_20261008 · wbuffix · slat_mean_us
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.806 ± 0.003 [0.803..0.809] | 1.226 ± 0.015 [1.216..1.243] | 1.669 ± 0.017 [1.649..1.680] |
| 16K | 0.852 ± 0.004 [0.848..0.855] | 1.243 ± 0.009 [1.234..1.252] | 1.678 ± 0.006 [1.675..1.685] |
| 32K | 0.928 ± 0.005 [0.922..0.933] | 1.257 ± 0.013 [1.245..1.270] | 1.690 ± 0.017 [1.677..1.709] |

#### seq3x3_20261008 · wbuffix · bw_first10s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2121.134 ± 10.702 [2110.275..2131.672] | 2232.963 ± 0.267 [2232.659..2233.156] | 2233.119 ± 0.043 [2233.075..2233.161] |
| 16K | 454.172 ± 0.019 [454.159..454.194] | 2233.109 ± 0.070 [2233.028..2233.150] | 2233.081 ± 0.017 [2233.061..2233.091] |
| 32K | 246.175 ± 0.003 [246.172..246.178] | 786.593 ± 0.163 [786.498..786.781] | 2232.966 ± 0.161 [2232.781..2233.081] |

#### seq3x3_20261008 · wbuffix · bw_last20s_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2083.166 ± 7.902 [2075.138..2090.935] | 2232.612 ± 0.453 [2232.091..2232.910] | 2232.928 ± 0.057 [2232.876..2232.990] |
| 16K | 314.054 ± 1.447 [312.454..315.272] | 2232.569 ± 0.082 [2232.489..2232.653] | 2232.606 ± 0.192 [2232.390..2232.760] |
| 32K | 195.617 ± 0.008 [195.608..195.624] | 267.806 ± 0.073 [267.732..267.879] | 2232.278 ± 0.152 [2232.103..2232.377] |

#### seq3x3_20261008 · wbuffix · gc_onset_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 5.914 ± 0.033 [5.881..5.947] | 5.694 ± 0.001 [5.693..5.695] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.692 ± 0.000 [5.692..5.692] | 5.693 ± 0.000 [5.693..5.693] | 5.693 ± 0.000 [5.693..5.694] |
| 32K | 5.692 ± 0.000 [5.692..5.692] | 5.692 ± 0.000 [5.692..5.692] | 5.693 ± 0.001 [5.692..5.693] |

#### seq3x3_20261008 · wbuffix · gc_onset_last_part_s
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 5.914 ± 0.033 [5.881..5.947] | 5.694 ± 0.001 [5.693..5.695] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.692 ± 0.000 [5.692..5.692] | 5.693 ± 0.000 [5.693..5.693] | 5.693 ± 0.000 [5.693..5.694] |
| 32K | 5.692 ± 0.000 [5.692..5.692] | 5.692 ± 0.000 [5.692..5.692] | 5.693 ± 0.001 [5.692..5.693] |

#### seq3x3_20261008 · wbuffix · bw_pre_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2147.912 ± 12.138 [2135.609..2159.879] | 2232.775 ± 0.487 [2232.216..2233.105] | 2233.040 ± 0.041 [2232.994..2233.074] |
| 16K | 556.100 ± 0.013 [556.089..556.114] | 2233.048 ± 0.089 [2232.946..2233.099] | 2232.973 ± 0.072 [2232.892..2233.028] |
| 32K | 278.518 ± 0.006 [278.513..278.525] | 1109.910 ± 0.002 [1109.909..1109.912] | 2232.795 ± 0.325 [2232.420..2232.994] |

#### seq3x3_20261008 · wbuffix · bw_post_gc_MiBps
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 2084.106 ± 8.058 [2075.866..2091.969] | 2232.624 ± 0.497 [2232.051..2232.930] | 2232.931 ± 0.026 [2232.913..2232.961] |
| 16K | 312.536 ± 0.516 [311.954..312.937] | 2232.699 ± 0.046 [2232.654..2232.746] | 2232.645 ± 0.202 [2232.415..2232.792] |
| 32K | 202.578 ± 0.001 [202.577..202.578] | 294.315 ± 0.045 [294.289..294.368] | 2232.329 ± 0.161 [2232.145..2232.445] |

#### seq3x3_20261008 · wbuffix · gc_cnt
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 14154.667 ± 62.011 [14092..14216] | 15225.333 ± 4.619 [15220..15228] | 15228.000 ± 0.000 [15228..15228] |
| 16K | 12048.667 ± 19.732 [12026..12062] | 15226.667 ± 2.309 [15224..15228] | 15226.667 ± 2.309 [15224..15228] |
| 32K | 12860.000 ± 0.000 [12860..12860] | 7900.667 ± 1.155 [7900..7902] | 15222.667 ± 2.309 [15220..15224] |

#### seq3x3_20261008 · wbuffix · ftl_host_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 32097869 ± 128735.496 [31966409..32223695] | 34290329 ± 8086.845 [34281000..34295340] | 34295275 ± 520.451 [34294832..34295848] |
| 16K | 5144209 ± 7877.037 [5135114..5148870] | 8573017 ± 176.001 [8572868..8573211] | 8572817 ± 800.511 [8571900..8573378] |
| 32K | 3218395 ± 0.000 [3218395..3218395] | 1417234 ± 158.771 [1417142..1417417] | 4285815 ± 408.779 [4285345..4286085] |

#### seq3x3_20261008 · wbuffix · ftl_gc_pgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 1805373 ± 2525.636 [1802472..1807080] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 464640.000 ± 0.000 [464640..464640] | 995349.333 ± 147.802 [995264..995520] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · wbuffix · waf_gc
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 16K | 1.351 ± 0.000 [1.351..1.351] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 32K | 1.144 ± 0.000 [1.144..1.144] | 1.702 ± 0.000 [1.702..1.702] | 1.000 ± 0.000 [1.000..1.000] |

#### seq3x3_20261008 · wbuffix · waf_total
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 16K | 5.404 ± 0.000 [5.404..5.404] | 1.000 ± 0.000 [1.000..1.000] | 1.000 ± 0.000 [1.000..1.000] |
| 32K | 9.155 ± 0.000 [9.155..9.155] | 3.405 ± 0.000 [3.405..3.405] | 1.000 ± 0.000 [1.000..1.000] |

#### seq3x3_20261008 · wbuffix · written_GiB
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 122.444 ± 0.491 [121.942..122.924] | 130.807 ± 0.031 [130.772..130.826] | 130.826 ± 0.002 [130.824..130.828] |
| 16K | 19.624 ± 0.030 [19.589..19.641] | 130.814 ± 0.003 [130.812..130.817] | 130.811 ± 0.012 [130.797..130.819] |
| 32K | 12.277 ± 0.000 [12.277..12.277] | 21.625 ± 0.002 [21.624..21.628] | 130.793 ± 0.012 [130.778..130.801] |

#### seq3x3_20261008 · wbuffix · fill_ratio
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 10.919 ± 0.044 [10.874..10.962] | 11.665 ± 0.003 [11.661..11.666] | 11.666 ± 0.000 [11.666..11.666] |
| 16K | 1.750 ± 0.003 [1.747..1.751] | 11.665 ± 0.000 [11.665..11.665] | 11.665 ± 0.001 [11.664..11.666] |
| 32K | 1.095 ± 0.000 [1.095..1.095] | 1.928 ± 0.000 [1.928..1.929] | 11.663 ± 0.001 [11.662..11.664] |

#### seq3x3_20261008 · wbuffix · chmodel_msgs
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · wbuffix · kernel_warn
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · wbuffix · blk_wr_ios
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 32097869 ± 128735.496 [31966409..32223695] | 8572582 ± 2021.711 [8570250..8573835] | 4286909 ± 65.056 [4286854..4286981] |
| 16K | 5144209 ± 7877.037 [5135114..5148870] | 8573017 ± 176.001 [8572868..8573211] | 4286408 ± 400.255 [4285950..4286689] |
| 32K | 3218395 ± 0.000 [3218395..3218395] | 1417234 ± 158.771 [1417142..1417417] | 4285815 ± 408.779 [4285345..4286085] |

#### seq3x3_20261008 · wbuffix · blk_wr_merges
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### seq3x3_20261008 · wbuffix · blk_avg_req_KiB
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | 4.000 ± 0.000 [4.000..4.000] | 16.000 ± 0.000 [16.000..16.000] | 32.000 ± 0.000 [32.000..32.000] |
| 16K | 4.000 ± 0.000 [4.000..4.000] | 16.000 ± 0.000 [16.000..16.000] | 32.000 ± 0.000 [32.000..32.000] |
| 32K | 4.000 ± 0.000 [4.000..4.000] | 16.000 ± 0.000 [16.000..16.000] | 32.000 ± 0.000 [32.000..32.000] |

### 11.3.3 변형 비교 (merge − wbuffix) / wbuffix, 60 s 평균 대역폭
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | -0.14% (2089.7→2086.7) | +0.01% (2232.4→2232.7) | +0.00% (2232.7→2232.8) |
| 16K | +525.38% (334.9→2094.4) | +0.00% (2232.5→2232.6) | +0.00% (2232.5→2232.6) |
| 32K | +899.77% (209.5→2094.6) | +504.87% (369.0→2232.2) | +0.00% (2232.2→2232.3) |

### 11.3.3w 변형 비교 (merge − wbuffix) / wbuffix, WAF_total
| map\bs | 4K | 16K | 32K |
|---|---|---|---|
| 4K | +0.00% (1.000→1.000) | +0.00% (1.000→1.000) | +0.00% (1.000→1.000) |
| 16K | -81.49% (5.404→1.000) | +0.00% (1.000→1.000) | +0.00% (1.000→1.000) |
| 32K | -89.08% (9.155→1.000) | -70.63% (3.405→1.000) | +0.00% (1.000→1.000) |

### 11.3.4 회차별 전체 (analysis/summary_runs.csv 와 같은 값)
```csv
variant,map,bs,rep,bw_MiBps,iops,written_GiB,fill_ratio,clat_mean_us,clat_p50_us,clat_p99_us,clat_p999_us,lat_mean_us,slat_mean_us,runtime_s,bw_first10s_MiBps,bw_last20s_MiBps,dev_bytes,chmodel_msgs,kernel_warn,blk_wr_ios,blk_wr_merges,blk_avg_req_KiB,gc_onset_s,gc_onset_last_part_s,bw_pre_gc_MiBps,bw_post_gc_MiBps,gc_cnt,ftl_host_pgs,ftl_gc_pgs,waf_gc,waf_total,mg_open,mg_merge,mg_full,mg_evict,mg_direct,mg_still_open
merge,4k,4k,1,2090.029297,535047.565874,122.464710,10.920659,58.854290,58.624000,62.208000,72.192000,59.658184,0.803894,60.001000,2119.573145,2085.065625,12040984064,0,0,32103389,0,4.000000,5.918470,5.918494,2146.086648,2084.697021,14156,32103389,0,1.000000,1.000000,0,0,0,0,32103389,0
merge,4k,4k,2,2083.576172,533395.693405,122.086620,10.886943,59.038197,59.136000,62.720000,73.216000,59.843886,0.805689,60.001000,2112.254639,2078.226294,12040984064,0,0,32004275,0,4.000000,5.939604,5.939629,2137.439631,2078.427517,14108,32004275,0,1.000000,1.000000,0,0,0,0,32004275,0
merge,4k,4k,3,2086.390625,534116.131398,122.251518,10.901648,58.955779,59.136000,62.720000,73.216000,59.763178,0.807399,60.001000,2116.144775,2080.005713,12040984064,0,0,32047502,0,4.000000,5.927847,5.927871,2142.771307,2081.020842,14132,32047502,0,1.000000,1.000000,0,0,0,0,32047502,0
merge,4k,16k,1,2232.570312,142884.551924,130.816895,11.665456,222.523875,222.208000,228.352000,238.592000,223.745091,1.221216,60.001000,2233.112354,2232.942041,12040984064,0,0,8573216,0,16.000000,5.693214,5.693235,2233.022727,2232.771701,15228,34292864,0,1.000000,1.000000,0,0,0,0,34292864,0
merge,4k,16k,2,2232.737305,142895.235079,130.826675,11.666328,222.476975,222.208000,226.304000,236.544000,223.728422,1.251447,60.001000,2233.132666,2232.913940,12040984064,0,0,8573857,0,16.000000,5.692924,5.692944,2233.090909,2232.938521,15228,34295428,0,1.000000,1.000000,0,0,0,0,34295428,0
merge,4k,16k,3,2232.697266,142892.651789,130.824310,11.666117,222.499198,222.208000,228.352000,236.544000,223.734924,1.235726,60.001000,2233.087500,2232.876270,12040984064,0,0,8573702,0,16.000000,5.693047,5.693069,2233.025568,2232.910364,15228,34294808,0,1.000000,1.000000,0,0,0,0,34294808,0
merge,4k,32k,1,2232.776367,71448.859186,130.828949,11.666531,446.001993,444.416000,452.608000,460.800000,447.660015,1.658023,60.001000,2233.143750,2232.920166,12040984064,0,0,4287003,0,32.000000,5.693241,5.693263,2233.079545,2232.974350,15228,34296024,0,1.000000,1.000000,0,0,0,0,34296024,0
merge,4k,32k,2,2232.751953,71448.075865,130.827515,11.666403,445.988811,444.416000,452.608000,464.896000,447.664809,1.675998,60.001000,2233.137500,2232.921606,12040984064,0,0,4286956,0,32.000000,5.693028,5.693049,2233.085227,2232.946137,15228,34295648,0,1.000000,1.000000,0,0,0,0,34295648,0
merge,4k,32k,3,2232.742188,71447.775870,130.826965,11.666354,445.956367,444.416000,448.512000,464.896000,447.668643,1.712276,60.001000,2233.093750,2232.901416,12040984064,0,0,4286938,0,32.000000,5.692938,5.692957,2233.034091,2232.940519,15228,34295504,0,1.000000,1.000000,0,0,0,0,34295504,0
merge,16k,4k,1,2089.913086,535017.966367,122.457935,10.920055,58.851536,58.624000,62.208000,73.216000,59.662284,0.810747,60.001000,2117.470703,2084.062012,12040984064,0,0,32101613,0,4.000000,5.920480,5.920500,2145.577415,2084.586815,14156,8025505,0,1.000000,1.000013,8025506,24076107,8025318,187,0,1
merge,16k,4k,2,2092.922852,535788.270195,122.634247,10.935777,58.772079,58.624000,62.208000,74.240000,59.576234,0.804156,60.001000,2123.164551,2087.707959,12040984064,0,0,32147832,0,4.000000,5.897663,5.897723,2152.787642,2087.161169,14180,8037043,0,1.000000,1.000011,8037044,24110788,8036888,155,0,1
merge,16k,4k,3,2100.262695,537667.422210,123.064358,10.974132,58.562213,58.624000,62.208000,71.168000,59.367424,0.805211,60.001000,2130.287158,2094.343115,12040984064,0,0,32260583,0,4.000000,5.885423,5.885485,2158.462358,2094.710296,14236,8065239,0,1.000000,1.000012,8065240,24195343,8065073,166,0,1
merge,16k,16k,1,2232.593750,142886.018566,130.818237,11.665576,222.509104,222.208000,226.304000,234.496000,223.739667,1.230563,60.001000,2233.139062,2232.737427,12040984064,0,0,8573304,0,16.000000,5.693129,5.693195,2233.105114,2232.773537,15228,8573304,0,1.000000,1.000000,0,0,0,0,8573304,0
merge,16k,16k,2,2232.499023,142879.985334,130.812714,11.665083,222.515898,222.208000,228.352000,234.496000,223.749747,1.233849,60.001000,2233.051416,2232.638916,12040984064,0,0,8572942,0,16.000000,5.692962,5.693031,2233.002841,2232.684212,15227,8572942,0,1.000000,1.000000,0,0,0,0,8572942,0
merge,16k,16k,3,2232.580078,142885.185247,130.817474,11.665508,222.486363,222.208000,226.304000,234.496000,223.741488,1.255125,60.001000,2233.090479,2232.713916,12040984064,0,0,8573254,0,16.000000,5.693025,5.693066,2233.017045,2232.784840,15228,8573254,0,1.000000,1.000000,0,0,0,0,8573254,0
merge,16k,32k,1,2232.618164,71443.792603,130.819672,11.665704,446.042339,444.416000,452.608000,473.088000,447.690346,1.648006,60.001000,2233.090625,2232.756958,12040984064,0,0,4286699,0,32.000000,5.693163,5.693229,2233.011364,2232.792074,15228,8573398,0,1.000000,1.000000,0,0,0,0,8573398,0
merge,16k,32k,2,2232.498047,71439.942668,130.812622,11.665075,446.044118,444.416000,452.608000,473.088000,447.718576,1.674458,60.001000,2233.037500,2232.638916,12040984064,0,0,4286468,0,32.000000,5.692999,5.693037,2232.977273,2232.676758,15226,8572936,0,1.000000,1.000000,0,0,0,0,8572936,0
merge,16k,32k,3,2232.589844,71442.892618,130.818024,11.665557,445.979642,444.416000,452.608000,473.088000,447.697503,1.717862,60.001000,2233.090625,2232.735083,12040984064,0,0,4286645,0,32.000000,5.693082,5.693147,2233.045455,2232.759151,15228,8573290,0,1.000000,1.000000,0,0,0,0,8573290,0
merge,32k,4k,1,2095.333984,536405.693238,122.775566,10.948379,58.700038,58.624000,62.208000,73.216000,59.507084,0.807046,60.001000,2124.830469,2089.427368,12040984064,0,0,32184878,0,4.000000,5.903838,5.903957,2151.418324,2089.965920,14196,4023129,0,1.000000,1.000005,4023130,28161748,4023091,38,0,1
merge,32k,4k,2,2094.772461,536261.895635,122.742653,10.945444,58.720629,58.624000,62.208000,72.192000,59.523468,0.802839,60.001000,2123.663672,2089.282202,12040984064,0,0,32176250,0,4.000000,5.902838,5.902952,2151.918324,2089.285283,14192,4022045,0,1.000000,1.000003,4022045,28154205,4022015,30,0,0
merge,32k,4k,3,2093.737305,535996.816720,122.681980,10.940034,58.744900,58.624000,62.208000,74.240000,59.552802,0.807902,60.001000,2122.938184,2088.224585,12040984064,0,0,32160345,0,4.000000,5.909056,5.909174,2149.599432,2088.415238,14184,4020064,0,1.000000,1.000005,4020065,28140280,4020020,44,0,1
merge,32k,16k,1,2232.287109,142866.385560,130.800262,11.663973,222.549925,222.208000,226.304000,240.640000,223.782133,1.232208,60.001000,2233.098437,2232.367114,12040984064,0,0,8572126,0,16.000000,5.692849,5.692987,2233.053977,2232.431613,15224,4286068,0,1.000000,1.000001,4286069,4286057,4286057,11,0,1
merge,32k,16k,2,2232.208984,142861.435643,130.795731,11.663569,222.558954,222.208000,226.304000,240.640000,223.783530,1.224576,60.001000,2232.965479,2232.269385,12040984064,0,0,8571829,0,16.000000,5.693348,5.693487,2232.843750,2232.381173,15224,4285920,0,1.000000,1.000001,4285920,4285909,4285909,11,0,0
merge,32k,16k,3,2232.252930,142864.202263,130.798264,11.663795,222.543107,222.208000,226.304000,240.640000,223.783002,1.239895,60.001000,2233.077979,2232.298364,12040984064,0,0,8571995,0,16.000000,5.693112,5.693193,2233.002841,2232.402091,15224,4286003,0,1.000000,1.000001,4286003,4285992,4285992,11,0,0
merge,32k,32k,1,2232.269531,71432.642789,130.799255,11.663883,446.060866,444.416000,452.608000,485.376000,447.762748,1.701883,60.001000,2232.718750,2232.356958,12040984064,0,0,4286030,0,32.000000,5.693203,5.693275,2233.005682,2232.407670,15224,4286030,0,1.000000,1.000000,0,0,0,0,4286030,0
merge,32k,32k,2,2232.233398,71431.476142,130.797119,11.663693,446.088010,444.416000,452.608000,485.376000,447.769385,1.681375,60.001000,2233.160791,2232.260791,12040984064,0,0,4285960,0,32.000000,5.694453,5.694596,2233.195756,2232.361695,15224,4285960,0,1.000000,1.000000,0,0,0,0,4285960,0
merge,32k,32k,3,2232.272461,71432.742788,130.799438,11.663899,446.083753,444.416000,448.512000,485.376000,447.760530,1.676777,60.001000,2233.059375,2232.339771,12040984064,0,0,4286036,0,32.000000,5.693064,5.693189,2232.977273,2232.409035,15224,4286036,0,1.000000,1.000000,0,0,0,0,4286036,0
wbuffix,4k,4k,1,2097.861328,537052.632456,122.923641,10.961584,58.633049,58.624000,62.720000,75.264000,59.435899,0.802850,60.001000,2131.671826,2090.934985,12040984064,0,0,32223695,0,4.000000,5.881322,5.881387,2159.878551,2091.969211,14216,32223695,0,1.000000,1.000000,,,,,,
wbuffix,4k,4k,2,2090.036133,535049.465842,122.465145,10.920698,58.851640,58.624000,62.208000,73.216000,59.658633,0.806994,60.001000,2121.454150,2083.425000,12040984064,0,0,32103503,0,4.000000,5.912592,5.912657,2148.247869,2084.483407,14156,32103503,0,1.000000,1.000000,,,,,,
wbuffix,4k,4k,3,2081.111328,532764.603923,121.942173,10.874062,59.106167,59.136000,62.720000,73.216000,59.914926,0.808759,60.001000,2110.274805,2075.137817,12040984064,0,0,31966409,0,4.000000,5.946759,5.946783,2135.609375,2075.865985,14092,31966409,0,1.000000,1.000000,,,,,,
wbuffix,4k,16k,1,2231.797852,142835.119415,130.771637,11.661420,222.608849,222.208000,228.352000,238.592000,223.825030,1.216182,60.001000,2232.659229,2232.090503,12040984064,0,0,8570250,0,16.000000,5.694948,5.694968,2232.215909,2232.051351,15220,34281000,0,1.000000,1.000000,,,,,,
wbuffix,4k,16k,2,2232.731445,142894.868419,130.826340,11.666298,222.507383,222.208000,226.304000,238.592000,223.727190,1.219807,60.001000,2233.156152,2232.910010,12040984064,0,0,8573835,0,16.000000,5.692810,5.692831,2233.105114,2232.930494,15228,34295340,0,1.000000,1.000000,,,,,,
wbuffix,4k,16k,3,2232.686523,142891.985134,130.823700,11.666063,222.492299,222.208000,226.304000,238.592000,223.735790,1.243490,60.001000,2233.074854,2232.834229,12040984064,0,0,8573662,0,16.000000,5.692954,5.692975,2233.002841,2232.891494,15228,34294648,0,1.000000,1.000000,,,,,,
wbuffix,4k,32k,1,2232.699219,71446.375894,130.824402,11.666126,446.028210,444.416000,452.608000,464.896000,447.677557,1.649347,60.001000,2233.160791,2232.989648,12040984064,0,0,4286854,0,32.000000,5.693224,5.693245,2233.051136,2232.912724,15228,34294832,0,1.000000,1.000000,,,,,,
wbuffix,4k,32k,2,2232.764648,71448.492525,130.828278,11.666471,445.985502,444.416000,452.608000,464.896000,447.663051,1.677549,60.001000,2233.121875,2232.918604,12040984064,0,0,4286981,0,32.000000,5.692875,5.692895,2233.073864,2232.961161,15228,34295848,0,1.000000,1.000000,,,,,,
wbuffix,4k,32k,3,2232.718750,71447.025883,130.825592,11.666232,445.991667,444.416000,452.608000,464.896000,447.671741,1.680074,60.001000,2233.075000,2232.876416,12040984064,0,0,4286893,0,32.000000,5.693098,5.693118,2232.994318,2232.919304,15228,34295144,0,1.000000,1.000000,,,,,,
wbuffix,16k,4k,1,334.305664,85582.380587,19.588905,1.746820,372.880186,222.208000,3653.632000,14352.384000,373.727928,0.847742,60.002000,454.194141,314.437646,12040984064,0,0,5135114,0,4.000000,5.692135,5.692183,556.114347,311.953582,12026,5135114,1802472,1.351009,5.404037,,,,,,
wbuffix,16k,4k,2,335.184570,85807.349388,19.641380,1.751499,371.894692,222.208000,3653.632000,14352.384000,372.749212,0.854521,60.005000,454.163672,315.271509,12040984064,0,0,5148870,0,4.000000,5.692083,5.692132,556.097301,312.937258,12062,5148870,1807080,1.350966,5.403865,,,,,,
wbuffix,16k,4k,3,335.192383,85809.269846,19.640511,1.751421,371.886026,222.208000,3620.864000,14352.384000,372.738876,0.852850,60.001000,454.158984,312.454321,12040984064,0,0,5148642,0,4.000000,5.692210,5.692261,556.089489,312.717819,12058,5148642,1806568,1.350882,5.403530,,,,,,
wbuffix,16k,16k,1,2232.480469,142878.752021,130.811584,11.664983,222.508955,222.208000,226.304000,234.496000,223.752501,1.243546,60.001000,2233.150000,2232.488940,12040984064,0,0,8572868,0,16.000000,5.692873,5.692902,2233.099432,2232.653553,15224,8572868,0,1.000000,1.000000,,,,,,
wbuffix,16k,16k,2,2232.569336,142884.468592,130.816818,11.665449,222.489009,222.208000,226.304000,234.496000,223.741411,1.252403,60.001000,2233.148291,2232.653052,12040984064,0,0,8573211,0,16.000000,5.692917,5.692978,2233.099432,2232.745841,15228,8573211,0,1.000000,1.000000,,,,,,
wbuffix,16k,16k,3,2232.506836,142880.468659,130.813156,11.665123,222.515689,222.208000,226.304000,234.496000,223.749409,1.233719,60.001000,2233.027979,2232.566260,12040984064,0,0,8572971,0,16.000000,5.693423,5.693470,2232.946023,2232.698538,15228,8572971,0,1.000000,1.000000,,,,,,
wbuffix,16k,32k,1,2232.227539,71431.309478,130.796814,11.663665,446.094508,444.416000,448.512000,477.184000,447.769666,1.675158,60.001000,2233.060791,2232.390479,12040984064,0,0,4285950,0,32.000000,5.693582,5.693644,2232.892045,2232.415084,15224,8571900,0,1.000000,1.000000,,,,,,
wbuffix,16k,32k,2,2232.613281,71443.625940,130.819366,11.665677,446.020377,444.416000,448.512000,473.088000,447.695272,1.674895,60.001000,2233.090625,2232.760083,12040984064,0,0,4286689,0,32.000000,5.692906,5.692979,2233.000000,2232.792137,15228,8573378,0,1.000000,1.000000,,,,,,
wbuffix,16k,32k,3,2232.559570,71441.909302,130.816223,11.665396,446.020420,444.416000,452.608000,473.088000,447.705764,1.685344,60.001000,2233.090625,2232.667896,12040984064,0,0,4286586,0,32.000000,5.692740,5.692806,2233.028409,2232.727828,15228,8573172,0,1.000000,1.000000,,,,,,
wbuffix,32k,4k,1,209.505859,53633.659406,12.277203,1.094806,595.515494,452.608000,2277.376000,2342.912000,596.437283,0.921789,60.007000,246.177734,195.607837,12040984064,0,0,3218395,0,4.000000,5.691702,5.691985,278.524858,202.577247,12860,3218395,464640,1.144370,9.154961,,,,,,
wbuffix,32k,4k,2,209.512695,53635.447046,12.277203,1.094806,595.485446,452.608000,2244.608000,2342.912000,596.414391,0.928945,60.005000,246.173828,195.618115,12040984064,0,0,3218395,0,4.000000,5.691883,5.692166,278.516335,202.578017,12860,3218395,464640,1.144370,9.154961,,,,,,
wbuffix,32k,4k,3,209.509766,53634.553211,12.277203,1.094806,595.503544,452.608000,2244.608000,2342.912000,596.436119,0.932575,60.006000,246.172266,195.624146,12040984064,0,0,3218395,0,4.000000,5.691938,5.692221,278.512784,202.578215,12860,3218395,464640,1.144370,9.154961,,,,,,
wbuffix,32k,16k,1,369.034180,23618.246058,21.623871,1.928285,1353.416328,468.992000,8355.840000,8978.432000,1354.660903,1.244574,60.002000,786.500000,267.732446,12040984064,0,0,1417142,0,16.000000,5.692097,5.692158,1109.911932,294.288964,7900,1417142,995264,1.702304,3.404607,,,,,,
wbuffix,32k,16k,2,369.034180,23618.246058,21.623871,1.928285,1353.409050,468.992000,8355.840000,8978.432000,1354.666502,1.257452,60.002000,786.498438,267.806592,12040984064,0,0,1417142,0,16.000000,5.692419,5.692480,1109.909091,294.289304,7900,1417142,995264,1.702304,3.404607,,,,,,
wbuffix,32k,16k,3,369.063477,23620.073656,21.628067,1.928660,1353.279528,473.088000,8355.840000,8978.432000,1354.549341,1.269813,60.009000,786.781250,267.879175,12040984064,0,0,1417417,0,16.000000,5.692428,5.692489,1109.909091,294.367618,7902,1417417,995520,1.702348,3.404696,,,,,,
wbuffix,32k,32k,1,2231.913086,71421.226313,130.778351,11.662019,446.153084,444.416000,452.608000,493.568000,447.836272,1.683189,60.001000,2232.781250,2232.102979,12040984064,0,0,4285345,0,32.000000,5.692036,5.692168,2232.420455,2232.145472,15220,4285345,0,1.000000,1.000000,,,,,,
wbuffix,32k,32k,2,2232.297852,71433.559441,130.800934,11.664033,446.046103,444.416000,448.512000,485.376000,447.755028,1.708925,60.001000,2233.081250,2232.377271,12040984064,0,0,4286085,0,32.000000,5.693020,5.693165,2232.994318,2232.444942,15224,4286085,0,1.000000,1.000000,,,,,,
wbuffix,32k,32k,3,2232.262695,71432.409460,130.798828,11.663845,446.086189,444.416000,448.512000,485.376000,447.763263,1.677073,60.001000,2233.034375,2232.352295,12040984064,0,0,4286016,0,32.000000,5.693183,5.693315,2232.971591,2232.396738,15224,4286016,0,1.000000,1.000000,,,,,,
```

### 11.3.5 조합별 집계 전체 (analysis/summary_agg.csv 와 같은 값)
```csv
variant,map,bs,n,bw_MiBps_mean,bw_MiBps_std,bw_MiBps_min,bw_MiBps_max,iops_mean,iops_std,iops_min,iops_max,written_GiB_mean,written_GiB_std,written_GiB_min,written_GiB_max,fill_ratio_mean,fill_ratio_std,fill_ratio_min,fill_ratio_max,clat_mean_us_mean,clat_mean_us_std,clat_mean_us_min,clat_mean_us_max,clat_p50_us_mean,clat_p50_us_std,clat_p50_us_min,clat_p50_us_max,clat_p99_us_mean,clat_p99_us_std,clat_p99_us_min,clat_p99_us_max,clat_p999_us_mean,clat_p999_us_std,clat_p999_us_min,clat_p999_us_max,lat_mean_us_mean,lat_mean_us_std,lat_mean_us_min,lat_mean_us_max,slat_mean_us_mean,slat_mean_us_std,slat_mean_us_min,slat_mean_us_max,runtime_s_mean,runtime_s_std,runtime_s_min,runtime_s_max,bw_first10s_MiBps_mean,bw_first10s_MiBps_std,bw_first10s_MiBps_min,bw_first10s_MiBps_max,bw_last20s_MiBps_mean,bw_last20s_MiBps_std,bw_last20s_MiBps_min,bw_last20s_MiBps_max,chmodel_msgs_mean,chmodel_msgs_std,chmodel_msgs_min,chmodel_msgs_max,kernel_warn_mean,kernel_warn_std,kernel_warn_min,kernel_warn_max,blk_wr_ios_mean,blk_wr_ios_std,blk_wr_ios_min,blk_wr_ios_max,blk_wr_merges_mean,blk_wr_merges_std,blk_wr_merges_min,blk_wr_merges_max,blk_avg_req_KiB_mean,blk_avg_req_KiB_std,blk_avg_req_KiB_min,blk_avg_req_KiB_max,gc_onset_s_mean,gc_onset_s_std,gc_onset_s_min,gc_onset_s_max,gc_onset_last_part_s_mean,gc_onset_last_part_s_std,gc_onset_last_part_s_min,gc_onset_last_part_s_max,bw_pre_gc_MiBps_mean,bw_pre_gc_MiBps_std,bw_pre_gc_MiBps_min,bw_pre_gc_MiBps_max,bw_post_gc_MiBps_mean,bw_post_gc_MiBps_std,bw_post_gc_MiBps_min,bw_post_gc_MiBps_max,gc_cnt_mean,gc_cnt_std,gc_cnt_min,gc_cnt_max,ftl_host_pgs_mean,ftl_host_pgs_std,ftl_host_pgs_min,ftl_host_pgs_max,ftl_gc_pgs_mean,ftl_gc_pgs_std,ftl_gc_pgs_min,ftl_gc_pgs_max,waf_gc_mean,waf_gc_std,waf_gc_min,waf_gc_max,waf_total_mean,waf_total_std,waf_total_min,waf_total_max,mg_open_mean,mg_open_std,mg_open_min,mg_open_max,mg_merge_mean,mg_merge_std,mg_merge_min,mg_merge_max,mg_full_mean,mg_full_std,mg_full_min,mg_full_max,mg_evict_mean,mg_evict_std,mg_evict_min,mg_evict_max,mg_direct_mean,mg_direct_std,mg_direct_min,mg_direct_max,mg_still_open_mean,mg_still_open_std,mg_still_open_min,mg_still_open_max
merge,4k,4k,3,2086.665365,3.235323,2083.576172,2090.029297,534186.463559,828.179101,533395.693405,535047.565874,122.267616,0.189558,122.086620,122.464710,10.903083,0.016904,10.886943,10.920659,58.949422,0.092118,58.854290,59.038197,58.965333,0.295603,58.624000,59.136000,62.549333,0.295603,62.208000,62.720000,72.874667,0.591207,72.192000,73.216000,59.755083,0.093116,59.658184,59.843886,0.805661,0.001753,0.803894,0.807399,60.001000,0.000000,60.001000,60.001000,2115.990853,3.661680,2112.254639,2119.573145,2081.099211,3.548368,2078.226294,2085.065625,0.000000,0.000000,0,0,0.000000,0.000000,0,0,32051722,49691.574225,32004275,32103389,0.000000,0.000000,0,0,4.000000,0.000000,4.000000,4.000000,5.928640,0.010589,5.918470,5.939604,5.928665,0.010590,5.918494,5.939629,2142.099195,4.362514,2137.439631,2146.086648,2081.381794,3.150299,2078.427517,2084.697021,14132.000000,24.000000,14108,14156,32051722,49691.574225,32004275,32103389,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,32051722,49691.574225,32004275,32103389,0.000000,0.000000,0,0
merge,4k,16k,3,2232.668294,0.087184,2232.570312,2232.737305,142890.812931,5.573912,142884.551924,142895.235079,130.822627,0.005103,130.816895,130.826675,11.665967,0.000455,11.665456,11.666328,222.500016,0.023460,222.476975,222.523875,222.208000,0.000000,222.208000,222.208000,227.669333,1.182413,226.304000,228.352000,237.226667,1.182413,236.544000,238.592000,223.736146,0.008401,223.728422,223.745091,1.236130,0.015120,1.221216,1.251447,60.001000,0.000000,60.001000,60.001000,2233.110840,0.022621,2233.087500,2233.132666,2232.910750,0.033002,2232.876270,2232.942041,0.000000,0.000000,0,0,0.000000,0.000000,0,0,8573592,334.440329,8573216,8573857,0.000000,0.000000,0,0,16.000000,0.000000,16.000000,16.000000,5.693062,0.000146,5.692924,5.693214,5.693083,0.000146,5.692944,5.693235,2233.046402,0.038571,2233.022727,2233.090909,2232.873529,0.089302,2232.771701,2232.938521,15228.000000,0.000000,15228,15228,34294367,1337.761314,34292864,34295428,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,34294367,1337.761314,34292864,34295428,0.000000,0.000000,0,0
merge,4k,32k,3,2232.756836,0.017605,2232.742188,2232.776367,71448.236974,0.559339,71447.775870,71448.859186,130.827810,0.001024,130.826965,130.828949,11.666429,0.000091,11.666354,11.666531,445.982390,0.023481,445.956367,446.001993,444.416000,0.000000,444.416000,444.416000,451.242667,2.364827,448.512000,452.608000,463.530667,2.364827,460.800000,464.896000,447.664489,0.004323,447.660015,447.668643,1.682099,0.027636,1.658023,1.712276,60.001000,0.000000,60.001000,60.001000,2233.125000,0.027243,2233.093750,2233.143750,2232.914396,0.011264,2232.901416,2232.921606,0.000000,0.000000,0,0,0.000000,0.000000,0,0,4286966,33.560890,4286938,4287003,0.000000,0.000000,0,0,32.000000,0.000000,32.000000,32.000000,5.693069,0.000156,5.692938,5.693241,5.693090,0.000157,5.692957,5.693263,2233.066288,0.028028,2233.034091,2233.085227,2232.953669,0.018129,2232.940519,2232.974350,15228.000000,0.000000,15228,15228,34295725,268.487119,34295504,34296024,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,34295725,268.487119,34295504,34296024,0.000000,0.000000,0,0
merge,16k,4k,3,2094.366211,5.323633,2089.913086,2100.262695,536157.886257,1362.852190,535017.966367,537667.422210,122.718847,0.311937,122.457935,123.064358,10.943321,0.027817,10.920055,10.974132,58.728609,0.149479,58.562213,58.851536,58.624000,0.000000,58.624000,58.624000,62.208000,0.000000,62.208000,62.208000,72.874667,1.564186,71.168000,74.240000,59.535314,0.151629,59.367424,59.662284,0.806705,0.003541,0.804156,0.810747,60.001000,0.000000,60.001000,60.001000,2123.640804,6.421487,2117.470703,2130.287158,2088.704362,5.212474,2084.062012,2094.343115,0.000000,0.000000,0,0,0.000000,0.000000,0,0,32170009,81772.494216,32101613,32260583,0.000000,0.000000,0,0,4.000000,0.000000,4.000000,4.000000,5.901189,0.017792,5.885423,5.920480,5.901236,0.017770,5.885485,5.920500,2152.275805,6.457703,2145.577415,2158.462358,2088.819426,5.261519,2084.586815,2094.710296,14190.666667,41.052812,14156,14236,8042596,20440.689062,8025505,8065239,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000012,0.000001,1.000011,1.000013,8042597,20440.689062,8025506,8065240,24127413,61331.807248,24076107,24195343,8042426,20447.979322,8025318,8065073,169.333333,16.258331,155,187,0.000000,0.000000,0,0,1.000000,0.000000,1,1
merge,16k,16k,3,2232.557617,0.051202,2232.499023,2232.593750,142883.729716,3.269388,142879.985334,142886.018566,130.816142,0.002993,130.812714,130.818237,11.665389,0.000267,11.665083,11.665576,222.503788,0.015468,222.486363,222.515898,222.208000,0.000000,222.208000,222.208000,226.986667,1.182413,226.304000,228.352000,234.496000,0.000000,234.496000,234.496000,223.743634,0.005372,223.739667,223.749747,1.239846,0.013334,1.230563,1.255125,60.001000,0.000000,60.001000,60.001000,2233.093652,0.043909,2233.051416,2233.139062,2232.696753,0.051449,2232.638916,2232.737427,0.000000,0.000000,0,0,0.000000,0.000000,0,0,8573167,196.166596,8572942,8573304,0.000000,0.000000,0,0,16.000000,0.000000,16.000000,16.000000,5.693039,0.000084,5.692962,5.693129,5.693097,0.000086,5.693031,5.693195,2233.041667,0.055404,2233.002841,2233.105114,2232.747530,0.055125,2232.684212,2232.784840,15227.666667,0.577350,15227,15228,8573167,196.166596,8572942,8573304,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,8573167,196.166596,8572942,8573304,0.000000,0.000000,0,0
merge,16k,32k,3,2232.568685,0.062792,2232.498047,2232.618164,71442.209296,2.013876,71439.942668,71443.792603,130.816772,0.003688,130.812622,130.819672,11.665445,0.000329,11.665075,11.665704,446.022033,0.036723,445.979642,446.044118,444.416000,0.000000,444.416000,444.416000,452.608000,0.000000,452.608000,452.608000,473.088000,0.000000,473.088000,473.088000,447.702142,0.014676,447.690346,447.718576,1.680109,0.035269,1.648006,1.717862,60.001000,0.000000,60.001000,60.001000,2233.072917,0.030672,2233.037500,2233.090625,2232.710319,0.062797,2232.638916,2232.756958,0.000000,0.000000,0,0,0.000000,0.000000,0,0,4286604,120.834598,4286468,4286699,0.000000,0.000000,0,0,32.000000,0.000000,32.000000,32.000000,5.693081,0.000082,5.692999,5.693163,5.693138,0.000096,5.693037,5.693229,2233.011364,0.034091,2232.977273,2233.045455,2232.742661,0.059400,2232.676758,2232.792074,15227.333333,1.154701,15226,15228,8573208,241.669195,8572936,8573398,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,8573208,241.669195,8572936,8573398,0.000000,0.000000,0,0
merge,32k,4k,3,2094.614583,0.809963,2093.737305,2095.333984,536221.468531,207.414476,535996.816720,536405.693238,122.733400,0.047474,122.681980,122.775566,10.944619,0.004233,10.940034,10.948379,58.721856,0.022456,58.700038,58.744900,58.624000,0.000000,58.624000,58.624000,62.208000,0.000000,62.208000,62.208000,73.216000,1.024000,72.192000,74.240000,59.527784,0.023163,59.507084,59.552802,0.805929,0.002710,0.802839,0.807902,60.001000,0.000000,60.001000,60.001000,2123.810775,0.954681,2122.938184,2124.830469,2088.978052,0.656546,2088.224585,2089.427368,0.000000,0.000000,0,0,0.000000,0.000000,0,0,32173824,12445.075987,32160345,32184878,0.000000,0.000000,0,0,4.000000,0.000000,4.000000,4.000000,5.905244,0.003339,5.902838,5.909056,5.905361,0.003340,5.902952,5.909174,2150.978693,1.220357,2149.599432,2151.918324,2089.222147,0.777266,2088.415238,2089.965920,14190.666667,6.110101,14184,14196,4021746,1554.222314,4020064,4023129,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000004,0.000001,1.000003,1.000005,4021747,1554.126228,4020065,4023130,28152078,10890.955713,28140280,28161748,4021709,1558.249124,4020020,4023091,37.333333,7.023769,30,44,0.000000,0.000000,0,0,0.666667,0.577350,0,1
merge,32k,16k,3,2232.249674,0.039164,2232.208984,2232.287109,142864.007822,2.480680,142861.435643,142866.385560,130.798086,0.002271,130.795731,130.800262,11.663779,0.000203,11.663569,11.663973,222.550662,0.007949,222.543107,222.558954,222.208000,0.000000,222.208000,222.208000,226.304000,0.000000,226.304000,226.304000,240.640000,0.000000,240.640000,240.640000,223.782888,0.000706,223.782133,223.783530,1.232226,0.007659,1.224576,1.239895,60.001000,0.000000,60.001000,60.001000,2233.047298,0.071592,2232.965479,2233.098437,2232.311621,0.050195,2232.269385,2232.367114,0.000000,0.000000,0,0,0.000000,0.000000,0,0,8571983,148.843318,8571829,8572126,0.000000,0.000000,0,0,16.000000,0.000000,16.000000,16.000000,5.693103,0.000250,5.692849,5.693348,5.693222,0.000251,5.692987,5.693487,2232.966856,0.109636,2232.843750,2233.053977,2232.404959,0.025342,2232.381173,2232.431613,15224.000000,0.000000,15224,15224,4285997,74.182208,4285920,4286068,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000001,0.000000,1.000001,1.000001,4285997,74.661458,4285920,4286069,4285986,74.182208,4285909,4286057,4285986,74.182208,4285909,4286057,11.000000,0.000000,11,11,0.000000,0.000000,0,0,0.333333,0.577350,0,1
merge,32k,32k,3,2232.258464,0.021756,2232.233398,2232.272461,71432.287240,0.704208,71431.476142,71432.742788,130.798604,0.001289,130.797119,130.799438,11.663825,0.000115,11.663693,11.663899,446.077543,0.014599,446.060866,446.088010,444.416000,0.000000,444.416000,444.416000,451.242667,2.364827,448.512000,452.608000,485.376000,0.000000,485.376000,485.376000,447.764221,0.004608,447.760530,447.769385,1.686678,0.013367,1.676777,1.701883,60.001000,0.000000,60.001000,60.001000,2232.979639,0.231557,2232.718750,2233.160791,2232.319173,0.051286,2232.260791,2232.356958,0.000000,0.000000,0,0,0.000000,0.000000,0,0,4286009,42.253205,4285960,4286036,0.000000,0.000000,0,0,32.000000,0.000000,32.000000,32.000000,5.693573,0.000765,5.693064,5.694453,5.693687,0.000789,5.693189,5.694596,2233.059570,0.118793,2232.977273,2233.195756,2232.392800,0.026946,2232.361695,2232.409035,15224.000000,0.000000,15224,15224,4286009,42.253205,4285960,4286036,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,0.000000,0.000000,0,0,4286009,42.253205,4285960,4286036,0.000000,0.000000,0,0
wbuffix,4k,4k,3,2089.669596,8.381013,2081.111328,2097.861328,534955.567407,2145.555840,532764.603923,537052.632456,122.443653,0.491087,121.942173,122.923641,10.918781,0.043792,10.874062,10.961584,58.863619,0.236786,58.633049,59.106167,58.794667,0.295603,58.624000,59.136000,62.549333,0.295603,62.208000,62.720000,73.898667,1.182413,73.216000,75.264000,59.669820,0.239709,59.435899,59.914926,0.806201,0.003033,0.802850,0.808759,60.001000,0.000000,60.001000,60.001000,2121.133594,10.702112,2110.274805,2131.671826,2083.165934,7.901770,2075.137817,2090.934985,0.000000,0.000000,0,0,0.000000,0.000000,0,0,32097869,128735.495944,31966409,32223695,0.000000,0.000000,0,0,4.000000,0.000000,4.000000,4.000000,5.913558,0.032729,5.881322,5.946759,5.913609,0.032708,5.881387,5.946783,2147.911932,12.138075,2135.609375,2159.878551,2084.106201,8.058237,2075.865985,2091.969211,14154.666667,62.010752,14092,14216,32097869,128735.495944,31966409,32223695,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,4k,16k,3,2232.405273,0.526522,2231.797852,2232.731445,142873.990989,33.694626,142835.119415,142894.868419,130.807226,0.030849,130.771637,130.826340,11.664594,0.002751,11.661420,11.666298,222.536177,0.063386,222.492299,222.608849,222.208000,0.000000,222.208000,222.208000,226.986667,1.182413,226.304000,228.352000,238.592000,0.000000,238.592000,238.592000,223.762670,0.054177,223.727190,223.825030,1.226493,0.014831,1.216182,1.243490,60.001000,0.000000,60.001000,60.001000,2232.963411,0.266548,2232.659229,2233.156152,2232.611580,0.452854,2232.090503,2232.910010,0.000000,0.000000,0,0,0.000000,0.000000,0,0,8572582,2021.711239,8570250,8573835,0.000000,0.000000,0,0,16.000000,0.000000,16.000000,16.000000,5.693571,0.001195,5.692810,5.694948,5.693591,0.001194,5.692831,5.694968,2232.774621,0.486554,2232.215909,2233.105114,2232.624446,0.496698,2232.051351,2232.930494,15225.333333,4.618802,15220,15228,34290329,8086.844955,34281000,34295340,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,4k,32k,3,2232.727539,0.033589,2232.699219,2232.764648,71447.298101,1.084255,71446.375894,71448.492525,130.826090,0.001985,130.824402,130.828278,11.666276,0.000177,11.666126,11.666471,446.001793,0.023084,445.985502,446.028210,444.416000,0.000000,444.416000,444.416000,452.608000,0.000000,452.608000,452.608000,464.896000,0.000000,464.896000,464.896000,447.670783,0.007300,447.663051,447.677557,1.668990,0.017058,1.649347,1.680074,60.001000,0.000000,60.001000,60.001000,2233.119222,0.042957,2233.075000,2233.160791,2232.928223,0.057226,2232.876416,2232.989648,0.000000,0.000000,0,0,0.000000,0.000000,0,0,4286909,65.056386,4286854,4286981,0.000000,0.000000,0,0,32.000000,0.000000,32.000000,32.000000,5.693066,0.000177,5.692875,5.693224,5.693086,0.000177,5.692895,5.693245,2233.039773,0.040972,2232.994318,2233.073864,2232.931063,0.026273,2232.912724,2232.961161,15228.000000,0.000000,15228,15228,34295275,520.451086,34294832,34295848,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,16k,4k,3,334.894206,0.509707,334.305664,335.192383,85732.999940,130.443721,85582.380587,85809.269846,19.623599,0.030049,19.588905,19.641380,1.749913,0.002680,1.746820,1.751499,372.220301,0.571493,371.886026,372.880186,222.208000,0.000000,222.208000,222.208000,3642.709333,18.918614,3620.864000,3653.632000,14352.384000,0.000000,14352.384000,14352.384000,373.072005,0.568069,372.738876,373.727928,0.851704,0.003532,0.847742,0.854521,60.002667,0.002082,60.001000,60.005000,454.172266,0.019089,454.158984,454.194141,314.054492,1.447150,312.454321,315.271509,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5144209,7877.037345,5135114,5148870,0.000000,0.000000,0,0,4.000000,0.000000,4.000000,4.000000,5.692143,0.000064,5.692083,5.692210,5.692192,0.000065,5.692132,5.692261,556.100379,0.012712,556.089489,556.114347,312.536220,0.516370,311.953582,312.937258,12048.666667,19.731531,12026,12062,5144209,7877.037345,5135114,5148870,1805373,2525.636026,1802472,1807080,1.350953,0.000064,1.350882,1.351009,5.403811,0.000258,5.403530,5.404037,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,16k,16k,3,2232.518880,0.045641,2232.480469,2232.569336,142881.229757,2.933300,142878.752021,142884.468592,130.813853,0.002686,130.811584,130.816818,11.665185,0.000239,11.664983,11.665449,222.504551,0.013875,222.489009,222.515689,222.208000,0.000000,222.208000,222.208000,226.304000,0.000000,226.304000,226.304000,234.496000,0.000000,234.496000,234.496000,223.747774,0.005723,223.741411,223.752501,1.243223,0.009346,1.233719,1.252403,60.001000,0.000000,60.001000,60.001000,2233.108757,0.069961,2233.027979,2233.150000,2232.569417,0.082101,2232.488940,2232.653052,0.000000,0.000000,0,0,0.000000,0.000000,0,0,8573017,176.000947,8572868,8573211,0.000000,0.000000,0,0,16.000000,0.000000,16.000000,16.000000,5.693071,0.000306,5.692873,5.693423,5.693117,0.000308,5.692902,5.693470,2233.048295,0.088571,2232.946023,2233.099432,2232.699311,0.046149,2232.653553,2232.745841,15226.666667,2.309401,15224,15228,8573017,176.000947,8572868,8573211,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,16k,32k,3,2232.466797,0.208936,2232.227539,2232.613281,71438.948240,6.670811,71431.309478,71443.625940,130.810801,0.012215,130.796814,130.819366,11.664913,0.001089,11.663665,11.665677,446.045102,0.042787,446.020377,446.094508,444.416000,0.000000,444.416000,444.416000,449.877333,2.364827,448.512000,452.608000,474.453333,2.364827,473.088000,477.184000,447.723567,0.040266,447.695272,447.769666,1.678466,0.005958,1.674895,1.685344,60.001000,0.000000,60.001000,60.001000,2233.080680,0.017225,2233.060791,2233.090625,2232.606152,0.192383,2232.390479,2232.760083,0.000000,0.000000,0,0,0.000000,0.000000,0,0,4286408,400.255335,4285950,4286689,0.000000,0.000000,0,0,32.000000,0.000000,32.000000,32.000000,5.693076,0.000446,5.692740,5.693582,5.693143,0.000442,5.692806,5.693644,2232.973485,0.071945,2232.892045,2233.028409,2232.645017,0.201707,2232.415084,2232.792137,15226.666667,2.309401,15224,15228,8572817,800.510670,8571900,8573378,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,32k,4k,3,209.509440,0.003430,209.505859,209.512695,53634.553221,0.893820,53633.659406,53635.447046,12.277203,0.000000,12.277203,12.277203,1.094806,0.000000,1.094806,1.094806,595.501494,0.015129,595.485446,595.515494,452.608000,0.000000,452.608000,452.608000,2255.530667,18.918614,2244.608000,2277.376000,2342.912000,0.000000,2342.912000,2342.912000,596.429264,0.012894,596.414391,596.437283,0.927770,0.005488,0.921789,0.932575,60.006000,0.001000,60.005000,60.007000,246.174609,0.002817,246.172266,246.177734,195.616699,0.008246,195.607837,195.624146,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3218395,0.000000,3218395,3218395,0.000000,0.000000,0,0,4.000000,0.000000,4.000000,4.000000,5.691841,0.000123,5.691702,5.691938,5.692124,0.000123,5.691985,5.692221,278.517992,0.006205,278.512784,278.524858,202.577826,0.000511,202.577247,202.578215,12860.000000,0.000000,12860,12860,3218395,0.000000,3218395,3218395,464640.000000,0.000000,464640,464640,1.144370,0.000000,1.144370,1.144370,9.154961,0.000000,9.154961,9.154961,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,32k,16k,3,369.043945,0.016915,369.034180,369.063477,23618.855257,1.055164,23618.246058,23620.073656,21.625270,0.002423,21.623871,21.628067,1.928410,0.000216,1.928285,1.928660,1353.368302,0.076966,1353.279528,1353.416328,470.357333,2.364827,468.992000,473.088000,8355.840000,0.000000,8355.840000,8355.840000,8978.432000,0.000000,8978.432000,8978.432000,1354.625582,0.066086,1354.549341,1354.666502,1.257280,0.012620,1.244574,1.269813,60.004333,0.004041,60.002000,60.009000,786.593229,0.162833,786.498438,786.781250,267.806071,0.073366,267.732446,267.879175,0.000000,0.000000,0,0,0.000000,0.000000,0,0,1417234,158.771324,1417142,1417417,0.000000,0.000000,0,0,16.000000,0.000000,16.000000,16.000000,5.692315,0.000189,5.692097,5.692428,5.692376,0.000189,5.692158,5.692489,1109.910038,0.001640,1109.909091,1109.911932,294.315295,0.045313,294.288964,294.367618,7900.666667,1.154701,7900,7902,1417234,158.771324,1417142,1417417,995349.333333,147.801669,995264,995520,1.702318,0.000026,1.702304,1.702348,3.404637,0.000051,3.404607,3.404696,,,,,,,,,,,,,,,,,,,,,,,,
wbuffix,32k,32k,3,2232.157878,0.212723,2231.913086,2232.297852,71429.065071,6.812871,71421.226313,71433.559441,130.792704,0.012475,130.778351,130.800934,11.663299,0.001112,11.662019,11.664033,446.095125,0.054047,446.046103,446.153084,444.416000,0.000000,444.416000,444.416000,449.877333,2.364827,448.512000,452.608000,488.106667,4.729653,485.376000,493.568000,447.784854,0.044719,447.755028,447.836272,1.689729,0.016903,1.677073,1.708925,60.001000,0.000000,60.001000,60.001000,2232.965625,0.161384,2232.781250,2233.081250,2232.277515,0.151668,2232.102979,2232.377271,0.000000,0.000000,0,0,0.000000,0.000000,0,0,4285815,408.779076,4285345,4286085,0.000000,0.000000,0,0,32.000000,0.000000,32.000000,32.000000,5.692746,0.000621,5.692036,5.693183,5.692883,0.000623,5.692168,5.693315,2232.795455,0.324958,2232.420455,2232.994318,2232.329050,0.160800,2232.145472,2232.444942,15222.666667,2.309401,15220,15224,4285815,408.779076,4285345,4286085,0.000000,0.000000,0,0,1.000000,0.000000,1.000000,1.000000,1.000000,0.000000,1.000000,1.000000,,,,,,,,,,,,,,,,,,,,,,,,
```

### 11.3.6 파티션별 GC 로그 (회차마다: 첫 GC 줄의 fio 시작 기준 시각·내용, rmmod 통계)
```
[merge map4k bs4k r1]
  +5.918s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.918s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.918s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.918s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8025855 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=1 host_pgs=8025845 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=2 host_pgs=8025845 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=3 host_pgs=8025844 gc_pgs=0 gc_cnt=3539 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8025855 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8025845 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8025845 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8025844 still_open=0
  (kernel) [83543.212919] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83543.280102] NVMeVirt: Virtual NVMe device closed
[merge map4k bs4k r2]
  +5.940s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.940s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.940s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.940s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8001077 gc_pgs=0 gc_cnt=3527 free_lines=3
  stats part=1 host_pgs=8001066 gc_pgs=0 gc_cnt=3527 free_lines=3
  stats part=2 host_pgs=8001066 gc_pgs=0 gc_cnt=3527 free_lines=3
  stats part=3 host_pgs=8001066 gc_pgs=0 gc_cnt=3527 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8001077 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8001066 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8001066 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8001066 still_open=0
  (kernel) [84810.255113] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84810.322340] NVMeVirt: Virtual NVMe device closed
[merge map4k bs4k r3]
  +5.928s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.928s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.928s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.928s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8011883 gc_pgs=0 gc_cnt=3533 free_lines=3
  stats part=1 host_pgs=8011873 gc_pgs=0 gc_cnt=3533 free_lines=3
  stats part=2 host_pgs=8011873 gc_pgs=0 gc_cnt=3533 free_lines=3
  stats part=3 host_pgs=8011873 gc_pgs=0 gc_cnt=3533 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8011883 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8011873 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8011873 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8011873 still_open=0
  (kernel) [86077.257339] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86077.325543] NVMeVirt: Virtual NVMe device closed
[merge map4k bs16k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573216 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573216 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573216 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573216 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8573216 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8573216 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8573216 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8573216 still_open=0
  (kernel) [83613.627912] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83613.695954] NVMeVirt: Virtual NVMe device closed
[merge map4k bs16k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573857 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573857 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573857 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573857 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8573857 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8573857 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8573857 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8573857 still_open=0
  (kernel) [84880.696568] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84880.764247] NVMeVirt: Virtual NVMe device closed
[merge map4k bs16k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573702 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573702 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573702 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573702 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8573702 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8573702 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8573702 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8573702 still_open=0
  (kernel) [86147.689118] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86147.756655] NVMeVirt: Virtual NVMe device closed
[merge map4k bs32k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8574006 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8574006 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8574006 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8574006 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8574006 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8574006 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8574006 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8574006 still_open=0
  (kernel) [83684.062808] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83684.130190] NVMeVirt: Virtual NVMe device closed
[merge map4k bs32k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573912 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573912 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573912 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573912 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8573912 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8573912 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8573912 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8573912 still_open=0
  (kernel) [84951.130973] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84951.197783] NVMeVirt: Virtual NVMe device closed
[merge map4k bs32k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573876 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573876 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573876 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573876 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=8573876 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=8573876 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=8573876 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=8573876 still_open=0
  (kernel) [86218.120875] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86218.187765] NVMeVirt: Virtual NVMe device closed
[merge map16k bs4k r1]
  +5.920s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.920s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.920s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.921s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2006373 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=1 host_pgs=2006381 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=2 host_pgs=2006373 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=3 host_pgs=2006378 gc_pgs=0 gc_cnt=3539 free_lines=3
  merge part=0 open=2006373 merge=6019039 full=2006334 evict=39 direct=0 still_open=0
  merge part=1 open=2006381 merge=6019031 full=2006329 evict=52 direct=0 still_open=0
  merge part=2 open=2006374 merge=6019037 full=2006334 evict=39 direct=0 still_open=1
  merge part=3 open=2006378 merge=6019000 full=2006321 evict=57 direct=0 still_open=0
  (kernel) [83754.475659] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83754.503334] NVMeVirt: Virtual NVMe device closed
[merge map16k bs4k r2]
  +5.898s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.898s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.898s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.898s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2009261 gc_pgs=0 gc_cnt=3545 free_lines=3
  stats part=1 host_pgs=2009264 gc_pgs=0 gc_cnt=3545 free_lines=3
  stats part=2 host_pgs=2009260 gc_pgs=0 gc_cnt=3545 free_lines=3
  stats part=3 host_pgs=2009258 gc_pgs=0 gc_cnt=3545 free_lines=3
  merge part=0 open=2009261 merge=6027707 full=2009223 evict=38 direct=0 still_open=0
  merge part=1 open=2009265 merge=6027701 full=2009221 evict=43 direct=0 still_open=1
  merge part=2 open=2009260 merge=6027704 full=2009228 evict=32 direct=0 still_open=0
  merge part=3 open=2009258 merge=6027676 full=2009216 evict=42 direct=0 still_open=0
  (kernel) [85021.520280] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85021.547923] NVMeVirt: Virtual NVMe device closed
[merge map16k bs4k r3]
  +5.885s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.885s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.885s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.885s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2016311 gc_pgs=0 gc_cnt=3559 free_lines=3
  stats part=1 host_pgs=2016303 gc_pgs=0 gc_cnt=3559 free_lines=3
  stats part=2 host_pgs=2016307 gc_pgs=0 gc_cnt=3559 free_lines=3
  stats part=3 host_pgs=2016318 gc_pgs=0 gc_cnt=3559 free_lines=3
  merge part=0 open=2016311 merge=6048845 full=2016272 evict=39 direct=0 still_open=0
  merge part=1 open=2016304 merge=6048849 full=2016273 evict=30 direct=0 still_open=1
  merge part=2 open=2016307 merge=6048845 full=2016272 evict=35 direct=0 still_open=0
  merge part=3 open=2016318 merge=6048804 full=2016256 evict=62 direct=0 still_open=0
  (kernel) [86288.530677] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86288.558173] NVMeVirt: Virtual NVMe device closed
[merge map16k bs16k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143329 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143329 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143329 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143317 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=2143329 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=2143329 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=2143329 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=2143317 still_open=0
  (kernel) [83824.846454] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83824.873779] NVMeVirt: Virtual NVMe device closed
[merge map16k bs16k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143239 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143238 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143238 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143227 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=2143239 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=2143238 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=2143238 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=2143227 still_open=0
  (kernel) [85091.865851] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85091.893560] NVMeVirt: Virtual NVMe device closed
[merge map16k bs16k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143317 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143316 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143316 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143305 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=2143317 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=2143316 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=2143316 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=2143305 still_open=0
  (kernel) [86358.895526] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86358.923318] NVMeVirt: Virtual NVMe device closed
[merge map16k bs32k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143355 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143355 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143344 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143344 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=2143355 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=2143355 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=2143344 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=2143344 still_open=0
  (kernel) [83895.218167] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83895.245520] NVMeVirt: Virtual NVMe device closed
[merge map16k bs32k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143240 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143240 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143228 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=2143228 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=2143240 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=2143240 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=2143228 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=2143228 still_open=0
  (kernel) [85162.199768] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85162.227521] NVMeVirt: Virtual NVMe device closed
[merge map16k bs32k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143328 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143328 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143317 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143317 gc_pgs=0 gc_cnt=3807 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=2143328 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=2143328 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=2143317 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=2143317 still_open=0
  (kernel) [86429.263404] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86429.291150] NVMeVirt: Virtual NVMe device closed
[merge map32k bs4k r1]
  +5.904s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.904s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.904s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.904s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1005790 gc_pgs=0 gc_cnt=3549 free_lines=3
  stats part=1 host_pgs=1005783 gc_pgs=0 gc_cnt=3549 free_lines=3
  stats part=2 host_pgs=1005779 gc_pgs=0 gc_cnt=3549 free_lines=3
  stats part=3 host_pgs=1005777 gc_pgs=0 gc_cnt=3549 free_lines=3
  merge part=0 open=1005790 merge=7040482 full=1005780 evict=10 direct=0 still_open=0
  merge part=1 open=1005784 merge=7040454 full=1005773 evict=10 direct=0 still_open=1
  merge part=2 open=1005779 merge=7040405 full=1005769 evict=10 direct=0 still_open=0
  merge part=3 open=1005777 merge=7040407 full=1005769 evict=8 direct=0 still_open=0
  (kernel) [83965.568872] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83965.589302] NVMeVirt: Virtual NVMe device closed
[merge map32k bs4k r2]
  +5.903s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.903s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.903s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.903s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1005516 gc_pgs=0 gc_cnt=3548 free_lines=3
  stats part=1 host_pgs=1005516 gc_pgs=0 gc_cnt=3548 free_lines=3
  stats part=2 host_pgs=1005504 gc_pgs=0 gc_cnt=3548 free_lines=3
  stats part=3 host_pgs=1005509 gc_pgs=0 gc_cnt=3548 free_lines=3
  merge part=0 open=1005516 merge=7038596 full=1005512 evict=4 direct=0 still_open=0
  merge part=1 open=1005516 merge=7038566 full=1005502 evict=14 direct=0 still_open=0
  merge part=2 open=1005504 merge=7038528 full=1005504 evict=0 direct=0 still_open=0
  merge part=3 open=1005509 merge=7038515 full=1005497 evict=12 direct=0 still_open=0
  (kernel) [85232.574941] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85232.595714] NVMeVirt: Virtual NVMe device closed
[merge map32k bs4k r3]
  +5.909s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.909s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.909s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.909s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1005023 gc_pgs=0 gc_cnt=3546 free_lines=3
  stats part=1 host_pgs=1005021 gc_pgs=0 gc_cnt=3546 free_lines=3
  stats part=2 host_pgs=1005006 gc_pgs=0 gc_cnt=3546 free_lines=3
  stats part=3 host_pgs=1005014 gc_pgs=0 gc_cnt=3546 free_lines=3
  merge part=0 open=1005023 merge=7035113 full=1005011 evict=12 direct=0 still_open=0
  merge part=1 open=1005021 merge=7035085 full=1005003 evict=18 direct=0 still_open=0
  merge part=2 open=1005007 merge=7035048 full=1005006 evict=0 direct=0 still_open=1
  merge part=3 open=1005014 merge=7035034 full=1005000 evict=14 direct=0 still_open=0
  (kernel) [86499.611305] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86499.631803] NVMeVirt: Virtual NVMe device closed
[merge map32k bs16k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071523 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071523 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071511 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071511 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=1071523 merge=1071523 full=1071523 evict=0 direct=0 still_open=0
  merge part=1 open=1071523 merge=1071512 full=1071512 evict=11 direct=0 still_open=0
  merge part=2 open=1071512 merge=1071511 full=1071511 evict=0 direct=0 still_open=1
  merge part=3 open=1071511 merge=1071511 full=1071511 evict=0 direct=0 still_open=0
  (kernel) [84035.906500] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84035.927101] NVMeVirt: Virtual NVMe device closed
[merge map32k bs16k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071486 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071486 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071474 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071474 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=1071486 merge=1071486 full=1071486 evict=0 direct=0 still_open=0
  merge part=1 open=1071486 merge=1071475 full=1071475 evict=11 direct=0 still_open=0
  merge part=2 open=1071474 merge=1071474 full=1071474 evict=0 direct=0 still_open=0
  merge part=3 open=1071474 merge=1071474 full=1071474 evict=0 direct=0 still_open=0
  (kernel) [85302.937373] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85302.957988] NVMeVirt: Virtual NVMe device closed
[merge map32k bs16k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071507 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071506 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071495 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071495 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=1071507 merge=1071507 full=1071507 evict=0 direct=0 still_open=0
  merge part=1 open=1071506 merge=1071495 full=1071495 evict=11 direct=0 still_open=0
  merge part=2 open=1071495 merge=1071495 full=1071495 evict=0 direct=0 still_open=0
  merge part=3 open=1071495 merge=1071495 full=1071495 evict=0 direct=0 still_open=0
  (kernel) [86569.944215] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86569.964810] NVMeVirt: Virtual NVMe device closed
[merge map32k bs32k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071516 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071505 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071505 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071504 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=1071516 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=1071505 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=1071505 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=1071504 still_open=0
  (kernel) [84106.254104] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84106.274361] NVMeVirt: Virtual NVMe device closed
[merge map32k bs32k r2]
  +5.694s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.695s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.695s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.695s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071499 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071487 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071487 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071487 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=1071499 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=1071487 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=1071487 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=1071487 still_open=0
  (kernel) [85373.292007] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85373.312341] NVMeVirt: Virtual NVMe device closed
[merge map32k bs32k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071518 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071506 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071506 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071506 gc_pgs=0 gc_cnt=3806 free_lines=3
  merge part=0 open=0 merge=0 full=0 evict=0 direct=1071518 still_open=0
  merge part=1 open=0 merge=0 full=0 evict=0 direct=1071506 still_open=0
  merge part=2 open=0 merge=0 full=0 evict=0 direct=1071506 still_open=0
  merge part=3 open=0 merge=0 full=0 evict=0 direct=1071506 still_open=0
  (kernel) [86640.294160] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86640.314800] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs4k r1]
  +5.881s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.881s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.881s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.881s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8055932 gc_pgs=0 gc_cnt=3554 free_lines=3
  stats part=1 host_pgs=8055921 gc_pgs=0 gc_cnt=3554 free_lines=3
  stats part=2 host_pgs=8055921 gc_pgs=0 gc_cnt=3554 free_lines=3
  stats part=3 host_pgs=8055921 gc_pgs=0 gc_cnt=3554 free_lines=3
  (kernel) [82909.766211] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [82909.834079] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs4k r2]
  +5.913s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.913s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.913s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.913s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8025884 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=1 host_pgs=8025873 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=2 host_pgs=8025873 gc_pgs=0 gc_cnt=3539 free_lines=3
  stats part=3 host_pgs=8025873 gc_pgs=0 gc_cnt=3539 free_lines=3
  (kernel) [84176.739695] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84176.807720] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs4k r3]
  +5.947s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.947s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.947s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.947s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=7991610 gc_pgs=0 gc_cnt=3523 free_lines=3
  stats part=1 host_pgs=7991600 gc_pgs=0 gc_cnt=3523 free_lines=3
  stats part=2 host_pgs=7991600 gc_pgs=0 gc_cnt=3523 free_lines=3
  stats part=3 host_pgs=7991599 gc_pgs=0 gc_cnt=3523 free_lines=3
  (kernel) [85443.803855] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85443.871180] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r1]
  +5.695s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.695s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.695s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.695s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8570250 gc_pgs=0 gc_cnt=3805 free_lines=3
  stats part=1 host_pgs=8570250 gc_pgs=0 gc_cnt=3805 free_lines=3
  stats part=2 host_pgs=8570250 gc_pgs=0 gc_cnt=3805 free_lines=3
  stats part=3 host_pgs=8570250 gc_pgs=0 gc_cnt=3805 free_lines=3
  (kernel) [82980.204495] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [82980.272313] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573835 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573835 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573835 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573835 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [84247.156264] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84247.224299] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573662 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573662 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573662 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573662 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [85514.242810] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85514.309630] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573708 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573708 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573708 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573708 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [83050.629708] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83050.696447] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573962 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573962 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573962 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573962 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [84317.581803] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84317.649753] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=2048 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=8573786 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=8573786 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=8573786 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=8573786 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [85584.682904] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85584.750101] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r1]
  +5.692s first GC part=0 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=1 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=2 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=3 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=1283780 gc_pgs=450355 gc_cnt=3006 free_lines=2
  stats part=1 host_pgs=1283780 gc_pgs=450355 gc_cnt=3006 free_lines=2
  stats part=2 host_pgs=1283780 gc_pgs=450355 gc_cnt=3006 free_lines=2
  stats part=3 host_pgs=1283774 gc_pgs=451407 gc_cnt=3008 free_lines=2
  (kernel) [83121.002644] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83121.030207] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r2]
  +5.692s first GC part=0 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=1 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=2 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=3 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=1287220 gc_pgs=451507 gc_cnt=3015 free_lines=2
  stats part=1 host_pgs=1287220 gc_pgs=451507 gc_cnt=3015 free_lines=2
  stats part=2 host_pgs=1287217 gc_pgs=451507 gc_cnt=3015 free_lines=2
  stats part=3 host_pgs=1287213 gc_pgs=452559 gc_cnt=3017 free_lines=2
  (kernel) [84387.991300] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84388.018786] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r3]
  +5.692s first GC part=0 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=1 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=2 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  +5.692s first GC part=3 victim line=0 vpc=128 ipc=384 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=1287164 gc_pgs=451379 gc_cnt=3014 free_lines=2
  stats part=1 host_pgs=1287161 gc_pgs=451379 gc_cnt=3014 free_lines=2
  stats part=2 host_pgs=1287160 gc_pgs=451379 gc_cnt=3014 free_lines=2
  stats part=3 host_pgs=1287157 gc_pgs=452431 gc_cnt=3016 free_lines=2
  (kernel) [85655.036139] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85655.063781] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r1]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143220 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=2143220 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=2143220 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=2143208 gc_pgs=0 gc_cnt=3806 free_lines=3
  (kernel) [83191.377395] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83191.404989] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143306 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143306 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143305 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143294 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [84458.366820] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84458.394394] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143246 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143246 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143245 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143234 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [85725.393498] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85725.421023] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r1]
  +5.694s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.694s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.694s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.694s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2142981 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=2142981 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=2142969 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=2142969 gc_pgs=0 gc_cnt=3806 free_lines=3
  (kernel) [83261.739966] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83261.767504] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143350 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143350 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143339 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143339 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [84528.720284] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84528.747833] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=512 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=2143299 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=1 host_pgs=2143299 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=2 host_pgs=2143287 gc_pgs=0 gc_cnt=3807 free_lines=3
  stats part=3 host_pgs=2143287 gc_pgs=0 gc_cnt=3807 free_lines=3
  (kernel) [85795.729932] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85795.757714] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs4k r1]
  +5.692s first GC part=0 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=1 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=2 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=3 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=804608 gc_pgs=116160 gc_cnt=3215 free_lines=1
  stats part=1 host_pgs=804603 gc_pgs=116160 gc_cnt=3215 free_lines=2
  stats part=2 host_pgs=804592 gc_pgs=116160 gc_cnt=3215 free_lines=2
  stats part=3 host_pgs=804592 gc_pgs=116160 gc_cnt=3215 free_lines=2
  (kernel) [83332.103399] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83332.123841] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs4k r2]
  +5.692s first GC part=0 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=1 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=2 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=3 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=804608 gc_pgs=116160 gc_cnt=3215 free_lines=1
  stats part=1 host_pgs=804603 gc_pgs=116160 gc_cnt=3215 free_lines=2
  stats part=2 host_pgs=804592 gc_pgs=116160 gc_cnt=3215 free_lines=2
  stats part=3 host_pgs=804592 gc_pgs=116160 gc_cnt=3215 free_lines=2
  (kernel) [84599.080785] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84599.101187] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs4k r3]
  +5.692s first GC part=0 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=1 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=2 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  +5.692s first GC part=3 victim line=0 vpc=32 ipc=224 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=804608 gc_pgs=116160 gc_cnt=3215 free_lines=1
  stats part=1 host_pgs=804603 gc_pgs=116160 gc_cnt=3215 free_lines=2
  stats part=2 host_pgs=804592 gc_pgs=116160 gc_cnt=3215 free_lines=2
  stats part=3 host_pgs=804592 gc_pgs=116160 gc_cnt=3215 free_lines=2
  (kernel) [85866.055422] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85866.076014] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs16k r1]
  +5.692s first GC part=0 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=1 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=2 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=3 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=354288 gc_pgs=248804 gc_cnt=1975 free_lines=3
  stats part=1 host_pgs=354286 gc_pgs=248782 gc_cnt=1975 free_lines=3
  stats part=2 host_pgs=354284 gc_pgs=248839 gc_cnt=1975 free_lines=2
  stats part=3 host_pgs=354284 gc_pgs=248839 gc_cnt=1975 free_lines=2
  (kernel) [83402.454682] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83402.475018] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs16k r2]
  +5.692s first GC part=0 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=1 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=2 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=3 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=354288 gc_pgs=248804 gc_cnt=1975 free_lines=3
  stats part=1 host_pgs=354286 gc_pgs=248782 gc_cnt=1975 free_lines=3
  stats part=2 host_pgs=354284 gc_pgs=248839 gc_cnt=1975 free_lines=2
  stats part=3 host_pgs=354284 gc_pgs=248839 gc_cnt=1975 free_lines=2
  (kernel) [84669.418230] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84669.438739] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs16k r3]
  +5.692s first GC part=0 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=1 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=2 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  +5.692s first GC part=3 victim line=0 vpc=128 ipc=128 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=354356 gc_pgs=248804 gc_cnt=1975 free_lines=2
  stats part=1 host_pgs=354355 gc_pgs=248782 gc_cnt=1975 free_lines=2
  stats part=2 host_pgs=354354 gc_pgs=248967 gc_cnt=1976 free_lines=2
  stats part=3 host_pgs=354352 gc_pgs=248967 gc_cnt=1976 free_lines=2
  (kernel) [85936.412008] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [85936.432514] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs32k r1]
  +5.692s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.692s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.692s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.692s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071345 gc_pgs=0 gc_cnt=3805 free_lines=3
  stats part=1 host_pgs=1071334 gc_pgs=0 gc_cnt=3805 free_lines=3
  stats part=2 host_pgs=1071333 gc_pgs=0 gc_cnt=3805 free_lines=3
  stats part=3 host_pgs=1071333 gc_pgs=0 gc_cnt=3805 free_lines=3
  (kernel) [83472.716856] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [83472.737297] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs32k r2]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071530 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071519 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071518 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071518 gc_pgs=0 gc_cnt=3806 free_lines=3
  (kernel) [84739.763687] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [84739.784011] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs32k r3]
  +5.693s first GC part=0 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=1 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=2 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  +5.693s first GC part=3 victim line=0 vpc=0 ipc=256 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=1071513 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=1 host_pgs=1071501 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=2 host_pgs=1071501 gc_pgs=0 gc_cnt=3806 free_lines=3
  stats part=3 host_pgs=1071501 gc_pgs=0 gc_cnt=3806 free_lines=3
  (kernel) [86006.756651] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [86006.777274] NVMeVirt: Virtual NVMe device closed
```

### 11.3.7 1 초 평균 대역폭 시계열 (MiB/s, t=1..60 s, fio_bw.1.log 의 0.5 s 값 두 개 평균)
형식: variant map bs rep | gc_onset_s | 값 60개 (공백 구분)
```
merge 4k 4k r1 | 5.918 | 2151 2151 2145 2150 2145 2105 2091 2086 2086 2086 2081 2083 2083 2082 2081 2081 2082 2084 2084 2084 2083 2082 2085 2087 2085 2083 2083 2081 2088 2085 2084 2085 2084 2085 2087 2087 2086 2085 2084 2090 2086 2083 2087 2082 2085 2087 2086 2086 2083 2081 2090 2087 2083 2084 2086 2085 2087 2084 2081 2085
merge 4k 4k r2 | 5.940 | 2144 2140 2140 2137 2135 2099 2084 2083 2079 2081 2078 2080 2084 2078 2079 2079 2076 2080 2080 2078 2079 2076 2080 2081 2078 2079 2078 2076 2079 2079 2075 2075 2077 2075 2078 2074 2075 2077 2075 2083 2078 2078 2080 2079 2077 2077 2075 2078 2078 2076 2082 2082 2081 2081 2080 2074 2078 2077 2076 2079
merge 4k 4k r3 | 5.928 | 2149 2143 2141 2142 2147 2103 2085 2083 2084 2083 2083 2083 2086 2083 2083 2080 2078 2085 2082 2080 2081 2075 2085 2080 2080 2080 2081 2080 2083 2078 2081 2079 2083 2080 2086 2082 2083 2082 2076 2082 2081 2078 2078 2079 2082 2085 2083 2082 2080 2076 2083 2082 2079 2078 2078 2079 2079 2078 2079 2078
merge 4k 16k r1 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2227 2229 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2230 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
merge 4k 16k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
merge 4k 16k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
merge 4k 32k r1 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
merge 4k 32k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
merge 4k 32k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
merge 16k 4k r1 | 5.920 | 2153 2150 2147 2146 2147 2097 2083 2084 2083 2085 2079 2088 2087 2085 2085 2084 2082 2087 2087 2088 2087 2082 2086 2087 2088 2086 2083 2082 2085 2087 2088 2081 2085 2087 2086 2085 2086 2086 2081 2086 2081 2079 2081 2078 2086 2083 2083 2083 2084 2080 2089 2088 2085 2085 2082 2086 2090 2086 2086 2088
merge 16k 4k r2 | 5.898 | 2156 2159 2156 2155 2154 2103 2090 2088 2086 2083 2083 2092 2093 2091 2091 2091 2084 2091 2091 2087 2087 2085 2090 2087 2087 2088 2089 2085 2087 2084 2086 2085 2079 2081 2087 2085 2086 2085 2082 2089 2087 2086 2084 2083 2091 2089 2086 2089 2089 2087 2092 2090 2089 2091 2086 2087 2086 2086 2088 2087
merge 16k 4k r3 | 5.885 | 2161 2166 2159 2162 2159 2114 2100 2097 2094 2092 2092 2093 2095 2094 2096 2095 2091 2098 2093 2094 2093 2092 2100 2096 2095 2097 2100 2092 2098 2094 2094 2096 2094 2099 2096 2095 2094 2093 2088 2093 2093 2090 2092 2091 2094 2093 2094 2091 2093 2097 2100 2095 2095 2096 2097 2096 2097 2096 2093 2093
merge 16k 16k r1 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2230 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2230 2233 2233 2233 2233 2231 2233 2233 2233
merge 16k 16k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2230 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233
merge 16k 16k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2230 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233
merge 16k 32k r1 | 5.693 | 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233
merge 16k 32k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233
merge 16k 32k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233
merge 32k 4k r1 | 5.904 | 2157 2155 2152 2152 2153 2112 2095 2092 2090 2090 2087 2093 2091 2089 2089 2089 2089 2094 2094 2089 2087 2089 2095 2092 2090 2088 2092 2090 2098 2093 2089 2090 2090 2086 2090 2088 2086 2084 2086 2090 2090 2081 2084 2081 2091 2093 2092 2092 2089 2087 2092 2088 2091 2092 2090 2092 2095 2090 2089 2091
merge 32k 4k r2 | 5.903 | 2158 2158 2154 2150 2152 2109 2093 2092 2081 2090 2087 2091 2089 2087 2088 2087 2088 2092 2090 2091 2089 2088 2090 2091 2089 2089 2087 2090 2093 2090 2089 2089 2088 2093 2092 2089 2088 2089 2085 2092 2091 2090 2089 2087 2095 2092 2087 2088 2090 2087 2091 2090 2089 2087 2084 2090 2091 2088 2088 2087
merge 32k 4k r3 | 5.909 | 2160 2135 2154 2154 2154 2110 2094 2091 2089 2088 2087 2091 2092 2091 2091 2091 2089 2094 2091 2089 2089 2084 2089 2089 2085 2087 2087 2086 2088 2086 2083 2085 2085 2089 2091 2087 2087 2088 2084 2092 2092 2088 2088 2085 2091 2093 2089 2088 2090 2085 2091 2087 2086 2086 2086 2087 2089 2086 2086 2086
merge 32k 16k r1 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233
merge 32k 16k r2 | 5.693 | 2234 2233 2233 2233 2233 2231 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2228 2233 2233 2233 2233 2229 2233 2233 2233
merge 32k 16k r3 | 5.693 | 2234 2233 2233 2233 2233 2231 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2228 2233 2233 2233
merge 32k 32k r1 | 5.693 | 2234 2233 2233 2233 2233 2232 2229 2233 2233 2233 2232 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233
merge 32k 32k r2 | 5.694 | 2235 2233 2233 2233 2233 2232 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2232
merge 32k 32k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233
wbuffix 4k 4k r1 | 5.881 | 2168 2166 2163 2163 2158 2109 2101 2095 2098 2096 2085 2079 2099 2089 2098 2091 2092 2093 2092 2086 2092 2075 2098 2100 2099 2093 2095 2093 2099 2079 2094 2094 2090 2100 2092 2078 2094 2094 2097 2103 2095 2090 2084 2092 2094 2095 2093 2094 2094 2091 2095 2093 2095 2089 2086 2076 2092 2089 2089 2087
wbuffix 4k 4k r2 | 5.913 | 2153 2153 2153 2149 2147 2105 2092 2089 2088 2085 2084 2087 2091 2087 2082 2085 2084 2086 2084 2087 2084 2081 2082 2086 2082 2083 2085 2084 2091 2086 2085 2087 2083 2084 2084 2083 2083 2083 2079 2086 2085 2083 2081 2082 2085 2086 2084 2084 2086 2080 2088 2086 2083 2083 2079 2086 2084 2079 2081 2079
wbuffix 4k 4k r3 | 5.947 | 2140 2139 2139 2137 2132 2101 2082 2080 2077 2077 2073 2074 2075 2073 2073 2072 2071 2081 2078 2074 2075 2072 2078 2081 2079 2078 2079 2074 2077 2078 2076 2078 2076 2072 2080 2077 2078 2078 2070 2074 2074 2071 2071 2072 2075 2077 2074 2076 2078 2070 2078 2079 2076 2076 2074 2075 2080 2075 2076 2078
wbuffix 4k 16k r1 | 5.695 | 2234 2233 2233 2233 2229 2232 2233 2233 2233 2233 2231 2232 2228 2228 2233 2232 2233 2233 2232 2233 2232 2233 2233 2233 2223 2232 2231 2233 2233 2233 2232 2233 2233 2233 2233 2231 2228 2233 2233 2233 2230 2231 2233 2233 2233 2233 2224 2232 2233 2233 2233 2226 2233 2233 2233 2233 2232 2233 2233 2233
wbuffix 4k 16k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
wbuffix 4k 16k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
wbuffix 4k 32k r1 | 5.693 | 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2229 2233 2233 2232 2232 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
wbuffix 4k 32k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2232
wbuffix 4k 32k r3 | 5.693 | 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233 2233 2232 2233 2233 2233
wbuffix 16k 4k r1 | 5.692 | 559 558 558 558 558 433 329 329 329 329 329 330 327 327 327 327 326 328 325 329 325 329 325 328 326 328 326 327 327 326 328 411 324 302 222 220 223 218 222 219 221 222 220 262 326 336 336 336 336 336 336 336 336 336 336 336 336 336 336 336
wbuffix 16k 4k r2 | 5.692 | 559 558 558 558 558 433 329 329 329 329 329 330 330 330 330 330 329 329 329 329 329 329 330 330 330 330 330 329 329 329 329 411 326 285 222 219 221 222 219 222 218 222 219 256 319 336 336 336 336 336 336 336 336 336 336 336 336 336 336 336
wbuffix 16k 4k r3 | 5.692 | 559 558 558 558 558 433 329 329 329 329 329 330 330 330 330 330 329 329 329 329 329 329 330 330 330 330 330 329 329 329 329 411 325 285 222 219 221 222 219 223 218 222 219 269 338 336 336 336 336 336 336 336 336 336 336 336 336 336 336 336
wbuffix 16k 16k r1 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2230 2233 2232 2232 2233 2232 2233 2233 2233 2233 2230 2233 2233 2233 2233 2230 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2228 2233 2233 2233 2233 2231 2233 2233 2233 2231 2232 2233 2233 2233 2233 2231 2233 2233 2233
wbuffix 16k 16k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2229 2233 2233 2233 2233 2232 2233 2233 2233 2233 2230 2233 2233 2233 2233 2231 2233 2233 2233
wbuffix 16k 16k r3 | 5.693 | 2234 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2229 2233 2233 2233
wbuffix 16k 32k r1 | 5.694 | 2234 2232 2233 2233 2233 2232 2233 2233 2233 2233 2231 2225 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2225 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2230 2233 2233 2233 2233 2231 2231 2233 2233 2233 2232 2227 2233 2233
wbuffix 16k 32k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233
wbuffix 16k 32k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2231 2233 2233 2233 2233 2229 2233 2233 2233 2233 2232 2233 2233 2233
wbuffix 32k 4k r1 | 5.692 | 279 279 279 279 279 240 206 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 206 207 207 207 207 207 206 228 209 207 207 153 112 112
wbuffix 32k 4k r2 | 5.692 | 279 279 279 279 279 240 206 206 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 206 206 207 207 207 207 207 207 228 209 207 207 153 112 112
wbuffix 32k 4k r3 | 5.692 | 279 279 279 279 279 240 206 206 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 207 206 206 207 207 207 228 209 207 207 153 112 112
wbuffix 32k 16k r1 | 5.692 | 1117 1117 1117 1116 1117 717 390 390 392 392 392 392 392 391 389 390 392 392 392 487 407 238 237 238 237 237 238 238 237 237 238 237 238 238 236 237 238 237 238 238 237 237 238 282 272 272 274 273 275 273 272 272 273 272 272 272 273 272 272 272
wbuffix 32k 16k r2 | 5.692 | 1117 1116 1117 1117 1116 718 390 390 392 392 392 392 392 390 389 390 392 392 392 487 407 238 237 237 238 237 238 238 237 237 238 237 237 238 237 237 237 238 237 237 238 237 237 306 269 272 272 273 275 273 272 272 272 273 272 272 274 273 272 272
wbuffix 32k 16k r3 | 5.692 | 1117 1117 1117 1117 1116 718 392 392 392 390 390 392 392 392 392 392 390 389 389 491 405 238 238 236 237 238 237 237 237 238 237 238 238 238 237 237 237 237 237 237 237 238 237 284 274 272 272 272 273 272 272 273 273 272 272 273 273 273 273 273
wbuffix 32k 32k r1 | 5.692 | 2230 2233 2233 2233 2233 2232 2233 2233 2233 2233 2229 2227 2233 2233 2233 2232 2233 2233 2233 2233 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2230 2233 2233 2233 2233 2233 2229 2228 2231 2232 2233 2232 2233 2233 2233 2233 2230 2233 2233 2232 2222 2232 2233 2233 2233 2233 2229 2233 2233 2233
wbuffix 32k 32k r2 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2234 2230 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233
wbuffix 32k 32k r3 | 5.693 | 2234 2233 2233 2233 2233 2232 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233 2233 2229 2233 2233 2233
```

### 11.3.8 실험 전후 환경 차이 (env_before vs env_after_* 의 마지막 스냅샷; 날짜·부하·여유 메모리 줄 제외)
- env_after_merge:
  - 08_nvmevirt_git.txt:
    `+ M EXPERIMENT_LOG_FOR_CLAUDE.md`
    `+ M README.md`
    `+ M exp/report/make_md_results.py`
    `+ M exp/report/make_report.py`
  - 09_block.txt:
    `-/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        122.10  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`
    `+/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        122.11  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`
- env_after_wbuffix:
  - 08_nvmevirt_git.txt:
    `+ M EXPERIMENT_LOG_FOR_CLAUDE.md`
    `+ M README.md`
    `+ M exp/report/make_md_results.py`
    `+ M exp/report/make_report.py`
  - 09_block.txt:
    `-/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        122.10  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`
    `+/dev/nvme0n1          /dev/ng0n1            S5GYNF0RA00765J      Samsung SSD 980 PRO 500GB                0x1        122.11  GB / 500.11  GB    512   B +  0 B   3B2QGXA7`

### 11.3.9 run_all 로그 끝 40 줄 (원본 로그, 시각은 KST 로 변환)
```
[2026-10-08 21:16:12 KST] skip (already done): map4k_bs4k_r1
[2026-10-08 21:16:12 KST] skip (already done): map4k_bs16k_r1
[2026-10-08 21:16:12 KST] skip (already done): map4k_bs32k_r1
[2026-10-08 21:16:12 KST] skip (already done): map16k_bs4k_r1
[2026-10-08 21:16:12 KST] skip (already done): map16k_bs16k_r1
[2026-10-08 21:16:12 KST] skip (already done): map16k_bs32k_r1
[2026-10-08 21:16:12 KST] skip (already done): map32k_bs4k_r1
[2026-10-08 21:16:12 KST] skip (already done): map32k_bs16k_r1
[2026-10-08 21:16:12 KST] skip (already done): map32k_bs32k_r1
[2026-10-08 21:16:12 KST] skip (already done): map4k_bs4k_r2
[2026-10-08 21:16:12 KST] skip (already done): map4k_bs16k_r2
[2026-10-08 21:16:12 KST] skip (already done): map4k_bs32k_r2
[2026-10-08 21:16:12 KST] skip (already done): map16k_bs4k_r2
[2026-10-08 21:16:12 KST] skip (already done): map16k_bs16k_r2
[2026-10-08 21:16:12 KST] skip (already done): map16k_bs32k_r2
[2026-10-08 21:16:12 KST] skip (already done): map32k_bs4k_r2
[2026-10-08 21:16:12 KST] skip (already done): map32k_bs16k_r2
[2026-10-08 21:16:12 KST] skip (already done): map32k_bs32k_r2
[2026-10-08 21:16:12 KST] === [1/27] variant=merge cache=nodrop map=4k bs=4k rep=3 ===
    -> 2086.4 MiB/s, 534116 IOPS, clat mean 59.0 us
[2026-10-08 21:17:22 KST] === [2/27] variant=merge cache=nodrop map=4k bs=16k rep=3 ===
    -> 2232.7 MiB/s, 142893 IOPS, clat mean 222.5 us
[2026-10-08 21:18:33 KST] === [3/27] variant=merge cache=nodrop map=4k bs=32k rep=3 ===
    -> 2232.7 MiB/s, 71448 IOPS, clat mean 446.0 us
[2026-10-08 21:19:43 KST] === [4/27] variant=merge cache=nodrop map=16k bs=4k rep=3 ===
    -> 2100.3 MiB/s, 537667 IOPS, clat mean 58.6 us
[2026-10-08 21:20:53 KST] === [5/27] variant=merge cache=nodrop map=16k bs=16k rep=3 ===
    -> 2232.6 MiB/s, 142885 IOPS, clat mean 222.5 us
[2026-10-08 21:22:04 KST] === [6/27] variant=merge cache=nodrop map=16k bs=32k rep=3 ===
    -> 2232.6 MiB/s, 71443 IOPS, clat mean 446.0 us
[2026-10-08 21:23:14 KST] === [7/27] variant=merge cache=nodrop map=32k bs=4k rep=3 ===
    -> 2093.7 MiB/s, 535997 IOPS, clat mean 58.7 us
[2026-10-08 21:24:24 KST] === [8/27] variant=merge cache=nodrop map=32k bs=16k rep=3 ===
    -> 2232.3 MiB/s, 142864 IOPS, clat mean 222.5 us
[2026-10-08 21:25:35 KST] === [9/27] variant=merge cache=nodrop map=32k bs=32k rep=3 ===
    -> 2232.3 MiB/s, 71433 IOPS, clat mean 446.1 us
environment snapshot -> /home/dccearth/jsw/nvmevirt/exp/results/seq3x3_20261008/env_after_merge
[2026-10-08 21:26:45 KST] finished: /home/dccearth/jsw/nvmevirt/exp/results/seq3x3_20261008/merge
54 runs, 0 failed -> /home/dccearth/jsw/nvmevirt/exp/results/seq3x3_20261008/analysis
SEQ-ALL-DONE
```

## 11.4 randbs_20261008  (묶음 경로 repo/exp/results/randbs_20261008/)

### 11.4.1 회차 목록
- wbuffix: 완료 회차 18 (DONE 있음). run.log 첫 시각 2026-10-08 22:11:48 KST, 마지막 시각 2026-10-08 22:32:55 KST. chmodel 오류 줄 합계 0. chmodel>0 회차 0. kernel_warn>0 회차 0.
  - 미완료/없음 0: -

### 11.4.2 조합별 행렬 (행 = 매핑 단위, 열 = fio bs). 칸 = mean ± std [min..max], n = 그 조합의 완료 회차 수(보통 3)
#### randbs_20261008 · wbuffix · bw_MiBps
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 437.018 ± 1.223 [435.709..438.131] | 486.317 ± 0.025 [486.294..486.344] |
| 16K | 217.303 ± 0.143 [217.188..217.463] | 486.401 ± 0.105 [486.280..486.472] |
| 32K | 131.949 ± 0.160 [131.824..132.129] | 447.136 ± 0.026 [447.111..447.164] |

#### randbs_20261008 · wbuffix · iops
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 55938.317 ± 156.481 [55770.834..56080.782] | 7781.083 ± 0.407 [7780.707..7781.515] |
| 16K | 27814.790 ± 18.305 [27800.037..27835.275] | 7782.422 ± 1.674 [7780.500..7783.554] |
| 32K | 16889.537 ± 20.417 [16873.604..16912.552] | 7154.188 ± 0.419 [7153.791..7154.626] |

#### randbs_20261008 · wbuffix · clat_mean_us
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 570.842 ± 1.607 [569.383..572.565] | 4109.675 ± 0.188 [4109.470..4109.839] |
| 16K | 1149.157 ± 0.769 [1148.295..1149.773] | 4108.971 ± 0.839 [4108.400..4109.934] |
| 32K | 1893.334 ± 2.290 [1890.756..1895.132] | 4470.025 ± 0.221 [4469.786..4470.221] |

#### randbs_20261008 · wbuffix · clat_p50_us
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 120.320 ± 0.000 [120.320..120.320] | 897.024 ± 0.000 [897.024..897.024] |
| 16K | 248.832 ± 0.000 [248.832..248.832] | 897.024 ± 0.000 [897.024..897.024] |
| 32K | 561.152 ± 0.000 [561.152..561.152] | 978.944 ± 0.000 [978.944..978.944] |

#### randbs_20261008 · wbuffix · clat_p99_us
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 16580.608 ± 0.000 [16580.608..16580.608] | 19005.440 ± 0.000 [19005.440..19005.440] |
| 16K | 16536.917 ± 75.674 [16449.536..16580.608] | 19005.440 ± 0.000 [19005.440..19005.440] |
| 32K | 15051.435 ± 75.674 [15007.744..15138.816] | 19005.440 ± 0.000 [19005.440..19005.440] |

#### randbs_20261008 · wbuffix · clat_p999_us
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 17782.101 ± 151.349 [17694.720..17956.864] | 19529.728 ± 0.000 [19529.728..19529.728] |
| 16K | 17694.720 ± 0.000 [17694.720..17694.720] | 19529.728 ± 0.000 [19529.728..19529.728] |
| 32K | 16012.629 ± 75.674 [15925.248..16056.320] | 19617.109 ± 151.349 [19529.728..19791.872] |

#### randbs_20261008 · wbuffix · lat_mean_us
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 571.830 ± 1.599 [570.377..573.543] | 4112.269 ± 0.191 [4112.067..4112.447] |
| 16K | 1150.216 ± 0.756 [1149.369..1150.823] | 4111.559 ± 0.885 [4110.985..4112.578] |
| 32K | 1894.410 ± 2.294 [1891.824..1896.199] | 4472.628 ± 0.235 [4472.381..4472.850] |

#### randbs_20261008 · wbuffix · slat_mean_us
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 0.988 ± 0.009 [0.978..0.994] | 2.593 ± 0.017 [2.575..2.608] |
| 16K | 1.059 ± 0.013 [1.050..1.074] | 2.588 ± 0.054 [2.536..2.644] |
| 32K | 1.076 ± 0.015 [1.067..1.094] | 2.603 ± 0.023 [2.586..2.629] |

#### randbs_20261008 · wbuffix · bw_first10s_MiBps
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 1285.577 ± 0.445 [1285.062..1285.835] | 1293.671 ± 0.004 [1293.667..1293.673] |
| 16K | 736.204 ± 0.245 [735.922..736.346] | 1293.673 ± 0.000 [1293.673..1293.673] |
| 32K | 377.150 ± 0.087 [377.098..377.251] | 1286.820 ± 0.003 [1286.818..1286.824] |

#### randbs_20261008 · wbuffix · bw_last20s_MiBps
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 330.076 ± 4.591 [325.344..334.511] | 254.474 ± 0.135 [254.386..254.630] |
| 16K | 80.895 ± 0.096 [80.785..80.964] | 254.663 ± 0.282 [254.364..254.924] |
| 32K | 60.501 ± 0.556 [59.910..61.014] | 319.961 ± 0.135 [319.806..320.043] |

#### randbs_20261008 · wbuffix · gc_onset_s
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 5.739 ± 0.001 [5.737..5.740] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.905 ± 0.000 [5.905..5.905] | 5.693 ± 0.000 [5.693..5.693] |
| 32K | 6.067 ± 0.000 [6.067..6.067] | 5.973 ± 0.000 [5.972..5.973] |

#### randbs_20261008 · wbuffix · gc_onset_last_part_s
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 5.758 ± 0.001 [5.756..5.759] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.972 ± 0.000 [5.972..5.973] | 5.693 ± 0.000 [5.693..5.693] |
| 32K | 6.122 ± 0.000 [6.122..6.122] | 5.995 ± 0.000 [5.995..5.995] |

#### randbs_20261008 · wbuffix · bw_pre_gc_MiBps
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 2211.022 ± 0.001 [2211.021..2211.023] | 2217.879 ± 0.007 [2217.872..2217.883] |
| 16K | 1072.020 ± 0.023 [1071.994..1072.034] | 2217.883 ± 0.000 [2217.883..2217.883] |
| 32K | 512.568 ± 0.002 [512.566..512.569] | 2124.234 ± 0.030 [2124.202..2124.262] |

#### randbs_20261008 · wbuffix · bw_post_gc_MiBps
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 258.085 ± 1.353 [256.648..259.335] | 311.690 ± 0.049 [311.658..311.746] |
| 16K | 131.089 ± 0.155 [130.966..131.263] | 311.759 ± 0.107 [311.645..311.857] |
| 32K | 89.674 ± 0.192 [89.526..89.891] | 277.957 ± 0.003 [277.954..277.960] |

#### randbs_20261008 · wbuffix · gc_cnt
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 9359.333 ± 62.268 [9294..9418] | 11345.333 ± 2.309 [11344..11348] |
| 16K | 8087.333 ± 16.653 [8074..8106] | 11346.667 ± 2.309 [11344..11348] |
| 32K | 7353.000 ± 29.547 [7329..7386] | 9562.000 ± 0.000 [9562..9562] |

#### randbs_20261008 · wbuffix · ftl_host_pgs
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 6713531 ± 18938.907 [6693504..6731152] | 7471168 ± 639.199 [7470752..7471904] |
| 16K | 1668989 ± 1079.137 [1668164..1670210] | 1868020 ± 391.939 [1867600..1868376] |
| 32K | 1013468 ± 1330.318 [1012450..1014973] | 858598.000 ± 0.000 [858598..858598] |

#### randbs_20261008 · wbuffix · ftl_gc_pgs
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 15575134 ± 108790.159 [15461194..15677914] | 18884208 ± 3866.144 [18881936..18888672] |
| 16K | 3252472 ± 7441.059 [3246459..3260794] | 4721493 ± 781.018 [4720596..4722020] |
| 32K | 1259304 ± 6247.714 [1254180..1266264] | 1979380 ± 0.000 [1979380..1979380] |

#### randbs_20261008 · wbuffix · waf_gc
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 3.320 ± 0.010 [3.310..3.329] | 3.528 ± 0.000 [3.527..3.528] |
| 16K | 2.949 ± 0.003 [2.946..2.952] | 3.528 ± 0.000 [3.527..3.528] |
| 32K | 2.243 ± 0.005 [2.239..2.248] | 3.305 ± 0.000 [3.305..3.305] |

#### randbs_20261008 · wbuffix · waf_total
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 3.320 ± 0.010 [3.310..3.329] | 3.528 ± 0.000 [3.527..3.528] |
| 16K | 5.897 ± 0.006 [5.892..5.904] | 3.528 ± 0.000 [3.527..3.528] |
| 32K | 8.970 ± 0.018 [8.955..8.990] | 3.305 ± 0.000 [3.305..3.305] |

#### randbs_20261008 · wbuffix · written_GiB
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 25.610 ± 0.072 [25.534..25.677] | 28.500 ± 0.002 [28.499..28.503] |
| 16K | 12.735 ± 0.008 [12.728..12.744] | 28.504 ± 0.006 [28.497..28.509] |
| 32K | 7.732 ± 0.010 [7.724..7.744] | 26.202 ± 0.000 [26.202..26.202] |

#### randbs_20261008 · wbuffix · fill_ratio
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 2.284 ± 0.006 [2.277..2.290] | 2.541 ± 0.000 [2.541..2.542] |
| 16K | 1.136 ± 0.001 [1.135..1.136] | 2.542 ± 0.001 [2.541..2.542] |
| 32K | 0.690 ± 0.001 [0.689..0.691] | 2.337 ± 0.000 [2.337..2.337] |

#### randbs_20261008 · wbuffix · chmodel_msgs
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### randbs_20261008 · wbuffix · kernel_warn
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### randbs_20261008 · wbuffix · blk_wr_ios
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 3354977 ± 9449.461 [3344978..3363759] | 466947.667 ± 40.278 [466921..466994] |
| 16K | 1668829 ± 1085.590 [1668020..1670063] | 467004.333 ± 97.449 [466900..467093] |
| 32K | 1013468 ± 1330.318 [1012450..1014973] | 429298.667 ± 0.577 [429298..429299] |

#### randbs_20261008 · wbuffix · blk_wr_merges
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 1788.333 ± 24.826 [1774..1817] | 0.333 ± 0.577 [0..1] |
| 16K | 317.667 ± 38.371 [288..361] | 0.667 ± 0.577 [0..1] |
| 32K | 0.333 ± 0.577 [0..1] | 0.333 ± 0.577 [0..1] |

#### randbs_20261008 · wbuffix · blk_avg_req_KiB
| map\bs | 8K | 64K |
|---|---|---|
| 4K | 8.004 ± 0.000 [8.004..8.004] | 64.000 ± 0.000 [64.000..64.000] |
| 16K | 8.002 ± 0.000 [8.001..8.002] | 64.000 ± 0.000 [64.000..64.000] |
| 32K | 8.000 ± 0.000 [8.000..8.000] | 64.000 ± 0.000 [64.000..64.000] |

### 11.4.4 회차별 전체 (analysis/summary_runs.csv 와 같은 값)
```csv
variant,map,bs,rep,bw_MiBps,iops,written_GiB,fill_ratio,clat_mean_us,clat_p50_us,clat_p99_us,clat_p999_us,lat_mean_us,slat_mean_us,runtime_s,bw_first10s_MiBps,bw_last20s_MiBps,dev_bytes,chmodel_msgs,kernel_warn,blk_wr_ios,blk_wr_merges,blk_avg_req_KiB,gc_onset_s,gc_onset_last_part_s,bw_pre_gc_MiBps,bw_post_gc_MiBps,gc_cnt,ftl_host_pgs,ftl_gc_pgs,waf_gc,waf_total
wbuffix,4k,8k,1,438.130859,56080.782497,25.677307,2.289746,569.382809,120.320000,16580.608000,17694.720000,570.377012,0.994203,60.013000,1285.062305,330.371655,12040984064,0,0,3363759,1817,8.004321,5.737141,5.756448,2211.021307,259.335230,9418,6731152,15677914,3.329158,3.329158
wbuffix,4k,8k,2,437.212891,55963.335167,25.619263,2.284570,570.579001,120.320000,16580.608000,17956.864000,571.570814,0.991813,60.003000,1285.833301,325.344287,12040984064,0,0,3356194,1774,8.004229,5.739599,5.758605,2211.022727,258.271395,9366,6715936,15586294,3.320793,3.320793
wbuffix,4k,8k,3,435.708984,55770.834375,25.533691,2.276940,572.564961,120.320000,16580.608000,17694.720000,573.543219,0.978258,60.009000,1285.834521,334.511279,12040984064,0,0,3344978,1774,8.004243,5.739419,5.758342,2211.022727,256.648393,9294,6693504,15461194,3.309880,3.309880
wbuffix,4k,64k,1,486.293945,7780.706870,28.499023,2.541370,4109.839365,897.024000,19005.440000,19529.728000,4112.447274,2.607909,60.011000,1293.667041,254.405859,12040984064,0,0,466928,0,64.000000,5.693086,5.693272,2217.871893,311.666069,11344,7470848,18881936,3.527415,3.527415
wbuffix,4k,64k,2,486.343750,7781.514566,28.498657,2.541337,4109.470216,897.024000,19005.440000,19529.728000,4112.067183,2.596967,60.004000,1293.673291,254.386230,12040984064,0,0,466921,1,64.000137,5.692843,5.693033,2217.883256,311.657890,11344,7470752,18882016,3.527459,3.527459
wbuffix,4k,64k,3,486.313477,7781.028709,28.503052,2.541729,4109.716784,897.024000,19005.440000,19529.728000,4112.292090,2.575307,60.017000,1293.673291,254.629785,12040984064,0,0,466994,0,64.000000,5.692765,5.692956,2217.883256,311.746407,11348,7471904,18888672,3.527960,3.527960
wbuffix,16k,8k,1,217.257812,27809.058792,12.731674,1.135333,1149.401972,248.832000,16580.608000,17694.720000,1150.455358,1.053385,60.008000,735.921875,80.785034,12040984064,0,0,1668405,361,8.001731,5.905100,5.972510,1071.994318,131.037996,8082,1668592,3250164,2.947848,5.895082
wbuffix,16k,8k,2,217.462891,27835.274709,12.743889,1.136423,1148.294872,248.832000,16449.536000,17694.720000,1149.368839,1.073967,60.009000,736.346484,80.936182,12040984064,0,0,1670063,304,8.001456,5.904937,5.972377,1072.034091,131.263116,8106,1670210,3260794,2.952326,5.904097
wbuffix,16k,8k,3,217.187500,27800.036660,12.728180,1.135022,1149.773176,248.832000,16580.608000,17694.720000,1150.822708,1.049532,60.011000,736.344922,80.963892,12040984064,0,0,1668020,288,8.001381,5.904839,5.972613,1072.032670,130.966134,8074,1668164,3246459,2.946127,5.891745
wbuffix,16k,64k,1,486.280273,7780.499592,28.497314,2.541217,4109.934451,897.024000,19005.440000,19529.728000,4112.578399,2.643948,60.009000,1293.673096,254.364087,12040984064,0,0,466900,0,64.000000,5.693203,5.693323,2217.882901,311.644603,11344,1867600,4720596,3.527627,3.527627
wbuffix,16k,64k,2,486.471680,7783.553607,28.504700,2.541876,4108.400097,897.024000,19005.440000,19529.728000,4110.984836,2.584739,60.001000,1293.673291,254.700244,12040984064,0,0,467020,1,64.000137,5.692717,5.692835,2217.883256,311.776224,11348,1868084,4722020,3.527734,3.527734
wbuffix,16k,64k,3,486.450195,7783.213637,28.509155,2.542273,4108.578080,897.024000,19005.440000,19529.728000,4111.113751,2.535672,60.013000,1293.673291,254.924414,12040984064,0,0,467093,1,64.000137,5.692996,5.693117,2217.883256,311.857368,11348,1868376,4721864,3.527256,3.527256
wbuffix,32k,8k,1,131.893555,16882.453918,7.728432,0.689175,1894.114134,561.152000,15007.744000,15925.248000,1895.208210,1.094076,60.002000,377.101562,59.910327,12040984064,0,0,1012980,1,8.000008,6.067083,6.122088,512.569010,89.603995,7344,1012980,1257468,2.241355,8.965412
wbuffix,32k,8k,2,131.824219,16873.604213,7.724380,0.688813,1895.132102,561.152000,15007.744000,16056.320000,1896.198845,1.066743,60.002000,377.098437,60.578589,12040984064,0,0,1012450,0,8.000000,6.066635,6.121722,512.566406,89.525843,7329,1012450,1254180,2.238757,8.955030
wbuffix,32k,8k,3,132.128906,16912.552280,7.743629,0.690530,1890.755613,561.152000,15138.816000,16056.320000,1891.824242,1.068629,60.013000,377.250781,61.013745,12040984064,0,0,1014973,0,8.000000,6.066664,6.121649,512.569010,89.891086,7386,1014973,1266264,2.247584,8.990336
wbuffix,32k,64k,1,447.133789,7154.148683,26.202332,2.336565,4470.067407,978.944000,19005.440000,19791.872000,4472.653493,2.586085,60.007000,1286.819336,319.806128,12040984064,0,0,429299,0,64.000000,5.972408,5.994798,2124.262429,277.953609,9562,858598,1979380,3.305363,3.305363
wbuffix,32k,64k,2,447.111328,7153.791035,26.202332,2.336565,4470.220853,978.944000,19005.440000,19529.728000,4472.850020,2.629167,60.010000,1286.823779,320.042676,12040984064,0,0,429298,1,64.000149,5.972674,5.995062,2124.202326,277.960310,9562,858598,1979380,3.305363,3.305363
wbuffix,32k,64k,3,447.164062,7154.625602,26.202332,2.336565,4469.785987,978.944000,19005.440000,19529.728000,4472.381158,2.595171,60.003000,1286.817871,320.035425,12040984064,0,0,429299,0,64.000000,5.972658,5.995078,2124.237038,277.956718,9562,858598,1979380,3.305363,3.305363
```

### 11.4.5 조합별 집계 전체 (analysis/summary_agg.csv 와 같은 값)
```csv
variant,map,bs,n,bw_MiBps_mean,bw_MiBps_std,bw_MiBps_min,bw_MiBps_max,iops_mean,iops_std,iops_min,iops_max,written_GiB_mean,written_GiB_std,written_GiB_min,written_GiB_max,fill_ratio_mean,fill_ratio_std,fill_ratio_min,fill_ratio_max,clat_mean_us_mean,clat_mean_us_std,clat_mean_us_min,clat_mean_us_max,clat_p50_us_mean,clat_p50_us_std,clat_p50_us_min,clat_p50_us_max,clat_p99_us_mean,clat_p99_us_std,clat_p99_us_min,clat_p99_us_max,clat_p999_us_mean,clat_p999_us_std,clat_p999_us_min,clat_p999_us_max,lat_mean_us_mean,lat_mean_us_std,lat_mean_us_min,lat_mean_us_max,slat_mean_us_mean,slat_mean_us_std,slat_mean_us_min,slat_mean_us_max,runtime_s_mean,runtime_s_std,runtime_s_min,runtime_s_max,bw_first10s_MiBps_mean,bw_first10s_MiBps_std,bw_first10s_MiBps_min,bw_first10s_MiBps_max,bw_last20s_MiBps_mean,bw_last20s_MiBps_std,bw_last20s_MiBps_min,bw_last20s_MiBps_max,chmodel_msgs_mean,chmodel_msgs_std,chmodel_msgs_min,chmodel_msgs_max,kernel_warn_mean,kernel_warn_std,kernel_warn_min,kernel_warn_max,blk_wr_ios_mean,blk_wr_ios_std,blk_wr_ios_min,blk_wr_ios_max,blk_wr_merges_mean,blk_wr_merges_std,blk_wr_merges_min,blk_wr_merges_max,blk_avg_req_KiB_mean,blk_avg_req_KiB_std,blk_avg_req_KiB_min,blk_avg_req_KiB_max,gc_onset_s_mean,gc_onset_s_std,gc_onset_s_min,gc_onset_s_max,gc_onset_last_part_s_mean,gc_onset_last_part_s_std,gc_onset_last_part_s_min,gc_onset_last_part_s_max,bw_pre_gc_MiBps_mean,bw_pre_gc_MiBps_std,bw_pre_gc_MiBps_min,bw_pre_gc_MiBps_max,bw_post_gc_MiBps_mean,bw_post_gc_MiBps_std,bw_post_gc_MiBps_min,bw_post_gc_MiBps_max,gc_cnt_mean,gc_cnt_std,gc_cnt_min,gc_cnt_max,ftl_host_pgs_mean,ftl_host_pgs_std,ftl_host_pgs_min,ftl_host_pgs_max,ftl_gc_pgs_mean,ftl_gc_pgs_std,ftl_gc_pgs_min,ftl_gc_pgs_max,waf_gc_mean,waf_gc_std,waf_gc_min,waf_gc_max,waf_total_mean,waf_total_std,waf_total_min,waf_total_max
wbuffix,4k,8k,3,437.017578,1.222694,435.708984,438.130859,55938.317346,156.481239,55770.834375,56080.782497,25.610087,0.072246,25.533691,25.677307,2.283752,0.006442,2.276940,2.289746,570.842257,1.607327,569.382809,572.564961,120.320000,0.000000,120.320000,120.320000,16580.608000,0.000000,16580.608000,16580.608000,17782.101333,151.348909,17694.720000,17956.864000,571.830348,1.598979,570.377012,573.543219,0.988091,0.008600,0.978258,0.994203,60.008333,0.005033,60.003000,60.013000,1285.576709,0.445488,1285.062305,1285.834521,330.075741,4.590655,325.344287,334.511279,0.000000,0.000000,0,0,0.000000,0.000000,0,0,3354977,9449.460672,3344978,3363759,1788.333333,24.826062,1774,1817,8.004264,0.000050,8.004229,8.004321,5.738720,0.001370,5.737141,5.739599,5.757798,0.001177,5.756448,5.758605,2211.022254,0.000820,2211.021307,2211.022727,258.085006,1.353081,256.648393,259.335230,9359.333333,62.268237,9294,9418,6713531,18938.906973,6693504,6731152,15575134,108790.159481,15461194,15677914,3.319944,0.009667,3.309880,3.329158,3.319944,0.009667,3.309880,3.329158
wbuffix,4k,64k,3,486.317057,0.025095,486.293945,486.343750,7781.083382,0.406614,7780.706870,7781.514566,28.500244,0.002438,28.498657,28.503052,2.541479,0.000217,2.541337,2.541729,4109.675455,0.188013,4109.470216,4109.839365,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4112.268849,0.191108,4112.067183,4112.447274,2.593394,0.016592,2.575307,2.607909,60.010667,0.006506,60.004000,60.017000,1293.671208,0.003608,1293.667041,1293.673291,254.473958,0.135306,254.386230,254.629785,0.000000,0.000000,0,0,0.000000,0.000000,0,0,466947.666667,40.278199,466921,466994,0.333333,0.577350,0,1,64.000046,0.000079,64.000000,64.000137,5.692898,0.000167,5.692765,5.693086,5.693087,0.000165,5.692956,5.693272,2217.879469,0.006561,2217.871893,2217.883256,311.690122,0.048916,311.657890,311.746407,11345.333333,2.309401,11344,11348,7471168,639.199499,7470752,7471904,18884208,3866.144333,18881936,18888672,3.527611,0.000303,3.527415,3.527960,3.527611,0.000303,3.527415,3.527960
wbuffix,16k,8k,3,217.302734,0.143086,217.187500,217.462891,27814.790054,18.304796,27800.036660,27835.274709,12.734581,0.008248,12.728180,12.743889,1.135593,0.000736,1.135022,1.136423,1149.156674,0.769074,1148.294872,1149.773176,248.832000,0.000000,248.832000,248.832000,16536.917333,75.674454,16449.536000,16580.608000,17694.720000,0.000000,17694.720000,17694.720000,1150.215635,0.755999,1149.368839,1150.822708,1.058961,0.013137,1.049532,1.073967,60.009333,0.001528,60.008000,60.011000,736.204427,0.244699,735.921875,736.346484,80.895036,0.096266,80.785034,80.963892,0.000000,0.000000,0,0,0.000000,0.000000,0,0,1668829,1085.590316,1668020,1670063,317.666667,38.370996,288,361,8.001523,0.000184,8.001381,8.001731,5.904959,0.000132,5.904839,5.905100,5.972500,0.000118,5.972377,5.972613,1072.020360,0.022564,1071.994318,1072.034091,131.089082,0.154942,130.966134,131.263116,8087.333333,16.653328,8074,8106,1668989,1079.137310,1668164,1670210,3252472,7441.058952,3246459,3260794,2.948767,0.003200,2.946127,2.952326,5.896975,0.006389,5.891745,5.904097
wbuffix,16k,64k,3,486.400716,0.104858,486.280273,486.471680,7782.422279,1.673750,7780.499592,7783.553607,28.503723,0.005981,28.497314,28.509155,2.541789,0.000533,2.541217,2.542273,4108.970876,0.839212,4108.400097,4109.934451,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4111.558996,0.885180,4110.984836,4112.578399,2.588120,0.054218,2.535672,2.643948,60.007667,0.006110,60.001000,60.013000,1293.673226,0.000113,1293.673096,1293.673291,254.662915,0.282023,254.364087,254.924414,0.000000,0.000000,0,0,0.000000,0.000000,0,0,467004.333333,97.449132,466900,467093,0.666667,0.577350,0,1,64.000091,0.000079,64.000000,64.000137,5.692972,0.000244,5.692717,5.693203,5.693092,0.000245,5.692835,5.693323,2217.883138,0.000205,2217.882901,2217.883256,311.759398,0.107376,311.644603,311.857368,11346.666667,2.309401,11344,11348,1868020,391.938771,1867600,1868376,4721493,781.018139,4720596,4722020,3.527539,0.000251,3.527256,3.527734,3.527539,0.000251,3.527256,3.527734
wbuffix,32k,8k,3,131.948893,0.159704,131.824219,132.128906,16889.536804,20.417234,16873.604213,16912.552280,7.732147,0.010148,7.724380,7.743629,0.689506,0.000905,0.688813,0.690530,1893.333950,2.290181,1890.755613,1895.132102,561.152000,0.000000,561.152000,561.152000,15051.434667,75.674454,15007.744000,15138.816000,16012.629333,75.674454,15925.248000,16056.320000,1894.410432,2.293823,1891.824242,1896.198845,1.076482,0.015265,1.066743,1.094076,60.005667,0.006351,60.002000,60.013000,377.150260,0.087068,377.098437,377.250781,60.500887,0.555798,59.910327,61.013745,0.000000,0.000000,0,0,0.000000,0.000000,0,0,1013468,1330.318132,1012450,1014973,0.333333,0.577350,0,1,8.000003,0.000005,8.000000,8.000008,6.066794,0.000251,6.066635,6.067083,6.121820,0.000235,6.121649,6.122088,512.568142,0.001504,512.566406,512.569010,89.673641,0.192324,89.525843,89.891086,7353.000000,29.546573,7329,7386,1013468,1330.318132,1012450,1014973,1259304,6247.714462,1254180,1266264,2.242566,0.004536,2.238757,2.247584,8.970259,0.018145,8.955030,8.990336
wbuffix,32k,64k,3,447.136393,0.026463,447.111328,447.164062,7154.188440,0.418702,7153.791035,7154.625602,26.202332,0.000000,26.202332,26.202332,2.336565,0.000000,2.336565,2.336565,4470.024749,0.220549,4469.785987,4470.220853,978.944000,0.000000,978.944000,978.944000,19005.440000,0.000000,19005.440000,19005.440000,19617.109333,151.348909,19529.728000,19791.872000,4472.628224,0.235450,4472.381158,4472.850020,2.603474,0.022709,2.586085,2.629167,60.006667,0.003512,60.003000,60.010000,1286.820329,0.003077,1286.817871,1286.823779,319.961410,0.134527,319.806128,320.042676,0.000000,0.000000,0,0,0.000000,0.000000,0,0,429298.666667,0.577350,429298,429299,0.333333,0.577350,0,1,64.000050,0.000086,64.000000,64.000149,5.972580,0.000149,5.972408,5.972674,5.994979,0.000157,5.994798,5.995078,2124.233931,0.030172,2124.202326,2124.262429,277.956879,0.003354,277.953609,277.960310,9562.000000,0.000000,9562,9562,858598.000000,0.000000,858598,858598,1979380,0.000000,1979380,1979380,3.305363,0.000000,3.305363,3.305363,3.305363,0.000000,3.305363,3.305363
```

### 11.4.6 파티션별 GC 로그 (회차마다: 첫 GC 줄의 fio 시작 기준 시각·내용, rmmod 통계)
```
[wbuffix map4k bs8k r1]
  +5.737s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.737s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.756s first GC part=0 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.756s first GC part=1 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1682776 gc_pgs=3918415 gc_cnt=2354 free_lines=2
  stats part=1 host_pgs=1682776 gc_pgs=3918415 gc_cnt=2354 free_lines=2
  stats part=2 host_pgs=1682800 gc_pgs=3920542 gc_cnt=2355 free_lines=2
  stats part=3 host_pgs=1682800 gc_pgs=3920542 gc_cnt=2355 free_lines=2
  (kernel) [89413.899329] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89413.966343] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs8k r2]
  +5.740s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.740s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.759s first GC part=0 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  +5.759s first GC part=1 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1678894 gc_pgs=3891573 gc_cnt=2339 free_lines=2
  stats part=1 host_pgs=1678894 gc_pgs=3891573 gc_cnt=2339 free_lines=2
  stats part=2 host_pgs=1679074 gc_pgs=3901574 gc_cnt=2344 free_lines=2
  stats part=3 host_pgs=1679074 gc_pgs=3901574 gc_cnt=2344 free_lines=2
  (kernel) [89836.064292] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89836.132268] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs8k r3]
  +5.739s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.739s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.758s first GC part=0 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.758s first GC part=1 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1673299 gc_pgs=3862245 gc_cnt=2322 free_lines=2
  stats part=1 host_pgs=1673299 gc_pgs=3862245 gc_cnt=2322 free_lines=2
  stats part=2 host_pgs=1673453 gc_pgs=3868352 gc_cnt=2325 free_lines=2
  stats part=3 host_pgs=1673453 gc_pgs=3868352 gc_cnt=2325 free_lines=2
  (kernel) [90258.311809] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90258.378770] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r1]
  +5.693s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  (kernel) [89484.320073] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89484.387095] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r2]
  +5.693s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  (kernel) [89906.491184] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89906.558199] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r3]
  +5.693s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  (kernel) [90328.740782] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90328.808051] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r1]
  +5.905s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.923s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.923s first GC part=3 victim line=10 vpc=178 ipc=334 free_lines=2 host_pgs=194560
  +5.973s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=417240 gc_pgs=812204 gc_cnt=2020 free_lines=2
  stats part=1 host_pgs=417395 gc_pgs=813557 gc_cnt=2023 free_lines=2
  stats part=2 host_pgs=417152 gc_pgs=814843 gc_cnt=2025 free_lines=2
  stats part=3 host_pgs=416805 gc_pgs=809560 gc_cnt=2014 free_lines=1
  (kernel) [89554.689889] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89554.717175] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r2]
  +5.905s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.923s first GC part=3 victim line=10 vpc=178 ipc=334 free_lines=2 host_pgs=194560
  +5.972s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=417657 gc_pgs=814854 gc_cnt=2026 free_lines=2
  stats part=1 host_pgs=417802 gc_pgs=815713 gc_cnt=2028 free_lines=1
  stats part=2 host_pgs=417541 gc_pgs=818546 gc_cnt=2033 free_lines=2
  stats part=3 host_pgs=417210 gc_pgs=811681 gc_cnt=2019 free_lines=2
  (kernel) [89976.901090] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89976.928781] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r3]
  +5.905s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.922s first GC part=3 victim line=10 vpc=179 ipc=333 free_lines=2 host_pgs=194560
  +5.973s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=417140 gc_pgs=810776 gc_cnt=2017 free_lines=2
  stats part=1 host_pgs=417291 gc_pgs=812127 gc_cnt=2020 free_lines=1
  stats part=2 host_pgs=417030 gc_pgs=813404 gc_cnt=2022 free_lines=2
  stats part=3 host_pgs=416703 gc_pgs=810152 gc_cnt=2015 free_lines=2
  (kernel) [90399.131737] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90399.159114] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r1]
  +5.693s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  (kernel) [89625.028679] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89625.056273] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r2]
  +5.693s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  (kernel) [90047.249993] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90047.277561] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r3]
  +5.693s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  (kernel) [90469.466695] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90469.494276] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs8k r1]
  +6.067s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.093s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +6.109s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +6.122s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=252948 gc_pgs=312364 gc_cnt=1827 free_lines=1
  stats part=1 host_pgs=253752 gc_pgs=319749 gc_cnt=1859 free_lines=1
  stats part=2 host_pgs=252896 gc_pgs=314194 gc_cnt=1834 free_lines=2
  stats part=3 host_pgs=253384 gc_pgs=311161 gc_cnt=1824 free_lines=2
  (kernel) [89695.351526] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89695.372009] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs8k r2]
  +6.067s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.093s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +6.109s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +6.122s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=252816 gc_pgs=311976 gc_cnt=1825 free_lines=2
  stats part=1 host_pgs=253630 gc_pgs=318861 gc_cnt=1855 free_lines=2
  stats part=2 host_pgs=252755 gc_pgs=313846 gc_cnt=1832 free_lines=2
  stats part=3 host_pgs=253249 gc_pgs=309497 gc_cnt=1817 free_lines=2
  (kernel) [90117.580917] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90117.601629] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs8k r3]
  +6.067s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.092s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +6.108s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +6.122s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=253418 gc_pgs=314714 gc_cnt=1838 free_lines=2
  stats part=1 host_pgs=254255 gc_pgs=322572 gc_cnt=1872 free_lines=1
  stats part=2 host_pgs=253427 gc_pgs=317001 gc_cnt=1847 free_lines=2
  stats part=3 host_pgs=253873 gc_pgs=311977 gc_cnt=1829 free_lines=2
  (kernel) [90539.830679] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90539.851141] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs64k r1]
  +5.972s first GC part=0 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.972s first GC part=1 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.995s first GC part=2 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +5.995s first GC part=3 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=1 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=2 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  stats part=3 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  (kernel) [89765.679385] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89765.699784] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs64k r2]
  +5.973s first GC part=0 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.973s first GC part=1 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.995s first GC part=2 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +5.995s first GC part=3 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=1 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=2 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  stats part=3 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  (kernel) [90187.918886] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90187.939349] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs64k r3]
  +5.973s first GC part=0 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.973s first GC part=1 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.995s first GC part=2 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +5.995s first GC part=3 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=1 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=2 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  stats part=3 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  (kernel) [90610.168654] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90610.189022] NVMeVirt: Virtual NVMe device closed
```

### 11.4.7 1 초 평균 대역폭 시계열 (MiB/s, t=1..60 s, fio_bw.1.log 의 0.5 s 값 두 개 평균)
형식: variant map bs rep | gc_onset_s | 값 60개 (공백 구분)
```
wbuffix 4k 8k r1 | 5.737 | 2217 2212 2212 2215 2210 1183 126 142 156 178 177 179 238 192 180 178 225 192 218 203 178 221 162 157 210 207 178 248 190 219 289 277 209 227 259 362 275 332 257 398 400 338 412 712 646 1138 689 135 152 162 194 193 234 204 197 184 200 220 223 198
wbuffix 4k 8k r2 | 5.740 | 2217 2212 2212 2215 2211 1183 128 142 161 179 190 200 229 175 209 209 179 210 238 211 177 184 259 246 242 226 185 180 258 225 221 224 217 218 269 287 342 254 315 293 303 333 435 605 739 1394 252 134 146 171 185 209 188 171 191 207 190 189 227 239
wbuffix 4k 8k r3 | 5.739 | 2217 2212 2212 2215 2211 1182 128 140 159 183 186 185 229 191 189 184 211 208 157 182 230 211 256 231 180 226 199 176 181 229 186 194 220 208 234 275 293 308 311 330 301 509 499 474 552 790 1140 122 140 158 175 194 177 225 199 190 180 209 232 223
wbuffix 4k 64k r1 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 214 236 221 209 221 225 238 237 251 256 269 265 281 290 303 307 319 351 364 384 413 443 499 547 649 833 1437 590 147 161 178 198 217 233 214 212 222 229 242 242 252 253 265 272 279 292 299 313 331 344
wbuffix 4k 64k r2 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 216 234 221 211 220 225 238 237 251 256 269 266 280 290 303 310 322 345 364 384 414 449 493 547 655 826 1444 582 147 161 178 198 221 222 222 212 222 231 241 242 252 258 260 273 284 287 299 314 329 344
wbuffix 4k 64k r3 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 214 236 221 213 218 225 238 237 251 256 269 265 280 290 303 310 322 345 364 384 413 448 494 547 654 828 1444 583 147 161 178 198 221 229 214 213 222 233 238 246 248 258 260 273 284 291 298 314 326 349
wbuffix 16k 8k r1 | 5.905 | 1071 1071 1076 1075 1071 834 324 286 283 267 247 230 198 204 189 178 184 156 150 149 146 130 123 126 121 120 117 112 108 112 102 100 110 102 103 87 94 87 93 82 91 77 77 79 77 80 81 83 82 82 79 81 78 78 85 79 82 85 80 79
wbuffix 16k 8k r2 | 5.905 | 1071 1071 1076 1075 1072 834 325 289 285 266 246 225 201 200 193 176 186 157 150 143 146 130 128 124 124 114 122 110 113 116 98 107 97 100 98 98 97 95 87 90 84 83 83 83 77 87 78 78 79 77 79 79 84 82 80 80 84 79 82 80
wbuffix 16k 8k r3 | 5.905 | 1071 1071 1076 1076 1071 834 324 290 286 266 244 226 201 202 191 178 184 157 150 144 143 128 129 129 124 112 115 116 115 99 111 106 104 101 91 97 90 90 90 87 83 83 83 80 79 85 79 79 76 82 81 82 82 81 80 81 80 84 82 77
wbuffix 16k 64k r1 | 5.693 | 2235 2232 2233 2233 2233 1103 144 156 174 193 216 234 221 213 217 225 238 237 251 258 267 270 276 290 303 310 322 345 364 387 410 449 493 551 657 821 1451 576 147 161 179 197 221 229 216 211 221 230 241 241 252 254 268 274 274 292 303 311 329 345
wbuffix 16k 64k r2 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 218 231 221 214 217 225 237 237 251 258 266 270 276 290 303 310 322 345 364 388 409 449 493 548 660 821 1450 577 147 161 178 198 221 229 215 211 222 233 238 247 246 258 266 268 284 294 300 309 329 349
wbuffix 16k 64k r3 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 218 231 221 214 217 228 234 241 246 261 264 270 280 286 303 310 322 345 364 392 406 449 493 558 651 826 1455 566 147 161 181 199 217 234 213 208 226 229 241 243 250 253 269 269 281 295 300 316 331 343
wbuffix 32k 8k r1 | 6.067 | 521 520 519 521 521 472 182 183 178 153 164 162 155 132 123 125 118 107 112 111 102 102 96 92 91 88 87 86 87 80 80 79 78 74 73 71 70 64 66 68 64 66 63 66 62 59 60 61 59 60 63 60 60 59 56 56 55 56 57 58
wbuffix 32k 8k r2 | 6.067 | 521 520 519 521 522 472 181 181 178 155 164 162 155 131 121 128 117 109 107 107 104 101 96 93 89 86 89 84 85 78 79 75 76 70 71 69 72 70 72 67 68 62 68 65 64 63 61 61 62 59 62 61 58 57 59 56 58 57 58 56
wbuffix 32k 8k r3 | 6.067 | 521 520 519 521 522 472 181 182 179 154 167 161 157 131 121 129 117 109 110 109 103 100 95 93 89 86 90 84 82 79 76 76 75 72 74 75 69 68 71 67 67 66 65 63 65 66 60 61 63 63 65 62 58 57 57 55 56 56 56 58
wbuffix 32k 64k r1 | 5.972 | 2130 2125 2115 2124 2120 1608 147 150 171 178 190 176 207 200 186 198 200 220 208 219 221 218 235 261 210 260 229 260 240 272 269 280 272 264 281 294 319 348 345 484 544 613 894 1236 141 149 166 165 194 208 194 211 187 208 203 213 220 214 220 216
wbuffix 32k 64k r2 | 5.973 | 2130 2125 2115 2124 2120 1609 147 150 171 178 190 176 207 200 186 198 198 219 210 219 221 216 232 265 210 259 230 261 240 270 271 278 274 262 282 294 320 346 338 489 548 607 888 1247 141 150 164 167 194 208 192 211 187 208 204 212 221 212 222 217
wbuffix 32k 64k r3 | 5.973 | 2130 2125 2115 2124 2120 1609 147 150 167 182 190 176 207 200 186 198 197 220 214 215 221 216 232 266 210 256 232 261 241 270 271 277 274 264 281 294 319 346 342 485 548 613 889 1240 142 149 166 165 194 208 194 211 188 207 203 217 216 214 220 216
```

### 11.4.8 실험 전후 환경 차이 (env_before vs env_after_* 의 마지막 스냅샷; 날짜·부하·여유 메모리 줄 제외)
- env_after_wbuffix:
  - 08_nvmevirt_git.txt:
    `+ M EXPERIMENT_LOG_FOR_CLAUDE.md`
    `+ M exp/build_modules.sh`
    `+ M exp/make_gallery.py`
    `+ M exp/report/findings_seq_ko.txt`
    `+ M exp/report/make_report.py`
    `+ M exp/run_all_seq.sh`

### 11.4.9 run_all 로그 끝 40 줄 (원본 로그, 시각은 KST 로 변환)
```
[2026-10-08 22:12:59 KST] === [2/18] variant=wbuffix cache=nodrop map=4k bs=64k rep=1 ===
    -> 486.3 MiB/s, 7781 IOPS, clat mean 4109.8 us
[2026-10-08 22:14:09 KST] === [3/18] variant=wbuffix cache=nodrop map=16k bs=8k rep=1 ===
    -> 217.3 MiB/s, 27809 IOPS, clat mean 1149.4 us
[2026-10-08 22:15:20 KST] === [4/18] variant=wbuffix cache=nodrop map=16k bs=64k rep=1 ===
    -> 486.3 MiB/s, 7780 IOPS, clat mean 4109.9 us
[2026-10-08 22:16:30 KST] === [5/18] variant=wbuffix cache=nodrop map=32k bs=8k rep=1 ===
    -> 131.9 MiB/s, 16882 IOPS, clat mean 1894.1 us
[2026-10-08 22:17:40 KST] === [6/18] variant=wbuffix cache=nodrop map=32k bs=64k rep=1 ===
    -> 447.1 MiB/s, 7154 IOPS, clat mean 4470.1 us
[2026-10-08 22:18:51 KST] === [7/18] variant=wbuffix cache=nodrop map=4k bs=8k rep=2 ===
    -> 437.2 MiB/s, 55963 IOPS, clat mean 570.6 us
[2026-10-08 22:20:01 KST] === [8/18] variant=wbuffix cache=nodrop map=4k bs=64k rep=2 ===
    -> 486.3 MiB/s, 7782 IOPS, clat mean 4109.5 us
[2026-10-08 22:21:11 KST] === [9/18] variant=wbuffix cache=nodrop map=16k bs=8k rep=2 ===
    -> 217.5 MiB/s, 27835 IOPS, clat mean 1148.3 us
[2026-10-08 22:22:22 KST] === [10/18] variant=wbuffix cache=nodrop map=16k bs=64k rep=2 ===
    -> 486.5 MiB/s, 7784 IOPS, clat mean 4108.4 us
[2026-10-08 22:23:32 KST] === [11/18] variant=wbuffix cache=nodrop map=32k bs=8k rep=2 ===
    -> 131.8 MiB/s, 16874 IOPS, clat mean 1895.1 us
[2026-10-08 22:24:42 KST] === [12/18] variant=wbuffix cache=nodrop map=32k bs=64k rep=2 ===
    -> 447.1 MiB/s, 7154 IOPS, clat mean 4470.2 us
[2026-10-08 22:25:53 KST] === [13/18] variant=wbuffix cache=nodrop map=4k bs=8k rep=3 ===
    -> 435.7 MiB/s, 55771 IOPS, clat mean 572.6 us
[2026-10-08 22:27:03 KST] === [14/18] variant=wbuffix cache=nodrop map=4k bs=64k rep=3 ===
    -> 486.3 MiB/s, 7781 IOPS, clat mean 4109.7 us
[2026-10-08 22:28:14 KST] === [15/18] variant=wbuffix cache=nodrop map=16k bs=8k rep=3 ===
    -> 217.2 MiB/s, 27800 IOPS, clat mean 1149.8 us
[2026-10-08 22:29:24 KST] === [16/18] variant=wbuffix cache=nodrop map=16k bs=64k rep=3 ===
    -> 486.5 MiB/s, 7783 IOPS, clat mean 4108.6 us
[2026-10-08 22:30:34 KST] === [17/18] variant=wbuffix cache=nodrop map=32k bs=8k rep=3 ===
    -> 132.1 MiB/s, 16913 IOPS, clat mean 1890.8 us
[2026-10-08 22:31:45 KST] === [18/18] variant=wbuffix cache=nodrop map=32k bs=64k rep=3 ===
    -> 447.2 MiB/s, 7155 IOPS, clat mean 4469.8 us
environment snapshot -> /home/dccearth/jsw/nvmevirt/exp/results/randbs_20261008/env_after_wbuffix
[2026-10-08 22:32:55 KST] finished: /home/dccearth/jsw/nvmevirt/exp/results/randbs_20261008/wbuffix
18 runs, 0 failed -> /home/dccearth/jsw/nvmevirt/exp/results/randbs_20261008/analysis
/home/dccearth/jsw/nvmevirt/exp/results/rand3x5_20261008: 45 runs linked into wbuffix/
45 runs, 0 failed -> /home/dccearth/jsw/nvmevirt/exp/results/rand3x5_20261008/analysis
RBS-ALL-DONE
```

## 11.5 rand3x5_20261008  (묶음 경로 repo/exp/results/rand3x5_20261008/)

### 11.5.1 회차 목록
- wbuffix: 완료 회차 45 (DONE 있음). run.log 첫 시각 NA, 마지막 시각 NA. chmodel 오류 줄 합계 0. chmodel>0 회차 0. kernel_warn>0 회차 0.
  - 미완료/없음 0: -

### 11.5.2 조합별 행렬 (행 = 매핑 단위, 열 = fio bs). 칸 = mean ± std [min..max], n = 그 조합의 완료 회차 수(보통 3)
#### rand3x5_20261008 · wbuffix · bw_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 415.997 ± 1.559 [414.744..417.743] | 437.018 ± 1.223 [435.709..438.131] | 480.960 ± 0.088 [480.858..481.021] | 482.267 ± 0.176 [482.105..482.454] | 486.317 ± 0.025 [486.294..486.344] |
| 16K | 129.721 ± 0.035 [129.697..129.761] | 217.303 ± 0.143 [217.188..217.463] | 420.388 ± 1.287 [419.193..421.751] | 441.581 ± 1.301 [440.150..442.691] | 486.401 ± 0.105 [486.280..486.472] |
| 32K | 68.288 ± 0.048 [68.236..68.331] | 131.949 ± 0.160 [131.824..132.129] | 219.565 ± 0.381 [219.138..219.869] | 424.649 ± 0.173 [424.519..424.845] | 447.136 ± 0.026 [447.111..447.164] |

#### rand3x5_20261008 · wbuffix · iops
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 106495.339 ± 399.194 [106174.680..106942.443] | 55938.317 ± 156.481 [55770.834..56080.782] | 30781.454 ± 5.676 [30774.953..30785.423] | 15432.564 ± 5.623 [15427.381..15438.542] | 7781.083 ± 0.407 [7780.707..7781.515] |
| 16K | 33208.731 ± 8.874 [33202.647..33218.913] | 27814.790 ± 18.305 [27800.037..27835.275] | 26904.846 ± 82.372 [26828.406..26992.085] | 14130.611 ± 41.620 [14084.818..14166.136] | 7782.422 ± 1.674 [7780.500..7783.554] |
| 32K | 17481.884 ± 12.241 [17468.633..17492.769] | 16889.537 ± 20.417 [16873.604..16912.552] | 14052.222 ± 24.404 [14024.843..14071.687] | 13588.795 ± 5.522 [13584.624..13595.057] | 7154.188 ± 0.419 [7153.791..7154.626] |

#### rand3x5_20261008 · wbuffix · clat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 299.451 ± 1.126 [298.191..300.360] | 570.842 ± 1.607 [569.383..572.565] | 1038.121 ± 0.204 [1037.985..1038.356] | 2071.614 ± 0.780 [2070.787..2072.336] | 4109.675 ± 0.188 [4109.470..4109.839] |
| 16K | 962.520 ± 0.259 [962.223..962.699] | 1149.157 ± 0.769 [1148.295..1149.773] | 1187.876 ± 3.628 [1184.053..1191.271] | 2262.688 ± 6.689 [2256.993..2270.054] | 4108.971 ± 0.839 [4108.400..4109.934] |
| 32K | 1829.245 ± 1.279 [1828.107..1830.630] | 1893.334 ± 2.290 [1890.756..1895.132] | 2275.722 ± 3.928 [2272.597..2280.132] | 2352.950 ± 0.954 [2351.873..2353.692] | 4470.025 ± 0.221 [4469.786..4470.221] |

#### rand3x5_20261008 · wbuffix · clat_p50_us
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 69.803 ± 0.591 [69.120..70.144] | 120.320 ± 0.000 [120.320..120.320] | 222.208 ± 0.000 [222.208..222.208] | 444.416 ± 0.000 [444.416..444.416] | 897.024 ± 0.000 [897.024..897.024] |
| 16K | 256.341 ± 1.182 [254.976..257.024] | 248.832 ± 0.000 [248.832..248.832] | 246.784 ± 0.000 [246.784..246.784] | 464.896 ± 0.000 [464.896..464.896] | 897.024 ± 0.000 [897.024..897.024] |
| 32K | 572.075 ± 4.730 [569.344..577.536] | 561.152 ± 0.000 [561.152..561.152] | 536.576 ± 0.000 [536.576..536.576] | 522.240 ± 0.000 [522.240..522.240] | 978.944 ± 0.000 [978.944..978.944] |

#### rand3x5_20261008 · wbuffix · clat_p99_us
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 13347.499 ± 75.674 [13303.808..13434.880] | 16580.608 ± 0.000 [16580.608..16580.608] | 17694.720 ± 0.000 [17694.720..17694.720] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] |
| 16K | 14046.549 ± 75.674 [13959.168..14090.240] | 16536.917 ± 75.674 [16449.536..16580.608] | 16842.752 ± 113.512 [16711.680..16908.288] | 18219.008 ± 0.000 [18219.008..18219.008] | 19005.440 ± 0.000 [19005.440..19005.440] |
| 32K | 14483.456 ± 0.000 [14483.456..14483.456] | 15051.435 ± 75.674 [15007.744..15138.816] | 17607.339 ± 151.349 [17432.576..17694.720] | 17694.720 ± 0.000 [17694.720..17694.720] | 19005.440 ± 0.000 [19005.440..19005.440] |

#### rand3x5_20261008 · wbuffix · clat_p999_us
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 16995.669 ± 151.349 [16908.288..17170.432] | 17782.101 ± 151.349 [17694.720..17956.864] | 18481.152 ± 0.000 [18481.152..18481.152] | 18743.296 ± 0.000 [18743.296..18743.296] | 19529.728 ± 0.000 [19529.728..19529.728] |
| 16K | 15313.579 ± 75.674 [15269.888..15400.960] | 17694.720 ± 0.000 [17694.720..17694.720] | 17956.864 ± 0.000 [17956.864..17956.864] | 18743.296 ± 0.000 [18743.296..18743.296] | 19529.728 ± 0.000 [19529.728..19529.728] |
| 32K | 15444.651 ± 75.674 [15400.960..15532.032] | 16012.629 ± 75.674 [15925.248..16056.320] | 17956.864 ± 0.000 [17956.864..17956.864] | 18219.008 ± 0.000 [18219.008..18219.008] | 19617.109 ± 151.349 [19529.728..19791.872] |

#### rand3x5_20261008 · wbuffix · lat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 300.298 ± 1.123 [299.041..301.202] | 571.830 ± 1.599 [570.377..573.543] | 1039.342 ± 0.194 [1039.208..1039.565] | 2073.270 ± 0.759 [2072.463..2073.970] | 4112.269 ± 0.191 [4112.067..4112.447] |
| 16K | 963.389 ± 0.260 [963.090..963.567] | 1150.216 ± 0.756 [1149.369..1150.823] | 1189.131 ± 3.645 [1185.275..1192.520] | 2264.343 ± 6.667 [2258.667..2271.686] | 4111.559 ± 0.885 [4110.985..4112.578] |
| 32K | 1830.215 ± 1.276 [1829.076..1831.593] | 1894.410 ± 2.294 [1891.824..1896.199] | 2276.968 ± 3.939 [2273.827..2281.388] | 2354.622 ± 0.953 [2353.546..2355.361] | 4472.628 ± 0.235 [4472.381..4472.850] |

#### rand3x5_20261008 · wbuffix · slat_mean_us
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 0.848 ± 0.005 [0.842..0.851] | 0.988 ± 0.009 [0.978..0.994] | 1.221 ± 0.012 [1.208..1.232] | 1.656 ± 0.021 [1.635..1.676] | 2.593 ± 0.017 [2.575..2.608] |
| 16K | 0.869 ± 0.004 [0.867..0.874] | 1.059 ± 0.013 [1.050..1.074] | 1.255 ± 0.037 [1.222..1.295] | 1.655 ± 0.022 [1.632..1.674] | 2.588 ± 0.054 [2.536..2.644] |
| 32K | 0.970 ± 0.007 [0.964..0.978] | 1.076 ± 0.015 [1.067..1.094] | 1.246 ± 0.014 [1.230..1.256] | 1.672 ± 0.002 [1.670..1.673] | 2.603 ± 0.023 [2.586..2.629] |

#### rand3x5_20261008 · wbuffix · bw_first10s_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 1272.909 ± 1.221 [1271.960..1274.286] | 1285.577 ± 0.445 [1285.062..1285.835] | 1288.244 ± 0.341 [1287.867..1288.533] | 1290.717 ± 0.203 [1290.562..1290.947] | 1293.671 ± 0.004 [1293.667..1293.673] |
| 16K | 378.912 ± 0.234 [378.643..379.058] | 736.204 ± 0.245 [735.922..736.346] | 1280.454 ± 0.119 [1280.323..1280.556] | 1285.856 ± 0.008 [1285.850..1285.865] | 1293.673 ± 0.000 [1293.673..1293.673] |
| 32K | 189.793 ± 0.123 [189.655..189.894] | 377.150 ± 0.087 [377.098..377.251] | 741.172 ± 0.006 [741.166..741.178] | 1278.010 ± 0.243 [1277.778..1278.263] | 1286.820 ± 0.003 [1286.818..1286.824] |

#### rand3x5_20261008 · wbuffix · bw_last20s_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 321.959 ± 1.628 [320.716..323.802] | 330.076 ± 4.591 [325.344..334.511] | 244.833 ± 0.260 [244.565..245.084] | 247.153 ± 0.359 [246.785..247.503] | 254.474 ± 0.135 [254.386..254.630] |
| 16K | 58.226 ± 0.105 [58.143..58.343] | 80.895 ± 0.096 [80.785..80.964] | 323.407 ± 1.170 [322.718..324.757] | 321.431 ± 1.819 [319.397..322.904] | 254.663 ± 0.282 [254.364..254.924] |
| 32K | 32.631 ± 0.266 [32.324..32.785] | 60.501 ± 0.556 [59.910..61.014] | 82.161 ± 0.396 [81.830..82.599] | 322.791 ± 1.322 [321.330..323.905] | 319.961 ± 0.135 [319.806..320.043] |

#### rand3x5_20261008 · wbuffix · gc_onset_s
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 6.317 ± 0.035 [6.277..6.342] | 5.739 ± 0.001 [5.737..5.740] | 5.694 ± 0.002 [5.693..5.696] | 5.693 ± 0.000 [5.693..5.693] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.913 ± 0.002 [5.911..5.915] | 5.905 ± 0.000 [5.905..5.905] | 5.921 ± 0.000 [5.921..5.921] | 5.844 ± 0.001 [5.843..5.846] | 5.693 ± 0.000 [5.693..5.693] |
| 32K | 6.061 ± 0.000 [6.061..6.061] | 6.067 ± 0.000 [6.067..6.067] | 6.064 ± 0.000 [6.064..6.064] | 6.096 ± 0.000 [6.096..6.096] | 5.973 ± 0.000 [5.972..5.973] |

#### rand3x5_20261008 · wbuffix · gc_onset_last_part_s
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 6.338 ± 0.035 [6.298..6.362] | 5.758 ± 0.001 [5.756..5.759] | 5.694 ± 0.002 [5.693..5.697] | 5.693 ± 0.000 [5.693..5.694] | 5.693 ± 0.000 [5.693..5.693] |
| 16K | 5.943 ± 0.002 [5.941..5.945] | 5.972 ± 0.000 [5.972..5.973] | 5.943 ± 0.000 [5.943..5.943] | 5.866 ± 0.001 [5.865..5.867] | 5.693 ± 0.000 [5.693..5.693] |
| 32K | 6.144 ± 0.000 [6.144..6.144] | 6.122 ± 0.000 [6.122..6.122] | 6.101 ± 0.000 [6.101..6.101] | 6.141 ± 0.000 [6.140..6.141] | 5.995 ± 0.000 [5.995..5.995] |

#### rand3x5_20261008 · wbuffix · bw_pre_gc_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 2001.359 ± 12.555 [1992.749..2015.765] | 2211.022 ± 0.001 [2211.021..2211.023] | 2217.592 ± 0.262 [2217.290..2217.750] | 2217.771 ± 0.003 [2217.767..2217.773] | 2217.879 ± 0.007 [2217.872..2217.883] |
| 16K | 535.595 ± 0.017 [535.576..535.609] | 1072.020 ± 0.023 [1071.994..1072.034] | 2143.200 ± 0.033 [2143.168..2143.233] | 2172.678 ± 0.558 [2172.034..2173.000] | 2217.883 ± 0.000 [2217.883..2217.883] |
| 32K | 256.082 ± 0.007 [256.074..256.089] | 512.568 ± 0.002 [512.566..512.569] | 1026.858 ± 0.016 [1026.844..1026.875] | 2032.771 ± 0.005 [2032.766..2032.776] | 2124.234 ± 0.030 [2124.202..2124.262] |

#### rand3x5_20261008 · wbuffix · bw_post_gc_MiBps
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 240.091 ± 2.885 [236.918..242.558] | 258.085 ± 1.353 [256.648..259.335] | 305.810 ± 0.086 [305.711..305.870] | 307.234 ± 0.180 [307.052..307.412] | 311.690 ± 0.049 [311.658..311.746] |
| 16K | 88.772 ± 0.036 [88.741..88.812] | 131.089 ± 0.155 [130.966..131.263] | 246.588 ± 1.450 [245.238..248.121] | 266.960 ± 1.475 [265.356..268.256] | 311.759 ± 0.107 [311.645..311.857] |
| 32K | 47.437 ± 0.054 [47.384..47.491] | 89.674 ± 0.192 [89.526..89.891] | 129.922 ± 0.412 [129.459..130.249] | 246.011 ± 0.174 [245.838..246.187] | 277.957 ± 0.003 [277.954..277.960] |

#### rand3x5_20261008 · wbuffix · gc_cnt
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 8204.667 ± 93.927 [8133..8311] | 9359.333 ± 62.268 [9294..9418] | 11270.667 ± 2.309 [11268..11272] | 11276.000 ± 0.000 [11276..11276] | 11345.333 ± 2.309 [11344..11348] |
| 16K | 7056.000 ± 4.583 [7052..7061] | 8087.333 ± 16.653 [8074..8106] | 8319.667 ± 74.969 [8250..8399] | 9463.333 ± 65.248 [9392..9520] | 11346.667 ± 2.309 [11344..11348] |
| 32K | 7222.667 ± 14.012 [7209..7237] | 7353.000 ± 29.547 [7329..7386] | 8289.667 ± 45.829 [8241..8332] | 8409.000 ± 10.149 [8398..8418] | 9562.000 ± 0.000 [9562..9562] |

#### rand3x5_20261008 · wbuffix · ftl_host_pgs
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 6390148 ± 24491.429 [6370587..6417616] | 6713531 ± 18938.907 [6693504..6731152] | 7388821 ± 1073.948 [7387712..7389856] | 7409112 ± 2433.933 [7406624..7411488] | 7471168 ± 639.199 [7470752..7471904] |
| 16K | 1992601 ± 505.547 [1992192..1993166] | 1668989 ± 1079.137 [1668164..1670210] | 1614479 ± 5060.688 [1609758..1619822] | 1695965 ± 4988.469 [1690488..1700248] | 1868020 ± 391.939 [1867600..1868376] |
| 32K | 1049105 ± 733.120 [1048380..1049846] | 1013468 ± 1330.318 [1012450..1014973] | 843318.667 ± 1426.180 [841716..844448] | 815404.667 ± 313.002 [815091..815717] | 858598.000 ± 0.000 [858598..858598] |

#### rand3x5_20261008 · wbuffix · ftl_gc_pgs
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 13533841 ± 167831.157 [13406435..13724008] | 15575134 ± 108790.159 [15461194..15677914] | 18814517 ± 4586.611 [18809364..18818152] | 18804544 ± 2463.636 [18802256..18807152] | 18884208 ± 3866.144 [18881936..18888672] |
| 16K | 2400837 ± 1819.679 [2399217..2402806] | 3252472 ± 7441.059 [3246459..3260794] | 3425415 ± 33300.381 [3394501..3460675] | 3929382 ± 28415.406 [3898342..3954112] | 4721493 ± 781.018 [4720596..4722020] |
| 32K | 1190282 ± 2836.155 [1187519..1193186] | 1259304 ± 6247.714 [1254180..1266264] | 1669245 ± 10323.704 [1658397..1678949] | 1727406 ± 2295.000 [1724901..1729407] | 1979380 ± 0.000 [1979380..1979380] |

#### rand3x5_20261008 · wbuffix · waf_gc
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 3.118 ± 0.018 [3.104..3.138] | 3.320 ± 0.010 [3.310..3.329] | 3.546 ± 0.001 [3.546..3.547] | 3.538 ± 0.001 [3.537..3.539] | 3.528 ± 0.000 [3.527..3.528] |
| 16K | 2.205 ± 0.001 [2.204..2.206] | 2.949 ± 0.003 [2.946..2.952] | 3.122 ± 0.014 [3.109..3.136] | 3.317 ± 0.010 [3.306..3.326] | 3.528 ± 0.000 [3.527..3.528] |
| 32K | 2.135 ± 0.002 [2.133..2.137] | 2.243 ± 0.005 [2.239..2.248] | 2.979 ± 0.009 [2.970..2.988] | 3.118 ± 0.002 [3.116..3.120] | 3.305 ± 0.000 [3.305..3.305] |

#### rand3x5_20261008 · wbuffix · waf_total
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 3.118 ± 0.018 [3.104..3.138] | 3.320 ± 0.010 [3.310..3.329] | 3.546 ± 0.001 [3.546..3.547] | 3.538 ± 0.001 [3.537..3.539] | 3.528 ± 0.000 [3.527..3.528] |
| 16K | 8.820 ± 0.002 [8.817..8.822] | 5.897 ± 0.006 [5.892..5.904] | 3.122 ± 0.014 [3.109..3.136] | 3.317 ± 0.010 [3.306..3.326] | 3.528 ± 0.000 [3.527..3.528] |
| 32K | 17.077 ± 0.015 [17.062..17.092] | 8.970 ± 0.018 [8.955..8.990] | 5.959 ± 0.018 [5.940..5.976] | 3.118 ± 0.002 [3.116..3.120] | 3.305 ± 0.000 [3.305..3.305] |

#### rand3x5_20261008 · wbuffix · written_GiB
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 24.376 ± 0.093 [24.302..24.481] | 25.610 ± 0.072 [25.534..25.677] | 28.186 ± 0.004 [28.182..28.190] | 28.264 ± 0.009 [28.254..28.273] | 28.500 ± 0.002 [28.499..28.503] |
| 16K | 7.601 ± 0.002 [7.600..7.603] | 12.735 ± 0.008 [12.728..12.744] | 24.635 ± 0.077 [24.563..24.717] | 25.878 ± 0.076 [25.795..25.944] | 28.504 ± 0.006 [28.497..28.509] |
| 32K | 4.002 ± 0.003 [3.999..4.005] | 7.732 ± 0.010 [7.724..7.744] | 12.868 ± 0.022 [12.844..12.885] | 24.884 ± 0.010 [24.875..24.894] | 26.202 ± 0.000 [26.202..26.202] |

#### rand3x5_20261008 · wbuffix · fill_ratio
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 2.174 ± 0.008 [2.167..2.183] | 2.284 ± 0.006 [2.277..2.290] | 2.513 ± 0.000 [2.513..2.514] | 2.520 ± 0.001 [2.520..2.521] | 2.541 ± 0.000 [2.541..2.542] |
| 16K | 0.678 ± 0.000 [0.678..0.678] | 1.136 ± 0.001 [1.135..1.136] | 2.197 ± 0.007 [2.190..2.204] | 2.308 ± 0.007 [2.300..2.314] | 2.542 ± 0.001 [2.541..2.542] |
| 32K | 0.357 ± 0.000 [0.357..0.357] | 0.690 ± 0.001 [0.689..0.691] | 1.148 ± 0.002 [1.145..1.149] | 2.219 ± 0.001 [2.218..2.220] | 2.337 ± 0.000 [2.337..2.337] |

#### rand3x5_20261008 · wbuffix · chmodel_msgs
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### rand3x5_20261008 · wbuffix · kernel_warn
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 16K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |
| 32K | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] | 0.000 ± 0.000 [0..0] |

#### rand3x5_20261008 · wbuffix · blk_wr_ios
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | NA | 3354977 ± 9449.461 [3344978..3363759] | NA | NA | 466947.667 ± 40.278 [466921..466994] |
| 16K | NA | 1668829 ± 1085.590 [1668020..1670063] | NA | NA | 467004.333 ± 97.449 [466900..467093] |
| 32K | NA | 1013468 ± 1330.318 [1012450..1014973] | NA | NA | 429298.667 ± 0.577 [429298..429299] |

#### rand3x5_20261008 · wbuffix · blk_wr_merges
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | NA | 1788.333 ± 24.826 [1774..1817] | NA | NA | 0.333 ± 0.577 [0..1] |
| 16K | NA | 317.667 ± 38.371 [288..361] | NA | NA | 0.667 ± 0.577 [0..1] |
| 32K | NA | 0.333 ± 0.577 [0..1] | NA | NA | 0.333 ± 0.577 [0..1] |

#### rand3x5_20261008 · wbuffix · blk_avg_req_KiB
| map\bs | 4K | 8K | 16K | 32K | 64K |
|---|---|---|---|---|---|
| 4K | NA | 8.004 ± 0.000 [8.004..8.004] | NA | NA | 64.000 ± 0.000 [64.000..64.000] |
| 16K | NA | 8.002 ± 0.000 [8.001..8.002] | NA | NA | 64.000 ± 0.000 [64.000..64.000] |
| 32K | NA | 8.000 ± 0.000 [8.000..8.000] | NA | NA | 64.000 ± 0.000 [64.000..64.000] |

### 11.5.4 회차별 전체 (analysis/summary_runs.csv 와 같은 값)
```csv
variant,map,bs,rep,bw_MiBps,iops,written_GiB,fill_ratio,clat_mean_us,clat_p50_us,clat_p99_us,clat_p999_us,lat_mean_us,slat_mean_us,runtime_s,bw_first10s_MiBps,bw_last20s_MiBps,dev_bytes,chmodel_msgs,kernel_warn,gc_onset_s,gc_onset_last_part_s,bw_pre_gc_MiBps,bw_post_gc_MiBps,gc_cnt,ftl_host_pgs,ftl_gc_pgs,waf_gc,waf_total,blk_wr_ios,blk_wr_merges,blk_avg_req_KiB
wbuffix,4k,4k,1,414.744141,106174.680422,24.301861,2.167092,300.359579,69.120000,13434.880000,16908.288000,301.201599,0.842020,60.001000,1274.286035,320.716162,12040984064,0,0,6.276949,6.297565,2015.765137,236.918231,8133,6370587,13406435,3.104427,3.104427,,,
wbuffix,4k,4k,2,415.502930,106368.893852,24.346313,2.171056,299.800560,70.144000,13303.808000,16908.288000,300.651257,0.850697,60.001000,1272.479395,323.801611,12040984064,0,0,6.341670,6.362200,1992.748698,240.795287,8170,6382240,13471081,3.110714,3.110714,,,
wbuffix,4k,4k,3,417.743164,106942.442926,24.481262,2.183090,298.191441,70.144000,13303.808000,17170.432000,299.041393,0.849952,60.010000,1271.960205,321.358008,12040984064,0,0,6.333402,6.354020,1995.562581,242.558205,8311,6417616,13724008,3.138490,3.138490,,,
wbuffix,4k,8k,1,438.130859,56080.782497,25.677307,2.289746,569.382809,120.320000,16580.608000,17694.720000,570.377012,0.994203,60.013000,1285.062305,330.371655,12040984064,0,0,5.737141,5.756448,2211.021307,259.335230,9418,6731152,15677914,3.329158,3.329158,3363759,1817,8.004321
wbuffix,4k,8k,2,437.212891,55963.335167,25.619263,2.284570,570.579001,120.320000,16580.608000,17956.864000,571.570814,0.991813,60.003000,1285.833301,325.344287,12040984064,0,0,5.739599,5.758605,2211.022727,258.271395,9366,6715936,15586294,3.320793,3.320793,3356194,1774,8.004229
wbuffix,4k,8k,3,435.708984,55770.834375,25.533691,2.276940,572.564961,120.320000,16580.608000,17694.720000,573.543219,0.978258,60.009000,1285.834521,334.511279,12040984064,0,0,5.739419,5.758342,2211.022727,256.648393,9294,6693504,15461194,3.309880,3.309880,3344978,1774,8.004243
wbuffix,4k,16k,1,480.999023,30783.988268,28.186401,2.513492,1038.022001,222.208000,17694.720000,18481.152000,1039.254059,1.232058,60.006000,1287.867432,245.083618,12040984064,0,0,5.696374,5.696590,2217.289773,305.847343,11268,7388896,18809364,3.545626,3.545626,,,
wbuffix,4k,16k,2,481.021484,30785.422673,28.190063,2.513819,1037.985228,222.208000,17694.720000,18481.152000,1039.207547,1.222319,60.011000,1288.532520,244.851978,12040984064,0,0,5.693162,5.693381,2217.735795,305.870359,11272,7389856,18816036,3.546198,3.546198,,,
wbuffix,4k,16k,3,480.858398,30774.952511,28.181885,2.513089,1038.356268,222.208000,17694.720000,18481.152000,1039.564602,1.208333,60.014000,1288.332617,244.564771,12040984064,0,0,5.693097,5.693314,2217.750000,305.711466,11272,7387712,18818152,3.547223,3.547223,,,
wbuffix,4k,32k,1,482.454102,15438.541528,28.272583,2.521177,2070.787029,444.416000,18219.008000,18743.296000,2072.462820,1.675792,60.008000,1290.641553,247.503369,12040984064,0,0,5.693038,5.693245,2217.772727,307.412378,11276,7411488,18802256,3.536907,3.536907,,,
wbuffix,4k,32k,2,482.242188,15431.768195,28.263947,2.520407,2071.719447,444.416000,18219.008000,18743.296000,2073.377194,1.657747,60.016000,1290.946875,247.171655,12040984064,0,0,5.693209,5.693420,2217.767045,307.238407,11276,7409224,18804224,3.537948,3.537948,,,
wbuffix,4k,32k,3,482.105469,15427.381190,28.254028,2.519523,2072.335555,444.416000,18219.008000,18743.296000,2073.970227,1.634673,60.012000,1290.562500,246.785425,12040984064,0,0,5.693451,5.693653,2217.772727,307.052331,11276,7406624,18807152,3.539234,3.539234,,,
wbuffix,4k,64k,1,486.293945,7780.706870,28.499023,2.541370,4109.839365,897.024000,19005.440000,19529.728000,4112.447274,2.607909,60.011000,1293.667041,254.405859,12040984064,0,0,5.693086,5.693272,2217.871893,311.666069,11344,7470848,18881936,3.527415,3.527415,466928,0,64.000000
wbuffix,4k,64k,2,486.343750,7781.514566,28.498657,2.541337,4109.470216,897.024000,19005.440000,19529.728000,4112.067183,2.596967,60.004000,1293.673291,254.386230,12040984064,0,0,5.692843,5.693033,2217.883256,311.657890,11344,7470752,18882016,3.527459,3.527459,466921,1,64.000137
wbuffix,4k,64k,3,486.313477,7781.028709,28.503052,2.541729,4109.716784,897.024000,19005.440000,19529.728000,4112.292090,2.575307,60.017000,1293.673291,254.629785,12040984064,0,0,5.692765,5.692956,2217.883256,311.746407,11348,7471904,18888672,3.527960,3.527960,466994,0,64.000000
wbuffix,16k,4k,1,129.705078,33204.632947,7.600571,0.677773,962.636117,257.024000,14090.240000,15269.888000,963.509758,0.873642,60.005000,379.058301,58.142700,12040984064,0,0,5.914784,5.944689,535.575994,88.762874,7055,1992444,2400489,2.204796,8.819185,,,
wbuffix,16k,4k,2,129.760742,33218.913018,7.603333,0.678019,962.223264,254.976000,13959.168000,15400.960000,963.090408,0.867144,60.001000,379.035547,58.343384,12040984064,0,0,5.911013,5.940904,535.598722,88.812070,7061,1993166,2402806,2.205522,8.822080,,,
wbuffix,16k,4k,3,129.697266,33202.646623,7.599609,0.677687,962.699315,257.024000,14090.240000,15269.888000,963.566723,0.867408,60.001000,378.642969,58.192456,12040984064,0,0,5.914207,5.944163,535.609375,88.740870,7052,1992192,2399217,2.204310,8.817241,,,
wbuffix,16k,8k,1,217.257812,27809.058792,12.731674,1.135333,1149.401972,248.832000,16580.608000,17694.720000,1150.455358,1.053385,60.008000,735.921875,80.785034,12040984064,0,0,5.905100,5.972510,1071.994318,131.037996,8082,1668592,3250164,2.947848,5.895082,1668405,361,8.001731
wbuffix,16k,8k,2,217.462891,27835.274709,12.743889,1.136423,1148.294872,248.832000,16449.536000,17694.720000,1149.368839,1.073967,60.009000,736.346484,80.936182,12040984064,0,0,5.904937,5.972377,1072.034091,131.263116,8106,1670210,3260794,2.952326,5.904097,1670063,304,8.001456
wbuffix,16k,8k,3,217.187500,27800.036660,12.728180,1.135022,1149.773176,248.832000,16580.608000,17694.720000,1150.822708,1.049532,60.011000,736.344922,80.963892,12040984064,0,0,5.904839,5.972613,1072.032670,130.966134,8074,1668164,3246459,2.946127,5.891745,1668020,288,8.001381
wbuffix,16k,16k,1,419.193359,26828.405720,24.562958,2.190375,1191.270901,246.784000,16711.680000,17956.864000,1192.519928,1.249026,60.002000,1280.556055,324.757324,12040984064,0,0,5.920972,5.942714,2143.232955,245.238210,8250,1609758,3394501,3.108703,3.108703,,,
wbuffix,16k,16k,2,420.218750,26894.047460,24.625519,2.195954,1188.302654,246.784000,16908.288000,17956.864000,1189.597476,1.294822,60.008000,1280.481250,322.744922,12040984064,0,0,5.920850,5.942568,2143.198864,246.406447,8310,1613858,3421069,3.119808,3.119808,,,
wbuffix,16k,16k,3,421.750977,26992.084784,24.716522,2.204069,1184.052978,246.784000,16908.288000,17956.864000,1185.275408,1.222431,60.011000,1280.323437,322.717505,12040984064,0,0,5.921050,5.942793,2143.167614,248.120655,8399,1619822,3460675,3.136454,3.136454,,,
wbuffix,16k,32k,1,440.150391,14084.817783,25.794800,2.300224,2270.053876,464.896000,18219.008000,18743.296000,2271.685656,1.631780,60.011000,1285.850000,319.397363,12040984064,0,0,5.843336,5.864878,2173.000000,265.355505,9392,1690488,3898342,3.306045,3.306045,,,
wbuffix,16k,32k,2,442.691406,14166.136208,25.943726,2.313504,2256.992831,464.896000,18219.008000,18743.296000,2258.667132,1.674301,60.011000,1285.865430,322.904028,12040984064,0,0,5.845501,5.867085,2172.034091,268.256209,9520,1700248,3954112,3.325609,3.325609,,,
wbuffix,16k,32k,3,441.902344,14140.878868,25.896606,2.309302,2261.016160,464.896000,18219.008000,18743.296000,2262.675991,1.659831,60.009000,1285.853125,321.991016,12040984064,0,0,5.843275,5.864806,2173.000000,267.268985,9478,1697160,3935692,3.318987,3.318987,,,
wbuffix,16k,64k,1,486.280273,7780.499592,28.497314,2.541217,4109.934451,897.024000,19005.440000,19529.728000,4112.578399,2.643948,60.009000,1293.673096,254.364087,12040984064,0,0,5.693203,5.693323,2217.882901,311.644603,11344,1867600,4720596,3.527627,3.527627,466900,0,64.000000
wbuffix,16k,64k,2,486.471680,7783.553607,28.504700,2.541876,4108.400097,897.024000,19005.440000,19529.728000,4110.984836,2.584739,60.001000,1293.673291,254.700244,12040984064,0,0,5.692717,5.692835,2217.883256,311.776224,11348,1868084,4722020,3.527734,3.527734,467020,1,64.000137
wbuffix,16k,64k,3,486.450195,7783.213637,28.509155,2.542273,4108.578080,897.024000,19005.440000,19529.728000,4111.113751,2.535672,60.013000,1293.673291,254.924414,12040984064,0,0,5.692996,5.693117,2217.883256,311.857368,11348,1868376,4721864,3.527256,3.527256,467093,1,64.000137
wbuffix,32k,4k,1,68.297852,17484.250525,4.001961,0.356871,1828.997847,577.536000,14483.456000,15400.960000,1829.975799,0.977952,60.002000,189.893750,32.784985,12040984064,0,0,6.061479,6.144004,256.082031,47.436044,7222,1049090,1190140,2.134450,17.075599,,,
wbuffix,32k,4k,2,68.236328,17468.632842,3.999252,0.356629,1830.629704,569.344000,14483.456000,15400.960000,1831.593495,0.963791,60.015000,189.828906,32.324097,12040984064,0,0,6.061112,6.143710,256.088542,47.383753,7209,1048380,1187519,2.132718,17.061745,,,
wbuffix,32k,4k,3,68.331055,17492.768595,4.004845,0.357128,1828.107287,569.344000,14483.456000,15532.032000,1829.075747,0.968460,60.016000,189.655078,32.785229,12040984064,0,0,6.061261,6.143886,256.074219,47.491310,7237,1049846,1193186,2.136534,17.092274,,,
wbuffix,32k,8k,1,131.893555,16882.453918,7.728432,0.689175,1894.114134,561.152000,15007.744000,15925.248000,1895.208210,1.094076,60.002000,377.101562,59.910327,12040984064,0,0,6.067083,6.122088,512.569010,89.603995,7344,1012980,1257468,2.241355,8.965412,1012980,1,8.000008
wbuffix,32k,8k,2,131.824219,16873.604213,7.724380,0.688813,1895.132102,561.152000,15007.744000,16056.320000,1896.198845,1.066743,60.002000,377.098437,60.578589,12040984064,0,0,6.066635,6.121722,512.566406,89.525843,7329,1012450,1254180,2.238757,8.955030,1012450,0,8.000000
wbuffix,32k,8k,3,132.128906,16912.552280,7.743629,0.690530,1890.755613,561.152000,15138.816000,16056.320000,1891.824242,1.068629,60.013000,377.250781,61.013745,12040984064,0,0,6.066664,6.121649,512.569010,89.891086,7386,1014973,1266264,2.247584,8.990336,1014973,0,8.000000
wbuffix,32k,16k,1,219.137695,14024.842961,12.843765,1.145329,2280.131635,536.576000,17694.720000,17956.864000,2281.387771,1.256136,60.017000,741.178125,82.053955,12040984064,0,0,6.063629,6.100835,1026.854167,129.459084,8241,841716,1658397,2.970257,5.940423,,,
wbuffix,32k,16k,2,219.869141,14071.686857,12.885376,1.149040,2272.596578,536.576000,17694.720000,17956.864000,2273.826587,1.230009,60.011000,741.165625,82.599487,12040984064,0,0,6.064007,6.101138,1026.843750,130.249032,8332,844448,1678949,2.988221,5.976385,,,
wbuffix,32k,16k,3,219.689453,14060.135968,12.875443,1.148154,2274.438362,536.576000,17432.576000,17956.864000,2275.689247,1.250885,60.014000,741.171875,81.829932,12040984064,0,0,6.063796,6.100865,1026.875000,130.057310,8296,843792,1670390,2.979623,5.959154,,,
wbuffix,32k,32k,1,424.518555,13584.623590,24.874603,2.218166,2353.691890,522.240000,17694.720000,18219.008000,2355.361397,1.669507,60.001000,1277.778125,323.905225,12040984064,0,0,6.096136,6.140668,2032.765625,245.838406,8398,815091,1724901,3.116207,3.116207,,,
wbuffix,32k,32k,2,424.844727,13595.056749,24.893707,2.219870,2351.873088,522.240000,17694.720000,18219.008000,2353.546356,1.673268,60.001000,1277.990625,321.330151,12040984064,0,0,6.095870,6.140373,2032.770833,246.186614,8418,815717,1729407,3.120107,3.120107,,,
wbuffix,32k,32k,3,424.583984,13586.703324,24.884216,2.219023,2353.284186,522.240000,17694.720000,18219.008000,2354.957588,1.673402,60.015000,1278.262500,323.138062,12040984064,0,0,6.096105,6.140618,2032.776042,246.006664,8411,815406,1727911,3.119081,3.119081,,,
wbuffix,32k,64k,1,447.133789,7154.148683,26.202332,2.336565,4470.067407,978.944000,19005.440000,19791.872000,4472.653493,2.586085,60.007000,1286.819336,319.806128,12040984064,0,0,5.972408,5.994798,2124.262429,277.953609,9562,858598,1979380,3.305363,3.305363,429299,0,64.000000
wbuffix,32k,64k,2,447.111328,7153.791035,26.202332,2.336565,4470.220853,978.944000,19005.440000,19529.728000,4472.850020,2.629167,60.010000,1286.823779,320.042676,12040984064,0,0,5.972674,5.995062,2124.202326,277.960310,9562,858598,1979380,3.305363,3.305363,429298,1,64.000149
wbuffix,32k,64k,3,447.164062,7154.625602,26.202332,2.336565,4469.785987,978.944000,19005.440000,19529.728000,4472.381158,2.595171,60.003000,1286.817871,320.035425,12040984064,0,0,5.972658,5.995078,2124.237038,277.956718,9562,858598,1979380,3.305363,3.305363,429299,0,64.000000
```

### 11.5.5 조합별 집계 전체 (analysis/summary_agg.csv 와 같은 값)
```csv
variant,map,bs,n,bw_MiBps_mean,bw_MiBps_std,bw_MiBps_min,bw_MiBps_max,iops_mean,iops_std,iops_min,iops_max,written_GiB_mean,written_GiB_std,written_GiB_min,written_GiB_max,fill_ratio_mean,fill_ratio_std,fill_ratio_min,fill_ratio_max,clat_mean_us_mean,clat_mean_us_std,clat_mean_us_min,clat_mean_us_max,clat_p50_us_mean,clat_p50_us_std,clat_p50_us_min,clat_p50_us_max,clat_p99_us_mean,clat_p99_us_std,clat_p99_us_min,clat_p99_us_max,clat_p999_us_mean,clat_p999_us_std,clat_p999_us_min,clat_p999_us_max,lat_mean_us_mean,lat_mean_us_std,lat_mean_us_min,lat_mean_us_max,slat_mean_us_mean,slat_mean_us_std,slat_mean_us_min,slat_mean_us_max,runtime_s_mean,runtime_s_std,runtime_s_min,runtime_s_max,bw_first10s_MiBps_mean,bw_first10s_MiBps_std,bw_first10s_MiBps_min,bw_first10s_MiBps_max,bw_last20s_MiBps_mean,bw_last20s_MiBps_std,bw_last20s_MiBps_min,bw_last20s_MiBps_max,chmodel_msgs_mean,chmodel_msgs_std,chmodel_msgs_min,chmodel_msgs_max,kernel_warn_mean,kernel_warn_std,kernel_warn_min,kernel_warn_max,gc_onset_s_mean,gc_onset_s_std,gc_onset_s_min,gc_onset_s_max,gc_onset_last_part_s_mean,gc_onset_last_part_s_std,gc_onset_last_part_s_min,gc_onset_last_part_s_max,bw_pre_gc_MiBps_mean,bw_pre_gc_MiBps_std,bw_pre_gc_MiBps_min,bw_pre_gc_MiBps_max,bw_post_gc_MiBps_mean,bw_post_gc_MiBps_std,bw_post_gc_MiBps_min,bw_post_gc_MiBps_max,gc_cnt_mean,gc_cnt_std,gc_cnt_min,gc_cnt_max,ftl_host_pgs_mean,ftl_host_pgs_std,ftl_host_pgs_min,ftl_host_pgs_max,ftl_gc_pgs_mean,ftl_gc_pgs_std,ftl_gc_pgs_min,ftl_gc_pgs_max,waf_gc_mean,waf_gc_std,waf_gc_min,waf_gc_max,waf_total_mean,waf_total_std,waf_total_min,waf_total_max,blk_avg_req_KiB_mean,blk_avg_req_KiB_std,blk_avg_req_KiB_min,blk_avg_req_KiB_max,blk_wr_ios_mean,blk_wr_ios_std,blk_wr_ios_min,blk_wr_ios_max,blk_wr_merges_mean,blk_wr_merges_std,blk_wr_merges_min,blk_wr_merges_max
wbuffix,4k,4k,3,415.996745,1.559303,414.744141,417.743164,106495.339067,399.194326,106174.680422,106942.442926,24.376479,0.093427,24.301861,24.481262,2.173746,0.008331,2.167092,2.183090,299.450527,1.125654,298.191441,300.359579,69.802667,0.591207,69.120000,70.144000,13347.498667,75.674454,13303.808000,13434.880000,16995.669333,151.348909,16908.288000,17170.432000,300.298083,1.122574,299.041393,301.201599,0.847556,0.004809,0.842020,0.850697,60.004000,0.005196,60.001000,60.010000,1272.908545,1.220860,1271.960205,1274.286035,321.958594,1.628044,320.716162,323.801611,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.317340,0.035223,6.276949,6.341670,6.337928,0.035194,6.297565,6.362200,2001.358805,12.555328,1992.748698,2015.765137,240.090574,2.885271,236.918231,242.558205,8204.666667,93.927277,8133,8311,6390148,24491.429202,6370587,6417616,13533841,167831.156709,13406435,13724008,3.117877,0.018126,3.104427,3.138490,3.117877,0.018126,3.104427,3.138490,,,,,,,,,,,,
wbuffix,4k,8k,3,437.017578,1.222694,435.708984,438.130859,55938.317346,156.481239,55770.834375,56080.782497,25.610087,0.072246,25.533691,25.677307,2.283752,0.006442,2.276940,2.289746,570.842257,1.607327,569.382809,572.564961,120.320000,0.000000,120.320000,120.320000,16580.608000,0.000000,16580.608000,16580.608000,17782.101333,151.348909,17694.720000,17956.864000,571.830348,1.598979,570.377012,573.543219,0.988091,0.008600,0.978258,0.994203,60.008333,0.005033,60.003000,60.013000,1285.576709,0.445488,1285.062305,1285.834521,330.075741,4.590655,325.344287,334.511279,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.738720,0.001370,5.737141,5.739599,5.757798,0.001177,5.756448,5.758605,2211.022254,0.000820,2211.021307,2211.022727,258.085006,1.353081,256.648393,259.335230,9359.333333,62.268237,9294,9418,6713531,18938.906973,6693504,6731152,15575134,108790.159481,15461194,15677914,3.319944,0.009667,3.309880,3.329158,3.319944,0.009667,3.309880,3.329158,8.004264,0.000050,8.004229,8.004321,3354977,9449.460672,3344978,3363759,1788.333333,24.826062,1774,1817
wbuffix,4k,16k,3,480.959635,0.088390,480.858398,481.021484,30781.454484,5.676365,30774.952511,30785.422673,28.186117,0.004097,28.181885,28.190063,2.513467,0.000365,2.513089,2.513819,1038.121166,0.204433,1037.985228,1038.356268,222.208000,0.000000,222.208000,222.208000,17694.720000,0.000000,17694.720000,17694.720000,18481.152000,0.000000,18481.152000,18481.152000,1039.342069,0.194117,1039.207547,1039.564602,1.220903,0.011925,1.208333,1.232058,60.010333,0.004041,60.006000,60.014000,1288.244189,0.341248,1287.867432,1288.532520,244.833455,0.259919,244.564771,245.083618,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.694211,0.001873,5.693097,5.696374,5.694428,0.001872,5.693314,5.696590,2217.591856,0.261708,2217.289773,2217.750000,305.809723,0.085867,305.711466,305.870359,11270.666667,2.309401,11268,11272,7388821,1073.948478,7387712,7389856,18814517,4586.610659,18809364,18818152,3.546349,0.000809,3.545626,3.547223,3.546349,0.000809,3.545626,3.547223,,,,,,,,,,,,
wbuffix,4k,32k,3,482.267253,0.175663,482.105469,482.454102,15432.563638,5.622529,15427.381190,15438.541528,28.263519,0.009285,28.254028,28.272583,2.520369,0.000828,2.519523,2.521177,2071.614010,0.779629,2070.787029,2072.335555,444.416000,0.000000,444.416000,444.416000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2073.270081,0.759390,2072.462820,2073.970227,1.656070,0.020611,1.634673,1.675792,60.012000,0.004000,60.008000,60.016000,1290.716976,0.202984,1290.562500,1290.946875,247.153483,0.359317,246.785425,247.503369,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.693233,0.000208,5.693038,5.693451,5.693439,0.000205,5.693245,5.693653,2217.770833,0.003280,2217.767045,2217.772727,307.234372,0.180057,307.052331,307.412378,11276.000000,0.000000,11276,11276,7409112,2433.933442,7406624,7411488,18804544,2463.636337,18802256,18807152,3.538030,0.001166,3.536907,3.539234,3.538030,0.001166,3.536907,3.539234,,,,,,,,,,,,
wbuffix,4k,64k,3,486.317057,0.025095,486.293945,486.343750,7781.083382,0.406614,7780.706870,7781.514566,28.500244,0.002438,28.498657,28.503052,2.541479,0.000217,2.541337,2.541729,4109.675455,0.188013,4109.470216,4109.839365,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4112.268849,0.191108,4112.067183,4112.447274,2.593394,0.016592,2.575307,2.607909,60.010667,0.006506,60.004000,60.017000,1293.671208,0.003608,1293.667041,1293.673291,254.473958,0.135306,254.386230,254.629785,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.692898,0.000167,5.692765,5.693086,5.693087,0.000165,5.692956,5.693272,2217.879469,0.006561,2217.871893,2217.883256,311.690122,0.048916,311.657890,311.746407,11345.333333,2.309401,11344,11348,7471168,639.199499,7470752,7471904,18884208,3866.144333,18881936,18888672,3.527611,0.000303,3.527415,3.527960,3.527611,0.000303,3.527415,3.527960,64.000046,0.000079,64.000000,64.000137,466947.666667,40.278199,466921,466994,0.333333,0.577350,0,1
wbuffix,16k,4k,3,129.721029,0.034614,129.697266,129.760742,33208.730863,8.873758,33202.646623,33218.913018,7.601171,0.001933,7.599609,7.603333,0.677826,0.000172,0.677687,0.678019,962.519565,0.258543,962.223264,962.699315,256.341333,1.182413,254.976000,257.024000,14046.549333,75.674454,13959.168000,14090.240000,15313.578667,75.674454,15269.888000,15400.960000,963.388963,0.260120,963.090408,963.566723,0.869398,0.003677,0.867144,0.873642,60.002333,0.002309,60.001000,60.005000,378.912272,0.233501,378.642969,379.058301,58.226180,0.104506,58.142700,58.343384,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.913335,0.002031,5.911013,5.914784,5.943252,0.002050,5.940904,5.944689,535.594697,0.017050,535.575994,535.609375,88.771938,0.036455,88.740870,88.812070,7056.000000,4.582576,7052,7061,1992601,505.546569,1992192,1993166,2400837,1819.679184,2399217,2402806,2.204876,0.000610,2.204310,2.205522,8.819502,0.002435,8.817241,8.822080,,,,,,,,,,,,
wbuffix,16k,8k,3,217.302734,0.143086,217.187500,217.462891,27814.790054,18.304796,27800.036660,27835.274709,12.734581,0.008248,12.728180,12.743889,1.135593,0.000736,1.135022,1.136423,1149.156674,0.769074,1148.294872,1149.773176,248.832000,0.000000,248.832000,248.832000,16536.917333,75.674454,16449.536000,16580.608000,17694.720000,0.000000,17694.720000,17694.720000,1150.215635,0.755999,1149.368839,1150.822708,1.058961,0.013137,1.049532,1.073967,60.009333,0.001528,60.008000,60.011000,736.204427,0.244699,735.921875,736.346484,80.895036,0.096266,80.785034,80.963892,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.904959,0.000132,5.904839,5.905100,5.972500,0.000118,5.972377,5.972613,1072.020360,0.022564,1071.994318,1072.034091,131.089082,0.154942,130.966134,131.263116,8087.333333,16.653328,8074,8106,1668989,1079.137310,1668164,1670210,3252472,7441.058952,3246459,3260794,2.948767,0.003200,2.946127,2.952326,5.896975,0.006389,5.891745,5.904097,8.001523,0.000184,8.001381,8.001731,1668829,1085.590316,1668020,1670063,317.666667,38.370996,288,361
wbuffix,16k,16k,3,420.387695,1.287151,419.193359,421.750977,26904.845988,82.372114,26828.405720,26992.084784,24.635000,0.077220,24.562958,24.716522,2.196800,0.006886,2.190375,2.204069,1187.875511,3.627871,1184.052978,1191.270901,246.784000,0.000000,246.784000,246.784000,16842.752000,113.511682,16711.680000,16908.288000,17956.864000,0.000000,17956.864000,17956.864000,1189.130937,3.644724,1185.275408,1192.519928,1.255426,0.036618,1.222431,1.294822,60.007000,0.004583,60.002000,60.011000,1280.453581,0.118751,1280.323437,1280.556055,323.406584,1.169856,322.717505,324.757324,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.920957,0.000101,5.920850,5.921050,5.942692,0.000114,5.942568,5.942793,2143.199811,0.032681,2143.167614,2143.232955,246.588437,1.449815,245.238210,248.120655,8319.666667,74.968882,8250,8399,1614479,5060.688227,1609758,1619822,3425415,33300.380719,3394501,3460675,3.121655,0.013967,3.108703,3.136454,3.121655,0.013967,3.108703,3.136454,,,,,,,,,,,,
wbuffix,16k,32k,3,441.581380,1.300559,440.150391,442.691406,14130.610953,41.620237,14084.817783,14166.136208,25.878377,0.076118,25.794800,25.943726,2.307677,0.006788,2.300224,2.313504,2262.687622,6.689026,2256.992831,2270.053876,464.896000,0.000000,464.896000,464.896000,18219.008000,0.000000,18219.008000,18219.008000,18743.296000,0.000000,18743.296000,18743.296000,2264.342926,6.667421,2258.667132,2271.685656,1.655304,0.021619,1.631780,1.674301,60.010333,0.001155,60.009000,60.011000,1285.856185,0.008157,1285.850000,1285.865430,321.430802,1.819218,319.397363,322.904028,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.844037,0.001268,5.843275,5.845501,5.865590,0.001295,5.864806,5.867085,2172.678030,0.557668,2172.034091,2173.000000,266.960233,1.474794,265.355505,268.256209,9463.333333,65.248244,9392,9520,1695965,4988.468837,1690488,1700248,3929382,28415.406033,3898342,3954112,3.316880,0.009950,3.306045,3.325609,3.316880,0.009950,3.306045,3.325609,,,,,,,,,,,,
wbuffix,16k,64k,3,486.400716,0.104858,486.280273,486.471680,7782.422279,1.673750,7780.499592,7783.553607,28.503723,0.005981,28.497314,28.509155,2.541789,0.000533,2.541217,2.542273,4108.970876,0.839212,4108.400097,4109.934451,897.024000,0.000000,897.024000,897.024000,19005.440000,0.000000,19005.440000,19005.440000,19529.728000,0.000000,19529.728000,19529.728000,4111.558996,0.885180,4110.984836,4112.578399,2.588120,0.054218,2.535672,2.643948,60.007667,0.006110,60.001000,60.013000,1293.673226,0.000113,1293.673096,1293.673291,254.662915,0.282023,254.364087,254.924414,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.692972,0.000244,5.692717,5.693203,5.693092,0.000245,5.692835,5.693323,2217.883138,0.000205,2217.882901,2217.883256,311.759398,0.107376,311.644603,311.857368,11346.666667,2.309401,11344,11348,1868020,391.938771,1867600,1868376,4721493,781.018139,4720596,4722020,3.527539,0.000251,3.527256,3.527734,3.527539,0.000251,3.527256,3.527734,64.000091,0.000079,64.000000,64.000137,467004.333333,97.449132,466900,467093,0.666667,0.577350,0,1
wbuffix,32k,4k,3,68.288411,0.048064,68.236328,68.331055,17481.883987,12.240671,17468.632842,17492.768595,4.002019,0.002797,3.999252,4.004845,0.356876,0.000249,0.356629,0.357128,1829.244946,1.279234,1828.107287,1830.629704,572.074667,4.729653,569.344000,577.536000,14483.456000,0.000000,14483.456000,14483.456000,15444.650667,75.674454,15400.960000,15532.032000,1830.215014,1.275806,1829.075747,1831.593495,0.970068,0.007216,0.963791,0.977952,60.011000,0.007810,60.002000,60.016000,189.792578,0.123413,189.655078,189.893750,32.631437,0.266165,32.324097,32.785229,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.061284,0.000185,6.061112,6.061479,6.143867,0.000148,6.143710,6.144004,256.081597,0.007171,256.074219,256.088542,47.437036,0.053786,47.383753,47.491310,7222.666667,14.011900,7209,7237,1049105,733.120272,1048380,1049846,1190282,2836.154850,1187519,1193186,2.134567,0.001911,2.132718,2.136534,17.076539,0.015287,17.061745,17.092274,,,,,,,,,,,,
wbuffix,32k,8k,3,131.948893,0.159704,131.824219,132.128906,16889.536804,20.417234,16873.604213,16912.552280,7.732147,0.010148,7.724380,7.743629,0.689506,0.000905,0.688813,0.690530,1893.333950,2.290181,1890.755613,1895.132102,561.152000,0.000000,561.152000,561.152000,15051.434667,75.674454,15007.744000,15138.816000,16012.629333,75.674454,15925.248000,16056.320000,1894.410432,2.293823,1891.824242,1896.198845,1.076482,0.015265,1.066743,1.094076,60.005667,0.006351,60.002000,60.013000,377.150260,0.087068,377.098437,377.250781,60.500887,0.555798,59.910327,61.013745,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.066794,0.000251,6.066635,6.067083,6.121820,0.000235,6.121649,6.122088,512.568142,0.001504,512.566406,512.569010,89.673641,0.192324,89.525843,89.891086,7353.000000,29.546573,7329,7386,1013468,1330.318132,1012450,1014973,1259304,6247.714462,1254180,1266264,2.242566,0.004536,2.238757,2.247584,8.970259,0.018145,8.955030,8.990336,8.000003,0.000005,8.000000,8.000008,1013468,1330.318132,1012450,1014973,0.333333,0.577350,0,1
wbuffix,32k,16k,3,219.565430,0.381168,219.137695,219.869141,14052.221929,24.404132,14024.842961,14071.686857,12.868195,0.021732,12.843765,12.885376,1.147507,0.001938,1.145329,1.149040,2275.722191,3.928159,2272.596578,2280.131635,536.576000,0.000000,536.576000,536.576000,17607.338667,151.348909,17432.576000,17694.720000,17956.864000,0.000000,17956.864000,17956.864000,2276.967868,3.939420,2273.826587,2281.387771,1.245677,0.013820,1.230009,1.256136,60.014000,0.003000,60.011000,60.017000,741.171875,0.006250,741.165625,741.178125,82.161125,0.395813,81.829932,82.599487,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.063811,0.000189,6.063629,6.064007,6.100946,0.000167,6.100835,6.101138,1026.857639,0.015912,1026.843750,1026.875000,129.921809,0.412038,129.459084,130.249032,8289.666667,45.829394,8241,8332,843318.666667,1426.179979,841716,844448,1669245,10323.704390,1658397,1678949,2.979367,0.008984,2.970257,2.988221,5.958654,0.017986,5.940423,5.976385,,,,,,,,,,,,
wbuffix,32k,32k,3,424.649089,0.172557,424.518555,424.844727,13588.794554,5.522014,13584.623590,13595.056749,24.884176,0.009552,24.874603,24.893707,2.219020,0.000852,2.218166,2.219870,2352.949721,0.954416,2351.873088,2353.691890,522.240000,0.000000,522.240000,522.240000,17694.720000,0.000000,17694.720000,17694.720000,18219.008000,0.000000,18219.008000,18219.008000,2354.621780,0.952979,2353.546356,2355.361397,1.672059,0.002211,1.669507,1.673402,60.005667,0.008083,60.001000,60.015000,1278.010417,0.242793,1277.778125,1278.262500,322.791146,1.322125,321.330151,323.905225,0.000000,0.000000,0,0,0.000000,0.000000,0,0,6.096037,0.000145,6.095870,6.096136,6.140553,0.000158,6.140373,6.140668,2032.770833,0.005208,2032.765625,2032.776042,246.010561,0.174137,245.838406,246.186614,8409.000000,10.148892,8398,8418,815404.666667,313.002130,815091,815717,1727406,2295.000073,1724901,1729407,3.118465,0.002022,3.116207,3.120107,3.118465,0.002022,3.116207,3.120107,,,,,,,,,,,,
wbuffix,32k,64k,3,447.136393,0.026463,447.111328,447.164062,7154.188440,0.418702,7153.791035,7154.625602,26.202332,0.000000,26.202332,26.202332,2.336565,0.000000,2.336565,2.336565,4470.024749,0.220549,4469.785987,4470.220853,978.944000,0.000000,978.944000,978.944000,19005.440000,0.000000,19005.440000,19005.440000,19617.109333,151.348909,19529.728000,19791.872000,4472.628224,0.235450,4472.381158,4472.850020,2.603474,0.022709,2.586085,2.629167,60.006667,0.003512,60.003000,60.010000,1286.820329,0.003077,1286.817871,1286.823779,319.961410,0.134527,319.806128,320.042676,0.000000,0.000000,0,0,0.000000,0.000000,0,0,5.972580,0.000149,5.972408,5.972674,5.994979,0.000157,5.994798,5.995078,2124.233931,0.030172,2124.202326,2124.262429,277.956879,0.003354,277.953609,277.960310,9562.000000,0.000000,9562,9562,858598.000000,0.000000,858598,858598,1979380,0.000000,1979380,1979380,3.305363,0.000000,3.305363,3.305363,3.305363,0.000000,3.305363,3.305363,64.000050,0.000086,64.000000,64.000149,429298.666667,0.577350,429298,429299,0.333333,0.577350,0,1
```

### 11.5.6 파티션별 GC 로그 (회차마다: 첫 GC 줄의 fio 시작 기준 시각·내용, rmmod 통계)
```
[wbuffix map4k bs4k r1]
  +6.277s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.279s first GC part=2 victim line=340 vpc=1890 ipc=158 free_lines=2 host_pgs=778240
  +6.296s first GC part=3 victim line=194 vpc=1892 ipc=156 free_lines=2 host_pgs=778240
  +6.298s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1592612 gc_pgs=3351083 gc_cnt=2033 free_lines=2
  stats part=1 host_pgs=1592973 gc_pgs=3350951 gc_cnt=2033 free_lines=2
  stats part=2 host_pgs=1592635 gc_pgs=3359213 gc_cnt=2037 free_lines=2
  stats part=3 host_pgs=1592367 gc_pgs=3345188 gc_cnt=2030 free_lines=2
  (kernel) [67140.460648] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67140.529053] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs4k r2]
  +6.342s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.344s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.361s first GC part=3 victim line=194 vpc=1893 ipc=155 free_lines=2 host_pgs=778240
  +6.362s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1595554 gc_pgs=3364734 gc_cnt=2041 free_lines=2
  stats part=1 host_pgs=1595898 gc_pgs=3366496 gc_cnt=2042 free_lines=2
  stats part=2 host_pgs=1595572 gc_pgs=3376919 gc_cnt=2047 free_lines=2
  stats part=3 host_pgs=1595216 gc_pgs=3362932 gc_cnt=2040 free_lines=2
  (kernel) [68478.392986] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68478.461462] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs4k r3]
  +6.333s first GC part=0 victim line=343 vpc=1898 ipc=150 free_lines=2 host_pgs=778240
  +6.335s first GC part=2 victim line=340 vpc=1889 ipc=159 free_lines=2 host_pgs=778240
  +6.353s first GC part=3 victim line=194 vpc=1893 ipc=155 free_lines=2 host_pgs=778240
  +6.354s first GC part=1 victim line=106 vpc=1897 ipc=151 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1604455 gc_pgs=3431525 gc_cnt=2078 free_lines=2
  stats part=1 host_pgs=1604663 gc_pgs=3429162 gc_cnt=2077 free_lines=2
  stats part=2 host_pgs=1604426 gc_pgs=3437602 gc_cnt=2081 free_lines=2
  stats part=3 host_pgs=1604072 gc_pgs=3425719 gc_cnt=2075 free_lines=2
  (kernel) [69675.373308] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69675.440673] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs8k r1]
  +5.737s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.737s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.756s first GC part=0 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.756s first GC part=1 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1682776 gc_pgs=3918415 gc_cnt=2354 free_lines=2
  stats part=1 host_pgs=1682776 gc_pgs=3918415 gc_cnt=2354 free_lines=2
  stats part=2 host_pgs=1682800 gc_pgs=3920542 gc_cnt=2355 free_lines=2
  stats part=3 host_pgs=1682800 gc_pgs=3920542 gc_cnt=2355 free_lines=2
  (kernel) [89413.899329] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89413.966343] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs8k r2]
  +5.740s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.740s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.759s first GC part=0 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  +5.759s first GC part=1 victim line=60 vpc=1895 ipc=153 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1678894 gc_pgs=3891573 gc_cnt=2339 free_lines=2
  stats part=1 host_pgs=1678894 gc_pgs=3891573 gc_cnt=2339 free_lines=2
  stats part=2 host_pgs=1679074 gc_pgs=3901574 gc_cnt=2344 free_lines=2
  stats part=3 host_pgs=1679074 gc_pgs=3901574 gc_cnt=2344 free_lines=2
  (kernel) [89836.064292] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89836.132268] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs8k r3]
  +5.739s first GC part=2 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.739s first GC part=3 victim line=313 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.758s first GC part=0 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  +5.758s first GC part=1 victim line=60 vpc=1896 ipc=152 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1673299 gc_pgs=3862245 gc_cnt=2322 free_lines=2
  stats part=1 host_pgs=1673299 gc_pgs=3862245 gc_cnt=2322 free_lines=2
  stats part=2 host_pgs=1673453 gc_pgs=3868352 gc_cnt=2325 free_lines=2
  stats part=3 host_pgs=1673453 gc_pgs=3868352 gc_cnt=2325 free_lines=2
  (kernel) [90258.311809] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90258.378770] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r1]
  +5.696s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.696s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.697s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.697s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  stats part=1 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  stats part=2 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  stats part=3 host_pgs=1847224 gc_pgs=4702341 gc_cnt=2817 free_lines=2
  (kernel) [67281.393642] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67281.461990] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r2]
  +5.693s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1847464 gc_pgs=4704009 gc_cnt=2818 free_lines=2
  (kernel) [68619.388342] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68619.455881] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs16k r3]
  +5.693s first GC part=0 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=291 vpc=1902 ipc=146 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  stats part=1 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  stats part=2 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  stats part=3 host_pgs=1846928 gc_pgs=4704538 gc_cnt=2818 free_lines=2
  (kernel) [69816.320560] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69816.387816] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r1]
  +5.693s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1852872 gc_pgs=4700564 gc_cnt=2819 free_lines=2
  (kernel) [67422.380994] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67422.447910] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r2]
  +5.693s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1852306 gc_pgs=4701056 gc_cnt=2819 free_lines=2
  (kernel) [68760.303887] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68760.372192] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs32k r3]
  +5.693s first GC part=0 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.694s first GC part=1 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.694s first GC part=2 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  +5.694s first GC part=3 victim line=26 vpc=1880 ipc=168 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  stats part=1 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  stats part=2 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  stats part=3 host_pgs=1851656 gc_pgs=4701788 gc_cnt=2819 free_lines=2
  (kernel) [69957.284852] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69957.352073] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r1]
  +5.693s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=1867712 gc_pgs=4720484 gc_cnt=2836 free_lines=3
  (kernel) [89484.320073] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89484.387095] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r2]
  +5.693s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=1867688 gc_pgs=4720504 gc_cnt=2836 free_lines=3
  (kernel) [89906.491184] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89906.558199] NVMeVirt: Virtual NVMe device closed
[wbuffix map4k bs64k r3]
  +5.693s first GC part=0 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=1 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=2 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  +5.693s first GC part=3 victim line=103 vpc=1876 ipc=172 free_lines=2 host_pgs=778240
  stats part=0 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=1867976 gc_pgs=4722168 gc_cnt=2837 free_lines=2
  (kernel) [90328.740782] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90328.808051] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r1]
  +5.915s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.926s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.944s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.945s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497230 gc_pgs=597554 gc_cnt=1757 free_lines=1
  stats part=1 host_pgs=498246 gc_pgs=596551 gc_cnt=1757 free_lines=1
  stats part=2 host_pgs=499280 gc_pgs=608304 gc_cnt=1782 free_lines=1
  stats part=3 host_pgs=497688 gc_pgs=598080 gc_cnt=1759 free_lines=1
  (kernel) [67563.295634] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67563.323382] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r2]
  +5.911s first GC part=2 victim line=6 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.940s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.941s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497426 gc_pgs=598400 gc_cnt=1759 free_lines=2
  stats part=1 host_pgs=498431 gc_pgs=597368 gc_cnt=1759 free_lines=2
  stats part=2 host_pgs=499452 gc_pgs=608601 gc_cnt=1783 free_lines=2
  stats part=3 host_pgs=497857 gc_pgs=598437 gc_cnt=1760 free_lines=2
  (kernel) [68901.156550] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68901.184548] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs4k r3]
  +5.914s first GC part=2 victim line=6 vpc=172 ipc=340 free_lines=2 host_pgs=194560
  +5.925s first GC part=1 victim line=8 vpc=164 ipc=348 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=10 vpc=168 ipc=344 free_lines=2 host_pgs=194560
  +5.944s first GC part=0 victim line=4 vpc=169 ipc=343 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=497171 gc_pgs=597627 gc_cnt=1757 free_lines=1
  stats part=1 host_pgs=498188 gc_pgs=596061 gc_cnt=1756 free_lines=1
  stats part=2 host_pgs=499219 gc_pgs=607359 gc_cnt=1780 free_lines=1
  stats part=3 host_pgs=497614 gc_pgs=598170 gc_cnt=1759 free_lines=2
  (kernel) [70098.161111] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70098.188836] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r1]
  +5.905s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.923s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.923s first GC part=3 victim line=10 vpc=178 ipc=334 free_lines=2 host_pgs=194560
  +5.973s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=417240 gc_pgs=812204 gc_cnt=2020 free_lines=2
  stats part=1 host_pgs=417395 gc_pgs=813557 gc_cnt=2023 free_lines=2
  stats part=2 host_pgs=417152 gc_pgs=814843 gc_cnt=2025 free_lines=2
  stats part=3 host_pgs=416805 gc_pgs=809560 gc_cnt=2014 free_lines=1
  (kernel) [89554.689889] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89554.717175] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r2]
  +5.905s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.923s first GC part=3 victim line=10 vpc=178 ipc=334 free_lines=2 host_pgs=194560
  +5.972s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=417657 gc_pgs=814854 gc_cnt=2026 free_lines=2
  stats part=1 host_pgs=417802 gc_pgs=815713 gc_cnt=2028 free_lines=1
  stats part=2 host_pgs=417541 gc_pgs=818546 gc_cnt=2033 free_lines=2
  stats part=3 host_pgs=417210 gc_pgs=811681 gc_cnt=2019 free_lines=2
  (kernel) [89976.901090] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89976.928781] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs8k r3]
  +5.905s first GC part=2 victim line=2 vpc=183 ipc=329 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=8 vpc=171 ipc=341 free_lines=2 host_pgs=194560
  +5.922s first GC part=3 victim line=10 vpc=179 ipc=333 free_lines=2 host_pgs=194560
  +5.973s first GC part=0 victim line=4 vpc=177 ipc=335 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=417140 gc_pgs=810776 gc_cnt=2017 free_lines=2
  stats part=1 host_pgs=417291 gc_pgs=812127 gc_cnt=2020 free_lines=1
  stats part=2 host_pgs=417030 gc_pgs=813404 gc_cnt=2022 free_lines=2
  stats part=3 host_pgs=416703 gc_pgs=810152 gc_cnt=2015 free_lines=2
  (kernel) [90399.131737] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90399.159114] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r1]
  +5.921s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.943s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=402514 gc_pgs=851867 gc_cnt=2069 free_lines=2
  stats part=1 host_pgs=402592 gc_pgs=851296 gc_cnt=2068 free_lines=2
  stats part=2 host_pgs=402576 gc_pgs=846185 gc_cnt=2058 free_lines=2
  stats part=3 host_pgs=402076 gc_pgs=845153 gc_cnt=2055 free_lines=2
  (kernel) [67704.063442] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67704.091003] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r2]
  +5.921s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.942s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=403495 gc_pgs=857538 gc_cnt=2082 free_lines=2
  stats part=1 host_pgs=403619 gc_pgs=858429 gc_cnt=2084 free_lines=2
  stats part=2 host_pgs=403588 gc_pgs=854387 gc_cnt=2076 free_lines=2
  stats part=3 host_pgs=403156 gc_pgs=850715 gc_cnt=2068 free_lines=2
  (kernel) [69041.945393] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69041.973688] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs16k r3]
  +5.921s first GC part=0 victim line=135 vpc=468 ipc=44 free_lines=2 host_pgs=194560
  +5.922s first GC part=1 victim line=144 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.943s first GC part=2 victim line=218 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  +5.943s first GC part=3 victim line=182 vpc=466 ipc=46 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=405037 gc_pgs=867257 gc_cnt=2104 free_lines=2
  stats part=1 host_pgs=405096 gc_pgs=866690 gc_cnt=2103 free_lines=2
  stats part=2 host_pgs=405065 gc_pgs=865195 gc_cnt=2100 free_lines=2
  stats part=3 host_pgs=404624 gc_pgs=861533 gc_cnt=2092 free_lines=2
  (kernel) [70238.949395] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70238.977171] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r1]
  +5.843s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.843s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.865s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.865s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=422769 gc_pgs=976483 gc_cnt=2352 free_lines=2
  stats part=1 host_pgs=422769 gc_pgs=976483 gc_cnt=2352 free_lines=2
  stats part=2 host_pgs=422475 gc_pgs=972688 gc_cnt=2344 free_lines=2
  stats part=3 host_pgs=422475 gc_pgs=972688 gc_cnt=2344 free_lines=2
  (kernel) [67844.827448] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67844.855323] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r2]
  +5.846s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.846s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.867s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.867s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=425136 gc_pgs=988954 gc_cnt=2381 free_lines=2
  stats part=1 host_pgs=425136 gc_pgs=988954 gc_cnt=2381 free_lines=2
  stats part=2 host_pgs=424988 gc_pgs=988102 gc_cnt=2379 free_lines=2
  stats part=3 host_pgs=424988 gc_pgs=988102 gc_cnt=2379 free_lines=2
  (kernel) [69182.714346] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69182.742224] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs32k r3]
  +5.843s first GC part=0 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.843s first GC part=1 victim line=152 vpc=465 ipc=47 free_lines=2 host_pgs=194560
  +5.865s first GC part=2 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.865s first GC part=3 victim line=344 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=424386 gc_pgs=985094 gc_cnt=2372 free_lines=2
  stats part=1 host_pgs=424386 gc_pgs=985094 gc_cnt=2372 free_lines=2
  stats part=2 host_pgs=424194 gc_pgs=982752 gc_cnt=2367 free_lines=2
  stats part=3 host_pgs=424194 gc_pgs=982752 gc_cnt=2367 free_lines=2
  (kernel) [70379.700715] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70379.728885] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r1]
  +5.693s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  stats part=1 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  stats part=2 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  stats part=3 host_pgs=466900 gc_pgs=1180149 gc_cnt=2836 free_lines=3
  (kernel) [89625.028679] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89625.056273] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r2]
  +5.693s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=467021 gc_pgs=1180505 gc_cnt=2837 free_lines=2
  (kernel) [90047.249993] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90047.277561] NVMeVirt: Virtual NVMe device closed
[wbuffix map16k bs64k r3]
  +5.693s first GC part=0 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=1 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=2 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  +5.693s first GC part=3 victim line=103 vpc=469 ipc=43 free_lines=2 host_pgs=194560
  stats part=0 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  stats part=1 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  stats part=2 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  stats part=3 host_pgs=467094 gc_pgs=1180466 gc_cnt=2837 free_lines=2
  (kernel) [90469.466695] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90469.494276] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs4k r1]
  +6.061s first GC part=0 victim line=6 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.099s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.122s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.144s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262646 gc_pgs=296766 gc_cnt=1804 free_lines=2
  stats part=1 host_pgs=262714 gc_pgs=302106 gc_cnt=1825 free_lines=1
  stats part=2 host_pgs=262172 gc_pgs=297736 gc_cnt=1806 free_lines=1
  stats part=3 host_pgs=261558 gc_pgs=293532 gc_cnt=1787 free_lines=2
  (kernel) [67985.618551] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [67985.639448] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs4k r2]
  +6.061s first GC part=0 victim line=8 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.098s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.121s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.144s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262452 gc_pgs=295672 gc_cnt=1799 free_lines=2
  stats part=1 host_pgs=262533 gc_pgs=301755 gc_cnt=1823 free_lines=2
  stats part=2 host_pgs=262006 gc_pgs=297157 gc_cnt=1803 free_lines=2
  stats part=3 host_pgs=261389 gc_pgs=292935 gc_cnt=1784 free_lines=1
  (kernel) [69323.475405] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69323.496390] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs4k r3]
  +6.061s first GC part=0 victim line=8 vpc=79 ipc=177 free_lines=2 host_pgs=97280
  +6.098s first GC part=1 victim line=34 vpc=77 ipc=179 free_lines=2 host_pgs=97280
  +6.122s first GC part=2 victim line=26 vpc=82 ipc=174 free_lines=2 host_pgs=97280
  +6.144s first GC part=3 victim line=29 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=262850 gc_pgs=298109 gc_cnt=1810 free_lines=2
  stats part=1 host_pgs=262911 gc_pgs=302397 gc_cnt=1827 free_lines=2
  stats part=2 host_pgs=262363 gc_pgs=298831 gc_cnt=1811 free_lines=2
  stats part=3 host_pgs=261722 gc_pgs=293849 gc_cnt=1789 free_lines=2
  (kernel) [70520.457108] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70520.477622] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs8k r1]
  +6.067s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.093s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +6.109s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +6.122s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=252948 gc_pgs=312364 gc_cnt=1827 free_lines=1
  stats part=1 host_pgs=253752 gc_pgs=319749 gc_cnt=1859 free_lines=1
  stats part=2 host_pgs=252896 gc_pgs=314194 gc_cnt=1834 free_lines=2
  stats part=3 host_pgs=253384 gc_pgs=311161 gc_cnt=1824 free_lines=2
  (kernel) [89695.351526] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89695.372009] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs8k r2]
  +6.067s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.093s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +6.109s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +6.122s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=252816 gc_pgs=311976 gc_cnt=1825 free_lines=2
  stats part=1 host_pgs=253630 gc_pgs=318861 gc_cnt=1855 free_lines=2
  stats part=2 host_pgs=252755 gc_pgs=313846 gc_cnt=1832 free_lines=2
  stats part=3 host_pgs=253249 gc_pgs=309497 gc_cnt=1817 free_lines=2
  (kernel) [90117.580917] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90117.601629] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs8k r3]
  +6.067s first GC part=0 victim line=3 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.092s first GC part=1 victim line=12 vpc=80 ipc=176 free_lines=2 host_pgs=97280
  +6.108s first GC part=2 victim line=0 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  +6.122s first GC part=3 victim line=14 vpc=78 ipc=178 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=253418 gc_pgs=314714 gc_cnt=1838 free_lines=2
  stats part=1 host_pgs=254255 gc_pgs=322572 gc_cnt=1872 free_lines=1
  stats part=2 host_pgs=253427 gc_pgs=317001 gc_cnt=1847 free_lines=2
  stats part=3 host_pgs=253873 gc_pgs=311977 gc_cnt=1829 free_lines=2
  (kernel) [90539.830679] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90539.851141] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs16k r1]
  +6.064s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.089s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.100s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.101s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210418 gc_pgs=414554 gc_cnt=2060 free_lines=2
  stats part=1 host_pgs=210533 gc_pgs=415966 gc_cnt=2066 free_lines=2
  stats part=2 host_pgs=210575 gc_pgs=417709 gc_cnt=2073 free_lines=2
  stats part=3 host_pgs=210190 gc_pgs=410168 gc_cnt=2042 free_lines=1
  (kernel) [68126.345737] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68126.366307] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs16k r2]
  +6.064s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.089s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.100s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.101s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=211115 gc_pgs=419470 gc_cnt=2082 free_lines=2
  stats part=1 host_pgs=211238 gc_pgs=420384 gc_cnt=2086 free_lines=1
  stats part=2 host_pgs=211230 gc_pgs=422434 gc_cnt=2094 free_lines=1
  stats part=3 host_pgs=210865 gc_pgs=416661 gc_cnt=2070 free_lines=2
  (kernel) [69464.250543] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69464.271401] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs16k r3]
  +6.064s first GC part=1 victim line=12 vpc=86 ipc=170 free_lines=2 host_pgs=97280
  +6.089s first GC part=2 victim line=0 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.100s first GC part=0 victim line=8 vpc=84 ipc=172 free_lines=2 host_pgs=97280
  +6.101s first GC part=3 victim line=47 vpc=83 ipc=173 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=210949 gc_pgs=416838 gc_cnt=2071 free_lines=1
  stats part=1 host_pgs=211076 gc_pgs=419523 gc_cnt=2082 free_lines=2
  stats part=2 host_pgs=211056 gc_pgs=419787 gc_cnt=2083 free_lines=2
  stats part=3 host_pgs=210711 gc_pgs=414242 gc_cnt=2060 free_lines=1
  (kernel) [70661.212390] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70661.233168] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs32k r1]
  +6.096s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.119s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.140s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.141s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203850 gc_pgs=430262 gc_cnt=2096 free_lines=2
  stats part=1 host_pgs=203598 gc_pgs=428726 gc_cnt=2089 free_lines=2
  stats part=2 host_pgs=203954 gc_pgs=433212 gc_cnt=2108 free_lines=2
  stats part=3 host_pgs=203689 gc_pgs=432701 gc_cnt=2105 free_lines=2
  (kernel) [68267.097035] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [68267.118069] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs32k r2]
  +6.096s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.119s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.140s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.140s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=204011 gc_pgs=431643 gc_cnt=2102 free_lines=2
  stats part=1 host_pgs=203744 gc_pgs=430879 gc_cnt=2098 free_lines=2
  stats part=2 host_pgs=204115 gc_pgs=434591 gc_cnt=2114 free_lines=2
  stats part=3 host_pgs=203847 gc_pgs=432294 gc_cnt=2104 free_lines=2
  (kernel) [69604.999711] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [69605.020648] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs32k r3]
  +6.096s first GC part=0 victim line=74 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +6.119s first GC part=1 victim line=143 vpc=231 ipc=25 free_lines=2 host_pgs=97280
  +6.140s first GC part=2 victim line=49 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +6.141s first GC part=3 victim line=344 vpc=227 ipc=29 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=203929 gc_pgs=431205 gc_cnt=2100 free_lines=2
  stats part=1 host_pgs=203675 gc_pgs=430945 gc_cnt=2098 free_lines=2
  stats part=2 host_pgs=204034 gc_pgs=433652 gc_cnt=2110 free_lines=2
  stats part=3 host_pgs=203768 gc_pgs=432109 gc_cnt=2103 free_lines=3
  (kernel) [70801.976214] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [70801.996911] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs64k r1]
  +5.972s first GC part=0 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.972s first GC part=1 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.995s first GC part=2 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +5.995s first GC part=3 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=1 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=2 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  stats part=3 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  (kernel) [89765.679385] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [89765.699784] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs64k r2]
  +5.973s first GC part=0 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.973s first GC part=1 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.995s first GC part=2 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +5.995s first GC part=3 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=1 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=2 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  stats part=3 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  (kernel) [90187.918886] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90187.939349] NVMeVirt: Virtual NVMe device closed
[wbuffix map32k bs64k r3]
  +5.973s first GC part=0 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.973s first GC part=1 victim line=117 vpc=230 ipc=26 free_lines=2 host_pgs=97280
  +5.995s first GC part=2 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  +5.995s first GC part=3 victim line=328 vpc=229 ipc=27 free_lines=2 host_pgs=97280
  stats part=0 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=1 host_pgs=214736 gc_pgs=496156 gc_cnt=2396 free_lines=2
  stats part=2 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  stats part=3 host_pgs=214563 gc_pgs=493534 gc_cnt=2385 free_lines=2
  (kernel) [90610.168654] pci_bus 0001:10: busn_res: [bus 10-ff] is released
  (kernel) [90610.189022] NVMeVirt: Virtual NVMe device closed
```

### 11.5.7 1 초 평균 대역폭 시계열 (MiB/s, t=1..60 s, fio_bw.1.log 의 0.5 s 값 두 개 평균)
형식: variant map bs rep | gc_onset_s | 값 60개 (공백 구분)
```
wbuffix 4k 4k r1 | 6.277 | 2011 2012 1999 2009 2006 2057 208 130 151 159 173 173 170 194 170 152 179 172 167 165 171 176 188 182 226 196 221 173 210 190 175 199 213 194 207 206 209 215 244 221 231 246 256 266 292 305 346 358 431 483 571 1401 137 132 134 158 152 169 174 173
wbuffix 4k 4k r2 | 6.342 | 1991 1987 1988 1985 1984 2020 335 128 147 159 166 159 161 187 178 166 174 178 169 178 176 185 182 205 174 179 194 197 183 186 212 216 193 212 210 235 214 218 234 222 230 263 259 272 282 312 326 353 403 505 661 1339 121 131 136 149 173 166 185 186
wbuffix 4k 4k r3 | 6.333 | 1992 1988 1992 1986 1988 2028 321 130 144 152 168 166 169 209 168 181 164 179 181 169 204 184 174 181 223 222 208 215 199 198 205 188 194 207 201 233 237 218 229 250 239 256 272 283 310 328 375 419 459 476 787 896 129 137 155 179 164 199 181 184
wbuffix 4k 8k r1 | 5.737 | 2217 2212 2212 2215 2210 1183 126 142 156 178 177 179 238 192 180 178 225 192 218 203 178 221 162 157 210 207 178 248 190 219 289 277 209 227 259 362 275 332 257 398 400 338 412 712 646 1138 689 135 152 162 194 193 234 204 197 184 200 220 223 198
wbuffix 4k 8k r2 | 5.740 | 2217 2212 2212 2215 2211 1183 128 142 161 179 190 200 229 175 209 209 179 210 238 211 177 184 259 246 242 226 185 180 258 225 221 224 217 218 269 287 342 254 315 293 303 333 435 605 739 1394 252 134 146 171 185 209 188 171 191 207 190 189 227 239
wbuffix 4k 8k r3 | 5.739 | 2217 2212 2212 2215 2211 1182 128 140 159 183 186 185 229 191 189 184 211 208 157 182 230 211 256 231 180 226 199 176 181 229 186 194 220 208 234 275 293 308 311 330 301 509 499 474 552 790 1140 122 140 158 175 194 177 225 199 190 180 209 232 223
wbuffix 4k 16k r1 | 5.696 | 2234 2233 2233 2226 2233 1098 128 145 164 185 212 231 221 204 215 228 234 238 239 251 254 260 277 278 292 300 324 325 348 372 395 420 462 516 577 694 921 1532 124 140 158 178 200 226 246 201 211 223 232 242 243 244 253 261 270 284 288 301 310 330
wbuffix 4k 16k r2 | 5.693 | 2234 2233 2233 2233 2233 1090 130 146 164 188 209 232 222 204 216 232 233 240 240 253 257 261 277 279 296 304 319 333 350 371 395 425 466 512 585 706 945 1454 127 141 159 179 202 226 239 201 215 223 232 237 247 244 248 263 270 283 288 303 311 328
wbuffix 4k 16k r3 | 5.693 | 2234 2233 2233 2233 2233 1090 130 146 163 187 211 232 222 204 216 228 237 240 241 252 255 262 277 280 296 302 319 334 348 370 391 420 471 508 584 697 938 1481 127 141 157 176 205 226 240 200 211 227 232 236 242 247 247 260 274 278 294 301 310 329
wbuffix 4k 32k r1 | 5.693 | 2234 2233 2233 2233 2233 1098 137 151 166 188 214 231 222 208 215 227 234 239 244 254 256 264 279 285 297 303 322 329 357 374 398 432 471 525 601 724 1023 1291 130 147 164 184 205 233 227 204 216 226 234 245 243 247 256 268 271 284 291 309 312 331
wbuffix 4k 32k r2 | 5.693 | 2233 2233 2233 2233 2233 1098 137 151 169 188 211 231 222 208 215 225 236 238 244 250 260 264 280 283 296 303 322 331 357 371 400 425 474 514 604 726 1008 1312 130 147 164 184 205 228 232 204 216 228 233 243 244 248 256 266 271 276 295 304 315 332
wbuffix 4k 32k r3 | 5.693 | 2234 2233 2233 2233 2233 1098 137 150 166 188 215 231 222 207 215 225 234 241 244 249 260 265 275 286 293 307 322 330 356 372 397 427 473 518 600 723 1008 1318 132 144 162 183 204 230 229 204 216 226 234 241 244 248 259 264 271 284 290 307 310 330
wbuffix 4k 64k r1 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 214 236 221 209 221 225 238 237 251 256 269 265 281 290 303 307 319 351 364 384 413 443 499 547 649 833 1437 590 147 161 178 198 217 233 214 212 222 229 242 242 252 253 265 272 279 292 299 313 331 344
wbuffix 4k 64k r2 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 216 234 221 211 220 225 238 237 251 256 269 266 280 290 303 310 322 345 364 384 414 449 493 547 655 826 1444 582 147 161 178 198 221 222 222 212 222 231 241 242 252 258 260 273 284 287 299 314 329 344
wbuffix 4k 64k r3 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 214 236 221 213 218 225 238 237 251 256 269 265 280 290 303 310 322 345 364 384 413 448 494 547 654 828 1444 583 147 161 178 198 221 229 214 213 222 233 238 246 248 258 260 273 284 291 298 314 326 349
wbuffix 16k 4k r1 | 5.915 | 536 533 538 536 535 430 179 162 175 166 152 144 139 131 119 123 111 118 104 101 103 97 91 92 95 88 80 86 79 81 76 72 75 69 76 68 66 67 65 64 66 61 60 62 60 60 57 59 57 58 57 58 56 61 56 59 56 53 57 51
wbuffix 16k 4k r2 | 5.911 | 536 534 538 536 535 430 176 165 176 165 153 140 137 132 121 121 111 117 106 101 104 97 95 90 93 93 82 81 84 77 79 73 70 70 71 70 67 66 65 63 64 67 61 64 61 61 61 61 61 57 58 53 59 55 55 52 55 53 56 52
wbuffix 16k 4k r3 | 5.914 | 536 533 538 536 535 430 176 163 176 163 152 145 141 133 118 126 105 110 104 102 100 97 93 87 93 93 83 83 80 82 76 73 73 75 68 71 66 65 72 65 66 63 62 63 58 61 57 58 57 59 62 55 54 56 53 59 56 54 57 53
wbuffix 16k 8k r1 | 5.905 | 1071 1071 1076 1075 1071 834 324 286 283 267 247 230 198 204 189 178 184 156 150 149 146 130 123 126 121 120 117 112 108 112 102 100 110 102 103 87 94 87 93 82 91 77 77 79 77 80 81 83 82 82 79 81 78 78 85 79 82 85 80 79
wbuffix 16k 8k r2 | 5.905 | 1071 1071 1076 1075 1072 834 325 289 285 266 246 225 201 200 193 176 186 157 150 143 146 130 128 124 124 114 122 110 113 116 98 107 97 100 98 98 97 95 87 90 84 83 83 83 77 87 78 78 79 77 79 79 84 82 80 80 84 79 82 80
wbuffix 16k 8k r3 | 5.905 | 1071 1071 1076 1076 1071 834 324 290 286 266 244 226 201 202 191 178 184 157 150 144 143 128 129 129 124 112 115 116 115 99 111 106 104 101 91 97 90 90 90 87 83 83 83 80 79 85 79 79 76 82 81 82 82 81 80 81 80 84 82 77
wbuffix 16k 16k r1 | 5.921 | 2141 2141 2143 2149 2140 1512 136 136 147 157 171 166 169 175 163 160 174 177 176 194 185 191 176 198 197 196 176 186 196 207 207 203 212 218 219 218 223 236 242 244 252 268 282 323 315 370 379 436 524 698 1201 130 139 147 155 172 178 174 183 170
wbuffix 16k 16k r2 | 5.921 | 2141 2141 2143 2149 2140 1512 136 136 147 161 170 162 179 185 178 178 169 179 183 203 184 179 189 190 206 191 191 186 195 194 223 201 226 209 215 236 242 226 240 245 254 265 297 300 323 362 390 460 573 874 889 130 142 152 161 169 177 179 183 176
wbuffix 16k 16k r3 | 5.921 | 2140 2141 2142 2149 2140 1512 136 136 149 158 176 173 186 178 192 168 173 182 177 185 187 196 183 189 193 207 209 205 201 204 209 203 212 219 234 231 224 242 254 259 257 270 288 311 347 387 413 532 675 1344 131 135 148 167 160 168 177 187 177 180
wbuffix 16k 32k r1 | 5.843 | 2176 2175 2169 2167 2173 1377 138 148 159 175 198 194 202 195 198 214 202 200 220 215 219 227 212 219 230 234 256 213 232 232 261 244 254 232 279 264 293 300 328 399 417 426 491 598 1273 541 141 154 170 179 199 205 184 193 187 186 223 213 214 193
wbuffix 16k 32k r2 | 5.846 | 2176 2175 2169 2167 2169 1382 138 146 162 175 194 198 207 190 194 212 200 214 191 209 223 212 194 225 224 192 234 239 249 234 254 269 273 290 264 285 315 311 346 408 399 533 740 875 1078 135 150 164 172 186 189 207 191 198 189 202 219 199 213 220
wbuffix 16k 32k r3 | 5.843 | 2176 2175 2169 2167 2173 1379 139 146 159 175 198 194 207 190 198 210 197 205 181 205 220 217 189 235 213 240 240 222 223 247 244 261 287 230 299 296 288 348 349 389 378 471 531 776 1451 135 143 158 176 189 192 209 196 201 194 197 205 206 225 207
wbuffix 16k 64k r1 | 5.693 | 2235 2232 2233 2233 2233 1103 144 156 174 193 216 234 221 213 217 225 238 237 251 258 267 270 276 290 303 310 322 345 364 387 410 449 493 551 657 821 1451 576 147 161 179 197 221 229 216 211 221 230 241 241 252 254 268 274 274 292 303 311 329 345
wbuffix 16k 64k r2 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 218 231 221 214 217 225 237 237 251 258 266 270 276 290 303 310 322 345 364 388 409 449 493 548 660 821 1450 577 147 161 178 198 221 229 215 211 222 233 238 247 246 258 266 268 284 294 300 309 329 349
wbuffix 16k 64k r3 | 5.693 | 2235 2233 2233 2233 2233 1102 144 156 174 193 218 231 221 214 217 228 234 241 246 261 264 270 280 286 303 310 322 345 364 392 406 449 493 558 651 826 1455 566 147 161 181 199 217 234 213 208 226 229 241 243 250 253 269 269 281 295 300 316 331 343
wbuffix 32k 4k r1 | 6.061 | 261 260 259 261 260 235 101 89 88 85 81 78 81 71 69 64 62 59 55 58 53 53 49 51 47 47 46 45 43 44 41 40 43 40 37 37 39 38 36 36 37 36 36 34 34 35 33 32 34 33 32 30 32 30 31 34 31 32 30 29
wbuffix 32k 4k r2 | 6.061 | 261 260 259 261 260 235 101 89 88 84 82 80 80 70 70 64 62 58 55 59 51 53 50 52 49 50 46 45 42 44 41 43 42 39 38 37 38 38 36 36 36 35 35 34 34 35 34 32 33 30 32 32 32 31 30 30 30 29 31 29
wbuffix 32k 4k r3 | 6.061 | 261 260 259 261 260 235 101 89 86 84 81 80 82 70 70 64 63 57 57 57 53 52 51 52 47 48 47 45 44 43 42 41 40 39 39 37 38 37 37 35 34 35 34 35 33 36 33 34 34 33 33 31 30 32 32 33 32 31 30 31
wbuffix 32k 8k r1 | 6.067 | 521 520 519 521 521 472 182 183 178 153 164 162 155 132 123 125 118 107 112 111 102 102 96 92 91 88 87 86 87 80 80 79 78 74 73 71 70 64 66 68 64 66 63 66 62 59 60 61 59 60 63 60 60 59 56 56 55 56 57 58
wbuffix 32k 8k r2 | 6.067 | 521 520 519 521 522 472 181 181 178 155 164 162 155 131 121 128 117 109 107 107 104 101 96 93 89 86 89 84 85 78 79 75 76 70 71 69 72 70 72 67 68 62 68 65 64 63 61 61 62 59 62 61 58 57 59 56 58 57 58 56
wbuffix 32k 8k r3 | 6.067 | 521 520 519 521 522 472 181 182 179 154 167 161 157 131 121 129 117 109 110 109 103 100 95 93 89 86 90 84 82 79 76 76 75 72 74 75 69 68 71 67 67 66 65 63 65 66 60 61 63 63 65 62 58 57 57 55 56 56 56 58
wbuffix 32k 16k r1 | 6.064 | 1041 1042 1040 1042 1045 952 363 313 302 273 240 234 216 207 185 189 166 157 157 148 139 131 126 138 128 115 119 115 109 111 105 104 98 103 102 95 95 90 92 88 82 83 82 80 83 82 84 85 82 82 83 82 78 82 84 84 80 82 83 78
wbuffix 32k 16k r2 | 6.064 | 1041 1042 1040 1042 1044 952 363 313 301 274 243 230 214 216 191 182 170 157 156 149 138 142 139 132 116 125 127 119 120 108 105 102 99 103 99 92 92 96 86 83 84 80 83 81 80 84 84 81 86 84 85 82 84 82 80 82 82 81 83 86
wbuffix 32k 16k r3 | 6.064 | 1041 1042 1040 1042 1045 952 363 314 302 272 243 228 219 211 181 184 168 157 159 146 146 140 131 125 122 122 124 120 113 112 113 104 106 99 101 96 97 89 90 87 83 79 83 82 82 89 78 81 84 84 84 80 86 80 81 82 81 81 79 79
wbuffix 32k 32k r1 | 6.096 | 2084 2079 2068 2079 2082 1805 138 143 145 155 165 172 174 193 179 169 170 181 187 188 187 192 200 196 199 194 207 216 220 224 222 221 240 235 230 247 242 248 252 270 280 293 318 359 389 439 503 620 1426 184 141 148 154 163 172 176 174 180 177 183
wbuffix 32k 32k r2 | 6.096 | 2084 2079 2068 2079 2082 1805 138 143 149 154 166 176 177 176 185 182 172 190 185 185 192 188 198 194 198 196 207 215 224 206 221 225 243 230 239 247 278 255 266 270 271 298 321 357 385 420 485 681 1398 131 136 149 162 166 176 179 182 174 181 174
wbuffix 32k 32k r3 | 6.096 | 2084 2079 2068 2079 2082 1804 138 143 149 157 163 176 177 178 184 180 173 187 186 183 194 191 185 194 196 198 206 207 217 218 221 220 218 235 234 245 245 263 274 287 303 290 316 339 402 422 486 655 1439 140 139 150 159 163 168 182 186 181 173 170
wbuffix 32k 64k r1 | 5.972 | 2130 2125 2115 2124 2120 1608 147 150 171 178 190 176 207 200 186 198 200 220 208 219 221 218 235 261 210 260 229 260 240 272 269 280 272 264 281 294 319 348 345 484 544 613 894 1236 141 149 166 165 194 208 194 211 187 208 203 213 220 214 220 216
wbuffix 32k 64k r2 | 5.973 | 2130 2125 2115 2124 2120 1609 147 150 171 178 190 176 207 200 186 198 198 219 210 219 221 216 232 265 210 259 230 261 240 270 271 278 274 262 282 294 320 346 338 489 548 607 888 1247 141 150 164 167 194 208 192 211 187 208 204 212 221 212 222 217
wbuffix 32k 64k r3 | 5.973 | 2130 2125 2115 2124 2120 1609 147 150 167 182 190 176 207 200 186 198 197 220 214 215 221 216 232 266 210 256 232 261 241 270 271 277 274 264 281 294 319 346 342 485 548 613 889 1240 142 149 166 165 194 208 194 211 188 207 203 217 216 214 220 216
```

### 11.5.8 실험 전후 환경 차이 (env_before vs env_after_* 의 마지막 스냅샷; 날짜·부하·여유 메모리 줄 제외)

### 11.5.9 run_all 로그 끝 40 줄 (원본 로그, 시각은 KST 로 변환)
```
```

<!-- AUTO-RESULTS-END -->

---------------------------------------------------------------------------------------------------

## 12. 그래프 도구 (exp/plot.py) 사용법

- 실행: 묶음에서는 `cd repo/exp`, 실험 서버에서는 `cd <repo>/exp` 한 뒤 `./.venv/bin/python plot.py <cmd> [옵션]`(venv 만드는 법은 H 절).
  - 결과 폴더를 직접 읽으므로 부분 데이터에도 쓸 수 있다. analyze.py 의 collect/aggregate 를 그대로 쓴다.
  - --exp 를 주지 않으면 results/main_* 중 이름순 마지막(= main_20261008)을 쓴다. 주 데이터셋은 `--exp results/main3x3_20261008` 로 지정한다.
  - --variant 기본값은 「있는 것 전부」다. main3x3 에서는 wbuffix_nodrop·wbuffix_drop 이 변형처럼 다뤄진다. compare 는 drop 과 nodrop 을 겹쳐 그린다.
  - 크기 목록은 결과에 있는 것만 쓴다(main3x3 이면 4K·16K·32K).
- 명령:
  - list — 완료된 회차 수와 지표 목록
  - bs — 지표를 bs 에 따라, 매핑 단위별 선 하나씩(변형마다 패널, 평균±표준편차)
  - map — 지표를 매핑 단위에 따라, bs 별 선
  - heatmap — 매핑×bs 열지도
  - ts — 0.5 s 시계열(--ts-metric bw|iops|clat|lat, 점선 = 첫 GC)
  - compare — base vs wbuffix(매핑 단위별 패널, 회색 = bs < 매핑)
  - all — 표준 묶음을 results/<EXP>/plots/ 에 만든다
- 옵션: --exp, --variant base,wbuffix, --metric(지표 이름 = summary_runs.csv 열), --maps 4k,128k, --bss 4k, --reps 1,2,3, --logy, --out 파일, --show(디스플레이가 있을 때 창으로 보기).
- 지표: bw_MiBps, iops, clat_mean_us, clat_p50_us, clat_p99_us, clat_p999_us, lat_mean_us, bw_first10s_MiBps, bw_last20s_MiBps, gc_onset_s, bw_pre_gc_MiBps, bw_post_gc_MiBps, waf_gc, waf_total, gc_cnt, written_GiB, fill_ratio, chmodel_msgs.
- 순차 쓰기 실험: `--exp results/seq3x3_20261008`. 변형은 wbuffix·merge 이고, compare 는 두 모델을 겹쳐 그린다.
- 랜덤 쓰기 bs 5 단계: `--exp results/rand3x5_20261008`(매핑 4K·16K·32K × bs 4K·8K·16K·32K·64K, 변형 wbuffix 하나). 새로 잰 회차만 보려면 `--exp results/randbs_20261008` 을 쓴다.
- exp/make_gallery.py (19:0x KST 추가): `python3 make_gallery.py results/<EXP> [out.html]` 은 analysis/·plots/ 의 모든 PNG 를 한 HTML 에 넣는다. 그림은 data URI 로 들어가고 주제별로 묶이며 한국어 설명이 붙는다. 기본 출력은 results/<EXP>/gallery_<EXP>.html 이다.
- 색: 범주색 고정 순서 #2a78d6 #eb6834 #1baf7a #eda100 #e87ba4 #008300 #4a3aa7 #e34948 (4K→128K 순). 열지도는 단일 파랑 계열. 그림 글자는 영어다(matplotlib 기본 글꼴에 한글이 없다).

---------------------------------------------------------------------------------------------------

## 13. 다음 Claude 를 위한 주의 사항

- 응답·보고는 한국어로만 한다.
- (아래 sudo·push·tmux 관련 항목은 실험 서버에서 작업하는 Claude 에게만 해당한다. 묶음을 받은 Claude 는 서버에 접근할 수 없다.)
- sudo 비밀번호는 사용자가 한 번 알려 줬지만 기록하지 않았다. Claude 가 그 비밀번호를 명령에 넣는 것은 자동 모드 분류기가 막는다(1.18). sudo 가 필요한 설치·제거는 사용자에게 명령을 주고 직접 실행해 달라고 한다.
- sudoers 규칙: 18:33 제거 → 20:17 순차 쓰기 실험을 위해 사용자가 다시 설치(6.4 절; 지금 파일은 새 경로·nomerges 포함) → 21:34 사용자가 제거 → 22:11 랜덤 bs 8K·64K 실험을 위해 사용자가 다시 설치 → 23:08 사용자가 제거. 지금은 없다. 서버에서 또 실험하려면 사용자에게 설치를 부탁한다(`sudo rm` 은 규칙에 없다).
- 실험 대상·설계를 바꾸는 결정(예: base 를 돌릴지)은 반드시 먼저 사용자에게 묻는다(1.15).
- base/wbuffix 를 설명할 때는 비유 대신 1.14 절의 사실로 설명한다. NAND 로 보내는 시점은 같고, 다른 것은 쓰기 버퍼 장부(back-pressure)뿐이다.
- GitHub push 는 사용자의 forwarded ssh-agent 소켓이 필요하다(`ls /tmp/ssh-*/agent.*`). 사용자가 접속해 있지 않으면 push 할 수 없다.
- 실험 중(tmux ksc2026)에는:
  - run_experiment.sh·run_all.sh 를 같은 파일로 덮어쓰지 않는다(bash 가 실행 중 읽음).
  - CPU 0–2 에서 무거운 작업을 하지 않는다(fio 가 그곳에서 돈다). 필요하면 nice -n 19.
  - nvmev 모듈을 손대지 않는다.
- 결과를 해석할 때:
  - base 의 bs < 매핑 단위 15 조합은 8.1 절 때문에 wbuffix 결과를 기준으로 본다.
  - 64K/128K 는 8.2 절의 NAND 변화가 섞여 있다.
  - 순차 쓰기에서 bs < 매핑 단위인 wbuffix 결과는 NVMeVirt 의 「병합 없음」 한계(8.6 절)를 그대로 반영한다. 실제 SSD 에 가까운 값은 merge 모델이다.
  - 60 s 평균에는 GC 이전 구간과 fio randommap 주기 현상이 섞여 있다.
- 사용자에게 아직 말하지 않았거나 결정이 필요한 후속 후보:
  - RMW 읽기 모델 추가
  - 64K/128K 에서 tPROG 를 비례로 키운 대조 실험
  - 사전 채움 후 정상 상태 측정(설정조사 보고서 추천 300 s)
  - norandommap / random_distribution 변경
  - RocksDB(db_bench) 응용 실험

---------------------------------------------------------------------------------------------------

## 갱신 이력
(시각은 모두 2026-10-08 KST)
- 2026-10-08 14:40경 최초 작성(본 실험 base 진행 중, 약 17/108).
- 2026-10-08 14:50 10 절에 첫 중단(base map32k_bs16k_r1 장치 실패)과 재개(wbuffix 먼저) 기록.
- 2026-10-08 15:25 감사 워크플로 완료 반영(9 절), GC 이전 처리량 정정과 IRQ 15/cpu5 사실(8.3 절) 추가. 저장소에 credential(sudo 비밀번호·서버 IP 문자열)이 없는지 grep 으로 검사 → 없음.
- 16:05 설계 변경(1.7)·인계 방식(1.8)·H 절·0 절 재작성. 주 데이터셋 = main3x3_20261008.
- 16:04 **커밋 재작성** (a93ef76 committer 시각 16:04:44 KST): 첫 중간 묶음(16:03)을 확인하다가, 커밋 1d6cd03 에 들어간 이 파일의 한 줄(15:25 에 「검사 명령」을 적으며 sudo 비밀번호·서버 IP 문자열을 그대로 씀)을 발견했다.
  - 그 묶음(ksc2026_handoff_20261008_0703_mid.tgz — 이름의 0703 은 당시 UTC 표기 = 16:03 KST)은 지웠고 전달 전이었다.
  - 1d6cd03 은 push 전이었으므로(origin/main = 5769378) 그 줄만 고쳐 amend → **a93ef76** 이 되었다. 코드·스크립트는 같고 이 파일 한 줄만 다르다.
  - reflog expire + gc --prune=now 로 옛 커밋 1d6cd03 을 지웠다. 단 git stash pop 충돌로 인덱스 resolve-undo 기록이 옛 파일 blob 0abc072(비밀번호 줄 포함)를 붙잡고 있어 그 blob 은 .git 안에 남아 있었다(어느 ref 에서도 닿지 않아 push·repo.gitbundle 에는 들어가지 않음). 18:27 KST 에 `rm .git/index && git reset -q` 후 reflog expire·gc --prune=now 로 지우고, 모든 git 객체를 검사해 credential 이 없음을 확인했다.
  - main3x3_20261008 의 처음 4 회차(map4k_bs4k_r1·map4k_bs16k_r1 의 nodrop·drop) meta.txt 와 wbuffix_*/git_head.txt·env_before/08_nvmevirt_git.txt 에 적힌 1d6cd03 은 a93ef76 과 같은 코드다.
  - make_handoff.sh 가 git 이력 전체(`git log -p --all`)도 검사하도록 고쳤다.
- 16:10 사용자 지시(1.9)에 따라 서술 시각을 UTC → KST 로 일괄 변환했다(이 이력의 앞 항목들도 KST 로 바뀌었다).
- 16:10 사용자 지시(1.10)에 따라 인계 묶음 안의 시각도 KST 로 쓰도록 고치고, 묶음을 KST 이름으로 다시 만들었다(ksc2026_handoff_20261008_1610_mid.tgz, 16:10:58 KST).
- 17:10 실험 완료·결과 요약(0 절)·이동·삭제(10.3 절) 반영.
- 17:24 진행 상태(0 절)·정리 기록(10.3 절) 갱신, 인계 묶음 postexp(ksc2026_handoff_20261008_1724_postexp.tgz) 생성.
- 18:3x 검증 워크플로 지적 반영, 보안 조치(묶음 삭제·검사 패턴·옛 blob·이메일 제거를 위한 커밋 재작성 2a462a3→949ae38, a93ef76→e598e75), sudoers 제거(18:33), 최종 문서 생성, 커밋·태그·push(10.3 절).
- 18:36 push 확인(main = 태그 ksc2026-final = c742c67), 최종 인계 묶음 생성.
- 19:0x 그래프 위치 안내, make_gallery.py 추가(1.13).
- 19:1x–19:2x base/wbuffix 설명 정정과 base 를 미리 묻지 않고 돌린 일에 대한 답(1.14·1.15).
- 19:53–20:23 순차 쓰기 실험 준비: 사용자 선택(1.16), 병합 모델 WBUF_MERGE 작성(5.6)과 코드 검토 워크플로(9.1), 스크립트 확장(6.6), 커밋 66446ea, sudoers 재설치(사용자, 1.18), 사전 점검(7.1)과 블록 계층 병합 발견(8.5).
- 20:23–21:26 순차 쓰기 실험(10.4). 실험 중 이 파일의 1.11–1.18, 5.6, 6.6, 7.1, 8.5–8.6, 9.1 을 쓰고, docx 생성기에 8 장(순차 쓰기)을 넣었다.
- 21:3x 순차 쓰기 결과 반영: 0 절, 8.7, 10.4, 11.3(자동 생성). env_after 중복 처리.
- 21:34 순차 쓰기 실험 후 sudoers 제거(사용자). 22:08 사용자 요청으로 랜덤 쓰기 bs 8K·64K 실험을 추가했다(1.20, 6.7). 22:11:48 커밋 a86fc87(순차 쓰기 결과·랜덤 bs 스크립트; 검증 반영 전). 22:12–22:17 순차 쓰기 기록 검증 워크플로의 지적 39 건을 반영했다(9.2; 커밋 403a6ae 에 들어감).
- 22:11–22:33 랜덤 쓰기 bs 8K·64K 실험(10.5). 22:3x 결과 반영: 0 절, 8.8, 10.5, 11.4·11.5(자동 생성), docx 9 장(랜덤 bs 8K·64K; 「실험 후 상태와 정리」는 10 장이 됨).
- 23:08 sudoers 제거(사용자), ssh -A 재접속. 23:1x 랜덤 bs 8K·64K 기록 검증 워크플로의 지적 30 건 반영(9.3; make_handoff.sh 이력 검사 fail-open 수정 포함). 23:2x 최종 docx(92 쪽), 커밋, 태그 ksc2026-v2, push, 최종 인계 묶음(10.5 절 끝).
