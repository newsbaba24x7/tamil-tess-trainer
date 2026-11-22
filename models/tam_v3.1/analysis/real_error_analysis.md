# Error analysis: 3968 real test lines, 168,582 characters, 19,178 words

## 1. Character errors by class (share of all reference characters, i.e. CER points)

| class | v31_best: CER pts (sub/del/ins) | v3_best: CER pts (sub/del/ins) |
|---|---:|---:|
| consonant | 2.06 (262/3151/53) | 2.11 (321/3162/80) |
| vowel sign | 0.98 (136/1475/40) | 0.99 (133/1486/44) |
| pulli ் | 0.62 (13/1004/25) | 0.63 (13/1014/31) |
| space | 0.54 (3/677/237) | 0.51 (1/686/168) |
| period/comma | 0.24 (90/241/77) | 0.25 (92/253/72) |
| vowel/aytham | 0.19 (48/267/11) | 0.20 (67/263/9) |
| quote | 0.13 (19/182/26) | 0.09 (16/109/34) |
| other punctuation | 0.05 (24/37/21) | 0.05 (21/41/16) |
| ASCII digit | 0.02 (19/15/8) | 0.03 (14/17/14) |
| Latin letter | 0.02 (35/3/3) | 0.03 (44/4/2) |
| hyphen/dash | 0.02 (7/24/9) | 0.02 (3/22/6) |
| other | 0.01 (6/5/1) | 0.01 (6/6/4) |
| Tamil numeral/symbol | 0.00 (2/1/1) | 0.00 (3/2/0) |
| **all** | **4.90** | **4.91** |

### CER / WER if a whole class of errors were fixed (both sides stripped of that class)

| scenario | v31_best CER / WER | v3_best CER / WER |
|---|---:|---:|
| as measured | 4.90 / 11.91 | 4.91 / 11.78 |
| spaces ignored | 4.78 / 11.91 (WER as measured) | 4.83 / 11.78 (WER as measured) |
| quotes ignored | 4.78 / 11.06 | 4.83 / 11.21 |
| all punctuation ignored | 4.56 / 9.46 | 4.62 / 9.64 |
| Tamil letters only | 4.53 / 9.24 | 4.57 / 9.35 |

## 2. Most frequent errors — v31_best

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| ' ' → (missing) | 675 |   | '்' → (missing) | 1004 |
| (extra) → ' ' | 235 |   | ' ' → (missing) | 677 |
| '.' → (missing) | 163 |   | 'ு' → (missing) | 457 |
| "'" → (missing) | 133 |   | 'க' → (missing) | 430 |
| 'ன்' → (missing) | 129 |   | 'த' → (missing) | 386 |
| 'ம்' → (missing) | 127 |   | 'ி' → (missing) | 363 |
| 'க' → (missing) | 125 |   | 'ம' → (missing) | 244 |
| 'க்' → (missing) | 106 |   | 'ா' → (missing) | 238 |
| 'து' → (missing) | 92 |   | (extra) → ' ' | 237 |
| 'அ' → (missing) | 91 |   | 'ப' → (missing) | 235 |
| 'த்' → (missing) | 85 |   | 'ர' → (missing) | 228 |
| 'ல்' → (missing) | 84 |   | 'ன' → (missing) | 220 |
| 'வ' → (missing) | 82 |   | 'வ' → (missing) | 214 |
| ',' → (missing) | 77 |   | 'ட' → (missing) | 191 |
| 'த' → (missing) | 77 |   | 'ற' → (missing) | 186 |
| 'கு' → (missing) | 75 |   | 'ல' → (missing) | 183 |
| 'ப்' → (missing) | 69 |   | '.' → (missing) | 163 |
| (extra) → '.' | 65 |   | 'ய' → (missing) | 148 |
| 'ர்' → (missing) | 64 |   | 'ை' → (missing) | 142 |
| 'ப' → (missing) | 63 |   | "'" → (missing) | 133 |
| ',' → '.' | 62 |   | 'ச' → (missing) | 115 |
| 'ரு' → (missing) | 62 |   | 'ந' → (missing) | 115 |
| 'தி' → (missing) | 58 |   | 'ள' → (missing) | 99 |
| 'ய' → (missing) | 55 |   | 'அ' → (missing) | 91 |
| 'எ' → (missing) | 53 |   | 'ே' → (missing) | 81 |
| 'ந்' → (missing) | 53 |   | ',' → (missing) | 78 |
| 'ற்' → (missing) | 53 |   | 'ண' → (missing) | 68 |
| '"' → (missing) | 49 |   | (extra) → '.' | 66 |
| 'இ' → (missing) | 49 |   | ',' → '.' | 62 |
| 'கி' → (missing) | 48 |   | 'ோ' → (missing) | 54 |

