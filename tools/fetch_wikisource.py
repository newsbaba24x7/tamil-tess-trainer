#!/usr/bin/env python3
"""Download real scanned Tamil book pages with human-proofread text from Tamil Wikisource.

Tamil Wikisource (ta.wikisource.org) volunteers proofread scanned books page by page. Pages
marked "proofread" (quality 3) or "validated" (quality 4, checked by a second person) give a
real scan plus its correct text: a test set that rendered fonts can't replace.

    python3 tools/fetch_wikisource.py --out scans/wikisource --pages 200

Pages are sampled at random across the whole site, at most --per-book pages per book, so the
set covers many printers, eras and scan qualities. The list of pages is saved in pages.json;
use --from-list pages.json to download exactly the same pages again.

Output (one pair per page, the layout `tamtrain scans` reads):
    <out>/<id>.jpg          the page scan (1920 px wide, from Wikimedia's thumbnail server)
    <out>/<id>.gt.txt       the proofread text, wiki markup removed, one line per paragraph
    <out>/<id>.wikitext     the original wiki text, to check the cleaning
    <out>/pages.json        title, book, page number, quality, source URLs per page
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tamtrain.tamil import normalize  # noqa: E402

API = "https://ta.wikisource.org/w/api.php"
SITE = "https://ta.wikisource.org/wiki/"
UA = "tamtrain/2.0 (https://github.com/newsbaba24x7/tamil-tess-trainer; Tamil OCR training data) python-urllib"
PAGE_NS = 250
INDEX_NS = 252
WIDTHS = (1280, 1920, 3840)   # Wikimedia only serves standard thumbnail widths


# ----------------------------------------------------------------------------- HTTP


def http_get(url: str, *, binary: bool = False, data: bytes | None = None, tries: int = 8):
    """GET (or POST with data), retrying on rate limits and server errors.

    Wikimedia renders page images on demand and rate-limits uncached renders (HTTP 429 with a
    Retry-After header), so a large download runs at about one new page every few seconds."""
    delay = 2.0
    for attempt in range(tries):
        req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read()
            return body if binary else body.decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            wait = exc.headers.get("Retry-After", "")
            time.sleep(float(wait) + 1 if wait.isdigit() else delay)
        except urllib.error.URLError:
            if attempt == tries - 1:
                raise
            time.sleep(delay)
        delay = min(delay * 2, 60)


def api(**params) -> dict:
    params = {"format": "json", "formatversion": "2", "maxlag": "5", **params}
    # POST: 50 percent-encoded Tamil titles are too long for a URL
    return json.loads(http_get(API, data=urllib.parse.urlencode(params).encode("ascii")))


# ----------------------------------------------------------------------------- wiki text -> plain text

DROP_TEMPLATES = {
    "gap", "dhr", "nop", "rule", "line", "clear", "custom rule", "***", "pagenum", "anchor",
    "dotted tc", "dotted toc page listing", "overfloat image", "missing image", "img float",
    "smallrefs", "reflist", "nbsp", "hr", "-", "brace", "brace2", "bar", "dropinitial",
}
SIZE_TEMPLATES = {"fs", "font-size", "font size", "fine", "span", "x-larger", "larger", "smaller"}
SIZE_ARG = re.compile(r"^\s*\d+(\.\d+)?\s*(%|em|px|pt)?\s*$")
SIZE_WITH_UNIT = re.compile(r"^\s*\d+(\.\d+)?\s*(%|em|px|pt)\s*$")   # never printed text, in any template
SPACE_TEMPLATES = {"dhr", "dhr2", "***", "asterism", "custom rule"}       # vertical space and ornaments
FIRST_ARG_ONLY = {"hws", "hwe", "hyphenated word start", "hyphenated word end", "lang", "nowrap"}


def _template(match: re.Match) -> str:
    parts = match.group(1).split("|")
    name = parts[0].strip().lower().replace("_", " ")
    args = [a for a in parts[1:] if not re.match(r"^\s*[\w -]+\s*=", a) and not SIZE_WITH_UNIT.match(a)]
    if name in DROP_TEMPLATES or name in SPACE_TEMPLATES or name.startswith(("dotted", "rule", "gap")):
        return ""
    if name in ("hws", "hyphenated word start", "hwe", "hyphenated word end"):
        return args[0] if args else ""
    if name == "lang":
        return args[1] if len(args) > 1 else ""
    if name in SIZE_TEMPLATES and args and SIZE_ARG.match(args[0]):
        args = args[1:]
    if name in ("rh", "runningheader", "running header"):
        return " ".join(a.strip() for a in args if a.strip())
    return " ".join(a for a in args)


def clean_wikitext(text: str) -> tuple[str | None, str]:
    """Return (plain text, reason). Text is None when the page is not a good test page."""
    text = re.sub(r"<pagequality[^>]*/>", "", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    if "{|" in text or "<math" in text or "<score" in text or "<table" in text.lower():
        return None, "table/math"
    # header | body | footer (ProofreadPage stores them in <noinclude> sections)
    m = re.match(r"^\s*<noinclude>(.*?)</noinclude>(.*?)(?:<noinclude>(.*?)</noinclude>)?\s*$", text, flags=re.S)
    header, body, footer = (m.group(1), m.group(2), m.group(3) or "") if m else ("", text, "")
    footer = re.sub(r"<references\s*/?>", "", footer)
    # footnotes are printed at the bottom of the page
    notes = re.findall(r"<ref(?:\s[^>/]*)?>(.*?)</ref>", body, flags=re.S)
    body = re.sub(r"<ref(?:\s[^>/]*)?>.*?</ref>", "", body, flags=re.S)
    body = re.sub(r"<ref[^>]*/>", "", body)
    text = "\n".join([header, body, "\n".join(notes), footer])

    text = re.sub(r"\[\[(?:File|Image|படிமம்|Category|பகுப்பு|கோப்பு):[^\]]*\]\]", "", text, flags=re.I)
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", text)
    for _ in range(10):                                  # innermost templates first
        new = re.sub(r"\{\{([^{}]*)\}\}", _template, text)
        if new == text:
            break
        text = new
    if "{{" in text or "}}" in text:
        return None, "unparsed template"
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("'''", "").replace("''", "")
    text = html.unescape(text)
    text = re.sub(r"__[A-Z]+__", "", text)

    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if re.fullmatch(r"-{4,}|_{3,}", line):
            continue
        line = re.sub(r"^=+\s*(.*?)\s*=+$", r"\1", line)
        line = re.sub(r"^[:*#;]+\s*", "", line)
        line = normalize(line)
        if line:
            lines.append(line)
    plain = "\n".join(lines)
    letters = [c for c in plain if unicodedata.category(c).startswith("L") or unicodedata.category(c) == "Mn"]
    tamil = sum(1 for c in letters if "஀" <= c <= "௿")
    if not letters or tamil / len(letters) < 0.8:
        return None, "not mostly Tamil"
    return plain, "ok"


# ----------------------------------------------------------------------------- sampling


def split_title(title: str) -> tuple[str, int] | None:
    """'பக்கம்:Book.pdf/82' -> ('Book.pdf', 82); single-image pages are skipped."""
    name = title.split(":", 1)[1]
    m = re.match(r"^(.*\.(?:pdf|djvu))/(\d+)$", name, flags=re.I)
    return (m.group(1), int(m.group(2))) if m else None


def sample_titles(n: int, per_book: int, min_quality: int, rng: random.Random, max_rounds: int = 60) -> list[dict]:
    by_book: dict[str, list[dict]] = defaultdict(list)
    seen = set()
    for rnd in range(max_rounds):
        data = api(action="query", generator="random", grnnamespace=PAGE_NS, grnlimit=500, prop="proofread")
        for p in data["query"]["pages"]:
            q = p.get("proofread", {}).get("quality", 0)
            parts = split_title(p["title"])
            if q < min_quality or not parts or p["title"] in seen:
                continue
            seen.add(p["title"])
            by_book[parts[0]].append({"title": p["title"], "book": parts[0], "page": parts[1], "quality": q})
        books = len(by_book)
        avail = sum(min(len(v), per_book) for v in by_book.values())
        print(f"  sampling round {rnd + 1}: {books} books, {avail} usable pages", flush=True)
        if avail >= n * 1.6:            # spare pages: some are dropped later (tables, too short…)
            break
        time.sleep(0.5)
    picked = []
    for book in sorted(by_book):
        pages = by_book[book]
        rng.shuffle(pages)
        picked += pages[:per_book]
    rng.shuffle(picked)
    return picked


def search_indexes(query: str, cap: int = 5000) -> list[str]:
    """Index pages matching a search, e.g. 'insource:/Year *= *19[0-5][0-9]/' or 'திராவிட நாடு'."""
    titles, offset = [], 0
    while True:
        d = api(action="query", list="search", srnamespace=INDEX_NS, srsearch=query, srlimit=500,
                sroffset=offset, srprop="")
        titles += [h["title"] for h in d["query"]["search"]]
        offset = d.get("continue", {}).get("sroffset")
        if not offset or len(titles) >= cap:
            return titles
        time.sleep(1)


def index_info(indexes: list[str]) -> dict[str, dict]:
    """Year and type (book, journal…) from each Index page's template."""
    info = {}
    for i in range(0, len(indexes), 50):
        chunk = indexes[i:i + 50]
        data = api(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(chunk))
        for p in data["query"]["pages"]:
            text = p["revisions"][0]["slots"]["main"]["content"] if p.get("revisions") else ""
            year = re.search(r"\|\s*Year\s*=\s*(1[5-9]\d\d|20\d\d)", text)
            kind = re.search(r"\|\s*Type\s*=\s*(\w+)", text)
            info[p["title"]] = {"year": int(year.group(1)) if year else None, "type": kind.group(1) if kind else None}
        time.sleep(0.5)
    return info


