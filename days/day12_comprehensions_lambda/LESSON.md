# Day 12 — Comprehensions, `lambda`, `sorted(key=…)`, `zip`, `enumerate`

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Write short “Pythonic” code to filter, transform, sort and pair data | Intermediate |

## 🌍 Real-world scenario & trend
**E-commerce filters + music charts.** “Show products under ₹1,000, sorted by rating” and “Top 10 most-played songs” are filter + sort + transform operations. **Trend:** readable one-liners like these are exactly what you see in data/AI code; pandas later turns them into column operations. Rule of thumb: if a comprehension doesn't fit comfortably on one line, use a normal loop.

## 0. Warm-up (5 min) — Day 11 recap
- What does `*args` collect?  • What goes wrong with `def f(x, items=[])`?

## 1. Concepts

### 1.1 List comprehension — build a list in one line
```python
nums = [1, 2, 3, 4, 5, 6]
squares = [n * n for n in nums]                  # [1, 4, 9, 16, 25, 36]
evens   = [n for n in nums if n % 2 == 0]        # filter  -> [2, 4, 6]
labels  = ["even" if n % 2 == 0 else "odd" for n in nums]   # transform with if/else
```
Pattern: `[ what_to_keep  for item in source  if condition ]`.

### 1.2 Dict and set comprehensions
```python
{n: n * n for n in range(1, 4)}          # {1: 1, 2: 4, 3: 9}
{w[0] for w in ["apple", "avocado"]}     # {'a'}
```

### 1.3 `zip` and `enumerate`
```python
names, scores = ["Aarav", "Diya"], [88, 95]
list(zip(names, scores))                 # [('Aarav', 88), ('Diya', 95)]
dict(zip(names, scores))                 # {'Aarav': 88, 'Diya': 95}
for rank, name in enumerate(names, start=1):
    print(rank, name)
```

### 1.4 `lambda` — a tiny nameless function
```python
double = lambda x: x * 2                 # same as def double(x): return x * 2
```
Mostly used as a quick `key=`.

### 1.5 `sorted`, `min`, `max` with `key=`
```python
products = [("Pen", 10), ("Bag", 899), ("Book", 120)]
sorted(products, key=lambda p: p[1])                 # by price ascending
sorted(products, key=lambda p: p[1], reverse=True)   # descending
sorted(products, key=lambda p: (-p[1], p[0]))        # price desc, then name A→Z
max(products, key=lambda p: p[1])                    # ('Bag', 899)
```
Sorting by a **tuple** key sorts by the first item, then ties by the second; use a minus sign to reverse a number.

### 1.6 `map`, `filter`, `any`, `all`
```python
list(map(str.upper, ["a", "b"]))         # ['A', 'B']  (comprehension is usually clearer)
any(m < 40 for m in marks)               # is there at least one fail?
all(m >= 40 for m in marks)              # did everybody pass?
```

### 1.7 Generator expression (preview of Day 22)
`sum(n * n for n in range(1_000_000))` — round brackets, no list built in memory.

## 2. Code along → `examples.py`

## 3. Common mistakes
- Too much logic in one comprehension (hard to read) — switch to a loop.
- `[x for x in data if cond else y]` is a SyntaxError (an `if/else` that *changes the value* goes **before** `for`).
- Using a comprehension just for side effects (printing) — use a normal loop.
- Forgetting `list(...)` around `zip/map/filter` when you want to see the values.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Squares, even numbers, uppercase list |
| L2-1…L2-3 | 🟡 | Affordable items under budget, sort words by length, names+scores → dict |
| L3-1, L3-2 | 🔴 | Top-N songs (plays desc, title A→Z), matrix transpose |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>First write it as a normal <code>for</code> loop that appends to a list. Then compress it.</details>
<details><summary>Hint 2</summary>Affordable: <code>sorted([name for name, price in menu.items() if price &lt;= budget])</code>. Sort by length then alphabet: <code>key=lambda w: (len(w), w)</code>. Top songs: <code>key=lambda s: (-s[1], s[0])</code> then take titles of the first n. Transpose: <code>[list(col) for col in zip(*matrix)]</code> or nested comprehension.</details>
<details><summary>Hint 3</summary><code>solutions/day12_solution.py</code></details>

## 6. Quiz — answers in `solutions/day12_answers.md`
1. `[n * 2 for n in range(4)]` → ?
2. `[n for n in range(10) if n % 3 == 0]` → ?
3. `dict(zip(["a", "b"], [1, 2]))` → ?
4. `sorted(["bb", "a", "ccc"], key=len, reverse=True)` → ?
5. Convert `lambda x: x + 1` into a normal function.
6. Where does `if ... else ...` go in a comprehension that transforms values?
7. What does `all([])` return?
8. Why use a tuple like `(-plays, title)` as a sort key?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: nested data (lists of dicts) and the `json` module — a restaurant API.
