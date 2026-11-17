"""Compare models on real scanned pages: a page image plus its proofread text (.gt.txt).

Rendered lines show how well a model reads fonts; real scans show how it copes with paper,
ink, old printing and page layout. This module OCRs whole pages (layout analysis included)
and compares the text with the proofread page text.
"""

from __future__ import annotations

import difflib
import json
import re
import statistics
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Sequence

from .evaluate import INVISIBLE, ModelSpec, _show, align, ocr_parallel
from .tamil import normalize
from .util import TamTrainError, log, save_json, step

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")
# Proofreaders and printers use different quote and dash characters for the same mark.
PUNCT_FOLD = str.maketrans({"‘": "'", "’": "'", "‛": "'", "′": "'", "`": "'", "“": '"', "”": '"',
                            "″": '"', "–": "-", "—": "-", "―": "-", "…": "..."})
TAMIL_DIGITS = set("௦௧௨௩௪௫௬௭௮௯")
REFORM_LETTERS = re.compile("[ணறன][ாொோ]|[ணலளன]ை")
MISMATCH_CER = 50.0


def levenshtein(p: Sequence, t: Sequence) -> int:
    """Edit distance with Myers/Hyyrö's bit-parallel algorithm: fast enough for whole pages."""
    m = len(p)
    if m == 0:
        return len(t)
    if not t:
        return m
    peq: dict = {}
    for i, c in enumerate(p):
        peq[c] = peq.get(c, 0) | (1 << i)
    full = (1 << m) - 1
    high = 1 << (m - 1)
    pv, mv, score = full, 0, m
    for c in t:
        eq = peq.get(c, 0)
        xv = eq | mv
        xh = ((((eq & pv) + pv) & full) ^ pv) | eq
        ph = mv | (~(xh | pv) & full)
        mh = pv & xh
        if ph & high:
            score += 1
        elif mh & high:
            score -= 1
        ph = ((ph << 1) | 1) & full
        mh = (mh << 1) & full
        pv = mh | (~(xv | ph) & full)
        mv = ph & xv
    return score


def prepare(text: str) -> str:
    """Text as compared: NFC, no zero-width characters, folded quotes/dashes, single spaces."""
    return normalize(text.translate(INVISIBLE).translate(PUNCT_FOLD))


def tamil_only(text: str) -> str:
    return "".join(c for c in text if "஀" <= c <= "௿")


