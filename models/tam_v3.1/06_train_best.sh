#!/usr/bin/env bash
# Step 6 - Fine-tune the BEST model (float, Lfx192, same network as tessdata_best tam / tam_v3)
# from tam_v3 onto the clean v3.1 character set.
#
#   bash 06_train_best.sh WORK ITERATIONS
# WORK must contain: release/tam_v3.traineddata, starter/tam/tam.traineddata, lines/train/list.txt
# Writes WORK/lists/{train,dev}.txt (shuffled, seed 31; 600 held-out dev lines used only to pick
# the checkpoint), WORK/ckpt/best/*, WORK/ckpt/best/selected.checkpoint
set -euo pipefail
WORK=$(cd "$1" && pwd); ITER=${2:-12000}
mkdir -p "$WORK/lists" "$WORK/ckpt/best" "$WORK/v3lstm"
if [[ ! -s $WORK/lists/train.txt ]]; then
  python3 -I - "$WORK/lines/train/list.txt" "$WORK/lists" <<'EOF'
import random, sys
files = [l.strip() for l in open(sys.argv[1]) if l.strip()]
random.Random(31).shuffle(files)
open(sys.argv[2] + "/dev.txt", "w").write("\n".join(files[:600]) + "\n")
open(sys.argv[2] + "/train.txt", "w").write("\n".join(files[600:]) + "\n")
print(f"train {len(files) - 600}, dev 600")
EOF
fi
combine_tessdata -e "$WORK/release/tam_v3.traineddata" "$WORK/v3lstm/tam.lstm" >/dev/null
echo "TRAIN BEST START $(date -u +%FT%TZ) iterations=$ITER"
lstmtraining \
  --continue_from "$WORK/v3lstm/tam.lstm" --old_traineddata "$WORK/release/tam_v3.traineddata" \
  --traineddata "$WORK/starter/tam/tam.traineddata" \
  --model_output "$WORK/ckpt/best/tam" \
  --train_listfile "$WORK/lists/train.txt" --eval_listfile "$WORK/lists/dev.txt" \
  --learning_rate 0.0001 --reset_learning_rate \
  --max_iterations "$ITER" --target_error_rate 0.01 --max_image_MB 2000 --debug_interval -1 \
  > "$WORK/ckpt/best/train.log" 2>&1
echo "TRAIN BEST END $(date -u +%FT%TZ)"
bash "$(dirname "$0")/select_checkpoint.sh" "$WORK/ckpt/best" "$WORK/starter/tam/tam.traineddata" "$WORK/lists/dev.txt"
