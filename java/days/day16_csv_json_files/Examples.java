/* Day 16 - Code along: a sales report from a spreadsheet export, and app settings as JSON.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * It reads ../../datasets/sales.csv (300 orders) and writes only into a temporary folder.
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Examples {
    // One sales row with the right types. A record can also have methods.
    record Sale(String orderId, String date, String region, String product, int quantity, int unitPrice, int discountPct) {
        double revenue() {
            return quantity * unitPrice * (1 - discountPct / 100.0);
        }
    }

    public static void main(String[] args) throws IOException {
        // ---- 1. CSV is text with commas: split a line ----
        String line = "ORD1108,2026-01-02,West,Electronics,Smartwatch,4,3499,15,NetBanking";
        String[] cells = line.split(",", -1);                    // -1 keeps empty cells at the end
        System.out.println(cells.length + " cells, region = " + cells[2]);   // 9 cells, region = West
        // Everything is TEXT: convert before doing maths.
        int quantity = Integer.parseInt(cells[5]);
        int unitPrice = Integer.parseInt(cells[6]);
        System.out.println("4 x 3499 = " + (quantity * unitPrice));         // 13996 ("4" * 3499 would not even compile)

        // ---- 2. Read the whole file into records ----
        Path salesFile = Path.of("../../datasets/sales.csv");
        List<String> lines = Files.readAllLines(salesFile, StandardCharsets.UTF_8);
        System.out.println("Header: " + lines.get(0).split(",")[0] + ", ... (" + (lines.size() - 1) + " orders)");
        List<Sale> sales = new ArrayList<>();
        for (String row : lines.subList(1, lines.size())) {           // skip the header line
            String[] c = row.split(",", -1);
            sales.add(new Sale(c[0], c[1], c[2], c[4], Integer.parseInt(c[5]), Integer.parseInt(c[6]), Integer.parseInt(c[7])));
        }
        System.out.println(sales.get(0));

        // ---- 3. Revenue = quantity x price x (1 - discount/100) ----
        double total = sales.stream().mapToDouble(Sale::revenue).sum();
        System.out.println("Total revenue: " + Math.round(total * 100) / 100.0);   // 1443241.55

        // ---- 4. The "group and total" pattern ----
        Map<String, Double> byRegion = new TreeMap<>();
        for (Sale s : sales) {
            byRegion.merge(s.region(), s.revenue(), Double::sum);
        }
        byRegion.forEach((region, value) -> System.out.println(String.format(Locale.US, "%-6s Rs. %,12.2f", region, value)));

        Map<String, Long> ordersPerMonth = sales.stream()          // the same idea with a Collector
                .collect(Collectors.groupingBy(s -> s.date().substring(0, 7), TreeMap::new, Collectors.counting()));
        System.out.println(ordersPerMonth);                         // {2026-01=26, ...}

        // ---- 5. Write a CSV report (into a temporary folder) ----
        Path tmp = Files.createTempDirectory("day16-demo");
        try {
            List<String> report = new ArrayList<>();
            report.add("region,revenue");
            byRegion.forEach((region, value) -> report.add(region + "," + Math.round(value * 100) / 100.0));
            Path reportFile = tmp.resolve("by_region.csv");
            Files.writeString(reportFile, String.join("\n", report) + "\n", StandardCharsets.UTF_8);
            System.out.println(Files.readAllLines(reportFile).get(0) + " | " + Files.readAllLines(reportFile).size() + " lines");   // region,revenue | 5 lines

            // ---- 6. JSON: settings as text ----
            Map<String, Object> settings = new LinkedHashMap<>();
            settings.put("theme", "dark");
            settings.put("currency", "INR");
            settings.put("limits", Map.of("daily", 20000));
            String json = toJson(settings);
            System.out.println(json);                               // {"theme":"dark","currency":"INR","limits":{"daily":20000}}
            Path settingsFile = tmp.resolve("settings.json");
            Files.writeString(settingsFile, json, StandardCharsets.UTF_8);

            // A reader turns the text back into data. This tiny one only handles FLAT objects:
            Map<String, String> flat = parseFlat("{\"theme\":\"dark\",\"size\":12}");
            System.out.println(flat.get("theme") + " " + (Integer.parseInt(flat.get("size")) + 1));   // dark 13
            // For nested JSON you need a real parser (see the Json helper in Practice.java, or Jackson / Gson).

            // ---- 7. Merge defaults with the user's overrides ----
            Map<String, Object> defaults = new LinkedHashMap<>(Map.of("lang", "en", "size", 12));
            Map<String, Object> user = Map.of("size", 16);
            Map<String, Object> merged = new LinkedHashMap<>(defaults);
            merged.putAll(user);                                    // user values win (flat merge)
            System.out.println(new TreeMap<>(merged));              // {lang=en, size=16}
        } finally {
            try (Stream<Path> all = Files.walk(tmp)) {
                for (Path p : all.sorted(Comparator.reverseOrder()).toList()) {
                    Files.deleteIfExists(p);
                }
            }
        }
    }

    // The Day 13 JSON writer (compact version).
    static String toJson(Object value) {
        if (value == null) {
            return "null";
        } else if (value instanceof String s) {
            return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
        } else if (value instanceof Number || value instanceof Boolean) {
            return value.toString();
        } else if (value instanceof List<?> list) {
            return list.stream().map(Examples::toJson).collect(Collectors.joining(",", "[", "]"));
        } else if (value instanceof Map<?, ?> map) {
            return map.entrySet().stream()
                    .map(e -> toJson(String.valueOf(e.getKey())) + ":" + toJson(e.getValue()))
                    .collect(Collectors.joining(",", "{", "}"));
        }
        throw new IllegalArgumentException("cannot write " + value);
    }

    // A beginner's JSON reader: flat objects only, no commas inside the text.
    static Map<String, String> parseFlat(String json) {
        Map<String, String> map = new LinkedHashMap<>();
        String body = json.strip();
        body = body.substring(1, body.length() - 1);                // cut off { and }
        for (String pair : body.split(",")) {
            String[] kv = pair.split(":", 2);
            map.put(unquote(kv[0]), unquote(kv[1]));
        }
        return map;
    }

    static String unquote(String text) {
        String t = text.strip();
        return t.startsWith("\"") ? t.substring(1, t.length() - 1) : t;
    }
}
