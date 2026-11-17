The 2,051 held-out lines tam_v2 was scored on (`tamtrain evaluate --work work-v2 --eval-lines 2000`),
kept as a fixed line set after the training images were deleted: 2,044 rendered lines with text never
used in training (63 of them in the three held-out font families) and 7 real check lines.
Score with: python3 -m tamtrain lines benchmarks/rendered-heldout-v2 --name rendered-heldout --psm 7
lines.json says which font, size and degradations each line was drawn with.
