# Day 29 - Quiz answers

1. **E**xtract (read the raw data), **T**ransform (clean it and add what you need, such as revenue), **L**oad (store it, here in SQLite). A report is usually the last step.
2. Schedulers and scripts only see the number: `0` means success, anything else means failure. Without it a broken job looks like a good one.
3. The raw file is your evidence and your way to re-run. If you overwrite it, a bug in the cleaning code destroys the original data. Write results into a separate output folder.
4. The price `"4,999"` has a comma *inside quotes*. `split(",")` cuts it into two cells and shifts every later column. A quote-aware splitter (`splitCsvLine`) flips an `inQuotes` flag and only splits on commas outside quotes.
5. A record has `equals`/`hashCode` over all its fields, so `raw.size() - new HashSet<>(raw).size()` is the number of exact copies. `new LinkedHashSet<>(raw)` removes them and keeps the first of each in order.
6. `?` placeholders keep data separate from SQL (no injection, no quoting bugs) and `addBatch` sends many rows efficiently. One transaction (`setAutoCommit(false)` ... `commit()`) means all rows are saved or none, and it is much faster than one commit per row.
7. Small methods are easy to name, test, reuse and replace. `runPipeline` just calls them in order.
8. Log the numbers (rows before/after, duplicates, total revenue), write a quality report before cleaning, print clear `Error: ...` messages, return a non-zero exit code, and add automated checks or tests.
