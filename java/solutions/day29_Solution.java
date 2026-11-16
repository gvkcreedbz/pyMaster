// SOLUTION FILE - try the hint ladder first!
/* Day 29 - Capstone practice: a sales data pipeline (CSV -> clean -> SQLite -> report).
 *
 * Run:  java Practice.java        (the jars in java/lib are already on the classpath in the portal)
 * Raw input: ../../datasets/sales_messy.csv. Build the pieces top to bottom: each one uses the ones above.
 * Everything you write goes into a temporary folder that the checker deletes at the end.
 */
import java.io.FileNotFoundException;
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
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

class Practice {

    // One line of the CSV exactly as it is in the file: every cell is still TEXT (and may be dirty).
    record RawRow(String orderId, String orderDate, String region, String category, String product,
                  String quantity, String unitPrice, String discountPct, String paymentMethod) {}

    // One CLEAN order with real types.
    record Sale(String orderId, LocalDate orderDate, String region, String category, String product,
                int quantity, int unitPrice, int discountPct) {
        double revenue() {
            return quantity * unitPrice * (1 - discountPct / 100.0);
        }
    }

    // The headline numbers of the report. The two money values are rounded to 2 decimals.
    record Kpis(int orders, double totalRevenue, double avgOrderValue,
                String bestRegion, String bestCategory, String bestProduct, String bestMonth) {}

    // --- provided helpers (no need to change) -------------------------------------------------------------------

    /** Split one CSV line; a cell in "double quotes" may contain commas (for example "4,999"). */
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

    /** "  sOUTH " -> "South": strip the spaces, first letter upper case, the rest lower case. */
    static String capitalise(String text) {
        String t = text.strip();
        return t.isEmpty() ? t : t.substring(0, 1).toUpperCase(Locale.ROOT) + t.substring(1).toLowerCase(Locale.ROOT);
    }

    static double round2(double value) {
        return Math.round(value * 100) / 100.0;
    }

    /** The key (region, category, ...) with the highest total revenue. */
    static String bestBy(List<Sale> sales, Function<Sale, String> key) {
        return sales.stream()
                .collect(Collectors.groupingBy(key, Collectors.summingDouble(Sale::revenue)))
                .entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .orElseThrow()
                .getKey();
    }

    /** A text bar chart (the Java version of the Python PNG): one # per 1/30 of the biggest value. */
    static String barChart(Map<String, Double> totals) {
        double max = totals.values().stream().mapToDouble(Double::doubleValue).max().orElse(1);
        StringBuilder out = new StringBuilder("Revenue by region\n");
        totals.forEach((name, value) -> out.append(String.format(Locale.US, "%-6s %-30s %,.0f%n",
                name, "#".repeat((int) Math.round(value / max * 30)), value)));
        return out.toString();
    }

