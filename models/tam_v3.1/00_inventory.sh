#!/usr/bin/env bash
# Step 1.1 / 1.2 — Release & artifact inventory for tam_v3 vs upstream `tam`.
#
# Downloads the pinned release (v3.0.0) and the three upstream tam.traineddata files,
# verifies checksums, lists every component (combine_tessdata -d), prints the LSTM
# network spec (combine_tessdata -l), unpacks each model (combine_tessdata -u) and
# diffs the character sets.
#
# Usage: bash 00_inventory.sh [WORK_DIR]      (default: ./work)
set -euo pipefail

TAG=${TAG:-v3.0.0}
SRC=${SRC:-newsbaba24x7/tamil-tess-trainer}
WORK=$(mkdir -p "${1:-$PWD/work}" && cd "${1:-$PWD/work}" && pwd)
mkdir -p "$WORK/release" "$WORK/upstream" "$WORK/unpack"

echo "### 1. Pinned release $SRC@$TAG"
gh release view "$TAG" -R "$SRC" --json tagName,publishedAt,targetCommitish \
  --jq '"tag=\(.tagName) published=\(.publishedAt) target=\(.targetCommitish)"'
gh api "repos/$SRC/git/ref/tags/$TAG" --jq '"tag commit=\(.object.sha)"'
( cd "$WORK/release"
  gh release download "$TAG" -R "$SRC" --clobber \
     -p 'tam_v3.traineddata' -p 'tam_v3_fast.traineddata' -p SHA256SUMS
  grep traineddata SHA256SUMS | sha256sum -c - )

echo; echo "### 2. Upstream tam.traineddata (main branch of each repo)"
for r in tessdata tessdata_fast tessdata_best; do
  curl -sSfL -o "$WORK/upstream/tam.$r.traineddata" \
    "https://raw.githubusercontent.com/tesseract-ocr/$r/main/tam.traineddata"
done
( cd "$WORK/upstream" && sha256sum *.traineddata )

echo; echo "### 3. Components, version strings and network specs"
for f in "$WORK"/release/*.traineddata "$WORK"/upstream/*.traineddata; do
  echo "== $(basename "$f")  ($(stat -c %s "$f") bytes)"
  combine_tessdata -d "$f" 2>&1 | grep -vE '^\s*$' | sed 's/^/   /'
  combine_tessdata -l "$f" 2>&1 | grep '^LSTM:' | sed 's/^/   /'
done

echo; echo "### 4. Unpack (combine_tessdata -u)"
unpack() { mkdir -p "$WORK/unpack/$2"; combine_tessdata -u "$1" "$WORK/unpack/$2/tam" >/dev/null 2>&1; ls "$WORK/unpack/$2"; }
unpack "$WORK/release/tam_v3.traineddata"            v3_best
unpack "$WORK/release/tam_v3_fast.traineddata"       v3_int
unpack "$WORK/upstream/tam.tessdata_best.traineddata" up_best
unpack "$WORK/upstream/tam.tessdata.traineddata"      up_std
unpack "$WORK/upstream/tam.tessdata_fast.traineddata" up_fast
for d in up_best up_std up_fast; do echo "-- $d config:"; cat "$WORK/unpack/$d/tam.config" 2>/dev/null || echo "   (none)"; done

echo; echo "### 5. Character-set diff (upstream best -> v3)"
python3 -I - "$WORK/unpack/up_best/tam.lstm-unicharset" "$WORK/unpack/v3_best/tam.lstm-unicharset" <<'EOF'
import sys, unicodedata as ud
def load(p):
    L = open(p, encoding="utf-8").read().splitlines()
    return [l.split(" ")[0] for l in L[1:int(L[0]) + 1]]
old, new = load(sys.argv[1]), load(sys.argv[2])
add = [u for u in new if u not in old]; rem = [u for u in old if u not in new]
print(f"unichars: upstream={len(old)} v3={len(new)} added={len(add)} removed={len(rem)}")
bad = [u for u in add if any(ud.category(c) in ("Cc", "Cf", "Co", "Cn") for c in u)]
cjk = [u for u in add if any("⺀" <= c <= "鿿" for c in u)]
print("added:", " ".join(repr(u) for u in add))
print("CONTROL/FORMAT chars in v3 unicharset:", [hex(ord(c)) for u in bad for c in u] or "none")
print("CJK chars in v3 unicharset:", cjk or "none")
EOF
