# KSC2026 — 커널 6.8.0-147 재측정 + RocksDB/YCSB-A 실험 기록 (2026-10-24 ~ 10-25, Claude 인계용)

이 파일은 **2026-10-24 ~ 10-25 (KST)** 의 작업 전 과정을 다른 서버의 Claude 가 이어받을 수 있도록 적은 기록이다.
그 이전(2026-10-08 ~ 10-09)의 NVMeVirt fio 실험은 같은 묶음의 `EXPERIMENT_LOG_FOR_CLAUDE.md` 에 있다.

- 경로는 **인계 묶음(.tgz) 루트 기준**이다: `repo/…` = 실험 서버의 저장소 작업 트리(`/home/dccearth/jsw/nvmevirt`).
  이 묶음을 받은 Claude 는 실험 서버(dccearth)에 접근할 수 없다. 서버 경로는 기록용이다.
- 시각은 모두 **KST** 다. 원자료(로그, meta.txt, kernel.log)는 서버 시계 **UTC** 그대로다(KST = UTC + 9 시간).
- 답장·보고는 한국어로 한다(사용자 지시).

<!-- BEGIN MANUAL: status -->
## 0. 현재 상태 (STATUS)

(실험이 끝난 뒤 채운다)
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
> 4. YCSB-A는 연구실에서 쓰는 db_bench YCSB로 돌리면 될까요, 아니면 정식 YCSB를 써야 할까요? … → **최신 버전, 정식 ycsb**
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
run 처음 약 10 초가 130–200 ops/s 였다(§4). 「측정 전에 밀린 compaction 을 끝낼까?」 → **적재 직후 바로 측정**(YCSB 기본 절차).
그래서 run 단계는 load 가 끝난 직후 새 JVM 으로 시작한다(대기 단계 없음).

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
| `results/pre_k147_trial_rdb_full/wbuffix` | 매핑 32K block 4K WAL on, **300 만 건**, run 60 초 | 적재 12.5 초, DB 3.53 GB(장치의 31 %), 첫 GC 는 load 중(시작 후 10.9 초) |

full 시험에서 본 것: load 가 240K ops/s 로 끝나 compaction 이 밀린 채(L0 21 개, 「Stalling writes because we have 21 level-0 files」,
예상 미처리 compaction 5.9 GB) run 이 시작되어 run 1–4 초 130–200 ops/s, 5–9 초 약 2,700, 11–17 초 약 13,000, 이후 7,500 → 4,900 → 3,600 ops/s.
→ §1.8 의 질문. 사용자 결정에 따라 대기 단계를 넣지 않았다. 10 분 평균 TPS 에는 이 초반 구간이 들어 있다.

<!-- BEGIN MANUAL: run log -->
## 5. 실행 기록

- 2026-10-25 01:29:45 KST: tmux 세션 `ksc_k147` 에서 `bash run_all_k147.sh 20261025` 시작 (커밋 bab6eef; 01:3x 에 e67701d — 스크립트를 블록으로 감싼 것뿐).
  전체 로그 `repo/exp/results/run_all_k147_20261025.log`(UTC), KST 변환본은 묶음의 `server_state/run_all_k147_20261025.KST.log`.

(실험이 끝난 뒤 채운다)
<!-- END MANUAL: run log -->

<!-- BEGIN AUTO: tables -->
<!-- END AUTO: tables -->

<!-- BEGIN MANUAL: findings -->
## 7. 관찰과 해석

(실험이 끝난 뒤 채운다)
<!-- END MANUAL: findings -->

## 8. 산출물

| 무엇 | 묶음 경로 |
|---|---|
| 원자료 (회차 폴더) | `repo/exp/results/{rand4x3,seq4x3,randbs,rocksdb_ycsba}_k147_20261025/` (+ 보기 `rand4x5_k147_20261025/`) |
| fio 분석 표·그림 | `repo/exp/results/<실험>/analysis/` (summary_runs.csv, summary_agg.csv, fig_*.png) |
| RocksDB 분석 표·그림 | `repo/exp/results/rocksdb_ycsba_k147_20261025/analysis/` (summary_runs.csv/.json, fig_tps_heatmap.png, fig_read_p99_heatmap.png, fig_update_p99_heatmap.png, fig_tps_vs_block.png, fig_tps_timeseries.png) |
| **선배 전달용 복사본 (.csv / .json)** | `repo/exp/results/share_k147_20261025/` (README.md 에 파일·열 설명). 서버에는 같은 내용의 zip `~/jsw/handoff/ksc2026_k147_share_20261025.zip` |
| 이 기록 | `EXPERIMENT_LOG_K147_ROCKSDB.md` (묶음 루트, 원본 `repo/EXPERIMENT_LOG_K147_ROCKSDB.md`) |

