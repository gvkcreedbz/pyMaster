# Day 12 - Quiz answers

1. `[2, 4, 6, 8]` - `map` turns every item into its double, and `toList()` collects the result.
2. `18` - the numbers divisible by 3 are 3, 6 and 9; they add up to 18.
3. `Predicate<String>` - it takes one `String` and gives back a `boolean`.
4. `String::toUpperCase`
5. `[ccc, bb, a]` - sorted by length, longest first (`reversed()` flips the order).
6. A variable used inside a lambda must be *effectively final* (it cannot change), but `total += n` changes it. Use `list.stream().mapToInt(Integer::intValue).sum()` instead.
7. `true` - "all of nothing" is true (there is no item that fails the test). The same as Python's `all([])`.
8. To break ties: when two items have the same first key (e.g. equal plays), the second key (e.g. title A-Z) decides their order.
