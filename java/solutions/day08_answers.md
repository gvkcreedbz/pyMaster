# Day 08 - Quiz answers

1. `[99, 2, 3]`. `b = a` copies only the name; both names point to the same array. Use `a.clone()` for a real copy.
2. `new int[3]` holds `0, 0, 0`. `new String[2]` holds `null, null` (no text yet).
3. `cart[cart.length - 1]`. `cart[-1]` compiles but crashes at run time with `ArrayIndexOutOfBoundsException` (Java has no negative indexes).
4. An array has a **field** `length` (no brackets). A `String` has a **method** `length()` (with brackets).
5. `n` is `[1, 2, 3]`. `Arrays.sort` sorts the array itself and returns nothing (`void`), so never write `n = Arrays.sort(n)`.
6. It prints the type and a hash such as `[I@1b6d3586`, not the values. Use `Arrays.toString(scores)` (or `Arrays.deepToString` for tables).
7. `t[1][0]` is `3` (row 1, column 0). `t.length` is `2` (the number of rows).
8. Create a new, longer array (`Arrays.copyOf(old, 4)`), then put the new item in the last slot. An array can never grow in place.
