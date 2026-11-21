#!/usr/bin/env python3
"""Rescale scanned pages to chosen scanning resolutions (DPI): one test set per resolution.

A scan's physical size is usually unknown (archive.org and Wikimedia record no trustworthy
resolution), so the resolution is set from the text itself: the body-text line height is measured
with Tesseract, converted to a font size, and each page is scaled so its text is as large as
--font-pt print scanned at each --dpi. What a model sees is the text's size in pixels, so pages
with larger type are scaled down further. The PNG records that resolution, so Tesseract reads it.

    python3 tools/make_dpi_set.py scans/wikisource --out res --dpi 72 100 150 200 300

writes res/dpi-072/, res/dpi-100/ ... (with one --dpi, the pages go straight into --out).

Pages are only ever made smaller, as a scanner with fewer dots would see them: each new pixel is the
average of the source pixels it covers (area averaging, --filter box). A page whose source text is
too small for a resolution is left out of that resolution instead of being enlarged (--allow-upsample
enlarges it and marks it "upsampled"); --common keeps only the pages that reach every resolution, so
every level has the same pages. Pages where fewer than 5 body-text lines are found are skipped.

Tesseract's text-line box is 1.14 times the font size on average for Tamil (measured on 8
fonts, from 0.92 to 1.35), so the resolution of a single page is accurate to about +-20%.
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
    ap.add_argument("--dpi", type=int, nargs="+", required=True, help="target scanning resolution(s)")
    ap.add_argument("--font-pt", type=float, default=12, help="assumed body-text size (books ~12, newspapers ~9)")
    ap.add_argument("--tessdata", type=Path, default=TESSDATA, help="folder with tam.traineddata for measuring lines")
    ap.add_argument("--filter", choices=["box", "lanczos"], default="box",
                    help="box: area averaging, as a scanner's sensor does (default); lanczos: sharper")
    ap.add_argument("--allow-upsample", action="store_true", help="enlarge pages whose text is too small for a level")
    ap.add_argument("--common", action="store_true", help="keep only pages that reach every --dpi without enlarging")
    args = ap.parse_args()
    resample = Image.BOX if args.filter == "box" else Image.LANCZOS
    outs = {d: (args.out if len(args.dpi) == 1 else args.out / f"dpi-{d:03d}") for d in args.dpi}
    for o in outs.values():
        o.mkdir(parents=True, exist_ok=True)
    info = {}
    if (args.src / "pages.json").exists():
        info = {p["id"]: p for p in json.loads((args.src / "pages.json").read_text(encoding="utf-8"))}
    done = {d: [] for d in args.dpi}
    measured = []
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
        measured.append({"id": stem, "source_line_px": round(line_px, 1), "lines_measured": n,
                         "source_dpi_estimate": round(src_dpi)})
        if args.common and not args.allow_upsample and max(args.dpi) / src_dpi > 1.02:
            print(f"  {stem}: text line {line_px:.0f}px, about {src_dpi:.0f} DPI at {args.font_pt:g} pt: "
                  f"too small for {max(args.dpi)} DPI, left out", flush=True)
            continue
        im = Image.open(img).convert("L")
        kept = []
        for d in args.dpi:
            scale = d / src_dpi
            upsampled = scale > 1.02
            if upsampled and not args.allow_upsample:
                continue
            size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
            im.resize(size, resample).save(outs[d] / f"{stem}.png", dpi=(d, d))
            shutil.copy2(gt, outs[d] / gt.name)
            done[d].append({**info.get(stem, {"id": stem}), **measured[-1], "scale": round(scale, 3), "size": list(size),
                            "dpi": d, "font_pt_assumed": args.font_pt, "filter": args.filter, "upsampled": upsampled})
            kept.append(f"{d}" + ("(UP)" if upsampled else ""))
        print(f"  {stem}: text line {line_px:.0f}px -> about {src_dpi:.0f} DPI at {args.font_pt:g} pt; "
              f"made at {', '.join(kept) or 'no level'}", flush=True)
    for d, o in outs.items():
        (o / "pages.json").write_text(json.dumps(done[d], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{len(done[d])} pages at {d} DPI in {o}" + (f"; {sum(p['upsampled'] for p in done[d])} enlarged"
                                                         if args.allow_upsample else ""))
    if len(args.dpi) > 1:
        (args.out / "measured.json").write_text(json.dumps(measured, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
