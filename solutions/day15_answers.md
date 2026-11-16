# Day 15 — Quiz answers

1. It closes the file automatically, even if an error happens inside the block (no leaks, no half-written files).
2. It **erases** the old content (or creates the file if missing).
3. Open with mode `"a"` (append) and write.
4. `\n` is the new-line character. `write()` doesn't add one for you, so you must add it.
5. The absolute path of the folder that contains the running script — a reliable base for other paths.
6. `Path("a/b/c.txt")`.
7. `.suffix` → `".csv"`, `.stem` → `"report.final"`.
8. On Windows the default encoding can't store characters like `₹` or emojis. UTF-8 handles all of them and is the universal standard.
