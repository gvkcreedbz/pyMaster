"""Drills: five short exercise types beyond "write code" (Parsons, fill-in, predict, find-the-bug, review).

Data: ``<day folder>/DRILLS.json`` (spec: _dev_tools/DRILLS_FORMAT.md). Logic lives in portal/drills_core.py.
Endpoints:
    GET  /api/drills/summary                       per-day totals/done (Home, Insights)
    GET  /api/drills/{day}?session_id=              the day's drills WITHOUT answers, shuffled per session
    POST /api/drills/{day}/{drill_id}/check        {answer, session_id} -> {ok, score, feedback, explain, attempts, ...}
    POST /api/drills/{day}/{drill_id}/giveup       {session_id} -> reveals the solution (logged, never counted as done)
Events: db.log_event(sid, "drill_check", day, {"drill", "type", "ok", "score"}) and "drill_giveup".
"""
from __future__ import annotations

import json
import logging
import re
import secrets
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import content, db, drills_core as core, track

log = logging.getLogger("portal.drills")
router = APIRouter()
_cache: dict[int, tuple[float, dict[str, dict]]] = {}      # day -> (file mtime, {drill id: drill})
_secret = ""
SID_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
MAX_BODY = 12000


def setup() -> None:
    global _secret
    db.run("CREATE TABLE IF NOT EXISTS drill_attempts(id INTEGER PRIMARY KEY AUTOINCREMENT, day_no INTEGER, drill_id TEXT, "
           "ok INTEGER, score REAL, answer_json TEXT, created_at TEXT, session_id TEXT)")
    db.run("CREATE INDEX IF NOT EXISTS ix_drill_attempts ON drill_attempts(day_no, drill_id)")
    db.run("CREATE TABLE IF NOT EXISTS drill_giveups(id INTEGER PRIMARY KEY AUTOINCREMENT, day_no INTEGER, drill_id TEXT, "
           "created_at TEXT, session_id TEXT)")
    _secret = db.get_setting("drills_secret") or ""
    if not _secret:
        _secret = secrets.token_hex(12)
        db.set_setting("drills_secret", _secret)


def _sid(v) -> str | None:
    return v if isinstance(v, str) and SID_RE.match(v) else None


def _day_folder(n: int):
    d = content.day(n)
    if not d:
        raise HTTPException(404, "no such day")
    return d


def _drills(n: int) -> dict[str, dict]:
    """Valid drills of day n keyed by id (re-read when the file changes; a broken file or drill is skipped, never fatal)."""
    _day_folder(n)
    f = core.find_file(track.DAYS_DIR, n)
    if not f:
        return {}
    mt = f.stat().st_mtime
    hit = _cache.get(n)
    if hit and hit[0] == mt:
        return hit[1]
    out: dict[str, dict] = {}
    doc = core.load_doc(f)
    if doc is None:
        log.warning("drills: cannot read %s", f)
    for d in (doc or {}).get("drills", []):
        errs = core.lint_drill(d, track.IS_JAVA)
        if errs or d.get("id") in out:
            log.warning("drills: skipping a drill in %s: %s", f.name, errs or "duplicate id")
            continue
        out[d["id"]] = d
    _cache[n] = (mt, out)
    return out


def _drill(n: int, did: str) -> dict:
    if not core.ID_RE.match(did or ""):
        raise HTTPException(404, "no such drill")
    d = _drills(n).get(did)
    if not d:
        raise HTTPException(404, "no such drill")
    return d


def _state(n: int) -> dict[str, dict]:
    st: dict[str, dict] = {}
    for r in db.rows("SELECT drill_id, COUNT(*) c, MAX(ok) ok, MAX(score) best FROM drill_attempts WHERE day_no=? GROUP BY drill_id", (n,)):
        st[r["drill_id"]] = {"attempts": r["c"], "solved": bool(r["ok"]), "best": round(r["best"] or 0, 2), "gave_up": False}
    for r in db.rows("SELECT DISTINCT drill_id FROM drill_giveups WHERE day_no=?", (n,)):
        st.setdefault(r["drill_id"], {"attempts": 0, "solved": False, "best": 0, "gave_up": False})["gave_up"] = True
    return st


