# 🧭 How to Get Unstuck (a routine, not a feeling)

Being stuck is **normal** — professionals are stuck daily. What differs is the *routine*. Use this in order and **time-box** every step.

## The 10-10-10 rule
| Minutes stuck | Do this |
|---|---|
| **0–10** | Re-read the task *slowly*. Re-read the lesson section it mentions. Compare the expected output with yours **character by character** (spaces, `%n`, decimals). |
| **10–20** | Make it smaller: print values, test with the simplest input, comment out half the code. Read the **hint (level 2)** in `LESSON.md`. |
| **20–30** | Explain the problem out loud (rubber duck 🦆) or write it in the Bug Journal. Take a **5-minute walk**. Then use hint 3: read **one** task in `solutions/dayNN_Solution.java`, close it, rewrite it from memory. |
| **30+** | Park it. Mark the exercise "Attempted" in the tracker and move on. Return tomorrow during warm-up — it often solves itself. |

## 1. Read the error properly
- **Compile error (`javac`)**: the **first** error first (the rest are often side effects), the `File.java:LINE` next, then the `^` under the code. Often the real mistake is on the line *before* (a missing `;` or `)`).
- **Runtime exception**: the **first line** of the stack trace is *what* (`NullPointerException: ...`); the first `at ...` line that names **your** file is *where*.
Decode both with `error_decoder.md`. Never "just retry" — nothing changes without a new idea.

## 2. Make the program talk
```java
System.out.println("DEBUG total = [" + total + "] " + ((Object) total).getClass().getSimpleName());
System.out.println("DEBUG items = " + java.util.Arrays.toString(items));   // arrays need Arrays.toString
```
The square brackets reveal hidden spaces. Print *before* the failing line, not after. Check: Is it the value I think? Is it `null`? Is it empty? Is the loop running at all?

## 3. Shrink the problem (minimal example)
Paste the failing method into **`jshell`** (or a scratch file `Scratch.java`), hard-code a tiny input and delete everything unrelated. Half the time the bug is revealed while shrinking.

## 4. Check your assumptions
- "This array has 3 items" → `System.out.println(arr.length)` (arrays: `.length`, lists: `.size()`, strings: `.length()`)
- "This is a number" → `scanner.nextLine()` returns **text**; convert with `Integer.parseInt(...)`
- "These strings are equal" → `==` compares *references*; use `a.equals(b)`
- "This file exists" → `System.out.println(Files.exists(path) + " " + Path.of("").toAbsolutePath());`
- "This method is called" → put `System.out.println("called")` inside it
- "This variable is not null" → `System.out.println(x == null)`

## 5. Use the debugger (Day 17)
Click left of a line number in Cursor to set a **breakpoint**, press F5 (or *Debug* above `main`), and inspect variables as the code runs. Slower to learn, faster for hard bugs. The portal's **👁 Visualizer** draws the same stack and heap for small snippets.

## 6. Ask well (humans, forums, or an AI assistant)
A great question contains:
1. **Goal** — what should the code do?
2. **Code** — the *smallest* snippet that reproduces the problem (as text, not a screenshot).
3. **Full error** — the whole compiler message or stack trace, copied.
4. **Expected vs actual** output.
5. **What you already tried** (and your `java -version`).

### Using AI the learning-friendly way
✅ "Here is my code and error. *Explain why* this fails, but don't give me the corrected code yet."
✅ "Review my solution: what edge cases did I miss? Which part is hardest to read?"
✅ "Give me 3 similar practice problems of increasing difficulty."
✅ "Explain this stack trace line by line."
❌ Pasting the task and copying the answer — you'll feel productive and learn nothing (and the final exam is closed-book).
⚠️ AI can be confidently wrong (it also loves to invent methods that do not exist in Java). Always **compile and run** its suggestion and let **tests** be your judge (Day 24 skills!).

## 7. Prevent being stuck
- Compile and run after **every 3–5 lines**. A short compile error is far easier than a long one.
- Write the method's *signature and a one-line comment* first, return a placeholder, check it compiles, then fill in the body.
- Let the IDE help: red squiggles, **Ctrl+.** quick fixes, **Shift+Alt+F** to format (a wrongly indented block often means a missing brace).
- Keep a **Bug Journal**: each bug you log is one you'll never debug twice.
- Sleep. Seriously — memory consolidates overnight; a stuck problem at 11 pm is easy at 8 am.

## 8. Java-specific "it can't be that" checklist
| Symptom | Check |
|---|---|
| "My `if` on text never matches" | `==` vs `.equals()`; case (`equalsIgnoreCase`); extra spaces (`trim()` / `strip()`) |
| "Maths is wrong" | `int / int` is a whole-number division (`7 / 2 == 3`); cast first: `(double) a / b`; money → `BigDecimal` |
| "Scanner skipped my input" | after `nextInt()` the Enter key is still waiting: add `scanner.nextLine();` or read lines and parse |
| "The loop is off by one" | `<` vs `<=`; arrays start at `0` and end at `length - 1` |
| "My list changed by itself" | two names, one object: copy with `new ArrayList<>(list)`; `List.of(...)` is read-only |
| "File not found but it is right there" | working directory: run from the day folder; print `Path.of("").toAbsolutePath()` |
| "Works in the editor, not in the terminal" | different JDK: `java -version` in both |

## 9. Emotional first-aid
| Thought | Reality |
|---|---|
| "Everyone else gets this instantly." | You see their results, not their 40 failed attempts. |
| "Java is so verbose and strict!" | The compiler is a free reviewer — it catches whole classes of bugs before you run anything. |
| "I should know this by now." | Confusion at the *edge* of your skill means you're learning. |
| "I deleted/broke everything." | Use Git (Day 24) — and until then, copy the file before big edits. |
| "I'm behind." | Use the catch-up protocol in `00_GAME_PLAN.md`. A 60-minute day beats a skipped day. |
