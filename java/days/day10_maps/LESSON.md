# Day 10 — Maps (key → value)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Model records and count or group data with `HashMap`, `LinkedHashMap` and `TreeMap` | Beginner+ → Intermediate |

## 🌍 Real-world scenario & trend
**A phone contact book, a product inventory, word counts.** Look up a name and get a number; look up an item and get its stock. Every web API (weather, payments, Instagram) sends **JSON, which is essentially a map of keys to values**. Configuration files and database rows map to maps too. "Count or group by key" (word frequency, sales per city) is the most common data-analysis pattern; you will use it again with streams on Days 25-26.

**Why Java?** Maps are the second pillar of the Collections Framework (after lists). Back-end Java code is full of `Map<String, ...>`: caches, lookups, request parameters. *Coming from Python?* `HashMap` is a `dict`, but the key type and value type are written in angle brackets, `Map<String, Integer>`, and a missing key gives `null` instead of a `KeyError`.

## 0. Warm-up (5 min) — Day 09 recap
- `set.add(x)` returns what?  • Which collection keeps its items sorted, `HashSet` or `TreeSet`?

## 1. Concepts (with tiny code)

### 1.1 Create, read, add, change, remove
```java
import java.util.HashMap;
import java.util.Map;

Map<String, Integer> menu = new HashMap<>();   // key = item name (text), value = price (Integer)
menu.put("chai", 20);                          // add
menu.put("samosa", 15);
menu.put("chai", 25);                          // same key again: the value is REPLACED
System.out.println(menu.get("chai"));          // 25
System.out.println(menu.get("pizza"));         // null  <- missing key, no crash
System.out.println(menu.getOrDefault("pizza", 0));   // 0   (safe + default)
System.out.println(menu.containsKey("samosa"));      // true (checks KEYS)
menu.remove("samosa");
System.out.println(menu.size());               // 1
```
Keys are **unique**. Values can repeat. Like lists, the value type must be an object type (`Integer`, not `int`).

### 1.2 Looping: keys, values or both
```java
for (String name : menu.keySet()) { System.out.println(name); }              // keys
for (int price : menu.values()) { System.out.println(price); }              // values
for (Map.Entry<String, Integer> e : menu.entrySet()) {                       // both (most common)
    System.out.println(e.getKey() + " -> " + e.getValue());
}
System.out.println(menu);              // {chai=25}   println shows a whole map
```
`Map.Entry` is one key-value pair. With `var` (Day 2) you can write `for (var e : menu.entrySet())` and skip the long type.

### 1.3 Three kinds of map: what order do you get?
| Class | Order of keys when you loop | Use it when |
|---|---|---|
| `HashMap` | no promised order | you only need fast lookups (default choice) |
| `LinkedHashMap` | the order you added them | you want to print things the way they came in |
| `TreeMap` | sorted (A-Z / smallest first) | you want a sorted report |

```java
Map<String, Integer> sorted = new TreeMap<>(menu);   // copy any map into a TreeMap to sort its keys
```
Declare the variable as `Map<...>` and choose the class only on the right side of `new`.

### 1.4 The counting pattern ⭐
```java
String text = "to be or not to be";
Map<String, Integer> counts = new TreeMap<>();
for (String word : text.split(" ")) {
    counts.put(word, counts.getOrDefault(word, 0) + 1);   // 0 the first time we see the word
}
System.out.println(counts);       // {be=2, not=1, or=1, to=2}
```
Shorter with `merge`: "put 1, or if the key exists add 1 to what is there".
```java
counts.merge(word, 1, Integer::sum);     // Integer::sum means "old + new" (lambdas and :: are explained on Day 12)
```

### 1.5 The grouping pattern ⭐
The value is a list, and the first time you see a key you must create that list.
```java
Map<String, List<String>> groups = new TreeMap<>();
for (String fruit : List.of("apple", "avocado", "banana")) {
    String letter = fruit.substring(0, 1);
    if (!groups.containsKey(letter)) {
        groups.put(letter, new ArrayList<>());      // first time: a fresh empty list
    }
    groups.get(letter).add(fruit);
}
System.out.println(groups);          // {a=[apple, avocado], b=[banana]}
```
One-line version: `groups.computeIfAbsent(letter, k -> new ArrayList<>()).add(fruit);` ("if the key is missing, create the value, then give it to me").

