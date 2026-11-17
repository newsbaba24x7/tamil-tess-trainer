# Tamil OCR for Tesseract: the open tam_v2 model and its trainer

**tam_v2** is an open Tesseract model for printed Tamil. It was fine-tuned from Tesseract's own
`tam` model with openly licensed fonts and 24,445 real scanned book lines whose text was
proofread on Tamil Wikisource. On 197 real scanned pages it never saw, it makes 36% fewer
character errors than the stock model, and it is better on 173 of the pages and worse on one.

```bash
curl -LO https://github.com/newsbaba24x7/tamil-tess-trainer/releases/download/v2.0.0/tam_v2.traineddata
tesseract page.png out -l tam_v2 --tessdata-dir .
```

| 197 real scanned pages | Stock `tam` | **tam_v2** |
|---|---:|---:|
| Character errors (CER) | 6.33% | **4.07%** |
| Tamil characters only | 4.34% | **2.60%** |
| Word errors (WER) | 31.1% | **20.8%** |
| Clean pages: word errors | 19.1% | **12.6%** |

**Project page: [newsbaba24x7.github.io/tamil-tess-trainer](https://newsbaba24x7.github.io/tamil-tess-trainer/)**,
an overview with features, every benchmark result, the models and references.

Downloads, test results, training data and known limits are in the [model card](MODEL_CARD.md).
`tam_v2_fast.traineddata` is the smaller integer version; it scores within 0.1 points of the
full one. Licence: Apache-2.0, like Tesseract's own models.

The two earlier models trained with this tool are also available as research models, for
comparison. Both were trained on fonts only.

- **V1 (`tam_multifont`)** is no better than the stock model on real scans. 4 of its font styles
  have no open licence. See its [model card](models/tam_multifont/README.md) and
  [release v1.0.0](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v1.0.0).
- **V2-research (`tam_v2_research`)** beat the stock model on real scans (CER 5.27%), but less
  than tam_v2. It is for **non-commercial use only** (CC BY-NC 4.0), because it was trained with
  the C-DAC GIST fonts. See its [model card](models/tam_v2_research/README.md) and
  [release v2.0.0-research](https://github.com/newsbaba24x7/tamil-tess-trainer/releases/tag/v2.0.0-research).

The rest of this page is about **tamtrain**, the tool that trained tam_v2. Use it to train
your own Tamil model or to test models on real scans.

## tamtrain: train Tesseract's Tamil model

Give it a folder of Unicode Tamil fonts. It renders thousands of realistic, scan-like text lines
in every font, fine-tunes Tesseract's official `tam` model on them, and measures how the new
model compares with the stock one on lines it never saw and on real scanned book pages.

```
fonts + Tamil text ──► render line images ──► fine-tune tam (tessdata_best) ──► evaluate
                         (png + gt.txt)          best + fast .traineddata         before/after report
```

The training recipe is the same as
[tesseract-ocr/tesstrain](https://github.com/tesseract-ocr/tesstrain) with `LANG_TYPE=Indic`.
The rendered lines use tesstrain's `*.png` + `*.gt.txt` layout, so you can also feed them to tesstrain.

## Requirements

- **Tesseract 5 with its training tools**: `lstmtraining`, `combine_tessdata`,
  `unicharset_extractor`, `merge_unicharsets`, `combine_lang_model`, `dawg2wordlist`.
  On Debian/Ubuntu: `sudo apt install tesseract-ocr`.
- **Python 3.9+ with Pillow built with libraqm**, which correct Tamil shaping needs.
  On Debian/Ubuntu: `sudo apt install python3-pil libraqm0`. The tool stops with a clear message
  if raqm is missing.
- **Internet on the first run.** It downloads `tam.traineddata` from tessdata_best and a few small
  langdata files, cached in `~/.cache/tamtrain` (change the location with `TAMTRAIN_CACHE`).

There is nothing else to install. Run it from this folder with `python3 -m tamtrain`, or install it
with `pip install .` to get a `tamtrain` command.

## Quick start

1. See which of your fonts can be used. `--ocr-check` renders a test sentence in each font and
   reads it back with your installed `tam` model:

   ```bash
   python3 -m tamtrain fonts --fonts ~/my-tamil-fonts --ocr-check
   ```

2. Render, train and evaluate in one go:

   ```bash
   python3 -m tamtrain all --fonts ~/my-tamil-fonts --name tam_myfonts \
       --lines-per-font 1000 --iterations 10000
   ```

3. Use the new model:

   ```bash
   tesseract page.png out --tessdata-dir work/output/tessdata_best -l tam_myfonts
   ```

## Steps one at a time

```bash
python3 -m tamtrain render   --fonts ~/my-tamil-fonts --lines-per-font 1000
python3 -m tamtrain train    --name tam_myfonts --iterations 10000
python3 -m tamtrain evaluate
```

Stopping training (Ctrl+C) is safe. Run `train` again with a higher `--iterations` and it
continues from the last checkpoint. Add `--fresh` to start over.

All commands accept `--work DIR` (default `./work`) and `--jobs N` (default: all CPU cores).
Run `python3 -m tamtrain <command> --help` for every option.

### `render`: make training images

| Option | Default | Meaning |
|---|---|---|
| `--fonts` | (required) | Font files or folders (searched recursively); .ttf/.otf/.ttc |
| `--include` / `--exclude` | | Glob patterns on `"Font Name [file.ttf]"`, e.g. `"*bold*"` |
| `--text` | official `tam.training_text` | Your own UTF-8 Tamil text files |
| `--lines-per-font` | 800 | Line images per font |
| `--eval-ratio` | 0.1 | Share held out for evaluation; held-out lines use text never used in training |
| `--holdout-font` | | Fonts (name substring) used **only** for evaluation, to test unseen fonts |
| `--coverage-ratio` | 0.15 | Share of lines that cycle through every Tamil syllable (ஙெ, ஞொ, ஷௌ…) |
| `--min-chars` / `--max-chars` | 12 / 60 | Line length |
| `--min-size` / `--max-size` | 28 / 64 | Font size range in pixels |
| `--clean-ratio` | 0.3 | Share of images without degradation |
| `--no-degrade` | | Clean images only |
| `--no-latin` | | Drop lines containing English words |
| `--old-letters` | 0.5 | For fonts with an OpenType feature for the pre-1978 letter shapes, the share of their lines drawn with it (0 = never) |
| `--tamil-digits` | 0.1 | Share of Tamil-digit numbers (௧௨௩) kept from the text |
| `--min-word-gap` | 0.25 | Word spaces narrower than this (in em) are widened |
| `--justify-ratio` | 0.3 | Share of lines with wider, justified-looking word spaces |
| `--tracking-ratio` | 0.12 | Share of lines with letter-spacing inside words |

The other images get a random mix of scan and print effects:

- **geometry**: rotation (up to 1.6°) and a gently warped baseline, as near a book's binding;
- **ink**: ink spread, bleed that fills small loops, faded print, broken strokes, uneven ink;
- **paper**: grey or stained paper, show-through from the other side of the page, dust specks;
- **capture**: low resolution, blur, sensor noise, JPEG artefacts and binarisation.

Effects that remove ink are only applied to larger text, so small marks like the pulli (்)
survive.

**Pre-1978 letter shapes.** Books printed before the 1978 script reform write ணா றா னா (and
ணொ றோ…) and ணை லை ளை னை as ligatures. Many fonts still contain those shapes behind an OpenType
feature: Mukta Malar `ss04`, Hind Madurai `hlig`, Tiro Tamil `dlig`, and `ss01` in Anek Tamil,
Post No Bills Jaffna and Yaldevi Jaffna. Arima and Catamaran (`ss02`) have only the old ணை லை
ளை னை. Lohit Tamil Classical and Karla Tamil draw them by default. `fonts` lists what each
font has, and `render` draws half the lines of those fonts with the old shapes. The text
stays modern Unicode, which is what the model must output. `evaluate` reports the error rate
on old-shape lines separately.

**Word spacing.** Lines are drawn word by word with a minimum word gap, some with wider,
justified-looking spaces, and some with letter-spacing inside words. Fonts with very narrow
spaces taught the earlier model that any small gap starts a new word.

**Tamil digits.** ௦–௯ are rare in real print and look like letters (௬/சு, ௦/ம). Only 10% of
the numbers written with them are kept, which brings them from 4.8 to 0.5 per 1,000 characters.

### `train`: fine-tune

| Option | Default | Meaning |
|---|---|---|
| `--name` | `tam_custom` | Model name (the `-l` value) |
| `--start-model` | `tam` | `tam` downloads tessdata_best; or a path to a *float* `.traineddata`; or `none` to train from scratch |
| `--iterations` | 10000 | Training iterations (one line per iteration) |
| `--learning-rate` | 0.0001 (0.002 from scratch) | |
| `--wordlist` | | Extra dictionary words, one per line, added to the stock `tam` dictionary |
| `--extra-gt` | | Folders of **real scanned lines** (`x.png` + `x.gt.txt`) to train on alongside the fonts |
| `--extra-gt-eval` | | Folders of real lines used only to measure progress during training (other books) |
| `--real-repeat` | 1 | Show each real training line this many times |
| `--eval-max` | 500 | At most this many lines in the progress check during training (0: all) |
| `--train-threads` | all cores | CPU threads for `lstmtraining` |
| `--fresh` | | Discard earlier checkpoints |

**Training time.** Measured on 4 CPU cores, fine-tuning takes about 0.046 s per iteration (0.050 s
with 2 threads, 0.068 s with 1), so 100,000 iterations take about 80 minutes. To keep it there:

- **Run nothing else heavy while training.** V2's training ran at half that speed because other
  jobs were using the CPU. `train` warns when the machine is busy, and records the time per
  iteration and every setting in `work/config.json`.
- **Start from the best model you have** (`--start-model path/to/model.traineddata`, a float
  model). Fine-tuning a model that already reads most lines needs far fewer iterations.
- **Give it lines it gets wrong.** When fine-tuning, a line the model already reads perfectly
  costs time but teaches nothing: in V2's training only 27% of the iterations changed the
  model. Real scans and new kinds of damage teach more than more of the same renders.
- **Render only what training will use.** Each iteration reads one line, so render about as many
  lines as iterations; V2 rendered twice as many as it used, and converting each line for
  training takes about 25 ms.
- **Keep the progress check small.** It runs in a second thread on every check; 500 lines
  (`--eval-max`) measure progress as well as thousands.

### `evaluate`: before/after report

This command OCRs the held-out lines with the start model, your installed `tam` and the new
model in both its best and fast versions. It writes `work/report/report.md` and `report.json`
with character and word error rates (CER/WER), the error rate on lines with old and modern
letter shapes, a per-font table and the most frequent confusions. Use
`--compare label=path/to/other.traineddata` to add more models.

### `scans`: test on real scanned pages

Rendered lines can't show how a model copes with real paper, ink and old printing. `scans` OCRs
whole scanned pages, including Tesseract's layout analysis, with the same models as `evaluate`. It
compares the output with the page text and writes `work/report/scans.md` and `scans.json`.

```bash
python3 tools/fetch_wikisource.py --out scans/wikisource --pages 200   # real pages + proofread text
python3 -m tamtrain scans scans/wikisource
```

A page is any image (`.png`/`.jpg`/`.tif`) next to a `.gt.txt` file with the same name that holds
its text. Your own scans work the same way. The report gives:

- **CER and WER** over the whole page;
- **Tamil CER**, the error rate on Tamil characters only. It ignores spacing, punctuation and digits,
  which proofreaders and printers often handle differently;
- results grouped by how hard each scan is, a per-page table and the most common confusions;
- **Tamil digits written**: how often a model wrote ௦–௯ where the page has none, which usually
  means it misread a damaged letter.

`tools/fetch_wikisource.py` downloads pages that volunteers have proofread (quality 3) or
validated (quality 4) on [Tamil Wikisource](https://ta.wikisource.org). It samples at random
across the whole site, with at most 2 pages per book. It removes wiki markup but keeps running
headers and page numbers that the proofreaders typed. It saves the page list in `pages.json`;
`--from-list pages.json` downloads exactly the same pages again, so results can be compared
across models and over time. The text is licensed CC BY-SA 4.0 by the Wikisource contributors.

Other options: `--index-search QUERY` samples only from books or periodicals whose Wikisource
index page matches a search. Examples are `'insource:/Year *= *19[0-5][0-9]/'` for books
published 1900–1959, or `'intitle:"திராவிட நாடு"'` for issues of the Dravida Nadu weekly.
`--exclude-books pages.json` leaves out books used in another set, and `--delay` slows the
image downloads; Wikimedia blocks clients that fetch page images too fast.

`tools/make_dpi_set.py` rescales a page set to a chosen scanning resolution, for example old
books at 72 DPI. A scan's physical size is unknown, so the tool measures the body-text line
height and scales each page so its text is as large as 12-pt print (`--font-pt`) scanned at
that resolution. The estimate for one page is accurate to about ±20%. Pages with fewer than 5
text lines, such as full-page pictures, can't be measured and are skipped.

Score a rescaled set with `scans --exclude-from`, giving the report of the same pages at full
resolution. Pages that report found to carry another page's text are left out, and every other
page counts, however badly it reads at low resolution. Without it, pages that only fail because
of the low resolution would be left out too, and the scores would look better than they are.

```bash
python3 -m tamtrain scans benchmarks/icon-style/source/old-books --name icon-source-old-books
python3 tools/make_dpi_set.py benchmarks/icon-style/source/old-books --out benchmarks/icon-style/old-books-72dpi --dpi 72
python3 -m tamtrain scans benchmarks/icon-style/old-books-72dpi --name icon-old-books-72dpi \
    --exclude-from work/report/icon-source-old-books.json
```

### `lines`: test on any line-image benchmark

```bash
python3 tools/hf_arrow_to_lines.py data-00000-of-00001.arrow --out benchmarks/ranlp2025/lines
python3 -m tamtrain lines benchmarks/ranlp2025/lines --name ranlp2025
```

`lines` OCRs single-line images, each with a `.gt.txt` file, with the same models as
`evaluate`. A `groups.json` in the folder (`{"00001": "natural text", …}`) splits the results.
`--raw` compares text exactly as published benchmarks usually do, so invisible characters count
as errors. `tools/hf_arrow_to_lines.py` turns a Hugging Face dataset file (`.arrow`) with an
image and a text column into that layout, without needing pyarrow.

Besides CER and WER, the report gives **BLEU, ANLS and METEOR**, the text-similarity measures of
the RANLP 2025 OCR comparison, computed as NLTK computes them (`tamtrain/metrics.py`; checked
against NLTK 3.9.1). Every line's OCR text is saved in `<name>.ocr.json`, so other measures can be
computed later without reading the images again. The scores of all current models on every test
set are in [benchmarks/BASELINE.md](benchmarks/BASELINE.md).

## What happens to your fonts

Before training, each font is checked:

| Check | Why |
|---|---|
| Has Unicode Tamil characters | Legacy fonts (TSCII, TAB/TAM, Bamini…) put Tamil shapes on Latin code points. Training on them would teach wrong text, so they are skipped |
| Has all core letters, vowel signs and the pulli | Incomplete fonts are skipped |
| Has OpenType Tamil shaping (`taml`/`tml2`) | Without it ெ ே ை are drawn after the consonant and கு/டு ligatures break |
| Duplicate family + style | Copies are skipped; of two copies the one with more characters is kept |
| No Latin letters, digits or Grantha | Lines the font can't draw are skipped *for that font only* |
| Variable font | Every named weight becomes its own style. A width axis without named widths adds Regular and Bold at SemiCondensed, Condensed and ExtraCondensed widths, the kind of face newspaper headlines use |
| Old letter shapes | Fonts that can draw pre-1978 letters are found by measuring the shapes, and the feature that turns them on is recorded |

## Output

```
work/
  ground-truth/<font>/<font>_00001.png + .gt.txt   rendered lines (tesstrain layout)
  manifest.jsonl                                    font, split, size, degradations per line
  model/training.log                                full log of every training command
  model/checkpoints/                                lstmtraining checkpoints
  output/tessdata_best/<name>.traineddata           float model: most accurate, can be fine-tuned further
  output/tessdata_fast/<name>.traineddata           integer model: faster, slightly less accurate
  report/report.md                                  evaluation on held-out rendered lines
  report/scans.md                                   evaluation on real scanned pages (`scans`)
```

## Collecting more Tamil fonts

`tools/collect_fonts.py` downloads about 95 Tamil font families (Google Fonts, Tamil Virtual
Academy TAU series, NLCI 0.901, Chemmozhi, TSCu, TAMu, Kadugu, Akruti, Mooniak's Yaldevi Jaffna
and Abhaya Libre, GNU FreeSerif, the C-DAC GIST set and more). It skips families already installed, except the variable Noto Sans
and Noto Serif Tamil, which add every weight and condensed widths to the installed Regular and
Bold. It records each family's source and license. It also builds `fonts/choose.html`, a page
with a preview of every family, the stock model's error rate on it, and a warning for families
that are near-copies of another.

The 22 **C-DAC GIST** families (Kumudam, Kalki, Kannadasan, Chanakya, Madhura, Krishnan and
others) are print and display faces, including outlined, striped and shadowed advertisement
styles that the stock model can't read at all. Their licence allows **non-commercial use
only**. The page marks them, and **Leave out non-commercial** unticks them. They are fine for
experiments. A model trained on them should be published for non-commercial use only, as
V2-research is, unless C-DAC agrees otherwise.

```bash
python3 tools/collect_fonts.py --src ~/tamil-font-sources --out fonts
```

Each family in `fonts/catalog.json` has a licence class:

- **open:** OFL, GPL, Apache or CC-BY;
- **free-use:** the author grants free use and distribution, but there is no standard licence (the
  Kadugu TAU river fonts);
- **non-commercial:** the C-DAC GIST set.

`fonts/open-fonts.txt` lists the open families that are not near-copies of another, for models
meant to be published.

[examples/report-188-styles.md](examples/report-188-styles.md) is the evaluation of a model
trained on 188 styles (about 75 families), 400 lines each and 50,000 iterations, with three
families held out. It took about an hour on 4 CPU cores.

## Results so far: rendered lines vs real scans

Two models have been trained with this tool: V1 (`tam_multifont`) and V2-research
(`tam_v2_research`). Both start from the stock `tam` (tessdata_best)
model and use 400 lines per style, 50,000 iterations and the same three held-out families. The
real-scan test uses the same 197 proofread Wikisource pages from 186 books.

| Test | Stock `tam` (best) | V1: 188 styles | V2-research: 276 styles + fixes |
|---|---:|---:|---:|
| Rendered lines, CER (each model's own test set) | 6.54% / 6.12% | 2.01% | 2.51% |
| **197 real scanned pages, CER** | **6.33%** | 6.34% | **5.27%** |
| the same pages, Tamil characters only | 4.34% | 4.19% | 3.63% |
| the same pages, WER | 31.1% | 32.0% | 26.0% |
| pages better / worse than stock (by > 0.5 points) | – | 62 / 57 | **136 / 5** |
| words with pre-1978 letters read exactly | 80.7% | 77.6% | 82.5% |
| extra words from spurious spaces | +5.9% | +7.5% | +4.5% |
| Tamil digits written (the pages have 6) | 173 | 227 | 40 |

V1 looked very good on rendered lines but didn't improve real scans at all. Its
real-scan report showed three problems:

1. **Old printing got worse.** It forgot part of what the stock model knew about the pre-1978
   letter shapes.
2. **Words got split by spurious spaces**, mostly right after a vowel sign, such as கொ திக்க and
   வீ டு. Several training fonts have very narrow word spaces (0.18 em).
3. **Damaged letters were read as Tamil digits**, for example ௬ for சு and ௦ for ம.

V2-research was trained with fixes for all three: old letter shapes in 59 font styles,
widened word gaps with letter-spacing, and about a tenth of the Tamil digits. It also has
stronger scan damage and 88 more font styles, including condensed Noto and the C-DAC display
faces. That made the difference on real pages:

- **CER fell from 6.33% to 5.27% and WER from 31.1% to 26.0%.** The average page improved by
  1.15 points (95% bootstrap interval 0.99–1.33).
- It is better on easy pages (2.80% → 2.17%), medium pages (8.90% → 7.14%) and hard pages
  (23.5% → 21.5%).
- It reads old-print words better than the stock model now (80.7% → 82.5%), splits fewer words
  than the stock model, and writes 40 stray Tamil digits instead of 173.

Full reports: [rendered lines](examples/report-v2-research-276-styles.md) and
[real scans](examples/scans-report-v2-research.md); for V1,
[rendered lines](examples/report-188-styles.md) and [real scans](examples/scans-report-188-styles.md).
The V2-research run took about 2 hours on 4 CPU cores. Its fonts are listed in
[examples/fonts-v1-v2-research.md](examples/fonts-v1-v2-research.md).

**V2-research is for non-commercial use only.** It was trained with the 20 C-DAC GIST families
(non-commercial licence), Latha (proprietary) and uniAmma (unknown origin), so it is released
under CC BY-NC 4.0 ([model card](models/tam_v2_research/README.md)). V1 used Latha and uniAmma
but no C-DAC fonts ([model card](models/tam_multifont/README.md)). The open model, V2 (below),
uses openly licensed fonts only.

What is still left:

- **Spurious spaces are still the most common error** (1,313 inserted spaces on 197 pages),
  followed by `.` read as `,` and missing or extra pullis and ு signs.
- **Some old, heavily damaged pages are still worse than with the stock model.** The worst is
  page 12 of உலகப்பெரியார் காந்தி: 13.4% → 15.5%. V1 scored 17.8% on it.
- **Hard pages stay hard** (21.5%): tables, numbered lists in a separate column, and very poor
  scans.

Rendered fonts alone don't reach real-world quality. Real scanned lines in training are the
next step, and Tamil Wikisource has tens of thousands of proofread pages to draw them from.
Train on books that are not in the test set. The test pages are listed in
[examples/wikisource-pages.json](examples/wikisource-pages.json); download exactly the same
pages with `tools/fetch_wikisource.py --from-list examples/wikisource-pages.json`.

## Public benchmark: RANLP 2025 synthetic Tamil

[Nevidu/tamil_synthetic_ocr](https://huggingface.co/datasets/Nevidu/tamil_synthetic_ocr) has 7,000
clean single-line images from Jayatilleke & de Silva,
[*Zero-shot OCR Accuracy of Low-Resourced Languages*](https://aclanthology.org/2025.ranlp-1.56/)
(RANLP 2025). The paper compares five OCR systems on its Tamil part. Below are the paper's figures
(Table 1), and this tool's models measured the same way: text compared as is, and each image read
with Tesseract's default page mode (`--raw --psm 3`). CER and WER: lower is better; BLEU, ANLS and
METEOR: higher is better.

| System | CER | WER | BLEU | ANLS | METEOR |
|---|---:|---:|---:|---:|---:|
| Document AI (Google, commercial), paper | **0.78%** | 11.98% | **0.5803** | **0.9923** | **0.8762** |
| Cloud Vision API (Google, commercial), paper | 0.79% | 12.04% | 0.5790 | 0.9922 | 0.8751 |
| V1 (`tam_multifont`) | 0.97% | 14.15% | 0.5587 | 0.9905 | 0.8600 |
| V2-research (`tam_v2_research`) | 1.07% | **11.16%** | 0.5514 | 0.9893 | 0.8560 |
| V2 (`tam_v2`) | 1.15% | 17.94% | 0.4994 | 0.9887 | 0.8214 |
| Tesseract 5.5.0, paper | 7.80% | 61.45% | 0.0493 | 0.9264 | 0.3201 |
| Stock `tam`, Ubuntu package, measured here | 7.73% | 58.35% | 0.0507 | 0.9270 | 0.3226 |
| Stock `tam`, tessdata_best, measured here | 7.36% | 57.98% | 0.0501 | 0.9303 | 0.3258 |
| EasyOCR, paper | 11.72% | 28.76% | 0.3461 | 0.8828 | 0.6744 |
| Surya, paper | 13.92% | 65.00% | 0.1487 | 0.8672 | 0.3359 |

- **This tool scores the way the paper does.** The stock model from the Ubuntu package gets
  within 0.1 points of the paper's Tesseract CER and within 0.003 of its BLEU, ANLS and METEOR.
- **Document AI leads on four of the five measures.** V2-research has the lowest word error rate;
  V1 comes closest on the other four.

- **The paper's poor Tesseract result is mostly one invisible character.** The stock `tam`
  model writes U+200C after many pullis, which a plain comparison counts as an error and which
  breaks word matches. With invisible characters ignored, the stock model scores 2.55% CER and
  22.5% WER, and V2-research 1.02% and 10.9% (`lines` without `--raw`, one line per image).
- **96% of the dataset's text is not real Tamil.** In 6,803 of the 7,000 lines the spacing vowel
  signs (ா ி ு ூ ெ ே ை ொ ோ) were stripped from the source subtitles before the images were drawn,
  for example இங்கச ர்ந்தமழப for what should read with vowel signs. The images match their text,
  so the benchmark is consistent, but it rewards reading letter by letter over knowing Tamil.
  On the 197 natural lines V2-research makes 0.04% character errors.
- **It favours these models.** The images use six Google fonts (Hind Madurai, Noto Sans/Serif
  Tamil, Kavivanar, Pavanam, Anek Tamil), all in its training fonts, and they are clean
  renders. Real scans are the harder test (see above).

To reproduce:

```bash
curl -L -o data.arrow https://huggingface.co/datasets/Nevidu/tamil_synthetic_ocr/resolve/main/data/data-00000-of-00001.arrow
python3 tools/hf_arrow_to_lines.py data.arrow --out benchmarks/ranlp2025/lines
python3 -m tamtrain lines benchmarks/ranlp2025/lines --work work-v2-research --name ranlp2025-raw --raw --psm 3
```

The dataset card states no licence, so the images are used here for testing only and are not
redistributed.

## V2: the open model

V2 is the model meant for publishing, trained only on fonts that allow it. The earlier
276-style model is kept as **V2-research** for comparison.

**Fonts:** 233 styles from 71 families, listed with their licences in
[examples/fonts-v2-open.md](examples/fonts-v2-open.md). Compared with V2-research, it
drops the C-DAC GIST set (non-commercial), Latha (proprietary) and uniAmma (unknown origin). It
adds Mooniak's Abhaya Libre (5 weights, with old letter shapes), GNU FreeSerif, and the NLCI
0.901 releases of ThiruValluvar and Auvaiyar. 64 styles can draw the pre-1978 letter shapes. The
same file lists every font that was checked but not used, and why. The 7 free-use Kadugu fonts
are included; leave them out with `--exclude "*TAU-kaviri*" …` if only formal licences are wanted.

[models/tam_v2/fonts.json](models/tam_v2/fonts.json) lists every style with its file name,
licence and old-letter feature. `tools/collect_fonts.py` downloads most of them. Mukta Malar, Noto
Sans/Serif Tamil, Lohit and Samyak come from Google Fonts or your Linux distribution's font
packages.

**Target: under 3% word errors on clean, modern print.** On V2-research's real-scan test, word
errors on the 109 cleaner pages come mostly from spacing and punctuation. V2-research gets
15.5% of words wrong there, but only 6.0% when spacing and punctuation are ignored.

| Cause of word errors (197 real pages, V2-research) | Points |
|---|---:|
| Words with 2+ wrong letters | 10.9 |
| Words with 1 wrong letter | 5.0 |
| Words split by spurious spaces | 4.2 |
| Punctuation (`.` read as `,`, a space before `?`) | 3.8 |
| Running headers and page numbers | 2.2 |

Planned changes, biggest effect first:

1. **Train on real scanned lines from Tamil Wikisource.** Proofread pages are cut into lines and
   matched to their text. Whole book PDFs are downloaded and rendered locally, because Wikimedia
   blocks fast page-image downloads. The test books stay out.
2. **Fix word splitting:** real lines, stronger letter-spacing, and a larger Tamil dictionary built
   from proofread Wikisource text.
3. **Use book-style training text** with realistic punctuation, from proofread Wikisource pages.
4. **Train longer:** about 1,000 lines per style, and choose the checkpoint by real-scan results.
5. **Measure fairly:** by page type, with and without headers, plus the 100-image test set (old
   newspapers at 200 DPI, old books at 72 DPI, contemporary books at 300 and 96 DPI).
   V2 is compared with the stock `tam`, V1 and V2-research.

### V2 results

V2 (`tam_v2`) was trained on 233 openly licensed font styles (186,400 rendered lines, with
book-style text from proofread Wikisource books) plus 24,445 real scanned lines from 37 books,
shown three times each. It was checked during training on 2,854 real lines from 5 other books,
and trained for 100,000 iterations (about 4 hours on 4 CPU cores). Its dictionary adds book
words to the stock one.

| Test (never trained on) | Stock `tam` | V1 | V2-research | **V2 (open)** |
|---|---:|---:|---:|---:|
| **197 real pages, CER** | 6.33% | 6.34% | 5.27% | **4.07%** |
| the same, Tamil characters only | 4.34% | 4.19% | 3.63% | **2.60%** |
| the same, WER | 31.1% | 32.0% | 26.0% | **20.8%** |
| pages better / worse than stock | – | 62 / 57 | 136 / 5 | **173 / 1** |
| clean pages (109): WER | 19.1% | – | 15.5% | **12.6%** |
| clean pages: words wrong, spacing and punctuation ignored | 8.8% | – | 6.0% | **4.1%** |
| 3,968 real lines from the test pages, CER / WER (`--psm 13`) | 3.56% / 21.2% | 3.21% / 19.8% | 2.30% / 14.7% | **1.49% / 10.1%** |
| rendered held-out lines, CER / WER | 5.88% / 20.3% | 2.81% / 10.1% | 2.70% / 8.9% | **2.35% / 7.8%** |
| Tamil OCR Benchmark (200 lines), CER / WER | 5.44% / 9.9% | 5.43% / 10.7% | 5.50% / 9.8% | **3.25%** / 10.3% |
| RANLP 2025 (7,000 lines, paper's scoring), CER / WER | 7.36% / 58.0% | 0.97% / 14.2% | 1.07% / 11.2% | 1.15% / 17.9% |

- On real pages V2 is better on easy (2.80% → 1.63%), medium (8.90% → 5.28%) and hard pages
  (23.5% → 18.1%). It writes 11 stray Tamil digits where stock writes 173, and reads 86.6% of
  words with pre-1978 letters exactly (stock 80.7%).
- On RANLP, V2's extra word errors are spaces. 96% of that set is Tamil with the vowel signs
  stripped, with spaces where real Tamil can't have them (இங்கச ர்ந்தமழப). V2 has learned real
  word boundaries and restores them. On its natural-Tamil lines V2 has 0.07% CER and 0.86% WER.
- The fast (integer) model scores within 0.1 points of the best (float) model everywhere.
- **The 3% target is not reached yet.** On clean pages V2 gets 12.6% of words wrong. Its biggest
  cause is now **spurious word splits** (5.1 points), mostly right after a vowel sign or pulli
  (தரை யோடு, அஞ் சாதவனைக்) and before `?`. Then come letters (4.3), punctuation (2.3) and page
  headers (0.8).
- English words inside Tamil lines are still misread (the Tamil OCR Benchmark).

Reports: [real pages](examples/scans-report-v2-open.md),
[real test lines](examples/real-test-lines-v2-open.md),
[real check lines](examples/real-dev-lines-v2-open.md),
[rendered lines](examples/report-v2-open.md), [RANLP 2025](examples/ranlp2025-v2-open.md),
[Tamil OCR Benchmark](examples/tamil-ocr-benchmark-v2-open.md).

**Scoring single lines:** line images cut from pages contain slivers of the neighbouring lines.
With `--psm 7` Tesseract re-finds the line and loses accuracy (V2: 5.23% CER), so line sets
are scored with `--psm 13` (raw line), as in training. Whole pages are always scored with the
default page mode.

### Real scanned lines: the V2 pipeline

```bash
# 1. pick fully proofread books (never a test book), get their text, render 40 pages each
python3 tools/fetch_wikisource_books.py select --out books --train 72 --dev 8 \
    --exclude-books examples/wikisource-pages.json
python3 tools/fetch_wikisource_books.py texts --out books
python3 tools/ia_book_pages.py books          # page images from archive.org (or: ... pdfs --out books)

# 2. cut the pages into lines matched to the proofread text
python3 tools/page_lines.py books/train/* --out books-lines/train \
    --model-dir work-v2-research/output/tessdata_best --lang tam_v2_research
python3 tools/page_lines.py books/dev/* --out books-lines/dev \
    --model-dir work-v2-research/output/tessdata_best --lang tam_v2_research

# 3. book-style training text and dictionary, from the training books only
python3 tools/build_corpus.py books --corpus corpus-v2.txt --wordlist wordlist-v2.txt \
    --mix ~/.cache/tamtrain/langdata/tam.training_text

# 4. render the open fonts with that text, then train on rendered + real lines
#    (fonts/v2: a folder with the fonts in models/tam_v2/fonts.json)
python3 -m tamtrain render --work work-v2 --fonts fonts/v2 \
    --text corpus-v2.txt --lines-per-font 800 \
    --holdout-font "Tiro Tamil" "TAU-Kambar" "Sundaram-20"
python3 -m tamtrain train --work work-v2 --name tam_v2 --iterations 100000 \
    --extra-gt books-lines/train --extra-gt-eval books-lines/dev --real-repeat 3 \
    --wordlist wordlist-v2.txt
```

**Shortcut: the exact V2 lines.** The release has the list of every real line V2 used, with its
text, page link and box (`tam_v2-real-lines.jsonl.gz`), the rendering text
(`tam_v2-training-text.txt.gz`) and the dictionary words (`tam_v2-wordlist.txt.gz`). Instead of
steps 1–3:

```bash
python3 tools/crop_lines.py tam_v2-real-lines.jsonl.gz --out real-lines    # train, dev and test
gunzip -k tam_v2-training-text.txt.gz tam_v2-wordlist.txt.gz
```

Then use `real-lines/train` and `real-lines/dev` in step 4, and `real-lines/test` with
`tamtrain lines --psm 13` to repeat the real-line test.

Step 2 used the V2-research model only to find the lines on each page. The stock `tam` model
works too; it keeps fewer lines.

- **Page images come from archive.org.** Wikimedia blocks fast downloads of page images, but
  many Wikisource books are Tamil Virtual Academy scans that archive.org also holds, often at
  600 ppi. `ia_book_pages.py` finds the archive.org copy by title. It pairs each proofread page
  with an archive.org page by comparing archive.org's own OCR text, and checks that most pages
  match before downloading. The proofread text stays the ground truth. 42 of 63 books were
  found this way; the others need Wikimedia's PDFs (`fetch_wikisource_books.py pdfs`).
- **Index labels are often wrong.** Many books marked fully proofread on Wikisource are not,
  so `texts` samples each candidate's pages and accepts a book only if most are really
  proofread. Of about 600 candidates, 63 were accepted.
- **`fetch_wikisource_books.py`:** books are spread over publication eras (before 1960,
  1960–99, 2000 on, unknown), with at most 2 per author. Periodicals stay out, because they are
  test material. It downloads one PDF per book and renders the pages locally with `pdftoppm`.
- **`page_lines.py`:** a line is kept only if its first and last words agree with the
  proofread text. That keeps line boundaries right even when the rough reading has errors. On
  the 197 test pages it kept about 20 lines per page, and every one of 14 lines checked by eye was
  correct, including the hardest ones.
- **`--extra-gt-eval`:** these real lines, from books not used for training, become the training
  log's evaluation set. Progress is then measured on real scans, not on rendered lines.
- **`--real-repeat`:** shows each real training line that many times, because rendered lines
  far outnumber them.

## Getting a model that helps everyone

- **Use many fonts.** Fine-tuning on a few fonts makes the model better at those and slightly
  worse at others. Train on a broad mix of plain book fonts, newspaper fonts and decorative
  fonts, and check the per-font table for regressions.
- **Always hold out fonts** (`--holdout-font`) and report results on them. That is the honest
  measure of how well the model works on fonts nobody trained on.
- **Add real scans** with `--extra-gt`, and **test on real scans** with `scans`. Rendered fonts
  can't reproduce old letterpress printing or pre-1978 letter forms. A model can improve a lot on
  rendered lines and not at all on real pages (see above).
- **Train long enough.** Use thousands of lines per font and 10,000+ iterations, and watch the eval
  error in the log.
- **Use clean text.** The default corpus is cleaned automatically: zero-width characters are
  removed, text is NFC-normalized, and noisy words are dropped (for example `அதத$ய(யதபத`, or `௨ன்னை`
  with the digit ௨ instead of the letter உ). Clean your own corpus the same way.

## Notes on Tamil output

- The stock `tam` model writes an invisible **U+200C (zero-width non-joiner) after many pullis**
  (்). It learned this from its training text: the official `tam.training_text` has U+200C after
  688,820 of its 1.79 million pullis. This tool strips zero-width characters from the training
  text, so trained models stop doing it. In a test of 60 lines, the stock model wrote 98 of them and
  the trained model wrote none. The report's main CER ignores invisible characters, so the
  comparison is on visible text only; "raw CER" counts them. If you keep using the stock model,
  strip U+200C from its output before searching or comparing text.
- Ground truth uses Unicode's composed vowel signs: `ொ` (U+0BCA), `ோ` (U+0BCB), `ௌ` (U+0BCC).

## Contributing a model upstream

Community Tesseract models go to
[tesseract-ocr/tessdata_contrib](https://github.com/tesseract-ocr/tessdata_contrib).
Open an issue there first. Publish the model together with the fonts list (`work/fonts.json`),
the settings (`work/config.json`), both evaluation reports (rendered lines and real scans), and the
license of every font and text source. A model should beat the stock one on real scans before
it is proposed. Leave out fonts with a non-commercial licence (the C-DAC GIST set) unless their
owner agrees.

## Tests

```bash
python3 -m unittest discover tests
```

## Licence

The code and the tam_v2 and V1 models are licensed under the [Apache License 2.0](LICENSE), like
Tesseract and its `tam` model. The V2-research model files are licensed for non-commercial use
only, under [CC BY-NC 4.0](models/tam_v2_research/LICENSE.md). Text from Tamil Wikisource, in the release's training text, word
list and line list, is CC BY-SA 4.0 by the Wikisource contributors. Fonts, scanned images and
third-party benchmarks are not redistributed. See [NOTICE](NOTICE).
