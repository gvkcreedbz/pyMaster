"""Day 26 - Code along: clean a messy export, summarise it, draw charts."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                      # draw to files (no window needed)
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# ---- 1. Inspect ----
df = pd.read_csv(ROOT / "datasets" / "sales_messy.csv")
print("raw shape:", df.shape, "| duplicates:", df.duplicated().sum())
print("missing:", df.isna().sum()[df.isna().sum() > 0].to_dict())
print("regions:", sorted(df["region"].unique()))

# ---- 2. Clean (one step per line) ----
df = df.drop_duplicates()
df["region"] = df["region"].str.strip().str.title()
df["category"] = df["category"].str.strip().str.title()
df["unit_price"] = df["unit_price"].astype(str).str.replace(",", "").astype(int)
df["discount_pct"] = df["discount_pct"].fillna(0)
df = df.dropna(subset=["quantity"]).copy()
df["quantity"] = df["quantity"].astype(int)
df["order_date"] = pd.to_datetime(df["order_date"])
df = df.reset_index(drop=True)
df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
print("\nclean shape:", df.shape, "| missing:", int(df.isna().sum().sum()), "| revenue:", round(df["revenue"].sum(), 2))

# ---- 3. groupby / agg / pivot ----
summary = df.groupby("category").agg(orders=("order_id", "count"), revenue=("revenue", "sum")).round(2)
print("\n", summary.to_string())
pivot = df.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0).round(0)
print("\n", pivot.to_string())

# ---- 4. merge with targets ----
by_region = df.groupby("region")["revenue"].sum().reset_index()
targets = pd.DataFrame({"region": ["East", "North", "South", "West"], "target": [300000, 300000, 350000, 450000]})
combined = by_region.merge(targets, on="region", how="left")
combined["achieved_pct"] = (combined["revenue"] / combined["target"] * 100).round(1)
print("\n", combined.to_string(index=False))

# ---- 5. Charts ----
fig, ax = plt.subplots(figsize=(7, 4))
by_region.set_index("region")["revenue"].plot(kind="bar", ax=ax, color="steelblue")
ax.set_title("Revenue by region (2026)")
ax.set_xlabel("Region")
ax.set_ylabel("Revenue")
fig.tight_layout()
fig.savefig(OUT / "revenue_by_region.png", dpi=120)
plt.close(fig)

monthly = df.groupby(df["order_date"].dt.to_period("M").astype(str))["revenue"].sum()
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(monthly.index, monthly.values, marker="o", color="darkorange")
ax.set_title("Monthly revenue trend")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue")
ax.tick_params(axis="x", rotation=45)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "monthly_revenue.png", dpi=120)
plt.close(fig)
print("\nCharts saved in:", OUT)
