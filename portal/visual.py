"""Visual explanations: step-through traces, Mermaid flowcharts from Python code, SQL clause-order diagrams."""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from . import runner

HARNESS = Path(__file__).resolve().parent / "tracer_harness.py"


# ---- step-through trace --------------------------------------------------------------------------
def trace(code: str, stdin: str = "", max_steps: int = 250, timeout: int = 12) -> dict:
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {"ok": False, "error": f"Syntax error on line {e.lineno}: {e.msg}", "steps": []}
    runner.prepare()
    wd = runner.WORK / "days" / "_play"
    target = wd / f"trace_{uuid.uuid4().hex[:8]}.py"      # unique per call: two windows can trace at once
    target.write_text(code, encoding="utf-8")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "trace.json"
            t0 = time.time()
            try:
                p = subprocess.run([sys.executable, "-u", str(HARNESS), str(target), str(max_steps), str(result)],
                                   cwd=str(wd), input=stdin, capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=timeout, env=runner.clean_env(), check=False)
            except subprocess.TimeoutExpired:
                return {"ok": False, "error": f"Stopped after {timeout}s. Is there a loop that never ends?", "steps": []}
            if not result.is_file():
                return {"ok": False, "error": (p.stderr or "tracer failed")[-400:], "steps": []}
            data = json.loads(result.read_text(encoding="utf-8"))
    finally:
        target.unlink(missing_ok=True)
    data["ok"] = True
    data["ms"] = int((time.time() - t0) * 1000)
    data["source"] = code
    return data


# ---- Mermaid flowchart from Python ---------------------------------------------------------------------
class Overflow(Exception):
    pass


def _clean(s: str, n: int = 46) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    if len(s) > n:
        s = s[: n - 1] + "…"
    return s.replace('"', "'").replace("`", "'").replace("#", "#35;").replace("<", "‹").replace(">", "›")


class Flow:
    LIMIT = 70

    def __init__(self, source: str):
        self.src = source
        self.lines = ["flowchart TD"]
        self.n = 0
        self.funcs: list[tuple[ast.FunctionDef, str]] = []

    def seg(self, node) -> str:
        return ast.get_source_segment(self.src, node) or ast.unparse(node)

    def node(self, label: str, shape: str = "box") -> str:
        if self.n >= self.LIMIT:
            raise Overflow()
        nid = f"n{self.n}"
        self.n += 1
        lbl = _clean(label)
        form = {"box": f'{nid}["{lbl}"]', "dec": f'{nid}{{"{lbl}"}}', "round": f'{nid}(["{lbl}"])',
                "io": f'{nid}[/"{lbl}"/]', "sub": f'{nid}[["{lbl}"]]'}[shape]
        self.lines.append("  " + form)
        return nid

    def edge(self, a: str, b: str, label: str | None = None, dashed: bool = False) -> None:
        arrow = "-.->" if dashed else "-->"
        self.lines.append(f"  {a} {arrow}{('|' + _clean(label, 20) + '|') if label else ''} {b}")

    def link(self, pending, nid):
        for a, lbl in pending:
            self.edge(a, nid, lbl)

    def block(self, stmts, pending):
        for st in stmts:
            pending = self.stmt(st, pending)
        return pending

    def chain(self, value) -> list[str] | None:
        """Method chains like df.groupby('a').sum().sort_values() become a left-to-right sequence."""
        parts, cur = [], value
        while isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute):
            args = ", ".join(self.seg(a) for a in cur.args[:2])
            parts.append(f".{cur.func.attr}({args})")
            cur = cur.func.value
        if len(parts) >= 3:
            return [self.seg(cur)] + parts[::-1]
        return None

    def stmt(self, st, pending):
        if isinstance(st, ast.If):
            d = self.node(self.seg(st.test) + " ?", "dec")
            self.link(pending, d)
            yes = self.block(st.body, [(d, "yes")])
            no = self.block(st.orelse, [(d, "no")]) if st.orelse else [(d, "no")]
            return yes + no
        if isinstance(st, ast.While):
            d = self.node(self.seg(st.test) + " ?", "dec")
            self.link(pending, d)
            for a, lbl in self.block(st.body, [(d, "yes")]):
                self.edge(a, d, lbl or "again")
            return [(d, "no")]
        if isinstance(st, (ast.For, ast.AsyncFor)):
            d = self.node(f"for {self.seg(st.target)} in {self.seg(st.iter)}", "dec")
            self.link(pending, d)
            for a, lbl in self.block(st.body, [(d, "next item")]):
                self.edge(a, d, lbl or "loop")
            return [(d, "done")]
        if isinstance(st, ast.Return):
            n = self.node("return " + (self.seg(st.value) if st.value else ""), "round")
            self.link(pending, n)
            return []
        if isinstance(st, ast.Raise):
            n = self.node("raise " + (self.seg(st.exc) if st.exc else ""), "round")
            self.link(pending, n)
            return []
        if isinstance(st, ast.Try):
            t = self.node("try", "box")
            self.link(pending, t)
            exits = self.block(st.body, [(t, None)])
            for h in st.handlers:
                hn = self.node("except " + (self.seg(h.type) if h.type else "anything"), "dec")
                self.edge(t, hn, "error")
                exits += self.block(h.body, [(hn, "caught")])
            if st.orelse:
                exits = self.block(st.orelse, exits)
            if st.finalbody:
                exits = self.block(st.finalbody, exits)
            return exits
        if isinstance(st, (ast.With, ast.AsyncWith)):
            n = self.node("with " + ", ".join(self.seg(i.context_expr) for i in st.items), "box")
            self.link(pending, n)
            return self.block(st.body, [(n, None)])
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
            n = self.node(f"def {st.name}(…)", "sub")
            self.funcs.append((st, n))
            self.link(pending, n)
            return [(n, None)]
        if isinstance(st, ast.ClassDef):
            n = self.node(f"class {st.name}", "sub")
            self.link(pending, n)
            return [(n, None)]
        if isinstance(st, (ast.Assign, ast.Expr, ast.AugAssign, ast.AnnAssign)):
            value = getattr(st, "value", None)
            parts = self.chain(value) if value is not None else None
            if parts:
                first = None
                prev = pending
                target = ""
                if isinstance(st, ast.Assign):
                    target = self.seg(st.targets[0]) + " = "
                for i, p in enumerate(parts):
                    nid = self.node(p, "box")
                    self.link(prev, nid)
                    prev = [(nid, None)]
                    first = first or nid
                if target:
                    nid = self.node("store in " + target.strip(" ="), "io")
                    self.link(prev, nid)
                    prev = [(nid, None)]
                return prev
            call = isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "print"
            n = self.node(self.seg(st), "io" if call or (isinstance(value, ast.Call) and "input" in self.seg(value)) else "box")
            self.link(pending, n)
            return [(n, None)]
        n = self.node(self.seg(st).splitlines()[0], "box")
        self.link(pending, n)
        return [(n, None)]


