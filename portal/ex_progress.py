"""Progress extension: XP, levels, streak, daily goal and badges, plus concept-level spaced review.

Everything is DERIVED from the existing tables (checks, quiz, activity, day_state, questions, attempts, events), so it is
retroactive and idempotent: calling any endpoint twice never double-counts. Nothing is ever penalised or locked.
The only things this feature stores are the daily-goal setting and the 'warmup_item' / 'warmup_done' events.
Concept scheduling lives in portal/progress_concepts.py. Endpoints: /api/progress/*.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import content, db, track
from . import progress_concepts as pc

router = APIRouter()

# ---- tunables ----------------------------------------------------------------------------------
CHECK_XP = {1: 2, 2: 3, 3: 5}            # per newly passing check, by exercise level
EXERCISE_BONUS = {1: 5, 2: 8, 3: 12}     # once every check of an exercise passes
QUIZ_XP = {0: 3, 1: 4, 2: 5}             # per rated quiz item (trying counts, nothing is penalised)
DAY_XP = 40                              # per completed day
MINUTE_CAP = 60                          # focused minutes that earn 1 XP each, per day
QUESTIONS_PER_DAY = 5                    # good questions that earn XP per day (2..6 XP each by quality)
DRILL_XP, DRILL_CAP = 3, 10              # 'drill_check' events with payload ok=true, per day
WARM_XP, WARM_CAP, WARM_DONE_XP = 3, 10, 10
LEVELS = [(0, "Hatchling"), (100, "Tinkerer"), (300, "Apprentice"), (600, "Builder"), (1000, "Problem Solver"),
          (1600, "Craftsperson"), (2400, "Engineer"), (3400, "Architect"), (4600, "Expert"), (6000, "Master")]
GOAL_LIMITS = {"min": (5, 480), "xp": (10, 2000)}
DEFAULT_GOAL = ("min", 30)


# ---- facts: one pass over the tables --------------------------------------------------------------
def _json(s: str | None) -> dict:
    try:
        v = json.loads(s or "{}")
        return v if isinstance(v, dict) else {}
    except ValueError:
        return {}


def _date(s: str | None) -> date | None:
    try:
        return date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def load_facts() -> dict:
    ex: dict = {}
    for r in db.rows("SELECT day_no, check_id, passed, first_pass_at, last_at, last_status FROM checks"):
        g = ex.setdefault((r["day_no"], r["check_id"]), {"n": 0, "p": 0, "pass_at": "", "fail_at": ""})
        g["n"] += 1
        if r["passed"]:
            g["p"] += 1
            g["pass_at"] = max(g["pass_at"], r["first_pass_at"] or r["last_at"] or "")
        if r["last_status"] == "FAIL":
            g["fail_at"] = max(g["fail_at"], r["last_at"] or "")
    warm, warm_items, drills, warm_done = defaultdict(list), set(), defaultdict(int), set()
    for r in db.rows("SELECT ts, date, type, day_no, payload FROM events WHERE type IN ('drill_check','warmup_item','warmup_done')"):
        p = _json(r["payload"])
        if r["type"] == "drill_check" and p.get("ok") is True:
            drills[r["date"]] += 1
        elif r["type"] == "warmup_item" and p.get("result") in ("ok", "partial", "miss") and isinstance(p.get("c"), int):
            warm[(r["day_no"], p["c"])].append((r["ts"], p["result"]))
            warm_items.add((r["date"], r["day_no"], p["c"], str(p.get("kind")), str(p.get("ref"))))
        elif r["type"] == "warmup_done":
            warm_done.add(r["date"])
    return {
        "ex": ex, "warm": dict(warm), "warm_items": warm_items, "warm_done": warm_done, "drills": dict(drills),
        "quiz": {(r["day_no"], r["q_no"]): r for r in db.rows(
            "SELECT day_no, q_no, rating, rated_at FROM quiz WHERE rating IS NOT NULL")},
        "secs": {r["date"]: r["s"] or 0 for r in db.rows("SELECT date, SUM(seconds) s FROM activity GROUP BY date")},
        "done": {r["day_no"]: r["completed_at"] or (r["last_opened_at"] or "") for r in db.rows(
            "SELECT day_no, completed_at, last_opened_at FROM day_state WHERE status='done'")},
        "questions": db.rows("SELECT date, quality FROM questions WHERE valid=1 AND quality IS NOT NULL"),
        "attempts": db.rows("SELECT date, ts FROM attempts"),
    }


def _level_of(f: dict, key: tuple) -> int:
    d = content.day(key[0])
    for e in (d or {}).get("exercises", []):
        if e["id"] == key[1]:
            return max(1, min(3, e["level"]))
    m = re.match(r"L(\d)", str(key[1]))
    return max(1, min(3, int(m.group(1)))) if m else 1


# ---- XP, levels -----------------------------------------------------------------------------------
def compute_xp(f: dict) -> dict:
    by_date: dict[str, int] = defaultdict(int)
    parts: dict[str, int] = defaultdict(int)

    def add(part: str, d: str | None, n: int) -> None:
        if n:
            by_date[(d or "")[:10]] += n
            parts[part] += n

    for key, g in f["ex"].items():
        lv = _level_of(f, key)
        add("exercises", g["pass_at"], g["p"] * CHECK_XP[lv])
        if g["n"] and g["p"] == g["n"]:
            add("exercises", g["pass_at"], EXERCISE_BONUS[lv])
    for r in f["quiz"].values():
        add("quiz", r["rated_at"], QUIZ_XP.get(r["rating"], 0))
    for d in f["done"].values():
        add("days", d, DAY_XP)
    for d, s in f["secs"].items():
        add("focus", d, int(min(s / 60, MINUTE_CAP)))
    per_day: dict[str, list[int]] = defaultdict(list)
    for q in f["questions"]:
        per_day[q["date"]].append(q["quality"] or 0)
    for d, qs in per_day.items():
        add("questions", d, sum(2 + min(4, q // 25) for q in sorted(qs, reverse=True)[:QUESTIONS_PER_DAY]))
    for d, n in f["drills"].items():
        add("drills", d, min(n, DRILL_CAP) * DRILL_XP)
    wn: dict[str, int] = defaultdict(int)
    for item in f["warm_items"]:
        wn[item[0]] += 1
    for d, n in wn.items():
        add("warmup", d, min(n, WARM_CAP) * WARM_XP)
    for d in f["warm_done"]:
        add("warmup", d, WARM_DONE_XP)
    return {"total": sum(by_date.values()), "by_date": dict(by_date), "parts": dict(parts)}


def level_info(xp: int) -> dict:
    i = max(k for k, (lo, _n) in enumerate(LEVELS) if xp >= lo)
    lo, name = LEVELS[i]
    name = track.T["name"] if i == len(LEVELS) - 1 else name
    nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return {"n": i + 1, "name": name, "min_xp": lo, "next_xp": nxt[0] if nxt else None,
            "next_name": nxt[1] if nxt else None, "to_next": nxt[0] - xp if nxt else 0,
            "pct": min(100, round(100 * (xp - lo) / (nxt[0] - lo))) if nxt else 100}


# ---- streak, goal ---------------------------------------------------------------------------------
def active_dates(f: dict) -> set[date]:
    raw = [d for d, s in f["secs"].items() if s >= 60]
    raw += [a["date"] for a in f["attempts"]] + [r["rated_at"] for r in f["quiz"].values()]
    raw += list(f["done"].values()) + list(f["warm_done"]) + [i[0] for i in f["warm_items"]]
    return {d for d in (_date(x) for x in raw) if d}


def streak(dates: set[date], today: date) -> dict:
    dates = {d for d in dates if d <= today}
    best = run = 0
    prev, reached = None, {}
    for d in sorted(dates):
        run = run + 1 if prev and (d - prev).days == 1 else 1
        best, prev = max(best, run), d
        for k in (3, 7):
            if run >= k and k not in reached:
                reached[k] = d
    cur, d = 0, (today if today in dates else today - timedelta(days=1))
    while d in dates:
        cur, d = cur + 1, d - timedelta(days=1)
    last = max(dates) if dates else None
    gap = (today - last).days if last else None
    wb = None
    if gap is not None and gap >= 2:           # a gap resets the streak; say so kindly
        wb = {"gap_days": gap, "previous_best": best,
              "text": f"Welcome back! A fresh streak starts with your next session. Your best so far is {best} day{'s' if best != 1 else ''}."}
    return {"current": cur, "best": best, "today_active": today in dates, "last_active": last.isoformat() if last else None,
            "welcome_back": wb, "reached": reached}


def get_goal() -> tuple[str, int]:
    kind = db.get_setting("progress.goal_kind", DEFAULT_GOAL[0])
    try:
        target = int(db.get_setting("progress.goal_target", str(DEFAULT_GOAL[1])))
    except (TypeError, ValueError):
        target = DEFAULT_GOAL[1]
    if kind not in GOAL_LIMITS:
        return DEFAULT_GOAL
    lo, hi = GOAL_LIMITS[kind]
    return kind, max(lo, min(hi, target))


def goal_info(f: dict, xp: dict, today: date) -> dict:
    kind, target = get_goal()
    iso = today.isoformat()
    done = round(f["secs"].get(iso, 0) / 60, 1) if kind == "min" else xp["by_date"].get(iso, 0)
    return {"kind": kind, "target": target, "done": done, "pct": min(100, round(100 * done / target)),
            "met": done >= target, "unit": "min" if kind == "min" else "XP", "limits": GOAL_LIMITS}


# ---- badges -----------------------------------------------------------------------------------------
def compute_badges(f: dict, st: dict, today: date) -> list[dict]:
    S, java = track.T["short"], track.IS_JAVA
    days = content.load_days()
    full = [k for k, g in f["ex"].items() if g["n"] and g["p"] == g["n"]]
    done = {n for n in f["done"] if n in days}
    runs = sorted(a["ts"] for a in f["attempts"] if a["ts"])
    hours = [int(a[11:13]) for a in runs if a[11:13].isdigit()]
    ds = sorted(active_dates(f))
    comeback = next((b for a, b in zip(ds, ds[1:]) if (b - a).days >= 4 and b <= today), None)
    qm = None
    for n, d in days.items():
        rs = [f["quiz"].get((n, q["n"])) for q in d["quiz"]]
        if rs and all(r and r["rating"] == 2 for r in rs):
            qm = max(qm or "", max(r["rated_at"] or "" for r in rs))
    wk = []                                  # (done days, size) per week
    for _w, _t, _s, a, b in track.T["weeks"]:
        size = [n for n in range(a, b + 1) if n in days]
        wk.append((sum(1 for n in size if n in done), len(size)))
    best_wk = max(wk, key=lambda x: (x[0] == x[1] > 0, x[0] / x[1] if x[1] else 0)) if wk else (0, 1)
    peak = max(f["secs"].values(), default=0) / 60
    good_q = len(f["questions"])
    reached = st["reached"]

    def mk(id_, name, glyph, how, cur, goal=1, when=None):
        cur = int(min(cur, goal))
        return {"id": id_, "name": name, "glyph": glyph, "how": how, "earned": cur >= goal, "cur": cur, "goal": goal,
                "when": (when.isoformat() if isinstance(when, date) else (when or "")[:10] or None) if cur >= goal else None}
    return [
        mk("first_run", "First run", "\u25B6", f"Run {S} code once: an exercise, an example or the playground.",
           len(runs) > 0, when=runs[0] if runs else None),
        mk("first_pass", "Clean sweep", "\u2713", "Pass every check of one practice exercise.",
           len(full) > 0, when=min((f["ex"][k]["pass_at"] for k in full), default=None)),
        mk("exercises_25", "Problem solver", "\u25C6", "Fully pass 25 practice exercises.", len(full), 25),
        mk("tough_nut", "Tough nut", "\u25B2", "Fully pass a Level 3 exercise.",
           any(_level_of(f, k) == 3 for k in full)),
        mk("first_day", "Day done", "\u2691", "Mark your first day as done.", len(done) > 0,
           when=min((f["done"][n] for n in done), default=None)),
        mk("week_done", "Week finished", "\u2605", "Finish every day of one week.", int(best_wk[0] == best_wk[1] > 0)),
        mk("course_done", f"{S} journey complete", "\u2726", "Finish all days of the course.", len(done), max(1, len(days))),
        mk("streak_3", "Three in a row", "\u25CF", "Be active 3 days in a row.", st["best"], 3, reached.get(3)),
        mk("streak_7", "Seven in a row", "\u25CF", "Be active 7 days in a row.", st["best"], 7, reached.get(7)),
        mk("questions_10", "Curious mind", "?", "Ask 10 good questions (specific, with your own thinking).", good_q, 10),
        mk("quiz_master", "Quiz master", "\u2756", "Rate every quiz question of one day as \u201CGot it\u201D.", qm is not None, when=qm),
        mk("comeback", "Welcome back", "\u21BA", "Return after 3 or more days away. No guilt, just keep going.",
           comeback is not None, when=comeback),
        mk("deep_focus", "Deep focus", "\u25CE", "Work for 60 focused minutes in a single day.", int(peak), 60),
        mk("warmup", "Warmed up", "\u2668", "Finish a 10-minute warm-up from the Home page.", len(f["warm_done"]) > 0,
           when=min(f["warm_done"], default=None)),
        mk("night_owl", "Night owl", "\u263E", f"Run {S} code between 10 pm and 4 am.", any(h >= 22 or h < 4 for h in hours)),
        mk("early_bird", "Early bird", "\u2600", f"Run {S} code between 5 am and 8 am.", any(5 <= h < 8 for h in hours)),
    ]


# ---- assembled views ----------------------------------------------------------------------------------
def _today() -> date:
    return date.fromisoformat(db.today())


def summary_data() -> dict:
    today, f = _today(), load_facts()
    xp = compute_xp(f)
    st = streak(active_dates(f), today)
    badges = compute_badges(f, st, today)
    earned = [b for b in badges if b["earned"]]
    recent = sorted(earned, key=lambda b: b["when"] or "", reverse=True)[:3]
    return {"track": track.T["short"], "xp": {"total": xp["total"], "today": xp["by_date"].get(today.isoformat(), 0),
                                              "parts": xp["parts"]},
            "level": level_info(xp["total"]), "levels": [{"n": i + 1, "name": n, "min_xp": lo} for i, (lo, n) in enumerate(LEVELS)],
            "streak": {k: v for k, v in st.items() if k != "reached"}, "goal": goal_info(f, xp, today),
            "recent_badges": [{k: b[k] for k in ("id", "name", "glyph", "when")} for b in recent],
            "badges_earned": [b["id"] for b in earned], "badges_total": len(badges)}


@router.get("/api/progress/summary")
def summary():
    return summary_data()


@router.get("/api/progress/badges")
def badges():
    f, today = load_facts(), _today()
    items = compute_badges(f, streak(active_dates(f), today), today)
    return {"items": items, "earned": sum(1 for b in items if b["earned"]), "total": len(items)}


@router.get("/api/progress/concepts")
def concepts(day: int | None = None, due_only: int = 0, limit: int = 120):
    limit = max(1, min(limit, 400))
    allc = pc.build(load_facts(), _today())
    due = pc.due_sorted(allc)
    items = [c for c in (due if due_only else allc) if day is None or c["day_no"] == day]
    return {"items": items[:limit], "due": due[:30],
            "counts": {"concepts": len(allc), "due": len(due), "practised": sum(1 for c in allc if c["step"] is not None)}}


class GoalIn(BaseModel):
    kind: str
    target: int


@router.post("/api/progress/goal")
def set_goal(b: GoalIn):
    if b.kind not in GOAL_LIMITS:
        raise HTTPException(400, "kind must be 'min' or 'xp'")
    lo, hi = GOAL_LIMITS[b.kind]
    if not lo <= b.target <= hi:
        raise HTTPException(400, f"target must be {lo} to {hi}")
    db.set_setting("progress.goal_kind", b.kind)
    db.set_setting("progress.goal_target", str(b.target))
    return {"ok": True, "goal": summary_data()["goal"]}


@router.get("/api/progress/warmup")
def warmup_build(size: int = 5):
    f = load_facts()
    return pc.warmup(f, pc.build(f, _today()), size)


@router.get("/api/progress/warmup/answer")
def warmup_answer(day_no: int, q_no: int):
    d = content.day(day_no)
    item = next((x for x in (d or {}).get("quiz", []) if x["n"] == q_no), None)
    if not item:
        raise HTTPException(404, "no such quiz item")
    return {"answer": item["a"]}


class WarmupIn(BaseModel):
    action: str = "item"                  # item | finish
    day_no: int | None = None
    concept_idx: int | None = None
    kind: str | None = None
    ref: str | None = None
    result: str | None = None             # ok | partial | miss
    items: int = 0
    ok_count: int = 0
    session_id: str | None = None


@router.post("/api/progress/warmup")
def warmup_complete(b: WarmupIn):
    sid = (b.session_id or "")[:40] or None
    if b.action == "finish":
        db.log_event(sid, "warmup_done", None, {"items": max(0, min(b.items, 20)), "ok": max(0, min(b.ok_count, 20))})
    elif b.action == "item":
        if b.result not in ("ok", "partial", "miss") or b.day_no is None or b.concept_idx is None or not b.kind or b.ref is None:
            raise HTTPException(400, "day_no, concept_idx, kind, ref and result (ok|partial|miss) are required")
        err = pc.validate_item(b.day_no, b.concept_idx, b.kind, str(b.ref)[:40])
        if err:
            raise HTTPException(400, err)
        db.log_event(sid, "warmup_item", b.day_no, {"c": b.concept_idx, "kind": b.kind, "ref": str(b.ref)[:40],
                                                    "result": b.result, "ok": b.result == "ok"})
    else:
        raise HTTPException(400, "action must be item or finish")
    s = summary_data()
    return {"ok": True, "xp": s["xp"], "level": s["level"], "goal": s["goal"]}
