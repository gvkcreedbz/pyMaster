# Day 29 — Capstone: Build a Sales Data Pipeline (CSV → clean → SQLite → report)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h (+ optional extra) | Combine four weeks of skills into one program that turns a messy CSV into a clean database and a report | Upper-intermediate |

## 🌍 Real-world scenario & trend
**Every Monday the store emails `sales_messy.csv`.** Your manager wants a cleaned database and a one-page report *without you repeating 40 manual steps*. That is a **data pipeline**: **E**xtract → **T**ransform → **L**oad → **R**eport. The same shape sits behind data engineering tools (Airflow, dbt, Spark), analytics dashboards and machine-learning feature pipelines.

**Why Java?** Nightly batch jobs that read a file, clean it, store it in a database and produce a report are classic Java work in banks, telecoms and retail. Types catch mistakes early, JDBC talks to every database, and the same code runs unchanged on a laptop or a server. *Coming from Python?* There is no pandas here: you use records for rows, streams for totals and JDBC for the database. It is more typing, but every step is explicit and easy to test.

## 0. Warm-up (5 min) — Day 28 recap
- Why do we use `?` placeholders in a `PreparedStatement`?  • What does `conn.commit()` do, and why `setAutoCommit(false)`?

## 1. Concepts (with tiny code)

### 1.1 The architecture
```text
sales_messy.csv --extract--> List<RawRow> --qualityReport--> (log the problems)
                                  |
                              transform (clean + types)
                                  |
                   List<Sale> --loadToSqlite--> sales.db --SQL--> revenue by region --> report.md + chart
                       |
                     kpis  ------------------------------------> report.md
```
**One method = one job.** `runPipeline` only calls the others in order; `cli` only reads the command line. That makes every piece easy to test (Day 24) and easy to replace.

### 1.2 Two records: raw and clean
```java
record RawRow(String orderId, String orderDate, String region, String quantity, String unitPrice) {}   // all text, dirty
record Sale(String orderId, LocalDate orderDate, String region, int quantity, int unitPrice, int discountPct) {
    double revenue() { return quantity * unitPrice * (1 - discountPct / 100.0); }
}
```
Keeping the raw data and the clean data in **different types** means the compiler stops you from using dirty values by mistake.

### 1.3 Look at the mess first: a quality report
Dirty files have **exact duplicate rows**, **empty cells**, prices like `"4,999"` (in quotes, with a comma!) and region text like `" south"` or `"SOUTH "`. Count them *before* you fix them, and log the numbers:
```java
long duplicates = raw.size() - new HashSet<>(raw).size();     // a record has equals/hashCode: copies collapse
```
Plain `split(",")` breaks `"4,999"` into two cells. Use the quote-aware `splitCsvLine` helper (Day 16).

### 1.4 Clean the rows
```java
for (RawRow r : new LinkedHashSet<>(raw)) {                    // keeps the first of every duplicate, keeps the order
    if (r.quantity().isBlank()) continue;                      // unusable order: skip it
    int discount = r.discountPct().isBlank() ? 0 : Integer.parseInt(r.discountPct());
    int price = Integer.parseInt(r.unitPrice().replace(",", ""));   // "4,999" -> 4999
}
```
Text: `strip()` the spaces and fix the capitals (`" south"` → `"South"`). Dates: `LocalDate.parse("2026-01-02")`. Never edit the raw input file.

### 1.5 Load into SQLite with JDBC
```java
try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbFile)) {      // the file is created for you
    conn.setAutoCommit(false);                                                       // one transaction
    try (PreparedStatement ps = conn.prepareStatement("INSERT INTO orders VALUES (?, ?, ?)")) {
        ps.setString(1, "ORD1"); ps.setString(2, "2026-01-02"); ps.setDouble(3, 13996.0);
        ps.addBatch();                                                               // collect many rows ...
        ps.executeBatch();                                                           // ... send them together
    }
    conn.commit();
}
```
SQLite has no date type: store dates as text `YYYY-MM-DD` (it sorts correctly). Use a **temporary file** for tests (`Files.createTempDirectory`) so a failed run leaves nothing behind. The driver lives in `java/lib/sqlite-jdbc-3.46.1.0.jar` (plus the slf4j jars); the portal puts them on the classpath for you.

