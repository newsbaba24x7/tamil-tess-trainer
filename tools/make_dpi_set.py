#!/usr/bin/env python3
"""Rescale scanned pages to a chosen scanning resolution (DPI), for test sets such as
"old books at 72 DPI" or "contemporary books at 300 DPI".

A scan's physical size is usually unknown, so the resolution is set from the text itself:
the body-text line height is measured with Tesseract, converted to a font size, and each page
is scaled so its text is as large as --font-pt print scanned at --dpi. The PNG records that
resolution, so Tesseract reads it too.

    python3 tools/make_dpi_set.py source/old-books --out old-books-72dpi --dpi 72 --font-pt 12

Tesseract's text-line box is 1.14 times the font size on average for Tamil (measured on 8
fonts, from 0.92 to 1.35), so the resolution of a single page is accurate to about +-20%.
Pages whose source scan is too small for the target are enlarged and marked "upsampled".
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

LINE_PER_EM = 1.14
TESSDATA = Path(os.environ.get("TAMTRAIN_CACHE", Path.home() / ".cache" / "tamtrain")) / "tessdata_best"


def body_line_height(img: Path, tessdata: Path) -> tuple[float, int]:
    """Median height (px) of body-text lines, and how many lines it is based on."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["tesseract", str(img), f"{tmp}/out", "--psm", "3", "-l", "tam", "--tessdata-dir", str(tessdata),
                        "-c", "tessedit_create_tsv=1"], capture_output=True, env={**os.environ, "OMP_THREAD_LIMIT": "1"})
        rows = [r.split("\t") for r in Path(f"{tmp}/out.tsv").read_text(encoding="utf-8", errors="replace").splitlines()[1:]]
    lines = [(int(r[8]), int(r[9])) for r in rows if r and r[0] == "4"]
    if not lines:
        return 0.0, 0
    widest = max(w for w, _ in lines)
    body = [h for w, h in lines if w >= 0.3 * widest]          # skip page numbers, short headers
    med = statistics.median(body)
    body = [h for h in body if 0.6 * med <= h <= 1.6 * med]     # skip merged lines and specks
    return (statistics.median(body), len(body)) if body else (0.0, 0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help="folder of page images + .gt.txt (+ pages.json)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dpi", type=int, required=True, help="target scanning resolution")
    ap.add_argument("--font-pt", type=float, default=12, help="assumed body-text size (books ~12, newspapers ~9)")
    ap.add_argument("--tessdata", type=Path, default=TESSDATA, help="folder with tam.traineddata for measuring lines")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    info = {}
    if (args.src / "pages.json").exists():
        info = {p["id"]: p for p in json.loads((args.src / "pages.json").read_text(encoding="utf-8"))}
    done, up = [], 0
    for gt in sorted(args.src.glob("*.gt.txt")):
        stem = gt.name[: -len(".gt.txt")]
        img = next((gt.with_name(stem + e) for e in (".jpg", ".png", ".tif") if gt.with_name(stem + e).exists()), None)
        if not img:
            continue
        line_px, n = body_line_height(img, args.tessdata)
        if n < 5:      # a picture page or a page with a few lines can't be measured reliably
            print(f"  {stem}: only {n} text lines found, skipped")
            continue
        src_dpi = line_px / LINE_PER_EM * 72 / args.font_pt
        scale = args.dpi / src_dpi
        im = Image.open(img).convert("L")
        size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
        im.resize(size, Image.LANCZOS).save(args.out / f"{stem}.png", dpi=(args.dpi, args.dpi))
        shutil.copy2(gt, args.out / gt.name)
        upsampled = scale > 1.02
        up += upsampled
        done.append({**info.get(stem, {"id": stem}), "source_line_px": round(line_px, 1), "lines_measured": n,
                     "source_dpi_estimate": round(src_dpi), "scale": round(scale, 3), "size": list(size),
                     "dpi": args.dpi, "font_pt_assumed": args.font_pt, "upsampled": upsampled})
        print(f"  {stem}: text line {line_px:.0f}px -> about {src_dpi:.0f} DPI at {args.font_pt:g} pt; "
              f"scaled x{scale:.2f} to {size[0]}x{size[1]}" + (" (UPSAMPLED)" if upsampled else ""), flush=True)
    (args.out / "pages.json").write_text(json.dumps(done, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(done)} pages at {args.dpi} DPI in {args.out}" + (f"; {up} had to be enlarged" if up else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
