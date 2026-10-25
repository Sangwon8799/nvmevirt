# KSC2026 FTL 매핑 단위 실험 — 결과 공유본 (2026-10-25, 커널 6.8.0-147)

원자료를 바꾸지 않고 복사해 `.csv` / `.json` 으로 정리한 폴더다. 모든 값은 **조건마다 1 회 측정**한 값이다.
같은 표가 `.csv` 와 `.json` 두 형식으로 들어 있다(내용 동일).

## 1. 공통 환경

| 항목 | 값 |
|---|---|
| 장치 | NVMeVirt conventional SSD (Samsung 970 PRO 설정 기반, 용량 11.2 GiB, OP 7 %, TRIM 없음) |
| 쓰기 버퍼 모델 | wbuffix (쓰기 버퍼가 매핑 단위로 차지되도록 고친 모델). 순차 쓰기에는 merge 모델(매핑 단위보다 작은 쓰기를 쓰기 버퍼에서 합침)도 측정 |
| FTL 매핑 단위 | 4 / 8 / 16 / 32 KiB (flash page 는 모두 32 KiB) |
| 서버 | Intel i5-13600K, 커널 6.8.0-147-generic, NVMeVirt 전용 CPU 3–5, 실험 프로그램 CPU 0–2 |
| 시작 상태 | 회차마다 NVMeVirt 모듈을 새로 올려 빈 장치에서 시작 |

## 2. RocksDB / YCSB-A (`rocksdb_*`)

- RocksDB 11.8.1 (RocksJava 11.8.1), 공식 YCSB(brianfrankcooper/YCSB, 2026-10-20 master) rocksdb 바인딩.
  바인딩은 RocksDB 11.8.1 에 맞추고 WAL 끄기 옵션(`rocksdb.disablewal`)을 더했다.
- 조건: 매핑 단위 4/8/16/32 KiB × RocksDB `block_size` 4/8/16/32 KiB × WAL off/on = 32 회.
- 회차 절차: 빈 장치 → ext4 포맷(`mkfs.ext4 -m 0`) → 마운트(`noatime`) → YCSB load 3,000,000 건(레코드 약 1.1 KB)
  → **적재 직후** YCSB run(workloada) 600 초 → 언마운트.
- workloada: 읽기 50 % / 업데이트 50 %, zipfian 분포, 레코드 = 필드 10 개 × 100 B. 클라이언트 스레드 1 개.
  YCSB 의 업데이트는 필드 하나를 바꾸므로 바인딩이 레코드를 읽고(Get) 다시 쓴다(Put).
- RocksDB 설정: 압축 없음, 블록 캐시 8 MiB, 데이터 읽기·flush·compaction 은 direct I/O,
  WAL 은 페이지 캐시를 거쳐 쓰고 쓰기마다 fsync 하지 않는다(`sync=false`, RocksDB 기본값). 나머지는 RocksDB 기본값(통계를 LOG 에 기록하는 주기 `stats_dump_period_sec` 만 600 → 60 초로 줄임).
  WAL 설정은 load 와 run 에 같이 적용했다.

### 파일

| 파일 | 내용 |
|---|---|
| **`rocksdb_ycsba_table.csv/.json`** | **요청하신 값만 모은 표**(32 줄): 매핑 단위, block_size, WAL, TPS, READ·UPDATE p99·평균 지연, READ·UPDATE 초당 처리 수. 반올림 값 |
| `rocksdb_ycsba_results.csv/.json` | 32 회 전체 표(반올림 없음, 열 약 100 개). 한 줄 = 한 회차 |
| `rocksdb_pivot_tps_ops_s.csv/.json` | TPS 표. 행 = 매핑 단위, 열 = WAL × block_size |
| `rocksdb_pivot_read_p99_us.csv/.json` | READ p99 지연(µs) 표 |
| `rocksdb_pivot_update_p99_us.csv/.json` | UPDATE p99 지연(µs) 표 |
| `rocksdb_pivot_read_tps_ops_s.csv/.json`, `rocksdb_pivot_update_tps_ops_s.csv/.json` | READ·UPDATE 각각의 초당 처리 수(두 값의 합 = TPS) |
| `rocksdb_pivot_read_avg_us.csv/.json`, `rocksdb_pivot_update_avg_us.csv/.json` | 평균 지연(µs) 표 |
| `*_failed_runs.csv` | 실패한 회차 목록(있을 때만) |
| `raw/rocksdb/<회차>/` | 회차별 원자료: `result.json`(정리한 전체 값), `ycsb_run_summary.json`·`ycsb_load_summary.json`(YCSB 최종 출력 전부, JVM GC 통계 포함), `ycsb_run_status_1s.csv`·`ycsb_load_status_1s.csv`(run·load 단계 1 초마다 처리량·지연. 마지막 행(`final_partial=True`)은 종료 직전 몇 ms 구간이라 초당 평균에서 뺀다), `device_blkstat_1s.csv`(1 초마다 장치 I/O 카운터, /sys/block/nvme1n1/stat 17 개 필드), `device_blkstat_phases.csv`(단계 경계 before_mkfs·before_load·after_load·before_run·after_run·after_umount 의 시각(epoch 초)과 같은 카운터), `meta.json`(설정·버전, 회차 시작·끝 시각 `start`·`end`(UTC), load·run 소요 시간 `load_wall_s`·`run_wall_s`) |

