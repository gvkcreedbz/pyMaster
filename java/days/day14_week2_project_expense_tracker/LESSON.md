# Day 14 — 🏆 Week 2 Project: Expense Tracker (and Week-2 Review)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Combine records, lists, maps, streams and formatting in one useful program; then test Weeks 1-2 | Intermediate |

## 🌍 Real-world scenario & trend
**A personal-finance app** (Walnut, Splitwise, Money Manager, Google Pay "Spends"). Behind the pretty charts is exactly this: a list of transactions, plus methods to total them, filter them, group them by month or category and compare them with a budget.

**Why Java?** Banks and fintech back-ends are largely Java: a small, well-typed `record Expense`, collections and streams are the daily tools there. The methods you write today are the real logic of a budget feature, and in Week 3 the data will come from files instead of memory. *Coming from Python?* Your list of dicts is now a `List<Expense>`, and the `f"{x:>9,.2f}"` formatting is `String.format("%,9.2f", x)`.

## ⏰ Time plan
| Min | Activity |
|---|---|
| 0-10 | Warm-up: redo any 1 failed exercise from Days 8-13 |
| 10-25 | Read this page + run `Examples.java` |
| 25-95 | Build the tracker (`Practice.java`, L1 → L2 → L3) |
| 95-115 | **Week-2 quiz** (closed book) |
| 115-120 | Tracker + weekly reflection |

## 1. Concepts (with tiny code)

### 1.1 The data model
One expense is a **record**; the tracker's whole state is a **list of records**. Every method receives the list it works on, so there are no global variables.
```java
record Expense(String date, String category, double amount, String note) {}
List<Expense> expenses = new ArrayList<>();
expenses.add(new Expense("2026-11-16", "Food", 250, "Lunch"));
```

### 1.2 What you will write (all in `Practice.java`)
| ID | Level | Methods | What they do |
|---|---|---|---|
| L1-1 | 🟢 | `addExpense` (two overloads), `totalSpent` | Add an expense (reject amount ≤ 0), sum of all amounts |
| L1-2 | 🟢 | `formatExpense(e)` | One aligned line of text |
| L2-1 | 🟡 | `totalsByCategory`, `filterExpenses` | `{category: total}`, matching expenses |
| L2-2 | 🟡 | `monthlyTotals`, `topNotes` | `{"2026-11": total}`, notes of the biggest spends |
| L3-1 | 🔴 | `budgetReport` | Lines with spent / budget / percent / status |
| L3-2 | 🔴 | `runTracker()` | The interactive menu (Add / List / Summary / Quit) |

Play it for real: `java Practice.java play`.

### 1.3 Lining up money with `String.format`
```java
String.format(Locale.US, "%-10s|", "Food");          // "Food      |"  (- = left-aligned, 10 wide)
String.format(Locale.US, "Rs. %,9.2f", 250.0);       // "Rs.    250.00"  (, = thousands comma, 9 wide, 2 decimals)
String.format(Locale.US, "%.1f%%", 90.0);            // "90.0%"          (%% prints a real percent sign)
```
`Locale.US` makes the decimal point and commas identical on every computer (some countries print `250,00`).

### 1.4 Grouping and counting with a Map
```java
Map<String, Double> totals = new TreeMap<>();            // TreeMap keeps the keys sorted
for (Expense e : expenses) {
    totals.merge(e.category(), e.amount(), Double::sum);   // add to the old total, or start a new one
}
```
The stream version: `expenses.stream().collect(Collectors.groupingBy(Expense::category, Collectors.summingDouble(Expense::amount)))`. For months use `e.date().substring(0, 7)` as the key.

### 1.5 Optional filters, overloads and sorting
```java
// category == null means "any category"
expenses.stream().filter(e -> category == null || e.category().equals(category)).toList();
// a short version of a method that calls the long one (overloading, Day 11)
static boolean addExpense(List<Expense> list, String d, String c, double a) { return addExpense(list, d, c, a, ""); }
// biggest first, ties by date
expenses.stream().sorted(Comparator.comparingDouble(Expense::amount).reversed().thenComparing(Expense::date))
```

