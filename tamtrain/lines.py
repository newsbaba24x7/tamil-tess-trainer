"""Compare models on any folder of single-line images with ground truth (x.png + x.gt.txt),
for example a public benchmark. Optional groups.json ({"<image stem>": "<group>"}) in the
folder splits the results by group."""

from __future__ import annotations

import json
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from .evaluate import ModelSpec, _show, ocr_parallel
from .metrics import similarity
from .scans import IMAGE_EXTS, confusions, levenshtein, prepare
from .util import TamTrainError, log, save_json, step


def find_lines(dirs: list[Path]) -> list[tuple[Path, Path]]:
    pairs = []
    for d in dirs:
        for gt in sorted(d.rglob("*.gt.txt")):
            base = gt.with_name(gt.name[: -len(".gt.txt")])
            img = next((base.with_suffix(e) for e in IMAGE_EXTS if base.with_suffix(e).exists()), None)
            if img:
                pairs.append((img, gt))
    if not pairs:
        raise TamTrainError(f"No line images with a matching .gt.txt in {', '.join(map(str, dirs))}")
    return pairs


def _rate(e: int, n: int) -> float:
    return round(100 * e / max(n, 1), 2)


def raw_text(text: str) -> str:
    """Text as published benchmarks usually compare it: NFC and single spaces, nothing removed."""
    return " ".join(unicodedata.normalize("NFC", text).split())


def evaluate_lines(dirs: list[Path], models: list[ModelSpec], report_dir: Path, name: str = "lines", *,
                   psm: int = 7, jobs: int = 4, limit: int | None = None, raw: bool = False) -> dict:
    step(f"Evaluating on line images ({name})")
    pairs = find_lines(dirs)[:limit]
    groups: dict[str, str] = {}
    for d in dirs:
        if (d / "groups.json").exists():
            groups.update(json.loads((d / "groups.json").read_text(encoding="utf-8")))
    norm = raw_text if raw else prepare
    truths = [norm(gt.read_text(encoding="utf-8")) for _, gt in pairs]
    ids = [img.stem for img, _ in pairs]
    log(f"    {len(pairs)} lines" + (f", groups: {dict(Counter(groups.get(i, 'other') for i in ids))}" if groups else ""))

    ocr_out = {m.label: ocr_parallel([img for img, _ in pairs], m, psm, jobs) for m in models}
    crashed = {i for texts in ocr_out.values() for i, t in enumerate(texts) if t is None}
    if crashed:
        log(f"    {len(crashed)} image(s) made tesseract crash; left out for every model")
    keep = [i for i in range(len(pairs)) if i not in crashed]
    results: dict = {"name": name, "lines": len(keep), "psm": psm, "raw": raw,
                     "crashed": [ids[i] for i in sorted(crashed)], "models": {}}
    saved = {"truth": {ids[i]: truths[i] for i in keep}, "models": {}}
    for m in models:
        texts = [norm(t or "") for t in ocr_out[m.label]]
        saved["models"][m.label] = {ids[i]: texts[i] for i in keep}
        tot: dict[str, Counter] = defaultdict(Counter)
        per_line: dict[str, list[float]] = defaultdict(list)
        pairs_by_group: dict[str, list[tuple[str, str]]] = defaultdict(list)
        conf: Counter = Counter()
        samples = []
        for i in keep:
            gt, ocr = truths[i], texts[i]
            e = levenshtein(gt, ocr)
            we = levenshtein(gt.split(), ocr.split())
            for g in ("all", groups.get(ids[i], "other") if groups else None):
                if g is None:
                    continue
                c = tot[g]
                c["chars"] += len(gt)
                c["errors"] += e
                c["words"] += len(gt.split())
                c["word_errors"] += we
                c["lines"] += 1
                c["exact"] += e == 0
                per_line[g].append(e / max(len(gt), 1))
                pairs_by_group[g].append((gt, ocr))
            conf.update(confusions(gt, ocr))
            if e and len(samples) < 12:
                samples.append({"id": ids[i], "truth": gt, "ocr": ocr})
        results["models"][m.label] = {
            "model": str(m.tessdata_dir / f"{m.lang}.traineddata"),
            "groups": {g: {"lines": c["lines"], "cer": _rate(c["errors"], c["chars"]),
                           "mean_line_cer": round(100 * statistics.mean(per_line[g]), 2),
                           "wer": _rate(c["word_errors"], c["words"]),
                           "exact_lines": _rate(c["exact"], c["lines"]),
                           **similarity(*map(list, zip(*pairs_by_group[g])))} for g, c in tot.items()},
            "top_confusions": [{"truth": a, "ocr": b, "count": n} for (a, b), n in conf.most_common(20)],
            "error_samples": samples,
        }
    write_lines_report(report_dir, results)
    save_json(report_dir / f"{name}.ocr.json", saved)     # every line's text, to recompute any measure later
    return results


