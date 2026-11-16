# Day 16 — CSV & JSON Files

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Turn real spreadsheet exports into insights with the `csv` module; save/load settings with `json` | Intermediate |

## 🌍 Real-world scenario & trend
**A sales report from an Excel/ERP export.** Every company has CSV exports (orders, attendance, bank statements). Analysts load them, total by region/month, and write a new CSV for management. App settings are stored as JSON. You will analyse `datasets/sales.csv` (300 orders) and `datasets/students.csv`. **Trend:** this is exactly the *Extract → Transform → Load* (ETL) idea behind data engineering; Day 25–26 do the same with pandas in 3 lines — but you must know what happens underneath.

## 0. Warm-up (5 min) — Day 15 recap
- Which open mode appends?  • Why `encoding="utf-8"`?

## 1. Concepts

### 1.1 CSV = text with commas
```text
order_id,order_date,region,quantity,unit_price,discount_pct
ORD1001,2026-01-02,North,2,1999,5
```

### 1.2 Read with `DictReader` (each row → a dict keyed by the header)
```python
import csv
with open("sales.csv", newline="", encoding="utf-8") as f:     # newline="" is required for csv
    for row in csv.DictReader(f):
        print(row["region"], row["quantity"])
```
**Everything is read as text!** Convert yourself: `int(row["quantity"])`, `float(row["unit_price"])`.

### 1.3 Write with `DictWriter`
```python
rows = [{"month": "2026-01", "orders": 26}, {"month": "2026-02", "orders": 25}]
with open("report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["month", "orders"])
    writer.writeheader()
    writer.writerows(rows)
```
(Plain `csv.reader` / `csv.writer` use lists instead of dicts.)

### 1.4 Revenue formula for the sales file
`revenue = quantity × unit_price × (1 − discount_pct / 100)`

### 1.5 JSON files: `load` / `dump` (no “s” → files!)
```python
import json
settings = {"theme": "dark", "currency": "INR", "limits": {"daily": 20000}}
with open("settings.json", "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
with open("settings.json", encoding="utf-8") as f:
    loaded = json.load(f)
```
`dump/load` ↔ files; `dumps/loads` ↔ strings.

### 1.6 Merging configs (defaults + user overrides)
Real apps keep `defaults.json` and let a user file override only some keys — a *deep merge* handles nested dicts (today's L3-2).

### 1.7 Pattern: the “group & total” loop
```python
totals = {}
for row in rows:
    totals[row["region"]] = totals.get(row["region"], 0) + revenue(row)
```

## 2. Code along → `examples.py`

## 3. Common mistakes
- Forgetting `newline=""` (blank lines between rows on Windows).
- Doing maths on text (`"3" * 1999` repeats text!). Convert first.
- Mixing up `json.load` (file) and `json.loads` (string).
- Not handling a missing file/key in real exports (blank cells!) — see Day 17.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Read CSV to dicts, total revenue, JSON save/load |
| L2-1…L2-3 | 🟡 | Revenue per region, write a CSV, top students |
| L3-1, L3-2 | 🔴 | Monthly sales report CSV, deep-merge JSON configs |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Print the first 3 rows (<code>print(rows[:3])</code>) to see the exact keys and types.</details>
<details><summary>Hint 2</summary>Revenue helper: <code>int(r["quantity"]) * int(r["unit_price"]) * (1 - int(r["discount_pct"]) / 100)</code>. Top students: average = (math + science + english) / 3, sort by <code>(-avg, name)</code>. Monthly report: month = <code>order_date[:7]</code>; keep <code>orders</code> and <code>revenue</code> per month; write months in sorted order. Deep merge: loop over user keys; if both values are dicts → recurse, else overwrite.</details>
<details><summary>Hint 3</summary><code>solutions/day16_solution.py</code></details>

## 6. Quiz — answers in `solutions/day16_answers.md`
1. In what type does `csv.DictReader` give you a quantity of `3`?
2. Why `newline=""` when opening a CSV?
3. `json.load` vs `json.loads`?
4. Which function writes the header row in `DictWriter`?
5. What is the revenue formula used today?
6. How do you get `"2026-01"` from `"2026-01-22"`?
7. What does `ensure_ascii=False` do?
8. What is a “deep merge”?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: errors, exceptions & logging — making programs robust.
