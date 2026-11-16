# Day 04 — Strings (Text Processing)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Slice, search, clean and transform text — the skill behind usernames, search boxes, hashtags and data cleaning | Beginner |

## 🌍 Real-world scenario & trend
**Instagram signup + caption tools.** When you sign up, the app trims spaces, lowercases your email, checks it has an `@`, suggests a username, and extracts #hashtags from captions. **Trend:** LLM/AI apps are text-in/text-out — cleaning and slicing text is the first step of almost every data and AI pipeline.

## 0. Warm-up (5 min) — Day 03 recap
- `17 // 5`, `17 % 5`?  • What does `math.ceil(4.1)` return?

## 1. Concepts

### 1.1 Strings are sequences of characters — indexing starts at 0
```python
word = "PYTHON"
#       P  Y  T  H  O  N
#       0  1  2  3  4  5       positive index
#      -6 -5 -4 -3 -2 -1       negative index (from the end)
word[0]      # 'P'      word[-1]  # 'N'      len(word) # 6
```

### 1.2 Slicing `[start:stop:step]` (stop is NOT included)
```python
word[0:3]    # 'PYT'     word[:3]  # 'PYT'     word[3:]  # 'HON'
word[::2]    # 'PTO'     word[::-1]# 'NOHTYP'  (reversed!)
```

### 1.3 Strings are immutable (cannot be changed in place)
`word[0] = "J"` → `TypeError`. Create a new string instead: `"J" + word[1:]`.

### 1.4 The methods you will use every week
```python
s = "  Learning Python is Fun!  "
s.strip()            # 'Learning Python is Fun!'   (removes outer spaces)
s.lower() / s.upper() / s.title() / s.capitalize()
s.replace("Fun", "Great")
s.split()            # ['Learning', 'Python', 'is', 'Fun!']   (text -> list of words)
"-".join(["a", "b"]) # 'a-b'                        (list -> text)
s.find("Python")     # index, or -1 if missing      s.count("n")
s.startswith("  L")  # True                         s.endswith("!")
"123".isdigit()      # True    "abc".isalpha() # True
```
Methods **return a new string** — `s.upper()` alone doesn't change `s`; write `s = s.upper()`.

### 1.5 `in` operator & comparison
```python
"@" in "me@mail.com"      # True
"apple" < "banana"        # True (alphabetical)
"a" == "A"                # False -> compare with .lower() for case-insensitive
```

### 1.6 Multi-line strings and escapes
```python
msg = """Dear user,
Your OTP is 4821."""
print("She said \"hi\"")      # escape quotes
print(r"C:\new\table")        # r"" = raw string, backslashes kept as-is
```

## 2. Code along → `examples.py` (signup form cleaner)

## 3. Common mistakes
- Forgetting that methods don't modify the original (`name.strip()` without saving).
- Off-by-one: `word[0:3]` has 3 characters, stops *before* index 3.
- `word[10]` → `IndexError` (index out of range).
- Mixing `split()` (no argument = split on any whitespace, ignoring extra spaces) and `split(" ")` (splits on every single space).

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | First name, initials, shout |
| L2-1…L2-3 | 🟡 | Username generator, email validator, message cleaner |
| L3-1, L3-2 | 🔴 | CamelCase hashtag generator, palindrome checker |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Try the idea in the REPL (<code>python</code> → type lines one at a time) before writing the function.</details>
<details><summary>Hint 2</summary>Initials: <code>first, last = name.split()</code> then <code>first[0]</code>. Username: <code>lower()</code>, <code>replace(" ", ".")</code>, <code>str(year)[-2:]</code>. Email: count of <code>@</code>, no spaces, a <code>.</code> after the <code>@</code>. Hashtag: remove punctuation with <code>replace</code> → <code>title()</code> → <code>split()</code> + <code>"".join(...)</code> to drop spaces. Palindrome: lower, remove spaces, compare with <code>[::-1]</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day04_solution.py</code></details>

## 6. Quiz — answers in `solutions/day04_answers.md`
1. For `s = "PYTHON"`: what are `s[1]`, `s[-2]`, `s[1:4]`, `s[::-1]`?
2. What does `"  hi  ".strip()` return? Does it change the original variable?
3. What happens with `s[0] = "J"`? Why?
4. `"a,b,c".split(",")` returns what?
5. `"-".join(["2026", "11", "16"])` returns what?
6. What does `"hello world".find("z")` return?
7. Is `"Apple" == "apple"`? How do you compare them ignoring case?
8. What does `len("Hello World")` return?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: decisions with `if / elif / else` — delivery-fee rules and ATM logic.
