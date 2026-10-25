#!/usr/bin/env python3
"""Parse one RocksDB/YCSB-A run directory of run_rocksdb_ycsb.sh into result.json and check it.

usage: python3 ycsb_parse.py <run dir> [--min-run-s N]

reads   meta.txt, load.txt, run.txt, run_status.txt, blkstat_phases.txt, kernel.log, dmesg_unload.txt, rocksdb/LOG
writes  <run dir>/result.json, <run dir>/run_status.csv (one row per YCSB status line)
checks  (exit 1 and the reason on stderr when one fails)
        - load inserted every record (INSERT Return=OK == recordcount)
        - no READ/UPDATE returned anything but OK (NOT_FOUND would mean records were lost)
        - the run phase lasted at least --min-run-s seconds
The last stdout line is a one-line summary (TPS, p99 per operation).
"""
import csv
import json
import re
import sys
from pathlib import Path

PCT_RE = re.compile(r"^(\d+(?:\.\d+)?)(?:th)?PercentileLatency\(us\)$")
SEC_RE = re.compile(r"^\[([^\]]+)\], ([^,]+), (.+)$")   # any section, incl. JVM GC lines like [TOTAL_GC_TIME_%_G1_Old_Generation]
STATUS_RE = re.compile(r"^\S+ \S+ (\d+) sec: (\d+) operations; ([\d.]+) current ops/sec;(.*)$")
STATUS_OP_RE = re.compile(r"\[([A-Z_-]+): ([^\]]*)\]")
MARK_RE = re.compile(r"^\[\s*([\d.]+)\] KSC2026-MARK (\S+) (\S+)")
TS_RE = re.compile(r"^\[\s*([\d.]+)\]")
BLK_FIELDS = ["rd_ios", "rd_merges", "rd_sectors", "rd_ticks", "wr_ios", "wr_merges", "wr_sectors", "wr_ticks",
              "in_flight", "io_ticks", "time_in_queue", "dc_ios", "dc_merges", "dc_sectors", "dc_ticks", "fl_ios", "fl_ticks"]


def num(v):
    v = v.strip()
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def parse_summary(path):
    """YCSB end-of-phase summary: {'OVERALL': {...}, 'READ': {'ops': .., 'avg_us': .., 'p99_us': .., 'return': {...}}}"""
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(errors="replace").splitlines():
        m = SEC_RE.match(line.strip())
        if not m:
            continue
        sec, key, val = m.group(1), m.group(2).strip(), num(m.group(3))
        d = out.setdefault(sec, {})
        if key.startswith("Return="):
            d.setdefault("return", {})[key[len("Return="):]] = val
            continue
        p = PCT_RE.match(key)
        if p:
            d[f"p{p.group(1)}_us"] = val
            continue
        d[{"Operations": "ops", "AverageLatency(us)": "avg_us", "MinLatency(us)": "min_us", "MaxLatency(us)": "max_us",
           "RunTime(ms)": "runtime_ms", "Throughput(ops/sec)": "throughput_ops_s"}.get(key, key)] = val
    return out


def parse_status(path):
    """YCSB -s status lines (one per status.interval): elapsed s, total ops, current ops/s, per-op Avg/99 (us).
    YCSB's StatusThread prints one more line after its loop ends, over the few ms up to client cleanup; that last
    row is flagged final_partial=True and must be left out of any per-second average (it is kept as raw data)."""
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(errors="replace").splitlines():
        m = STATUS_RE.match(line.strip())
        if not m:
            continue
        r = {"t_s": int(m.group(1)), "ops_total": int(m.group(2)), "ops_per_s": float(m.group(3))}
        for op, body in STATUS_OP_RE.findall(m.group(4)):
            kv = dict(x.strip().split("=", 1) for x in body.split(",") if "=" in x)
            for k in ("Count", "Avg", "99", "Max"):
                if k in kv:
                    r[f"{op.lower()}_{k.lower()}"] = num(kv[k])
        rows.append(r)
    if rows:
        rows[-1]["final_partial"] = True
    return rows


def parse_meta(path):
    out = {}
    for line in path.read_text(errors="replace").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out.setdefault(k.strip(), v.strip())
    return out


