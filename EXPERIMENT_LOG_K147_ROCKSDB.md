# KSC2026 — 커널 6.8.0-147 재측정 + RocksDB/YCSB-A 실험 기록 (2026-10-24 ~ 10-25, Claude 인계용)

이 파일은 **2026-10-24 ~ 10-25 (KST)** 의 작업 전 과정을 다른 서버의 Claude 가 이어받을 수 있도록 적은 기록이다.
그 이전(2026-10-08 ~ 10-09)의 NVMeVirt fio 실험은 같은 묶음의 `EXPERIMENT_LOG_FOR_CLAUDE.md` 에 있다.

- 경로는 **인계 묶음(.tgz) 루트 기준**이다: `repo/…` = 실험 서버의 저장소 작업 트리(`/home/dccearth/jsw/nvmevirt`).
  이 묶음을 받은 Claude 는 실험 서버(dccearth)에 접근할 수 없다. 서버 경로는 기록용이다.
- 시각은 모두 **KST** 다. 원자료(로그, meta.txt, kernel.log)는 서버 시계 **UTC** 그대로다(KST = UTC + 9 시간).
- 답장·보고는 한국어로 한다(사용자 지시).

<!-- BEGIN MANUAL: status -->
## 0. 현재 상태 (STATUS) — 2026-10-25 08:3x KST 기준

- **실험 완료.** 2026-10-25 01:29:45 – 08:33:48 KST, 마스터 `run_all_k147.sh` 종료 코드 0.
  - fio 재측정 44 회(랜덤 12 + 순차 24 + 랜덤 bs 추가 8): DONE 44, FAILED 0, 커널 경고 0.
  - RocksDB/YCSB-A 32 회: DONE 32, FAILED 0. 모든 회차에서 READ·UPDATE 응답이 전부 OK(레코드 유실 없음), run 600.0–600.1 초, 커널 경고 0.
- **선배 전달용 복사본**: `repo/exp/results/share_k147_20261025/` (README.md 가 파일·열 설명). 요청 값만 모은 표는
  `rocksdb_ycsba_table.csv/.json` (매핑 × block_size × WAL 32 줄: TPS, READ·UPDATE p99·평균 지연). 서버에는 같은 폴더의 zip
  `~/jsw/handoff/ksc2026_k147_share_20261025.zip` 도 있다.
- **핵심 결과** (§6 표, §7 해석):
  - RocksDB: 모든 block_size·WAL 조건에서 매핑 단위가 커질수록 TPS 가 줄었다(32 칸 모두 단조). 매핑 32K 는 4K 대비 −20.3 ~ −31.6 %.
    block_size 32K 는 4K 대비 −8.5 ~ −22.9 %(4K 와 8K 는 ±3 % 안). WAL on/off 차이는 −3.1 ~ +4.4 %(1 회 측정이라 잡음과 구분 못 함).
    READ p99 는 511–756 µs, UPDATE p99 는 READ p99 와 −6 ~ +13 µs 차이.
  - fio: 커널 147 결과가 142 결과를 재현했다(같은 33 조합의 처음 60 초 평균 대역폭 차이 평균 0.10 %, 최대 1.06 %). 매핑 8K 를 새로 쟀다.
- 실험 동안 서버 상태: RocksDB run 동안 CPU 0–2 사용률 2.1–3.5 %, CPU 압력(PSI some) 0.04–0.07 % → 다른 작업의 간섭 없음.
- sudo 규칙: 사용자가 삭제했다(2026-10-25 15:20:05 KST 보고, `/etc/sudoers.d/` 에 README 만 남은 것 확인). 가상 SSD 는 내려져 있고 마운트된 것도 없다.
- 저장소: 2026-10-25 15:24 KST 에 GitHub main 으로 push(bc31375..8d3e348, 사용자 ssh -A 접속; 이 기록의 마지막 커밋도 이어서 push, §12). 남은 일 없음.
<!-- END MANUAL: status -->

## 1. 사용자 지시와 결정 (시간순, 원문 인용)

### 1.1 RocksDB 설치 (2026-10-24 19:44:39)
> 선배님이 이제 RocksDB config 설정을 통해 데이터를 쌓자고 하셨어. 서버에 RocksDB 설치해주고, 버전 확인하는 방법 알려줘.

→ RocksDB v11.8.1 을 소스로 빌드했다(19:46–19:52, `/home/dccearth/jsw/rocksdb`, `make -j3 DEBUG_LEVEL=0 static_lib db_bench ldb sst_dump`).
버전 확인: `./db_bench --version` → `db_bench version 11.8.1`. 업스트림 태그 v11.8.0 과 v11.8.1 이 같은 커밋(abeebd9)을 가리킨다.
**실험 자체는 이 빌드가 아니라 YCSB 가 쓰는 RocksJava `rocksdbjni-11.8.1.jar`(Maven Central, 같은 11.8.1 릴리스)로 돌았다.**

### 1.2 선배의 실험 설명 (21:36:51, 사용자가 정리해 붙여 넣음)
> FTL Mapping size unit 실험 정리 / 작성 일자 2026-10-24 21:24 / 환경 RocksDB / 조건 WA disable인 경우, enable인 경우 각각에 대해 같은 실험을 진행 /
> 실험: mapping size unit, BL size unit, FTL size unit 각각 4/8/16 KB로 설정 · 실험은 모두 1번씩만, 시간은 10분 이내로만 측정 · YCSB-A를 돌렸을 때 TPS, lat p99 뽑기 /
> 결과: Raw data 정리해서 선배님께 전달 · (선택) 그래프 뽑기
> (사용자) YCSB-A가 뭐야? TPS가 뭐야? … 실험은 아직 진행하지 말고, 이 전달 사항을 토대로 어떤 식으로 진행해야 하는지 정리해서 알려줘.

→ 설명과 계획만 했다(조사 워크플로 wf_0acfca0a-29f). YCSB-A = 읽기 50 % / 업데이트 50 % zipfian 워크로드, TPS = run 단계 초당 연산 수.
21:50:23 사용자: 「BL은 블럭 사이즈 … 선배님께서 실험 케이스가 3x3니까 9회 … 총 18회」, 21:51:00 「WA는 Write Amplification 말하는거 아닐까?」

### 1.3 커널 질문 (22:30 – 23:01)
- 22:30 「커널 버전 바뀌었어? 어떻게 확인해?」 → 당시 실행 커널 6.8.0-146, 147 도 설치되어 있었다(`uname -r`, `/boot`, dpkg 로그).
- 22:32 「모듈을 146으로 바꾸면 이전에 쌓았던 데이터도 다시 측정해야 해?」, 22:40 「이전 커널 버전이 142인건 어떻게 안거야? 내 실험 기록에는 136으로 되어 있는데?」
  → 커널 이력(`last -x reboot`, dpkg 로그): 136 은 10-07 21:19 KST 까지, 10-08 실험은 142, 10-11 부터 146.
  사용자의 136 기록은 10-07 21:19 이전의 상태다.
- 22:46 다음 자동 업데이트: unattended-upgrades 가 매일 15:00–16:00 KST 에 확인한다. 자동 재부팅은 없다.
- 22:52 「그럼 이번에 146으로 모듈 바꾸면 이전에 했던 실험을 다시 진행하고 동시에 이어서 RocksDB에서도 진행하는걸로 하자. 계획만 알아둬.」
- 22:53 「이전 실험도 각각에 대해서 3회 반복이 아닌 1회만 진행하는걸로 하면 횟수가 어떻게 돼?」

### 1.4 선배의 답 (23:12:24, 사용자가 전달)
사용자가 선배에게 보낸 질문과 답(원문):
> 1. WA disable/enable은 RocksDB의 WAL(Write-Ahead Log)을 끄고 켜는 것을 말씀하신 건가요? … → **wal**
> 2. BL Size는 RocksDB의 block_size 옵션(SST 블록 크기, 기본 4KB)을 4/8/16KB로 바꾸는 것으로 이해했는데 맞을까요? → **맞을듯**
> 3. FTL Size가 … FTL 매핑 단위(mapping size unit)를 말씀하신 걸까요? … 총 18회로 이해했습니다. → **맞음**
> 4. YCSB-A는 연구실에서 쓰는 db_bench YCSB(ycsb_load/ycsb_run)로 돌리면 될까요, 아니면 정식 YCSB를 써야 할까요? 맞춰야 하는 RocksDB 버전이 있는지도 궁금합니다. → **최신 버전, 정식 ycsb**
> 5. 10분은 … run 단계만 10분으로 맞추면 될까요? p99는 read와 update를 따로 정리해 드리면 될까요? → **직접 정하면 될듯?**
> 아 그리고 만약에 시간되면 32kb도 추가해서 ㄹ하면좋을듯?? 설정은 따로 정리 해서 안줘도 되고 그냥 결과 나오면 값만 표로 공유해주면 될듯 ㅎㅎ
> (사용자) 그래서 32KB 실험도 추가로 진행하면 될 것 같아.

23:27:57 질문과 답: 32KB 는 「두 축 모두」(매핑 단위와 block_size), YCSB 는 「정식 Java YCSB」.
→ RocksDB 행렬 = 매핑 {4,8,16,32}K × block_size {4,8,16,32}K × WAL {off,on} = 32 회. run 단계 10 분, p99 는 READ·UPDATE 따로.

