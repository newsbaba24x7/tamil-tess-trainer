# Licence of the tam_v2_research model files

`tam_v2_research.traineddata` and `tam_v2_research_fast.traineddata` are licensed under the
**Creative Commons Attribution-NonCommercial 4.0 International licence (CC BY-NC 4.0)**:
https://creativecommons.org/licenses/by-nc/4.0/

You may use, share and adapt them for **non-commercial purposes**, with attribution to the
tamil-tess-trainer project (https://github.com/newsbaba24x7/tamil-tess-trainer).

**Why non-commercial.** The model was trained on text images rendered with 45 styles of the
C-DAC GIST Tamil fonts, whose licence reads: "Copyright (c) 2005, C-DAC, GIST PUNE, INDIA. FOR
NON-COMMERCIAL FREE USAGE. For commercial license contact C-DAC, GIST, Pune." Its training fonts
also include Latha (proprietary, Microsoft) and uniAmma-10, -11 and -16 (origin unknown). The
fonts themselves are not distributed.

For commercial use, use **tam_v2** instead. It is trained only on openly licensed fonts and is
licensed under Apache-2.0 ([MODEL_CARD.md](../../MODEL_CARD.md)).

The model is fine-tuned from Tesseract's `tam` model (tessdata_best, Copyright Google, Apache
License 2.0). The Apache-2.0 licence and notice for that part are in [LICENSE](../../LICENSE) and
[NOTICE](../../NOTICE).
