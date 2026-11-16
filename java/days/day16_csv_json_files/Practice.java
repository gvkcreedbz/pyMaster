/* Day 16 - Practice: CSV and JSON files.
 *
 * Run:  java Practice.java
 * Sales file columns: order_id, order_date, region, category, product, quantity,
 * unit_price, discount_pct, payment_method.
 * revenue of a row = quantity * unit_price * (1 - discount_pct / 100.0)
 * The checks write only into a temporary folder that is deleted at the end.
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Practice {

    // The answer shape for L2-3.
    record Ranked(String name, double average) {}

    // Helper (already written for you): round to 2 decimal places.
    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    // ---------------------------------------------------------------------------
    // L1-1 | readCsvRows   (Level 1 - Beginner)
    // Return the CSV file as a List of rows. Each row is a Map from column name (taken from
    // the first line) to the cell text. All values stay TEXT. Skip blank lines.
    // Hint: Files.readAllLines, line.split(",", -1)  (the -1 keeps empty cells at the end)
    // ---------------------------------------------------------------------------
    static List<Map<String, String>> readCsvRows(Path path) throws IOException {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | revenue of a row, total revenue   (Level 1 - Beginner)
    // revenueOf(row): quantity * unit_price * (1 - discount_pct / 100.0) for ONE row from
    //   readCsvRows (convert the text with Integer.parseInt first!).
    // totalRevenue(path): the total revenue of a sales CSV, rounded to 2 decimals (round2).
    // ---------------------------------------------------------------------------
    static double revenueOf(Map<String, String> row) {
        // TODO: write your code here
        return -1;
    }

    static double totalRevenue(Path path) throws IOException {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | JSON save and load   (Level 1 - Beginner)
    // A ready-made reader/writer called Json is at the bottom of this class (read it AFTER
    // you finish: it is the Day 13 writer plus a small reader).
    // saveJson(path, data): write Json.write(data) to the file as UTF-8 text.
    // loadJson(path, defaultValue): return Json.parse(<file text>); return defaultValue
    //   if the file does not exist.
    // ---------------------------------------------------------------------------
    static void saveJson(Path path, Object data) throws IOException {
        // TODO: write your code here
    }

    static Object loadJson(Path path, Object defaultValue) throws IOException {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | revenueByRegion   (Level 2 - Intermediate)
    // Return a Map region -> revenue (rounded to 2 decimals) for a sales CSV.
    //   e.g. {East=335268.6, North=300446.25, ...} for datasets/sales.csv
    // Hint: map.merge(region, revenueOf(row), Double::sum), round each total at the END.
    // ---------------------------------------------------------------------------
    static Map<String, Double> revenueByRegion(Path path) throws IOException {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-2 | writeCsv   (Level 2 - Intermediate)
    // Write rows to a CSV file: first line = the column names joined with commas, then one
    // line per row with the values in `columns` order (use String.valueOf(value)).
    // Every line ends with a new line. If a value contains a comma or a double quote, wrap
    // it in double quotes and double any inner quote:  x,y  ->  "x,y"   say "hi" -> "say ""hi"""
    //   writeCsv(path, [{a=1, b=x}, {a=2, b=y}], ["a", "b"]) writes   a,b / 1,x / 2,y
    // ---------------------------------------------------------------------------
    static void writeCsv(Path path, List<Map<String, Object>> rows, List<String> columns) throws IOException {
        // TODO: write your code here
    }

    // Used by the solution of L2-2 only; you may write your own version inside writeCsv instead.
    static String csvCell(String value) {
        if (value.contains(",") || value.contains("\"")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | topStudents   (Level 2 - Intermediate)
    // students.csv has name, class, math, science, english, attendance_pct.
    // Return the n best students as Ranked(name, average): the average of the three
    // subjects rounded to 2 decimals, best first; equal averages -> name A-Z.
    // ---------------------------------------------------------------------------
    static List<Ranked> topStudents(Path path, int n) throws IOException {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | monthlyReport   (Level 3 - Challenge)
    // From a sales CSV write a NEW CSV at outPath with the header  month,orders,revenue
    // - one row per month ("2026-01", from order_date), sorted by month, orders = number of
    //   rows, revenue rounded to 2 decimals. Return the number of months written.
    // Hint: reuse readCsvRows, revenueOf and writeCsv.
    // ---------------------------------------------------------------------------
    static int monthlyReport(Path salesPath, Path outPath) throws IOException {
        // TODO: write your code here
        return -1;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | mergeJsonConfigs   (Level 3 - Challenge)
    // defaultPath holds default settings; userPath holds the user's overrides (the user file
    // may NOT exist). Return the defaults updated with the user values. Nested objects are
    // merged key by key (a DEEP merge); every other value is simply replaced.
    //   defaults {"ui":{"theme":"light","size":12},"lang":"en"}   user {"ui":{"theme":"dark"}}
    //   -> {ui={theme=dark, size=12}, lang=en}
    // Hint: loadJson gives an Object; test it with  x instanceof Map<?, ?> m ; a recursive helper
    // that merges two maps is the cleanest way.
    // ---------------------------------------------------------------------------
    static Map<String, Object> mergeJsonConfigs(Path defaultPath, Path userPath) throws IOException {
        // TODO: write your code here
        return null;
    }

    static Map<String, Object> merge(Map<?, ?> base, Map<?, ?> override) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-3 | Quote-aware CSV line   (Level 3 - Challenge)
    // Real CSV cells can contain commas when they are wrapped in double quotes, and a quote
    // inside a quoted cell is written twice. Split ONE line into its cells:
    //   splitCsvLine("a,b,c")                 -> [a, b, c]
    //   splitCsvLine("1,\"Chai, masala\",20") -> [1, Chai, masala, 20]   (3 cells: the middle one is "Chai, masala")
    //   splitCsvLine("\"say \"\"hi\"\"\",ok") -> [say "hi", ok]
    //   splitCsvLine("a,,c")                  -> [a, , c]                (an empty cell stays)
    // Hint: walk through the characters with a boolean inQuotes and a StringBuilder for the current cell.
    // ---------------------------------------------------------------------------
    static List<String> splitCsvLine(String line) {
        // TODO: write your code here
        return null;
    }

    // ======================= ready-made JSON helper (read it after the tasks) ====================
    static final class Json {
        /** Nested data -> compact JSON text (Map, List, String, Number, Boolean, null). */
        static String write(Object value) {
            if (value == null) {
                return "null";
            } else if (value instanceof String s) {
                return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\t", "\\t") + "\"";
            } else if (value instanceof Number || value instanceof Boolean) {
                return value.toString();
            } else if (value instanceof List<?> list) {
                return list.stream().map(Json::write).collect(Collectors.joining(",", "[", "]"));
            } else if (value instanceof Map<?, ?> map) {
                return map.entrySet().stream()
                        .map(e -> write(String.valueOf(e.getKey())) + ":" + write(e.getValue()))
                        .collect(Collectors.joining(",", "{", "}"));
            }
            throw new IllegalArgumentException("cannot write " + value.getClass().getSimpleName());
        }

        /** JSON text -> LinkedHashMap / ArrayList / String / Integer (or Long) / Double / Boolean / null. */
        static Object parse(String text) {
            Reader reader = new Reader(text);
            Object value = reader.value();
            reader.skipSpaces();
            if (reader.pos != text.length()) {
                throw new IllegalArgumentException("extra text after the JSON value at position " + reader.pos);
            }
            return value;
        }

        // A reader walks through the text with a position and reads one value at a time.
        private static final class Reader {
            private final String s;
            private int pos = 0;

            Reader(String s) {
                this.s = s;
            }

            void skipSpaces() {
                while (pos < s.length() && Character.isWhitespace(s.charAt(pos))) {
                    pos++;
                }
            }

            void expect(char c) {
                if (pos >= s.length() || s.charAt(pos) != c) {
                    throw new IllegalArgumentException("expected '" + c + "' at position " + pos);
                }
                pos++;
            }

            Object value() {
                skipSpaces();
                if (pos >= s.length()) {
                    throw new IllegalArgumentException("unexpected end of JSON text");
                }
                char c = s.charAt(pos);
                if (c == '{') {
                    return object();
                } else if (c == '[') {
                    return array();
                } else if (c == '"') {
                    return string();
                } else if (s.startsWith("true", pos)) {
                    pos += 4;
                    return true;
                } else if (s.startsWith("false", pos)) {
                    pos += 5;
                    return false;
                } else if (s.startsWith("null", pos)) {
                    pos += 4;
                    return null;
                }
                return number();
            }

            Map<String, Object> object() {
                Map<String, Object> map = new LinkedHashMap<>();
                expect('{');
                skipSpaces();
                if (pos < s.length() && s.charAt(pos) == '}') {
                    pos++;
                    return map;
                }
                while (true) {
                    skipSpaces();
                    String key = string();
                    skipSpaces();
                    expect(':');
                    map.put(key, value());
                    skipSpaces();
                    if (pos < s.length() && s.charAt(pos) == ',') {
                        pos++;
                    } else {
                        expect('}');
                        return map;
                    }
                }
            }

            List<Object> array() {
                List<Object> list = new ArrayList<>();
                expect('[');
                skipSpaces();
                if (pos < s.length() && s.charAt(pos) == ']') {
                    pos++;
                    return list;
                }
                while (true) {
                    list.add(value());
                    skipSpaces();
                    if (pos < s.length() && s.charAt(pos) == ',') {
                        pos++;
                    } else {
                        expect(']');
                        return list;
                    }
                }
            }

            String string() {
                expect('"');
                StringBuilder sb = new StringBuilder();
                while (pos < s.length() && s.charAt(pos) != '"') {
                    char c = s.charAt(pos++);
                    if (c == '\\') {
                        char next = s.charAt(pos++);
                        switch (next) {
                            case 'n' -> sb.append('\n');
                            case 't' -> sb.append('\t');
                            case 'u' -> {
                                sb.append((char) Integer.parseInt(s.substring(pos, pos + 4), 16));
                                pos += 4;
                            }
                            default -> sb.append(next);
                        }
                    } else {
                        sb.append(c);
                    }
                }
                expect('"');
                return sb.toString();
            }

            Object number() {
                int start = pos;
                while (pos < s.length() && "+-0123456789.eE".indexOf(s.charAt(pos)) >= 0) {
                    pos++;
                }
                String t = s.substring(start, pos);
                if (t.isEmpty()) {
                    throw new IllegalArgumentException("unexpected character at position " + pos);
                }
                if (t.contains(".") || t.contains("e") || t.contains("E")) {
                    return Double.parseDouble(t);
                }
                long n = Long.parseLong(t);
                if (n >= Integer.MIN_VALUE && n <= Integer.MAX_VALUE) {
                    return (int) n;
                }
                return n;
            }
        }
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    // The Checker's lambdas cannot throw IOException, so attempt(...) wraps it for the tests.
    interface Action<T> {
        T run() throws Exception;
    }

    static <T> T attempt(Action<T> action) {
        try {
            return action.run();
        } catch (RuntimeException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException(e.getClass().getSimpleName() + ": " + e.getMessage(), e);
        }
    }

    static String text(Path p) throws IOException {
        return new String(Files.readAllBytes(p), StandardCharsets.UTF_8).replace("\r\n", "\n");
    }

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> all = Files.walk(root)) {
            for (Path p : all.sorted(Comparator.reverseOrder()).toList()) {
                Files.deleteIfExists(p);
            }
        }
    }

    public static void main(String[] args) throws IOException {
        String smallSales = "order_id,order_date,region,category,product,quantity,unit_price,discount_pct,payment_method\n"
                + "O1,2026-01-05,North,Home,Lamp,2,500,10,UPI\n"
                + "O2,2026-01-20,South,Home,Lamp,1,500,0,Card\n"
                + "O3,2026-02-02,North,Fashion,Kurta,3,900,5,UPI\n";
        Path sales = Path.of("../../datasets/sales.csv");
        Path students = Path.of("../../datasets/students.csv");

        System.out.println("--- Day 16 checks ---");
        Path tmp = Files.createTempDirectory("day16");
        try {
            Path small = tmp.resolve("small.csv");
            Files.writeString(small, smallSales);
            Checker.check("L1-1 readCsvRows", () -> attempt(() -> {
                List<Map<String, String>> rows = readCsvRows(small);
                return List.of(rows.size(), rows.get(0).get("region"), rows.get(0).get("quantity"), rows.get(2).get("product"));
            }), List.of(3, "North", "2", "Kurta"));
            Checker.check("L1-1 readCsvRows real file", () -> attempt(() -> readCsvRows(sales).size()), 300);
            Checker.check("L1-2 revenueOf", () -> revenueOf(Map.of("quantity", "2", "unit_price", "500", "discount_pct", "10")), 900.0);
            Checker.check("L1-2 totalRevenue small", () -> attempt(() -> totalRevenue(small)), 900 + 500 + 2565.0);
            Checker.check("L1-2 totalRevenue real file", () -> attempt(() -> totalRevenue(sales)), 1443241.55);

            Path jp = tmp.resolve("cfg.json");
            Map<String, Object> cfg = new LinkedHashMap<>();
            cfg.put("symbol", "\u20b9");
            cfg.put("n", List.of(1, 2));
            Checker.check("L1-3 saveJson + loadJson", () -> attempt(() -> {
                saveJson(jp, cfg);
                return loadJson(jp, null);
            }), cfg);
            Checker.check("L1-3 saveJson writes UTF-8 text", () -> attempt(() -> text(jp)), "{\"symbol\":\"\u20b9\",\"n\":[1,2]}");
            Checker.check("L1-3 loadJson default", () -> attempt(() -> loadJson(tmp.resolve("missing.json"), Map.of("x", 1))),
                    Map.of("x", 1));

            Checker.check("L2-1 revenueByRegion small", () -> attempt(() -> revenueByRegion(small)),
                    Map.of("North", 3465.0, "South", 500.0));
            Checker.check("L2-1 revenueByRegion real", () -> attempt(() -> revenueByRegion(sales)),
                    Map.of("East", 335268.6, "North", 300446.25, "South", 348849.7, "West", 458677.0));
            Path out = tmp.resolve("out.csv");
            Checker.check("L2-2 writeCsv", () -> attempt(() -> {
                writeCsv(out, List.of(Map.of("a", 1, "b", "x"), Map.of("a", 2, "b", "y")), List.of("a", "b"));
                return text(out);
            }), "a,b\n1,x\n2,y\n");
            Checker.check("L2-2 writeCsv quotes", () -> attempt(() -> {
                writeCsv(out, List.of(Map.of("a", "x,y", "b", "say \"hi\"")), List.of("a", "b"));
                return text(out);
            }), "a,b\n\"x,y\",\"say \"\"hi\"\"\"\n");
            Checker.check("L2-3 topStudents", () -> attempt(() -> topStudents(students, 3)),
                    List.of(new Ranked("Chirag", 93.67), new Ranked("Neel", 86.0), new Ranked("Gauri", 84.33)));

            Path rep = tmp.resolve("monthly.csv");
            Checker.check("L3-1 monthlyReport months", () -> attempt(() -> monthlyReport(small, rep)), 2);
            Checker.check("L3-1 monthlyReport content", () -> attempt(() -> text(rep)),
                    "month,orders,revenue\n2026-01,2,1400.0\n2026-02,1,2565.0\n");
            Checker.check("L3-1 monthlyReport real file", () -> attempt(() -> monthlyReport(sales, tmp.resolve("real_monthly.csv"))), 10);

            Path d = tmp.resolve("defaults.json");
            Path u = tmp.resolve("user.json");
            Files.writeString(d, "{\"ui\":{\"theme\":\"light\",\"size\":12},\"lang\":\"en\"}");
            Checker.check("L3-2 merge without user file", () -> attempt(() -> mergeJsonConfigs(d, u)),
                    Map.of("ui", Map.of("theme", "light", "size", 12), "lang", "en"));
            Files.writeString(u, "{\"ui\":{\"theme\":\"dark\"},\"extra\":true}");
            Checker.check("L3-2 deep merge", () -> attempt(() -> mergeJsonConfigs(d, u)),
                    Map.of("ui", Map.of("theme", "dark", "size", 12), "lang", "en", "extra", true));

            Checker.check("L3-3 splitCsvLine plain", () -> List.of(splitCsvLine("a,b,c"), splitCsvLine("a,,c"), splitCsvLine("a,")),
                    List.of(List.of("a", "b", "c"), List.of("a", "", "c"), List.of("a", "")));
            Checker.check("L3-3 splitCsvLine quotes", () -> List.of(splitCsvLine("1,\"Chai, masala\",20"),
                    splitCsvLine("\"say \"\"hi\"\"\",ok")), List.of(List.of("1", "Chai, masala", "20"), List.of("say \"hi\"", "ok")));
        } finally {
            deleteTree(tmp);
        }
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