### 1.6 Sort the keys by value
A map has no "sort by value" method. Make a *list of the keys* and sort that list.
```java
List<String> words = new ArrayList<>(new TreeMap<>(counts).keySet());   // keys, A-Z
words.sort((a, b) -> counts.get(b) - counts.get(a));                     // biggest count first
System.out.println(words);           // [be, to, not, or]
```
`(a, b) -> counts.get(b) - counts.get(a)` says "put the item with the bigger count first". Java's `List.sort` is **stable**: equal items keep their earlier order, so sorting A-Z first keeps ties alphabetical (just like Python).

### 1.7 Nested maps
```java
Map<String, Map<String, Integer>> inventory = new TreeMap<>();
inventory.put("book", new TreeMap<>(Map.of("price", 120, "stock", 5)));
inventory.get("book").merge("stock", -1, Integer::sum);     // one book sold -> stock 4
```
`Map.of(k1, v1, k2, v2, ...)` makes a small **read-only** map (like `List.of`). Copy it into a `HashMap` if you need to change it. Nested data comes back on Day 13.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button. Try counting the letters of your own name.

## 3. Common mistakes
- Treating `get` as safe: `menu.get("pizza")` is `null`, and `int price = menu.get("pizza");` crashes with `NullPointerException`. Use `getOrDefault`.
- `Map<String, int>`: not allowed, write `Map<String, Integer>`.
- Forgetting that `for (x : map)` does not compile: loop over `keySet()`, `values()` or `entrySet()`.
- Expecting a `HashMap` to print in the order you added things (use `LinkedHashMap`), or sorted (use `TreeMap`).
- `map.put(key, new ArrayList<>())` every time in a grouping loop: it throws away the earlier list. Create it only when the key is missing.
- Changing a `Map.of(...)` map: `UnsupportedOperationException`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Safe price lookup, add stock, inventory value |
| L2-1 … L2-4 | 🟡 Intermediate | Word frequency, group by first letter, merge two maps and add, a sorted menu board |
| L3-1, L3-2 | 🔴 Challenge | Top-N words (ties alphabetical), first non-repeating character |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Ask three questions: "What is my key? What is my value? What is the value the first time I see a key?"
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
getPrice: <code>getOrDefault</code>. addStock: <code>put(item, getOrDefault(item, 0) + qty)</code>. inventoryValue: loop over <code>stock.entrySet()</code> and look up each price with <code>getOrDefault(key, 0)</code>. wordFrequency: lower-case, <code>replace</code> the four punctuation marks with <code>""</code>, <code>split(" ")</code>, skip empty words, then the counting pattern. groupByFirstLetter: the grouping pattern with <code>word.substring(0, 1).toLowerCase()</code>. mergeSum: start from <code>new HashMap&lt;&gt;(a)</code>, then <code>merge</code> each entry of <code>b</code>. menuLines: loop over <code>new TreeMap&lt;&gt;(menu).entrySet()</code> and add <code>key + "=" + value</code>. topWords: keys in A-Z order, <code>sort</code> by count (1.6), then <code>subList(0, Math.min(n, size))</code>. firstUniqueChar: <code>Map&lt;Character, Integer&gt;</code> counted with <code>text.charAt(i)</code>, then scan the text again.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day10_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day10_answers.md`
1. `Map<String, Integer> d = new HashMap<>(); d.put("a", 1);` What do `d.get("b")` and `d.getOrDefault("b", 0)` give?
2. How do you check whether a key exists in a map?
3. What does `d.put("a", 5)` do when the key `"a"` already exists?
4. Write the one-line way to add 1 to the counter of `word`, even when the word has never been seen.
5. Which map class keeps keys sorted, and which one keeps them in the order you added them?
6. How do you loop over keys and values together?
7. Why do we write `Map<String, Integer>` and not `Map<String, int>`?
8. Why does sorting the words A-Z first and then sorting by count keep ties alphabetical?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: methods: write reusable, well-named building blocks (and finally understand every `static` you have been typing).
