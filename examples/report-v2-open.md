# Evaluation report

2051 held-out line images, `--psm 7`. CER = character error rate, WER = word error rate (lower is better).

The stock `tam` model writes an invisible U+200C (zero-width non-joiner) after many pullis (்), learned from its training text. CER and WER ignore invisible characters so models are compared on visible text; 'raw CER' counts them.

| Model | CER | WER | raw CER |
|---|---:|---:|---:|
| start (tam, best) | 5.88% | 20.31% | 11.52% |
| tam_v2 (best) | 2.35% | 7.76% | 2.35% |
| tam_v2 (fast) | 2.34% | 7.73% | 2.34% |
| V1 (188 styles) | 2.81% | 10.06% | 2.81% |
| V2-research | 2.7% | 8.86% | 2.7% |

## Pre-1978 letter shapes

Lines drawn with the old shapes of ணா றா னா / ணை லை ளை னை (fonts that draw them by default, or with the OpenType feature turned on) and all other lines.

| Model | Old shapes CER | Modern shapes CER |
|---|---:|---:|
| start (tam, best) | 4.39% (448 lines) | 6.3% |
| tam_v2 (best) | 2.24% (448 lines) | 2.39% |
| tam_v2 (fast) | 2.21% (448 lines) | 2.38% |
| V1 (188 styles) | 3.02% (448 lines) | 2.75% |
| V2-research | 2.47% (448 lines) | 2.76% |

## CER per font

