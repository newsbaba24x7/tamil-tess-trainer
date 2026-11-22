#!/usr/bin/env python3
"""Step 13 - Where do the errors come from? Exact edit alignment of every line, classified.

  python3 -I 13_error_analysis.py RESULTS_DIR LINE_LIST.jsonl.gz MODEL [MODEL...] > report.md
RESULTS_DIR holds <model>.jsonl from 10_evaluate.py (id, ref, hyp). LINE_LIST gives page, box and book.
Sections: error classes (and CER/WER if a class were fixed), character and cluster confusions, words,
pages/books, line height, pre-1978 letter forms, suspicious lines (likely ground-truth or crop issues).
"""
import collections, gzip, json, re, statistics, sys
from pathlib import Path

CONS = set("கஙசஞடணதநபமயரலவழளறனஜஷஸஹஶ") ; VOW = set("அஆஇஈஉஊஎஏஐஒஓஔ")
SIGNS = set("ாிீுூெேைொோௌௗ")
CLUSTER = re.compile("[஀-௿][ா-்ௗ]*|.", re.S)
REFORM = re.compile("[ணறன][ாொோ]|[ணலளன]ை")          # letters drawn differently before the 1978 reform


def cls(c):
    if c == " ": return "space"
    if c in "'\"‘’“”‛′″`": return "quote"
    if c in "-–—―": return "hyphen/dash"
    if c in ".,": return "period/comma"
    if c in ";:!?…()[]{}": return "other punctuation"
    if c == "்": return "pulli ்"
    if c in SIGNS: return "vowel sign"
    if c in CONS: return "consonant"
    if c in VOW or c == "ஃ": return "vowel/aytham"
    if "௦" <= c <= "௺" or c == "ௐ": return "Tamil numeral/symbol"
    if c.isdigit(): return "ASCII digit"
    if c.isascii() and c.isalpha(): return "Latin letter"
    return "other"


