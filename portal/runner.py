"""Runs learner code in a separate Python process (timeout, output cap).

Code runs inside a work copy of the course tree (portal/data/work) so relative paths like
`datasets/sales.csv` behave exactly as they do on disk, and your original files are never touched.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
import time

from . import content, db

WORK = db.DATA_DIR / "work"
MAX_OUT = 20000
TIMEOUT = int(os.environ.get("PORTAL_RUN_TIMEOUT", "25"))
SLOW_DAYS = {25, 26, 27, 28, 29, 30}  # pandas/matplotlib import time


_prep_lock = threading.Lock()
_prepared = False


def prepare(force: bool = False) -> None:
    """Mirror datasets and day folders into the work tree (without overwriting existing work files).

    The heavy copy happens once per server start (it used to run before *every* execution, which made each
    Run click slower than it needed to be); afterwards only the scratch folder is guaranteed to exist.
    """
    global _prepared
    (WORK / "days" / "_play").mkdir(parents=True, exist_ok=True)
    if _prepared and not force:
        return
    with _prep_lock:
        if _prepared and not force:
            return
        if content.DATASETS.is_dir():
            shutil.copytree(content.DATASETS, WORK / "datasets", dirs_exist_ok=True)
        for d in content.load_days().values():
            dst = WORK / "days" / d["folder"]
            if not dst.exists():
                shutil.copytree(content.DAYS_DIR / d["folder"], dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        _prepared = True


_file_locks: dict[str, threading.Lock] = {}


def file_lock(path) -> threading.Lock:
    """One lock per script path: two windows pressing Run at once must not overwrite each other's file mid-run."""
    return _file_locks.setdefault(str(path), threading.Lock())


def clean_env() -> dict:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "MPLBACKEND": "Agg", "PYTHONWARNINGS": "ignore"}
    # never leak assistant keys into learner code
    for k in ("CURSOR_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        env.pop(k, None)
    return env


def _workdir(day_no: int | None) -> os.PathLike:
    if day_no and (d := content.day(day_no)):
        return WORK / "days" / d["folder"]
    return WORK / "days" / "_play"


def execute(code: str, *, day_no: int | None, filename: str, stdin: str = "") -> dict:
    prepare()
    wd = _workdir(day_no)
    wd.mkdir(parents=True, exist_ok=True)
    path = wd / filename
    env = clean_env()
    limit = TIMEOUT * (2 if day_no in SLOW_DAYS else 1)
    t0 = time.time()
    timed_out = False
    with file_lock(path):
        path.write_text(code, encoding="utf-8")
        try:
            p = subprocess.run([sys.executable, "-u", str(path)], cwd=str(wd), input=stdin, capture_output=True,
                               text=True, encoding="utf-8", errors="replace", timeout=limit, env=env, check=False)
            out = (p.stdout or "") + (("\n" + p.stderr) if p.stderr else "")
            rc = p.returncode
        except subprocess.TimeoutExpired as e:
            timed_out = True
            raw = e.stdout or ""
            out = (raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw) + \
                  f"\n\n⏱ Stopped after {limit}s. Is there a loop that never ends (while True without break)?"
            rc = -1
    ms = int((time.time() - t0) * 1000)
    if len(out) > MAX_OUT:
        out = out[:MAX_OUT] + "\n… output truncated …"
    hint = None
    if "EOFError" in out and not stdin.strip():
        hint = "Your program called input(). Type the answers in the Input box (one line per input() call) and run again."
    return {"output": out.rstrip(), "ok": rc == 0, "returncode": rc, "ms": ms, "timed_out": timed_out, "hint": hint}


_LAUNCH = "import sys, runpy; sys.path.insert(0, '.'); runpy.run_path(sys.argv[1], run_name='__main__')"


def run_blueprint_demo(bid: str) -> dict | None:
    """Run a blueprint's demo.py from a fresh private copy (so a demo can never touch the originals)."""
    bp = content.load_blueprints().get(bid)
    if not bp or not bp.get("demo"):
        return None
    src, dst = content.BP_DIR / bp["folder"], WORK / "blueprints" / bp["folder"]
    with file_lock(dst):
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.db"))
        t0 = time.time()
        timed_out = False
        try:
            p = subprocess.run([sys.executable, "-u", "-c", _LAUNCH, bp["demo"]], cwd=str(dst), capture_output=True,
                               text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT, env=clean_env(), check=False)
            out = (p.stdout or "") + (("\n" + p.stderr) if p.stderr else "")
            rc = p.returncode
        except subprocess.TimeoutExpired as e:
            timed_out, rc = True, -1
            raw = e.stdout or ""
            out = (raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw) + f"\n\n⏱ Stopped after {TIMEOUT}s."
    if len(out) > MAX_OUT:
        out = out[:MAX_OUT] + "\n… output truncated …"
    hint = None
    if "ModuleNotFoundError" in out and ("fastapi" in out or "httpx" in out):
        hint = "This demo needs the Week-4 libraries: python -m pip install -r requirements-week4.txt"
    return {"output": out.rstrip(), "ok": rc == 0, "returncode": rc, "ms": int((time.time() - t0) * 1000),
            "timed_out": timed_out, "hint": hint}


def run_practice(day_no: int, code: str, stdin: str = "") -> dict:
    res = execute(code, day_no=day_no, filename="practice.py", stdin=stdin)
    parsed = db.record_attempt(day_no, "practice", res["output"], res["ok"], res["ms"], res["timed_out"], len(code))
    return {**res, **parsed}


def run_examples(day_no: int, code: str, stdin: str = "") -> dict:
    res = execute(code, day_no=day_no, filename="examples.py", stdin=stdin)
    db.record_attempt(day_no, "examples", "", res["ok"], res["ms"], res["timed_out"], len(code))
    return {**res, "results": [], "passed": None, "total": None}


def run_playground(code: str, stdin: str = "") -> dict:
    res = execute(code, day_no=None, filename="play.py", stdin=stdin)
    db.record_attempt(0, "playground", "", res["ok"], res["ms"], res["timed_out"], len(code))
    return {**res, "results": [], "passed": None, "total": None}
