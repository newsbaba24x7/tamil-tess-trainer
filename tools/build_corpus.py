#!/usr/bin/env python3
"""Training text and dictionary from proofread Wikisource books (training books only).

    python3 tools/build_corpus.py books --corpus corpus-v2.txt --wordlist wordlist-v2.txt \\
        --mix ~/.cache/tamtrain/langdata/tam.training_text --book-share 0.6

    # several book folders, Wikipedia sentences (English words in Tamil) kept whole, a size cap
    python3 tools/build_corpus.py books books-more --corpus corpus.txt --wordlist wordlist.txt \\
        --mix ~/.cache/tamtrain/langdata/tam.training_text --whole text-sources/tawiki-sample.txt \\
        --max-chars 26e6

corpus    book paragraphs interleaved with paragraphs from --mix files, so that about
          --book-share of the text is book Tamil (spelling, punctuation and vocabulary of print),
          plus every line of the --whole files. With --max-chars the book and --mix text is cut
          down in proportion, so the --whole files make up a known share. `tamtrain render`
          reads only the first part of a long text, so the share is what the rendered lines get.
wordlist  words seen at least --min-freq times in the training books (all of them, before any
          cut), for the model's dictionary

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
    ap.add_argument("books", type=Path, nargs="+",
                    help="folders made by fetch_wikisource_books.py or wikisource_pool.py")
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--wordlist", type=Path, required=True)
    ap.add_argument("--mix", type=Path, nargs="*", default=[], help="other text files to interleave")
    ap.add_argument("--whole", type=Path, nargs="*", default=[], help="text files included in full")
    ap.add_argument("--max-chars", type=float, help="cap the corpus at about this many characters")
    ap.add_argument("--book-share", type=float, default=0.6)
    ap.add_argument("--min-freq", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    files = []
    for folder in args.books:
        books = json.loads((folder / "books.json").read_text(encoding="utf-8"))
        files += [folder / "text" / f"{b['id']}.txt" for b in books if b["split"] == "train"]
    train_ids = files
    paras, words = [], Counter()
    for f in files:
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
    whole = []
    for w in args.whole:
        whole += [tamil.normalize(ln) for ln in w.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    whole_chars = sum(map(len, whole))
    if args.max_chars:                 # cut the book text so books + mix + whole fit the cap
        budget = max(0.0, args.max_chars - whole_chars) * args.book_share
        kept, n = [], 0
        for p in paras:
            if n >= budget:
                break
            kept.append(p)
            n += len(p)
        paras = kept
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
    mixed = paras + picked + whole
    rng.shuffle(mixed)
    args.corpus.write_text("\n".join(mixed) + "\n", encoding="utf-8")
    vocab = sorted(w for w, c in words.items() if c >= args.min_freq and len(w) >= 2)
    args.wordlist.write_text("\n".join(vocab) + "\n", encoding="utf-8")
    total = book_chars + sum(map(len, picked)) + whole_chars
    print(f"{len(train_ids)} training books: {len(paras)} paragraphs, {book_chars / 1e6:.1f}M characters of book text")
    print(f"corpus: {len(mixed)} paragraphs, {total / 1e6:.1f}M characters: books {100 * book_chars / total:.0f}%, "
          f"{', '.join(m.name for m in args.mix) or 'no mix'} {100 * sum(map(len, picked)) / total:.0f}%, "
          f"{', '.join(w.name for w in args.whole) or 'no whole files'} {100 * whole_chars / total:.0f}% -> {args.corpus}")
    print(f"wordlist: {len(vocab)} words seen >= {args.min_freq} times ({len(words)} distinct) -> {args.wordlist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
