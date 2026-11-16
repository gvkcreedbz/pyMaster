"""Day 29 - Capstone practice: a sales data pipeline.

Run:  python practice.py          (needs: pandas matplotlib)
Raw input: datasets/sales_messy.csv. Build the pieces top to bottom - each depends on the
ones above. Reuse your Day 26 cleaning code.
"""
import argparse
import logging
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

log = logging.getLogger("sales_pipeline")


# ---------------------------------------------------------------------------
# L1-1 | extract   (Level 1 - Beginner)
# Read the CSV at `path` and return the RAW DataFrame (no cleaning at all).
# ---------------------------------------------------------------------------
def extract(path):
    """Load the raw data."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | quality_report   (Level 1 - Beginner)
# Inspect the RAW DataFrame and return a dict with exactly these keys:
#   "rows"                - number of rows
#   "duplicates"          - number of fully duplicated rows
#   "missing_cells"       - total number of missing cells (all columns)
#   "prices_with_commas"  - how many unit_price values contain a comma (e.g. "1,999")
#   "dirty_text_cells"    - how many region + category values differ from their
#                           .str.strip().str.title() version (messy spacing/case)
# ---------------------------------------------------------------------------
def quality_report(raw):
    """Count the data problems."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | transform   (Level 2 - Intermediate)
# Clean the raw DataFrame (do not change `raw` itself) and add a revenue column:
#   drop duplicates; region & category strip+Title; unit_price -> int (no commas);
#   blank discount_pct -> 0; drop rows with missing quantity and make quantity int;
#   order_date -> datetime; reset_index(drop=True);
#   revenue = quantity * unit_price * (1 - discount_pct / 100)
# ---------------------------------------------------------------------------
def transform(raw):
    """Return the clean table with a revenue column."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | load_to_sqlite   (Level 2 - Intermediate)
# Write the clean DataFrame into table "orders" of the SQLite file db_path (replace the
# table if it exists). Store order_date as text "YYYY-MM-DD". Do not store the index.
# Return the number of rows written.
# ---------------------------------------------------------------------------
def load_to_sqlite(df, db_path):
    """Save df to SQLite."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | kpis   (Level 2 - Intermediate)
# From the clean DataFrame (with revenue) return a dict with exactly:
#   "orders" (int), "total_revenue" (rounded 2), "avg_order_value" (rounded 2),
#   "best_region", "best_category", "best_product" (by total revenue),
#   "best_month" (text "YYYY-MM" with the highest revenue)
# ---------------------------------------------------------------------------
def kpis(df):
    """Headline numbers."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# --- provided helper: draws the chart (no need to change) -------------------
def save_chart(df, path):
    totals = df.groupby("region")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(totals.index, totals.values, color="steelblue")
    ax.set_title("Revenue by region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


# ---------------------------------------------------------------------------
# L3-1 | write_report   (Level 3 - Challenge)
# Write a Markdown file at `path` (UTF-8) that contains:
#   line 1:  "# Sales Report"
#   then one bullet per KPI, exactly like these examples:
#   "- Orders: 294"   "- Total revenue: 1,415,139.55"   "- Average order value: 4,813.40"
#   "- Best region: West"  "- Best category: ..."  "- Best product: ..."  "- Best month: 2026-06"
# Money has thousands separators and 2 decimals.
# ---------------------------------------------------------------------------
def write_report(k, path):
    """Create report.md."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | run_pipeline   (Level 3 - Challenge)
# Wire everything together:
#   * csv_path missing -> raise FileNotFoundError(f"input file not found: {csv_path}")
#   * create out_dir (and parents) if needed
#   * extract -> log the quality report -> transform -> load_to_sqlite(out_dir/"sales.db")
#     -> kpis -> write_report(out_dir/"report.md") -> save_chart(out_dir/"revenue_by_region.png")
#   * log one INFO line per step (log.info(...))   * return the kpis dict
# ---------------------------------------------------------------------------
def run_pipeline(csv_path, out_dir):
    """Run the whole pipeline."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-3 | main   (Level 3 - Challenge)
# A command-line front door using argparse:  --input (required)  --out (default "output").
# Call run_pipeline; return 0 on success. If the input file is missing print
# "Error: <message>" and return 1.  main(argv) must accept a list of arguments (or None).
# ---------------------------------------------------------------------------
def main(argv=None):
    """CLI entry point."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ======================= AUTO-CHECKER (do not edit below) ====================
