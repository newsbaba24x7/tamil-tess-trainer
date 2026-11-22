#!/usr/bin/env python3
"""Step 10 - Accuracy, size and speed evaluation of Tamil traineddata variants.

Accuracy: every evaluation line (PNG + .gt.txt, categories from eval.tsv, fonts from
manifest.tsv) is recognised by every model with `tesseract --psm 7`, in N parallel shards
(one tesseract process per shard, pages separated by \\f).
Speed: one process, OMP_THREAD_LIMIT=1, on the first --speed-lines images: model load time
(median of 3 runs on a 1-line image), ms per line, and peak memory (max RSS).

  python3 -I 10_evaluate.py --lines lines/eval --corpus corpus/eval.tsv --out results \
      --model up_best=models/up_best --model v31_best=models/v31_best ...
Each TESSDATA_DIR holds tam.traineddata. All text is NFC-normalised, whitespace collapsed.
"""
import argparse, collections, json, os, re, statistics, subprocess, sys, tempfile, time, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charset import ALLOWED  # noqa: E402

EDGE = {
    "க்ஷ": re.compile("க்ஷ"), "ஸ்ரீ": re.compile("ஸ்ரீ"), "grantha ஜ ஷ ஸ ஹ ஶ": re.compile("[ஜஷஸஹஶ]"),
    "ஔ / ௌ": re.compile("[ஔௌ]"), "ொ ோ": re.compile("[ொோ]"), "ெ ே ை": re.compile("[ெ-ை]"),
    "ி ீ": re.compile("[ிீ]"), "ு ூ": re.compile("[ுூ]"), "pulli ்": re.compile("்"), "ஃ (aytham)": re.compile("ஃ"),
    "Tamil numerals ௦–௲": re.compile("[௦-௲]"), "Tamil symbols ௳–௺ ௐ": re.compile("[௳-௺ௐ]"),
    "ASCII digits": re.compile("[0-9]"), "quotes “ ” ‘ ’ \" '": re.compile("[“”‘’\"']"),
    "brackets ( ) [ ]": re.compile(r"[()\[\]]"), "dashes — – -": re.compile("[—–-]"), ". , ; :": re.compile("[.,;:]"),
    "? ! … %": re.compile("[?!…%]"), "currency ₹ € £ $": re.compile("[₹€£$]"), "Latin letters": re.compile("[A-Za-z]"),
}
NUM_TOKEN = re.compile("[௦-௲]+")
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9.+#\-]*[A-Za-z0-9+#]|[A-Za-z]")


# --fold: compare text as tamil-tess-trainer v3.0's benchmark does (tamtrain/scans.py prepare()):
# zero-width characters removed, quote and dash variants folded, "…" -> "...".
FOLD = {"on": False}
INVISIBLE_FOLD = dict.fromkeys(map(ord, "​‌‍⁠﻿­"))
PUNCT_FOLD = str.maketrans({"‘": "'", "’": "'", "‛": "'", "′": "'", "`": "'", "“": '"', "”": '"',
                            "″": '"', "–": "-", "—": "-", "―": "-", "…": "..."})


def norm(s):
    s = unicodedata.normalize("NFC", s)
    if FOLD["on"]:
        s = s.translate(INVISIBLE_FOLD).translate(PUNCT_FOLD)
    return re.sub(r"\s+", " ", s).strip()


