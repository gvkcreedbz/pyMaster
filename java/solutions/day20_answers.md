# Day 20 - Quiz answers
1. It calls the parent class's constructor so the parent part of the object is set up (name, salary). It must be the **first line** of the child's constructor (if you leave it out, Java inserts `super();`, which fails when the parent has no empty constructor).
2. Polymorphism: the same method call does different things depending on the real object. `e.pay()` runs the **Manager's** `pay()` (salary + bonus), because the object is a `Manager`, even though the variable type is `Employee`.
3. `extends` makes a class inherit from ONE parent class (IS-A, with its fields and code). `implements` promises to provide the methods of an interface; a class can implement many.
4. An abstract class is unfinished (it has at least one abstract method without a body), so Java refuses to create an object from it. Create a subclass that implements the missing method and create that instead.
5. Any three of: a constructor, getter methods (`c.amount()`), `equals`, `hashCode`, `toString`.
6. The compiler knows every valid value, so a typo like `SMAL` is a compile error, `switch` can check you covered every case, and each constant can carry data and methods (`extra`, `total`).
7. Only the listed classes can implement the interface, so the compiler knows all the possible cases. A `switch` over it needs no `default`, and adding a new type makes the compiler point at every `switch` you must update.
8. A negative number if `this` comes first, `0` if equal, a positive number if `this` comes after. `Collections.sort` (and `TreeSet`, `Collections.max`) need it to know the order of your own objects, via `implements Comparable<YourClass>`.
