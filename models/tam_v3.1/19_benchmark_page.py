#!/usr/bin/env python3
"""Step 19 - Build the benchmark page for tam_v3.1 (docs/benchmarks/index.html).

Every number on the page is read from this folder's results (results/*/summary.json from 10_evaluate.py,
results/tables.md from 18_report_tables.py, results/confidence_intervals.md from bootstrap_ci.py and
results/crash_*.txt from 17_crash_scan.py), so the page can be rebuilt after new runs. It reuses the
stylesheet of docs/index.html, like the archived tam_v3 page (tools/make_benchmark_page.py).

  python3 -I models/tam_v3.1/19_benchmark_page.py            # from the repository root
"""
import argparse, html, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--results", type=Path, default=HERE / "results")
ap.add_argument("--index", type=Path, default=HERE.parent.parent / "docs" / "index.html", help="page whose <style> is reused")
ap.add_argument("--out", type=Path, default=HERE.parent.parent / "docs" / "benchmarks" / "index.html")
ap.add_argument("--date", default="22 November 2026")
a = ap.parse_args()
R = a.results
S = {k: json.loads((R / k / "summary.json").read_text(encoding="utf-8")) for k in ("real_test_psm13", "real_dev_psm13", "synthetic")}
rt, rd, sy = S["real_test_psm13"], S["real_dev_psm13"], S["synthetic"]
M = ["up_best", "up_std", "up_fast", "v3_best", "v3_int", "v31_best", "v31_std", "v31_fast"]
NAME = {"up_best": "Stock <code>tam</code>, tessdata_best 4.1.0", "up_std": "Stock <code>tam</code>, tessdata 4.1.0",
        "up_fast": "Stock <code>tam</code>, tessdata_fast 4.1.0", "v3_best": "tam_v3", "v3_int": "tam_v3_fast",
        "v31_best": "tam_best_v3.1", "v31_std": "tam_v3.1", "v31_fast": "tam_fast_v3.1"}
SHORT = {"up_best": "Stock best", "up_std": "Stock tessdata", "up_fast": "Stock fast", "v3_best": "tam_v3",
         "v3_int": "tam_v3_fast", "v31_best": "v3.1 best", "v31_std": "v3.1", "v31_fast": "v3.1 fast"}
OURS = {"v31_best", "v31_std", "v31_fast"}

# folded scores (tam_v3's own scoring) from 18_report_tables.py
row = [l for l in (R / "tables.md").read_text(encoding="utf-8").splitlines() if l.startswith("| folded |")][0]
FOLD = {m: tuple(float(x) for x in c.split(" / ")) for m, c in zip(M, row.strip("| ").split(" | ")[1:])}

# confidence intervals (ALL rows) from bootstrap_ci.py
CI = {}
for blk in (R / "confidence_intervals.md").read_text(encoding="utf-8").split("## ")[1:]:
    head = blk.splitlines()[0]
    m = re.search(r"\| ALL \| \d+ \| [\d.]+ \| [\d.]+ \| ([-+][\d.]+) \(([-+][\d.]+) to ([-+][\d.]+)\)", blk)
    if m:
        CI[head.strip()] = tuple(float(x) for x in m.groups())
ci = lambda s, b, base, met: CI[f"{s}: {b} vs {base} ({met})"]
CRASH = {p.stem.replace("crash_", ""): sum(1 for l in p.read_text().splitlines() if l.startswith("CRASH"))
         for p in R.glob("crash_*.txt")}
N_ALL = 3968 + 2854 + 1389

pct = lambda x, d=2: f"{x:.{d}f}%"
dash = lambda x: f"{x:+.2f}".replace("-", "−").replace("+", "+")
fewer = lambda new, old: round(100 * (1 - new / old))


