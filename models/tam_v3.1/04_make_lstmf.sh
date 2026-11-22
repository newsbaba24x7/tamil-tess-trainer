#!/usr/bin/env bash
# Step 4.2 - Turn line images + .gt.txt into Tesseract .lstmf training files.
# For each <id>.png: write a WordStr box file covering the whole line (same as tesstrain's
# generate_line_box.py), then `tesseract <id>.png <id> --psm 13 lstm.train`.
# Usage: bash 04_make_lstmf.sh LINES_DIR [JOBS]   -> LINES_DIR/list.txt (one .lstmf per line)
set -euo pipefail
DIR=$(cd "$1" && pwd); JOBS=${2:-$(nproc)}
export OMP_THREAD_LIMIT=1
one() {
  png=$1; base=${png%.png}
  [[ -s $base.lstmf ]] && return 0
  python3 -I - "$png" "$base.gt.txt" "$base.box" <<'EOF'
import sys, unicodedata, PIL.Image
png, gt, box = sys.argv[1:]
w, h = PIL.Image.open(png).size
text = unicodedata.normalize("NFC", open(gt, encoding="utf-8").read().strip())
open(box, "w", encoding="utf-8").write(f"WordStr 0 0 {w} {h} 0 #{text}\n\t {w} {h} {w+1} {h+1} 0\n")
EOF
  tesseract "$png" "$base" --psm 13 lstm.train >/dev/null 2>&1 || echo "FAILED $png" >&2
}
export -f one
find "$DIR" -maxdepth 1 -name '*.png' ! -name '_*' | sort | xargs -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
find "$DIR" -maxdepth 1 -name '*.lstmf' -size +0 | sort > "$DIR/list.txt"
echo "lstmf files: $(wc -l < "$DIR/list.txt") of $(find "$DIR" -maxdepth 1 -name '*.png' ! -name '_*' | wc -l) images"
