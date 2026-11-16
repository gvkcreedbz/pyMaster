# Day 21 — 🏆 Week 3 Project: Library Management System (and Week-3 Review)
| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Design classes that work together, enforce business rules with exceptions, and keep the state in a text file | Intermediate |
## 🌍 Real-world scenario & trend
**A public-library / office-asset system.** Books (or laptops, or bikes) are lent to members for 14 days; late returns cost ₹5 a day; each member may hold at most 3 items; staff want an overdue report and a "most borrowed" list. That is a classic *CRUD + business rules + persistence* application, the same shape as inventory, rentals and booking systems.
**Why Java?** This is the daily work of Java back-end developers: small immutable `record`s for data, one service class that guards the rules, custom exceptions, and a storage layer. The storage you write today is a plain text file; later you will swap it for a database (Day 28) and put a web API in front (Day 30) without changing the rules. *Coming from Python?* The `@dataclass` is a `record`, the `dict` loans are `Loan` records, and `date.fromisoformat` is `LocalDate.parse`.
## ⏰ Time plan
| Min | Activity |
|---|---|
| 0-10 | Warm-up: redo 1 failed exercise from Days 15-20 |
| 10-25 | Read the design below + run `Examples.java` (the same idea with bikes) |
| 25-95 | Build the system in `Practice.java` (L1 → L2 → L3) |
| 95-115 | **Week-3 Review Test** (closed book) |
| 115-120 | Tracker + weekly reflection |
## 1. Concepts (with tiny code)
### 1.1 The design
```text
record Book(isbn, title, author, copies)     class Library
record Loan(isbn, member, out)                 books:           Map<isbn, Book>        (a TreeMap: sorted keys)
(given)                                        loans:           List<Loan>             (active loans)
class LibraryError extends RuntimeException    checkoutCounts:  Map<isbn, times borrowed>
(given)
Rules: loan period 14 days · late fee Rs. 5 per late day · max 3 active loans per member
Errors: LibraryError("Unknown book" | "No copies available" | "Loan limit reached" | "No such loan")
```
Data in records, rules in the `Library` class. The three fields and the constants (`LOAN_DAYS`, `FEE_PER_DAY`, `MAX_LOANS`) are given; every method only reads or changes those three fields.
### 1.2 What you will write (all in `Practice.java`)
| ID | Level | Piece |
|---|---|---|
| L1-1 | 🟢 | `Book` record (second constructor, `withMoreCopies`) |
| L1-2 | 🟢 | `addBook`, `find(text)` (title search ignoring capitals) |
| L1-3 | 🟢 | `availableCopies(isbn)` |
| L2-1 | 🟡 | `checkout(isbn, member, dateText)` with all rules |
| L2-2 | 🟡 | `returnBook(isbn, member, dateText)` returns the late fee |
| L2-3 | 🟡 | `save(path)` and `Library.load(path)` (one text line per fact) |
| L3-1 | 🔴 | `overdueReport(todayText)` |
| L3-2 | 🔴 | `popularBooks(n)` |
Stretch (not auto-checked): a `Scanner` menu (like Day 7) around the library, a `Member` record, or logging every checkout with `java.util.logging`.
### 1.3 Days between two dates
```java
long days = ChronoUnit.DAYS.between(LocalDate.parse("2026-11-01"), LocalDate.parse("2026-11-20"));   // 19
long late = Math.max(0, days - 14);                                                                  // never negative
int fee = (int) late * 5;                                                                            // 25
```
`LocalDate.parse` understands the text `YYYY-MM-DD` (Day 18). `ChronoUnit.DAYS.between(from, to)` returns a `long`, so cast with `(int)` when you need an `int`.
### 1.4 Rules as exceptions, checked in a fixed order
```java
if (!books.containsKey(isbn)) throw new LibraryError("Unknown book");
if (availableCopies(isbn) < 1) throw new LibraryError("No copies available");
```
Check the rules **before** changing anything, so a failed checkout leaves the library exactly as it was. `LibraryError extends RuntimeException` (Day 17), so callers are not forced to catch it.
### 1.5 Persistence: one text line per fact
```java
List<String> lines = new ArrayList<>();
lines.add("BOOK|" + book.isbn() + "|" + book.title() + "|" + book.author() + "|" + book.copies());
Files.write(path, lines);                              // UTF-8, one line each
...
for (String line : Files.readAllLines(path)) {
    String[] part = line.split("\\|");                 // | is special in regex, so write \\|
    if (part[0].equals("BOOK")) { /* new Book(part[1], part[2], part[3], Integer.parseInt(part[4])) */ }
}
```
A `switch` on `part[0]` (`case "BOOK" -> ...`) reads even better. The **first piece names the kind of line**; this is how real log and data files work. `save` and `load` must be exact opposites. Limit: a title may not contain `|`. The checker writes into a **temporary folder that it deletes afterwards**, so you can run `Practice.java` again and again.
### 1.6 Sorting by two things
```java
ranked.sort(Comparator.comparing((Map.Entry<String, Integer> e) -> e.getValue()).reversed()   // most borrowed first
        .thenComparing(e -> books.get(e.getKey()).title()));                                  // ties: title A-Z
```
For top-N, sort first, then take items until you have `n` of them.
### 1.7 Design tips
- One method = one job. `checkout` should call `availableCopies` instead of repeating its code.
- Build from the top (L1 → L3): every piece you finish is a tool for the next one.
- Records never change: to "add copies" you build a **new** `Book` (`withMoreCopies`) and `put` it in the map.
## 2. Code along (30 min)  `Examples.java`
A short guided tour of the finished idea, for a **bike-rental shop**: records, a rules class, a custom exception, `save`/`load` to a temp folder and fees from dates. Read it, type it, run it with `java Examples.java`, then build your library.
## 3. Common mistakes
- Changing the library before all rules are checked (a failed checkout must change nothing).
- Removing from a list inside a for-each and continuing the loop (`ConcurrentModificationException`): `return` right after `remove`, as the solution does.
- `line.split("|")` instead of `line.split("\\|")`: `|` means "or" in a regex and the line is cut after every character.
- Comparing dates as plain text, or forgetting `Integer.parseInt` for the copies.
- Using `==` to compare member names or ISBNs: use `.equals`.
- Forgetting `throws IOException` on a method that calls `Files.write` or `Files.readAllLines`.
## 4. Today's tasks  `Practice.java`
Fewer but bigger exercises: some tasks fill in a whole method body, some a small record.
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `Book` record, `addBook` + `find`, `availableCopies` |
| L2-1 … L2-3 | 🟡 Intermediate | `checkout` rules, `returnBook` with late fee, `save` and `load` |
| L3-1, L3-2 | 🔴 Challenge | `overdueReport`, `popularBooks` |
Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.
## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Read the three fields at the top of <code>Library</code>: <code>books</code>, <code>loans</code>, <code>checkoutCounts</code>. Every method only reads or changes those. Solve the small ones first; <code>checkout</code> reuses <code>availableCopies</code>.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Available = <code>books.get(isbn).copies()</code> minus the number of loans with that isbn. Late days = <code>ChronoUnit.DAYS.between(out, back) - 14</code>, never below 0. Counting: <code>checkoutCounts.merge(isbn, 1, Integer::sum)</code>. Save: build a <code>List&lt;String&gt;</code> and call <code>Files.write(path, lines)</code>. Load: <code>new Library()</code>, then fill its fields from each line. Overdue line: <code>member + ": " + title + " (" + late + " days late)"</code>, then <code>Collections.sort</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day21_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>
## 6. Quiz — Week-3 review (closed book, 20 min) - answers in `java/solutions/day21_answers.md`
1. What does `Files.writeString(path, "Hi")` do when the file already exists? How do you add to the end instead?
2. Why name the charset (UTF-8) when you read or write text, and which `Files` methods already use it?
3. What type does `Files.readAllLines(path)` return, and what type is each piece of `line.split(",")`? How do you get a number from it?
4. Why is `line.split(",")` risky for real CSV files?
5. In what order do `try`, `catch` and `finally` run, and when does `finally` NOT run its block?
6. Why is `catch (Exception e) { }` with an empty block bad?
7. Give one checked and one unchecked exception. What is the difference for the caller?
8. What does try-with-resources do for you?
9. What is `this`?
10. What is risky about `static List<String> items = new ArrayList<>();` inside a `Cart` class?
11. What does `super(...)` do?
12. Which two methods must agree so a `HashSet` treats two objects as the same, and which interface makes objects sortable?
13. What is the difference between a `static` method and an instance method?
14. Which methods does a `record` generate for you?
15. "IS-A" or "HAS-A": which one means inheritance?
**Scoring:** 13-15 great · 10-12 good · fewer than 10 → redo the Day 15-20 level-1 tasks tomorrow (20 min).
## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5), then the **Weekly Review** sheet: easiest/hardest this week, which 3 concepts you still confuse, hours planned vs actual.
- Add **one** error you hit today to the **Bug Journal** sheet.
- **Week 4 plan:** generics/`Optional`/iterators → regex and clean code → JUnit and Git → collections + `Collectors` → streams for reporting → HTTP + JSON → JDBC + SQL → capstone → REST API + final exam.
### ✅ Week-3 checklist
- [ ] I read and write text and CSV/JSON-style files confidently
- [ ] I handle errors with specific `catch` blocks, custom exceptions and try-with-resources
- [ ] I know packages, imports and `java.time`
- [ ] I can design 2-3 cooperating classes with `private` fields and rules inside
- [ ] My Library passes every check in `Practice.java`
