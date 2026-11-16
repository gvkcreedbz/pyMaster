/* Day 10 - Code along: a contact book, an inventory and word counts with maps.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class Examples {
    public static void main(String[] args) {
        // ---- 1. Create, read, add, change, remove ----
        Map<String, Integer> menu = new HashMap<>();       // key = item name, value = price
        menu.put("chai", 20);
        menu.put("samosa", 15);
        menu.put("pizza", 300);
        System.out.println(menu.get("chai"));              // 20
        System.out.println(menu.get("burger"));            // null  (missing key: no crash, but null!)
        System.out.println(menu.getOrDefault("burger", 0)); // 0     (safe + default)
        System.out.println(menu.containsKey("pizza") + " " + menu.containsValue(15));   // true true
        menu.put("chai", 25);                              // same key: the value is REPLACED
        menu.remove("pizza");
        System.out.println(menu.size() + " items, chai costs " + menu.get("chai"));

        // ---- 2. Looping: keys, values, or both ----
        Map<String, Integer> shelf = new LinkedHashMap<>();   // remembers the order you added things
        shelf.put("pen", 10);
        shelf.put("book", 120);
        shelf.put("bag", 450);
        for (String name : shelf.keySet()) {
            System.out.println("key: " + name);
        }
        int sum = 0;
        for (int price : shelf.values()) {
            sum += price;
        }
        System.out.println("all prices add up to " + sum);
        for (Map.Entry<String, Integer> entry : shelf.entrySet()) {   // both at once (most common)
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }
        System.out.println(shelf);                         // {pen=10, book=120, bag=450}

        // ---- 3. The counting pattern ----
        String text = "to be or not to be";
        Map<String, Integer> counts = new HashMap<>();
        for (String word : text.split(" ")) {
            counts.put(word, counts.getOrDefault(word, 0) + 1);   // 0 the first time we see a word
        }
        System.out.println(new TreeMap<>(counts));         // {be=2, not=1, or=1, to=2}

        // the same with merge: "put 1, or ADD 1 to what is already there"
        Map<String, Integer> counts2 = new TreeMap<>();
        for (String word : text.split(" ")) {
            counts2.merge(word, 1, Integer::sum);          // Integer::sum = "old + new" (more on Day 12)
        }
        System.out.println(counts2);                       // {be=2, not=1, or=1, to=2}

        // ---- 4. The grouping pattern: key -> list ----
        List<String> fruits = List.of("apple", "avocado", "banana", "blueberry", "cherry");
        Map<String, List<String>> groups = new TreeMap<>();
        for (String fruit : fruits) {
            String letter = fruit.substring(0, 1);
            if (!groups.containsKey(letter)) {
                groups.put(letter, new ArrayList<>());     // first time: create an empty list
            }
            groups.get(letter).add(fruit);
        }
        System.out.println(groups);                        // {a=[apple, avocado], b=[banana, blueberry], c=[cherry]}
        Map<String, List<String>> groups2 = new TreeMap<>();
        for (String fruit : fruits) {
            groups2.computeIfAbsent(fruit.substring(0, 1), k -> new ArrayList<>()).add(fruit);   // one-line version
        }
        System.out.println(groups2.equals(groups));        // true

        // ---- 5. HashMap vs LinkedHashMap vs TreeMap ----
        Map<String, Integer> byKey = new TreeMap<>(counts);            // sorted by key
        Map<String, Integer> byInsert = new LinkedHashMap<>();         // insertion order
        byInsert.put("zebra", 1);
        byInsert.put("ant", 2);
        byInsert.put("mouse", 3);
        System.out.println(byKey.keySet());                // [be, not, or, to]
        System.out.println(byInsert.keySet());             // [zebra, ant, mouse]

        // ---- 6. Sort the keys by value: TreeMap first, then a STABLE sort by count ----
        List<String> words = new ArrayList<>(new TreeMap<>(counts).keySet());   // A-Z
        words.sort((a, b) -> counts.get(b) - counts.get(a));                    // biggest count first; ties stay A-Z
        System.out.println(words);                         // [be, to, not, or]

        // ---- 7. Nested maps ----
        Map<String, Map<String, Integer>> inventory = new TreeMap<>();
        inventory.put("pen", new TreeMap<>(Map.of("price", 10, "stock", 50)));
        inventory.put("book", new TreeMap<>(Map.of("price", 120, "stock", 5)));
        inventory.get("book").merge("stock", -1, Integer::sum);          // sold one book
        System.out.println(inventory);                     // {book={price=120, stock=4}, pen={price=10, stock=50}}
    }
}
