# Day 18 - Quiz answers

1. The class belongs to the package `shop.billing`. The file must be in a folder path that matches: `shop/billing/ClassName.java`.
2. `java.lang`, for example `String`, `Math`, `System` and `Integer`. No `import` is needed for them.
3. `javac -d out ...` compiles the source files and puts the `.class` files in the folder `out` (in matching package folders). `java -cp out App` runs the class `App` and looks for classes inside `out` (the class path).
4. A zip-like file holding compiled classes and a manifest (`META-INF/MANIFEST.MF`). Run an executable one with `java -jar app.jar`.
5. The unique address of a project or library in Maven (for example `org.junit.jupiter : junit-jupiter : 5.10.2`).
6. `MONDAY` (a `DayOfWeek` value).
7. Month names depend on the computer's language. With `Locale.ENGLISH` you always get `Dec`, `Nov`... so the output is the same everywhere.
8. A seed makes the "random" sequence repeatable, so a test gets the same numbers every run. Without a seed the results change each time.
