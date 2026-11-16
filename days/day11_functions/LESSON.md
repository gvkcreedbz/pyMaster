# Day 11 — Functions (reusable building blocks)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Design clean functions: parameters, defaults, `*args/**kwargs`, scope, recursion | Intermediate |

## 🌍 Real-world scenario & trend
**A billing service.** Real systems don't have one giant script; they have small functions — `calculate_tax()`, `apply_coupon()`, `send_receipt()` — each doing one job, each testable. **Trend:** AI coding assistants write functions from docstrings; being able to *read, name and judge* a function is the core professional skill. “Pure functions” (same input → same output, no side effects) are the easiest to test and debug.

## 0. Warm-up (5 min) — Day 10 recap
- How do you count words with a dict?  • `d.get("x", 0)` returns?

## 1. Concepts

### 1.1 Define and call
```python
def greet(name):                 # name = parameter
    """Return a greeting."""     # docstring: what the function does
    return f"Hello, {name}!"

message = greet("Aarav")         # "Aarav" = argument
```

### 1.2 `return` vs `print`
`print` shows something on screen; `return` hands a value back so you can use it. A function without `return` gives `None`.
```python
def add(a, b):
    return a + b
total = add(2, 3) * 10           # 50  (you can't do this if add() only printed)
```

### 1.3 Default and keyword arguments
```python
def price_with_tax(price, qty=1, tax=18):
    return price * qty * (1 + tax / 100)
price_with_tax(100)                 # qty=1, tax=18
price_with_tax(100, tax=5)          # keyword argument: clear and order-free
```
Parameters with defaults must come **after** those without.

### 1.4 `*args` and `**kwargs`
```python
def average(*numbers):             # numbers is a tuple of everything passed
    return sum(numbers) / len(numbers)
average(4, 8, 6)

def show(**fields):                # fields is a dict of keyword args
    for k, v in fields.items():
        print(k, "=", v)
show(name="Aarav", age=25)
```

### 1.5 Return several values
```python
def min_max_avg(nums):
    return min(nums), max(nums), sum(nums) / len(nums)   # a tuple
low, high, avg = min_max_avg([4, 8, 6])
```

### 1.6 Scope — where a variable lives
```python
rate = 10                       # global
def f():
    rate = 99                   # a NEW local variable; global untouched
f(); print(rate)                # 10
```
Prefer passing values in / returning values out instead of using `global`.

### 1.7 Recursion — a function that calls itself
```python
def factorial(n):
    if n <= 1:                  # base case: stops the recursion
        return 1
    return n * factorial(n - 1) # smaller problem
```
Always have a base case. Python stops at ~1000 nested calls (`RecursionError`).

### 1.8 ⚠ The mutable-default trap
```python
def add_item(item, items=[]):     # BUG: the SAME list is reused on every call
    items.append(item); return items
def add_item_ok(item, items=None):# correct pattern
    if items is None:
        items = []
    items.append(item); return items
```

### 1.9 Good function habits
One job per function · verb names (`calculate_total`) · docstring · no hidden global changes · return results instead of printing inside.

## 2. Code along → `examples.py`

## 3. Common mistakes
- Forgetting `return` (result is `None`).  • Calling `greet` without `()` (you get the function object).
- `return` inside a loop returns on the first round.  • Code after `return` never runs.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Default args, tax total, `*args` average |
| L2-1…L2-3 | 🟡 | `**kwargs` profile, multiple returns, Fibonacci (recursion) |
| L3-1, L3-2 | 🔴 | Flatten nested lists (recursion), safe-default pattern |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Write 3 example calls and their expected results first. Then write the function.</details>
<details><summary>Hint 2</summary>Profile: <code>sorted(fields)</code> gives keys alphabetically; build <code>f"{k}={fields[k]}"</code> pieces and join with <code>"; "</code>. Fibonacci: base cases 0 → 0, 1 → 1, otherwise sum of the previous two calls. Flatten: loop over items; if <code>isinstance(x, list)</code> extend with <code>flatten(x)</code>, else append.</details>
<details><summary>Hint 3</summary><code>solutions/day11_solution.py</code></details>

## 6. Quiz — answers in `solutions/day11_answers.md`
1. Parameter vs argument?
2. What does a function without `return` give back?
3. Why is `def f(x, items=[])` dangerous?
4. In `def f(*args, **kwargs)`, what are `args` and `kwargs`?
5. What is a base case in recursion?
6. `x = 5` globally, then `def f(): x = 10` and `f()`. What is `x` afterwards?
7. Why can't `def f(a=1, b)` exist?
8. What is the difference between `return a, b` and `print(a, b)`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: comprehensions, `lambda`, `sorted(key=...)`, `zip` — the Pythonic toolbox.
