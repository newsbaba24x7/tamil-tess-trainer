"""Tamil script data, validation and coverage-text generation."""

from __future__ import annotations

import random
import unicodedata

VOWELS = "அஆஇஈஉஊஎஏஐஒஓஔ"
AYTHAM = "ஃ"
CONSONANTS = "கஙசஞடணதநபமயரலவழளறன"
GRANTHA = "ஜஶஷஸஹ"
VOWEL_SIGNS = ["", "ா", "ி", "ீ", "ு", "ூ", "ெ", "ே", "ை", "ொ", "ோ", "ௌ"]
PULLI = "்"
TAMIL_DIGITS = "௦௧௨௩௪௫௬௭௮௯"
TAMIL_SYMBOLS = "௰௱௲௳௴௵௶௷௸௹௺ௐ"

# Characters every usable Tamil font must contain.
CORE_CHARS = set(VOWELS + AYTHAM + CONSONANTS + PULLI + "".join(VOWEL_SIGNS))

CONSONANT_SET = set(CONSONANTS + GRANTHA)
# Dependent marks: vowel signs, pulli, au length mark. They must follow a consonant.
DEPENDENT = {chr(c) for c in range(0x0BBE, 0x0BCE)} | {"ௗ"}
TAMIL_BLOCK = {chr(c) for c in range(0x0B80, 0x0C00) if unicodedata.name(chr(c), "")}

# Punctuation/symbols allowed in training text besides ASCII letters and digits.
PUNCT = set(".,;:!?-()[]{}\"'/%&*+=@#") | set("“”‘’–—…•·₹°×")
# Invisible characters that only confuse OCR training.
STRIP_CHARS = dict.fromkeys(map(ord, "​‌‍⁠﻿­"), None)


def normalize(text: str) -> str:
    """NFC-normalize, drop zero-width joiners/BOM/soft hyphens, collapse spaces."""
    text = unicodedata.normalize("NFC", text).translate(STRIP_CHARS)
    return " ".join(text.split())


def is_tamil_char(ch: str) -> bool:
    return ch in TAMIL_BLOCK


def is_tamil_number(ch: str) -> bool:
    """Tamil digits ௦-௯ and number signs ௰ ௱ ௲."""
    return 0x0BE6 <= ord(ch) <= 0x0BF2


def valid_tamil_sequence(word: str) -> bool:
    """True if every dependent mark follows a consonant (one mark per consonant)."""
    prev_is_bare_consonant = False
    for ch in word:
        if ch in DEPENDENT:
            if not prev_is_bare_consonant:
                return False
            prev_is_bare_consonant = False
        else:
            prev_is_bare_consonant = ch in CONSONANT_SET
    return True


def clean_token(token: str, allow_latin: bool) -> str | None:
    """Return the token if it is acceptable training text, else None."""
    core = token.strip("".join(PUNCT))
    if not core:  # pure punctuation
        return token if all(ch in PUNCT for ch in token) and len(token) <= 3 else None
    has_tamil = any(is_tamil_char(ch) for ch in core)
    for ch in token:
        if ch in PUNCT or is_tamil_char(ch) or ch.isdigit() and ch.isascii():
            continue
        if ch.isascii() and ch.isalpha():
            if not allow_latin or has_tamil:
                return None  # Latin letters mixed into a Tamil word = corpus noise
            continue
        return None
    if has_tamil:
        # Inside a Tamil word allow only Tamil, hyphen and digits ("2024-ல்", "1990களில்");
        # symbols such as "அதத$ய(யதபத" are corpus noise.
        if any(not (is_tamil_char(ch) or ch == "-" or (ch.isdigit() and ch.isascii())) for ch in core):
            return None
        # Tamil digits look like letters (௨/உ, ௧/க, ௭/எ, ௮/அ); OCR'd corpora often contain
        # "௨ன்னை" for "உன்னை". A word mixing Tamil digits/number signs and letters is noise.
        has_letters = any(is_tamil_char(ch) and not is_tamil_number(ch) for ch in core)
        if has_letters and any(is_tamil_number(ch) for ch in core):
            return None
        if not valid_tamil_sequence(core):
            return None
    return token


# Conjuncts that fonts draw as one ligature across two clusters: க்ஷ and ஸ்ரீ/ஶ்ரீ.
_JOINED = {("க்", "ஷ"), ("ஸ்", "ரீ"), ("ஶ்", "ரீ")}


def clusters(word: str) -> list[str]:
    """Split text into pieces that can be drawn separately: a letter with its vowel sign or
    pulli stays together (so ெ ே ை still go before the consonant), and the க்ஷ and ஸ்ரீ
    ligatures stay whole. Used to add letter-spacing without breaking the script."""
    out: list[str] = []
    for ch in word:
        if out and (ch in DEPENDENT or ch in "\u200c\u200d"):
            out[-1] += ch
        else:
            out.append(ch)
    merged: list[str] = []
    for c in out:
        if merged and any(merged[-1].endswith(a) and c.startswith(b) for a, b in _JOINED):
            merged[-1] += c
        else:
            merged.append(c)
    return merged


def syllables(include_grantha: bool = True) -> list[str]:
    """All vowels, consonant+pulli and consonant+vowel-sign combinations."""
    out = list(VOWELS) + [AYTHAM]
    cons = CONSONANTS + (GRANTHA if include_grantha else "")
    for c in cons:
        out.append(c + PULLI)
        for vs in VOWEL_SIGNS:
            out.append(c + vs)
    if include_grantha:
        out += ["க்ஷ", "க்ஷ்", "க்ஷா", "க்ஷி", "ஸ்ரீ", "ஶ்ரீ"]
    return out


def coverage_lines(n: int, rng: random.Random, *, include_grantha=True, include_digits=True,
                   tamil_digit_share: float = 0.0, include_symbols=False) -> list[str]:
    """Lines of pseudo-words that cycle through every Tamil syllable.

    Real text rarely contains rare syllables (e.g. ஙெ, ஞொ); these lines make sure
    every glyph combination is seen in every font. Numbers use ASCII digits; a share
    `tamil_digit_share` of them use Tamil digits (௧௨௩), which are rare in real print and
    look like letters (௬/சு, ௦/ம), so too many teach the model to see digits in damaged letters.
    """
    sylls = syllables(include_grantha)
    pool: list[str] = []
    lines = []
    for _ in range(n):
        words = []
        for _ in range(rng.randint(5, 9)):
            if include_digits and rng.random() < 0.08:
                digits = TAMIL_DIGITS if rng.random() < tamil_digit_share else "0123456789"
                words.append("".join(rng.choice(digits) for _ in range(rng.randint(1, 4))))
                continue
            if include_symbols and rng.random() < 0.03:
                words.append(rng.choice(TAMIL_SYMBOLS))
                continue
            k = rng.randint(2, 4)
            if len(pool) < k:
                pool = sylls[:]
                rng.shuffle(pool)
            word = [pool.pop() for _ in range(k)]
            # Independent vowels only start a word; aytham never does. Extra vowels go back.
            vowels = [s for s in word if s in VOWELS]
            rest = [s for s in word if s not in VOWELS]
            pool[:0] = vowels[1:]
            word = vowels[:1] + rest
            if word and word[0] == AYTHAM:
                word = word[1:] + word[:1]
            words.append("".join(word))
        line = " ".join(words)
        if rng.random() < 0.3:
            line += rng.choice(".,;:!?")
        lines.append(line)
    return lines
