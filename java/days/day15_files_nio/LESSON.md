# Day 15 — Files with `java.nio.file` (Path, Files, folders and a log analyser)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Read and write text files safely, build paths that work on any computer, analyse a real log file | Intermediate |

## 🌍 Real-world scenario & trend
**A server log analyser.** Every app writes logs (`2026-11-01 08:00:01 ERROR user=bob action=db_timeout`). On-call engineers and data teams read these files to find errors, busy hours and failing users. The same skills save a to-do list, load a config file or process an export.

**Why Java?** Java back-ends live on servers, and servers live on logs and files. `java.nio.file` (`Path` + `Files`) is the modern way to work with files: one short call reads or writes a whole file, and the same code runs on Windows, Mac and Linux. *Coming from Python?* `Path` is `pathlib.Path`, `Files.writeString` is `write_text`, and `Files.readAllLines` is `readlines` without the `\n`.

## 0. Warm-up (5 min) — Day 14 recap
- How do you make a `Map` of totals per category?  • What does `date.substring(0, 7)` give for `"2026-11-16"`?

## 1. Concepts (with tiny code)

### 1.1 `Path`: a file location as an object
```java
Path todo = Path.of("notes", "todo.txt");          // notes/todo.txt (notes\todo.txt on Windows)
Path inFolder = base.resolve("todo.txt");          // resolve = join a name onto a folder
todo.getFileName();                                // todo.txt
todo.getParent();                                  // notes
todo.toAbsolutePath();                             // the full path from the drive root
```
Never glue paths with `"notes/" + name`; `Path.of(...)` and `resolve(...)` add the right separator for you.

### 1.2 Writing text
```java
Files.writeString(path, "Line 1\nLine 2\n");                  // creates the file or OVERWRITES it
Files.write(path, List.of("Line 1", "Line 2"));               // a list: each item becomes one line
Files.writeString(path, "Line 3\n", StandardOpenOption.CREATE, StandardOpenOption.APPEND);   // add to the END
```
| Option | Meaning |
|---|---|
| (none) | create, or erase the old content and write |
| `APPEND` (+ `CREATE`) | add to the end, create the file if missing |
| `CREATE_NEW` | create, but fail if the file already exists |

### 1.3 Reading text
```java
String everything = Files.readString(path);          // one big String
List<String> lines = Files.readAllLines(path);       // list of lines, line endings removed
```
For a huge file, stream it one line at a time and let `try` close it:
```java
try (Stream<String> stream = Files.lines(path)) {
    long errors = stream.filter(l -> l.contains("ERROR")).count();
}
```

### 1.4 Always think UTF-8
Text with `₹`, `é` or emojis must be written and read with the same encoding. The `Files` methods above already use UTF-8, and you can say it out loud with `StandardCharsets.UTF_8`: `Files.readString(path, StandardCharsets.UTF_8)`. (Windows' old default is the classic cause of broken `₹` signs in other languages.)

### 1.5 Folders and "does it exist?"
```java
Files.exists(path);   Files.isRegularFile(path);   Files.isDirectory(path);   Files.size(path);
Files.createDirectories(Path.of("out", "reports"));      // makes every missing folder
try (Stream<Path> entries = Files.list(folder)) {          // the files directly inside a folder
    entries.filter(Files::isRegularFile).forEach(p -> System.out.println(p.getFileName()));
}
Path playground = Files.createTempDirectory("demo");       // a throw-away folder for tests
```
`Files.list` gives a stream that holds the folder open, so wrap it in `try ( ... ) { }` exactly like above: a pattern to copy now, explained on Day 17.

### 1.6 `throws IOException`: files can fail
A missing file or a full disk is not your bug, but it can happen. Java forces you to admit it by writing `throws IOException` on the method:
```java
static List<String> readLines(Path path) throws IOException {
    return Files.readAllLines(path);
}
```
Any method that calls it must also say `throws IOException` (or handle the error, which is Day 17). In `Practice.java` every method that touches a file already has it.

### 1.7 Parsing a log line
```java
String line = "2026-11-01 08:30:00 ERROR user=bob action=db_timeout";
String[] parts = line.split("\\s+");                 // [date, time, level, user=bob, action=db_timeout]
String level = parts[2];                              // ERROR
String[] pair = parts[3].split("=");                  // ["user", "bob"]
```
Put the `key=value` pairs into a `Map<String, String>` and you can ask for `fields.get("user")`.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run. It writes into a temporary folder that it deletes at the end, and reads the real `datasets/app.log` (relative path `../../datasets/app.log`).

## 3. Common mistakes
- Writing with `writeString` when you meant to append: you just erased the file.
- Forgetting the `\n` at the end of each line you write with `writeString`.
- Forgetting `throws IOException`: the compiler says `unreported exception IOException; must be caught or declared to be thrown`.
- Not closing `Files.list` / `Files.lines`: always use `try ( ... ) { }` with them.
- `Files.readAllLines` on a missing file: `NoSuchFileException`. Check `Files.exists(path)` first when it may be missing.
- Reading a gigantic file with `readString` instead of `Files.lines`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Write lines, read lines, count lines |
| L2-1 … L2-4 | 🟡 Intermediate | Append a to-do, count log levels, find files by extension, get a file's extension |
| L3-1, L3-2 | 🔴 Challenge | Write an error report file, find the busiest hour |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]`. It only writes to a temporary folder and deletes it afterwards.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Say it in steps: read all lines → loop over them → clean or split each line → collect → return (or write).
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Level = <code>line.split("\\s+")[2]</code>. Hour = <code>Integer.parseInt(parts[1].substring(0, 2))</code>. Count with <code>map.merge(key, 1, Integer::sum)</code>. Append: <code>Files.writeString(path, task + "\n", StandardOpenOption.CREATE, StandardOpenOption.APPEND)</code>. Folder listing: the <code>try (Stream&lt;Path&gt; entries = Files.list(folder))</code> pattern from 1.5, then <code>sorted()</code>. Busiest hour with ties → earliest: loop over a <code>TreeMap</code> and only replace the best when the new count is <em>strictly</em> bigger. Report line: <code>time + " " + action + " " + user</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day15_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day15_answers.md`
1. What does `Files.writeString(path, "hi")` do to a file that already exists?
2. How do you add a line to the end of a file without erasing it?
3. What does `Files.readAllLines(path)` return for the file `"x\ny\n"`?
4. What does `throws IOException` on a method mean?
5. What does `Path.of("a", "b", "c.txt").getFileName()` give?
6. Why should you use `Path.of(...)` / `resolve(...)` instead of `"a/" + "b"`?
7. Why is `Files.list(folder)` placed in `try ( ... )`?
8. Why do we mention UTF-8 when reading and writing text?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: CSV and JSON-style files: sales reports from a spreadsheet export, and settings you save and load.
