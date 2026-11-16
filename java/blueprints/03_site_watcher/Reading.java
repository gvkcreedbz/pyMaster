/**
 * What a check returns. A SEALED interface lists every possible answer, so a {@code switch} over it needs no
 * default branch and the compiler tells you when you forget a case (Day 20).
 * Python returned "a float or a str"; Java makes the two shapes explicit.
 */
public sealed interface Reading permits Reading.Price, Reading.Text {

    /** Human-friendly form used in alerts and on the dashboard. */
    String display();

    /** A number found on the page, e.g. 1299.0. */
    record Price(double value) implements Reading {
        @Override public String display() {
            return Double.toString(value);
        }
    }

    /** A fingerprint ("a3f9...") or a status word ("up"). */
    record Text(String value) implements Reading {
        @Override public String display() {
            return value;
        }
    }
}