class CheckIn(BaseModel):
    answer: Any = None
    session_id: str | None = None


class GiveUpIn(BaseModel):
    session_id: str | None = None


@router.get("/api/drills/summary")
def summary():
    days, total, done = {}, 0, 0
    solved: dict[int, set] = {}
    seen: dict[int, set] = {}
    for r in db.rows("SELECT day_no, drill_id, MAX(ok) ok FROM drill_attempts GROUP BY day_no, drill_id"):
        seen.setdefault(r["day_no"], set()).add(r["drill_id"])
        if r["ok"]:
            solved.setdefault(r["day_no"], set()).add(r["drill_id"])
    for r in db.rows("SELECT DISTINCT day_no, drill_id FROM drill_giveups"):
        seen.setdefault(r["day_no"], set()).add(r["drill_id"])
    for n in sorted(content.load_days()):
        ids = set(_drills(n))
        if not ids:
            continue
        days[str(n)] = {"total": len(ids), "done": len(ids & solved.get(n, set())), "attempted": len(ids & seen.get(n, set()))}
        total += len(ids)
        done += days[str(n)]["done"]
    return {"days": days, "total": total, "done": done, "track": track.ID}


@router.get("/api/drills/{day}")
def list_drills(day: int, session_id: str | None = None):
    _day_folder(day)
    sid = _sid(session_id) or "anon"
    st = _state(day)
    out = []
    for did, d in _drills(day).items():
        v = core.public_view(d, core.Tok(_secret, day, did), f"{sid}|{day}|{did}", track.IS_JAVA)
        s = st.get(did, {"attempts": 0, "solved": False, "best": 0, "gave_up": False})
        v["state"] = s
        if s["attempts"] or s["gave_up"]:
            v["explain"] = d["explain"]            # revealed only after an attempt or giving up
        out.append(v)
    return {"day": day, "track": track.ID, "drills": out, "total": len(out), "done": sum(1 for x in out if x["state"]["solved"])}


def _attempts(day: int, did: str) -> int:
    return (db.one("SELECT COUNT(*) c FROM drill_attempts WHERE day_no=? AND drill_id=?", (day, did)) or {"c": 0})["c"]


@router.post("/api/drills/{day}/{drill_id}/check")
def check(day: int, drill_id: str, body: CheckIn):
    _day_folder(day)
    d = _drill(day, drill_id)
    blob = json.dumps(body.answer, ensure_ascii=False)
    if len(blob) > MAX_BODY:
        raise HTTPException(413, "answer too large")
    try:
        ok, score, fb = core.check(d, body.answer, core.Tok(_secret, day, drill_id), track.IS_JAVA)
    except core.BadAnswer as e:
        raise HTTPException(422, str(e)) from None
    score = round(float(score), 2)
    sid = _sid(body.session_id)
    db.run("INSERT INTO drill_attempts(day_no,drill_id,ok,score,answer_json,created_at,session_id) VALUES(?,?,?,?,?,?,?)",
           (day, drill_id, int(ok), score, blob[:3000], db.now_iso(), sid))
    db.log_event(sid, "drill_check", day, {"drill": drill_id, "type": d["type"], "ok": ok, "score": score})
    res = {"ok": ok, "score": score, "feedback": fb, "explain": d["explain"], "attempts": _attempts(day, drill_id),
           "type": d["type"], "concepts": d.get("concepts", [])}
    if ok:
        res["solution"] = core.solution_view(d, track.IS_JAVA)
    return res


@router.post("/api/drills/{day}/{drill_id}/giveup")
def giveup(day: int, drill_id: str, body: GiveUpIn | None = None):
    _day_folder(day)
    d = _drill(day, drill_id)
    sid = _sid(body.session_id) if body else None
    db.run("INSERT INTO drill_giveups(day_no,drill_id,created_at,session_id) VALUES(?,?,?,?)", (day, drill_id, db.now_iso(), sid))
    db.log_event(sid, "drill_giveup", day, {"drill": drill_id, "type": d["type"]})
    return {"ok": False, "solution": core.solution_view(d, track.IS_JAVA), "explain": d["explain"],
            "attempts": _attempts(day, drill_id), "type": d["type"], "concepts": d.get("concepts", [])}
