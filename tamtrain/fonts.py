"""Find font files and decide which ones can render correct Unicode Tamil."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import tamil
from .sfnt import FontParseError, read_faces
from .util import TamTrainError

FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".otc"}
TAMIL_GSUB_TAGS = {"taml", "tml2"}


@dataclass
class Font:
    path: Path
    index: int
    name: str
    slug: str
    codepoints: set[int] = field(repr=False, default_factory=set)
    usable: bool = True
    reason: str = ""
    notes: list[str] = field(default_factory=list)
    variation: str | None = None   # named instance of a variable font, e.g. "Bold"
    old_letters: list[str] = field(default_factory=list)  # OpenType features that draw pre-1978 letters
    old_letters_default: bool = False                      # the font draws them without any feature

    def supports(self, text: str) -> bool:
        cps = self.codepoints
        return all(ord(ch) in cps for ch in text if ch != " ")

    def to_json(self) -> dict:
        return {"path": str(self.path), "index": self.index, "name": self.name, "slug": self.slug,
                "variation": self.variation, "old_letters": self.old_letters,
                "old_letters_default": self.old_letters_default}


# Optical-size instances of variable fonts are skipped. Width instances (Condensed, SemiCondensed…)
# are kept because condensed faces are common in newspaper headlines, but only in a few weights,
# so one variable font doesn't flood the training set with near-identical styles.
_SKIP_INSTANCE = re.compile(r"display|caption|small|text\b", re.I)
_WIDTH_WORD = re.compile(r"condensed|compressed|narrow|expanded|extended|wide", re.I)
_WIDTH_WEIGHTS = re.compile(r"^(?:\w*(?:condensed|compressed|narrow|expanded|extended|wide))\s*"
                            r"(?:regular|medium|bold|black)?$", re.I)


# Width axis values for condensed instances made from the axis when a variable font has a width
# axis but no named width instances (Google's Noto Tamil fonts, for example).
_SYNTH_WIDTHS = [(87.5, "SemiCondensed"), (75.0, "Condensed"), (62.5, "ExtraCondensed")]
_SYNTH_WEIGHTS = [(400, "Regular"), (700, "Bold")]


def _axis_key(axis: dict) -> str:
    name = axis["name"].decode("utf-8", "replace") if isinstance(axis["name"], bytes) else str(axis["name"])
    return {"weight": "wght", "width": "wdth", "slant": "slnt", "italic": "ital"}.get(name.lower(), name.lower())


def apply_variation(font, variation: str | None) -> None:
    """Select a variable-font instance: a named instance ("Bold") or axis values ("@wdth=75,wght=700")."""
    if not variation:
        return
    if variation.startswith("@"):
        want = dict(kv.split("=") for kv in variation[1:].split(","))
        axes = font.get_variation_axes()
        font.set_variation_by_axes([float(want.get(_axis_key(a), a["default"])) for a in axes])
    else:
        font.set_variation_by_name(variation)


def variable_instances(path: Path, index: int) -> list[tuple[str, str]]:
    """(style label, variation) for the instances of a variable font worth training on: every
    named instance (Light, Regular, Bold…) and, when the font has a width axis without named
    width instances, Regular and Bold at three condensed widths."""
    from PIL import ImageFont  # local import: fonts.py stays usable without Pillow for parsing

    try:
        ft = ImageFont.truetype(str(path), 20, index=index)
        names = [n.decode("utf-8", "replace") if isinstance(n, bytes) else str(n) for n in ft.get_variation_names()]
        axes = {_axis_key(a): a for a in ft.get_variation_axes()}
    except (OSError, AttributeError):
        return []
    out: list[tuple[str, str]] = []
    for name in names:
        if not name or _SKIP_INSTANCE.search(name) or any(name == n for n, _ in out):
            continue
        if _WIDTH_WORD.search(name) and not _WIDTH_WEIGHTS.match(name.replace(" ", "")):
            continue
        out.append((name, name))
    wdth = axes.get("wdth")
    if wdth and wdth["minimum"] < 100 and not any(_WIDTH_WORD.search(n) for n in names):
        italic = bool(names) and all("italic" in n.lower() for n in names)
        wght = axes.get("wght")
        for width, wname in ([] if italic else _SYNTH_WIDTHS):   # condensed italics are rare in print
            if width < wdth["minimum"] - 1:
                continue
            for weight, gname in _SYNTH_WEIGHTS:
                if wght and not wght["minimum"] <= weight <= wght["maximum"]:
                    continue
                spec = f"@wdth={max(width, wdth['minimum'])}" + (f",wght={weight}" if wght else "")
                out.append((f"{wname} {gname}", spec))
    return out


# ----------------------------------------------------------------------------- pre-1978 letters
# Before the 1978 script reform, ணா றா னா (and ணொ றொ னொ…) and ணை லை ளை னை were printed as
# ligatures. Many fonts still contain those shapes behind an OpenType feature. The old shapes
# are narrower than the modern ones (consonant + separate vowel sign), which is how they are found.
REFORM_AA = ["ணா", "றா", "னா"]
REFORM_AI = ["ணை", "லை", "ளை", "னை"]
OLD_LETTER_FEATURES = ["hist", "hlig", "dlig"] + [f"ss{i:02d}" for i in range(1, 21)] + ["salt", "cv01"]
_NARROWER = 0.92


def _old_shapes(widths: list[float], reference: list[float]) -> bool:
    narrower = sum(w < _NARROWER * r for w, r in zip(widths, reference))
    wider = any(w > 1.05 * r for w, r in zip(widths, reference))
    return narrower >= max(2, len(widths) - 1) and not wider


def detect_old_letters(font: "Font") -> tuple[list[str], bool]:
    """Return (features that turn on old letter shapes, whether old shapes are the default)."""
    from PIL import ImageFont

    try:
        ft = ImageFont.truetype(str(font.path), 100, index=font.index, layout_engine=ImageFont.Layout.RAQM)
        apply_variation(ft, font.variation)
        width = lambda t, f=None: ft.getlength(t, language="ta", features=f)  # noqa: E731
        # modern reference: consonant + the vowel sign as it is drawn after an ordinary consonant
        ka = width("க")
        ref = {t: width(t[0]) + width("க" + t[1]) - ka for t in REFORM_AA + REFORM_AI}
        base = {t: width(t) for t in ref}
    except (OSError, ValueError, KeyError):
        return [], False
    default = (_old_shapes([base[t] for t in REFORM_AA], [ref[t] for t in REFORM_AA])
               or _old_shapes([base[t] for t in REFORM_AI], [ref[t] for t in REFORM_AI]))
    if default:
        return [], True
    feats: list[str] = []
    for group in (REFORM_AA, REFORM_AI):
        if feats and _old_shapes([width(t, feats) for t in group], [base[t] for t in group]):
            continue  # the feature chosen for ணா றா னா covers ணை லை ளை னை too
        for tag in OLD_LETTER_FEATURES:
            try:
                ws = [width(t, [tag]) for t in group]
            except (OSError, ValueError):
                continue
            if _old_shapes(ws, [base[t] for t in group]):
                feats.append(tag)
                break
    return feats, False


def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return s or "font"


def find_font_files(sources: list[Path]) -> list[Path]:
    files: list[Path] = []
    for src in sources:
        if src.is_dir():
            files += sorted(p for p in src.rglob("*") if p.suffix.lower() in FONT_SUFFIXES and p.is_file())
        elif src.is_file():
            files.append(src)
        else:
            raise TamTrainError(f"Font path not found: {src}")
    return files


def assess(face) -> tuple[bool, str, list[str]]:
    """Return (usable, reason-if-not, notes) for one font face."""
    cps = face.codepoints
    tamil_cps = {c for c in cps if 0x0B80 <= c <= 0x0BFF}
    notes = []
    if not tamil_cps:
        has_latin = all(ord(c) in cps for c in "aeiouAEIOU")
        if has_latin:
            return False, "no Unicode Tamil; probably a legacy (TSCII/TAB/TAM/Bamini) font", notes
        return False, "no Tamil characters", notes
    missing = sorted(ch for ch in tamil.CORE_CHARS if ord(ch) not in cps)
    if missing:
        return False, "missing core Tamil characters: " + "".join(missing[:12]), notes
    if not face.has_gsub:
        return False, "no OpenType GSUB table: கு/டு-style ligatures cannot render", notes
    if not (face.gsub_scripts & TAMIL_GSUB_TAGS):
        return False, ("no Tamil OpenType script (taml/tml2): ெ/ே/ை would be drawn after the "
                       "consonant instead of before it"), notes
    if not all(ord(c) in cps for c in "aAzZ09"):
        notes.append("no Latin letters (English words are skipped for this font)")
    if not all(ord(c) in cps for c in tamil.TAMIL_DIGITS):
        notes.append("no Tamil digits")
    if not all(ord(c) in cps for c in tamil.GRANTHA):
        notes.append("missing some Grantha letters")
    return True, "", notes


def discover(sources: list[Path], include: list[str] | None = None,
             exclude: list[str] | None = None, old_letters: bool = True) -> list[Font]:
    """Return every font face found, each marked usable or not (with the reason).
    With old_letters, usable fonts are also checked for pre-1978 letter shapes."""
    fonts: list[Font] = []
    seen: dict[str, Font] = {}
    slugs: set[str] = set()
    for path in find_font_files(sources):
        try:
            faces = read_faces(path)
        except (FontParseError, OSError) as exc:
            fonts.append(Font(path, 0, path.name, slugify(path.stem), usable=False, reason=str(exc)))
            continue
        for face in faces:
            usable, reason, notes = assess(face)
            # A variable font becomes one entry per named weight/style instance.
            instances = variable_instances(path, face.index) if face.is_variable and usable else []
            variants = [(f"{face.family} {label}", label, spec) for label, spec in instances] or \
                       [(face.full_name or path.stem, face.style, None)]
            for name, style, variation in variants:
                label = f"{name} [{path.name}]"
                if include and not any(fnmatch.fnmatch(label.lower(), p.lower()) for p in include):
                    continue
                if exclude and any(fnmatch.fnmatch(label.lower(), p.lower()) for p in exclude):
                    continue
                ok, why = usable, reason
                # the same style can come under two family names ("Noto Sans Tamil Condensed" + "Bold"
                # in a static font, "Noto Sans Tamil" + "Condensed Bold" in a variable one)
                key = re.sub(r"[^a-z0-9]", "", f"{face.family} {style}".lower().replace("regular", ""))
                replaces = None
                if ok and key in seen:
                    # keep the copy with more characters (newer versions add Latin, digits…)
                    if len(face.codepoints) > len(seen[key].codepoints):
                        replaces = seen[key]
                    else:
                        ok, why = False, f"duplicate of {seen[key].path.name}"
                slug = slugify(name)
                base, n = slug, 2
                while slug in slugs:
                    slug, n = f"{base}_{n}", n + 1
                slugs.add(slug)
                font = Font(path, face.index, name, slug, face.codepoints, ok, why, list(notes), variation)
                if replaces is not None:
                    replaces.usable, replaces.reason = False, f"duplicate of {path.name} (which has more characters)"
                if ok:
                    seen[key] = font
                if ok and old_letters:
                    font.old_letters, font.old_letters_default = detect_old_letters(font)
                fonts.append(font)
    return fonts


def print_report(fonts: list[Font]) -> None:
    usable = [f for f in fonts if f.usable]
    skipped = [f for f in fonts if not f.usable]
    print(f"\nUsable Tamil fonts: {len(usable)}")
    for f in usable:
        notes = list(f.notes)
        if f.old_letters:
            notes.append("old letter shapes via " + "+".join(f.old_letters))
        elif f.old_letters_default:
            notes.append("draws old letter shapes")
        extra = f"  ({'; '.join(notes)})" if notes else ""
        print(f"  + {f.name}  [{f.path.name}]{extra}")
    n_old = sum(bool(f.old_letters or f.old_letters_default) for f in usable)
    if n_old:
        print(f"\n  {n_old} fonts can draw pre-1978 letter shapes (ணா றா னா / ணை லை ளை னை)")
    if skipped:
        print(f"\nSkipped: {len(skipped)}")
        for f in skipped:
            print(f"  - {f.name}  [{f.path.name}]: {f.reason}")
