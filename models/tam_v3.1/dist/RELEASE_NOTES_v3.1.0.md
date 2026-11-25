Three Tesseract 5 models for printed Tamil, one for each official model repository (tessdata_best, tessdata, tessdata_fast). They are fine-tuned from tam_v3 (v3.0.0) with a cleaned character set, 16,012 of tam_v3's own real scanned training lines, and 16,012 new synthetic lines covering Tamil numerals, English words and punctuation.

```bash
curl -LO https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v3.1.0/tam_v3.1.traineddata
tesseract page.png out -l tam_v3.1 --tessdata-dir .
```

| Test (never trained on) | Stock `tam` | tam_v3 | **v3.1** |
|---|---:|---:|---:|
| 3,968 real scanned lines (197 pages), best model: CER / WER | 9.38% / 61.95% | 1.13% / 7.94% | **0.98% / 6.90%** |
| the same, integer model (tessdata): CER / WER | 9.38% / 62.00% | 1.21% / 8.01% | **1.05% / 7.04%** |
| the same, fast model: CER / WER | 10.04% / 63.53% | – | **1.34% / 8.36%** |
| the same lines, best model, scored as in the v3.0 release (zero-width characters dropped, quote and dash variants folded): CER / WER | 3.56% / 21.16% | 1.13% / 7.92% | **0.97% / 6.88%** |
| 1,389 synthetic lines (text never trained on) in 6 fonts not used to train v3.1 itself; 4 of them were used to train tam_v2 and tam_v3. Best model: CER / WER | 19.43% / 68.59% | 6.59% / 27.95% | **5.54% / 24.84%** |
| the 463 of them in the 2 fonts never used to train tam_v2, tam_v3 or v3.1 (Uni Ila.Sundaram-20, Latha), best model: CER / WER | 20.75% / 70.96% | 8.51% / 35.86% | **7.24% / 31.20%** |

Real lines are tam_v3's test split, read one line image at a time with `--psm 13` on Tesseract 5.5.0. The first three rows are scored strictly (NFC; quote and dash variants not folded), which counts the invisible U+200C that stock `tam` outputs after many pulli signs (in 3,697 of the 3,968 lines). The fourth row is scored as in the v3.0 release and is the like-for-like comparison with the stock and tam_v3 figures published there. Against tam_v3 on the real lines, v3.1 best is better by 0.16 CER points (95% CI 0.11–0.21) and 1.04 WER points (0.71–1.38), resampling whole pages. Full report: [RESULTS.md](https://github.com/newsbaba24x7/tamil-tess-trainer/blob/main/models/tam_v3.1/RESULTS.md).

**Files**

| File | For | What it is |
|---|---|---|
| `tam_best_v3.1.traineddata` | tessdata_best | Float model (`Lfx192` top layer), 7.3 MB. Most accurate; can be fine-tuned further |
| `tam_v3.1.traineddata` | tessdata | The same network in integers, 4.6 MB. A third less time per line; within 0.07 CER / 0.14 WER points of best on real lines |
| `tam_fast_v3.1.traineddata` | tessdata_fast | A separate, smaller integer network (`Lfx128`), 4.4 MB. Best of the three on Tamil numerals, mixed Tamil-English text and English terms |
| `SHA256SUMS` | | Checksums of the three files |

Speed on one core of an Intel i3-9100: 46 / 31 / 30 ms per line (best / integer / fast), within 3% of the stock networks.

**What is new in 3.1**
- Character set cleaned: 36 entries removed (control characters, Cyrillic and Cherokee look-alikes, CJK, Hangul, Malayalam, and a pulli + invisible U+200C entry), 8 added (`^`, `` ` ``, `×`, ௐ, ௶, ௷, ௹, ௺). No output in the tests contains a character outside the set.
- Training covers all 36 Tamil numeral forms (௦ … ௫௲), Latin words in Noto Sans and Noto Serif, and book-style punctuation.
- Punctuation patterns now include straight single quotes, so the dictionary no longer makes the decoder drop them: 93.0% of quotes recovered on real lines (tam_v3 88.5%).
- Word dictionary deduplicated (366,671 words): the files are 14% (best) and 20% (integer) smaller than tam_v3.

**Known limitations**
- Word error rate on real lines is above 5% for every model (best 6.90%). Most remaining word errors are punctuation and spacing: with punctuation ignored, best scores 4.75% WER.
- The fast model is 0.36 points over 8% WER on real lines (8.36%).
- Tamil numerals: best and integer read 57% of them on synthetic lines (stock `tam` 82%, fast 80%). Tamil symbols ௳–௺ ௐ are not read by best and integer.
- With the Tesseract 5.5.0–5.5.3 command-line program, the fast model stops with "Floating point exception" on 2 of 8,211 test lines in `--psm 7` (none in `--psm 13`; best and integer: none in either). This is Tesseract bug [tesseract-ocr/tesseract#4627](https://github.com/tesseract-ocr/tesseract/issues/4627), fixed in Tesseract 5.5.4; page modes and library use are not affected. The stock `tam` files did not hit it on these lines.

**Licence:** Apache-2.0, like `tam` and tam_v3. The word dictionary contains words from Tamil Wikisource text (CC BY-SA 4.0, its contributors). Training text includes Tamil Wikisource and Tamil Wikipedia text (CC BY-SA 4.0, their contributors) and English words from SCOWL by Kevin Atkinson. New training images use fonts under OFL-1.1 and GPL-3.0-or-later with the font exception. Details: [LICENSING.md](https://github.com/newsbaba24x7/tamil-tess-trainer/blob/main/models/tam_v3.1/LICENSING.md).

**Correction (25 Nov 2026):** the synthetic test row said "6 unseen fonts". 4 of the 6 fonts (Noto Sans Tamil Condensed Regular, Noto Serif Tamil Slanted Regular, Uni Ila.Sundaram-19 and TAU-Neythal) were used to train tam_v2 and tam_v3, so the row now says so, and a row for the 2 fonts never used in training was added. Every font used to train or test tam_multifont, tam_v2, tam_v3 and v3.1: [fonts.json](https://github.com/newsbaba24x7/tamil-tess-trainer/blob/main/models/tam_v3.1/fonts.json).

**Reproduce:** every step, script and seed is in [models/tam_v3.1/README.md](https://github.com/newsbaba24x7/tamil-tess-trainer/blob/main/models/tam_v3.1/README.md).
