"""Maintainer tool: builds the Java Day 30 final exam and its answer key by COMPILING AND RUNNING every snippet
with the JDK, so the published answers can never be wrong (twin of build_exam.py).

Usage (from the project root):  python _dev_tools/build_exam_java.py
Writes: java/days/day30_rest_api_final_exam/FINAL_EXAM.md and java/solutions/day30_ExamKey.md

A snippet is either
  * a few statements (they are placed inside  public static void main(String[] args) throws Exception { ... } ), or
  * a complete program that starts with `class Main { ... public static void main ... }`.
Default imports for statement snippets: java.util.*, java.util.function.*, java.util.stream.*, java.util.regex.*,
java.time.*, java.sql.* (the sqlite jar from java/lib is on the classpath, like in the portal).
Each snippet declares what it is expected to do: "ok" (prints and exits), "raises" (a runtime exception) or
"compile" (does not compile). The build fails loudly if a snippet behaves differently from its declaration.
"""
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jdk  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "java"
EXAM_FILE = JAVA / "days" / "day30_rest_api_final_exam" / "FINAL_EXAM.md"
KEY_FILE = JAVA / "solutions" / "day30_ExamKey.md"

IMPORTS = ("import java.util.*;\nimport java.util.function.*;\nimport java.util.stream.*;\nimport java.util.regex.*;\n"
           "import java.time.*;\nimport java.sql.*;\n")

