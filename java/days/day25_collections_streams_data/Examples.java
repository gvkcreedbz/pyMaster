/* Day 25 - Code along: "Which region earns most? Which products carry the business?"
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * Data: ../../datasets/sales.csv (300 orders).
 */
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

class Examples {
    // One order = one record (Day 13). revenue() is the formula we used on Day 16.
    record Sale(String orderId, String orderDate, String region, String category, String product,
                int quantity, int unitPrice, int discountPct, String paymentMethod) {
        double revenue() {
            return quantity * unitPrice * (1 - discountPct / 100.0);
        }
    }

    static List<Sale> load(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        return lines.subList(1, lines.size()).stream()
                .filter(line -> !line.isBlank())
                .map(line -> line.split(",", -1))
                .map(c -> new Sale(c[0], c[1], c[2], c[3], c[4], Integer.parseInt(c[5]),
                        Integer.parseInt(c[6]), Integer.parseInt(c[7]), c[8]))
                .toList();
    }

    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    public static void main(String[] args) throws IOException {
        // ---- 1. The collection toolbox ----
        List<String> cart = new ArrayList<>(List.of("Pen", "Notebook", "Pen", "Lamp"));
        System.out.println(Collections.frequency(cart, "Pen"));     // 2
        cart.removeIf(item -> item.equals("Lamp"));                 // remove by a rule
        System.out.println(cart);                                   // [Pen, Notebook, Pen]
        Set<String> unique = new TreeSet<>(cart);                   // no duplicates, A-Z
        System.out.println(unique);                                 // [Notebook, Pen]

        Deque<String> counter = new ArrayDeque<>();                 // a queue at the billing counter
        counter.addLast("Asha");
        counter.addLast("Ben");
        counter.addLast("Chitra");
        System.out.println("Next customer: " + counter.pollFirst()); // Asha (first in, first out)
        System.out.println("Waiting: " + counter);                   // [Ben, Chitra]

        Map<String, List<String>> shopsByCity = new TreeMap<>();
        shopsByCity.computeIfAbsent("Pune", k -> new ArrayList<>()).add("Chai Point");
        shopsByCity.computeIfAbsent("Pune", k -> new ArrayList<>()).add("Book Nook");
        shopsByCity.computeIfAbsent("Goa", k -> new ArrayList<>()).add("Beach Cafe");
        System.out.println(shopsByCity);   // {Goa=[Beach Cafe], Pune=[Chai Point, Book Nook]}

        List<Integer> frozen = List.copyOf(List.of(3, 1, 2));       // an unchangeable copy
        try {
            frozen.add(4);
        } catch (UnsupportedOperationException e) {
            System.out.println("List.of / copyOf lists cannot be changed");
        }

        // ---- 2. Load the real file ----
        List<Sale> sales = load(Path.of("../../datasets/sales.csv"));
        System.out.println("Orders: " + sales.size());                      // 300
        System.out.println("First: " + sales.get(0));

        // ---- 3. groupingBy + counting: "how many per region?" ----
        Map<String, Long> perRegion = sales.stream()
                .collect(Collectors.groupingBy(Sale::region, TreeMap::new, Collectors.counting()));
        System.out.println(perRegion);   // {East=84, North=70, South=71, West=75}

        // ---- 4. Other "downstream" collectors ----
        Map<String, Double> revenueByRegion = sales.stream()
                .collect(Collectors.groupingBy(Sale::region, TreeMap::new, Collectors.summingDouble(Sale::revenue)));
        revenueByRegion.replaceAll((region, total) -> round2(total));
        System.out.println(revenueByRegion);   // {East=335268.6, North=300446.25, South=348849.7, West=458677.0}

        Map<String, Double> avgQty = sales.stream()
                .collect(Collectors.groupingBy(Sale::category, TreeMap::new, Collectors.averagingDouble(Sale::quantity)));
        avgQty.forEach((category, avg) -> System.out.printf("%-12s average quantity %.2f%n", category, avg));

        Map<String, Set<String>> productsByCategory = sales.stream()
                .collect(Collectors.groupingBy(Sale::category, TreeMap::new,
                        Collectors.mapping(Sale::product, Collectors.toCollection(TreeSet::new))));
        System.out.println(productsByCategory.get("Grocery"));   // [Almonds 500g, Basmati Rice 5kg, Green Tea, Olive Oil 1L]

        Map<String, String> payments = sales.stream()
                .collect(Collectors.groupingBy(Sale::region, TreeMap::new,
                        Collectors.mapping(Sale::paymentMethod, Collectors.collectingAndThen(
                                Collectors.toCollection(TreeSet::new), set -> String.join("/", set)))));
        System.out.println(payments.get("East"));                // COD/Card/NetBanking/UPI (capital letters sort before small ones)

        // ---- 5. Top 3 products: group, then sort the entries ----
        Map<String, Double> byProduct = sales.stream()
                .collect(Collectors.groupingBy(Sale::product, Collectors.summingDouble(Sale::revenue)));
        System.out.println("Top 3 products:");
        byProduct.entrySet().stream()
                .sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
                .limit(3)
                .forEach(e -> System.out.printf("  %-14s Rs.%.2f%n", e.getKey(), e.getValue()));

        // ---- 6. partitioningBy: exactly two groups (true / false) ----
        Map<Boolean, Long> bigOrFinal = sales.stream()
                .collect(Collectors.partitioningBy(s -> s.revenue() >= 10000, Collectors.counting()));
        System.out.println("Orders worth Rs.10000 or more: " + bigOrFinal.get(true) + ", smaller: " + bigOrFinal.get(false));

        // ---- 7. toMap: one value per key ----
        Map<String, Integer> priceOf = sales.stream()
                .collect(Collectors.toMap(Sale::product, Sale::unitPrice, (first, second) -> first, TreeMap::new));
        System.out.println(priceOf.get("Smartwatch"));   // 3499

        // ---- 8. The total of everything ----
        double total = sales.stream().mapToDouble(Sale::revenue).sum();
        System.out.println("Total revenue: Rs." + round2(total));   // 1443241.55
    }
}
