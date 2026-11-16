"""Maintainer tool: verify the Java course (the twin of verify.py).

For every day it checks:  the solution scores X/X, Examples.java exits 0, the unfinished Practice.java compiles and
reports a score, Practice.java is in sync with the solution, and the lesson has the structure the portal parses
(title, scenario, concept headings, 3 hints, quiz with matching answers, exercise headers).

usage:  python _dev_tools/verify_java.py [day numbers...]      sample keyboard input: _dev_tools/stdin_java/dayNN.txt
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jdk  # noqa: E402
import java_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "java"
STDIN = Path(__file__).resolve().parent / "stdin_java"
days = [int(a) for a in sys.argv[1:]] or list(range(1, 31))
EX_HEADER = re.compile(r"^\s*//\s+(L\d-\d)\s+\|\s+(.+?)\s+\(Level\s+(\d)", re.M)
bad = 0
for n in days:
    msgs = []
    folder = next(iter((JAVA / "days").glob(f"day{n:02d}_*")), None)
    sol = JAVA / "solutions" / f"day{n:02d}_Solution.java"
    ans = JAVA / "solutions" / f"day{n:02d}_answers.md"
    if folder is None:
        print(f"Day {n:02d}: PROBLEMS\n    no folder java/days/day{n:02d}_*")
        bad += 1
        continue
    sin = STDIN / f"day{n:02d}.txt"
    stdin_text = sin.read_text(encoding="utf-8") if sin.exists() else ""
    if sol.exists():
        r = jdk.run_file(sol, folder, stdin_text)
        m = re.search(r"Score: (\d+)/(\d+)", r.stdout)
        if r.returncode != 0 or not m or m.group(1) != m.group(2):
            msgs.append(f"SOLUTION problem rc={r.returncode} score={m.group(0) if m else None}\n{r.stdout[-1200:]}\n{r.stderr[-1200:]}")
        elif "// @@CHECKER@@" in sol.read_text(encoding="utf-8"):
            msgs.append("solution still has the @@CHECKER@@ placeholder: run java_sync.py")
    else:
        msgs.append("no solution file")
    ex = folder / "Examples.java"
    if ex.exists():
        r = jdk.run_file(ex, folder, stdin_text)
        if r.returncode != 0:
            msgs.append(f"EXAMPLES crashed rc={r.returncode}\n{r.stdout[-400:]}\n{r.stderr[-900:]}")
    else:
        msgs.append("no Examples.java")
    pr = folder / "Practice.java"
    if pr.exists():
        r = jdk.run_file(pr, folder, stdin_text)
        if "error:" in r.stderr or "Exception in thread" in r.stderr and "Score" not in r.stdout:
            msgs.append(f"PRACTICE does not compile/run in its unfinished state\n{r.stderr[-900:]}")
        elif not re.search(r"Score: (\d+)/(\d+)", r.stdout):
            msgs.append("PRACTICE has no Score line")
        if sol.exists() and pr.read_text(encoding="utf-8") != java_sync.make_practice(sol.read_text(encoding="utf-8")):
            msgs.append("Practice.java is out of sync with the solution: run java_sync.py")
        n_ex = len(EX_HEADER.findall(pr.read_text(encoding="utf-8")))
        if n_ex < 5:
            msgs.append(f"only {n_ex} exercises with a header like `// L1-1 | Title   (Level 1 - Beginner)` (need 5+)")
    else:
        msgs.append("no Practice.java")
    lesson = folder / "LESSON.md"
    if not lesson.exists():
        msgs.append("missing LESSON.md")
    else:
        t = lesson.read_text(encoding="utf-8")
        if not re.search(rf"^#\s+Day\s+{n:02d}\s+—\s+\S", t, flags=re.M):
            msgs.append("LESSON.md title must look like `# Day 05 — Decisions (if / else / switch)` (em dash)")
        if not re.search(r"\|\s*⏱[^\n]*\n\|[-| ]+\|\n\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", t):
            msgs.append("LESSON.md needs the header table  | ⏱ Time | 🎯 Goal | 🏁 Level |")
        if not re.search(r"^##\s+🌍[^\n]*\n+\S", t, flags=re.M):
            msgs.append("LESSON.md needs a `## 🌍 Real-world scenario & trend` section")
        if len(re.findall(r"^###\s+\d+\.\d+\s+\S", t, flags=re.M)) < 3:
            msgs.append("LESSON.md needs 3+ concept headings like `### 1.1 Something`")
        if len(re.findall(r"<details>\s*<summary>Hint \d", t)) != 3:
            msgs.append("LESSON.md needs exactly 3 hints: <details><summary>Hint 1 - ...")
        qm = re.search(r"^##\s+\d+\.\s+[^\n]*?(?:Quiz|Review Test)[^\n]*\n(.*?)(?=^##\s|\Z)", t, flags=re.M | re.S)
        nq = len(re.findall(r"^\s*\d+\.\s+\S", qm.group(1), flags=re.M)) if qm else 0
        na = len(re.findall(r"^\s*\d+\.\s+\S", ans.read_text(encoding="utf-8"), flags=re.M)) if ans.exists() else 0
        if nq < 6 or nq != na:
            msgs.append(f"quiz has {nq} questions but answers.md has {na} (need 6+ and equal)")
    if not ans.exists():
        msgs.append("missing answers.md")
    print(f"Day {n:02d}: {'OK' if not msgs else 'PROBLEMS'}")
    for m in msgs:
        print("   ", m)
        bad += 1
print("TOTAL PROBLEMS:", bad)
sys.exit(1 if bad else 0)
