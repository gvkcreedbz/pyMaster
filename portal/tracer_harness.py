"""Runs a learner's script under a line tracer and writes a step-by-step JSON recording.

Invoked by portal/visual.py:  python tracer_harness.py <script.py> <max_steps> <result.json>
Records, for every executed line, the call stack, each frame's variables and the objects they point to,
so the portal can draw "memory boxes and arrows" (like Python Tutor).
"""
import io
import json
import sys
import types

TARGET, MAX_STEPS, RESULT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
MAX_ITEMS, MAX_DEPTH, MAX_HEAP = 24, 4, 60


class StopTrace(BaseException):
    pass


class Tee(io.StringIO):
    def isatty(self):
        return False


out = Tee()
steps = []
state = {"truncated": False}


def enc(v, heap, depth=0):
    """Encode a value as {p: shown-inline, k: kind} or {ref: object id} (objects go in the heap)."""
    t = type(v).__name__
    if v is None or isinstance(v, (bool, int, float, complex)):
        return {"p": repr(v), "k": t}
    if isinstance(v, str):
        return {"p": repr(v if len(v) <= 60 else v[:57] + "..."), "k": "str"}
    if isinstance(v, types.ModuleType):
        return {"p": "module " + v.__name__, "k": "module"}
    if isinstance(v, (types.FunctionType, types.BuiltinFunctionType, types.MethodType)):
        return {"p": "function " + getattr(v, "__name__", "?"), "k": "func"}
    if isinstance(v, type):
        return {"p": "class " + v.__name__, "k": "func"}
    i = id(v)
    if i in heap:
        return {"ref": i}
    if depth > MAX_DEPTH or len(heap) > MAX_HEAP:
        return {"p": "...", "k": t}
    if isinstance(v, (list, tuple, set, frozenset)):
        box = heap[i] = {"k": t, "items": [], "more": max(0, len(v) - MAX_ITEMS)}
        box["items"] = [enc(x, heap, depth + 1) for x in list(v)[:MAX_ITEMS]]
    elif isinstance(v, dict):
        box = heap[i] = {"k": "dict", "items": [], "more": max(0, len(v) - MAX_ITEMS)}
        box["items"] = [[enc(k, heap, depth + 1), enc(x, heap, depth + 1)] for k, x in list(v.items())[:MAX_ITEMS]]
    elif hasattr(v, "__dict__") and not callable(v):
        box = heap[i] = {"k": "object", "cls": t, "attrs": {}}
        for name, x in list(vars(v).items())[:MAX_ITEMS]:
            box["attrs"][name] = enc(x, heap, depth + 1)
    else:
        return {"p": repr(v)[:60], "k": t}
    return {"ref": i}


def snapshot(frame, heap):
    stack = []
    f = frame
    while f is not None:
        if f.f_code.co_filename == TARGET:
            is_module = f.f_code.co_name == "<module>"
            src = f.f_globals if is_module else f.f_locals
            vars_ = {}
            for name, val in list(src.items()):
                if name.startswith("__"):
                    continue
                if is_module and isinstance(val, (types.ModuleType, types.FunctionType, type)):
                    continue
                vars_[name] = enc(val, heap)
            stack.append({"name": "Global" if is_module else f.f_code.co_name + "()", "vars": vars_})
        f = f.f_back
    stack.reverse()
    return stack


def tracer(frame, event, arg):
    if frame.f_code.co_filename != TARGET:
        return None
    if event in ("line", "return", "exception"):
        if len(steps) >= MAX_STEPS:
            state["truncated"] = True
            raise StopTrace()
        heap = {}
        rec = {"line": frame.f_lineno, "ev": event, "stack": snapshot(frame, heap), "out": len(out.getvalue())}
        if event == "return" and frame.f_code.co_name != "<module>":
            rec["ret"] = enc(arg, heap)
        if event == "exception":
            rec["err"] = f"{arg[0].__name__}: {arg[1]}"
        rec["heap"] = heap
        steps.append(rec)
    return tracer


result = {"steps": steps, "error": None}
real_stdout = sys.stdout
try:
    source = open(TARGET, encoding="utf-8").read()
    code = compile(source, TARGET, "exec")
    g = {"__name__": "__main__", "__file__": TARGET, "__builtins__": __builtins__}
    sys.stdout = out
    sys.settrace(tracer)
    try:
        exec(code, g)
    finally:
        sys.settrace(None)
        sys.stdout = real_stdout
except StopTrace:
    pass
except SystemExit:
    pass
except BaseException as e:  # noqa: BLE001
    tb = e.__traceback__
    line = None
    while tb:
        if tb.tb_frame.f_code.co_filename == TARGET:
            line = tb.tb_lineno
        tb = tb.tb_next
    result["error"] = {"type": type(e).__name__, "msg": str(e)[:300], "line": line}
result["output"] = out.getvalue()[-6000:]
result["truncated"] = state["truncated"]
result["total_steps"] = len(steps)
with open(RESULT, "w", encoding="utf-8") as fh:
    json.dump(result, fh)
