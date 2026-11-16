# SOLUTION FILE - try the hint ladder first!
"""Day 28 - Practice: SQLite and SQL.

Run:  python practice.py
Every function receives an open sqlite3 connection `conn`. The table is:
  orders(order_id, order_date, region, category, product, quantity, unit_price, discount_pct, payment_method)
Revenue = quantity * unit_price * (1 - discount_pct / 100.0)
Use ? placeholders for any value that comes from a parameter - never f-strings.
"""
import sqlite3  # noqa: F401  (used by the checker below)


# ---------------------------------------------------------------------------
# L1-1 | count_orders   (Level 1 - Beginner)
# Return the number of rows in orders (an int).
# ---------------------------------------------------------------------------
def count_orders(conn):
    """Number of orders."""
    # >>> SOLUTION
    return conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | orders_in_region   (Level 1 - Beginner)
# Return a LIST of order_id strings for the region, sorted ascending. Use a placeholder.
# A malicious region like "West' OR '1'='1" must simply return [].
# ---------------------------------------------------------------------------
def orders_in_region(conn, region):
    """Order ids for one region."""
    # >>> SOLUTION
    rows = conn.execute("SELECT order_id FROM orders WHERE region = ? ORDER BY order_id", (region,)).fetchall()
    return [row[0] for row in rows]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | create_customers   (Level 1 - Beginner)
# Create table customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT) if it does
# not exist, insert every (name, city) tuple of `rows`, and COMMIT. Return nothing.
# ---------------------------------------------------------------------------
def create_customers(conn, rows):
    """Create and fill the customers table."""
    # >>> SOLUTION
    conn.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT)")
    conn.executemany("INSERT INTO customers (name, city) VALUES (?, ?)", rows)
    conn.commit()
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | revenue_by_payment   (Level 2 - Intermediate)
# Return {payment_method: total revenue rounded to 2 decimals}. Use GROUP BY.
# ---------------------------------------------------------------------------
def revenue_by_payment(conn):
    """Revenue per payment method."""
    # >>> SOLUTION
    rows = conn.execute(
        "SELECT payment_method, ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) "
        "FROM orders GROUP BY payment_method").fetchall()
    return dict(rows)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | top_products   (Level 2 - Intermediate)
# Return a list of (product, revenue rounded to 2) tuples for the n highest-revenue
# products, best first. n comes from a parameter (use a placeholder for LIMIT too).
# ---------------------------------------------------------------------------
def top_products(conn, n):
    """Best products by revenue."""
    # >>> SOLUTION
    return conn.execute(
        "SELECT product, ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS r "
        "FROM orders GROUP BY product ORDER BY r DESC LIMIT ?", (n,)).fetchall()
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | orders_per_month   (Level 2 - Intermediate)
# Return {"2026-01": number of orders, ...} using strftime on order_date.
# ---------------------------------------------------------------------------
def orders_per_month(conn):
    """Order counts per month."""
    # >>> SOLUTION
    rows = conn.execute("SELECT strftime('%Y-%m', order_date), COUNT(*) FROM orders GROUP BY 1").fetchall()
    return dict(rows)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | regions_above   (Level 3 - Challenge)
# Return the LIST of regions whose TOTAL revenue is strictly greater than min_revenue,
# highest revenue first. Use HAVING.
# ---------------------------------------------------------------------------
def regions_above(conn, min_revenue):
    """Regions beating a revenue threshold."""
    # >>> SOLUTION
    rows = conn.execute(
        "SELECT region FROM orders GROUP BY region "
        "HAVING SUM(quantity * unit_price * (1 - discount_pct / 100.0)) > ? "
        "ORDER BY SUM(quantity * unit_price * (1 - discount_pct / 100.0)) DESC", (min_revenue,)).fetchall()
    return [row[0] for row in rows]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | customer_totals   (Level 3 - Challenge)
# Tables: customers(id, name, city) and purchases(id, customer_id, amount).
# Return [(name, total_spent), ...] for EVERY customer (0 if they bought nothing),
# highest total first, ties broken by name A-Z. Use LEFT JOIN + COALESCE.
# ---------------------------------------------------------------------------
def customer_totals(conn):
    """Total spent per customer."""
    # >>> SOLUTION
    return conn.execute(
        "SELECT c.name, COALESCE(SUM(p.amount), 0) AS total "
        "FROM customers c LEFT JOIN purchases p ON p.customer_id = c.id "
        "GROUP BY c.id ORDER BY total DESC, c.name").fetchall()
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-3 | transfer   (Level 3 - Challenge)
# Table accounts(id INTEGER PRIMARY KEY, owner TEXT, balance REAL).
# Move `amount` from account from_id to to_id as ONE transaction (use `with conn:`):
#   * source missing or balance < amount  -> raise ValueError("insufficient funds")
#   * destination does not exist           -> raise ValueError("unknown account")
#     and the debit must be rolled back (balances unchanged!).
# ---------------------------------------------------------------------------
def transfer(conn, from_id, to_id, amount):
    """Atomic money transfer."""
    # >>> SOLUTION
    with conn:
        row = conn.execute("SELECT balance FROM accounts WHERE id = ?", (from_id,)).fetchone()
        if row is None or row[0] < amount:
            raise ValueError("insufficient funds")
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_id))
        cursor = conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_id))
        if cursor.rowcount == 0:
            raise ValueError("unknown account")
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
import csv
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


