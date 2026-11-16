// SOLUTION FILE - try the hint ladder first!
/* Day 17 - Practice: exceptions, try-with-resources and logging.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.Callable;
import java.util.logging.Handler;
import java.util.logging.Formatter;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.StreamHandler;

class Practice {

    /** Raised when a withdrawal is bigger than the balance. (given - don't edit) */
    static class InsufficientFundsException extends Exception {
        InsufficientFundsException(String message) {
            super(message);
        }
    }

    /** A connection that must always be closed again; LOG records what happened. (given - don't edit) */
    static class Connection implements AutoCloseable {
        static final List<String> LOG = new ArrayList<>();

        Connection() {
            LOG.add("open");
        }

        void send(String message) {
            LOG.add(message);
        }

        @Override
        public void close() {
            LOG.add("close");
        }
    }

    /** One payment of a batch; amount is text and may be null. (given - don't edit) */
    record Payment(int id, String amount) {
    }

    /** The result of checking a batch. (given - don't edit) */
    record Report(List<Integer> ok, Map<Integer, String> failed) {
    }

    // ---------------------------------------------------------------------------
    // L1-1 | safeInt   (Level 1 - Beginner)
    // Convert text to an int. If that is impossible return defaultValue (never crash).
    //   safeInt("42", 0) -> 42    safeInt("abc", 0) -> 0    safeInt("12.5", -1) -> -1
    //   safeInt(null, 7) -> 7
    // Hint: Integer.parseInt throws NumberFormatException (also for null).
    // ---------------------------------------------------------------------------
    static int safeInt(String text, int defaultValue) {
        // >>> SOLUTION stub: return 0;
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException e) {
            return defaultValue;
        }
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | safeDivide   (Level 1 - Beginner)
    // Return a / b (whole-number division), or null when b is zero.
    //   safeDivide(10, 2) -> 5    safeDivide(1, 0) -> null
    // Hint: dividing ints by zero throws ArithmeticException.
    // ---------------------------------------------------------------------------
    static Integer safeDivide(int a, int b) {
        // >>> SOLUTION stub: return 0;
        try {
            return a / b;
        } catch (ArithmeticException e) {
            return null;
        }
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | readFirstLine   (Level 1 - Beginner)
    // Return the first line of the file (no new line at the end). If the file does
    // not exist, cannot be read, or is empty, return "" (an empty text).
    // Hint: Files.readAllLines(path) throws the checked IOException.
    // ---------------------------------------------------------------------------
    static String readFirstLine(Path path) {
        // >>> SOLUTION stub: return null;
        try {
            List<String> lines = Files.readAllLines(path);
            return lines.isEmpty() ? "" : lines.get(0);
        } catch (IOException e) {
            return "";
        }
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | parseAge   (Level 2 - Intermediate)
    // Trim the spaces, then:
    //   not made only of digits -> throw new IllegalArgumentException("Age must be a whole number")
    //   a number above 120      -> throw new IllegalArgumentException("Age must be between 0 and 120")
    // otherwise return the age as an int.   parseAge(" 25 ") -> 25    parseAge("abc") -> error
    // ---------------------------------------------------------------------------
    static int parseAge(String text) {
        // >>> SOLUTION stub: return 0;
        text = text.trim();
        if (!text.matches("\\d{1,9}")) {
            throw new IllegalArgumentException("Age must be a whole number");
        }
        int age = Integer.parseInt(text);
        if (age > 120) {
            throw new IllegalArgumentException("Age must be between 0 and 120");
        }
        return age;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | withdraw   (Level 2 - Intermediate)
    // Return balance - amount. If amount is bigger than balance throw
    //   new InsufficientFundsException("Need Rs. " + (amount - balance) + " more")
    // (the exception class is given at the top; it is a CHECKED exception, so the
    // method already says "throws InsufficientFundsException").
    // ---------------------------------------------------------------------------
    static int withdraw(int balance, int amount) throws InsufficientFundsException {
        // >>> SOLUTION stub: return 0;
        if (amount > balance) {
            throw new InsufficientFundsException("Need Rs. " + (amount - balance) + " more");
        }
        return balance - amount;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | retry   (Level 2 - Intermediate)
    // Call task.call() up to `attempts` times (attempts is at least 1). Return the first
    // successful result. If EVERY attempt throws, throw the LAST exception again.
    // ---------------------------------------------------------------------------
    static <T> T retry(Callable<T> task, int attempts) throws Exception {
        // >>> SOLUTION stub: return null;
        Exception last = null;
        for (int i = 0; i < attempts; i++) {
            try {
                return task.call();
            } catch (Exception e) {
                last = e;
            }
        }
        throw last;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-4 | runReport with try-with-resources   (Level 2 - Intermediate)
    // Open a Connection in a try-with-resources block, then c.send("query").
    // If fail is true, throw new IllegalStateException("boom") after sending.
    // Return "ok" on success; if an IllegalStateException happens, catch it and
    // return "failed: " + its message. The connection must be closed in BOTH cases
    // (try-with-resources does that for you: Connection.LOG shows open, query, close).
    // ---------------------------------------------------------------------------
    static String runReport(boolean fail) {
        // >>> SOLUTION stub: return null;
        try (Connection c = new Connection()) {
            c.send("query");
            if (fail) {
                throw new IllegalStateException("boom");
            }
            return "ok";
        } catch (IllegalStateException e) {
            return "failed: " + e.getMessage();
        }
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | processPayments   (Level 3 - Challenge)
    // Check a batch of payments (record Payment(int id, String amount) is given).
    // Return new Report(okIds, failedMap): okIds = ids that are fine, in the original order;
    // failedMap = id -> reason. Rules, checked in this order:
    //   amount is null                     -> "missing amount"
    //   amount cannot be read as a double  -> "amount must be a number"
    //   amount <= 0                        -> "amount must be positive"
    //   amount > 50000                     -> "amount too large"
    // "250" counts as 250 and "99.5" as 99.5. One bad payment must never stop the others.
    // ---------------------------------------------------------------------------
    static Report processPayments(List<Payment> payments) {
        // >>> SOLUTION stub: return new Report(new ArrayList<>(), new TreeMap<>());
        List<Integer> ok = new ArrayList<>();
        Map<Integer, String> failed = new TreeMap<>();
        for (Payment p : payments) {
            if (p.amount() == null) {
                failed.put(p.id(), "missing amount");
                continue;
            }
            double amount;
            try {
                amount = Double.parseDouble(p.amount());
            } catch (NumberFormatException e) {
                failed.put(p.id(), "amount must be a number");
                continue;
            }
            if (amount <= 0) {
                failed.put(p.id(), "amount must be positive");
            } else if (amount > 50000) {
                failed.put(p.id(), "amount too large");
            } else {
                ok.add(p.id());
            }
        }
        return new Report(ok, failed);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | makeLogger   (Level 3 - Challenge)
    // Return a java.util.logging.Logger called `name` that writes into the stream `out`
    // using the format  LEVEL - message   (for example "SEVERE - payment failed",
    // one line per message, each line ending in \n). Level INFO: FINE messages must NOT appear.
    // Recipe: Logger.getLogger(name); setUseParentHandlers(false) (no console copy);
    // setLevel(Level.INFO); new StreamHandler(out, formatter) where your Formatter's
    // format(LogRecord r) returns r.getLevel().getName() + " - " + formatMessage(r) + "\n";
    // logger.addHandler(handler). (The checker flushes the handler for you.)
    // ---------------------------------------------------------------------------
    static Logger makeLogger(String name, OutputStream out) {
        // >>> SOLUTION stub: return Logger.getLogger(name);
        Logger logger = Logger.getLogger(name);
        logger.setUseParentHandlers(false);
        logger.setLevel(Level.INFO);
        StreamHandler handler = new StreamHandler(out, new Formatter() {
            @Override
            public String format(LogRecord r) {
                return r.getLevel().getName() + " - " + formatMessage(r) + "\n";
            }
        });
        handler.setLevel(Level.ALL);
        logger.addHandler(handler);
        return logger;
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    /** Code that may throw anything (used by errorOf). */
    interface Risky {
        void run() throws Exception;
    }

    /** ["ExceptionName", "message"] if run() throws, else ["no error"]. */
    static List<String> errorOf(Risky r) {
        try {
            r.run();
        } catch (Exception e) {
            return List.of(e.getClass().getSimpleName(), String.valueOf(e.getMessage()));
        }
        return List.of("no error");
    }

    static <T> T value(Callable<T> c) {
        try {
            return c.call();
        } catch (Exception e) {
            throw new RuntimeException(e.getClass().getSimpleName() + ": " + e.getMessage());
        }
    }

    static List<String> firstLines() throws IOException {
        Path tmp = Files.createTempDirectory("day17");
        try {
            Files.writeString(tmp.resolve("a.txt"), "first\nsecond\n");
            Files.writeString(tmp.resolve("empty.txt"), "");
            return List.of(readFirstLine(tmp.resolve("a.txt")), readFirstLine(tmp.resolve("missing.txt")),
                    readFirstLine(tmp.resolve("empty.txt")));
        } finally {
            Files.deleteIfExists(tmp.resolve("a.txt"));
            Files.deleteIfExists(tmp.resolve("empty.txt"));
            Files.deleteIfExists(tmp);
        }
    }

    static List<Object> reports() {
        Connection.LOG.clear();
        String good = runReport(false);
        List<String> goodLog = new ArrayList<>(Connection.LOG);
        Connection.LOG.clear();
        String bad = runReport(true);
        return List.of(good, goodLog, bad, new ArrayList<>(Connection.LOG));
    }

    static List<String> loggedLines() {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        Logger lg = makeLogger("day17-test", out);
        lg.info("order placed");
        lg.fine("hidden detail");
        lg.severe("payment failed");
        for (Handler h : lg.getHandlers()) {
            h.flush();
        }
        return Arrays.asList(out.toString(StandardCharsets.UTF_8).trim().split("\n"));
    }

    public static void main(String[] args) {
        System.out.println("--- Day 17 checks ---");
        Checker.check("L1-1 safeInt", () -> List.of(safeInt("42", 0), safeInt("abc", 0), safeInt("12.5", -1), safeInt(null, 7)),
                List.of(42, 0, -1, 7));
        Checker.check("L1-2 safeDivide", () -> Arrays.asList(safeDivide(10, 2), safeDivide(7, 2), safeDivide(1, 0)),
                Arrays.asList(5, 3, null));
        Checker.check("L1-3 readFirstLine", () -> value(Practice::firstLines), List.of("first", "", ""));
        Checker.check("L2-1 parseAge ok", () -> List.of(parseAge(" 25 "), parseAge("0"), parseAge("120")), List.of(25, 0, 120));
        Checker.check("L2-1 parseAge text", () -> errorOf(() -> parseAge("abc")),
                List.of("IllegalArgumentException", "Age must be a whole number"));
        Checker.check("L2-1 parseAge range", () -> errorOf(() -> parseAge("150")),
                List.of("IllegalArgumentException", "Age must be between 0 and 120"));
        Checker.check("L2-2 withdraw ok", () -> value(() -> withdraw(1000, 400)), 600);
        Checker.check("L2-2 withdraw error", () -> errorOf(() -> withdraw(100, 600)),
                List.of("InsufficientFundsException", "Need Rs. 500 more"));
        int[] calls = {0};
        Checker.check("L2-3 retry succeeds on 3rd try", () -> value(() -> {
            String result = retry(() -> {
                calls[0]++;
                if (calls[0] < 3) {
                    throw new java.io.IOException("network down");
                }
                return "connected";
            }, 5);
            return List.of(result, calls[0]);
        }), List.of("connected", 3));
        Checker.check("L2-3 retry gives up", () -> errorOf(() -> retry(() -> Integer.parseInt("x"), 3)),
                List.of("NumberFormatException", "For input string: \"x\""));
        Checker.check("L2-4 try-with-resources", Practice::reports,
                List.of("ok", List.of("open", "query", "close"), "failed: boom", List.of("open", "query", "close")));
        Checker.check("L3-1 processPayments", () -> processPayments(List.of(
                        new Payment(1, "250"), new Payment(2, "abc"), new Payment(3, null), new Payment(4, "-5"),
                        new Payment(5, "70000"), new Payment(6, "99.5"), new Payment(7, ""))),
                new Report(List.of(1, 6), Map.of(2, "amount must be a number", 3, "missing amount", 4, "amount must be positive",
                        5, "amount too large", 7, "amount must be a number")));
        Checker.check("L3-2 makeLogger", Practice::loggedLines, List.of("INFO - order placed", "SEVERE - payment failed"));
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
