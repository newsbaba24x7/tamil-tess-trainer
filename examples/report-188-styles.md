# Evaluation report

2068 held-out line images, `--psm 7`. CER = character error rate, WER = word error rate (lower is better).

The stock `tam` model writes an invisible U+200C (zero-width non-joiner) after many pullis (்), learned from its training text. CER and WER ignore invisible characters so models are compared on visible text; 'raw CER' counts them.

| Model | CER | WER | raw CER |
|---|---:|---:|---:|
| start (tam, best) | 6.54% | 22.73% | 11.88% |
| installed tam | 6.64% | 22.71% | 12.09% |
| new (best/float) | 2.01% | 7.21% | 2.01% |
| new (fast/int) | 1.98% | 7.05% | 1.98% |

## CER per font

| Font | Lines | start (tam, best) | installed tam | new (best/float) | new (fast/int) |
|---|---:|---:|---:|---:|---:|
| Aaram Regular | 11 | 8.41% | 7.51% | 1.2% | 0.6% |
| AkrutiTml1 Bold | 11 | 4.44% | 1.71% | 1.02% | 1.02% |
| AkrutiTml1 Normal | 11 | 8.54% | 7.44% | 6.61% | 6.61% |
| AkrutiTml2 Bold | 11 | 2.85% | 1.55% | 1.3% | 1.3% |
| AkrutiTml2 Normal | 11 | 2.27% | 1.13% | 0.57% | 0.57% |
| Anek Tamil Bold | 11 | 3.11% | 3.5% | 0.0% | 0.0% |
| Anek Tamil ExtraBold | 11 | 3.56% | 2.67% | 1.19% | 0.89% |
| Anek Tamil ExtraLight | 11 | 11.06% | 7.53% | 4.71% | 4.47% |
| Anek Tamil Light | 11 | 0.32% | 2.59% | 0.32% | 0.32% |
| Anek Tamil Medium | 11 | 1.81% | 4.22% | 0.0% | 0.0% |
| Anek Tamil Regular | 11 | 1.55% | 2.79% | 0.31% | 0.31% |
| Anek Tamil SemiBold | 11 | 1.26% | 3.14% | 0.31% | 0.0% |
| Anek Tamil Thin | 11 | 1.72% | 4.66% | 1.47% | 1.72% |
| Arima Bold | 11 | 0.9% | 1.13% | 0.45% | 0.23% |
| Arima ExtraLight | 11 | 1.7% | 0.85% | 0.28% | 0.0% |
| Arima Light | 11 | 5.01% | 4.75% | 5.01% | 5.01% |
| Arima Medium | 11 | 3.62% | 3.62% | 1.45% | 1.45% |
| Arima Regular | 11 | 0.3% | 0.3% | 0.0% | 0.0% |
| Arima SemiBold | 11 | 3.17% | 0.95% | 0.0% | 0.0% |
| Arima Thin | 11 | 12.84% | 13.39% | 12.84% | 12.84% |
| Auvaiyar Bold | 11 | 2.15% | 1.61% | 1.34% | 1.34% |
| Auvaiyar Bold Italic | 11 | 7.41% | 12.35% | 1.23% | 1.23% |
| Auvaiyar Italic | 11 | 8.87% | 13.83% | 0.35% | 0.71% |
| Auvaiyar Regular | 11 | 3.18% | 2.44% | 1.47% | 0.73% |
| Baloo Thambi 2 Bold | 11 | 0.0% | 1.07% | 0.0% | 0.0% |
| Baloo Thambi 2 ExtraBold | 11 | 0.58% | 0.87% | 0.29% | 0.29% |
| Baloo Thambi 2 Medium | 11 | 0.29% | 1.44% | 0.57% | 0.57% |
| Baloo Thambi 2 Regular | 11 | 0.0% | 0.32% | 0.0% | 0.0% |
| Baloo Thambi 2 SemiBold | 11 | 0.3% | 2.08% | 0.6% | 0.3% |
| Catamaran Black | 11 | 0.31% | 0.61% | 0.31% | 0.31% |
| Catamaran Bold | 11 | 0.28% | 1.13% | 0.0% | 0.0% |
| Catamaran ExtraBold | 11 | 1.41% | 1.87% | 0.23% | 0.23% |
| Catamaran ExtraLight | 11 | 17.96% | 17.96% | 21.67% | 21.36% |
| Catamaran Light | 11 | 1.85% | 0.92% | 0.62% | 0.62% |
| Catamaran Medium | 11 | 1.56% | 1.56% | 0.52% | 0.78% |
| Catamaran Regular | 11 | 1.14% | 1.14% | 0.29% | 0.29% |
| Catamaran SemiBold | 11 | 1.37% | 0.68% | 0.0% | 0.0% |
| Catamaran Thin | 11 | 14.4% | 14.4% | 13.33% | 13.33% |
| Chemmozhi Comic | 11 | 18.32% | 18.02% | 17.42% | 17.42% |
| Chemmozhi Paranar | 11 | 1.09% | 1.36% | 0.82% | 0.82% |
| Chemmozhi Thendral | 11 | 0.25% | 0.51% | 0.25% | 0.25% |
| Chemmozhi Thenee | 11 | 0.87% | 0.58% | 0.58% | 0.58% |
| Chemmozhi Times | 11 | 3.67% | 2.67% | 0.0% | 0.0% |
| Chemmozhi Vaigai | 11 | 1.27% | 0.95% | 0.32% | 0.32% |
| Coiny Regular | 11 | 5.1% | 4.82% | 1.42% | 1.42% |
| Droid Sans Tamil | 11 | 0.59% | 0.3% | 0.0% | 0.0% |
| Droid Sans Tamil Bold | 11 | 5.26% | 5.26% | 5.26% | 5.26% |
| Google Sans Bold | 11 | 0.29% | 0.59% | 0.29% | 0.29% |
| Google Sans Bold Italic | 11 | 0.55% | 0.55% | 0.0% | 0.0% |
| Google Sans Italic | 11 | 1.29% | 1.08% | 0.0% | 0.0% |
| Google Sans Medium | 11 | 0.31% | 0.62% | 0.0% | 0.0% |
| Google Sans Medium Italic | 11 | 1.49% | 0.0% | 0.6% | 0.3% |
| Google Sans Regular | 11 | 0.29% | 0.29% | 0.0% | 0.0% |
| Hind Madurai Bold | 11 | 0.66% | 0.33% | 0.33% | 0.33% |
| Hind Madurai Light | 11 | 1.25% | 0.62% | 0.0% | 0.0% |
| Hind Madurai Medium | 11 | 0.67% | 0.34% | 0.34% | 0.67% |
| Hind Madurai Regular | 11 | 0.55% | 0.0% | 0.0% | 0.0% |
| Hind Madurai SemiBold | 11 | 0.73% | 0.73% | 0.0% | 0.0% |
| Karla Tamil Inclined | 11 | 0.0% | 0.0% | 0.22% | 0.22% |
| Karla Tamil Inclined Bold | 11 | 0.27% | 0.27% | 0.27% | 0.27% |
| Karla Tamil Upright | 11 | 0.0% | 0.0% | 0.0% | 0.0% |
| Karla Tamil Upright Bold | 11 | 0.0% | 0.0% | 0.26% | 0.26% |
| Kavivanar Regular | 11 | 0.0% | 1.47% | 0.0% | 0.0% |
| Latha | 11 | 0.52% | 0.77% | 0.0% | 0.0% |
| Lohit Tamil | 11 | 2.01% | 3.16% | 0.86% | 0.57% |
| Lohit Tamil Classical | 11 | 0.0% | 0.0% | 0.0% | 0.0% |
| Madurai Bold | 11 | 24.04% | 26.23% | 3.83% | 4.64% |
| Madurai Regular | 11 | 39.26% | 22.73% | 0.83% | 0.83% |
| Madurai Thin | 11 | 49.73% | 37.84% | 20.81% | 20.81% |
| Meera Inimai Regular | 11 | 0.35% | 0.35% | 0.35% | 0.69% |
| Mukta Malar Bold | 11 | 0.28% | 0.28% | 0.28% | 0.28% |
| Mukta Malar ExtraBold | 11 | 0.84% | 0.0% | 0.0% | 0.0% |
| Mukta Malar ExtraLight | 11 | 0.7% | 0.7% | 0.7% | 0.7% |
| Mukta Malar Light | 11 | 1.08% | 0.54% | 0.54% | 0.54% |
| Mukta Malar Medium | 11 | 1.75% | 1.17% | 0.58% | 0.58% |
| Mukta Malar Regular | 11 | 0.58% | 1.16% | 0.58% | 0.58% |
| Mukta Malar SemiBold | 11 | 0.0% | 0.79% | 0.53% | 0.53% |
| Neythal Regular | 11 | 6.12% | 2.75% | 0.92% | 1.22% |
| Noto Sans Tamil Bold | 11 | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil Condensed Bold | 11 | 0.29% | 0.0% | 0.29% | 0.29% |
| Noto Sans Tamil Condensed Regular | 11 | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Sans Tamil Regular | 11 | 0.0% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Bold | 11 | 1.28% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Regular | 11 | 0.38% | 0.38% | 0.38% | 0.38% |
| Noto Serif Tamil Slanted Bold | 11 | 2.25% | 0.0% | 0.0% | 0.0% |
| Noto Serif Tamil Slanted Regular | 11 | 0.87% | 0.87% | 0.29% | 0.29% |
| Oi Regular | 11 | 33.45% | 38.91% | 4.0% | 3.27% |
| Pavanam Regular | 11 | 1.05% | 2.44% | 0.0% | 0.0% |
| PostNoBillsJaffna Bold | 11 | 4.78% | 2.39% | 0.96% | 0.96% |
| PostNoBillsJaffna ExtraBold | 11 | 1.88% | 2.81% | 0.94% | 0.94% |
| PostNoBillsJaffna Light | 11 | 3.3% | 5.77% | 1.1% | 0.82% |
| PostNoBillsJaffna Medium | 11 | 4.78% | 4.49% | 0.0% | 0.0% |
| PostNoBillsJaffna Regular | 11 | 7.66% | 4.55% | 0.48% | 0.48% |
| PostNoBillsJaffna SemiBold | 11 | 3.76% | 1.16% | 0.58% | 0.87% |
| Samyak Tamil | 11 | 1.66% | 0.66% | 0.66% | 1.0% |
| TABUni-Tamil021 | 11 | 19.94% | 18.15% | 0.89% | 1.19% |
| TABUni-Tamil032 | 11 | 1.02% | 2.73% | 0.0% | 0.0% |
| TAMUni-Tamil042 | 11 | 46.03% | 48.22% | 21.1% | 21.37% |
| TAMUni-Tamil046 | 11 | 15.14% | 12.7% | 2.97% | 2.97% |
| TAMUni-Tamil150 | 11 | 34.59% | 46.86% | 6.92% | 5.97% |
| TAMUni-Tamil195 | 11 | 47.68% | 52.63% | 8.98% | 8.67% |
| TAMu_Kadambri Regular | 11 | 0.33% | 1.63% | 0.0% | 0.0% |
| TAMu_Kalyani | 11 | 4.96% | 6.87% | 8.02% | 7.25% |
| TAMu_Maduram | 11 | 1.23% | 0.92% | 0.62% | 0.62% |
| TAU-Achu | 11 | 8.76% | 9.37% | 0.0% | 0.0% |
| TAU-Achu Italic | 11 | 22.54% | 19.26% | 3.28% | 3.28% |
| TAU-Barathi | 11 | 0.59% | 0.29% | 0.29% | 0.29% |
| TAU-Barathi Bold | 11 | 0.0% | 0.31% | 0.31% | 0.31% |
| TAU-Barathi BoldItalic | 11 | 2.42% | 3.32% | 0.91% | 0.91% |
| TAU-Barathi Italic | 11 | 1.38% | 1.38% | 1.93% | 1.93% |
| TAU-Ezhil | 11 | 9.46% | 9.19% | 1.62% | 1.35% |
| TAU-Ezhil Bold | 11 | 9.15% | 9.45% | 0.61% | 0.91% |
| TAU-Ezhil Italic | 11 | 8.62% | 9.66% | 1.57% | 1.31% |
| TAU-Kabilar | 11 | 0.5% | 1.01% | 0.5% | 0.25% |
| TAU-Kabilar Bold | 11 | 4.35% | 2.3% | 1.02% | 1.28% |
| TAU-Kabilar BoldItalic | 11 | 10.77% | 3.08% | 0.31% | 0.31% |
| TAU-Kabilar Italic | 11 | 12.89% | 10.6% | 3.44% | 3.44% |
| TAU-Kambar | 11 | 17.91% | 16.12% | 5.37% | 5.37% |
| TAU-Kambar Bold | 11 | 11.07% | 14.98% | 2.93% | 2.61% |
| TAU-Kambar BoldItalic | 11 | 24.03% | 35.27% | 10.47% | 10.47% |
| TAU-Kambar Italic | 11 | 13.41% | 16.91% | 3.21% | 3.21% |
| TAU-Kaveri | 11 | 14.9% | 17.88% | 13.25% | 13.58% |
| TAU-Kaveri Bold | 11 | 5.09% | 5.56% | 1.39% | 1.16% |
| TAU-Kaveri BoldItalic | 11 | 6.74% | 6.74% | 1.47% | 2.05% |
| TAU-Kaveri Italic | 11 | 4.21% | 3.88% | 0.0% | 0.32% |
| TAU-Kurinji | 11 | 0.57% | 1.14% | 0.28% | 0.0% |
| TAU-Kurinji Bold | 11 | 1.6% | 1.28% | 0.64% | 0.32% |
| TAU-Kurinji Italic | 11 | 8.8% | 5.87% | 0.59% | 0.59% |
| TAU-Malar | 11 | 3.96% | 1.58% | 0.79% | 0.79% |
| TAU-Malar Bold | 11 | 2.87% | 2.29% | 0.29% | 0.29% |
| TAU-Malar Italic | 11 | 11.45% | 12.57% | 0.56% | 0.56% |
| TAU-Marutham | 11 | 0.59% | 0.59% | 0.29% | 0.29% |
| TAU-Marutham Bold | 11 | 0.58% | 0.58% | 0.58% | 0.58% |
| TAU-Marutham Italic | 11 | 3.78% | 3.24% | 0.54% | 0.54% |
| TAU-Mullai | 11 | 9.63% | 7.64% | 4.98% | 3.65% |
| TAU-Mullai Bold | 11 | 0.66% | 0.33% | 0.66% | 0.66% |
| TAU-Mullai Italic | 11 | 13.3% | 18.35% | 1.6% | 1.6% |
| TAU-Neythal | 11 | 14.8% | 19.08% | 1.32% | 1.64% |
| TAU-Neythal Bold | 11 | 11.76% | 12.35% | 0.88% | 1.18% |
| TAU-Neythal Italic | 11 | 47.6% | 53.08% | 3.77% | 4.45% |
| TAU-Nilavu | 11 | 13.97% | 10.48% | 1.27% | 1.27% |
| TAU-Nilavu Bold | 11 | 10.94% | 8.07% | 1.56% | 1.56% |
| TAU-Nilavu Italic | 11 | 21.59% | 26.48% | 0.77% | 0.51% |
| TAU-Paalai Bold | 11 | 2.08% | 0.78% | 0.26% | 0.26% |
| TAU-Paalai Italic | 11 | 9.5% | 10.06% | 7.26% | 7.26% |
| TAU-Urai Bold | 11 | 0.97% | 0.0% | 0.97% | 0.97% |
| TAU-Urai Italic | 11 | 11.22% | 8.91% | 1.32% | 1.32% |
| TAU-Valluvar | 11 | 0.65% | 0.97% | 0.0% | 0.0% |
| TAU-Valluvar Bold | 11 | 1.05% | 0.52% | 0.0% | 0.0% |
| TAU-Valluvar BoldItalic | 11 | 3.13% | 3.42% | 0.85% | 1.14% |
| TAU-Valluvar Italic | 11 | 12.29% | 11.06% | 8.11% | 7.62% |
| TAU-kaviri | 11 | 7.26% | 6.99% | 1.08% | 0.81% |
| TAU-kollidam | 11 | 8.47% | 5.54% | 0.33% | 0.98% |
| TAU-palar | 11 | 35.64% | 37.09% | 32.36% | 30.91% |
| TAU-ponni | 11 | 7.25% | 5.22% | 1.45% | 1.45% |
| TAU-porunai | 11 | 11.37% | 12.32% | 9.48% | 9.48% |
| TAU-pothigai | 11 | 3.86% | 3.86% | 1.54% | 1.54% |
| TAU-thamirabarani | 11 | 0.33% | 0.33% | 0.33% | 0.33% |
| TSCu_Times | 11 | 2.36% | 2.36% | 1.05% | 0.79% |
| ThiruValluvar Bold | 11 | 0.69% | 1.38% | 0.34% | 0.34% |
| ThiruValluvar Bold Italic | 11 | 2.32% | 2.03% | 1.45% | 1.16% |
| ThiruValluvar Italic | 11 | 1.01% | 1.26% | 0.25% | 0.25% |
| ThiruValluvar Regular | 11 | 4.78% | 3.18% | 0.96% | 0.96% |
| Tiro Tamil Italic | 11 | 2.53% | 2.53% | 0.28% | 0.28% |
| Tiro Tamil Regular | 11 | 0.0% | 0.34% | 0.34% | 0.34% |
| Uni Ila.Sundaram-01 | 11 | 0.29% | 0.0% | 0.29% | 0.0% |
| Uni Ila.Sundaram-02 | 11 | 8.31% | 4.65% | 0.33% | 0.33% |
| Uni Ila.Sundaram-03 | 11 | 0.32% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-04 | 11 | 1.57% | 0.52% | 0.0% | 0.0% |
| Uni Ila.Sundaram-05 | 11 | 7.46% | 9.55% | 0.0% | 0.0% |
| Uni Ila.Sundaram-06 | 11 | 14.53% | 13.66% | 0.0% | 0.0% |
| Uni Ila.Sundaram-07 | 11 | 0.0% | 0.0% | 0.32% | 0.32% |
| Uni Ila.Sundaram-08 | 11 | 4.52% | 8.19% | 1.13% | 1.13% |
| Uni Ila.Sundaram-09 | 11 | 23.88% | 29.4% | 2.89% | 2.89% |
| Uni Ila.Sundaram-10 | 11 | 1.6% | 1.07% | 0.0% | 0.0% |
| Uni Ila.Sundaram-11 | 11 | 0.33% | 0.0% | 0.0% | 0.0% |
| Uni Ila.Sundaram-12 | 11 | 2.74% | 2.74% | 0.55% | 0.55% |
| Uni Ila.Sundaram-13 | 11 | 3.22% | 4.39% | 0.0% | 0.0% |
| Uni Ila.Sundaram-14 | 11 | 1.39% | 1.74% | 0.35% | 0.35% |
| Uni Ila.Sundaram-15 | 11 | 13.44% | 17.7% | 0.33% | 0.33% |
| Uni Ila.Sundaram-16 | 11 | 40.61% | 41.71% | 11.88% | 11.6% |
| Uni Ila.Sundaram-17 | 11 | 1.12% | 1.49% | 0.0% | 0.0% |
| Uni Ila.Sundaram-18 | 11 | 11.31% | 11.93% | 1.53% | 1.53% |
| Uni Ila.Sundaram-19 | 11 | 8.65% | 12.74% | 0.48% | 0.72% |
| Uni Ila.Sundaram-20 | 11 | 11.48% | 8.76% | 2.11% | 1.81% |
| uniAmma-10 | 11 | 25.07% | 36.09% | 6.61% | 6.61% |
| uniAmma-11 | 11 | 14.81% | 13.89% | 9.57% | 9.57% |
| uniAmma-16 | 11 | 5.01% | 0.88% | 0.59% | 0.59% |