def align(a, b):
    """Levenshtein alignment with backtrace: list of (op, ref_token, hyp_token)."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    ops, i, j = [], n, m
    while i or j:
        if i and j and D[i][j] == D[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            if a[i - 1] != b[j - 1]: ops.append(("sub", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i and D[i][j] == D[i - 1][j] + 1:
            ops.append(("del", a[i - 1], "")); i -= 1
        else:
            ops.append(("ins", "", b[j - 1])); j -= 1
    return ops[::-1]


def lev(a, b):
    return sum(1 for _ in align(a, b))


def main():
    args = sys.argv[1:]
    skip_empty = "--skip-empty" in args          # drop lines that every model returned empty (mode/crop problem)
    args = [a for a in args if a != "--skip-empty"]
    rdir, listfile, models = Path(args[0]), args[1], args[2:]
    meta = {}
    for l in gzip.open(listfile, "rt", encoding="utf-8"):
        r = json.loads(l)
        if r["split"] == "test":
            meta[r["id"]] = r
    P = print
    data = {m: [json.loads(l) for l in open(rdir / f"{m}.jsonl", encoding="utf-8")] for m in models}
    if skip_empty:
        empty = set.intersection(*({r["id"] for r in data[m] if not r["hyp"].strip()} for m in models))
        data = {m: [r for r in rows if r["id"] not in empty] for m, rows in data.items()}
        print(f"_{len(empty)} lines that every model returned empty are left out._\n")
    nchar = sum(len(r["ref"]) for r in data[models[0]]); nword = sum(len(r["ref"].split()) for r in data[models[0]])
    P(f"# Error analysis: {len(data[models[0]])} real test lines, {nchar:,} characters, {nword:,} words\n")

    # 1. error classes ------------------------------------------------------------------
    P("## 1. Character errors by class (share of all reference characters, i.e. CER points)\n")
    per = {}
    for m in models:
        c = collections.Counter(); wrong_words = collections.Counter(); total = 0
        for r in data[m]:
            for op, x, y in align(r["ref"], r["hyp"]):
                k = cls(x) if op != "ins" else cls(y)
                c[(k, op)] += 1; total += 1
        per[m] = (c, total)
    classes = sorted({k for m in models for (k, _) in per[m][0]}, key=lambda k: -sum(per[models[0]][0][(k, o)] for o in ("sub", "del", "ins")))
    P("| class | " + " | ".join(f"{m}: CER pts (sub/del/ins)" for m in models) + " |")
    P("|---|" + "---:|" * len(models))
    for k in classes:
        cells = []
        for m in models:
            c = per[m][0]; s, d, i = c[(k, "sub")], c[(k, "del")], c[(k, "ins")]
            cells.append(f"{100 * (s + d + i) / nchar:.2f} ({s}/{d}/{i})")
        P(f"| {k} | " + " | ".join(cells) + " |")
    P("| **all** | " + " | ".join(f"**{100 * per[m][1] / nchar:.2f}**" for m in models) + " |\n")

    # what-if: remove a class from both sides and rescore
    P("### CER / WER if a whole class of errors were fixed (both sides stripped of that class)\n")
    def strip(t, keep):
        return re.sub(" +", " ", "".join(ch for ch in t if keep(ch))).strip()
    scen = {"as measured": lambda ch: True,
            "spaces ignored": None,
            "quotes ignored": lambda ch: cls(ch) != "quote",
            "all punctuation ignored": lambda ch: cls(ch) not in ("quote", "hyphen/dash", "period/comma", "other punctuation"),
            "Tamil letters only": lambda ch: "஀" <= ch <= "௿" or ch == " "}
    P("| scenario | " + " | ".join(f"{m} CER / WER" for m in models) + " |\n|---|" + "---:|" * len(models))
    for name, keep in scen.items():
        cells = []
        for m in models:
            ce = cn = we = wn = 0
            for r in data[m]:
                if name == "spaces ignored":
                    a, b = r["ref"].replace(" ", ""), r["hyp"].replace(" ", "")
                    ce += lev(a, b); cn += len(a)
                    we += lev(r["ref"].split(), r["hyp"].split()); wn += len(r["ref"].split())
                    continue
                a, b = strip(r["ref"], keep), strip(r["hyp"], keep)
                ce += lev(a, b); cn += len(a); we += lev(a.split(), b.split()); wn += len(a.split())
            cells.append(f"{100 * ce / max(cn, 1):.2f} / {100 * we / max(wn, 1):.2f}" + (" (WER as measured)" if name == "spaces ignored" else ""))
        P(f"| {name} | " + " | ".join(cells) + " |")
    P()

    # 2. confusions --------------------------------------------------------------------------
    for m in models:
        cl = collections.Counter(); cp = collections.Counter()
        for r in data[m]:
            for op, x, y in align(CLUSTER.findall(r["ref"]), CLUSTER.findall(r["hyp"])):
                cl[(op, x, y)] += 1
            for op, x, y in align(r["ref"], r["hyp"]):
                cp[(op, x, y)] += 1
        P(f"## 2. Most frequent errors — {m}\n")
        P("| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |\n|---|---:|---|---|---:|")
        a, b = cl.most_common(30), cp.most_common(30)
        show = lambda t: {"sub": f"{t[1]!r} → {t[2]!r}", "del": f"{t[1]!r} → (missing)", "ins": f"(extra) → {t[2]!r}"}[t[0]]
        for (x, n1), (y, n2) in zip(a, b):
            P(f"| {show(x)} | {n1} |   | {show(y)} | {n2} |")
        P()

    # 3. words ---------------------------------------------------------------------------------
    m = models[0]
    P(f"## 3. Words — {m}\n")
    kinds = collections.Counter(); wrong = collections.Counter(); examples = {}
    for r in data[m]:
        for op, x, y in align(r["ref"].split(), r["hyp"].split()):
            if op == "sub":
                core = lambda w: re.sub(r"[^஀-௿A-Za-z0-9]", "", w)
                kinds["punctuation only" if core(x) == core(y) else "letters"] += 1
                if core(x) != core(y):
                    wrong[x] += 1; examples.setdefault(x, y)
            elif op == "del":
                kinds["word missing (often merged with a neighbour)"] += 1
            else:
                kinds["extra word (often a word split by a space)"] += 1
    tot = sum(kinds.values())
    P("| word error kind | count | share of word errors |\n|---|---:|---:|")
    for k, v in kinds.most_common():
        P(f"| {k} | {v} | {100 * v / tot:.0f}% |")
    P("\nMost often misread words (truth → one OCR example):\n")
    P(", ".join(f"{w} → {examples[w]} ({n}×)" for w, n in wrong.most_common(25)) + "\n")

    # 4. pages, books, line height ---------------------------------------------------------------
    P(f"## 4. Where errors concentrate — {m}\n")
    pg = collections.defaultdict(lambda: [0, 0]); bk = collections.defaultdict(lambda: [0, 0]); hb = collections.defaultdict(lambda: [0, 0])
    yr = collections.defaultdict(lambda: [0, 0])
    for r in data[m]:
        e, n = lev(r["ref"], r["hyp"]), len(r["ref"])
        md = meta.get(r["id"], {}); page = md.get("page", r["id"].rsplit("_", 1)[0])
        book = md.get("wikisource", {}).get("page", "?").split("/")[0].replace("பக்கம்:", "")
        h = md.get("box", [0, 0, 0, 0])[3]; hbin = "<30 px" if h < 30 else "30–39 px" if h < 40 else "40–49 px" if h < 50 else "≥50 px"
        y = md.get("wikisource", {}).get("year"); ybin = "no year" if not y else ("before 1978" if y < 1978 else "1978 or later")
        for d, k in ((pg, page), (bk, book), (hb, hbin), (yr, ybin)):
            d[k][0] += e; d[k][1] += n
    pcer = sorted((100 * e / n, k, e) for k, (e, n) in pg.items() if n)
    errs = sorted((e for _, _, e in pcer), reverse=True); T = sum(errs)
    P(f"- Page CER: median {statistics.median(x for x, _, _ in pcer):.2f}%, best {pcer[0][0]:.2f}%, worst {pcer[-1][0]:.2f}%.")
    for q in (10, 20, 50):
        k = max(1, len(errs) * q // 100)
        P(f"- The worst {q}% of pages ({k}) hold {100 * sum(errs[:k]) / T:.0f}% of all character errors.")
    P(f"- Pages under 2% CER: {sum(1 for x, _, _ in pcer if x < 2)} of {len(pcer)}.\n")
    P("| line height (box) | lines' CER |\n|---|---:|")
    for k in ("<30 px", "30–39 px", "40–49 px", "≥50 px"):
        if hb[k][1]: P(f"| {k} | {100 * hb[k][0] / hb[k][1]:.2f}% ({hb[k][1]:,} chars) |")
    P("\n| printed | CER |\n|---|---:|")
    for k, (e, n) in sorted(yr.items()): P(f"| {k} | {100 * e / n:.2f}% ({n:,} chars) |")
    P("\nWorst 12 books by CER:\n\n| book | CER | chars |\n|---|---:|---:|")
    for c, k, n in sorted(((100 * e / n, k, n) for k, (e, n) in bk.items() if n > 300), reverse=True)[:12]:
        P(f"| {k} | {c:.1f}% | {n:,} |")
    P()

    # 5. pre-reform letters -------------------------------------------------------------------------
    P(f"## 5. Letters whose shape changed in the 1978 reform — {m}\n")
    hit = tot_r = 0; c2 = collections.Counter()
    for r in data[m]:
        refs = REFORM.findall(r["ref"]); hyps = collections.Counter(REFORM.findall(r["hyp"]))
        for x in refs:
            tot_r += 1
            if hyps[x] > 0: hyps[x] -= 1; hit += 1
            else: c2[x] += 1
    P(f"Recovered {hit} of {tot_r} ({100 * hit / max(tot_r, 1):.1f}%). Most often missed: " + ", ".join(f"{k} ({v})" for k, v in c2.most_common(12)) + "\n")

    # 6. suspicious lines ------------------------------------------------------------------------------
    P(f"## 6. Lines with CER over 30% — {m} (likely crop or ground-truth problems)\n")
    bad = [(lev(r["ref"], r["hyp"]) / max(len(r["ref"]), 1), r) for r in data[m]]
    bad = sorted([x for x in bad if x[0] > .3], key=lambda x: -x[0])
    share = sum(lev(r["ref"], r["hyp"]) for _, r in bad)
    P(f"{len(bad)} lines ({100 * len(bad) / len(data[m]):.1f}%) hold {100 * share / per[m][1]:.0f}% of the character errors. Examples:\n")
    for c, r in bad[:10]:
        P(f"- {100 * c:.0f}% `{r['id']}`  truth: {r['ref'][:70]}  |  OCR: {r['hyp'][:70]}")


if __name__ == "__main__":
    main()
