# Day 09 — Lists & Sets (collections that grow, and collections without repeats)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Use `ArrayList` for changing lists, `List.of` for fixed ones, and `HashSet`/`TreeSet` for uniqueness and "who is in both?" questions | Beginner+ |

## 🌍 Real-world scenario & trend
**Instagram "mutual friends" and "unique visitors".** A shopping cart grows and shrinks as you shop (a list). Counting *unique* users per day, finding the followers you share with someone, and de-duplicating tags are all set questions. Checking `set.contains(x)` stays almost instant even with millions of items, which is why back-end teams reach for sets first.

**Why Java?** Yesterday's arrays cannot grow. Java's *Collections Framework* (`ArrayList`, `HashSet`, `TreeSet`, ...) is the everyday toolbox of every Java back end. *Coming from Python?* `ArrayList` is a Python `list`, `HashSet` is a `set`, and `List.of(...)` is the closest thing to a tuple (a list that cannot change). The big difference: the type of the items goes in angle brackets, `List<String>`, and lists cannot hold plain `int`, only the object version `Integer`.

## 0. Warm-up (5 min) — Day 08 recap
- How do you make a real copy of an array?  • What does `Arrays.sort(arr)` return?

## 1. Concepts (with tiny code)

### 1.1 `ArrayList`: an array that grows
```java
import java.util.ArrayList;
import java.util.List;

List<String> cart = new ArrayList<>();      // empty list of text; <> lets Java fill in the type
cart.add("milk");                           // add at the end
cart.add("bread");
cart.add(0, "tea");                         // insert at position 0
System.out.println(cart);                   // [tea, milk, bread]  (println shows a list nicely)
System.out.println(cart.get(1));            // milk    (cart[1] does NOT work on lists)
System.out.println(cart.size());            // 3       (size(), not length)
cart.set(1, "oat milk");                    // replace position 1
cart.remove("bread");                       // remove by value
cart.remove(0);                             // remove by position
System.out.println(cart.contains("oat milk") + " " + cart.indexOf("oat milk"));   // true 0
for (String item : cart) {                  // the enhanced for loop works here too
    System.out.println(item);
}
```
Write the variable's type as the interface `List<String>` and create the real thing with `new ArrayList<>()`. This is the habit of Java developers.

### 1.2 `List.of`: a list that cannot change
```java
List<String> weekdays = List.of("Mon", "Tue", "Wed");
// weekdays.add("Thu");    -> UnsupportedOperationException at run time
List<String> changeable = new ArrayList<>(weekdays);    // copy it into an ArrayList when you need changes
```
Use `List.of` for fixed data (menu, weekdays, test data). Like a Python tuple, it is safe to share because nobody can change it.

### 1.3 Wrapper types: `int` becomes `Integer`
Collections hold *objects*, so a list of whole numbers is `List<Integer>`. Java converts for you (this is called *autoboxing*).
```java
List<Integer> marks = new ArrayList<>();
marks.add(72);                       // int -> Integer
int first = marks.get(0);            // Integer -> int
```
Other pairs: `double` → `Double`, `boolean` → `Boolean`, `char` → `Character`, `long` → `Long`. Two traps:
```java
marks.add(95); marks.add(60);
marks.remove(1);                       // an int: removes the item AT POSITION 1  -> [72, 60]
marks.remove(Integer.valueOf(60));     // an Integer: removes the VALUE 60       -> [72]

Integer a = 1000, b = 1000;
System.out.println(a == b);            // false! == compares objects (for numbers above 127)
System.out.println(a.equals(b));       // true  <- always compare wrappers with equals
```

### 1.4 `Collections`: a helper class for lists
```java
List<Integer> scores = new ArrayList<>(List.of(72, 95, 88, 60, 95));
Collections.max(scores);               // 95
Collections.min(scores);               // 60
Collections.frequency(scores, 95);     // 2
Collections.sort(scores);              // [60, 72, 88, 95, 95]  sorts IN PLACE
Collections.reverse(scores);           // [95, 95, 88, 72, 60]
Collections.swap(scores, 0, 4);        // swap two positions, no temp variable needed
```
(`Collections` with an **s** is the helper; `Collection` is a type. Same family as `Arrays` for arrays.)

### 1.5 `HashSet`: unique items, very fast lookups
```java
Set<String> visitors = new HashSet<>(List.of("aarav", "diya", "kabir"));
visitors.add("aarav");                       // false: already there, nothing changes
visitors.add("zoya");                        // true: new
visitors.remove("kabir");
System.out.println(visitors.contains("diya"));   // true, and fast
System.out.println(visitors.size());             // 3
```
A `HashSet` has **no positions** (`get(0)` does not exist) and **no promised order**: never rely on the order it prints. Put a list into a set to count the different items: `new HashSet<>(list).size()`.

