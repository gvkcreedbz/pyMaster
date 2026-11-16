# ☕ Java Cheatsheet (Java 21 — core language on one page)

Run a file: `java File.java` · try one line: `jshell` · classic: `javac File.java` then `java File`

## Program skeleton & output
```java
import java.util.*;                       // imports go first (java.lang is automatic)

class Hello {                              // one class...
    public static void main(String[] args) {   // ...with a main method = entry point
        System.out.println("Hi");          // print + newline        (statements end with ;)
        System.out.print("no newline");    // print only
        System.out.printf("%s paid %d, change %.2f%n", "Asha", 500, 12.5);   // %s text %d int %f decimal %n newline
        System.out.println(String.format("%-10s|%8.2f|%05d|%,d", "chai", 60.0, 42, 1234567)); // left-pad, width, zeros, thousands
    }
}
// single-line comment      /* multi-line */      /** doc comment */
```

## Variables & types (static typing: the type is fixed at declaration)
```java
int cups = 3;            long big = 10_000_000_000L;      short s = 1;      byte b = 1;     // whole numbers
double price = 59.99;    float f = 1.5f;                                                    // decimals
boolean paid = true;     char grade = 'A';                                                  // true/false, ONE character
String shop = "Chai Point";                                                                 // text (an object, not a primitive)
var total = cups * price;                          // var = compiler infers the type (locals only)
final double GST = 0.18;                           // final = cannot be reassigned (constant)
Integer boxed = 5;  Double d = 2.5;                // wrapper objects (needed inside List/Map; can be null)
```
Defaults of fields: `0`, `0.0`, `false`, `'\0'`, `null`. Local variables have **no** default: assign before use.

## Input (`Scanner`)
```java
Scanner in = new Scanner(System.in);
String name = in.nextLine();                  // a whole line (always text)
int qty = Integer.parseInt(in.nextLine());    // text -> int   (NumberFormatException if not a number)
double p = Double.parseDouble(in.nextLine());
// in.nextInt() leaves the Enter key behind -> follow with in.nextLine()
```

## Operators
`+ - * /` (int / int = **whole number**: `7 / 2 == 3`) · `%` remainder · `++ --` · `+= -= *= /=`
Compare `== != < <= > >=` · logic `&& || !` (short-circuit) · ternary `cond ? a : b`
Casting: `(double) a / b` · `(int) 3.9 == 3` · `Math.round(2.5) == 3` · `Math.abs  Math.max  Math.min  Math.pow  Math.sqrt  Math.floorMod`
Overflow wraps silently (`Integer.MAX_VALUE + 1` is negative). Money: `new BigDecimal("19.99")` and `.add .multiply .setScale(2, RoundingMode.HALF_UP)`.

## Strings (immutable) — compare with `.equals`, never `==`
```java
String s = "Hello, World";
s.length()  s.charAt(0)  s.substring(0, 5)  s.indexOf("o")  s.contains("lo")
s.toUpperCase()  s.toLowerCase()  s.trim()  s.strip()  s.isEmpty()  s.isBlank()
s.replace("l", "L")  s.split(", ")  String.join("-", "a", "b")  "ab".repeat(3)
s.equals("x")  s.equalsIgnoreCase("x")  s.startsWith("He")  s.endsWith("d")  s.compareTo("x")
StringBuilder sb = new StringBuilder();  sb.append("a").append(1).reverse().toString();   // fast concatenation in loops
String box = """
    Text block:
      keeps line breaks and "quotes"
    """;
"x=%d".formatted(5)                                   // String.format shortcut
```

## Decisions
```java
if (x > 0) { ... } else if (x == 0) { ... } else { ... }
String r = (x > 0) ? "yes" : "no";
String label = switch (day) {                   // switch EXPRESSION (no fall-through, no break)
    case "SAT", "SUN" -> "weekend";
    case "FRI"        -> { String t = "almost"; yield t; }   // yield inside a block
    default           -> "weekday";
};
switch (cmd) { case "go": run(); break; default: stop(); }  // old style: needs break!
if (obj instanceof String t && t.length() > 3) { ... }      // pattern matching: t is already a String
```

## Loops
```java
for (int i = 0; i < 5; i++) { }                 // 0..4
for (String item : items) { }                   // enhanced for (arrays and collections)
while (cond) { }          do { } while (cond);  // do-while runs at least once
break;  continue;  outer: for (...) { for (...) { break outer; } }   // labelled break
for (var e : map.entrySet()) { e.getKey(); e.getValue(); }
```

