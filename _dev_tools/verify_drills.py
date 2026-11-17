"""Verify DRILLS.json files: structural lint + REAL execution of every snippet (Python interpreter / JDK 21).

    python _dev_tools/verify_drills.py                 # every day, both tracks
    python _dev_tools/verify_drills.py 1 2 5-7         # only these days
    python _dev_tools/verify_drills.py 4 --track java  # one track
    python _dev_tools/verify_drills.py 1-3 --fix       # rewrite stored outputs ('expected', 'output', buggy_runs.output) from real runs
    options: --jobs N (parallel runs, default 4), -v (list passing drills too), --lint-only (no execution)

What is executed
  predict  the code; real output must equal `expected`.
  parsons  the assembled program (and every `alternatives` order, and every other accepted blank answer): must exit 0 and
           print `output`; alternatives must print the same as the main order.
  fill     the code with the first answers, every other accepted answer, and every wrong option (a wrong option that gives the
           same output is reported: the blank would be ambiguous).
  bug      fixed_code must print `output`; the buggy code must really fail with `contains` (fails: true) or print the stated
           wrong `output` (fails: false); wrong fix options must not also repair the program.
  review   Python code must parse (ast); Java review code is not compiled.
Exit code 1 if anything fails. Needs no portal server and no database.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from portal import drills_core as core, sandbox, track  # noqa: E402

TIMEOUT = 25
HERE = Path(__file__).resolve().parent
CACHE_FILE = Path(tempfile.gettempdir()) / "drills_verify_cache_v1.json"
_cache: dict = {}
_disk: dict = {}
_lock = threading.Lock()
USE_CACHE = True


def env() -> dict:
    e = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONWARNINGS": "ignore"}
    for k in ("CURSOR_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        e.pop(k, None)
    return e


class JavaWorker:
    """One long-lived JVM running DrillRunner.java (compiles + runs many snippets without paying JVM start-up each time)."""

    def __init__(self):
        self.p = None
        self.lock = threading.Lock()

    def _start(self):
        self.p = subprocess.Popen(track.java_run_cmd(str(HERE / "DrillRunner.java")), stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env())

    def run(self, code: str, stdin: str) -> tuple[str, int]:
        c, s = code.encode("utf-8"), stdin.encode("utf-8")
        for attempt in (1, 2):
            try:
                if self.p is None or self.p.poll() is not None:
                    self._start()
                self.p.stdin.write(f"RUN {TIMEOUT * 1000} {len(c)} {len(s)}\n".encode() + c + s)
                self.p.stdin.flush()
                head = self.p.stdout.readline().decode().split()
                if len(head) != 3 or head[0] != "RES":
                    raise OSError("helper gave no answer")
                out = self.p.stdout.read(int(head[2])).decode("utf-8", "replace")
                return out, int(head[1])
            except (OSError, ValueError):
                self.p = None
                if attempt == 2:
                    return "the Java helper died (does the snippet call System.exit?)", 1
        return "", 1

    def close(self):
        if self.p and self.p.poll() is None:
            try:
                self.p.stdin.close()
                self.p.wait(timeout=5)
            except Exception:  # noqa: BLE001
                self.p.kill()


_workers: queue.Queue = queue.Queue()
_all_workers: list[JavaWorker] = []


def start_java_workers(n: int) -> None:
    for _ in range(max(1, n)):
        w = JavaWorker()
        _all_workers.append(w)
        _workers.put(w)


def run_java(code: str, stdin: str) -> tuple[str, int]:
    w = _workers.get()
    try:
        return w.run(code, stdin)
    finally:
        _workers.put(w)


def run_python(code: str, stdin: str) -> tuple[str, int]:
    tmp = tempfile.mkdtemp(prefix="drill_")
    try:
        f = Path(tmp) / "drill.py"
        f.write_text(code if code.endswith("\n") else code + "\n", encoding="utf-8")
        out, rc, timed = sandbox.run(track.python_run_cmd(str(f)), cwd=tmp, stdin=stdin, timeout=TIMEOUT, env=env())
        return out, (-9 if timed else rc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_code(java: bool, code: str, stdin: str = "") -> tuple[str, int]:
    key = hashlib.sha256(f"{java}|{stdin}|{code}".encode()).hexdigest()
    with _lock:
        if key in _cache:
            return _cache[key]
        if USE_CACHE and key in _disk:
            return tuple(_disk[key])  # type: ignore[return-value]
    try:
        res = run_java(code, stdin) if java else run_python(code, stdin)
    except FileNotFoundError as e:
        return (str(e), 127)
    with _lock:
        _cache[key] = res
        if res[1] not in (127, -9):
            _disk[key] = list(res)
    return res


def load_cache() -> None:
    try:
        _disk.update(json.loads(CACHE_FILE.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass


def save_cache() -> None:
    try:
        CACHE_FILE.write_text(json.dumps(_disk), encoding="utf-8")
    except OSError:
        pass

def canon(s: str) -> str:
    ls = [ln.rstrip() for ln in s.replace("\r\n", "\n").split("\n")]
    while ls and not ls[-1]:
        ls.pop()
    return "\n".join(ls)


def short(s: str, n: int = 160) -> str:
    s = s.strip().replace("\n", " / ")
    return s if len(s) <= n else s[:n] + "..."


def apply_option(code: str, d: dict, option: str) -> str | None:
    """Replace the bug line(s) of `code` with `option`, keeping each line's own indentation."""
    new = option.split("\n")
    if len(new) != len(d["bug_lines"]):
        return None
    ls = code.split("\n")
    for ln, text in zip(d["bug_lines"], new):
        ls[ln - 1] = re.match(r"\s*", ls[ln - 1]).group(0) + text.strip()
    return "\n".join(ls)


