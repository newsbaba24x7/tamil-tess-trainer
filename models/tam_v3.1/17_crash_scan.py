#!/usr/bin/env python3
"""Step 17 - List the lines on which the stock tesseract CLI crashes (SIGFPE).

Tesseract 5.5.0-5.5.3 can be killed by SIGFPE in single-row modes (--psm 7/8/9/10/13) when a
row holds two words the recogniser left empty: their certainties (-FLT_MAX each) overflow when
Textord::CleanupSingleRowResult adds them, and the CLI traps overflow (feenableexcept in main1()).
Upstream issue tesseract-ocr/tesseract#4627, fixed by #4630 in Tesseract 5.5.4. Library/API users
do not enable the trap and are not affected. Which lines trigger it depends on the image and model.

One tesseract process reads a whole shard (an image list, stdout unbuffered); after a crash the
shard restarts on the line after the one that crashed, and each crash is confirmed by re-running
that line alone.

  python3 -I 17_crash_scan.py TESSDATA_DIR PSM LIST OUT_TXT [JOBS]
OUT_TXT gets one line per crash: "CRASH <signal> <image path relative to LIST's folder>" (empty = no crash).
"""
import os, signal, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

tdir, psm, lst, out = sys.argv[1:5]
jobs = int(sys.argv[5]) if len(sys.argv) > 5 else os.cpu_count()
lines = [l.strip() for l in open(lst, encoding="utf-8") if l.strip()]
env = dict(os.environ, OMP_THREAD_LIMIT="1")
env.pop("LD_PRELOAD", None)          # always the stock CLI


def tess(paths):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(paths) + "\n"); name = f.name
    try:
        p = subprocess.run(["stdbuf", "-o0", "tesseract", name, "stdout", "--tessdata-dir", tdir, "-l", "tam",
                            "--psm", psm], capture_output=True, env=env)
    finally:
        os.unlink(name)
    return p.returncode, p.stdout


def scan(shard):
    # The text renderer writes the page separator \f BEFORE every page but the first, so after n finished
    # pages stdout holds n-1 separators: the crashing line is i + count + 1, or i itself if nothing was written.
    found, i = [], 0
    while i < len(shard):
        rc, out = tess(shard[i:])
        if rc == 0:
            break
        k = min(i + out.count(b"\f") + (1 if out else 0), len(shard) - 1)
        rc1, _ = tess([shard[k]])
        if rc1 == 0 and not out and k + 1 < len(shard):   # the first page may have produced no text at all
            k += 1; rc1, _ = tess([shard[k]])
        st = lambda r: signal.Signals(-r).name if r < 0 else str(r)
        rel = os.path.relpath(shard[k], os.path.dirname(os.path.abspath(lst)))   # no machine-specific paths
        found.append(f"CRASH {st(rc1)} {rel}" if rc1 != 0 else f"BATCH-ONLY {st(rc)} {rel}")
        i = k + 1
    return found


shards = [lines[k::jobs] for k in range(jobs)]
with ThreadPoolExecutor(jobs) as ex:
    res = sorted(x for r in ex.map(scan, shards) for x in r)
open(out, "w", encoding="utf-8").write("".join(x + "\n" for x in res))
print(f"{os.path.basename(os.path.normpath(tdir))} psm {psm}: {sum(x.startswith('CRASH') for x in res)} crash(es) "
      f"in {len(lines)} lines" + (f", {len(res) - sum(x.startswith('CRASH') for x in res)} batch-only" if len(res) else ""))
