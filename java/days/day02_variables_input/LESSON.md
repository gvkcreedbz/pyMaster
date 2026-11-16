# Day 02 — Variables, Types & Keyboard Input (`Scanner`)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Store data in typed variables, read text and numbers from the keyboard, format money neatly | Beginner |

## 🌍 Real-world scenario & trend
**A food-delivery bill splitter** (Swiggy / Zomato / Uber Eats style). The app keeps `itemName`, `price`, `qty`, `deliveryFee` in variables, then calculates and displays your bill. Every screen you see in an app is variables plus formatting.

**Why Java?** Java is *statically typed*: you say `int` or `String` once, and the compiler stops you from putting text in a number box. Banks and payment systems love this safety net. **Trend:** modern Java (10+) lets you write `var` and let the compiler work out the type, and Java 15+ has *text blocks* for multi-line text.

## 0. Warm-up (5 min) — Day 01 recap
- What is the difference between `print` and `println`?
- Which compile error do you fix first when there are five?

## 1. Concepts (with tiny code)

### 1.1 Variables have a type
A variable is a labelled box. In Java the label **and the kind of thing it holds** are written together.
```java
String itemName = "Paneer Pizza";   // text (capital S!)
int price = 349;                    // whole number
double rating = 4.5;                // decimal number
boolean isVeg = true;               // true or false (lower case)
char size = 'M';                    // ONE character, single quotes
long phone = 9876543210L;           // huge whole number: long, with an L at the end
```
`=` means "store the right side in the box on the left". *Different from Python:* a box keeps its type forever, so `price = "cheap";` is a compile error.

### 1.2 Naming rules and `final`
- Letters, digits, `_` and `$` only; cannot start with a digit; no spaces or `-`.
- Style is `camelCase` for variables (`deliveryFee`) and `UPPER_SNAKE` for constants (`DELIVERY_FEE`).
- Names are case-sensitive: `Price` and `price` are different boxes.
```java
final double DELIVERY_FEE = 40;   // final = constant, a later change will not compile
```

### 1.3 Variables can change, copies stay independent
```java
int qty = 2;
qty = qty + 1;     // now 3
int copy = qty;    // copy gets its own 3
qty = 10;
System.out.println(copy);   // still 3
```

### 1.4 `var` — let Java guess the type
```java
var city = "Pune";       // Java sees text -> String
var distanceKm = 4.2;    // double
var items = 3;           // int
```
It is **not** a loose type like Python: `city` is a `String` for life. Use `var` when the type is obvious from the right-hand side.

### 1.5 Reading from the keyboard with `Scanner`
```java
import java.util.Scanner;               // at the very top of the file

Scanner in = new Scanner(System.in);    // System.in = the keyboard
System.out.print("Item name: ");
String item = in.nextLine();            // one whole line of text
System.out.print("Quantity: ");
int qty = in.nextInt();                 // one whole number
```
`nextLine()` gives text, `nextInt()` an `int`, `nextDouble()` a `double`. Careful: **`nextInt()` leaves the invisible end-of-line behind.** A `nextLine()` right after it returns an empty text. Fix: call `in.nextLine();` once to throw the leftover away, or read every line with `nextLine()` and convert it yourself (next concept).

### 1.6 Text → number conversion (parsing)
Text and numbers are different things, even if they look alike.
```java
int age = Integer.parseInt("25");          // 25
double amount = Double.parseDouble("12.5");// 12.5
String text = String.valueOf(25);          // "25"
System.out.println("5" + 3);               // 53   (glued as text!)
System.out.println(5 + 3);                 // 8
```
`Integer.parseInt("12.5")` crashes with a `NumberFormatException`: use `Double.parseDouble` for decimals.

### 1.7 Formatting: `printf`, `String.format`, `.formatted`
```java
String name = "Aarav"; double total = 1234.5;
System.out.printf("Hi %s, total Rs. %.2f%n", name, total);   // Hi Aarav, total Rs. 1234.50
String line = String.format("%d x %s", 2, "Chai");           // 2 x Chai  (returns the text)
String same = "%d x %s".formatted(2, "Chai");                // the same thing
String cols = String.format("%-8s|%5d|", "Chai", 2);         // |Chai    |    2|  (- = left aligned)
```
`%s` text, `%d` whole number, `%f` decimal (`%.2f` = 2 decimals), `%%` a real percent sign, `%n` a new line. Use `\n` inside strings you *return*, because `%n` is `\r\n` on Windows.

### 1.8 Text blocks and `null`
A **text block** keeps line breaks for you. The closing `"""` decides how much indentation is removed.
```java
String slip = """
        ===== DELIVERY SLIP =====
        Item : %s
        """.formatted(itemName);
```
`null` means "no object yet" and only works for objects such as `String` (never for `int`): `String coupon = null;`.

## 2. Code along (30 min)  `Examples.java`
Builds a delivery-bill splitter step by step. The last section uses `Scanner`: run it in the terminal and answer the four prompts (your name, item, price, quantity). Type, do not copy-paste, then change values and re-run.

## 3. Common mistakes
- `"Total: " + 5 + 3` prints `Total: 53`, not 8. Put brackets around the sum: `"Total: " + (5 + 3)`.
- `int x = 12.5;` is a compile error: a decimal does not fit in an `int`.
- `nextInt()` followed directly by `nextLine()` returns an empty text (see 1.5).
- `1000 / 3` with two `int`s is `333`: the decimals are dropped. Make one side a `double`: `1000 / 3.0`. (More on Day 3.)
- `%.2f` follows your computer's language: some regions print `333,33` with a comma. That is normal, not a bug.
- Writing `string` or `Boolean` when you meant `String` or `boolean`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Declare variables of the right type; calculate a total; convert text to numbers |
| L2-1 … L2-3 | 🟡 Intermediate | Format an order summary; split a bill; read an order with `Scanner` |
| L3-1, L3-2 | 🔴 Challenge | Build a full multi-line invoice; read a trip bill (the `nextInt` trap) |

Run `java Practice.java`. Keyboard tasks are tested automatically: the checker types the answers for you.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Say the type out loud for every value: text, whole number, decimal or yes/no? For output tasks, compare your text with the expected text character by character (spaces, dots and <code>Rs.</code> count!).
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
L2-1: <code>return String.format("%d x %s = Rs. %.2f", quantity, item, unitPrice * quantity);</code>. L2-2: <code>(double) total / people</code> before formatting. L2-3: <code>Scanner in = new Scanner(System.in);</code>, then <code>in.nextLine()</code> three times and <code>Double.parseDouble</code> / <code>Integer.parseInt</code>. L3-1: subtotal, then tip = subtotal * tipPercent / 100, then total; glue four <code>String.format</code> lines with <code>\n</code>. L3-2: <code>nextInt()</code> twice, one extra <code>nextLine()</code> to clear the line, then <code>nextLine()</code> for the name.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day02_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day02_answers.md`
1. Which Java type would you use for `5`, `5.0`, `"5"`, `'5'` and `true`?
2. `int x = 10; int y = x; x = 20; System.out.println(y);` prints what?
3. Which names are valid: `2ndItem`, `item2`, `my-price`, `my_price`, `class`?
4. What does `System.out.println("5" + 3);` print, and what does `System.out.println(5 + 3);` print?
5. What does `String.format("%.2f", 349.5)` return?
6. Why does `int n = in.nextInt(); String s = in.nextLine();` give an empty `s`, and how do you fix it?
7. What does `Integer.parseInt("12.5")` do?
8. What does the keyword `final` do in `final double GST = 18;`?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: numbers and operators; we build a discount, GST and loan-EMI calculator.
