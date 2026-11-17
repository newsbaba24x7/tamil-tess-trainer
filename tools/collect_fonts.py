#!/usr/bin/env python3
"""Collect openly licensed Tamil fonts, group them by family, and build a preview page.

Usage:
    python3 tools/collect_fonts.py --src ~/tamil-font-sources --out fonts

--src must contain (the script clones/downloads what is missing):
    fonts-tamil-libre/   https://github.com/lecramyajiv/fonts-tamil-libre
    fonts-tamil-tva/     https://github.com/lecramyajiv/fonts-tamil-tva   (Tamil Virtual Academy TAU fonts)
    fonts-tamil-nonlibre/ https://github.com/lecramyajiv/fonts-tamil-nonlibre (C-DAC GIST, non-commercial)
    tamil-fonts/         https://github.com/thamizha/tamil-fonts
    google/<dir>/        files from https://github.com/google/fonts/tree/main/ofl/<dir>

Output (--out):
    candidates/<family>/   font files + license
    catalog.json           family, styles, source, license, stock-model error, look-alikes
    choose.html            preview page with checkboxes
Families already installed on this computer (fc-list :lang=ta) are left out, except the
variable Noto Tamil fonts, which add weights and condensed widths to the installed ones.
Fonts with a non-commercial licence (the C-DAC GIST set) are marked on the page and in
catalog.json ("restricted"): fine for experiments, but ask the owner before publishing a
model trained on them.
"""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageChops  # noqa: E402

from tamtrain import fonts as fontmod  # noqa: E402
from tamtrain import render  # noqa: E402
from tamtrain.evaluate import ModelSpec, align, ocr_batch  # noqa: E402
from tamtrain.sfnt import read_faces  # noqa: E402

