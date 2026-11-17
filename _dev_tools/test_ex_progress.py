"""Tests for the 'progress' extension (XP / levels / streak / badges / concept review / warm-up).

Run once per track:
    & "$env:TEMP\\pyverify\\py\\python.exe" -W ignore -m pytest -p no:cacheprovider _dev_tools/test_ex_progress.py -q
    $env:PORTAL_TRACK="java"; (same command)
"""
import os
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["PORTAL_DATA"] = tempfile.mkdtemp(prefix="ex_progress_")
for _k in ("CURSOR_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    os.environ.pop(_k, None)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from portal import content, db, ex_progress as xp_mod, main, progress_concepts as pc, track  # noqa: E402

H = {"x-portal": "1"}
TABLES = ("settings", "sessions", "activity", "events", "attempts", "checks", "drafts", "notes", "quiz", "day_state",
          "questions", "reflections")


def ts(days_ago: int = 0, hour: int = 12) -> str:
    return (datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0) - timedelta(days=days_ago)).isoformat(timespec="seconds")


def dstr(days_ago: int = 0) -> str:
    return (date.today() - timedelta(days=days_ago)).isoformat()


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app, base_url="http://127.0.0.1:8765") as c:
        yield c


@pytest.fixture(autouse=True)
def clean(client):
    for t in TABLES:
        db.run(f"DELETE FROM {t}")
    yield


DAYS = content.load_days()
D1 = DAYS[1]
EX = D1["exercises"][0]


def add_check(day, cid, name, passed=1, when=0, status=None):
    db.run("INSERT INTO checks(day_no,check_id,name,passed,fails,runs,first_pass_at,last_at,last_status) VALUES(?,?,?,?,?,?,?,?,?)",
           (day, cid, name, passed, 0 if passed else 1, 1, ts(when) if passed else None, ts(when), status or ("PASS" if passed else "FAIL")))


def add_quiz(day, q, rating, when=0):
    db.run("INSERT OR REPLACE INTO quiz(day_no,q_no,rating,revealed_at,rated_at) VALUES(?,?,?,?,?)", (day, q, rating, ts(when), ts(when)))


def add_activity(day_ago, seconds, day_no=1):
    db.run("INSERT OR REPLACE INTO activity(date,day_no,area,seconds) VALUES(?,?,?,?)", (dstr(day_ago), day_no, "day", seconds))


def add_attempt(when=0, hour=12, ok=1):
    db.run("INSERT INTO attempts(ts,date,day_no,kind,passed,total,ok) VALUES(?,?,?,?,?,?,?)", (ts(when, hour), dstr(when), 1, "practice", 1, 1, ok))


def finish_day(n, when=0):
    db.run("INSERT OR REPLACE INTO day_state(day_no,status,first_opened_at,last_opened_at,completed_at,opens) VALUES(?,?,?,?,?,1)",
           (n, "done", ts(when), ts(when), ts(when)))


def summary(c):
    r = c.get("/api/progress/summary")
    assert r.status_code == 200, r.text
    return r.json()


def badge_ids(c):
    return {b["id"] for b in c.get("/api/progress/badges").json()["items"] if b["earned"]}


# ---- XP --------------------------------------------------------------------------------------------
def test_empty_database_is_fine(client):
    s = summary(client)
    assert s["xp"]["total"] == 0 and s["level"]["n"] == 1 and s["level"]["name"] == "Hatchling"
    assert s["streak"]["current"] == 0 and s["streak"]["welcome_back"] is None
    assert s["goal"] == {**s["goal"], "kind": "min", "target": 30, "done": 0, "pct": 0, "met": False}
    assert s["recent_badges"] == [] and s["badges_earned"] == []
    assert client.get("/api/progress/concepts").json()["counts"]["due"] == 0
    w = client.get("/api/progress/warmup").json()
    assert w["items"] == [] and w["empty"] is True


