"""Day 08 - Code along: a shopping cart and a game leaderboard."""

# ---- 1. A cart that changes ----
cart = ["milk", "bread", "eggs"]
cart.append("butter")
cart.insert(0, "tea")
cart.extend(["jam", "salt"])
cart.remove("eggs")
print(cart, "| items:", len(cart))
print("Last removed:", cart.pop(), "| now:", cart)

# ---- 2. Prices and totals ----
prices = [49.5, 30, 120, 85.25]
print("Total:", sum(prices), "| cheapest:", min(prices), "| dearest:", max(prices))

# ---- 3. Loop with enumerate ----
for number, item in enumerate(cart, start=1):
    print(f"{number}. {item}")

# ---- 4. Leaderboard: sorting ----
scores = [72, 95, 88, 95, 60]
print("Top 3:", sorted(scores, reverse=True)[:3])
scores.sort()
print("Ascending:", scores)

# ---- 5. The copy trap ----
a = [1, 2, 3]
b = a            # same list!
c = a.copy()     # real copy
b.append(4)
print("a:", a, "| c:", c)

# ---- 6. Building a new list while looping ----
numbers = [4, 9, 12, 7, 20]
big = []
for n in numbers:
    if n > 8:
        big.append(n)
print("Numbers above 8:", big)

# ---- 7. Table (list of lists) and unpacking ----
grid = [[1, 2, 3], [4, 5, 6]]
print("Row 2, col 3:", grid[1][2])
first, second, *rest = [10, 20, 30, 40]
print(first, second, rest)
