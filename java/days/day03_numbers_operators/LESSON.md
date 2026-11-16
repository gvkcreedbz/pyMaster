# Day 03 — Numbers, Operators & the `Math` class

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Do any calculation in Java: discounts, GST, EMI, BMI; understand `int` vs `double` division, `%`, casting, rounding and the `double` gotcha | Beginner |

## 🌍 Real-world scenario & trend
**E-commerce checkout + loan EMI calculator** (Amazon/Flipkart cart, bank apps, fintech like CRED/Groww). Every price, discount, tax and EMI you see is arithmetic on numbers. Java is the language behind a huge number of bank and payment back-ends, so it is very strict about *which kind* of number you use.

**Why it matters:** real systems keep money in `BigDecimal` (or in whole paise) because of the `double` gotcha below. Java also does **not** turn `7 / 2` into `3.5` for you, and that surprise has caused real production bugs. You meet both today.

## 0. Warm-up (5 min) — Day 02 recap
- Which type holds `4.5`? Which holds `349`?
- Write a `printf` format that shows `3.14159` with 2 decimals.

## 1. Concepts (with tiny code)

### 1.1 Arithmetic operators and the `int` division trap
| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+ - *` | add, subtract, multiply | `7 * 3` | `21` |
| `/` | divide | `7 / 2` and `7 / 2.0` | `3` and `3.5` |
| `%` | remainder (modulo) | `7 % 2` | `1` |

```java
System.out.println(7 / 2);     // 3    <- both are int, so the answer is an int (decimals dropped)
System.out.println(7 / 2.0);   // 3.5  <- one side is double, so the answer is double
```
*Different from Python:* Python's `/` always gives a decimal. In Java, **int ÷ int = int**. There is no `//` and no `**` (use `Math.pow`, see 1.3).

### 1.2 Order of operations (like school maths)
```java
int a = 2 + 3 * 4 * 4;     // 3*4*4 = 48 first, then + 2  -> 50
int b = (2 + 3) * 4;       // brackets first -> 20
```
`*`, `/` and `%` go before `+` and `-`. Use brackets when in doubt. **Percent maths:** `price * percent / 100`.

### 1.3 The `Math` class: your calculator toolbox
No import needed. These are *methods*: you call them with brackets.
```java
Math.sqrt(16)        // 4.0
Math.pow(2, 3)       // 8.0      (2 to the power 3)
Math.abs(-250)       // 250
Math.max(4, 9)       // 9        Math.min(4, 9) -> 4
Math.ceil(4.2)       // 5.0      (round UP)      Math.floor(4.8) -> 4.0 (round DOWN)
Math.round(3.5)      // 4        (nearest whole number; returns a long)
```
To round to **2 decimals**: `Math.round(x * 100) / 100.0` (note the `100.0`, so the division keeps decimals).
`Math.round(2.5)` is `3`, `Math.round(-2.5)` is `-2` (it always rounds .5 *up*).

### 1.4 Shortcuts: `+=`, `-=`, `*=`, `++`, `--`
```java
int cartTotal = 500;
cartTotal += 250;     // same as cartTotal = cartTotal + 250  -> 750
cartTotal *= 2;       // 1500
cartTotal++;          // add 1 -> 1501      (cartTotal-- subtracts 1)
```

### 1.5 Comparisons and `&&`, `||`, `!`
Comparisons give `true` or `false`: `==` equal, `!=` not equal, `<  >  <=  >=`. (`=` stores a value, `==` asks "are they equal?".)
```java
System.out.println(5 == 5.0);          // true  (numbers are compared by value)
System.out.println(5 != 6);            // true
System.out.println(3 >= 4);            // false
System.out.println(age >= 18 && age < 60);   // && = AND: both must be true
System.out.println(age < 5 || age >= 60);    // || = OR: one is enough
System.out.println(!(age >= 18));            // !  = NOT: flips true/false
```
Python writes `and`, `or`, `not`; Java writes `&&`, `||`, `!`. Tomorrow's email validator and Day 5's `if` statements use these.

