"""Turn a raw Tamil text corpus into clean, OCR-line-sized training text."""

from __future__ import annotations

import random
from pathlib import Path

from . import tamil
from .util import CACHE_DIR, LANGDATA_URL, download, log

DEFAULT_CORPUS_NAME = "tam/tam.training_text"


def default_corpus() -> Path:
    """The official Tesseract Tamil training text from langdata_lstm (cached)."""
    return download(LANGDATA_URL.format(name=DEFAULT_CORPUS_NAME), CACHE_DIR / "langdata" / "tam.training_text")


def iter_tokens(paths: list[Path], allow_latin: bool, stats: dict, tamil_digits: float = 1.0,
                rng: random.Random | None = None):
    rng = rng or random.Random(0)
    for path in paths:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                for tok in tamil.normalize(raw).split(" "):
                    if not tok:
                        continue
                    stats["tokens"] += 1
                    cleaned = tamil.clean_token(tok, allow_latin)
                    if cleaned is not None and tamil_digits < 1 and any(tamil.is_tamil_number(c) for c in cleaned):
                        if rng.random() >= tamil_digits:
                            stats["tamil_numbers_dropped"] += 1
                            yield None
                            continue
                    if cleaned is None:
                        stats["dropped"] += 1
                        yield None  # paragraph break: don't join words across dropped noise
                    else:
                        yield cleaned
                yield None  # end of input line


def build_lines(paths: list[Path], *, min_chars: int, max_chars: int, allow_latin: bool,
                max_lines: int, seed: int, tamil_digits: float = 1.0) -> list[str]:
    """Wrap corpus text into lines of min_chars..max_chars characters.

    Lines are de-duplicated and must contain Tamil. Text is never joined across
    a dropped (noisy) token, so no line contains words that were not adjacent.
    """
    rng = random.Random(seed)
    stats = {"tokens": 0, "dropped": 0, "tamil_numbers_dropped": 0}
    seen: set[str] = set()
    lines: list[str] = []
    cur: list[str] = []
    cur_len = 0
    target = rng.randint(min_chars, max_chars)

    def flush():
        nonlocal cur, cur_len, target
        if cur and cur_len >= min_chars:
            line = " ".join(cur)
            if line not in seen and any(tamil.is_tamil_char(c) for c in line):
                seen.add(line)
                lines.append(line)
        cur, cur_len = [], 0
        target = rng.randint(min_chars, max_chars)

    for tok in iter_tokens(paths, allow_latin, stats, tamil_digits, random.Random(f"{seed}:digits")):
        if tok is None:
            flush()
            continue
        add = len(tok) + (1 if cur else 0)
        if cur and cur_len + add > target:
            flush()
            add = len(tok)
        if add > max_chars:
            continue
        cur.append(tok)
        cur_len += add
        if max_lines and len(lines) >= max_lines * 3:
            break  # plenty to sample from
    flush()

    rng.shuffle(lines)
    if max_lines:
        lines = lines[:max_lines]
    pct = 100 * stats["dropped"] / max(stats["tokens"], 1)
    log(f"    corpus: {stats['tokens']} words read, {stats['dropped']} noisy words dropped ({pct:.1f}%), "
        f"{stats['tamil_numbers_dropped']} Tamil-digit numbers left out, {len(lines)} lines kept")
    return lines
