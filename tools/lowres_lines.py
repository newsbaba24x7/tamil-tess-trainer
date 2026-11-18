#!/usr/bin/env python3
"""Low-resolution copies of line images, as if the page had been scanned at 72-100 DPI.

Real training lines are cut from high-resolution scans (text lines 40-80 px tall). A model trained
mostly on them reads low-resolution scans worse. This tool shrinks a random sample of lines so
that the text line is --min-height to --max-height px tall (12-pt print gives about 14 px at
72 DPI and 18 px at 96 DPI), with Lanczos resampling, the same way tools/make_dpi_set.py makes the
low-resolution test sets. Tesseract enlarges such lines itself before reading them, as it does
with low-resolution pages.

    python3 tools/lowres_lines.py books-lines/train books-lines-more/train --out lowres/lines \\
        --sample 25000 --seed 7

Writes <out>/<stem>.png and .gt.txt, and <out>/lowres.json (source line, height, scale).
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

from PIL import Image

PAD = 4          # tools/page_lines.py crops each line with 2 px above and below the text box


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", type=Path, nargs="+", help="folders of line images with .gt.txt")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sample", type=int, help="this many random lines (default: all)")
    ap.add_argument("--exclude", type=Path, help="text file of line image paths to leave out")
    ap.add_argument("--min-height", type=float, default=12, help="smallest text-line height, px")
    ap.add_argument("--max-height", type=float, default=20, help="largest text-line height, px")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    skip = set(args.exclude.read_text(encoding="utf-8").split()) if args.exclude else set()
    lines = sorted(p for d in args.dirs for p in d.rglob("*.png")
                   if p.with_suffix("").with_suffix(".gt.txt").exists() or Path(str(p)[:-4] + ".gt.txt").exists())
    lines = [p for p in lines if str(p) not in skip]
    rng = random.Random(args.seed)
    if args.sample and args.sample < len(lines):
        lines = rng.sample(lines, args.sample)
    args.out.mkdir(parents=True, exist_ok=True)
    made = []
    for n, src in enumerate(lines, 1):
        with Image.open(src) as im:
            im = im.convert("L")
            target = rng.uniform(args.min_height, args.max_height)
            scale = min(1.0, target / max(im.height - PAD, 1))
            size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
            stem = f"lr_{src.stem}"
            im.resize(size, Image.LANCZOS).save(args.out / f"{stem}.png")
        shutil.copyfile(str(src)[:-4] + ".gt.txt", args.out / f"{stem}.gt.txt")
        made.append({"line": stem, "source": str(src), "text_height": round(target, 1), "scale": round(scale, 3)})
        if n % 5000 == 0:
            print(f"  {n}/{len(lines)}", flush=True)
    (args.out / "lowres.json").write_text(json.dumps(made, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"{len(made)} low-resolution lines in {args.out} (text {args.min_height:g}-{args.max_height:g} px tall)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
