# Day 15 — Files & `pathlib`

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Read and write text files safely, build paths that work on any computer, analyse a real log file | Intermediate |

## 🌍 Real-world scenario & trend
**A server log analyser.** Every app writes logs (`2026-11-01 08:00:01 ERROR user=bob action=db_timeout`). On-call engineers and data teams parse these to find errors, busiest hours, failing users. Also: saving a to-do list, reading config, processing exports. **Trend:** `pathlib` is the modern way to handle paths (replacing string-glued `os.path`), and always specifying `encoding="utf-8"` avoids the classic Windows/emoji/₹ bugs.

## 0. Warm-up (5 min) — Day 14 recap
- How do you make a dict of totals per category?  • What does `date[:7]` give for `"2026-11-16"`?

## 1. Concepts

### 1.1 Open → use → close: always use `with`
```python
with open("notes.txt", "w", encoding="utf-8") as f:   # w = write (erases old content!)
    f.write("Line 1\n")                                # YOU add the \n
    f.write("Line 2\n")
# file is closed automatically here, even if an error happened
```
| Mode | Meaning |
|---|---|
| `"r"` | read (default) — error if the file is missing |
| `"w"` | write — **creates/overwrites** |
| `"a"` | append — adds to the end |
| `"x"` | create, error if it already exists |

### 1.2 Reading
```python
with open("notes.txt", encoding="utf-8") as f:
    everything = f.read()            # one big string
with open("notes.txt", encoding="utf-8") as f:
    lines = f.readlines()            # list, each ends with \n
with open("notes.txt", encoding="utf-8") as f:
    for line in f:                   # best for big files: one line at a time
        print(line.rstrip("\n"))
```

### 1.3 Always add `encoding="utf-8"`
Windows defaults to a legacy encoding; text with `₹`, `é` or emojis breaks. UTF-8 everywhere = safe.

### 1.4 `pathlib` — paths as objects
```python
from pathlib import Path
here = Path(__file__).resolve().parent         # the folder of THIS script (works from anywhere)
data = here / "output" / "todo.txt"            # '/' joins path parts
data.parent.mkdir(parents=True, exist_ok=True) # create folders
data.exists(), data.is_file(), data.name, data.stem, data.suffix   # 'todo.txt' 'todo' '.txt'
data.write_text("hello\n", encoding="utf-8")   # shortcuts for small files
data.read_text(encoding="utf-8")
for p in here.glob("*.py"):                    # find files by pattern
    print(p.name)
```

### 1.5 Missing files
Check first (`path.exists()`) or handle the error (`try/except FileNotFoundError` — tomorrow's topic is errors in depth).

### 1.6 Parsing a log line
```python
line = "2026-11-01 08:30:00 ERROR user=bob action=db_timeout"
date, time, level, *rest = line.split()
fields = dict(item.split("=") for item in rest)     # {'user': 'bob', 'action': 'db_timeout'}
```

## 2. Code along → `examples.py` (writes to an `output/` folder + reads `datasets/app.log`)

## 3. Common mistakes
- Opening with `"w"` when you meant `"a"` (you just erased the file).
- Forgetting `\n` when writing lines.
- Relative paths that depend on where you launch Python — build them from `Path(__file__)`.
- Reading a huge file with `.read()` instead of looping line by line.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Write lines, read lines, count lines |
| L2-1…L2-3 | 🟡 | Append a to-do, count log levels, find files by extension |
| L3-1, L3-2 | 🔴 | Write an error report file, find the busiest hour |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Say it in steps: open → loop over lines → clean each line → collect → return.</details>
<details><summary>Hint 2</summary>Level = <code>line.split()[2]</code>. Hour = <code>int(line.split()[1][:2])</code>. Report lines: <code>f"{time} {action} {user}"</code> using the <code>key=value</code> parsing from 1.6. Busiest hour with ties → earliest: <code>sorted(counts, key=lambda h: (-counts[h], h))[0]</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day15_solution.py</code></details>

## 6. Quiz — answers in `solutions/day15_answers.md`
1. Why use `with open(...)`?
2. What does mode `"w"` do to an existing file?
3. How do you add text to the end of a file?
4. What does `"\n"` do and why must you add it yourself when writing?
5. What does `Path(__file__).resolve().parent` give you?
6. `Path("a") / "b" / "c.txt"` → ?
7. `Path("report.final.csv").suffix` and `.stem`?
8. Why pass `encoding="utf-8"`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: CSV & JSON files — sales reports and settings.
