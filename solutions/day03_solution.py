# SOLUTION FILE - try the hint ladder first!
"""Day 03 - Practice: numbers and operators.

Run:  python practice.py
Each task is a "function box": fill in the body and `return` the answer.
"""


# ---------------------------------------------------------------------------
# L1-1 | Discount price   (Level 1 - Beginner)
# Return the price after taking percent off.   apply_discount(1000, 20) -> 800.0
# ---------------------------------------------------------------------------
def apply_discount(price, percent):
    """Return price after the discount percent."""
    # >>> SOLUTION
    return price - price * percent / 100
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | Add GST   (Level 1 - Beginner)
# Return price plus GST percent.   add_gst(1000, 18) -> 1180.0
# ---------------------------------------------------------------------------
def add_gst(price, gst_percent):
    """Return price including GST."""
    # >>> SOLUTION
    return price + price * gst_percent / 100
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | Even or odd   (Level 1 - Beginner)
# Return True if n is even, otherwise False.   is_even(10) -> True, is_even(7) -> False
# ---------------------------------------------------------------------------
def is_even(n):
    """Return True for even numbers."""
    # >>> SOLUTION
    return n % 2 == 0
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | Minutes to hours   (Level 2 - Intermediate)
# Return text like "2h 5m".   hours_minutes(125) -> "2h 5m",  hours_minutes(45) -> "0h 45m"
# ---------------------------------------------------------------------------
def hours_minutes(total_minutes):
    """Convert minutes to 'Hh Mm' text."""
    # >>> SOLUTION
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes}m"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | BMI   (Level 2 - Intermediate)
# BMI = weight_kg / (height in METRES) ** 2, rounded to 1 decimal.
#   bmi(70, 175) -> 22.9
# ---------------------------------------------------------------------------
def bmi(weight_kg, height_cm):
    """Return BMI rounded to 1 decimal."""
    # >>> SOLUTION
    return round(weight_kg / (height_cm / 100) ** 2, 1)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | Home-loan EMI   (Level 3 - Challenge)
# r = annual_rate_percent / 12 / 100      n = years * 12
# EMI = P * r * (1 + r) ** n / ((1 + r) ** n - 1)    -> round to 2 decimals
#   emi(500000, 9, 5) -> 10379.18
# ---------------------------------------------------------------------------
def emi(principal, annual_rate_percent, years):
    """Return the monthly EMI rounded to 2 decimals."""
    # >>> SOLUTION
    r = annual_rate_percent / 12 / 100
    n = years * 12
    return round(principal * r * (1 + r) ** n / ((1 + r) ** n - 1), 2)
    # <<< SOLUTION


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


print("--- Day 03 checks ---")
check("L1-1 apply_discount", lambda: apply_discount(1000, 20), 800.0)
check("L1-1 apply_discount #2", lambda: apply_discount(2499, 10), 2249.1)
check("L1-2 add_gst", lambda: add_gst(1000, 18), 1180.0)
check("L1-3 is_even(10)", lambda: is_even(10), True)
check("L1-3 is_even(7)", lambda: is_even(7), False)
check("L2-1 hours_minutes(125)", lambda: hours_minutes(125), "2h 5m")
check("L2-1 hours_minutes(45)", lambda: hours_minutes(45), "0h 45m")
check("L2-2 bmi(70, 175)", lambda: bmi(70, 175), 22.9)
check("L3-1 emi 5L/9%/5y", lambda: emi(500000, 9, 5), 10379.18)
check("L3-1 emi 12L/8.5%/20y", lambda: emi(1200000, 8.5, 20), 10413.88)
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
