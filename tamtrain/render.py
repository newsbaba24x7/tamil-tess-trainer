"""Render text lines with a font into degraded, scan-like line images (ground truth)."""

from __future__ import annotations

import io
import math
import random
from dataclasses import dataclass, field
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps, features

from .fonts import apply_variation
from .tamil import clusters
from .util import Progress, TamTrainError


def check_shaping_support() -> None:
    if not features.check("raqm"):
        raise TamTrainError(
            "Pillow was built without libraqm, so it cannot shape Tamil text (vowel signs and "
            "ligatures would render wrongly).\nInstall libraqm and fribidi (Debian/Ubuntu: "
            "sudo apt install libraqm0 libfribidi0) and use a Pillow build with raqm support."
        )


@dataclass
class RenderOptions:
    min_size: int = 28          # font size in pixels (em height)
    max_size: int = 64
    clean_ratio: float = 0.3    # share of images with no degradation at all
    degrade: bool = True
    min_word_gap: float = 0.25  # word spaces narrower than this (in em) are widened
    justify_ratio: float = 0.3  # share of lines with wider, justified-looking word spaces
    tracking_ratio: float = 0.12  # share of lines with letter-spacing inside words


@dataclass
class Task:
    out_base: str               # path without extension
    text: str
    font_path: str
    font_index: int
    seed: int
    variation: str | None = None
    features: list[str] = field(default_factory=list)  # OpenType features, e.g. old letter shapes


_font_cache: dict[tuple, ImageFont.FreeTypeFont] = {}


def _font(path: str, index: int, size: int, variation: str | None = None) -> ImageFont.FreeTypeFont:
    key = (path, index, size, variation)
    if key not in _font_cache:
        if len(_font_cache) > 200:
            _font_cache.clear()
        font = ImageFont.truetype(path, size, index=index, layout_engine=ImageFont.Layout.RAQM)
        apply_variation(font, variation)
        _font_cache[key] = font
    return _font_cache[key]


def render_clean(text: str, font: ImageFont.FreeTypeFont, ink: int = 0, paper: int = 255,
                 pad_x: int = 12, pad_y: int = 8, features: list[str] | None = None) -> Image.Image:
    """Render a line as the font lays it out (used for previews and font checks)."""
    left, top, right, bottom = font.getbbox(text, language="ta", features=features)
    w, h = right - left, bottom - top
    if w <= 0 or h <= 0:
        raise ValueError("nothing rendered")
    img = Image.new("L", (w + 2 * pad_x, h + 2 * pad_y), paper)
    ImageDraw.Draw(img).text((pad_x - left, pad_y - top), text, font=font, fill=ink, language="ta",
                             features=features)
    return img


def render_spaced(text: str, font: ImageFont.FreeTypeFont, *, word_gap: float, tracking: float = 0.0,
                  ink: int = 0, paper: int = 255, pad_x: int = 12, pad_y: int = 8,
                  features: list[str] | None = None, jitter: random.Random | None = None) -> Image.Image:
    """Render a line word by word with a chosen gap between words (pixels) and optional
    letter-spacing inside words (pixels between letter clusters).

    Some fonts have very narrow spaces (0.18 em); trained on them, a model learns that a small
    gap means a new word and splits words wherever a scan leaves a gap. Drawing each word with
    a minimum gap, and sometimes spacing the letters of a word, teaches the difference."""
    pieces: list[tuple[float, str]] = []      # (pen x, text) on a common baseline
    x = 0.0
    for wi, word in enumerate(text.split(" ")):
        if wi:
            x += word_gap * (jitter.uniform(0.92, 1.08) if jitter else 1.0)
        parts = clusters(word) if tracking > 0 else [word]
        for pi, part in enumerate(parts):
            if pi:
                x += tracking
            if part:
                pieces.append((x, part))
                x += font.getlength(part, language="ta", features=features)
    if not pieces:
        raise ValueError("nothing rendered")
    boxes = [font.getbbox(t, language="ta", features=features, anchor="ls") for _, t in pieces]
    x0 = min(px + b[0] for (px, _), b in zip(pieces, boxes))
    x1 = max(px + b[2] for (px, _), b in zip(pieces, boxes))
    y0 = min(b[1] for b in boxes)
    y1 = max(b[3] for b in boxes)
    w, h = math.ceil(x1 - x0), y1 - y0
    if w <= 0 or h <= 0:
        raise ValueError("nothing rendered")
    img = Image.new("L", (w + 2 * pad_x, h + 2 * pad_y), paper)
    draw = ImageDraw.Draw(img)
    for px, t in pieces:
        draw.text((pad_x - x0 + px, pad_y - y0), t, font=font, fill=ink, language="ta", features=features,
                  anchor="ls")
    return img


