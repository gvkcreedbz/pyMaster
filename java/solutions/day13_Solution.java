// SOLUTION FILE - try the hint ladder first!
/* Day 13 - Practice: nested data, records and JSON-style text.
 *
 * Run:  java Practice.java
 * A Restaurant has a LIST of cuisines inside it: read the data like a path (list -> record -> list).
 */
import java.util.*;
import java.util.stream.*;

class Practice {

    // A record is a tiny data class: Java writes the getters (name(), city() ...), equals and toString for you.
    record Restaurant(String name, String city, double rating, List<String> cuisines, int avgCost) {}

    // The answer shape for L3-1.
    record CitySummary(int count, double avgRating, double avgCost) {}

    // An order from a food-delivery app (used by L2-3).
    record Item(String name, int price, int qty) {}
    record Order(String customer, List<Item> items) {}

    static final List<Restaurant> RESTAURANTS = List.of(
            new Restaurant("Spice Hub", "Delhi", 4.5, List.of("North Indian", "Chinese"), 600),
            new Restaurant("Dosa Corner", "Pune", 4.2, List.of("South Indian"), 250),
            new Restaurant("Pasta Palace", "Delhi", 4.0, List.of("Italian"), 800),
            new Restaurant("Biryani Bay", "Pune", 4.7, List.of("Mughlai", "North Indian"), 500),
            new Restaurant("Wok Express", "Mumbai", 3.9, List.of("Chinese"), 450));

