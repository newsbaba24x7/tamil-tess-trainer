"""Command line interface: fonts, render, train, evaluate, all."""

from __future__ import annotations

import argparse
import os
import random
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

from . import fonts as fontmod
from . import render as rendermod
from . import tamil, textprep
from .evaluate import ModelSpec, align, evaluate, ocr_batch
from .lines import evaluate_lines
from .scans import evaluate_scans
from .train import TrainOptions, train
from .util import TamTrainError, check_tools, load_json, log, save_json, step, warn, write_jsonl

# ----------------------------------------------------------------------------- helpers


def installed_tessdata() -> Path | None:
    """Directory of the system tessdata (where `tesseract --list-langs` looks)."""
    try:
        out = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    except OSError:
        return None
    first = out.splitlines()[0] if out else ""
    if '"' in first:
        return Path(first.split('"')[1])
    return None


def pick_lines(pool: list[str], n: int, start: int, font: fontmod.Font) -> list[str]:
    """Take n lines from pool starting at `start` (wrapping), skipping lines the font can't render."""
    out: list[str] = []
    if not pool:
        return out
    for k in range(len(pool)):
        line = pool[(start + k) % len(pool)]
        if font.supports(line):
            out.append(line)
            if len(out) == n:
                break
    return out


def coverage_for_font(font: fontmod.Font, n: int, rng: random.Random, tamil_digits: float) -> list[str]:
    grantha = font.supports(tamil.GRANTHA + "க்ஷஸ்ரீ")
    lines = tamil.coverage_lines(n * 2, rng, include_grantha=grantha, include_digits=True,
                                 tamil_digit_share=0.3 * tamil_digits)
    return [line for line in lines if font.supports(line)][:n]


# ----------------------------------------------------------------------------- commands


def cmd_fonts(args) -> None:
    fonts = fontmod.discover(args.fonts, args.include, args.exclude)
    fontmod.print_report(fonts)
    if not args.ocr_check:
        return
    rendermod.check_shaping_support()
    tessdata = installed_tessdata()
    if not tessdata or not (tessdata / "tam.traineddata").exists():
        raise TamTrainError("--ocr-check needs an installed 'tam' model (tesseract --list-langs).")
    step("OCR check: rendering a test sentence in each font and reading it back with the installed 'tam'")
    sentence = "தமிழ் மொழி கொண்டு பெயர் வைத்தேன் கூடு நீர் ஞாயிறு வெளிச்சம் ஆடை"
    tmp = args.work / "fontcheck"
    tmp.mkdir(parents=True, exist_ok=True)
    usable = [f for f in fonts if f.usable]
    images = []
    for f in usable:
        img = rendermod.render_clean(sentence, rendermod._font(str(f.path), f.index, 48, f.variation))
        p = tmp / f"{f.slug}.png"
        img.save(p)
        images.append(p)
    texts = ocr_batch(images, ModelSpec("installed", tessdata, "tam"), 7) if images else []
    log(f"\n    {'CER':>6}  font")
    for f, t in zip(usable, texts):
        t = (t or "").translate(dict.fromkeys(map(ord, "‌‍"), None))
        cer = 100 * align(sentence, t)[0] / len(sentence)
        flag = "   <-- check this font (wrong glyph mapping or unusual style?)" if cer > 20 else ""
        log(f"    {cer:5.1f}%  {f.name}{flag}")
    shutil.rmtree(tmp, ignore_errors=True)


