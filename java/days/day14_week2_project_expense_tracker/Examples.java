/* Day 14 - Code along: the building blocks of a personal-finance app (Walnut / Splitwise style).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * The last section is a tiny interactive menu: type 1, 2 or 4 (and follow the questions).
 */
import java.util.*;
import java.util.stream.*;

class Examples {
    // The data model: one expense = one record; the app's state = a List<Expense>.
    record Expense(String date, String category, double amount, String note) {}

    public static void main(String[] args) {
        // ---- 1. Build the state ----
        List<Expense> expenses = new ArrayList<>();
        add(expenses, "2026-11-02", "Food", 1500, "Groceries");
        add(expenses, "2026-11-09", "Food", 300, "Dinner");
        add(expenses, "2026-11-10", "Travel", 1200, "Cab");
        add(expenses, "2026-12-01", "Fun", 99.5, "Game");
        System.out.println(add(expenses, "2026-12-02", "Fun", -10, "Oops") + " (a negative amount is rejected)");
        System.out.println("Expenses stored: " + expenses.size());   // 4

        // ---- 2. Total, and one tidy line per expense ----
        System.out.println("Total: " + total(expenses));              // 3099.5
        for (Expense e : expenses) {
            System.out.println(line(e));
        }

        // ---- 3. Group by category (two ways) ----
        Map<String, Double> byCategory = new TreeMap<>();
        for (Expense e : expenses) {
            byCategory.merge(e.category(), e.amount(), Double::sum);   // add to the old total, or start a new one
        }
        System.out.println(byCategory);   // {Food=1800.0, Fun=99.5, Travel=1200.0}

        Map<String, Double> sameThing = expenses.stream().collect(
                Collectors.groupingBy(Expense::category, TreeMap::new, Collectors.summingDouble(Expense::amount)));
        System.out.println(sameThing.equals(byCategory));   // true

        // ---- 4. Filter and rank ----
        List<String> bigOnes = expenses.stream().filter(e -> e.amount() >= 1000).map(Expense::note).toList();
        System.out.println("Big spends: " + bigOnes);         // [Groceries, Cab]
        Expense biggest = expenses.stream().max(Comparator.comparingDouble(Expense::amount)).get();
        System.out.println("Biggest: " + biggest.note() + " (" + biggest.amount() + ")");   // Groceries (1500.0)

        // ---- 5. Months: date.substring(0, 7) gives "2026-11" ----
        Map<String, Double> months = new TreeMap<>();
        for (Expense e : expenses) {
            months.merge(e.date().substring(0, 7), e.amount(), Double::sum);
        }
        System.out.println(months);   // {2026-11=3000.0, 2026-12=99.5}

        // ---- 6. Budget check: spent vs limit ----
        double limit = 2000;
        double spent = byCategory.get("Food");
        double percent = spent / limit * 100;
        String status = spent > limit ? "OVER" : percent >= 80 ? "WARN" : "OK";
        System.out.println(String.format(Locale.US, "Food: spent %.2f of %.2f (%.1f%%) %s", spent, limit, percent, status));

        // ---- 7. A tiny menu loop (reads from the keyboard) ----
        Scanner in = new Scanner(System.in);
        while (true) {
            System.out.println("1) Add  2) List  4) Quit");
            System.out.print("Choose: ");
            if (!in.hasNextLine()) {
                break;                       // no more input: stop politely
            }
            String choice = in.nextLine().trim();
            if (choice.equals("1")) {
                System.out.print("Date: ");
                String date = in.nextLine();
                System.out.print("Category: ");
                String category = in.nextLine();
                System.out.print("Amount: ");
                double amount = Double.parseDouble(in.nextLine().trim());
                System.out.print("Note: ");
                String note = in.nextLine();
                System.out.println(add(expenses, date, category, amount, note) ? "Added" : "Invalid amount");
            } else if (choice.equals("2")) {
                expenses.forEach(e -> System.out.println(line(e)));
            } else if (choice.equals("4")) {
                System.out.println("Goodbye!");
                break;
            } else {
                System.out.println("Invalid option");
            }
        }
    }

    // Each function does ONE job and receives the list it works on (no global variables).
    static boolean add(List<Expense> expenses, String date, String category, double amount, String note) {
        if (amount <= 0) {
            return false;
        }
        expenses.add(new Expense(date, category, amount, note));
        return true;
    }

    static double total(List<Expense> expenses) {
        return expenses.stream().mapToDouble(Expense::amount).sum();
    }

    static String line(Expense e) {
        // %-10s = text, left-aligned, 10 wide.  %,9.2f = 2 decimals, thousands comma, 9 wide.
        return String.format(Locale.US, "%s | %-10s | Rs. %,9.2f | %s", e.date(), e.category(), e.amount(), e.note());
    }
}
