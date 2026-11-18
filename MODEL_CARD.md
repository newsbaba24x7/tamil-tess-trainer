# Model card: tam_v3, an open Tesseract model for printed Tamil

`tam_v3` is a Tesseract 5 LSTM model for printed Tamil, fine-tuned from `tam_v2`, which was
fine-tuned from Tesseract's official `tam` model (tessdata_best). It was trained only on openly
licensed fonts and openly licensed text, plus 174,624 real scanned lines from 394 proofread
books and periodical issues. Use it in place of `tam` or `tam_v2`.

| | |
|---|---|
| Version | 3.0.0 (18 November 2026) |
| Files | `tam_v3.traineddata` (float, 8.5 MB, most accurate, can be fine-tuned further); `tam_v3_fast.traineddata` (integer, 5.7 MB, faster, within 0.3 points of the float model) |
| Tesseract | 5.x (trained and tested with 5.5.0) |
| Output | Unicode Tamil, NFC, composed vowel signs (ொ ோ ௌ), no zero-width characters |
| Licence | Apache-2.0, the same as the `tam` model it starts from. See [NOTICE](NOTICE) for the data sources |

## Use

```bash
curl -LO https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v3.0.0/tam_v3.traineddata
tesseract page.png out -l tam_v3 --tessdata-dir .
```

Or copy the file into your tessdata folder (`tesseract --list-langs` shows where it is) and use
`-l tam_v3`. For Tamil pages with some English, `-l tam_v3+eng` also works. Single text lines
read best with `--psm 13`; whole pages with the default page mode. Scan at 300 DPI where you can
(see Limitations).

## Results

None of these test sets was used for training. CER = character error rate, WER = word error
rate; lower is better.

