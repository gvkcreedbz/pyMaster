import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * A tiny JSON reader/writer. The JDK ships none, and "no third-party libraries" is the rule of this blueprint.
 * Reader gives you Map / List / String / Long / Double / Boolean / null. Writer accepts the same, plus any Number.
 * Maps are LinkedHashMap, so key order (and therefore the output) is always deterministic.
 */
final class Json {
    private Json() {}

    /** Thrown for malformed input; the HTTP layer turns it into a 400. */
    static final class ParseException extends RuntimeException {
        ParseException(String message) {
            super(message);
        }
    }

    /** obj("a", 1, "b", "x") -> {"a":1,"b":"x"} in that order. */
    static Map<String, Object> obj(Object... keyValues) {
        Map<String, Object> m = new LinkedHashMap<>();
        for (int i = 0; i < keyValues.length; i += 2) {
            m.put((String) keyValues[i], keyValues[i + 1]);
        }
        return m;
    }

    // ---- writer ----------------------------------------------------------------------------------------------
    static String write(Object value) {
        StringBuilder sb = new StringBuilder();
        write(sb, value);
        return sb.toString();
    }

    private static void write(StringBuilder sb, Object v) {
        switch (v) {                                        // pattern matching for switch (Java 21)
            case null -> sb.append("null");
            case String s -> quote(sb, s);
            case Boolean b -> sb.append(b.booleanValue());
            case Number n -> sb.append(n);
            case Map<?, ?> m -> {
                sb.append('{');
                boolean first = true;
                for (Map.Entry<?, ?> e : m.entrySet()) {
                    if (!first) sb.append(',');
                    first = false;
                    quote(sb, String.valueOf(e.getKey()));
                    sb.append(':');
                    write(sb, e.getValue());
                }
                sb.append('}');
            }
            case Collection<?> c -> {
                sb.append('[');
                boolean first = true;
                for (Object item : c) {
                    if (!first) sb.append(',');
                    first = false;
                    write(sb, item);
                }
                sb.append(']');
            }
            default -> throw new IllegalArgumentException("cannot write " + v.getClass().getName() + " as JSON");
        }
    }

    private static void quote(StringBuilder sb, String s) {
        sb.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
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
        sb.append('"');
    }

    // ---- reader ----------------------------------------------------------------------------------------------
    static Object parse(String text) {
        Parser p = new Parser(text);
        Object v = p.value(0);
        p.ws();
        if (p.i != text.length()) throw p.fail("unexpected trailing characters");
        return v;
    }

    private static final class Parser {
        private final String s;
        private int i;

        Parser(String s) {
            this.s = s;
        }

        ParseException fail(String why) {
            return new ParseException(why + " at position " + i);
        }

        void ws() {
            while (i < s.length() && " \t\r\n".indexOf(s.charAt(i)) >= 0) i++;
        }

        boolean peek(char c) {
            return i < s.length() && s.charAt(i) == c;
        }

        void expect(char c) {
            if (!peek(c)) throw fail("expected '" + c + "'");
            i++;
        }

        Object value(int depth) {
            if (depth > 64) throw fail("nesting too deep");
            ws();
            if (i >= s.length()) throw fail("unexpected end of input");
            return switch (s.charAt(i)) {
                case '{' -> object(depth);
                case '[' -> array(depth);
                case '"' -> string();
                case 't' -> literal("true", Boolean.TRUE);
                case 'f' -> literal("false", Boolean.FALSE);
                case 'n' -> literal("null", null);
                default -> number();
            };
        }

        Object literal(String word, Object result) {
            if (!s.startsWith(word, i)) throw fail("unexpected character");
            i += word.length();
            return result;
        }

        Map<String, Object> object(int depth) {
            Map<String, Object> m = new LinkedHashMap<>();
            i++;                                            // skip {
            ws();
            if (peek('}')) {
                i++;
                return m;
            }
            while (true) {
                ws();
                if (!peek('"')) throw fail("expected a string key");
                String key = string();
                ws();
                expect(':');
                m.put(key, value(depth + 1));
                ws();
                if (peek(',')) {
                    i++;
                    continue;
                }
                expect('}');
                return m;
            }
        }

        List<Object> array(int depth) {
            List<Object> list = new ArrayList<>();
            i++;                                            // skip [
            ws();
            if (peek(']')) {
                i++;
                return list;
            }
            while (true) {
                list.add(value(depth + 1));
                ws();
                if (peek(',')) {
                    i++;
                    continue;
                }
                expect(']');
                return list;
            }
        }

        String string() {
            i++;                                            // skip opening quote
            StringBuilder sb = new StringBuilder();
            while (i < s.length()) {
                char c = s.charAt(i++);
                if (c == '"') return sb.toString();
                if (c < 0x20) throw fail("control character in string");
                if (c != '\\') {
                    sb.append(c);
                    continue;
                }
                if (i >= s.length()) break;
                char e = s.charAt(i++);
                switch (e) {
                    case '"', '\\', '/' -> sb.append(e);
                    case 'n' -> sb.append('\n');
                    case 'r' -> sb.append('\r');
                    case 't' -> sb.append('\t');
                    case 'b' -> sb.append('\b');
                    case 'f' -> sb.append('\f');
                    case 'u' -> {
                        if (i + 4 > s.length()) throw fail("bad unicode escape");
                        try {
                            sb.append((char) Integer.parseInt(s.substring(i, i + 4), 16));
                        } catch (NumberFormatException ex) {
                            throw fail("bad unicode escape");
                        }
                        i += 4;
                    }
                    default -> throw fail("bad escape");
                }
            }
            throw fail("unterminated string");
        }

        Object number() {
            int start = i;
            while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
            if (start == i) throw fail("unexpected character");
            String t = s.substring(start, i);
            try {
                boolean isDouble = t.indexOf('.') >= 0 || t.indexOf('e') >= 0 || t.indexOf('E') >= 0;
                return isDouble ? (Object) Double.parseDouble(t) : (Object) Long.parseLong(t);
            } catch (NumberFormatException ex) {
                i = start;
                throw fail("bad number");
            }
        }
    }
}
