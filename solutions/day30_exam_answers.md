# Day 30 — Final Exam answer key

Every output below was produced by actually running the code (via `_dev_tools/build_exam.py`).

Scoring: 22–25 🏆 · 17–21 ✅ · 12–16 🟡 · <12 🔁 (see LESSON.md).

---

### Q1. (Day 3) — numbers & strings
```text
3 1 3.5 8 abab
```
`//` floors, `%` is the remainder, `/` always gives a float, `**` is power, and `*` repeats a string.

### Q2. (Day 4) — string slicing
```text
skco 2 R
```
`s[::-1]` reverses the text (`skcoR nohtyP`) and `[:4]` keeps 4 characters; the lower-cased text has two `o`; `split()[1]` is `Rocks` and `[0]` its first letter.

### Q3. (Day 5) — truthiness
```text
False True False True False
```
Empty containers/strings are falsy; the *text* `"0"` and the list `[0]` are not empty, so truthy. `None == False` is `False` (use `is None` to test for None).

### Q4. (Day 6) — range & loops
```text
10 7 4 1 
```
`range(10, 0, -3)` counts down by 3 and stops before 0: 10, 7, 4, 1.

### Q5. (Day 6) — loop with else
```text
odd found: 9
```
`else` on a loop runs only if the loop finished without `break`. Here 9 triggers `break`, so `else` is skipped.

### Q6. (Day 8) — list aliasing
```text
[1, 2, 3, 4] [1, 2, 3]
```
`b = a` makes both names point to the *same* list; `a[:]` makes a copy. Appending through `b` changes `a` but not `c`.

### Q7. (Day 8) — list methods
```text
[5, 8] 3 [5, 8, 1]
```
`sorted()` returns a new list `[1, 3, 5, 8]` -> last two `[5, 8]`; `pop(1)` removes and returns `3`; the original now holds `[5, 8, 1]`.

### Q8. (Day 10) — dictionary counting
```text
{'a': 3, 'b': 2, 'c': 1} a
```
`get(w, 0)` supplies 0 for new keys, so we count words. `max(d, key=d.get)` returns the key with the largest value.

### Q9. (Day 9) — sets
```text
{2, 3} {1, 2, 5} 2
```
`&` is intersection, `|` is union, and sets drop duplicates (`{1, 1, 2}` has 2 items).

### Q10. (Day 11) — mutable default argument
```text
[1, 2] [1, 2]
```
The default list is created **once** when the function is defined and shared by every call, so both calls return the same list (a classic trap — use `bucket=None`).

### Q11. (Day 11) — *args and **kwargs
```text
(1, (2, 3), {'k': 4})
```
`*args` collects extra positional arguments into a tuple and `**kw` collects keyword arguments into a dict.

### Q12. (Day 12) — comprehensions
```text
[0, 4, 16] {'hi': 2, 'python': 6} 6
```
List comprehension with a filter keeps even numbers' squares; dict comprehension maps word -> length; the generator sums 0+1+2+3.

### Q13. (Day 12) — sorting with lambda
```text
[('Ann', 30), ('Cy', 30), ('Bob', 25)]
```
The key `(-age, name)` sorts by age descending, then by name A-Z for ties (Ann before Cy).

### Q14. (Day 17) — try / finally
```text
cleanup
try
```
`finally` always runs before the function really returns, so `cleanup` prints first, then the returned value is printed.

### Q15. (Day 17) — exception flow
```text
value
done
```
`int("x")` raises `ValueError`; the matching `except` runs, `else` is skipped (it only runs if nothing was raised) and `finally` always runs.

### Q16. (Day 19) — classes & inheritance
```text
Rex says Woof | Tom says ...
```
`Dog` inherits `speak` and `__init__` but overrides the class attribute `sound`; `self.sound` finds the most specific version.

### Q17. (Day 22) — generators
```text
0 1 [4] []
```
A generator is consumed as you iterate: two `next` calls give 0 and 1, `list(g)` collects the rest (`[4]`), and a second `list(g)` is empty because it is exhausted.

### Q18. (Day 22) — decorators
```text
10
```
`@twice` replaces `add` with `wrapper`, which doubles the original result: (2+3)*2.

### Q19. (Day 23) — regex
```text
['1', '22', '333'] a b c
```
`\d+` finds runs of digits; `\s+` matches any whitespace run (spaces and newline) which is replaced by one space.

### Q20. (Day 26) — pandas groupby
```text
{'A': 90, 'B': 60} (3, 2)
```
City A: 10+30+50 = 90, B: 20+40 = 60. Three rows have sales > 20 and the table has 2 columns, so the shape is (3, 2).

### Q21. (Day 28) — SQL
```text
(5, 2)
```
`WHERE x > 1` keeps 2 and 3 -> sum 5, count 2. `fetchone()` returns a tuple.

### Q22. (Day 3) — types & conversion
```text
float int 34 7
```
`/` always produces a float (even `3 / 1`), `//` of ints stays an int; `+` on two strings concatenates, on ints adds.

### Q23. (Day 8) — zip & enumerate
```text
[('a', 1), ('b', 2)] {1: 'a', 2: 'b'}
```
`zip` pairs items position by position; `enumerate(names, 1)` numbers them starting at 1.

### Q24. (Day 4) — f-string formats
```text
1,234.50 |     1234.5 | 25.6%
```
`:,.2f` adds thousands separators and 2 decimals; `>10.1f` right-aligns in 10 characters; `.1%` multiplies by 100 and adds `%`.

### Q25. (Day 6) — BUG: typo operator
```text
30
```
`=+` is *assignment of a positive number*, not `+=`. Each pass replaces `total`, so the result is just the last item. Fix: `total += p` (expected 60).

### Q26. (Day 10) — BUG: missing key
```text
<raises KeyError>
```
Reading a missing key raises `KeyError`. Fix: `scores.get("bob", 0)` or check `"bob" in scores` first.

### Q27. (Day 8) — BUG: changing a list while looping
```text
[1, 2, 3]
```
Removing items shifts the positions while the `for` loop is still walking, so one `2` gets skipped. Fix: iterate over a copy (`for n in nums[:]`) or build a new list with a comprehension.
