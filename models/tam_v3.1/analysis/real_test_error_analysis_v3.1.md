# Error analysis: 3968 real test lines, 168,582 characters, 19,178 words

## 1. Character errors by class (share of all reference characters, i.e. CER points)

| class | v31_best: CER pts (sub/del/ins) | v31_std: CER pts (sub/del/ins) | v31_fast: CER pts (sub/del/ins) | v3_best: CER pts (sub/del/ins) |
|---|---:|---:|---:|---:|
| consonant | 0.25 (273/88/56) | 0.28 (254/155/64) | 0.37 (340/201/78) | 0.35 (408/109/81) |
| period/comma | 0.18 (101/103/96) | 0.17 (88/92/103) | 0.24 (108/153/144) | 0.18 (105/107/87) |
| vowel sign | 0.16 (156/67/39) | 0.17 (148/98/40) | 0.23 (210/135/49) | 0.17 (143/87/58) |
| space | 0.13 (7/88/120) | 0.15 (12/92/143) | 0.13 (14/100/97) | 0.11 (6/89/88) |
| quote | 0.06 (20/42/47) | 0.06 (21/40/48) | 0.09 (31/72/51) | 0.08 (24/66/40) |
| vowel/aytham | 0.04 (54/4/15) | 0.05 (56/6/17) | 0.06 (71/15/13) | 0.05 (71/6/15) |
| pulli ் | 0.04 (11/36/25) | 0.06 (18/52/24) | 0.08 (20/60/48) | 0.06 (18/45/38) |
| other punctuation | 0.03 (20/17/19) | 0.03 (19/18/19) | 0.05 (35/29/18) | 0.04 (32/11/20) |
| Latin letter | 0.03 (39/7/0) | 0.02 (37/4/1) | 0.02 (32/2/6) | 0.03 (44/3/1) |
| ASCII digit | 0.03 (19/8/19) | 0.03 (15/7/28) | 0.04 (26/9/36) | 0.04 (18/13/32) |
| hyphen/dash | 0.02 (8/21/5) | 0.02 (9/18/6) | 0.02 (10/16/7) | 0.02 (7/16/7) |
| other | 0.01 (6/5/0) | 0.01 (7/4/0) | 0.01 (12/3/2) | 0.01 (8/3/3) |
| Tamil numeral/symbol | 0.00 (2/1/0) | 0.00 (2/1/0) | 0.00 (1/0/1) | 0.00 (2/2/0) |
| **all** | **0.98** | **1.05** | **1.34** | **1.13** |

### CER / WER if a whole class of errors were fixed (both sides stripped of that class)

| scenario | v31_best CER / WER | v31_std CER / WER | v31_fast CER / WER | v3_best CER / WER |
|---|---:|---:|---:|---:|
| as measured | 0.98 / 6.90 | 1.05 / 7.04 | 1.34 / 8.36 | 1.13 / 7.94 |
| spaces ignored | 0.93 / 6.90 (WER as measured) | 0.99 / 7.04 (WER as measured) | 1.32 / 8.36 (WER as measured) | 1.12 / 7.94 (WER as measured) |
| quotes ignored | 0.91 / 6.42 | 0.98 / 6.56 | 1.25 / 7.71 | 1.06 / 7.36 |
| all punctuation ignored | 0.68 / 4.75 | 0.76 / 4.95 | 0.95 / 5.67 | 0.83 / 5.69 |
| Tamil letters only | 0.63 / 4.51 | 0.70 / 4.69 | 0.87 / 5.32 | 0.76 / 5.37 |

