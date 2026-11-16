# Day 05 — Quiz answers

1. `A` (7 > 5 matches first; the rest are skipped).
2. `0` falsy, `""` falsy, `"0"` **truthy** (non-empty text), `None` falsy.
3. `=` assigns; comparisons need `==`.
4. `"blue"` on its own is always truthy, so the condition is always True. Write `color == "red" or color == "blue"` or `color in ("red", "blue")`.
5. `status = "adult" if age >= 18 else "minor"`
6. `True` (`3 > 2 and 1 > 2` is False; `not False` is True).
7. At most **one** (the first whose condition is True, otherwise `else`).
8. `case _:` (underscore = wildcard).
