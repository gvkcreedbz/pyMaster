# Day 26 — Quiz answers

1. Messy data hides in the details (blanks, whitespace, odd spellings, duplicates). `info()`, `isna().sum()` and `unique()` show you what to fix; cleaning blind can silently corrupt results.
2. **Fill** when a safe, honest default exists (e.g. discount blank → 0). **Drop** when guessing would invent facts (e.g. unknown quantity). Record the decision either way.
3. `" sOUTH "` → `"South"` (spaces removed, then first letter capital, rest lower-case).
4. A DataFrame indexed by the values of `a` with one column `n` containing the row count of each group.
5. When you want to keep **every row of the left table** even if the right table has no match (unmatched right-hand values become `NaN`).
6. Trend over time → **line**; comparing 4 regions → **bar**; distribution of order values → **histogram**.
7. It frees the figure's memory; otherwise figures pile up (and later charts can draw on top of old ones).
8. If key values differ (`"east"` vs `"East"`, trailing spaces) rows don't match, so the joined columns are `NaN` without raising an error — clean the keys first and validate the row counts after.
