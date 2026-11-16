"""Day 06 - Practice: loops.

Run:  python practice.py
"""


# ---------------------------------------------------------------------------
# L1-1 | Sum 1..n   (Level 1 - Beginner)
# Return 1 + 2 + ... + n using a loop.   sum_to(5) -> 15,  sum_to(100) -> 5050
# ---------------------------------------------------------------------------
def sum_to(n):
    """Return the sum of 1..n."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | Count vowels   (Level 1 - Beginner)
# Count a, e, i, o, u in the text (upper or lower case).
#   count_vowels("Hello World") -> 3
# ---------------------------------------------------------------------------
def count_vowels(text):
    """Return how many vowels text contains."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | Multiplication table   (Level 1 - Beginner)
# Return 10 lines joined with "\n" (no trailing newline), like:
#   5 x 1 = 5
#   5 x 2 = 10   ...   5 x 10 = 50
# ---------------------------------------------------------------------------
def multiplication_table(n):
    """Return the table of n as one multi-line string."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | Factorial   (Level 2 - Intermediate)
# n! = 1 * 2 * ... * n    factorial(5) -> 120, factorial(0) -> 1
# ---------------------------------------------------------------------------
def factorial(n):
    """Return n factorial."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | FizzBuzz   (Level 2 - Intermediate)
# For numbers 1..n: multiples of 3 -> Fizz, of 5 -> Buzz, of both -> FizzBuzz,
# otherwise the number. Return everything joined by single spaces.
#   fizzbuzz(5) -> "1 2 Fizz 4 Buzz"
# ---------------------------------------------------------------------------
def fizzbuzz(n):
    """Return the FizzBuzz sequence as text."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | Prime check   (Level 2 - Intermediate)
# Return True if n is prime (only divisible by 1 and itself). 0 and 1 are not.
#   is_prime(7) -> True,  is_prime(9) -> False,  is_prime(1) -> False
# ---------------------------------------------------------------------------
def is_prime(n):
    """Return True when n is prime."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | PIN with 3 attempts   (Level 3 - Challenge)
# guesses_text holds guesses separated by commas, e.g. "1111,2222,4321".
# Return the attempt number (1, 2 or 3) at which the PIN was entered correctly.
# Only the FIRST 3 guesses count (card locks after that). Return 0 if the PIN
# was never entered correctly within 3 attempts.
#   first_correct_attempt("4321", "1111,2222,4321,0000") -> 3
#   first_correct_attempt("4321", "1,2,3,4321")          -> 0
# ---------------------------------------------------------------------------
def first_correct_attempt(correct_pin, guesses_text):
    """Return the winning attempt number (1-3) or 0."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | Star pyramid   (Level 3 - Challenge)
# Return a centred pyramid with n rows joined by "\n" (no trailing newline).
# Row i has (2*i - 1) stars, padded on the left with (n - i) spaces. n = 3:
#     *
#    ***
#   *****
# ---------------------------------------------------------------------------
def pyramid(n):
    """Return an n-row star pyramid."""
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


print("--- Day 06 checks ---")
check("L1-1 sum_to", lambda: (sum_to(5), sum_to(100), sum_to(0)), (15, 5050, 0))
check("L1-2 count_vowels", lambda: (count_vowels("Hello World"), count_vowels("RHYTHM"), count_vowels("AEIOU")), (3, 0, 5))
check("L1-3 multiplication_table", lambda: multiplication_table(5).split("\n")[::9], ["5 x 1 = 5", "5 x 10 = 50"])
check("L1-3 table has 10 lines", lambda: len(multiplication_table(3).split("\n")), 10)
check("L2-1 factorial", lambda: (factorial(5), factorial(0), factorial(10)), (120, 1, 3628800))
check("L2-2 fizzbuzz(5)", lambda: fizzbuzz(5), "1 2 Fizz 4 Buzz")
check("L2-2 fizzbuzz(15)", lambda: fizzbuzz(15).endswith("13 14 FizzBuzz"), True)
check("L2-3 is_prime", lambda: [is_prime(n) for n in (0, 1, 2, 7, 9, 97, 100)], [False, False, True, True, False, True, False])
check("L3-1 pin attempt 3", lambda: first_correct_attempt("4321", "1111,2222,4321,0000"), 3)
check("L3-1 pin attempt 1", lambda: first_correct_attempt("4321", "4321"), 1)
check("L3-1 pin locked", lambda: first_correct_attempt("4321", "1,2,3,4321"), 0)
check("L3-1 pin never", lambda: first_correct_attempt("4321", "1,2"), 0)
check("L3-2 pyramid(3)", lambda: pyramid(3), "  *\n ***\n*****")
check("L3-2 pyramid(1)", lambda: pyramid(1), "*")
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
