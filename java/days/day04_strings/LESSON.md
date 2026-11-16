# Day 04 — Strings (Text Processing)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Cut, search, clean and build text with `String` and `StringBuilder`: the skill behind usernames, search boxes, hashtags and data cleaning | Beginner |

## 🌍 Real-world scenario & trend
**Instagram signup + caption tools.** When you sign up, the app trims spaces, lowercases your email, checks it has an `@`, suggests a username, and extracts #hashtags from captions. Every one of those steps is a `String` method.

**Why Java?** Banks, airlines and e-commerce back-ends spend much of their time reading and writing text: names, addresses, CSV rows, JSON, log lines. **Trend:** AI and LLM apps are text-in/text-out too, so cleaning and slicing text is the first step of almost every data and AI pipeline.

## 0. Warm-up (5 min) — Day 03 recap
- What are `17 / 5` and `17 % 5`? What does `Math.ceil(4.1)` return?
- What does `&&` mean?

## 1. Concepts (with tiny code)

### 1.1 Strings are sequences of characters: indexing starts at 0
```java
String word = "PYTHON";
//             P  Y  T  H  O  N
//             0  1  2  3  4  5       (index)
word.charAt(0)               // 'P'
word.charAt(word.length() - 1)   // 'N'   (last letter: length - 1)
word.length()                // 6      (a method: needs the brackets)
```
*Different from Python:* there is no `word[0]` and no negative index. `charAt(10)` crashes with `StringIndexOutOfBoundsException`. Also `'P'` (single quotes) is one `char`; `"P"` (double quotes) is a `String`.

### 1.2 Cutting out pieces with `substring` (the end is NOT included)
```java
word.substring(0, 3)     // "PYT"     (index 0, 1, 2)
word.substring(3)        // "HON"     (from index 3 to the end)
word.substring(1, 4)     // "YTH"
```
There is no `[::-1]` slice. To reverse, use a `StringBuilder` (see 1.7).

### 1.3 Strings are immutable (they cannot be changed in place)
Every method returns a **new** String. `word.toUpperCase();` on its own does nothing useful: save the result.
```java
String s = "Java";
s.toUpperCase();        // result thrown away, s is still "Java"
s = s.toUpperCase();    // now s is "JAVA"
```

### 1.4 The methods you will use every week
```java
String s = "  Learning Java is Fun!  ";
s.strip()                    // "Learning Java is Fun!"   (removes outer spaces; trim() is the old name)
s.toLowerCase()   s.toUpperCase()
s.replace("Fun", "Great")    // replaces every match
s.indexOf("Java")            // index of the first match, or -1 if missing
s.contains("Java")           // true      s.startsWith("  L")  s.endsWith("!  ")
s.isEmpty()                  // true only for ""      s.isBlank()  // true for "" and "   "
"ab".repeat(3)               // "ababab"
```
There is no `title()` or `capitalize()`. Build it: `w.substring(0, 1).toUpperCase() + w.substring(1).toLowerCase()`.

### 1.5 `split` and `join`: text ↔ words
```java
String[] words = "red green blue".split(" ");     // a row of three Strings
System.out.println(words[0]);                     // red   (words[0] = the first one)
System.out.println(words.length);                 // 3
String again = String.join("-", "2026", "11", "16");    // "2026-11-16"
```
`String[]` is an *array* (a numbered row of items). You only need `words[0]`, `words[1]` and `.length` today. Arrays get their full lesson on Day 8.
To split on **any amount of spaces** (and clean messy input) use `text.strip().split("\\s+")`. Treat `"\\s+"` as a magic word for now (patterns are explained on Day 23). `String.join(" ", array)` glues an array back together.

### 1.6 Comparing text: `equals`, not `==`
```java
String typed = new String("yes");        // a brand-new text object, like a user typing it
System.out.println(typed == "yes");      // false  <- == asks "is it the very same object?"
System.out.println(typed.equals("yes")); // true   <- equals asks "are the letters the same?"
System.out.println("Yes".equalsIgnoreCase("YES"));    // true
System.out.println("apple".compareTo("banana") < 0);  // true  (alphabetical order)
```
**Always compare Strings with `.equals(...)`.** (`==` is for numbers.) *Different from Python:* in Python `==` works on text, in Java it does not.

