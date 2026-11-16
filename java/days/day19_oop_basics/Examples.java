/* Day 19 - Code along: classes and objects (a tiny shop).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.*;
class Examples {
    // ---- 1. A class is a blueprint: data (fields) + behaviour (methods) ----
    static class Product {
        private final String name;       // private: only this class may touch it
        private final double price;
        Product(String name, double price) {     // the constructor: runs on "new"
            this.name = name;                    // this.name = the field, name = the parameter
            this.price = price;
        }
        String getName() {
            return name;
        }
        double getPrice() {
            return price;
        }
        double discountedPrice(int percent) {
            return price * (1 - percent / 100.0);
        }
        @Override
        public String toString() {               // how the object prints
            return name + " (Rs. " + price + ")";
        }
    }
    // ---- 2. Every object keeps its own state ----
    static class Counter {
        private int count = 0;
        void hit() {
            count++;
        }
        int getCount() {
            return count;
        }
    }
    // ---- 3. static = shared by the whole class, not by one object ----
    static class Account {
        static final String BANK_NAME = "Chai Bank";   // one copy for everybody
        private static int accountsOpened = 0;
        private final String owner;
        private double balance;
        Account(String owner, double balance) {
            this.owner = owner;
            this.balance = balance;
            accountsOpened++;
        }
        // Encapsulation: the rule "no overdraft" lives INSIDE the class
        boolean withdraw(double amount) {
            if (amount <= 0 || amount > balance) {
                return false;
            }
            balance -= amount;
            return true;
        }
        double getBalance() {
            return balance;
        }
        static int getAccountsOpened() {
            return accountsOpened;
        }
        @Override
        public String toString() {
            return owner + ": Rs. " + balance;
        }
    }
    // ---- 4. equals and hashCode: when are two objects "the same"? ----
    static class Sku {
        private final String code;
        Sku(String code) {
            this.code = code;
        }
        @Override
        public boolean equals(Object other) {
            return other instanceof Sku that && code.equals(that.code);
        }
        @Override
        public int hashCode() {
            return code.hashCode();
        }
    }
    // ---- 5. A setter that protects the field ----
    static class Temperature {
        private double celsius;
        Temperature(double celsius) {
            setCelsius(celsius);               // reuse the validation
        }
        void setCelsius(double celsius) {
            if (celsius < -273.15) {
                throw new IllegalArgumentException("Below absolute zero");
            }
            this.celsius = celsius;
        }
        double getFahrenheit() {
            return celsius * 9 / 5 + 32;       // calculated, so no setter
        }
    }
    public static void main(String[] args) {
        // ---- 1. Make objects with new ----
        System.out.println("1. Objects");
        Product pen = new Product("Pen", 10);
        Product book = new Product("Book", 120);
        System.out.println("  " + pen.getName() + " costs " + pen.getPrice());
        System.out.println("  Book with 25% off: " + book.discountedPrice(25));
        System.out.println("  printing the object: " + book);          // calls toString()
        // ---- 2. Own state ----
        System.out.println("2. Each object has its own data");
        Counter a = new Counter();
        Counter b = new Counter();
        a.hit();
        a.hit();
        b.hit();
        System.out.println("  a=" + a.getCount() + " b=" + b.getCount());
        // ---- 3. static ----
        System.out.println("3. static and encapsulation");
        Account aarav = new Account("Aarav", 1000);
        Account diya = new Account("Diya", 50);
        System.out.println("  " + Account.BANK_NAME + " has " + Account.getAccountsOpened() + " accounts");
        System.out.println("  Aarav withdraws 300: " + aarav.withdraw(300) + " -> " + aarav);
        System.out.println("  Diya withdraws 300: " + diya.withdraw(300) + " -> " + diya);
        // ---- 4. == versus equals ----
        System.out.println("4. == vs equals");
        Sku first = new Sku("P100");
        Sku second = new Sku("P100");
        System.out.println("  first == second      : " + (first == second));        // two different objects
        System.out.println("  first.equals(second) : " + first.equals(second));     // same code
        Set<Sku> shelf = new HashSet<>();
        shelf.add(first);
        shelf.add(second);
        System.out.println("  HashSet size         : " + shelf.size());
        // ---- 5. Validation ----
        System.out.println("5. Validation");
        Temperature boiling = new Temperature(100);
        System.out.println("  100 C = " + boiling.getFahrenheit() + " F");
        try {
            new Temperature(-300);
        } catch (IllegalArgumentException e) {
            System.out.println("  rejected: " + e.getMessage());
        }
    }
}
