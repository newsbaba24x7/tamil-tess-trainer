# Line-image evaluation: tamil-ocr-benchmark

200 line images, `--psm 7`. Lower is better except exact lines.

- **CER**: character errors / characters, over all lines together.
- **Mean line CER**: CER of each line, averaged (some benchmarks report this one).
- **WER**: word error rate. **Exact**: share of lines read without any error.
- Text is compared after NFC normalisation, with zero-width characters removed and quote/dash variants treated as the same character.


## All lines (200 lines)

| Model | CER | Mean line CER | WER | Exact lines |
|---|---:|---:|---:|---:|
| start (tam, best) | 5.44% | 8.53% | 9.92% | 69.5% |
| tam_v2 (best) | 3.25% | 5.14% | 10.27% | 68.5% |
| tam_v2 (fast) | 3.24% | 5.13% | 10.27% | 68.5% |
| V1 (188 styles) | 5.43% | 8.44% | 10.69% | 68.5% |
| V2-research | 5.5% | 8.53% | 9.78% | 70.0% |

## Group: clean (200 lines)

| Model | CER | Mean line CER | WER | Exact lines |
|---|---:|---:|---:|---:|
| start (tam, best) | 5.44% | 8.53% | 9.92% | 69.5% |
| tam_v2 (best) | 3.25% | 5.14% | 10.27% | 68.5% |
| tam_v2 (fast) | 3.24% | 5.13% | 10.27% | 68.5% |
| V1 (188 styles) | 5.43% | 8.44% | 10.69% | 68.5% |
| V2-research | 5.5% | 8.53% | 9.78% | 70.0% |

## Top confusions: start (tam, best)

| Truth | OCR | Count |
|---|---|---:|
| ␠ | ∅ | 20 |
| a | 8 | 12 |
| e | 6 | 12 |
| r | 1 | 8 |
| s | 5 | 8 |
| o | ∅ | 6 |
| o | ௦ | 5 |
| a | ∅ | 5 |
| g | 9 | 5 |
| i | 1 | 5 |
| l | 1 | 4 |
| t | ∅ | 4 |
| ∅ | 1 | 4 |
| i | ∅ | 4 |
| n | 1 | 4 |
| r | ∅ | 4 |
| d | 0 | 4 |
| n | ∅ | 4 |
| C | ∅ | 3 |
| S | ∅ | 3 |

## Top confusions: tam_v2 (best)

| Truth | OCR | Count |
|---|---|---:|
| ␠ | ∅ | 28 |
| l | ∅ | 16 |
| d | o | 11 |
| c | t | 10 |
| i | ∅ | 9 |
| r | n | 9 |
| h | n | 8 |
| a | ∅ | 8 |
| h | ∅ | 8 |
| ∅ | ␠ | 7 |
| u | ∅ | 7 |
| r | ∅ | 7 |
| a | e | 6 |
| G | ∅ | 6 |
| m | n | 6 |
| ∅ | 1 | 6 |
| C | ∅ | 6 |
| l | 1 | 5 |
| S | 5 | 5 |
| R | ∅ | 5 |

## Top confusions: tam_v2 (fast)

| Truth | OCR | Count |
|---|---|---:|
| ␠ | ∅ | 25 |
| l | ∅ | 15 |
| d | o | 12 |
| c | t | 9 |
| h | ∅ | 9 |
| ∅ | ␠ | 8 |
| h | n | 8 |
| ∅ | 1 | 8 |
| r | n | 8 |
| C | ∅ | 7 |
| r | ∅ | 7 |
| u | ∅ | 7 |
| s | 5 | 7 |
| i | ∅ | 7 |
| m | n | 7 |
| S | 5 | 5 |
| R | ∅ | 5 |
| i | t | 5 |
| M | i | 5 |
| g | 9 | 5 |

## Top confusions: V1 (188 styles)

| Truth | OCR | Count |
|---|---|---:|
| a | 8 | 19 |
| ␠ | ∅ | 18 |
| r | 1 | 17 |
| s | 5 | 14 |
| e | 8 | 14 |
| n | 1 | 13 |
| o | ௦ | 10 |
| l | 1 | 10 |
| i | 1 | 10 |
| ∅ | ␠ | 10 |
| e | 6 | 7 |
| ∅ | 1 | 6 |
| t | 1 | 5 |
| d | 0 | 5 |
| o | 0 | 5 |
| a | 3 | 4 |
| g | 9 | 4 |
| S | 5 | 3 |
| u | ∅ | 3 |
| n | 8 | 3 |

## Top confusions: V2-research

| Truth | OCR | Count |
|---|---|---:|
| ␠ | ∅ | 21 |
| r | 1 | 18 |
| o | 0 | 13 |
| e | 8 | 13 |
| s | 5 | 12 |
| i | 1 | 11 |
| a | 8 | 10 |
| e | 6 | 9 |
| l | 1 | 8 |
| ∅ | 1 | 7 |
| n | 1 | 7 |
| n | ◌ா (U+0BBE) | 5 |
| d | 0 | 5 |
| ∅ | 8 | 5 |
| a | 3 | 4 |
| u | ப | 4 |
| p | 0 | 3 |
| t | 0 | 3 |
| t | 1 | 3 |
| a | ச | 3 |
