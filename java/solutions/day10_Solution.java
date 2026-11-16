// SOLUTION FILE - try the hint ladder first!
/* Day 10 - Practice: maps (key -> value).
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 * Maps made with Map.of(...) cannot be changed: the checker passes you a HashMap when your method must change it.
 */
import java.util.*;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Safe price lookup   (Level 1 - Beginner)
    // Return the price of item from the menu map, or 0 if it is not on the menu.
    //   getPrice({chai=20}, "chai") -> 20       getPrice({chai=20}, "pizza") -> 0
    // ---------------------------------------------------------------------------
    static int getPrice(Map<String, Integer> menu, String item) {
        // >>> SOLUTION stub: return -1;
        return menu.getOrDefault(item, 0);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Add stock   (Level 1 - Beginner)
    // Increase inventory.get(item) by qty (create the key when it is missing).
    // Change the map itself AND return it.
    //   addStock({pen=5}, "pen", 3) -> {pen=8}       addStock({}, "bag", 2) -> {bag=2}
    // ---------------------------------------------------------------------------
    static Map<String, Integer> addStock(Map<String, Integer> inventory, String item, int qty) {
        // >>> SOLUTION stub: return null;
        inventory.put(item, inventory.getOrDefault(item, 0) + qty);
        return inventory;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Inventory value   (Level 1 - Beginner)
    // prices = {pen=10, book=120}      stock = {pen=5, book=2, bag=4}
    // Return the sum of price * quantity for every item in stock. An item with no
    // price is worth 0.   -> 10*5 + 120*2 = 290
    // ---------------------------------------------------------------------------
    static int inventoryValue(Map<String, Integer> prices, Map<String, Integer> stock) {
        // >>> SOLUTION stub: return -1;
        int total = 0;
        for (Map.Entry<String, Integer> entry : stock.entrySet()) {
            total += prices.getOrDefault(entry.getKey(), 0) * entry.getValue();
        }
        return total;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Word frequency   (Level 2 - Intermediate)
    // Lowercase the text, remove the characters . , ! ? and count every word. Words
    // are separated by single spaces. An empty text gives an empty map.
    //   wordFrequency("Hi hi, there!") -> {hi=2, there=1}
    // ---------------------------------------------------------------------------
    static Map<String, Integer> wordFrequency(String text) {
        // >>> SOLUTION stub: return null;
        String clean = text.toLowerCase().replace(".", "").replace(",", "").replace("!", "").replace("?", "");
        Map<String, Integer> counts = new HashMap<>();
        for (String word : clean.split(" ")) {
            if (!word.isEmpty()) {
                counts.merge(word, 1, Integer::sum);
            }
        }
        return counts;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Group by first letter   (Level 2 - Intermediate)
    // Return a map: first letter (lowercase text) -> list of the words with that
    // letter, in their ORIGINAL order.
    //   groupByFirstLetter([apple, banana, Avocado]) -> {a=[apple, Avocado], b=[banana]}
    // ---------------------------------------------------------------------------
    static Map<String, List<String>> groupByFirstLetter(List<String> words) {
        // >>> SOLUTION stub: return null;
        Map<String, List<String>> groups = new HashMap<>();
        for (String word : words) {
            String letter = word.substring(0, 1).toLowerCase();
            groups.computeIfAbsent(letter, k -> new ArrayList<>()).add(word);
        }
        return groups;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Merge and add   (Level 2 - Intermediate)
    // Return a NEW map with every key from a and b. If a key is in both, ADD the two
    // values. Do not change a or b.
    //   mergeSum({x=1, y=2}, {y=3, z=4}) -> {x=1, y=5, z=4}
    // ---------------------------------------------------------------------------
    static Map<String, Integer> mergeSum(Map<String, Integer> a, Map<String, Integer> b) {
        // >>> SOLUTION stub: return null;
        Map<String, Integer> result = new HashMap<>(a);
        for (Map.Entry<String, Integer> entry : b.entrySet()) {
            result.merge(entry.getKey(), entry.getValue(), Integer::sum);
        }
        return result;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-4 | Menu board   (Level 2 - Intermediate)
    // Return one line "name=price" for every menu item, sorted by NAME (A-Z).
    //   menuLines({samosa=15, chai=20}) -> [chai=20, samosa=15]
    // Hint: new TreeMap<>(menu) sorts the keys for you.
    // ---------------------------------------------------------------------------
    static List<String> menuLines(Map<String, Integer> menu) {
        // >>> SOLUTION stub: return null;
        List<String> lines = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : new TreeMap<>(menu).entrySet()) {
            lines.add(entry.getKey() + "=" + entry.getValue());
        }
        return lines;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Top-N words   (Level 3 - Challenge)
    // Return the n most frequent words (use wordFrequency above). Ties are broken
    // ALPHABETICALLY.   topWords("b a b c a d", 3) -> [a, b, c]
    // (a and b appear twice -> alphabetical; c and d once -> c first)
    // Idea: put the words in A-Z order first, then do a STABLE sort by count, biggest first.
    // ---------------------------------------------------------------------------
    static List<String> topWords(String text, int n) {
        // >>> SOLUTION stub: return null;
        Map<String, Integer> freq = wordFrequency(text);
        List<String> words = new ArrayList<>(new TreeMap<>(freq).keySet());
        words.sort((a, b) -> freq.get(b) - freq.get(a));
        return new ArrayList<>(words.subList(0, Math.min(n, words.size())));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | First non-repeating character   (Level 3 - Challenge)
    // Return the INDEX of the first character that appears exactly once, or -1.
    //   firstUniqueChar("swiss") -> 1   (the "w")       firstUniqueChar("aabb") -> -1
    // Idea: count every char first (Map<Character, Integer>), then scan the text again.
    // ---------------------------------------------------------------------------
    static int firstUniqueChar(String text) {
        // >>> SOLUTION stub: return -2;
        Map<Character, Integer> counts = new HashMap<>();
        for (int i = 0; i < text.length(); i++) {
            counts.merge(text.charAt(i), 1, Integer::sum);
        }
        for (int i = 0; i < text.length(); i++) {
            if (counts.get(text.charAt(i)) == 1) {
                return i;
            }
        }
        return -1;
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 10 checks ---");
        Map<String, Integer> menu = Map.of("chai", 20);
        Checker.check("L1-1 getPrice found", () -> getPrice(menu, "chai"), 20);
        Checker.check("L1-1 getPrice missing", () -> getPrice(menu, "pizza"), 0);
        Checker.check("L1-2 addStock existing", () -> addStock(new HashMap<>(Map.of("pen", 5)), "pen", 3), Map.of("pen", 8));
        Checker.check("L1-2 addStock new key", () -> addStock(new HashMap<>(), "bag", 2), Map.of("bag", 2));
        Map<String, Integer> shop = new HashMap<>(Map.of("pen", 1));
        Checker.check("L1-2 addStock changes the map itself", () -> {
            addStock(shop, "pen", 4);
            return shop;
        }, Map.of("pen", 5));
        Checker.check("L1-3 inventoryValue", () -> inventoryValue(Map.of("pen", 10, "book", 120),
                Map.of("pen", 5, "book", 2, "bag", 4)), 290);
        Checker.check("L1-3 inventoryValue empty stock", () -> inventoryValue(Map.of("pen", 10), Map.of()), 0);
        Checker.check("L2-1 wordFrequency", () -> wordFrequency("Hi hi, there!"), Map.of("hi", 2, "there", 1));
        Checker.check("L2-1 wordFrequency sentence", () -> wordFrequency("To be. Or not to be?"),
                Map.of("to", 2, "be", 2, "or", 1, "not", 1));
        Checker.check("L2-1 wordFrequency empty", () -> wordFrequency(""), Map.of());
        Checker.check("L2-2 groupByFirstLetter", () -> groupByFirstLetter(List.of("apple", "banana", "Avocado")),
                Map.of("a", List.of("apple", "Avocado"), "b", List.of("banana")));
        Checker.check("L2-2 groupByFirstLetter empty", () -> groupByFirstLetter(List.of()), Map.of());
        Map<String, Integer> a = new HashMap<>(Map.of("x", 1, "y", 2));
        Map<String, Integer> b = new HashMap<>(Map.of("y", 3, "z", 4));
        Checker.check("L2-3 mergeSum", () -> mergeSum(a, b), Map.of("x", 1, "y", 5, "z", 4));
        Checker.check("L2-3 mergeSum leaves a alone", () -> a, Map.of("x", 1, "y", 2));
        Checker.check("L2-3 mergeSum leaves b alone", () -> b, Map.of("y", 3, "z", 4));
        Checker.check("L2-4 menuLines", () -> menuLines(Map.of("samosa", 15, "chai", 20)), List.of("chai=20", "samosa=15"));
        Checker.check("L2-4 menuLines empty", () -> menuLines(Map.of()), List.of());
        Checker.check("L3-1 topWords ties alphabetical", () -> topWords("b a b c a d", 3), List.of("a", "b", "c"));
        Checker.check("L3-1 topWords one", () -> topWords("the cat the dog the end", 1), List.of("the"));
        Checker.check("L3-1 topWords n bigger than the words", () -> topWords("x y x", 5), List.of("x", "y"));
        Checker.check("L3-2 firstUniqueChar", () -> firstUniqueChar("swiss"), 1);
        Checker.check("L3-2 firstUniqueChar none", () -> firstUniqueChar("aabb"), -1);
        Checker.check("L3-2 firstUniqueChar first letter", () -> firstUniqueChar("python"), 0);
        Checker.check("L3-2 firstUniqueChar last letter", () -> firstUniqueChar("aabbc"), 4);
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
