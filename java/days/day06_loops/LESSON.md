# Day 06 — Loops (`for`, `while`, `do/while`, `break`, `continue`)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Repeat work automatically: tables, totals, retries, games, patterns | Beginner |

## 🌍 Real-world scenario & trend
**Number-guessing game + PIN retry + processing 1,000 orders.** Anything repeated is a loop: checking every row of a sales file, retrying a failed payment, a game that waits for the player, an ATM that keeps showing its menu.

**Why Java?** Batch jobs that process millions of rows (bank statements, invoices, log files) are classic Java work, and the loops you write today are the same ones, just on a small scale. **Trend:** later (Day 12) you will replace many loops with `stream` pipelines, but you must understand loops first.

## 0. Warm-up (5 min) — Day 05 recap
- What does `else if` do?
- Why can you not write `if (name)` for a String in Java?

## 1. Concepts (with tiny code)

### 1.1 The `for` loop: start, condition, step
```java
for (int i = 1; i <= 5; i++) {      // start; keep going while true; step after each round
    System.out.println("Round " + i);
}
for (int i = 10; i > 0; i -= 3) {   // 10 7 4 1  (countdown with step 3)
    System.out.print(i + " ");
}
```
Read it as: "start `i` at 1; while `i <= 5`, run the block; after each round do `i++`". `i++` means add 1. *Different from Python:* there is no `range()`; the three parts are written out. To count 0 to 4 write `i = 0; i < 5` (the end is excluded because of `<`).

### 1.2 Loop over every item: the enhanced `for`
When you do not need the counter, say "for each item":
```java
for (char ch : "Java".toCharArray()) {      // toCharArray() = the letters as a row
    System.out.println(ch);
}
for (String word : "red green blue".split(" ")) {
    System.out.println(word.toUpperCase());
}
```
Read `:` as "in". The row types (`char[]`, `String[]`, `int[]`) are *arrays*; Day 8 teaches them properly. Today you only loop over them.

### 1.3 The accumulator pattern (totals, counters)
```java
int[] prices = {499, 1299, 250};
int total = 0;                  // start value, BEFORE the loop
for (int p : prices) {
    total += p;                 // update inside the loop
}
System.out.println(total);      // 2048
```
`prices.length` is how many items the row has (3).

### 1.4 `while`: repeat until a condition becomes false
```java
int attempts = 0;
while (attempts < 3) {
    System.out.println("Try " + (attempts + 1));
    attempts++;                 // forget this -> infinite loop (Ctrl + C stops it)
}
```
The condition is checked **before** each round, so a `while` whose condition starts false never runs.

### 1.5 `do / while`: run once, then check
```java
int tries = 0;
do {
    tries++;
    System.out.println("Asking for the PIN, try " + tries);
} while (tries < 3);            // note the ; at the end
```
Use it when the body must run **at least once** (show a menu, then ask whether to continue).

### 1.6 `break` and `continue`
```java
for (int n = 1; n < 10; n++) {
    if (n == 3) continue;       // skip this round
    if (n == 6) break;          // leave the loop completely
    System.out.print(n + " ");  // 1 2 4 5
}
```
`while (true)` + `break` is the standard "keep asking until valid" pattern. *Different from Python:* Java has no `for ... else`; use a `boolean found = false;` flag instead.

### 1.7 Nested loops
```java
for (int row = 1; row <= 3; row++) {
    for (int col = 1; col <= 3; col++) {
        System.out.print(row * col + " ");
    }
    System.out.println();       // new line after each row
}
```
The inner loop runs completely for every round of the outer loop: 3 x 3 = 9 prints.

### 1.8 Random numbers for games
```java
import java.util.Random;                       // at the top of the file
Random random = new Random(2026);              // a seed makes the numbers repeatable (good for testing)
int secret = random.nextInt(20) + 1;           // nextInt(20) is 0..19, so +1 gives 1..20
```
Leave the seed out (`new Random()`) to get a different number every run.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section (rounds, totals, a table, patterns, a guessing game), run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button.

## 3. Common mistakes
- Infinite `while` loop: always change something that makes the condition false.
- Off-by-one: `i < 5` stops at 4; `i <= 5` includes 5.
- A semicolon after the loop head: `for (...);` runs an empty loop.
- Putting `int total = 0;` **inside** the loop, so it resets every round.
- Changing the loop variable inside the body by accident (`i++` twice).
- Comparing Strings in a loop with `==`. Use `.equals(...)`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Sum 1..n, count vowels, multiplication table |
| L2-1 … L2-3 | 🟡 Intermediate | Factorial, FizzBuzz, prime check |
| L3-1, L3-2 | 🔴 Challenge | PIN with 3 attempts, star pyramid |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Say the loop in words: "Start with ___. For each ___, do ___. At the end return ___."
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Sum: <code>int total = 0;</code> then <code>for (int i = 1; i &lt;= n; i++) total += i;</code>. Factorial: start <code>long result = 1;</code> and multiply by each number 2..n. FizzBuzz: check "divisible by 15" first, and join with spaces by adding <code>" "</code> before every word except the first. Prime: n &lt; 2 is not prime; try divisors <code>d</code> from 2 to n-1 and <code>return false</code> on the first <code>n % d == 0</code>. PIN: <code>for (String guess : guessesText.split(","))</code>, count the attempt, stop after 3 with <code>break</code>. Pyramid row i: <code>" ".repeat(n - i) + "*".repeat(2 * i - 1)</code>, with a <code>"\n"</code> between rows but not after the last.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day06_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day06_answers.md`
1. What numbers does `for (int i = 2; i < 10; i += 3)` produce?
2. What is printed? `for (int i = 0; i < 3; i++) { System.out.println(i); }`
3. How many times does `while (5 < 3) { ... }` run its body?
4. What is the difference between `break` and `continue`?
5. After `int total = 0; for (int n : new int[]{1, 2, 3}) { total += n; }` what is `total`?
6. How do you stop an infinite loop in the terminal?
7. Write a loop that prints 5 down to 1.
8. What is wrong with: `int count = 0; while (count < 3) { System.out.println(count); }`?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: **Week-1 project**, a mini ATM with a menu loop and `Scanner`, plus a review test.
