"""Pure logic for the "drills" feature: schema lint, learner view (no answers), answer checking, program assembly.

No database and no web code here, so ``_dev_tools/verify_drills.py`` can import it too.
The authoring spec is ``_dev_tools/DRILLS_FORMAT.md``.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path

TYPES = ("parsons", "fill", "predict", "bug", "review")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$")
BLANK = "___"
COMMON = {"id", "type", "title", "prompt", "explain", "concepts", "hint", "viz", "norun", "wrap"}
FIELDS = {
    "parsons": {"lines", "indent", "distractors", "alternatives", "faded", "blanks", "output", "check_indent"},
    "fill": {"code", "blanks", "output"},
    "predict": {"code", "expected", "stdin"},
    "bug": {"code", "bug_lines", "options", "answer", "fixed_code", "output", "buggy_runs", "stdin"},
    "review": {"code", "issues", "non_issues"},
}
TEXT_KEYS = ("code", "fixed_code", "expected", "output", "stdin", "prompt", "explain")


def norm(s: str) -> str:
    return " ".join(str(s).split())


def as_text(v):
    """Allow a list of lines wherever a multi-line string is expected."""
    return "\n".join(v) if isinstance(v, list) and all(isinstance(x, str) for x in v) else v


def normalize_drill(d: dict) -> dict:
    d = dict(d)
    for k in TEXT_KEYS:
        if k in d:
            d[k] = as_text(d[k])
    return d


def find_file(days_dir: Path, n: int) -> Path | None:
    for p in sorted(days_dir.glob(f"day{n:02d}_*")):
        f = p / "DRILLS.json"
        if f.is_file():
            return f
    return None


def load_doc(path: Path) -> dict | None:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or not isinstance(doc.get("drills"), list):
        return None
    doc["drills"] = [normalize_drill(d) for d in doc["drills"] if isinstance(d, dict)]
    return doc


# ---- program assembly (used by verify_drills; also tells the UI what "Visualize" should run) -----------------
def wrap_java(code: str) -> str:
    lines = code.split("\n")
    imports = [ln for ln in lines if re.match(r"^\s*import\s", ln)]
    body = "\n".join("        " + ln for ln in lines if not re.match(r"^\s*import\s", ln))
    head = "\n".join(imports) + "\n\n" if imports else ""
    return head + "class Drill {\n    public static void main(String[] args) throws Exception {\n" + body + "\n    }\n}\n"


def program(d: dict, code: str, java: bool) -> str:
    return wrap_java(code) if (java and d.get("wrap")) else code


def fill_code(code: str, values: list[str]) -> str:
    it = iter(values)
    return re.sub(re.escape(BLANK), lambda _m: next(it), code)


def parsons_text(d: dict, order: list[int] | None = None, blanks: list[str] | None = None, java: bool = False) -> str:
    return "\n".join(parsons_lines(d, order, blanks))


def parsons_lines(d: dict, order: list[int] | None = None, blanks: list[str] | None = None) -> list[str]:
    """The assembled program lines (indented, blanks filled with the first accepted answers unless given)."""
    lines, ind = d["lines"], d.get("indent") or [0] * len(d["lines"])
    order = order if order is not None else list(range(len(lines)))
    vals = blanks if blanks is not None else ([b["answers"][0] for b in d["blanks"]] if d.get("faded") else [])
    spans = _blank_spans(d) if d.get("faded") else [[] for _ in lines]
    out = []
    for i in order:
        ln = fill_code(lines[i], [vals[k] for k in spans[i]]) if spans[i] else lines[i]
        out.append(("    " * ind[i]) + ln)
    return out

def display_indent(java: bool, d: dict) -> bool:
    """Whether the learner must set indentation (Python) or the UI indents by braces (Java)."""
    return bool(d.get("check_indent", not java)) and any(d.get("indent") or [])


# ---- lint ----------------------------------------------------------------------------------------------------
def _is_str(v, lo=1, hi=4000) -> bool:
    return isinstance(v, str) and lo <= len(v) <= hi


def _err(errs: list[str], did: str, msg: str) -> None:
    errs.append(f"{did}: {msg}")


def lint_drill(d: dict, java: bool) -> list[str]:
    errs: list[str] = []
    did = str(d.get("id", "?"))
    t = d.get("type")
    if not isinstance(d.get("id"), str) or not ID_RE.match(d["id"]):
        _err(errs, did, "id must match [A-Za-z0-9][A-Za-z0-9_-]{0,39}")
    if t not in TYPES:
        return errs + [f"{did}: type must be one of {', '.join(TYPES)}"]
    for k in d:
        if k not in COMMON | FIELDS[t]:
            _err(errs, did, f"unknown key '{k}' for type {t}")
    for k, hi in (("title", 80), ("prompt", 700), ("explain", 1500)):
        if not _is_str(d.get(k), 1, hi):
            _err(errs, did, f"'{k}' must be a non-empty string up to {hi} chars")
    c = d.get("concepts")
    if not (isinstance(c, list) and 1 <= len(c) <= 6 and all(_is_str(x, 1, 60) for x in c)):
        _err(errs, did, "'concepts' must be a list of 1-6 short strings")
    if d.get("wrap") and not java:
        _err(errs, did, "'wrap' is for Java only")
    for k in ("viz", "norun", "wrap", "faded", "check_indent"):
        if k in d and not isinstance(d[k], bool):
            _err(errs, did, f"'{k}' must be true/false")
    chk = {"parsons": _lint_parsons, "fill": _lint_fill, "predict": _lint_predict, "bug": _lint_bug, "review": _lint_review}[t]
    chk(d, java, errs, did)
    return errs


def _code_ok(d, key, errs, did, max_lines=40, blanks=False):
    code = d.get(key)
    if not _is_str(code, 1, 3000):
        _err(errs, did, f"'{key}' must be a non-empty string (or list of lines), max 3000 chars")
        return ""
    if len(code.split("\n")) > max_lines:
        _err(errs, did, f"'{key}' has more than {max_lines} lines")
    if any(len(x) > 110 for x in code.split("\n")):
        _err(errs, did, f"'{key}' has a line over 110 chars (does not fit on a phone)")
    if "\t" in code:
        _err(errs, did, f"'{key}' contains a tab; use spaces")
    if not blanks and BLANK in code:
        _err(errs, did, f"'{key}' must not contain '{BLANK}' in a {d.get('type')} drill")
    return code


def _lint_parsons(d, java, errs, did):
    lines = d.get("lines")
    if not (isinstance(lines, list) and 3 <= len(lines) <= 14 and all(_is_str(x, 1, 110) for x in lines)):
        return _err(errs, did, "'lines' must be a list of 3-14 non-empty strings")
    n = len(lines)
    if any(x != x.strip() for x in lines):
        _err(errs, did, "'lines' must have no leading/trailing spaces; give indentation in 'indent'")
    if "output" not in d and not d.get("norun"):
        _err(errs, did, "'output' (what the finished program prints) is required; run verify_drills.py --fix to fill it")
    ind = d.get("indent")
    if ind is not None:
        if not (isinstance(ind, list) and len(ind) == n and all(isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 5 for x in ind)):
            _err(errs, did, "'indent' must be a list of ints 0-5, one per line")
        else:
            if ind[0] != 0:
                _err(errs, did, "first line must have indent 0")
            for i in range(1, n):
                opens = lines[i - 1].endswith(":") if not java else lines[i - 1].endswith("{")
                if ind[i] > ind[i - 1] + 1:
                    _err(errs, did, f"line {i + 1}: indent jumps by more than one level")
                if not java and opens and ind[i] != ind[i - 1] + 1:
                    _err(errs, did, f"line {i + 1}: must be indented one level after a line ending with ':'")
                if not java and not opens and ind[i] > ind[i - 1]:
                    _err(errs, did, f"line {i + 1}: indented but the previous line does not end with ':'")
    elif not java and any(x.endswith(":") for x in lines):
        _err(errs, did, "Python lines ending with ':' need an 'indent' list")
    if java:
        if sum(x.count("{") for x in lines) != sum(x.count("}") for x in lines):
            _err(errs, did, "braces '{' and '}' are not balanced across 'lines'")
    dis = d.get("distractors", [])
    if not (isinstance(dis, list) and len(dis) <= 4 and all(_is_str(x, 1, 110) and x == x.strip() for x in dis)):
        _err(errs, did, "'distractors' must be a list of up to 4 trimmed strings")
    else:
        for x in dis:
            if x in lines:
                _err(errs, did, f"distractor '{x}' equals a real line")
        if BLANK in "".join(dis):
            _err(errs, did, "distractors must not contain blanks")
    alts = d.get("alternatives", [])
    if not (isinstance(alts, list) and all(isinstance(a, list) and sorted(a) == list(range(n)) for a in alts)):
        _err(errs, did, "each 'alternatives' entry must be a permutation of 0..n-1 (indexes into 'lines')")
    elif any(a == list(range(n)) for a in alts):
        _err(errs, did, "an alternative equals the main order")
    total = sum(x.count(BLANK) for x in lines)
    if d.get("faded"):
        bl = d.get("blanks")
        if not (isinstance(bl, list) and len(bl) == total >= 1):
            _err(errs, did, f"faded: 'blanks' needs {total} entries (one per '{BLANK}' in 'lines', in order)")
        else:
            _lint_blanks(bl, errs, did, need_options=True)
    elif total or d.get("blanks"):
        _err(errs, did, f"'{BLANK}'/'blanks' only allowed with \"faded\": true")


def _lint_blanks(bl, errs, did, need_options=False):
    for i, b in enumerate(bl):
        if not (isinstance(b, dict) and set(b) <= {"answers", "regex", "options"}):
            _err(errs, did, f"blank {i + 1}: must be an object with answers/regex/options")
            continue
        a = b.get("answers")
        if not (isinstance(a, list) and a and all(_is_str(x, 1, 80) for x in a)):
            _err(errs, did, f"blank {i + 1}: 'answers' must be a non-empty list of strings")
            continue
        if "regex" in b:
            try:
                rx = re.compile(b["regex"])
                if not all(rx.fullmatch(norm(x)) for x in a):
                    _err(errs, did, f"blank {i + 1}: 'regex' does not match its own 'answers'")
            except (re.error, TypeError):
                _err(errs, did, f"blank {i + 1}: bad regex")
        o = b.get("options")
        if need_options and o is None:
            _err(errs, did, f"blank {i + 1}: 'options' is required here")
        if o is not None:
            if not (isinstance(o, list) and 2 <= len(o) <= 6 and all(_is_str(x, 1, 80) for x in o) and len(set(map(norm, o))) == len(o)):
                _err(errs, did, f"blank {i + 1}: 'options' must be 2-6 distinct strings")
            elif not any(norm(x) == norm(a[0]) for x in o):
                _err(errs, did, f"blank {i + 1}: 'options' must include the first answer")


def _lint_fill(d, java, errs, did):
    code = _code_ok(d, "code", errs, did, blanks=True)
    bl = d.get("blanks")
    k = code.count(BLANK)
    if not (isinstance(bl, list) and len(bl) == k and 1 <= k <= 8):
        return _err(errs, did, f"'code' has {k} '{BLANK}' but 'blanks' has {len(bl) if isinstance(bl, list) else '?'} entries (need 1-8, equal)")
    _lint_blanks(bl, errs, did)
    if "output" not in d and not d.get("norun"):
        _err(errs, did, "'output' (what the finished program prints) is required; run verify_drills.py --fix to fill it")


def _lint_predict(d, java, errs, did):
    _code_ok(d, "code", errs, did)
    if not isinstance(d.get("expected"), str) or not d["expected"].strip() or len(d["expected"]) > 800:
        _err(errs, did, "'expected' (real program output) is required, max 800 chars; run verify_drills.py --fix")
    if "stdin" in d and not isinstance(d["stdin"], str):
        _err(errs, did, "'stdin' must be a string")


def _lint_bug(d, java, errs, did):
    code = _code_ok(d, "code", errs, did)
    fixed = _code_ok(d, "fixed_code", errs, did)
    n = len(code.split("\n"))
    bl = d.get("bug_lines")
    if not (isinstance(bl, list) and 1 <= len(bl) <= 3 and all(isinstance(x, int) and not isinstance(x, bool) and 1 <= x <= n for x in bl)
            and bl == sorted(set(bl))):
        _err(errs, did, f"'bug_lines' must be 1-3 sorted unique line numbers within 1..{n}")
        return
    opts, ans = d.get("options"), d.get("answer")
    if not (isinstance(opts, list) and 3 <= len(opts) <= 4 and all(_is_str(x, 1, 300) for x in opts) and len(set(map(norm, opts))) == len(opts)):
        return _err(errs, did, "'options' must be 3-4 distinct strings")
    if not (isinstance(ans, int) and not isinstance(ans, bool) and 0 <= ans < len(opts)):
        return _err(errs, did, "'answer' must be the index (0-based) of the correct option")
    cl, fl = code.split("\n"), fixed.split("\n")
    if len(cl) != len(fl):
        return _err(errs, did, "'fixed_code' must have the same number of lines as 'code' (change lines, do not add or remove)")
    diff = [i + 1 for i in range(len(cl)) if cl[i] != fl[i]]
    if diff != bl:
        _err(errs, did, f"lines that differ between code and fixed_code are {diff} but bug_lines is {bl}")
    want = [norm(fl[i - 1]) for i in bl]
    if [norm(x) for x in opts[ans].split("\n")] != want:
        _err(errs, did, "the correct option must equal the fixed line(s) (one option line per bug line)")
    if not isinstance(d.get("output"), str) and not d.get("norun"):
        _err(errs, did, "'output' (what fixed_code prints) is required; run verify_drills.py --fix")
    br = d.get("buggy_runs")
    if not (isinstance(br, dict) and set(br) <= {"fails", "contains", "output"} and isinstance(br.get("fails"), bool)):
        return _err(errs, did, "'buggy_runs' must be {\"fails\": bool, \"contains\": str?, \"output\": str?}")
    if br["fails"] and not _is_str(br.get("contains"), 1, 200):
        _err(errs, did, "buggy_runs: when fails is true give 'contains' (e.g. the exception name or compiler message)")
    if not br["fails"] and not isinstance(br.get("output"), str):
        _err(errs, did, "buggy_runs: when fails is false give the wrong 'output' it really prints")


def _lint_review(d, java, errs, did):
    code = _code_ok(d, "code", errs, did, max_lines=45)
    n = len(code.split("\n"))
    seen = set()
    for key, lo, hi in (("issues", 2, 4), ("non_issues", 2, 5)):
        arr = d.get(key)
        if not (isinstance(arr, list) and lo <= len(arr) <= hi):
            _err(errs, did, f"'{key}' must have {lo}-{hi} entries")
            continue
        for j, it in enumerate(arr):
            ok = isinstance(it, dict) and set(it) <= {"id", "text", "why", "lines"} and _is_str(it.get("text"), 1, 200) and _is_str(it.get("why"), 1, 600)
            if not ok or not isinstance(it.get("id"), str) or not ID_RE.match(it["id"]):
                _err(errs, did, f"{key}[{j}] needs id, text (<=200), why (<=600)")
                continue
            if it["id"] in seen:
                _err(errs, did, f"duplicate item id '{it['id']}'")
            seen.add(it["id"])
            ln = it.get("lines", [])
            if not (isinstance(ln, list) and all(isinstance(x, int) and 1 <= x <= n for x in ln)):
                _err(errs, did, f"{key}[{j}].lines must be line numbers within 1..{n}")


def lint_doc(doc, day_no: int, java: bool) -> list[str]:
    if not isinstance(doc, dict):
        return ["file must contain a JSON object"]
    errs: list[str] = []
    if doc.get("day") != day_no:
        errs.append(f"'day' is {doc.get('day')!r} but the file is in day {day_no}")
    arr = doc.get("drills")
    if not (isinstance(arr, list) and 1 <= len(arr) <= 12):
        return errs + ["'drills' must be a list of 1-12 drills"]
    for k in doc:
        if k not in ("day", "drills", "title"):
            errs.append(f"unknown top-level key '{k}'")
    ids = [x.get("id") for x in arr if isinstance(x, dict)]
    for i in {i for i in ids if ids.count(i) > 1}:
        errs.append(f"duplicate drill id '{i}'")
    for x in arr:
        errs += lint_drill(normalize_drill(x), java) if isinstance(x, dict) else ["a drill must be an object"]
    return errs


# ---- learner view ---------------------------------------------------------------------------------------------
class Tok:
    """Opaque per-drill tokens for shuffled items, so answers refer to items without revealing their true index."""

    def __init__(self, secret: str, day: int, did: str):
        self.base = f"{secret}|{day}|{did}"

    def __call__(self, kind: str, i: int) -> str:
        return hashlib.sha256(f"{self.base}|{kind}|{i}".encode()).hexdigest()[:8]


def shuffled(seq, seed: str):
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16))
    out = list(seq)
    rng.shuffle(out)
    return out


def _blank_spans(d: dict) -> list[list[int]]:
    """For faded parsons: which blank numbers sit on each line (blanks are numbered in correct order)."""
    spans, k = [], 0
    for ln in d["lines"]:
        c = ln.count(BLANK)
        spans.append(list(range(k, k + c)))
        k += c
    return spans


def public_view(d: dict, tok: Tok, seed: str, java: bool) -> dict:
    """What the browser may see: everything needed to attempt the drill, nothing that gives the answer away."""
    t = d["type"]
    v = {k: d[k] for k in ("id", "type", "title", "prompt", "concepts") if k in d}
    v["viz"] = bool(d.get("viz"))
    v["wrap"] = bool(d.get("wrap"))
    if d.get("hint"):
        v["hint"] = d["hint"]
    if t == "parsons":
        spans = _blank_spans(d) if d.get("faded") else [[] for _ in d["lines"]]
        items = [("L", i, ln) for i, ln in enumerate(d["lines"])] + [("D", j, x) for j, x in enumerate(d.get("distractors", []))]
        order = shuffled(range(len(items)), seed + "|p")
        for salt in range(8):                              # never hand out the solved order
            if [items[k][1] for k in order if items[k][0] == "L"] != sorted(items[k][1] for k in order if items[k][0] == "L"):
                break
            order = shuffled(range(len(items)), seed + f"|p{salt}")
        v["items"] = []
        for k in order:
            kind, i, text = items[k]
            it = {"id": tok(kind, i), "text": text, "blanks": []}
            if kind == "L":
                for b in spans[i]:
                    it["blanks"].append({"id": tok("B", b), "options": shuffled(d["blanks"][b]["options"], seed + f"|b{b}")})
            v["items"].append(it)
        v["check_indent"] = display_indent(java, d)
        v["faded"] = bool(d.get("faded"))
        v["indent_by_braces"] = bool(java) and not v["check_indent"]
        if "output" in d:
            v["output"] = d["output"]
    elif t == "fill":
        v["code"] = d["code"]
        v["blanks"] = [{"id": tok("B", i), "size": max(len(norm(x)) for x in b["answers"]) if not b.get("options") else 0,
                        "options": shuffled(b["options"], seed + f"|b{i}") if b.get("options") else None}
                       for i, b in enumerate(d["blanks"])]
        if "output" in d:
            v["output"] = d["output"]
    elif t == "predict":
        v["code"] = d["code"]
        if d.get("stdin"):
            v["stdin"] = d["stdin"]
    elif t == "bug":
        v["code"] = d["code"]
        v["n_bugs"] = len(d["bug_lines"])
        v["options"] = [{"id": tok("O", i), "text": d["options"][i]} for i in shuffled(range(len(d["options"])), seed + "|o")]
        if "output" in d:
            v["output"] = d["output"]
    elif t == "review":
        its = [(x, True) for x in d["issues"]] + [(x, False) for x in d["non_issues"]]
        v["code"] = d["code"]
        v["n_issues"] = len(d["issues"])
        v["items"] = [{"id": tok("I", k), "text": its[k][0]["text"]} for k in shuffled(range(len(its)), seed + "|i")]
    return v


def solution_view(d: dict, java: bool) -> dict:
    """Revealed after a correct check or "give up"."""
    t = d["type"]
    if t == "parsons":
        ls = parsons_lines(d)
        return {"code": "\n".join(ls), "lines": ls, "blanks": [b["answers"][0] for b in d["blanks"]] if d.get("faded") else []}
    if t == "fill":
        vals = [b["answers"][0] for b in d["blanks"]]
        return {"blanks": vals, "code": fill_code(d["code"], vals)}
    if t == "predict":
        return {"output": d["expected"]}
    if t == "bug":
        return {"lines": d["bug_lines"], "fix": d["options"][d["answer"]], "code": d["fixed_code"]}
    its = [(x, True) for x in d["issues"]] + [(x, False) for x in d["non_issues"]]
    return {"items": [{"text": x["text"], "real": r, "why": x["why"], "lines": x.get("lines", [])} for x, r in its]}


# ---- checking ------------------------------------------------------------------------------------------------
class BadAnswer(ValueError):
    pass


def _list(v, hi, what, kind=None):
    if not isinstance(v, list) or len(v) > hi or (kind and not all(isinstance(x, kind) and not isinstance(x, bool) for x in v)):
        raise BadAnswer(f"{what} must be a list of at most {hi} items")
    return v


def _val(v) -> str:
    if not isinstance(v, str) or len(v) > 200:
        raise BadAnswer("answers must be short text")
    return v


def blank_ok(b: dict, given: str) -> bool:
    g = norm(given)
    if any(g == norm(a) for a in b["answers"]):
        return True
    rx = b.get("regex")
    return bool(rx and re.fullmatch(rx, g))


def _lines_of(text: str) -> list[str]:
    ls = [ln.rstrip() for ln in str(text).replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while ls and not ls[-1]:
        ls.pop()
    while ls and not ls[0]:
        ls.pop(0)
    return ls


def check(d: dict, answer, tok: Tok, java: bool) -> tuple[bool, float, dict]:
    """Returns (ok, score 0..1, feedback). Raises BadAnswer on a malformed or stale answer."""
    if not isinstance(answer, dict):
        raise BadAnswer("answer must be an object")
    t = d["type"]
    if t == "parsons":
        return _check_parsons(d, answer, tok, java)
    if t == "fill":
        vals = [_val(x) for x in _list(answer.get("blanks"), 8, "blanks")]
        if len(vals) != len(d["blanks"]):
            raise BadAnswer("wrong number of blanks")
        res = [blank_ok(b, v) for b, v in zip(d["blanks"], vals)]
        return all(res), sum(res) / len(res), {"blanks": res}
    if t == "predict":
        txt = answer.get("text")
        if not isinstance(txt, str) or len(txt) > 4000:
            raise BadAnswer("text must be a string up to 4000 characters")
        exp, got = _lines_of(d["expected"]), _lines_of(txt)
        res = [i < len(exp) and got[i] == exp[i] for i in range(len(got))]
        score = sum(res) / max(len(exp), len(got), 1)
        return got == exp, score, {"lines": res, "expected_lines": len(exp)}
    if t == "bug":
        picked = _list(answer.get("lines"), 12, "lines", int)
        o = answer.get("option")
        rev = {tok("O", i): i for i in range(len(d["options"]))}
        if o is not None and o not in rev:
            raise BadAnswer("stale option; reload the drill")
        want, got = set(d["bug_lines"]), set(picked)
        lines_ok = got == want
        opt_ok = o is not None and rev[o] == d["answer"]
        jac = len(want & got) / len(want | got) if (want | got) else 0
        score = 0.5 * jac + 0.5 * opt_ok
        return lines_ok and opt_ok, score, {"lines_ok": lines_ok, "option_ok": opt_ok, "right": sorted(want & got),
                                            "wrong": sorted(got - want), "missed": len(want - got)}
    picks = [_val(x) for x in _list(answer.get("picks"), 12, "picks")]
    items = [(x, True) for x in d["issues"]] + [(x, False) for x in d["non_issues"]]
    rev = {tok("I", k): k for k in range(len(items))}
    if any(p not in rev for p in picks):
        raise BadAnswer("stale item; reload the drill")
    ticked = {rev[p] for p in picks}
    right = sum(1 for k in ticked if items[k][1])
    wrong = len(ticked) - right
    n = len(d["issues"])
    fb = {"right": right, "wrong": wrong, "missed": n - right, "total": n,
          "items": [{"id": tok("I", k), "ticked": k in ticked, "real": items[k][1] if k in ticked else None,
                     "why": items[k][0]["why"] if k in ticked else None, "lines": items[k][0].get("lines", []) if k in ticked else []}
                    for k in range(len(items))]}
    return right == n and wrong == 0, max(0, right - wrong) / n, fb


def _check_parsons(d, a, tok, java):
    n = len(d["lines"])
    order = [_val(x) for x in _list(a.get("order"), 20, "order")]
    ind = _list(a.get("indents", []), 20, "indents", int)
    if len(ind) != len(order):
        ind = (ind + [0] * len(order))[: len(order)]
    texts = {tok("L", i): ("L", i) for i in range(n)} | {tok("D", j): ("D", j) for j in range(len(d.get("distractors", [])))}
    if any(o not in texts for o in order) or len(set(order)) != len(order):
        raise BadAnswer("stale or repeated line; reload the drill")
    want_ind = d.get("indent") or [0] * n
    use_ind = display_indent(java, d)
    cands = [list(range(n))] + [list(a_) for a_ in d.get("alternatives", [])]
    best = None
    for cand in cands:
        marks = []
        for p, o in enumerate(order):
            kind, i = texts[o]
            if kind == "D":
                marks.append("distractor")
            elif p >= n or d["lines"][i] != d["lines"][cand[p]]:
                marks.append("position")
            elif use_ind and ind[p] != want_ind[cand[p]]:
                marks.append("indent")
            else:
                marks.append("ok")
        if best is None or marks.count("ok") > best.count("ok"):
            best = marks
    bres, units_ok = {}, 0
    if d.get("faded"):
        vals = a.get("blanks", {})
        if not isinstance(vals, dict) or len(vals) > 20:
            raise BadAnswer("blanks must be an object")
        for b, spec in enumerate(d["blanks"]):
            v = vals.get(tok("B", b))
            bres[tok("B", b)] = isinstance(v, str) and len(v) <= 200 and blank_ok(spec, v)
        units_ok = sum(bres.values())
    units = n + (len(d["blanks"]) if d.get("faded") else 0)
    done = best.count("ok") + units_ok
    ok = done == units and len(order) == n and all(m == "ok" for m in best)
    return ok, done / units, {"lines": best, "blanks": bres, "missing": max(0, n - len(order))}