### 1.5 준비 (23:30 – 23:44)
- 23:30:22 「서버는 나 혼자 쓰고 있어서 재부팅이 가능해 … `sudo apt install openjdk-17-jdk-headless maven` 명령어 입력해서 설치했어.」(OpenJDK 17.0.20.1, Maven 3.8.7)
- 23:31:58 「재부팅했어」 → 커널 **6.8.0-147-generic**. `memmap=12G$12G`, `isolcpus=3-5` 유지 확인. NVMeVirt 모듈을 147 용으로 다시 빌드(23:32, 커밋 becebf1, §2.2).
- 23:38:10 「1~2번까지만 진행해줘」 → 1 = 정식 YCSB 빌드·패치, 2 = sudo 규칙 파일 작성(설치는 사용자).
- 23:44:14 「설치했어.」 → `/etc/sudoers.d/nvmevirt-exp` 설치 확인. 무해한 명령으로 확인: 규칙과 정확히 같은 명령만 비밀번호 없이 실행되고, 인자가 다르면 비밀번호를 요구한다.

### 1.6 실험 지시 (2026-10-25 01:11:01) — 원문 그대로
```
NVMeVirt fio + RocksDB 실험
실험 일자 2026-10-25, Kernel 6.8.0-147
환경
* RocksDB 11.8.1
* NVMeVirt
조건
1. Kernel 버전이 변경(142→147)됨에 따라 NVMeVirt 성능 재측정
   * mapping 단위는 4/8/16/32 KB로만 측정
   * bs 8/64 KB는 그대로 사용
   * Page Cache no-drop으로만 측정.
2. RocksDB: WA ① disable인 경우, ② enable인 경우 각각에 대해 같은 실험을 진행
방법
* NVMeVirt fio: 2분, 회차마다 빈 장치에서 시작
* RocksDB: FTL mapping size unit + BL size unit 4/8/16/32 KB(4×4), WAL disable/enable, 10분
실험
NVMeVirt fio 재측정
1. random write (3×3) = 9회
2. sequential write (3×3) × 모델 2가지(wbuffix, merge) = 18회
3. random write bs 추가 mapping 4/16/32 KB × bs 8/64 KB = 6회
RocksDB
* YCSB-A (4×4) × WAL disable/enable 2회 = 32회
결과
* 원자료 보관
* (추가 작업) Raw Data → 선배님에게 전달할 수 있도록 복사본 만들어서 `.json`, `.csv` 파일로 정리
* 다른 세션의 Claude가 읽을 수 있도록 `.md` 파일로 실험 전 과정 정리하여 상세히 기록하여 `handoff` 폴더에 `LATEST.tgz`에 저장
-----
이렇게 실험 진행해줘. 그리고 실험에 사용한 스크립트 파일이 뭔지도 정리해서 함께 `LATEST.tgz`에 적어줘.
```

### 1.7 Claude 가 물은 것과 답 (01:17:53, AskUserQuestion)
| 질문 | 답 |
|---|---|
| fio 매핑 단위: 지시문은 「4/8/16/32 KB로만」인데 횟수(9·18·6)는 4/16/32 기준. 어느 쪽? | **8KB도 추가** (매핑 4/8/16/32 → 랜덤 12 + 순차 24 + bs 추가 8 = 44 회) |
| RocksDB 적재량 | **300만 건 ≈ 3.3 GB** (권장안) |
| WAL 을 켤 때 업데이트마다 fsync? | **동기화 안 함** (RocksDB 기본값 `sync=false`, 권장안) |
| YCSB 클라이언트 스레드 | **1 개** (권장안) |

### 1.8 시험 실행 뒤 질문 (01:31:06)
3M 건 적재가 12.5 초(240K ops/s)로 끝나 compaction 이 약 6 GB 밀린 채(L0 파일 21 개, 쓰기 지연) run 이 시작되고,
run 처음 4 초가 130–200 ops/s, 5–9 초가 약 2,700 ops/s 였다(§4; 질문할 때는 「처음 10초」라고 적었다). 「측정 전에 밀린 compaction 을 끝낼까?」 → **적재 직후 바로 측정**(YCSB 기본 절차).
그래서 run 단계는 load 가 끝난 직후 새 JVM 으로 시작한다(대기 단계 없음).

### 1.9 실험 중 (01:48 – 01:59)
- 01:48:45 「한글로 알려줘」(Claude 가 진행 보고를 영어로 써서) → 다시 한국어로 보고.
- 01:50:40 「나한테 더 물어볼거 있어?」 → 없음. 끝날 때 GitHub push 여부와 sudo 규칙 삭제만 확인하기로 함.
- 01:51:31 **「알아서 진행한 뒤 끝나면 알려줘.」** → 이후 묻지 않고 분석·공유본(csv·json)·이 기록·인계 묶음(LATEST.tgz)까지 마친 뒤 보고.
- 01:56:41 「지금 진행 상황 알려줘」, 01:58:32 「10시간 정도 더 걸린다는거지?」(→ 실제로는 약 7 시간: Claude 의 처음 예상 12:00 이 틀렸다고 정정, 완료 예상 09:00, 정리 포함 10:00), 01:59:12 「알겠어, 끝나면 알려줘」.

### 1.10 실험이 끝난 뒤 (2026-10-25)
- 09:10 경 Claude 가 완료 보고(결과 요약, 공유본 zip·TPS 그림 첨부, sudo 규칙 삭제 명령, push 여부 질문).
- 15:20:05 「sudo 규칙 지웠어. 각 실험 당 진행 시간은 어떻게 돼?」 → 삭제 확인. 실험별 시간: 랜덤 12 회 26 분 5 초, 순차 wbuffix 12 회 26 분 5 초,
  순차 merge 12 회 26 분 5 초, 랜덤 bs 추가 8 회 17 분 24 초(fio 회차당 약 130 초), RocksDB 32 회 5 시간 28 분 17 초(회차당 613–618 초), 전체 7 시간 4 분 3 초.
- 15:23:02 「ssh -A 접속했어. GitHub push 해줘.」 → §12.

## 2. 환경

### 2.1 서버
- Intel i5-13600K, 6 코어 사용(부팅 옵션 `isolcpus=3-5` → 일반 프로세스는 CPU 0–2, NVMeVirt 는 `cpus=3,4,5`), 24 GB RAM 중 12 GiB 를
  `memmap=12G$12G` 로 NVMeVirt 에 예약 → 호스트가 쓰는 RAM 11.45 GiB.
- 커널 **6.8.0-147-generic** (2026-10-24 23:31 KST 재부팅부터). 이전 fio 결과(10-08)는 6.8.0-142.
- 환경 스냅샷: `repo/exp/results/<실험>/env_before/`, `env_after_<변형>/` (collect_env.sh).

### 2.2 NVMeVirt 모듈 (커널 147 용, 2026-10-24 23:32 KST, 커밋 becebf1)
- 소스: `repo/nvmevirt/` (업스트림 snu-csl/nvmevirt @ 61c90f7 + KSC2026 수정, `EXPERIMENT_LOG_FOR_CLAUDE.md` §5).
- 빌드: `repo/exp/build_modules.sh <변형>` → `exp/modules/<변형>/nvmev_map<M>.ko` (.ko 는 git 에 없음, 체크섬은 `SHA256SUMS`, 빌드 기록 `build_info.txt`).
  - wbuffix (`GC_STATS=1 WBUF_FIX=1`): 4k 8k 16k 32k 64k 128k
  - merge (`GC_STATS=1 WBUF_FIX=1 WBUF_MERGE=1`): 4k 8k 16k 32k
  - 커널 142 용 이전 빌드 기록은 `exp/modules/wbuffix_k142/`, `merge_k142/`.
- insmod: `memmap_start=12G memmap_size=12G cpus=3,4,5`. 장치 `/dev/nvme1n1`, 모델 `CSL_Virt_MN_01`, 12,040,984,064 B (11.21 GiB).
  flash page 는 매핑 단위 ≤ 32K 에서 항상 32 KiB, 플래시 블록 2 MiB, GC 단위 line = 블록 4 개 = 8 MiB, 파티션 4 개(이전 기록 §8.4).
- NVMeVirt 특성(이전 기록 §8): TRIM 없음(oncs=0), 휘발성 캐시 없음(vwc=0), SMART 카운터 0 고정, 예약 메모리는 rmmod/insmod 해도 지워지지 않음
  (그래서 RocksDB 회차는 매번 mkfs), 매핑 단위보다 작은 쓰기의 read-modify-write 읽기를 모델링하지 않음.

### 2.3 RocksDB / YCSB
- 정식 YCSB: github.com/brianfrankcooper/YCSB master **ae02b31f (2026-10-20)**, 서버 `/home/dccearth/jsw/YCSB`,
  브랜치 `ksc2026-rocksdb-11.8.1` 커밋 **8cd243b4**. 패치 = `repo/exp/ycsb/ycsb-rocksdb-11.8.1.patch` (설명 `repo/exp/ycsb/README.md`):
  - `pom.xml`: rocksdbjni 6.2.2 → **11.8.1**
  - `RocksDBClient.java`: `OptionsUtil.loadOptionsFromFile(ConfigOptions, …)` (11.x API), 새 속성 `rocksdb.disablewal`, `rocksdb.sync` → 모든 put/delete 의 `WriteOptions`
  - 테스트 1 개 API 수정, README. 빌드 `mvn -B -pl site.ycsb:rocksdb-binding -am clean package` (테스트 통과), 풀어 둔 곳 `/home/dccearth/jsw/ycsb-dist/ycsb-rocksdb-binding-0.18.0-SNAPSHOT`.
- Java: OpenJDK 17.0.20.1, Maven 3.8.7 (사용자가 apt 로 설치).
- 바인딩 동작(코드 확인): 레코드는 column family `usertable` 에 저장. YCSB-A 의 update 는 필드 1 개를 바꾸므로 **Get + Put**(레코드 전체 다시 씀).
  옵션 파일에 `[CFOptions "usertable"]`·`[TableOptions/BlockBasedTable "usertable"]` 가 없으면 run 단계가 「Column families not opened: usertable」로 실패한다.

