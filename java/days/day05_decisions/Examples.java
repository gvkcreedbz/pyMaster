/* Day 05 - Code along: delivery-fee rules and ticket pricing.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
class Examples {
    public static void main(String[] args) {
        // ---- 1. A grade with if / else if / else ----
        int marks = 82;
        String grade;
        if (marks >= 90) {
            grade = "A";
        } else if (marks >= 75) {
            grade = "B";
        } else if (marks >= 50) {
            grade = "C";
        } else {
            grade = "Fail";
        }
        System.out.println("Marks " + marks + " -> " + grade);

        // ---- 2. Delivery-fee rules (real business logic) ----
        int orderValue = 350;
        int distanceKm = 5;
        boolean isMember = false;
        int fee;
        if (isMember || orderValue >= 499) {
            fee = 0;
        } else if (distanceKm <= 3) {
            fee = 30;
        } else if (distanceKm <= 7) {
            fee = 50;
        } else {
            fee = 80;
        }
        System.out.println("Order Rs. " + orderValue + ", " + distanceKm + " km, member=" + isMember
                + " -> delivery fee Rs. " + fee);

        // ---- 3. Conditions must be true/false (no "truthy" values in Java) ----
        String name = "";
        if (name.isEmpty()) {                       // not: if (name)
            System.out.println("Please enter your name");
        }
        int stock = 0;
        if (stock == 0) {                           // not: if (!stock)
            System.out.println("Out of stock");
        }

        // ---- 4. Combining conditions and the ternary operator ----
        int age = 34;
        System.out.println("Working-age adult? " + (age >= 18 && age < 60));
        String status = age >= 18 ? "adult" : "minor";
        System.out.println(status);
        System.out.println("Items: " + 1 + (1 == 1 ? " item" : " items"));

        // ---- 5. Comparing text and several answers ----
        String answer = "Yes";
        if (answer.equalsIgnoreCase("y") || answer.equalsIgnoreCase("yes")) {
            System.out.println("Order confirmed");
        }

        // ---- 6. switch expression: many choices, one value ----
        String command = "halt";
        String reply = switch (command) {
            case "go" -> "Starting";
            case "stop", "halt" -> "Stopping";
            default -> "Unknown command";
        };
        System.out.println(reply);

        int day = 6;
        String dayType = switch (day) {
            case 1, 2, 3, 4, 5 -> "Weekday";
            case 6, 7 -> "Weekend";
            default -> "Invalid day";
        };
        System.out.println("Day " + day + " is a " + dayType);

        // ---- 7. Ticket price: decisions that build on each other ----
        age = 8;
        boolean isWeekend = true;
        int price;
        if (age < 5) {
            price = 0;
        } else if (age < 12 || age >= 60) {
            price = 100;
        } else {
            price = 200;
        }
        if (isWeekend && price > 0) {
            price += 50;                           // weekend surcharge
        }
        System.out.println("Age " + age + ", weekend=" + isWeekend + " -> ticket Rs. " + price);

        // ---- 8. The classic bug: = vs ==, and a missing else ----
        int score = 5;
        if (score == 5) {
            System.out.println("score is five");
        }
        if (score > 3) System.out.println("one-line if without braces works...");
    }
}
