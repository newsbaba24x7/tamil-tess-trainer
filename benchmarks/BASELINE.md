# Benchmark scores of the current models

Scores of every current model on every test set, measured 17 November 2026 with Tesseract 5.5.0.
CER and WER: lower is better.
BLEU, ANLS and METEOR (0–1): higher is better, computed as NLTK does (see `tamtrain/metrics.py`).

## Key findings

1. **Our scoring matches the RANLP 2025 paper.** The Ubuntu-packaged stock `tam` model scores what the paper reports for Tesseract 5.5.0: CER 7.73% vs 7.80%, BLEU 0.0507 vs 0.0493, ANLS 0.9270 vs 0.9264, METEOR 0.3226 vs 0.3201 (WER 58.4% vs 61.5%). Comparisons with Document AI are like for like.
2. **No current model beats Document AI on RANLP 2025.** V2-research beats it on WER only (11.16% vs 11.98%). V1 comes closest on the other four (CER 0.97% vs 0.78%). V2 is furthest of our models, because it restores real Tamil word boundaries in this mostly vowel-sign-stripped text.
3. **Low resolution is the biggest weakness.** The same old-book pages go from 7.28% CER (V2, full resolution) to 22.27% at 72 DPI, where V2 is no better than stock (21.59%; better on 11 pages, worse on 9). Contemporary pages go from 5.12% to 19.18% at 96 DPI, with all models alike.
4. **At normal resolution V2 leads on every real-print set:** old books 7.28% vs stock 11.55%, contemporary books 2.02% vs 2.60% at 300 DPI, real test lines 1.49% vs 3.56%.
5. **English words in Tamil lines** (Tamil OCR Benchmark): V2 has the lowest CER (3.25%), but its WER, BLEU and METEOR are no better than the older models'.
6. **The fast models score within about 0.4 points of the full ones** everywhere.

## RANLP 2025 synthetic Tamil (7,000 lines), scored as in the paper

Text compared as is (`--raw`), each image read in Tesseract's default page mode (`--psm 3`). Paper rows are Table 1 of Jayatilleke & de Silva, *Zero-shot OCR Accuracy of Low-Resourced Languages* (RANLP 2025).

| System | CER ↓ | WER ↓ | BLEU ↑ | ANLS ↑ | METEOR ↑ |
|---|---:|---:|---:|---:|---:|
| Document AI (Google, commercial), paper | 0.78% | 11.98% | 0.5803 | 0.9923 | 0.8762 |
| Cloud Vision API (Google, commercial), paper | 0.79% | 12.04% | 0.5790 | 0.9922 | 0.8751 |
| EasyOCR, paper | 11.72% | 28.76% | 0.3461 | 0.8828 | 0.6744 |
| Tesseract 5.5.0, paper | 7.80% | 61.45% | 0.0493 | 0.9264 | 0.3201 |
| Surya, paper | 13.92% | 65.00% | 0.1487 | 0.8672 | 0.3359 |
| Stock `tam` (tessdata_best) | 7.36% | 57.98% | 0.0501 | 0.9303 | 0.3258 |
| Stock `tam` (Ubuntu package) | 7.73% | 58.35% | 0.0507 | 0.9270 | 0.3226 |
| V1 `tam_multifont` | 0.97% | 14.15% | 0.5587 | 0.9905 | 0.8600 |
| V2-research `tam_v2_research` | 1.07% | 11.16% | 0.5514 | 0.9893 | 0.8560 |
| **V2 `tam_v2`** | 1.15% | 17.94% | 0.4994 | 0.9887 | 0.8214 |
| V2 `tam_v2_fast` | 1.18% | 18.38% | 0.4942 | 0.9884 | 0.8191 |

## 3,968 real lines from the 197 test pages

`--psm 13`, as in training.

