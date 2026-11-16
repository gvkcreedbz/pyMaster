/* Day 22 - Practice: generics, Optional, iterators and functional interfaces.
 *
 * Run:  java Practice.java
 * Fill in every TODO. The auto-checker at the bottom tells you what passes.
 */
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.*;

class Practice {

    // ---------------------------------------------------------------------------
    // L1-1 | countdown   (Level 1 - Beginner)
    // Return an Iterable<Integer> that hands out n, n-1, ..., 1 (nothing when n <= 0).
    // Every call to iterator() must start again from n (so a for-each can run twice).
    //   countdown(3)  ->  3, 2, 1
    // Hint: an Iterable has ONE method, iterator(), so a lambda  () -> new Iterator<>() {...}  works.
    // ---------------------------------------------------------------------------
    static Iterable<Integer> countdown(int n) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-2 | fibonacci   (Level 1 - Beginner)
    // Return an INFINITE Iterator<Long> of Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8, ...
    // hasNext() is always true. Keep the two latest numbers in fields.
    // ---------------------------------------------------------------------------
    static Iterator<Long> fibonacci() {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L1-3 | findFirst (generic + Optional)   (Level 1 - Beginner)
    // Return the first item for which test.test(item) is true, wrapped in an Optional.
    // If nothing matches return Optional.empty(). It must work for ANY item type T.
    //   findFirst(List.of("Chai", "Coffee", "Cola"), s -> s.startsWith("Co"))  ->  Optional[Coffee]
    // ---------------------------------------------------------------------------
    static <T> Optional<T> findFirst(List<T> items, Predicate<T> test) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-1 | Box<T>.map   (Level 2 - Intermediate)
    // Box is a tiny generic container. Write map(): apply the function to the value and
    // return a NEW Box holding the result (the result type R can differ from T).
    //   new Box<>("chai").map(String::length).get()  ->  4
    // ---------------------------------------------------------------------------
    static class Box<T> {
        private final T value;

        Box(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }

        // TODO: write your code here
        <R> Box<R> map(Function<T, R> mapper) { return null; }
    }

    // ---------------------------------------------------------------------------
    // L2-2 | countCalls (a decorator)   (Level 2 - Intermediate)
    // Return a function that behaves exactly like f but adds 1 to `counter` every time it
    // is called. (A lambda cannot change a normal local int, so we use an AtomicInteger.)
    // ---------------------------------------------------------------------------
    static <T, R> Function<T, R> countCalls(Function<T, R> f, AtomicInteger counter) {
        // TODO: write your code here
        return f;
    }

    // ---------------------------------------------------------------------------
    // L2-3 | retry   (Level 2 - Intermediate)
    // Run action.get() up to `times` times. Return the first successful result.
    // If every attempt throws a RuntimeException, throw the LAST one.
    // ---------------------------------------------------------------------------
    static <T> T retry(int times, Supplier<T> action) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L2-4 | runJob (try-with-resources)   (Level 2 - Intermediate)
    // Connection (below) writes "open" to a log when created and "close" when closed.
    // In runJob create ONE Connection in a try-with-resources, call send("hello"), then:
    //   * if fail is true: throw new IllegalStateException("boom") inside the try, and
    //     catch it (after the try block) by adding "caught:boom" to the log;
    //   * otherwise add "done" to the log inside the try.
    // Return the log. Notice WHEN "close" shows up:
    //   runJob(false) -> [open, send:hello, done, close]
    //   runJob(true)  -> [open, send:hello, close, caught:boom]
    // ---------------------------------------------------------------------------
    static class Connection implements AutoCloseable {
        private final List<String> log;

        Connection(List<String> log) {
            this.log = log;
            log.add("open");
        }

        void send(String message) {
            log.add("send:" + message);
        }

        @Override
        public void close() {
            log.add("close");
        }
    }

    static List<String> runJob(boolean fail) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-1 | chunked (a lazy batcher)   (Level 3 - Challenge)
    // Wrap an Iterator<T> so that it hands out lists of `size` items (the last list may be
    // shorter). It must be LAZY: next() may only pull as many items as it needs, so it also
    // works on an endless source. Used to send 500 database rows at a time.
    //   chunked(List.of(0,1,2,3,4,5,6).iterator(), 3)  ->  [0,1,2], [3,4,5], [6]
    // ---------------------------------------------------------------------------
    static <T> Iterator<List<T>> chunked(Iterator<T> source, int size) {
        // TODO: write your code here
        return null;
    }

    // ---------------------------------------------------------------------------
    // L3-2 | memoize   (Level 3 - Challenge)
    // Return a function that remembers answers: calling it again with the same input returns
    // the stored value WITHOUT calling f again. Use a HashMap as the memory.
    // ---------------------------------------------------------------------------
    static <K, V> Function<K, V> memoize(Function<K, V> f) {
        // TODO: write your code here
        return f;
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    static <T> List<T> toList(Iterable<T> items) {
        List<T> out = new ArrayList<>();
        for (T item : items) {
            out.add(item);
        }
        return out;
    }

    static <T> List<T> take(Iterator<T> it, int n) {
        List<T> out = new ArrayList<>();
        while (out.size() < n && it.hasNext()) {
            out.add(it.next());
        }
        return out;
    }

    static String errorOf(Runnable action) {
        try {
            action.run();
        } catch (Throwable e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
        return "no error";
    }

    public static void main(String[] args) {
        System.out.println("--- Day 22 checks ---");
        Checker.check("L1-1 countdown", () -> {
            Iterable<Integer> three = countdown(3);
            return List.of(toList(three), toList(three), toList(countdown(0)));
        }, List.of(List.of(3, 2, 1), List.of(3, 2, 1), List.of()));
        Checker.check("L1-2 fibonacci", () -> take(fibonacci(), 10),
                List.of(0L, 1L, 1L, 2L, 3L, 5L, 8L, 13L, 21L, 34L));
        Checker.check("L1-2 fibonacci never ends", () -> take(fibonacci(), 50).get(49), 7778742049L);
        List<String> drinks = List.of("Chai", "Coffee", "Cola");
        Checker.check("L1-3 findFirst", () -> List.of(
                findFirst(drinks, s -> s.startsWith("Co")),
                findFirst(drinks, s -> s.startsWith("Z")),
                findFirst(List.of(5, 12, 30), n -> n > 10)),
                List.of(Optional.of("Coffee"), Optional.empty(), Optional.of(12)));
        Checker.check("L2-1 Box.map", () -> List.of(
                new Box<>("chai").map(String::length).map(n -> n * 10).get(),
                new Box<>(3).map(n -> "ab".repeat(n)).get()),
                List.of(40, "ababab"));
        Checker.check("L2-2 countCalls", () -> {
            AtomicInteger calls = new AtomicInteger();
            Function<Integer, Integer> square = countCalls(n -> n * n, calls);
            int before = calls.get();
            int a = square.apply(3);
            int b = square.apply(4);
            return List.of(before, a, b, calls.get());
        }, List.of(0, 9, 16, 2));
        Checker.check("L2-3 retry succeeds on the 3rd try", () -> {
            int[] attempts = {0};
            String result = retry(3, () -> {
                attempts[0]++;
                if (attempts[0] < 3) {
                    throw new IllegalStateException("server down");
                }
                return "ok";
            });
            return List.of(result, attempts[0]);
        }, List.of("ok", 3));
        Checker.check("L2-3 retry gives up (last error)", () -> {
            int[] attempts = {0};
            String error = errorOf(() -> retry(2, () -> {
                attempts[0]++;
                return Integer.parseInt("abc" + attempts[0]);
            }));
            return List.of(error, attempts[0]);
        }, List.of("NumberFormatException: For input string: \"abc2\"", 2));
        Checker.check("L2-4 runJob", () -> List.of(runJob(false), runJob(true)),
                List.of(List.of("open", "send:hello", "done", "close"),
                        List.of("open", "send:hello", "close", "caught:boom")));
        Checker.check("L3-1 chunked", () -> List.of(
                toList(() -> chunked(List.of(0, 1, 2, 3, 4, 5, 6).iterator(), 3)),
                toList(() -> chunked(List.of("a", "b", "c", "d").iterator(), 2)),
                toList(() -> chunked(List.<Integer>of().iterator(), 3)),
                toList(() -> chunked(List.of(1, 2, 3).iterator(), 5))),
                List.of(List.of(List.of(0, 1, 2), List.of(3, 4, 5), List.of(6)),
                        List.of(List.of("a", "b"), List.of("c", "d")),
                        List.of(),
                        List.of(List.of(1, 2, 3))));
        Checker.check("L3-1 chunked is lazy (works on an endless source)", () -> {
            AtomicInteger pulled = new AtomicInteger();
            Iterator<Integer> naturals = new Iterator<>() {
                public boolean hasNext() {
                    return true;
                }

                public Integer next() {
                    return pulled.incrementAndGet();
                }
            };
            List<Integer> firstChunk = chunked(naturals, 3).next();
            return List.of(firstChunk, pulled.get());
        }, List.of(List.of(1, 2, 3), 3));
        Checker.check("L3-2 memoize", () -> {
            List<Integer> calls = new ArrayList<>();
            Function<Integer, Integer> slowSquare = memoize(x -> {
                calls.add(x);
                return x * x;
            });
            return List.of(slowSquare.apply(4), slowSquare.apply(4), slowSquare.apply(5), calls);
        }, List.of(16, 16, 25, List.of(4, 5)));
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
