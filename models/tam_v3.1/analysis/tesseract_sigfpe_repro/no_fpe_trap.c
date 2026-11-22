/* Test aid for tesseract 5.5.0-5.5.3 (tesseract-ocr/tesseract#4627, fixed in 5.5.4 by #4630).
 * The CLI turns on floating-point traps (feenableexcept) in main1(); two unrecognised words in one
 * row then make -FLT_MAX + -FLT_MAX overflow and kill the process with SIGFPE. Preloading this
 * no-op leaves every computation unchanged; the overflow just yields -inf instead of a signal.
 *   gcc -shared -fPIC -O2 -o no_fpe_trap.so no_fpe_trap.c
 *   LD_PRELOAD=$PWD/no_fpe_trap.so tesseract line.png - -l tam --psm 7                       */
int feenableexcept(int excepts) { (void)excepts; return 0; }
