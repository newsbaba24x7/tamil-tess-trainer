#!/usr/bin/env python3
"""Read the licence fields embedded in each font file (OpenType 'name' table) and its
character coverage, so every rendering font is documented from the file itself.

  python3 -I fonts_audit.py FONT_FILE... > fonts_audit.json

Name IDs: 0 copyright, 1 family, 2 subfamily, 5 version, 13 licence text, 14 licence URL.
Coverage via fc-query. Nothing is downloaded.
"""
import hashlib, json, struct, subprocess, sys

WANT = {0: "copyright", 1: "family", 2: "style", 5: "version", 13: "licence", 14: "licence_url"}
PROBES = {"tamil_numerals": "௦௧௨௩௪௫௬௭௮௯௰௱௲", "tamil_symbols": "௳௴௵௶௷௸௹௺ௐ",
          "latin": "AZaz", "rupee_euro_pound": "₹€£", "quotes_dashes": "‘’“”–—…"}


def name_table(data):
    num = struct.unpack(">H", data[4:6])[0]
    for i in range(num):
        tag, _, off, _ = struct.unpack(">4sIII", data[12 + 16 * i: 28 + 16 * i])
        if tag == b"name":
            break
    else:
        return {}
    _, count, soff = struct.unpack(">HHH", data[off:off + 6])
    out = {}
    for i in range(count):
        pid, eid, lid, nid, ln, so = struct.unpack(">HHHHHH", data[off + 6 + 12 * i: off + 18 + 12 * i])
        if nid not in WANT:
            continue
        raw = data[off + soff + so: off + soff + so + ln]
        if pid == 3 or pid == 0:
            txt = raw.decode("utf-16-be", "replace")
        else:
            txt = raw.decode("latin-1", "replace")
        if WANT[nid] not in out or (pid == 3 and lid == 0x409):
            out[WANT[nid]] = " ".join(txt.split())
    return out


def coverage(path):
    cs = subprocess.run(["fc-query", "-f", "%{charset}", path], capture_output=True, text=True).stdout
    ranges = []
    for part in cs.split():
        a, _, b = part.partition("-")
        ranges.append((int(a, 16), int(b or a, 16)))
    has = lambda ch: any(a <= ord(ch) <= b for a, b in ranges)
    return {k: "".join(c for c in v if has(c)) or "-" for k, v in PROBES.items()}


rows = []
for p in sys.argv[1:]:
    data = open(p, "rb").read()
    rows.append({"file": p, "sha256": hashlib.sha256(data).hexdigest(), **name_table(data), **coverage(p)})
json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)
