# Day 01 — Hello, Java! (How a computer follows instructions)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h (incl. 30 min setup) | Compile and run your first program, print text and numbers, read a compiler error without panic | Beginner |

## 🌍 Real-world scenario & trend
**A café receipt printer.** Every POS machine, banking app and ATM runs *instructions*: "print the shop name, print each item, print the total". That is all a program is: a list of instructions executed top to bottom.

**Why Java?** It has been a top-5 language for 25+ years (TIOBE index, Stack Overflow survey). Android apps, most big-bank and insurance back-ends, Amazon- and Netflix-scale services, and a huge share of enterprise "Spring Boot" systems run on the JVM. Java is also *statically typed*: the compiler catches many mistakes before the program ever runs, which makes you a more careful programmer. This plan ends with data processing, a database and a small REST API, all in modern Java 21.

---

## 0. Setup (≈30 min) — skip what you already did
1. Follow `java/SETUP.md` (install a JDK 21, for example Eclipse Temurin).
2. Open a terminal in Cursor (**Ctrl + `**) and check:
   ```powershell
   java -version      # should print openjdk version "21..."
   javac -version     # should print javac 21...
   ```
3. Try **jshell**, a live calculator for Java. Type `jshell`, press Enter, then:
   ```java
   jshell> 2 + 3
   $1 ==> 5
   jshell> System.out.println("Hello")
   Hello
   jshell> /exit
   ```

## 1. Concepts (with tiny code)

### 1.1 A program = a class with a `main` method
Java wants every program inside a **class**. The computer starts at `main` and runs the instructions inside it top to bottom.
```java
class Hello {
    public static void main(String[] args) {
        System.out.println("Welcome to Chai Point");    // line 1 runs first
        System.out.println("One masala chai, please");  // line 2 runs second
    }
}
```
Run it with `java Hello.java` (Java 21 compiles and runs a single file for you).

### 1.2 `System.out.println()` shows things on screen
```java
System.out.println("Hello, World!");   // text goes in "double quotes"
System.out.println(2 + 3);             // numbers need no quotes -> 5
System.out.println("2 + 3");           // in quotes it is just text -> 2 + 3
```
Every statement ends with a semicolon `;`. Blocks of code live between `{` and `}`.

### 1.3 Comments — notes for humans (Java ignores them)
```java
// This is a one-line comment
System.out.println("Hi");   // this is also a comment
/* A comment that
   spans several lines */
```

### 1.4 Useful printing tricks
```java
System.out.print("Loading");            // print: no new line afterwards
System.out.println("...done");          // Loading...done
System.out.println("Line 1\nLine 2");   // \n = new line
System.out.println("Name\tPrice");      // \t = tab (aligns columns)
System.out.println("=".repeat(20));     // ==================== (repeat text)
System.out.printf("%d-%d-%d%n", 2026, 11, 16);   // 2026-11-16  (%d = whole number, %n = new line)
System.out.printf("%s costs %.2f%n", "Chai", 60.0);   // Chai costs 60.00  (%s = text, %.2f = 2 decimals)
```

### 1.5 Variables (preview — full lesson tomorrow)
A variable is a **labelled box with a type**: `String shop = "Chai Point";` or `int cups = 3;`. Java makes you say the type up front.

### 1.6 Errors are normal (every developer sees hundreds a day)
There are two kinds: **compile errors** (the compiler refuses to run your code) and **runtime errors** (it runs, then crashes).
```java
System.out.println("Hello);      // error: unclosed string literal       -> you forgot a quote
system.out.println("Hello");     // error: package system does not exist -> Java is CASE-SENSITIVE
System.out.println(hello);       // error: cannot find symbol            -> text needs quotes
System.out.println("Hi")         // error: ';' expected                  -> missing semicolon
```
**How to read a compiler error:** the first line says *what* and *where* (`Hello.java:3`), the next line shows your code with a `^` under the problem. Fix the **first** error first; the others are often side effects.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button.

## 3. Common mistakes
- Using "curly quotes" pasted from Word/WhatsApp instead of straight `"`.
- Forgetting the closing `)`, `}` or `;`.
- Writing `system.out` or `string` in lower case (it is `System` and `String`).
- Single quotes `'Hello'` for text: in Java, `'H'` is one character and text needs `"double quotes"`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Return text and numbers from small methods |
| L2-1, L2-2 | 🟡 Intermediate | Print a receipt; use `print` and `printf` |
| L3-1 | 🔴 Challenge | Draw a star triangle with `println` |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.
*(Each task is a **method** (a named box of instructions) that you fill in. You will master methods on Day 11. For now just write the lines inside the braces.)*

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Re-read sections 1.2 and 1.4. Compare the exact text in the task with what you print, character by character (spaces count!).
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
L1: <code>return "text";</code> or <code>return 3 * 120;</code>. L2-1: five <code>System.out.println(...)</code> lines inside the method. L2-2: one <code>printf</code>, one <code>print</code>, one <code>println</code>. L3-1: <code>System.out.println("*".repeat(1));</code>, then 2, 3, 4.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day01_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day01_answers.md`
1. What do `System.out.println("2 + 3");` and `System.out.println(2 + 3);` display?
2. Name the error: `system.out.println("Hi");`. Why does it happen?
3. Find the bug: `System.out.println("Hello);`
4. What is the difference between `print` and `println`?
5. What does `System.out.println("a\nb");` display?
6. What does `//` do in Java?
7. True or false: Java runs your file from the bottom to the top.
8. In a compiler error, which error should you fix first?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: variables, data types and `Scanner` input; we build a food-delivery bill splitter.