# (day tag, topic, expectation, code, explanation)
QUESTIONS = [
    (3, "numbers, casts and char arithmetic", "ok",
     'System.out.println(7 / 2 + " " + 7 % 2 + " " + 7 / 2.0 + " " + (int) 3.99 + " " + (char) (\'a\' + 1) + " " + (\'a\' + 1));',
     "`7 / 2` is whole-number division (3), `%` is the remainder, `7 / 2.0` is a double. `(int) 3.99` cuts the decimals (no rounding). "
     "`'a' + 1` is an `int` (98); casting it back with `(char)` gives `b`."),
    (4, "String methods", "ok",
     'String s = "Java Rocks";\n'
     'System.out.println(new StringBuilder(s).reverse().substring(0, 4) + " " + s.toLowerCase().indexOf(\'o\') + " "\n'
     '        + s.split(" ")[1].charAt(0) + " " + s.substring(5).length());',
     "The reversed text is `skcoR avaJ`, its first 4 characters are `skco`. In `java rocks` the first `o` is at index 6. "
     "`split(\" \")[1]` is `Rocks`, its `charAt(0)` is `R`, and `substring(5)` is `Rocks` (length 5)."),
    (4, "== versus equals", "ok",
     'String a = "chai";\nString b = new String("chai");\nString c = "ch" + "ai";\n'
     'System.out.println((a == b) + " " + a.equals(b) + " " + (a == c) + " " + (a == b.intern()));',
     "`new String(...)` creates a separate object, so `a == b` is false while `equals` compares the text. `\"ch\" + \"ai\"` is joined by the "
     "compiler into the same shared literal, so `a == c` is true, and `intern()` returns that shared literal. Always use `equals` for text."),
    (4, "String.format", "ok",
     'System.out.println(String.format(Locale.US, "%,.2f|%5d|%-6s|%05.1f|%b", 1234.5, 42, "ab", 3.14159, true));',
     "`%,.2f` adds thousands separators and 2 decimals; `%5d` right-aligns in 5 characters; `%-6s` left-aligns in 6; "
     "`%05.1f` pads with zeros to width 5 with one decimal; `%b` prints a boolean."),
    (5, "switch expression", "ok",
     'int day = 6;\nString type = switch (day) {\n    case 1, 2, 3, 4, 5 -> "weekday";\n    case 6, 7 -> {\n        String t = "week";\n'
     '        yield t + "end";\n    }\n    default -> "invalid";\n};\nSystem.out.println(type + " " + (day > 5 ? "rest" : "work"));',
     "A `switch` expression gives a value. A block branch returns it with `yield`. `6` matches `case 6, 7`, so the type is `weekend`, "
     "and the ternary chooses `rest` because `6 > 5`."),
    (6, "for loop with a step", "ok",
     'for (int i = 10; i > 0; i -= 3) {\n    System.out.print(i + " ");\n}\nSystem.out.println("done");',
     "`i` starts at 10 and loses 3 each time while it is above 0: 10, 7, 4, 1 (the next value, -2, fails the test). `print` does not end the line."),
    (8, "array aliasing", "ok",
     'int[] a = {1, 2, 3};\nint[] b = a;\nint[] c = a.clone();\nb[0] = 99;\n'
     'System.out.println(Arrays.toString(a) + " " + Arrays.toString(c) + " " + (a == b) + " " + a.equals(c) + " " + Arrays.equals(a, new int[]{99, 2, 3}));',
     "`b = a` makes two names for the *same* array, so changing `b[0]` changes `a`. `clone()` makes a copy, so `c` keeps `1`. "
     "`==` and `equals` on arrays compare identity (false for the copy), `Arrays.equals` compares the contents."),
    (9, "List.remove overloads", "ok",
     'List<Integer> nums = new ArrayList<>(List.of(5, 3, 8, 1));\nnums.remove(1);\nnums.remove(Integer.valueOf(8));\nnums.add(0, 7);\n'
     'Collections.sort(nums);\nSystem.out.println(nums + " " + nums.indexOf(5) + " " + nums.contains(3));',
     "`remove(1)` with an `int` removes the item at index 1 (the 3). `remove(Integer.valueOf(8))` removes the *value* 8. "
     "After `add(0, 7)` the list is `[7, 5, 1]`, sorted `[1, 5, 7]`; `5` sits at index 1 and `3` is gone."),
    (9, "sets", "ok",
     'Set<Integer> a = new TreeSet<>(List.of(1, 2, 3));\nSet<Integer> b = new HashSet<>(List.of(2, 3, 4));\na.retainAll(b);\n'
     'Set<Integer> u = new TreeSet<>(b);\nu.addAll(List.of(9, 2));\n'
     'System.out.println(a + " " + u + " " + new HashSet<>(List.of(1, 1, 2)).size());',
     "`retainAll` keeps only the common items (intersection), so `a` becomes `[2, 3]`. A `TreeSet` prints in sorted order and `addAll` ignores "
     "values it already has (the `2`). A `HashSet` copy of the list `[1, 1, 2]` holds only 2 distinct values."),
    (10, "counting with a map", "ok",
     'Map<String, Integer> counts = new TreeMap<>();\nfor (String w : "a b a c b a".split(" ")) {\n    counts.merge(w, 1, Integer::sum);\n}\n'
     'String top = Collections.max(counts.entrySet(), Map.Entry.comparingByValue()).getKey();\n'
     'System.out.println(counts + " " + top + " " + counts.getOrDefault("z", 0));',
     "`merge(w, 1, Integer::sum)` starts a count at 1 or adds 1. A `TreeMap` prints its keys sorted. `Collections.max` with "
     "`comparingByValue()` finds the entry with the biggest count. `getOrDefault` gives 0 for a missing key."),
    (11, "overloading and varargs", "ok",
     'class Main {\n    static String show(int x) { return "int"; }\n    static String show(long x) { return "long"; }\n'
     '    static String show(double x) { return "double"; }\n    static String show(Object x) { return "object"; }\n'
     '    static int sum(int... xs) {\n        int t = 0;\n        for (int x : xs) t += x;\n        return t;\n    }\n\n'
     '    public static void main(String[] args) {\n        byte b = 5;\n'
     '        System.out.println(show(b) + " " + show(5L) + " " + show(2.5f) + " " + show("hi") + " " + sum() + " " + sum(1, 2, 3));\n    }\n}',
     "Java picks the most specific overload, widening a primitive if needed: `byte` widens to `int`, `float` widens to `double`. "
     "A `String` only fits `Object`. A varargs method can be called with no arguments (sum 0) or many."),
    (11, "recursion", "ok",
     'class Main {\n    static int f(int n) {\n        return n <= 1 ? n : f(n - 1) + f(n - 2);\n    }\n\n'
     '    static String rev(String s) {\n        return s.isEmpty() ? "" : rev(s.substring(1)) + s.charAt(0);\n    }\n\n'
     '    public static void main(String[] args) {\n        System.out.println(f(7) + " " + rev("chai"));\n    }\n}',
     "`f` is the Fibonacci sequence 0, 1, 1, 2, 3, 5, 8, 13 so `f(7)` is 13. `rev` moves the first character behind the reversed rest: `iahc`."),
    (12, "stream pipeline", "ok",
     'List<String> words = List.of("kiwi", "apple", "fig", "banana", "cherry");\n'
     'System.out.println(words.stream().filter(w -> w.length() > 4).map(String::toUpperCase).collect(Collectors.joining("-")) + " "\n'
     '        + IntStream.rangeClosed(1, 5).map(x -> x * x).sum() + " "\n'
     '        + words.stream().mapToInt(String::length).max().getAsInt());',
     "Words longer than 4 letters are `apple`, `banana`, `cherry`, upper-cased and joined with `-`. The squares 1+4+9+16+25 add up to 55. "
     "The longest word has 6 letters."),
    (12, "sorting with comparators", "ok",
     'record Person(String name, int age) {}\n'
     'List<Person> people = new ArrayList<>(List.of(new Person("Ann", 30), new Person("Bob", 25), new Person("Cy", 30)));\n'
     'people.sort(Comparator.comparingInt(Person::age).reversed().thenComparing(Person::name));\n'
     'System.out.println(people.stream().map(Person::name).toList() + " " + people.get(0));',
     "The comparator sorts by age from high to low, then by name A-Z for ties (Ann before Cy), so Bob is last. "
     "A record prints as `Name[field=value, ...]`."),
    (17, "try / finally", "ok",
     'class Main {\n    static int f() {\n        int x = 1;\n        try {\n            return x;\n        } finally {\n'
     '            x = 2;\n            System.out.println("cleanup " + x);\n        }\n    }\n\n'
     '    public static void main(String[] args) {\n        System.out.println(f());\n    }\n}',
     "`finally` always runs before the method really returns, so `cleanup 2` prints first. The return value was already copied "
     "(`1`) when `return x` ran, so changing `x` in `finally` does not change what is returned."),
    (17, "exception flow", "ok",
     'try {\n    int n = Integer.parseInt("12x");\n    System.out.println("parsed " + n);\n} catch (IllegalArgumentException e) {\n'
     '    System.out.println("bad number: " + e.getClass().getSimpleName());\n} catch (RuntimeException e) {\n    System.out.println("other");\n} finally {\n'
     '    System.out.println("done");\n}\nSystem.out.println("after");',
     "`parseInt(\"12x\")` throws `NumberFormatException`, which is a subclass of `IllegalArgumentException`, so the first matching `catch` runs. "
     "`finally` runs, then the program continues after the `try`."),
    (18, "java.time", "ok",
     'LocalDate d = LocalDate.of(2026, 1, 31);\n'
     'System.out.println(d.plusMonths(1) + " " + d.getDayOfWeek() + " "\n'
     '        + java.time.temporal.ChronoUnit.DAYS.between(d, LocalDate.of(2026, 3, 1)) + " " + d.isLeapYear());',
     "`plusMonths(1)` from 31 January lands on the last valid day, 28 February (2026 is not a leap year). 31 January 2026 is a Saturday. "
     "From 31 Jan to 1 March are 29 days. Dates are immutable: every method returns a new `LocalDate`."),
    (19, "inheritance and polymorphism", "ok",
     'class Main {\n    static class Animal {\n        String name;\n\n        Animal(String name) {\n            this.name = name;\n        }\n\n'
     '        String sound() {\n            return "...";\n        }\n\n        @Override\n        public String toString() {\n'
     '            return name + " says " + sound();\n        }\n    }\n\n    static class Dog extends Animal {\n'
     '        Dog(String name) {\n            super(name);\n        }\n\n        @Override\n        String sound() {\n            return "Woof";\n        }\n    }\n\n'
     '    public static void main(String[] args) {\n        Animal a = new Dog("Rex");\n        Animal b = new Animal("Tom");\n'
     '        System.out.println(a + " | " + b);\n        System.out.println(a instanceof Dog);\n    }\n}',
     "The variable type is `Animal`, but the object is a `Dog`, so `sound()` runs the `Dog` version (polymorphism). "
     "`toString()` is called automatically when an object is joined to text."),
    (20, "record, enum and sealed", "ok",
     'class Main {\n    sealed interface Shape permits Circle, Square {}\n\n    record Circle(int r) implements Shape {}\n\n    record Square(int side) implements Shape {}\n\n'
     '    enum Level { LOW, MID, HIGH }\n\n    static int area(Shape s) {\n        return switch (s) {\n'
     '            case Circle c -> 3 * c.r() * c.r();\n            case Square q -> q.side() * q.side();\n        };\n    }\n\n'
     '    public static void main(String[] args) {\n        System.out.println(area(new Circle(2)) + " " + area(new Square(3)) + " " + new Square(3) + " "\n'
     '                + new Square(3).equals(new Square(3)) + " " + Level.valueOf("MID").ordinal());\n    }\n}',
     "A `switch` over a sealed type needs no `default`: the compiler knows every case. A circle of radius 2 gives 3*2*2 = 12, a square of side 3 gives 9. "
     "Records get `toString` and `equals` (same values = equal) for free. Enum constants are numbered from 0, so `MID` is 1."),
    (22, "Optional", "ok",
     'Optional<String> a = Optional.of("chai");\nOptional<String> b = Optional.empty();\n'
     'System.out.println(a.map(String::toUpperCase).orElse("none") + " " + b.map(String::length).orElse(-1) + " "\n'
     '        + b.isPresent() + " " + a.filter(s -> s.length() > 4).isPresent());',
     "`map` transforms the value only when there is one. An empty `Optional` skips `map` and uses the `orElse` default (-1). "
     "`\"chai\"` has 4 letters, so `filter(length > 4)` removes it and the Optional becomes empty."),
    (23, "regex", "ok",
     'Matcher m = Pattern.compile("(\\\\d+)-(\\\\w+)").matcher("a 12-ab b 7-zz");\nList<String> found = new ArrayList<>();\nwhile (m.find()) {\n'
     '    found.add(m.group(2) + m.group(1));\n}\n'
     'System.out.println(found + " " + "a   b \\n c".replaceAll("\\\\s+", " ") + " " + "2026-11-16".matches("\\\\d{4}-\\\\d{2}-\\\\d{2}"));',
     "Each match has group 1 (digits) and group 2 (word); the code glues them back in the order 2 then 1: `ab12`, `zz7`. `\\s+` matches any run of "
     "white space (spaces and the new line) and is replaced by one space. `matches` must match the whole text, which the date does."),
    (25, "groupingBy and partitioningBy", "ok",
     'List<String> orders = List.of("North:100", "South:50", "North:25", "East:10", "South:5");\n'
     'Map<String, Integer> totals = orders.stream().collect(Collectors.groupingBy(\n'
     '        o -> o.split(":")[0], TreeMap::new, Collectors.summingInt(o -> Integer.parseInt(o.split(":")[1]))));\n'
     'Map<Boolean, Long> parts = orders.stream().collect(Collectors.partitioningBy(o -> o.startsWith("N"), Collectors.counting()));\n'
     'System.out.println(totals + " " + parts);',
     "`groupingBy` with a `TreeMap` gives the totals per region in sorted order (North 100+25, South 50+5). `partitioningBy` always has both keys, "
     "`false` first: 3 orders do not start with N, 2 do."),
    (28, "SQL with JDBC", "ok",
     'try (Connection c = DriverManager.getConnection("jdbc:sqlite::memory:");\n     Statement st = c.createStatement()) {\n'
     '    st.executeUpdate("create table t(x int)");\n    st.executeUpdate("insert into t values (1), (2), (3)");\n'
     '    ResultSet rs = st.executeQuery("select sum(x), count(*) from t where x > 1");\n    rs.next();\n'
     '    System.out.println(rs.getInt(1) + " " + rs.getInt(2));\n}',
     "`WHERE x > 1` keeps 2 and 3, so the sum is 5 and the count is 2. A `ResultSet` starts *before* the first row: call `next()` before reading. "
     "The `:memory:` database disappears when the connection closes."),
    (5, "BUG: lossy conversion", "compile",
     'int cups = 3;\nint total = cups * 12.5;\nSystem.out.println(total);',
     "`cups * 12.5` is a `double` and Java refuses to squeeze it into an `int` without your permission, so the file does not compile. "
     "Fix: `double total = cups * 12.5;` or an explicit cast `(int) (cups * 12.5)` if you really want to cut the decimals."),
    (6, "BUG: =+ instead of +=", "ok",
     'int total = 0;\nfor (int p : new int[]{10, 20, 30}) {\n    total =+ p;\n}\nSystem.out.println(total);',
     "`=+ p` is parsed as `= +p`: assign the positive number. Every pass replaces `total`, so only the last item is left. "
     "Fix: `total += p;` (expected 60)."),
    (10, "BUG: missing map key", "raises",
     'Map<String, Integer> scores = new HashMap<>();\nscores.put("alice", 90);\nint bob = scores.get("bob");\nSystem.out.println(bob);',
     "`get(\"bob\")` returns `null` for a missing key, and unboxing `null` into an `int` throws `NullPointerException`. "
     "Fix: `scores.getOrDefault(\"bob\", 0)` or check `containsKey` first."),
    (9, "BUG: changing a list while looping", "raises",
     'List<Integer> nums = new ArrayList<>(List.of(1, 2, 2, 3));\nfor (Integer n : nums) {\n    if (n == 2) {\n        nums.remove(n);\n    }\n}\nSystem.out.println(nums);',
     "Removing from a list inside an enhanced `for` loop changes it under the loop's feet, and the iterator notices on the next step: "
     "`ConcurrentModificationException`. Fix: `nums.removeIf(n -> n == 2);` or loop over a copy."),
]


