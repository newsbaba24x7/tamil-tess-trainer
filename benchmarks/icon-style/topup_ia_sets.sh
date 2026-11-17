#!/bin/bash
# Top up the book-based ICON-style sets to 25 pages each and fetch sharper images for the 300 DPI set.
set -e
cd "$(dirname "$0")/../.."
B=benchmarks/icon-style/source
OLD='insource:"Type=book" insource:/Year *= *(18[0-9][0-9]|19[0-5][0-9])/'
NEW='insource:"Type=book" insource:/Year *= *20[0-9][0-9]/'
USED="examples/wikisource-pages.json books/books.json $B/old-books/pages.json $B/contemporary-books/pages.json $B/contemporary-lowres/pages.json"
F="python3 tools/fetch_wikisource.py --pages 120 --min-chars 250 --per-book 1 --no-images"

merge() {  # move pages with images from $2 into $1 until it has 25
python3 - "$1" "$2" <<'PY'
import json, shutil, sys
from pathlib import Path
dst, src = Path(sys.argv[1]), Path(sys.argv[2])
have = json.loads((dst / "pages.json").read_text(encoding="utf-8"))
books = {p["book"] for p in have}
for p in json.loads((src / "pages.json").read_text(encoding="utf-8")):
    if len(have) >= 25:
        break
    if p["book"] in books or not (src / f"{p['id']}.png").exists():
        continue
    for ext in (".png", ".gt.txt", ".wikitext"):
        if (src / f"{p['id']}{ext}").exists():
            shutil.move(str(src / f"{p['id']}{ext}"), str(dst / f"{p['id']}{ext}"))
    have.append(p); books.add(p["book"])
(dst / "pages.json").write_text(json.dumps(have, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
shutil.rmtree(src)
print(f"{dst}: {len(have)} pages")
PY
}

$F --out $B/old-books-more --seed 12 --index-search "$OLD" --exclude-books $USED
python3 tools/ia_book_pages.py --pages $B/old-books-more && merge $B/old-books $B/old-books-more
$F --out $B/contemporary-lowres-more --seed 14 --index-search "$NEW" --exclude-books $USED
python3 tools/ia_book_pages.py --pages $B/contemporary-lowres-more && merge $B/contemporary-lowres $B/contemporary-lowres-more

# sharper source images for the 300 DPI set (archive.org keeps 600 ppi originals)
rm -f $B/contemporary-books/*.png
python3 tools/ia_book_pages.py --pages $B/contemporary-books --width 3200

rm -rf benchmarks/icon-style/old-books-72dpi benchmarks/icon-style/contemporary-books-300dpi benchmarks/icon-style/contemporary-lowres-96dpi
python3 tools/make_dpi_set.py $B/old-books --out benchmarks/icon-style/old-books-72dpi --dpi 72 --font-pt 12
python3 tools/make_dpi_set.py $B/contemporary-books --out benchmarks/icon-style/contemporary-books-300dpi --dpi 300 --font-pt 12
python3 tools/make_dpi_set.py $B/contemporary-lowres --out benchmarks/icon-style/contemporary-lowres-96dpi --dpi 96 --font-pt 12
echo "ICON BOOK SETS TOPPED UP"
