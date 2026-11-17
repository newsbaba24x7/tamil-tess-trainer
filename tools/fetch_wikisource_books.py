#!/usr/bin/env python3
"""Collect whole proofread books from Tamil Wikisource for training on real scans.

Three steps, each resumable:

    python3 tools/fetch_wikisource_books.py select --out books --train 72 --dev 8 \\
        --exclude-books examples/wikisource-pages.json
    python3 tools/fetch_wikisource_books.py texts --out books --pages-per-book 40
    python3 tools/fetch_wikisource_books.py pdfs --out books

select   picks fully proofread books (index progress C or V) spread across publication eras,
         at most 2 per author, never a book listed in --exclude-books; a few go to a
         separate "dev" set used only to check training.
texts    downloads the proofread text of every page (for training text and the dictionary) and
         marks up to --pages-per-book pages, spread through the book, as line sources.
pdfs     downloads each book's PDF once (one request per book instead of one per page, which
         Wikimedia rate-limits) and renders the marked pages with pdftoppm at 1920 px width.

Layout: <out>/books.json, <out>/<split>/<book_id>/p0042.png + p0042.gt.txt, <out>/text/<book_id>.txt
Text: Tamil Wikisource contributors, CC BY-SA 4.0. Scans: see each file's page on Wikimedia.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_wikisource as fw  # noqa: E402

ERAS = [("before 1960", 0, 1959), ("1960-1999", 1960, 1999), ("2000 on", 2000, 2100), ("year unknown", None, None)]
WEIGHTS = {"before 1960": 0.33, "1960-1999": 0.22, "2000 on": 0.28, "year unknown": 0.17}


def field(text: str, name: str) -> str:
    m = re.search(rf"\|\s*{name}\s*=\s*([^\n|]*)", text)
    return m.group(1).strip() if m else ""


def book_id(book: str) -> str:
    return "wb_" + hashlib.sha1(book.encode("utf-8")).hexdigest()[:10]


def load(out: Path) -> list[dict]:
    return json.loads((out / "books.json").read_text(encoding="utf-8"))


def save(out: Path, books: list[dict]) -> None:
    (out / "books.json").write_text(json.dumps(books, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- select

def cmd_select(args) -> None:
    exclude = set()
    for f in args.exclude_books or []:
        exclude |= {e["book"] for e in json.loads(f.read_text(encoding="utf-8"))}
    titles = sorted(set(fw.search_indexes('insource:"Progress=V"')) | set(fw.search_indexes('insource:"Progress=C"')))
    print(f"{len(titles)} fully proofread books/issues on Tamil Wikisource")
    info = []
    for i in range(0, len(titles), 50):
        data = fw.api(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(titles[i:i + 50]))
        for p in data["query"]["pages"]:
            text = p["revisions"][0]["slots"]["main"]["content"] if p.get("revisions") else ""
            book = p["title"].split(":", 1)[1]
            year = re.match(r"(1[5-9]\d\d|20\d\d)", field(text, "Year"))
            pages = re.match(r"\d+", field(text, "Number of pages"))
            size = re.match(r"[\d.]+", field(text, "File size"))
            author = re.sub(r"\[\[[^|\]]*\|?([^\]]*)\]\]", r"\1", field(text, "Author")) or "?"
            info.append({"index": p["title"], "book": book, "type": field(text, "Type"), "author": author,
                         "year": int(year.group(1)) if year else None, "pages": int(pages.group()) if pages else None,
                         "size_mb": float(size.group()) if size else None})
        time.sleep(0.5)
    ok = [b for b in info if b["book"] not in exclude and b["book"].lower().endswith(".pdf")
          and b["type"] != "journal" and (b["size_mb"] or 0) <= args.max_mb and (b["pages"] or 100) >= 30]
    print(f"{len(ok)} usable (PDF, not a periodical, <= {args.max_mb} MB, not excluded)")
    rng = random.Random(args.seed)
    rng.shuffle(ok)
    per_era = {e[0]: [] for e in ERAS}
    for b in ok:
        y = b["year"]
        era = next(name for name, lo, hi in ERAS if (lo is None and y is None) or (y is not None and lo is not None and lo <= y <= hi))
        b["era"] = era
        per_era[era].append(b)
    total = args.train + args.dev
    if args.append:
        # top up eras whose candidates ran out before their quota was met (texts step accepts later)
        books = load(args.out)
        known = {b["book"] for b in books}
        added = 0
        for era, w in WEIGHTS.items():
            want = round(total * w)
            have = sum(b["era"] == era and b["split"] in ("train", "dev") for b in books)
            left = sum(b["era"] == era and b["split"] == "candidate" for b in books)
            if have >= want or left:
                continue
            more = [b for b in per_era[era] if b["book"] not in known][: (want - have) * args.pool]
            for b in more:
                b["split"], b["id"], b["quota"] = "candidate", book_id(b["book"]), want
            books += more
            added += len(more)
            print(f"  {era:13} has {have}/{want}; added {len(more)} more candidates")
        save(args.out, books)
        print(f"{added} candidates added")
        return
    pool = []
    for era, w in WEIGHTS.items():
        want = round(total * w)
        cands = per_era[era][: want * args.pool]
        for b in cands:
            b["split"], b["id"], b["quota"] = "candidate", book_id(b["book"]), want
        pool += cands
        print(f"  {era:13} want {want:3} books; {len(cands)} candidates (of {len(per_era[era])})")
    args.out.mkdir(parents=True, exist_ok=True)
    save(args.out, pool)
    print(f"{len(pool)} candidate books in {args.out / 'books.json'}; 'texts' checks them and accepts "
          f"{args.train} training and {args.dev} dev books")
    (args.out / "quota.json").write_text(json.dumps({"train": args.train, "dev": args.dev}) + "\n")


# ----------------------------------------------------------------------------- texts

def fetch_pages(titles: list[str], delay: float) -> tuple[list[dict], int]:
    """Proofread (quality >= 3) pages among titles, cleaned; and how many pages were checked."""
    entries, checked = [], 0
    for i in range(0, len(titles), 50):
        data = fw.api(action="query", prop="revisions|proofread", rvprop="content|ids", rvslots="main",
                      titles="|".join(titles[i:i + 50]))
        for p in data["query"]["pages"]:
            checked += 1
            q = p.get("proofread", {}).get("quality", 0)
            parts = fw.split_title(p["title"])
            if q < 3 or not parts or not p.get("revisions"):
                continue
            plain, _ = fw.clean_wikitext(p["revisions"][0]["slots"]["main"]["content"])
            if plain:
                entries.append({"page": parts[1], "text": plain, "revid": p["revisions"][0]["revid"]})
        time.sleep(delay)
    return entries, checked


def cmd_texts(args) -> None:
    """Check candidates in order and accept books whose pages really are proofread (the index's
    progress field is often out of date), until every era has its share of books."""
    books = load(args.out)
    quota = json.loads((args.out / "quota.json").read_text())
    (args.out / "text").mkdir(parents=True, exist_ok=True)
    dev_per_era = max(1, quota["dev"] // len(WEIGHTS))
    authors = defaultdict(int)
    for b in books:
        if b["split"] in ("train", "dev"):
            authors[b["author"]] += 1
    for era in WEIGHTS:
        accepted = [b for b in books if b["era"] == era and b["split"] in ("train", "dev")]
        for b in books:
            if b["era"] != era or b["split"] != "candidate":
                continue
            if len(accepted) >= b["quota"]:
                break
            if authors[b["author"]] >= 2:
                b["split"] = "skipped: author limit"
                continue
            listed = fw.api(action="query", list="proofreadpagesinindex", prppiititle=b["index"],
                            prppiiprop="title")["query"].get("proofreadpagesinindex", [])
            titles = [x["title"] for x in listed]
            if len(titles) > args.max_text_pages:      # spread through the book; fewer requests
                step_t = len(titles) / args.max_text_pages
                titles = [titles[int(i * step_t)] for i in range(args.max_text_pages)]
            first, checked = fetch_pages(titles[:50], args.delay)   # titles are spread, so a fair sample
            if checked == 0 or len(first) < 0.6 * checked:
                b["split"] = f"rejected: {len(first)} of {checked} sampled pages proofread"
                save(args.out, books)
                print(f"  {era:13} {b['book'][:45]}: {b['split']}", flush=True)
                continue
            rest, _ = fetch_pages(titles[50:], args.delay)
            entries = sorted(first + rest, key=lambda e: e["page"])
            body = [e for e in entries if len(e["text"]) >= args.min_chars]
            if len(body) < args.min_pages:
                b["split"] = f"rejected: only {len(body)} pages with enough text"
                save(args.out, books)
                print(f"  {era:13} {b['book'][:45]}: {b['split']}", flush=True)
                continue
            b["split"] = "dev" if sum(a["split"] == "dev" for a in accepted) < dev_per_era else "train"
            step = max(1, len(body) // args.pages_per_book)
            chosen = body[::step][: args.pages_per_book]
            d = args.out / b["split"] / b["id"]
            d.mkdir(parents=True, exist_ok=True)
            for e in chosen:
                (d / f"p{e['page']:04d}.gt.txt").write_text(e["text"] + "\n", encoding="utf-8")
            (args.out / "text" / f"{b['id']}.txt").write_text("\n".join(e["text"] for e in entries) + "\n",
                                                                encoding="utf-8")
            b["proofread_pages"] = len(entries)
            b["pages_chosen"] = [{"page": e["page"], "revid": e["revid"]} for e in chosen]
            accepted.append(b)
            authors[b["author"]] += 1
            save(args.out, books)
            print(f"  {era:13} {len(accepted):3}/{b['quota']} {b['split']:5} {b['book'][:45]}: "
                  f"{len(entries)} proofread pages, {len(chosen)} chosen", flush=True)
    n = {s: sum(b["split"] == s for b in books) for s in ("train", "dev")}
    print(f"accepted {n['train']} training and {n['dev']} dev books")


# ----------------------------------------------------------------------------- pdfs

def cmd_pdfs(args) -> None:
    if not shutil.which("pdftoppm"):
        raise SystemExit("pdftoppm is needed (Debian/Ubuntu: sudo apt install poppler-utils)")
    books = load(args.out)
    urls = fw.file_urls([b["book"] for b in books if b["split"] in ("train", "dev") and not b.get("rendered")])
    for n, b in enumerate(books, 1):
        if b.get("rendered") or not b.get("pages_chosen") or b["split"] not in ("train", "dev"):
            continue
        url = urls.get(b["book"])
        if not url:
            print(f"  {b['book']}: no file URL"); continue
        d = args.out / b["split"] / b["id"]
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "book.pdf"
            try:
                pdf.write_bytes(fw.http_get(url, binary=True, tries=args.tries))
            except urllib.error.HTTPError as exc:
                print(f"  {b['book'][:50]}: download failed ({exc.code}); run again later", flush=True)
                if exc.code == 429:
                    break           # Wikimedia is rate-limiting this computer: stop instead of hammering
                continue
            for p in b["pages_chosen"]:
                target = d / f"p{p['page']:04d}"
                subprocess.run(["pdftoppm", "-f", str(p["page"]), "-l", str(p["page"]), "-scale-to-x", str(args.width),
                                "-scale-to-y", "-1", "-gray", "-png", "-singlefile", str(pdf), str(target)],
                               capture_output=True)
        b["rendered"] = sum((d / f"p{p['page']:04d}.png").exists() for p in b["pages_chosen"])
        save(args.out, books)
        print(f"  {n}/{len(books)} {b['book'][:50]}: {b['rendered']} pages rendered", flush=True)
        time.sleep(args.delay)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select"); s.set_defaults(func=cmd_select)
    s.add_argument("--train", type=int, default=72); s.add_argument("--dev", type=int, default=8)
    s.add_argument("--max-mb", type=float, default=60, help="skip books whose PDF is larger")
    s.add_argument("--exclude-books", type=Path, nargs="+", help="pages.json files whose books must not be used")
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--pool", type=int, default=4, help="candidates per wanted book (some are not really proofread)")
    s.add_argument("--append", action="store_true", help="add candidates for eras still short of their quota")
    t = sub.add_parser("texts"); t.set_defaults(func=cmd_texts)
    t.add_argument("--pages-per-book", type=int, default=40)
    t.add_argument("--min-chars", type=int, default=300)
    t.add_argument("--max-text-pages", type=int, default=120, help="pages of text fetched per book")
    t.add_argument("--min-pages", type=int, default=20, help="accept a book only with this many usable pages")
    t.add_argument("--delay", type=float, default=1.0, help="seconds between API requests")
    p = sub.add_parser("pdfs"); p.set_defaults(func=cmd_pdfs)
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--delay", type=float, default=20, help="seconds between books")
    p.add_argument("--tries", type=int, default=4)
    for sp in (s, t, p):
        sp.add_argument("--out", type=Path, default=Path("books"))
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
