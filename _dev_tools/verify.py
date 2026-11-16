"""Maintainer tool: run solution / examples / practice for each day and report problems.

Usage:  python _dev_tools/verify.py [day numbers...]
Sample keyboard input for examples that call input() lives in _dev_tools/stdin/dayNN.txt.
(Learners do NOT need this file.)
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STDIN = Path(__file__).resolve().parent / "stdin"
days = [int(a) for a in sys.argv[1:]] or list(range(1, 31))
env = dict(os.environ, PYTHONUTF8="1")


LAUNCHER = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); "
            "runpy.run_path(sys.argv[2], run_name='__main__')")   # mimics `python file.py` even for embeddable Python


def run(path: Path, stdin_text: str = "", timeout=90):
    return subprocess.run([sys.executable, "-c", LAUNCHER, str(path.parent), str(path)], input=stdin_text,
                          capture_output=True, text=True, encoding="utf-8", cwd=path.parent, env=env, timeout=timeout)


bad = 0
for n in days:
    folder = next((ROOT / "days").glob(f"day{n:02d}_*"))
    sol = ROOT / "solutions" / f"day{n:02d}_solution.py"
    sin = STDIN / f"day{n:02d}.txt"
    stdin_text = sin.read_text(encoding="utf-8") if sin.exists() else ""
    msgs = []
    if sol.exists():
        r = run(sol, stdin_text)
        m = re.search(r"Score: (\d+)/(\d+)", r.stdout)
        if r.returncode != 0 or not m or m.group(1) != m.group(2):
            msgs.append(f"SOLUTION problem rc={r.returncode} score={m.group(0) if m else None}\n{r.stdout[-1200:]}\n{r.stderr[-900:]}")
    else:
        msgs.append("no solution file")
    ex = folder / "examples.py"
    if ex.exists():
        r = run(ex, stdin_text)
        if r.returncode != 0:
            msgs.append(f"EXAMPLES crashed rc={r.returncode}\n{r.stderr[-900:]}")
    else:
        msgs.append("no examples.py")
    pr = folder / "practice.py"
    if pr.exists():
        r = run(pr, stdin_text)
        if "Traceback" in r.stderr or "SyntaxError" in r.stderr or "IndentationError" in r.stderr:
            msgs.append(f"PRACTICE crashes before reporting a score (an unfinished file must run cleanly)\n{r.stderr[-700:]}")
        elif not re.search(r"Score: (\d+)/(\d+)", r.stdout):
            msgs.append("PRACTICE has no Score line")
    else:
        msgs.append("no practice.py")
    if not (folder / "LESSON.md").exists():
        msgs.append("missing LESSON.md")
    if not (ROOT / "solutions" / f"day{n:02d}_answers.md").exists():
        msgs.append("missing answers.md")
    print(f"Day {n:02d}: {'OK' if not msgs else 'PROBLEMS'}")
    for m in msgs:
        print("   ", m)
        bad += 1
print("TOTAL PROBLEMS:", bad)
