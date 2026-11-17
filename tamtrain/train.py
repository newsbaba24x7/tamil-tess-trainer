"""Turn rendered ground truth into a Tesseract LSTM model.

Follows the same recipe as tesseract-ocr/tesstrain (LANG_TYPE=Indic):
box files (WordStr) -> .lstmf -> unicharset (merged with the start model's)
-> proto model (combine_lang_model --pass_through_recoder) -> lstmtraining
-> best (float) and fast (int) .traineddata.
"""

from __future__ import annotations

import random
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .tamil import normalize
from .util import (CACHE_DIR, LANGDATA_URL, SINGLE_THREAD_ENV, TESSDATA_BEST_URL, Progress, TamTrainError,
                   download, log, read_jsonl, run, step, warn, write_jsonl)


def load_manifest(work: Path) -> list[dict]:
    """Rendered lines (manifest.jsonl) plus imported real lines (extra_manifest.jsonl)."""
    rows = []
    for name in ("manifest.jsonl", "extra_manifest.jsonl"):
        if (work / name).exists():
            rows += read_jsonl(work / name)
    return rows

NORM_MODE = "2"                  # tesstrain LANG_TYPE=Indic
SCRATCH_NET_SPEC = "[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx192 O1c{n}]"
LANGDATA_FILES = ["radical-stroke.txt", "Tamil.unicharset", "Latin.unicharset"]


@dataclass
class TrainOptions:
    name: str = "tam_custom"
    start_model: str = "tam"         # "tam" (download tessdata_best), a .traineddata path, or "none"
    iterations: int = 10000
    learning_rate: float | None = None
    target_error_rate: float = 0.01
    wordlist: Path | None = None
    extra_gt: list[Path] | None = None
    extra_gt_eval: list[Path] | None = None   # real lines used only to measure training (e.g. other books)
    real_repeat: int = 1                     # how many times each real training line is shown per epoch
    psm: int = 13
    jobs: int = 4
    fresh: bool = False
    seed: int = 42


# ----------------------------------------------------------------------------- inputs

def resolve_start_model(spec: str) -> Path | None:
    if spec.lower() == "none":
        return None
    p = Path(spec).expanduser()
    if p.suffix == ".traineddata":
        if not p.exists():
            raise TamTrainError(f"Start model not found: {p}")
        return p
    # A language code: fetch the float ("best") model, the only kind that can be fine-tuned.
    return download(TESSDATA_BEST_URL.format(name=f"{spec}.traineddata"),
                    CACHE_DIR / "tessdata_best" / f"{spec}.traineddata")


def langdata_dir() -> Path:
    d = CACHE_DIR / "langdata"
    for name in LANGDATA_FILES:
        download(LANGDATA_URL.format(name=name), d / name)
    return d


def import_extra_gt(dirs: list[Path], work: Path, seed: int, all_eval: bool = False,
                    holdout: float = 0.1) -> list[dict]:
    """Copy real scanned line images + .gt.txt (tesstrain layout) into the work dir.
    With all_eval every line is an evaluation line; otherwise `holdout` of them are."""
    rows = []
    dest_root = work / "ground-truth" / "_extra"
    for d in dirs:
        gts = sorted(d.rglob("*.gt.txt"))
        if not gts:
            raise TamTrainError(f"No *.gt.txt files in {d}")
        tag = ("eval_" if all_eval else "") + (re.sub(r"[^A-Za-z0-9]+", "_", d.name).strip("_") or "extra")
        for i, gt in enumerate(gts):
            stem = gt.name[: -len(".gt.txt")]
            img = next((gt.with_name(stem + ext) for ext in (".png", ".tif", ".tiff", ".jpg", ".bin.png",
                                                             ".nrm.png", ".raw.png")
                        if gt.with_name(stem + ext).exists()), None)
            if img is None:
                warn(f"no image for {gt}, skipped")
                continue
            base = dest_root / tag / f"{tag}_{i:06d}"
            base.parent.mkdir(parents=True, exist_ok=True)
            Image.open(img).convert("L").save(str(base) + ".png")
            text = gt.read_text(encoding="utf-8").strip()
            (base.parent / (base.name + ".gt.txt")).write_text(normalize(text) + "\n", encoding="utf-8")
            split = "eval" if all_eval or random.Random(f"{seed}:{gt}").random() < holdout else "train"
            rows.append({"base": str(base.relative_to(work)), "font": f"real:{d.name}", "split": split,
                         "real": True})
    log(f"    imported {len(rows)} real ground-truth lines")
    return rows


