# 🎯 00 — GAME PLAN: Python in 30 Days (strict timeline)

**Start:** Mon 16 Nov 2026 (Day 1) · **Finish:** Tue 15 Dec 2026 (Day 30) · **Budget:** ~2 hours/day = ~60 hours
**Target:** *Above-intermediate* — you can write 100–200-line programs, clean and analyse data, call APIs, use databases, write tests, build a small web API, and — most importantly — **read and understand** code written by others.
**Direction:** Data/AI-leaning **and** Automation/backend-leaning (the second half of the course is the shared foundation of both).

---

## 1. How this course works (the method)
| Principle | What it means for you |
|---|---|
| **Real example first, theory second** | Every day opens with a real-world situation (Swiggy bill, ATM, sales export…) and a **trend** note: *why* professionals use this. |
| **Code before words** | Each concept is shown as 3–10 lines you can run, then a code-along, then exercises. |
| **Three difficulty levels daily** | L1 Beginner → L2 Intermediate → L3 Challenge, all auto-checked. See §5. |
| **Immediate feedback** | `python practice.py` prints `[PASS]`/`[FAIL]`. No guessing whether you're right. |
| **Spiral learning** | Lists appear in Day 8, then again in dicts, comprehensions, JSON, pandas… everything returns in later projects. |
| **Project every Sunday** | Days 7, 14, 21 are *project + review* days (the weekend buffer); Day 29 is the capstone. |
| **Reflection** | Bug Journal + Weekly Review + Concept Checklist make learning visible. |

## 2. The 30-day timeline
Click a topic to open the lesson. 🏆 = project/review day. Dates assume the default start; they update in the tracker if you change it.

