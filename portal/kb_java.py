"""Built-in tutor knowledge (JAVA track): for each concept, what it is, WHERE it's used in real jobs, HOW it's used.

Same public names and dict keys as `portal/kb.py` (KB, BY_ID, GENERIC_USAGE, VISUALS) so the portal can swap the module
by track. Powers the offline tutor's "where will I use this?" answers for the Java course (30 days, Java 21).

Entry keys: id, name, days, keys, what, where, how, pitfall, nxt.
Strings are raw triple-quoted so Java code (quotes, backslashes, text blocks) stays readable.
"""

KB = [
    dict(id="hello_main", name="Classes, main & running Java", days=[1], keys=["class", "main", "public static void main", "hello world", "compile", "compiler", "javac", "jvm", "jdk", "jre", "bytecode", "string[] args", "jshell", "java -version", "semicolon", "run"],
         what=r'''Every Java program lives inside a **class**, and the JVM starts running at the `main` method. `javac Hello.java` *compiles* your text into bytecode (`Hello.class`); `java Hello` runs that bytecode on the JVM.''',
         where=r'''- **Android apps, bank back-ends, insurance portals, Minecraft: Java Edition:** all start life as classes with entry points.
- **"Write once, run anywhere":** the same `.class` / `.jar` runs on a developer's Windows laptop and on a Linux container in the cloud.
- **Servers** (Tomcat, Spring Boot apps) are just a `main` that starts a web server and then keeps running.
- **The compiler is a free reviewer:** typos and type mistakes are caught *before* the program ever runs.''',
         how=r'''```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Welcome to Chai Point");   // runs first
        System.out.println("One masala chai, please"); // runs second
    }
}
```
Terminal: `javac Hello.java` then `java Hello`. (Java 21 also lets you run a single file straight away: `java Hello.java`.)''',
         pitfall=r'''A `public class Hello` must live in a file named **exactly** `Hello.java` (capital letters count). Also: every statement ends with `;` and every `{` needs its `}`.''',
         nxt=r'''Print your own shop name and two items, then break one `;` on purpose and read what `javac` says.'''),
    dict(id="output", name="println, print & printf", days=[1, 2], keys=["println", "print", "printf", "format", "system.out", "%d", "%s", "%.2f", "%n", "output", "display", "string.format", "escape", "\\n"],
         what=r'''`System.out.println` prints and moves to the next line. `printf` mixes values into text with placeholders: `%s` text, `%d` whole number, `%.2f` decimals, `%n` new line.''',
         where=r'''- **Receipts, invoices and reports:** "Order #123 shipped to Priya" is a `printf`/`String.format` call.
- **CLI tools and batch jobs** print progress so you can see what a 2-hour job is doing.
- **Quick debugging** while learning (real teams switch to a logger, see the logging entry).''',
         how=r'''```java
String name = "Priya";
int items = 3;
double total = items * 49.5;
System.out.printf("Hi %s, you have %d items (total ₹%.2f)%n", name, items, total);
System.out.println(String.format("%,d", 1250000));   // 1,250,000
```
`%-10s` pads text to 10 characters (left-aligned): handy for table columns.''',
         pitfall=r'''`%d` with a `double` throws `IllegalFormatConversionException`; use `%f`. Prefer `%n` over `\n` for a portable line break.''',
         nxt=r'''Print three items and prices as an aligned table using `%-10s` and `%8.2f`.'''),
    dict(id="variables", name="Variables, types & var", days=[2], keys=["variable", "int", "double", "long", "boolean", "char", "var", "final", "constant", "declare", "declaration", "primitive", "camelcase", "naming", "wrapper"],
         what=r'''Java is **statically typed**: you declare what kind of value a variable holds (`int price = 49;`) and the compiler enforces it. Primitives (`int`, `double`, `boolean`, `char`, `long`) hold the value itself; `String` and other objects hold a reference. `var` lets the compiler infer the type; `final` makes it a constant.''',
         where=r'''- **Every program ever:** a checkout holds `cartTotal`, `taxRate`, `customerName`.
- **Constants** like `static final int MAX_RETRIES = 3;` appear in every real codebase so a rule changes in one place.
- **Databases and APIs:** a Java field's type maps onto a column or JSON type (`long id`, `String email`).
- **Money and ids:** banks pick `long` or `BigDecimal` on purpose; the type *is* part of the design.''',
         how=r'''```java
final double TAX_RATE = 0.18;      // constant: cannot be reassigned
int price = 200;
double total = price * (1 + TAX_RATE);
var label = "Total";               // compiler infers String
System.out.println(label + ": " + total);   // Total: 236.0
```
Name variables for what they *mean* (`totalPrice`), in `camelCase`.''',
         pitfall=r'''`int` overflows silently: `Integer.MAX_VALUE + 1` becomes a large **negative** number; use `long` for ids, timestamps and cents. Local variables are *not* auto-initialised: use one before giving it a value and the compiler refuses.''',
         nxt=r'''Declare a `final` tax rate and compute the price of three items with it. Then try assigning to it and read the error.'''),
    dict(id="scanner", name="Reading input with Scanner", days=[2, 7], keys=["scanner", "system.in", "nextint", "nextdouble", "nextline", "hasnext", "hasnextint", "input", "read input", "keyboard", "stdin", "inputmismatchexception", "bufferedreader"],
         what=r'''`Scanner` reads text typed by the user (or from a file). `nextLine()` reads a whole line, `nextInt()` / `nextDouble()` parse the next token as a number. What arrives is always *text first*, then converted.''',
         where=r'''- **Command-line tools and ATM-style menus** that ask a question and wait.
- **Online judges** (HackerRank, Codeforces, university autograders) feed test data through standard input.
- **Reading files line by line** uses the same `Scanner` idea (`new Scanner(path)`).''',
         how=r'''```java
import java.util.Scanner;

Scanner in = new Scanner(System.in);
System.out.print("Name? ");
String name = in.nextLine();
System.out.print("How many chai? ");
int cups = Integer.parseInt(in.nextLine().trim());   // read a line, then convert
System.out.println(name + " owes ₹" + cups * 15);
```
Reading numbers via `nextLine()` + `parseInt` avoids the leftover-newline trap below.''',
         pitfall=r'''After `nextInt()` the Enter key is still waiting, so the next `nextLine()` returns an **empty string**. And typing `abc` for `nextInt()` throws `InputMismatchException` (the bad token stays unread, so retrying without `nextLine()` loops forever).''',
         nxt=r'''Ask for two numbers and print their sum; if the user types text, ask again instead of crashing.'''),
    dict(id="casting_math", name="Casting, integer division & Math", days=[3], keys=["cast", "casting", "integer division", "(double)", "(int)", "math", "math.round", "math.max", "bigdecimal", "overflow", "modulo", "%", "remainder", "lossy", "precision", "divide", "division", "operator", "arithmetic"],
         what=r'''`int / int` throws the fraction away (`7 / 2` is `3`). To keep decimals, make one side a `double` (`(double) a / b`). Going to a *smaller* type needs an explicit cast and can lose data. `%` gives the remainder.''',
         where=r'''- **Pagination:** `pages = (items + perPage - 1) / perPage`; the leftover row is `items % perPage`.
- **Money:** banks and invoicing systems use `BigDecimal` (or whole cents in a `long`), never `double`.
- **Time:** `seconds / 3600` hours, `seconds % 3600 / 60` minutes.
- **Every-Nth logic** (`i % 3 == 0`) for scheduling, batching, FizzBuzz-style rules.''',
         how=r'''```java
int sum = 17, count = 4;
double wrong = sum / count;            // 4.0 (division happened on ints first!)
double right = (double) sum / count;   // 4.25
int pages = (95 + 20 - 1) / 20;        // 5 pages for 95 rows
System.out.println(Math.round(4.256 * 100) / 100.0);   // 4.26
```''',
         pitfall=r'''`double avg = sum / count;` is still integer division; the cast must happen *before* the `/`. And `0.1 + 0.2 != 0.3`: binary floats are inexact, so never use `double` for money.''',
         nxt=r'''Turn 3725 seconds into `h:m:s` using `/` and `%`.'''),
    dict(id="strings", name="String & StringBuilder", days=[4], keys=["string", "stringbuilder", "substring", "charat", "split", "trim", "strip", "touppercase", "tolowercase", "indexof", "contains", "replace", "length", "join", "string.format", "text block", "isempty", "isblank", "startswith", "endswith", "immutable", "append", "chars"],
         what=r'''A `String` is an ordered, **immutable** sequence of characters. Methods like `trim()`, `split()`, `toLowerCase()` return **new** strings. `StringBuilder` is a *mutable* buffer for building a string piece by piece.''',
         where=r'''- **Cleaning data:** `" SOUTH ".trim().toLowerCase()`; every messy export needs it.
- **Parsing logs, URLs, emails:** `line.split(" ")`, `email.substring(email.indexOf('@') + 1)`.
- **Building reports, SQL, JSON or e-mails** line by line with `StringBuilder` (or text blocks for fixed templates).
- **Search & NLP** start with `text.toLowerCase().split("\\s+")`.''',
         how=r'''```java
String line = "  Priya , priya@MAIL.com ";
String[] parts = line.split(",");
String name = parts[0].trim();
String email = parts[1].trim().toLowerCase();
System.out.println(name + " " + email);        // Priya priya@mail.com

StringBuilder sb = new StringBuilder();
for (int i = 1; i <= 3; i++) sb.append("Row ").append(i).append('\n');
System.out.print(sb);
```''',
         pitfall=r'''Strings never change in place: `s.toUpperCase();` on its own does nothing, write `s = s.toUpperCase();`. `+=` inside a big loop copies the text every time (use `StringBuilder`). `split(".")` treats the dot as a regex: write `split("\\.")`. `substring(a, b)` excludes `b`.''',
         nxt=r'''Given `"  hello   world "`, produce `"Hello World"` using `trim`, `split("\\s+")` and a `StringBuilder`.'''),
    dict(id="equals_ref", name="equals vs == (identity vs content)", days=[4, 19], keys=["equals", "==", "compare strings", "comparing strings", "compare two strings", "string comparison", "hashcode", "reference", "string pool", "intern", "compareto", "equalsignorecase", "objects.equals", "new string", "identity", "integer cache", "null check", "contentequals"],
         what=r'''For objects, `==` asks *"are these the very same object in memory?"* while `.equals()` asks *"do they hold the same content?"*. For primitives (`int`, `double`) `==` compares the values, which is fine.''',
         where=r'''- **Login and validation:** `"admin".equals(role)`, `password.equals(saved)`.
- **HashMap / HashSet keys** rely on `equals` + `hashCode` to find things.
- **Code-review bots and IDEs** (IntelliJ, SonarQube, SpotBugs) flag `==` on strings because it is one of the most common real bugs.
- **Null-safe comparison:** `Objects.equals(a, b)` is everywhere in model classes.''',
         how=r'''```java
String a = new String("chai");
String b = "chai";
System.out.println(a == b);                // false (two different objects)
System.out.println(a.equals(b));           // true  (same letters)
System.out.println("chai".equals(input));  // safe even when input is null
```
Put the **known** value on the left: `"yes".equals(answer)` never throws `NullPointerException`.''',
         pitfall=r'''`==` on strings sometimes *seems* to work (identical literals share one object), which hides the bug until real input arrives. Same trap with boxed numbers: `Integer` values `127 == 127` is true but `1000 == 1000` is false.''',
         nxt=r'''Read a word with `Scanner` and compare it to `"quit"` first with `==`, then with `.equals`. Which one works?'''),
    dict(id="conditions", name="if / else, switch expressions & booleans", days=[5], keys=["if", "else", "else if", "switch", "case", "ternary", "?", "boolean", "&&", "||", "!", "condition", "comparison", "yield", "pattern matching", "instanceof", "default", "decision"],
         what=r'''`if` lets the program choose a path. Conditions are `boolean` expressions combined with `&&` (and), `||` (or), `!` (not). A modern **`switch` expression** with arrows (`case X ->`) picks a value, with no fall-through.''',
         where=r'''- **Login and permissions:** `if (passwordOk && !accountLocked)`.
- **Pricing rules:** discounts by tier, cart size or day of week.
- **Mapping codes to meaning:** HTTP status, order status, day names with a `switch`.
- **Validation:** reject rows with missing values before they reach the database.''',
         how=r'''```java
int spend = 1800;
String tier;
if (spend >= 5000)      tier = "gold";
else if (spend >= 1000) tier = "silver";
else                    tier = "basic";

String label = switch (tier) {
    case "gold", "silver" -> "VIP";
    default               -> "regular";
};
System.out.println(tier + " / " + label);   // silver / VIP
```
Order matters: the first true branch wins.''',
         pitfall=r'''Old-style `case X:` needs `break;` or it falls through into the next case. Use `&&`/`||` (they stop early) rather than `&`/`|`: `s != null && s.length() > 0` is safe, `&` would still evaluate the second half and crash.''',
         nxt=r'''Add a `"platinum"` tier above gold. Where in the chain must it go?'''),
    dict(id="for_loops", name="for loops & enhanced for", days=[6], keys=["for loop", "for", "enhanced for", "for-each", "foreach", "iterate", "iteration", "i++", "nested loop", "accumulator", "counter", "off-by-one", "length", "loop through"],
         what=r'''`for (int i = 0; i < n; i++)` repeats a block with a counter. The enhanced `for (Item it : items)` walks every element of an array or collection without an index.''',
         where=r'''- **Processing every row, order or file:** nightly settlement jobs at banks, thumbnail generation for every image.
- **Totals and statistics:** the *accumulator* pattern (`total += x`) is how sums, counts and maxima work.
- **Games:** Minecraft-style engines update every entity once per tick in a loop.
- **Grids and tables:** nested loops walk rows and columns.''',
         how=r'''```java
double[] prices = {49.5, 30, 120};
double total = 0;
for (double p : prices) {            // each item in turn
    total += p;                      // accumulate
}
System.out.println(total);           // 199.5
for (int i = 0; i < prices.length; i++) {
    System.out.println((i + 1) + ". " + prices[i]);
}
```''',
         pitfall=r'''Off-by-one: `i <= prices.length` runs one step too far and throws `ArrayIndexOutOfBoundsException`. Removing from a list *inside* an enhanced `for` throws `ConcurrentModificationException`; use `list.removeIf(...)` or an `Iterator`.''',
         nxt=r'''Write a loop that prints only the prices above 40.'''),
    dict(id="while_loops", name="while, do/while, break & continue", days=[6, 7], keys=["while", "do while", "do/while", "break", "continue", "infinite", "sentinel", "retry", "menu loop", "labelled break", "loop until"],
         what=r'''`while (condition)` repeats **until the condition turns false** (use it when you don't know the number of rounds). `do { } while (...)` runs at least once. `break` leaves the loop, `continue` skips to the next round.''',
         where=r'''- **Menus, ATMs, chatbots** that run until the user picks Quit.
- **Retry logic:** call a flaky HTTP API up to 3 times before giving up.
- **Polling:** wait until a batch job reports DONE.
- **Servers:** the heart of a server is `while (running) { accept a request; handle it; }`.''',
         how=r'''```java
int attempts = 0;
boolean ok = false;
while (attempts < 3 && !ok) {
    System.out.print("PIN: ");
    ok = "1234".equals(in.nextLine());
    attempts++;
}
System.out.println(ok ? "Welcome" : "Card blocked");
```''',
         pitfall=r'''If nothing in the body changes the condition the loop never ends (Ctrl+C to stop). A `break` inside a `switch` that sits inside a loop only leaves the *switch*.''',
         nxt=r'''Show how many attempts are left after each wrong PIN.'''),
    dict(id="arrays", name="Arrays", days=[8], keys=["array", "int[]", "new int[", "length", "arrays.", "arrays.sort", "arrays.tostring", "2d array", "matrix", "index", "fixed size", "args", "arrays.fill", "arrays.aslist", "zero-based"],
         what=r'''An array is a **fixed-size**, same-type, zero-indexed row of values: `int[] scores = new int[5];`. `length` (no parentheses) tells its size. The `Arrays` helper class sorts, prints, fills and searches them.''',
         where=r'''- **Grids:** game boards (Tic-tac-toe, Minesweeper), pixel rows of an image, spreadsheet-like tables.
- **Raw bytes:** `byte[]` buffers hold files and network data in every I/O library.
- **Performance-critical code** (games, trading engines) prefers arrays to avoid object overhead.
- **`main(String[] args)`:** the command-line arguments you pass arrive as an array.''',
         how=r'''```java
int[] scores = {72, 95, 88};
Arrays.sort(scores);
System.out.println(Arrays.toString(scores));        // [72, 88, 95]
int best = scores[scores.length - 1];                // last element
int[][] grid = new int[3][4];                        // 3 rows, 4 columns
grid[1][2] = 7;
```''',
         pitfall=r'''`System.out.println(scores)` prints something like `[I@1b6d3586`; use `Arrays.toString` (or `deepToString` for 2-D). Arrays can't grow; need a flexible size? Use `ArrayList`. `==` on arrays compares identity; use `Arrays.equals`.''',
         nxt=r'''Find the highest and lowest value in an array without sorting it.'''),
    dict(id="arraylist", name="ArrayList & List", days=[9], keys=["arraylist", "list", "list.of", "add", "get", "remove", "size", "contains", "indexof", "collections.sort", "collections", "linkedlist", "wrapper", "integer", "boxing", "autoboxing", "immutable list", "list<", "generics"],
         what=r'''`ArrayList<String>` is a **resizable** ordered list of objects. Declare the variable as the interface (`List<String> cart = new ArrayList<>();`). Primitives are stored as wrapper types (`List<Integer>`) via automatic boxing.''',
         where=r'''- **Carts, playlists, search results, to-do lists:** anything whose size isn't known up front.
- **Spring / JPA repositories** return `List<User>` for "all users where...".
- **JSON arrays** parsed by Jackson or Gson become `List`s.
- **Work queues:** a list of file names or ids to process.''',
         how=r'''```java
List<String> cart = new ArrayList<>();
cart.add("milk");
cart.add("bread");
cart.add("eggs");
cart.remove("bread");
Collections.sort(cart);
System.out.println(cart + " size=" + cart.size());   // [eggs, milk] size=2
List<Integer> fixed = List.of(3, 1, 2);              // immutable
```''',
         pitfall=r'''On a `List<Integer>`, `remove(1)` removes **index** 1 while `remove(Integer.valueOf(1))` removes the *value* 1. `List.of(...)` is read-only: `add` throws `UnsupportedOperationException`. `get(list.size())` is out of bounds (last is `size() - 1`).''',
         nxt=r'''Remove all duplicates from a list while keeping the order (hint: `LinkedHashSet`).'''),
    dict(id="sets", name="HashSet, TreeSet & Set", days=[9], keys=["set", "hashset", "treeset", "linkedhashset", "unique", "union", "retainall", "addall", "removeall", "containsall", "duplicate", "set.of", "distinct", "membership", "intersection"],
         what=r'''A `Set` is a collection of **unique** items with very fast `contains`. `HashSet` is unordered, `LinkedHashSet` keeps insertion order, `TreeSet` keeps items sorted. Set maths: `addAll` (union), `retainAll` (intersection), `removeAll` (difference).''',
         where=r'''- **Unique visitors / distinct customers:** `new HashSet<>(userIds).size()`.
- **Mutual friends or common tags:** `retainAll`.
- **Permission checks:** `userPerms.containsAll(required)`.
- **Speed:** `bigSet.contains(x)` is instant, scanning a list is not.''',
         how=r'''```java
Set<String> monday = new HashSet<>(List.of("ana", "raj", "li"));
Set<String> tuesday = new HashSet<>(List.of("raj", "li", "sam"));
Set<String> both = new HashSet<>(monday);
both.retainAll(tuesday);                       // [raj, li] came both days
Set<String> everyone = new TreeSet<>(monday);
everyone.addAll(tuesday);                      // [ana, li, raj, sam]
```''',
         pitfall=r'''A set of *your own* class only de-duplicates if the class defines `equals` and `hashCode` (a `record` gives you both). Don't change an object's fields after putting it in a `HashSet`; it can no longer be found.''',
         nxt=r'''Find the users who visited Monday but not Tuesday.'''),
    dict(id="hashmap", name="HashMap & Map", days=[10], keys=["map", "hashmap", "treemap", "linkedhashmap", "getordefault", "merge", "put", "computeifabsent", "entryset", "keyset", "values", "key", "lookup", "counting", "frequency", "word count", "cache", "containskey", "map.of", "entry", "dictionary"],
         what=r'''A `Map<K, V>` links a **key to a value** (like a phone book). `HashMap` lookup is near-instant, `TreeMap` keeps keys sorted, `LinkedHashMap` keeps insertion order.''',
         where=r'''- **Counting:** votes, word frequency, orders per customer, HTTP status counts in a log.
- **Grouping rows** by region or category: the core of every report.
- **JSON objects:** Jackson/Gson hand you nested `Map`s when the shape isn't known.
- **Caches and lookups:** country code to name, session id to user, products by SKU (Guava/Caffeine caches are fancy maps).''',
         how=r'''```java
Map<String, Integer> votes = new TreeMap<>();
for (String v : List.of("a", "b", "a")) {
    votes.merge(v, 1, Integer::sum);            // add 1, or start at 1
}
System.out.println(votes);                      // {a=2, b=1}
for (Map.Entry<String, Integer> e : votes.entrySet()) {
    System.out.println(e.getKey() + " -> " + e.getValue());
}
int zero = votes.getOrDefault("z", 0);          // no null, no crash
```''',
         pitfall=r'''`map.get(key)` returns `null` when the key is missing, so `int n = map.get("z");` throws `NullPointerException`. Use `getOrDefault`. Plain `HashMap` order is not guaranteed; use `TreeMap` or `LinkedHashMap` when you print.''',
         nxt=r'''Group a list of orders by region into `Map<String, List<Order>>` with `computeIfAbsent`.'''),
    dict(id="methods", name="Methods, overloading & varargs", days=[11], keys=["method", "function", "return", "void", "parameter", "argument", "overload", "overloading", "varargs", "static", "scope", "pass by value", "javadoc", "call", "signature", "..."],
         what=r'''A method is a **named, reusable recipe**: parameters in, `return` value out (`void` = nothing returned). *Overloading* means several methods share a name but take different parameters. `int... nums` accepts any number of ints.''',
         where=r'''- **Every codebase** is thousands of small methods: `calculateTax`, `sendEmail`, `cleanName`.
- **Spring controllers:** every endpoint is a method; services call repositories' methods.
- **Testing:** you can only unit-test code that sits in methods.
- **The JDK itself:** `Math.max(int, int)`, `Math.max(double, double)` are overloads.''',
         how=r'''```java
static double finalPrice(double price, double taxRate, double discount) {
    return Math.round((price - discount) * (1 + taxRate) * 100) / 100.0;
}
static double finalPrice(double price) {            // overload with defaults
    return finalPrice(price, 0.18, 0);
}
static int sum(int... nums) { int t = 0; for (int n : nums) t += n; return t; }

System.out.println(finalPrice(200));       // 236.0
System.out.println(sum(1, 2, 3));          // 6
```''',
         pitfall=r'''Java is **pass-by-value**: reassigning a parameter never changes the caller's variable (the *object's contents* can change, the variable can't). Every path of a non-`void` method must `return`, or the compiler says "missing return statement".''',
         nxt=r'''Turn a block of code you wrote earlier into a method with parameters and a return value.'''),
    dict(id="recursion", name="Recursion", days=[11, 22], keys=["recursion", "recursive", "base case", "call itself", "stackoverflowerror", "memoization", "fibonacci", "factorial", "tree", "divide and conquer"],
         what=r'''A method that **calls itself on a smaller version of the problem**, with a base case that stops it.''',
         where=r'''- **Folder trees:** a folder contains folders (disk-usage tools, build tools scanning a project).
- **Nested data of unknown depth:** JSON documents, menus, organisation charts, comment threads.
- **Algorithms:** merge sort, quick sort, binary search, parsing expressions in compilers.''',
         how=r'''```java
static long totalSize(java.io.File f) {
    if (f.isFile()) return f.length();                 // base case
    long sum = 0;
    for (java.io.File child : f.listFiles()) {
        sum += totalSize(child);                       // smaller problem
    }
    return sum;
}
static long factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }
```''',
         pitfall=r'''No base case (or one that is never reached) ends in `StackOverflowError`. Java does not optimise tail calls, so a very deep recursion is better written as a loop.''',
         nxt=r'''Write `fib(n)`, then notice how slow it gets for n=40. How would a `HashMap` cache help?'''),
    dict(id="lambdas", name="Lambdas, method references & functional interfaces", days=[12, 22], keys=["lambda", "->", "method reference", "::", "functional interface", "predicate", "function", "consumer", "supplier", "comparator", "comparator.comparing", "runnable", "anonymous class", "foreach", "removeif", "sort"],
         what=r'''A lambda is a **tiny unnamed function**: `(a, b) -> a + b`. It can be used wherever an interface with a single abstract method (a *functional interface* such as `Predicate`, `Function`, `Comparator`, `Runnable`) is expected. `User::name` is a shorter method reference.''',
         where=r'''- **Sorting and filtering records:** `users.sort(Comparator.comparing(User::age))`.
- **Event handlers:** Android `button.setOnClickListener(v -> ...)`, JavaFX and Swing callbacks.
- **Concurrency:** `executor.submit(() -> fetch(url))`.
- **Streams and Spring code** are written almost entirely with lambdas.''',
         how=r'''```java
List<String> names = new ArrayList<>(List.of("Zoya", "ana", "Raj"));
names.sort(String::compareToIgnoreCase);                 // [ana, Raj, Zoya]
names.removeIf(n -> n.length() < 4);                     // drops "ana", "Raj"
Predicate<Integer> isBig = amt -> amt > 500;
System.out.println(isBig.test(900));                     // true
```
Read `n -> n.length() < 4` as *"given n, answer whether its length is under 4"*.''',
         pitfall=r'''A lambda can only use local variables that are **effectively final** (never reassigned). If the body needs several lines and a long explanation, give it a real method name instead.''',
         nxt=r'''Sort a list of `record Order(String id, double amt)` by amount, biggest first, with `Comparator.comparingDouble`.'''),
    dict(id="streams", name="Streams: filter, map, reduce", days=[12, 14, 25, 26], keys=["stream", "streams", "stream()", "map", "filter", "reduce", "collect", "tolist", "sum", "maptoint", "mapToDouble", "average", "sorted", "limit", "distinct", "anymatch", "allmatch", "flatmap", "intstream", "boxed", "findfirst", "parallelstream"],
         what=r'''A stream is a **pipeline over a collection**: a source, then lazy steps (`filter`, `map`, `sorted`, `limit`), then one final step (`toList()`, `sum()`, `count()`, `collect(...)`) that makes it run. Think of Python comprehensions, written as a chain.''',
         where=r'''- **Cleaning columns and filtering rows:** keep only orders above ₹500.
- **Top-N reports:** "three best-selling products this week".
- **Spring services** convert entities to DTOs with `.map(...)`.
- **Analytics code** on the JVM (Spark's Java API, Kafka Streams) uses the same fluent style.''',
         how=r'''```java
List<Integer> amounts = List.of(900, 120, 640, 75);
List<Integer> big = amounts.stream().filter(a -> a > 500).toList();   // [900, 640]
int total = amounts.stream().mapToInt(Integer::intValue).sum();       // 1735
double avg = amounts.stream().mapToInt(a -> a).average().orElse(0);
String ids = IntStream.rangeClosed(1, 3).mapToObj(String::valueOf).collect(Collectors.joining(","));
```''',
         pitfall=r'''A stream can be consumed **once**. Nothing runs until the terminal step. Don't change outside variables inside `map`/`filter`. `.toList()` returns an *immutable* list. Use `parallelStream()` only for big CPU-heavy jobs.''',
         nxt=r'''From a list of words, print the three longest ones, uppercased, with a single stream chain.'''),
    dict(id="records", name="Records & data classes", days=[13, 14, 20], keys=["record", "compact constructor", "immutable", "data class", "dto", "tostring", "accessor", "pojo", "lombok", "value object"],
         what=r'''`record Item(String name, double price) {}` is one line that gives you the fields, a constructor, accessors (`item.name()`), and correct `equals`, `hashCode` and `toString`. Records are shallowly immutable.''',
         where=r'''- **REST DTOs:** Spring + Jackson serialise records straight to JSON.
- **Database rows:** map a `ResultSet` row onto a record.
- **Return several values** from a method (`record MinMax(int min, int max)`).
- **Replacing Lombok / boilerplate getters** in modern Java 17-21 code.''',
         how=r'''```java
record Item(String name, double price) {
    Item {                                           // compact constructor = validation
        if (price < 0) throw new IllegalArgumentException("price must be >= 0");
    }
    Item withDiscount(double pct) { return new Item(name, price * (1 - pct / 100)); }
}
Item tea = new Item("tea", 49);
System.out.println(tea);                              // Item[name=tea, price=49.0]
System.out.println(tea.equals(new Item("tea", 49)));  // true
```''',
         pitfall=r'''"Immutable" is shallow: a `List` field can still be changed from outside, so copy it with `List.copyOf(...)` in the constructor. There are no setters; build a changed *copy*. Accessors are `p.name()`, not `getName()`.''',
         nxt=r'''Create `record Order(int id, List<Item> items)` and compute the order total with a stream.'''),
    dict(id="nested_data", name="Nested data & JSON-style structures", days=[13, 16], keys=["json", "nested", "map<string", "list<map", "jackson", "gson", "parse json", "serialize", "deserialize", "api response", "nested map", "objectmapper", "text block"],
         what=r'''Real data is **nested**: lists inside objects inside lists. In Java you model it with `record`s plus `List` / `Map`, and libraries such as **Jackson** or **Gson** convert JSON text into those typed objects and back.''',
         where=r'''- **Every web API** (payments, maps, weather, GitHub) speaks JSON.
- **Kafka messages, Elasticsearch documents and NoSQL stores** (MongoDB, DynamoDB) hold JSON-like data.
- **Android apps:** Retrofit + Gson/Moshi turn a server response into model classes.
- **Config files and app settings.**''',
         how=r'''```java
record Order(int id, double amt) {}
record User(String name, List<Order> orders) {}

User ana = new User("Ana", List.of(new Order(1, 90), new Order(2, 40)));
double total = ana.orders().stream().mapToDouble(Order::amt).sum();   // 130.0

// With Jackson:  User u = new ObjectMapper().readValue(jsonText, User.class);
// Unknown shape?  Map<String, Object> raw = mapper.readValue(jsonText, new TypeReference<>() {});
```
Read nested data **one level at a time**: print each level until you see the shape.''',
         pitfall=r'''Avoid `Map<String, Object>` plus casts when the shape is known (a wrong cast is a `ClassCastException`). Real APIs omit fields, so expect `null`s; and a typed record must match the JSON field names.''',
         nxt=r'''Sum all `amt` values across a `List<User>` with `flatMap`.'''),
    dict(id="files_nio", name="Files & java.nio.file", days=[15, 21], keys=["file", "files", "path", "paths.get", "path.of", "readalllines", "readstring", "writestring", "files.lines", "files.walk", "exists", "createdirectories", "nio", "utf-8", "standardcharsets", "standardopenoption", "filenotfoundexception", "nosuchfileexception", "directory", "folder", "read file", "write file"],
         what=r'''`java.nio.file` is the modern file API: `Path` describes a location, `Files` reads and writes it (`readAllLines`, `readString`, `writeString`, `lines`, `walk`, `list`). Text defaults to UTF-8.''',
         where=r'''- **Reading data exports, logs and configs** at the start of almost every batch job.
- **Automation:** rename or sort thousands of files, nightly backups, report generation.
- **Log analysis:** stream a 1 GB log with `Files.lines` and keep only `ERROR` lines.
- **Build tools** (Maven, Gradle) are largely a smart walker over a file tree.''',
         how=r'''```java
Path log = Path.of("datasets", "app.log");
List<String> errors = Files.readAllLines(log).stream()
        .filter(l -> l.contains("ERROR")).toList();
Files.write(Path.of("errors.txt"), errors);                  // overwrites by default

try (Stream<String> lines = Files.lines(log)) {              // lazy, for huge files
    System.out.println(lines.filter(l -> l.contains("WARN")).count());
}
```''',
         pitfall=r'''`Files.write` / `writeString` **replace** the file unless you pass `StandardOpenOption.APPEND`. Streams from `Files.lines`, `list` and `walk` must be closed (use try-with-resources). Relative paths start from the *working directory*, so print `Path.of("").toAbsolutePath()` when a file "isn't found".''',
         nxt=r'''Count how many lines of `app.log` contain WARN, then append the count to `summary.txt`.'''),
    dict(id="csv", name="CSV files", days=[16], keys=["csv", "split(\",\")", "header", "delimiter", "opencsv", "commons-csv", "bufferedreader", "readline", "parseint", "parsedouble", "spreadsheet", "excel export", "quoted field", "bom"],
         what=r'''CSV is plain-text rows of values separated by commas: the universal spreadsheet export. In Java you read the lines, skip the header, `split` each line and **convert** the text into numbers.''',
         where=r'''- **Bank statements, sales exports, analytics dashboards** all download as CSV.
- **Data engineering:** the first step of nearly every pipeline.
- **Bulk imports** of users or products into a system.''',
         how=r'''```java
record Sale(String region, double price, int qty) {}

List<Sale> sales = new ArrayList<>();
List<String> lines = Files.readAllLines(Path.of("datasets", "sales.csv"));
for (String line : lines.subList(1, lines.size())) {          // skip header
    String[] c = line.split(",");
    sales.add(new Sale(c[0].trim(), Double.parseDouble(c[1]), Integer.parseInt(c[2])));
}
double revenue = sales.stream().mapToDouble(s -> s.price() * s.qty()).sum();
```''',
         pitfall=r'''`split(",")` breaks on quoted fields like `"Sharma, Priya"`; use **Apache Commons CSV** or **OpenCSV** for real files. `split` also drops trailing empty fields (use `split(",", -1)`). Every value arrives as text: convert, and expect a stray BOM on Excel exports.''',
         nxt=r'''Total revenue per region using a `Map<String, Double>` and `merge`.'''),
    dict(id="exceptions", name="Exceptions: try / catch / throw", days=[17], keys=["try", "catch", "finally", "throw", "throws", "exception", "checked exception", "unchecked", "runtimeexception", "custom exception", "ioexception", "nullpointerexception", "numberformatexception", "stack trace", "printstacktrace", "error handling", "illegalargumentexception", "robust"],
         what=r'''Errors are **objects that stop your program unless you handle them**. `try/catch` says "if this specific thing goes wrong, do this instead". *Checked* exceptions (like `IOException`) must be caught or declared with `throws`; *unchecked* ones (`RuntimeException`) need not be.''',
         where=r'''- **Anything touching the outside world fails sometimes:** files missing, network down, a user typing "abc" for age.
- **Web servers** must not crash on one bad request: Spring turns exceptions into a 400 or 500 response (`@ExceptionHandler`).
- **Pipelines** log a bad row, skip it, and keep going.
- **Payments:** retry on a network `IOException`, but never silently ignore a failure.''',
         how=r'''```java
static int readAge(String text) {
    try {
        return Integer.parseInt(text.trim());
    } catch (NumberFormatException e) {      // the *specific* error
        return -1;
    }
}
static void setAge(int age) {
    if (age <= 0) throw new IllegalArgumentException("age must be positive: " + age);
}
```
Wrap and keep the cause: `throw new OrderException("save failed", e);`.''',
         pitfall=r'''An **empty `catch`** swallows the problem for ever. `catch (Exception e)` is too broad and `e.printStackTrace()` is not logging. Order catches from most specific to most general.''',
         nxt=r'''Wrap `Files.readAllLines` so a missing file prints a friendly message and the program continues.'''),
    dict(id="try_resources", name="try-with-resources", days=[17, 28], keys=["try-with-resources", "autocloseable", "close", "resource leak", "closeable", "inputstream", "connection", "scanner close", "finally", "try (", "resource"],
         what=r'''`try (var in = Files.newBufferedReader(path)) { ... }` **closes the resource automatically** when the block ends, even if an exception is thrown. It is Java's version of Python's `with`.''',
         where=r'''- **Database connections** (JDBC): an unclosed one eventually exhausts the pool and the whole site stops answering.
- **File and network streams:** "too many open files" outages come from leaks.
- **HTTP clients, locks, temp files:** anything that must be released.''',
         how=r'''```java
try (BufferedReader in = Files.newBufferedReader(Path.of("orders.txt"));
     PrintWriter out = new PrintWriter("copy.txt")) {      // several resources: separate with ;
    String line;
    while ((line = in.readLine()) != null) {
        out.println(line.toUpperCase());
    }
}   // both closed here, in reverse order, no finally needed
```''',
         pitfall=r'''Only types implementing `AutoCloseable` work. Closing a `Scanner(System.in)` also closes standard input for the rest of the program. Remember `Files.lines`, `Files.list` and `Files.walk` streams need it too.''',
         nxt=r'''Rewrite an old `try/finally { reader.close(); }` as try-with-resources.'''),
    dict(id="logging", name="Logging", days=[17], keys=["logging", "logger", "java.util.logging", "slf4j", "log4j", "logback", "log level", "info", "warning", "severe", "debug", "system.out.println", "log file"],
         what=r'''Logging is `System.out.println` for grown-ups: levels (`FINE`, `INFO`, `WARNING`, `SEVERE`), timestamps, and the ability to send messages to files or a central service.''',
         where=r'''- **Production servers:** the only way to know what happened at 3 a.m.
- **Spring Boot** uses SLF4J + Logback by default; Elasticsearch/Kibana stacks collect the logs of whole fleets.
- **Batch jobs:** a log shows which of 10,000 items failed.
- **Security:** the 2021 Log4Shell vulnerability in the Log4j library shows how universal logging libraries are.''',
         how=r'''```java
private static final Logger LOG = Logger.getLogger(OrderService.class.getName());

LOG.info("Processed " + rows + " rows");
LOG.log(Level.WARNING, "Row {0} failed", 7);
LOG.log(Level.SEVERE, "Could not save order", exception);   // passes the stack trace too
// SLF4J (Spring Boot):  log.info("Processed {} rows", rows);
```''',
         pitfall=r'''Never log passwords or tokens. Log the *exception object* (not just `e.getMessage()`) so the stack trace is kept. The default level hides `FINE`/`DEBUG`; that's why your debug lines "disappear".''',
         nxt=r'''Replace three `System.out.println` calls in a program with `LOG.info` / `LOG.warning`.'''),
    dict(id="packages_build", name="Packages, imports & Maven/Gradle", days=[18], keys=["package", "import", "maven", "gradle", "pom", "pom.xml", "build.gradle", "dependency", "jar", "classpath", "mvn", "gradlew", "wrapper", "artifact", "groupid", "java.util", "wildcard import", "static import", "build tool"],
         what=r'''A **package** (`com.shop.billing`) organises classes into folders; `import` brings a class into scope. **Maven** and **Gradle** are build tools that download dependencies, compile, test and package your app into a `.jar`. `pom.xml` / `build.gradle` describe the project.''',
         where=r'''- **Every enterprise Java project** starts from a `pom.xml` or `build.gradle` (Spring Initializr generates one).
- **CI servers** (Jenkins, GitHub Actions) run `mvn test` or `./gradlew build` on every commit.
- **Android apps** are built with Gradle.
- **Teams** share one build file so everyone has the same library versions.''',
         how=r'''```xml
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
  <version>2.17.2</version>
</dependency>
```
```text
mvn test                      # compile + run tests
mvn package                   # builds target/app.jar
java -jar target/app.jar      # run it anywhere with a JDK/JRE
```''',
         pitfall=r'''The package line must match the folder path (`package com.shop;` lives in `com/shop/`). "package does not exist" usually means a missing dependency or a typo in the import. Use the build wrapper (`mvnw`/`gradlew`) so teammates need no manual install.''',
         nxt=r'''Open a `pom.xml` and name its `groupId`, `artifactId` and two dependencies.'''),
    dict(id="datetime", name="java.time: dates & times", days=[18], keys=["java.time", "localdate", "localdatetime", "zoneddatetime", "instant", "duration", "period", "datetimeformatter", "chronounit", "date", "time", "timezone", "calendar", "simpledateformat", "plusdays", "today"],
         what=r'''`java.time` is the modern, immutable date API: `LocalDate` (a day), `LocalDateTime`, `ZonedDateTime`, `Instant` (a point on the global timeline), `Duration` and `Period`.''',
         where=r'''- **Invoices and subscriptions:** due dates, renewal dates, "30 days from today".
- **Booking and airline systems:** time zones are everything.
- **SLAs and reports:** the last 7 days, month-to-date.
- **Logs and events** stored as UTC `Instant`s.''',
         how=r'''```java
LocalDate today = LocalDate.of(2026, 11, 16);
LocalDate due = today.plusDays(30);
long days = ChronoUnit.DAYS.between(today, due);                 // 30
String text = due.format(DateTimeFormatter.ofPattern("dd MMM yyyy"));
Instant now = Instant.now();                                      // store this, show local time later
```''',
         pitfall=r'''Avoid the old `Date`, `Calendar` and `SimpleDateFormat` (confusing, not thread-safe). Months are 1-12 in `java.time`. `LocalDate` has no time zone, so don't use it for "the moment something happened".''',
         nxt=r'''Print the date 100 days from today and which weekday it is.'''),
    dict(id="classes", name="Classes, objects & constructors", days=[19, 21], keys=["class", "object", "constructor", "this", "field", "attribute", "method", "instance", "new", "encapsulation", "private", "getter", "setter", "tostring", "hashcode", "oop", "state", "static"],
         what=r'''A **class** is a blueprint; an **object** is one thing built from it with `new`, bundling data (fields) with behaviour (methods). The constructor sets it up, `this` means "this particular object", and `private` fields protect the rules.''',
         where=r'''- **Anything with state and rules:** `BankAccount`, `User`, `Order`, `Player`.
- **Frameworks:** Spring beans, JPA entities, Android `Activity` classes, Minecraft mods are all classes.
- **Domain models** in banking and insurance encode business rules (a balance can't go negative) inside the class.''',
         how=r'''```java
class Account {
    private final String owner;
    private double balance;

    Account(String owner, double balance) {
        this.owner = owner;                 // this.field = parameter
        this.balance = balance;
    }
    void deposit(double amt) {
        if (amt <= 0) throw new IllegalArgumentException("amount must be positive");
        balance += amt;
    }
    double getBalance() { return balance; }
    @Override public String toString() { return owner + ": ₹" + balance; }
}
Account acc = new Account("Ana", 0);
acc.deposit(500);
System.out.println(acc);                    // Ana: ₹500.0
```''',
         pitfall=r'''Forgetting `this.` when a parameter has the same name as the field: `balance = balance;` assigns the parameter to itself and the field stays `0`. If you override `equals` you must override `hashCode` too.''',
         nxt=r'''Add a `withdraw` that refuses to go below zero by throwing an exception.'''),
    dict(id="inheritance", name="Inheritance, polymorphism & abstract classes", days=[20], keys=["inheritance", "inherit", "extends", "super", "override", "@override", "polymorphism", "abstract", "abstract class", "protected", "composition", "instanceof", "final class"],
         what=r'''Inheritance lets a class **reuse and specialise** another (`class Savings extends Account`). *Polymorphism* means different classes answer the same method call in their own way, so code written against the parent works with every child.''',
         where=r'''- **Frameworks expect you to subclass:** custom exceptions (`extends RuntimeException`), servlets, JUnit test base classes, Android `AppCompatActivity`.
- **Plug-in designs:** `CardPayment` and `UpiPayment` both implement `pay()`; checkout code doesn't care which.
- **GUI toolkits and game engines** are class hierarchies.''',
         how=r'''```java
abstract class Payment {
    abstract void pay(double amt);
}
class CardPayment extends Payment {
    @Override void pay(double amt) { System.out.println("Card charged ₹" + amt); }
}
class UpiPayment extends Payment {
    @Override void pay(double amt) { System.out.println("UPI request ₹" + amt); }
}
for (Payment p : List.of(new CardPayment(), new UpiPayment())) p.pay(499);
```
Prefer **composition** (an object *has* another) over deep inheritance.''',
         pitfall=r'''Always write `@Override`: a typo in the method name then becomes a compile error instead of a silent new method. Deep hierarchies get confusing fast; don't call overridable methods from a constructor.''',
         nxt=r'''Add a `WalletPayment` and loop over a mixed list without changing the checkout loop.'''),
    dict(id="interfaces_enums", name="Interfaces, enums & sealed types", days=[20], keys=["interface", "implements", "default method", "enum", "enum values", "sealed", "permits", "switch pattern", "pattern matching", "values()", "valueof", "ordinal", "contract", "constants"],
         what=r'''An **interface** is a contract ("anything with `pay()`"). An **enum** is a fixed set of named constants (`NEW, PAID, SHIPPED`) that can carry fields and methods. A **sealed** type lists exactly which classes may implement it, so a `switch` can be checked for completeness.''',
         where=r'''- **`List`, `Map`, `Comparable`, `Runnable`** are all interfaces; Spring repositories are `interface UserRepository`.
- **Enums** model order status, HTTP methods, weekdays, roles, card types.
- **Sealed result types** (`Success` / `Failure`) make payment and parsing code explicit.
- **Mocking in tests** relies on interfaces.''',
         how=r'''```java
enum Status { NEW, PAID, SHIPPED }

sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}

static double area(Shape s) {
    return switch (s) {
        case Circle c -> Math.PI * c.r() * c.r();
        case Square q -> q.side() * q.side();
    };                                    // no default needed: the compiler knows all cases
}
```''',
         pitfall=r'''Compare enums with `==`. `Status.valueOf("OLD")` throws if the name doesn't exist. Don't store `ordinal()` in a database: reordering the enum would silently change the meaning of old data.''',
         nxt=r'''Add a `Triangle` to the sealed interface and watch the compiler point at the `switch`.'''),
    dict(id="generics", name="Generics", days=[22], keys=["generic", "generics", "<t>", "type parameter", "diamond", "<>", "wildcard", "? extends", "raw type", "type erasure", "bounded", "comparable", "list<string>"],
         what=r'''Generics let one class or method work with **many types while staying type-safe**: `List<String>` can only hold strings, `Box<T>` holds whatever `T` you choose. The compiler checks it, so no casts are needed.''',
         where=r'''- **Collections:** `List<Order>`, `Map<String, User>`.
- **Frameworks:** `ResponseEntity<T>`, `Optional<User>`, `Repository<T, ID>`, `CompletableFuture<T>`.
- **API wrappers** such as `ApiResponse<T>` or `Result<T, E>` in your own libraries.''',
         how=r'''```java
class Box<T> {
    private final T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}
static <T extends Comparable<T>> T maxOf(List<T> items) {
    T best = items.get(0);
    for (T it : items) if (it.compareTo(best) > 0) best = it;
    return best;
}
System.out.println(maxOf(List.of(3, 9, 4)));        // 9
```''',
         pitfall=r'''Generics don't work with primitives (`List<int>` is illegal; use `List<Integer>`). Type erasure means you can't `new T()` or test `instanceof List<String>`. Raw types (`List` without `<>`) switch the safety off. `List<Integer>` is *not* a `List<Number>`.''',
         nxt=r'''Write a generic `Pair<A, B>` record and a method that swaps it.'''),
    dict(id="optional", name="Optional & avoiding null", days=[22], keys=["optional", "orelse", "orelsethrow", "orelseget", "ifpresent", "ispresent", "optional.of", "ofnullable", "null", "nullpointerexception", "npe", "empty", "findfirst", "findbyid"],
         what=r'''`Optional<T>` is a box that **may or may not contain a value**. It makes "this might be missing" visible in the method signature and gives safe ways to deal with it (`map`, `orElse`, `ifPresent`).''',
         where=r'''- **Spring Data:** `userRepository.findById(id)` returns `Optional<User>`.
- **Streams:** `findFirst()`, `max()`, `min()` return Optionals.
- **Config and lookup code:** "the setting if it exists, else a default".
- **Fewer production `NullPointerException`s** (the classic Java crash).''',
         how=r'''```java
Optional<User> found = users.stream().filter(u -> u.id() == 7).findFirst();
String name = found.map(User::name).orElse("guest");
found.ifPresent(u -> System.out.println("Welcome " + u.name()));
User must = found.orElseThrow(() -> new NoSuchElementException("user 7 not found"));
```''',
         pitfall=r'''Calling `get()` on an empty Optional throws `NoSuchElementException`. `orElse(expensive())` always runs `expensive()`; use `orElseGet(() -> ...)`. Use Optional for *return values*, not for fields or parameters, and never return `null` from a method that returns Optional.''',
         nxt=r'''Write `Optional<Double> parsePrice(String text)` that returns empty instead of throwing.'''),
    dict(id="regex", name="Regular expressions", days=[23], keys=["regex", "pattern", "matcher", "matches", "find", "group", "replaceall", "split", "\\d", "regular expression", "named group", "validation", "pattern.compile"],
         what=r'''A regex is a **mini-language describing text patterns**: "five digits, a dash, five digits". Java uses `Pattern` (the compiled pattern) and `Matcher` (the search over a text).''',
         where=r'''- **Extracting emails, phones and order ids** from messy text.
- **Log parsing:** pull the IP and status code out of every line.
- **Validation:** is this a plausible PIN, postcode or id?
- **Cleaning:** strip everything except digits (`replaceAll("\\D", "")`).''',
         how=r'''```java
Pattern p = Pattern.compile("(?<user>[\\w.]+)@(?<domain>[\\w.]+)");
Matcher m = p.matcher("mail ana@x.com now");
if (m.find()) System.out.println(m.group("domain"));      // x.com

List<String> phones = Pattern.compile("\\d{5}-\\d{5}")
        .matcher("Call 98765-43210 or 91234-56789").results()
        .map(MatchResult::group).toList();
```''',
         pitfall=r'''Backslashes must be doubled inside Java strings (`"\\d"`). `matches()` demands the **whole** text matches; `find()` looks anywhere. Compile a `Pattern` once and reuse it, not inside a loop. Nested quantifiers can freeze a server (catastrophic backtracking).''',
         nxt=r'''Extract all #hashtags from a tweet.'''),
    dict(id="clean_code", name="Clean code, naming & constants", days=[23], keys=["clean code", "naming", "camelcase", "magic number", "constant", "static final", "immutability", "small method", "refactor", "readability", "javadoc", "checkstyle", "spotless", "sonarqube", "code style", "google java style", "readable"],
         what=r'''Clean code means **small methods, meaningful names, no magic numbers and little hidden state**. Java convention: `PascalCase` classes, `camelCase` methods and variables, `UPPER_SNAKE_CASE` constants.''',
         where=r'''- **Code reviews:** readable code is the main thing teammates judge.
- **Quality gates** (SonarQube, Checkstyle, Spotless in CI) fail the build on messy code at banks and insurers.
- **IDE inspections** (IntelliJ IDEA) underline smells as you type.
- **Books and talks** such as *Effective Java* are the common vocabulary of Java teams.''',
         how=r'''```java
private static final double GST_RATE = 0.18;
private static final int FREE_SHIPPING_FROM = 999;

/** Returns the payable amount including GST. */
static double payable(double subtotal) {
    double withTax = subtotal * (1 + GST_RATE);
    return subtotal >= FREE_SHIPPING_FROM ? withTax : withTax + shippingFee();
}
```''',
         pitfall=r'''A bare `0.18` in the middle of a formula tells nobody what it is. Comments that repeat the code are noise; explain *why*. Methods with 6+ parameters usually want a record.''',
         nxt=r'''Pick one 20-line method of yours and split it into three well-named methods.'''),
    dict(id="junit", name="Testing with JUnit 5 & git", days=[24], keys=["junit", "test", "@test", "assert", "assertequals", "assertthrows", "assertall", "parameterizedtest", "mockito", "mock", "tdd", "git", "commit", "branch", "ci", "coverage", "jacoco", "mvn test", "unit test"],
         what=r'''A test is code that **checks your code**: call a method, `assertEquals(expected, actual)`. JUnit 5 finds methods marked `@Test` and reports passes and failures. Git records every change so you can undo and collaborate.''',
         where=r'''- **Every professional codebase** blocks merging when tests fail (continuous integration).
- **Spring Boot** ships with JUnit and Mockito ready to use (`@SpringBootTest`).
- **Safe refactoring:** change anything, re-run, know instantly if something broke.
- **Git/GitHub:** your portfolio, teamwork and rollbacks.''',
         how=r'''```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CartTest {
    @Test void totalOfTwoItems() { assertEquals(30, Cart.total(List.of(10, 20))); }
    @Test void emptyCartIsZero() { assertEquals(0, Cart.total(List.of())); }
    @Test void negativePriceRejected() {
        assertThrows(IllegalArgumentException.class, () -> Cart.total(List.of(-5)));
    }
}
```
Run `mvn test` (or the JUnit console launcher). Test the **edges**: empty, zero, huge, wrong input.''',
         pitfall=r'''`assertEquals(expected, actual)`: the order matters for readable failure messages. Doubles need a tolerance: `assertEquals(0.3, a + b, 1e-9)`. Tests must not depend on each other, the clock or random numbers; happy-path-only tests give false confidence.''',
         nxt=r'''Write a test that proves a method throws on a negative price.'''),
    dict(id="collectors", name="Collectors & groupingBy", days=[25, 26], keys=["collectors", "groupingby", "counting", "averagingdouble", "summingdouble", "partitioningby", "tomap", "joining", "summarystatistics", "top n", "top-n", "reporting", "group by", "aggregate", "bar chart"],
         what=r'''`Collectors` end a stream by **grouping and summarising**, like SQL `GROUP BY` or a pandas `groupby`: `groupingBy` splits into groups, a *downstream* collector (`counting`, `summingDouble`, `averagingInt`) summarises each one.''',
         where=r'''- **Sales dashboards:** revenue per region, best product per month.
- **Log analytics:** requests per status code, errors per service.
- **A/B-test and survey summaries.**
- **Spring report endpoints** that return grouped statistics as JSON.''',
         how=r'''```java
record Sale(String region, String product, double price, int qty) {}

Map<String, Double> byRegion = sales.stream().collect(
        Collectors.groupingBy(Sale::region, TreeMap::new,
                Collectors.summingDouble(s -> s.price() * s.qty())));

List<Map.Entry<String, Double>> top3 = byRegion.entrySet().stream()
        .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
        .limit(3).toList();
for (var e : top3) System.out.printf("%-8s %,10.2f%n", e.getKey(), e.getValue());
```''',
         pitfall=r'''`toMap` throws `IllegalStateException` on duplicate keys unless you pass a merge function. `groupingBy` returns an unordered `HashMap` by default. Report numbers with `double`s are fine, but money should be `BigDecimal` or whole cents.''',
         nxt=r'''Top 3 products by revenue, with a text bar made from `"#".repeat(...)`.'''),
    dict(id="http_client", name="HttpClient & HttpServer", days=[27], keys=["http", "httpclient", "httprequest", "httpresponse", "httpserver", "com.sun.net.httpserver", "api", "status code", "get", "post", "header", "timeout", "bearer", "rate limit", "endpoint", "404", "429", "request", "response", "web request"],
         what=r'''`java.net.http.HttpClient` (Java 11+) sends requests to an API and gives you the status code and body. The JDK also contains `com.sun.net.httpserver.HttpServer`, a tiny server good for learning and local tests.''',
         where=r'''- **Everything connected:** weather, payments, maps, GitHub, OpenAI and Slack all expose HTTP APIs.
- **Microservices** call each other with HTTP clients (Spring's `RestClient` / `WebClient` are built on the same ideas).
- **Health checks and webhooks** between systems.
- **Data collection** for analysis or machine learning.''',
         how=r'''```java
HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
HttpRequest req = HttpRequest.newBuilder(URI.create("https://api.github.com/repos/openjdk/jdk"))
        .timeout(Duration.ofSeconds(10)).header("Accept", "application/json").GET().build();
HttpResponse<String> res = client.send(req, HttpResponse.BodyHandlers.ofString());
if (res.statusCode() != 200) throw new IOException("HTTP " + res.statusCode());
System.out.println(res.body().length());
```
Status codes: **200** ok · **201** created · **400** bad request · **401** not allowed · **404** not found · **429** slow down · **500** their bug.''',
         pitfall=r'''A 404 or 500 is **not** an exception: check `statusCode()` yourself. Always set timeouts, reuse one `HttpClient`, respect rate limits, and read secret tokens from environment variables (`System.getenv("API_TOKEN")`), never from source code.''',
         nxt=r'''Start a local `HttpServer` returning `{"ok":true}` and call it with `HttpClient`.'''),
    dict(id="jdbc", name="JDBC & SQL", days=[28], keys=["jdbc", "sql", "sqlite", "select", "preparedstatement", "resultset", "connection", "drivermanager", "datasource", "hikaricp", "insert", "update", "delete", "join", "group by", "transaction", "commit", "rollback", "sql injection", "primary key", "jpa", "hibernate", "database", "table"],
         what=r'''SQL **asks questions of tables** (`SELECT` what, `FROM` where, `WHERE` filter, `GROUP BY` summarise, `JOIN` combine). **JDBC** is Java's standard way to send SQL to a database (SQLite, PostgreSQL, MySQL, Oracle...) and read the rows back.''',
         where=r'''- **Almost every enterprise back-end** (banks, insurers, e-commerce, telecom) stores its data in a SQL database.
- **Spring JdbcTemplate, JPA and Hibernate** are layers on top of JDBC.
- **Analysts** live in SQL; Java services run the same queries on a schedule.
- **Connection pools** (HikariCP) keep a few open connections ready for thousands of requests.''',
         how=r'''```java
String sql = "SELECT region, SUM(amt) FROM sales WHERE amt > ? GROUP BY region";
try (Connection con = DriverManager.getConnection("jdbc:sqlite:shop.db");
     PreparedStatement ps = con.prepareStatement(sql)) {
    ps.setDouble(1, 100);                              // fills the first ? (1-based!)
    try (ResultSet rs = ps.executeQuery()) {
        while (rs.next()) {
            System.out.println(rs.getString(1) + " " + rs.getDouble(2));
        }
    }
}
```''',
         pitfall=r'''**Never** build SQL by gluing user text into the string (SQL injection): use `?` placeholders. JDBC indexes start at **1**. Close connections (try-with-resources). For several related changes use `con.setAutoCommit(false)`, then `commit()` or `rollback()`.''',
         nxt=r'''Write a query for the top 3 customers by total spend and print them.'''),
    dict(id="pipeline", name="Data pipelines (ETL) & project structure", days=[29], keys=["pipeline", "etl", "extract", "transform", "load", "capstone", "project structure", "end-to-end", "idempotent", "batch job", "spring batch", "orchestrat"],
         what=r'''A pipeline is **Extract → Transform → Load**: read raw data, clean and reshape it, write a trusted result. Each step is a small, testable method.''',
         where=r'''- **Every company's analytics:** nightly jobs that turn raw exports and logs into dashboards.
- **Banks and insurers** run Spring Batch jobs for statements and settlements.
- **Streaming systems** (Apache Kafka consumers, Spark jobs on the JVM) apply the same idea continuously.
- **Automation:** receipts → database → e-mailed report.''',
         how=r'''```java
static void run(Path in, String dbUrl) throws Exception {
    List<Row> raw = extract(in);               // read
    List<Row> clean = transform(raw);          // fix types, drop duplicates and bad rows
    load(clean, dbUrl);                        // write to SQLite
    LOG.info("rows: " + raw.size() + " -> " + clean.size());
}
```
Log row counts at each step: they reveal silent data loss.''',
         pitfall=r'''Make runs repeatable (running twice must not duplicate rows: `INSERT OR REPLACE` or clear first) and never modify the raw input.''',
         nxt=r'''Add a validation step that rejects negative prices and logs how many rows it dropped.'''),
    dict(id="rest_spring", name="REST APIs & Spring Boot", days=[30], keys=["rest", "rest api", "spring", "spring boot", "restcontroller", "@getmapping", "@postmapping", "requestbody", "responseentity", "controller", "endpoint", "route", "dto", "bean validation", "swagger", "openapi", "actuator", "backend", "microservice"],
         what=r'''A REST API turns your methods into **web endpoints** (`GET /items/7`) that other programs (a website, a phone app) can call, with JSON in and out and the right HTTP status codes. **Spring Boot** is the framework most Java teams use to build them.''',
         where=r'''- **Back-ends for web and mobile apps** at banks, insurers, e-commerce and telecoms are overwhelmingly Spring Boot.
- **Microservices:** dozens of small APIs that call each other.
- **Internal tools and webhooks:** trigger your code from a button or another system.
- **Auto-generated docs** (OpenAPI/Swagger UI) come almost for free.''',
         how=r'''```java
@RestController
@RequestMapping("/items")
class ItemController {
    private final Map<Integer, Item> store = new ConcurrentHashMap<>();

    @PostMapping
    ResponseEntity<Item> add(@RequestBody Item item) {
        if (item.price() < 0) return ResponseEntity.badRequest().build();   // 400
        store.put(item.id(), item);
        return ResponseEntity.status(201).body(item);                        // 201 Created
    }
    @GetMapping("/{id}")
    ResponseEntity<Item> get(@PathVariable int id) {
        Item it = store.get(id);
        return it == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(it);
    }
}
```
In the course you first build the same routes with the JDK's `HttpServer`, so you see what Spring does for you.''',
         pitfall=r'''Validate input at the edge (`@Valid` + Bean Validation), return correct codes (201, 400, 404), expose DTO records rather than database entities, and keep secrets out of `application.properties` in git.''',
         nxt=r'''Add `DELETE /items/{id}` that returns 204, or 404 when the id is unknown.'''),
    dict(id="concurrency", name="Concurrency basics: threads & executors", days=[27, 30], keys=["thread", "threads", "executorservice", "executors", "completablefuture", "runnable", "synchronized", "atomicinteger", "concurrenthashmap", "race condition", "deadlock", "virtual thread", "parallel", "async", "volatile", "lock", "future", "concurrency", "thread.sleep"],
         what=r'''A **thread** lets a program do several things at once. An `ExecutorService` manages a pool of threads and runs your tasks (`submit`) for you. Java 21 adds cheap **virtual threads**. The hard part is shared data: two threads changing the same variable can step on each other.''',
         where=r'''- **Web servers** (Tomcat, Spring Boot) handle each request on its own thread.
- **Fetching 50 APIs in parallel** instead of one after another.
- **Background jobs, schedulers and message consumers.**
- **Android:** keep slow work off the UI thread so the app doesn't freeze; trading and gaming systems tune this heavily.''',
         how=r'''```java
try (ExecutorService pool = Executors.newFixedThreadPool(4)) {     // AutoCloseable since Java 19
    List<Future<Integer>> jobs = new ArrayList<>();
    for (String url : urls) {
        jobs.add(pool.submit(() -> fetchStatus(url)));              // runs in the background
    }
    for (Future<Integer> f : jobs) {
        System.out.println(f.get());                                // waits for that result
    }
}   // (method must declare: throws Exception)
AtomicInteger hits = new AtomicInteger();
hits.incrementAndGet();                                             // safe from many threads
```''',
         pitfall=r'''`count++` from several threads **loses updates**: use `AtomicInteger`, `synchronized` or a `ConcurrentHashMap`. `thread.run()` runs in the *current* thread (you want `start()`). A pool that is never shut down keeps the program alive; deadlocks come from locks taken in different orders.''',
         nxt=r'''Run three `Thread.sleep(500)` tasks in a pool and measure that the total is about 0.5 s, not 1.5 s.'''),
]

