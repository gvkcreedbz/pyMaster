/* Day 02 - Practice: Variables, types, Scanner input and formatting.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
import java.util.Scanner;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Order variables   (Level 1 - Beginner)
    // Give the five fields below the right type and value:
    //   itemName = "Paneer Pizza" (text)     price = 349 (whole number)
    //   qty = 2 (whole number)               rating = 4.5 (decimal number)
    //   isVeg = true (yes/no)
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    static String itemName = null;
    // TODO: write your code here
    static int price = 0;
    // TODO: write your code here
    static int qty = 0;
    // TODO: write your code here
    static double rating = 0;
    // TODO: write your code here
    static boolean isVeg = false;

    // ---------------------------------------------------------------------------
    // L1-2 | Order total   (Level 1 - Beginner)
    // Make orderTotal() return price times qty, using the two variables above
    // (do not type 698 yourself: if the variables change, the total must change too).
    // ---------------------------------------------------------------------------
    static int orderTotal() {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Text to numbers   (Level 1 - Beginner)
    // Scanner hands you TEXT. Convert it:
    //   parseQty("3")        -> 3      (an int)
    //   parsePrice("20.5")   -> 20.5   (a double)
    // ---------------------------------------------------------------------------
    static int parseQty(String text) {
        // TODO: write your code here
        return 0;
    }

    static double parsePrice(String text) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Order summary   (Level 2 - Intermediate)
    // Return text in exactly this format (price always with 2 decimals):
    //   orderSummary("Paneer Pizza", 349, 2)  ->  "2 x Paneer Pizza = Rs. 698.00"
    // Hint: String.format("%d x %s = Rs. %.2f", ...)
    // ---------------------------------------------------------------------------
    static String orderSummary(String item, double unitPrice, int quantity) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Split the bill   (Level 2 - Intermediate)
    // Return  "Each person pays Rs. X"  with X rounded to 2 decimals.
    //   splitBill(1000, 3) -> "Each person pays Rs. 333.33"
    //   splitBill(999, 2)  -> "Each person pays Rs. 499.50"   (careful: int / int drops the .5!)
    // ---------------------------------------------------------------------------
    static String splitBill(int total, int people) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Read an order from the keyboard   (Level 2 - Intermediate)
    // Create a Scanner on System.in and read THREE lines: the item name, the unit
    // price (decimal) and the quantity (whole number). Then return
    // orderSummary(...) built from them.
    //   input "Chai", "20.5", "4"   ->  "4 x Chai = Rs. 82.00"
    // ---------------------------------------------------------------------------
    static String readOrder() {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Full invoice   (Level 3 - Challenge)
    // Return a 4-line text (lines joined with \n, NO trailing newline):
    //   Subtotal: Rs. 698.00
    //   Delivery: Rs. 40.00
    //   Tip (10%): Rs. 69.80        <- tip is a percentage of the SUBTOTAL
    //   TOTAL: Rs. 807.80
    // Example call: deliveryInvoice(349, 2, 40, 10)
    // Tip: inside String.format a literal percent sign is written %%
    // and for the line breaks use \n (the %n of printf gives \r\n on Windows).
    // ---------------------------------------------------------------------------
    static String deliveryInvoice(double unitPrice, int quantity, double deliveryFee, int tipPercent) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Trip bill from the keyboard   (Level 3 - Challenge)
    // The input has THREE lines: the total (whole number), the number of friends
    // (whole number) and the name of the group (text with spaces). Return
    //   "<group>: Rs. X each"      with X to 2 decimals, e.g. input 1200, 4, "Goa Trip"
    //   -> "Goa Trip: Rs. 300.00 each"
    // Trap: after nextInt() the rest of the line (the invisible new line) is still
    // waiting. If you call nextLine() right away you get an EMPTY text.
    // ---------------------------------------------------------------------------
    static String tripBill() {
        // TODO: write your code here
        return null;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 02 checks ---");
        Checker.check("L1-1 itemName", () -> itemName, "Paneer Pizza");
        Checker.check("L1-1 price", () -> price, 349);
        Checker.check("L1-1 qty", () -> qty, 2);
        Checker.check("L1-1 rating", () -> rating, 4.5);
        Checker.check("L1-1 isVeg", () -> isVeg, true);
        Checker.check("L1-2 orderTotal", () -> orderTotal(), 698);
        Checker.check("L1-3 parseQty", () -> parseQty("3") + parseQty("12"), 15);
        Checker.check("L1-3 parsePrice", () -> parsePrice("20.5") + parsePrice("0.25"), 20.75);
        Checker.check("L2-1 orderSummary", () -> orderSummary("Paneer Pizza", 349, 2), "2 x Paneer Pizza = Rs. 698.00");
        Checker.check("L2-1 orderSummary #2", () -> orderSummary("Chai", 20.5, 4), "4 x Chai = Rs. 82.00");
        Checker.check("L2-2 splitBill", () -> splitBill(1000, 3), "Each person pays Rs. 333.33");
        Checker.check("L2-2 splitBill #2", () -> splitBill(999, 2), "Each person pays Rs. 499.50");
        Checker.check("L2-3 readOrder", () -> Checker.withInput("Chai\n20.5\n4\n", () -> readOrder()), "4 x Chai = Rs. 82.00");
        Checker.check("L2-3 readOrder #2", () -> Checker.withInput("Veg Biryani\n249\n3\n", () -> readOrder()),
                "3 x Veg Biryani = Rs. 747.00");
        Checker.check("L3-1 deliveryInvoice", () -> deliveryInvoice(349, 2, 40, 10),
                "Subtotal: Rs. 698.00\nDelivery: Rs. 40.00\nTip (10%): Rs. 69.80\nTOTAL: Rs. 807.80");
        Checker.check("L3-1 deliveryInvoice #2", () -> deliveryInvoice(100, 1, 0, 5),
                "Subtotal: Rs. 100.00\nDelivery: Rs. 0.00\nTip (5%): Rs. 5.00\nTOTAL: Rs. 105.00");
        Checker.check("L3-2 tripBill", () -> Checker.withInput("1200\n4\nGoa Trip\n", () -> tripBill()),
                "Goa Trip: Rs. 300.00 each");
        Checker.check("L3-2 tripBill #2", () -> Checker.withInput("1000\n3\nOffice Lunch\n", () -> tripBill()),
                "Office Lunch: Rs. 333.33 each");
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
