"""Java visuals: a Mermaid flowchart from Java source (the Java twin of visual.flowchart) and a Java detector.

No AST library is available for Java, so this file has a small tokenizer plus a brace-aware statement parser:
if/else, for, enhanced for, while, do-while, switch, try/catch/finally, return/throw/break/continue, and plain
statements (calls, assignments, declarations) as boxes.  `main` is the main flow; every other method (up to 6)
becomes a subgraph, linked by a dashed arrow from the first place that calls it.
"""
from __future__ import annotations

import re
from typing import NamedTuple


class Overflow(Exception):
    pass


def _clean(s: str, n: int = 46) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    if len(s) > n:
        s = s[: n - 1] + "…"
    return s.replace('"', "'").replace("`", "'").replace("#", "#35;").replace("<", "‹").replace(">", "›")


# ---- tokenizer ---------------------------------------------------------------------------------------------
class Tok(NamedTuple):
    k: str      # id | num | str | chr | op
    s: str
    sp: bool    # whitespace / comment before this token in the source


_TOKEN_RE = re.compile(
    r"""(?P<ws>\s+)
      | (?P<lc>//[^\n]*)
      | (?P<bc>/\*.*?\*/)
      | (?P<tb>\"\"\".*?\"\"\")
      | (?P<str>"(?:\\.|[^"\\\n])*")
      | (?P<chr>'(?:\\.|[^'\\\n])+')
      | (?P<num>\d[\w.]*)
      | (?P<id>[A-Za-z_$][\w$]*)
      | (?P<op>->|::|\+\+|--|.)""",
    re.X | re.S,
)


def _tokenize(src: str) -> list[Tok]:
    toks: list[Tok] = []
    sp = False
    for m in _TOKEN_RE.finditer(src):
        kind = m.lastgroup
        text = m.group()
        if kind in ("ws", "lc", "bc"):
            sp = True
            continue
        if kind == "op" and text in ('"', "'"):
            raise ValueError("Syntax error: unterminated string or character literal")
        if kind == "op" and text == "/" and src.startswith("/*", m.start()):
            raise ValueError("Syntax error: unterminated comment")
        if kind == "tb":
            kind = "str"
        toks.append(Tok(kind, text, sp))
        sp = False
    return toks


_OPEN, _CLOSE = "([{", ")]}"
_MODS = {"public", "private", "protected", "static", "final", "abstract", "sealed", "strictfp", "synchronized",
         "native", "default", "transient", "volatile"}
_TYPE_KW = {"class", "interface", "enum", "record"}
_KEYWORDS = {"if", "for", "while", "switch", "catch", "try", "do", "else", "synchronized", "return", "throw", "new",
             "super", "this"}
_COMMON = {"add", "get", "put", "remove", "size", "length", "print", "println", "printf", "equals", "toString",
           "contains", "append", "next", "nextInt", "nextLine", "hasNext", "set", "clear", "isEmpty", "charAt",
           "format", "valueOf", "indexOf", "substring", "close", "run", "apply", "accept", "test", "compareTo",
           "hashCode", "forEach", "stream", "map", "filter", "sort", "keySet", "values", "entrySet"}


class Method(NamedTuple):
    name: str
    params: str
    owner: str
    lo: int          # body token range [lo, hi) (inside the braces)
    hi: int
    is_main: bool


