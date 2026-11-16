# 🎓 Day 30 — FINAL EXAM (45 minutes, closed-book)

**Rules:** do NOT run the code, do NOT use AI or notes. Read each snippet carefully and write down exactly what it prints (or the error it raises). 1 point each → **27 points**. The questions mix all four weeks; the *Day* tag tells you which lesson to revisit if you miss one. Four questions are *find the bug*: say what goes wrong (compile error, exception or wrong result).

> Tip: trace the variables on paper. Exact output counts: spaces, brackets and quotes matter.

> A snippet that is only a few lines is the body of `main` (with `java.util.*`, `java.util.stream.*`, `java.util.function.*`, `java.util.regex.*`, `java.time.*` and `java.sql.*` imported). A snippet that starts with `class Main` is a complete program.

After finishing, check `java/solutions/day30_ExamKey.md`, write your score in the tracker and note your weak topics.

---

### Q1. (Day 3) — numbers, casts and char arithmetic
```java
System.out.println(7 / 2 + " " + 7 % 2 + " " + 7 / 2.0 + " " + (int) 3.99 + " " + (char) ('a' + 1) + " " + ('a' + 1));
```
**Your answer:** ______________________

### Q2. (Day 4) — String methods
```java
String s = "Java Rocks";
System.out.println(new StringBuilder(s).reverse().substring(0, 4) + " " + s.toLowerCase().indexOf('o') + " "
        + s.split(" ")[1].charAt(0) + " " + s.substring(5).length());
```
**Your answer:** ______________________

### Q3. (Day 4) — == versus equals
```java
String a = "chai";
String b = new String("chai");
String c = "ch" + "ai";
System.out.println((a == b) + " " + a.equals(b) + " " + (a == c) + " " + (a == b.intern()));
```
**Your answer:** ______________________

### Q4. (Day 4) — String.format
```java
System.out.println(String.format(Locale.US, "%,.2f|%5d|%-6s|%05.1f|%b", 1234.5, 42, "ab", 3.14159, true));
```
**Your answer:** ______________________

### Q5. (Day 5) — switch expression
```java
int day = 6;
String type = switch (day) {
    case 1, 2, 3, 4, 5 -> "weekday";
    case 6, 7 -> {
        String t = "week";
        yield t + "end";
    }
    default -> "invalid";
};
System.out.println(type + " " + (day > 5 ? "rest" : "work"));
```
**Your answer:** ______________________

### Q6. (Day 6) — for loop with a step
```java
for (int i = 10; i > 0; i -= 3) {
    System.out.print(i + " ");
}
System.out.println("done");
```
**Your answer:** ______________________

### Q7. (Day 8) — array aliasing
```java
int[] a = {1, 2, 3};
int[] b = a;
int[] c = a.clone();
b[0] = 99;
System.out.println(Arrays.toString(a) + " " + Arrays.toString(c) + " " + (a == b) + " " + a.equals(c) + " " + Arrays.equals(a, new int[]{99, 2, 3}));
```
**Your answer:** ______________________

### Q8. (Day 9) — List.remove overloads
```java
List<Integer> nums = new ArrayList<>(List.of(5, 3, 8, 1));
nums.remove(1);
nums.remove(Integer.valueOf(8));
nums.add(0, 7);
Collections.sort(nums);
System.out.println(nums + " " + nums.indexOf(5) + " " + nums.contains(3));
```
**Your answer:** ______________________

### Q9. (Day 9) — sets
```java
Set<Integer> a = new TreeSet<>(List.of(1, 2, 3));
Set<Integer> b = new HashSet<>(List.of(2, 3, 4));
a.retainAll(b);
Set<Integer> u = new TreeSet<>(b);
u.addAll(List.of(9, 2));
System.out.println(a + " " + u + " " + new HashSet<>(List.of(1, 1, 2)).size());
```
**Your answer:** ______________________

