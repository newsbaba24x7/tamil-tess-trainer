#!/usr/bin/env python3
"""Cut proofread scanned pages into line images with their text, for training on real scans.

For every page (image + .gt.txt with the proofread page text) Tesseract finds the text lines
and reads them roughly. Its words are aligned to the proofread words, which tells which
proofread words belong to which line. A line is kept only if its first and last words agree
with the proofread text (so the line boundaries are right) and the rough reading is not too
far from it; the line image is then saved with the *proofread* text as ground truth.

    python3 tools/page_lines.py scans/books --out lines/books --model-dir work-v2-research/output/tessdata_best \\
        --lang tam_v2_research

Output: <out>/<page>_<n>.png + .gt.txt, and lines.json (page, box, match quality).
Lines from one page never go to both training and testing: split by book, not by line.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tamtrain.scans import levenshtein, prepare  # noqa: E402

TESSDATA = Path(os.environ.get("TAMTRAIN_CACHE", Path.home() / ".cache" / "tamtrain")) / "tessdata_best"


def ocr_lines(img: Path, model_dir: Path, lang: str) -> list[dict]:
    """Tesseract's text lines: box and words, in reading order."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["tesseract", str(img), f"{tmp}/out", "--psm", "3", "-l", lang, "--tessdata-dir",
                        str(model_dir), "-c", "tessedit_create_tsv=1"], capture_output=True,
                       env={**os.environ, "OMP_THREAD_LIMIT": "1"})
        tsv = Path(f"{tmp}/out.tsv")
        rows = tsv.read_text(encoding="utf-8", errors="replace").splitlines()[1:] if tsv.exists() else []
    lines: dict[tuple, dict] = {}
    for r in rows:
        c = r.split("\t")
        if len(c) < 12:
            continue
        key = (int(c[1]), int(c[2]), int(c[3]), int(c[4]))
        if c[0] == "4":
            lines[key] = {"box": [int(c[6]), int(c[7]), int(c[8]), int(c[9])], "words": []}
        elif c[0] == "5" and key in lines and c[11].strip():
            lines[key]["words"].append(c[11].strip())
    return [ln for ln in lines.values() if ln["words"]]


def close(a: str, b: str, tol: float = 0.2) -> bool:
    return levenshtein(a, b) <= max(1, tol * max(len(a), len(b)))


def assign(gt_words: list[str], ocr_words: list[str], ocr_line: list[int]) -> list[int]:
    """Line index for every proofread word, from a word alignment with the OCR words."""
    where = [-1] * len(gt_words)
    sm = difflib.SequenceMatcher(None, gt_words, ocr_words, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("equal", "replace") and j2 > j1:
            for i in range(i1, i2):
                j = j1 + (i - i1) * (j2 - j1) // max(i2 - i1, 1)
                where[i] = ocr_line[min(j, j2 - 1)]
    last = -1
    for i, w in enumerate(where):          # proofread words OCR missed: give them to the line before
        if w < 0:
            where[i] = last
        else:
            last = w
    return where


def crop_line(page: Image.Image, box: list[int]) -> Image.Image:
    """The line image for a Tesseract line box (x, y, w, h)."""
    x, y, w, h = box
    # pad sideways only: Tesseract's box already covers ascenders and descenders, and vertical
    # padding pulls in parts of the neighbouring lines
    pad = max(4, h // 6)
    return page.crop((max(0, x - pad), max(0, y - 2), min(page.width, x + w + pad), min(page.height, y + h + 2)))


def cut_page(img: Path, gt: Path, out: Path, model_dir: Path, lang: str, max_cer: float) -> list[dict]:
    truth = prepare(gt.read_text(encoding="utf-8"))
    gt_words = truth.split()
    lines = ocr_lines(img, model_dir, lang)
    ocr_words, ocr_line = [], []
    for k, ln in enumerate(lines):
        for w in prepare(" ".join(ln["words"])).split():
            ocr_words.append(w)
            ocr_line.append(k)
    if not gt_words or not ocr_words:
        return []
    where = assign(gt_words, ocr_words, ocr_line)
    per_line: dict[int, list[str]] = defaultdict(list)
    for w, k in zip(gt_words, where):
        if k >= 0:
            per_line[k].append(w)
    page = Image.open(img).convert("L")
    heights = sorted(ln["box"][3] for ln in lines)
    typical_h = heights[len(heights) // 2]
    kept = []
    for k, ln in enumerate(lines):
        gtw = per_line.get(k, [])
        ocr = prepare(" ".join(ln["words"]))
        ow = ocr.split()
        if not gtw or len(" ".join(gtw)) < 4 or not ow:
            continue
        text = " ".join(gtw)
        cer = levenshtein(text, ocr) / len(text)
        # line boundaries must agree: first and last words close to the proofread ones
        if cer > max_cer or not close(gtw[0], ow[0]) or not close(gtw[-1], ow[-1]):
            continue
        x, y, w, h = ln["box"]
        if h < 10 or w < 2 * h or h > 1.6 * typical_h:     # too small, not a line, or two merged lines
            continue
        name = f"{img.parent.name}_{img.stem}_{k:03d}"     # book + page: page numbers repeat across books
        crop_line(page, ln["box"]).save(out / f"{name}.png")
        (out / f"{name}.gt.txt").write_text(text + "\n", encoding="utf-8")
        kept.append({"id": name, "page": f"{img.parent.name}/{img.stem}", "box": ln["box"], "ocr_cer": round(cer, 3)})
    return kept


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", type=Path, nargs="+", help="folders of page images + .gt.txt")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model-dir", type=Path, default=TESSDATA, help="tessdata folder of the model used to find lines")
    ap.add_argument("--lang", default="tam")
    ap.add_argument("--max-cer", type=float, default=0.35,
                    help="drop lines whose rough reading differs more than this from the proofread text")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    pairs = []
    for d in args.pages:
        for gt in sorted(d.glob("*.gt.txt")):
            stem = gt.name[: -len(".gt.txt")]
            img = next((gt.with_name(stem + e) for e in (".png", ".jpg", ".tif") if gt.with_name(stem + e).exists()), None)
            if img:
                pairs.append((img, gt))
    rows = []
    with ThreadPoolExecutor(args.jobs) as ex:
        for i, kept in enumerate(ex.map(lambda p: cut_page(p[0], p[1], args.out, args.model_dir, args.lang,
                                                           args.max_cer), pairs), 1):
            rows += kept
            if i % 25 == 0:
                print(f"  {i}/{len(pairs)} pages, {len(rows)} lines kept", flush=True)
    (args.out / "lines.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"{len(rows)} lines from {len({r['page'] for r in rows})} of {len(pairs)} pages in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
