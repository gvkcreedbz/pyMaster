# Day 08 — Arrays (many values of the same type in one box)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Store, read, change, search, sort and loop over a fixed-size collection of values with arrays | Beginner+ |

## 🌍 Real-world scenario & trend
**A shopping cart, a game leaderboard, a week of sales.** Anything "many of the same kind" is a row of values: cart prices, 10,000 sensor readings, today's marks of a whole class. A table of rows and columns (shops × days) is simply a row of rows.

**Why Java?** Arrays are the oldest and fastest collection in Java. Image pixels, audio samples, game boards and the `args` that reach `main` are all arrays. Bigger helpers such as `ArrayList` (tomorrow) are built on top of them, so understanding arrays makes everything after Day 8 easier. *Coming from Python?* A Java array is like a Python list with three differences: **one type only**, a **fixed length**, and **no negative indexes**.

## 0. Warm-up (5 min) — Day 07 recap
- Which loop keeps a menu running until the user chooses "Exit"?  • Why do we compare text with `.equals` and never with `==`?

## 1. Concepts (with tiny code)

### 1.1 Create, index and length
An array has **one element type** and a **length that is fixed when you create it**. Positions (indexes) start at 0.
```java
String[] cart = {"milk", "bread", "eggs"};      // create with values
System.out.println(cart[0]);                    // milk
System.out.println(cart.length);                // 3   (no brackets: length is a field, not a method)
System.out.println(cart[cart.length - 1]);      // eggs  (the last item; there is NO cart[-1] in Java)

int[] marks = new int[5];                       // five slots, all start as 0
String[] names = new String[2];                 // two slots, both start as null (= "nothing here yet")
```
Default values: `0` for numbers, `0.0` for decimals, `false` for booleans, `null` for text and other objects.

### 1.2 Change items, but not the length
```java
cart[1] = "brown bread";                              // replacing is fine
String[] bigger = Arrays.copyOf(cart, cart.length + 1);   // a NEW array, one slot longer
bigger[3] = "butter";                                 // the extra slot started as null
```
To "add" or "remove" you build a new array. (`ArrayList` on Day 9 does this for you.) `Arrays` lives in `java.util`, so write `import java.util.Arrays;` at the top of the file.

### 1.3 Two ways to loop
```java
double[] prices = {49.5, 30, 120};
for (int i = 0; i < prices.length; i++) {       // classic: you need the position
    System.out.println((i + 1) + ". Rs. " + prices[i]);
}
double total = 0;
for (double price : prices) {                   // enhanced: just the items, read "for each price in prices"
    total += price;
}
```
Use the classic loop when you need `i` (to print numbers, to change `prices[i]`, to walk two arrays together). Otherwise the enhanced loop is shorter and safer.

### 1.4 The `Arrays` toolbox
```java
int[] scores = {72, 95, 88, 60};
System.out.println(Arrays.toString(scores));        // [72, 95, 88, 60]  (println(scores) alone prints junk like [I@1b6d3586)
int[] sorted = Arrays.copyOf(scores, scores.length);
Arrays.sort(sorted);                                // sorts IN PLACE, returns nothing (like Python's list.sort())
System.out.println(Arrays.toString(sorted));        // [60, 72, 88, 95]
System.out.println(Arrays.binarySearch(sorted, 88)); // 2  (fast search, only on a SORTED array)
System.out.println(Arrays.equals(scores, new int[]{72, 95, 88, 60}));   // true (same content)
int[] sevens = new int[3];
Arrays.fill(sevens, 7);                             // every slot becomes 7 -> [7, 7, 7]
int[] middle = Arrays.copyOfRange(scores, 1, 3);    // {95, 88}  (from index 1 up to, not including, 3)
System.out.println(Arrays.deepToString(new int[][]{{1, 2}, {3, 4}}));   // [[1, 2], [3, 4]]
```
Min and max have no ready-made method on a plain array: loop and keep the best so far, or sort a copy and take the ends.

