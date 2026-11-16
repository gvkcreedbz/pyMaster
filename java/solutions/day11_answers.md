# Day 11 - Quiz answers

1. A parameter is the variable in the method definition (`String name`); an argument is the actual value you pass in the call (`"Aarav"`).
2. `void` means the method returns no value. `int x = printLine("a");` is a compile error because there is nothing to put into `x`.
3. Write an overload: a second method with the same name and fewer parameters that calls the longer one with the default, for example `static double total(double price) { return total(price, 1); }`.
4. It is an `int[]`. `average()` calls it with an empty array (`numbers.length == 0`); the practice task returns `0.0` for that case.
5. The base case is the input where the method stops calling itself (for example `n <= 1` returns `1`). Without it the calls never end and Java throws `StackOverflowError`.
6. `a` is still `5`: the method changed only its own copy. With an `int[]` the method gets a reference to the same array, so `arr[0] = 10` is visible to the caller.
7. The method has a non-`void` return type but no `return`: `error: missing return statement`.
8. A returned value can be stored, tested, formatted or combined with other results; text printed inside the method is gone and the method cannot be tested by comparing a result.
