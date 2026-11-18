#!/bin/bash
# Download more proofread Wikisource books with archive.org page images, as real training lines.
# Resumable: every step skips work already done. Run from the tamil-tess-trainer folder.
set -e
cd "$(dirname "$0")/.."
OUT=${OUT:-books-more}
EXCLUDE="examples/wikisource-pages.json scans/wikisource/pages.json books/books.json benchmarks/icon-style/source/*/pages.json"
echo "START $(date +%H:%M:%S)"
[ -f $OUT/pool.json ] || python3 tools/wikisource_pool.py scan --out $OUT
[ -f $OUT/books.json ] || python3 tools/wikisource_pool.py pick --out $OUT --books ${BOOKS:-400} --pages-per-book 24 --exclude-books $EXCLUDE
python3 tools/wikisource_pool.py texts --out $OUT
echo "TEXTS DONE $(date +%H:%M:%S)"
python3 tools/ia_book_pages.py $OUT --workers 4 --book-workers ${BOOK_WORKERS:-3}
echo "IMAGES DONE $(date +%H:%M:%S)"