class Ctx:
    def __init__(self, java: bool, fix: bool, lint_only: bool):
        self.java, self.fix, self.lint_only = java, fix, lint_only

    def run(self, d: dict, code: str, stdin: str = "") -> tuple[str, int]:
        return run_code(self.java, core.program(d, code, self.java), stdin)


def v_predict(c: Ctx, d: dict, bad: list, fixes: dict):
    out, rc = c.run(d, d["code"], d.get("stdin", ""))
    if rc != 0:
        return bad.append(f"snippet exits with code {rc}: {short(out)} (predict snippets must run cleanly)")
    if canon(out) != canon(d["expected"]):
        fixes["expected"] = canon(out)
        if not c.fix:
            bad.append(f"expected output differs from the real output.\n      stored: {short(d['expected'])}\n      real:   {short(out)}")


def _same_output(c, d, code, want, label, bad, stdin="", fixable=False):
    out, rc = c.run(d, code, stdin)
    if rc != 0:
        bad.append(f"{label} exits with code {rc}: {short(out)}")
        return None
    if want is not None and canon(out) != canon(want) and not (fixable and c.fix):
        bad.append(f"{label} prints something else.\n      want: {short(want)}\n      got:  {short(out)}")
    return canon(out)


def _sync_output(d, out, bad_before, bad, fixes):
    """Record the real output for --fix when `output` is missing or stale."""
    if out is not None and canon(d.get("output", "\0")) != out:
        fixes["output"] = out


def v_parsons(c: Ctx, d: dict, bad: list, fixes: dict):
    if d.get("norun"):
        return
    n0 = len(bad)
    main = core.parsons_text(d)
    out = _same_output(c, d, main, d.get("output"), "assembled program", bad, fixable=True)
    if out is None:
        return
    _sync_output(d, out, n0, bad, fixes)
    for k, alt in enumerate(d.get("alternatives", [])):
        _same_output(c, d, core.parsons_text(d, order=alt), out, f"alternative order #{k + 1}", bad)
    for b, spec in enumerate(d.get("blanks", []) if d.get("faded") else []):
        for a in spec["answers"][1:]:
            vals = [x["answers"][0] for x in d["blanks"]]
            vals[b] = a
            _same_output(c, d, core.parsons_text(d, blanks=vals), out, f"blank {b + 1} alternative answer '{a}'", bad)
        for o in spec.get("options", []):
            if not core.blank_ok(spec, o):
                vals = [x["answers"][0] for x in d["blanks"]]
                vals[b] = o
                o2, rc = c.run(d, core.parsons_text(d, blanks=vals))
                if rc == 0 and canon(o2) == out:
                    bad.append(f"blank {b + 1}: wrong option '{o}' also gives the same output (ambiguous)")