def test_exercise_xp_is_weighted_and_idempotent(client):
    lv = max(1, min(3, EX["level"]))
    for i in range(3):
        add_check(1, EX["id"], f"check {i}")
    want = 3 * xp_mod.CHECK_XP[lv] + xp_mod.EXERCISE_BONUS[lv]
    a, b, c3 = summary(client), summary(client), summary(client)
    assert a["xp"]["total"] == b["xp"]["total"] == c3["xp"]["total"] == want
    assert a["xp"]["today"] == want and a["xp"]["parts"] == {"exercises": want}
    # a partly passing exercise gets no completion bonus
    add_check(1, EX["id"], "check 3", passed=0)
    assert summary(client)["xp"]["total"] == 3 * xp_mod.CHECK_XP[lv]
    # failing again later never removes XP already earned
    db.run("UPDATE checks SET last_status='FAIL', fails=fails+1 WHERE name='check 0'")
    assert summary(client)["xp"]["total"] == 3 * xp_mod.CHECK_XP[lv]


def test_quiz_day_focus_question_drill_xp(client):
    add_quiz(1, 1, 0); add_quiz(1, 2, 1); add_quiz(1, 3, 2)
    assert summary(client)["xp"]["parts"]["quiz"] == 3 + 4 + 5
    finish_day(1)
    assert summary(client)["xp"]["parts"]["days"] == xp_mod.DAY_XP
    add_activity(0, 5 * 3600)                                           # 5 h in a day: capped
    assert summary(client)["xp"]["parts"]["focus"] == xp_mod.MINUTE_CAP
    add_activity(1, 20 * 60 + 30)
    assert summary(client)["xp"]["parts"]["focus"] == xp_mod.MINUTE_CAP + 20
    for q in (90, 50, 10):                                              # only valid questions with a quality score count
        db.run("INSERT INTO questions(ts,date,day_no,text,quality,valid,duplicate) VALUES(?,?,?,?,?,?,0)", (ts(), dstr(), 1, "q", q, 1 if q >= 45 else 0))
    db.run("INSERT INTO questions(ts,date,day_no,text,quality,valid,duplicate) VALUES(?,?,?,?,NULL,1,0)", (ts(), dstr(), 1, "quick"))
    assert summary(client)["xp"]["parts"]["questions"] == (2 + 3) + (2 + 2)
    db.log_event(None, "drill_check", 1, {"ok": True, "n": 1})
    db.log_event(None, "drill_check", 1, {"ok": False})
    db.log_event(None, "drill_check", 1, {"ok": "yes"})
    db.run("INSERT INTO events(ts,date,type,day_no,payload) VALUES(?,?,?,?,?)", (ts(), dstr(), "drill_check", 1, "{not json"))
    assert summary(client)["xp"]["parts"]["drills"] == xp_mod.DRILL_XP
    for _ in range(20):
        db.log_event(None, "drill_check", 1, {"ok": True})
    assert summary(client)["xp"]["parts"]["drills"] == xp_mod.DRILL_CAP * xp_mod.DRILL_XP
    t1, t2 = summary(client)["xp"]["total"], summary(client)["xp"]["total"]
    assert t1 == t2


def test_level_boundaries():
    names = [n for _lo, n in xp_mod.LEVELS]
    assert xp_mod.level_info(0)["n"] == 1
    for i, (lo, _n) in enumerate(xp_mod.LEVELS):
        assert xp_mod.level_info(lo)["n"] == i + 1
        if lo:
            assert xp_mod.level_info(lo - 1)["n"] == i
    top = xp_mod.level_info(10 ** 6)
    assert top["n"] == len(names) and top["next_xp"] is None and top["pct"] == 100 and top["name"] == track.T["name"]
    mid = xp_mod.level_info(150)
    assert mid["n"] == 2 and mid["next_xp"] == 300 and mid["to_next"] == 150 and mid["pct"] == 25
    assert [xp_mod.LEVELS[i][0] for i in range(len(names))] == sorted(xp_mod.LEVELS[i][0] for i in range(len(names)))


