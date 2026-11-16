# Day 17 — Exceptions, try-with-resources & Logging (programs that survive)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Make programs survive bad input and failures, clean up resources safely, and leave a trail with `java.util.logging` | Intermediate |

## 🌍 Real-world scenario & trend
**A payment service.** Customers type letters instead of amounts, the bank API times out, a file is missing. A professional program never just crashes: it validates, retries, reports a clear reason, and **logs** what happened so engineers can investigate at 3 a.m.

**Why Java?** Banks and payment companies run on the JVM, and Java's exception system is one of its strongest tools: the compiler even *forces* you to think about failures that can happen (checked exceptions). **Trend:** observability (logs, metrics, traces) is a core skill; `System.out.println` debugging gets replaced by proper logging. Real projects use SLF4J/Logback, but they all work like the built-in `java.util.logging` you learn today.

## 0. Warm-up (5 min) — Day 16 recap
- How do you read all lines of a file with `java.nio.file`?  • What does `String.split(",")` return?

## 1. Concepts

### 1.1 `try / catch / finally`
```java
try {
    int amount = Integer.parseInt("two hundred");   // risky line
    System.out.println("OK: " + amount);            // skipped when the line above fails
} catch (NumberFormatException e) {                 // runs ONLY if that error happened
    System.out.println("Please type digits only");
} finally {                                         // ALWAYS runs (cleanup)
    System.out.println("Done");
}
```
Catch **specific** exceptions. `catch (Exception e)` catches almost everything and hides real bugs, so keep it as a last resort. Several types in one handler: `catch (ClassCastException | NumberFormatException e)`. *Different from Python:* it is `catch`, not `except`, and there is no `else` block.

### 1.2 The usual suspects
```java
Integer.parseInt("abc");        // NumberFormatException
int x = 10 / 0;                 // ArithmeticException: / by zero  (int division only)
int[] cart = new int[3];
cart[5] = 1;                    // ArrayIndexOutOfBoundsException (valid places are 0, 1, 2)
String s = null; s.length();    // NullPointerException (Java's most famous error)
(Integer) (Object) "text";      // ClassCastException
```
Every exception object has `e.getMessage()` (the explanation) and `e.getClass().getSimpleName()` (its name).

### 1.3 Checked vs unchecked exceptions
Java has two families. **Unchecked** ones (`RuntimeException` and children, like the list above) are bugs or bad input: you *may* catch them. **Checked** ones (like `IOException`) are failures outside your control (disk, network): the **compiler refuses** to compile until you either `catch` them or declare `throws`.
```java
static String firstLine(Path path) {
    try {
        return Files.readAllLines(path).get(0);
    } catch (IOException e) {                  // file missing, no permission, ...
        return "";
    }
}
static String firstLineOrFail(Path path) throws IOException {   // "my caller must deal with it"
    return Files.readAllLines(path).get(0);
}
```
Rule of thumb: handle an exception where you know what to do about it; otherwise let it travel up with `throws`.

### 1.4 Throwing your own errors
```java
static int setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("Age cannot be negative");   // "throw" + "new"
    }
    return age;
}
```
`IllegalArgumentException` ("you gave me a bad value") and `IllegalStateException` ("not allowed right now") are the two you will throw most.

### 1.5 Custom exceptions
```java
static class InsufficientFundsException extends Exception {     // extends Exception = checked
    InsufficientFundsException(String message) {
        super(message);                                          // hand the message to the parent
    }
}
throw new InsufficientFundsException("Need Rs. 500 more");
```
(`extends` is Day 20 — for now copy the pattern: it gives your errors a meaningful name. Use `extends RuntimeException` if you want an unchecked one.)

### 1.6 try-with-resources: automatic cleanup
Files, network connections and database connections must be **closed**. Put them in the parentheses of `try` and Java closes them for you, even when an exception flies:
```java
try (BufferedReader in = Files.newBufferedReader(path)) {   // any AutoCloseable
    System.out.println(in.readLine());
}                                                            // in.close() was called here
```
Any class with `implements AutoCloseable` and a `close()` method works (see `Examples.java`). It replaces the old, ugly `finally { in.close(); }`.

