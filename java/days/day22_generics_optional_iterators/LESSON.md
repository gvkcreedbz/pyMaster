# Day 22 — Generics, Optional, Iterators & Functional Interfaces (lazy data, wrapped functions, safe resources)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Write code that works for any type, avoid `null` surprises, process data lazily, wrap functions with extra behaviour and close resources safely | Intermediate |

## 🌍 Real-world scenario & trend
**Streaming a 10-GB log file, retrying flaky API calls, auto-closing database connections.** You never load a huge file into memory: you read it one line at a time. You never trust a network call to work the first time: you retry. You never forget to close a connection: you let the language do it. Python solves this with generators, decorators and `with`; Java solves it with **`Iterator`/`Stream`**, **functions that return functions**, and **try-with-resources**.

**Why Java?** Every collection you have used (`List<String>`, `Map<String, Integer>`) is built on **generics**. `Optional` is how modern Java APIs say "there may be no answer" instead of returning `null`. `Function`, `Predicate` and `Supplier` are the building blocks of streams (Day 12) and of Spring Boot, JUnit and every big framework you will meet.

## 0. Warm-up (5 min) — Day 21 recap
- What is a *constructor* for?  • Which keyword stops a field from being changed after creation?

## 1. Concepts (with tiny code)

### 1.1 `Iterable` and `Iterator` — what a for-each really does
```java
List<String> shelf = List.of("Chai", "Samosa");
Iterator<String> it = shelf.iterator();      // 1. ask for an iterator
while (it.hasNext()) {                       // 2. is there another item?
    System.out.println(it.next());           // 3. hand it over
}
```
`for (String s : shelf)` is just a shortcut for the loop above. Any class that implements `Iterable<T>` (one method: `iterator()`) can be used in a for-each. *Different from Python:* an `Iterable` can be looped over again and again; each `iterator()` call starts fresh.

### 1.2 Writing your own `Iterator` — a lazy "generator"
Python uses `yield`. Java has no `yield`, so you keep the state in fields:
```java
static Iterable<Integer> countdown(int n) {
    return () -> new Iterator<>() {
        private int current = n;                       // state lives here
        public boolean hasNext() { return current > 0; }
        public Integer next() { return current--; }    // hand out, then move on
    };
}
for (int x : countdown(3)) System.out.println(x);      // 3 2 1
```
**Lazy** means "calculate only when asked". That is why an iterator can describe an *endless* list (`hasNext()` always `true`). Streams are lazy too: `Stream.iterate(1, n -> n * 2).limit(5)` produces `1 2 4 8 16` and nothing more. And `Files.lines(path)` reads a giant file one line at a time.

### 1.3 Generics — one class for every type
The `<T>` is a **type parameter**: a placeholder that is filled in when you use the class.
```java
class Box<T> {
    private final T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}
Box<String> name = new Box<>("Chai");        // T = String
Box<Integer> cups = new Box<>(3);            // T = Integer
String s = name.get();                       // no cast needed: the compiler knows
```
A **generic method** declares its own `<T>` before the return type: `static <T> T firstOr(List<T> items, T fallback)`. Generics only work with objects, so you write `List<Integer>`, never `List<int>` (Day 9: wrapper types). The compiler checks the types for you: `name.get()` can never secretly be a number.

### 1.4 `Optional` — "maybe a value" instead of `null`
```java
Map<String, Integer> prices = Map.of("Chai", 20);
Optional<Integer> price = Optional.ofNullable(prices.get("Pizza"));   // empty box
System.out.println(price.isPresent());             // false
System.out.println(price.orElse(0));               // 0  (the fallback)
System.out.println(price.map(p -> p * 2).orElse(-1));   // -1: map only runs when a value exists
Optional.of("Chai");                               // a box with a value (never pass null here)
Optional.empty();                                  // an empty box
```
Return `Optional<T>` from a method that might find nothing; callers are *forced* to think about the empty case. Do not use it for fields or parameters. Avoid calling `get()` blindly: it throws if the box is empty.

