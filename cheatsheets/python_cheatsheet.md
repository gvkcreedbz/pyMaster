# 🐍 Python Cheatsheet (Weeks 1–4 core language)

## Basics
```python
print("Hi", 5, sep="-", end="!\n")       # Hi-5!
name = input("Name? ")                    # always returns str
age = int(input("Age? "))                 # convert: int() float() str() bool()
print(f"{name} is {age + 1} next year")   # f-string
print(f"{1234.5:,.2f} | {0.256:.1%} | {7:03d} | {'x':>5}")   # 1,234.50 | 25.6% | 007 |     x
# comment        type(x)        id(x)        isinstance(x, int)
```

## Numbers & operators
`+ - * /` (float) `//` (floor) `%` (remainder) `**` (power) · `+= -= *= /=` · `abs round(x, 2) min max sum divmod` · `import math` → `math.sqrt math.ceil math.floor math.pi`
Comparison `== != < <= > >=` · logic `and or not` · membership `in` / `not in` · identity `is` (use for `None`)

## Strings (immutable)
```python
s = "Hello, World"
s[0]  s[-1]  s[0:5]  s[::-1]  len(s)
s.upper() .lower() .title() .strip() .replace("l", "L") .split(", ") ", ".join(list)
s.startswith("He")  s.endswith("d")  s.find("o")  s.count("l")  "lo" in s  s.isdigit()
"""multi
line"""   "tab\t newline\n quote\" backslash\\"   r"raw\d"
```

## Decisions & loops
```python
if x > 0: ...
elif x == 0: ...
else: ...
result = "yes" if x else "no"
match command:                      # Python 3.10+
    case "go" | "run": ...
    case _: ...

for i in range(5): ...              # 0..4        range(1, 6)  range(10, 0, -2)
for i, item in enumerate(items, 1): ...
for a, b in zip(list1, list2): ...
while condition: ...                # break · continue · for/while ... else
```
Falsy: `0 0.0 "" [] {} () set() None False`  — everything else is truthy.

## Collections
| Type | Make | Key operations |
|---|---|---|
| **list** (mutable, ordered) | `[1, 2, 3]` | `.append .extend .insert .remove .pop .sort() sorted() .reverse() .index .count`, slicing, `a[:]` copy |
| **tuple** (immutable) | `(1, 2)` `1,` | unpacking `a, b = t`, swap `a, b = b, a`, dict keys |
| **set** (unique, unordered) | `{1, 2}` `set()` | `.add .discard`, `a & b`, `a \| b`, `a - b`, `a ^ b` |
| **dict** (key → value) | `{"a": 1}` | `d[k]`, `d.get(k, default)`, `d[k] = v`, `del d[k]`, `.keys() .values() .items()`, `.setdefault`, `.update`, `k in d` |
```python
counts = {}
for word in words: counts[word] = counts.get(word, 0) + 1          # counting
groups = {}
for item in items: groups.setdefault(item["type"], []).append(item) # grouping
sorted(counts.items(), key=lambda kv: kv[1], reverse=True)          # sort by value
```

## Comprehensions & functional helpers
```python
[x * x for x in nums if x % 2 == 0]        {w: len(w) for w in words}        {c for c in text}
sum(x for x in nums)                        any(x > 5 for x in nums)          all(...)
sorted(people, key=lambda p: (-p["age"], p["name"]))
list(map(str.upper, words))                 list(filter(None, values))
```

## Functions
```python
def area(width, height=1, *args, scale=1.0, **options):
    """One-line summary."""
    return width * height * scale            # no return → None
area(3, 4);  area(3, height=4);  area(*[3, 4]);  area(**{"width": 3})
# Never: def f(x, bucket=[])  →  def f(x, bucket=None): bucket = bucket or []
lambda x: x * 2        # tiny anonymous function
```
Scope: local → enclosing → global → built-in (LEGB). Use parameters + `return` instead of `global`.

## Files, paths, JSON, CSV
```python
from pathlib import Path
p = Path("data") / "sales.csv";  p.exists();  p.read_text(encoding="utf-8");  p.write_text("hi", encoding="utf-8")
p.parent.mkdir(parents=True, exist_ok=True);  list(Path(".").glob("*.py"));  Path(__file__).parent

with open("f.txt", "w", encoding="utf-8") as f: f.write("line\n")     # modes: r w a  (+ b for bytes)
with open("f.txt", encoding="utf-8") as f:
    for line in f: print(line.rstrip())

import json;  data = json.loads(text);  text = json.dumps(data, indent=2)
json.load(f);  json.dump(data, f, indent=2)

import csv
with open("a.csv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f): print(row["col"])       # all values are str!
with open("b.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["a", "b"]); w.writeheader(); w.writerow({"a": 1, "b": 2})
```

## Errors & logging
```python
try:
    value = int(text)
except ValueError as error:
    print("bad number:", error)
except (KeyError, IndexError):
    ...
else:
    ...          # no error happened
finally:
    ...          # always runs
raise ValueError("price must be positive")
class AppError(Exception): ...
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.info("started");  logging.warning("..."); logging.error("...", exc_info=True)
```

## Modules
```python
import math, random, datetime, collections, itertools, functools, os, sys, re, json, csv, sqlite3, argparse
from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta
if __name__ == "__main__":  main()
```
`python -m venv .venv` → `.venv\Scripts\Activate.ps1` → `python -m pip install x` → `python -m pip freeze > requirements.txt`

## OOP
```python
from dataclasses import dataclass
class Account:
    interest = 0.04                          # class attribute (shared)
    def __init__(self, owner, balance=0):    # constructor
        self.owner = owner                   # instance attributes
        self._balance = balance              # "private" by convention
    @property
    def balance(self): return self._balance
    def deposit(self, amount):
        if amount <= 0: raise ValueError("amount must be positive")
        self._balance += amount
    def __str__(self):  return f"{self.owner}: {self._balance}"
    def __repr__(self): return f"Account({self.owner!r}, {self._balance})"
class Savings(Account):                      # inheritance
    def __init__(self, owner, balance=0, rate=0.05):
        super().__init__(owner, balance); self.rate = rate
@dataclass
class Point: x: float; y: float = 0.0       # auto __init__, __repr__, __eq__
```
Dunder methods: `__len__ __getitem__ __iter__ __eq__ __lt__ __add__ __contains__ __enter__/__exit__`.

## Generators, decorators, context managers
```python
def countdown(n):
    while n > 0:
        yield n; n -= 1                      # lazy, one value at a time
import functools
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter(); result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.perf_counter() - start:.3f}s"); return result
    return wrapper
from contextlib import contextmanager
@contextmanager
def opened(name):
    f = open(name); 
    try: yield f
    finally: f.close()
```

## Type hints
`def f(a: int, b: str = "x") -> list[str]:` · `dict[str, float]` · `int | None` · `from collections.abc import Callable` · checked by tools (`mypy`, Pylance), not at run time.

## Style (PEP 8)
`snake_case` names, `PascalCase` classes, `UPPER_CASE` constants, 4-space indents, lines ≤ 88–100 chars, docstrings for public functions, no magic numbers, early `return` instead of deep nesting. `ruff check .` and `ruff format .`.
