# 🎯 00 — GAME PLAN: Java in 30 Days (strict timeline)

**Start:** Mon 16 Nov 2026 (Day 1) · **Finish:** Tue 15 Dec 2026 (Day 30) · **Budget:** ~2 hours/day = ~60 hours
**Target:** *Above-intermediate* — you can write 100–200-line programs, model data with classes/records/enums, process data with collections and streams, read and write files, handle errors, write tests, query a database with JDBC, call and serve HTTP — and, most importantly, **read and understand** code written by others.
**Direction:** The twin of the [Python plan](../00_GAME_PLAN.md): same days, same real-world scenarios, same weekly rhythm. The Java language adds **static types, compile-time checking and a bigger standard library** — which is exactly why it dominates banks, insurers, Android and large back-end systems.

---

## 1. How this course works (the method)
| Principle | What it means for you |
|---|---|
| **Real example first, theory second** | Every day opens with a real-world situation (Swiggy bill, ATM, sales export…) and a **trend** note: *why* professionals use this. |
| **Code before words** | Each concept is shown as 3–10 lines you can run (or paste into `jshell`), then a code-along, then exercises. |
| **Three difficulty levels daily** | L1 Beginner → L2 Intermediate → L3 Challenge, all auto-checked. See §5. |
| **Immediate feedback** | `java Practice.java` prints `[PASS]`/`[FAIL]`. The compiler also tells you about mistakes *before* the program runs. |
| **Spiral learning** | Arrays in Day 8, then again in lists, maps, streams, CSV, JDBC… everything returns in later projects. |
| **Project every Sunday** | Days 7, 14, 21 are *project + review* days (the weekend buffer); Day 29 is the capstone. |
| **Reflection** | Bug Journal + Weekly Review + Concept Checklist make learning visible. |

## 2. The 30-day timeline
Click a topic to open the lesson. 🏆 = project/review day. Dates assume the default start; they update in the tracker if you change it.

