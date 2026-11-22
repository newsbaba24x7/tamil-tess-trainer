#!/usr/bin/env python3
"""Step 3.2 - Build the v3.1 training and evaluation line texts.

Training lines (train.tsv: id, category, text) by category:
  natural   chunks of cleaned natural Tamil text
  numerals  all 36 requested Tamil numeral forms, positional and traditional numbers,
            dates, page numbers, money, Tamil day/month/year/debit/credit symbols, ௐ
  punct     natural chunks with quotes, brackets, dashes, ellipses, ?, !, :, ;, %, money, dates
  mixed     Tamil chunks with English technical terms, units, versions, file names
  english   pure English lines (SCOWL words + technical terms)
  edge      words with grantha letters, க்ஷ, ஸ்ரீ, ஔ/ௌ, ஃ, dense vowel signs and pulli
Evaluation lines (eval.tsv) come from 3% of natural text lines never used for training and
from English terms held out of training (every 5th term), one category per point 16 A-G:
  A_tamil  B_vowel_signs  C_grantha  D_pulli  E_numerals  F_mixed  G_technical  P_punct

  python3 -I 02_make_corpus.py --natural clean/natural.txt --words clean/words.txt \
      --terms english_terms.txt --english /usr/share/dict/american-english \
      --train 24000 --out corpus
"""
import argparse, collections, random, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charset import NUMERAL_FORMS, ok  # noqa: E402

TD = "௦௧௨௩௪௫௬௭௮௯"
GRANTHA = re.compile("[ஜஷஸஹஶ]|க்ஷ|ஸ்ரீ")
VOWEL_SIGNS = re.compile("[\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCC]")
SHARE = {"natural": .38, "numerals": .12, "punct": .13, "mixed": .20, "english": .07, "edge": .10}
EVAL_N = {"A_tamil": 250, "B_vowel_signs": 150, "C_grantha": 150, "D_pulli": 150,
          "E_numerals": 200, "F_mixed": 200, "G_technical": 150, "P_punct": 150}
SUFFIX = ["-இல்", "-ஐ", "-க்கு", "-இன்", "-ஆல்", "-உடன்", "-இலிருந்து", "-ஆக", "", "", "", ""]
UNITS = ["DPI", "MB", "GB", "KB", "GHz", "MHz", "km", "kg", "cm", "mm", "ml", "%", "px", "pt", "Mbps"]


def tamil_positional(n):
    return "".join(TD[int(d)] for d in str(n))


def tamil_traditional(n):
    """Traditional notation with ௰ (10), ௱ (100), ௲ (1000) multipliers, 1 <= n < 100000."""
    out = []
    for value, sign in ((1000, "௲"), (100, "௱"), (10, "௰")):
        q, n = divmod(n, value)
        if q:
            out.append(("" if q == 1 else tamil_traditional(q)) + sign)
    if n:
        out.append(TD[n])
    return "".join(out)


