# Day 02 — Variables, Data Types & `input()`

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Store data in variables, know the 4 basic types, take user input, format output with f-strings | Beginner |

## 🌍 Real-world scenario & trend
**Food-delivery bill splitter** (Swiggy / Zomato / Uber Eats style). An app stores `item_name`, `price`, `quantity`, `delivery_fee`… then calculates and displays your bill. Every app screen is built from variables + formatting. **Trend:** f-strings (Python 3.6+) replaced older `%` and `.format()` — you will see f-strings in nearly all modern code.

## 0. Warm-up (5 min) — Day 01 recap
- What does `print("a", "b", sep="-")` show?
- Which line of a traceback do you read first?

## 1. Concepts (with tiny code)

### 1.1 Variables — labels on values
```python
item_name = "Paneer Pizza"   # str   (text)
price = 349                  # int   (whole number)
rating = 4.5                 # float (decimal number)
is_veg = True                # bool  (True / False — capital T/F)
print(type(price))           # <class 'int'>
```
`=` means **“store the right side into the name on the left”** — it is not maths equality.

### 1.2 Naming rules
- Letters, digits, `_` only; cannot start with a digit; no spaces or `-`.
- Style: `snake_case` (`delivery_fee`), meaningful names (`price`, not `x`).
- Case-sensitive: `Price` ≠ `price`. Don't use keywords (`class`, `if`, `for`…).

### 1.3 Variables can change
```python
qty = 2
qty = qty + 1      # now 3
y = qty            # y gets a copy of the value 3
qty = 10
print(y)           # still 3
```

### 1.4 `input()` always gives text (`str`)
```python
age = input("Your age: ")     # user types 25
print(type(age))              # <class 'str'>   <- not a number!
age = int(age)                # convert: int() / float() / str()
print(age + 1)                # 26
```
`int("12.5")` fails (`ValueError`) — use `float("12.5")`.

### 1.5 f-strings — put variables inside text
```python
name, total = "Aarav", 1234.5
print(f"Hi {name}, your total is Rs. {total}")        # Hi Aarav, your total is Rs. 1234.5
print(f"Total: Rs. {total:.2f}")                       # Total: Rs. 1234.50   (2 decimals)
print(f"Population: {1234567:,}")                      # Population: 1,234,567
print(f"{'Item':<10}|{'Qty':>5}")                      # align: < left, > right
```

### 1.6 `None` — “no value yet”
`coupon = None` is how programs say “nothing here yet”.

## 2. Code along (30 min) → `examples.py`
Builds a delivery-bill splitter step by step. The last section uses `input()` — run it in the terminal and answer the prompts.

## 3. Common mistakes
- `"5" + 3` → `TypeError` (text + number). Convert first: `int("5") + 3`.
- `qty = input()` then `qty * 100` → **no error**, it repeats the text 100 times! Convert with `int()`.
- `True` vs `true` — only `True` works.
- Forgetting the `f` before the quote: `"Hi {name}"` prints `{name}` literally.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Create variables of the right type; calculate a total; convert text → number |
| L2-1, L2-2 | 🟡 | f-string order summary; split a bill between friends |
| L3-1 | 🔴 | Build a full multi-line invoice (subtotal, delivery, tip, total) |

## 5. Stuck? Hint ladder
<details><summary>Hint 1 — Direction</summary>
Check the type with <code>type(x)</code>. For output tasks, print your result and compare it with the expected text character by character.
</details>
<details><summary>Hint 2 — Shape of the answer</summary>
L2-1: <code>return f"{qty} x {item} = Rs. {price * qty:.2f}"</code> style. L2-2: divide first, then format with <code>:.2f</code>. L3-1: compute subtotal → tip = subtotal * tip_percent / 100 → total; join lines with <code>\n</code>.
</details>
<details><summary>Hint 3 — Peek</summary>
<code>solutions/day02_solution.py</code> — one task only, then rewrite from memory.
</details>

## 6. Quiz (10 min) — answers in `solutions/day02_answers.md`
1. What are the types of `5`, `5.0`, `"5"` and `True`?
2. `x = 10`, `y = x`, `x = 20`, `print(y)` → ?
3. Which names are valid: `2nd_item`, `item2`, `my-price`, `my_price`, `class`?
4. A user types `25` into `age = input()`. What is `type(age)`, and what does `age + 1` do?
5. Output of `print("5" + "3")` and of `print(5 + 3)`?
6. Output of `print(f"{349.5:.2f}")`?
7. `qty = input("Qty: ")` (user types 3) then `print(qty * 2)` → ?
8. What does `int("12.5")` do?

## 7. Wrap-up
Update the tracker row (hours, quiz score, confidence) + one entry in the Bug Journal. Tomorrow: numbers and operators — an EMI / discount calculator.