### 2.4 sudo 규칙 (`repo/exp/report/nvmevirt-exp.sudoers`, 2026-10-24 23:44 KST 사용자 설치)
insmod, rmmod, fio, dmesg, nvme, `cat /proc/iomem`, `tee /dev/kmsg`, `tee /proc/sys/vm/drop_caches`, `tee /sys/block/nvme1n1/queue/nomerges`,
`chown -R dccearth:dccearth /home/dccearth/jsw/nvmevirt/exp/*`, 그리고 이번에 추가한 4 개(인자까지 고정):
`mkfs.ext4 -F -m 0 -E lazy_itable_init=0,lazy_journal_init=0 /dev/nvme1n1`, `mount -o noatime /dev/nvme1n1 /mnt/jsw_nvmevirt`,
`umount /mnt/jsw_nvmevirt`, `chown dccearth:dccearth /mnt/jsw_nvmevirt`. 실험이 끝나면 사용자가 `sudo rm /etc/sudoers.d/nvmevirt-exp` 로 지운다.
`/dev/nvme0n1` 은 실제 시스템 디스크(Samsung 980 PRO)다. 스크립트는 장치 모델이 `CSL_Virt*` 이고 이름이 정확히 `nvme1n1` 일 때만 포맷한다.

## 3. 실험 설계 (실제로 돈 사양)

### 3.1 fio 재측정 — 44 회 (wbuffix, merge 는 순차만)
| 결과 폴더 (`repo/exp/results/`) | 작업 | 매핑 | bs | 모델 | 블록 계층 병합 | 회차 |
|---|---|---|---|---|---|---|
| `rand4x3_k147_20261025/wbuffix` | randwrite | 4/8/16/32K | 4/16/32K | wbuffix | 커널 기본(0) | 12 |
| `seq4x3_k147_20261025/{wbuffix,merge}` | write(순차) | 4/8/16/32K | 4/16/32K | wbuffix, merge | nomerges=2 | 24 |
| `randbs_k147_20261025/wbuffix` | randwrite | 4/8/16/32K | 8/64K | wbuffix | 커널 기본(0) | 8 |
| `rand4x5_k147_20261025/wbuffix` | (보기) rand4x3 + randbs 심볼릭 링크 | 4/8/16/32K | 4/8/16/32/64K | | | 20 |

공통: fio libaio, `direct=1`, iodepth 32, numjobs 1, **runtime 120 s** time_based, ramp 0, `randrepeat=1`, 0.5 초 평균 로그,
회차마다 rmmod → insmod(빈 FTL) → 5 초 대기 → fio → rmmod(GC 통계 출력), 페이지 캐시 drop 없음(nodrop), 1 회씩.
이전(커널 142)과 다른 점: 매핑 8K 추가, 60 s → 120 s, 3 회 → 1 회, drop 조건 없음. 작업 파일 = `repo/exp/jobs/{randwrite,seqwrite}.fio.in`.

### 3.2 RocksDB / YCSB-A — 32 회 (`rocksdb_ycsba_k147_20261025/wbuffix`)
- 행렬: 매핑 {4,8,16,32}K × RocksDB `block_size` {4,8,16,32}K × WAL {off, on}. 순서: 매핑 → block → WAL(off, on 연달아).
- 모델 wbuffix. 회차 절차(`repo/exp/run_rocksdb_ycsb.sh`):
  1. rmmod → insmod `nvmev_map<M>.ko` (빈 장치) → 장치가 `nvme1n1`·`CSL_Virt*`·크기 범위·마운트 안 됨인지 확인
  2. `mkfs.ext4 -F -m 0 -E lazy_itable_init=0,lazy_journal_init=0 /dev/nvme1n1` → `mount -o noatime` → `/mnt/jsw_nvmevirt/db`
  3. YCSB **load**: workloada, `recordcount=3000000`, 1 스레드, 같은 WAL 설정 (끝나면 DB 를 닫는다)
  4. 곧바로 YCSB **run**: workloada, 1 스레드, `operationcount=1000000000`, `maxexecutiontime=600` (600 초에 멈춤)
  5. RocksDB LOG·OPTIONS 복사 → umount → rmmod (NVMeVirt GC 통계)
  6. `ycsb_parse.py` 로 result.json 을 만들고 검사: load INSERT OK = 3,000,000, READ/UPDATE 에 OK 아닌 응답 0, run ≥ 570 초
- YCSB 명령(회차마다 meta.txt 의 `load_cmd`/`run_cmd` 에 그대로 기록):
  `taskset -c 0-2 java -cp <ycsb>/lib/* site.ycsb.Client -load|-t -db site.ycsb.db.rocksdb.RocksDBClient -P workloads/workloada
  -p recordcount=3000000 -p rocksdb.dir=/mnt/jsw_nvmevirt/db -p rocksdb.optionsfile=<회차>/rocksdb_options.ini
  -p rocksdb.disablewal=true|false -p rocksdb.sync=false -p measurementtype=hdrhistogram
  -p hdrhistogram.percentiles=50,90,95,99,99.9,99.99 -threads 1 -s -p status.interval=1` (+ run: `-p operationcount=1000000000 -p maxexecutiontime=600`)
- workloada: `readproportion=0.5 updateproportion=0.5 requestdistribution=zipfian readallfields=true`, 필드 10 × 100 B.
- RocksDB 옵션(`repo/exp/rocksdb/options.ini.in`, 회차별 사본 `rocksdb_options.ini`): `create_if_missing`, `create_missing_column_families`,
  `use_direct_reads=true`, `use_direct_io_for_flush_and_compaction=true`, `max_background_jobs=2`, `stats_dump_period_sec=60`,
  두 CF 모두 `compression=kNoCompression`, `block_size=<회차 값>`, `block_cache=8388608`(8 MiB). 나머지는 RocksDB 11.8.1 기본값
  (실제 적용값은 회차의 `rocksdb/OPTIONS-*`).
- WAL off = `disableWAL=true` (load·run 모두). WAL on 은 `sync=false`: WAL 은 페이지 캐시를 거쳐 쓰이고 커널 writeback 이 장치로 보낸다.
- 측정값: TPS = run 의 `[OVERALL] Throughput(ops/sec)`, 지연 = `[READ]`·`[UPDATE]` 의 평균과 p50–p99.99 (µs, hdrhistogram).
  추가 기록: 1 초 status(처리량·지연), 장치 I/O 카운터(1 초, 단계 경계), RocksDB LOG(60 초마다 통계), NVMeVirt GC 통계(세션 전체), DB 크기.

## 4. 시험 실행 (결과에 넣지 않음, 2026-10-25 01:24 – 01:27 KST)
| 폴더 | 내용 | 확인한 것 |
|---|---|---|
| `results/pre_k147_trial/merge` | fio 순차 merge 매핑 8K bs 4K, 10 초 | 147 용 모듈 적재, fio 동작 (2,114.8 MiB/s) |
| `results/pre_k147_trial_rdb/wbuffix` | RocksDB 매핑 4K block 4K WAL off/on, 10 만 건, run 20 초 | sudo mkfs/mount/umount 규칙 일치, 파싱·검사 동작, WAL off 에서 레코드 유실 없음 |
| `results/pre_k147_trial_rdb_full/wbuffix` | 매핑 32K block 4K WAL on, **300 만 건**, run 60 초 | 적재 12.5 초, DB 3.53 GB(장치 12.04 GB 의 29 %), 첫 GC 는 load 중(시작 후 10.9 초) |

full 시험에서 본 것: load 가 240K ops/s 로 끝나 compaction 이 밀린 채(L0 21 개, 「Stalling writes because we have 21 level-0 files」,
예상 미처리 compaction 5.9 GB) run 이 시작되어 run 1–4 초 130–200 ops/s, 5–9 초 약 2,700, 11–17 초 약 13,000, 이후 7,500 → 4,900 → 3,600 ops/s.
→ §1.8 의 질문. 사용자 결정에 따라 대기 단계를 넣지 않았다. 10 분 평균 TPS 에는 이 초반 구간이 들어 있다.

<!-- BEGIN MANUAL: run log -->
## 5. 실행 기록 (KST)

| 시각 | 일 |
|---|---|
| 01:24 – 01:27 | 시험 실행 3 개(§4) |
| 01:29:45 | tmux 세션 `ksc_k147` 에서 `bash run_all_k147.sh 20261025` 시작 (커밋 bab6eef) |
| 01:29:45 – 01:55:50 | ① 랜덤 쓰기 rand4x3_k147 12 회 |
| 01:32 | 첫 검토 워크플로(01:32:22 시작)를 01:32:35 에 멈추고 규칙을 좁혀 01:32:52 에 다시 시작(§11). 남은 프로세스 없음 확인 |
| 01:55:50 – 02:21:55 | ② 순차 쓰기 seq4x3_k147 wbuffix 12 회 |
| 02:09 – 02:10 | 검토 반영 커밋 3fe1c6d (02:09; RocksDB 스크립트, link_runs.py·make_handoff.sh 수정, 보고 스크립트와 이 기록 초안 추가. fio 회차 스크립트 run_experiment.sh·common.sh·jobs 는 그대로). 02:10 에 새 안전장치가 fio 실행 중 시작을 거부하는 것을 실제로 확인 |
| 02:21:55 – 02:48:00 | ② 순차 쓰기 seq4x3_k147 merge 12 회 |
| 02:48:00 – 03:05:24 | ③ 랜덤 쓰기 bs 추가 randbs_k147 8 회 |
| 03:05:24 – 03:05:30 | fio 분석(analyze.py × 3), 보기 rand4x5_k147 (20 회 링크), 보기 분석 |
| 03:05:30 | ④ RocksDB rocksdb_ycsba_k147 32 회 시작 |
| 03:15:43 | RocksDB 1 회차(map4k_blk4k_waloff) 정상 종료: TPS 6,198.4, READ p99 511 µs, UPDATE p99 513 µs, 적재 8.34 초, run 동안 CPU 0–2 사용률 3.1 %, CPU 압력(PSI) 0.07 % |