### 1.5 The copy trap (very common bug)
```java
int[] a = {1, 2, 3};
int[] b = a;            // NOT a copy: b is a second NAME for the same array
b[0] = 99;
System.out.println(Arrays.toString(a));   // [99, 2, 3]  <- surprise
int[] c = a.clone();    // a real copy (or Arrays.copyOf(a, a.length))
```
For the same reason `a == c` asks "is it the very same array?", not "same content?". Use `Arrays.equals(a, c)` for content. *Python twin:* exactly the `b = a` trap of lists.

### 1.6 Tables: arrays of arrays
```java
int[][] sales = {
        {120, 80, 150},      // shop 0: Mon, Tue, Wed
        {90, 100, 60}        // shop 1
};
System.out.println(sales[1][1]);        // 100  (row first, then column)
for (int[] row : sales) {               // each row is itself an int[]
    int rowTotal = 0;
    for (int amount : row) {
        rowTotal += amount;
    }
    System.out.println(Arrays.toString(row) + " -> " + rowTotal);
}
```
`sales.length` is the number of rows, `sales[0].length` the number of columns.

### 1.7 Out of bounds is a runtime error
```java
int[] scores = {72, 95, 88, 60};
System.out.println(scores[4]);   // ArrayIndexOutOfBoundsException: Index 4 out of bounds for length 4
```
The valid positions are `0` to `length - 1`. The error message tells you which index you used and the length.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button. Try making the cart longer, or add a third shop to the sales table.

## 3. Common mistakes
- Writing `cart.length()` (that is for `String`) or `name.length` (that is for arrays). Arrays: `.length`, no brackets.
- Looping with `i <= arr.length` instead of `i < arr.length` (one step too far: `ArrayIndexOutOfBoundsException`).
- `int[] b = a;` and believing `b` is a copy.
- Printing an array with `System.out.println(arr)`: use `Arrays.toString(arr)`.
- Comparing arrays with `==` or `.equals`: use `Arrays.equals(a, b)`.
- Sorting the original array when you still need the old order: sort a copy.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Cart total, find an item's position, top two scores |
| L2-1 … L2-4 | 🟡 Intermediate | Remove all copies of a value, running totals, judges' trimmed average, totals per day in a sales table |
| L3-1, L3-2 | 🔴 Challenge | Rotate an array, merge two sorted arrays |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.
*(Each task is a `static` method. You will learn how methods work on Day 11; for now fill in the body and keep the first line as it is.)*

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Try your idea on a 4-item example on paper and write down the array after every step. Remember: you cannot change the length, so "remove" means "create a smaller array and fill it".
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
cartTotal: a <code>total</code> variable and an enhanced <code>for</code>. indexOf: classic loop, <code>items[i].equals(target)</code>, <code>return i</code>; after the loop <code>return -1</code>. topTwo: <code>Arrays.copyOf</code>, <code>Arrays.sort</code>, then the last two items. removeAll: count the keepers, <code>new int[count]</code>, fill with a second variable <code>next</code>. runningTotals: keep <code>total += numbers[i]</code> and store it in <code>result[i]</code>. trimmedAverage: sort a copy, add up positions <code>1</code> to <code>length - 2</code>, divide as a <code>double</code>. columnTotals: <code>totals[day] += row[day]</code> inside two loops. rotate: <code>result[(i + k) % n] = items[i]</code>. mergeSorted: two index variables <code>i</code> and <code>j</code>, copy the smaller item each round, then copy what is left.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day08_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day08_answers.md`
1. `int[] a = {1, 2, 3}; int[] b = a; b[0] = 99;` What does `Arrays.toString(a)` show?
2. What values does `new int[3]` hold? What does `new String[2]` hold?
3. How do you read the last item of an array called `cart`? What happens with `cart[-1]`?
4. What is the difference between `cart.length` and `name.length()`?
5. `int[] n = {3, 1, 2}; Arrays.sort(n);` What does `n` contain afterwards, and what does `sort` return?
6. Why is `System.out.println(scores)` a bad way to look at an `int[]`, and what should you use?
7. For `int[][] t = {{1, 2}, {3, 4}};` what are `t[1][0]` and `t.length`?
8. An array has 3 slots and you need room for a 4th item. What do you do?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: `ArrayList`, `List.of`, `HashSet` and `TreeSet`: collections that grow, plus unique visitors and mutual friends.