| Day | Date | Topic (lesson) | Real-world scenario |
|---|---|---|---|
| 1 | Mon 16 Nov | [Hello, Python! (How a computer follows instructions)](days/day01_hello_python/LESSON.md) | A café receipt printer. |
| 2 | Tue 17 Nov | [Variables, Data Types & input()](days/day02_variables_input/LESSON.md) | Food-delivery bill splitter (Swiggy / Zomato / Uber Eats style). |
| 3 | Wed 18 Nov | [Numbers, Operators & the math Module](days/day03_numbers_operators/LESSON.md) | E-commerce checkout + loan EMI calculator. |
| 4 | Thu 19 Nov | [Strings (Text Processing)](days/day04_strings/LESSON.md) | Instagram signup + caption tools. |
| 5 | Fri 20 Nov | [Decisions: if / elif / else, and / or / not](days/day05_decisions/LESSON.md) | Delivery-fee rules and ATM checks. |
| 6 | Sat 21 Nov | [Loops: for, while, break, continue](days/day06_loops/LESSON.md) | Number-guessing game + PIN retry + processing 1,000 orders. |
| 7 🏆 | Sun 22 Nov | [Week 1 Project: Mini ATM + Guessing Game (and Week-1 Review)](days/day07_week1_project_atm/LESSON.md) | An ATM (and every "menu-driven" app). |
| 8 | Mon 23 Nov | [Lists](days/day08_lists/LESSON.md) | A shopping cart, a Spotify playlist, a to-do app. |
| 9 | Tue 24 Nov | [Tuples & Sets](days/day09_tuples_sets/LESSON.md) | Instagram "mutual friends" and "unique visitors". |
| 10 | Wed 25 Nov | [Dictionaries (key → value)](days/day10_dictionaries/LESSON.md) | Contact book, inventory, user profile, word counts. |
| 11 | Thu 26 Nov | [Functions (reusable building blocks)](days/day11_functions/LESSON.md) | A billing service. |
| 12 | Fri 27 Nov | [Comprehensions, lambda, sorted(key=…), zip, enumerate](days/day12_comprehensions_lambda/LESSON.md) | E-commerce filters + music charts. |
| 13 | Sat 28 Nov | [Nested Data & JSON](days/day13_nested_data_json/LESSON.md) | A restaurant-listing API (Zomato/Swiggy style). |
| 14 🏆 | Sun 29 Nov | [Week 2 Project: Expense Tracker (and Week-2 Review)](days/day14_week2_project_expense_tracker/LESSON.md) | A personal-finance app (Splitwise / Google Pay "Spends"). |
| 15 | Mon 30 Nov | [Files & pathlib](days/day15_files_pathlib/LESSON.md) | A server log analyser. |
| 16 | Tue 01 Dec | [CSV & JSON Files](days/day16_csv_json_files/LESSON.md) | A sales report from an Excel/ERP export. |
| 17 | Wed 02 Dec | [Errors, Exceptions, Debugging & Logging](days/day17_errors_logging/LESSON.md) | A payment service. |
| 18 | Thu 03 Dec | [Modules, the Standard Library, pip & Virtual Environments](days/day18_modules_stdlib_venv/LESSON.md) | A birthday/deadline reminder + a quick analytics helper. |
| 19 | Fri 04 Dec | [Object-Oriented Programming I: Classes & Objects](days/day19_oop_basics/LESSON.md) | A banking app. |
| 20 | Sat 05 Dec | [OOP II: Inheritance, Polymorphism, Dunder Methods, Dataclasses, ABCs](days/day20_oop_advanced/LESSON.md) | An HR/payroll system and a game. |
| 21 🏆 | Sun 06 Dec | [Week 3 Project: Library Management System (and Week-3 Review)](days/day21_week3_project_library_system/LESSON.md) | A public-library / office-asset system. |
| 22 | Mon 07 Dec | [Generators, Iterators, Decorators & Context Managers](days/day22_generators_decorators/LESSON.md) | Streaming a 10-GB log file, retrying API calls, auto-closing DB connections. |
| 23 | Tue 08 Dec | [Regular Expressions, Type Hints & Clean Code](days/day23_regex_typehints_cleancode/LESSON.md) | Cleaning a messy contact/invoice dump. |
| 24 | Wed 09 Dec | [Testing with pytest & Git Basics](days/day24_pytest_git/LESSON.md) | A shop's discount code broke on Black Friday. |
| 25 | Thu 10 Dec | [NumPy & pandas I: Arrays and DataFrames](days/day25_numpy_pandas_1/LESSON.md) | You're the new analyst at an online store. |
| 26 | Fri 11 Dec | [pandas II: Cleaning, groupby, merge, pivot & Charts](days/day26_pandas_2_matplotlib/LESSON.md) | A messy weekly sales export lands on your desk. |
| 27 | Sat 12 Dec | [APIs & Web Scraping: Getting Data from the Internet](days/day27_apis_scraping/LESSON.md) | A dashboard that needs live weather/posts/prices. |
| 28 | Sun 13 Dec | [Databases: SQLite & SQL](days/day28_sqlite_sql/LESSON.md) | Files don't scale — store and query orders with SQL. |
| 29 🏆 | Mon 14 Dec | [Capstone: Build a Sales Data Pipeline (ETL)](days/day29_capstone_pipeline/LESSON.md) | Every Monday the store emails a messy CSV. |
| 30 🎓 | Tue 15 Dec | [FastAPI Taste & The Final Exam](days/day30_fastapi_final_exam/LESSON.md) | The mobile-app team needs your data. |

## 3. Weekly milestones — "I can…" checks
| Week | Days | By the end you can… | Milestone |
|---|---|---|---|
| **1 · Foundations** | 1–7 | read/write simple scripts: variables, input, f-strings, numbers, strings, `if`, loops; read an error message | 🏆 Mini ATM + guessing game (interactive, auto-tested) |
| **2 · Data structures & functions** | 8–14 | choose between list / tuple / set / dict, write functions, use comprehensions, handle nested data & JSON | 🏆 Expense Tracker with budget report |
| **3 · Real programs** | 15–21 | read/write files (CSV, JSON), handle errors, log, use modules & venvs, design classes (inheritance, dataclasses) | 🏆 Library Management System with save/load |
| **4 · Professional toolkit** | 22–30 | generators, decorators, regex, type hints, **pytest + Git**, NumPy/pandas/charts, APIs & scraping, **SQL**, ETL pipeline, FastAPI | 🏆 Sales pipeline (CLI) + mini API + closed-book final exam |

