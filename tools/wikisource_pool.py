#!/usr/bin/env python3
"""Pick proofread Tamil Wikisource books for real-line training by counting their proofread pages.

An index page's "fully proofread" flag is often wrong, and a book needs only enough proofread
pages, not every page. So this tool lists every page volunteers have proofread (quality 3) or
validated (quality 4), counts them per book, and picks books with enough of them:

    python3 tools/wikisource_pool.py scan --out books-more
    python3 tools/wikisource_pool.py pick --out books-more --books 400 --pages-per-book 24 \\
        --exclude-books examples/wikisource-pages.json books/books.json benchmarks/icon-style/source/*/pages.json
    python3 tools/wikisource_pool.py texts --out books-more
    python3 tools/ia_book_pages.py books-more          # page images from archive.org

scan   lists the two quality categories (a few hundred API requests) into <out>/pool.json.
pick   reads the index pages of books with at least --min-pages proofread pages, leaves out
       excluded books, spreads the choice over publication eras, allows at most --author-cap
       books per author, and holds back a share of periodical titles (--reserve-periodicals)
       for testing only: <out>/reserved-periodicals.json. Every picked book is for training.
texts  downloads the text of the chosen pages (the ground truth) and more proofread pages of the
       same book for training text, in the layout of fetch_wikisource_books.py, so
       ia_book_pages.py and page_lines.py work on it unchanged.

Text: Tamil Wikisource contributors, CC BY-SA 4.0.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_wikisource as fw  # noqa: E402
from fetch_wikisource_books import ERAS, WEIGHTS, book_id, fetch_pages, field  # noqa: E402

PAGE_NS = 250


def quality_categories() -> dict[int, str]:
    levels = fw.api(action="query", meta="proofreadinfo", piprop="qualitylevels")["query"]["proofreadqualitylevels"]
    return {q["id"]: q["category"] for q in levels}


def cmd_scan(args) -> None:
    cats = quality_categories()
    pool: dict[str, dict[str, int]] = defaultdict(dict)
    for q in (3, 4):
        n, cont = 0, {}
        while True:
            d = fw.api(action="query", list="categorymembers", cmtitle=f"Category:{cats[q]}",
                       cmnamespace=PAGE_NS, cmlimit=500, cmprop="title", **cont)
            for m in d["query"]["categorymembers"]:
                parts = fw.split_title(m["title"])
                if parts:
                    pool[parts[0]][str(parts[1])] = q
                    n += 1
            cont = d.get("continue", {})
            if not cont:
                break
            if n % 20000 < 500:
                print(f"  quality {q}: {n} pages", flush=True)
            time.sleep(args.delay)
        print(f"quality {q} ({cats[q]}): {n} pages")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "pool.json").write_text(json.dumps(pool, ensure_ascii=False) + "\n", encoding="utf-8")
    sizes = sorted((len(v) for v in pool.values()), reverse=True)
    print(f"{len(pool)} books with proofread pages; {sum(s >= 25 for s in sizes)} with 25 or more, "
          f"{sum(s >= 100 for s in sizes)} with 100 or more")


def series_name(title: str) -> str:
    """A periodical's name: the title up to its first digit or punctuation, without volume words.
    'திராவிட நாடு 1945 சனவரி 21-TVA…' -> 'திராவிட நாடு'; 'தென்மொழி, சுவடி1…' -> 'தென்மொழி'."""
    t = re.split(r"[\d,.;:–\-()/]", title, maxsplit=1)[0]
    words = [w for w in t.split() if w not in ("இதழ்", "இதழ்கள்", "தொகுப்பு", "மலர்", "சுவடி", "ஓலை", "தொகுதி")]
    return " ".join(words) or title.strip()


def cmd_pick(args) -> None:
    pool = json.loads((args.out / "pool.json").read_text(encoding="utf-8"))
    exclude = set()
    for f in args.exclude_books or []:
        for e in json.loads(f.read_text(encoding="utf-8")):
            # a book that an earlier selection only checked (rejected, skipped) was never used
            if "book" in e and e.get("split", "used").split(":")[0] not in ("rejected", "skipped", "candidate"):
                exclude.add(e["book"])
    least = min(args.min_pages, args.min_pages_periodical)       # periodical issues are short
    big = sorted(b for b, pages in pool.items() if len(pages) >= least and b not in exclude)
    print(f"{len(big)} books or issues with >= {least} proofread pages, not excluded "
          f"({len(exclude)} excluded titles); reading their index pages")
    info = []
    for i in range(0, len(big), 50):
        titles = [f"அட்டவணை:{b}" for b in big[i:i + 50]]
        d = fw.api(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(titles))
        for p in d["query"]["pages"]:
            if not p.get("revisions"):
                continue
            text = p["revisions"][0]["slots"]["main"]["content"]
            book = p["title"].split(":", 1)[1]
            year = re.search(r"(1[5-9]\d\d|20\d\d)", field(text, "Year"))
            author = re.sub(r"\[\[[^|\]]*\|?([^\]]*)\]\]", r"\1", field(text, "Author")) or "?"
            info.append({"index": p["title"], "book": book, "type": field(text, "Type") or "book",
                         "title": field(text, "Title") or book, "author": author,
                         "year": int(year.group(1)) if year else None, "proofread_in_pool": len(pool[book])})
        time.sleep(args.delay)
        if (i // 50) % 20 == 0:
            print(f"  index pages read: {min(i + 50, len(big))}/{len(big)}", flush=True)
    info = [b for b in info if b["proofread_in_pool"] >= (args.min_pages_periodical if b["type"] == "journal" else args.min_pages)]
    rng = random.Random(args.seed)
    # periodicals: hold back whole titles for testing, so test issues never share a title with training
    # the periodical's name comes from the file name: an issue's Title field often names one story
    series = sorted({series_name(b["book"]) for b in info if b["type"] == "journal"})
    rng.shuffle(series)
    reserved = set(series[: round(len(series) * args.reserve_periodicals)])
    (args.out / "reserved-periodicals.json").write_text(json.dumps(
        {"note": "Periodical titles held back for testing only; never train on their issues.",
         "titles": sorted(reserved),
         "issues": sorted(b["book"] for b in info if b["type"] == "journal" and series_name(b["book"]) in reserved)},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cands = [b for b in info if not (b["type"] == "journal" and series_name(b["book"]) in reserved)]
    print(f"{len(series)} periodical titles, {len(reserved)} held back for testing; {len(cands)} candidate books")
    for b in cands:
        y = b["year"]
        b["era"] = next(n for n, lo, hi in ERAS if (lo is None and y is None) or (y is not None and lo is not None and lo <= y <= hi))
    rng.shuffle(cands)
    per_era = defaultdict(list)
    for b in cands:
        per_era[b["era"]].append(b)
    authors: dict[str, int] = defaultdict(int)
    picked = []
    # periodicals first (there are few), then books by era share
    for b in [c for c in cands if c["type"] == "journal"]:
        picked.append(b)
        authors[b["author"]] += 1
    def take(b: dict) -> bool:
        if b in picked or len(picked) >= args.books or (b["author"] != "?" and authors[b["author"]] >= args.author_cap):
            return False
        picked.append(b)
        authors[b["author"]] += 1
        return True

    remaining = args.books - len(picked)
    for era, w in WEIGHTS.items():               # each era's share first
        want, got = round(remaining * w), 0
        for b in per_era[era]:
            if got >= want:
                break
            got += take(b)
        print(f"  {era:13} {got} books (share {want})")
    filled = sum(take(b) for b in cands)         # then fill from any era if some era ran short
    if filled:
        print(f"  {filled} more books from eras with candidates left")
    for b in picked:
        pages = sorted(int(p) for p in pool[b["book"]])
        step = max(1, len(pages) // args.pages_per_book)
        b.update({"split": "train", "id": book_id(b["book"]),
                  "pages_wanted": pages[::step][: args.pages_per_book], "text_pages": pages})
    (args.out / "books.json").write_text(json.dumps(picked, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(picked)} books picked ({sum(b['type'] == 'journal' for b in picked)} periodical issues) "
          f"in {args.out / 'books.json'}")


def cmd_texts(args) -> None:
    books = json.loads((args.out / "books.json").read_text(encoding="utf-8"))
    (args.out / "text").mkdir(parents=True, exist_ok=True)
    done = 0
    for n, b in enumerate(books, 1):
        if b.get("pages_chosen") is not None or b["split"] != "train":
            continue
        wanted = set(b["pages_wanted"])
        budget = max(0, args.max_text_pages - len(wanted))          # more pages of text for training text
        more = [p for p in b["text_pages"] if p not in wanted]
        extra = more[:: max(1, len(more) // budget)][:budget] if more and budget else []
        titles = [f"பக்கம்:{b['book']}/{p}" for p in sorted(wanted | set(extra))]
        entries, _ = fetch_pages(titles, args.delay)
        chosen = [e for e in entries if e["page"] in wanted and len(e["text"]) >= args.min_chars]
        if len(chosen) < (1 if b["type"] == "journal" else args.min_pages):
            b["split"] = f"rejected: only {len(chosen)} chosen pages with enough text"
        else:
            d = args.out / "train" / b["id"]
            d.mkdir(parents=True, exist_ok=True)
            for e in chosen:
                (d / f"p{e['page']:04d}.gt.txt").write_text(e["text"] + "\n", encoding="utf-8")
            (args.out / "text" / f"{b['id']}.txt").write_text(
                "\n".join(e["text"] for e in sorted(entries, key=lambda e: e["page"])) + "\n", encoding="utf-8")
            b["pages_chosen"] = [{"page": e["page"], "revid": e["revid"]} for e in chosen]
            b["proofread_pages"] = len(entries)
            done += 1
        (args.out / "books.json").write_text(json.dumps(books, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if n % 20 == 0:
            print(f"  {n}/{len(books)} books, {done} with text", flush=True)
    ok = [b for b in books if b.get("pages_chosen")]
    print(f"{len(ok)} books with text, {sum(len(b['pages_chosen']) for b in ok)} chosen pages")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    p = sub.add_parser("pick")
    p.add_argument("--books", type=int, default=400)
    p.add_argument("--pages-per-book", type=int, default=24)
    p.add_argument("--min-pages", type=int, default=25, help="proofread pages a book needs")
    p.add_argument("--min-pages-periodical", type=int, default=3, help="proofread pages a periodical issue needs")
    p.add_argument("--author-cap", type=int, default=4)
    p.add_argument("--reserve-periodicals", type=float, default=0.25, help="share of periodical titles kept for testing")
    p.add_argument("--exclude-books", type=Path, nargs="+", help="JSON lists with a 'book' field (test pages, used books)")
    p.add_argument("--seed", type=int, default=7)
    t = sub.add_parser("texts")
    t.add_argument("--max-text-pages", type=int, default=100, help="pages of text per book (chosen pages included)")
    t.add_argument("--min-chars", type=int, default=300)
    t.add_argument("--min-pages", type=int, default=12, help="chosen pages with enough text a book needs")
    for sp in (s, p, t):
        sp.add_argument("--out", type=Path, default=Path("books-more"))
        sp.add_argument("--delay", type=float, default=0.5, help="seconds between API requests")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    {"scan": cmd_scan, "pick": cmd_pick, "texts": cmd_texts}[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