| Font | Lines | start (tam, best) | tam_v2 (best) | tam_v2 (fast) | V1 (188 styles) | V2-research |
|---|---:|---:|---:|---:|---:|---:|
| Aaram Regular | 7 | 24.03% | 19.74% | 19.74% | 19.74% | 20.17% |
| Abhaya Libre CANARY Bold | 7 | 6.35% | 3.97% | 3.97% | 5.16% | 5.56% |
| Abhaya Libre CANARY Bold (old letters) | 7 | 4.05% | 4.05% | 4.05% | 3.15% | 2.25% |
| Abhaya Libre CANARY ExtraBold | 7 | 6.37% | 2.55% | 3.82% | 6.37% | 5.1% |
| Abhaya Libre CANARY ExtraBold (old letters) | 7 | 0.49% | 0.49% | 0.49% | 2.45% | 0.98% |
| Abhaya Libre CANARY Medium | 7 | 5.8% | 5.8% | 5.8% | 6.76% | 5.8% |
| Abhaya Libre CANARY Medium (old letters) | 7 | 2.31% | 0.93% | 0.93% | 1.39% | 0.0% |
| Abhaya Libre CANARY Regular | 7 | 0.41% | 0.0% | 0.0% | 0.81% | 0.0% |
| Abhaya Libre CANARY Regular (old letters) | 7 | 21.93% | 21.93% | 21.39% | 21.39% | 21.39% |
| Abhaya Libre CANARY SemiBold | 7 | 2.61% | 0.87% | 1.3% | 1.3% | 1.74% |
| Abhaya Libre CANARY SemiBold (old letters) | 7 | 2.6% | 0.87% | 0.87% | 1.73% | 1.3% |
| AkrutiTml1 Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| AkrutiTml1 Normal | 7 | 15.96% | 15.49% | 15.49% | 15.96% | 16.43% |
| AkrutiTml2 Bold | 7 | 1.22% | 0.0% | 0.0% | 0.0% | 0.0% |
| AkrutiTml2 Normal | 7 | 1.26% | 0.84% | 0.84% | 0.84% | 0.84% |
| Anek Tamil Bold | 7 | 3.72% | 0.0% | 0.0% | 0.0% | 0.0% |
| Anek Tamil Bold (old letters) | 7 | 7.65% | 0.0% | 0.0% | 2.04% | 1.02% |
| Anek Tamil Condensed Bold | 7 | 16.59% | 8.78% | 8.29% | 8.78% | 6.83% |
| Anek Tamil Condensed Bold (old letters) | 7 | 9.21% | 0.84% | 0.42% | 0.42% | 0.42% |
| Anek Tamil Condensed Regular | 7 | 10.5% | 1.37% | 0.91% | 1.37% | 0.46% |
| Anek Tamil Condensed Regular (old letters) | 7 | 20.22% | 1.69% | 1.69% | 4.49% | 1.12% |
| Anek Tamil ExtraBold | 7 | 1.77% | 0.0% | 0.0% | 0.88% | 0.0% |
| Anek Tamil ExtraBold (old letters) | 7 | 4.42% | 0.0% | 0.0% | 1.61% | 0.0% |
| Anek Tamil ExtraLight | 7 | 4.73% | 0.36% | 0.36% | 0.0% | 1.09% |
| Anek Tamil ExtraLight (old letters) | 7 | 28.71% | 27.27% | 27.27% | 26.79% | 26.79% |
| Anek Tamil Light | 7 | 1.15% | 0.57% | 0.57% | 0.0% | 0.57% |
| Anek Tamil Light (old letters) | 7 | 3.83% | 0.96% | 0.48% | 1.91% | 0.0% |
| Anek Tamil Medium | 7 | 0.49% | 0.0% | 0.49% | 0.49% | 0.49% |
| Anek Tamil Medium (old letters) | 7 | 2.19% | 0.36% | 0.73% | 2.19% | 0.36% |
| Anek Tamil Regular | 7 | 2.51% | 0.42% | 0.42% | 0.42% | 0.42% |
| Anek Tamil Regular (old letters) | 7 | 3.38% | 0.84% | 0.84% | 1.27% | 1.27% |
| Anek Tamil SemiBold | 7 | 3.16% | 2.53% | 2.53% | 2.53% | 3.16% |
| Anek Tamil SemiBold (old letters) | 7 | 3.02% | 0.43% | 0.43% | 1.29% | 0.86% |
| Anek Tamil SemiCondensed Bold | 7 | 5.63% | 0.0% | 0.0% | 0.94% | 0.0% |
| Anek Tamil SemiCondensed Bold (old letters) | 7 | 9.05% | 1.36% | 0.9% | 1.36% | 1.36% |
| Anek Tamil SemiCondensed Regular | 7 | 5.33% | 0.0% | 0.0% | 0.41% | 0.0% |
| Anek Tamil SemiCondensed Regular (old letters) | 7 | 5.19% | 0.94% | 1.42% | 1.89% | 0.94% |
| Anek Tamil Thin | 7 | 7.94% | 1.59% | 1.98% | 0.4% | 1.98% |
| Anek Tamil Thin (old letters) | 7 | 12.15% | 8.1% | 8.1% | 8.5% | 7.69% |
| Arima Bold | 7 | 6.22% | 1.04% | 1.04% | 0.52% | 1.04% |
| Arima Bold (old letters) | 7 | 0.36% | 0.36% | 0.0% | 0.36% | 0.36% |
| Arima ExtraLight | 7 | 18.27% | 16.75% | 16.75% | 16.24% | 17.26% |
| Arima ExtraLight (old letters) | 7 | 1.81% | 0.9% | 0.9% | 1.36% | 1.36% |
| Arima Light | 7 | 6.99% | 1.08% | 0.54% | 1.08% | 1.61% |
| Arima Light (old letters) | 7 | 1.22% | 0.81% | 0.0% | 0.0% | 0.41% |
| Arima Medium | 7 | 0.35% | 0.71% | 0.71% | 0.71% | 0.0% |
| Arima Medium (old letters) | 7 | 1.18% | 0.0% | 0.0% | 0.78% | 0.0% |
| Arima Regular | 7 | 2.4% | 2.0% | 2.0% | 1.6% | 1.6% |
| Arima Regular (old letters) | 7 | 2.01% | 0.4% | 0.4% | 0.8% | 0.0% |
| Arima SemiBold | 7 | 0.0% | 0.36% | 0.36% | 0.0% | 0.0% |
| Arima SemiBold (old letters) | 7 | 0.92% | 0.92% | 0.92% | 0.92% | 0.92% |
| Arima Thin | 7 | 6.7% | 3.57% | 3.57% | 6.7% | 5.8% |
| Arima Thin (old letters) | 7 | 15.32% | 15.32% | 15.32% | 15.32% | 15.32% |
| Auvaiyar | 7 | 3.03% | 0.43% | 0.43% | 0.0% | 0.43% |
| Auvaiyar Bold | 7 | 4.86% | 2.16% | 2.16% | 2.16% | 1.62% |
| Auvaiyar Bold Italic | 7 | 8.19% | 1.17% | 0.58% | 0.58% | 0.0% |
| Auvaiyar Italic | 7 | 9.96% | 2.21% | 2.21% | 3.32% | 1.48% |
| Baloo Thambi 2 Bold | 7 | 0.0% | 0.47% | 0.47% | 0.0% | 0.0% |
| Baloo Thambi 2 ExtraBold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Baloo Thambi 2 Medium | 7 | 1.91% | 0.48% | 0.48% | 1.44% | 0.96% |
| Baloo Thambi 2 Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Baloo Thambi 2 SemiBold | 7 | 1.9% | 2.38% | 1.9% | 1.9% | 1.43% |
| Catamaran Black | 7 | 2.93% | 0.49% | 0.49% | 1.95% | 2.44% |
| Catamaran Black (old letters) | 7 | 3.72% | 0.0% | 0.0% | 0.83% | 0.83% |
| Catamaran Bold | 7 | 1.53% | 1.53% | 1.02% | 0.0% | 1.02% |
| Catamaran Bold (old letters) | 7 | 1.32% | 0.0% | 0.0% | 1.32% | 0.44% |
| Catamaran ExtraBold | 7 | 2.28% | 0.91% | 0.91% | 1.83% | 1.83% |
| Catamaran ExtraBold (old letters) | 7 | 3.9% | 0.43% | 0.43% | 2.16% | 1.3% |
| Catamaran ExtraLight | 7 | 14.09% | 5.45% | 5.91% | 5.91% | 7.27% |
| Catamaran ExtraLight (old letters) | 7 | 0.91% | 0.0% | 0.0% | 0.91% | 0.0% |
| Catamaran Light | 7 | 1.19% | 0.4% | 0.4% | 0.0% | 0.0% |
| Catamaran Light (old letters) | 7 | 7.21% | 1.44% | 1.44% | 4.33% | 1.92% |
| Catamaran Medium | 7 | 1.36% | 0.0% | 0.0% | 0.0% | 0.0% |
| Catamaran Medium (old letters) | 7 | 0.0% | 0.0% | 0.0% | 0.97% | 0.0% |
| Catamaran Regular | 7 | 2.53% | 0.84% | 0.84% | 0.0% | 0.42% |
| Catamaran Regular (old letters) | 7 | 2.83% | 0.0% | 0.0% | 1.42% | 0.0% |
| Catamaran SemiBold | 7 | 1.07% | 1.07% | 1.07% | 0.53% | 1.07% |
| Catamaran SemiBold (old letters) | 7 | 2.12% | 0.85% | 0.85% | 1.27% | 0.0% |
| Catamaran Thin | 7 | 5.21% | 2.84% | 2.84% | 5.21% | 4.74% |
| Catamaran Thin (old letters) | 7 | 1.72% | 1.72% | 1.72% | 0.86% | 1.72% |
| Chemmozhi Comic | 7 | 14.58% | 15.0% | 15.0% | 13.75% | 13.75% |
| Chemmozhi Paranar | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Chemmozhi Thendral | 7 | 2.24% | 2.61% | 2.61% | 1.49% | 1.87% |
| Chemmozhi Thenee | 7 | 0.85% | 0.85% | 0.85% | 0.85% | 0.85% |
| Chemmozhi Times | 7 | 1.75% | 0.0% | 0.0% | 0.44% | 0.88% |
| Chemmozhi Vaigai | 7 | 2.92% | 0.73% | 0.73% | 1.46% | 0.73% |
| Coiny Regular | 7 | 9.85% | 1.48% | 0.99% | 2.96% | 2.96% |
| Droid Sans Tamil | 7 | 0.51% | 0.51% | 0.51% | 0.51% | 0.51% |
| Droid Sans Tamil Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| FreeSerif | 7 | 4.19% | 2.4% | 2.99% | 4.79% | 2.4% |
| Google Sans Bold | 7 | 0.42% | 0.0% | 0.0% | 0.42% | 0.42% |
| Google Sans Bold Italic | 7 | 0.48% | 0.0% | 0.0% | 0.0% | 0.0% |
| Google Sans Italic | 7 | 0.0% | 0.62% | 0.62% | 0.0% | 0.0% |
| Google Sans Medium | 7 | 0.7% | 0.7% | 0.7% | 1.05% | 0.7% |
| Google Sans Medium Italic | 7 | 0.82% | 0.41% | 0.41% | 0.82% | 1.22% |
| Google Sans Regular | 7 | 16.12% | 9.09% | 9.09% | 15.7% | 15.7% |
| Hind Madurai Bold | 7 | 2.03% | 0.51% | 0.51% | 0.51% | 0.51% |
| Hind Madurai Bold (old letters) | 7 | 2.62% | 0.52% | 0.52% | 1.05% | 0.52% |
| Hind Madurai Light | 7 | 1.93% | 0.0% | 0.0% | 0.39% | 0.0% |
| Hind Madurai Light (old letters) | 7 | 0.0% | 0.41% | 0.41% | 0.41% | 0.41% |
| Hind Madurai Medium | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Hind Madurai Medium (old letters) | 7 | 1.1% | 1.1% | 1.1% | 1.1% | 0.55% |
| Hind Madurai Regular | 7 | 1.4% | 0.0% | 0.0% | 0.93% | 0.0% |
| Hind Madurai Regular (old letters) | 7 | 1.16% | 0.58% | 0.58% | 1.74% | 0.58% |
| Hind Madurai SemiBold | 7 | 1.1% | 0.0% | 0.0% | 0.74% | 0.37% |
| Hind Madurai SemiBold (old letters) | 7 | 0.0% | 0.0% | 0.0% | 0.95% | 0.0% |
| Karla Tamil Inclined | 7 | 0.51% | 0.0% | 0.0% | 0.0% | 0.0% |
| Karla Tamil Inclined Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Karla Tamil Upright | 7 | 0.44% | 0.0% | 0.0% | 0.44% | 0.0% |
| Karla Tamil Upright Bold | 7 | 0.36% | 0.36% | 0.73% | 1.82% | 0.73% |
| Kavivanar Regular | 7 | 1.52% | 0.76% | 0.76% | 0.38% | 0.0% |
| Lohit Tamil | 7 | 1.14% | 0.0% | 0.0% | 0.0% | 0.0% |
| Lohit Tamil Classical | 7 | 1.22% | 0.81% | 0.81% | 0.81% | 0.81% |
| Madurai Bold | 7 | 16.67% | 2.19% | 2.19% | 2.19% | 3.07% |
| Madurai Regular | 7 | 29.79% | 3.83% | 3.83% | 2.13% | 3.83% |
| Madurai Thin | 7 | 40.67% | 2.87% | 2.87% | 3.35% | 4.78% |
| Meera Inimai Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Mukta Malar Bold | 7 | 0.0% | 0.58% | 0.58% | 0.58% | 0.58% |
| Mukta Malar Bold (old letters) | 7 | 0.0% | 0.46% | 0.46% | 0.0% | 0.0% |
| Mukta Malar ExtraBold | 7 | 1.73% | 0.58% | 0.58% | 1.16% | 1.16% |
| Mukta Malar ExtraBold (old letters) | 7 | 0.55% | 0.0% | 0.0% | 0.55% | 0.0% |
| Mukta Malar ExtraLight | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Mukta Malar ExtraLight (old letters) | 7 | 0.97% | 0.0% | 0.0% | 0.49% | 0.49% |
| Mukta Malar Light | 7 | 0.77% | 0.38% | 0.38% | 0.38% | 0.38% |
| Mukta Malar Light (old letters) | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Mukta Malar Medium | 7 | 1.72% | 1.72% | 1.29% | 1.29% | 0.86% |
| Mukta Malar Medium (old letters) | 7 | 7.35% | 4.08% | 4.08% | 6.94% | 7.35% |
| Mukta Malar Regular | 7 | 1.03% | 0.51% | 0.51% | 0.51% | 0.51% |
| Mukta Malar Regular (old letters) | 7 | 1.89% | 0.94% | 0.94% | 1.42% | 0.94% |
| Mukta Malar SemiBold | 7 | 6.87% | 1.91% | 1.91% | 6.87% | 7.25% |
| Mukta Malar SemiBold (old letters) | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Neythal Regular | 7 | 7.04% | 0.35% | 0.35% | 0.7% | 0.35% |
| Noto Sans Tamil Black | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil Bold | 7 | 1.84% | 1.1% | 1.1% | 1.1% | 1.1% |
| Noto Sans Tamil Condensed Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil Condensed Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil ExtraBold | 7 | 12.3% | 3.74% | 3.74% | 11.76% | 11.76% |
| Noto Sans Tamil ExtraCondensed Bold | 7 | 0.0% | 0.0% | 0.0% | 0.4% | 0.0% |
| Noto Sans Tamil ExtraCondensed Regular | 7 | 0.42% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil ExtraLight | 7 | 0.48% | 1.43% | 1.43% | 0.48% | 0.48% |
| Noto Sans Tamil Light | 7 | 1.1% | 1.1% | 1.1% | 1.1% | 0.55% |
| Noto Sans Tamil Medium | 7 | 0.8% | 0.8% | 0.8% | 0.8% | 0.8% |
| Noto Sans Tamil Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil SemiBold | 7 | 0.0% | 0.0% | 0.0% | 0.44% | 0.0% |
| Noto Sans Tamil SemiCondensed Bold | 7 | 0.41% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil SemiCondensed Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil Thin | 7 | 1.06% | 1.06% | 1.06% | 1.06% | 0.53% |
| Noto Serif Tamil Black | 7 | 2.54% | 0.0% | 0.0% | 0.0% | 0.51% |
| Noto Serif Tamil Black Italic | 7 | 16.49% | 9.04% | 9.04% | 12.23% | 11.7% |
| Noto Serif Tamil Bold | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Bold Italic | 7 | 3.2% | 1.83% | 1.83% | 0.91% | 0.91% |
| Noto Serif Tamil Condensed Bold | 7 | 1.15% | 0.57% | 0.57% | 1.15% | 0.0% |
| Noto Serif Tamil Condensed Regular | 7 | 0.4% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil ExtraBold | 7 | 1.35% | 0.0% | 0.0% | 0.0% | 0.9% |
| Noto Serif Tamil ExtraBold Italic | 7 | 0.36% | 0.72% | 0.72% | 0.0% | 0.36% |
| Noto Serif Tamil ExtraCondensed Bold | 7 | 0.0% | 0.0% | 0.0% | 0.56% | 0.0% |
| Noto Serif Tamil ExtraCondensed Regular | 7 | 0.0% | 0.51% | 0.51% | 0.0% | 0.0% |
| Noto Serif Tamil ExtraLight | 7 | 0.48% | 1.44% | 1.44% | 0.96% | 0.48% |
| Noto Serif Tamil ExtraLight Italic | 7 | 2.07% | 1.04% | 1.55% | 0.52% | 0.52% |
| Noto Serif Tamil Italic | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Light | 7 | 0.51% | 0.51% | 0.51% | 0.51% | 0.51% |
| Noto Serif Tamil Light Italic | 7 | 2.15% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Medium | 7 | 1.58% | 1.05% | 1.05% | 1.05% | 1.05% |
| Noto Serif Tamil Medium Italic | 7 | 0.52% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Regular | 7 | 0.55% | 0.0% | 0.0% | 1.1% | 0.55% |
| Noto Serif Tamil SemiBold | 7 | 0.4% | 0.0% | 0.0% | 0.4% | 0.0% |
| Noto Serif Tamil SemiBold Italic | 7 | 4.17% | 2.08% | 2.08% | 1.04% | 1.56% |
| Noto Serif Tamil SemiCondensed Bold | 7 | 1.46% | 0.49% | 0.49% | 0.49% | 0.49% |
| Noto Serif Tamil SemiCondensed Regular | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Slanted Bold | 7 | 0.46% | 0.92% | 0.92% | 0.46% | 0.46% |
| Noto Serif Tamil Slanted Regular | 7 | 1.05% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Thin | 7 | 1.28% | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Thin Italic | 7 | 23.18% | 22.32% | 22.32% | 22.32% | 21.89% |
| Oi Regular | 7 | 58.72% | 32.56% | 30.81% | 32.56% | 33.72% |
| Pavanam Regular | 7 | 0.62% | 0.0% | 0.0% | 0.0% | 0.62% |
| PostNoBillsJaffna Bold | 7 | 2.28% | 1.9% | 1.9% | 1.9% | 1.52% |
| PostNoBillsJaffna Bold (old letters) | 7 | 2.13% | 1.06% | 1.06% | 2.66% | 1.6% |
| PostNoBillsJaffna ExtraBold | 7 | 3.94% | 0.79% | 0.79% | 1.97% | 2.36% |
| PostNoBillsJaffna ExtraBold (old letters) | 7 | 11.26% | 5.41% | 5.41% | 9.91% | 9.91% |
| PostNoBillsJaffna Light | 7 | 22.27% | 19.33% | 19.33% | 18.91% | 18.49% |
| PostNoBillsJaffna Light (old letters) | 7 | 3.2% | 0.0% | 0.0% | 1.37% | 1.83% |
| PostNoBillsJaffna Medium | 7 | 9.13% | 0.0% | 0.0% | 1.83% | 2.28% |
| PostNoBillsJaffna Medium (old letters) | 7 | 4.08% | 1.22% | 1.22% | 0.41% | 0.41% |
| PostNoBillsJaffna Regular | 7 | 8.18% | 1.12% | 1.49% | 2.97% | 2.6% |
| PostNoBillsJaffna Regular (old letters) | 7 | 4.55% | 0.83% | 0.83% | 2.48% | 2.07% |
| PostNoBillsJaffna SemiBold | 7 | 2.13% | 0.0% | 0.0% | 0.0% | 0.35% |
| PostNoBillsJaffna SemiBold (old letters) | 7 | 7.03% | 3.52% | 3.12% | 5.47% | 5.86% |
| Samyak Tamil | 7 | 2.79% | 0.0% | 0.0% | 1.12% | 0.0% |
| TABUni-Tamil021 | 7 | 21.33% | 4.27% | 3.79% | 2.37% | 5.69% |
| TABUni-Tamil032 | 7 | 7.05% | 1.32% | 1.32% | 1.32% | 0.88% |
| TAMUni-Tamil042 | 7 | 26.92% | 4.4% | 2.75% | 4.4% | 6.04% |
| TAMUni-Tamil046 | 7 | 20.92% | 14.23% | 14.64% | 13.39% | 14.23% |
| TAMUni-Tamil150 | 7 | 47.52% | 30.5% | 30.5% | 28.37% | 33.33% |
| TAMUni-Tamil195 | 7 | 57.32% | 31.3% | 32.93% | 36.18% | 36.99% |
| TAMu_Kadambri Regular | 7 | 2.65% | 1.06% | 1.06% | 1.59% | 1.06% |
| TAMu_Kalyani | 7 | 0.47% | 0.0% | 0.0% | 0.0% | 0.47% |
| TAMu_Maduram | 7 | 4.84% | 2.02% | 2.02% | 3.63% | 2.82% |
| TAU-Achu | 7 | 12.28% | 4.39% | 3.95% | 3.07% | 3.51% |
| TAU-Achu Italic | 7 | 22.34% | 5.85% | 4.79% | 4.26% | 6.38% |
| TAU-Barathi | 7 | 8.26% | 7.39% | 7.39% | 7.39% | 7.39% |
| TAU-Barathi Bold | 7 | 0.93% | 0.46% | 0.46% | 0.46% | 0.0% |
| TAU-Barathi BoldItalic | 7 | 1.23% | 0.0% | 0.0% | 0.41% | 0.0% |
| TAU-Barathi Italic | 7 | 1.21% | 0.61% | 0.61% | 0.61% | 0.0% |
| TAU-Ezhil | 7 | 5.97% | 1.0% | 0.5% | 1.49% | 1.0% |
| TAU-Ezhil Bold | 7 | 8.98% | 0.39% | 0.78% | 1.17% | 1.56% |
| TAU-Ezhil Italic | 7 | 5.96% | 0.0% | 0.43% | 0.85% | 1.7% |
| TAU-Kabilar | 7 | 1.83% | 0.61% | 0.61% | 0.0% | 1.22% |
| TAU-Kabilar Bold | 7 | 4.66% | 0.0% | 0.0% | 0.0% | 0.0% |
| TAU-Kabilar BoldItalic | 7 | 11.79% | 2.85% | 2.85% | 3.25% | 2.85% |
| TAU-Kabilar Italic | 7 | 3.0% | 0.5% | 0.5% | 2.0% | 1.0% |
| TAU-Kambar | 7 | 14.21% | 3.05% | 3.55% | 3.55% | 3.55% |
| TAU-Kambar Bold | 7 | 13.64% | 5.05% | 5.05% | 4.55% | 6.06% |
| TAU-Kambar BoldItalic | 7 | 13.22% | 3.52% | 3.08% | 6.17% | 7.05% |
| TAU-Kambar Italic | 7 | 32.51% | 20.16% | 20.99% | 21.81% | 22.22% |
| TAU-Kaveri | 7 | 4.27% | 0.95% | 1.42% | 1.42% | 1.9% |
| TAU-Kaveri Bold | 7 | 3.17% | 1.59% | 2.12% | 2.12% | 1.59% |
| TAU-Kaveri BoldItalic | 7 | 4.42% | 1.77% | 1.77% | 0.88% | 1.33% |
| TAU-Kaveri Italic | 7 | 3.92% | 0.0% | 0.0% | 0.0% | 0.0% |
| TAU-Kurinji | 7 | 15.21% | 3.23% | 2.3% | 4.15% | 3.23% |
| TAU-Kurinji Bold | 7 | 0.48% | 0.48% | 0.48% | 0.97% | 0.48% |
| TAU-Kurinji Italic | 7 | 8.07% | 0.62% | 0.62% | 0.0% | 0.0% |
| TAU-Malar | 7 | 17.39% | 14.67% | 14.67% | 14.67% | 14.13% |
| TAU-Malar Bold | 7 | 1.6% | 0.0% | 0.0% | 0.53% | 0.0% |
| TAU-Malar Italic | 7 | 19.05% | 1.36% | 1.36% | 0.0% | 1.36% |
| TAU-Marutham | 7 | 0.79% | 0.39% | 0.39% | 0.39% | 0.79% |
| TAU-Marutham Bold | 7 | 0.78% | 0.0% | 0.0% | 0.39% | 0.0% |
| TAU-Marutham Italic | 7 | 3.24% | 0.54% | 0.54% | 1.08% | 0.54% |
| TAU-Mullai | 7 | 2.25% | 1.69% | 1.69% | 0.56% | 0.56% |
| TAU-Mullai Bold | 7 | 1.15% | 0.38% | 0.38% | 0.0% | 0.76% |
| TAU-Mullai Italic | 7 | 17.68% | 8.29% | 5.52% | 9.39% | 6.08% |
| TAU-Neythal | 7 | 23.18% | 10.0% | 10.0% | 13.18% | 10.45% |
| TAU-Neythal Bold | 7 | 15.21% | 0.0% | 0.0% | 0.0% | 0.0% |
| TAU-Neythal Italic | 7 | 45.16% | 5.99% | 6.45% | 7.37% | 7.83% |
| TAU-Nilavu | 7 | 14.19% | 0.34% | 0.34% | 0.68% | 0.68% |
| TAU-Nilavu Bold | 7 | 9.76% | 0.7% | 0.7% | 1.39% | 1.39% |
| TAU-Nilavu Italic | 7 | 21.6% | 2.35% | 2.82% | 1.88% | 0.94% |
| TAU-Paalai Bold | 7 | 0.0% | 0.0% | 0.0% | 0.51% | 0.51% |
| TAU-Paalai Italic | 7 | 11.2% | 10.8% | 10.8% | 10.8% | 10.8% |
| TAU-Urai Bold | 7 | 0.0% | 0.42% | 0.42% | 0.0% | 0.0% |
| TAU-Urai Italic | 7 | 8.0% | 1.0% | 1.0% | 1.5% | 2.5% |
| TAU-Valluvar | 7 | 3.83% | 2.13% | 2.13% | 6.38% | 5.96% |
| TAU-Valluvar Bold | 7 | 0.96% | 0.0% | 0.0% | 1.44% | 0.48% |
| TAU-Valluvar BoldItalic | 7 | 2.5% | 0.0% | 0.83% | 2.5% | 0.42% |
| TAU-Valluvar Italic | 7 | 8.7% | 2.17% | 2.17% | 3.8% | 3.8% |
| TAU-kaviri | 7 | 5.37% | 0.0% | 0.0% | 0.0% | 0.0% |
| TAU-kollidam | 7 | 8.54% | 0.0% | 0.0% | 0.0% | 0.61% |
| TAU-palar | 7 | 9.71% | 3.43% | 3.43% | 4.57% | 4.57% |
| TAU-ponni | 7 | 4.72% | 0.47% | 0.47% | 0.0% | 0.0% |
| TAU-porunai | 7 | 5.19% | 0.47% | 0.47% | 1.89% | 0.47% |
| TAU-pothigai | 7 | 0.0% | 0.88% | 0.88% | 0.44% | 0.44% |
| TAU-thamirabarani | 7 | 5.6% | 3.36% | 3.36% | 5.6% | 4.85% |
| TSCu_Times | 7 | 3.64% | 1.82% | 1.82% | 1.36% | 1.36% |
| ThiruValluvar | 7 | 1.5% | 0.75% | 0.75% | 1.12% | 0.75% |
| ThiruValluvar Bold | 7 | 1.94% | 1.94% | 1.94% | 3.4% | 2.91% |
| ThiruValluvar Bold Italic | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| ThiruValluvar Italic | 7 | 1.26% | 0.84% | 0.84% | 0.84% | 0.42% |
| Tiro Tamil Italic | 7 | 1.98% | 0.5% | 0.5% | 0.5% | 0.99% |
| Tiro Tamil Italic (old letters) | 7 | 24.12% | 13.57% | 13.57% | 17.59% | 16.08% |
| Tiro Tamil Regular | 7 | 1.49% | 1.86% | 1.86% | 1.12% | 1.86% |
| Tiro Tamil Regular (old letters) | 7 | 1.85% | 0.46% | 0.46% | 0.93% | 0.46% |
| Uni Ila.Sundaram-01 | 7 | 0.37% | 0.0% | 0.0% | 0.0% | 0.75% |
| Uni Ila.Sundaram-02 | 7 | 7.41% | 0.82% | 0.82% | 0.82% | 0.82% |
| Uni Ila.Sundaram-03 | 7 | 1.27% | 0.85% | 0.85% | 1.27% | 0.85% |
| Uni Ila.Sundaram-04 | 7 | 2.22% | 0.0% | 0.0% | 1.11% | 0.56% |
| Uni Ila.Sundaram-05 | 7 | 5.83% | 0.0% | 0.0% | 0.0% | 0.42% |
| Uni Ila.Sundaram-06 | 7 | 13.18% | 0.45% | 0.0% | 0.45% | 0.0% |
| Uni Ila.Sundaram-07 | 7 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-08 | 7 | 6.51% | 0.47% | 0.47% | 1.4% | 1.4% |
| Uni Ila.Sundaram-09 | 7 | 23.83% | 2.07% | 2.07% | 2.07% | 6.74% |
| Uni Ila.Sundaram-10 | 7 | 1.18% | 0.39% | 0.39% | 0.0% | 0.0% |
| Uni Ila.Sundaram-11 | 7 | 13.24% | 13.24% | 13.24% | 12.75% | 13.24% |
| Uni Ila.Sundaram-12 | 7 | 1.01% | 0.0% | 0.0% | 0.5% | 0.5% |
| Uni Ila.Sundaram-13 | 7 | 8.38% | 2.62% | 2.62% | 4.19% | 4.19% |
| Uni Ila.Sundaram-14 | 7 | 9.28% | 3.61% | 3.61% | 2.06% | 5.15% |
| Uni Ila.Sundaram-15 | 7 | 18.55% | 0.0% | 0.0% | 3.17% | 1.81% |
| Uni Ila.Sundaram-16 | 7 | 29.58% | 4.17% | 4.17% | 2.92% | 7.5% |
| Uni Ila.Sundaram-17 | 7 | 1.03% | 0.0% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-18 | 7 | 8.3% | 2.77% | 2.37% | 4.74% | 3.16% |
| Uni Ila.Sundaram-19 | 7 | 9.38% | 0.35% | 0.0% | 1.04% | 0.69% |
| Uni Ila.Sundaram-20 | 7 | 8.64% | 3.29% | 3.29% | 3.7% | 4.94% |
| YaldeviJaffna Bold | 7 | 0.34% | 0.0% | 0.0% | 0.0% | 0.34% |
| YaldeviJaffna Bold (old letters) | 7 | 0.69% | 0.0% | 0.0% | 1.38% | 0.0% |
| YaldeviJaffna ExtraLight | 7 | 4.04% | 0.45% | 0.9% | 2.24% | 0.45% |
| YaldeviJaffna ExtraLight (old letters) | 7 | 1.49% | 0.5% | 1.0% | 0.5% | 0.5% |
| YaldeviJaffna Light | 7 | 20.08% | 15.98% | 15.98% | 16.39% | 15.98% |
| YaldeviJaffna Light (old letters) | 7 | 17.56% | 14.63% | 14.15% | 17.07% | 14.63% |
| YaldeviJaffna Medium | 7 | 1.7% | 0.43% | 0.43% | 0.85% | 0.85% |
| YaldeviJaffna Medium (old letters) | 7 | 0.52% | 0.52% | 0.52% | 0.52% | 0.52% |
| YaldeviJaffna Regular | 7 | 6.51% | 1.4% | 1.4% | 1.4% | 1.4% |
| YaldeviJaffna Regular (old letters) | 7 | 3.64% | 1.36% | 1.36% | 1.82% | 1.82% |
| YaldeviJaffna SemiBold | 7 | 1.84% | 0.46% | 0.46% | 0.46% | 0.46% |
| YaldeviJaffna SemiBold (old letters) | 7 | 0.94% | 0.94% | 0.94% | 1.42% | 0.94% |
| real:dev | 7 | 1.61% | 0.64% | 0.96% | 1.93% | 0.96% |

