# Day 05 — Decisions (`if / else`, `&&` `||` `!`, ternary, `switch`)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Make programs choose between paths: the heart of every business rule | Beginner |

## 🌍 Real-world scenario & trend
**Delivery-fee rules (Swiggy/Zomato/Amazon) and ATM checks.** "Free delivery for members or orders above ₹499, else ₹30/₹50/₹80 by distance" is literally an `if / else if / else` chain. Fraud detection, pricing engines, loan approvals and game logic are the same idea at scale.

**Why Java?** Banking and insurance rules are written as thousands of decisions like these, and Java's compiler checks that every condition is a real `true`/`false`. **Trend:** modern Java (14+) has `switch` *expressions* with `->` arrows, which are shorter and safer than the old `switch` (see 1.6).

## 0. Warm-up (5 min) — Day 04 recap
- What does `"Python".substring(1, 4)` return?
- How do you compare two Strings ignoring case?

## 1. Concepts (with tiny code)

### 1.1 `if / else if / else`: braces mark the blocks
```java
int marks = 82;
if (marks >= 90) {
    System.out.println("A");
} else if (marks >= 75) {      // checked only if the previous conditions were false
    System.out.println("B");
} else {                       // runs when nothing above matched
    System.out.println("Keep going");
}
```
Rules: the condition goes in **round brackets**; the block goes in **curly braces**; the **first match wins** and the rest are skipped. *Different from Python:* Java uses `{ }`, not indentation (but still indent for humans), and the word is `else if`, not `elif`.

### 1.2 Combine conditions: `&&`, `||`, `!`
```java
int age = 25;
boolean hasTicket = true;
if (age >= 18 && hasTicket) {           // && = AND: both must be true
    System.out.println("Enter");
}
if (!hasTicket || age < 5) {            // || = OR, ! = NOT
    System.out.println("Special desk");
}
boolean workingAge = age >= 18 && age < 60;   // Java has no 18 <= age < 60: write both parts
```
A condition may be a `boolean` variable, a comparison, or a method that returns `boolean` (`name.isEmpty()`).

### 1.3 Conditions must be `boolean`: no "truthy" values
In Python `if name:` works for `""` or `0`. In Java the compiler refuses: you must ask a real true/false question.
```java
String name = "";
if (name.isEmpty()) {                   // not: if (name)
    System.out.println("Please enter your name");
}
int stock = 0;
if (stock == 0) { System.out.println("Out of stock"); }   // not: if (!stock)
```

### 1.4 Nested `if` (and when to avoid it)
```java
if (isMember) {
    if (orderValue > 500) {
        System.out.println("Free delivery + bonus");
    }
}
```
Prefer a flat `else if` chain or `&&` when possible: deep nesting is hard to read. You may leave out the braces for a single statement, but **always use braces**: it prevents bugs when you add a second line.

### 1.5 The ternary operator: a one-line choice
```java
String status = age >= 18 ? "adult" : "minor";     // condition ? valueIfTrue : valueIfFalse
```
Use it for small *values*; use `if` when you need to run several statements.

### 1.6 `switch` expressions: many choices, one value
```java
String command = "halt";
String reply = switch (command) {
    case "go" -> "Starting";
    case "stop", "halt" -> "Stopping";      // several labels in one case
    default -> "Unknown command";           // required: covers everything else
};
System.out.println(reply);                  // Stopping
```
The `switch` works for numbers, Strings and `enum`s (later). Each `case` has an arrow `->` and **no `break`** is needed. (You will see the old colon style `case 1: ... break;` in older code; forgetting `break` made it "fall through" to the next case.)

### 1.7 Text in conditions: `equals`, never `==`
```java
String answer = "Yes";
if (answer.equalsIgnoreCase("y") || answer.equalsIgnoreCase("yes")) {
    System.out.println("Order confirmed");
}
```
A common bug is `if (answer == "yes")`: it compares *objects*, not letters (Day 4). Another is `if (color.equals("red") || "blue")`: `"blue"` alone is not a question. Write `color.equals("red") || color.equals("blue")`.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section (grade, delivery fee, ternary, `switch`, ticket pricing), run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button.

## 3. Common mistakes
- `=` instead of `==` in a condition (`if (x = 5)` does not compile).
- A semicolon right after the condition: `if (x > 5);` ends the `if` early and the block always runs.
- Wrong order: put the **most strict** check first (`>= 90` before `>= 75`).
- `age == 18 || 19` is not allowed: write `age == 18 || age == 19`.
- Comparing Strings with `==` instead of `.equals(...)`.
- Forgetting `default` in a `switch` expression, or forgetting to give a value on every path of a method that `return`s.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Grade letter, sign of a number, biggest of three |
| L2-1 … L2-4 | 🟡 Intermediate | Delivery fee, ticket price, leap year, weekday name with `switch` |
| L3-1, L3-2 | 🔴 Challenge | Rock-paper-scissors referee, triangle classifier |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Draw a decision table on paper: rows = situations, columns = result. Then write one <code>if</code> / <code>else if</code> per row, strictest first.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Delivery: <code>if (isMember || orderValue &gt;= 499) return 0;</code> then by distance. Ticket: set a <code>price</code> variable first, then add the weekend surcharge in a second <code>if</code> only when <code>price &gt; 0</code>. Leap year: divisible by 4 <code>&amp;&amp;</code> (not by 100 <code>||</code> by 400). Weekday name: <code>return switch (day) { case 1 -&gt; "Monday"; ... default -&gt; "Invalid day"; };</code>. Rock-paper-scissors: check "same" first with <code>equals</code>, then list the 3 winning pairs for player 1. Triangle: check "not a triangle" first (sum of two sides &lt;= the third).
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day05_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day05_answers.md`
1. What is printed? `int x = 7; if (x > 5) { print("A"); } else if (x > 3) { print("B"); } else { print("C"); }`
2. Can you write `if (0)` or `if ("")` in Java? What do you write instead to test "empty" or "zero"?
3. Why is `if (x = 5)` an error?
4. What is wrong with `if (color == "red" || "blue")`? Write a correct version.
5. Rewrite as one line with the ternary operator: if `age >= 18` then `"adult"` else `"minor"`.
6. What does `!(3 > 2 && 1 > 2)` evaluate to?
7. In an `if / else if / else if / else` chain, how many blocks can run?
8. Which keyword is the "everything else" case in a `switch`?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: loops, with a number-guessing game and star patterns.