def cmd_render(args) -> None:
    rendermod.check_shaping_support()
    work: Path = args.work
    step("Finding fonts")
    fonts = fontmod.discover(args.fonts, args.include, args.exclude, old_letters=args.old_letters > 0)
    fontmod.print_report(fonts)
    usable = [f for f in fonts if f.usable]
    if not usable:
        raise TamTrainError("No usable Unicode Tamil fonts found.")
    holdout = {f.slug for f in usable
               if args.holdout_font and any(p.lower() in f.name.lower() for p in args.holdout_font)}
    if holdout:
        log(f"\n    held out for evaluation only: {', '.join(sorted(holdout))}")

    step("Preparing text")
    corpus = args.text or [textprep.default_corpus()]
    lpf = args.lines_per_font
    n_eval = max(1, round(lpf * args.eval_ratio)) if args.eval_ratio > 0 else 0
    n_cov = round(lpf * args.coverage_ratio)
    needed = len(usable) * lpf
    lines = textprep.build_lines(corpus, min_chars=args.min_chars, max_chars=args.max_chars,
                                 allow_latin=not args.no_latin, max_lines=needed, seed=args.seed,
                                 tamil_digits=args.tamil_digits)
    if len(lines) < 20:
        raise TamTrainError("Too little usable text in the corpus (need at least 20 lines).")
    n_eval_pool = max(1, round(len(lines) * max(args.eval_ratio, 0.02)))
    eval_pool, train_pool = lines[:n_eval_pool], lines[n_eval_pool:]

    step(f"Rendering {len(usable)} fonts x {lpf} lines")
    gt_root = work / "ground-truth"
    if gt_root.exists():
        for d in gt_root.iterdir():
            if d.is_dir() and d.name != "_extra":
                shutil.rmtree(d)
    tasks, meta = [], {}
    n_old_fonts = 0
    for k, font in enumerate(usable):
        rng = random.Random(f"{args.seed}:{font.slug}")
        old_rng = random.Random(f"{args.seed}:{font.slug}:old")
        if font.slug in holdout:
            plan = [("eval", line) for line in pick_lines(eval_pool + train_pool, lpf, k * lpf, font)]
        else:
            plan = [("eval", line) for line in pick_lines(eval_pool, n_eval, k * n_eval, font)]
            plan += [("train", line) for line in coverage_for_font(font, n_cov, rng, args.tamil_digits)]
            plan += [("train", line) for line in pick_lines(train_pool, lpf - len(plan), k * lpf, font)]
        if len(plan) < lpf:
            warn(f"{font.name}: only {len(plan)} renderable lines")
        use_old = bool(font.old_letters) and args.old_letters > 0
        n_old_fonts += use_old or font.old_letters_default
        for i, (split, text) in enumerate(plan):
            base = gt_root / font.slug / f"{font.slug}_{i:05d}"
            seed = zlib.crc32(f"{args.seed}:{font.slug}:{i}".encode())
            old = use_old and old_rng.random() < args.old_letters
            t = rendermod.Task(str(base), text, str(font.path), font.index, seed, font.variation,
                               list(font.old_letters) if old else [])
            tasks.append(t)
            # Lines drawn with old letter shapes are reported as their own "font" in the evaluation.
            label = f"{font.name} (old letters)" if old else font.name
            meta[t.out_base] = (font, split, label, old or font.old_letters_default)
    if n_old_fonts:
        log(f"    {n_old_fonts} fonts draw pre-1978 letter shapes"
            + (f" (in {args.old_letters:.0%} of their lines where a feature turns them on)" if args.old_letters else ""))
    opts = rendermod.RenderOptions(args.min_size, args.max_size, args.clean_ratio, not args.no_degrade,
                                   min_word_gap=args.min_word_gap, justify_ratio=args.justify_ratio,
                                   tracking_ratio=args.tracking_ratio)
    results = rendermod.render_all(tasks, opts, args.jobs)

    rows, failed = [], 0
    for task, res in sorted(results, key=lambda r: r[0].out_base):
        if res is None:
            failed += 1
            continue
        font, split, label, old = meta[task.out_base]
        rows.append({"base": str(Path(task.out_base).relative_to(work)), "font": label,
                     "font_slug": font.slug, "split": split, "old_letters": old, **res})
    if failed:
        warn(f"{failed} lines could not be rendered and were skipped")
    write_jsonl(work / "manifest.jsonl", rows)
    save_json(work / "fonts.json", [f.to_json() for f in usable])
    cfg = load_json(work / "config.json", {})
    cfg["render"] = {k: (str(v) if isinstance(v, Path) else [str(x) for x in v] if isinstance(v, list) else v)
                     for k, v in vars(args).items() if k not in ("func", "work")}
    save_json(work / "config.json", cfg)
    n_train = sum(r["split"] == "train" for r in rows)
    log(f"    {len(rows)} line images ({n_train} train, {len(rows) - n_train} eval) in {gt_root}")


def train_options(args) -> TrainOptions:
    return TrainOptions(name=args.name, start_model=args.start_model, iterations=args.iterations,
                        learning_rate=args.learning_rate, target_error_rate=args.target_error_rate,
                        wordlist=args.wordlist, extra_gt=args.extra_gt, extra_gt_eval=args.extra_gt_eval,
                        real_repeat=args.real_repeat, jobs=args.jobs, fresh=args.fresh,
                        seed=args.seed)


def cmd_train(args) -> None:
    check_tools()
    result = train(args.work, train_options(args))
    cfg = load_json(args.work / "config.json", {})
    cfg["train"] = {"name": args.name, **result}
    save_json(args.work / "config.json", cfg)
    log(f"\nDone. Use it with:\n  tesseract image.png out --tessdata-dir {Path(result['best']).parent} "
        f"-l {args.name}")


