# Day 25 — Quiz answers

1. NumPy applies the operation to **every element** (`[2, 4, 6]`); a list `* 2` **repeats** the list (`[1, 2, 3, 1, 2, 3]`).
2. Collapse (sum down) the **rows** → one result per **column**. `axis=1` gives one result per row.
3. `df[(df["quantity"] >= 5) & (df["region"] == "West")]` — use `&` and brackets around each condition.
4. `loc` selects by **label** (and its slice end is inclusive, conditions allowed); `iloc` selects by integer **position** (end exclusive).
5. Count, mean, std, min, quartiles (25/50/75%) and max for numeric columns.
6. So you modify an independent copy and avoid the `SettingWithCopyWarning` / accidentally changing the original.
7. `df["category"].value_counts()` (or `groupby("category").size()`).
8. They are slow and verbose; vectorised column operations run in optimised C and read more clearly.
