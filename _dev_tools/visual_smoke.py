"""Smoke test for the visual explainers. Run: python _dev_tools/visual_smoke.py"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["PORTAL_DATA"] = tempfile.mkdtemp(prefix="visual_smoke_")
from portal import visual  # noqa: E402

bad = []


def check(name, cond, extra=""):
    print(("[ok]   " if cond else "[FAIL] ") + name + ("" if cond else f"  {extra}"))
    if not cond:
        bad.append(name)


code = '''a = [1, 2, 3]
b = a
b.append(4)
def total(xs):
    s = 0
    for x in xs:
        s += x
    return s
print(total(a), "done")
d = {"k": [1, 2]}
'''
t = visual.trace(code)
check("trace ok", t["ok"] and not t["error"], t)
check("trace has steps", t["total_steps"] > 8, t["total_steps"])
last = t["steps"][-1]
check("global frame has a,b", {"a", "b"} <= set(last["stack"][0]["vars"]), last["stack"][0]["vars"].keys())
va, vb = last["stack"][0]["vars"]["a"], last["stack"][0]["vars"]["b"]
check("aliasing: a and b point at the same object", va.get("ref") and va["ref"] == vb["ref"], (va, vb))
check("append visible in heap", [i["p"] for i in last["heap"][str(va["ref"]) if str(va["ref"]) in last["heap"] else va["ref"]]["items"]] == ["1", "2", "3", "4"])
check("function frame captured", any(len(s["stack"]) == 2 and s["stack"][1]["name"] == "total()" for s in t["steps"]))
check("return value recorded", any("ret" in s for s in t["steps"]))
check("output captured", "10 done" in t["output"], t["output"])

e = visual.trace("x = 1\ny = x / 0\n")
check("exception recorded", e["ok"] and e["error"]["type"] == "ZeroDivisionError" and e["error"]["line"] == 2, e.get("error"))
inf = visual.trace("i = 0\nwhile True:\n    i += 1\n", max_steps=40)
check("infinite loop truncated safely", inf["ok"] and inf["truncated"] and inf["total_steps"] == 40, inf.get("error"))
check("syntax error handled", not visual.trace("def (:")["ok"])
inp = visual.trace("n = input('x? ')\nprint(n)\n", stdin="hi\n")
check("stdin supported", "hi" in inp["output"], inp.get("output"))
cls = visual.trace("class C:\n    def __init__(self):\n        self.x = [1]\nc = C()\nc.x.append(2)\n")
check("object attrs captured", any(b["k"] == "object" for b in cls["steps"][-1]["heap"].values()))

fc = visual.flowchart(code)
check("flowchart header", fc.startswith("flowchart TD"))
check("flowchart has decision for loop", "for x in xs" in fc and "subgraph" in fc, fc)
fc2 = visual.flowchart("if age >= 18:\n    print('adult')\nelif age > 12:\n    print('teen')\nelse:\n    print('kid')\n")
check("if/elif/else branches", fc2.count("yes") >= 2 and "no" in fc2, fc2)
fc3 = visual.flowchart("try:\n    n = int(input())\nexcept ValueError:\n    n = 0\n")
check("try/except", "except ValueError" in fc3)
fc4 = visual.flowchart("import pandas as pd\ndf = pd.read_csv('a.csv')\nres = df.groupby('region')['price'].sum().sort_values().head(3)\n")
check("method chain expanded", ".groupby" in fc4 and ".sort_values" in fc4 and ".head" in fc4, fc4)
big = visual.flowchart("\n".join(f"x{i} = {i}" for i in range(200)))
check("long code trimmed, not crashed", "trimmed" in big)
check("quotes escaped", '"' not in visual._clean('say "hi"'))

sq = visual.diagram("SELECT region, SUM(price) AS rev FROM sales s JOIN products p ON s.pid = p.id WHERE price > 10 GROUP BY region HAVING rev > 100 ORDER BY rev DESC LIMIT 3", "sql")
m = sq["mermaid"]
check("sql diagram order", sq["kind"] == "sql" and m.index("FROM") < m.index("WHERE") < m.index("GROUP BY") < m.index("HAVING") < m.index("SELECT") < m.index("ORDER BY") < m.index("LIMIT"), m)
check("diagram() picks flow for python", visual.diagram(code)["kind"] == "flow")
check("diagram() detects bare sql", visual.diagram("SELECT a FROM t WHERE a > 1")["kind"] == "sql")

print("\nALL OK" if not bad else f"\nPROBLEMS: {bad}")
sys.exit(1 if bad else 0)
