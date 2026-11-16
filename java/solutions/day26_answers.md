# Day 26 - Quiz answers

1. Messy data hides in details (blanks, extra spaces, odd spellings, duplicates). Counting rows, listing the distinct values and counting blanks shows what to fix; cleaning blind can silently corrupt the results.
2. **Fill** when a safe, honest default exists (a blank discount means no discount, so 0). **Drop** when guessing would invent facts (an unknown quantity). Record the decision either way.
3. `"South"`: `strip()` removes the spaces, `toUpperCase` on the first character makes it a capital, `substring(1).toLowerCase()` makes the rest small.
4. When reading, the comma inside the quotes must not be treated as a separator (use a quote-aware split instead of `split(",")`). When converting, `Integer.parseInt("1,999")` throws `NumberFormatException`, so remove the comma (and spaces) first.
5. It runs two collectors on the same stream in one pass and combines their two results with a function (for example the count and the sum of a group into a `Summary` record).
6. Trend over time: a line chart. Comparing four regions: bars. Spread of order values: a histogram.
7. Without a tie-breaker, entries with an equal sort key can come out in a different order. The top-N list would then differ between runs or machines; `thenComparing` makes it deterministic.
8. The lookup finds nothing (`get` returns `null`) and the row is silently missing or crashes with a `NullPointerException` later. Clean the keys first, and check the row counts afterwards.
