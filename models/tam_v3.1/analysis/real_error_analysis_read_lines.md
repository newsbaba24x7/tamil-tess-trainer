_140 lines that every model returned empty are left out._

# Error analysis: 3828 real test lines, 162,118 characters, 18,435 words

## 1. Character errors by class (share of all reference characters, i.e. CER points)

| class | v31_best: CER pts (sub/del/ins) | v3_best: CER pts (sub/del/ins) | v31_fast: CER pts (sub/del/ins) |
|---|---:|---:|---:|
| consonant | 0.26 (262/107/53) | 0.32 (321/118/80) | 0.63 (555/307/161) |
| space | 0.19 (3/74/237) | 0.16 (1/83/168) | 0.28 (17/55/379) |
| period/comma | 0.17 (90/108/77) | 0.18 (92/120/72) | 0.28 (135/210/105) |
| vowel sign | 0.15 (136/67/40) | 0.16 (133/78/44) | 0.55 (526/294/75) |
| quote | 0.12 (19/151/26) | 0.08 (16/78/34) | 0.31 (282/139/86) |
| pulli ் | 0.05 (13/50/25) | 0.06 (13/60/31) | 0.13 (57/88/63) |
| vowel/aytham | 0.05 (48/14/11) | 0.05 (67/10/9) | 0.11 (107/35/34) |
| other punctuation | 0.04 (24/16/21) | 0.04 (21/20/16) | 0.09 (65/28/53) |
| Latin letter | 0.03 (35/3/3) | 0.03 (44/4/2) | 0.04 (32/5/27) |
| ASCII digit | 0.02 (19/10/8) | 0.02 (14/12/14) | 0.08 (87/20/15) |
| hyphen/dash | 0.02 (7/14/9) | 0.01 (3/12/6) | 0.07 (78/18/19) |
| other | 0.01 (6/3/1) | 0.01 (6/4/4) | 0.01 (9/1/14) |
| Tamil numeral/symbol | 0.00 (2/1/1) | 0.00 (3/2/0) | 0.01 (2/0/19) |
| **all** | **1.11** | **1.12** | **2.59** |

### CER / WER if a whole class of errors were fixed (both sides stripped of that class)

| scenario | v31_best CER / WER | v3_best CER / WER | v31_fast CER / WER |
|---|---:|---:|---:|
| as measured | 1.11 / 8.36 | 1.12 / 8.23 | 2.59 / 16.66 |
| spaces ignored | 0.99 / 8.36 (WER as measured) | 1.05 / 8.23 (WER as measured) | 2.50 / 16.66 (WER as measured) |
| quotes ignored | 0.99 / 7.48 | 1.04 / 7.63 | 2.29 / 14.70 |
| all punctuation ignored | 0.77 / 5.82 | 0.83 / 6.02 | 1.89 / 11.97 |
| Tamil letters only | 0.71 / 5.57 | 0.76 / 5.68 | 1.74 / 11.23 |

## 2. Most frequent errors — v31_best

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| (extra) → ' ' | 235 |   | (extra) → ' ' | 237 |
| "'" → (missing) | 132 |   | "'" → (missing) | 132 |
| '.' → (missing) | 86 |   | '.' → (missing) | 86 |
| ' ' → (missing) | 72 |   | ' ' → (missing) | 74 |
| (extra) → '.' | 65 |   | (extra) → '.' | 66 |
| ',' → '.' | 62 |   | ',' → '.' | 62 |
| ',' → (missing) | 21 |   | '்' → (missing) | 50 |
| '"' → (missing) | 19 |   | (extra) → '்' | 25 |
| (extra) → "'" | 14 |   | 'ு' → (missing) | 23 |
| 'ஒ' → 'ஓ' | 14 |   | ',' → (missing) | 22 |
| '.' → ',' | 13 |   | 'ந' → 'த' | 20 |
| '-' → (missing) | 13 |   | '"' → (missing) | 19 |
| (extra) → ',' | 11 |   | (extra) → 'ர' | 17 |
| 'ன்' → 'ள்' | 10 |   | 'ச' → (missing) | 16 |
| (extra) → '"' | 10 |   | '-' → (missing) | 14 |
| 'ஓ' → 'ஒ' | 9 |   | (extra) → "'" | 14 |
| (extra) → '-' | 9 |   | 'ஒ' → 'ஓ' | 14 |
| (extra) → 'ப' | 8 |   | '.' → ',' | 13 |
| ';' → ':' | 8 |   | 'ா' → (missing) | 12 |
| 'ந்' → 'த்' | 7 |   | 'க' → 'ச' | 12 |
| '1' → (missing) | 7 |   | 'ன' → 'ள' | 12 |
| (extra) → 'க' | 7 |   | (extra) → ',' | 11 |
| (extra) → 'ர' | 7 |   | 'ல' → 'வ' | 11 |
| (extra) → '!' | 7 |   | 'க' → (missing) | 11 |
| '!' → (missing) | 7 |   | 'ி' → 'ீ' | 11 |
| 'சு' → 'க' | 7 |   | 'வ' → 'ல' | 11 |
| '-' → ' ' | 6 |   | 'ர' → (missing) | 10 |
| 'க' → 'சு' | 6 |   | 'வ' → (missing) | 10 |
| 'ந' → 'த' | 6 |   | (extra) → 'ு' | 10 |
| 'ன' → (missing) | 6 |   | (extra) → '"' | 10 |

