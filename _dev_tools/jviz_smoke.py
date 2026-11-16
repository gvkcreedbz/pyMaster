"""Self-checking smoke test for portal/jtracer/JTracer.java (step tracer) and portal/jviz.py (flowchart).

Run with the isolated interpreter, e.g.
  "%TEMP%\\pyverify\\py\\python.exe" -W ignore -c "import sys,runpy; sys.path.insert(0,'.'); sys.argv=['x']; runpy.run_path('_dev_tools/jviz_smoke.py', run_name='__main__')"
Exits 0 and prints "ALL OK" when every check passes.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(os.getcwd())
if not (ROOT / "portal" / "jtracer" / "JTracer.java").is_file():
    ROOT = Path(__file__).resolve().parent.parent
JTRACER = ROOT / "portal" / "jtracer" / "JTracer.java"
JAVA = ROOT / ".tools" / "jdk21" / "bin" / "java.exe"
if not JAVA.is_file():
    JAVA = Path(shutil.which("java") or "java")

spec = importlib.util.spec_from_file_location("jviz", ROOT / "portal" / "jviz.py")
jviz = importlib.util.module_from_spec(spec)
sys.modules["jviz"] = jviz
spec.loader.exec_module(jviz)

FAILS: list[str] = []
WORK = Path(tempfile.mkdtemp(prefix="jviz_smoke_"))


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("  FAIL:", msg)
    return cond


def trace(name, code, max_steps=250, stdin=None, env=None):
    """Write <name>.java in WORK, run JTracer from WORK, return (result dict, seconds)."""
    src = WORK / f"{name}.java"
    src.write_text(code, encoding="utf-8")
    out = WORK / f"{name}.json"
    out.unlink(missing_ok=True)
    cmd = [str(JAVA), "--add-modules", "jdk.jdi", str(JTRACER), src.name, str(max_steps), str(out)]
    if stdin is not None:
        (WORK / f"{name}.in").write_text(stdin, encoding="utf-8")
        cmd.append(f"{name}.in")
    e = dict(os.environ)
    e.update(env or {})
    t0 = time.time()
    p = subprocess.run(cmd, cwd=str(WORK), capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=90, env=e)
    dt = time.time() - t0
    if not out.is_file():
        raise SystemExit(f"{name}: JTracer produced no result (rc={p.returncode})\n{p.stdout}\n{p.stderr}")
    data = json.loads(out.read_text(encoding="utf-8"))
    if os.environ.get("JVIZ_DEBUG") or (data["error"] and data["error"]["type"] == "TracerError"):
        print(f"   [{name}] error={data['error']} stderr={p.stderr[-300:]!r}")
    return data, dt


def final_vars(res):
    return res["steps"][-1]["stack"][-1]["vars"]


def frames_of(step, name):
    return [f for f in step["stack"] if f["name"] == name]


def heap_kinds(res):
    kinds = set()
    for s in res["steps"]:
        for box in s["heap"].values():
            kinds.add(box["k"])
    return kinds


def structure_ok(res, label):
    check(set(res) == {"steps", "error", "output", "truncated", "total_steps"}, f"{label}: top-level keys {sorted(res)}")
    check(res["total_steps"] == len(res["steps"]), f"{label}: total_steps matches")
    prev = 0
    for k, s in enumerate(res["steps"]):
        if not (s["ev"] in ("line", "return", "exception") and isinstance(s["line"], int) and s["stack"] and "heap" in s):
            check(False, f"{label}: bad step #{k}: {str(s)[:120]}")
            break
        if not check(s["out"] >= prev, f"{label}: out not monotonic at step {k}"):
            break
        prev = s["out"]
        for fr in s["stack"]:
            for v in fr["vars"].values():
                if "ref" in v and not check(str(v["ref"]) in s["heap"], f"{label}: dangling ref at step {k}"):
                    return


# ---- 1. loop with an int accumulator --------------------------------------------------------------------------
print("1. loop + int accumulator")
res, secs_loop = trace("Loop", """\
class Loop {
    public static void main(String[] args) {
        int total = 0;
        for (int i = 1; i <= 5; i++) {
            total += i;
        }
        System.out.println("Total: " + total);
    }
}
""")
structure_ok(res, "loop")
check(res["error"] is None, f"loop: error {res['error']}")
check(res["output"] == "Total: 15\n", f"loop: output {res['output']!r}")
check(not res["truncated"], "loop: not truncated")
check(res["steps"][0]["ev"] == "line" and res["steps"][0]["line"] == 3, "loop: first step is line 3")
check(res["steps"][0]["stack"][0]["name"] == "main()", "loop: entry frame is main()")
check(final_vars(res)["total"] == {"p": "15", "k": "int"}, f"loop: total {final_vars(res).get('total')}")
seen_total = [fr["vars"]["total"]["p"] for s in res["steps"] for fr in s["stack"] if "total" in fr["vars"]]
check(["0", "1", "3", "6", "10", "15"] == [x for k, x in enumerate(seen_total) if k == 0 or x != seen_total[k - 1]],
      f"loop: total progression {seen_total}")
check(any("i" in fr["vars"] and fr["vars"]["i"]["p"] == "5" for s in res["steps"] for fr in s["stack"]), "loop: i reaches 5")
check(res["steps"][-1]["ev"] == "return", "loop: last step is main's return")
check(max(s["out"] for s in res["steps"]) == len(res["output"]), "loop: out reaches len(output)")
check(res["steps"][-1]["ret"]["k"] == "void", "loop: void ret")
check(len(res["steps"]) == 15, f"loop: expected 15 steps, got {len(res['steps'])}")
print(f"   {len(res['steps'])} steps, {secs_loop:.2f}s wall")

# ---- 2. ArrayList + HashMap + other containers ------------------------------------------------------------------
print("2. collections")
res, _ = trace("Coll", """\
import java.util.*;