## Top confusions: start (tam, best)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 188 |
| ◌ு (U+0BC1) | ∅ | 97 |
| ◌ி (U+0BBF) | ∅ | 94 |
| ட | ∅ | 81 |
| க | ∅ | 74 |
| ␠ | ∅ | 64 |
| ப | ∅ | 60 |
| ◌ி (U+0BBF) | ◌ீ (U+0BC0) | 60 |
| ர | ற | 59 |
| ◌ெ (U+0BC6) | ∅ | 52 |
| த | க | 51 |
| த | ∅ | 50 |
| ர | ∅ | 47 |
| வ | ∅ | 47 |
| ச | ∅ | 46 |

## Top confusions: installed tam

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 142 |
| ◌ு (U+0BC1) | ∅ | 85 |
| ◌ி (U+0BBF) | ∅ | 79 |
| க | ∅ | 70 |
| ட | ∅ | 67 |
| ␠ | ∅ | 62 |
| ◌ி (U+0BBF) | ◌ீ (U+0BC0) | 56 |
| ∅ | ␠ | 48 |
| த | ∅ | 47 |
| இ | ஒ | 44 |
| ◌ு (U+0BC1) | ◌ூ (U+0BC2) | 43 |
| ◌ா (U+0BBE) | ∅ | 39 |
| வ | ∅ | 39 |
| ◌ி (U+0BBF) | ◌் (U+0BCD) | 39 |
| ல | ∅ | 38 |

