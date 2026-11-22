#!/usr/bin/env python3
"""Step 3.1 - Clean v3's character set, dictionary and training text for v3.1.

Inputs (all from the pinned v3.0.0 release, unpacked by step1_inventory.sh):
  --unicharset  tam_v3 lstm-unicharset        --words/--puncs/--numbers  dawg2wordlist output
  --text        tam_v3-training-text.txt.gz
Outputs in --out: tam.unicharset (clean), words.txt, puncs.txt, numbers.txt,
  natural.txt (clean natural-text lines), charset_report.md
"""
import argparse, collections, gzip, json, sys, unicodedata as ud
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charset import ALLOWED, DELETE, MAP, TAMIL_SYMBOLS, normalize, ok  # noqa: E402

SPECIAL = {"NULL", "Joined", "|Broken|0|1"}


def name(u):
    return " + ".join(ud.name(c, f"U+{ord(c):04X}") for c in u)


def clean_unicharset(src, dst):
    lines = open(src, encoding="utf-8").read().splitlines()
    n = int(lines[0]); entries = lines[1:n + 1]
    keep, removed = [], []
    for e in entries:
        u = e.split(" ")[0]
        (keep if u in SPECIAL or (len(u) == 1 and u in ALLOWED) else removed).append(e)
    have = {e.split(" ")[0] for e in keep}
    added = sorted(c for c in ALLOWED if c not in have)
    out = []
    for i, e in enumerate(keep):          # reset other_case / mirror to self; combine_lang_model recomputes them
        f = e.split("\t")[0].split(" ")
        if len(f) >= 8 and f[0] not in ("NULL",):
            f[4] = f[6] = str(i)
        out.append(" ".join(f) + ("\t" + e.split("\t", 1)[1] if "\t" in e else ""))
    for c in added:
        i = len(out)
        script = "Tamil" if "஀" <= c <= "௿" else ("Latin" if c.isalpha() else "Common")
        out.append(f"{c} 0 0,255,0,255,0,0,0,0,0,0 {script} {i} 0 {i} {c}\t# {c} [{ord(c):x} ]")
    Path(dst).write_text(f"{len(out)}\n" + "\n".join(out) + "\n", encoding="utf-8")
    return [e.split(" ")[0] for e in removed], added, len(entries), len(out)


def clean_list(src, dst, pattern=False):
    """Words: one token per line. Punctuation/number patterns: spaces are placeholders
    for the word or number slot, so they are kept exactly (no trimming or collapsing)."""
    seen, dropped = [], 0
    for w in open(src, encoding="utf-8"):
        w = w.rstrip("\n")
        if pattern:
            w = "".join(MAP.get(c, c) for c in ud.normalize("NFC", w)).translate(DELETE)
            good = w.strip() != "" and ok(w)
        else:
            w = normalize(w)
            good = w != "" and ok(w) and " " not in w
        if good:
            seen.append(w)
        elif w.strip():
            dropped += 1
    uniq = sorted(set(seen))
    Path(dst).write_text("\n".join(uniq) + "\n", encoding="utf-8")
    return len(uniq), dropped


def clean_text(src, dst):
    kept = dropped_lines = dropped_words = 0
    bad = collections.Counter()
    with gzip.open(src, "rt", encoding="utf-8") as fi, open(dst, "w", encoding="utf-8") as fo:
        for line in fi:
            line = normalize(line)
            if not line:
                continue
            words = line.split(" ")
            good = [w for w in words if ok(w)]
            for w in words:
                if not ok(w):
                    bad.update(c for c in w if c not in ALLOWED)
            dropped_words += len(words) - len(good)
            if len(good) < 0.8 * len(words) or len(" ".join(good)) < 10:
                dropped_lines += 1
                continue
            fo.write(" ".join(good) + "\n"); kept += 1
    return kept, dropped_lines, dropped_words, bad


def main():
    ap = argparse.ArgumentParser()
    for a in ("unicharset", "words", "puncs", "numbers", "text", "out"):
        ap.add_argument(f"--{a}", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    removed, added, n_old, n_new = clean_unicharset(a.unicharset, out / "tam.unicharset")
    lists = {k: clean_list(getattr(a, k), out / f"{k}.txt", pattern=(k != "words"))
             for k in ("words", "puncs", "numbers")}
    kept, dl, dw, bad = clean_text(a.text, out / "natural.txt")

    r = ["# tam v3.1 character-set cleanup report", "",
         f"Unicharset entries: v3 {n_old} -> v3.1 {n_new} ({len(removed)} removed, {len(added)} added)", "",
         "## Removed from the unicharset", "", "| Char | Code points | Name |", "|---|---|---|"]
    r += [f"| `{u!r}` | {' '.join(f'U+{ord(c):04X}' for c in u)} | {name(u)} |" for u in removed]
    r += ["", "## Added to the unicharset", "", "| Char | Code point | Name |", "|---|---|---|"]
    r += [f"| {c} | U+{ord(c):04X} | {name(c)} |" for c in added]
    r += ["", "## Dictionary lists (after NFC, removing U+200C/U+200D, dropping entries with removed chars)", ""]
    r += [f"- {k}: {n} entries kept, {d} dropped" for k, (n, d) in lists.items()]
    r += ["", "## Training text", "",
          f"- lines kept: {kept}; lines dropped (over 20% of words had removed chars, or too short): {dl}",
          f"- words dropped inside kept lines: {dw}",
          "- most frequent removed characters: " + ", ".join(
              f"{c!r} U+{ord(c):04X} x{n}" for c, n in bad.most_common(25))]
    (out / "charset_report.md").write_text("\n".join(r) + "\n", encoding="utf-8")
    print("\n".join(r[:3])); print(json.dumps({"lists": lists, "text_kept": kept, "text_dropped": dl}))
    missing_sym = [c for c in TAMIL_SYMBOLS if c not in open(out / "tam.unicharset", encoding="utf-8").read()]
    assert not missing_sym, missing_sym


if __name__ == "__main__":
    main()
