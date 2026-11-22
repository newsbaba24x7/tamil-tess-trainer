# Error analysis: 2854 real test lines, 114,024 characters, 12,685 words

## 1. Character errors by class (share of all reference characters, i.e. CER points)

| class | r4a0.5: CER pts (sub/del/ins) | v3: CER pts (sub/del/ins) |
|---|---:|---:|
| quote | 0.25 (29/238/17) | 0.10 (26/61/30) |
| consonant | 0.21 (139/78/24) | 0.26 (167/94/39) |
| space | 0.12 (4/96/42) | 0.12 (5/99/36) |
| vowel sign | 0.11 (58/47/19) | 0.11 (63/47/18) |
| period/comma | 0.09 (29/56/15) | 0.10 (30/62/17) |
| pulli ் | 0.05 (12/25/15) | 0.06 (17/37/18) |
| other | 0.03 (28/6/0) | 0.03 (28/6/0) |
| Latin letter | 0.02 (22/4/2) | 0.03 (28/8/2) |
| ASCII digit | 0.02 (10/14/2) | 0.02 (9/16/1) |
| vowel/aytham | 0.02 (13/9/1) | 0.02 (17/9/1) |
| hyphen/dash | 0.02 (2/16/2) | 0.02 (4/12/3) |
| other punctuation | 0.01 (7/4/3) | 0.01 (7/5/3) |
| Tamil numeral/symbol | 0.00 (1/1/0) | 0.00 (1/1/0) |
| **all** | **0.96** | **0.90** |

### CER / WER if a whole class of errors were fixed (both sides stripped of that class)

| scenario | r4a0.5 CER / WER | v3 CER / WER |
|---|---:|---:|
| as measured | 0.96 / 6.98 | 0.90 / 6.26 |
| spaces ignored | 0.91 / 6.98 (WER as measured) | 0.85 / 6.26 (WER as measured) |
| quotes ignored | 0.71 / 4.95 | 0.80 / 5.42 |
| all punctuation ignored | 0.59 / 4.00 | 0.68 / 4.48 |
| Tamil letters only | 0.51 / 3.49 | 0.60 / 3.99 |

## 2. Most frequent errors — r4a0.5

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| "'" → (missing) | 232 |   | "'" → (missing) | 232 |
| ' ' → (missing) | 97 |   | ' ' → (missing) | 96 |
| '.' → (missing) | 47 |   | '.' → (missing) | 47 |
| (extra) → ' ' | 44 |   | (extra) → ' ' | 42 |
| '❍' → 'o' | 18 |   | '்' → (missing) | 25 |
| '-' → (missing) | 16 |   | 'க' → 'ச' | 20 |
| "'" → '"' | 15 |   | '❍' → 'o' | 18 |
| ',' → '.' | 14 |   | '-' → (missing) | 16 |
| 'க்' → 'ச்' | 13 |   | (extra) → '்' | 15 |
| (extra) → '"' | 13 |   | "'" → '"' | 15 |
| (extra) → '.' | 10 |   | ',' → '.' | 14 |
| ',' → (missing) | 9 |   | 'ு' → (missing) | 13 |
| '.' → ',' | 9 |   | 'த' → (missing) | 13 |
| 'லு' → 'னு' | 8 |   | (extra) → '"' | 13 |
| (extra) → 'ர' | 6 |   | 'ச' → (missing) | 12 |
| '"' → (missing) | 6 |   | 'ா' → (missing) | 11 |
| '1' → (missing) | 6 |   | 'ம' → (missing) | 10 |
| '❍' → (missing) | 6 |   | (extra) → '.' | 10 |
| '"' → '“' | 6 |   | ',' → (missing) | 9 |
| (extra) → ',' | 5 |   | '.' → ',' | 9 |
| (extra) → 'பெ' | 5 |   | 'ல' → (missing) | 9 |
| 'பௌ' → 'ள' | 5 |   | 'ி' → (missing) | 9 |
| 'ம்' → (missing) | 4 |   | 'ர' → (missing) | 9 |
| 'தி' → (missing) | 4 |   | (extra) → 'ு' | 8 |
| 'ரா' → 'ர' | 4 |   | 'ல' → 'ன' | 8 |
| '1' → '7' | 4 |   | 'க' → (missing) | 8 |
| '9' → (missing) | 4 |   | (extra) → 'ர' | 7 |
| '❍' → 'O' | 4 |   | '"' → (missing) | 6 |
| 'ங்' → 'ந்' | 4 |   | '1' → (missing) | 6 |
| 'க' → 'ச' | 4 |   | '❍' → (missing) | 6 |