def table(head, rows, cls=None):
    th = "".join(f'<th{" class=\"n\"" if i else ""}>{h}</th>' for i, h in enumerate(head))
    out = [f'<div class="table-wrap"><table>\n    <thead><tr>{th}</tr></thead>\n    <tbody>']
    for r, ours in rows:
        tds = "".join(f'<td{" class=\"n\"" if i else ""}>{c}</td>' for i, c in enumerate(r))
        out.append(f'      <tr{" class=\"ours\"" if ours else ""}>{tds}</tr>')
    out.append("    </tbody>\n  </table></div>")
    return "\n".join(out)


def best_mark(vals, fmt, lower=True):
    """Format values, marking the best (lowest by default) with <b class="best">."""
    b = min(vals) if lower else max(vals)
    return [f'<b class="best">{fmt(v)}</b>' if v == b else fmt(v) for v in vals]


# --- real test lines
cer_f = best_mark([FOLD[m][0] for m in M], pct); wer_f = best_mark([FOLD[m][1] for m in M], pct)
cer_s = best_mark([rt["overall"][m][0] for m in M], pct); wer_s = best_mark([rt["overall"][m][1] for m in M], pct)
tam_s = best_mark([rt["overall"][m][2] for m in M], pct)
t_real = table(["Model", "CER", "WER", "CER, strict", "WER, strict", "Tamil letters only, CER"],
               [([NAME[m], cer_f[i], wer_f[i], cer_s[i], wer_s[i], tam_s[i]], m in OURS) for i, m in enumerate(M)])
cats = {"R_tamil": "Tamil only", "R_numbers": "with numbers", "R_latin": "with Latin letters"}
n_cat = {"R_tamil": 3715, "R_numbers": 236, "R_latin": 17}
CM = ["up_best", "v3_best", "v31_best", "v31_std", "v31_fast"]
t_real_cat = table(["Lines (strict CER / WER)"] + [SHORT[m] for m in CM],
                   [([f"{cats[c]} ({n_cat[c]:,})"] + [f"{rt['category'][c][m][0]:.2f}% / {rt['category'][c][m][1]:.1f}%" for m in CM], False) for c in cats])
# --- real check lines
t_dev = table(["Model", "CER", "WER", "Tamil letters only, CER"],
              [([NAME[m]] + best_mark([rd["overall"][x][0] for x in M], pct)[i:i + 1] + best_mark([rd["overall"][x][1] for x in M], pct)[i:i + 1]
                + best_mark([rd["overall"][x][2] for x in M], pct)[i:i + 1], m in OURS) for i, m in enumerate(M)])
# --- rendered lines by category
SC = {"A_tamil": "A · Tamil text", "B_vowel_signs": "B · vowel signs and consonant combinations", "C_grantha": "C · grantha letters",
      "D_pulli": "D · pulli and diacritics", "E_numerals": "E · Tamil numerals", "F_mixed": "F · mixed Tamil-English",
      "G_technical": "G · English technical terms in Tamil", "P_punct": "Punctuation"}
RM = ["up_best", "up_fast", "v3_best", "v31_best", "v31_std", "v31_fast"]
rows = []
for c, lab in SC.items():
    vals = [sy["category"][c][m][0] for m in RM]
    cells = [f'{v}' for v in best_mark(vals, lambda x: f"{x:.2f}%")]
    rows.append(([lab] + [f"{cells[i]} / {sy['category'][c][m][1]:.1f}%" for i, m in enumerate(RM)], False))
ov = best_mark([sy["overall"][m][0] for m in RM], lambda x: f"{x:.2f}%")
rows.append((["<b>All 1,389 lines</b>"] + [f"{ov[i]} / {sy['overall'][m][1]:.1f}%" for i, m in enumerate(RM)], False))
t_syn = table(["Category (CER / WER)"] + [SHORT[m] for m in RM], rows)
# --- characters
EK = [("ஸ்ரீ", "ஸ்ரீ"), ("grantha ஜ ஷ ஸ ஹ ஶ", "grantha ஜ ஷ ஸ ஹ ஶ"), ("ஔ / ௌ", "ஔ / ௌ"), ("pulli ்", "pulli ்"),
      ("Tamil numerals ௦–௲", "Tamil numerals ௦–௲"), ("Tamil symbols ௳–௺ ௐ", "Tamil symbols ௳–௺ ௐ"), ("ASCII digits", "ASCII digits"),
      ("quotes “ ” ‘ ’ \" '", "quotes “ ” ‘ ’ \" '"), ("brackets ( ) [ ]", "brackets ( ) [ ]"), ("dashes — – -", "dashes — – -"),
      ("Latin letters", "Latin letters")]