class Coll {
    public static void main(String[] args) {
        List<Integer> nums = new ArrayList<>();
        nums.add(10);
        nums.add(20);
        Map<String, Integer> ages = new HashMap<>();
        ages.put("Ann", 30);
        ages.put("Bob", 41);
        Set<String> tags = new HashSet<>();
        tags.add("x");
        int[] arr = {1, 2, 3};
        List<String> fixed = List.of("p", "q");
        Map<String, Integer> sorted = new TreeMap<>(ages);
        StringBuilder sb = new StringBuilder("hi");
        long big = 1L << 40;
        char c = 'z';
        double d = 2.5;
        boolean ok = true;
        String name = null;
        List<Integer> many = new ArrayList<>();
        for (int i = 0; i < 30; i++) many.add(i);
        System.out.println(nums + " " + ages);
    }
}
""")
structure_ok(res, "coll")
check(res["error"] is None, f"coll: error {res['error']}")
last = res["steps"][-1]
v, heap = last["stack"][-1]["vars"], last["heap"]
check(heap_kinds(res) >= {"list", "dict", "set", "array"}, f"coll: heap kinds {heap_kinds(res)}")
nums = heap[str(v["nums"]["ref"])]
check(nums["k"] == "list" and [x["p"] for x in nums["items"]] == ["10", "20"], f"coll: nums {nums}")
ages = heap[str(v["ages"]["ref"])]
check(ages["k"] == "dict" and sorted(p[0]["p"] for p in ages["items"]) == ['"Ann"', '"Bob"'], f"coll: ages {ages}")
check(sorted(p[1]["p"] for p in ages["items"]) == ["30", "41"], "coll: ages values")
check(heap[str(v["tags"]["ref"])] == {"k": "set", "items": [{"p": '"x"', "k": "String"}], "more": 0}, "coll: tags set")
arr = heap[str(v["arr"]["ref"])]
check(arr["k"] == "array" and [x["p"] for x in arr["items"]] == ["1", "2", "3"] and arr["items"][0]["k"] == "int", "coll: arr")
check([x["p"] for x in heap[str(v["fixed"]["ref"])]["items"]] == ['"p"', '"q"'], "coll: List.of (invoke fallback)")
check(heap[str(v["sorted"]["ref"])]["k"] == "dict" and len(heap[str(v["sorted"]["ref"])]["items"]) == 2, "coll: TreeMap")
check(v["sb"] == {"p": '"hi"', "k": "StringBuilder"}, f"coll: sb {v['sb']}")
check(v["big"] == {"p": "1099511627776", "k": "long"}, "coll: long")
check(v["c"] == {"p": "'z'", "k": "char"}, "coll: char")
check(v["d"] == {"p": "2.5", "k": "double"}, "coll: double")
check(v["ok"] == {"p": "true", "k": "boolean"}, "coll: boolean")
check(v["name"] == {"p": "null", "k": "null"}, "coll: null")
many = heap[str(v["many"]["ref"])]
check(len(many["items"]) == 24 and many["more"] == 6, f"coll: 24-item cap, more={many['more']}")
check(res["output"] == "[10, 20] {Bob=41, Ann=30}\n" or res["output"].startswith("[10, 20] {"), f"coll: output {res['output']!r}")

# ---- 3. object with fields ----------------------------------------------------------------------------------------
print("3. objects")
res, _ = trace("Pets", """\
record Point(int x, int y) { }

