# SETUP — Install Java 21 and get ready (≈ 30 minutes, once)

You only do this **once**, on Day 1. Windows 10/11 instructions. If something fails, see *Troubleshooting* at the bottom.

You need a **JDK** (Java *Development* Kit — it contains the compiler `javac`, the runtime `java` and the live calculator `jshell`). A plain "JRE" is not enough. This course uses **JDK 21** (an LTS release) and nothing newer than Java 21 features.

## 1. Install a JDK 21

### Option A — One command (recommended)
```powershell
winget install EclipseAdoptium.Temurin.21.JDK
```
**Close and re-open your terminal** afterwards (so the new `PATH` is picked up). The installer sets `JAVA_HOME` and `PATH` for you.

### Option B — Installer
Download **Temurin 21 (LTS), Windows x64, `.msi`** from <https://adoptium.net/temurin/releases/?version=21>. In the installer, enable the features **"Add to PATH"** and **"Set JAVA_HOME variable"**.

### Option C — Portable JDK, no admin rights (what this project can do for you)
From the project root:
```powershell
python _dev_tools\fetch_java_libs.py --jdk
```
This downloads Temurin 21 into `.tools\jdk21` inside the project (and the course jars, see §6). The portal and the maintainer scripts find it automatically (`JAVA_HOME`, then `.tools\jdk21`, then `PATH`). To use it in a terminal too:
```powershell
$env:JAVA_HOME = (Resolve-Path .tools\jdk21).Path
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
```
(That only lasts for the current terminal window.)

