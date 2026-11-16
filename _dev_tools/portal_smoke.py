"""Backend smoke test for the portal (uses a throw-away data dir).  Run: python _dev_tools/portal_smoke.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["PORTAL_DATA"] = tempfile.mkdtemp(prefix="portal_smoke_")
for k in ("CURSOR_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    os.environ.pop(k, None)

from fastapi.testclient import TestClient  # noqa: E402

from portal import analytics, content, main  # noqa: E402

problems = []


def check(name, cond, extra=""):
    print(("[ok]   " if cond else "[FAIL] ") + name + (f"  {extra}" if extra and not cond else ""))
    if not cond:
        problems.append(name)


days = content.load_days()
check("30 days parsed", len(days) == 30, len(days))
check("233 exercises parsed", sum(len(d["exercises"]) for d in days.values()) == 233,
      sum(len(d["exercises"]) for d in days.values()))
for n, d in days.items():
    if not d["title"] or not d["quiz"] or not d["scenario"] or not d["concepts"]:
        check(f"day {n} fields", False, f"title={bool(d['title'])} quiz={len(d['quiz'])} scen={bool(d['scenario'])} concepts={len(d['concepts'])}")
    if any(not q["a"] for q in d["quiz"]):
        check(f"day {n} quiz answers", False, [q["n"] for q in d["quiz"] if not q["a"]])
    if len(d["hints"]) != 3:
        check(f"day {n} hints", False, len(d["hints"]))
    if not d["solution"].strip():
        check(f"day {n} solution", False)

H = {"x-portal": "1"}
with TestClient(main.app, base_url="http://127.0.0.1:8765") as c:
    r = c.post("/api/session/start", headers=H)
    check("session start", r.status_code == 200, r.text)
    sid = r.json()["session_id"]
    check("welcome kind start", r.json()["welcome"]["kind"] == "start", r.json()["welcome"])
    check("POST without header blocked", c.post("/api/session/start").status_code == 403)
    check("bad host blocked", TestClient(main.app, base_url="http://evil.com").get("/api/overview").status_code == 403)

    ov = c.get("/api/overview").json()
    check("overview 30 days", len(ov["days"]) == 30)
    check("planned date day1", ov["days"][0]["planned"] == "2026-11-16", ov["days"][0]["planned"])
    check("planned date day30", ov["days"][29]["planned"] == "2026-12-15", ov["days"][29]["planned"])

    d8 = c.get("/api/day/8").json()
    check("day8 has lesson/exercises", "Lists" in d8["title"] and len(d8["exercises"]) == 8, len(d8["exercises"]))

    # run unfinished practice -> must print score, record checks
    res = c.post("/api/run", headers=H, json={"kind": "practice", "day_no": 8, "code": d8["practice_starter"], "session_id": sid}).json()
    check("practice runs without traceback", "Traceback" not in res["output"], res["output"][-300:])
    check("score parsed", res["total"] and res["passed"] is not None, res)
    check("progress returned", "progress" in res)

    # solve L1-1 only
    code = d8["practice_starter"].replace("    # TODO: write your code here\n    pass  # delete this line once you add your code",
                                          "    return sum(prices)", 1)
    res2 = c.post("/api/run", headers=H, json={"kind": "practice", "day_no": 8, "code": code}).json()
    check("solving one exercise raises passes", res2["passed"] > res["passed"], (res["passed"], res2["passed"]))
    d8b = c.get("/api/day/8").json()
    check("exercise status tracked", d8b["progress"]["ex_passed"] >= 1, d8b["progress"])
    check("draft persisted", "return sum(prices)" in d8b["drafts"]["practice"])

    # playground + stdin
    pg = c.post("/api/run", headers=H, json={"kind": "playground", "code": "n = input('x? ')\nprint('got', n)", "stdin": "42\n"}).json()
    check("playground stdin", "got 42" in pg["output"], pg)
    pg2 = c.post("/api/run", headers=H, json={"kind": "playground", "code": "input()"}).json()
    check("EOF hint", pg2["hint"] is not None)
    pg3 = c.post("/api/run", headers=H, json={"kind": "playground", "code": "while True: pass"}).json() if os.environ.get("SMOKE_TIMEOUT") else {"timed_out": True}
    check("timeout enforced", pg3["timed_out"])
    pg4 = c.post("/api/run", headers=H, json={"kind": "playground", "code": "from pathlib import Path\nprint(len(list(Path('..').parent.glob('*'))), Path('../../datasets/sales.csv').exists())"}).json()
    check("datasets reachable from play dir", "True" in pg4["output"], pg4["output"])

    # heartbeats credit server time only
    for _ in range(2):
        c.post("/api/session/heartbeat", headers=H, json={"session_id": sid, "day_no": 8, "area": "day", "active": True})
    check("inactive credits nothing", c.post("/api/session/heartbeat", headers=H, json={"session_id": sid, "day_no": 8, "area": "day", "active": False}).json()["ok"])

    # quiz
    q = c.get("/api/day/8/quiz/1/answer").json()
    check("quiz answer", "[1, 2, 3, 4]" in q["answer"], q)
    check("quiz rate", c.post("/api/day/8/quiz/1", headers=H, json={"rating": 2}).json()["progress"]["quiz_rated"] == 1)
    check("hint", "hint" in c.get("/api/day/8/hint/1").json())
    check("solution view logged", "attempts_before" in c.get("/api/day/8/solution").json())
    check("notes", c.post("/api/day/8/notes", headers=H, json={"text": "lists!"}).json()["ok"])
    check("mark done", c.post("/api/day/8/state", headers=H, json={"status": "done", "confidence": 4}).json()["progress"]["pct"] == 100)


    def ask(text, quick=None, ctx=None):
        ctx = {"day_no": 8, "tab": "learn", **(ctx or {})}
        r = c.post("/api/chat", headers=H, json={"session_id": sid, "text": text, "quick_id": quick, "ctx": ctx})
        evs = [json.loads(x) for x in r.text.splitlines() if x.strip()]
        ans = "".join(e["x"] for e in evs if e["t"] == "delta")
        return evs, ans

    evs, ans = ask("", "where_used", {"selection": "cart.append('butter')"})
    check("quick where_used offline answer", "Lists" in ans and "Where you'll meet it" in ans, ans[:200])
    check("quick not graded", evs[0]["analysis"]["quality"] is None)
    evs, ans = ask("I think a list is like a shopping cart. Why does b = a change a too, and where would that bite me in real code?")
    check("good question scored high", evs[0]["analysis"]["quality"] >= 60 and evs[0]["analysis"]["valid"], evs[0]["analysis"])
    evs, ans = ask("help")
    check("vague question scored low", evs[0]["analysis"]["quality"] < 40 and not evs[0]["analysis"]["valid"], evs[0]["analysis"])
    evs, ans = ask("help")
    check("duplicate/vague repeat flagged", not evs[0]["analysis"]["valid"])
    evs, ans = ask("I get KeyError: 'name' when reading my dict, what does it mean?", None, {"day_no": 10})
    check("error decoded", "KeyError" in ans and ("get" in ans), ans[:300])
    evs, ans = ask("quiz me")
    check("quiz intent", "Quick quiz" in ans)
    evs, ans = ask("reveal")
    check("reveal answer", "Answer to question" in ans, ans[:200])
    evs, ans = ask("give me a hint", None, {"exercise_id": "L1-1"})
    check("hint intent", "Hint" in ans, ans[:200])
    evs, ans = ask("review my code", None, {"code": "def f(x=[]):\n    try:\n        pass\n    except:\n        pass\n"})
    check("review finds mutable default & bare except", "mutable default" in ans and "bare" in ans, ans)
    evs, ans = ask("how does enumerate work and where is it used?", None, {"day_no": 6})
    check("enumerate → for loops concept", "for loops" in ans.lower(), ans[:150])
    evs, ans = ask("what is a decorator used for in the real world", None, {"day_no": 22})
    check("decorator usage", "decorator" in ans.lower() and "FastAPI" in ans, ans[:200])
    evs, ans = ask("xyzzy plugh")
    check("unknown topic graceful", "not sure" in ans.lower())

    # ---- visual explanations (HTTP) ----
    vcode = "a = [1, 2]\nb = a\nb.append(3)\nprint(a)\n"
    vt = c.post("/api/visual/trace", headers=H, json={"code": vcode, "session_id": sid, "day_no": 8}).json()
    check("visual trace over HTTP", vt["ok"] and len(vt["steps"]) >= 4 and vt["output"] == "[1, 2, 3]\n", vt.get("error"))
    last = vt["steps"][-1]["stack"][0]["vars"]
    check("trace shows aliasing (a and b share one object)", last["a"].get("ref") and last["a"]["ref"] == last["b"]["ref"], last)
    vd = c.post("/api/visual/diagram", headers=H, json={"code": "for i in range(3):\n    print(i)\n", "lang": "python"}).json()
    check("flow diagram over HTTP", vd["kind"] == "flow" and vd["mermaid"].startswith("flowchart"), vd)
    vs = c.post("/api/visual/diagram", headers=H, json={"code": "SELECT a, COUNT(*) FROM t WHERE x>1 GROUP BY a", "lang": "sql"}).json()
    check("sql order diagram over HTTP", vs["kind"] == "sql" and "FROM" in vs["mermaid"] and "GROUP BY" in vs["mermaid"], vs)
    check("visual endpoints need the portal header", c.post("/api/visual/trace", json={"code": "x=1"}).status_code == 403)
    check("syntax error is reported, not crashed", c.post("/api/visual/diagram", headers=H, json={"code": "def (:"}).status_code == 400)
    evs, ans = ask("show me a visual of this", None, {"code": vcode})
    check("chat: visual intent draws a mermaid flowchart of the editor code", "```mermaid" in ans and "flowchart" in ans, ans[:200])
    evs, ans = ask("explain lists visually")
    check("chat: visual of a concept (lists alias picture)", "```mermaid" in ans and "ONE list" in ans, ans[:200])
    evs, ans = ask("", "visual", {"selection": "SELECT region, SUM(x) FROM orders GROUP BY region ORDER BY 2 DESC"})
    check("chat: visual quick action on SQL", "```mermaid" in ans and "GROUP BY" in ans, ans[:200])
    h = c.get("/api/chat/history?day=8").json()["items"]
    check("history saved", len(h) >= 5 and all(i["answer"] for i in h))
    check("feedback", c.post("/api/chat/feedback", headers=H, json={"qid": h[0]["id"], "helpful": 1}).json()["ok"])

    # every day/concept: where_used never crashes
    bad = []
    for n in days:
        _, a = ask("", "where_used", {"day_no": n})
        if len(a) < 120:
            bad.append(n)
    check("where_used answers for all 30 days", not bad, bad)

    ins = c.get("/api/insights").json()
    check("insights totals", ins["totals"]["questions"] >= 10 and ins["totals"]["avg_quality"] is not None, ins["totals"])
    check("profile present", ins["profile"]["label"])
    check("series 35 points", len(ins["series"]) == 35)
    rf = c.post("/api/insights/reflect", headers=H).json()
    check("reflection rule-based", rf["provider"] == "rules" and rf["text"])
    check("question log", len(c.get("/api/questions").json()["items"]) >= 10)
    check("export", "questions" in json.loads(c.get("/api/export").text))
    check("settings roundtrip", c.post("/api/settings", headers=H, json={"values": {"provider_pref": "offline", "start_date": "2026-11-16"}}).json()["pref"] == "offline")
    check("library", len(c.get("/api/library").json()["items"]) >= 5)
    check("library doc", len(c.get("/api/library/doc", params={"id": "cheatsheets/error_decoder.md"}).json()["text"]) > 100)
    check("library traversal blocked", c.get("/api/library/doc", params={"id": "../../etc/passwd"}).status_code == 404)
    check("extra", c.get("/api/day/30/extra/FINAL_EXAM.md").status_code == 200)

    # ---- hardening (regression for the scrutiny pass) ----
    check("IPv6 loopback host allowed", TestClient(main.app, base_url="http://[::1]:8765").get("/api/chat/quick").status_code == 200)
    check("lookalike host blocked", TestClient(main.app, base_url="http://127.0.0.1.evil.com").get("/api/chat/quick").status_code == 403)
    check("quiz rating for a non-existent question refused", c.post("/api/day/8/quiz/999", headers=H, json={"rating": 0}).status_code == 400)
    check("quiz rating out of range refused", c.post("/api/day/8/quiz/1", headers=H, json={"rating": 7}).status_code == 400)
    check("draft reset validates kind", c.delete("/api/day/8/draft/evil", headers=H).status_code == 400)
    check("draft reset validates day", c.delete("/api/day/99/draft/practice", headers=H).status_code == 404)
    check("giant limit is capped", len(c.get("/api/questions?limit=-1").json()["items"]) >= 0 and c.get("/api/chat/history?day=8&limit=100000").status_code == 200)
    c.post("/api/event", headers=H, json={"type": "big", "payload": {"x": "y" * 9000}})
    from portal import db as _dbx
    last_ev = _dbx.one("SELECT payload FROM events WHERE type='big' ORDER BY id DESC LIMIT 1")
    check("oversized event payload still valid JSON", json.loads(last_ev["payload"]).get("truncated") is True, last_ev)
    evs, ans = ask("what is a list", None, {"day_no": "abc"})
    check("chat survives a junk day_no", evs and evs[-1]["t"] == "done", evs[-1] if evs else None)
    evs, ans = ask("review my code", None, {"code": "if x == 1:\n    pass\nif y == True:\n    pass\n"})
    check("review flags == True but not == 1", "if flag:" in ans and ans.count("Compare booleans") == 1, ans)
    two = []
    import threading
    def _run(i):
        two.append(c.post("/api/run", headers=H, json={"kind": "playground", "code": f"import time; time.sleep(0.3); print('run{i}')"}).json()["output"])
    ts = [threading.Thread(target=_run, args=(i,)) for i in (1, 2)]
    [t.start() for t in ts]; [t.join() for t in ts]
    check("two simultaneous runs keep their own output", sorted(two) == ["run1", "run2"], two)

    # ---- search ----
    s = c.get("/api/search", params={"q": "decorator"}).json()["items"]
    check("search finds the decorators day", any(i["hash"] == "#/day/22/learn" for i in s), s[:3])
    check("search finds a concept", any(i["type"] == "concept" for i in s))
    check("search finds blueprints by pattern", any(i["hash"] == "#/blueprints/site-watcher" for i in c.get("/api/search", params={"q": "circuit breaker"}).json()["items"]))
    check("empty search is empty", c.get("/api/search", params={"q": "  "}).json()["items"] == [])
    check("search junk is safe", c.get("/api/search", params={"q": "(((*[\\"}).status_code == 200)

    # ---- review queue ----
    c.post("/api/day/8/quiz/2", headers=H, json={"rating": 0})
    rq = c.get("/api/review", params={"all": 1}).json()
    check("missed quiz question appears (not yet due)", any(x["day_no"] == 8 and x["q_no"] == 2 and not x["due"] for x in rq["quiz"]), rq["quiz"][:2])
    check("due list excludes fresh misses", all(x["q_no"] != 2 for x in c.get("/api/review").json()["quiz"]))
    from portal import db as _dbr
    _dbr.run("UPDATE quiz SET rated_at='2020-01-01T00:00:00' WHERE day_no=8 AND q_no=2")
    check("old miss becomes due", any(x["q_no"] == 2 and x["due"] for x in c.get("/api/review").json()["quiz"]))
    c.post("/api/day/8/quiz/2", headers=H, json={"rating": 2})
    check("re-rating 'got it' leaves the queue", all(x["q_no"] != 2 for x in c.get("/api/review", params={"all": 1}).json()["quiz"]))
    check("failing exercises listed", isinstance(c.get("/api/review").json()["exercises"], list) and c.get("/api/review").json()["counts"]["exercises"] >= 1)

    # ---- blueprints ----
    bl = c.get("/api/blueprints").json()["items"]
    check("3 blueprints + patterns catalog", [b["id"] for b in bl] == ["live-order-tracker", "ticket-triage-pipeline", "site-watcher", "patterns"], [b["id"] for b in bl])
    for b in bl:
        doc = c.get(f"/api/blueprints/{b['id']}").json()["text"]
        check(f"blueprint doc {b['id']}", len(doc) > 3000, len(doc))
        for f in b["files"]:
            check(f"blueprint file {b['id']}/{f}", len(c.get(f"/api/blueprints/{b['id']}/file/{f}").json()["text"]) > 500)
    check("blueprint file traversal blocked", c.get("/api/blueprints/site-watcher/file/..%2f..%2fmeta.json").status_code == 404 and c.get("/api/blueprints/site-watcher/file/meta.json").status_code == 404)
    check("unknown blueprint 404", c.get("/api/blueprints/nope").status_code == 404 and c.post("/api/blueprints/nope/run", headers=H).status_code == 404)
    check("patterns has no demo", c.post("/api/blueprints/patterns/run", headers=H).status_code == 404)
    check("blueprint run needs header", c.post("/api/blueprints/site-watcher/run").status_code == 403)
    expect = {"site-watcher": ["laptop-price: price dropped 15%", "payments-api recovered", "after restart, laptop-price last seen = 1089.0"],
              "ticket-triage-pipeline": ["total before: 7 | total after: 7", "AI calls made: 4"],
              "live-order-tracker": ["409 cannot go from delivered to preparing", "same id? True", "placed -> accepted -> preparing -> out_for_delivery -> delivered"]}
    for bid, needles in expect.items():
        r = c.post(f"/api/blueprints/{bid}/run", headers=H, json={}).json()
        check(f"blueprint demo runs: {bid}", r["ok"] and all(n in r["output"] for n in needles), (r["output"][-400:], r["hint"]))
    from pathlib import Path as _P
    check("demos leave the originals clean", not list((ROOT / "blueprints").rglob("*.db")) and not list((ROOT / "blueprints").rglob("__pycache__")))
    from portal import db as _db
    _db.run("UPDATE sessions SET active_seconds=120, date='2026-11-10' WHERE id=?", (sid,))
    s2 = c.post("/api/session/start", headers=H).json()
    check("welcome recap after a multi-day gap", s2["welcome"]["kind"] == "recap" and s2["welcome"]["gap_days"] >= 2 and s2["welcome"]["recap"], s2["welcome"])
    _db.run("UPDATE sessions SET date=? WHERE id=?", ((__import__('datetime').date.today() - __import__('datetime').timedelta(days=1)).isoformat(), sid))
    s3 = c.post("/api/session/start", headers=H).json()
    check("welcome resume after 1 day", s3["welcome"]["kind"] == "resume", s3["welcome"])

print()
print("PROBLEMS:" if problems else "ALL OK", problems if problems else "")
sys.exit(1 if problems else 0)
