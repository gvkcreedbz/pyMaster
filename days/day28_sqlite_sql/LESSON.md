# Day 28 — Databases: SQLite & SQL

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Store data in a real database and ask it questions with SQL from Python | Upper-intermediate |

## 🌍 Real-world scenario & trend
**Files don't scale:** two people editing one CSV, a million rows, "show me West-region orders over ₹5,000 sorted by date" — databases solve this. SQLite is a full SQL database in **one file**, built into Python (`import sqlite3`) and running inside phones, browsers and apps. **Trend:** SQL is the #1 data skill after Python; the same SQL you learn today runs on PostgreSQL, MySQL, BigQuery and Snowflake. AI apps use databases for memory and (increasingly) vector search.

## 0. Warm-up (5 min) — Day 27 recap
- What does `raise_for_status()` do?  • How do you read an API key safely?

## 1. Concepts

### 1.1 Tables, rows, columns, keys
A **table** = spreadsheet with strict column types. A **primary key** uniquely identifies a row. A **foreign key** points to a row in another table (`purchases.customer_id → customers.id`).

### 1.2 Python ↔ SQLite
```python
import sqlite3
conn = sqlite3.connect("shop.db")        # creates the file (":memory:" = temporary DB)
conn.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT)")
conn.execute("INSERT INTO customers (name, city) VALUES (?, ?)", ("Asha", "Pune"))
conn.commit()                            # save the changes!
rows = conn.execute("SELECT name, city FROM customers WHERE city = ?", ("Pune",)).fetchall()   # list of tuples
conn.close()
```
`executemany(sql, list_of_tuples)` inserts many rows. `with conn:` commits on success and **rolls back on error**.

### 1.3 🔒 Always use `?` placeholders — never f-strings in SQL
```python
conn.execute(f"SELECT * FROM users WHERE name = '{name}'")      # ❌ SQL injection: name = "x' OR '1'='1"
conn.execute("SELECT * FROM users WHERE name = ?", (name,))     # ✅ safe
```
SQL injection is one of the most common real-world security holes.

### 1.4 The SELECT sentence (clause order matters!)
```sql
SELECT   region, SUM(quantity * unit_price) AS revenue     -- what to show
FROM     orders                                            -- which table
WHERE    order_date >= '2026-06-01'                        -- filter ROWS (before grouping)
GROUP BY region                                            -- one result row per region
HAVING   SUM(quantity * unit_price) > 100000               -- filter GROUPS (after grouping)
ORDER BY revenue DESC                                      -- sort
LIMIT    3;                                                -- only the first 3
```
Handy: `COUNT(*)`, `SUM`, `AVG`, `MIN`, `MAX`, `DISTINCT`, `LIKE '%watch%'`, `IN ('UPI','Card')`, `BETWEEN`, `IS NULL`, `strftime('%Y-%m', order_date)` (month of a date), `ROUND(x, 2)`, `COALESCE(x, 0)` (default for NULL).

### 1.5 JOIN — combining tables
```sql
SELECT c.name, COALESCE(SUM(p.amount), 0) AS total
FROM customers c
LEFT JOIN purchases p ON p.customer_id = c.id     -- LEFT keeps customers with no purchases
GROUP BY c.id
ORDER BY total DESC, c.name;
```
`INNER JOIN` = only matches; `LEFT JOIN` = all left rows (NULL where no match).

### 1.6 Transactions — all or nothing
Moving ₹500 = subtract here **and** add there. If the second step fails, the first must be undone:
```python
with conn:                              # BEGIN ... COMMIT, or ROLLBACK if an exception escapes
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (500, 1))
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (500, 2))
```
(ACID: Atomic, Consistent, Isolated, Durable.)

### 1.7 Indexes & pandas
`CREATE INDEX idx_orders_region ON orders(region);` speeds up searches on that column. Load results straight into pandas: `pd.read_sql("SELECT ...", conn)` and save with `df.to_sql("orders", conn, if_exists="replace", index=False)`.

## 2. Code along → `examples.py`
It builds `output/shop.db` from `datasets/sales.csv`, then asks real business questions. Optional: open the `.db` file with the *SQLite Viewer* VS Code extension or DB Browser for SQLite.

## 3. Common mistakes
- Forgetting `conn.commit()` — your inserts vanish.
- f-string SQL (injection!).
- `WHERE SUM(x) > 5` — aggregates belong in `HAVING`.
- Selecting non-grouped columns with `GROUP BY` (SQLite allows it silently — other databases don't).
- Integer division: `discount_pct/100` is `0` in SQL for integers → write `/100.0`.
- Comparing to `NULL` with `=` — use `IS NULL`.

## 4. Today's tasks → `practice.py` (an in-memory database with the 300 sales orders is prepared for you)
Table `orders(order_id, order_date, region, category, product, quantity, unit_price, discount_pct, payment_method)`. Revenue = `quantity * unit_price * (1 - discount_pct / 100.0)`.
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Count rows, parameterised filter, create + fill a table |
| L2-1…L2-3 | 🟡 | Revenue per payment method, top-N products, orders per month |
| L3-1…L3-3 | 🔴 | `HAVING`, `LEFT JOIN` customer totals, an all-or-nothing money transfer |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Write the SQL in plain words first: "From orders, for each payment method, add up revenue, biggest first." Then map words to clauses: FROM → GROUP BY → SUM → ORDER BY.</details>
<details><summary>Hint 2</summary>Rows come back as tuples: <code>[("COD", 444847.65), ...]</code>; <code>dict(rows)</code> turns two-column rows into a dict. Month: <code>strftime('%Y-%m', order_date)</code>. Transfer: <code>with conn:</code> + check <code>cursor.rowcount</code> after an UPDATE.</details>
<details><summary>Hint 3</summary><code>solutions/day28_solution.py</code></details>

## 6. Quiz — answers in `solutions/day28_answers.md`
1. What is a primary key? A foreign key?
2. Why `?` placeholders instead of f-strings?
3. `WHERE` vs `HAVING`?
4. When do you need `conn.commit()`?
5. `INNER JOIN` vs `LEFT JOIN`?
6. What does `with conn:` do when an exception occurs inside?
7. Why can `discount_pct/100` be wrong in SQL?
8. What does an index do and what's its cost?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: the **capstone** — combine everything into a data pipeline.