def models_to_compare(args) -> list[ModelSpec]:
    """Start model, installed tam, the newly trained best/fast models and any --compare models."""
    cfg = load_json(args.work / "config.json", {})
    trained = cfg.get("train", {})
    models: list[ModelSpec] = []
    start = trained.get("start_model")
    if start:
        models.append(ModelSpec(f"start ({Path(start).stem}, best)", Path(start).parent, Path(start).stem))
    sys_dir = installed_tessdata()
    if not args.no_installed and sys_dir and (sys_dir / "tam.traineddata").exists():
        models.append(ModelSpec("installed tam", sys_dir, "tam"))
    name = trained.get("name", "new")
    for key, label in (("best", f"{name} (best)"), ("fast", f"{name} (fast)")):
        if trained.get(key) and Path(trained[key]).exists():
            p = Path(trained[key])
            models.append(ModelSpec(label, p.parent, p.stem))
    for spec in args.compare or []:
        label, _, path = spec.partition("=")
        p = Path(path or label).expanduser()
        models.append(ModelSpec(label if path else p.stem, p.parent, p.stem))
    if not models:
        raise TamTrainError("No models to evaluate. Train first, or pass --compare label=path.traineddata")
    return models


def cmd_evaluate(args) -> None:
    check_tools(["tesseract"])
    evaluate(args.work, models_to_compare(args), max_lines=args.eval_lines, psm=args.psm, jobs=args.jobs,
             seed=args.seed)


def cmd_lines(args) -> None:
    check_tools(["tesseract"])
    evaluate_lines(args.folders, models_to_compare(args), args.work / "report", args.name, psm=args.psm,
                   jobs=args.jobs, limit=args.limit, raw=args.raw)


def cmd_scans(args) -> None:
    check_tools(["tesseract"])
    evaluate_scans(args.pages, models_to_compare(args), args.work / "report", psm=args.psm, jobs=args.jobs,
                   limit=args.limit, name=args.name, exclude_from=args.exclude_from)


def cmd_all(args) -> None:
    check_tools()
    cmd_render(args)
    cmd_train(args)
    cmd_evaluate(args)


