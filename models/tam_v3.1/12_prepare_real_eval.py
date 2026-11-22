#!/usr/bin/env python3
"""Step 12 - Describe the real test lines for 10_evaluate.py.

Writes LINES_DIR/real.tsv (id, category, text) and LINES_DIR/manifest.tsv (font column = book).
Categories by content of the proofread text:
  R_latin    has Latin letters          R_numbers  has ASCII digits or Tamil numerals
  R_tamil    everything else (Tamil text with ordinary punctuation)

  python3 -I 12_prepare_real_eval.py tam_v3-real-lines.jsonl.gz real_test/lines
"""
import collections, gzip, json, re, sys
from pathlib import Path

src, lines = sys.argv[1], Path(sys.argv[2])
split = sys.argv[3] if len(sys.argv) > 3 else "test"          # test (default) or dev
rows = [json.loads(l) for l in gzip.open(src, "rt", encoding="utf-8") if l.strip()]
test = [r for r in rows if r["split"] == split and (lines / f"{r['id']}.png").exists()]
cat = lambda t: "R_latin" if re.search("[A-Za-z]", t) else ("R_numbers" if re.search("[0-9௦-௲]", t) else "R_tamil")
with open(lines / "real.tsv", "w", encoding="utf-8") as c, open(lines / "manifest.tsv", "w", encoding="utf-8") as m:
    m.write("id\tcategory\tfont\tlatin_font\tpx\taugment\tfonts_used\n")
    for r in test:
        k = cat(r["text"]); book = r["wikisource"]["page"].split("/")[0].replace("பக்கம்:", "")
        c.write(f"{r['id']}\t{k}\t{r['text']}\n")
        m.write(f"{r['id']}\t{k}\treal scan\t-\t-\t-\t{book}\n")
print(f"{len(test)} real test lines with images:", dict(collections.Counter(cat(r['text']) for r in test)))