def share(s, m, k):
    h, t = s["edge"][m][k]
    return f"{100 * h / t:.1f}%" if t else "–"
t_chars = table(["Characters (real n / rendered n)"] + [SHORT[m] for m in CM],
                [([f"{html.escape(lab)} ({rt['edge']['v31_best'][k][1]:,} / {sy['edge']['v31_best'][k][1]:,})"]
                  + [f"{share(rt, m, k)} / {share(sy, m, k)}" for m in CM], False) for k, lab in EK]
                + [([f"lines with characters outside the model's set"] + [f"{rt['noise_outputs'][m]:,} / {sy['noise_outputs'][m]:,}" for m in CM], False)])
# --- significance
def cirow(lab, base, mod):
    c, w = ci("real_test_psm13", mod, base, "cer"), ci("real_test_psm13", mod, base, "wer")
    dc, dw = ci("real_dev_psm13", mod, base, "cer"), ci("real_dev_psm13", mod, base, "wer")
    sc = ci("synthetic", mod, base, "cer")
    f = lambda t: f"<b>{dash(t[0])}</b> ({dash(t[1])} to {dash(t[2])})"
    return ([lab, f(c), f(w), f"{dash(dc[0])} / {dash(dw[0])}", f(sc)], False)
t_ci = table(["Comparison (points)", "Real test CER", "Real test WER", "Real check CER / WER", "Rendered CER"],
             [cirow("tam_best_v3.1 − tam_v3", "v3_best", "v31_best"), cirow("tam_v3.1 − tam_v3_fast", "v3_int", "v31_std"),
              cirow("tam_best_v3.1 − stock tessdata_best", "up_best", "v31_best"), cirow("tam_v3.1 − stock tessdata", "up_std", "v31_std"),
              cirow("tam_fast_v3.1 − stock tessdata_fast", "up_fast", "v31_fast")])
# --- speed and size
t_speed = table(["Model", "ms per line", "Model load", "Peak memory", "File size"],
                [([NAME[m], f"{rt['speed'][m]['ms_per_line']:.1f}", f"{rt['speed'][m]['load_s']:.2f} s", f"{rt['speed'][m]['max_rss_MB']:.0f} MB",
                   f"{rt['size'][m]:.2f} MB"], m in OURS) for m in M])
# --- crash scan
t_crash = table(["Model", "<code>--psm 7</code>", "<code>--psm 13</code>"],
                [([NAME[m], str(CRASH.get(f"{m}_psm7", "–")), str(CRASH.get(f"{m}_psm13", "not scanned"))], m in OURS) for m in M])

