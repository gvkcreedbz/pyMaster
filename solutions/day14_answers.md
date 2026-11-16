# Day 14 — Week-2 Review Test answers

1. `[1, 2, 3]` — `b` is the same list as `a`.
2. `[2, 3]` and `[4, 3, 2, 1]`.
3. `list.sort()` sorts in place and returns `None`; `sorted(list)` returns a new sorted list and leaves the original unchanged.
4. `{2, 3}`; `{1, 2, 3}`; `{1, 3}`.
5. `set()` (`{}` is an empty dict).
6. `d.get(key, 0)`.
7. `counts = {}` / `for w in text.split(): counts[w] = counts.get(w, 0) + 1`.
8. `[0, 4, 8]`.
9. `['ccc', 'bb', 'a']`.
10. The default list is created once and shared by all calls, so data from earlier calls leaks into later ones. Use `items=None`.
11. `*args` → extra positional arguments as a tuple; `**kwargs` → extra keyword arguments as a dict.
12. The case where the function returns without calling itself again (it ends the recursion).
13. `dumps`: Python data → JSON text. `loads`: JSON text → Python data.
14. `None` and `True`.
15. `[p["name"] for p in products if p["price"] < 500]`.