## 2. Most frequent errors — v3

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| ' ' → (missing) | 99 |   | ' ' → (missing) | 99 |
| "'" → (missing) | 52 |   | "'" → (missing) | 53 |
| '.' → (missing) | 51 |   | '.' → (missing) | 52 |
| (extra) → ' ' | 36 |   | '்' → (missing) | 37 |
| (extra) → "'" | 18 |   | (extra) → ' ' | 36 |
| ',' → '.' | 15 |   | 'க' → 'ச' | 23 |
| 'க்' → 'ச்' | 14 |   | (extra) → '்' | 18 |
| '-' → (missing) | 12 |   | (extra) → "'" | 18 |
| '❍' → '0' | 12 |   | 'த' → (missing) | 16 |
| "'" → '"' | 11 |   | 'ம' → (missing) | 15 |
| (extra) → '"' | 11 |   | 'ு' → (missing) | 15 |
| (extra) → '.' | 11 |   | ',' → '.' | 15 |
| 'லு' → 'னு' | 11 |   | 'ர' → (missing) | 12 |
| ',' → (missing) | 10 |   | 'ல' → 'ன' | 12 |
| '❍' → 'o' | 9 |   | '-' → (missing) | 12 |
| '"' → (missing) | 8 |   | 'ச' → (missing) | 12 |
| (extra) → 'ர' | 7 |   | '❍' → '0' | 12 |
| '.' → ',' | 7 |   | (extra) → '"' | 11 |
| '1' → (missing) | 7 |   | (extra) → '.' | 11 |
| (extra) → ',' | 6 |   | ',' → (missing) | 10 |
| '❍' → (missing) | 6 |   | (extra) → 'ர' | 10 |
| 'க' → 'ச' | 6 |   | 'ி' → (missing) | 10 |
| 'தி' → (missing) | 5 |   | "'" → '"' | 10 |
| 'ன்' → 'ன' | 5 |   | (extra) → 'ு' | 9 |
| 'க்' → 'க' | 5 |   | 'ா' → (missing) | 9 |
| '1' → '7' | 5 |   | '❍' → 'o' | 9 |
| (extra) → 'ள' | 5 |   | '"' → (missing) | 8 |
| 'மா' → (missing) | 5 |   | '.' → ',' | 7 |
| 'த்' → (missing) | 4 |   | 'ட' → (missing) | 7 |
| 'த' → (missing) | 4 |   | '1' → (missing) | 7 |

## 3. Words — r4a0.5

| word error kind | count | share of word errors |
|---|---:|---:|
| letters | 390 | 44% |
| punctuation only | 352 | 40% |
| word missing (often merged with a neighbour) | 96 | 11% |
| extra word (often a word split by a space) | 48 | 5% |

Most often misread words (truth → one OCR example):

❍ → 14o (24×), சு. → வ.வே.சு. (9×), தராசு → தரர்சு (8×), கொண்டு → அறிந்துகொண்டு (4×), வின் → நா.வா.வின் (3×), போல → போ (2×), தராசு:- → :- (2×), சுவாமி → ஸ்வாமி (2×), ? → விரைவாய்......7 (2×), - → ஒவியர், (2×), பலவிதமான → பல்விதமான (1×), கட்சிகளையும் → கட்சிக்ளையும் (1×), கொண்டிருப்பது → சொல்லிக்கொண்டிருப்பது (1×), துன்பமென்றும் → துன்பமென்று (1×), பெரியதோர் → பேற்றுததோர் (1×), நன்மைக்குறியென்பது → நன்னைச்குற்ம்ன்பது (1×), விளையாட்டுப் → ஷிகைமாய்டுப் (1×), குடியரசு → குடியாசு (1×), பக்கம் → புக்கம் (1×), ஸேனாபலம் → இஸேனாபலம் (1×), அந்தக் → அந்தத் (1×), இங்கிலிஷ்காரர் → இவ்கிலீஷ்காரர் (1×), ஊயரே, → ஐயரே, (1×), சம்மா → சும்மா (1×), அப்படியில்லை. → நதி (1×)

## 4. Where errors concentrate — r4a0.5

- Page CER: median 0.79%, best 0.00%, worst 18.29%.
- The worst 10% of pages (16) hold 38% of all character errors.
- The worst 20% of pages (32) hold 56% of all character errors.
- The worst 50% of pages (82) hold 86% of all character errors.
- Pages under 2% CER: 134 of 164.

| line height (box) | lines' CER |
|---|---:|
| <30 px | 0.96% (114,024 chars) |

| printed | CER |
|---|---:|
| no year | 0.96% (114,024 chars) |

Worst 12 books by CER:

| book | CER | chars |
|---|---:|---:|
| ? | 1.0% | 114,024 |

## 5. Letters whose shape changed in the 1978 reform — r4a0.5

Recovered 1296 of 1301 (99.6%). Most often missed: ளை (1), னா (1), னை (1), றோ (1), லை (1)

## 6. Lines with CER over 30% — r4a0.5 (likely crop or ground-truth problems)

14 lines (0.5%) hold 16% of the character errors. Examples:

- 94% `wb_3b71a11e37_p0010_009`  truth: கொள்ளலாமா? ௸ தீர்மானத்திலிருந்து முரணிச் செல்லச்  |  OCR: அ ரி
- 80% `wb_05f33f0963_p0051_000`  truth: தராசு  |  OCR: 5ர௬
- 70% `wb_3b71a11e37_p0005_026`  truth: 1919-ம் ஆண்டில் மான்ட் போர்டு சீர்திருத்தச் சட்டம்  |  OCR: பய அன்ட் பல் போடு வக்கம்
- 60% `wb_05f33f0963_p0039_000`  truth: தராசு  |  OCR: தர ௩௬
- 48% `wb_05f33f0963_p0019_007`  truth: அப்படியில்லை. அந்த சாஸ்திரத்திலே நம்மைக்  |  OCR: தப்பரமிகலை, நதி ன்ஸ் நாத்தி நம்ல்க்
- 40% `wb_05f33f0963_p0027_000`  truth: தராசு  |  OCR: தரர்சு
- 40% `wb_05f33f0963_p0031_000`  truth: தராசு  |  OCR: தரர்சு
- 40% `wb_05f33f0963_p0067_000`  truth: தராசு  |  OCR: கரசு
- 40% `wb_05f33f0963_p0079_000`  truth: தராசு  |  OCR: தரா
- 39% `wb_3b71a11e37_p0003_027`  truth: அழைக்கவுமே யென்பதை திராவிடர் கழகம் அனுசரித்தது  |  OCR: முக்கள் பென்ப ரொடிடர் பகம் அனரித்தது