# ---- streak ----------------------------------------------------------------------------------------
def test_streak_pure_with_gaps():
    t = date(2030, 6, 20)
    D = lambda *offs: {t - timedelta(days=o) for o in offs}  # noqa: E731
    assert xp_mod.streak(set(), t)["current"] == 0
    s = xp_mod.streak(D(0, 1, 2), t)
    assert (s["current"], s["best"], s["today_active"], s["welcome_back"]) == (3, 3, True, None)
    s = xp_mod.streak(D(1, 2), t)                                       # not yet active today: streak still alive
    assert s["current"] == 2 and not s["today_active"] and s["welcome_back"] is None
    s = xp_mod.streak(D(2, 3, 4, 5), t)                                 # missed yesterday: resets, gentle welcome back
    assert s["current"] == 0 and s["best"] == 4 and s["welcome_back"]["gap_days"] == 2
    assert "Welcome back" in s["welcome_back"]["text"]
    s = xp_mod.streak(D(0, 3, 4, 5, 6, 7, 8, 9), t)
    assert s["current"] == 1 and s["best"] == 7 and s["reached"][7] == t - timedelta(days=3)
    assert xp_mod.streak({t + timedelta(days=3)}, t)["current"] == 0    # future rows are ignored


def test_streak_from_db_counts_runs_and_time(client):
    add_activity(0, 90); add_attempt(1); add_quiz(1, 1, 2, when=2)
    add_activity(3, 30)                                                 # under a minute: does not count
    s = summary(client)["streak"]
    assert s["current"] == 3 and s["today_active"] and s["best"] == 3
    db.run("DELETE FROM activity"); db.run("DELETE FROM attempts"); db.run("DELETE FROM quiz")
    add_attempt(6)
    s = summary(client)["streak"]
    assert s["current"] == 0 and s["welcome_back"]["gap_days"] == 6


# ---- goal ------------------------------------------------------------------------------------------
def test_goal_default_set_and_validation(client):
    assert summary(client)["goal"]["target"] == 30 and summary(client)["goal"]["kind"] == "min"
    add_activity(0, 15 * 60)
    g = summary(client)["goal"]
    assert g["done"] == 15 and g["pct"] == 50 and not g["met"]
    r = client.post("/api/progress/goal", json={"kind": "xp", "target": 40}, headers=H)
    assert r.status_code == 200 and r.json()["goal"]["kind"] == "xp"
    add_quiz(1, 1, 2)
    g = summary(client)["goal"]
    assert g["kind"] == "xp" and g["target"] == 40 and g["done"] == summary(client)["xp"]["today"]
    for bad in ({"kind": "hours", "target": 3}, {"kind": "min", "target": 0}, {"kind": "min", "target": 481},
                {"kind": "xp", "target": 9}, {"kind": "xp", "target": 2001}, {"kind": "min", "target": "abc"}, {"kind": "min"}, {}):
        assert client.post("/api/progress/goal", json=bad, headers=H).status_code in (400, 422), bad
    assert summary(client)["goal"]["target"] == 40                      # bad input changed nothing
    assert client.post("/api/progress/goal", json={"kind": "min", "target": 30}).status_code == 403     # needs x-portal
    db.set_setting("progress.goal_target", "99999")                    # a hand-edited value is clamped on read
    db.set_setting("progress.goal_kind", "xp")
    assert xp_mod.get_goal() == ("xp", 2000)
    db.set_setting("progress.goal_kind", "bogus")
    assert xp_mod.get_goal() == ("min", 30)


# ---- badges ----------------------------------------------------------------------------------------
def test_badges_catalogue_shape(client):
    r = client.get("/api/progress/badges").json()
    assert 12 <= r["total"] <= 16 and r["total"] == len(r["items"])
    ids = [b["id"] for b in r["items"]]
    assert len(set(ids)) == len(ids)
    for b in r["items"]:
        assert b["name"] and b["how"] and b["glyph"] and b["earned"] is False and b["when"] is None
    short = track.T["short"]
    assert any(short in b["how"] for b in r["items"])