## 9. 실험에 사용한 스크립트와 파일 (사용자 요청 목록)

경로는 `repo/` 기준. 커밋은 실험 시작 시점 `bab6eef`(+ `e67701d`).

| 파일 | 역할 | 이번에 |
|---|---|---|
| `exp/run_all_k147.sh` | **마스터.** fio 3 부분(랜덤 12, 순차 24, bs 추가 8) → fio 분석 → RocksDB 32 회 → RocksDB 분석을 차례로 실행. 다시 실행하면 끝난 회차를 건너뛴다 | 새로 작성 |
| `exp/run_experiment.sh` | fio 회차 드라이버(rmmod/insmod, 장치 확인, nomerges, fio, 커널 로그, GC 통계, DONE/FAILED). 환경 변수 `MAPS BSS REPS RUNTIME CACHE_MODES WORKLOAD NOMERGES` | 그대로(10-08 실험과 같은 코드) |
| `exp/common.sh` | 공통 설정(insmod 인자, 기본값, 변형별 빌드 인자) | 그대로 |
| `exp/jobs/randwrite.fio.in`, `exp/jobs/seqwrite.fio.in` | fio 작업 템플릿 | 그대로 |
| `exp/collect_env.sh` | 환경 스냅샷(env_before / env_after_*) | 그대로 |
| `exp/build_modules.sh` | NVMeVirt 모듈 빌드(변형 × 매핑 단위) | 그대로(10-24 23:32 에 147 용으로 실행) |
| `exp/link_runs.py` | 여러 실험의 회차를 심볼릭 링크로 묶은 보기(rand4x5) | 그대로 |
| `exp/analyze.py` | fio 결과 표(summary_runs/agg.csv)와 그림 | 그림 제목이 실행 시간·회차 수를 데이터에서 읽도록 수정(60 s·n=3 고정 → 120 s·single run) |
| `exp/plot.py` | fio 추가 그림 | 축 이름의 「60 s」 를 「run」 으로 |
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
| 서버 밖 저장소: `/home/dccearth/jsw/YCSB` (패치 적용), `/home/dccearth/jsw/ycsb-dist/…` (실행 파일), `/home/dccearth/jsw/rocksdb` (11.8.1 소스 빌드, 실험에는 미사용) | | |

## 10. 재현 방법 (실험 서버 기준, 기록용)
```bash
cd /home/dccearth/jsw/nvmevirt/exp
bash build_modules.sh wbuffix && bash build_modules.sh merge      # 커널이 바뀌었을 때만
# sudo 규칙 설치(사용자): sudo install -m 0440 -o root -g root report/nvmevirt-exp.sudoers /etc/sudoers.d/nvmevirt-exp ; sudo mkdir -p /mnt/jsw_nvmevirt
tmux new -s ksc_k147 'bash run_all_k147.sh 20261025'
python3 report/make_share_k147.py 20261025
python3 report/make_md_k147.py 20261025
bash report/make_handoff.sh k147
```

<!-- BEGIN MANUAL: verification -->
## 11. 검증

- 2026-10-25 01:3x KST: 실행 전 검토 워크플로(RocksDB 드라이버·파서·분석·마스터, 4 영역 × 반박 검증). 결과는 실험 뒤 채운다.
<!-- END MANUAL: verification -->

## 12. 남은 일
- sudo 규칙 삭제(사용자): `sudo rm /etc/sudoers.d/nvmevirt-exp`
- GitHub push(사용자 ssh-agent 연결 필요): 로컬 커밋이 origin/main(bc31375)보다 앞서 있다.
