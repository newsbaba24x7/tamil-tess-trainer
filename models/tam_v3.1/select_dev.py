#!/usr/bin/env python3
"""Round-4 candidate choice on tam_v3's REAL DEV split (the real test split is not used).

Rule, fixed 2026-11-22 before any round-4 result existed:
  guard 1  real dev:          CER <= baseline and WER <= baseline
  guard 2  synthetic, even lines: categories A, B, C, D <= baseline
  objective                   lowest real-dev WER
  python3 -I select_dev.py BASELINE --dev DIR... --synth DIR...
"""
import json, sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
lev = import_module("10_evaluate").lev
a = sys.argv[1:]; base = a[0]
dev_dirs = a[a.index("--dev") + 1: a.index("--synth")]; syn_dirs = a[a.index("--synth") + 1:]


def load(dirs):
    out = {}
    for d in dirs:
        for f in Path(d).glob("*.jsonl"):
            out.setdefault(f.stem, [json.loads(l) for l in open(f, encoding="utf-8")])
    return out


def rates(rows):
    ce = sum(lev(r["ref"], r["hyp"]) for r in rows); cn = sum(len(r["ref"]) for r in rows)
    we = sum(lev(r["ref"].split(), r["hyp"].split()) for r in rows); wn = sum(len(r["ref"].split()) for r in rows)
    return 100 * ce / max(cn, 1), 100 * we / max(wn, 1)


D, S = load(dev_dirs), load(syn_dirs)
T = {}
for m in sorted(set(D) & set(S)):
    ss = [r for r in S[m] if int(r["id"][2:]) % 2 == 0]
    T[m] = {"dev": rates(D[m]), **{c: rates([r for r in ss if r["category"] == c])[0] for c in ("A_tamil", "B_vowel_signs", "C_grantha", "D_pulli")}}
b = T[base]
print(f"{'candidate':10} dev CER  dev WER   A     B     C     D   result")
best = None
for m, v in sorted(T.items(), key=lambda kv: kv[1]["dev"][1]):
    g1 = v["dev"][0] <= b["dev"][0] and v["dev"][1] <= b["dev"][1]
    g2 = all(v[c] <= b[c] for c in ("A_tamil", "B_vowel_signs", "C_grantha", "D_pulli"))
    ok = g1 and g2 and m != base
    if ok and best is None:
        best = m
    print(f"{m:10} {v['dev'][0]:7.2f} {v['dev'][1]:8.2f} {v['A_tamil']:5.2f} {v['B_vowel_signs']:5.2f} {v['C_grantha']:5.2f} {v['D_pulli']:5.2f}  "
          + ("baseline" if m == base else ("PASS" if ok else ("fails real dev " if not g1 else "") + ("fails synthetic" if not g2 else ""))))
print(f"\nCHOSEN: {best or 'none passes'}")
