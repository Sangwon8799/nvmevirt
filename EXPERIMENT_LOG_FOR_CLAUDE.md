# KSC2026 NVMeVirt FTL 매핑 단위 실험 — 전체 기록 (Claude 인계용)

이 파일은 다른 Claude 세션이 이 논문 실험의 진행 상황을 완전하고 정확하게 이해하도록 쓴 기록이다. 사람이 읽기 좋은 형식보다 정확성과 빠짐없음을 우선한다. 사실은 파일 경로·커밋·로그 줄·숫자로 근거를 붙였다. 「추정」으로 표시하지 않은 문장은 확인된 사실이다.

- 작성: Claude Code (모델 Claude Opus 5.5, 세션 ID 13edeb42-0011-48bf-800d-a7f7e0251b76). 작업 디렉터리 /home/dccearth/jsw. 서버 dccearth.
- 작성 시작: 2026-10-08 05:40 UTC (서버 시계 UTC, +00:00). 마지막 갱신: 맨 아래 「갱신 이력」 참고.
- 사용자: GitHub 계정 Sangwon8799 (git user.email ekfghfl@naver.com). 사용자를 지칭할 때는 they/them.
- 사용자 선호: 2026-10-08 05:21경 「앞으로는 한국어로만 답변해주고 보고해줘.」 → 모든 응답·보고는 한국어. 메모리 파일 /home/dccearth/.claude/projects/-home-dccearth-jsw/memory/korean-only-replies.md 에 저장됨.

---------------------------------------------------------------------------------------------------

## 0. 현재 상태 요약 (STATUS)

- 상태: 본 실험(main_20261008)이 실행 중 또는 완료. 정확한 상태는 다음으로 확인한다.
  - `tmux ls` (세션 ksc2026)
  - `tail /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/run_all_main_20261008.log`
  - `ls /home/dccearth/jsw/KSC2026/nvmevirt/exp/results/main_20261008/{base,wbuffix}/ | grep -c _r` (각 108 이면 완료)
- 실험 행렬: 매핑 단위 {4k,8k,16k,32k,64k,128k} × fio bs {4k,8k,16k,32k,64k,128k} × 3 회. 변형 2 개(base, wbuffix) → 216 회. 회차당 약 70 s, 전체 약 4.2 시간.
- 일정: 2026-10-08 05:20:28 UTC 시작(모듈 빌드). base 측정 1 회차 05:21:02. base 21 회차(map32k_bs16k_r1)에서 장치 실패로 05:46:57 중단 → 스크립트 수정 후 05:49:13 재개. 재개 순서는 wbuffix 108 회 → base 나머지 87 회(10 절). wbuffix 종료 약 07:55, base 종료는 실패 회차 수에 따라 약 09:40–10:30 UTC 로 예상.
- 최종 산출물(완료 후):
  - 실험 기록 Word 문서: `/home/dccearth/jsw/KSC2026/nvmevirt/exp/report/KSC2026_NVMeVirt_매핑단위_실험기록.docx`. 같은 파일을 /home/dccearth/jsw/KSC2026/산출물/ 에도 복사할 예정.
  - 결과 CSV: `exp/results/main_20261008/analysis/summary_runs.csv`(회차별), `summary_agg.csv`(조합별 평균·표준편차·최소·최대)
  - 그림: `exp/results/main_20261008/analysis/fig_*.png` (analyze.py), `exp/results/main_20261008/plots/*.png` (plot.py all)
  - GitHub: git@github.com:Sangwon8799/nvmevirt.git, 브랜치 main
- 이 파일 맨 아래 「11. 결과」에는 실험이 끝난 뒤 자동 생성한 전체 수치가 들어간다(AUTO-RESULTS 표지 사이).

---------------------------------------------------------------------------------------------------

## 1. 사용자 지시 원문과 이행 상태 (시간순, 이 세션)

### 1.1 첫 지시 (2026-10-08 04:4x UTC) — 원문 그대로

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
| 처음 만든 nvmevirt 폴더를 GitHub 에 | origin = git@github.com:Sangwon8799/nvmevirt.git, main 에 push 했다(05:20 경, 커밋 5769378 까지). 결과·문서는 실험 후 추가로 push 한다. | 코드 완료, 결과는 완료 후 |
| mapping size 4k–128k | `make MAPPING_UNIT=<bytes>` 로 매핑 단위별 모듈을 빌드한다. ssd.c 의 secs_per_pg = MAPPING_UNIT / LBA_SIZE | 완료 |
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
| 전 과정 .docx 기록 | exp/report/make_report.py 가 결과로부터 docx 를 생성한다. 실험 후 최종 생성·렌더링 확인 예정 | 진행 중 |
| fio 블록 크기 | 지시에 명시되지 않았다. 연구 계획 문서의 「randwrite 4k, 8k, 16k, 32k, 64k, 128k」에 따라 6 개 모두 측정하기로 결정했다(묻지 않음). | 완료 |

### 1.2 Claude 가 물은 것과 사용자의 답 (AskUserQuestion, 04:5x UTC)

- Q1 sudo 방식 → 사용자 답: 「NOPASSWD 규칙 추가 (Recommended)」
- Q2 GitHub 인증(서버에 키·gh 없음) → 답 원문: 「ssh config에 agent forwarding으로 github 정보를 보내고 있어. 이거 활용할 수 있어?」
  - 확인 결과 /tmp/ssh-UN8QkXPn5f/agent.4695 (사용자의 pts/0 SSH 세션)에 ed25519 키 2 개가 있었다. 하나는 ekfghfl@naver.com, 다른 하나는 dccearth_gateway_key. `SSH_AUTH_SOCK=/tmp/ssh-UN8QkXPn5f/agent.4695 ssh -T git@github.com` → "Hi Sangwon8799! You've successfully authenticated". Claude 의 Bash 환경에는 SSH_AUTH_SOCK 이 없으므로 git 명령마다 SSH_AUTH_SOCK=<소켓> 을 붙여야 한다. 소켓 경로는 사용자가 다시 접속하면 바뀐다(`ls /tmp/ssh-*/agent.*` 로 찾는다).