import tempfile

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
KPIS = {"orders": 294, "total_revenue": 1415139.55, "avg_order_value": 4813.4, "best_region": "West",
        "best_category": "Electronics", "best_product": "Smartwatch", "best_month": "2026-06"}


def _clean():
    return transform(extract(MESSY))


def _transform_checks():
    raw = extract(MESSY)
    before = raw.shape
    out = transform(raw)
    return (raw.shape == before, len(out), out.isna().sum().sum().item(), sorted(out["region"].unique()),
            str(out["order_date"].dtype).startswith("datetime64"), str(out["quantity"].dtype), str(out["unit_price"].dtype),
            round(float(out["revenue"].sum()), 2))


def _load_check():
    db = Path(tempfile.mkdtemp()) / "t.db"
    clean = _clean()
    written = load_to_sqlite(clean, db)
    conn = sqlite3.connect(db)
    try:
        count, total, sample = conn.execute("SELECT COUNT(*), ROUND(SUM(revenue), 2), MIN(order_date) FROM orders").fetchone()
        columns = [row[1] for row in conn.execute("PRAGMA table_info(orders)")]
    finally:
        conn.close()
    return (written, count, total, sample, "index" in columns)


def _report_check():
    path = Path(tempfile.mkdtemp()) / "r.md"
    write_report(KPIS, path)
    lines = path.read_text(encoding="utf-8").splitlines()
    return (lines[0], "- Orders: 294" in lines, "- Total revenue: 1,415,139.55" in lines, "- Average order value: 4,813.40" in lines,
            "- Best region: West" in lines, "- Best category: Electronics" in lines, "- Best product: Smartwatch" in lines,
            "- Best month: 2026-06" in lines)


def _pipeline_check():
    out = Path(tempfile.mkdtemp()) / "deep" / "results"
    result = run_pipeline(MESSY, out)
    files = sorted(p.name for p in out.iterdir())
    return (result, files, MESSY.read_bytes()[:7])


def _missing_input_check():
    try:
        run_pipeline(MESSY.parent / "nope.csv", Path(tempfile.mkdtemp()))
    except FileNotFoundError as e:
        return str(e).startswith("input file not found:")
    return False


def _main_check():
    out = Path(tempfile.mkdtemp()) / "cli"
    ok = main(["--input", str(MESSY), "--out", str(out)])
    bad = main(["--input", str(MESSY.parent / "nope.csv"), "--out", str(out)])
    return (ok, bad, (out / "report.md").exists())


print("--- Day 29 checks ---")
check("L1-1 extract is RAW (308 x 9)", lambda: extract(MESSY).shape, (308, 9))
check("L1-2 quality_report", lambda: quality_report(extract(MESSY)),
      {"rows": 308, "duplicates": 8, "missing_cells": 16, "prices_with_commas": 7, "dirty_text_cells": 51})
check("L2-1 transform", _transform_checks,
      (True, 294, 0, ["East", "North", "South", "West"], True, "int64", "int64", 1415139.55))
check("L2-2 load_to_sqlite", _load_check, (294, 294, 1415139.55, "2026-01-02", False))
check("L2-3 kpis", lambda: kpis(_clean()), KPIS)
check("L3-1 write_report", _report_check, ("# Sales Report", True, True, True, True, True, True, True))
check("L3-2 run_pipeline creates files and returns kpis", lambda: _pipeline_check()[:2],
      (KPIS, ["report.md", "revenue_by_region.png", "sales.db"]))
check("L3-2 run_pipeline raises FileNotFoundError", _missing_input_check, True)
check("L3-3 main returns 0 / 1 and writes output", _main_check, (0, 1, True))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