REPOS = {
    "fonts-tamil-libre": "https://github.com/lecramyajiv/fonts-tamil-libre.git",
    "fonts-tamil-tva": "https://github.com/lecramyajiv/fonts-tamil-tva.git",
    "tamil-fonts": "https://github.com/thamizha/tamil-fonts.git",
    "fonts-tamil-nonlibre": "https://github.com/lecramyajiv/fonts-tamil-nonlibre.git",
}
GOOGLE = {  # ofl/<dir>: Google Fonts family
    "anektamil": "Anek Tamil", "arima": "Arima", "baloothambi2": "Baloo Thambi 2", "catamaran": "Catamaran",
    "coiny": "Coiny", "googlesans": "Google Sans", "hindmadurai": "Hind Madurai",
    "karlatamilinclined": "Karla Tamil Inclined", "karlatamilupright": "Karla Tamil Upright",
    "kavivanar": "Kavivanar", "meerainimai": "Meera Inimai", "oi": "Oi", "pavanam": "Pavanam",
    "tirotamil": "Tiro Tamil", "notosanstamil": "Noto Sans Tamil", "notoseriftamil": "Noto Serif Tamil",
}
# Installed as static Regular/Bold by most Linux distributions; the variable versions add the
# other weights and the condensed widths used in newspaper headlines.
# Release downloads (zip archives or single font files), unpacked into --src/<name>/.
NLCI_REL = "https://github.com/nlci/taml-font-thiruvalluvar/releases/download/v0.901/nlci-taml-{}-0.901.zip"
ARCHIVES = {
    "nlci-0.901/thiruvalluvar": NLCI_REL.format("thiruvalluvar"),
    "nlci-0.901/auvaiyar": NLCI_REL.format("auvaiyar"),
    "nlci-0.901/vaigai": NLCI_REL.format("vaigai"),
    "abhaya-libre/AbhayaLibre.ttf":
        "https://github.com/mooniak/abhaya-libre-font/releases/download/canary/AbhayaLibreCANARY.wght.ttf",
    "abhaya-libre/OFL.txt": "https://github.com/mooniak/abhaya-libre-font/releases/download/canary/OFL.txt",
    "freefont": "https://ftp.gnu.org/gnu/freefont/freefont-ttf-20120503.zip",
}
ALLOW_INSTALLED = {"notosanstamil", "notoseriftamil"}
NONCOMMERCIAL = "Non-commercial use only (C-DAC)"
CDAC = "https://github.com/lecramyajiv/fonts-tamil-nonlibre"
LIBRE = "https://github.com/lecramyajiv/fonts-tamil-libre"
# (glob relative to --src, source, url, license, license file relative to --src)
SOURCES = [
    *[(f"google/{d}/*.ttf", "Google Fonts", f"https://fonts.google.com/specimen/{fam.replace(' ', '+')}",
       "OFL-1.1", f"google/{d}/OFL.txt") for d, fam in GOOGLE.items()],
    ("fonts-tamil-libre/Googlefonts/TTF/PostNoBills-Jaffna/*.ttf", "Google Fonts",
     "https://fonts.google.com/specimen/Post+No+Bills+Jaffna", "OFL-1.1",
     "fonts-tamil-libre/Googlefonts/license/postnobills/OFL.txt"),
    ("nlci-0.901/thiruvalluvar/*/*-*.ttf", "NLCI", "https://github.com/nlci/taml-font-thiruvalluvar",
     "OFL-1.1", "nlci-0.901/thiruvalluvar/nlci-taml-thiruvalluvar-0.901/OFL.txt"),
    ("nlci-0.901/auvaiyar/*/*-*.ttf", "NLCI", "https://github.com/nlci/taml-font-thiruvalluvar",
     "OFL-1.1", "nlci-0.901/auvaiyar/nlci-taml-auvaiyar-0.901/OFL.txt"),
    ("nlci-0.901/vaigai/*/*-*.ttf", "NLCI", "https://github.com/nlci/taml-font-thiruvalluvar",
     "OFL-1.1", "nlci-0.901/vaigai/nlci-taml-vaigai-0.901/OFL.txt"),
    ("fonts-tamil-libre/OTF/Madurai/*.otf", "Agam Type Foundry", "https://github.com/sgangaprasath/madurai",
     "CC-BY-4.0", "fonts-tamil-libre/licenses/Madurai/Copyright"),
    ("fonts-tamil-libre/TTF/aaram/*.ttf", "Enathu (Tharique Azeez)", LIBRE, "OFL-1.1",
     "fonts-tamil-libre/licenses/aaram/OFL.txt"),
    ("fonts-tamil-libre/TTF/neythal/*.ttf", "Enathu (Tharique Azeez)", LIBRE, "OFL-1.1",
     "fonts-tamil-libre/licenses/neythal/OFL.txt"),
    ("fonts-tamil-libre/TTF/Meera-tamil/MeeraTamil-Regular.ttf", "SMC", LIBRE, "OFL-1.1",
     "fonts-tamil-libre/licenses/meera-tamil/OFL.txt"),
    ("fonts-tamil-libre/TTF/droidsans-tamil/*.ttf", "Android (Droid)", LIBRE, "Apache-2.0",
     "fonts-tamil-libre/licenses/Droid Sans/NOTICE"),
    ("fonts-tamil-tva/tau_fonts/*.ttf", "Tamil Virtual Academy", "https://github.com/lecramyajiv/fonts-tamil-tva",
     "GPL-2.0+ (TVA)", "fonts-tamil-tva/licenses/TAU/TVA_Copyright.md"),
    ("fonts-tamil-libre/TTF/kadugu/*.ttf", "Kadugu (P S Ranganathan)", LIBRE, "Free use and distribution",
     "fonts-tamil-libre/licenses/Kadugu/Copyright"),
    ("fonts-tamil-libre/TTF/chemmozhi/*.ttf", "Chemmozhi (ICTA.lk)", LIBRE, "GPL-2.0",
     "fonts-tamil-libre/licenses/Chemmozhi/gpl-2.0.txt"),
    ("fonts-tamil-libre/TTF/Umar/*.ttf", "Umar", LIBRE, "GPL-2.0", "fonts-tamil-libre/licenses/Umar/Copyright"),
    ("fonts-tamil-libre/TTF/TSCu/*.ttf", "TSCu", LIBRE, "GPL-2.0",
     "fonts-tamil-libre/licenses/TSCu/tscu_1.0-3_copyright"),
    ("fonts-tamil-libre/TTF/TAMu/*.ttf", "TAMu (Kamban Software)", LIBRE, "GPL-2.0",
     "fonts-tamil-libre/licenses/Tamu/tamu_1.0-4_copyright"),
    ("fonts-tamil-libre/TTF/Akruti/*.ttf", "Akruti", LIBRE, "GPL", "fonts-tamil-libre/licenses/Akruti/README"),
    ("tamil-fonts/fonts-installer/fontfiles/*Uni-Tamil*.ttf", "Gopi (higopi.com)",
     "https://github.com/thamizha/tamil-fonts", "GPL", "tamil-fonts/fonts-installer/license.txt"),
    ("tamil-fonts/open-sourced/YaldeviJaffna-*.ttf", "Mooniak", "https://github.com/mooniak/yaldevi-font",
     "OFL-1.1", "tamil-fonts/open-sourced/LICENSE.OFL.yaldevi"),
    ("abhaya-libre/AbhayaLibre.ttf", "Mooniak", "https://github.com/mooniak/abhaya-libre-font", "OFL-1.1",
     "abhaya-libre/OFL.txt"),
    ("freefont/freefont-20120503/FreeSerif.ttf", "GNU FreeFont", "https://www.gnu.org/software/freefont/",
     "GPL-3.0+ with font exception", "freefont/freefont-20120503/COPYING"),
    ("fonts-tamil-nonlibre/TTF/*.TTF", "C-DAC GIST", CDAC, NONCOMMERCIAL, "fonts-tamil-nonlibre/LICENSE"),
    ("fonts-tamil-nonlibre/ttf/*.ttf", "C-DAC GIST", CDAC, NONCOMMERCIAL, "fonts-tamil-nonlibre/LICENSE"),
]
SAMPLE = "யாதும் ஊரே யாவரும் கேளிர் தீதும் நன்றும் பிறர்தர வாரா கொண்டு ஞாயிறு வெளிச்சம்"
PREFERRED_STYLES = ["Regular", "Normal", "Book", "Roman", "Medium", "Plain"]
LOOKALIKE = 0.90  # glyph-shape similarity above which a family is treated as a copy of an earlier one


