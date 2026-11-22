# tam v3.1 — reproducible training and benchmarking

Fine-tunes `tam_v3` (tamil-tess-trainer v3.0.0) into three Tesseract models, one per upstream repo.
Results: `RESULTS.md`. Licensing: `LICENSING.md`. Error analyses: `analysis/`.

| Release file | Repo | Network | Precision |
|---|---|---|---|
| `tam_best_v3.1.traineddata` | tessdata_best | `[1,36,0,1Ct3,3,16Mp3,3Lfys48Lfx96Lrx96Lfx192O1c1]` | float |
| `tam_v3.1.traineddata` | tessdata | same as best | integer (best converted) |
| `tam_fast_v3.1.traineddata` | tessdata_fast | `[1,36,0,1Ct3,3,16Mp3,3Lfys48Lfx96Lrx96Lfx128O1c1]` | integer |

All three carry the cleaned word dictionary (`lstm-word-dawg`), the number patterns, and the punctuation patterns
with straight single-quote patterns added (`16_quote_patterns.py`).

## Requirements
Tesseract 5.5 with training tools (`lstmtraining`, `lstmeval`, `combine_tessdata`, `combine_lang_model`,
`dawg2wordlist`), Python 3 with PyGObject (Pango, PangoCairo), pycairo, Pillow, NumPy; `fc-query`; GNU `time`.
Fonts listed in `fonts.tsv`. CPU only (developed on a 4-core i3-9100). Each training round needs ~1.5 GB of
`.lstmf` files.

