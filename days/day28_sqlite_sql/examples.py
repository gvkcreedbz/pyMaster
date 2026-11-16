"""Day 28 - Code along: build a SQLite database from the sales CSV and query it."""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)
DB = OUT / "shop.db"
DB.unlink(missing_ok=True)                       # start fresh every run

# ---- 1. Create the table and load the CSV ----
conn = sqlite3.connect(DB)
conn.execute("""
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY, order_date TEXT, region TEXT, category TEXT, product TEXT,
        quantity INTEGER, unit_price INTEGER, discount_pct INTEGER, payment_method TEXT)
""")
with open(ROOT / "datasets" / "sales.csv", encoding="utf-8", newline="") as f:
    rows = [tuple(r.values()) for r in csv.DictReader(f)]
conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)", rows)
conn.commit()
print("rows loaded:", conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0])

REVENUE = "quantity * unit_price * (1 - discount_pct / 100.0)"


def ask(title, sql, params=()):
    print(f"\n-- {title}")
    for row in conn.execute(sql, params).fetchall():
        print("  ", row)


# ---- 2. Questions ----
ask("First 3 orders in the West", "SELECT order_id, product, quantity FROM orders WHERE region = ? ORDER BY order_id LIMIT 3", ("West",))
ask("Revenue per region", f"SELECT region, ROUND(SUM({REVENUE}), 2) AS revenue FROM orders GROUP BY region ORDER BY revenue DESC")
ask("Top 3 products", f"SELECT product, ROUND(SUM({REVENUE}), 2) AS r FROM orders GROUP BY product ORDER BY r DESC LIMIT 3")
ask("Orders per month", "SELECT strftime('%Y-%m', order_date) AS month, COUNT(*) FROM orders GROUP BY month")
ask("Regions above 330,000 (HAVING)", f"SELECT region, ROUND(SUM({REVENUE}), 2) FROM orders GROUP BY region HAVING SUM({REVENUE}) > ? ORDER BY 2 DESC", (330000,))
ask("Cards or UPI, quantity 5", "SELECT COUNT(*) FROM orders WHERE payment_method IN ('Card','UPI') AND quantity = 5")

# ---- 3. SQL injection demo: why placeholders matter ----
evil = "West' OR '1'='1"
unsafe = conn.execute(f"SELECT COUNT(*) FROM orders WHERE region = '{evil}'").fetchone()[0]
safe = conn.execute("SELECT COUNT(*) FROM orders WHERE region = ?", (evil,)).fetchone()[0]
print(f"\nInjection demo -> unsafe f-string matched {unsafe} rows (ALL of them!), safe placeholder matched {safe}")

# ---- 4. JOIN + transaction ----
conn.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
conn.execute("CREATE TABLE purchases (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL)")
conn.executemany("INSERT INTO customers (name, city) VALUES (?, ?)", [("Asha", "Pune"), ("Ben", "Delhi"), ("Chitra", "Goa")])
conn.executemany("INSERT INTO purchases (customer_id, amount) VALUES (?, ?)", [(1, 100), (1, 50), (2, 30)])
conn.commit()
ask("Customer totals (LEFT JOIN keeps Chitra)", """
    SELECT c.name, COALESCE(SUM(p.amount), 0) AS total
    FROM customers c LEFT JOIN purchases p ON p.customer_id = c.id
    GROUP BY c.id ORDER BY total DESC""")

try:
    with conn:                                   # rolls back automatically when an error escapes
        conn.execute("INSERT INTO customers (name, city) VALUES ('Temp', 'Nowhere')")
        raise RuntimeError("something went wrong mid-way")
except RuntimeError as error:
    print("\nerror:", error, "| customers after rollback:", conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0], "(still 3)")

conn.close()
print("\nDatabase file:", DB)
