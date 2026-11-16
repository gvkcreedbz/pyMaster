// SOLUTION FILE - try the hint ladder first!
/* Day 19 - Practice: classes and objects.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 * Every exercise is a class: write the fields, the constructor and the methods.
 */
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.*;
class Practice {
    // ---------------------------------------------------------------------------
    // L1-1 | Product   (Level 1 - Beginner)
    // Write class Product (inside the markers below, replace the one-line stub).
    //   Product(String name, double price)   stores both in PRIVATE fields
    //   String getName()      double getPrice()
    //   double discountedPrice(int percent)  the price after the discount, rounded to 2 decimals
    //   static int getCreatedCount()         how many Product objects have been created so far
    //                                        (a static field shared by all products; add 1 in the constructor)
    //   new Product("Book", 120).discountedPrice(25)  ->  90.0
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class Product { Product(String name, double price) { } String getName() { return null; } double getPrice() { return 0; } double discountedPrice(int percent) { return 0; } static int getCreatedCount() { return 0; } }
    static class Product {
        private static int created = 0;
        private final String name;
        private final double price;
        Product(String name, double price) {
            this.name = name;
            this.price = price;
            created++;
        }
        String getName() {
            return name;
        }
        double getPrice() {
            return price;
        }
        double discountedPrice(int percent) {
            double result = price * (1 - percent / 100.0);
            return Math.round(result * 100) / 100.0;
        }
        static int getCreatedCount() {
            return created;
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L1-2 | Student   (Level 1 - Beginner)
    // Write class Student. A new student has no marks.
    //   Student(String name)      String getName()
    //   void addMark(int mark)    remember one more mark
    //   double average()          mean of the marks rounded to 2 decimals (0 when there are no marks)
    //   Integer highest()         the biggest mark, or null when there are no marks
    // Keep the marks in a private List<Integer> that is created INSIDE the object.
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class Student { Student(String name) { } String getName() { return null; } void addMark(int mark) { } double average() { return -1; } Integer highest() { return -1; } }
    static class Student {
        private final String name;
        private final List<Integer> marks = new ArrayList<>();
        Student(String name) {
            this.name = name;
        }
        String getName() {
            return name;
        }
        void addMark(int mark) {
            marks.add(mark);
        }
        double average() {
            if (marks.isEmpty()) {
                return 0;
            }
            int sum = 0;
            for (int mark : marks) {
                sum += mark;
            }
            return Math.round(sum * 100.0 / marks.size()) / 100.0;
        }
        Integer highest() {
            if (marks.isEmpty()) {
                return null;
            }
            return Collections.max(marks);
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L1-3 | Rectangle   (Level 1 - Beginner)
    // Write class Rectangle(int width, int height) with the methods
    //   int area()   int perimeter()   boolean isSquare()
    // and a toString() that returns text like  Rectangle(3x4)
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class Rectangle { Rectangle(int width, int height) { } int area() { return 0; } int perimeter() { return 0; } boolean isSquare() { return false; } }
    static class Rectangle {
        private final int width;
        private final int height;
        Rectangle(int width, int height) {
            this.width = width;
            this.height = height;
        }
        int area() {
            return width * height;
        }
        int perimeter() {
            return 2 * (width + height);
        }
        boolean isSquare() {
            return width == height;
        }
        @Override
        public String toString() {
            return "Rectangle(" + width + "x" + height + ")";
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L2-1 | BankAccount   (Level 2 - Intermediate)
    // Transaction (given) is a record: Transaction("deposit", 500).
    // Write class BankAccount with PRIVATE fields:
    //   BankAccount(String owner, double balance)   and a second constructor BankAccount(String owner)
    //                                               that starts at 0 (hint: this(owner, 0);)
    //   String getOwner()     double getBalance()
    //   List<Transaction> getHistory()   a COPY of the history (outsiders must not be able to change it)
    //   void deposit(double amount)   amount <= 0 -> throw new IllegalArgumentException("Deposit must be positive");
    //                                 otherwise add it and record new Transaction("deposit", amount)
    //   boolean withdraw(double amount)   if amount > balance return false (nothing changes);
    //                                 otherwise subtract, record new Transaction("withdraw", amount), return true
    //   toString()  ->  Aarav: Rs. 1,500.00   (String.format(Locale.US, "%s: Rs. %,.2f", ...))
    // ---------------------------------------------------------------------------
    record Transaction(String type, double amount) {
    }
    // >>> SOLUTION stub: static class BankAccount { BankAccount(String owner, double balance) { } BankAccount(String owner) { } String getOwner() { return null; } double getBalance() { return -1; } List<Transaction> getHistory() { return null; } void deposit(double amount) { } boolean withdraw(double amount) { return false; } }
    static class BankAccount {
        private final String owner;
        private double balance;
        private final List<Transaction> history = new ArrayList<>();
        BankAccount(String owner, double balance) {
            this.owner = owner;
            this.balance = balance;
        }
        BankAccount(String owner) {
            this(owner, 0);
        }
        String getOwner() {
            return owner;
        }
        double getBalance() {
            return balance;
        }
        List<Transaction> getHistory() {
            return new ArrayList<>(history);
        }
        void deposit(double amount) {
            if (amount <= 0) {
                throw new IllegalArgumentException("Deposit must be positive");
            }
            balance += amount;
            history.add(new Transaction("deposit", amount));
        }
        boolean withdraw(double amount) {
            if (amount > balance) {
                return false;
            }
            balance -= amount;
            history.add(new Transaction("withdraw", amount));
            return true;
        }
        @Override
        public String toString() {
            return String.format(Locale.US, "%s: Rs. %,.2f", owner, balance);
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L2-2 | ShoppingCart   (Level 2 - Intermediate)
    // Write class ShoppingCart (it starts empty):
    //   void add(String name, double price, int qty)   adding a name that is already there
    //                                                  increases its quantity (the price stays)
    //   void add(String name, double price)            one piece (call the other add)
    //   boolean remove(String name)                    true if the item existed, else false
    //   double total()        sum of price * qty, rounded to 2 decimals
    //   int itemCount()       total number of pieces (sum of the quantities)
    //   List<String> names()  the item names sorted A-Z
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class ShoppingCart { void add(String name, double price, int qty) { } void add(String name, double price) { } boolean remove(String name) { return false; } double total() { return -1; } int itemCount() { return -1; } List<String> names() { return null; } }
    static class ShoppingCart {
        private final Map<String, Double> prices = new TreeMap<>();
        private final Map<String, Integer> quantities = new TreeMap<>();
        void add(String name, double price, int qty) {
            if (quantities.containsKey(name)) {
                quantities.put(name, quantities.get(name) + qty);
            } else {
                prices.put(name, price);
                quantities.put(name, qty);
            }
        }
        void add(String name, double price) {
            add(name, price, 1);
        }
        boolean remove(String name) {
            if (!quantities.containsKey(name)) {
                return false;
            }
            prices.remove(name);
            quantities.remove(name);
            return true;
        }
        double total() {
            double sum = 0;
            for (String name : prices.keySet()) {
                sum += prices.get(name) * quantities.get(name);
            }
            return Math.round(sum * 100) / 100.0;
        }
        int itemCount() {
            int count = 0;
            for (int qty : quantities.values()) {
                count += qty;
            }
            return count;
        }
        List<String> names() {
            return new ArrayList<>(prices.keySet());
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L2-3 | Temperature (encapsulation)   (Level 2 - Intermediate)
    // Write class Temperature with ONE private field (celsius) and these methods:
    //   Temperature(double celsius)     must also validate (call setCelsius)
    //   double getCelsius()
    //   void setCelsius(double celsius) a value below -273.15 -> throw new IllegalArgumentException("Below absolute zero")
    //   double getFahrenheit()          celsius * 9 / 5 + 32  (calculated; there is NO setFahrenheit)
    // Java has no @property: getters and setters are how you protect a field.
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class Temperature { Temperature(double celsius) { } double getCelsius() { return 0; } void setCelsius(double celsius) { } double getFahrenheit() { return 0; } }
    static class Temperature {
        private double celsius;
        Temperature(double celsius) {
            setCelsius(celsius);
        }
        double getCelsius() {
            return celsius;
        }
        void setCelsius(double celsius) {
            if (celsius < -273.15) {
                throw new IllegalArgumentException("Below absolute zero");
            }
            this.celsius = celsius;
        }
        double getFahrenheit() {
            return celsius * 9 / 5 + 32;
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L2-4 | Item: equals, hashCode, toString   (Level 2 - Intermediate)
    // Two Items are the SAME product when their sku is the same (the name does not matter).
    // Write class Item(String sku, String name) with getSku(), getName() and
    //   equals(Object)   true when the other object is an Item with the same sku (false for null)
    //   hashCode()       must agree with equals (hint: sku.hashCode())
    //   toString()       Item[sku=P100, name=Pen]
    // Then a HashSet will keep only one Item per sku.
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class Item { Item(String sku, String name) { } String getSku() { return null; } String getName() { return null; } }
    static class Item {
        private final String sku;
        private final String name;
        Item(String sku, String name) {
            this.sku = sku;
            this.name = name;
        }
        String getSku() {
            return sku;
        }
        String getName() {
            return name;
        }
        @Override
        public boolean equals(Object other) {
            if (this == other) {
                return true;
            }
            return other instanceof Item that && sku.equals(that.sku);
        }
        @Override
        public int hashCode() {
            return sku.hashCode();
        }
        @Override
        public String toString() {
            return "Item[sku=" + sku + ", name=" + name + "]";
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L3-1 | Library   (Level 3 - Challenge)
    // Write class Library (it starts empty). Business rules live INSIDE the class.
    //   void addBook(String title, int copies)     adding an existing title adds more copies
    //   void checkout(String title, String member) needs a free copy, otherwise
    //                                              throw new IllegalStateException("Not available")
    //   void returnBook(String title, String member)  if that member does not hold the title:
    //                                              throw new IllegalStateException("Not borrowed by this member");
    //                                              otherwise the copy is free again
    //   List<String> available()                   titles with at least one free copy, sorted A-Z
    //   List<String> borrowedBy(String member)     titles that member holds now, sorted A-Z
    // Hint: a Map<String, Integer> of free copies and a List of loans (a tiny record Loan(title, member)).
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class Library { void addBook(String title, int copies) { } void checkout(String title, String member) { } void returnBook(String title, String member) { } List<String> available() { return null; } List<String> borrowedBy(String member) { return null; } }
    static class Library {
        private record Loan(String title, String member) {
        }
        private final Map<String, Integer> freeCopies = new TreeMap<>();
        private final List<Loan> loans = new ArrayList<>();
        void addBook(String title, int copies) {
            freeCopies.put(title, freeCopies.getOrDefault(title, 0) + copies);
        }
        void checkout(String title, String member) {
            if (freeCopies.getOrDefault(title, 0) < 1) {
                throw new IllegalStateException("Not available");
            }
            freeCopies.put(title, freeCopies.get(title) - 1);
            loans.add(new Loan(title, member));
        }
        void returnBook(String title, String member) {
            if (!loans.remove(new Loan(title, member))) {
                throw new IllegalStateException("Not borrowed by this member");
            }
            freeCopies.put(title, freeCopies.get(title) + 1);
        }
        List<String> available() {
            List<String> titles = new ArrayList<>();
            for (Map.Entry<String, Integer> entry : freeCopies.entrySet()) {
                if (entry.getValue() > 0) {
                    titles.add(entry.getKey());
                }
            }
            return titles;
        }
        List<String> borrowedBy(String member) {
            List<String> titles = new ArrayList<>();
            for (Loan loan : loans) {
                if (loan.member().equals(member)) {
                    titles.add(loan.title());
                }
            }
            Collections.sort(titles);
            return titles;
        }
    }
    // <<< SOLUTION
    // ---------------------------------------------------------------------------
    // L3-2 | CharStack and balanced brackets   (Level 3 - Challenge)
    // Write class CharStack (last in, first out) for characters:
    //   void push(char c)   char pop()   char peek() (look at the top, do not remove it)
    //   boolean isEmpty()   int size()
    //   pop() and peek() on an empty stack throw new IllegalStateException("pop from empty stack")
    //   (same message text for both is fine for peek: "peek from empty stack")
    // Then write static boolean isBalanced(String text): true when every ( [ { is closed
    // in the right order. Other characters are ignored. Use your CharStack.
    //   isBalanced("{[()]}") -> true     isBalanced("(]") -> false
    // ---------------------------------------------------------------------------
    // >>> SOLUTION stub: static class CharStack { void push(char c) { } char pop() { return '?'; } char peek() { return '?'; } boolean isEmpty() { return false; } int size() { return -1; } }
    static class CharStack {
        private final List<Character> items = new ArrayList<>();
        void push(char c) {
            items.add(c);
        }
        char pop() {
            if (items.isEmpty()) {
                throw new IllegalStateException("pop from empty stack");
            }
            return items.remove(items.size() - 1);
        }
        char peek() {
            if (items.isEmpty()) {
                throw new IllegalStateException("peek from empty stack");
            }
            return items.get(items.size() - 1);
        }
        boolean isEmpty() {
            return items.isEmpty();
        }
        int size() {
            return items.size();
        }
    }
    // <<< SOLUTION
    static boolean isBalanced(String text) {
        // >>> SOLUTION stub: return false;
        CharStack stack = new CharStack();
        for (char c : text.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') {
                stack.push(c);
            } else if (c == ')' || c == ']' || c == '}') {
                if (stack.isEmpty()) {
                    return false;
                }
                char open = stack.pop();
                boolean matches = (open == '(' && c == ')') || (open == '[' && c == ']') || (open == '{' && c == '}');
                if (!matches) {
                    return false;
                }
            }
        }
        return stack.isEmpty();
        // <<< SOLUTION
    }
    // ======================= AUTO-CHECKER (do not edit below) ====================
    static String errorOf(Runnable action) {
        try {
            action.run();
        } catch (Throwable e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
        return "no error";
    }
    /** True when every field of the class is private (encapsulation). */
    static boolean allFieldsPrivate(Class<?> type) {
        for (Field field : type.getDeclaredFields()) {
            if (!field.isSynthetic() && !Modifier.isPrivate(field.getModifiers())) {
                return false;
            }
        }
        return true;
    }
    static boolean hasMethod(Class<?> type, String name) {
        for (java.lang.reflect.Method method : type.getDeclaredMethods()) {
            if (method.getName().equals(name)) {
                return true;
            }
        }
        return false;
    }
    public static void main(String[] args) {
        System.out.println("--- Day 19 checks ---");
        Checker.check("L1-1 Product", () -> {
            Product book = new Product("Book", 120);
            return List.of(book.getName(), book.getPrice(), book.discountedPrice(25), new Product("Pen", 9.99).discountedPrice(10));
        }, List.of("Book", 120.0, 90.0, 8.99));
        Checker.check("L1-1 Product counts the objects created (static field)", () -> {
            int before = Product.getCreatedCount();
            new Product("A", 1);
            new Product("B", 2);
            new Product("C", 3);
            return Product.getCreatedCount() - before;
        }, 3);
        Checker.check("L1-1 Product fields are private", () -> allFieldsPrivate(Product.class), true);
        Checker.check("L1-2 Student without marks", () -> {
            Student empty = new Student("A");
            return Arrays.asList(empty.average(), empty.highest());
        }, Arrays.asList(0.0, null));
        Checker.check("L1-2 Student with marks", () -> {
            Student aarav = new Student("Aarav");
            for (int mark : new int[]{80, 95, 70}) {
                aarav.addMark(mark);
            }
            return List.of(aarav.average(), aarav.highest(), aarav.getName());
        }, List.of(81.67, 95, "Aarav"));
        Checker.check("L1-2 every Student has its own marks", () -> {
            Student a = new Student("A");
            Student b = new Student("B");
            a.addMark(100);
            return List.of(a.highest(), b.average());
        }, List.of(100, 0.0));
        Checker.check("L1-3 Rectangle", () -> List.of(new Rectangle(3, 4).area(), new Rectangle(3, 4).perimeter(),
                new Rectangle(2, 2).isSquare(), new Rectangle(2, 3).isSquare()), List.of(12, 14, true, false));
        Checker.check("L1-3 Rectangle toString", () -> new Rectangle(3, 4).toString() + " / " + new Rectangle(1, 1), "Rectangle(3x4) / Rectangle(1x1)");
        Checker.check("L2-1 BankAccount", () -> {
            BankAccount acc = new BankAccount("Aarav", 1000);
            acc.deposit(500);
            boolean tooMuch = acc.withdraw(2000);
            boolean fine = acc.withdraw(300);
            return List.of(acc.getBalance(), tooMuch, fine, acc.getHistory(), acc.toString(), new BankAccount("X").getBalance(), acc.getOwner());
        }, List.of(1200.0, false, true, List.of(new Transaction("deposit", 500), new Transaction("withdraw", 300)),
                "Aarav: Rs. 1,200.00", 0.0, "Aarav"));
        Checker.check("L2-1 deposit error", () -> errorOf(() -> new BankAccount("A").deposit(-5)), "IllegalArgumentException: Deposit must be positive");
        Checker.check("L2-1 each account has its own history", () -> {
            BankAccount a = new BankAccount("A");
            BankAccount b = new BankAccount("B");
            a.deposit(10);
            return List.of(a.getHistory().size(), b.getHistory().size());
        }, List.of(1, 0));
        Checker.check("L2-1 outsiders cannot change the history / fields are private", () -> {
            BankAccount acc = new BankAccount("A", 50);
            try {
                acc.getHistory().add(new Transaction("deposit", 1));
            } catch (RuntimeException ignored) {
                // an unmodifiable list is fine too
            }
            return List.of(acc.getHistory().size(), allFieldsPrivate(BankAccount.class));
        }, List.of(0, true));
        Checker.check("L2-2 ShoppingCart", () -> {
            ShoppingCart cart = new ShoppingCart();
            cart.add("Pen", 10, 3);
            cart.add("Book", 120.5);
            cart.add("Pen", 10);
            return List.of(cart.total(), cart.itemCount(), cart.names(), cart.remove("Pen"), cart.remove("Pen"), cart.total());
        }, List.of(160.5, 5, List.of("Book", "Pen"), true, false, 120.5));
        Checker.check("L2-2 carts are separate", () -> {
            ShoppingCart a = new ShoppingCart();
            a.add("Pen", 10);
            return new ShoppingCart().itemCount();
        }, 0);
        Checker.check("L2-3 Temperature", () -> List.of(new Temperature(100).getFahrenheit(), new Temperature(0).getFahrenheit(),
                new Temperature(-40).getFahrenheit(), new Temperature(36.6).getCelsius()), List.of(212.0, 32.0, -40.0, 36.6));
        Checker.check("L2-3 Temperature validates (constructor and setter)", () -> List.of(
                errorOf(() -> new Temperature(-300)),
                errorOf(() -> new Temperature(5).setCelsius(-274)),
                errorOf(() -> new Temperature(-273.15))),
                List.of("IllegalArgumentException: Below absolute zero", "IllegalArgumentException: Below absolute zero", "no error"));
        Checker.check("L2-3 Temperature setter works, field private, fahrenheit read-only", () -> {
            Temperature t = new Temperature(10);
            t.setCelsius(20);
            return List.of(t.getCelsius(), allFieldsPrivate(Temperature.class), hasMethod(Temperature.class, "setFahrenheit"));
        }, List.of(20.0, true, false));
        Checker.check("L2-4 Item equals / hashCode", () -> {
            Item pen = new Item("P100", "Pen");
            Item samePen = new Item("P100", "Blue Pen");
            Item book = new Item("B200", "Book");
            Object notAnItem = "P100";
            return List.of(pen.equals(samePen), pen.equals(book), pen.equals(null), pen.equals(notAnItem),
                    pen.hashCode() == samePen.hashCode());
        }, List.of(true, false, false, false, true));
        Checker.check("L2-4 Item in a HashSet", () -> {
            Set<Item> shelf = new HashSet<>();
            shelf.add(new Item("P100", "Pen"));
            shelf.add(new Item("P100", "Blue Pen"));
            shelf.add(new Item("B200", "Book"));
            return List.of(shelf.size(), shelf.contains(new Item("B200", "anything")));
        }, List.of(2, true));
        Checker.check("L2-4 Item toString", () -> new Item("P100", "Pen").toString(), "Item[sku=P100, name=Pen]");
        Checker.check("L3-1 Library", () -> {
            Library lib = new Library();
            lib.addBook("Dune", 2);
            lib.addBook("Emma", 1);
            lib.checkout("Dune", "aarav");
            lib.checkout("Dune", "diya");
            lib.checkout("Emma", "aarav");
            List<Object> out = new ArrayList<>();
            out.add(lib.available());
            out.add(lib.borrowedBy("aarav"));
            out.add(errorOf(() -> lib.checkout("Dune", "kabir")));
            out.add(errorOf(() -> lib.returnBook("Emma", "diya")));
            lib.returnBook("Dune", "diya");
            out.add(lib.available());
            out.add(errorOf(() -> lib.checkout("Unknown", "kabir")));
            return out;
        }, List.of(List.of(), List.of("Dune", "Emma"), "IllegalStateException: Not available",
                "IllegalStateException: Not borrowed by this member", List.of("Dune"), "IllegalStateException: Not available"));
        Checker.check("L3-1 Library adds copies to an existing title", () -> {
            Library lib = new Library();
            lib.addBook("Dune", 1);
            lib.addBook("Dune", 1);
            lib.checkout("Dune", "a");
            lib.checkout("Dune", "b");
            return List.of(lib.available(), lib.borrowedBy("b"), lib.borrowedBy("zzz"));
        }, List.of(List.of(), List.of("Dune"), List.of()));
        Checker.check("L3-2 CharStack", () -> {
            CharStack s = new CharStack();
            boolean first = s.isEmpty();
            s.push('a');
            s.push('b');
            return List.of(first, s.size(), s.peek(), s.pop(), s.pop(), s.isEmpty(),
                    errorOf(() -> s.pop()));
        }, List.of(true, 2, 'b', 'b', 'a', true, "IllegalStateException: pop from empty stack"));
        Checker.check("L3-2 isBalanced", () -> {
            List<Boolean> results = new ArrayList<>();
            for (String text : new String[]{"{[()]}", "(]", "((", "", "a(b)c", ")(", "([)]", "{[]}()"}) {
                results.add(isBalanced(text));
            }
            return results;
        }, List.of(true, false, false, true, true, false, false, true));
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
