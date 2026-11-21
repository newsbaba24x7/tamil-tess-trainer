#!/usr/bin/env python3
"""Cut text lines out of photos annotated in LabelMe format (one JSON per photo, a box and the
text of each line), e.g. the Appen Tamil document photos on Kaggle.

Each box becomes <out>/<kind>_<photo>_<nn>.png + .gt.txt, where <kind> is the photo's folder
(NEWSPAPERS, NOTES...). Boxes whose text contains ### (unreadable) are left out, and so are lines
with fewer than --min-tamil Tamil letters (English words and numbers only). groups.json in <out>
maps each line to its kind, so `tamtrain lines` reports every kind separately.

  python3 tools/labelme_lines.py downloads/appen/extracted --out benchmarks/appen-tamil-photos/lines
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageOps


def tamil_letters(text: str) -> int:
    return sum("஀" <= c <= "௿" for c in text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pad", type=int, default=4, help="pixels added around each box")
    ap.add_argument("--min-tamil", type=int, default=3)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    groups, kept, skipped = {}, 0, {"###": 0, "not Tamil": 0, "empty": 0}
    for js in sorted(a.src.rglob("*.json")):
        ann = json.loads(js.read_text(encoding="utf-8"))
        img_path = js.parent / ann["imagePath"]
        kind = re.sub(r"[^a-z0-9]+", "-", js.parent.name.lower()).strip("-")
        with Image.open(img_path) as im:
            im = im.convert("RGB")
            if im.size != (ann["imageWidth"], ann["imageHeight"]):
                im = ImageOps.exif_transpose(im)        # boxes refer to the upright photo
            W, H = im.size
            photo = re.sub(r"[^A-Za-z0-9]+", "_", img_path.stem)
            for n, shape in enumerate(ann["shapes"]):
                text = " ".join((shape.get("label") or "").split())
                if not text:
                    skipped["empty"] += 1
                    continue
                if "###" in text:
                    skipped["###"] += 1
                    continue
                if tamil_letters(text) < a.min_tamil:
                    skipped["not Tamil"] += 1
                    continue
                xs = [p[0] for p in shape["points"]]
                ys = [p[1] for p in shape["points"]]
                box = (max(0, int(min(xs)) - a.pad), max(0, int(min(ys)) - a.pad),
                       min(W, int(max(xs)) + a.pad + 1), min(H, int(max(ys)) + a.pad + 1))
                if box[2] - box[0] < 8 or box[3] - box[1] < 8:
                    continue
                stem = f"{kind}_{photo}_{n:03d}"
                im.crop(box).convert("L").save(a.out / f"{stem}.png")
                (a.out / f"{stem}.gt.txt").write_text(text + "\n", encoding="utf-8")
                groups[stem] = kind
                kept += 1
    (a.out / "groups.json").write_text(json.dumps(groups, indent=1), encoding="utf-8")
    print(f"{kept} lines -> {a.out}; left out: {skipped}")


if __name__ == "__main__":
    main()
