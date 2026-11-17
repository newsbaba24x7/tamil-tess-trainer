# Model card: tam_multifont (V1), a research model

`tam_multifont` is the first model trained with tamtrain. It is published for comparison and
research. **For reading real scans, use [tam_v2](../../MODEL_CARD.md)**: V1 is no better than the
stock `tam` model on real scanned pages.

| | |
|---|---|
| Version | 1.0.0 (trained 17 November 2026) |
| Files | `tam_multifont.traineddata` (float, 6.0 MB); `tam_multifont_fast.traineddata` (integer, 3.4 MB) |
| Tesseract | 5.x (trained and tested with 5.5.0) |
| Licence | Apache-2.0, like the `tam` model it starts from. Read the font note below |

```bash
curl -LO https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v1.0.0/tam_multifont.traineddata
tesseract page.png out -l tam_multifont --tessdata-dir .
```

## Training

- **Fonts only, no real scans:** 188 font styles from 70 families, 400 rendered lines each
  (75,200 lines) with scan-like damage. Three families (Tiro Tamil, TAU-Kambar, Sundaram-20)
  were held out for testing. Fonts and licences: [fonts.json](fonts.json) and
  [examples/fonts-v1-v2-research.md](../../examples/fonts-v1-v2-research.md).
- **Text:** Tesseract's `tam.training_text`, with zero-width characters removed.
- **Training:** 50,000 iterations from `tam` (tessdata_best), learning rate 0.0001, about an
  hour on 4 CPU cores. Settings: [settings.json](settings.json).

**Font note.** 4 of the 188 styles do not have an open licence: **Latha**, a proprietary
Microsoft font, and **uniAmma-10, -11 and -16**, whose origin is unknown. Only images of text
rendered with them were used; the fonts are not distributed. 7 styles are Kadugu TAU river fonts
(free use and distribution, no standard licence); the other 177 are OFL, GPL, Apache or CC-BY.
If you need a model trained only on openly licensed fonts, use tam_v2.

## Results

None of these test sets was used for training.

| Test | Stock `tam` | **V1** | tam_v2 |
|---|---:|---:|---:|
| 197 real scanned pages, CER | 6.33% | 6.34% | 4.07% |
| the same, Tamil characters only | 4.34% | 4.19% | 2.60% |
| the same, WER | 31.1% | 32.0% | 20.8% |
| pages better / worse than stock (by > 0.5 points) | – | 62 / 57 | 173 / 1 |
| words with pre-1978 letter shapes read exactly | 80.7% | 77.6% | 86.6% |
| stray Tamil digits written (the pages have 6) | 173 | 227 | 11 |
| 3,968 real lines from those pages, CER / WER | 3.56% / 21.2% | 3.21% / 19.8% | 1.49% / 10.1% |
| held-out rendered lines (V1's own test set), CER | 6.54% | 2.01% | – |
| Tamil OCR Benchmark (200 lines), CER / WER | 5.44% / 9.9% | 5.43% / 10.7% | 3.25% / 10.3% |
| RANLP 2025 synthetic Tamil (7,000 lines, the paper's scoring), CER / WER | 7.36% / 58.0% | 0.97% / 14.2% | 1.15% / 17.9% |

## What V1 showed

V1 learned the training fonts very well: on rendered lines its character errors fell by more
than two thirds, and it has the lowest character error rate of all our models on the RANLP 2025
synthetic set. On real scans it gained nothing, for three reasons the real-scan report made
visible:

1. **It forgot part of the pre-1978 letter shapes** (ணா, றா, னா, ணை, லை…) that the stock model
   could read. Only 5 of its 188 styles drew them (Lohit Tamil Classical and Karla Tamil); the
   OpenType features that turn them on in other fonts were not used yet.
2. **It split more words with spurious spaces**, often right after a vowel sign, because several
   training fonts have very narrow word spaces.
3. **It read damaged letters as Tamil digits** (௬ for சு, ௦ for ம).

tam_v2 fixes all three and adds real scanned lines. Reports: [rendered lines](../../examples/report-188-styles.md),
[real scans](../../examples/scans-report-188-styles.md).
