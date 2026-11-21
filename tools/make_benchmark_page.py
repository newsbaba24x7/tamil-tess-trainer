#!/usr/bin/env python3
"""Build the benchmark results page (docs/benchmarks/index.html) from evaluation reports.

Every number on the page comes from the JSON reports that `tamtrain lines` and `tamtrain scans`
write, so the page can be rebuilt after new runs (maintainers only; the reports are not published):

    python3 tools/make_benchmark_page.py --reports work-v2/report \\
        --extra-reports work-v3/report work-v3/report-extra work-anuvaad/report \\
        --new-reports work-bench-extra/report work-anuvaad-extra/report \\
        --res-reports work-resolution/report --date "17–21 November 2026"

--extra-reports add the models a report in --reports does not have (for example a newer model,
scored later against the same test sets). --new-reports hold the handwriting, camera-photo and
cover tests, which were run with the stock models, the Anuvaad model and tam_v3 only, and the speed
timings; --res-reports the scanning-resolution ladders (tools/make_dpi_set.py). The page reuses the stylesheet of docs/index.html, so
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
from tamtrain.metrics import similarity  # noqa: E402
from tamtrain.scans import levenshtein, prepare  # noqa: E402

ORDER = ["start (tam, best)", "installed tam", "Anuvaad tam", "V1 (188 styles)", "V2-research", "tam_v2 (best)",
         "tam_v2 (fast)", "tam_v3 (best)", "tam_v3 (fast)"]
NAME = {"start (tam, best)": "Stock <code>tam</code> (tessdata_best 4.1.0)",
        "installed tam": "Stock <code>tam</code> (tessdata_fast 4.1.0, Ubuntu package)",
        "Anuvaad tam": "Anuvaad <code>tam</code> <span class=\"small muted\">third party</span>",
        "V1 (188 styles)": "V1 <span class=\"small muted\">tam_multifont</span>",
        "V2-research": "V2-research <span class=\"small muted\">tam_v2_research</span>",
        "tam_v2 (best)": "tam_v2", "tam_v2 (fast)": "tam_v2_fast",
        "tam_v3 (best)": "tam_v3", "tam_v3 (fast)": "tam_v3_fast"}
OURS = "tam_v3 (best)"
# Labels never taken from --extra-reports: in the reports of 18 November 2026 "installed tam" was
# tam_v2, because this machine's packaged tam.traineddata had been replaced by it. Only the
# reports of 17 November have the real Ubuntu package model.
NOT_FROM_EXTRA = {"installed tam"}
PAPER = [("Google Document AI (commercial), paper", 0.78, 11.98, 0.5803, 0.9923, 0.8762),
         ("Google Cloud Vision API (commercial), paper", 0.79, 12.04, 0.5790, 0.9922, 0.8751),
         ("Tesseract 5.5.0, paper", 7.80, 61.45, 0.0493, 0.9264, 0.3201),
         ("EasyOCR, paper", 11.72, 28.76, 0.3461, 0.8828, 0.6744),
         ("Surya, paper", 13.92, 65.00, 0.1487, 0.8672, 0.3359)]
# Speed and memory (seconds per page and peak memory on one thread, the same 8 real pages, every model
# timed together on 21 November 2026) are read from speed.json in --new-reports.

# Tests added on 21 November 2026 (handwriting, camera photos, covers and posters) were run with the stock
# models, the Anuvaad model and tam_v3 only. Their reports sit in the --new-reports folders: the
# `tamtrain lines` reports, covers-posters.json from tools/score_covers.py and covers-posters-passes.json.
SHORT = {"start (tam, best)": "Stock tam, best", "installed tam": "Stock tam, Ubuntu fast", "Anuvaad tam": "Anuvaad tam",
         "tam_v3 (best)": "tam_v3", "tam_v3 (fast)": "tam_v3_fast"}
PLAIN = {"start (tam, best)": "the stock model (tessdata_best)", "installed tam": "the stock model of the Ubuntu package",
         "Anuvaad tam": "the Anuvaad model", "V1 (188 styles)": "V1", "V2-research": "V2-research", "tam_v2 (best)": "tam_v2",
         "tam_v2 (fast)": "tam_v2_fast", "tam_v3 (best)": "tam_v3", "tam_v3 (fast)": "tam_v3_fast"}
COVER_KEY = {"start (tam, best)": "stock tam best", "installed tam": "stock tam",
             "tam_v3 (best)": "tam_v3", "tam_v3 (fast)": "tam_v3 fast"}
KINDS = {"newspapers": "Newspapers", "book-contents-or-covers": "Book pages and covers", "papers": "Papers",
         "trade-documents": "Trade documents", "notes": "Handwritten notes", "contracts": "Contracts",
         "whiteboard-blackboard": "Whiteboards and blackboards", "bills": "Bills", "identity-cards": "Identity cards",
         "badges-and-passes": "Badges and passes", "forms": "Forms"}
COVER_KINDS = {"kind: book": "Book covers", "kind: magazine": "Magazine covers", "kind: poster": "Film posters"}


def row_best_table(first: str, models: list[str], rows: list[tuple[str, dict]], better: str, fmt) -> str:
    """One row per group, one column per model; the best model in each row is marked."""
    out = ['<div class="table-wrap"><table>', f"<thead><tr><th>{first}</th>" + "".join(
        f'<th class="n m">{html.escape(SHORT[m])}</th>' for m in models) + "</tr></thead><tbody>"]
    for label, vals in rows:
        have = [v for v in vals.values() if v is not None]
        best = (min(have) if better == "low" else max(have)) if have else None
        tds = "".join(f'<td class="n">{"<b class=\"best\">" + fmt(vals[m]) + "</b>" if vals[m] == best else fmt(vals[m])}</td>'
                      for m in models)
        out.append(f"<tr><td>{label}</td>{tds}</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def model_table(rep: dict, cols: list[tuple[str, str, object, str]]) -> str:
    """One row per model from a `tamtrain lines` report; cols: (heading, key, format, 'low'/'high')."""
    rows = []
    for m in [m for m in ORDER if m in rep["models"]]:
        x = rep["models"][m]["groups"]["all"]
        rows.append(("ours" if m == OURS else "", NAME[m], [(x[k], f(x[k])) for _, k, f, _ in cols]))
    return table([("Model", False)] + [(h, True) for h, *_ in cols], rows, [b for *_, b in cols])


def p1(x: float) -> str:
    return "–" if x is None else f"{x:.1f}%"


def fast_gain(speed: dict) -> str:
    s = speed["models"]
    return f"{round(100 * (1 - s['tam_v3 (fast)']['sec_per_page'] / s['tam_v3 (best)']['sec_per_page']))}%"


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


def tob_split(reports: Path, extra: list[Path], models: list[str]) -> dict:
    """Tamil OCR Benchmark: CER on Tamil letters only and on English (Latin) letters only, per model,
    from the saved OCR text (same label rules as the reports)."""
    ocr, truth = {}, None
    for i, d in enumerate([reports] + extra):
        f = d / "tamil-ocr-benchmark.ocr.json"
        if not f.exists():
            continue
        x = json.loads(f.read_text(encoding="utf-8"))
        truth = truth or x["truth"]
        for m, v in x["models"].items():
            if m in models and m not in ocr and not (i and m in NOT_FROM_EXTRA):
                ocr[m] = v
    def keep(s: str, tamil: bool) -> str:
        if tamil:
            return "".join(c for c in s if "஀" <= c <= "௿")
        return "".join(c for c in s if c.isascii() and c.isalpha())
    out = {"latin_lines": sum(any(c.isascii() and c.isalpha() for c in t) for t in truth.values())}
    for m, o in ocr.items():
        r = {}
        for tamil in (True, False):
            e = n = 0
            for k, t in truth.items():
                a, b = keep(t, tamil), keep(o[k], tamil)
                e, n = e + levenshtein(a, b), n + len(a)
            r["tamil" if tamil else "latin"], r["n_tamil" if tamil else "n_latin"] = 100 * e / n, n
        out[m] = r
    return out


RES_LEVELS = ["300", "200", "150", "100", "072"]
RES_MEASURES = [("cer", "CER by resolution", pct, "low"), ("wer", "WER by resolution", pct, "low")]
RES_OTHER = [("bleu", "BLEU"), ("anls", "ANLS"), ("meteor", "METEOR")]   # shown as scanned and at 72 DPI only


def res_load(res: Path, name: str) -> dict:
    return json.loads((res / f"{name}.json").read_text(encoding="utf-8"))


def page_set_measures(levels: dict, ids: list[str], truth: dict, models: list[str]) -> dict:
    """CER and WER pooled over the pages; BLEU, ANLS and METEOR per page (the whole page as one text),
    averaged over the pages. Every level is scored on the same pages."""
    out = {}
    for lv, rep in levels.items():
        out[lv] = {}
        for m in models:
            ocr = [rep["per_page"][i][m]["ocr"] for i in ids]
            gts = [truth[i] for i in ids]
            ce = sum(levenshtein(g, o) for g, o in zip(gts, ocr))
            we = sum(levenshtein(g.split(), o.split()) for g, o in zip(gts, ocr))
            out[lv][m] = {"cer": 100 * ce / sum(map(len, gts)), "wer": 100 * we / sum(len(g.split()) for g in gts),
                          **similarity(gts, ocr)}
    return out


def build(reports: Path, extra: list[Path], new: list[Path], pages_dir: Path, date: str, res: Path,
          res_old_dir: Path, with_covers: bool = True) -> str:
    def load(n: str) -> dict:
        rep = json.loads((reports / f"{n}.json").read_text(encoding="utf-8"))
        for d in extra:
            f = d / f"{n}.json"
            if not f.exists():
                continue
            more = json.loads(f.read_text(encoding="utf-8"))
            for m in ORDER:
                if m in NOT_FROM_EXTRA:
                    continue
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
    r13 = res_load(res, "rendered-heldout-psm13")
    assert r13["lines"] == rendered["lines"]
    rows = []
    for m in [m for m in ORDER if m in rendered["models"] and m in r13["models"]]:
        x, y = rendered["models"][m]["groups"]["all"], r13["models"][m]["groups"]["all"]
        rows.append(("ours" if m == OURS else "", NAME[m], [(x["cer"], pct(x["cer"])), (x["wer"], pct(x["wer"])),
                                                           (y["cer"], pct(y["cer"])), (y["wer"], pct(y["wer"]))]))
    rendered_tbl = table([("Model", False), ("psm 7: CER", True), ("WER", True), ("psm 13: CER", True), ("WER", True)],
                         rows, ["low"] * 4)
    r13_ours = r13["models"][OURS]["groups"]
    # where tam_v3 still errs on rendered lines: lines returned empty, and the held-out font families
    ro = json.loads(next(d / "rendered-heldout.ocr.json" for d in [reports] + extra
                         if (d / "rendered-heldout.ocr.json").exists() and OURS in json.loads(
                             (d / "rendered-heldout.ocr.json").read_text(encoding="utf-8"))["models"]).read_text(encoding="utf-8"))
    e_all = e_empty = n_rest = e_rest = n_empty = 0
    for k, t in ro["truth"].items():
        t2, o2 = prepare(t), prepare(ro["models"][OURS][k])
        e = levenshtein(t2, o2)
        e_all += e
        if o2.strip():
            e_rest, n_rest = e_rest + e, n_rest + len(t2)
        else:
            e_empty, n_empty = e_empty + e, n_empty + 1
    rg = {m: rendered["models"][m]["groups"] for m in ORDER if m in rendered["models"]}
    held = rg[OURS]["held-out font"]
    rendered_note = (
        f'tam_v3 can still improve a lot here, and part of the gain needs no new model. With <code>--psm 7</code>, '
        f'{round(100 * e_empty / e_all)}% of its errors come from {n_empty} lines it returns empty, as every model does on '
        f'nearly the same lines: very thin letters or heavy damage, where Tesseract\'s own line check finds no text line. '
        f'<code>--psm 13</code> (raw line) skips that check and reads them, which brings tam_v3 to '
        f'{pct(r13_ours["all"]["cer"])}; the real-line tests on this page all use <code>--psm 13</code>. The rest is the '
        f'model\'s: on the lines it does read with <code>--psm 7</code> its CER is {pct(100 * e_rest / n_rest)}, and in the '
        f'three font families no model was trained on ({held["lines"]} lines) it is {pct(r13_ours["held-out font"]["cer"])} '
        f'with <code>--psm 13</code>. Rendered lines are easier than real scans, and a model can improve here without '
        f'improving on real pages, as V1 did. tam_v3\'s rendering text includes the books this set\'s text was drawn from, '
        f'so for tam_v3 only the three held-out font families are fully unseen.')

    # scanning resolution: the same pages as scanned and at each resolution of the ladder
    res_sets = []
    for key, title, src_rep, gt_dir in (
            ("real", "All test pages", scans, pages_dir),
            ("old", "Old books, published before 1960", res_load(res, "old-books-source"), res_old_dir)):
        levels = {"As scanned": src_rep}
        for d in RES_LEVELS:
            levels[f"{int(d)} DPI"] = res_load(res, f"{'real-pages' if key == 'real' else 'old-books'}-{d}")
        skip = set(src_rep["excluded"]) | {p for r in levels.values() for p in r.get("crashed", [])}
        ids = sorted(set.intersection(*(set(r["per_page"]) for r in levels.values())) - skip)
        truth = {i: prepare((gt_dir / f"{i}.gt.txt").read_text(encoding="utf-8")) for i in ids}
        models = [m for m in ORDER if all(m in r["models"] for r in levels.values())]
        res_sets.append((key, title, ids, levels, models, page_set_measures(levels, ids, truth, models)))
    res_tbls = []
    for key, title, ids, levels, models, meas in res_sets:
        blocks = []
        for mk, label, fmt, better in RES_MEASURES:
            rows = [("ours" if m == OURS else "", NAME[m], [(round(meas[lv][m][mk], 4), fmt(meas[lv][m][mk])) for lv in levels])
                    for m in models]
            blocks.append(f'<h4>{label} <span class="muted small">lower is better</span></h4>\n'
                          + table([("Model", False)] + [(lv, True) for lv in levels], rows, [better] * len(levels)))
        ends = ["As scanned", "72 DPI"]
        rows = [("ours" if m == OURS else "", NAME[m], [(round(meas[lv][m][k], 4), num(meas[lv][m][k])) for lv in ends
                                                        for k, _ in RES_OTHER]) for m in models]
        head = [("Model", False)] + [(f"{lv}: {n}" if i == 0 else n, True) for lv in ends for i, (_, n) in enumerate(RES_OTHER)]
        blocks.append('<h4>BLEU, ANLS and METEOR, as scanned and at 72 DPI <span class="muted small">higher is better</span></h4>\n'
                      + table(head, rows, ["high"] * (len(ends) * len(RES_OTHER))))
        res_tbls.append(f'<h3 id="resolution-{key}">{title} ({len(ids)} pages)</h3>\n' + "\n".join(blocks))
    # notes: tam_v3 at each level, the lowest resolution that keeps its accuracy, the best model at 72 DPI
    def cers(meas: dict, m: str) -> list[float]:
        return [meas[lv][m]["cer"] for lv in meas]
    lvls = list(res_sets[0][3])
    keep = None
    for i in range(len(lvls) - 1, 0, -1):     # lowest level whose CER is within 10% (relative) of as scanned, on both sets
        if all(cers(x[5], OURS)[i] <= 1.1 * cers(x[5], OURS)[0] for x in res_sets):
            keep = lvls[i]
            break
    def at(x, lv: str, m: str) -> str:
        return pct(x[5][lv][m]["cer"])
    real, old = res_sets
    best72 = {x[0]: min(x[4], key=lambda m: x[5]["72 DPI"][m]["cer"]) for x in res_sets}
    res_note = (
        f'tam_v3\'s CER on the real pages: {at(real, "As scanned", OURS)} as scanned, '
        + ", ".join(f'{at(real, lv, OURS)} at {lv}' for lv in lvls[1:]) +
        f'. On the old books: {at(old, "As scanned", OURS)} as scanned, '
        + ", ".join(f'{at(old, lv, OURS)} at {lv}' for lv in lvls[1:]) + ". "
        + (f'Down to {keep} its errors stay within a tenth of the as-scanned figure on both sets; below that they rise '
           f'steeply for every model. ' if keep else "")
        + " ".join(f'At 72 DPI the most accurate model on the {"real pages" if k == "real" else "old books"} is '
                   f'{PLAIN.get(m, m)}, at {at(real if k == "real" else old, "72 DPI", m)}.'
                   for k, m in best72.items()))
    res_summary = (
        f'    <li><b>Scanning resolution:</b> '
        + (f'tam_v3 keeps its accuracy down to {keep} (for 12-pt text); below that every model\'s errors rise steeply: '
           if keep else "every model's errors rise as the resolution falls: ")
        + f'at 72 DPI tam_v3\'s CER is {at(real, "72 DPI", OURS)} on the real pages and {at(old, "72 DPI", OURS)} on old '
          f'books (stock: {at(real, "72 DPI", "start (tam, best)")} and {at(old, "72 DPI", "start (tam, best)")})'
        + (', so at that resolution the stock model is the better choice' if all(
            x[5]["72 DPI"]["start (tam, best)"]["cer"] < x[5]["72 DPI"][OURS]["cer"] for x in res_sets) else '')
        + '. tam_v3 was trained on scans at normal resolution; very small text is its weak spot.</li>')

    # handwriting, camera photos, covers and posters (stock models, Anuvaad and tam_v3 only); a report
    # name may sit in several --new-reports folders, each with other models: they are merged
    def load_new(n: str) -> dict:
        rep = None
        for d in new:
            f = d / f"{n}.json"
            if f.exists():
                x = json.loads(f.read_text(encoding="utf-8"))
                if rep is None:
                    rep = x
                else:
                    assert x["lines"] == rep["lines"], n
                    for m, v in x["models"].items():
                        rep["models"].setdefault(m, v)
        return rep
    speed = load_new("speed")
    speed_tbl = table([("Model", False), ("Seconds per page", True), ("Peak memory", True), ("File size", True)],
                      [("ours" if m == OURS else "", NAME[m], [(x["sec_per_page"], f"{x['sec_per_page']:.2f}"),
                                                               (x["peak_mb"], f"{x['peak_mb']} MB"), (None, f"{x['file_mb']:.1f} MB")])
                       for m in ORDER if (x := speed["models"].get(m))], ["low", "low", None])
    hw_words, hw_lines = load_new("iiit-hw-test-words"), load_new("iiit-hw-test-lines")
    appen = load_new("appen-photo-lines-psm13")
    covers, passes = load_new("covers-posters"), load_new("covers-posters-passes")
    cer, wer, anls = ("CER", "cer", pct, "low"), ("WER", "wer", pct, "low"), ("ANLS", "anls", num, "high")
    hw_words_tbl = model_table(hw_words, [cer, ("Words read exactly", "exact_lines", pct, "high"), anls])
    line_cols = [cer, wer, ("Lines read exactly", "exact_lines", pct, "high"), anls]
    hw_lines_tbl = model_table(hw_lines, [cer, wer, anls])  # no model reads a whole joined line exactly
    appen_tbl = model_table(appen, line_cols)
    hw_cers = [r["models"][m]["groups"]["all"]["cer"] for r in (hw_words, hw_lines) for m in r["models"]]
    best_exact = max(x["groups"]["all"]["exact_lines"] for x in hw_words["models"].values())
    min_wer = min(x["groups"]["all"]["wer"] for x in hw_lines["models"].values())
    ag = appen["models"][OURS]["groups"]
    S0, A0 = "start (tam, best)", "Anuvaad tam"
    assert all(appen["models"][m]["groups"][g]["cer"] > 100 / 3 for m in appen["models"] for g in ("notes", "whiteboard-blackboard"))
    assert min(hw_cers) > 40 and best_exact < 10 and min_wer > 100
    def kinds(g: str) -> str:
        return ", ".join(f"{n} {pct(appen['models'][m]['groups'][g]['cer'])}" for n, m in (("stock", S0), ("Anuvaad", A0)))
    hw_reasons = f"""  <ul class="list">
    <li><b>Most letters come out wrong.</b> In the camera-photo test below, on phone photos of handwritten notes tam_v3
      gets {pct(ag["notes"]["cer"])} of the letters wrong ({kinds("notes")}), and on whiteboards and blackboards
      {pct(ag["whiteboard-blackboard"]["cer"])} ({kinds("whiteboard-blackboard")}): more than one letter in three, whichever
      model reads them.
      Text like that takes longer to correct than to type again.</li>
    <li><b>They learnt printed letters only.</b> Every model here was trained on printed fonts, and tam_v3 also on scanned
      printed books; the Anuvaad model's training data is not published. Handwritten letters change from writer to writer
      (slant, joined or broken strokes, uneven sizes, loops), and the models never saw those shapes. Even on clean,
      cut-out handwritten words and lines (the tests below) the character error rate is
      {min(hw_cers):.0f}–{max(hw_cers):.0f}%, and the best model reads only {best_exact:.1f}% of words exactly.</li>
    <li><b>A photo adds what the models were not trained for.</b> They learnt from flat, evenly lit scans. A phone photo
      adds blur, shadows, uneven light, an angled view, paper texture and ruled lines, which make the thin, uneven strokes of
      handwriting harder still to separate from the background.</li>
    <li><b>Lines are hard to find.</b> On a whole photo Tesseract must first find the lines of text, and handwritten lines
      slope, touch and run into each other. The tests on this page cut the lines out first, so a whole photo reads worse.</li>
    <li><b>Words get split.</b> The gaps in handwriting are uneven, so the models put spaces inside words: on handwritten
      lines every model writes more words than the lines have (word error rate {min_wer:.0f}% or more).</li>
  </ul>
  <p class="note">Reading handwriting would need a Tesseract model trained on handwritten Tamil lines.</p>"""

    # Tamil OCR Benchmark: where the errors are (Tamil letters or English letters)
    tob_models = [m for m in ORDER if m in tob["models"]]
    split = tob_split(reports, extra, tob_models)
    tob_split_tbl = table([("Model", False), (f"Tamil letters only ({split[OURS]['n_tamil']:,}): CER", True),
                           (f"English letters only ({split[OURS]['n_latin']:,}): CER", True)],
                          [("ours" if m == OURS else "", NAME[m], [(round(split[m]["tamil"], 2), pct(split[m]["tamil"])),
                                                                   (round(split[m]["latin"], 2), pct(split[m]["latin"]))])
                           for m in tob_models], ["low", "low"])
    A = "Anuvaad tam"
    anuvaad_what = (
        'Tamil Tesseract model from Project Anuvaad (EkStep Foundation and Tarento), an open document-translation platform '
        'for Indian languages whose other models are made for court judgments. Trained for Tamil and English: its '
        'character set has the full English alphabet beside the Tamil letters. Its strength is English words inside Tamil '
        'text. No dictionary; its training data is not documented.')
    assert split[A]["latin"] < 5 < 20 < split[OURS]["latin"] and abs(split[A]["tamil"] - split[OURS]["tamil"]) < 0.1
    assert all(split[m]["latin"] == 100 for m in ("start (tam, best)", "installed tam", "V1 (188 styles)", "V2-research"))
    tob_note = (
        f'Anuvaad <code>tam</code> leads here because it reads the English words: on the {split[OURS]["n_latin"]:,} English '
        f'letters (in {split["latin_lines"]} of the 200 lines) it gets {pct(split[A]["latin"])} wrong, against '
        f'{pct(split[OURS]["latin"])} for tam_v3. The stock model cannot write English at all: its character set has no '
        f'Latin letters, so it turns English words into Tamil letters and digits, and so do V1 and V2-research, which kept '
        f'that character set; tam_v2 and tam_v3 added Latin letters. On the Tamil letters alone, Anuvaad and tam_v3 are almost equal '
        f'({pct(split[A]["tamil"])} and {pct(split[OURS]["tamil"])}). The lines are clean renders in a single font, Noto Sans '
        f'Tamil, which is also among the training fonts of our models, so the test says little about real scans, where '
        f'Anuvaad is weaker than the stock model.')
    nm = [m for m in ORDER if m in appen["models"]]
    kinds = sorted((g for g in appen["models"][OURS]["groups"] if g != "all"),
                   key=lambda g: -appen["models"][OURS]["groups"][g]["lines"])
    appen_kinds_tbl = row_best_table("Document type (lines)", nm, [
        (f"{KINDS.get(g, g)} ({appen['models'][OURS]['groups'][g]['lines']:,})",
         {m: appen["models"][m]["groups"][g]["cer"] for m in nm}) for g in kinds], "low", pct)

    cm = [m for m in ORDER if m in COVER_KEY]
    cg = covers["groups"]
    def cv(g: str, m: str, psm: int) -> dict:
        return cg[g][f"{COVER_KEY[m]}, psm {psm}"]
    rows = []
    for m in cm:
        a, b = cv("all", m, 3), cv("all", m, 11)
        n_titles = round(b["titles_read"] * b["titles"] / 100)
        rows.append(("ours" if m == OURS else "", NAME[m], [
            (a["words_found"], p1(a["words_found"])), (a["precision"], p1(a["precision"])),
            (b["words_found"], p1(b["words_found"])), (b["precision"], p1(b["precision"])),
            (b["tamil_found"], p1(b["tamil_found"])), (n_titles, f"{n_titles} of {b['titles']}")]))
    covers_tbl = table([("Model", False), ("psm 3: words found", True), ("precision", True), ("psm 11: words found", True),
                        ("precision", True), ("Tamil words found, psm 11", True), ("Titles read, psm 11", True)],
                       rows, ["high"] * 6)
    def group_rows(keys: list[str], label) -> list:
        return [(label(g, cv(g, OURS, 11)), {m: cv(g, m, 11)["words_found"] for m in cm}) for g in keys]
    covers_kind_tbl = row_best_table("Kind (images, words)", cm, group_rows(
        [g for g in COVER_KINDS if g in cg], lambda g, x: f"{COVER_KINDS[g]} ({x['images']}, {x['truth_words']:,})"), "high", p1)
    decades = sorted((g for g in cg if g.startswith("decade: ")), key=lambda g: (g == "decade: unknown", g))
    covers_decade_tbl = row_best_table("Decade (images, words)", cm, group_rows(
        decades, lambda g, x: f"{'Year unknown' if g.endswith('unknown') else g[8:]} ({x['images']}, {x['truth_words']:,})"),
        "high", p1)
    pm = [m for m in ORDER if m in passes["runs"][0]["models"]]
    head = [("Run", False)]
    for m in pm:
        head += [(f"{SHORT[m]}: words found", True), ("precision", True)]
    passes_tbl = table(head, [("", html.escape(r["run"]), [c for m in pm for c in (
        (r["models"][m]["found"], p1(r["models"][m]["found"])), (r["models"][m]["precision"], p1(r["models"][m]["precision"])))])
        for r in passes["runs"]], ["high"] * (2 * len(pm)))

    # summary sentences; the asserts stop a rebuild whose numbers no longer fit the words
    S = "start (tam, best)"
    def a(rep: dict, m: str, g: str = "all") -> float:
        return rep["models"][m]["groups"][g]["cer"]
    assert all(a(r, OURS) < min(a(r, S), a(r, A)) for r in (hw_words, hw_lines, appen))
    printed = ("trade-documents", "book-contents-or-covers", "papers")
    assert max(a(appen, OURS, g) for g in printed) < 3 < 30 < min(a(appen, OURS, g) for g in ("notes", "whiteboard-blackboard"))
    c3, cs = cv("all", OURS, 11), cv("all", S, 11)
    t3, ts = (round(x["titles_read"] * x["titles"] / 100) for x in (c3, cs))
    assert c3["words_found"] > cs["words_found"] and t3 > ts
    r1, r4 = passes["runs"][1]["models"], passes["runs"][-1]["models"]
    new_summary = (
        f'    <li><b>Handwriting:</b> no model here was trained on it, and all read it poorly, but tam_v3 makes the fewest '
        f'character errors on both handwriting tests: CER {pct(a(hw_words, OURS))} on handwritten words (stock '
        f'{pct(a(hw_words, S))}, Anuvaad {pct(a(hw_words, A))}) and {pct(a(hw_lines, OURS))} on handwritten lines (stock '
        f'{pct(a(hw_lines, S))}, Anuvaad {pct(a(hw_lines, A))}).</li>\n'
        f'    <li><b>Camera photos of documents:</b> on {appen["lines"]:,} lines from 55 phone photos tam_v3\'s CER is '
        f'{pct(a(appen, OURS))}, against {pct(a(appen, S))} for the stock model and {pct(a(appen, A))} for Anuvaad. Printed '
        f'documents read well (trade documents, book pages and papers under 3%); handwritten notes and whiteboards do not.</li>\n'
        f'<!--COVERS-->    <li><b>Covers and posters are the hardest test.</b> On whole images, in sparse-text mode (<code>--psm 11</code>), '
        f'tam_v3 finds {p1(c3["words_found"])} of the words against {p1(cs["words_found"])} for the stock model, and reads '
        f'{t3} of {c3["titles"]} main titles (stock: {ts}). Tesseract\'s default page mode finds no text at all on '
        f'{min(passes["psm3_empty"].values())}–{max(passes["psm3_empty"].values())} of the {passes["images"]} images. '
        f'Reading each image in four <code>--psm 11</code> passes raises tam_v3\'s share to {p1(r4[OURS]["found"])}.</li><!--/COVERS-->')
    passes_note = (
        f'Four passes together find {p1(r4[OURS]["found"])} of the words with tam_v3 ({p1(r4[S]["found"])} with the stock '
        f'model), against {p1(r1[OURS]["found"])} ({p1(r1[S]["found"])}) for one pass on the image as is, at the cost of more '
        f'picture noise read as text. On covers, how Tesseract is run changes the result more than the choice of model.')

    n_lines = (test_lines["lines"] + dev_lines["lines"] + ranlp["lines"] + tob["lines"] + rendered["lines"]
               + hw_lines["lines"] + appen["lines"])
    tpl = TEMPLATE
    for key, val in {"STYLE": style, "DATE": date, "PAGES_TBL": pages_tbl, "BANDS_TBL": bands_tbl,
                     "HW_WORDS_TBL": hw_words_tbl, "HW_LINES_TBL": hw_lines_tbl, "TOB_SPLIT_TBL": tob_split_tbl,
                     "TOB_NOTE": tob_note, "HW_REASONS": hw_reasons, "ANUVAAD_WHAT": anuvaad_what, "RENDERED_NOTE": rendered_note,
                     "APPEN_TBL": appen_tbl, "APPEN_KINDS_TBL": appen_kinds_tbl, "COVERS_TBL": covers_tbl,
                     "COVERS_KIND_TBL": covers_kind_tbl, "COVERS_DECADE_TBL": covers_decade_tbl, "PASSES_TBL": passes_tbl,
                     "N_HW_WORDS": f"{hw_words['lines']:,}", "N_HW_LINES": f"{hw_lines['lines']:,}",
                     "N_APPEN": f"{appen['lines']:,}", "ANUVAAD_SEC": f"{speed['models'][A]['sec_per_page']:.1f}",
                     "N_COVERS": str(passes["images"]), "N_COVER_WORDS": f"{passes['words']:,}",
                     "PSM3_EMPTY": f"{min(passes['psm3_empty'].values())}–{max(passes['psm3_empty'].values())}",
                     "NEW_SUMMARY": new_summary, "PASSES_NOTE": passes_note,
                     "TEST_LINES_TBL": lines_table(test_lines), "DEV_LINES_TBL": lines_table(dev_lines),
                     "RANLP_TBL": ranlp_tbl, "RANLP_GROUPS_TBL": ranlp_groups_tbl, "TOB_TBL": lines_table(tob),
                     "RENDERED_TBL": rendered_tbl, "SPEED_TBL": speed_tbl, "N_LINES": f"{n_lines:,}",
                     "N_RENDERED": f"{rendered['lines']:,}", "FAST_GAIN": fast_gain(speed),
                     "RES_TBLS": "\n".join(res_tbls), "N_TESTSETS": str(10 + with_covers),
                     "N_PAGES": str(scans["pages"] - len(scans["excluded"]) + len(res_sets[1][2])), "N_OLD_PAGES": str(len(res_sets[1][2])),
                     "N_RES_PAGES": str(len(res_sets[0][2]) + len(res_sets[1][2])), "N_REAL_RES": str(len(res_sets[0][2])),
                     "RES_NOTE": res_note, "RES_SUMMARY": res_summary}.items():
        tpl = tpl.replace("{{" + key + "}}", val)
    if not with_covers:
        tpl = re.sub(r"<!--COVERS-->.*?<!--/COVERS-->\n?", "", tpl, flags=re.S)
    tpl = tpl.replace("<!--COVERS-->", "").replace("<!--/COVERS-->", "")
    assert "{{" not in tpl, re.findall(r"\{\{\w+\}\}", tpl)
    return tpl


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Tamil OCR benchmark results</title>
<meta name="description" content="Every benchmark result for the open Tamil Tesseract model tam_v3 and the models it is compared with: real scanned pages and lines, RANLP 2025, the Tamil OCR Benchmark, rendered lines, scanning resolution, handwriting, camera photos of documents<!--COVERS-->, book covers and film posters<!--/COVERS-->, and speed.">
<meta property="og:title" content="Tamil OCR benchmark results">
<meta property="og:description" content="tam_v3 against stock Tesseract, tam_v2 and earlier models on real scans, RANLP 2025, handwriting, camera photos<!--COVERS-->, covers and posters<!--/COVERS-->, with CER, WER, BLEU, ANLS and METEOR.">
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
thead th.m { text-transform: none; letter-spacing: 0; font-size: 13px; }
h4 { font-family: var(--display); font-weight: 700; font-size: 16px; line-height: 1.3; margin: 20px 0 6px; }
tr.group td { font-weight: 600; font-size: 13.5px; color: var(--muted); background: var(--bg); }
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
    model, the previous open model tam_v2, the two research models trained before them, and a third-party Tamil model from
    Project Anuvaad. The handwriting, camera-photo<!--COVERS--> and cover<!--/COVERS--> tests compare tam_v3 with the stock models and the Anuvaad
    model. None of our models was trained on any of these test sets; for the Anuvaad model this cannot be checked. Four
    other OCR systems, two commercial and two open source, appear with the results a published paper reports for them.</p>
  <div class="summary" aria-label="What was tested">
    <span class="chip"><b>{{N_TESTSETS}}</b> test sets</span>
    <span class="chip"><b>9</b> models tested</span>
    <span class="chip"><b>4</b> other OCR systems, from a paper</span>
    <span class="chip"><b>{{N_LINES}}</b> text lines</span>
    <span class="chip"><b>{{N_HW_WORDS}}</b> handwritten words</span>
    <span class="chip"><b>{{N_PAGES}}</b> scanned pages</span>
<!--COVERS-->    <span class="chip"><b>{{N_COVERS}}</b> covers and posters</span><!--/COVERS-->
  </div>
</header>

<nav class="toc" aria-label="Contents">
  <ul>
    <li><a href="#summary">Summary</a></li>
    <li><a href="#models">Models</a></li>
    <li><a href="#measures">Measures</a></li>
    <li><a href="#psm">PSM</a></li>
    <li><a href="#test-sets">Test sets</a></li>
    <li><a href="#pages">Real pages</a></li>
    <li><a href="#lines">Real lines</a></li>
    <li><a href="#ranlp">RANLP 2025</a></li>
    <li><a href="#tob">Tamil OCR Benchmark</a></li>
    <li><a href="#rendered">Rendered lines</a></li>
    <li><a href="#resolution">Resolution</a></li>
    <li><a href="#handwriting">Handwriting</a></li>
    <li><a href="#photos">Camera photos</a></li>
<!--COVERS-->    <li><a href="#covers">Covers and posters</a></li>
<!--/COVERS-->
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
      against 3.25%); nearly all of its remaining errors are in the English words.</li>
    <li><b>Our scoring reproduces the paper's:</b> the stock Ubuntu model scores within 0.1 points of the paper's Tesseract
      CER and within 0.003 of its BLEU, ANLS and METEOR.</li>
{{RES_SUMMARY}}
{{NEW_SUMMARY}}
    <li><b>tam_v3_fast</b> scores within about 0.4 points of tam_v3 on every test set and is {{FAST_GAIN}} faster.</li>
    <li><b>Anuvaad <code>tam</code></b>, a third-party model, is weaker than the stock model on real book pages and lines
      but better on RANLP 2025. It leads the Tamil OCR Benchmark because it reads English words far better than any
      other model here; on that benchmark's Tamil letters it and tam_v3 are almost equal (see that section). It is also
      the slowest model here, at about {{ANUVAAD_SEC}} seconds per page.</li>
  </ul>
</section>

<section id="models">
  <h2>Models compared</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Model</th><th>Version</th><th>What it is</th><th>Licence</th></tr></thead>
    <tbody>
      <tr class="group"><td colspan="4">Run here</td></tr>
      <tr><td>Stock <code>tam</code> (tessdata_best 4.1.0)</td><td><a href="https://github.com/tesseract-ocr/tessdata_best/tree/4.1.0">tessdata_best 4.1.0</a>, released 16 February 2021. The Tamil model in it was trained on 29 June 2017 and added on 14 September 2017; it has not changed since. <span class="small muted">Model string <code>4.00.00alpha:tam:synth20170629</code></span></td><td>Tesseract's official Tamil model, the most accurate version; the starting point of all our models</td><td>Apache-2.0</td></tr>
      <tr><td>Stock <code>tam</code> (tessdata_fast 4.1.0, Ubuntu package)</td><td>Ubuntu 26.04 package <code>tesseract-ocr-tam</code> 1:4.1.0-2build1 (rebuilt 9 January 2026), which holds <a href="https://github.com/tesseract-ocr/tessdata_fast/tree/4.1.0">tessdata_fast 4.1.0</a>, released 16 February 2021. The Tamil model in it was trained on 29 June 2017 and added on 14 September 2017; it has not changed since.</td><td>The Tamil model installed by <code>apt install tesseract-ocr-tam</code>: a smaller, faster version</td><td>Apache-2.0</td></tr>
      <tr><td>Anuvaad <code>tam</code> <span class="small muted">third party</span></td><td><a href="https://github.com/project-anuvaad/anuvaad-ocr-model">anuvaad-ocr-model</a>, <code>anuvaad_tam.traineddata</code> of 18 May 2024; version tag 4.1.1</td><td>{{ANUVAAD_WHAT}}</td><td>MIT</td></tr>
      <tr><td>V1 <span class="small muted">tam_multifont</span></td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v1.0.0">1.0.0</a></td><td>Research model: 188 font styles, fonts only</td><td>Apache-2.0</td></tr>
      <tr><td>V2-research <span class="small muted">tam_v2_research</span></td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0-research">2.0.0-research</a></td><td>Research model: 276 font styles with fixes for old letters, spacing and digits, fonts only</td><td>CC BY-NC 4.0</td></tr>
      <tr><td>tam_v2</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0">2.0.0</a></td><td>The previous open model: 233 openly licensed font styles and 24,445 real scanned lines</td><td>Apache-2.0</td></tr>
      <tr><td>tam_v2_fast</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0">2.0.0</a></td><td>Integer version of tam_v2</td><td>Apache-2.0</td></tr>
      <tr class="ours"><td>tam_v3</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.0.0">3.0.0</a></td><td>The released model: tam_v2 trained further on 174,624 real scanned lines from 394 books and the same fonts</td><td>Apache-2.0</td></tr>
      <tr><td>tam_v3_fast</td><td><a href="https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.0.0">3.0.0</a></td><td>Integer version of tam_v3</td><td>Apache-2.0</td></tr>
      <tr class="group"><td colspan="4">Not run here: results quoted from <a href="https://aclanthology.org/2025.ranlp-1.56/">Jayatilleke &amp; de Silva, “Zero-shot OCR Accuracy of Low-Resourced Languages: A Comparative Analysis on Sinhala and Tamil”, RANLP 2025</a>, on that paper's test set only (<a href="#ranlp">RANLP 2025</a>)</td></tr>
      <tr class="paper"><td>Google Document AI <span class="small muted">commercial</span></td><td>Google Cloud service, as tested for the paper (2025)</td><td>Google's paid document-processing service, which includes OCR</td><td>Commercial cloud service</td></tr>
      <tr class="paper"><td>Google Cloud Vision API <span class="small muted">commercial</span></td><td>Google Cloud service, as tested for the paper (2025)</td><td>Google's paid image-analysis service, whose OCR has been generally available since May 2017</td><td>Commercial cloud service</td></tr>
      <tr class="paper"><td>EasyOCR</td><td><a href="https://github.com/JaidedAI/EasyOCR">JaidedAI/EasyOCR</a>; the paper gives no version</td><td>Open-source OCR library for over 80 languages: CRAFT text detection, then a ResNet, LSTM and CTC recogniser</td><td>Apache-2.0</td></tr>
      <tr class="paper"><td>Surya</td><td><a href="https://github.com/datalab-to/surya">datalab-to/surya</a>; the paper gives no version</td><td>Open-source OCR toolkit for over 90 languages, with a transformer text recogniser</td><td>Code Apache-2.0; model weights under a modified OpenRAIL-M licence</td></tr>
      <tr class="paper"><td>Tesseract 5.5.0, as run in the paper</td><td>Tesseract 5.5.0 with its stock Tamil model, through pytesseract</td><td>The paper's own run of stock Tesseract; our runs of the same model are the two stock rows above</td><td>Apache-2.0</td></tr>
    </tbody>
  </table></div>
  <p class="note">Every model run here was run with Tesseract 5.5.0 (Ubuntu package 5.5.0-1build1). The four other systems
    are not Tesseract models and were not run here: their numbers are the paper's, on its synthetic Tamil lines only, and
    show where Tesseract models stand against them on that one test.</p>
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
  <p class="note"><b>CER and WER are the main measures on this page.</b> BLEU and METEOR were made for machine translation and
    count whole words, so they miss the letter-level errors that Tamil OCR makes; ANLS comes from document question
    answering and scores any text with half or more of it wrong as 0. They are given mainly to compare with the RANLP 2025
    paper, which reports them.</p>
  <p class="note">Unless a section says otherwise, text is compared after Unicode NFC normalisation with invisible zero-width characters removed. RANLP 2025 is compared as is, as in its paper.</p>
</section>

<section id="psm">
  <h2>Page segmentation modes (PSM)</h2>
  <p>Before Tesseract reads any letters, it splits the image into blocks, lines and words. The page segmentation mode
    (<code>--psm</code>) tells it what kind of image to expect; the model then reads only the pieces this layout step
    hands it. So the mode decides what gets read at all, and the model decides how well. The modes on this page:</p>
  <dl class="measures">
    <dt><code>--psm 3</code></dt><dd>Fully automatic page layout, Tesseract's default. It looks for columns, paragraphs and
      lines and reads them in order, which suits book pages. Used for the page tests. On a cover or poster it often takes a
      large or decorated title for a picture and skips it.</dd>
    <dt><code>--psm 11</code></dt><dd>Sparse text: find as much text as possible, anywhere, in no particular order. It
      suits covers, posters and signs, but also reads parts of pictures as letters.</dd>
    <dt><code>--psm 7</code></dt><dd>The whole image is one line of text. Tesseract still checks that it can find a text
      line; on very faint or damaged lines that check can fail, and the output is empty.</dd>
    <dt><code>--psm 13</code></dt><dd>A raw line: the whole image is one line, without that check. Used for the real-line,
      handwriting and camera-photo tests.</dd>
  </dl>
  <p class="note">Other modes include 6 (one uniform block of text) and 12 (sparse text with orientation detection);
    <code>tesseract --help-psm</code> lists them all.</p>

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
      <tr><td><a href="#tob">Tamil OCR Benchmark</a></td><td class="n">200 lines</td><td>Clean rendered lines of real Tamil sentences in one font, a quarter of them with English words (mvbalaji/tamil-ocr-benchmark)</td><td><code>--psm 7</code></td></tr>
      <tr><td><a href="#rendered">Rendered lines</a></td><td class="n">{{N_RENDERED}} lines</td><td>A fixed set of held-out rendered lines, including three font families never used in training</td><td><code>--psm 7</code> and <code>--psm 13</code></td></tr>
      <tr><td><a href="#resolution">Scanning resolution</a></td><td class="n">{{N_RES_PAGES}} pages</td><td>{{N_REAL_RES}} of the real test pages (those sharp enough for 300 DPI) and {{N_OLD_PAGES}} pages from as many other books published before 1960, each as scanned and shrunk to 300, 200, 150, 100 and 72 DPI</td><td>Default page mode</td></tr>
      <tr><td><a href="#handwriting">Handwritten words</a></td><td class="n">{{N_HW_WORDS}} words</td><td>The Tamil test split of IIIT-INDIC-HW-WORDS, each word cropped to its ink</td><td><code>--psm 13</code></td></tr>
      <tr><td><a href="#handwriting">Handwritten lines</a></td><td class="n">{{N_HW_LINES}} lines</td><td>The same handwritten words joined 3–6 to a line</td><td><code>--psm 13</code></td></tr>
      <tr><td><a href="#photos">Camera photos</a></td><td class="n">{{N_APPEN}} lines</td><td>Lines cut from 55 phone photos of Tamil documents of 11 types (Appen)</td><td><code>--psm 13</code></td></tr>
<!--COVERS-->      <tr><td><a href="#covers">Covers and posters</a></td><td class="n">{{N_COVERS}} images</td><td>Book covers, magazine covers and film posters, read as whole images</td><td><code>--psm 3</code> and <code>--psm 11</code></td></tr><!--/COVERS-->
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
  <p>The 200 Tamil lines of the "real" set of <a href="https://huggingface.co/datasets/mvbalaji/tamil-ocr-benchmark">mvbalaji/tamil-ocr-benchmark</a>
    (Venkateswaran 2026; CC BY 4.0). "Real" means real Tamil sentences, as opposed to the set's scrambled text; the images are
    clean black-on-white renders in Noto Sans Tamil, not scans. 52 of the lines have English words in them, mostly names and
    terms in brackets.</p>
  {{TOB_TBL}}
  <h3>Where the errors are: Tamil letters or English letters</h3>
  <p class="cap">CER counted on the Tamil letters alone and on the English letters alone.</p>
  {{TOB_SPLIT_TBL}}
  <p class="note">{{TOB_NOTE}}</p>
</section>

<section id="rendered">
  <h2>Rendered lines</h2>
  <p>2,051 held-out rendered lines kept from tam_v2's training: the same kind of scan-like lines the models were trained on, including lines in three font families that none of our models was trained on.</p>
  {{RENDERED_TBL}}
  <p class="note">{{RENDERED_NOTE}}</p>
</section>

<section id="resolution">
  <h2>Scanning resolution</h2>
  <p>How small can the text be? Each page is read as scanned, and again after being shrunk to what a scanner set to 300,
    200, 150, 100 or 72 DPI would capture of 12-pt print. Scans rarely record their true resolution, so each page's
    body-text line height is measured first (<code>tools/make_dpi_set.py</code>) and pages printed in larger type are
    shrunk further: what a model sees is the size of the letters in pixels. At 12 pt a text line is about 57 pixels tall
    at 300 DPI, 38 at 200, 28 at 150, 19 at 100 and 14 at 72.</p>
  <p>Pages are only ever made smaller, never enlarged: each new pixel is the average of the source pixels it covers, as
    in a scanner's sensor. Every column has the same pages, so the columns can be compared; a page whose source text is too
    small for 300 DPI is left out of all of them. Pages whose text belongs to another page are found as scanned and left
    out; every other page counts, however badly it reads.</p>
  <p class="note">CER and WER are given at every resolution. BLEU, ANLS and METEOR follow the same pattern and are given as
    scanned and at 72 DPI only; each page is scored as one text and the scores are averaged over the pages.</p>
  {{RES_TBLS}}
  <p class="note">{{RES_NOTE}}</p>
  <p class="note">This test replaces an earlier one that read each page set at a single resolution, from archive.org page
    images that did not always match the proofread page. All pages here are the page images the Wikisource volunteers
    proofread.</p>
</section>

<section id="handwriting">
  <h2>Handwriting</h2>
  <p><b>None of the models on this page should be used to read photographs of handwritten text</b> (notes, letters,
    forms filled in by hand, whiteboards). The reasons:</p>
{{HW_REASONS}}
  <p>The two tests below show how far these printed-text models get on handwritten Tamil. Each image is read as one line
    (<code>--psm 13</code>).</p>
  <h3>{{N_HW_WORDS}} handwritten words (IIIT-INDIC-HW-WORDS)</h3>
  <p class="cap">The Tamil test split of <a href="https://cvit.iiit.ac.in/research/projects/cvit-projects/iiit-indic-hw-words">IIIT-INDIC-HW-WORDS</a>
    (CVIT, IIIT Hyderabad; CC BY 4.0), each word image cropped to its ink. There is one word per image, so the word error
    rate is left out: a space put inside a word counts as extra words.</p>
  {{HW_WORDS_TBL}}
  <h3>{{N_HW_LINES}} handwritten lines made from the same words</h3>
  <p class="cap">The test words joined 3–6 to a line, side by side with word spaces (<code>tools/join_hw_words.py</code>,
    seed 42), so a model must also find the gaps between words.</p>
  {{HW_LINES_TBL}}
  <p class="note">No model reads a whole line without an error. A word error rate above 100% means the output has more
    words than the line: printed-text models put spaces inside handwritten words. tam_v3 does this more often than the
    stock model here, so its WER is higher although its CER is lower.</p>
  <p class="note">The joined lines are made of real handwriting but are not written lines: their spacing and baselines are
    more regular than in a letter or a notebook. Handwritten notes and whiteboards photographed with a phone are in the
    camera-photo test below.</p>
</section>

<section id="photos">
  <h2>Camera photos of documents</h2>
  <p>{{N_APPEN}} Tamil text lines cut from 55 phone-camera photos of documents of 11 types, from Appen's free Tamil
    sample (<a href="https://www.kaggle.com/datasets/appenlimited/tamil-language-file-type-ocr-image-data">Kaggle:
    appenlimited/tamil-language-file-type-ocr-image-data</a>; © Appen Limited, CC BY-SA 4.0). Each line is cut out along
    its annotated box (<code>tools/labelme_lines.py</code>) and read as one line (<code>--psm 13</code>). Boxes marked
    unreadable and lines without Tamil letters are left out.</p>
  {{APPEN_TBL}}
  <p class="note">CER is the main measure here. Tamil words average about 8 letters and many photo lines (identity cards,
    bills, forms) are only a few words long, so one wrong letter or space makes a whole word wrong and WER swings widely;
    it still shows what share of words would be usable for search or copying.</p>
  <h3>CER by document type <span class="muted small">lower is better</span></h3>
  <p class="cap">The best model in each row is marked.</p>
  {{APPEN_KINDS_TBL}}
  <p class="note">Some photos show identity cards, badges, forms and bills with personal details, so the line images and
    their text are not published here or in the repository; only these totals are.</p>
</section>

<!--COVERS--><section id="covers">
  <h2>Covers and posters</h2>
  <p>Book covers, magazine covers and film posters are among the hardest scenarios for OCR: stylised and decorative
    lettering, text over pictures and coloured backgrounds, Tamil and English mixed, low-resolution scans, and layouts with
    no reading order. Tesseract and the models here were made for pages of running text, so this test shows where they
    stand, not what they were built for.</p>
  <p>{{N_COVERS}} whole images: 35 book covers (1967–2014) and 35 magazine covers (32 issues of Kalki from 1943 to 2010
    and three other magazines) from the Internet Archive, and 30 Tamil film posters (1940–1960, public domain) from
    Wikimedia Commons. Every word on each image was transcribed by hand and checked image by image: {{N_COVER_WORDS}}
    words. The images are not redistributed.</p>

  <h3>How covers are scored</h3>
  <dl class="measures">
    <dt>Words found</dt><dd>Share of the transcription's words that appear anywhere in the output, each counted as often
      as it occurs (recall). Covers have no single reading order, so order is ignored. Higher is better.</dd>
    <dt>Precision</dt><dd>Share of the output's words that are on the image. Low precision means parts of pictures were
      read as letters. Higher is better.</dd>
    <dt>Titles read</dt><dd>Images whose main title was found whole, every word of it.</dd>
  </dl>
  <p class="note">Words are compared after NFC normalisation, with punctuation removed and Latin letters in lower case
    (<code>tools/score_covers.py</code>).</p>

  <h3>All {{N_COVERS}} images</h3>
  {{COVERS_TBL}}
  <p class="note">With <code>--psm 3</code> Tesseract finds no text at all on {{PSM3_EMPTY}} of the {{N_COVERS}} images,
    whichever model reads them.</p>
  <h3>By kind</h3>
  <p class="cap">Words found with <code>--psm 11</code>; the best model in each row is marked.</p>
  {{COVERS_KIND_TBL}}
  <h3>By decade</h3>
  <p class="cap">Words found with <code>--psm 11</code>. The 1940s and 1950s are mostly film posters; the later decades
    are book and magazine covers.</p>
  {{COVERS_DECADE_TBL}}
  <h3>Reading each image in several passes</h3>
  <p class="cap"><code>--psm 11</code> on the image as is, on an inverted copy (for light text on a dark background), on a
    half-size copy (large titles become line-sized) and with Sauvola thresholding (<code>-c thresholding_method=2</code>,
    for uneven backgrounds). Merged passes keep each word as often as the pass that found it most often.</p>
  {{PASSES_TBL}}
  <p class="note">{{PASSES_NOTE}}</p>
</section><!--/COVERS-->

<section id="speed">
  <h2>Speed and memory</h2>
  <p>One page at a time on one CPU thread (<code>OMP_THREAD_LIMIT=1</code>), the same 8 real pages for every model, each
    page read three times and the middle time kept; all models timed together on 21 November 2026, on the machine that ran
    all tests. Peak memory is the largest resident size of the <code>tesseract</code> process. Differences under about
    0.1 s are within the run-to-run variation.</p>
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
python3 -m tamtrain lines benchmarks/ranlp2025/lines --name ranlp2025 --raw --psm 3 $C

<span class="c"># scanning resolution: the real pages and the old-book pages, shrunk to 300, 200, 150, 100 and 72 DPI</span>
python3 tools/fetch_wikisource.py --from-list benchmarks/resolution/old-books-source/pages.json --out old-books
python3 -m tamtrain scans old-books --name old-books-source $C
for s in scans/wikisource:real-pages old-books:old-books; do
  python3 tools/make_dpi_set.py ${s%%:*} --out res/${s##*:} --dpi 72 100 150 200 300
done
for d in 300 200 150 100 072; do
  python3 -m tamtrain scans res/real-pages/dpi-$d --name real-pages-$d --exclude-from work/report/scans.json $C
  python3 -m tamtrain scans res/old-books/dpi-$d --name old-books-$d --exclude-from work/report/old-books-source.json $C
done

<span class="c"># handwriting: IIIT-INDIC-HW-WORDS, Tamil test split, then the same words joined into lines</span>
python3 tools/iiit_hw_words.py fetch test --out downloads/iiit-hw
python3 tools/iiit_hw_words.py convert downloads/iiit-hw/test.zip --labels downloads/iiit-hw/test.txt \
    --vocab downloads/iiit-hw/vocab.txt --out hw-words/test
python3 -m tamtrain lines hw-words/test --name iiit-hw-test-words --psm 13 $C
python3 tools/join_hw_words.py hw-words/test --out hw-lines/test
python3 -m tamtrain lines hw-lines/test --name iiit-hw-test-lines --psm 13 $C

<span class="c"># camera photos: download and unpack the Appen sample from Kaggle into appen-photos/</span>
python3 tools/labelme_lines.py appen-photos --out appen-lines
python3 -m tamtrain lines appen-lines --name appen-photo-lines --psm 13 $C

<!--COVERS--><span class="c"># covers and posters: images/&lt;id&gt;.jpg, gt/&lt;id&gt;.txt, list.json and titles.json in one folder</span>
python3 tools/score_covers.py my-covers --out work/report/covers --model "tam_v3=models/tam_v3.traineddata" --psm 3 11<!--/COVERS--></code></pre>
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
    ap.add_argument("--extra-reports", type=Path, nargs="*", default=[ROOT / "work-v3" / "report", ROOT / "work-v3" / "report-extra",
                                                                     ROOT / "work-anuvaad" / "report"])
    ap.add_argument("--new-reports", type=Path, nargs="*", default=[ROOT / "work-bench-extra" / "report",
                                                                    ROOT / "work-anuvaad-extra" / "report"],
                    help="reports of the handwriting, camera-photo and cover tests, and speed.json")
    ap.add_argument("--res-reports", type=Path, default=ROOT / "work-resolution" / "report",
                    help="scans reports of the resolution ladders (real-pages-NNN, old-books-source, old-books-NNN)")
    ap.add_argument("--res-old-pages", type=Path, default=ROOT / "benchmarks" / "resolution" / "old-books-source",
                    help="the old-book pages (.gt.txt) of the resolution test")
    ap.add_argument("--pages", type=Path, default=ROOT / "scans" / "wikisource", help="the real test pages (.gt.txt)")
    ap.add_argument("--date", default="17–21 November 2026")
    ap.add_argument("--no-covers", action="store_true", help="leave the covers-and-posters test off the page")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "benchmarks" / "index.html")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build(args.reports, args.extra_reports, args.new_reports, args.pages, args.date, args.res_reports,
                              args.res_old_pages, not args.no_covers), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
