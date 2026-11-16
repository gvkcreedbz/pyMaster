# Day 22 — Quiz answers

1. It calls `iter()` on the iterable once, then calls `next()` repeatedly until `StopIteration` is raised, running the loop body for each value.
2. `return` ends the function once and hands back one value; `yield` hands back a value and **pauses**, so the function can continue later and produce many values.
3. They produce one item at a time instead of building the whole collection in memory.
4. It copies the original function's name, docstring and metadata onto the wrapper so the decorated function still looks like the original (important for debugging, docs and frameworks).
5. `f = timer(f)`.
6. That the cleanup code (`__exit__` / the code after `yield`) runs when the block ends, even if an error occurred.
7. No — a generator is exhausted after one pass; create a new one.
8. Layer 1 takes the argument (`times`), layer 2 takes the function (`func`), layer 3 is the wrapper that runs on each call.
