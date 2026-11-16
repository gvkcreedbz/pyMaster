"""Pure logic for the 'struggle' extension: error-type extraction, the five detectors, and exercise-region extraction.
No database access here (ex_struggle.py loads the history and passes it in), so every rule can be tested with made-up data.
"""
from __future__ import annotations
import ast
import re
from datetime import datetime, timedelta
from . import track

REPEAT_N = 3            # same failure this many runs in a row with the same code
HINT_N = 3              # hint / solution views ...
HINT_WINDOW_MIN = 10    # ... inside this many minutes with no run in between
IDLE_MIN = 8            # active minutes since a failed run without running again
THRASH_RUNS = 8         # runs ...
THRASH_WINDOW_S = 180   # ... inside this many seconds with an unchanged pass count
PRODUCTIVE_MIN_RUNS = 3
PRODUCTIVE_WINDOW_MIN = 45
COOLDOWN_MIN = 20
PRIORITY = ["hint_spam", "repeat_failure", "thrash", "idle_after_failure", "productive_struggle"]

# ---- error type ------------------------------------------------------------------------------------
_PY_ERR = re.compile(r"^\s*(?:[\w.]+\.)?([A-Z]\w*(?:Error|Exception|Exit))\b")
_JAVA_EXC = re.compile(r'Exception in thread "[^"]*"\s+([\w.$]+)')
_JAVA_COMPILE = re.compile(r":\d+:\s*error:\s*(.+?)\s*$")
_CHECK_CRASH = re.compile(r"\(got ['\"]?(?:[\w.]+\.)?([A-Z]\w*(?:Error|Exception))\b:")


def error_type(output: str, ok: bool) -> str | None:
    """A short label for what went wrong in a run, derived from its stored output (None when nothing crashed)."""
    out = output or ""
    if not ok:
        if "Stopped after" in out:
            return "Timeout"
        m = _JAVA_EXC.search(out)
        if m:
            return m.group(1).rsplit(".", 1)[-1]
        for line in reversed(out.splitlines()):
            m = _JAVA_COMPILE.search(line)
            if m and track.IS_JAVA:
                return "compile: " + re.sub(r"\s+", " ", m.group(1))[:40]
        if not track.IS_JAVA:
            for line in reversed(out.splitlines()):
                m = _PY_ERR.match(line)
                if m:
                    return m.group(1)
    found = _CHECK_CRASH.findall(out)           # a check that crashed: "[FAIL] x  (got 'TypeError: ...', want ...)"
    if found:
        return max(set(found), key=found.count)
    return None


# ---- detectors ------------------------------------------------------------------------------------------
def failed(r: dict) -> bool:
    if r.get("total"):
        return not (r["ok"] and r["passed"] == r["total"])
    return not r["ok"]


