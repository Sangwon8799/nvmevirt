#!/usr/bin/env python3
"""Build a combined view of run directories from several data sets (relative symlinks, no copies).

usage: python3 link_runs.py results/<VIEW> <run-dir parent> [<run-dir parent> ...] [--variant NAME]

Every <parent>/map<M>_bs<B>_r<R>/ that has a DONE marker is linked as results/<VIEW>/<NAME>/map<M>_bs<B>_r<R>
(NAME defaults to wbuffix). analyze.py, plot.py and make_md_results.py then treat the view like any data set.
The same run name must not come from two parents; nothing is linked when that happens. SOURCES.txt in the view
lists every link that exists under the view (all variants), so it stays complete when the tool is called again.
"""
import os
import re
import sys
from pathlib import Path

RUN_RE = re.compile(r"^map\d+k_bs\d+k_r\d+$")

args = sys.argv[1:]
name = "wbuffix"
if "--variant" in args:
    i = args.index("--variant")
    name = args[i + 1]
    del args[i:i + 2]
if len(args) < 2:
    sys.exit(__doc__)
view = Path(args[0]).resolve()
dst = view / name

# 1. collect and check everything before touching the view
seen = {}
for parent in map(lambda a: Path(a).resolve(), args[1:]):
    if not parent.is_dir():
        sys.exit(f"{parent} is not a directory")
    for run in sorted(parent.iterdir()):
        if not RUN_RE.match(run.name) or not (run / "DONE").exists():
            continue
        if run.name in seen and seen[run.name] != run:
            sys.exit(f"{run.name} comes from both {seen[run.name]} and {run} — nothing linked")
        seen[run.name] = run
if not seen:
    sys.exit("no finished runs (map*_bs*_r* with DONE) under the given directories")
for run_name, run in seen.items():
    link, rel = dst / run_name, os.path.relpath(run, dst)
    if link.is_symlink():
        if os.readlink(link) != rel:
            sys.exit(f"{link} exists and points elsewhere ({os.readlink(link)}) — nothing linked")
    elif link.exists():
        sys.exit(f"{link} exists and is not a symlink — nothing linked")

# 2. link
dst.mkdir(parents=True, exist_ok=True)
for run_name, run in seen.items():
    link = dst / run_name
    if not link.is_symlink():
        link.symlink_to(os.path.relpath(run, dst), target_is_directory=True)

# 3. SOURCES.txt from what is really there
lines = []
for link in sorted(p for p in view.glob("*/map*_bs*_r*") if p.is_symlink()):
    target = (link.parent / os.readlink(link)).resolve()
    note = "" if (target / "DONE").exists() else "   (WARNING: target has no DONE marker)"
    lines.append(f"{link.parent.name}/{link.name} -> {os.path.relpath(target, view)}{note}")
(view / "SOURCES.txt").write_text("# combined view made by exp/link_runs.py (relative symlinks)\n" + "\n".join(lines) + "\n")
print(f"{view}: {len(seen)} runs linked into {name}/")
