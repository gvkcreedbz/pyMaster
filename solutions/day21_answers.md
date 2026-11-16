# Day 21 — Week-3 Review Test answers

1. `"r"` read (error if missing); `"w"` write — creates or **erases**; `"a"` append at the end.
2. `with` closes the file automatically even on errors; `encoding="utf-8"` makes text with `₹`, accents, emojis safe on every OS.
3. `str` (text) — convert yourself with `int()`/`float()`.
4. `dump` writes to an open file; `dumps` returns a JSON string.
5. `try` → `except` → `else` → `finally`. `else` runs only if no error; `finally` runs always.
6. It hides real bugs (even `Ctrl+C` and typos) and gives no information. Catch specific exceptions.
7. It runs code only when the file is executed directly, not when imported, so a file can be a script and a module.
8. Isolated, reproducible dependencies per project.
9. The object the method was called on.
10. The list is shared by all `Cart` objects; create it in `__init__`.
11. Calls the parent class `__init__` so parent setup also happens.
12. `__len__`; `__eq__`.
13. `@classmethod` gets the class (`cls`) — alternative constructors; `@staticmethod` gets nothing automatically — a plain helper inside the class namespace.
14. `__init__`, `__repr__`, `__eq__` (and optionally ordering, immutability, hashing).
15. IS-A.

## Project notes
- The late-fee/loan-limit rules live **inside** the `Library` class — outside code can't forget to apply them.
- Next step (Day 28): replace the JSON file by SQLite so many programs can share the data safely.