### 1.6 A menu loop with `Scanner`
```java
Scanner in = new Scanner(System.in);
while (true) {
    System.out.print("Choose: ");
    String choice = in.nextLine().trim();      // always nextLine(): no leftover-newline surprises
    switch (choice) {
        case "1" -> System.out.println("add...");
        case "4" -> { System.out.println("Goodbye!"); return; }
        default -> System.out.println("Invalid option");
    }
}
```
The auto-checker feeds your program fake keyboard input, exactly like Day 7's ATM.

### 1.7 Design tips
- One method = one job. `runTracker` should call `addExpense`, `formatExpense`, `totalsByCategory` and `totalSpent` instead of repeating their code.
- Build the pieces from the top (L1 → L3): every piece you finish is a tool for the next one.
- Money as `double` is fine for learning (see Day 3 for `BigDecimal`, which real banks use).

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run. The last section is a small menu: when it asks `Choose:`, type `1` and answer the questions, then `2` to list, then `4` to quit.

## 3. Common mistakes
- Using `==` to compare the menu choice (`choice == "1"`): use `.equals` or a `switch`.
- Using `nextDouble()` and then `nextLine()`: the leftover new line gives you an empty text. Use `nextLine()` + `Double.parseDouble`.
- `Map.of(...)` / `List.of(...)` cannot be changed: use `new TreeMap<>()` / `new ArrayList<>()` for data you add to.
- Forgetting `Locale.US`: numbers print as `250,00` on some computers and the check fails.
- Putting the same logic in two places: reuse your own methods.

## 4. Today's tasks  `Practice.java`
Fewer but bigger exercises today: each one asks for one or two small methods.

| ID | Level | Task |
|---|---|---|
| L1-1, L1-2 | 🟢 Beginner | Add expenses and total them; format one aligned line |
| L2-1, L2-2 | 🟡 Intermediate | Totals by category, filters, monthly totals, top spends |
| L3-1, L3-2 | 🔴 Challenge | A budget report; the interactive tracker menu |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Pass the list into every method (no global variables). Each method does <em>one</em> job. Solve the small ones first; the menu only glues them together.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Format line: <code>String.format(Locale.US, "%s | %-10s | Rs. %,9.2f | %s", ...)</code>. Totals: <code>map.merge(key, amount, Double::sum)</code>. Budget status: <code>OVER</code> if spent &gt; limit, else <code>WARN</code> if percent &gt;= 80, else <code>OK</code>; lines for sorted categories via <code>new TreeMap&lt;&gt;(budgets).keySet()</code>. In <code>runTracker</code> reuse <code>addExpense</code>, <code>formatExpense</code>, <code>totalsByCategory</code>, <code>totalSpent</code>, and read everything with <code>in.nextLine()</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day14_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz — Week-2 review (closed book, 20 min) - answers in `java/solutions/day14_answers.md`
1. `List<Integer> a = new ArrayList<>(List.of(1, 2)); List<Integer> b = a; b.add(3);` What is `a` now?
2. What does `List.of(1, 2).add(3)` do?
3. Write the one-line `HashMap` counting pattern for a word `w` (use `merge`).
4. What does `IntStream.rangeClosed(1, 5).filter(x -> x % 2 == 1).sum()` give?
5. Why is `if (cmd == "quit")` a bug waiting to happen? What should you write?
6. What does `String.format(Locale.US, "%-6s|", "Food")` print?
7. How do you sort expenses biggest amount first, ties by date?
8. Name three things a `record` gives you for free.

**Scoring:** 7-8 great · 5-6 good · fewer than 5 → spend 20 minutes tomorrow morning on the Day 8-13 level-1 tasks.

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5), then the **Weekly Review** sheet: what was easiest/hardest this week, which 3 concepts you still confuse, hours planned vs actual.
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: Week 3 starts with files: save and load text with `java.nio.file`, and analyse a real server log.

### ✅ Week-2 checklist
- [ ] I can pick between array / `List` / `Set` / `Map` for a problem
- [ ] I write overloaded methods and short, single-purpose methods
- [ ] I use lambdas, streams and `Comparator` comfortably
- [ ] I can navigate nested data made of records, lists and maps
- [ ] My tracker passes every check in `Practice.java`
