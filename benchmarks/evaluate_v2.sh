#!/bin/bash
# Evaluate V2 against stock tam, V1 and V2-research on every test set we have.
# Reports go to work-v2/report/. Run from the tamil-tess-trainer folder.
# V1 and V2-research are research models that are not released (see MODEL_CARD.md); drop
# their --compare entries to compare V2 with the stock model only.
set -e
cd "$(dirname "$0")/.."
CMP=(--compare "V1 (188 styles)=work-60/output/tessdata_best/tam_multifont.traineddata"
     --compare "V2-research=work-v2-research/output/tessdata_best/tam_v2_research.traineddata")
T="python3 -m tamtrain"
CMP+=(--no-installed)
$T lines benchmarks/rendered-heldout-v2 --work work-v2 --name rendered-heldout "${CMP[@]}"    # rendered held-out lines (fixed set)
$T lines books-lines/dev --work work-v2 --name real-dev-lines "${CMP[@]}"                   # real lines, check books
$T lines benchmarks/wikisource-test-lines --work work-v2 --name real-test-lines "${CMP[@]}" # real lines, test pages
$T scans scans/wikisource --work work-v2 --name scans "${CMP[@]}"                          # 197 real pages
$T lines benchmarks/ranlp2025/lines --work work-v2 --name ranlp2025 "${CMP[@]}"            # RANLP 2025
$T lines benchmarks/ranlp2025/lines --work work-v2 --name ranlp2025-raw-psm3 --raw --psm 3 "${CMP[@]}"
$T lines benchmarks/tamil-ocr-benchmark/lines --work work-v2 --name tamil-ocr-benchmark "${CMP[@]}"
[ -n "$SKIP_ICON" ] || for s in old-newspapers-200dpi old-books-72dpi contemporary-books-300dpi contemporary-lowres-96dpi; do
  [ -d benchmarks/icon-style/$s ] && $T scans benchmarks/icon-style/$s --work work-v2 --name icon-$s "${CMP[@]}"
done
echo "ALL EVALUATIONS DONE"
