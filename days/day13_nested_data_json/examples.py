"""Day 13 - Code along: a restaurant API response."""
import copy
import json

# This is what an API might send back (already converted to Python data).
restaurants = [
    {"name": "Spice Hub", "city": "Delhi", "rating": 4.5, "cuisines": ["North Indian", "Chinese"], "avg_cost": 600},
    {"name": "Dosa Corner", "city": "Pune", "rating": 4.2, "cuisines": ["South Indian"], "avg_cost": 250},
    {"name": "Pasta Palace", "city": "Delhi", "rating": 4.0, "cuisines": ["Italian"], "avg_cost": 800},
    {"name": "Biryani Bay", "city": "Pune", "rating": 4.7, "cuisines": ["Mughlai", "North Indian"], "avg_cost": 500},
]

# ---- 1. Navigate: list -> dict -> list ----
print(restaurants[0]["cuisines"][1])

# ---- 2. Filter / summarise ----
delhi = [r["name"] for r in restaurants if r["city"] == "Delhi"]
avg_rating = sum(r["rating"] for r in restaurants) / len(restaurants)
best = max(restaurants, key=lambda r: r["rating"])
print("Delhi:", delhi, "| avg rating:", round(avg_rating, 2), "| best:", best["name"])

# ---- 3. Group by city ----
by_city = {}
for r in restaurants:
    by_city.setdefault(r["city"], []).append(r["name"])
print(by_city)

# ---- 4. JSON round-trip ----
text = json.dumps(restaurants[1], indent=2)
print(text)
back = json.loads(text)
print(back == restaurants[1])

incoming = '{"order_id": 77, "paid": true, "coupon": null, "items": [{"name": "Dosa", "price": 90, "qty": 2}]}'
order = json.loads(incoming)
print(order["paid"], order["coupon"], sum(i["price"] * i["qty"] for i in order["items"]))

# ---- 5. Safe deep access ----
profile = {"customer": {"address": {"city": "Pune"}}}
print(profile.get("customer", {}).get("address", {}).get("pin", "unknown"))

# ---- 6. Shallow vs deep copy ----
a = {"tags": ["x"]}
shallow = a.copy()
deep = copy.deepcopy(a)
a["tags"].append("y")
print("shallow sees the change:", shallow["tags"], "| deep does not:", deep["tags"])