| Model | CER ↓ | WER ↓ | BLEU ↑ | ANLS ↑ | METEOR ↑ |
|---|---:|---:|---:|---:|---:|
| Stock `tam` (tessdata_best) | 3.56% | 21.16% | 0.4320 | 0.9593 | 0.7373 |
| Stock `tam` (Ubuntu package) | 4.18% | 22.77% | 0.4280 | 0.9493 | 0.7280 |
| V1 `tam_multifont` | 3.21% | 19.79% | 0.4879 | 0.9631 | 0.7706 |
| V2-research `tam_v2_research` | 2.30% | 14.65% | 0.5406 | 0.9720 | 0.8022 |
| **V2 `tam_v2`** | 1.49% | 10.08% | 0.6363 | 0.9814 | 0.8613 |
| V2 `tam_v2_fast` | 1.46% | 10.11% | 0.6341 | 0.9818 | 0.8609 |

## 2,854 real check lines (5 books, used to monitor V2's training)

`--psm 13`.

| Model | CER ↓ | WER ↓ | BLEU ↑ | ANLS ↑ | METEOR ↑ |
|---|---:|---:|---:|---:|---:|
| Stock `tam` (tessdata_best) | 3.21% | 19.53% | 0.4342 | 0.9636 | 0.7541 |
| Stock `tam` (Ubuntu package) | 3.60% | 21.15% | 0.4191 | 0.9562 | 0.7355 |
| V1 `tam_multifont` | 2.65% | 16.68% | 0.4855 | 0.9692 | 0.7965 |
| V2-research `tam_v2_research` | 1.93% | 12.34% | 0.5243 | 0.9779 | 0.8268 |
| **V2 `tam_v2`** | 1.20% | 8.27% | 0.5979 | 0.9866 | 0.8687 |
| V2 `tam_v2_fast` | 1.32% | 8.22% | 0.6015 | 0.9851 | 0.8698 |

## Tamil OCR Benchmark (200 lines, English words in Tamil text)

`--psm 7`.

| Model | CER ↓ | WER ↓ | BLEU ↑ | ANLS ↑ | METEOR ↑ |
|---|---:|---:|---:|---:|---:|
| Stock `tam` (tessdata_best) | 5.44% | 9.92% | 0.5838 | 0.9124 | 0.8597 |
| Stock `tam` (Ubuntu package) | 5.36% | 9.72% | 0.5879 | 0.9162 | 0.8632 |
| V1 `tam_multifont` | 5.43% | 10.69% | 0.5765 | 0.9165 | 0.8610 |
| V2-research `tam_v2_research` | 5.50% | 9.78% | 0.5897 | 0.9157 | 0.8675 |
| **V2 `tam_v2`** | 3.25% | 10.27% | 0.5772 | 0.9489 | 0.8598 |
| V2 `tam_v2_fast` | 3.24% | 10.27% | 0.5797 | 0.9488 | 0.8603 |

## 197 real Wikisource pages

Whole pages, Tesseract's default page mode. From V2's evaluation.

| Model | CER ↓ | Tamil CER ↓ | WER ↓ |
|---|---:|---:|---:|
| Stock `tam` (tessdata_best) | 6.33% | 4.34% | 31.10% |
| V1 `tam_multifont` | 6.34% | 4.19% | 32.01% |
| V2-research `tam_v2_research` | 5.27% | 3.63% | 25.95% |
| **V2 `tam_v2`** | 4.07% | 2.60% | 20.84% |
| V2 `tam_v2_fast` | 4.14% | 2.68% | 20.92% |

## ICON-style test sets

Proofread Wikisource pages (text by Wikisource volunteers) with archive.org page images, rescaled so that 12-pt body text matches the stated scanning resolution. Each set is shown at the archive.org image's own resolution and at the stated one. Pages whose text belongs to another page are found at full resolution and left out of both; every other page counts, however badly it is read at low resolution. Old newspapers and contemporary newspapers are not built yet.

### Old books at 72 DPI

