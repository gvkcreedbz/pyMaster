# Day 30 — Final Exam answer key

Every output below was produced by actually compiling and running the code with the JDK (via `_dev_tools/build_exam_java.py`).

Scoring (out of 27): 24–27 🏆 · 19–23 ✅ · 13–18 🟡 · <13 🔁 (see LESSON.md).

---

### Q1. (Day 3) — numbers, casts and char arithmetic
```text
3 1 3.5 3 b 98
```
`7 / 2` is whole-number division (3), `%` is the remainder, `7 / 2.0` is a double. `(int) 3.99` cuts the decimals (no rounding). `'a' + 1` is an `int` (98); casting it back with `(char)` gives `b`.

### Q2. (Day 4) — String methods
```text
skco 6 R 5
```
The reversed text is `skcoR avaJ`, its first 4 characters are `skco`. In `java rocks` the first `o` is at index 6. `split(" ")[1]` is `Rocks`, its `charAt(0)` is `R`, and `substring(5)` is `Rocks` (length 5).

### Q3. (Day 4) — == versus equals
```text
false true true true
```
`new String(...)` creates a separate object, so `a == b` is false while `equals` compares the text. `"ch" + "ai"` is joined by the compiler into the same shared literal, so `a == c` is true, and `intern()` returns that shared literal. Always use `equals` for text.

### Q4. (Day 4) — String.format
```text
1,234.50|   42|ab    |003.1|true
```
`%,.2f` adds thousands separators and 2 decimals; `%5d` right-aligns in 5 characters; `%-6s` left-aligns in 6; `%05.1f` pads with zeros to width 5 with one decimal; `%b` prints a boolean.

### Q5. (Day 5) — switch expression
```text
weekend rest
```
A `switch` expression gives a value. A block branch returns it with `yield`. `6` matches `case 6, 7`, so the type is `weekend`, and the ternary chooses `rest` because `6 > 5`.

### Q6. (Day 6) — for loop with a step
```text
10 7 4 1 done
```
`i` starts at 10 and loses 3 each time while it is above 0: 10, 7, 4, 1 (the next value, -2, fails the test). `print` does not end the line.

### Q7. (Day 8) — array aliasing
```text
[99, 2, 3] [1, 2, 3] true false true
```
`b = a` makes two names for the *same* array, so changing `b[0]` changes `a`. `clone()` makes a copy, so `c` keeps `1`. `==` and `equals` on arrays compare identity (false for the copy), `Arrays.equals` compares the contents.

### Q8. (Day 9) — List.remove overloads
```text
[1, 5, 7] 1 false
```
`remove(1)` with an `int` removes the item at index 1 (the 3). `remove(Integer.valueOf(8))` removes the *value* 8. After `add(0, 7)` the list is `[7, 5, 1]`, sorted `[1, 5, 7]`; `5` sits at index 1 and `3` is gone.

### Q9. (Day 9) — sets
```text
[2, 3] [2, 3, 4, 9] 2
```
`retainAll` keeps only the common items (intersection), so `a` becomes `[2, 3]`. A `TreeSet` prints in sorted order and `addAll` ignores values it already has (the `2`). A `HashSet` copy of the list `[1, 1, 2]` holds only 2 distinct values.

### Q10. (Day 10) — counting with a map
```text
{a=3, b=2, c=1} a 0
```
`merge(w, 1, Integer::sum)` starts a count at 1 or adds 1. A `TreeMap` prints its keys sorted. `Collections.max` with `comparingByValue()` finds the entry with the biggest count. `getOrDefault` gives 0 for a missing key.

### Q11. (Day 11) — overloading and varargs
```text
int long double object 0 6
```
Java picks the most specific overload, widening a primitive if needed: `byte` widens to `int`, `float` widens to `double`. A `String` only fits `Object`. A varargs method can be called with no arguments (sum 0) or many.

### Q12. (Day 11) — recursion
```text
13 iahc
```
`f` is the Fibonacci sequence 0, 1, 1, 2, 3, 5, 8, 13 so `f(7)` is 13. `rev` moves the first character behind the reversed rest: `iahc`.

### Q13. (Day 12) — stream pipeline
```text
APPLE-BANANA-CHERRY 55 6
```
Words longer than 4 letters are `apple`, `banana`, `cherry`, upper-cased and joined with `-`. The squares 1+4+9+16+25 add up to 55. The longest word has 6 letters.

