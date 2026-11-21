#!/usr/bin/env python3
"""Handwritten Tamil words from IIIT-INDIC-HW-WORDS (CVIT, IIIT Hyderabad; CC BY 4.0) for Tesseract.

The official Tamil file (ta.zip, 5.1 GB) holds train.zip, val.zip and test.zip plus label files
(train.txt: "train/1.jpg, 7424", the number being a 0-based line of vocab.txt). The scans are
600 DPI word images of about 1570 x 290 pixels, mostly white margin.

  fetch    download chosen splits from ta.zip with HTTP range requests (resumable, in parallel)
  convert  write word images as greyscale PNG + .gt.txt (tesstrain layout), cropped to the ink
           and scaled to a fixed height, from a split zip or from a folder of images + .gt.txt

  python3 tools/iiit_hw_words.py fetch train val --out downloads/iiit-hw
  python3 tools/iiit_hw_words.py convert downloads/iiit-hw/train.zip --labels downloads/iiit-hw/train.txt \\
      --vocab downloads/iiit-hw/vocab.txt --out hw-words/train
  python3 tools/iiit_hw_words.py convert benchmarks/iiit-hw-tamil/test --out hw-words/test-cropped

Training lines are made with --psm 13 (the whole image is the line), so cropping matters: an
uncropped word sits in a small corner of the line the network sees.
"""
from __future__ import annotations

import argparse
import io
import itertools
import os
import struct
import sys
import threading
import time
import urllib.request
import zipfile
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

URL = "https://cvit.iiit.ac.in/images/Projects/iiit-indic-hw-words/ta.zip"
UA = {"User-Agent": "tamtrain/3.0"}
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")


# ----------------------------------------------------------------------------- fetch