### 1.5 Functional interfaces — functions as values
A **functional interface** has exactly one abstract method, so a lambda (Day 12) can implement it. The four you need every day:
| Interface | Method | Meaning | Example |
|---|---|---|---|
| `Function<T, R>` | `R apply(T)` | turn one thing into another | `s -> s.length()` |
| `Predicate<T>` | `boolean test(T)` | yes/no question | `n -> n > 10` |
| `Supplier<T>` | `T get()` | produce a value, takes nothing | `() -> "Hello"` |
| `Consumer<T>` | `void accept(T)` | use a value, return nothing | `s -> System.out.println(s)` |
```java
Function<Integer, Integer> addGst = price -> price * 118 / 100;
Function<Integer, String> label = price -> "Rs " + price;
addGst.andThen(label).apply(100);                  // "Rs 118"   (glue two functions together)
Predicate<String> isLong = s -> s.length() > 5;
isLong.negate().test("Chai");                      // true       (also .and(...) and .or(...))
```

### 1.6 Decorators — a function that returns a better function
Python has `@decorator`. Java has no `@` syntax for this, but the idea is the same: **take a function, return a new function that wraps it**.
```java
static <T, R> Function<T, R> logged(String name, Function<T, R> f) {
    return input -> {                                  // the wrapper
        System.out.println("calling " + name + "(" + input + ")");
        return f.apply(input);                         // call the original
    };
}
Function<Integer, Integer> square = logged("square", n -> n * n);
square.apply(6);        // prints the log line, returns 36
```
The same recipe gives you `retry(3, action)`, timers, and `memoize(f)` (a `HashMap` remembers earlier answers so a slow function runs only once per input). The variables a lambda uses from outside must not change (they are *effectively final*), so counters use `AtomicInteger` or an `int[]` box.

### 1.7 try-with-resources — Python's `with`
```java
try (Connection db = new Connection("shop-db")) {      // opened here
    db.query("SELECT * FROM orders");
}                                                       // close() runs here, ALWAYS
```
Anything that `implements AutoCloseable` can go in the round brackets. Its `close()` runs when the block ends normally *or* when an exception flies out, and **before** the `catch` block. Files, scanners, database connections and HTTP clients all work this way.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each numbered section, run it with `java Examples.java`, then change values and re-run. Watch the order of the lines printed in section 8: *opening, query, query, closing, caught*.

## 3. Common mistakes
- Writing `List<int>` (use `List<Integer>`), or raw `List` without `<...>` (you lose the compiler's help).
- Calling `optional.get()` on an empty `Optional` (throws `NoSuchElementException`). Use `orElse`, `map`, `ifPresent`.
- Forgetting that a lambda cannot change a local variable: `count++` inside a lambda will not compile.
- An `Iterator` whose `next()` forgets to move forward (infinite loop), or whose `hasNext()` is never `false` by accident.
- Closing a resource by hand (`db.close()`) and forgetting it when an exception happens: use try-with-resources.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `countdown` Iterable, endless `fibonacci` Iterator, generic `findFirst` returning an `Optional` |
| L2-1 … L2-4 | 🟡 Intermediate | generic `Box.map`, `countCalls` decorator, `retry`, `runJob` with try-with-resources |
| L3-1, L3-2 | 🔴 Challenge | lazy `chunked` batcher, `memoize` |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
For iterators, decide which <b>fields</b> hold the state (the current number, or the two latest Fibonacci numbers) and what <code>next()</code> must change. For the functions, ask: "what do I return? a new function (a lambda)". The lambda calls the original function and adds one extra thing.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
countdown: <code>return () -&gt; new Iterator&lt;&gt;() { private int current = n; ... };</code>. findFirst: a for-each with <code>if (test.test(item)) return Optional.of(item);</code> and <code>Optional.empty()</code> at the end. countCalls: <code>return input -&gt; { counter.incrementAndGet(); return f.apply(input); };</code>. retry: a for loop around <code>try { return action.get(); } catch (RuntimeException e) { last = e; }</code>, then <code>throw last;</code>. runJob: <code>try (Connection c = new Connection(log)) { ... } catch (...) { ... }</code>. chunked: <code>next()</code> fills a list while <code>chunk.size() &lt; size &amp;&amp; source.hasNext()</code>. memoize: <code>Map&lt;K, V&gt; cache</code> created OUTSIDE the returned lambda.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day22_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day22_answers.md`
1. What does a for-each loop do under the hood?
2. Which two methods must an `Iterator` have?
3. What does the `<T>` in `class Box<T>` mean?
4. Why can you not write `List<int>`? What do you write instead?
5. Why is returning `Optional<String>` better than returning `null`?
6. What does `new Box<>("Chai").map(String::length).get()` return?
7. Which functional interface fits "give me a boolean for this item"?
8. When does the `close()` of a try-with-resources run if the body throws an exception?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: regular expressions (cleaning a messy contact list), immutability and clean-code habits.