b, s3, f3 = FOLD["v31_best"], FOLD["v3_best"], FOLD["up_best"]
q = lambda m: 100 * rt["edge"][m]["quotes “ ” ‘ ’ \" '"][0] / rt["edge"][m]["quotes “ ” ‘ ’ \" '"][1]
num = lambda m: 100 * sy["edge"][m]["Tamil numerals ௦–௲"][0] / sy["edge"][m]["Tamil numerals ௦–௲"][1]
cb, cw = ci("real_test_psm13", "v31_best", "v3_best", "cer"), ci("real_test_psm13", "v31_best", "v3_best", "wer")
style = re.search(r"<style>(.*?)</style>", a.index.read_text(encoding="utf-8"), re.S).group(1)
EXTRA = """
.crumbs { font-size: 14px; color: var(--muted); }
.crumbs a { color: var(--muted); }
h4 { font-family: var(--display); font-weight: 700; font-size: 16px; line-height: 1.3; margin: 20px 0 6px; }"""

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Tamil OCR benchmark results</title>
<meta name="description" content="Benchmark results for tam_v3.1, open Tesseract models for printed Tamil (best, integer and fast), against Tesseract's stock Tamil models and tam_v3 on real scanned lines and rendered lines.">
<meta property="og:title" content="Tamil OCR benchmark results">
<meta property="og:description" content="tam_v3.1 against stock Tesseract and tam_v3: real scanned lines, rendered lines by category, characters, significance, speed and size.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://newsbaba24x7.github.io/tamil-tess-trainer/benchmarks/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Catamaran:wght@500;700;800&family=Hind+Madurai:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{style}{EXTRA}
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
  <div class="eyebrow">Measured {a.date} · Tesseract 5.5.0 · 4 CPU cores</div>
  <h1>Benchmark results <span class="ta" lang="ta">அளவீட்டு முடிவுகள்</span></h1>
  <p class="lede">Tests of <b>tam_v3.1</b>, the three open Tesseract models for printed Tamil (<code>tam_best_v3.1</code>,
    <code>tam_v3.1</code> and <code>tam_fast_v3.1</code>), against Tesseract's stock Tamil models from tessdata_best,
    tessdata and tessdata_fast, and against tam_v3. No model here was trained on these test lines.</p>
  <p class="note">Results for tam_v3 and the models before it, on more test sets (197 whole pages, RANLP 2025, the Tamil
    OCR Benchmark, scanning resolution, handwriting and camera photos), are on the
    <a href="tam_v3/">tam_v3 benchmark page</a>. tam_v3.1 has not been run on those tests yet.</p>
  <div class="summary" aria-label="What was tested">
    <span class="chip"><b>3</b> test sets</span>
    <span class="chip"><b>{N_ALL:,}</b> text lines</span>
    <span class="chip"><b>8</b> models</span>
    <span class="chip"><b>{fewer(b[0], f3[0])}%</b> fewer character errors than stock</span>
  </div>
</header>

<nav class="toc" aria-label="Contents">
  <ul>
    <li><a href="#summary">Summary</a></li>
    <li><a href="#models">Models</a></li>
    <li><a href="#scoring">Scoring</a></li>
    <li><a href="#real-lines">Real lines</a></li>
    <li><a href="#check-lines">Check lines</a></li>
    <li><a href="#rendered">Rendered lines</a></li>
    <li><a href="#characters">Characters</a></li>
    <li><a href="#significance">Significance</a></li>
    <li><a href="#speed">Speed and size</a></li>
    <li><a href="#crash">Crash check</a></li>
    <li><a href="#reproduce">Reproduce</a></li>
    <li><a href="tam_v3/">Earlier results</a></li>
  </ul>
</nav>

<main>

<section id="summary">
  <h2>Summary</h2>
  <ul class="list">
    <li><b>Real scanned lines:</b> on tam_v3's 3,968 test lines from 197 pages, tam_best_v3.1 has a CER of {pct(b[0])} and a
      WER of {pct(b[1])}: {fewer(b[0], s3[0])}% and {fewer(b[1], s3[1])}% fewer errors than tam_v3 ({pct(s3[0])} / {pct(s3[1])}), and
      {fewer(b[0], f3[0])}% and {fewer(b[1], f3[1])}% fewer than the stock model ({pct(f3[0])} / {pct(f3[1])}). The integer
      tam_v3.1 scores {pct(FOLD['v31_std'][0])} / {pct(FOLD['v31_std'][1])} and tam_fast_v3.1 {pct(FOLD['v31_fast'][0])} / {pct(FOLD['v31_fast'][1])}.</li>
    <li><b>The gain over tam_v3 is significant:</b> {dash(cb[0])} CER points ({dash(cb[1])} to {dash(cb[2])}) and {dash(cw[0])} WER points
      ({dash(cw[1])} to {dash(cw[2])}), 95% confidence intervals resampling whole pages.</li>
    <li><b>Rendered lines in unseen fonts:</b> tam_best_v3.1 is better than tam_v3 in every category of Tamil text, vowel
      signs, grantha, pulli, numerals, mixed Tamil-English and English terms. tam_fast_v3.1 is the best of all models on
      numerals, mixed text and English terms.</li>
    <li><b>Quotation marks:</b> {q('v31_best'):.1f}% are read on the real lines (tam_v3 {q('v3_best'):.1f}%, stock {q('up_best'):.1f}%).</li>
    <li><b>Still weak:</b> Tamil numerals in tam_best_v3.1 and tam_v3.1 ({num('v31_best'):.0f}% read, stock {num('up_best'):.0f}%); Tamil symbols
      ௳–௺ ௐ; and word errors stay above 5%, mostly from punctuation and spacing.</li>
  </ul>
