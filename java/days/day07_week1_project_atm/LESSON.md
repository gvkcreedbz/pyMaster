# Day 07 — 🏆 Week 1 Project: Mini ATM + Guessing Game (and Week-1 Review)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Combine variables, strings, operators, `if`/`switch`, loops and `Scanner` into one working program, then test yourself on Week 1 | Beginner |

## 🌍 Real-world scenario & trend
**An ATM (and every "menu-driven" app).** A bank ATM = ask PIN → show menu → loop until Exit → each option checks the input against business rules. This "**input → validate → act → repeat**" loop is the skeleton of command-line tools, chatbots and game loops. **Why Java?** Banking back-ends are one of Java's biggest homes: the code that decides "may this customer withdraw ₹6,000 today?" very often runs on the JVM. **Trend:** professionals test such flows automatically. Today our checker feeds *fake keyboard input* to your ATM, a small preview of Day 24 (testing with JUnit).

## ⏰ Time plan
| Min | Activity |
|---|---|
| 0-10 | Warm-up: re-read your Bug Journal. Which mistakes keep coming back? |
| 10-30 | Read this page and run `Examples.java` (the menu-loop pattern) |
| 30-90 | Build the project in `Practice.java` (L1 → L2 → L3) |
| 90-110 | **Week-1 quiz** below (closed book) |
| 110-120 | Update the tracker, write your weekly reflection |

## 1. Concepts

### 1.1 The plan: small methods first, one big method last
```text
            +----------------------+
            | runAtm(balance, pin) |
            +----------+-----------+
                       v
        ask PIN (max 3 tries) --wrong x3--> "Card blocked" -> return
                       | correct
                       v
      +--------> show menu 1 Balance 2 Deposit 3 Withdraw 4 Exit
      |                |
      |  1 -> formatBalance()      2 -> deposit()
      |  3 -> validateWithdrawal() -> subtract + track today's total
      |  4 -> "Thank you!" -> return the final balance
      +----------------+
```
**Business rules (from Day 5):** a withdrawal must be a positive multiple of 100, not above the balance, and the total withdrawn today must stay within ₹20,000. Make each small method pass first. `runAtm` mostly just *calls* them, like a manager handing out jobs.

### 1.2 Reading a whole line with `Scanner`
```java
import java.util.Scanner;

Scanner in = new Scanner(System.in);        // create it ONCE per program
System.out.print("Enter PIN: ");
String pin = in.nextLine();                  // everything the user typed until Enter
int amount = Integer.parseInt(in.nextLine().trim());   // text "500" -> number 500
```
In this project we read **every** answer with `nextLine()` and convert the text ourselves. Why not `nextInt()`? It reads the number but leaves the Enter key behind, so the *next* `nextLine()` returns an empty line. Using `nextLine()` everywhere avoids that classic trap. Never call `in.close()` on a Scanner built on `System.in`: it closes the keyboard for the whole program.

### 1.3 The menu-loop pattern
```java
while (true) {
    System.out.print("Choose: ");
    String choice = in.nextLine().trim();
    switch (choice) {
        case "1" -> System.out.println("Balance...");
        case "2" -> System.out.println("Deposit...");
        case "4" -> { return; }                    // or: break out of the loop
        default  -> System.out.println("Invalid option");
    }
}
```
`while (true)` means "repeat forever", so you **must** have a way out: `return`, or `break` inside an `if`. (Careful: a plain `break` inside an old-style `switch` leaves only the switch, not the loop. The arrow form `case "4" -> { return ...; }` is the easy way out.)

### 1.4 Compare text with `.equals`, never `==`
```java
String typed = in.nextLine();
if (typed.equals("1234")) { ... }       // correct: compares the characters
if (typed == "1234")      { ... }       // WRONG: asks "same object in memory?", usually false
```
This is the most common Week-1 bug for people coming from Python, where `==` just works on text. Use `.equals` for every `String`.

### 1.5 Methods calling methods
A method can call any other method of the class. `runAtm` uses your `deposit`, `formatBalance` and `validateWithdrawal`. If the small ones pass their checks, the big one only has to put them in the right order. This is exactly how real programs are built: small, named, testable pieces.
```java
String reason = validateWithdrawal(balance, amount, withdrawnToday);
if (reason.equals("OK")) {
    balance -= amount;
    withdrawnToday += amount;       // remember today's total for the daily limit
}
```

