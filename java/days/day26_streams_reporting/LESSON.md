# Day 26 — Streams II: Cleaning Messy Data & Reporting (sort, top-N, text charts)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Turn a messy export into trustworthy numbers, rank it, and draw a bar chart made of text | Intermediate |

## 🌍 Real-world scenario & trend
**Monday morning, a "fresh export" arrives: `datasets/sales_messy.csv`.** It has `" SOUTH "`, `"grocery "`, prices like `"1,999"`, blank cells and 8 duplicated rows. If you add it up as it is, every total is wrong. 

**Trend:** data analysts and engineers spend most of their time cleaning data. The habit *inspect → clean → validate → report* separates trustworthy numbers from confident nonsense. **Why Java?** Nightly ETL jobs in banks and shops are Java programs that do exactly this with streams, then write a report. *Coming from Python?* This is pandas II (`drop_duplicates`, `fillna`, `groupby`, `merge`, `pivot_table`) done with `distinct()`, `filter`, `map`, `Collectors` and plain `Map`s. For charts, Python used matplotlib; we draw bars with `"#".repeat(n)` (real Java apps use a charting library or send the numbers to a web page).

## 0. Warm-up (5 min) — Day 25 recap
- What does `groupingBy(Sale::region, TreeMap::new, counting())` return?  • Why round only at the end?

## 1. Concepts (with tiny code)

### 1.1 Inspect before you clean
```java
raw.size();                                                  // 308 rows
raw.stream().distinct().count();                             // 300 -> 8 exact duplicates
raw.stream().map(r -> r.get("region")).collect(Collectors.toCollection(TreeSet::new));   // 16 spellings of 4 regions!
raw.stream().filter(r -> r.get("quantity").isBlank()).count();   // 6 blanks
```
Each row is a `Map<String, String>` (column → text). Nothing is trimmed or converted yet, so you can *see* the mess. A `TreeSet` of the values shows every spelling at a glance.

### 1.2 The cleaning toolbox
```java
s.strip()                                    // " SOUTH " -> "SOUTH" (removes spaces on both sides)
Character.toUpperCase(s.charAt(0)) + s.substring(1).toLowerCase()   // "SOUTH" -> "South"
price.replace(",", "")                       // "1,999" -> "1999"; then Integer.parseInt(...)
cell.isBlank()                               // true for "" and "   "
rows.stream().distinct()                     // drops exact duplicates (works because Map has equals)
```
A reading tip: a cell like `"1,999"` contains a comma inside quotes, so `split(",")` would cut it in two. The `splitCsvLine` method you wrote on Day 16 (L3-3) handles it; it is already in today's `Practice.java`.

### 1.3 Decision log: fill or drop?
**Fill** when a sensible default exists: a blank discount means "no discount", so `0`. **Drop** when guessing would invent data: a blank quantity means we do not know what was sold. Write the decision down (a comment is enough) and **validate afterwards**: 300 distinct rows, 6 without quantity, so 294 rows remain.

### 1.4 One stream = one pipeline of small steps
```java
List<Sale> sales = raw.stream()
        .distinct()
        .filter(r -> !r.get("quantity").isBlank())
        .map(r -> new Sale(r.get("order_id"), r.get("order_date"), titleCase(r.get("region")), ...))
        .toList();
```
Each line does one job, in the order you would explain it to a colleague. Start from raw `String`s and end with a typed `record`: from then on the compiler protects you.

### 1.5 Sorting and top-N
```java
sales.stream()
        .sorted(Comparator.comparingDouble(Sale::revenue).reversed().thenComparing(Sale::orderId))
        .limit(5)                                // top 5 (the stream stops early)
        .toList();
```
`reversed()` flips the order (biggest first). `thenComparing` breaks ties so the result is the same every run.