    // Helper (already written for you): round to 2 decimal places.
    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    // ---------------------------------------------------------------------------
    // L1-1 | Names in a city   (Level 1 - Beginner)
    // Return the restaurant NAMES in the given city, in the original order.
    //   namesInCity(RESTAURANTS, "Delhi") -> ["Spice Hub", "Pasta Palace"]
    // ---------------------------------------------------------------------------
    static List<String> namesInCity(List<Restaurant> restaurants, String city) {
        // >>> SOLUTION stub: return null;
        return restaurants.stream()
                .filter(r -> r.city().equals(city))
                .map(Restaurant::name)
                .toList();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Average rating   (Level 1 - Beginner)
    // Mean of all ratings, rounded to 2 decimals (use round2). Return 0 for an empty list.
    // ---------------------------------------------------------------------------
    static double averageRating(List<Restaurant> restaurants) {
        // >>> SOLUTION stub: return -1;
        return round2(restaurants.stream().mapToDouble(Restaurant::rating).average().orElse(0));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | One-line description   (Level 1 - Beginner)
    // Return the text:  <name> (<city>) - <rating> stars - <cuisines joined by ", ">
    //   describe(first restaurant) -> "Spice Hub (Delhi) - 4.5 stars - North Indian, Chinese"
    // Hint: String.join(", ", list) glues a list of text.
    // ---------------------------------------------------------------------------
    static String describe(Restaurant r) {
        // >>> SOLUTION stub: return null;
        return r.name() + " (" + r.city() + ") - " + r.rating() + " stars - " + String.join(", ", r.cuisines());
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Best restaurant per city   (Level 2 - Intermediate)
    // Return a Map: city -> NAME of the highest-rated restaurant in that city.
    //   -> {Delhi=Spice Hub, Pune=Biryani Bay, Mumbai=Wok Express}
    // ---------------------------------------------------------------------------
    static Map<String, String> bestByCity(List<Restaurant> restaurants) {
        // >>> SOLUTION stub: return null;
        Map<String, Restaurant> best = new HashMap<>();
        for (Restaurant r : restaurants) {
            best.merge(r.city(), r, (old, candidate) -> candidate.rating() > old.rating() ? candidate : old);
        }
        Map<String, String> result = new HashMap<>();
        best.forEach((city, r) -> result.put(city, r.name()));
        return result;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Cuisine index   (Level 2 - Intermediate)
    // Return a Map: cuisine -> list of restaurant names serving it, sorted A-Z.
    // EVERY cuisine must appear.
    //   result.get("North Indian") -> ["Biryani Bay", "Spice Hub"]
    // Hint: map.computeIfAbsent(key, k -> new ArrayList<>()).add(...)
    // ---------------------------------------------------------------------------
    static Map<String, List<String>> cuisineIndex(List<Restaurant> restaurants) {
        // >>> SOLUTION stub: return null;
        Map<String, List<String>> index = new HashMap<>();
        for (Restaurant r : restaurants) {
            for (String cuisine : r.cuisines()) {
                index.computeIfAbsent(cuisine, c -> new ArrayList<>()).add(r.name());
            }
        }
        index.values().forEach(Collections::sort);
        return index;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Order total   (Level 2 - Intermediate)
    // Return the sum of price * qty over all items of the order (0 when it has no items).
    //   Order("Asha", [Item(Dosa, 90, 2), Item(Tea, 20, 1)]) -> 200
    // ---------------------------------------------------------------------------
    static int orderTotal(Order order) {
        // >>> SOLUTION stub: return -1;
        return order.items().stream().mapToInt(i -> i.price() * i.qty()).sum();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | City summary report   (Level 3 - Challenge)
    // Return a Map: city -> CitySummary(count, avgRating, avgCost) with both averages
    // rounded to 2 decimals (round2).
    //   result.get("Delhi") -> CitySummary[count=2, avgRating=4.25, avgCost=700.0]
    // Hint: group first (Collectors.groupingBy or a loop), then summarise each group.
    // ---------------------------------------------------------------------------
    static Map<String, CitySummary> citySummary(List<Restaurant> restaurants) {
        // >>> SOLUTION stub: return null;
        Map<String, List<Restaurant>> groups = restaurants.stream().collect(Collectors.groupingBy(Restaurant::city));
        Map<String, CitySummary> summary = new TreeMap<>();
        for (Map.Entry<String, List<Restaurant>> entry : groups.entrySet()) {
            List<Restaurant> items = entry.getValue();
            double rating = items.stream().mapToDouble(Restaurant::rating).average().orElse(0);
            double cost = items.stream().mapToInt(Restaurant::avgCost).average().orElse(0);
            summary.put(entry.getKey(), new CitySummary(items.size(), round2(rating), round2(cost)));
        }
        return summary;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | deepGet   (Level 3 - Challenge)
    // Follow a dotted path through nested Maps AND Lists. A number in the path is a
    // list position. Return defaultValue if anything is missing.
    //   data = {a={b=[{c=42}]}}
    //   deepGet(data, "a.b.0.c", null) -> 42      deepGet(data, "a.x.0", "none") -> "none"
    // Hint: loop over path.split("\\."); use  current instanceof Map<?, ?> m  and  instanceof List<?> list.
    // ---------------------------------------------------------------------------
    static Object deepGet(Object data, String path, Object defaultValue) {
        // >>> SOLUTION stub: return null;
        Object current = data;
        for (String part : path.split("\\.")) {
            if (current instanceof Map<?, ?> map && map.containsKey(part)) {
                current = map.get(part);
            } else if (current instanceof List<?> list && part.matches("\\d+") && Integer.parseInt(part) < list.size()) {
                current = list.get(Integer.parseInt(part));
            } else {
                return defaultValue;
            }
        }
        return current;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-3 | Write JSON by hand   (Level 3 - Challenge)
    // Turn nested data into COMPACT JSON text (no spaces after : or ,):
    //   null -> null | true/false | numbers as-is (2.5 -> 2.5) | String -> "text"
    //   (escape \ as \\ , " as \" and a new line as \n) | List -> [a,b] | Map -> {"key":value}
    //   Map keys must come out sorted A-Z. Throw IllegalArgumentException for anything else.
    //   toJson(Map of b=1, a=true, c=null) -> {"a":true,"b":1,"c":null}
    //   toJson(List.of(1, "x", Map.of("k", 2.5))) -> [1,"x",{"k":2.5}]
    // Hint: recursion! A list is "[" + the toJson of every item joined by "," + "]".
    // ---------------------------------------------------------------------------
    static String toJson(Object value) {
        // >>> SOLUTION stub: return null;
        if (value == null) {
            return "null";
        }
        if (value instanceof String s) {
            return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\"";
        }
        if (value instanceof Number || value instanceof Boolean) {
            return value.toString();
        }
        if (value instanceof List<?> list) {
            return list.stream().map(Practice::toJson).collect(Collectors.joining(",", "[", "]"));
        }
        if (value instanceof Map<?, ?> map) {
            Map<String, Object> sorted = new TreeMap<>();
            for (Map.Entry<?, ?> e : map.entrySet()) {
                sorted.put(String.valueOf(e.getKey()), e.getValue());
            }
            return sorted.entrySet().stream()
                    .map(e -> toJson(e.getKey()) + ":" + toJson(e.getValue()))
                    .collect(Collectors.joining(",", "{", "}"));
        }
        throw new IllegalArgumentException("cannot write " + value.getClass().getSimpleName());
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 13 checks ---");
        Checker.check("L1-1 namesInCity", () -> List.of(namesInCity(RESTAURANTS, "Delhi"), namesInCity(RESTAURANTS, "Goa")),
                List.of(List.of("Spice Hub", "Pasta Palace"), List.of()));
        Checker.check("L1-2 averageRating", () -> List.of(averageRating(RESTAURANTS), averageRating(List.of())),
                List.of(4.26, 0.0));
        Checker.check("L1-3 describe", () -> List.of(describe(RESTAURANTS.get(0)), describe(RESTAURANTS.get(1))),
                List.of("Spice Hub (Delhi) - 4.5 stars - North Indian, Chinese", "Dosa Corner (Pune) - 4.2 stars - South Indian"));
        Checker.check("L2-1 bestByCity", () -> bestByCity(RESTAURANTS),
                Map.of("Delhi", "Spice Hub", "Pune", "Biryani Bay", "Mumbai", "Wok Express"));
        Checker.check("L2-2 cuisineIndex", () -> {
            Map<String, List<String>> index = cuisineIndex(RESTAURANTS);
            return List.of(index.get("North Indian"), index.get("Chinese"), new TreeSet<>(index.keySet()).toString());
        }, List.of(List.of("Biryani Bay", "Spice Hub"), List.of("Spice Hub", "Wok Express"),
                "[Chinese, Italian, Mughlai, North Indian, South Indian]"));
        Order order = new Order("Asha", List.of(new Item("Dosa", 90, 2), new Item("Tea", 20, 1)));
        Checker.check("L2-3 orderTotal", () -> List.of(orderTotal(order), orderTotal(new Order("Ben", List.of()))),
                List.of(200, 0));
        Checker.check("L3-1 citySummary Delhi", () -> citySummary(RESTAURANTS).get("Delhi"), new CitySummary(2, 4.25, 700.0));
        Checker.check("L3-1 citySummary Pune", () -> citySummary(RESTAURANTS).get("Pune"), new CitySummary(2, 4.45, 375.0));
        Checker.check("L3-1 citySummary cities", () -> new TreeSet<>(citySummary(RESTAURANTS).keySet()).toString(),
                "[Delhi, Mumbai, Pune]");
        Map<String, Object> data = Map.of("a", Map.of("b", List.of(Map.of("c", 42))), "x", List.of(10, 20));
        Checker.check("L3-2 deepGet found", () -> List.of(deepGet(data, "a.b.0.c", null), deepGet(data, "x.1", null)),
                List.of(42, 20));
        Checker.check("L3-2 deepGet missing", () -> Arrays.asList(deepGet(data, "a.x.0", "none"), deepGet(data, "x.5", null),
                deepGet(data, "a.b.9.c", 0)), Arrays.asList("none", null, 0));
        Map<String, Object> flags = new HashMap<>();
        flags.put("b", 1);
        flags.put("a", true);
        flags.put("c", null);
        Checker.check("L3-3 toJson map", () -> toJson(flags), "{\"a\":true,\"b\":1,\"c\":null}");
        Checker.check("L3-3 toJson nested", () -> toJson(List.of(1, "x", Map.of("k", 2.5))), "[1,\"x\",{\"k\":2.5}]");
        Checker.check("L3-3 toJson escapes", () -> toJson(Map.of("q", "say \"hi\"\nbye")), "{\"q\":\"say \\\"hi\\\"\\nbye\"}");
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
