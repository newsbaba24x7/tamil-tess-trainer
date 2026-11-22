#!/usr/bin/env python3
"""Paired bootstrap 95% confidence intervals for the CER difference (model - baseline),
per category (10,000 resamples, seed 1).

Synthetic lines (ids ev#####) are resampled line by line; halves = even / odd line numbers.
Real scanned lines (ids <page>_<n>) are resampled by PAGE (cluster bootstrap), because lines of
one page share print quality; halves = even / odd page in sorted page order.

  python3 -I bootstrap_ci.py BASE.jsonl MODEL.jsonl [--half 0|1] [--metric cer|wer]
"""
import json, random, sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
lev = import_module("10_evaluate").lev
base = {r["id"]: r for r in map(json.loads, open(sys.argv[1], encoding="utf-8"))}
mod = {r["id"]: r for r in map(json.loads, open(sys.argv[2], encoding="utf-8"))}
half = int(sys.argv[sys.argv.index("--half") + 1]) if "--half" in sys.argv else None
metric = sys.argv[sys.argv.index("--metric") + 1] if "--metric" in sys.argv else "cer"
real = not next(iter(base)).startswith("ev")
page = (lambda i: i.rsplit("_", 1)[0]) if real else (lambda i: i)
order = {p: k for k, p in enumerate(sorted({page(i) for i in base}))}
side = (lambda i: order[page(i)] % 2) if real else (lambda i: int(i[2:]) % 2)
ids = [i for i in base if half is None or side(i) == half]


def counts(r):
    if metric == "wer":
        return lev(r["ref"].split(), r["hyp"].split()), len(r["ref"].split())
    return lev(r["ref"], r["hyp"]), len(r["ref"])


rows = {}
for i in ids:
    eb, n = counts(base[i]); em, _ = counts(mod[i])
    rows[i] = (eb, em, n, base[i]["category"], page(i))
rng = random.Random(1)
unit = "pages" if real else "lines"
print(f"| category | lines | baseline {metric.upper()} | model {metric.upper()} | difference (95% CI, resampling {unit}), points |\n|---|---:|---:|---:|---|")
for cat in ["ALL"] + sorted({r[3] for r in rows.values()}):
    sel = [rows[i] for i in ids if cat == "ALL" or rows[i][3] == cat]
    eb, em, n = sum(r[0] for r in sel), sum(r[1] for r in sel), sum(r[2] for r in sel)
    groups = {}
    for r in sel:
        g = groups.setdefault(r[4], [0, 0, 0]); g[0] += r[0]; g[1] += r[1]; g[2] += r[2]
    G = list(groups.values()); diffs = []
    for _ in range(10000):
        smp = [G[rng.randrange(len(G))] for _ in G]
        nn = sum(g[2] for g in smp)
        diffs.append(100 * (sum(g[1] for g in smp) - sum(g[0] for g in smp)) / max(nn, 1))
    diffs.sort()
    lo, hi = diffs[250], diffs[9749]
    verdict = "better" if hi < 0 else ("worse" if lo > 0 else "no significant difference")
    print(f"| {cat} | {len(sel)} | {100 * eb / n:.2f} | {100 * em / n:.2f} | {100 * (em - eb) / n:+.2f} ({lo:+.2f} to {hi:+.2f}) {verdict} |")
