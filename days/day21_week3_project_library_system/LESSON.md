# Day 21 — 🏆 Week 3 Project: Library Management System (and Week-3 Review)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Design classes that work together, enforce business rules with exceptions, and persist state to JSON | Intermediate |

## 🌍 Real-world scenario & trend
**A public-library / office-asset system.** Books (or laptops, or bikes) are lent to members for 14 days; late returns cost ₹5/day; each member may hold at most 3 items; staff want an overdue report and a “most borrowed” list. That is a classic *CRUD + business rules + persistence* application — the same shape as inventory, rentals and booking systems. **Trend:** the design you practise here (classes + rules + JSON file) is what you'd later swap for a database (Day 28) and a web API (Day 30).

## ⏰ Time plan
| Min | Activity |
|---|---|
| 0–10 | Warm-up: redo 1 failed exercise from Days 15–20 |
| 10–25 | Read the design below + run `examples.py` |
| 25–95 | Build the system in `practice.py` (L1 → L2 → L3) |
| 95–115 | **Week-3 Review Test** (closed book) |
| 115–120 | Tracker + weekly reflection |

## 1. Design
```text
Book (dataclass)            Library
  isbn, title, author,        books:  {isbn: Book}
  copies=1                    loans:  [{"isbn", "member", "out": "YYYY-MM-DD"}]
                              checkout_counts: {isbn: times borrowed}

Rules: loan period 14 days · late fee Rs. 5 per late day · max 3 active loans per member
Errors: LibraryError("Unknown book" | "No copies available" | "Loan limit reached" | "No such loan")
```
Methods (all in `practice.py`):
| ID | Level | Piece |
|---|---|---|
| L1-1 | 🟢 | `Book` dataclass |
| L1-2 | 🟢 | `add_book`, `find(text)` (case-insensitive title search) |
| L1-3 | 🟢 | `available_copies(isbn)` |
| L2-1 | 🟡 | `checkout(isbn, member, date_text)` with all rules |
| L2-2 | 🟡 | `return_book(isbn, member, date_text)` → returns the late fee |
| L2-3 | 🟡 | `save(path)` and `Library.load(path)` (JSON) |
| L3-1 | 🔴 | `overdue_report(today_text)` |
| L3-2 | 🔴 | `popular_books(n)` |

Stretch (not auto-checked): build a small menu (`run_library_cli`) using `input()`; add a `Member` class; send the overdue report to a file with `logging`.

## 2. Code along → `examples.py` (a short guided tour of the finished idea — read it, then build yours)

## 3. Hint ladder
<details><summary>Hint 1</summary>Make <code>__init__</code> (given) your map: <code>self.books</code>, <code>self.loans</code>, <code>self.checkout_counts</code>. Every method only reads/changes those three things.</details>
<details><summary>Hint 2</summary>available = <code>books[isbn].copies</code> minus the number of active loans with that isbn. Late days = <code>(return_date - out_date).days - 14</code>, never below 0. Dates: <code>date.fromisoformat</code>. Save: <code>asdict(book)</code> for each book, <code>json.dump(..., indent=2)</code>; load: <code>Book(**data)</code>. Overdue line: <code>f"{member}: {title} ({late} days late)"</code>, sorted.</details>
<details><summary>Hint 3</summary><code>solutions/day21_solution.py</code></details>

## 4. 🧪 Week-3 Review Test (closed book, 20 min — answers in `solutions/day21_answers.md`)
1. Open modes `"r"`, `"w"`, `"a"` — what does each do?
2. Why `with open(...)`? Why `encoding="utf-8"`?
3. `csv.DictReader` gives each value as which type?
4. `json.dump` vs `json.dumps`?
5. Order of blocks in `try`, and when `else`/`finally` run?
6. Why is bare `except:` bad?
7. What is `if __name__ == "__main__":` for?
8. Why use a virtual environment?
9. `self` — what is it?
10. What is wrong with `class Cart: items = []`?
11. What does `super().__init__()` do?
12. Which dunder makes `len(x)` work? And `x == y`?
13. Difference between `@classmethod` and `@staticmethod`.
14. What does `@dataclass` generate for you?
15. “IS-A” or “HAS-A” → inheritance?

**Scoring:** 13–15 great · 10–12 good · < 10 → re-do Day 15–20 L1 tasks tomorrow (20 min).

## 5. Weekly reflection (tracker → “Weekly Review”)
Easiest/hardest this week? Concepts I still confuse? Hours planned vs actual? **Week 4 plan:** generators/decorators → regex/typing → pytest/git → NumPy/pandas ×2 → APIs/scraping → SQL → capstone → FastAPI + final exam.

## 6. ✅ Week-3 checklist
- [ ] I read/write text, CSV and JSON files confidently
- [ ] I handle errors with specific `except` blocks and log events
- [ ] I can create a venv and use standard-library modules
- [ ] I can design 2–3 cooperating classes
- [ ] My Library passes every check in `practice.py`
