/* Day 09 - Code along: a shopping cart (ArrayList) and unique visitors (sets).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

class Examples {
    public static void main(String[] args) {
        // ---- 1. ArrayList: a list that can grow and shrink ----
        List<String> cart = new ArrayList<>();
        cart.add("milk");
        cart.add("bread");
        cart.add("eggs");
        System.out.println(cart);                          // [milk, bread, eggs]  (println shows lists nicely)
        System.out.println(cart.get(0) + " / " + cart.get(cart.size() - 1));   // milk / eggs
        cart.set(1, "brown bread");                        // replace
        cart.add(0, "tea");                                // insert at a position
        cart.remove("eggs");                               // remove by value
        cart.remove(0);                                    // remove by position
        System.out.println(cart + " has " + cart.size() + " items");
        System.out.println("milk in cart? " + cart.contains("milk") + ", position of milk: " + cart.indexOf("milk"));
        for (String item : cart) {
            System.out.println("- " + item);
        }

        // ---- 2. List.of: a list you cannot change ----
        List<String> weekdays = List.of("Mon", "Tue", "Wed");
        System.out.println(weekdays);
        try {
            weekdays.add("Thu");
        } catch (UnsupportedOperationException e) {
            System.out.println("List.of lists are read-only: add() is refused");
        }
        List<String> changeable = new ArrayList<>(weekdays);   // a changeable copy
        changeable.add("Thu");
        System.out.println(changeable);

        // ---- 3. Wrapper types: lists hold objects, so int becomes Integer ----
        List<Integer> marks = new ArrayList<>();
        marks.add(72);                                     // int -> Integer happens automatically (autoboxing)
        marks.add(95);
        marks.add(88);
        marks.add(60);
        int first = marks.get(0);                          // Integer -> int automatically
        System.out.println("first = " + first + ", sum of first two = " + (marks.get(0) + marks.get(1)));
        marks.remove(1);                                   // an int: remove the item AT POSITION 1
        System.out.println(marks);                         // [72, 88, 60]
        marks.remove(Integer.valueOf(60));                 // an Integer: remove the VALUE 60
        System.out.println(marks);                         // [72, 88]
        Integer x = 127, y = 127, p = 1000, q = 1000;
        System.out.println((x == y) + " " + (p == q) + " " + p.equals(q));   // true false true -> always use equals!

        // ---- 4. Collections: handy helpers for lists ----
        List<Integer> scores = new ArrayList<>(List.of(72, 95, 88, 60, 95));
        System.out.println("max " + Collections.max(scores) + ", min " + Collections.min(scores)
                + ", 95 appears " + Collections.frequency(scores, 95) + " times");
        Collections.sort(scores);                          // sorts IN PLACE
        System.out.println(scores);                        // [60, 72, 88, 95, 95]
        Collections.reverse(scores);
        System.out.println(scores);                        // [95, 95, 88, 72, 60]
        Collections.swap(scores, 0, 4);
        System.out.println(scores);                        // [60, 95, 88, 72, 95]

        // ---- 5. HashSet: unique items, very fast "is it in there?" ----
        List<String> visits = List.of("aarav", "diya", "aarav", "kabir", "diya", "aarav");
        Set<String> unique = new HashSet<>(visits);
        System.out.println(visits.size() + " visits, " + unique.size() + " unique visitors");
        System.out.println("diya visited? " + unique.contains("diya"));
        System.out.println("added kabir again? " + unique.add("kabir") + ", added zoya? " + unique.add("zoya"));

        // ---- 6. TreeSet: unique AND sorted ----
        Set<String> sortedNames = new TreeSet<>(unique);
        System.out.println(sortedNames);                   // [aarav, diya, kabir, zoya]

        // ---- 7. Set maths: mutual friends ----
        Set<String> mine = new TreeSet<>(List.of("A", "B", "C"));
        Set<String> hers = new TreeSet<>(List.of("B", "C", "D"));
        Set<String> both = new TreeSet<>(mine);
        both.retainAll(hers);                              // intersection
        Set<String> all = new TreeSet<>(mine);
        all.addAll(hers);                                  // union
        Set<String> onlyMine = new TreeSet<>(mine);
        onlyMine.removeAll(hers);                          // difference
        System.out.println("both " + both + ", union " + all + ", only mine " + onlyMine);

        // ---- 8. Keep the order while removing repeats ----
        List<String> tags = List.of("a", "b", "a", "c", "b");
        List<String> kept = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        for (String tag : tags) {
            if (seen.add(tag)) {                           // add() says true only the first time
                kept.add(tag);
            }
        }
        System.out.println(kept);                          // [a, b, c]
    }
}
