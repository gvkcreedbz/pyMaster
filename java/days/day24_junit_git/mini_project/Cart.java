import java.util.ArrayList;
import java.util.List;

/* Day 24 mini project: a tiny shopping cart (the second class we test). */
public class Cart {
    private final List<Double> prices = new ArrayList<>();

    public void add(double price) {
        if (price <= 0) {
            throw new IllegalArgumentException("Price must be positive");
        }
        prices.add(price);
    }

    public int size() {
        return prices.size();
    }

    public double total() {
        double sum = 0;
        for (double price : prices) {
            sum += price;
        }
        return sum;
    }
}