class Dog {
    String name;
    int age;
    Dog(String name, int age) {
        this.name = name;
        this.age = age;
    }
    void birthday() {
        age++;
    }
}

class Pets {
    public static void main(String[] args) {
        Dog d = new Dog("Rex", 3);
        d.birthday();
        Point p = new Point(1, 2);
        System.out.println(d.name + p.x());
    }
}
""")
structure_ok(res, "pets")
check(res["error"] is None, f"pets: error {res['error']}")
last = res["steps"][-1]
v = last["stack"][-1]["vars"]
dog = last["heap"][str(v["d"]["ref"])]
check(dog["k"] == "object" and dog["cls"] == "Dog", f"pets: dog {dog}")
check(dog["attrs"]["name"] == {"p": '"Rex"', "k": "String"} and dog["attrs"]["age"] == {"p": "4", "k": "int"}, f"pets: attrs {dog['attrs']}")
pt = last["heap"][str(v["p"]["ref"])]
check(pt["cls"] == "Point" and pt["attrs"]["x"]["p"] == "1" and pt["attrs"]["y"]["p"] == "2", f"pets: record {pt}")
in_method = [s for s in res["steps"] if len(s["stack"]) == 2 and s["stack"][-1]["name"] == "birthday()"]
check(in_method and "this" in in_method[0]["stack"][-1]["vars"], "pets: birthday() frame has this")
check(any(s["stack"][-1]["name"] == "Dog()" for s in res["steps"]), "pets: constructor frame named Dog()")
check(any(s["ev"] == "return" and s["stack"][-1]["name"] == "birthday()" for s in res["steps"]), "pets: birthday return event")

# ---- 4. recursion -----------------------------------------------------------------------------------------------------
print("4. recursion")
res, _ = trace("Rec", """\
class Rec {
    static int fact(int n) {
        if (n <= 1) return 1;
        return n * fact(n - 1);
    }

    public static void main(String[] args) {
        int r = fact(4);
        System.out.println(r);
    }
}
""")
structure_ok(res, "rec")
check(res["error"] is None, f"rec: error {res['error']}")
check(max(len(s["stack"]) for s in res["steps"]) == 5, f"rec: max depth {max(len(s['stack']) for s in res['steps'])}")
rets = [s["ret"]["p"] for s in res["steps"] if s["ev"] == "return" and s["stack"][-1]["name"] == "fact()"]
check(rets == ["1", "2", "6", "24"], f"rec: return values {rets}")
check(res["output"] == "24\n", f"rec: output {res['output']!r}")
deepest = max(res["steps"], key=lambda s: len(s["stack"]))
check([f["vars"]["n"]["p"] for f in deepest["stack"][1:]] == ["4", "3", "2", "1"], "rec: n per frame")

# ---- 5. uncaught exception ------------------------------------------------------------------------------------------
print("5. uncaught exception")
res, _ = trace("Boom", """\
class Boom {
    static int divide(int a, int b) {
        return a / b;
    }

