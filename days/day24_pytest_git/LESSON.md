# Day 24 — Testing with pytest & Git Basics

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Write automated tests that catch bugs; save and share your work with Git | Upper-intermediate |

## 🌍 Real-world scenario & trend
**A shop's discount code broke on Black Friday.** One wrong `<` instead of `<=` cost real money. Professional teams write tests so such bugs are caught in seconds, and keep history in Git so any change can be undone. **Trend:** every job posting asks for pytest + Git/GitHub; AI-generated code *must* be tested because it can be confidently wrong.

## 0. Warm-up (5 min) — Day 23 recap
- Write a regex for a 6-digit PIN.  • What does `Optional`/`X | None` mean?

## 1. Setup (3 min)
```powershell
python -m pip install pytest
python -m pytest --version
```

## 2. Concepts

### 2.1 `assert` — "this must be true"
```python
assert add(2, 3) == 5                  # silent if true
assert add(2, 3) == 6, "add is broken" # raises AssertionError if false
```

### 2.2 A pytest test is just a function named `test_...` in a file named `test_*.py`
```python
# shop.py
def apply_discount(price, percent):
    return round(price * (1 - percent / 100), 2)

# test_shop.py
from shop import apply_discount

def test_ten_percent():
    assert apply_discount(200, 10) == 180

def test_zero_percent_changes_nothing():
    assert apply_discount(99.5, 0) == 99.5
```
Run all tests: `python -m pytest -v` (verbose) · one file: `python -m pytest test_shop.py` · stop at first failure: `-x`.

### 2.3 Testing errors — `pytest.raises`
```python
import pytest
def test_negative_price_rejected():
    with pytest.raises(ValueError):
        apply_discount(-5, 10)
```

### 2.4 Many cases, one test — `parametrize`
```python
@pytest.mark.parametrize("price, pct, expected", [(100, 10, 90), (50, 50, 25), (80, 0, 80)])
def test_discount_table(price, pct, expected):
    assert apply_discount(price, pct) == expected
```

### 2.5 Fixtures — shared setup
```python
@pytest.fixture
def cart():
    return Cart()          # a fresh cart for every test that asks for `cart`

def test_new_cart_is_empty(cart):
    assert cart.total() == 0
```

### 2.6 What makes a good test?
Tiny, independent, readable name (`test_<what>_<expected>`), covers **normal**, **edge** (0, empty, boundary) and **error** cases. Think *Arrange → Act → Assert*.
**TDD loop:** write a failing test → write the minimum code → watch it pass → tidy.

### 2.7 Git in 10 commands
```powershell
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git init                         # start tracking this folder
git status                       # what changed?
git add .                        # stage everything
git commit -m "Add discount function"    # save a snapshot
git log --oneline                # history
git diff                         # what exactly changed (not yet staged)
git switch -c feature/coupons    # new branch to experiment safely
git switch main                  # go back;  git merge feature/coupons
```
Share it: create an empty repo on GitHub → `git remote add origin <url>` → `git push -u origin main`.
Add a `.gitignore` (`.venv/`, `__pycache__/`, `.env`, `*.pyc`) so junk and **secrets are never committed**.

## 3. Code along → `examples.py` + the mini project in this folder
- `shop.py` and `test_shop.py` are a real mini project. Run `python -m pytest -v` **in this folder**. Then break `shop.py` on purpose and see the test fail!
- `examples.py` shows how `assert` works and builds a tiny test runner so you understand what pytest does for you.

## 4. Common mistakes
- File not named `test_*.py` or function not named `test_*` → pytest silently ignores it.
- Tests that depend on each other or on the order they run.
- Asserting floats with `==` (`0.1+0.2`) — use `pytest.approx(0.3)`.
- One giant test with 20 asserts — you can't tell which part failed.
- Committing secrets/API keys; committing with the message "stuff".

## 5. Today's tasks → `practice.py`
Here **you write tests**, and the checker grades them by *mutation testing*: it runs your test against the correct code (must pass) and against secretly broken versions (must fail — otherwise your test isn't strong enough).
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Test `is_even`; write `clamp`; test `clamp` |
| L2-1…L2-3 | 🟡 | Test `slugify` with a case table; test an error with `pytest.raises`; test the `Account` class |
| L3-1, L3-2 | 🔴 | TDD: write `word_count` to satisfy tests; fix a buggy `median` |

## 6. Stuck? Hint ladder
<details><summary>Hint 1</summary>For tests, think: what are the normal inputs, the edges (0, boundaries) and the invalid inputs? Each category kills a different bug.</details>
<details><summary>Hint 2</summary>For <code>clamp</code> test a value below the range, inside, above, and exactly on both limits. For <code>slugify</code> test: upper-case, extra spaces, symbols. For errors use <code>with pytest.raises(ValueError):</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day24_solution.py</code></details>

## 7. Quiz — answers in `solutions/day24_answers.md`
1. How must test files and functions be named for pytest to find them?
2. What happens when an `assert` fails?
3. How do you test that a function raises `ValueError`?
4. What does `@pytest.mark.parametrize` save you from?
5. What is a fixture?
6. Why `pytest.approx` for floats?
7. Difference between `git add` and `git commit`?
8. Why have a `.gitignore`?

## 8. Wrap-up
Tracker + Bug Journal. Optional bonus (15 min): `git init` your `PY` folder and commit your progress — you'll never lose work again. Tomorrow: NumPy & pandas.
