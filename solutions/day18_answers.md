# Day 18 — Quiz answers

1. The code under it runs only when the file is executed directly, not when it is imported — so a file can be both a script and a reusable module.
2. To give each project its own isolated set of packages/versions (no conflicts, reproducible setups).
3. It writes all installed packages and exact versions into `requirements.txt` so others can recreate the same environment with `pip install -r requirements.txt`.
4. `[('b', 3)]`.
5. Missing keys automatically get a default (like an empty list), so you don't need `if key not in d` checks.
6. `0` (Monday).
7. It shadows the standard `random` module — `import random` would load your file instead and break your code.
8. `import math` → use `math.sqrt(...)` (namespaced); `from math import sqrt` → use `sqrt(...)` directly.