| Day | Date | Topic (lesson) | Real-world scenario |
|---|---|---|---|
| 1 | Mon 16 Nov | [Hello, Java! (class/main, println/printf, errors)](days/day01_hello_java/LESSON.md) | A café receipt printer. |
| 2 | Tue 17 Nov | [Variables, Data Types, `Scanner` input, `var`](days/day02_variables_input/LESSON.md) | Food-delivery bill splitter (Swiggy / Zomato / Uber Eats style). |
| 3 | Wed 18 Nov | [Numbers, Operators, casting, `Math`, `BigDecimal` intro](days/day03_numbers_operators/LESSON.md) | E-commerce checkout + loan EMI calculator. |
| 4 | Thu 19 Nov | [Strings (Text Processing): methods, `StringBuilder`, `equals` vs `==`](days/day04_strings/LESSON.md) | Instagram signup + caption tools. |
| 5 | Fri 20 Nov | [Decisions: `if/else`, ternary, `switch` expressions, `&&` `\|\|` `!`](days/day05_decisions/LESSON.md) | Delivery-fee rules and ATM checks. |
| 6 | Sat 21 Nov | [Loops: `for`, `while`, `do/while`, enhanced for, `break`, `continue`](days/day06_loops/LESSON.md) | Number-guessing game + PIN retry + processing 1,000 orders. |
| 7 🏆 | Sun 22 Nov | [Week 1 Project: Mini ATM (and Week-1 Review)](days/day07_week1_project_atm/LESSON.md) | An ATM (and every "menu-driven" app). |
| 8 | Mon 23 Nov | [Arrays (1-D, 2-D) and the `Arrays` class](days/day08_arrays/LESSON.md) | A shopping cart, a Spotify playlist, a to-do app. |
| 9 | Tue 24 Nov | [`ArrayList`, `List.of`, wrappers, `HashSet`, `TreeSet`, `Collections`](days/day09_lists_sets/LESSON.md) | Instagram "mutual friends" and "unique visitors". |
| 10 | Wed 25 Nov | [Maps: `HashMap`, `TreeMap`, `LinkedHashMap`, `merge`](days/day10_maps/LESSON.md) | Contact book, inventory, user profile, word counts. |
| 11 | Thu 26 Nov | [Methods: parameters, return, overloading, varargs, recursion](days/day11_methods/LESSON.md) | A billing service. |
| 12 | Fri 27 Nov | [Lambdas, functional interfaces, method references, `Stream` basics](days/day12_lambdas_streams/LESSON.md) | E-commerce filters + music charts. |
| 13 | Sat 28 Nov | [Nested Data, `record`s & JSON-like output](days/day13_nested_data_records/LESSON.md) | A restaurant-listing API (Zomato/Swiggy style). |
| 14 🏆 | Sun 29 Nov | [Week 2 Project: Expense Tracker (and Week-2 Review)](days/day14_week2_project_expense_tracker/LESSON.md) | A personal-finance app (Splitwise / Google Pay "Spends"). |
| 15 | Mon 30 Nov | [Files with `java.nio.file`](days/day15_files_nio/LESSON.md) | A server log analyser. |
| 16 | Tue 01 Dec | [CSV & JSON-style Files](days/day16_csv_json_files/LESSON.md) | A sales report from an Excel/ERP export. |
| 17 | Wed 02 Dec | [Exceptions, try-with-resources & `java.util.logging`](days/day17_exceptions_logging/LESSON.md) | A payment service. |
| 18 | Thu 03 Dec | [Packages, `java.time`, the Standard Library, Maven/Gradle basics, JARs](days/day18_packages_stdlib_build_tools/LESSON.md) | A birthday/deadline reminder + a quick analytics helper. |
| 19 | Fri 04 Dec | [OOP I: Classes, Objects, Encapsulation, `toString/equals/hashCode`](days/day19_oop_basics/LESSON.md) | A banking app. |
| 20 | Sat 05 Dec | [OOP II: Inheritance, `interface`, abstract classes, `enum`, `sealed`, `record`](days/day20_oop_advanced/LESSON.md) | An HR/payroll system and a game. |
| 21 🏆 | Sun 06 Dec | [Week 3 Project: Library Management System (and Week-3 Review)](days/day21_week3_project_library_system/LESSON.md) | A public-library / office-asset system. |
| 22 | Mon 07 Dec | [Generics, `Optional`, `Iterator`/`Iterable`, `Function`/`Predicate`](days/day22_generics_optional_iterators/LESSON.md) | Streaming a 10-GB log file, retrying API calls, auto-closing DB connections. |
| 23 | Tue 08 Dec | [Regex (`Pattern/Matcher`), Immutability & Clean Code](days/day23_regex_clean_code/LESSON.md) | Cleaning a messy contact/invoice dump. |
| 24 | Wed 09 Dec | [Testing with JUnit 5 & Git Basics](days/day24_junit_git/LESSON.md) | A shop's discount code broke on Black Friday. |
| 25 | Thu 10 Dec | [Collections Deep-Dive & `Collectors` on `sales.csv`](days/day25_collections_streams_data/LESSON.md) | You're the new analyst at an online store. |
| 26 | Fri 11 Dec | [Streams II: Cleaning, Sorting, Top-N & Text Reports](days/day26_streams_reporting/LESSON.md) | A messy weekly sales export lands on your desk. |
| 27 | Sat 12 Dec | [HTTP & JSON: `HttpClient` against a local server](days/day27_http_json/LESSON.md) | A dashboard that needs live weather/posts/prices. |
| 28 | Sun 13 Dec | [Databases: JDBC & SQL with SQLite](days/day28_jdbc_sql/LESSON.md) | Files don't scale — store and query orders with SQL. |
| 29 🏆 | Mon 14 Dec | [Capstone: Build a Sales Data Pipeline (ETL)](days/day29_capstone_pipeline/LESSON.md) | Every Monday the store emails a messy CSV. |
| 30 🎓 | Tue 15 Dec | [A REST API with `HttpServer`, Spring Boot explained & The Final Exam](days/day30_rest_api_final_exam/LESSON.md) | The mobile-app team needs your data. |

## 3. Weekly milestones — "I can…" checks
| Week | Days | By the end you can… | Milestone |
|---|---|---|---|
| **1 · Foundations** | 1–7 | write a class with `main`, use variables and types, read input with `Scanner`, format text, branch with `if`/`switch`, loop; read a compiler error | 🏆 Mini ATM (interactive, auto-tested with scripted input) |
| **2 · Data structures & methods** | 8–14 | choose between array / `List` / `Set` / `Map`, write overloaded methods, use lambdas and basic streams, model data with records and nested collections | 🏆 Expense Tracker with budget report |
| **3 · Real programs** | 15–21 | read/write files and CSV, handle exceptions, log, use packages and `java.time`, design classes (inheritance, interfaces, enums, records) | 🏆 Library Management System with save/load |
| **4 · Professional toolkit** | 22–30 | generics, `Optional`, regex, **JUnit + Git**, `Collectors`, HTTP client/server, **JDBC + SQL**, ETL pipeline, a REST API | 🏆 Sales pipeline (CLI) + mini REST API + closed-book final exam |

*(Week 4 has 9 days because the plan is exactly 30 days.)*

