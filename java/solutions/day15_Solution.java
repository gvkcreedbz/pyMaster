// SOLUTION FILE - try the hint ladder first!
/* Day 15 - Practice: files with java.nio.file.
 *
 * Run:  java Practice.java
 * File methods can fail (missing file, full disk), so Java makes you write "throws IOException"
 * after the method's brackets. Day 17 explains how to handle it; today just keep that promise.
 * The checks only touch a temporary folder that is deleted at the end.
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | writeLines   (Level 1 - Beginner)
    // Write every item of `lines` to the file at `path`, one per line. Overwrite the
    // file if it exists (create it if it does not).
    // Hint: Files.write(path, lines)
    // ---------------------------------------------------------------------------
    static void writeLines(Path path, List<String> lines) throws IOException {
        // >>> SOLUTION
        Files.write(path, lines, StandardCharsets.UTF_8);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | readLines   (Level 1 - Beginner)
    // Return the file's lines as a List<String> (without the line endings).
    // Hint: Files.readAllLines(path)
    // ---------------------------------------------------------------------------
    static List<String> readLines(Path path) throws IOException {
        // >>> SOLUTION stub: return null;
        return Files.readAllLines(path, StandardCharsets.UTF_8);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | countLines   (Level 1 - Beginner)
    // Return how many lines the file has (0 for an empty file).
    // ---------------------------------------------------------------------------
    static int countLines(Path path) throws IOException {
        // >>> SOLUTION stub: return -1;
        return readLines(path).size();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | addTodo   (Level 2 - Intermediate)
    // Append `task` as a new line at the END of the file. Create the file if it does not
    // exist, but never erase old tasks. Return how many tasks the file now holds.
    // Hint: Files.writeString(path, text, StandardOpenOption.CREATE, StandardOpenOption.APPEND)
    //       and do not forget the "\n" after the task.
    // ---------------------------------------------------------------------------
    static int addTodo(Path path, String task) throws IOException {
        // >>> SOLUTION stub: return -1;
        Files.writeString(path, task + "\n", StandardCharsets.UTF_8, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        return countLines(path);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | countLogLevels   (Level 2 - Intermediate)
    // Each log line looks like:  2026-11-01 08:30:00 ERROR user=bob action=db_timeout
    // Return a Map: level -> how many lines have it (the level is the 3rd word).
    // Ignore blank lines.   -> {INFO=2, ERROR=2, WARNING=1}
    // Hint: line.split("\\s+")[2] and map.merge(level, 1, Integer::sum)
    // ---------------------------------------------------------------------------
    static Map<String, Integer> countLogLevels(Path path) throws IOException {
        // >>> SOLUTION stub: return null;
        Map<String, Integer> counts = new HashMap<>();
        for (String line : readLines(path)) {
            if (line.isBlank()) {
                continue;
            }
            String level = line.trim().split("\\s+")[2];
            counts.merge(level, 1, Integer::sum);
        }
        return counts;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | findFiles   (Level 2 - Intermediate)
    // Return a sorted List of the NAMES (not full paths) of the FILES directly inside
    // `folder` whose name ends with `suffix` (e.g. ".txt"). Ignore sub-folders.
    // Hint: try (Stream<Path> entries = Files.list(folder)) { ... }   (a pattern to copy:
    //       the try(...) closes the folder for you), then Files.isRegularFile(p), p.getFileName().
    // ---------------------------------------------------------------------------
    static List<String> findFiles(Path folder, String suffix) throws IOException {
        // >>> SOLUTION stub: return null;
        try (Stream<Path> entries = Files.list(folder)) {
            return entries.filter(Files::isRegularFile)
                    .map(p -> p.getFileName().toString())
                    .filter(name -> name.endsWith(suffix))
                    .sorted()
                    .toList();
        }
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-4 | extensionOf   (Level 2 - Intermediate)
    // Return the part of the file NAME after the last dot, in lower case; "" when the
    // name has no dot. No file access needed, just look at the Path.
    //   extensionOf(Path.of("docs", "Report.FINAL.CSV")) -> "csv"     extensionOf(Path.of("README")) -> ""
    // Hint: path.getFileName().toString(), name.lastIndexOf('.')
    // ---------------------------------------------------------------------------
    static String extensionOf(Path file) {
        // >>> SOLUTION stub: return null;
        String name = file.getFileName().toString();
        int dot = name.lastIndexOf('.');
        return dot < 0 ? "" : name.substring(dot + 1).toLowerCase();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | errorReport   (Level 3 - Challenge)
    // Read the log at logPath and write a report file at reportPath that has one line per
    // ERROR entry:  "<time> <action> <user>"   e.g. "08:30:00 db_timeout bob"
    // (original order). Return the number of ERROR lines found.
    // Hint: split each line on spaces; words from the 4th on look like key=value
    //       (put them in a Map by splitting on "=").
    // ---------------------------------------------------------------------------
    static int errorReport(Path logPath, Path reportPath) throws IOException {
        // >>> SOLUTION stub: return -1;
        List<String> report = new ArrayList<>();
        for (String line : readLines(logPath)) {
            String[] parts = line.trim().split("\\s+");
            if (parts.length >= 3 && parts[2].equals("ERROR")) {
                Map<String, String> fields = new HashMap<>();
                for (int i = 3; i < parts.length; i++) {
                    String[] pair = parts[i].split("=", 2);
                    fields.put(pair[0], pair[1]);
                }
                report.add(parts[1] + " " + fields.get("action") + " " + fields.get("user"));
            }
        }
        writeLines(reportPath, report);
        return report.size();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | busiestHour   (Level 3 - Challenge)
    // Return the hour (an int 0-23, taken from the time part) that has the MOST log
    // lines. If several hours tie, return the earliest. Return -1 for an empty log.
    // Hint: Integer.parseInt(parts[1].substring(0, 2))
    // ---------------------------------------------------------------------------
    static int busiestHour(Path logPath) throws IOException {
        // >>> SOLUTION stub: return -2;
        Map<Integer, Integer> counts = new TreeMap<>();   // TreeMap: hours come out in order
        for (String line : readLines(logPath)) {
            if (line.isBlank()) {
                continue;
            }
            int hour = Integer.parseInt(line.trim().split("\\s+")[1].substring(0, 2));
            counts.merge(hour, 1, Integer::sum);
        }
        int bestHour = -1;
        int bestCount = 0;
        for (Map.Entry<Integer, Integer> e : counts.entrySet()) {
            if (e.getValue() > bestCount) {      // strictly bigger: on a tie the earlier hour stays
                bestHour = e.getKey();
                bestCount = e.getValue();
            }
        }
        return bestHour;
        // <<< SOLUTION
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
        String sampleLog = "2026-11-01 08:00:01 INFO user=alice action=login ip=1.1.1.1\n"
                + "2026-11-01 08:30:00 ERROR user=bob action=db_timeout ip=1.1.1.2\n"
                + "2026-11-01 09:15:10 WARNING user=alice action=slow_response ip=1.1.1.1\n"
                + "2026-11-01 09:20:00 ERROR user=alice action=payment_failed ip=1.1.1.1\n"
                + "2026-11-01 09:45:00 INFO user=charu action=logout ip=1.1.1.3\n";

        System.out.println("--- Day 15 checks ---");
        Path tmp = Files.createTempDirectory("day15");
        try {
            Path f1 = tmp.resolve("a.txt");
            Checker.check("L1-1 writeLines (utf-8, newline per line)", () -> attempt(() -> {
                writeLines(f1, List.of("one", "two", "\u20b9three"));
                return text(f1);
            }), "one\ntwo\n\u20b9three\n");
            Checker.check("L1-1 writeLines overwrites", () -> attempt(() -> {
                writeLines(f1, List.of("only"));
                return text(f1);
            }), "only\n");
            Path f2 = tmp.resolve("b.txt");
            Files.writeString(f2, "x\ny\n\nz\n");
            Checker.check("L1-2 readLines", () -> attempt(() -> readLines(f2)), List.of("x", "y", "", "z"));
            Checker.check("L1-3 countLines", () -> attempt(() -> countLines(f2)), 4);
            Path empty = tmp.resolve("empty.txt");
            Files.writeString(empty, "");
            Checker.check("L1-3 countLines empty", () -> attempt(() -> countLines(empty)), 0);

            Path todo = tmp.resolve("todo.txt");
            Checker.check("L2-1 addTodo creates file", () -> attempt(() -> addTodo(todo, "Buy milk")), 1);
            Checker.check("L2-1 addTodo appends", () -> attempt(() -> List.of(addTodo(todo, "Learn Java"), readLines(todo))),
                    List.of(2, List.of("Buy milk", "Learn Java")));
            Path log = tmp.resolve("app.log");
            Files.writeString(log, sampleLog);
            Checker.check("L2-2 countLogLevels", () -> attempt(() -> countLogLevels(log)),
                    Map.of("INFO", 2, "ERROR", 2, "WARNING", 1));

            Path docs = Files.createDirectory(tmp.resolve("docs"));
            Files.writeString(docs.resolve("b.txt"), "b");
            Files.writeString(docs.resolve("a.txt"), "a");
            Files.writeString(docs.resolve("note.md"), "m");
            Files.createDirectory(docs.resolve("sub.txt"));       // a folder that LOOKS like a text file
            Checker.check("L2-3 findFiles", () -> attempt(() -> List.of(findFiles(docs, ".txt"), findFiles(docs, ".md"),
                    findFiles(docs, ".zip"))), List.of(List.of("a.txt", "b.txt"), List.of("note.md"), List.of()));
            Checker.check("L2-4 extensionOf", () -> List.of(extensionOf(Path.of("docs", "Report.FINAL.CSV")),
                    extensionOf(Path.of("README")), extensionOf(Path.of("notes.txt"))), List.of("csv", "", "txt"));

            Path rep = tmp.resolve("report.txt");
            Checker.check("L3-1 errorReport count", () -> attempt(() -> errorReport(log, rep)), 2);
            Checker.check("L3-1 errorReport file", () -> attempt(() -> readLines(rep)),
                    List.of("08:30:00 db_timeout bob", "09:20:00 payment_failed alice"));
            Checker.check("L3-2 busiestHour", () -> attempt(() -> busiestHour(log)), 9);
            Path tie = tmp.resolve("tie.log");
            Files.writeString(tie, "2026-11-01 07:00:00 INFO user=a action=x\n2026-11-01 05:10:00 INFO user=b action=y\n"
                    + "\n2026-11-01 07:30:00 INFO user=a action=x\n2026-11-01 05:40:00 INFO user=b action=y\n");
            Checker.check("L3-2 busiestHour tie -> earliest", () -> attempt(() -> busiestHour(tie)), 5);
            Checker.check("L3-2 busiestHour empty", () -> attempt(() -> busiestHour(empty)), -1);

            Path real = Path.of("../../datasets/app.log");
            Checker.check("Real app.log: level counts", () -> attempt(() -> countLogLevels(real)),
                    Map.of("INFO", 180, "WARNING", 21, "ERROR", 39));
            Checker.check("Real app.log: errors in report", () -> attempt(() -> errorReport(real, tmp.resolve("real_report.txt"))), 39);
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
