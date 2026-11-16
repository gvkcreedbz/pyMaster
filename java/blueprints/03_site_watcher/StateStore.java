import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AccessDeniedException;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

/**
 * 4. ATOMIC STATE FILE: a crash in the middle of a write must never corrupt what we remember.
 *
 * <p>Recipe: write a temporary file in the SAME folder, then {@code Files.move(tmp, target, ATOMIC_MOVE)}.
 * Readers see the old file or the new one, never half of each. The JSON is hand-written (the JDK has no JSON
 * library), which is fine for a flat object of numbers and strings: {@code {"laptop": 1099.0, "docs": "a3f9c1"}}.
 */
public final class StateStore {

    private static final int ATTEMPTS = 8;

    private StateStore() { }

    // ---- save -----------------------------------------------------------------------------------------------------

    public static void save(Path path, Map<String, Reading> state) throws IOException {
        Path dir = path.toAbsolutePath().getParent();
        Path tmp = Files.createTempFile(dir, "state-", ".tmp");
        try {
            Files.writeString(tmp, toJson(state), StandardCharsets.UTF_8);
            moveWithRetry(tmp, path);
        } finally {
            Files.deleteIfExists(tmp);                // only still there if the move failed
        }
    }

    /**
     * Windows wrinkle: an antivirus scanner or the search indexer may hold the target for a few milliseconds, and
     * the move then fails with AccessDeniedException. Retry with growing pauses (8 tries, 20 ms, 40 ms, ...).
     * Linux and macOS never need it; code that must run on both does.
     */
    private static void moveWithRetry(Path tmp, Path target) throws IOException {
        for (int attempt = 1; ; attempt++) {
            try {
                try {
                    Files.move(tmp, target, StandardCopyOption.ATOMIC_MOVE);
                } catch (AtomicMoveNotSupportedException e) {
                    Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING);   // exotic file system: best effort
                }
                return;
            } catch (AccessDeniedException e) {
                if (attempt == ATTEMPTS) throw e;
                pause(20L * attempt);
            }
        }
    }

    private static void pause(long millis) throws IOException {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();       // never swallow an interrupt: restore the flag
            throw new IOException("interrupted while retrying the state file swap", e);
        }
    }

    // ---- load -----------------------------------------------------------------------------------------------------

    /** Missing or corrupt file means "start from scratch"; a watcher that cannot start is worse than one that forgot. */
    public static Map<String, Reading> load(Path path) {
        try {
            return new Parser(Files.readString(path, StandardCharsets.UTF_8)).parseObject();
        } catch (IOException | IllegalArgumentException e) {
            return new LinkedHashMap<>();
        }
    }

    // ---- tiny JSON writer -----------------------------------------------------------------------------------------

    static String toJson(Map<String, Reading> state) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Reading> e : new TreeMap<>(state).entrySet()) {     // sorted keys: stable files
            sb.append(first ? "\n  " : ",\n  ");
            first = false;
            sb.append(quote(e.getKey())).append(": ");
            switch (e.getValue()) {                                                // sealed: no default needed
                case Reading.Price p -> sb.append(p.value());
                case Reading.Text t -> sb.append(quote(t.value()));
            }
        }
        return sb.append(first ? "}" : "\n}").toString();
    }

    private static String quote(String s) {
        StringBuilder sb = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
                }
            }
        }
        return sb.append('"').toString();
    }

    // ---- tiny JSON reader: a flat object whose values are numbers or strings --------------------------------------

    private static final class Parser {
        private final String s;
        private int i;

        Parser(String s) {
            this.s = s;
        }

        Map<String, Reading> parseObject() {
            Map<String, Reading> out = new LinkedHashMap<>();
            skipSpaces();
            expect('{');
            skipSpaces();
            if (peek() == '}') {
                i++;
            } else {
                while (true) {
                    skipSpaces();
                    String key = parseString();
                    skipSpaces();
                    expect(':');
                    skipSpaces();
                    out.put(key, peek() == '"' ? new Reading.Text(parseString()) : new Reading.Price(parseNumber()));
                    skipSpaces();
                    if (peek() == ',') { i++; continue; }
                    expect('}');
                    break;
                }
            }
            skipSpaces();
            if (i != s.length()) throw new IllegalArgumentException("trailing characters");
            return out;
        }

        private String parseString() {
            expect('"');
            StringBuilder sb = new StringBuilder();
            while (true) {
                if (i >= s.length()) throw new IllegalArgumentException("unterminated string");
                char c = s.charAt(i++);
                if (c == '"') return sb.toString();
                if (c != '\\') { sb.append(c); continue; }
                if (i >= s.length()) throw new IllegalArgumentException("bad escape");
                char e = s.charAt(i++);
                switch (e) {
                    case '"', '\\', '/' -> sb.append(e);
                    case 'n' -> sb.append('\n');
                    case 'r' -> sb.append('\r');
                    case 't' -> sb.append('\t');
                    case 'b' -> sb.append('\b');
                    case 'f' -> sb.append('\f');
                    case 'u' -> {
                        if (i + 4 > s.length()) throw new IllegalArgumentException("bad unicode escape");
                        sb.append((char) Integer.parseInt(s.substring(i, i + 4), 16));   // NumberFormatException is an IllegalArgumentException
                        i += 4;
                    }
                    default -> throw new IllegalArgumentException("bad escape \\" + e);
                }
            }
        }

        private double parseNumber() {
            int start = i;
            while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
            if (start == i) throw new IllegalArgumentException("number expected at " + i);
            return Double.parseDouble(s.substring(start, i));
        }

        private char peek() {
            return i < s.length() ? s.charAt(i) : '\0';
        }

        private void expect(char c) {
            if (peek() != c) throw new IllegalArgumentException("expected '" + c + "' at " + i);
            i++;
        }

        private void skipSpaces() {
            while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++;
        }
    }
}
