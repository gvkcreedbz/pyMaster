# SOLUTION FILE - try the hint ladder first!
"""Day 26 - Practice: cleaning, groupby, merge, pivot and charts.

Run:  python practice.py          (needs: python -m pip install pandas matplotlib)
Data: datasets/sales_messy.csv - blanks, duplicates, ' SOUTH ' style text, '1,999' prices.
"""
import matplotlib

matplotlib.use("Agg")  # draw to files, no window
import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------------------
# L1-1 | strip_and_title   (Level 1 - Beginner)
# Take a pandas Series of text, return it stripped of spaces around and in Title Case.
#   " sOUTH " -> "South"
# ---------------------------------------------------------------------------
def strip_and_title(series):
    """Clean a text column."""
    # >>> SOLUTION
    return series.str.strip().str.title()
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | count_missing   (Level 1 - Beginner)
# Return a dict {column: number of missing values} containing ONLY columns that
# have at least one missing value.
# ---------------------------------------------------------------------------
def count_missing(df):
    """Missing values per column (only if > 0)."""
    # >>> SOLUTION
    missing = df.isna().sum()
    return {col: int(n) for col, n in missing.items() if n > 0}
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | drop_dupes   (Level 1 - Beginner)
# Return the DataFrame without fully duplicated rows (keep the first copy).
# ---------------------------------------------------------------------------
def drop_dupes(df):
    """Remove duplicate rows."""
    # >>> SOLUTION
    return df.drop_duplicates()
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | fix_price   (Level 2 - Intermediate)
# A Series of prices written as text, some with thousands commas ("1,999", "499").
# Return a Series of integers.
# ---------------------------------------------------------------------------
def fix_price(series):
    """'1,999' -> 1999."""
    # >>> SOLUTION
    return series.astype(str).str.replace(",", "").astype(int)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | clean_sales   (Level 2 - Intermediate)
# Full pipeline on the raw messy DataFrame; return the clean DataFrame:
#   1. drop duplicate rows            4. blank discount_pct -> 0
#   2. region & category: strip+Title 5. drop rows where quantity is missing, then make quantity int
#   3. unit_price -> int (no commas)  6. order_date -> real dates;  reset_index(drop=True)
# You may reuse the functions you wrote above.
# ---------------------------------------------------------------------------
def clean_sales(raw):
    """Return the cleaned sales table."""
    # >>> SOLUTION
    df = drop_dupes(raw).copy()
    df["region"] = strip_and_title(df["region"])
    df["category"] = strip_and_title(df["category"])
    df["unit_price"] = fix_price(df["unit_price"])
    df["discount_pct"] = df["discount_pct"].fillna(0)
    df = df.dropna(subset=["quantity"]).copy()
    df["quantity"] = df["quantity"].astype(int)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df.reset_index(drop=True)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | summary_by_category   (Level 2 - Intermediate)
# df (clean) -> add revenue = quantity*unit_price*(1-discount_pct/100) internally, then
# return {category: {"orders": number of rows, "revenue": total rounded to 2}}.
# Use groupby + agg with named aggregation.
# ---------------------------------------------------------------------------
def summary_by_category(df):
    """Orders and revenue per category."""
    # >>> SOLUTION
    d = df.copy()
    d["revenue"] = d["quantity"] * d["unit_price"] * (1 - d["discount_pct"] / 100)
    summary = d.groupby("category").agg(orders=("order_id", "count"), revenue=("revenue", "sum")).round(2)
    return summary.to_dict("index")
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | region_vs_target   (Level 3 - Challenge)
# sales has columns region, revenue (many rows); targets has columns region, target.
# Return {region: achieved percent} = total revenue / target * 100, rounded to 1 decimal.
# Use groupby then merge. Regions without a target are left out.
# ---------------------------------------------------------------------------
def region_vs_target(sales, targets):
    """Achievement percentage per region."""
    # >>> SOLUTION
    totals = sales.groupby("region")["revenue"].sum().reset_index()
    combined = totals.merge(targets, on="region", how="inner")
    combined["pct"] = (combined["revenue"] / combined["target"] * 100).round(1)
    return dict(zip(combined["region"], combined["pct"]))
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | save_revenue_chart   (Level 3 - Challenge)
# df has region + revenue. Draw a BAR chart of total revenue per region with a title,
# x label and y label, save it as a PNG at `path`, then close the figure.
# ---------------------------------------------------------------------------
def save_revenue_chart(df, path):
    """Write a bar chart PNG."""
    # >>> SOLUTION
    totals = df.groupby("region")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(totals.index, totals.values, color="steelblue")
    ax.set_title("Revenue by region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-3 | pivot_region_category   (Level 3 - Challenge)
# df has region, category, revenue. Return a dict of dicts {region: {category: total}}
# (rows = region, columns = category, missing combinations = 0, rounded to 2 decimals)
# using pivot_table.
# ---------------------------------------------------------------------------
def pivot_region_category(df):
    """Region x category revenue table as a dict."""
    # >>> SOLUTION
    table = df.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0)
    return table.round(2).to_dict("index")
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
import os
import tempfile
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