## 2. Most frequent errors — v3_best

| letter cluster: truth → OCR | count |   | code point: truth → OCR | count |
|---|---:|---|---|---:|
| ' ' → (missing) | 685 |   | '்' → (missing) | 1014 |
| '.' → (missing) | 174 |   | ' ' → (missing) | 686 |
| (extra) → ' ' | 165 |   | 'ு' → (missing) | 461 |
| 'ன்' → (missing) | 128 |   | 'க' → (missing) | 434 |
| 'க' → (missing) | 127 |   | 'த' → (missing) | 389 |
| 'ம்' → (missing) | 127 |   | 'ி' → (missing) | 366 |
| 'க்' → (missing) | 106 |   | 'ம' → (missing) | 246 |
| 'து' → (missing) | 92 |   | 'ா' → (missing) | 240 |
| 'அ' → (missing) | 92 |   | 'ப' → (missing) | 238 |
| 'த்' → (missing) | 85 |   | 'ர' → (missing) | 228 |
| 'ல்' → (missing) | 84 |   | 'ன' → (missing) | 219 |
| 'வ' → (missing) | 82 |   | 'வ' → (missing) | 214 |
| 'த' → (missing) | 79 |   | 'ட' → (missing) | 191 |
| ',' → (missing) | 76 |   | 'ற' → (missing) | 187 |
| 'கு' → (missing) | 73 |   | 'ல' → (missing) | 181 |
| 'ப்' → (missing) | 69 |   | '.' → (missing) | 174 |
| ',' → '.' | 68 |   | (extra) → ' ' | 168 |
| 'ப' → (missing) | 66 |   | 'ய' → (missing) | 149 |
| 'ர்' → (missing) | 65 |   | 'ை' → (missing) | 140 |
| 'ரு' → (missing) | 63 |   | 'ந' → (missing) | 116 |
| (extra) → '.' | 60 |   | 'ச' → (missing) | 115 |
| 'தி' → (missing) | 59 |   | 'ள' → (missing) | 97 |
| 'ய' → (missing) | 56 |   | 'அ' → (missing) | 92 |
| '"' → (missing) | 54 |   | 'ே' → (missing) | 81 |
| "'" → (missing) | 54 |   | ',' → (missing) | 79 |
| 'எ' → (missing) | 53 |   | ',' → '.' | 68 |
| 'ந்' → (missing) | 53 |   | 'ண' → (missing) | 68 |
| 'ற்' → (missing) | 53 |   | (extra) → '.' | 60 |
| 'இ' → (missing) | 48 |   | 'ோ' → (missing) | 55 |
| 'கி' → (missing) | 48 |   | "'" → (missing) | 55 |

## 3. Words — v31_best

| word error kind | count | share of word errors |
|---|---:|---:|
| word missing (often merged with a neighbour) | 814 | 36% |
| letters | 784 | 34% |
| punctuation only | 412 | 18% |
| extra word (often a word split by a space) | 275 | 12% |

Most often misread words (truth → one OCR example):

நீ → ந் (4×), ; → பெற்றது; (3×), நமது → நம்து (3×), love) → Iosd) (2×), ஓர் → ஒர் (2×), ஒரு → i (2×), தான் → உடலிலேயேதான் (2×), பல → 100 (2×), என்று → எனறு (2×), 90 → 9/) (2×), "இல்லே → சரிப்படாது. (1×), சரிப்படாது-வருத்தப்படாதீக → வருத்தப்படாதீக (1×), ஏன்? → ஏbi (1×), கண்ணாடி → கன்னாடி (1×), வாழ்வை-உணர்வு → - (1×), வாழ்வை-அகம் → அகம் (1×), (Subnormal → (Suhnornral (1×), (Abnormal → (Abuonual (1×), பரந்துப்பட்ட → பட்ட (1×), என → ஏன (1×), சிறந்த → சிறத்த (1×), நுழைதியோ → தி (1×), - → யோ. (1×), 115 → I7 (1×), நீஏன் → ஏன் (1×)

