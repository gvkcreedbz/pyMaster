# SOLUTION FILE - try the hint ladder first!
"""Day 16 - Practice: CSV and JSON files.

Run:  python practice.py
Sales file columns: order_id, order_date, region, category, product, quantity,
unit_price, discount_pct, payment_method.
revenue of a row = quantity * unit_price * (1 - discount_pct / 100)
"""
import csv
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# L1-1 | read_csv_rows   (Level 1 - Beginner)
# Return the CSV file as a list of dicts (one per data row, keys from the header).
# All values stay as text.
# ---------------------------------------------------------------------------
def read_csv_rows(path):
    """Return a list of row dicts."""
    # >>> SOLUTION
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | total_revenue   (Level 1 - Beginner)
# Total revenue of a sales CSV, rounded to 2 decimals.
# ---------------------------------------------------------------------------
def total_revenue(path):
    """Return the total revenue of the sales file."""
    # >>> SOLUTION
    total = 0
    for r in read_csv_rows(path):
        total += int(r["quantity"]) * int(r["unit_price"]) * (1 - int(r["discount_pct"]) / 100)
    return round(total, 2)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | JSON save and load   (Level 1 - Beginner)
# save_json(path, data): write data as pretty JSON (indent=2, ensure_ascii=False).
# load_json(path, default=None): return the data; return `default` if the file
# does not exist.
# ---------------------------------------------------------------------------
def save_json(path, data):
    """Write data to a JSON file."""
    # >>> SOLUTION
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # <<< SOLUTION


def load_json(path, default=None):
    """Read a JSON file (or return default when missing)."""
    # >>> SOLUTION
    if not Path(path).exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | revenue_by_region   (Level 2 - Intermediate)
# Return {region: revenue rounded to 2 decimals} for a sales CSV.
# ---------------------------------------------------------------------------
def revenue_by_region(path):
    """Return revenue per region."""
    # >>> SOLUTION
    totals = {}
    for r in read_csv_rows(path):
        value = int(r["quantity"]) * int(r["unit_price"]) * (1 - int(r["discount_pct"]) / 100)
        totals[r["region"]] = totals.get(r["region"], 0) + value
    return {region: round(v, 2) for region, v in totals.items()}
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | write_csv   (Level 2 - Intermediate)
# Write a list of dicts to a CSV file with a header row using `fieldnames` order.
# ---------------------------------------------------------------------------
def write_csv(path, rows, fieldnames):
    """Write rows (list of dicts) to a CSV file."""
    # >>> SOLUTION
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | top_students   (Level 2 - Intermediate)
# students.csv has name, class, math, science, english, attendance_pct.
# Return the n best students as a list of (name, average) tuples, average of the
# three subjects rounded to 2 decimals, best first; equal averages -> name A-Z.
# ---------------------------------------------------------------------------
def top_students(path, n):
    """Return the top n (name, average) tuples."""
    # >>> SOLUTION
    scored = []
    for s in read_csv_rows(path):
        avg = round((int(s["math"]) + int(s["science"]) + int(s["english"])) / 3, 2)
        scored.append((s["name"], avg))
    scored.sort(key=lambda t: (-t[1], t[0]))
    return scored[:n]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | monthly_report   (Level 3 - Challenge)
# From a sales CSV write a NEW CSV at out_path with the header  month,orders,revenue
# - one row per month ("2026-01"), sorted by month, orders = number of rows,
#   revenue rounded to 2 decimals. Return the number of months written.
# ---------------------------------------------------------------------------
def monthly_report(sales_path, out_path):
    """Write the monthly summary CSV; return the month count."""
    # >>> SOLUTION
    months = {}
    for r in read_csv_rows(sales_path):
        month = r["order_date"][:7]
        value = int(r["quantity"]) * int(r["unit_price"]) * (1 - int(r["discount_pct"]) / 100)
        info = months.setdefault(month, {"month": month, "orders": 0, "revenue": 0})
        info["orders"] += 1
        info["revenue"] += value
    rows = []
    for month in sorted(months):
        info = months[month]
        rows.append({"month": month, "orders": info["orders"], "revenue": round(info["revenue"], 2)})
    write_csv(out_path, rows, ["month", "orders", "revenue"])
    return len(rows)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | merge_json_configs   (Level 3 - Challenge)
