"""Compare models on held-out line images: character/word error rates and top confusions."""

from __future__ import annotations

import math
import random
import subprocess
import tempfile
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from .train import load_manifest
from .util import SINGLE_THREAD_ENV, Progress, TamTrainError, log, save_json, step

INVISIBLE = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)


@dataclass
class ModelSpec:
    label: str
    tessdata_dir: Path
    lang: str


def align(a: str, b: str) -> tuple[int, list[tuple[str, str]]]:
    """Levenshtein distance between a (truth) and b (OCR) plus the list of edits."""
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        ai = a[i - 1]
        row, prev = d[i], d[i - 1]
        for j in range(1, m + 1):
            row[j] = min(prev[j] + 1, row[j - 1] + 1, prev[j - 1] + (ai != b[j - 1]))
    edits = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            if a[i - 1] != b[j - 1]:
                edits.append((a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            edits.append((a[i - 1], ""))
            i -= 1
        else:
            edits.append(("", b[j - 1]))
            j -= 1
    return d[n][m], edits


def word_errors(a: str, b: str) -> int:
    aw, bw = a.split(), b.split()
    prev = list(range(len(bw) + 1))
    for i in range(1, len(aw) + 1):
        cur = [i] + [0] * len(bw)
        for j in range(1, len(bw) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (aw[i - 1] != bw[j - 1]))
        prev = cur
    return prev[-1]


class TesseractCrash(TamTrainError):
    """tesseract exited with an error (or crashed) on a batch of images."""


def _ocr_once(images: list[Path], model: ModelSpec, psm: int) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        lst = Path(tmp) / "images.txt"
        lst.write_text("\n".join(str(p.resolve()) for p in images) + "\n", encoding="utf-8")
        out = Path(tmp) / "out"
        proc = subprocess.run(["tesseract", str(lst), str(out), "--tessdata-dir", str(model.tessdata_dir),
                               "-l", model.lang, "--psm", str(psm)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                              errors="replace", env=SINGLE_THREAD_ENV)
        if proc.returncode != 0:
            raise TesseractCrash(f"tesseract failed for model {model.label} (exit {proc.returncode}):\n"
                                 f"{proc.stdout[-800:]}")
        pages = (Path(str(out) + ".txt")).read_text(encoding="utf-8", errors="replace").split("\f")
    pages = pages[: len(images)]
    if len(pages) != len(images):
        raise TamTrainError(f"tesseract returned {len(pages)} pages for {len(images)} images")
    return [" ".join(unicodedata.normalize("NFC", p).split()) for p in pages]


def _ocr_split(images: list[Path], model: ModelSpec, psm: int) -> list[str | None]:
    try:
        return list(_ocr_once(images, model, psm))
    except TesseractCrash:
        if len(images) == 1:
            return [None]
        mid = len(images) // 2
        return _ocr_split(images[:mid], model, psm) + _ocr_split(images[mid:], model, psm)


def ocr_batch(images: list[Path], model: ModelSpec, psm: int) -> list[str | None]:
    """OCR many images with one tesseract call (one 'page' per image).

    Tesseract 5 crashes (floating point exception) on a few faint images in single-line
    mode. When a batch fails, it is split in halves until the images that crash are found;
    those get None. If every image fails, the error is real (missing model…) and is raised."""
    try:
        return list(_ocr_once(images, model, psm))
    except TesseractCrash as first:
        out = _ocr_split(images, model, psm) if len(images) > 1 else [None]
        if all(t is None for t in out):
            raise TamTrainError(str(first)) from None
        return out


def ocr_parallel(images: list[Path], model: ModelSpec, psm: int, jobs: int) -> list[str]:
    """OCR images in `jobs` single-threaded tesseract processes; results in input order."""
    chunks = [list(range(i, len(images), jobs)) for i in range(jobs)]
    chunks = [c for c in chunks if c]
    progress = Progress(len(chunks), model.label)
    texts: list[str | None] = [""] * len(images)

    def do(chunk):
        return chunk, ocr_batch([images[i] for i in chunk], model, psm)

    with ThreadPoolExecutor(jobs) as ex:
        for k, (chunk, outs) in enumerate(ex.map(do, chunks), 1):
            for i, t in zip(chunk, outs):
                texts[i] = t
            progress.update(k)
    return texts


def select_lines(work: Path, max_lines: int, seed: int) -> list[dict]:
    rows = [r for r in load_manifest(work) if r["split"] == "eval"]
    if not rows:
        raise TamTrainError("No evaluation lines in the manifest (render with --eval-ratio > 0).")
    by_font: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_font[r["font"]].append(r)
    per_font = max(1, math.ceil(max_lines / len(by_font)))
    rng = random.Random(seed)
    chosen = []
    for font in sorted(by_font):
        group = by_font[font]
        rng.shuffle(group)
        chosen += group[:per_font]
    return chosen


def evaluate(work: Path, models: list[ModelSpec], *, max_lines: int = 600, psm: int = 7, jobs: int = 4,
             seed: int = 42) -> dict:
    step("Evaluating on held-out lines")
    for m in models:
        if not (m.tessdata_dir / f"{m.lang}.traineddata").exists():
            raise TamTrainError(f"Model not found: {m.tessdata_dir / (m.lang + '.traineddata')}")
    rows = select_lines(work, max_lines, seed)
    images = [work / (r["base"] + ".png") for r in rows]
    truths = [unicodedata.normalize("NFC", (work / (r["base"] + ".gt.txt")).read_text(encoding="utf-8").strip())
              for r in rows]
    log(f"    {len(rows)} lines from {len({r['font'] for r in rows})} fonts")

    all_texts = {m.label: ocr_parallel(images, m, psm, jobs) for m in models}
    # Lines on which tesseract crashed for any model are left out for all models.
    crashed = sorted({i for texts in all_texts.values() for i, t in enumerate(texts) if t is None})
    if crashed:
        log(f"    {len(crashed)} line image(s) made tesseract crash; left out for every model")
    keep = [i for i in range(len(rows)) if i not in set(crashed)]
    results: dict = {"lines": len(keep), "psm": psm, "models": {},
                     "crashed": [rows[i]["base"] for i in crashed]}
    for model in models:
        texts = all_texts[model.label]
        tot = Counter()
        per_group: dict[str, Counter] = defaultdict(Counter)   # old vs modern letter shapes
        per_font: dict[str, Counter] = defaultdict(Counter)
        confusions = Counter()
        samples = []
        for r, gt, ocr in ((rows[i], truths[i], texts[i]) for i in keep):
            dist, edits = align(gt, ocr)
            clean = ocr.translate(INVISIBLE)
            dist_clean, edits_clean = align(gt, clean)
            werr = word_errors(gt, clean)
            for c in (tot, per_font[r["font"]], per_group["old" if r.get("old_letters") else "modern"]):
                c["chars"] += len(gt)
                c["errors"] += dist
                c["errors_clean"] += dist_clean
                c["words"] += len(gt.split())
                c["word_errors"] += werr
                c["lines"] += 1
            confusions.update(edits_clean)
            if dist_clean and len(samples) < 15:
                samples.append({"font": r["font"], "truth": gt, "ocr": ocr})
        rate = lambda e, n: round(100 * e / max(n, 1), 2)  # noqa: E731
        results["models"][model.label] = {
            "model": str(model.tessdata_dir / f"{model.lang}.traineddata"),
            "cer": rate(tot["errors_clean"], tot["chars"]),
            "cer_raw": rate(tot["errors"], tot["chars"]),
            "wer": rate(tot["word_errors"], tot["words"]),
            "letter_shapes": {g: {"lines": c["lines"], "cer": rate(c["errors_clean"], c["chars"]),
                                  "wer": rate(c["word_errors"], c["words"])} for g, c in sorted(per_group.items())},
            "per_font": {f: {"lines": c["lines"], "cer": rate(c["errors_clean"], c["chars"]),
                             "wer": rate(c["word_errors"], c["words"])} for f, c in sorted(per_font.items())},
            "top_confusions": [{"truth": a, "ocr": b, "count": n} for (a, b), n in confusions.most_common(15)],
            "error_samples": samples,
        }
    write_report(work, results)
    return results


def _show(ch: str) -> str:
    if ch == "":
        return "∅"
    if ch == " ":
        return "␠"
    if unicodedata.category(ch) in ("Mn", "Mc", "Cf"):
        return f"◌{ch} (U+{ord(ch):04X})" if unicodedata.category(ch) != "Cf" else f"U+{ord(ch):04X}"
    return ch


def write_report(work: Path, results: dict) -> None:
    out = work / "report"
    save_json(out / "report.json", results)
    labels = list(results["models"])
    md = ["# Evaluation report\n", f"{results['lines']} held-out line images, `--psm {results['psm']}`. "
          "CER = character error rate, WER = word error rate (lower is better).\n",
          "The stock `tam` model writes an invisible U+200C (zero-width non-joiner) after many pullis (்), "
          "learned from its training text. CER and WER ignore invisible characters so models are compared "
          "on visible text; 'raw CER' counts them.\n"
          + (f"{len(results['crashed'])} line image(s) made tesseract itself crash (a tesseract bug on some faint "
             "images) and are left out for every model.\n" if results.get("crashed") else ""),
          "| Model | CER | WER | raw CER |", "|---|---:|---:|---:|"]
    for lab in labels:
        m = results["models"][lab]
        md.append(f"| {lab} | {m['cer']}% | {m['wer']}% | {m['cer_raw']}% |")
    groups = results["models"][labels[0]].get("letter_shapes", {})
    if "old" in groups:
        md += ["\n## Pre-1978 letter shapes\n",
               "Lines drawn with the old shapes of ணா றா னா / ணை லை ளை னை (fonts that draw them by default, "
               "or with the OpenType feature turned on) and all other lines.\n",
               "| Model | Old shapes CER | Modern shapes CER |", "|---|---:|---:|"]
        for lab in labels:
            g = results["models"][lab]["letter_shapes"]
            md.append(f"| {lab} | {g['old']['cer']}% ({g['old']['lines']} lines) | {g.get('modern', {}).get('cer', 0)}% |")
    fonts = list(results["models"][labels[0]]["per_font"])
    md += ["\n## CER per font\n", "| Font | Lines | " + " | ".join(labels) + " |",
           "|---|---:|" + "---:|" * len(labels)]
    for f in fonts:
        cells = [f"{results['models'][lab]['per_font'][f]['cer']}%" for lab in labels]
        md.append(f"| {f} | {results['models'][labels[0]]['per_font'][f]['lines']} | " + " | ".join(cells) + " |")
    for lab in labels:
        md += [f"\n## Top confusions: {lab}\n", "| Truth | OCR | Count |", "|---|---|---:|"]
        for c in results["models"][lab]["top_confusions"]:
            md.append(f"| {_show(c['truth'])} | {_show(c['ocr'])} | {c['count']} |")
    (out / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    log("")
    log(f"    {'model':<24} {'CER':>8} {'WER':>8}")
    for lab in labels:
        m = results["models"][lab]
        log(f"    {lab:<24} {m['cer']:>7}% {m['wer']:>7}%")
    log(f"    full report (per font, top confusions): {out / 'report.md'}")
