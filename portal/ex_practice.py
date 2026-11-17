"""Practice sessions: mixed, unlabeled problems drawn from every day you have reached (an extension).

Idea (borrowed from the learning-science literature and from LearnHarness' "practice" mode): knowing a topic while the
lesson names it is easy; the real skill is recognising WHICH idea a problem needs when nothing tells you. So a practice
session
  * mixes problems from all the days you have opened (interleaving), never showing the day, title or concept up front;
  * adapts the difficulty: up after 3 good answers in a row, down after 2 misses, so it stays hard but doable;
  * offers a ladder of 3 hints, smallest first, and records which ones you used;
  * lets you write your thinking and rate your confidence, then compares confidence with what actually happened;
  * reveals the model solution only when the problem ends.
The problem bank is the verified drills (DRILLS.json, see portal/ex_drills.py); nothing here needs an AI.

Endpoints: POST /api/practice/next  POST /api/practice/{pid}/hint  POST /api/practice/{pid}/check
           POST /api/practice/{pid}/giveup  GET /api/practice/summary  POST /api/practice/end
"""
from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import content, db, drills_core as core, ex_drills, track

router = APIRouter()

TYPE_BASE = {"fill": 1, "predict": 2, "parsons": 2, "bug": 3, "review": 4}     # how demanding each kind of problem is
MAX_LEVEL = 5
PID_RE = re.compile(r"^(\d{1,2})~([A-Za-z0-9][A-Za-z0-9_-]{0,39})$")
SID_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
MAX_THINK = 1500
HINT_STEPS = 3


def setup() -> None:
    db.run("CREATE TABLE IF NOT EXISTS practice_attempts(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, date TEXT, "
           "psession TEXT, day_no INTEGER, drill_id TEXT, type TEXT, level INTEGER, ok INTEGER, score REAL, "
           "tries INTEGER, hints INTEGER, gave_up INTEGER, confidence INTEGER, thinking TEXT, seconds REAL)")
    db.run("CREATE INDEX IF NOT EXISTS ix_practice_day ON practice_attempts(day_no, drill_id)")


# ---- the problem bank ---------------------------------------------------------------------------------------------
def reached_days() -> list[int]:
    """Days the learner has opened (any), or days 1-3 for a brand-new learner. Never more than the course has."""
    rows = db.rows("SELECT day_no FROM day_state WHERE opens > 0 OR status = 'done'")
    days = sorted({r["day_no"] for r in rows if r["day_no"]})
    have = [n for n in sorted(content.load_days()) if core.find_file(track.DAYS_DIR, n)]
    pick = [n for n in days if n in have] or [n for n in have if n <= 3]
    return pick


def bank(days: list[int]) -> list[dict]:
    """Every valid drill of the given days, with its difficulty level 1..5."""
    out = []
    for n in days:
        for did, d in ex_drills._drills(n).items():
            lvl = TYPE_BASE.get(d["type"], 2) + (1 if n >= 12 else 0) + (1 if n >= 22 else 0)
            out.append({"day": n, "id": did, "type": d["type"], "level": min(MAX_LEVEL, lvl), "d": d})
    return out


def pid_of(day: int, did: str) -> str:
    return f"{day}~{did}"


def parse_pid(pid: str) -> tuple[int, str]:
    m = PID_RE.match(pid or "")
    if not m:
        raise HTTPException(404, "no such problem")
    return int(m.group(1)), m.group(2)


def problem(pid: str) -> dict:
    day, did = parse_pid(pid)
    d = ex_drills._drills(day).get(did) if content.day(day) else None
    if not d:
        raise HTTPException(404, "no such problem")
    return d


# ---- adaptive difficulty -------------------------------------------------------------------------------------------------
def target_level(rows: list[dict]) -> int:
    """Walk this session's results in order: 3 good answers in a row go up a level, 2 misses in a row go down one."""
    lvl, good, bad = 2, 0, 0
    for r in rows:
        if r["ok"] and r["hints"] <= 1 and r["tries"] <= 2 and not r["gave_up"]:
            good, bad = good + 1, 0
        elif r["ok"]:
            good, bad = 0, 0                                  # right, but only with help: stay
        else:
            good, bad = 0, bad + 1
        if good >= 3:
            lvl, good = min(MAX_LEVEL, lvl + 1), 0
        if bad >= 2:
            lvl, bad = max(1, lvl - 1), 0
    return lvl


