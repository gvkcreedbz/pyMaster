# Day 25 — Collections Deep-Dive & Collectors (the sales analyst)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Load a real sales file, then group, count, total and rank it with `Collectors` in a few lines | Intermediate |

## 🌍 Real-world scenario & trend
**You're the new analyst at an online store.** The boss drops `datasets/sales.csv` (300 orders) on your desk: *"Which region earns most? Which products carry the business?"* Excel can answer it, but a program answers it again every morning, for 300 million rows, without mistakes.

**Why Java?** Reporting back-ends in banks, retail chains and airlines are written in Java. The tool they use every day is the stream `Collector`: *"group these rows by region, then count / add up / average each group"*. In the Python course you did the same with NumPy and pandas (`df.groupby("region")["revenue"].sum()`). In Java the table is a `List` of records and the groups are a `Map`. *Coming from Python?* There is no `DataFrame` in the JDK; a `List<Sale>` plus `Collectors.groupingBy` gives you the same answers, and the compiler checks every column name for you (`Sale::region` cannot be misspelled).

## 0. Warm-up (5 min) — Day 24 recap
- What does a unit test compare?  • Which Checker call prints `[PASS]` or `[FAIL]`?

## 1. Concepts (with tiny code)

### 1.1 Pick the right collection
| Need | Use | Why |
|---|---|---|
| ordered items, duplicates allowed | `ArrayList` | fast `get(i)` |
| a queue at the billing counter | `ArrayDeque` (`addLast`, `pollFirst`) | fast at both ends |
| no duplicates | `HashSet` (any order), `TreeSet` (A-Z) | `contains` is fast |
| key → value | `HashMap` (fast), `TreeMap` (keys sorted), `LinkedHashMap` (insertion order) | |
```java
Deque<String> counter = new ArrayDeque<>();
counter.addLast("Asha");
counter.addLast("Ben");
System.out.println(counter.pollFirst());   // Asha: first in, first out
```

### 1.2 Handy collection methods
```java
List<String> cart = new ArrayList<>(List.of("Pen", "Notebook", "Pen", "Lamp"));
Collections.frequency(cart, "Pen");          // 2
cart.removeIf(item -> item.equals("Lamp"));  // remove by a rule
Map<String, List<String>> byCity = new TreeMap<>();
byCity.computeIfAbsent("Pune", k -> new ArrayList<>()).add("Chai Point");   // make the list if missing, then add
List<Integer> frozen = List.copyOf(List.of(3, 1, 2));   // cannot be changed: add(...) throws UnsupportedOperationException
```
`computeIfAbsent` replaces the "if the key is missing, put a new list, then add" dance from Day 10.

### 1.3 One order = one record
```java
record Sale(String orderId, String orderDate, String region, String category, String product,
            int quantity, int unitPrice, int discountPct, String paymentMethod) {
    double revenue() { return quantity * unitPrice * (1 - discountPct / 100.0); }
}
```
Load the file once into a `List<Sale>` (Day 16: `readAllLines`, `split(",", -1)`, `Integer.parseInt`). Everything below works on that list.

### 1.4 `groupingBy` + `counting`
```java
Map<String, Long> perRegion = sales.stream()
        .collect(Collectors.groupingBy(Sale::region, TreeMap::new, Collectors.counting()));
// {East=84, North=70, South=71, West=75}
```
Read it aloud: *"group the sales by region (keep the regions A-Z in a TreeMap) and count each group"*. The first argument says **what to group by**, the middle one (optional) **which Map to build**, the last one **what to do with each group** (the "downstream" collector). Without the last argument you get a `List<Sale>` per key.

### 1.5 More downstream collectors
```java
Collectors.summingDouble(Sale::revenue)       // add up a number per group
Collectors.averagingDouble(Sale::quantity)    // average of a number per group
Collectors.mapping(Sale::product, Collectors.toSet())   // collect only one field of each row
Collectors.joining(", ")                      // glue strings together (on a Stream<String>)
```
```java
Map<String, Double> revenue = sales.stream()
        .collect(Collectors.groupingBy(Sale::region, TreeMap::new, Collectors.summingDouble(Sale::revenue)));
revenue.replaceAll((region, total) -> Math.round(total * 100) / 100.0);   // round at the END
```
Money tip: keep full precision while adding; round only for the final answer. (In real shop software use `BigDecimal`, Day 3.)

