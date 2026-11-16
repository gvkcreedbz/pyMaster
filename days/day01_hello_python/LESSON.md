# Day 01 — Hello, Python! (How a computer follows instructions)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h (incl. 30 min setup) | Run your first program, print text and numbers, read an error message without panic | Beginner |

## 🌍 Real-world scenario & trend
**A café receipt printer.** Every POS machine, food-delivery app and ATM runs *instructions*: "print the shop name, print each item, print the total". That is all a program is — a list of instructions executed top to bottom.

**Why Python?** It consistently ranks #1–#2 in popularity (TIOBE index, Stack Overflow survey). Instagram's backend runs on Django (Python), Netflix and Spotify use it for automation and data, and almost all modern AI/ML tooling (pandas, PyTorch, scikit-learn) is Python-first. That is why this plan ends with data + automation + a small API.

---

## 0. Setup (≈30 min) — skip what you already did
1. Follow `SETUP.md` in the project root (install Python 3.13, tick **Add python.exe to PATH**).
2. Open a terminal in Cursor (**Ctrl + `**) and check:
   ```powershell
   python --version      # should print Python 3.13.x
   ```
3. Try the **REPL** (a live calculator for Python). Type `python`, press Enter, then:
   ```python
   >>> 2 + 3
   5
   >>> print("Hello")
   Hello
   >>> exit()
   ```

## 1. Concepts (with tiny code)

### 1.1 A program = instructions, top → bottom
```python
print("Welcome to Chai Point")   # line 1 runs first
print("One masala chai, please") # line 2 runs second
```

### 1.2 `print()` shows things on screen
```python
print("Hello, World!")   # text goes in quotes
print(2 + 3)             # numbers do not need quotes -> 5
print("2 + 3")           # in quotes it is just text -> 2 + 3
```

### 1.3 Comments — notes for humans (Python ignores them)
```python
# This is a comment
print("Hi")  # this is also a comment
```

### 1.4 Useful `print` tricks
```python
print("A", "B", "C")            # A B C       (space between)
print("A", "B", sep="-")        # A-B         (change the separator)
print("Loading", end="...")     # no new line after this print
print("done")                   # Loading...done
print("Line 1\nLine 2")         # \n = new line
print("Name\tPrice")            # \t = tab (aligns columns)
print("=" * 20)                 # ==================== (repeat text)
```

### 1.5 Variables (preview — full lesson tomorrow)
A variable is a **label stuck on a value**: `shop = "Chai Point"`. Use it later with `print(shop)`.

### 1.6 Errors are normal (every developer sees hundreds a day)
```python
print("Hello)      # SyntaxError: unterminated string literal  -> you forgot a quote
Print("Hello")     # NameError: name 'Print' is not defined    -> Python is CASE-SENSITIVE
print(hello)       # NameError: name 'hello' is not defined    -> text needs quotes
```
**How to read a traceback:** read the **last line first** (error type + message), then look at the line number just above it.

## 2. Code along (30 min) → `examples.py`
Open `examples.py`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `python examples.py` (inside this folder) or the ▶ Run button.

## 3. Common mistakes
- Using “curly quotes” pasted from Word/WhatsApp instead of straight `"`.
- Forgetting the closing `)` or quote.
- Writing `print` with a capital P.
- Indenting a line by accident (Python cares about spaces at the start of a line).

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 Beginner | Store text/number results in variables |
| L2-1, L2-2 | 🟡 Intermediate | Print a receipt; use `sep` and `end` |
| L3-1 | 🔴 Challenge | Draw a star triangle with `print` |

Run `python practice.py` — the auto-checker prints `[PASS]` / `[FAIL]` for every task.
*(Tasks with `def name():` are “boxes” you fill in — you will master functions on Day 11. For now just add `print(...)` lines inside.)*

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 — Direction</summary>
Re-read section 1.2 and 1.4. Compare the exact text in the task with what you print, character by character (spaces count!).
</details>
<details><summary>Hint 2 — Shape of the answer</summary>
L1: <code>name = value</code>. L2-1: five <code>print(...)</code> lines inside the box. L2-2: one print with <code>sep</code>, one with <code>end</code>. L3-1: <code>print("*" * 1)</code>, <code>print("*" * 2)</code>…
</details>
<details><summary>Hint 3 — Peek (last resort)</summary>
Open <code>solutions/day01_solution.py</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) — answers in `solutions/day01_answers.md`
1. What do `print("2 + 3")` and `print(2 + 3)` display?
2. Name the error: `Print("Hi")`. Why does it happen?
3. Find the bug: `print("Hello)`
4. What does `print("A", "B", sep="-")` display?
5. What does `print("a\nb")` display?
6. What does `#` do in Python?
7. True or false: Python runs your file from the bottom to the top.
8. In a traceback, which line should you read first?

## 7. Wrap-up (5 min)
- Fill today's row in `tracker/PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1–5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: variables, data types and `input()` — we build a food-delivery bill splitter.
