# Day 18 — Modules, the Standard Library, `pip` & Virtual Environments

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Split code into files, use “batteries included” tools (datetime, collections, itertools…), install packages safely | Intermediate |

## 🌍 Real-world scenario & trend
**A birthday/deadline reminder + a quick analytics helper.** Real projects never reinvent date maths or counting — they import. Python's standard library (200+ modules) plus 500,000+ packages on PyPI is the reason Python wins. **Trend:** every professional project uses a **virtual environment** and a dependency file so “works on my machine” becomes “works everywhere”; modern teams use `uv` or `pip` + `venv`.

## 0. Warm-up (5 min) — Day 17 recap
- When does `finally` run?  • How do you raise a `ValueError`?

## 1. Concepts

### 1.1 Importing
```python
import math                      # math.sqrt(9)
from math import sqrt, pi        # sqrt(9)
import datetime as dt            # alias
from collections import Counter
```
Your own file is a module too: `shop_utils.py` → `import shop_utils` (same folder).

### 1.2 `if __name__ == "__main__":`
```python
def main(): ...
if __name__ == "__main__":   # True only when the file is RUN, not when it is imported
    main()
```
This is how a file can be both a reusable module and a runnable script. (See `shop_utils.py`.)

### 1.3 Tour of the standard library (the 12 you will use most)
| Module | Use | Example |
|---|---|---|
| `datetime` | dates & times | `date.fromisoformat("2026-11-16")`, `date.today()`, `timedelta(days=7)`, `.strftime("%d %b %Y")` |
| `random` | games, sampling | `random.choice(list)`, `random.shuffle`, `random.sample`, `random.seed(1)` |
| `collections` | smarter containers | `Counter`, `defaultdict(list)`, `deque`, `namedtuple` |
| `itertools` | combinatorics | `combinations`, `permutations`, `product`, `chain` |
| `statistics` | stats | `mean`, `median`, `stdev` |
| `math` | maths | `sqrt`, `ceil`, `floor`, `comb`, `isclose` |
| `pathlib` / `os` / `shutil` | files & system | `Path`, `os.environ["HOME"]`, `shutil.copy` |
| `json` / `csv` | data files | Day 13 / 16 |
| `time` | delays & timing | `time.sleep(1)`, `time.perf_counter()` |
| `sys` | interpreter | `sys.argv`, `sys.exit()` |
| `re` | text patterns | Day 23 |
| `uuid` / `secrets` | ids / secure random | `uuid.uuid4()`, `secrets.token_hex(8)` |

```python
from collections import Counter, defaultdict
Counter("banana").most_common(2)            # [('a', 3), ('n', 2)]
groups = defaultdict(list); groups["x"].append(1)   # no KeyError, auto-creates []
from itertools import combinations
list(combinations("ABC", 2))                # [('A','B'), ('A','C'), ('B','C')]
from datetime import date, timedelta
(date(2026, 12, 25) - date(2026, 11, 16)).days      # 39
date(2026, 11, 16) + timedelta(days=30)             # 2026-12-16
date(2026, 11, 16).weekday()                         # 0 = Monday ... 6 = Sunday
```

### 1.4 `pip` — install third-party packages
```powershell
python -m pip install requests          # install
python -m pip list                      # what is installed
python -m pip install "pandas>=2"       # version rule
```

### 1.5 Virtual environments — one clean “room” per project
```powershell
python -m venv .venv                    # create (once per project)
.venv\Scripts\Activate.ps1              # activate (prompt shows (.venv))
python -m pip install requests pandas   # installs INTO .venv only
python -m pip freeze > requirements.txt # save the exact versions
python -m pip install -r requirements.txt   # recreate on another machine
deactivate
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. In Cursor: **Ctrl+Shift+P → “Python: Select Interpreter” → pick `.venv`**. Never commit `.venv/` to git. *(Modern alternative: `uv` — `uv init`, `uv add requests`, `uv run main.py`.)*

### 1.6 Module hygiene
- Don't name your file like a module you import (`random.py`, `json.py` break imports!).
- Imports at the top; one per line; standard → third-party → yours.

## 2. Code along → `examples.py` (+ the helper module `shop_utils.py` next to it)
**Optional lab (15 min):** create a venv in this folder, install `requests`, run `python -c "import requests; print(requests.__version__)"`.

## 3. Common mistakes
- `ModuleNotFoundError`: package not installed in the *active* interpreter/venv.
- Naming your script `random.py`/`datetime.py` (shadows the real module).
- Forgetting `date.fromisoformat` needs `YYYY-MM-DD`.
- `random` results without `seed` change each run — use `random.seed(…)` for repeatable tests.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Days until an event, pretty date, median & mean |
| L2-1…L2-3 | 🟡 | Most common words (Counter), group by length (defaultdict), exact age in years |
| L3-1, L3-2 | 🔴 | All possible teams (itertools), “next Friday” date |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Read the standard-library docs page for the module (search “python datetime docs”); 90% of the answer is one function.</details>
<details><summary>Hint 2</summary>Days until: subtract two <code>date</code> objects, take <code>.days</code>. Age: <code>today.year - born.year</code>, minus 1 if the birthday hasn't happened yet: <code>(today.month, today.day) &lt; (born.month, born.day)</code>. Next weekday: <code>(target - d.weekday()) % 7 or 7</code> days ahead. Counter ties: <code>sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day18_solution.py</code></details>

## 6. Quiz — answers in `solutions/day18_answers.md`
1. What does `if __name__ == "__main__":` achieve?
2. Why use a virtual environment?
3. What does `pip freeze > requirements.txt` do?
4. `Counter("aabbbc").most_common(1)` → ?
5. What does `defaultdict(list)` solve?
6. `date(2026, 11, 16).weekday()` → ? (Monday = 0)
7. Why is naming your file `random.py` a bad idea?
8. Difference between `import math` and `from math import sqrt`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: Object-Oriented Programming — classes and objects.