fio 44 회: FAILED 0, 커널 경고·채널 모델 메시지 0. 회차당 약 2 분 10 초.
전체 로그 `repo/exp/results/run_all_k147_20261025.log`(UTC), KST 변환본은 묶음의 `server_state/run_all_k147_20261025.KST.log`.

| 03:05:30 – 08:33:46 | ④ RocksDB 32 회 (회차당 평균 10 분 16 초: meta.txt 의 start→end 611–616 초 + 모듈 적재·정리. load 8–13 초, run 600 초) |
| 08:33:47 – 08:33:48 | 환경 스냅샷(env_after_wbuffix), analyze_rocksdb.py(32 회, FAILED 0), 마스터 종료(EXIT=0) |
| 08:3x – | (Claude) fio plot.py·갤러리, 공유본(make_share_k147.py), 결과 표(make_md_k147.py), 이 기록, 검증, 인계 묶음 |

RocksDB 32 회: FAILED 0, READ/UPDATE 의 OK 아닌 응답 0, 커널 경고 0. run 단계 LOG 의 쓰기 지연(stall) 기록은 32 회 중 4 회에 1 번씩(모두 WAL on: map4k·map8k·map32k 의 blk4k, map32k_blk8k).
<!-- END MANUAL: run log -->

<!-- BEGIN AUTO: tables -->
## 6. 결과 표 (자동 생성: exp/report/make_md_k147.py — 손으로 고치지 말 것)

### fio 랜덤 쓰기 (rand4x5_k147: 매핑 4 × bs 5, wbuffix)

rand4x3_k147(bs 4/16/32K) 과 randbs_k147(bs 8/64K) 을 합친 보기. 블록 계층 병합은 커널 기본값.

**wbuffix** — 120 초 평균 대역폭 (MiB/s), 행 = 매핑 단위, 열 = fio bs

| 매핑 \ bs | 4K | 8K | 16K | 32K | 64K |
|---|---:|---:|---:|---:|---:|
| 4K | 326.5 | 360.1 | 419.8 | 421.2 | 425.1 |
| 8K | 148.6 | 328.9 | 354.5 | 421.2 | 424.9 |
| 16K | 88.4 | 149.0 | 330.9 | 360.6 | 425.1 |
| 32K | 47.3 | 89.6 | 150.6 | 336.6 | 382.5 |

**wbuffix** — GC 이전 구간 평균 대역폭 (MiB/s)

| 매핑 \ bs | 4K | 8K | 16K | 32K | 64K |
|---|---:|---:|---:|---:|---:|
| 4K | 2,010.5 | 2,211.0 | 2,217.7 | 2,217.8 | 2,217.9 |
| 8K | 1,091.5 | 2,182.6 | 2,200.6 | 2,217.3 | 2,217.9 |
| 16K | 535.6 | 1,072.0 | 2,143.2 | 2,173.1 | 2,217.9 |
| 32K | 256.1 | 512.6 | 1,026.4 | 2,032.8 | 2,124.2 |

**wbuffix** — GC 이후 구간 평균 대역폭 (MiB/s)

| 매핑 \ bs | 4K | 8K | 16K | 32K | 64K |
|---|---:|---:|---:|---:|---:|
| 4K | 237.9 | 271.2 | 333.5 | 334.9 | 339.0 |
| 8K | 103.3 | 240.0 | 265.9 | 335.0 | 338.9 |
| 16K | 66.9 | 104.6 | 243.9 | 273.5 | 339.1 |
| 32K | 36.3 | 67.3 | 104.5 | 247.3 | 298.9 |

**wbuffix** — 첫 GC 시각 (fio 시작 후 초)

| 매핑 \ bs | 4K | 8K | 16K | 32K | 64K |
|---|---:|---:|---:|---:|---:|
| 4K | 6.29 | 5.74 | 5.69 | 5.69 | 5.69 |
| 8K | 5.81 | 5.82 | 5.77 | 5.70 | 5.69 |
| 16K | 5.91 | 5.90 | 5.92 | 5.84 | 5.69 |
| 32K | 6.06 | 6.07 | 6.07 | 6.10 | 5.97 |

**wbuffix** — WAF_total (NAND 바이트 ÷ 호스트 바이트, 120 초 전체)

| 매핑 \ bs | 4K | 8K | 16K | 32K | 64K |
|---|---:|---:|---:|---:|---:|
| 4K | 3.84 | 3.88 | 4.01 | 4.00 | 3.99 |
| 8K | 8.95 | 3.83 | 3.88 | 4.00 | 3.99 |
| 16K | 13.62 | 8.91 | 3.80 | 3.84 | 3.99 |
| 32K | 25.06 | 13.73 | 8.88 | 3.78 | 3.68 |

**wbuffix** — 평균 완료 지연 (µs)

| 매핑 \ bs | 4K | 8K | 16K | 32K | 64K |
|---|---:|---:|---:|---:|---:|
| 4K | 382 | 693 | 1,189 | 2,372 | 4,702 |
| 8K | 840 | 759 | 1,409 | 2,372 | 4,704 |
| 16K | 1,414 | 1,677 | 1,510 | 2,772 | 4,702 |
| 32K | 2,644 | 2,789 | 3,319 | 2,969 | 5,226 |

**wbuffix** — p99 완료 지연 (µs)

| 매핑 \ bs | 4K | 8K | 16K | 32K | 64K |
|---|---:|---:|---:|---:|---:|
| 4K | 14,221 | 16,712 | 17,695 | 18,219 | 19,005 |
| 8K | 16,450 | 15,663 | 17,433 | 18,481 | 19,005 |
| 16K | 16,187 | 17,170 | 16,908 | 18,219 | 19,005 |
| 32K | 16,450 | 17,170 | 17,695 | 17,695 | 18,743 |

이상 신호: kernel_warn·chmodel_msgs 가 0 이 아닌 회차 0 개

### fio 순차 쓰기 (seq4x3_k147: 매핑 4 × bs 3 × 모델 2)

블록 계층 병합 끔(nomerges=2).

**wbuffix** — 120 초 평균 대역폭 (MiB/s), 행 = 매핑 단위, 열 = fio bs

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 2,081.6 | 2,232.4 | 2,232.7 |
| 8K | 352.6 | 2,232.5 | 2,232.4 |
| 16K | 288.5 | 2,232.5 | 2,232.6 |
| 32K | 185.6 | 326.0 | 2,232.2 |

**wbuffix** — GC 이전 구간 평균 대역폭 (MiB/s)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 2,137.1 | 2,233.2 | 2,233.0 |
| 8K | 1,109.9 | 2,233.1 | 2,233.1 |
| 16K | 556.1 | 2,233.0 | 2,233.1 |
| 32K | 278.5 | 1,109.9 | 2,233.0 |

**wbuffix** — GC 이후 구간 평균 대역폭 (MiB/s)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 2,079.2 | 2,232.6 | 2,232.9 |
| 8K | 316.2 | 2,232.7 | 2,232.6 |
| 16K | 275.8 | 2,232.7 | 2,232.7 |
| 32K | 181.3 | 288.4 | 2,232.4 |

**wbuffix** — 첫 GC 시각 (fio 시작 후 초)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 5.94 | 5.69 | 5.69 |
| 8K | 5.69 | 5.69 | 5.69 |
| 16K | 5.69 | 5.69 | 5.69 |
| 32K | 5.69 | 5.69 | 5.69 |

**wbuffix** — WAF_total (NAND 바이트 ÷ 호스트 바이트, 120 초 전체)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 1.00 | 1.00 | 1.00 |
| 8K | 3.65 | 1.00 | 1.00 |
| 16K | 5.73 | 1.00 | 1.00 |
| 32K | 9.96 | 3.63 | 1.00 |

**wbuffix** — 평균 완료 지연 (µs)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 59 | 223 | 446 |
| 8K | 354 | 222 | 446 |
| 16K | 432 | 223 | 446 |
| 32K | 672 | 1,532 | 446 |

**wbuffix** — p99 완료 지연 (µs)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 63 | 228 | 453 |
| 8K | 8,454 | 228 | 453 |
| 16K | 3,785 | 226 | 453 |
| 32K | 2,310 | 8,585 | 449 |

이상 신호: kernel_warn·chmodel_msgs 가 0 이 아닌 회차 0 개

**merge** — 120 초 평균 대역폭 (MiB/s), 행 = 매핑 단위, 열 = fio bs

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 2,076.3 | 2,232.7 | 2,232.7 |
| 8K | 2,087.4 | 2,232.6 | 2,232.7 |
| 16K | 2,092.7 | 2,232.6 | 2,232.6 |
| 32K | 2,081.6 | 2,232.2 | 2,232.2 |

**merge** — GC 이전 구간 평균 대역폭 (MiB/s)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 2,135.2 | 2,233.1 | 2,233.0 |
| 8K | 2,142.3 | 2,233.0 | 2,233.0 |
| 16K | 2,148.5 | 2,233.0 | 2,233.0 |
| 32K | 2,142.9 | 2,232.8 | 2,233.0 |