## 4. A typical 2-hour day
| Min | Step | Notes |
|---|---|---|
| 0–10 | Warm-up recall | From memory — retrieval beats re-reading |
| 10–30 | Lesson | Concept + tiny runnable snippets (use `jshell` for one-liners) |
| 30–60 | Code-along | Type, run, modify, break `Examples.java` |
| 60–105 | Practice | `java Practice.java` — L1 → L2 → L3, hint ladder if stuck |
| 105–115 | Quiz | Closed book; check the answer file |
| 115–120 | Tracker | Status, hours, quiz score, exercise statuses, Bug Journal |

**Best schedule:** one fixed daily slot (same time, phone away). Two 60-minute blocks (e.g. morning learn + evening practice) work as well as one 2-hour block.

## 5. Difficulty design
| Level | Typical skill | Support |
|---|---|---|
| 🟢 L1 Beginner | Apply one concept from today's lesson | Pattern in the lesson; checker messages show expected vs actual |
| 🟡 L2 Intermediate | Combine today's idea with earlier days; handle edge cases | Hint ladder |
| 🔴 L3 Challenge | Multi-step problem, design choices, tricky data | Hint ladder + solution as last resort |
| 🏆 Project | An interactive or end-to-end program that uses the whole week | Review section + checklist |
| 🎓 Final exam | 27 "what does this print / find the bug" questions (closed-book) | Answer key with explanations |

**Spiral difficulty curve:** short, concrete exercises in Week 1 → data-structure puzzles in Week 2 → mini systems in Week 3 → realistic datasets and tools in Week 4.

## 6. The hint ladder (use in order, 10 minutes each)
1. **Direction** — re-read the lesson section named in hint 1; compare the expected output with yours character by character (spaces and `%n` count).
2. **Shape of the answer** — the second `<details>` in `LESSON.md` shows the skeleton (which method, which loop, which collection).
3. **Peek (last resort)** — open `solutions/dayNN_Solution.java`, read **one** task, close it, rewrite it from memory.

Log honestly in the tracker: *Passed alone* · *Passed with hints* · *Viewed solution*. The dashboard shows the split — it is for you, not for a teacher.

## 7. Falling behind? The catch-up protocol (read this *before* you need it)
Life happens. The timeline is strict, so the plan has a built-in recovery system:

1. **Never stop for more than 1 day in a row.** Do the **Minimum Viable Day (60 min)** instead: Lesson (15) → Code-along (25) → *only the L1 and L2 exercises* (15) → Quiz (5). Mark the day **Done**; mark skipped L3 exercises **Not started**.
2. **Weekend buffer:** Days 6, 7, 13, 14, 20, 21, 27, 28 fall on weekends. If you're ≤ 1 day behind, use the weekend slot to finish the missed day's L3 exercises, then do the project.
3. **Behind by 2–3 days:** for each missed day do the Minimum Viable Day (60 min) and spend the saved time in two extra 60-min sessions — one *double day* per weekend.
4. **Behind by 4+ days:** do **not** compress the foundations (Days 1–14). Instead: skip *Level 3 exercises* on Days 15–23 (revisit them after Day 30), and keep the capstone (Day 29) and final exam (Day 30). The dashboard shows "BEHIND by N day(s)" so you notice early.
5. **Ahead of schedule?** Do the stretch goals (Day 29), write JUnit tests for an old project, or start a portfolio idea from the *Projects* sheet. Don't skip ahead to later days — the order matters (Java builds strictly on earlier days).

**"Done" for a day means:** all L1 + L2 exercises pass · quiz ≥ 6/8 (or you reviewed the misses) · tracker updated · one Bug Journal entry.

