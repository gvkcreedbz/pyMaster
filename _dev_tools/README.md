# _dev_tools — maintainer scripts (learners: ignore this folder)

These scripts rebuild and verify the course itself. They need a Python with `pandas numpy matplotlib requests beautifulsoup4 pytest fastapi httpx openpyxl` installed. Run them from the project root.

| Script | Purpose |
|---|---|
| `make_practice.py [days…]` | Builds `days/dayNN_*/practice.py` from `solutions/dayNN_solution.py` by replacing each `# >>> SOLUTION … # <<< SOLUTION` block with a TODO. **The solution file is the source of truth** — never edit `practice.py` by hand. |
| `verify.py [days…]` | For every day: the solution must score X/X, `examples.py` must exit 0, and the (unfinished) `practice.py` must run cleanly and print a score. `stdin/dayNN.txt` feeds interactive days. |
| `build_exam.py` | Runs the 27 snippets of the Day 30 exam and writes `FINAL_EXAM.md` + the answer key from the *real* output. |
| `build_tracker.py` | Rebuilds `tracker/PROGRESS_TRACKER.xlsx` from the lessons/solutions. ⚠️ **Overwrites the workbook — any progress typed into it is lost.** |

### Portal tests (need `fastapi httpx pytest websockets`; UI scripts need Chrome)

| Script | Purpose |
|---|---|
| `portal_smoke.py` | In-process API suite (~105 checks) against a throw-away data dir: security guards, progress, quiz, search, review, blueprints. |
| `visual_smoke.py` / `portal_fallback_test.py` | Visualizer engine; tutor fallback chain when a provider key is bad. |
| `test_blueprints.py` | `pytest` unit tests for the three blueprints (state machine, idempotency, retry, circuit breaker…). |
| `ui_regress.py [url] [--quick] [--widths=1440,420]` | Headless Chrome sweep of every route at 3 widths: JS errors, bad requests, empty views, overflow, diagrams. **Run it against a TEST server** (`PORTAL_DATA=<tmp> PORTAL_PORT=8777`), it creates activity. |
| `ui_overflow_probe.py [url] [width] [route]` / `ui_shots2.py` | Diagnostics: list elements overflowing a narrow viewport; screenshots of the new screens. |
| `ui_popout_test.py` / `ui_detach_test.py` | Pop-out and drag-out pane windows. |

Typical workflow after editing a solution: `python _dev_tools/make_practice.py 12` then `python _dev_tools/verify.py 12`.
