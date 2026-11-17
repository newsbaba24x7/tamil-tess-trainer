#!/usr/bin/env python3
"""Rebuild V2's real scanned lines (training, check and test) from the published line list.

The line images are not redistributed. The release has `tam_v2-real-lines.jsonl.gz`: for every
line, its proofread text (Tamil Wikisource, CC BY-SA 4.0), where its page image can be downloaded,
and the line's box on that page. This tool downloads each page once and cuts the lines:

    python3 tools/crop_lines.py tam_v2-real-lines.jsonl.gz --out real-lines
    python3 tools/crop_lines.py tam_v2-real-lines.jsonl.gz --out real-lines --split test

Output: <out>/<split>/<id>.png + .gt.txt for the splits train, dev and test, ready for
`tamtrain train --extra-gt` and `tamtrain lines`. Page images are kept in <out>/pages, so the
tool can be stopped and run again. Training and check pages come from archive.org; test pages
come from Wikimedia, which blocks fast downloads, so they are fetched slowly (`--delay`).
A page served at another size than when the lines were cut has its boxes scaled to match.
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ia_book_pages import get  # noqa: E402
from page_lines import crop_line  # noqa: E402


def fetch_page(urls: list[str], width: int, dest: Path, delay: float) -> Image.Image | None:
    if dest.exists():
        return Image.open(dest).convert("L")
    for url in urls:
        try:
            im = Image.open(io.BytesIO(get(url))).convert("L")
        except Exception as exc:  # noqa: BLE001
            print(f"  {url[:90]}: {exc}")
            continue
        finally:
            time.sleep(delay)
        if im.width > width:      # page services sometimes ignore the requested width
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest)
        return im
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("list", type=Path, help="tam_v2-real-lines.jsonl(.gz)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--split", nargs="*", help="only these splits (train, dev, test)")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between archive.org downloads")
    ap.add_argument("--wikimedia-delay", type=float, default=15.0, help="seconds between Wikimedia downloads")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    opener = gzip.open if args.list.suffix == ".gz" else open
    with opener(args.list, "rt", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if args.split:
        rows = [r for r in rows if r["split"] in args.split]
    by_page: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_page[r["page"]].append(r)
    stats: Counter = Counter()
    for n, (page_id, lines) in enumerate(by_page.items(), 1):
        first = lines[0]
        w0, h0 = first["page_size"]
        slow = any("wikimedia.org" in u for u in first["image_urls"])
        page = fetch_page(first["image_urls"], w0, args.out / "pages" / f"{page_id}.png",
                          args.wikimedia_delay if slow else args.delay)
        if page is None:
            stats["lines on missing pages"] += len(lines)
            continue
        sx, sy = page.width / w0, page.height / h0
        for r in lines:
            x, y, w, h = r["box"]
            box = [round(x * sx), round(y * sy), round(w * sx), round(h * sy)]
            out = args.out / r["split"]
            out.mkdir(parents=True, exist_ok=True)
            crop_line(page, box).save(out / f"{r['id']}.png")
            (out / f"{r['id']}.gt.txt").write_text(r["text"] + "\n", encoding="utf-8")
            stats[r["split"]] += 1
        if (sx, sy) != (1, 1):
            stats["pages rescaled"] += 1
        if n % 50 == 0:
            print(f"  {n}/{len(by_page)} pages")
    print(", ".join(f"{k}: {v}" for k, v in stats.items()) or "nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
