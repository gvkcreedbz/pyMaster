# Day 11 — Methods (reusable building blocks)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Design clean methods: parameters, return values, overloading, varargs, scope and recursion | Intermediate |

## 🌍 Real-world scenario & trend
**A billing service.** Real systems do not have one giant `main`; they have small methods such as `calculateTax()`, `applyCoupon()` and `sendReceipt()`, each doing one job and each testable on its own. In professional Java, 90% of the code you read is methods calling other methods.

**Why Java?** Java code is organised as classes full of methods, and clear method signatures (name, parameter types, return type) are how teams agree on how pieces fit together. IDEs, code reviewers and AI coding assistants all read the *signature* first. "Pure" methods (same input gives the same output, nothing else changes) are the easiest to test; the auto-checker you use every day tests your methods exactly that way. *Coming from Python?* `def` becomes a signature with types, there are **no default values** (you write overloads instead), `*args` becomes `int...`, and there is no `**kwargs` (pass a `Map`).

## 0. Warm-up (5 min) — Day 10 recap
- What does `map.getOrDefault("x", 0)` return when `"x"` is missing?  • How do you add 1 to a word counter with `merge`?

## 1. Concepts (with tiny code)

### 1.1 Define and call
```java
static String greet(String name) {          // static  |  returns a String  |  called greet  |  takes one String
    return "Hello, " + name + "!";
}

String message = greet("Aarav");             // "Aarav" is the argument, name is the parameter
```
You have typed `static` since Day 1: for now it means "this method belongs to the class itself, so `main` can call it directly". (`static` is explained fully on Day 19, when we create objects.) Write the **return type** before the name; Java checks that every `return` matches it.

### 1.2 `return` vs `print`, and `void`
`return` hands a value back so you can use it. `System.out.println` only shows something on screen. A method that returns nothing says `void`.
```java
static int add(int a, int b) { return a + b; }
static void printLine(String text) { System.out.println(">> " + text); }   // void: no return value

int total = add(2, 3) * 10;       // 50 (you cannot do this if add only printed)
// int x = printLine("a");        // compile error: a void method gives no value
```
A non-`void` method must return on **every** path; otherwise: `error: missing return statement`.

### 1.3 Overloading: one name, different parameters
Java has no default argument values. Instead you may write several methods with the **same name but different parameter lists**; Java picks the one that matches the call.
```java
static double total(double price)                         { return total(price, 1); }
static double total(double price, int qty)                { return total(price, qty, 18); }
static double total(double price, int qty, int taxPercent) { return price * qty * (1 + taxPercent / 100.0); }

total(100);          // 118.0   (qty 1, tax 18)
total(100, 3, 5);    // 315.0
```
Only the parameters count: two methods that differ just in the return type are not allowed. You already use overloading: `println` accepts an `int`, a `String`, a `double`...

### 1.4 Varargs: any number of arguments
```java
static double average(int... numbers) {      // inside the method, numbers is a plain int[]
    if (numbers.length == 0) { return 0; }
    int sum = 0;
    for (int n : numbers) { sum += n; }
    return (double) sum / numbers.length;
}
average(4, 8, 6);       // 6.0
average();              // 0.0
average(new int[]{1, 2});   // an array is fine too
```
The varargs parameter must be the **last** one. *Python twin:* `*args`. For `**kwargs`, take a `Map<String, Object>`.

### 1.5 Returning several values
A method returns exactly one thing. To give back more, return an array (or a list, or a `record` from Day 13).
```java
static int[] minAndMax(int[] numbers) {
    int min = numbers[0], max = numbers[0];
    for (int n : numbers) {
        if (n < min) min = n;
        if (n > max) max = n;
    }
    return new int[]{min, max};
}
int[] range = minAndMax(new int[]{4, 8, 6});     // range[0] = 4, range[1] = 8
```

