# Day 03 — Numbers, Operators & the `math` Module

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Do any calculation in Python: discounts, GST, EMI, BMI; understand `/` vs `//` vs `%`, rounding and the float gotcha | Beginner |

## 🌍 Real-world scenario & trend
**E-commerce checkout + loan EMI calculator** (Amazon/Flipkart cart, bank apps, fintech like CRED/Groww). Every price, discount, tax and EMI you see is arithmetic on `int` and `float`. **Trend:** fintech and data work rely on correct number handling — real systems often use `decimal` for money because of the float gotcha below (we'll meet it today).

## 0. Warm-up (5 min) — Day 02 recap
- What type does `input()` return?  • Write an f-string that shows `3.14159` with 2 decimals.

## 1. Concepts

### 1.1 Arithmetic operators
| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+ - *` | add, subtract, multiply | `7 * 3` | `21` |
| `/` | true division (always `float`) | `7 / 2` | `3.5` |
| `//` | floor division (drop the decimals) | `7 // 2` | `3` |
| `%` | remainder (modulo) | `7 % 2` | `1` |
| `**` | power | `2 ** 3` | `8` |

### 1.2 Order of operations (like school maths: **PEMDAS**)
```python
2 + 3 * 4 ** 2     # 4**2=16 -> 3*16=48 -> 2+48 = 50
(2 + 3) * 4        # brackets first -> 20
```

### 1.3 Handy built-ins
```python
round(3.14159, 2)  # 3.14
abs(-250)          # 250
max(4, 9, 1)       # 9      min(4, 9, 1) -> 1
divmod(125, 60)    # (2, 5) -> 2 hours 5 minutes
```

### 1.4 Shortcuts: `+=  -=  *=  /=`
```python
cart_total = 500
cart_total += 250   # same as cart_total = cart_total + 250  -> 750
```

### 1.5 Comparison operators → give `True` / `False`
`==` equal, `!=` not equal, `<  >  <=  >=`.
```python
print(5 == 5.0, 5 != 6, 3 >= 4)   # True True False
```
(`=` stores a value, `==` asks “are they equal?”.)

### 1.6 The float gotcha
```python
print(0.1 + 0.2)            # 0.30000000000000004  (computers store binary fractions)
print(0.1 + 0.2 == 0.3)     # False!
print(round(0.1 + 0.2, 2) == 0.3)   # True
import math
print(math.isclose(0.1 + 0.2, 0.3)) # True
```
`round(2.5)` → `2` and `round(3.5)` → `4` (Python rounds .5 to the nearest *even* number).

### 1.7 The `math` module — your first import
```python
import math
math.sqrt(16)     # 4.0
math.ceil(4.2)    # 5   (round UP)   math.floor(4.8) -> 4 (round DOWN)
math.pi           # 3.14159...
```

### 1.8 Preview: “function boxes”
Today's tasks are written as `def name(inputs): return answer`. A function is a reusable calculator: give it inputs, it **returns** a result. (Full lesson on Day 11.)
```python
def add_gst(price):
    return price * 1.18
```

## 2. Code along → `examples.py` (checkout + EMI + BMI)

## 3. Common mistakes
- Using `^` for power (it's `**`).  • Integer-vs-float surprise: `7 / 2` is `3.5`, not `3`.
- `10 % 3` is the **remainder** (1), not a percentage.  • Percent maths: `price * percent / 100`.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Discount price, add GST, even/odd test |
| L2-1, L2-2 | 🟡 | Minutes → “2h 5m”; BMI calculator |
| L3-1 | 🔴 | Real bank EMI formula |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Write the calculation on paper with sample numbers first, then translate it into Python.</details>
<details><summary>Hint 2</summary>Discount: <code>price - price * percent / 100</code>. Even: <code>n % 2 == 0</code>. Time: <code>divmod(total_minutes, 60)</code>. BMI = weight ÷ (height in metres)². EMI: <code>r = annual_rate / 12 / 100</code>, <code>n = years * 12</code>, <code>EMI = P*r*(1+r)**n / ((1+r)**n - 1)</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day03_solution.py</code></details>

## 6. Quiz — answers in `solutions/day03_answers.md`
1. Evaluate `7 / 2`, `7 // 2`, `7 % 2`, `2 ** 3`.
2. Evaluate `2 + 3 * 4 ** 2`.
3. Is `0.1 + 0.2 == 0.3` true? Why? How do you compare floats safely?
4. What do `round(2.5)` and `round(3.5)` return?
5. What does `x += 5` mean?
6. How would you turn 125 minutes into hours and minutes in one line?
7. What is the type of `10 / 2`?
8. Output of `print(5 == 5.0, 5 != 5, 2 < 1)`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: strings — Instagram username & hashtag generator.