## 2. Most frequent errors — v31_best

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| (extra) → ' ' | 118 |   | (extra) → ' ' | 120 |
| ' ' → (missing) | 87 |   | ' ' → (missing) | 88 |
| (extra) → '.' | 82 |   | (extra) → '.' | 83 |
| '.' → (missing) | 78 |   | '.' → (missing) | 80 |
| ',' → '.' | 69 |   | ',' → '.' | 69 |
| (extra) → "'" | 37 |   | (extra) → "'" | 37 |
| ',' → (missing) | 23 |   | '்' → (missing) | 36 |
| "'" → (missing) | 22 |   | 'ு' → (missing) | 30 |
| '-' → (missing) | 21 |   | (extra) → '்' | 25 |
| '.' → ',' | 19 |   | ',' → (missing) | 23 |
| '"' → (missing) | 19 |   | "'" → (missing) | 22 |
| 'ஒ' → 'ஓ' | 18 |   | '-' → (missing) | 21 |
| (extra) → ',' | 13 |   | '"' → (missing) | 20 |
| 'ஓ' → 'ஒ' | 10 |   | '.' → ',' | 19 |
| 'சு' → 'க' | 10 |   | 'ஒ' → 'ஓ' | 18 |
| (extra) → '"' | 9 |   | 'ச' → (missing) | 15 |
| '!' → (missing) | 9 |   | (extra) → 'ர' | 14 |
| '"' → "'" | 8 |   | 'ல' → 'வ' | 14 |
| 'ன்' → 'ள்' | 8 |   | 'க' → (missing) | 14 |
| '-' → ' ' | 7 |   | 'ந' → 'த' | 14 |
| (extra) → 'க' | 7 |   | (extra) → ',' | 13 |
| (extra) → '!' | 7 |   | 'ன' → 'ள' | 13 |
| 'ரி' → 'ர்' | 6 |   | 'க' → 'த' | 12 |
| 'ல' → 'ல்' | 6 |   | 'ி' → '்' | 12 |
| 'ன' → 'னா' | 6 |   | 'ா' → (missing) | 11 |
| 'லி' → 'வி' | 5 |   | 'ூ' → 'ு' | 11 |
| 'து' → 'தூ' | 5 |   | 'ி' → 'ீ' | 11 |
| 'று' → 'ற' | 5 |   | 'ச' → 'க' | 11 |
| (extra) → 'ம' | 5 |   | (extra) → 'ு' | 10 |
| ';' → ':' | 5 |   | 'ி' → 'ு' | 10 |

## 2. Most frequent errors — v31_std

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| (extra) → ' ' | 142 |   | (extra) → ' ' | 143 |
| ' ' → (missing) | 88 |   | ' ' → (missing) | 92 |
| (extra) → '.' | 87 |   | (extra) → '.' | 88 |
| '.' → (missing) | 70 |   | '.' → (missing) | 71 |
| ',' → '.' | 55 |   | ',' → '.' | 55 |
| (extra) → "'" | 38 |   | '்' → (missing) | 52 |
| "'" → (missing) | 21 |   | (extra) → "'" | 38 |
| ',' → (missing) | 21 |   | 'ு' → (missing) | 37 |
| '.' → ',' | 20 |   | 'க' → (missing) | 29 |
| '"' → (missing) | 19 |   | (extra) → '்' | 24 |
| '-' → (missing) | 18 |   | "'" → (missing) | 21 |
| (extra) → ',' | 15 |   | ',' → (missing) | 21 |
| 'ஒ' → 'ஓ' | 15 |   | '.' → ',' | 20 |
| 'க' → (missing) | 11 |   | '"' → (missing) | 19 |
| 'ஓ' → 'ஒ' | 11 |   | '-' → (missing) | 18 |
| (extra) → '"' | 9 |   | 'ச' → (missing) | 17 |
| '!' → (missing) | 9 |   | 'ி' → (missing) | 16 |
| 'சு' → 'க' | 8 |   | 'ர' → (missing) | 16 |
| (extra) → '8' | 8 |   | 'ா' → (missing) | 16 |
| '"' → "'" | 7 |   | 'ந' → 'த' | 16 |
| (extra) → '!' | 7 |   | (extra) → ',' | 15 |
| '-' → ' ' | 6 |   | 'ஒ' → 'ஓ' | 15 |
| (extra) → 'ம' | 6 |   | 'த' → (missing) | 14 |
| 'ல' → 'ல்' | 6 |   | 'ல' → 'வ' | 14 |
| (extra) → '-' | 6 |   | 'ன' → 'ள' | 14 |
| (extra) → 'வ' | 6 |   | (extra) → 'ர' | 14 |
| (extra) → 'க' | 6 |   | 'ி' → 'ீ' | 13 |
| 'ன்' → 'ள்' | 6 |   | 'ள' → (missing) | 12 |
| 'ன' → 'னா' | 6 |   | 'ஓ' → 'ஒ' | 11 |
| (extra) → '2' | 6 |   | 'ூ' → 'ு' | 11 |

