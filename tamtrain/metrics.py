"""Text-similarity measures used by published OCR benchmarks, without extra dependencies.

The RANLP 2025 Tamil/Sinhala OCR comparison (Jayatilleke & de Silva) reports BLEU, ANLS and
METEOR next to CER and WER. These follow the usual Python definitions so scores can be compared:

- BLEU: NLTK's `sentence_bleu` defaults (1- to 4-grams, equal weights, no smoothing) on
  whitespace tokens, averaged over lines. `corpus_bleu` (counts pooled over all lines) is given
  too. A line with no matching n-gram of some order scores 0, as in NLTK (which returns ~1e-77).
- ANLS (Biten et al. 2019): per line 1 - NL when the normalised Levenshtein distance
  NL = distance / max(len) is below 0.5, else 0; averaged over lines. Case-insensitive.
- METEOR: NLTK's `single_meteor_score` (alpha 0.9, beta 3, gamma 0.5, lower-cased) with exact
  word matches. NLTK's extra stem and WordNet synonym matches are English-only and never fire on
  Tamil words.
"""

from __future__ import annotations

import math
from collections import Counter

from .scans import levenshtein


def _ngrams(tokens: list[str], n: int) -> Counter:
    return Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def _bleu_counts(ref: list[str], hyp: list[str], max_n: int = 4) -> tuple[list[int], list[int]]:
    num, den = [], []
    for n in range(1, max_n + 1):
        h, r = _ngrams(hyp, n), _ngrams(ref, n)
        num.append(sum(min(c, r[g]) for g, c in h.items()))
        den.append(max(1, sum(h.values())))
    return num, den


def _bleu(num: list[int], den: list[int], ref_len: int, hyp_len: int) -> float:
    if hyp_len == 0 or any(x == 0 for x in num):
        return 0.0
    bp = 1.0 if hyp_len > ref_len else math.exp(1 - ref_len / hyp_len)
    return bp * math.exp(sum(math.log(a / b) for a, b in zip(num, den)) / len(num))


def sentence_bleu(ref: list[str], hyp: list[str]) -> float:
    num, den = _bleu_counts(ref, hyp)
    return _bleu(num, den, len(ref), len(hyp))


def corpus_bleu(refs: list[list[str]], hyps: list[list[str]]) -> float:
    num, den = [0] * 4, [0] * 4
    for r, h in zip(refs, hyps):
        a, b = _bleu_counts(r, h)
        num = [x + y for x, y in zip(num, a)]
        den = [x + y for x, y in zip(den, b)]
    return _bleu(num, den, sum(map(len, refs)), sum(map(len, hyps)))


def anls(truth: str, ocr: str, tau: float = 0.5) -> float:
    a, b = truth.strip().lower(), ocr.strip().lower()
    if not a and not b:
        return 1.0
    nl = levenshtein(a, b) / max(len(a), len(b))
    return 1 - nl if nl < tau else 0.0


def meteor(ref: list[str], hyp: list[str], alpha: float = 0.9, beta: float = 3.0, gamma: float = 0.5) -> float:
    h = [(i, w.lower()) for i, w in enumerate(hyp)]
    r = [(j, w.lower()) for j, w in enumerate(ref)]
    matches = []
    for i in range(len(h))[::-1]:          # same order as NLTK, so ties align the same way
        for j in range(len(r))[::-1]:
            if h[i][1] == r[j][1]:
                matches.append((h[i][0], r[j][0]))
                h.pop(i)
                r.pop(j)
                break
    matches.sort(key=lambda m: m[0])
    if not hyp or not ref or not matches:
        return 0.0
    precision, recall = len(matches) / len(hyp), len(matches) / len(ref)
    fmean = precision * recall / (alpha * precision + (1 - alpha) * recall)
    chunks = 1 + sum(1 for a, b in zip(matches, matches[1:]) if not (b[0] == a[0] + 1 and b[1] == a[1] + 1))
    return (1 - gamma * (chunks / len(matches)) ** beta) * fmean


def similarity(truths: list[str], ocrs: list[str]) -> dict[str, float]:
    """BLEU (mean of lines), corpus BLEU, ANLS and METEOR for paired lines, on a 0-1 scale."""
    refs, hyps = [t.split() for t in truths], [o.split() for o in ocrs]
    n = max(len(truths), 1)
    return {"bleu": round(sum(sentence_bleu(r, h) for r, h in zip(refs, hyps)) / n, 4),
            "bleu_corpus": round(corpus_bleu(refs, hyps), 4),
            "anls": round(sum(anls(t, o) for t, o in zip(truths, ocrs)) / n, 4),
            "meteor": round(sum(meteor(r, h) for r, h in zip(refs, hyps)) / n, 4)}
