"""Day 11 - Practice: functions.

Run:  python practice.py
"""


# ---------------------------------------------------------------------------
# L1-1 | Greeting with a default   (Level 1 - Beginner)
# greet("Aarav") -> "Hello, Aarav!"      greet("Diya", "Namaste") -> "Namaste, Diya!"
# The greeting word must be an optional parameter that defaults to "Hello".
# ---------------------------------------------------------------------------
def greet(name, greeting="Hello"):
    """Return '<greeting>, <name>!'."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | Total with tax   (Level 1 - Beginner)
# price * qty * (1 + tax_percent / 100), rounded to 2 decimals.
# qty defaults to 1 and tax_percent defaults to 18.
#   calc_total(100) -> 118.0     calc_total(100, qty=3, tax_percent=5) -> 315.0
# ---------------------------------------------------------------------------
def calc_total(price, qty=1, tax_percent=18):
    """Return the total price including tax."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | Average of anything   (Level 1 - Beginner)
# Accept any number of numbers with *args. average(4, 8, 6) -> 6.0
# With no numbers at all return 0.
# ---------------------------------------------------------------------------
def average(*numbers):
    """Return the mean of the given numbers (0 if none)."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | Profile line   (Level 2 - Intermediate)
# Accept any keyword arguments (**fields). Return "key=value" pairs joined by
# "; ", with the keys in alphabetical order.
#   format_profile(name="Aarav", age=25) -> "age=25; name=Aarav"       format_profile() -> ""
# ---------------------------------------------------------------------------
def format_profile(**fields):
    """Return the fields as one tidy line."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | Several return values   (Level 2 - Intermediate)
# Return (smallest, largest, average rounded to 2 decimals) as a tuple.
#   min_max_avg([4, 8, 6]) -> (4, 8, 6.0)      min_max_avg([1, 2]) -> (1, 2, 1.5)
# ---------------------------------------------------------------------------
def min_max_avg(numbers):
    """Return (min, max, rounded average)."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | Fibonacci (recursion)   (Level 2 - Intermediate)
# fib(0)=0, fib(1)=1, fib(n)=fib(n-1)+fib(n-2).  fib(7) -> 13.
# Use recursion (the function calls itself). n is at most 20.
# ---------------------------------------------------------------------------
def fib(n):
    """Return the n-th Fibonacci number."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | Flatten nested lists   (Level 3 - Challenge)
# Turn any depth of nested lists into one flat list, keeping the order.
#   flatten([1, [2, [3, 4]], 5]) -> [1, 2, 3, 4, 5]       flatten([]) -> []
# Hint: isinstance(x, list) tells you whether x is a list.
# ---------------------------------------------------------------------------
def flatten(nested):
    """Return a flat list."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | Safe default   (Level 3 - Challenge)
# safe_append(item, items=None): add item to items and return it. When items is
# not given, start from a FRESH empty list EVERY call (avoid the mutable-default trap).
#   safe_append(1) -> [1]     safe_append(2) -> [2]     safe_append(3, [1, 2]) -> [1, 2, 3]
# ---------------------------------------------------------------------------
def safe_append(item, items=None):
    """Append item to items (or to a new list)."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ======================= AUTO-CHECKER (do not edit below) ====================
_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


print("--- Day 11 checks ---")
check("L1-1 greet", lambda: (greet("Aarav"), greet("Diya", "Namaste")), ("Hello, Aarav!", "Namaste, Diya!"))
check("L1-2 calc_total", lambda: (calc_total(100), calc_total(100, qty=3, tax_percent=5), calc_total(50, 2)), (118.0, 315.0, 118.0))
check("L1-3 average", lambda: (average(4, 8, 6), average(), average(5)), (6.0, 0, 5.0))
check("L2-1 format_profile", lambda: (format_profile(name="Aarav", age=25), format_profile()), ("age=25; name=Aarav", ""))
check("L2-2 min_max_avg", lambda: (min_max_avg([4, 8, 6]), min_max_avg([1, 2])), ((4, 8, 6.0), (1, 2, 1.5)))
check("L2-3 fib", lambda: [fib(n) for n in (0, 1, 2, 7, 15)], [0, 1, 1, 13, 610])
check("L3-1 flatten", lambda: (flatten([1, [2, [3, 4]], 5]), flatten([]), flatten([[[1]]])), ([1, 2, 3, 4, 5], [], [1]))
check("L3-2 safe_append", lambda: (safe_append(1), safe_append(2), safe_append(3, [1, 2])), ([1], [2], [1, 2, 3]))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
