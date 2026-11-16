"""Day 09 - Code along: coordinates, unique visitors and mutual friends."""

# ---- 1. Tuples: fixed records ----
delhi = (28.61, 77.21)
lat, lon = delhi
print(f"Delhi is at {lat}N, {lon}E")
a, b = 1, 2
a, b = b, a
print("Swapped:", a, b)


def min_max(numbers):
    return min(numbers), max(numbers)       # returns a tuple


lowest, highest = min_max([7, 2, 9, 4])
print("Lowest/highest:", lowest, highest)

# ---- 2. Sets: unique visitors ----
monday = ["aarav", "diya", "aarav", "kabir", "diya"]
unique_monday = set(monday)
print(f"{len(monday)} visits, {len(unique_monday)} unique visitors:", sorted(unique_monday))

# ---- 3. Set maths: mutual friends ----
my_friends = {"Diya", "Kabir", "Meera", "Rohan"}
her_friends = {"Kabir", "Meera", "Sana", "Vihaan"}
print("Mutual:", sorted(my_friends & her_friends))
print("Only mine:", sorted(my_friends - her_friends))
print("Everyone:", sorted(my_friends | her_friends))
print("In exactly one list:", sorted(my_friends ^ her_friends))

# ---- 4. Friend suggestions ----
suggestions = her_friends - my_friends - {"Aarav"}   # Aarav is me
print("Suggested:", sorted(suggestions))

# ---- 5. De-duplicate while keeping the order ----
tags = ["python", "code", "python", "ai", "code", "data"]
seen = set()
ordered_unique = []
for tag in tags:
    if tag not in seen:
        seen.add(tag)
        ordered_unique.append(tag)
print(ordered_unique)

# ---- 6. Speed idea: membership in a set ----
blocked = {"spam@x.com", "bad@y.com"}
print("spam@x.com" in blocked, "ok@z.com" in blocked)
