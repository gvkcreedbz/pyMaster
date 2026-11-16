/* Day 23 - Practice: regular expressions, immutability, clean code.
 *
 * Run:  java Practice.java
 * The sample text is ../../datasets/contacts_messy.txt (open it and look at it first).
 * Remember: inside a Java string every regex backslash is doubled:  \d  is written "\\d".
 */
import java.io.IOException;
import java.io.UncheckedIOException;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
class Practice {
    // ---------------------------------------------------------------------------
    // L1-1 | findEmails   (Level 1 - Beginner)
    // Return all valid-looking email addresses in the text, in order. Things like
    // "john@@example..com" must NOT match.  (letters/digits/._+- before @, a domain with a dot)
    // Hint: Pattern.compile(...), matcher.find() in a while loop, matcher.group().
    // ---------------------------------------------------------------------------
    static List<String> findEmails(String text) {
        // TODO: write your code here
        return null;
    }
    // ---------------------------------------------------------------------------
    // L1-2 | findPhoneNumbers   (Level 1 - Beginner)
    // Indian mobile numbers: 10 digits starting with 6, 7, 8 or 9; they may be written as
    // "+91 98765 43210", "+91-98765-43210", "98765 43210" or "9876543210".
    // Return the plain 10-digit strings in order. Toll-free "1800-123-4567" is NOT a mobile.
    // Hint: two groups (5 digits + 5 digits), join them: matcher.group(1) + matcher.group(2).
    // ---------------------------------------------------------------------------
    static List<String> findPhoneNumbers(String text) {
        // TODO: write your code here
        return null;
    }
    // ---------------------------------------------------------------------------
    // L1-3 | isValidPincode   (Level 1 - Beginner)
    // An Indian PIN code is exactly 6 digits and does not start with 0.
    //   isValidPincode("560001") -> true    "060001" -> false    "56001" -> false
    // Hint: Pattern.matches(regex, text) (or text.matches(regex)) must match the WHOLE text.
    // ---------------------------------------------------------------------------
    static boolean isValidPincode(String text) {
        // TODO: write your code here
        return false;
    }
    // ---------------------------------------------------------------------------
    // L2-1 | extractInvoices   (Level 2 - Intermediate)
    // Lines look like:  Invoice INV-2026-0042 dated 2026-11-03 total Rs. 12,450.50
    // Return a List<Invoice> (record below) with the id, the date text exactly as written, and the
    // amount as a double (remove the comma before Double.parseDouble). Use NAMED groups: (?<id>...)
    // ---------------------------------------------------------------------------
    record Invoice(String id, String date, double amount) {
    }
    static List<Invoice> extractInvoices(String text) {
        // TODO: write your code here
        return null;
    }
    // ---------------------------------------------------------------------------
    // L2-2 | maskCardNumbers   (Level 2 - Intermediate)
    // Replace every 16-digit card number (digits may be grouped by 4 with spaces or dashes) with
    // "**** **** **** " + its last four digits. Other numbers are untouched.
    //   maskCardNumbers("Card 1234 5678 9012 3456 used") -> "Card **** **** **** 3456 used"
    // Hint: text.replaceAll(regex, "**** **** **** $1") where $1 is the last group.
    // ---------------------------------------------------------------------------
    static String maskCardNumbers(String text) {
        // TODO: write your code here
        return text;
    }
    // ---------------------------------------------------------------------------
    // L2-3 | normalizeOrderIds   (Level 2 - Intermediate)
    // Orders are written ORD1001, ord1003 or ORD-1004. Return a SORTED list of the UNIQUE ids in the
    // standard form "ORD" + digits.   -> [ORD1001, ORD1002, ORD1003, ORD1004] for the sample file
    // Hint: (?i) makes the pattern ignore capitals; a TreeSet is sorted and has no duplicates.
    // ---------------------------------------------------------------------------
    static List<String> normalizeOrderIds(String text) {
        // TODO: write your code here
        return null;
    }
    // ---------------------------------------------------------------------------
    // L2-4 | priceWithGst (clean code: constants and guard clauses)   (Level 2 - Intermediate)
    // Add 18% GST to a price, rounded to 2 decimals:  priceWithGst(100) -> 118.0
    // Clean-code rules for this task:
    //   * NO magic number inside the method: declare  static final double GST_RATE = 0.18;
    //   * a negative price is a bug: FIRST throw new IllegalArgumentException("Price must not be negative")
    //     (a guard clause), then do the calculation without any nesting.
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    static final double GST_RATE = 0;
    static double priceWithGst(double price) {
        // TODO: write your code here
        return -1;
    }
    // ---------------------------------------------------------------------------
    // L3-1 | parseLogLine   (Level 3 - Challenge)
    // Line format: 2026-11-01 08:30:00 ERROR user=bob action=db_timeout ip=192.168.1.20
    // Return Optional.of(new LogEntry(date, time, level, user, action, ip)) (all text), or
    // Optional.empty() when the line does not follow the format EXACTLY.
    // Hint: named groups and matcher.matches().
    // ---------------------------------------------------------------------------
    record LogEntry(String date, String time, String level, String user, String action, String ip) {
    }
    static Optional<LogEntry> parseLogLine(String line) {
        // TODO: write your code here
        return Optional.empty();
    }
    // ---------------------------------------------------------------------------
    // L3-2 | Basket (an IMMUTABLE class)   (Level 3 - Challenge)
    // An immutable object never changes after it is built: it is safe to share and easy to test.
    // Write  final class Basket  with ONE private final field (a List<String>) and
    //   Basket(List<String> items)   keeps its OWN unmodifiable copy (hint: List.copyOf), so changing the
    //                                list you passed in later cannot change the basket
    //   List<String> items()         the items; callers must not be able to change them
    //   int size()
    //   Basket add(String item)      returns a NEW Basket with the item added at the end; this one is unchanged
    //   Basket remove(String item)   returns a NEW Basket without the first matching item (same basket if absent)
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    static final class Basket { Basket(List<String> items) { } List<String> items() { return null; } int size() { return -1; } Basket add(String item) { return this; } Basket remove(String item) { return this; } }
    // ======================= AUTO-CHECKER (do not edit below) ====================
    static String sampleText() {
        try {
            return Files.readString(Path.of("../../datasets/contacts_messy.txt"));
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
    static String errorOf(Runnable action) {
        try {
            action.run();
        } catch (Throwable e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
        return "no error";
    }
    public static void main(String[] args) {
        System.out.println("--- Day 23 checks ---");
        Checker.check("L1-1 findEmails (sample file)", () -> findEmails(sampleText()), List.of(
                "priya.sharma@example.com", "rahul_v99@mail.co.in", "help@shop-india.com", "meera.iyer@university.edu.in", "cto@startup.io"));
        Checker.check("L1-1 findEmails (tricky)", () -> findEmails("a@b.com, bad@@x..com and no-at.com; c.d+e@f-g.org."),
                List.of("a@b.com", "c.d+e@f-g.org"));
        Checker.check("L1-2 findPhoneNumbers (sample file)", () -> findPhoneNumbers(sampleText()),
                List.of("9876543210", "9123456780", "9000011111"));
        Checker.check("L1-2 findPhoneNumbers (tricky)", () -> findPhoneNumbers("Call 1800-123-4567 or 5876543210 or 8765432109"),
                List.of("8765432109"));
        Checker.check("L1-3 isValidPincode", () -> {
            List<Boolean> results = new ArrayList<>();
            for (String pin : new String[]{"560001", "060001", "56001", "5600011", "56000a"}) {
                results.add(isValidPincode(pin));
            }
            return results;
        }, List.of(true, false, false, false, false));
        Checker.check("L2-1 extractInvoices", () -> extractInvoices(sampleText()), List.of(
                new Invoice("INV-2026-0042", "2026-11-03", 12450.5),
                new Invoice("INV-2026-0043", "03/11/2026", 899.0)));
        Checker.check("L2-2 maskCardNumbers", () -> List.of(
                maskCardNumbers("Card 1234 5678 9012 3456 used"),
                maskCardNumbers("pay 1234-5678-9012-3456!"),
                maskCardNumbers("1234567890123456"),
                maskCardNumbers("PIN 1234 phone 9876543210")),
                List.of("Card **** **** **** 3456 used", "pay **** **** **** 3456!", "**** **** **** 3456", "PIN 1234 phone 9876543210"));
        Checker.check("L2-3 normalizeOrderIds", () -> normalizeOrderIds(sampleText()), List.of("ORD1001", "ORD1002", "ORD1003", "ORD1004"));
        Checker.check("L2-3 normalizeOrderIds (duplicates)", () -> normalizeOrderIds("ord-7 and ORD7, ORD12 then Ord3"),
                List.of("ORD12", "ORD3", "ORD7"));
        Checker.check("L2-4 priceWithGst", () -> List.of(priceWithGst(100), priceWithGst(99.99), priceWithGst(0),
                errorOf(() -> priceWithGst(-1))), List.of(118.0, 117.99, 0.0, "IllegalArgumentException: Price must not be negative"));
        Checker.check("L2-4 GST_RATE is a named constant (static final 0.18)", () -> {
            try {
                Field field = Practice.class.getDeclaredField("GST_RATE");
                int modifiers = field.getModifiers();
                return List.of(Modifier.isStatic(modifiers), Modifier.isFinal(modifiers), field.getDouble(null));
            } catch (ReflectiveOperationException e) {
                return "no field GST_RATE";
            }
        }, List.of(true, true, 0.18));
        String line = "2026-11-01 08:30:00 ERROR user=bob action=db_timeout ip=192.168.1.20";
        Checker.check("L3-1 parseLogLine", () -> parseLogLine(line),
                Optional.of(new LogEntry("2026-11-01", "08:30:00", "ERROR", "bob", "db_timeout", "192.168.1.20")));
        Checker.check("L3-1 parseLogLine (bad lines)", () -> List.of(parseLogLine("garbage line"),
                parseLogLine(line + " extra"), parseLogLine("2026-11-01 08:30:00 error user=bob action=x ip=1.2.3.4")),
                List.of(Optional.empty(), Optional.empty(), Optional.empty()));
        Checker.check("L3-2 Basket add / remove return NEW baskets", () -> {
            Basket empty = new Basket(List.of());
            Basket one = empty.add("Chai");
            Basket two = one.add("Samosa").add("Chai");
            Basket fewer = two.remove("Chai");
            return List.of(empty.size(), one.items(), two.items(), fewer.items(), two.remove("Pizza").items());
        }, List.of(0, List.of("Chai"), List.of("Chai", "Samosa", "Chai"), List.of("Samosa", "Chai"), List.of("Chai", "Samosa", "Chai")));
        Checker.check("L3-2 Basket keeps its own copy and cannot be changed from outside", () -> {
            List<String> mine = new ArrayList<>(List.of("Chai"));
            Basket basket = new Basket(mine);
            mine.add("Pizza");
            boolean refused = errorOf(() -> basket.items().add("Hack")).startsWith("UnsupportedOperationException");
            return List.of(basket.items(), refused, basket.size());
        }, List.of(List.of("Chai"), true, 1));
        Checker.check("L3-2 Basket is final with private final fields", () -> {
            boolean allPrivateFinal = true;
            for (Field field : Basket.class.getDeclaredFields()) {
                int modifiers = field.getModifiers();
                allPrivateFinal &= Modifier.isPrivate(modifiers) && Modifier.isFinal(modifiers);
            }
            return List.of(Modifier.isFinal(Basket.class.getModifiers()), allPrivateFinal);
        }, List.of(true, true));
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