def pick_next(days: list[int], psession: str, seed: str | None = None) -> dict | None:
    items = bank(days)
    if not items:
        return None
    mine = db.rows("SELECT * FROM practice_attempts WHERE psession=? ORDER BY id", (psession,))
    want = target_level(mine)
    seen_here = {(r["day_no"], r["drill_id"]) for r in mine}
    hist: dict[tuple, dict] = defaultdict(lambda: {"n": 0, "miss": 0, "last": ""})
    for r in db.rows("SELECT day_no, drill_id, ok, ts FROM practice_attempts"):
        h = hist[(r["day_no"], r["drill_id"])]
        h["n"] += 1
        h["miss"] += 0 if r["ok"] else 1
        h["last"] = max(h["last"], r["ts"] or "")
    last = mine[-1] if mine else None
    rng = random.Random(seed or f"{psession}|{len(mine)}")
    scored = []
    for it in items:
        key = (it["day"], it["id"])
        if key in seen_here:
            continue                                          # no repeats inside one session
        h = hist.get(key)
        s = -abs(it["level"] - want) * 2.0                    # stay near the target level
        if h:
            s += 1.5 * min(h["miss"], 2)                      # problems you missed before come back
            s -= 0.6 * h["n"]                                 # ...and ones you know well come back less
        else:
            s += 0.8                                          # never seen: slightly preferred
        if last and it["day"] == last["day_no"]:
            s -= 1.5                                          # interleave: avoid the same day twice in a row
        if last and it["type"] == last["type"]:
            s -= 1.0                                          # ...and the same kind of problem
        scored.append((s + rng.random() * 0.5, it))
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    pick = scored[0][1]
    return {**pick, "target": want, "answered": len(mine)}


# ---- hints: three steps, smallest first, never the whole answer -------------------------------------------------------------
def _ordinal_lines(n: int) -> str:
    return f"{n} line{'s' if n != 1 else ''}"


def hint_for(d: dict, step: int) -> str:
    """Step 1 names the area, step 2 gives the author's nudge or a guiding question, step 3 narrows the search."""
    t = d["type"]
    if step == 1:
        cs = d.get("concepts") or []
        return "This is about: " + ", ".join(cs[:3]) + "." if cs else "Think about what the program does first, line by line."
    if step == 2:
        if d.get("hint"):
            return str(d["hint"])
        return {"parsons": "Decide what must happen first, then what depends on it. Lines that do not fit the story are traps.",
                "fill": "Read the line out loud with the blank in it. What does the next line need from it?",
                "predict": "Keep a small table of the variables and update it after every line, like the computer does.",
                "bug": "Run the program in your head. Where does the first thing differ from what the prompt says it should do?",
                "review": "For each item ask: could this really go wrong, and what exact input would show it?"}[t]
    if t == "parsons":
        return f"The first line of the program is:  {d['lines'][0]}"
    if t == "fill":
        return "The first blank is:  " + str(d["blanks"][0]["answers"][0])
    if t == "predict":
        exp = core._lines_of(d["expected"])
        return f"It prints {_ordinal_lines(len(exp))}, and the first one is:  {exp[0]}"
    if t == "bug":
        n = len(core.as_text(d["code"]).split("\n"))
        b = d["bug_lines"][0]
        lo, hi = max(1, b - 1), min(n, b + 1)
        return f"Look at lines {lo} to {hi}."
    first = d["issues"][0]
    return "One real problem: " + first["text"]


# ---- API -------------------------------------------------------------------------------------------------------------------
def _sid(v) -> str | None:
    return v if isinstance(v, str) and SID_RE.match(v) else None


class NextIn(BaseModel):
    psession: str
    session_id: str | None = None
    scope: str = "reached"          # reached | all