## 2. Most frequent errors — v3_best

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| (extra) → ' ' | 165 |   | (extra) → ' ' | 168 |
| '.' → (missing) | 97 |   | '.' → (missing) | 97 |
| ' ' → (missing) | 82 |   | ' ' → (missing) | 83 |
| ',' → '.' | 68 |   | ',' → '.' | 68 |
| (extra) → '.' | 60 |   | (extra) → '.' | 60 |
| "'" → (missing) | 53 |   | '்' → (missing) | 60 |
| (extra) → "'" | 26 |   | "'" → (missing) | 54 |
| 'ஓ' → 'ஒ' | 25 |   | (extra) → '்' | 31 |
| '"' → (missing) | 24 |   | 'ந' → 'த' | 27 |
| ',' → (missing) | 20 |   | 'ு' → (missing) | 27 |
| '-' → (missing) | 12 |   | (extra) → "'" | 26 |
| (extra) → ',' | 12 |   | 'ஓ' → 'ஒ' | 25 |
| 'ன்' → 'ள்' | 12 |   | '"' → (missing) | 24 |
| (extra) → 'த' | 11 |   | ',' → (missing) | 23 |
| '.' → ',' | 10 |   | 'ல' → 'வ' | 22 |
| 'க' → 'சு' | 10 |   | 'வ' → 'ல' | 17 |
| (extra) → 'ப' | 10 |   | 'ச' → (missing) | 16 |
| 'ஒ' → 'ஓ' | 10 |   | 'க' → 'ச' | 16 |
| 'ல' → 'வ' | 9 |   | (extra) → 'ச' | 15 |
| 'ந' → 'த' | 9 |   | 'ன' → 'ள' | 15 |
| '1' → (missing) | 8 |   | (extra) → 'ு' | 15 |
| 'வி' → 'லி' | 8 |   | 'க' → (missing) | 15 |
| (extra) → '"' | 7 |   | (extra) → 'ர' | 15 |
| 'ன' → (missing) | 7 |   | 'ா' → (missing) | 14 |
| 'சு' → 'க' | 7 |   | '-' → (missing) | 12 |
| (extra) → '!' | 7 |   | 'த' → (missing) | 12 |
| 'ந்' → 'த்' | 6 |   | (extra) → ',' | 12 |
| '"' → "'" | 6 |   | 'ி' → (missing) | 12 |
| 'ப' → 'பு' | 6 |   | '.' → ',' | 10 |
| (extra) → '-' | 6 |   | 'ம' → (missing) | 10 |

## 2. Most frequent errors — v31_fast

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| (extra) → ' ' | 388 |   | (extra) → ' ' | 379 |
| '.' → (missing) | 173 |   | '.' → (missing) | 182 |
| '"' → '“' | 117 |   | '"' → '“' | 120 |
| (extra) → '.' | 90 |   | 'ு' → (missing) | 106 |
| "'" → (missing) | 82 |   | (extra) → '.' | 89 |
| ' ' → (missing) | 54 |   | '்' → (missing) | 88 |
| '"' → (missing) | 53 |   | "'" → (missing) | 85 |
| '.' → ',' | 52 |   | (extra) → '்' | 63 |
| (extra) → 'க' | 50 |   | ' ' → (missing) | 55 |
| '"' → '”' | 48 |   | '"' → (missing) | 54 |
| '-' → '–' | 45 |   | 'ா' → (missing) | 52 |
| ',' → '.' | 45 |   | '.' → ',' | 52 |
| "'" → '‘' | 36 |   | '"' → '”' | 48 |
| (extra) → 'த' | 35 |   | ',' → '.' | 45 |
| (extra) → 'ப' | 31 |   | '-' → '–' | 44 |
| ',' → (missing) | 28 |   | "'" → '‘' | 38 |
| ';' → ':' | 25 |   | 'த' → (missing) | 34 |
| (extra) → '“' | 24 |   | (extra) → 'க' | 33 |
| 'து' → 'த' | 24 |   | 'க' → (missing) | 33 |
| (extra) → '‘' | 23 |   | 'ம' → (missing) | 32 |
| '-' → '—' | 21 |   | 'ி' → (missing) | 31 |
| (extra) → "'" | 20 |   | 'ை' → (missing) | 30 |
| (extra) → 'ல' | 20 |   | 'ச' → (missing) | 29 |
| (extra) → 'ட' | 18 |   | (extra) → 'ர' | 28 |
| "'" → '’' | 18 |   | ',' → (missing) | 28 |
| 'பெ' → 'ப' | 17 |   | 'ர' → (missing) | 27 |
| '-' → (missing) | 17 |   | 'ா' → 'ர' | 26 |
| 'எ' → 'ஏ' | 16 |   | ';' → ':' | 25 |
| (extra) → ',' | 16 |   | 'ு' → 'ூ' | 25 |
| (extra) → 'ன' | 16 |   | 'வ' → 'ல' | 24 |