## 4. Where errors concentrate — v31_best

- Page CER: median 1.31%, best 0.00%, worst 100.00%.
- The worst 10% of pages (19) hold 57% of all character errors.
- The worst 20% of pages (39) hold 78% of all character errors.
- The worst 50% of pages (98) hold 94% of all character errors.
- Pages under 2% CER: 122 of 197.

| line height (box) | lines' CER |
|---|---:|
| <30 px | 1.47% (407 chars) |
| 30–39 px | 1.36% (4,274 chars) |
| 40–49 px | 1.19% (11,933 chars) |
| ≥50 px | 5.30% (151,968 chars) |

| printed | CER |
|---|---:|
| no year | 4.90% (168,582 chars) |

Worst 12 books by CER:

| book | CER | chars |
|---|---:|---:|
| அகநானூறு 1, புலியூர்க் கேசிகன்.pdf | 64.9% | 747 |
| கவிஞரைச் சந்தித்தேன்.pdf | 54.0% | 398 |
| குன்றக்குடி அடிகளார் நூல்வரிசை 10.pdf | 50.0% | 1,329 |
| குறட்செல்வம்.pdf | 41.1% | 419 |
| எல்லோரும் இந்நாட்டு மன்னர்.pdf | 39.6% | 508 |
| தம்பிக்கு அண்ணாவின் கடிதங்கள் 04, தமிழ்நாடு அரசு.pdf | 34.6% | 1,056 |
| பழைய கணக்கு.pdf | 31.6% | 1,148 |
| கலைஞர் கடிதம் 3.pdf | 27.0% | 800 |
| கரை மணலும் காகித ஓடமும்.pdf | 26.9% | 579 |
| அண்ணாவின் நாடகங்கள்.pdf | 23.7% | 346 |
| சின்னஞ் சிறு பெண் (மொழிபெயர்ப்பு).pdf | 21.5% | 862 |
| நெஞ்சுக்கு நீதி பாகம் 5.pdf | 20.2% | 327 |

## 5. Letters whose shape changed in the 1978 reform — v31_best

Recovered 1946 of 2048 (95.0%). Most often missed: லை (29), னை (23), னா (20), றா (12), ளை (11), ணை (4), ணா (1), னொ (1), னோ (1)

## 6. Lines with CER over 30% — v31_best (likely crop or ground-truth problems)

148 lines (3.7%) hold 79% of the character errors. Examples:

- 129% `ws_70df19151d_p0101_003`  truth: கண்கள்.  |  OCR: 446597௧௭7.
- 100% `ws_0cc4dbf3b6_p0062_002`  truth: "இராத்திரியில் கண் விழித்து வேலை செய்வது அவர்களுக்குக்  |  OCR: 
- 100% `ws_0cc4dbf3b6_p0062_008`  truth: "வேலை செய்வதில் அவர்கள் சினிமா பார்க்கிற அளவுக்கு  |  OCR: 
- 100% `ws_0cc4dbf3b6_p0062_021`  truth: வீட்டுக்கு டெலிபோன் செய்து "கோயங்கா பேசறேன்" என்றார்.  |  OCR: 
- 100% `ws_0cc4dbf3b6_p0062_023`  truth: "காமராஜ் போயிட்டாரேப்பா, தெரியுமா?" என்று கேட்டார்.  |  OCR: 
- 100% `ws_0cc4dbf3b6_p0062_027`  truth: "நீ போய்ப் பார்க்கவில்லையா?" என்று கேட்டார்.  |  OCR: 
- 100% `ws_0cc4dbf3b6_p0062_031`  truth: திரும்பத் திரும்பச் சொல்லி வருத்தப்பட்டார். அவர் குரலில்  |  OCR: 
- 100% `ws_0cc4dbf3b6_p0062_032`  truth: கனமான சோகம் தோய்ந்து கிடப்பதை என்னால் உணர  |  OCR: 
- 100% `ws_11f052b752_p0304_002`  truth: இல்லை. தினகரியின் பேதைமை மிளிரும் மதிமுகம் உருவெளியில் என் கண்முன்  |  OCR: 
- 100% `ws_11f052b752_p0304_034`  truth: என்றும் சுமங்கலியாகவே பார்த்துக் கொண்டிருப்பதற்கு என்னால் இடையூறு  |  OCR: 