@router.post("/api/practice/next")
def next_problem(b: NextIn):
    if not SID_RE.match(b.psession or ""):
        raise HTTPException(400, "bad practice session id")
    if b.scope not in ("reached", "all"):
        raise HTTPException(400, "scope must be reached or all")
    days = reached_days() if b.scope == "reached" else [n for n in sorted(content.load_days()) if core.find_file(track.DAYS_DIR, n)]
    pick = pick_next(days, b.psession)
    if not pick:
        return {"done": True, "reason": "You have been through every problem available in this scope. Open more days, or choose 'all days'."}
    d, n = pick["d"], pick["day"]
    sid = _sid(b.session_id) or "anon"
    view = core.public_view(d, core.Tok(ex_drills._secret, n, pick["id"]), f"{sid}|{b.psession}|{n}|{pick['id']}", track.IS_JAVA)
    for k in ("title", "concepts", "hint"):                       # the point of practice: nothing names the idea
        view.pop(k, None)
    view["viz"] = False
    return {"done": False, "pid": pid_of(n, pick["id"]), "problem": view, "level": pick["level"], "target": pick["target"],
            "number": pick["answered"] + 1, "pool": len(bank(days)), "days_in_scope": len(days), "hint_steps": HINT_STEPS}


class HintIn(BaseModel):
    step: int


@router.post("/api/practice/{pid}/hint")
def hint(pid: str, b: HintIn):
    d = problem(pid)
    if not 1 <= b.step <= HINT_STEPS:
        raise HTTPException(400, f"step must be 1 to {HINT_STEPS}")
    return {"step": b.step, "text": hint_for(d, b.step), "more": b.step < HINT_STEPS}


class CheckIn(BaseModel):
    psession: str
    answer: Any = None
    session_id: str | None = None
    thinking: str = ""
    confidence: int | None = None      # 1 not sure, 2 fairly sure, 3 certain
    hints: int = 0
    tries: int = 1
    seconds: float | None = None


def _record(pid: str, d: dict, b, ok: bool, score: float, gave_up: bool) -> None:
    day, did = parse_pid(pid)
    lvl = next((x["level"] for x in bank([day]) if x["id"] == did), 2)
    think = (b.thinking or "")[:MAX_THINK]
    conf = b.confidence if b.confidence in (1, 2, 3) else None
    db.run("INSERT INTO practice_attempts(ts,date,psession,day_no,drill_id,type,level,ok,score,tries,hints,gave_up,confidence,thinking,seconds) "
           "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
           (db.now_iso(), db.today(), b.psession, day, did, d["type"], lvl, int(ok), score, max(1, min(b.tries, 50)),
            max(0, min(b.hints, HINT_STEPS)), int(gave_up), conf, think, b.seconds if b.seconds and 0 <= b.seconds < 36000 else None))
    if ok and not gave_up:                                         # counts toward XP exactly like a drill
        db.log_event(_sid(b.session_id), "drill_check", day, {"drill": did, "type": d["type"], "ok": True, "score": score, "practice": True})


@router.post("/api/practice/{pid}/check")
def check(pid: str, b: CheckIn):
    d = problem(pid)
    day, did = parse_pid(pid)
    if not SID_RE.match(b.psession or ""):
        raise HTTPException(400, "bad practice session id")
    if len(json.dumps(b.answer, ensure_ascii=False)) > ex_drills.MAX_BODY:
        raise HTTPException(413, "answer too large")
    # public_view() hands out tokens from Tok(secret, day, drill); check() rebuilds the same Tok, so answers line up.
    try:
        ok, score, fb = core.check(d, b.answer, core.Tok(ex_drills._secret, day, did), track.IS_JAVA)
    except core.BadAnswer as e:
        raise HTTPException(422, str(e)) from None
    score = round(float(score), 2)
    res: dict[str, Any] = {"ok": ok, "score": score, "feedback": fb, "type": d["type"]}
    if ok:
        res.update(solution=core.solution_view(d, track.IS_JAVA), explain=d["explain"], concepts=d.get("concepts", []), day=day,
                   title=d["title"])
        _record(pid, d, b, True, score, False)
    return res


class GiveUpIn(BaseModel):
    psession: str
    session_id: str | None = None
    thinking: str = ""
    confidence: int | None = None
    hints: int = 0
    tries: int = 1
    seconds: float | None = None