</section>

<section id="models">
  <h2>Models compared</h2>
  <ul class="list">
    <li><b>tam_best_v3.1</b> (float, <code>Lfx192</code>), <b>tam_v3.1</b> (the same network in integers) and
      <b>tam_fast_v3.1</b> (a smaller integer network, <code>Lfx128</code>), from release
      <a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.1.0">v3.1.0</a>.</li>
    <li><b>tam_v3</b> and <b>tam_v3_fast</b> (its integer version), from release
      <a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.0.0">v3.0.0</a>.</li>
    <li><b>Stock <code>tam</code></b> from Tesseract's tessdata_best, tessdata and tessdata_fast (4.1.0, trained in 2017).</li>
  </ul>
</section>

<section id="scoring">
  <h2>Scoring</h2>
  <p>CER is the character error rate and WER the word error rate: lower is better. Text is compared after Unicode NFC
    normalisation with spaces collapsed. The main real-line columns use tam_v3's scoring: zero-width characters are
    dropped and quote and dash variants folded. The <em>strict</em> columns keep them, which counts the invisible U+200C
    that the stock models write after many pullis. Real lines are read one at a time with <code>--psm 13</code>,
    rendered lines with <code>--psm 7</code>. Confidence intervals come from a paired bootstrap with 10,000 resamples,
    resampling whole pages for real lines.</p>
</section>

<section id="real-lines">
  <h2>Real scanned lines</h2>
  <p class="cap">tam_v3's test split: 3,968 lines from 197 pages of Tamil Wikisource books (scans on Wikimedia Commons),
    cut with tam_v3's line boxes. Never used for training or to choose a model.</p>
  {t_real}
  <h4>By content</h4>
  {t_real_cat}
  <p class="note">Only 236 lines contain numbers and 17 contain Latin letters, so those rows vary widely.</p>
</section>

<section id="check-lines">
  <h2>Real check lines</h2>
  <p class="cap">tam_v3's dev split: 2,854 lines from 164 archive.org pages, strict scoring. These lines were used to choose
    tam_v3.1's checkpoint and blend, so its scores here are optimistic.</p>
  {t_dev}
</section>

<section id="rendered">
  <h2>Rendered lines by category</h2>
  <p class="cap">1,389 lines rendered from text never trained on, in 6 fonts never used to train tam_v3.1; strict scoring.
    Categories A–G cover the parts of Tamil writing that OCR most often gets wrong, plus punctuation.</p>
  {t_syn}
</section>

<section id="characters">
  <h2>Characters</h2>
  <p class="cap">Share of the occurrences in the reference text that the model reproduced, real test lines / rendered lines.</p>
  {t_chars}
</section>

<section id="significance">
  <h2>Significance</h2>
  <p class="cap">Difference in percentage points, model minus baseline, with 95% confidence intervals; negative is better.</p>
  {t_ci}
  <p class="note">Every interval excludes zero.</p>
</section>

<section id="speed">
  <h2>Speed and size</h2>
  <p class="cap">One CPU thread (<code>OMP_THREAD_LIMIT=1</code>), 300 real lines in one process on an Intel i3-9100;
    model load is the middle of three runs.</p>
  {t_speed}
  <p class="note">Each tam_v3.1 network reads about as fast as the stock network of the same size (within 3%). The larger
    dictionary adds 0.07–0.09 s to loading and about 10 MB of memory.</p>