class Flow:
    LIMIT = 70
    MAX_METHODS = 6

    def __init__(self, source: str):
        self.t = _tokenize(source)
        self.match: dict[int, int] = {}
        self._pair()
        self.lines = ["flowchart TD"]
        self.n = 0
        self.methods: list[Method] = []
        self.types_found = False
        self.ctx: list[dict] = []
        self.calls: dict[str, list[tuple[str, str]]] = {}   # method name -> [(node id, caller key)]
        self.cur = ""                                       # key of the method being drawn ("" = main flow)
        self.names: set[str] = set()
        self.classes: set[str] = set()

    # -- bracket matching ---------------------------------------------------------------------------------
    def _pair(self) -> None:
        stack: list[int] = []
        for i, tk in enumerate(self.t):
            if tk.k != "op":
                continue
            if tk.s in _OPEN:
                stack.append(i)
            elif tk.s in _CLOSE:
                if not stack or _OPEN.index(self.t[stack[-1]].s) != _CLOSE.index(tk.s):
                    raise ValueError("Syntax error: unbalanced brackets near '" + self.label(max(0, i - 3), i + 1) + "'")
                j = stack.pop()
                self.match[j] = i
                self.match[i] = j
        if stack:
            raise ValueError("Syntax error: '" + self.t[stack[-1]].s + "' is never closed")

    def label(self, lo: int, hi: int) -> str:
        return "".join((" " if tk.sp and i > lo else "") + tk.s for i, tk in enumerate(self.t[lo:hi], lo)).strip()

    def is_(self, i: int, text: str) -> bool:
        return 0 <= i < len(self.t) and self.t[i].s == text and self.t[i].k in ("id", "op")

    def top(self, lo: int, hi: int, texts: set[str]):
        """Positions in [lo, hi) of tokens whose text is in `texts`, skipping nested bracket groups."""
        j = lo
        while j < hi:
            tk = self.t[j]
            if tk.k in ("id", "op") and tk.s in texts:
                yield j
            if tk.k == "op" and tk.s in _OPEN:
                j = self.match[j]
            j += 1

    # -- diagram primitives (same look as visual.Flow) ----------------------------------------------------
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

    # -- declarations: find the methods ------------------------------------------------------------------
    def collect(self, lo: int, hi: int, owner: str) -> None:
        i = lo
        while i < hi:
            j = i
            kind = None
            while j < hi:
                tk = self.t[j]
                if tk.k == "op" and tk.s in "([":
                    j = self.match[j] + 1
                    continue
                if tk.k == "op" and tk.s in (";", "{", "="):
                    kind = tk.s
                    break
                j += 1
            if kind is None:
                return
            if kind in (";", "="):                         # field / abstract method / import / package
                if kind == "=":
                    j = next(iter(self.top(j, hi, {";"})), hi)
                i = j + 1
                continue
            body_lo, body_hi = j + 1, self.match[j]
            words = [self.t[k].s for k in range(i, j) if self.t[k].k == "id"]
            fi = self._first_idx(i, j)
            first = self.t[fi].s if fi < j else ""
            paren = next(iter(self.top(i, j, {"("})), None)
            if first in _TYPE_KW and fi + 1 < j and self.t[fi + 1].k == "id":
                p = fi
                name = self.t[p + 1].s
                self.types_found = True
                self.classes.add(name)
                if first == "enum":
                    semi = next(iter(self.top(body_lo, body_hi, {";"})), None)
                    if semi is not None:
                        self.collect(semi + 1, body_hi, name)
                else:
                    self.collect(body_lo, body_hi, name)
            elif paren is not None:
                name = self.t[paren - 1].s if paren > i else "?"
                if name not in _KEYWORDS and self.t[paren - 1].k == "id":
                    params = self.label(paren + 1, self.match[paren])
                    is_main = name == "main" and "String" in params
                    self.methods.append(Method(name, params, owner, body_lo, body_hi, is_main))
                    self.names.add(name)
            elif words and words[-1] == owner and owner:  # compact record constructor
                self.methods.append(Method(owner, "", owner, body_lo, body_hi, False))
                self.names.add(owner)
            i = body_hi + 1

    def _first_idx(self, lo: int, hi: int) -> int:
        j = lo
        while j < hi:
            tk = self.t[j]
            if tk.s == "@" and tk.k == "op":                 # annotation: @Name or @Name(args)
                j += 2
                if j < hi and self.t[j].s == "(":
                    j = self.match[j] + 1
                continue
            if (tk.k == "id" and tk.s in _MODS) or (tk.s in ("non", "-") and tk.k in ("id", "op")):
                j += 1
                continue
            return j
        return hi

    # -- statements -----------------------------------------------------------------------------------------
    def block(self, lo: int, hi: int, pending):
        i = lo
        while i < hi:
            i, pending = self.stmt(i, hi, pending)
        return pending

    def _end_simple(self, i: int, hi: int) -> int:
        j = next(iter(self.top(i, hi, {";"})), hi)
        return j

    def _user_call(self, lo: int, hi: int) -> str | None:
        for j in range(lo, hi - 1):
            tk = self.t[j]
            if tk.k != "id" or not self.is_(j + 1, "(") or tk.s not in self.names:
                continue
            prev = self.t[j - 1].s if j > lo else ""
            if prev == "new":
                continue
            if prev == ".":
                owner = self.t[j - 2].s if j - 2 >= lo else ""
                if not (owner in self.classes or owner == "this" or tk.s not in _COMMON):
                    continue
            return tk.s
        return None

    def stmt(self, i: int, hi: int, pending):
        tk = self.t[i]
        s = tk.s if tk.k in ("id", "op") else ""
        if s == ";":
            return i + 1, pending
        if s == "{" and tk.k == "op":
            j = self.match[i]
            return j + 1, self.block(i + 1, j, pending)
        if tk.k == "id" and self.is_(i + 1, ":") and s not in ("default", "case") and not self.is_(i + 2, ":"):
            return self.stmt(i + 2, hi, pending)                       # label:
        if s == "if" and self.is_(i + 1, "("):
            close = self.match[i + 1]
            d = self.node(self.label(i + 2, close) + " ?", "dec")
            self.link(pending, d)
            j, yes = self.stmt(close + 1, hi, [(d, "yes")])
            if self.is_(j, "else"):
                j, no = self.stmt(j + 1, hi, [(d, "no")])
            else:
                no = [(d, "no")]
            return j, yes + no
        if s == "while" and self.is_(i + 1, "("):
            close = self.match[i + 1]
            cond = self.label(i + 2, close)
            d = self.node(cond + " ?", "dec")
            self.link(pending, d)
            self.ctx.append({"loop": True, "head": d, "breaks": []})
            j, body_end = self.stmt(close + 1, hi, [(d, "yes")])
            c = self.ctx.pop()
            for a, lbl in body_end:
                self.edge(a, d, lbl or "again")
            forever = cond.replace(" ", "") == "true"
            exits = ([] if forever else [(d, "no")]) + c["breaks"]
            return j, exits or [(d, "no")]
        if s == "do":
            top = self.node("do", "box")
            self.link(pending, top)
            self.ctx.append({"loop": True, "head": top, "breaks": []})
            j, body_end = self.stmt(i + 1, hi, [(top, None)])
            c = self.ctx.pop()
            if self.is_(j, "while") and self.is_(j + 1, "("):
                close = self.match[j + 1]
                d = self.node(self.label(j + 2, close) + " ?", "dec")
                self.link(body_end, d)
                self.edge(d, top, "yes")
                j = close + 1
                if self.is_(j, ";"):
                    j += 1
                return j, [(d, "no")] + c["breaks"]
            return j, body_end + c["breaks"]
        if s == "for" and self.is_(i + 1, "("):
            close = self.match[i + 1]
            semis = list(self.top(i + 2, close, {";"}))
            if len(semis) >= 2:
                init = self.label(i + 2, semis[0])
                cond = self.label(semis[0] + 1, semis[1]) or "true"
                upd = self.label(semis[1] + 1, close)
                if init:
                    n0 = self.node(init, "box")
                    self.link(pending, n0)
                    pending = [(n0, None)]
                d = self.node(cond + " ?", "dec")
            else:
                cols = list(self.top(i + 2, close, {":"}))
                if cols:
                    d = self.node(f"for each {self.label(cols[0] - 1, cols[0])} in {self.label(cols[0] + 1, close)}", "dec")
                    upd, cond = "next item", ""
                else:
                    d = self.node(self.label(i + 2, close) + " ?", "dec")
                    upd, cond = "", ""
            self.link(pending, d)
            self.ctx.append({"loop": True, "head": d, "breaks": []})
            yes = "next item" if upd == "next item" else "yes"
            j, body_end = self.stmt(close + 1, hi, [(d, yes)])
            c = self.ctx.pop()
            for a, lbl in body_end:
                self.edge(a, d, lbl or upd or "loop")
            forever = len(semis) >= 2 and cond.replace(" ", "") == "true"
            done = [(d, "done" if upd == "next item" else "no")]
            return j, ([] if forever and c["breaks"] else done) + c["breaks"]
        if s == "switch" and self.is_(i + 1, "(") and self.is_(self.match[i + 1] + 1, "{"):
            return self.switch(i, pending)
        if s == "try":
            return self.try_(i, pending)
        if s == "synchronized" and self.is_(i + 1, "(") and self.is_(self.match[i + 1] + 1, "{"):
            close = self.match[i + 1]
            n = self.node("synchronized " + self.label(i + 1, close + 1), "box")
            self.link(pending, n)
            end = self.match[close + 1]
            return end + 1, self.block(close + 2, end, [(n, None)])
        if s in ("return", "throw"):
            j = self._end_simple(i, hi)
            n = self.node(self.label(i, j), "round")
            self._register_calls(n, i, j)
            self.link(pending, n)
            return j + 1, []
        if s in ("break", "continue"):
            j = self._end_simple(i, hi)
            for c in reversed(self.ctx):
                if s == "break":
                    c["breaks"] += pending
                    break
                if c["loop"]:
                    for a, lbl in pending:
                        self.edge(a, c["head"], lbl or "continue")
                    break
            return j + 1, []
        if self._is_local_type(i, hi):
            p = self._first_idx(i, hi)
            brace = next(iter(self.top(p, hi, {"{"})), None)
            n = self.node(f"{self.t[p].s} {self.t[p + 1].s if p + 1 < hi else ''}", "sub")
            self.link(pending, n)
            return (self.match[brace] + 1 if brace is not None else hi), [(n, None)]
        # plain statement: declaration, assignment, method call ...
        j = self._end_simple(i, hi)
        text = self.label(i, j)
        io = bool(re.search(r"System\.(?:out|err)\.|\bScanner\b|\.next(?:Int|Line|Double|Long)?\s*\(|System\.in", text))
        call = self._user_call(i, j)
        shape = "io" if io else ("sub" if call else "box")
        n = self.node(text, shape)
        self._register_calls(n, i, j)
        self.link(pending, n)
        return j + 1, [(n, None)]

    def _is_local_type(self, i: int, hi: int) -> bool:
        p = self._first_idx(i, hi)
        if p + 1 >= hi or self.t[p].s not in _TYPE_KW or self.t[p + 1].k != "id":
            return False
        if self.t[p].s == "record" and not self.is_(p + 2, "(") and not self.is_(p + 2, "<"):
            return False
        first = next(iter(self.top(p, hi, {"{", ";"})), None)
        return first is not None and self.t[first].s == "{"

    def _register_calls(self, nid: str, lo: int, hi: int) -> None:
        name = self._user_call(lo, hi)
        if name:
            self.calls.setdefault(name, []).append((nid, self.cur))

    def switch(self, i: int, pending):
        close = self.match[i + 1]
        brace = close + 1
        end = self.match[brace]
        d = self.node("switch (" + self.label(i + 2, close) + ")", "dec")
        self.link(pending, d)
        starts = [j for j in self.top(brace + 1, end, {"case", "default"})
                  if self.t[j].k == "id" and (self.t[j].s == "case" or self.is_(j + 1, "->") or self.is_(j + 1, ":"))]
        exits: list = []
        self.ctx.append({"loop": False, "head": d, "breaks": []})
        has_default = False
        for n, st in enumerate(starts):
            stop = starts[n + 1] if n + 1 < len(starts) else end
            sep = next((j for j in self.top(st, stop, {":", "->"}) if self.t[j].s in (":", "->")), None)
            if sep is None:
                continue
            lab = self.label(st, sep)
            has_default = has_default or lab.startswith("default")
            exits += self.block(sep + 1, stop, [(d, lab)])     # (old-style fall-through is drawn as leaving the switch)
        c = self.ctx.pop()
        if not has_default:
            exits.append((d, "other"))
        return end + 1, exits + c["breaks"]

    def try_(self, i: int, pending):
        j = i + 1
        label = "try"
        if self.is_(j, "("):
            label = "try " + self.label(j, self.match[j] + 1)
            j = self.match[j] + 1
        t = self.node(label, "box")
        self.link(pending, t)
        if not self.is_(j, "{"):
            return j, [(t, None)]
        body_end = self.match[j]
        exits = self.block(j + 1, body_end, [(t, None)])
        j = body_end + 1
        while self.is_(j, "catch") and self.is_(j + 1, "("):
            close = self.match[j + 1]
            hn = self.node("catch " + self.label(j + 1, close + 1), "dec")
            self.edge(t, hn, "error")
            b = close + 1
            exits += self.block(b + 1, self.match[b], [(hn, "caught")])
            j = self.match[b] + 1
        if self.is_(j, "finally") and self.is_(j + 1, "{"):
            exits = self.block(j + 2, self.match[j + 1], exits)
            j = self.match[j + 1] + 1
        return j, exits