### Q10. (Day 10) — counting with a map
```java
Map<String, Integer> counts = new TreeMap<>();
for (String w : "a b a c b a".split(" ")) {
    counts.merge(w, 1, Integer::sum);
}
String top = Collections.max(counts.entrySet(), Map.Entry.comparingByValue()).getKey();
System.out.println(counts + " " + top + " " + counts.getOrDefault("z", 0));
```
**Your answer:** ______________________

### Q11. (Day 11) — overloading and varargs
```java
class Main {
    static String show(int x) { return "int"; }
    static String show(long x) { return "long"; }
    static String show(double x) { return "double"; }
    static String show(Object x) { return "object"; }
    static int sum(int... xs) {
        int t = 0;
        for (int x : xs) t += x;
        return t;
    }

    public static void main(String[] args) {
        byte b = 5;
        System.out.println(show(b) + " " + show(5L) + " " + show(2.5f) + " " + show("hi") + " " + sum() + " " + sum(1, 2, 3));
    }
}
```
**Your answer:** ______________________

### Q12. (Day 11) — recursion
```java
class Main {
    static int f(int n) {
        return n <= 1 ? n : f(n - 1) + f(n - 2);
    }

    static String rev(String s) {
        return s.isEmpty() ? "" : rev(s.substring(1)) + s.charAt(0);
    }

    public static void main(String[] args) {
        System.out.println(f(7) + " " + rev("chai"));
    }
}
```
**Your answer:** ______________________

### Q13. (Day 12) — stream pipeline
```java
List<String> words = List.of("kiwi", "apple", "fig", "banana", "cherry");
System.out.println(words.stream().filter(w -> w.length() > 4).map(String::toUpperCase).collect(Collectors.joining("-")) + " "
        + IntStream.rangeClosed(1, 5).map(x -> x * x).sum() + " "
        + words.stream().mapToInt(String::length).max().getAsInt());
```
**Your answer:** ______________________

### Q14. (Day 12) — sorting with comparators
```java
record Person(String name, int age) {}
List<Person> people = new ArrayList<>(List.of(new Person("Ann", 30), new Person("Bob", 25), new Person("Cy", 30)));
people.sort(Comparator.comparingInt(Person::age).reversed().thenComparing(Person::name));
System.out.println(people.stream().map(Person::name).toList() + " " + people.get(0));
```
**Your answer:** ______________________

### Q15. (Day 17) — try / finally
```java
class Main {
    static int f() {
        int x = 1;
        try {
            return x;
        } finally {
            x = 2;
            System.out.println("cleanup " + x);
        }
    }

    public static void main(String[] args) {
        System.out.println(f());
    }
}
```
**Your answer:** ______________________

### Q16. (Day 17) — exception flow
```java
try {
    int n = Integer.parseInt("12x");
    System.out.println("parsed " + n);
} catch (IllegalArgumentException e) {
    System.out.println("bad number: " + e.getClass().getSimpleName());
} catch (RuntimeException e) {
    System.out.println("other");
} finally {
    System.out.println("done");
}
System.out.println("after");
```
**Your answer:** ______________________

### Q17. (Day 18) — java.time
```java
LocalDate d = LocalDate.of(2026, 1, 31);
System.out.println(d.plusMonths(1) + " " + d.getDayOfWeek() + " "
        + java.time.temporal.ChronoUnit.DAYS.between(d, LocalDate.of(2026, 3, 1)) + " " + d.isLeapYear());
```
**Your answer:** ______________________

### Q18. (Day 19) — inheritance and polymorphism
```java
class Main {
    static class Animal {
        String name;

        Animal(String name) {
            this.name = name;
        }

        String sound() {
            return "...";
        }

        @Override
        public String toString() {
            return name + " says " + sound();
        }
    }

    static class Dog extends Animal {
        Dog(String name) {
            super(name);
        }

        @Override
        String sound() {
            return "Woof";
        }
    }

    public static void main(String[] args) {
        Animal a = new Dog("Rex");
        Animal b = new Animal("Tom");
        System.out.println(a + " | " + b);
        System.out.println(a instanceof Dog);
    }
}
```
**Your answer:** ______________________