## Arrays (fixed size)
```java
int[] a = new int[5];  int[] b = {3, 1, 2};  int[][] grid = new int[3][4];
a.length   b[0]   b[b.length - 1]
Arrays.toString(b)  Arrays.deepToString(grid)  Arrays.sort(b)  Arrays.fill(a, 7)
Arrays.copyOf(b, 5)  Arrays.equals(x, y)  Arrays.asList(1, 2, 3)  Arrays.stream(b).sum()
```

## Methods
```java
static int add(int a, int b) { return a + b; }                  // modifiers returnType name(params)
static void greet(String... names) { }                          // varargs: greet(), greet("a", "b")
static double area(double r) { return Math.PI * r * r; }
static double area(double w, double h) { return w * h; }        // overloading: same name, different params
// Java passes copies of values; for objects the copy is of the REFERENCE (changes to the object are visible).
```

## Classes, records, enums, interfaces
```java
class Account {
    private double balance;                                     // private field = encapsulation
    Account(double opening) { this.balance = opening; }         // constructor
    void deposit(double amt) { if (amt <= 0) throw new IllegalArgumentException("amount"); balance += amt; }
    double getBalance() { return balance; }
    @Override public String toString() { return "Account[" + balance + "]"; }
}
record Point(int x, int y) { }                                  // immutable data class: p.x(), equals/hashCode/toString free
enum Size { SMALL, MEDIUM, LARGE }                              // fixed set of constants: Size.valueOf("SMALL"), Size.values()
interface Shape { double area(); default String name() { return "shape"; } }
abstract class Animal { abstract String sound(); }
class Dog extends Animal { @Override String sound() { return "Woof"; } }     // inheritance
sealed interface Pay permits Card, Upi { }  record Card(String no) implements Pay { }  record Upi(String id) implements Pay { }
static final int MAX = 10;                                      // static = belongs to the class, not an object
```
`equals` + `hashCode` go together. `==` on objects compares identity. Access: `private` < (package) < `protected` < `public`.

## Exceptions
```java
try {
    int n = Integer.parseInt(text);
} catch (NumberFormatException e) {            // most specific first
    System.out.println("not a number: " + e.getMessage());
} finally {
    System.out.println("always runs");
}
try (var lines = Files.lines(Path.of("a.txt"))) { ... }        // try-with-resources closes automatically
throw new IllegalStateException("bad state");
class OutOfStockException extends Exception { OutOfStockException(String m) { super(m); } }   // checked: must catch or declare `throws`
```

## Lambdas & functional interfaces
```java
Function<Integer, Integer> sq = x -> x * x;             sq.apply(4)
Predicate<String> empty = String::isEmpty;              empty.test("")
Supplier<Double> now = Math::random;                    Consumer<String> out = System.out::println;
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;       Comparator<String> byLen = Comparator.comparing(String::length);
```

## Files (`java.nio.file`)
```java
Path p = Path.of("data", "sales.csv");
Files.exists(p)  Files.readAllLines(p)  Files.readString(p)  Files.writeString(p, "text")  Files.lines(p)
Files.write(p, List.of("a", "b"))  Files.createDirectories(p.getParent())  Files.list(dir)  Files.delete(p)
```

## Math, time, random
```java
Math.floor(2.7)  Math.ceil(2.1)  Math.round(2.5)  Math.hypot(3, 4)
LocalDate d = LocalDate.of(2026, 11, 16);  d.plusDays(30)  d.getDayOfWeek()  ChronoUnit.DAYS.between(a, b)  LocalDateTime.now()
new Random(42).nextInt(6)           // seeded = repeatable      ThreadLocalRandom.current().nextInt(1, 7)
```

## Naming & style (Google/Oracle convention)
`ClassName` (UpperCamel) · `methodName`, `variableName` (lowerCamel) · `CONSTANT_NAME` · `package.lower.case` · 4-space indent · one statement per line · braces even for one-line `if`.

## Handy commands
| Do this | Command |
|---|---|
| Run a file | `java File.java` |
| …with jars | `java -cp "..\..\lib\*" File.java` |
| Compile only | `javac File.java` |
| Show versions | `java -version` · `javac -version` |
| Live experiments | `jshell` (`/exit` to leave) |
| UTF-8 output | `java -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 File.java` |
