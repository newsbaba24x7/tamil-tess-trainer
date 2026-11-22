#!/usr/bin/env bash
# Step 15 - Round 4: fine-tune the BEST model from tam_v3 on a 50/50 mix of tam_v3's own real
# training lines (re-cut from archive.org pages) and round-3 synthetic lines. Checkpoints are
# chosen on tam_v3's REAL dev split; the real test split is only used for the final report.
#
#   bash 15_train_round4.sh WORK REAL_TRAIN_LINES REAL_DEV_LINES SYNTH_LSTMF_DIR STARTER V3_TRAINEDDATA ITERATIONS
set -euo pipefail
WORK=$(mkdir -p "$1" && cd "$1" && pwd); RT=$2; RD=$3; SYN=$4; T=$5; V3=$6; ITER=${7:-20000}
HERE=$(cd "$(dirname "$0")" && pwd)
echo "LSTMF START $(date -u +%T)"
bash "$HERE/04_make_lstmf.sh" "$RT" 4 | tail -1
bash "$HERE/04_make_lstmf.sh" "$RD" 4 | tail -1
python3 -I - "$RT/list.txt" "$SYN" "$WORK" <<'EOF'
import random, sys, glob
real = [l.strip() for l in open(sys.argv[1]) if l.strip()]
syn = sorted(glob.glob(sys.argv[2] + "/*.lstmf"))
r = random.Random(44); r.shuffle(syn)
mix = real + syn[:len(real)]; r.shuffle(mix)
open(sys.argv[3] + "/mix.txt", "w").write("\n".join(mix) + "\n")
print(f"mix: {len(real)} real + {min(len(real), len(syn))} synthetic = {len(mix)} lines")
EOF
python3 -I -c "import random,sys; L=[l.strip() for l in open('$RD/list.txt') if l.strip()]; random.Random(45).shuffle(L); open('$WORK/dev_sample.txt','w').write('\n'.join(L[:800])+'\n')"
mkdir -p "$WORK/v3lstm" "$WORK/ckpt"; combine_tessdata -e "$V3" "$WORK/v3lstm/tam.lstm" >/dev/null
echo "TRAIN START $(date -u +%T) iterations=$ITER"
lstmtraining --continue_from "$WORK/v3lstm/tam.lstm" --old_traineddata "$V3" --traineddata "$T" \
  --model_output "$WORK/ckpt/tam" --train_listfile "$WORK/mix.txt" --eval_listfile "$WORK/dev_sample.txt" \
  --learning_rate 0.0001 --reset_learning_rate --max_iterations "$ITER" --target_error_rate 0.01 \
  --max_image_MB 2000 --debug_interval -1 > "$WORK/ckpt/train.log" 2>&1
echo "TRAIN END $(date -u +%T)"
bash "$HERE/select_checkpoint.sh" "$WORK/ckpt" "$T" "$RD/list.txt"
find "$WORK/ckpt" -maxdepth 1 -name 'tam_[0-9]*.checkpoint' -delete
