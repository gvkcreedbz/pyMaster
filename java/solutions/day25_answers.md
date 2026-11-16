# Day 25 - Quiz answers

1. `Sale::region` is the key to group by, `TreeMap::new` says which kind of `Map` to build (keys sorted A-Z), and `Collectors.counting()` is the downstream collector that counts the rows inside each group.
2. A `Long` (so the map is `Map<String, Long>`).
3. `Collectors.summingDouble(...)` adds up, `Collectors.averagingDouble(...)` averages.
4. A `Map` has no order you can sort. The `entrySet()` is a collection of key/value pairs that a stream can sort (by value, biggest first), then `limit(3)` keeps the top three.
5. `partitioningBy` always returns exactly two groups, `true` and `false`, even when one of them is empty. `groupingBy` only creates keys that actually occur.
6. When two elements produce the same key. Pass a merge function as the third argument, e.g. `(first, second) -> first`.
7. Every rounding throws away a tiny part of the value; thousands of those errors add up. Add with full precision and round once, for the final answer.
8. If the map has no value for `"Pune"` it creates a new empty list, stores it and returns it; if there is one, it returns the existing list. So `.add(...)` always has a list to work with.
