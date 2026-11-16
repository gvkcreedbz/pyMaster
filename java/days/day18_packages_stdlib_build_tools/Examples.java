/* Day 18 - Code along: a deadline reminder and a quick analytics helper using the standard library.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.time.DayOfWeek;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.Period;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalAdjusters;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.TreeMap;
import java.util.stream.IntStream;

import static java.lang.Math.sqrt;                 // static import: write sqrt(...) instead of Math.sqrt(...)

class Examples {
    public static void main(String[] args) {
        // ---- 1. Packages and imports: where does a class live? ----
        System.out.println("String lives in:    " + String.class.getPackageName());          // java.lang (imported for you)
        System.out.println("ArrayList lives in: " + ArrayList.class.getPackageName());       // java.util
        System.out.println("LocalDate lives in: " + LocalDate.class.getPackageName());       // java.time
        System.out.println("Our class lives in: '" + Examples.class.getPackageName() + "'"); // '' = the default (no) package
        java.util.Set<String> fullName = new java.util.HashSet<>();   // no import needed if you write the full name
        System.out.println(fullName.isEmpty() + ", sqrt(144) = " + sqrt(144));
        System.out.println("command-line arguments: " + args.length);   // like Python's sys.argv: try  java Examples.java a b

        // ---- 2. java.time: dates without the headaches ----
        LocalDate today = LocalDate.of(2026, 11, 16);        // a fixed "today" keeps our output the same every run
        LocalDate diwali = LocalDate.parse("2026-11-08");    // ISO text yyyy-MM-dd -> LocalDate
        LocalDate xmas = LocalDate.of(2026, 12, 25);
        System.out.println(today.getDayOfWeek() + ", " + today.getMonth() + ", day " + today.getDayOfMonth());
        System.out.println("days to Christmas: " + ChronoUnit.DAYS.between(today, xmas));        // 39
        System.out.println("days since Diwali: " + ChronoUnit.DAYS.between(diwali, today));        // 8
        System.out.println("in 30 days: " + today.plusDays(30) + ", a week ago: " + today.minusWeeks(1));
        System.out.println("today is before Christmas? " + today.isBefore(xmas));
        System.out.println("real clock works too: " + LocalDate.now().isAfter(LocalDate.of(2024, 1, 1)));   // true

        // ---- 3. Pretty dates and Period/Duration ----
        DateTimeFormatter pretty = DateTimeFormatter.ofPattern("dd MMM yyyy", Locale.ENGLISH);
        System.out.println(xmas.format(pretty));                                                // 25 Dec 2026
        System.out.println(LocalDate.parse("16/11/2026", DateTimeFormatter.ofPattern("dd/MM/yyyy")));   // 2026-11-16
        Period age = Period.between(LocalDate.of(2000, 11, 17), today);
        System.out.println("age: " + age.getYears() + " years, " + age.getMonths() + " months, " + age.getDays() + " days");
        Duration shift = Duration.between(LocalTime.of(9, 30), LocalTime.of(17, 45));
        System.out.println("shift: " + shift.toHours() + " h " + shift.toMinutesPart() + " min");   // 8 h 15 min
        LocalDateTime meeting = LocalDateTime.of(2026, 11, 16, 9, 30).plusHours(30);
        System.out.println("meeting moved to " + meeting);                                        // 2026-11-17T15:30
        System.out.println("next Friday: " + today.with(TemporalAdjusters.next(DayOfWeek.FRIDAY)));   // 2026-11-20
        System.out.println("end of month: " + today.with(TemporalAdjusters.lastDayOfMonth()));          // 2026-11-30

        // ---- 4. java.util tools ----
        Random dice = new Random(7);                          // same seed -> same numbers, so tests can repeat
        int roll1 = dice.nextInt(6) + 1;
        int roll2 = dice.nextInt(6) + 1;
        System.out.println("rolls with seed 7: " + roll1 + " " + roll2);
        List<Integer> marks = new ArrayList<>(List.of(72, 95, 88, 60, 95));
        Collections.shuffle(marks, new Random(1));            // a seeded shuffle is repeatable too
        System.out.println(marks.size() + " marks shuffled");
        System.out.println(Collections.frequency(marks, 95) + " students scored 95");
        System.out.println(String.join(" | ", List.of("chai", "samosa", "vada")));
        System.out.println(Objects.requireNonNullElse(null, "default value"));
        System.out.println("-".repeat(3) + " " + Collections.nCopies(3, "ha"));

        var stats = IntStream.of(3, 1, 2, 10).summaryStatistics();         // like Python's statistics module
        System.out.println("min " + stats.getMin() + ", max " + stats.getMax() + ", mean " + stats.getAverage());

        Map<String, Integer> counts = new TreeMap<>();                      // Counter-style counting (Day 10)
        for (String word : "the cat and the hat and the bat".split(" ")) {
            counts.merge(word, 1, Integer::sum);
        }
        System.out.println(counts);                                         // {and=2, bat=1, cat=1, hat=1, the=3}

        // ---- 5. Reading a pom.xml (Maven) with plain String methods ----
        String pom = """
                <project>
                  <groupId>shop</groupId>
                  <artifactId>billing</artifactId>
                  <version>1.2</version>
                  <dependencies>
                    <dependency>
                      <groupId>org.junit.jupiter</groupId>
                      <artifactId>junit-jupiter</artifactId>
                      <version>5.10.2</version>
                    </dependency>
                  </dependencies>
                </project>
                """;
        String open = "<artifactId>";
        int start = pom.indexOf(open) + open.length();
        int end = pom.indexOf("</artifactId>", start);
        System.out.println("this project: " + pom.substring(start, end));       // billing
        int dependencies = pom.split("<dependency>").length - 1;
        System.out.println("dependencies declared: " + dependencies);           // 1

        // ---- 6. Which Java runs this? ----
        System.out.println("Java feature release: " + Runtime.version().feature());
    }
}
