# Day 21 - Week-3 review: quiz answers
1. It **overwrites** the file (the old content is gone). To add at the end, pass an option: `Files.writeString(path, "Hi", StandardOpenOption.CREATE, StandardOpenOption.APPEND)`.
2. Different computers use different default charsets, so accents, rupee signs and emoji can turn into garbage. `Files.readAllLines`, `Files.readString`, `Files.write` and `Files.writeString` use UTF-8 by default (and `Files.newBufferedReader/Writer` too); with old classes like `FileReader` you must name it.
3. `List<String>`. Every piece from `split` is a `String`; convert with `Integer.parseInt(text)` or `Double.parseDouble(text)`.
4. A value can contain a comma inside quotes (`"Tea, masala"`), and `split(",")` would cut it in two. Use a real CSV parser or handle the quotes yourself.
5. `try` runs first; if an exception is thrown, the matching `catch` runs; `finally` runs last, always (also after a `return` or an uncaught exception). It does not run only if the JVM stops (`System.exit`, crash).
6. It hides every error (even bugs like `NullPointerException`), so the program carries on with wrong data and nobody can find out why. Catch the specific exception and handle or log it.
7. Checked: `IOException` (the compiler forces the caller to catch it or declare `throws`). Unchecked: `IllegalArgumentException`, `NullPointerException`, a `RuntimeException` subclass like `LibraryError` (the caller may catch it but is not forced to).
8. It closes every resource declared in the round brackets automatically, even when an exception happens, and before the `catch` block runs.
9. `this` is the current object, the one whose method or constructor is running. `this.name = name;` copies the parameter into the field.
10. `static` means ONE list shared by every `Cart` object: all customers would see and change the same items. Make it an instance field (no `static`) created per object.
11. It calls the parent class's constructor so the inherited part of the object is set up; it must be the first line of the child's constructor.
12. `equals` and `hashCode` (they must agree). `Comparable` (its `compareTo` method) makes objects sortable.
13. A `static` method belongs to the class, is called as `Library.load(path)` and has no `this` (no access to the object's own fields). An instance method works on one object and can use its fields.
14. A constructor, accessor methods (`book.title()`), `equals`, `hashCode` and `toString`.
15. "IS-A" means inheritance (`Manager extends Employee`). "HAS-A" is composition: a field.