# ----------------------------------------------------------------------------- lstmf

def write_wordstr_box(base: Path, text: str) -> None:
    """Same output as tesstrain's generate_wordstr_box.py (used for Indic scripts)."""
    with Image.open(str(base) + ".png") as im:
        w, h = im.size
    Path(str(base) + ".box").write_text(f"WordStr 0 0 {w} {h} 0 #{text}\n\t 0 0 {w} {h} 0\n",
                                        encoding="utf-8")


def make_lstmf(base: Path, psm: int) -> str | None:
    png = Path(str(base) + ".png")
    lstmf = Path(str(base) + ".lstmf")
    if lstmf.exists() and lstmf.stat().st_mtime >= png.stat().st_mtime:
        return None
    text = Path(str(base) + ".gt.txt").read_text(encoding="utf-8").strip()
    if not text:
        return f"{base}: empty ground truth"
    write_wordstr_box(base, text)
    proc = subprocess.run(["tesseract", str(png), str(base), "--psm", str(psm), "lstm.train"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=SINGLE_THREAD_ENV)
    if proc.returncode != 0 or not lstmf.exists():
        return f"{base}: {proc.stdout.strip()[-300:]}"
    return None


def build_lstmf(bases: list[Path], psm: int, jobs: int) -> list[Path]:
    progress = Progress(len(bases), "lstmf")
    errors = []
    with ThreadPoolExecutor(jobs) as ex:
        for i, err in enumerate(ex.map(lambda b: make_lstmf(b, psm), bases), 1):
            if err:
                errors.append(err)
            progress.update(i)
    if errors:
        warn(f"{len(errors)} lines could not be converted (first: {errors[0]})")
    return [Path(str(b) + ".lstmf") for b in bases if Path(str(b) + ".lstmf").exists()]


# ----------------------------------------------------------------------------- training

LOSS_RE = re.compile(r"At iteration (\d+)/(\d+)/(\d+).*?BCER train=([\d.]+)%.*?BWER train=([\d.]+)%")
EVAL_RE = re.compile(r"At iteration (\d+), stage \d+, (?:Eval Char error rate=([\d.]+), Word error rate=([\d.]+)|"
                     r"BCER eval=([\d.]+), BWER eval=([\d.]+))")


def run_lstmtraining(cmd: list[str], log_file: Path, max_iter: int) -> None:
    log("    " + " ".join(cmd))
    with open(log_file, "a", encoding="utf-8") as lf, subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1
    ) as proc:
        tail: list[str] = []
        started = finished = False
        for line in proc.stdout:
            lf.write(line)
            tail = (tail + [line.rstrip()])[-30:]
            if m := LOSS_RE.search(line):
                started = True
                # "At iteration L/T/S": L = lines learned from, T = training iterations (what
                # --max_iterations counts), S = samples seen.
                log(f"    iter {m.group(2):>6}/{max_iter}  train char error {m.group(4):>6}%  "
                    f"word error {m.group(5):>6}%")
            # The evaluation thread can print in the middle of another line, so check separately.
            if m := EVAL_RE.search(line):
                cer, wer = (m.group(2), m.group(3)) if m.group(2) else (m.group(4), m.group(5))
                log(f"    iter {m.group(1):>6}  ** eval (unseen lines) char error {float(cer):.2f}%  "
                    f"word error {float(wer):.2f}% **")
            if "Finished!" in line:
                finished = True
                log("    " + line.rstrip())
            elif not m and ("Error" in line or "error:" in line.lower()):
                log("    " + line.rstrip())
        proc.wait()
        if proc.returncode != 0:
            if finished:
                # lstmtraining sometimes exits non-zero while its evaluation thread shuts down,
                # after the final checkpoint has been written.
                warn(f"lstmtraining exited with code {proc.returncode} after finishing; checkpoint is complete")
                return
            msg = "\n".join(tail)
            if not started:
                msg += ("\nHint: fine-tuning needs a float model from tessdata_best, not tessdata_fast "
                        "or a distribution package.")
            raise TamTrainError(f"lstmtraining failed (see {log_file}):\n{msg}")


