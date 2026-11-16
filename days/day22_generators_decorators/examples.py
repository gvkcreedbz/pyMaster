"""Day 22 - Code along: generators, decorators and context managers."""
import functools
import sys
import time
from contextlib import contextmanager
from itertools import islice


# ---- 1. Iterator protocol ----
it = iter([10, 20, 30])
print(next(it), next(it), next(it))
try:
    next(it)
except StopIteration:
    print("StopIteration: the iterator is exhausted (a for-loop catches this for you)")


# ---- 2. Generators ----
def countdown(n):
    while n > 0:
        yield n
        n -= 1


print(list(countdown(5)))

big_list = [n * n for n in range(100_000)]
lazy = (n * n for n in range(100_000))
print("list bytes:", sys.getsizeof(big_list), "| generator bytes:", sys.getsizeof(lazy))
print("sum without building a list:", sum(n * n for n in range(1, 1001)))


def naturals():
    n = 1
    while True:                       # infinite, but lazy = no problem
        yield n
        n += 1


print(list(islice(naturals(), 5)))

# Stream a log file one line at a time (constant memory)
from pathlib import Path

log = Path(__file__).resolve().parents[2] / "datasets" / "app.log"


def error_lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if " ERROR " in line:
                yield line.rstrip("\n")


first_two = list(islice(error_lines(log), 2))
print(*first_two, sep="\n")


# ---- 3. Decorators ----
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"  {func.__name__} took {time.perf_counter() - start:.3f}s")
        return result
    return wrapper


@timer
def slow_square(x):
    """Pretend to do heavy work."""
    time.sleep(0.05)
    return x * x


print(slow_square(12), "| name kept:", slow_square.__name__, "|", slow_square.__doc__)


def retry(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"  attempt {attempt} failed: {e}")
            raise RuntimeError(f"{func.__name__} failed {times} times")
        return wrapper
    return decorator


state = {"calls": 0}


@retry(3)
def flaky_download():
    state["calls"] += 1
    if state["calls"] < 3:
        raise ConnectionError("network blip")
    return "downloaded"


print(flaky_download())


@functools.lru_cache(maxsize=None)         # built-in memoize decorator
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print("fib(80) =", fib(80))


# ---- 4. Context manager ----
@contextmanager
def timer_block(label):
    start = time.perf_counter()
    try:
        yield
    finally:                              # runs even if the body fails
        print(f"  [{label}] finished in {time.perf_counter() - start:.3f}s")


with timer_block("sum of squares"):
    total = sum(n * n for n in range(200_000))
print("total:", total)
