#!/usr/bin/env python3
"""Step 11 - Rebuild tam_v3's real scanned TEST lines for evaluation only (never for training).

Same method as tools/crop_lines.py in tamil-tess-trainer v3.0.0, limited to the test split:
each page image is downloaded once from Wikimedia (15 s apart, as Wikimedia blocks fast
downloads; same User-Agent and retries), boxes are scaled if the page arrives at another size,
and each line is cut with the same padding (sideways max(4, h/6), vertically 2 px).

  python3 -I 11_fetch_real_test.py tam_v3-real-lines.jsonl.gz --out real_test
Output: real_test/pages/<page>.png, real_test/lines/<id>.png + .gt.txt, real_test/fetch_log.tsv
(page, url, bytes, HTTP result, seconds). Re-running skips pages already downloaded.
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
            code = getattr(exc, "code", None)
            if attempt == tries - 1 or code in (401, 403, 404):
                raise
            time.sleep(delay); delay *= 2


def crop_line(page, box):
    x, y, w, h = box
    pad = max(4, h // 6)
    return page.crop((max(0, x - pad), max(0, y - 2), min(page.width, x + w + pad), min(page.height, y + h + 2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list"); ap.add_argument("--out", required=True)
    ap.add_argument("--delay", type=float, default=15.0, help="seconds between Wikimedia downloads")
    a = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    out = Path(a.out); (out / "pages").mkdir(parents=True, exist_ok=True); (out / "lines").mkdir(exist_ok=True)
    rows = [json.loads(l) for l in gzip.open(a.list, "rt", encoding="utf-8") if l.strip()]
    pages = collections.OrderedDict()
    for r in rows:
        if r["split"] == "test":
            pages.setdefault(r["page"], []).append(r)
    log = open(out / "fetch_log.tsv", "a", encoding="utf-8")
    total, stats = 0, collections.Counter()
    print(f"START {time.strftime('%H:%M:%S', time.gmtime())} UTC: {len(pages)} pages")
    for n, (pid, lines) in enumerate(pages.items(), 1):
        dest = out / "pages" / f"{pid}.png"
        w0, h0 = lines[0]["page_size"]
        if dest.exists():
            page = Image.open(dest).convert("L")
        else:
            url = lines[0]["image_urls"][0]; t = time.time()
            try:
                data, status = get(url)
                page = Image.open(io.BytesIO(data)).convert("L")
                if page.width > w0:
                    page = page.resize((w0, round(page.height * w0 / page.width)), Image.LANCZOS)
                page.save(dest); total += len(data)
                log.write(f"{pid}\t{url}\t{len(data)}\t{status}\t{time.time() - t:.1f}\n"); log.flush()
            except Exception as exc:  # noqa: BLE001
                log.write(f"{pid}\t{url}\t0\tFAILED {exc}\t{time.time() - t:.1f}\n"); log.flush()
                stats["lines on missing pages"] += len(lines); print(f"  {pid}: {exc}")
                time.sleep(a.delay); continue
            time.sleep(a.delay)
        sx, sy = page.width / w0, page.height / h0
        for r in lines:
            x, y, w, h = r["box"]
            crop_line(page, [round(x * sx), round(y * sy), round(w * sx), round(h * sy)]).save(out / "lines" / f"{r['id']}.png")
            (out / "lines" / f"{r['id']}.gt.txt").write_text(r["text"] + "\n", encoding="utf-8")
            stats["test lines"] += 1
        if (sx, sy) != (1, 1):
            stats["pages rescaled"] += 1
        if n % 10 == 0:
            print(f"  {time.strftime('%H:%M:%S', time.gmtime())} {n}/{len(pages)} pages, {total / 1e6:.1f} MB downloaded")
    print(f"END {time.strftime('%H:%M:%S', time.gmtime())} UTC: " + ", ".join(f"{k}: {v}" for k, v in stats.items()) + f", {total / 1e6:.1f} MB downloaded this run")


if __name__ == "__main__":
    main()
