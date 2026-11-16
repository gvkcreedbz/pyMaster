# 🔍 Error Decoder — what Python is telling you

**Golden rule:** read the **last line** of the error first (type + message). Then look at the **line number** just above it. Then look at the *line before* that one if the error line looks fine (a missing bracket/quote often reports the *next* line).

```
Traceback (most recent call last):
  File "practice.py", line 12, in <module>      ← where it happened (read bottom-up)
    total = price * qty
TypeError: can't multiply sequence by non-int of type 'str'   ← WHAT happened (read first!)
```

| Error | Usually means | Typical cause → fix |
|---|---|---|
| `SyntaxError: unterminated string literal` | A quote isn't closed | `print("Hi)` → add the closing `"` |
| `SyntaxError: invalid syntax` | Python can't parse the line | missing `:` after `if/for/def`, missing `)`, `=` instead of `==` in a condition — also check the *previous* line |
| `SyntaxError: '(' was never closed` | Unbalanced brackets | count `( [ {` against `) ] }` |
| `IndentationError: expected an indented block` | Nothing under `if/for/def/class` | indent the body by 4 spaces (or add `pass`) |
| `IndentationError: unindent does not match` | Mixed tabs/spaces | use 4 spaces everywhere (editor: "Convert Indentation to Spaces") |
| `NameError: name 'x' is not defined` | Python never saw `x` | typo, wrong case (`Print`), used before assignment, forgot quotes around text, forgot `import` |
| `UnboundLocalError: ... referenced before assignment` | Assigned inside a function, used before that | pass it in as a parameter / return it; avoid changing globals |
| `TypeError: can only concatenate str (not "int") to str` | `"a" + 5` | `str(5)` or an f-string |
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | Mixed types in arithmetic | convert: `int(text)` (remember `input()` returns text!) |
| `TypeError: 'int' object is not iterable` | `for x in 5` | use `range(5)` |
| `TypeError: 'NoneType' object is not subscriptable` / `... has no attribute` | A function returned `None` | forgot `return`; `my_list = my_list.sort()` (sort returns None) |
| `TypeError: f() takes 2 positional arguments but 3 were given` | Wrong number of arguments | compare the call with `def f(...)`; methods get `self` automatically |
| `ValueError: invalid literal for int() with base 10: 'abc'` | Text isn't a number | validate input with `try/except` or `.isdigit()` |
| `ValueError: not enough values to unpack` | Unpacking `a, b = [1]` | counts must match |
| `IndexError: list index out of range` | Position doesn't exist | indexes go `0 … len-1`; check `len(x)` |
| `KeyError: 'name'` | Missing dict key | `d.get("name")`, `"name" in d`, check spelling/case |
| `AttributeError: 'str' object has no attribute 'append'` | Method doesn't exist for that type | check the type with `print(type(x))`; typo in method name |
| `AttributeError: module 'x' has no attribute 'y'` | Wrong name — or **your file is named like the module** | don't name files `random.py`, `math.py`, `csv.py`, `requests.py` |
| `ModuleNotFoundError: No module named 'x'` | Not installed / wrong Python | `python -m pip install x`; check the interpreter & active venv |
| `ImportError: cannot import name 'f' from 'm'` | Name isn't in that module | typo, or circular import |
| `ZeroDivisionError: division by zero` | `/ 0` or `% 0` | check the divisor before dividing |
| `FileNotFoundError: [Errno 2] No such file or directory` | Wrong path / working directory | print `Path.cwd()`; use a path relative to the file (`Path(__file__).parent`) |
| `PermissionError` | File open in Excel / protected folder | close the file; choose another folder |
| `UnicodeDecodeError / UnicodeEncodeError` | Wrong encoding | `open(path, encoding="utf-8")` |
| `RecursionError: maximum recursion depth exceeded` | A function calls itself forever | add/repair the stopping condition (base case) |
| `StopIteration` | Called `next()` on an exhausted iterator/generator | create a new generator, or use `for` |
| `AssertionError` | An `assert` / test failed (on purpose) | compare expected vs actual; fix code or the test |
| `RuntimeError: dictionary changed size during iteration` | Edited a dict/list while looping over it | loop over a copy: `for k in list(d):` |
| `requests.exceptions.ConnectionError / Timeout` | Network problem | check internet/URL; use `timeout=` and retries (Day 27) |
| `sqlite3.OperationalError: no such table` | Table not created / wrong file | check the DB path and `CREATE TABLE` ran |
| `sqlite3.ProgrammingError: Incorrect number of bindings` | `?` count ≠ values | one `?` per value; pass a **tuple** (even for one value: `(x,)`) |
| `KeyboardInterrupt` | You pressed Ctrl+C | normal — it stops the program |

## Not an error, but a bug (no message!)
| Symptom | Likely cause |
|---|---|
| Output is *almost* right | off-by-one (`range(1, n)` vs `range(1, n + 1)`), wrong comparison (`<` vs `<=`) |
| A list/dict "changed by itself" | aliasing: `b = a` shares the object — use `a.copy()` / `a[:]` / `copy.deepcopy` |
| Function returns `None` | missing `return` (printing ≠ returning) |
| `if x = 5` / always True | `=` assigns, `==` compares; `if x == 5 or 6` is always true — write `x in (5, 6)` |
| Loop never ends | the loop variable never changes inside `while` |
| Results differ every run | randomness (`random.seed(1)` for repeatability), set ordering, dictionary of changing data |
| Float surprises (`0.1 + 0.2`) | binary floats — use `round()`, `math.isclose`, or `Decimal` for money |
| Works alone, fails in a function | variable scope — pass values as parameters |

## Debugging toolbox (in order)
1. **Read** the message. 2. **Print** the values and types near the failing line (`print(repr(x), type(x))`). 3. **Shrink** the problem to the smallest failing example. 4. **Explain it aloud** (rubber-duck). 5. **Search** the exact message. 6. **Ask** with: your code, the full error, what you expected, what you tried. See `how_to_get_unstuck.md`.
