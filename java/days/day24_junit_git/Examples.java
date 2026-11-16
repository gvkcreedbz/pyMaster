/* Day 24 - Code along: tests that catch a Black-Friday discount bug (JUnit 5).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * The JUnit jar in java/lib is put on the class path for you.
 * The mini project (Shop.java + ShopTest.java in the folder mini_project) shows the same tests the "real" way.
 */
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.platform.engine.TestExecutionResult;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.LauncherDiscoveryRequest;
import org.junit.platform.launcher.TestExecutionListener;
import org.junit.platform.launcher.TestIdentifier;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
class Examples {
    // ---- The code under test ----
    static double applyDiscount(double price, int percent) {
        if (price < 0) {
            throw new IllegalArgumentException("Price must not be negative");
        }
        return Math.round(price * (100 - percent)) / 100.0;
    }
    // A buggy copy: a "<" instead of "<=" at the boundary. Only a boundary test finds it.
    static String buggyGrade(int score) {
        return score > 90 ? "A" : score >= 50 ? "B" : "F";          // bug: 90 should be an "A"
    }
    static class Cart {
        private final List<Double> prices = new ArrayList<>();
        void add(double price) {
            prices.add(price);
        }
        double total() {
            double sum = 0;
            for (double price : prices) {
                sum += price;
            }
            return sum;
        }
    }
    // ---- Real JUnit tests: ordinary methods marked with @Test ----
    static class ShopTests {
        private Cart cart;
        @BeforeEach                                   // runs before EVERY test method
        void freshCart() {
            cart = new Cart();
        }
        @Test
        void tenPercentOff() {
            assertEquals(180.0, applyDiscount(200, 10));
        }
        @Test
        void negativePriceIsRejected() {
            assertThrows(IllegalArgumentException.class, () -> applyDiscount(-5, 10));
        }
        @ParameterizedTest                            // one method, three test cases
        @CsvSource({"100, 10, 90.0", "50, 50, 25.0", "80, 0, 80.0"})
        void discountTable(double price, int percent, double expected) {
            assertEquals(expected, applyDiscount(price, percent));
        }
        @Test
        void newCartIsEmpty() {
            assertEquals(0.0, cart.total());
        }
        @Test
        void decimalsNeedATolerance() {
            assertEquals(0.3, 0.1 + 0.2, 0.000001);   // 0.1 + 0.2 is 0.30000000000000004
        }
        @Test
        void thisTestFailsOnPurpose() {                // to SEE what a failure looks like
            assertEquals("A", buggyGrade(90));
        }
    }
    // A listener prints one line per test, like the JUnit console launcher does
    static class Printer implements TestExecutionListener {
        @Override
        public void executionFinished(TestIdentifier test, TestExecutionResult result) {
            if (test.isTest()) {
                boolean passed = result.getStatus() == TestExecutionResult.Status.SUCCESSFUL;
                String why = result.getThrowable().map(t -> "   <- " + t.getMessage()).orElse("");
                System.out.println("  " + (passed ? "PASS " : "FAIL ") + test.getDisplayName() + why);
            }
        }
    }
    public static void main(String[] args) {
        // ---- 1. A test is a check that shouts when something is wrong ----
        System.out.println("1. assertEquals either stays silent or throws");
        assertEquals(180.0, applyDiscount(200, 10));                       // silent: all good
        try {
            assertEquals(190.0, applyDiscount(200, 10));                   // wrong on purpose
        } catch (AssertionError e) {
            System.out.println("  caught: " + e.getMessage());
        }
        // Java's own `assert` keyword is OFF unless you start the program with -ea, so use JUnit's assertions.
        boolean javaAssertOn = false;
        assert javaAssertOn = true;                                         // only runs when -ea is given
        System.out.println("  Java's own assert is " + (javaAssertOn ? "ON" : "OFF"));
        // ---- 2. What a test runner does, by hand ----
        System.out.println("2. A tiny test runner");
        Map<String, Runnable> tests = new LinkedHashMap<>();
        tests.put("90 is an A", () -> assertEquals("A", buggyGrade(90)));
        tests.put("95 is an A", () -> assertEquals("A", buggyGrade(95)));
        tests.put("49 is an F", () -> assertEquals("F", buggyGrade(49)));
        for (Map.Entry<String, Runnable> test : tests.entrySet()) {
            try {
                test.getValue().run();
                System.out.println("  PASS " + test.getKey());
            } catch (AssertionError e) {
                System.out.println("  FAIL " + test.getKey() + "   <- " + e.getMessage());
            }
        }
        System.out.println("  Only the BOUNDARY test (90) found the bug. 95 and 49 looked fine.");
        // ---- 3. The real JUnit launcher runs the @Test methods ----
        System.out.println("3. JUnit runs ShopTests");
        LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
                .selectors(DiscoverySelectors.selectClass(ShopTests.class)).build();
        LauncherFactory.create().execute(request, new Printer());
        // ---- 4. Good tests cover normal, edge and error cases ----
        System.out.println("4. Think: normal (200, 10), edge (0 percent, price 0) and error (negative price).");
    }
}
