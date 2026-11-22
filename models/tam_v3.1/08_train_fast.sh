#!/usr/bin/env bash
# Step 8 - Train the FAST model: same network as tessdata_fast tam
#   [1,36,0,1Ct3,3,16Mp3,3Lfys48Lfx96Lrx96Lfx128O1c1]
# Layers 0-5 (convolution, Lfys48, Lfx96, Lrx96) come from the chosen v3.1 BEST model
# (BEST_LSTM, a float runtime .lstm); its Lfx192 layer is replaced by a new Lfx128 layer and a
# new output layer (--append_index 5), trained at the default rate 0.001 (all layers learn).
#
#   bash 08_train_fast.sh WORK ITERATIONS BEST_LSTM TRAIN_LIST DEV_LIST
set -euo pipefail
WORK=$(cd "$1" && pwd); ITER=$2; BEST=$3; TRAIN=$4; DEV=$5
mkdir -p "$WORK/ckpt/fast"
echo "TRAIN FAST START $(date -u +%FT%TZ) iterations=$ITER base=$BEST lines=$(wc -l < "$TRAIN")"
lstmtraining \
  --continue_from "$BEST" --traineddata "$WORK/starter/tam/tam.traineddata" \
  --append_index 5 --net_spec '[Lfx128 O1c1]' --learning_rate 0.001 \
  --model_output "$WORK/ckpt/fast/tam" --train_listfile "$TRAIN" --eval_listfile "$DEV" \
  --max_iterations "$ITER" --target_error_rate 0.01 --max_image_MB 2000 --debug_interval -1 \
  > "$WORK/ckpt/fast/train.log" 2>&1
echo "TRAIN FAST END $(date -u +%FT%TZ)"
grep -m1 'Built network' "$WORK/ckpt/fast/train.log"
bash "$(dirname "$0")/select_checkpoint.sh" "$WORK/ckpt/fast" "$WORK/starter/tam/tam.traineddata" "$DEV"
