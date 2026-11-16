# Day 04 — Quiz answers

1. `'Y'`, `'O'`, `'YTH'`, `'NOHTYP'`.
2. `"hi"`. No — strings are immutable; the original is unchanged unless you save the result (`s = s.strip()`).
3. `TypeError` — strings cannot be changed in place; build a new string (`"J" + s[1:]`).
4. `['a', 'b', 'c']`.
5. `'2026-11-16'`.
6. `-1` (not found).
7. No (`False`). Compare `"Apple".lower() == "apple".lower()`.
8. `11` (spaces count).