def test_badge_rules(client):
    assert badge_ids(client) == set()
    add_attempt(0, hour=23)
    assert {"first_run", "night_owl"} <= badge_ids(client) and "early_bird" not in badge_ids(client)
    add_attempt(0, hour=6)
    assert "early_bird" in badge_ids(client)
    for i in range(2):
        add_check(1, EX["id"], f"c{i}")
    assert "first_pass" in badge_ids(client)
    # 25 fully-passed exercises
    for n, d in DAYS.items():
        for e in d["exercises"]:
            if (n, e["id"]) != (1, EX["id"]):
                add_check(n, e["id"], "only")
    ids = badge_ids(client)
    assert "exercises_25" in ids
    has_l3 = any(e["level"] == 3 for d in DAYS.values() for e in d["exercises"])
    assert ("tough_nut" in ids) == has_l3
    # questions
    for i in range(9):
        db.run("INSERT INTO questions(ts,date,day_no,text,quality,valid,duplicate) VALUES(?,?,?,?,?,1,0)", (ts(), dstr(), 1, f"q{i}", 60))
    assert "questions_10" not in badge_ids(client)
    db.run("INSERT INTO questions(ts,date,day_no,text,quality,valid,duplicate) VALUES(?,?,?,?,?,1,0)", (ts(), dstr(), 1, "q9", 60))
    assert "questions_10" in badge_ids(client)
    # quiz master needs every item of one day rated 'got it'
    for q in D1["quiz"][:-1]:
        add_quiz(1, q["n"], 2)
    assert "quiz_master" not in badge_ids(client)
    add_quiz(1, D1["quiz"][-1]["n"], 1)
    assert "quiz_master" not in badge_ids(client)
    add_quiz(1, D1["quiz"][-1]["n"], 2)
    assert "quiz_master" in badge_ids(client)
    # deep focus
    add_activity(2, 59 * 60)
    assert "deep_focus" not in badge_ids(client)
    add_activity(2, 60 * 60)
    assert "deep_focus" in badge_ids(client)


def test_badges_streak_comeback_days_weeks(client):
    for o in (0, 1):
        add_attempt(o)
    assert "streak_3" not in badge_ids(client)
    add_attempt(2)
    assert "streak_3" in badge_ids(client) and "streak_7" not in badge_ids(client) and "comeback" not in badge_ids(client)
    for o in (3, 4, 5, 6):
        add_attempt(o)
    assert "streak_7" in badge_ids(client)
    db.run("DELETE FROM attempts")
    add_attempt(10); add_attempt(0)                                     # 9 quiet days in between
    assert "comeback" in badge_ids(client) and "streak_3" not in badge_ids(client)
    assert "first_day" not in badge_ids(client)
    finish_day(1)
    assert "first_day" in badge_ids(client) and "week_done" not in badge_ids(client)
    for n in range(2, 8):
        finish_day(n)
    ids = badge_ids(client)
    first_week = [n for n in DAYS if track.T["weeks"][0][3] <= n <= track.T["weeks"][0][4]]
    assert ("week_done" in ids) == all(n in range(1, 8) for n in first_week)
    for n in DAYS:
        finish_day(n)
    ids = badge_ids(client)
    assert {"week_done", "course_done"} <= ids
    r = client.get("/api/progress/badges").json()
    assert r["earned"] == len(ids)
    s = summary(client)
    assert set(s["badges_earned"]) == ids and len(s["recent_badges"]) == 3


# ---- concept schedule ---------------------------------------------------------------------------------
def test_interval_ladder():
    assert [pc.interval_for(i) for i in range(8)] == [1, 3, 7, 14, 30, 60, 120, 180]


