import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

/* Day 24 mini project: real JUnit 5 tests. Run them with run_tests.ps1 (see the lesson), then break Shop.java
 * on purpose (for example change 100 - percent to 100 + percent) and watch a test fail. */
class ShopTest {
    private Cart cart;

    @BeforeEach                          // runs before EVERY test: each test gets a fresh cart
    void freshCart() {
        cart = new Cart();
    }

    @Test
    void tenPercentOff() {
        assertEquals(180.0, Shop.applyDiscount(200, 10));
    }

    @Test
    void zeroPercentChangesNothing() {
        assertEquals(99.5, Shop.applyDiscount(99.5, 0));
    }

    @Test
    void negativePriceIsRejected() {
        assertThrows(IllegalArgumentException.class, () -> Shop.applyDiscount(-5, 10));
    }

    @ParameterizedTest                   // one test method, many rows
    @CsvSource({"100, 10, 90.0", "50, 50, 25.0", "80, 0, 80.0"})
    void discountTable(double price, int percent, double expected) {
        assertEquals(expected, Shop.applyDiscount(price, percent));
    }

    @Test
    void newCartIsEmpty() {
        assertEquals(0, cart.size());
        assertEquals(0.0, cart.total());
    }

    @Test
    void cartAddsUpPrices() {
        cart.add(10.5);
        cart.add(20);
        assertEquals(30.5, cart.total());
        assertEquals(2, cart.size());
    }

    @Test
    void decimalsNeedATolerance() {
        assertEquals(0.3, 0.1 + 0.2, 0.000001);   // the third argument is the allowed difference
    }
}
