/* Day 24 mini project: the code we want to test. See ShopTest.java for its tests. */
public class Shop {
    /** Price after a percentage discount, rounded to 2 decimals. */
    public static double applyDiscount(double price, int percent) {
        if (price < 0) {
            throw new IllegalArgumentException("Price must not be negative");
        }
        return Math.round(price * (100 - percent)) / 100.0;
    }
}
