"""Day 10 - Code along: contact book, inventory and word counts."""

# ---- 1. A record: user profile ----
user = {"name": "Aarav", "age": 25, "city": "Pune"}
print(user["name"], "|", user.get("email"), "|", user.get("email", "n/a"))
user["email"] = "aarav@example.com"
user.update({"city": "Delhi", "vip": True})
print(user)
print("vip" in user, "salary" in user)

# ---- 2. Looping ----
for key, value in user.items():
    print(f"  {key:<6} -> {value}")

# ---- 3. Inventory (nested dict) ----
inventory = {
    "pen": {"price": 10, "stock": 50},
    "notebook": {"price": 120, "stock": 5},
}
inventory["notebook"]["stock"] -= 1
worth = 0
for item, info in inventory.items():
    worth += info["price"] * info["stock"]
print("Stock worth Rs.", worth)

# ---- 4. Counting pattern: word frequency ----
text = "to be or not to be that is the question"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)
by_count = sorted(sorted(counts), key=counts.get, reverse=True)
print("Most common:", by_count[:3])

# ---- 5. Grouping pattern ----
groups = {}
for word in ["apple", "avocado", "banana", "blueberry", "cherry"]:
    groups.setdefault(word[0], []).append(word)
print(groups)

# ---- 6. Cart price lookup with a menu ----
menu = {"chai": 20, "samosa": 15, "vada pav": 25}
order = ["chai", "samosa", "samosa", "pizza"]
bill = 0
for item in order:
    price = menu.get(item)
    if price is None:
        print(f"Sorry, {item} is not on the menu")
    else:
        bill += price
print("Bill:", bill)
