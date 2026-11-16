# Day 12 — Lambdas & Streams (filter, transform and sort data in one pipeline)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Write short, readable code to filter, transform, sort and total data with lambdas and `Stream` | Intermediate |

## 🌍 Real-world scenario & trend
**E-commerce filters + music charts.** "Show products under ₹1,000, best rated first" and "Top 10 most-played songs" are all the same three moves: *filter*, *sort*, *transform*. Every shopping app, streaming service and dashboard does this all day long.

**Why Java?** Since Java 8, the `Stream` API is how back-end teams process lists of orders, users and events without writing loop after loop. The same style appears later in this course for reports and data pipelines (Days 25-26). *Coming from Python?* Streams are Java's list comprehensions and `sorted(key=...)`, and lambdas are Python's `lambda` with an arrow: `x -> x * 2`.

## 0. Warm-up (5 min) — Day 11 recap
- What does *overloading* mean?  • What does a `static int add(int a, int b)` method return and take?

## 1. Concepts (with tiny code)

### 1.1 A lambda is a tiny nameless method
Syntax: `(inputs) -> result`. With one input the brackets are optional.
```java
Function<Integer, Integer> doubler = x -> x * 2;      // takes an Integer, gives an Integer
System.out.println(doubler.apply(21));                 // 42
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
System.out.println(add.apply(60, 15));                 // 75
```
For a longer body use braces and `return`: `x -> { int y = x * 2; return y + 1; }`.

### 1.2 Functional interfaces: the "shape" of a lambda
Java is strictly typed, so every lambda needs a type. The JDK gives you ready-made ones in `java.util.function`:

| Type | Shape | Example |
|---|---|---|
| `Function<T, R>` | one input → one output | `s -> s.length()` |
| `Predicate<T>` | one input → `boolean` | `n -> n % 2 == 0` |
| `Supplier<T>` | nothing → one output | `() -> "Hello"` |
| `Consumer<T>` | one input → nothing (does something) | `s -> System.out.println(s)` |
| `BiFunction<A, B, R>` | two inputs → one output | `(a, b) -> a + b` |

Call them with `apply`, `test`, `get`, `accept`. You can also *pass* a lambda into a method, or *return* one from a method:
```java
static Predicate<Integer> biggerThan(int limit) { return n -> n > limit; }
System.out.println(biggerThan(100).test(250));   // true
```

### 1.3 Method references: a shortcut when the lambda only calls one method
```java
Function<String, String> a = s -> s.toUpperCase();
Function<String, String> b = String::toUpperCase;   // exactly the same thing
```
You will see `String::length`, `Integer::intValue`, `Product::price` and `System.out::println` everywhere.

### 1.4 Streams: source → middle steps → final step
A stream is a *pipeline*. You start from a collection, chain steps, and finish with one **terminal** step that produces the answer.
```java
List<Integer> nums = List.of(1, 2, 3, 4, 5, 6);
List<Integer> squares = nums.stream().map(n -> n * n).toList();           // [1, 4, 9, 16, 25, 36]
List<Integer> evens   = nums.stream().filter(n -> n % 2 == 0).toList();   // [2, 4, 6]
```
- `filter(test)` keeps what passes the test (Python: the `if` in a comprehension).
- `map(change)` turns every item into something else.
- Nothing happens until the terminal step (`toList()`, `sum()`, `count()` ...) runs.

### 1.5 Totals, counts and yes/no questions
```java
int total = nums.stream().mapToInt(Integer::intValue).sum();          // 21
double avg = nums.stream().mapToInt(Integer::intValue).average().orElse(0);   // 3.5
long big = nums.stream().filter(n -> n > 3).count();                   // 3 (count() gives a long)
boolean any = nums.stream().anyMatch(n -> n > 5);                      // true
int sumTo5 = IntStream.rangeClosed(1, 5).sum();                        // 15, like Python's range
```
`mapToInt` switches to an `IntStream`, which has `sum()` and `average()`. `average()` returns an `OptionalDouble` (maybe nothing for an empty list), so we finish with `.orElse(0)`.

### 1.6 Sorting with a `Comparator`
```java
record Song(String title, int plays) {}        // a tiny data class, more on Day 13
songs.stream()
     .sorted(Comparator.comparingInt(Song::plays).reversed().thenComparing(Song::title))
     .limit(3)                                  // keep the first 3
     .map(Song::title)
     .toList();
```
`comparingInt(...)` picks the sort key, `.reversed()` flips it (biggest first), `.thenComparing(...)` breaks ties. It is Python's key `(-plays, title)` in words.

### 1.7 Good to know
```java
int gst = 18;
List<Integer> taxed = prices.stream().map(p -> p + p * gst / 100).toList();   // OK: gst never changes
// gst = 5;  -> compile error: variables used inside a lambda must be effectively final
```
- A stream can be used **once**; the original list is never changed.
- `toList()` gives a list you cannot modify. Need a changeable one? `new ArrayList<>(list)`.
- `Collectors.joining(", ")` glues strings: `stream.collect(Collectors.joining(", "))`.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button. Try adding your own `filter` step.

## 3. Common mistakes
- Forgetting the terminal step: `list.stream().map(...)` alone does nothing.
- Writing `.sum()` straight after `map` on an `Integer` stream: use `mapToInt(...)` first.
- Changing a local variable inside a lambda (`total += n`): use `sum()` instead.
- Using `==` to compare strings inside `filter`: use `.equals(...)`.
- Reusing a stream: `IllegalStateException: stream has already been operated upon or closed`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Squares, even numbers, upper-case a list |
| L2-1 … L2-4 | 🟡 Intermediate | Affordable items, sort by length, count with a `Predicate`, build a discount `Function` |
| L3-1, L3-2 | 🔴 Challenge | Top-N songs (plays desc, title A-Z), transpose a matrix |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Write it as an ordinary <code>for</code> loop first. Then name each step of the loop: "keep this", "change that", "collect". Each name becomes <code>filter</code>, <code>map</code>, <code>toList</code>.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
squares: <code>IntStream.rangeClosed(1, n).map(i -> i * i).boxed().toList()</code>. affordable: stream the <code>menu.entrySet()</code>, <code>filter(e -> e.getValue() &lt;= budget)</code>, <code>map(Map.Entry::getKey)</code>, <code>sorted()</code>. sortByLength: <code>Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder())</code>. makeDiscount: <code>return price -> ...;</code>. topSongs: comparator from 1.6, then <code>limit(n)</code>. transpose: for each column number <code>c</code> use <code>IntStream.range(0, columns).mapToObj(c -> ...)</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day12_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day12_answers.md`
1. What does `Stream.of(1, 2, 3, 4).map(n -> n * 2).toList()` give?
2. What does `IntStream.rangeClosed(1, 10).filter(n -> n % 3 == 0).sum()` give?
3. Which functional interface fits the lambda `s -> s.length() > 3`?
4. Rewrite `x -> x.toUpperCase()` as a method reference.
5. What does `Stream.of("bb", "a", "ccc").sorted(Comparator.comparingInt(String::length).reversed()).toList()` give?
6. Why does `int total = 0; list.forEach(n -> total += n);` not compile? What should you use instead?
7. What does `Stream.<Integer>empty().allMatch(n -> n > 0)` return?
8. Why do we add `.thenComparing(...)` to a comparator?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: nested data (maps of lists) and `record`s, with a restaurant-listing API as the scenario.
