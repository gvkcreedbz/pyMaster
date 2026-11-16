/* Day 08 - Code along: a shopping cart and a leaderboard with arrays.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.Arrays;

class Examples {
    public static void main(String[] args) {
        // ---- 1. Create, index, length ----
        String[] cart = {"milk", "bread", "eggs"};
        System.out.println(cart[0] + " / " + cart[cart.length - 1]);   // milk / eggs (no cart[-1] in Java!)
        System.out.println("Items in cart: " + cart.length);
        System.out.println(cart);                                      // ugly: [Ljava.lang.String;@...
        System.out.println(Arrays.toString(cart));                     // [milk, bread, eggs]

        // ---- 2. Arrays have a fixed size: you can change items, not the length ----
        cart[1] = "brown bread";                                       // replace is fine
        String[] bigger = Arrays.copyOf(cart, cart.length + 1);        // new array, one slot longer
        bigger[3] = "butter";                                          // the new slot starts as null
        System.out.println(Arrays.toString(bigger));

        // ---- 3. Looping: classic for (need the position) and enhanced for (just the items) ----
        double[] prices = {49.5, 30, 120};
        double total = 0;
        for (int i = 0; i < prices.length; i++) {
            System.out.println((i + 1) + ". Rs. " + prices[i]);
            total += prices[i];
        }
        System.out.println("Total: " + total);
        for (String item : bigger) {
            System.out.println("- " + item);
        }

        // ---- 4. Handy tools from the Arrays class ----
        int[] scores = {72, 95, 88, 60};
        int[] sorted = Arrays.copyOf(scores, scores.length);           // sort a COPY, keep the original
        Arrays.sort(sorted);
        System.out.println("original: " + Arrays.toString(scores));    // [72, 95, 88, 60]
        System.out.println("sorted:   " + Arrays.toString(sorted));    // [60, 72, 88, 95]
        System.out.println("highest: " + sorted[sorted.length - 1]);
        System.out.println("position of 88 in the sorted copy: " + Arrays.binarySearch(sorted, 88));
        System.out.println("same content? " + Arrays.equals(scores, new int[]{72, 95, 88, 60}));
        int[] zeros = new int[5];                                      // five 0s
        Arrays.fill(zeros, 7);                                         // now five 7s
        System.out.println(Arrays.toString(zeros));

        // ---- 5. The copy trap: = copies the NAME, not the array ----
        int[] a = {1, 2, 3};
        int[] b = a;                                                   // b is a second name for the SAME array
        b[0] = 99;
        System.out.println("a = " + Arrays.toString(a));               // [99, 2, 3]  <- surprise
        int[] c = a.clone();                                           // a real copy
        c[0] = 1;
        System.out.println("a = " + Arrays.toString(a) + ", c = " + Arrays.toString(c));
        System.out.println("a == b? " + (a == b) + ", a == c? " + (a == c) + ", Arrays.equals(a, c)? " + Arrays.equals(a, c));

        // ---- 6. Tables: arrays of arrays ----
        int[][] sales = {
                {120, 80, 150},        // shop 0: Mon, Tue, Wed
                {90, 100, 60}          // shop 1
        };
        System.out.println("shop 1, Tuesday: " + sales[1][1]);          // 100
        for (int[] row : sales) {
            int rowTotal = 0;
            for (int amount : row) {
                rowTotal += amount;
            }
            System.out.println(Arrays.toString(row) + " -> " + rowTotal);
        }
        System.out.println(Arrays.deepToString(sales));

        // ---- 7. Out of bounds is a runtime error (we catch it here just to show the message) ----
        try {
            System.out.println(scores[4]);
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Oops: " + e.getMessage());
        }
    }
}