## 2. Check that it works
Open a terminal in Cursor (**Ctrl + `**, or *Terminal → New Terminal*) and type:
```powershell
java -version
javac -version
```
You should see `openjdk version "21.0.x"` and `javac 21.0.x`. 🎉 Both must say **21** (or higher).

> If `java` is "not recognized", or `javac` is missing while `java` works, jump to *Troubleshooting*.

## 3. Try `jshell` — a live Java calculator
`jshell` runs one line of Java at a time, perfect for experiments (you do not need a class or `main`):
```text
PS> jshell
jshell> 2 + 3
$1 ==> 5
jshell> "chai".toUpperCase()
$2 ==> "CHAI"
jshell> /exit
```

## 4. Run your first file
Since Java 11 you can run a single `.java` file in one step — no separate compile command:
```powershell
cd java\days\day01_hello_java
java Examples.java       # the code-along
java Practice.java       # your exercises + the auto-checker ([PASS] / [FAIL])
```
Behind the scenes Java compiles the file in memory and runs the first class in it. The "classic" two-step way (you will see it in older books) is:
```powershell
javac Hello.java         # creates Hello.class
java Hello               # runs it (note: no .java here)
```
Tips: **↑ arrow** repeats the previous command · **Tab** auto-completes folder names · **Ctrl+C** stops a running program.

## 5. Cursor / VS Code setup (5 min)
1. Open this project folder (**File → Open Folder** → the `PY` folder, or just its `java` subfolder).
2. Install **Extension Pack for Java** (Microsoft; includes *Language Support for Java by Red Hat*, *Debugger for Java*, *Test Runner for Java*, *Maven for Java*) from the Extensions panel (Ctrl+Shift+X).
3. If the extension asks which JDK to use: **Ctrl+Shift+P → "Java: Configure Java Runtime"** and pick JDK 21. If you used the portable JDK, add this to your user `settings.json`:
   ```json
   "java.jdt.ls.java.home": "C:\\path\\to\\PY\\.tools\\jdk21"
   ```
4. Open `java/days/day01_hello_java/Examples.java`. You can run it with the **Run** link above `main`, with ▶ in the top-right corner, or from the terminal with `java Examples.java`.
5. Handy shortcuts: **Shift+Alt+F** formats the file · **F5** starts the debugger (set a breakpoint by clicking left of a line number) · **Ctrl+.** shows quick fixes for red squiggles · type `sout` + Tab for `System.out.println()`.
6. The editor may underline `Practice.java` files as "not on the classpath" or show duplicate-class warnings (every day has its own `class Practice`). That is harmless — running from the terminal always works.

## 6. Jars for Days 24, 28 and 29 (install on Day 24 — not before)
Most days use only the JDK. Three days need small helper libraries (**jars**):

| Day | Jar | Used for |
|---|---|---|
| 24 | `junit-platform-console-standalone` | JUnit 5 tests |
| 28, 29 | `sqlite-jdbc` | SQLite database from Java (JDBC) |
| 28, 29 | `slf4j-api`, `slf4j-nop` | logging facade needed by sqlite-jdbc |

Download them all with one command (from the project root):
```powershell
python _dev_tools\fetch_java_libs.py
```
They are saved in `java\lib\`. The lessons show the exact command; it looks like this (a `*` after the folder lets Java take every jar in it):
```powershell
java -cp "..\..\lib\*" Practice.java
```
Nothing else to install, no Maven, no internet needed afterwards.

## 7. Optional but recommended
- **Excel** (or LibreOffice / Google Sheets) to open `java/tracker/JAVA_PROGRESS_TRACKER.xlsx`.
- **Git**: `winget install Git.Git` (needed on Day 24), then `git --version`.
- **SQLite Viewer** extension in Cursor (Day 28) to peek inside `.db` files.
- Show UTF-8 properly in the terminal if you see strange symbols: `chcp 65001` — and see the encoding row below.
- The **learning portal**: double-click `start_app.bat java` in the project root (it fetches a private Python and JDK 21 by itself on a PC that has none; no admin rights). The older `run_java_portal.bat` → <http://127.0.0.1:8766>. It needs Python (see the root `SETUP.md`) only to run the portal server; your Java code is compiled by your JDK. The first run builds a private environment (a few minutes, once). `run_all.bat` starts the Python and the Java portal together.

## Troubleshooting
| Problem | Fix |
|---|---|
| `java` is not recognized as a command | The JDK is not on `PATH`. Re-open the terminal after installing; if it still fails, re-run the installer with **Add to PATH** enabled, or add `C:\Program Files\Eclipse Adoptium\jdk-21...\bin` to *Environment Variables → Path*. For the portable JDK use the `$env:Path` lines in §1 Option C. |
| `javac` is not recognized, but `java` works | You installed a **JRE** (no compiler). Install the **JDK** (§1). Check with `where.exe javac`. |
| `java -version` shows 8, 11 or 17 | An older Java comes first on `PATH`. Run `where.exe java` to see the order; remove the old one from `PATH`, or put the JDK 21 `bin` folder first. |
| `error: class found on application class path: Examples` / *"class not found"* / `Error: Could not find or load main class X` | You used the classic form with a wrong name or folder. Be in the file's folder, and run `java File.java` **with** `.java`, or `java ClassName` (without `.java`) only *after* `javac`. Class names are case-sensitive. |
| `Error: LinkageError ... UnsupportedClassVersionError: ... class file version 65.0, this version only recognizes 52.0 (or 55.0, 61.0)` | The code was compiled by Java 21 but you run an older `java`. Make `java -version` say 21 (see above), delete stale `*.class` files and run again. |
| `error: release version 21 not supported` / `invalid source release: 21` | `javac` is older than 21. Same fix: put JDK 21 first on `PATH`. |
| `error: class Practice is public, should be declared in a file named Practice.java` | The file name must match a `public` class name. Rename the file or the class. (Course files use non-public classes, so you should not see this unless you edited them.) |
| Garbled characters like `â€”`, `Ã©`, or `?` for ₹ / emoji | Java 21 reads files as UTF-8 by default, but the Windows console may not print it. Run `chcp 65001`, and start Java with `java -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 File.java` (or set `$env:JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8"` once per terminal). Save your files as UTF-8 in the editor (bottom-right status bar). |
| `NoSuchFileException: ../../datasets/sales.csv` | Wrong working directory. Run from **inside the day folder** (`cd java\days\dayNN_...`). Print where you are with `System.out.println(Path.of("").toAbsolutePath());`. |
| `ClassNotFoundException: org.sqlite.JDBC` / `java.sql.SQLException: No suitable driver` | The sqlite-jdbc jar is not on the classpath. Run `python _dev_tools\fetch_java_libs.py` and use `-cp "..\..\lib\*"`. |
| `Could not find or load main class org.junit.platform.console.ConsoleLauncher` (Day 24) | The JUnit jar is missing or the `-cp` path is wrong. Fetch the jars (§6) and check that `java\lib\junit-platform-console-standalone-*.jar` exists. |
| `Address already in use: bind` (Days 27, 30) | An earlier run of your server is still alive. Press **Ctrl+C** in its terminal, or end `java.exe` in Task Manager; or use another port. |
| Cursor/VS Code shows red squiggles but `java File.java` works | The Java extension is using another JDK or sees no project. **Ctrl+Shift+P → "Java: Clean Java Language Server Workspace"** → restart, and pick JDK 21 (§5). |
| PowerShell says "running scripts is disabled" | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then try again (only needed for `.ps1` scripts). |
| `python` is not recognized when running `fetch_java_libs.py` | Install Python from the root `SETUP.md`, or use `py _dev_tools\fetch_java_libs.py`. |
| Download fails behind a company proxy | Open the URLs in `_dev_tools\fetch_java_libs.py` in a browser (Maven Central / Adoptium) and put the jars into `java\lib\` by hand; install the JDK with the `.msi` (Option B). |
| Still stuck | Read `cheatsheets/how_to_get_unstuck.md`, then ask a human or an AI assistant with the **full error text** and your code. |
