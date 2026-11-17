#!/bin/bash
# Build the book-based ICON-style test sets with Wikisource proofread text and archive.org page
# images (Wikimedia rate-limits page images). One page per book; never a training, dev or test book.
set -e
cd "$(dirname "$0")/../.."
B=benchmarks/icon-style/source
EX="examples/wikisource-pages.json books/books.json"
OLD='insource:"Type=book" insource:/Year *= *(18[0-9][0-9]|19[0-5][0-9])/'
NEW='insource:"Type=book" insource:/Year *= *20[0-9][0-9]/'
F="python3 tools/fetch_wikisource.py --pages 45 --min-chars 250 --per-book 1 --no-images"

trim() {  # keep the first 25 pages that have an image
python3 - "$1" <<'PY'
import json, sys
from pathlib import Path
d = Path(sys.argv[1]); pages = json.loads((d / "pages.json").read_text(encoding="utf-8"))
keep = [p for p in pages if (d / f"{p['id']}.png").exists()][:25]
ids = {p["id"] for p in keep}
for f in d.iterdir():
    if f.name != "pages.json" and f.name.split(".")[0] not in ids:
        f.unlink()
(d / "pages.json").write_text(json.dumps(keep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"{d}: {len(keep)} pages kept")
PY
}

$F --out $B/old-books --seed 2 --index-search "$OLD" --exclude-books $EX
python3 tools/ia_book_pages.py --pages $B/old-books && trim $B/old-books
$F --out $B/contemporary-books --seed 3 --index-search "$NEW" --exclude-books $EX
python3 tools/ia_book_pages.py --pages $B/contemporary-books && trim $B/contemporary-books
$F --out $B/contemporary-lowres --seed 4 --index-search "$NEW" --exclude-books $EX $B/contemporary-books/pages.json
python3 tools/ia_book_pages.py --pages $B/contemporary-lowres && trim $B/contemporary-lowres

python3 tools/make_dpi_set.py $B/old-books --out benchmarks/icon-style/old-books-72dpi --dpi 72 --font-pt 12
python3 tools/make_dpi_set.py $B/contemporary-books --out benchmarks/icon-style/contemporary-books-300dpi --dpi 300 --font-pt 12
python3 tools/make_dpi_set.py $B/contemporary-lowres --out benchmarks/icon-style/contemporary-lowres-96dpi --dpi 96 --font-pt 12
echo "ICON BOOK SETS DONE"
