# Day 16 - Quiz answers

1. A `String` (`"3"`): everything from a CSV is text. Convert with `Integer.parseInt("3")` (or `Double.parseDouble`).
2. `["a", "b", "", ""]` - the `-1` tells `split` to keep empty cells at the end; without it you would get just `["a", "b"]`.
3. `revenue = quantity * unit_price * (1 - discount_pct / 100.0)`.
4. `"2026-01-22".substring(0, 7)`.
5. `write` turns nested data (maps, lists, text, numbers...) into JSON text; `parse` turns JSON text back into maps, lists, text, numbers...
6. Because the cell itself contains the separator (a comma). The quotes tell the reader "this comma belongs to the cell, it does not start a new cell".
7. A merge that goes into nested objects: when both the defaults and the user file hold an object for the same key, those two objects are merged key by key instead of the user's object replacing the whole thing.
8. `split(",")` cuts at EVERY comma, including the one inside the quotes, so you get three broken cells (`"Chai`, ` masala"`, `20`) instead of two correct ones. You need a quote-aware splitter.
