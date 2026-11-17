# 🐍 Python in 30 Days — from zero to "I can read and write real code"

A strict, hands-on, 2-hours-a-day programme. You learn by **running real examples from real-world situations** (food delivery, ATMs, sales reports, APIs), not by reading definitions. Every day has a **lesson**, a **code-along**, **auto-checked exercises at three difficulty levels**, a **quiz**, and a line in your **tracker**.

> **Goal:** above-intermediate Python for **data/AI** *and* **automation/backend** work — and the ability to understand almost any beginner-to-intermediate code you meet.
> **Schedule:** Day 1 = **Mon 16 Nov 2026**, Day 30 = **Tue 15 Dec 2026** (change the start date in the tracker's *Settings* sheet).

## ⚡ Run it on any Windows PC (no VS Code, no Python, no Java needed)

**Double-click `start_app.bat`** in this folder. That's it.

| You double-click | What starts | Open |
|---|---|---|
| `start_app.bat` | asks: Python course, Java course, or both | (it tells you) |
| `start_app.bat py` | **Py Master**, the Python course | <http://127.0.0.1:8765> |
| `start_app.bat java` | **Java Master**, the Java course | <http://127.0.0.1:8766> |
| `start_app.bat both` | both courses side by side | both links above |

(From a terminal: `start_app.bat java`. Add `--no-browser` if you do not want the browser to open by itself.)

**The first run sets itself up, once.** It needs the internet and a few minutes, needs **no administrator rights**, and puts everything inside this folder:

- no suitable Python on the PC → it downloads a private Python 3.13 into `.tools\py` and installs the app's packages;
- Java course chosen and no Java 21 on the PC → it downloads a private JDK 21 into `.tools\jdk21` (about 190 MB) and the small JUnit / SQLite helper libraries into `java\lib`;
- if something is interrupted (for example the connection drops), just double-click again: it carries on where it stopped.

After that it starts in a few seconds, **even offline**. Keep the black window open while you learn; close it, or press `Ctrl+C`, to stop. Your progress is saved on that computer in `portal\data\` (Python course) and `portal\data-java\` (Java course), and the portal also keeps automatic daily backups in a `backups` folder inside each of them (use the 💾 button in the top bar to restore).

**Moving to another computer?** Copy this whole folder (or clone the repository) and double-click `start_app.bat`. To bring your progress along, also copy `portal\data` and `portal\data-java`. You can skip the `.tools` folder: it is rebuilt automatically, but copying it saves the downloads.

If something goes wrong:

| Problem | Fix |
|---|---|
| "Setup could not finish" | There is no internet right now. Connect, then double-click again. |
| The window closes at once | Open *Command Prompt*, go to this folder with `cd`, run `start_app.bat` and read the message it prints before it stops. No administrator rights are needed. |
| "address already in use" / the page does not load | The course is already running in another window (the launcher then just opens it), or another program uses port 8765 / 8766. Close the other window. |
| Antivirus or a company PC blocks the downloads | Install Python 3.11+ (and, for Java, a JDK 21) yourself with `SETUP.md`, then run `start_app.bat` again: it uses what is installed. |
| You want to start over | Delete the `.tools` folder (and `.venv-portal` if it exists), then double-click again. Your progress in `portal\data*` is not touched. |

Developers can also run `python -m portal [--track java] [--port N] [--no-browser]`, or `pip install -e .` and then `pymaster` / `javamaster`.
## ✦ Py Master — the learning portal (optional, recommended)
Double-click **`start_app.bat`** (see above; `run_portal.bat` still works if you already installed Python). It opens a calm local web app at <http://127.0.0.1:8765> with all 30 days, an in-browser editor that runs and auto-checks your code, quizzes, notes, and a **three-pane workspace**:
- **Left 50 % — the lesson** (code-along, exercises, quiz). **Right 50 % — a playground** that stays put, so you never re-copy code. Press **▶ Try** on any code block to drop it into the playground.
- **Bottom — the AI assistant** (a slim ask-bar; click it or press `Ctrl+K` to open it as a third pane): "I understood the code, but where would it be used?"
- **Resize** by dragging the gutters (double-click a gutter to reset). **Pop a pane out** into its own window with ⧉, or drag its tab out of the browser like a Chrome tab (drop it on the other pane to swap sides; ⇲ docks it back). Windows stay in sync and the clock keeps counting.
- The **☰ navigation drawer** closes itself when you pick something. The current day is highlighted; "where you left off" is a small dot.
- **👁 Visualize** on any code block (or ask the assistant "show me a visual"): step through the code with variables, stack and heap drawn live (shows when two names share one object), or see a flow chart of the code; SQL gets a query-order diagram.
- **No day is ever locked.** Finish a day in 40 minutes, spend three days on one topic, or vanish for a week: the portal just welcomes you back with a recap.
- **It tracks, quietly:** active time per day, runs and results, hints/solutions used, quiz self-ratings, and every question you ask, scored for quality, with an **Insights** page about how you learn. Everything stays in `portal/data/` on your computer.
- **Search everything:** press `Ctrl+P` (or `/`) for a command palette: full-text search across every lesson, quiz, concept and guide, plus quick actions (resume, theme, settings…).
- **Smart review:** the home page shows a spaced-review card: quiz questions you missed (back after 1 day, or 3 if "partly") and exercises you failed most.
- **🧩 Blueprints:** three real-time style mini-systems (live order tracker, ticket-triage pipeline, site watcher) with architecture / sequence / state diagrams, the Python features each one uses (mapped to course days), runnable code, a ▶ run-the-demo tab, and a catalog of **16 reusable patterns**. Open it from the drawer, or go to `#/blueprints`.
- **🧩 Drills (new exercise types):** every day has a **Drills** tab with five short exercises besides writing code: **arrange** the lines of a program (some are traps), **fill the blanks**, **predict the output**, **find the bug** and **review AI-written code**. 150 drills for the whole course; every program in them was really run, so the answers are never guesses. Open it from a day's tab bar or go to `#/day/N/drills`.
- **⭐ XP, levels and badges (optional):** the chip in the top bar turns what you already do (passing checks, quiz answers, finished days, focused minutes, good questions, drills) into XP, a level, a streak that never punishes gaps, a daily goal and 16 badges. The home page also offers a **10-minute warm-up** that brings back concepts that are due for review. Hide it any time from the chip.
- **💾 Backups:** your progress is copied safely once a day (the last 14 days plus 4 weekly copies are kept). Use the 💾 button in the top bar to back up now, download a copy, or restore one (a restore saves your current progress first, so you can undo it).
- **Tutor:** works out of the box (built-in knowledge of "where / how is this used?"). For open-ended answers click ⚙ and paste a Cursor / Anthropic / OpenAI key, or set `CURSOR_API_KEY`.

## ▶ Start here (3 steps)
1. **Start the app** → double-click `start_app.bat` (sets itself up on the first run; nothing to install by hand). Prefer working in an editor with plain files? Then install Python with [`SETUP.md`](SETUP.md) (≈ 30 min, once).
2. **Read the plan** → [`00_GAME_PLAN.md`](00_GAME_PLAN.md) (10 min): timeline, rules, what to do when you fall behind.
3. **Open Day 1** → [`days/day01_hello_python/LESSON.md`](days/day01_hello_python/LESSON.md), and open [`tracker/PROGRESS_TRACKER.xlsx`](tracker/PROGRESS_TRACKER.xlsx) next to it.

## 📁 What's in the box
```
PY/
├── README.md                  ← you are here
├── 00_GAME_PLAN.md            ← 30-day timeline, weekly milestones, catch-up rules, concept map
├── SETUP.md                   ← install Python, editor setup, troubleshooting
├── requirements-week4.txt     ← libraries for Days 24–30 (install on Day 24)
├── tracker/
│   └── PROGRESS_TRACKER.xlsx  ← dashboard, daily plan, 233-exercise log, concept checklist, bug journal …
├── days/
│   └── dayNN_topic/
│       ├── LESSON.md          ← scenario → concepts → common mistakes → tasks → hints → quiz
│       ├── examples.py        ← code-along: type it, run it, change it
│       └── practice.py        ← YOUR exercises + auto-checker ([PASS]/[FAIL])
├── solutions/
│   ├── dayNN_answers.md       ← quiz answers  (check AFTER the quiz)
│   └── dayNN_solution.py      ← model solutions (last resort! see hint ladder)
├── blueprints/                ← 3 full-stack reference projects + PATTERNS.md (shown in the portal; run `python demo.py` inside each)
├── datasets/                  ← realistic data used from Day 15 on (sales, messy sales, students, logs, contacts)
├── cheatsheets/               ← one-page references + error decoder + "how to get unstuck"
└── _dev_tools/                ← maintainer scripts (you can ignore this folder)
```

## 🔁 The daily routine (≈ 2 hours)
| Min | Step | What you do |
|---|---|---|
| 0–10 | **Warm-up** | Answer the recap questions at the top of the lesson, from memory |
| 10–30 | **Learn** | Read `LESSON.md` (concept + tiny code). Run the snippets. |
| 30–60 | **Code-along** | Open `examples.py`. **Type** it (don't paste), run, change values, break it on purpose |
| 60–105 | **Practice** | Run `python practice.py` in the day's folder. Fix `[FAIL]`s one by one — Level 1 → 2 → 3 |
| 105–115 | **Quiz** | 6–8 questions, closed book, then check `solutions/dayNN_answers.md` |
| 115–120 | **Track** | Update the tracker: status, hours, quiz score, exercise statuses, **one Bug Journal entry** |

### How `practice.py` works
```powershell
cd days\day08_lists
python practice.py
```
Each exercise has a comment block with the task, and a `# TODO: write your code here` spot. The checker at the bottom runs your code and prints:
```
[PASS] L1-1 first_and_last
[FAIL] L1-2 total  (got 5, want 6)
Score: 7/12 checks passed
```
Your job: make every line `[PASS]`. A crash in one exercise never stops the others.

## 🧗 Three difficulty levels in every day
| Level | Label | Feels like |
|---|---|---|
| 🟢 **L1** | Beginner | Guided, one idea at a time (copy the pattern from the lesson) |
| 🟡 **L2** | Intermediate | Combine 2–3 ideas, handle simple edge cases |
| 🔴 **L3** | Challenge | Design it yourself, tricky data, edge cases. Expect to struggle — that's the learning |

**Hint ladder** (10 min each, in order): ① re-read the lesson section → ② the hint shape in `LESSON.md` → ③ read **one** task in `solutions/dayNN_solution.py`, close it, write it from memory. Log "Passed with hints" honestly in the tracker.

## ⚖️ Ground rules
1. **Type the code yourself.** Copy-paste teaches nothing.
2. **Run code every few lines.** Small steps, constant feedback.
3. **Errors are information.** Read the *last line* of the error first; write each new one in the **Bug Journal**.
4. **Time-box:** stuck >15 min on one problem → use the next hint level.
5. **Never skip the quiz or the tracker update.** They take 15 minutes and make the rest stick.
6. **Behind schedule?** Follow the *catch-up protocol* in the game plan — don't try to "make it all up" in one night.
7. **Use AI assistants as a tutor, not a vending machine:** attempt first, then ask "why does this fail?" or "review my code"; never paste the task and copy the answer. (On Day 30 the exam is closed-book.)

## 🧪 Checking everything works
- `python days\day01_hello_python\examples.py` should print without errors.
- Every `practice.py` runs immediately and shows `[FAIL]` for unfinished exercises — that's expected until you solve them.
- Solutions in `solutions/` score full marks (`Score: X/X`) — they were all executed and verified when this course was built.

## 🆘 Help
- [`cheatsheets/error_decoder.md`](cheatsheets/error_decoder.md) — what every common error means and how to fix it
- [`cheatsheets/how_to_get_unstuck.md`](cheatsheets/how_to_get_unstuck.md) — a step-by-step debugging routine
- [`cheatsheets/python_cheatsheet.md`](cheatsheets/python_cheatsheet.md) and [`data_cheatsheet.md`](cheatsheets/data_cheatsheet.md) — syntax at a glance

Good luck — see you on Day 30 with your own API and a final score! 🚀