# default_path holds default settings; user_path holds the user's overrides (the
# user file may NOT exist). Return the defaults updated by the user values. Nested
# dicts are merged key by key (deep merge); everything else is replaced.
#   defaults {"ui": {"theme": "light", "size": 12}, "lang": "en"}
#   user     {"ui": {"theme": "dark"}}  ->  {"ui": {"theme": "dark", "size": 12}, "lang": "en"}
# ---------------------------------------------------------------------------
def merge_json_configs(default_path, user_path):
    """Return defaults deep-merged with user overrides."""
    # >>> SOLUTION
    def merge(base, override):
        result = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = merge(result[key], value)
            else:
                result[key] = value
        return result

    defaults = load_json(default_path, {})
    user = load_json(user_path, {})
    return merge(defaults, user)
    # <<< SOLUTION


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


SMALL_SALES = (
    "order_id,order_date,region,category,product,quantity,unit_price,discount_pct,payment_method\n"
    "O1,2026-01-05,North,Home,Lamp,2,500,10,UPI\n"
    "O2,2026-01-20,South,Home,Lamp,1,500,0,Card\n"
    "O3,2026-02-02,North,Fashion,Kurta,3,900,5,UPI\n"
)

print("--- Day 16 checks ---")
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    small = tmp / "small.csv"
    small.write_text(SMALL_SALES, encoding="utf-8")
    sales = _datasets() / "sales.csv"
    check("L1-1 read_csv_rows", lambda: (len(read_csv_rows(small)), read_csv_rows(small)[0]["region"], read_csv_rows(small)[0]["quantity"]),
          (3, "North", "2"))
    check("L1-2 total_revenue small", lambda: total_revenue(small), 900 + 500 + 2565.0 + 0.0)
    check("L1-2 total_revenue real file", lambda: total_revenue(sales), 1443241.55)
    jp = tmp / "cfg.json"
    save_json(jp, {"symbol": "₹", "n": [1, 2]})
    check("L1-3 save_json + load_json", lambda: load_json(jp), {"symbol": "₹", "n": [1, 2]})
    check("L1-3 save_json is pretty UTF-8", lambda: jp.read_text(encoding="utf-8").startswith('{\n  "symbol": "₹"'), True)
    check("L1-3 load_json default", lambda: load_json(tmp / "missing.json", {"x": 1}), {"x": 1})
    check("L2-1 revenue_by_region small", lambda: revenue_by_region(small), {"North": 3465.0, "South": 500.0})
    check("L2-1 revenue_by_region real", lambda: revenue_by_region(sales),
          {"East": 335268.6, "North": 300446.25, "South": 348849.7, "West": 458677.0})
    out = tmp / "out.csv"
    write_csv(out, [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}], ["a", "b"])
    check("L2-2 write_csv", lambda: out.read_text(encoding="utf-8").replace("\r\n", "\n"), "a,b\n1,x\n2,y\n")
    check("L2-3 top_students", lambda: top_students(_datasets() / "students.csv", 3),
          [("Chirag", 93.67), ("Neel", 86.0), ("Gauri", 84.33)])
    rep = tmp / "monthly.csv"
    check("L3-1 monthly_report months", lambda: monthly_report(small, rep), 2)
    check("L3-1 monthly_report content", lambda: rep.read_text(encoding="utf-8").replace("\r\n", "\n"),
          "month,orders,revenue\n2026-01,2,1400.0\n2026-02,1,2565.0\n")
    check("L3-1 monthly_report real file", lambda: monthly_report(sales, tmp / "real_monthly.csv"), 10)
    d, u = tmp / "defaults.json", tmp / "user.json"
    save_json(d, {"ui": {"theme": "light", "size": 12}, "lang": "en"})
    check("L3-2 merge without user file", lambda: merge_json_configs(d, u), {"ui": {"theme": "light", "size": 12}, "lang": "en"})
    save_json(u, {"ui": {"theme": "dark"}, "extra": True})
    check("L3-2 deep merge", lambda: merge_json_configs(d, u), {"ui": {"theme": "dark", "size": 12}, "lang": "en", "extra": True})
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
