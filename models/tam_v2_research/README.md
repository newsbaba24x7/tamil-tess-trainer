# Model card: tam_v2_research (V2-research), non-commercial research model

`tam_v2_research` is the second model trained with tamtrain, from fonts only. It fixed the
problems V1 showed on real scans and was the first to beat the stock `tam` model there. It is
published for research and comparison, **for non-commercial use only**
([CC BY-NC 4.0](LICENSE.md)), because some of its training fonts are licensed for non-commercial
use only. **For best results, and for any commercial use, use [tam_v2](../../MODEL_CARD.md).**

| | |
|---|---|
| Version | 2.0.0-research (trained 17 November 2026, under the working name `tam_multifont_v2`) |
| Files | `tam_v2_research.traineddata` (float, 6.0 MB); `tam_v2_research_fast.traineddata` (integer, 3.4 MB) |
| Tesseract | 5.x (trained and tested with 5.5.0) |
| Licence | **CC BY-NC 4.0, non-commercial use only**. See [LICENSE.md](LICENSE.md) |

```bash
curl -LO https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v2.0.0-research/tam_v2_research.traineddata
tesseract page.png out -l tam_v2_research --tessdata-dir .
```

## Training

- **Fonts only, no real scans:** 276 font styles from 91 families, 400 rendered lines each
  (110,400 lines). Three families (Tiro Tamil, TAU-Kambar, Sundaram-20) were held out for
  testing. Fonts and licences: [fonts.json](fonts.json) and
  [examples/fonts-v1-v2-research.md](../../examples/fonts-v1-v2-research.md).
- **Fixes for what V1 got wrong on real scans:**
  - 59 styles draw the pre-1978 letter shapes: fonts that need an OpenType feature for them use
    it on half their lines;
  - word spaces at least 0.25 em wide, plus justified spacing (30% of lines) and letter-spacing
    (12%);
  - only a tenth of the Tamil-digit numbers kept, so damaged letters aren't read as digits;
  - stronger scan damage.
- **Text:** Tesseract's `tam.training_text`, with zero-width characters removed.
- **Training:** 50,000 iterations from `tam` (tessdata_best), learning rate 0.0001, about 2 hours
  on 4 CPU cores. Settings: [settings.json](settings.json).

**Font licences.** Of the 276 styles, 220 are OFL, GPL, Apache or CC-BY, and 7 are Kadugu TAU
river fonts (free use and distribution). The rest are why this model is non-commercial:

- **45 styles from 20 C-DAC GIST families** (Kumudam, Kalki, Kannadasan, Chanakya, Madhura,
  Krishnan and others): "for non-commercial free usage";
- **Latha:** proprietary, Microsoft;
- **uniAmma-10, -11 and -16:** origin unknown.

Only images of text rendered with them were used; the fonts are not distributed.

## Results

None of these test sets was used for training.

| Test | Stock `tam` | V1 | **V2-research** | tam_v2 |
|---|---:|---:|---:|---:|
| 197 real scanned pages, CER | 6.33% | 6.34% | **5.27%** | 4.07% |
| the same, Tamil characters only | 4.34% | 4.19% | **3.63%** | 2.60% |
| the same, WER | 31.1% | 32.0% | **26.0%** | 20.8% |
| pages better / worse than stock (by > 0.5 points) | – | 62 / 57 | **136 / 5** | 173 / 1 |
| 109 clean pages, WER | 19.1% | – | **15.5%** | 12.6% |
| words with pre-1978 letter shapes read exactly | 80.7% | 77.6% | **82.5%** | 86.6% |
| stray Tamil digits written (the pages have 6) | 173 | 227 | **40** | 11 |
| 3,968 real lines from those pages, CER / WER | 3.56% / 21.2% | 3.21% / 19.8% | **2.30% / 14.7%** | 1.49% / 10.1% |
| held-out rendered lines (its own test set), CER / WER | 6.12% / 21.7% | 2.55% / 9.5% | **2.51% / 8.8%** | – |
| Tamil OCR Benchmark (200 lines), CER / WER | 5.44% / 9.9% | 5.43% / 10.7% | **5.50% / 9.8%** | 3.25% / 10.3% |
| RANLP 2025 synthetic Tamil (7,000 lines, the paper's scoring), CER / WER | 7.36% / 58.0% | 0.97% / 14.2% | **1.07% / 11.2%** | 1.15% / 17.9% |

- On RANLP 2025, V2-research has a lower word error rate than Google's commercial services in the
  paper (Document AI 11.98%, Cloud Vision 12.04%), though more character errors (1.07% against
  0.78%). That set is clean renders of fonts it was trained on, so real scans are the harder test.
- It is better than stock on easy (2.80% → 2.17%), medium (8.90% → 7.14%) and hard real pages
  (23.5% → 21.5%). Its most common error is still a spurious space that splits a word.

Reports: [rendered lines](../../examples/report-v2-research-276-styles.md),
[real scans](../../examples/scans-report-v2-research.md).
