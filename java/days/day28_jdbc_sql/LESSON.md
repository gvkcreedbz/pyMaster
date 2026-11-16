# Day 28 — Databases: JDBC & SQL with SQLite

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Store data in a real database and ask it business questions with SQL from Java (JDBC) | Intermediate |

## 🌍 Real-world scenario & trend
**Files don't scale.** Two people editing one CSV, a million rows, "show me West-region orders over ₹5,000, sorted by date": a database solves this. **SQLite** is a complete SQL database in **one file**; it runs inside phones, browsers and apps, and it needs no server. 

**Trend:** SQL is the most requested data skill after your main language. The same SQL you learn today runs on PostgreSQL, MySQL, Oracle, BigQuery and Snowflake. **Why Java?** Almost every bank and insurance back-end is Java talking to a database through **JDBC** (Java DataBase Connectivity): the one standard API for all databases. Spring Boot and Hibernate are built on top of it. *Coming from Python?* This is `sqlite3`, but with three differences: JDBC is in **auto-commit mode** by default (Python's `sqlite3` waits for `commit()`), column numbers start at **1**, and you map every result row to Java objects yourself.

## 0. Setup (3 min)
SQLite is not part of the JDK. The course folder `java/lib/` holds the driver `sqlite-jdbc-3.46.1.0.jar` (and two small `slf4j` jars it uses for logging). The portal's **Run** button puts them on the classpath for you. In a terminal add `-cp "../../lib/*"`:
```powershell
java -cp "../../lib/*" Examples.java
java -cp "../../lib/*" Practice.java
```
(If a jar is missing: `python _dev_tools/fetch_java_libs.py`.) No `import` of the driver is needed: `DriverManager` finds it on the classpath.

## 1. Concepts (with tiny code)

### 1.1 Tables, rows, columns, keys
A **table** is a spreadsheet with strict column types. A **primary key** identifies a row (`orders.order_id`). A **foreign key** points to a row in another table (`purchases.customer_id → customers.id`).

### 1.2 Connect, create, insert (JDBC)
```java
try (Connection conn = DriverManager.getConnection("jdbc:sqlite:shop.db")) {   // creates the file if missing
    try (Statement st = conn.createStatement()) {
        st.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT)");
    }
}
```
Everything that holds a database resource (`Connection`, `Statement`, `ResultSet`) goes into **try-with-resources** (Day 17), so it is closed even when an error happens. All JDBC methods throw the checked `SQLException`: add `throws SQLException` to your method.

### 1.3 🔒 Always use `?` placeholders (PreparedStatement)
```java
// WRONG: SQL injection. name = "x' OR '1'='1" changes the meaning of the query.
st.executeQuery("SELECT * FROM users WHERE name = '" + name + "'");

// RIGHT: the value travels separately from the SQL text.
try (PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE name = ?")) {
    ps.setString(1, name);                 // placeholder numbers start at 1
    try (ResultSet rs = ps.executeQuery()) { /* ... */ }
}
```
SQL injection is one of the most common security holes in real systems. `setString`, `setInt`, `setDouble` fit the column type. A `?` can only replace a **value** (not a table or column name).

### 1.4 Reading results: `ResultSet`
```java
try (Statement st = conn.createStatement();
     ResultSet rs = st.executeQuery("SELECT product, quantity FROM orders")) {
    while (rs.next()) {                    // moves to the next row; false when there are no more
        String product = rs.getString("product");   // by column name ...
        int quantity = rs.getInt(2);                 // ... or by number (starts at 1!)
    }
}
```
`executeQuery` is for `SELECT`; `executeUpdate` (returns the number of changed rows) is for `INSERT`, `UPDATE`, `DELETE`; `execute` is for anything else (`CREATE TABLE`). To insert many rows fast: `ps.addBatch()` in the loop, then one `ps.executeBatch()`.

### 1.5 The SELECT sentence (clause order matters!)
```sql
SELECT   region, SUM(quantity * unit_price) AS revenue     -- what to show
FROM     orders                                            -- which table
WHERE    order_date >= '2026-06-01'                        -- filter ROWS (before grouping)
GROUP BY region                                            -- one result row per region
HAVING   SUM(quantity * unit_price) > 100000               -- filter GROUPS (after grouping)
ORDER BY revenue DESC                                      -- sort
LIMIT    3;                                                -- only the first 3
```
Handy: `COUNT(*)`, `SUM`, `AVG`, `MIN`, `MAX`, `DISTINCT`, `LIKE '%watch%'`, `IN ('UPI','Card')`, `BETWEEN`, `IS NULL`, `strftime('%Y-%m', order_date)` (the month of a date), `ROUND(x, 2)`, `COALESCE(x, 0)` (a default for NULL). Same idea as `groupingBy` on Day 25: the database does it for you, close to the data.

### 1.6 JOIN: combining tables
```sql
SELECT c.name, COALESCE(SUM(p.amount), 0) AS total
FROM customers c
LEFT JOIN purchases p ON p.customer_id = c.id     -- LEFT keeps customers with no purchases
GROUP BY c.id
ORDER BY total DESC, c.name;
```
`INNER JOIN` keeps only matches; `LEFT JOIN` keeps every left row (NULL where nothing matches).

### 1.7 Transactions: all or nothing
Moving ₹500 means subtract here **and** add there. If the second step fails, the first must be undone:
```java
conn.setAutoCommit(false);              // start a transaction: nothing is saved yet
try {
    // UPDATE ... debit;  UPDATE ... credit;
    conn.commit();                      // save both
} catch (SQLException | RuntimeException e) {
    conn.rollback();                    // undo both
    throw e;
} finally {
    conn.setAutoCommit(true);
}
```
`executeUpdate` returns how many rows changed: `0` after the credit means "no such account". (ACID: Atomic, Consistent, Isolated, Durable.)

### 1.8 Indexes and integer division
`CREATE INDEX idx_orders_region ON orders(region);` makes searches on that column fast; the price is disk space and slower writes. And a classic trap: in SQL `discount_pct / 100` with whole numbers is `0` (`15 / 100 = 0`). Write `/ 100.0`.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it with `-cp "../../lib/*"`, then change values and re-run. It builds a database in a temporary file from `datasets/sales.csv`, asks business questions, shows an injection attempt that fails, a `LEFT JOIN` and a rolled-back transfer, then deletes the file.

## 3. Common mistakes
- Gluing values into the SQL text with `+` (injection!). Use `?`.
- Counting columns from 0: `rs.getInt(0)` throws; the first column is `1`.
- Forgetting `rs.next()` before reading the first row.
- Not closing the `Connection`, `Statement` or `ResultSet` (use try-with-resources). On Windows an open connection also stops you deleting the `.db` file.
- Turning auto-commit off and forgetting `commit()`: your inserts vanish when the connection closes.
- `WHERE SUM(x) > 5`: aggregates belong in `HAVING`.
- `discount_pct / 100` instead of `/ 100.0`, and comparing to `NULL` with `=` (use `IS NULL`).
- Forgetting `-cp "../../lib/*"`: `No suitable driver found for jdbc:sqlite:...`.

## 4. Today's tasks  `Practice.java`
The checker builds a database with the 300 orders of `sales.csv` in a temporary file. The table is `orders(order_id, order_date, region, category, product, quantity, unit_price, discount_pct, payment_method)`. Revenue = `quantity * unit_price * (1 - discount_pct / 100.0)`.
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Count rows, a parameterised filter (and an injection attempt), create and fill a table |
| L2-1 … L2-3 | 🟡 Intermediate | Revenue per payment method, top-N products, orders per month |
| L3-1 … L3-3 | 🔴 Challenge | `HAVING`, `LEFT JOIN` customer totals, an all-or-nothing money transfer |

Run `java -cp "../../lib/*" Practice.java` (or the portal's Run button): the auto-checker prints `[PASS]` / `[FAIL]`.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Write the SQL in plain words first: "From orders, for each payment method, add up the revenue." Then map the words to clauses: FROM, GROUP BY, SUM. Test the SQL alone in your head or print the rows before you map them to Java objects.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
The loop is always the same: <code>try (PreparedStatement ps = conn.prepareStatement(sql)) { ps.setString(1, value); try (ResultSet rs = ps.executeQuery()) { while (rs.next()) { list.add(rs.getString(1)); } } }</code>. For one number: <code>rs.next(); return rs.getInt(1);</code>. Month: <code>strftime('%Y-%m', order_date)</code>. Revenue: <code>ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2)</code>. Transfer: <code>setAutoCommit(false)</code>, the two <code>UPDATE</code>s, check <code>executeUpdate()</code> of the credit for <code>0</code>, <code>commit()</code>; in the <code>catch</code>: <code>rollback()</code> and rethrow; in <code>finally</code>: <code>setAutoCommit(true)</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day28_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day28_answers.md`
1. What is a primary key? A foreign key?
2. Why use `?` placeholders (`PreparedStatement`) instead of joining text with `+`?
3. `WHERE` versus `HAVING`?
4. How is auto-commit in JDBC different from Python's `sqlite3`, and when do you call `commit()`?
5. `INNER JOIN` versus `LEFT JOIN`?
6. What must happen to a transfer when the credit step fails, and which two calls make it happen?
7. Why can `discount_pct / 100` be wrong in SQL?
8. What does an index do, and what is its cost?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: the **capstone**. A CSV goes in, gets cleaned, lands in SQLite, and a report comes out.