**merge** — GC 이후 구간 평균 대역폭 (MiB/s)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 2,073.7 | 2,232.8 | 2,232.9 |
| 8K | 2,085.0 | 2,232.8 | 2,232.9 |
| 16K | 2,090.3 | 2,232.7 | 2,232.8 |
| 32K | 2,078.9 | 2,232.4 | 2,232.4 |

**merge** — 첫 GC 시각 (fio 시작 후 초)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 5.95 | 5.69 | 5.69 |
| 8K | 5.93 | 5.69 | 5.69 |
| 16K | 5.91 | 5.69 | 5.69 |
| 32K | 5.93 | 5.69 | 5.69 |

**merge** — WAF_total (NAND 바이트 ÷ 호스트 바이트, 120 초 전체)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 1.00 | 1.00 | 1.00 |
| 8K | 1.00 | 1.00 | 1.00 |
| 16K | 1.00 | 1.00 | 1.00 |
| 32K | 1.00 | 1.00 | 1.00 |

**merge** — 평균 완료 지연 (µs)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 59 | 223 | 446 |
| 8K | 59 | 223 | 446 |
| 16K | 59 | 222 | 446 |
| 32K | 59 | 223 | 446 |

**merge** — p99 완료 지연 (µs)

| 매핑 \ bs | 4K | 16K | 32K |
|---|---:|---:|---:|
| 4K | 63 | 226 | 449 |
| 8K | 62 | 228 | 449 |
| 16K | 62 | 226 | 453 |
| 32K | 62 | 226 | 449 |

이상 신호: kernel_warn·chmodel_msgs 가 0 이 아닌 회차 0 개

### 커널 142 결과와 비교 (같은 조합, 처음 60 초)

142 는 60 초 × 3 회, 147 은 120 초 × 1 회라 전체 평균은 비교할 수 없다. 두 커널 모두 fio 대역폭 로그(0.5 초 평균)의 0–60 초 구간 평균으로 비교한다.

| 실험 | 매핑 | bs | 142: 0–60 초 평균 (3 회 평균) | 147: 0–60 초 평균 (1 회) | 차이 % | 142 첫 GC (초) | 147 첫 GC (초) |
|---|---|---|---:|---:|---:|---:|---:|
| 랜덤 쓰기 | 4K | 4K | 416.7 | 415.8 | -0.22 | 6.32 | 6.29 |
| 랜덤 쓰기 | 4K | 16K | 481.1 | 480.9 | -0.03 | 5.69 | 5.69 |
| 랜덤 쓰기 | 4K | 32K | 482.4 | 482.5 | +0.03 | 5.69 | 5.69 |
| 랜덤 쓰기 | 16K | 4K | 129.7 | 129.7 | +0.01 | 5.91 | 5.91 |
| 랜덤 쓰기 | 16K | 16K | 420.4 | 421.0 | +0.13 | 5.92 | 5.92 |
| 랜덤 쓰기 | 16K | 32K | 441.7 | 439.9 | -0.40 | 5.84 | 5.84 |
| 랜덤 쓰기 | 32K | 4K | 68.3 | 68.3 | +0.03 | 6.06 | 6.06 |
| 랜덤 쓰기 | 32K | 16K | 219.6 | 219.6 | -0.03 | 6.06 | 6.07 |
| 랜덤 쓰기 | 32K | 32K | 424.7 | 424.7 | -0.00 | 6.10 | 6.10 |
| 랜덤 쓰기 bs 8K·64K | 4K | 8K | 437.1 | 441.7 | +1.06 | 5.74 | 5.74 |
| 랜덤 쓰기 bs 8K·64K | 4K | 64K | 486.4 | 486.4 | -0.01 | 5.69 | 5.69 |
| 랜덤 쓰기 bs 8K·64K | 16K | 8K | 217.3 | 217.5 | +0.07 | 5.90 | 5.90 |
| 랜덤 쓰기 bs 8K·64K | 16K | 64K | 486.5 | 486.4 | -0.01 | 5.69 | 5.69 |
| 랜덤 쓰기 bs 8K·64K | 32K | 8K | 132.0 | 131.8 | -0.14 | 6.07 | 6.07 |
| 랜덤 쓰기 bs 8K·64K | 32K | 64K | 447.2 | 447.2 | +0.00 | 5.97 | 5.97 |
| 순차 쓰기 wbuffix | 4K | 4K | 2,090.0 | 2,084.4 | -0.27 | 5.91 | 5.94 |
| 순차 쓰기 wbuffix | 4K | 16K | 2,232.6 | 2,232.7 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 wbuffix | 4K | 32K | 2,232.9 | 2,233.0 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 wbuffix | 16K | 4K | 334.9 | 335.2 | +0.09 | 5.69 | 5.69 |
| 순차 쓰기 wbuffix | 16K | 16K | 2,232.7 | 2,232.8 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 wbuffix | 16K | 32K | 2,232.7 | 2,232.8 | +0.01 | 5.69 | 5.69 |
| 순차 쓰기 wbuffix | 32K | 4K | 209.5 | 209.5 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 wbuffix | 32K | 16K | 369.1 | 369.1 | +0.01 | 5.69 | 5.69 |
| 순차 쓰기 wbuffix | 32K | 32K | 2,232.4 | 2,232.5 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 merge | 4K | 4K | 2,087.0 | 2,080.1 | -0.33 | 5.93 | 5.95 |
| 순차 쓰기 merge | 4K | 16K | 2,232.9 | 2,232.9 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 merge | 4K | 32K | 2,233.0 | 2,232.9 | -0.00 | 5.69 | 5.69 |
| 순차 쓰기 merge | 16K | 4K | 2,094.7 | 2,095.8 | +0.05 | 5.90 | 5.91 |
| 순차 쓰기 merge | 16K | 16K | 2,232.8 | 2,232.8 | -0.00 | 5.69 | 5.69 |
| 순차 쓰기 merge | 16K | 32K | 2,232.8 | 2,232.8 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 merge | 32K | 4K | 2,094.9 | 2,085.7 | -0.44 | 5.91 | 5.93 |
| 순차 쓰기 merge | 32K | 16K | 2,232.5 | 2,232.5 | +0.00 | 5.69 | 5.69 |
| 순차 쓰기 merge | 32K | 32K | 2,232.5 | 2,232.5 | +0.00 | 5.69 | 5.69 |

겹치는 33 조합의 |차이|: 평균 0.10 %, 최대 1.06 %

### RocksDB / YCSB-A (32 회, 회차마다 1 회)

행 = FTL 매핑 단위, 열 = RocksDB block_size. TPS = run 600 초의 YCSB `[OVERALL] Throughput`.

**WAL off — TPS (ops/s)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 6,198 | 6,019 | 5,213 | 4,780 |
| 8K | 5,731 | 5,628 | 4,995 | 4,581 |
| 16K | 5,075 | 5,057 | 4,481 | 4,336 |
| 32K | 4,238 | 4,206 | 3,878 | 3,754 |

**WAL off — READ p99 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 511 | 515 | 543 | 591 |
| 8K | 553 | 555 | 570 | 616 |
| 16K | 627 | 612 | 630 | 651 |
| 32K | 754 | 731 | 738 | 756 |

**WAL off — UPDATE p99 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 513 | 517 | 545 | 593 |
| 8K | 555 | 558 | 572 | 618 |
| 16K | 629 | 613 | 632 | 653 |
| 32K | 755 | 725 | 740 | 758 |

**WAL off — READ 평균 지연 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 159.5 | 164.4 | 190.3 | 207.4 |
| 8K | 172.8 | 175.9 | 198.5 | 216.7 |
| 16K | 195.2 | 196.0 | 221.3 | 228.8 |
| 32K | 234.3 | 236.2 | 255.9 | 264.7 |

**WAL off — UPDATE 평균 지연 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 161.6 | 166.3 | 191.7 | 209.3 |
| 8K | 174.6 | 177.8 | 200.3 | 218.3 |
| 16K | 197.3 | 197.9 | 223.4 | 230.9 |
| 32K | 236.0 | 237.7 | 258.1 | 266.4 |

**WAL off — run 동안 장치 읽기 (MiB/s)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 87.9 | 130.0 | 196.6 | 333.6 |
| 8K | 80.4 | 118.5 | 186.0 | 324.1 |
| 16K | 71.2 | 106.5 | 168.8 | 302.0 |
| 32K | 60.2 | 88.8 | 146.0 | 261.5 |

**WAL off — run 동안 평균 읽기 요청 크기 (KiB)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 6.66 | 10.15 | 17.93 | 33.86 |
| 8K | 6.61 | 10.08 | 18.06 | 33.96 |
| 16K | 6.63 | 10.10 | 18.00 | 33.87 |
| 32K | 6.79 | 10.15 | 18.20 | 33.95 |

**WAL off — run 동안 장치 쓰기 (MiB/s)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 22.3 | 22.9 | 18.5 | 17.8 |
| 8K | 20.0 | 20.4 | 18.7 | 18.2 |
| 16K | 18.1 | 18.6 | 16.7 | 16.3 |
| 32K | 16.5 | 16.1 | 16.0 | 14.8 |

**WAL off — run 동안 RocksDB compaction 쓰기 (GB, LOG 이벤트 합)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 12.50 | 12.93 | 10.36 | 10.06 |
| 8K | 11.22 | 11.47 | 10.58 | 10.35 |
| 16K | 10.18 | 10.51 | 9.43 | 9.22 |
| 32K | 9.33 | 9.10 | 9.12 | 8.37 |

