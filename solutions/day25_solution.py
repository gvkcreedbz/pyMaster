# SOLUTION FILE - try the hint ladder first!
"""Day 25 - Practice: NumPy and pandas basics.

Run:  python practice.py          (needs: python -m pip install numpy pandas)
Data: datasets/sales.csv  (order_id, order_date, region, category, product,
                           quantity, unit_price, discount_pct, payment_method)
Rule of the day: NO for-loops over rows - use array/column maths and masks.
"""
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# L1-1 | celsius_to_fahrenheit   (Level 1 - Beginner)
# Take a list of Celsius temperatures, return a NumPy array of Fahrenheit (F = C*9/5+32).
#   celsius_to_fahrenheit([0, 100]) -> array([32., 212.])
# ---------------------------------------------------------------------------
def celsius_to_fahrenheit(temps_c):
    """Vectorised conversion - no loop."""
    # >>> SOLUTION
    return np.array(temps_c) * 9 / 5 + 32
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | above_average   (Level 1 - Beginner)
# Return a NumPy array of the values that are strictly greater than the mean.
#   above_average([1, 2, 3, 10]) -> array([10])      (mean is 4)
# ---------------------------------------------------------------------------
def above_average(values):
    """Use a boolean mask."""
    # >>> SOLUTION
    arr = np.array(values)
    return arr[arr > arr.mean()]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | load_sales   (Level 1 - Beginner)
# Read the CSV at `path` into a DataFrame, converting the order_date column to real dates.
# ---------------------------------------------------------------------------
def load_sales(path):
    """Return the sales DataFrame."""
    # >>> SOLUTION
    return pd.read_csv(path, parse_dates=["order_date"])
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | add_revenue   (Level 2 - Intermediate)
# Return a COPY of df with a new column "revenue" = quantity * unit_price * (1 - discount_pct/100).
# Do not modify the original DataFrame.
# ---------------------------------------------------------------------------
def add_revenue(df):
    """Return df plus a revenue column."""
    # >>> SOLUTION
    result = df.copy()
    result["revenue"] = result["quantity"] * result["unit_price"] * (1 - result["discount_pct"] / 100)
    return result
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | top_products   (Level 2 - Intermediate)
# df has a "revenue" column. Return a LIST with the names of the n products with the
# highest TOTAL revenue, best first.
# ---------------------------------------------------------------------------
def top_products(df, n=3):
    """Best-selling products by total revenue."""
    # >>> SOLUTION
    totals = df.groupby("product")["revenue"].sum()
    return list(totals.nlargest(n).index)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | filter_orders   (Level 2 - Intermediate)
# Return the rows for the given region whose quantity is at least min_quantity.
# ---------------------------------------------------------------------------
def filter_orders(df, region, min_quantity):
    """Boolean-mask filter with & and brackets."""
    # >>> SOLUTION
    return df[(df["region"] == region) & (df["quantity"] >= min_quantity)]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | revenue_by_region   (Level 3 - Challenge)
# df has "revenue". Return a plain dict {region: total revenue rounded to 2 decimals}.
# ---------------------------------------------------------------------------
def revenue_by_region(df):
    """Total revenue per region."""
    # >>> SOLUTION
    return df.groupby("region")["revenue"].sum().round(2).to_dict()
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | monthly_revenue   (Level 3 - Challenge)
# Return {"2026-01": total, ...}: revenue per calendar month (keys "YYYY-MM", values
# rounded to 2 decimals). order_date must already be a datetime column.
# ---------------------------------------------------------------------------
def monthly_revenue(df):
    """Revenue per month."""
    # >>> SOLUTION
    month = df["order_date"].dt.to_period("M").astype(str)
    return df.groupby(month)["revenue"].sum().round(2).to_dict()
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
from pathlib import Path

_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


def _datasets():
    for parent in Path(__file__).resolve().parents:
        if (parent / "datasets").is_dir():
            return parent / "datasets"


SALES = _datasets() / "sales.csv"


def _fresh():
    return pd.read_csv(SALES, parse_dates=["order_date"])


def _with_revenue():
    d = _fresh()
    d["revenue"] = d["quantity"] * d["unit_price"] * (1 - d["discount_pct"] / 100)
    return d


def _add_revenue_checks():
    d = _fresh()
    before = list(d.columns)
    out = add_revenue(d)
    return (round(float(out["revenue"].sum()), 2), list(d.columns) == before, len(out))


print("--- Day 25 checks ---")
check("L1-1 celsius_to_fahrenheit", lambda: (celsius_to_fahrenheit([0, 100, -40]).tolist(), type(celsius_to_fahrenheit([0])).__name__),
      ([32.0, 212.0, -40.0], "ndarray"))
check("L1-2 above_average", lambda: (above_average([1, 2, 3, 10]).tolist(), above_average([5, 5, 5]).tolist()), ([10], []))
check("L1-3 load_sales shape + date dtype", lambda: (load_sales(SALES).shape, str(load_sales(SALES)["order_date"].dtype).startswith("datetime64")),
      ((300, 9), True))
check("L2-1 add_revenue (total, original untouched, rows)", _add_revenue_checks, (1443241.55, True, 300))
check("L2-2 top_products", lambda: top_products(_with_revenue(), 3), ["Smartwatch", "Air Fryer", "Running Shoes"])
check("L2-3 filter_orders count", lambda: len(filter_orders(_fresh(), "West", 5)), 19)
check("L2-3 filter_orders only matching rows", lambda: (set(filter_orders(_fresh(), "West", 5)["region"]), int(filter_orders(_fresh(), "West", 5)["quantity"].min()) >= 5),
      ({"West"}, True))
check("L3-1 revenue_by_region", lambda: revenue_by_region(_with_revenue()),
      {"East": 335268.6, "North": 300446.25, "South": 348849.7, "West": 458677.0})
check("L3-2 monthly_revenue", lambda: monthly_revenue(_with_revenue()), {
    "2026-01": 102041.05, "2026-02": 128597.5, "2026-03": 174010.9, "2026-04": 183688.4, "2026-05": 174384.85,
    "2026-06": 198503.1, "2026-07": 82858.25, "2026-08": 135710.75, "2026-09": 125223.0, "2026-10": 138223.75})
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
