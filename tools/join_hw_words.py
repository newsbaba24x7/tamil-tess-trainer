#!/usr/bin/env python3
"""Join handwritten word images into lines, so a model learns handwriting and word spaces together.

A model trained on single words (one word per image) never learns to output a space. This joins
3-6 word images (image + .gt.txt, e.g. from tools/iiit_hw_words.py) side by side into one line:
each word scaled so the dense middle band of its writing has the same height, centred on a common
line with a little up-and-down jitter, separated by a word gap of 0.3-0.8 x that height. Each
word is used once; the text is the words joined by single spaces.

  python3 tools/join_hw_words.py hw-words/train --out hw-lines/train
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageOps

BODY = 34      # height of the dense middle band of the writing, in pixels


def body_band(a: np.ndarray) -> tuple[int, int]:
    """Rows of the dense middle band: rows with at least 30% of the busiest row's ink."""
    ink = (a < 160).sum(axis=1)
    if ink.max() == 0:
        return 0, a.shape[0]
    rows = np.nonzero(ink >= 0.3 * ink.max())[0]
    return int(rows[0]), int(rows[-1]) + 1


def load_word(png: Path) -> tuple[Image.Image, float]:
    """The word scaled to a BODY-high middle band, paper made white; returns (image, band centre y)."""
    im = Image.open(png).convert("L")
    a = np.asarray(im)
    top, bottom = body_band(a)
    scale = BODY / max(8, bottom - top)
    scale = min(max(scale, 0.5), 2.0)
    im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    im = im.point(lambda v: 255 if v > 225 else v)
    return im, (top + bottom) / 2 * scale


def join(words: list[tuple[Image.Image, float]], rng: random.Random) -> Image.Image:
    pad = 10
    gaps = [rng.uniform(0.3, 0.8) * BODY for _ in words[1:]]
    jitter = [rng.uniform(-0.08, 0.08) * BODY for _ in words]
    above = max(c + j for (im, c), j in zip(words, jitter))
    below = max(im.height - c - j for (im, c), j in zip(words, jitter))
    width = sum(im.width for im, _ in words) + sum(gaps) + 2 * pad
    canvas = Image.new("L", (int(width) + 1, int(above + below) + 2 * pad), 255)
    x = pad
    for k, ((im, c), j) in enumerate(zip(words, jitter)):
        y = int(pad + above - c - j)
        region = canvas.crop((int(x), y, int(x) + im.width, y + im.height))
        canvas.paste(ImageChops.darker(region, im), (int(x), y))
        x += im.width + (gaps[k] if k < len(gaps) else 0)
    return ImageOps.autocontrast(canvas, cutoff=0.2)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help="folder of word images + .gt.txt")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--min-words", type=int, default=3)
    ap.add_argument("--max-words", type=int, default=6)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    pairs = []
    for gt in sorted(a.src.glob("*.gt.txt")):
        png = gt.with_name(gt.name[: -len(".gt.txt")] + ".png")
        text = gt.read_text(encoding="utf-8").strip()
        if png.exists() and text:
            pairs.append((png, text))
    rng = random.Random(a.seed)
    rng.shuffle(pairs)
    a.out.mkdir(parents=True, exist_ok=True)
    i = n = 0
    while i < len(pairs):
        k = rng.randint(a.min_words, a.max_words)
        group = pairs[i:i + k]
        i += k
        img = join([load_word(p) for p, _ in group], rng)
        base = a.out / f"hwline_{n:06d}"
        img.save(str(base) + ".png")
        Path(str(base) + ".gt.txt").write_text(" ".join(t for _, t in group) + "\n", encoding="utf-8")
        n += 1
    print(f"{n} lines from {len(pairs)} words -> {a.out}")


if __name__ == "__main__":
    main()
