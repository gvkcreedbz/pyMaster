/* Day 25 - Practice: collections and Collectors on the sales file.
 *
 * Run:  java Practice.java
 * Data: ../../datasets/sales.csv  (order_id, order_date, region, category, product,
 *       quantity, unit_price, discount_pct, payment_method)
 * Rule of the day: no hand-written counting loops - let groupingBy and the other Collectors do it.
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Practice {

    // One row of the sales file (already written for you).
    record Sale(String orderId, String orderDate, String region, String category, String product,
                int quantity, int unitPrice, int discountPct, String paymentMethod) {
        double revenue() {
            return quantity * unitPrice * (1 - discountPct / 100.0);
        }
    }

    // Helper (already written for you): round to 2 decimal places.
    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    // ---------------------------------------------------------------------------
    // L1-1 | celsiusToFahrenheit   (Level 1 - Beginner)
    // Turn a list of Celsius temperatures into a list of Fahrenheit ones (F = C * 9 / 5 + 32).
    // Use a stream with map - no for loop.
    //   celsiusToFahrenheit([0.0, 100.0]) -> [32.0, 212.0]
    // ---------------------------------------------------------------------------
    static List<Double> celsiusToFahrenheit(List<Double> temps) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | aboveAverage   (Level 1 - Beginner)
    // Return the numbers that are strictly greater than the average of the list (keep the order).
    //   aboveAverage([1, 2, 3, 10]) -> [10]        (the average is 4)
    //   aboveAverage([5, 5, 5])     -> []
    // Hint: work out the average first (mapToInt(...).average()), then filter.
    // ---------------------------------------------------------------------------
    static List<Integer> aboveAverage(List<Integer> values) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | loadSales   (Level 1 - Beginner)
    // Read the sales CSV at `path` into a List<Sale> in file order. Skip the header line and
    // blank lines. Columns: order_id, order_date, region, category, product, quantity,
    // unit_price, discount_pct, payment_method (convert the three numbers with Integer.parseInt).
    // ---------------------------------------------------------------------------
    static List<Sale> loadSales(Path path) throws IOException {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | filterOrders   (Level 2 - Intermediate)
    // Return the sales of the given region whose quantity is at least minQuantity (file order).
    //   filterOrders(sales, "West", 5) -> the 19 big orders of the West
    // ---------------------------------------------------------------------------
    static List<Sale> filterOrders(List<Sale> sales, String region, int minQuantity) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | countByRegion   (Level 2 - Intermediate)
    // How many orders did each region get?  Return a Map region -> number of orders
    // (a TreeMap, so the regions are A-Z).   e.g. {East=84, North=70, ...}
    // Hint: groupingBy(Sale::region, TreeMap::new, counting())
    // ---------------------------------------------------------------------------
    static Map<String, Long> countByRegion(List<Sale> sales) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | averageQuantityByCategory   (Level 2 - Intermediate)
    // The average quantity per order for each category, rounded to 2 decimals (use round2).
    //   e.g. {Electronics=2.82, Fashion=2.98, ...}
    // Hint: groupingBy + averagingDouble, then round the values at the END.
    // ---------------------------------------------------------------------------
    static Map<String, Double> averageQuantityByCategory(List<Sale> sales) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | revenueByRegion   (Level 3 - Challenge)
    // Total revenue per region (Sale.revenue()), each total rounded to 2 decimals (round2).
    //   e.g. {East=335268.6, North=300446.25, South=348849.7, West=458677.0}
    // Hint: groupingBy + summingDouble, round at the END.
    // ---------------------------------------------------------------------------
    static Map<String, Double> revenueByRegion(List<Sale> sales) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | monthlyRevenue   (Level 3 - Challenge)
    // Revenue per calendar month: keys like "2026-01" (the first 7 characters of order_date),
    // values rounded to 2 decimals, months in order (TreeMap).
    // ---------------------------------------------------------------------------
    static Map<String, Double> monthlyRevenue(List<Sale> sales) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-3 | topProducts   (Level 3 - Challenge)
    // The names of the n products with the highest TOTAL revenue, best first.
    // If two products have the same total, the name A-Z comes first.
    // Hint: build a Map product -> total, then sort its entrySet() (entry.getValue() is the total)
    // and limit(n).
    // ---------------------------------------------------------------------------
    static List<String> topProducts(List<Sale> sales, int n) {
        // TODO: write your code here
        return null;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    // The Checker's lambdas cannot throw IOException, so attempt(...) wraps it for the tests.
    interface Action<T> {
        T run() throws Exception;
    }

    static <T> T attempt(Action<T> action) {
        try {
            return action.run();
        } catch (RuntimeException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException(e.getClass().getSimpleName() + ": " + e.getMessage(), e);
        }
    }

    public static void main(String[] args) throws IOException {
        Path salesPath = Path.of("../../datasets/sales.csv");
        System.out.println("--- Day 25 checks ---");
        Checker.check("L1-1 celsiusToFahrenheit", () -> celsiusToFahrenheit(List.of(0.0, 100.0, -40.0)),
                List.of(32.0, 212.0, -40.0));
        Checker.check("L1-2 aboveAverage", () -> List.of(aboveAverage(List.of(1, 2, 3, 10)), aboveAverage(List.of(5, 5, 5))),
                List.of(List.of(10), List.of()));
        Checker.check("L1-3 loadSales (rows, first and last order)", () -> attempt(() -> {
            List<Sale> s = loadSales(salesPath);
            return List.of(s.size(), s.get(0).orderId(), s.get(0).unitPrice(), s.get(299).orderId());
        }), List.of(300, "ORD1108", 3499, "ORD1195"));
        List<Sale> sales = attempt(() -> loadSalesForChecks(salesPath));
        Checker.check("L2-1 filterOrders count", () -> filterOrders(sales, "West", 5).size(), 19);
        Checker.check("L2-1 filterOrders only matching rows", () -> {
            List<Sale> west = filterOrders(sales, "West", 5);
            return west.stream().allMatch(s -> s.region().equals("West") && s.quantity() >= 5);
        }, true);
        Checker.check("L2-2 countByRegion", () -> countByRegion(sales), Map.of("East", 84L, "North", 70L, "South", 71L, "West", 75L));
        Checker.check("L2-3 averageQuantityByCategory", () -> averageQuantityByCategory(sales),
                Map.of("Electronics", 2.82, "Fashion", 2.98, "Grocery", 2.98, "Home", 3.01));
        Checker.check("L3-1 revenueByRegion", () -> revenueByRegion(sales),
                Map.of("East", 335268.6, "North", 300446.25, "South", 348849.7, "West", 458677.0));
        Checker.check("L3-2 monthlyRevenue", () -> monthlyRevenue(sales), Map.of(
                "2026-01", 102041.05, "2026-02", 128597.5, "2026-03", 174010.9, "2026-04", 183688.4, "2026-05", 174384.85,
                "2026-06", 198503.1, "2026-07", 82858.25, "2026-08", 135710.75, "2026-09", 125223.0, "2026-10", 138223.75));
        Checker.check("L3-3 topProducts", () -> topProducts(sales, 3), List.of("Smartwatch", "Air Fryer", "Running Shoes"));
        List<Sale> tie = List.of(
                new Sale("1", "2026-01-01", "East", "Home", "Lamp", 1, 100, 0, "UPI"),
                new Sale("2", "2026-01-02", "East", "Home", "Bowl", 1, 100, 0, "UPI"),
                new Sale("3", "2026-01-03", "East", "Home", "Cup", 2, 100, 0, "UPI"));
        Checker.check("L3-3 topProducts (tie -> name A-Z)", () -> topProducts(tie, 3), List.of("Cup", "Bowl", "Lamp"));
        Checker.done();
    }

    static List<Sale> loadSalesForChecks(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        List<Sale> sales = new ArrayList<>();
        for (String line : lines.subList(1, lines.size())) {
            String[] c = line.split(",", -1);
            sales.add(new Sale(c[0], c[1], c[2], c[3], c[4], Integer.parseInt(c[5]),
                    Integer.parseInt(c[6]), Integer.parseInt(c[7]), c[8]));
        }
        return sales;
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
