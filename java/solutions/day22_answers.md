# Day 22 - Quiz answers

1. It asks the collection for an `Iterator`, then repeats `hasNext()` / `next()` until `hasNext()` is `false`. The for-each is a shortcut for that loop.
2. `hasNext()` (is there another item?) and `next()` (give me the next item and move forward).
3. `T` is a type parameter: a placeholder for a real type that is chosen when you use the class (`Box<String>`, `Box<Integer>`). One class works for every type, and the compiler still checks the types.
4. Generics only work with objects, not primitives. Use the wrapper type: `List<Integer>` (Java converts `int` <-> `Integer` for you).
5. The type tells the caller "there may be no answer", so they must handle the empty case (`orElse`, `map`, `ifPresent`) instead of getting a surprise `NullPointerException` later.
6. `4` (the box holds "Chai", `map(String::length)` makes a new `Box<Integer>` holding 4).
7. `Predicate<T>` (its method `test` returns a `boolean`).
8. It runs **before** control leaves the try block, so before any `catch` block starts: the resource is always closed, with or without an exception.