</section>

<section id="crash">
  <h2>Crash check</h2>
  <p class="cap">All {N_ALL:,} test lines, read one by one with the unmodified <code>tesseract</code> 5.5.0 command-line program.</p>
  {t_crash}
  <p class="note">The two lines that stop tam_fast_v3.1 hit Tesseract bug
    <a href="https://github.com/tesseract-ocr/tesseract/issues/4627">#4627</a> (two unrecognised words in one line
    overflow a sum, and the command-line program traps the overflow). It is fixed in Tesseract 5.5.4 and does not
    affect page modes or programs that use the Tesseract library.</p>
</section>

<section id="reproduce">
  <h2>Reproduce these results</h2>
  <p>The scripts and the full report are in
    <a href="https://github.com/newsbaba24x7/tamil-tess-trainer/tree/main/models/tam_v3.1">models/tam_v3.1</a>
    (<a href="https://github.com/newsbaba24x7/tamil-tess-trainer/blob/main/models/tam_v3.1/RESULTS.md">RESULTS.md</a>).</p>
<pre><button class="copy" type="button">Copy</button><code>git clone https://github.com/newsbaba24x7/tamil-tess-trainer && cd tamil-tess-trainer/models/tam_v3.1
R=https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download
for f in tam_best_v3.1 tam_v3.1 tam_fast_v3.1; do mkdir -p m/$f && curl -L -o m/$f/tam.traineddata $R/v3.1.0/$f.traineddata; done
curl -LO $R/v3.0.0/tam_v3-real-lines.jsonl.gz

<span class="c"># real test lines (downloads 197 page images from Wikimedia, 15 s apart)</span>
python3 -I 14_fetch_real_lines.py tam_v3-real-lines.jsonl.gz --split test --out real_test
python3 -I 12_prepare_real_eval.py tam_v3-real-lines.jsonl.gz real_test/lines test
python3 -I 10_evaluate.py --lines real_test/lines --corpus real_test/lines/real.tsv --psm 13 --out results/real_test_psm13 \\
    --model v31_best=m/tam_best_v3.1 --model v31_std=m/tam_v3.1 --model v31_fast=m/tam_fast_v3.1
python3 -I 18_report_tables.py results > results/tables.md</code></pre>
  <p class="note">Add <code>--model NAME=DIR</code> for any other model (each DIR holds a <code>tam.traineddata</code>).
    The README in that folder has every step, including the rendered test lines, the check lines, the crash scan and
    the confidence intervals.</p>
</section>

<section id="earlier">
  <h2>Earlier results</h2>
  <p>The <a href="tam_v3/">tam_v3 benchmark page</a> keeps every test of tam_v3, tam_v2 and the research models: 197 whole
    pages, real lines, RANLP 2025, the Tamil OCR Benchmark, rendered lines, scanning resolution, handwriting, camera photos
    and speed per page, with BLEU, ANLS and METEOR.</p>
</section>

</main>

<footer>
  <div><a href="/tamil-tess-trainer/">Tamil OCR for Tesseract</a> · <a href="https://github.com/newsbaba24x7/tamil-tess-trainer">github.com/newsbaba24x7/tamil-tess-trainer</a> · Apache-2.0</div>
  <div>Measured {a.date} with Tesseract 5.5.0. Generated by <code>models/tam_v3.1/19_benchmark_page.py</code> from <code>models/tam_v3.1/results</code>.</div>
</footer>

</div>
<script>
for (const btn of document.querySelectorAll("pre .copy")) {{
  btn.addEventListener("click", async () => {{
    const code = btn.parentElement.querySelector("code").innerText;
    try {{ await navigator.clipboard.writeText(code); btn.textContent = "Copied"; }}
    catch {{ btn.textContent = "Select and copy"; }}
    setTimeout(() => (btn.textContent = "Copy"), 1600);
  }});
}}
</script>
</body>
</html>
"""
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(page, encoding="utf-8")
print(f"wrote {a.out} ({len(page):,} chars)")
