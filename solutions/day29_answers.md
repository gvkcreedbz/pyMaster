# Day 29 — Quiz answers

1. **E**xtract (read data from the source), **T**ransform (clean/reshape/calculate), **L**oad (store it somewhere useful, e.g. a database).
2. The exit code tells the shell, schedulers and CI whether the job succeeded (`0`) or failed (non-zero) so failures aren't silent.
3. Raw data is your source of truth: if your cleaning code has a bug, you can fix it and re-run; if you overwrote the file the original is lost.
4. It runs that block only when the file is executed directly (`python file.py`), not when it's imported by another module/test.
5. Small functions are easy to understand, test, reuse and replace; bugs are easier to locate.
6. Log what happens (row counts before/after, totals, quality report), validate outputs, and fail loudly with clear error messages.
7. It reads the real command-line arguments (`sys.argv[1:]`); passing a list instead lets you test `main` without a terminal.
8. Unit-test each function with tiny hand-made data (pytest), and run the whole pipeline on a known sample and compare outputs/KPIs (an "end-to-end" or "golden file" test).