def blk_phases(path):
    """Block-layer counters between the phase labels in blkstat_phases.txt (bytes and requests)."""
    snaps = {}
    if not path.exists():
        return {}
    for line in path.read_text().splitlines():
        f = line.split()
        if len(f) >= 2 + 7:
            snaps[f[0]] = (float(f[1]), [int(x) for x in f[2:]])
    out = {}
    for name, a, b in (("load", "before_load", "after_load"), ("run", "before_run", "after_run")):
        if a in snaps and b in snaps:
            (t0, s0), (t1, s1) = snaps[a], snaps[b]
            d = {k: s1[i] - s0[i] for i, k in enumerate(BLK_FIELDS[:min(len(s0), len(s1))])}
            r = {"seconds": round(t1 - t0, 3),
                 "read_bytes": d["rd_sectors"] * 512, "read_ios": d["rd_ios"],
                 "write_bytes": d["wr_sectors"] * 512, "write_ios": d["wr_ios"], "write_merges": d["wr_merges"]}
            r["read_avg_req_KiB"] = r["read_bytes"] / 1024 / r["read_ios"] if r["read_ios"] else None
            r["write_avg_req_KiB"] = r["write_bytes"] / 1024 / r["write_ios"] if r["write_ios"] else None
            r["read_MiB_s"] = r["read_bytes"] / 2**20 / r["seconds"] if r["seconds"] else None
            r["write_MiB_s"] = r["write_bytes"] / 2**20 / r["seconds"] if r["seconds"] else None
            if "fl_ios" in d:
                r["flush_ios"] = d["fl_ios"]
            out[name] = r
    if "before_load" in snaps and "after_run" in snaps:
        s0, s1 = snaps["before_load"][1], snaps["after_run"][1]
        out["load_and_run_write_bytes"] = (s1[6] - s0[6]) * 512
    if "before_mkfs" in snaps and "before_load" in snaps:
        out["mkfs_write_bytes"] = (snaps["before_load"][1][6] - snaps["before_mkfs"][1][6]) * 512
    if "before_mkfs" in snaps and "after_umount" in snaps:   # everything the host wrote since insmod (= the FTL counters)
        out["session_write_bytes"] = (snaps["after_umount"][1][6] - snaps["before_mkfs"][1][6]) * 512
    return out


def ftl_stats(rdir, map_bytes):
    """NVMeVirt GC statistics (GC_STATS=1): totals at rmmod (whole session: mkfs + load + run) and first GC time."""
    out = {}
    un = rdir / "dmesg_unload.txt"
    if un.exists():
        tot = {"host_pgs": 0, "gc_pgs": 0, "gc_cnt": 0}
        parts = 0
        for line in un.read_text(errors="replace").splitlines():
            m = re.search(r"KSC2026: stats part=\d+ host_pgs=(\d+) gc_pgs=(\d+) gc_cnt=(\d+)", line)
            if m:
                parts += 1
                for k, g in zip(("host_pgs", "gc_pgs", "gc_cnt"), m.groups()):
                    tot[k] += int(g)
        if parts:
            out.update(tot)
            out["partitions"] = parts
            out["nand_write_bytes"] = (tot["host_pgs"] + tot["gc_pgs"]) * map_bytes
            out["waf_gc"] = (tot["host_pgs"] + tot["gc_pgs"]) / tot["host_pgs"] if tot["host_pgs"] else None
    klog = rdir / "kernel.log"
    marks, first_gc = {}, None
    if klog.exists():
        for line in klog.read_text(errors="replace").splitlines():
            m = MARK_RE.match(line)
            if m:
                marks.setdefault(m.group(3), float(m.group(1)))
                continue
            if "KSC2026: first GC" in line and first_gc is None:
                t = TS_RE.match(line)
                if t:
                    first_gc = float(t.group(1))
    if first_gc is not None:
        for ph in ("run-start", "load-start", "mkfs"):
            if ph in marks and first_gc >= marks[ph]:
                out["first_gc_phase"] = ph.split("-")[0]
                out["first_gc_s_after_phase_start"] = round(first_gc - marks[ph], 3)
                break
    else:
        out["first_gc_phase"] = "none"
    for a, b, k in (("load-start", "load-end", "load_s_kernel"), ("run-start", "run-end", "run_s_kernel")):
        if a in marks and b in marks:
            out[k] = round(marks[b] - marks[a], 3)
    return out


