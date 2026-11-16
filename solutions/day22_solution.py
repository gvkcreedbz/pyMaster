# SOLUTION FILE - try the hint ladder first!
"""Day 22 - Practice: generators, decorators, context managers.

Run:  python practice.py
"""
import functools
from contextlib import contextmanager


# ---------------------------------------------------------------------------
# L1-1 | countdown   (Level 1 - Beginner)
# A GENERATOR that yields n, n-1, ..., 1 (nothing when n <= 0).
#   list(countdown(3)) -> [3, 2, 1]
# ---------------------------------------------------------------------------
def countdown(n):
    """Yield n down to 1."""
    # >>> SOLUTION
    while n > 0:
        yield n
        n -= 1
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | fibonacci_gen   (Level 1 - Beginner)
# An INFINITE generator of Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8, ...
# ---------------------------------------------------------------------------
def fibonacci_gen():
    """Yield Fibonacci numbers forever."""
    # >>> SOLUTION
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | running_average   (Level 1 - Beginner)
# Generator: after each number yield the average of all numbers so far, rounded to 2.
#   list(running_average([10, 20, 60])) -> [10.0, 15.0, 30.0]
# ---------------------------------------------------------------------------
def running_average(numbers):
    """Yield the running mean."""
    # >>> SOLUTION
    total = 0
    count = 0
    for n in numbers:
        total += n
        count += 1
        yield round(total / count, 2)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | count_calls decorator   (Level 2 - Intermediate)
# @count_calls counts how many times the decorated function was called and stores
# the number in the attribute  .calls  of the decorated function (start at 0).
# The function must still return its normal result and keep its __name__.
# ---------------------------------------------------------------------------
def count_calls(func):
    """Decorator: count the calls in func.calls."""
    # >>> SOLUTION
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)

    wrapper.calls = 0
    return wrapper
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | retry(times) decorator with an argument   (Level 2 - Intermediate)
# @retry(3): call the function up to `times` times. Return the first successful
# result; if every attempt raises, raise the LAST exception. Keep __name__.
# ---------------------------------------------------------------------------
def retry(times):
    """Decorator factory: retry a function."""
    # >>> SOLUTION
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
            raise last_error
        return wrapper
    return decorator
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | ignore_errors context manager   (Level 2 - Intermediate)
# with ignore_errors(ValueError, KeyError): ...   swallows those exception types
# (and ONLY those) raised inside the block. Use @contextmanager.
# ---------------------------------------------------------------------------
@contextmanager
def ignore_errors(*exc_types):
    """Context manager that ignores the given exception types."""
    # >>> SOLUTION
    try:
        yield
    except exc_types:
        pass
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | chunked   (Level 3 - Challenge)
# Generator that groups any iterable into lists of `size` items (the last list may be
# shorter). Must work lazily with generators too.
#   list(chunked(range(7), 3)) -> [[0, 1, 2], [3, 4, 5], [6]]
# ---------------------------------------------------------------------------
def chunked(iterable, size):
    """Yield lists of at most `size` items."""
    # >>> SOLUTION
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | memoize decorator   (Level 3 - Challenge)
# Cache results by the positional arguments: calling again with the same arguments
# returns the stored value WITHOUT running the function again. Keep __name__.
# ---------------------------------------------------------------------------
def memoize(func):
    """Decorator: remember results."""
    # >>> SOLUTION
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
import inspect
from itertools import islice

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
    """Return (ExceptionName, message) if fn() raises, else 'no error'."""
    try:
        fn()
    except Exception as e:
        return type(e).__name__, str(e)
    return "no error"


print("--- Day 22 checks ---")
check("L1-1 countdown", lambda: (list(countdown(3)), list(countdown(0)), inspect.isgenerator(countdown(2))), ([3, 2, 1], [], True))
check("L1-2 fibonacci_gen", lambda: list(islice(fibonacci_gen(), 10)), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])
check("L1-3 running_average", lambda: (list(running_average([10, 20, 60])), inspect.isgenerator(running_average([1]))),
      ([10.0, 15.0, 30.0], True))


def _count_calls():
    @count_calls
    def add(a, b):
        """Add."""
        return a + b

    first = add.calls
    return first, add(1, 2), add(3, 4), add.calls, add.__name__


check("L2-1 count_calls", _count_calls, (0, 3, 7, 2, "add"))


def _retry_ok():
    state = {"n": 0}

    @retry(3)
    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise ConnectionError("down")
        return "ok"

    return flaky(), state["n"], flaky.__name__


check("L2-2 retry succeeds on 3rd try", _retry_ok, ("ok", 3, "flaky"))
check("L2-2 retry gives up (last error)", lambda: error_of(lambda: retry(2)(lambda: 1 / 0)()), ("ZeroDivisionError", "division by zero"))


def _ignore():
    with ignore_errors(ValueError, KeyError):
        int("x")
    with ignore_errors(KeyError):
        {}["a"]
    return "survived"


check("L2-3 ignore_errors swallows listed types", _ignore, "survived")


def _raise_inside():
    with ignore_errors(KeyError):
        1 / 0


check("L2-3 ignore_errors does NOT swallow others", lambda: error_of(_raise_inside), ("ZeroDivisionError", "division by zero"))


check("L3-1 chunked", lambda: (list(chunked(range(7), 3)), list(chunked("abcd", 2)), list(chunked([], 3)), list(chunked(iter([1, 2, 3]), 5))),
      ([[0, 1, 2], [3, 4, 5], [6]], [["a", "b"], ["c", "d"]], [], [[1, 2, 3]]))


def _memo():
    calls = []

    @memoize
    def slow_square(x):
        calls.append(x)
        return x * x

    return slow_square(4), slow_square(4), slow_square(5), calls, slow_square.__name__


check("L3-2 memoize", _memo, (16, 16, 25, [4, 5], "slow_square"))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