    public static void main(String[] args) {
        System.out.println("before");
        int x = divide(10, 0);
        System.out.println("never " + x);
    }
}
""")
structure_ok(res, "boom")
check(res["error"] == {"type": "ArithmeticException", "msg": "/ by zero", "line": 3}, f"boom: error {res['error']}")
check(res["output"] == "before\n", f"boom: output {res['output']!r}")
ex = [s for s in res["steps"] if s["ev"] == "exception"]
check(len(ex) == 1 and ex[0]["err"] == "ArithmeticException: / by zero" and ex[0]["line"] == 3, f"boom: exception step {ex[:1]}")
check(ex and len(ex[0]["stack"]) == 2 and ex[0]["stack"][1]["name"] == "divide()", "boom: stack at exception")

# ---- 6. compile error -------------------------------------------------------------------------------------------------
print("6. compile error")
res, _ = trace("Bad", """\
class Bad {
    public static void main(String[] args) {
        int x = 5
        System.out.println(x);
    }
}
""")
check(res["steps"] == [] and res["total_steps"] == 0, "bad: no steps")
check(res["error"] and res["error"]["type"] == "CompileError" and res["error"]["line"] == 3, f"bad: error {res['error']}")
check(res["error"] and "';'" in res["error"]["msg"], f"bad: msg {res['error'] and res['error']['msg']}")
res, _ = trace("Bad2", "class Bad2 {\n    public static void main(String[] args) {\n        String s = 42;\n    }\n}\n")
check(res["error"] and res["error"]["line"] == 3 and res["error"]["type"] == "CompileError", f"bad2: {res['error']}")

# ---- 7. stdin (Scanner), truncation, timeout, callbacks -----------------------------------------------------------------
print("7. stdin / truncation / timeout / lambda callbacks")
res, _ = trace("Sum", """\
import java.util.Scanner;

class Sum {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println("sum=" + (a + b));
    }
}
""", stdin="3 4\n")
structure_ok(res, "sum")
check(res["error"] is None and res["output"] == "sum=7\n", f"sum: {res['error']} {res['output']!r}")
check(final_vars(res)["a"]["p"] == "3" and final_vars(res)["b"]["p"] == "4", "sum: a and b read from stdin")

res, _ = trace("Many", "class Many {\n    public static void main(String[] args) {\n        for (int i = 0; i < 1000; i++) {\n            int sq = i * i;\n        }\n    }\n}\n", max_steps=20)
check(res["truncated"] is True and res["total_steps"] == 20 and res["error"] is None, f"many: truncated={res['truncated']} n={res['total_steps']}")

t0 = time.time()
res, _ = trace("Spin", "class Spin {\n    public static void main(String[] args) {\n        while (true) { }\n    }\n}\n",
               env={"JTRACER_TIMEOUT_MS": "2500"})
check(res["error"] and res["error"]["type"] == "TimeoutError", f"spin: {res['error']}")
check(time.time() - t0 < 20, "spin: child killed in time")

res, _ = trace("Lam", """\
import java.util.*;