def rocksdb_events(log):
    """Totals from the EVENT_LOG_v1 records of one RocksDB LOG file (one DB open: the run phase or the load phase).
    sst_write = all new SST files (flush + compaction outputs), split by the job that created them."""
    out = {"flush_jobs": 0, "compaction_jobs": 0, "flush_write_bytes": 0, "compaction_write_bytes": 0,
           "compaction_read_bytes": 0, "sst_write_bytes": 0, "stall_msgs": 0, "stop_msgs": 0}
    if not log.exists():
        return {}
    flush_jobs, comp_jobs, created = set(), set(), []
    for line in log.read_text(errors="replace").splitlines():
        if "Stalling writes" in line:
            out["stall_msgs"] += 1
        elif "Stopping writes" in line:
            out["stop_msgs"] += 1
        i = line.find("EVENT_LOG_v1 {")
        if i < 0:
            continue
        try:
            ev = json.loads(line[i + len("EVENT_LOG_v1 "):])
        except ValueError:
            continue
        e, job = ev.get("event"), ev.get("job")
        if e == "flush_started":
            flush_jobs.add(job)
        elif e == "compaction_started":
            comp_jobs.add(job)
            out["compaction_read_bytes"] += int(ev.get("input_data_size", 0))
        elif e == "table_file_creation":
            created.append((job, int(ev.get("file_size", 0))))
    for job, size in created:
        out["sst_write_bytes"] += size
        if job in flush_jobs:
            out["flush_write_bytes"] += size
        elif job in comp_jobs:
            out["compaction_write_bytes"] += size
    out["flush_jobs"], out["compaction_jobs"] = len(flush_jobs), len(comp_jobs)
    return out


def cpu_phases(path):
    """CPU 0-2 busy share and CPU pressure (PSI 'some') between before_run and after_run (cpu_phases.txt)."""
    if not path.exists():
        return {}
    snaps, cur = {}, None
    for line in path.read_text().splitlines():
        f = line.split()
        if line.startswith("== "):
            cur = f[1]
            snaps[cur] = {"t": float(f[2]), "busy": 0, "total": 0}
        elif cur and f and re.match(r"^cpu[0-2]$", f[0]):
            v = [int(x) for x in f[1:]]
            snaps[cur]["total"] += sum(v[:8])            # user nice system idle iowait irq softirq steal
            snaps[cur]["busy"] += sum(v[:8]) - v[3] - v[4]
        elif cur and f and f[0] == "some":
            m = re.search(r"total=(\d+)", line)
            if m:
                snaps[cur]["psi_some_us"] = int(m.group(1))
    out = {}
    for ph in ("load", "run"):
        a, b = snaps.get(f"before_{ph}"), snaps.get(f"after_{ph}")
        if a and b and b["total"] > a["total"]:
            out[f"{ph}_cpu0_2_busy_pct"] = 100 * (b["busy"] - a["busy"]) / (b["total"] - a["total"])
            if "psi_some_us" in a and "psi_some_us" in b and b["t"] > a["t"]:
                out[f"{ph}_cpu_psi_some_pct"] = 100 * (b["psi_some_us"] - a["psi_some_us"]) / 1e6 / (b["t"] - a["t"])
    return out


def rocksdb_log(rdir):
    """Last periodic stats dump in the run-phase LOG (stats_dump_period_sec=60): cumulative since the DB was opened."""
    log = rdir / "rocksdb" / "LOG"
    if not log.exists():
        return {}
    text = log.read_text(errors="replace")
    out = {}
    for key, pat in (("cumulative_writes", r"Cumulative writes: (.*)"), ("cumulative_wal", r"Cumulative WAL: (.*)"),
                     ("cumulative_compaction", r"Cumulative compaction: (.*)"), ("uptime", r"Uptime\(secs\): (.*)")):
        found = re.findall(pat, text)
        if found:
            out[key] = found[-1].strip()
    v = re.search(r"RocksDB version: (\S+)", text)
    if v:
        out["rocksdb_version"] = v.group(1)
    return out


def ops_block(sec):
    keep = {k: v for k, v in sec.items() if k != "return"}
    keep["return"] = sec.get("return", {})
    return keep