- Q3 push 대상(공개 목록에 Sangwon8799/nvmevirt 없음) → 답 원문: 「nvmevirt 이름으로 새로 만들게. 이전 기록은 잊어.」 → 사용자가 빈 저장소를 만들었다. `git ls-remote` 결과가 비어 있어(exit 0) 빈 저장소임을 확인한 뒤 main 을 push 했다. 예전 저장소의 map4k–map128k 브랜치 이력(2.3 절)은 무시한다.

### 1.3 두 번째 메시지 (05:0x UTC)

- 원문: 「sudo 비밀번호 줄테니 그냥 알아서 진행해. 비밀번호 <생략> 이야.」 — **비밀번호는 어디에도 기록하지 않는다**(이 파일·스크립트·메모리 모두). 사용처는 sudoers 규칙 설치 2 번(05:06, 05:10)과 dmidecode 실행 1 번(DIMM 정보 기록, 05:2x)뿐이다. `sudo -S` 로 stdin 에 넘긴 뒤 바로 `sudo -k` 했다. 나머지 판단(base/wbuffix 두 변형 실행, GC_STATS 계측 사용)은 이 「알아서 진행」 지시에 따라 Claude 가 정했다.

### 1.4 세 번째 메시지 (05:21경)

- 원문: 「앞으로는 한국어로만 답변해주고 보고해줘.」 → 메모리에 저장했다.

### 1.5 네 번째 메시지 (05:3x UTC) — 이 파일을 만든 계기

- 원문: 「그래프로 확인할 수 있도록 하는 코드도 만들어주고, 다른 Claude가 이 논문의 진행 상황을 완전하고 정확하게 이해할 수 있도록 아주 상세한 기록을 적은 `.md` 파일도 만들어줘. 길이 제한은 없고, 내가 지시한 것을 포함하여 실험의 시작과 끝까지 진행되면서 측정한 것, 설정을 바꾼 것, 결과 등등 모든 것들을 아주 상세히 기록해줘. 사람이 볼 게 아니기 때문에 가독성은 신경쓰지 말고 내용을 정확히 전달할 수 있도록 해줘.」
- 이행:
  - exp/plot.py — 명령줄 그래프 도구(8 절)
  - 이 파일 — /home/dccearth/jsw/KSC2026/nvmevirt/EXPERIMENT_LOG_FOR_CLAUDE.md, git 으로 관리하며 push 된다.

### 1.6 다섯 번째 메시지 (2026-10-08 06:3x UTC, 본 실험 진행 중)

- 원문: 「실험이 끝나면 nvmevirt 폴더 위치를 ~/jsw로 옮겨주고 ~/jsw에 있는 ~/jsw/exp 폴더는 내용물을 포함해서 모두 삭제해줘.」
- 계획(실험 종료 후):
  - /home/dccearth/jsw/KSC2026/nvmevirt → /home/dccearth/jsw/nvmevirt 로 이동
  - /home/dccearth/jsw/exp(2.2 절의 이전 작업 폴더) 전체 삭제. 삭제 전에 그 안의 iodepth 결과 수치를 2.2 절에 옮겨 적는다.
  - 저장소 안 upstream_tmp/ 삭제, exp/.venv 재생성(절대경로), KSC2026/EXPERIMENT_LOG_FOR_CLAUDE.md 심볼릭 링크 갱신
  - 문서의 경로를 갱신하고 이동 사실을 기록한다.
- 이행 결과는 「갱신 이력」과 14 절에 적는다.

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

- /home/dccearth/jsw/before.txt, after.txt — insmod 전후 `ls -l /dev/nvme*` (after 에 /dev/nvme1, /dev/nvme1n1 이 생김). 2026-10-07 작성. 06:4x 확인 때 두 파일이 /home/dccearth/jsw 에 없었다(디렉터리 mtime 06:42). Claude 가 지운 것이 아니며 사용자가 정리한 것으로 보인다. 내용(세션 시작 때 읽음):
  - before.txt: /dev/nvme0 (241,0), /dev/nvme0n1 (259,0), nvme0n1p1 (259,1), nvme0n1p2 (259,2), /dev/nvme-fabrics (10,261) — 날짜 Sep 30/Oct 1
  - after.txt: 위 + /dev/nvme1 (241,1, Oct 7 12:28), /dev/nvme1n1 (259,3, Oct 7 12:28)
- /home/dccearth/jsw/exp/ (이전 실험 폴더, KSC2026 밖에 있음. 이번 실험과 별개이며 그대로 두었다):
  - jobs/randwrite.fio, results/iodepth_test/ (iodepth 1–128, 매핑 4K, bs 4K, ramp_time 10, runtime 60, 모듈 재적재 없이 연속 실행 → GC 정상 상태, filename=/dev/nvme1n1, 2026-10-08 02:33–02:41 UTC). iodepth_summary.csv 에 따르면 QD32 에서 64,041 IOPS, 250.2 MiB/s, clat 평균 498.8 µs, p99 14,352 µs이고, QD 1–128 모두 약 59–66K IOPS 다. 이 폴더는 사용자 지시(1.6)로 실험 후 삭제되므로 CSV 전문을 여기에 옮겨 둔다:
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
  - 그 저장소는 이번 세션 시점에 공개 API 에서 보이지 않았고, 사용자 지시(「이전 기록은 잊어」)에 따라 새 저장소로 대체되었다. 로컬 사본(/home/dccearth/jsw/nvmevirt)도 이미 없었다.
  - ~/.ssh 의 jsw_github_key 는 사용자가 지웠다(현재 ~/.ssh 에는 authorized_keys, 빈 config, known_hosts 만 있다).

---------------------------------------------------------------------------------------------------

## 3. 서버 환경 (exp/results/main_20261008/env_before/ 스냅샷 근거)

