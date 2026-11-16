"""Day 24 - Code along: what assert does, and what a test runner does for you."""
import math


def add(a, b):
    return a + b


# ---- 1. assert ----
assert add(2, 3) == 5
print("assert passed silently")
try:
    assert add(2, 3) == 6, "add is broken"
except AssertionError as e:
    print("assert failed ->", e)

# ---- 2. A tiny test runner (pytest does this, plus much more) ----
def test_add_positive():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-2, -3) == -5


def test_add_floats():
    assert math.isclose(add(0.1, 0.2), 0.3)      # pytest.approx(0.3) does the same job


def test_deliberate_failure():
    assert add(1, 1) == 3


tests = [f for name, f in sorted(globals().items()) if name.startswith("test_") and callable(f)]
passed = failed = 0
for test in tests:
    try:
        test()
        print("PASS", test.__name__)
        passed += 1
    except AssertionError:
        print("FAIL", test.__name__)
        failed += 1
print(f"{passed} passed, {failed} failed  (the failure above is deliberate!)")

# ---- 3. Floats are tricky ----
print(0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))

print("\nNow run the REAL thing:  python -m pytest -v   (in this folder)")