### 1.6 Scope, and "who sees my change?"
A variable lives only inside the braces `{ }` where it was declared (and the loop it belongs to).
```java
for (int i = 0; i < 3; i++) { int square = i * i; }
// System.out.println(i);        // compile error: cannot find symbol
```
Java always passes a **copy of the argument**. For a plain number the copy is separate; for an array or list the copy still points to the *same* array, so the method can change the caller's data.
```java
static void tryToChange(int price, int[] prices) {
    price = 999;         // only the method's own copy: the caller's price is unchanged
    prices[0] = 999;     // same array as the caller's: the caller sees this
}
```
Same idea as Python's "mutable vs immutable arguments". When you must not change the caller's list, build a new one: `new ArrayList<>(items)` and change the copy.

### 1.7 Recursion: a method that calls itself
```java
static long factorial(int n) {
    if (n <= 1) {                 // base case: stops the recursion
        return 1;
    }
    return n * factorial(n - 1);  // the same problem, but smaller
}
factorial(5);    // 120
```
Always have a base case and make every call move towards it. Without one Java ends the program with `StackOverflowError` (after about 10,000 nested calls). Every call gets its own copy of the parameters, which is why the calls do not mix up.

### 1.8 Good method habits
One job per method · a verb name (`calculateTotal`, `isAdult`) · `return` results instead of printing inside (printing makes a method hard to test) · a few parameters · small enough to read at a glance. A method that answers yes/no is usually named `isSomething` and returns `boolean`.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button. Try adding a fourth `total` overload, or delete the base case of `factorial` and read the error.

## 3. Common mistakes
- Forgetting `return` (`error: missing return statement`), or writing `return` in a `void` method with a value.
- Calling `greet` without the parentheses, or with the wrong number or type of arguments (`error: method greet in class ... cannot be applied to given types`).
- Putting the `return` inside a loop and then being surprised it stops on the first round.
- Code after `return` never runs (`error: unreachable statement`).
- Printing inside a method that is meant to *calculate* something.
- Recursion without a base case, or a base case that is never reached.
- Thinking a method can change a caller's `int`: it only changes its own copy.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Greeting overloads, total with tax overloads, varargs average |
| L2-1 … L2-4 | 🟡 Intermediate | Profile line from a map, several return values in an array, Fibonacci (recursion), raise prices inside an array |
| L3-1, L3-2 | 🔴 Challenge | Flatten nested lists (recursion), add an item without touching the original list |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Write three example calls and their expected results on paper first. Then write the method so that the first call works, then the others.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Overloads: the short versions just call the longest one with the missing values (<code>greet(name, "Hello")</code>, <code>calcTotal(price, 1, 18)</code>). Rounding: <code>Math.round(x * 100) / 100.0</code>. Varargs: <code>numbers.length</code> and an enhanced <code>for</code>; remember the empty case. Profile: <code>new TreeMap&lt;&gt;(fields)</code>, one <code>key + "=" + value</code> per entry, then <code>String.join("; ", parts)</code>. minMaxAvg: loop once keeping <code>min</code>, <code>max</code>, <code>sum</code>; return <code>new double[]{min, max, average}</code>. fib: base case <code>n &lt; 2</code> returns <code>n</code>, otherwise the sum of the two previous calls. raisePrices: <code>prices[i] += extra</code> in a classic loop. flatten: loop over the items; if <code>item instanceof List&lt;?&gt; inner</code> then <code>flat.addAll(flatten(inner))</code>, else <code>flat.add((Integer) item)</code>. withItem: <code>new ArrayList&lt;&gt;(items)</code>, add, return the new list.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day11_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day11_answers.md`
1. What is the difference between a parameter and an argument?
2. What does `void` mean, and what happens if you write `int x = printLine("a");` for a `void` method?
3. Java has no default parameter values. How do you make `qty` optional for `total(price, qty)`?
4. In `static double average(int... numbers)`, what type is `numbers` inside the method, and what does `average()` give?
5. What is a base case in recursion, and what happens without one?
6. `static void change(int x) { x = 10; }` and `int a = 5; change(a);` What is `a` afterwards? What if the parameter were an `int[]` and the method did `arr[0] = 10;`?
7. Why is `static int f(int a) { }` a compile error?
8. Why is it better to `return` a result than to `println` it inside a calculation method?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: lambdas and streams: pass a *method* as an argument and filter, transform and sort data in one pipeline.
