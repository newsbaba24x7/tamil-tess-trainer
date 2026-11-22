#!/usr/bin/env python3
"""Step 14 - Rebuild real scanned lines of tam_v3 (any split, optional page list).

Same method as tools/crop_lines.py in tamil-tess-trainer v3.0.0: each page image is downloaded
once (same User-Agent and retries; archive.org 1 s apart, Wikimedia 15 s apart), boxes are scaled
if the page arrives at another size, lines are cut with the same padding. The page image is
deleted right after its lines are cut unless --keep-pages.

  python3 -I 14_fetch_real_lines.py tam_v3-real-lines.jsonl.gz --split dev --out real_dev
  python3 -I 14_fetch_real_lines.py tam_v3-real-lines.jsonl.gz --split train --pages train_pages_round4.tsv --out real_train
Output: OUT/lines/<id>.png + .gt.txt, OUT/fetch_log.tsv. Re-running skips pages already done.
"""
import argparse, collections, gzip, io, json, sys, time, urllib.error, urllib.request
from pathlib import Path

from PIL import Image

UA = {"User-Agent": "tamtrain/2.0 (https://github.com/newsbaba24x7/tamil-tess-trainer; Tamil OCR training data) python-urllib"}


def get(url, tries=4):
    delay = 5.0
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return r.read(), r.status
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt == tries - 1 or getattr(exc, "code", None) in (401, 403, 404):
                raise
            time.sleep(delay); delay *= 2


def crop_line(page, box):
    x, y, w, h = box
    pad = max(4, h // 6)
    return page.crop((max(0, x - pad), max(0, y - 2), min(page.width, x + w + pad), min(page.height, y + h + 2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list"); ap.add_argument("--split", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--pages", help="TSV whose first column lists the page ids to fetch")
    ap.add_argument("--keep-pages", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    out = Path(a.out); (out / "lines").mkdir(parents=True, exist_ok=True); (out / "pages").mkdir(exist_ok=True)
    want = None
    if a.pages:
        want = {l.split("\t")[0] for l in open(a.pages, encoding="utf-8") if l.strip() and not l.startswith("page_id")}
    pages = collections.OrderedDict()
    for l in gzip.open(a.list, "rt", encoding="utf-8"):
        r = json.loads(l)
        if r["split"] == a.split and (want is None or r["page"] in want):
            pages.setdefault(r["page"], []).append(r)
    done = {l.split("\t")[0] for l in open(out / "fetch_log.tsv", encoding="utf-8")} if (out / "fetch_log.tsv").exists() else set()
    log = open(out / "fetch_log.tsv", "a", encoding="utf-8")
    total, stats = 0, collections.Counter()
    print(f"START {time.strftime('%H:%M:%S', time.gmtime())} UTC: {len(pages)} pages, {sum(map(len, pages.values()))} lines")
    for n, (pid, lines) in enumerate(pages.items(), 1):
        if all((out / "lines" / f"{r['id']}.gt.txt").exists() for r in lines):   # done earlier or by a parallel run
            stats["lines"] += len(lines); continue
        w0, h0 = lines[0]["page_size"]
        slow = "wikimedia.org" in lines[0]["image_urls"][0]
        page = None
        for url in lines[0]["image_urls"]:
            t = time.time()
            try:
                data, status = get(url)
                page = Image.open(io.BytesIO(data)).convert("L"); total += len(data)
                log.write(f"{pid}\t{url}\t{len(data)}\t{status}\t{time.time() - t:.1f}\n"); log.flush()
                break
            except Exception as exc:  # noqa: BLE001
                log.write(f"{pid}\t{url}\t0\tFAILED {exc}\t{time.time() - t:.1f}\n"); log.flush()
            finally:
                time.sleep(15.0 if slow else 1.0)
        if page is None:
            stats["lines on missing pages"] += len(lines); continue
        if page.width > w0:
            page = page.resize((w0, round(page.height * w0 / page.width)), Image.LANCZOS)
        if a.keep_pages:
            page.save(out / "pages" / f"{pid}.png")
        sx, sy = page.width / w0, page.height / h0
        for r in lines:
            x, y, w, h = r["box"]
            crop_line(page, [round(x * sx), round(y * sy), round(w * sx), round(h * sy)]).save(out / "lines" / f"{r['id']}.png")
            (out / "lines" / f"{r['id']}.gt.txt").write_text(r["text"] + "\n", encoding="utf-8")
            stats["lines"] += 1
        if (sx, sy) != (1, 1):
            stats["pages rescaled"] += 1
        if n % 50 == 0:
            print(f"  {time.strftime('%H:%M:%S', time.gmtime())} {n}/{len(pages)} pages, {total / 1e6:.1f} MB")
    print(f"END {time.strftime('%H:%M:%S', time.gmtime())} UTC: " + ", ".join(f"{k}: {v}" for k, v in stats.items()) + f", {total / 1e6:.1f} MB this run")


if __name__ == "__main__":
    main()
