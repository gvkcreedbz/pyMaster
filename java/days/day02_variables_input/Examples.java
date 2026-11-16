/* Day 02 - Code along: a food-delivery bill splitter.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * The last section asks YOU questions: type the answers in the terminal
 * (name, item name, price, quantity - one per line).
 */
import java.util.Scanner;

class Examples {
    public static void main(String[] args) {
        // ---- 1. Variables: a labelled box WITH a type ----
        String itemName = "Paneer Pizza";   // text
        int price = 349;                    // whole number
        double rating = 4.5;                // decimal number
        boolean isVeg = true;               // true / false (all lower case!)
        char size = 'M';                    // ONE character, single quotes
        long phone = 9876543210L;           // a very big whole number needs long and an L
        System.out.println(itemName + " | Rs. " + price + " | rating " + rating + " | veg? " + isVeg
                + " | size " + size + " | phone " + phone);

        // ---- 2. Variables can change (but not their type) ----
        int qty = 2;
        qty = qty + 1;          // now 3
        int copy = qty;         // copy gets the value 3
        qty = 10;
        System.out.println("qty=" + qty + " copy=" + copy);   // qty=10 copy=3

        final double DELIVERY_FEE = 40;   // final = a constant: Java refuses any later change
        System.out.println("Delivery fee: " + DELIVERY_FEE);

        // ---- 3. var: let Java work out the type from the value ----
        var city = "Pune";          // String
        var distanceKm = 4.2;       // double
        var items = 3;              // int
        System.out.println(city + " is " + distanceKm + " km away, " + items + " items");

        // ---- 4. Text + number: Java glues them together ----
        System.out.println("5" + 3);        // 53  (text glue)
        System.out.println(5 + 3);          // 8
        System.out.println("Total: " + 5 + 3);     // Total: 53   (left to right!)
        System.out.println("Total: " + (5 + 3));   // Total: 8

        // ---- 5. Converting text to numbers ----
        String ageText = "25";
        int age = Integer.parseInt(ageText);
        double amount = Double.parseDouble("12.5");
        System.out.println(age + 1);        // 26
        System.out.println(amount * 2);     // 25.0
        System.out.println(String.valueOf(age) + " years");   // number -> text

        // ---- 6. Formatting output ----
        String name = "Aarav";
        double total = 1234.5;
        System.out.printf("Hi %s, your total is Rs. %.2f%n", name, total);   // Hi Aarav, your total is Rs. 1234.50
        System.out.println(String.format("%-10s|%5d|", "Item", 3));          // left / right aligned columns
        String line = "%s x%d".formatted("Chai", 2);                          // same idea, called on the text
        System.out.println(line);

        // ---- 7. Text block: a multi-line text between triple quotes ----
        String slip = """
                ===== DELIVERY SLIP =====
                Item : %s
                Price: Rs. %d
                """.formatted(itemName, price);
        System.out.print(slip);

        // ---- 8. null = "no value yet" (only for objects like String, not for int) ----
        String coupon = null;
        System.out.println("Coupon: " + coupon);

        // ---- 9. Keyboard input with Scanner ----
        Scanner in = new Scanner(System.in);
        System.out.print("Your name: ");
        String customer = in.nextLine();                         // a whole line of text
        System.out.print("Item name: ");
        String item = in.nextLine();
        System.out.print("Unit price: ");
        double unitPrice = Double.parseDouble(in.nextLine());    // text -> double
        System.out.print("Quantity: ");
        int quantity = in.nextInt();                             // reads a whole number directly
        double bill = unitPrice * quantity;
        System.out.println();
        System.out.printf("%s, your %d x %s costs Rs. %.2f%n", customer, quantity, item, bill);
        System.out.printf("Split between 3 friends: Rs. %.2f each%n", bill / 3);
    }
}
