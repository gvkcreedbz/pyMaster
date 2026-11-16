# Day 28 - Quiz answers

1. A **primary key** uniquely identifies each row of its table (no duplicates, never NULL). A **foreign key** is a column that stores another table's primary key to link the rows (`purchases.customer_id` → `customers.id`).
2. A placeholder sends the value separately from the SQL text, so input can never be read as SQL. That prevents **SQL injection** (for example `West' OR '1'='1` would otherwise return every row).
3. `WHERE` filters individual rows **before** grouping; `HAVING` filters groups **after** aggregation (for example `SUM(x) > 100`).
4. A JDBC connection starts in auto-commit mode: every statement is saved at once. Python's `sqlite3` keeps changes in an open transaction until `commit()`. In JDBC you call `commit()` only after `setAutoCommit(false)`, to save a group of statements together.
5. `INNER JOIN` keeps only rows that have a match in both tables. `LEFT JOIN` keeps every row of the left table and fills the right-hand columns with NULL when there is no match.
6. Both steps must be undone, so no money disappears. `conn.setAutoCommit(false)` starts the transaction and `conn.rollback()` (in the `catch`) cancels it; `conn.commit()` saves it when everything worked.
7. With integer columns `discount_pct / 100` is whole-number division (`15 / 100 = 0`), so the discount vanishes. Write `/ 100.0` to get a decimal.
8. An index lets the database find rows by that column quickly (like a book index). The cost is extra disk space and slower writes (`INSERT`/`UPDATE`).
