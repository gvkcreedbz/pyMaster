/* Day 12 - Code along: product filters and a music chart.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.*;
import java.util.function.*;
import java.util.stream.*;

class Examples {
    // Tiny data classes (records are explained properly tomorrow).
    record Product(String name, int price, double rating) {}
    record Song(String title, int plays) {}

    public static void main(String[] args) {
        // ---- 1. Lambdas: tiny nameless methods ----
        Function<Integer, Integer> doubler = x -> x * 2;
        Predicate<Integer> isEven = n -> n % 2 == 0;
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        Supplier<String> greeting = () -> "Welcome to Chai Point";
        Consumer<String> shout = s -> System.out.println(s.toUpperCase() + "!");
        System.out.println(doubler.apply(21));          // 42
        System.out.println(isEven.test(7));             // false
        System.out.println(add.apply(60, 15));          // 75
        System.out.println(greeting.get());
        shout.accept("one masala chai");                // ONE MASALA CHAI!
        System.out.println(doubler.andThen(doubler).apply(5));   // 20 (double, then double again)

        // ---- 2. Method references: a lambda that only calls one method ----
        Function<String, String> upper = String::toUpperCase;   // same as s -> s.toUpperCase()
        System.out.println(upper.apply("samosa"));

        // ---- 3. Streams: source -> middle steps -> final step ----
        List<Integer> nums = List.of(1, 2, 3, 4, 5, 6);
        List<Integer> squares = nums.stream().map(n -> n * n).toList();
        List<Integer> evens = nums.stream().filter(n -> n % 2 == 0).toList();
        System.out.println(squares);   // [1, 4, 9, 16, 25, 36]
        System.out.println(evens);     // [2, 4, 6]
        System.out.println(nums.stream().mapToInt(Integer::intValue).sum());                      // 21
        System.out.println(nums.stream().mapToInt(Integer::intValue).average().orElse(0));        // 3.5
        System.out.println(IntStream.rangeClosed(1, 5).sum());                                    // 15 (like Python range)
        System.out.println(nums.stream().anyMatch(n -> n > 5) + " " + nums.stream().allMatch(n -> n > 1));   // true false

        // ---- 4. A product filter: "under Rs.1000, best rated first" ----
        List<Product> shop = List.of(
                new Product("Pen", 10, 4.1),
                new Product("Backpack", 899, 4.6),
                new Product("Book", 120, 4.8),
                new Product("Headphones", 2499, 4.4),
                new Product("Lamp", 650, 4.2));
        List<String> deals = shop.stream()
                .filter(p -> p.price() < 1000)
                .sorted(Comparator.comparingDouble(Product::rating).reversed())
                .map(Product::name)
                .toList();
        System.out.println("Deals: " + deals);   // [Book, Backpack, Lamp, Pen]
        int basket = shop.stream().mapToInt(Product::price).sum();
        System.out.println("Basket total: Rs." + basket);   // 4178
        Optional<Product> priciest = shop.stream().max(Comparator.comparingInt(Product::price));
        System.out.println("Priciest: " + priciest.get().name());   // Headphones
        System.out.println(shop.stream().map(Product::name).collect(Collectors.joining(", ", "[", "]")));

        // ---- 5. Sorting with a Comparator (two keys) ----
        List<Song> songs = List.of(new Song("Kesariya", 90), new Song("Apna Bana Le", 90),
                new Song("Naatu Naatu", 120), new Song("Chaleya", 75));
        List<String> top3 = songs.stream()
                .sorted(Comparator.comparingInt(Song::plays).reversed().thenComparing(Song::title))
                .limit(3)
                .map(Song::title)
                .toList();
        System.out.println("Top 3: " + top3);   // [Naatu Naatu, Apna Bana Le, Kesariya]

        // ---- 6. Lambdas can use (but not change) variables around them ----
        int gst = 18;
        List<Integer> withTax = List.of(100, 200).stream().map(p -> p + p * gst / 100).toList();
        System.out.println(withTax);   // [118, 236]
        // gst = 5;   // <- uncomment: "local variables referenced from a lambda must be final"

        // ---- 7. A stream is used once; the original list is never changed ----
        List<String> words = List.of("kiwi", "fig", "pear");
        System.out.println(words.stream().sorted().toList() + " vs original " + words);
    }
}
