/* Day 13 - Code along: a restaurant-listing API (Zomato / Swiggy style).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
import java.util.*;
import java.util.stream.*;

class Examples {
    // A record = a tiny data class. Java gives you name(), city() ..., equals and a readable toString.
    record Restaurant(String name, String city, double rating, List<String> cuisines, int avgCost) {}

    public static void main(String[] args) {
        List<Restaurant> restaurants = List.of(
                new Restaurant("Spice Hub", "Delhi", 4.5, List.of("North Indian", "Chinese"), 600),
                new Restaurant("Dosa Corner", "Pune", 4.2, List.of("South Indian"), 250),
                new Restaurant("Pasta Palace", "Delhi", 4.0, List.of("Italian"), 800),
                new Restaurant("Biryani Bay", "Pune", 4.7, List.of("Mughlai", "North Indian"), 500),
                new Restaurant("Wok Express", "Mumbai", 3.9, List.of("Chinese"), 450));

        // ---- 1. Records and nested data: read it like a path ----
        Restaurant first = restaurants.get(0);
        System.out.println(first);                          // Restaurant[name=Spice Hub, city=Delhi, ...]
        System.out.println(first.name() + " serves " + first.cuisines().get(1));   // Spice Hub serves Chinese
        System.out.println(restaurants.get(1).city());      // Pune

        // ---- 2. Loop, filter, summarise ----
        List<String> delhi = restaurants.stream().filter(r -> r.city().equals("Delhi")).map(Restaurant::name).toList();
        double avg = restaurants.stream().mapToDouble(Restaurant::rating).average().orElse(0);
        Restaurant best = restaurants.stream().max(Comparator.comparingDouble(Restaurant::rating)).get();
        System.out.println(delhi);                                  // [Spice Hub, Pasta Palace]
        System.out.println("Average rating: " + Math.round(avg * 100) / 100.0);   // 4.26
        System.out.println("Best: " + best.name());                 // Biryani Bay

        // ---- 3. Group into a Map of Lists ----
        Map<String, List<String>> byCity = new TreeMap<>();         // TreeMap keeps the keys sorted
        for (Restaurant r : restaurants) {
            byCity.computeIfAbsent(r.city(), c -> new ArrayList<>()).add(r.name());
        }
        System.out.println(byCity);                                 // {Delhi=[...], Mumbai=[...], Pune=[...]}

        Map<String, Double> avgCost = restaurants.stream()          // the same idea with a Collector
                .collect(Collectors.groupingBy(Restaurant::city, TreeMap::new, Collectors.averagingInt(Restaurant::avgCost)));
        System.out.println(avgCost);                                // {Delhi=700.0, Mumbai=450.0, Pune=375.0}

        // ---- 4. Safe access to nested data ----
        Map<String, Map<String, String>> order = Map.of("customer", Map.of("city", "Pune"));
        System.out.println(order.getOrDefault("customer", Map.of()).getOrDefault("pin", "unknown"));   // unknown

        // ---- 5. JSON by hand: nested data -> text ----
        Map<String, Object> menuItem = new LinkedHashMap<>();       // LinkedHashMap keeps the order we add things
        menuItem.put("name", "Masala Dosa");
        menuItem.put("price", 90);
        menuItem.put("vegetarian", true);
        menuItem.put("tags", List.of("south", "breakfast"));
        System.out.println(toJson(menuItem));   // {"name":"Masala Dosa","price":90,"vegetarian":true,"tags":["south","breakfast"]}

        String sample = """
                {
                  "restaurant": "Spice Hub",
                  "open": true
                }
                """;                                                // a text block: handy for JSON samples
        System.out.println(sample.strip());

        // ---- 6. Copying: shallow vs independent ----
        List<String> cuisines = new ArrayList<>(first.cuisines());  // a new list with the same items
        cuisines.add("Thai");
        System.out.println(first.cuisines().size() + " vs " + cuisines.size());   // 2 vs 3
    }

    // A small recursive JSON writer: it calls itself for nested lists and maps.
    static String toJson(Object value) {
        if (value == null) {
            return "null";
        } else if (value instanceof String s) {
            return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
        } else if (value instanceof Number || value instanceof Boolean) {
            return value.toString();
        } else if (value instanceof List<?> list) {
            return list.stream().map(Examples::toJson).collect(Collectors.joining(",", "[", "]"));
        } else if (value instanceof Map<?, ?> map) {
            return map.entrySet().stream()
                    .map(e -> toJson(String.valueOf(e.getKey())) + ":" + toJson(e.getValue()))
                    .collect(Collectors.joining(",", "{", "}"));
        }
        throw new IllegalArgumentException("cannot write " + value);
    }
}
