#!/usr/bin/env bash
# Pick the checkpoint with the lowest character error on the held-out dev lines (lstmeval),
# among the final checkpoint and the three best-on-training checkpoints. Copies it to
# CKPT_DIR/selected.checkpoint and records the scores in CKPT_DIR/selection.tsv.
# Usage: bash select_checkpoint.sh CKPT_DIR STARTER_TRAINEDDATA DEV_LIST
set -euo pipefail
D=$1; T=$2; DEV=$3
mapfile -t C < <( { ls "$D"/tam_checkpoint; for f in "$D"/tam_[0-9]*.checkpoint; do [[ -e $f ]] && basename "$f"; done \
                    | awk -F_ '{print $2"\t"$0}' | sort -g | head -3 | cut -f2 | sed "s#^#$D/#"; } )
: > "$D/selection.tsv"
for c in "${C[@]}"; do
  r=$(lstmeval --model "$c" --traineddata "$T" --eval_listfile "$DEV" 2>&1 | grep -oE 'BCER eval=[0-9.]+, BWER eval=[0-9.]+' | tail -1)
  printf '%s\t%s\n' "$(basename "$c")" "$r" | tee -a "$D/selection.tsv"
done
best=$(awk -F'\t' '{split($2, a, /[=,]/); print a[2] "\t" $1}' "$D/selection.tsv" | sort -g | head -1 | cut -f2)
cp "$D/$best" "$D/selected.checkpoint"
echo "selected: $best"
