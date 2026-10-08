#!/usr/bin/env python3
"""Build a combined view of run directories from several data sets (relative symlinks, no copies).

usage: python3 link_runs.py results/<VIEW> <run-dir parent> [<run-dir parent> ...] [--variant NAME]

Every <parent>/map<M>_bs<B>_r<R>/ that has a DONE marker is linked as results/<VIEW>/<NAME>/map<M>_bs<B>_r<R>
(NAME defaults to wbuffix). analyze.py, plot.py and make_md_results.py then treat the view like any data set.
The same run name must not come from two parents. SOURCES.txt in the view lists where every run came from.
"""
import os
import re
import sys
from pathlib import Path

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
dst.mkdir(parents=True, exist_ok=True)
seen, lines = {}, []
for parent in map(lambda a: Path(a).resolve(), args[1:]):
    for run in sorted(parent.iterdir()):
        if not re.match(r"^map\d+k_bs\d+k_r\d+$", run.name) or not (run / "DONE").exists():
            continue
        if run.name in seen and seen[run.name] != run:
            sys.exit(f"{run.name} comes from both {seen[run.name]} and {run}")
        seen[run.name] = run
        link = dst / run.name
        rel = os.path.relpath(run, dst)
        if link.is_symlink() or link.exists():
            if os.readlink(link) == rel:
                continue
            sys.exit(f"{link} exists and points elsewhere")
        link.symlink_to(rel, target_is_directory=True)
for run_name, run in sorted(seen.items()):
    lines.append(f"{name}/{run_name} -> {os.path.relpath(run, view)}")
(view / "SOURCES.txt").write_text("# combined view made by exp/link_runs.py (relative symlinks)\n" + "\n".join(lines) + "\n")
print(f"{view}: {len(seen)} runs linked into {name}/")
