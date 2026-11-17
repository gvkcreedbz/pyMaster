"""Tests for the drills extension (portal/ex_drills.py + portal/drills_core.py).
Run once per track:  PORTAL_TRACK=python|java  python -m pytest _dev_tools/test_ex_drills.py -q -p no:cacheprovider
(or  powershell -File _dev_tools\\test_tracks.ps1 _dev_tools/test_ex_drills.py  for both)
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
os.environ["PORTAL_DATA"] = tempfile.mkdtemp(prefix="drills_test_")
for k in ("CURSOR_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402

from portal import content, db, drills_core as core, ex_drills, main, track  # noqa: E402

H = {"x-portal": "1"}
JAVA = track.IS_JAVA


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app, base_url="http://127.0.0.1:8765") as c:
        yield c


def shipped():
    """[(day, drill dict)] of every shipped drill for the selected track."""
    out = []
    for n in range(1, 31):
        f = core.find_file(track.DAYS_DIR, n)
        if f:
            doc = core.load_doc(f)
            out += [(n, d) for d in doc["drills"]]
    return out


def good_answer(n, d):
    tok = core.Tok(ex_drills._secret, n, d["id"])
    t = d["type"]
    if t == "parsons":
        ln = len(d["lines"])
        a = {"order": [tok("L", i) for i in range(ln)], "indents": list(d.get("indent") or [0] * ln)}
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


def bad_answer(n, d):
    tok = core.Tok(ex_drills._secret, n, d["id"])
    t = d["type"]
    if t == "parsons":
        ln = len(d["lines"])
        return {"order": [tok("L", i) for i in reversed(range(ln))], "indents": [0] * ln}
    if t == "fill":
        return {"blanks": ["zzz-not-it"] * len(d["blanks"])}
    if t == "predict":
        return {"text": "definitely not the output"}
    if t == "bug":
        wrong = [x for x in range(1, 40) if x not in d["bug_lines"]][:1]
        return {"lines": wrong, "option": tok("O", (d["answer"] + 1) % len(d["options"]))}
    return {"picks": [tok("I", len(d["issues"]))]}          # the first non-issue only


def test_there_are_drills_of_every_type():
    types = {d["type"] for _n, d in shipped()}
    assert types == set(core.TYPES), types


def test_every_shipped_file_lints_clean():
    for n in range(1, 31):
        f = core.find_file(track.DAYS_DIR, n)
        if f:
            doc = core.load_doc(f)
            assert doc is not None, f
            assert core.lint_doc(doc, n, JAVA) == [], (f, core.lint_doc(doc, n, JAVA))


def test_list_never_leaks_answers(client):
    secret_keys = {"expected", "answers", "answer", "bug_lines", "fixed_code", "issues", "non_issues", "regex", "alternatives", "buggy_runs"}
    for n in sorted({n for n, _d in shipped()}):
        r = client.get(f"/api/drills/{n}", params={"session_id": "abc"})
        assert r.status_code == 200
        for v in r.json()["drills"]:
            assert not (secret_keys & set(v)), (n, v["id"], secret_keys & set(v))
            assert "explain" not in v                            # revealed only after an attempt
            for it in v.get("items", []):
                assert not ({"real", "why"} & set(it))
            for b in v.get("blanks", []):
                assert "answers" not in b


def test_right_answers_pass_and_wrong_ones_do_not(client):
    for n, d in shipped():
        base = f"/api/drills/{n}/{d['id']}"
        r = client.post(base + "/check", headers=H, json={"answer": bad_answer(n, d), "session_id": "t1"})
        assert r.status_code == 200, (d["id"], r.text)
        assert r.json()["ok"] is False, f"{d['id']}: a wrong answer was accepted"
        assert r.json()["explain"]
        r = client.post(base + "/check", headers=H, json={"answer": good_answer(n, d), "session_id": "t1"})
        assert r.status_code == 200, (d["id"], r.text)
        body = r.json()
        assert body["ok"] is True and body["score"] == 1.0, (d["id"], body)
        assert body["solution"], d["id"]


def test_attempts_events_and_state_are_recorded(client):
    n, d = shipped()[0]
    rows = db.rows("SELECT ok FROM drill_attempts WHERE day_no=? AND drill_id=? ORDER BY id", (n, d["id"]))
    assert [r["ok"] for r in rows] == [0, 1]                    # the wrong try, then the right one
    ev = [json.loads(e["payload"]) for e in db.rows("SELECT payload FROM events WHERE type='drill_check' AND day_no=?", (n,))]
    assert any(p["drill"] == d["id"] and p["ok"] is True for p in ev)
    view = next(v for v in client.get(f"/api/drills/{n}", params={"session_id": "t1"}).json()["drills"] if v["id"] == d["id"])
    assert view["state"]["solved"] is True and view["state"]["attempts"] == 2
    assert view["explain"]                                      # visible now that it was attempted


def test_giveup_reveals_but_never_counts_as_done(client):
    n = shipped()[-1][0]
    drills = [d for m, d in shipped() if m == n]
    d = drills[-1]
    db.run("DELETE FROM drill_attempts WHERE day_no=? AND drill_id=?", (n, d["id"]))      # an earlier test solved it: start fresh
    before = client.get("/api/drills/summary").json()["days"][str(n)]["done"]
    r = client.post(f"/api/drills/{n}/{d['id']}/giveup", headers=H, json={"session_id": "t2"})
    assert r.status_code == 200 and r.json()["solution"] and r.json()["explain"]
    after = client.get("/api/drills/summary").json()["days"][str(n)]
    assert after["done"] == before and after["attempted"] >= 1
    view = next(v for v in client.get(f"/api/drills/{n}").json()["drills"] if v["id"] == d["id"])
    assert view["state"]["gave_up"] is True and view["state"]["solved"] is False


def test_summary_counts(client):
    s = client.get("/api/drills/summary").json()
    per_day = {}
    for n, _d in shipped():
        per_day[n] = per_day.get(n, 0) + 1
    assert s["track"] == track.ID
    assert {int(k): v["total"] for k, v in s["days"].items()} == per_day
    assert s["total"] == sum(per_day.values())
    assert s["done"] == sum(v["done"] for v in s["days"].values())


def test_validation(client):
    n, d = shipped()[0]
    assert client.get("/api/drills/99").status_code == 404
    assert client.post(f"/api/drills/{n}/nope/check", headers=H, json={"answer": {}}).status_code == 404
    assert client.post(f"/api/drills/{n}/..%2f..%2fx/check", headers=H, json={"answer": {}}).status_code in (404, 422)
    assert client.post(f"/api/drills/{n}/{d['id']}/check", json={"answer": {}}).status_code == 403          # needs x-portal
    r = client.post(f"/api/drills/{n}/{d['id']}/check", headers=H, json={"answer": {"text": "x" * 20000}})
    assert r.status_code == 413
    for junk in (None, 5, "str", [], {"order": "no"}, {"blanks": 3}, {"lines": "x"}, {"picks": {}}):
        r = client.post(f"/api/drills/{n}/{d['id']}/check", headers=H, json={"answer": junk})
        assert r.status_code in (422, 200), (junk, r.status_code)
        assert r.status_code != 500, junk
    # a stale token (from another session secret) is refused, not crashed on
    parsons = next(((m, x) for m, x in shipped() if x["type"] == "parsons"), None)
    if parsons:
        m, x = parsons
        r = client.post(f"/api/drills/{m}/{x['id']}/check", headers=H, json={"answer": {"order": ["deadbeef"], "indents": [0]}})
        assert r.status_code == 422


def test_shuffle_is_stable_per_session_and_never_solved(client):
    for n, d in shipped():
        if d["type"] != "parsons":
            continue
        a = client.get(f"/api/drills/{n}", params={"session_id": "s1"}).json()["drills"]
        b = client.get(f"/api/drills/{n}", params={"session_id": "s1"}).json()["drills"]
        assert [v.get("items") for v in a] == [v.get("items") for v in b]
        tok = core.Tok(ex_drills._secret, n, d["id"])
        v = next(v for v in a if v["id"] == d["id"])
        placed = [it["id"] for it in v["items"] if it["id"] in {tok("L", i) for i in range(len(d["lines"]))}]
        assert placed != [tok("L", i) for i in range(len(d["lines"]))], "handed out the solved order"


def test_day_tab_data_matches_content():
    assert content.load_days()
    for n, _d in shipped():
        assert content.day(n), n
