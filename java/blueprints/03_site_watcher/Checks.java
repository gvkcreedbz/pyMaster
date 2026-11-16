import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 1. PLUGIN REGISTRY. A static map from a name to a {@link Check}. The engine only ever says
 * {@code Checks.lookup(kind).run(target, fetch)}, so a new kind of check never touches the engine.
 *
 * <p>Python used a decorator ({@code @check("price")}). Java has no function decorators; the closest
 * equivalents are (a) this explicit {@code register(name, methodReference)} call, or (b) a custom annotation
 * scanned by reflection or {@code ServiceLoader}. The explicit call is greppable and needs no magic.
 */
public final class Checks {

    private static final Map<String, Check> REGISTRY = new ConcurrentHashMap<>();

    static {                                                     // built-in plugins
        register("price", Checks::price);
        register("content", Checks::content);
        register("uptime", Checks::uptime);
    }

    private Checks() { }                                         // utility class: no instances

    /** Add (or replace) a plugin. Anyone can call this at start-up: tests, extensions, your own code. */
    public static void register(String kind, Check check) {
        REGISTRY.put(kind, check);
    }

    public static Check lookup(String kind) {
        Check c = REGISTRY.get(kind);
        if (c == null) throw new IllegalArgumentException("unknown check kind: " + kind);
        return c;
    }

    /** Sorted, so the demo output is deterministic (a ConcurrentHashMap has no stable order). */
    public static List<String> kinds() {
        return REGISTRY.keySet().stream().sorted().toList();
    }

    /** Thrown when the page no longer looks the way we expect: better a loud error than a wrong price. */
    public static final class LayoutChangedException extends RuntimeException {
        private static final long serialVersionUID = 1L;

        public LayoutChangedException(String message) {
            super(message);
        }
    }

    // ---- the built-in plugins -------------------------------------------------------------------------------------

    /** Return the number found by the regex ("Price: $1,299.00" gives 1299.0). */
    static Reading price(Target t, Fetcher fetch) throws Exception {
        String html = fetch.fetch(t.url());
        Matcher m = Pattern.compile(t.pattern()).matcher(html);
        if (!m.find()) throw new LayoutChangedException("price pattern not found: the site layout probably changed");
        return new Reading.Price(Double.parseDouble(m.group(1).replace(",", "")));
    }

    /** Return a fingerprint of the page: any change in the text changes the hash. */
    static Reading content(Target t, Fetcher fetch) throws Exception {
        String html = fetch.fetch(t.url()).replaceAll("\\s+", " ");
        MessageDigest sha = MessageDigest.getInstance("SHA-256");   // checked exception, but every JDK has SHA-256
        byte[] digest = sha.digest(html.getBytes(StandardCharsets.UTF_8));
        return new Reading.Text(HexFormat.of().formatHex(digest).substring(0, 12));
    }

    /** Success is "the call did not throw". Timeouts and 5xx become exceptions inside the Fetcher. */
    static Reading uptime(Target t, Fetcher fetch) throws Exception {
        fetch.fetch(t.url());
        return new Reading.Text("up");
    }
}
