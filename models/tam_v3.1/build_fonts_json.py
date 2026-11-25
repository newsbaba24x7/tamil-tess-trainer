#!/usr/bin/env python3
"""Build fonts.json: every font style used to train or test tam_multifont (v1), tam_v2, tam_v3 and tam_v3.1.

  python3 -I build_fonts_json.py TRAINER_REPO V31_DIR OUT.json

Inputs (all local, nothing downloaded):
  TRAINER_REPO/models/{tam_multifont,tam_v2,tam_v3}/fonts.json   published font metadata (name, source, licence)
  TRAINER_REPO/work-{60,v2,v3}/fonts.json                         font file paths used by the renderer
  TRAINER_REPO/work-{60,v2,v3}/manifest.jsonl                     one row per rendered line: font, split (train/eval)
                                                                  (local render records; not in the repository)
  V31_DIR/fonts.tsv, V31_DIR/03_render_lines.py                   tam_v3.1 font list and renderer (Latin-font rule)
  V31_DIR/results/synthetic/v31_best.jsonl                        tam_v3.1 rendered test lines (font per line)
The same font is matched across versions by the SHA-256 of its file plus the variable-font setting.
"""
import collections, hashlib, importlib.util, json, os, subprocess, sys

R, V, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
OLD = " (old letters)"


def resolve(p):
    p = os.path.expanduser(p)
    return p if os.path.isabs(p) else os.path.join(R, p)


_sha = {}
def sha(p):
    if p not in _sha:
        _sha[p] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return _sha[p]


def key(path, variation):
    return sha(resolve(path)) + "|" + json.dumps(variation, sort_keys=True)


# ---- licence review of 2026-11-22 (models/tam_v3.1/LICENSING.md, section 3; single-source, not re-checked) ----
REVIEW_NOTE = "models/tam_v3.1/LICENSING.md section 3 (2026-11-22); single source, not yet independently re-checked"
def review(rec):
    fam, src, lic = rec["family"], rec.get("source", ""), rec.get("licence", "")
    if fam == "AkrutiTml1":
        return {"finding": "GNU GPL with no version stated anywhere found", "spdx": "GPL-1.0-or-later", "source": REVIEW_NOTE}
    if fam == "AkrutiTml2":
        return {"finding": "Same GPL notice, but withdrawn by FSF India 'due to possible copyright issues'; Debian removed "
                "it for the same reason. Recommended: leave out of future training", "spdx": "GPL-1.0-or-later (withdrawn)",
                "source": REVIEW_NOTE}
    if src.startswith("Gopi"):
        return {"finding": "Not GPL. The author's page allows free use and free redistribution only, 'strictly not for sale / "
                "commercial re-distribution'; the 'GPL' label came from a third-party installer. Training use is not addressed",
                "spdx": "LicenseRef-Gopi-TAMUni", "source": REVIEW_NOTE}
    if src.startswith("Kadugu"):
        return {"finding": "'TSCII Based Royalty Free Tamil Fonts' (Sarma's Solutions, archived 2007); embedded string "
                "'[Free Usage/Distribution]'; Unicode conversions by Neechalkaran. Commercial use, modification and training "
                "are not addressed", "spdx": "LicenseRef-Kadugu", "source": REVIEW_NOTE}
    if fam.startswith("Uni Ila.Sundaram"):
        return {"finding": "OFL-1.1 is stated only by secondary sources; the author's blog gives no licence",
                "spdx": "unconfirmed (records say OFL-1.1)", "source": REVIEW_NOTE}
    if "TVA" in lic or src == "Tamil Virtual Academy":
        return {"finding": "Tamil Virtual Academy policy page puts its computing resources under GPL-2.0-or-later; the fonts "
                "are not named explicitly. Probable, not explicit", "spdx": "GPL-2.0-or-later (probable)", "source": REVIEW_NOTE}
    return None


fonts = {}          # key -> record
order = []


def add(k, rec):
    if k not in fonts:
        fonts[k] = rec; order.append(k)
    return fonts[k]


