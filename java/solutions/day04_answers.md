# Day 04 - Quiz answers

1. `s.charAt(1)` = `'Y'`, `s.substring(1, 4)` = `"YTH"`, `s.substring(3)` = `"HON"`, `s.length()` = `6`.
2. `"hi"` (outer spaces removed). The original variable does not change: Strings are immutable, so you must save the result (`s = s.strip();`).
3. Strings are immutable: you cannot replace one character inside a String. Build a new one: `"J" + s.substring(1)` gives `"JYTHON"`.
4. It returns an array of three Strings: `"a"`, `"b"`, `"c"`. Its `.length` is `3`.
5. `"2026-11-16"`.
6. `-1` (not found).
7. No, it is `false` (different capitals). Use `"Apple".equalsIgnoreCase("apple")` (or lower-case both). `==` asks whether both sides are the very same object in memory, not whether the letters match, so it can be `false` for equal texts. Use `.equals(...)`.
8. A `String` never changes (each method gives a new one); a `StringBuilder` can be changed in place (`append`, `insert`), which is better for building text in steps. Reverse with `new StringBuilder(text).reverse().toString()`.
