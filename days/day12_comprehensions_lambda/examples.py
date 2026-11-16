"""Day 12 - Code along: filters, sorting and pairing."""

# ---- 1. Comprehensions ----
nums = [1, 2, 3, 4, 5, 6]
print([n * n for n in nums])
print([n for n in nums if n % 2 == 0])
print(["even" if n % 2 == 0 else "odd" for n in nums])
print({n: n ** 2 for n in range(1, 4)})

# ---- 2. Product filters ----
catalog = [
    {"name": "Earbuds", "price": 1999, "rating": 4.3},
    {"name": "Power Bank", "price": 1299, "rating": 4.5},
    {"name": "Cable", "price": 299, "rating": 4.1},
    {"name": "Smartwatch", "price": 3499, "rating": 4.6},
]
budget = 2000
under_budget = [p["name"] for p in catalog if p["price"] <= budget]
print("Under", budget, ":", under_budget)
best_first = sorted(catalog, key=lambda p: p["rating"], reverse=True)
print("Best rated:", [p["name"] for p in best_first])
cheapest = min(catalog, key=lambda p: p["price"])
print("Cheapest:", cheapest["name"])

# ---- 3. Music chart: sort by plays, ties by title ----
songs = [("Kesariya", 900), ("Apna Bana Le", 900), ("Heeriye", 1200), ("Tum Hi Ho", 400)]
chart = sorted(songs, key=lambda s: (-s[1], s[0]))
for rank, (title, plays) in enumerate(chart, start=1):
    print(f"{rank}. {title} ({plays} plays)")

# ---- 4. zip ----
names = ["Aarav", "Diya", "Kabir"]
marks = [88, 95, 40]
scores = dict(zip(names, marks))
print(scores)
print("Anyone failed?", any(m < 40 for m in marks), "| Everyone >= 40?", all(m >= 40 for m in marks))

# ---- 5. Matrix transpose ----
matrix = [[1, 2, 3], [4, 5, 6]]
print([list(col) for col in zip(*matrix)])

# ---- 6. Big sum without building a list ----
print(sum(n * n for n in range(1, 1001)))
