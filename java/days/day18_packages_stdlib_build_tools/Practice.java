/* Day 18 - Practice: the standard library (java.time, java.util) and reading a pom.xml.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 * All dates are text in the form "yyyy-MM-dd". 2026-11-16 is a Monday.
 */
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.Period;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalAdjusters;
import java.util.*;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | daysUntil   (Level 1 - Beginner)
    // Number of days from todayText to eventText (negative when the event is in the past).
    //   daysUntil("2026-11-16", "2026-12-25") -> 39
    // Hint: LocalDate.parse(text) and ChronoUnit.DAYS.between(from, to)
    // ---------------------------------------------------------------------------
    static long daysUntil(String todayText, String eventText) {
        // TODO: write your code here
        return -999;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | formatDate   (Level 1 - Beginner)
    // "2026-12-05" -> "05 Dec 2026"
    // Hint: DateTimeFormatter.ofPattern("dd MMM yyyy", Locale.ENGLISH) and date.format(...).
    // (Without Locale.ENGLISH the month name would depend on the computer's language.)
    // ---------------------------------------------------------------------------
    static String formatDate(String isoText) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | medianAndMean   (Level 1 - Beginner)
    // Return {median, mean} with the mean rounded to 2 decimals. At least one number.
    // The median of an even count is the average of the two middle numbers. Do not
    // change the array that came in (sort a copy).
    //   medianAndMean(new int[]{3, 1, 2, 10}) -> {2.5, 4.0}
    // ---------------------------------------------------------------------------
    static double[] medianAndMean(int[] numbers) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | mostCommonWords   (Level 2 - Intermediate)
    // Lowercase the text, split on spaces, count the words and return the n most common
    // as "word=count" texts, biggest count first. Ties -> alphabetical order.
    //   mostCommonWords("the cat and the hat and the bat", 2) -> [the=3, and=2]
    // ---------------------------------------------------------------------------
    static List<String> mostCommonWords(String text, int n) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | groupByLength   (Level 2 - Intermediate)
    // Return a map {length -> words with that length}; inside each list keep the
    // original order. Hint: computeIfAbsent.
    //   groupByLength([hi, yo, sun]) -> {2=[hi, yo], 3=[sun]}
    // ---------------------------------------------------------------------------
    static Map<Integer, List<String>> groupByLength(List<String> words) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | ageInYears   (Level 2 - Intermediate)
    // Completed years between the birth date and today (birthday not reached yet ->
    // one year less).
    //   ageInYears("2000-11-17", "2026-11-16") -> 25     ageInYears("2000-11-16", "2026-11-16") -> 26
    // Hint: Period.between(birth, today).getYears()
    // ---------------------------------------------------------------------------
    static int ageInYears(String birthText, String todayText) {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L2-4 | tagValue (read a pom.xml)   (Level 2 - Intermediate)
    // Return the text between the FIRST <tag> and </tag> in xml (spaces around it
    // removed), or "" when the tag is missing.
    //   tagValue("<a><version> 1.2 </version></a>", "version") -> "1.2"
    //   tagValue("<a></a>", "version") -> ""
    // Hint: indexOf, the length of the opening tag, and substring.
    // ---------------------------------------------------------------------------
    static String tagValue(String xml, String tag) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | possibleTeams   (Level 3 - Challenge)
    // All different teams of `size` players. Return a list of teams; the players inside
    // each team and the teams themselves are in alphabetical order. A team of 0 players
    // is one empty team; a size bigger than the number of players gives no teams.
    //   possibleTeams([C, A, B], 2) -> [[A, B], [A, C], [B, C]]
    // Idea (recursion): sort the players. For each player in turn: that player + every
    // team of size-1 chosen from the players AFTER him/her (subList(i + 1, n)).
    // ---------------------------------------------------------------------------
    static List<List<String>> possibleTeams(List<String> players, int size) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | nextWeekday   (Level 3 - Challenge)
    // Return the ISO date of the NEXT given weekday strictly AFTER dateText.
    // weekdayName is e.g. "friday" (any capitalisation).
    //   nextWeekday("2026-11-16", "friday") -> "2026-11-20"
    //   nextWeekday("2026-11-16", "monday") -> "2026-11-23"   (not the same day)
    // Hint: DayOfWeek.valueOf("FRIDAY") and date.with(TemporalAdjusters.next(day)).
    // ---------------------------------------------------------------------------
    static String nextWeekday(String dateText, String weekdayName) {
        // TODO: write your code here
        return null;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    public static void main(String[] args) {
        System.out.println("--- Day 18 checks ---");
        Checker.check("L1-1 daysUntil", () -> daysUntil("2026-11-16", "2026-12-25"), 39);
        Checker.check("L1-1 daysUntil in the past", () -> daysUntil("2026-11-16", "2026-11-10"), -6);
        Checker.check("L1-1 daysUntil across a leap day", () -> daysUntil("2028-02-28", "2028-03-01"), 2);
        Checker.check("L1-2 formatDate", () -> formatDate("2026-12-05"), "05 Dec 2026");
        Checker.check("L1-2 formatDate September", () -> formatDate("2026-09-01"), "01 Sep 2026");
        Checker.check("L1-3 medianAndMean even count", () -> medianAndMean(new int[]{3, 1, 2, 10}), new double[]{2.5, 4.0});
        Checker.check("L1-3 medianAndMean odd count", () -> medianAndMean(new int[]{5, 1, 3}), new double[]{3.0, 3.0});
        Checker.check("L1-3 medianAndMean rounds the mean", () -> medianAndMean(new int[]{1, 2, 2}), new double[]{2.0, 1.67});
        int[] data = {3, 1, 2, 10};
        Checker.check("L1-3 medianAndMean leaves the input alone", () -> {
            medianAndMean(data);
            return data;
        }, new int[]{3, 1, 2, 10});
        Checker.check("L2-1 mostCommonWords", () -> mostCommonWords("the cat and the hat and the bat", 2), List.of("the=3", "and=2"));
        Checker.check("L2-1 mostCommonWords ties alphabetical", () -> mostCommonWords("b a c a b", 3), List.of("a=2", "b=2", "c=1"));
        Checker.check("L2-1 mostCommonWords lowercases", () -> mostCommonWords("Tea tea TEA chai", 1), List.of("tea=3"));
        Checker.check("L2-2 groupByLength", () -> groupByLength(List.of("hi", "yo", "sun", "a")),
                Map.of(2, List.of("hi", "yo"), 3, List.of("sun"), 1, List.of("a")));
        Checker.check("L2-2 groupByLength empty", () -> groupByLength(List.of()), Map.of());
        Checker.check("L2-3 ageInYears birthday tomorrow", () -> ageInYears("2000-11-17", "2026-11-16"), 25);
        Checker.check("L2-3 ageInYears birthday today", () -> ageInYears("2000-11-16", "2026-11-16"), 26);
        Checker.check("L2-3 ageInYears earlier in the year", () -> ageInYears("2000-01-01", "2026-11-16"), 26);
        String pom = """
                <project>
                  <groupId>shop</groupId>
                  <artifactId> billing </artifactId>
                  <version>1.2</version>
                  <dependency><artifactId>junit</artifactId></dependency>
                </project>
                """;
        Checker.check("L2-4 tagValue", () -> tagValue(pom, "groupId"), "shop");
        Checker.check("L2-4 tagValue trims spaces", () -> tagValue(pom, "artifactId"), "billing");
        Checker.check("L2-4 tagValue version", () -> tagValue(pom, "version"), "1.2");
        Checker.check("L2-4 tagValue missing tag", () -> tagValue(pom, "packaging"), "");
        Checker.check("L2-4 tagValue missing closing tag", () -> tagValue("<a>5", "a"), "");
        Checker.check("L3-1 possibleTeams", () -> possibleTeams(List.of("C", "A", "B"), 2),
                List.of(List.of("A", "B"), List.of("A", "C"), List.of("B", "C")));
        Checker.check("L3-1 possibleTeams count", () -> possibleTeams(List.of("A", "B", "C", "D", "E"), 3).size(), 10);
        Checker.check("L3-1 possibleTeams of one", () -> possibleTeams(List.of("B", "A"), 1), List.of(List.of("A"), List.of("B")));
        Checker.check("L3-1 possibleTeams too big", () -> possibleTeams(List.of("A", "B"), 3), List.of());
        Checker.check("L3-2 nextWeekday", () -> nextWeekday("2026-11-16", "friday"), "2026-11-20");
        Checker.check("L3-2 nextWeekday same day -> next week", () -> nextWeekday("2026-11-16", "Monday"), "2026-11-23");
        Checker.check("L3-2 nextWeekday from a Friday", () -> nextWeekday("2026-11-20", "monday"), "2026-11-23");
        Checker.check("L3-2 nextWeekday over New Year", () -> nextWeekday("2026-12-31", "thursday"), "2027-01-07");
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