def sample_from_indexes(query: str, n: int, per_book: int, min_quality: int, rng: random.Random,
                        exclude_books: set[str]) -> list[dict]:
    """Pages from books (Index pages) matching a search, at most per_book (+1 spare) per book."""
    indexes = search_indexes(query)
    rng.shuffle(indexes)
    print(f"  {len(indexes)} books/issues match the search")
    want_books = -(-n // per_book) * 3 // 2 + 3   # spare books: some pages get filtered out later
    out: list[dict] = []
    books = 0
    for idx in indexes:
        if books >= want_books:
            break
        book = idx.split(":", 1)[1]
        if book in exclude_books or not re.search(r"\.(pdf|djvu)$", book, re.I):
            continue
        listed = api(action="query", list="proofreadpagesinindex", prppiititle=idx,
                     prppiiprop="title")["query"].get("proofreadpagesinindex", [])
        titles = [x["title"] for x in listed]
        rng.shuffle(titles)
        good = []
        for i in range(0, min(len(titles), 100), 50):
            q = api(action="query", prop="proofread", titles="|".join(titles[i:i + 50]))["query"]["pages"]
            good += [(p["title"], p["proofread"]["quality"]) for p in q
                     if p.get("proofread", {}).get("quality", 0) >= min_quality]
            if len(good) > per_book:
                break
        time.sleep(0.3)
        if not good:
            continue
        books += 1
        for title, quality in good[:per_book + 1]:
            parts = split_title(title)
            if parts:
                out.append({"title": title, "book": parts[0], "page": parts[1], "quality": quality, "index": idx})
    info = index_info(sorted({e["index"] for e in out}))
    for e in out:
        e.update(info.get(e["index"], {}))
    print(f"  {len(out)} candidate pages from {books} books")
    return out


def fetch_texts(entries: list[dict]) -> None:
    for i in range(0, len(entries), 50):
        chunk = entries[i:i + 50]
        if all(e.get("revid") for e in chunk):   # --from-list: the exact revisions tested before
            data = api(action="query", prop="revisions|proofread", rvprop="content|ids", rvslots="main",
                       revids="|".join(str(e["revid"]) for e in chunk))
        else:
            data = api(action="query", prop="revisions|proofread", rvprop="content|ids", rvslots="main",
                       titles="|".join(e["title"] for e in chunk))
        norm = {x["from"]: x["to"] for x in data["query"].get("normalized", [])}
        pages = {p["title"]: p for p in data["query"]["pages"]}
        for e in chunk:
            p = pages.get(norm.get(e["title"], e["title"]))
            if not p or "revisions" not in p:
                continue
            e["wikitext"] = p["revisions"][0]["slots"]["main"]["content"]
            e["revid"] = p["revisions"][0]["revid"]
            e["quality"] = p.get("proofread", {}).get("quality", e.get("quality"))
        time.sleep(0.3)


def file_info(books: list[str]) -> dict[str, dict]:
    """Book file name -> {"url": original upload URL, "size": bytes} (the file may live on Commons
    or on ta.wikisource)."""
    info = {}
    for i in range(0, len(books), 50):
        chunk = books[i:i + 50]
        data = api(action="query", prop="imageinfo", iiprop="url|size", titles="|".join("File:" + b for b in chunk))
        norm = {x["from"]: x["to"] for x in data["query"].get("normalized", [])}
        pages = {p["title"]: p for p in data["query"]["pages"]}
        for b in chunk:
            t = "File:" + b
            p = pages.get(norm.get(t, t))
            if p and p.get("imageinfo"):
                ii = p["imageinfo"][0]
                info[b] = {"url": ii["url"].split("?")[0], "size": ii.get("size", 0)}
        time.sleep(0.3)
    return info


def file_urls(books: list[str]) -> dict[str, str]:
    """Book file name -> original upload URL."""
    return {b: i["url"] for b, i in file_info(books).items()}


def thumb_url(original: str, page: int, width: int) -> str:
    m = re.match(r"^(https://upload\.wikimedia\.org/.+?)/([0-9a-f])/([0-9a-f]{2})/([^/]+)$", original)
    if not m:
        raise ValueError(f"unexpected upload URL: {original}")
    prefix, a, ab, name = m.groups()
    return f"{prefix}/thumb/{a}/{ab}/{name}/page{page}-{width}px-{name}.jpg"


def page_id(entry: dict) -> str:
    h = hashlib.sha1(entry["book"].encode("utf-8")).hexdigest()[:10]
    return f"ws_{h}_p{entry['page']:04d}"


# ----------------------------------------------------------------------------- main


def save_list(out: Path, done: list[dict]) -> None:
    (out / "pages.json").write_text(json.dumps(done, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("scans/wikisource"))
    ap.add_argument("--pages", type=int, default=200, help="number of pages to download")
    ap.add_argument("--per-book", type=int, default=2, help="at most this many pages per book")
    ap.add_argument("--min-quality", type=int, default=3, choices=(3, 4),
                    help="3 = proofread or validated, 4 = validated only")
    ap.add_argument("--min-chars", type=int, default=300, help="skip pages with less text")
    ap.add_argument("--width", type=int, default=1920, choices=WIDTHS, help="image width in pixels")
    ap.add_argument("--from-list", type=Path, help="download the pages listed in an earlier pages.json")
    ap.add_argument("--index-search", metavar="QUERY",
                    help="only books/issues whose Index page matches this search, e.g. "
                         "'insource:/Year *= *19[0-5][0-9]/' (published 1900-1959) or 'திராவிட நாடு'")
    ap.add_argument("--exclude-books", type=Path, nargs="+", metavar="PAGES_JSON",
                    help="leave out books used in these earlier pages.json files")
    ap.add_argument("--no-images", action="store_true",
                    help="save the proofread text and page list only (get images elsewhere, e.g. ia_book_pages.py --pages)")
    ap.add_argument("--delay", type=float, default=0.4,
                    help="seconds to wait between page images (Wikimedia limits how fast it renders them)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    sys.stdout.reconfigure(line_buffering=True)
    rng = random.Random(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.from_list:
        listed = json.loads(args.from_list.read_text(encoding="utf-8"))
        entries = [{k: e.get(k) for k in ("title", "book", "page", "quality", "revid", "year")} for e in listed]
        print(f"Re-downloading {len(entries)} pages from {args.from_list}")
    elif args.index_search:
        exclude = set()
        for f in args.exclude_books or []:
            exclude |= {e["book"] for e in json.loads(f.read_text(encoding="utf-8"))}
        print(f"Sampling pages from books matching {args.index_search!r} (quality >= {args.min_quality}, "
              f"<= {args.per_book} per book, {len(exclude)} books excluded)")
        entries = sample_from_indexes(args.index_search, args.pages, args.per_book, args.min_quality, rng, exclude)
    else:
        print(f"Sampling Tamil Wikisource pages (quality >= {args.min_quality}, <= {args.per_book} per book)")
        entries = sample_titles(args.pages, args.per_book, args.min_quality, rng)

    fetch_texts(entries)
    kept, skipped = [], defaultdict(int)
    per_book: dict[str, int] = defaultdict(int)
    for e in entries:
        if not args.from_list and per_book[e["book"]] >= args.per_book:
            continue
        if "wikitext" not in e:
            skipped["missing"] += 1
            continue
        if not args.from_list and e.get("quality", 0) < args.min_quality:
            skipped["quality"] += 1
            continue
        plain, reason = clean_wikitext(e["wikitext"])
        if plain is None:
            skipped[reason] += 1
            continue
        if not args.from_list and len(plain) < args.min_chars:
            skipped["too short"] += 1
            continue
        e["text"] = plain
        kept.append(e)
        per_book[e["book"]] += 1
        if not args.from_list and len(kept) >= args.pages:
            break
    print(f"  {len(kept)} pages with usable text; skipped: "
          + (", ".join(f"{k} {v}" for k, v in sorted(skipped.items())) or "none"))

    if args.no_images:
        done = []
        for e in kept:
            pid = page_id(e)
            (args.out / f"{pid}.gt.txt").write_text(e["text"] + "\n", encoding="utf-8")
            (args.out / f"{pid}.wikitext").write_text(e["wikitext"], encoding="utf-8")
            done.append({"id": pid, "title": e["title"], "book": e["book"], "page": e["page"], "quality": e["quality"],
                         "revid": e.get("revid"), "year": e.get("year"),
                         "url": SITE + urllib.parse.quote(e["title"].replace(" ", "_"))})
        save_list(args.out, done)
        print(f"Saved the text of {len(done)} pages from {len({d['book'] for d in done})} books in {args.out} (no images)")
        return 0
    urls = file_urls(sorted({e["book"] for e in kept}))
    done = []
    for i, e in enumerate(kept, 1):
        if e["book"] not in urls:
            continue
        pid = page_id(e)
        img = args.out / f"{pid}.jpg"
        e["image_url"] = thumb_url(urls[e["book"]], e["page"], args.width)
        if not img.exists():
            try:
                img.write_bytes(http_get(e["image_url"], binary=True))
            except urllib.error.HTTPError as exc:
                print(f"  {e['title']}: image download failed ({exc.code})")
                continue
            time.sleep(args.delay)
        (args.out / f"{pid}.gt.txt").write_text(e["text"] + "\n", encoding="utf-8")
        (args.out / f"{pid}.wikitext").write_text(e["wikitext"], encoding="utf-8")
        done.append({"id": pid, "title": e["title"], "book": e["book"], "page": e["page"],
                     "quality": e["quality"], "revid": e.get("revid"), "year": e.get("year"),
                     "url": SITE + urllib.parse.quote(e["title"].replace(" ", "_")),
                     "image_url": e["image_url"], "file_url": urls[e["book"]]})
        if i % 10 == 0:
            print(f"  downloaded {i}/{len(kept)}")
            save_list(args.out, done)       # keep the list current if the download is stopped
    save_list(args.out, done)
    books = len({d["book"] for d in done})
    print(f"Saved {len(done)} pages from {books} books in {args.out}")
    print("Text: Tamil Wikisource contributors (CC BY-SA 4.0); scans: see each file's page on Wikimedia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
