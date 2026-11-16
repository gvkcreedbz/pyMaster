# Day 22 — Generators, Iterators, Decorators & Context Managers

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Process data lazily, wrap functions with extra behaviour, manage resources safely — the “advanced Python” trio | Upper-intermediate |

## 🌍 Real-world scenario & trend
**Streaming a 10-GB log file, timing/retrying API calls, auto-closing database connections.** Generators read one line at a time (constant memory), decorators add logging/retry/caching without touching your function, context managers guarantee cleanup. **Trend:** FastAPI's `@app.get("/")`, pytest's `@pytest.fixture`, Flask routes, `@dataclass`, `@lru_cache` — **decorators are everywhere** in modern Python. Data pipelines (Airflow, pandas chunks, ML data loaders) are built from generators.

## 0. Warm-up (5 min) — Day 21 recap
- What does `@classmethod` receive?  • `Book(**data)` — what does `**` do?

## 1. Concepts

### 1.1 Iterables and iterators
```python
nums = [10, 20, 30]
it = iter(nums)          # get an iterator
next(it), next(it)       # 10, 20
next(it); next(it)       # 30, then StopIteration (what a for-loop catches silently)
```
A `for` loop = “call `iter()` once, call `next()` until `StopIteration`”.

### 1.2 Generators — functions that `yield`
```python
def countdown(n):
    while n > 0:
        yield n              # pause here, hand out a value
        n -= 1               # resume here on the next request

for x in countdown(3):       # 3 2 1
    print(x)
gen = countdown(2)
type(gen)                    # <class 'generator'>   (nothing has run yet!)
```
**Lazy**: values are produced on demand → works for huge/infinite sequences:
```python
def naturals():
    n = 1
    while True:
        yield n; n += 1
from itertools import islice
list(islice(naturals(), 5))  # [1, 2, 3, 4, 5]
```
Generator expression: `(n * n for n in range(10**9))` — nothing is built until you loop.
`yield from other_gen` delegates to another generator. A generator can be used **once**.

### 1.3 Decorators — functions that wrap functions
```python
import functools, time

def timer(func):
    @functools.wraps(func)                  # keeps name/docstring of the original
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer                                       # same as: slow = timer(slow)
def slow():
    time.sleep(0.1)
```
Recipe: outer function takes `func` → inner `wrapper(*args, **kwargs)` calls it → return `wrapper`.

### 1.4 Decorators with arguments (one more layer)
```python
def retry(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ...
        return wrapper
    return decorator

@retry(3)
def call_api(): ...
```

### 1.5 Closures & built-in decorators you should know
`@functools.lru_cache(maxsize=None)` (memoisation), `@staticmethod`, `@classmethod`, `@property`, `@dataclass`, `@contextmanager`. A closure = an inner function that remembers variables of the outer one (the cache dict in `memoize`).

### 1.6 Context managers — `with` for setup + guaranteed cleanup
```python
from contextlib import contextmanager

@contextmanager
def timer_block(label):
    start = time.perf_counter()
    try:
        yield                                  # the body of the with-block runs here
    finally:
        print(label, round(time.perf_counter() - start, 3))

with timer_block("loading"):
    ...
```
Class form uses `__enter__` and `__exit__`. Built-ins you already use: `open`, `sqlite3` connections (Day 28), locks, `tempfile.TemporaryDirectory`, `contextlib.suppress`.

## 2. Code along → `examples.py` (memory comparison, timer/retry decorators, context manager)

## 3. Common mistakes
- Forgetting `return wrapper` (the decorated function becomes `None`).
- Forgetting `functools.wraps` (names/docstrings are lost — breaks debugging and FastAPI).
- Reusing an exhausted generator (second loop is empty).
- Decorator with arguments: `@retry` instead of `@retry(3)`.
- Putting `yield` and `return value` expecting a list — a generator **yields** values.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | `countdown`, infinite `fibonacci_gen`, `running_average` generators |
| L2-1…L2-3 | 🟡 | `count_calls` decorator, `retry(times)` decorator, `ignore_errors` context manager |
| L3-1, L3-2 | 🔴 | `chunked` generator (batching), `memoize` decorator |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>For generators: write the loop that would build a list, then replace <code>append(x)</code> with <code>yield x</code>.</details>
<details><summary>Hint 2</summary>count_calls: put a counter attribute on <code>wrapper</code> (<code>wrapper.calls = 0</code>) and increase it inside. retry: three nested functions (times → func → wrapper). ignore_errors: <code>@contextmanager</code>, <code>try: yield</code>, <code>except exc_types: pass</code>. chunked: collect items in a list; when it reaches <code>size</code>, yield it and start a new one; yield the leftover at the end. memoize: <code>cache = {}</code>; key = <code>args</code> tuple.</details>
<details><summary>Hint 3</summary><code>solutions/day22_solution.py</code></details>

## 6. Quiz — answers in `solutions/day22_answers.md`
1. What does a `for` loop do under the hood?
2. What is the difference between `return` and `yield`?
3. Why are generators memory-friendly?
4. What does `@functools.wraps` do?
5. `@timer` above `def f()` is shorthand for what line?
6. What does a context manager guarantee?
7. Can you iterate a generator twice?
8. Why does `retry(3)` need three nested functions?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: regular expressions, type hints and clean-code habits.
