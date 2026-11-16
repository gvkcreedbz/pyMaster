"""Day 24 - Practice: pytest-style testing.

Run:  python practice.py     (needs:  python -m pip install pytest)

Today YOU write the TESTS. The checker grades them by "mutation testing":
 * your test must PASS on the correct code, and
 * it must FAIL on secretly broken copies ("mutants") of that code.
A weak test (like `assert True`) lets the mutants survive -> FAIL.
"""
import re

try:
    import pytest
except ImportError:
    raise SystemExit("pytest is missing. Run:  python -m pip install pytest")


# ---------------------------------------------------------------------------
# L1-1 | test_is_even   (Level 1 - Beginner)
# is_even below is correct. Write a test with several asserts that would catch a
# broken version (hint: think 0, negative numbers, odd numbers).
# ---------------------------------------------------------------------------
def is_even(n):
    return n % 2 == 0


def test_is_even():
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | clamp   (Level 1 - Beginner)
# Return `value` limited to the range [low, high]:
#   clamp(5, 0, 10) -> 5    clamp(-3, 0, 10) -> 0    clamp(15, 0, 10) -> 10
# ---------------------------------------------------------------------------
def clamp(value, low, high):
    """Limit value to the range low..high."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | test_percent_to_grade   (Level 1 - Beginner)
# Rules: >=90 "A", >=75 "B", >=50 "C", else "F". Bugs love BOUNDARIES: test the exact
# boundary values AND the numbers just below them.
# ---------------------------------------------------------------------------
def percent_to_grade(score):
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 50:
        return "C"
    return "F"


def test_percent_to_grade():
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | test_slugify   (Level 2 - Intermediate)
# slugify("  Hello,  World! ") -> "hello-world"  (lower-case, symbols removed,
# spaces collapsed to single "-", no "-" at the ends). Write a test that loops over a
# table of (input, expected) pairs. Must catch 3 different bugs.
# ---------------------------------------------------------------------------
def slugify(text):
    cleaned = re.sub(r"[^a-z0-9 ]", "", text.lower())
    return "-".join(cleaned.split())


def test_slugify():
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | test_withdraw_rejects_overdraft   (Level 2 - Intermediate)
# Account.withdraw(amount) must raise ValueError when amount > balance, and must leave
# the balance UNCHANGED. Use `with pytest.raises(ValueError):`.
# ---------------------------------------------------------------------------
class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0 or amount > self.balance:
            raise ValueError("invalid amount")
        self.balance -= amount


def test_withdraw_rejects_overdraft():
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | test_account_flow   (Level 2 - Intermediate)
# Test the normal behaviour of Account: deposit increases the balance, withdraw
# decreases it (including withdrawing the ENTIRE balance), and depositing a
# non-positive amount raises ValueError.
# ---------------------------------------------------------------------------
def test_account_flow():
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | word_count (TDD)   (Level 3 - Challenge)
# The test below already exists. Write word_count(text) so it passes:
# lower-case words (letters and apostrophes only, punctuation ignored) -> counts dict.
# ---------------------------------------------------------------------------
def word_count(text):
    """Return {word: how many times it appears}."""
    # TODO: write your code here
    pass  # delete this line once you add your code


def test_word_count():
    assert word_count("The cat. The DOG!") == {"the": 2, "cat": 1, "dog": 1}
    assert word_count("") == {}
    assert word_count("don't stop") == {"don't": 1, "stop": 1}


# ---------------------------------------------------------------------------
# L3-2 | median (finish it using tests)   (Level 3 - Challenge)
# median([3, 1, 2]) -> 2     median([4, 1, 3, 2]) -> 2.5     median([5]) -> 5
# median([]) must raise ValueError("empty list"). One part is missing: run the checker,
# read the failure messages and complete the missing lines (sort first!).
# ---------------------------------------------------------------------------
def median(numbers):
    # TODO: write your code here
    pass  # delete this line once you add your code
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


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


def _passes(test_fn):
    """Run one test function; True if it raised nothing."""
    try:
        test_fn()
        return True
    except (Exception, pytest.fail.Exception):
        return False


def _kills(test_fn, target_name, mutants):
    """Test must pass on the real code and fail on every mutant."""
    original = globals()[target_name]
    if not _passes(test_fn):
        return "your test FAILS on the correct code - fix the test"
    survivors = []
    for label, broken in mutants.items():
        globals()[target_name] = broken
        try:
            if _passes(test_fn):
                survivors.append(label)
        finally:
            globals()[target_name] = original
    return "OK" if not survivors else f"test did not catch these bugs: {survivors}"


class _NoOverdraftCheck(Account):
    def withdraw(self, amount):
        self.balance -= amount


class _WrongException(Account):
    def withdraw(self, amount):
        if amount > self.balance:
            raise RuntimeError("wrong exception type")
        self.balance -= amount


class _ChangesThenRaises(Account):
    def withdraw(self, amount):
        self.balance -= amount
        if self.balance < 0:
            raise ValueError("invalid amount")


class _DepositSubtracts(Account):
    def deposit(self, amount):
        self.balance -= amount


class _DepositAllowsAnything(Account):
    def deposit(self, amount):
        self.balance += amount


class _WithdrawDoesNothing(Account):
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("invalid amount")


class _CannotEmptyAccount(Account):
    def withdraw(self, amount):
        if amount >= self.balance:
            raise ValueError("invalid amount")
        self.balance -= amount


def _grade_mutant(low_a, low_b, low_c):
    def grade(score):
        if score >= low_a:
            return "A"
        if score >= low_b:
            return "B"
        if score >= low_c:
            return "C"
        return "F"
    return grade


print("--- Day 24 checks ---")
check("L1-1 test_is_even catches bugs", lambda: _kills(test_is_even, "is_even", {
    "returns odd instead": lambda n: n % 2 == 1,
    "always True": lambda n: True,
    "breaks on 0 and negatives": lambda n: n > 0 and n % 2 == 0,
}), "OK")
check("L1-2 clamp values", lambda: [clamp(5, 0, 10), clamp(-3, 0, 10), clamp(15, 0, 10), clamp(0, 0, 10), clamp(10, 0, 10), clamp(2.5, 0, 1)],
      [5, 0, 10, 0, 10, 1])
check("L1-3 test_percent_to_grade catches boundary bugs", lambda: _kills(test_percent_to_grade, "percent_to_grade", {
    "> 90 instead of >= 90": _grade_mutant(91, 75, 50),
    "> 75 instead of >= 75": _grade_mutant(90, 76, 50),
    "> 50 instead of >= 50": _grade_mutant(90, 75, 51),
}), "OK")
check("L2-1 test_slugify catches bugs", lambda: _kills(test_slugify, "slugify", {
    "forgets lower-case": lambda t: "-".join(re.sub(r"[^a-zA-Z0-9 ]", "", t).split()),
    "keeps extra spaces": lambda t: re.sub(r"[^a-z0-9 ]", "", t.lower()).replace(" ", "-"),
    "keeps symbols": lambda t: "-".join(t.lower().split()),
}), "OK")
check("L2-2 test_withdraw_rejects_overdraft catches bugs", lambda: _kills(test_withdraw_rejects_overdraft, "Account", {
    "no overdraft check": _NoOverdraftCheck,
    "wrong exception type": _WrongException,
    "changes balance before raising": _ChangesThenRaises,
}), "OK")
check("L2-3 test_account_flow catches bugs", lambda: _kills(test_account_flow, "Account", {
    "deposit subtracts": _DepositSubtracts,
    "deposit accepts 0/negative": _DepositAllowsAnything,
    "withdraw forgets to subtract": _WithdrawDoesNothing,
    "cannot withdraw the full balance": _CannotEmptyAccount,
}), "OK")
check("L3-1 the provided test_word_count passes", lambda: _passes(test_word_count), True)
check("L3-1 word_count extra cases", lambda: (word_count("Hello, hello HELLO"), word_count("a b a. b! c?")),
      ({"hello": 3}, {"a": 2, "b": 2, "c": 1}))


def _median_error():
    try:
        median([])
    except ValueError as e:
        return str(e)
    return "no error"


check("L3-2 median odd / even / single", lambda: (median([3, 1, 2]), median([4, 1, 3, 2]), median([5]), median([9, 1, 5, 7, 3])), (2, 2.5, 5, 5))
check("L3-2 median of empty list raises ValueError", _median_error, "empty list")
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
