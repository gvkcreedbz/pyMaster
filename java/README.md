# ☕ Java in 30 Days — from zero to "I can read and write real code"

The Java twin of the [Python course](../README.md). Same strict, hands-on, 2-hours-a-day programme, same real-world scenarios (food delivery, ATMs, sales reports, APIs), same three difficulty levels, same tracker — but every day is taught in **idiomatic modern Java 21**. You learn by **running real examples**, not by reading definitions. Every day has a **lesson**, a **code-along**, **auto-checked exercises at three levels**, a **quiz**, and a line in your **tracker**.

> **Goal:** confident, above-intermediate Java: you can write 100–200-line programs, model data with classes and records, process data with collections and streams, read files, talk to a database, call and serve HTTP, test your code, and — most importantly — **read and understand** code written by others.
> **Schedule:** Day 1 = **Mon 16 Nov 2026**, Day 30 = **Tue 15 Dec 2026** (change the start date in the tracker's *Settings* sheet).
> **Already know the Python course?** Great: every Java day names what is *different from Python* (types, braces, semicolons, `==` vs `.equals`). You can do both courses side by side.

## ✦ Java Master — the learning portal (optional, recommended)
Double-click **`start_app.bat java`** in the project root (or `start_app.bat` and press 2). On a PC with nothing installed it downloads a private Python and a private JDK 21 the first time, no admin rights needed (details in the root `README.md`). `run_java_portal.bat` still works if you installed the JDK and Python yourself ([`SETUP.md`](SETUP.md)). It opens a calm local web app at <http://127.0.0.1:8766> with all 30 days, an in-browser editor that compiles, runs and auto-checks your code, quizzes, notes and a **three-pane workspace**.

> Want the Python course open too? Double-click **`start_app.bat both`** (or the older `run_all.bat`): it starts *Py Master* (<http://127.0.0.1:8765>) **and** *Java Master* (<http://127.0.0.1:8766>) at the same time. Both keep their progress separately.

- **Three-pane workspace.** Left 50 % — the lesson (code-along, exercises, quiz). Right 50 % — a playground that stays put, so you never re-copy code (press **▶ Try** on any code block). Bottom — the AI assistant (click the ask-bar or press `Ctrl+K` to open it as a third pane). Drag the gutters to resize (double-click to reset); pop a pane out into its own window with ⧉.
- **👁 Visualizer.** Step through Java code line by line: local variables on the **stack**, objects on the **heap**, and arrows that show when two variables point at the *same* object — the single best way to understand references, `String` vs `StringBuilder`, and `==` vs `.equals`.
- **`Ctrl+P` search.** A command palette (also `/`): full-text search across every lesson, quiz, concept and guide, plus quick actions (resume, theme, settings…).
- **Smart review.** The home page shows a spaced-review card: quiz questions you missed (back after 1 day, or 3 if "partly") and exercises you failed most.
- **🧩 Blueprints.** Real-time-style mini-systems with architecture / sequence / state diagrams, the Java features each one uses (mapped to course days), runnable code and a catalog of reusable patterns. Open it from the drawer or go to `#/blueprints`.
- **🧩 Drills (new exercise types).** Every day has a **Drills** tab with five short exercises besides writing code: **arrange** the lines (braces included, some lines are traps), **fill the blanks**, **predict the output**, **find the bug** and **review AI-written code**. 150 drills for the course; every program was compiled and run with the real JDK, so the answers are never guesses. Open it from a day's tab bar or go to `#/day/N/drills`.
- **⚡ Practice sessions:** mixed problems from every day you have opened, with the topic hidden, so you learn to *recognise* which idea a problem needs. It adapts (harder after three clean answers, easier after two misses), gives a 3-step hint ladder (smallest hint first), lets you **think out loud** (type, or dictate in Chrome/Edge) and rate your confidence, then shows whether feeling sure meant being right. Open it from the menu or `#/practice`.
- **🔮 Predict before you run:** on the Code-along tab, Run first asks what you expect it to print, then shows your guess next to the real output. Switch it off with the *Predict first* checkbox.
- **📋 Learning-loop notes:** [`LEARNING_LOOP.md`](../LEARNING_LOOP.md) compares these features with the open-source LearnHarness app and lists what was and was not borrowed.
- **⭐ XP, levels and badges (optional)** and **💾 backups** work exactly as in the Python course (see the root `README.md`).
- **No day is ever locked.** Finish a day in 40 minutes, spend three days on one topic, or vanish for a week: the portal welcomes you back with a recap.
- **It tracks, quietly:** active time per day, compile/run results, hints/solutions used, quiz self-ratings and the questions you ask the tutor. Everything stays in the portal's data folder on your computer.
- **Tutor:** works out of the box; for open-ended answers click ⚙ and paste a Cursor / Anthropic / OpenAI key, or set `CURSOR_API_KEY`.

## ▶ Start here (3 steps)
1. **Install the JDK** → follow [`SETUP.md`](SETUP.md) (≈ 30 min, once).
2. **Read the plan** → [`00_GAME_PLAN.md`](00_GAME_PLAN.md) (10 min): timeline, rules, what to do when you fall behind.
3. **Open Day 1** → [`days/day01_hello_java/LESSON.md`](days/day01_hello_java/LESSON.md), and open [`tracker/JAVA_PROGRESS_TRACKER.xlsx`](tracker/JAVA_PROGRESS_TRACKER.xlsx) next to it.

## 📁 What's in the box
```
java/
├── README.md                  ← you are here
├── 00_GAME_PLAN.md            ← 30-day timeline, weekly milestones, catch-up rules, concept map
├── SETUP.md                   ← install JDK 21, editor setup, jars, troubleshooting
├── _AUTHORING.md              ← (maintainers) syllabus and file formats
├── tracker/
│   └── JAVA_PROGRESS_TRACKER.xlsx  ← dashboard, daily plan, exercise log, concept checklist, bug journal …
├── days/
│   └── dayNN_topic/
│       ├── LESSON.md          ← scenario → concepts → common mistakes → tasks → hints → quiz
│       ├── Examples.java      ← code-along: type it, run it, change it
│       └── Practice.java      ← YOUR exercises + auto-checker ([PASS]/[FAIL])
├── solutions/
│   ├── dayNN_answers.md       ← quiz answers  (check AFTER the quiz)
│   └── dayNN_Solution.java    ← model solutions (last resort! see hint ladder)
├── datasets/                  ← realistic data used from Day 15 on (sales, messy sales, students, logs, contacts)
├── cheatsheets/               ← java cheatsheet, collections & streams, error decoder, "how to get unstuck"
├── blueprints/                ← reference mini-systems + patterns (shown in the portal)
└── lib/                       ← jars for Days 24, 28, 29 (JUnit console, sqlite-jdbc, slf4j) - fetched by a script
```
The portal, the Python course (`days/`, `solutions/` in the project root) and the maintainer scripts in `_dev_tools/` live one level up; you can ignore `_dev_tools/`.

## 🔁 The daily routine (≈ 2 hours)
| Min | Step | What you do |
|---|---|---|
| 0–10 | **Warm-up** | Answer the recap questions at the top of the lesson, from memory |
| 10–30 | **Learn** | Read `LESSON.md` (concept + tiny code). Run the snippets (or paste them into `jshell`). |
| 30–60 | **Code-along** | Open `Examples.java`. **Type** it (don't paste), run, change values, break it on purpose |
| 60–105 | **Practice** | Run `java Practice.java` in the day's folder. Fix `[FAIL]`s one by one — Level 1 → 2 → 3 |
| 105–115 | **Quiz** | 8 questions, closed book, then check `solutions/dayNN_answers.md` |
| 115–120 | **Track** | Update the tracker: status, hours, quiz score, exercise statuses, **one Bug Journal entry** |

### How `Practice.java` works
```powershell
cd java\days\day08_arrays
java Practice.java
```
Java 21 compiles and runs a single source file in one step. Each exercise is a **method** with a comment block (the task) and a spot for your code. The checker at the bottom runs your code and prints:
```
[PASS] L1-1 firstAndLast
[FAIL] L1-2 total  (got 5, want 6)
Score: 7/12 checks passed
```
Your job: make every line `[PASS]`. Unfinished methods contain a harmless placeholder (`return 0;`) so the file always compiles, and a crash in one exercise never stops the others.

## 🧗 Three difficulty levels in every day
| Level | Label | Feels like |
|---|---|---|
| 🟢 **L1** | Beginner | Guided, one idea at a time (copy the pattern from the lesson) |
| 🟡 **L2** | Intermediate | Combine 2–3 ideas, handle simple edge cases |
| 🔴 **L3** | Challenge | Design it yourself, tricky data, edge cases. Expect to struggle — that's the learning |

**Hint ladder** (10 min each, in order): ① re-read the lesson section → ② the hint shape in `LESSON.md` → ③ read **one** task in `solutions/dayNN_Solution.java`, close it, write it from memory. Log "Passed with hints" honestly in the tracker.

## 🗓 The 30 days at a glance
| Week | Days | Theme | 🏆 Milestone |
|---|---|---|---|
| 1 | 1–7 | Foundations: classes, `main`, variables, `Scanner`, numbers, strings, `if`/`switch`, loops | Mini ATM |
| 2 | 8–14 | Data structures & methods: arrays, `List`/`Set`/`Map`, lambdas & streams, records | Expense tracker |
| 3 | 15–21 | Real programs: files, CSV/JSON, exceptions, packages & `java.time`, OOP | Library system |
| 4 | 22–30 | Professional toolkit: generics, regex, JUnit & Git, collectors, HTTP, JDBC/SQL, pipeline, REST API | Sales pipeline + mini API + final exam |

Full day-by-day table: [`00_GAME_PLAN.md`](00_GAME_PLAN.md).

## ⚖️ Ground rules
1. **Type the code yourself.** Copy-paste teaches nothing.
2. **Compile and run every few lines.** Small steps, constant feedback.
3. **Errors are information.** Read the *first* compiler error (and the *last* line of a stack trace first); write each new one in the **Bug Journal**.
4. **Time-box:** stuck >15 min on one problem → use the next hint level.
5. **Never skip the quiz or the tracker update.** They take 15 minutes and make the rest stick.
6. **Behind schedule?** Follow the *catch-up protocol* in the game plan — don't try to "make it all up" in one night.
7. **Use AI assistants as a tutor, not a vending machine:** attempt first, then ask "why does this fail?"; never paste the task and copy the answer. (On Day 30 the exam is closed-book.)

## 🧪 Checking everything works
- `java Examples.java` inside a day folder should print without errors.
- Every `Practice.java` runs immediately and shows `[FAIL]` for unfinished exercises — that's expected until you solve them.
- Solutions in `solutions/` score full marks (`Score: X/X`) — they were all executed and verified when this course was built.

## 🆘 Help
- [`cheatsheets/error_decoder.md`](cheatsheets/error_decoder.md) — what every common `javac` and runtime error means and how to fix it
- [`cheatsheets/how_to_get_unstuck.md`](cheatsheets/how_to_get_unstuck.md) — a step-by-step debugging routine
- [`cheatsheets/java_cheatsheet.md`](cheatsheets/java_cheatsheet.md) and [`collections_streams_cheatsheet.md`](cheatsheets/collections_streams_cheatsheet.md) — syntax at a glance
- Prefer Python first? The twin course lives in the project root: [`../README.md`](../README.md) (portal "Py Master", `run_portal.bat`, port 8765).

Good luck — see you on Day 30 with your own REST API and a final score! 🚀