### 1.6 Top-N: group, then sort the entries
```java
byProduct.entrySet().stream()
        .sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))   // biggest value first
        .limit(3)
        .forEach(e -> System.out.println(e.getKey() + " " + e.getValue()));
```
A `Map` has no order you can sort, so sort its `entrySet()` (a stream of key/value pairs). For a tie-breaker use a lambda comparator: `Comparator.comparingDouble((Map.Entry<String, Double> e) -> e.getValue()).reversed().thenComparing(Map.Entry::getKey)`.

### 1.7 `partitioningBy` and `toMap`
```java
Map<Boolean, Long> split = sales.stream()
        .collect(Collectors.partitioningBy(s -> s.revenue() >= 10000, Collectors.counting()));   // {false=263, true=37}
Map<String, Integer> priceOf = sales.stream()
        .collect(Collectors.toMap(Sale::product, Sale::unitPrice, (first, second) -> first));   // one price per product
```
`partitioningBy` always gives exactly two groups. `toMap` needs a **merge function** (third argument) as soon as a key can repeat, otherwise it throws `IllegalStateException: Duplicate key`.

### 1.8 Python twin: the golden rule
In pandas the rule was "no `for` loops over rows". Here it is "no hand-written counting loops": if you catch yourself writing `map.put(key, map.get(key) + 1)`, a `Collector` does it better. Streams are lazy and used once: nothing happens until the final `collect(...)`.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run. It reads `../../datasets/sales.csv` and prints orders per region, revenue per region, the top 3 products and more.

## 3. Common mistakes
- `Collectors.counting()` returns a `Long`, not an `Integer`: `Map<String, Integer>` does not compile.
- `Collectors.toMap` without a merge function crashes on a repeated key.
- Rounding every order before adding (the totals drift). Round once at the end.
- Forgetting `TreeMap::new`: a plain `HashMap` has no useful order, so your output looks "random".
- Using a stream twice: `IllegalStateException: stream has already been operated upon or closed`.
- Dividing whole numbers: `discountPct / 100` is `0`; write `/ 100.0` (Day 3).

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | °C → °F with `map`, numbers above average, load the CSV into `Sale` records |
| L2-1 … L2-3 | 🟡 Intermediate | Filter orders, orders per region (`counting`), average quantity per category (`averagingDouble`) |
| L3-1 … L3-3 | 🔴 Challenge | Revenue per region, revenue per month, top-N products |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Say the task as a sentence: "group the sales by region, then add up the revenue of each group". The first half is the key function (<code>Sale::region</code>), the second half is the downstream collector. Print the map before you round it.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
<code>sales.stream().collect(Collectors.groupingBy(Sale::region, TreeMap::new, Collectors.summingDouble(Sale::revenue)))</code>, then <code>map.replaceAll((k, v) -> round2(v))</code>. Counting uses <code>Collectors.counting()</code>, averages use <code>Collectors.averagingDouble(Sale::quantity)</code>. Months: the key function is <code>s -> s.orderDate().substring(0, 7)</code>. Top-N: build the product totals map, then <code>entrySet().stream().sorted(...).limit(n).map(Map.Entry::getKey).toList()</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day25_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day25_answers.md`
1. What do the three arguments of `Collectors.groupingBy(Sale::region, TreeMap::new, Collectors.counting())` mean?
2. Which type does `Collectors.counting()` produce, `int` or `Long`?
3. Which collector adds up a `double` per group? Which one averages it?
4. Why do we sort `map.entrySet()` and not the map itself when we want a top 3?
5. What does `partitioningBy` return that `groupingBy` does not always return?
6. When does `Collectors.toMap` throw `IllegalStateException`, and how do you prevent it?
7. Why round only at the end when you add up revenue?
8. What does `computeIfAbsent("Pune", k -> new ArrayList<>())` do?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: streams again, but on a **messy** file: cleaning, sorting, top-N and text bar charts.
