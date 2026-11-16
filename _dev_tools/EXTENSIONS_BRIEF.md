# Brief for feature authors (read fully before coding)

Project: a 30-day Python course and a Java twin, with ONE local web portal (FastAPI backend + vanilla-JS ES-module
front end, no build step, nothing loaded from a CDN) that serves one track per process: `PORTAL_TRACK=python`
(Py Master, port 8765, default) or `PORTAL_TRACK=java` (Java Master, port 8766). Every feature you build must work for
BOTH tracks (read `portal/track.py`: file names, comment syntax, `track.IS_JAVA`, `track.T[...]`, `track.public()`).
Workspace root: `c:\Users\C8T9C7\Desktop\desk\TESTING-AI\PY`. Windows + PowerShell 5.

## How features plug in (read `portal/ext.py` first)
* Backend: create `portal/ex_<name>.py` with `router = APIRouter()` (paths `/api/<name>/...`) and optional `setup()`
  (create your own tables with `db.run("CREATE TABLE IF NOT EXISTS ...")`). Do NOT edit `portal/main.py`.
  Every POST/PUT/DELETE needs the header `x-portal: 1` (the app guard enforces it; the front end `api()` adds it).
* Front end: create `portal/static/js/extras/<name>.js` exporting `async init(ctx)` (ctx = api, $, $$, esc, md, enhance,
  toast, modal, store, TRK, S, hooks, layout, tutor, openVisualizer, openSettings, openPalette, PANE) and optional CSS
  `portal/static/css/extras/<name>.css` (auto-linked; use the existing CSS variables from `portal/static/app.css`, support
  light + dark, keep the calm, minimal look). Hook into the UI by listening for document events `pm:route`,
  `pm:dayrendered`, `pm:runresult` and by injecting DOM (topbar widgets go into `#topbar-extras`). Study how
  `portal/static/js/day.js`, `home.js`, `insights.js`, `tutor.js`, `util.js`, `runpanel.js`, `layout.js` build views so your
  DOM matches the existing patterns. The lesson/playground/tutor can live in separate browser windows (see `layout.js`,
  `sync.js`): never assume all panes are in one window, and guard `PANE` usage (only inject UI where the element exists).
* Data: the SQLite progress db (see `portal/db.py`: tables settings, sessions, activity, events, attempts, checks,
  drafts, notes, quiz, day_state, questions, reflections; helpers `db.rows/one/run/log_event/get_setting/set_setting`).
  Prefer DERIVING numbers from existing tables so results are retroactive and never double-count. Log your own
  user actions with `db.log_event(session_id, "<type>", day_no, payload_dict)`.
* Never lock learner progress or content. Never block a run. Degrade silently if something is missing.
* Local-only security posture: validate inputs, cap sizes, no shell strings built from user text, no external network.

## Conventions
* UTF-8 WITHOUT BOM everywhere. Create files with the `fs_write` tool (not `Set-Content -Encoding UTF8`, which adds a BOM
  in PowerShell 5). Existing files may use CRLF; keep a file's existing line endings when you edit it.
* The terminal shows UTF-8 text garbled (e.g. an arrow shows as 3 odd characters). That is a display artifact, not file
  corruption. Do not "repair" characters because of it. When printing text from Python set `$env:PYTHONUTF8="1"`.
* Redirect long outputs to a file and read it back (e.g. `... *> "$env:TEMP\x.log"`), the shell output can get mangled.
* Python for tools/tests: `& "$env:TEMP\pyverify\py\python.exe" -W ignore ...` (plain `python` is not installed). pytest, fastapi,
  httpx, pandas, websockets are available there. JDK 21 is in `.tools\jdk21` (found automatically via `portal/track.py`).
* Tests: write `_dev_tools/test_ex_<name>.py` (pytest, `-p no:cacheprovider`). Pattern: set `os.environ["PORTAL_DATA"]` to a temp dir
  BEFORE importing `portal.main`, use `fastapi.testclient.TestClient(main.app, base_url="http://127.0.0.1:8765")` with
  `headers={"x-portal": "1"}` for writes; see `_dev_tools/portal_smoke.py` and `_dev_tools/portal_smoke_java.py`. The track is chosen by
  `PORTAL_TRACK` before import, so run your test file once per track (`$env:PORTAL_TRACK="java"` for the second run).
  `sys.dont_write_bytecode = True` in tests; never leave `__pycache__` in `portal/` or blueprint folders... (it is git-ignored anyway).
* Browser checks (optional, keep light): do NOT use `_dev_tools/ui_regress.py` (it uses a fixed debugging port that other
  agents share). If you want to see your UI, start a test server on YOUR port with YOUR temp data dir
  (`$env:PORTAL_DATA=...; $env:PORTAL_PORT=<your port>; & python portal\run.py --no-browser` in the background), and drive Chrome
  (`$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe`) headless with your own `--user-data-dir` and your own
  `--remote-debugging-port`, e.g. a tiny websockets/CDP script, or `--dump-dom --virtual-time-budget=8000`. Always stop servers you start.
* Do not touch files owned by other features (listed in your task). If you need a change in a shared file, make the smallest
  possible edit, and say so in your final message. No git commands. No questions: decide and report your assumptions.
* Quality bar: no dead UI, no console errors, empty states handled, works at 420 px, 1000 px and 1440 px widths, keyboard
  accessible, plain wording for beginners. Keep each new file under ~450 lines; split if bigger.
* Final message (brief): files created/changed, endpoints added (method + path), how to see it in the UI (URL + what to click),
  test results, assumptions, known limits.
