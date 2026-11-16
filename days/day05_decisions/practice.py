"""Day 05 - Practice: decisions with if / elif / else.

Run:  python practice.py
"""


# ---------------------------------------------------------------------------
# L1-1 | Grade letter   (Level 1 - Beginner)
# 90+ -> "A", 75-89 -> "B", 50-74 -> "C", below 50 -> "Fail"
# ---------------------------------------------------------------------------
def grade(marks):
    """Return the grade letter for marks."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | Sign of a number   (Level 1 - Beginner)
# Return "positive", "negative" or "zero".
# ---------------------------------------------------------------------------
def sign(n):
    """Return 'positive', 'negative' or 'zero'."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | Biggest of three   (Level 1 - Beginner)
# Return the largest of a, b, c using if/elif (do NOT use max()).
# ---------------------------------------------------------------------------
def max_of_three(a, b, c):
    """Return the largest number."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | Delivery fee   (Level 2 - Intermediate)
# Members always pay 0. Non-members pay 0 when order_value >= 499.
# Otherwise: distance <= 3 km -> 30, <= 7 km -> 50, farther -> 80.
# ---------------------------------------------------------------------------
def delivery_fee(order_value, distance_km, is_member):
    """Return the delivery fee in rupees."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | Ticket price   (Level 2 - Intermediate)
# Base price 200. Under 5 years: free. Under 12 or 60 and above: half price (100).
# Weekend surcharge of +50 applies only if the ticket is not free.
# ---------------------------------------------------------------------------
def ticket_price(age, is_weekend):
    """Return the ticket price."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | Leap year   (Level 2 - Intermediate)
# Divisible by 4, except century years, which must be divisible by 400.
#   2024 -> True, 1900 -> False, 2000 -> True, 2023 -> False
# ---------------------------------------------------------------------------
def is_leap_year(year):
    """Return True for leap years."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | Rock-paper-scissors referee   (Level 3 - Challenge)
# Inputs are "rock", "paper" or "scissors". Rock beats scissors, scissors beats
# paper, paper beats rock. Return "Player 1 wins", "Player 2 wins" or "Draw".
# ---------------------------------------------------------------------------
def rps(p1, p2):
    """Return the winner of rock-paper-scissors."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | Triangle classifier   (Level 3 - Challenge)
# If the sum of any two sides is <= the third side -> "Not a triangle".
# Otherwise: all equal -> "Equilateral", exactly two equal -> "Isosceles",
# none equal -> "Scalene".
# ---------------------------------------------------------------------------
def triangle_type(a, b, c):
    """Return the triangle type."""
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


print("--- Day 05 checks ---")
for m, g in [(95, "A"), (90, "A"), (80, "B"), (50, "C"), (49, "Fail")]:
    check(f"L1-1 grade({m})", lambda m=m: grade(m), g)
check("L1-2 sign(5)", lambda: sign(5), "positive")
check("L1-2 sign(-2)", lambda: sign(-2), "negative")
check("L1-2 sign(0)", lambda: sign(0), "zero")
check("L1-3 max_of_three", lambda: (max_of_three(1, 9, 3), max_of_three(9, 2, 3), max_of_three(1, 2, 3)), (9, 9, 3))
for args, want in [((300, 2, False), 30), ((300, 5, False), 50), ((300, 10, False), 80),
                   ((600, 10, False), 0), ((100, 10, True), 0), ((499, 9, False), 0)]:
    check(f"L2-1 delivery_fee{args}", lambda args=args: delivery_fee(*args), want)
for args, want in [((3, True), 0), ((8, False), 100), ((8, True), 150), ((30, False), 200),
                   ((30, True), 250), ((65, False), 100)]:
    check(f"L2-2 ticket_price{args}", lambda args=args: ticket_price(*args), want)
check("L2-3 leap years", lambda: [is_leap_year(y) for y in (2024, 1900, 2000, 2023)], [True, False, True, False])
check("L3-1 rps draw", lambda: rps("rock", "rock"), "Draw")
check("L3-1 rps p1", lambda: [rps("rock", "scissors"), rps("scissors", "paper"), rps("paper", "rock")], ["Player 1 wins"] * 3)
check("L3-1 rps p2", lambda: [rps("scissors", "rock"), rps("paper", "scissors"), rps("rock", "paper")], ["Player 2 wins"] * 3)
check("L3-2 triangle", lambda: [triangle_type(3, 3, 3), triangle_type(3, 3, 5), triangle_type(3, 4, 5), triangle_type(1, 2, 3)],
      ["Equilateral", "Isosceles", "Scalene", "Not a triangle"])
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
