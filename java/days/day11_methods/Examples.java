/* Day 11 - Code along: a small billing service built from methods.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Examples {

    // ---- 1. Define: modifiers, return type, name, (parameters) ----
    static String greet(String name) {                     // name = parameter
        return "Hello, " + name + "!";
    }

    // ---- 2. return vs print: void methods give nothing back ----
    static int add(int a, int b) {
        return a + b;
    }

    static void printLine(String text) {                   // void = returns nothing
        System.out.println(">> " + text);
    }

    // ---- 3. Overloading: same name, different parameters (Java has no default values) ----
    static String greet(String name, String greeting) {
        return greeting + ", " + name + "!";
    }

    static double total(double price) {
        return total(price, 1);                            // a method can call its sibling
    }

    static double total(double price, int qty) {
        return total(price, qty, 18);
    }

    static double total(double price, int qty, int taxPercent) {
        return price * qty * (1 + taxPercent / 100.0);
    }

    // ---- 4. Varargs: any number of arguments (inside, it is an array) ----
    static double average(int... numbers) {
        if (numbers.length == 0) {
            return 0;
        }
        int sum = 0;
        for (int n : numbers) {
            sum += n;
        }
        return (double) sum / numbers.length;
    }

    // ---- 5. Several results? Return an array (records come on Day 13) ----
    static int[] minAndMax(int[] numbers) {
        int min = numbers[0];
        int max = numbers[0];
        for (int n : numbers) {
            if (n < min) {
                min = n;
            }
            if (n > max) {
                max = n;
            }
        }
        return new int[]{min, max};
    }

    // ---- 6. Scope and pass-by-value ----
    static void tryToChange(int price, int[] prices) {
        price = 999;                                       // changes only the method's own copy
        prices[0] = 999;                                   // changes the array the caller also sees
    }

    // ---- 7. Recursion: a method that calls itself ----
    static long factorial(int n) {
        if (n <= 1) {                                      // base case: stops the recursion
            return 1;
        }
        return n * factorial(n - 1);                       // a smaller problem
    }

    static int fib(int n) {
        if (n < 2) {
            return n;
        }
        return fib(n - 1) + fib(n - 2);
    }

    static int forever(int n) {                            // no base case: do not do this
        return forever(n + 1) + 1;
    }

    // ---- 8. Good habits: one job, a verb name, return results instead of printing ----
    static boolean isAdult(int age) {
        return age >= 18;
    }

    public static void main(String[] args) {
        System.out.println(greet("Aarav"));                         // Hello, Aarav!
        System.out.println(greet("Diya", "Namaste"));               // Namaste, Diya!

        int sum = add(2, 3) * 10;                                   // 50: a returned value can be used
        System.out.println(sum);
        printLine("done");                                          // >> done
        // int x = printLine("a");                                  // compile error: void gives no value

        System.out.println(total(100));                             // 118.0
        System.out.println(total(100, 3));                          // 354.0
        System.out.println(total(100, 3, 5));                       // 315.0
        System.out.println(average(4, 8, 6) + " " + average(5) + " " + average());   // 6.0 5.0 0.0
        System.out.println(average(new int[]{1, 2}));               // an array works for varargs too: 1.5

        int[] range = minAndMax(new int[]{4, 8, 6, 2});
        System.out.println("low " + range[0] + ", high " + range[1]);   // low 2, high 8

        int price = 100;
        int[] prices = {100, 200};
        tryToChange(price, prices);
        System.out.println(price + " " + Arrays.toString(prices));  // 100 [999, 200]

        {
            int inner = 5;                                          // lives only inside these braces
            System.out.println(inner);
        }
        // System.out.println(inner);                               // compile error: cannot find symbol
        for (int i = 0; i < 2; i++) {
            System.out.println("loop " + i);                        // i exists only inside the loop
        }

        System.out.println(factorial(5) + " " + fib(7));            // 120 13
        try {
            forever(1);
        } catch (StackOverflowError e) {
            System.out.println("StackOverflowError: a recursion without a base case never stops");
        }

        List<String> log = new ArrayList<>();
        log.add(isAdult(20) ? "20 is an adult" : "20 is a minor");
        log.add(isAdult(15) ? "15 is an adult" : "15 is a minor");
        System.out.println(log);
    }
}
