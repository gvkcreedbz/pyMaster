# Authoring guide for the Java course (maintainers and AI authors: read this first)

The Java course is the twin of the Python course in `days/` and `solutions/`. **Day N teaches the same idea, with the
same real-world scenario, in idiomatic modern Java 21.** Read `days/dayNN_*/LESSON.md` and `solutions/dayNN_solution.py`
for the same N before you write a day. Reference implementation of the format: **Day 01** (copy its structure exactly).

## Files for day N (NN = two digits, topic = lower_snake)

```
java/days/dayNN_<topic>/LESSON.md       lesson (format below)
java/days/dayNN_<topic>/Examples.java   code-along (class Examples with main); must exit 0
java/days/dayNN_<topic>/Practice.java   GENERATED - never edit by hand
java/solutions/dayNN_Solution.java      SOURCE OF TRUTH: the full practice file with solutions inside markers
java/solutions/dayNN_answers.md         quiz answers
```
After writing the solution file run `python _dev_tools/java_sync.py N` (expands the checker, writes Practice.java) and then
`python _dev_tools/verify_java.py N` until it prints `Day NN: OK`.
Java is found automatically (JAVA_HOME, `.tools/jdk21`, or PATH). Use the isolated Python for tools if plain `python` is missing:
`%TEMP%\pyverify\py\python.exe -W ignore -c "import sys,runpy; sys.path.insert(0,'_dev_tools'); sys.argv=['x','N']; runpy.run_path('_dev_tools/verify_java.py', run_name='__main__')"`

## Solution file format (study `java/solutions/day01_Solution.java`)

* One non-public `class Practice { ... }` with the exercises as **static methods** (or static fields/nested types), then `main` at the
  bottom under the banner `// ======================= AUTO-CHECKER (do not edit below) ====================`.
* End the file with the line `// @@CHECKER@@` (the sync tool replaces it with the shared `Checker` class).
* Each exercise starts with this comment header (the portal parses it):
  ```java
      // ---------------------------------------------------------------------------
      // L1-1 | Title here   (Level 1 - Beginner)
      // Description lines, every line starting with //
      // ---------------------------------------------------------------------------
  ```
  IDs `L1-1, L1-2, ...`, `L2-1, ...`, `L3-1, ...`. Level text: `Level 1 - Beginner`, `Level 2 - Intermediate`, `Level 3 - Challenge`.
  Write **6-9 exercises** per day (about 3 / 3 / 1-2). Project days (7, 14, 21, 29, 30) may have fewer but bigger exercises.
* Wrap what the learner writes in markers; the optional `stub:` keeps the unfinished file compiling:
  ```java
      static int add(int a, int b) {
          // >>> SOLUTION stub: return 0;
          return a + b;
          // <<< SOLUTION
      }
  ```
  For `void` methods no stub is needed. For a field: `// >>> SOLUTION stub: static String name = null;` then the real declaration.
  The unfinished `Practice.java` MUST compile and run to its `Score: x/y` line (every check may fail).
* Checks in `main` use `Checker.check("L1-1 name", () -> expr, expected)`, `Checker.printed(Runnable)` to capture `System.out`,
  `Checker.withInput("line1\nline2\n", () -> expr)` to feed `System.in`, and finally `Checker.done()`.
  Numbers: int vs long compare by value; doubles compare within 1e-6. Arrays/lists/maps compare by content.
