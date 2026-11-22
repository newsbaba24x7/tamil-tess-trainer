#!/usr/bin/env python3
"""Step 4.1 - Render synthetic text-line images + ground truth (tesstrain layout).

For each line in a corpus TSV (id, category, text) writes OUT/<id>.png and OUT/<id>.gt.txt,
plus OUT/manifest.tsv (id, category, font, latin font, px size, augmentations, fonts used).

* Fontconfig is restricted to the files in fonts.tsv for the chosen roles, so no other
  installed font can be picked up by fallback. Every run records the fonts Pango really used.
* Tamil text uses the chosen Tamil font; runs that start with a Latin letter use Noto Sans
  (with sans Tamil fonts) or Noto Serif (with serif Tamil fonts) in the matching weight.
* Lines with any glyph that no allowed font can draw are skipped and logged.

  python3 -I 03_render_lines.py --corpus corpus/train.tsv --fonts fonts.tsv --role train --out lines/train
"""
import argparse, html, multiprocessing as mp, os, random, re, sys
from pathlib import Path

LATIN_RUN = re.compile(r"[A-Za-z][A-Za-z0-9._+\-/@:#&\\^`~]*")
FC_WEIGHT_TO_PANGO = {0: 100, 40: 200, 50: 300, 55: 350, 75: 380, 80: 400, 100: 500, 180: 600, 200: 700, 205: 800, 210: 900, 215: 1000}
G = {}


def fc(path, fmt):
    import subprocess
    return subprocess.run(["fc-query", "-f", fmt, path], capture_output=True, text=True).stdout.split("\n")[0]