MESSY = _datasets() / "sales_messy.csv"


def _raw():
    return pd.read_csv(MESSY)


def _revenue(d):
    d = d.copy()
    d["revenue"] = d["quantity"] * d["unit_price"] * (1 - d["discount_pct"] / 100)
    return d


def _clean_checks():
    out = clean_sales(_raw())
    return (len(out), int(out.isna().sum().sum()), sorted(out["region"].unique()), sorted(out["category"].unique()),
            str(out["order_date"].dtype).startswith("datetime64"), str(out["quantity"].dtype),
            round(float(_revenue(out)["revenue"].sum()), 2), int(out.index[-1]))


def _chart_check():
    path = os.path.join(tempfile.mkdtemp(), "chart.png")
    save_revenue_chart(_revenue(clean_sales(_raw())), path)
    with open(path, "rb") as f:
        head = f.read(8)
    return (head == b"\x89PNG\r\n\x1a\n", os.path.getsize(path) > 2000)


print("--- Day 26 checks ---")
check("L1-1 strip_and_title", lambda: strip_and_title(pd.Series([" sOUTH ", "east", "GROCERY "])).tolist(), ["South", "East", "Grocery"])
check("L1-2 count_missing", lambda: count_missing(_raw()), {"quantity": 6, "discount_pct": 10})
check("L1-3 drop_dupes", lambda: (len(drop_dupes(_raw())), len(_raw())), (300, 308))
check("L2-1 fix_price", lambda: fix_price(pd.Series(["1,999", "499", "12,500"])).tolist(), [1999, 499, 12500])
check("L2-2 clean_sales", _clean_checks,
      (294, 0, ["East", "North", "South", "West"], ["Electronics", "Fashion", "Grocery", "Home"], True, "int64", 1415139.55, 293))
check("L2-3 summary_by_category", lambda: summary_by_category(clean_sales(_raw())), {
    "Electronics": {"orders": 70, "revenue": 500410.1}, "Fashion": {"orders": 91, "revenue": 451201.35},
    "Grocery": {"orders": 60, "revenue": 99976.5}, "Home": {"orders": 73, "revenue": 363551.6}})
_sales = pd.DataFrame({"region": ["East", "East", "West", "North"], "revenue": [100.0, 200.0, 450.0, 10.0]})
_targets = pd.DataFrame({"region": ["East", "West", "South"], "target": [400.0, 500.0, 100.0]})
check("L3-1 region_vs_target", lambda: region_vs_target(_sales, _targets), {"East": 75.0, "West": 90.0})
check("L3-2 save_revenue_chart writes a real PNG", _chart_check, (True, True))
check("L3-3 pivot_region_category", lambda: pivot_region_category(_revenue(clean_sales(_raw()))), {
    "East": {"Electronics": 74893.55, "Fashion": 149298.75, "Grocery": 34188.85, "Home": 65437.55},
    "North": {"Electronics": 74914.05, "Fashion": 117493.85, "Grocery": 22758.8, "Home": 74782.55},
    "South": {"Electronics": 172516.25, "Fashion": 64119.45, "Grocery": 25484.05, "Home": 87479.45},
    "West": {"Electronics": 178086.25, "Fashion": 120289.3, "Grocery": 17544.8, "Home": 135852.05}})
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
