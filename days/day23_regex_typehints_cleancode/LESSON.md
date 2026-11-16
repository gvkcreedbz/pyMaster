# Day 23 — Regular Expressions, Type Hints & Clean Code

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Extract/validate patterns from messy text, annotate code with types, and write code others (and linters) love | Upper-intermediate |

## 🌍 Real-world scenario & trend
**Cleaning a messy contact/invoice dump** (`datasets/contacts_messy.txt`): pull out emails, Indian mobile numbers, invoice IDs and amounts, mask card numbers before logging. **Trend:** regex is the Swiss-army knife for log parsing, data cleaning and validating LLM output; type hints + `ruff` + `mypy/pyright` are the 2026 standard for readable, safe code — AI assistants read your annotations too.

## 0. Warm-up (5 min) — Day 22 recap
- `yield` vs `return`?  • What does `@functools.wraps` do?

## 1. Concepts

### 1.1 Regex building blocks (always use raw strings `r"..."`)
| Pattern | Meaning |
|---|---|
| `.` | any character (except newline) |
| `\d` `\w` `\s` | digit / word char (letter, digit, `_`) / whitespace (`\D \W \S` = the opposite) |
| `[abc]` `[a-z0-9]` `[^0-9]` | one char from a set / range / not in set |
| `* + ?` | 0+ / 1+ / 0-or-1 of the previous |
| `{4}` `{2,5}` | exactly 4 / between 2 and 5 |
| `^` `$` `\b` | start / end / word boundary |
| `(...)` `(?:...)` `\|` | capture group / non-capturing / OR |
| `(?P<name>...)` | named group |

### 1.2 The `re` functions
```python
import re
text = "Order ORD1001 on 2026-11-03 for Rs. 899"
re.search(r"ORD\d+", text).group()                  # 'ORD1001'  (first match anywhere; None if absent)
re.findall(r"\d+", text)                            # ['1001', '2026', '11', '03', '899']
re.fullmatch(r"\d{6}", "560001")                    # match whole string (validation)
re.sub(r"\d", "#", "a1b22")                         # 'a#b##'    (replace)
re.split(r"[,;]\s*", "a, b;c")                      # ['a', 'b', 'c']
m = re.search(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})", text)
m["y"], m.groupdict()                               # '2026', {'y': '2026', 'm': '11', 'd': '03'}
for m in re.finditer(r"ORD(\d+)", text): ...        # iterate match objects
```
Flags: `re.IGNORECASE` / `(?i)`. `re.compile(pattern)` pre-builds a pattern for reuse.

### 1.3 Greedy vs lazy
`<.+>` on `"<b>x</b>"` grabs everything; `<.+?>` stops at the first `>`.

### 1.4 Regex advice
Start simple, test on real samples, use named groups, prefer `str` methods when they suffice, and **don't parse HTML with regex** (use BeautifulSoup, Day 27). Test regexes interactively at regex101.com (choose Python flavour).

### 1.5 Type hints — documentation that tools can check
```python
def average(values: list[float]) -> float: ...
def find_user(user_id: int) -> dict[str, str] | None: ...      # "or None" (Python 3.10+)
def apply(func: Callable[[int], int], x: int) -> int: ...      # from collections.abc import Callable
prices: dict[str, float] = {}
```
Hints are **not enforced at runtime** — a checker (`mypy`, `pyright`, Cursor/VS Code Pylance) reads them. They make autocomplete and AI assistance far better. Common types: `int str float bool list[T] dict[K, V] tuple[int, ...] set[T] T | None`.

### 1.6 Clean code checklist (PEP 8 + habits)
- `snake_case` functions/variables, `PascalCase` classes, `UPPER_CASE` constants; max ~88–100 chars per line; 4 spaces.
- Meaningful names (`total_price`, not `tp`); small functions (one job); docstrings for public functions.
- No magic numbers (`TAX_RATE = 0.18`); no dead code; no deep nesting (use early `return`).
- Prefer f-strings, `pathlib`, `with`, comprehensions, `enumerate`, `zip`.
- Tools: `python -m pip install ruff` → `ruff check .` (lint), `ruff format .` (auto-format). In Cursor, install the *Ruff* extension to see issues as you type.

## 2. Code along → `examples.py` (runs regexes on `datasets/contacts_messy.txt`)

## 3. Common mistakes
- Forgetting the raw string (`"\d"` warns/behaves oddly) — use `r"\d"`.
- `re.match` only matches at the **start**; use `search` for “anywhere”, `fullmatch` for validation.
- Greedy `.*` swallowing too much.
- Writing monster patterns nobody can read — break into steps or add `re.VERBOSE` comments.
- Believing type hints change behaviour (they don't).

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Find emails, find mobile numbers, validate a PIN code |
| L2-1…L2-3 | 🟡 | Extract invoices (named groups), mask card numbers, normalise order IDs |
| L3-1, L3-2 | 🔴 | Parse a log line into a dict; write a fully **type-annotated** `group_average` |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Open <code>datasets/contacts_messy.txt</code> and look at what you want — and what you do NOT want to match (invalid emails, toll-free numbers).</details>
<details><summary>Hint 2</summary>Email: <code>[\w.+-]+@[\w-]+(?:\.[\w-]+)+</code>. Indian mobile: starts with 6–9, 10 digits, optional <code>+91</code>, optional space/dash after 5 digits — use two groups and join them. PIN: <code>[1-9]\d{5}</code> with <code>fullmatch</code>. Card: <code>\b(?:\d{4}[ -]?){3}(\d{4})\b</code> → <code>"**** **** **** \1"</code>. Log line: anchored pattern with <code>(?P&lt;date&gt;...)</code> etc., return <code>m.groupdict()</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day23_solution.py</code></details>

## 6. Quiz — answers in `solutions/day23_answers.md`
1. Why use raw strings (`r"..."`) for regex?
2. Difference between `re.match`, `re.search` and `re.fullmatch`?
3. What does `\d{3}-\d{4}` match?
4. Greedy vs lazy: what does `.+?` do?
5. How do you get named groups as a dict?
6. Do type hints stop `average("hello")` from running?
7. Name three PEP 8 naming rules.
8. What do `ruff check` and `ruff format` do?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: testing with `pytest` and Git/GitHub basics.
