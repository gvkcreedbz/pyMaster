# Day 06 — Loops: `for`, `while`, `break`, `continue`

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Repeat work automatically: tables, totals, retries, games, patterns | Beginner |

## 🌍 Real-world scenario & trend
**Number-guessing game + PIN retry + processing 1,000 orders.** Anything repeated — checking every row of a sales file, retrying a failed payment, a game loop that waits for the player — is a loop. **Trend:** data & automation work is “loop over lots of items”; later you'll replace many loops with pandas/comprehensions, but you must understand loops first.

## 0. Warm-up (5 min) — Day 05 recap
- What does `elif` do?  • Is `""` truthy or falsy?

## 1. Concepts

### 1.1 `for` loop with `range()`
```python
for i in range(5):            # 0,1,2,3,4   (stop is excluded)
    print(i)
range(1, 6)        # 1..5
range(0, 10, 2)    # 0,2,4,6,8   (step)
range(5, 0, -1)    # 5,4,3,2,1   (countdown)
```

### 1.2 Loop over text (and later lists)
```python
for ch in "Python":
    print(ch)
for word in "red green blue".split():
    print(word.upper())
```

### 1.3 The accumulator pattern (totals, counters)
A group of items in round brackets, like `(499, 1299, 250)`, is a **tuple** — a fixed collection (lists and tuples get their own lessons on Day 8–9). A `for` loop can walk through any collection.
```python
total = 0                     # start value
for price in (499, 1299, 250):
    total += price            # update inside the loop
print(total)                  # 2048
```

### 1.4 `while` — repeat until a condition becomes False
```python
attempts = 0
while attempts < 3:
    print("Try", attempts + 1)
    attempts += 1             # forget this -> infinite loop (Ctrl+C stops it)
```

### 1.5 `break` and `continue`
```python
for n in range(1, 10):
    if n == 3:
        continue              # skip this round
    if n == 6:
        break                 # leave the loop completely
    print(n)                  # 1 2 4 5
```
`while True:` + `break` is the standard “keep asking until valid” pattern.

### 1.6 `for ... else` (bonus)
The `else` block runs if the loop finished **without** `break`: handy for “not found” (e.g. PIN checking).

### 1.7 Nested loops
```python
for row in range(1, 4):
    for col in range(1, 4):
        print(row * col, end=" ")
    print()                    # new line after each row
```

### 1.8 `random` (standard library) for games
```python
import random
secret = random.randint(1, 20)   # 1..20 inclusive
```

## 2. Code along → `examples.py` (guessing game, table, patterns)

## 3. Common mistakes
- Infinite `while` loop — always change something that makes the condition False.
- Off-by-one: `range(5)` stops at 4; `range(1, 6)` gives 1–5.
- Modifying the accumulator *outside* the loop (wrong indentation).
- Resetting `total = 0` **inside** the loop.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Sum 1..n, count vowels, multiplication table |
| L2-1…L2-3 | 🟡 | Factorial, FizzBuzz, prime check |
| L3-1, L3-2 | 🔴 | PIN with 3 attempts, star pyramid |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Say the loop in words: “Start with ___. For each ___, do ___. At the end return ___.”</details>
<details><summary>Hint 2</summary>Factorial: start <code>result = 1</code>, multiply by each number 1..n. FizzBuzz: check “divisible by 15” first. Prime: n &lt; 2 is not prime; try divisors from 2 to n−1 (or up to √n) and return False on the first hit. PIN: <code>guesses_text.split(",")</code> gives the guesses; count attempts; stop after 3. Pyramid row i: <code>" " * (n - i) + "*" * (2*i - 1)</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day06_solution.py</code></details>

## 6. Quiz — answers in `solutions/day06_answers.md`
1. What numbers does `range(2, 10, 3)` produce?
2. What is printed? `for i in range(3): print(i)`
3. How many times does `while 5 < 3:` run its body?
4. What is the difference between `break` and `continue`?
5. After `total = 0; for n in (1,2,3): total += n` what is `total`?
6. How do you stop an infinite loop in the terminal?
7. Write a loop that prints 5 down to 1.
8. What is wrong with: `while count < 3: print(count)` (count starts at 0)?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: **Week-1 project** — a mini ATM + guessing game, plus a review test.