### 1.6 Two numbers in one pass: `teeing`
```java
record Summary(long orders, double revenue) {}
Collectors.groupingBy(Sale::category, TreeMap::new,
        Collectors.teeing(Collectors.counting(), Collectors.summingDouble(Sale::revenue), Summary::new))
```
`teeing` runs two collectors at once and combines their results. (`Summary::new` works when both result types match the record's fields; with rounding use a lambda.)

### 1.7 A pivot table and a "merge" with plain maps
```java
Map<String, Map<String, Double>> pivot = new TreeMap<>();                      // region -> (category -> revenue)
pivot.computeIfAbsent(s.region(), k -> new TreeMap<>()).merge(s.category(), s.revenue(), Double::sum);
Double target = targets.get(region);                                           // the "merge": look the key up in the other table
```
If the key spellings differ (`"east"` vs `"East"`) the lookup silently returns `null`. Clean your keys **first**.

### 1.8 A bar chart made of text
```java
int bar = (int) Math.round(value / biggest * 30);                // longest bar = 30 characters
System.out.printf("%-6s | %s %d%n", region, "#".repeat(bar), Math.round(value));
// West   | ############################## 451772
```
`%-6s` pads the label to 6 characters (left-aligned). A chart needs a title, labels and one sentence that says what it shows. Pick the right type: **bars** compare categories, a **line** shows a trend over time, a **histogram** shows a spread of values.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run. It cleans the messy file, prints summaries, the five biggest orders, two text charts and saves a clean file in a temporary folder.

## 3. Common mistakes
- Cleaning without looking first, or without validating after (row counts, totals).
- `Integer.parseInt(" 4")` or `parseInt("1,999")` throws `NumberFormatException`: strip and remove commas first.
- `"a" == "a "` and friends: compare text with `equals`, after `strip()`.
- Merging maps whose keys are spelled differently: `get` returns `null`, then `null * 100` throws a `NullPointerException`.
- Forgetting a tie-breaker in `sorted(...)`: two products with the same revenue may swap places.
- Dividing by zero or by the "biggest" value when the list is empty: check `isEmpty()` first.
- Cut-off axes and 3D pies exaggerate or hide the truth, even in a text chart: start bars at zero.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `stripAndTitle`, count blank cells, drop duplicate rows |
| L2-1 … L2-3 | 🟡 Intermediate | Fix `"1,999"` prices, the full `cleanSales` pipeline, a summary per category (`teeing`) |
| L3-1 … L3-3 | 🔴 Challenge | Region vs target (%), a text `barChart` (top-N), a region × category pivot |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task. `readRows` and `splitCsvLine` are already written for you.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Do one cleaning step per line and print the size after each: <code>System.out.println(rows.size())</code>. The expected sizes are 308, 300 and 294. Say each task as a sentence first, then pick the stream step for every word.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Duplicates: <code>rows.stream().distinct().toList()</code>. Price: <code>Integer.parseInt(text.strip().replace(",", ""))</code>. cleanSales: <code>distinct()</code>, then <code>filter(r -&gt; !r.get("quantity").isBlank())</code>, then <code>map(r -&gt; new Sale(...))</code>. Summary: <code>Collectors.teeing(counting(), summingDouble(Sale::revenue), (orders, revenue) -&gt; new Summary(orders, round2(revenue)))</code>. Chart: sort the entries by value (biggest first), <code>limit(n)</code>, then <code>"#".repeat(Math.round(value / biggest * width))</code> and <code>String.format("%-" + labelWidth + "s | %s %d", ...)</code>. Pivot: <code>computeIfAbsent</code> + <code>merge</code>, then <code>putIfAbsent(category, 0.0)</code> for the gaps.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day26_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day26_answers.md`
1. Why inspect the data before you clean it?
2. When do you fill a missing value and when do you drop the row?
3. What does `stripAndTitle(" sOUTH ")` give, and which three calls build it?
4. Why does `"1,999"` need special care when you read a CSV line and when you convert it to a number?
5. What does `Collectors.teeing(a, b, f)` do?
6. Which chart type fits: a trend over time; comparing four regions; the spread of order values?
7. Why add `thenComparing(...)` to a `sorted(...)` that ends in `limit(n)`?
8. What goes wrong if the keys of two maps are spelled `"east"` and `"East"`?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: HTTP and JSON. Your program will talk to a web server (one you start yourself, no internet needed).
