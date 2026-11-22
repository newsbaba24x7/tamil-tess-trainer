# Tesseract SIGFPE in single-row modes (known upstream bug, fixed in 5.5.4)

**Status:** already reported as tesseract-ocr/tesseract#4627 (closed 2026-09-27) and fixed by PR #4630
(merge `db20f322d0`, 2026-09-28), which is part of **Tesseract 5.5.4** (released 2026-10-28). No new report needed.

## What happens
The stock `tesseract` CLI 5.5.0–5.5.3 can be killed by SIGFPE (exit status 136) with `--psm 7/8/9/10/13` when a line
yields two words the recogniser left empty. `WERD_RES::FakeWordFromRatings` / `WERD_CHOICE::make_bad()` give such a
word the certainty −FLT_MAX; `Textord::CleanupSingleRowResult` adds the word certainties of a row in a `float`, so
−FLT_MAX + −FLT_MAX overflows, and `main1()` in `src/tesseract.cpp` enables `FE_DIVBYZERO | FE_OVERFLOW | FE_INVALID`
traps (GCC builds). Library/API users do not enable the traps and get a harmless −inf row mean. The fix makes the
bad-word certainty a finite −100000.

Which lines trigger it depends on the image and the model (speck noise next to text is typical). The upstream report
used `tessdata_fast` `fas`; here `tam_fast_v3.1` triggers it on two of 8,211 lines (see `../../results/crash_*.txt`).

## Evidence on this machine (Tesseract 5.5.0, Debian `tesseract-ocr 5.5.0-1build1`)
gdb on line `wb_05f33f0963_p0041_018` (tam_v3 dev split, archive.org scan; crop not redistributed) with `tam_fast_v3.1`:
```
Program received signal SIGFPE, Arithmetic exception.
=> addss  0x80(%rax),%xmm0          xmm0 = -3.40282347e+38, 0x80(%rax) = -3.40282347e+38
#1 tesseract::Tesseract::recog_all_words(...)
```
Both operands are −FLT_MAX, exactly the case fixed by #4630.

## Test aid
`no_fpe_trap.c` makes `feenableexcept` a no-op when preloaded. Every computation is unchanged; an overflow gives −inf
instead of a signal. With it, 5.5.0 reads both crash lines (the first as `சொன்னார்.` plus speck noise), and models that
do not crash give byte-identical output with and without it. The v3.1 accuracy runs use it so that a crash cannot
abort a batch; crash counts are measured separately with the stock CLI (`../../17_crash_scan.py`).
```bash
gcc -shared -fPIC -O2 -o no_fpe_trap.so no_fpe_trap.c
LD_PRELOAD=$PWD/no_fpe_trap.so tesseract line.png - -l tam --psm 7
```
