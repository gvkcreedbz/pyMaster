# SOLUTION FILE - try the hint ladder first!
"""Day 01 - Practice: Hello, Python!

Run:  python practice.py
Fill in every TODO. The auto-checker at the bottom tells you what passes.
"""

# ---------------------------------------------------------------------------
# L1-1 | Greeting variable   (Level 1 - Beginner)
# Store the text  Hello, World!  in a variable called greeting.
# ---------------------------------------------------------------------------
greeting = None
# >>> SOLUTION
greeting = "Hello, World!"
# <<< SOLUTION

# ---------------------------------------------------------------------------
# L1-2 | Coffee total   (Level 1 - Beginner)
# 3 coffees cost 120 each. Store the total cost (a number, calculated by
# Python, not typed by you) in coffee_total.
# ---------------------------------------------------------------------------
coffee_total = None
# >>> SOLUTION
coffee_total = 3 * 120
# <<< SOLUTION

# ---------------------------------------------------------------------------
# L1-3 | Two lines in one text   (Level 1 - Beginner)
# Store the text below in two_lines. It must contain a real new line
# (hint: \n):   first line is  Chai   second line is  Samosa
# ---------------------------------------------------------------------------
two_lines = None
# >>> SOLUTION
two_lines = "Chai\nSamosa"
# <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | Print a receipt   (Level 2 - Intermediate)
# Inside the box, print EXACTLY these 5 lines (watch spaces/dots):
#   ===== CHAI POINT =====
#   Masala Chai x2 ... 60
#   Samosa x3 ... 45
#   TOTAL ... 105
#   Thank you, visit again!
# ---------------------------------------------------------------------------
def print_receipt():
    # >>> SOLUTION
    print("===== CHAI POINT =====")
    print("Masala Chai x2 ... 60")
    print("Samosa x3 ... 45")
    print("TOTAL ... 105")
    print("Thank you, visit again!")
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | sep and end   (Level 2 - Intermediate)
# Make the box print exactly two lines:
#   2026-11-16
#   Loading...done
# Use the numbers 2026, 11, 16 with sep="-" for line 1, and end="..." for line 2.
# ---------------------------------------------------------------------------
def print_date_and_loading():
    # >>> SOLUTION
    print(2026, 11, 16, sep="-")
    print("Loading", end="...")
    print("done")
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | Star triangle   (Level 3 - Challenge)
# Print this triangle (4 rows). Do NOT type the stars by hand: use "*" * n.
#   *
#   **
#   ***
#   ****
# ---------------------------------------------------------------------------
def print_triangle():
    # >>> SOLUTION
    print("*" * 1)
    print("*" * 2)
    print("*" * 3)
    print("*" * 4)
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
import io
from contextlib import redirect_stdout

_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


def printed(fn):
    """Return everything fn() prints, as one string."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn()
    return buf.getvalue()


print("--- Day 01 checks ---")
check("L1-1 greeting", lambda: greeting, "Hello, World!")
check("L1-2 coffee_total", lambda: coffee_total, 360)
check("L1-3 two_lines", lambda: two_lines, "Chai\nSamosa")
check("L2-1 print_receipt", lambda: printed(print_receipt),
      "===== CHAI POINT =====\nMasala Chai x2 ... 60\nSamosa x3 ... 45\nTOTAL ... 105\nThank you, visit again!\n")
check("L2-2 print_date_and_loading", lambda: printed(print_date_and_loading), "2026-11-16\nLoading...done\n")
check("L3-1 print_triangle", lambda: printed(print_triangle), "*\n**\n***\n****\n")
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
