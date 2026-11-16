/* Day 22 - Code along: log streaming, retrying calls, auto-closing resources.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.*;
import java.util.function.*;
import java.util.stream.*;

class Examples {

    // ---- A tiny Iterable: the numbers from..to (what a Python generator does with yield) ----
    static class Range implements Iterable<Integer> {
        private final int from;
        private final int to;

        Range(int from, int to) {
            this.from = from;
            this.to = to;
        }

        @Override
        public Iterator<Integer> iterator() {
            return new Iterator<>() {
                private int next = from;

                @Override
                public boolean hasNext() {
                    return next <= to;
                }

                @Override
                public Integer next() {
                    return next++;
                }
            };
        }
    }

    // ---- A generic class: a Box that can hold ANY type ----
    static class Box<T> {
        private final T value;

        Box(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }

        <R> Box<R> map(Function<T, R> f) {
            return new Box<>(f.apply(value));
        }
    }

    // ---- A generic method: the first item, or a fallback ----
    static <T> T firstOr(List<T> items, T fallback) {
        return items.isEmpty() ? fallback : items.get(0);
    }

    // ---- A "decorator": takes a function, returns a function with extra behaviour ----
    static <T, R> Function<T, R> logged(String name, Function<T, R> f) {
        return input -> {
            System.out.println("  [log] calling " + name + "(" + input + ")");
            R result = f.apply(input);
            System.out.println("  [log] " + name + " returned " + result);
            return result;
        };
    }

    // ---- A resource that must always be closed ----
    static class Connection implements AutoCloseable {
        private final String name;

        Connection(String name) {
            this.name = name;
            System.out.println("  opening " + name);
        }

        void query(String sql) {
            System.out.println("  " + name + " runs: " + sql);
            if (sql.contains("DROP")) {
                throw new IllegalStateException("not allowed: " + sql);
            }
        }

        @Override
        public void close() {
            System.out.println("  closing " + name);
        }
    }

    public static void main(String[] args) {
        // ---- 1. What a for-each really does ----
        System.out.println("1. Iterator by hand");
        List<String> shelf = List.of("Chai", "Samosa", "Biscuit");
        Iterator<String> it = shelf.iterator();
        while (it.hasNext()) {
            System.out.println("  next item: " + it.next());
        }

        // ---- 2. Our own Iterable works in a for-each ----
        System.out.println("2. A custom Iterable");
        int total = 0;
        for (int n : new Range(1, 5)) {
            total += n;
        }
        System.out.println("  1+2+3+4+5 = " + total);

        // ---- 3. Lazy sequences with streams (nothing runs until the end) ----
        System.out.println("3. Lazy streams");
        List<Integer> powersOfTwo = Stream.iterate(1, n -> n * 2).limit(8).collect(Collectors.toList());
        System.out.println("  " + powersOfTwo);
        long bigSquares = Stream.iterate(1, n -> n + 1).map(n -> n * n).filter(n -> n > 50).limit(3).count();
        System.out.println("  squares above 50 found: " + bigSquares);

        // ---- 4. Generics ----
        System.out.println("4. Generics");
        Box<String> nameBox = new Box<>("Masala Chai");
        Box<Integer> lengthBox = nameBox.map(String::length);
        System.out.println("  " + nameBox.get() + " has " + lengthBox.get() + " letters");
        System.out.println("  " + firstOr(List.of(), "empty shelf") + " / " + firstOr(List.of(7, 8), 0));

        // ---- 5. Optional instead of null ----
        System.out.println("5. Optional");
        Map<String, Integer> prices = Map.of("Chai", 20, "Samosa", 15);
        Optional<Integer> chai = Optional.ofNullable(prices.get("Chai"));
        Optional<Integer> pizza = Optional.ofNullable(prices.get("Pizza"));
        System.out.println("  chai: " + chai.map(p -> "Rs " + p).orElse("not sold"));
        System.out.println("  pizza: " + pizza.map(p -> "Rs " + p).orElse("not sold"));
        pizza.ifPresentOrElse(p -> System.out.println("  found"), () -> System.out.println("  pizza is missing"));

        // ---- 6. Function, Predicate, Supplier, Consumer ----
        System.out.println("6. Functional interfaces");
        Function<Integer, Integer> addGst = price -> price * 118 / 100;
        Function<Integer, String> label = price -> "Rs " + price;
        System.out.println("  " + addGst.andThen(label).apply(100));
        Predicate<String> isLong = s -> s.length() > 5;
        Predicate<String> startsWithC = s -> s.startsWith("C");
        System.out.println("  long and C: " + shelf.stream().filter(isLong.and(startsWithC)).toList());
        System.out.println("  not long: " + shelf.stream().filter(isLong.negate()).toList());
        Supplier<String> greeting = () -> "Welcome to Chai Point";
        Consumer<String> shout = s -> System.out.println("  " + s.toUpperCase());
        shout.accept(greeting.get());

        // ---- 7. A decorator: wrap a function with logging ----
        System.out.println("7. Decorator");
        Function<Integer, Integer> square = n -> n * n;
        Function<Integer, Integer> loggedSquare = logged("square", square);
        loggedSquare.apply(6);

        // ---- 8. try-with-resources: close() always runs ----
        System.out.println("8. try-with-resources");
        try (Connection db = new Connection("shop-db")) {
            db.query("SELECT * FROM orders");
            db.query("DROP TABLE orders");
        } catch (IllegalStateException e) {
            System.out.println("  caught: " + e.getMessage());
        }
    }
}