# ---- v1, v2, v3 ---------------------------------------------------------------------------------------------
GEN = [("tam_multifont", "work-60"), ("tam_v2", "work-v2"), ("tam_v3", "work-v3")]
gen_summary = {}
for model, work in GEN:
    meta = {x["name"]: x for x in json.load(open(f"{R}/models/{model}/fonts.json", encoding="utf-8"))}
    paths = {x["name"]: x for x in json.load(open(f"{R}/{work}/fonts.json", encoding="utf-8"))}
    assert set(meta) == set(paths), (model, set(meta) ^ set(paths))
    lines = collections.Counter()
    for l in open(f"{R}/{work}/manifest.jsonl", encoding="utf-8"):
        r = json.loads(l)
        base = r["font"][:-len(OLD)] if r["font"].endswith(OLD) else r["font"]
        lines[(base, r["split"], r["font"].endswith(OLD))] += 1
    trained = held = 0
    for name, m in meta.items():
        p = paths[name]
        k = key(p["path"], p.get("variation"))
        rec = add(k, {"name": name, "family": m["family"], "source": m["source"], "file": m["file"],
                      "variation": m["variation"], "sha256": sha(resolve(p["path"])),
                      "licence_recorded": m["licence"], "licence_class": m["licence_class"], "used_in": {}})
        if model != "tam_multifont":         # newer metadata wins (names and sources were tidied for tam_v2)
            rec.update(name=name, family=m["family"], source=m["source"], file=m["file"],
                       licence_recorded=m["licence"], licence_class=m["licence_class"])
        tr = lines[(name, "train", False)] + lines[(name, "train", True)]
        te = lines[(name, "eval", False)] + lines[(name, "eval", True)]
        use = "train" if tr else "test only (held out)"
        trained += bool(tr); held += not tr
        u = {"use": use, "train_lines": tr, "test_lines": te}
        if lines[(name, "train", True)] or lines[(name, "eval", True)]:
            u["of_which_old_letter_forms"] = lines[(name, "train", True)] + lines[(name, "eval", True)]
        rec["used_in"][model] = u
    gen_summary[model] = {"styles_listed": len(meta), "styles_trained": trained, "styles_held_out_for_testing": held,
                          "rendered_train_lines": sum(n for (f, s, o), n in lines.items() if s == "train"),
                          "rendered_test_lines": sum(n for (f, s, o), n in lines.items() if s != "train")}

# ---- v3.1 --------------------------------------------------------------------------------------------------
spec = importlib.util.spec_from_file_location("rl", f"{V}/03_render_lines.py")
rl = importlib.util.module_from_spec(spec); spec.loader.exec_module(rl)
f31 = rl.load_fonts(f"{V}/fonts.tsv", {"train", "latin", "eval"})
tsv = {}
for line in open(f"{V}/fonts.tsv", encoding="utf-8"):
    if line.startswith("#") or not line.strip():
        continue
    role, cls, lic, ev, path = line.rstrip("\n").split("\t")
    tsv[os.path.expanduser(path)] = {"role": role, "cls": cls, "licence": lic, "evidence": ev}
latin = {c: [f for f in f31 if f["role"] == "latin" and f["cls"] == c] for c in ("sans", "serif")}
picked = {"train": set(), "eval": set()}
for f in f31:
    if f["role"] in picked:
        lat = [x for x in latin[f["cls"]] if (x["weight"] >= 600) == (f["weight"] >= 600)]
        picked[f["role"]] |= {x["path"] for x in ([x for x in lat if x["italic"] == f["italic"]] or lat)}
test_lines = collections.Counter(json.loads(l)["font"].rsplit(" w", 1)[0]
                                 for l in open(f"{V}/results/synthetic/v31_best.jsonl", encoding="utf-8"))
