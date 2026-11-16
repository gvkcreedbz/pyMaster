# Day 13 — Nested Data & JSON

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Read, query, group and summarise API-style data (lists of dicts) and convert it to/from JSON | Intermediate |

## 🌍 Real-world scenario & trend
**A restaurant-listing API (Zomato/Swiggy style).** The server returns *JSON*: a list of restaurants, each a dict with a list of cuisines inside. Your job as a developer: filter by city, compute averages, group and re-shape that data. **Trend:** JSON is the universal data format of web APIs, config files and LLM tool calls — handling nested JSON confidently is a daily skill for backend, data and AI engineers.

## 0. Warm-up (5 min) — Day 12 recap
- `[n for n in range(6) if n % 2]` → ?  • What is `key=` in `sorted`?

## 1. Concepts

### 1.1 Nested structures
```python
restaurants = [
    {"name": "Spice Hub", "city": "Delhi", "rating": 4.5, "cuisines": ["North Indian", "Chinese"]},
    {"name": "Dosa Corner", "city": "Pune", "rating": 4.2, "cuisines": ["South Indian"]},
]
restaurants[0]["cuisines"][1]        # 'Chinese'
restaurants[1]["city"]               # 'Pune'
```
Read it like a path: list index → dict key → list index.

### 1.2 Loop, filter, summarise
```python
delhi = [r["name"] for r in restaurants if r["city"] == "Delhi"]
avg = sum(r["rating"] for r in restaurants) / len(restaurants)
best = max(restaurants, key=lambda r: r["rating"])
```

### 1.3 Group into a dict of lists
```python
by_city = {}
for r in restaurants:
    by_city.setdefault(r["city"], []).append(r["name"])
```

### 1.4 The `json` module
```python
import json
text = json.dumps(restaurants[0], indent=2)       # Python -> JSON text (a str)
data = json.loads('{"price": 99, "tags": ["a"], "vip": true, "coupon": null}')  # JSON text -> Python
print(data["vip"], data["coupon"])                # True None
```
| Python | JSON |
|---|---|
| dict / list / str / int / float | object / array / string / number |
| `True / False / None` | `true / false / null` |
Keys in JSON are always strings. Tuples become arrays. `json.dumps(obj, sort_keys=True)` makes output order stable.

### 1.5 Safe access to deep data
```python
order = {"customer": {"address": {"city": "Pune"}}}
order.get("customer", {}).get("address", {}).get("pin", "unknown")   # no KeyError
```

### 1.6 Copy: shallow vs deep
```python
import copy
a = {"tags": ["x"]}
b = a.copy()              # shallow: inner list is SHARED
c = copy.deepcopy(a)      # fully independent
```

### 1.7 Pretty-printing for debugging
`print(json.dumps(data, indent=2))` — the quickest way to *see* nested data.

## 2. Code along → `examples.py`

## 3. Common mistakes
- Forgetting that `json.dumps` returns **text**, and `json.loads` needs **text** (not a dict).
- Single quotes in a JSON string (`'{"a": 1}'` is fine; `"{'a': 1}"` is invalid JSON).
- `KeyError` on missing keys in real-world data — use `.get`.
- Shallow copy surprises with nested lists/dicts.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Names in a city, average rating, dict → JSON text |
| L2-1…L2-3 | 🟡 | Best restaurant per city, cuisine index, total from a JSON order |
| L3-1, L3-2 | 🔴 | City summary report, `deep_get("a.b.0.c")` path lookup |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Print one restaurant, then work out the path to the value you need on paper.</details>
<details><summary>Hint 2</summary>Best per city: loop; keep the best seen so far in a dict. Cuisine index: nested loop (restaurant → each cuisine) with <code>setdefault</code>, then sort each list. Order total: <code>json.loads</code> then loop items. City summary: first group restaurants per city, then compute count/averages (<code>round(..., 2)</code>). deep_get: split the path on <code>"."</code>; for each part, if current is a list use <code>int(part)</code> as index, else use it as a dict key; return <code>default</code> on any problem.</details>
<details><summary>Hint 3</summary><code>solutions/day13_solution.py</code></details>

## 6. Quiz — answers in `solutions/day13_answers.md`
1. What does `json.dumps` return? And `json.loads` takes what?
2. JSON `null`, `true` in Python?
3. Path to `"Chinese"` in the example above?
4. Why use `.get("a", {}).get("b")` on nested data?
5. Difference between `.copy()` and `copy.deepcopy()`?
6. Are JSON object keys always strings?
7. How do you pretty-print a dict?
8. What happens to a tuple in `json.dumps`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: **Week-2 project — Expense Tracker** + review test.
