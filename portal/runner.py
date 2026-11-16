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

from . import content, db, sandbox, track

WORK = db.DATA_DIR / "work"
MAX_OUT = 20000
TIMEOUT = int(os.environ.get("PORTAL_RUN_TIMEOUT", "25"))



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
    limit = TIMEOUT * (2 if day_no in track.T["slow_days"] else 1)
    t0 = time.time()
    with file_lock(path):
        path.write_text(code, encoding="utf-8")
        try:
            cmd = track.run_cmd(str(path))
        except FileNotFoundError as e:
            return {"output": str(e), "ok": False, "returncode": 127, "ms": 0, "timed_out": False, "hint": "Java is not installed yet."}
        out, rc, timed_out = sandbox.run(cmd, cwd=str(wd), stdin=stdin, timeout=limit, env=env)
    if timed_out:
        out += f"\n\n⏱ Stopped after {limit}s. Is there a loop that never ends ({'while (true)' if track.IS_JAVA else 'while True'} without break)?"
    ms = int((time.time() - t0) * 1000)
    if len(out) > MAX_OUT:
        out = out[:MAX_OUT] + "\n… output truncated …"
    hint = None
    if not stdin.strip():
        if "EOFError" in out:
            hint = "Your program called input(). Type the answers in the Input box (one line per input() call) and run again."
        elif "NoSuchElementException" in out and "Scanner" in code:
            hint = "Your program reads from the keyboard (Scanner). Type the answers in the Input box (one line per read) and run again."
    return {"output": out.rstrip(), "ok": rc == 0, "returncode": rc, "ms": ms, "timed_out": timed_out, "hint": hint}


_LAUNCH = "import sys, runpy; sys.path.insert(0, '.'); runpy.run_path(sys.argv[1], run_name='__main__')"


def run_blueprint_demo(bid: str) -> dict | None:
    """Run a blueprint's demo from a fresh private copy (so a demo can never touch the originals)."""
    bp = content.load_blueprints().get(bid)
    if not bp or not bp.get("demo"):
        return None
    src, dst = content.BP_DIR / bp["folder"], WORK / "blueprints" / bp["folder"]
    with file_lock(dst):
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.db", "*.class", "_out"))
        t0 = time.time()
        out, rc, timed_out = "", 0, False
        env = clean_env()
        if track.IS_JAVA:
            javac, java = track.jtool("javac"), track.jtool("java")
            if not javac or not java:
                return {"output": "No JDK found. Install JDK 21 (see java/SETUP.md).", "ok": False, "returncode": 127,
                        "ms": 0, "timed_out": False, "hint": "Java is not installed yet."}
            outdir = dst / "_out"
            shutil.rmtree(outdir, ignore_errors=True)
            outdir.mkdir(parents=True, exist_ok=True)
            srcs = sorted(p.name for p in dst.glob("*.java"))
            cout, crc, cto = sandbox.run([javac, "-encoding", "UTF-8", "-d", str(outdir), *srcs], cwd=str(dst), timeout=TIMEOUT * 2, env=env)
            if crc != 0:
                out, rc, timed_out = "Compile error:\n" + cout, crc, cto
            else:
                cls = bp["demo"].rsplit(".", 1)[0]
                out, rc, timed_out = sandbox.run([java, *track.JAVA_FLAGS, "-cp", str(outdir), cls], cwd=str(dst), timeout=TIMEOUT, env=env)
        else:
            out, rc, timed_out = sandbox.run([sys.executable, "-u", "-c", _LAUNCH, bp["demo"]], cwd=str(dst), timeout=TIMEOUT, env=env)
        if timed_out:
            out += f"\n\n⏱ Stopped after {TIMEOUT}s."
    if len(out) > MAX_OUT:
        out = out[:MAX_OUT] + "\n… output truncated …"
    hint = None
    if "ModuleNotFoundError" in out and ("fastapi" in out or "httpx" in out):
        hint = "This demo needs the Week-4 libraries: python -m pip install -r requirements-week4.txt"
    return {"output": out.rstrip(), "ok": rc == 0, "returncode": rc, "ms": int((time.time() - t0) * 1000),
            "timed_out": timed_out, "hint": hint}

def run_practice(day_no: int, code: str, stdin: str = "") -> dict:
    res = execute(code, day_no=day_no, filename=track.T["practice"], stdin=stdin)
    parsed = db.record_attempt(day_no, "practice", res["output"], res["ok"], res["ms"], res["timed_out"], len(code))
    return {**res, **parsed}


def run_examples(day_no: int, code: str, stdin: str = "") -> dict:
    res = execute(code, day_no=day_no, filename=track.T["examples"], stdin=stdin)
    db.record_attempt(day_no, "examples", "", res["ok"], res["ms"], res["timed_out"], len(code))
    return {**res, "results": [], "passed": None, "total": None}


def run_playground(code: str, stdin: str = "") -> dict:
    res = execute(code, day_no=None, filename=track.T["play"], stdin=stdin)
    db.record_attempt(0, "playground", "", res["ok"], res["ms"], res["timed_out"], len(code))
    return {**res, "results": [], "passed": None, "total": None}
