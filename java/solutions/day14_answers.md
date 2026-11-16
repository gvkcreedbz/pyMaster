# Day 14 - Week-2 review: quiz answers

1. `[1, 2, 3]` - `b = a` copies the *reference*, not the list: both names point to the same list.
2. It throws `UnsupportedOperationException`: lists made by `List.of(...)` cannot be changed. Use `new ArrayList<>(List.of(1, 2))` for a changeable one.
3. `counts.merge(w, 1, Integer::sum);` (add 1 to the old count, or start at 1).
4. `9` - the odd numbers 1, 3 and 5 add up to 9.
5. `==` compares whether two variables point to the *same* text object, not whether the letters match, so it can be false for equal text. Write `cmd.equals("quit")` (or use a `switch`).
6. `Food  |` - the text is left-aligned in a field 6 wide (`Food` + 2 spaces), then the `|`.
7. `expenses.stream().sorted(Comparator.comparingDouble(Expense::amount).reversed().thenComparing(Expense::date)).toList()`
8. Any three of: a constructor, getter methods (`name()`), `equals`/`hashCode`, a readable `toString`, immutability (fields cannot change).