def test_schedule_steps_miss_and_early_practice():
    t0 = date(2030, 1, 1)
    at = lambda off, o: ((t0 + timedelta(days=off)).isoformat() + "T10:00:00", o)  # noqa: E731
    s = pc.schedule([at(0, "ok")])
    assert (s["step"], s["interval"], s["due"]) == (0, 1, t0 + timedelta(days=1))
    s = pc.schedule([at(0, "ok"), at(1, "ok")])                          # on the due date: step up
    assert (s["step"], s["interval"], s["due"]) == (1, 3, t0 + timedelta(days=4))
    s = pc.schedule([at(0, "ok"), at(1, "ok"), at(4, "ok"), at(11, "ok"), at(25, "ok"), at(55, "ok")])
    assert (s["step"], s["interval"]) == (5, 60)
    s = pc.schedule([at(0, "ok"), at(1, "ok"), at(4, "ok"), at(5, "miss")])   # a miss starts over
    assert (s["step"], s["interval"], s["last_outcome"]) == (0, 1, "miss")
    s = pc.schedule([at(0, "ok"), at(1, "ok"), at(2, "ok")])             # early practice does not climb the ladder
    assert s["step"] == 1 and s["due"] == t0 + timedelta(days=5)
    s = pc.schedule([at(0, "ok"), at(1, "ok"), at(4, "partial")])        # partial keeps the step
    assert s["step"] == 1
    s = pc.schedule([("2030-01-01T09:00:00", "miss"), ("2030-01-01T18:00:00", "ok")])   # same day: last wins
    assert s["step"] == 0 and s["last_outcome"] == "ok"
    assert pc.schedule([]) is None and pc.schedule([("garbage", "ok"), ("2030-01-01T00:00:00", "weird")]) is None
    assert pc.schedule([at(3, "ok"), at(0, "ok")])["last"] == t0 + timedelta(days=3)   # order does not matter


def test_keyword_mapping():
    assert pc.tokens("Slicing strings") == {"slicing", "string"}
    ct = [pc.tokens("Loops"), pc.tokens("String slicing")]
    assert pc._targets(ct, "Slice a string") == [1]
    assert pc._targets(ct, "Totally unrelated") == [0, 1]


def test_concepts_due_logic_and_order(client):
    n_conc = len(D1["concepts"])
    assert n_conc >= 2
    q = D1["quiz"][0]["n"]
    add_quiz(1, q, 2, when=0)                                           # practised today: not due yet
    r = client.get("/api/progress/concepts").json()
    assert r["counts"]["due"] == 0 and r["counts"]["practised"] >= 1
    day1 = [c for c in r["items"] if c["day_no"] == 1]
    assert day1 and all(c["due_date"] == dstr(-1) for c in day1 if c["step"] is not None and c["last_practiced"] == dstr(0))
    # yesterday's first practice: due today
    db.run("DELETE FROM quiz"); add_quiz(1, q, 2, when=1)
    r = client.get("/api/progress/concepts").json()
    assert r["counts"]["due"] >= 1 and all(c["due"] for c in r["due"])
    first = r["due"][0]
    assert first["day_no"] == 1 and first["overdue_days"] == 0 and first["href"] == "#/day/1/learn"
    # a missed one two days ago is more urgent than a plain overdue one
    add_quiz(2, DAYS[2]["quiz"][0]["n"], 0, when=2)
    add_quiz(3, DAYS[3]["quiz"][0]["n"], 2, when=2)
    due = client.get("/api/progress/concepts?due_only=1").json()["items"]
    urg = [c["urgency"] for c in due]
    assert urg == sorted(urg, reverse=True) and due[0]["day_no"] == 2 and due[0]["last_outcome"] == "miss"
    assert all(c["day_no"] == 2 for c in client.get("/api/progress/concepts?day=2").json()["items"])
    assert len(client.get("/api/progress/concepts?limit=1").json()["items"]) == 1
    assert len(client.get("/api/progress/concepts?limit=99999").json()["items"]) <= 400
    # a rated quiz that moved far into the future is not due
    db.run("DELETE FROM quiz"); add_quiz(1, q, 2, when=40); add_quiz(1, q + 100, 2, when=39)
    for c in client.get("/api/progress/concepts?day=1").json()["items"]:
        assert c["step"] in (None, 0)                                    # only one practice day in the data: still step 0


