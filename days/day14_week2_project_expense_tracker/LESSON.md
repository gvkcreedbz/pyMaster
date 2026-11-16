# Day 14 — 🏆 Week 2 Project: Expense Tracker (and Week-2 Review)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Combine lists, dicts, functions, comprehensions & formatting in one useful program; then test Weeks 1–2 | Intermediate |

## 🌍 Real-world scenario & trend
**A personal-finance app** (Walnut, Splitwise, Money Manager, Google Pay “Spends”). Behind the charts is exactly this: a list of transactions (dicts) + functions to total, filter, group by month/category and compare against a budget. **Trend:** fintech apps lean heavily on data summaries; the same functions you write today are the logic of a real budget feature — and tomorrow's data will come from files instead of memory.

## ⏰ Time plan
| Min | Activity |
|---|---|
| 0–10 | Warm-up: redo any 1 failed exercise from Days 8–13 |
| 10–25 | Read this page + run `examples.py` |
| 25–95 | Build the tracker (`practice.py`, L1 → L2 → L3) |
| 95–115 | **Week-2 Review Test** (closed book) |
| 115–120 | Tracker + weekly reflection |

## 1. Data model
Each expense is a **dict**; the tracker's state is a **list of dicts**:
```python
{"date": "2026-11-16", "category": "Food", "amount": 250.0, "note": "Lunch"}
```

## 2. Functions to write (all in `practice.py`)
| ID | Level | Function | What it does |
|---|---|---|---|
| L1-1 | 🟢 | `add_expense(expenses, date, category, amount, note="")` | Appends a dict; rejects amount ≤ 0 |
| L1-2 | 🟢 | `total_spent(expenses)` | Sum of all amounts |
| L1-3 | 🟢 | `format_expense(e)` | One aligned line of text |
| L2-1 | 🟡 | `totals_by_category(expenses)` | `{category: total}` |
| L2-2 | 🟡 | `filter_expenses(expenses, category=None, min_amount=0)` | Matching expenses |
| L2-3 | 🟡 | `monthly_totals(expenses)` | `{"2026-11": total}` (hint: `date[:7]`) |
| L3-1 | 🔴 | `budget_report(expenses, budgets)` | Lines with spent/budget/percent/status |
| L3-2 | 🔴 | `run_tracker()` | Interactive menu (Add / List / Summary / Quit) |

Play it for real: `python practice.py play`  ·  Stretch: save/load later in Week 3 (files!).

## 3. Code along → `examples.py`

## 4. Hint ladder
<details><summary>Hint 1</summary>Pass the list into every function (no global variables). Each function does <em>one</em> job.</details>
<details><summary>Hint 2</summary>Format line: <code>f"{e['date']} | {e['category']:&lt;10} | Rs. {e['amount']:&gt;9,.2f} | {e['note']}"</code>. Budget status: <code>OVER</code> if spent &gt; budget, else <code>WARN</code> if percent ≥ 80, else <code>OK</code>. In <code>run_tracker</code> reuse <code>add_expense</code>, <code>format_expense</code>, <code>totals_by_category</code>, <code>total_spent</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day14_solution.py</code></details>

## 5. 🧪 Week-2 Review Test (closed book, 20 min — answers in `solutions/day14_answers.md`)
1. `a = [1,2]; b = a; b.append(3)` → `a` is?
2. `[1,2,3,4][1:3]` and `[1,2,3,4][::-1]`?
3. Difference between `list.sort()` and `sorted(list)`?
4. `{1,2,3} & {2,3,4}`; `{1,2} | {2,3}`; `{1,2,3} - {2}`?
5. How do you make an empty set?
6. Safe way to read a possibly missing dict key with default 0?
7. Write the counting pattern for words in `text.split()`.
8. `[x * 2 for x in range(5) if x % 2 == 0]` → ?
9. `sorted(["bb","a","ccc"], key=lambda s: -len(s))` → ?
10. Why is `def f(x, items=[])` a bug waiting to happen?
11. What do `*args` and `**kwargs` collect?
12. What is a base case?
13. `json.dumps` vs `json.loads`?
14. JSON `null/true` become what in Python?
15. Write a one-line expression: names of products with price < 500 from `products = [{"name": ..., "price": ...}, ...]`.

**Scoring:** 13–15 great · 10–12 good · < 10 → spend 20 min tomorrow morning on the Day 8–13 L1 tasks.

## 6. Weekly reflection (tracker → “Weekly Review” sheet)
What was easiest/hardest this week? Which 3 concepts do I still confuse? Hours planned vs actual? What will I change in Week 3?

## 7. ✅ Week-2 checklist
- [ ] I can pick between list / tuple / set / dict for a problem
- [ ] I write functions with defaults, `*args`, `**kwargs` and docstrings
- [ ] I use comprehensions and `sorted(key=...)` comfortably
- [ ] I can navigate nested JSON-style data
- [ ] My tracker passes every check in `practice.py`
