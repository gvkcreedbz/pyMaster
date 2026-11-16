// SOLUTION FILE - try the hint ladder first!
/* Day 28 - Practice: JDBC and SQL with SQLite.
 *
 * Run:  java -cp "../../lib/*" Practice.java        (the portal's Run button adds the jars for you)
 * Every method receives an open JDBC Connection `conn`. The checker builds a small shop database in a
 * temporary file (deleted at the end). The table is:
 *   orders(order_id, order_date, region, category, product, quantity, unit_price, discount_pct, payment_method)
 * Revenue = quantity * unit_price * (1 - discount_pct / 100.0)    (note the 100.0: integer division is 0!)
 * Use ? placeholders (PreparedStatement) for any value that comes from a parameter - never glue text into SQL.
 * Column numbers in a ResultSet start at 1.
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.util.stream.*;

class Practice {

    // The answer shapes for L2-2 and L3-2.
    record ProductRevenue(String product, double revenue) {}

    record CustomerTotal(String name, double total) {}

    // ---------------------------------------------------------------------------
    // L1-1 | countOrders   (Level 1 - Beginner)
    // Return the number of rows in the orders table.
    // Hint: SELECT COUNT(*) FROM orders  -> rs.next() -> rs.getInt(1)
    // ---------------------------------------------------------------------------
    static int countOrders(Connection conn) throws SQLException {
        // >>> SOLUTION stub: return -1;
        try (Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery("SELECT COUNT(*) FROM orders")) {
            rs.next();
            return rs.getInt(1);
        }
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | ordersInRegion   (Level 1 - Beginner)
    // Return the order_id of every order of the given region, sorted ascending (a List<String>).
    // Use a PreparedStatement with a ? placeholder. A malicious region such as  West' OR '1'='1
    // must simply return an empty list.
    // ---------------------------------------------------------------------------
    static List<String> ordersInRegion(Connection conn, String region) throws SQLException {
        // >>> SOLUTION stub: return null;
        List<String> ids = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement("SELECT order_id FROM orders WHERE region = ? ORDER BY order_id")) {
            ps.setString(1, region);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    ids.add(rs.getString("order_id"));
                }
            }
        }
        return ids;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | createCustomers   (Level 1 - Beginner)
    // Create the table  customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT)  if it does
    // not exist yet, then insert every String[]{name, city} of `rows` (id is filled in by SQLite).
    // Use one PreparedStatement with addBatch() / executeBatch(). A JDBC connection starts in
    // auto-commit mode, so the rows are saved by themselves (unlike Python's sqlite3, no commit() needed).
    // ---------------------------------------------------------------------------
    static void createCustomers(Connection conn, List<String[]> rows) throws SQLException {
        // >>> SOLUTION
        try (Statement st = conn.createStatement()) {
            st.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT)");
        }
        try (PreparedStatement ps = conn.prepareStatement("INSERT INTO customers (name, city) VALUES (?, ?)")) {
            for (String[] row : rows) {
                ps.setString(1, row[0]);
                ps.setString(2, row[1]);
                ps.addBatch();
            }
            ps.executeBatch();
        }
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | revenueByPayment   (Level 2 - Intermediate)
    // Return a TreeMap payment_method -> total revenue rounded to 2 decimals. Use GROUP BY and
    // ROUND(SUM(...), 2) in the SQL.     e.g. {COD=444847.65, Card=396415.65, ...}
    // ---------------------------------------------------------------------------
    static Map<String, Double> revenueByPayment(Connection conn) throws SQLException {
        // >>> SOLUTION stub: return null;
        Map<String, Double> totals = new TreeMap<>();
        String sql = "SELECT payment_method, ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) "
                + "FROM orders GROUP BY payment_method";
        try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                totals.put(rs.getString(1), rs.getDouble(2));
            }
        }
        return totals;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | topProducts   (Level 2 - Intermediate)
    // Return the n products with the highest total revenue as ProductRevenue(product, revenue
    // rounded to 2 decimals), best first. n comes from a parameter: use a ? placeholder for LIMIT too.
    // ---------------------------------------------------------------------------
    static List<ProductRevenue> topProducts(Connection conn, int n) throws SQLException {
        // >>> SOLUTION stub: return null;
        List<ProductRevenue> top = new ArrayList<>();
        String sql = "SELECT product, ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS r "
                + "FROM orders GROUP BY product ORDER BY r DESC LIMIT ?";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, n);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    top.add(new ProductRevenue(rs.getString("product"), rs.getDouble("r")));
                }
            }
        }
        return top;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | ordersPerMonth   (Level 2 - Intermediate)
    // Return a TreeMap "2026-01" -> number of orders, using strftime('%Y-%m', order_date) in the SQL.
    // ---------------------------------------------------------------------------
    static Map<String, Integer> ordersPerMonth(Connection conn) throws SQLException {
        // >>> SOLUTION stub: return null;
        Map<String, Integer> counts = new TreeMap<>();
        String sql = "SELECT strftime('%Y-%m', order_date) AS month, COUNT(*) FROM orders GROUP BY month";
        try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                counts.put(rs.getString(1), rs.getInt(2));
            }
        }
        return counts;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | regionsAbove   (Level 3 - Challenge)
    // Return the regions whose TOTAL revenue is strictly greater than minRevenue, highest
    // revenue first (a List<String>). Use GROUP BY ... HAVING ... ORDER BY ... DESC with a ? placeholder.
    // ---------------------------------------------------------------------------
    static List<String> regionsAbove(Connection conn, double minRevenue) throws SQLException {
        // >>> SOLUTION stub: return null;
        List<String> regions = new ArrayList<>();
        String revenue = "SUM(quantity * unit_price * (1 - discount_pct / 100.0))";
        String sql = "SELECT region FROM orders GROUP BY region HAVING " + revenue + " > ? ORDER BY " + revenue + " DESC";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setDouble(1, minRevenue);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    regions.add(rs.getString(1));
                }
            }
        }
        return regions;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | customerTotals   (Level 3 - Challenge)
    // Tables: customers(id, name, city) and purchases(id, customer_id, amount).
    // Return a CustomerTotal(name, total spent) for EVERY customer (0 if they bought nothing),
    // highest total first, ties broken by name A-Z. Use LEFT JOIN + COALESCE + GROUP BY.
    // ---------------------------------------------------------------------------
    static List<CustomerTotal> customerTotals(Connection conn) throws SQLException {
        // >>> SOLUTION stub: return null;
        List<CustomerTotal> totals = new ArrayList<>();
        String sql = "SELECT c.name, COALESCE(SUM(p.amount), 0) AS total "
                + "FROM customers c LEFT JOIN purchases p ON p.customer_id = c.id "
                + "GROUP BY c.id ORDER BY total DESC, c.name";
        try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                totals.add(new CustomerTotal(rs.getString("name"), rs.getDouble("total")));
            }
        }
        return totals;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-3 | transfer   (Level 3 - Challenge)
    // Table accounts(id INTEGER PRIMARY KEY, owner TEXT, balance REAL).
    // Move `amount` from account fromId to toId as ONE transaction:
    //   conn.setAutoCommit(false) ... conn.commit()  /  conn.rollback() when something goes wrong.
    //   * source account missing or balance < amount -> throw new IllegalArgumentException("insufficient funds")
    //   * destination does not exist (UPDATE changes 0 rows) -> throw new IllegalArgumentException("unknown account")
    //     and the debit must be rolled back (all balances unchanged!).
    // Leave the connection in auto-commit mode when you are done (put that in a finally block).
    // ---------------------------------------------------------------------------
    static void transfer(Connection conn, int fromId, int toId, double amount) throws SQLException {
        // >>> SOLUTION
        conn.setAutoCommit(false);
        try {
            try (PreparedStatement read = conn.prepareStatement("SELECT balance FROM accounts WHERE id = ?")) {
                read.setInt(1, fromId);
                try (ResultSet rs = read.executeQuery()) {
                    if (!rs.next() || rs.getDouble(1) < amount) {
                        throw new IllegalArgumentException("insufficient funds");
                    }
                }
            }
            try (PreparedStatement debit = conn.prepareStatement("UPDATE accounts SET balance = balance - ? WHERE id = ?")) {
                debit.setDouble(1, amount);
                debit.setInt(2, fromId);
                debit.executeUpdate();
            }
            try (PreparedStatement credit = conn.prepareStatement("UPDATE accounts SET balance = balance + ? WHERE id = ?")) {
                credit.setDouble(1, amount);
                credit.setInt(2, toId);
                if (credit.executeUpdate() == 0) {
                    throw new IllegalArgumentException("unknown account");
                }
            }
            conn.commit();
        } catch (SQLException | RuntimeException e) {
            conn.rollback();
            throw e;
        } finally {
            conn.setAutoCommit(true);
        }
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    // The Checker's lambdas cannot throw SQLException, so attempt(...) wraps it for the tests.
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

    static Connection open(Path file) throws SQLException {
        return DriverManager.getConnection("jdbc:sqlite:" + file.toAbsolutePath());
    }

    /** Builds shop.db with the 300 sales orders (the same thing you do in Examples.java). */
    static Connection shopDb(Path dir) throws SQLException, IOException {
        Connection conn = open(dir.resolve("shop.db"));
        try (Statement st = conn.createStatement()) {
            st.execute("CREATE TABLE orders (order_id TEXT PRIMARY KEY, order_date TEXT, region TEXT, category TEXT, product TEXT, "
                    + "quantity INTEGER, unit_price INTEGER, discount_pct INTEGER, payment_method TEXT)");
        }
        List<String> lines = Files.readAllLines(Path.of("../../datasets/sales.csv"), StandardCharsets.UTF_8);
        conn.setAutoCommit(false);
        try (PreparedStatement ps = conn.prepareStatement("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)")) {
            for (String line : lines.subList(1, lines.size())) {
                String[] c = line.split(",", -1);
                for (int i = 0; i < 9; i++) {
                    if (i >= 5 && i <= 7) {
                        ps.setInt(i + 1, Integer.parseInt(c[i]));
                    } else {
                        ps.setString(i + 1, c[i]);
                    }
                }
                ps.addBatch();
            }
            ps.executeBatch();
        }
        conn.commit();
        conn.setAutoCommit(true);
        return conn;
    }

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> all = Files.walk(root)) {
            for (Path p : all.sorted(Comparator.reverseOrder()).toList()) {
                Files.deleteIfExists(p);
            }
        }
    }

    static List<String> customerRows(Connection conn) throws SQLException {
        List<String> rows = new ArrayList<>();
        try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery("SELECT id, name, city FROM customers ORDER BY id")) {
            while (rs.next()) {
                rows.add(rs.getInt(1) + ":" + rs.getString(2) + ":" + rs.getString(3));
            }
        }
        return rows;
    }

    static List<Double> balances(Connection conn) throws SQLException {
        List<Double> out = new ArrayList<>();
        try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery("SELECT balance FROM accounts ORDER BY id")) {
            while (rs.next()) {
                out.add(rs.getDouble(1));
            }
        }
        return out;
    }

    static String tryTransfer(Connection conn, int from, int to, double amount) {
        try {
            transfer(conn, from, to, amount);
            return "ok";
        } catch (Exception e) {
            return e.getMessage();
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("--- Day 28 checks ---");
        Path tmp = Files.createTempDirectory("day28");
        try (Connection shop = shopDb(tmp)) {
            Checker.check("L1-1 countOrders", () -> attempt(() -> countOrders(shop)), 300);
            Checker.check("L1-2 ordersInRegion", () -> attempt(() -> {
                List<String> west = ordersInRegion(shop, "West");
                return List.of(west.size(), west.get(0), west.get(1));
            }), List.of(75, "ORD1003", "ORD1005"));
            Checker.check("L1-2 injection attempt returns []", () -> attempt(() -> ordersInRegion(shop, "West' OR '1'='1")), List.of());

            Path custFile = tmp.resolve("customers.db");
            try (Connection c1 = open(custFile); Connection c2 = open(custFile)) {
                Checker.check("L1-3 createCustomers (saved, visible from a second connection)", () -> attempt(() -> {
                    createCustomers(c1, List.of(new String[]{"Asha", "Pune"}, new String[]{"Ben", "Delhi"}));
                    return customerRows(c2);
                }), List.of("1:Asha:Pune", "2:Ben:Delhi"));
                Checker.check("L1-3 createCustomers (name is NOT NULL)", () -> {
                    try (Statement st = c2.createStatement()) {
                        st.executeUpdate("INSERT INTO customers (name, city) VALUES (NULL, 'x')");
                        return false;
                    } catch (SQLException e) {
                        return String.valueOf(e.getMessage()).contains("NOT NULL");
                    }
                }, true);
            }

            Checker.check("L2-1 revenueByPayment", () -> attempt(() -> revenueByPayment(shop)),
                    Map.of("COD", 444847.65, "Card", 396415.65, "NetBanking", 321280.2, "UPI", 280698.05));
            Checker.check("L2-2 topProducts", () -> attempt(() -> topProducts(shop, 3)), List.of(
                    new ProductRevenue("Smartwatch", 298814.6), new ProductRevenue("Air Fryer", 279194.15),
                    new ProductRevenue("Running Shoes", 143652.1)));
            Checker.check("L2-2 topProducts (n comes from the parameter)", () -> attempt(() -> topProducts(shop, 1).size()), 1);
            Checker.check("L2-3 ordersPerMonth", () -> attempt(() -> ordersPerMonth(shop)), Map.of(
                    "2026-01", 26, "2026-02", 25, "2026-03", 37, "2026-04", 32, "2026-05", 30,
                    "2026-06", 35, "2026-07", 26, "2026-08", 32, "2026-09", 25, "2026-10", 32));
            Checker.check("L3-1 regionsAbove 330000", () -> attempt(() -> regionsAbove(shop, 330000)), List.of("West", "South", "East"));
            Checker.check("L3-1 regionsAbove 400000", () -> attempt(() -> regionsAbove(shop, 400000)), List.of("West"));

            try (Connection people = open(tmp.resolve("people.db"))) {
                try (Statement st = people.createStatement()) {
                    st.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)");
                    st.execute("CREATE TABLE purchases (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL)");
                    st.execute("INSERT INTO customers (name, city) VALUES ('Asha','Pune'), ('Ben','Delhi'), ('Chitra','Goa'), ('Dev','Goa')");
                    st.execute("INSERT INTO purchases (customer_id, amount) VALUES (1, 100), (1, 50), (2, 30)");
                }
                Checker.check("L3-2 customerTotals (LEFT JOIN keeps customers without purchases)", () -> attempt(() -> customerTotals(people)),
                        List.of(new CustomerTotal("Asha", 150.0), new CustomerTotal("Ben", 30.0),
                                new CustomerTotal("Chitra", 0.0), new CustomerTotal("Dev", 0.0)));
            }

            try (Connection bank = open(tmp.resolve("bank.db"))) {
                try (Statement st = bank.createStatement()) {
                    st.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance REAL)");
                    st.execute("INSERT INTO accounts VALUES (1, 'Asha', 1000), (2, 'Ben', 200)");
                }
                Checker.check("L3-3 transfer ok / insufficient / unknown account (rolled back)", () -> attempt(() -> List.of(
                        tryTransfer(bank, 1, 2, 300), balances(bank),
                        tryTransfer(bank, 1, 2, 5000), balances(bank),
                        tryTransfer(bank, 1, 99, 100), balances(bank))),
                        List.of("ok", List.of(700.0, 500.0), "insufficient funds", List.of(700.0, 500.0),
                                "unknown account", List.of(700.0, 500.0)));
                Checker.check("L3-3 transfer leaves auto-commit on", () -> attempt(() -> bank.getAutoCommit()), true);
            }
        } finally {
            deleteTree(tmp);
        }
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
