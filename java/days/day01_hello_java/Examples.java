/* Day 01 - Code along: a cafe receipt printer.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
class Examples {
    public static void main(String[] args) {
        // ---- 1. Our first instructions (they run top to bottom) ----
        System.out.println("Welcome to Chai Point");
        System.out.println("One masala chai, please");

        // ---- 2. Text vs numbers ----
        System.out.println(2 + 3);      // Java calculates -> 5
        System.out.println("2 + 3");    // just text -> 2 + 3
        System.out.println("Total: " + (2 * 60 + 3 * 15));   // 2 chai at 60 + 3 samosa at 15 -> Total: 165

        // ---- 3. Making the output pretty ----
        System.out.println("=".repeat(24));
        System.out.println("      CHAI POINT");
        System.out.println("=".repeat(24));
        System.out.println("Item\tQty\tPrice");          // \t = tab
        System.out.println("Chai\t2\t120");
        System.out.println("Samosa\t3\t45");
        System.out.println("-".repeat(24));
        System.out.println("TOTAL\t\t165");

        // ---- 4. print vs println vs printf ----
        System.out.print("Loading");
        System.out.print("...");
        System.out.println("done");
        System.out.printf("%d-%d-%d%n", 2026, 11, 16);
        System.out.printf("%s costs %.2f%n", "Masala Chai", 60.0);

        // ---- 5. A first look at variables ----
        String shop = "Chai Point";
        int cups = 3;
        double price = 20.5;
        System.out.println(shop + " sold " + cups + " cups at " + price + " each");
        System.out.println("Revenue: " + cups * price);
    }
}
