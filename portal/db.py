"""SQLite storage for everything the portal tracks about your learning.

Nothing here ever locks content. It only records what you do.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

DATA_DIR = Path(os.environ.get("PORTAL_DATA", Path(__file__).resolve().parent / "data"))
DB_PATH = DATA_DIR / "progress.db"
_lock = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS sessions(
  id TEXT PRIMARY KEY, started_at TEXT, last_seen TEXT, ended_at TEXT,
  last_hb REAL, active_seconds REAL DEFAULT 0, date TEXT);
CREATE TABLE IF NOT EXISTS activity(
  date TEXT, day_no INTEGER, area TEXT, seconds REAL DEFAULT 0,
  PRIMARY KEY(date, day_no, area));
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, date TEXT, session_id TEXT,
  type TEXT, day_no INTEGER, payload TEXT);
CREATE INDEX IF NOT EXISTS ix_events_day ON events(day_no, type);
CREATE TABLE IF NOT EXISTS attempts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, date TEXT, day_no INTEGER, kind TEXT,
  passed INTEGER, total INTEGER, ok INTEGER, duration_ms INTEGER, timed_out INTEGER,
  code_len INTEGER, output TEXT);
CREATE TABLE IF NOT EXISTS checks(
  day_no INTEGER, check_id TEXT, name TEXT, passed INTEGER DEFAULT 0, fails INTEGER DEFAULT 0,
  runs INTEGER DEFAULT 0, first_pass_at TEXT, last_at TEXT, last_status TEXT,
  PRIMARY KEY(day_no, check_id, name));
CREATE TABLE IF NOT EXISTS drafts(
  day_no INTEGER, kind TEXT, code TEXT, updated_at TEXT, PRIMARY KEY(day_no, kind));
CREATE TABLE IF NOT EXISTS notes(day_no INTEGER PRIMARY KEY, text TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS quiz(
  day_no INTEGER, q_no INTEGER, rating INTEGER, revealed_at TEXT, rated_at TEXT,
  PRIMARY KEY(day_no, q_no));
CREATE TABLE IF NOT EXISTS day_state(
  day_no INTEGER PRIMARY KEY, status TEXT DEFAULT 'open', confidence INTEGER,
  first_opened_at TEXT, last_opened_at TEXT, completed_at TEXT, opens INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS questions(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, date TEXT, session_id TEXT, day_no INTEGER,
  tab TEXT, source TEXT, text TEXT, selection TEXT, has_code INTEGER, attempted_first INTEGER,
  quality INTEGER, qtype TEXT, bloom TEXT, valid INTEGER, duplicate INTEGER,
  flags TEXT, tips TEXT, provider TEXT, answer TEXT, helpful INTEGER, meta TEXT);
CREATE TABLE IF NOT EXISTS reflections(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, provider TEXT, text TEXT);
"""


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def today() -> str:
    return date.today().isoformat()


@contextmanager
def conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _lock:
        c = sqlite3.connect(DB_PATH, timeout=30)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()


def init() -> None:
    with conn() as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript(SCHEMA)


def rows(sql: str, args: tuple = ()) -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def one(sql: str, args: tuple = ()) -> dict | None:
    r = rows(sql, args)
    return r[0] if r else None


def run(sql: str, args: tuple = ()) -> int:
    with conn() as c:
        return c.execute(sql, args).lastrowid


# ---- settings --------------------------------------------------------------------------------
def get_setting(k: str, default: str | None = None) -> str | None:
    r = one("SELECT v FROM settings WHERE k=?", (k,))
    return r["v"] if r else default