### 1.6 `TreeSet`: unique *and* sorted
```java
Set<String> sortedNames = new TreeSet<>(visitors);
System.out.println(sortedNames);            // [aarav, diya, zoya]  alphabetical
```
`TreeSet` is a little slower than `HashSet` but always keeps A-Z (or smallest-first for numbers). Need uniqueness *and* the order you added things? Use `LinkedHashSet`.

### 1.7 Set maths (Venn diagrams)
```java
Set<String> mine = new TreeSet<>(List.of("A", "B", "C"));
Set<String> hers = Set.of("B", "C", "D");

Set<String> both = new TreeSet<>(mine);  both.retainAll(hers);    // intersection [B, C]  (mutual friends)
Set<String> all  = new TreeSet<>(mine);  all.addAll(hers);        // union        [A, B, C, D]
Set<String> only = new TreeSet<>(mine);  only.removeAll(hers);    // difference   [A]     (only mine)
```
Notice the **copy first** (`new TreeSet<>(mine)`): `retainAll`, `addAll` and `removeAll` change the set they are called on.

### 1.8 Remove repeats but keep the order
`set.add(x)` returns `true` only the first time. That is the whole trick:
```java
Set<String> seen = new HashSet<>();
List<String> result = new ArrayList<>();
for (String tag : tags) {
    if (seen.add(tag)) {          // true = first time we see it
        result.add(tag);
    }
}
```

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section, run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button. Try adding yourself to the visitors and see what the set prints.

## 3. Common mistakes
- `int[]`-style `cart[0]` on a list: use `cart.get(0)`. And `size()` for lists, `length` for arrays.
- `List<int>`: not allowed, write `List<Integer>`.
- `marks.remove(1)` when you meant "remove the value 1": use `remove(Integer.valueOf(1))`.
- Comparing `Integer` objects with `==`. Use `.equals(...)`.
- Changing a `List.of(...)` list: `UnsupportedOperationException`. Copy it into `new ArrayList<>(...)` first.
- Expecting a `HashSet` to keep your order or to have `get(0)`.
- Forgetting `import java.util.*;` (or the single imports) at the top of the file.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Count unique numbers, swap the first and last item, min and max |
| L2-1 … L2-4 | 🟡 Intermediate | Mutual followers, friend suggestions, de-duplicate keeping order, remove a value (not a position) |
| L3-1, L3-2 | 🔴 Challenge | First duplicate, "two numbers that add up to a target" in one pass |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Draw two circles (a Venn diagram), shade the region you need, then pick the set method: <code>retainAll</code> (shared), <code>addAll</code> (everything), <code>removeAll</code> (only one side).
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
uniqueCount: <code>new HashSet&lt;&gt;(items).size()</code>. swapEnds: keep <code>items.get(0)</code> in a temp variable, then two <code>set(...)</code> calls. minMax: <code>List.of(Collections.min(x), Collections.max(x))</code>. commonFollowers: <code>TreeSet</code> of a, <code>retainAll</code> b, then <code>new ArrayList&lt;&gt;(set)</code>. suggestFriends: <code>TreeSet</code> of the friends-of-friends, <code>removeAll(myFriends)</code>, <code>remove(me)</code>. dedupe: the <code>seen</code> pattern from 1.8. removeValue: <code>items.remove(Integer.valueOf(value))</code>. firstDuplicate: <code>if (!seen.add(x)) return x;</code>, and <code>return null;</code> after the loop. hasPairWithSum: for each <code>n</code> ask <code>seen.contains(target - n)</code> before adding <code>n</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day09_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day09_answers.md`
1. How do you create an empty list of text and add `"milk"` to it? How do you read the first item?
2. What happens if you call `add` on a list made with `List.of(...)`? How do you get a changeable copy?
3. Why can't you write `List<int>`? What do you write?
4. `List<Integer> n = new ArrayList<>(List.of(5, 1, 7));` What are `n.remove(1)` and `n.remove(Integer.valueOf(1))` doing, and what is `n` after both?
5. `Set<Integer> s = new HashSet<>(List.of(1, 1, 2, 2, 3)); s.size()` gives what? Does `s.get(0)` work?
6. What is the difference between `HashSet` and `TreeSet`?
7. `Set<String> a = new TreeSet<>(List.of("A", "B", "C")); a.retainAll(Set.of("B", "C", "D"));` What is `a` now?
8. Why should you compare two `Integer` objects with `.equals` and not `==`?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: `HashMap`, `TreeMap` and `LinkedHashMap`: contact books, inventory and word counts.
