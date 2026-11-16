# 🧭 How to Get Unstuck (a routine, not a feeling)

Being stuck is **normal** — professionals are stuck daily. What differs is the *routine*. Use this in order and **time-box** every step.

## The 10-10-10 rule
| Minutes stuck | Do this |
|---|---|
| **0–10** | Re-read the task *slowly*. Re-read the lesson section it mentions. Compare the expected output with yours **character by character**. |
| **10–20** | Make it smaller: print values, test with the simplest input, comment out half the code. Read the **hint (level 2)** in `LESSON.md`. |
| **20–30** | Explain the problem out loud (rubber duck 🦆) or write it in the Bug Journal. Take a **5-minute walk**. Then use hint 3: read **one** task in the solution, close it, rewrite it from memory. |
| **30+** | Park it. Mark the exercise "Attempted" in the tracker and move on. Return tomorrow during warm-up — it often solves itself. |

## 1. Read the error properly
Last line first (what), line number next (where). Decode it with `error_decoder.md`. Never "just retry" — nothing changes without a new idea.

## 2. Make the program talk
```python
print("DEBUG total =", repr(total), type(total))   # repr shows quotes/spaces that hide bugs
```
Print *before* the failing line, not after. Check: Is it the type I think? Is it empty? Is the loop running at all?

## 3. Shrink the problem (minimal example)
Copy the failing function into a scratch file, hard-code a tiny input, and delete everything unrelated. Half the time the bug is revealed while shrinking.

## 4. Check your assumptions
- "This list has 3 items" → `print(len(x))`
- "This is a number" → `print(type(x))` (`input()` returns **text**)
- "This file exists" → `print(Path(path).exists(), Path.cwd())`
- "This function is called" → put a `print("called")` inside it

## 5. Use the debugger (Day 17)
Click left of a line number in Cursor to set a **breakpoint**, press F5, and inspect variables as the code runs. Slower to learn, faster for hard bugs.

## 6. Ask well (humans, forums, or an AI assistant)
A great question contains:
1. **Goal** — what should the code do?
2. **Code** — the *smallest* snippet that reproduces the problem (as text, not a screenshot).
3. **Full error** — the whole traceback, copied.
4. **Expected vs actual** output.
5. **What you already tried.**

### Using AI the learning-friendly way
✅ "Here is my code and error. *Explain why* this fails, but don't give me the corrected code yet."
✅ "Review my solution: what edge cases did I miss? Which part is hardest to read?"
✅ "Give me 3 similar practice problems of increasing difficulty."
✅ "Explain this traceback line by line."
❌ Pasting the task and copying the answer — you'll feel productive and learn nothing (and the final exam is closed-book).
⚠️ AI can be confidently wrong. Always **run** its suggestion and **tests** are your judge (Day 24 skills!).

## 7. Prevent being stuck
- Run code after **every 3–5 lines**.
- Write the function's *signature and a one-line docstring* first, then the body.
- Keep a **Bug Journal**: each bug you log is one you'll never debug twice.
- Sleep. Seriously — memory consolidates overnight; a stuck problem at 11 pm is easy at 8 am.

## 8. Emotional first-aid
| Thought | Reality |
|---|---|
| "Everyone else gets this instantly." | You see their results, not their 40 failed attempts. |
| "I should know this by now." | Confusion at the *edge* of your skill means you're learning. |
| "I deleted/broke everything." | Use Git (Day 24) — and until then, copy the file before big edits. |
| "I'm behind." | Use the catch-up protocol in `00_GAME_PLAN.md`. A 60-minute day beats a skipped day. |
