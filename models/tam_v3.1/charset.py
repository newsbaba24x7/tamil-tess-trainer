"""tam v3.1 character policy: one place that defines what the model may output.

Imported by the other v3.1 scripts. Run directly to print the policy.
"""
import re
import unicodedata

# 1. Tamil: every assigned code point U+0B83-U+0BFA (U+0B82 ANUSVARA is not used in Tamil text).
TAMIL = {chr(c) for c in range(0x0B83, 0x0BFB) if unicodedata.category(chr(c)) != "Cn"}
TAMIL_NUMERALS = "௦௧௨௩௪௫௬௭௮௯௰௱௲"           # 13 code points: digits 0-9, 10, 100, 1000
TAMIL_SYMBOLS = "௳௴௵௶௷௸௹௺"                 # day, month, year, debit, credit, as above, rupee, number
# 2. Basic Latin: every printable ASCII character (letters, digits, punctuation, ^ and `).
ASCII = {chr(c) for c in range(0x21, 0x7F)}
# 3. Typographic punctuation and symbols found in Tamil print (all except × were already in v3 or upstream tam).
EXTRA = set("‘’“”–—…•°₹€£©×½¼।॥")
ALLOWED = TAMIL | ASCII | EXTRA
ALLOWED_WITH_SPACE = ALLOWED | {" "}

# Characters rewritten before checking (mis-encoded or invisible).
MAP = {
    "\u0093": "“", "\u0094": "”",                 # Windows-1252 smart quotes read as C1 controls
    "−": "-", "‐": "-", "‑": "-",   # minus / hyphen variants
    "′": "'", "″": '"', "‛": "'",
    " ": " ", " ": " ", " ": " ", " ": " ", " ": " ",
}
DELETE = dict.fromkeys(map(ord, "​‌‍‎‏⁠﻿­"))

# The 36 numeral forms requested for training (sequences of the 13 code points above).
NUMERAL_FORMS = ("௦ ௧ ௨ ௩ ௪ ௫ ௬ ௭ ௮ ௯ ௰ ௱ ௲ ௧௦ ௨௦ ௩௦ ௪௦ ௫௦ ௬௦ ௭௦ ௮௦ ௯௦ ௱௦ "
                 "௨௱ ௩௱ ௪௱ ௫௱ ௬௱ ௭௱ ௮௱ ௯௱ ௲௦ ௨௲ ௩௲ ௪௲ ௫௲").split()
assert len(NUMERAL_FORMS) == 36


def normalize(s):
    s = unicodedata.normalize("NFC", s)
    s = "".join(MAP.get(c, c) for c in s).translate(DELETE)
    return re.sub(r"[ \t]+", " ", unicodedata.normalize("NFC", s)).strip()


def ok(s):
    return all(c in ALLOWED_WITH_SPACE for c in s)


if __name__ == "__main__":
    print(f"Tamil {len(TAMIL)}, ASCII {len(ASCII)}, extra {len(EXTRA)}, total {len(ALLOWED)}")
    print("extra:", " ".join(sorted(EXTRA)))
    print("numeral forms:", len(NUMERAL_FORMS))
