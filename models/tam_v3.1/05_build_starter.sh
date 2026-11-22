#!/usr/bin/env bash
# Step 5.1 - Build the v3.1 "starter" traineddata: clean unicharset, recoder and dictionaries.
# lstmtraining later maps v3's output layer onto this character set (--old_traineddata).
#
# combine_lang_model needs a radical-stroke table; it is only used for Han characters, and the
# v3.1 character set has none, so a comment-only table is supplied (no langdata download).
# Usage: bash 05_build_starter.sh CLEAN_DIR OUT_DIR
set -euo pipefail
CLEAN=$(cd "$1" && pwd); OUT=$(mkdir -p "$2" && cd "$2" && pwd)
mkdir -p "$OUT/script_dir"
printf '# Han radical-stroke table intentionally empty: the tam v3.1 character set has no Han characters.\n' \
  > "$OUT/script_dir/radical-stroke.txt"
# PUNCS=... selects another punctuation-pattern list (release: puncs_quotes.txt from 16_quote_patterns.py)
combine_lang_model --input_unicharset "$CLEAN/tam.unicharset" --script_dir "$OUT/script_dir" \
  --words "$CLEAN/words.txt" --puncs "${PUNCS:-$CLEAN/puncs.txt}" --numbers "$CLEAN/numbers.txt" \
  --output_dir "$OUT" --lang tam > "$OUT/combine_lang_model.log" 2>&1
# Replace the recoder with the identity layout used by upstream tam and tam_v3 (unichar i -> code i,
# CTC blank = code 2 "|Broken|0|1"). Tesseract 5.5's combine_lang_model instead puts "Joined" and
# "Broken" on a new last code and shifts all others; lstmtraining's MapRecoder then copies the old
# "Joined" weights into the blank output, which raised CER from 3.1% to 14.4% before any training.
# Format (UnicharCompress::Serialize): int32 count, then per unichar: int8 self_normalized,
# int32 length, length x int32 codes (little-endian).
python3 -I - "$OUT/tam/tam.unicharset" "$OUT/tam/tam.lstm-recoder" <<'EOF'
import struct, sys
n = int(open(sys.argv[1], encoding="utf-8").readline())
with open(sys.argv[2], "wb") as f:
    f.write(struct.pack("<i", n))
    for i in range(n):
        f.write(struct.pack("<bii", 1, 1, i))
print(f"identity recoder: {n} codes, blank = code 2")
EOF
combine_tessdata -o "$OUT/tam/tam.traineddata" "$OUT/tam/tam.lstm-recoder" >/dev/null
combine_tessdata -d "$OUT/tam/tam.traineddata" 2>&1 | grep -v '^$'
python3 -I - "$OUT/tam/tam.unicharset" <<'EOF'
import sys, unicodedata as ud
L = open(sys.argv[1], encoding="utf-8").read().splitlines()
u = [l.split(" ")[0] for l in L[1:int(L[0]) + 1]]
bad = [x for x in u if x not in ("NULL", "Joined", "|Broken|0|1") and any(ud.category(c)[0] == "C" for c in x)]
print(f"starter unicharset: {len(u)} entries; control/format characters: {bad or 'none'}")
EOF