def test_concepts_via_checks_and_done_days(client):
    add_check(1, EX["id"], "a", when=3)
    finish_day(2, when=5)
    items = client.get("/api/progress/concepts").json()["items"]
    d2 = [c for c in items if c["day_no"] == 2]
    assert d2 and all(c["due"] and c["overdue_days"] == 4 and c["status"] == "learning" for c in d2)
    assert all(c["mastery"] == 100 or c["evidence"]["ex_total"] + c["evidence"]["quiz_total"] > 0 for c in d2)
    # failing the check later counts as a miss: the interval resets to 1 day
    db.run("UPDATE checks SET last_status='FAIL', last_at=? WHERE day_no=1", (ts(0),))
    d1 = [c for c in client.get("/api/progress/concepts?day=1").json()["items"] if c["last_outcome"]]
    assert d1 and all(c["last_outcome"] == "miss" and c["step"] == 0 and c["due_date"] == dstr(-1) for c in d1)
    db.run("UPDATE checks SET last_at=? WHERE day_no=1", (ts(2),))        # the miss was two days ago: due since yesterday
    d1 = [c for c in client.get("/api/progress/concepts?day=1").json()["items"] if c["last_outcome"]]
    assert d1 and all(c["due"] and c["urgency"] >= 1.5 for c in d1)


# ---- warm-up -----------------------------------------------------------------------------------------
def seed_due():
    for n in (1, 2, 3):
        add_quiz(n, DAYS[n]["quiz"][0]["n"], 1, when=4)
        add_check(n, DAYS[n]["exercises"][0]["id"], "x", when=4)
        finish_day(n, when=4)


def test_warmup_build(client):
    seed_due()
    w = client.get("/api/progress/warmup").json()
    assert 1 <= len(w["items"]) <= 5 and w["light"] is False and w["due_total"] >= 3 and w["minutes"] > 0
    assert len({i["id"] for i in w["items"]}) == len(w["items"])
    kinds = {i["kind"] for i in w["items"]}
    assert kinds <= {"quiz", "exercise"}
    for i in w["items"]:
        d = DAYS[i["day_no"]]
        assert i["concept"] == d["concepts"][i["concept_idx"]] and i["href"].startswith(f"#/day/{i['day_no']}/")
        if i["kind"] == "quiz":
            assert any(q["n"] == i["q_no"] and q["q"] == i["text"] for q in d["quiz"])
            assert "answer" not in i                                      # revealed on request only
        else:
            assert any(e["id"] == i["check_id"] for e in d["exercises"])
    assert len(client.get("/api/progress/warmup?size=2").json()["items"]) <= 2
    assert len(client.get("/api/progress/warmup?size=999").json()["items"]) <= 8
    assert client.get("/api/progress/warmup").json() == w               # building is a pure read
    q = next((i for i in w["items"] if i["kind"] == "quiz"), None)
    if q:
        a = client.get(f"/api/progress/warmup/answer?day_no={q['day_no']}&q_no={q['q_no']}")
        assert a.status_code == 200 and a.json()["answer"] == next(x["a"] for x in DAYS[q["day_no"]]["quiz"] if x["n"] == q["q_no"])
        assert db.one("SELECT COUNT(*) c FROM events WHERE type='quiz_reveal'")["c"] == 0
    assert client.get("/api/progress/warmup/answer?day_no=999&q_no=1").status_code == 404
    assert client.get("/api/progress/warmup/answer?day_no=1&q_no=9999").status_code == 404
    assert client.get("/api/progress/warmup/answer?day_no=x&q_no=1").status_code == 422


def test_warmup_light_mode_when_nothing_due(client):
    add_quiz(1, D1["quiz"][0]["n"], 2, when=0)
    w = client.get("/api/progress/warmup").json()
    assert w["light"] is True and w["items"] and w["due_total"] == 0


