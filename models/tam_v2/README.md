# Model card: tam_v2, an open Tesseract model for printed Tamil

`tam_v2` is a Tesseract 5 LSTM model for printed Tamil, fine-tuned from Tesseract's official `tam`
model (tessdata_best). It was trained only on openly licensed fonts and openly licensed text,
plus real scanned book lines with proofread text. Use it in place of `tam`.

**Superseded by tam_v3** (release [v3.0.0](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v3.0.0), [model card](../../MODEL_CARD.md)), which is more accurate on every test at normal scanning resolution.

| | |
|---|---|
| Version | 2.0.0 (17 November 2026) |
| Files | `tam_v2.traineddata` (float, 6.5 MB, most accurate, can be fine-tuned further); `tam_v2_fast.traineddata` (integer, 3.7 MB, faster, within 0.1 points of the float model) |
| Tesseract | 5.x (trained and tested with 5.5.0) |
| Output | Unicode Tamil, NFC, composed vowel signs (ொ ோ ௌ), no zero-width characters |
| Licence | Apache-2.0, the same as the `tam` model it starts from. See [NOTICE](../../NOTICE) for the data sources |

## Use

```bash
curl -LO https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v2.0.0/tam_v2.traineddata
tesseract page.png out -l tam_v2 --tessdata-dir .
```

Or copy the file into your tessdata folder (`tesseract --list-langs` shows where it is) and use
`-l tam_v2`. For Tamil pages with some English, `-l tam_v2+eng` also works. Single text lines
read best with `--psm 13`; whole pages with the default page mode.

## Results

None of these test sets was used for training. CER = character error rate, WER = word error
rate; lower is better.

| Test | Stock `tam` | **tam_v2** |
|---|---:|---:|
| **197 real scanned pages from 186 Wikisource books, CER** | 6.33% | **4.07%** |
| the same, Tamil characters only | 4.34% | **2.60%** |
| the same, WER | 31.1% | **20.8%** |
| pages better / worse than stock (by > 0.5 points) | – | **173 / 1** |
| 109 clean pages, WER | 19.1% | **12.6%** |
| 109 clean pages, wrong words when spacing and punctuation are ignored | 8.8% | **4.1%** |
| 3,968 real lines from those pages, CER / WER | 3.56% / 21.2% | **1.49% / 10.1%** |
| words with pre-1978 letter shapes read exactly | 80.7% | **86.6%** |
| stray Tamil digits written (the pages have 6) | 173 | **11** |
| Tamil OCR Benchmark (200 lines), CER / WER | 5.44% / 9.9% | **3.25%** / 10.3% |
| RANLP 2025 synthetic Tamil (7,000 lines, the paper's scoring), CER / WER | 7.36% / 58.0% | **1.15% / 17.9%** |

By page difficulty, real-page CER fell from 2.80% to 1.63% on easy pages, 8.90% to 5.28% on
medium pages and 23.5% to 18.1% on hard ones. The full reports are in [examples/](../../examples/), and
the [README](../../README.md#v2-results) compares tam_v2 with the two research models trained before it.
Scores of all models on every test set, including BLEU, ANLS and METEOR and pages rescaled to
72, 96 and 300 DPI, are in [benchmarks/BASELINE.md](../../benchmarks/BASELINE.md).

## Training data

- **Rendered lines:** 186,400 lines in 233 font styles from 71 families, all with open
  licences (OFL, GPL, Apache, CC-BY) except the 7 Kadugu TAU river fonts, whose author allows
  free use and distribution. 64 styles also draw the pre-1978 letter shapes. Lines have
  scan-like damage: blur, noise, faded and spreading ink, show-through, low resolution, warped
  baselines. Three families (Tiro Tamil, TAU-Kambar, Sundaram-20) were held out for testing.
  Fonts and licences: [examples/fonts-v2-open.md](../../examples/fonts-v2-open.md),
  [models/tam_v2/fonts.json](fonts.json).
- **Text:** book text proofread on Tamil Wikisource (60%) and Tesseract's `tam.training_text`
  (40%), with zero-width characters removed. Released as `tam_v2-training-text.txt.gz`.
- **Real scanned lines:** 24,445 lines from 37 proofread Wikisource books, cut from archive.org
  copies of the scans and paired with the proofread text. Each was shown three times. 2,854 lines
  from 5 other books measured progress during training. The training books' known publication
  years run from 1941 to 2014; 14 were printed before the 1978 script reform (10 have no year).
  No test book was used.
  The full list, with page links, line boxes and text, is `tam_v2-real-lines.jsonl.gz`;
  `tools/crop_lines.py` rebuilds the line images from it.
- **Dictionary:** the stock `tam` word list plus 41,431 words that appear at least twice in the
  training books, released as `tam_v2-wordlist.txt.gz`.

Training: 100,000 iterations from `tam` (tessdata_best), learning rate 0.0001, about 4 hours on 4
CPU cores. Render settings are in [models/tam_v2/settings.json](settings.json); the
commands are in the [README](../../README.md#real-scanned-lines-the-v2-pipeline).

## Limitations

- **Word errors are not yet under the 3% target.** On clean pages 12.6% of words are wrong. The
  largest cause is spurious spaces that split a word (5.1 points), mostly right after a vowel
  sign or pulli (தரை யோடு), then wrong letters (4.3), punctuation (2.3) and page headers (0.8).
- **English words inside Tamil lines** are often misread.
- **Hard pages stay hard:** tables, text in several columns, very faded or damaged print
  (18.1% CER).
- **Very low-resolution scans are read poorly.** Old-book pages that tam_v2 reads with 7.3% CER
  at full resolution give 22.3% at 72 DPI, where it is no better than the stock model (21.6%).
  Contemporary pages go from 5.1% to 19.2% at 96 DPI. Scan at 300 DPI where you can.
- **Not tested yet:** old and contemporary newspapers.
- Not for handwriting, and not for legacy-encoded (TSCII, TAB/TAM, Bamini) PDF text layers.

## Other models

- **V1 (`tam_multifont`)** is released as a research model, for comparison: release
  [v1.0.0](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v1.0.0), model card
  [models/tam_multifont](../../models/tam_multifont/README.md). It was trained on fonts only, and 4 of
  its 188 font styles are not openly licensed: Latha (proprietary) and three uniAmma fonts
  (unknown origin). It is no better than the stock model on real scans.
- **V2-research (`tam_v2_research`)** is released as a research model for **non-commercial use
  only** (CC BY-NC 4.0): release
  [v2.0.0-research](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0-research),
  model card [models/tam_v2_research](../../models/tam_v2_research/README.md). Besides Latha and
  uniAmma, it was trained with 45 styles of the C-DAC GIST fonts, whose licence allows
  non-commercial use only. On real scans it is better than stock (CER 5.27%), but not as good
  as tam_v2.

## Checksums (SHA-256)

Listed in `SHA256SUMS` on the release page. Check with `sha256sum -c SHA256SUMS`.
