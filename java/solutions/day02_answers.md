# Day 02 - Quiz answers

1. `5` is `int`, `5.0` is `double`, `"5"` is `String`, `'5'` is `char`, `true` is `boolean`.
2. `10`. `y` got its own copy of 10 when it was created; changing `x` later does not touch it.
3. Valid: `item2` and `my_price`. Invalid: `2ndItem` (starts with a digit), `my-price` (the `-` is a minus sign), `class` (reserved keyword).
4. `53` (the number is glued on as text) and `8` (two numbers are added).
5. `"349.50"` (a `String` with 2 decimals).
6. `nextInt()` reads only the digits and leaves the end of the line in the input, so `nextLine()` reads that empty rest. Fix: call `nextLine()` once to throw it away, or read every line with `nextLine()` and use `Integer.parseInt`.
7. It crashes with a `NumberFormatException`: `"12.5"` is not a whole number. Use `Double.parseDouble("12.5")`.
8. It makes the variable a constant: any later assignment (`GST = 5;`) is a compile error.
