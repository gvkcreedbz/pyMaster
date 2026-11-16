"""Backend smoke test for the JAVA track of the portal (throw-away data dir).  Run: python _dev_tools/portal_smoke_java.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
os.environ["PORTAL_TRACK"] = "java"
os.environ["PORTAL_DATA"] = tempfile.mkdtemp(prefix="portal_smoke_java_")
for k in ("CURSOR_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    os.environ.pop(k, None)
from fastapi.testclient import TestClient  # noqa: E402
from portal import content, main, track  # noqa: E402

problems = []


def check(name, cond, extra=""):
    print(("[ok]   " if cond else "[FAIL] ") + name + (f"  {extra}" if extra and not cond else ""))
    if not cond:
        problems.append(name)


check("track is java", track.ID == "java" and track.T["name"] == "Java Master")
days = content.load_days()
check("30 days parsed", len(days) == 30, len(days))
n_ex = sum(len(d["exercises"]) for d in days.values())
check("at least 200 exercises parsed", n_ex >= 200, n_ex)
print(f"       {n_ex} Java exercises")
for n, d in days.items():
    if not d["title"] or not d["scenario"] or not d["concepts"]:
        check(f"day {n} fields", False, f"title={bool(d['title'])} scen={bool(d['scenario'])} concepts={len(d['concepts'])}")
    if len(d["quiz"]) < 6 or any(not q["a"] for q in d["quiz"]):
        check(f"day {n} quiz", False, [q["n"] for q in d["quiz"] if not q["a"]] or len(d["quiz"]))
    if len(d["hints"]) != 3:
        check(f"day {n} hints", False, len(d["hints"]))
    if not d["exercises"]:
        check(f"day {n} has exercises", False)
    if not d["solution"].strip():
        check(f"day {n} solution", False)
    if "```python" in d.get("lesson", ""):
        check(f"day {n} lesson has no python fences", False)

H = {"x-portal": "1"}
with TestClient(main.app, base_url="http://127.0.0.1:8766") as c:
    r = c.post("/api/session/start", headers=H)
    check("session start", r.status_code == 200, r.text)
    sid = r.json()["session_id"]
    ov = c.get("/api/overview")
    check("overview ok", ov.status_code == 200 and len(ov.json()["days"]) == 30)
    check("overview announces java track", ov.json().get("track", {}).get("id") == "java", ov.json().get("track"))
    page = c.get("/")
    check("index served with java baked in", page.status_code == 200 and "Java Master" in page.text and "clike" in page.text)
    d3 = c.get("/api/day/3").json()
    check("day3 title", "Numbers" in d3["title"], d3["title"])
    # unfinished practice must compile, run and print a score line, and record the checks
    res = c.post("/api/run", headers=H, json={"kind": "practice", "day_no": 3, "code": d3["practice_starter"], "session_id": sid}).json()
    check("unfinished practice scores", "Score:" in res["output"], res["output"][-300:])
    check("checks parsed from [PASS]/[FAIL]", len(res.get("results", [])) > 3, res.get("results"))
    # solution scores 100% (hits the solution endpoint then runs it)
    check("solution view returns the blocks", "return" in c.get("/api/day/3/solution", params={"session_id": sid}).json()["solution"])
    sol = (track.SOL_DIR / "day03_Solution.java").read_text(encoding="utf-8")
    res = c.post("/api/run", headers=H, json={"kind": "practice", "day_no": 3, "code": sol, "session_id": sid}).json()
    import re
    m = re.search(r"Score: (\d+)/(\d+)", res["output"])
    check("reference solution scores full marks", bool(m) and m.group(1) == m.group(2), res["output"][-300:])
    # playground
    res = c.post("/api/run", headers=H, json={"kind": "playground", "code": track.JAVA_PLAY, "session_id": sid}).json()
    check("playground runs", "Hello from Java Master" in res["output"], res["output"][-300:])
    res = c.post("/api/run", headers=H, json={"kind": "playground", "code": "class Play { public static void main(String[] a) { int x = ; } }", "session_id": sid}).json()
    check("compile error reported, not crashed", res.get("returncode", 1) != 0 and "error" in res["output"].lower(), res["output"][-300:])
    # stdin
    res = c.post("/api/run", headers=H, json={"kind": "playground", "stdin": "Asha\n", "session_id": sid, "code":
                  "import java.util.Scanner;\nclass Play { public static void main(String[] a) { System.out.println(\"Hi \" + new Scanner(System.in).nextLine()); } }"}).json()
    check("stdin reaches the program", "Hi Asha" in res["output"], res["output"][-300:])
    # tutor (offline) answers with Java content
    r = c.post("/api/chat", headers=H, json={"session_id": sid, "text": "Where is a HashMap used in real projects?", "ctx": {"day_no": 10}})
    check("chat ok", r.status_code == 200, r.text[:200])
    evs = [json.loads(x) for x in r.text.splitlines() if x.strip()]
    ans = "".join(e["x"] for e in evs if e["t"] == "delta")
    check("offline tutor knows HashMap", "map" in ans.lower() and "python" not in ans.lower()[:200], ans[:200])
    # visuals
    r = c.post("/api/visual/diagram", headers=H, json={"code": "class A { public static void main(String[] a) { int x = 3; if (x > 2) { System.out.println(\"hi\"); } } }"})
    check("java flowchart", r.status_code == 200 and "flowchart" in r.text, r.text[:200])
    r = c.post("/api/visual/trace", headers=H, json={"code": "class A { public static void main(String[] a) { int x = 3; x++; System.out.println(x); } }"})
    check("java trace", r.status_code == 200 and r.json().get("steps"), r.text[:200])
    # blueprints + library + search
    bp = c.get("/api/blueprints").json()
    check("3 java blueprints", len(bp["items"]) >= 3, bp)
    lib = c.get("/api/library")
    check("library lists cheatsheets", lib.status_code == 200 and "java" in lib.text.lower())
    s = c.get("/api/search", params={"q": "stream"})
    check("search finds streams", s.status_code == 200 and "stream" in s.text.lower())
    d30 = c.get("/api/day/30/extra/FINAL_EXAM.md")
    check("day 30 exam served", d30.status_code == 200 and len(d30.text) > 500, d30.status_code)

print("\nALL OK" if not problems else f"\n{len(problems)} PROBLEMS: {problems}")
sys.exit(1 if problems else 0)