def confusions(gt: str, ocr: str, max_region: int = 6) -> Counter:
    """Character substitutions/insertions/deletions inside short differing regions."""
    out: Counter = Counter()
    sm = difflib.SequenceMatcher(None, gt, ocr, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or max(i2 - i1, j2 - j1) > max_region:
            continue
        out.update(align(gt[i1:i2], ocr[j1:j2])[1])
    return out


def find_pages(dirs: list[Path]) -> list[tuple[Path, Path]]:
    pairs = []
    for d in dirs:
        if not d.is_dir():
            raise TamTrainError(f"Not a folder: {d}")
        for gt in sorted(d.rglob("*.gt.txt")):
            base = gt.with_name(gt.name[: -len(".gt.txt")])
            img = next((base.with_suffix(e) for e in IMAGE_EXTS if base.with_suffix(e).exists()), None)
            if img:
                pairs.append((img, gt))
    if not pairs:
        raise TamTrainError(f"No page images with a matching .gt.txt in {', '.join(map(str, dirs))}")
    return pairs


def load_page_info(dirs: list[Path]) -> dict[str, dict]:
    """Optional pages.json (written by tools/fetch_wikisource.py): book title and source per page."""
    info = {}
    for d in dirs:
        f = d / "pages.json"
        if f.exists():
            for row in json.loads(f.read_text(encoding="utf-8")):
                info[row["id"]] = row
    return info


def evaluate_scans(dirs: list[Path], models: list[ModelSpec], report_dir: Path, *, psm: int = 3,
                   jobs: int = 4, limit: int | None = None, name: str = "scans",
                   exclude_from: Path | None = None) -> dict:
    """exclude_from: a scans report of the same pages at full resolution. Its excluded pages are
    left out here, and no page is excluded for scoring badly: on a rescaled (low-resolution) copy,
    a page every model fails is a real failure, not a page with another page's text."""
    step("Evaluating on real scanned pages")
    for m in models:
        if not (m.tessdata_dir / f"{m.lang}.traineddata").exists():
            raise TamTrainError(f"Model not found: {m.tessdata_dir / (m.lang + '.traineddata')}")
    pairs = find_pages(dirs)[:limit]
    info = load_page_info(dirs)
    truths = [prepare(gt.read_text(encoding="utf-8")) for _, gt in pairs]
    ids = [img.stem for img, _ in pairs]
    log(f"    {len(pairs)} pages" + (f" from {len({info[i]['book'] for i in ids if i in info})} books" if info else ""))

    results: dict = {"pages": len(pairs), "psm": psm, "models": {}, "per_page": {i: {} for i in ids}}
    rows: dict[str, dict[str, dict]] = {}
    confs: dict[str, dict[str, Counter]] = {}
    raw = {m.label: ocr_parallel([img for img, _ in pairs], m, psm, jobs) for m in models}
    crashed = {ids[i] for texts in raw.values() for i, t in enumerate(texts) if t is None}
    if crashed:
        log(f"    {len(crashed)} page(s) made tesseract crash; left out for every model")
    for model in models:
        texts = [prepare(t or "") for t in raw[model.label]]
        rows[model.label], confs[model.label] = {}, {}
        for pid, gt, ocr in zip(ids, truths, texts):
            gt_t, ocr_t = tamil_only(gt), tamil_only(ocr)
            row = {
                "chars": len(gt), "errors": levenshtein(gt, ocr),
                "tamil_chars": len(gt_t), "tamil_errors": levenshtein(gt_t, ocr_t),
                "words": len(gt.split()), "word_errors": levenshtein(gt.split(), ocr.split()),
                "ocr_words": len(ocr.split()),
                "tamil_digits_ocr": sum(c in TAMIL_DIGITS for c in ocr),
                "tamil_digits_gt": sum(c in TAMIL_DIGITS for c in gt),
                **reform_words(gt, ocr),
            }
            rows[model.label][pid] = row
            confs[model.label][pid] = confusions(gt, ocr)
            results["per_page"][pid][model.label] = {
                "cer": _rate(row["errors"], row["chars"]), "tamil_cer": _rate(row["tamil_errors"], row["tamil_chars"]),
                "wer": _rate(row["word_errors"], row["words"]), "ocr": ocr}

    # A page that every model gets mostly wrong almost always has text that belongs to another
    # page (Wikisource scans and texts are sometimes offset by a page). Those are listed, not counted.
    if exclude_from:
        wrong_text = set(json.loads(exclude_from.read_text(encoding="utf-8")).get("excluded", []))
        excluded = [p for p in ids if p in crashed or p in wrong_text]
        results["exclusions_from"] = str(exclude_from)
    else:
        excluded = [p for p in ids if p in crashed
                    or min(results["per_page"][p][m.label]["cer"] for m in models) > MISMATCH_CER]
    results["crashed"] = sorted(crashed)
    kept = [p for p in ids if p not in excluded]
    results["excluded"] = excluded
    for model in models:
        tot: Counter = Counter()
        conf: Counter = Counter()
        for pid in kept:
            tot.update(rows[model.label][pid])
            conf.update(confs[model.label][pid])
        results["models"][model.label] = {
            "model": str(model.tessdata_dir / f"{model.lang}.traineddata"),
            "cer": _rate(tot["errors"], tot["chars"]),
            "tamil_cer": _rate(tot["tamil_errors"], tot["tamil_chars"]),
            "wer": _rate(tot["word_errors"], tot["words"]),
            "median_page_cer": round(statistics.median(results["per_page"][p][model.label]["cer"] for p in kept), 2)
            if kept else 0.0,
            "word_count_change": round(100 * (tot["ocr_words"] - tot["words"]) / max(tot["words"], 1), 1),
            "tamil_digits_ocr": tot["tamil_digits_ocr"], "tamil_digits_gt": tot["tamil_digits_gt"],
            "reform_words": tot["reform_words"], "reform_words_ok": _rate(tot["reform_ok"], tot["reform_words"]),
            "other_words_ok": _rate(tot["other_ok"], tot["other_words"]),
            "top_confusions": [{"truth": a, "ocr": b, "count": n} for (a, b), n in conf.most_common(20)],
        }
    for pid, gt in zip(ids, truths):
        results["per_page"][pid]["_truth"] = gt
        if pid in info:
            results["per_page"][pid]["_info"] = info[pid]
    write_scans_report(report_dir, results, name)
    return results


def reform_words(gt: str, ocr: str) -> dict:
    """Exact-word recall for words with letters whose printed shape changed in the 1978 script
    reform (ணா றா னா, ணொ றோ…, ணை லை ளை னை) and for all other words. Old books print these
    letters differently, so a low score here and not elsewhere points to old-print trouble."""
    strip = ".,;:!?'\"()-[]"
    avail = Counter(w.strip(strip) for w in ocr.split())
    out = Counter(reform_words=0, reform_ok=0, other_words=0, other_ok=0)
    for w in (w.strip(strip) for w in gt.split()):
        if not w:
            continue
        kind = "reform" if REFORM_LETTERS.search(w) else "other"
        out[kind + "_words"] += 1
        if avail[w] > 0:
            avail[w] -= 1
            out[kind + "_ok"] += 1
    return dict(out)


def _rate(e: int, n: int) -> float:
    return round(100 * e / max(n, 1), 2)


def write_scans_report(out: Path, results: dict, name: str = "scans") -> None:
    out.mkdir(parents=True, exist_ok=True)
    save_json(out / f"{name}.json", results)
    labels = list(results["models"])
    base = labels[0]
    pages = results["per_page"]
    excluded = results.get("excluded", [])
    ids = [p for p in pages if p not in excluded]

    md = ["# Evaluation on real scanned pages\n",
          f"{len(ids)} scanned pages, whole-page OCR (`--psm {results['psm']}`, layout analysis included), "
          "compared with the proofread page text. Lower is better."
          + (f" {len(excluded)} more pages were left out (listed at the end): pages where every model scored "
             f"above {MISMATCH_CER:.0f}% CER, which almost always means the text belongs to a different page, "
             "and pages on which tesseract itself crashed." if excluded else "") + "\n",
          "- **CER**: character error rate over all text, spaces and punctuation included.",
          "- **Tamil CER**: the same on Tamil characters only. Spacing, punctuation, digits and Latin are "
          "ignored, so this isolates how well the Tamil script is read.",
          "- **WER**: word error rate.",
          "- **Words ±**: how many more (or fewer) words the OCR text has than the page. A large plus "
          "means words are being split by spurious spaces.",
          "- Running headers and page numbers count when the proofreaders typed them. Curly and straight "
          "quotes and the dash variants are treated as the same character; zero-width characters are ignored.\n",
          f"Better/worse: pages where the model's CER is lower/higher than **{base}** by more than 0.5 points.\n",
          "| Model | CER | Tamil CER | WER | Words ± | Median page CER | Better | Worse | Tamil digits written |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for lab in labels:
        m = results["models"][lab]
        if lab == base:
            better = worse = "–"
        else:
            diffs = [pages[p][lab]["cer"] - pages[p][base]["cer"] for p in ids]
            better, worse = sum(d < -0.5 for d in diffs), sum(d > 0.5 for d in diffs)
        md.append(f"| {lab} | {m['cer']}% | {m['tamil_cer']}% | {m['wer']}% | {m['word_count_change']:+}% | "
                  f"{m['median_page_cer']}% | "
                  f"{better} | {worse} | {m['tamil_digits_ocr']} (truth: {m['tamil_digits_gt']}) |")

    md += ["\n## Letters changed by the 1978 script reform\n",
           "Books printed before the reform write ணா றா னா (and ணொ றோ…) and ணை லை ளை னை with different "
           "shapes. Share of words read exactly, for words with these letters and for all other words.\n",
           "| Model | Words with these letters | Other words |", "|---|---:|---:|"]
    for lab in labels:
        m = results["models"][lab]
        md.append(f"| {lab} | {m['reform_words_ok']}% (of {m['reform_words']}) | {m['other_words_ok']}% |")

    # by scan difficulty, measured with the baseline model
    bands = [("easy: baseline CER < 5%", 0, 5), ("medium: 5-15%", 5, 15), ("hard: > 15%", 15, 1e9)]
    md += ["\n## By scan difficulty\n",
           f"Pages grouped by **{base}**'s CER on them. Average page CER per group.\n",
           "| Pages | Count | " + " | ".join(labels) + " |", "|---|---:|" + "---:|" * len(labels)]
    for band, lo, hi in bands:
        group = [p for p in ids if lo <= pages[p][base]["cer"] < hi]
        if group:
            cells = [f"{statistics.mean(pages[p][lab]['cer'] for p in group):.2f}%" for lab in labels]
            md.append(f"| {band} | {len(group)} | " + " | ".join(cells) + " |")

    md += ["\n## Every page\n", "| Page | " + " | ".join(labels) + " |", "|---|" + "---:|" * len(labels)]
    for p in sorted(ids, key=lambda p: pages[p][base]["cer"]):
        inf = pages[p].get("_info")
        url = urllib.parse.unquote(inf["url"]).replace("(", "%28").replace(")", "%29") if inf else ""
        cell = f"[{inf['book']} p.{inf['page']}]({url})" if inf else p
        md.append(f"| {cell} | " + " | ".join(f"{pages[p][lab]['cer']}%" for lab in labels) + " |")

    if excluded:
        md += ["\n## Left out\n"]
        crashed = set(results.get("crashed", []))
        for p in excluded:
            inf = pages[p].get("_info")
            why = "tesseract crashed on this page" if p in crashed else "text does not match the image"
            md.append(f"- {inf['book']} p.{inf['page']} ({why}): {urllib.parse.unquote(inf['url'])}"
                      if inf else f"- {p} ({why})")
    for lab in labels:
        md += [f"\n## Top confusions: {lab}\n", "| Truth | OCR | Count |", "|---|---|---:|"]
        for c in results["models"][lab]["top_confusions"]:
            md.append(f"| {_show(c['truth'])} | {_show(c['ocr'])} | {c['count']} |")
    (out / f"{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    log("")
    log(f"    {'model':<24} {'CER':>8} {'TamilCER':>9} {'WER':>8}")
    for lab in labels:
        m = results["models"][lab]
        log(f"    {lab:<24} {m['cer']:>7}% {m['tamil_cer']:>8}% {m['wer']:>7}%")
    log(f"    full report (per page, by difficulty, confusions): {out / (name + '.md')}")
