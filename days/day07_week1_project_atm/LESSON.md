# Day 07 — 🏆 Week 1 Project: Mini ATM + Guessing Game  (and Week-1 Review)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Combine variables, strings, operators, `if`, loops into one working program, then test yourself on Week 1 | Beginner → Beginner+ |

## 🌍 Real-world scenario & trend
**An ATM (and every “menu-driven” app).** A bank ATM = ask PIN → show menu → loop until Exit → each option validates input with business rules. This “**input → validate → act → repeat**” loop is the skeleton of CLI tools, chatbots and game loops. **Trend:** professionals test such flows automatically — today your checker feeds *fake keyboard input* to your ATM, a preview of Day 24 (testing).

## ⏰ Time plan
| Min | Activity |
|---|---|
| 0–10 | Warm-up: re-read your Bug Journal (what mistakes keep repeating?) |
| 10–30 | Read this page + run `examples.py` (menu-loop pattern) |
| 30–90 | Build the project in `practice.py` (L1 → L2 → L3) |
| 90–110 | **Week-1 Review Test** (below, closed book) |
| 110–120 | Update tracker, weekly reflection |

## 1. Project brief
Build the logic of a mini ATM. Pieces (all in `practice.py`):

```text
            +--------------------+
            | run_atm(balance,pin)|
            +---------+----------+
                      v
          ask PIN (max 3 tries) --wrong x3--> "Card blocked" -> return
                      | correct
                      v
     +--------> show menu 1 Balance 2 Deposit 3 Withdraw 4 Exit
     |                |
     |   1 -> format_balance()       2 -> deposit()
     |   3 -> validate_withdrawal() -> subtract + track daily total
     |   4 -> "Thank you!" -> return final balance
     +----------------+
```
**Business rules (from Day 5):** withdrawal must be a positive multiple of 100, not above the balance, and the total withdrawn today must not exceed ₹20,000.

### The menu-loop pattern
```python
while True:
    choice = input("Choose: ")
    if choice == "4":
        break
    elif choice == "1":
        ...
    else:
        print("Invalid option")
```

## 2. Code along → `examples.py` (a tiny tip-calculator menu using the same pattern)

## 3. Tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | `deposit`, `format_balance`, `guess_feedback` |
| L2-1, L2-2 | 🟡 | `validate_withdrawal`, `play_guessing_game` |
| L3-1 | 🔴 | `run_atm` — the full interactive program |

Stretch (not auto-checked): add a PIN-change option, a mini-statement, or a 4th wrong-PIN lock timer.
Play it for real: `python practice.py play`

## 4. Hint ladder
<details><summary>Hint 1</summary>Make every small function pass first (L1, L2). <code>run_atm</code> mostly just <em>calls</em> them.</details>
<details><summary>Hint 2</summary>Inside <code>run_atm</code>: variables <code>balance</code>, <code>withdrawn_today</code>; a PIN loop with a counter; then <code>while True</code> menu. For withdraw: <code>reason = validate_withdrawal(...)</code>; if <code>reason == "OK"</code> subtract and add to <code>withdrawn_today</code>, else print the reason. Messages must match the task text exactly.</details>
<details><summary>Hint 3</summary><code>solutions/day07_solution.py</code></details>

## 5. 🧪 Week-1 Review Test (closed book, 20 min — answers in `solutions/day07_answers.md`)
1. Output of `print("Hi", "there", sep="_")`?
2. Type of `input("x")` and of `3 / 1`?
3. Evaluate `17 // 5`, `17 % 5`, `2 ** 4`.
4. `name = "Aarav"` → what are `name[0]`, `name[-1]`, `name[1:3]`?
5. Why does `"3" + 4` fail and how do you fix it?
6. What does `" a b ".strip().upper()` return?
7. What is `bool("False")`?
8. `x = 5` → `print(x > 3 and x < 5)` prints?
9. What is printed? `for i in range(1, 8, 3): print(i)`
10. How many times does this run? `i = 0` / `while i < 3: i += 1`
11. Find the bug: `if age = 18:`
12. Find the bug: `total = 0` inside the loop body when summing prices.
13. Difference between `break` and `continue`?
14. What does `round(0.1 + 0.2, 2) == 0.3` give and why use `round` here?
15. Write one `f-string` that prints a price `1234.5` as `Rs. 1,234.50`.

**Scoring:** 13–15 great · 10–12 good (re-read weak spots) · below 10 → redo Day 2–6 L1 tasks tomorrow morning (15 min) before starting Day 8.

## 6. Weekly reflection (write in the tracker “Weekly Review” sheet)
What was easiest? What was hardest? Which 3 concepts do I still confuse? Hours spent vs planned?

## 7. ✅ Week-1 checklist
- [ ] I can explain variables, types and f-strings
- [ ] I can write if/elif/else with and/or/not
- [ ] I can write for and while loops with break/continue
- [ ] I can read a traceback and find the failing line
- [ ] My ATM passes every check in `practice.py`
