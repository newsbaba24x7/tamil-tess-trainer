# Evaluation report

2309 held-out line images, `--psm 7`. CER = character error rate, WER = word error rate (lower is better).

The stock `tam` model writes an invisible U+200C (zero-width non-joiner) after many pullis (்), learned from its training text. CER and WER ignore invisible characters so models are compared on visible text; 'raw CER' counts them.
1 line image(s) made tesseract itself crash (a tesseract bug on some faint images) and are left out for every model.

| Model | CER | WER | raw CER |
|---|---:|---:|---:|
| start (tam, best) | 6.12% | 21.69% | 11.41% |
| installed tam | 5.95% | 20.97% | 11.32% |
| V2-research (best) | 2.51% | 8.78% | 2.51% |
| V2-research (fast) | 2.52% | 8.82% | 2.52% |
| V1 (188 styles) | 2.55% | 9.47% | 2.55% |

## Pre-1978 letter shapes

Lines drawn with the old shapes of ணா றா னா / ணை லை ளை னை (fonts that draw them by default, or with the OpenType feature turned on) and all other lines.

| Model | Old shapes CER | Modern shapes CER |
|---|---:|---:|
| start (tam, best) | 3.23% (413 lines) | 6.79% |
| installed tam | 3.06% (413 lines) | 6.61% |
| V2-research (best) | 1.38% (413 lines) | 2.77% |
| V2-research (fast) | 1.39% (413 lines) | 2.77% |
| V1 (188 styles) | 1.65% (413 lines) | 2.76% |

## CER per font

