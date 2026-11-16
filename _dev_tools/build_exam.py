"""Maintainer tool: builds the Day 30 final exam and its answer key by RUNNING every snippet,
so the published answers can never be wrong.

Usage (from the project root):  python _dev_tools/build_exam.py
Writes: days/day30_fastapi_final_exam/FINAL_EXAM.md and solutions/day30_exam_answers.md
"""
import contextlib
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (day tag, topic, code, explanation)
QUESTIONS = [
    (3, "numbers & strings",
     'print(7 // 2, 7 % 2, 7 / 2, 2 ** 3, "ab" * 2)',
     "`//` floors, `%` is the remainder, `/` always gives a float, `**` is power, and `*` repeats a string."),
    (4, "string slicing",
     's = "Python Rocks"\nprint(s[::-1][:4], s.lower().count("o"), s.split()[1][0])',
     "`s[::-1]` reverses the text (`skcoR nohtyP`) and `[:4]` keeps 4 characters; the lower-cased text has two `o`; `split()[1]` is `Rocks` and `[0]` its first letter."),
    (5, "truthiness",
     'print(bool(""), bool("0"), bool([]), bool([0]), None == False)',
     "Empty containers/strings are falsy; the *text* `\"0\"` and the list `[0]` are not empty, so truthy. `None == False` is `False` (use `is None` to test for None)."),
    (6, "range & loops",
     'for i in range(10, 0, -3):\n    print(i, end=" ")',
     "`range(10, 0, -3)` counts down by 3 and stops before 0: 10, 7, 4, 1."),
    (6, "loop with else",
     'for n in [4, 8, 9]:\n    if n % 2 == 1:\n        print("odd found:", n)\n        break\nelse:\n    print("all even")',
     "`else` on a loop runs only if the loop finished without `break`. Here 9 triggers `break`, so `else` is skipped."),
    (8, "list aliasing",
     'a = [1, 2, 3]\nb = a\nc = a[:]\nb.append(4)\nprint(a, c)',
     "`b = a` makes both names point to the *same* list; `a[:]` makes a copy. Appending through `b` changes `a` but not `c`."),
    (8, "list methods",
     'nums = [5, 3, 8, 1]\nprint(sorted(nums)[-2:], nums.pop(1), nums)',
     "`sorted()` returns a new list `[1, 3, 5, 8]` -> last two `[5, 8]`; `pop(1)` removes and returns `3`; the original now holds `[5, 8, 1]`."),
    (10, "dictionary counting",
     'd = {}\nfor w in "a b a c b a".split():\n    d[w] = d.get(w, 0) + 1\nprint(d, max(d, key=d.get))',
     "`get(w, 0)` supplies 0 for new keys, so we count words. `max(d, key=d.get)` returns the key with the largest value."),
    (9, "sets",
     'print({1, 2, 3} & {2, 3, 4}, {1, 2} | {2, 5}, len({1, 1, 2}))',
     "`&` is intersection, `|` is union, and sets drop duplicates (`{1, 1, 2}` has 2 items)."),
    (11, "mutable default argument",
     'def add(x, bucket=[]):\n    bucket.append(x)\n    return bucket\n\nprint(add(1), add(2))',
     "The default list is created **once** when the function is defined and shared by every call, so both calls return the same list (a classic trap — use `bucket=None`)."),
    (11, "*args and **kwargs",
     'def f(a, *args, **kw):\n    return a, args, kw\n\nprint(f(1, 2, 3, k=4))',
     "`*args` collects extra positional arguments into a tuple and `**kw` collects keyword arguments into a dict."),
    (12, "comprehensions",
     'print([x * x for x in range(6) if x % 2 == 0], {w: len(w) for w in ["hi", "python"]}, sum(x for x in range(4)))',
     "List comprehension with a filter keeps even numbers' squares; dict comprehension maps word -> length; the generator sums 0+1+2+3."),
    (12, "sorting with lambda",
     'people = [("Ann", 30), ("Bob", 25), ("Cy", 30)]\nprint(sorted(people, key=lambda p: (-p[1], p[0])))',
     "The key `(-age, name)` sorts by age descending, then by name A-Z for ties (Ann before Cy)."),
    (17, "try / finally",
     'def f():\n    try:\n        return "try"\n    finally:\n        print("cleanup")\n\nprint(f())',
     "`finally` always runs before the function really returns, so `cleanup` prints first, then the returned value is printed."),
    (17, "exception flow",
     'try:\n    int("x")\nexcept ZeroDivisionError:\n    print("zero")\nexcept ValueError:\n    print("value")\nelse:\n    print("else")\nfinally:\n    print("done")',
     "`int(\"x\")` raises `ValueError`; the matching `except` runs, `else` is skipped (it only runs if nothing was raised) and `finally` always runs."),
    (19, "classes & inheritance",
     'class Animal:\n    sound = "..."\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        return f"{self.name} says {self.sound}"\n\nclass Dog(Animal):\n    sound = "Woof"\n\nprint(Dog("Rex").speak(), "|", Animal("Tom").speak())',
     "`Dog` inherits `speak` and `__init__` but overrides the class attribute `sound`; `self.sound` finds the most specific version."),
    (22, "generators",
     'def gen():\n    for i in range(3):\n        yield i * i\n\ng = gen()\nprint(next(g), next(g), list(g), list(g))',
     "A generator is consumed as you iterate: two `next` calls give 0 and 1, `list(g)` collects the rest (`[4]`), and a second `list(g)` is empty because it is exhausted."),
    (22, "decorators",
     'def twice(f):\n    def wrapper(*a):\n        return f(*a) * 2\n    return wrapper\n\n@twice\ndef add(a, b):\n    return a + b\n\nprint(add(2, 3))',
     "`@twice` replaces `add` with `wrapper`, which doubles the original result: (2+3)*2."),
    (23, "regex",
     'import re\nprint(re.findall(r"\\d+", "a1b22c333"), re.sub(r"\\s+", " ", "a   b \\n c"))',
     "`\\d+` finds runs of digits; `\\s+` matches any whitespace run (spaces and newline) which is replaced by one space."),
    (26, "pandas groupby",
     'import pandas as pd\ndf = pd.DataFrame({"city": ["A", "B", "A", "B", "A"], "sales": [10, 20, 30, 40, 50]})\nprint(df.groupby("city")["sales"].sum().to_dict(), df[df.sales > 20].shape)',
     "City A: 10+30+50 = 90, B: 20+40 = 60. Three rows have sales > 20 and the table has 2 columns, so the shape is (3, 2)."),
    (28, "SQL",
     'import sqlite3\nc = sqlite3.connect(":memory:")\nc.execute("create table t(x int)")\nc.executemany("insert into t values(?)", [(1,), (2,), (3,)])\nprint(c.execute("select sum(x), count(*) from t where x > 1").fetchone())',
     "`WHERE x > 1` keeps 2 and 3 -> sum 5, count 2. `fetchone()` returns a tuple."),
    (3, "types & conversion",
     'print(type(3 / 1).__name__, type(3 // 1).__name__, "3" + "4", int("3") + int("4"))',
     "`/` always produces a float (even `3 / 1`), `//` of ints stays an int; `+` on two strings concatenates, on ints adds."),
    (8, "zip & enumerate",
     'names = ["a", "b"]\nages = [1, 2]\nprint(list(zip(names, ages)), dict(enumerate(names, 1)))',
     "`zip` pairs items position by position; `enumerate(names, 1)` numbers them starting at 1."),
    (4, "f-string formats",
     'price = 1234.5\nprint(f"{price:,.2f} | {price:>10.1f} | {0.256:.1%}")',
     "`:,.2f` adds thousands separators and 2 decimals; `>10.1f` right-aligns in 10 characters; `.1%` multiplies by 100 and adds `%`."),
    (6, "BUG: typo operator",
     'total = 0\nfor p in [10, 20, 30]:\n    total =+ p\nprint(total)',
     "`=+` is *assignment of a positive number*, not `+=`. Each pass replaces `total`, so the result is just the last item. Fix: `total += p` (expected 60)."),
    (10, "BUG: missing key",
     'scores = {"alice": 90}\nprint(scores["bob"])',
     "Reading a missing key raises `KeyError`. Fix: `scores.get(\"bob\", 0)` or check `\"bob\" in scores` first."),
    (8, "BUG: changing a list while looping",
     'nums = [1, 2, 2, 3]\nfor n in nums:\n    if n == 2:\n        nums.remove(n)\nprint(nums)',
     "Removing items shifts the positions while the `for` loop is still walking, so one `2` gets skipped. Fix: iterate over a copy (`for n in nums[:]`) or build a new list with a comprehension."),
]


