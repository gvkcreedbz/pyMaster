"""Day 14 - Code along: how the tracker's data flows (no input needed)."""

expenses = [
    {"date": "2026-11-02", "category": "Food", "amount": 250.0, "note": "Lunch"},
    {"date": "2026-11-03", "category": "Travel", "amount": 120.5, "note": "Metro"},
    {"date": "2026-11-09", "category": "Food", "amount": 480.0, "note": "Dinner out"},
    {"date": "2026-12-01", "category": "Fun", "amount": 799.0, "note": "Movie + snacks"},
]

# ---- total and totals per category (the counting pattern again) ----
total = sum(e["amount"] for e in expenses)
print(f"Total: Rs. {total:,.2f}")

by_category = {}
for e in expenses:
    by_category[e["category"]] = by_category.get(e["category"], 0) + e["amount"]
print(by_category)

# ---- totals per month (slice the date text) ----
by_month = {}
for e in expenses:
    month = e["date"][:7]                    # "2026-11"
    by_month[month] = by_month.get(month, 0) + e["amount"]
print(by_month)

# ---- aligned printing with f-string formatting ----
for e in expenses:
    print(f"{e['date']} | {e['category']:<10} | Rs. {e['amount']:>9,.2f} | {e['note']}")

# ---- budget check ----
budgets = {"Food": 1000, "Travel": 500}
for category, limit in budgets.items():
    spent = by_category.get(category, 0)
    percent = spent / limit * 100
    status = "OVER" if spent > limit else "WARN" if percent >= 80 else "OK"
    print(f"{category}: {spent:.2f} / {limit:.2f} ({percent:.1f}%) {status}")
