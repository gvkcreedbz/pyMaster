# 🔍 Error Decoder — what `javac` and the JVM are telling you

Java has **two kinds** of errors:
- **Compile errors** — `javac` refuses to run your code. Nothing has executed yet. Fix the **first** error first; later ones are often side effects.
- **Runtime exceptions** — the program started, then crashed. Read the **first line** of the stack trace (what), then the first `at ...` line that names **your** file (where).

```
Main.java:7: error: incompatible types: String cannot be converted to int     ← WHAT   (file:LINE: error: message)
        int qty = "3";                                                         ← the code
                  ^                                                            ← WHERE (the caret)
1 error
```
```
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.length()" because "name" is null   ← WHAT
	at Main.greet(Main.java:12)          ← WHERE: first line in YOUR file = the culprit
	at Main.main(Main.java:5)            ← who called it (read downwards)
```

## A. Compile errors (before the program runs)
| Message | Plain English | Typical cause → fix |
|---|---|---|
| `error: ';' expected` | A statement isn't finished | missing `;` at the end of **this or the previous** line |
| `error: unclosed string literal` | A `"` was never closed | `System.out.println("Hi);` → add the closing `"` |
| `error: ')' expected` / `'(' expected` / `illegal start of expression` | Brackets don't match | count `( [ {` against `) ] }`; a missing `}` earlier makes later lines look wrong |
| `error: reached end of file while parsing` | A `}` is missing at the end | add the closing brace; format the file (Shift+Alt+F) to spot it |
| `error: class, interface, enum, or record expected` | Code outside a class (often an extra `}`) | remove the stray `}` or move the code into the class |
| `error: cannot find symbol` + `symbol: variable x` | Java has never heard of `x` | typo, wrong case (`system.out`, `string`), used outside its `{ }` scope, forgot to declare it, text without quotes |
| `error: cannot find symbol` + `symbol: method foo(int)` | No such method (for those argument types) | typo; wrong argument types; method is in another class (`obj.foo()`); forgot `import` |
| `error: package system does not exist` | `system.out` in lower case | write `System.out` |
| `error: incompatible types: String cannot be converted to int` | Wrong type on the right of `=` | `Integer.parseInt(text)`; or declare `String` |
| `error: incompatible types: possible lossy conversion from double to int` | Would lose the decimals | cast on purpose `(int) x`, or use `double` / `Math.round(x)` (returns `long`) |
| `error: incompatible types: int cannot be converted to boolean` | `if (x = 5)` or `if (count)` | use `==` for comparing; conditions must be `boolean` |
| `error: bad operand types for binary operator '&&'` | `&&`/`\|\|` on non-booleans | write full comparisons: `x > 1 && x < 5` |
| `error: variable x might not have been initialized` | Local variable read before it has a value | give it a value (`int x = 0;`) or assign in **every** branch |
| `error: variable x is already defined in method main(String[])` | Declared twice in the same scope | remove the type the second time (`x = 5;`) or rename |
| `error: cannot assign a value to final variable x` | Reassigning a `final` | drop `final`, or don't reassign |
| `error: missing return statement` | A branch of the method returns nothing | return in every path (add `else` / a final `return`) |
| `error: unreachable statement` | Code after `return`/`break`/`continue`/`throw` | delete it or fix the logic |
| `error: non-static variable x cannot be referenced from a static context` (also: non-static method) | `main` is static, `x` belongs to an object | make it `static`, or create an object: `new Thing().x` |
| `error: incomparable types: int and String` / `bad operand types for binary operator '=='` | Comparing different types | convert one side; compare strings with `.equals` |
| `error: unreported exception IOException; must be caught or declared to be thrown` | A checked exception is ignored | wrap in `try/catch`, or add `throws IOException` to the method |
| `error: exception IOException is never thrown in body of corresponding try statement` | Catching a checked exception nothing throws | remove that `catch` |
| `error: Foo is not abstract and does not override abstract method bar() in Baz` | Class promised a method it doesn't have | implement `bar()` with the same signature (and `@Override`) |
| `error: constructor Foo in class Foo cannot be applied to given types` | Wrong constructor arguments | look at the constructor's parameter list (`required` / `found` lines) |
| `error: method x in class Y cannot be applied to given types` | Wrong number/type of arguments | compare the call with the method signature in the message |
| `error: 'void' type not allowed here` | Using the result of a `void` method (e.g. inside `println(...)`) | make the method return a value, or call it on its own line |
| `error: array required, but String found` | `s[0]` on a String | `s.charAt(0)` |
| `error: char cannot be dereferenced` / `int cannot be dereferenced` | `.method()` on a primitive | use `String.valueOf(c)`, or the wrapper (`Integer`) |
| `error: unexpected type` + `required: reference` + `found: int` | Primitive inside generics: `List<int>` | `List<Integer>` |
| `error: class Foo is public, should be declared in a file named Foo.java` | File name ≠ public class name | rename the file or the class |
| `error: invalid method declaration; return type required` | Method without a return type (often a misspelled constructor) | add `void`/a type, or fix the class name |
| `error: illegal character: '\u201c'` | "Curly quotes" pasted from Word/WhatsApp | retype with straight `"` |
| `error: duplicate class: X` | Two classes with the same name in one compilation | rename one |
| `error: switch expressions are not supported in -source 8` (or `records` / `text blocks` / `var` not supported) | `javac` is older than the feature | check `javac -version` says 21 |
| `warning: [preview] ...` / `error: ... is a preview feature` | Using a preview feature | not needed in this course; remove it |
| `Note: Foo.java uses unchecked or unsafe operations` | Raw types (`List` instead of `List<String>`) | add the type argument: `new ArrayList<String>()` / `<>` |

