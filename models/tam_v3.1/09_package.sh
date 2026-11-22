#!/usr/bin/env bash
# Step 9 - Make the three release files, each matching its upstream repo:
#   tam_best_v3.1.traineddata  float   Lfx192 -> tessdata_best (config as upstream best)
#   tam_v3.1.traineddata       integer Lfx192 -> tessdata      (best converted to int; config OEM 1 as upstream)
#   tam_fast_v3.1.traineddata  integer Lfx128 -> tessdata_fast (no config, as upstream fast)
# Each gets a version string recording release, variant, date and network.
# BEST_LSTM / FAST_LSTM: float runtime .lstm files (after interpolation / grafting) or lstmtraining checkpoints.
# STARTER_TRAINEDDATA supplies the character set, recoder and dictionaries (release: starter_q, see README).
# Usage: bash 09_package.sh STARTER_TRAINEDDATA BEST_LSTM FAST_LSTM DIST_DIR
set -euo pipefail
T=$1; BEST=$2; FAST=$3; DIST=$(mkdir -p "$4" && cd "$4" && pwd)
D=$(date -u +%Y%m%d); P=$(mktemp -d "$DIST/.pkg.XXXX")
NET192='[1,36,0,1Ct3,3,16Mp3,3Lfys48Lfx96Lrx96Lfx192O1c1]'; NET128='[1,36,0,1Ct3,3,16Mp3,3Lfys48Lfx96Lrx96Lfx128O1c1]'
lstmtraining --stop_training                  --continue_from "$BEST" --traineddata "$T" --model_output "$P/best.traineddata" >/dev/null 2>&1
lstmtraining --stop_training --convert_to_int --continue_from "$BEST" --traineddata "$T" --model_output "$P/std.traineddata"  >/dev/null 2>&1
lstmtraining --stop_training --convert_to_int --continue_from "$FAST" --traineddata "$T" --model_output "$P/fast.traineddata" >/dev/null 2>&1
# DROP_WORD_DAWG=1 (optional, not used for the release): ship without the word dictionary. Before the
# single-quote patterns (16_quote_patterns.py) existed, the dictionary made the decoder drop quotes.
if [[ ${DROP_WORD_DAWG:-0} == 1 ]]; then
  for f in best std fast; do
    u=$(mktemp -d "$P/u.XXXX"); combine_tessdata -u "$P/$f.traineddata" "$u/tam." >/dev/null
    rm -f "$u/tam.lstm-word-dawg"; combine_tessdata "$u/tam." >/dev/null
    mv "$u/tam.traineddata" "$P/$f.traineddata"; rm -rf "$u"
  done
fi
meta() {  # file version [config-text]
  local f=$1 dir; dir=$(mktemp -d "$P/meta.XXXX")
  printf '%s' "$2" > "$dir/tam.version"
  if [[ -n ${3:-} ]]; then printf '%b' "$3" > "$dir/tam.config"; combine_tessdata -o "$f" "$dir/tam.version" "$dir/tam.config" >/dev/null
  else combine_tessdata -o "$f" "$dir/tam.version" >/dev/null; fi
}
meta "$P/best.traineddata" "5.5.0:tam:tamil-tess-trainer-3.1.0:best:ft$D:$NET192" \
  '# Turn off adaption, since it introduces high CPU overhead and a small error rate increase.\ntessedit_tess_adaption_mode\t0x00\n'
meta "$P/std.traineddata"  "5.5.0:tam:tamil-tess-trainer-3.1.0:best2int$D" 'tessedit_ocr_engine_mode\t1\n'
meta "$P/fast.traineddata" "5.5.0:tam:tamil-tess-trainer-3.1.0:fast:ft$D:$NET128"
cp "$P/best.traineddata" "$DIST/tam_best_v3.1.traineddata"
cp "$P/std.traineddata"  "$DIST/tam_v3.1.traineddata"
cp "$P/fast.traineddata" "$DIST/tam_fast_v3.1.traineddata"
rm -rf "$P"
( cd "$DIST" && sha256sum tam_best_v3.1.traineddata tam_v3.1.traineddata tam_fast_v3.1.traineddata > SHA256SUMS && cat SHA256SUMS )
for f in tam_best_v3.1 tam_v3.1 tam_fast_v3.1; do
  echo "== $f.traineddata $(stat -c %s "$DIST/$f.traineddata") bytes"
  combine_tessdata -d "$DIST/$f.traineddata" 2>&1 | grep -v '^$' | sed 's/^/   /'
  combine_tessdata -l "$DIST/$f.traineddata" 2>&1 | grep '^LSTM:' | sed 's/^/   /'
done
