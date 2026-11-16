# Day 24 — Testing with JUnit 5 & Git Basics
| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Write automated tests that catch bugs; save and share your work with Git | Upper-intermediate |
## 🌍 Real-world scenario & trend
**A shop's discount code broke on Black Friday.** One wrong `>` instead of `>=` cost real money. Professional teams write tests so such bugs are caught in seconds, and keep history in Git so any change can be undone. **Trend:** every Java job posting asks for JUnit + Git/GitHub; AI-generated code *must* be tested because it can be confidently wrong.
**Why Java?** **JUnit 5** is the standard test framework of the Java world: Spring Boot, Maven and Gradle all run it for you, and every build server (Jenkins, GitHub Actions) fails a release when a test fails. *Coming from Python?* `pytest` finds `test_*` functions; JUnit finds methods marked `@Test`. `assert x == y` becomes `assertEquals(y, x)`, `pytest.raises` becomes `assertThrows`, `parametrize` becomes `@ParameterizedTest`, and a fixture becomes `@BeforeEach`.
## 0. Setup (3 min)
The JUnit "console launcher" is one jar file, already in `java/lib/junit-platform-console-standalone-1.10.3.jar` (if it is missing run `python _dev_tools/fetch_java_libs.py`). The portal and `java Practice.java` put every jar of `java/lib` on the class path for you, so `import org.junit...` just works. To run the tests of a **mini project** by hand:
```powershell
cd java\days\day24_junit_git\mini_project
.\run_tests.ps1        # compiles Shop.java, Cart.java, ShopTest.java and runs the tests
```
## 1. Concepts (with tiny code)
### 1.1 Assertions: "this must be true"
```java
import static org.junit.jupiter.api.Assertions.*;
assertEquals(180.0, applyDiscount(200, 10));        // (expected, actual): silent if equal, else throws AssertionFailedError
assertTrue(isEven(4));      assertFalse(isEven(7));
assertEquals(0.3, 0.1 + 0.2, 0.000001);            // decimals: the 3rd argument is the allowed difference
```
**Order matters for the message:** `assertEquals(expected, actual)` prints `expected: <180.0> but was: <190.0>`. Java also has an `assert` keyword, but it is **switched off** unless you start with `java -ea`, so tests always use JUnit's assertions.
### 1.2 A JUnit test is a method marked `@Test`
```java
// Shop.java
public class Shop {
    public static double applyDiscount(double price, int percent) { return Math.round(price * (100 - percent)) / 100.0; }
}
// ShopTest.java  (the class is named <Thing>Test)
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class ShopTest {
    @Test void tenPercentOff()               { assertEquals(180.0, Shop.applyDiscount(200, 10)); }
    @Test void zeroPercentChangesNothing()   { assertEquals(99.5, Shop.applyDiscount(99.5, 0)); }
}
```
Test methods are not `static`, take no parameters (except in 1.4) and return `void`. The console launcher finds them: `java -jar junit-platform-console-standalone-1.10.3.jar execute --class-path out --scan-class-path` (that is what `run_tests.ps1` runs). With Maven it is just `mvn test` (Day 18). Each test method runs on a **new** object of the test class, so tests cannot depend on each other.
### 1.3 Testing errors: `assertThrows`
```java
@Test void negativePriceIsRejected() {
    IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> Shop.applyDiscount(-5, 10));
    assertEquals("Price must not be negative", e.getMessage());     // you even get the exception back
}
```
The code that must throw goes into a lambda (Day 12). The test fails if nothing is thrown *or* a different type is thrown.
### 1.4 Many cases, one test: `@ParameterizedTest`
```java
@ParameterizedTest
@CsvSource({"100, 10, 90.0", "50, 50, 25.0", "80, 0, 80.0"})
void discountTable(double price, int percent, double expected) {
    assertEquals(expected, Shop.applyDiscount(price, percent));
}
```
JUnit runs the method three times and reports each row separately. (Plain alternative, used in today's `testSlugify`: a `for` loop over a table of cases.)
### 1.5 Fixtures: shared setup with `@BeforeEach`
```java
private Cart cart;
@BeforeEach void freshCart() { cart = new Cart(); }       // runs before EVERY test: a fresh cart each time
@Test void newCartIsEmpty() { assertEquals(0.0, cart.total()); }
```
There is also `@AfterEach` (cleanup), `@BeforeAll`/`@AfterAll` (once per class, must be `static`), `@DisplayName("nice text")` and `@Disabled`.
### 1.6 What makes a good test?
Tiny, independent, readable name (`negativePriceIsRejected`), and it covers **normal**, **edge** (0, empty, boundaries) and **error** cases. Think *Arrange → Act → Assert*. **TDD loop:** write a failing test → write the minimum code → watch it pass → tidy. **Today's grader** uses *mutation testing*: it secretly breaks the code ("mutants") and your test must notice. A test like `assertTrue(true)` never notices, so it fails the check.
### 1.7 Git in 10 commands (lesson only: try them in a copy of your folder)
```powershell
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git init                         # start tracking this folder
git status                       # what changed?
git add .                        # stage everything for the next snapshot
git commit -m "Add discount function"    # save the snapshot (a clear message, never "stuff")
git log --oneline                # history
git diff                         # what exactly changed (not yet staged)
git switch -c feature/coupons    # new branch to experiment safely
git switch main                  # go back;  git merge feature/coupons
```
Share it: create an empty repository on GitHub, then `git remote add origin <url>` and `git push -u origin main`. If you break something: `git restore <file>` throws away your unsaved changes to one file.
### 1.8 `.gitignore`: keep junk and secrets out
A text file named `.gitignore` lists what Git must never commit. For Java: `out/` and `target/` (build output), `*.class`, `.idea/`, `.env`, `*.jar` you can download again, and any file with passwords or API keys. **A secret that was committed once is public forever**, even if you delete it later.
## 2. Code along (30 min)  `Examples.java` + the mini project
- `Examples.java` shows how an assertion works, builds a tiny test runner by hand (so you see what JUnit does for you) and then lets the **real** JUnit run a class with `@Test`, `@BeforeEach` and `@ParameterizedTest`. One test **fails on purpose** so you can read a failure message.
- `mini_project/` holds `Shop.java`, `Cart.java` and `ShopTest.java`. Run `.\run_tests.ps1` there, then break `Shop.java` on purpose (change `100 - percent` to `100 + percent`) and watch the tests fail.
## 3. Common mistakes
- Swapping the arguments: `assertEquals(actual, expected)` gives a confusing message. It is `(expected, actual)`.
- Test class or method not found: the method needs `@Test` (from `org.junit.jupiter.api`, not the old `org.junit`), and must not be `private` or `static`.
- Tests that depend on each other or on the order they run.
- `assertEquals(0.3, 0.1 + 0.2)` for decimals: use the delta version.
- One giant test with 20 assertions: you cannot tell which part failed. After the first failing assertion, the rest of the method does not run.
- Committing secrets/API keys or build folders; committing with the message "stuff".
## 4. Today's tasks  `Practice.java`
Here **you write tests**, and the checker grades them by *mutation testing*: it runs your test against the correct code (must pass) and against secretly broken versions (must fail, otherwise your test is not strong enough). Your test method receives the code under test as a **parameter** (a function or a way to create an `Account`), so the checker can swap in the broken versions.
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Test `isEven`; write `clamp`; test `percentToGrade` boundaries |
| L2-1 … L2-3 | 🟡 Intermediate | Test `slugify` with a case table; test an error with `assertThrows`; test the `Account` class |
| L3-1, L3-2 | 🔴 Challenge | TDD: write `wordCount` so the given real `@Test` class passes; finish a half-written `median` using its failing tests |
Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.
## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
For tests, think: what are the normal inputs, the edges (0, boundaries, negative numbers) and the invalid inputs? Each category kills a different bug. Read the FAIL message: it lists the bugs ("mutants") your test did not catch.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
<code>isEven</code>: 4, 7, 0, a negative even and a negative odd number (in Java <code>-3 % 2</code> is <code>-1</code>). <code>clamp</code>: a value below the range, inside, above, and exactly on both limits. <code>percentToGrade</code>: 100, 90, 89, 75, 74, 50, 49, 0. <code>slugify</code>: a <code>String[][] cases</code> table and a for loop with <code>assertEquals(expected, slugify.apply(input))</code>. Errors: <code>assertThrows(IllegalArgumentException.class, () -&gt; account.withdraw(150));</code>, then check the balance did not change. <code>wordCount</code>: lower-case, regex <code>[a-z']+</code>, <code>merge</code>. <code>median</code>: reject the empty list, then sort a copy.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day24_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>
## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day24_answers.md`
1. How does JUnit know which methods are tests?
2. What happens when an `assertEquals` fails, and what do the two arguments mean?
3. How do you test that a method throws `IllegalArgumentException`?
4. What does `@ParameterizedTest` with `@CsvSource` save you from?
5. What is `@BeforeEach` used for?
6. Why `assertEquals(0.3, 0.1 + 0.2, 0.000001)` for decimals?
7. What is the difference between `git add` and `git commit`?
8. Why have a `.gitignore`?
## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Optional bonus (15 min): `git init` your project folder, add a `.gitignore`, and commit your progress: you will never lose work again.
- Tomorrow: collections in depth and `Collectors` (`groupingBy`, `counting`) on the real `sales.csv`.