| Test | Stock `tam` | tam_v2 | **tam_v3** |
|---|---:|---:|---:|
| **197 real scanned pages from 186 Wikisource books, CER** | 6.33% | 4.07% | **3.41%** |
| the same, Tamil characters only | 4.34% | 2.60% | **2.07%** |
| the same, WER | 31.1% | 20.8% | **19.1%** |
| pages better / worse than stock (by > 0.5 points) | – | 173 / 1 | **179 / 0** |
| 109 clean pages, WER | 19.1% | 12.6% | **11.4%** |
| 3,968 real lines from those pages, CER / WER (`--psm 13`) | 3.56% / 21.2% | 1.49% / 10.1% | **1.13% / 7.9%** |
| words with pre-1978 letter shapes read exactly | 80.7% | 86.6% | **87.8%** |
| stray Tamil digits written (the pages have 6) | 173 | **11** | 17 |
| Tamil OCR Benchmark (200 lines, English words in Tamil), CER / WER | 5.44% / 9.9% | 3.25% / 10.3% | **1.54% / 8.4%** |
| RANLP 2025 synthetic Tamil (7,000 lines, the paper's scoring), CER / WER | 7.36% / 58.0% | 1.15% / 17.9% | **0.80% / 12.8%** |
| Rendered lines in fonts and text never trained on, CER | 5.82% | 2.30% | **2.25%** |
| Old-book pages rescaled to 72 DPI, CER | **21.6%** | 22.3% | 23.5% |
| Contemporary pages at 300 DPI, CER | 2.60% | 2.02% | **1.68%** |
| Contemporary pages at 96 DPI, CER | 19.6% | **19.2%** | 19.3% |

**RANLP 2025:** the paper's best system, Google Document AI, scores CER 0.78%, WER 11.98%,
BLEU 0.5803, ANLS 0.9923 and METEOR 0.8762. tam_v3 scores 0.80%, 12.78%, **0.5825**, 0.9923 and
0.8715: ahead on BLEU, level on ANLS and close on the other three. Stock Tesseract scores 7.36%
CER there.

By page difficulty (grouped by the stock model's CER), real-page CER is 1.38% on easy pages
(stock 2.80%, tam_v2 1.63%), 4.20% on medium pages (8.90%, 5.28%) and 16.4% on hard ones (23.5%,
18.1%). Reading speed is the same as tam_v2: about 1.5 s per page for the float model and 1.1 s
for the fast one on one CPU thread, with 108 MB of memory. Every result, with BLEU, ANLS and
METEOR, is on the [benchmark page](https://newsbaba24x7.github.io/tamil-tess-trainer/benchmarks/).

## Training data

- **Real scanned lines:** 174,624 lines from 394 proofread Tamil Wikisource books and periodical
  issues, each shown once: tam_v2's 24,445 lines from 37 books, and 150,179 lines from 357 more.
  Pages come from archive.org copies of the scans (116,797 lines) or from the scans on Wikimedia
  (57,827 lines). Among them are 11 issues of the newspaper Dravida Nadu (1945, 1950 and 1954;
  its other years are kept for testing) and 2 magazine issues. 127 of the books were printed
  before the 1978 script reform; 72 have no year. No test book was used, and 67 lines whose text
  shares a run of four words with any test set were left out. The full list, with page links,
  line boxes and text, is `tam_v3-real-lines.jsonl.gz`; `tools/crop_lines.py` rebuilds the line
  images from it.
- **Rendered lines:** 91,530 training lines in the same 233 openly licensed font styles as
  tam_v2 (450 lines per style), with scan-like damage. Three families (Tiro Tamil, TAU-Kambar,
  Sundaram-20) were held out for testing. Fonts and licences:
  [examples/fonts-v2-open.md](examples/fonts-v2-open.md), [models/tam_v3/fonts.json](models/tam_v3/fonts.json).
- **Text for the rendered lines:** book text proofread on Tamil Wikisource from 420 training
  books (54%), Tesseract's `tam.training_text` (36%) and sentences from the openings of 5,000
  random Tamil Wikipedia articles (10%), which often give an English name in brackets after the
  Tamil one. Paragraphs that share a run of four words with any test set were removed. Released
  as `tam_v3-training-text.txt.gz`.
- **Dictionary:** tam_v2's word list plus words that appear at least twice in the 420 training
  books, 433,566 words in all; the book words are released as `tam_v3-wordlist.txt.gz`.
- **Progress check:** 2,854 real lines from 5 other books measured progress during training, as
  for tam_v2 (CER 0.89% at the end; tam_v2 1.20%).

Training: 270,000 iterations from `tam_v2`, in 14 sessions of 20,000
(`tamtrain train --segment-iterations 20000`, see the [README](README.md#train-fine-tune)),
learning rate 0.0001, 4 h 28 min on 2 CPU threads. All settings are in
[models/tam_v3/settings.json](models/tam_v3/settings.json); the commands are in the
[README](README.md#v3-more-real-lines).

## Limitations

- **Very low-resolution scans are read poorly, and 72 DPI slightly worse than before.** Old-book
  pages give 23.5% CER at 72 DPI (tam_v2 22.3%, stock 21.6%) and contemporary pages 19.3% at
  96 DPI. Almost all the real training lines come from high-resolution scans. A further round of
  training on shrunken copies of them brought 72 DPI to 20.6%, but made the model split words
  with spurious spaces elsewhere (RANLP 2025 CER went from 0.80% to 1.75%), so it was not used.
  Scan at 300 DPI where you can.
- **Word errors are still high on clean pages:** 11.4% of words are wrong, mostly from spurious
  spaces inside words and from punctuation, then wrong letters and page headers.
- **English words inside Tamil lines** are read better than before but still cost words.
- **Stray Tamil digits:** it writes a few more Tamil digits that are not on the page (17 on the
  test pages, which have 6) than tam_v2 (11).
- **Hard pages stay hard:** tables, text in several columns, very faded or damaged print
  (16.4% CER).
- **Newspapers:** 11 issues of one old newspaper were used in training; there is no newspaper
  test set yet.
- Not for handwriting, and not for legacy-encoded (TSCII, TAB/TAM, Bamini) PDF text layers.

## Other models

- **tam_v2** (release [v2.0.0](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0),
  model card [models/tam_v2](models/tam_v2/README.md)): the previous open model, trained on the
  same fonts and 24,445 real lines. It is slightly better on very low-resolution scans (72 and
  96 DPI) and writes fewer stray Tamil digits.
- **V1 (`tam_multifont`)** is released as a research model, for comparison: release
  [v1.0.0](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v1.0.0), model card
  [models/tam_multifont](models/tam_multifont/README.md). It was trained on fonts only, and 4 of
  its 188 font styles are not openly licensed: Latha (proprietary) and three uniAmma fonts
  (unknown origin).
- **V2-research (`tam_v2_research`)** is released as a research model for **non-commercial use
  only** (CC BY-NC 4.0): release
  [v2.0.0-research](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0-research),
  model card [models/tam_v2_research](models/tam_v2_research/README.md).

## Checksums (SHA-256)

Listed in `SHA256SUMS` on the release page. Check with `sha256sum -c SHA256SUMS`.
