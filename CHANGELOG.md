# Changelog

All notable changes to tamil-tess-trainer, newest first. Dates are in UTC.
Model releases are on the [Releases page](https://github.com/newsbaba24x7/tamil-tess-trainer/releases).

## Since v3.1.0 (documentation and website only, no model changes)

### 25 November 2026

- **New status page.** [docs/status](https://newsbaba24x7.github.io/tamil-tess-trainer/status/) explains why
  tam_v3.1 should become Tesseract's Tamil model and shows where the three pull requests stand. The project
  page links to it.
- **Corrected: test fonts.** The 1,389 rendered test lines were described as using 6 fonts not used for
  training. 4 of the 6 were used to train tam_v2 and tam_v3, so only Uni Ila.Sundaram-20 and Latha are new
  to tam_v3.1. The model card, RESULTS.md, LICENSING.md, fonts.tsv, the benchmark page, the v3.1.0 release
  notes and the three pull request descriptions now say so. The model card, RESULTS.md, the release notes
  and the pull request descriptions also give scores on the 463 lines in those 2 fonts: tam_best_v3.1
  7.24% CER / 31.20% WER, stock `tam` (tessdata_best) 20.75% / 70.96%.
- **Corrected: font count.** tam_v3.1's training lines were rendered with 20 font files, not 23 (16 Tamil
  files, plus Noto Sans and Noto Serif Regular and Bold for English).
- **New: [models/tam_v3.1/fonts.json](models/tam_v3.1/fonts.json).** Every font style used to train or test
  tam_multifont, tam_v2, tam_v3 and tam_v3.1 (249 styles), with their licences and, where recorded, how
  many lines each one rendered.
- **Status page fix.** Our own edit of the pull request descriptions no longer shows as "New activity".
- **New: this changelog.**

### 22 November 2026

- README and MODEL_CARD.md present tam_v3.1 as the current model. tam_v3's model card moved to
  [models/tam_v3/README.md](models/tam_v3/README.md). NOTICE lists the tam_v3.1 sources.
- The project page shows tam_v3.1 as the current model, with one summary table.
- New benchmark page for tam_v3.1. The tam_v3 page moved to
  [docs/benchmarks/tam_v3](https://newsbaba24x7.github.io/tamil-tess-trainer/benchmarks/tam_v3/).
- tam_v3.1 documents updated after publication: real-test scores are also given as tam_v3's benchmark
  scores them (invisible characters dropped, quote and dash variants folded).

## v3.1.0 — 22 November 2026: tam_v3.1 (best, integer, fast)

- Three models, one for each Tesseract model repository: `tam_best_v3.1` (tessdata_best),
  `tam_v3.1` (tessdata, integer) and `tam_fast_v3.1` (tessdata_fast).
- Fine-tuned from tam_v3 with a cleaned character set, 16,012 of tam_v3's own real scanned lines and
  16,012 new rendered lines with Tamil numerals, English words and book punctuation.
- On 3,968 real test lines, tam_best_v3.1 scores 0.98% CER / 6.90% WER (stock `tam`: 9.38% / 61.95%,
  strict scoring). Scored as tam_v3's benchmark does (invisible characters dropped, quote and dash variants
  folded): 0.97% / 6.88% (stock `tam`: 3.56% / 21.16%).
- Pull requests opened to make it Tesseract's `tam` model in
  [tessdata_best](https://github.com/tesseract-ocr/tessdata_best/pull/89),
  [tessdata](https://github.com/tesseract-ocr/tessdata/pull/209) and
  [tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast/pull/41).
- Benchmark page, 19–21 November: the Anuvaad Tamil model, handwriting and camera-photo tests, a new
  scanning-resolution test, and the version of each stock model. Rows wrongly labelled as the Ubuntu
  package model (they were tam_v2) were removed.

## v3.0.0 — 18 November 2026: tam_v3

- Fine-tuned from tam_v2 with 174,624 real scanned lines from 394 books and periodical issues proofread
  on Tamil Wikisource, the same 233 font styles as tam_v2, and Tamil Wikipedia text with English names.
- Training can run in sessions, with tools for long runs, and runs faster.
- New project page and benchmark page on GitHub Pages; BLEU, ANLS and METEOR scores for all models.

## v2.0.0 — 17 November 2026: tam_v2

- Fine-tuned from Tesseract's own `tam` with 233 font styles and 24,445 real scanned book lines proofread
  on Tamil Wikisource.
- The 233 font styles were recorded as openly licensed. A later review (22 November) found that some of
  these licences are unverified or differ from the records: see
  [models/tam_v3.1/LICENSING.md](models/tam_v3.1/LICENSING.md), section 3.
- First release of the trainer (tamtrain) in this repository.

## v2.0.0-research — 17 November 2026: tam_v2_research (non-commercial use only)

- Research model trained on fonts only (276 styles), including C-DAC GIST fonts licensed for
  non-commercial use, so the model is licensed CC BY-NC 4.0. It was the first of our models to beat
  stock `tam` on real scans.

## v1.0.0 — 17 November 2026: tam_multifont (research model)

- The first model trained with tamtrain, on fonts only (188 styles), published for comparison. It is no
  better than stock `tam` on real scanned pages. 4 of its styles are not openly licensed: Latha
  (proprietary) and three uniAmma fonts (unknown origin).
