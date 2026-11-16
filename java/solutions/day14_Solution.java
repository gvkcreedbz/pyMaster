// SOLUTION FILE - try the hint ladder first!
/* Day 14 - Week 2 Project: Expense Tracker.
 *
 * Run the checks:      java Practice.java
 * Play your tracker:   java Practice.java play
 */
import java.util.*;
import java.util.stream.*;

class Practice {

    // The data model: one expense = one record. The tracker's state = a List<Expense>.
    record Expense(String date, String category, double amount, String note) {}

    // ---------------------------------------------------------------------------
    // L1-1 | Add and total   (Level 1 - Beginner)
    // addExpense(expenses, date, category, amount, note): add a new Expense to the list.
    //   If amount <= 0 do NOT add anything and return false. Otherwise add it and return true.
    // addExpense(expenses, date, category, amount): the same, but with an EMPTY note ("").
    //   (This is method overloading: reuse the 5-argument version.)
    // totalSpent(expenses): the sum of all amounts (0 for an empty list).
    // ---------------------------------------------------------------------------
    static boolean addExpense(List<Expense> expenses, String date, String category, double amount, String note) {
        // >>> SOLUTION stub: return false;
        if (amount <= 0) {
            return false;
        }
        expenses.add(new Expense(date, category, amount, note));
        return true;
        // <<< SOLUTION
    }

    static boolean addExpense(List<Expense> expenses, String date, String category, double amount) {
        // >>> SOLUTION stub: return false;
        return addExpense(expenses, date, category, amount, "");
        // <<< SOLUTION
    }

