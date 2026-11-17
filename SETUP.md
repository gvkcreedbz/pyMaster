# SETUP — Install Python and get ready (≈ 30 minutes, once)

You only do this **once**, on Day 1. Windows 10/11 instructions. If something fails, see *Troubleshooting* at the bottom.

## 1. Install Python 3.13

### Option A — Installer (most reliable for beginners)
1. Go to <https://www.python.org/downloads/windows/> and download **Python 3.13.x (Windows installer, 64-bit)**.
   *(3.12 or 3.14 also work. Avoid very old versions.)*
2. Run the installer. On the **first screen**, tick ☑ **"Add python.exe to PATH"** (very important!), then click **Install Now**.
3. When it finishes, click **Disable path length limit** if offered, then **Close**.

### Option B — One command (if you prefer the terminal)
```powershell
winget install Python.Python.3.13
```
Close and re-open your terminal afterwards.

## 2. Check that it works
Open a terminal in Cursor (**Ctrl + `**, or *Terminal → New Terminal*) and type:
```powershell
python --version
python -m pip --version
```
You should see `Python 3.13.x` and a pip version. 🎉

> If `python` opens the Microsoft Store or says "not found", jump to *Troubleshooting*.

## 3. Cursor / VS Code setup (5 min)
1. Open this project folder (**File → Open Folder** → the `PY` folder).
2. Install the extensions **Python** (Microsoft) and **Ruff** (Astral) from the Extensions panel (Ctrl+Shift+X).
3. Bottom-right (or Ctrl+Shift+P → *Python: Select Interpreter*): choose the Python 3.13 you just installed.
4. Open `days/day01_hello_python/examples.py` and press the ▶ **Run Python File** button (top right). You should see output in the terminal.

## 4. How to run things (you will do this every day)
In the terminal, move into the day's folder and run the files:
```powershell
cd days\day01_hello_python
python examples.py       # the code-along
python practice.py       # your exercises + the auto-checker ([PASS] / [FAIL])
```
Tips: **↑ arrow** repeats the previous command · **Tab** auto-completes folder names · **Ctrl+C** stops a running program.

## 5. Libraries for Week 4 (install on Day 24 — not before)
```powershell
cd <the PY project folder>
python -m pip install -r requirements-week4.txt
```
Always use `python -m pip ...` (not just `pip ...`) so the library goes into the same Python that runs your code.

The portal's **Blueprints** demos (the live order tracker needs `fastapi` and `httpx`) use this same file, so install it before pressing ▶ Run demo there.

## 6. Git (needed on Day 24)
```powershell
winget install Git.Git
```
Re-open the terminal, then `git --version`. Create a free account at <https://github.com> when Day 24 tells you to.

## 7. Optional but recommended
- **Excel** (or LibreOffice / Google Sheets) to open `tracker/PROGRESS_TRACKER.xlsx`.
- **SQLite Viewer** extension in Cursor (Day 28) to peek inside `.db` files.
- Make the terminal show UTF-8 if you ever see strange symbols: `chcp 65001`.

## Troubleshooting
| Problem | Fix |
|---|---|
| `python` is not recognized | Python was installed without PATH. Re-run the installer → **Modify** → tick *Add Python to environment variables*; or uninstall and reinstall ticking *Add python.exe to PATH*. Then open a **new** terminal. |
| `python` opens the Microsoft Store | Windows Settings → *Apps → Advanced app settings → App execution aliases* → turn **off** the two "python" / "python3" aliases. Or use `py` instead of `python` (e.g. `py practice.py`). |
| `pip` is not recognized | Use `python -m pip install ...`. |
| PowerShell says "running scripts is disabled" (when activating a venv on Day 18) | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` then try again. |
| `ModuleNotFoundError: No module named 'pandas'` (etc.) | Run `python -m pip install -r requirements-week4.txt`. If you use a virtual environment, activate it first. |
| Weird characters like `â€”` in output | Save files as UTF-8 and run `chcp 65001` in the terminal. |
| A warning about `httpx` / `starlette` on Day 30 | It is only a deprecation notice — everything still works. |
| Cursor runs a different Python than the terminal | Ctrl+Shift+P → *Python: Select Interpreter* → pick the 3.13 one. |
| Still stuck | Read `cheatsheets/how_to_get_unstuck.md`, then ask a human or an AI assistant with the **full error text** and your code. |

## Learning portal (optional)
**Easiest: double-click `start_app.bat`.** It installs a private Python for you if the PC has none (no admin rights; see the top of `README.md`). Alternatively, after installing Python yourself, double-click `run_portal.bat` in this folder (the app is called Py Master; two panes: lesson + playground, assistant at the bottom). The first run builds a private environment (a few minutes, once); after that it opens http://127.0.0.1:8765 in seconds. Your progress lives in `portal/data/` (back it up if you like). To enable the open-ended AI tutor, click Settings in the portal and paste a Cursor / Anthropic / OpenAI API key, or set the `CURSOR_API_KEY` environment variable before launching.
