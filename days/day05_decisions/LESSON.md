# Day 05 — Decisions: `if / elif / else`, `and / or / not`

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Make programs choose between paths — the heart of every business rule | Beginner |

## 🌍 Real-world scenario & trend
**Delivery-fee rules (Swiggy/Zomato/Amazon) and ATM checks.** “Free delivery for members or orders above ₹499, else ₹30/₹50/₹80 by distance” is literally an `if/elif/else` chain. Fraud detection, pricing engines, loan approvals and game logic are the same idea at scale. **Trend:** modern Python (3.10+) also has `match / case` for multi-way branching (see 1.7).

## 0. Warm-up (5 min) — Day 04 recap
- `"Python"[1:4]`?  • How do you compare two strings ignoring case?

## 1. Concepts

### 1.1 `if / elif / else` — and **indentation is the syntax**
```python
marks = 82
if marks >= 90:
    print("A")
elif marks >= 75:       # checked only if the previous conditions were False
    print("B")
else:                   # runs when nothing above matched
    print("Keep going")
```
Rules: end the condition line with `:`; indent the block by 4 spaces; **first match wins**, the rest are skipped.

### 1.2 Combine conditions: `and`, `or`, `not`
```python
age, has_ticket = 25, True
if age >= 18 and has_ticket:       # both must be True
    print("Enter")
if not has_ticket or age < 5:      # either is enough / negate
    print("Special desk")
```
Chained comparison (Python bonus): `18 <= age < 60`.

### 1.3 Truthy and falsy values
Falsy: `False, 0, 0.0, "", None` (and empty lists/dicts later). Everything else is truthy.
```python
name = ""
if not name:
    print("Please enter your name")
```

### 1.4 Nested `if`
```python
if is_member:
    if order_value > 500:
        print("Free delivery + bonus")
```
Prefer flat `elif` chains or `and` when possible — deep nesting is hard to read.

### 1.5 Conditional expression (one-line if)
```python
status = "adult" if age >= 18 else "minor"
```

### 1.6 `in` for membership
```python
if answer.lower() in ("y", "yes"):  # compares against several values
    print("Confirmed")
```

### 1.7 `match / case` (Python 3.10+)
```python
command = "stop"
match command:
    case "go":
        print("Starting")
    case "stop" | "halt":
        print("Stopping")
    case _:                 # default
        print("Unknown")
```

## 2. Code along → `examples.py` (delivery fee + ticket pricing)

## 3. Common mistakes
- `=` instead of `==` in a condition (`if x = 5` is a SyntaxError).
- Forgetting the `:` or the indentation.
- Wrong order: put the **most specific/strictest** check first (`>= 90` before `>= 75`).
- `if age == 18 or 19:` is always true — write `if age == 18 or age == 19:` (or `age in (18, 19)`).

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Grade letter, sign of a number, max of three |
| L2-1…L2-3 | 🟡 | Delivery fee, ticket price, leap year |
| L3-1, L3-2 | 🔴 | Rock-paper-scissors referee, triangle classifier |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Draw a decision table on paper: rows = situations, columns = result. Then code one row per <code>if/elif</code>.</details>
<details><summary>Hint 2</summary>Delivery: members → 0; elif value ≥ 499 → 0; else by distance. Leap year: divisible by 4 AND (not by 100 OR by 400). Rock-paper-scissors: Draw first; then list the 3 winning pairs for player 1 using <code>or</code>. Triangle: check "not a triangle" first (sum of two sides ≤ third).</details>
<details><summary>Hint 3</summary><code>solutions/day05_solution.py</code></details>

## 6. Quiz — answers in `solutions/day05_answers.md`
1. What is printed? `x = 7` → `if x > 5: print("A")` / `elif x > 3: print("B")` / `else: print("C")`.
2. Is `0`, `""`, `"0"`, `None` truthy or falsy (each)?
3. Why is `if x = 5:` an error?
4. What is wrong with `if color == "red" or "blue":`?
5. Rewrite as one line: if `age >= 18` then `"adult"` else `"minor"`.
6. What does `not (3 > 2 and 1 > 2)` evaluate to?
7. In an `if/elif/elif/else` chain, how many blocks can run?
8. Which keyword is the default case in `match`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: loops — a number-guessing game and patterns.
