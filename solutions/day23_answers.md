# Day 23 — Quiz answers

1. In a normal string `\d` / `\b` / `\n` are escape sequences interpreted by Python; a raw string passes the backslashes unchanged to the regex engine.
2. `match` only tries at the **start** of the string; `search` finds the first match **anywhere**; `fullmatch` requires the **whole** string to match.
3. Three digits, a hyphen, then four digits (e.g. `555-1234`).
4. `+?` makes the repetition **lazy**: it matches as little as possible instead of as much as possible.
5. Give the groups names `(?P<name>...)` and call `match.groupdict()`.
6. No — hints aren't enforced at run time; checkers (mypy, pyright, IDEs) and readers use them.
7. e.g. `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants (4-space indents, ~88–100 char lines are also in PEP 8 / Ruff defaults).
8. `ruff check` lints (finds bugs/style issues); `ruff format` auto-formats the code.
