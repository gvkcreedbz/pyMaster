# Day 18 — Packages, the Standard Library & Build Tools (java.time, Maven, JARs)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Organise code in packages, use the "batteries included" JDK (`java.time`, `java.util`), and read a Maven `pom.xml` and a JAR | Intermediate |

## 🌍 Real-world scenario & trend
**A birthday/deadline reminder plus a quick analytics helper.** Real projects never rewrite date maths or counting code: they import it. "How many days until the Diwali sale ends?", "How old is this customer?" and "Which are the three most common words in the reviews?" are each a few lines when you know the standard library.

**Why Java?** The JDK ships thousands of ready-made classes, and a huge world of open-source libraries is one line in a build file away. Almost every company project is built by **Maven** or **Gradle**: they download libraries, compile, test and pack the result into a **JAR**. You do not need to master them today. You need to *read* a `pom.xml` without fear. *Coming from Python?* packages are like folders of modules, a `pom.xml` plays the role of `requirements.txt` (and much more), and `java.time` replaces `datetime`.

## 0. Warm-up (5 min) — Day 17 recap
- When does a `finally` block run?  • How do you read a map value safely with a default?

## 1. Concepts (with tiny code)

### 1.1 Packages: folders for classes
A **package** is a named group of classes. The name matches a folder path. By convention it is your reversed website name plus the project: `com.chaipoint.billing`.
```java
// file: shop/billing/Tax.java        <- the folder path equals the package name
package shop.billing;                  // must be the FIRST line

public class Tax {
    public static double gst(double price) { return price * 0.18; }
}
```
`public` makes a class (or method) visible outside its package. Without `package`, a class lives in the *default package* (what all our single-file practice files use).

### 1.2 `import`: use classes from other packages
```java
import java.util.List;               // one class
import java.util.*;                  // every class in java.util (fine for small programs)
import java.time.LocalDate;
import shop.billing.Tax;             // our own class from the package above
import static java.lang.Math.sqrt;   // static import: write sqrt(9) instead of Math.sqrt(9)
```
Everything in `java.lang` (`String`, `Math`, `System`, `Integer`...) is imported for you. You can also skip `import` by writing the full name: `java.util.Set<String> s = new java.util.HashSet<>();`. If two packages have a class with the same name (`java.util.Date` and `java.sql.Date`) use the full name for one of them.

### 1.3 `java.time`: dates and times done right
Old Java had a confusing `Date` class; since Java 8 use `java.time`. All its objects are **immutable** (every change returns a new object).
```java
LocalDate today = LocalDate.of(2026, 11, 16);          // LocalDate.now() gives the real date
LocalDate event = LocalDate.parse("2026-12-25");       // text in yyyy-MM-dd form
long days = ChronoUnit.DAYS.between(today, event);     // 39
today.plusDays(30);                                    // 2026-12-16
today.getDayOfWeek();                                  // MONDAY
today.isBefore(event);                                 // true
Period p = Period.between(LocalDate.of(2000, 11, 17), today);   // p.getYears() = 25, p.getMonths() = 11
```
Format and parse with a pattern. **Always pass a `Locale`** so month names do not change from computer to computer:
```java
DateTimeFormatter pretty = DateTimeFormatter.ofPattern("dd MMM yyyy", Locale.ENGLISH);
event.format(pretty);                                   // 25 Dec 2026
LocalDate.parse("16/11/2026", DateTimeFormatter.ofPattern("dd/MM/yyyy"));   // 2026-11-16
```
Other helpful types: `LocalTime`, `LocalDateTime`, `Duration` (hours/minutes between times), `DayOfWeek`, and `TemporalAdjusters.next(DayOfWeek.FRIDAY)` ("the next Friday").

### 1.4 A tour of the standard library (the ones you will use most)
| Package / class | Use | Example |
|---|---|---|
| `java.time` | dates & times | `LocalDate.parse("2026-11-16")`, `plusDays(7)`, `ChronoUnit.DAYS.between(a, b)` |
| `java.util.Random` | games, sampling | `new Random(42).nextInt(6) + 1` (the seed makes it repeatable) |
| `java.util.Collections` | list helpers | `frequency`, `max`, `shuffle(list, new Random(1))`, `nCopies` |
| `java.util.Objects` | null-safe helpers | `Objects.equals(a, b)`, `Objects.requireNonNullElse(x, "n/a")` |
| `java.util.stream.IntStream` | quick stats | `IntStream.of(3, 1, 2).summaryStatistics()` gives min, max, average |
| `java.lang.Math` | maths | `sqrt`, `ceil`, `floor`, `pow`, `abs`, `floorMod` |
| `java.nio.file` | files | Day 15 |
| `java.util.regex` | text patterns | Day 23 |
| `String.join`, `String.repeat` | text helpers | `String.join(", ", list)` |

Counting words (a `Counter`) and grouping (a `defaultdict`) are the `merge` and `computeIfAbsent` patterns from Day 10.

### 1.5 Compile and run code that uses packages
Single files run with `java Examples.java`. Several files in packages need the classic two steps: `javac` compiles into an output folder, `java -cp` (class path) says where to find the classes.
```powershell
javac -d out shop\billing\Tax.java App.java     # -d out: put the .class files in the folder out\
java -cp out App                                 # -cp out: look for classes inside out\
```
`App.java` starts with `import shop.billing.Tax;` and calls `Tax.gst(100)`. Mistakes here show up as `package shop.billing does not exist` (wrong folder or `-cp`) or `class Tax is public, should be declared in a file named Tax.java`.