## 8. Concept coverage map
| Area | Concepts | Days |
|---|---|---|
| **Basics** | `class`/`main`, `println`/`printf`, variables, primitive types, `var`, `Scanner`, casting, operators, `Math`, `BigDecimal` | 1–3 |
| **Text** | `String` methods, immutability, `StringBuilder`, `String.format`, `equals` vs `==`, text blocks, regex | 4, 23 |
| **Control flow** | `if/else`, ternary, `switch` expressions, boolean logic, `for`, `while`, `do/while`, enhanced `for`, `break/continue` | 5–7 |
| **Data structures** | arrays, `ArrayList`, `List.of`, `HashSet`/`TreeSet`, `HashMap`/`TreeMap`/`LinkedHashMap`, wrappers, nested data, copy vs alias, counting/grouping patterns | 8–10, 13 |
| **Methods & functional style** | parameters, return, overloading, varargs, scope, recursion, lambdas, functional interfaces, method references, `Stream` | 11–12, 22 |
| **Records & modelling** | `record`, nested collections, JSON-like output | 13 |
| **Files & data formats** | `Path`, `Files`, CSV, hand-rolled JSON, charsets/encoding | 15–16 |
| **Robustness** | checked vs unchecked exceptions, `try/catch/finally`, custom exceptions, try-with-resources, `java.util.logging`, debugging | 17, 24 |
| **Project structure** | packages, imports, `java.time`, standard library, JARs, Maven/Gradle (`pom.xml`), `-cp` classpath | 18, 29 |
| **OOP** | classes, constructors, `this`, encapsulation, `toString/equals/hashCode`, inheritance, `interface`, abstract classes, polymorphism, `enum`, `sealed`, `record` | 19–21 |
| **Advanced Java** | generics, `Optional`, `Iterator`/`Iterable`, `Function`/`Predicate`, immutability | 22–23 |
| **Quality** | naming, small methods, clean code, JUnit 5 (`@Test`, assertions, parameterized tests), Git | 23–24 |
| **Data analysis** | `Collectors` (`groupingBy`, `counting`, `averagingDouble`), sorting/top-N, cleaning messy data, text reports | 25–26 |
| **Internet & automation** | `HttpClient`, JSON over HTTP, `com.sun.net.httpserver`, status codes | 27, 30 |
| **Databases** | JDBC, `PreparedStatement`, SQL (SELECT, GROUP BY, JOIN), transactions, injection safety | 28 |
| **Putting it together** | ETL pipeline, CLI, reports, REST API, Spring Boot explained | 29–30 |

*Intentionally left for later (≥ intermediate+ topics):* concurrency (`Thread`, `ExecutorService`, `CompletableFuture`), Spring Boot in depth, JPA/Hibernate, Maven/Gradle in depth, Docker, Mockito. Day 30's "where to go next" gives a roadmap.

## 9. Tracking your progress
Open **`java/tracker/JAVA_PROGRESS_TRACKER.xlsx`** (first tab *START HERE*).
- **Dashboard:** progress %, on-track/behind status, hours vs plan, longest streak, exercise & quiz stats, 4 charts.
- **Daily Plan:** the 30 days above with live dates, statuses, hours, quiz scores, per-day exercise counts.
- **Exercise Log:** one row for every graded exercise (L1/L2/L3) — mark *Passed alone / Passed with hints / Viewed solution*.
- **Concept Checklist:** every concept chip from the lessons, confidence 1–5, "can I explain it?".
- **Projects · Weekly Review · Time Log · Bug Journal · Settings.**

Update it for 5 minutes at the end of every session; do the Weekly Review every Sunday (15 min).

## 10. Where to go deeper
Optional extra practice from well-known free resources:
- **The Java Tutorials** (dev.java/learn, Oracle) · **Java 21 API docs** (docs.oracle.com/en/java/javase/21/docs/api) · **Effective Java** (Joshua Bloch)
- **MOOC.fi Java Programming** (University of Helsinki) — free, exercise-driven · **CodingBat Java** — tiny warm-ups · **Exercism Java track** — mentor-style exercises with tests
- **Baeldung** — short, practical articles per topic · **JUnit 5 User Guide** · **SQLite docs** · **Spring Guides** (spring.io/guides)

## 11. After Day 30 — your next 30 days
0. Study the **Java Blueprints** (`java/blueprints/`, or `#/blueprints` in Java Master): reference mini-systems with diagrams, a Java-feature map and runnable code. Rebuild one from its milestones.
1. Re-do the final exam in 2 weeks — your score should go *up*. Put one portfolio project (Projects sheet) on GitHub with a README.
2. Choose a track and learn in this order:
   - **Spring Boot** — REST controllers, dependency injection, `application.properties`, validation; the Day-30 `HttpServer` API becomes a 20-line controller.
   - **Persistence: JPA / Hibernate** (with Spring Data JPA) on PostgreSQL or H2 — entities, repositories, transactions; compare with your Day-28 JDBC code.
   - **Build tools: Maven or Gradle** — dependencies, lifecycle (`mvn test`, `mvn package`), multi-module projects; turn your capstone into a proper project with a `pom.xml`.
   - **Testing: JUnit 5 + Mockito** — mocks and verification, test slices, testing REST endpoints.
   - **Concurrency** — `ExecutorService`, `CompletableFuture`, virtual threads (Java 21), thread-safety (`synchronized`, `ConcurrentHashMap`, atomics).
   - **Docker** — a multi-stage `Dockerfile` for your Spring Boot JAR, `docker compose` with a database, then deploy it.
3. Read other people's code for 20 minutes a day (open-source Java libraries such as Guava or Apache Commons are friendly) — you have the skills now.
4. Curious about the other side? The [Python course](../README.md) teaches the same ideas in 30 days with pandas, FastAPI and data/AI tooling — compare the two versions of each day.
