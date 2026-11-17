"""Tiny, dependency-free reader for the parts of TrueType/OpenType fonts we need.

Reads: which code points a font maps (cmap), which scripts its GSUB table
supports, its names (name table) and whether it is a variable font (fvar).
Supports .ttf, .otf and .ttc/.otc collections.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path


class FontParseError(ValueError):
    pass


@dataclass
class FaceInfo:
    path: Path
    index: int
    family: str = ""
    style: str = ""
    full_name: str = ""
    codepoints: set[int] = field(default_factory=set)
    gsub_scripts: set[str] = field(default_factory=set)
    has_gsub: bool = False
    is_variable: bool = False


def _u16(b: bytes, o: int) -> int:
    return struct.unpack_from(">H", b, o)[0]


def _u32(b: bytes, o: int) -> int:
    return struct.unpack_from(">I", b, o)[0]


def _table_dir(data: bytes, offset: int) -> dict[str, tuple[int, int]]:
    num_tables = _u16(data, offset + 4)
    tables = {}
    for i in range(num_tables):
        rec = offset + 12 + 16 * i
        tag = data[rec : rec + 4].decode("latin-1")
        tables[tag] = (_u32(data, rec + 8), _u32(data, rec + 12))
    return tables


def _parse_cmap(data: bytes, off: int) -> set[int]:
    num = _u16(data, off + 2)
    subtables = []
    for i in range(num):
        rec = off + 4 + 8 * i
        pid, eid, sub_off = _u16(data, rec), _u16(data, rec + 2), _u32(data, rec + 4)
        subtables.append((pid, eid, off + sub_off))
    # Prefer full-repertoire Unicode tables, then BMP Unicode tables.
    def rank(st):
        pid, eid, _ = st
        if (pid, eid) == (3, 10) or (pid == 0 and eid in (4, 6)):
            return 0
        if (pid, eid) == (3, 1) or pid == 0:
            return 1
        return 9

    cps: set[int] = set()
    for pid, eid, so in sorted(subtables, key=rank):
        if rank((pid, eid, so)) == 9:
            continue
        fmt = _u16(data, so)
        if fmt == 4:
            seg2 = _u16(data, so + 6)
            ends = so + 14
            starts = ends + seg2 + 2
            deltas = starts + seg2
            ranges = deltas + seg2
            for s in range(seg2 // 2):
                end = _u16(data, ends + 2 * s)
                start = _u16(data, starts + 2 * s)
                delta = _u16(data, deltas + 2 * s)
                ro = _u16(data, ranges + 2 * s)
                for c in range(start, end + 1):
                    if c == 0xFFFF:
                        continue
                    if ro == 0:
                        gid = (c + delta) & 0xFFFF
                    else:
                        gpos = ranges + 2 * s + ro + 2 * (c - start)
                        if gpos + 2 > len(data):
                            continue
                        gid = _u16(data, gpos)
                        if gid:
                            gid = (gid + delta) & 0xFFFF
                    if gid:
                        cps.add(c)
        elif fmt == 12:
            ngroups = _u32(data, so + 12)
            for g in range(ngroups):
                go = so + 16 + 12 * g
                start, end, gid = _u32(data, go), _u32(data, go + 4), _u32(data, go + 8)
                for c in range(start, end + 1):
                    if gid + (c - start):
                        cps.add(c)
        else:
            continue
        if cps:
            break
    return cps


def _parse_gsub_scripts(data: bytes, off: int) -> set[str]:
    script_list = off + _u16(data, off + 4)
    count = _u16(data, script_list)
    tags = set()
    for i in range(count):
        rec = script_list + 2 + 6 * i
        tags.add(data[rec : rec + 4].decode("latin-1"))
    return tags


def _parse_names(data: bytes, off: int) -> dict[int, str]:
    count = _u16(data, off + 2)
    str_base = off + _u16(data, off + 4)
    found: dict[int, tuple[int, str]] = {}
    for i in range(count):
        rec = off + 6 + 12 * i
        pid, eid, lang, nid, length, soff = struct.unpack_from(">HHHHHH", data, rec)
        raw = data[str_base + soff : str_base + soff + length]
        if pid == 3 or pid == 0:
            try:
                text = raw.decode("utf-16-be")
            except UnicodeDecodeError:
                continue
            prio = 0 if (pid == 3 and lang == 0x409) else 1
        elif pid == 1 and eid == 0:
            text = raw.decode("mac_roman", errors="replace")
            prio = 2
        else:
            continue
        if nid not in found or prio < found[nid][0]:
            found[nid] = (prio, text.strip())
    return {nid: text for nid, (_, text) in found.items()}


def _parse_face(data: bytes, offset: int, path: Path, index: int) -> FaceInfo:
    tables = _table_dir(data, offset)
    face = FaceInfo(path=path, index=index)
    if "cmap" in tables:
        face.codepoints = _parse_cmap(data, tables["cmap"][0])
    if "GSUB" in tables:
        face.has_gsub = True
        try:
            face.gsub_scripts = _parse_gsub_scripts(data, tables["GSUB"][0])
        except struct.error:
            face.gsub_scripts = set()
    if "name" in tables:
        names = _parse_names(data, tables["name"][0])
        face.family = names.get(16) or names.get(1, "")
        face.style = names.get(17) or names.get(2, "")
        face.full_name = names.get(4) or f"{face.family} {face.style}".strip()
    face.is_variable = "fvar" in tables
    if not face.full_name:
        face.full_name = path.stem if index == 0 else f"{path.stem} #{index}"
    return face


def read_faces(path: Path) -> list[FaceInfo]:
    """Return one FaceInfo per face in the font file."""
    data = path.read_bytes()
    if len(data) < 12:
        raise FontParseError("file too small to be a font")
    tag = data[:4]
    try:
        if tag == b"ttcf":
            n = _u32(data, 8)
            return [_parse_face(data, _u32(data, 12 + 4 * i), path, i) for i in range(n)]
        if tag in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
            return [_parse_face(data, 0, path, 0)]
    except (struct.error, IndexError) as exc:
        raise FontParseError(f"corrupt font: {exc}") from exc
    raise FontParseError("not a TrueType/OpenType font (WOFF/Type1 are not supported)")
