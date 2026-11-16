# Day 28 — Quiz answers

1. A **primary key** uniquely identifies each row in its table (no duplicates, not NULL). A **foreign key** is a column that stores another table's primary key to link rows (`purchases.customer_id → customers.id`).
2. Placeholders send values separately from the SQL text, so user input can never be interpreted as SQL — this prevents **SQL injection**.
3. `WHERE` filters individual rows **before** grouping; `HAVING` filters groups **after** aggregation (e.g. `SUM(x) > 100`).
4. After any INSERT/UPDATE/DELETE/CREATE you want to keep (unless you use `with conn:` which commits automatically on success).
5. `INNER JOIN` keeps only rows with a match in both tables; `LEFT JOIN` keeps all left rows and fills the right-hand columns with NULL when there is no match.
6. It rolls the whole transaction back (no partial changes are saved) and lets the exception continue to propagate.
7. With integer columns, `discount_pct / 100` is integer division (`15/100 = 0`); write `/ 100.0` to get a decimal.
8. An index lets the database find rows by that column quickly (like a book index) at the cost of extra disk space and slower writes.