def load_fonts(tsv, roles):
    fonts = []
    for line in open(tsv, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        role, cls, lic, ev, path = line.rstrip("\n").split("\t")
        path = os.path.expanduser(path)          # fonts.tsv writes user-installed fonts as ~/.local/share/fonts/...
        if role in roles:
            fam = fc(path, "%{family[0]}")
            w = float((fc(path, "%{weight}") or "80").strip("[]").split()[0])
            s = float((fc(path, "%{slant}") or "0").strip("[]").split()[0])
            near = min(FC_WEIGHT_TO_PANGO, key=lambda k: abs(k - w))
            fonts.append({"role": role, "cls": cls, "path": path, "family": fam,
                          "weight": FC_WEIGHT_TO_PANGO[near], "italic": s > 0})
    return fonts


def write_fontconf(fonts, out):
    d = out / "_fonts"; d.mkdir(parents=True, exist_ok=True)
    for f in fonts:
        link = d / Path(f["path"]).name
        if not link.exists():
            link.symlink_to(f["path"])
    conf = out / "_fonts.conf"
    conf.write_text(f"""<?xml version="1.0"?>\n<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><dir>{html.escape(str(d))}</dir><cachedir>{html.escape(str(out / '_fccache'))}</cachedir></fontconfig>\n""")
    return conf


def init(conf):
    os.environ["FONTCONFIG_FILE"] = str(conf)
    import gi
    gi.require_version("Pango", "1.0"); gi.require_version("PangoCairo", "1.0")
    from gi.repository import Pango, PangoCairo, GLib
    import cairo, numpy, PIL.Image, PIL.ImageFilter
    G.update(Pango=Pango, PangoCairo=PangoCairo, GLib=GLib, cairo=cairo, np=numpy, Image=PIL.Image, Filter=PIL.ImageFilter)


SYMBOL_RUN = re.compile(r"[0-9₹€£$%&@#*+=/\\|<>~^`_.,;:!?'\"“”‘’()\[\]{}—–…•°×½¼-]+")


def markup(text, latin, symbols_in_latin=False):
    """Latin-letter runs always use the Latin font; digit/punctuation runs too when
    symbols_in_latin is set (otherwise they use the Tamil font's own glyphs)."""
    GLib = G["GLib"]; out, pos = [], 0
    rx = re.compile(f"{LATIN_RUN.pattern}|{SYMBOL_RUN.pattern}") if symbols_in_latin else LATIN_RUN
    for m in rx.finditer(text):
        out.append(GLib.markup_escape_text(text[pos:m.start()], -1))
        out.append(f'<span font_family="{latin["family"]}" weight="{latin["weight"]}" style="{"italic" if latin["italic"] else "normal"}">'
                   f'{GLib.markup_escape_text(m.group(), -1)}</span>')
        pos = m.end()
    out.append(GLib.markup_escape_text(text[pos:], -1))
    return "".join(out)


def layout_for(ctx, font, px, mk):
    Pango, PangoCairo = G["Pango"], G["PangoCairo"]
    lay = PangoCairo.create_layout(ctx)
    fo = G["cairo"].FontOptions(); fo.set_antialias(G["cairo"].ANTIALIAS_GRAY); fo.set_hint_style(G["cairo"].HINT_STYLE_NONE)
    PangoCairo.context_set_font_options(lay.get_context(), fo)
    fd = Pango.FontDescription(); fd.set_family(font["family"]); fd.set_weight(font["weight"])
    fd.set_style(Pango.Style.ITALIC if font["italic"] else Pango.Style.NORMAL); fd.set_absolute_size(px * Pango.SCALE)
    lay.set_font_description(fd); lay.set_markup(mk, -1)
    return lay


def used_families(lay):
    fams, it = set(), lay.get_iter()
    while True:
        run = it.get_run_readonly()
        if run is not None:
            fams.add(run.item.analysis.font.describe().get_family())
        if not it.next_run():
            return fams


def render(job):
    lid, cat, text, font, latin, seed, out, opt = job
    np, Image, Filter, cairo, PangoCairo = G["np"], G["Image"], G["Filter"], G["cairo"], G["PangoCairo"]
    r = random.Random(seed)
    px = r.uniform(34, 62)                      # ~8-15 pt at 300 DPI
    # no random draw when the option is off, so round-1 renders reproduce exactly
    sym_latin = opt["symbols_latin"] > 0 and r.random() < opt["symbols_latin"]
    mk = markup(text, latin, sym_latin)
    probe = cairo.ImageSurface(cairo.FORMAT_RGB24, 8, 8)
    lay = layout_for(cairo.Context(probe), font, px, mk)
    if lay.get_unknown_glyphs_count():
        return ("skip", lid, "unknown glyphs")
    _, logical = lay.get_pixel_extents()
    padx, pady = r.randint(8, 30), r.randint(6, 18)
    w, h = logical.width + 2 * padx, logical.height + 2 * pady
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h); ctx = cairo.Context(surf)
    ctx.set_source_rgb(1, 1, 1); ctx.paint(); ctx.set_source_rgb(0, 0, 0)
    lay = layout_for(ctx, font, px, mk); ctx.move_to(padx - logical.x, pady - logical.y)
    PangoCairo.show_layout(ctx, lay); surf.flush()
    fams = used_families(lay)
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(h, surf.get_stride() // 4, 4)[:, :w, 1]
    img = Image.fromarray(a.copy(), "L"); aug = ["symlatin"] if sym_latin else []
    if opt["strong"]:
        if r.random() < .4:                     # horizontal stretch: condensed / expanded designs
            f = r.uniform(.85, 1.15); img = img.resize((max(1, int(img.width * f)), img.height), Image.BICUBIC); aug.append(f"xscale{f:.2f}")
        if px > 45 and r.random() < .4:         # stroke weight: MinFilter thickens dark text, MaxFilter thins it
            if r.random() < .5:
                img = img.filter(Filter.MinFilter(3)); aug.append("bolder")
            else:
                img = img.filter(Filter.MaxFilter(3)); aug.append("thinner")
    if r.random() < .5:
        ang = r.uniform(-.6, .6); img = img.rotate(ang, resample=Image.BICUBIC, expand=True, fillcolor=255); aug.append(f"rot{ang:.2f}")
    if r.random() < .3:
        f = r.uniform(.5, .8); sz = img.size
        img = img.resize((max(1, int(sz[0] * f)), max(1, int(sz[1] * f))), Image.BILINEAR).resize(sz, Image.BILINEAR); aug.append(f"lowres{f:.2f}")
    if r.random() < .6:
        rad = r.uniform(.3, 1.0); img = img.filter(Filter.GaussianBlur(rad)); aug.append(f"blur{rad:.2f}")
    x = np.asarray(img, np.float32) / 255.0
    ink, paper = r.uniform(0, 80), r.uniform(190, 255)
    x = ink + x * (paper - ink); aug.append(f"ink{ink:.0f}/paper{paper:.0f}")
    if r.random() < .5:
        sd = r.uniform(3, 14); x = x + np.random.default_rng(seed).normal(0, sd, x.shape); aug.append(f"noise{sd:.1f}")
    if r.random() < .12:
        x = np.where(x < (ink + paper) / 2, 0, 255); aug.append("binary")
    Image.fromarray(np.clip(x, 0, 255).astype(np.uint8), "L").save(out / f"{lid}.png", optimize=False)
    (out / f"{lid}.gt.txt").write_text(text + "\n", encoding="utf-8")
    return ("ok", lid, cat, font["family"] + (f" w{font['weight']}" + (" italic" if font["italic"] else "")),
            latin["family"] + f" w{latin['weight']}", f"{px:.1f}", " ".join(aug), ";".join(sorted(fams)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True); ap.add_argument("--fonts", required=True)
    ap.add_argument("--role", choices=["train", "eval"], required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=os.cpu_count()); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--symbols-latin", type=float, default=0.5,
                    help="share of lines whose digits/punctuation use the Latin font (round 1: 0)")
    ap.add_argument("--strong-aug", type=int, default=1, help="horizontal stretch + stroke weight (round 1: 0)")
    a = ap.parse_args()
    opt = {"symbols_latin": a.symbols_latin, "strong": bool(a.strong_aug)}
    out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts(a.fonts, {a.role, "latin", "train"} if a.role == "eval" else {"train", "latin"})
    conf = write_fontconf(fonts, out)
    tamil = [f for f in fonts if f["role"] == a.role]
    latin = {c: [f for f in fonts if f["role"] == "latin" and f["cls"] == c] for c in ("sans", "serif")}
    rows = [l.rstrip("\n").split("\t") for l in open(a.corpus, encoding="utf-8")][: a.limit or None]
    r = random.Random(a.seed); jobs = []
    for i, (lid, cat, text) in enumerate(rows):
        f = tamil[i % len(tamil)] if a.role == "eval" else r.choice(tamil)
        lat = [x for x in latin[f["cls"]] if (x["weight"] >= 600) == (f["weight"] >= 600)]
        lat = r.choice([x for x in lat if x["italic"] == f["italic"]] or lat)
        jobs.append((lid, cat, text, f, lat, a.seed * 1000003 + i, out, opt))
    with mp.get_context("spawn").Pool(a.jobs, initializer=init, initargs=(conf,)) as pool:
        res = pool.map(render, jobs, chunksize=32)
    allowed = {f["family"] for f in fonts}
    ok = [x for x in res if x[0] == "ok"]; skipped = [x for x in res if x[0] == "skip"]
    stray = {fam for x in ok for fam in x[7].split(";") if fam not in allowed}
    with open(out / "manifest.tsv", "w", encoding="utf-8") as m:
        m.write("id\tcategory\tfont\tlatin_font\tpx\taugment\tfonts_used\n")
        for x in ok:
            m.write("\t".join(x[1:]) + "\n")
    (out / "skipped.txt").write_text("".join(f"{x[1]}\t{x[2]}\n" for x in skipped), encoding="utf-8")
    print(f"rendered {len(ok)}, skipped {len(skipped)}, fonts used outside the allowed list: {sorted(stray) or 'none'}")
    if stray:
        sys.exit("ERROR: a font outside fonts.tsv was used")


if __name__ == "__main__":
    main()
