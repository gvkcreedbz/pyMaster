"""Day 25 - Code along: NumPy and pandas on the real sales file."""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "datasets" / "sales.csv"

# ================= NumPy =================
print("=== NumPy ===")
temps_c = np.array([22.5, 30.1, 18.0, 35.2])
temps_f = temps_c * 9 / 5 + 32
print("Fahrenheit:", temps_f)
print("mean/max/std:", temps_c.mean().round(2), temps_c.max(), temps_c.std().round(2))
print("hot days (>25):", temps_c[temps_c > 25])
print("list * 2 :", [1, 2, 3] * 2, "| array * 2 :", np.array([1, 2, 3]) * 2)

grid = np.array([[1, 2, 3], [4, 5, 6]])
print("shape:", grid.shape, "| column sums:", grid.sum(axis=0), "| row sums:", grid.sum(axis=1))
print("second column:", grid[:, 1], "| broadcasting:", (grid + np.array([10, 20, 30])).tolist())
print("arange / linspace:", np.arange(0, 10, 2), np.linspace(0, 1, 5))

# ================= pandas =================
print("\n=== pandas ===")
df = pd.read_csv(DATA, parse_dates=["order_date"])
print("shape:", df.shape)
print(df.head(3).to_string())
print(df.dtypes.to_string())
print(df[["quantity", "unit_price", "discount_pct"]].describe().round(1).to_string())

# selecting
print("\nfirst product:", df.loc[0, "product"], "| first row by position:", df.iloc[0]["order_id"])

# filtering
west_big = df[(df["region"] == "West") & (df["quantity"] >= 5)]
print("West orders with qty >= 5:", len(west_big))
print("UPI or Card payments:", df["payment_method"].isin(["UPI", "Card"]).sum())

# new columns
df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
print("Total revenue:", round(df["revenue"].sum(), 2))
print("Average order value:", round(df["revenue"].mean(), 2))
print(df.sort_values("revenue", ascending=False)[["order_id", "product", "revenue"]].head(3).to_string(index=False))
print(df["region"].value_counts().to_string())
print("Orders per month number:", df["order_date"].dt.month.value_counts().sort_index().to_dict())