def licence_class(lic: str) -> str:
    """open: OFL, GPL, Apache, CC-BY (fine for a published model); free-use: freeware without a
    formal licence; non-commercial: experiments only."""
    if lic == NONCOMMERCIAL:
        return "non-commercial"
    if lic.lower().startswith("free use"):
        return "free-use"
    return "open"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def fetch_archives(src: Path) -> None:
    import zipfile
    for name, url in ARCHIVES.items():
        dest = src / name
        if dest.exists():
            continue
        print(f"downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "tamtrain"})
        with urllib.request.urlopen(req) as r:
            data = r.read()
        if url.endswith(".zip"):
            dest.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(dest)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)


def fetch_sources(src: Path) -> None:
    src.mkdir(parents=True, exist_ok=True)
    fetch_archives(src)
    for name, url in REPOS.items():
        if not (src / name).exists():
            print(f"cloning {url}")
            subprocess.run(["git", "clone", "-q", "--depth", "1", url, str(src / name)], check=True)
    for d in GOOGLE:
        dest = src / "google" / d
        if dest.exists() and any(dest.glob("*.ttf")):
            continue
        dest.mkdir(parents=True, exist_ok=True)
        api = f"https://api.github.com/repos/google/fonts/contents/ofl/{d}"
        with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": "tamtrain"})) as r:
            for item in json.load(r):
                if re.search(r"\.(ttf|otf)$|OFL\.txt$", item["name"]):
                    print(f"downloading {item['name']}")
                    urllib.request.urlretrieve(item["download_url"], dest / urllib.parse.unquote(item["name"]))