# ----------------------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tamtrain",
        description="Train Tesseract's Tamil OCR model from Tamil font files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--work", type=Path, default=Path("work"), help="working directory")
        sp.add_argument("--jobs", type=int, default=os.cpu_count() or 2, help="parallel processes")
        sp.add_argument("--seed", type=int, default=42, help="random seed (results are reproducible)")

    def font_args(sp, required=True):
        sp.add_argument("--fonts", type=Path, nargs="+", required=required,
                        help="font files and/or directories (searched recursively)")
        sp.add_argument("--include", nargs="+", help="only fonts whose name/file matches these globs")
        sp.add_argument("--exclude", nargs="+", help="skip fonts whose name/file matches these globs")

    def render_args(sp):
        font_args(sp)
        sp.add_argument("--text", type=Path, nargs="+",
                        help="UTF-8 Tamil text files (default: Tesseract's official tam.training_text)")
        sp.add_argument("--lines-per-font", type=int, default=800)
        sp.add_argument("--eval-ratio", type=float, default=0.1, help="share of lines held out for evaluation")
        sp.add_argument("--coverage-ratio", type=float, default=0.15,
                        help="share of lines that cycle through every Tamil syllable")
        sp.add_argument("--holdout-font", nargs="+",
                        help="fonts (name substring) used only for evaluation, to test generalisation")
        sp.add_argument("--min-chars", type=int, default=12)
        sp.add_argument("--max-chars", type=int, default=60)
        sp.add_argument("--min-size", type=int, default=28, help="smallest font size in pixels")
        sp.add_argument("--max-size", type=int, default=64, help="largest font size in pixels")
        sp.add_argument("--clean-ratio", type=float, default=0.3, help="share of images left undegraded")
        sp.add_argument("--no-degrade", action="store_true", help="render clean images only")
        sp.add_argument("--no-latin", action="store_true", help="drop text lines with English words")
        sp.add_argument("--old-letters", type=float, default=0.5, metavar="SHARE",
                        help="for fonts with an OpenType feature for pre-1978 letter shapes (ணா றா னா, "
                             "ணை லை ளை னை), the share of their lines drawn with it; 0 = never")
        sp.add_argument("--tamil-digits", type=float, default=0.1, metavar="SHARE",
                        help="share of Tamil-digit numbers (௧௨௩) kept from the text; they are rare in "
                             "print and look like letters")
        sp.add_argument("--min-word-gap", type=float, default=0.25, metavar="EM",
                        help="word spaces narrower than this (in em) are widened")
        sp.add_argument("--justify-ratio", type=float, default=0.3,
                        help="share of lines with wider, justified-looking word spaces")
        sp.add_argument("--tracking-ratio", type=float, default=0.12,
                        help="share of lines with letter-spacing inside words")

    def train_args(sp):
        sp.add_argument("--name", default="tam_custom", help="model name (the -l value)")
        sp.add_argument("--start-model", default="tam",
                        help="'tam' (downloads tessdata_best), a .traineddata path, or 'none' (from scratch)")
        sp.add_argument("--iterations", type=int, default=10000)
        sp.add_argument("--learning-rate", type=float, help="default 0.0001 fine-tuning, 0.002 from scratch")
        sp.add_argument("--target-error-rate", type=float, default=0.01)
        sp.add_argument("--wordlist", type=Path, help="extra dictionary words, one per line")
        sp.add_argument("--extra-gt-eval", type=Path, nargs="+",
                        help="dirs of real scanned lines used only to measure training (e.g. other books); "
                             "the training log's evaluation numbers then come from real scans")
        sp.add_argument("--real-repeat", type=int, default=1,
                        help="show each real training line this many times (real lines are fewer than rendered)")
        sp.add_argument("--extra-gt", type=Path, nargs="+",
                        help="dirs of real scanned lines: line.png + line.gt.txt (tesstrain layout)")
        sp.add_argument("--fresh", action="store_true", help="discard previous checkpoints")

    def eval_args(sp):
        sp.add_argument("--eval-lines", type=int, default=600)
        sp.add_argument("--psm", type=int, default=7, help="page segmentation mode for evaluation OCR")
        sp.add_argument("--compare", action="append", metavar="LABEL=PATH",
                        help="also evaluate another .traineddata (repeatable)")
        sp.add_argument("--no-installed", action="store_true", help="don't evaluate the system 'tam' model")

    sp = sub.add_parser("fonts", help="list fonts and whether they can be used",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    font_args(sp)
    sp.add_argument("--ocr-check", action="store_true", help="render + OCR a test sentence per font")
    sp.add_argument("--work", type=Path, default=Path("work"))
    sp.set_defaults(func=cmd_fonts)

    sp = sub.add_parser("render", help="render training line images from fonts",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    common(sp), render_args(sp)
    sp.set_defaults(func=cmd_render)

    sp = sub.add_parser("train", help="fine-tune the model on the rendered lines",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    common(sp), train_args(sp)
    sp.set_defaults(func=cmd_train)

    sp = sub.add_parser("evaluate", help="compare old and new models on held-out lines",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    common(sp), eval_args(sp)
    sp.set_defaults(func=cmd_evaluate)

    sp = sub.add_parser("scans", help="compare old and new models on real scanned pages",
                        description="OCR whole scanned pages (image + .gt.txt with the page text) with each "
                                    "model and compare. Writes <work>/report/scans.md.",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    common(sp)
    sp.add_argument("pages", type=Path, nargs="+",
                    help="folders with page images (.png/.jpg/.tif) and matching .gt.txt files")
    sp.add_argument("--psm", type=int, default=3, help="page segmentation mode (3 = automatic layout)")
    sp.add_argument("--name", default="scans", help="report name (<work>/report/<name>.md)")
    sp.add_argument("--exclude-from", type=Path, metavar="REPORT.json",
                    help="for rescaled copies of a page set: leave out the pages that the full-resolution "
                         "report found to have another page's text, and keep every other page")
    sp.add_argument("--limit", type=int, help="only the first N pages")
    sp.add_argument("--compare", action="append", metavar="LABEL=PATH",
                    help="also evaluate another .traineddata (repeatable)")
    sp.add_argument("--no-installed", action="store_true", help="don't evaluate the system 'tam' model")
    sp.set_defaults(func=cmd_scans)

    sp = sub.add_parser("lines", help="compare models on any folder of line images (e.g. a public benchmark)",
                        description="OCR single-line images (image + .gt.txt) with each model and compare. "
                                    "An optional groups.json in the folder ({\"<image stem>\": \"<group>\"}) "
                                    "splits the results. Writes <work>/report/<name>.md.",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    common(sp)
    sp.add_argument("folders", type=Path, nargs="+", help="folders with line images and .gt.txt files")
    sp.add_argument("--name", default="lines", help="report name")
    sp.add_argument("--psm", type=int, default=7, help="page segmentation mode (7 = one text line)")
    sp.add_argument("--raw", action="store_true",
                    help="compare text as is (NFC only): invisible characters such as U+200C count as errors")
    sp.add_argument("--limit", type=int, help="only the first N lines")
    sp.add_argument("--compare", action="append", metavar="LABEL=PATH",
                    help="also evaluate another .traineddata (repeatable)")
    sp.add_argument("--no-installed", action="store_true", help="don't evaluate the system 'tam' model")
    sp.set_defaults(func=cmd_lines)

    sp = sub.add_parser("all", help="render, train and evaluate in one go",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    common(sp), render_args(sp), train_args(sp), eval_args(sp)
    sp.set_defaults(func=cmd_all)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except TamTrainError as exc:
        print(f"\nerror: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted (training can be resumed by running the same command again)", file=sys.stderr)
        return 130
    return 0
