#!/usr/bin/env python3
"""Page images from archive.org for proofread Wikisource books (no Wikimedia downloads needed).

Many Tamil Wikisource books are scans from the Tamil Virtual Academy / Tamil Digital Library,
and archive.org holds copies of them, often at higher resolution. For every book accepted by
`fetch_wikisource_books.py texts`, this tool:

  1. searches archive.org by the book's title;
  2. reads each candidate's per-page OCR text (the item's _djvu.xml);
  3. pairs every chosen Wikisource page with the archive.org page whose text matches it best
     (character 4-gram overlap), so different page numbering or front matter does not matter;
  4. accepts the candidate only if most chosen pages find a clear match (it is the same edition),
     and downloads those page images (1920 px wide) next to the proofread text.

    python3 tools/ia_book_pages.py books

State is kept in <books>/ia.json, so the tool can be stopped and run again. The proofread
text stays the ground truth; archive.org's own OCR text is only used to find the pages.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tamtrain.tamil import normalize  # noqa: E402

UA = {"User-Agent": "tamtrain/2.0 (https://github.com/newsbaba24x7/tamil-tess-trainer; Tamil OCR training data) python-urllib"}


def get(url: str, tries: int = 4, binary: bool = True):
    delay = 5.0
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            code = getattr(exc, "code", None)
            if attempt == tries - 1 or code in (401, 403, 404):
                raise
            time.sleep(delay)
            delay *= 2


def search(title: str, rows: int = 6) -> list[dict]:
    words = [w for w in re.sub(r"\.pdf$|\(IA [^)]*\)|\d{4} AD[- ]?(paper copy)?|[-,.()]", " ", title).split() if len(w) > 1][:4]
    if not words:
        return []
    q = "mediatype:texts AND (" + " AND ".join(f'title:"{w}"' for w in words) + ")"
    params = [("q", q), ("rows", rows), ("output", "json"), ("fl[]", "identifier"), ("fl[]", "title")]
    data = json.loads(get("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(params), binary=False))
    return data["response"]["docs"]


def grams(text: str, n: int = 4) -> set[str]:
    t = re.sub(r"[^஀-௿]", "", normalize(text))
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def ia_pages(ident: str) -> tuple[list[set[str]], str] | None:
    meta = json.loads(get(f"https://archive.org/metadata/{ident}", binary=False))
    xml_name = next((f["name"] for f in meta.get("files", []) if f.get("format") == "Djvu XML"), None)
    if not xml_name:
        return None
    raw = get(f"https://archive.org/download/{ident}/{urllib.parse.quote(xml_name)}")
    root = ET.fromstring(raw)
    pages = []
    for obj in root.iter("OBJECT"):
        pages.append(grams(" ".join(w.text or "" for w in obj.iter("WORD"))))
    return pages, xml_name


def match(gt_pages: dict[int, set[str]], ia: list[set[str]]) -> dict[int, tuple[int, float]]:
    """Wikisource page -> (archive.org page index, overlap) for clear matches only."""
    out = {}
    for p, g in gt_pages.items():
        if len(g) < 50:
            continue
        scores = sorted(((len(g & s) / max(len(g | s), 1), i) for i, s in enumerate(ia) if s), reverse=True)
        if not scores:
            continue
        best, second = scores[0], (scores[1][0] if len(scores) > 1 else 0.0)
        if best[0] >= 0.25 and best[0] >= 2 * second:
            out[p] = (best[1], round(best[0], 3))
    return out


def pages_mode(args) -> int:
    """Images for single pages listed in <dir>/pages.json (written by fetch_wikisource.py --no-images):
    each page is matched by its text among the archive.org copy's pages and saved as <id>.png."""
    d = args.pages
    entries = json.loads((d / "pages.json").read_text(encoding="utf-8"))
    done = 0
    for n, e in enumerate(entries, 1):
        out = d / f"{e['id']}.png"
        if out.exists():
            done += 1; continue
        g = grams((d / f"{e['id']}.gt.txt").read_text(encoding="utf-8"))
        status = "no archive.org copy found"
        try:
            cands = search(e["book"])
        except Exception as exc:  # noqa: BLE001
            print(f"  {n}: search failed ({exc})"); continue
        for c in cands:
            try:
                got = ia_pages(c["identifier"])
            except Exception:  # noqa: BLE001
                continue
            time.sleep(args.delay)
            if not got:
                continue
            m = match({e["page"]: g}, got[0])
            if e["page"] not in m:
                continue
            idx, score = m[e["page"]]
            ident = urllib.parse.quote(c["identifier"])
            try:
                im = Image.open(io.BytesIO(get(f"https://archive.org/download/{ident}/page/n{idx}_w{args.width}.jpg"))).convert("L")
            except Exception as exc:  # noqa: BLE001
                status = f"download failed ({exc})"; continue
            if im.width > args.width:
                im = im.resize((args.width, round(im.height * args.width / im.width)), Image.LANCZOS)
            im.save(out)
            e["ia_identifier"], e["ia_page"], e["ia_match"] = c["identifier"], idx, score
            status = f"{c['identifier']} page {idx} (match {score})"
            done += 1
            break
        print(f"  {n}/{len(entries)} {e['book'][:40]} p{e['page']}: {status}")
        (d / "pages.json").write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{done} of {len(entries)} pages have an archive.org image in {d}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("books", type=Path, nargs="?", help="folder made by fetch_wikisource_books.py")
    ap.add_argument("--pages", type=Path, help="instead: a folder of single pages (pages.json + .gt.txt)")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--min-share", type=float, default=0.6, help="share of chosen pages that must match")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--limit", type=int, help="only the first N books (for testing)")
    ap.add_argument("--workers", type=int, default=4, help="pages of one book downloaded at the same time")
    ap.add_argument("--book-workers", type=int, default=1,
                    help="books worked on at the same time; archive.org renders each page image on request "
                         "(4-10 s), so a few books at once mostly waits in parallel")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    if args.pages:
        return pages_mode(args)
    books = [b for b in json.loads((args.books / "books.json").read_text(encoding="utf-8"))
             if b["split"] in ("train", "dev") and b.get("pages_chosen")]
    books = books[: args.limit] if args.limit else books
    state_f = args.books / "ia.json"
    state = json.loads(state_f.read_text(encoding="utf-8")) if state_f.exists() else {}
    lock = threading.Lock()

    def one_book(n: int, b: dict) -> None:
        d = args.books / b["split"] / b["id"]
        gt_pages = {int(f.name[1:5]): grams(f.read_text(encoding="utf-8")) for f in d.glob("p*.gt.txt")}
        result = {"book": b["book"], "status": "no archive.org copy found"}
        try:
            cands = search(b["book"])
        except Exception as exc:  # noqa: BLE001
            print(f"  {n}/{len(books)} {b['book'][:45]}: search failed ({exc})"); return
        for c in cands:
            try:
                got = ia_pages(c["identifier"])
            except Exception as exc:  # noqa: BLE001
                print(f"     {c['identifier']}: {exc}"); continue
            time.sleep(args.delay)
            if not got:
                continue
            ia, _ = got
            m = match(gt_pages, ia)
            share = len(m) / max(len(gt_pages), 1)
            if share < args.min_share:
                continue
            def fetch(item, ident=urllib.parse.quote(c["identifier"])):
                p, (idx, score) = item
                out = d / f"p{p:04d}.png"
                if out.exists():
                    return 1
                urls = [f"https://archive.org/download/{ident}/page/n{idx}_w{args.width}.jpg",
                        f"https://iiif.archive.org/iiif/{ident}%24{idx}/full/{args.width},/0/default.jpg"]
                err = None
                for url in urls:
                    try:
                        im = Image.open(io.BytesIO(get(url))).convert("L")
                    except Exception as exc:  # noqa: BLE001
                        err = exc
                        continue
                    if im.width > args.width:      # the page service sometimes ignores the width
                        im = im.resize((args.width, round(im.height * args.width / im.width)), Image.LANCZOS)
                    part = out.with_name(f".{out.name}.part")     # a stopped run never leaves half an image
                    im.save(part, format="PNG")
                    part.replace(out)
                    time.sleep(args.delay)
                    return 1
                print(f"     page {p}: download failed ({err})")
                return 0

            with ThreadPoolExecutor(args.workers) as ex:     # a few pages at a time
                saved = sum(ex.map(fetch, m.items()))
            result = {"book": b["book"], "status": "ok", "identifier": c["identifier"], "matched": len(m),
                      "chosen": len(gt_pages), "saved": saved, "pages": {str(p): v for p, v in m.items()}}
            break
        with lock:
            state[b["id"]] = result
            state_f.write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        extra = f"{result['identifier']}: {result['saved']}/{result['chosen']} pages" if result["status"] == "ok" else result["status"]
        print(f"  {n}/{len(books)} {b['split']:5} {b['book'][:45]}: {extra}")

    todo = [(n, b) for n, b in enumerate(books, 1) if b["id"] not in state]
    with ThreadPoolExecutor(args.book_workers) as ex:
        for f in [ex.submit(one_book, n, b) for n, b in todo]:
            f.result()
    ok = [v for v in state.values() if v["status"] == "ok"]
    print(f"{len(ok)} of {len(state)} books found on archive.org; {sum(v['saved'] for v in ok)} page images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
