# Day 07 — Week-1 Review Test answers

1. `Hi_there`
2. `str`; `float` (`3 / 1` is `3.0`).
3. `3`, `2`, `16`.
4. `'A'`, `'v'`, `'ar'`.
5. You can't add text and a number (`TypeError`). Fix: `"3" + str(4)` → `"34"` or `int("3") + 4` → `7`.
6. `"A B"`
7. `True` (any non-empty text is truthy, even `"False"`).
8. `False` (`x < 5` is False).
9. `1`, `4`, `7` (start 1, step 3, stop before 8).
10. 3 times.
11. `=` assigns; use `==` for comparison.
12. Resetting the total inside the loop wipes it every round; initialise it **before** the loop.
13. `break` leaves the loop; `continue` skips the rest of this round and continues with the next.
14. `True`. `0.1 + 0.2` is `0.30000000000000004` in binary floating point; rounding removes the tiny error.
15. `print(f"Rs. {1234.5:,.2f}")` → `Rs. 1,234.50`

## Project notes
- Keep each rule in one small function (`validate_withdrawal`) — `run_atm` just coordinates them. This idea (small functions, one job each) is Day 11.
- Stretch ideas: PIN change, mini statement (store every transaction in a list — Day 8), save balance to a file (Day 15).