def _orders_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE orders(order_id TEXT PRIMARY KEY, order_date TEXT, region TEXT, category TEXT, product TEXT, "
                 "quantity INTEGER, unit_price INTEGER, discount_pct INTEGER, payment_method TEXT)")
    with open(_datasets() / "sales.csv", encoding="utf-8", newline="") as f:
        conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)", [tuple(r.values()) for r in csv.DictReader(f)])
    conn.commit()
    return conn


def _create_customers_check():
    conn = sqlite3.connect(":memory:")
    create_customers(conn, [("Asha", "Pune"), ("Ben", "Delhi")])
    conn.rollback()  # if you forgot commit(), the rows vanish here
    rows = conn.execute("SELECT id, name, city FROM customers ORDER BY id").fetchall()
    try:
        conn.execute("INSERT INTO customers (name, city) VALUES (NULL, 'x')")
        not_null = False
    except sqlite3.IntegrityError:
        not_null = True
    return rows, not_null


def _totals_conn():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
        CREATE TABLE purchases (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL);
        INSERT INTO customers (name, city) VALUES ('Asha','Pune'), ('Ben','Delhi'), ('Chitra','Goa'), ('Dev','Goa');
        INSERT INTO purchases (customer_id, amount) VALUES (1, 100), (1, 50), (2, 30);""")
    return conn


def _transfer_scenarios():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance REAL);
        INSERT INTO accounts VALUES (1, 'Asha', 1000), (2, 'Ben', 200);""")

    def balances():
        return [row[0] for row in conn.execute("SELECT balance FROM accounts ORDER BY id")]

    def attempt(*args):
        try:
            transfer(conn, *args)
            return "ok"
        except ValueError as e:
            return str(e)

    return (
        attempt(1, 2, 300), balances(),
        attempt(1, 2, 5000), balances(),
        attempt(1, 99, 100), balances(),
    )


print("--- Day 28 checks ---")
check("L1-1 count_orders", lambda: count_orders(_orders_conn()), 300)
check("L1-2 orders_in_region", lambda: (len(orders_in_region(_orders_conn(), "West")), orders_in_region(_orders_conn(), "West")[:2]),
      (75, ["ORD1003", "ORD1005"]))
check("L1-2 injection attempt returns []", lambda: orders_in_region(_orders_conn(), "West' OR '1'='1"), [])
check("L1-3 create_customers (committed, NOT NULL)", _create_customers_check, ([(1, "Asha", "Pune"), (2, "Ben", "Delhi")], True))
check("L2-1 revenue_by_payment", lambda: revenue_by_payment(_orders_conn()),
      {"COD": 444847.65, "Card": 396415.65, "NetBanking": 321280.2, "UPI": 280698.05})
check("L2-2 top_products", lambda: top_products(_orders_conn(), 3),
      [("Smartwatch", 298814.6), ("Air Fryer", 279194.15), ("Running Shoes", 143652.1)])
check("L2-3 orders_per_month", lambda: orders_per_month(_orders_conn()), {
    "2026-01": 26, "2026-02": 25, "2026-03": 37, "2026-04": 32, "2026-05": 30,
    "2026-06": 35, "2026-07": 26, "2026-08": 32, "2026-09": 25, "2026-10": 32})
check("L3-1 regions_above 330000", lambda: regions_above(_orders_conn(), 330000), ["West", "South", "East"])
check("L3-1 regions_above 400000", lambda: regions_above(_orders_conn(), 400000), ["West"])
check("L3-2 customer_totals (LEFT JOIN)", lambda: customer_totals(_totals_conn()),
      [("Asha", 150.0), ("Ben", 30.0), ("Chitra", 0), ("Dev", 0)])
check("L3-3 transfer ok / insufficient / unknown account (rolled back)", _transfer_scenarios,
      ("ok", [700.0, 500.0], "insufficient funds", [700.0, 500.0], "unknown account", [700.0, 500.0]))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