* Deterministic output only (no random without a seed, no current time in expected values, no network except a loopback server you start yourself).
* Reading data files: relative path `../../datasets/sales.csv` (the program's working directory is the day folder; `java/datasets/` holds copies).
* Do not use preview features or libraries other than: the JDK, and (only on the days that say so) the jars in `java/lib/`
  (JUnit console launcher on Day 24, sqlite-jdbc + slf4j on Days 28-29). If a jar is missing, `python _dev_tools/fetch_java_libs.py` downloads it.

## LESSON.md format (study Day 01; the portal parses these exact things)

```
# Day NN — Title (subtitle)                       <- em dash (—), not a hyphen

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | one sentence goal | Beginner / Intermediate / Advanced |

## 🌍 Real-world scenario & trend                 <- first paragraph = the scenario (bold lead-in), then why Java is used for it
## 0. Setup / Warm-up (only if needed)
## 1. Concepts (with tiny code)
### 1.1 Concept name                               <- every "### N.M Name" becomes a concept chip: 4-8 of them, with ```java blocks
## 2. Code along (30 min)  `Examples.java`
## 3. Common mistakes
## 4. Today's tasks  `Practice.java`               <- table ID | Level | Task
## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary> ... </details>
<details><summary>Hint 2 - Shape of the answer</summary> ... </details>
<details><summary>Hint 3 - Peek (last resort)</summary> ... </details>     <- EXACTLY three hints, HTML inside (<code>, not backticks)
## 6. Quiz (10 min, no peeking) - answers in `java/solutions/dayNN_answers.md`
1. question ...                                   <- 8 numbered questions (at least 6); answers.md has the SAME numbers
## 7. Wrap-up (5 min)
```
Lesson length: 120-200 lines. Real code blocks are tagged ```java. Teach by showing tiny runnable snippets then explaining;
beginner voice, short sentences, concrete money/shop/app examples (Indian-rupee shop prices are used in the Python course; keep them).
Mention what is *different from Python* in one sentence where it helps (types, braces, semicolons, `==` vs `.equals`).
Folder names: `day01_hello_java`, `day02_variables_input`, `day03_numbers_operators`, `day04_strings`, `day05_decisions`, `day06_loops`,
`day07_week1_project_atm`, `day08_arrays`, `day09_lists_sets`, `day10_maps`, `day11_methods`, `day12_lambdas_streams`,
`day13_nested_data_records`, `day14_week2_project_expense_tracker`, `day15_files_nio`, `day16_csv_json_files`,
`day17_exceptions_logging`, `day18_packages_stdlib_build_tools`, `day19_oop_basics`, `day20_oop_advanced`,
`day21_week3_project_library_system`, `day22_generics_optional_iterators`, `day23_regex_clean_code`, `day24_junit_git`,
`day25_collections_streams_data`, `day26_streams_reporting`, `day27_http_json`, `day28_jdbc_sql`, `day29_capstone_pipeline`,
`day30_rest_api_final_exam`.

## The 30-day syllabus (Python day -> Java day)

| Day | Java topic | Notes |
|---|---|---|
| 1 | Hello Java: class/main, println/printf, errors | DONE (reference) |
| 2 | Variables, types, `Scanner` input, `var`, text blocks preview | bill splitter |
| 3 | Numbers/operators, casting, `Math`, integer vs double division, `BigDecimal` intro | |
| 4 | Strings: methods, `StringBuilder`, `String.format`, `equals` vs `==`, text blocks | |
| 5 | Decisions: `if/else`, ternary, `switch` expressions, boolean logic | |
| 6 | Loops: `for`, `while`, `do/while`, enhanced for, `break/continue`, nested loops | |
| 7 | Week-1 project: ATM (menu loop with `Scanner`; tested with `Checker.withInput`) | project |
| 8 | Arrays (1-D, 2-D), `Arrays` class, loops over arrays | Python lists |
| 9 | `ArrayList`, `List.of`, wrappers (`Integer`), `HashSet`, `TreeSet`, `Collections` | Python list/tuple/set |
| 10 | `HashMap`, `TreeMap`, `LinkedHashMap`, counting words, `getOrDefault`, `merge` | Python dict |
| 11 | Methods: parameters, return, overloading, varargs, scope, recursion intro | Python functions |
| 12 | Lambdas, functional interfaces, method references, `Stream` basics (`map/filter/sum`) | Python comprehensions/lambda |
| 13 | Nested data: `Map<String,List<...>>`, `record`, simple JSON-like building/printing | |
| 14 | Week-2 project: expense tracker (records, lists, maps, streams) | project |
| 15 | Files with `java.nio.file` (`Path`, `Files.readAllLines/writeString`, directories) | |
| 16 | CSV and JSON-style data: parse `sales.csv`, write reports; hand-rolled JSON writer/reader | |
| 17 | Exceptions: `try/catch/finally`, custom exceptions, try-with-resources, `java.util.logging` | |
| 18 | Packages, imports, `java.time`, `java.util`, Maven/Gradle basics (read `pom.xml`), JAR | |
| 19 | OOP basics: classes, fields, constructors, `this`, encapsulation, `toString/equals/hashCode` | |
| 20 | OOP advanced: inheritance, `interface`, abstract classes, polymorphism, `enum`, `sealed`, `record` | |
| 21 | Week-3 project: library system (classes + file persistence) | project |
| 22 | Generics, `Optional`, `Iterator/Iterable`, functional interfaces (`Function`, `Predicate`) | generators/decorators |
| 23 | Regex (`Pattern/Matcher`), immutability, clean code, naming, small methods | regex/type hints |
| 24 | Testing with JUnit 5 (console launcher jar) + our `Checker`; git basics | pytest/git |
| 25 | Collections deep-dive + `Collectors` (`groupingBy`, `counting`, `averagingDouble`) on `sales.csv` | numpy/pandas 1 |
| 26 | Streams 2: cleaning messy data, sorting, top-N, text bar charts / reporting | pandas 2/matplotlib |
| 27 | HTTP + JSON: `java.net.http.HttpClient` against a **local** `com.sun.net.httpserver` you start in the program | requests/scraping |
| 28 | JDBC + SQL with SQLite (`sqlite-jdbc` jar in `java/lib/`) | sqlite3 |
| 29 | Capstone: a CSV -> clean -> SQLite -> report pipeline | pipeline |
| 30 | A REST API with the JDK's built-in `HttpServer` (routes, JSON, status codes) + Spring Boot explained + final exam | FastAPI + exam |

Day 30 also needs `FINAL_EXAM.md` (27 snippets with expected output) in its folder; its answer key goes in `java/solutions/day30_ExamKey.md`.
