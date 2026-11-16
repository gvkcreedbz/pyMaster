/* Day 05 - Practice: decisions with if / else if / else and switch.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Grade letter   (Level 1 - Beginner)
    // 90 and above -> "A", 75-89 -> "B", 50-74 -> "C", below 50 -> "Fail"
    //   grade(82) -> "B"
    // ---------------------------------------------------------------------------
    static String grade(int marks) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Sign of a number   (Level 1 - Beginner)
    // Return "positive", "negative" or "zero".
    //   sign(5) -> "positive"      sign(-2) -> "negative"      sign(0) -> "zero"
    // ---------------------------------------------------------------------------
    static String sign(int n) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Biggest of three   (Level 1 - Beginner)
    // Return the largest of a, b, c using if / else if (do NOT use Math.max).
    //   maxOfThree(1, 9, 3) -> 9
    // ---------------------------------------------------------------------------
    static int maxOfThree(int a, int b, int c) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Delivery fee   (Level 2 - Intermediate)
    // Members always pay 0. Non-members pay 0 when orderValue >= 499.
    // Otherwise: distanceKm <= 3 -> 30, <= 7 -> 50, farther -> 80.
    //   deliveryFee(300, 5, false) -> 50
    // ---------------------------------------------------------------------------
    static int deliveryFee(int orderValue, int distanceKm, boolean isMember) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Ticket price   (Level 2 - Intermediate)
    // Base price 200. Under 5 years: free (0). Under 12, or 60 and above: half price (100).
    // A weekend surcharge of +50 applies only if the ticket is not free.
    //   ticketPrice(8, true) -> 150      ticketPrice(3, true) -> 0
    // ---------------------------------------------------------------------------
    static int ticketPrice(int age, boolean isWeekend) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Leap year   (Level 2 - Intermediate)
    // Divisible by 4, except century years, which must be divisible by 400.
    //   2024 -> true, 1900 -> false, 2000 -> true, 2023 -> false
    // ---------------------------------------------------------------------------
    static boolean isLeapYear(int year) {
        // TODO: write your code here
        return false;
    }

    // ---------------------------------------------------------------------------
    // L2-4 | Weekday name   (Level 2 - Intermediate)
    // Use a switch EXPRESSION: 1 -> "Monday", 2 -> "Tuesday", 3 -> "Wednesday",
    // 4 -> "Thursday", 5 -> "Friday", 6 -> "Saturday", 7 -> "Sunday",
    // any other number -> "Invalid day".
    //   dayName(3) -> "Wednesday"      dayName(9) -> "Invalid day"
    // ---------------------------------------------------------------------------
    static String dayName(int day) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | Rock-paper-scissors referee   (Level 3 - Challenge)
    // Inputs are "rock", "paper" or "scissors". Rock beats scissors, scissors beats
    // paper, paper beats rock. Return "Player 1 wins", "Player 2 wins" or "Draw".
    // Remember: compare Strings with equals, never ==.
    // ---------------------------------------------------------------------------
    static String rps(String p1, String p2) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Triangle classifier   (Level 3 - Challenge)
    // If the sum of any two sides is <= the third side -> "Not a triangle".
    // Otherwise: all equal -> "Equilateral", exactly two equal -> "Isosceles",
    // none equal -> "Scalene".
    //   triangleType(3, 4, 5) -> "Scalene"      triangleType(1, 2, 3) -> "Not a triangle"
    // ---------------------------------------------------------------------------
    static String triangleType(int a, int b, int c) {
        // TODO: write your code here
        return null;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 05 checks ---");
        Checker.check("L1-1 grade(95)", () -> grade(95), "A");
        Checker.check("L1-1 grade(90)", () -> grade(90), "A");
        Checker.check("L1-1 grade(80)", () -> grade(80), "B");
        Checker.check("L1-1 grade(50)", () -> grade(50), "C");
        Checker.check("L1-1 grade(49)", () -> grade(49), "Fail");
        Checker.check("L1-2 sign(5)", () -> sign(5), "positive");
        Checker.check("L1-2 sign(-2)", () -> sign(-2), "negative");
        Checker.check("L1-2 sign(0)", () -> sign(0), "zero");
        Checker.check("L1-3 maxOfThree", () -> new int[]{maxOfThree(1, 9, 3), maxOfThree(9, 2, 3), maxOfThree(1, 2, 3)},
                new int[]{9, 9, 3});
        Checker.check("L2-1 deliveryFee near", () -> deliveryFee(300, 2, false), 30);
        Checker.check("L2-1 deliveryFee mid", () -> deliveryFee(300, 5, false), 50);
        Checker.check("L2-1 deliveryFee far", () -> deliveryFee(300, 10, false), 80);
        Checker.check("L2-1 deliveryFee big order", () -> deliveryFee(600, 10, false), 0);
        Checker.check("L2-1 deliveryFee member", () -> deliveryFee(100, 10, true), 0);
        Checker.check("L2-1 deliveryFee exactly 499", () -> deliveryFee(499, 9, false), 0);
        Checker.check("L2-2 ticketPrice(3, weekend)", () -> ticketPrice(3, true), 0);
        Checker.check("L2-2 ticketPrice(8, weekday)", () -> ticketPrice(8, false), 100);
        Checker.check("L2-2 ticketPrice(8, weekend)", () -> ticketPrice(8, true), 150);
        Checker.check("L2-2 ticketPrice(30, weekday)", () -> ticketPrice(30, false), 200);
        Checker.check("L2-2 ticketPrice(30, weekend)", () -> ticketPrice(30, true), 250);
        Checker.check("L2-2 ticketPrice(65, weekday)", () -> ticketPrice(65, false), 100);
        Checker.check("L2-3 leap years", () -> new boolean[]{isLeapYear(2024), isLeapYear(1900), isLeapYear(2000), isLeapYear(2023)},
                new boolean[]{true, false, true, false});
        Checker.check("L2-4 dayName", () -> new String[]{dayName(1), dayName(3), dayName(7)},
                new String[]{"Monday", "Wednesday", "Sunday"});
        Checker.check("L2-4 dayName invalid", () -> new String[]{dayName(0), dayName(9)},
                new String[]{"Invalid day", "Invalid day"});
        Checker.check("L3-1 rps draw", () -> rps("rock", "rock"), "Draw");
        Checker.check("L3-1 rps p1", () -> new String[]{rps("rock", "scissors"), rps("scissors", "paper"), rps("paper", "rock")},
                new String[]{"Player 1 wins", "Player 1 wins", "Player 1 wins"});
        Checker.check("L3-1 rps p2", () -> new String[]{rps("scissors", "rock"), rps("paper", "scissors"), rps("rock", "paper")},
                new String[]{"Player 2 wins", "Player 2 wins", "Player 2 wins"});
        Checker.check("L3-2 triangle",
                () -> new String[]{triangleType(3, 3, 3), triangleType(3, 3, 5), triangleType(3, 4, 5), triangleType(1, 2, 3)},
                new String[]{"Equilateral", "Isosceles", "Scalene", "Not a triangle"});
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
