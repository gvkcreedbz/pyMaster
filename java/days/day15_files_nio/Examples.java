/* Day 15 - Code along: a to-do list and a server-log analyser.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * We write into a temporary folder that is deleted at the end, so nothing is left on your disk.
 * File methods can fail, so main says "throws IOException" (Day 17 explains how to handle errors).
 */
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Examples {
    public static void main(String[] args) throws IOException {
        Path tmp = Files.createTempDirectory("day15-demo");   // a safe playground folder
        try {
            // ---- 1. Paths are objects ----
            Path todo = tmp.resolve("notes").resolve("todo.txt");      // resolve = "join": notes/todo.txt inside tmp
            System.out.println(todo.getFileName());                    // todo.txt
            System.out.println(todo.getParent().getFileName());        // notes
            System.out.println(Path.of("a", "b", "c.txt"));            // a/b/c.txt (a\b\c.txt on Windows)
            System.out.println(Files.exists(todo));                    // false: nothing there yet

            // ---- 2. Write (create the folder first) ----
            Files.createDirectories(todo.getParent());                 // makes every missing folder
            Files.writeString(todo, "Buy milk\nLearn Java\n", StandardCharsets.UTF_8);   // creates or OVERWRITES
            System.out.println(Files.exists(todo) + " " + Files.size(todo) + " bytes");

            // ---- 3. Append: add to the end, never erase ----
            Files.writeString(todo, "Call mom\n", StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
            Files.write(todo, List.of("Pay rent", "Walk 5 km"), StandardOpenOption.APPEND);   // several lines at once

            // ---- 4. Read ----
            String everything = Files.readString(todo);                // one big String
            List<String> lines = Files.readAllLines(todo);             // a list, without the line endings
            System.out.println(lines.size() + " tasks, first = " + lines.get(0));   // 5 tasks, first = Buy milk
            System.out.println(everything.length() + " characters");
            long learn = lines.stream().filter(line -> line.contains("Java")).count();
            System.out.println("Mentions Java: " + learn);             // 1

            // ---- 5. UTF-8 and the rupee sign ----
            Path price = tmp.resolve("price.txt");
            Files.writeString(price, "Chai \u20b920\n", StandardCharsets.UTF_8);    // \u20b9 is the Rs. sign
            System.out.println(Files.readString(price, StandardCharsets.UTF_8).strip().equals("Chai \u20b920"));   // true

            // ---- 6. List the files in a folder (the try(...) closes the folder for us) ----
            Files.writeString(tmp.resolve("notes").resolve("ideas.md"), "# ideas\n");
            try (Stream<Path> entries = Files.list(todo.getParent())) {
                List<String> names = entries.map(p -> p.getFileName().toString()).sorted().toList();
                System.out.println(names);                            // [ideas.md, todo.txt]
            }

            // ---- 7. Parse a log line ----
            String line = "2026-11-01 08:30:00 ERROR user=bob action=db_timeout";
            String[] parts = line.split(" ");
            Map<String, String> fields = new HashMap<>();
            for (int i = 3; i < parts.length; i++) {
                String[] pair = parts[i].split("=");
                fields.put(pair[0], pair[1]);
            }
            System.out.println(parts[2] + " by " + fields.get("user") + " (" + fields.get("action") + ")");   // ERROR by bob (db_timeout)

            // ---- 8. The real log: count the levels ----
            Path log = Path.of("../../datasets/app.log");              // relative to this folder
            if (Files.exists(log)) {
                Map<String, Long> levels = new TreeMap<>();
                for (String entry : Files.readAllLines(log)) {
                    if (!entry.isBlank()) {
                        levels.merge(entry.split(" ")[2], 1L, Long::sum);
                    }
                }
                System.out.println(levels);                           // {ERROR=39, INFO=180, WARNING=21}
            } else {
                System.out.println("(datasets/app.log not found: run this file from its own folder)");
            }
        } finally {
            try (Stream<Path> all = Files.walk(tmp)) {                // clean up the playground
                for (Path p : all.sorted(Comparator.reverseOrder()).toList()) {
                    Files.deleteIfExists(p);
                }
            }
        }
    }
}