## 3. Words — v31_best

| word error kind | count | share of word errors |
|---|---:|---:|
| letters | 784 | 51% |
| punctuation only | 412 | 27% |
| extra word (often a word split by a space) | 275 | 18% |
| word missing (often merged with a neighbour) | 71 | 5% |

Most often misread words (truth → one OCR example):

நீ → ந் (4×), ; → பெற்றது; (3×), நமது → நம்து (3×), love) → Iosd) (2×), ஓர் → ஒர் (2×), ஒரு → i (2×), தான் → உடலிலேயேதான் (2×), பல → 100 (2×), என்று → எனறு (2×), 90 → 9/) (2×), "இல்லே → சரிப்படாது. (1×), சரிப்படாது-வருத்தப்படாதீக → வருத்தப்படாதீக (1×), ஏன்? → ஏbi (1×), கண்ணாடி → கன்னாடி (1×), வாழ்வை-உணர்வு → - (1×), வாழ்வை-அகம் → அகம் (1×), (Subnormal → (Suhnornral (1×), (Abnormal → (Abuonual (1×), பரந்துப்பட்ட → பட்ட (1×), என → ஏன (1×), சிறந்த → சிறத்த (1×), நுழைதியோ → தி (1×), - → யோ. (1×), 115 → I7 (1×), நீஏன் → ஏன் (1×)

## 4. Where errors concentrate — v31_best

- Page CER: median 0.93%, best 0.00%, worst 12.43%.
- The worst 10% of pages (19) hold 28% of all character errors.
- The worst 20% of pages (39) hold 48% of all character errors.
- The worst 50% of pages (98) hold 81% of all character errors.
- Pages under 2% CER: 155 of 196.

| line height (box) | lines' CER |
|---|---:|
| <30 px | 1.47% (407 chars) |
| 30–39 px | 0.64% (4,243 chars) |
| 40–49 px | 0.94% (11,903 chars) |
| ≥50 px | 1.13% (145,565 chars) |

| printed | CER |
|---|---:|
| no year | 1.11% (162,118 chars) |

Worst 12 books by CER:

| book | CER | chars |
|---|---:|---:|
| உணர்வின் எல்லை.pdf | 11.7% | 453 |
| சின்னஞ் சிறு பெண் (மொழிபெயர்ப்பு).pdf | 6.7% | 726 |
| எல்லோரும் இந்நாட்டு மன்னர்.pdf | 5.2% | 324 |
| கரை மணலும் காகித ஓடமும்.pdf | 4.9% | 445 |
| தமிழ்நாட்டில் சாதி சமத்துவப் போராட்டம்.pdf | 4.5% | 352 |
| பாரதிதாசன் பரம்பரை.pdf | 4.3% | 460 |
| தமிழர் வரலாறு 2, பி. டி. சீனிவாச அய்யங்கார்.pdf | 4.1% | 366 |
| கோயில் மணி.pdf | 3.9% | 461 |
| மயிலை சீனி. வேங்கடசாமி ஆய்வுக் களஞ்சியம் 6.pdf | 3.9% | 1,037 |
| ஆரியர்க்கு முற்பட்ட தமிழ்ப்பண்பாடு.pdf | 3.4% | 676 |
| வழிப்போக்கன்.pdf | 3.1% | 643 |
| நித்திலவல்லி.pdf | 3.0% | 833 |

## 5. Letters whose shape changed in the 1978 reform — v31_best

Recovered 1946 of 1962 (99.2%). Most often missed: லை (6), னை (6), ளை (2), ணா (1), னா (1)

## 6. Lines with CER over 30% — v31_best (likely crop or ground-truth problems)

8 lines (0.2%) hold 5% of the character errors. Examples:

- 129% `ws_70df19151d_p0101_003`  truth: கண்கள்.  |  OCR: 446597௧௭7.
- 100% `ws_18b9d4c4a1_p0109_010`  truth: வாழ்வு நாளடைவில் தொலைய வழிகோலியது ; ஒரு  |  OCR: i
- 62% `ws_d40807f8d1_p0306_020`  truth: கொண்டே.]  |  OCR: கொண்டே] த த
- 62% `ws_d95881d2f4_p0056_000`  truth: மேடைப் பேச்சு 47  |  OCR: டப் 47
- 57% `ws_dc69dd69eb_p0044_008`  truth: சமமானவை  |  OCR: மம னல
- 50% `ws_42d8503698_p0019_031`  truth: கெ-3  |  OCR: கௌ 3
- 40% `ws_1eed874bd5_p0174_002`  truth: நாட்களில்.  |  OCR: நாட்களில். க வ
- 30% `ws_2c9d5a533a_p0075_013`  truth: வந்தன. குடியானவர்கள் பல இடங்களில்  |  OCR: வெந்த? தடியான் வர்கள் 100 இடங்களில்
