#!/usr/bin/env python3
"""Step 18 - Markdown tables for RESULTS.md, read from results/*/summary.json (written by 10_evaluate.py)
and the line outputs (*.jsonl), so that every number in the report can be regenerated.

  python3 -I 18_report_tables.py results > results/tables.md
"""
import json, sys
from pathlib import Path

R = Path(sys.argv[1])
SETS = {"real": "real_test_psm13", "dev": "real_dev_psm13", "syn": "synthetic"}
S = {k: json.loads((R / v / "summary.json").read_text(encoding="utf-8")) for k, v in SETS.items()}
M = ["up_best", "up_std", "up_fast", "v3_best", "v3_int", "v31_best", "v31_std", "v31_fast"]
L = {"up_best": "upstream best", "up_std": "upstream std", "up_fast": "upstream fast", "v3_best": "tam_v3 best",
     "v3_int": "tam_v3 int", "v31_best": "**v3.1 best**", "v31_std": "**v3.1 std**", "v31_fast": "**v3.1 fast**"}
P = print


def head(first, cols):
    P(f"| {first} | " + " | ".join(cols) + " |\n|---|" + "---:|" * len(cols))


def cw(t):
    return f"{t[0]:.2f} / {t[1]:.2f}"


P("### Headline: CER % / WER % (strict: NFC, spaces collapsed)\n")
head("model", ["real test (3,968 lines, psm 13)", "real test, invisible chars removed", "real dev (2,854, psm 13)",
               "synthetic (1,389, psm 7)"])
for m in M:
    P(f"| {L[m]} | {cw(S['real']['overall'][m])} | {cw(S['real']['overall_no_invisible'][m])} | "
      f"{cw(S['dev']['overall'][m])} | {cw(S['syn']['overall'][m])} |")

P("\n### Tamil-only CER % (only Tamil-block characters compared)\n")
head("set", [L[m] for m in M])
for k, n in (("real", "real test"), ("dev", "real dev"), ("syn", "synthetic")):
    P(f"| {n} | " + " | ".join(f"{S[k]['overall'][m][2]:.2f}" for m in M) + " |")

for k, n in (("real", "Real test lines by content"), ("syn", "Synthetic categories (request item 16)")):
    P(f"\n### {n}: CER % / WER %\n")
    head("category", [L[m] for m in M])
    for c, d in S[k]["category"].items():
        P(f"| {c} | " + " | ".join(f"{d[m][0]:.2f} / {d[m][1]:.1f}" for m in M) + " |")

P("\n### Characters: share of reference occurrences recovered (real test / synthetic)\n")
head("pattern (real n / synthetic n)", [L[m] for m in M])
for key in S["syn"]["edge"]["v31_best"]:
    nr, ns = S["real"]["edge"]["v31_best"][key][1], S["syn"]["edge"]["v31_best"][key][1]
    cell = lambda k, m: (f"{100 * S[k]['edge'][m][key][0] / S[k]['edge'][m][key][1]:.1f}%" if S[k]["edge"][m][key][1] else "–")
    P(f"| {key} ({nr:,} / {ns:,}) | " + " | ".join(f"{cell('real', m)} / {cell('syn', m)}" for m in M) + " |")
for key, n in (("numeral_tokens", "Tamil numeral tokens"), ("latin_tokens", "Latin word tokens")):
    cell = lambda k, m: (f"{100 * S[k][key][m][0] / S[k][key][m][1]:.1f}%" if S[k][key][m][1] else "–")
    P(f"| {n} ({S['real'][key]['v31_best'][1]:,} / {S['syn'][key]['v31_best'][1]:,}) | "
      + " | ".join(f"{cell('real', m)} / {cell('syn', m)}" for m in M) + " |")
P("| lines with characters outside the v3.1 set | " + " | ".join(
    f"{S['real']['noise_outputs'][m]:,} / {S['syn']['noise_outputs'][m]:,}" for m in M) + " |")

P("\n### Speed and memory (one thread, 300 lines in one process, idle machine)\n")
head("", [L[m] for m in M])
P("| ms per line, real (psm 13) | " + " | ".join(f"{S['real']['speed'][m]['ms_per_line']}" for m in M) + " |")
P("| ms per line, synthetic (psm 7) | " + " | ".join(f"{S['syn']['speed'][m]['ms_per_line']}" for m in M) + " |")
P("| model load, s (median of 3) | " + " | ".join(f"{S['real']['speed'][m]['load_s']}" for m in M) + " |")
P("| peak memory, MB (real) | " + " | ".join(f"{S['real']['speed'][m]['max_rss_MB']}" for m in M) + " |")
P("| file size, MB | " + " | ".join(f"{S['real']['size'][m]}" for m in M) + " |")

# integer cost: agreement of std with best, line by line
P("\n### Float vs integer (same network)\n")
head("", ["identical lines, real test", "identical lines, synthetic"])
for a, b in (("v3_best", "v3_int"), ("v31_best", "v31_std"), ("up_best", "up_std")):
    row = []
    for k in ("real", "syn"):
        x = {r["id"]: r["hyp"] for r in map(json.loads, open(R / SETS[k] / f"{a}.jsonl", encoding="utf-8"))}
        y = {r["id"]: r["hyp"] for r in map(json.loads, open(R / SETS[k] / f"{b}.jsonl", encoding="utf-8"))}
        row.append(f"{100 * sum(x[i] == y[i] for i in x) / len(x):.1f}%")
    P(f"| {L[a]} vs {L[b]} | " + " | ".join(row) + " |")

# Real test scored as tam_v3's own benchmark does (10_evaluate.py --fold: zero-width characters dropped, quote and
# dash variants folded), for a like-for-like comparison with the figures published for tam_v3.
import importlib
sys.path.insert(0, str(Path(__file__).resolve().parent))
E = importlib.import_module("10_evaluate")
E.FOLD["on"] = True
P("\n### Real test, scored as tam_v3's benchmark (zero-width dropped, quotes/dashes folded): CER % / WER %\n")
head("", [L[m] for m in M])
cells = []
for m in M:
    ce = cn = we = wn = 0
    for r in map(json.loads, open(R / SETS["real"] / f"{m}.jsonl", encoding="utf-8")):
        a, b = E.norm(r["ref"]), E.norm(r["hyp"])
        ce += E.lev(a, b); cn += len(a); we += E.lev(a.split(), b.split()); wn += len(a.split())
    cells.append(f"{100 * ce / cn:.2f} / {100 * we / wn:.2f}")
P("| folded | " + " | ".join(cells) + " |")
