"""Day 13 - Practice: nested data and JSON.

Run:  python practice.py
"""
import json

RESTAURANTS = [
    {"name": "Spice Hub", "city": "Delhi", "rating": 4.5, "cuisines": ["North Indian", "Chinese"], "avg_cost": 600},
    {"name": "Dosa Corner", "city": "Pune", "rating": 4.2, "cuisines": ["South Indian"], "avg_cost": 250},
    {"name": "Pasta Palace", "city": "Delhi", "rating": 4.0, "cuisines": ["Italian"], "avg_cost": 800},
    {"name": "Biryani Bay", "city": "Pune", "rating": 4.7, "cuisines": ["Mughlai", "North Indian"], "avg_cost": 500},
    {"name": "Wok Express", "city": "Mumbai", "rating": 3.9, "cuisines": ["Chinese"], "avg_cost": 450},
]


# ---------------------------------------------------------------------------
# L1-1 | Names in a city   (Level 1 - Beginner)
# Return the restaurant NAMES in the given city, in the original order.
#   names_in_city(RESTAURANTS, "Delhi") -> ["Spice Hub", "Pasta Palace"]
# ---------------------------------------------------------------------------
def names_in_city(restaurants, city):
    """Return names of restaurants in city."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | Average rating   (Level 1 - Beginner)
# Mean of all ratings rounded to 2 decimals; return 0 for an empty list.
# ---------------------------------------------------------------------------
def average_rating(restaurants):
    """Return the average rating."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | To JSON text   (Level 1 - Beginner)
# Convert any Python data into JSON text with the keys sorted alphabetically
# (sort_keys=True). to_json_text({"b": 1, "a": True}) -> '{"a": true, "b": 1}'
# ---------------------------------------------------------------------------
def to_json_text(data):
    """Return JSON text for data."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | Best restaurant per city   (Level 2 - Intermediate)
# Return {city: name_of_highest_rated_restaurant}.
#   -> {"Delhi": "Spice Hub", "Pune": "Biryani Bay", "Mumbai": "Wok Express"}
# ---------------------------------------------------------------------------
def best_by_city(restaurants):
    """Return the top-rated restaurant name for every city."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | Cuisine index   (Level 2 - Intermediate)
# Return {cuisine: [restaurant names sorted A-Z]} covering EVERY cuisine.
#   result["North Indian"] -> ["Biryani Bay", "Spice Hub"]
# ---------------------------------------------------------------------------
def cuisine_index(restaurants):
    """Map each cuisine to the sorted names serving it."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | Order total from JSON   (Level 2 - Intermediate)
# json_text looks like: '{"items": [{"name": "Dosa", "price": 90, "qty": 2}, ...]}'
# Return the sum of price * qty over all items (0 when there are no items).
# ---------------------------------------------------------------------------
def order_total(json_text):
    """Return the total of an order given as JSON text."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | City summary report   (Level 3 - Challenge)
# Return {city: {"count": n, "avg_rating": x, "avg_cost": y}} with both averages
# rounded to 2 decimals.
#   result["Delhi"] -> {"count": 2, "avg_rating": 4.25, "avg_cost": 700.0}
# ---------------------------------------------------------------------------
def city_summary(restaurants):
    """Summarise restaurants per city."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | deep_get   (Level 3 - Challenge)
# Follow a dotted path through nested dicts AND lists. Numbers in the path are
# list positions. Return default if anything is missing.
#   data = {"a": {"b": [{"c": 42}]}}
#   deep_get(data, "a.b.0.c") -> 42        deep_get(data, "a.x.0", "none") -> "none"
# ---------------------------------------------------------------------------
def deep_get(data, path, default=None):
    """Return the value at path or default."""
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


print("--- Day 13 checks ---")
check("L1-1 names_in_city", lambda: (names_in_city(RESTAURANTS, "Delhi"), names_in_city(RESTAURANTS, "Goa")),
      (["Spice Hub", "Pasta Palace"], []))
check("L1-2 average_rating", lambda: (average_rating(RESTAURANTS), average_rating([])), (4.26, 0))
check("L1-3 to_json_text", lambda: to_json_text({"b": 1, "a": True, "c": None}), '{"a": true, "b": 1, "c": null}')
check("L2-1 best_by_city", lambda: best_by_city(RESTAURANTS), {"Delhi": "Spice Hub", "Pune": "Biryani Bay", "Mumbai": "Wok Express"})
check("L2-2 cuisine_index", lambda: (cuisine_index(RESTAURANTS)["North Indian"], sorted(cuisine_index(RESTAURANTS))),
      (["Biryani Bay", "Spice Hub"], ["Chinese", "Italian", "Mughlai", "North Indian", "South Indian"]))
check("L2-3 order_total", lambda: (order_total('{"items": [{"name": "Dosa", "price": 90, "qty": 2}, {"name": "Tea", "price": 20, "qty": 1}]}'),
                                   order_total('{"items": []}'), order_total("{}")), (200, 0, 0))
check("L3-1 city_summary", lambda: city_summary(RESTAURANTS)["Delhi"], {"count": 2, "avg_rating": 4.25, "avg_cost": 700.0})
check("L3-1 city_summary Pune", lambda: city_summary(RESTAURANTS)["Pune"], {"count": 2, "avg_rating": 4.45, "avg_cost": 375.0})
_d = {"a": {"b": [{"c": 42}]}, "x": [10, 20]}
check("L3-2 deep_get found", lambda: (deep_get(_d, "a.b.0.c"), deep_get(_d, "x.1")), (42, 20))
check("L3-2 deep_get missing", lambda: (deep_get(_d, "a.x.0", "none"), deep_get(_d, "x.5"), deep_get(_d, "a.b.9.c", 0)), ("none", None, 0))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