def test_warmup_complete_moves_schedule_and_xp(client):
    seed_due()
    w = client.get("/api/progress/warmup").json()
    it = w["items"][0]
    base = summary(client)["xp"]["total"]
    ref = str(it["q_no"]) if it["kind"] == "quiz" else it["check_id"]
    body = {"action": "item", "day_no": it["day_no"], "concept_idx": it["concept_idx"], "kind": it["kind"], "ref": ref, "result": "ok"}
    r = client.post("/api/progress/warmup", json=body, headers=H)
    assert r.status_code == 200 and r.json()["xp"]["total"] == base + xp_mod.WARM_XP
    r = client.post("/api/progress/warmup", json=body, headers=H)       # same item again the same day: no double XP
    assert r.json()["xp"]["total"] == base + xp_mod.WARM_XP
    c = next(c for c in client.get(f"/api/progress/concepts?day={it['day_no']}").json()["items"] if c["idx"] == it["concept_idx"])
    assert c["last_practiced"] == dstr(0) and c["due"] is False and c["last_outcome"] == "ok"
    # a miss reports as due tomorrow (interval resets) and still earns the same XP: nothing is penalised
    miss = {**body, "result": "miss", "concept_idx": it["concept_idx"]}
    r = client.post("/api/progress/warmup", json=miss, headers=H)
    assert r.status_code == 200 and r.json()["xp"]["total"] == base + xp_mod.WARM_XP
    c = next(c for c in client.get(f"/api/progress/concepts?day={it['day_no']}").json()["items"] if c["idx"] == it["concept_idx"])
    assert c["step"] == 0 and c["last_outcome"] == "miss" and c["due_date"] == dstr(-1)
    # finishing the warm-up: bonus once per day, and the 'Warmed up' badge
    assert "warmup" not in badge_ids(client)
    fin = {"action": "finish", "items": 5, "ok_count": 3}
    r1 = client.post("/api/progress/warmup", json=fin, headers=H).json()
    r2 = client.post("/api/progress/warmup", json=fin, headers=H).json()
    assert r1["xp"]["total"] == r2["xp"]["total"] == base + xp_mod.WARM_XP + xp_mod.WARM_DONE_XP
    assert "warmup" in badge_ids(client) and summary(client)["streak"]["today_active"]


def test_warmup_input_validation(client):
    ok = {"action": "item", "day_no": 1, "concept_idx": 0, "kind": "quiz", "ref": str(D1["quiz"][0]["n"]), "result": "ok"}
    assert client.post("/api/progress/warmup", json=ok, headers=H).status_code == 200
    assert client.post("/api/progress/warmup", json=ok).status_code == 403
    bad = [{**ok, "day_no": 0}, {**ok, "day_no": 31}, {**ok, "day_no": -5}, {**ok, "concept_idx": -1}, {**ok, "concept_idx": 500},
           {**ok, "kind": "video"}, {**ok, "ref": "9999"}, {**ok, "ref": "../../etc"}, {**ok, "result": "great"}, {**ok, "result": None},
           {**ok, "kind": "exercise", "ref": "NOPE"}, {**ok, "action": "explode"}, {**ok, "day_no": None}, {**ok, "day_no": "abc"},
           {k: v for k, v in ok.items() if k != "ref"}]
    for b in bad:
        assert client.post("/api/progress/warmup", json=b, headers=H).status_code in (400, 422), b
    assert db.one("SELECT COUNT(*) c FROM events WHERE type='warmup_item'")["c"] == 1     # rejected items logged nothing
    ex_ok = {**ok, "kind": "exercise", "ref": EX["id"]}
    assert client.post("/api/progress/warmup", json=ex_ok, headers=H).status_code == 200
    big = client.post("/api/progress/warmup", json={"action": "finish", "items": 10 ** 9, "ok_count": -4, "session_id": "s" * 500}, headers=H)
    assert big.status_code == 200
    p = db.one("SELECT payload, session_id FROM events WHERE type='warmup_done'")
    assert '"items": 20' in p["payload"] and '"ok": 0' in p["payload"] and len(p["session_id"]) == 40


def test_existing_review_endpoint_untouched(client):
    add_quiz(1, 1, 0, when=3)
    r = client.get("/api/review")
    assert r.status_code == 200 and r.json()["counts"]["quiz_due"] == 1
    assert client.get("/api/overview").status_code == 200
    assert client.get("/api/extras").json()["js"].count("progress.js") == 1
    assert "progress.css" in client.get("/api/extras").json()["css"]
