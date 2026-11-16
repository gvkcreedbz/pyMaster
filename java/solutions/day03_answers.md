# Day 03 - Quiz answers

1. `7 / 2` = `3` (int division), `7 / 2.0` = `3.5`, `7 % 2` = `1`, `Math.pow(2, 3)` = `8.0` (a double).
2. `2 + 3 * 4 * 4` = `50` (multiplication first), `(2 + 3) * 4` = `20` (brackets first).
3. No, it is `false`. Computers store decimals in binary, so `0.1 + 0.2` is `0.30000000000000004`. Compare with a tolerance: `Math.abs(a - b) < 1e-9` (or use `BigDecimal` for money).
4. `Math.round(2.5)` = `3` and `Math.round(3.5)` = `4` (halves round up; the result is a `long`).
5. It is a shortcut for `x = x + 5;` (add 5 to `x` and store it back).
6. `hours = totalMinutes / 60` and `minutes = totalMinutes % 60` (125 gives 2 and 5).
7. `(int) 3.99` = `3` (decimals are cut off, not rounded). `(double) 7 / 2` = `3.5` (the cast happens before the division).
8. It silently wraps around to `-2147483648`. Avoid it by converting to `long` before the maths: `(long) big + 1`.
