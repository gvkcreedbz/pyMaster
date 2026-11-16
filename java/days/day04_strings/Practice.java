/* Day 04 - Practice: strings.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | First name   (Level 1 - Beginner)
    // Return the first word.
    //   firstName("Aarav Sharma") -> "Aarav"
    // Hint: fullName.split(" ") cuts the text into words; the first word is [0].
    // ---------------------------------------------------------------------------
    static String firstName(String fullName) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | Initials   (Level 1 - Beginner)
    // For a name made of exactly two words, return the initials in capitals,
    // each followed by a dot.
    //   initials("aarav sharma") -> "A.S."
    // ---------------------------------------------------------------------------
    static String initials(String fullName) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | Shout   (Level 1 - Beginner)
    // Return the text in UPPERCASE followed by "!".
    //   shout("hello") -> "HELLO!"
    // ---------------------------------------------------------------------------
    static String shout(String text) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Username generator   (Level 2 - Intermediate)
    // Lowercase full name, spaces replaced by dots, plus the last 2 digits of the year
    // (always 2 digits: the year 2005 gives "05").
    //   makeUsername("Aarav Sharma", 2001) -> "aarav.sharma01"
    // Hint: String.format("%02d", birthYear % 100)
    // ---------------------------------------------------------------------------
    static String makeUsername(String fullName, int birthYear) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | Simple email validator   (Level 2 - Intermediate)
    // Valid when ALL are true: exactly one "@", no spaces, text before the "@",
    // and a "." somewhere AFTER the "@" (but not as the very last character).
    //   isValidEmail("a@b.com") -> true      isValidEmail("a@@b.com") -> false
    //   isValidEmail("a b@c.com") -> false   isValidEmail("a@b.") -> false
    // Hint: one return line with &&. indexOf("@") == lastIndexOf("@") means "at most one @".
    // ---------------------------------------------------------------------------
    static boolean isValidEmail(String email) {
        // TODO: write your code here
        return false;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | Capitalise a word   (Level 2 - Intermediate)
    // First letter UPPER case, all the other letters lower case. (Java has no
    // title() or capitalize(): build it with substring.)
    //   capitalize("hELLO") -> "Hello"      capitalize("a") -> "A"
    // ---------------------------------------------------------------------------
    static String capitalize(String word) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-4 | Message cleaner   (Level 2 - Intermediate)
    // Remove outer spaces, collapse repeated spaces into one, capitalise the first
    // letter (and lower-case the rest). You may call your capitalize() from above.
    //   cleanMessage("   hello    world  ") -> "Hello world"
    // Hint: String.join(" ", text.strip().split("\\s+"))
    // ---------------------------------------------------------------------------
    static String cleanMessage(String text) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | CamelCase hashtag   (Level 3 - Challenge)
    // The caption has exactly THREE words. Remove the characters . , ! ? and the
    // extra spaces, capitalise every word, join them and put # in front.
    // (On Day 6 you will learn loops and can handle any number of words.)
    //   makeHashtag("learning java daily!")      -> "#LearningJavaDaily"
    //   makeHashtag("  chai  with   friends, ")  -> "#ChaiWithFriends"
    // ---------------------------------------------------------------------------
    static String makeHashtag(String caption) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | Palindrome   (Level 3 - Challenge)
    // true if the text reads the same backwards, ignoring upper/lower case and spaces.
    //   isPalindrome("Never odd or even") -> true      isPalindrome("Python") -> false
    // Hint: new StringBuilder(text).reverse().toString() gives the reversed text,
    // and compare texts with equals (NOT ==).
    // ---------------------------------------------------------------------------
    static boolean isPalindrome(String text) {
        // TODO: write your code here
        return false;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 04 checks ---");
        Checker.check("L1-1 firstName", () -> firstName("Aarav Sharma"), "Aarav");
        Checker.check("L1-1 firstName #2", () -> firstName("  Diya Rao"), "Diya");
        Checker.check("L1-2 initials", () -> initials("aarav sharma"), "A.S.");
        Checker.check("L1-3 shout", () -> shout("hello"), "HELLO!");
        Checker.check("L2-1 makeUsername", () -> makeUsername("Aarav Sharma", 2001), "aarav.sharma01");
        Checker.check("L2-1 makeUsername #2", () -> makeUsername("Diya Rao", 1999), "diya.rao99");
        Checker.check("L2-1 makeUsername #3", () -> makeUsername("Kabir Das", 2005), "kabir.das05");
        Checker.check("L2-2 valid email", () -> isValidEmail("a@b.com"), true);
        Checker.check("L2-2 two @", () -> isValidEmail("a@@b.com"), false);
        Checker.check("L2-2 space", () -> isValidEmail("a b@c.com"), false);
        Checker.check("L2-2 ends with dot", () -> isValidEmail("a@b."), false);
        Checker.check("L2-2 no dot after @", () -> isValidEmail("a.b@c"), false);
        Checker.check("L2-2 nothing before @", () -> isValidEmail("@b.com"), false);
        Checker.check("L2-3 capitalize", () -> capitalize("hELLO"), "Hello");
        Checker.check("L2-3 capitalize one letter", () -> capitalize("a"), "A");
        Checker.check("L2-4 cleanMessage", () -> cleanMessage("   hello    world  "), "Hello world");
        Checker.check("L2-4 cleanMessage #2", () -> cleanMessage("  gOOD   MORNING  all "), "Good morning all");
        Checker.check("L3-1 makeHashtag", () -> makeHashtag("learning java daily!"), "#LearningJavaDaily");
        Checker.check("L3-1 makeHashtag #2", () -> makeHashtag("  chai  with   friends, "), "#ChaiWithFriends");
        Checker.check("L3-2 palindrome yes", () -> isPalindrome("Never odd or even"), true);
        Checker.check("L3-2 palindrome no", () -> isPalindrome("Python"), false);
        Checker.check("L3-2 palindrome #3", () -> isPalindrome("A man a plan a canal Panama"), true);
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
