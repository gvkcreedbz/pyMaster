# Day 09 - Quiz answers

1. `List<String> cart = new ArrayList<>(); cart.add("milk");` and the first item is `cart.get(0)`.
2. It throws `UnsupportedOperationException` (the list is read-only). Make a changeable copy with `new ArrayList<>(theList)`.
3. A list holds objects, not primitive types. Write `List<Integer>` (the wrapper type of `int`).
4. `n.remove(1)` is an `int`, so it removes the item **at position 1** (the `1`), leaving `[5, 7]`. `n.remove(Integer.valueOf(1))` removes the **value** 1, but 1 is no longer in the list, so nothing happens. Final: `[5, 7]`.
5. `3` (the set keeps 1, 2, 3). `s.get(0)` does not compile: a set has no positions.
6. `HashSet` is very fast and gives no promised order. `TreeSet` keeps the items sorted (A-Z / smallest first) and is a bit slower.
7. `[B, C]` - `retainAll` keeps only the items that are also in the other set (the intersection).
8. `==` compares the two objects (are they the very same object?), and that can be `false` for equal numbers above 127 (`Integer a = 1000, b = 1000; a == b` is `false`). `.equals` compares the values.