| Model | Full resolution (23 pages): CER / WER | At 72 DPI (23 pages): CER / WER |
|---|---:|---:|
| Stock `tam` (tessdata_best) | 11.55% / 53.75% | 21.59% / 71.41% |
| Stock `tam` (Ubuntu package) | 11.46% / 52.88% | 21.98% / 72.63% |
| V1 `tam_multifont` | 10.63% / 54.11% | 24.02% / 75.47% |
| V2-research `tam_v2_research` | 8.99% / 44.12% | 22.17% / 70.14% |
| **V2 `tam_v2`** | 7.28% / 35.43% | 22.27% / 67.97% |
| V2 `tam_v2_fast` | 7.30% / 35.47% | 21.83% / 67.14% |

### Contemporary books at 300 DPI

| Model | Full resolution (24 pages): CER / WER | At 300 DPI (24 pages): CER / WER |
|---|---:|---:|
| Stock `tam` (tessdata_best) | 3.28% / 14.40% | 2.60% / 12.51% |
| Stock `tam` (Ubuntu package) | 3.40% / 15.19% | 2.81% / 13.65% |
| V1 `tam_multifont` | 3.07% / 13.59% | 2.43% / 11.72% |
| V2-research `tam_v2_research` | 2.80% / 11.53% | 2.26% / 10.06% |
| **V2 `tam_v2`** | 2.52% / 10.74% | 2.02% / 9.70% |
| V2 `tam_v2_fast` | 2.53% / 11.01% | 2.02% / 9.76% |

### Contemporary books at 96 DPI

| Model | Full resolution (6 pages): CER / WER | At 96 DPI (6 pages): CER / WER |
|---|---:|---:|
| Stock `tam` (tessdata_best) | 5.73% / 20.68% | 19.63% / 34.72% |
| Stock `tam` (Ubuntu package) | 5.79% / 20.42% | 19.93% / 34.20% |
| V1 `tam_multifont` | 5.54% / 18.73% | 19.67% / 33.55% |
| V2-research `tam_v2_research` | 5.32% / 16.38% | 19.23% / 30.17% |
| **V2 `tam_v2`** | 5.12% / 16.12% | 19.18% / 30.17% |
| V2 `tam_v2_fast` | 5.17% / 16.38% | 19.17% / 30.04% |

## Speed (single thread, 8 real pages, this machine)

| Model | Seconds per page | Peak memory |
|---|---:|---:|
| Stock `tam` (tessdata_best) | 1.49 | 95 MB |
| Stock `tam` (Ubuntu package) | 1.05 | 88 MB |
| V2 `tam_v2` | 1.59 | 105 MB |
| V2 `tam_v2_fast` | 1.15 | 97 MB |

## How these were measured

Six models, 4 CPU cores, about 30 minutes in all. Reports with every page and line are in `work-v2/report/` (not published). The commands, with `--compare` for V1 and V2-research:

```bash
python3 -m tamtrain lines benchmarks/ranlp2025/lines --work work-v2 --name ranlp2025-raw-psm3 --raw --psm 3
python3 -m tamtrain lines benchmarks/wikisource-test-lines --work work-v2 --name real-test-lines-psm13 --psm 13
python3 -m tamtrain lines books-lines/dev --work work-v2 --name real-dev-lines-psm13 --psm 13
python3 -m tamtrain lines benchmarks/tamil-ocr-benchmark/lines --work work-v2 --name tamil-ocr-benchmark
python3 -m tamtrain scans benchmarks/icon-style/source/old-books --work work-v2 --name icon-source-old-books
python3 tools/make_dpi_set.py benchmarks/icon-style/source/old-books --out benchmarks/icon-style/old-books-72dpi --dpi 72
python3 -m tamtrain scans benchmarks/icon-style/old-books-72dpi --work work-v2 --name icon-old-books-72dpi \
    --exclude-from work-v2/report/icon-source-old-books.json
```