### 1.7 `StringBuilder`: build text step by step
Gluing with `+` over and over makes many throw-away Strings. A `StringBuilder` is a text you *can* change.
```java
StringBuilder sb = new StringBuilder();
sb.append("Chai").append(", ").append("Samosa");   // chain the calls
sb.insert(0, "Order: ");
System.out.println(sb);                            // Order: Chai, Samosa
String result = sb.toString();                     // turn it back into a String
String backwards = new StringBuilder("PYTHON").reverse().toString();   // "NOHTYP"
```

### 1.8 Formatting, text blocks and escapes
```java
String.format("%-10s|%6.2f|%5d", "Chai", 20.5, 3)   // "Chai      | 20.50|    3"
String.format("%02d", 5)                            // "05"  (pad with zeros)
String msg = """
        Dear %s,
        Your OTP is %d.
        """.formatted("Aarav", 4821);                // a multi-line text block
System.out.println("She said \"hi\" and C:\\new");   // She said "hi" and C:\new
```
`%s` is text, `%d` a whole number, `%.2f` a decimal, `%-10s` pads text to 10 characters, `\"` is a quote, `\\` is one backslash.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) each section (a signup-form cleaner), run it, then change values and re-run.
Run it with: `java Examples.java` (inside this folder) or the ▶ Run button.

## 3. Common mistakes
- Comparing Strings with `==`. Use `.equals(...)`.
- Forgetting that methods return new Strings (`name.strip();` alone does nothing).
- Off-by-one: `word.substring(0, 3)` has 3 characters and stops *before* index 3.
- `word.charAt(10)` or `substring(2, 20)` on a short text: `StringIndexOutOfBoundsException`.
- Mixing `'A'` (a `char`) and `"A"` (a `String`).
- `"a b".split(" ")` splits at every single space, so double spaces give empty pieces. Use `split("\\s+")` after `strip()`.

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | First name, initials, shout |
| L2-1 … L2-4 | 🟡 Intermediate | Username generator, email validator, capitalise a word, message cleaner |
| L3-1, L3-2 | 🔴 Challenge | CamelCase hashtag (3 words), palindrome checker |

Run `java Practice.java`: the auto-checker prints `[PASS]` / `[FAIL]` for every task. There is no `if` yet (Day 5): use `&&` inside one `return`.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Try the idea in <code>jshell</code> (type lines one at a time) before writing the method. Say in words what each step does to the text.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
Initials: <code>String[] parts = name.strip().split("\\s+");</code> then <code>parts[0].substring(0, 1)</code>. Username: <code>toLowerCase()</code>, <code>replace(" ", ".")</code>, <code>String.format("%02d", year % 100)</code>. Email: <code>indexOf("@")</code> must be &gt; 0 and equal <code>lastIndexOf("@")</code>, no <code>contains(" ")</code>, and the part after the @ <code>contains(".")</code> but does not <code>endsWith(".")</code>. Hashtag: remove punctuation with <code>replace</code>, <code>split("\\s+")</code>, capitalise each of the three words, join with <code>+</code>. Palindrome: lower-case, remove spaces, compare with the <code>StringBuilder(...).reverse().toString()</code> using <code>equals</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day04_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day04_answers.md`
1. For `String s = "PYTHON";` what are `s.charAt(1)`, `s.substring(1, 4)`, `s.substring(3)` and `s.length()`?
2. What does `"  hi  ".strip()` return? Does it change the original variable?
3. Why can you not write `s[0] = 'J';` or `s.charAt(0) = 'J';`? How do you get "JYTHON"?
4. What does `"a,b,c".split(",")` return, and what is its `.length`?
5. What does `String.join("-", "2026", "11", "16")` return?
6. What does `"hello world".indexOf("z")` return?
7. Is `"Apple".equals("apple")` true? How do you compare them ignoring case? Why is `==` the wrong tool?
8. What is the difference between `String` and `StringBuilder`, and how do you reverse a text?

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: decisions with `if / else` and `switch`: delivery-fee rules and ATM logic.
