# Model card: tam_v3.1, open Tesseract models for printed Tamil

`tam_v3.1` is a set of three Tesseract 5 LSTM models for printed Tamil, one for each kind of official
Tesseract model, fine-tuned from `tam_v3` (which comes from `tam_v2` and Tesseract's official `tam`).
They clean the character set, add Tamil numerals, English words and punctuation, and train again on
16,012 of tam_v3's own real scanned lines. Use them in place of `tam` or `tam_v3`; they are proposed as
replacements for `tam` in tessdata_best, tessdata and tessdata_fast.

| | |
|---|---|
| Version | 3.1.0 (22 November 2026) |
| Files | `tam_best_v3.1.traineddata` (float, 7.3 MB, most accurate, can be fine-tuned further); `tam_v3.1.traineddata` (the same network in integers, 4.6 MB, a third less time per line); `tam_fast_v3.1.traineddata` (a smaller integer network, 4.4 MB) |
| Tesseract | 5.x (trained and tested with 5.5.0; for single-line modes with the command-line program, 5.5.4 or later, see Limitations) |
| Output | Unicode Tamil, NFC, composed vowel signs (ொ ோ ௌ), no zero-width characters; Latin letters, Tamil numerals |
| Licence | Apache-2.0, the same as the `tam` model it starts from. See [NOTICE](NOTICE) and [models/tam_v3.1/LICENSING.md](models/tam_v3.1/LICENSING.md) |

## Use

```bash
curl -LO https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v3.1.0/tam_v3.1.traineddata
tesseract page.png out -l tam_v3.1 --tessdata-dir .
```

`tam_best_v3.1` is the most accurate and the one to fine-tune; `tam_v3.1` is for everyday use;
`tam_fast_v3.1` is the smallest network and the best of the three on Tamil numerals, mixed Tamil-English
text and English terms. To use one as Tesseract's Tamil model, copy it into your tessdata folder as
`tam.traineddata`. Tamil text with English words needs only `-l tam_v3.1` (it reads Latin letters).
Single text lines read best with `--psm 13`; whole pages with the default page mode.

## Results

None of these test sets was used for training, and the real test lines were not used to choose the
model either. CER = character error rate, WER = word error rate; lower is better.

| Test | Stock `tam` | tam_v3 | **tam_v3.1** |
|---|---:|---:|---:|
| **3,968 real lines from 197 pages, best model, CER / WER** (`--psm 13`, scored as for tam_v3) | 3.56% / 21.2% | 1.13% / 7.9% | **0.97% / 6.9%** |
| the same, integer model | 3.56% / 21.2% | 1.21% / 8.0% | **1.04% / 7.0%** |
| the same, fast model | 4.18% / 22.8% | – | **1.33% / 8.3%** |
| the same, best model, strict scoring (invisible characters and quote variants count) | 9.38% / 61.9% | 1.13% / 7.9% | **0.98% / 6.9%** |
| 1,389 rendered lines, text never trained on, in 6 fonts not used to train tam_v3.1 itself (4 of them were used to train tam_v2 and tam_v3), best model, CER / WER (strict) | 19.4% / 68.6% | 6.59% / 27.9% | **5.54% / 24.8%** |
| the 463 of them in the 2 fonts never used to train tam_v2, tam_v3 or tam_v3.1 (Uni Ila.Sundaram-20, Latha) | 20.7% / 71.0% | 8.51% / 35.9% | **7.24% / 31.2%** |

On the real lines, best and integer are better than tam_v3 by 0.16 and 0.17 CER points and by 1.04
and 0.97 WER points; the 95% confidence intervals (resampling whole pages) exclude zero.

| Rendered lines by content, CER (strict) | tam_v3 | **v3.1 best** | **v3.1 fast** |
|---|---:|---:|---:|
| Tamil text | 2.39% | **1.97%** | 2.38% |
| vowel signs and consonant combinations | 1.60% | **1.32%** | 1.92% |
| grantha letters | 3.01% | **2.65%** | 3.33% |
| pulli and diacritics | 1.79% | **1.32%** | 2.03% |
| Tamil numerals | 14.9% | 12.7% | **8.1%** |
| mixed Tamil-English | 10.2% | 8.4% | **6.1%** |
| English technical terms in Tamil | 13.6% | 10.8% | **7.3%** |

On the real lines, 93.0% of quotation marks are read (tam_v3 88.5%), and no line contains a character
outside the model's character set. Reading speed on one core of an Intel i3-9100 is 46, 31 and 30 ms per
line (best, integer, fast), within 3% of the stock networks; loading takes 0.14–0.16 s, and peak memory is 39–48 MB.

**Not yet measured for tam_v3.1:** whole pages (tam_v3's 197-page test), the Tamil OCR Benchmark,
RANLP 2025 and low-resolution scans. tam_v3's results there are in its
[model card](models/tam_v3/README.md). Full v3.1 report: [models/tam_v3.1/RESULTS.md](models/tam_v3.1/RESULTS.md).

## Training data

- **Real scanned lines:** 16,012 of tam_v3's 174,624 real training lines (814 archive.org pages from
  251 books), cut again with tam_v3's line boxes. No test book was used.
- **Rendered lines:** 16,012 lines, mixed half and half with the real lines, rendered in 20 font files:
  16 for Tamil under OFL-1.1 (Noto Sans Tamil, Noto Serif Tamil, Mukta Malar, Lohit Tamil) or
  GPL-3.0-or-later with the font exception (Samyak Tamil), and 4 for English (Noto Sans and Noto Serif,
  Regular and Bold; OFL-1.1). They are listed in [models/tam_v3.1/fonts.tsv](models/tam_v3.1/fonts.tsv),
  which also lists 4 italic English files that the renderer never picked. Every font used to train or
  test tam_multifont, tam_v2, tam_v3 and tam_v3.1 is listed in
  [models/tam_v3.1/fonts.json](models/tam_v3.1/fonts.json). The text is tam_v3's training text plus all
  36 Tamil numeral forms (௦ … ௫௲), English words (SCOWL) and technical terms, and book-style punctuation.
- **Character set:** tam_v3's, with 36 entries removed (control characters, Cyrillic and Cherokee
  look-alikes, CJK, Hangul, Malayalam, and a pulli + invisible U+200C entry) and 8 added (`^`, `` ` ``,
  `×`, ௐ, ௶, ௷, ௹, ௺). See [models/tam_v3.1/charset_report.md](models/tam_v3.1/charset_report.md).
- **Dictionary:** tam_v3's word list cleaned to the new character set and deduplicated (366,671 words);
  punctuation patterns with straight single quotes added (404 patterns).
- **Model choice:** checkpoints and the blend 0.5 × tam_v3 + 0.5 × fine-tuned model were chosen on
  tam_v3's 2,854 real check lines with a rule fixed in advance.
- **Fast model:** the lower layers of the best model, kept frozen, with new `Lfx128` and output layers.

Training: 20,000 iterations from `tam_v3` at learning rate 0.0001 for the best model; 40,000 for the fast
layers. The commands and scripts are in [models/tam_v3.1/README.md](models/tam_v3.1/README.md).

## Limitations

- **Word errors are above 5% on real lines** (best 6.9%), mostly from punctuation and spacing; with
  punctuation ignored, 4.75%.
- **Fast model:** 8.3% WER on real lines, more than best and integer.
- **Tamil numerals:** best and integer read 57% of the numerals on rendered lines (stock 82%, fast 80%);
  Tamil digits look like letters (௧/க, ௨/உ, ௭/எ, ௮/அ).
- **Tamil symbols** ௳–௺ ௐ are not read by best and integer (fast 31%).
- On real lines, ஔ / ௌ was read 7 times out of 11 (tam_v3 9) and dashes 82.8% of the time (tam_v3 86.4%).
- **Tesseract 5.5.0–5.5.3 command-line program:** with `--psm 7`, the fast model stops with "Floating
  point exception" on 2 of 8,211 test lines. This is Tesseract bug tesseract-ocr/tesseract#4627, fixed
  in Tesseract 5.5.4; page modes, `--psm 13` and library use were not affected.
- Whole pages, low-resolution scans and newspapers are not measured yet; tam_v3's limits there
  probably apply. Not for handwriting, and not for legacy-encoded (TSCII, TAB/TAM, Bamini) PDF text layers.

## Other models

- **tam_v3** (release [v3.0.0](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.0.0),
  model card [models/tam_v3](models/tam_v3/README.md)): the previous model, one float and one integer
  file, measured on more test sets (whole pages, public benchmarks, low resolution).
- **tam_v2** (release [v2.0.0](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0),
  model card [models/tam_v2](models/tam_v2/README.md)), **V1** (`tam_multifont`) and **V2-research**
  (`tam_v2_research`, non-commercial use only): see their model cards.

## Checksums (SHA-256)

Listed in `SHA256SUMS` on the release page. Check with `sha256sum -c SHA256SUMS`.