    // ---------------------------------------------------------------------------
    // L1-1 | extract   (Level 1 - Beginner)
    // Read the CSV at `path` and return its rows as RawRow objects: NO cleaning at all.
    // Skip the header line and any empty line. Use splitCsvLine (it handles "4,999").
    // ---------------------------------------------------------------------------
    static List<RawRow> extract(Path path) throws IOException {
        // >>> SOLUTION stub: return null;
        List<RawRow> rows = new ArrayList<>();
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        for (String line : lines.subList(1, lines.size())) {
            if (line.isBlank()) {
                continue;
            }
            List<String> c = splitCsvLine(line);
            rows.add(new RawRow(c.get(0), c.get(1), c.get(2), c.get(3), c.get(4), c.get(5), c.get(6), c.get(7), c.get(8)));
        }
        return rows;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | qualityReport   (Level 1 - Beginner)
    // Inspect the RAW rows and return a Map<String, Integer> with exactly these keys:
    //   "rows"                - number of rows
    //   "duplicates"          - rows that are an exact copy of an earlier row (rows minus distinct rows)
    //   "missing_cells"       - cells that are empty (isBlank) in ANY of the 9 columns
    //   "prices_with_commas"  - how many unitPrice values contain a comma (e.g. "4,999")
    //   "dirty_text_cells"    - how many region + category values differ from capitalise(value)
    // Hint: a record has equals/hashCode, so new HashSet<>(raw) removes exact duplicates.
    // ---------------------------------------------------------------------------
    static Map<String, Integer> qualityReport(List<RawRow> raw) {
        // >>> SOLUTION stub: return null;
        int missing = 0;
        int dirty = 0;
        int commas = 0;
        for (RawRow r : raw) {
            for (String cell : List.of(r.orderId(), r.orderDate(), r.region(), r.category(), r.product(),
                    r.quantity(), r.unitPrice(), r.discountPct(), r.paymentMethod())) {
                if (cell.isBlank()) {
                    missing++;
                }
            }
            if (r.unitPrice().contains(",")) {
                commas++;
            }
            if (!r.region().equals(capitalise(r.region()))) {
                dirty++;
            }
            if (!r.category().equals(capitalise(r.category()))) {
                dirty++;
            }
        }
        Map<String, Integer> report = new LinkedHashMap<>();
        report.put("rows", raw.size());
        report.put("duplicates", raw.size() - new HashSet<>(raw).size());
        report.put("missing_cells", missing);
        report.put("prices_with_commas", commas);
        report.put("dirty_text_cells", dirty);
        return report;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | transform   (Level 2 - Intermediate)
    // Turn the raw rows into clean Sale objects (do not change the input list):
    //   1. drop exact duplicate rows (keep the first, keep the order)
    //   2. drop rows whose quantity is empty
    //   3. region and category: capitalise(...)
    //   4. unitPrice: remove commas, then Integer.parseInt          ("4,999" -> 4999)
    //   5. discountPct: empty -> 0, else Integer.parseInt
    //   6. orderDate: LocalDate.parse(...)
    // ---------------------------------------------------------------------------
    static List<Sale> transform(List<RawRow> raw) {
        // >>> SOLUTION stub: return null;
        List<Sale> clean = new ArrayList<>();
        for (RawRow r : new LinkedHashSet<>(raw)) {
            if (r.quantity().isBlank()) {
                continue;
            }
            int discount = r.discountPct().isBlank() ? 0 : Integer.parseInt(r.discountPct().strip());
            clean.add(new Sale(r.orderId(), LocalDate.parse(r.orderDate().strip()), capitalise(r.region()),
                    capitalise(r.category()), r.product().strip(), Integer.parseInt(r.quantity().strip()),
                    Integer.parseInt(r.unitPrice().replace(",", "").strip()), discount));
        }
        return clean;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | loadToSqlite   (Level 2 - Intermediate)
    // Write the clean sales into table "orders" of the SQLite file `dbFile` (JDBC URL "jdbc:sqlite:" + dbFile).
    // Start fresh: DROP TABLE IF EXISTS, then CREATE TABLE orders with these columns, in this order:
    //   order_id TEXT, order_date TEXT ("2026-01-02"), region TEXT, category TEXT, product TEXT,
    //   quantity INTEGER, unit_price INTEGER, discount_pct INTEGER, revenue REAL
    // Insert every sale with a PreparedStatement (? placeholders, addBatch) inside ONE transaction
    // (setAutoCommit(false) ... commit). Close the connection (try-with-resources). Return the rows written.
    // ---------------------------------------------------------------------------
    static int loadToSqlite(List<Sale> sales, Path dbFile) throws SQLException {
        // >>> SOLUTION stub: return 0;
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbFile)) {
            conn.setAutoCommit(false);
            try (Statement st = conn.createStatement()) {
                st.executeUpdate("DROP TABLE IF EXISTS orders");
                st.executeUpdate("CREATE TABLE orders (order_id TEXT, order_date TEXT, region TEXT, category TEXT, "
                        + "product TEXT, quantity INTEGER, unit_price INTEGER, discount_pct INTEGER, revenue REAL)");
            }
            try (PreparedStatement ps = conn.prepareStatement("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")) {
                for (Sale s : sales) {
                    ps.setString(1, s.orderId());
                    ps.setString(2, s.orderDate().toString());
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
        return sales.size();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | kpis   (Level 2 - Intermediate)
    // From the clean sales build a Kpis record:
    //   orders = how many sales, totalRevenue and avgOrderValue (rounded with round2),
    //   bestRegion / bestCategory / bestProduct = highest total revenue (use the provided bestBy),
    //   bestMonth = the month "YYYY-MM" with the highest revenue (hint: orderDate().toString().substring(0, 7)).
    // ---------------------------------------------------------------------------
    static Kpis kpis(List<Sale> sales) {
        // >>> SOLUTION stub: return null;
        double total = sales.stream().mapToDouble(Sale::revenue).sum();
        return new Kpis(sales.size(), round2(total), round2(total / sales.size()),
                bestBy(sales, Sale::region), bestBy(sales, Sale::category), bestBy(sales, Sale::product),
                bestBy(sales, s -> s.orderDate().toString().substring(0, 7)));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | revenueByRegionFromDb   (Level 3 - Challenge)
    // The report should come from the DATABASE, not from memory. Open `dbFile` and ask SQL:
    //   SELECT region, ROUND(SUM(revenue), 2) FROM orders GROUP BY region ORDER BY region
    // Return the result as a Map that keeps that order (LinkedHashMap): region -> total.
    // ---------------------------------------------------------------------------
    static Map<String, Double> revenueByRegionFromDb(Path dbFile) throws SQLException {
        // >>> SOLUTION stub: return null;
        Map<String, Double> totals = new LinkedHashMap<>();
        String sql = "SELECT region, ROUND(SUM(revenue), 2) FROM orders GROUP BY region ORDER BY region";
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbFile);
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                totals.put(rs.getString(1), rs.getDouble(2));
            }
        }
        return totals;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | writeReport   (Level 3 - Challenge)
    // Write a Markdown file at `path` (UTF-8). Line 1 is "# Sales Report", line 2 is empty, then one
    // bullet per KPI, exactly like these examples (money: thousands separators and 2 decimals, Locale.US):
    //   - Orders: 294
    //   - Total revenue: 1,415,139.55
    //   - Average order value: 4,813.40
    //   - Best region: West
    //   - Best category: Electronics
    //   - Best product: Smartwatch
    //   - Best month: 2026-06
    // ---------------------------------------------------------------------------
    static void writeReport(Kpis k, Path path) throws IOException {
        // >>> SOLUTION
        List<String> lines = List.of(
                "# Sales Report",
                "",
                "- Orders: " + k.orders(),
                String.format(Locale.US, "- Total revenue: %,.2f", k.totalRevenue()),
                String.format(Locale.US, "- Average order value: %,.2f", k.avgOrderValue()),
                "- Best region: " + k.bestRegion(),
                "- Best category: " + k.bestCategory(),
                "- Best product: " + k.bestProduct(),
                "- Best month: " + k.bestMonth());
        Files.writeString(path, String.join("\n", lines) + "\n", StandardCharsets.UTF_8);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-3 | runPipeline   (Level 3 - Challenge)
    // Wire everything together (log.accept(...) once per step, exact texts below):
    //   * csv missing  -> throw new FileNotFoundException("input file not found: " + csv)
    //   * create outDir (and parents) if needed
    //   * extract            -> log "extracted 308 rows"          (the real number of rows)
    //   * qualityReport      -> log "quality: " + the map
    //   * transform          -> log "cleaned -> 294 rows"
    //   * loadToSqlite(outDir/"sales.db") -> log "loaded 294 rows into sales.db"
    //   * kpis, then writeReport(outDir/"report.md")
    //   * revenueByRegionFromDb -> barChart -> write it to outDir/"revenue_by_region.txt"
    //   * log "report and chart written to " + outDir     * return the Kpis
    // Never modify the input file.
    // ---------------------------------------------------------------------------
    static Kpis runPipeline(Path csv, Path outDir, Consumer<String> log) throws IOException, SQLException {
        // >>> SOLUTION stub: return null;
        if (!Files.exists(csv)) {
            throw new FileNotFoundException("input file not found: " + csv);
        }
        Files.createDirectories(outDir);
        List<RawRow> raw = extract(csv);
        log.accept("extracted " + raw.size() + " rows");
        log.accept("quality: " + qualityReport(raw));
        List<Sale> clean = transform(raw);
        log.accept("cleaned -> " + clean.size() + " rows");
        Path db = outDir.resolve("sales.db");
        int written = loadToSqlite(clean, db);
        log.accept("loaded " + written + " rows into sales.db");
        Kpis result = kpis(clean);
        writeReport(result, outDir.resolve("report.md"));
        Map<String, Double> byRegion = revenueByRegionFromDb(db);
        Files.writeString(outDir.resolve("revenue_by_region.txt"), barChart(byRegion), StandardCharsets.UTF_8);
        log.accept("report and chart written to " + outDir);
        return result;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-4 | cli   (Level 3 - Challenge)
    // The command-line front door (what a real main would call: System.exit(cli(args))).
    // Understand  --input <csv> (required)  and  --out <folder> (default "output").
    //   * success: run runPipeline (print each log line as "INFO: <line>") and return 0
    //   * --input missing: print "Error: --input is required" and return 2
    //   * input file missing (FileNotFoundException): print "Error: <message>" and return 1
    //   * any other IOException / SQLException: print "Error: <message>" and return 1
    // ---------------------------------------------------------------------------
    static int cli(String[] args) {
        // >>> SOLUTION stub: return -1;
        String input = null;
        String out = "output";
        for (int i = 0; i + 1 < args.length; i += 2) {
            if (args[i].equals("--input")) {
                input = args[i + 1];
            } else if (args[i].equals("--out")) {
                out = args[i + 1];
            }
        }
        if (input == null) {
            System.out.println("Error: --input is required");
            return 2;
        }
        try {
            runPipeline(Path.of(input), Path.of(out), line -> System.out.println("INFO: " + line));
        } catch (FileNotFoundException e) {
            System.out.println("Error: " + e.getMessage());
            return 1;
        } catch (IOException | SQLException e) {
            System.out.println("Error: " + e.getMessage());
            return 1;
        }
        return 0;
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    // The Checker's lambdas cannot throw checked exceptions, so attempt(...) wraps them for the tests.
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

    static String text(Path p) throws IOException {
        return new String(Files.readAllBytes(p), StandardCharsets.UTF_8).replace("\r\n", "\n");
    }

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> all = Files.walk(root)) {
            for (Path p : all.sorted(Comparator.reverseOrder()).toList()) {
                Files.deleteIfExists(p);
            }
        }
    }

    static final Path MESSY = Path.of("../../datasets/sales_messy.csv");
    static final Kpis EXPECTED = new Kpis(294, 1415139.55, 4813.4, "West", "Electronics", "Smartwatch", "2026-06");

    static List<Sale> cleanSales() throws IOException {
        return transform(extract(MESSY));
    }

    static List<Object> loadCheck(Path tmp) throws Exception {
        Path db = tmp.resolve("t.db");
        int written = loadToSqlite(cleanSales(), db);
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + db);
             Statement st = conn.createStatement()) {
            ResultSet rs = st.executeQuery("SELECT COUNT(*), ROUND(SUM(revenue), 2), MIN(order_date) FROM orders");
            rs.next();
            List<Object> out = new ArrayList<>(List.of(written, rs.getInt(1), rs.getDouble(2), rs.getString(3)));
            List<String> columns = new ArrayList<>();
            ResultSet info = st.executeQuery("PRAGMA table_info(orders)");
            while (info.next()) {
                columns.add(info.getString("name"));
            }
            out.add(columns);
            return out;
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("--- Day 29 checks ---");
        Path tmp = Files.createTempDirectory("day29");
        try {
            Checker.check("L1-1 extract is RAW (308 rows, nothing cleaned)", () -> attempt(() -> {
                List<RawRow> raw = extract(MESSY);
                RawRow quoted = raw.stream().filter(r -> r.orderId().equals("ORD1142")).findFirst().orElseThrow();
                return List.of(raw.size(), raw.get(0).orderId(), raw.get(0).quantity(), raw.get(4).region(), quoted.unitPrice());
            }), List.of(308, "ORD1186", "", "SOUTH ", "4,999"));
            Checker.check("L1-2 qualityReport", () -> attempt(() -> qualityReport(extract(MESSY))),
                    Map.of("rows", 308, "duplicates", 8, "missing_cells", 16, "prices_with_commas", 7, "dirty_text_cells", 51));
            Checker.check("L2-1 transform: counts and types", () -> attempt(() -> {
                List<RawRow> raw = extract(MESSY);
                List<Sale> out = transform(raw);
                Set<String> regions = new TreeSet<>();
                out.forEach(s -> regions.add(s.region()));
                double total = out.stream().mapToDouble(Sale::revenue).sum();
                return List.of(raw.size(), out.size(), regions.toString(), round2(total), out.get(0).orderId(),
                        out.get(0).unitPrice(), out.get(0).orderDate().toString());
            }), List.of(308, 294, "[East, North, South, West]", 1415139.55, "ORD1176", 2199, "2026-04-03"));
            Checker.check("L2-1 transform: commas, blanks and spaces", () -> attempt(() -> {
                List<RawRow> raw = List.of(
                        new RawRow("A1", "2026-01-05", " south ", "grocery ", "Tea", "2", "1,999", "", "UPI"),
                        new RawRow("A1", "2026-01-05", " south ", "grocery ", "Tea", "2", "1,999", "", "UPI"),
                        new RawRow("A2", "2026-01-06", "EAST", "Home", "Lamp", "", "699", "5", "COD"));
                return transform(raw);
            }), List.of(new Sale("A1", LocalDate.of(2026, 1, 5), "South", "Grocery", "Tea", 2, 1999, 0)));
            Checker.check("L2-2 loadToSqlite", () -> attempt(() -> loadCheck(tmp)),
                    List.of(294, 294, 1415139.55, "2026-01-02",
                            List.of("order_id", "order_date", "region", "category", "product",
                                    "quantity", "unit_price", "discount_pct", "revenue")));
            Checker.check("L2-2 loadToSqlite replaces the table", () -> attempt(() -> {
                Path db = tmp.resolve("twice.db");
                loadToSqlite(cleanSales(), db);
                loadToSqlite(cleanSales().subList(0, 10), db);
                return revenueByRegionFromDb(db).size() > 0 && loadToSqlite(List.of(), db) == 0;
            }), true);
            Checker.check("L2-3 kpis", () -> attempt(() -> kpis(cleanSales())), EXPECTED);
            Checker.check("L3-1 revenueByRegionFromDb", () -> attempt(() -> {
                Path db = tmp.resolve("sql.db");
                loadToSqlite(cleanSales(), db);
                Map<String, Double> totals = revenueByRegionFromDb(db);
                return List.of(new ArrayList<>(totals.keySet()), totals.get("West"));
            }), List.of(List.of("East", "North", "South", "West"), 451772.4));
            Checker.check("L3-2 writeReport", () -> attempt(() -> {
                Path p = tmp.resolve("r.md");
                writeReport(EXPECTED, p);
                return text(p);
            }), "# Sales Report\n\n- Orders: 294\n- Total revenue: 1,415,139.55\n- Average order value: 4,813.40\n"
                    + "- Best region: West\n- Best category: Electronics\n- Best product: Smartwatch\n- Best month: 2026-06\n");

            Path out = tmp.resolve("deep").resolve("results");
            List<String> lines = new ArrayList<>();
            Checker.check("L3-3 runPipeline returns the KPIs and creates 3 files", () -> attempt(() -> {
                Kpis k = runPipeline(MESSY, out, lines::add);
                try (Stream<Path> files = Files.list(out)) {
                    return List.of(k, files.map(f -> f.getFileName().toString()).sorted().toList());
                }
            }), List.of(EXPECTED, List.of("report.md", "revenue_by_region.txt", "sales.db")));
            Checker.check("L3-3 runPipeline logs each step", () -> List.of(lines.size() >= 5, lines.isEmpty() ? "" : lines.get(0),
                    lines.size() < 3 ? "" : lines.get(2)), List.of(true, "extracted 308 rows", "cleaned -> 294 rows"));
            Checker.check("L3-3 chart comes from the database", () -> attempt(() -> {
                String chart = text(out.resolve("revenue_by_region.txt"));
                return List.of(chart.startsWith("Revenue by region\n"), chart.contains("West"), chart.contains("451,772"));
            }), List.of(true, true, true));
            Checker.check("L3-3 runPipeline missing input", () -> {
                try {
                    runPipeline(MESSY.resolveSibling("nope.csv"), tmp.resolve("x"), s -> { });
                    return "no exception";
                } catch (FileNotFoundException e) {
                    return e.getMessage().startsWith("input file not found:");
                } catch (Exception e) {
                    return e.getClass().getSimpleName();
                }
            }, true);

            Path cliOut = tmp.resolve("cli");
            Checker.check("L3-4 cli success", () -> attempt(() -> {
                String[] holder = new String[1];
                int code = cliExit(new String[]{"--input", MESSY.toString(), "--out", cliOut.toString()}, holder);
                return List.of(code, holder[0].startsWith("INFO: extracted 308 rows\n"), Files.exists(cliOut.resolve("report.md")));
            }), List.of(0, true, true));
            Checker.check("L3-4 cli errors", () -> {
                String[] holder = new String[1];
                int missingFile = cliExit(new String[]{"--input", MESSY.resolveSibling("nope.csv").toString(), "--out", cliOut.toString()}, holder);
                String first = holder[0].split("\n")[0];
                int noInput = cliExit(new String[]{"--out", cliOut.toString()}, holder);
                return List.of(missingFile, first.startsWith("Error: input file not found"), noInput, holder[0]);
            }, List.of(1, true, 2, "Error: --input is required\n"));
        } finally {
            deleteTree(tmp);
        }
        Checker.done();
    }

    /** Run cli(args), remember what it printed in holder[0], return its exit code. */
    static int cliExit(String[] args, String[] holder) {
        int[] code = new int[1];
        holder[0] = Checker.printed(() -> code[0] = cli(args));
        return code[0];
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
