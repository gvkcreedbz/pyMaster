# Day 19 — Object-Oriented Programming I: Classes & Objects
| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Model real things (account, cart, library) as classes with data + behaviour, and protect their rules with encapsulation | Intermediate |
## 🌍 Real-world scenario & trend
**A banking app.** A `BankAccount` *has data* (owner, balance, history) and *can do things* (deposit, withdraw), and the rules ("no overdraft") live inside it. Games (characters), shops (products, carts), libraries (books, members) and almost every framework (Spring beans, JDBC connections, `ArrayList` itself) are classes.
**Why Java?** Java was built around classes: **everything you write lives in one**, and its big banking and insurance systems are millions of lines of cooperating objects. The compiler checks every field and method for you, so a typo like `acount.balanse` is caught before the program runs. *Coming from Python?* `__init__` becomes a **constructor** named like the class, `self` becomes `this`, `_balance` becomes a real `private` field, and `@property` becomes getter/setter methods.
## 0. Warm-up (5 min) — Day 18 recap
- What does `LocalDate.of(2026, 11, 16).plusDays(30)` give?  • What does `import java.util.*;` do?
## 1. Concepts (with tiny code)
### 1.1 Class = blueprint, object = a thing built from it
```java
class Product {
    private final String name;                  // fields: the object's data
    private final double price;
    Product(String name, double price) {        // constructor: runs when you say "new"
        this.name = name;
        this.price = price;
    }
    double discountedPrice(int percent) {       // method: the object's behaviour
        return price * (1 - percent / 100.0);
    }
}
Product pen = new Product("Pen", 10);           // create an object (an "instance")
Product book = new Product("Book", 120);
System.out.println(book.discountedPrice(25));   // 90.0
```
The constructor has the **same name as the class and no return type**. Python passes `self` automatically; in Java you do not even write it: inside a method the fields are simply available.
### 1.2 `this`, and objects that keep their own state
Inside the constructor the parameter `name` hides the field `name`. `this.name` means "the field of this object", so `this.name = name;` copies the parameter into the field. Without `this.` you only assign the parameter to itself and the field stays empty.
```java
class Counter {
    private int count = 0;                      // every Counter gets its own count
    void hit() { count++; }
    int getCount() { return count; }
}
Counter a = new Counter(), b = new Counter();
a.hit(); a.hit(); b.hit();
System.out.println(a.getCount() + " " + b.getCount());   // 2 1
```
A class may have several constructors (overloading, Day 11). One can call another with `this(...)`: `BankAccount(String owner) { this(owner, 0); }`.
### 1.3 `toString()`: how an object prints
```java
@Override
public String toString() { return "Rectangle(" + width + "x" + height + ")"; }
System.out.println(new Rectangle(3, 4));        // Rectangle(3x4)
```
Without it you get unreadable text like `Rectangle@1b6d3586`. `@Override` asks the compiler to check that you really are replacing a method that exists.
### 1.4 `static`: one copy for the whole class
```java
class Account {
    static final String BANK_NAME = "Chai Bank";   // shared by ALL accounts (a constant)
    private static int opened = 0;                 // shared counter
    private final String owner;                    // different for each object
    Account(String owner) { this.owner = owner; opened++; }
    static int getOpened() { return opened; }      // call it on the class: Account.getOpened()
}
```
A `static` method has no `this`: it cannot see the object's own fields. That is what `main` is, and why it starts the program without any object.
### 1.5 Encapsulation: `private` fields, public methods
Make fields `private` and let the outside world use **methods**. Then the rules cannot be bypassed.
```java
class Temperature {
    private double celsius;
    Temperature(double celsius) { setCelsius(celsius); }     // the constructor validates too
    double getCelsius() { return celsius; }
    void setCelsius(double celsius) {
        if (celsius < -273.15) throw new IllegalArgumentException("Below absolute zero");
        this.celsius = celsius;
    }
    double getFahrenheit() { return celsius * 9 / 5 + 32; }  // calculated: no setter at all
}
```
Python only *hints* privacy with `_name`; Java **enforces** it: `temp.celsius = -500` from outside is a compile error. Use `final` for fields that must never change after the constructor. If a getter returns a list, return a **copy** (`new ArrayList<>(history)`), otherwise callers can empty your list behind your back.
### 1.6 `equals` and `hashCode`: when are two objects "the same"?
```java
Sku a = new Sku("P100"), b = new Sku("P100");
System.out.println(a == b);        // false: == asks "the very same object?"
System.out.println(a.equals(b));   // true once you write equals
@Override public boolean equals(Object other) { return other instanceof Sku that && code.equals(that.code); }
@Override public int hashCode()   { return code.hashCode(); }
```
`other instanceof Sku that` checks the type **and** gives it the name `that` in one step (and is `false` for `null`). **Rule:** whenever you write `equals`, write `hashCode` from the same fields. `HashSet` and `HashMap` use both; break the rule and the same product appears twice in a set. (A `record`, Day 13, writes `equals`, `hashCode` and `toString` for you.)
### 1.7 Methods call each other and raise errors
Business rules belong **inside** the class (`withdraw` checks the balance), so no outside code can break them. Throw `IllegalArgumentException` for a bad argument and `IllegalStateException` for "not allowed right now" (Day 17).
### 1.8 Design tip: nouns → classes, verbs → methods
"A *library* lets a *member* check out a *book*" gives `Library`, `Member`, `Book` and `checkout()`. Start with the data (fields), then ask "what can it do?" (methods).
## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each numbered section, run it with `java Examples.java`, then change values and re-run. In section 4 predict `first == second` before you run it.
## 3. Common mistakes
- Writing `name = name;` in a constructor (it does nothing): write `this.name = name;`.
- Giving the constructor a return type (`void Product(...)`): then it is just a normal method and `new Product(...)` fails.
- Forgetting `new`: `Product p = Product("Pen", 10);` does not compile.
- Comparing objects with `==` when you mean `equals`; writing `equals` but not `hashCode`.
- Making every field `public`: anyone can then set a negative balance.
- Calling an instance method from a `static` method without an object ("non-static method cannot be referenced from a static context").
## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `Product` (with a `static` counter), `Student`, `Rectangle` with `toString` |
| L2-1 … L2-4 | 🟡 Intermediate | `BankAccount` (validation, copy of history), `ShoppingCart`, `Temperature` (encapsulation), `Item` with `equals`/`hashCode` |
| L3-1, L3-2 | 🔴 Challenge | A small `Library` class, a `CharStack` and a balanced-brackets checker |
Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task. Today each exercise starts as one long stub line: **replace it with your own class** between the markers.
## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
For each class write down: what data does it hold (these are the <b>fields</b>, make them <code>private</code>) and what can it do (these are the <b>methods</b>)? Then write the constructor that fills the fields.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Cart: two <code>TreeMap</code>s, <code>Map&lt;String, Double&gt;</code> for prices and <code>Map&lt;String, Integer&gt;</code> for quantities, created in the field declaration. Rounding to 2 decimals: <code>Math.round(x * 100) / 100.0</code>. Library: a <code>Map&lt;String, Integer&gt;</code> of free copies and a <code>List</code> of loans (a tiny <code>record Loan(String title, String member)</code>, so <code>loans.remove(new Loan(t, m))</code> works). CharStack: a <code>List&lt;Character&gt;</code>; push = <code>add</code>, pop = <code>remove(size() - 1)</code>. Balanced brackets: push opening brackets; on a closing bracket pop and compare with its partner; the stack must be empty at the end.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day19_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>
## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day19_answers.md`
1. What is the difference between a class and an object?
2. What does `this` refer to, and when must you write `this.name = name;`?
3. When does a constructor run, and what two things make it different from a normal method?
4. What does `System.out.println(obj)` show if the class has no `toString()`?
5. What is the difference between a `static` field and an instance field?
6. Why make fields `private` and use getters and setters?
7. What is wrong with `getHistory() { return history; }` when `history` is a private list?
8. If you override `equals`, which other method must you override, and why?
## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: OOP II: inheritance, interfaces, abstract classes, polymorphism, `enum` and `sealed` types.