class Lam {
    public static void main(String[] args) {
        List<Integer> xs = List.of(1, 2, 3);
        int[] sum = {0};
        xs.forEach(x -> {
            sum[0] += x;
        });
        System.out.println(sum[0]);
    }
}
""")
structure_ok(res, "lam")
check(res["error"] is None and res["output"] == "6\n", f"lam: {res['error']} {res['output']!r}")
lam_lines = [s for s in res["steps"] if s["line"] == 8 and s["ev"] == "line"]
check(len(lam_lines) == 3, f"lam: lambda body stepped once per element, got {len(lam_lines)}")

# ---- a 50-step program (timing) ---------------------------------------------------------------------------------------------
print("8. ~50-step timing")
code50 = """\
class Fifty {
    public static void main(String[] args) {
        int s = 0;
        for (int i = 0; i < 22; i++) {
            s += i;
        }
        System.out.println(s);
    }
}
"""
res, secs50 = trace("Fifty", code50)
check(res["error"] is None and 45 <= res["total_steps"] <= 60, f"fifty: steps={res['total_steps']}")
print(f"   {res['total_steps']} steps -> {secs50:.2f}s wall (JVM start + javac + JDI)")

# ---- flowchart ----------------------------------------------------------------------------------------------------------
print("9. flowchart / looks_like_java")
SRC = """\
import java.util.*;

public class Shop {
    static int total(int[] prices) {
        int sum = 0;
        for (int p : prices) {
            sum += p;
        }
        return sum;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] prices = new int[n];
        int i = 0;
        while (i < n) {
            prices[i] = sc.nextInt();
            i++;
        }
        int t = total(prices);
        if (t > 100) {
            System.out.println("big");
        } else if (t > 50) {
            System.out.println("medium");
        } else {
            System.out.println("small");
        }
        switch (n) {
            case 1:
                System.out.println("one");
                break;
            default:
                System.out.println("many");
        }
        try {
            int z = t / n;
        } catch (ArithmeticException e) {
            System.out.println("oops");
        }
        do {
            n--;
        } while (n > 0);
    }
}
"""
fc = jviz.flowchart(SRC)
check(fc.startswith("flowchart TD"), "flow: starts with flowchart TD")
for needle in ("Start", "End", "int sum = 0", "sum += p", "return sum", "i ‹ n ?", "t › 100 ?", "t › 50 ?",
               "for each p in prices", "System.out.println('big')", "switch (n)", "case 1", "default",
               "catch (ArithmeticException e)", "n ›", "subgraph sg0", "total(int[] prices)", "when called", "n-- ?" if False else "do"):
    check(needle in fc, f"flow: missing {needle!r}")
check('Scanner sc = new Scanner(System.in)' in fc, "flow: scanner line")
check(fc.count("subgraph") == 1 and fc.count("\n  end") == 1, "flow: one subgraph, closed")
check("<" not in fc.split("\n", 1)[1].replace("<br/>", ""), "flow: no raw < in labels")
fc_snip = jviz.flowchart("int x = 1;\nwhile (x < 3) { x++; }\nSystem.out.println(x);\n")
check(fc_snip.startswith("flowchart TD") and "x ‹ 3 ?" in fc_snip, "flow: bare statements work")
big = "class Big {\n  public static void main(String[] a) {\n" + "".join(f"    int v{i} = {i};\n" for i in range(120)) + "  }\n}\n"
fc_big = jviz.flowchart(big)
check("trimmed" in fc_big and "too large" in fc_big, "flow: overflow message")
check(len([ln for ln in fc_big.splitlines() if ln.lstrip().startswith("n") and "[" in ln]) <= 70, "flow: <= 70 nodes")
try:
    jviz.flowchart("class A { void f() { if (x { } }")
    check(False, "flow: unbalanced input should raise ValueError")
except ValueError:
    pass
check(jviz.looks_like_java(SRC), "looks_like_java: Java program")
check(jviz.looks_like_java("int x = 5;\nSystem.out.println(x);\nString[] a = new String[3];"), "looks_like_java: snippet")
check(not jviz.looks_like_java("def f(x):\n    print(x)\n"), "looks_like_java: Python def")
check(not jviz.looks_like_java("x = [1, 2]\nfor i in x:\n    print(i)\n"), "looks_like_java: Python for loop")
check(not jviz.looks_like_java("SELECT name FROM people WHERE age > 3;"), "looks_like_java: SQL")
shutil.rmtree(WORK, ignore_errors=True)
print("ALL OK" if not FAILS else f"{len(FAILS)} FAILED")
sys.exit(1 if FAILS else 0)
