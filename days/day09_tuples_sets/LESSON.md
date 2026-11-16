# Day 09 — Tuples & Sets

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Use tuples for fixed records and sets for uniqueness and fast “who is in both / only one?” questions | Beginner+ |

## 🌍 Real-world scenario & trend
**Instagram “mutual friends” and “unique visitors”.** Counting *unique* users per day, finding followers you share with someone, de-duplicating tags — all set operations. Latitude/longitude pairs, RGB colours and database rows are tuples. **Trend:** sets power fast lookups (checking `x in my_set` is near-instant even with millions of items) — a key interview and performance idea.

## 0. Warm-up (5 min) — Day 08 recap
- How do you make a real copy of a list?  • What does `lst.sort()` return?

## 1. Concepts

### 1.1 Tuples: ordered, **immutable**
```python
point = (28.61, 77.21)         # latitude, longitude
lat, lon = point               # unpacking
point[0]                       # 28.61
# point[0] = 1  -> TypeError (cannot change)
single = (5,)                  # one-item tuple needs the comma
```
Use a tuple when the data is a fixed record; use a list when it grows/changes. Functions that “return two things” really return a tuple.

### 1.2 Swap two variables
```python
a, b = 1, 2
a, b = b, a        # a=2, b=1  (no temp variable needed)
```

### 1.3 Sets: unordered, **unique** items
```python
visitors = {"aarav", "diya", "aarav"}     # {'aarav', 'diya'}  duplicates vanish
unique = set([1, 2, 2, 3, 3, 3])          # {1, 2, 3}
empty = set()                             # NOT {}  (that is an empty dict)
visitors.add("kabir");  visitors.discard("zoya")   # discard: no error if missing
"diya" in visitors                         # True (very fast)
```
No indexing (`s[0]` fails) — sets have no order.

### 1.4 Set maths (Venn diagrams)
```python
mine, hers = {"A", "B", "C"}, {"B", "C", "D"}
mine | hers     # union        {'A','B','C','D'}
mine & hers     # intersection {'B','C'}       <- mutual friends
mine - hers     # difference   {'A'}           <- only mine
mine ^ hers     # symmetric    {'A','D'}       <- in exactly one
{"B"} <= mine   # subset test  True
```

### 1.5 Quick de-duplication
`list(set(items))` removes duplicates but **loses order**. To keep order, track what you have `seen` in a set (today's L2-3).

## 2. Code along → `examples.py`

## 3. Common mistakes
- `{}` is an empty **dict**, not an empty set.
- Expecting a set to keep insertion order.
- Trying to put a list inside a set (`{[1,2]}` → `TypeError: unhashable`). Use a tuple.
- `("a")` is just text; `("a",)` is a tuple.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Unique count, swap, min & max as a tuple |
| L2-1…L2-3 | 🟡 | Mutual followers, friend suggestions, de-duplicate keeping order |
| L3-1, L3-2 | 🔴 | First duplicate, “two numbers add up to target” |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Draw two circles (Venn) and shade the region you need; map it to <code>| &amp; - ^</code>.</details>
<details><summary>Hint 2</summary>Mutual followers: <code>sorted(set(a) &amp; set(b))</code>. Suggestions: <code>set(their) - set(mine) - {me}</code>. Keep-order dedupe: loop, if item not in <code>seen</code> → append and add to <code>seen</code>. Two-sum: for each number, check if <code>target - n</code> is already in a <code>seen</code> set.</details>
<details><summary>Hint 3</summary><code>solutions/day09_solution.py</code></details>

## 6. Quiz — answers in `solutions/day09_answers.md`
1. `type({})` is `dict` or `set`? How do you make an empty set?
2. `{1, 2, 3} & {2, 3, 4}` → ?
3. Why can't you do `my_set[0]`?
4. `t = (1, 2, 3)`; what does `t[0] = 9` do?
5. How do you swap `a` and `b` in one line?
6. `len({1, 1, 2, 2, 3})` → ?
7. Which is faster for “is x in the collection?” on 1 million items: list or set?
8. What is `(5)` vs `(5,)`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: dictionaries — contact books, inventory and word counts.