*(Week 4 has 9 days because the plan is exactly 30 days.)*

## 4. A typical 2-hour day
| Min | Step | Notes |
|---|---|---|
| 0–10 | Warm-up recall | From memory — retrieval beats re-reading |
| 10–30 | Lesson | Concept + tiny runnable snippets |
| 30–60 | Code-along | Type, run, modify, break `examples.py` |
| 60–105 | Practice | `practice.py` — L1 → L2 → L3, hint ladder if stuck |
| 105–115 | Quiz | Closed book; check the answer file |
| 115–120 | Tracker | Status, hours, quiz score, exercise statuses, Bug Journal |

**Best schedule:** one fixed daily slot (same time, phone away). Two 60-minute blocks (e.g. morning learn + evening practice) work as well as one 2-hour block.

## 5. Difficulty design
| Level | Typical skill | Support |
|---|---|---|
| 🟢 L1 Beginner | Apply one concept from today's lesson | Pattern in the lesson; checker messages show expected vs actual |
| 🟡 L2 Intermediate | Combine today's idea with earlier days; handle edge cases | Hint ladder |
| 🔴 L3 Challenge | Multi-step problem, design choices, tricky data | Hint ladder + solution as last resort |
| 🏆 Project | An interactive or end-to-end program that uses the whole week | Review section + checklist |
| 🎓 Final exam | 27 "what does this print / find the bug" questions (closed-book) | Answer key with explanations |

**Spiral difficulty curve:** short, concrete exercises in Week 1 → data-structure puzzles in Week 2 → mini systems in Week 3 → realistic datasets and tools in Week 4.

## 6. Falling behind? The catch-up protocol (read this *before* you need it)
Life happens. The timeline is strict, so the plan has a built-in recovery system:

1. **Never stop for more than 1 day in a row.** Do the **Minimum Viable Day (60 min)** instead: Lesson (15) → Code-along (25) → *only the L1 and L2 exercises* (15) → Quiz (5). Mark the day **Done**; mark skipped L3 exercises **Not started**.
2. **Weekend buffer:** Days 6, 7, 13, 14, 20, 21, 27, 28 fall on weekends. If you're ≤ 1 day behind, use the weekend slot to finish the missed day's L3 exercises, then do the project.
3. **Behind by 2–3 days:** for each missed day do the Minimum Viable Day (60 min) and spend the saved time in two extra 60-min sessions — one *double day* per weekend.
4. **Behind by 4+ days:** do **not** compress the foundations (Days 1–14). Instead: skip *Level 3 exercises* on Days 15–23 (revisit them after Day 30), and keep the capstone (Day 29) and final exam (Day 30). The dashboard shows "BEHIND by N day(s)" so you notice early.
5. **Ahead of schedule?** Do the stretch goals (Day 29), write pytest tests for an old project, or start a portfolio idea from the *Projects* sheet. Don't skip ahead to later days — the order matters.

**"Done" for a day means:** all L1 + L2 exercises pass · quiz ≥ 6/8 (or you reviewed the misses) · tracker updated · one Bug Journal entry.