- 호스트명 dccearth. 메인보드 Micro-Star International Co., Ltd. MAG B760M MORTAR (MS-7E01), BIOS M.30 (05/16/2023).
- CPU: 13th Gen Intel Core i5-13600K. OS 에 보이는 CPU 는 6 개(0–5), 코어당 스레드 1, 소켓 1, NUMA 노드 1. max 5100 MHz, min 800 MHz. L1d 288 KiB, L2 12 MiB, L3 24 MiB. 원래 13600K 는 P 6 + E 8 이지만 OS 에는 6 개만 보인다(BIOS 에서 E-core/HT 를 끈 것으로 추정 — 확인 안 함).
- 메모리: DDR5-5600. Controller0-DIMMA2 8 GB Samsung M323R1GB4DB0-CWMOL, Controller1-DIMMB2 16 GB Samsung M323R2GA3DB0-CWMOL (DIMMA1·DIMMB1 은 비어 있음). 합계 24 GB, 최대 128 GB, 슬롯 4. (sudo dmidecode -t memory, env_before/12_dimm.txt — 실험 시작 후 05:2x 에 기록. 정적 정보다.)
- free -h: total 11Gi (memmap 으로 12 GiB 가 빠짐), swap 8 GiB.
- 물리 주소 맵(/proc/iomem, 4 GiB 위): 100000000-2ffffffff System RAM (4–12 GiB) / **300000000-5ffffffff Reserved (12–24 GiB, NVMeVirt 저장 공간)** / 600000000-67f7fffff System RAM (24–25.99 GiB, PCI hole 재배치분). e820 user map: [mem 0x0000000300000000-0x00000005ffffffff] reserved.
- OS Ubuntu 24.04.4 LTS (noble). 커널 6.8.0-142-generic (#142-Ubuntu SMP PREEMPT_DYNAMIC Wed Sep 2 14:24:27 UTC 2026), x86_64-linux-gnu-gcc-13 13.3.0 로 빌드됨.
- 커널 명령줄: `BOOT_IMAGE=/boot/vmlinuz-6.8.0-142-generic root=UUID=bb1b37f9-0806-4044-a2bf-5ff988ecb286 ro memmap=12G$12G isolcpus=3-5`
- /etc/default/grub: `GRUB_CMDLINE_LINUX="memmap=12G\\\$12G isolcpus=3-5"`, `GRUB_CMDLINE_LINUX_DEFAULT=""`. /sys/devices/system/cpu/isolated = 3-5.
- CPU 주파수: intel_pstate active(HWP), 모든 CPU 가 governor powersave · EPP balance_performance · no_turbo=0 (터보 켜짐), 800–5100 MHz. 바꾸지 않았다.
- THP: always [madvise] never. kernel.dmesg_restrict=1, kptr_restrict=1, numa_balancing=0, vm.swappiness=60. kernel.printk = 4 4 1 7 (콘솔 loglevel 4 → KERN_ERR 가 tty0 콘솔에 출력된다). /proc/consoles: tty0. systemd-journald 가 /dev/kmsg 를 읽는다.
- 시스템 디스크: /dev/nvme0n1 Samsung SSD 980 PRO 500GB (FW 3B2QGXA7). nvme0n1p1 1G /boot/efi, nvme0n1p2 464.7G / (루트). 실험 스크립트는 이 디스크에 절대 쓰지 않도록 검사한다.
- 소프트웨어 버전: fio-3.36 (deb 3.36-1ubuntu0.1), libaio1t64 0.3.113-6build1.1, gcc 13.3.0 (gcc-13 13.3.0-6ubuntu2~24.04.1), GNU Make 4.3 (4.3-4.1build2), linux-headers-6.8.0-142-generic 6.8.0-142.142, nvme-cli 2.8 (libnvme 1.8), util-linux 2.39.3, Python 3.12.3, git 2.43.0, GNU bash 5.2.21, awk = GNU Awk 5.2.1. 시스템 python3 에는 python-docx·pypdf 가 없다. exp/.venv 의 버전은 exp/requirements.txt: numpy 2.5.3, matplotlib 3.11.2, python-docx 1.2.0, lxml 6.1.3, pillow 12.3.0, contourpy 1.4.0, cycler 0.12.1, fonttools 4.66.1, kiwisolver 1.5.1, packaging 26.3, pyparsing 3.3.3, python-dateutil 2.9.0.post0, six 1.17.0, typing_extensions 4.16.0.
- 없는 도구: gh, pandoc, libreoffice/soffice, pdftoppm, node/npm. LibreOffice AppImage(still, 291 MB)를 scratchpad 에 받아 두었다: /tmp/claude-1000/-home-dccearth-jsw/13edeb42-0011-48bf-800d-a7f7e0251b76/scratchpad/lo/LibreOffice-still.AppImage (docx 렌더링 확인용).
- Claude Code 의 Bash 도구 셸에서는 `grep` 이 ugrep 래퍼 함수다(패턴이 '-' 로 시작하면 옵션으로 해석되어 실패한다). 스크립트(bash script.sh)에서는 /usr/bin/grep(GNU)이 쓰이므로 영향이 없다.

---------------------------------------------------------------------------------------------------

## 4. 저장소 (/home/dccearth/jsw/KSC2026/nvmevirt)

- remote: origin = git@github.com:Sangwon8799/nvmevirt.git (push 용), upstream = https://github.com/snu-csl/nvmevirt.git
- 커밋(시간순):
  - 61c90f7758cbd9545b4a4727e89377bf88eab060 — upstream main HEAD, 2026-05-21 11:05:11 +0900 "Merge pull request #72 from duckhanson/fix/zns-append-return-slba". 모듈 버전 문자열 "NVMeVirt: Version 1.10 for >> Samsung 970 Pro SSD <<". upstream 에는 multi-instance 브랜치도 있다(사용 안 함).
  - d5086101c43d0414aa073579dbae4c7516f832a1 — 2026-10-08 04:54:03 "Move NVMeVirt sources into nvmevirt/ subdirectory" (순수 rename)
  - c02b9fda3aefeaab306a3bd6f00853b240a04c6c — 05:20:15 "nvmevirt: KSC2026 mapping-unit configuration" (Kbuild, ssd.c, ssd_config.h, conv_ftl.c, conv_ftl.h)
  - 5769378d46821c45595585c932522e4f76538fc6 — 05:20:15 "exp: scripts for the KSC2026 mapping-unit experiment". **본 실험(main_20261008)은 이 커밋에서 빌드·실행되었다**(exp/results/main_20261008/base/git_head.txt).
  - 이후 커밋(결과, plot.py, 보고서 생성기, 이 파일, 스크립트 수정)은 실험 후에 추가되며 11 절과 「갱신 이력」에 적는다.
- 커밋 작성자: Sangwon8799 <ekfghfl@naver.com> (전역 git config), 메시지 끝에 "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>".
- 저장소에 넣지 않는 것(exp/.gitignore): modules/*/*.ko (SHA256SUMS 는 넣음), .venv/, __pycache__/. nvmevirt/.gitignore 는 원본 그대로(`.*`, *.ko, *.o 등). .git/info/exclude 에 upstream_tmp/ 를 넣었다.
- /home/dccearth/jsw/KSC2026/nvmevirt/upstream_tmp/ — 감사 워크플로가 읽은 원본 사본(커밋 61c90f7, 수정 없음). 저장소에 포함되지 않으며, 실험 후 지워도 된다.
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
- 6 개 매핑 단위 모두 경고 없이 빌드된다. 경고는 "the compiler differs from the one used to build the kernel" 하나뿐이다. 커널은 x86_64-linux-gnu-gcc-13 13.3.0, 모듈은 gcc 13.3.0 으로, 바이너리 이름만 다르고 버전은 같다.
- 모듈과 SHA-256: exp/modules/<변형>/nvmev_map<단위>.ko, SHA256SUMS, build_info.txt (srcversion, vermagic "6.8.0-142-generic SMP preempt mod_unload modversions"). .ko 는 git 에 넣지 않는다. base 와 wbuffix 모듈은 run_all.sh 가 05:20:28 부터 다시 빌드했으므로, 결과 폴더의 modules_SHA256SUMS 를 참조한다.

---------------------------------------------------------------------------------------------------

## 6. 실험 설계와 스크립트 동작 (정확한 사양)

### 6.1 matrix / 순서
- MAPS = 4k 8k 16k 32k 64k 128k. BSS = 4k 8k 16k 32k 64k 128k. REPS = 3. 변형 = base, wbuffix (run_all.sh 가 base 108 회를 먼저 끝낸 뒤 wbuffix 108 회를 실행한다).
- 순서: for rep in 1..3 { for map in MAPS { for bs in BSS } }. 반복을 가장 바깥에 둔다.
- 회차 폴더: exp/results/main_20261008/<변형>/map<MAP>_bs<BS>_r<REP>/

### 6.2 회차 하나 (run_experiment.sh run_one)
1. DONE 이 있으면 건너뛴다(이어서 하기). 없으면 폴더를 지우고 다시 만든다.
2. nvmev 가 적재되어 있으면 rmmod(마운트 확인 후). 최대 30 s 기다리고 2 s 쉰다.
3. 커널 로그 기록을 시작한다: `sudo -n dmesg -W 2>&1 > >(awk … > kernel.log) &`. awk 는 '[chmodel_request]' 줄을 세고 처음 20 줄만 남긴다. 그 수는 END 에서 chmodel_msgs.txt 에 쓴다. 0.5 s 기다린다.
4. `echo "KSC2026-MARK <회차> insmod <ns>" | sudo -n tee /dev/kmsg` → `sudo -n insmod <ko> memmap_start=12G memmap_size=12G cpus=3,4,5`
5. /sys/block/nvme*n*/device/model 이 CSL_Virt 로 시작하는 장치를 최대 30 s(0.5 s × 60) 기다린다. 1 s 쉰 뒤, 표지 이후의 링 버퍼 dmesg 를 dmesg_load.txt 에 저장하고 "KSC2026: mapping unit=<bytes> B" 가 있는지 확인한다(없으면 die).
6. check_target_dev: 모델이 CSL_Virt*, 크기 11 GiB ≤ size ≤ 12 GiB, 파티션 없음, 마운트 없음, 루트 FS 장치 아님. 하나라도 어긋나면 die.
7. jobs/randwrite.fio.in 의 @DEV@ @BS@ @IODEPTH@ @RUNTIME@ @RAMP@ @LOG_MSEC@ @LOG_PREFIX@ 를 sed 로 채워 job.fio 를 만든다. meta.txt 를 쓴다.
8. SETTLE_SEC=5 s 쉬고, "KSC2026-MARK <회차> fio-start <ns>" 를 남긴 뒤 `sudo -n fio --output-format=json --output=fio.json job.fio`(stdout/stderr 는 fio_stdout.txt). 끝나면 "fio-end" 표지를 남긴다.
9. "KSC2026-MARK <회차> rmmod <ns>" 표지 → unload_nvmev(rmmod; GC 통계가 찍힌다) → 0.5 s → dmesg 기록 프로세스 kill → chmodel_msgs.txt 를 최대 60 s 기다림 → `sudo -n chown -R dccearth:dccearth <회차폴더>`
10. kernel.log 를 표지로 나눈다: fio-start ~ rmmod 표지 = dmesg_run.txt (chmodel 줄 제외), rmmod 표지 이후 = dmesg_unload.txt. meta.txt 에 end, fio_exit, chmodel_msgs, kernel_warn 을 더한다.
11. fio 종료 코드가 0 이고 fio.json jobs[0].error == 0 이면 결과 1 줄을 출력하고 DONE 을 만든다. 아니면 FAILED 표지를 만들고 계속한다(커밋 2a462a3 부터. 그 전 5769378 에서는 die 했다 — 10 절 첫 중단). fio 는 백그라운드로 실행하고 감시 타이머(RUNTIME+180 s SIGTERM, +60 s SIGKILL)가 지킨다.
- 시작할 때: sudo -n -l 로 insmod·rmmod·fio·dmesg·"tee /dev/kmsg" 권한 확인, /proc/cmdline 에 memmap=12G$12G 확인, 모든 .ko 존재 확인, sha256sum -c 확인. 그 뒤 env_before 스냅샷(없을 때만), modules_SHA256SUMS·modules_build_info.txt·randwrite.fio.in·git_head.txt·nvmevirt_vs_upstream.diff·nvmevirt_uncommitted.diff 를 <변형>/ 에 복사한다. 끝날 때: unload, env_after_<변형> 스냅샷.
- **알려진 결함 1**: run_experiment.sh 가 만든 `nvmevirt_vs_upstream.diff` 는 `git diff -M 61c90f7 HEAD -- nvmevirt` 라서, pathspec 때문에 rename 을 찾지 못하고 모든 파일을 새 파일로 표시한다(수천 줄). 올바른 diff 는 `git diff d508610 HEAD -- nvmevirt` 다. 실험이 실행 중이라 스크립트를 고치지 못했다. bash 는 스크립트를 실행 중에 조금씩 읽으므로, 실행 중인 run_experiment.sh·run_all.sh 를 같은 inode 로 덮어쓰면 위험하다. 실험이 끝난 뒤 고치고 결과 폴더의 파일도 다시 만들 것이다(갱신 이력에 기록).
- **알려진 결함 2**: meta.txt 의 kernel_warn 은 kernel.log 에서 chmodel 이 아닌 줄을 세려 했지만, 처음 20 개 chmodel 표본 줄 중 "No free entry" 줄도 셌다. analyze.py 는 kernel.log 에서 '[chmodel_request]' 와 'KSC2026' 줄을 빼고 WARNING|almost full|timeout|reset|Oops|BUG|Disk read failed|I/O error 를 다시 센다. CSV 의 kernel_warn 은 이렇게 다시 센 값이다.

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

### 6.4 권한 (/etc/sudoers.d/nvmevirt-exp, 0440 root:root) — 05:06 설치, 05:10 /dev/kmsg 추가
```
# KSC2026 NVMeVirt mapping-unit experiment — remove after the experiment:
#   sudo rm /etc/sudoers.d/nvmevirt-exp
dccearth ALL=(root) NOPASSWD: /usr/sbin/insmod, /usr/sbin/rmmod, /usr/bin/fio, /usr/bin/dmesg, /usr/sbin/nvme, /usr/bin/cat /proc/iomem, /usr/bin/tee /dev/kmsg, /usr/bin/chown -R dccearth\:dccearth /home/dccearth/jsw/KSC2026/nvmevirt/exp/*
```
- 사본: exp/report/nvmevirt-exp.sudoers. insmod·fio 권한은 사실상 root 와 같다. 실험 후 지우기로 사용자에게 말했다(7 절의 정리 단계 참조).

### 6.5 분석 (exp/analyze.py results/<EXP>)
- 회차별 지표: bw_MiBps(= fio write.bw/1024), iops, written_GiB, fill_ratio(= io_bytes/장치 크기), clat_mean/p50/p99/p999_us, lat_mean_us, slat_mean_us, runtime_s, bw_first10s_MiBps(t ≤ 10 s), bw_last20s_MiBps(t > 마지막 시각 − 20 s), dev_bytes, chmodel_msgs, kernel_warn.
- GC_STATS 가 있는 경우: gc_onset_s(fio-start 표지부터 4 개 파티션 중 가장 이른 "first GC" 줄까지), gc_onset_last_part_s, bw_pre_gc_MiBps(t ≤ onset), bw_post_gc_MiBps(t > onset), gc_cnt(4 개 파티션 합), ftl_host_pgs, ftl_gc_pgs, waf_gc = (host+gc)/host, waf_total = (host+gc)×매핑 단위 바이트 / fio io_bytes.
- 주의: ftl_host_pgs 에는 rmmod 직전까지 디스패처가 처리한 모든 쓰기가 들어간다. fio 가 끝난 뒤 udev 의 파티션 재검사 같은 읽기는 쓰기가 아니므로 포함되지 않는다.
- 집계: (variant, map, bs) 별 mean/std(표본 표준편차, n−1)/min/max/n.
- 그림: fig_bw_vs_bs_<v>, fig_clat_mean_vs_bs_<v>(log), fig_clat_p99_vs_bs_<v>(log), fig_bw_last20s_vs_bs_<v>, fig_bw_heatmap_<v>, fig_waf_heatmap_<v>, fig_timeseries_<v> (6×6, 3 회 겹침, 점선 = 첫 GC), fig_variant_compare.

---------------------------------------------------------------------------------------------------

## 7. 사전 점검 기록 (시간순, UTC)

- 04:46 upstream clone → /home/dccearth/jsw/KSC2026/nvmevirt/upstream_tmp (감사용으로 그대로 둠)
- 04:49 감사 워크플로 시작(wf_b41bb861-a42; 9 절)
- 04:53 스테이징 clone(/home/dccearth/jsw/KSC2026/.nvmevirt_stage) → git mv → 04:54:03 커밋 d508610
- 04:5x 소스 수정. 6 개 매핑 단위 시험 빌드 모두 OK(경고는 compiler differs 하나). WBUF_FIX/GC_STATS 4 가지 조합 × 4K·128K 시험 빌드도 모두 OK.
- 05:06 sudoers 설치. 이때 /proc/iomem 과 e820 으로 예약 영역을 확인했다(3 절).
- 05:07 스테이징 저장소를 /home/dccearth/jsw/KSC2026/nvmevirt 로 옮겼다. 그래서 exp/.venv 를 다시 만들었다(venv 경로가 절대경로라).
- 05:07:51 스모크 테스트 1 차는 실패했다. 원인: dmesg 를 /proc/uptime 기준 시각으로 잘랐는데 printk 시계가 CLOCK_BOOTTIME 보다 약 1 s 이상 늦어서 적재 로그를 놓쳤다. 모듈 자체는 정상 적재되었다. → /dev/kmsg 표지 방식으로 바꾸고 sudoers 에 tee /dev/kmsg 를 추가했다(05:10).
- 05:08:48 스모크 테스트 2 차(base, 매핑 4k·128k × bs 4k·128k, 10 s, 1 회):
  - 4k/4k 1273.2 MiB/s 325,927 IOPS clat 97.2 µs
  - 4k/128k 1297.5 MiB/s 10,380 IOPS clat 3078.3 µs
  - 128k/4k 101.8 MiB/s 26,065 IOPS clat 1226.1 µs
  - 128k/128k 1481.2 MiB/s 11,850 IOPS clat 2696.6 µs
  - 128k/4k 회차의 dmesg_run 이 비어 있었다. 원인: '[chmodel_request] Need to increase array size' 오류가 넘쳐 256 KiB(CONFIG_LOG_BUF_SHIFT=18) 링 버퍼가 덮어쓰였다. → 회차마다 `dmesg -W` 로 실시간 기록하도록 바꿨다.
  - 이 스모크 결과의 GC 통계(rmmod 시): 4k/4k host_pgs ≈ 815K/파티션, gc_pgs ≈ 356K, 첫 GC 6.3 s(host_pgs=778240/파티션에서). 128k/128k 첫 GC 3.86 s(host_pgs 24320/파티션에서). 128k/4k host_pgs ≈ 65K/파티션(= 7.9 GiB/파티션 NAND 쓰기, 호스트 약 1 GiB) → 매핑 128K 에 4K 쓰기면 NAND 쓰기 32 배.
- 05:12–05:14 스모크 3 차(base·wbuffix 각 4 조합, 10 s, kernel.log 전체 저장 방식):
  - base: 4k/4k 1272.9, 4k/128k 1297.5, 128k/4k 101.6 (chmodel 오류 1,665,207 줄, kernel.log.gz 16 MB), 128k/128k 1482.0 MiB/s
  - wbuffix: 4k/4k 1272.4, 4k/128k 1297.5, 128k/4k 77.0 (19,724 IOPS, clat 1621.0 µs, 오류 0), 128k/128k 1482.3 MiB/s
  - → 60 s 실행이면 회차당 약 100 MB 가 되므로, awk 로 세기만 하고 20 줄만 남기도록 바꿨다(05:15).
- 05:15:12 스모크 4 차(base 128k/4k, 10 s): 101.6 MiB/s 26,006 IOPS clat 1227.9 µs, chmodel_msgs 1,859,673. kernel.log 는 79 줄(6.8 KB). systemd-journald: "/dev/kmsg buffer overrun, some messages lost. (Dropped 93506 similar message(s))". 첫 GC 는 2.2 s(host_pgs=24320/파티션에서). 이 결과가 exp/results/pre_smoke_test/ 에 남아 있다(앞선 스모크 결과는 지웠다. 수치는 위 기록이 전부다).
- 05:15:50–05:18:36 GC_STATS A/B(매핑 4k, bs 4k, 20 s, 3 회, SETTLE 3 s), exp/results/pre_gcstats_ab/:
  - plain(GC_STATS 끔): 724.1 / 721.9 / 722.1 MiB/s (185,361 / 184,807 / 184,868 IOPS, clat 171.6 / 172.1 / 172.1 µs)
  - base(GC_STATS 켬): 724.3 / 726.0 / 724.4 MiB/s (185,428 / 185,864 / 185,444 IOPS, clat 171.5 / 171.1 / 171.5 µs)
  - 평균 722.7 vs 724.9 (+0.3 %, 반복 편차 수준) → 계측 영향 없음
  - (첫 시도는 Claude 셸의 grep 래퍼 문제로 파이프가 끊겨 run.log 만 남았다. 지우고 다시 실행했다.)
- 05:20:15 커밋 c02b9fd, 5769378 → push(main, 신규 브랜치)
- 05:20:28 run_all.sh main_20261008 시작(tmux 세션 ksc2026, 로그 exp/results/run_all_main_20261008.log). 05:20:28–05:20:4x 에 base 와 wbuffix 모듈 12 개를 빌드했다. 05:21:02 env_before 스냅샷, 1/108 회차 시작.

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
  - 이 오류는 rate limit 없는 pr_err 다. 디스패처(cpu3) 핫패스에서 요청마다 찍히고, 콘솔 loglevel 4 라 tty0 콘솔과 journald 에도 간다. 측정값: 128k/4k 10 s 에 약 170–186 만 줄, 8k/4k 60 s 에 8,242,206 줄.
  - 따라서 base 의 bs < 매핑 단위 결과는 「채널 시간이 빠져 빨라짐」과 「printk·콘솔 부담으로 느려짐」이 섞인 값이다. 타이밍 모델이 정상 범위를 벗어났다.
- 수정: WBUF_FIX=1 (5.4 절). 감사 에이전트 2 개(wbuf-write-path, geometry-init)가 독립적으로 blocker 로 판정했고 같은 수정을 제안했다. 검증 에이전트도 확인했다(9 절).
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
- 활성 I/O 워커 1 개: nvmev.h 의 `#define CONFIG_NVMEV_IO_WORKER_BY_SQ` 때문에 워커 = (sqid−1) % nr_io_workers 다. 가상 장치가 MSI-X 없이 레거시 IO-APIC IRQ 15 하나(/proc/interrupts: "15: … IR-IO-APIC 15-edge nvme1q0, nvme1q1")만 받아 I/O 큐가 1 개("nvme nvme1: 1/0/0 default/read/poll queues")다. 그래서 모든 요청이 sqid 1 → cpu4 의 워커 0 만 쓰이고, fio 가 어느 CPU 에 있든 같다. 워커 1(cpu5)은 I/O 없이 폴링만 한다. /proc/irq/15/effective_affinity_list = 5 (smp_affinity_list 0-5, irqbalance inactive)라서 호스트 nvme 완료 인터럽트는 cpu5 에서 처리된다(06:2x 확인, IRQ 15 누적 112,040,881 회 전부 CPU5). 논문에는 「디스패처 1 + 워커 2(활성 1)」로 적는 것이 정확하다.
- 매핑 표가 호스트 메모리 배열(DFTL 캐시 모델 없음)이라 L2P 크기 효과는 성능에 나타나지 않는다. L2P 크기는 계산으로 따로 보고한다: 전체 FTL 페이지 × 8 B = 4K 24 MiB, 8K 12, 16K 6, 32K 3, 64K 1.5, 128K 0.75 MiB. rmap 도 같은 크기다.
- GC 문턱: free line ≤ 2 (gc_thres_lines = gc_thres_lines_high = 2). 쓰기 크레딧(pgs_per_line)을 다 쓸 때마다 검사한다. 처음 free line 은 파티션당 382 개(384 − 사용자·GC 쓰기 포인터 2). 첫 GC 는 파티션당 380 line = 장치 전체 12,160 MiB 의 페이지 쓰기 뒤에 온다. 측정에서도 첫 GC 시점의 host_pgs = 778,240/파티션(4K 매핑, = 380 × 2048) — 정확히 일치한다.
- fio randommap 의 주기 현상(05:3x 에 시계열로 확인):
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

---------------------------------------------------------------------------------------------------

## 9. 감사 워크플로 (wf_b41bb861-a42) 요약

- 스크립트: /home/dccearth/.claude/projects/-home-dccearth-jsw-KSC2026-nvmevirt-upstream-tmp/13edeb42-0011-48bf-800d-a7f7e0251b76/workflows/scripts/ksc2026-nvmevirt-understand-audit-wf_b41bb861-a42.js. 기록은 /home/dccearth/.claude/projects/-home-dccearth-jsw/13edeb42-0011-48bf-800d-a7f7e0251b76/subagents/workflows/wf_b41bb861-a42/journal.jsonl 에 있다.
- 단계: Read(설정조사 보고서 → 설정 사양, 논문 → 연구 맥락) / Audit(렌즈 3 개: wbuf-write-path, geometry-init, gc-timing) / Verify(blocker·high·medium 주장마다 반박 시도 2 개: 코드 경로 추적, 수치 예시 대조).
- 주요 주장(심각도):
  - [blocker] 쓰기 버퍼 과다 반환(8.1) — 두 렌즈가 독립적으로 찾았다.
  - [high] 그 결과로 NAND 대기열이 끝없이 늘어 io-worker 큐(16384) 고갈, 393 ms 채널 창 초과, O(N) 비용이 생긴다.
  - [high] 64K/128K flash page 변경에 따른 NAND 대역폭·버퍼 변화(8.2).
  - [high] 조기 완료 때문에 GC 가 버퍼 정체로만 보인다.
  - [high] 장치는 모델명으로 찾아야 한다(루트가 nvme0n1). 이미 반영했다.
  - [medium] RMW 미모델, DFTL 없음, 60 s 창에서 GC 시작 시점이 달라 GC 전후 구간이 섞임(시계열·GC 시각 기록으로 대응), 워커 1 개만 활성(fio 고정 권고 — 고정은 하지 않음. 큐가 1 개라 워커가 바뀌지 않는다), 64K/128K 에서 FLASH_PAGE_SIZE 를 안 바꾸면 assert(이미 반영).
  - [info] assert 전부 통과, 블록 2 MiB·용량·OP 가 모든 매핑에서 같음, MAX_CH_XFER_SIZE 는 쓰기에 무관, MDTS 로 128k 가 분할되지 않음, rmmod/insmod 가 FTL 을 완전히 초기화(저장 데이터는 남음), 4KB 전용 상수(ssd.c 394, conv_ftl.c 867)는 쓰기 전용 실험에 무관.
- 워크플로 완료: 06:22 UTC, 에이전트 51 개(오류 0), 하위 에이전트 토큰 약 4.94 M, 소요 약 92 분.
  - 결과 원본: exp/report/audit_result.json (spec = 설정조사 보고서에서 뽑은 기본값 전체, ctx = 논문 맥락, audit = 렌즈별 주장·검증 판정)
  - 한국어 요약: exp/report/audit_summary_ko.txt (docx 부록 E)
- 검증 판정 요약: 핵심 주장은 하나도 뒤집히지 않았다. 「refuted」로 표시된 판정은 모두 세부 정정이다. 주요 정정:
  - (a) GC 전 4k/4k 는 CPU 병목이 아니라 NAND 한계의 90 %
  - (b) base 의 bs<MAP(MAP≤32K)는 GC 전에 NAND×bs/MAP 에 머문다
  - (c) 워커 선택은 큐가 1 개라 고정이다(IRQ 15 → cpu5)
  - (d) bs≥MAP 의 GC 영향은 버퍼 정체 재시도 + do_gc CPU 시간으로 나타난다
  - (e) randommap 주기: 둘째 바퀴 끝에 WA 약 1.5, bs<MAP 는 WA 7.6–8.4 까지 상승
  - (f) WB-2 의 「무한 증가」는 O(N) 브레이크 때문에 GC 전에는 제한된다

---------------------------------------------------------------------------------------------------

## 10. 본 실험 진행 기록 (main_20261008)

- 05:20:28 시작. base 1/108 05:21:02.
- base 첫 회차들(60 s): 4k/4k r1 418.4 MiB/s 107,109 IOPS clat 297.7 µs, 첫 GC 6.30 s, WAF_gc 3.14 / 4k/8k r1 433.6 MiB/s / 4k/128k r1 496.8 MiB/s 3,974 IOPS clat 8047.2 µs / 8k/4k r1 chmodel_msgs 8,242,206, kernel_warn 1(그 회차의 "No free entry" 표본 줄), rmmod 때 파티션 읽기 실패 4 줄.
- **05:44:22–05:46:57 첫 중단**: base 21/108 회차 map32k_bs16k_r1 에서 fio 가 I/O 오류(fio error 5 = EIO, exit 1)로 실패했다. run_experiment.sh(당시 커밋 5769378)가 die 하면서 run_all.sh(set -e)도 끝났고, tmux 세션 ksc2026 이 종료되었다.
  - 시간선(fio-start 표지 기준, 해당 회차 kernel.log 에서 추출):
    - +5.64 s 첫 GC
    - +24.97 s `WARNING: CPU: 3 PID: 30089 at …/nvmevirt/io.c:302 __allocate_work_queue_entry+0x8a/0xb0 [nvmev]` — "IO queue is almost full" WARN_ON_ONCE. 쓰기 버퍼 과다 반환으로 NAND 완료 시각이 먼 미래인 internal operation 이 io-worker 작업 큐(16384 항목)를 채운 것이다(감사 WB-2/C2 예측과 같음).
    - +55.09 s `nvme nvme1: I/O tag 192 … QID 1 timeout, aborting req_op:WRITE(1) size:16384` (커널 nvme 기본 io_timeout 30 s)
    - +85.29 s `timeout, reset controller` → Abort status 0x371
    - +146.74 s `I/O tag 28 (301c) QID 0 timeout, disable controller` → `Identify Controller failed (-4)` → `Disabling device after reset failure: -5`
    - +146.76 s 이후 `I/O error, dev nvme1n1 … op 0x1:(WRITE)` 10 줄 → fio 종료(runtime 146,507 ms, 그때까지 평균 114.4 MiB/s, 7,319 IOPS, 16.36 GiB). udev 의 파티션 읽기 Buffer I/O error / attempt to access beyond end of device.
    - rmmod 정상("Virtual NVMe device closed"). GC 통계: 파티션별 host_pgs 약 268K, gc_pgs 약 839K, gc_cnt 약 3,946. chmodel_msgs 10,038,918.
  - 판단: 요청 설정 그대로인 base 모델이 bs < 매핑 단위에서 무너지는 현상이므로 그 자체를 결과로 남긴다.
  - 조치(커밋 2a462a3, 05:49):
    - run_experiment.sh 가 fio 실패 회차에 FAILED 표지(첫 줄 `fio_exit=… fio_json_error=… kernel_warn=… chmodel_msgs=…`, 그 뒤 관련 커널 줄 최대 20 개)를 남기고 다음 회차로 넘어가도록 바꿨다. 다시 실행해도 FAILED 회차는 건너뛴다.
    - fio 감시 타이머: RUNTIME + FIO_GRACE(180 s) 에 SIGTERM, 60 s 뒤 SIGKILL. sudo 프로세스로 보내면 sudo 가 fio 에 전달한다.
    - meta.txt 에 git_head 를 추가했다. git_head.txt 는 실행마다 한 줄씩 덧붙인다(base 의 git_head.txt 첫 줄은 손으로 시각을 붙였다: "2026-10-08T05:21:02+00:00 5769378…").
    - nvmevirt_vs_upstream.diff 를 rename 커밋 기준으로 고쳤다.
    - kernel_warn 집계에서 chmodel 표본 줄을 뺐다.
    - analyze.py 가 failed_runs.csv 를 쓰도록 했다(t_gc_s, t_queue_full_warn_s, t_nvme_timeout_s, t_reset_s, t_disable_s, t_first_io_error_s).
    - plot.py, 보고서 생성기, 이 파일도 같은 커밋에 넣었다.
  - map32k_bs16k_r1 은 손으로 FAILED 표지를 만들어 보존했다(첫 줄에 "marked by hand" 명시).
- **05:49:13 재개**(tmux ksc2026): `bash run_experiment.sh main_20261008 wbuffix` → 이어서 `bash run_experiment.sh main_20261008 base`(완료된 20 회와 FAILED 1 회는 건너뜀) → `analyze.py`. 로그는 같은 run_all_main_20261008.log 에 이어 쓴다.
  - 순서를 바꾼 이유: 유효한 데이터셋(wbuffix)을 먼저 확보하기 위해서다.
  - 모듈은 다시 빌드하지 않았다. 05:20 에 빌드한 exp/modules/{base,wbuffix} 를 그대로 써서 base 의 앞 20 회와 같은 바이너리다(sha256 검사).
  - 따라서 실제 실행 순서는 run_all.sh(빌드 → base → wbuffix)와 다르다. base 회차는 1–20(커밋 5769378 스크립트)과 22–108(커밋 2a462a3 스크립트)이다. NVMeVirt 소스와 모듈은 같고, 스크립트 차이는 실패 처리·기록 방식뿐이라 측정 절차는 같다.
- 진행 중 이상은 이 절에 이어서 적는다(완료 후 갱신).

---------------------------------------------------------------------------------------------------

## 11. 결과

<!-- AUTO-RESULTS-BEGIN -->
(실험 완료 후 exp/report/make_md_results.py 가 이 자리를 채운다)
<!-- AUTO-RESULTS-END -->

---------------------------------------------------------------------------------------------------

## 12. 그래프 도구 (exp/plot.py) 사용법

- 실행: `cd /home/dccearth/jsw/KSC2026/nvmevirt/exp && ./.venv/bin/python plot.py <cmd> [옵션]`. 결과 폴더를 직접 읽으므로 실험 도중의 부분 데이터에도 쓸 수 있다. analyze.py 의 collect/aggregate 를 그대로 쓴다.
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
- 색: 범주색 고정 순서 #2a78d6 #eb6834 #1baf7a #eda100 #e87ba4 #008300 #4a3aa7 #e34948 (4K→128K 순). 열지도는 단일 파랑 계열. 그림 글자는 영어다(matplotlib 기본 글꼴에 한글이 없다).

---------------------------------------------------------------------------------------------------

## 13. 다음 Claude 를 위한 주의 사항

- 응답·보고는 한국어로만 한다.
- sudo 비밀번호는 사용자가 한 번 알려 줬지만 기록하지 않았다. 필요하면 사용자에게 묻는다. sudoers 규칙이 남아 있으면 `sudo -n` 으로 insmod/rmmod/fio/dmesg/nvme/tee /dev/kmsg/cat /proc/iomem/chown(exp 아래) 을 쓸 수 있다.
- GitHub push 는 사용자의 forwarded ssh-agent 소켓이 필요하다(`ls /tmp/ssh-*/agent.*`). 사용자가 접속해 있지 않으면 push 할 수 없다.
- 실험 중(tmux ksc2026)에는:
  - run_experiment.sh·run_all.sh 를 같은 파일로 덮어쓰지 않는다(bash 가 실행 중 읽음).
  - CPU 0–2 에서 무거운 작업을 하지 않는다(fio 가 그곳에서 돈다). 필요하면 nice -n 19.
  - nvmev 모듈을 손대지 않는다.
- 결과를 해석할 때:
  - base 의 bs < 매핑 단위 15 조합은 8.1 절 때문에 wbuffix 결과를 기준으로 본다.
  - 64K/128K 는 8.2 절의 NAND 변화가 섞여 있다.
  - 60 s 평균에는 GC 이전 구간과 fio randommap 주기 현상이 섞여 있다.
- 사용자에게 아직 말하지 않았거나 결정이 필요한 후속 후보:
  - RMW 읽기 모델 추가
  - 64K/128K 에서 tPROG 를 비례로 키운 대조 실험
  - 사전 채움 후 정상 상태 측정(설정조사 보고서 추천 300 s)
  - norandommap / random_distribution 변경
  - RocksDB(db_bench) 응용 실험

---------------------------------------------------------------------------------------------------

## 갱신 이력
- 2026-10-08 05:40경 최초 작성(본 실험 base 진행 중, 약 13/108).
- 2026-10-08 05:50 10 절에 첫 중단(base map32k_bs16k_r1 장치 실패)과 재개(wbuffix 먼저) 기록.
- 2026-10-08 06:25 감사 워크플로 완료 반영(9 절), GC 이전 처리량 정정과 IRQ 15/cpu5 사실(8.3 절) 추가. 저장소에 credential 이 없는지 검사(grep 으로 sudo 비밀번호·서버 IP 문자열 검사 → 없음.