def flowchart(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Syntax error on line {e.lineno}: {e.msg}") from e
    f = Flow(code)
    trimmed = False
    try:
        start = f.node("Start", "round")
        pending = f.block(tree.body, [(start, None)])
        end = f.node("End", "round")
        f.link(pending, end)
        for i, (fn, def_node) in enumerate(f.funcs[:6]):
            f.lines.append(f'  subgraph sg{i}["def {_clean(fn.name)}({_clean(ast.unparse(fn.args), 30)})"]')
            f.lines.append("    direction TB")
            s = f.node("call", "round")
            body_end = f.block(fn.body, [(s, None)])
            e = f.node("back to caller", "round")
            f.link(body_end, e)
            f.lines.append("  end")
            f.lines.append(f'  {def_node} -.->|"when called"| {s}')
    except Overflow:
        trimmed = True
    if trimmed:
        f.lines.append('  more["… diagram trimmed (long code)"]')
    f.lines += ["  classDef dec fill:#fff4d6,stroke:#c98524;"]
    return "\n".join(f.lines)


# ---- SQL: logical execution order ---------------------------------------------------------------------------
SQL_CLAUSES = [
    ("FROM", r"\bFROM\b", "start with this table"),
    ("JOIN", r"\b(?:LEFT\s+|RIGHT\s+|INNER\s+|FULL\s+|CROSS\s+)?(?:OUTER\s+)?JOIN\b", "match rows from another table"),
    ("WHERE", r"\bWHERE\b", "keep only rows that match"),
    ("GROUP BY", r"\bGROUP\s+BY\b", "squash rows into groups"),
    ("HAVING", r"\bHAVING\b", "keep only groups that match"),
    ("SELECT", r"\bSELECT\b", "pick / compute the columns to show"),
    ("ORDER BY", r"\bORDER\s+BY\b", "sort the result"),
    ("LIMIT", r"\bLIMIT\b", "stop after N rows"),
]


def looks_like_sql(text: str) -> bool:
    return bool(re.search(r"\bSELECT\b.+\bFROM\b", text, re.I | re.S))


def sql_diagram(sql: str) -> str:
    text = re.sub(r"--[^\n]*", "", sql)
    text = re.sub(r"\s+", " ", text).strip().rstrip(";")
    marks = []
    for name, rx, _ in SQL_CLAUSES:
        for m in re.finditer(rx, text, re.I):
            marks.append((m.start(), m.end(), name))
    marks.sort()
    parts: dict[str, list[str]] = {}
    for i, (s, e, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        parts.setdefault(name, []).append(text[s:end].strip())
    notes = {n: d for n, _r, d in SQL_CLAUSES}
    lines = ["flowchart LR"]
    prev, idx = None, 0
    for step, name in enumerate(["FROM", "JOIN", "WHERE", "GROUP BY", "HAVING", "SELECT", "ORDER BY", "LIMIT"]):
        if name not in parts:
            continue
        idx += 1
        nid = f"c{step}"
        body = _clean(" ⏎ ".join(parts[name]), 60)
        lines.append(f'  {nid}["<b>{idx}. {name}</b><br/>{body}<br/><i>{notes[name]}</i>"]')
        if prev:
            lines.append(f"  {prev} --> {nid}")
        prev = nid
    lines.append("  classDef default fill:#eeeefb,stroke:#5856d6,color:#1c1c21;")
    return "\n".join(lines)


def diagram(code: str, lang: str | None = None) -> dict:
    lang = (lang or "").lower()
    if lang == "sql" or (lang not in ("python", "py") and looks_like_sql(code) and not _is_python(code)):
        return {"kind": "sql", "mermaid": sql_diagram(code),
                "caption": "SQL runs in this order (not top to bottom): tables first, then filters, then grouping, then the columns you see."}
    return {"kind": "flow", "mermaid": flowchart(code),
            "caption": "Follow the arrows from Start. Diamonds are decisions or loops; rounded boxes are start / end / return."}


def _is_python(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    return not all(isinstance(n, ast.Expr) and isinstance(n.value, ast.Name) for n in tree.body)
