/* Day 20 - Practice: inheritance, interfaces, abstract classes, enum, sealed types.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
import java.lang.reflect.Modifier;
import java.util.*;
class Practice {
    // ---------------------------------------------------------------------------
    // L1-1 | Animals (inheritance)   (Level 1 - Beginner)
    // Animal (given) has a name, speak() returns "..." and intro() returns "<name> says <speak()>".
    // Write three subclasses (replace the stub line):
    //   Dog(String name)    speak() returns "Woof"
    //   Cat(String name)    speak() returns "Meow"
    //   Parrot(String name, String phrase)   call super(name); speak() returns the phrase
    //   new Dog("Rex").intro()  ->  "Rex says Woof"
    // ---------------------------------------------------------------------------
    static class Animal {
        private final String name;
        Animal(String name) {
            this.name = name;
        }
        String getName() {
            return name;
        }
        String speak() {
            return "...";
        }
        String intro() {
            return name + " says " + speak();
        }
    }
    // TODO: write your code here
    static class Dog extends Animal { Dog(String name) { super(name); } } static class Cat extends Animal { Cat(String name) { super(name); } } static class Parrot extends Animal { Parrot(String name, String phrase) { super(name); } }
    // ---------------------------------------------------------------------------
    // L1-2 | Point (a record)   (Level 1 - Beginner)
    // Write  record Point(double x, double y)  with
    //   a second constructor Point(double x) that uses y = 0   (hint: this(x, 0);)
    //   double distanceTo(Point other)   straight-line distance rounded to 2 decimals
    //   new Point(0, 0).distanceTo(new Point(3, 4))  ->  5.0
    // The record gives you equals, hashCode and toString for free.
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    record Point(double x, double y) { Point(double x) { this(x, 99); } double distanceTo(Point other) { return -1; } }
    // ---------------------------------------------------------------------------
    // L1-3 | Vector (immutable maths)   (Level 1 - Beginner)
    // Java has no operator overloading (no + for your own types), so we write methods.
    // Write  record Vector(int x, int y)  with
    //   Vector plus(Vector other)   adds the two vectors
    //   Vector times(int k)         multiplies both numbers by k
    //   toString() returning  Vector(1, 2)   (instead of the record's Vector[x=1, y=2])
    // Records compare by value, so new Vector(1, 2).equals(new Vector(1, 2)) is already true.
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    record Vector(int x, int y) { Vector plus(Vector other) { return this; } Vector times(int k) { return this; } }
    // ---------------------------------------------------------------------------
    // L2-1 | Payroll (polymorphism)   (Level 2 - Intermediate)
    // Employee (given): pay() returns the salary. Write
    //   Manager(String name, int salary, int bonus)   pay() = salary + bonus (use super.pay())
    //   Intern(String name)                           always paid 10000 (call super(name, 10000))
    //   static int totalPayroll(List<Employee> staff) the sum of pay() of everybody
    // totalPayroll must not care which kind of employee it gets: each object knows its own pay().
    // ---------------------------------------------------------------------------
    static class Employee {
        private final String name;
        private final int salary;
        Employee(String name, int salary) {
            this.name = name;
            this.salary = salary;
        }
        String getName() {
            return name;
        }
        int pay() {
            return salary;
        }
    }
    // TODO: write your code here
    static class Manager extends Employee { Manager(String name, int salary, int bonus) { super(name, salary); } } static class Intern extends Employee { Intern(String name) { super(name, 0); } } static int totalPayroll(List<Employee> staff) { return 0; }
    // ---------------------------------------------------------------------------
    // L2-2 | Notifiers (interface)   (Level 2 - Intermediate)
    // Notifier (given) is an interface: one abstract method send(message), plus a default
    // method shout(message) that sends the message in CAPITAL letters.
    // Write two classes that implement it:
    //   EmailNotifier(String address)   send returns  "Email to <address>: <message>"
    //   SmsNotifier(String phone)       send returns  "SMS to <phone>: <message>" where the
    //                                   message is cut to its first 20 characters
    // and  static List<String> broadcast(List<Notifier> notifiers, String message)
    // which returns what every notifier's send(message) returned, in order.
    // Because Notifier has ONE abstract method, a lambda can be a Notifier too.
    // ---------------------------------------------------------------------------
    interface Notifier {
        String send(String message);
        default String shout(String message) {
            return send(message.toUpperCase());
        }
    }
    // TODO: write your code here
    static class EmailNotifier implements Notifier { EmailNotifier(String address) { } public String send(String message) { return null; } } static class SmsNotifier implements Notifier { SmsNotifier(String phone) { } public String send(String message) { return null; } } static List<String> broadcast(List<Notifier> notifiers, String message) { return null; }
    // ---------------------------------------------------------------------------
    // L2-3 | CupSize (enum)   (Level 2 - Intermediate)
    // Write  enum CupSize  with the constants SMALL, MEDIUM, LARGE (in this order).
    // Each has an extra charge in rupees: SMALL 0, MEDIUM 10, LARGE 20 (a private final int field
    // set by the enum's constructor, e.g. MEDIUM(10)).
    //   int total(int basePrice)          the base price plus the extra charge
    //   static CupSize parse(String text) ignores capitals and spaces around the text:
    //                                     parse(" large ") -> LARGE; unknown text -> IllegalArgumentException
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    enum CupSize { SMALL, MEDIUM, LARGE; int total(int basePrice) { return 0; } static CupSize parse(String text) { return null; } }
    // ---------------------------------------------------------------------------
    // L3-1 | Abstract shapes   (Level 3 - Challenge)
    // Write an ABSTRACT class Shape with
    //   abstract double area();
    //   String describe()   (a normal method that all shapes share) returns
    //                       "<class name> with area <area with 2 decimals>", e.g. "Circle with area 3.14"
    //                       (hint: getClass().getSimpleName() and String.format(Locale.US, "%.2f", ...))
    // and the subclasses Circle(double radius) (area = pi * r * r, rounded to 2 decimals)
    // and Square(double side).
    // Then  static Shape largest(List<Shape> shapes)  returns the shape with the biggest area.
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    static class Shape { double area() { return 0; } String describe() { return null; } } static class Circle extends Shape { Circle(double radius) { } } static class Square extends Shape { Square(double side) { } } static Shape largest(List<Shape> shapes) { return null; }
    // ---------------------------------------------------------------------------
    // L3-2 | Version numbers (Comparable)   (Level 3 - Challenge)
    // Software versions must compare by their NUMBERS, not as text: 1.10.0 is newer than 1.9.5.
    // Write class Version that implements Comparable<Version>:
    //   static Version fromText(String text)  "1.10.2" -> the parts 1, 10, 2 as numbers
    //   int compareTo(Version other)          negative / 0 / positive; compare part by part
    //                                         (when one version is a prefix of the other, the shorter one is smaller)
    //   equals / hashCode                     same parts means equal
    //   toString()                            "Version(1.10.2)"
    // Then Collections.sort(list) and Collections.max(list) work on your versions.
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    static class Version implements Comparable<Version> { static Version fromText(String text) { return null; } public int compareTo(Version other) { return 0; } }
    // ---------------------------------------------------------------------------
    // L3-3 | Payments (sealed types + switch)   (Level 3 - Challenge)
    // Payment (given) is a SEALED interface: only Cash, Upi and Card may implement it.
    // Write two methods with a switch that has one case per type (no default needed:
    // the compiler knows these are all the cases):
    //   static double fee(Payment p)   Cash -> 0, Upi -> 0, Card -> 2% of the amount,
    //                                  but 3% when emiMonths >= 3 (hint: case Card c when c.emiMonths() >= 3)
    //                                  rounded to 2 decimals
    //   static String label(Payment p) Cash -> "Cash Rs. 500.00"
    //                                  Upi  -> "UPI aarav@upi Rs. 250.00"
    //                                  Card -> "Card Rs. 1000.00", or "Card (EMI 6 months) Rs. 1000.00" when emiMonths > 0
    //                                  (amounts with String.format(Locale.US, "%.2f", ...))
    // ---------------------------------------------------------------------------
    sealed interface Payment permits Cash, Upi, Card {
    }
    record Cash(double amount) implements Payment {
    }
    record Upi(double amount, String handle) implements Payment {
    }
    record Card(double amount, int emiMonths) implements Payment {
    }
    static double fee(Payment payment) {
        // TODO: write your code here
        return -1;
    }
    static String label(Payment payment) {
        // TODO: write your code here
        return null;
    }
    // ======================= AUTO-CHECKER (do not edit below) ====================
    static String errorType(Runnable action) {
        try {
            action.run();
        } catch (Throwable e) {
            return e.getClass().getSimpleName();
        }
        return "no error";
    }
    public static void main(String[] args) {
        System.out.println("--- Day 20 checks ---");
        Checker.check("L1-1 Dog / Cat", () -> List.of(new Dog("Rex").intro(), new Cat("Tom").intro(), new Dog("a") instanceof Animal),
                List.of("Rex says Woof", "Tom says Meow", true));
        Checker.check("L1-1 Parrot", () -> List.of(new Parrot("Polly", "Hello!").intro(), new Parrot("P", "x").getName()),
                List.of("Polly says Hello!", "P"));
        Checker.check("L1-1 polymorphism: one loop, three behaviours", () -> {
            List<Animal> zoo = List.of(new Dog("a"), new Cat("b"), new Parrot("c", "hi"), new Animal("d"));
            List<String> sounds = new ArrayList<>();
            for (Animal animal : zoo) {
                sounds.add(animal.speak());
            }
            return sounds;
        }, List.of("Woof", "Meow", "hi", "..."));
        Checker.check("L1-2 Point", () -> List.of(new Point(0, 0).distanceTo(new Point(3, 4)), new Point(1, 1).distanceTo(new Point(2, 2)),
                new Point(5).equals(new Point(5, 0.0)), new Point(1, 2).equals(new Point(1, 2)), new Point(1, 2).equals(new Point(2, 1))),
                List.of(5.0, 1.41, true, true, false));
        Checker.check("L1-3 Vector", () -> List.of(new Vector(1, 2).plus(new Vector(3, 4)).equals(new Vector(4, 6)),
                new Vector(1, 2).times(3).equals(new Vector(3, 6)), new Vector(1, 2).equals(new Vector(1, 2)),
                new Vector(1, 2).equals(new Vector(2, 1))), List.of(true, true, true, false));
        Checker.check("L1-3 Vector toString", () -> new Vector(1, 2).toString(), "Vector(1, 2)");
        Checker.check("L2-1 pay()", () -> {
            List<Employee> team = List.of(new Employee("A", 50000), new Manager("B", 80000, 20000), new Intern("C"));
            List<Integer> pay = new ArrayList<>();
            for (Employee e : team) {
                pay.add(e.pay());
            }
            return pay;
        }, List.of(50000, 100000, 10000));
        Checker.check("L2-1 totalPayroll / inheritance", () -> {
            List<Employee> team = List.of(new Employee("A", 50000), new Manager("B", 80000, 20000), new Intern("C"));
            return List.of(totalPayroll(team), team.get(1) instanceof Employee, team.get(2).getName(), totalPayroll(List.of()));
        }, List.of(160000, true, "C", 0));
        Checker.check("L2-2 EmailNotifier / SmsNotifier", () -> List.of(
                new EmailNotifier("a@b.com").send("Order shipped"),
                new SmsNotifier("98765").send("Order shipped"),
                new SmsNotifier("98765").send("Your order number 1001 is out for delivery")),
                List.of("Email to a@b.com: Order shipped", "SMS to 98765: Order shipped", "SMS to 98765: Your order number 10"));
        Checker.check("L2-2 broadcast (classes and a lambda)", () -> {
            List<Notifier> all = List.of(new EmailNotifier("a@b.com"), new SmsNotifier("98765"), message -> "LOG: " + message);
            return List.of(broadcast(all, "Hi"), broadcast(List.of(), "Hi"), all.get(0).shout("hi"));
        }, List.of(List.of("Email to a@b.com: Hi", "SMS to 98765: Hi", "LOG: Hi"), List.of(), "Email to a@b.com: HI"));
        Checker.check("L2-3 CupSize", () -> List.of(CupSize.values().length, CupSize.SMALL.total(50), CupSize.MEDIUM.total(50),
                CupSize.LARGE.total(50), CupSize.valueOf("MEDIUM").ordinal()), List.of(3, 50, 60, 70, 1));
        Checker.check("L2-3 CupSize.parse", () -> List.of(CupSize.parse("large"), CupSize.parse("  Small "), errorType(() -> CupSize.parse("huge"))),
                List.of(CupSize.LARGE, CupSize.SMALL, "IllegalArgumentException"));
        Checker.check("L3-1 shapes", () -> List.of(new Circle(1).area(), new Square(3).area(), new Circle(1).describe(), new Square(2).describe(),
                largest(List.of(new Square(1), new Circle(2), new Square(3))).getClass().getSimpleName()),
                List.of(3.14, 9.0, "Circle with area 3.14", "Square with area 4.00", "Circle"));
        Checker.check("L3-1 Shape is abstract", () -> Modifier.isAbstract(Shape.class.getModifiers()), true);
        Checker.check("L3-2 Version sorting", () -> {
            List<Version> versions = new ArrayList<>();
            for (String text : new String[]{"1.10.0", "1.9.5", "1.9.10"}) {
                versions.add(Version.fromText(text));
            }
            Collections.sort(versions);
            return List.of(versions.toString(), Collections.max(versions).toString());
        }, List.of("[Version(1.9.5), Version(1.9.10), Version(1.10.0)]", "Version(1.10.0)"));
        Checker.check("L3-2 Version compare / equals", () -> List.of(
                Version.fromText("2.0.0").compareTo(Version.fromText("1.99.99")) > 0,
                Version.fromText("1.2").compareTo(Version.fromText("1.2.0")) < 0,
                Version.fromText("1.2").equals(Version.fromText("1.2")),
                Version.fromText("1.2").equals(Version.fromText("1.3")),
                Version.fromText("1.2").hashCode() == Version.fromText("1.2").hashCode(),
                new HashSet<>(List.of(Version.fromText("3.1"), Version.fromText("3.1"))).size()),
                List.of(true, true, true, false, true, 1));
        Checker.check("L3-3 fee", () -> List.of(fee(new Cash(500)), fee(new Upi(250, "aarav@upi")), fee(new Card(1000, 0)),
                fee(new Card(1000, 6)), fee(new Card(333.33, 1))), List.of(0.0, 0.0, 20.0, 30.0, 6.67));
        Checker.check("L3-3 label", () -> List.of(label(new Cash(500)), label(new Upi(250, "aarav@upi")), label(new Card(1000, 0)),
                label(new Card(1000, 6))),
                List.of("Cash Rs. 500.00", "UPI aarav@upi Rs. 250.00", "Card Rs. 1000.00", "Card (EMI 6 months) Rs. 1000.00"));
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
