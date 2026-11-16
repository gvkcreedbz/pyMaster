/* Day 06 - Practice: loops.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | Sum 1..n   (Level 1 - Beginner)
    // Return 1 + 2 + ... + n using a loop.
    //   sumTo(5) -> 15      sumTo(100) -> 5050      sumTo(0) -> 0
    // ---------------------------------------------------------------------------
    static int sumTo(int n) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Count vowels   (Level 1 - Beginner)
    // Count a, e, i, o, u in the text (upper or lower case).
    //   countVowels("Hello World") -> 3
    // Hint: for (char ch : text.toLowerCase().toCharArray()) { ... }
    //       and "aeiou".indexOf(ch) is -1 when ch is not a vowel.
    // ---------------------------------------------------------------------------
    static int countVowels(String text) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Multiplication table   (Level 1 - Beginner)
    // Return 10 lines joined with "\n" (NO new line after the last one), like:
    //   5 x 1 = 5
    //   5 x 2 = 10   ...   5 x 10 = 50
    // ---------------------------------------------------------------------------
    static String multiplicationTable(int n) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Factorial   (Level 2 - Intermediate)
    // n! = 1 * 2 * ... * n.  Return a long (15! is already too big for an int).
    //   factorial(5) -> 120      factorial(0) -> 1      factorial(15) -> 1307674368000
    // ---------------------------------------------------------------------------
    static long factorial(int n) {
        // TODO: write your code here
        return 0;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | FizzBuzz   (Level 2 - Intermediate)
    // For numbers 1..n: multiples of 3 -> Fizz, of 5 -> Buzz, of both -> FizzBuzz,
    // otherwise the number. Return everything joined by single spaces (no space at the end).
    //   fizzbuzz(5) -> "1 2 Fizz 4 Buzz"
    // ---------------------------------------------------------------------------
    static String fizzbuzz(int n) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Prime check   (Level 2 - Intermediate)
    // Return true if n is prime (only divisible by 1 and itself). 0 and 1 are not.
    //   isPrime(7) -> true      isPrime(9) -> false      isPrime(1) -> false
    // ---------------------------------------------------------------------------
    static boolean isPrime(int n) {
        // TODO: write your code here
        return false;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | PIN with 3 attempts   (Level 3 - Challenge)
    // guessesText holds guesses separated by commas, e.g. "1111,2222,4321".
    // Return the attempt number (1, 2 or 3) at which the PIN was entered correctly.
    // Only the FIRST 3 guesses count (the card locks after that). Return 0 if the
    // PIN was never entered correctly within 3 attempts.
    //   firstCorrectAttempt("4321", "1111,2222,4321,0000") -> 3
    //   firstCorrectAttempt("4321", "1,2,3,4321")          -> 0
    // Hint: for (String guess : guessesText.split(",")) { ... } and equals (not ==).
    // ---------------------------------------------------------------------------
    static int firstCorrectAttempt(String correctPin, String guessesText) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Star pyramid   (Level 3 - Challenge)
    // Return a centred pyramid with n rows joined by "\n" (no new line at the end).
    // Row i has (2*i - 1) stars, padded on the left with (n - i) spaces. n = 3:
    //     *
    //    ***
    //   *****
    // Hint: " ".repeat(n - i) + "*".repeat(2 * i - 1)
    // ---------------------------------------------------------------------------
    static String pyramid(int n) {
        // TODO: write your code here
        return null;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 06 checks ---");
        Checker.check("L1-1 sumTo", () -> new int[]{sumTo(5), sumTo(100), sumTo(0)}, new int[]{15, 5050, 0});
        Checker.check("L1-2 countVowels", () -> new int[]{countVowels("Hello World"), countVowels("RHYTHM"), countVowels("AEIOU")},
                new int[]{3, 0, 5});
        Checker.check("L1-3 multiplicationTable", () -> {
            String[] lines = multiplicationTable(5).split("\n");
            return new String[]{lines[0], lines[1], lines[9]};
        }, new String[]{"5 x 1 = 5", "5 x 2 = 10", "5 x 10 = 50"});
        Checker.check("L1-3 table has 10 lines", () -> multiplicationTable(3).split("\n").length, 10);
        Checker.check("L1-3 no trailing new line", () -> multiplicationTable(3).endsWith("3 x 10 = 30"), true);
        Checker.check("L2-1 factorial", () -> new long[]{factorial(5), factorial(0), factorial(10), factorial(15)},
                new long[]{120, 1, 3628800, 1307674368000L});
        Checker.check("L2-2 fizzbuzz(5)", () -> fizzbuzz(5), "1 2 Fizz 4 Buzz");
        Checker.check("L2-2 fizzbuzz(15)", () -> fizzbuzz(15).endsWith("13 14 FizzBuzz"), true);
        Checker.check("L2-3 isPrime", () -> new boolean[]{isPrime(0), isPrime(1), isPrime(2), isPrime(7), isPrime(9), isPrime(97), isPrime(100)},
                new boolean[]{false, false, true, true, false, true, false});
        Checker.check("L3-1 pin attempt 3", () -> firstCorrectAttempt("4321", "1111,2222,4321,0000"), 3);
        Checker.check("L3-1 pin attempt 1", () -> firstCorrectAttempt("4321", "4321"), 1);
        Checker.check("L3-1 pin locked", () -> firstCorrectAttempt("4321", "1,2,3,4321"), 0);
        Checker.check("L3-1 pin never", () -> firstCorrectAttempt("4321", "1,2"), 0);
        Checker.check("L3-2 pyramid(3)", () -> pyramid(3), "  *\n ***\n*****");
        Checker.check("L3-2 pyramid(1)", () -> pyramid(1), "*");
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