**WAL off — run 동안 CPU 0–2 사용률 (%)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 3.1 | 3.1 | 3.0 | 3.2 |
| 8K | 2.7 | 2.8 | 2.8 | 3.1 |
| 16K | 2.5 | 2.6 | 2.6 | 2.9 |
| 32K | 2.1 | 2.2 | 2.2 | 2.6 |

**WAL off — 적재 시간 (초)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 8.3 | 9.6 | 9.4 | 9.2 |
| 8K | 8.3 | 9.7 | 9.3 | 9.2 |
| 16K | 8.5 | 9.8 | 9.5 | 9.4 |
| 32K | 8.3 | 9.6 | 9.4 | 8.8 |

**WAL off — NVMeVirt GC 횟수 (mkfs + load + run 전체)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 1,418 | 1,671 | 1,234 | 1,211 |
| 8K | 1,208 | 1,471 | 1,342 | 1,219 |
| 16K | 1,108 | 1,347 | 1,125 | 1,130 |
| 32K | 956 | 1,220 | 1,085 | 1,050 |

**WAL off — WAF (NAND 쓰기 ÷ 호스트 쓰기, mkfs + load + run 전체)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 1.06 | 1.07 | 1.04 | 1.06 |
| 8K | 1.05 | 1.07 | 1.08 | 1.05 |
| 16K | 1.07 | 1.08 | 1.05 | 1.07 |
| 32K | 1.06 | 1.11 | 1.06 | 1.11 |

**WAL on — TPS (ops/s)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 6,005 | 6,048 | 5,252 | 4,901 |
| 8K | 5,693 | 5,676 | 5,066 | 4,709 |
| 16K | 5,086 | 5,098 | 4,581 | 4,405 |
| 32K | 4,266 | 4,328 | 4,050 | 3,904 |

**WAL on — READ p99 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 521 | 515 | 538 | 587 |
| 8K | 553 | 550 | 565 | 611 |
| 16K | 619 | 576 | 627 | 651 |
| 32K | 740 | 675 | 730 | 752 |

**WAL on — UPDATE p99 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 525 | 519 | 542 | 591 |
| 8K | 556 | 554 | 569 | 616 |
| 16K | 624 | 589 | 631 | 655 |
| 32K | 743 | 679 | 733 | 756 |

**WAL on — READ 평균 지연 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 163.8 | 162.8 | 187.5 | 201.4 |
| 8K | 173.1 | 173.3 | 194.5 | 209.4 |
| 16K | 193.7 | 193.2 | 215.2 | 224.6 |
| 32K | 231.6 | 228.2 | 244.2 | 253.2 |

**WAL on — UPDATE 평균 지연 (µs)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 167.5 | 166.2 | 191.6 | 204.9 |
| 8K | 176.5 | 177.3 | 198.5 | 213.5 |
| 16K | 197.8 | 197.4 | 219.7 | 227.6 |
| 32K | 235.4 | 232.1 | 247.9 | 257.2 |

**WAL on — run 동안 장치 읽기 (MiB/s)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 83.6 | 127.4 | 194.0 | 331.5 |
| 8K | 79.4 | 117.5 | 184.2 | 319.2 |
| 16K | 70.3 | 105.4 | 168.1 | 297.9 |
| 32K | 59.2 | 88.4 | 144.1 | 259.5 |

**WAL on — run 동안 평균 읽기 요청 크기 (KiB)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 6.53 | 10.10 | 17.98 | 33.90 |
| 8K | 6.64 | 10.13 | 18.01 | 33.96 |
| 16K | 6.63 | 10.10 | 18.19 | 33.85 |
| 32K | 6.80 | 10.16 | 18.20 | 34.09 |

**WAL on — run 동안 장치 쓰기 (MiB/s)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 23.8 | 25.5 | 21.9 | 21.0 |
| 8K | 23.5 | 24.1 | 21.2 | 20.7 |
| 16K | 21.0 | 21.5 | 20.8 | 18.5 |
| 32K | 18.8 | 18.8 | 18.2 | 18.2 |

**WAL on — run 동안 RocksDB compaction 쓰기 (GB, LOG 이벤트 합)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 11.31 | 12.35 | 10.47 | 10.19 |
| 8K | 11.33 | 11.68 | 10.19 | 10.16 |
| 16K | 10.05 | 10.39 | 10.29 | 8.98 |
| 32K | 9.28 | 9.13 | 8.99 | 9.10 |

**WAL on — run 동안 CPU 0–2 사용률 (%)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 3.1 | 3.3 | 3.2 | 3.5 |
| 8K | 3.0 | 3.1 | 3.0 | 3.3 |
| 16K | 2.6 | 2.7 | 2.8 | 3.1 |
| 32K | 2.2 | 2.4 | 2.4 | 2.7 |

**WAL on — 적재 시간 (초)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 12.7 | 12.5 | 12.5 | 12.4 |
| 8K | 12.6 | 12.7 | 12.6 | 12.6 |
| 16K | 12.6 | 12.7 | 12.4 | 12.6 |
| 32K | 12.4 | 12.5 | 12.6 | 12.4 |

**WAL on — NVMeVirt GC 횟수 (mkfs + load + run 전체)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 2,375 | 2,439 | 2,093 | 2,041 |
| 8K | 2,379 | 2,397 | 2,128 | 2,165 |
| 16K | 2,104 | 2,118 | 2,098 | 1,995 |
| 32K | 2,212 | 1,900 | 2,072 | 2,139 |

**WAL on — WAF (NAND 쓰기 ÷ 호스트 쓰기, mkfs + load + run 전체)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | 1.12 | 1.09 | 1.07 | 1.08 |
| 8K | 1.13 | 1.11 | 1.10 | 1.12 |
| 16K | 1.12 | 1.10 | 1.11 | 1.13 |
| 32K | 1.21 | 1.10 | 1.17 | 1.19 |

**WAL on 의 TPS 변화 (WAL off 대비 %)**

| 매핑 \ block | 4K | 8K | 16K | 32K |
|---|---:|---:|---:|---:|
| 4K | -3.1 | 0.5 | 0.8 | 2.5 |
| 8K | -0.7 | 0.8 | 1.4 | 2.8 |
| 16K | 0.2 | 0.8 | 2.2 | 1.6 |
| 32K | 0.7 | 2.9 | 4.4 | 4.0 |

READ/UPDATE 가 OK 가 아닌 응답을 받은 회차: 0 개. kernel_warn 이 0 이 아닌 회차: 0 개.

<!-- END AUTO: tables -->

<!-- BEGIN MANUAL: findings -->
## 7. 관찰과 해석

모든 값은 조건마다 1 회 측정이다. 이전 fio 실험(커널 142, 3 회 반복)의 반복 간 대역폭 변동계수는 최대 0.4 %(조건별 0.001–0.40 %, 중앙값 0.04 %)였지만,
RocksDB 는 반복 측정이 없어 회차 간 잡음의 크기를 모른다. 아래 「차이」는 그 점을 감안해 읽는다.

### 7.1 fio 재측정 (커널 147)
- **커널 영향 없음.** 142 와 147 에서 같은 33 조합의 처음 60 초 평균 대역폭 차이는 평균 0.10 %, 최대 1.06 %(랜덤 쓰기 매핑 4K·bs 8K)이고, 첫 GC 시각도 같다(§6 비교 표).
  따라서 10-08 의 fio 결론(EXPERIMENT_LOG_FOR_CLAUDE.md §8)은 147 에서도 그대로다.
- 120 초 평균은 60 초 평균보다 낮다(예: 랜덤 4K/4K 326.5 vs 142 의 60 초 평균 416.0 MiB/s). GC 이후 구간(237.9 MiB/s)이 평균에 더 많이 들어가기 때문이며 커널 차이가 아니다.
- **랜덤 쓰기(매핑 4 × bs 5)**: 결과는 bs/매핑 비율로 거의 정해진다. 비율 1(4K/4K, 8K/8K, 16K/16K, 32K/32K) 326.5·328.9·330.9·336.6,
  비율 1/2(8K/4K, 16K/8K, 32K/16K) 148.6·149.0·150.6, 비율 1/4(16K/4K, 32K/8K) 88.4·89.6, 비율 1/8(32K/4K) 47.3 MiB/s.
  비율 2 는 354.5–382.5, 비율 4 이상은 419.8–425.1 MiB/s. 새로 잰 매핑 8K 도 같은 규칙을 따른다.
  bs < 매핑이면 쓰기마다 매핑 단위 전체를 써서 WAF_total = (매핑/bs) × WAF_gc 가 된다(8K/4K 8.95 = 2 × 4.48, 16K/4K 13.62 = 4 × 3.41, 32K/4K 25.06 = 8 × 3.13; bs = 매핑 대비로는 약 2.3·3.6·6.6 배; bs ≥ 매핑은 3.68–4.01).
- **순차 쓰기**: wbuffix 는 bs ≥ 매핑이면 2,081.6–2,232.7 MiB/s(WAF 1.00), bs < 매핑이면 185.6–352.6 MiB/s(WAF 3.63–9.96)로 크게 떨어진다.
  merge 모델은 모든 조합 2,076.3–2,232.7 MiB/s 로 손실이 없다(이전 결론과 같음: NVMeVirt 는 매핑 단위보다 작은 쓰기를 합치지 않는다).

### 7.2 RocksDB / YCSB-A
- **매핑 단위가 클수록 TPS 가 낮다.** 32 칸(4 block_size × 2 WAL × 매핑 4 단계)에서 예외 없이 단조 감소한다.
  매핑 4K 대비 8K −3.5 ~ −7.5 %, 16K −9.3 ~ −18.1 %, 32K −20.3 ~ −31.6 %. block_size 가 작을수록 매핑의 영향이 크다
  (WAL off: block 4K −31.6 %, 32K −21.5 %).
