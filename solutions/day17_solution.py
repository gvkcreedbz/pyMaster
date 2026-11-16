# SOLUTION FILE - try the hint ladder first!
"""Day 17 - Practice: errors, exceptions and logging.

Run:  python practice.py
"""
import logging
from pathlib import Path


class InsufficientFundsError(Exception):
    """Raised when a withdrawal is bigger than the balance. (given - don't edit)"""


# ---------------------------------------------------------------------------
# L1-1 | safe_int   (Level 1 - Beginner)
# Convert text to int; if that is impossible return `default` (never crash).
#   safe_int("42") -> 42     safe_int("abc") -> 0     safe_int("12.5", -1) -> -1
#   safe_int(None, 7) -> 7
# ---------------------------------------------------------------------------
def safe_int(text, default=0):
    """Return int(text) or default."""
    # >>> SOLUTION
    try:
        return int(text)
    except (ValueError, TypeError):
        return default
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | safe_divide   (Level 1 - Beginner)
# Return a / b, or None when b is zero.
# ---------------------------------------------------------------------------
def safe_divide(a, b):
    """Return a / b or None for division by zero."""
    # >>> SOLUTION
    try:
        return a / b
    except ZeroDivisionError:
        return None
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | read_first_line   (Level 1 - Beginner)
# Return the first line of the file without the trailing newline. If the file does
# not exist (or is empty) return "".
# ---------------------------------------------------------------------------
def read_first_line(path):
    """Return the first line or an empty string."""
    # >>> SOLUTION
    try:
        with open(path, encoding="utf-8") as f:
            return f.readline().rstrip("\n")
    except FileNotFoundError:
        return ""
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | parse_age   (Level 2 - Intermediate)
# Strip spaces, then:
#   not made only of digits  -> raise ValueError("Age must be a whole number")
#   number outside 0..120    -> raise ValueError("Age must be between 0 and 120")
# otherwise return the age as an int.
# ---------------------------------------------------------------------------
def parse_age(text):
    """Return a validated age."""
    # >>> SOLUTION
    text = text.strip()
    if not text.isdigit():
        raise ValueError("Age must be a whole number")
    age = int(text)
    if not 0 <= age <= 120:
        raise ValueError("Age must be between 0 and 120")
    return age
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | withdraw   (Level 2 - Intermediate)
# Return balance - amount. If amount > balance raise
#   InsufficientFundsError(f"Need Rs. {amount - balance} more")
# ---------------------------------------------------------------------------
def withdraw(balance, amount):
    """Return the new balance or raise InsufficientFundsError."""
    # >>> SOLUTION
    if amount > balance:
        raise InsufficientFundsError(f"Need Rs. {amount - balance} more")
    return balance - amount
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | retry   (Level 2 - Intermediate)
# Call func() (no arguments) up to `attempts` times. Return the first successful
# result. If every attempt raises, raise the LAST exception.
# ---------------------------------------------------------------------------
def retry(func, attempts):
    """Call func until it succeeds or attempts run out."""
    # >>> SOLUTION
    last_error = None
    for _ in range(attempts):
        try:
            return func()
        except Exception as e:
            last_error = e
    raise last_error
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | process_payments   (Level 3 - Challenge)
# payments = list of dicts {"id": ..., "amount": ...}. Return
#   {"ok": [ids that are fine], "failed": {id: reason}}
# Rules (check in this order): no "amount" key -> "missing amount"; amount can't be
# converted with float() (letters, None) -> "amount must be a number"; amount <= 0 ->
# "amount must be positive"; amount > 50000 -> "amount too large". "250" counts as 250.
# ---------------------------------------------------------------------------
def process_payments(payments):
    """Validate a batch of payments."""
    # >>> SOLUTION
    result = {"ok": [], "failed": {}}
    for p in payments:
        try:
            amount = float(p["amount"])
        except KeyError:
            result["failed"][p["id"]] = "missing amount"
            continue
        except (ValueError, TypeError):
            result["failed"][p["id"]] = "amount must be a number"
            continue
        if amount <= 0:
            result["failed"][p["id"]] = "amount must be positive"
        elif amount > 50000:
            result["failed"][p["id"]] = "amount too large"
        else:
            result["ok"].append(p["id"])
    return result
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | make_logger   (Level 3 - Challenge)
# Return a logging.Logger called `name` that writes to the file `path` (UTF-8) using
# the format "LEVEL - message" (e.g. "ERROR - payment failed"). Level INFO: DEBUG
# messages must NOT appear. Hint: getLogger, setLevel, FileHandler, Formatter,
# addHandler. Set logger.propagate = False so nothing is printed twice.
# ---------------------------------------------------------------------------
def make_logger(name, path):
    """Return a file logger."""
    # >>> SOLUTION
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
import tempfile

_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


def error_of(fn):
    """Return (ExceptionName, message) if fn() raises, else the string 'no error'."""
    try:
        fn()
    except Exception as e:
        return type(e).__name__, str(e)
    return "no error"


print("--- Day 17 checks ---")
check("L1-1 safe_int", lambda: (safe_int("42"), safe_int("abc"), safe_int("12.5", -1), safe_int(None, 7)), (42, 0, -1, 7))
check("L1-2 safe_divide", lambda: (safe_divide(10, 4), safe_divide(1, 0)), (2.5, None))
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp / "a.txt").write_text("first\nsecond\n", encoding="utf-8")
    (tmp / "empty.txt").write_text("", encoding="utf-8")
    check("L1-3 read_first_line", lambda: (read_first_line(tmp / "a.txt"), read_first_line(tmp / "missing.txt"), read_first_line(tmp / "empty.txt")),
          ("first", "", ""))
    check("L2-1 parse_age ok", lambda: (parse_age(" 25 "), parse_age("0"), parse_age("120")), (25, 0, 120))
    check("L2-1 parse_age text", lambda: error_of(lambda: parse_age("abc")), ("ValueError", "Age must be a whole number"))
    check("L2-1 parse_age range", lambda: error_of(lambda: parse_age("150")), ("ValueError", "Age must be between 0 and 120"))
    check("L2-2 withdraw ok", lambda: withdraw(1000, 400), 600)
    check("L2-2 withdraw error", lambda: error_of(lambda: withdraw(100, 600)), ("InsufficientFundsError", "Need Rs. 500 more"))
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("network down")
        return "connected"

    check("L2-3 retry succeeds on 3rd try", lambda: (retry(flaky, 5), len(calls)), ("connected", 3))
    check("L2-3 retry gives up", lambda: error_of(lambda: retry(lambda: 1 / 0, 3)), ("ZeroDivisionError", "division by zero"))
    check("L3-1 process_payments", lambda: process_payments([
        {"id": 1, "amount": 250}, {"id": 2, "amount": "abc"}, {"id": 3}, {"id": 4, "amount": -5},
        {"id": 5, "amount": 70000}, {"id": 6, "amount": "99.5"}, {"id": 7, "amount": None}]),
        {"ok": [1, 6], "failed": {2: "amount must be a number", 3: "missing amount", 4: "amount must be positive",
                                  5: "amount too large", 7: "amount must be a number"}})
    log_file = tmp / "x.log"

    def _logged_lines():
        lg = make_logger("day17-test", log_file)
        try:
            lg.info("order placed")
            lg.debug("hidden detail")
            lg.error("payment failed")
        finally:
            for h in list(lg.handlers):
                h.close()
                lg.removeHandler(h)
        return log_file.read_text(encoding="utf-8").splitlines()

    check("L3-2 make_logger", _logged_lines, ["INFO - order placed", "ERROR - payment failed"])
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
