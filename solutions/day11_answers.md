# Day 11 — Quiz answers

1. A **parameter** is the name in the definition (`def f(x)`); an **argument** is the value you pass (`f(5)`).
2. `None`.
3. The default list is created once and shared by every call, so items pile up between calls. Use `items=None` and create the list inside.
4. `args` is a tuple of extra positional arguments; `kwargs` is a dict of extra keyword arguments.
5. The simplest input where the function returns without calling itself again; it stops the recursion.
6. `5` — the `x = 10` inside the function is a separate local variable.
7. Parameters with defaults must come after those without (`def f(b, a=1)`).
8. `return a, b` hands back a tuple the caller can use; `print(a, b)` only displays text and the function returns `None`.
