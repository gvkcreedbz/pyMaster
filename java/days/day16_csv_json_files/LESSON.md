# Day 16 — CSV & JSON-Style Files (sales reports and settings)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Turn real spreadsheet exports into insights, write new CSV reports, and save/load settings as JSON | Intermediate |

## 🌍 Real-world scenario & trend
**A sales report from an Excel/ERP export.** Every company has CSV exports (orders, attendance, bank statements). Analysts load them, total by region or month, and write a new CSV for management. App settings are usually stored as JSON. Today you analyse `datasets/sales.csv` (300 orders) and `datasets/students.csv`.

**Why Java?** Data feeds, batch jobs and report generators in banks, shops and airlines are very often Java programs that read a file, transform it and write another file: *Extract → Transform → Load* (ETL). Days 25-26 do the same with streams and collectors in a few lines; today you build the pieces by hand so you know what happens underneath. *Coming from Python?* There is no `csv` module in the JDK: you split lines yourself (or use a library such as Apache Commons CSV or Jackson in real projects), and a JSON reader/writer is also a library. We write small ones so you truly understand them.

## 0. Warm-up (5 min) — Day 15 recap
- Which option appends instead of overwriting?  • What does `throws IOException` promise?

## 1. Concepts (with tiny code)

### 1.1 CSV = text with commas
```text
order_id,order_date,region,quantity,unit_price,discount_pct
ORD1001,2026-01-02,North,2,1999,5
```
The first line is the **header** (column names); every other line is one record. Splitting a line is one call:
```java
String[] cells = "ORD1001,2026-01-02,North,2,1999,5".split(",", -1);   // 6 cells; -1 keeps empty cells at the end
```
Without the `-1`, `"a,b,,".split(",")` quietly drops the empty cells at the end!

### 1.2 Read a CSV: header + rows
```java
List<String> lines = Files.readAllLines(Path.of("../../datasets/sales.csv"));
String[] header = lines.get(0).split(",", -1);
for (String row : lines.subList(1, lines.size())) {          // skip the header
    String[] cells = row.split(",", -1);
    System.out.println(cells[2] + " " + cells[5]);            // region, quantity
}
```
**Everything is read as text!** Convert yourself: `Integer.parseInt(cells[5])`, `Double.parseDouble(...)`. A handy shape is a row as `Map<String, String>` (column name → cell), or a `record` with real types.

### 1.3 A record with a method
```java
record Sale(String region, int quantity, int unitPrice, int discountPct) {
    double revenue() { return quantity * unitPrice * (1 - discountPct / 100.0); }
}
```
The revenue formula for the sales file is `quantity × unit_price × (1 − discount_pct / 100)`. Note the `100.0`: with `100` Java would use whole-number division (Day 3!) and give 0 discount.

### 1.4 The "group & total" pattern
```java
Map<String, Double> totals = new TreeMap<>();
for (Sale s : sales) {
    totals.merge(s.region(), s.revenue(), Double::sum);       // add to the old total, or start one
}
```
Round only at the very end: `Math.round(x * 100) / 100.0` gives 2 decimals.

### 1.5 Writing a CSV
```java
List<String> out = List.of("month,orders", "2026-01,26", "2026-02,25");
Files.writeString(Path.of("report.csv"), String.join("\n", out) + "\n");
```
If a value contains a comma or a quote, wrap it in double quotes and write each inner quote twice: `Chai, masala` → `"Chai, masala"`. That is also why the plain `split(",")` is not enough for messy files (L3-3 builds a quote-aware splitter).

### 1.6 JSON as text: write and read
JSON is nested text: `{"theme":"dark","limits":{"daily":20000},"tags":["a","b"],"vip":true}`. You wrote a **writer** on Day 13 (nested data → text). Its partner, a **reader**, walks through the text with a position and, on seeing `{` reads an object, on `[` an array, on `"` a string, otherwise a number, `true`, `false` or `null`. It gives back `Map`, `List`, `String`, `Integer`/`Double`, `Boolean` and `null`.
```java
Object data = Json.parse("{\"size\": 12, \"tags\": [\"a\"]}");   // a Map with 12 (Integer) and a List
String text = Json.write(data);                                  // {"size":12,"tags":["a"]}
```
`Practice.java` contains a ready-made `Json` helper with both. Read it after the tasks: it is the recursion idea from Day 13 again. In real projects use a library (Jackson, Gson). Save and load are then just a file call around write/parse:
```java
Files.writeString(path, Json.write(settings));              // save
Object loaded = Json.parse(Files.readString(path));         // load
```

### 1.7 Merging configs: defaults + user overrides
Apps ship `defaults.json` and let a user file override only some keys. A **deep merge** goes key by key: if both sides hold an object, merge those objects too (a method that calls itself); otherwise the user's value wins.
```text
defaults {"ui":{"theme":"light","size":12},"lang":"en"}
user     {"ui":{"theme":"dark"}}
result   {"ui":{"theme":"dark","size":12},"lang":"en"}
```

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run. It reads `../../datasets/sales.csv` and writes only into a temporary folder that it deletes at the end.

## 3. Common mistakes
- Doing maths on text: `cells[5] * 3499` does not compile. Convert with `Integer.parseInt` first.
- `discountPct / 100` instead of `/ 100.0` (whole-number division, Day 3).
- Forgetting the header line: the first "row" is the column names and `parseInt` crashes on it.
- Splitting a messy row with `split(",")` when a cell contains a quoted comma.
- Forgetting `\n` at the end of each line you write (or the last line).
- Comparing doubles with `==` after adding them: round, or compare with a tiny tolerance.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Read a CSV into rows, revenue and total revenue, JSON save/load |
| L2-1 … L2-3 | 🟡 Intermediate | Revenue per region, write a CSV (with quoting), top students |
| L3-1 … L3-3 | 🔴 Challenge | Monthly sales report CSV, deep-merge JSON configs, quote-aware CSV line splitter |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]`. It writes only to a temporary folder.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Print the first three rows (<code>System.out.println(rows.subList(0, 3))</code>) to see the exact keys and types. Remember: every cell is text until you convert it.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Revenue helper: <code>Integer.parseInt(row.get("quantity")) * Integer.parseInt(row.get("unit_price")) * (1 - Integer.parseInt(row.get("discount_pct")) / 100.0)</code>. Top students: average = (math + science + english) / 3.0, sort with <code>comparingDouble(Ranked::average).reversed().thenComparing(Ranked::name)</code>. Monthly report: month = <code>order_date.substring(0, 7)</code>; keep two <code>TreeMap</code>s (orders, revenue) so months come out sorted. Deep merge: copy the defaults, then for each user key: if both values are <code>Map</code>s, merge them recursively; else <code>put</code>. Quote-aware split: loop over the characters, flip a <code>boolean inQuotes</code> on every quote, and only treat a comma as a separator when <code>inQuotes</code> is false.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day16_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day16_answers.md`
1. After `split(",")`, which type is the quantity `3` in a CSV row? How do you get a number?
2. What does `"a,b,,".split(",", -1)` give, and why the `-1`?
3. What is the revenue formula used today?
4. How do you get `"2026-01"` from `"2026-01-22"`?
5. What is the difference between `Json.write(...)` and `Json.parse(...)`?
6. Why is a CSV cell like `Chai, masala` wrapped in double quotes?
7. What is a "deep merge"?
8. Why is `"\"Chai, masala\",20".split(",")` the wrong way to read a messy CSV line?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: exceptions and logging: making programs robust when files are missing or data is messy.
