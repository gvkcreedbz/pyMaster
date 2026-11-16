# Day 17 — Errors, Exceptions, Debugging & Logging

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Make programs survive bad input and failures; debug methodically; leave a trail with `logging` | Intermediate |

## 🌍 Real-world scenario & trend
**A payment service.** Customers type letters instead of amounts, the bank API times out, a file is missing. A professional program never just crashes: it validates, retries, reports a clear reason, and **logs** what happened so engineers can investigate at 3 a.m. **Trend:** observability (logs, metrics, traces) is a core skill; `print` debugging is replaced by structured logging in production.

## 0. Warm-up (5 min) — Day 16 recap
- Which module writes dicts to CSV?  • `json.load` or `json.loads` for a file?

## 1. Concepts

### 1.1 `try / except / else / finally`
```python
try:
    amount = int(input("Amount: "))          # risky code
except ValueError:                           # run ONLY if a ValueError happened
    print("Please type digits only")
else:                                        # run only if NO error happened
    print("OK:", amount)
finally:                                     # ALWAYS runs (cleanup)
    print("Done")
```
Catch **specific** exceptions (`ValueError`, `ZeroDivisionError`, `FileNotFoundError`, `KeyError`, `TypeError`). Avoid bare `except:` — it hides real bugs.
```python
except (ValueError, TypeError):    # several types
except Exception as e:              # last resort; e holds the message
    print("Failed:", e)
```

### 1.2 Raising your own errors
```python
def set_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age
```

### 1.3 Custom exceptions
```python
class InsufficientFundsError(Exception):
    """Raised when a withdrawal is bigger than the balance."""
raise InsufficientFundsError("Need Rs. 500 more")
```
(`class` is Day 19 — for now just copy the pattern: it gives your errors a meaningful name.)

### 1.4 EAFP vs LBYL
- LBYL “look before you leap”: `if key in d: ...`
- EAFP “easier to ask forgiveness”: `try: d[key] ... except KeyError`. Python style prefers EAFP when failures are rare.

### 1.5 Reading a traceback (bottom-up)
```text
Traceback (most recent call last):
  File "app.py", line 12, in <module>      <- where it started
    total = average([])
  File "app.py", line 5, in average        <- where it blew up (look here)
    return sum(nums) / len(nums)
ZeroDivisionError: division by zero         <- WHAT happened (read first!)
```

### 1.6 Debugging toolbox
1. **Reproduce** with the smallest input. 2. **Read** the last line + line number. 3. **Print/inspect** values (`print(f"{x=}")` shows name and value). 4. **Debugger**: click left of a line number in Cursor to set a breakpoint, press F5, step with F10/F11 — or type `breakpoint()` in code (use `n`, `p var`, `c`, `q`). 5. **Bisect**: comment out half the code. 6. **Rubber-duck**: explain it aloud.

### 1.7 `assert` — sanity checks while developing
`assert total >= 0, "total can't be negative"` raises `AssertionError` if false.

### 1.8 `logging` instead of `print`
```python
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    filename="app.log", encoding="utf-8")
logging.debug("details for developers")      # hidden at INFO level
logging.info("order placed")                  # normal events
logging.warning("disk almost full")           # something odd
logging.error("payment failed")               # a failure
logging.exception("crashed")                  # inside except: error + traceback
```
Levels: DEBUG < INFO < WARNING < ERROR < CRITICAL.

## 2. Code along → `examples.py`

## 3. Common mistakes
- Bare `except:` / `except Exception: pass` — silently swallowing errors.
- Huge `try` blocks (wrap only the risky line).
- Catching an error and then using a variable that was never set.
- Using `print` for production diagnostics (no time, no level, easy to lose).

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | `safe_int`, `safe_divide`, read first line of a maybe-missing file |
| L2-1…L2-3 | 🟡 | Validate age (raise), withdraw with custom error, `retry` helper |
| L3-1, L3-2 | 🔴 | Process a batch of payments with reasons, build a file logger |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>List what could go wrong on each line, then decide: fix by validation or handle with <code>except</code>.</details>
<details><summary>Hint 2</summary>retry: loop <code>attempts</code> times, <code>try: return func()</code>, remember the last exception, and <code>raise</code> it after the loop. process_payments: <code>float(p["amount"])</code> can raise <code>KeyError</code>, <code>ValueError</code> or <code>TypeError</code> — handle each with its own message. Logger: <code>logging.getLogger(name)</code>, <code>FileHandler(path, encoding="utf-8")</code>, <code>Formatter("%(levelname)s - %(message)s")</code>, <code>setLevel(logging.INFO)</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day17_solution.py</code></details>

## 6. Quiz — answers in `solutions/day17_answers.md`
1. When does the `else` block of a `try` run? When does `finally` run?
2. Why is a bare `except:` risky?
3. `int("abc")`, `1/0`, `{"a":1}["b"]`, `open("nope.txt")` raise which errors?
4. Which line of a traceback do you read first?
5. How do you raise an error with your own message?
6. What does `print(f"{total=}")` show?
7. Which log level is hidden when the level is `INFO`?
8. Difference between `logging.error(...)` and `logging.exception(...)`?

## 7. Wrap-up
Tracker + Bug Journal (this day's journal entry should be your most interesting error!). Tomorrow: modules, the standard library, `pip` and virtual environments.