## B. Runtime exceptions (the program crashed)
| Exception | Plain English | Typical cause → fix |
|---|---|---|
| `NullPointerException` | You used `.something` on `null` ("nothing") | variable never assigned; `map.get(missing)`; method returned `null`; fix: initialise, `getOrDefault`, `Optional`, check `x != null`. The message tells you *which* variable |
| `ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 5` | Array position doesn't exist | valid indexes: `0 … length - 1`; loop with `i < arr.length` (not `<=`) |
| `IndexOutOfBoundsException: Index 3 out of bounds for length 3` | Same, for `List` | `i < list.size()`; check `isEmpty()` before `get(0)` |
| `StringIndexOutOfBoundsException: begin 0, end 9, length 5` | Bad `charAt` / `substring` position | check `s.length()` first |
| `NumberFormatException: For input string: "abc"` | Text isn't a number | validate/`try-catch`; `trim()` first; `"12.5"` isn't an `int` (`Double.parseDouble`) |
| `InputMismatchException` | `nextInt()` got text | read lines and parse, or check `hasNextInt()` |
| `NoSuchElementException: No line found` | `Scanner` ran out of input | end of input (Ctrl+Z on Windows), or you read more lines than were supplied; check `hasNextLine()` |
| `ArithmeticException: / by zero` | Integer divided by 0 (doubles give `Infinity`/`NaN` instead) | check the divisor before dividing |
| `ClassCastException: class A cannot be cast to class B` | Wrong cast | check with `instanceof` first; use generics instead of casts |
| `IllegalArgumentException` / `IllegalStateException` | A method refused your argument / the object is in the wrong state (often thrown *on purpose*) | read the message; fix the input or the call order |
| `UnsupportedOperationException` | Modifying an immutable collection | `List.of`, `Map.of`, `stream.toList()`, `Arrays.asList` (can't add) → copy with `new ArrayList<>(...)` |
| `ConcurrentModificationException` | Changed a list while looping over it | `list.removeIf(...)`, an `Iterator`, or loop over a copy |
| `IllegalStateException: Duplicate key x` | `Collectors.toMap` found the same key twice | give a merge function: `toMap(k, v, (a, b) -> a)` or use `groupingBy` |
| `IllegalStateException: stream has already been operated upon or closed` | A stream was reused | build a new stream each time |
| `NoSuchElementException: No value present` | `Optional.get()/orElseThrow()` on empty | `orElse(...)`, `isPresent()`, `ifPresent(...)` |
| `NegativeArraySizeException` | `new int[-1]` | check the size |
| `OutOfMemoryError: Java heap space` | Too much data held at once | stream the file (`Files.lines`) instead of loading it all; fix endless loops that keep adding |
| `StackOverflowError` | A method calls itself forever | add/repair the stopping condition (base case) of the recursion |
| `ExceptionInInitializerError` | A `static` initialiser threw | read the "Caused by" line |
| `java.nio.file.NoSuchFileException: data/x.csv` | Path wrong / wrong working directory | print `Path.of("").toAbsolutePath()`; run from the day folder |
| `java.nio.file.AccessDeniedException` / `FileSystemException ... being used by another process` | File open in Excel / protected folder | close the file; choose another folder |
| `java.io.UncheckedIOException` / `MalformedInputException: Input length = 1` | Wrong text encoding | `Files.readAllLines(p, StandardCharsets.UTF_8)` / `ISO_8859_1` for Excel files |
| `java.net.ConnectException` / `HttpTimeoutException` | Server not running / network problem | start the server first; check the URL and port; set `.timeout(...)` |
| `java.net.BindException: Address already in use` | Port already taken | stop the old program (Ctrl+C) or pick another port |
| `java.sql.SQLException: No suitable driver found` / `ClassNotFoundException: org.sqlite.JDBC` | sqlite-jdbc jar not on the classpath | `python _dev_tools\fetch_java_libs.py`; run with `-cp "..\..\lib\*"` |
| `SQLException: [SQLITE_ERROR] SQL error or missing database (no such table: orders)` | Table not created / wrong DB file | run `CREATE TABLE` first; check the DB path |
| `SQLException: ... NOT NULL constraint failed` / `UNIQUE constraint failed` | The database rejected your data | supply the value / avoid duplicates; read the column name in the message |
| `SQLException: ... Parameter index out of range` | `?` count ≠ `setXxx` calls | one `setXxx(i, value)` per `?` (indexes start at **1**) |
| `UnsupportedClassVersionError: ... class file version 65.0, this version of the Java Runtime only recognizes class file versions up to 52.0` | Compiled with Java 21, run with an older `java` | `java -version` must say 21; delete stale `.class` files |
| `Error: Could not find or load main class X` / `ClassNotFoundException: X` | Wrong class name/folder/classpath | run `java File.java` (with `.java`) from the file's folder; case matters |
| `Error: Main method not found in class X` | No `public static void main(String[] args)` | check the exact signature |
| `java.lang.NoClassDefFoundError` | A class existed when compiling but not now | missing jar on `-cp`, or renamed class |
| `AssertionError` | An `assert` / JUnit test failed | compare expected vs actual in the message; fix code or the test |

## Not an error, but a bug (no message!)
| Symptom | Likely cause |
|---|---|
| Output is *almost* right | off-by-one (`<` vs `<=`, `0` vs `1`), `int` division (`7 / 2 == 3`), wrong comparison |
| `if (a == b)` on strings is `false` although they look equal | `==` compares references; use `a.equals(b)` |
| Prints `[I@1b6d3586` or `Person@7a81197d` | no `toString()`: use `Arrays.toString(arr)`, or add `@Override toString()` |
| A list "changed by itself" | aliasing: `b = a` shares one object — copy with `new ArrayList<>(a)` |
| Money shows `0.30000000000000004` | binary floating point — `BigDecimal`, or round with `printf("%.2f")` |
| Integer result suddenly negative | overflow: use `long` / `Math.addExact` |
| Method "does nothing" | return value ignored (`s.toUpperCase();` — strings are immutable: `s = s.toUpperCase();`) |
| `scanner.nextLine()` returns an empty string | leftover Enter after `nextInt()` — read lines and `parseInt` |
| `switch` runs several cases | old-style `switch` without `break`; use `case X ->` arrows |
| Loop never ends | the loop variable never changes inside `while` |
| `if (x > 5);` — body always runs | stray `;` after the condition |
| Results differ every run | randomness (`new Random(42)`), `HashSet`/`HashMap` ordering, current time |
| Characters look wrong (`â‚¹`) | encoding: save UTF-8, `chcp 65001`, `-Dfile.encoding=UTF-8` |

## Debugging toolbox (in order)
1. **Read** the message (compile: first error; runtime: first line + first `at` line in your code). 2. **Print** the values near the failing line (`System.out.println("[" + x + "]")`). 3. **Shrink** the problem to the smallest failing example (try it in `jshell`). 4. **Explain it aloud** (rubber-duck). 5. **Search** the exact message (without your file names). 6. **Ask** with: your code, the full error, what you expected, what you tried. See `how_to_get_unstuck.md`.