### 1.6 Pretty money with `String.format`
```java
String.format(Locale.US, "Balance: Rs. %,.2f", 10300.0);   // Balance: Rs. 10,300.00
```
`%,.2f` = a number with a thousands comma and exactly 2 decimals. We pass `Locale.US` so the result does not change on a computer set to another country (some locales use `.` for thousands!). `String.format` *returns* the text; `System.out.printf` *prints* it.

### 1.7 How the checker "types" for you
Typing 10 lines into your ATM after every change would be tiring. So the checker swaps the keyboard for a prepared text: `"1234\n2\n500\n4\n"` means "type 1234, Enter, type 2, Enter...". Your code does not notice the difference. This is called an *automated test*, and professionals do it all day. You can still play for real with `java Practice.java play`.

## 2. Code along → `Examples.java`
A tiny tip-calculator menu that uses the same pattern: one `Scanner`, a `while (true)` loop, `break` to leave and `continue` to go back to the menu. Run it and type answers, or replay a saved conversation: `java Examples.java < ..\..\..\_dev_tools\stdin_java\day07.txt`.

## 3. Tasks → `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `deposit`, `formatBalance`, `guessFeedback` |
| L2-1, L2-2 | 🟡 Intermediate | `validateWithdrawal`, `playGuessingGame` (parse "10,15,12") |
| L3-1 | 🔴 Challenge | `runAtm`: the full interactive program, tested with fake keyboard input |

Stretch (not auto-checked): add a PIN-change option, a mini-statement that remembers the last 5 transactions, or a "guess the number" game that reads each guess from the keyboard. Play your ATM for real: `java Practice.java play`.

## 4. Common mistakes
- Comparing text with `==` instead of `.equals(...)`.
- Mixing `nextInt()` and `nextLine()`: the leftover Enter shows up as an empty line.
- Creating a new `Scanner` inside the loop on every round (create it once, before the loop).
- Forgetting a way out of `while (true)`: your ATM never ends.
- Typing the withdrawal rules in a different order than the task says: the *first* problem found wins.
- Printing the prompt with `println` when the task says `print` (the answer then appears on the next line).

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Make every small method pass first (L1, L2). <code>runAtm</code> mostly just <em>calls</em> them. Write the PIN part alone and test it before you touch the menu.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Inside <code>runAtm</code>: variables <code>balance</code> and <code>withdrawnToday</code>; a PIN loop with an <code>attempts</code> counter; then <code>while (true)</code> with a <code>switch</code> on the choice. For withdraw: <code>String reason = validateWithdrawal(...)</code>; if <code>reason.equals("OK")</code> subtract and add to <code>withdrawnToday</code>, else print the reason. Messages must match the task text exactly.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day07_Solution.java</code>, read one method only, close it, then write it yourself from memory.
</details>

## 6. Quiz — Week-1 review (closed book, 20 min) - answers in `java/solutions/day07_answers.md`
1. What is the difference between `System.out.print` and `System.out.println`, and what does `\n` do?
2. What is the result of `17 / 5`, `17 % 5` and `17 / 5.0`?
3. Why does `"3" + 4` give `"34"` and not `7`? How do you get 7 from the text `"3"` and the number 4?
4. How do you compare two `String`s for equality, and why is `==` wrong?
5. For `String name = "Aarav";` what are `name.charAt(0)`, `name.length()` and `name.substring(1, 3)`?
6. What does `for (int i = 1; i < 8; i += 3) System.out.println(i);` print?
7. What is the difference between `break` and `continue` inside a loop?
8. Find the bug: `if (age = 18) { ... }`, and why `in.nextInt()` followed by `in.nextLine()` surprises beginners.

**Scoring:** 7-8 great · 5-6 good (re-read your weak spots) · below 5 → redo the Day 2-6 L1 tasks tomorrow morning (15 min) before starting Day 8.

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` and the **Weekly Review** sheet: what was easiest, what was hardest, which 3 concepts do you still confuse, hours spent vs planned?
- Add **one** error you hit today to the **Bug Journal** sheet.
- ✅ Week-1 checklist:
  - [ ] I can explain variables, types and `String.format`
  - [ ] I can write `if / else if / else` and `switch` with `&&`, `||`, `!`
  - [ ] I can write `for` and `while` loops with `break` / `continue`
  - [ ] I can read a compiler error and a stack trace and find the failing line
  - [ ] My ATM passes every check in `Practice.java`
- Tomorrow: **arrays**, Java's fixed-size row of boxes. We start with a shopping cart and a leaderboard.
