/* Day 08 - Practice: arrays.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 * Remember: an array has a FIXED length, so "remove" or "add" means "build a new array".
 */
import java.util.Arrays;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Cart total   (Level 1 - Beginner)
    // Return the sum of the prices (0 for an empty cart).
    //   cartTotal(new double[]{49.5, 30, 120}) -> 199.5
    // ---------------------------------------------------------------------------
    static double cartTotal(double[] prices) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Find an item   (Level 1 - Beginner)
    // Return the position (index) of the FIRST item equal to target, or -1 when it is
    // not in the array. Compare text with .equals.
    //   indexOf(new String[]{"milk", "bread", "eggs"}, "bread") -> 1
    //   indexOf(new String[]{"milk", "bread", "eggs"}, "tea")   -> -1
    // ---------------------------------------------------------------------------
    static int indexOf(String[] items, String target) {
        // TODO: write your code here
        return -2;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Top two scores   (Level 1 - Beginner)
    // Return a NEW array {highest, second highest}. Do NOT change the original array
    // (Arrays.sort changes the array it is given: sort a copy!). At least 2 scores.
    //   topTwo(new int[]{72, 95, 88, 60}) -> {95, 88}
    // ---------------------------------------------------------------------------
    static int[] topTwo(int[] scores) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Remove all   (Level 2 - Intermediate)
    // Return a NEW array without any copy of value. The original array stays unchanged.
    // (Count the keepers first, create the new array, then fill it.)
    //   removeAll(new int[]{1, 2, 3, 2, 2}, 2) -> {1, 3}
    // ---------------------------------------------------------------------------
    static int[] removeAll(int[] items, int value) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Running totals   (Level 2 - Intermediate)
    // Return a new array where each position holds the sum so far.
    //   runningTotals(new int[]{1, 2, 3, 4}) -> {1, 3, 6, 10}     runningTotals(new int[]{}) -> {}
    // ---------------------------------------------------------------------------
    static int[] runningTotals(int[] numbers) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Judges' trimmed average   (Level 2 - Intermediate)
    // Drop ONE lowest and ONE highest score, then return the average of the rest,
    // rounded to 2 decimals. At least 3 scores are always given. Do not change the
    // original array. (Rounding to 2 decimals: Math.round(x * 100) / 100.0)
    //   trimmedAverage(new int[]{9, 5, 8, 10, 7}) -> 8.0
    // ---------------------------------------------------------------------------
    static double trimmedAverage(int[] scores) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L2-4 | Sales table: totals per day   (Level 2 - Intermediate)
    // sales[shop][day] = rupees sold. Return an array with the total of each DAY
    // (each column) over all shops. All rows have the same length; no rows -> {}.
    //   columnTotals(new int[][]{{10, 20, 30}, {5, 5, 5}}) -> {15, 25, 35}
    // ---------------------------------------------------------------------------
    static int[] columnTotals(int[][] sales) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Rotate right   (Level 3 - Challenge)
    // Return a NEW array with the last k items moved to the front. k may be bigger
    // than the length (wrap around), may be 0, and the array may be empty.
    //   rotate(new int[]{1, 2, 3, 4, 5}, 2) -> {4, 5, 1, 2, 3}     rotate(new int[]{1, 2, 3}, 4) -> {3, 1, 2}
    // Idea: the item at position i moves to position (i + k) % length.
    // ---------------------------------------------------------------------------
    static int[] rotate(int[] items, int k) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Merge two sorted arrays   (Level 3 - Challenge)
    // Both inputs are already sorted ascending. Return one sorted array WITHOUT
    // calling Arrays.sort (walk through both arrays with two index variables).
    //   mergeSorted(new int[]{1, 4, 7}, new int[]{2, 3, 9, 10}) -> {1, 2, 3, 4, 7, 9, 10}
    // ---------------------------------------------------------------------------
    static int[] mergeSorted(int[] a, int[] b) {
        // TODO: write your code here
        return null;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 08 checks ---");
        Checker.check("L1-1 cartTotal", () -> cartTotal(new double[]{49.5, 30, 120}), 199.5);
        Checker.check("L1-1 cartTotal of an empty cart", () -> cartTotal(new double[0]), 0.0);
        String[] cart = {"milk", "bread", "eggs"};
        Checker.check("L1-2 indexOf found", () -> indexOf(cart, "bread"), 1);
        Checker.check("L1-2 indexOf last", () -> indexOf(cart, "eggs"), 2);
        Checker.check("L1-2 indexOf missing", () -> indexOf(cart, "tea"), -1);
        Checker.check("L1-2 indexOf compares text, not objects", () -> indexOf(cart, new String("milk")), 0);
        int[] scores = {72, 95, 88, 60};
        Checker.check("L1-3 topTwo", () -> topTwo(scores), new int[]{95, 88});
        Checker.check("L1-3 topTwo leaves the input alone", () -> scores, new int[]{72, 95, 88, 60});
        Checker.check("L1-3 topTwo with duplicates", () -> topTwo(new int[]{50, 90, 90, 10}), new int[]{90, 90});
        int[] original = {1, 2, 3, 2, 2};
        Checker.check("L2-1 removeAll", () -> removeAll(original, 2), new int[]{1, 3});
        Checker.check("L2-1 removeAll leaves the input alone", () -> original, new int[]{1, 2, 3, 2, 2});
        Checker.check("L2-1 removeAll everything", () -> removeAll(new int[]{4, 4}, 4), new int[0]);
        Checker.check("L2-1 removeAll nothing to remove", () -> removeAll(new int[]{1, 2}, 9), new int[]{1, 2});
        Checker.check("L2-2 runningTotals", () -> runningTotals(new int[]{1, 2, 3, 4}), new int[]{1, 3, 6, 10});
        Checker.check("L2-2 runningTotals empty", () -> runningTotals(new int[0]), new int[0]);
        Checker.check("L2-2 runningTotals with negatives", () -> runningTotals(new int[]{5, -2, 4}), new int[]{5, 3, 7});
        int[] judges = {9, 5, 8, 10, 7};
        Checker.check("L2-3 trimmedAverage", () -> trimmedAverage(judges), 8.0);
        Checker.check("L2-3 trimmedAverage leaves the input alone", () -> judges, new int[]{9, 5, 8, 10, 7});
        Checker.check("L2-3 trimmedAverage rounds to 2 decimals", () -> trimmedAverage(new int[]{1, 5, 6, 8, 100}), 6.33);
        Checker.check("L2-4 columnTotals", () -> columnTotals(new int[][]{{10, 20, 30}, {5, 5, 5}}), new int[]{15, 25, 35});
        Checker.check("L2-4 columnTotals 3 shops", () -> columnTotals(new int[][]{{1, 2}, {3, 4}, {5, 6}}), new int[]{9, 12});
        Checker.check("L2-4 columnTotals empty", () -> columnTotals(new int[0][0]), new int[0]);
        Checker.check("L3-1 rotate 2", () -> rotate(new int[]{1, 2, 3, 4, 5}, 2), new int[]{4, 5, 1, 2, 3});
        Checker.check("L3-1 rotate wraps around", () -> rotate(new int[]{1, 2, 3}, 4), new int[]{3, 1, 2});
        Checker.check("L3-1 rotate by 0", () -> rotate(new int[]{1, 2, 3}, 0), new int[]{1, 2, 3});
        Checker.check("L3-1 rotate empty", () -> rotate(new int[0], 3), new int[0]);
        Checker.check("L3-2 mergeSorted", () -> mergeSorted(new int[]{1, 4, 7}, new int[]{2, 3, 9, 10}),
                new int[]{1, 2, 3, 4, 7, 9, 10});
        Checker.check("L3-2 mergeSorted with an empty side", () -> mergeSorted(new int[0], new int[]{5, 6}), new int[]{5, 6});
        Checker.check("L3-2 mergeSorted keeps duplicates", () -> mergeSorted(new int[]{2, 2}, new int[]{2}), new int[]{2, 2, 2});
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
