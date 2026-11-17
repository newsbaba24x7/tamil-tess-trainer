# Line-image evaluation: real-dev-lines-psm13

2854 line images, `--psm 13`. Lower is better except exact lines.

- **CER**: character errors / characters, over all lines together.
- **Mean line CER**: CER of each line, averaged (some benchmarks report this one).
- **WER**: word error rate. **Exact**: share of lines read without any error.
- Text is compared after NFC normalisation, with zero-width characters removed and quote/dash variants treated as the same character.


## All lines (2854 lines)

| Model | CER | Mean line CER | WER | Exact lines |
|---|---:|---:|---:|---:|
| start (tam, best) | 3.21% | 3.64% | 19.53% | 51.02% |
| tam_v2 (best) | 1.2% | 1.31% | 8.27% | 76.07% |
| tam_v2 (fast) | 1.32% | 1.44% | 8.22% | 76.42% |
| V2-research | 1.93% | 2.19% | 12.34% | 65.49% |

## Top confusions: start (tam, best)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | . | 297 |
| ' | " | 191 |
| ∅ | ␠ | 172 |
| த | க | 159 |
| ∅ | : | 136 |
| ␠ | ∅ | 97 |
| ' | ∅ | 84 |
| ◌ி (U+0BBF) | ∅ | 70 |
| த | ∅ | 69 |
| ◌ி (U+0BBF) | இ | 66 |
| ∅ | - | 62 |
| ◌் (U+0BCD) | ∅ | 61 |
| க | ச | 54 |
| ச | ∅ | 49 |
| ∅ | * | 47 |
| ◌ு (U+0BC1) | ∅ | 45 |
| ந | க | 41 |
| ∅ | ' | 40 |
| ∅ | க | 38 |
| . | ∅ | 38 |

## Top confusions: tam_v2 (best)

| Truth | OCR | Count |
|---|---|---:|
| ' | ∅ | 116 |
| . | ∅ | 95 |
| ␠ | ∅ | 94 |
| ∅ | ␠ | 87 |
| ' | " | 47 |
| க | ச | 38 |
| ∅ | ◌் (U+0BCD) | 25 |
| ❍ | 0 | 21 |
| ∅ | . | 19 |
| ◌ு (U+0BC1) | ∅ | 17 |
| ∅ | ' | 17 |
| - | ∅ | 16 |
| " | ∅ | 16 |
| ◌் (U+0BCD) | ∅ | 15 |
| க | த | 15 |
| . | , | 14 |
| , | . | 14 |
| ∅ | " | 13 |
| , | ∅ | 10 |
| ச | க | 10 |

## Top confusions: tam_v2 (fast)

| Truth | OCR | Count |
|---|---|---:|
| ' | ∅ | 115 |
| ␠ | ∅ | 93 |
| . | ∅ | 93 |
| ∅ | ␠ | 83 |
| ' | " | 44 |
| க | ச | 37 |
| ∅ | ◌் (U+0BCD) | 23 |
| ∅ | . | 22 |
| ❍ | 0 | 21 |
| ◌் (U+0BCD) | ∅ | 17 |
| ◌ு (U+0BC1) | ∅ | 17 |
| " | ∅ | 17 |
| ∅ | ' | 17 |
| ∅ | " | 15 |
| . | , | 14 |
| - | ∅ | 14 |
| , | . | 14 |
| , | ∅ | 11 |
| ம | ∅ | 10 |
| ∅ | ◌ு (U+0BC1) | 10 |

## Top confusions: V2-research

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 97 |
| ' | " | 97 |
| ␠ | ∅ | 89 |
| ' | ∅ | 79 |
| . | ∅ | 69 |
| ∅ | ' | 67 |
| க | ச | 65 |
| ◌் (U+0BCD) | ∅ | 48 |
| . | , | 44 |
| " | ' | 44 |
| ∅ | * | 38 |
| ◌ு (U+0BC1) | ∅ | 38 |
| ◌ி (U+0BBF) | இ | 35 |
| ∅ | ◌் (U+0BCD) | 32 |
| ∅ | . | 28 |
| ∅ | ? | 28 |
| ∅ | - | 25 |
| " | ? | 25 |
| ◌ி (U+0BBF) | ∅ | 23 |
| ◌் (U+0BCD) | ◌ீ (U+0BC0) | 23 |
