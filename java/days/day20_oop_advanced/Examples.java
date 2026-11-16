/* Day 20 - Code along: payroll, notifications and a cafe menu (inheritance, interfaces, enum, sealed).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.*;
class Examples {
    // ---- 1. Inheritance: Manager IS-A Employee ----
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
    static class Manager extends Employee {
        private final int bonus;
        Manager(String name, int salary, int bonus) {
            super(name, salary);               // reuse the parent's setup FIRST
            this.bonus = bonus;
        }
        @Override
        int pay() {                            // override: same signature, new behaviour
            return super.pay() + bonus;
        }
    }
    // ---- 2. Interface: a promise of what a class can do ----
    interface Notifier {
        String send(String message);
        default String shout(String message) {      // a ready-made method every Notifier gets
            return send(message.toUpperCase());
        }
    }
    static class Email implements Notifier {
        public String send(String message) {
            return "Email: " + message;
        }
    }
    static class Sms implements Notifier {
        public String send(String message) {
            return "SMS: " + message;
        }
    }
    // ---- 3. Abstract class: shared code + methods the children MUST write ----
    abstract static class Shape {
        abstract double area();
        String describe() {
            return getClass().getSimpleName() + " area " + String.format(Locale.US, "%.2f", area());
        }
    }
    static class Square extends Shape {
        private final double side;
        Square(double side) {
            this.side = side;
        }
        double area() {
            return side * side;
        }
    }
    static class Circle extends Shape {
        private final double radius;
        Circle(double radius) {
            this.radius = radius;
        }
        double area() {
            return Math.PI * radius * radius;
        }
    }
    // ---- 4. enum: a fixed list of choices that can carry data ----
    enum CupSize {
        SMALL(0), MEDIUM(10), LARGE(20);
        private final int extra;
        CupSize(int extra) {
            this.extra = extra;
        }
        int total(int base) {
            return base + extra;
        }
    }
    // ---- 5. sealed + record: a closed family of cases ----
    sealed interface Payment permits Cash, Upi {
    }
    record Cash(int amount) implements Payment {
    }
    record Upi(int amount, String handle) implements Payment {
    }
    static String receipt(Payment payment) {
        return switch (payment) {                    // no default: the compiler checks every case is covered
            case Cash c -> "Paid Rs. " + c.amount() + " in cash";
            case Upi u -> "Paid Rs. " + u.amount() + " by UPI (" + u.handle() + ")";
        };
    }
    // ---- 6. Comparable: tell Java how to sort your objects ----
    record Version(int major, int minor) implements Comparable<Version> {
        @Override
        public int compareTo(Version other) {
            if (major != other.major) {
                return Integer.compare(major, other.major);
            }
            return Integer.compare(minor, other.minor);
        }
    }
    public static void main(String[] args) {
        // ---- 1. Polymorphism: same call, different behaviour ----
        System.out.println("1. Inheritance and polymorphism");
        List<Employee> staff = List.of(new Employee("Asha", 50000), new Manager("Ravi", 80000, 20000));
        int total = 0;
        for (Employee e : staff) {
            System.out.println("  " + e.getName() + " earns " + e.pay());   // each object runs its OWN pay()
            total += e.pay();
        }
        System.out.println("  payroll: " + total);
        System.out.println("  Ravi is an Employee: " + (staff.get(1) instanceof Employee));
        // ---- 2. Interfaces ----
        System.out.println("2. Interface");
        List<Notifier> channels = List.of(new Email(), new Sms(), message -> "LOG: " + message);   // a lambda is a Notifier too
        for (Notifier n : channels) {
            System.out.println("  " + n.send("Order shipped"));
        }
        System.out.println("  " + channels.get(0).shout("sale today"));
        // ---- 3. Abstract classes ----
        System.out.println("3. Abstract class");
        List<Shape> shapes = List.of(new Square(3), new Circle(1));
        for (Shape s : shapes) {
            System.out.println("  " + s.describe());
        }
        // new Shape();   // will NOT compile: Shape is abstract
        // ---- 4. enum ----
        System.out.println("4. enum");
        for (CupSize size : CupSize.values()) {
            System.out.println("  " + size + " chai costs " + size.total(20));
        }
        CupSize chosen = CupSize.valueOf("MEDIUM");
        String mood = switch (chosen) {
            case SMALL -> "just a sip";
            case MEDIUM -> "a good cup";
            case LARGE -> "big thirst";
        };
        System.out.println("  " + chosen + " (number " + chosen.ordinal() + ") is " + mood);
        // ---- 5. sealed ----
        System.out.println("5. sealed types");
        System.out.println("  " + receipt(new Cash(250)));
        System.out.println("  " + receipt(new Upi(900, "diya@upi")));
        // ---- 6. Comparable and records ----
        System.out.println("6. Comparable");
        List<Version> versions = new ArrayList<>(List.of(new Version(1, 10), new Version(1, 9), new Version(0, 99)));
        Collections.sort(versions);
        System.out.println("  " + versions);
        System.out.println("  same value: " + new Version(1, 9).equals(new Version(1, 9)));
        // ---- 7. HAS-A (composition) ----
        System.out.println("7. Composition: a Car HAS an Engine");
        class Engine {
            String start() {
                return "vroom";
            }
        }
        class Car {
            private final Engine engine = new Engine();      // a field, not a parent class
            String drive() {
                return "Car goes " + engine.start();
            }
        }
        System.out.println("  " + new Car().drive());
    }
}
