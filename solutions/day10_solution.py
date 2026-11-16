# SOLUTION FILE - try the hint ladder first!
"""Day 10 - Practice: dictionaries.

Run:  python practice.py
"""


# ---------------------------------------------------------------------------
# L1-1 | Safe price lookup   (Level 1 - Beginner)
# Return the price of item from the menu dict, or 0 if it is not on the menu.
#   get_price({"chai": 20}, "chai") -> 20      get_price({"chai": 20}, "pizza") -> 0
# ---------------------------------------------------------------------------
def get_price(menu, item):
    """Return the item price or 0."""
    # >>> SOLUTION
    return menu.get(item, 0)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | Add stock   (Level 1 - Beginner)
# Increase inventory[item] by qty (create the key if missing). Change the dict
# itself and also return it.   add_stock({"pen": 5}, "pen", 3) -> {"pen": 8}
# ---------------------------------------------------------------------------
def add_stock(inventory, item, qty):
    """Add qty units of item to inventory."""
    # >>> SOLUTION
    inventory[item] = inventory.get(item, 0) + qty
    return inventory
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | Inventory value   (Level 1 - Beginner)
# prices = {"pen": 10, "book": 120}   stock = {"pen": 5, "book": 2, "bag": 4}
# Return the sum of price * stock for every item in stock. Items with no price
# are worth 0.   -> 10*5 + 120*2 = 290
# ---------------------------------------------------------------------------
def inventory_value(prices, stock):
    """Return total stock value."""
    # >>> SOLUTION
    total = 0
    for item, qty in stock.items():
        total += prices.get(item, 0) * qty
    return total
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | Word frequency   (Level 2 - Intermediate)
# Lowercase the text, remove . , ! ? characters, and count each word.
#   word_frequency("Hi hi, there!") -> {"hi": 2, "there": 1}
# ---------------------------------------------------------------------------
def word_frequency(text):
    """Return a dict of word counts."""
    # >>> SOLUTION
    text = text.lower()
    for ch in ".,!?":
        text = text.replace(ch, "")
    counts = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | Group by first letter   (Level 2 - Intermediate)
# Return a dict: first letter (lowercase) -> list of words in their ORIGINAL order.
#   group_by_first_letter(["apple", "banana", "avocado"]) -> {"a": ["apple", "avocado"], "b": ["banana"]}
# ---------------------------------------------------------------------------
def group_by_first_letter(words):
    """Group words by their first letter."""
    # >>> SOLUTION
    groups = {}
    for word in words:
        groups.setdefault(word[0].lower(), []).append(word)
    return groups
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | Merge and add   (Level 2 - Intermediate)
# Return a NEW dict with every key from a and b; if a key is in both, ADD the
# values. Do not change a or b.
#   merge_sum({"x": 1, "y": 2}, {"y": 3, "z": 4}) -> {"x": 1, "y": 5, "z": 4}
# ---------------------------------------------------------------------------
def merge_sum(a, b):
    """Merge two dicts, adding values of shared keys."""
    # >>> SOLUTION
    result = dict(a)
    for key, value in b.items():
        result[key] = result.get(key, 0) + value
    return result
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | Top-N words   (Level 3 - Challenge)
# Return a list of the n most frequent words (use word_frequency above). Ties are
# broken ALPHABETICALLY.  top_words("b a b c a d", 3) -> ["a", "b", "c"]
# (a and b both appear twice -> alphabetical; c and d appear once -> c first)
# ---------------------------------------------------------------------------
def top_words(text, n):
    """Return the n most common words, ties alphabetical."""
    # >>> SOLUTION
    freq = word_frequency(text)
    return sorted(sorted(freq), key=freq.get, reverse=True)[:n]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | First non-repeating character   (Level 3 - Challenge)
# Return the INDEX of the first character that appears exactly once, or -1.
#   first_unique_char("swiss") -> 1   ("w")     first_unique_char("aabb") -> -1
# ---------------------------------------------------------------------------
def first_unique_char(text):
    """Return the index of the first unique character, or -1."""
    # >>> SOLUTION
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    for i, ch in enumerate(text):
        if counts[ch] == 1:
            return i
    return -1
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


print("--- Day 10 checks ---")
check("L1-1 get_price", lambda: (get_price({"chai": 20}, "chai"), get_price({"chai": 20}, "pizza")), (20, 0))
check("L1-2 add_stock", lambda: (add_stock({"pen": 5}, "pen", 3), add_stock({}, "bag", 2)), ({"pen": 8}, {"bag": 2}))
check("L1-3 inventory_value", lambda: inventory_value({"pen": 10, "book": 120}, {"pen": 5, "book": 2, "bag": 4}), 290)
check("L2-1 word_frequency", lambda: word_frequency("Hi hi, there!"), {"hi": 2, "there": 1})
check("L2-2 group_by_first_letter", lambda: group_by_first_letter(["apple", "banana", "avocado"]),
      {"a": ["apple", "avocado"], "b": ["banana"]})


def _merge_check():
    a, b = {"x": 1, "y": 2}, {"y": 3, "z": 4}
    return merge_sum(a, b), a, b


check("L2-3 merge_sum (and inputs unchanged)", _merge_check, ({"x": 1, "y": 5, "z": 4}, {"x": 1, "y": 2}, {"y": 3, "z": 4}))
check("L3-1 top_words", lambda: (top_words("b a b c a d", 3), top_words("the cat the dog the end", 1)), (["a", "b", "c"], ["the"]))
check("L3-2 first_unique_char", lambda: (first_unique_char("swiss"), first_unique_char("aabb"), first_unique_char("python")), (1, -1, 0))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