def write_lines_report(out: Path, results: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    name = results["name"]
    save_json(out / f"{name}.json", results)
    labels = list(results["models"])
    groups = list(results["models"][labels[0]]["groups"])
    md = [f"# Line-image evaluation: {name}\n",
          f"{results['lines']} line images, `--psm {results['psm']}`. Lower is better except exact lines.\n",
          "- **CER**: character errors / characters, over all lines together.",
          "- **Mean line CER**: CER of each line, averaged (some benchmarks report this one).",
          "- **WER**: word error rate. **Exact**: share of lines read without any error.",
          "- **BLEU, ANLS, METEOR** (0–1, higher is better): text similarity as in the RANLP 2025 OCR "
          "comparison; BLEU is the mean of per-line BLEU (NLTK defaults). See `tamtrain/metrics.py`.",
          ("- Text is compared as is (`--raw`): NFC normalisation and single spaces only, so invisible "
           "characters such as U+200C count as errors, as in most published benchmarks.\n" if results.get("raw") else
           "- Text is compared after NFC normalisation, with zero-width characters removed and quote/dash "
           "variants treated as the same character.\n")]
    if results.get("crashed"):
        md.append(f"{len(results['crashed'])} images made tesseract crash and are left out for every model.\n")
    for g in groups:
        n = results["models"][labels[0]]["groups"][g]["lines"]
        md += [f"\n## {'All lines' if g == 'all' else 'Group: ' + g} ({n} lines)\n",
               "| Model | CER | Mean line CER | WER | Exact lines | BLEU | ANLS | METEOR |",
               "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for lab in labels:
            x = results["models"][lab]["groups"][g]
            md.append(f"| {lab} | {x['cer']}% | {x['mean_line_cer']}% | {x['wer']}% | {x['exact_lines']}% "
                      f"| {x.get('bleu', '–')} | {x.get('anls', '–')} | {x.get('meteor', '–')} |")
    for lab in labels:
        md += [f"\n## Top confusions: {lab}\n", "| Truth | OCR | Count |", "|---|---|---:|"]
        for c in results["models"][lab]["top_confusions"]:
            md.append(f"| {_show(c['truth'])} | {_show(c['ocr'])} | {c['count']} |")
    (out / f"{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    log("")
    for g in groups:
        log(f"    [{g}]")
        log(f"    {'model':<26} {'CER':>8} {'line CER':>9} {'WER':>8} {'BLEU':>7} {'ANLS':>7} {'METEOR':>7}")
        for lab in labels:
            x = results["models"][lab]["groups"][g]
            log(f"    {lab:<26} {x['cer']:>7}% {x['mean_line_cer']:>8}% {x['wer']:>7}% "
                f"{x.get('bleu', 0):>7} {x.get('anls', 0):>7} {x.get('meteor', 0):>7}")
    log(f"    full report: {out / (name + '.md')}")
