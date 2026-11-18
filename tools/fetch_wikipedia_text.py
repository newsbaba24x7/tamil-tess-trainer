#!/usr/bin/env python3
"""Sample Tamil Wikipedia article text, for training lines that mix English words into Tamil.

Tamil Wikipedia often writes an English name after its Tamil form, as in "கர்லோ ஸ்கார்ப்பா
(Carlo Scarpa)". Book text has little of this. The tool reads random articles through the
Wikipedia API (the opening section of each, 20 per request) and keeps their sentences, one per line.

Test text must never become training text: every sentence that shares a run of four words with
any test set (--exclude-text: .gt.txt folders, .txt or .jsonl files) is dropped.

    python3 tools/fetch_wikipedia_text.py --out text-sources/tawiki-sample.txt --articles 5000 \\
        --exclude-text scans/wikisource benchmarks/wikisource-test-lines benchmarks/tamil-ocr-benchmark \\
        benchmarks/ranlp2025/lines benchmarks/icon-style/source

Text: Tamil Wikipedia contributors, CC BY-SA 4.0 (https://ta.wikipedia.org).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tamtrain.tamil import normalize  # noqa: E402

API = "https://ta.wikipedia.org/w/api.php"
UA = "tamtrain/2.0 (https://github.com/newsbaba24x7/tamil-tess-trainer; Tamil OCR training data) python-urllib"
TAMIL = re.compile(r"[஀-௿]")


def api(**params) -> dict:
    params.update(format="json", formatversion="2")
    data = urllib.parse.urlencode(params).encode()
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(API, data=data, headers={"User-Agent": UA}), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 15))
    raise RuntimeError("unreachable")


def words4(text: str) -> set[tuple[str, ...]]:
    w = text.split()
    return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}


def test_text(paths: list[Path]) -> set[tuple[str, ...]]:
    grams: set[tuple[str, ...]] = set()
    for p in paths:
        files = [p] if p.is_file() else list(p.rglob("*.gt.txt")) + list(p.rglob("*.jsonl"))
        for f in files:
            if f.suffix == ".jsonl":
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        r = json.loads(line)
                        grams |= words4(normalize(r.get("ground_truth") or r.get("text") or ""))
            else:
                grams |= words4(normalize(f.read_text(encoding="utf-8")))
    return grams


def sentences(extract: str) -> list[str]:
    out = []
    for para in extract.split("\n"):
        para = para.strip()
        if not para or para.startswith("=="):
            continue
        for s in re.split(r"(?<=[.!?])\s+", para):
            s = normalize(" ".join(s.split()))
            if len(s) >= 20 and TAMIL.search(s):
                out.append(s)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--articles", type=int, default=5000)
    ap.add_argument("--exclude-text", type=Path, nargs="+", default=[], help="test text that must not be trained on")
    ap.add_argument("--delay", type=float, default=0.5)
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    banned = test_text(args.exclude_text)
    print(f"{len(banned)} four-word runs from test text are banned")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    seen_titles: set[str] = set()
    kept = dropped = 0
    with open(args.out, "w", encoding="utf-8") as fh:
        while len(seen_titles) < args.articles:
            # whole-article extracts come one per request; opening sections come 20 at a time,
            # and openings are where Tamil Wikipedia gives English names in brackets
            d = api(action="query", generator="random", grnnamespace=0, grnlimit=20, prop="extracts",
                    explaintext=1, exintro=1, exlimit=20)
            for p in d.get("query", {}).get("pages", []):
                if p["title"] in seen_titles or not p.get("extract"):
                    continue
                seen_titles.add(p["title"])
                for s in sentences(p["extract"]):
                    if words4(s) & banned:
                        dropped += 1
                        continue
                    fh.write(s + "\n")
                    kept += 1
            if len(seen_titles) % 500 < 20:
                print(f"  {len(seen_titles)} articles, {kept} sentences", flush=True)
            time.sleep(args.delay)
    mixed = sum(1 for line in open(args.out, encoding="utf-8") if re.search(r"[A-Za-z]{2,}", line))
    print(f"{kept} sentences from {len(seen_titles)} articles in {args.out} ({mixed} with English words); "
          f"{dropped} dropped for sharing text with a test set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
