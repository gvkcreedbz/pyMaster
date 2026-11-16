"""Day 16 - Code along: sales report from datasets/sales.csv."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# ---- 1. Read the CSV into a list of dicts ----
with open(ROOT / "datasets" / "sales.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
print(len(rows), "orders; first row:", rows[0])


def revenue(row):
    """Everything in a CSV is text, so convert before doing maths."""
    return int(row["quantity"]) * int(row["unit_price"]) * (1 - int(row["discount_pct"]) / 100)


# ---- 2. Totals ----
print(f"Total revenue: Rs. {sum(revenue(r) for r in rows):,.2f}")

by_region = {}
by_category = {}
for r in rows:
    by_region[r["region"]] = by_region.get(r["region"], 0) + revenue(r)
    by_category[r["category"]] = by_category.get(r["category"], 0) + revenue(r)
for region in sorted(by_region, key=by_region.get, reverse=True):
    print(f"  {region:<6} Rs. {by_region[region]:>12,.2f}")
print("Best category:", max(by_category, key=by_category.get))

# ---- 3. Write a new CSV (the 'Load' of ETL) ----
report_rows = [{"region": k, "revenue": round(v, 2)} for k, v in sorted(by_region.items())]
with open(OUT / "region_report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["region", "revenue"])
    writer.writeheader()
    writer.writerows(report_rows)
print("Wrote", OUT / "region_report.csv")

# ---- 4. JSON settings file ----
settings = {"currency": "INR", "symbol": "₹", "limits": {"daily": 20000, "per_txn": 5000}}
with open(OUT / "settings.json", "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
with open(OUT / "settings.json", encoding="utf-8") as f:
    print(json.load(f))

# ---- 5. Students: averages from another CSV ----
with open(ROOT / "datasets" / "students.csv", newline="", encoding="utf-8") as f:
    students = list(csv.DictReader(f))
for s in students[:3]:
    avg = (int(s["math"]) + int(s["science"]) + int(s["english"])) / 3
    print(f"{s['name']:<8} average {avg:.1f}")