def installed_families() -> set[str]:
    out = subprocess.run(["fc-list", ":lang=ta", "family"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    fams = set()
    for line in out.splitlines():
        for part in line.replace("\\", "").split(","):
            fams.add(norm(part))
    return fams


def preview_png(font: fontmod.Font, size: int = 34) -> Image.Image:
    f = render._font(str(font.path), font.index, size, font.variation)
    text = "".join(ch for ch in SAMPLE if ch == " " or font.supports(ch))
    return render.render_clean(text, f, pad_x=10, pad_y=8)


STYLE_SUFFIX = re.compile(r"[\s_-]+(bold\s*italic|bold|italic|oblique)$", re.I)
SIGNATURE_GLYPHS = ["க", "ங", "ச", "ஞ", "ட", "ண", "த", "ந", "ப", "ம", "ய", "ர", "ல", "வ", "ழ", "ள", "ற", "ன",
                    "அ", "ஆ", "இ", "எ", "ஐ", "ஒ", "கு", "டு", "கூ", "கை", "கொ", "தி"]


def base_family(name: str) -> str:
    """'TAU-Kurinji Bold' -> 'TAU-Kurinji' (some fonts put the style in the family name)."""
    prev = None
    while prev != name:
        prev, name = name, STYLE_SUFFIX.sub("", name).strip()
    return name


def glyph_signature(font: fontmod.Font) -> list[Image.Image]:
    """Each sample glyph rendered alone, cropped to its ink and scaled to 24x24."""
    f = render._font(str(font.path), font.index, 64, font.variation)
    sig = []
    for g in SIGNATURE_GLYPHS:
        if not font.supports(g):
            continue
        img = render.render_clean(g, f, pad_x=2, pad_y=2)
        box = ImageChops.invert(img).getbbox()
        sig.append(img.crop(box).resize((24, 24)) if box else img.resize((24, 24)))
    return sig


def similarity(a: list[Image.Image], b: list[Image.Image]) -> float:
    """Average overlap of the glyph shapes: 1.0 = same design, about 0.5 = unrelated designs."""
    scores = []
    for x, y in zip(a, b):
        ink = 2 * 255 * 24 * 24 - sum(x.tobytes()) - sum(y.tobytes())
        diff = sum(ImageChops.difference(x, y).tobytes())
        scores.append(1 - diff / max(ink, 1))
    return sum(scores) / max(len(scores), 1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("fonts"))
    ap.add_argument("--no-fetch", action="store_true")
    args = ap.parse_args()
    render.check_shaping_support()
    if not args.no_fetch:
        fetch_sources(args.src)
    installed = installed_families()

    # 1. Read every font face, in source priority order.
    families: dict[str, dict] = {}
    skipped: dict[str, str] = {}
    seen_styles: set[str] = set()
    for pattern, source, url, lic, lic_file in SOURCES:
        for path in sorted(args.src.glob(pattern)):
            for font in fontmod.discover([path]):
                face_family = base_family(read_faces(path)[font.index].family or font.name)
                fam_key = norm(face_family)
                if fam_key not in ALLOW_INSTALLED and (
                        fam_key in installed or norm(read_faces(path)[font.index].family) in installed):
                    continue
                if not font.usable and not font.reason.startswith("duplicate"):
                    skipped[f"{face_family} [{path.name}]"] = font.reason
                    continue
                style_key = norm(font.name)
                if style_key in seen_styles:
                    continue
                seen_styles.add(style_key)
                fam = families.setdefault(fam_key, {
                    "family": face_family, "slug": fontmod.slugify(face_family), "source": source, "url": url,
                    "license": lic, "license_file": lic_file, "restricted": lic == NONCOMMERCIAL,
                    "licence_class": licence_class(lic),
                    "styles": [], "_fonts": []})
                fam["styles"].append({"name": font.name, "file": path.name, "variation": font.variation})
                fam["_fonts"].append((font, path))

    # 2. Preview, stock-model OCR check, look-alike detection.
    tessdata = Path(subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True, encoding="utf-8", errors="replace")
                    .stdout.split('"')[1])
    out = args.out
    (out / "candidates").mkdir(parents=True, exist_ok=True)
    order = sorted(families.values(), key=lambda f: (f["source"] != "Google Fonts", f["family"].lower()))
    previews = {}
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for fam in order:
            fonts = [f for f, _ in fam["_fonts"]]
            pick = next((f for s in PREFERRED_STYLES for f in fonts if f.name.lower().endswith(s.lower())),
                        fonts[0])
            img = preview_png(pick)
            previews[fam["slug"]] = img
            p = Path(tmp) / f"{fam['slug']}.png"
            img.save(p)
            paths.append(p)
            fam["preview_style"] = pick.name
        texts = ocr_batch(paths, ModelSpec("installed", tessdata, "tam"), 7)
    for fam, text in zip(order, texts):
        truth = "".join(ch for ch in SAMPLE if ch == " " or fam["_fonts"][0][0].supports(ch))
        text = (text or "").replace("‌", "").replace("‍", "")
        fam["stock_cer"] = round(100 * align(truth, text)[0] / len(truth), 1)
        fam["stock_ocr"] = text
    sigs = {}
    for fam in order:
        pick = next(f for f, _ in fam["_fonts"] if f.name == fam["preview_style"])
        sigs[fam["slug"]] = glyph_signature(pick)
    for i, fam in enumerate(order):
        fam["looks_like"], fam["similarity"] = None, 0.0
        for other in order[:i]:
            if other["looks_like"]:
                continue
            s = similarity(sigs[fam["slug"]], sigs[other["slug"]])
            if s > fam["similarity"]:
                fam["similarity"] = round(s, 3)
                if s >= LOOKALIKE:
                    fam["looks_like"] = other["family"]

    # 3. Copy files and licenses, write catalog and page.
    for fam in order:
        dest = out / "candidates" / fam["slug"]
        dest.mkdir(parents=True, exist_ok=True)
        for _, path in fam["_fonts"]:
            shutil.copy2(path, dest / path.name)
        lic = args.src / fam["license_file"]
        if lic.exists():
            shutil.copy2(lic, dest / ("LICENSE-" + lic.name))
        fam["dir"] = f"candidates/{fam['slug']}"
    catalog = [{k: v for k, v in f.items() if not k.startswith("_")} for f in order]
    (out / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=1), encoding="utf-8")
    # Font folders for a model that can be published: openly licensed, not a near-copy.
    open_dirs = [f"{out}/{f['dir']}" for f in catalog if f["licence_class"] == "open" and not f["looks_like"]]
    (out / "open-fonts.txt").write_text("\n".join(open_dirs) + "\n", encoding="utf-8")
    write_page(out / "choose.html", catalog, previews, skipped, len(installed))
    print(f"{len(catalog)} new Tamil font families ({sum(len(f['styles']) for f in catalog)} styles); "
          f"{len(skipped)} unusable files skipped")
    for k, v in skipped.items():
        print(f"  skipped {k}: {v}")