def set_setting(k: str, v: str | None) -> None:
    if v is None or v == "":
        run("DELETE FROM settings WHERE k=?", (k,))
    else:
        run("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, v))


# ---- sessions & time tracking ----------------------------------------------------------------
def start_session() -> str:
    sid = uuid.uuid4().hex[:12]
    t = time.time()
    run("INSERT INTO sessions(id,started_at,last_seen,last_hb,date) VALUES(?,?,?,?,?)",
        (sid, now_iso(), now_iso(), t, today()))
    return sid


MAX_CREDIT = 30.0     # never credit more than 30 s per heartbeat
MAX_GAP = 60.0        # a longer silence means the tab was asleep: credit nothing


def heartbeat(sid: str, day_no: int, area: str, active: bool) -> dict:
    """Credit time on the *server* clock so the client can't inflate it."""
    with conn() as c:
        s = c.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
        if not s:
            return {"ok": False}
        t = time.time()
        dt = t - (s["last_hb"] or t)
        credit = min(dt, MAX_CREDIT) if (active and 0 < dt <= MAX_GAP) else 0.0
        c.execute("UPDATE sessions SET last_hb=?, last_seen=?, active_seconds=active_seconds+?, ended_at=NULL WHERE id=?",
                  (t, now_iso(), credit, sid))
        if credit:
            c.execute(
                "INSERT INTO activity(date,day_no,area,seconds) VALUES(?,?,?,?) "
                "ON CONFLICT(date,day_no,area) DO UPDATE SET seconds=seconds+excluded.seconds",
                (today(), day_no, area, credit))
        total = c.execute("SELECT COALESCE(SUM(seconds),0) FROM activity WHERE date=?", (today(),)).fetchone()[0]
    return {"ok": True, "today_seconds": int(total)}


def end_session(sid: str) -> None:
    run("UPDATE sessions SET ended_at=? WHERE id=?", (now_iso(), sid))


def log_event(sid: str | None, etype: str, day_no: int | None, payload: dict | None = None) -> None:
    body = json.dumps(payload or {}, ensure_ascii=False)
    if len(body) > 4000:               # never cut JSON in half: readers json.loads() this column
        body = json.dumps({"truncated": True, "chars": len(body)})
    run("INSERT INTO events(ts,date,session_id,type,day_no,payload) VALUES(?,?,?,?,?,?)",
        (now_iso(), today(), sid, etype, day_no, body))


# ---- day state -------------------------------------------------------------------------------
def touch_day(day_no: int) -> None:
    t = now_iso()
    run("INSERT INTO day_state(day_no,first_opened_at,last_opened_at,opens) VALUES(?,?,?,1) "
        "ON CONFLICT(day_no) DO UPDATE SET last_opened_at=excluded.last_opened_at, opens=opens+1",
        (day_no, t, t))


def set_day_state(day_no: int, status: str | None, confidence: int | None) -> None:
    touch_day(day_no)
    if status in ("open", "done"):
        run("UPDATE day_state SET status=?, completed_at=? WHERE day_no=?",
            (status, now_iso() if status == "done" else None, day_no))
    if confidence is not None:
        run("UPDATE day_state SET confidence=? WHERE day_no=?", (max(1, min(5, int(confidence))), day_no))


# ---- check results parsed from the auto-checker output -----------------------------------------
_CHECK = re.compile(r"^\[(PASS|FAIL)\]\s+(\S+)\s*(.*)$")
_SCORE = re.compile(r"Score:\s*(\d+)\s*/\s*(\d+)")


def parse_output(output: str) -> tuple[list[dict], int | None, int | None]:
    res, passed, total = [], None, None
    for line in output.splitlines():
        m = _CHECK.match(line.strip())
        if m:
            name, _, detail = m.group(3).partition("  (got ")   # failing checks append "(got X, want Y)"
            res.append({"status": m.group(1), "id": m.group(2), "name": name.strip(),
                        "detail": ("(got " + detail) if detail else ""})
        s = _SCORE.search(line)
        if s:
            passed, total = int(s.group(1)), int(s.group(2))
    return res, passed, total


def record_attempt(day_no: int, kind: str, output: str, ok: bool, ms: int, timed_out: bool, code_len: int) -> dict:
    results, passed, total = parse_output(output)
    ts = now_iso()
    with conn() as c:
        c.execute("INSERT INTO attempts(ts,date,day_no,kind,passed,total,ok,duration_ms,timed_out,code_len,output) "
                  "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                  (ts, today(), day_no, kind, passed, total, int(ok), ms, int(timed_out), code_len, output[-3000:]))
        for r in results:
            ok_ = 1 if r["status"] == "PASS" else 0
            c.execute(
                "INSERT INTO checks(day_no,check_id,name,passed,fails,runs,first_pass_at,last_at,last_status) "
                "VALUES(?,?,?,?,?,1,?,?,?) ON CONFLICT(day_no,check_id,name) DO UPDATE SET "
                "passed=MAX(passed,excluded.passed), fails=fails+?, runs=runs+1, "
                "first_pass_at=COALESCE(first_pass_at, excluded.first_pass_at), last_at=excluded.last_at, "
                "last_status=excluded.last_status",
                (day_no, r["id"], r["name"], ok_, 0 if ok_ else 1, ts if ok_ else None, ts,
                 r["status"], 0 if ok_ else 1))
    return {"results": results, "passed": passed, "total": total}


def export_all() -> dict:
    out = {}
    for t in ("sessions", "activity", "events", "attempts", "checks", "drafts", "notes", "quiz",
              "day_state", "questions", "reflections"):
        out[t] = rows(f"SELECT * FROM {t}")
    out["exported_at"] = now_iso()
    return out
