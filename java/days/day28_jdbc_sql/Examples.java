/* Day 28 - Code along: from a CSV file to a real database, and business questions in SQL.
 *
 * Run:  java -cp "../../lib/*" Examples.java      (the portal's Run button adds the jars for you)
 * Type each section yourself, run it, then change values and re-run.
 * The database is a temporary file that the program deletes at the end.
 */
import java.io.IOException;
import java.nio.file.*;
import java.sql.*;
import java.util.*;

class Examples {
    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("shop");
        Path dbFile = dir.resolve("shop.db");
        try {
            run(dbFile);
        } finally {
            Files.deleteIfExists(dbFile);
            Files.deleteIfExists(dir);
        }
    }

    static void run(Path dbFile) throws SQLException, IOException {
        // ---- 1. Connect: the URL says "SQLite, this file" (it is created if missing) ----
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbFile.toAbsolutePath())) {

            // ---- 2. Create a table (DDL) ----
            try (Statement st = conn.createStatement()) {
                st.execute("""
                        CREATE TABLE orders (
                            order_id TEXT PRIMARY KEY,
                            order_date TEXT, region TEXT, category TEXT, product TEXT,
                            quantity INTEGER, unit_price INTEGER, discount_pct INTEGER, payment_method TEXT)""");
            }

            // ---- 3. Insert 300 rows from the CSV: one PreparedStatement, one batch, ONE transaction ----
            List<String> lines = Files.readAllLines(Path.of("../../datasets/sales.csv"));
            conn.setAutoCommit(false);                      // JDBC saves every statement by itself unless you say otherwise
            try (PreparedStatement insert = conn.prepareStatement("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)")) {
                for (String line : lines.subList(1, lines.size())) {
                    String[] c = line.split(",", -1);
                    insert.setString(1, c[0]);
                    insert.setString(2, c[1]);
                    insert.setString(3, c[2]);
                    insert.setString(4, c[3]);
                    insert.setString(5, c[4]);
                    insert.setInt(6, Integer.parseInt(c[5]));     // parameter numbers start at 1
                    insert.setInt(7, Integer.parseInt(c[6]));
                    insert.setInt(8, Integer.parseInt(c[7]));
                    insert.setString(9, c[8]);
                    insert.addBatch();
                }
                insert.executeBatch();
            }
            conn.commit();                                  // make it permanent
            conn.setAutoCommit(true);

            // ---- 4. A query: ResultSet = a cursor over the answer rows ----
            try (Statement st = conn.createStatement();
                 ResultSet rs = st.executeQuery("SELECT COUNT(*) FROM orders")) {
                rs.next();                                  // move to the first (and only) row
                System.out.println("Orders in the database: " + rs.getInt(1));        // 300
            }

            // ---- 5. GROUP BY: revenue per region ----
            String revenue = "SUM(quantity * unit_price * (1 - discount_pct / 100.0))";   // 100.0, not 100!
            try (Statement st = conn.createStatement();
                 ResultSet rs = st.executeQuery("SELECT region, ROUND(" + revenue + ", 2) AS total FROM orders "
                         + "GROUP BY region ORDER BY total DESC")) {
                while (rs.next()) {
                    System.out.printf("%-6s %.2f%n", rs.getString("region"), rs.getDouble("total"));
                }
            }

            // ---- 6. ? placeholders: safe, even for evil input ----
            for (String region : new String[]{"West", "West' OR '1'='1"}) {
                try (PreparedStatement ps = conn.prepareStatement("SELECT COUNT(*) FROM orders WHERE region = ?")) {
                    ps.setString(1, region);
                    try (ResultSet rs = ps.executeQuery()) {
                        rs.next();
                        System.out.println(region + " -> " + rs.getInt(1) + " orders");       // 75, then 0
                    }
                }
            }

            // ---- 7. WHERE vs HAVING, ORDER BY, LIMIT ----
            String top = "SELECT product, ROUND(" + revenue + ", 2) AS total FROM orders WHERE order_date >= ? "
                    + "GROUP BY product HAVING " + revenue + " > ? ORDER BY total DESC LIMIT 3";
            try (PreparedStatement ps = conn.prepareStatement(top)) {
                ps.setString(1, "2026-06-01");              // WHERE filters ROWS before grouping
                ps.setDouble(2, 50000);                     // HAVING filters GROUPS after grouping
                try (ResultSet rs = ps.executeQuery()) {
                    while (rs.next()) {
                        System.out.println("  " + rs.getString(1) + " Rs." + rs.getDouble(2));
                    }
                }
            }

            // ---- 8. Months with strftime ----
            try (Statement st = conn.createStatement();
                 ResultSet rs = st.executeQuery("SELECT strftime('%Y-%m', order_date) AS month, COUNT(*) FROM orders GROUP BY month LIMIT 3")) {
                while (rs.next()) {
                    System.out.println(rs.getString(1) + ": " + rs.getInt(2) + " orders");
                }
            }

            // ---- 9. JOIN: customers and what they bought ----
            try (Statement st = conn.createStatement()) {
                st.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT)");
                st.execute("CREATE TABLE purchases (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL)");
                st.execute("INSERT INTO customers (name, city) VALUES ('Asha','Pune'), ('Ben','Delhi'), ('Chitra','Goa')");
                st.execute("INSERT INTO purchases (customer_id, amount) VALUES (1, 100), (1, 50), (2, 30)");
            }
            String join = "SELECT c.name, COALESCE(SUM(p.amount), 0) AS total FROM customers c "
                    + "LEFT JOIN purchases p ON p.customer_id = c.id GROUP BY c.id ORDER BY total DESC, c.name";
            try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery(join)) {
                while (rs.next()) {
                    System.out.println(rs.getString("name") + " spent " + rs.getDouble("total"));   // Chitra: 0.0 (LEFT JOIN)
                }
            }

            // ---- 10. A transaction: all or nothing ----
            try (Statement st = conn.createStatement()) {
                st.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance REAL)");
                st.execute("INSERT INTO accounts VALUES (1, 'Asha', 1000), (2, 'Ben', 200)");
            }
            conn.setAutoCommit(false);
            try (Statement st = conn.createStatement()) {
                st.executeUpdate("UPDATE accounts SET balance = balance - 500 WHERE id = 1");
                System.out.println("Something goes wrong before the credit...");
                conn.rollback();                            // undo the debit
            } finally {
                conn.setAutoCommit(true);
            }
            try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery("SELECT balance FROM accounts ORDER BY id")) {
                while (rs.next()) {
                    System.out.println("balance " + rs.getDouble(1));      // 1000.0 and 200.0: nothing was lost
                }
            }

            // ---- 11. An index makes searches on a column fast ----
            try (Statement st = conn.createStatement()) {
                st.execute("CREATE INDEX idx_orders_region ON orders(region)");
            }
            System.out.println("Index created");
        }
    }
}
