#!/bin/bash
# Download the four ICON-style test sets (25 pages each) from Tamil Wikisource.
set -e
cd "$(dirname "$0")/../.."
B=benchmarks/icon-style/source
F="python3 tools/fetch_wikisource.py --pages 25 --min-chars 250 --delay ${DELAY:-15}"
$F --out $B/old-newspapers --per-book 2 --seed 1 \
   --index-search 'intitle:"திராவிட நாடு" insource:"Type=journal"' --exclude-books examples/wikisource-pages.json books/books.json
$F --out $B/old-books --per-book 1 --seed 2 \
   --index-search 'insource:"Type=book" insource:/Year *= *(18[0-9][0-9]|19[0-5][0-9])/' --exclude-books examples/wikisource-pages.json books/books.json
$F --out $B/contemporary-books --per-book 1 --seed 3 \
   --index-search 'insource:"Type=book" insource:/Year *= *20[0-9][0-9]/' --exclude-books examples/wikisource-pages.json books/books.json
$F --out $B/contemporary-lowres --per-book 1 --seed 4 \
   --index-search 'insource:"Type=book" insource:/Year *= *20[0-9][0-9]/' \
   --exclude-books examples/wikisource-pages.json books/books.json $B/contemporary-books/pages.json
echo "ALL SETS DOWNLOADED"