### 1.7 Reading a stack trace (bottom of the story first)
```text
Exception in thread "main" java.lang.ArithmeticException: / by zero     <- WHAT happened (read first!)
    at Shop.average(Shop.java:5)                                         <- where it blew up (look here)
    at Shop.main(Shop.java:12)                                           <- who called it
```
Debugging toolbox: **reproduce** with the smallest input; **read** the first line and the first `at` line that is *your* file; **print** values; use the **debugger** (click left of a line number in Cursor to set a breakpoint, press F5, step with F10/F11); **bisect** by commenting out half the code; **explain it aloud** to a rubber duck.

### 1.8 Logging instead of `println`
```java
Logger log = Logger.getLogger("shop");
log.info("order placed");                      // normal event
log.fine("details for developers");            // hidden: the default level is INFO
log.warning("disk almost full");               // something odd
log.severe("payment failed");                  // a failure (Java's word for ERROR)
log.log(Level.SEVERE, "crashed", exception);   // message + the stack trace
```
Levels, from quiet to loud: `FINE < INFO < WARNING < SEVERE`. A **handler** decides *where* the text goes (console, file, memory) and a **formatter** decides *how* it looks. Today you build a logger that writes into memory so the checker can read it (see `Examples.java`).

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** each section, run it with `java Examples.java`, then break things on purpose: parse `"12abc"`, withdraw too much, remove the `finally`.

## 3. Common mistakes
- An empty `catch` block (`catch (Exception e) { }`): errors vanish silently. At least log them.
- A huge `try` around 50 lines: wrap only the risky line.
- Catching `Exception` first and a specific one later (the compiler rejects unreachable catch blocks).
- Using a variable after a failed `try` that never assigned it (the compiler warns you).
- Forgetting `flush()` on a `StreamHandler`: the text stays in a buffer.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `safeInt`, `safeDivide`, read the first line of a maybe-missing file |
| L2-1 … L2-4 | 🟡 Intermediate | Validate an age (throw), withdraw with a custom checked exception, a `retry` helper, try-with-resources |
| L3-1, L3-2 | 🔴 Challenge | Check a batch of payments with reasons, build a `java.util.logging` logger |

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
On each line ask: <em>what could go wrong here?</em> Then decide: prevent it with an <code>if</code>, or handle it with <code>catch</code>. Read the exact exception name in your failing check.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
safeInt: <code>try { return Integer.parseInt(text); } catch (NumberFormatException e) { return defaultValue; }</code>. retry: loop <code>attempts</code> times, <code>try { return task.call(); } catch (Exception e) { last = e; }</code>, then <code>throw last;</code>. Payments: <code>Double.parseDouble</code> can throw, so catch it per payment and <code>continue</code>. Logger: <code>Logger.getLogger(name)</code>, <code>setUseParentHandlers(false)</code>, <code>setLevel(Level.INFO)</code>, <code>new StreamHandler(out, formatter)</code>, <code>addHandler</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day17_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day17_answers.md`
1. When does the `finally` block run? Name one thing it is good for.
2. Why is `catch (Exception e) { }` (empty) a bad idea?
3. Which exceptions are thrown by `Integer.parseInt("abc")`, `5 / 0`, writing to index 9 of `new int[3]`, and `Files.readAllLines(missingPath)`?
4. What is the difference between a checked and an unchecked exception?
5. How do you create and throw an error with your own message?
6. What does try-with-resources do for you, and what must the resource implement?
7. Which log level is hidden when the logger level is `INFO`: `FINE` or `WARNING`?
8. In a stack trace, which line do you read first, and which `at` line do you look at next?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` and add your most interesting error to the **Bug Journal**.
- Tomorrow: packages, imports, `java.time`, the standard library and a first look at Maven (`pom.xml`).
