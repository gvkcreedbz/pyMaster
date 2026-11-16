/* Day 29 - Code along: a sales data pipeline.  CSV -> clean -> SQLite -> report.
 *
 * Type each section yourself, run it (java Examples.java; the jars in java/lib are on the classpath in the portal),
 * then change values and re-run. The database and the report are written into a temporary folder that is deleted at the end.
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

class Examples {
    // The raw row: all text, dirty. The clean row: real types. Two records = two stages of the pipeline.
    record RawRow(String orderId, String orderDate, String region, String category, String product,
                  String quantity, String unitPrice, String discountPct) {}

    record Sale(String orderId, LocalDate orderDate, String region, String category, String product,
                int quantity, int unitPrice, int discountPct) {
        double revenue() {
            return quantity * unitPrice * (1 - discountPct / 100.0);
        }
    }

    public static void main(String[] args) throws IOException, SQLException {
        Path csv = Path.of("../../datasets/sales_messy.csv");
        Path tmp = Files.createTempDirectory("day29-demo");           // the program creates its own temp folder
        try {
            // ---- 1. EXTRACT: read the file, change nothing ----
            List<RawRow> raw = extract(csv);
            System.out.println("extracted " + raw.size() + " rows");
            System.out.println(raw.get(4));                           // region is "SOUTH " (capitals + a trailing space)

            // ---- 2. QUALITY REPORT: make the problems visible BEFORE fixing them ----
            long duplicates = raw.size() - new HashSet<>(raw).size();
            long blanks = raw.stream().filter(r -> r.quantity().isBlank() || r.discountPct().isBlank()).count();
            long commas = raw.stream().filter(r -> r.unitPrice().contains(",")).count();
            System.out.println("duplicates=" + duplicates + ", rows with a blank quantity/discount=" + blanks + ", prices with commas=" + commas);

            // ---- 3. TRANSFORM: duplicates out, text tidy, numbers real ----
            List<Sale> clean = new ArrayList<>();
            for (RawRow r : new LinkedHashSet<>(raw)) {               // a record has equals(), so the set drops exact copies
                if (r.quantity().isBlank()) {
                    continue;                                         // no quantity = no usable order
                }
                int discount = r.discountPct().isBlank() ? 0 : Integer.parseInt(r.discountPct());
                clean.add(new Sale(r.orderId(), LocalDate.parse(r.orderDate()), capitalise(r.region()), capitalise(r.category()),
                        r.product().strip(), Integer.parseInt(r.quantity()), Integer.parseInt(r.unitPrice().replace(",", "")), discount));
            }
            System.out.println("cleaned -> " + clean.size() + " rows");
            double total = clean.stream().mapToDouble(Sale::revenue).sum();
            System.out.printf(Locale.US, "total revenue (check number): %,.2f%n", total);

            // ---- 4. LOAD: put the clean rows into SQLite (JDBC) ----
            Path db = tmp.resolve("sales.db");
            try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + db)) {
                conn.setAutoCommit(false);                            // one transaction: all rows or none
                try (Statement st = conn.createStatement()) {
                    st.executeUpdate("CREATE TABLE orders (order_id TEXT, order_date TEXT, region TEXT, category TEXT, "
                            + "product TEXT, quantity INTEGER, unit_price INTEGER, discount_pct INTEGER, revenue REAL)");
                }
                try (PreparedStatement ps = conn.prepareStatement("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")) {
                    for (Sale s : clean) {
                        ps.setString(1, s.orderId());
                        ps.setString(2, s.orderDate().toString());    // SQLite has no date type: store "2026-01-02" text
                        ps.setString(3, s.region());
                        ps.setString(4, s.category());
                        ps.setString(5, s.product());
                        ps.setInt(6, s.quantity());
                        ps.setInt(7, s.unitPrice());
                        ps.setInt(8, s.discountPct());
                        ps.setDouble(9, s.revenue());
                        ps.addBatch();
                    }
                    ps.executeBatch();
                }
                conn.commit();
            }
            System.out.println("database file exists: " + Files.exists(db));

            // ---- 5. REPORT: ask the DATABASE, not the list ----
            Map<String, Double> byRegion = new LinkedHashMap<>();
            try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + db);
                 Statement st = conn.createStatement();
                 ResultSet rs = st.executeQuery("SELECT region, ROUND(SUM(revenue), 2) FROM orders GROUP BY region ORDER BY region")) {
                while (rs.next()) {
                    byRegion.put(rs.getString(1), rs.getDouble(2));
                }
            }
            double max = Collections.max(byRegion.values());
            for (Map.Entry<String, Double> e : byRegion.entrySet()) {
                String bar = "#".repeat((int) Math.round(e.getValue() / max * 30));
                System.out.println(String.format(Locale.US, "%-6s %-30s %,.0f", e.getKey(), bar, e.getValue()));
            }

            String bestProduct = clean.stream()
                    .collect(Collectors.groupingBy(Sale::product, Collectors.summingDouble(Sale::revenue)))
                    .entrySet().stream().max(Map.Entry.comparingByValue()).orElseThrow().getKey();
            Path report = tmp.resolve("report.md");
            Files.writeString(report, "# Sales Report\n\n- Orders: " + clean.size() + "\n- Best product: " + bestProduct + "\n",
                    StandardCharsets.UTF_8);
            System.out.println(Files.readString(report));

            // ---- 6. The raw input file was never touched ----
            System.out.println("input still has " + (Files.readAllLines(csv).size() - 1) + " data lines");
        } finally {
            try (Stream<Path> all = Files.walk(tmp)) {
                for (Path p : all.sorted(Comparator.reverseOrder()).toList()) {
                    Files.deleteIfExists(p);
                }
            }
        }
    }

    static List<RawRow> extract(Path path) throws IOException {
        List<RawRow> rows = new ArrayList<>();
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        for (String line : lines.subList(1, lines.size())) {
            List<String> c = splitCsvLine(line);
            rows.add(new RawRow(c.get(0), c.get(1), c.get(2), c.get(3), c.get(4), c.get(5), c.get(6), c.get(7)));
        }
        return rows;
    }

    // "4,999" is ONE cell because it is in quotes, so a plain split(",") would break it.
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

    static String capitalise(String text) {
        String t = text.strip();
        return t.isEmpty() ? t : t.substring(0, 1).toUpperCase(Locale.ROOT) + t.substring(1).toLowerCase(Locale.ROOT);
    }
}
