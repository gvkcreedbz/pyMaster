/* Day 23 - Code along: cleaning a messy contact / invoice dump with regular expressions.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * The sample text is ../../datasets/contacts_messy.txt (open it next to this file).
 */
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
class Examples {
    // ---- Clean code: a named constant instead of a magic number, patterns compiled ONCE ----
    static final double GST_RATE = 0.18;
    private static final Pattern EMAIL = Pattern.compile("[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+");
    private static final Pattern DATE = Pattern.compile("(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})");
    // ---- Small methods, each with ONE job and a name that says what it does ----
    static List<String> findAll(Pattern pattern, String text) {
        Matcher matcher = pattern.matcher(text);
        List<String> found = new ArrayList<>();
        while (matcher.find()) {
            found.add(matcher.group());
        }
        return found;
    }
    static double priceWithGst(double price) {
        if (price < 0) {                                   // guard clause: reject bad input first
            throw new IllegalArgumentException("Price must not be negative");
        }
        return Math.round(price * (1 + GST_RATE) * 100) / 100.0;
    }
    // ---- Immutable: an object that can never change after it is built ----
    record Money(String currency, int paise) {
        Money plus(Money other) {
            return new Money(currency, paise + other.paise);       // a NEW object
        }
    }
    public static void main(String[] args) throws IOException {
        String text = Files.readString(Path.of("../../datasets/contacts_messy.txt"));
        // ---- 1. find(): every match in the text ----
        System.out.println("1. Emails");
        for (String email : findAll(EMAIL, text)) {
            System.out.println("  " + email);
        }
        // ---- 2. Groups: pick the parts out of one match ----
        System.out.println("2. Named groups");
        Matcher date = DATE.matcher("Order ORD1001 on 2026-11-03 for Rs. 899");
        if (date.find()) {
            System.out.println("  year=" + date.group("year") + " month=" + date.group("month") + " day=" + date.group("day"));
            System.out.println("  whole match: " + date.group() + " at position " + date.start());
        }
        // ---- 3. matches(): does the WHOLE text fit? (validation) ----
        System.out.println("3. Validation with matches()");
        for (String pin : new String[]{"560001", "060001", "56001"}) {
            System.out.println("  " + pin + " -> " + pin.matches("[1-9]\\d{5}"));
        }
        System.out.println("  find vs matches: " + Pattern.compile("\\d{3}").matcher("a123b").find()
                + " / " + Pattern.compile("\\d{3}").matcher("a123b").matches());
        // ---- 4. Replace and split ----
        System.out.println("4. replaceAll and split");
        System.out.println("  " + "Card 1234 5678 9012 3456 used".replaceAll("\\b(?:\\d{4}[ -]?){3}(\\d{4})\\b", "**** **** **** $1"));
        System.out.println("  " + "a1b22".replaceAll("\\d", "#"));
        System.out.println("  " + Arrays.toString("a, b;c".split("[,;]\\s*")));
        // ---- 5. Greedy versus lazy ----
        System.out.println("5. Greedy vs lazy");
        String html = "<b>chai</b> and <i>samosa</i>";
        System.out.println("  greedy <.+> : " + findAll(Pattern.compile("<.+>"), html));
        System.out.println("  lazy   <.+?>: " + findAll(Pattern.compile("<.+?>"), html));
        // ---- 6. Flags ----
        System.out.println("6. Ignoring capitals");
        System.out.println("  " + findAll(Pattern.compile("ord-?\\d+", Pattern.CASE_INSENSITIVE), text));
        // ---- 7. Clean code and immutability ----
        System.out.println("7. Clean code");
        System.out.println("  price with GST: " + priceWithGst(100));
        Money wallet = new Money("INR", 5000);
        Money bigger = wallet.plus(new Money("INR", 2550));
        System.out.println("  old wallet: " + wallet + "  new wallet: " + bigger);
        List<String> fixed = List.copyOf(new ArrayList<>(List.of("Chai", "Samosa")));
        try {
            fixed.add("Pizza");
        } catch (UnsupportedOperationException e) {
            System.out.println("  an unmodifiable list refuses changes: UnsupportedOperationException");
        }
    }
}
