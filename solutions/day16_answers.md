# Day 16 — Quiz answers

1. As text: `"3"` (a `str`). Convert with `int()`/`float()`.
2. The `csv` module handles line endings itself; without `newline=""` you can get blank lines between rows on Windows (and mis-parse embedded newlines).
3. `json.load(file)` reads from an open file; `json.loads(text)` parses a string.
4. `writer.writeheader()`.
5. `quantity × unit_price × (1 − discount_pct / 100)`.
6. `"2026-01-22"[:7]`.
7. It keeps non-English characters (like `₹`) readable in the file instead of writing `\u20b9`.
8. Merging two nested dictionaries recursively: matching sub-dicts are merged key by key; other values from the override replace the defaults.