## 2. Most frequent errors — v31_fast

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| '.' → (missing) | 124 |   | '.' → (missing) | 127 |
| (extra) → '.' | 122 |   | (extra) → '.' | 123 |
| (extra) → ' ' | 98 |   | ' ' → (missing) | 100 |
| ' ' → (missing) | 96 |   | (extra) → ' ' | 97 |
| ',' → '.' | 52 |   | '்' → (missing) | 60 |
| "'" → (missing) | 41 |   | 'ு' → (missing) | 56 |
| (extra) → "'" | 37 |   | ',' → '.' | 52 |
| '.' → ',' | 36 |   | (extra) → '்' | 48 |
| '"' → (missing) | 28 |   | "'" → (missing) | 43 |
| ',' → (missing) | 25 |   | (extra) → "'" | 38 |
| (extra) → ',' | 21 |   | '.' → ',' | 36 |
| 'ஒ' → 'ஓ' | 18 |   | 'க' → (missing) | 31 |
| '-' → (missing) | 16 |   | 'ர' → (missing) | 30 |
| (extra) → 'க' | 14 |   | '"' → (missing) | 29 |
| 'ன்' → 'ள்' | 13 |   | ',' → (missing) | 26 |
| '"' → "'" | 12 |   | 'ச' → (missing) | 23 |
| (extra) → '"' | 12 |   | 'ன' → 'ள' | 23 |
| (extra) → '4' | 12 |   | 'ா' → (missing) | 22 |
| 'சு' → 'க' | 12 |   | (extra) → ',' | 21 |
| 'ஓ' → 'ஒ' | 11 |   | 'ி' → (missing) | 19 |
| 'க' → (missing) | 10 |   | 'ல' → 'வ' | 19 |
| (extra) → '8' | 10 |   | 'ி' → 'ீ' | 19 |
| (extra) → 'ல' | 10 |   | 'ஒ' → 'ஓ' | 18 |
| '!' → (missing) | 10 |   | 'ந' → 'த' | 18 |
| (extra) → '6' | 8 |   | '-' → (missing) | 16 |
| (extra) → 'ன' | 8 |   | 'த' → (missing) | 16 |
| ';' → ':' | 8 |   | 'க' → 'த' | 16 |
| (extra) → 'ப' | 7 |   | (extra) → 'ர' | 15 |
| 'க' → 'த' | 7 |   | 'ை' → (missing) | 13 |
| 'ன' → 'ன்' | 7 |   | 'ள' → 'ன' | 13 |

## 2. Most frequent errors — v3_best

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| ' ' → (missing) | 87 |   | ' ' → (missing) | 89 |
| (extra) → ' ' | 85 |   | (extra) → ' ' | 88 |
| '.' → (missing) | 82 |   | '.' → (missing) | 84 |
| ',' → '.' | 79 |   | ',' → '.' | 79 |
| (extra) → '.' | 76 |   | (extra) → '.' | 74 |
| "'" → (missing) | 40 |   | '்' → (missing) | 45 |
| (extra) → "'" | 30 |   | "'" → (missing) | 40 |
| '"' → (missing) | 25 |   | (extra) → '்' | 38 |
| 'ஓ' → 'ஒ' | 25 |   | 'ு' → (missing) | 31 |
| ',' → (missing) | 23 |   | (extra) → "'" | 30 |
| 'ன்' → 'ள்' | 20 |   | 'ன' → 'ள' | 28 |
| '-' → (missing) | 16 |   | '"' → (missing) | 26 |
| (extra) → ',' | 13 |   | 'ஓ' → 'ஒ' | 25 |
| (extra) → 'க' | 12 |   | 'ந' → 'த' | 24 |
| '.' → ',' | 11 |   | 'வ' → 'ல' | 24 |
| 'ஒ' → 'ஓ' | 11 |   | ',' → (missing) | 23 |
| 'வி' → 'லி' | 10 |   | 'ல' → 'வ' | 22 |
| (extra) → '"' | 9 |   | (extra) → 'ு' | 21 |
| (extra) → '8' | 9 |   | (extra) → 'ர' | 18 |
| 'க' → 'சு' | 8 |   | 'ச' → (missing) | 18 |
| 'ல' → 'வ' | 8 |   | '-' → (missing) | 16 |
| 'சு' → 'க' | 8 |   | 'க' → (missing) | 16 |
| (extra) → '!' | 8 |   | 'க' → 'ச' | 15 |
| 'ர' → (missing) | 7 |   | 'ா' → (missing) | 15 |
| '"' → "'" | 7 |   | (extra) → 'ச' | 14 |
| 'க' → 'க்' | 7 |   | 'ி' → (missing) | 14 |
| 'ப' → 'பு' | 7 |   | (extra) → ',' | 13 |
| (extra) → 'ம' | 7 |   | 'ர' → (missing) | 13 |
| (extra) → '-' | 7 |   | 'க' → 'த' | 12 |
| ';' → ':' | 7 |   | 'த' → 'க' | 12 |

## 3. Words — v31_best

| word error kind | count | share of word errors |
|---|---:|---:|
| letters | 744 | 56% |
| punctuation only | 355 | 27% |
| extra word (often a word split by a space) | 137 | 10% |
| word missing (often merged with a neighbour) | 88 | 7% |

Most often misread words (truth → one OCR example):

