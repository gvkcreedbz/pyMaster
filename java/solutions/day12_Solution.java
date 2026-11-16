// SOLUTION FILE - try the hint ladder first!
/* Day 12 - Practice: lambdas, method references and streams.
 *
 * Run:  java Practice.java
 * Tip: say the pipeline out loud first: "take the list, keep only..., turn each into..., collect".
 */
import java.util.*;
import java.util.function.*;
import java.util.stream.*;

class Practice {

    // A tiny data class for the music chart (records are explained properly on Day 13).
    record Song(String title, int plays) {}

    // ---------------------------------------------------------------------------
    // L1-1 | Squares   (Level 1 - Beginner)
    // Return the squares of 1..n as a List<Integer>.
    //   squares(4) -> [1, 4, 9, 16]      squares(0) -> []
    // Hint: IntStream.rangeClosed(1, n) ... .boxed().toList()
    // ---------------------------------------------------------------------------
    static List<Integer> squares(int n) {
        // >>> SOLUTION stub: return null;
        return IntStream.rangeClosed(1, n).map(i -> i * i).boxed().toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Even numbers   (Level 1 - Beginner)
    // Keep only the even numbers, in the original order.
    //   evenNumbers([1, 2, 3, 4, 6]) -> [2, 4, 6]
    // ---------------------------------------------------------------------------
    static List<Integer> evenNumbers(List<Integer> numbers) {
        // >>> SOLUTION stub: return null;
        return numbers.stream().filter(n -> n % 2 == 0).toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Uppercase list   (Level 1 - Beginner)
    // Return every word in UPPER CASE. Try a method reference (String::toUpperCase).
    //   toUpper(["ab", "Cd"]) -> ["AB", "CD"]
    // ---------------------------------------------------------------------------
    static List<String> toUpper(List<String> words) {
        // >>> SOLUTION stub: return null;
        return words.stream().map(String::toUpperCase).toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Affordable items   (Level 2 - Intermediate)
    // menu maps item name -> price. Return the names whose price is <= budget,
    // sorted A-Z.
    //   affordable({chai=20, pizza=300, samosa=15}, 50) -> ["chai", "samosa"]
    // ---------------------------------------------------------------------------
    static List<String> affordable(Map<String, Integer> menu, int budget) {
        // >>> SOLUTION stub: return null;
        return menu.entrySet().stream()
                .filter(e -> e.getValue() <= budget)
                .map(Map.Entry::getKey)
                .sorted()
                .toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Sort by length   (Level 2 - Intermediate)
    // Shortest word first; words of the same length in alphabetical order.
    //   sortByLength(["pear", "fig", "apple", "kiwi"]) -> ["fig", "kiwi", "pear", "apple"]
    // Hint: Comparator.comparingInt(String::length).thenComparing(...)
    // ---------------------------------------------------------------------------
    static List<String> sortByLength(List<String> words) {
        // >>> SOLUTION stub: return null;
        return words.stream()
                .sorted(Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()))
                .toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Count matches   (Level 2 - Intermediate)
    // The caller hands you a test (a Predicate, i.e. a lambda). Return how many
    // words pass it.
    //   countMatching(["a", "bb", "cc"], w -> w.length() == 2) -> 2
    // ---------------------------------------------------------------------------
    static long countMatching(List<String> words, Predicate<String> test) {
        // >>> SOLUTION stub: return 0;
        return words.stream().filter(test).count();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-4 | Discount maker   (Level 2 - Intermediate)
    // Return a Function that takes a price (whole rupees) and gives the price after
    // `percent` percent off. Use integer maths: price * (100 - percent) / 100.
    //   makeDiscount(25).apply(1000) -> 750      makeDiscount(10).apply(2000) -> 1800
    // ---------------------------------------------------------------------------
    static Function<Integer, Integer> makeDiscount(int percent) {
        // >>> SOLUTION stub: return price -> 0;
        return price -> price * (100 - percent) / 100;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Top songs   (Level 3 - Challenge)
    // Return the TITLES of the n most-played songs, most plays first. Songs with
    // equal plays are ordered by title A-Z. If there are fewer than n songs, return
    // them all.
    //   topSongs([B:5, A:5, C:9], 2) -> ["C", "A"]
    // ---------------------------------------------------------------------------
    static List<String> topSongs(List<Song> songs, int n) {
        // >>> SOLUTION stub: return null;
        return songs.stream()
                .sorted(Comparator.comparingInt(Song::plays).reversed().thenComparing(Song::title))
                .limit(n)
                .map(Song::title)
                .toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Transpose a matrix   (Level 3 - Challenge)
    // Swap rows and columns of a rectangular matrix (a list of rows).
    //   transpose([[1, 2, 3], [4, 5, 6]]) -> [[1, 4], [2, 5], [3, 6]]
    //   transpose([]) -> []
    // Hint: for each column number c, collect row.get(c) from every row.
    // ---------------------------------------------------------------------------
    static List<List<Integer>> transpose(List<List<Integer>> matrix) {
        // >>> SOLUTION stub: return null;
        if (matrix.isEmpty()) {
            return List.of();
        }
        int columns = matrix.get(0).size();
        return IntStream.range(0, columns)
                .mapToObj(c -> matrix.stream().map(row -> row.get(c)).toList())
                .toList();
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 12 checks ---");
        Checker.check("L1-1 squares", () -> List.of(squares(4), squares(0)), List.of(List.of(1, 4, 9, 16), List.of()));
        Checker.check("L1-2 evenNumbers", () -> evenNumbers(List.of(1, 2, 3, 4, 6)), List.of(2, 4, 6));
        Checker.check("L1-3 toUpper", () -> toUpper(List.of("ab", "Cd")), List.of("AB", "CD"));
        Checker.check("L2-1 affordable", () -> affordable(Map.of("chai", 20, "pizza", 300, "samosa", 15), 50),
                List.of("chai", "samosa"));
        Checker.check("L2-2 sortByLength", () -> sortByLength(List.of("pear", "fig", "apple", "kiwi")),
                List.of("fig", "kiwi", "pear", "apple"));
        Checker.check("L2-3 countMatching", () -> List.of(
                countMatching(List.of("a", "bb", "cc"), w -> w.length() == 2),
                countMatching(List.of("apple", "avocado", "kiwi"), w -> w.startsWith("a")),
                countMatching(List.of(), w -> true)), List.of(2L, 2L, 0L));
        Checker.check("L2-4 makeDiscount", () -> List.of(makeDiscount(25).apply(1000), makeDiscount(10).apply(2000),
                makeDiscount(0).apply(500)), List.of(750, 1800, 500));
        Checker.check("L2-4 makeDiscount andThen", () -> makeDiscount(10).andThen(makeDiscount(10)).apply(1000), 810);
        List<Song> chart = List.of(new Song("B", 5), new Song("A", 5), new Song("C", 9));
        Checker.check("L3-1 topSongs", () -> List.of(topSongs(chart, 2), topSongs(List.of(new Song("x", 1)), 3)),
                List.of(List.of("C", "A"), List.of("x")));
        Checker.check("L3-2 transpose", () -> List.of(transpose(List.of(List.of(1, 2, 3), List.of(4, 5, 6))),
                transpose(List.of(List.of(7))), transpose(List.of())),
                List.of(List.of(List.of(1, 4), List.of(2, 5), List.of(3, 6)), List.of(List.of(7)), List.of()));
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