def wrap(code: str) -> str:
    """Complete programs stay as they are; statement snippets go into main()."""
    if code.lstrip().startswith("class Main"):
        return IMPORTS + code + "\n"
    body = "\n".join("        " + line if line else line for line in code.splitlines())
    return IMPORTS + "class Main {\n    public static void main(String[] args) throws Exception {\n" + body + "\n    }\n}\n"


def run(code: str) -> tuple[str, str]:
    """Compile and run one snippet. Returns (kind, text) where kind is ok / raises / compile and text is what to show."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "Main.java"
        source.write_text(wrap(code), encoding="utf-8", newline="\n")
        result = jdk.run_file(source, Path(tmp))
    out = result.stdout.replace("\r\n", "\n").rstrip("\n")
    err = result.stderr.replace("\r\n", "\n")
    compile_error = re.search(r"error: (.+)", err)
    if result.returncode != 0 and "Exception in thread" not in err:
        return "compile", f"<does not compile: {compile_error.group(1) if compile_error else err.strip()[:200]}>"
    raised = re.search(r'Exception in thread "[^"]+" ([\w.$]+)', err)
    if result.returncode != 0 and raised:
        name = raised.group(1).rsplit(".", 1)[-1]
        return "raises", (out + "\n" if out else "") + f"<raises {name}>"
    if result.returncode != 0:
        raise SystemExit(f"snippet failed unexpectedly:\n{code}\n{err}")
    return "ok", out


def main() -> None:
    assert len(QUESTIONS) == 27, f"the exam needs 27 questions, found {len(QUESTIONS)}"
    exam = ["# 🎓 Day 30 — FINAL EXAM (45 minutes, closed-book)\n",
            "**Rules:** do NOT run the code, do NOT use AI or notes. Read each snippet carefully and write down exactly what it prints "
            "(or the error it raises). 1 point each → **27 points**. The questions mix all four weeks; the *Day* tag tells you which lesson "
            "to revisit if you miss one. Four questions are *find the bug*: say what goes wrong (compile error, exception or wrong result).\n",
            "> Tip: trace the variables on paper. Exact output counts: spaces, brackets and quotes matter.\n",
            "> A snippet that is only a few lines is the body of `main` (with `java.util.*`, `java.util.stream.*`, `java.util.function.*`, `java.util.regex.*`, "
            "`java.time.*` and `java.sql.*` imported). A snippet that starts with `class Main` is a complete program.\n",
            "After finishing, check `java/solutions/day30_ExamKey.md`, write your score in the tracker and note your weak topics.\n", "---\n"]
    key = ["# Day 30 — Final Exam answer key\n",
           "Every output below was produced by actually compiling and running the code with the JDK (via `_dev_tools/build_exam_java.py`).\n",
           "Scoring (out of 27): 24–27 🏆 · 19–23 ✅ · 13–18 🟡 · <13 🔁 (see LESSON.md).\n", "---\n"]
    for number, (day, topic, expect, code, why) in enumerate(QUESTIONS, 1):
        kind, output = run(code)
        if kind != expect:
            raise SystemExit(f"Q{number} ({topic}) was declared '{expect}' but behaved like '{kind}':\n{output}")
        exam.append(f"### Q{number}. (Day {day}) — {topic}\n```java\n{code}\n```\n**Your answer:** ______________________\n")
        key.append(f"### Q{number}. (Day {day}) — {topic}\n```text\n{output}\n```\n{why}\n")
    EXAM_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXAM_FILE.write_text("\n".join(exam), encoding="utf-8", newline="\n")
    KEY_FILE.write_text("\n".join(key), encoding="utf-8", newline="\n")
    print(f"Wrote exam with {len(QUESTIONS)} questions and answer key.")


if __name__ == "__main__":
    main()
