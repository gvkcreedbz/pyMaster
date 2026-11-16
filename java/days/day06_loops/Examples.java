/* Day 06 - Code along: loops in action (tables, totals, patterns, a guessing game).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.Random;

class Examples {
    public static void main(String[] args) {
        // ---- 1. for loop: start; keep going while; step ----
        for (int i = 1; i <= 5; i++) {
            System.out.println("Round " + i);
        }
        for (int i = 10; i > 0; i -= 3) {         // countdown with a step of 3
            System.out.print(i + " ");
        }
        System.out.println();

        // ---- 2. Accumulator: cart total and average ----
        int[] prices = {499, 1299, 250, 899};      // a numbered row of values (Day 8 explains arrays)
        int total = 0;
        for (int p : prices) {                      // enhanced for: "for each p in prices"
            total += p;
        }
        System.out.println("Cart total: " + total + " | average: " + (double) total / prices.length);

        // ---- 3. Multiplication table ----
        int n = 7;
        for (int k = 1; k <= 10; k++) {
            System.out.printf("%d x %2d = %3d%n", n, k, n * k);
        }

        // ---- 4. break / continue ----
        for (int x = 1; x < 10; x++) {
            if (x == 3) {
                continue;                           // skip this round
            }
            if (x == 6) {
                break;                              // leave the loop completely
            }
            System.out.print(x + " ");
        }
        System.out.println();

        // ---- 5. Looping over text ----
        int vowels = 0;
        for (char ch : "Education".toLowerCase().toCharArray()) {
            if ("aeiou".indexOf(ch) >= 0) {
                vowels++;
            }
        }
        System.out.println("Vowels in Education: " + vowels);
        for (String word : "red green blue".split(" ")) {
            System.out.println(word.toUpperCase());
        }

        // ---- 6. Patterns with nested loops ----
        for (int row = 1; row <= 4; row++) {
            System.out.println("*".repeat(row));
        }
        for (int row = 1; row <= 3; row++) {
            for (int col = 1; col <= 3; col++) {
                System.out.print(row * col + " ");
            }
            System.out.println();                    // new line after each row
        }

        // ---- 7. while: a guessing game (computer picks 1-20, you get 5 tries) ----
        Random random = new Random(2026);            // same seed = same "random" numbers every run
        int secret = random.nextInt(20) + 1;         // nextInt(20) is 0..19, so +1 gives 1..20
        int[] guesses = {10, 15, 18, 20, 3};    // pretend the player typed these
        int attempts = 0;
        boolean won = false;
        while (attempts < 5 && !won) {
            int guess = guesses[attempts];
            attempts++;
            if (guess == secret) {
                System.out.println("Correct! You needed " + attempts + " attempt(s).");
                won = true;
            } else {
                System.out.println(guess + (guess > secret ? " is too high" : " is too low"));
            }
        }
        if (!won) {
            System.out.println("Out of attempts. The number was " + secret);
        }

        // ---- 8. do / while: runs at least once ----
        int countdown = 3;
        do {
            System.out.println("Launch in " + countdown);
            countdown--;
        } while (countdown > 0);

        // ---- 9. "Keep asking until valid" pattern: while (true) + break ----
        int pin = 0;
        while (true) {
            pin += 1111;                             // pretend the user typed 1111, 2222, ...
            if (pin == 3333) {
                System.out.println("PIN accepted: " + pin);
                break;
            }
        }
    }
}
