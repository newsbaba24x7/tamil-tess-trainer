"""Shared helpers: logging, subprocess calls, downloads, config files."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

TESSDATA_BEST_URL = "https://github.com/tesseract-ocr/tessdata_best/raw/main/{name}"
LANGDATA_URL = "https://github.com/tesseract-ocr/langdata_lstm/raw/main/{name}"

CACHE_DIR = Path(os.environ.get("TAMTRAIN_CACHE", Path.home() / ".cache" / "tamtrain"))

# Tesseract's OpenMP threads spin-wait; several multi-threaded tesseract processes running
# side by side slow each other down by 10-100x. Parallel calls therefore run single-threaded.
SINGLE_THREAD_ENV = {**os.environ, "OMP_THREAD_LIMIT": "1"}

REQUIRED_TOOLS = [
    "tesseract",
    "lstmtraining",
    "combine_tessdata",
    "unicharset_extractor",
    "merge_unicharsets",
    "combine_lang_model",
    "dawg2wordlist",
]


class TamTrainError(RuntimeError):
    """An error with a message meant for the user (no traceback)."""


def log(msg: str = "") -> None:
    print(msg, flush=True)


def step(msg: str) -> None:
    log(f"\n==> {msg}")


def warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr, flush=True)


def check_tools(tools: list[str] = REQUIRED_TOOLS) -> None:
    missing = [t for t in tools if shutil.which(t) is None]
    if missing:
        raise TamTrainError(
            "Missing Tesseract training tools: " + ", ".join(missing) + "\n"
            "On Debian/Ubuntu they come with the 'tesseract-ocr' package "
            "(Tesseract 5.x); otherwise build Tesseract with training tools enabled."
        )


def run(cmd: list[str], *, log_file: Path | None = None, quiet: bool = True, cwd: Path | None = None) -> str:
    """Run a command, raise TamTrainError with its output if it fails."""
    proc = subprocess.run(
        [str(c) for c in cmd], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace"
    )
    if log_file is not None:
        with open(log_file, "a", encoding="utf-8") as fh:
            fh.write("$ " + " ".join(str(c) for c in cmd) + "\n" + proc.stdout + "\n")
    if not quiet:
        log(proc.stdout.rstrip())
    if proc.returncode != 0:
        tail = "\n".join(proc.stdout.strip().splitlines()[-25:])
        raise TamTrainError(f"Command failed ({proc.returncode}): {' '.join(str(c) for c in cmd)}\n{tail}")
    return proc.stdout


def download(url: str, dest: Path) -> Path:
    """Download url to dest unless it already exists. Returns dest."""
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    log(f"    downloading {url}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "tamtrain"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as out:
            shutil.copyfileobj(resp, out)
    except Exception as exc:  # noqa: BLE001 - surface any network error clearly
        tmp.unlink(missing_ok=True)
        raise TamTrainError(f"Download failed: {url}\n{exc}\nDownload it manually to {dest}") from exc
    tmp.rename(dest)
    return dest


def load_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_jsonl(path: Path, rows) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


class Progress:
    """Minimal progress printer that works in plain logs and terminals."""

    def __init__(self, total: int, label: str):
        self.total = max(total, 1)
        self.label = label
        self.start = time.time()
        self.last = 0.0
        self.tty = sys.stdout.isatty()

    def update(self, done: int) -> None:
        now = time.time()
        if done < self.total and now - self.last < (0.5 if self.tty else 15):
            return
        self.last = now
        pct = 100 * done / self.total
        rate = done / max(now - self.start, 1e-6)
        msg = f"    {self.label}: {done}/{self.total} ({pct:.0f}%, {rate:.1f}/s)"
        if self.tty:
            print("\r" + msg, end="" if done < self.total else "\n", flush=True)
        else:
            log(msg)
