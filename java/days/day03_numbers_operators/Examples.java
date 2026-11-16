/* Day 03 - Code along: a shopping checkout, a loan EMI and a BMI calculator.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.math.BigDecimal;

class Examples {
    public static void main(String[] args) {
        // ---- 1. Operators cheat-run ----
        System.out.println(7 / 2);        // int / int -> 3 (decimals dropped!)
        System.out.println(7 / 2.0);      // 3.5
        System.out.println(7 % 2);        // remainder -> 1
        System.out.println(Math.pow(2, 3));   // there is no ** in Java -> 8.0
        System.out.println(2 + 3 * 4 * 4 + " " + (2 + 3) * 4);   // 50 and 20

        // ---- 2. Checkout: discount + GST ----
        double price = 2499;
        double discountPercent = 20;
        double gstPercent = 18;
        double discountAmount = price * discountPercent / 100;
        double afterDiscount = price - discountAmount;
        double gstAmount = afterDiscount * gstPercent / 100;
        double finalPrice = afterDiscount + gstAmount;
        System.out.printf("MRP: %.0f  |  Discount: %.2f  |  GST: %.2f  |  Pay: %.2f%n",
                price, discountAmount, gstAmount, finalPrice);

        // ---- 3. Even/odd and time conversion with % and / ----
        System.out.println("Is 18 even? " + (18 % 2 == 0));
        int totalMinutes = 125;
        int hours = totalMinutes / 60;
        int minutes = totalMinutes % 60;
        System.out.println(totalMinutes + " minutes = " + hours + "h " + minutes + "m");

        // ---- 4. Bank EMI formula ----
        double principal = 500_000;      // underscores make big numbers readable
        double annualRate = 9;           // percent
        int years = 5;
        double r = annualRate / 12 / 100;   // monthly rate
        int n = years * 12;                 // number of months
        double growth = Math.pow(1 + r, n);
        double emi = principal * r * growth / (growth - 1);
        System.out.printf("Monthly EMI: Rs. %.2f%n", emi);
        System.out.printf("Total paid:  Rs. %.2f  (interest = Rs. %.2f)%n", emi * n, emi * n - principal);

        // ---- 5. BMI ----
        int weightKg = 70;
        int heightCm = 175;
        double heightM = heightCm / 100.0;     // 100.0, not 100! (int / int would give 1)
        double bmi = weightKg / (heightM * heightM);
        System.out.printf("BMI = %.1f%n", bmi);

        // ---- 6. Casting: converting between number types ----
        int items = 7;
        int people = 2;
        System.out.println("Wrong share: " + items / people);               // 3
        System.out.println("Right share: " + (double) items / people);      // 3.5
        double pi = 3.99;
        System.out.println("(int) 3.99 = " + (int) pi + "   rounded = " + Math.round(pi));

        // ---- 7. The double gotcha + Math ----
        System.out.println(0.1 + 0.2);                       // 0.30000000000000004
        System.out.println(0.1 + 0.2 == 0.3);                // false
        System.out.println(Math.abs(0.1 + 0.2 - 0.3) < 1e-9);   // true: "close enough"
        System.out.println(Math.round(2.5) + " " + Math.round(3.5) + " " + Math.round(-2.5));
        System.out.println(Math.sqrt(16) + " " + Math.ceil(4.2) + " " + Math.floor(4.8));
        System.out.println(Math.max(4, 9) + " " + Math.min(4, 9) + " " + Math.abs(-250));
        System.out.println(Math.round(2.567 * 100) / 100.0);   // round to 2 decimals -> 2.57

        // ---- 8. BigDecimal: exact money ----
        BigDecimal a = new BigDecimal("0.1");
        BigDecimal b = new BigDecimal("0.2");
        System.out.println(a.add(b));                                        // 0.3
        System.out.println(new BigDecimal("19.99").multiply(BigDecimal.valueOf(3)));   // 59.97

        // ---- 9. Overflow: int has a ceiling ----
        int big = Integer.MAX_VALUE;
        System.out.println(big + " + 1 = " + (big + 1));      // wraps around to a negative number!
        long safe = (long) big + 1;
        System.out.println("as long: " + safe);

        // ---- 10. += and ++ shortcuts: a growing cart ----
        int cart = 0;
        cart += 499;
        cart += 1299;
        cart *= 2;
        cart++;
        System.out.println("Cart = " + cart);
    }
}