- **원인 — 읽기.** 이 워크로드에서 장치 쓰기는 run 동안 15–26 MiB/s 이고 대부분 flush·compaction 의 큰 요청(평균 214–247 KiB)이라,
  매핑 단위의 쓰기 불이익(작은 쓰기)이 거의 없다(세션 전체 WAF 1.04–1.21). 반면 데이터 블록 읽기는 block_size 크기(평균 요청 6.5–34 KiB)의 작은 direct read 다.
  NVMeVirt 의 읽기 모델은 요청 크기와 상관없이 **매핑 단위 전체를 NAND 채널로 옮기는 시간**을 매긴다(`repo/nvmevirt/conv_ftl.c` conv_read: 매핑 단위마다 `xfer_size += spp->pgsz`).
  그래서 매핑 단위가 커질수록 읽기 지연이 늘고(READ 평균 159.5 → 234.3 µs, block 4K WAL off), 스레드 1 개인 YCSB 의 TPS 가 그만큼 준다.
  읽기 p99 도 매핑 32K 에서 4K 대비 +27.9 ~ +47.6 % 크다.
- **block_size**: 4K 와 8K 는 비슷하고(−2.9 ~ +1.4 %), 16K·32K 에서 떨어진다(32K 는 4K 대비 −8.5 ~ −22.9 %). 블록이 클수록 Get 하나가 읽는 바이트가 늘어
  장치 읽기 대역폭은 늘지만(매핑 4K WAL off: 87.9 → 333.6 MiB/s) 처리량은 준다.
- **WAL on/off**: 차이는 −3.1 ~ +4.4 %(16 쌍 중 14 쌍에서 on 이 조금 높음, 평균 +1.4 %). WAL 은 `sync=false` 라 페이지 캐시에 쓰이고
  장치로는 큰 쓰기로 나가므로(run 장치 쓰기 WAL on 18.2–25.5 vs off 14.8–22.9 MiB/s) TPS 에 주는 부담이 작다. 1 회 측정이라 이 정도 차이는 잡음과 구분할 수 없다.
  WAL on 쪽이 조금 높은 이유는 확인하지 않았다(가설: WAL on 은 load 가 12.4–12.7 초로 길어(off 8.3–9.8 초) run 시작 때 밀린 compaction 이 다를 수 있음).
  참고: CF 가 2 개(default + usertable)라 WAL on 이면 memtable flush 전마다 닫힌 WAL 파일을 fsync 한다(RocksDB needs_to_sync_closed_wals).
- **UPDATE ≈ READ.** YCSB 의 update 는 Get + Put 이고 Put 은 memtable 에 쓰므로, UPDATE 지연은 READ 보다 평균 1.4–4.5 µs, p99 −6 ~ +13 µs 차이뿐이다.
- **시간에 따라 변함.** run 처리량은 60–90 초 주기의 톱니 모양(compaction 주기)이고 점점 떨어진다: 처음 60 초 5,436–7,641, 마지막 60 초 2,596–5,832 ops/s
  (마지막/처음 −15 ~ −53 %). 10 분 평균은 실행 시간에 따라 달라지는 값이다. `fig_tps_timeseries.png` 참고.
- **적재 직후 측정의 영향**(사용자 결정에 따라 대기 단계 없이 측정): 모든 회차에서 run 처음 3 초는 114–443 ops/s 로 낮고(8 회는 4 초째도 202–957 ops/s; load 직후 밀린 compaction, JVM 시작),
  5 초째에 1,590–4,757 ops/s, 12–18 초에 1 초 처리량 최고치 11,052–19,845 ops/s 에 이른다(`fig_tps_timeseries.png` 는 10 초 이동평균). 처음 4 초가 600 초 평균을 낮춘 몫은 0.55–0.64 % 다.
  run 단계 LOG 의 stall 기록은 WAL on 4 회에 1 번씩뿐이다(load 단계 LOG 에는 17 회에 22 건: WAL off 16 회 전부와 map16k_blk8k_walon; stop 기록은 0 건).
- **NVMeVirt GC**: WAL off 는 첫 GC 가 run 시작 2.2–4.6 초 뒤, WAL on 은 load 중(시작 10.8–11.5 초 뒤)에 시작한다(WAL 이 load 동안 약 3.5 GB 를 더 씀).
  GC 횟수(세션 전체)는 WAL off 956–1,671, on 1,900–2,439.
- **간섭 없음**: run 동안 CPU 0–2 사용률 2.1–3.5 %, CPU 압력 0.04–0.07 %. 이 워크로드(스레드 1)는 CPU 가 아니라 장치 지연이 정한다.
- 한계: NVMeVirt 는 TRIM 이 없어 지운 SST 파일도 유효 데이터로 GC 한다. 매핑 단위보다 작은 쓰기의 read-modify-write 읽기는 모델링하지 않는다.
  읽기는 매핑 단위 전체 전송으로 계산되므로, 실제 SSD(필요한 섹터만 전송할 수 있음)보다 매핑 단위의 읽기 불이익이 클 수 있다.
<!-- END MANUAL: findings -->

## 8. 산출물

| 무엇 | 묶음 경로 |
|---|---|
| 원자료 (회차 폴더) | `repo/exp/results/{rand4x3,seq4x3,randbs,rocksdb_ycsba}_k147_20261025/` (+ 보기 `rand4x5_k147_20261025/`) |
| fio 분석 표·그림 | `repo/exp/results/<실험>/analysis/` (summary_runs.csv, summary_agg.csv, fig_*.png) |
| RocksDB 분석 표·그림 | `repo/exp/results/rocksdb_ycsba_k147_20261025/analysis/` (summary_runs.csv/.json, fig_tps_heatmap.png, fig_read_p99_heatmap.png, fig_update_p99_heatmap.png, fig_tps_vs_block.png, fig_tps_timeseries.png) |
| **선배 전달용 복사본 (.csv / .json)** | `repo/exp/results/share_k147_20261025/` (README.md 에 파일·열 설명). 서버에는 같은 내용의 zip `~/jsw/handoff/ksc2026_k147_share_20261025.zip` |
| 이 기록 | `EXPERIMENT_LOG_K147_ROCKSDB.md` (묶음 루트, 원본 `repo/EXPERIMENT_LOG_K147_ROCKSDB.md`) |
| 인계 묶음 | 서버 `~/jsw/handoff/LATEST.tgz` → `ksc2026_handoff_<KST YYYYMMDD_HHMM>_k147.tgz` (`bash exp/report/make_handoff.sh k147`, 이 기록과 스크립트 목록(§9)이 묶음 루트·repo/ 에 있음) |

## 9. 실험에 사용한 스크립트와 파일 (사용자 요청 목록)