### 1.6 Casting: changing the type of a number
Going to a *bigger* type is automatic (`int` → `double`). Going to a *smaller* one needs a cast in brackets, and the decimals are **cut off** (not rounded).
```java
int items = 7, people = 2;
System.out.println(items / people);            // 3     (int division)
System.out.println((double) items / people);   // 3.5   (cast first, then divide)
System.out.println((int) 3.99);                // 3     (cut off, not rounded)
double heightM = 175 / 100.0;                  // 1.75  (175 / 100 would give 1)
```
The cast applies to the thing right after it, so `(double) items / people` means `((double) items) / people`.

### 1.7 The `double` gotcha, and `BigDecimal` for money
```java
System.out.println(0.1 + 0.2);                      // 0.30000000000000004
System.out.println(0.1 + 0.2 == 0.3);               // false!
System.out.println(Math.abs(0.1 + 0.2 - 0.3) < 1e-9);   // true: "close enough" (1e-9 = 0.000000001)
```
Computers store decimals in binary, so some numbers (like 0.1) are slightly off. Never compare `double`s with `==`. For real money use `BigDecimal`, built from **text**:
```java
import java.math.BigDecimal;                       // at the top of the file
BigDecimal a = new BigDecimal("0.1");
BigDecimal b = new BigDecimal("0.2");
System.out.println(a.add(b));                      // 0.3  (exact)
System.out.println(new BigDecimal("19.99").multiply(BigDecimal.valueOf(3)));   // 59.97
```
`BigDecimal` has no `+`: use `.add`, `.subtract`, `.multiply`.

### 1.8 Overflow: an `int` has a ceiling
An `int` holds up to `2147483647` (about 2.1 billion). One more and it wraps around to a **negative** number, silently.
```java
int big = Integer.MAX_VALUE;
System.out.println(big + 1);          // -2147483648  (!)
long safe = (long) big + 1;           // convert BEFORE the maths
System.out.println(safe);             // 2147483648
```
Use `long` (write big literals with an `L`, as in `9876543210L`) when numbers can pass about 2 billion.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section (checkout, EMI, BMI, casting, `Math`, `BigDecimal`, overflow), run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button.

## 3. Common mistakes
- Dividing two `int`s and expecting decimals: `7 / 2` is `3`. Make one side a `double` (`7 / 2.0`).
- Writing `^` or `**` for power. Use `Math.pow(2, 3)`.
- `10 % 3` is the **remainder** (1), not a percentage.
- Comparing `double`s with `==`. Compare with a tiny tolerance instead.
- Casting too late: `(double) (a / b)` has already lost the decimals. Write `(double) a / b`.
- Storing money in `double` for real accounts. Use `BigDecimal` or whole paise in a `long`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Discount price, add GST, even/odd test |
| L2-1 … L2-3 | 🟡 Intermediate | Minutes → "2h 5m"; BMI calculator; exact average |
| L3-1 … L3-3 | 🔴 Challenge | Real bank EMI formula; exact bill with `BigDecimal`; overflow-safe total |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Write the calculation on paper with sample numbers first, then translate it into Java. If a result has no decimals when it should, look for an <code>int / int</code>.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Discount: <code>price - price * percent / 100</code>. Even: <code>n % 2 == 0</code>. Time: <code>total / 60</code> and <code>total % 60</code>. BMI = weight ÷ (height in metres)², so use <code>heightCm / 100.0</code>. Average: divide by <code>3.0</code>. EMI: <code>r = rate / 12 / 100</code>, <code>n = years * 12</code>, <code>growth = Math.pow(1 + r, n)</code>, <code>EMI = P * r * growth / (growth - 1)</code>, then <code>Math.round(x * 100) / 100.0</code>. Exact bill: <code>new BigDecimal(text).multiply(BigDecimal.valueOf(qty))</code>. Overflow: <code>(long) a * b</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day03_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day03_answers.md`
1. Evaluate `7 / 2`, `7 / 2.0`, `7 % 2`, `Math.pow(2, 3)`.
2. Evaluate `2 + 3 * 4 * 4`. Then `(2 + 3) * 4`.
3. Is `0.1 + 0.2 == 0.3` true? Why? How do you compare `double`s safely?
4. What do `Math.round(2.5)` and `Math.round(3.5)` return?
5. What does `x += 5;` mean?
6. How do you turn 125 minutes into hours and minutes? Write both expressions.
7. What is the value of `(int) 3.99`, and what is the value of `(double) 7 / 2`?
8. What happens when `Integer.MAX_VALUE + 1` is calculated, and how do you avoid it?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: strings, with an Instagram username and hashtag generator.