# ----------------------------------------------------------------------------- degradation


def _noise(size: tuple[int, int], rng: random.Random) -> Image.Image:
    """Uniform noise from our own random generator, so images are reproducible."""
    w, h = max(1, size[0]), max(1, size[1])
    return Image.frombytes("L", (w, h), rng.randbytes(w * h))


def _field(size: tuple[int, int], cell: int, rng: random.Random) -> Image.Image:
    """Smooth, low-frequency random field (0-255) with features about `cell` pixels wide."""
    small = _noise((size[0] // cell + 2, size[1] // cell + 2), rng)
    return small.resize(size, Image.BICUBIC)


def _quantile_threshold(img: Image.Image, keep: float) -> int:
    """Grey level above which the brightest `keep` share of pixels lies."""
    hist = img.histogram()
    total, acc = sum(hist), 0
    for level in range(255, -1, -1):
        acc += hist[level]
        if acc >= keep * total:
            return level
    return 0


def _warp(img: Image.Image, amp: float, period: float, phase: float, fill: int) -> Image.Image:
    """Bend the baseline along a gentle sine wave (page curl near the binding)."""
    w, h = img.size
    n = max(4, w // 24)
    mesh = []
    for k in range(n):
        xa, xb = k * w // n, (k + 1) * w // n
        da = amp * math.sin(2 * math.pi * xa / period + phase)
        db = amp * math.sin(2 * math.pi * xb / period + phase)
        mesh.append(((xa, 0, xb, h), (xa, da, xa, h + da, xb, h + db, xb, db)))
    return img.transform(img.size, Image.MESH, mesh, resample=Image.BICUBIC, fillcolor=fill)


def degrade(img: Image.Image, rng: random.Random, size: int, paper: int = 255) -> tuple[Image.Image, list[str]]:
    """Apply a random mix of scan and print artefacts.

    Geometry: rotation, warped baseline. Ink: spread, bleed that fills small loops, faded print,
    broken strokes, uneven ink. Paper: texture and stains, show-through from the other side, dust.
    Capture: low resolution, blur, sensor noise, binarisation, JPEG. Effects that remove ink are
    limited to larger text so small marks such as the pulli (்) survive."""
    applied = []
    # geometry
    if rng.random() < 0.3:
        angle = rng.uniform(-0.8, 0.8) if rng.random() < 0.8 else rng.uniform(-1.6, 1.6)
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=paper)
        applied.append(f"rot{angle:+.1f}")
    if rng.random() < 0.15:
        amp = rng.uniform(0.02, 0.06) * size
        img = _warp(img, amp, rng.uniform(4, 12) * size, rng.uniform(0, 2 * math.pi), paper)
        applied.append(f"warp{amp:.1f}")
    # ink
    r = rng.random()
    if size >= 44 and r < 0.10:
        img = img.filter(ImageFilter.MinFilter(3))  # thicker (ink spread)
        applied.append("bold")
    elif size >= 34 and r < 0.20:
        blur = rng.uniform(0.6, 1.2)
        level = rng.randint(150, 200)  # dark threshold after blur: strokes swell, small loops fill
        img = img.filter(ImageFilter.GaussianBlur(blur)).point(lambda v, t=level: 0 if v < t else 255)
        applied.append(f"bleed{level}")
    elif size >= 52 and r < 0.28:
        img = img.filter(ImageFilter.MaxFilter(3))  # thinner (faded print)
        applied.append("thin")
    if size >= 32 and rng.random() < 0.18:
        cell = max(2, size // 16)  # blobs about half a stroke wide: strokes break, dots survive
        blobs = _field(img.size, cell, rng)
        level = _quantile_threshold(blobs, rng.uniform(0.04, 0.10))
        holes = blobs.point(lambda v, t=level, p=paper: p if v >= t else 0)
        img = ImageChops.lighter(img, holes)   # ink under a hole becomes paper; paper is unchanged
        applied.append("broken")
    if rng.random() < 0.2:
        fade = _field(img.size, max(8, size), rng).point(lambda v, lo=rng.uniform(0.4, 0.75): int(255 * (lo + (1 - lo) * v / 255)))
        img = ImageOps.invert(ImageChops.multiply(ImageOps.invert(img), fade))
        applied.append("uneven")
    # paper
    if rng.random() < 0.12:
        stain = _field(img.size, max(12, size * 2), rng).point(lambda v, d=rng.randint(10, 35): int(d * v / 255))
        img = ImageChops.subtract(img, stain)
        applied.append("paper")
    if rng.random() < 0.08:
        ghost = ImageOps.invert(ImageOps.mirror(img)).point(lambda v, k=rng.uniform(0.06, 0.14): int(v * k))
        shift = rng.randint(-size // 3, size // 3)
        ghost = ImageChops.offset(ghost, rng.randint(0, img.width), shift)
        img = ImageChops.subtract(img, ghost)
        applied.append("showthrough")
    if rng.random() < 0.15:
        draw = ImageDraw.Draw(img)
        rmax = 1.0 if size < 40 else 1.6
        for _ in range(rng.randint(3, 15)):
            x, y, rr = rng.uniform(0, img.width), rng.uniform(0, img.height), rng.uniform(0.5, rmax)
            draw.ellipse((x - rr, y - rr, x + rr, y + rr), fill=rng.randint(0, 90))
        applied.append("dust")
    # capture
    if rng.random() < 0.25:
        scale = rng.uniform(0.5, 0.8) if size < 44 or rng.random() < 0.6 else rng.uniform(0.35, 0.5)
        small = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
        img = small.resize(img.size, Image.BICUBIC)
        applied.append(f"lowres{scale:.2f}")
    if rng.random() < 0.35:
        blur = rng.uniform(0.3, 1.0 if size < 40 else 1.4)
        img = img.filter(ImageFilter.GaussianBlur(blur))
        applied.append(f"blur{blur:.1f}")
    if rng.random() < 0.3:
        sigma = rng.uniform(4, 22)
        noise = _noise(img.size, rng).point(lambda v, k=sigma / 74: int(128 + (v - 128) * k))
        img = ImageChops.add(img, noise, 1.0, -128)
        applied.append(f"noise{sigma:.0f}")
    if rng.random() < 0.15:
        level = rng.randint(120, 160)
        img = img.point(lambda v, t=level: 255 if v > t else 0)
        applied.append("binary")
    elif rng.random() < 0.20:
        buf = io.BytesIO()
        q = rng.randint(25, 70)
        img.save(buf, "JPEG", quality=q)
        img = Image.open(io.BytesIO(buf.getvalue())).convert("L")
        applied.append(f"jpeg{q}")
    return img, applied


# ----------------------------------------------------------------------------- tasks


def render_task(task: Task, opts: RenderOptions) -> dict | None:
    rng = random.Random(task.seed)
    size = rng.randint(opts.min_size, opts.max_size)
    clean = not opts.degrade or rng.random() < opts.clean_ratio
    ink = 0 if clean else rng.randint(0, 70)
    paper = 255 if clean else rng.randint(200, 255)
    feats = task.features or None
    info: dict = {}
    try:
        font = _font(task.font_path, task.font_index, size, task.variation)
        space = font.getlength(" ")
        gap = max(space, opts.min_word_gap * size)
        if rng.random() < opts.justify_ratio:
            gap *= rng.uniform(1.1, 1.9)
            info["spacing"] = "justified"
        tracking = 0.0
        if rng.random() < opts.tracking_ratio:
            tracking = rng.uniform(0.03, 0.12) * size
            gap = max(gap, 3 * tracking + 0.2 * size)   # word gaps stay clearly wider than letter gaps
            info["spacing"] = f"tracking{tracking / size:.2f}"
        img = render_spaced(task.text, font, word_gap=gap, tracking=tracking, ink=ink, paper=paper,
                            pad_x=rng.randint(6, 24), pad_y=rng.randint(6, 14), features=feats, jitter=rng)
    except (OSError, ValueError):
        return None
    applied: list[str] = []
    if not clean:
        img, applied = degrade(img, rng, size, paper)
    img.save(task.out_base + ".png", optimize=False)
    with open(task.out_base + ".gt.txt", "w", encoding="utf-8") as fh:
        fh.write(task.text + "\n")
    if task.features:
        info["features"] = task.features
    return {"size": size, "degradations": applied, **info}


def _worker(args):
    task, opts = args
    return task, render_task(task, opts)


def render_all(tasks: list[Task], opts: RenderOptions, jobs: int) -> list[tuple[Task, dict | None]]:
    for t in tasks:
        Path(t.out_base).parent.mkdir(parents=True, exist_ok=True)
    progress = Progress(len(tasks), "rendered")
    results = []
    with Pool(jobs) as pool:
        for i, res in enumerate(pool.imap_unordered(_worker, [(t, opts) for t in tasks], chunksize=16), 1):
            results.append(res)
            progress.update(i)
    return results