class HTTPFile(io.RawIOBase):
    """A remote file read with HTTP range requests (enough for zipfile to read the directory)."""

    def __init__(self, url: str):
        self.url, self.pos = url, 0
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers=UA), timeout=60) as r:
            self.size = int(r.headers["Content-Length"])

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        end = min(self.size, self.pos + n) - 1
        req = urllib.request.Request(self.url, headers={**UA, "Range": f"bytes={self.pos}-{end}"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        self.pos += len(data)
        return data

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def _fetch_part(url, start, end, path, stats, k):
    for attempt in range(30):
        have = path.stat().st_size if path.exists() else 0
        if start + have > end:
            return
        req = urllib.request.Request(url, headers={**UA, "Range": f"bytes={start + have}-{end}"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r, open(path, "ab") as out:
                while chunk := r.read(1 << 20):
                    out.write(chunk)
                    stats[k] = path.stat().st_size
        except OSError as e:          # network hiccup: carry on from where it stopped
            print(f"    part {k}: {e!r}, retrying", flush=True)
            time.sleep(min(60, 5 * (attempt + 1)))
    raise SystemExit(f"part {k} of {url} failed")


def fetch_member(url: str, info: zipfile.ZipInfo, data_offset: int, out: Path, parts: int) -> None:
    """Download one member's compressed bytes in parallel ranges, then inflate it to out."""
    if out.exists() and out.stat().st_size == info.file_size:
        print(f"    {out} already complete")
        return
    size = info.compress_size
    step = -(-size // parts)
    pieces, stats, threads = [], {}, []
    for k in range(parts):
        lo = data_offset + k * step
        hi = min(data_offset + size, lo + step) - 1
        p = out.with_name(f"{out.name}.c.part{k}")
        pieces.append((p, hi - lo + 1))
        stats[k] = p.stat().st_size if p.exists() else 0
        t = threading.Thread(target=_fetch_part, args=(url, lo, hi, p, stats, k), daemon=True)
        t.start()
        threads.append(t)
    t0, done0 = time.time(), sum(stats.values())
    while any(t.is_alive() for t in threads):
        time.sleep(30)
        done = sum(stats.values())
        rate = (done - done0) / max(1.0, time.time() - t0)
        left = f"~{(size - done) / rate / 60:.0f} min left" if rate else ""
        print(f"    {time.strftime('%H:%M:%S')}  {info.filename}: {done / 1e9:.2f}/{size / 1e9:.2f} GB  "
              f"{rate / 1e6:.1f} MB/s  {left}", flush=True)
    for p, n in pieces:
        if p.stat().st_size != n:
            raise SystemExit(f"{p}: {p.stat().st_size} bytes, expected {n}")
    if info.compress_type == zipfile.ZIP_STORED:
        inflate = None
    elif info.compress_type == zipfile.ZIP_DEFLATED:
        inflate = zlib.decompressobj(-15)
    else:
        raise SystemExit(f"{info.filename}: compression type {info.compress_type} not supported")
    tmp = out.with_name(out.name + ".tmp")
    crc = 0
    with open(tmp, "wb") as fh:
        for p, _ in pieces:
            with open(p, "rb") as f:
                while chunk := f.read(16 << 20):
                    data = inflate.decompress(chunk) if inflate else chunk
                    crc = zlib.crc32(data, crc)
                    fh.write(data)
        if inflate:
            data = inflate.flush()
            crc = zlib.crc32(data, crc)
            fh.write(data)
    if crc != info.CRC or tmp.stat().st_size != info.file_size:
        raise SystemExit(f"{info.filename}: checksum or size mismatch; delete {tmp} and the parts and retry")
    tmp.replace(out)
    for p, _ in pieces:
        p.unlink()
    print(f"    {out} ({out.stat().st_size / 1e9:.2f} GB, checksum OK)")


def cmd_fetch(a) -> None:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    remote = HTTPFile(a.url)
    z = zipfile.ZipFile(remote)
    names = ["vocab.txt"] + [f"{s}.txt" for s in a.splits] + [f"{s}.zip" for s in a.splits]
    for name in names:
        info = z.getinfo(name)
        if name.endswith(".txt"):
            (out / name).write_bytes(z.read(name))
            print(f"    {out / name}")
            continue
        remote.seek(info.header_offset)
        header = remote.read(30)
        n, m = struct.unpack("<HH", header[26:30])
        fetch_member(a.url, info, info.header_offset + 30 + n + m, out / name, a.parts)


# ----------------------------------------------------------------------------- convert

def otsu(a: np.ndarray) -> int:
    hist = np.bincount(a.ravel(), minlength=256).astype(float)
    w = np.cumsum(hist)
    mu = np.cumsum(hist * np.arange(256))
    total, mu_t = w[-1], mu[-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        between = (mu_t * w - mu * total) ** 2 / (w * (total - w))
    return int(np.nanargmax(between))


def form_lines(ink: np.ndarray) -> np.ndarray:
    """Pixels of the printed box around each word on the scanned forms: long straight horizontal
    runs anywhere, long vertical runs near the left and right edges. Slightly skewed or broken
    lines are found too (one pixel of slack across the line, 8% gaps along it)."""
    from scipy import ndimage
    h, w = ink.shape
    out = np.zeros_like(ink)
    for axis, length in ((1, max(60, w // 4)), (0, max(40, int(h * 0.6)))):
        thick = ndimage.maximum_filter1d(ink, 3, axis=1 - axis)
        full = ndimage.uniform_filter1d(thick.astype(np.float32), length, axis=axis) >= 0.92
        run = ndimage.maximum_filter1d(full, length, axis=axis) & thick
        if axis == 0:                          # vertical: only the box's sides
            run[:, int(w * 0.15):int(w * 0.85)] = False
        out |= run
    return ndimage.binary_dilation(out, iterations=2)


def ink_box(ink: np.ndarray, min_area: int) -> tuple[int, int, int, int] | None:
    """Bounding box (x0, y0, x1, y1) of the handwriting: dark connected parts, without specks of
    dust and parts lying along the image edge."""
    from scipy import ndimage
    if not ink.any():
        return None
    lab, n = ndimage.label(ink, structure=np.ones((3, 3), bool))
    if n == 0:
        return None
    objs = ndimage.find_objects(lab)
    areas = ndimage.sum_labels(ink, lab, index=np.arange(1, n + 1))
    h, w = ink.shape
    edge = 3
    boxes = []
    for sl, area in zip(objs, areas):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if area < min_area:
            continue
        if y1 <= edge or y0 >= h - edge or x1 <= edge or x0 >= w - edge:
            continue
        if (y1 - y0 <= 4 and (y0 < edge or y1 > h - edge)) or (x1 - x0 <= 4 and (x0 < edge or x1 > w - edge)):
            continue                  # a thin line along an edge
        boxes.append((x0, y0, x1, y1))
    if not boxes:
        return None
    b = np.array(boxes)
    return int(b[:, 0].min()), int(b[:, 1].min()), int(b[:, 2].max()), int(b[:, 3].max())


def prepare(img: Image.Image, height: int, pad: float, min_area: int) -> Image.Image:
    """Greyscale word image: form lines painted white, cropped to the ink with a margin,
    contrast stretched, scaled to `height` pixels."""
    a = np.array(img.convert("L"))
    ink = a < min(otsu(a), 200)
    lines = form_lines(ink)
    if lines.any():
        a[lines] = int(np.median(a[~ink])) if (~ink).any() else 255
        ink &= ~lines
    grey = Image.fromarray(a)
    box = ink_box(ink, min_area)
    if box:
        x0, y0, x1, y1 = box
        p = max(4, round(pad * (y1 - y0)))
        grey = grey.crop((max(0, x0 - p), max(0, y0 - p), min(a.shape[1], x1 + p), min(a.shape[0], y1 + p)))
    grey = ImageOps.autocontrast(grey, cutoff=0.5)
    if height and grey.height != height:
        w = max(1, round(grey.width * height / grey.height))
        grey = grey.resize((w, height), Image.LANCZOS)
    return grey


def _done(out_png: Path) -> bool:
    return out_png.exists() and out_png.with_name(out_png.name[:-4] + ".gt.txt").exists()


def _convert_one(job):
    src, data, out_png, gt_text, opts = job
    if _done(out_png):
        return None
    try:
        with Image.open(io.BytesIO(data) if data is not None else src) as im:
            im = prepare(im, opts["height"], opts["pad"], opts["min_area"])
        tmp = out_png.with_name(out_png.name + ".part")
        im.save(tmp, format="PNG", optimize=True)
        tmp.replace(out_png)
        out_png.with_name(out_png.name[:-4] + ".gt.txt").write_text(gt_text + "\n", encoding="utf-8")
    except Exception as e:      # a damaged image: skip it, say which
        return f"{src}: {e}"
    return None


def jobs_from_zip(zpath: Path, labels: Path, vocab: Path, out: Path, opts: dict):
    words = vocab.read_text(encoding="utf-8").split("\n")
    with zipfile.ZipFile(zpath) as z:
        names = set(z.namelist())
        for line in labels.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            path, idx = (x.strip() for x in line.rsplit(",", 1))
            member = path if path in names else next((n for n in (path.split("/", 1)[-1],) if n in names), None)
            if member is None:
                print(f"    not in zip: {path}", file=sys.stderr)
                continue
            num = int(Path(path).stem)
            text = words[int(idx)].strip()
            if not text:
                continue
            out_png = out / f"hw_{num:06d}.png"
            if _done(out_png):     # converted on an earlier run
                yield (member, None, out_png, text, opts)
            else:
                yield (f"{zpath.name}:{member}", z.read(member), out_png, text, opts)


def jobs_from_dir(src: Path, out: Path, opts: dict):
    for gt in sorted(src.glob("*.gt.txt")):
        stem = gt.name[: -len(".gt.txt")]
        img = next((gt.with_name(stem + e) for e in IMAGE_EXTS if gt.with_name(stem + e).exists()), None)
        if img is None:
            continue
        yield (img, None, out / f"{stem}.png", gt.read_text(encoding="utf-8").strip(), opts)


def cmd_convert(a) -> None:
    src, out = Path(a.src), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    opts = {"height": a.height, "pad": a.pad, "min_area": a.min_area}
    if src.is_dir():
        jobs = jobs_from_dir(src, out, opts)
    else:
        if not (a.labels and a.vocab):
            raise SystemExit("a zip needs --labels and --vocab")
        jobs = jobs_from_zip(src, Path(a.labels), Path(a.vocab), out, opts)
    errors, n, t0 = [], 0, time.time()
    with ProcessPoolExecutor(a.jobs) as ex:
        # Executor.map takes all its input at once; in batches, only a few images are in memory.
        while batch := list(itertools.islice(jobs, 2000)):
            for err in ex.map(_convert_one, batch, chunksize=32):
                n += 1
                if err:
                    errors.append(err)
                if n % 5000 == 0:
                    print(f"    {time.strftime('%H:%M:%S')}  {n} words ({n / (time.time() - t0):.0f}/s)",
                          flush=True)
    print(f"    {n} words -> {out}" + (f"; {len(errors)} skipped (first: {errors[0]})" if errors else ""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="download splits from the official ta.zip")
    f.add_argument("splits", nargs="+", choices=["train", "val", "test"])
    f.add_argument("--out", default="downloads/iiit-hw")
    f.add_argument("--url", default=URL)
    f.add_argument("--parts", type=int, default=6, help="parallel range requests per file")
    c = sub.add_parser("convert", help="word images -> cropped greyscale PNG + .gt.txt")
    c.add_argument("src", help="a split zip (train.zip) or a folder of images + .gt.txt")
    c.add_argument("--labels", help="train.txt / val.txt / test.txt (with a zip)")
    c.add_argument("--vocab", help="vocab.txt (with a zip)")
    c.add_argument("--out", required=True)
    c.add_argument("--height", type=int, default=64, help="output height in pixels (0: keep the size)")
    c.add_argument("--pad", type=float, default=0.12, help="white margin, as a share of the ink height")
    c.add_argument("--min-area", type=int, default=25, help="ignore dark specks smaller than this (pixels)")
    c.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    cmd_fetch(a) if a.cmd == "fetch" else cmd_convert(a)


if __name__ == "__main__":
    main()
