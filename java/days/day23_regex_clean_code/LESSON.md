# Day 23 — Regular Expressions, Immutability & Clean Code
| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Extract and validate patterns from messy text, build objects that cannot change, and write code others (and linters) love | Upper-intermediate |
## 🌍 Real-world scenario & trend
**Cleaning a messy contact/invoice dump** (`java/datasets/contacts_messy.txt`): pull out emails, Indian mobile numbers, invoice IDs and amounts, and mask card numbers before they reach a log file. **Trend:** regex is the Swiss-army knife for log parsing, data cleaning and validating LLM output; **immutable objects** (records, `List.copyOf`) are the modern default because they are safe to share between threads and easy to test; clean, small, well-named methods are what code reviews (and AI assistants) reward.
**Why Java?** Every Java web framework validates input with patterns (`@Pattern`, `String.matches`), and big Java code bases follow strict style rules. *Coming from Python?* There is no `r"..."` raw string: every backslash is doubled (`\d` is written `"\\d"`). The type hints you used in Python are simply part of Java, so today's second topic is immutability instead.
## 0. Warm-up (5 min) — Day 22 recap
- What does `Optional.empty().orElse(5)` return?  • What does `<T>` mean in `class Box<T>`?
## 1. Concepts (with tiny code)
### 1.1 Regex building blocks (in a Java string, double every backslash)
| Pattern | Meaning |
|---|---|
| `.` | any character (except a new line) |
| `\d` `\w` `\s` | digit / word char (letter, digit, `_`) / whitespace (`\D \W \S` = the opposite). In Java: `"\\d"` |
| `[abc]` `[a-z0-9]` `[^0-9]` | one char from a set / range / not in the set |
| `*` `+` `?` | 0+ / 1+ / 0-or-1 of the previous thing |
| `{4}` `{2,5}` | exactly 4 / between 2 and 5 |
| `^` `$` `\b` | start / end / word boundary |
| `(...)` `(?:...)` `\|` | capture group / non-capturing group / OR |
| `(?<name>...)` | named group (Python writes `(?P<name>...)`) |
### 1.2 `Pattern` and `Matcher`
```java
String text = "Order ORD1001 on 2026-11-03 for Rs. 899";
Pattern orderId = Pattern.compile("ORD\\d+");           // build the pattern once
Matcher m = orderId.matcher(text);
while (m.find()) {                                       // find() = next match ANYWHERE
    System.out.println(m.group());                       // ORD1001
}
Matcher date = Pattern.compile("(?<y>\\d{4})-(?<m>\\d{2})-(?<d>\\d{2})").matcher(text);
if (date.find()) System.out.println(date.group("y") + "/" + date.group("m"));   // 2026/11  (group(1) also works)
"560001".matches("[1-9]\\d{5}");                         // true: matches() must fit the WHOLE text
"a1b22".replaceAll("\\d", "#");                          // "a#b##"
"a, b;c".split("[,;]\\s*");                              // ["a", "b", "c"]
```
`find()` = "somewhere inside", `matches()` = "the whole text" (use it to validate), `lookingAt()` = "from the start". In a replacement text `$1` means "group 1". Flags: `Pattern.compile(regex, Pattern.CASE_INSENSITIVE)` or `(?i)` inside the pattern.
### 1.3 Greedy vs lazy
`<.+>` on `"<b>x</b>"` grabs everything from the first `<` to the last `>`; `<.+?>` stops at the first `>`. A `?` after `* + {n,m}` makes it lazy.
### 1.4 Lookaround: "next to, but not part of the match" (you need it for phone numbers)
```java
"(?<!\\d)9876543210(?!\\d)"      // (?<!\d) = NOT preceded by a digit,  (?!\d) = NOT followed by a digit
```
Without them, a pattern for a 10-digit mobile number would also match the last 10 digits inside a longer number (a 12-digit code, say). Lookarounds only check the surroundings and use up no characters, so they are not part of `group()`.
### 1.5 Regex advice
Start simple and test on real samples. Compile a `Pattern` **once** (`private static final Pattern EMAIL = ...`), not inside a loop. Use named groups. Prefer plain `String` methods (`contains`, `startsWith`, `split(",")`) when they are enough. **Do not parse HTML with regex** (use a parser library). Test your pattern at regex101.com (choose the *Java 8* flavour). Beware of nested quantifiers like `(a+)+`: on bad input they can take minutes ("catastrophic backtracking").
### 1.6 Immutability: objects that never change
```java
final class Basket {                                     // final: nobody can extend it and add changes
    private final List<String> items;                    // final: assigned once, in the constructor
    Basket(List<String> items) { this.items = List.copyOf(items); }   // OWN unmodifiable copy (defensive copy)
    Basket add(String item) {                            // "changes" return a NEW object
        List<String> more = new ArrayList<>(items);
        more.add(item);
        return new Basket(more);
    }
}
```
`String`, `Integer` and `LocalDate` are immutable too (`name.toUpperCase()` returns a new text). A `record` is immutable if its components are. **Recipe:** private final fields, no setters, copy mutable inputs in and out, return new objects. Why? Fewer bugs: nobody can change your data behind your back, and the same object is safe to use from many threads.
### 1.7 Clean code checklist
- Names: `camelCase` methods and variables, `PascalCase` classes, `UPPER_SNAKE_CASE` constants, `lowercase` packages. A name says *what*: `totalPrice`, not `tp`; a method is a verb (`findEmails`), a boolean starts with `is`/`has`.
- Small methods: one job each (about 20 lines or fewer). If you need a comment to explain a block, make it a method with a good name.
- No magic numbers: `static final double GST_RATE = 0.18;` instead of `1.18` in the middle of a formula.
- Guard clauses: check bad input first and `return`/`throw` early, so the main path is not buried in nested `if`s.
- No dead code, no copy-paste (extract a method), no huge `catch (Exception e) {}`.
- Comments explain **why**, not what. Javadoc (`/** ... */`) for public methods.
- Format consistently (4 spaces, braces always). Tools: your IDE's *Reformat* and inspections, `javac -Xlint:all` (extra compiler warnings), and in teams Checkstyle / Spotless / SonarLint.
### 1.8 Refactoring in one picture
```java
// before: deep nesting, magic number, unclear name
double f(double p) { if (p >= 0) { if (p > 0) { return p * 1.18; } else { return 0; } } else { throw new IllegalArgumentException(); } }
// after: guard clause, named constant, clear name
double priceWithGst(double price) {
    if (price < 0) throw new IllegalArgumentException("Price must not be negative");
    return price * (1 + GST_RATE);
}
```
## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each numbered section, run it with `java Examples.java` (inside this folder, because it reads `../../datasets/contacts_messy.txt`), then change the patterns. Try making the email pattern greedier and see what it swallows.
## 3. Common mistakes
- Writing `"\d"` instead of `"\\d"` ("illegal escape character" compile error).
- Using `matches()` when you meant `find()` (and the other way round): `"a123b".matches("\\d+")` is `false`.
- Calling `m.group()` before `m.find()` (`IllegalStateException: No match found`).
- A `split("|")` or `split(".")`: `|` and `.` are regex symbols; write `split("\\|")`.
- Greedy `.*` swallowing too much.
- Returning your private `List` from a getter, or storing the caller's list without copying: the "immutable" object is not immutable.
- Writing monster patterns nobody can read: split the task into steps and name the pieces.
## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Find emails, find mobile numbers, validate a PIN code |
| L2-1 … L2-4 | 🟡 Intermediate | Extract invoices (named groups), mask card numbers, normalise order ids, `priceWithGst` with a constant and a guard clause |
| L3-1, L3-2 | 🔴 Challenge | Parse a log line into a record (`Optional`), build an immutable `Basket` |
Run `java Practice.java` from this folder: the auto-checker prints `[PASS]` / `[FAIL]` for every task.
## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Open <code>java/datasets/contacts_messy.txt</code> and look at what you want, and what you do NOT want to match (invalid emails, toll-free numbers). Write the pattern for ONE example first, then test the rest.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Email: <code>"[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+"</code>. Indian mobile: starts with 6-9, 10 digits, optional <code>+91</code>, optional space/dash after 5 digits: two groups of 5 digits, joined, with <code>(?&lt;!\\d)</code> before and <code>(?!\\d)</code> after. PIN: <code>"[1-9]\\d{5}"</code> with <code>matches</code>. Card: <code>"\\b(?:\\d{4}[ -]?){3}(\\d{4})\\b"</code> replaced by <code>"**** **** **** $1"</code>. Order ids: <code>"(?i)\\bord-?(\\d+)"</code> and a <code>TreeSet</code>. Log line: one anchored pattern with named groups and <code>matcher.matches()</code>. Basket: <code>List.copyOf</code> in the constructor; <code>add</code> copies into a new <code>ArrayList</code>, adds, returns <code>new Basket(...)</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day23_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>
## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day23_answers.md`
1. Why must you write `"\\d"` in a Java string, and how do you write a regex for a literal dot?
2. What is the difference between `find()` and `matches()`?
3. What does `\d{3}-\d{4}` match?
4. Greedy vs lazy: what does `.+?` do?
5. How do you read a named group, and how do you refer to group 1 in `replaceAll`?
6. Name the three things that make a class immutable.
7. Why does a getter that returns a private `ArrayList` break immutability, and how do you fix it?
8. Name three Java naming rules, and say what a guard clause is.
## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: testing with **JUnit 5** and Git/GitHub basics.