| Font | Lines | start (tam, best) | installed tam | V2-research (best) | V2-research (fast) | V1 (188 styles) |
|---|---:|---:|---:|---:|---:|---:|
| Aaram Regular | 7 | 16.14% | 14.8% | 1.35% | 1.35% | 1.79% |
| AkrutiTml1 Bold | 7 | 2.87% | 1.64% | 2.05% | 2.46% | 0.41% |
| AkrutiTml1 Normal | 7 | 1.84% | 1.84% | 1.84% | 2.3% | 1.38% |
| AkrutiTml2 Bold | 7 | 6.14% | 5.26% | 4.82% | 4.39% | 3.51% |
| AkrutiTml2 Normal | 7 | 1.05% | 1.05% | 1.05% | 1.05% | 1.05% |
| Anek Tamil Bold | 7 | 2.38% | 3.57% | 0.4% | 0.4% | 0.79% |
| Anek Tamil Bold (old letters) | 7 | 2.67% | 3.56% | 0.44% | 0.89% | 0.89% |
| Anek Tamil Condensed Bold | 7 | 6.02% | 5.56% | 0.0% | 0.0% | 0.46% |
| Anek Tamil Condensed Bold (old letters) | 7 | 22.06% | 8.09% | 5.15% | 3.68% | 6.62% |
| Anek Tamil Condensed Regular | 7 | 7.96% | 6.19% | 1.77% | 1.77% | 1.77% |
| Anek Tamil Condensed Regular (old letters) | 7 | 13.4% | 12.89% | 0.52% | 0.52% | 1.03% |
| Anek Tamil ExtraBold | 7 | 2.46% | 1.97% | 0.49% | 0.49% | 0.49% |
| Anek Tamil ExtraBold (old letters) | 7 | 2.4% | 2.4% | 0.0% | 0.0% | 0.0% |
| Anek Tamil ExtraLight | 7 | 1.09% | 2.72% | 0.0% | 0.0% | 0.0% |
| Anek Tamil ExtraLight (old letters) | 7 | 1.62% | 4.05% | 0.81% | 1.62% | 0.4% |
| Anek Tamil Light | 7 | 2.13% | 2.66% | 1.6% | 1.06% | 0.53% |
| Anek Tamil Light (old letters) | 7 | 0.58% | 2.92% | 0.0% | 0.0% | 0.0% |
| Anek Tamil Medium | 7 | 0.0% | 0.45% | 0.0% | 0.0% | 0.0% |
| Anek Tamil Medium (old letters) | 7 | 1.62% | 2.16% | 0.0% | 0.0% | 1.62% |
| Anek Tamil Regular | 7 | 5.86% | 4.95% | 0.45% | 0.45% | 0.45% |
| Anek Tamil Regular (old letters) | 7 | 2.96% | 1.48% | 0.0% | 0.0% | 0.99% |
| Anek Tamil SemiBold | 7 | 2.75% | 2.75% | 0.0% | 0.0% | 0.46% |
| Anek Tamil SemiBold (old letters) | 7 | 2.96% | 2.46% | 0.99% | 0.99% | 0.99% |
| Anek Tamil SemiCondensed Bold | 7 | 4.7% | 5.13% | 0.0% | 0.0% | 0.0% |
| Anek Tamil SemiCondensed Bold (old letters) | 7 | 7.84% | 8.24% | 1.18% | 1.18% | 2.35% |
| Anek Tamil SemiCondensed Regular | 7 | 4.21% | 7.72% | 1.75% | 2.11% | 0.35% |
| Anek Tamil SemiCondensed Regular (old letters) | 7 | 8.53% | 12.32% | 0.47% | 0.47% | 0.47% |
| Anek Tamil Thin | 7 | 24.77% | 23.87% | 22.52% | 21.62% | 21.62% |
| Anek Tamil Thin (old letters) | 7 | 2.41% | 9.04% | 1.81% | 1.81% | 3.61% |
| Arima Bold | 7 | 1.27% | 0.85% | 0.0% | 0.0% | 0.42% |
| Arima Bold (old letters) | 7 | 0.33% | 0.99% | 0.33% | 0.33% | 0.0% |
| Arima ExtraLight | 7 | 16.15% | 14.78% | 15.81% | 15.46% | 15.12% |
| Arima ExtraLight (old letters) | 7 | 1.92% | 0.77% | 0.77% | 0.77% | 0.0% |
| Arima Light | 7 | 0.4% | 0.79% | 0.4% | 0.4% | 0.4% |
| Arima Light (old letters) | 7 | 0.0% | 0.41% | 0.0% | 0.0% | 0.0% |
| Arima Medium | 7 | 4.26% | 5.85% | 1.06% | 1.06% | 0.53% |
| Arima Medium (old letters) | 7 | 2.25% | 1.35% | 0.0% | 0.0% | 2.25% |
| Arima Regular | 7 | 0.0% | 0.0% | 0.47% | 0.47% | 0.0% |
| Arima Regular (old letters) | 7 | 1.28% | 1.7% | 0.43% | 0.43% | 0.85% |
| Arima SemiBold | 7 | 0.0% | 0.0% | 0.48% | 0.48% | 0.0% |
| Arima SemiBold (old letters) | 7 | 3.94% | 3.54% | 2.76% | 2.76% | 2.76% |
| Arima Thin | 6 | 1.83% | 1.83% | 0.61% | 0.61% | 1.22% |
| Arima Thin (old letters) | 7 | 19.19% | 18.86% | 17.85% | 17.85% | 17.85% |
| Auvaiyar Bold | 7 | 2.86% | 0.82% | 1.22% | 1.22% | 0.82% |
| Auvaiyar Bold Italic | 7 | 6.99% | 11.89% | 0.7% | 0.7% | 0.7% |
| Auvaiyar Italic | 7 | 6.22% | 8.61% | 2.39% | 1.91% | 0.0% |
| Auvaiyar Regular | 7 | 2.84% | 0.0% | 0.0% | 0.47% | 0.47% |
| Baloo Thambi 2 Bold | 7 | 0.42% | 0.83% | 0.42% | 0.83% | 0.0% |
| Baloo Thambi 2 ExtraBold | 7 | 0.0% | 2.21% | 0.0% | 0.0% | 0.0% |
| Baloo Thambi 2 Medium | 7 | 0.0% | 1.83% | 0.0% | 0.0% | 0.46% |
| Baloo Thambi 2 Regular | 7 | 0.0% | 2.6% | 0.0% | 0.0% | 0.0% |
| Baloo Thambi 2 SemiBold | 7 | 0.8% | 2.4% | 0.8% | 0.8% | 1.2% |
| Catamaran Black | 7 | 2.08% | 3.33% | 0.0% | 2.5% | 1.25% |
| Catamaran Black (old letters) | 7 | 2.11% | 0.42% | 0.0% | 0.0% | 1.69% |
| Catamaran Bold | 7 | 1.14% | 1.14% | 0.0% | 0.0% | 0.0% |
| Catamaran Bold (old letters) | 7 | 0.97% | 0.97% | 0.0% | 0.0% | 0.49% |
| Catamaran ExtraBold | 7 | 0.87% | 1.74% | 0.43% | 0.43% | 0.0% |
| Catamaran ExtraBold (old letters) | 7 | 1.97% | 2.76% | 0.0% | 0.0% | 1.18% |
| Catamaran ExtraLight | 7 | 2.63% | 2.63% | 0.53% | 0.53% | 0.0% |
| Catamaran ExtraLight (old letters) | 7 | 1.88% | 1.5% | 1.5% | 1.5% | 1.5% |
| Catamaran Light | 7 | 4.66% | 2.12% | 1.27% | 1.27% | 1.27% |
| Catamaran Light (old letters) | 7 | 2.45% | 4.9% | 0.98% | 0.98% | 2.45% |
| Catamaran Medium | 7 | 0.51% | 0.51% | 0.0% | 0.0% | 0.0% |
| Catamaran Medium (old letters) | 7 | 1.3% | 0.43% | 0.0% | 0.0% | 0.0% |
| Catamaran Regular | 7 | 1.61% | 1.61% | 0.0% | 0.0% | 0.81% |
| Catamaran Regular (old letters) | 7 | 1.4% | 1.4% | 0.0% | 0.0% | 1.4% |
| Catamaran SemiBold | 7 | 1.52% | 1.02% | 0.51% | 0.51% | 1.02% |
| Catamaran SemiBold (old letters) | 7 | 0.88% | 0.0% | 0.44% | 0.44% | 3.1% |
| Catamaran Thin | 7 | 17.31% | 17.95% | 17.31% | 17.31% | 17.95% |
| Catamaran Thin (old letters) | 7 | 0.42% | 0.42% | 0.0% | 0.0% | 0.0% |
| Chemmozhi Comic | 7 | 1.3% | 3.03% | 0.87% | 0.43% | 0.87% |
| Chemmozhi Paranar | 7 | 1.65% | 1.1% | 0.55% | 0.55% | 1.1% |
| Chemmozhi Thendral | 7 | 0.0% | 0.42% | 0.0% | 0.0% | 0.0% |
| Chemmozhi Thenee | 7 | 0.76% | 0.76% | 0.76% | 0.76% | 0.38% |
| Chemmozhi Times | 7 | 3.0% | 1.72% | 0.86% | 0.86% | 0.43% |
| Chemmozhi Vaigai | 7 | 0.49% | 0.49% | 0.99% | 0.99% | 0.49% |
| Coiny Regular | 7 | 5.39% | 5.81% | 2.9% | 3.73% | 2.9% |
| Droid Sans Tamil | 7 | 1.14% | 1.14% | 0.0% | 0.0% | 0.57% |
| Droid Sans Tamil Bold | 7 | 0.44% | 0.0% | 1.33% | 1.33% | 0.0% |
| GIST-TMOTAbhirami Bold | 7 | 20.57% | 20.57% | 1.71% | 1.14% | 2.86% |
| GIST-TMOTAbhirami BoldItalic | 7 | 59.15% | 57.75% | 16.9% | 17.84% | 17.37% |
| GIST-TMOTAmala Bold | 7 | 5.71% | 3.81% | 1.43% | 1.43% | 0.48% |
| GIST-TMOTAmala BoldItalic | 7 | 15.22% | 20.11% | 0.54% | 0.54% | 1.09% |
| GIST-TMOTAppar Bold | 7 | 3.72% | 2.13% | 0.0% | 0.53% | 0.53% |
| GIST-TMOTAppar BoldItalic | 7 | 12.64% | 13.19% | 0.55% | 0.55% | 0.0% |
| GIST-TMOTChanakya Bold | 7 | 0.51% | 0.0% | 0.51% | 0.51% | 0.51% |
| GIST-TMOTChanakya BoldItalic | 7 | 0.5% | 0.0% | 0.5% | 0.5% | 1.0% |
| GIST-TMOTChanakya Italic | 7 | 0.52% | 0.0% | 0.52% | 0.52% | 0.0% |
| GIST-TMOTChanakya Normal | 7 | 1.42% | 0.47% | 0.47% | 0.47% | 0.47% |
| GIST-TMOTChandra Bold | 7 | 1.29% | 2.15% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTChandra BoldItalic | 7 | 4.21% | 4.21% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTHeena Bold | 7 | 3.43% | 2.94% | 1.47% | 0.98% | 1.47% |
| GIST-TMOTHeena BoldItalic | 7 | 3.6% | 5.86% | 0.9% | 0.9% | 0.0% |
| GIST-TMOTKalyani Bold | 7 | 15.52% | 10.34% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTKalyani BoldItalic | 7 | 26.34% | 28.12% | 2.23% | 2.23% | 6.25% |
| GIST-TMOTKamal Bold | 7 | 0.45% | 0.0% | 0.45% | 0.45% | 0.45% |
| GIST-TMOTKamal BoldItalic | 7 | 4.69% | 3.76% | 0.94% | 0.94% | 3.29% |
| GIST-TMOTKamal Italic | 7 | 6.45% | 1.08% | 1.61% | 1.08% | 2.15% |
| GIST-TMOTKamal Normal | 7 | 0.39% | 0.78% | 0.39% | 0.39% | 0.0% |
| GIST-TMOTKannadasan Italic | 7 | 8.68% | 9.59% | 1.83% | 1.37% | 1.83% |
| GIST-TMOTKannadasan Normal | 7 | 4.13% | 0.46% | 0.46% | 0.46% | 0.92% |
| GIST-TMOTKannagi Bold | 7 | 3.64% | 3.18% | 0.0% | 0.0% | 0.91% |
| GIST-TMOTKannagi BoldItalic | 7 | 16.0% | 8.89% | 2.22% | 1.78% | 2.67% |
| GIST-TMOTKomala Bold | 7 | 0.45% | 0.45% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTKomala BoldItalic | 7 | 1.98% | 2.97% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTKrishnan Bold | 7 | 19.87% | 15.38% | 14.1% | 14.1% | 14.74% |
| GIST-TMOTKumudam Normal | 7 | 17.2% | 26.75% | 8.92% | 8.92% | 8.28% |
| GIST-TMOTLalitha Bold | 7 | 1.99% | 0.5% | 0.5% | 0.5% | 1.49% |
| GIST-TMOTLalitha BoldItalic | 7 | 4.18% | 5.44% | 1.67% | 2.09% | 2.51% |
| GIST-TMOTLalitha Italic | 7 | 1.98% | 3.57% | 0.4% | 0.0% | 1.19% |
| GIST-TMOTLalitha Normal | 7 | 3.72% | 2.89% | 0.83% | 0.83% | 2.48% |
| GIST-TMOTMadhura Bold | 7 | 93.27% | 91.35% | 90.87% | 88.46% | 101.44% |
| GIST-TMOTMina Bold | 7 | 7.89% | 8.55% | 1.97% | 3.29% | 5.26% |
| GIST-TMOTNambi Bold | 7 | 1.92% | 0.96% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTNambi BoldItalic | 7 | 6.57% | 5.05% | 2.53% | 2.02% | 2.53% |
| GIST-TMOTNambi Italic | 7 | 2.36% | 1.01% | 0.0% | 0.34% | 0.0% |
| GIST-TMOTNambi Normal | 7 | 2.94% | 2.94% | 1.47% | 1.47% | 1.47% |
| GIST-TMOTPadma Bold | 7 | 0.6% | 0.6% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTPadma Normal | 7 | 6.5% | 1.0% | 0.5% | 0.5% | 0.5% |
| GIST-TMOTParvathi BoldItalic | 7 | 31.11% | 29.33% | 22.22% | 22.67% | 23.11% |
| GIST-TMOTPattinathar Bold | 7 | 3.37% | 6.18% | 0.56% | 0.56% | 1.12% |
| GIST-TMOTPattinathar BoldItalic | 7 | 2.23% | 4.02% | 0.0% | 0.0% | 0.0% |
| GIST-TMOTPattinathar Italic | 7 | 16.98% | 21.23% | 16.04% | 16.04% | 15.57% |
| GIST-TMOTPattinathar Normal | 7 | 5.26% | 3.38% | 0.75% | 0.75% | 1.5% |
| Google Sans Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Google Sans Bold Italic | 7 | 0.9% | 0.9% | 0.0% | 0.0% | 0.0% |
| Google Sans Italic | 7 | 0.44% | 0.44% | 0.44% | 0.44% | 0.87% |
| Google Sans Medium | 7 | 1.11% | 0.0% | 1.11% | 1.11% | 2.78% |
| Google Sans Medium Italic | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.52% |
| Google Sans Regular | 7 | 0.0% | 1.12% | 0.37% | 0.37% | 0.0% |
| Hind Madurai Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.6% |
| Hind Madurai Bold (old letters) | 7 | 1.32% | 0.66% | 0.0% | 0.0% | 0.0% |
| Hind Madurai Light | 7 | 0.5% | 0.0% | 0.5% | 0.5% | 0.0% |
| Hind Madurai Light (old letters) | 7 | 2.81% | 2.25% | 0.0% | 0.0% | 1.69% |
| Hind Madurai Medium | 7 | 0.0% | 1.09% | 0.0% | 0.0% | 0.0% |
| Hind Madurai Medium (old letters) | 7 | 2.14% | 0.0% | 0.43% | 0.43% | 0.43% |
| Hind Madurai Regular | 7 | 0.46% | 0.0% | 0.0% | 0.0% | 0.0% |
| Hind Madurai Regular (old letters) | 7 | 1.53% | 0.51% | 0.0% | 0.0% | 0.0% |
| Hind Madurai SemiBold | 7 | 0.0% | 0.67% | 0.0% | 0.0% | 0.0% |
| Hind Madurai SemiBold (old letters) | 7 | 1.62% | 1.21% | 0.81% | 0.81% | 1.21% |
| Karla Tamil Inclined | 7 | 0.8% | 0.8% | 1.2% | 1.2% | 1.2% |
| Karla Tamil Inclined Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Karla Tamil Upright | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Karla Tamil Upright Bold | 7 | 0.0% | 0.0% | 0.38% | 0.38% | 0.0% |
| Kavivanar Regular | 7 | 0.79% | 0.79% | 0.4% | 0.4% | 0.79% |
| Latha | 7 | 1.0% | 1.0% | 0.0% | 0.0% | 0.5% |
| Lohit Tamil | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Lohit Tamil Classical | 7 | 0.0% | 1.82% | 0.0% | 0.0% | 0.0% |
| Madurai Bold | 7 | 17.62% | 13.33% | 0.48% | 0.48% | 0.95% |
| Madurai Regular | 7 | 44.33% | 24.14% | 3.94% | 3.45% | 1.48% |
| Madurai Thin | 7 | 36.84% | 22.11% | 3.16% | 3.16% | 1.58% |
| Meera Inimai Regular | 7 | 0.0% | 0.0% | 0.49% | 0.49% | 0.49% |
| Mukta Malar Bold | 7 | 0.5% | 0.5% | 0.0% | 0.0% | 0.0% |
| Mukta Malar Bold (old letters) | 7 | 0.64% | 0.0% | 0.0% | 0.0% | 0.0% |
| Mukta Malar ExtraBold | 7 | 0.0% | 0.48% | 0.48% | 0.0% | 0.0% |
| Mukta Malar ExtraBold (old letters) | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Mukta Malar ExtraLight | 7 | 8.42% | 8.42% | 7.43% | 7.43% | 7.92% |
| Mukta Malar ExtraLight (old letters) | 7 | 0.85% | 0.43% | 0.43% | 0.43% | 0.43% |
| Mukta Malar Light | 7 | 1.33% | 0.44% | 0.0% | 0.0% | 0.0% |
| Mukta Malar Light (old letters) | 7 | 1.95% | 1.95% | 1.95% | 1.95% | 1.46% |
| Mukta Malar Medium | 7 | 0.35% | 0.35% | 0.35% | 0.35% | 0.35% |
| Mukta Malar Medium (old letters) | 7 | 0.0% | 0.0% | 0.49% | 0.49% | 0.0% |
| Mukta Malar Regular | 7 | 1.46% | 0.98% | 0.49% | 0.49% | 0.49% |
| Mukta Malar Regular (old letters) | 7 | 0.0% | 0.79% | 0.4% | 0.4% | 0.0% |
| Mukta Malar SemiBold | 7 | 0.52% | 1.57% | 1.05% | 1.05% | 1.05% |
| Mukta Malar SemiBold (old letters) | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Neythal Regular | 7 | 8.44% | 2.67% | 0.0% | 0.0% | 0.44% |
| Noto Sans Tamil Black | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.49% |
| Noto Sans Tamil Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil Condensed Bold | 7 | 0.0% | 0.0% | 0.51% | 0.51% | 0.51% |
| Noto Sans Tamil Condensed Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil ExtraBold | 7 | 8.5% | 8.5% | 8.5% | 8.5% | 8.5% |
| Noto Sans Tamil ExtraCondensed Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil ExtraCondensed Regular | 7 | 2.75% | 3.85% | 0.55% | 0.55% | 0.55% |
| Noto Sans Tamil ExtraLight | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.43% |
| Noto Sans Tamil Light | 7 | 0.0% | 0.0% | 0.61% | 0.61% | 0.61% |
| Noto Sans Tamil Medium | 7 | 1.01% | 0.5% | 1.01% | 1.01% | 1.01% |
| Noto Sans Tamil Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil SemiBold | 7 | 0.47% | 0.47% | 0.93% | 0.93% | 1.4% |
| Noto Sans Tamil SemiCondensed Bold | 7 | 0.56% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil SemiCondensed Regular | 7 | 0.93% | 0.93% | 0.93% | 0.93% | 0.0% |
| Noto Sans Tamil Thin | 7 | 23.08% | 22.62% | 23.98% | 23.53% | 24.43% |
| Noto Serif Tamil Black | 7 | 0.0% | 0.6% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Black Italic | 7 | 3.0% | 0.43% | 0.43% | 0.86% | 0.43% |
| Noto Serif Tamil Bold | 7 | 0.37% | 0.37% | 0.0% | 0.0% | 0.37% |
| Noto Serif Tamil Bold Italic | 7 | 1.58% | 1.05% | 1.05% | 1.05% | 2.11% |
| Noto Serif Tamil Condensed Bold | 7 | 1.03% | 0.68% | 0.34% | 0.34% | 0.34% |
| Noto Serif Tamil Condensed Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.51% |
| Noto Serif Tamil ExtraBold | 7 | 2.14% | 0.0% | 0.43% | 0.43% | 0.85% |
| Noto Serif Tamil ExtraBold Italic | 7 | 1.81% | 1.45% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil ExtraCondensed Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil ExtraCondensed Regular | 7 | 0.68% | 0.34% | 0.34% | 0.34% | 0.68% |
| Noto Serif Tamil ExtraLight | 7 | 0.39% | 0.78% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil ExtraLight Italic | 7 | 53.5% | 53.5% | 53.5% | 53.5% | 54.0% |
| Noto Serif Tamil Italic | 7 | 1.49% | 1.49% | 0.5% | 0.5% | 0.5% |
| Noto Serif Tamil Light | 7 | 16.86% | 16.48% | 16.86% | 16.86% | 16.48% |
| Noto Serif Tamil Light Italic | 7 | 2.6% | 1.12% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Medium | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Medium Italic | 7 | 7.37% | 6.84% | 6.84% | 6.84% | 6.32% |
| Noto Serif Tamil Regular | 7 | 0.39% | 0.0% | 0.0% | 0.0% | 0.39% |
| Noto Serif Tamil SemiBold | 7 | 0.47% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil SemiBold Italic | 7 | 1.92% | 1.44% | 0.48% | 0.48% | 0.48% |
| Noto Serif Tamil SemiCondensed Bold | 7 | 0.0% | 0.47% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil SemiCondensed Regular | 7 | 2.91% | 2.18% | 2.18% | 2.18% | 2.18% |
| Noto Serif Tamil Slanted Bold | 7 | 25.38% | 26.14% | 25.0% | 25.0% | 25.0% |
| Noto Serif Tamil Slanted Regular | 7 | 2.69% | 4.3% | 2.69% | 3.23% | 3.23% |
| Noto Serif Tamil Thin | 7 | 13.04% | 13.04% | 11.18% | 11.18% | 11.8% |
| Noto Serif Tamil Thin Italic | 7 | 3.33% | 1.11% | 0.56% | 0.0% | 0.0% |
| Oi Regular | 7 | 36.36% | 38.76% | 9.09% | 10.53% | 8.61% |
| Pavanam Regular | 7 | 0.0% | 1.0% | 0.0% | 0.0% | 0.0% |
| PostNoBillsJaffna Bold | 7 | 2.22% | 1.67% | 0.56% | 1.67% | 0.0% |
| PostNoBillsJaffna Bold (old letters) | 7 | 2.14% | 2.67% | 1.6% | 1.6% | 1.07% |
| PostNoBillsJaffna ExtraBold | 7 | 2.41% | 2.41% | 3.61% | 3.61% | 4.22% |
| PostNoBillsJaffna ExtraBold (old letters) | 7 | 2.97% | 1.27% | 0.42% | 0.42% | 0.0% |
| PostNoBillsJaffna Light | 7 | 6.5% | 5.78% | 1.81% | 1.44% | 1.44% |
| PostNoBillsJaffna Light (old letters) | 7 | 24.37% | 24.37% | 22.27% | 21.85% | 21.85% |
| PostNoBillsJaffna Medium | 7 | 4.44% | 5.56% | 1.11% | 1.11% | 2.22% |
| PostNoBillsJaffna Medium (old letters) | 7 | 4.78% | 1.44% | 0.96% | 0.96% | 0.48% |
| PostNoBillsJaffna Regular | 7 | 7.6% | 5.85% | 2.92% | 2.92% | 3.51% |
| PostNoBillsJaffna Regular (old letters) | 7 | 2.86% | 2.86% | 0.0% | 0.95% | 0.48% |
| PostNoBillsJaffna SemiBold | 7 | 3.72% | 2.07% | 0.0% | 0.0% | 0.0% |
| PostNoBillsJaffna SemiBold (old letters) | 7 | 4.08% | 5.1% | 3.06% | 3.06% | 2.55% |
| Samyak Tamil | 7 | 1.75% | 2.92% | 0.0% | 0.0% | 0.58% |
| TABUni-Tamil021 | 7 | 17.04% | 21.52% | 2.69% | 2.24% | 2.24% |
| TABUni-Tamil032 | 7 | 4.06% | 4.06% | 0.51% | 0.51% | 0.0% |
| TAMUni-Tamil042 | 7 | 28.11% | 35.48% | 5.99% | 6.45% | 4.61% |
| TAMUni-Tamil046 | 7 | 10.0% | 9.05% | 4.76% | 4.76% | 3.81% |
| TAMUni-Tamil150 | 7 | 41.41% | 39.9% | 16.67% | 16.67% | 11.11% |
| TAMUni-Tamil195 | 7 | 43.16% | 48.29% | 20.51% | 19.23% | 12.82% |
| TAMu_Kadambri Regular | 7 | 1.6% | 1.6% | 2.67% | 2.67% | 2.67% |
| TAMu_Kalyani | 7 | 0.98% | 0.98% | 0.49% | 0.49% | 0.98% |
| TAMu_Maduram | 7 | 1.43% | 1.43% | 0.0% | 0.0% | 0.0% |
| TAU-Achu | 7 | 6.63% | 2.76% | 0.0% | 0.0% | 0.0% |
| TAU-Achu Italic | 7 | 18.18% | 19.79% | 3.21% | 3.21% | 1.07% |
| TAU-Barathi | 7 | 0.73% | 0.73% | 0.36% | 0.36% | 0.36% |
| TAU-Barathi Bold | 7 | 0.0% | 1.08% | 0.0% | 0.0% | 0.0% |
| TAU-Barathi BoldItalic | 7 | 0.85% | 2.97% | 0.42% | 0.42% | 0.85% |
| TAU-Barathi Italic | 7 | 8.51% | 12.77% | 2.84% | 2.84% | 4.96% |
| TAU-Ezhil | 7 | 8.2% | 9.43% | 1.64% | 1.64% | 1.64% |
| TAU-Ezhil Bold | 7 | 7.55% | 7.08% | 1.89% | 2.36% | 2.36% |
| TAU-Ezhil Italic | 7 | 5.81% | 6.4% | 1.16% | 1.16% | 1.74% |
| TAU-Kabilar | 7 | 0.0% | 1.18% | 0.0% | 0.0% | 0.0% |
| TAU-Kabilar Bold | 7 | 3.04% | 2.17% | 0.0% | 0.0% | 0.0% |
| TAU-Kabilar BoldItalic | 7 | 9.71% | 4.85% | 0.97% | 0.97% | 0.49% |
| TAU-Kabilar Italic | 7 | 2.55% | 1.27% | 1.91% | 1.91% | 1.27% |
| TAU-Kambar | 7 | 12.46% | 10.03% | 3.81% | 4.15% | 2.08% |
| TAU-Kambar Bold | 7 | 15.08% | 15.64% | 9.5% | 9.5% | 8.94% |
| TAU-Kambar BoldItalic | 7 | 14.85% | 12.38% | 3.47% | 3.47% | 4.46% |
| TAU-Kambar Italic | 7 | 12.43% | 31.95% | 4.73% | 4.73% | 3.55% |
| TAU-Kaveri | 7 | 5.58% | 4.57% | 4.57% | 5.08% | 2.54% |
| TAU-Kaveri Bold | 7 | 3.48% | 5.47% | 1.99% | 1.99% | 2.49% |
| TAU-Kaveri BoldItalic | 7 | 7.51% | 6.72% | 3.16% | 2.77% | 3.16% |
| TAU-Kaveri Italic | 7 | 6.91% | 8.13% | 1.22% | 2.03% | 2.03% |
| TAU-Kurinji | 7 | 2.75% | 1.65% | 1.1% | 2.2% | 1.1% |
| TAU-Kurinji Bold | 7 | 2.79% | 1.4% | 0.0% | 0.0% | 0.0% |
| TAU-Kurinji Italic | 7 | 7.63% | 6.43% | 0.8% | 0.4% | 1.2% |
| TAU-Malar | 7 | 4.03% | 3.23% | 1.61% | 0.81% | 1.61% |
| TAU-Malar Bold | 7 | 5.64% | 2.05% | 1.03% | 1.03% | 1.03% |
| TAU-Malar Italic | 7 | 17.39% | 15.65% | 0.87% | 0.87% | 0.87% |
| TAU-Marutham | 7 | 0.0% | 0.63% | 1.27% | 1.27% | 0.0% |
| TAU-Marutham Bold | 7 | 1.05% | 0.53% | 1.58% | 1.58% | 1.05% |
| TAU-Marutham Italic | 7 | 15.32% | 14.89% | 12.34% | 12.34% | 12.34% |
| TAU-Mullai | 7 | 0.63% | 0.0% | 0.0% | 0.0% | 0.0% |
| TAU-Mullai Bold | 7 | 3.37% | 1.12% | 1.69% | 1.69% | 1.69% |
| TAU-Mullai Italic | 7 | 5.7% | 10.88% | 0.0% | 0.0% | 1.55% |
| TAU-Neythal | 7 | 18.78% | 20.66% | 0.94% | 0.94% | 2.35% |
| TAU-Neythal Bold | 7 | 7.65% | 10.93% | 0.55% | 0.55% | 1.09% |
| TAU-Neythal Italic | 7 | 33.03% | 51.58% | 2.26% | 2.71% | 2.26% |
| TAU-Nilavu | 7 | 13.0% | 4.0% | 1.0% | 1.0% | 0.5% |
| TAU-Nilavu Bold | 7 | 10.8% | 6.25% | 1.7% | 2.27% | 1.14% |
| TAU-Nilavu Italic | 7 | 25.62% | 28.1% | 1.24% | 1.65% | 0.83% |
| TAU-Paalai Bold | 7 | 1.88% | 0.0% | 0.0% | 0.62% | 0.0% |
| TAU-Paalai Italic | 7 | 2.44% | 2.93% | 0.49% | 0.49% | 0.49% |
| TAU-Urai Bold | 7 | 1.74% | 1.16% | 0.0% | 0.0% | 0.0% |
| TAU-Urai Italic | 7 | 12.9% | 11.52% | 3.69% | 4.15% | 2.3% |
| TAU-Valluvar | 7 | 0.0% | 1.9% | 0.47% | 0.47% | 0.0% |
| TAU-Valluvar Bold | 7 | 2.06% | 0.52% | 1.03% | 1.03% | 0.52% |
| TAU-Valluvar BoldItalic | 7 | 5.68% | 10.8% | 1.7% | 1.7% | 1.14% |
| TAU-Valluvar Italic | 7 | 3.62% | 2.26% | 0.0% | 0.0% | 0.9% |
| TAU-kaviri | 7 | 10.33% | 7.07% | 4.89% | 4.35% | 3.8% |
| TAU-kollidam | 7 | 13.03% | 7.66% | 2.68% | 2.68% | 1.92% |
| TAU-palar | 7 | 11.88% | 12.26% | 1.92% | 1.53% | 2.3% |
| TAU-ponni | 7 | 2.43% | 5.83% | 1.46% | 1.46% | 1.46% |
| TAU-porunai | 7 | 4.86% | 4.86% | 2.16% | 2.16% | 2.16% |
| TAU-pothigai | 7 | 9.47% | 8.28% | 8.28% | 8.28% | 10.06% |
| TAU-thamirabarani | 7 | 0.58% | 1.16% | 1.16% | 0.58% | 0.0% |
| TSCu_Times | 7 | 3.54% | 3.98% | 1.77% | 1.77% | 1.33% |
| ThiruValluvar Bold | 7 | 2.44% | 4.39% | 1.95% | 1.46% | 0.49% |
| ThiruValluvar Bold Italic | 7 | 4.27% | 3.42% | 0.43% | 0.43% | 1.28% |
| ThiruValluvar Italic | 7 | 3.82% | 3.05% | 1.53% | 1.53% | 1.91% |
| ThiruValluvar Regular | 7 | 2.72% | 0.54% | 0.0% | 0.0% | 0.0% |
| Tiro Tamil Italic | 7 | 1.98% | 0.0% | 0.0% | 0.0% | 0.0% |
| Tiro Tamil Italic (old letters) | 7 | 6.09% | 10.15% | 0.51% | 0.51% | 1.02% |
| Tiro Tamil Regular | 7 | 0.0% | 0.5% | 0.0% | 0.0% | 0.0% |
| Tiro Tamil Regular (old letters) | 7 | 0.93% | 0.47% | 0.47% | 0.0% | 0.0% |
| Uni Ila.Sundaram-01 | 7 | 1.99% | 2.49% | 1.0% | 1.0% | 1.49% |
| Uni Ila.Sundaram-02 | 7 | 3.12% | 6.77% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-03 | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-04 | 7 | 0.88% | 0.0% | 0.44% | 0.44% | 0.44% |
| Uni Ila.Sundaram-05 | 7 | 9.04% | 4.52% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-06 | 7 | 19.27% | 11.47% | 2.29% | 2.29% | 4.13% |
| Uni Ila.Sundaram-07 | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-08 | 7 | 8.15% | 6.01% | 3.0% | 3.43% | 2.15% |
| Uni Ila.Sundaram-09 | 7 | 25.66% | 31.7% | 8.68% | 7.55% | 8.68% |
| Uni Ila.Sundaram-10 | 7 | 2.8% | 3.27% | 1.4% | 1.4% | 2.8% |
| Uni Ila.Sundaram-11 | 7 | 0.45% | 0.45% | 0.9% | 0.9% | 0.9% |
| Uni Ila.Sundaram-12 | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-13 | 7 | 5.99% | 1.8% | 0.6% | 0.0% | 1.8% |
| Uni Ila.Sundaram-14 | 7 | 2.37% | 1.78% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-15 | 7 | 14.41% | 13.1% | 2.62% | 2.62% | 1.31% |
| Uni Ila.Sundaram-16 | 7 | 34.81% | 25.97% | 5.52% | 4.97% | 2.76% |
| Uni Ila.Sundaram-17 | 7 | 20.93% | 18.6% | 18.02% | 18.02% | 13.95% |
| Uni Ila.Sundaram-18 | 7 | 16.53% | 19.35% | 3.63% | 3.63% | 4.03% |
| Uni Ila.Sundaram-19 | 7 | 12.38% | 13.81% | 7.62% | 7.62% | 8.1% |
| Uni Ila.Sundaram-20 | 7 | 17.09% | 17.09% | 5.7% | 5.06% | 5.7% |
| YaldeviJaffna Bold | 7 | 2.15% | 3.0% | 0.86% | 0.86% | 0.86% |
| YaldeviJaffna Bold (old letters) | 7 | 2.5% | 2.5% | 1.0% | 1.0% | 1.0% |
| YaldeviJaffna ExtraLight | 7 | 23.12% | 23.12% | 22.11% | 22.11% | 22.11% |
| YaldeviJaffna ExtraLight (old letters) | 7 | 3.98% | 2.65% | 0.44% | 0.44% | 0.44% |
| YaldeviJaffna Light | 7 | 3.99% | 1.45% | 1.45% | 1.45% | 0.72% |
| YaldeviJaffna Light (old letters) | 7 | 3.26% | 1.09% | 0.54% | 0.54% | 0.54% |
| YaldeviJaffna Medium | 7 | 2.81% | 2.25% | 0.0% | 0.0% | 0.0% |
| YaldeviJaffna Medium (old letters) | 7 | 4.31% | 1.29% | 0.0% | 0.0% | 0.0% |
| YaldeviJaffna Regular | 7 | 3.51% | 0.88% | 0.0% | 0.0% | 1.75% |
| YaldeviJaffna Regular (old letters) | 7 | 1.21% | 0.61% | 1.21% | 0.61% | 0.61% |
| YaldeviJaffna SemiBold | 7 | 1.48% | 2.46% | 0.0% | 0.0% | 0.0% |
| YaldeviJaffna SemiBold (old letters) | 7 | 4.24% | 3.18% | 0.71% | 1.06% | 2.12% |
| uniAmma-10 | 7 | 22.98% | 34.16% | 8.7% | 11.18% | 4.97% |
| uniAmma-11 | 7 | 12.36% | 10.67% | 1.12% | 1.12% | 1.69% |
| uniAmma-16 | 7 | 2.29% | 0.76% | 0.0% | 0.0% | 0.76% |