## Top confusions: start (tam, best)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 179 |
| ◌ு (U+0BC1) | ∅ | 98 |
| ◌ி (U+0BBF) | ∅ | 92 |
| ட | ∅ | 88 |
| க | ∅ | 80 |
| ␠ | ∅ | 69 |
| த | ∅ | 65 |
| ன | ண | 59 |
| த | க | 59 |
| ர | ற | 56 |
| ப | ∅ | 55 |
| ◌ை (U+0BC8) | ∅ | 49 |
| ர | ∅ | 46 |
| வ | ∅ | 45 |
| ◌ெ (U+0BC6) | ∅ | 42 |

## Top confusions: tam_v2 (best)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 124 |
| ␠ | ∅ | 73 |
| ◌ு (U+0BC1) | ∅ | 57 |
| ◌ி (U+0BBF) | ∅ | 55 |
| க | ∅ | 52 |
| த | ∅ | 52 |
| ப | ∅ | 35 |
| ∅ | ␠ | 33 |
| . | ∅ | 32 |
| ட | ∅ | 31 |
| ◌ா (U+0BBE) | ∅ | 30 |
| ' | ∅ | 26 |
| ல | ∅ | 25 |
| வ | ∅ | 24 |
| ந | ∅ | 24 |

## Top confusions: tam_v2 (fast)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 124 |
| ␠ | ∅ | 72 |
| ◌ு (U+0BC1) | ∅ | 56 |
| ◌ி (U+0BBF) | ∅ | 54 |
| த | ∅ | 53 |
| க | ∅ | 51 |
| ப | ∅ | 34 |
| ∅ | ␠ | 33 |
| ◌ா (U+0BBE) | ∅ | 31 |
| ட | ∅ | 30 |
| . | ∅ | 29 |
| ல | ∅ | 26 |
| வ | ∅ | 25 |
| ' | ∅ | 25 |
| ந | ∅ | 24 |

