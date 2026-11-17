"""Tests for practice sessions (portal/ex_practice.py). Run once per track (PORTAL_TRACK=python|java), or both with
  powershell -File _dev_tools\\test_tracks.ps1 _dev_tools/test_ex_practice.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["PORTAL_DATA"] = tempfile.mkdtemp(prefix="practice_test_")
for k in ("CURSOR_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402

from portal import db, drills_core as core, ex_drills, ex_practice, main  # noqa: E402

H = {"x-portal": "1"}
LEAK_KEYS = {"title", "concepts", "hint", "explain", "expected", "answers", "answer", "bug_lines", "fixed_code", "issues", "non_issues",
             "regex", "alternatives", "buggy_runs", "solution"}


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app, base_url="http://127.0.0.1:8765") as c:
        yield c


def drill(pid):
    day, did = ex_practice.parse_pid(pid)
    return day, did, ex_drills._drills(day)[did]


def good(day, d):
    tok = core.Tok(ex_drills._secret, day, d["id"])
    t = d["type"]
    if t == "parsons":
        n = len(d["lines"])
        a = {"order": [tok("L", i) for i in range(n)], "indents": list(d.get("indent") or [0] * n)}
        if d.get("faded"):
            a["blanks"] = {tok("B", i): b["answers"][0] for i, b in enumerate(d["blanks"])}
        return a
    if t == "fill":
        return {"blanks": [b["answers"][0] for b in d["blanks"]]}
    if t == "predict":
        return {"text": d["expected"]}
    if t == "bug":
        return {"lines": list(d["bug_lines"]), "option": tok("O", d["answer"])}
    return {"picks": [tok("I", k) for k in range(len(d["issues"]))]}


def bad(day, d):
    tok = core.Tok(ex_drills._secret, day, d["id"])
    t = d["type"]
    if t == "parsons":
        n = len(d["lines"])
        return {"order": [tok("L", i) for i in reversed(range(n))], "indents": [0] * n}
    if t == "fill":
        return {"blanks": ["zzz-not-it"] * len(d["blanks"])}
    if t == "predict":
        return {"text": "definitely not the output"}
    if t == "bug":
        return {"lines": [x for x in range(1, 40) if x not in d["bug_lines"]][:1], "option": tok("O", (d["answer"] + 1) % len(d["options"]))}
    return {"picks": [tok("I", len(d["issues"]))]}


def nxt(client, ps, scope="reached"):
    r = client.post("/api/practice/next", headers=H, json={"psession": ps, "session_id": "t", "scope": scope})
    assert r.status_code == 200, r.text
    return r.json()


def solve(client, ps, p, hints=0, conf=None, thinking="", tries=1, ok=True):
    day, _did, d = drill(p["pid"])
    ans = good(day, d) if ok else bad(day, d)
    r = client.post(f"/api/practice/{p['pid']}/check", headers=H,
                    json={"psession": ps, "answer": ans, "session_id": "t", "hints": hints, "confidence": conf, "thinking": thinking, "tries": tries})
    assert r.status_code == 200, r.text
    return r.json()


def giveup(client, ps, p, hints=0, conf=None):
    r = client.post(f"/api/practice/{p['pid']}/giveup", headers=H, json={"psession": ps, "session_id": "t", "hints": hints, "confidence": conf})
    assert r.status_code == 200, r.text
    return r.json()


def test_problem_never_names_its_topic(client):
    p = nxt(client, "ps-leak")
    assert p["done"] is False
    assert not (LEAK_KEYS & set(p["problem"])), LEAK_KEYS & set(p["problem"])
    assert not (LEAK_KEYS & set(p)), LEAK_KEYS & set(p)
    assert 1 <= p["level"] <= 5 and p["number"] == 1 and p["hint_steps"] == 3
    # right answer reveals everything only afterwards
    wrong = solve(client, "ps-leak", p, ok=False)
    assert wrong["ok"] is False and not ({"solution", "explain", "title", "concepts", "day"} & set(wrong))
    right = solve(client, "ps-leak", p)
    assert right["ok"] and right["solution"] and right["explain"] and right["title"] and right["day"]


def test_scope_follows_the_days_you_have_opened(client):
    ex_practice.setup()
    db.run("DELETE FROM day_state")
    assert ex_practice.reached_days() == [1, 2, 3]            # brand new learner: the first days
    db.touch_day(10)
    assert ex_practice.reached_days() == [10]
    seen = set()
    for i in range(5):
        p = nxt(client, f"ps-scope{i}")
        seen.add(ex_practice.parse_pid(p["pid"])[0])
    assert seen == {10}
    allp = nxt(client, "ps-all", scope="all")
    assert allp["days_in_scope"] == 30 and allp["pool"] == 150
    db.run("DELETE FROM day_state")


def test_no_repeats_and_mixes_days_and_types(client):
    for d in (2, 5, 9):
        db.touch_day(d)
    ps, pids, days, types = "ps-mix", [], [], []
    for _ in range(10):
        p = nxt(client, ps)
        assert not p["done"]
        day, _did, d = drill(p["pid"])
        pids.append(p["pid"]); days.append(day); types.append(d["type"])
        solve(client, ps, p, hints=0)
    assert len(set(pids)) == len(pids), "a problem repeated inside one session"
    assert set(days) <= {2, 5, 9} and len(set(days)) >= 2
    assert len(set(types)) >= 3
    assert sum(1 for a, b in zip(days, days[1:]) if a == b) <= 4              # interleaved, not blocked by day
    db.run("DELETE FROM day_state")


def test_difficulty_goes_up_after_three_good_and_down_after_two_misses(client):
    for d in range(1, 31):
        db.touch_day(d)
    ps = "ps-adapt"
    first = nxt(client, ps)
    assert first["target"] == 2
    p = first
    targets = []
    for _ in range(3):
        solve(client, ps, p, hints=0)
        p = nxt(client, ps)
        targets.append(p["target"])
    assert targets[-1] == 3, targets                                           # three clean answers: harder
    giveup(client, ps, p)
    p = nxt(client, ps)
    giveup(client, ps, p)
    p = nxt(client, ps)
    assert p["target"] == 2, p["target"]                                       # two misses: easier
    # answers that needed help do not raise the level
    ps2 = "ps-help"
    p = nxt(client, ps2)
    for _ in range(4):
        solve(client, ps2, p, hints=3)
        p = nxt(client, ps2)
    assert p["target"] == 2
    db.run("DELETE FROM day_state")


def test_hint_ladder_is_graded_and_never_the_whole_answer(client):
    ex_practice.setup()
    n = 0
    for day in range(1, 31):
        for did, d in ex_drills._drills(day).items():
            pid = ex_practice.pid_of(day, did)
            texts = []
            for step in (1, 2, 3):
                r = client.post(f"/api/practice/{pid}/hint", headers=H, json={"step": step})
                assert r.status_code == 200, (pid, step, r.text)
                assert r.json()["text"].strip() and r.json()["more"] is (step < 3)
                texts.append(r.json()["text"])
            assert len(set(texts)) == 3, (pid, texts)
            # hint 3 may narrow the search but must not hand over the answer: it is built from ONE piece only
            if d["type"] == "predict":
                exp = core._lines_of(d["expected"])
                assert texts[2].endswith(exp[0]) and len(exp) < 2 or exp[0] in texts[2], (pid, texts[2])
                assert texts[2] != "\n".join(exp) or len(exp) == 1, (pid, "hint 3 gives away the whole output")
            if d["type"] == "parsons":
                assert texts[2].endswith(d["lines"][0]), (pid, texts[2])            # only the first line of the program
            if d["type"] == "fill":
                assert texts[2].endswith(str(d["blanks"][0]["answers"][0])), (pid, texts[2])   # only the first blank
            n += 1
    assert n == 150, n
    assert client.post(f"/api/practice/{ex_practice.pid_of(1, 'd01-fill')}/hint", headers=H, json={"step": 4}).status_code == 400
    assert client.post(f"/api/practice/{ex_practice.pid_of(1, 'd01-fill')}/hint", headers=H, json={"step": 0}).status_code == 400


def test_thinking_confidence_and_hints_are_stored(client):
    ps = "ps-store"
    p = nxt(client, ps)
    solve(client, ps, p, hints=2, conf=2, thinking="I think the loop runs three times because ...", tries=2)
    row = db.one("SELECT * FROM practice_attempts WHERE psession=?", (ps,))
    assert row["ok"] == 1 and row["hints"] == 2 and row["confidence"] == 2 and row["tries"] == 2
    assert row["thinking"].startswith("I think the loop") and row["gave_up"] == 0
    p = nxt(client, ps)
    r = client.post(f"/api/practice/{p['pid']}/check", headers=H, json={"psession": ps, "answer": good(*drill(p["pid"])[::2]), "confidence": 9, "thinking": "x" * 5000})
    assert r.status_code == 200
    row = db.one("SELECT * FROM practice_attempts WHERE psession=? ORDER BY id DESC", (ps,))
    assert row["confidence"] is None and len(row["thinking"]) == 1500          # out-of-range confidence dropped, text capped


def test_giveup_is_recorded_and_not_counted_as_solved(client):
    ps = "ps-giveup"
    p = nxt(client, ps)
    r = giveup(client, ps, p, hints=1, conf=3)
    assert r["solution"] and r["explain"] and r["title"]
    row = db.one("SELECT * FROM practice_attempts WHERE psession=?", (ps,))
    assert row["gave_up"] == 1 and row["ok"] == 0 and row["confidence"] == 3
    ev = db.rows("SELECT payload FROM events WHERE type='drill_check' AND session_id='t'")
    assert all(json.loads(e["payload"])["ok"] for e in ev)                     # only real solves feed XP


def test_solved_problems_feed_xp_like_drills(client):
    ps = "ps-xp"
    p = nxt(client, ps)
    before = len(db.rows("SELECT id FROM events WHERE type='drill_check'"))
    solve(client, ps, p)
    after = db.rows("SELECT payload FROM events WHERE type='drill_check' ORDER BY id")
    assert len(after) == before + 1 and json.loads(after[-1]["payload"]).get("practice") is True


def test_calibration_math_and_summary(client):
    db.run("DELETE FROM practice_attempts")
    ps = "ps-cal"
    plan = [(3, True), (3, True), (3, False), (1, True), (1, False), (1, False), (2, True), (2, True)]
    for conf, ok in plan:
        p = nxt(client, ps)
        if ok:
            solve(client, ps, p, hints=0, conf=conf)
        else:
            giveup(client, ps, p, conf=conf)
    s = client.get("/api/practice/summary", params={"psession": ps}).json()
    lv = {x["c"]: x for x in s["calibration"]["levels"]}
    assert (lv[3]["n"], lv[3]["right"], lv[3]["pct"]) == (3, 2, 67)
    assert (lv[1]["n"], lv[1]["right"], lv[1]["pct"]) == (3, 1, 33)
    assert (lv[2]["n"], lv[2]["pct"]) == (2, 100)
    assert s["calibration"]["certain_and_wrong"] == 1 and s["calibration"]["lucky_guesses"] == 1 and s["calibration"]["rated"] == 8
    assert s["session"]["problems"] == 8 and s["session"]["solved"] == 5 and s["session"]["gave_up"] == 3
    assert s["weak"] and set(s["weak"][0]) == {"day", "concept", "misses"}
    e = client.post("/api/practice/end", headers=H, json={"psession": ps, "session_id": "t"}).json()
    assert e["session"]["problems"] == 8 and len(e["review"]) == 8


def test_validation(client):
    assert client.post("/api/practice/next", headers=H, json={"psession": "bad id!"}).status_code == 400
    assert client.post("/api/practice/next", headers=H, json={"psession": "x", "scope": "everything"}).status_code == 400
    assert client.post("/api/practice/next", json={"psession": "x"}).status_code == 403               # needs x-portal
    for pid in ("nonsense", "99~d01-fill", "1~nope", "1~..%2fx", "1~"):
        r = client.post(f"/api/practice/{pid}/hint", headers=H, json={"step": 1})
        assert r.status_code in (404, 405), (pid, r.status_code)
    p = nxt(client, "ps-val")
    big = client.post(f"/api/practice/{p['pid']}/check", headers=H, json={"psession": "ps-val", "answer": {"text": "x" * 30000}})
    assert big.status_code == 413
    bad_tok = client.post(f"/api/practice/{p['pid']}/check", headers=H, json={"psession": "ps-val", "answer": {"order": ["deadbeef"], "picks": ["deadbeef"], "blanks": 3, "lines": "x"}})
    assert bad_tok.status_code in (200, 422) and bad_tok.status_code != 500


def test_runs_out_of_problems_gracefully(client):
    db.run("DELETE FROM day_state")
    ps = "ps-exhaust"
    seen = 0
    for _ in range(40):
        p = nxt(client, ps)
        if p["done"]:
            assert "every problem" in p["reason"]
            break
        solve(client, ps, p)
        seen += 1
    assert seen == 15 and p["done"], seen                                       # a new learner has days 1-3: 15 problems
