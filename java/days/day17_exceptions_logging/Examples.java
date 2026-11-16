/* Day 17 - Code along: a payment service that never just crashes.
 *
 * Type each section yourself, run it (java Examples.java), then break things on purpose and re-run.
 */
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.logging.Formatter;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.StreamHandler;

class Examples {

    // ---- 4. A custom exception: a clear name for a clear problem ----
    static class InsufficientFundsException extends Exception {
        InsufficientFundsException(String message) {
            super(message);
        }
    }

    // ---- 5. A resource that must always be closed ----
    static class Printer implements AutoCloseable {
        Printer() {
            System.out.println("  printer: on");
        }

        void print(String text) {
            System.out.println("  printer: " + text);
        }

        @Override
        public void close() {
            System.out.println("  printer: off");
        }
    }

    static int parseAmount(String text) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException e) {
            System.out.println("  '" + text + "' is not a whole number");
            return 0;
        } finally {
            System.out.println("  (finished parsing '" + text + "')");   // ALWAYS runs
        }
    }

    static int withdraw(int balance, int amount) throws InsufficientFundsException {
        if (amount > balance) {
            throw new InsufficientFundsException("Need Rs. " + (amount - balance) + " more");
        }
        return balance - amount;
    }

    static int setAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative");
        }
        return age;
    }

    static String firstLine(Path path) {
        try {
            var lines = Files.readAllLines(path);          // may throw IOException (checked!)
            return lines.isEmpty() ? "(empty)" : lines.get(0);
        } catch (IOException e) {
            return "(cannot read: " + e.getClass().getSimpleName() + ")";
        }
    }

    public static void main(String[] args) throws Exception {
        // ---- 1. try / catch / finally ----
        System.out.println("== 1. try / catch / finally ==");
        System.out.println(parseAmount("250"));
        System.out.println(parseAmount("two hundred"));

        // ---- 2. Different problems, different exception types ----
        System.out.println("== 2. Common exceptions ==");
        try {
            int[] cart = new int[3];
            cart[5] = 1;
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("  " + e.getMessage());
        }
        try {
            String coupon = null;
            System.out.println(coupon.length());
        } catch (NullPointerException e) {
            System.out.println("  null has no length");
        }
        try {
            System.out.println(10 / (3 - 3));
        } catch (ArithmeticException e) {
            System.out.println("  " + e.getMessage());
        }

        // ---- 3. Checked exceptions: the compiler forces you to deal with them ----
        System.out.println("== 3. Checked exceptions ==");
        System.out.println(firstLine(Path.of("no-such-file.txt")));
        Path temp = Files.createTempFile("day17", ".txt");
        Files.writeString(temp, "Order #1001\nOrder #1002\n");
        System.out.println(firstLine(temp));
        Files.deleteIfExists(temp);

        // ---- 4. Throwing your own ----
        System.out.println("== 4. throw ==");
        try {
            System.out.println(setAge(30));
            System.out.println(setAge(-1));
        } catch (IllegalArgumentException e) {
            System.out.println("  rejected: " + e.getMessage());
        }
        try {
            System.out.println(withdraw(1000, 400));
            System.out.println(withdraw(100, 600));
        } catch (InsufficientFundsException e) {
            System.out.println("  " + e.getClass().getSimpleName() + ": " + e.getMessage());
        }

        // multi-catch: one handler for two exception types
        try {
            Object text = "abc";
            Integer wrong = (Integer) text;
        } catch (ClassCastException | NumberFormatException e) {
            System.out.println("  wrong type or format");
        }

        // ---- 5. try-with-resources ----
        System.out.println("== 5. try-with-resources ==");
        try (Printer p = new Printer()) {
            p.print("Receipt #1");
            throw new IllegalStateException("paper jam");
        } catch (IllegalStateException e) {
            System.out.println("  caught: " + e.getMessage());   // the printer was already switched off
        }

        // ---- 6. Logging into memory so we can look at it ----
        System.out.println("== 6. java.util.logging ==");
        ByteArrayOutputStream sink = new ByteArrayOutputStream();
        StreamHandler handler = new StreamHandler(sink, new Formatter() {
            @Override
            public String format(LogRecord record) {
                return record.getLevel() + " - " + formatMessage(record) + "\n";
            }
        });
        Logger log = Logger.getLogger("shop");
        log.setUseParentHandlers(false);       // do not also print to the console
        log.setLevel(Level.INFO);              // FINE and below are hidden
        log.addHandler(handler);

        log.info("order placed");
        log.fine("details for developers");     // hidden
        log.warning("disk almost full");
        log.log(Level.SEVERE, "payment failed for order {0}", "#1001");
        handler.flush();                        // StreamHandler keeps text in a buffer until you flush
        System.out.print(sink.toString());
    }
}
