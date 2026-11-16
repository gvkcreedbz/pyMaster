"""Day 18 - Code along: modules and the standard library."""
import random
import statistics
from collections import Counter, defaultdict, deque
from datetime import date, timedelta
from itertools import combinations, product

import shop_utils                          # our own module (shop_utils.py in this folder)
from shop_utils import format_money

# ---- 1. Using our own module ----
print(format_money(shop_utils.add_gst(999)))

# ---- 2. datetime: countdowns ----
today = date(2026, 11, 16)
christmas = date(2026, 12, 25)
print("Days to Christmas:", (christmas - today).days)
print("30 days from today:", today + timedelta(days=30), "| weekday number:", today.weekday())
print("Pretty:", christmas.strftime("%A, %d %B %Y"))
print("Parsed:", date.fromisoformat("2026-12-31").strftime("%d %b %Y"))

# ---- 3. random (seeded = repeatable) ----
random.seed(42)
print("Dice:", random.randint(1, 6), "| pick:", random.choice(["tea", "coffee", "juice"]))
deck = list(range(1, 11))
random.shuffle(deck)
print("Shuffled:", deck, "| sample of 3:", random.sample(deck, 3))

# ---- 4. collections ----
print(Counter("mississippi").most_common(2))
by_length = defaultdict(list)
for word in ["tea", "chai", "coffee", "milk", "pop"]:
    by_length[len(word)].append(word)
print(dict(by_length))
queue = deque(["Aarav", "Diya"])
queue.append("Kabir")
print("Next customer:", queue.popleft(), "| waiting:", list(queue))

# ---- 5. itertools ----
print(list(combinations(["A", "B", "C"], 2)))
print(len(list(product("HT", repeat=3))), "outcomes for 3 coin flips")

# ---- 6. statistics ----
marks = [72, 88, 95, 60, 88]
print("mean:", statistics.mean(marks), "median:", statistics.median(marks), "stdev:", round(statistics.stdev(marks), 2))