## Top confusions: V1 (188 styles)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 139 |
| ∅ | ␠ | 64 |
| ◌ு (U+0BC1) | ∅ | 62 |
| ◌ி (U+0BBF) | ∅ | 61 |
| ␠ | ∅ | 57 |
| த | ∅ | 52 |
| க | ∅ | 51 |
| ◌ை (U+0BC8) | ∅ | 36 |
| ப | ∅ | 34 |
| ◌ா (U+0BBE) | ∅ | 32 |
| ட | ∅ | 31 |
| வ | ∅ | 25 |
| ல | ∅ | 25 |
| ந | ∅ | 24 |
| ன | ∅ | 21 |

## Top confusions: V2-research

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 139 |
| ␠ | ∅ | 66 |
| ◌ு (U+0BC1) | ∅ | 55 |
| ◌ி (U+0BBF) | ∅ | 54 |
| க | ∅ | 53 |
| த | ∅ | 53 |
| ப | ∅ | 31 |
| ◌ா (U+0BBE) | ∅ | 30 |
| . | ∅ | 28 |
| ட | ∅ | 28 |
| ல | ∅ | 27 |
| ∅ | ␠ | 27 |
| ந | ∅ | 26 |
| வ | ∅ | 24 |
| ◌ை (U+0BC8) | ∅ | 23 |
