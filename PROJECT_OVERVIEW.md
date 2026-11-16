# Project overview: 30-Day Python Course + "Py Master" portal

*Last updated: Mon 16 Nov 2026. Everything below was checked against the files in this folder.*

## 1. What is this project?

A complete **learn-Python-in-30-days** kit for a person with zero coding experience, aiming past intermediate level
(goals: data/AI-ML and automation/backend). It has two halves:

| Half | What it is | Where |
|---|---|---|
| **The course** | 30 daily lessons, practice files with auto-checkers, quizzes, datasets, cheatsheets, an Excel tracker | `days/`, `solutions/`, `datasets/`, `cheatsheets/`, `tracker/`, `00_GAME_PLAN.md` |
| **Py Master** (the portal) | A local web app (FastAPI + SQLite + vanilla JS) that shows the course, runs your code, checks it, tracks how you learn, and has an AI assistant beside the lesson | `portal/`, started by `run_portal.bat` |
| **Blueprints** | 3 real-time style reference projects (with diagrams and runnable code) showing how Python is used in real systems, plus 16 reusable patterns | `blueprints/` (also shown in the portal) |

- Timeline: Day 1 = Mon 16 Nov 2026, Day 30 = Tue 15 Dec 2026, about 2 hours a day. Nothing is locked; the dates are only a suggestion.
- Runs **only on your own computer** (127.0.0.1:8765). Your progress and questions are stored in `portal/data/progress.db`.
- Homepage: http://127.0.0.1:8765/

## 2. The numbers

| Item | Count |
|---|---|
| Lessons | 30 (4 weeks; Days 7, 14, 21 are weekly projects, Day 29 capstone, Day 30 FastAPI + final exam) |
| Exercises with auto-checkers | 233 |
| Quiz questions | 259 |
| Python files under `days/` (examples + practice) | 63 |
| Model solutions | 30 |
| Datasets / cheatsheets | 5 / 4 |
| Portal backend modules (Python) | 12 |
| Portal frontend modules (JavaScript) | 16 |
| Built-in tutor knowledge-base entries | 34 |
| Blueprints / patterns | 3 / 16 |
| Test suites | `portal_smoke` ~100 checks, `test_blueprints` 20 tests, `ui_regress` 871 checks, plus visual, fallback, pop-out and detach tests |

Curriculum by week:

| Week | Theme | Days |
|---|---|---|
| 1 Foundations | variables, decisions, loops, ATM project | 1-7 |
| 2 Data and functions | lists, tuples/sets, dicts, functions, comprehensions, nested data/JSON, expense tracker project | 8-14 |
| 3 Real-world tools | files/pathlib, CSV/JSON, errors/logging, modules/venv, OOP, library system project | 15-21 |
| 4 Pro toolkit | generators/decorators, regex/type hints, pytest/git, numpy/pandas, plotting, APIs/scraping, SQLite/SQL, capstone pipeline, FastAPI + exam | 22-30 |

## 3. Portal backend modules (`portal/*.py`) and whether they use AI

**Short answer: only 1 of the 12 backend modules (`assistant.py`) can call an AI. The other 11 are ordinary code with no AI.**
Even the assistant works with **no AI at all**, because it falls back to a built-in tutor.