### 1.6 A JAR is a zip file of classes
A **JAR** (Java ARchive) packs `.class` files and a `META-INF/MANIFEST.MF` into one file you can share.
```powershell
jar --create --file app.jar --main-class App -C out .    # pack the compiled classes in out\
java -jar app.jar                                        # run it: the manifest names the main class
jar --list --file app.jar                                # see what is inside
```
A library jar (for example `junit.jar`) is used by adding it to the class path: `java -cp "out;lib\junit.jar" App` (on Linux/macOS use `:` instead of `;`).

### 1.7 Maven: `pom.xml` is the project's recipe
**Maven** builds a project from one XML file. You read it top to bottom:
```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>shop</groupId>                    <!-- who: your company/package prefix -->
  <artifactId>billing</artifactId>           <!-- what: the project's name -->
  <version>1.2</version>                     <!-- which version -->
  <properties>
    <maven.compiler.release>21</maven.compiler.release>   <!-- compile for Java 21 -->
  </properties>
  <dependencies>
    <dependency>                             <!-- a library Maven downloads for you -->
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.10.2</version>
      <scope>test</scope>                    <!-- only needed for tests -->
    </dependency>
  </dependencies>
</project>
```
The trio **groupId : artifactId : version** is the address of every library (like a PIN code + street + house number). Maven expects a fixed layout: code in `src/main/java`, tests in `src/test/java`, results in `target/`. Typical commands: `mvn compile`, `mvn test`, `mvn package` (creates `target/billing-1.2.jar`). We do not use Maven in this course; you will meet it the first day at any Java job.

### 1.8 Gradle: the same idea, shorter file
```groovy
plugins { id 'java' }
group = 'shop'
version = '1.2'
dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.2'     // group:artifact:version
}
```
Commands: `gradle build`, `gradle test`. Spring Boot projects (Day 30) use either tool. *Python twin:* `pip install` + `requirements.txt` + `venv`, all in one tool.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button. Then try `java Examples.java hello world` and watch `args.length`. **Optional lab (15 min):** make the `shop/billing/Tax.java` and `App.java` from 1.1-1.2 in a scratch folder, compile with `javac -d out`, run with `java -cp out App`, then make the JAR and run `java -jar app.jar`.

## 3. Common mistakes
- Forgetting `import` (`error: cannot find symbol ... class LocalDate`).
- A `package` line that does not match the folder path.
- `DateTimeFormatter.ofPattern("dd MMM yyyy")` without a `Locale`: month names change with the user's language.
- Using `MM` (month) and `mm` (minute) the wrong way round, or `yyyy` vs `YYYY` (`YYYY` is the week-based year and gives wrong dates around New Year).
- `LocalDate.parse("5/12/2026")`: without a formatter the text must be exactly `yyyy-MM-dd`.
- Forgetting that `java.time` objects never change: `today.plusDays(1);` alone does nothing, use `today = today.plusDays(1);`.
- `new Random()` without a seed in tests: the results change each run. Use `new Random(42)`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Days until an event, pretty date, median & mean |
| L2-1 … L2-4 | 🟡 Intermediate | Most common words, group by length, exact age in years, read a value out of a `pom.xml` |
| L3-1, L3-2 | 🔴 Challenge | All possible teams (recursion), "next Friday" date |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Read the docs page of the class you need (search "Java LocalDate javadoc"). About 90% of the answer is one method: <code>ChronoUnit.DAYS.between</code>, <code>Period.between</code>, <code>TemporalAdjusters.next</code>.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
daysUntil: <code>ChronoUnit.DAYS.between(LocalDate.parse(a), LocalDate.parse(b))</code>. formatDate: <code>LocalDate.parse(text).format(DateTimeFormatter.ofPattern("dd MMM yyyy", Locale.ENGLISH))</code>. medianAndMean: sort a <code>clone()</code>; odd count: middle item, even count: average of the two middle items. mostCommonWords: <code>TreeMap</code> counts, a list of the keys sorted by count (like Day 10), then build <code>"word=count"</code>. groupByLength: <code>computeIfAbsent(word.length(), k -&gt; new ArrayList&lt;&gt;()).add(word)</code>. ageInYears: <code>Period.between(birth, today).getYears()</code>. tagValue: <code>indexOf("&lt;" + tag + "&gt;")</code>, add the length of the tag, <code>indexOf</code> the closing tag, <code>substring</code>, <code>trim</code>; return <code>""</code> if either is <code>-1</code>. possibleTeams: sort the players; for each player <code>i</code> take every team of <code>size - 1</code> from <code>subList(i + 1, n)</code> and put player <code>i</code> in front; <code>size == 0</code> is the base case (one empty team). nextWeekday: <code>DayOfWeek.valueOf(name.toUpperCase())</code> and <code>date.with(TemporalAdjusters.next(day))</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day18_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day18_answers.md`
1. What does the line `package shop.billing;` mean, and where must the file be stored?
2. Which package is imported automatically, and give two classes from it?
3. What do `javac -d out ...` and `java -cp out App` do?
4. What is a JAR file, and which command runs one?
5. In a `pom.xml`, what do `groupId`, `artifactId` and `version` together identify?
6. `LocalDate.of(2026, 11, 16).getDayOfWeek()` gives what? (2026-11-16 is a Monday)
7. Why pass `Locale.ENGLISH` to `DateTimeFormatter.ofPattern("dd MMM yyyy", ...)`?
8. Why use `new Random(42)` instead of `new Random()` in a test?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: Object-Oriented Programming: classes and objects with fields, constructors and `toString`.