def write_page(path: Path, catalog: list[dict], previews: dict, skipped: dict, n_installed: int) -> None:
    def img_tag(slug):
        buf = io.BytesIO()
        previews[slug].save(buf, "PNG", optimize=True)
        return f'<img alt="" src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}">'

    cards = []
    for i, f in enumerate(catalog, 1):
        recommended = f["looks_like"] is None
        cer = f["stock_cer"]
        level = "hard" if cer >= 15 else "mid" if cer >= 5 else "easy"
        dup = (f'<span class="dup">looks like {html.escape(f["looks_like"])}</span>' if f["looks_like"] else "")
        if f.get("restricted"):
            dup += ('<span class="dup" title="Fine for experiments. Ask the owner before publishing a model '
                    'trained on it.">non-commercial licence</span>')
        styles = ", ".join(html.escape(s["name"].replace(f["family"], "").strip() or "Regular")
                           for s in f["styles"])
        cards.append(f"""
<label class="card" data-slug="{f['slug']}" data-rec="{int(recommended)}" data-styles="{len(f['styles'])}"
       data-nc="{int(bool(f.get('restricted')))}">
  <div class="head">
    <input type="checkbox" {'checked' if recommended else ''}>
    <span class="num">{i}</span>
    <span class="name">{html.escape(f['family'])}</span>
    <span class="badge {level}" title="Character errors when the current Tamil model reads this sample">
      stock model: {cer}% errors</span>
    {dup}
  </div>
  <div class="preview">{img_tag(f['slug'])}</div>
  <div class="meta">{len(f['styles'])} style{'s' if len(f['styles']) > 1 else ''}: {styles}<br>
    {html.escape(f['source'])} · {html.escape(f['license'])}</div>
</label>""")
    total_styles = sum(len(f["styles"]) for f in catalog)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Choose Tamil fonts</title>
<style>
:root {{ --bg:#f7f6f2; --card:#fff; --ink:#1d1d1b; --muted:#6b6a64; --line:#e3e1da; --accent:#0b6e4f;
        --hard:#b3261e; --mid:#a15c00; --easy:#2e7d32; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#161614; --card:#21211e; --ink:#ecebe6; --muted:#a3a29b;
        --line:#3a3934; --accent:#5cc49a; --hard:#ff8a80; --mid:#ffb74d; --easy:#81c784; }}
  .preview img {{ filter: invert(1); }} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.45 system-ui,sans-serif; }}
