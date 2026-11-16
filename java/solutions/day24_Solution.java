// SOLUTION FILE - try the hint ladder first!
/* Day 24 - Practice: testing with JUnit 5.
 *
 * Run:  java Practice.java      (the JUnit jar in java/lib is put on the class path for you)
 * Today YOU write the TESTS. The checker grades them by "mutation testing":
 *  - your test must PASS on the correct code, and
 *  - it must FAIL on secretly broken copies ("mutants") of that code.
 * A weak test (like assertTrue(true)) lets the mutants survive -> FAIL.
 *
 * How it works: a test method receives the thing it tests as a PARAMETER (a function, or a way to make an
 * Account). In your own projects you would call the real method directly; here the checker hands your test
 * the real code first and then the broken versions. Use JUnit's assertions: assertEquals(expected, actual),
 * assertTrue, assertFalse, assertThrows. (Plain Java `assert` is switched off unless you run with -ea.)
 */
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.util.function.*;
import org.junit.jupiter.api.Test;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.LauncherDiscoveryRequest;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;
import org.junit.platform.launcher.listeners.TestExecutionSummary;
class Practice {
    // ---------------------------------------------------------------------------
    // L1-1 | testIsEven   (Level 1 - Beginner)
    // isEven below is correct. Write the BODY of testIsEven: several assertions that would catch a broken
    // version. Think: an even number, an odd number, zero, a negative even and a negative odd number.
    //   assertTrue(isEven.test(4));    assertFalse(isEven.test(7));
    // ---------------------------------------------------------------------------
    static boolean isEven(int n) {
        return n % 2 == 0;
    }
    static void testIsEven(Predicate<Integer> isEven) {
        // >>> SOLUTION
        assertTrue(isEven.test(4));
        assertFalse(isEven.test(7));
        assertTrue(isEven.test(0));
        assertTrue(isEven.test(-4));
        assertFalse(isEven.test(-3));
        // <<< SOLUTION
    }
    // ---------------------------------------------------------------------------
    // L1-2 | clamp   (Level 1 - Beginner)
    // Return `value` limited to the range low..high:
    //   clamp(5, 0, 10) -> 5    clamp(-3, 0, 10) -> 0    clamp(15, 0, 10) -> 10
    // ---------------------------------------------------------------------------
    static int clamp(int value, int low, int high) {
        // >>> SOLUTION stub: return 0;
        if (value < low) {
            return low;
        }
        if (value > high) {
            return high;
        }
        return value;
        // <<< SOLUTION
    }
    // ---------------------------------------------------------------------------
    // L1-3 | testPercentToGrade   (Level 1 - Beginner)
    // Rules: >= 90 "A", >= 75 "B", >= 50 "C", else "F". Bugs love BOUNDARIES: test the exact boundary
    // values AND the numbers just below them. grade.apply(90) calls the function under test.
    // ---------------------------------------------------------------------------
    static String percentToGrade(int score) {
        if (score >= 90) {
            return "A";
        }
        if (score >= 75) {
            return "B";
        }
        if (score >= 50) {
            return "C";
        }
        return "F";
    }
    static void testPercentToGrade(Function<Integer, String> grade) {
        // >>> SOLUTION
        assertEquals("A", grade.apply(100));
        assertEquals("A", grade.apply(90));
        assertEquals("B", grade.apply(89));
        assertEquals("B", grade.apply(75));
        assertEquals("C", grade.apply(74));
        assertEquals("C", grade.apply(50));
        assertEquals("F", grade.apply(49));
        assertEquals("F", grade.apply(0));
        // <<< SOLUTION
    }
    // ---------------------------------------------------------------------------
    // L2-1 | testSlugify   (Level 2 - Intermediate)
    // slugify("  Hello,  World! ") -> "hello-world"  (lower-case, symbols removed, spaces collapsed
    // to a single "-", no "-" at the ends). Write a test that loops over a table of
    // {input, expected} pairs. It must catch 3 different bugs.
    // ---------------------------------------------------------------------------
    static String slugify(String text) {
        String cleaned = text.toLowerCase().replaceAll("[^a-z0-9 ]", "");
        return String.join("-", cleaned.trim().split("\\s+"));
    }
    static void testSlugify(Function<String, String> slugify) {
        // >>> SOLUTION
        String[][] cases = {
                {"Hello World", "hello-world"},
                {"  Hello,  World! ", "hello-world"},
                {"Python 3.13 Rocks", "python-313-rocks"},
                {"", ""},
                {"ALLCAPS", "allcaps"},
        };
        for (String[] testCase : cases) {
            assertEquals(testCase[1], slugify.apply(testCase[0]));
        }
        // <<< SOLUTION
    }
    // ---------------------------------------------------------------------------
    // L2-2 | testWithdrawRejectsOverdraft   (Level 2 - Intermediate)
    // Account (below, correct) throws IllegalArgumentException when you withdraw more than the balance,
    // and must leave the balance UNCHANGED. open.apply(100) gives you an account with Rs. 100.
    // Use assertThrows(IllegalArgumentException.class, () -> account.withdraw(150));
    // ---------------------------------------------------------------------------
    static class Account {
        protected int balance;
        Account(int balance) {
            this.balance = balance;
        }
        int getBalance() {
            return balance;
        }
        void deposit(int amount) {
            if (amount <= 0) {
                throw new IllegalArgumentException("amount must be positive");
            }
            balance += amount;
        }
        void withdraw(int amount) {
            if (amount <= 0 || amount > balance) {
                throw new IllegalArgumentException("invalid amount");
            }
            balance -= amount;
        }
    }
    static void testWithdrawRejectsOverdraft(Function<Integer, Account> open) {
        // >>> SOLUTION
        Account account = open.apply(100);
        assertThrows(IllegalArgumentException.class, () -> account.withdraw(150));
        assertEquals(100, account.getBalance());
        // <<< SOLUTION
    }
    // ---------------------------------------------------------------------------
    // L2-3 | testAccountFlow   (Level 2 - Intermediate)
    // Test the normal behaviour of Account: deposit increases the balance, withdraw decreases it
    // (including withdrawing the ENTIRE balance), and depositing 0 or a negative amount throws
    // IllegalArgumentException.
    // ---------------------------------------------------------------------------
    static void testAccountFlow(Function<Integer, Account> open) {
        // >>> SOLUTION
        Account account = open.apply(100);
        account.deposit(50);
        assertEquals(150, account.getBalance());
        account.withdraw(30);
        assertEquals(120, account.getBalance());
        account.withdraw(120);
        assertEquals(0, account.getBalance());
        assertThrows(IllegalArgumentException.class, () -> account.deposit(0));
        assertThrows(IllegalArgumentException.class, () -> account.deposit(-5));
        // <<< SOLUTION
    }
    // ---------------------------------------------------------------------------
    // L3-1 | wordCount (TDD)   (Level 3 - Challenge)
    // The tests in WordCountTest below already exist (real JUnit @Test methods). Write wordCount(text)
    // so they all pass: lower-case words (letters and apostrophes only, punctuation ignored) -> counts.
    //   wordCount("The cat. The DOG!") -> {the=2, cat=1, dog=1}
    // Hint: a regex "[a-z']+" on the lower-cased text (Day 23), then map.merge(word, 1, Integer::sum).
    // ---------------------------------------------------------------------------
    static Map<String, Integer> wordCount(String text) {
        // >>> SOLUTION stub: return null;
        Map<String, Integer> counts = new HashMap<>();
        java.util.regex.Matcher matcher = java.util.regex.Pattern.compile("[a-z']+").matcher(text.toLowerCase());
        while (matcher.find()) {
            counts.merge(matcher.group(), 1, Integer::sum);
        }
        return counts;
        // <<< SOLUTION
    }
    static class WordCountTest {
        @Test
        void countsWordsIgnoringCaseAndPunctuation() {
            assertEquals(Map.of("the", 2, "cat", 1, "dog", 1), wordCount("The cat. The DOG!"));
        }
        @Test
        void emptyTextGivesEmptyMap() {
            assertEquals(Map.of(), wordCount(""));
        }
        @Test
        void keepsApostrophes() {
            assertEquals(Map.of("don't", 1, "stop", 1), wordCount("don't stop"));
        }
    }
    // ---------------------------------------------------------------------------
    // L3-2 | median (finish it using tests)   (Level 3 - Challenge)
    // median(List.of(3, 1, 2)) -> 2.0    median(List.of(4, 1, 3, 2)) -> 2.5    median(List.of(5)) -> 5.0
    // median(List.of()) must throw new IllegalArgumentException("empty list").
    // The method is half written: the lines BELOW the markers are correct, but the first part is
    // missing. Run the checker, read the failure messages (they come from the real MedianTest below)
    // and complete the missing lines: reject an empty list, and sort a COPY of the numbers first.
    // ---------------------------------------------------------------------------
    static double median(List<Integer> numbers) {
        // >>> SOLUTION stub: List<Integer> ordered = new ArrayList<>(numbers);
        if (numbers.isEmpty()) {
            throw new IllegalArgumentException("empty list");
        }
        List<Integer> ordered = new ArrayList<>(numbers);
        Collections.sort(ordered);
        // <<< SOLUTION
        int middle = ordered.size() / 2;
        if (ordered.size() % 2 == 1) {
            return ordered.get(middle);
        }
        return (ordered.get(middle - 1) + ordered.get(middle)) / 2.0;
    }
    static class MedianTest {
        @Test
        void oddCountTakesTheMiddleAfterSorting() {
            assertEquals(2.0, median(List.of(3, 1, 2)));
            assertEquals(5.0, median(List.of(9, 1, 5, 7, 3)));
        }
        @Test
        void evenCountAveragesTheTwoMiddleOnes() {
            assertEquals(2.5, median(List.of(4, 1, 3, 2)));
        }
        @Test
        void singleNumber() {
            assertEquals(5.0, median(List.of(5)));
        }
        @Test
        void emptyListIsRejected() {
            IllegalArgumentException error = assertThrows(IllegalArgumentException.class, () -> median(List.of()));
            assertEquals("empty list", error.getMessage());
        }
        @Test
        void doesNotChangeTheCallersList() {
            List<Integer> original = new ArrayList<>(List.of(3, 1, 2));
            median(original);
            assertEquals(List.of(3, 1, 2), original);
        }
    }
    // ======================= AUTO-CHECKER (do not edit below) ====================
    /** Run the test on the real code (must pass) and on every mutant (must fail). */
    static <T> String mutationTest(Consumer<T> test, T real, Map<String, T> mutants) {
        if (!passes(test, real)) {
            return "your test FAILS on the correct code - fix the test";
        }
        List<String> survivors = new ArrayList<>();
        for (Map.Entry<String, T> mutant : mutants.entrySet()) {
            if (passes(test, mutant.getValue())) {
                survivors.add(mutant.getKey());
            }
        }
        return survivors.isEmpty() ? "OK" : "test did not catch these bugs: " + survivors;
    }
    static <T> boolean passes(Consumer<T> test, T target) {
        try {
            test.accept(target);
            return true;
        } catch (Throwable e) {              // AssertionFailedError is an Error, so catch Throwable
            return false;
        }
    }
    /** Run the @Test methods of a class with the real JUnit launcher. Returns "OK" or the failure messages. */
    static String runJUnit(Class<?> testClass) {
        LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
                .selectors(DiscoverySelectors.selectClass(testClass)).build();
        SummaryGeneratingListener listener = new SummaryGeneratingListener();
        LauncherFactory.create().execute(request, listener);
        TestExecutionSummary summary = listener.getSummary();
        if (summary.getTestsFoundCount() == 0) {
            return "no tests found";
        }
        List<String> failures = new ArrayList<>();
        for (TestExecutionSummary.Failure failure : summary.getFailures()) {
            failures.add(failure.getTestIdentifier().getDisplayName() + " -> " + failure.getException());
        }
        return failures.isEmpty() ? "OK" : "failed: " + failures;
    }
    static class NoOverdraftCheck extends Account {
        NoOverdraftCheck(int balance) {
            super(balance);
        }
        @Override
        void withdraw(int amount) {
            balance -= amount;
        }
    }
    static class WrongException extends Account {
        WrongException(int balance) {
            super(balance);
        }
        @Override
        void withdraw(int amount) {
            if (amount > balance) {
                throw new IllegalStateException("wrong exception type");
            }
            balance -= amount;
        }
    }
    static class ChangesThenThrows extends Account {
        ChangesThenThrows(int balance) {
            super(balance);
        }
        @Override
        void withdraw(int amount) {
            balance -= amount;
            if (balance < 0) {
                throw new IllegalArgumentException("invalid amount");
            }
        }
    }
    static class DepositSubtracts extends Account {
        DepositSubtracts(int balance) {
            super(balance);
        }
        @Override
        void deposit(int amount) {
            balance -= amount;
        }
    }
    static class DepositAllowsAnything extends Account {
        DepositAllowsAnything(int balance) {
            super(balance);
        }
        @Override
        void deposit(int amount) {
            balance += amount;
        }
    }
    static class WithdrawDoesNothing extends Account {
        WithdrawDoesNothing(int balance) {
            super(balance);
        }
        @Override
        void withdraw(int amount) {
            if (amount > balance) {
                throw new IllegalArgumentException("invalid amount");
            }
        }
    }
    static class CannotEmptyAccount extends Account {
        CannotEmptyAccount(int balance) {
            super(balance);
        }
        @Override
        void withdraw(int amount) {
            if (amount >= balance) {
                throw new IllegalArgumentException("invalid amount");
            }
            balance -= amount;
        }
    }
    static Function<Integer, String> gradeMutant(int lowA, int lowB, int lowC) {
        return score -> score >= lowA ? "A" : score >= lowB ? "B" : score >= lowC ? "C" : "F";
    }
    public static void main(String[] args) {
        System.out.println("--- Day 24 checks ---");
        Map<String, Predicate<Integer>> isEvenMutants = new LinkedHashMap<>();
        isEvenMutants.put("returns odd instead", n -> n % 2 == 1);
        isEvenMutants.put("always true", n -> true);
        isEvenMutants.put("breaks on 0 and negatives", n -> n > 0 && n % 2 == 0);
        isEvenMutants.put("wrong for negative odd numbers (-3 % 2 is -1 in Java)", n -> n % 2 != 1);
        Checker.check("L1-1 testIsEven catches bugs", () -> mutationTest(Practice::testIsEven, Practice::isEven, isEvenMutants), "OK");
        Checker.check("L1-2 clamp values", () -> List.of(clamp(5, 0, 10), clamp(-3, 0, 10), clamp(15, 0, 10), clamp(0, 0, 10),
                clamp(10, 0, 10), clamp(7, 7, 7)), List.of(5, 0, 10, 0, 10, 7));
        Map<String, Function<Integer, String>> gradeMutants = new LinkedHashMap<>();
        gradeMutants.put("> 90 instead of >= 90", gradeMutant(91, 75, 50));
        gradeMutants.put("> 75 instead of >= 75", gradeMutant(90, 76, 50));
        gradeMutants.put("> 50 instead of >= 50", gradeMutant(90, 75, 51));
        Checker.check("L1-3 testPercentToGrade catches boundary bugs",
                () -> mutationTest(Practice::testPercentToGrade, Practice::percentToGrade, gradeMutants), "OK");
        Map<String, Function<String, String>> slugMutants = new LinkedHashMap<>();
        slugMutants.put("forgets lower-case", t -> String.join("-", t.replaceAll("[^a-zA-Z0-9 ]", "").trim().split("\\s+")));
        slugMutants.put("keeps extra spaces", t -> t.toLowerCase().replaceAll("[^a-z0-9 ]", "").replace(" ", "-"));
        slugMutants.put("keeps symbols", t -> String.join("-", t.toLowerCase().trim().split("\\s+")));
        Checker.check("L2-1 testSlugify catches bugs", () -> mutationTest(Practice::testSlugify, Practice::slugify, slugMutants), "OK");
        Map<String, Function<Integer, Account>> overdraftMutants = new LinkedHashMap<>();
        overdraftMutants.put("no overdraft check", NoOverdraftCheck::new);
        overdraftMutants.put("wrong exception type", WrongException::new);
        overdraftMutants.put("changes balance before throwing", ChangesThenThrows::new);
        Checker.check("L2-2 testWithdrawRejectsOverdraft catches bugs",
                () -> mutationTest(Practice::testWithdrawRejectsOverdraft, Account::new, overdraftMutants), "OK");
        Map<String, Function<Integer, Account>> flowMutants = new LinkedHashMap<>();
        flowMutants.put("deposit subtracts", DepositSubtracts::new);
        flowMutants.put("deposit accepts 0 / negative", DepositAllowsAnything::new);
        flowMutants.put("withdraw forgets to subtract", WithdrawDoesNothing::new);
        flowMutants.put("cannot withdraw the full balance", CannotEmptyAccount::new);
        Checker.check("L2-3 testAccountFlow catches bugs", () -> mutationTest(Practice::testAccountFlow, Account::new, flowMutants), "OK");
        Checker.check("L3-1 the provided WordCountTest passes (real JUnit)", () -> runJUnit(WordCountTest.class), "OK");
        Checker.check("L3-1 wordCount extra cases", () -> List.of(wordCount("Hello, hello HELLO"), wordCount("a b a. b! c?")),
                List.of(Map.of("hello", 3), Map.of("a", 2, "b", 2, "c", 1)));
        Checker.check("L3-2 the provided MedianTest passes (real JUnit)", () -> runJUnit(MedianTest.class), "OK");
        Checker.check("L3-2 median odd / even / single", () -> List.of(median(List.of(3, 1, 2)), median(List.of(4, 1, 3, 2)),
                median(List.of(5)), median(List.of(9, 1, 5, 7, 3))), List.of(2.0, 2.5, 5.0, 5.0));
        Checker.check("L3-2 median of an empty list throws IllegalArgumentException", () -> {
            try {
                median(List.of());
            } catch (IllegalArgumentException e) {
                return e.getMessage();
            }
            return "no error";
        }, "empty list");
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
