#!/usr/bin/env python3
"""Build the files of a model release (maintainers only).

    python3 tools/make_release.py --work work-v2 --name tam_v2 --dist dist

Writes to --dist:
  <name>.traineddata          float model (tessdata_best)
  <name>_fast.traineddata     integer model (tessdata_fast)
  <name>-real-lines.jsonl.gz  every real scanned line used for training (train), checking (dev)
                              and testing (test): text, page image URLs and line box
  <name>-training-text.txt.gz the text the font lines were rendered from
  <name>-wordlist.txt.gz      the book words added to the dictionary
  SHA256SUMS
and to models/<name>/ in the repository: fonts.json (every font style, without local paths, with
its licence) and settings.json (the render and train settings).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_wikisource as fw  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IA_WIDTH = 1920     # ia_book_pages.py default, used for the V2 books


def font_licences(md: Path) -> list[tuple[str, dict]]:
    """(family, source/licence/class) from the first table of a fonts page: the fonts used."""
    rows, cols = [], None
    for line in md.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| Family |"):
            cols = {name: i for i, name in enumerate(cells)}
        elif cols is not None:
            if not line.startswith("|"):
                break
            if not cells[0].startswith("---"):
                lic = cells[cols["Licence"]]
                cls = cells[cols["Class"]] if "Class" in cols else licence_class(lic)
                rows.append((cells[0], {"source": cells[cols["Source"]], "licence": lic, "class": cls}))
    return sorted(rows, key=lambda r: -len(r[0]))     # longest family name first


def licence_class(lic: str) -> str:
    low = lic.lower()
    if low in ("proprietary", "unknown"):
        return "restricted"
    if low.startswith("non-commercial"):
        return "non-commercial"
    return "free-use" if low.startswith("free use") else "open"


def portable_fonts(work: Path, md: Path) -> list[dict]:
    fams = font_licences(md)
    key = lambda s: s.lower().replace(" ", "")     # "PostNoBillsJaffna Bold" is family "Post No Bills Jaffna"
    out = []
    for f in json.loads((work / "fonts.json").read_text(encoding="utf-8")):
        fam = next((info | {"family": name} for name, info in fams if key(f["name"]).startswith(key(name))), None)
        out.append({"name": f["name"], "file": Path(f["path"]).name, "variation": f.get("variation"),
                    "old_letters": f.get("old_letters") or [], "old_letters_default": f.get("old_letters_default", False),
                    "family": fam["family"] if fam else None, "source": fam["source"] if fam else None,
                    "licence": fam["licence"] if fam else None, "licence_class": fam["class"] if fam else None})
    return out


def strip_paths(obj):
    if isinstance(obj, dict):
        return {k: strip_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [strip_paths(v) for v in obj]
    if isinstance(obj, str) and obj.startswith("/"):
        p = Path(obj)
        return "~/" + str(p.relative_to(Path.home())) if p.is_relative_to(Path.home()) else str(p)
    return obj


def real_lines(sources: list[tuple[Path, Path]], test_lines: Path, test_pages: Path) -> list[dict]:
    """sources: (books folder, lines folder) pairs. A book's pages come from archive.org when
    ia.json found a copy, otherwise from its scan on Wikimedia (fetch_wikisource_books.py pdfs)."""
    rows = []
    for books, lines_root in sources:
        meta = {b["id"]: b for b in json.loads((books / "books.json").read_text(encoding="utf-8"))}
        ia_f = books / "ia.json"
        ia = json.loads(ia_f.read_text(encoding="utf-8")) if ia_f.exists() else {}
        on_ia = {i for i, s in ia.items() if s.get("status") == "ok"}
        wm = fw.file_info(sorted({meta[i]["book"] for i in meta if i not in on_ia and meta[i].get("rendered")}))
        for split in ("train", "dev"):
            listing = lines_root / split / "lines.json"
            if not listing.exists():
                continue
            for ln in json.loads(listing.read_text(encoding="utf-8")):
                book_id, page = ln["page"].split("/")
                b = meta[book_id]
                n = int(page[1:])
                img = next(books / d / book_id / f"{page}.png" for d in ("train", "dev")
                           if (books / d / book_id / f"{page}.png").exists())
                rev = next((p.get("revid") for p in b.get("pages_chosen", []) if p["page"] == n), None)
                row = {"split": split, "id": ln["id"], "page": f"{book_id}_{page}",
                       "text": (lines_root / split / f"{ln['id']}.gt.txt").read_text(encoding="utf-8").strip(),
                       "box": ln["box"], "page_size": list(Image.open(img).size),
                       "wikisource": {"page": f"பக்கம்:{b['book']}/{n}", "revid": rev, "year": b.get("year")}}
                if book_id in on_ia:
                    src = ia[book_id]
                    idx = src["pages"][str(n)][0]
                    ident = urllib.parse.quote(src["identifier"])
                    row["image_urls"] = [f"https://archive.org/download/{ident}/page/n{idx}_w{IA_WIDTH}.jpg",
                                         f"https://iiif.archive.org/iiif/{ident}%24{idx}/full/{IA_WIDTH},/0/default.jpg"]
                    row["archive_org"] = {"identifier": src["identifier"], "page_index": idx}
                else:
                    f = wm[b["book"]]
                    row["image_urls"] = [fw.thumb_url(f["url"], n, IA_WIDTH)]
                    row["wikimedia_file"] = {"url": f["url"], "page": n, "bytes": f["size"]}
                rows.append(row)
    pages = {p["id"]: p for p in json.loads((test_pages / "pages.json").read_text(encoding="utf-8"))}
    for ln in json.loads((test_lines / "lines.json").read_text(encoding="utf-8")):
        p = pages[ln["page"]]
        rows.append({"split": "test", "id": ln["id"], "page": ln["page"],
                     "text": (test_lines / f"{ln['id']}.gt.txt").read_text(encoding="utf-8").strip(),
                     "box": ln["box"], "page_size": list(Image.open(test_pages / f"{ln['page']}.jpg").size),
                     "image_urls": [p["image_url"]],
                     "wikisource": {"page": p["title"], "revid": p.get("revid")}})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", type=Path, default=ROOT / "work-v2")
    ap.add_argument("--name", default="tam_v2")
    ap.add_argument("--dist", type=Path, default=ROOT / "dist")
    ap.add_argument("--fonts-md", type=Path, default=ROOT / "examples" / "fonts-v2-open.md")
    ap.add_argument("--sources", nargs="+", default=["books:books-lines"], metavar="BOOKS:LINES",
                    help="book folder and line folder pairs, e.g. books:books-lines books-more:books-lines-more")
    ap.add_argument("--test-lines", type=Path, default=ROOT / "benchmarks" / "wikisource-test-lines")
    ap.add_argument("--test-pages", type=Path, default=ROOT / "scans" / "wikisource")
    ap.add_argument("--text", type=Path, default=ROOT / "corpus-v2.txt")
    ap.add_argument("--wordlist", type=Path, default=ROOT / "wordlist-v2.txt")
    ap.add_argument("--model-only", action="store_true",
                    help="only the model files (for models trained without real lines or own text, like V1)")
    args = ap.parse_args()
    args.dist.mkdir(parents=True, exist_ok=True)
    out = args.work / "output"
    shutil.copy2(out / "tessdata_best" / f"{args.name}.traineddata", args.dist / f"{args.name}.traineddata")
    shutil.copy2(out / "tessdata_fast" / f"{args.name}.traineddata", args.dist / f"{args.name}_fast.traineddata")

    sources = [tuple(ROOT / p for p in s.split(":", 1)) for s in args.sources]
    rows = [] if args.model_only else real_lines(sources, args.test_lines, args.test_pages)
    if not args.model_only:
        with gzip.open(args.dist / f"{args.name}-real-lines.jsonl.gz", "wt", encoding="utf-8", compresslevel=9) as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        for src_path, label in ((args.text, "training-text"), (args.wordlist, "wordlist")):
            with open(src_path, "rb") as src, gzip.open(args.dist / f"{args.name}-{label}.txt.gz", "wb", compresslevel=9) as dst:
                shutil.copyfileobj(src, dst)

    sums = []
    for p in sorted(args.dist.iterdir()):
        if p.name != "SHA256SUMS":
            sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    (args.dist / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")

    model_dir = ROOT / "models" / args.name
    model_dir.mkdir(parents=True, exist_ok=True)
    fonts = portable_fonts(args.work, args.fonts_md)
    (model_dir / "fonts.json").write_text(json.dumps(fonts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cfg = strip_paths(json.loads((args.work / "config.json").read_text(encoding="utf-8")))
    (model_dir / "settings.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    counts = {s: sum(r["split"] == s for r in rows) for s in ("train", "dev", "test")}
    missing = [f["name"] for f in fonts if not f["licence"]]
    print((f"{len(rows)} real lines {counts}; " if rows else "") + f"{len(fonts)} font styles"
          + (f"; NO LICENCE FOUND for {missing}" if missing else ""))
    for line in sums:
        print(" ", line)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
