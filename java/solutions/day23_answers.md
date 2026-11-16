# Day 23 - Quiz answers
1. A backslash starts an escape (`\n`, `\t`) in a Java string, so the regex backslash must be doubled: the string `"\\d"` contains the two characters `\d`, which the regex engine reads as "a digit". A literal dot is `"\\."` (a plain `.` means any character).
2. `find()` looks for a match anywhere inside the text (call it again for the next match). `matches()` succeeds only if the whole text fits the pattern, so it is the one to use for validation. `"a123b"`: `find()` for `\d{3}` is true, `matches()` is false.
3. Exactly three digits, a dash, then exactly four digits, for example `555-1234`.
4. The `?` makes the repeat lazy: `.+?` takes as FEW characters as possible (at least one) so the match stops at the first place the rest of the pattern fits. Greedy `.+` takes as many as possible.
5. `matcher.group("name")` after a successful `find()` or `matches()` (a group is declared as `(?<name>...)`). In a replacement text, `$1` is group 1: `text.replaceAll("(\\d+)", "<$1>")`.
6. The class is `final` (cannot be extended), every field is `private final` (assigned once), and there are no methods that change state (changes return a new object). Mutable inputs and outputs, like lists, are copied.
7. The caller gets the real list and can add or remove items behind the object's back. Fix: store `List.copyOf(items)` (or `Collections.unmodifiableList`) and return that, or return a fresh copy.
8. Any three of: `camelCase` for methods and variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants, lowercase package names, meaningful names, methods named as verbs. A guard clause checks bad input first and returns or throws immediately, so the main logic is not nested inside `if`s.