## Inputs (pinned)
- Release `v3.0.0` of newsbaba24x7/tamil-tess-trainer (checked against its `SHA256SUMS`): `tam_v3.traineddata`,
  `tam_v3-training-text.txt.gz`, `tam_v3-real-lines.jsonl.gz` (line boxes and proofread text of tam_v3's real lines).
- tam_v3's own real scans, re-cut with `14_fetch_real_lines.py` (as `tools/crop_lines.py`): the **dev** split
  (2,854 lines, 164 archive.org pages) for model choice, **16,012 training lines** (814 archive.org pages, listed in
  `real_scan/train_pages_round4.tsv`) for training, and the **test** split (3,968 lines, 197 Wikimedia pages) for
  the final score only. No image from any other source.
- Fonts in `fonts.tsv`; `/usr/share/dict/american-english` (SCOWL); `english_terms.txt`.

## Steps (released models)
```bash
W=work; L=$W/release/tam_v3-real-lines.jsonl.gz
bash 00_inventory.sh $W      # downloads the pinned v3.0.0 release and the three upstream tam files, checks, unpacks
for k in word punc number; do dawg2wordlist $W/unpack/v3_best/tam.lstm-unicharset $W/unpack/v3_best/tam.lstm-$k-dawg $W/lists/$k.raw; done
python3 -I 01_clean_charset.py --unicharset $W/unpack/v3_best/tam.lstm-unicharset --words $W/lists/word.raw \
   --puncs $W/lists/punc.raw --numbers $W/lists/number.raw --text $W/release/tam_v3-training-text.txt.gz --out $W/clean
python3 -I 02_make_corpus.py --natural $W/clean/natural.txt --words $W/clean/words.txt --terms english_terms.txt \
   --english /usr/share/dict/american-english --train 24000 --out $W/corpus             # eval.tsv = synthetic test
python3 03_render_lines.py --corpus $W/corpus/eval.tsv --fonts fonts.tsv --role eval --out $W/lines/eval
bash 05_build_starter.sh $W/clean $W/starter

# Synthetic half of the training mix (round 3 corpus, rendered in chunks)
python3 -I 02_make_corpus.py --natural $W/clean/natural.txt --words $W/clean/words.txt --terms english_terms.txt \
   --english /usr/share/dict/american-english --train 24000 --train-seed 33 --book-punct \
   --share natural=.55,numerals=.04,punct=.12,mixed=.15,english=.05,edge=.09 --fixed-eval $W/corpus/eval.tsv --out r3/corpus
split -l 3000 -d r3/corpus/train.tsv r3/part_
for c in r3/part_*; do python3 03_render_lines.py --corpus $c --fonts fonts.tsv --role train --out r3/lines --seed 9${c##*_}; \
   bash 04_make_lstmf.sh r3/lines; rm -f r3/lines/tr*.png r3/lines/tr*.box; done

# Real lines (downloads; archive.org 1 s apart, Wikimedia 15 s apart)
python3 -I 14_fetch_real_lines.py $L --split dev   --out real_dev
python3 -I 14_fetch_real_lines.py $L --split train --pages real_scan/train_pages_round4.tsv --out real_train
python3 -I 14_fetch_real_lines.py $L --split test  --out real_test

# Round 4 -> BEST: 16,012 real + 16,012 synthetic lines, 20,000 iterations, checkpoint chosen on real dev
bash 15_train_round4.sh r4 real_train/lines real_dev/lines r3/lines $W/starter/tam/tam.traineddata $W/release/tam_v3.traineddata 20000
#   blend with tam_v3 (remapped to the v3.1 character set, A.lstm; see 'v3map' below): 0.5 x tam_v3 + 0.5 x round 4
lstmtraining --continue_from r4/v3lstm/tam.lstm --old_traineddata $W/release/tam_v3.traineddata \
   --traineddata $W/starter/tam/tam.traineddata --model_output v3map --train_listfile one_line.txt \
   --max_iterations 1 --learning_rate 1e-9 --reset_learning_rate
lstmtraining --stop_training --continue_from v3map_checkpoint --traineddata $W/starter/tam/tam.traineddata --model_output v3map.traineddata
lstmtraining --stop_training --continue_from r4/ckpt/selected.checkpoint --traineddata $W/starter/tam/tam.traineddata --model_output r4.traineddata
combine_tessdata -e v3map.traineddata A.lstm; combine_tessdata -e r4.traineddata B4.lstm
python3 -I interpolate_lstm.py A.lstm B4.lstm 0.5 best_r4.lstm

# FAST: best_r4's layers 0-5 frozen (--append_index 5) + new Lfx128 and output, same mix, 36,000 iterations ...
bash 08_train_fast.sh fast4 36000 best_r4.lstm r4/mix.txt real_dev/lines/list.txt
#   ... then 4,000 more at learning rate 1e-4 (fast5; real dev CER/WER 1.16/7.24 -> 1.06/6.39)
lstmtraining --continue_from fast4/ckpt/fast/tam_checkpoint --traineddata $W/starter/tam/tam.traineddata \
   --model_output fast5/tam --train_listfile r4/mix.txt --learning_rate 0.0001 --reset_learning_rate --max_iterations 40000

# Package with the word dictionary and single-quote punctuation patterns (same weights, new dictionaries)
python3 -I 16_quote_patterns.py $W/clean/puncs.txt $W/clean/puncs_quotes.txt          # 308 -> 404 patterns
PUNCS=$W/clean/puncs_quotes.txt bash 05_build_starter.sh $W/clean $W/starter_q
bash 09_package.sh $W/starter_q/tam/tam.traineddata best_r4.lstm fast5/tam_checkpoint dist

# Evaluate (tam_v3's protocol for line images is --psm 13). Accuracy runs preload a no-op feenableexcept so a
# Tesseract < 5.5.4 SIGFPE (tesseract#4627) cannot abort a batch; outputs are otherwise byte-identical.
gcc -shared -fPIC -O2 -o no_fpe_trap.so analysis/tesseract_sigfpe_repro/no_fpe_trap.c
python3 -I 12_prepare_real_eval.py $L real_test/lines test; python3 -I 12_prepare_real_eval.py $L real_dev/lines dev
export LD_PRELOAD=$PWD/no_fpe_trap.so
python3 -I 10_evaluate.py --lines real_test/lines --corpus real_test/lines/real.tsv --psm 13 --out results/real_test_psm13 --model NAME=DIR ...
python3 -I 10_evaluate.py --lines real_dev/lines --corpus real_dev/lines/real.tsv --psm 13 --speed-lines 3 --out results/real_dev_psm13 --model NAME=DIR ...
python3 -I 10_evaluate.py --lines $W/lines/eval --corpus $W/corpus/eval.tsv --psm 7 --out results/synthetic --model NAME=DIR ...
unset LD_PRELOAD
python3 -I bootstrap_ci.py results/real_test_psm13/v3_best.jsonl results/real_test_psm13/v31_best.jsonl --metric wer
python3 -I 13_error_analysis.py results/real_test_psm13 $L v31_best v3_best > analysis/report.md
# Crash scan with the stock CLI: all 8,211 real test + real dev + synthetic lines
python3 -I 17_crash_scan.py DIR 7 all_lines.txt results/crash_NAME_psm7.txt
```
(`03_render_lines.py` runs without `-I` because PyGObject is a system package.)

## Design decisions and findings
- **Character set** (`charset.py`; `charset_report.md`): 36 entries removed (C1 controls U+0093/U+0094, Cyrillic
  look-alikes А/Ѕ, Cherokee, CJK, Hangul, Malayalam, decorative symbols, and the pulli+U+200C unichar that makes
  upstream `tam` emit invisible U+200C); 8 added (`^`, `` ` ``, `×`, ௐ, ௶, ௷, ௹, ௺).
- **Recoder**: tam_v3 and upstream `tam` use an identity code table (blank = code 2). Tesseract 5.5's
  `combine_lang_model` builds another layout; remapping onto it put the never-trained "Joined" output into the blank
  (CER 3.1% → 14.4%). `05_build_starter.sh` writes the identity table.
- **Word dictionary + single-quote patterns**: with U+200C removed, the dictionary actually matches real words. Neither
  tam_v3's nor Tesseract's Tamil punctuation patterns contain a straight single quote (`'`), which Tamil books use a
  lot, so the decoder dropped quotes (and split words) to reach dictionary words: round 4 with the dictionary kept
  42.8% of the quotes on real dev lines. `16_quote_patterns.py` adds 96 `'` patterns (every double-quote pattern in
  single-quote form, plus word-boundary forms): 93.4% kept, real dev WER 6.98% → 5.55% (tam_v3: 84.7%, 6.26%).
  A no-dictionary variant was also built (`DROP_WORD_DAWG=1`); the dictionary is kept for the release.
- **Real lines in training**: synthetic-only rounds 1–3 never beat tam_v3 on real scans; round 4 mixes tam_v3's own
  real training lines (re-cut, 50%) with synthetic lines (50%) for numerals, English and the clean character set.
- **Weight-space interpolation** (WiSE-FT; `interpolate_lstm.py`, byte-exact at both ends) of tam_v3 and the
  fine-tuned model keeps tam_v3's robustness; α = 0.5 for round 4.
- **Selection** on tam_v3's real dev split (rule in `select_dev.py`, fixed before round-4 results): real dev CER and
  WER no worse than tam_v3, synthetic categories A–D no worse; then lowest real-dev WER. The real **test** split is
  used only for the final report.
- **Measurement**: with `--psm 7`, 140 of the 3,968 test line images (and 148 dev lines) come back empty for every
  model, which added ~3.8 CER points to every model in earlier reports. `--psm 13` (tam_v3's protocol) reads them.
- **Fast model**: `--append_index 5` keeps the copied layers frozen (verified to 2·10⁻⁷). The 36,000-iteration run
  finished, then lstmtraining crashed in its final evaluation; its final checkpoint was continued for 4,000
  iterations at learning rate 1e-4 (fast5), whose final checkpoint is released.
- **Tesseract SIGFPE (not a model defect)**: the stock Tesseract 5.5.0–5.5.3 CLI can die with SIGFPE in single-row
  modes (`--psm 7/8/9/10/13`) when a line yields two empty words: their certainties (−FLT_MAX each) overflow in
  `Textord::CleanupSingleRowResult`, and the CLI traps overflow. Reported upstream as tesseract-ocr/tesseract#4627
  (with `tessdata_fast` `fas`) and fixed by #4630 in **Tesseract 5.5.4**; library/API users are not affected. Which
  lines trigger it depends on image and model. Every file is scanned with the stock 5.5.0 CLI on all 8,211 test lines
  (`17_crash_scan.py`, `results/crash_*.txt`); gdb evidence and a test shim are in `analysis/tesseract_sigfpe_repro/`.
- **Tesseract quirk**: line-normalisation noise is seeded from the model's iteration counters, so files with
  identical weights but different counters can differ on a few characters.

## Earlier rounds (tried, not released)
Round 1 (synthetic, digits/punctuation in Tamil fonts), round 2 (+ Noto digits/punctuation, stretch, stroke weight),
round 3 (book-style punctuation, 4% numerals) and their interpolations; a linear-probe output layer; a fast model on
round-3 data (crashed Tesseract with SIGFPE on one line). All scored worse than tam_v3 on real scans with the word
dictionary in place. Commands for them are in the history of this file.
