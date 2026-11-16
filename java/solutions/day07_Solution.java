// SOLUTION FILE - try the hint ladder first!
/* Day 07 - Week 1 Project: Mini ATM + Guessing Game.
 *
 * Run the checks:   java Practice.java
 * Play your ATM:    java Practice.java play
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
import java.util.Locale;
import java.util.Scanner;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | deposit   (Level 1 - Beginner)
    // Return the new balance after depositing amount. A deposit of 0 or less is
    // invalid: return the balance unchanged.   deposit(1000, 500) -> 1500
    // ---------------------------------------------------------------------------
    static int deposit(int balance, int amount) {
        // >>> SOLUTION stub: return 0;
        if (amount <= 0) {
            return balance;
        }
        return balance + amount;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | formatBalance   (Level 1 - Beginner)
    // Return text like  "Balance: Rs. 10,300.00"  (comma between thousands, exactly
    // 2 decimals). Hint: String.format(Locale.US, "... %,.2f", balance)
    // ---------------------------------------------------------------------------
    static String formatBalance(double balance) {
        // >>> SOLUTION stub: return null;
        return String.format(Locale.US, "Balance: Rs. %,.2f", balance);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | guessFeedback   (Level 1 - Beginner)
    // Return "Too high", "Too low" or "Correct!" by comparing guess with secret.
    // ---------------------------------------------------------------------------
    static String guessFeedback(int secret, int guess) {
        // >>> SOLUTION stub: return null;
        if (guess > secret) {
            return "Too high";
        } else if (guess < secret) {
            return "Too low";
        }
        return "Correct!";
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | validateWithdrawal   (Level 2 - Intermediate)
    // Check IN THIS ORDER and return the first problem found:
    //   amount <= 0 or not a multiple of 100 -> "Invalid amount"
    //   amount > balance                      -> "Insufficient balance"
    //   withdrawnToday + amount > 20000       -> "Daily limit exceeded"
    // Otherwise return "OK".
    // ---------------------------------------------------------------------------
    static String validateWithdrawal(int balance, int amount, int withdrawnToday) {
        // >>> SOLUTION stub: return null;
        if (amount <= 0 || amount % 100 != 0) {
            return "Invalid amount";
        }
        if (amount > balance) {
            return "Insufficient balance";
        }
        if (withdrawnToday + amount > 20000) {
            return "Daily limit exceeded";
        }
        return "OK";
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | playGuessingGame   (Level 2 - Intermediate)
    // guessesText holds the player's guesses separated by commas ("10,15,12").
    // The player gets at most 5 guesses. Return the attempt number on which the
    // secret was guessed, or -1 if it was not guessed within 5 attempts.
    //   playGuessingGame(12, "10,15,12")      -> 3
    //   playGuessingGame(12, "1,2,3,4,5,12")  -> -1   (the 6th guess is too late)
    // Hint: text.split(",") gives a String[]; Integer.parseInt(...) turns text into a number.
    // ---------------------------------------------------------------------------
    static int playGuessingGame(int secret, String guessesText) {
        // >>> SOLUTION stub: return 0;
        String[] parts = guessesText.split(",");
        int attempt = 0;
        for (String part : parts) {
            attempt++;
            if (attempt > 5) {
                break;
            }
            if (Integer.parseInt(part.trim()) == secret) {
                return attempt;
            }
        }
        return -1;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | runAtm   (Level 3 - Challenge)  -> the full interactive program
    // Create ONE Scanner on System.in at the top and read every answer with nextLine().
    // 1. PIN: print "Enter PIN: " (print, not println) and read a line, up to 3 times.
    //    Wrong -> println "Wrong PIN". After 3 wrong tries println "Card blocked" and
    //    return the starting balance.   (Compare text with .equals, never ==)
    // 2. Menu loop. Each round println:  1) Balance  2) Deposit  3) Withdraw  4) Exit
    //    then print "Choose: " and read the choice.
    //    "1": println(formatBalance(balance))
    //    "2": print "Amount to deposit: ", read a number; use deposit();
    //         if the balance changed println "Deposited Rs. 500" (with the amount) else "Invalid amount"
    //    "3": print "Amount to withdraw: ", read a number; reason = validateWithdrawal(...)
    //         "OK" -> subtract, add to withdrawnToday, println "Collect your cash: Rs. 200"
    //         otherwise println the reason
    //    "4": println "Thank you!" and return the final balance
    //    anything else: println "Invalid option"
    // ---------------------------------------------------------------------------
    static int runAtm(int startingBalance, String correctPin) {
        // >>> SOLUTION stub: return 0;
        Scanner in = new Scanner(System.in);
        int balance = startingBalance;
        int withdrawnToday = 0;

        boolean pinOk = false;
        int attempts = 0;
        while (attempts < 3 && !pinOk) {
            System.out.print("Enter PIN: ");
            if (in.nextLine().trim().equals(correctPin)) {
                pinOk = true;
            } else {
                attempts++;
                System.out.println("Wrong PIN");
            }
        }
        if (!pinOk) {
            System.out.println("Card blocked");
            return balance;
        }

        while (true) {
            System.out.println("1) Balance  2) Deposit  3) Withdraw  4) Exit");
            System.out.print("Choose: ");
            String choice = in.nextLine().trim();
            switch (choice) {
                case "1" -> System.out.println(formatBalance(balance));
                case "2" -> {
                    System.out.print("Amount to deposit: ");
                    int amount = Integer.parseInt(in.nextLine().trim());
                    int newBalance = deposit(balance, amount);
                    if (newBalance == balance) {
                        System.out.println("Invalid amount");
                    } else {
                        balance = newBalance;
                        System.out.println("Deposited Rs. " + amount);
                    }
                }
                case "3" -> {
                    System.out.print("Amount to withdraw: ");
                    int amount = Integer.parseInt(in.nextLine().trim());
                    String reason = validateWithdrawal(balance, amount, withdrawnToday);
                    if (reason.equals("OK")) {
                        balance -= amount;
                        withdrawnToday += amount;
                        System.out.println("Collect your cash: Rs. " + amount);
                    } else {
                        System.out.println(reason);
                    }
                }
                case "4" -> {
                    System.out.println("Thank you!");
                    return balance;
                }
                default -> System.out.println("Invalid option");
            }
        }
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    /** Run runAtm with fake keyboard input; return {final balance, everything it printed}. */
    private static Object[] session(String keys, int startingBalance, String pin) {
        int[] result = new int[1];
        String shown = Checker.withInput(keys, () -> Checker.printed(() -> result[0] = runAtm(startingBalance, pin)));
        return new Object[]{result[0], shown};
    }

    private static int count(String text, String piece) {
        int n = 0;
        for (int at = text.indexOf(piece); at >= 0; at = text.indexOf(piece, at + 1)) {
            n++;
        }
        return n;
    }

    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("play")) {
            runAtm(10000, "1234");
            return;
        }
        System.out.println("--- Day 07 checks ---");
        Checker.check("L1-1 deposit 500", () -> deposit(1000, 500), 1500);
        Checker.check("L1-1 deposit 0 is ignored", () -> deposit(1000, 0), 1000);
        Checker.check("L1-1 deposit negative is ignored", () -> deposit(1000, -5), 1000);
        Checker.check("L1-2 formatBalance", () -> formatBalance(10300), "Balance: Rs. 10,300.00");
        Checker.check("L1-2 formatBalance #2", () -> formatBalance(99.5), "Balance: Rs. 99.50");
        Checker.check("L1-2 formatBalance #3", () -> formatBalance(1234567), "Balance: Rs. 1,234,567.00");
        Checker.check("L1-3 guessFeedback", () -> new String[]{guessFeedback(10, 15), guessFeedback(10, 5), guessFeedback(10, 10)},
                new String[]{"Too high", "Too low", "Correct!"});
        Checker.check("L2-1 validateWithdrawal", () -> new String[]{
                        validateWithdrawal(5000, 0, 0), validateWithdrawal(5000, 250, 0), validateWithdrawal(5000, 6000, 0),
                        validateWithdrawal(50000, 6000, 15000), validateWithdrawal(5000, 500, 0)},
                new String[]{"Invalid amount", "Invalid amount", "Insufficient balance", "Daily limit exceeded", "OK"});
        Checker.check("L2-2 guessing game win", () -> playGuessingGame(12, "10,15,12"), 3);
        Checker.check("L2-2 guessing game too late", () -> playGuessingGame(12, "1,2,3,4,5,12"), -1);
        Checker.check("L2-2 guessing game 5th try", () -> playGuessingGame(7, "1,2,3,4,7"), 5);
        Checker.check("L2-2 guessing game with spaces", () -> playGuessingGame(7, "3, 7"), 2);

        Object[] happy = session("1234\n2\n500\n3\n200\n1\n4\n", 10000, "1234");
        Checker.check("L3-1 ATM happy path balance", () -> happy[0], 10300);
        Checker.check("L3-1 ATM shows balance line", () -> ((String) happy[1]).contains("Balance: Rs. 10,300.00"), true);
        Checker.check("L3-1 ATM messages", () -> {
            String out = (String) happy[1];
            return out.contains("Deposited Rs. 500") && out.contains("Collect your cash: Rs. 200") && out.contains("Thank you!");
        }, true);
        Checker.check("L3-1 ATM prompts", () -> {
            String out = (String) happy[1];
            return out.contains("Enter PIN: ") && out.contains("Choose: ") && out.contains("1) Balance  2) Deposit  3) Withdraw  4) Exit");
        }, true);

        Object[] blocked = session("1\n2\n3\n", 10000, "1234");
        Checker.check("L3-1 ATM blocks card after 3 wrong PINs", () -> blocked[0], 10000);
        Checker.check("L3-1 ATM says Wrong PIN 3 times then Card blocked", () -> {
            String out = (String) blocked[1];
            return count(out, "Wrong PIN") == 3 && out.contains("Card blocked") && !out.contains("Choose: ");
        }, true);

        Object[] lateOk = session("9\n1234\n4\n", 500, "1234");
        Checker.check("L3-1 ATM accepts the right PIN on the 2nd try", () -> lateOk[0] + "/" + count((String) lateOk[1], "Wrong PIN"), "500/1");

        Object[] refusals = session("9\n1234\n3\n20000\n3\n300\n3\n250\n7\n4\n", 10000, "1234");
        Checker.check("L3-1 ATM refusals", () -> {
            String out = (String) refusals[1];
            return refusals[0] + " " + out.contains("Insufficient balance") + " " + out.contains("Invalid amount")
                    + " " + out.contains("Invalid option");
        }, "9700 true true true");

        Object[] badDeposit = session("1234\n2\n-50\n4\n", 800, "1234");
        Checker.check("L3-1 ATM refuses a negative deposit", () -> badDeposit[0] + " " + ((String) badDeposit[1]).contains("Invalid amount"),
                "800 true");

        Object[] limit = session("1234\n3\n15000\n3\n6000\n4\n", 50000, "1234");
        Checker.check("L3-1 ATM daily limit", () -> limit[0] + " " + ((String) limit[1]).contains("Daily limit exceeded"),
                "35000 true");
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