fc = lambda p, fmt: subprocess.run(["fc-query", "-f", fmt, p], capture_output=True, text=True).stdout.split("\n")[0]
for f in f31:
    p = f["path"]; t = tsv[p]
    full = fc(p, "%{fullname[0]}") or f["family"]
    rec = add(key(p, None), {"name": full, "family": f["family"], "source": None, "file": os.path.basename(p),
                             "variation": None, "sha256": sha(p), "licence_recorded": t["licence"],
                             "licence_class": "open" if t["licence"].startswith(("OFL", "GPL")) else
                             ("restricted" if "proprietary" in t["licence"] else "unverified"), "used_in": {}})
    if t["role"] == "train":
        u = {"use": "train", "role": "Tamil text"}
    elif t["role"] == "latin":
        u = {"use": "train" if p in picked["train"] else "listed, never picked",
             "role": f"English (Latin) runs next to {t['cls']} Tamil fonts"}
        if p in picked["eval"]:
            u["also"] = "English runs in the rendered test lines"
    else:
        u = {"use": "test only", "role": "Tamil text of the 1,389 rendered test lines",
             "test_lines": test_lines[f["family"]],
             "note": "Even-numbered test lines were also one of the checks when choosing the release "
                     "(select_dev.py: categories A-D no worse than tam_v3). Not used in tam_v3.1's own fine-tuning"}
    u["licence_evidence"] = t["evidence"]
    rec["used_in"]["tam_v3.1"] = u
    if t["role"] in ("train", "latin") and rec["licence_recorded"] != t["licence"]:
        rec["licence_recorded_v3.1"] = t["licence"]

# ---- finish records ----------------------------------------------------------------------------------------
SRC31 = {"Noto": "Google (Noto)", "Mukta": "Ek Type", "Lohit": "Lohit (Red Hat)", "Samyak": "Samyak", "Latha": "Microsoft",
         "Uni Ila": "Uni Ila.Sundaram Fonts Project", "TAU": "Tamil Virtual Academy"}
out_fonts = []
for k in order:
    r = fonts[k]
    if r["source"] is None:
        r["source"] = next((v for p, v in SRC31.items() if r["family"].startswith(p)), "unknown")
    lr = review(r)
    if lr:
        r["licence_review"] = lr
    trained_in = [m for m in ("tam_v2", "tam_v3", "tam_v3.1") if r["used_in"].get(m, {}).get("use") == "train"]
    u31 = r["used_in"].get("tam_v3.1", {})
    if u31.get("use") == "test only":
        u31["trained_earlier"] = ([m for m in ("tam_multifont", "tam_v2", "tam_v3") if r["used_in"].get(m, {}).get("use") == "train"])
        if trained_in:
            u31["warning"] = ("Not used in tam_v3.1's own fine-tuning, but the same file trained tam_v2 and tam_v3, so this font "
                              "is not unseen for tam_v3.1 (or for tam_v3)")
    if sum(1 for x in fonts.values() if x["name"] == r["name"]) > 1:
        r["same_name_note"] = "Another entry has the same style name but a different font file (see file and sha256)"
    r["in_tam_v3_1_weights"] = bool(trained_in)
    r["in_tam_v3_1_weights_via"] = trained_in
    out_fonts.append(r)
out_fonts.sort(key=lambda r: (r["family"].lower(), r["name"].lower(), r["file"]))

s31 = {"tamil_files_trained": sum(1 for r in out_fonts if r["used_in"].get("tam_v3.1", {}).get("role") == "Tamil text"),
       "latin_files_listed": sum(1 for r in out_fonts if "Latin" in r["used_in"].get("tam_v3.1", {}).get("role", "")),
       "latin_files_picked_for_training": sum(1 for r in out_fonts if "Latin" in r["used_in"].get("tam_v3.1", {}).get("role", "")
                                              and r["used_in"]["tam_v3.1"]["use"] == "train"),
       "test_only_files": sum(1 for r in out_fonts if r["used_in"].get("tam_v3.1", {}).get("use") == "test only"),
       "rendered_train_lines": 16012, "rendered_test_lines": sum(test_lines.values())}

