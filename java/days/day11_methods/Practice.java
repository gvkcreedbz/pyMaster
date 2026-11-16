/* Day 11 - Practice: methods.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 * Java has no default parameter values: to make a parameter optional, write one more method with the same name (overloading).
 */
import java.util.*;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Greeting with and without a word   (Level 1 - Beginner)
    // Write TWO methods called greet:
    //   greet("Aarav")            -> "Hello, Aarav!"
    //   greet("Diya", "Namaste")  -> "Namaste, Diya!"
    // The one-parameter version should call the two-parameter one.
    // ---------------------------------------------------------------------------
    static String greet(String name) {
        // TODO: write your code here
        return null;
    }

    static String greet(String name, String greeting) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Total with tax   (Level 1 - Beginner)
    // total = price * qty * (1 + taxPercent / 100), rounded to 2 decimals
    // (Math.round(x * 100) / 100.0). Write THREE overloads; the missing values are
    // qty = 1 and taxPercent = 18.
    //   calcTotal(100) -> 118.0     calcTotal(50, 2) -> 118.0     calcTotal(100, 3, 5) -> 315.0
    // ---------------------------------------------------------------------------
    static double calcTotal(double price) {
        // TODO: write your code here
        return -1;
    }

    static double calcTotal(double price, int qty) {
        // TODO: write your code here
        return -1;
    }

    static double calcTotal(double price, int qty, int taxPercent) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Average of anything   (Level 1 - Beginner)
    // Accept any number of ints with varargs (int... numbers). Inside, numbers is an
    // int[]. With no numbers at all return 0.
    //   average(4, 8, 6) -> 6.0      average(5) -> 5.0      average() -> 0.0
    // ---------------------------------------------------------------------------
    static double average(int... numbers) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Profile line   (Level 2 - Intermediate)
    // Java has no **kwargs, so the fields come in as a map. Return "key=value" pairs
    // joined by "; ", with the keys in alphabetical order. No fields -> "".
    //   formatProfile({name=Aarav, age=25}) -> "age=25; name=Aarav"
    // Hint: new TreeMap<>(fields) sorts the keys; String.join("; ", list) glues the pieces.
    // ---------------------------------------------------------------------------
    static String formatProfile(Map<String, Object> fields) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Several return values   (Level 2 - Intermediate)
    // A method returns ONE thing, so return a double[] holding
    // {smallest, largest, average rounded to 2 decimals}. At least one number is given.
    //   minMaxAvg(new int[]{4, 8, 6}) -> {4.0, 8.0, 6.0}      minMaxAvg(new int[]{1, 2}) -> {1.0, 2.0, 1.5}
    // ---------------------------------------------------------------------------
    static double[] minMaxAvg(int[] numbers) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Fibonacci (recursion)   (Level 2 - Intermediate)
    // fib(0) = 0, fib(1) = 1, fib(n) = fib(n - 1) + fib(n - 2).   fib(7) -> 13
    // Use recursion (the method calls itself). n is at most 20.
    // ---------------------------------------------------------------------------
    static int fib(int n) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L2-4 | Raise the prices   (Level 2 - Intermediate)
    // Add extra to EVERY price in the array itself. The method returns nothing: the
    // caller sees the change because an array is passed by reference (the method gets
    // the same array, not a copy).
    //   int[] p = {100, 250};  raisePrices(p, 10);  -> p is now {110, 260}
    // ---------------------------------------------------------------------------
    static void raisePrices(int[] prices, int extra) {
        // TODO: write your code here
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Flatten nested lists   (Level 3 - Challenge)
    // The items of nested are either an Integer or another list (of any depth).
    // Return one flat List<Integer> in the same order. Use recursion.
    //   flatten([1, [2, [3, 4]], 5]) -> [1, 2, 3, 4, 5]       flatten([]) -> []
    // Hint: "item instanceof List<?> inner" is true when item is a list and gives it the name inner.
    // For a plain number use (Integer) item.
    // ---------------------------------------------------------------------------
    static List<Integer> flatten(List<?> nested) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Add without touching the original   (Level 3 - Challenge)
    // Return a NEW list: all the items followed by item. The list that came in must
    // stay unchanged (the checker even passes a read-only List.of, which refuses changes).
    //   withItem([a, b], "c") -> [a, b, c]  (and the original is still [a, b])
    // ---------------------------------------------------------------------------
    static List<String> withItem(List<String> items, String item) {
        // TODO: write your code here
        return null;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 11 checks ---");
        Checker.check("L1-1 greet with a word", () -> greet("Diya", "Namaste"), "Namaste, Diya!");
        Checker.check("L1-1 greet without a word", () -> greet("Aarav"), "Hello, Aarav!");
        Checker.check("L1-2 calcTotal one argument", () -> calcTotal(100), 118.0);
        Checker.check("L1-2 calcTotal two arguments", () -> calcTotal(50, 2), 118.0);
        Checker.check("L1-2 calcTotal three arguments", () -> calcTotal(100, 3, 5), 315.0);
        Checker.check("L1-2 calcTotal rounds to 2 decimals", () -> calcTotal(19.99, 3), 70.76);
        Checker.check("L1-3 average", () -> average(4, 8, 6), 6.0);
        Checker.check("L1-3 average of one", () -> average(5), 5.0);
        Checker.check("L1-3 average of nothing", () -> average(), 0.0);
        Checker.check("L1-3 average of an array", () -> average(new int[]{1, 2}), 1.5);
        Checker.check("L2-1 formatProfile", () -> formatProfile(Map.of("name", "Aarav", "age", 25)), "age=25; name=Aarav");
        Checker.check("L2-1 formatProfile three fields", () -> formatProfile(Map.of("city", "Pune", "name", "Diya", "age", 30)),
                "age=30; city=Pune; name=Diya");
        Checker.check("L2-1 formatProfile empty", () -> formatProfile(Map.of()), "");
        Checker.check("L2-2 minMaxAvg", () -> minMaxAvg(new int[]{4, 8, 6}), new double[]{4, 8, 6.0});
        Checker.check("L2-2 minMaxAvg two numbers", () -> minMaxAvg(new int[]{1, 2}), new double[]{1, 2, 1.5});
        Checker.check("L2-2 minMaxAvg rounds", () -> minMaxAvg(new int[]{1, 2, 2}), new double[]{1, 2, 1.67});
        Checker.check("L2-3 fib", () -> List.of(fib(0), fib(1), fib(2), fib(7), fib(15)), List.of(0, 1, 1, 13, 610));
        int[] prices = {100, 250};
        Checker.check("L2-4 raisePrices changes the array", () -> {
            raisePrices(prices, 10);
            return prices;
        }, new int[]{110, 260});
        Checker.check("L2-4 raisePrices empty array", () -> {
            int[] none = {};
            raisePrices(none, 5);
            return none;
        }, new int[0]);
        Checker.check("L3-1 flatten", () -> flatten(List.of(1, List.of(2, List.of(3, 4)), 5)), List.of(1, 2, 3, 4, 5));
        Checker.check("L3-1 flatten empty", () -> flatten(List.of()), List.of());
        Checker.check("L3-1 flatten deep", () -> flatten(List.of(List.of(List.of(1)))), List.of(1));
        List<String> base = List.of("a", "b");
        Checker.check("L3-2 withItem", () -> withItem(base, "c"), List.of("a", "b", "c"));
        Checker.check("L3-2 withItem leaves the original alone", () -> base, List.of("a", "b"));
        Checker.check("L3-2 withItem on an empty list", () -> withItem(List.of(), "x"), List.of("x"));
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
