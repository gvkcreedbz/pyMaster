# Day 02 — Quiz answers

1. `int`, `float`, `str`, `bool`.
2. `10` — `y` got a copy of the value; changing `x` later does not change `y`.
3. Valid: `item2`, `my_price`. Invalid: `2nd_item` (starts with digit), `my-price` (hyphen), `class` (keyword).
4. `str`. `age + 1` raises `TypeError` (can't add text and a number). Fix: `int(age) + 1`.
5. `53` (text joined) and `8` (numbers added).
6. `349.50`
7. `33` — the text `"3"` repeated twice. No error, but not what you wanted! Use `int(input(...))`.
8. `ValueError` — `int()` can't parse a decimal string. Use `float("12.5")` (then `int()` if you need a whole number).
