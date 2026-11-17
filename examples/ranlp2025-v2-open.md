# Line-image evaluation: ranlp2025-raw-psm3

7000 line images, `--psm 3`. Lower is better except exact lines.

- **CER**: character errors / characters, over all lines together.
- **Mean line CER**: CER of each line, averaged (some benchmarks report this one).
- **WER**: word error rate. **Exact**: share of lines read without any error.
- Text is compared as is (`--raw`): NFC normalisation and single spaces only, so invisible characters such as U+200C count as errors, as in most published benchmarks.


## All lines (7000 lines)

| Model | CER | Mean line CER | WER | Exact lines |
|---|---:|---:|---:|---:|
| start (tam, best) | 7.36% | 7.38% | 57.98% | 2.8% |
| tam_v2 (best) | 1.15% | 1.16% | 17.94% | 61.67% |
| tam_v2 (fast) | 1.18% | 1.19% | 18.38% | 60.94% |
| V1 (188 styles) | 0.97% | 0.98% | 14.15% | 67.33% |
| V2-research | 1.07% | 1.09% | 11.16% | 66.7% |

## Group: vowel signs stripped (6803 lines)

| Model | CER | Mean line CER | WER | Exact lines |
|---|---:|---:|---:|---:|
| start (tam, best) | 7.41% | 7.42% | 58.63% | 2.85% |
| tam_v2 (best) | 1.18% | 1.19% | 18.72% | 60.68% |
| tam_v2 (fast) | 1.21% | 1.22% | 19.18% | 59.91% |
| V1 (188 styles) | 1.0% | 1.0% | 14.77% | 66.47% |
| V2-research | 1.11% | 1.12% | 11.65% | 65.79% |

## Group: natural text (197 lines)

| Model | CER | Mean line CER | WER | Exact lines |
|---|---:|---:|---:|---:|
| start (tam, best) | 5.95% | 6.03% | 43.84% | 1.02% |
| tam_v2 (best) | 0.07% | 0.07% | 0.86% | 95.94% |
| tam_v2 (fast) | 0.06% | 0.06% | 0.79% | 96.45% |
| V1 (188 styles) | 0.05% | 0.05% | 0.57% | 96.95% |
| V2-research | 0.04% | 0.03% | 0.36% | 97.97% |

## Top confusions: start (tam, best)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | U+200C | 16427 |
| த | க | 797 |
| ◌் (U+0BCD) | ∅ | 705 |
| ␠ | ∅ | 658 |
| ∅ | ␠ | 519 |
| ற | ந | 359 |
| ∅ | க | 256 |
| ஒ | ∅ | 251 |
| ற | ஈ | 203 |
| ர | ∅ | 198 |
| ∅ | ◌் (U+0BCD) | 194 |
| ∅ | ◌ா (U+0BBE) | 181 |
| ஒ | ஓ | 172 |
| ∅ | ௮ | 142 |
| ந | ற | 141 |
| ர | ஹ | 141 |
| ◌் (U+0BCD) | ◌ா (U+0BBE) | 135 |
| ◌ீ (U+0BC0) | ∅ | 131 |
| ஒ | ஜ | 130 |
| ∅ | த | 130 |

## Top confusions: tam_v2 (best)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 1520 |
| ␠ | ∅ | 966 |
| ∅ | ◌ு (U+0BC1) | 373 |
| ∅ | ◌ா (U+0BBE) | 84 |
| ∅ | ◌் (U+0BCD) | 84 |
| ◌் (U+0BCD) | ∅ | 64 |
| ர | ◌ா (U+0BBE) | 50 |
| ஓ | ஒ | 47 |
| ∅ | ட | 39 |
| ∅ | த | 33 |
| ∅ | ர | 29 |
| எ | ள | 22 |
| ∅ | ள | 21 |
| ஈ | ◌ா (U+0BBE) | 18 |
| ந | ◌ு (U+0BC1) | 17 |
| ஜ | ஐ | 17 |
| ஐ | ஜ | 16 |
| ஒ | ∅ | 15 |
| ◌ீ (U+0BC0) | ◌ி (U+0BBF) | 15 |
| ∅ | ◌ி (U+0BBF) | 15 |

## Top confusions: tam_v2 (fast)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 1635 |
| ␠ | ∅ | 924 |
| ∅ | ◌ு (U+0BC1) | 386 |
| ∅ | ◌் (U+0BCD) | 99 |
| ∅ | ◌ா (U+0BBE) | 85 |
| ◌் (U+0BCD) | ∅ | 57 |
| ர | ◌ா (U+0BBE) | 49 |
| ஓ | ஒ | 45 |
| ∅ | ட | 42 |
| ∅ | த | 32 |
| ∅ | ர | 30 |
| ∅ | ள | 26 |
| ஈ | ◌ா (U+0BBE) | 18 |
| எ | ள | 18 |
| ஜ | ஐ | 18 |
| எ | ◌ா (U+0BBE) | 17 |
| ஐ | ஜ | 16 |
| ந | ◌ு (U+0BC1) | 15 |
| ∅ | ப | 15 |
| ∅ | ◌ி (U+0BBF) | 14 |

## Top confusions: V1 (188 styles)

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 1726 |
| ஒ | ஓ | 177 |
| ∅ | ◌ு (U+0BC1) | 121 |
| ◌் (U+0BCD) | ∅ | 87 |
| க | ௧ | 86 |
| ∅ | ட | 67 |
| ∅ | ஓ | 66 |
| ◌ீ (U+0BC0) | ◌ி (U+0BBF) | 50 |
| ∅ | ர | 44 |
| ∅ | ள | 44 |
| ∅ | க | 39 |
| ␠ | ∅ | 28 |
| த | க | 28 |
| ∅ | ௮ | 26 |
| ∅ | வ | 23 |
| ழ | ◌ி (U+0BBF) | 22 |
| அ | ௮ | 22 |
| ஜ | ஐ | 21 |
| ந | ◌ு (U+0BC1) | 19 |
| ∅ | ஒ | 18 |

## Top confusions: V2-research

| Truth | OCR | Count |
|---|---|---:|
| ∅ | ␠ | 361 |
| ␠ | ∅ | 310 |
| ◌் (U+0BCD) | ∅ | 308 |
| எ | ள | 225 |
| ர | ∅ | 177 |
| ∅ | ◌ு (U+0BC1) | 173 |
| ◌் (U+0BCD) | ◌ா (U+0BBE) | 172 |
| ∅ | ள | 166 |
| த | க | 123 |
| ர | ◌ா (U+0BBE) | 92 |
| ∅ | ர | 87 |
| ∅ | ◌ா (U+0BBE) | 86 |
| ∅ | க | 81 |
| ஒ | ∅ | 65 |
| ∅ | ட | 64 |
| ஓ | ஒ | 63 |
| ∅ | ◌ை (U+0BC8) | 47 |
| ∅ | ◌் (U+0BCD) | 45 |
| ற | ர | 41 |
| ற | ∅ | 36 |
