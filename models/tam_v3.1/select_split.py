#!/usr/bin/env python3
"""Choose a model variant on one half of the evaluation lines and report it on the other half,
so the reported numbers are not the ones used for the choice.

Half S (selection) = even line numbers, half R (report) = odd line numbers.
Rule: among candidates whose CER on S is no worse than the baseline in every Tamil-text category
(A, B, C, D), in punctuation (P) and on every font, pick the lowest overall CER on S.

  python3 -I select_split.py BASELINE_NAME RESULT_DIR... (each holds <model>.jsonl from 10_evaluate.py)
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module
ev = import_module("10_evaluate")

base, dirs = sys.argv[1], sys.argv[2:]
models = {}
for d in dirs:
    for f in Path(d).glob("*.jsonl"):
        models.setdefault(f.stem, [json.loads(l) for l in open(f, encoding="utf-8")])


def cer(rows):
    e = sum(ev.lev(r["ref"], r["hyp"]) for r in rows); n = sum(len(r["ref"]) for r in rows)
    return 100 * e / max(n, 1)


def table(half):
    out = {}
    for name, rows in models.items():
        rs = [r for r in rows if int(r["id"][2:]) % 2 == half]
        cats = sorted({r["category"] for r in rs}); fonts = sorted({r["font"] for r in rs})
        out[name] = {"overall": cer(rs), **{c: cer([r for r in rs if r["category"] == c]) for c in cats},
                     **{f: cer([r for r in rs if r["font"] == f]) for f in fonts}}
    return out


S, Rp = table(0), table(1)
guard = [k for k in S[base] if k[:2] in ("A_", "B_", "C_", "D_", "P_") or " w" in k]
ok = [m for m in S if m != base and all(S[m][k] <= S[base][k] + 1e-9 for k in guard)]
print("selection half: candidates with no regression vs", base, "->", {m: round(S[m]["overall"], 2) for m in ok})
rejected = {m: [k for k in guard if S[m][k] > S[base][k]] for m in S if m not in ok and m != base}
print("rejected (regressing keys):", rejected)
if not ok:
    sys.exit("no candidate passes")
best = min(ok, key=lambda m: S[m]["overall"])
print(f"\nCHOSEN on selection half: {best}\n\nReport half (not used for the choice), CER %:")
print(f"| key | {base} | {best} |\n|---|---:|---:|")
for k in Rp[base]:
    print(f"| {k} | {Rp[base][k]:.2f} | {Rp[best][k]:.2f} |")