## 7. Concept coverage map
| Area | Concepts | Days |
|---|---|---|
| **Basics** | `print`, variables, types, `input`, f-strings, operators, `math` | 1–3 |
| **Text** | indexing, slicing, string methods, formatting, regex | 4, 23 |
| **Control flow** | `if/elif/else`, `match`, boolean logic, `for`, `while`, `break/continue`, `random` | 5–7 |
| **Data structures** | list, tuple, set, dict, nested data, copy vs alias, counting/grouping patterns | 8–10, 13 |
| **Functions** | parameters, defaults, `*args/**kwargs`, scope, recursion, `lambda`, `zip/enumerate`, `map/filter` | 3, 11–12 |
| **Comprehensions** | list/dict/set comprehensions, generator expressions | 12, 22 |
| **Files & data formats** | `open`, `with`, `pathlib`, CSV, JSON, encodings | 13, 15–16 |
| **Robustness** | exceptions, custom errors, `assert`, logging, debugging | 17, 24 |
| **Project structure** | modules, standard library, `pip`, venv, `__main__`, argparse | 18, 29 |
| **OOP** | classes, `__init__`, `@property`, inheritance, polymorphism, dunder methods, dataclasses, ABC | 19–21 |
| **Advanced Python** | iterators, generators, decorators, closures, context managers, type hints | 22–23 |
| **Quality** | PEP 8, clean code, Ruff, pytest, fixtures, parametrize, Git | 23–24 |
| **Data analysis** | NumPy, pandas, cleaning, `groupby`, merge, pivot, matplotlib | 25–26 |
| **Internet & automation** | HTTP, `requests`, JSON APIs, retries, BeautifulSoup scraping | 27 |
| **Databases** | SQLite, SQL (SELECT, GROUP BY, JOIN), transactions, injection safety | 28 |
| **Putting it together** | ETL pipeline, CLI, reports, FastAPI (routes, Pydantic, status codes) | 29–30 |

*Intentionally left for later (≥ intermediate+ topics):* `async/await`, multiprocessing, packaging/publishing, Docker, machine-learning libraries, web frameworks beyond FastAPI basics. Day 30's "where to go next" gives a roadmap.

## 8. Tracking your progress
Open **`tracker/PROGRESS_TRACKER.xlsx`** (first tab *START HERE*).
- **Dashboard:** progress %, on-track/behind status, hours vs plan, longest streak, exercise & quiz stats, 4 charts.
- **Daily Plan:** the 30 days above with live dates, statuses, hours, quiz scores, per-day exercise counts.
- **Exercise Log:** one row for each of the **233 exercises** (L1/L2/L3) — mark *Passed alone / Passed with hints / Viewed solution*.
- **Concept Checklist:** 192 concepts, confidence 1–5, "can I explain it?".
- **Projects · Weekly Review · Time Log · Bug Journal · Settings.**

Update it for 5 minutes at the end of every session; do the Weekly Review every Sunday (15 min).

## 9. Design inspirations & where to go deeper
The structure borrows proven ideas from well-known free resources — use them as optional extra practice:
- **CS50P** (Harvard) — problem sets, testing mindset · **Automate the Boring Stuff with Python** (Al Sweigart) — practical automation projects
- **Exercism Python track** — mentor-style exercises with tests · **Real Python** tutorials — deep dives per topic
- **The official Python Tutorial** (docs.python.org) · **PEP 8** (style) · **pytest**, **pandas**, **FastAPI** official docs
- **Kaggle Learn** (pandas, data visualisation) — datasets and short courses after Day 26
- Practice sites for scraping/APIs: `quotes.toscrape.com`, `books.toscrape.com`, JSONPlaceholder, Open-Meteo

## 10. After Day 30 — your next 30 days
0. Study the three **Blueprints** (`blueprints/`, or `#/blueprints` in the portal): a live order tracker, an AI ticket-triage pipeline and a site watcher, each with diagrams, a Python-feature map and runnable code. Rebuild one from its 6 milestones.
1. Pick **one** portfolio project (Projects sheet) and put it on GitHub with a README.
2. Re-do the final exam in 2 weeks — your score should go *up*.
3. Choose a track: **Data/AI** (scikit-learn → PyTorch → LLM APIs/RAG) or **Backend/Automation** (FastAPI + PostgreSQL → auth → Docker → deploy).
4. Read other people's code for 20 minutes a day — you have the skills now.