## Top confusions: start (tam, best)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 235 |
| ␠ | ∅ | 99 |
| ட | ∅ | 96 |
| ◌ு (U+0BC1) | ∅ | 89 |
| க | ∅ | 87 |
| ◌ி (U+0BBF) | ∅ | 82 |
| ப | ∅ | 70 |
| த | ∅ | 66 |
| ர | ∅ | 62 |
| ர | ற | 61 |
| ◌ே (U+0BC7) | ∅ | 57 |
| ◌ெ (U+0BC6) | ∅ | 55 |
| ம | ∅ | 55 |
| வ | ∅ | 50 |
| ◌ா (U+0BBE) | ∅ | 48 |

## Top confusions: installed tam

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 183 |
| ␠ | ∅ | 83 |
| க | ∅ | 78 |
| ◌ு (U+0BC1) | ∅ | 73 |
| ட | ∅ | 66 |
| ◌ி (U+0BBF) | ∅ | 62 |
| த | ∅ | 58 |
| ∅ | ␠ | 58 |
| ர | ∅ | 56 |
| வ | ∅ | 53 |
| ◌ா (U+0BBE) | ∅ | 46 |
| ◌ே (U+0BC7) | ∅ | 45 |
| ம | ∅ | 44 |
| ◌ு (U+0BC1) | ◌ூ (U+0BC2) | 42 |
| த | க | 38 |

