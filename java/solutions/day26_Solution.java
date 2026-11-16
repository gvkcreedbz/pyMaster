// SOLUTION FILE - try the hint ladder first!
/* Day 26 - Practice: cleaning a messy export, summaries and text bar charts.
 *
 * Run:  java Practice.java
 * Data: ../../datasets/sales_messy.csv - blank cells, duplicate rows, " SOUTH " style text and
 *       prices like "1,999". Revenue of a sale = quantity * unitPrice * (1 - discountPct / 100.0).
 * Already written for you: Sale, round2, splitCsvLine (the quote-aware splitter from Day 16)
 * and readRows (the CSV file as a list of maps: column name -> text, nothing trimmed).
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Practice {

    // A CLEAN sale (already written for you).
    record Sale(String orderId, String orderDate, String region, String category, String product,
                int quantity, int unitPrice, int discountPct, String paymentMethod) {
        double revenue() {
            return quantity * unitPrice * (1 - discountPct / 100.0);
        }
    }

    // The answer shape for L2-3.
    record Summary(long orders, double revenue) {}

    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    // Quote-aware split of one CSV line: a cell like "1,999" stays ONE cell (the quotes are removed).
    static List<String> splitCsvLine(String line) {
        List<String> cells = new ArrayList<>();
        StringBuilder cell = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (inQuotes) {
                if (c == '"' && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                    cell.append('"');
                    i++;
                } else if (c == '"') {
                    inQuotes = false;
                } else {
                    cell.append(c);
                }
            } else if (c == '"') {
                inQuotes = true;
            } else if (c == ',') {
                cells.add(cell.toString());
                cell.setLength(0);
            } else {
                cell.append(c);
            }
        }
        cells.add(cell.toString());
        return cells;
    }

    // The file as rows: column name -> raw text (spaces and blanks are kept as they are).
    static List<Map<String, String>> readRows(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        List<String> header = splitCsvLine(lines.get(0));
        List<Map<String, String>> rows = new ArrayList<>();
        for (String line : lines.subList(1, lines.size())) {
            if (line.isBlank()) {
                continue;
            }
            List<String> cells = splitCsvLine(line);
            Map<String, String> row = new LinkedHashMap<>();
            for (int c = 0; c < header.size(); c++) {
                row.put(header.get(c), c < cells.size() ? cells.get(c) : "");
            }
            rows.add(row);
        }
        return rows;
    }

    // ---------------------------------------------------------------------------
    // L1-1 | stripAndTitle   (Level 1 - Beginner)
    // Clean ONE word of text: remove the spaces around it, then make the first letter
    // a capital and the rest small.     " sOUTH " -> "South"     "GROCERY " -> "Grocery"
    // (An empty text stays empty.)
    // ---------------------------------------------------------------------------
    static String stripAndTitle(String text) {
        // >>> SOLUTION stub: return null;
        String s = text.strip();
        if (s.isEmpty()) {
            return s;
        }
        return Character.toUpperCase(s.charAt(0)) + s.substring(1).toLowerCase();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | countMissing   (Level 1 - Beginner)
    // Count the blank cells (isBlank) per column. Return a Map column -> count that contains
    // ONLY the columns that have at least one blank cell.
    //   for sales_messy.csv -> {quantity=6, discount_pct=10}
    // ---------------------------------------------------------------------------
    static Map<String, Integer> countMissing(List<Map<String, String>> rows) {
        // >>> SOLUTION stub: return null;
        Map<String, Integer> missing = new LinkedHashMap<>();
        for (Map<String, String> row : rows) {
            for (Map.Entry<String, String> cell : row.entrySet()) {
                if (cell.getValue().isBlank()) {
                    missing.merge(cell.getKey(), 1, Integer::sum);
                }
            }
        }
        return missing;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | dropDupes   (Level 1 - Beginner)
    // Return the rows without exact duplicates (all cells equal), keeping the FIRST copy and
    // the original order. Hint: a stream has a one-word step for this.
    // ---------------------------------------------------------------------------
    static List<Map<String, String>> dropDupes(List<Map<String, String>> rows) {
        // >>> SOLUTION stub: return null;
        return rows.stream().distinct().toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | fixPrice   (Level 2 - Intermediate)
    // A price written as text, maybe with a thousands comma: "1,999" -> 1999, "499" -> 499,
    // " 12,500 " -> 12500.
    // ---------------------------------------------------------------------------
    static int fixPrice(String text) {
        // >>> SOLUTION stub: return -1;
        return Integer.parseInt(text.strip().replace(",", ""));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | cleanSales   (Level 2 - Intermediate)
    // The whole cleaning pipeline: raw rows (from readRows) -> List<Sale> in file order.
    //   1. drop exact duplicate rows               4. a blank discount_pct becomes 0
    //   2. region and category: stripAndTitle      5. drop rows whose quantity is blank
    //   3. unit_price through fixPrice             6. quantity and discount_pct become ints
    // Decision log: FILL when a sensible default exists (no discount = 0), DROP when guessing
    // would invent data (unknown quantity). You may reuse the methods above.
    // ---------------------------------------------------------------------------
    static List<Sale> cleanSales(List<Map<String, String>> raw) {
        // >>> SOLUTION stub: return null;
        return dropDupes(raw).stream()
                .filter(r -> !r.get("quantity").isBlank())
                .map(r -> new Sale(
                        r.get("order_id"),
                        r.get("order_date"),
                        stripAndTitle(r.get("region")),
                        stripAndTitle(r.get("category")),
                        r.get("product"),
                        Integer.parseInt(r.get("quantity").strip()),
                        fixPrice(r.get("unit_price")),
                        r.get("discount_pct").isBlank() ? 0 : Integer.parseInt(r.get("discount_pct").strip()),
                        r.get("payment_method")))
                .toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | summaryByCategory   (Level 2 - Intermediate)
    // For every category: how many orders and the total revenue (rounded to 2 decimals).
    // Return a TreeMap category -> new Summary(orders, revenue).
    // Hint: groupingBy(Sale::category, TreeMap::new, Collectors.teeing(counting(), summingDouble(...), ...))
    // teeing runs two collectors at once and combines their results with a function.
    // ---------------------------------------------------------------------------
    static Map<String, Summary> summaryByCategory(List<Sale> sales) {
        // >>> SOLUTION stub: return null;
        return sales.stream().collect(Collectors.groupingBy(Sale::category, TreeMap::new,
                Collectors.teeing(Collectors.counting(), Collectors.summingDouble(Sale::revenue),
                        (orders, revenue) -> new Summary(orders, round2(revenue)))));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | regionVsTarget   (Level 3 - Challenge)
    // targets maps region -> revenue target. Return a Map region -> percent of the target that
    // was reached = total revenue / target * 100, rounded to 1 decimal (Math.round(x * 10) / 10.0).
    // Regions without a target are left out. (This is the "merge" of pandas: two tables joined by the key.)
    // ---------------------------------------------------------------------------
    static Map<String, Double> regionVsTarget(List<Sale> sales, Map<String, Double> targets) {
        // >>> SOLUTION stub: return null;
        Map<String, Double> totals = sales.stream()
                .collect(Collectors.groupingBy(Sale::region, Collectors.summingDouble(Sale::revenue)));
        Map<String, Double> percent = new TreeMap<>();
        for (Map.Entry<String, Double> e : totals.entrySet()) {
            Double target = targets.get(e.getKey());
            if (target != null) {
                percent.put(e.getKey(), Math.round(e.getValue() / target * 100 * 10) / 10.0);
            }
        }
        return percent;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | barChart   (Level 3 - Challenge)
    // A chart made of text. Take the n biggest values (biggest first; equal values -> label A-Z)
    // and return one line per entry:
    //     <label padded with spaces to the longest label shown> | <bar of '#'> <value rounded to a whole number>
    // The longest bar (the biggest value) is `width` characters; the others are in proportion
    // (Math.round(value / biggest * width)), but at least 1 character when the value is above 0.
    //   {East=100, West=50, North=25, South=10}, n=3, width=20 ->
    //     East  | #################### 100
    //     West  | ########## 50
    //     North | ##### 25
    // ---------------------------------------------------------------------------
    static List<String> barChart(Map<String, Double> values, int n, int width) {
        // >>> SOLUTION stub: return null;
        List<Map.Entry<String, Double>> top = values.entrySet().stream()
                .sorted(Comparator.comparingDouble((Map.Entry<String, Double> e) -> e.getValue()).reversed()
                        .thenComparing(Map.Entry::getKey))
                .limit(n)
                .toList();
        if (top.isEmpty()) {
            return List.of();
        }
        double biggest = top.get(0).getValue();
        int labelWidth = top.stream().mapToInt(e -> e.getKey().length()).max().getAsInt();
        List<String> lines = new ArrayList<>();
        for (Map.Entry<String, Double> e : top) {
            int bar = (int) Math.round(e.getValue() / biggest * width);
            if (bar == 0 && e.getValue() > 0) {
                bar = 1;
            }
            lines.add(String.format("%-" + labelWidth + "s | %s %d", e.getKey(), "#".repeat(bar), Math.round(e.getValue())));
        }
        return lines;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-3 | pivotRegionCategory   (Level 3 - Challenge)
    // The Excel "pivot table": revenue per region (rows) and category (columns).
    // Return a TreeMap region -> (TreeMap category -> total revenue rounded to 2 decimals).
    // EVERY region gets EVERY category that occurs anywhere in `sales`; a combination
    // without sales is 0.0.
    // Hint: first collect the set of all categories, then group by region and sum per category.
    // ---------------------------------------------------------------------------
    static Map<String, Map<String, Double>> pivotRegionCategory(List<Sale> sales) {
        // >>> SOLUTION stub: return null;
        Set<String> categories = sales.stream().map(Sale::category).collect(Collectors.toCollection(TreeSet::new));
        Map<String, Map<String, Double>> pivot = new TreeMap<>();
        for (Sale s : sales) {
            Map<String, Double> row = pivot.computeIfAbsent(s.region(), k -> new TreeMap<>());
            row.merge(s.category(), s.revenue(), Double::sum);
        }
        for (Map<String, Double> row : pivot.values()) {
            for (String category : categories) {
                row.putIfAbsent(category, 0.0);
            }
            row.replaceAll((category, total) -> round2(total));
        }
        return pivot;
        // <<< SOLUTION
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

    static Sale sale(String region, String category, int quantity, int unitPrice, int discount) {
        return new Sale("X", "2026-01-01", region, category, "P", quantity, unitPrice, discount, "UPI");
    }

    public static void main(String[] args) {
        Path messy = Path.of("../../datasets/sales_messy.csv");
        List<Map<String, String>> raw = attempt(() -> readRows(messy));
        System.out.println("--- Day 26 checks ---");
        Checker.check("L1-1 stripAndTitle", () -> List.of(stripAndTitle(" sOUTH "), stripAndTitle("east"),
                stripAndTitle("GROCERY "), stripAndTitle("")), List.of("South", "East", "Grocery", ""));
        Checker.check("L1-2 countMissing", () -> countMissing(raw), Map.of("quantity", 6, "discount_pct", 10));
        Checker.check("L1-2 countMissing (nothing missing -> empty map)",
                () -> countMissing(List.of(Map.of("a", "x", "b", "y"))), Map.of());
        Checker.check("L1-3 dropDupes", () -> List.of(dropDupes(raw).size(), raw.size()), List.of(300, 308));
        Checker.check("L1-3 dropDupes keeps the first copy, in order", () -> dropDupes(List.of(
                Map.of("a", "1"), Map.of("a", "2"), Map.of("a", "1"), Map.of("a", "3"))),
                List.of(Map.of("a", "1"), Map.of("a", "2"), Map.of("a", "3")));
        Checker.check("L2-1 fixPrice", () -> List.of(fixPrice("1,999"), fixPrice("499"), fixPrice(" 12,500 ")), List.of(1999, 499, 12500));
        Checker.check("L2-2 cleanSales (rows, regions, categories, total revenue)", () -> {
            List<Sale> clean = cleanSales(raw);
            return List.of(clean.size(),
                    clean.stream().map(Sale::region).distinct().sorted().toList(),
                    clean.stream().map(Sale::category).distinct().sorted().toList(),
                    round2(clean.stream().mapToDouble(Sale::revenue).sum()));
        }, List.of(294, List.of("East", "North", "South", "West"), List.of("Electronics", "Fashion", "Grocery", "Home"), 1415139.55));
        Checker.check("L2-2 cleanSales (a price with a comma, a blank discount, a blank quantity)", () -> {
            List<Map<String, String>> three = List.of(
                    new LinkedHashMap<>(Map.of("order_id", "A", "order_date", "2026-01-01", "region", " east ", "category", "HOME ",
                            "product", "Lamp", "quantity", "2", "unit_price", "1,299", "discount_pct", "", "payment_method", "UPI")),
                    new LinkedHashMap<>(Map.of("order_id", "B", "order_date", "2026-01-02", "region", "West", "category", "Home",
                            "product", "Lamp", "quantity", "", "unit_price", "699", "discount_pct", "5", "payment_method", "UPI")));
            return cleanSales(three);
        }, List.of(new Sale("A", "2026-01-01", "East", "Home", "Lamp", 2, 1299, 0, "UPI")));
        List<Sale> clean = attempt(() -> cleanSalesForChecks(raw));
        Checker.check("L2-3 summaryByCategory", () -> summaryByCategory(clean), Map.of(
                "Electronics", new Summary(70, 500410.1), "Fashion", new Summary(91, 451201.35),
                "Grocery", new Summary(60, 99976.5), "Home", new Summary(73, 363551.6)));
        List<Sale> small = List.of(sale("East", "Home", 1, 100, 0), sale("East", "Home", 2, 100, 0),
                sale("West", "Home", 4, 112, 0), sale("North", "Home", 1, 10, 0));
        Checker.check("L3-1 regionVsTarget", () -> regionVsTarget(small, Map.of("East", 400.0, "West", 500.0, "South", 100.0)),
                Map.of("East", 75.0, "West", 89.6));
        Checker.check("L3-2 barChart (top 3 of 4)", () -> barChart(Map.of("East", 100.0, "West", 50.0, "North", 25.0, "South", 10.0), 3, 20),
                List.of("East  | #################### 100", "West  | ########## 50", "North | ##### 25"));
        Checker.check("L3-2 barChart (tiny value still gets 1 #, ties A-Z)", () -> barChart(Map.of("B", 1.0, "A", 1000.0, "C", 1.0), 5, 10),
                List.of("A | ########## 1000", "B | # 1", "C | # 1"));
        Checker.check("L3-2 barChart (real data: revenue per region)", () -> {
            Map<String, Double> byRegion = clean.stream()
                    .collect(Collectors.groupingBy(Sale::region, Collectors.summingDouble(Sale::revenue)));
            return barChart(byRegion, 3, 20);
        }, List.of("West  | #################### 451772", "South | ############### 349599", "East  | ############## 323819"));
        Checker.check("L3-3 pivotRegionCategory", () -> pivotRegionCategory(clean), Map.of(
                "East", Map.of("Electronics", 74893.55, "Fashion", 149298.75, "Grocery", 34188.85, "Home", 65437.55),
                "North", Map.of("Electronics", 74914.05, "Fashion", 117493.85, "Grocery", 22758.8, "Home", 74782.55),
                "South", Map.of("Electronics", 172516.25, "Fashion", 64119.45, "Grocery", 25484.05, "Home", 87479.45),
                "West", Map.of("Electronics", 178086.25, "Fashion", 120289.3, "Grocery", 17544.8, "Home", 135852.05)));
        Checker.check("L3-3 pivotRegionCategory (missing combination = 0.0)", () -> pivotRegionCategory(List.of(
                        sale("East", "Home", 1, 100, 0), sale("West", "Fashion", 2, 50, 0))),
                Map.of("East", Map.of("Fashion", 0.0, "Home", 100.0), "West", Map.of("Fashion", 100.0, "Home", 0.0)));
        Checker.done();
    }

    // Used by the checks below L2-2 so that one unfinished task does not break the others.
    static List<Sale> cleanSalesForChecks(List<Map<String, String>> raw) {
        return raw.stream().distinct()
                .filter(r -> !r.get("quantity").isBlank())
                .map(r -> new Sale(r.get("order_id"), r.get("order_date"),
                        stripOne(r.get("region")), stripOne(r.get("category")), r.get("product"),
                        Integer.parseInt(r.get("quantity").strip()),
                        Integer.parseInt(r.get("unit_price").strip().replace(",", "")),
                        r.get("discount_pct").isBlank() ? 0 : Integer.parseInt(r.get("discount_pct").strip()),
                        r.get("payment_method")))
                .toList();
    }

    static String stripOne(String text) {
        String s = text.strip();
        return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1).toLowerCase();
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