def v_fill(c: Ctx, d: dict, bad: list, fixes: dict):
    if d.get("norun"):
        return
    n0 = len(bad)
    first = [b["answers"][0] for b in d["blanks"]]
    out = _same_output(c, d, core.fill_code(d["code"], first), d.get("output"), "completed program", bad, fixable=True)
    if out is None:
        return
    _sync_output(d, out, n0, bad, fixes)
    for b, spec in enumerate(d["blanks"]):
        for a in spec["answers"][1:]:
            vals = list(first)
            vals[b] = a
            _same_output(c, d, core.fill_code(d["code"], vals), out, f"blank {b + 1} alternative answer '{a}'", bad)
        for o in spec.get("options") or []:
            if not core.blank_ok(spec, o):
                vals = list(first)
                vals[b] = o
                o2, rc = c.run(d, core.fill_code(d["code"], vals))
                if rc == 0 and canon(o2) == out:
                    bad.append(f"blank {b + 1}: wrong option '{o}' also gives the same output (ambiguous)")


def v_bug(c: Ctx, d: dict, bad: list, fixes: dict):
    if d.get("norun"):
        return
    n0 = len(bad)
    stdin = d.get("stdin", "")
    out = _same_output(c, d, d["fixed_code"], d.get("output"), "fixed_code", bad, stdin, fixable=True)
    if out is not None:
        _sync_output(d, out, n0, bad, fixes)
    bo, brc = c.run(d, d["code"], stdin)
    br = d["buggy_runs"]
    if br["fails"]:
        if brc == 0:
            bad.append(f"buggy code runs fine but buggy_runs says it fails. Output: {short(bo)}")
        elif br["contains"] not in bo:
            bad.append(f"buggy code fails, but its output does not contain '{br['contains']}': {short(bo)}")
    else:
        if brc != 0:
            bad.append(f"buggy code crashes (exit {brc}) but buggy_runs says it only prints wrong output: {short(bo)}")
        elif canon(bo) != canon(br["output"]):
            fixes["buggy_runs.output"] = canon(bo)
            if not c.fix:
                bad.append(f"buggy_runs.output differs.\n      stored: {short(br['output'])}\n      real:   {short(bo)}")
        if out is not None and canon(bo) == out:
            bad.append("buggy code prints the same as fixed_code: the bug has no visible symptom")
    for i, opt in enumerate(d["options"]):
        if i == d["answer"] or out is None:
            continue
        code = apply_option(d["code"], d, opt)
        if code is None:
            continue
        o2, rc2 = c.run(d, code, stdin)
        if rc2 == 0 and canon(o2) == out:
            bad.append(f"wrong option #{i + 1} ('{short(opt, 50)}') also repairs the program (ambiguous)")


def v_review(c: Ctx, d: dict, bad: list, fixes: dict):
    if not c.java:
        try:
            ast.parse(d["code"])
        except SyntaxError as e:
            bad.append(f"review code does not parse: {e}")


VERIFY = {"predict": v_predict, "parsons": v_parsons, "fill": v_fill, "bug": v_bug, "review": v_review}


def prefill(drills: list[dict]) -> None:
    """With --fix, give missing stored outputs a placeholder so lint passes and the real run can replace it."""
    for d in drills:
        t = d.get("type")
        if t == "predict" and "expected" not in d:
            d["expected"] = "?"
        if t in ("parsons", "fill", "bug") and "output" not in d:
            d["output"] = "\0"


def one_drill(c: Ctx, d: dict) -> tuple[list[str], dict]:
    bad: list[str] = []
    fixes: dict = {}
    if c.lint_only:
        return bad, fixes
    try:
        VERIFY[d["type"]](c, d, bad, fixes)
    except Exception as e:  # noqa: BLE001
        bad.append(f"verifier crashed: {type(e).__name__}: {e}")
    return bad, fixes