def flowchart(code: str) -> str:
    f = Flow(code)
    top_lo, top_hi = 0, len(f.t)
    f.collect(top_lo, top_hi, "")
    f.names -= {m.name for m in f.methods if m.is_main}
    trimmed = False
    open_sg = False
    try:
        start = f.node("Start", "round")
        pending = [(start, None)]
        entry = next((m for m in f.methods if m.is_main), None)
        if entry is not None:
            pending = f.block(entry.lo, entry.hi, pending)
        elif not f.types_found and not f.methods:
            pending = f.block(top_lo, top_hi, pending)           # a bare snippet of statements
        else:
            n = f.node("no main method found", "box")
            f.link(pending, n)
            pending = [(n, None)]
        end = f.node("End", "round")
        f.link(pending, end)
        main_cls = entry.owner if entry else ""
        order = sorted((m for m in f.methods if not m.is_main),
                       key=lambda m: (m.owner != main_cls, f.methods.index(m)))
        linked: set[str] = set()
        for i, m in enumerate(order[: f.MAX_METHODS]):
            key = f"{m.owner}.{m.name}"
            title = (f"{m.owner}." if m.owner and m.owner != main_cls else "") + f"{m.name}({_clean(m.params, 30)})"
            f.lines.append(f'  subgraph sg{i}["{_clean(title, 60)}"]')
            open_sg = True
            f.lines.append("    direction TB")
            f.cur = key
            s = f.node("call", "round")
            body_end = f.block(m.lo, m.hi, [(s, None)])
            e = f.node("back to caller", "round")
            f.link(body_end, e)
            f.lines.append("  end")
            open_sg = False
            sites = f.calls.get(m.name, [])
            outer = next((nid for nid, owner in sites if owner != key), None)
            if outer and m.name not in linked:
                f.lines.append(f'  {outer} -.->|"when called"| {s}')
                linked.add(m.name)
            inner = next((nid for nid, owner in sites if owner == key), None)
            if inner:
                f.lines.append(f'  {inner} -.->|"calls itself"| {s}')
    except Overflow:
        trimmed = True
    if open_sg:
        f.lines.append("  end")
    if trimmed:
        f.lines.append('  more["… diagram trimmed (too large, long code)"]')
    f.lines += ["  classDef dec fill:#fff4d6,stroke:#c98524;"]
    return "\n".join(f.lines)


# ---- is this text Java? ---------------------------------------------------------------------------------------
def looks_like_java(code: str) -> bool:
    if re.search(r"^\s*(def\s+\w+\s*\(.*\)\s*:|elif\b|from\s+\w+\s+import\b|print\s*\()", code, re.M):
        return False
    if re.search(r"\bpublic\s+static\s+void\s+main\s*\(", code):
        return True
    score = 0
    for rx in (r"\bSystem\.(?:out|err|in)\b", r"\bString\s*\[\]", r"^\s*import\s+java\.", r"\bnew\s+[A-Z]\w*\s*[(\[<]",
               r"^\s*(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?[\w<>\[\]]+\s+\w+\s*[(=;]",
               r"\b(?:class|interface|enum|record)\s+[A-Z]\w*[^\n{;]*\{", r"@Override\b",
               r"\b(?:int|double|long|boolean|char|float)\s+\w+\s*(?:=|;|\[\])", r"\bList<\w+>|\bMap<\w+\s*,", r"\bvoid\s+\w+\s*\("):
        if re.search(rx, code, re.M):
            score += 1
    return score >= 2 and code.count(";") >= 1