    static double totalSpent(List<Expense> expenses) {
        // >>> SOLUTION stub: return -1;
        return expenses.stream().mapToDouble(Expense::amount).sum();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | A tidy line   (Level 1 - Beginner)
    // formatExpense(e): return ONE aligned line:
    //   date | category (left-aligned, width 10) | Rs. amount (width 9, thousands comma, 2 decimals) | note
    //   -> "2026-11-16 | Food       | Rs.    250.00 | Lunch"
    // Hint: String.format(Locale.US, "%s | %-10s | Rs. %,9.2f | %s", ...)
    //   (Locale.US makes the numbers look the same on every computer.)
    // ---------------------------------------------------------------------------
    static String formatExpense(Expense e) {
        // >>> SOLUTION stub: return null;
        return String.format(Locale.US, "%s | %-10s | Rs. %,9.2f | %s", e.date(), e.category(), e.amount(), e.note());
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Group and filter   (Level 2 - Intermediate)
    // totalsByCategory(expenses): return a Map  category -> total amount.
    // filterExpenses(expenses, category, minAmount): return the expenses (original order)
    //   whose category equals `category` (any category when `category` is null)
    //   AND whose amount is >= minAmount.
    // ---------------------------------------------------------------------------
    static Map<String, Double> totalsByCategory(List<Expense> expenses) {
        // >>> SOLUTION stub: return null;
        return expenses.stream()
                .collect(Collectors.groupingBy(Expense::category, Collectors.summingDouble(Expense::amount)));
        // <<< SOLUTION
    }

    static List<Expense> filterExpenses(List<Expense> expenses, String category, double minAmount) {
        // >>> SOLUTION stub: return null;
        return expenses.stream()
                .filter(e -> category == null || e.category().equals(category))
                .filter(e -> e.amount() >= minAmount)
                .toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Months and top spends   (Level 2 - Intermediate)
    // monthlyTotals(expenses): return a Map "YYYY-MM" -> total. The date text looks like
    //   "2026-11-16" (hint: date.substring(0, 7)). Keys must be sorted (use a TreeMap).
    // topNotes(expenses, n): return the NOTES of the n biggest expenses, biggest amount
    //   first (equal amounts: earlier date first). Fewer than n expenses -> return them all.
    // ---------------------------------------------------------------------------
    static Map<String, Double> monthlyTotals(List<Expense> expenses) {
        // >>> SOLUTION stub: return null;
        Map<String, Double> totals = new TreeMap<>();
        for (Expense e : expenses) {
            totals.merge(e.date().substring(0, 7), e.amount(), Double::sum);
        }
        return totals;
        // <<< SOLUTION
    }

    static List<String> topNotes(List<Expense> expenses, int n) {
        // >>> SOLUTION stub: return null;
        return expenses.stream()
                .sorted(Comparator.comparingDouble(Expense::amount).reversed().thenComparing(Expense::date))
                .limit(n)
                .map(Expense::note)
                .toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Budget report   (Level 3 - Challenge)
    // budgets maps category -> limit, e.g. {Food=2000, Travel=1000}. Return a List of lines,
    // one per budget category, sorted A-Z by category, each formatted like:
    //   "Food: spent 1800.00 of 2000.00 (90.0%) WARN"
    // percent = spent / limit * 100 (1 decimal). Status: "OVER" if spent > limit, else
    // "WARN" if percent >= 80, else "OK". A category with no expenses has spent 0.
    // Expenses in categories that have no budget are ignored.
    // Hint: reuse totalsByCategory; String.format(Locale.US, "... %.2f ... %.1f%% ...", ...)
    // ---------------------------------------------------------------------------
    static List<String> budgetReport(List<Expense> expenses, Map<String, Double> budgets) {
        // >>> SOLUTION stub: return null;
        Map<String, Double> spentBy = totalsByCategory(expenses);
        List<String> lines = new ArrayList<>();
        for (String category : new TreeMap<>(budgets).keySet()) {
            double limit = budgets.get(category);
            double spent = spentBy.getOrDefault(category, 0.0);
            double percent = spent / limit * 100;
            String status = spent > limit ? "OVER" : percent >= 80 ? "WARN" : "OK";
            lines.add(String.format(Locale.US, "%s: spent %.2f of %.2f (%.1f%%) %s", category, spent, limit, percent, status));
        }
        return lines;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | The tracker program   (Level 3 - Challenge)
    // Keep a list of expenses and loop. Read EVERY answer with a Scanner on System.in
    // (use nextLine() each time). Each round:
    //   print "1) Add  2) List  3) Summary  4) Quit"   (println)
    //   print "Choose: "                                (print, no new line), read the choice
    //  "1": ask (with print) "Date (YYYY-MM-DD): ", "Category: ", "Amount: " (parse with
    //       Double.parseDouble), "Note: "; call addExpense; println "Added" or "Invalid amount"
    //  "2": no expenses -> println "No expenses yet"; else println formatExpense(e) for each
    //  "3": no expenses -> println "No expenses yet"; else for every category (A-Z) println
    //       "<category>: Rs. <total>" with the total as %,.2f, then "Total: Rs. <all>" (%,.2f)
    //  "4": println "Goodbye!" and return the list of expenses
    //  anything else: println "Invalid option"
    // Try it yourself:  java Practice.java play
    // ---------------------------------------------------------------------------
    static List<Expense> runTracker() {
        // >>> SOLUTION stub: return new ArrayList<>();
        List<Expense> expenses = new ArrayList<>();
        Scanner in = new Scanner(System.in);
        while (true) {
            System.out.println("1) Add  2) List  3) Summary  4) Quit");
            System.out.print("Choose: ");
            String choice = in.nextLine().trim();
            switch (choice) {
                case "1" -> {
                    System.out.print("Date (YYYY-MM-DD): ");
                    String date = in.nextLine();
                    System.out.print("Category: ");
                    String category = in.nextLine();
                    System.out.print("Amount: ");
                    double amount = Double.parseDouble(in.nextLine().trim());
                    System.out.print("Note: ");
                    String note = in.nextLine();
                    System.out.println(addExpense(expenses, date, category, amount, note) ? "Added" : "Invalid amount");
                }
                case "2" -> {
                    if (expenses.isEmpty()) {
                        System.out.println("No expenses yet");
                    }
                    for (Expense e : expenses) {
                        System.out.println(formatExpense(e));
                    }
                }
                case "3" -> {
                    if (expenses.isEmpty()) {
                        System.out.println("No expenses yet");
                    } else {
                        Map<String, Double> totals = new TreeMap<>(totalsByCategory(expenses));
                        totals.forEach((category, total) ->
                                System.out.println(String.format(Locale.US, "%s: Rs. %,.2f", category, total)));
                        System.out.println(String.format(Locale.US, "Total: Rs. %,.2f", totalSpent(expenses)));
                    }
                }
                case "4" -> {
                    System.out.println("Goodbye!");
                    return expenses;
                }
                default -> System.out.println("Invalid option");
            }
        }
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    // What a run of the tracker produced: the returned list and everything it printed.
    record Run(List<Expense> expenses, String output) {}

    static Run play(String keyboardInput) {
        List<List<Expense>> box = new ArrayList<>();
        String printed = Checker.printed(() -> box.add(Checker.withInput(keyboardInput, Practice::runTracker)));
        return new Run(box.get(0), printed);
    }

    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("play")) {
            runTracker();
            return;
        }
        List<Expense> sample = List.of(
                new Expense("2026-11-02", "Food", 1500.0, "Groceries"),
                new Expense("2026-11-09", "Food", 300.0, "Dinner"),
                new Expense("2026-11-10", "Travel", 1200.0, "Cab"),
                new Expense("2026-12-01", "Fun", 99.5, "Game"));

        System.out.println("--- Day 14 checks ---");
        Checker.check("L1-1 addExpense", () -> {
            List<Expense> list = new ArrayList<>();
            boolean first = addExpense(list, "2026-11-16", "Food", 250, "Lunch");
            boolean bad = addExpense(list, "2026-11-16", "Food", 0, "");
            boolean negative = addExpense(list, "2026-11-16", "Food", -3, "");
            boolean noNote = addExpense(list, "2026-11-17", "Travel", 40);
            return List.of(first, bad, negative, noNote, list.size(), list.get(0), list.get(1));
        }, List.of(true, false, false, true, 2, new Expense("2026-11-16", "Food", 250, "Lunch"),
                new Expense("2026-11-17", "Travel", 40, "")));
        Checker.check("L1-1 totalSpent", () -> List.of(totalSpent(sample), totalSpent(List.of())), List.of(3099.5, 0.0));
        Checker.check("L1-2 formatExpense", () -> formatExpense(new Expense("2026-11-16", "Food", 250, "Lunch")),
                "2026-11-16 | Food       | Rs.    250.00 | Lunch");
        Checker.check("L1-2 formatExpense thousands", () -> formatExpense(new Expense("2026-11-02", "Travel", 12345.5, "Flight")),
                "2026-11-02 | Travel     | Rs. 12,345.50 | Flight");
        Checker.check("L2-1 totalsByCategory", () -> totalsByCategory(sample),
                Map.of("Food", 1800.0, "Travel", 1200.0, "Fun", 99.5));
        Checker.check("L2-1 filter by category", () -> filterExpenses(sample, "Food", 0).stream().map(Expense::note).toList(),
                List.of("Groceries", "Dinner"));
        Checker.check("L2-1 filter by amount", () -> filterExpenses(sample, null, 1000).stream().map(Expense::note).toList(),
                List.of("Groceries", "Cab"));
        Checker.check("L2-1 filter both", () -> filterExpenses(sample, "Food", 1000).stream().map(Expense::note).toList(),
                List.of("Groceries"));
        Checker.check("L2-2 monthlyTotals", () -> monthlyTotals(sample), Map.of("2026-11", 3000.0, "2026-12", 99.5));
        Checker.check("L2-2 monthlyTotals sorted keys", () -> new ArrayList<>(monthlyTotals(sample).keySet()),
                List.of("2026-11", "2026-12"));
        Checker.check("L2-2 topNotes", () -> List.of(topNotes(sample, 2), topNotes(sample, 10)),
                List.of(List.of("Groceries", "Cab"), List.of("Groceries", "Cab", "Dinner", "Game")));
        Checker.check("L2-2 topNotes tie", () -> topNotes(List.of(new Expense("2026-02-01", "A", 50, "later"),
                new Expense("2026-01-01", "A", 50, "earlier")), 1), List.of("earlier"));
        Checker.check("L3-1 budgetReport", () -> budgetReport(sample,
                        Map.of("Travel", 1000.0, "Food", 2000.0, "Movies", 500.0, "Fun", 100.0)),
                List.of("Food: spent 1800.00 of 2000.00 (90.0%) WARN",
                        "Fun: spent 99.50 of 100.00 (99.5%) WARN",
                        "Movies: spent 0.00 of 500.00 (0.0%) OK",
                        "Travel: spent 1200.00 of 1000.00 (120.0%) OVER"));
        String session = "1\n2026-11-16\nFood\n250\nLunch\n1\n2026-11-17\nTravel\n-5\nx\n"
                + "1\n2026-11-17\nTravel\n120.5\nMetro\n2\n3\n4\n";
        Checker.check("L3-2 tracker stores 2 expenses", () -> {
            Run run = play(session);
            return List.of(run.expenses().size(), totalSpent(run.expenses()));
        }, List.of(2, 370.5));
        Checker.check("L3-2 tracker messages", () -> {
            String out = play(session).output();
            return List.of(out.contains("Added"), out.contains("Invalid amount"), out.contains("Goodbye!"));
        }, List.of(true, true, true));
        Checker.check("L3-2 tracker list + summary", () -> {
            String out = play(session).output();
            return Stream.of("2026-11-16 | Food       | Rs.    250.00 | Lunch", "Food: Rs. 250.00",
                    "Travel: Rs. 120.50", "Total: Rs. 370.50").allMatch(out::contains);
        }, true);
        Checker.check("L3-2 tracker empty state", () -> {
            Run run = play("2\n3\n9\n4\n");
            return List.of(run.expenses().size(), run.output().split("No expenses yet", -1).length - 1,
                    run.output().contains("Invalid option"));
        }, List.of(0, 2, true));
        Checker.done();
    }
}

// ==== CHECKER-BEGIN (generated by _dev_tools/java_sync.py - do not edit) ====
final class Checker {
    private static int passed = 0, total = 0;

    /** Compare what your code produced with what we expect and print [PASS] / [FAIL]. */
    static void check(String name, java.util.function.Supplier<Object> fn, Object want) {
        Object got;
        boolean good;
        try {
            got = fn.get();
            good = same(got, want);
        } catch (Throwable e) {              // your code crashed: show why instead of stopping
            got = e.getClass().getSimpleName() + ": " + e.getMessage();
            good = false;
        }
        total++;
        if (good) passed++;
        System.out.println("[" + (good ? "PASS" : "FAIL") + "] " + name
                + (good ? "" : "  (got " + show(got) + ", want " + show(want) + ")"));
    }

    /** Everything that run() prints, as one string (new lines normalised to \n). */
    static String printed(Runnable run) {
        java.io.PrintStream old = System.out;
        java.io.ByteArrayOutputStream buf = new java.io.ByteArrayOutputStream();
        System.setOut(new java.io.PrintStream(buf, true, java.nio.charset.StandardCharsets.UTF_8));
        try {
            run.run();
        } finally {
            System.setOut(old);
        }
        return buf.toString(java.nio.charset.StandardCharsets.UTF_8).replace("\r\n", "\n");
    }

    /** Run fn while System.in contains text (to test code that uses Scanner). */
    static <T> T withInput(String text, java.util.function.Supplier<T> fn) {
        java.io.InputStream old = System.in;
        System.setIn(new java.io.ByteArrayInputStream(text.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        try {
            return fn.get();
        } finally {
            System.setIn(old);
        }
    }

    /** Print the final score line (the portal reads this). */
    static void done() {
        System.out.println("\nScore: " + passed + "/" + total + " checks passed");
    }

    private static boolean same(Object got, Object want) {
        if (got instanceof Number g && want instanceof Number w) {
            boolean floating = got instanceof Double || got instanceof Float || want instanceof Double || want instanceof Float;
            return floating ? Math.abs(g.doubleValue() - w.doubleValue()) < 1e-6 : g.longValue() == w.longValue();
        }
        return java.util.Objects.deepEquals(got, want);
    }

    private static String show(Object o) {
        if (o == null) return "null";
        if (o instanceof String s) {
            return "\"" + s.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t").replace("\"", "\\\"") + "\"";
        }
        if (o instanceof Object[] a) return java.util.Arrays.deepToString(a);
        if (o instanceof int[] a) return java.util.Arrays.toString(a);
        if (o instanceof long[] a) return java.util.Arrays.toString(a);
        if (o instanceof double[] a) return java.util.Arrays.toString(a);
        if (o instanceof char[] a) return java.util.Arrays.toString(a);
        if (o instanceof boolean[] a) return java.util.Arrays.toString(a);
        return String.valueOf(o);
    }
}
// ==== CHECKER-END ====
