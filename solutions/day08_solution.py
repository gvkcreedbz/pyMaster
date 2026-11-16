# SOLUTION FILE - try the hint ladder first!
"""Day 08 - Practice: lists.

Run:  python practice.py
"""


# ---------------------------------------------------------------------------
# L1-1 | Cart total   (Level 1 - Beginner)
# Return the sum of the prices (0 for an empty cart).   cart_total([49.5, 30, 120]) -> 199.5
# ---------------------------------------------------------------------------
def cart_total(prices):
    """Return the total of all prices."""
    # >>> SOLUTION
    total = 0
    for p in prices:
        total += p
    return total
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | Add without duplicates   (Level 1 - Beginner)
# Add item to the END of cart only if it is not already in the cart.
# Change the list itself AND return it.
#   add_item(["milk"], "eggs") -> ["milk", "eggs"]     add_item(["milk"], "milk") -> ["milk"]
# ---------------------------------------------------------------------------
def add_item(cart, item):
    """Append item unless it is already present; return the cart."""
    # >>> SOLUTION
    if item not in cart:
        cart.append(item)
    return cart
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | Top two scores   (Level 1 - Beginner)
# Return the two highest scores, highest first. Do NOT change the original list.
#   top_two([72, 95, 88, 60]) -> [95, 88]
# ---------------------------------------------------------------------------
def top_two(scores):
    """Return the two highest scores in descending order."""
    # >>> SOLUTION
    return sorted(scores, reverse=True)[:2]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | Remove all   (Level 2 - Intermediate)
# Return a NEW list without any copy of value. Original list stays unchanged.
#   remove_all([1, 2, 3, 2, 2], 2) -> [1, 3]
# ---------------------------------------------------------------------------
def remove_all(items, value):
    """Return a new list without value."""
    # >>> SOLUTION
    result = []
    for x in items:
        if x != value:
            result.append(x)
    return result
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | Judges' trimmed average   (Level 2 - Intermediate)
# Drop ONE lowest and ONE highest score, then return the average of the rest,
# rounded to 2 decimals. At least 3 scores are always given.
#   trimmed_average([9, 5, 8, 10, 7]) -> 8.0
# ---------------------------------------------------------------------------
def trimmed_average(scores):
    """Average after removing one min and one max."""
    # >>> SOLUTION
    middle = sorted(scores)[1:-1]
    return round(sum(middle) / len(middle), 2)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | Running totals   (Level 2 - Intermediate)
#   running_totals([1, 2, 3, 4]) -> [1, 3, 6, 10]      running_totals([]) -> []
# ---------------------------------------------------------------------------
def running_totals(numbers):
    """Return the cumulative sums."""
    # >>> SOLUTION
    result = []
    total = 0
    for n in numbers:
        total += n
        result.append(total)
    return result
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | Rotate right   (Level 3 - Challenge)
# Move the last k items to the front, return a new list. k may be bigger than
# the list length (wrap around) and the list may be empty.
#   rotate([1, 2, 3, 4, 5], 2) -> [4, 5, 1, 2, 3]     rotate([1, 2, 3], 4) -> [3, 1, 2]
# ---------------------------------------------------------------------------
def rotate(items, k):
    """Rotate items to the right by k positions."""
    # >>> SOLUTION
    if not items:
        return []
    k = k % len(items)
    if k == 0:
        return items[:]
    return items[-k:] + items[:-k]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | Merge two sorted lists   (Level 3 - Challenge)
# Both inputs are already sorted ascending. Return one sorted list WITHOUT
# using sort()/sorted() (walk through both lists with two index variables).
#   merge_sorted([1, 4, 7], [2, 3, 9, 10]) -> [1, 2, 3, 4, 7, 9, 10]
# ---------------------------------------------------------------------------
def merge_sorted(a, b):
    """Merge two ascending lists into one ascending list."""
    # >>> SOLUTION
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result
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


print("--- Day 08 checks ---")
check("L1-1 cart_total", lambda: (cart_total([49.5, 30, 120]), cart_total([])), (199.5, 0))
check("L1-2 add_item new", lambda: add_item(["milk"], "eggs"), ["milk", "eggs"])
check("L1-2 add_item duplicate", lambda: add_item(["milk"], "milk"), ["milk"])


def _same_list_changed():
    c = ["a"]
    add_item(c, "b")
    return c


check("L1-2 add_item changes the list itself", _same_list_changed, ["a", "b"])


def _top_two_keeps_original():
    s = [72, 95, 88, 60]
    return top_two(s), s


check("L1-3 top_two", _top_two_keeps_original, ([95, 88], [72, 95, 88, 60]))


def _remove_all_check():
    original = [1, 2, 3, 2, 2]
    return remove_all(original, 2), original


check("L2-1 remove_all", _remove_all_check, ([1, 3], [1, 2, 3, 2, 2]))
check("L2-2 trimmed_average", lambda: (trimmed_average([9, 5, 8, 10, 7]), trimmed_average([6, 7, 9])), (8.0, 7.0))
check("L2-3 running_totals", lambda: (running_totals([1, 2, 3, 4]), running_totals([])), ([1, 3, 6, 10], []))
check("L3-1 rotate", lambda: (rotate([1, 2, 3, 4, 5], 2), rotate([1, 2, 3], 4), rotate([], 3), rotate([1, 2], 0)),
      ([4, 5, 1, 2, 3], [3, 1, 2], [], [1, 2]))
check("L3-2 merge_sorted", lambda: (merge_sorted([1, 4, 7], [2, 3, 9, 10]), merge_sorted([], [1]), merge_sorted([2, 2], [2])),
      ([1, 2, 3, 4, 7, 9, 10], [1], [2, 2, 2]))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
