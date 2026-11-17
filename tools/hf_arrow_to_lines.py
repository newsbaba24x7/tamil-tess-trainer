#!/usr/bin/env python3
"""Turn a Hugging Face `datasets` .arrow file (an image column and a text column) into
line images with ground truth: <out>/<00001>.png + <00001>.gt.txt, the layout that
`tamtrain lines` and tesstrain read.

    python3 tools/hf_arrow_to_lines.py data-00000-of-00001.arrow --out benchmarks/ranlp2025/lines

Reads the Arrow IPC stream format directly, so pyarrow is not needed. Supports image
columns stored as struct<bytes, path> (how `datasets` stores Image features) and
string/large_string text columns, without compression.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

# Arrow type ids (Schema.fbs "Type" union)
BINARY, UTF8, STRUCT, LARGE_BINARY, LARGE_UTF8 = 4, 5, 13, 19, 20


class Table:
    """Minimal flatbuffers table reader."""

    def __init__(self, buf: bytes, pos: int):
        self.buf, self.pos = buf, pos
        self.vt = pos - struct.unpack_from("<i", buf, pos)[0]
        self.vt_len = struct.unpack_from("<H", buf, self.vt)[0]

    def _off(self, idx: int) -> int:
        o = 4 + 2 * idx
        return struct.unpack_from("<H", self.buf, self.vt + o)[0] if o < self.vt_len else 0

    def scalar(self, idx: int, fmt: str, default=0):
        off = self._off(idx)
        return struct.unpack_from(fmt, self.buf, self.pos + off)[0] if off else default

    def table(self, idx: int) -> "Table | None":
        off = self._off(idx)
        if not off:
            return None
        p = self.pos + off
        return Table(self.buf, p + struct.unpack_from("<I", self.buf, p)[0])

    def vector(self, idx: int) -> tuple[int, int]:
        off = self._off(idx)
        if not off:
            return 0, 0
        p = self.pos + off
        p += struct.unpack_from("<I", self.buf, p)[0]
        return p + 4, struct.unpack_from("<I", self.buf, p)[0]

    def string(self, idx: int) -> str:
        start, n = self.vector(idx)
        return self.buf[start:start + n].decode("utf-8") if n else ""

    def tables(self, idx: int) -> list["Table"]:
        start, n = self.vector(idx)
        out = []
        for i in range(n):
            p = start + 4 * i
            out.append(Table(self.buf, p + struct.unpack_from("<I", self.buf, p)[0]))
        return out


def messages(data: bytes):
    pos = 0
    while pos + 8 <= len(data):
        first = struct.unpack_from("<I", data, pos)[0]
        if first == 0xFFFFFFFF:
            meta_len = struct.unpack_from("<i", data, pos + 4)[0]
            pos += 8
        else:  # pre-0.15 format without continuation marker
            meta_len = first
            pos += 4
        if meta_len == 0:
            return
        meta = data[pos:pos + meta_len]
        pos += meta_len
        msg = Table(meta, struct.unpack_from("<I", meta, 0)[0])
        header_type = msg.scalar(1, "<B")
        body_len = msg.scalar(3, "<q")
        yield header_type, msg.table(2), data[pos:pos + body_len]
        pos += body_len


def flatten(fields: list[Table], prefix: str = "") -> list[tuple[str, int]]:
    """Depth-first (name, type id) list, the order of field nodes and buffers in a batch."""
    out = []
    for f in fields:
        name = prefix + f.string(0)
        out.append((name, f.scalar(2, "<B")))
        out += flatten(f.tables(5), name + ".")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arrow", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--image-column", default="image")
    ap.add_argument("--text-column", default="text")
    args = ap.parse_args()

    data = args.arrow.read_bytes()
    columns: list[tuple[str, int]] = []
    args.out.mkdir(parents=True, exist_ok=True)
    row = 0
    for header_type, header, body in messages(data):
        if header_type == 1:                       # Schema
            columns = flatten(header.tables(1))
            continue
        if header_type != 3:                       # only RecordBatch carries rows
            continue
        if header.table(3) is not None:
            raise SystemExit("compressed Arrow batches are not supported")
        n_rows = header.scalar(0, "<q")
        bstart, bcount = header.vector(2)
        buffers = [struct.unpack_from("<qq", header.buf, bstart + 16 * i) for i in range(bcount)]
        cols, k = {}, 0
        for name, tid in columns:
            if tid == STRUCT:
                k += 1                              # validity only
            elif tid in (BINARY, UTF8, LARGE_BINARY, LARGE_UTF8):
                (oo, ol), (do, dl) = buffers[k + 1], buffers[k + 2]
                fmt = "<q" if tid in (LARGE_BINARY, LARGE_UTF8) else "<i"
                size = struct.calcsize(fmt)
                offs = [struct.unpack_from(fmt, body, oo + size * i)[0] for i in range(n_rows + 1)]
                cols[name] = [body[do + offs[i]:do + offs[i + 1]] for i in range(n_rows)]
                k += 3
            else:
                raise SystemExit(f"column {name}: unsupported Arrow type id {tid}")
        images = cols.get(args.image_column + ".bytes") or cols.get(args.image_column)
        texts = cols.get(args.text_column)
        if images is None or texts is None:
            raise SystemExit(f"columns not found; available: {sorted(cols)}")
        for img, txt in zip(images, texts):
            row += 1
            ext = ".png" if img[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg" if img[:2] == b"\xff\xd8" else ".img"
            (args.out / f"{row:05d}{ext}").write_bytes(img)
            (args.out / f"{row:05d}.gt.txt").write_text(txt.decode("utf-8") + "\n", encoding="utf-8")
    print(f"{row} rows written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