## Top confusions: new (best/float)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 121 |
| ␠ | ∅ | 54 |
| க | ∅ | 51 |
| ◌ு (U+0BC1) | ∅ | 44 |
| ◌ி (U+0BBF) | ∅ | 39 |
| ப | ∅ | 30 |
| ∅ | ␠ | 30 |
| ல | ∅ | 26 |
| ட | ∅ | 25 |
| த | ∅ | 25 |
| ◌ா (U+0BBE) | ∅ | 24 |
| ள | ∅ | 20 |
| " | ” | 20 |
| ர | ∅ | 19 |
| ◌ை (U+0BC8) | ∅ | 18 |

## Top confusions: new (fast/int)

| Truth | OCR | Count |
|---|---|---:|
| ◌் (U+0BCD) | ∅ | 118 |
| ␠ | ∅ | 52 |
| க | ∅ | 51 |
| ◌ு (U+0BC1) | ∅ | 44 |
| ◌ி (U+0BBF) | ∅ | 41 |
| ப | ∅ | 31 |
| ல | ∅ | 26 |
| ∅ | ␠ | 26 |
| ட | ∅ | 25 |
| த | ∅ | 24 |
| ◌ா (U+0BBE) | ∅ | 23 |
| ள | ∅ | 21 |
| ர | ∅ | 20 |
| ◌ி (U+0BBF) | ◌் (U+0BCD) | 20 |
| " | ” | 19 |
