# Day 13 — Nested Data, Records & JSON (a restaurant-listing API)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Read, query, group and summarise API-style data (records, lists inside lists, maps of lists) and write it out as JSON text | Intermediate |

## 🌍 Real-world scenario & trend
**A restaurant-listing API (Zomato / Swiggy style).** The server returns a list of restaurants, and every restaurant has a *list of cuisines inside it*. As the developer you filter by city, compute averages, group and re-shape that data, and finally send it back as **JSON**.

**Why Java?** Java back-ends model this kind of data with **records** (small, safe data classes) and collections inside collections. JSON is the universal data format of web APIs, config files and tool calls from AI assistants, so handling nested data confidently is a daily skill. *Coming from Python?* A Python dict of fixed keys becomes a `record` here: the compiler knows `rating` is a `double`, so typos like `r.ratng()` are caught before you run anything.

## 0. Warm-up (5 min) — Day 12 recap
- What does `.filter(n -> n % 2 == 0)` keep?  • What does `Comparator.comparingInt(...).reversed()` do?

## 1. Concepts (with tiny code)

### 1.1 Nested structures: read them like a path
```java
record Restaurant(String name, String city, double rating, List<String> cuisines, int avgCost) {}

List<Restaurant> restaurants = List.of(
    new Restaurant("Spice Hub", "Delhi", 4.5, List.of("North Indian", "Chinese"), 600),
    new Restaurant("Dosa Corner", "Pune", 4.2, List.of("South Indian"), 250));
restaurants.get(0).cuisines().get(1);   // "Chinese"
restaurants.get(1).city();              // "Pune"
```
Read it like a path: list position → record field → list position.

### 1.2 `record`: a tiny data class
One line gives you a constructor, the getters (`name()`, `city()`, ... no `get` prefix), `equals` and a readable `toString`.
```java
Restaurant r = new Restaurant("Wok Express", "Mumbai", 3.9, List.of("Chinese"), 450);
System.out.println(r);        // Restaurant[name=Wok Express, city=Mumbai, rating=3.9, cuisines=[Chinese], avgCost=450]
System.out.println(r.equals(new Restaurant("Wok Express", "Mumbai", 3.9, List.of("Chinese"), 450)));   // true
```
A record never changes after it is built (its fields are final). Records can live inside your class, as in today's `Practice.java`.

### 1.3 Loop, filter, summarise
```java
List<String> delhi = restaurants.stream().filter(r -> r.city().equals("Delhi")).map(Restaurant::name).toList();
double avg = restaurants.stream().mapToDouble(Restaurant::rating).average().orElse(0);
Restaurant best = restaurants.stream().max(Comparator.comparingDouble(Restaurant::rating)).get();
```
`max(...)` returns an `Optional` (maybe nothing for an empty list); `.get()` is fine when you know the list is not empty.

### 1.4 Group into a Map of Lists
```java
Map<String, List<String>> byCity = new TreeMap<>();        // TreeMap: keys sorted A-Z
for (Restaurant r : restaurants) {
    byCity.computeIfAbsent(r.city(), c -> new ArrayList<>()).add(r.name());
}
```
`computeIfAbsent` says "if this city has no list yet, create an empty one", then you add to it. Python's `setdefault(city, []).append(...)`. Streams can do the same: `Collectors.groupingBy(Restaurant::city)`.

### 1.5 Safe access to deep data
```java
Map<String, Map<String, String>> order = Map.of("customer", Map.of("city", "Pune"));
order.getOrDefault("customer", Map.of()).getOrDefault("pin", "unknown");   // "unknown", no crash
```
When the data is a mix of maps and lists (like parsed JSON), test the type with `instanceof` pattern matching:
```java
if (current instanceof Map<?, ?> map && map.containsKey("a")) { current = map.get("a"); }
else if (current instanceof List<?> list && list.size() > 0) { current = list.get(0); }
```

### 1.6 JSON: nested data as text
JSON is just text with strict rules: `{"name":"Dosa","price":90,"veg":true,"tags":["south"],"coupon":null}`.

| Java | JSON |
|---|---|
| `Map` / `record` | object `{...}` |
| `List` | array `[...]` |
| `String` / `int` / `double` | string / number |
| `true` / `false` / `null` | `true` / `false` / `null` |

Real projects use a library (Jackson, Gson). Today you write a tiny writer yourself, because then you *really* know what JSON is: a method that calls itself for every nested list or map (**recursion**). Strings need `"` and `\` escaped:
```java
static String toJson(Object value) {
    if (value == null) return "null";
    if (value instanceof String s) return "\"" + s.replace("\"", "\\\"") + "\"";
    if (value instanceof Number || value instanceof Boolean) return value.toString();
    if (value instanceof List<?> list) return list.stream().map(v -> toJson(v)).collect(Collectors.joining(",", "[", "]"));
    throw new IllegalArgumentException("unsupported: " + value);
}
```

### 1.7 Copies and text blocks
```java
List<String> copy = new ArrayList<>(r.cuisines());   // a new list: adding to it leaves the original alone
String sample = """
        {"restaurant": "Spice Hub", "open": true}
        """;                                        // text block: multi-line text without \n and \"
```
The copy is **shallow**: the *items* are shared. That is harmless for strings and records (they never change), but lists inside lists would still be shared.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button. Add a sixth restaurant and watch the numbers change.

## 3. Common mistakes
- Writing `r.name` or `r.getName()` on a record: the getter is `r.name()`.
- Comparing text with `==` in `filter` (use `.equals`).
- `Map.of(...)` and `List.of(...)` cannot be changed and cannot hold `null`: use `new HashMap<>()` / `new ArrayList<>()` when you need to add things.
- Calling `.get(...)` on a list position that does not exist: `IndexOutOfBoundsException`. Check `size()` first.
- Forgetting to escape a `"` inside JSON text.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Names in a city, average rating, one-line description |
| L2-1 … L2-3 | 🟡 Intermediate | Best restaurant per city, cuisine index, total of an order made of records |
| L3-1 … L3-3 | 🔴 Challenge | City summary report, `deepGet("a.b.0.c")` path lookup, a JSON writer |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Print one restaurant, then work out on paper the path to the value you need (list → record → list). Solve a tiny example by hand first.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Best per city: loop and keep the best seen so far in a <code>Map</code> (<code>merge</code> helps). Cuisine index: a loop inside a loop with <code>computeIfAbsent</code>, then sort each list. Order total: <code>mapToInt(i -> i.price() * i.qty()).sum()</code>. City summary: group first, then <code>average()</code> each group and <code>round2</code>. deepGet: <code>path.split("\\.")</code>, then for each part ask "is it a Map with this key?" or "is it a List and the part a valid number?". toJson: one <code>if</code> per kind of value, calling <code>toJson</code> again for items.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day13_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day13_answers.md`
1. Which getter reads the city of a `record Restaurant(String name, String city)` value `r`?
2. What do you get for free when you write a `record`?
3. What is the path to `"Chinese"` in the Spice Hub example above?
4. Why use `getOrDefault("pin", "unknown")` on nested data?
5. What does `computeIfAbsent(city, c -> new ArrayList<>())` do?
6. What JSON text does `toJson` give for `List.of(1, "a")`?
7. Why can `Map.of("a", null)` not be used?
8. Is `new ArrayList<>(original)` a deep copy? Explain.

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: **Week-2 project**, an expense tracker that combines records, lists, maps and streams.
