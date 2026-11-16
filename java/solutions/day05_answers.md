# Day 05 - Quiz answers

1. `A`. The first condition `x > 5` is true (7 > 5), so the `"B"` and `"C"` branches are skipped.
2. Java has no truthy/falsy values: `if (0)`, `if ("")` or `if (null)` do not compile. A condition must be a `boolean`. Write `n == 0` or `text.isEmpty()` instead.
3. `=` stores a value, `==` compares. `if (x = 5)` tries to put 5 in `x` and then use the number 5 as a condition, which is a compile error (`int cannot be converted to boolean`).
4. `"blue"` on its own is not a true/false question, so `color == "red" || "blue"` does not compile. Also `==` is wrong for Strings. Write `color.equals("red") || color.equals("blue")`.
5. `String status = age >= 18 ? "adult" : "minor";`
6. `true`. `3 > 2 && 1 > 2` is `true && false` = `false`, and `!` flips it to `true`.
7. At most one block: the first condition that is true runs, the rest are skipped. If none match, the `else` block runs.
8. `default` (it is the "everything else" case; a switch expression must cover all values, so it needs one).
