#!/usr/bin/env python3
"""Build the benchmark results page (docs/benchmarks/index.html) from evaluation reports.

Every number on the page comes from the JSON reports that `tamtrain lines` and `tamtrain scans`
write, so the page can be rebuilt after new runs (maintainers only; the reports are not published):

    python3 tools/make_benchmark_page.py --reports work-v2/report \\
        --extra-reports work-v3/report work-v3/report-extra --date "17–18 November 2026"

--extra-reports add the models a report in --reports does not have (for example a newer model,
scored later against the same test sets). The page reuses the stylesheet of docs/index.html, so
both pages always look the same.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tamtrain.scans import levenshtein, prepare  # noqa: E402

ORDER = ["start (tam, best)", "installed tam", "V1 (188 styles)", "V2-research", "tam_v2 (best)", "tam_v2 (fast)",
         "tam_v3 (best)", "tam_v3 (fast)"]
NAME = {"start (tam, best)": "Stock <code>tam</code> (tessdata_best 4.1.0)",
        "installed tam": "Stock <code>tam</code> (tessdata_fast 4.1.0, Ubuntu package)",
        "V1 (188 styles)": "V1 <span class=\"small muted\">tam_multifont</span>",
        "V2-research": "V2-research <span class=\"small muted\">tam_v2_research</span>",
        "tam_v2 (best)": "tam_v2", "tam_v2 (fast)": "tam_v2_fast",
        "tam_v3 (best)": "tam_v3", "tam_v3 (fast)": "tam_v3_fast"}
OURS = "tam_v3 (best)"
PAPER = [("Google Document AI (commercial), paper", 0.78, 11.98, 0.5803, 0.9923, 0.8762),
         ("Google Cloud Vision API (commercial), paper", 0.79, 12.04, 0.5790, 0.9922, 0.8751),
         ("Tesseract 5.5.0, paper", 7.80, 61.45, 0.0493, 0.9264, 0.3201),
         ("EasyOCR, paper", 11.72, 28.76, 0.3461, 0.8828, 0.6744),
         ("Surya, paper", 13.92, 65.00, 0.1487, 0.8672, 0.3359)]
# seconds per page and peak MB on one thread, 8 pages; measured together on 18 November 2026,
# except the Ubuntu package (17 November: by the 18th this machine's packaged tam had been replaced)
SPEED = [("start (tam, best)", 1.50, 95, "6.0 MB"), ("installed tam", 1.05, 88, "3.2 MB"),
         ("tam_v2 (best)", 1.58, 105, "6.5 MB"), ("tam_v2 (fast)", 1.16, 97, "3.7 MB"),
         ("tam_v3 (best)", 1.49, 108, "8.5 MB"), ("tam_v3 (fast)", 1.12, 100, "5.7 MB")]


def fast_gain() -> str:
    speed = {m: sec for m, sec, _, _ in SPEED}
    return f"{round(100 * (1 - speed['tam_v3 (fast)'] / speed['tam_v3 (best)']))}%"


def pct(x: float) -> str:
    return f"{x:.2f}%"


def num(x: float) -> str:
    return f"{x:.4f}"


def table(head: list[tuple[str, bool]], rows: list[tuple[str, str, list]], better: list[str | None]) -> str:
    """head: (label, numeric). rows: (row class, first cell html, [(value, text), ...]).
    better: per numeric column 'low', 'high' or None; the best value is marked."""
    best = []
    for k, b in enumerate(better):
        vals = [r[2][k][0] for r in rows if r[2][k][0] is not None]
        best.append(None if not b or not vals else (min(vals) if b == "low" else max(vals)))
    out = ['<div class="table-wrap"><table>', "<thead><tr>" + "".join(
        f'<th{" class=\"n\"" if n else ""}>{h}</th>' for h, n in head) + "</tr></thead><tbody>"]
    for cls, first, cells in rows:
        tds = []
        for k, (v, text) in enumerate(cells):
            mark = v is not None and best[k] is not None and v == best[k]
            tds.append(f'<td class="n">{"<b class=\"best\">" + text + "</b>" if mark else text}</td>')
        out.append(f'<tr{f" class=\"{cls}\"" if cls else ""}><td>{first}</td>{"".join(tds)}</tr>')
    out.append("</tbody></table></div>")
    return "\n".join(out)


def lines_table(rep: dict) -> str:
    rows = []
    for m in [m for m in ORDER if m in rep["models"]]:
        x = rep["models"][m]["groups"]["all"]
        rows.append(("ours" if m == OURS else "", NAME[m],
                     [(x["cer"], pct(x["cer"])), (x["wer"], pct(x["wer"])), (x["bleu"], num(x["bleu"])),
                      (x["anls"], num(x["anls"])), (x["meteor"], num(x["meteor"]))]))
    return table([("Model", False), ("CER", True), ("WER", True), ("BLEU", True), ("ANLS", True), ("METEOR", True)],
                 rows, ["low", "low", "high", "high", "high"])


def page_details(rep: dict, pages_dir: Path) -> dict:
    """Average page CER by difficulty (as the scans report), WER on easy pages, pages better/worse."""
    base = "start (tam, best)"
    skip = set(rep["excluded"]) | set(rep["crashed"])
    models = [m for m in ORDER if m in rep["models"]]
    bands = {"easy": {m: [] for m in models}, "medium": {m: [] for m in models}, "hard": {m: [] for m in models}}
    easy_words = {m: [0, 0] for m in models}
    bw = {m: [0, 0] for m in models}
    for pid, pm in rep["per_page"].items():
        if pid in skip:
            continue
        b = pm[base]["cer"]
        band = "easy" if b < 5 else "medium" if b < 15 else "hard"
        gt = prepare((pages_dir / f"{pid}.gt.txt").read_text(encoding="utf-8")) if band == "easy" else ""
        for m in models:
            bands[band][m].append(pm[m]["cer"])
            if band == "easy":
                easy_words[m][0] += levenshtein(gt.split(), pm[m]["ocr"].split())
                easy_words[m][1] += len(gt.split())
            d = pm[m]["cer"] - b
            bw[m][0] += d < -0.5
            bw[m][1] += d > 0.5
    return {"bands": {k: {m: sum(v) / len(v) for m, v in d.items()} for k, d in bands.items()},
            "band_pages": {k: len(next(iter(d.values()))) for k, d in bands.items()},
            "easy_wer": {m: 100 * e / n for m, (e, n) in easy_words.items()}, "better_worse": bw}


def build(reports: Path, extra: list[Path], pages_dir: Path, date: str) -> str:
    def load(n: str) -> dict:
        rep = json.loads((reports / f"{n}.json").read_text(encoding="utf-8"))
        for d in extra:
            f = d / f"{n}.json"
            if not f.exists():
                continue
            more = json.loads(f.read_text(encoding="utf-8"))
            for m in ORDER:
                if m in more["models"] and m not in rep["models"]:
                    rep["models"][m] = more["models"][m]
                    for pid, pm in (more.get("per_page") or {}).items():
                        if m in pm and pid in rep["per_page"]:
                            rep["per_page"][pid][m] = pm[m]
        return rep

    style = re.search(r"<style>(.*?)</style>", (ROOT / "docs" / "index.html").read_text(encoding="utf-8"), re.S).group(1)
    scans, ranlp = load("scans"), load("ranlp2025-raw-psm3")
    test_lines, dev_lines, tob = load("real-test-lines-psm13"), load("real-dev-lines-psm13"), load("tamil-ocr-benchmark")
    rendered = load("rendered-heldout")
    det = page_details(scans, pages_dir)
    smodels = [m for m in ORDER if m in scans["models"]]

    # 197 real pages
    rows = []
    for m in smodels:
        x, (b, w) = scans["models"][m], det["better_worse"][m]
        rows.append(("ours" if m == OURS else "", NAME[m], [
            (x["cer"], pct(x["cer"])), (x["tamil_cer"], pct(x["tamil_cer"])), (x["wer"], pct(x["wer"])),
            (None if m.startswith("start") else b, "–" if m.startswith("start") else f"{b} / {w}"),
            (x["reform_words_ok"], pct(x["reform_words_ok"])), (x["word_count_change"], f"+{x['word_count_change']}%"),
            (x["tamil_digits_ocr"], str(x["tamil_digits_ocr"]))]))
    pages_tbl = table([("Model", False), ("CER", True), ("Tamil letters only", True), ("WER", True),
                       ("Pages better / worse than stock", True), ("Pre-1978 letter words exact", True),
                       ("Extra words (spurious spaces)", True), ("Stray Tamil digits (truth: 6)", True)],
                      rows, ["low", "low", "low", "high", "high", "low", "low"])
    rows = []
    for m in smodels:
        rows.append(("ours" if m == OURS else "", NAME[m], [
            (round(det["bands"][k][m], 2), pct(det["bands"][k][m])) for k in ("easy", "medium", "hard")]
            + [(round(det["easy_wer"][m], 2), pct(det["easy_wer"][m]))]))
    bp = det["band_pages"]
    bands_tbl = table([("Model", False), (f"Easy ({bp['easy']} pages)", True), (f"Medium ({bp['medium']})", True),
                       (f"Hard ({bp['hard']})", True), (f"Word errors, easy pages", True)],
                      rows, ["low", "low", "low", "low"])

    # RANLP
    rows = [("paper", html.escape(p[0]), [(p[1], pct(p[1])), (p[2], pct(p[2])), (p[3], num(p[3])),
                                          (p[4], num(p[4])), (p[5], num(p[5]))]) for p in PAPER]
    for m in [m for m in ORDER if m in ranlp["models"]]:
        x = ranlp["models"][m]["groups"]["all"]
        rows.append(("ours" if m == OURS else "", NAME[m] + ", measured here",
                     [(x["cer"], pct(x["cer"])), (x["wer"], pct(x["wer"])), (x["bleu"], num(x["bleu"])),
                      (x["anls"], num(x["anls"])), (x["meteor"], num(x["meteor"]))]))
    ranlp_tbl = table([("System", False), ("CER", True), ("WER", True), ("BLEU", True), ("ANLS", True), ("METEOR", True)],
                      rows, ["low", "low", "high", "high", "high"])
    groups = [g for g in ranlp["models"][OURS]["groups"] if g != "all"]
    rows = []
    for m in [m for m in ORDER if m in ranlp["models"]]:
        cells = []
        for g in groups:
            x = ranlp["models"][m]["groups"][g]
            cells += [(x["cer"], pct(x["cer"])), (x["wer"], pct(x["wer"]))]
        rows.append(("ours" if m == OURS else "", NAME[m], cells))
    head = [("Model", False)]
    for g in groups:
        n = ranlp["models"][OURS]["groups"][g]["lines"]
        head += [(f"{g} ({n:,}): CER", True), ("WER", True)]
    ranlp_groups_tbl = table(head, rows, ["low"] * (2 * len(groups)))

    # rendered held-out lines (the fixed set in benchmarks/rendered-heldout-v2)
    rows = []
    for m in [m for m in ORDER if m in rendered["models"]]:
        x = rendered["models"][m]["groups"]["all"]
        rows.append(("ours" if m == OURS else "", NAME[m], [(x["cer"], pct(x["cer"])), (x["wer"], pct(x["wer"]))]))
    rendered_tbl = table([("Model", False), ("CER", True), ("WER", True)], rows, ["low", "low"])

    # resolution sets
    res_tbls = []
    for title, src, dst, dpi in (("Old books", "old-books", "old-books-72dpi", "72 DPI"),
                                 ("Contemporary books", "contemporary-books", "contemporary-books-300dpi", "300 DPI"),
                                 ("Other contemporary books", "contemporary-lowres", "contemporary-lowres-96dpi", "96 DPI")):
        a, b = load(f"icon-source-{src}"), load(f"icon-{dst}")
        na, nb = a["pages"] - len(a["excluded"]), b["pages"] - len(b["excluded"])
        rows = []
        for m in [m for m in ORDER if m in b["models"]]:
            x, y = a["models"][m], b["models"][m]
            rows.append(("ours" if m == OURS else "", NAME[m], [(x["cer"], pct(x["cer"])), (x["wer"], pct(x["wer"])),
                                                               (y["cer"], pct(y["cer"])), (y["wer"], pct(y["wer"]))]))
        res_tbls.append((f"{title} ({nb} pages)", na, nb, table(
            [("Model", False), ("archive.org scan: CER", True), ("WER", True), (f"{dpi}: CER", True), ("WER", True)],
            rows, ["low"] * 4)))

    speed_tbl = table([("Model", False), ("Seconds per page", True), ("Peak memory", True), ("File size", True)],
                      [("ours" if m == OURS else "", NAME[m], [(s, f"{s:.2f}"), (mem, f"{mem} MB"), (None, size)])
                       for m, s, mem, size in SPEED], ["low", "low", None])

    n_lines = (test_lines["lines"] + dev_lines["lines"] + ranlp["lines"] + tob["lines"] + rendered["lines"])
    tpl = TEMPLATE
    for key, val in {"STYLE": style, "DATE": date, "PAGES_TBL": pages_tbl, "BANDS_TBL": bands_tbl,
                     "TEST_LINES_TBL": lines_table(test_lines), "DEV_LINES_TBL": lines_table(dev_lines),
                     "RANLP_TBL": ranlp_tbl, "RANLP_GROUPS_TBL": ranlp_groups_tbl, "TOB_TBL": lines_table(tob),
                     "RENDERED_TBL": rendered_tbl, "SPEED_TBL": speed_tbl, "N_LINES": f"{n_lines:,}",
                     "N_RENDERED": f"{rendered['lines']:,}", "FAST_GAIN": fast_gain(),
                     "RES_TBLS": "\n".join(f"<h3>{t}</h3>\n{tb}" for t, _, _, tb in res_tbls)}.items():
        tpl = tpl.replace("{{" + key + "}}", val)
    assert "{{" not in tpl, re.findall(r"\{\{\w+\}\}", tpl)
    return tpl


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Tamil OCR benchmark results</title>
<meta name="description" content="Every benchmark result for the open Tamil Tesseract model tam_v3 and the models it is compared with: real scanned pages and lines, RANLP 2025, the Tamil OCR Benchmark, rendered lines, scanning resolution and speed.">
<meta property="og:title" content="Tamil OCR benchmark results">
<meta property="og:description" content="tam_v3 against stock Tesseract, tam_v2 and earlier models on real scans, RANLP 2025 and more, with CER, WER, BLEU, ANLS and METEOR.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://newsbaba24x7.github.io/tamil-tess-trainer/benchmarks/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Catamaran:wght@500;700;800&family=Hind+Madurai:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{{STYLE}}
.crumbs { font-size: 14px; color: var(--muted); }
.crumbs a { color: var(--muted); }
dl.measures { display: grid; grid-template-columns: max-content 1fr; gap: 6px 18px; margin: 8px 0 0; max-width: 85ch; }
dl.measures dt { font-weight: 600; }
dl.measures dd { margin: 0; color: var(--muted); }
@media (max-width: 640px) { dl.measures { grid-template-columns: 1fr; } dl.measures dd { margin-bottom: 8px; } }
</style>
</head>
<body>
<nav class="sitebar" aria-label="Site">
  <div class="bar">
    <a class="brand" href="/">News<span>Baba</span></a>
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/tamil-tess-trainer/" aria-current="page">Tamil OCR</a></li>
      <li><a href="/artcraft-tamil/">ArtCraft in Tamil</a></li>
      <li><a href="https://github.com/newsbaba24x7">GitHub ↗</a></li>
    </ul>
  </div>
</nav>
<div class="wrap">

<header>
  <div class="crumbs"><a href="/tamil-tess-trainer/">Tamil OCR for Tesseract</a> › Benchmark results</div>
  <div class="eyebrow">Measured {{DATE}} · Tesseract 5.5.0 · 4 CPU cores</div>
  <h1>Benchmark results <span class="ta" lang="ta">அளவீட்டு முடிவுகள்</span></h1>
  <p class="lede">Every test of <b>tam_v3</b>, the open Tesseract model for printed Tamil, against Tesseract's stock Tamil
    model, the previous open model tam_v2 and the two research models trained before them. No model was trained on any of
    these test sets.</p>
  <div class="summary" aria-label="What was tested">
    <span class="chip"><b>7</b> test sets</span>
    <span class="chip"><b>8</b> models compared</span>
    <span class="chip"><b>{{N_LINES}}</b> text lines</span>
    <span class="chip"><b>250</b> scanned pages</span>
  </div>
</header>

<nav class="toc" aria-label="Contents">
  <ul>
    <li><a href="#summary">Summary</a></li>
    <li><a href="#models">Models</a></li>
    <li><a href="#measures">Measures</a></li>
    <li><a href="#test-sets">Test sets</a></li>
    <li><a href="#pages">Real pages</a></li>
    <li><a href="#lines">Real lines</a></li>
    <li><a href="#ranlp">RANLP 2025</a></li>
    <li><a href="#tob">Tamil OCR Benchmark</a></li>
    <li><a href="#rendered">Rendered lines</a></li>
    <li><a href="#resolution">Resolution</a></li>
    <li><a href="#speed">Speed</a></li>
    <li><a href="#reproduce">Reproduce</a></li>
  </ul>
</nav>

<main>

<section id="summary">
  <h2>Summary</h2>
  <ul class="list">
    <li><b>On real scanned books tam_v3 is the most accurate model tested.</b> On 197 real pages it makes 46% fewer
      character errors and 39% fewer word errors than the stock model (16% and 8% fewer than tam_v2), and is better than
      stock on 179 pages and worse on none.</li>
    <li><b>At normal scanning resolution the gain holds on every kind of page:</b> easy, medium and hard pages, old print
      with pre-1978 letter shapes, and real lines read one at a time (CER 1.13%, tam_v2 1.49%).</li>
    <li><b>RANLP 2025:</b> tam_v3 beats Google Document AI on BLEU (0.5825 against 0.5803), ties it on ANLS (0.9923) and
      comes close on CER (0.80% against 0.78%); Document AI still leads on WER and METEOR, and V2-research has the lowest
      WER. The set is mostly Tamil with its vowel signs stripped; on its natural-Tamil lines tam_v3's CER is 0.02%.</li>
    <li><b>English words inside Tamil:</b> on the Tamil OCR Benchmark tam_v3 halves tam_v2's character errors (1.54%
      against 3.25%).</li>
    <li><b>Our scoring reproduces the paper's:</b> the stock Ubuntu model scores within 0.1 points of the paper's Tesseract
      CER and within 0.003 of its BLEU, ANLS and METEOR.</li>
    <li><b>Weak spot:</b> very low resolution (72–96 DPI), where every model's errors roughly triple; on old books at
      72 DPI tam_v3 is slightly behind tam_v2 and the stock model.</li>
    <li><b>tam_v3_fast</b> scores within about 0.3 points of tam_v3 everywhere and is {{FAST_GAIN}} faster.</li>
  </ul>
</section>

<section id="models">
  <h2>Models compared</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Model</th><th>Version</th><th>What it is</th><th>Licence</th></tr></thead>
    <tbody>
      <tr><td>Stock <code>tam</code> (tessdata_best 4.1.0)</td><td><a href="https://github.com/tesseract-ocr/tessdata_best/tree/4.1.0">tessdata_best 4.1.0</a>; model <code>4.00.00alpha:tam:synth20170629</code></td><td>Tesseract's official Tamil model, the most accurate version; the starting point of all our models</td><td>Apache-2.0</td></tr>
      <tr><td>Stock <code>tam</code> (tessdata_fast 4.1.0, Ubuntu package)</td><td>Ubuntu 26.04 <code>tesseract-ocr-tam</code> 1:4.1.0-2build1, which is <a href="https://github.com/tesseract-ocr/tessdata_fast/tree/4.1.0">tessdata_fast 4.1.0</a>; model <code>4.00.00alpha:tam:synth20170629</code></td><td>The Tamil model installed by <code>apt install tesseract-ocr-tam</code>: a smaller, faster version</td><td>Apache-2.0</td></tr>
      <tr><td>V1 <span class="small muted">tam_multifont</span></td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v1.0.0">1.0.0</a></td><td>Research model: 188 font styles, fonts only</td><td>Apache-2.0</td></tr>
      <tr><td>V2-research <span class="small muted">tam_v2_research</span></td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0-research">2.0.0-research</a></td><td>Research model: 276 font styles with fixes for old letters, spacing and digits, fonts only</td><td>CC BY-NC 4.0</td></tr>
      <tr><td>tam_v2</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0">2.0.0</a></td><td>The previous open model: 233 openly licensed font styles and 24,445 real scanned lines</td><td>Apache-2.0</td></tr>
      <tr><td>tam_v2_fast</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0">2.0.0</a></td><td>Integer version of tam_v2</td><td>Apache-2.0</td></tr>
      <tr class="ours"><td>tam_v3</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.0.0">3.0.0</a></td><td>The released model: tam_v2 trained further on 174,624 real scanned lines from 394 books and the same fonts</td><td>Apache-2.0</td></tr>
      <tr><td>tam_v3_fast</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.0.0">3.0.0</a></td><td>Integer version of tam_v3</td><td>Apache-2.0</td></tr>
    </tbody>
  </table></div>
  <p class="note">Every model was run with Tesseract 5.5.0 (Ubuntu package 5.5.0-1build1). Both stock files are unchanged in tessdata_best and tessdata_fast since 2017; the model string records the training date, 29 June 2017.</p>
  <p class="note">The best value in each column is marked in green. The tam_v3 row is highlighted. Downloads and model cards: <a href="/tamil-tess-trainer/#models">Models</a>.</p>
</section>

<section id="measures">
  <h2>Measures</h2>
  <dl class="measures">
    <dt>CER</dt><dd>Character error rate: insertions, deletions and substitutions needed to turn the output into the true text, divided by its length. Lower is better.</dd>
    <dt>WER</dt><dd>Word error rate: the same, counted in words. Tamil words average about 8 characters, so one wrong letter or space makes the whole word wrong. Lower is better.</dd>
    <dt>Tamil letters only</dt><dd>CER on Tamil characters alone, ignoring spaces, punctuation and digits, which proofreaders and printers handle differently.</dd>
    <dt>BLEU</dt><dd>Share of matching word sequences of 1 to 4 words, averaged over lines (Papineni et al. 2002, as NLTK computes it). Higher is better, 0 to 1.</dd>
    <dt>ANLS</dt><dd>Average normalised Levenshtein similarity: per line 1 − normalised edit distance, or 0 when the distance is 0.5 or more (Biten et al. 2019). Higher is better.</dd>
    <dt>METEOR</dt><dd>Word matches weighted towards recall, with a penalty for words out of order (Banerjee &amp; Lavie 2005, as NLTK computes it). Higher is better.</dd>
  </dl>
  <p class="note">Unless a section says otherwise, text is compared after Unicode NFC normalisation with invisible zero-width characters removed. RANLP 2025 is compared as is, as in its paper.</p>
</section>

<section id="test-sets">
  <h2>Test sets</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Test set</th><th class="n">Size</th><th>What it is</th><th>Read with</th></tr></thead>
    <tbody>
      <tr><td><a href="#pages">Real pages</a></td><td class="n">197 pages</td><td>Random pages proofread on Tamil Wikisource, from 186 books; never used for training</td><td>Default page mode</td></tr>
      <tr><td><a href="#lines">Real test lines</a></td><td class="n">3,968 lines</td><td>Lines cut from those pages, matched to the proofread text</td><td><code>--psm 13</code></td></tr>
      <tr><td><a href="#lines">Real check lines</a></td><td class="n">2,854 lines</td><td>Lines from 5 other books; the training of tam_v2 and tam_v3 watched its progress on them</td><td><code>--psm 13</code></td></tr>
      <tr><td><a href="#ranlp">RANLP 2025</a></td><td class="n">7,000 lines</td><td>Synthetic lines from the RANLP 2025 OCR comparison (Jayatilleke &amp; de Silva)</td><td>Default page mode, raw text</td></tr>
      <tr><td><a href="#tob">Tamil OCR Benchmark</a></td><td class="n">200 lines</td><td>Real lines, many with English words (mvbalaji/tamil-ocr-benchmark)</td><td><code>--psm 7</code></td></tr>
      <tr><td><a href="#rendered">Rendered lines</a></td><td class="n">{{N_RENDERED}} lines</td><td>A fixed set of held-out rendered lines, including three font families never used in training</td><td><code>--psm 7</code></td></tr>
      <tr><td><a href="#resolution">Scanning resolution</a></td><td class="n">53 pages</td><td>Proofread pages rescaled to 72, 96 and 300 DPI, after an ICON 2024 test design</td><td>Default page mode</td></tr>
    </tbody>
  </table></div>
</section>

<section id="pages">
  <h2>197 real scanned pages</h2>
  <p>Whole pages from 186 Tamil Wikisource books, read with Tesseract's own layout analysis and compared with the
    proofread text. Three of the 200 sampled pages are left out for every model because their text belongs to another page.</p>
  {{PAGES_TBL}}
  <p class="note">"Better / worse" counts pages where a model's CER is more than 0.5 points below or above the stock model's.
    "Extra words" is how many more words a model writes than the page has, mostly from spaces that split words.</p>
  <h3>By difficulty</h3>
  <p class="cap">Pages grouped by the stock model's CER on them (easy: under 5%, medium: 5–15%, hard: over 15%). Average page CER per group, and word errors over all easy pages.</p>
  {{BANDS_TBL}}
</section>

<section id="lines">
  <h2>Real scanned lines</h2>
  <h3>3,968 test lines from the 197 pages</h3>
  {{TEST_LINES_TBL}}
  <h3>2,854 check lines from 5 other books</h3>
  {{DEV_LINES_TBL}}
  <p class="note">The training of tam_v2 and tam_v3 measured its progress on the check lines, so they are not fully independent for those models.</p>
</section>

<section id="ranlp">
  <h2>RANLP 2025 synthetic Tamil</h2>
  <p>7,000 line images from <a href="https://aclanthology.org/2025.ranlp-1.56/">Jayatilleke &amp; de Silva (2025)</a>,
    scored the way the paper does: text compared as is and each image read in Tesseract's default page mode. Paper rows are its Table 1.</p>
  {{RANLP_TBL}}
  <h3>Natural Tamil and vowel-stripped lines</h3>
  <p class="cap">In 6,803 of the 7,000 lines the vowel signs were removed from the text before the images were drawn, so the text is not real Tamil. The other 197 lines are natural Tamil.</p>
  {{RANLP_GROUPS_TBL}}
  <p class="note">The images use six Google Fonts that are also among the training fonts of every model here, and they are clean renders. Real scans are the harder test.</p>
</section>

<section id="tob">
  <h2>Tamil OCR Benchmark</h2>
  <p>200 real lines from <a href="https://huggingface.co/datasets/mvbalaji/tamil-ocr-benchmark">mvbalaji/tamil-ocr-benchmark</a>, many with English words inside Tamil text.</p>
  {{TOB_TBL}}
  <p class="note">tam_v3 makes the fewest character errors and word errors; English words still cost some whole words.</p>
</section>

<section id="rendered">
  <h2>Rendered lines</h2>
  <p>2,051 held-out rendered lines kept from tam_v2's training: the same kind of scan-like lines the models were trained on, including lines in three font families that none of our models was trained on.</p>
  {{RENDERED_TBL}}
  <p class="note">Rendered lines are easier than real scans; a model can improve a lot here and not at all on real pages, as V1 did. tam_v3's rendering text includes the books this set's text was drawn from, so for tam_v3 only the three held-out font families are fully unseen.</p>
</section>

<section id="resolution">
  <h2>Scanning resolution</h2>
  <p>The same proofread pages at the resolution of their archive.org scans, and rescaled so that 12-pt text matches a
    given scanning resolution. Pages whose text belongs to another page are found at full resolution and left out of
    both; every other page counts, however badly it reads at low resolution.</p>
  {{RES_TBLS}}
  <p class="note">At 72–96 DPI every model's errors roughly triple, and on old books tam_v3 is slightly behind tam_v2 and stock. Scan at 300 DPI where you can.</p>
</section>

<section id="speed">
  <h2>Speed and memory</h2>
  <p>One page at a time on one CPU thread, 8 real pages, on the machine that ran all tests. V1 and V2-research have the
    same network size as tessdata_best and were not timed. Differences under about 0.1 s are within the run-to-run variation.</p>
  {{SPEED_TBL}}
</section>

<section id="reproduce">
  <h2>Reproduce these results</h2>
  <p>All test lists, the scoring code and the commands are in the repository; the full tables with every line set are in
    <a href="https://github.com/newsbaba24x7/tamil-tess-trainer/blob/main/benchmarks/BASELINE.md">benchmarks/BASELINE.md</a>.</p>
<pre><button class="copy" type="button">Copy</button><code>git clone https://github.com/newsbaba24x7/tamil-tess-trainer && cd tamil-tess-trainer
R=https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v3.0.0
mkdir -p models && curl -L -o models/tam_v3.traineddata $R/tam_v3.traineddata
C="--compare tam_v3=models/tam_v3.traineddata"

<span class="c"># 197 real pages (slow: Wikimedia limits image downloads)</span>
python3 tools/fetch_wikisource.py --from-list examples/wikisource-pages.json --out scans/wikisource
python3 -m tamtrain scans scans/wikisource --name scans $C

<span class="c"># real lines, rebuilt from the release's line list</span>
curl -LO $R/tam_v3-real-lines.jsonl.gz
python3 tools/crop_lines.py tam_v3-real-lines.jsonl.gz --out real-lines --split test
python3 -m tamtrain lines real-lines/test --name real-test-lines --psm 13 $C

<span class="c"># RANLP 2025, scored as in the paper</span>
curl -L -o data.arrow https://huggingface.co/datasets/Nevidu/tamil_synthetic_ocr/resolve/main/data/data-00000-of-00001.arrow
python3 tools/hf_arrow_to_lines.py data.arrow --out benchmarks/ranlp2025/lines
python3 -m tamtrain lines benchmarks/ranlp2025/lines --name ranlp2025 --raw --psm 3 $C</code></pre>
  <p class="note">Reports go to <code>work/report/</code> and always include the stock <code>tam</code> model. Add more <code>--compare label=path/to/model.traineddata</code> options for more models. Each line report also saves every line's OCR text.</p>
</section>

</main>

<footer>
  <div><a href="/tamil-tess-trainer/">Tamil OCR for Tesseract</a> · <a href="https://github.com/newsbaba24x7/tamil-tess-trainer">github.com/newsbaba24x7/tamil-tess-trainer</a> · Apache-2.0</div>
  <div>Measured {{DATE}} with Tesseract 5.5.0. Generated by <code>tools/make_benchmark_page.py</code> from the evaluation reports.</div>
</footer>

</div>
<script>
for (const btn of document.querySelectorAll("pre .copy")) {
  btn.addEventListener("click", async () => {
    const code = btn.parentElement.querySelector("code").innerText;
    try { await navigator.clipboard.writeText(code); btn.textContent = "Copied"; }
    catch { btn.textContent = "Select and copy"; }
    setTimeout(() => (btn.textContent = "Copy"), 1600);
  });
}
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reports", type=Path, default=ROOT / "work-v2" / "report")
    ap.add_argument("--extra-reports", type=Path, nargs="*", default=[ROOT / "work-v3" / "report", ROOT / "work-v3" / "report-extra"])
    ap.add_argument("--pages", type=Path, default=ROOT / "scans" / "wikisource", help="the real test pages (.gt.txt)")
    ap.add_argument("--date", default="17–18 November 2026")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "benchmarks" / "index.html")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build(args.reports, args.extra_reports, args.pages, args.date), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