def train(work: Path, opts: TrainOptions) -> dict:
    if opts.extra_gt or opts.extra_gt_eval:
        step("Importing real ground truth")
        rows = []
        if opts.extra_gt:   # with a separate evaluation set, all of these lines are for training
            rows += import_extra_gt(opts.extra_gt, work, opts.seed, holdout=0.0 if opts.extra_gt_eval else 0.1)
        if opts.extra_gt_eval:
            rows += import_extra_gt(opts.extra_gt_eval, work, opts.seed, all_eval=True)
        write_jsonl(work / "extra_manifest.jsonl", rows)
    manifest = load_manifest(work)
    if not manifest:
        raise TamTrainError(f"No ground truth in {work}. Run 'render' first (or pass --extra-gt).")

    model_dir = work / "model"
    if opts.fresh and model_dir.exists():
        shutil.rmtree(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    log_file = model_dir / "training.log"
    name = opts.name

    step("Preparing start model")
    start = resolve_start_model(opts.start_model)
    start_dir = model_dir / "start"
    if start:
        start_dir.mkdir(exist_ok=True)
        run(["combine_tessdata", "-u", start, start_dir / name], log_file=log_file)
        if not (start_dir / f"{name}.lstm").exists():
            raise TamTrainError(f"{start} has no LSTM model; it cannot be fine-tuned.")
        log(f"    start model: {start}")
    else:
        log("    training from scratch (no start model)")

    step("Building dictionary files")
    words, numbers, puncs = (model_dir / f"{name}.{x}" for x in ("wordlist", "numbers", "punc"))
    for out, comp in ((words, "lstm-word-dawg"), (numbers, "lstm-number-dawg"), (puncs, "lstm-punc-dawg")):
        out.write_text("", encoding="utf-8")
        dawg = start_dir / f"{name}.{comp}"
        if start and dawg.exists():
            run(["dawg2wordlist", start_dir / f"{name}.lstm-unicharset", dawg, out], log_file=log_file)
    if opts.wordlist:
        merged = set(words.read_text(encoding="utf-8").split())
        merged |= {normalize(w) for w in opts.wordlist.read_text(encoding="utf-8").split()}
        words.write_text("\n".join(sorted(merged)) + "\n", encoding="utf-8")
    log(f"    dictionary words: {sum(1 for _ in open(words, encoding='utf-8'))}")

    step("Creating .lstmf training files")
    bases = [work / row["base"] for row in manifest]
    build_lstmf(bases, opts.psm, opts.jobs)
    split_of = {str(work / r["base"]): r["split"] for r in manifest}
    real = {str(work / r["base"]) for r in manifest if r.get("real")}
    real_eval_given = any(r.get("real") and r["split"] == "eval" for r in manifest) and bool(opts.extra_gt_eval)
    train_list, eval_list = [], []
    for b in bases:
        f = Path(str(b) + ".lstmf")
        if not f.exists():
            continue
        if split_of[str(b)] == "eval":
            # with a real evaluation set, training is measured on real scans only
            if not real_eval_given or str(b) in real:
                eval_list.append(str(f.resolve()))
        else:
            train_list += [str(f.resolve())] * (max(1, opts.real_repeat) if str(b) in real else 1)
    if not train_list:
        raise TamTrainError("No training .lstmf files were created; see warnings above.")
    rng = random.Random(opts.seed)
    rng.shuffle(train_list)
    if not eval_list:
        eval_list = train_list[: max(1, len(train_list) // 20)]
    (model_dir / "list.train").write_text("\n".join(train_list) + "\n", encoding="utf-8")
    (model_dir / "list.eval").write_text("\n".join(eval_list) + "\n", encoding="utf-8")
    log(f"    {len(train_list)} training lines, {len(eval_list)} evaluation lines")

    step("Building unicharset and proto model")
    all_gt = model_dir / "all-gt"
    with open(all_gt, "w", encoding="utf-8") as fh:
        for b in bases:
            fh.write(Path(str(b) + ".gt.txt").read_text(encoding="utf-8"))
    unicharset = model_dir / "unicharset"
    if start:
        run(["unicharset_extractor", "--output_unicharset", model_dir / "my.unicharset",
             "--norm_mode", NORM_MODE, all_gt], log_file=log_file)
        run(["merge_unicharsets", start_dir / f"{name}.lstm-unicharset", model_dir / "my.unicharset",
             unicharset], log_file=log_file)
    else:
        run(["unicharset_extractor", "--output_unicharset", unicharset, "--norm_mode", NORM_MODE, all_gt],
            log_file=log_file)
    run(["combine_lang_model", "--input_unicharset", unicharset, "--script_dir", langdata_dir(),
         "--numbers", numbers, "--puncs", puncs, "--words", words, "--output_dir", model_dir,
         "--pass_through_recoder", "--lang", name], log_file=log_file)
    proto = model_dir / name / f"{name}.traineddata"
    if not proto.exists():
        raise TamTrainError(f"combine_lang_model did not create {proto}; see {log_file}")

    step(f"Training ({opts.iterations} iterations; progress every 100)")
    ckpt_dir = model_dir / "checkpoints"
    ckpt_dir.mkdir(exist_ok=True)
    lr = opts.learning_rate if opts.learning_rate is not None else (0.0001 if start else 0.002)
    cmd = ["lstmtraining", "--debug_interval", "0", "--traineddata", str(proto),
           "--learning_rate", str(lr), "--model_output", str(ckpt_dir / name),
           "--train_listfile", str(model_dir / "list.train"), "--eval_listfile", str(model_dir / "list.eval"),
           "--max_iterations", str(opts.iterations), "--target_error_rate", str(opts.target_error_rate)]
    if start:
        cmd[3:3] = ["--old_traineddata", str(start), "--continue_from", str(start_dir / f"{name}.lstm")]
    else:
        n_chars = unicharset.read_text(encoding="utf-8").split("\n", 1)[0].strip()
        cmd[3:3] = ["--net_spec", SCRATCH_NET_SPEC.format(n=n_chars)]
    if (ckpt_dir / f"{name}_checkpoint").exists():
        log("    resuming from existing checkpoint (use --fresh to start over)")
    run_lstmtraining(cmd, log_file, opts.iterations)

    step("Writing final models")
    checkpoint = ckpt_dir / f"{name}_checkpoint"
    if not checkpoint.exists():
        raise TamTrainError(f"No checkpoint written; see {log_file}")
    out = work / "output"
    best = out / "tessdata_best" / f"{name}.traineddata"
    fast = out / "tessdata_fast" / f"{name}.traineddata"
    for target, extra in ((best, []), (fast, ["--convert_to_int"])):
        target.parent.mkdir(parents=True, exist_ok=True)
        run(["lstmtraining", "--stop_training", "--continue_from", checkpoint, "--traineddata", proto,
             *extra, "--model_output", target], log_file=log_file)
        log(f"    {target}")
    return {"best": str(best), "fast": str(fast), "start_model": str(start) if start else None}
