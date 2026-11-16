import java.time.Duration;

/**
 * One thing to watch. A record: immutable, with equals/hashCode/toString for free (Day 20).
 * The Python version used a plain dict; here the compact constructor validates once, at the edge.
 *
 * @param kind        the plugin name looked up in {@link Checks} ("price", "content", "uptime", ...)
 * @param pattern     regex with ONE group (only the "price" kind needs it, others pass null)
 * @param every       how often this target is due
 * @param minDropPct  a price must fall at least this many percent to raise an alert
 */
public record Target(String name, String kind, String url, String pattern, Duration every, double minDropPct) {

    public Target {
        if (name == null || name.isBlank()) throw new IllegalArgumentException("name is required");
        if (kind == null || kind.isBlank()) throw new IllegalArgumentException("kind is required");
        if (every == null || every.isZero() || every.isNegative()) throw new IllegalArgumentException("every must be positive");
    }

    public static Target price(String name, String url, String pattern, Duration every, double minDropPct) {
        return new Target(name, "price", url, pattern, every, minDropPct);
    }

    public static Target content(String name, String url, Duration every) {
        return new Target(name, "content", url, null, every, 0);
    }

    public static Target uptime(String name, String url, Duration every) {
        return new Target(name, "uptime", url, null, every, 0);
    }

    /** Records are immutable, so "change one field" means "make a modified copy" (Python: {**t, "pattern": ...}). */
    public Target withPattern(String newPattern) {
        return new Target(name, kind, url, newPattern, every, minDropPct);
    }
}
