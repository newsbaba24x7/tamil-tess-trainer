# tam v3.1 — results and engineering report

Status: published as release v3.1.0 (2026-11-22 13:06 UTC); pull requests to tessdata_best (#89), tessdata (#209)
and tessdata_fast (#41) are open. Process: 2026-11-21 22:16 UTC → 2026-11-22 12:51 UTC (final benchmark
12:13–12:51 UTC).
Machine: Intel i3-9100 (4 cores, AVX2), 18 GB RAM, Tesseract 5.5.0 (Debian `5.5.0-1build1`), no GPU.
All numbers were measured on this machine on the exact release files. The tables are generated from
`results/*/summary.json` by `18_report_tables.py` (full set: `results/tables.md`).

## Correction to earlier figures

Earlier drafts reported real-scan CER/WER of about 4.9 / 11.9 for v3.1 best. Those runs used `--psm 7`, which returns
**empty text for 140 of the 3,968 test lines** (148 of the dev lines) for every model, adding about 3.8 CER points to
all of them. tam_v3's published protocol for line images is `--psm 13`; with it tam_v3 reproduces its published
1.13% / 7.94% exactly. All real-scan figures below use `--psm 13`. The earlier draft release notes were withdrawn.

## Release files

| File | Target repo | Bytes | SHA-256 |
|---|---|---:|---|
| `tam_best_v3.1.traineddata` | tessdata_best | 7,340,283 | `c86d470778d2e5860714a3717aa8a56af1a692c0499765fe3477659c134f703b` |
| `tam_v3.1.traineddata` | tessdata | 4,553,596 | `d03a2f086f94469dc40b4f60568e631e4afde86721db962bf9e20ba9af7076be` |
| `tam_fast_v3.1.traineddata` | tessdata_fast | 4,432,897 | `7ddd23a875cb2945ec3a147f33c5c55318d38521f94f96ca9f25756bc3b39fa4` |

Checks on each file: `sha256sum -c SHA256SUMS`; `combine_tessdata -d / -l / -u`; `tesseract --list-langs` lists `tam`;
all 8,211 test lines recognised; no output character outside the v3.1 character set; a crash scan with the stock CLI
(see "Tesseract crash in single-line modes").

## Target: real scans at most 2% CER and 8% WER

| tam_v3 real test split, 3,968 lines, `--psm 13` | CER % | WER % | Target |
|---|---:|---:|---|
| upstream `tam` best | 9.38 | 61.95 | — |
| tam_v3 best | 1.13 | 7.94 | — |
| **v3.1 best** (tessdata_best) | **0.98** | **6.90** | met |
| **v3.1 std** (tessdata) | **1.05** | **7.04** | met |
| **v3.1 fast** (tessdata_fast) | **1.34** | **8.36** | CER met; WER 0.36 points over |

WER is still above 5% for every model. Most remaining word errors are punctuation and spacing: with all punctuation
ignored, v3.1 best scores 0.68% / 4.75% (tam_v3: 0.83% / 5.69%); on Tamil letters only, 0.63% / 4.51%
(`analysis/real_test_error_analysis_v3.1.md`).

## Test sets

| | Real test | Real dev | Synthetic |
|---|---|---|---|
| Lines | 3,968 from 197 pages | 2,854 from 164 pages | 1,389 |
| Source | tam_v3's test split: Wikimedia Commons scans of Tamil Wikisource books, cut with tam_v3's line boxes | tam_v3's dev split: archive.org scans, same cutting | text never trained on, rendered in 6 fonts never used to train v3.1 |
| Use | **final report only** | choosing checkpoints and candidates (so not an unbiased score for v3.1) | categories A–G of the request, plus punctuation |
| Mode | `--psm 13` | `--psm 13` | `--psm 7` |
| Confidence intervals | paired bootstrap resampling **pages** | same | paired bootstrap resampling lines |

Text is compared strictly, after NFC normalisation and space collapsing, without folding quote or dash variants.
Accuracy runs preload a no-op `feenableexcept` (`analysis/tesseract_sigfpe_repro/`) so that the Tesseract < 5.5.4
SIGFPE cannot abort a batch. Outputs are byte-identical to the stock CLI on every line that does not crash.

## E. Accuracy

### Headline: CER % / WER %

| model | real test | real test, invisible chars removed | real dev | synthetic |
|---|---:|---:|---:|---:|
| upstream best | 9.38 / 61.95 | 3.71 / 22.15 | 8.89 / 61.39 | 19.43 / 68.59 |
| upstream std | 9.38 / 62.00 | 3.71 / 22.18 | 8.96 / 61.33 | 19.34 / 68.38 |
| upstream fast | 10.04 / 63.53 | 4.35 / 23.73 | 9.29 / 62.48 | 20.75 / 69.20 |
| tam_v3 best | 1.13 / 7.94 | 1.13 / 7.94 | 0.90 / 6.26 | 6.59 / 27.95 |
| tam_v3 int | 1.21 / 8.01 | 1.21 / 8.01 | 1.09 / 6.40 | 6.60 / 28.04 |
| **v3.1 best** | **0.98 / 6.90** | 0.98 / 6.90 | **0.78 / 5.55** | **5.54 / 24.84** |
| **v3.1 std** | **1.05 / 7.04** | 1.05 / 7.04 | **0.94 / 5.66** | **5.55 / 24.96** |
| **v3.1 fast** | **1.34 / 8.36** | 1.34 / 8.36 | **1.06 / 6.39** | **4.69 / 22.68** |

Upstream `tam` emits an invisible U+200C after many pulli signs (3,697 of the 3,968 real test lines), so its strict
scores are much worse than what a reader sees. The "invisible chars removed" column shows its scores with that character
removed. Scored as tam_v3's own benchmark does (zero-width characters dropped, quote and dash variants folded), the real
test gives: upstream best / std / fast 3.56 / 21.16 · 3.56 / 21.24 · 4.18 / 22.77; tam_v3 best / int 1.13 / 7.92 ·
1.21 / 7.98; **v3.1 best / std / fast 0.97 / 6.88 · 1.04 / 7.02 · 1.33 / 8.32**. This is the like-for-like comparison
with the figures on the repository's front page (stock 3.56% / 21.2%, tam_v3 1.13% / 7.9%).

### Significance (difference in points, 95% CI; negative = v3.1 better)

| Comparison | Real test CER | Real test WER | Real dev CER / WER | Synthetic CER |
|---|---|---|---|---|
| v3.1 best − tam_v3 best | **−0.16** (−0.21…−0.11) | **−1.04** (−1.38…−0.71) | −0.12 / −0.71 | **−1.06** (−1.19…−0.92); better in A–G, punctuation n.s. |
| v3.1 std − tam_v3 int | **−0.17** (−0.22…−0.11) | **−0.97** (−1.33…−0.61) | −0.15 / −0.74 | **−1.05** (−1.18…−0.91); better in A–G, punctuation n.s. |
| v3.1 best − upstream best | **−8.40** (−8.70…−8.12) | **−55.04** (−56.23…−53.85) | −8.11 / −55.84 | **−13.89** (−14.51…−13.27) |
| v3.1 std − upstream std | **−8.33** (−8.63…−8.06) | **−54.96** (−56.14…−53.76) | −8.02 / −55.67 | **−13.79** (−14.41…−13.17) |
| v3.1 fast − upstream fast | **−8.71** (−9.04…−8.39) | **−55.17** (−56.44…−53.89) | −8.23 / −56.08 | **−16.06** (−16.80…−15.33) |

Every interval excludes zero (`results/confidence_intervals.md`; 10,000 resamples; real sets resampled by page). By
content against tam_v3, Tamil-only real lines are significantly better in CER and WER; lines with numbers are better in
CER (−0.45) with WER not significant; the 17 Latin lines show no significant difference. Real dev was used to choose
the release, so its differences are optimistic; the real test split was not.

### Synthetic categories (request item 16): CER % / WER %

| Category | upstream best | upstream fast | tam_v3 best | **v3.1 best** | **v3.1 std** | **v3.1 fast** |
|---|---:|---:|---:|---:|---:|---:|
| A Tamil text | 12.78 / 63.8 | 13.69 / 64.2 | 2.39 / 11.6 | **1.97 / 9.8** | **1.91 / 9.5** | 2.38 / 11.5 |
| B vowel signs & consonant combinations | 12.27 / 64.5 | 13.57 / 66.1 | 1.60 / 10.6 | **1.32 / 9.5** | 1.40 / 10.0 | 1.92 / 12.4 |
| C grantha | 13.49 / 66.3 | 15.51 / 68.3 | 3.01 / 16.3 | **2.65 / 13.6** | **2.65 / 13.3** | 3.33 / 16.6 |
| D pulli & diacritics | 12.30 / 63.5 | 13.82 / 64.8 | 1.79 / 11.8 | **1.32 / 8.7** | 1.36 / 9.3 | 2.03 / 12.4 |
| E Tamil numerals | 16.36 / 65.0 | 16.83 / 64.4 | 14.93 / 53.8 | 12.70 / 47.5 | 12.52 / 47.4 | **8.15 / 31.4** |
| F mixed Tamil-English | 29.14 / 76.2 | 30.47 / 75.3 | 10.16 / 35.4 | 8.41 / 32.6 | 8.38 / 32.6 | **6.14 / 28.0** |
| G English technical terms in Tamil | 40.18 / 78.8 | 42.80 / 80.5 | 13.56 / 45.0 | 10.77 / 40.2 | 10.88 / 40.1 | **7.32 / 32.1** |
| Punctuation | 15.47 / 68.6 | 15.67 / 68.5 | 6.73 / 36.1 | **6.51 / 33.9** | 6.63 / 34.7 | 7.12 / 36.6 |

### Real test lines by content: CER % / WER %

| Lines | upstream best | tam_v3 best | **v3.1 best** | **v3.1 std** | **v3.1 fast** |
|---|---:|---:|---:|---:|---:|
| Tamil only (3,715) | 9.14 / 61.8 | 1.00 / 7.4 | **0.86 / 6.4** | 0.93 / 6.5 | 1.20 / 7.7 |
| with numbers (236) | 12.30 / 62.9 | 2.95 / 14.1 | **2.50 / 12.7** | 2.75 / 13.1 | 3.41 / 15.6 |
| with Latin (17) | 25.40 / 72.2 | 7.75 / 33.3 | 7.49 / 35.6 | 7.09 / 35.6 | 6.28 / 36.7 |

### Characters: share of reference occurrences recovered (real test / synthetic)

| Pattern (real n / synthetic n) | upstream best | tam_v3 best | **v3.1 best** | **v3.1 std** | **v3.1 fast** |
|---|---:|---:|---:|---:|---:|
| ஸ்ரீ (6 / 14) | 83.3% / 64.3% | 83.3% / 85.7% | 100% / 100% | 100% / 100% | 50.0% / 78.6% |
| grantha ஜ ஷ ஸ ஹ ஶ (295 / 579) | 94.6% / 92.4% | 98.0% / 95.5% | 98.0% / 96.7% | 97.6% / 97.1% | 98.3% / 95.3% |
| ஔ / ௌ (11 / 8) | 0% / 0% | 81.8% / 75.0% | 63.6% / 87.5% | 63.6% / 87.5% | 45.5% / 62.5% |
| pulli ் (25,016 / 8,952) | 99.2% / 99.2% | 99.8% / 98.9% | 99.8% / 99.2% | 99.7% / 99.2% | 99.7% / 99.1% |
| Tamil numerals ௦–௲ (6 / 1,178) | 83.3% / 82.3% | 50.0% / 43.9% | 66.7% / 56.8% | 66.7% / 57.3% | 100% / 79.7% |
| Tamil symbols ௳–௺ ௐ (0 / 86) | – / 0% | – / 0% | – / 0% | – / 0% | – / 31.4% |
| ASCII digits (641 / 1,221) | 90.5% / 99.3% | 97.8% / 99.1% | 97.3% / 98.8% | 98.4% / 98.8% | 97.7% / 97.4% |
| quotes “ ” ‘ ’ " ' (616 / 444) | 71.6% / 79.7% | 88.5% / 78.2% | **93.0% / 88.3%** | **93.2% / 88.3%** | 88.1% / 84.2% |
| brackets (219 / 473) | 80.4% / 86.9% | 96.8% / 94.3% | 98.2% / 94.9% | 98.6% / 95.1% | 93.6% / 91.5% |
| dashes — – - (169 / 359) | 82.2% / 93.6% | 86.4% / 97.8% | 82.8% / 98.9% | 84.0% / 99.2% | 85.8% / 96.9% |
| Latin letters (117 / 5,004) | 0% / 0% | 80.3% / 86.0% | 82.1% / 91.9% | 86.3% / 91.8% | 91.5% / 97.5% |
| Latin word tokens (24 / 894) | 0% / 0% | 4.2% / 10.9% | 8.3% / 19.7% | 8.3% / 19.7% | 12.5% / 38.8% |
| lines with characters outside the v3.1 set | 3,697 / 1,299 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

### Where the remaining real-scan errors are (`analysis/real_test_error_analysis_v3.1.md`)

| CER points by class | tam_v3 best | **v3.1 best** | **v3.1 std** | **v3.1 fast** |
|---|---:|---:|---:|---:|
| consonants | 0.35 | **0.25** | 0.28 | 0.37 |
| period / comma (`,` read as `.` 69×) | 0.18 | 0.18 | 0.17 | 0.24 |
| vowel signs | 0.17 | 0.16 | 0.17 | 0.23 |
| spaces (inserted / dropped) | 0.11 | 0.13 | 0.15 | 0.13 |
| quotes | 0.08 | 0.06 | 0.06 | 0.09 |
| pulli | 0.06 | 0.04 | 0.06 | 0.08 |
| everything else | 0.18 | 0.16 | 0.16 | 0.20 |

### Known limitations
1. **WER above 5%** on real scans for every model (best 6.90%); mostly punctuation and spacing (see above).
2. **Fast** misses the 8% WER target on real scans (8.36%), though it is far better than upstream fast (63.53%) and
   the best of the three on numerals, mixed Tamil-English and English terms.
3. **Tamil numerals** in best/std: 57% of synthetic occurrences (tam_v3 44%, upstream 82%). Tamil digits look like
   letters (௧/க, ௨/உ, ௭/எ, ௮/அ); pushing harder made candidates read words as numbers on real pages.
4. **Tamil symbols** ௳–௺ ௐ: not read by best/std; fast reads 31%.
5. **ஔ / ௌ** on real scans: 7 of 11 (tam_v3 9 of 11). **Dashes** on real scans: 82.8% (tam_v3 86.4%).
6. The real test set has few lines with numbers (236) or Latin (17), so those rows have wide intervals.
7. Single-line modes on Tesseract 5.5.0–5.5.3 CLI: see the crash section (fixed in Tesseract 5.5.4).

## How the release was chosen

- **Rounds 1–3** (synthetic lines only, about 24,000 per round) improved the synthetic test but never beat tam_v3 on
  real scans, even after weight-space interpolation (WiSE-FT) with tam_v3.
- **Round 4** (released): 16,012 of tam_v3's own real training lines (re-cut from 814 archive.org pages) mixed 50/50
  with 16,012 synthetic lines, 20,000 iterations from tam_v3 (learning rate 1e-4), checkpoint chosen on real dev; then
  0.5 × tam_v3 + 0.5 × round 4 (WiSE-FT). The images are tam_v3's own training scans; no image from any other source.
- **Selection rule** (`select_dev.py`, fixed before the round-4 results): real dev CER and WER no worse than tam_v3,
  synthetic categories A–D no worse than tam_v3, then lowest real dev WER. Chosen: round 4, α = 0.5, with the word
  dictionary and the single-quote patterns (real dev 0.78 / 5.55 against tam_v3 0.90 / 6.26). The real **test** split
  was not used for any choice.
- **Dictionary**: with the cleaned character set the word dictionary became active and made the decoder drop straight
  quotes (no `'` punctuation pattern existed): round 4 kept 42.8% of quotes on dev lines. Adding 96 single-quote
  patterns (`16_quote_patterns.py`) raised this to 93.4% and lowered dev WER from 6.98% to 5.55%. The full dictionary
  is kept (owner's decision); a no-dictionary build was tested and not released.
- **Fast**: frozen lower layers of the released best network plus new Lfx128 and output layers, trained 36,000
  iterations on the round-4 mix, then 4,000 more at learning rate 1e-4: real dev 1.16 / 7.24 → 1.06 / 6.39. The earlier
  fast model built on round 2 (real dev 1.96 / 12.45) was rejected.

## A. Architecture

All models: input height 36; 3×3 convolution with 16 filters + tanh; 3×3 max-pool; LSTMs; CTC output.

| Layer (weights) | upstream best/std `tam` | tam_v3 | **v3.1 best / std** | upstream fast | **v3.1 fast** |
|---|---:|---:|---:|---:|---:|
| ConvNL | 160 | 160 | 160 | 160 | 160 |
| Lfys48 | 12,480 | 12,480 | 12,480 | 12,480 | 12,480 |
| Lfx96 | 55,680 | 55,680 | 55,680 | 55,680 | 55,680 |
| Lrx96 | 74,112 | 74,112 | 74,112 | 74,112 | 74,112 |
| top LSTM | Lfx192 221,952 | Lfx192 221,952 | **Lfx192 221,952** | Lfx128 115,200 | **Lfx128 115,200** |
| Output (characters × inputs) | 99 × 193 | 214 × 193 | **186 × 193** | 99 × 129 | **186 × 129** |
| **Total** | 383,491 | 405,686 | **400,282** | 270,403 | **281,626** |

- **Best**: 0.5 × tam_v3 + 0.5 × round-4 fine-tune, every layer (`interpolate_lstm.py`).
- **Std**: the best model converted to integers (`lstmtraining --stop_training --convert_to_int`).
- **Fast**: convolution, Lfys48, Lfx96 and Lrx96 copied from best and frozen (`--append_index 5`; released file differs
  from best in these layers by at most 2.4·10⁻⁷); new Lfx128 and output layers. Tesseract records its spec as `[…Lfx192O1c1][Lfx128 O1c1]` (the base spec plus
  the appended part); the layers actually present are those above (`interpolate_lstm.py --dump`).

## B. Numerical precision

| | best | std (tessdata) | fast |
|---|---|---|---|
| Weights | float (stored as doubles) | 8-bit integers + one float scale per row | 8-bit integers + scales |
| LSTM component | 3,203,299 B | 416,759 B (13% of float) | 296,038 B |
| Identical text to float best | — | 94.6% of real test lines, 73.3% of synthetic (tam_v3: 93.8% / 69.5%; upstream: 82.5% / 58.6%) | different network |
| Cost of integers (std − best) | — | real test CER +0.07, WER +0.14; real dev +0.16 / +0.11; synthetic +0.01 / +0.12 (tam_v3: +0.08 / +0.07; +0.19 / +0.14; +0.01 / +0.09) | — |

## C. Model size

| Bytes | upstream best | upstream std | upstream fast | tam_v3 best | tam_v3 int | **v3.1 best** | **v3.1 std** | **v3.1 fast** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LSTM network | 3,068,971 | 399,224 | 284,088 | 3,246,531 | 422,355 | 3,203,299 | 416,759 | 296,038 |
| word dictionary | 2,943,474 | 2,943,474 | 2,943,474 | 5,281,642 | 5,281,642 | 4,118,082 | 4,118,082 | 4,118,082 |
| punctuation + number patterns | 3,260 | 3,260 | 3,260 | 3,260 | 3,260 | 3,980 | 3,980 | 3,980 |
| unicharset + recoder | 6,865 | 6,865 | 6,865 | 16,828 | 16,828 | 14,501 | 14,501 | 14,501 |
| **Total file** | 6,023,201 | 3,353,079 | 3,237,963 | 8,548,462 | 5,724,286 | **7,340,283** | **4,553,596** | **4,432,897** |

Networks are within 4.4% of upstream (larger output layer: 186 characters against 99). The rest of the difference is
the dictionary: 366,671 words (tam_v3 had 433,566 entries, many duplicates differing only by an invisible U+200C).
v3.1 is 14% (best) and 20% (std) smaller than tam_v3.

## D. Inference speed

One thread (`OMP_THREAD_LIMIT=1`), 300 lines in one process, idle machine; load = median of 3 runs on one line.

| | upstream best | upstream std | upstream fast | tam_v3 best | tam_v3 int | **v3.1 best** | **v3.1 std** | **v3.1 fast** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ms per line, real (psm 13) | 46.0 | 30.2 | 29.2 | 45.7 | 30.4 | **46.4** | **30.8** | **29.7** |
| ms per line, synthetic (psm 7) | 45.3 | 30.7 | 29.6 | 46.2 | 31.8 | **46.7** | **31.1** | **30.1** |
| model load, s | 0.090 | 0.063 | 0.060 | 0.171 | 0.134 | **0.159** | **0.148** | **0.136** |
| peak memory, MB | 36.9 | 30.0 | 29.7 | 48.7 | 40.9 | **47.5** | **39.5** | **39.2** |

Per-line speed is within 3% of upstream for each network, which is the run-to-run noise here (tam_v3 best and upstream
best have the same network and differ by 2%). Loading takes 70–90 ms longer and uses about 10 MB more memory because of
the larger dictionary (memory is still below tam_v3). On this AVX2 CPU the fast network is only ~4% faster per line
than std.

## Tesseract crash in single-line modes (not a model defect; fixed in Tesseract 5.5.4)

Scan with the stock CLI (`17_crash_scan.py`) on all 8,211 lines (3,968 real test + 2,854 real dev + 1,389 synthetic):

| Crashes (SIGFPE) | `--psm 7` | `--psm 13` |
|---|---:|---:|
| v3.1 best | 0 | 0 |
| v3.1 std | 0 | 0 |
| v3.1 fast | **2** | 0 |
| upstream best / std / fast | 0 / 0 / 0 | not scanned |
| tam_v3 best / int | 0 / 0 | not scanned |

The two lines are `wb_05f33f0963_p0041_018` (real dev) and `ws_64a6fe7b87_p0072_004` (real test); both have speck noise
next to the text. The cause is in Tesseract, not in the model file: when a line yields two words that the recogniser
leaves empty, each gets the certainty −FLT_MAX; `Textord::CleanupSingleRowResult` adds them in a `float`, which
overflows, and the CLI traps overflow (`feenableexcept(FE_DIVBYZERO | FE_OVERFLOW | FE_INVALID)`). gdb on this machine
shows both operands of the faulting `addss` equal to −3.40282347e+38. This is tesseract-ocr/tesseract#4627 (reported with
`tessdata_fast` `fas`), fixed by #4630 in **Tesseract 5.5.4**. It can occur only in single-row modes
(`--psm 7/8/9/10/13`), only in the CLI (library/API users do not enable the trap), and which lines trigger it depends
on image and model. With the trap disabled, 5.5.0 reads both lines (the dev line as `சொன்னார்.` plus speck noise);
the accuracy figures above include them. Details: `analysis/tesseract_sigfpe_repro/README.md`.

## F. Optimisation techniques

Used (each verified): character-set cleanup (NFC, invisible-character and foreign-script removal); identity recoder
(remapping without losing the old output layer); `--reset_learning_rate` with rate 1e-4; real-line training mixed
50/50 with synthetic lines; weight-space interpolation (WiSE-FT) with tam_v3; frozen feature layers for the fast model
(`--append_index 5`) and a short low-rate continuation; dictionary deduplication; single-quote punctuation patterns;
font-locked rendering; candidate selection on a dev split with a rule fixed in advance; page-level bootstrap
confidence intervals; crash scan of every release file.

Recommended next:
1. **Punctuation and spacing on scans** (largest remaining error): more real lines with `,`/`.` and quotes; check
   whether `,` → `.` comes from small print or from the language model.
2. **Tamil numerals vs letters**: train numerals in real contexts (page numbers, dates, money) with look-alike words
   (உக, கஉ …) as hard negatives; validate on real pages with numerals.
3. **Fast model WER**: a longer continuation on more real lines.
4. **Tamil symbols in best/std**: a longer output-layer pass guarded by the real dev split.
5. **Mobile**: a smaller dictionary (see H).

## G. Reproducible scripts

`README.md` has the exact commands. Files: `00_inventory.sh`, `charset.py`, `01_clean_charset.py`, `02_make_corpus.py`,
`english_terms.txt`, `fonts.tsv`, `fonts_audit.py`, `03_render_lines.py`, `04_make_lstmf.sh`, `05_build_starter.sh`,
`06_train_best.sh`, `select_checkpoint.sh`, `interpolate_lstm.py`, `08_train_fast.sh`, `09_package.sh`,
`10_evaluate.py`, `11_fetch_real_test.py`, `12_prepare_real_eval.py`, `13_error_analysis.py`,
`14_fetch_real_lines.py`, `15_train_round4.sh`, `16_quote_patterns.py`, `17_crash_scan.py`, `18_report_tables.py`, `19_benchmark_page.py`,
`select_split.py`, `select_real.py`, `select_dev.py`, `bootstrap_ci.py`. Seeds fixed. Results: `results/`.

## H. Proposed deployment configurations

| Use | Model | Settings | Expect (this machine, real test) |
|---|---|---|---|
| Desktop/server, best accuracy, further fine-tuning | `tam_best_v3.1` | `--oem 1 --psm 3` (pages) or `6` (blocks), `--psm 13` for pre-cut lines; 300 DPI; batches: `OMP_THREAD_LIMIT=1`, one process per core | 46 ms/line/core, 48 MB, CER 0.98% / WER 6.90% |
| Desktop default (`tessdata`) | `tam_v3.1` | same | 31 ms/line/core, 40 MB, CER 1.05% / WER 7.04% |
| Mobile/embedded; numerals and English-heavy text | `tam_fast_v3.1` | `--oem 1`, one thread, ~300 DPI, binarised | 30 ms/line, 39 MB, CER 1.34% / WER 8.36% |
| Numeric fields | any | `-c tessedit_char_whitelist=0123456789.,/-` | avoids digit/letter confusions |
| Memory-constrained | `tam_fast_v3.1` + smaller dictionary | rebuild with the most frequent words via `combine_lang_model` (not done or measured here) | smaller file, faster load |

Use Tesseract 5.5.4 or later for single-line modes (`--psm 7/8/13`) with the CLI. Mixed Tamil-English documents:
`-l tam` alone (v3.1 reads Latin); `-l tam+eng` is not needed.

## I. Licensing and redistribution

See `LICENSING.md`. Model files are Apache-2.0, like `tam` and tam_v3. The dictionary contains words from CC BY-SA
4.0 Tamil Wikisource text (attributed). New synthetic training images used only fonts under OFL-1.1 and one under
GPL-3.0-or-later with the font exception, each confirmed from the font file or its Debian package. Real training
lines are tam_v3's own training scans; real test pages were used only for testing and deleted. tam_v3's inherited
font list has licence questions (Gopi fonts are not GPL; AkrutiTml2 was withdrawn), single-source, to be re-checked
before its NOTICE is corrected.