경로는 `repo/` 기준. 커밋: 실험 시작 시점은 `bab6eef`(01:29:45 KST). 2 분 뒤의 `e67701d` 는 run_rocksdb_ycsb.sh 만 바꿨다. fio 회차 스크립트(run_experiment.sh·common.sh·jobs·collect_env.sh·build_modules.sh)는 10-08 판 그대로이고, run_all_k147.sh·analyze.py·plot.py 는 `bab6eef` 판이다 (fio 44 회의 meta.txt git_head 는 bab6eef 1·e67701d 18·3fe1c6d 25 회지만 fio 드라이버는 세 커밋에서 같다). RocksDB 32 회(run_rocksdb_ycsb.sh·rocksdb/*)와 rand4x5 보기(link_runs.py)는 검토 반영 커밋 `3fe1c6d`(02:09 KST) 판으로 돌았다(회차 meta.txt 와 wbuffix/git_head.txt). 보고 스크립트의 최종판은 make_share_k147.py·make_md_k147.py·share_k147_README.md·make_gallery.py 가 이 기록과 같은 마지막 커밋, make_handoff.sh 가 `3fe1c6d` 다.

| 파일 | 역할 | 이번에 |
|---|---|---|
| `exp/run_all_k147.sh` | **마스터.** fio 3 부분(랜덤 12, 순차 24, bs 추가 8) → fio 분석 → RocksDB 32 회 → RocksDB 분석을 차례로 실행. 다시 실행하면 끝난 회차를 건너뛴다 | 새로 작성 |
| `exp/run_experiment.sh` | fio 회차 드라이버(rmmod/insmod, 장치 확인, nomerges, fio, 커널 로그, GC 통계, DONE/FAILED). 환경 변수 `MAPS BSS REPS RUNTIME CACHE_MODES WORKLOAD NOMERGES` | 그대로(10-08 실험과 같은 코드) |
| `exp/common.sh` | 공통 설정(insmod 인자, 기본값, 변형별 빌드 인자) | 그대로 |
| `exp/jobs/randwrite.fio.in`, `exp/jobs/seqwrite.fio.in` | fio 작업 템플릿 | 그대로 |
| `exp/collect_env.sh` | 환경 스냅샷(env_before / env_after_*) | 그대로 |
| `exp/build_modules.sh` | NVMeVirt 모듈 빌드(변형 × 매핑 단위) | 그대로(10-24 23:32 에 147 용으로 실행) |
| `exp/link_runs.py` | 여러 실험의 회차를 심볼릭 링크로 묶은 보기(rand4x5) | FAILED 회차도 링크하도록 수정(3fe1c6d, 검토 pipeline-4). 03:05 에 수정본으로 rand4x5 보기 생성 |
| `exp/analyze.py` | fio 결과 표(summary_runs/agg.csv)와 그림 | 그림 제목이 실행 시간·회차 수를 데이터에서 읽도록 수정(60 s·n=3 고정 → 120 s·single run) |
| `exp/plot.py` | fio 추가 그림(`plot.py all --exp results/<실험>` → `results/<실험>/plots/`) | 축 이름의 「60 s」 를 「run」 으로 |
| `exp/make_gallery.py` | 결과 폴더별 그림 갤러리 HTML(`results/<실험>/gallery_<실험>.html`, git·인계 묶음에서 제외) | 그림 설명을 실행 시간·회차 수에 맞게 일반화(60 s 고정 → 「60 s 또는 120 s」, 1 회 측정이면 오차막대 없음), RocksDB 그림 묶음과 k147 실험 제목 추가 |
| `exp/run_rocksdb_ycsb.sh` | **RocksDB 회차 드라이버** (§3.2 절차). 환경 변수 `RDB_MAPS RDB_BLOCKS RDB_WALS RECORDS RUN_SEC THREADS` | 새로 작성 |
| `exp/rocksdb/options.ini.in` | RocksDB 옵션 파일 템플릿(`@BLOCK_SIZE@`) | 새로 작성 |
| `exp/rocksdb/ycsb_parse.py` | 회차 하나 → `result.json`, `run_status.csv` + 검사 | 새로 작성 |
| `exp/rocksdb/analyze_rocksdb.py` | 32 회 → `analysis/summary_runs.csv/.json`, 그림 | 새로 작성 |
| `exp/report/make_share_k147.py` | 선배 전달용 `.csv/.json` 복사본(`results/share_k147_<D>/`)과 zip | 새로 작성 |
| `exp/report/share_k147_README.md` | 복사본 README(파일·열 설명) | 새로 작성 |
| `exp/report/make_md_k147.py` | 이 기록의 결과 표(§6) 자동 생성 | 새로 작성 |
| `exp/report/make_handoff.sh` | 인계 묶음(.tgz) 생성, `LATEST.tgz` 링크 | 이 기록을 묶음 루트에 넣도록 수정 |
| `exp/ycsb/ycsb-rocksdb-11.8.1.patch`, `exp/ycsb/README.md` | 정식 YCSB rocksdb 바인딩 패치와 빌드 방법 | 10-24 작성 |
| `exp/report/nvmevirt-exp.sudoers` | sudo 규칙 원본 | 10-24 mkfs/mount 규칙 추가 |
| `nvmevirt/` (conv_ftl.c, conv_ftl.h, ssd_config.h, ssd.c, Kbuild) | NVMeVirt 소스와 KSC2026 수정(WBUF_FIX, GC_STATS, WBUF_MERGE) | 그대로 |
| nvmevirt 저장소 밖(같은 실험 서버 dccearth, 인계 묶음에는 없음): `/home/dccearth/jsw/YCSB` (패치 적용, 브랜치 ksc2026-rocksdb-11.8.1 커밋 8cd243b4 — 묶음의 `repo/exp/ycsb/ycsb-rocksdb-11.8.1.patch` 로 재현), `/home/dccearth/jsw/ycsb-dist/…` (실행 파일), `/home/dccearth/jsw/rocksdb` (11.8.1 소스 빌드, 실험에는 미사용) | | |

## 10. 재현 방법 (실험 서버 기준, 기록용)
```bash
cd /home/dccearth/jsw/nvmevirt/exp
bash build_modules.sh wbuffix && MAPS="4k 8k 16k 32k" bash build_modules.sh merge      # 커널이 바뀌었을 때만
# sudo 규칙 설치(사용자): sudo install -m 0440 -o root -g root report/nvmevirt-exp.sudoers /etc/sudoers.d/nvmevirt-exp ; sudo mkdir -p /mnt/jsw_nvmevirt
tmux new -s ksc_k147 'bash run_all_k147.sh 20261025'
for e in rand4x3 seq4x3 randbs rand4x5; do ./.venv/bin/python plot.py all --exp results/${e}_k147_20261025; done
for e in rand4x3 seq4x3 randbs rand4x5 rocksdb_ycsba; do ./.venv/bin/python make_gallery.py results/${e}_k147_20261025; done
python3 report/make_share_k147.py 20261025
python3 report/make_md_k147.py 20261025
bash report/make_handoff.sh k147
```

<!-- BEGIN MANUAL: verification -->
## 11. 검증

- **실행 전 검토 워크플로 wf_a7fea7e7-59c** (2026-10-25 01:32 – 02:05 KST, 에이전트 8: 4 영역 검토 → 영역별 반박 검증; 반영·커밋 02:09, 안전장치 시험 02:10).
  첫 시도 wf_78a6eb90-b8a 는 01:32 에 시작해 13 초 만에 멈췄다: 검토자가 Java·그림 그리기를 돌리면 fio 가 쓰는 CPU 0–2 를 방해할 수 있어,
  「코드 읽기 + 1 초 미만 파서 시험만」으로 규칙을 좁혀 다시 돌렸다(멈춘 시점에 남은 프로세스 없음 확인).
  - 발견 19 개 중 16 개가 사실로 확인(중요도: medium 2, 나머지 low), 3 개는 반박됨. 측정값(TPS, p99)을 틀리게 만드는 결함은 없었다.
  - 반영(커밋 3fe1c6d, 02:09 KST, RocksDB 단계 시작 전, 파일마다 임시 파일 → 원자적 교체; fio 가 쓰는 run_experiment.sh·common.sh·jobs 는 건드리지 않음):
    - safety-1 (medium): 두 번째 인스턴스가 fio 실행 중에 rmmod 할 수 있음 → `flock` 한 인스턴스만 + `run_experiment.sh` 실행 중이면 거부(30 초 대기 후).
      02:10 KST 에 실제로 실행해 「run_experiment.sh (fio) is running on NVMeVirt — refusing」으로 아무것도 건드리지 않고 멈추는 것을 확인.
    - safety-2: 중단 시 trap 이 YCSB 종료를 기다리지 않고 umount → YCSB 가 끝날 때까지(최대 120 초) 기다린 뒤 umount·rmmod.
    - safety-3: Ctrl-C 가 YCSB 에 닿지 않고 로거만 죽어 DONE 이 빠질 수 있음 → DONE 을 로그 줄보다 먼저 기록. 중단은 Ctrl-C 대신 `kill <스크립트 pid>`.
    - safety-4 / method-1: load 실패 때 RocksDB LOG 가 사라짐 → fail_run 이 umount 전에 LOG·OPTIONS·파일 목록을 복사.
    - parsing-1 / pipeline-3: YCSB 가 끝에 찍는 몇 ms 짜리 status 줄이 1 초 표본처럼 쓰임 → `final_partial` 로 표시하고 구간 평균·그림에서 제외(원자료 유지).
    - parsing-2 / method-2: compaction 양이 마지막 60 초 통계 덤프 값이라 run 끝 약 60 초가 빠짐 → LOG 의 EVENT_LOG_v1(flush/compaction 작업별 SST 크기)로 단계 전체 합. 덤프 값은 `*_at_last_dump` 로 이름 변경.
    - parsing-3: 이동평균이 끝을 0 으로 채워 그림 끝이 떨어져 보임 → 가장자리 정규화. parsing-4: 그림 제목 600 s 고정 → 데이터에서.
    - method-5: READ·UPDATE 따로 TPS → `read_tps_ops_s`, `update_tps_ops_s` (합 = TPS, 시험 자료로 일치 확인).
    - method-4: CPU 0–2 간섭 기록 없음 → 1 초마다 `/proc/stat` cpu0–2 (`cpu_1s.txt`), 단계 경계마다 cpu0–2 + PSI (`cpu_phases.txt`), 결과 열 `run_cpu0_2_busy_pct`, `run_cpu_psi_some_pct`.
    - pipeline-4: 묶은 보기(rand4x5)에 FAILED 회차가 빠짐 → link_runs.py 가 FAILED 도 링크(분석에서는 failed_runs.csv 로).
    - 중단된 회차 폴더는 지우지 않고 `*.aborted.<시각>` 으로 옮긴다.
  - 반영하지 않음: pipeline-1(실행 중인 fio 스크립트를 고치면 안 됨 — 운영 규칙으로 지킴), pipeline-2(마스터의 `set -e` 로 한 단계가 die 하면 이후 단계가 건너뛰어짐 — 실행 중인 마스터는 바꿀 수 없어 감시로 대응).
  - 반박됨(결함 아님): parsing-5, method-3, method-6. method-6 의 권고(WAL 이 켜져 있으면 CF 가 2 개라 memtable flush 전마다 닫힌 WAL 파일을 fsync 한다)는 옵션 파일 주석에 한 줄 보탰다.
<!-- END MANUAL: verification -->

## 12. 마무리
- sudo 규칙: 사용자가 `sudo rm /etc/sudoers.d/nvmevirt-exp` 로 삭제(15:20:05 KST 보고). 다시 실험하려면 `repo/exp/report/nvmevirt-exp.sudoers` 를 사용자가 설치한다.
- GitHub push: 사용자가 15:23:02 KST 에 「ssh -A 접속했어. GitHub push 해줘.」 → origin/main(bc31375) 위로 커밋 8 개(becebf1 … 8d3e348)를 push 했다(15:24 KST, `bc31375..8d3e348  main -> main`, `git ls-remote` 로 원격 main = 8d3e348 확인). 이 기록의 push 결과를 적은 커밋도 이어서 push 했다(15:24 KST).
- 서버의 `exp/results/ftl.tgz`(15:16 KST, 공유본 폴더를 묶은 tar, 627 개 파일)는 Claude 가 만든 것이 아니다(사용자가 만든 것으로 보임). git 에 넣지 않았고 건드리지 않았다.