| # | Module | What it does | Uses AI? |
|---|---|---|---|
| 1 | `main.py` | FastAPI app: all `/api/...` endpoints, the local-only security guards (127.0.0.1, Host allow-list, `x-portal` header). Routes `/api/chat` and `/api/insights/reflect` to the assistant | No (it only forwards to `assistant.py`) |
| 2 | `assistant.py` | The tutor. Tries Cursor SDK, then Anthropic (Claude), then OpenAI (GPT), then the offline tutor. Also the optional "reflect on my learning" text | **Yes, optional** (the only module with AI calls) |
| 3 | `kb.py` | Hand-written knowledge base (34 concepts: "where is this used / how / pitfalls"), used by the offline tutor | No (static content) |
| 4 | `analytics.py` | Progress per day, streaks, welcome-back logic, question scoring (quality, type, Bloom level, duplicates), insights, recommendations | No (rules and heuristics) |
| 5 | `db.py` | SQLite storage (sessions, activity, attempts, checks, quiz, notes, drafts, questions, reflections), export | No |
| 6 | `content.py` | Loads lessons, exercises, quizzes, extras and blueprints from the files | No |
| 7 | `runner.py` | Runs your code and the checkers in a sandboxed subprocess (timeouts, API keys removed from its environment); runs blueprint demos | No |
| 8 | `visual.py` | "Visualize": step-through trace, flow chart, SQL query-order diagram (built from the code's syntax tree) | No (deterministic) |
| 9 | `tracer_harness.py` | The little program that records each step and variable while your code runs | No |
| 10 | `search.py` | Full-text search over lessons, quizzes, concepts, guides, blueprints (Ctrl+P) | No |
| 11 | `review.py` | Spaced-review queue (missed quiz questions, most-failed exercises) | No |
| 12 | `run.py` | Starts the server | No |

### How the AI assistant behaves (all in `assistant.py`)
- Every question is first **scored and stored** by `analytics.py` (no AI), then answered.
- Answer order: your preferred provider -> any other connected provider -> **built-in offline tutor**. If a provider fails (bad key, no network) it silently falls through, and the answer shows which provider answered.
- With **no key configured, it is 100% offline** (rules + the 34-entry knowledge base + a code reviewer + a Python error decoder).
- AI calls that exist: (1) the chat answer, (2) the "Reflect on my learning" button on the Insights page (without AI it produces a rule-based reflection instead).
- Quick buttons: where is it used, explain simply, real example, why, quiz me, review my code, hint, recap, show a visual.
- Your keys are stored only in `portal/data` or read from environment variables, and are stripped from the environment of the subprocess that runs your code.

### What is NOT AI even though it looks smart
Question-quality scoring and the "thinking profile", spaced review, search, Visualize/diagrams, auto-checking of exercises, welcome-back recaps, recommendations. All are plain rules and SQL.

## 4. Portal frontend modules (`portal/static/js/*.js`)

16 modules, no framework (plain ES modules, CodeMirror editor, marked for Markdown, vendored Mermaid for diagrams).
**Only `tutor.js` (chat) and the Reflect button in `insights.js` talk to the AI endpoints**; the other 14 never do.

| Module | Role |
|---|---|
| `app.js` | Boot, top bar, drawer navigation, router, settings, command-palette actions |
| `layout.js` | Three-pane workspace: resize, pop-out windows, drag-a-tab-out, dock back |
| `day.js` | A day: Learn / Code-along / Practice / Quiz / Notes tabs |
| `home.js` | Home: welcome back, week map, review card, Blueprints card |
| `playground.js` | Persistent playground pane |
| `runpanel.js` | Run button, output, check results |
| `tutor.js` | The AI assistant pane (streaming chat) |
| `visualizer.js` | Step-through visualizer |
| `diagram.js` | Mermaid diagram rendering (queued, strict security) |
| `insights.js` | Learning analytics page |
| `blueprints.js` | Blueprints pages (Guide / Code / Run the demo) |
| `palette.js` | Ctrl+P command palette and search |
| `sync.js` | Keeps pop-out windows in sync (BroadcastChannel) |
| `util.js` | API helper, sanitizer, Markdown, helpers |
| `misc.js`, `state.js` | Small helpers, shared state |

## 5. The 3 Blueprints (real-time style projects)

None of the three needs a real AI service to run: the demo "AI" in project 2 is a deliberately flaky stand-in so you can see how to protect against a bad model.

| # | Project | Kind | Python used | Uses AI? |
|---|---|---|---|---|
| 1 | **Live Order Tracker** (`01_live_order_tracker`) | Real-time backend | FastAPI, WebSocket, SQLite, pydantic, asyncio; state machine, idempotency, pub/sub, repository, app factory + DI | No |
| 2 | **Ticket Triage Pipeline** (`02_ticket_triage_pipeline`) | Data + AI pipeline | csv, generators, dataclasses, `Protocol` strategy, retry/backoff/jitter, fallback chain, idempotent SQLite upsert, validating model output | **Pattern for AI** (rules first, a pluggable `LLMClassifier(client)` that in production would wrap OpenAI/Claude; the demo uses a fake flaky client) |
| 3 | **Site & Price Watcher** (`03_site_watcher`) | Automation | plugin registry (decorator), circuit breaker, observer, atomic file writes, injected clock/network, alert on transitions | No |

So: **1 of 3 blueprints is about using AI safely (and runs offline), 2 of 3 have no AI.**
Each has a `BLUEPRINT.md` (problem, architecture/sequence/state diagrams, API contract, Python-feature to course-day map, failure modes, 6 build-it-yourself milestones) and a `demo.py` you can run. `blueprints/PATTERNS.md` is the 16-pattern catalog.

## 6. Features of the portal (what you can do)

- Three-pane workspace: lesson | playground | assistant; resizable, pop-out windows, light/dark theme.
- Run code in the browser; 233 exercises auto-checked ([PASS]/[FAIL]); hint ladder, then solutions.
- Quizzes with self-rating; notes; per-day drafts.
- Visualize any code: step-through with variables/stack/heap, flow chart, SQL diagrams.
- Time tracking with a server clock (heartbeat every 15 s, gaps ignored), never locks a day, welcome-back recap after a gap.
- Insights: time, streaks, question quality/type/Bloom level, how you think, weak spots, recommendations, optional AI reflection.
- Ctrl+P search; spaced review card; Blueprints and patterns; export all your data.

## 7. Folder map

```
PY/
|-- README.md, SETUP.md, 00_GAME_PLAN.md, PROJECT_OVERVIEW.md (this file)
|-- run_portal.bat, requirements-portal.txt, requirements-week4.txt
|-- days/dayNN_topic/        LESSON.md, examples.py, practice.py   (30 days)
|-- solutions/               dayNN_solution.py, dayNN_answers.md
|-- datasets/                sales.csv, sales_messy.csv, students.csv, contacts_messy.txt, app.log
|-- cheatsheets/             python, data, error decoder, how to get unstuck
|-- tracker/                 PROGRESS_TRACKER.xlsx (and PROGRESS_TRACKER2.xlsx)
|-- blueprints/              3 projects + PATTERNS.md
|-- portal/                  the Py Master app (12 Python modules, 16 JS modules, CSS, data/)
`-- _dev_tools/              maintainer scripts and test suites (learners can ignore)
```

## 8. Technology

- **Backend:** Python, FastAPI, SQLite (WAL mode). **Frontend:** vanilla JavaScript, CodeMirror 5, marked, Mermaid 10.9.1.
- **Optional AI:** Cursor SDK (`cursor-sdk`), Anthropic API, OpenAI API (keys are optional).
- **Course libraries (Week 4):** pytest, numpy, pandas, matplotlib, requests, beautifulsoup4, fastapi, uvicorn, httpx, ruff.

## 9. Privacy and safety

- Binds to 127.0.0.1 only; the Host header is checked; every change request needs the `x-portal: 1` header.
- Your code runs in a subprocess with a timeout; API keys are removed from its environment.
- Library and blueprint file access is allow-listed. Responses are `no-store`.
- Data stays in `portal/data/` (use the Export button to download everything).
- With no AI key, nothing is sent anywhere. With a key, only your question plus lesson context goes to that provider.

## 10. Run and test

```powershell
# start the portal (double-click run_portal.bat, or:)
python portal\run.py          # then open http://127.0.0.1:8765/

# check the course itself
python _dev_tools\verify.py

# portal tests (see _dev_tools\README.md)
python _dev_tools\portal_smoke.py
python -m pytest _dev_tools\test_blueprints.py
```

## 11. Known limits

- The UI regression scripts need Chrome and run against a **test** server (they create activity).
- Blueprint 1's demo needs `fastapi` and `httpx` (`requirements-week4.txt`).
- Without an AI key the tutor is rule-based: good on the 34 covered concepts, generic elsewhere.
