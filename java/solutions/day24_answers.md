# Day 24 - Quiz answers
1. By the `@Test` annotation (from `org.junit.jupiter.api`). The launcher scans the classes (usually named `...Test`) and runs every method marked `@Test` (or `@ParameterizedTest`). The method must not be `private` or `static`, and takes no parameters (except parameterized tests).
2. It throws an `AssertionFailedError` and that test is reported as failed (the rest of that method does not run; other tests still run). `assertEquals(expected, actual)`: the first is the value you expect, the second what the code really returned; the message reads `expected: <A> but was: <B>`.
3. `assertThrows(IllegalArgumentException.class, () -> method(badInput));`. The test fails if nothing is thrown or if a different exception type is thrown. The call returns the exception, so you can also check `getMessage()`.
4. Copy-pasting the same test for every input. You write the method once and list the rows (`@CsvSource({"100, 10, 90.0", ...})`); JUnit runs and reports each row separately.
5. A method marked `@BeforeEach` runs before every test method and sets up shared, fresh state (for example `cart = new Cart();`), so tests do not depend on each other.
6. Decimals are stored in binary, so `0.1 + 0.2` is `0.30000000000000004`, not exactly `0.3`. The third argument is the allowed difference, so the test passes for tiny rounding errors.
7. `git add` puts the changes you choose into the *staging area* (what the next snapshot will contain). `git commit` saves the staged changes as a permanent snapshot in the history, with a message.
8. To keep files out of the repository that must not be shared or do not belong there: secrets and API keys (`.env`), build output (`out/`, `target/`, `*.class`), IDE folders (`.idea/`). A secret committed once stays in the history.
