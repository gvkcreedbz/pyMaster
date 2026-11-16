/* Day 09 - Practice: lists and sets.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 * Remember: List<Integer> holds Integer objects; compare them with .equals, not ==.
 */
import java.util.*;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Unique count   (Level 1 - Beginner)
    // How many DIFFERENT numbers are in the list?
    //   uniqueCount([1, 2, 2, 3, 3, 3]) -> 3      uniqueCount([]) -> 0
    // ---------------------------------------------------------------------------
    static int uniqueCount(List<Integer> items) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Swap the ends   (Level 1 - Beginner)
    // Swap the FIRST and the LAST item of the list itself (do not build a new list),
    // then return that same list. With fewer than 2 items nothing changes.
    //   swapEnds([A, B, C]) -> [C, B, A]       swapEnds([A]) -> [A]
    // ---------------------------------------------------------------------------
    static List<String> swapEnds(List<String> items) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Min and max   (Level 1 - Beginner)
    // Return a list with two numbers: [smallest, largest]. The list has at least one item.
    //   minMax([7, 2, 9, 4]) -> [2, 9]       minMax([5]) -> [5, 5]
    // ---------------------------------------------------------------------------
    static List<Integer> minMax(List<Integer> numbers) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Mutual followers   (Level 2 - Intermediate)
    // Names that appear in BOTH lists, as an alphabetically sorted list.
    //   commonFollowers([Diya, Kabir, Meera], [Meera, Sana, Kabir]) -> [Kabir, Meera]
    // Hint: a TreeSet keeps its items sorted; retainAll keeps only what the other set has.
    // ---------------------------------------------------------------------------
    static List<String> commonFollowers(List<String> a, List<String> b) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Friend suggestions   (Level 2 - Intermediate)
    // Suggest people from friendsOfFriends who are NOT already in myFriends and are
    // not me. Return an alphabetically sorted list without repeats.
    //   suggestFriends("Aarav", [Diya, Kabir], [Kabir, Sana, Aarav, Meera, Sana]) -> [Meera, Sana]
    // ---------------------------------------------------------------------------
    static List<String> suggestFriends(String me, List<String> myFriends, List<String> friendsOfFriends) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | De-duplicate, keep order   (Level 2 - Intermediate)
    // Remove repeated items but keep the FIRST occurrence of each, in the original order.
    //   dedupe([a, b, a, c, b]) -> [a, b, c]
    // Hint: a HashSet called seen; set.add(x) returns true only when x was new.
    // ---------------------------------------------------------------------------
    static List<String> dedupe(List<String> items) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-4 | Remove a value   (Level 2 - Intermediate)
    // Remove the FIRST item equal to value (not the item at that position!) from the
    // list itself and return the same list. If the value is not there, nothing changes.
    //   removeValue([3, 9, 1], 1) -> [3, 9]        removeValue([3, 9, 1], 7) -> [3, 9, 1]
    // Trap: list.remove(1) removes by POSITION. Use list.remove(Integer.valueOf(value)).
    // ---------------------------------------------------------------------------
    static List<Integer> removeValue(List<Integer> items, int value) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | First duplicate   (Level 3 - Challenge)
    // Reading left to right, return the first number that has already been seen.
    // Return null when all numbers are different.
    //   firstDuplicate([3, 1, 4, 1, 5, 3]) -> 1       firstDuplicate([1, 2, 3]) -> null
    // ---------------------------------------------------------------------------
    static Integer firstDuplicate(List<Integer> items) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Two numbers that add up   (Level 3 - Challenge)
    // True if two DIFFERENT positions in the list add up to target. Aim for ONE pass
    // using a set (not two nested loops).
    //   hasPairWithSum([2, 7, 11, 15], 9) -> true       hasPairWithSum([3], 6) -> false
    //   hasPairWithSum([3, 3], 6) -> true
    // ---------------------------------------------------------------------------
    static boolean hasPairWithSum(List<Integer> numbers, int target) {
        // TODO: write your code here
        return false;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 09 checks ---");
        Checker.check("L1-1 uniqueCount", () -> uniqueCount(List.of(1, 2, 2, 3, 3, 3)), 3);
        Checker.check("L1-1 uniqueCount empty", () -> uniqueCount(List.of()), 0);
        Checker.check("L1-2 swapEnds", () -> swapEnds(new ArrayList<>(List.of("A", "B", "C"))), List.of("C", "B", "A"));
        Checker.check("L1-2 swapEnds two items", () -> swapEnds(new ArrayList<>(List.of("x", "y"))), List.of("y", "x"));
        Checker.check("L1-2 swapEnds one item", () -> swapEnds(new ArrayList<>(List.of("A"))), List.of("A"));
        List<String> mine = new ArrayList<>(List.of("p", "q", "r", "s"));
        Checker.check("L1-2 swapEnds changes the list itself", () -> {
            swapEnds(mine);
            return mine;
        }, List.of("s", "q", "r", "p"));
        Checker.check("L1-3 minMax", () -> minMax(List.of(7, 2, 9, 4)), List.of(2, 9));
        Checker.check("L1-3 minMax one item", () -> minMax(List.of(5)), List.of(5, 5));
        Checker.check("L1-3 minMax negatives", () -> minMax(List.of(-3, 0, -8, 4)), List.of(-8, 4));
        Checker.check("L2-1 commonFollowers", () -> commonFollowers(List.of("Diya", "Kabir", "Meera"),
                List.of("Meera", "Sana", "Kabir")), List.of("Kabir", "Meera"));
        Checker.check("L2-1 commonFollowers nobody", () -> commonFollowers(List.of("A"), List.of("B")), List.of());
        Checker.check("L2-2 suggestFriends", () -> suggestFriends("Aarav", List.of("Diya", "Kabir"),
                List.of("Kabir", "Sana", "Aarav", "Meera", "Sana")), List.of("Meera", "Sana"));
        Checker.check("L2-3 dedupe", () -> dedupe(List.of("a", "b", "a", "c", "b")), List.of("a", "b", "c"));
        Checker.check("L2-3 dedupe keeps first-seen order", () -> dedupe(List.of("z", "a", "z", "m", "a")), List.of("z", "a", "m"));
        Checker.check("L2-4 removeValue", () -> removeValue(new ArrayList<>(List.of(3, 9, 1)), 1), List.of(3, 9));
        Checker.check("L2-4 removeValue missing value", () -> removeValue(new ArrayList<>(List.of(3, 9, 1)), 7), List.of(3, 9, 1));
        Checker.check("L2-4 removeValue only the first one", () -> removeValue(new ArrayList<>(List.of(4, 5, 4)), 4), List.of(5, 4));
        Checker.check("L3-1 firstDuplicate", () -> firstDuplicate(List.of(3, 1, 4, 1, 5, 3)), 1);
        Checker.check("L3-1 firstDuplicate none", () -> firstDuplicate(List.of(1, 2, 3)), null);
        Checker.check("L3-1 firstDuplicate large numbers", () -> firstDuplicate(List.of(1000, 2000, 1000)), 1000);
        Checker.check("L3-2 hasPairWithSum yes", () -> hasPairWithSum(List.of(2, 7, 11, 15), 9), true);
        Checker.check("L3-2 hasPairWithSum one item", () -> hasPairWithSum(List.of(3), 6), false);
        Checker.check("L3-2 hasPairWithSum equal items", () -> hasPairWithSum(List.of(3, 3), 6), true);
        Checker.check("L3-2 hasPairWithSum no", () -> hasPairWithSum(List.of(1, 2, 4), 10), false);
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
