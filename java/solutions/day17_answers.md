# Day 17 - Quiz answers

1. `finally` **always** runs, whether the `try` succeeded, an exception was caught, or one flew past. It is good for cleanup (closing a file/connection, releasing a lock). Try-with-resources is the modern way for resources.
2. It silently swallows the error: the program carries on with wrong data and nobody ever finds out what failed. Catch specific exceptions and at least log or report them.
3. `NumberFormatException`; `ArithmeticException` (`/ by zero`); `ArrayIndexOutOfBoundsException`; `NoSuchFileException` (a kind of the checked `IOException`).
4. A **checked** exception (like `IOException`) must be caught or declared with `throws`, or the code does not compile. An **unchecked** one (a `RuntimeException`, like `IllegalArgumentException`) needs no declaration: it usually signals a bug or bad input.
5. `throw new IllegalArgumentException("Age cannot be negative");` (or your own class that `extends Exception` / `RuntimeException`).
6. It closes the resource automatically at the end of the block, even when an exception is thrown. The resource's class must implement `AutoCloseable` (have a `close()` method).
7. `FINE` is hidden (it is quieter than `INFO`); `WARNING` is shown.
8. The **first** line (exception name and message: *what* happened); then the first `at` line that points into **your** file (*where* it happened).
