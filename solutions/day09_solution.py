# SOLUTION FILE - try the hint ladder first!
"""Day 09 - Practice: tuples and sets.

Run:  python practice.py
"""


# ---------------------------------------------------------------------------
# L1-1 | Unique count   (Level 1 - Beginner)
# How many different items are in the list?   unique_count([1, 2, 2, 3, 3, 3]) -> 3
# ---------------------------------------------------------------------------
def unique_count(items):
    """Return the number of distinct items."""
    # >>> SOLUTION
    return len(set(items))
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | Swap   (Level 1 - Beginner)
# Return the two values swapped, as a tuple.   swap(1, 2) -> (2, 1)
# ---------------------------------------------------------------------------
def swap(a, b):
    """Return (b, a)."""
    # >>> SOLUTION
    return b, a
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | Min and max   (Level 1 - Beginner)
# Return a tuple (smallest, largest).   min_max([7, 2, 9, 4]) -> (2, 9)
# ---------------------------------------------------------------------------
def min_max(numbers):
    """Return (min, max)."""
    # >>> SOLUTION
    return min(numbers), max(numbers)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | Mutual followers   (Level 2 - Intermediate)
# Names that appear in BOTH lists, as an alphabetically sorted list.
#   common_followers(["Diya", "Kabir", "Meera"], ["Meera", "Sana", "Kabir"]) -> ["Kabir", "Meera"]
# ---------------------------------------------------------------------------
def common_followers(a, b):
    """Return sorted names present in both lists."""
    # >>> SOLUTION
    return sorted(set(a) & set(b))
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | Friend suggestions   (Level 2 - Intermediate)
# Suggest people from friends_of_friends who are NOT already in my_friends and
# are not me. Return an alphabetically sorted list.
#   suggest_friends("Aarav", ["Diya", "Kabir"], ["Kabir", "Sana", "Aarav", "Meera"]) -> ["Meera", "Sana"]
# ---------------------------------------------------------------------------
def suggest_friends(me, my_friends, friends_of_friends):
    """Return sorted friend suggestions."""
    # >>> SOLUTION
    return sorted(set(friends_of_friends) - set(my_friends) - {me})
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | De-duplicate, keep order   (Level 2 - Intermediate)
# Remove repeated items but keep the FIRST occurrence of each, in original order.
#   dedupe(["a", "b", "a", "c", "b"]) -> ["a", "b", "c"]
# ---------------------------------------------------------------------------
def dedupe(items):
    """Return items without repeats, order preserved."""
    # >>> SOLUTION
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | First duplicate   (Level 3 - Challenge)
# Return the first item whose SECOND occurrence appears earliest while reading
# left to right. Return None when all items are unique.
#   first_duplicate([3, 1, 4, 1, 5, 3]) -> 1      first_duplicate([1, 2, 3]) -> None
# ---------------------------------------------------------------------------
def first_duplicate(items):
    """Return the first repeated item or None."""
    # >>> SOLUTION
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | Two numbers that add up   (Level 3 - Challenge)
# True if two DIFFERENT positions in the list add up to target. Aim for ONE pass
# using a set (not two nested loops).
#   has_pair_with_sum([2, 7, 11, 15], 9) -> True      has_pair_with_sum([3], 6) -> False
#   has_pair_with_sum([3, 3], 6) -> True
# ---------------------------------------------------------------------------
def has_pair_with_sum(numbers, target):
    """Return True if any two items sum to target."""
    # >>> SOLUTION
    seen = set()
    for n in numbers:
        if target - n in seen:
            return True
        seen.add(n)
    return False
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


print("--- Day 09 checks ---")
check("L1-1 unique_count", lambda: (unique_count([1, 2, 2, 3, 3, 3]), unique_count([])), (3, 0))
check("L1-2 swap", lambda: swap(1, 2), (2, 1))
check("L1-3 min_max", lambda: min_max([7, 2, 9, 4]), (2, 9))
check("L2-1 common_followers", lambda: common_followers(["Diya", "Kabir", "Meera"], ["Meera", "Sana", "Kabir"]), ["Kabir", "Meera"])
check("L2-2 suggest_friends", lambda: suggest_friends("Aarav", ["Diya", "Kabir"], ["Kabir", "Sana", "Aarav", "Meera"]), ["Meera", "Sana"])
check("L2-3 dedupe", lambda: dedupe(["a", "b", "a", "c", "b"]), ["a", "b", "c"])
check("L3-1 first_duplicate", lambda: (first_duplicate([3, 1, 4, 1, 5, 3]), first_duplicate([1, 2, 3])), (1, None))
check("L3-2 has_pair_with_sum", lambda: (has_pair_with_sum([2, 7, 11, 15], 9), has_pair_with_sum([3], 6),
                                         has_pair_with_sum([3, 3], 6), has_pair_with_sum([1, 2, 4], 10)), (True, False, True, False))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