### 1.6 Report from the database
```java
SELECT region, ROUND(SUM(revenue), 2) FROM orders GROUP BY region ORDER BY region
```
Let SQL do the grouping: it is what databases are good at. Then format numbers for people: `String.format(Locale.US, "%,.2f", 1415139.55)` gives `1,415,139.55`. A text chart (`#` repeated with `"#".repeat(n)`) replaces the picture.

### 1.7 A command-line front door and exit codes
A real program is started like `java Pipeline --input sales_messy.csv --out output`. Read `args` in pairs, print a friendly `Error: ...` message instead of a stack trace, and finish with `System.exit(code)`: **0 = success, non-zero = failure**. Schedulers (cron, Windows Task Scheduler) use that number to know whether the job worked.

## 2. Code along (30 min)  `Examples.java`
It runs the whole pipeline on the messy file inside a temporary folder and prints the quality numbers, the region chart and the report. **Type** each section, run it, then change something (for example drop the duplicate step) and watch the total change.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button.

## 3. Common mistakes
- One giant 200-line `main`. Split it: one method per job.
- Cleaning and reporting on **different** data. Always pass the cleaned list forward.
- Overwriting the raw input file. Write results into a separate output folder.
- No validation numbers: always log "rows before / after" and the revenue total, so a silent bug is visible.
- Forgetting `conn.commit()` after `setAutoCommit(false)` (nothing is saved), or not closing the connection (the file stays locked on Windows).
- Building SQL by gluing strings. Use `?` placeholders.
- Returning exit code `0` even when the job failed.

## 4. Today's tasks  `Practice.java`
You write the pieces in order. The helpers (`splitCsvLine`, `capitalise`, `bestBy`, `barChart`) are given.
| ID | Level | Task |
|---|---|---|
| L1-1, L1-2 | 🟢 Beginner | `extract` the raw rows, `qualityReport` of the problems |
| L2-1 … L2-3 | 🟡 Intermediate | `transform` to clean `Sale`s, `loadToSqlite`, `kpis` |
| L3-1 … L3-4 | 🔴 Challenge | report from SQL, `writeReport`, `runPipeline` (files + errors), `cli` with exit codes |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]`. It works in a temporary folder and deletes it afterwards.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Test each method alone with the real CSV before wiring them together. Print <code>raw.size()</code> after extract and <code>clean.size()</code> after transform: you should see 308 and 294.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
extract: <code>Files.readAllLines</code>, skip line 0, <code>splitCsvLine</code>, <code>new RawRow(c.get(0), ...)</code>. transform: loop over <code>new LinkedHashSet&lt;&gt;(raw)</code>, <code>continue</code> on a blank quantity, <code>replace(",", "")</code> before <code>parseInt</code>. loadToSqlite: DROP + CREATE with a <code>Statement</code>, then <code>PreparedStatement</code> with <code>addBatch</code>, <code>executeBatch</code>, <code>commit</code>. kpis: <code>round2(total)</code> and the provided <code>bestBy(sales, Sale::region)</code>. runPipeline: <code>Files.createDirectories(outDir)</code> and call your own methods in order. cli: loop <code>i += 2</code> over the args, catch <code>FileNotFoundException</code> first.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day29_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Stretch goals (after the checks pass)
1. Turn it into a real project folder with a `README.md` (what it does, how to run it, the diagram above).
2. Write 5 JUnit-style checks for `transform` and `kpis` with a tiny hand-made list (Day 24).
3. Add an optional `--month 2026-06` filter.
4. Add an index in SQL (`CREATE INDEX ... ON orders(region)`) and compare query times.
5. Ask an AI assistant to *review* your code, then **you** decide which suggestions are right. That judgement is the skill.

## 7. Quiz (10 min, no peeking) - answers in `java/solutions/day29_answers.md`
1. What do E, T and L stand for in ETL?
2. Why should the program finish with an exit code (`0` or non-zero)?
3. Why must you never overwrite the raw input file?
4. Why can `"ORD1142,...,\"4,999\",..."` not be read with a plain `split(",")`?
5. How can you count exact duplicate rows when the rows are records?
6. Why does `loadToSqlite` use a `PreparedStatement` and one transaction?
7. Why keep methods small and single-purpose?
8. Name two ways to make a pipeline's problems visible.

## 8. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: a REST API with the JDK's own `HttpServer`, a short look at Spring Boot, and the **final exam**.