### 주요 열 (`rocksdb_ycsba_results`)

| 열 | 뜻 |
|---|---|
| `map_unit_KiB`, `block_size_KiB`, `wal` | 조건 (WAL off = `disableWAL=true`) |
| `tps_ops_s` | run 600 초 동안의 처리량 = 완료한 연산 수 ÷ 실행 시간 (YCSB `[OVERALL] Throughput`) |
| `read_tps_ops_s`, `update_tps_ops_s` | 연산별 처리량 = 그 연산 수 ÷ 같은 실행 시간 (합 = `tps_ops_s`) |
| `read_p99_us`, `update_p99_us` | 연산별 99 번째 백분위 지연(µs, YCSB hdrhistogram) |
| `read_avg_us`, `update_avg_us`, `*_p50_us` … `*_p99.99_us`, `*_max_us` | 연산별 평균·백분위·최대 지연(µs) |
| `read_ops`, `update_ops` | 연산 수. `*_not_ok` = 실패·없음 응답 수(모두 0 이어야 정상) |
| `tps_first60s`, `tps_last60s`, `tps_60s_windows_cv_pct` | run 처음·마지막 60 초 평균 처리량, 60 초 구간 처리량의 변동계수(%) |
| `load_wall_s`, `load_tps_ops_s` | 적재 시간과 적재 처리량 |
| `db_bytes_after_load`, `db_bytes_after_run`, `wal_file_bytes_after_run` | DB 디렉터리 크기, 남아 있는 WAL 파일 크기 |
| `run_dev_read_MiB_s`, `run_dev_write_MiB_s`, `run_dev_*_avg_req_KiB` | run 동안 장치가 받은 읽기·쓰기 대역폭과 평균 요청 크기 |
| `rocksdb_run_flush_write_bytes`, `rocksdb_run_compaction_write_bytes`, `rocksdb_run_compaction_read_bytes` | run 동안 RocksDB 가 flush·compaction 으로 쓰고 읽은 양(LOG 의 이벤트 기록 합). `rocksdb_load_*` 는 적재 단계 |
| `rocksdb_run_stall_msgs` | run 동안 RocksDB 가 쓰기를 늦춘(write stall) 기록 수 |
| `run_cpu0_2_busy_pct`, `run_cpu_psi_some_pct` | run 동안 CPU 0–2(YCSB·RocksDB 용) 사용률과 CPU 대기 비율(PSI). 다른 작업의 간섭 확인용 |
| `ftl_gc_cnt`, `ftl_waf_session` | NVMeVirt GC 횟수와 쓰기 증폭(NAND 쓰기 ÷ 호스트 쓰기). **mkfs + load + run 전체 합**이다(GC 통계는 모듈을 내릴 때 한 번 나온다) |
| `first_gc_phase`, `first_gc_s_after_phase_start` | 첫 GC 가 일어난 단계(load / run)와 그 단계 시작부터의 시간 |

## 3. fio 재측정 (`fio_*`)

커널이 6.8.0-142 → 6.8.0-147 로 바뀌어 NVMeVirt fio 실험을 다시 측정했다.
fio: libaio, O_DIRECT, iodepth 32, **120 초**, 회차마다 빈 장치, 페이지 캐시 drop 없음.

| 파일 | 내용 |
|---|---|
| `fio_randwrite.csv/.json` | 랜덤 쓰기 매핑 4/8/16/32 KiB × bs 4/8/16/32/64 KiB = 20 회 (wbuffix) |
| `fio_seqwrite.csv/.json` | 순차 쓰기 매핑 4/8/16/32 KiB × bs 4/16/32 KiB × 모델 wbuffix/merge = 24 회. 블록 계층 병합 끔(nomerges=2) |
| `raw/fio_*/<모델>/<회차>/` | `fio.json`(fio 출력 원본), `fio_bw/iops/clat/lat_500ms.csv`(0.5 초 평균 시계열: `time_ms`, `value`(bw KiB/s · iops 회/s · clat·lat ns), `direction`(1 = 쓰기). `block_size_bytes`·`offset` 은 평균 로그라 항상 0), `meta.json` |

주요 열: `bw_MiBps`(120 초 평균 대역폭), `iops`, `clat_mean_us`·`clat_p99_us`(완료 지연),
`bw_pre_gc_MiBps`·`bw_post_gc_MiBps`(첫 GC 전·후 평균), `gc_onset_s`(첫 GC 시각), `waf_total`(NAND 쓰기 ÷ 호스트 쓰기).

## 4. 읽을 때 주의할 점

- 조건마다 1 회 측정이라 반복 간 편차는 이 자료에 없다. 이전 fio 실험(커널 142, 3 회 반복)에서 반복 간 대역폭 변동계수는 최대 0.4 %(조건별 0.001–0.40 %, 중앙값 0.04 %)였다. RocksDB 는 반복 측정이 없어 회차 간 잡음의 크기를 모른다.
- NVMeVirt 는 TRIM 을 지원하지 않는다. 파일을 지워도 장치는 그 블록을 유효 데이터로 보고 GC 한다.
- NVMeVirt 는 매핑 단위보다 작은 쓰기의 read-modify-write 읽기를 모델링하지 않는다.
- fio 결과는 이전(커널 142) 결과와 실행 시간이 다르다(60 초 → 120 초). 120 초 평균에는 GC 이후 구간이 더 많이 들어간다.
