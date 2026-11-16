# Day 10 — Dictionaries (key → value)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Model real records and count/group data with dictionaries | Beginner+ → Intermediate |

## 🌍 Real-world scenario & trend
**Phone contact book, product inventory, user profile, word counts.** Every web API (weather, payments, Instagram) sends **JSON, which is essentially a Python dict**. Configuration files, database rows and pandas rows map to dicts. **Trend:** “count/group by key” (word frequency, sales per region) is the most common data-analysis pattern — you will do it with pandas on Day 26, but the idea starts here.

## 0. Warm-up (5 min) — Day 09 recap
- `{1,2,3} - {2}`?  • Difference between a list and a tuple?

## 1. Concepts

### 1.1 Create and read
```python
user = {"name": "Aarav", "age": 25, "city": "Pune"}
user["name"]                 # 'Aarav'
user["email"]                # KeyError (missing key!)
user.get("email")            # None            (safe)
user.get("email", "n/a")     # 'n/a'           (safe + default)
"age" in user                # True (checks KEYS)
```

### 1.2 Add, change, delete
```python
user["email"] = "a@x.com"    # add
user["age"] = 26             # change
user.update({"city": "Delhi", "vip": True})   # many at once
removed = user.pop("vip")    # remove & return
del user["email"]
```

### 1.3 Loop
```python
for key in user:                    # keys
    print(key)
for value in user.values():
    print(value)
for key, value in user.items():     # both (most common)
    print(f"{key}: {value}")
```
Keys must be **unique and immutable** (text, numbers, tuples). Insertion order is preserved (Python 3.7+).

### 1.4 The counting pattern ⭐
```python
text = "to be or not to be"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1     # 0 if first time seen
print(counts)       # {'to': 2, 'be': 2, 'or': 1, 'not': 1}
```

### 1.5 The grouping pattern ⭐
```python
groups = {}
for word in ["apple", "avocado", "banana"]:
    first = word[0]
    if first not in groups:
        groups[first] = []
    groups[first].append(word)         # {'a': ['apple', 'avocado'], 'b': ['banana']}
```
(`groups.setdefault(first, []).append(word)` is the one-line version.)

### 1.6 Sorting a dict’s keys by value
```python
sorted(counts)                                  # keys alphabetically
sorted(counts, key=counts.get, reverse=True)    # keys by count, biggest first
```
Python's sort is **stable**: equal items keep their previous order. So sort alphabetically first, then by count → ties stay alphabetical.

### 1.7 Nested dictionaries
```python
inventory = {"pen": {"price": 10, "stock": 50}, "book": {"price": 120, "stock": 5}}
inventory["book"]["stock"] -= 1
```

## 2. Code along → `examples.py`

## 3. Common mistakes
- `KeyError`: use `.get()` or check `in` first.
- Using a list as a key (`TypeError: unhashable`).
- Forgetting that `for x in d` gives **keys**, not values.
- Modifying a dict's size while looping over it (`RuntimeError`) — loop over `list(d)`.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Safe price lookup, add stock, inventory value |
| L2-1…L2-3 | 🟡 | Word frequency, group by first letter, merge & sum two dicts |
| L3-1, L3-2 | 🔴 | Top-N words (ties alphabetical), first non-repeating character |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Ask: “What is my key? What is my value? What is the value when I see the key for the first time?”</details>
<details><summary>Hint 2</summary>Word frequency: lowercase, remove <code>. , ! ?</code>, split, counting pattern. Merge: start with a copy of <code>a</code>, then for each key in <code>b</code> add using <code>.get(key, 0)</code>. Top-N: <code>words = sorted(freq)</code> then <code>sorted(words, key=freq.get, reverse=True)[:n]</code>. First unique char: count first, then scan the text again.</details>
<details><summary>Hint 3</summary><code>solutions/day10_solution.py</code></details>

## 6. Quiz — answers in `solutions/day10_answers.md`
1. `d = {"a": 1}` → what do `d["b"]` and `d.get("b")` do?
2. How do you check whether a key exists?
3. `for x in {"a": 1, "b": 2}: print(x)` prints?
4. How do you add 1 to a counter that may not exist yet?
5. Which can be a dict key: `"x"`, `5`, `(1,2)`, `[1,2]`?
6. `len({"a": 1, "a": 2})` → ?
7. What does `d.items()` give you?
8. Why does sorting alphabetically first, then by count, keep ties alphabetical?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: functions — write reusable, well-named building blocks.