def parse_run(rdir):
    rdir = Path(rdir)
    meta = parse_meta(rdir / "meta.txt")
    map_s = meta.get("map_unit", "").split()[0]
    blk_s = meta.get("block_size", "").split()[0]
    wal_s = meta.get("wal", "").split()[0]
    map_b = int(re.search(r"\((\d+) B\)", meta["map_unit"]).group(1))
    blk_b = int(re.search(r"\((\d+) B\)", meta["block_size"]).group(1))
    records = int(re.search(r"recordcount=(\d+)", meta["workload"]).group(1))
    load, run = parse_summary(rdir / "load.txt"), parse_summary(rdir / "run.txt")
    status = parse_status(rdir / "run_status.txt")
    if status:
        with (rdir / "run_status.csv").open("w", newline="") as f:
            cols = []
            for r in status:
                cols += [k for k in r if k not in cols]
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(status)
    ov = run.get("OVERALL", {})
    res = {
        "run": rdir.name, "variant": meta.get("variant"), "map_unit": map_s, "map_unit_bytes": map_b,
        "block_size": blk_s, "block_size_bytes": blk_b, "wal": wal_s, "recordcount": records,
        "threads": int(re.search(r"threads=(\d+)", meta["workload"]).group(1)),
        "tps_ops_s": ov.get("throughput_ops_s"), "run_runtime_s": ov.get("runtime_ms", 0) / 1000 if ov else None,
        "read": ops_block(run.get("READ", {})), "update": ops_block(run.get("UPDATE", {})),
        "load": {"tps_ops_s": load.get("OVERALL", {}).get("throughput_ops_s"),
                 "runtime_s": load.get("OVERALL", {}).get("runtime_ms", 0) / 1000 if load.get("OVERALL") else None,
                 "wall_s": num(meta["load_wall_s"]) if "load_wall_s" in meta else None,
                 "insert": ops_block(load.get("INSERT", {}))},
        "other_sections": sorted(set(run) - {"OVERALL", "READ", "UPDATE"}),
        "block_layer": blk_phases(rdir / "blkstat_phases.txt"),
        "ftl": ftl_stats(rdir, map_b),
        "rocksdb_log_last_dump": rocksdb_log(rdir),
        "rocksdb_run_events": rocksdb_events(rdir / "rocksdb" / "LOG"),
        "rocksdb_load_events": rocksdb_events(max((rdir / "rocksdb").glob("LOG.old.*"), default=rdir / "rocksdb" / "none")),
        "cpu": cpu_phases(rdir / "cpu_phases.txt"),
        "db_bytes_after_load": int(meta["db_after_load"].split()[0]) if "db_after_load" in meta else None,
        "db_bytes_after_run": int(meta["db_after_run"].split()[0]) if "db_after_run" in meta else None,
        "fs_used_after_run": int(meta["df_after_run"].split()[0]) if "df_after_run" in meta else None,
        "status_lines": len(status),
        "chmodel_msgs": meta.get("chmodel_msgs"), "kernel_warn": meta.get("kernel_warn"),
        "start": meta.get("start"), "end": meta.get("end"),
    }
    wal_files = 0
    lf = rdir / "rocksdb" / "db_files_after_run.txt"
    if lf.exists():
        for line in lf.read_text().splitlines():
            f = line.split()
            if len(f) >= 7 and f[-1].endswith(".log"):
                wal_files += int(f[4])
        res["wal_file_bytes_after_run"] = wal_files
    for op in ("read", "update"):
        n, t = res[op].get("ops"), res["run_runtime_s"]
        res[op]["tps_ops_s"] = n / t if n is not None and t else None
    host = res["block_layer"].get("session_write_bytes")
    if host and res["ftl"].get("nand_write_bytes"):   # NAND bytes / host bytes for the whole session (mkfs + load + run)
        res["ftl"]["waf_session"] = res["ftl"]["nand_write_bytes"] / host
    return res


def check(res, min_run_s):
    errs = []
    ins = res["load"]["insert"].get("return", {})
    if ins.get("OK") != res["recordcount"]:
        errs.append(f"load INSERT OK={ins.get('OK')} != recordcount {res['recordcount']}")
    for op in ("read", "update"):
        rc = res[op].get("return", {})
        if not rc.get("OK"):
            errs.append(f"{op}: no successful operations")
        bad = {k: v for k, v in rc.items() if k != "OK" and v}
        if bad:
            errs.append(f"{op}: non-OK returns {bad}")
    if [s for s in res["other_sections"] if s.endswith("-FAILED")]:
        errs.append(f"failed-operation sections: {res['other_sections']}")
    if res["run_runtime_s"] is None or res["run_runtime_s"] < min_run_s:
        errs.append(f"run phase lasted {res['run_runtime_s']} s < {min_run_s} s")
    return errs


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    min_run = 0.0
    if "--min-run-s" in args:
        i = args.index("--min-run-s")
        min_run = float(args[i + 1])
        del args[i:i + 2]
    rdir = Path(args[0])
    res = parse_run(rdir)
    (rdir / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    errs = check(res, min_run)
    for e in errs:
        print("CHECK FAILED:", e, file=sys.stderr)
    r, u = res["read"], res["update"]
    print(f"TPS {res['tps_ops_s']:.1f} ops/s | READ avg {r.get('avg_us', float('nan')):.1f} p99 {r.get('p99_us')} us | "
          f"UPDATE avg {u.get('avg_us', float('nan')):.1f} p99 {u.get('p99_us')} us | load {res['load']['wall_s']} s"
          if res["tps_ops_s"] is not None else "no run summary")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
