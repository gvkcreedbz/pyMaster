# Day 07 - Quiz answers (Week-1 review)

1. `print` stays on the same line, `println` finishes the line (moves to a new one). `\n` is a new-line character inside text.
2. `17 / 5` is `3` (both are `int`, so Java drops the decimals), `17 % 5` is `2` (the remainder), `17 / 5.0` is `3.4` (one side is a `double`).
3. With a `String` on one side, `+` glues text together, so `"3" + 4` is `"34"`. To add numbers: `Integer.parseInt("3") + 4` gives `7`.
4. Use `a.equals(b)`. `==` asks whether both names point to the very same object in memory, which is often false even when the characters are identical.
5. `name.charAt(0)` is `'A'`, `name.length()` is `5`, `name.substring(1, 3)` is `"ar"` (start included, end excluded).
6. It prints `1`, `4` and `7` (each on its own line); `i` goes 1, 4, 7 and then 10 stops the loop.
7. `break` leaves the whole loop; `continue` skips the rest of this round and jumps to the next round.
8. `age = 18` is an assignment, not a comparison: write `age == 18` (Java even refuses to compile the `int` as a condition). `nextInt()` reads only the digits and leaves the Enter key in the input, so the following `nextLine()` returns an empty line; read everything with `nextLine()` and use `Integer.parseInt`.