doc = {
    "title": "Fonts used to train and test the tamil-tess-trainer Tamil models: tam_multifont (v1), tam_v2, tam_v3, tam_v3.1",
    "date": "2026-11-25",
    "lineage": "Tesseract tessdata_best/tam -> tam_v2 -> tam_v3 -> tam_v3.1. tam_multifont (v1) was also fine-tuned from "
               "Tesseract's tam, but tam_v2 did not start from it, so fonts used only by v1 are not in the tam_v3.1 weights.",
    "how_to_read": {
        "fonts": "One entry per font style (one font file, or one setting of a variable font). The same file used by "
                 "several models is one entry, matched by its SHA-256.",
        "used_in": "Per model: 'train' = rendered training lines were made with it; 'test only (held out)' = used only for "
                   "test lines; train_lines / test_lines = rendered lines in this style (counts are not kept for tam_v3.1's "
                   "training lines). tam_v3 used the same font list as tam_v2 and rendered new lines.",
        "in_tam_v3_1_weights": "true if the style was used to train tam_v2, tam_v3 or tam_v3.1, so it has influenced the "
                               "tam_v3.1 weights. No font, image or text is stored inside any .traineddata file.",
        "licence_recorded": "The licence as recorded when the model was made.",
        "licence_review": "Findings of the licence review made for tam_v3.1 (where they differ from, or qualify, the record).",
    },
    "models": {
        "tam (Tesseract, base model)": {"fonts": "Not listed here. The base model was trained by the Tesseract project; "
                                        "this project has no record of its fonts."},
        "tam_multifont": {"release": "v1.0.0", "base": "Tesseract tessdata_best/tam", "in_tam_v3_1_lineage": False,
                          **gen_summary["tam_multifont"]},
        "tam_v2": {"release": "v2.0.0", "base": "Tesseract tessdata_best/tam", "in_tam_v3_1_lineage": True,
                   **gen_summary["tam_v2"], "also_trained_on": "24,445 real scanned lines"},
        "tam_v3": {"release": "v3.0.0", "base": "tam_v2", "in_tam_v3_1_lineage": True, **gen_summary["tam_v3"],
                   "also_trained_on": "174,624 real scanned lines"},
        "tam_v3.1": {"release": "v3.1.0", "base": "tam_v3", "in_tam_v3_1_lineage": True, **s31,
                     "also_trained_on": "16,012 of tam_v3's real scanned training lines (mixed 50/50 with the rendered lines)",
                     "font_list_file": "models/tam_v3.1/fonts.tsv"},
    },
    "not_included": ["tam_v2_research (V2-research, non-commercial research model, 276 styles): see "
                     "models/tam_v2_research/fonts.json"],
    "corrections_and_notes": [
        "tam_v3.1 rendered test lines: until 25 Nov 2026 the model card, release notes, benchmark page, RESULTS.md and the "
        "pull requests described them as rendered in 6 fonts not used for training (corrected on that date). "
        "4 of the 6 files (Noto Sans Tamil Condensed Regular, Noto Serif Tamil Slanted Regular, Uni Ila.Sundaram-19, "
        "TAU-Neythal; same SHA-256) were used to train tam_v2 and tam_v3, so they are in the tam_v3.1 weights. They were "
        "not used in tam_v3.1's own fine-tuning. Only Uni Ila.Sundaram-20 (held out in every version) and Latha (trained "
        "only in tam_multifont, which is not in the lineage) are unseen for tam_v3.1.",
        "tam_v3.1: until 25 Nov 2026 MODEL_CARD.md and NOTICE said the training lines were rendered in '23 font files' "
        "(corrected on that date). fonts.tsv lists 24 "
        "(16 Tamil + 8 Latin). By the renderer's rule (03_render_lines.py: Latin font of the same class, same boldness and "
        "same slant as the Tamil font) only 20 can be picked: 16 Tamil + Noto Sans Regular/Bold + Noto Serif Regular/Bold. "
        "The 4 italic Latin files are never picked, because no Tamil training font is italic to fontconfig (Noto Serif "
        "Tamil Slanted reports slant 0). The per-line render records were deleted after training, so this count comes "
        "from the code, not from the records. Every render run reported 'fonts used outside the allowed list: none'.",
        "tam_v2 / tam_v3: some recorded licences are unverified or differ from what the review found (Gopi, Akruti, "
        "Kadugu, Uni Ila.Sundaram, Tamil Virtual Academy fonts); see licence_review in each entry.",
        "tam_multifont (v1) used 4 styles without an open licence (Latha, proprietary; uniAmma-10/11/16, unknown). "
        "They are not in the tam_v3.1 weights.",
    ],
    "fonts": out_fonts,
}
json.dump(doc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(OUT, "a").write("\n")
print("fonts", len(out_fonts)); print(json.dumps(doc["models"], indent=1))