@router.post("/api/practice/{pid}/giveup")
def giveup(pid: str, b: GiveUpIn):
    d = problem(pid)
    day, _did = parse_pid(pid)
    if not SID_RE.match(b.psession or ""):
        raise HTTPException(400, "bad practice session id")
    _record(pid, d, b, False, 0.0, True)
    return {"ok": False, "solution": core.solution_view(d, track.IS_JAVA), "explain": d["explain"],
            "concepts": d.get("concepts", []), "day": day, "title": d["title"], "type": d["type"]}


# ---- summaries -------------------------------------------------------------------------------------------------------------
CONF_NAME = {1: "not sure", 2: "fairly sure", 3: "certain"}


def calibration(rows: list[dict]) -> dict:
    """How well confidence predicted correctness. 'Certain and wrong' is the signal worth a second look."""
    by = {c: {"label": CONF_NAME[c], "n": 0, "right": 0} for c in (1, 2, 3)}
    for r in rows:
        c = r["confidence"]
        if c in by:
            by[c]["n"] += 1
            by[c]["right"] += 1 if (r["ok"] and not r["gave_up"]) else 0
    for v in by.values():
        v["pct"] = round(100 * v["right"] / v["n"]) if v["n"] else None
    wrong_sure = [r for r in rows if r["confidence"] == 3 and not (r["ok"] and not r["gave_up"])]
    guess_right = [r for r in rows if r["confidence"] == 1 and r["ok"] and not r["gave_up"]]
    rated = sum(v["n"] for v in by.values())
    note = None
    if rated >= 6:
        c3, c1 = by[3]["pct"], by[1]["pct"]
        if c3 is not None and c1 is not None and c3 + 10 < c1:
            note = "Your 'certain' answers are right less often than your 'not sure' ones: slow down on the ones that feel obvious."
        elif c3 is not None and c3 >= 80:
            note = "When you say 'certain' you are usually right. Your confidence is a good guide."
    return {"levels": [{"c": c, **by[c]} for c in (1, 2, 3)], "rated": rated, "certain_and_wrong": len(wrong_sure),
            "lucky_guesses": len(guess_right), "note": note}


@router.get("/api/practice/summary")
def summary(psession: str | None = None):
    rows = db.rows("SELECT * FROM practice_attempts ORDER BY id")
    mine = [r for r in rows if psession and r["psession"] == psession]

    def stats(rs: list[dict]) -> dict:
        n = len(rs)
        solved = [r for r in rs if r["ok"] and not r["gave_up"]]
        return {"problems": n, "solved": len(solved), "first_try": sum(1 for r in solved if r["tries"] == 1 and r["hints"] == 0),
                "with_hints": sum(1 for r in rs if r["hints"] > 0), "gave_up": sum(1 for r in rs if r["gave_up"]),
                "avg_hints": round(sum(r["hints"] for r in rs) / n, 1) if n else 0}
    cons = Counter()
    for r in rows:
        if not (r["ok"] and not r["gave_up"]) or r["hints"] >= 2:
            d = ex_drills._drills(r["day_no"]).get(r["drill_id"])
            for c in (d or {}).get("concepts", [])[:2]:
                cons[(r["day_no"], c)] += 1
    weak = [{"day": k[0], "concept": k[1], "misses": v} for k, v in cons.most_common(6)]
    sessions = len({r["psession"] for r in rows})
    return {"all": stats(rows), "session": stats(mine), "sessions": sessions, "calibration": calibration(rows),
            "weak": weak, "reached_days": len(reached_days()), "level": target_level([r for r in rows if psession and r["psession"] == psession]) if psession else None,
            "review": [{"day": r["day_no"], "drill": r["drill_id"], "type": r["type"], "ok": bool(r["ok"] and not r["gave_up"]),
                        "hints": r["hints"], "confidence": r["confidence"]} for r in mine][-20:]}


class EndIn(BaseModel):
    psession: str
    session_id: str | None = None


@router.post("/api/practice/end")
def end(b: EndIn):
    if not SID_RE.match(b.psession or ""):
        raise HTTPException(400, "bad practice session id")
    s = summary(b.psession)
    db.log_event(_sid(b.session_id), "practice_end", None, {"problems": s["session"]["problems"], "solved": s["session"]["solved"]})
    return s
