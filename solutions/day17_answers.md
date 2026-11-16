# Day 17 — Quiz answers

1. `else` runs only when the `try` block raised **no** exception; `finally` runs **always** (error or not) — used for cleanup.
2. It catches every error, including bugs and `Ctrl+C`, hiding the real cause. Catch specific exceptions.
3. `ValueError`, `ZeroDivisionError`, `KeyError`, `FileNotFoundError`.
4. The **last** line (error type and message), then the line number above it.
5. `raise ValueError("my message")` (or your own exception class).
6. `total=120` — the variable name and its value (the `=` specifier).
7. `DEBUG`.
8. `logging.error` logs a message; `logging.exception` (inside an `except` block) logs it at ERROR level **plus the full traceback**.