; → பெற்றது; (4×), வேலை → கஸ் (3×), ஒரு → ஒகு (3×), நமது → நம்து (3×), love) → Iosd) (2×), என → ஏன (2×), : → காணலாம்: (2×), என்பது → என்புது (2×), மணிபல்லவம் → மமணிபல்லவம் (2×), ? → யார்? (2×), தான் → உடலிலேயேதான் (2×), பல → பல் (2×), வெற்றி → வேற்றி (2×), மூவரும் → முவரும் (2×), நான்கு → நாள்கு (2×), என்று → என்ற (2×), கைஸ் → கைன்; (2×), இசுட்டீபன் → இசுட்டீபள் (2×), "இல்லே → சரிப்படாது. (1×), சரிப்படாது-வருத்தப்படாதீக → வருத்தப்படாதீக (1×), தம்பி?" → தம்பிசி (1×), நீரில் → குளிர்நீரில் (1×), கண்ணாடி → கன்ணாடி (1×), வாழ்வை-உணர்வு → - (1×), வாழ்வை-அகம் → அகம் (1×)

## 4. Where errors concentrate — v31_best

- Page CER: median 0.83%, best 0.00%, worst 7.51%.
- The worst 10% of pages (19) hold 33% of all character errors.
- The worst 20% of pages (39) hold 53% of all character errors.
- The worst 50% of pages (98) hold 83% of all character errors.
- Pages under 2% CER: 162 of 197.

| line height (box) | lines' CER |
|---|---:|
| <30 px | 0.98% (407 chars) |
| 30–39 px | 0.66% (4,274 chars) |
| 40–49 px | 0.81% (11,933 chars) |
| ≥50 px | 1.00% (151,968 chars) |

| printed | CER |
|---|---:|
| no year | 0.98% (168,582 chars) |

Worst 12 books by CER:

| book | CER | chars |
|---|---:|---:|
| அண்ணாவின் நாடகங்கள்.pdf | 7.5% | 346 |
| உணர்வின் எல்லை.pdf | 4.6% | 453 |
| கரை மணலும் காகித ஓடமும்.pdf | 4.5% | 579 |
| தமிழ்நாட்டில் சாதி சமத்துவப் போராட்டம்.pdf | 4.3% | 352 |
| தமிழர் வரலாறு 2, பி. டி. சீனிவாச அய்யங்கார்.pdf | 4.1% | 366 |
| தாய், மக்சீம் கார்க்கி.pdf | 4.1% | 1,277 |
| மயிலை சீனி. வேங்கடசாமி ஆய்வுக் களஞ்சியம் 6.pdf | 4.1% | 1,082 |
| குறட்செல்வம்.pdf | 4.1% | 419 |
| புறநானூற்றுச் சிறுகதைகள்.pdf | 3.5% | 769 |
| நா. பார்த்தசாரதி சிறுகதைகள் 2.pdf | 3.4% | 1,511 |
| இந்தியப் பெருங்கடல்.pdf | 3.1% | 445 |
| அகநானூறு 1, புலியூர்க் கேசிகன்.pdf | 3.1% | 747 |

## 5. Letters whose shape changed in the 1978 reform — v31_best

Recovered 2027 of 2048 (99.0%). Most often missed: லை (9), னை (5), னா (3), ணை (2), ளை (2)

## 6. Lines with CER over 30% — v31_best (likely crop or ground-truth problems)

12 lines (0.3%) hold 8% of the character errors. Examples:

- 88% `ws_fc16352787_p0022_000`  truth: 8 கலைஞர்  |  OCR: க
- 65% `ws_ab47be27c6_p0145_000`  truth: டாக்டர். சி. பா. 143  |  OCR: பாடப். 1149
- 62% `ws_d95881d2f4_p0056_000`  truth: மேடைப் பேச்சு 47  |  OCR: டப் சபக் 9.
- 57% `ws_cec4c0ddb3_p0235_028`  truth: "கருணையுள்ள கடவுளே! அவர்களுக்கு நல்லது செய்.  |  OCR: ரன பற்க கடவன அன்களு கு ந4g ரெப்
- 53% `ws_afae783b7f_p0199_000`  truth: 188 நெஞ்சுக்கு நீதி  |  OCR: ஓ] ப நேருகுக்கு ந்து
- 50% `ws_1eed874bd5_p0174_002`  truth: நாட்களில்.  |  OCR: காட்களிலி....
- 44% `ws_f1dc9444b2_p0090_000`  truth: 90 வல்லிக்கண்ணன்  |  OCR: 909090 வி வல்லிக்கண்ணன்
- 43% `ws_dc69dd69eb_p0044_008`  truth: சமமானவை  |  OCR: சமமான லவ்
- 40% `ws_b4f3b04bb5_p0601_026`  truth: துணைவேந்தராக நியமிக்கத் தரணி காவலர் அரசு யோசித்து வருவதை இங்கு நான்  |  OCR: தனவே நரா நியாக்கர் சண காவலா ரச வோரகித்து வரு இந்துதான்
- 38% `ws_d40807f8d1_p0306_020`  truth: கொண்டே.]  |  OCR: கொண்ட
