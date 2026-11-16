# Day 20 — OOP II: Inheritance, Interfaces, Abstract Classes, Enums & Sealed Types
| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Reuse code with inheritance, program against interfaces, model fixed choices with `enum`/`sealed`, and make objects sortable | Intermediate → Upper-intermediate |
## 🌍 Real-world scenario & trend
**An HR/payroll system and a notification service.** Employees, managers and interns are all "employees" but are paid differently; an app can alert you by e-mail, SMS or push and the code that sends the alert should not care which. Frameworks (Spring, JDBC, JUnit, Android) ask you to *implement an interface* or *extend a class* and override a method.
**Why Java?** Interfaces and polymorphism are the heart of Java design: a `List` can be an `ArrayList` or a `LinkedList`, and your code does not change. **Trend:** modern Java (17-21) prefers **composition over deep inheritance**, `record`s for data, and `sealed` types with `switch` so the compiler proves you handled every case. *Coming from Python?* There is no operator overloading: `__str__` is `toString()`, `__eq__` is `equals()`, `__lt__` is `compareTo()`, and `@dataclass` is `record`.
## 0. Warm-up (5 min) — Day 19 recap
- What does `this` mean?  • Why are fields `private`?  • Which method must you write together with `equals`?
## 1. Concepts (with tiny code)
### 1.1 Inheritance, `extends` and `super`
```java
class Employee {
    private final String name; private final int salary;
    Employee(String name, int salary) { this.name = name; this.salary = salary; }
    int pay() { return salary; }
}
class Manager extends Employee {                // Manager IS-A Employee
    private final int bonus;
    Manager(String name, int salary, int bonus) {
        super(name, salary);                    // run the parent's constructor first
        this.bonus = bonus;
    }
    @Override
    int pay() { return super.pay() + bonus; }   // override: same signature, new behaviour
}
```
A class can extend **only one** parent. If the parent has no empty constructor, the child **must** call `super(...)` on its first line. `private` members are not visible to children; use `super.pay()` or a getter.
### 1.2 Polymorphism: same call, different behaviour
```java
List<Employee> staff = List.of(new Employee("Asha", 50000), new Manager("Ravi", 80000, 20000));
for (Employee e : staff) System.out.println(e.pay());   // 50000, then 100000
```
The variable's type is `Employee`, but Java runs the `pay()` of the **real** object at run time. `staff.get(1) instanceof Employee` is `true` for a manager too.
### 1.3 Interfaces: a promise of behaviour
```java
interface Notifier {
    String send(String message);                         // abstract: no body
    default String shout(String m) { return send(m.toUpperCase()); }   // ready-made extra
}
class Email implements Notifier {
    public String send(String message) { return "Email: " + message; }   // must be public
}
Notifier n = new Email();                 // program against the INTERFACE type
Notifier log = message -> "LOG: " + message;   // one abstract method, so a lambda works (Day 12)
```
A class can implement **many** interfaces. Interface methods are `public` automatically, so the implementing method must say `public`.
### 1.4 Abstract classes: shared code + "you must write this part"
```java
abstract class Shape {
    abstract double area();                               // children MUST implement it
    String describe() { return getClass().getSimpleName() + " " + area(); }   // shared by all
}
// new Shape();   // compile error: an abstract class cannot be created
```
**Interface or abstract class?** An interface says *what* something can do (no fields). An abstract class is a half-finished parent with shared fields and code. When unsure, choose the interface.
### 1.5 `enum`: a fixed set of choices
```java
enum CupSize {
    SMALL(0), MEDIUM(10), LARGE(20);             // the only three objects that will ever exist
    private final int extra;
    CupSize(int extra) { this.extra = extra; }
    int total(int base) { return base + extra; }
}
CupSize.valueOf("LARGE").total(20);              // 40.  Also: CupSize.values(), size.name(), size.ordinal()
```
Better than the texts `"large"`, `"Large"`, `"lrge"`: a typo is a compile error. `switch (size) { case SMALL -> ...; case MEDIUM -> ...; case LARGE -> ...; }` needs no `default`, and the compiler warns you when you add a new constant and forget a case.
### 1.6 `record` and `sealed`: closed families of data
```java
sealed interface Payment permits Cash, Upi {}            // ONLY these two may implement it
record Cash(int amount) implements Payment {}
record Upi(int amount, String handle) implements Payment {}
static String receipt(Payment p) {
    return switch (p) {                                  // pattern matching: the case also names the variable
        case Cash c -> "Cash " + c.amount();
        case Upi u -> "UPI " + u.handle();               // no default: all cases are covered
    };
}
```
A `record` already has the constructor, getters (`c.amount()`), `equals`, `hashCode` and `toString`. You can still add methods and extra constructors. Add a `when` guard for more detail: `case Card c when c.emiMonths() >= 3 -> ...`.
### 1.7 `Comparable`: teach Java how to sort your objects
```java
record Version(int major, int minor) implements Comparable<Version> {
    public int compareTo(Version other) {          // negative: this first, 0: equal, positive: this after
        if (major != other.major) return Integer.compare(major, other.major);
        return Integer.compare(minor, other.minor);
    }
}
Collections.sort(versions);                        // now works; Collections.max(versions) too
```
`<Version>` says "I compare with other Versions" (generics, explained properly on Day 22). Compare numbers, not text: `"1.10"` sorts *before* `"1.9"` as text but after as numbers.
### 1.8 Composition vs inheritance
"IS-A" means inherit (`Dog` is an `Animal`). "HAS-A" means a **field** (`Car` *has an* `Engine`). Use inheritance only for a true IS-A and keep trees shallow; mark a class `final` if nobody should extend it.
## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each numbered section, run it with `java Examples.java`, then change values and re-run. Try un-commenting `new Shape();` and read the compiler message. Add a third payment type and see what the compiler says about `receipt`.
## 3. Common mistakes
- Forgetting `super(...)` in the child constructor ("constructor Employee in class Employee cannot be applied").
- Forgetting `public` when implementing an interface method ("attempting to assign weaker access privileges").
- Overriding with a different signature (`pay(int)` instead of `pay()`): it is a *new* method. `@Override` catches it.
- Comparing an `enum` with text: `size.equals("LARGE")` is always `false`. Compare with the constant: `size == CupSize.LARGE`.
- Writing `compareTo` with text comparison when you wanted numbers.
- Inheriting just to reuse one helper: a plain method or composition is cleaner.
## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `Dog`/`Cat`/`Parrot` extend `Animal`, a `Point` record, `Vector` maths with methods |
| L2-1 … L2-3 | 🟡 Intermediate | Payroll (polymorphism), `Notifier` interface (classes and a lambda), `CupSize` enum |
| L3-1 … L3-3 | 🔴 Challenge | Abstract `Shape` family, `Comparable` `Version`, sealed `Payment` with `switch` |
Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task. As on Day 19, replace the stub line with your own classes between the markers.
## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Draw a tiny family tree: who is the parent, what does each child change? For the sealed task list the cases first: Cash, Upi, Card, then write one <code>case</code> for each.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Parrot: <code>super(name)</code> then store the phrase. Intern: <code>super(name, 10000)</code>. Enum: constants with arguments, a private field, a constructor; <code>parse</code> is <code>valueOf(text.trim().toUpperCase())</code>. Shape: <code>abstract double area();</code> in the parent. Version: split on <code>"\\."</code>, <code>Integer.parseInt</code> each piece, then compare part by part with <code>Integer.compare</code>. Sealed: <code>return switch (p) { case Cash c -&gt; ...; case Upi u -&gt; ...; case Card c when ... -&gt; ...; case Card c -&gt; ...; };</code> (put the <code>when</code> case first).
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day20_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>
## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day20_answers.md`
1. What does `super(name, salary);` do, and where must it be?
2. What is polymorphism (one sentence)? Which method runs for `Employee e = new Manager(...); e.pay();`?
3. What is the difference between `extends` and `implements`?
4. Why can you not write `new Shape()` when `Shape` is abstract?
5. Which three things does a `record` give you for free?
6. Why is an `enum` better than the texts `"SMALL"`, `"MEDIUM"`, `"LARGE"`?
7. What does `sealed ... permits ...` guarantee, and what does that allow in a `switch`?
8. What does `compareTo` return, and when does `Collections.sort` need it?
## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: **Week-3 project, a Library Management System** (classes + rules + a file on disk) and the Week-3 review test.