class Gen:
    def __init__(self, rng, natural, words, terms, english, book_style=False):
        self.r, self.nat, self.words, self.terms, self.eng = rng, natural, words, terms, english
        self.i = 0; self.book_style = book_style
        self.edge_words = [w for w in words if GRANTHA.search(w) or "ஔ" in w or "ௌ" in w or "ஃ" in w]
        self.num_cycle = []

    def chunk(self, lo=4, hi=9, maxlen=70):
        while True:
            ws = self.nat[self.i % len(self.nat)].split(); self.i += 1
            if len(ws) < lo:
                continue
            k = self.r.randint(lo, min(hi, len(ws))); s = self.r.randint(0, len(ws) - k)
            text = " ".join(ws[s:s + k])
            while len(text) > maxlen and " " in text:
                text = text.rsplit(" ", 1)[0]
            if len(text) >= 12:
                return text

    def tw(self, n):  # n Tamil dictionary words
        return " ".join(self.r.choice(self.words) for _ in range(n))

    def numerals(self):
        r = self.r
        if not self.num_cycle:
            self.num_cycle = NUMERAL_FORMS[:]; r.shuffle(self.num_cycle)
        kind = r.random()
        if kind < .35:   # the 36 requested forms, evenly cycled
            forms = [self.num_cycle.pop() for _ in range(min(r.randint(3, 6), len(self.num_cycle)))]
            parts = []
            for f in forms:
                parts += [f, self.tw(1)] if r.random() < .6 else [f]
            return " ".join(parts)
        n = r.choice([r.randint(1, 99), r.randint(100, 9999), r.randint(10000, 99999)])
        num = tamil_traditional(n) if r.random() < .4 and n < 100000 else tamil_positional(n)
        d, m, y = r.randint(1, 28), r.randint(1, 12), r.randint(1800, 2030)
        tmpl = r.choice([
            f"{num} {self.tw(2)}",
            f"பக்கம் {tamil_positional(r.randint(1, 999))} — {self.tw(2)}",
            f"{tamil_positional(r.randint(1, 30))}. {self.chunk(3, 6, 50)}",
            f"{tamil_positional(d)}-{tamil_positional(m)}-{tamil_positional(y)} அன்று {self.tw(2)}",
            f"{tamil_positional(d)} ௳ {tamil_positional(m)} ௴ {tamil_positional(y)} ௵",
            f"௹ {tamil_positional(r.randint(1, 99999))} {r.choice(['௶', '௷'])} {self.tw(1)}",
            f"ரூ. {tamil_positional(r.randint(1, 9999))} ({n} ரூபாய்) {self.tw(1)}",
            f"{tamil_traditional(r.randint(1, 9999))} {self.tw(1)} {tamil_positional(r.randint(1, 999))} {self.tw(1)}",
            f"௺ {tamil_positional(r.randint(1, 999))} {self.tw(2)} ௸",
            f"ௐ {self.tw(r.randint(2, 4))}",
            f"{y} ({tamil_positional(y)}) ஆம் ஆண்டு {self.tw(1)}",
        ])
        return tmpl

    def punctuate(self, text):
        if self.book_style:
            return self.punctuate_book(text)
        r, ws = self.r, text.split()
        ops = r.sample(range(12), r.randint(2, 3))
        for op in ops:
            i = r.randrange(len(ws))
            if op == 0: ws[i] = "“" + ws[i] + "”"
            elif op == 1: ws[i] = "‘" + ws[i] + "’"
            elif op == 2: ws[i] = '"' + ws[i] + '"'
            elif op == 3: ws[i] = "'" + ws[i] + "'"
            elif op == 4: ws[i] = "(" + ws[i] + ")"
            elif op == 5: ws[i] = "[" + ws[i] + "]"
            elif op == 6: ws.insert(i, r.choice(["—", "–", "-"]))
            elif op == 7: ws[i] += r.choice([",", ";", ":", "...", "…", "!", "?", "?!", "."])
            elif op == 8: ws.insert(i, f"{r.randint(1, 99)}%")
            elif op == 9: ws.insert(i, r.choice(["₹", "€", "£", "$"]) + f"{r.randint(1, 99999):,}" + (f".{r.randint(0, 99):02d}" if r.random() < .5 else ""))
            elif op == 10: ws.insert(i, r.choice([f"{r.randint(1, 28):02d}-{r.randint(1, 12):02d}-{r.randint(1900, 2030)}",
                                                    f"{r.randint(1, 28)}/{r.randint(1, 12)}/{r.randint(1900, 2030)}",
                                                    f"{r.randint(0, 23):02d}:{r.randint(0, 59):02d}"]))
            elif op == 11: ws[i] = ws[i] + r.choice(["*", "/", " &", " #" + str(r.randint(1, 99)), "-ஆம்"])
        s = " ".join(ws)
        return s + r.choice(["", ".", "?", "!", ":", "…", "."])

    def punctuate_book(self, text):
        """Punctuation as printed in Tamil books (round 3): hyphens mostly join words without
        spaces, quotes wrap whole phrases, dashes sometimes spaced; money/dates/percent kept."""
        r, ws = self.r, text.split()
        if len(ws) < 3:
            return text + r.choice([".", ",", "?", "!"])
        for _ in range(r.randint(1, 3)):
            op = r.choices(range(7), weights=[30, 30, 12, 8, 8, 6, 6])[0]
            i = r.randrange(len(ws) - 1)
            if op == 0:                                   # joined hyphen: வாழ்வை-உணர்வு
                ws[i:i + 2] = [ws[i] + "-" + ws[i + 1]]
            elif op == 1:                                 # quote around a 1-3 word phrase
                j = min(len(ws), i + r.randint(1, 3)); q = r.choice(["''", "''", "‘’", '""', "“”"])
                ws[i] = q[0] + ws[i]; ws[j - 1] = ws[j - 1] + q[1]
            elif op == 2:                                 # spaced dash
                ws.insert(i + 1, r.choice(["-", "-", "—", "–"]))
            elif op == 3:                                 # brackets around a phrase
                j = min(len(ws), i + r.randint(1, 3)); ws[i] = "(" + ws[i]; ws[j - 1] += ")"
            elif op == 4:
                ws[i] += r.choice([",", ";", ":", "...", "!", "?"])
            elif op == 5:
                ws.insert(i, r.choice(["₹", "$", "€", "£"]) + f"{r.randint(1, 99999):,}" if r.random() < .5 else f"{r.randint(1, 99)}%")
            else:
                ws.insert(i, r.choice([f"{r.randint(1, 28)}-{r.randint(1, 12)}-{r.randint(1900, 2030)}", f"{r.randint(1, 28)}.{r.randint(1, 12)}.{r.randint(1900, 2030)}"]))
        return " ".join(ws) + r.choice([".", ".", ".", ",", "?", "!", ";", ":"])

    def term(self, terms):
        r, t = self.r, self.r.choice(terms)
        x = r.random()
        if x < .25: return t + r.choice(SUFFIX)
        if x < .35: return f"({t})"
        if x < .45: return f"{r.randint(1, 999)} {r.choice(UNITS)}" if r.random() < .5 else f"v{r.randint(1, 9)}.{r.randint(0, 20)}"
        if x < .50: return r.choice(["tam.traineddata", "README.md", "config.json", "index.html", "main.py", "data.csv",
                                     "user@example.com", "https://example.org", "C:\\Users", "~/tessdata", "x^2", "`code`"])
        return t

    def mixed(self, terms, n_terms=(1, 3)):
        ws = self.chunk(3, 7, 55).split()
        for _ in range(self.r.randint(*n_terms)):
            ws.insert(self.r.randint(0, len(ws)), self.term(terms))
        return " ".join(ws)

    def english(self):
        r = self.r
        ws = [r.choice(self.eng) for _ in range(r.randint(4, 8))]
        for _ in range(r.randint(1, 2)):
            ws.insert(r.randint(0, len(ws)), r.choice(self.terms))
        s = " ".join(ws)
        s = s[0].upper() + s[1:]
        return s + r.choice([".", ".", ",", "?", "!", ":", ";"])

    def edge(self):
        r = self.r
        ws = [r.choice(self.edge_words) for _ in range(r.randint(3, 6))]
        ws.insert(r.randint(0, len(ws)), r.choice(["ஸ்ரீ", "ஸ்ரீமதி", "க்ஷேத்திரம்", "லக்ஷ்மி", "ஔவை", "கௌரவம்", "அஃது", "எஃகு"]))
        return " ".join(ws)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--natural", required=True); ap.add_argument("--words", required=True)
    ap.add_argument("--terms", required=True); ap.add_argument("--english", required=True)
    ap.add_argument("--train", type=int, default=24000); ap.add_argument("--seed", type=int, default=31)
    ap.add_argument("--out", required=True)
    ap.add_argument("--share", help="category shares, e.g. natural=.55,numerals=.04,... (default: rounds 1-2)")
    ap.add_argument("--train-seed", type=int, help="separate seed for training lines (the held-out split still uses --seed)")
    ap.add_argument("--book-punct", action="store_true", help="round 3: book-style hyphens, phrase quotes")
    ap.add_argument("--fixed-eval", help="keep this eval.tsv; drop training lines containing any of its lines")
    a = ap.parse_args()
    if a.share:
        SHARE.clear(); SHARE.update({k: float(v) for k, v in (x.split("=") for x in a.share.split(","))})
    rng = random.Random(a.seed)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    natural = [l.strip() for l in open(a.natural, encoding="utf-8") if l.strip()]
    rng.shuffle(natural)
    k = int(len(natural) * .03)
    nat_eval, nat_train = natural[:k], natural[k:]
    words = [w.strip() for w in open(a.words, encoding="utf-8") if w.strip()]
    terms = [t.strip() for t in open(a.terms, encoding="utf-8") if t.strip() and not t.startswith("#")]
    t_eval, t_train = terms[4::5], [t for i, t in enumerate(terms) if i % 5 != 4]
    eng = [w.strip() for w in open(a.english, encoding="utf-8") if re.fullmatch(r"[A-Za-z]{2,14}", w.strip())]

    g = Gen(random.Random(a.train_seed) if a.train_seed is not None else rng, nat_train, words, t_train, eng, a.book_punct)
    rows, n = [], 0
    for cat, share in SHARE.items():
        for _ in range(int(round(a.train * share))):
            text = {"natural": g.chunk, "numerals": g.numerals, "punct": lambda: g.punctuate(g.chunk()),
                    "mixed": lambda: g.mixed(t_train), "english": g.english, "edge": g.edge}[cat]()
            if ok(text):
                rows.append((f"tr{n:06d}", cat, text)); n += 1
    rng.shuffle(rows)

    if a.fixed_eval:
        fixed = [l.rstrip("\n").split("\t") for l in open(a.fixed_eval, encoding="utf-8") if l.strip()]
        texts = [t for _, _, t in fixed]
        before = len(rows)
        rows = [row for row in rows if not any(t in row[2] for t in texts)]
        (out / "train.tsv").write_text("".join(f"{i}\t{c}\t{t}\n" for i, c, t in rows), encoding="utf-8")
        forms = {f: "\n".join(t for _, _, t in rows).count(f) for f in NUMERAL_FORMS}
        print("train:", dict(collections.Counter(c for _, c, _ in rows)), f"| dropped {before - len(rows)} lines containing an eval line")
        print("eval kept as", a.fixed_eval, "| min/max occurrences of the 36 numeral forms:", min(forms.values()), max(forms.values()))
        return

    ge = Gen(random.Random(a.seed + 1), nat_eval, words, t_eval, eng)
    pool = [ge.chunk() for _ in range(6000)]
    pick = lambda pred, m: [p for p in dict.fromkeys(pool) if pred(p)][:m]
    ev = {
        "A_tamil": pick(lambda p: True, EVAL_N["A_tamil"]),
        "B_vowel_signs": sorted(dict.fromkeys(pool), key=lambda p: -len(set(VOWEL_SIGNS.findall(p))))[:EVAL_N["B_vowel_signs"]],
        "C_grantha": pick(lambda p: len(GRANTHA.findall(p)) >= 2, EVAL_N["C_grantha"]),
        "D_pulli": pick(lambda p: p.count("்") >= 6 or "ஃ" in p, EVAL_N["D_pulli"]),
        "E_numerals": [ge.numerals() for _ in range(EVAL_N["E_numerals"])],
        "F_mixed": [ge.mixed(t_eval, (1, 2)) for _ in range(EVAL_N["F_mixed"])],
        "G_technical": [ge.mixed(t_eval, (2, 4)) for _ in range(EVAL_N["G_technical"])],
        "P_punct": [ge.punctuate(ge.chunk()) for _ in range(EVAL_N["P_punct"])],
    }
    train_text = "\n".join(t for _, _, t in rows)
    erows, m, overlap = [], 0, 0
    for cat, lines in ev.items():
        for t in lines:
            if t in train_text:           # never score on a line the model was trained on
                overlap += 1
            elif ok(t):
                erows.append((f"ev{m:05d}", cat, t)); m += 1

    for name, rr in (("train.tsv", rows), ("eval.tsv", erows)):
        (out / name).write_text("".join(f"{i}\t{c}\t{t}\n" for i, c, t in rr), encoding="utf-8")
    stats = collections.Counter(c for _, c, _ in rows), collections.Counter(c for _, c, _ in erows)
    forms = {f: train_text.count(f) for f in NUMERAL_FORMS}
    print("train:", dict(stats[0]), "\neval:", dict(stats[1]))
    print("eval lines removed because they occur verbatim in training text:", overlap)
    print("held-out English terms:", len(t_eval), "| min/max occurrences of the 36 numeral forms:", min(forms.values()), max(forms.values()))


if __name__ == "__main__":
    main()
