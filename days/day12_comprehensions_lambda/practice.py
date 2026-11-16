"""Day 12 - Practice: comprehensions, lambda, sorting and zip.

Run:  python practice.py
Tip: write a normal loop first, then compress it into a comprehension.
"""


# ---------------------------------------------------------------------------
# L1-1 | Squares   (Level 1 - Beginner)
# squares(4) -> [1, 4, 9, 16]      squares(0) -> []
# ---------------------------------------------------------------------------
def squares(n):
    """Return the squares of 1..n."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | Even numbers   (Level 1 - Beginner)
# even_numbers([1, 2, 3, 4, 6]) -> [2, 4, 6]
# ---------------------------------------------------------------------------
def even_numbers(numbers):
    """Return only the even numbers."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | Uppercase list   (Level 1 - Beginner)
# to_upper(["ab", "Cd"]) -> ["AB", "CD"]
# ---------------------------------------------------------------------------
def to_upper(words):
    """Return the words in uppercase."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | Affordable items   (Level 2 - Intermediate)
# menu is a dict name -> price. Return the names whose price is <= budget, sorted A-Z.
#   affordable({"chai": 20, "pizza": 300, "samosa": 15}, 50) -> ["chai", "samosa"]
# ---------------------------------------------------------------------------
def affordable(menu, budget):
    """Return sorted names of items within budget."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | Sort by length   (Level 2 - Intermediate)
# Shortest word first; words of the same length in alphabetical order.
#   sort_by_length(["pear", "fig", "apple", "kiwi"]) -> ["fig", "kiwi", "pear", "apple"]
# ---------------------------------------------------------------------------
def sort_by_length(words):
    """Return words sorted by (length, alphabet)."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | Names and scores   (Level 2 - Intermediate)
# Pair two lists into a dict (use zip).  pair_up(["a", "b"], [1, 2]) -> {"a": 1, "b": 2}
# ---------------------------------------------------------------------------
def pair_up(names, scores):
    """Return {name: score}."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | Top songs   (Level 3 - Challenge)
# songs = list of (title, plays) tuples. Return the TITLES of the n most-played
# songs, most plays first; equal plays -> title A-Z.
#   top_songs([("B", 5), ("A", 5), ("C", 9)], 2) -> ["C", "A"]
# ---------------------------------------------------------------------------
def top_songs(songs, n):
    """Return the titles of the top n songs."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | Transpose a matrix   (Level 3 - Challenge)
# Swap rows and columns. Return a list of lists.
#   transpose([[1, 2, 3], [4, 5, 6]]) -> [[1, 4], [2, 5], [3, 6]]
# ---------------------------------------------------------------------------
def transpose(matrix):
    """Return the transposed matrix."""
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


print("--- Day 12 checks ---")
check("L1-1 squares", lambda: (squares(4), squares(0)), ([1, 4, 9, 16], []))
check("L1-2 even_numbers", lambda: even_numbers([1, 2, 3, 4, 6]), [2, 4, 6])
check("L1-3 to_upper", lambda: to_upper(["ab", "Cd"]), ["AB", "CD"])
check("L2-1 affordable", lambda: affordable({"chai": 20, "pizza": 300, "samosa": 15}, 50), ["chai", "samosa"])
check("L2-2 sort_by_length", lambda: sort_by_length(["pear", "fig", "apple", "kiwi"]), ["fig", "kiwi", "pear", "apple"])
check("L2-3 pair_up", lambda: pair_up(["a", "b"], [1, 2]), {"a": 1, "b": 2})
check("L3-1 top_songs", lambda: (top_songs([("B", 5), ("A", 5), ("C", 9)], 2), top_songs([("x", 1)], 3)), (["C", "A"], ["x"]))
check("L3-2 transpose", lambda: (transpose([[1, 2, 3], [4, 5, 6]]), transpose([[7]])), ([[1, 4], [2, 5], [3, 6]], [[7]]))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
