# Day 10 — Quiz answers

1. `d["b"]` raises `KeyError`; `d.get("b")` returns `None`.
2. `"b" in d` (checks keys).
3. `a` then `b` (loop gives keys).
4. `counts[key] = counts.get(key, 0) + 1`.
5. `"x"`, `5`, `(1, 2)` are fine. `[1, 2]` is not (lists are mutable/unhashable).
6. `1` — a repeated key keeps only the last value (`{"a": 2}`).
7. A view of `(key, value)` pairs — usually used as `for k, v in d.items()`.
8. Python's sort is **stable**: items with equal sort keys keep their existing relative order, so the earlier alphabetical order survives among equal counts.
