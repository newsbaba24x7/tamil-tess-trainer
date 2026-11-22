#!/usr/bin/env python3
"""Choose the release candidate using real scans AND synthetic lines, without using the halves
that are reported.

Rule (fixed before the full real-scan results were seen, 2026-11-22 02:12 UTC):
  1. real-scan guard, even pages:   CER <= baseline and WER <= baseline
  2. synthetic guard, even lines:   CER in categories A, B, C, D <= baseline
  3. objective:                     lowest synthetic CER on even lines
Then report odd pages (real) and odd lines (synthetic).

  python3 -I select_real.py BASELINE --real DIR... --synth DIR...
Model names must match across the result folders (<name>.jsonl).
"""
import json, sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
lev = import_module("10_evaluate").lev
args = sys.argv[1:]; base = args[0]
real_dirs = args[args.index("--real") + 1: args.index("--synth")]; synth_dirs = args[args.index("--synth") + 1:]


def load(dirs):
    out = {}
    for d in dirs:
        for f in Path(d).glob("*.jsonl"):
            out.setdefault(f.stem, [json.loads(l) for l in open(f, encoding="utf-8")])
    return out


R, S = load(real_dirs), load(synth_dirs)
pages = sorted({r["id"].rsplit("_", 1)[0] for r in R[base]}); order = {p: k for k, p in enumerate(pages)}
rhalf = lambda r: order[r["id"].rsplit("_", 1)[0]] % 2
shalf = lambda r: int(r["id"][2:]) % 2


def rates(rows):
    ce = sum(lev(r["ref"], r["hyp"]) for r in rows); cn = sum(len(r["ref"]) for r in rows)
    we = sum(lev(r["ref"].split(), r["hyp"].split()) for r in rows); wn = sum(len(r["ref"].split()) for r in rows)
    return 100 * ce / max(cn, 1), 100 * we / max(wn, 1)


def table(models, half):
    t = {}
    for m in models:
        if m not in R or m not in S:
            continue
        rr = [r for r in R[m] if rhalf(r) == half]; ss = [r for r in S[m] if shalf(r) == half]
        t[m] = {"real": rates(rr), "synth": rates(ss)[0],
                **{c: rates([r for r in ss if r["category"] == c])[0] for c in ("A_tamil", "B_vowel_signs", "C_grantha", "D_pulli")}}
    return t


names = sorted(set(R) & set(S))
T0 = table(names, 0); b = T0[base]
print(f"{'candidate':12} real CER  real WER  synth CER   A     B     C     D    guard")
for m, v in sorted(T0.items(), key=lambda kv: kv[1]["synth"]):
    ok_r = v["real"][0] <= b["real"][0] and v["real"][1] <= b["real"][1]
    ok_s = all(v[c] <= b[c] for c in ("A_tamil", "B_vowel_signs", "C_grantha", "D_pulli"))
    v["pass"] = ok_r and ok_s and m != base
    print(f"{m:12} {v['real'][0]:7.2f} {v['real'][1]:8.2f} {v['synth']:9.2f} {v['A_tamil']:5.2f} {v['B_vowel_signs']:5.2f} {v['C_grantha']:5.2f} {v['D_pulli']:5.2f}  "
          + ("PASS" if v["pass"] else ("baseline" if m == base else ("real" if not ok_r else "") + (" synth" if not ok_s else ""))))
passing = [m for m, v in T0.items() if v["pass"]]
if not passing:
    print("\nNo candidate passes both guards on the selection halves.")
    sys.exit(0)
best = min(passing, key=lambda m: T0[m]["synth"])
T1 = table([base, best], 1)
print(f"\nCHOSEN: {best}\nReport halves (not used for the choice): real CER/WER {base} {T1[base]['real'][0]:.2f}/{T1[base]['real'][1]:.2f} -> "
      f"{best} {T1[best]['real'][0]:.2f}/{T1[best]['real'][1]:.2f}; synthetic CER {T1[base]['synth']:.2f} -> {T1[best]['synth']:.2f}")