### Q19. (Day 20) — record, enum and sealed
```java
class Main {
    sealed interface Shape permits Circle, Square {}

    record Circle(int r) implements Shape {}

    record Square(int side) implements Shape {}

    enum Level { LOW, MID, HIGH }

    static int area(Shape s) {
        return switch (s) {
            case Circle c -> 3 * c.r() * c.r();
            case Square q -> q.side() * q.side();
        };
    }

    public static void main(String[] args) {
        System.out.println(area(new Circle(2)) + " " + area(new Square(3)) + " " + new Square(3) + " "
                + new Square(3).equals(new Square(3)) + " " + Level.valueOf("MID").ordinal());
    }
}
```
**Your answer:** ______________________

### Q20. (Day 22) — Optional
```java
Optional<String> a = Optional.of("chai");
Optional<String> b = Optional.empty();
System.out.println(a.map(String::toUpperCase).orElse("none") + " " + b.map(String::length).orElse(-1) + " "
        + b.isPresent() + " " + a.filter(s -> s.length() > 4).isPresent());
```
**Your answer:** ______________________

### Q21. (Day 23) — regex
```java
Matcher m = Pattern.compile("(\\d+)-(\\w+)").matcher("a 12-ab b 7-zz");
List<String> found = new ArrayList<>();
while (m.find()) {
    found.add(m.group(2) + m.group(1));
}
System.out.println(found + " " + "a   b \n c".replaceAll("\\s+", " ") + " " + "2026-11-16".matches("\\d{4}-\\d{2}-\\d{2}"));
```
**Your answer:** ______________________

### Q22. (Day 25) — groupingBy and partitioningBy
```java
List<String> orders = List.of("North:100", "South:50", "North:25", "East:10", "South:5");
Map<String, Integer> totals = orders.stream().collect(Collectors.groupingBy(
        o -> o.split(":")[0], TreeMap::new, Collectors.summingInt(o -> Integer.parseInt(o.split(":")[1]))));
Map<Boolean, Long> parts = orders.stream().collect(Collectors.partitioningBy(o -> o.startsWith("N"), Collectors.counting()));
System.out.println(totals + " " + parts);
```
**Your answer:** ______________________

### Q23. (Day 28) — SQL with JDBC
```java
try (Connection c = DriverManager.getConnection("jdbc:sqlite::memory:");
     Statement st = c.createStatement()) {
    st.executeUpdate("create table t(x int)");
    st.executeUpdate("insert into t values (1), (2), (3)");
    ResultSet rs = st.executeQuery("select sum(x), count(*) from t where x > 1");
    rs.next();
    System.out.println(rs.getInt(1) + " " + rs.getInt(2));
}
```
**Your answer:** ______________________

### Q24. (Day 5) — BUG: lossy conversion
```java
int cups = 3;
int total = cups * 12.5;
System.out.println(total);
```
**Your answer:** ______________________

### Q25. (Day 6) — BUG: =+ instead of +=
```java
int total = 0;
for (int p : new int[]{10, 20, 30}) {
    total =+ p;
}
System.out.println(total);
```
**Your answer:** ______________________

### Q26. (Day 10) — BUG: missing map key
```java
Map<String, Integer> scores = new HashMap<>();
scores.put("alice", 90);
int bob = scores.get("bob");
System.out.println(bob);
```
**Your answer:** ______________________

### Q27. (Day 9) — BUG: changing a list while looping
```java
List<Integer> nums = new ArrayList<>(List.of(1, 2, 2, 3));
for (Integer n : nums) {
    if (n == 2) {
        nums.remove(n);
    }
}
System.out.println(nums);
```
**Your answer:** ______________________