BY_ID = {e["id"]: e for e in KB}

GENERIC_USAGE = (
    "Here's a reliable way to think about *\"where would I use this?\"* for any Java concept:\n"
    "1. **Find the data:** what real thing does it represent (orders, users, files, readings)?\n"
    "2. **Find the repetition or decision:** what would be painful to do by hand 1,000 times?\n"
    "3. **Find the job:** back-end developer building a Spring Boot service, Android developer, data engineer writing a nightly batch job, or a script automating a boring chore.")


# ---- concept visuals (Mermaid) -------------------------------------------------------------------------
# Used when someone asks "show me a visual" about a concept and no code is attached.
VISUALS = {
    "hello_main": dict(title="From source file to running program", caption="javac turns text into bytecode once, the JVM runs that bytecode on any operating system.",
        mermaid='''flowchart LR
  src["Hello.java<br/>(your text)"] -->|"javac"| bc["Hello.class<br/>(bytecode)"] -->|"java Hello"| jvm["JVM"] --> out(["Welcome to Chai Point"])
  jvm --- os["Windows / Linux / macOS"]'''),
    "output": dict(title="printf fills the holes in a template", caption="Each % placeholder takes the next argument, in order.",
        mermaid='''flowchart LR
  t["printf('Hi %s, %d items, total %.2f%n', ...)"] --> a1["%s gets name"]
  t --> a2["%d gets items"]
  t --> a3["%.2f gets total"]
  a1 --> r(["Hi Priya, 3 items, total 148.50"])
  a2 --> r
  a3 --> r'''),
    "variables": dict(title="A typed variable: the type decides what fits", caption="The compiler refuses to put the wrong kind of value into a variable.",
        mermaid='''flowchart LR
  a["int price = 49"] --> ok1["fits: 49 is a whole number"]
  b["double rate = 0.18"] --> ok2["fits: decimal number"]
  c["String name = 'Ana'"] --> ok3["fits: text"]
  d["int bad = 'hello'"] -.-> err(["compile error: incompatible types"])'''),
    "scanner": dict(title="Scanner turns typed text into values", caption="Everything typed arrives as text. You convert it yourself.",
        mermaid='''sequenceDiagram
  participant U as User
  participant S as Scanner
  participant P as Your program
  P->>U: How many chai?
  U->>S: types 3 and presses Enter
  S-->>P: nextLine() returns the text "3"
  P->>P: Integer.parseInt gives the number 3'''),
    "casting_math": dict(title="Integer division happens BEFORE the assignment", caption="Casting one side to double first keeps the decimals.",
        mermaid='''flowchart TD
  s["sum = 17, count = 4"] --> w["double avg = sum / count"]
  s --> r["double avg = (double) sum / count"]
  w --> w1["17 / 4 as ints = 4"] --> w2["stored as 4.0"]
  r --> r1["17.0 / 4 = 4.25"] --> r2["stored as 4.25"]'''),
    "strings": dict(title="A String is a row of characters with numbered slots", caption="substring(start, end) takes slots from start up to (not including) end.",
        mermaid='''flowchart LR
  subgraph s["String text = 'JAVA21'"]
    direction LR
    c0["J<br/>0"] --- c1["A<br/>1"] --- c2["V<br/>2"] --- c3["A<br/>3"] --- c4["2<br/>4"] --- c5["1<br/>5"]
  end
  s --> r["text.substring(1, 4) gives 'AVA'<br/>text.charAt(0) gives 'J'<br/>text.length() is 6"]'''),
    "equals_ref": dict(title="== compares addresses, equals compares content", caption="Two different objects can hold the same letters.",
        mermaid='''flowchart LR
  a(("a")) --> o1["String object<br/>chai"]
  b(("b")) --> o2["String object<br/>chai"]
  a -. "a == b is false" .- b
  o1 -. "a.equals(b) is true" .- o2'''),
    "conditions": dict(title="if / else if / else: the first true branch wins", caption="Java checks top to bottom and stops at the first condition that is true.",
        mermaid='''flowchart TD
  s(["spend"]) --> c1{"spend >= 5000 ?"}
  c1 -->|yes| g["gold"]
  c1 -->|no| c2{"spend >= 1000 ?"}
  c2 -->|yes| sv["silver"]
  c2 -->|no| b["basic"]'''),
    "for_loops": dict(title="A for loop: set up, test, run the body, step, repeat", caption="for (int i = 0; i < 3; i++): the test is checked before every round.",
        mermaid='''flowchart TD
  s(["int i = 0"]) --> t{"i is less than 3 ?"}
  t -->|yes| b["run the body"]
  b --> st["i++"]
  st --> t
  t -->|no| d(["loop ends"])'''),
    "while_loops": dict(title="A while loop: check, run, check again", caption="Something inside the body must change the condition, or it never stops.",
        mermaid='''flowchart TD
  s(["attempts = 0"]) --> c{"attempts less than 3 ?"}
  c -->|yes| p["ask for PIN"]
  p --> ok{"correct?"}
  ok -->|yes| w(["Welcome (break)"])
  ok -->|no| i["attempts++"]
  i --> c
  c -->|no| bl(["Card blocked"])'''),
    "arrays": dict(title="An array is a fixed row of numbered boxes", caption="Indexes run from 0 to length - 1. One step past the end is an exception.",
        mermaid='''flowchart LR
  subgraph arr["int[] scores = {72, 95, 88}"]
    direction LR
    i0["0<br/>72"] --- i1["1<br/>95"] --- i2["2<br/>88"]
  end
  arr --> ok["scores[2] is 88"]
  arr -.-> bad(["scores[3] throws ArrayIndexOutOfBoundsException"])'''),
    "arraylist": dict(title="An ArrayList grows as you add", caption="The list hides a bigger array and replaces it when it fills up.",
        mermaid='''flowchart LR
  e["new ArrayList - empty"] -->|"add milk"| a["milk"]
  a -->|"add bread"| b["milk, bread"]
  b -->|"add eggs"| c["milk, bread, eggs"]
  c -->|"remove bread"| d["milk, eggs"]'''),
    "sets": dict(title="Sets and the overlap of two groups", caption="retainAll keeps who is in both, addAll is everyone, removeAll is only the first group.",
        mermaid='''flowchart LR
  m["Monday: ana, raj, li"] --> both["retainAll<br/>raj, li"]
  t["Tuesday: raj, li, sam"] --> both
  m --> all["addAll<br/>ana, raj, li, sam"]
  t --> all'''),
    "hashmap": dict(title="A Map: look up by key, not by position", caption="Counting votes: each key keeps its own running number.",
        mermaid='''flowchart LR
  subgraph votes["Map of String to Integer"]
    k1["'a'"] --> v1["2"]
    k2["'b'"] --> v2["1"]
  end
  x(["votes.merge('a', 1, Integer::sum)"]) --> k1'''),
    "methods": dict(title="A method: inputs, work, one output", caption="return hands the value back to whoever called the method.",
        mermaid='''flowchart LR
  call(["finalPrice(200, 0.18, 50)"]) --> p["parameters<br/>price=200, taxRate=0.18, discount=50"]
  p --> w["work: (price - discount) * 1.18"]
  w --> r(["return 177.0"])
  r --> back(["value flows back to the caller"])'''),
    "recursion": dict(title="Recursion: a method calls a smaller version of itself", caption="Each call waits for the next. The base case starts the answers flowing back.",
        mermaid='''flowchart TD
  a["factorial(3)"] -->|"3 * factorial(2)"| b["factorial(2)"] -->|"2 * factorial(1)"| c["factorial(1) is 1 (base case)"]
  c -.->|"returns 1"| b
  b -.->|"returns 2"| a
  a -.->|"returns 6"| r(["answer"])'''),
    "lambdas": dict(title="A lambda is a function you pass around", caption="removeIf asks the lambda one question per element.",
        mermaid='''flowchart LR
  l["names = Zoya, ana, Raj"] --> f{"is n.length() under 4 ?"}
  f -->|true| rm(["removed: ana, Raj"])
  f -->|false| keep["kept: Zoya"]'''),
    "streams": dict(title="A stream pipeline: source, steps, one final step", caption="Nothing runs until the terminal step (toList, sum, count) is reached.",
        mermaid='''flowchart LR
  src["amounts<br/>900, 120, 640, 75"] -->|"filter a > 500"| f["900, 640"] -->|"map a * 0.9"| m["810, 576"] -->|"sum"| t(["1386"])'''),
    "records": dict(title="One line of record gives you a whole class", caption="Fields, constructor, accessors, equals, hashCode and toString are generated for you.",
        mermaid='''flowchart TD
  r["record Item(String name, double price)"] --> a["constructor Item(name, price)"]
  r --> b["accessors name() and price()"]
  r --> c["equals and hashCode by content"]
  r --> d["toString: Item[name=tea, price=49.0]"]'''),
    "nested_data": dict(title="Nested JSON maps onto records and lists", caption="Read it one level at a time.",
        mermaid='''flowchart TD
  d["User (record)"] --> n["name = 'Ana'"]
  d --> o["orders (List of Order)"]
  o --> o0["[0] Order id=1, amt=90"]
  o --> o1["[1] Order id=2, amt=40"]'''),
    "files_nio": dict(title="Reading and writing files with Path and Files", caption="Files.readAllLines loads everything. Files.lines streams a line at a time, so close it.",
        mermaid='''flowchart LR
  d[("app.log on disk")] -->|"Files.readAllLines"| l["List of lines in memory"] -->|"filter ERROR"| e["error lines"] -->|"Files.write"| o[("errors.txt on disk")]'''),
    "csv": dict(title="CSV rows become typed objects", caption="Every field is text until you parse it.",
        mermaid='''flowchart LR
  f[("sales.csv<br/>north,49.5,3")] -->|"line.split"| r["array of 3 Strings"] -->|"parseDouble / parseInt"| n["Sale(north, 49.5, 3)"]'''),
    "exceptions": dict(title="try / catch: what happens when something goes wrong", caption="Only the matching catch block runs. The program carries on afterwards.",
        mermaid='''flowchart TD
  s(["try: parseInt(text)"]) -->|fine| ok["use the number"]
  s -->|"NumberFormatException"| ex["catch block: return -1"]
  ok --> end1(["continue"])
  ex --> end1'''),
    "try_resources": dict(title="try-with-resources always closes", caption="Resources are closed in reverse order, even when an exception is thrown.",
        mermaid='''flowchart TD
  o["open reader and writer"] --> b["run the block"]
  b -->|"normal end"| c["close writer, then reader"]
  b -->|"exception"| c
  c --> n(["continue or propagate the exception"])'''),
    "packages_build": dict(title="What Maven or Gradle does for you", caption="One build file, the same result on every laptop and CI server.",
        mermaid='''flowchart LR
  pom["pom.xml / build.gradle"] --> dep["download dependencies"] --> comp["compile"] --> tst["run tests"] --> jar["app.jar"] --> run(["java -jar app.jar"])'''),
    "classes": dict(title="Class = blueprint, objects = things built from it", caption="Each object has its own data (fields) but shares the same methods.",
        mermaid='''flowchart TD
  C["class Account<br/>deposit(), toString()"]
  C -->|"new Account('Ana', 0)"| a1["acc1<br/>owner='Ana'<br/>balance=500"]
  C -->|"new Account('Raj', 0)"| a2["acc2<br/>owner='Raj'<br/>balance=0"]'''),
    "inheritance": dict(title="Inheritance: children reuse and specialise the parent", caption="Code written against Payment works with every subclass. That is polymorphism.",
        mermaid='''flowchart TD
  P["Payment (abstract)<br/>pay(amount)"] --> C["CardPayment<br/>pay charges the card"]
  P --> U["UpiPayment<br/>pay sends a UPI request"]
  P --> W["WalletPayment<br/>pay debits the wallet"]
  checkout(["for each Payment p: p.pay(499)"]) -.-> P'''),
    "interfaces_enums": dict(title="A sealed type lists every possible case", caption="The switch needs no default branch because the compiler knows all cases.",
        mermaid='''flowchart TD
  S["sealed interface Shape"] --> C["Circle"]
  S --> Q["Square"]
  sw{"switch on a Shape"} --> C
  sw --> Q
  sw -.-> miss(["add Triangle and the switch fails to compile"])'''),
    "generics": dict(title="Generics: the same class, checked for each type", caption="The compiler remembers what each list may hold, so no casts are needed.",
        mermaid='''flowchart LR
  g["class Box of T"] -->|"T = String"| a["Box of String<br/>only text goes in"]
  g -->|"T = Integer"| b["Box of Integer<br/>only numbers go in"]
  a -.-> x(["Box of String cannot hold 42: compile error"])'''),
    "optional": dict(title="Optional: a box that may be empty", caption="Instead of returning null, return a box and let the caller decide what to do when it is empty.",
        mermaid='''flowchart LR
  f["findFirst"] --> o{"Optional"}
  o -->|"has value"| v["map and use it"]
  o -->|"empty"| d["orElse default<br/>or orElseThrow"]'''),
    "regex": dict(title="A regex scans text for a shape", caption="Pattern.compile builds the shape once, Matcher.find walks through the text.",
        mermaid='''flowchart LR
  p["Pattern '\\\\d{5}-\\\\d{5}'"] --> m["Matcher over the text"]
  t["Call 98765-43210 or 91234-56789"] --> m
  m -->|"find"| r1["98765-43210"]
  m -->|"find again"| r2["91234-56789"]'''),
    "junit": dict(title="A test: arrange, act, assert", caption="If the assertion fails you get a precise message about what differed.",
        mermaid='''flowchart LR
  a["arrange: sample input"] --> b["act: call the method"] --> c{"assertEquals expected, actual"}
  c -->|equal| p(["PASS"])
  c -->|different| f(["FAIL with both values"])'''),
    "collectors": dict(title="groupingBy = split, summarise, combine", caption="The same idea as a pivot table or a SQL GROUP BY.",
        mermaid='''flowchart LR
  df["all sales<br/>(region, price, qty)"] -->|"groupingBy region"| n["North sales"]
  df --> s["South sales"]
  n -->|"summingDouble"| rn["North: 900"]
  s -->|"summingDouble"| rs["South: 450"]
  rn --> out["Map of region to revenue"]
  rs --> out'''),
    "http_client": dict(title="An HTTP call: request, then response", caption="Always check the status code before using the body.",
        mermaid='''sequenceDiagram
  participant App as Your Java app
  participant API as Web API
  App->>API: GET /repos/openjdk/jdk (with timeout)
  API-->>App: 200 OK plus JSON body
  Note over App: check statusCode, then parse the body'''),
    "jdbc": dict(title="A JDBC query from Java to the database and back", caption="PreparedStatement keeps the SQL and the user's values separate, which stops SQL injection.",
        mermaid='''sequenceDiagram
  participant J as Java code
  participant D as Database
  J->>D: open Connection
  J->>D: prepare 'SELECT ... WHERE amt over ?'
  J->>D: setDouble 1 = 100, executeQuery
  D-->>J: ResultSet (rows)
  J->>J: while rs.next read the columns
  J->>D: close everything'''),
    "pipeline": dict(title="An ETL pipeline: Extract, Transform, Load", caption="Each step is one small method you can test on its own.",
        mermaid='''flowchart LR
  raw[("raw CSV")] -->|extract| a["rows as records"] -->|transform| b["clean rows<br/>(types fixed, bad rows dropped)"] -->|load| out[("SQLite database")]'''),
    "rest_spring": dict(title="What happens when someone calls your endpoint", caption="Spring parses the JSON, calls your method, and turns the return value into a response.",
        mermaid='''sequenceDiagram
  participant C as Client (browser or app)
  participant S as Spring Boot
  participant M as Your controller method
  C->>S: POST /items with JSON body
  S->>S: convert JSON to an Item record and validate
  S->>M: add(item)
  M-->>S: ResponseEntity 201 plus item
  S-->>C: 201 Created plus JSON'''),
    "concurrency": dict(title="Life of a thread", caption="A pool reuses threads for many tasks. Blocked threads wait without using the CPU.",
        mermaid='''stateDiagram-v2
  [*] --> NEW
  NEW --> RUNNABLE : start
  RUNNABLE --> BLOCKED : waits for a lock
  BLOCKED --> RUNNABLE : lock acquired
  RUNNABLE --> WAITING : sleep or future get
  WAITING --> RUNNABLE : woken up
  RUNNABLE --> TERMINATED : run ends
  TERMINATED --> [*]'''),
}