def lev(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


TESS_C = []   # extra "-c KEY=VALUE" settings from --config


def run_batch(images, tdir, psm, threads=1):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(str(i) for i in images) + "\n"); lst = f.name
    env = dict(os.environ, OMP_THREAD_LIMIT=str(threads))
    t = time.perf_counter()
    p = subprocess.run(["/usr/bin/time", "-f", "MAXRSS_KB=%M", "tesseract", lst, "stdout", "--tessdata-dir", tdir,
                        "-l", "tam", "--psm", str(psm), *TESS_C], capture_output=True, text=True, env=env)
    dt = time.perf_counter() - t
    os.unlink(lst)
    parts = p.stdout.split("\f")
    if len(parts) != len(images):
        sys.exit(f"page split mismatch: {len(parts)} parts for {len(images)} images ({tdir})\n{p.stderr[-500:]}")
    rss = int(re.search(r"MAXRSS_KB=(\d+)", p.stderr).group(1))
    return [norm(x) for x in parts], dt, rss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", required=True); ap.add_argument("--corpus", required=True)
    ap.add_argument("--model", action="append", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--psm", type=int, default=7); ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--speed-lines", type=int, default=300)
    ap.add_argument("--fold", action="store_true", help="fold quotes/dashes and drop zero-width characters (v3.0 benchmark style)")
    ap.add_argument("--config", action="append", default=[], help="tesseract -c KEY=VALUE (repeatable)")
    a = ap.parse_args()
    FOLD["on"] = a.fold
    for kv in a.config:
        TESS_C.extend(["-c", kv])
    lines = Path(a.lines); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    cat = {l.split("\t")[0]: l.split("\t")[1] for l in open(a.corpus, encoding="utf-8")}
    font = {r[0]: r[2] for r in (l.rstrip("\n").split("\t") for l in open(lines / "manifest.tsv", encoding="utf-8")) if r[0] != "id"}
    ids = sorted(cat)
    imgs = [lines / f"{i}.png" for i in ids]
    ref = {i: norm((lines / f"{i}.gt.txt").read_text(encoding="utf-8")) for i in ids}
    models = [m.split("=", 1) for m in a.model]
    from concurrent.futures import ThreadPoolExecutor
    res = {}
    for name, tdir in models:
        shards = [imgs[k::a.jobs] for k in range(a.jobs)]
        with ThreadPoolExecutor(a.jobs) as ex:
            outs = list(ex.map(lambda s: run_batch(s, tdir, a.psm)[0], shards))
        hyp = {}
        for k, s in enumerate(shards):
            for img, h in zip(s, outs[k]):
                hyp[img.stem] = h
        res[name] = hyp
        (out / f"{name}.jsonl").write_text("".join(json.dumps({"id": i, "category": cat[i], "font": font.get(i), "ref": ref[i], "hyp": hyp[i]}, ensure_ascii=False) + "\n" for i in ids), encoding="utf-8")
        print(f"recognised {len(ids)} lines with {name}", file=sys.stderr)

    INVISIBLE = dict.fromkeys(map(ord, "​‌‍‎‏⁠﻿"))

    def score(sel, name, strip_invisible=False):
        ce = cn = we = wn = te = tn = 0
        for i in sel:
            r, h = ref[i], res[name][i]
            if strip_invisible:
                h = norm(h.translate(INVISIBLE))
            ce += lev(r, h); cn += len(r); we += lev(r.split(), h.split()); wn += len(r.split())
            rt = "".join(c for c in r if "஀" <= c <= "௿"); ht = "".join(c for c in h if "஀" <= c <= "௿")
            te += lev(rt, ht); tn += len(rt)
        return 100 * ce / max(cn, 1), 100 * we / max(wn, 1), 100 * te / max(tn, 1)

    names = [n for n, _ in models]
    S = {"overall": {}, "category": collections.defaultdict(dict), "font": collections.defaultdict(dict), "edge": {},
         "numeral_tokens": {}, "latin_tokens": {}, "noise_outputs": {}, "speed": {}, "size": {}}
    S["overall_no_invisible"] = {}
    for n in names:
        S["overall"][n] = score(ids, n)
        S["overall_no_invisible"][n] = score(ids, n, strip_invisible=True)
        for c in sorted(set(cat.values())):
            S["category"][c][n] = score([i for i in ids if cat[i] == c], n)
        for f in sorted(set(font.values())):
            S["font"][f][n] = score([i for i in ids if font.get(i) == f], n)[0]
        S["edge"][n] = {k: (sum(min(len(rx.findall(ref[i])), len(rx.findall(res[n][i]))) for i in ids),
                            sum(len(rx.findall(ref[i])) for i in ids)) for k, rx in EDGE.items()}
        for key, rx in (("numeral_tokens", NUM_TOKEN), ("latin_tokens", LATIN_TOKEN)):
            hit = tot = 0
            for i in ids:
                rt = collections.Counter(rx.findall(ref[i])); ht = collections.Counter(rx.findall(res[n][i]))
                hit += sum(min(v, ht[k]) for k, v in rt.items()); tot += sum(rt.values())
            S[key][n] = (hit, tot)
        S["noise_outputs"][n] = sum(1 for i in ids if any(c not in ALLOWED and c != " " for c in res[n][i]))

    sp_imgs = imgs[: a.speed_lines]
    one = [imgs[0]]
    for n, tdir in models:
        load = statistics.median(run_batch(one, tdir, a.psm)[1] for _ in range(3))
        _, dt, rss = run_batch(sp_imgs, tdir, a.psm)
        S["speed"][n] = {"load_s": round(load, 3), "ms_per_line": round(1000 * max(dt - load, 0) / len(sp_imgs), 1), "max_rss_MB": round(rss / 1024, 1)}
        S["size"][n] = round(os.path.getsize(Path(tdir) / "tam.traineddata") / 1e6, 2)
    (out / "summary.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")

    P = print
    hdr = lambda first: P(f"| {first} | " + " | ".join(names) + " |\n|---|" + "---:|" * len(names))
    P(f"## Overall ({len(ids)} held-out lines, psm {a.psm})\n"); hdr("metric")
    for k, j in (("CER %", 0), ("Tamil-only CER %", 2), ("WER %", 1)):
        P(f"| {k} | " + " | ".join(f"{S['overall'][n][j]:.2f}" for n in names) + " |")
    for k, j in (("CER % (invisible chars removed from output)", 0), ("WER % (invisible chars removed)", 1)):
        P(f"| {k} | " + " | ".join(f"{S['overall_no_invisible'][n][j]:.2f}" for n in names) + " |")
    P("| size MB | " + " | ".join(f"{S['size'][n]}" for n in names) + " |")
    P("| load s | " + " | ".join(f"{S['speed'][n]['load_s']}" for n in names) + " |")
    P("| ms / line | " + " | ".join(f"{S['speed'][n]['ms_per_line']}" for n in names) + " |")
    P("| peak RSS MB | " + " | ".join(f"{S['speed'][n]['max_rss_MB']}" for n in names) + " |")
    P("| lines with chars outside v3.1 set | " + " | ".join(str(S['noise_outputs'][n]) for n in names) + " |")
    P("\n## CER % / WER % by category\n"); hdr("category")
    for c, d in S["category"].items():
        P(f"| {c} | " + " | ".join(f"{d[n][0]:.2f} / {d[n][1]:.1f}" for n in names) + " |")
    P("\n## CER % by font (all held out of v3.1 training)\n"); hdr("font")
    for f, d in S["font"].items():
        P(f"| {f} | " + " | ".join(f"{d[n]:.2f}" for n in names) + " |")
    P("\n## Recovered / reference occurrences\n"); hdr("pattern")
    for k in EDGE:
        tot = S["edge"][names[0]][k][1]
        if tot:
            P(f"| {k} ({tot}) | " + " | ".join(f"{100 * S['edge'][n][k][0] / tot:.1f}%" for n in names) + " |")
    for key, label in (("numeral_tokens", "Tamil numeral tokens exact"), ("latin_tokens", "English tokens exact")):
        tot = S[key][names[0]][1]
        P(f"| {label} ({tot}) | " + " | ".join(f"{100 * S[key][n][0] / max(tot, 1):.1f}%" for n in names) + " |")


if __name__ == "__main__":
    main()