header {{ padding:20px 16px 8px; max-width:1100px; margin:auto; }}
h1 {{ font-size:22px; margin:0 0 6px; }}
p {{ margin:4px 0; color:var(--muted); }}
.tools {{ display:flex; gap:8px; flex-wrap:wrap; margin:12px 0 4px; }}
button {{ border:1px solid var(--line); background:var(--card); color:var(--ink); border-radius:8px;
         padding:7px 12px; font:inherit; cursor:pointer; }}
button.primary {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
main {{ max-width:1100px; margin:auto; padding:0 16px 120px; display:grid; gap:10px; }}
.card {{ display:block; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px 12px;
        cursor:pointer; }}
.card:has(input:checked) {{ border-color:var(--accent); box-shadow:0 0 0 1px var(--accent) inset; }}
.head {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
.num {{ color:var(--muted); font-variant-numeric:tabular-nums; min-width:2ch; }}
.name {{ font-weight:600; }}
.badge {{ font-size:12px; border-radius:99px; padding:1px 8px; border:1px solid currentColor; }}
.badge.hard {{ color:var(--hard); }} .badge.mid {{ color:var(--mid); }} .badge.easy {{ color:var(--easy); }}
.dup {{ font-size:12px; color:var(--mid); }}
.preview {{ overflow-x:auto; margin:8px 0 4px; }}
.preview img {{ display:block; max-width:none; height:46px; }}
.meta {{ font-size:13px; color:var(--muted); }}
footer {{ position:fixed; bottom:0; left:0; right:0; background:var(--card); border-top:1px solid var(--line);
         padding:10px 16px; display:flex; gap:12px; align-items:center; justify-content:center; flex-wrap:wrap; }}
#count {{ font-weight:600; }}
textarea {{ position:absolute; left:-9999px; }}
</style></head><body>
<header>
  <h1>Choose Tamil fonts for training</h1>
  <p>{len(catalog)} Tamil font families ({total_styles} styles) that are not installed on your computer,
     openly licensed unless marked "non-commercial licence". Each preview was rendered by the trainer itself.</p>
  <p>The badge shows how many character errors the current Tamil model makes on that sample.
     Fonts it already reads well add less to training, and fonts with many errors add the most.
     "Looks like" marks a family that renders almost the same as one listed earlier; those start unticked.</p>
  <div class="tools">
    <button data-act="rec">Recommended</button><button data-act="all">Select all</button>
    <button data-act="none">Select none</button><button data-act="hard">Only fonts the model reads badly</button>
    <button data-act="open">Leave out non-commercial</button>
  </div>
</header>
<main>{''.join(cards)}</main>
<footer><span id="count"></span>
  <button class="primary" id="copy">Copy my selection</button><span id="copied"></span></footer>
<textarea id="out"></textarea>
<script>
const boxes = [...document.querySelectorAll('.card input')];
function update() {{
  const sel = boxes.filter(b => b.checked).map(b => b.closest('.card'));
  const styles = sel.reduce((n, c) => n + Number(c.dataset.styles), 0);
  document.getElementById('count').textContent =
    sel.length + ' families selected (' + styles + ' styles)' + (sel.length >= 35 ? ' ✓ 35 or more' : ' · need 35');
}}
boxes.forEach(b => b.addEventListener('change', update));
document.querySelectorAll('[data-act]').forEach(btn => btn.addEventListener('click', () => {{
  const a = btn.dataset.act;
  boxes.forEach(b => {{
    const c = b.closest('.card');
    if (a === 'open') {{ if (c.dataset.nc === '1') b.checked = false; return; }}
    b.checked = a === 'all' ? true : a === 'none' ? false : a === 'rec' ? c.dataset.rec === '1'
      : c.querySelector('.badge.hard, .badge.mid') !== null;
  }});
  update();
}}));
document.getElementById('copy').addEventListener('click', async () => {{
  const nums = boxes.filter(b => b.checked).map(b => b.closest('.card').querySelector('.num').textContent);
  const text = 'Use fonts: ' + nums.join(', ');
  try {{ await navigator.clipboard.writeText(text); }}
  catch (e) {{ const t = document.getElementById('out'); t.value = text; t.select(); document.execCommand('copy'); }}
  document.getElementById('copied').textContent = 'Copied. Paste it in the chat.';
}});
update();
</script></body></html>"""
    path.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
