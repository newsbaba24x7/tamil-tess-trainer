#!/usr/bin/env python3
"""Step 16 - Add straight single-quote patterns to the punctuation dictionary.

tam_v3's (and Tesseract's) Tamil punctuation patterns contain double quotes but no pattern with a
straight single quote ('), which Tamil books and their proofread text use a lot. With an active word
dictionary the decoder then drops the quote to reach a dictionary word: on tam_v3's real dev lines,
round 4 with the full dictionary kept 42.8% of quotes; with these patterns 93.4% (WER 6.98% -> 5.55%).

  python3 -I 16_quote_patterns.py clean/puncs.txt clean/puncs_quotes.txt
"""
import sys

pats = [l.rstrip("\n") for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
out = list(dict.fromkeys(pats))
for p in pats:                        # every double-quote pattern also in a single-quote form
    if any(q in p for q in ('“', '”', '"')):
        out.append(p.replace('“', "'").replace('”', "'").replace('"', "'"))
for p in ("' ", " '", "' '", "' ',", "' '.", "' ';", "' ':", "' '?", "' '!",   # space = the word
          " ',", " '.", " ';", " '?", " '!", "(' ", " ')", "' -", "- '"):
    out.append(p)
out = list(dict.fromkeys(out))
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"punctuation patterns: {len(pats)} -> {len(out)} ({sum(1 for p in out if chr(39) in p)} with ')")
