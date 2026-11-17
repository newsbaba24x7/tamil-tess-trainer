#!/usr/bin/env python3
"""Training text and dictionary from proofread Wikisource books (training books only).

    python3 tools/build_corpus.py books --corpus corpus-v2.txt --wordlist wordlist-v2.txt \\
        --mix ~/.cache/tamtrain/langdata/tam.training_text --book-share 0.6

corpus    book paragraphs interleaved with paragraphs from --mix files, so that about
          --book-share of the text is book Tamil (spelling, punctuation and vocabulary of print)
wordlist  words seen at least --min-freq times in the training books, for the model's dictionary

Only books with split "train" in books.json are used: the dev books and every test book stay out,
so their words cannot leak into the model. Text: Tamil Wikisource contributors, CC BY-SA 4.0.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tamtrain import tamil  # noqa: E402

PUNCT = "".join(sorted(tamil.PUNCT))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("books", type=Path, help="folder made by fetch_wikisource_books.py")
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--wordlist", type=Path, required=True)
    ap.add_argument("--mix", type=Path, nargs="*", default=[], help="other text files to interleave")
    ap.add_argument("--book-share", type=float, default=0.6)
    ap.add_argument("--min-freq", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    books = json.loads((args.books / "books.json").read_text(encoding="utf-8"))
    train_ids = [b["id"] for b in books if b["split"] == "train"]
    paras, words = [], Counter()
    for bid in train_ids:
        f = args.books / "text" / f"{bid}.txt"
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = tamil.normalize(line)
            if len(line) < 20 or not any(tamil.is_tamil_char(c) for c in line):
                continue
            paras.append(line)
            for tok in line.split():
                core = tok.strip(PUNCT)
                if core and tamil.clean_token(core, allow_latin=False) and any(tamil.is_tamil_char(c) for c in core):
                    words[core] += 1
    rng = random.Random(args.seed)
    rng.shuffle(paras)
    book_chars = sum(map(len, paras))
    want_other = book_chars * (1 - args.book_share) / max(args.book_share, 1e-6)
    other = []
    for m in args.mix:
        other += [ln for ln in m.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    rng.shuffle(other)
    picked, n = [], 0
    for ln in other:
        if n >= want_other:
            break
        picked.append(ln)
        n += len(ln)
    mixed = paras + picked
    rng.shuffle(mixed)
    args.corpus.write_text("\n".join(mixed) + "\n", encoding="utf-8")
    vocab = sorted(w for w, c in words.items() if c >= args.min_freq and len(w) >= 2)
    args.wordlist.write_text("\n".join(vocab) + "\n", encoding="utf-8")
    print(f"{len(train_ids)} training books: {len(paras)} paragraphs, {book_chars / 1e6:.1f}M characters of book text")
    print(f"corpus: {len(mixed)} paragraphs ({len(picked)} from {', '.join(m.name for m in args.mix) or 'nothing'}) -> {args.corpus}")
    print(f"wordlist: {len(vocab)} words seen >= {args.min_freq} times ({len(words)} distinct) -> {args.wordlist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
