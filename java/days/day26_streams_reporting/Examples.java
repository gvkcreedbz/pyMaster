/* Day 26 - Code along: Monday morning, a "fresh export" arrives and it is full of mess.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * Data: ../../datasets/sales_messy.csv (blanks, duplicates, " SOUTH ", "1,999" prices).
 */
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Examples {
    record Sale(String orderId, String orderDate, String region, String category, String product,
                int quantity, int unitPrice, int discountPct, String paymentMethod) {
        double revenue() {
            return quantity * unitPrice * (1 - discountPct / 100.0);
        }
    }

    // Quote-aware split (Day 16): "4,999" in quotes stays ONE cell.
    static List<String> splitCsvLine(String line) {
        List<String> cells = new ArrayList<>();
        StringBuilder cell = new StringBuilder();
        boolean inQuotes = false;
        for (char c : line.toCharArray()) {
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                cells.add(cell.toString());
                cell.setLength(0);
            } else {
                cell.append(c);
            }
        }
        cells.add(cell.toString());
        return cells;
    }

    static List<Map<String, String>> readRows(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        List<String> header = splitCsvLine(lines.get(0));
        List<Map<String, String>> rows = new ArrayList<>();
        for (String line : lines.subList(1, lines.size())) {
            List<String> cells = splitCsvLine(line);
            Map<String, String> row = new LinkedHashMap<>();
            for (int c = 0; c < header.size(); c++) {
                row.put(header.get(c), cells.get(c));
            }
            rows.add(row);
        }
        return rows;
    }

    static String titleCase(String text) {
        String s = text.strip();
        return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1).toLowerCase();
    }

    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    public static void main(String[] args) throws IOException {
        // ---- 1. Inspect BEFORE you clean ----
        List<Map<String, String>> raw = readRows(Path.of("../../datasets/sales_messy.csv"));
        System.out.println("Raw rows: " + raw.size());                                  // 308
        System.out.println("Distinct rows: " + raw.stream().distinct().count());         // 300 -> 8 duplicates
        Set<String> regions = raw.stream().map(r -> r.get("region")).collect(Collectors.toCollection(TreeSet::new));
        System.out.println(regions.size() + " spellings of 4 regions: " + regions);
        long noQuantity = raw.stream().filter(r -> r.get("quantity").isBlank()).count();
        long noDiscount = raw.stream().filter(r -> r.get("discount_pct").isBlank()).count();
        System.out.println("Blank quantity: " + noQuantity + ", blank discount: " + noDiscount);   // 6 and 10

        // ---- 2. Clean it: one stream, one rule per step ----
        List<Sale> sales = raw.stream()
                .distinct()                                                  // drop exact duplicates
                .filter(r -> !r.get("quantity").isBlank())                   // DROP: we cannot guess a quantity
                .map(r -> new Sale(
                        r.get("order_id"),
                        r.get("order_date"),
                        titleCase(r.get("region")),                          // " SOUTH " -> "South"
                        titleCase(r.get("category")),
                        r.get("product"),
                        Integer.parseInt(r.get("quantity")),
                        Integer.parseInt(r.get("unit_price").replace(",", "")),   // "1,999" -> 1999
                        r.get("discount_pct").isBlank() ? 0 : Integer.parseInt(r.get("discount_pct")),   // FILL: no discount = 0
                        r.get("payment_method")))
                .toList();
        System.out.println("Clean rows: " + sales.size());                    // 294
        System.out.println("Regions now: " + sales.stream().map(Sale::region).distinct().sorted().toList());

        // ---- 3. Validate: do the totals still make sense? ----
        double total = sales.stream().mapToDouble(Sale::revenue).sum();
        System.out.println("Total revenue: Rs." + round2(total));              // 1415139.55

        // ---- 4. Sorting and top-N ----
        System.out.println("Five biggest orders:");
        sales.stream()
                .sorted(Comparator.comparingDouble(Sale::revenue).reversed().thenComparing(Sale::orderId))
                .limit(5)
                .forEach(s -> System.out.printf("  %s  %-12s Rs.%.2f%n", s.orderId(), s.product(), s.revenue()));

        // ---- 5. Two summaries in one pass: teeing ----
        record Summary(long orders, double revenue) {}
        Map<String, Summary> byCategory = sales.stream().collect(Collectors.groupingBy(Sale::category, TreeMap::new,
                Collectors.teeing(Collectors.counting(), Collectors.summingDouble(Sale::revenue),
                        (orders, revenue) -> new Summary(orders, round2(revenue)))));
        byCategory.forEach((category, s) -> System.out.println(category + ": " + s.orders() + " orders, Rs." + s.revenue()));

        // ---- 6. A text bar chart (no libraries needed) ----
        Map<String, Double> byRegion = sales.stream()
                .collect(Collectors.groupingBy(Sale::region, Collectors.summingDouble(Sale::revenue)));
        double biggest = byRegion.values().stream().mapToDouble(Double::doubleValue).max().orElse(1);
        System.out.println("Revenue by region");
        byRegion.entrySet().stream()
                .sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
                .forEach(e -> {
                    int bar = (int) Math.round(e.getValue() / biggest * 30);        // the longest bar is 30 characters
                    System.out.printf("  %-6s | %s %d%n", e.getKey(), "#".repeat(bar), Math.round(e.getValue()));
                });

        // ---- 7. Monthly trend ----
        Map<String, Double> byMonth = sales.stream().collect(Collectors.groupingBy(s -> s.orderDate().substring(0, 7),
                TreeMap::new, Collectors.summingDouble(Sale::revenue)));
        double bestMonth = byMonth.values().stream().mapToDouble(Double::doubleValue).max().orElse(1);
        byMonth.forEach((month, revenue) -> System.out.println(month + " " + "*".repeat((int) Math.round(revenue / bestMonth * 20))));

        // ---- 8. Save the clean file (always keep the raw one!) ----
        Path out = Files.createTempFile("sales_clean", ".csv");
        List<String> lines = new ArrayList<>();
        lines.add("order_id,order_date,region,category,product,quantity,unit_price,discount_pct,payment_method");
        for (Sale s : sales) {
            lines.add(String.join(",", s.orderId(), s.orderDate(), s.region(), s.category(), s.product(),
                    String.valueOf(s.quantity()), String.valueOf(s.unitPrice()), String.valueOf(s.discountPct()), s.paymentMethod()));
        }
        Files.write(out, lines);
        System.out.println("Wrote " + (Files.readAllLines(out).size() - 1) + " clean rows");
        Files.delete(out);
    }
}