def _mins(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 60


def _short(s: str, n: int = 120) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def next_hint(ctx: dict) -> int | None:
    seen = ctx.get("hints_seen") or set()
    for i in range(1, int(ctx.get("hints_total") or 0) + 1):
        if i not in seen:
            return i
    return None


def tutor_question(ctx: dict, check: dict | None, extra: str = "") -> str:
    ex = ctx.get("exercise") or {}
    where = f"Day {ctx['day']}" + (f", exercise {ex['id']} ({ex['title']})" if ex.get("id") else "")
    what = ""
    if check:
        what = f' The check "{check["id"]} {check["name"]}" fails' + (f" {_short(check.get('detail', ''), 100)}" if check.get("detail") else "") + "."
    q = f"I am stuck on {where} in {track.T['short']}.{what}{extra} Without giving me the full answer, what should I look at first?"
    return q[:600]


def _fail_check(r: dict, only: tuple[str, str] | None = None) -> dict | None:
    for f in r["fails"]:
        if only is None or (f["id"], f["name"]) == only:
            return f
    return None


def _mk(kind: str, severity: int, ctx: dict, evidence: str, text: str, action: str | None, alt: str | None = None,
        positive: bool = False, check: dict | None = None) -> dict:
    return {"kind": kind, "severity": severity, "day": ctx["day"], "evidence": evidence, "nudge_text": text,
            "suggested_action": action, "alt_action": alt, "positive": positive,
            "check": {"id": check["id"], "name": check["name"]} if check else None}


def _hint_action(ctx: dict, check: dict | None) -> tuple[str, str]:
    """(primary, alternative) for 'look at the failing check' situations."""
    nh = next_hint(ctx)
    ask = "ask_tutor:" + tutor_question(ctx, check)
    return (f"hint:{nh}", ask) if nh else (ask, "visualize")


def d_repeat(runs: list[dict], ctx: dict) -> dict | None:
    """Same error type or same failing check >= 3 runs in a row, and the code did not change in between."""
    if len(runs) < REPEAT_N:
        return None
    tail = runs[-REPEAT_N:]
    if not all(failed(r) for r in tail) or len({r["codekey"] for r in tail}) != 1:
        return None
    if len({r["passed"] for r in tail}) != 1:           # a moving score proves the code changed, whatever its length says
        return None
    errs = {r["err"] for r in tail}
    if len(errs) == 1 and None not in errs:
        n = 0
        for r in reversed(runs):
            if failed(r) and r["err"] == tail[-1]["err"] and r["codekey"] == tail[-1]["codekey"]:
                n += 1
            else:
                break
        err = tail[-1]["err"]
        check = _fail_check(tail[-1])
        return _mk("repeat_failure", 3 if n >= 5 else 2, ctx, f"{n} runs in a row, same code, same error: {err}",
                   f"You have run the same code {n} times and got {err} each time. Running it again will give the same result. "
                   "Step through the code to see where it goes wrong, or change one thing before you run again.",
                   "visualize", "ask_tutor:" + tutor_question(ctx, check, f" My program stops with {err}."), check=check)
    common = None
    for r in tail:
        keys = {(f["id"], f["name"]) for f in r["fails"]}
        common = keys if common is None else common & keys
    if not common:
        return None
    key = sorted(common)[0]
    n = 0
    for r in reversed(runs):
        if failed(r) and key in {(f["id"], f["name"]) for f in r["fails"]} and r["codekey"] == tail[-1]["codekey"]:
            n += 1
        else:
            break
    check = _fail_check(tail[-1], key)
    primary, alt = _hint_action(ctx, check)
    return _mk("repeat_failure", 3 if n >= 5 else 2, ctx, f"{n} runs in a row, same code, same failing check: {key[0]} {key[1]}",
               f'The check "{key[1]}" has failed {n} runs in a row and your code has not changed. Running again will not fix it. '
               "Read what it expected, change one thing, then run.", primary, alt, check=check)


def d_hint_spam(runs: list[dict], ctx: dict) -> dict | None:
    """>= 3 hint or solution views within 10 minutes with no run in between."""
    now: datetime = ctx["now"]
    last_run = ctx.get("last_run_any_ts") or (runs[-1]["ts"] if runs else None)
    views = [v for v in ctx.get("views", []) if last_run is None or v["ts"] > last_run]
    if len(views) < HINT_N:
        return None
    tail = views[-HINT_N:]
    if _mins(tail[0]["ts"], tail[-1]["ts"]) > HINT_WINDOW_MIN or _mins(tail[-1]["ts"], now) > HINT_WINDOW_MIN:
        return None
    sol = any(v["type"] == "solution_view" for v in tail)
    span = max(1, round(_mins(tail[0]["ts"], tail[-1]["ts"])))
    check = _fail_check(runs[-1]) if runs else None
    what = "hints and the solution" if sol else "hints"
    return _mk("hint_spam", 3 if sol else 2, ctx, f"{len(tail)} {what} opened in {span} min with no run in between",
               f"You opened {len(tail)} {what} in {span} min without running your code. They work best one at a time: read one, "
               "try it, run, then decide. Want to talk it through with the tutor instead?",
               "ask_tutor:" + tutor_question(ctx, check, " I already looked at the hints but I am not sure how to use them."),
               "easier_step", check=check)


def d_thrash(runs: list[dict], ctx: dict) -> dict | None:
    """>= 8 runs within 3 minutes and the pass count never moved."""
    if len(runs) < THRASH_RUNS or not failed(runs[-1]) or _mins(runs[-1]["ts"], ctx["now"]) > 10:
        return None
    win = [r for r in runs if (runs[-1]["ts"] - r["ts"]).total_seconds() <= THRASH_WINDOW_S]
    if len(win) < THRASH_RUNS or any(r["passed"] is None for r in win):
        return None
    if len({(r["passed"], r["total"]) for r in win}) != 1:
        return None
    secs = max(1, round((win[-1]["ts"] - win[0]["ts"]).total_seconds()))
    p, t = win[-1]["passed"], win[-1]["total"]
    check = _fail_check(win[-1])
    return _mk("thrash", 2, ctx, f"{len(win)} runs in {secs}s, still {p}/{t}",
               f"{len(win)} runs in {secs} seconds and still {p}/{t}. Quick re-runs rarely help. Pause, pick one failing check "
               "and watch what your code does with it.", "visualize", "take_a_break", check=check)


def d_idle(runs: list[dict], ctx: dict) -> dict | None:
    """The page was active for >= 8 minutes after a failed run and nothing was run since."""
    if not runs or not failed(runs[-1]) or ctx.get("editing"):
        return None
    last = runs[-1]
    since = ctx.get("active_since_last_run_s")
    if since is None:                                   # no snapshot of the active clock: fall back to wall time + page alive
        since = _mins(last["ts"], ctx["now"]) * 60 if ctx.get("page_alive") else 0
    if since < IDLE_MIN * 60:
        return None
    mins = int(since // 60)
    check = _fail_check(last)
    primary = "easier_step"
    nh = next_hint(ctx)
    alt = f"hint:{nh}" if nh else "ask_tutor:" + tutor_question(ctx, check)
    return _mk("idle_after_failure", 1, ctx, f"{mins} active min since the last run, which failed",
               f"It has been {mins} min since your last run and it failed. If you are stuck, a smaller first step often helps.",
               primary, alt, check=check)


def d_productive(runs: list[dict], ctx: dict) -> dict | None:
    """Pass count rising over the last few runs: say so."""
    now: datetime = ctx["now"]
    if len(runs) < PRODUCTIVE_MIN_RUNS or _mins(runs[-1]["ts"], now) > COOLDOWN_MIN:
        return None
    last = runs[-1]
    if not last.get("total") or last["passed"] is None or not failed(last):
        return None
    win = [r for r in runs if _mins(r["ts"], now) <= PRODUCTIVE_WINDOW_MIN and r["total"] == last["total"] and r["passed"] is not None]
    if len(win) < PRODUCTIVE_MIN_RUNS or win[-1] is not last or win[-1]["passed"] <= win[0]["passed"]:
        return None
    if len(win) >= 2 and win[-1]["passed"] <= win[-2]["passed"]:     # the newest run must be the one that improved
        return None
    a, b, t, n = win[0]["passed"], win[-1]["passed"], last["total"], len(win)
    return _mk("productive_struggle", 1, ctx, f"{a}/{t} to {b}/{t} in {n} runs",
               f"You went from {a}/{t} to {b}/{t} in {n} tries. That is how learning looks. Keep going.", None, None, positive=True)


DETECTORS = {"hint_spam": d_hint_spam, "repeat_failure": d_repeat, "thrash": d_thrash,
             "idle_after_failure": d_idle, "productive_struggle": d_productive}


def detect(runs: list[dict], ctx: dict) -> list[dict]:
    """All detections for this moment, highest priority first. `runs` are this day's practice runs (oldest first)."""
    out = []
    for kind in PRIORITY:
        d = DETECTORS[kind](runs, ctx)
        if d:
            out.append(d)
    return out


# ---- exercise region extraction ----------------------------------------------------------------------------
_MARK = re.compile(r"AUTO-CHECKER")


def _headers(lines: list[str]) -> list[tuple[int, str]]:
    return [(i, m.group(1)) for i, ln in enumerate(lines) if (m := track.EX_HEADER.match(ln))]


def region(code: str, ex_id: str) -> tuple[str, str] | None:
    """(preamble imports, the learner's code for one exercise: header comments through its last line)."""
    lines = code.splitlines()
    hs = _headers(lines)
    idx = next((k for k, (_, i) in enumerate(hs) if i == ex_id), None)
    if idx is None:
        return None
    start = hs[idx][0]
    end = hs[idx + 1][0] if idx + 1 < len(hs) else next((i for i, ln in enumerate(lines) if i > start and _MARK.search(ln)), len(lines))
    while end > start + 1 and (track.SEPARATOR.match(lines[end - 1]) or not lines[end - 1].strip()):
        end -= 1                                       # the dashed line above the next header belongs to that header
    pre_end = hs[0][0]
    imp = re.compile(r"^import\s" if track.IS_JAVA else r"^(import|from)\s")
    pre = "\n".join(ln for ln in lines[:pre_end] if imp.match(ln))
    return pre, "\n".join(lines[start:end]).rstrip() + "\n"


def _py_expr(code: str, label: str) -> str | None:
    lines = code.splitlines()
    pat = re.compile(r"^\s*check\(\s*[\"']" + re.escape(label) + r"[\"']")
    for i, ln in enumerate(lines):
        if not pat.match(ln):
            continue
        for j in range(i, min(i + 8, len(lines))):
            try:
                tree = ast.parse("\n".join(l.strip() if k else l.lstrip() for k, l in enumerate(lines[i:j + 1])))
            except SyntaxError:
                continue
            call = tree.body[0].value if tree.body and isinstance(tree.body[0], ast.Expr) else None
            if isinstance(call, ast.Call) and len(call.args) >= 2 and isinstance(call.args[1], ast.Lambda):
                return ast.unparse(call.args[1].body)
            return None
    return None


def _java_expr(code: str, label: str) -> str | None:
    m = re.search(r'Checker\.check\(\s*"' + re.escape(label) + r'"\s*,\s*\(\)\s*->\s*', code)
    if not m:
        return None
    i, depth, buf, quote = m.end(), 0, [], None
    if code[i:i + 1] == "{":
        return None                                    # a block lambda: not worth rebuilding
    while i < len(code):
        ch = code[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and i + 1 < len(code):
                buf.append(code[i + 1]); i += 1
            elif ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch; buf.append(ch)
        elif ch in "([{":
            depth += 1; buf.append(ch)
        elif ch in ")]}":
            if depth == 0:
                break
            depth -= 1; buf.append(ch)
        elif ch == "," and depth == 0:
            break
        else:
            buf.append(ch)
        i += 1
    expr = "".join(buf).strip()
    return expr or None


def isolate(code: str, ex_id: str, check_name: str | None = None) -> dict:
    """Try to cut out ONE exercise and add a one-line call so the visualizer traces only that.
    Returns {mode: 'region'|'whole', code, note}."""
    whole = {"mode": "whole", "code": code, "note": "Could not isolate that exercise, so the whole practice file is opened. "
             "It runs every check, so the step-by-step trace can be long."}
    reg = region(code, ex_id) if ex_id else None
    if not reg:
        return whole
    pre, body = reg
    labels = [f"{ex_id} {check_name}"] if check_name else []
    labels += [m.group(1) for m in re.finditer(r'check\(\s*"(' + re.escape(ex_id) + r'\b[^"]*)"', code)]
    expr = None
    for label in labels:
        expr = (_java_expr if track.IS_JAVA else _py_expr)(code, label)
        if expr:
            break
    if not expr:
        return whole
    if track.IS_JAVA:
        text = (pre + "\n\n" if pre else "") + "class Practice {\n" + "\n".join("    " + ln if ln.strip() else ln for ln in body.splitlines()) + \
            f"\n    public static void main(String[] args) {{\n        System.out.println(java.util.Arrays.deepToString(new Object[]{{ {expr} }}));\n    }}\n}}\n"
    else:
        text = (pre + "\n\n" if pre else "") + body + f"\nprint({expr})\n"
    return {"mode": "region", "code": text, "note": f"Tracing only your code for {ex_id} with one call taken from its check: {expr[:80]}"}
