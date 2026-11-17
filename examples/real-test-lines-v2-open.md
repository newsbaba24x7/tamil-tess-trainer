# Line-image evaluation: real-test-lines-psm13

3968 line images, `--psm 13`. Lower is better except exact lines.

- **CER**: character errors / characters, over all lines together.
- **Mean line CER**: CER of each line, averaged (some benchmarks report this one).
- **WER**: word error rate. **Exact**: share of lines read without any error.
- Text is compared after NFC normalisation, with zero-width characters removed and quote/dash variants treated as the same character.


## All lines (3968 lines)

| Model | CER | Mean line CER | WER | Exact lines |
|---|---:|---:|---:|---:|
| start (tam, best) | 3.56% | 4.17% | 21.16% | 41.0% |
| tam_v2 (best) | 1.49% | 1.8% | 10.08% | 68.88% |
| tam_v2 (fast) | 1.46% | 1.76% | 10.11% | 68.8% |
| V1 (188 styles) | 3.21% | 3.69% | 19.79% | 48.44% |
| V2-research | 2.3% | 2.76% | 14.65% | 54.94% |

## Top confusions: start (tam, best)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | . | 482 |
| ∅ | ␠ | 303 |
| த | க | 196 |
| ◌் (U+0BCD) | ∅ | 146 |
| ∅ | : | 129 |
| த | ∅ | 123 |
| ◌ி (U+0BBF) | ∅ | 122 |
| . | , | 117 |
| ◌ி (U+0BBF) | இ | 109 |
| ◌ு (U+0BC1) | ∅ | 108 |
| ␠ | ∅ | 107 |
| ∅ | - | 89 |
| , | . | 78 |
| " | ∅ | 75 |
| க | ∅ | 71 |
| ள | ன | 70 |
| ஆ | அ | 66 |
| ச | ∅ | 66 |
| . | ∅ | 65 |
| ∅ | ' | 64 |

## Top confusions: tam_v2 (best)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 186 |
| . | ∅ | 112 |
| ␠ | ∅ | 103 |
| ∅ | . | 77 |
| ' | ∅ | 73 |
| ∅ | ◌் (U+0BCD) | 60 |
| ◌ு (U+0BC1) | ∅ | 54 |
| . | , | 48 |
| , | . | 47 |
| ◌் (U+0BCD) | ∅ | 41 |
| ந | த | 31 |
| " | ∅ | 30 |
| க | த | 28 |
| , | ∅ | 28 |
| வ | ல | 27 |
| ∅ | ' | 25 |
| க | ∅ | 25 |
| ன | ள | 23 |
| ' | " | 21 |
| ர | ∅ | 21 |

## Top confusions: tam_v2 (fast)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 194 |
| . | ∅ | 113 |
| ␠ | ∅ | 102 |
| ∅ | . | 77 |
| ' | ∅ | 70 |
| . | , | 63 |
| ∅ | ◌் (U+0BCD) | 56 |
| ◌் (U+0BCD) | ∅ | 47 |
| ◌ு (U+0BC1) | ∅ | 44 |
| , | . | 41 |
| க | த | 31 |
| " | ∅ | 29 |
| , | ∅ | 29 |
| ந | த | 28 |
| க | ∅ | 27 |
| ∅ | ' | 26 |
| ன | ள | 25 |
| வ | ல | 24 |
| ∅ | ர | 21 |
| ஒ | ஓ | 20 |

## Top confusions: V1 (188 styles)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 565 |
| ∅ | . | 288 |
| ∅ | ' | 259 |
| . | , | 134 |
| ந | த | 108 |
| ∅ | ◌் (U+0BCD) | 96 |
| ◌் (U+0BCD) | ∅ | 91 |
| ◌ு (U+0BC1) | ∅ | 85 |
| ∅ | - | 84 |
| வ | ல | 75 |
| . | ∅ | 71 |
| ␠ | ∅ | 70 |
| த | ∅ | 57 |
| ன | ள | 57 |
| ∅ | " | 54 |
| க | ச | 54 |
| ∅ | , | 48 |
| ◌ு (U+0BC1) | ◌ூ (U+0BC2) | 48 |
| " | ' | 47 |
| , | . | 46 |

## Top confusions: V2-research

| Truth | OCR | Count |
|---|---|---:|
| . | , | 156 |
| ∅ | ␠ | 147 |
| ◌் (U+0BCD) | ∅ | 138 |
| ∅ | . | 105 |
| . | ∅ | 95 |
| ␠ | ∅ | 94 |
| ∅ | ◌் (U+0BCD) | 86 |
| க | ச | 72 |
| ◌ு (U+0BC1) | ∅ | 69 |
| ∅ | ' | 67 |
| " | ∅ | 62 |
| ' | ∅ | 54 |
| ர | ∅ | 52 |
| " | ' | 49 |
| ந | த | 49 |
| ◌ி (U+0BBF) | ∅ | 48 |
| க | ∅ | 48 |
| ∅ | ச | 47 |
| ன | ள | 45 |
| ◌ி (U+0BBF) | இ | 41 |