### Q14. (Day 12) — sorting with comparators
```text
[Ann, Cy, Bob] Person[name=Ann, age=30]
```
The comparator sorts by age from high to low, then by name A-Z for ties (Ann before Cy), so Bob is last. A record prints as `Name[field=value, ...]`.

### Q15. (Day 17) — try / finally
```text
cleanup 2
1
```
`finally` always runs before the method really returns, so `cleanup 2` prints first. The return value was already copied (`1`) when `return x` ran, so changing `x` in `finally` does not change what is returned.

### Q16. (Day 17) — exception flow
```text
bad number: NumberFormatException
done
after
```
`parseInt("12x")` throws `NumberFormatException`, which is a subclass of `IllegalArgumentException`, so the first matching `catch` runs. `finally` runs, then the program continues after the `try`.

### Q17. (Day 18) — java.time
```text
2026-02-28 SATURDAY 29 false
```
`plusMonths(1)` from 31 January lands on the last valid day, 28 February (2026 is not a leap year). 31 January 2026 is a Saturday. From 31 Jan to 1 March are 29 days. Dates are immutable: every method returns a new `LocalDate`.

### Q18. (Day 19) — inheritance and polymorphism
```text
Rex says Woof | Tom says ...
true
```
The variable type is `Animal`, but the object is a `Dog`, so `sound()` runs the `Dog` version (polymorphism). `toString()` is called automatically when an object is joined to text.

### Q19. (Day 20) — record, enum and sealed
```text
12 9 Square[side=3] true 1
```
A `switch` over a sealed type needs no `default`: the compiler knows every case. A circle of radius 2 gives 3*2*2 = 12, a square of side 3 gives 9. Records get `toString` and `equals` (same values = equal) for free. Enum constants are numbered from 0, so `MID` is 1.

### Q20. (Day 22) — Optional
```text
CHAI -1 false false
```
`map` transforms the value only when there is one. An empty `Optional` skips `map` and uses the `orElse` default (-1). `"chai"` has 4 letters, so `filter(length > 4)` removes it and the Optional becomes empty.

### Q21. (Day 23) — regex
```text
[ab12, zz7] a b c true
```
Each match has group 1 (digits) and group 2 (word); the code glues them back in the order 2 then 1: `ab12`, `zz7`. `\s+` matches any run of white space (spaces and the new line) and is replaced by one space. `matches` must match the whole text, which the date does.

### Q22. (Day 25) — groupingBy and partitioningBy
```text
{East=10, North=125, South=55} {false=3, true=2}
```
`groupingBy` with a `TreeMap` gives the totals per region in sorted order (North 100+25, South 50+5). `partitioningBy` always has both keys, `false` first: 3 orders do not start with N, 2 do.

### Q23. (Day 28) — SQL with JDBC
```text
5 2
```
`WHERE x > 1` keeps 2 and 3, so the sum is 5 and the count is 2. A `ResultSet` starts *before* the first row: call `next()` before reading. The `:memory:` database disappears when the connection closes.

### Q24. (Day 5) — BUG: lossy conversion
```text
<does not compile: incompatible types: possible lossy conversion from double to int>
```
`cups * 12.5` is a `double` and Java refuses to squeeze it into an `int` without your permission, so the file does not compile. Fix: `double total = cups * 12.5;` or an explicit cast `(int) (cups * 12.5)` if you really want to cut the decimals.

### Q25. (Day 6) — BUG: =+ instead of +=
```text
30
```
`=+ p` is parsed as `= +p`: assign the positive number. Every pass replaces `total`, so only the last item is left. Fix: `total += p;` (expected 60).

### Q26. (Day 10) — BUG: missing map key
```text
<raises NullPointerException>
```
`get("bob")` returns `null` for a missing key, and unboxing `null` into an `int` throws `NullPointerException`. Fix: `scores.getOrDefault("bob", 0)` or check `containsKey` first.

### Q27. (Day 9) — BUG: changing a list while looping
```text
<raises ConcurrentModificationException>
```
Removing from a list inside an enhanced `for` loop changes it under the loop's feet, and the iterator notices on the next step: `ConcurrentModificationException`. Fix: `nums.removeIf(n -> n == 2);` or loop over a copy.