def apply_fixes(raw: dict, d: dict, fixes: dict) -> None:
    for k, v in fixes.items():
        parts = k.split(".")
        tgt = raw
        for p in parts[:-1]:
            tgt = tgt[p]
        old = tgt.get(parts[-1])
        tgt[parts[-1]] = v.split("\n") if (isinstance(old, list) or (old is None and "\n" in v)) else v


def do_file(path: Path, day: int, java: bool, a, pool):
    """Lint the file, queue its drills on the pool, and return a function that waits for them and reports."""
    msgs: list[str] = []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        why = str(e)                                       # `e` is deleted when this block ends, so keep the text
        return lambda: (0, 1, [f"LINT  invalid JSON: {why}"])
    doc = core.load_doc(path) or {}
    drills = doc.get("drills", [])
    if a.fix:
        prefill(drills)
    problems = core.lint_doc({**doc, "drills": drills}, day, java)
    for p in problems:
        msgs.append(f"LINT  {p}")
    c = Ctx(java, a.fix, a.lint_only)
    futs = []
    for d in drills:
        if core.lint_drill(d, java) or d.get("type") not in core.TYPES:
            continue                                   # lint errors already reported; do not run broken drills
        futs.append((d, pool.submit(one_drill, c, d)))
    return lambda: _finish(path, raw, drills, futs, msgs, a)


def _finish(path, raw, drills, futs, msgs, a):
    ok_ids = []
    changed = False
    for d, f in futs:
        bad, fixes = f.result()
        if bad:
            for b in bad:
                msgs.append(f"FAIL  {d['id']} ({d['type']}): {b}")
        else:
            ok_ids.append(d["id"])
        if fixes and a.fix:
            raw_d = next(r for r in raw["drills"] if r.get("id") == d["id"])
            apply_fixes(raw_d, d, fixes)
            changed = True
            msgs.append(f"FIXED {d['id']}: rewrote {', '.join(fixes)} from the real run")
    if changed:
        path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if a.v:
        msgs += [f"ok    {i}" for i in ok_ids]
    fails = sum(1 for m in msgs if m.startswith(("LINT", "FAIL")))
    return len(drills), fails, msgs


def parse_days(items: list[str]) -> list[int]:
    out: list[int] = []
    for it in items:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", it)
        if not m:
            raise SystemExit(f"bad day '{it}' (use 3 or 2-5)")
        lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
        out += range(lo, hi + 1)
    return sorted(set(out))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("days", nargs="*", help="day numbers or ranges (default: all days that have a DRILLS.json)")
    ap.add_argument("--track", choices=("python", "java", "both"), default="both")
    ap.add_argument("--fix", action="store_true", help="rewrite stored outputs from real runs")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--lint-only", action="store_true")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    want = parse_days(a.days) if a.days else list(range(1, 31))
    total = bad = files = 0
    tracks = ["python", "java"] if a.track == "both" else [a.track]
    if "java" in tracks and not a.lint_only:
        start_java_workers(a.jobs)
    if not a.lint_only:
        load_cache()
    pool = ThreadPoolExecutor(max_workers=max(1, a.jobs))
    waiting = []
    for tr in tracks:
        java = tr == "java"
        days_dir = ROOT / "java" / "days" if java else ROOT / "days"
        for n in want:
            f = core.find_file(days_dir, n)
            if f:
                waiting.append((tr, n, f, do_file(f, n, java, a, pool)))
    for tr, n, f, finish in waiting:                      # report in order while the pool keeps working
        count, fails, msgs = finish()
        files += 1
        total += count
        bad += fails
        print(f"[{tr:6}] day {n:02d}: {count} drills, {'OK' if not fails else str(fails) + ' PROBLEM(S)'}")
        for m in msgs:
            print("    " + m)
    pool.shutdown()
    for w in _all_workers:
        w.close()
    if not a.lint_only:
        save_cache()
    print(f"\n{files} file(s), {total} drills, {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
