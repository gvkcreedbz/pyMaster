/* Day 03 - Practice: numbers and operators.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
import java.math.BigDecimal;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Discount price   (Level 1 - Beginner)
    // Return the price after taking percent off.
    //   applyDiscount(1000, 20) -> 800.0
    // ---------------------------------------------------------------------------
    static double applyDiscount(double price, double percent) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Add GST   (Level 1 - Beginner)
    // Return the price plus GST percent.
    //   addGst(1000, 18) -> 1180.0
    // ---------------------------------------------------------------------------
    static double addGst(double price, double gstPercent) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Even or odd   (Level 1 - Beginner)
    // Return true if n is even, otherwise false (hint: the remainder operator).
    //   isEven(10) -> true      isEven(7) -> false
    // ---------------------------------------------------------------------------
    static boolean isEven(int n) {
        // TODO: write your code here
        return false;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Minutes to hours   (Level 2 - Intermediate)
    // Return text like "2h 5m".
    //   hoursMinutes(125) -> "2h 5m"      hoursMinutes(45) -> "0h 45m"
    // ---------------------------------------------------------------------------
    static String hoursMinutes(int totalMinutes) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | BMI   (Level 2 - Intermediate)
    // BMI = weight in kg / (height in METRES) squared, rounded to 1 decimal.
    // Careful: heightCm is a whole number, so heightCm / 100 would drop the decimals.
    //   bmi(70, 175) -> 22.9
    // Hint to round to 1 decimal: Math.round(x * 10) / 10.0
    // ---------------------------------------------------------------------------
    static double bmi(double weightKg, int heightCm) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Average marks   (Level 2 - Intermediate)
    // Return the exact average of three whole-number marks, as a double.
    // The trap: (a + b + c) / 3 is an int division and drops the decimals.
    //   average(80, 90, 85) -> 85.0      average(1, 2, 2) -> 1.6666...
    // ---------------------------------------------------------------------------
    static double average(int a, int b, int c) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Home-loan EMI   (Level 3 - Challenge)
    // r = annualRatePercent / 12 / 100        n = years * 12
    // EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)      -> round to 2 decimals
    // Java has no ** operator: use Math.pow(base, exponent).
    //   emi(500000, 9, 5) -> 10379.18
    // ---------------------------------------------------------------------------
    static double emi(double principal, double annualRatePercent, int years) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Exact bill with BigDecimal   (Level 3 - Challenge)
    // Doubles cannot store 0.1 exactly, so banks use BigDecimal for money.
    // Return unit price times quantity as plain text, computed with BigDecimal
    // (build it from the TEXT, never from a double):
    //   exactTotal("19.99", 3) -> "59.97"      exactTotal("0.10", 3) -> "0.30"
    // Hint: new BigDecimal("19.99").multiply(BigDecimal.valueOf(3)).toPlainString()
    // ---------------------------------------------------------------------------
    static String exactTotal(String unitPrice, int qty) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-3 | Overflow-safe total   (Level 3 - Challenge)
    // Prices are stored in paise (1 rupee = 100 paise) as whole numbers. An int can
    // only hold about 2.1 billion, so the multiplication below must happen in long.
    // Return pricePaise * qty as a long.
    //   totalPaise(2_000_000_000, 3) -> 6000000000
    // Hint: convert ONE side to long BEFORE multiplying: (long) pricePaise * qty
    // ---------------------------------------------------------------------------
    static long totalPaise(int pricePaise, int qty) {
        // TODO: write your code here
        return 0;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 03 checks ---");
        Checker.check("L1-1 applyDiscount", () -> applyDiscount(1000, 20), 800.0);
        Checker.check("L1-1 applyDiscount #2", () -> applyDiscount(2499, 10), 2249.1);
        Checker.check("L1-2 addGst", () -> addGst(1000, 18), 1180.0);
        Checker.check("L1-3 isEven(10)", () -> isEven(10), true);
        Checker.check("L1-3 isEven(7)", () -> isEven(7), false);
        Checker.check("L1-3 isEven(0)", () -> isEven(0), true);
        Checker.check("L2-1 hoursMinutes(125)", () -> hoursMinutes(125), "2h 5m");
        Checker.check("L2-1 hoursMinutes(45)", () -> hoursMinutes(45), "0h 45m");
        Checker.check("L2-2 bmi(70, 175)", () -> bmi(70, 175), 22.9);
        Checker.check("L2-2 bmi(55, 160)", () -> bmi(55, 160), 21.5);
        Checker.check("L2-3 average", () -> average(80, 90, 85), 85.0);
        Checker.check("L2-3 average #2", () -> average(1, 2, 2), 5.0 / 3);
        Checker.check("L3-1 emi 5L/9%/5y", () -> emi(500000, 9, 5), 10379.18);
        Checker.check("L3-1 emi 12L/8.5%/20y", () -> emi(1200000, 8.5, 20), 10413.88);
        Checker.check("L3-2 exactTotal", () -> exactTotal("19.99", 3), "59.97");
        Checker.check("L3-2 exactTotal #2", () -> exactTotal("0.10", 3), "0.30");
        Checker.check("L3-3 totalPaise", () -> totalPaise(2_000_000_000, 3), 6_000_000_000L);
        Checker.check("L3-3 totalPaise #2", () -> totalPaise(4999, 2), 9998L);
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