def run(code):
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, {"__name__": "__exam__"})
    except Exception as error:  # a snippet that is MEANT to fail
        return buffer.getvalue() + f"<raises {type(error).__name__}>\n"
    return buffer.getvalue()


def main():
    exam = ["# 🎓 Day 30 — FINAL EXAM (45 minutes, closed-book)\n",
            "**Rules:** do NOT run the code, do NOT use AI or notes. Read each snippet carefully and write down exactly what it prints "
            "(or the error it raises). 1 point each → **27 points**. Questions are in a deliberate mix of topics; the *Day* tag tells you "
            "which lesson to revisit if you miss it.\n",
            "> Tip: trace variables on paper. Exact output counts — spaces, brackets and quotes matter.\n",
            "After finishing, check `solutions/day30_exam_answers.md`, write your score in the tracker and note your weak topics.\n", "---\n"]
    answers = ["# Day 30 — Final Exam answer key\n",
               "Every output below was produced by actually running the code (via `_dev_tools/build_exam.py`).\n",
               "Scoring (out of 27): 24–27 🏆 · 19–23 ✅ · 13–18 🟡 · <13 🔁 (see LESSON.md).\n", "---\n"]
    for number, (day, topic, code, why) in enumerate(QUESTIONS, 1):
        exam.append(f"### Q{number}. (Day {day}) — {topic}\n```python\n{code}\n```\n**Your answer:** ______________________\n")
        output = run(code).rstrip("\n")
        answers.append(f"### Q{number}. (Day {day}) — {topic}\n```text\n{output}\n```\n{why}\n")
    (ROOT / "days" / "day30_fastapi_final_exam" / "FINAL_EXAM.md").write_text("\n".join(exam), encoding="utf-8")
    (ROOT / "solutions" / "day30_exam_answers.md").write_text("\n".join(answers), encoding="utf-8")
    print(f"Wrote exam with {len(QUESTIONS)} questions and answer key.")


if __name__ == "__main__":
    main()