## Top confusions: V2-research (best)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 183 |
| ␠ | ∅ | 94 |
| க | ∅ | 59 |
| ◌ி (U+0BBF) | ∅ | 52 |
| ◌ு (U+0BC1) | ∅ | 49 |
| த | ∅ | 46 |
| ர | ∅ | 40 |
| ∅ | ␠ | 37 |
| ம | ∅ | 35 |
| ◌ா (U+0BBE) | ∅ | 34 |
| வ | ∅ | 34 |
| ட | ∅ | 32 |
| ' | ∅ | 31 |
| ல | ∅ | 30 |
| ன | ∅ | 28 |

## Top confusions: V2-research (fast)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 184 |
| ␠ | ∅ | 94 |
| க | ∅ | 58 |
| ◌ி (U+0BBF) | ∅ | 52 |
| ◌ு (U+0BC1) | ∅ | 48 |
| த | ∅ | 45 |
| ர | ∅ | 42 |
| ∅ | ␠ | 38 |
| ◌ா (U+0BBE) | ∅ | 35 |
| ம | ∅ | 34 |
| வ | ∅ | 33 |
| ட | ∅ | 33 |
| ல | ∅ | 32 |
| ' | ∅ | 30 |
| . | ∅ | 30 |

## Top confusions: V1 (188 styles)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 174 |
| ␠ | ∅ | 88 |
| ∅ | ␠ | 79 |
| க | ∅ | 61 |
| ◌ி (U+0BBF) | ∅ | 48 |
| த | ∅ | 46 |
| ◌ு (U+0BC1) | ∅ | 45 |
| ர | ∅ | 37 |
| ◌ா (U+0BBE) | ∅ | 36 |
| வ | ∅ | 35 |
| ம | ∅ | 34 |
| ட | ∅ | 32 |
| ல | ∅ | 31 |
| ன | ∅ | 29 |
| ள | ∅ | 26 |
