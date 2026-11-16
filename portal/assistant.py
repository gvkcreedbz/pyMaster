"""The tutor beside the lesson.

Provider chain (first configured wins, failures fall through):
  1. Cursor SDK   (CURSOR_API_KEY)     - the real Cursor agent as your tutor
  2. Anthropic    (ANTHROPIC_API_KEY)
  3. OpenAI       (OPENAI_API_KEY)
  4. Offline tutor - built in, no key needed; strong on "where / how is this used?"
"""
from __future__ import annotations

import ast
import json
import os
import re
from typing import Iterator

from . import content, db, track

if track.IS_JAVA:
    from . import java_assist as _jl
    from .kb_java import GENERIC_USAGE, KB, VISUALS
else:
    _jl = None
    from .kb import GENERIC_USAGE, KB, VISUALS

QUICK = {
    "where_used": "Where and how is this used in the real world? Who uses it, in what kind of project, and what does it look like there?",
    "explain_simple": "Explain this in the simplest possible words, with an everyday analogy.",
    "example": "Show me a real-world example that is a bit harder than the lesson's, with a step-by-step walkthrough.",
    "why": "Why does it work this way? What's actually going on under the hood?",
    "quiz": "Quiz me on what I've learned in this lesson, one question at a time.",
    "review": "Review my code: what's good, what could be cleaner, any bugs? Coach me; don't just rewrite it.",
    "hint": "Give me the next hint for the exercise I'm on, without giving away the full answer.",
    "recap": "Give me a quick 2-minute recap of this lesson.",
    "visual": "Show me a visual: draw a diagram that explains this code (or idea) step by step.",
    # not shown as buttons; sent by the "Want more?" chip and the "Show the answer anyway" button (see ex_tutor.py)
    "more": "Go deeper on your last answer, with a fuller explanation and a worked example.",
    "answer_anyway": "Show me the full answer for this exercise. I would like to see it now.",
}

_SYSTEM = """You are **Py Master Tutor**, a warm, sharp Python mentor sitting beside the lesson in a 30-day course.
The learner began with zero coding knowledge and wants to get well beyond intermediate, aiming at data/AI work and automation/backend work.

How to teach:
- Plain words, short paragraphs. Define any jargon in one line. No walls of text; usually under ~300 words unless they ask for depth.
- When asked "where / how is this used", ALWAYS give: (1) a one-sentence answer, (2) 2-3 concrete real-world scenarios (kinds of companies, apps, jobs), (3) a tiny realistic code snippet as used on the job with a line-by-line explanation, (4) one common pitfall, (5) a "try it" micro-challenge.
- For graded exercises: coach, don't hand over the full solution. Give the next hint unless they've clearly attempted and explicitly ask for the answer.
- If their code, selection or error output is attached, use it specifically (quote the exact line).
- Connect ideas to earlier days when helpful. End with one short check-for-understanding question when it fits.
- Use Markdown with fenced ```python code blocks. Never invent library features; if unsure, say so.
- When asked for a visual / diagram / "show me", answer with a ```mermaid block (flowchart TD/LR, sequenceDiagram or similar; short quoted labels, no HTML except <br/>) followed by 3-5 plain-language bullets that walk through it. For code that changes data, also give a small table of how the variables change line by line.
- This is chat only: do NOT create files, run commands or use tools. Just answer."""
SYSTEM = _SYSTEM
if track.IS_JAVA:
    SYSTEM = (_SYSTEM.replace("Py Master Tutor", "Java Master Tutor").replace("Python", "Java")
              .replace("```python", "```java")
              .replace("data/AI work and automation/backend work", "back-end and enterprise software work"))
_FENCE = track.T["fence"]


def _tx():
    """The tutor-extras module (try-first gate, answer style, run context). A problem there never stops an answer."""
    try:
        from . import ex_tutor
        return ex_tutor
    except Exception:  # noqa: BLE001
        return None


_STYLE_CONCISE = (
    "ANSWER STYLE = CONCISE. This overrides the length and structure rules above, including the 5-part 'where is this used' format. "
    "Give a direct answer in 3-6 short lines (at most ~120 words), then exactly ONE tiny runnable example, no filler, no preamble, "
    "no closing offers. The app adds its own 'Want more?' button, so do not ask whether they want more.")
_STYLE_DETAILED = (
    "ANSWER STYLE = DETAILED. A fuller explanation with a line-by-line walk-through is welcome (plain words, under ~300 words).")
_VERIFIED = (
    "Never present output as real unless it came from actually running the code. If you show output, label it 'expected output'. "
    "The learner can press 'Run it' under any example to see the real output, so keep examples short, self-contained and runnable.")


def style_block(style: str) -> str:
    return (_STYLE_CONCISE if style == "concise" else _STYLE_DETAILED) + " " + _VERIFIED


# ---- configuration -----------------------------------------------------------------------------
def key(name: str) -> str | None:
    env = {"cursor": "CURSOR_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}[name]
    return db.get_setting(f"key_{name}") or os.environ.get(env) or None


def model(name: str) -> str:
    defaults = {"cursor": "composer-2.5", "anthropic": "claude-sonnet-4-5", "openai": "gpt-4o-mini"}
    return db.get_setting(f"model_{name}") or defaults[name]


def available() -> list[str]:
    return [p for p in ("cursor", "anthropic", "openai") if key(p)]


def status() -> dict:
    pref = db.get_setting("provider_pref", "auto")
    avail = available()
    active = pref if pref in avail else (avail[0] if avail and pref in ("auto", "") else (avail[0] if avail else "offline"))
    if pref == "offline":
        active = "offline"
    return {
        "pref": pref, "active": active,
        "providers": {p: {"configured": bool(key(p)), "model": model(p),
                          "source": "settings" if db.get_setting(f"key_{p}") else ("env" if key(p) else None)}
                      for p in ("cursor", "anthropic", "openai")},
    }


# ---- prompt building ---------------------------------------------------------------------------
def build_context(ctx: dict) -> str:
    n = ctx.get("day_no")
    d = content.day(n) if n else None
    parts = []
    if d:
        parts.append(f"CURRENT LESSON: Day {n} - {d['title']} (week {d['week']}). Goal: {d['goal']}")
        parts.append(f"Real-world scenario of the day: {d['scenario'][:500]}")
        parts.append("Concepts today: " + ", ".join(d["concepts"][:12]))
        if ctx.get("exercise_id"):
            ex = next((e for e in d["exercises"] if e["id"] == ctx["exercise_id"]), None)
            if ex:
                parts.append(f"The learner is working on exercise {ex['id']} ({ex['title']}):\n{ex['desc']}")
        failing = db.rows("SELECT check_id, name FROM checks WHERE day_no=? AND last_status='FAIL' LIMIT 6", (n,))
        if failing:
            parts.append("Currently failing checks: " + ", ".join(f"{f['check_id']} {f['name']}" for f in failing))
        tx = _tx()
        if tx:
            try:
                block = tx.context_block(n, bool(ctx.get("output")))
                if block:
                    parts.append(block)
            except Exception:  # noqa: BLE001
                pass
    if ctx.get("tab"):
        parts.append(f"Learner is on the '{ctx['tab']}' tab.")
    if ctx.get("selection"):
        parts.append("TEXT/CODE THE LEARNER HIGHLIGHTED:\n" + ctx["selection"][:1500])
    if ctx.get("code"):
        parts.append(f"LEARNER'S CURRENT CODE:\n```{_FENCE}\n" + ctx["code"][:4500] + "\n```")
    if ctx.get("output"):
        parts.append("LAST RUN OUTPUT:\n```\n" + ctx["output"][-1500:] + "\n```")
    return "\n\n".join(parts)


# ---- providers (LLMs) --------------------------------------------------------------------------
_patched = False


def _patch_sdk_for_windows() -> None:
    """cursor-sdk 1.3.x waits for its bridge with select() on a pipe, which only works for sockets on
    Windows (WinError 10038). Read the bridge's discovery line from a thread instead."""
    global _patched
    if _patched or os.name != "nt":
        return
    import queue
    import threading
    import time

    from cursor_sdk import _bridge as b

    def read_discovery(process, timeout):
        q: queue.Queue = queue.Queue()

        def pump():
            for line in process.stderr:
                q.put(line)
            q.put(None)

        threading.Thread(target=pump, daemon=True).start()
        seen, deadline = [], time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                line = q.get(timeout=0.2)
            except queue.Empty:
                continue
            if line is None:
                raise b.CursorSDKError("Bridge exited before discovery: " + "".join(seen))
            seen.append(line)
            found = b.parse_discovery_line(line)
            if found is not None:
                return found
        raise b.CursorSDKError("Timed out waiting for bridge discovery")

    b._read_discovery = read_discovery
    _patched = True


def _cursor(history: list[dict], user_msg: str, context: str) -> Iterator[str]:
    from cursor_sdk import Agent, LocalAgentOptions   # imported lazily so the portal runs without it
    _patch_sdk_for_windows()

    ws = db.DATA_DIR / "tutor_ws"
    ws.mkdir(parents=True, exist_ok=True)
    convo = "\n".join(f"{'Learner' if m['role'] == 'user' else 'Tutor'}: {m['content'][:1200]}" for m in history[-6:])
    prompt = f"{SYSTEM}\n\n=== CONTEXT ===\n{context}\n\n=== CONVERSATION SO FAR ===\n{convo or '(none)'}\n\n=== LEARNER NOW ===\n{user_msg}"
    agent = Agent.create(model=model("cursor"), api_key=key("cursor"), name=f"{track.T['short']} tutor",
                         local=LocalAgentOptions(cwd=str(ws)))
    try:
        run = agent.send(prompt)
        got = False
        for chunk in run.iter_text():
            got = True
            yield chunk
        if not got:
            raise RuntimeError("Cursor agent returned no text")
    finally:
        try:
            agent.close()
        except Exception:
            pass


def _sse_json(lines) -> Iterator[dict]:
    for line in lines:
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data != "[DONE]":
                try:
                    yield json.loads(data)
                except ValueError:
                    pass


def _anthropic(history, user_msg, context) -> Iterator[str]:
    import httpx
    msgs = [{"role": m["role"], "content": m["content"][:3000]} for m in history[-6:]]
    msgs.append({"role": "user", "content": user_msg})
    body = {"model": model("anthropic"), "max_tokens": 1400, "stream": True,
            "system": SYSTEM + "\n\n=== CONTEXT ===\n" + context, "messages": msgs}
    with httpx.stream("POST", "https://api.anthropic.com/v1/messages", timeout=90, json=body,
                      headers={"x-api-key": key("anthropic"), "anthropic-version": "2023-06-01"}) as r:
        if r.status_code >= 400:
            raise RuntimeError(f"Anthropic {r.status_code}: {r.read().decode('utf-8', 'replace')[:200]}")
        for ev in _sse_json(r.iter_lines()):
            if ev.get("type") == "content_block_delta":
                yield ev["delta"].get("text", "")


def _openai(history, user_msg, context) -> Iterator[str]:
    import httpx
    msgs = [{"role": "system", "content": SYSTEM + "\n\n=== CONTEXT ===\n" + context}]
    msgs += [{"role": m["role"], "content": m["content"][:3000]} for m in history[-6:]]
    msgs.append({"role": "user", "content": user_msg})
    body = {"model": model("openai"), "stream": True, "messages": msgs, "max_tokens": 1400}
    with httpx.stream("POST", "https://api.openai.com/v1/chat/completions", timeout=90, json=body,
                      headers={"Authorization": f"Bearer {key('openai')}"}) as r:
        if r.status_code >= 400:
            raise RuntimeError(f"OpenAI {r.status_code}: {r.read().decode('utf-8', 'replace')[:200]}")
        for ev in _sse_json(r.iter_lines()):
            delta = (ev.get("choices") or [{}])[0].get("delta", {}).get("content")
            if delta:
                yield delta


PROVIDERS = {"cursor": _cursor, "anthropic": _anthropic, "openai": _openai}


# ---- offline tutor -----------------------------------------------------------------------------
INTENT_RX = [
    ("reveal", re.compile(r"^\s*(reveal|show (me )?the answer|what'?s the answer|answer\??|i give up|next)\b", re.I)),
    ("visual", re.compile(r"\b(visual|visually|visuali[sz]e|diagram|flow ?chart|draw|picture|illustrat\w+|graphic(al)?(ly)?|map (it|this) out|step[- ]by[- ]step trace|trace (it|this|the code))\b", re.I)),
    ("quiz", re.compile(r"\b(quiz me|test me|ask me a question|practice questions?)\b", re.I)),
    ("hint", re.compile(r"\b(hint|stuck|clue|nudge|next step)\b", re.I)),
    ("recap", re.compile(r"\b(recap|summar(y|ise|ize)|what did i learn|revision|revise)\b", re.I)),
    ("review", re.compile(r"\b(review|feedback|is this good|check my code|improve|cleaner|refactor)\b", re.I)),
    ("debug", re.compile(r"(Traceback|\b\w+Error\b|not working|doesn'?t work|fails?|failing|bug|crash)", re.I)),
    ("where_used", re.compile(r"(where|how).{0,40}\b(use|used|using|apply|applied)\b|real[- ]world|real life|use ?case|"
                              r"in production|companies|in practice|on the job|why would i (need|use)|when would i", re.I)),
    ("example", re.compile(r"\b(example|harder|challenge|more advanced|another one)\b", re.I)),
    ("explain_simple", re.compile(r"\b(simple|simply|eli5|analogy|confus|don'?t (get|understand)|plain)\b", re.I)),
    ("why", re.compile(r"\bwhy\b|\bhow does\b|under the hood|what happens", re.I)),
]


def detect_intent(text: str, quick_id: str | None) -> str:
    if quick_id in QUICK:
        return quick_id
    for name, rx in INTENT_RX:
        if rx.search(text):
            return name
    return "concept"


def find_concepts(text: str, selection: str, code: str, day_no: int | None) -> list[dict]:
    t, s, c = text.lower(), (selection or "").lower(), (code or "").lower()
    scored = []
    for e in KB:
        sc = 0.0
        for k in e["keys"]:
            kl = k.lower()
            if re.search(r"[^a-z0-9_]", kl):       # symbols/phrases: substring match
                hit = lambda hay, kl=kl: kl in hay
            else:
                rx = re.compile(r"(?<![a-z0-9_])" + re.escape(kl) + r"(?:e?s)?(?![a-z0-9_])")
                hit = lambda hay, rx=rx: bool(rx.search(hay))
            if hit(t): sc += 3
            if hit(s): sc += 3
            if hit(c): sc += 0.7
        if sc and day_no and day_no in e["days"]:
            sc += 1.5                      # prefer today's topic when several match
        if sc:
            scored.append((sc, e))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return []
    top = scored[0][0]
    # the best match always counts; extras must be a genuine match (named in the question/selection), not stray code keywords
    return [scored[0][1]] + [e for s, e in scored[1:3] if s >= 3 and s >= 0.5 * top]


def day_concepts(day_no: int | None) -> list[dict]:
    return [e for e in KB if day_no and day_no in e["days"]]


def _first_sentence(s: str) -> str:
    return re.split(r"(?<=[.!?])\s", s, maxsplit=1)[0]


def _entry_where(e: dict) -> str:
    return (f"### {e['name']}: where and how it's used\n\n**In one line:** {_first_sentence(e['what'])}\n\n"
            f"**Where you'll meet it**\n{e['where']}\n\n**How it looks on the job**\n{e['how']}\n\n"
            f"**Watch out:** {e['pitfall']}\n\n**Try it:** {e['nxt']}")


def _decode_error(text: str) -> str | None:
    if _jl:
        return _jl.decode_error(text)
    m = re.search(r"\b([A-Z]\w*(?:Error|Exception|Iteration))\b", text)
    if not m:
        return None
    name = m.group(1)
    doc = content.read(content.ROOT / "cheatsheets" / "error_decoder.md")
    rows = [ln for ln in doc.splitlines()
            if ln.startswith("|") and ln.count("|") > 2 and name in ln.split("|")[1]]
    if not rows:
        return f"`{name}`: read the **last line** of the traceback first, then the line number just above it."
    out = []
    for r in rows[:2]:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) >= 3:
            out.append(f"- {cells[0]}: **{cells[1]}**. Typical fix: {cells[2]}")
    return "\n".join(out)


def static_review(code: str) -> list[str]:
    if _jl:
        return _jl.static_review(code)
    notes = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"**Syntax problem on line {e.lineno}:** {e.msg}. Python often reports the line *after* the real mistake (check a missing `:`, quote or bracket just above)."]
    if "TODO" in code or re.search(r"^\s*pass\s*(#.*)?$", code, re.M):
        notes.append("There are still `pass` / `TODO` placeholders, so those functions return `None`.")
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dflt in node.args.defaults:
                if isinstance(dflt, (ast.List, ast.Dict, ast.Set)):
                    notes.append(f"`{node.name}` has a mutable default argument; it's shared between calls. Use `None` and create the list inside.")
            has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
            if not has_return and node.name != "main" and len(node.body) <= 3 and not node.name.startswith("__"):
                notes.append(f"`{node.name}` never returns a value. If you expected a result, add `return`.")
            if not ast.get_docstring(node) and len(node.body) > 4:
                notes.append(f"`{node.name}` is longer than a few lines and has no docstring; one sentence helps future-you.")
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            notes.append("A bare `except:` hides real bugs. Catch a specific error such as `ValueError`.")
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comp, ast.Constant) and isinstance(comp.value, bool):
                    notes.append("Compare booleans directly: write `if flag:` instead of `if flag == True:`.")
    names = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and len(n.id) == 1 and n.id not in "ijkxyn_"]
    if names:
        notes.append(f"Single-letter names like `{names[0]}` make code harder to read; name what it *means*.")
    return notes[:5]


def _looks_code(text: str) -> bool:
    if not text.strip():
        return False
    if _jl:
        return _jl.looks_code(text)
    from . import visual
    if visual.looks_like_sql(text):
        return True
    try:
        ast.parse(text)
    except SyntaxError:
        return False
    # a single bare word parses as a name; require a code-like shape
    return bool(re.search(r"[=():\[\]{}]|^\s*(import|from|def|class|for|while|if)\b", text, re.M))


def visual_answer(question: str, ctx: dict, concepts: list[dict]) -> str:
    """Offline 'show me a visual': a Mermaid diagram for code/SQL, otherwise a concept picture."""
    from . import visual
    sel, code = (ctx.get("selection") or "").strip(), (ctx.get("code") or "").strip()
    src = sel if _looks_code(sel) else (code if _looks_code(code) else "")
    if src:
        try:
            dg = visual.diagram(src, None)
        except Exception as e:  # noqa: BLE001
            dg = {"mermaid": "", "caption": f"({type(e).__name__})"}
        if dg.get("mermaid"):
            what = "the highlighted code" if src == sel else "your code in the editor"
            if dg.get("kind") == "sql":
                head, tail = "### The order this query actually runs in", \
                    "Remember: you *write* SELECT first, but the database *reads* FROM first."
            else:
                head = f"### How control flows through {what}"
                tail = ("Want to *watch* it run? Press **▶ Visualize** above the code to step through it line by line "
                        "and see variables and objects change.")
            return f"{head}\n\n```mermaid\n{dg['mermaid']}\n```\n\n*{dg.get('caption', '')}*\n\n{tail}"
    for c in concepts + [x for x in day_concepts(ctx.get("day_no")) if x not in concepts]:
        v = VISUALS.get(c["id"])
        if v:
            return (f"### {v['title']}\n\n```mermaid\n{v['mermaid']}\n```\n\n*{v['caption']}*\n\n"
                    f"**In words:** {_first_sentence(c['what'])}\n\n"
                    "Highlight any code in the lesson and ask again for a diagram of *that* code.")
    return ("I can draw a picture of code or an idea. **Highlight a snippet** in the lesson (or write code in the editor) "
            "and ask again, or press **▶ Visualize** on any code block to step through it.\n\n"
            "Or name the idea: *variables, lists, loops, dicts, functions, classes, pandas groupby, SQL, APIs…*")


_MORE = "\n\n<!--tutor:more-->"       # the page turns this marker into the single "Want more?" chip


def _sentences(s: str, k: int) -> str:
    parts = re.split(r"(?<=[.!?])\s+", s.strip())
    return " ".join(parts[:k])


def _bullets(s: str, k: int = 3) -> list[str]:
    items = [re.sub(r"^\s*[-*]\s*", "", ln).strip() for ln in s.splitlines() if ln.strip().startswith(("-", "*"))]
    return [_first_sentence(i) for i in (items or [s.strip()])[:k] if i]


def _first_block(how: str) -> str:
    """The first fenced example of a KB entry, whole (never cut, so the page's Run it button gets runnable code)."""
    m = re.search(r"```[^\n]*\n.*?```", how, re.S)
    return m.group(0) if m else ""


def _concise_entry(e: dict, intent: str) -> str:
    """3-6 lines + one tiny example + the 'Want more?' marker."""
    name, ex = e["name"], _first_block(e["how"])
    if intent == "where_used":
        bl = "\n".join(f"- {b}" for b in _bullets(e["where"], 3))
        body = (f"### {name}: where it's used\n\n{_first_sentence(e['what'])}\n\n**Where you'll meet it**\n{bl}\n\n{ex}\n\n"
                f"**Watch out:** {_first_sentence(e['pitfall'])}")
    elif intent == "explain_simple":
        body = f"### {name}, simply\n\n{_sentences(e['what'], 2)}\n\n{ex}"
    elif intent == "example":
        body = f"### A realistic example: {name}\n\n{ex}\n\n**Level it up:** {_first_sentence(e['nxt'])}"
    elif intent == "why":
        body = f"### Why {name} works this way\n\n{_first_sentence(e['what'])}\n\n**The gotcha that shows it:** {_first_sentence(e['pitfall'])}\n\n{ex}"
    else:
        used = _bullets(e["where"], 1)
        body = f"### {name}\n\n{_sentences(e['what'], 2)}\n\n{ex}" + (f"\n\n**Used for:** {used[0]}" if used else "")
    return body.strip() + _MORE


def _is_solution_request(question: str, quick_id: str | None, ctx: dict, history_today: list[dict]) -> bool:
    """Explicit 'show me the answer' for a practice exercise (the offline tutor answers it with the reference solution)."""
    if quick_id == "answer_anyway" or ctx.get("gate_override"):
        return True
    tx = _tx()
    if not tx or quick_id or not tx.is_solution_request(question):
        return False
    if any((m.get("meta") or {}).get("quiz_q") for m in history_today[-2:]):
        return False
    return bool(ctx.get("tab") == "practice" or ctx.get("exercise_id"))


def _solution_answer(d: dict, ctx: dict) -> str:
    ex = next((e for e in d["exercises"] if e["id"] == ctx.get("exercise_id")), None)
    tx = _tx()
    code = tx.solution_excerpt(d, ex["id"]) if (tx and ex) else None
    if not code:
        return ("The full reference solution is behind the **Solution** button on the Practice tab (opening it is logged, never blocked). "
                "Tell me which exercise you mean and I can give a hint instead.")
    att = db.one("SELECT COUNT(*) c FROM attempts WHERE day_no=? AND kind='practice'", (d["n"],))["c"]
    db.log_event(ctx.get("sid"), "solution_view", d["n"], {"attempts_before": att, "via": "tutor"})
    return (f"### Reference answer: {ex['id']} · {ex['title']}\n\n```{_FENCE}\n{code}\n```\n\n"
            "Read it line by line and say each line aloud in plain words. Then close it and rewrite it from memory; that is where it sticks.")


def _run_note(n: int | None) -> str:
    tx = _tx()
    try:
        return tx.run_note(n) if tx else ""
    except Exception:  # noqa: BLE001
        return ""


def offline_answer(question: str, quick_id: str | None, ctx: dict, history_today: list[dict]) -> str:
    n = ctx.get("day_no")
    d = content.day(n) if n else None
    sel, code, output = ctx.get("selection") or "", ctx.get("code") or "", ctx.get("output") or ""
    intent = detect_intent(question, quick_id)
    tx = _tx()
    style = tx.answer_style(ctx) if tx else "detailed"
    if quick_id == "more":                          # the "Want more?" chip: same topic, full detail
        style = "detailed"
    if intent in ("more", "answer_anyway"):
        intent = detect_intent(question, None)
    if re.match(r"^\s*(hi|hello|hey|thanks|thank you|ok|okay|cool)\b[\s!.]*$", question, re.I):
        return "Hi! Ask me anything about this lesson. Try **“where would I actually use this?”** or highlight some code and use a quick action below."
    if d and _is_solution_request(question, quick_id, ctx, history_today):
        return _solution_answer(d, ctx)
    concise = style == "concise"
    concepts = find_concepts(question + " " + sel, sel, code, n)
    if not concepts and intent != "concept":      # "where is this used?" with no topic named -> today's main idea
        concepts = day_concepts(n)[:1]

    if intent == "visual":
        return visual_answer(question, ctx, concepts)

    if intent == "reveal":
        last = next((m for m in reversed(history_today) if m.get("meta", {}).get("quiz_q")), None)
        if d and last:
            q = next((x for x in d["quiz"] if x["n"] == last["meta"]["quiz_q"]), None)
            if q:
                return f"**Answer to question {q['n']}:** {q['a']}\n\nDid you get it? Rate it honestly on the **Quiz** tab, or say **quiz me** for the next one."
        return "I haven't asked you a quiz question yet. Say **quiz me** and I'll start."

    if intent == "quiz" and d and d["quiz"]:
        asked = [m["meta"]["quiz_q"] for m in history_today if m.get("meta", {}).get("quiz_q")]
        rated = {r["q_no"] for r in db.rows("SELECT q_no FROM quiz WHERE day_no=? AND rating IS NOT NULL", (n,))}
        pool = [q for q in d["quiz"] if q["n"] not in rated and q["n"] not in asked] or [q for q in d["quiz"] if q["n"] not in asked] or d["quiz"]
        q = pool[0]
        return {"text": f"**Quick quiz · Day {n}, question {q['n']}**\n\n{q['q']}\n\nThink first, even a rough guess. Then type your answer or say **reveal**.",
                "meta": {"quiz_q": q["n"]}}

    if intent == "hint" and d:
        used = sum(1 for m in history_today if m.get("intent") == "hint")
        hints = d["hints"]
        ex = next((e for e in d["exercises"] if e["id"] == ctx.get("exercise_id")), None)
        head = f"**Hint for {ex['id']} · {ex['title']}**\n\n" if ex else "**Hint**\n\n"
        if used == 0 and ex:
            return head + "Before the hint: say in plain words what the function receives and what it must give back. " + \
                   f"Try it on a tiny example by hand.\n\n> {ex['desc'].splitlines()[0] if ex['desc'] else ''}\n\nAsk again for the next hint if you're still stuck."
        idx = min(max(used - 1, 0), max(len(hints) - 2, 0))
        h = hints[idx] if hints else "Try the smallest possible example by hand, step by step."
        tail = "\n\nStill stuck? Ask once more and I'll point you to the solution view."
        if idx >= len(hints) - 2 and used >= 3:
            tail = "\n\nThe full solution is in the **Solution** button on the Practice tab. Opening it is logged, so try one more time first."
        note = _run_note(n)
        return head + h + (f"\n\n{note}" if note else "") + tail

    if intent == "recap" and d:
        c = ", ".join(f"`{x}`" for x in d["concepts"][:6])
        if concise:
            return (f"### Day {n} recap: {d['title']}\n**Goal:** {d['goal']}\n\n**Key ideas:** {c}\n\n"
                    f"Say **quiz me** and I'll check what stuck." + _MORE)
        return (f"### Day {n} recap: {d['title']}\n**Goal:** {d['goal']}\n\n**The idea in the real world:** {d['scenario'][:420]}\n\n"
                f"**Key ideas:** {c}\n\nSay **quiz me** and I'll check what stuck.")

    if intent == "review":
        if not code.strip():
            return "I don't see any code yet. Write something in the editor (or highlight a snippet) and ask again."
        notes = static_review(code)
        failing = db.rows("SELECT check_id FROM checks WHERE day_no=? AND last_status='FAIL'", (n,)) if n else []
        out = ["### Code review\n"]
        out += [f"- {x}" for x in notes] or ["- Nothing alarming from a quick read. Naming and structure look reasonable."]
        if failing:
            out.append(f"\nStill failing: {', '.join(sorted({f['check_id'] for f in failing})[:6])}. Run the checks, then ask for a **hint** on one of them.")
        out.append("\n*(Built-in tutor does a static read. Add an AI key in ⚙ settings for line-by-line coaching.)*")
        return "\n".join(out)

    if intent == "debug":
        dec = _decode_error(question + "\n" + output)
        note = _run_note(n)
        if not dec and n and tx:                      # nothing pasted: decode the error from the learner's actual last runs
            try:
                top = (tx.learner_context(n) or {}).get("top_error")
                dec = _decode_error(top) if top and not top.startswith("compile error") else None
            except Exception:  # noqa: BLE001
                dec = None
        out = ["### Let's debug it\n"]
        if dec:
            out.append(dec + "\n")
        if note:
            out.append(note + "\n")
        if concise:
            out.append("**Next:** read the **last line** of the error, jump to the **line number** just above it, and `print()` "
                       "the values on that line to see what they really hold.")
            if concepts:
                out.append(f"\n**Common trap here ({concepts[0]['name']}):** {_first_sentence(concepts[0]['pitfall'])}")
            if not (output or code or note):
                out.append("\nPaste the full error (or run your code first) and I'll be more specific.")
            return "\n".join(out) + _MORE
        out.append("**A 4-step routine that works every time**\n1. Read the **last line** of the error: it names the type of problem.\n2. Look at the **line number** above it (and the line before if that one looks fine).\n3. `print()` the variables on that line to see what they *really* hold.\n4. Shrink the problem: test with the smallest input that still fails.")
        if concepts:
            out.append(f"\n**Common trap here ({concepts[0]['name']}):** {concepts[0]['pitfall']}")
        if not (output or code):
            out.append("\nPaste the full error (or run your code first so I can see it) and I'll be more specific.")
        return "\n".join(out)

    if not concepts:
        sc = d["scenario"][:360] if d else ""
        if concise:
            return "I'm not sure which idea you mean. Highlight the exact line or word in the lesson, or name the function or concept."
        return ("I'm not sure which idea you mean. Try highlighting the exact line or word in the lesson, or name the function/concept.\n\n"
                + (f"**Today's scenario:** {sc}\n\n" if sc else "") + GENERIC_USAGE)

    e = concepts[0]
    if concise:
        return _concise_entry(e, intent if intent in ("where_used", "explain_simple", "example", "why") else "concept")
    extra = ""
    if len(concepts) > 1 and intent in ("where_used", "concept"):
        extra = "\n\n*Related:* " + ", ".join(f"{c['name']}" for c in concepts[1:]) + ". Ask about any of them."
    if intent == "where_used":
        return _entry_where(e) + extra
    if intent == "explain_simple":
        return f"### {e['name']}, simply\n\n{e['what']}\n\n**Tiny example**\n{e['how']}\n\nDoes that click? Tell me which part still feels fuzzy and I'll try another angle." + extra
    if intent == "example":
        return f"### A realistic example: {e['name']}\n\n{e['how']}\n\n**Level it up:** {e['nxt']}\n\nWant a hint when you try it? Just say **hint**." + extra
    if intent == "why":
        return f"### Why {e['name']} works this way\n\n{e['what']}\n\n**Gotcha that reveals the mechanism:** {e['pitfall']}\n\n**See it in action**\n{e['how']}" + extra
    # plain concept question: short explanation + usage teaser
    return (f"### {e['name']}\n\n{e['what']}\n\n{e['how']}\n\n**Where it's used:** "
            f"{e['where'].splitlines()[0].lstrip('- ')}\n\nAsk **“where is this used?”** for the full real-world picture." + extra)


def offline_stream(question, quick_id, ctx, history_today) -> tuple[Iterator[str], dict]:
    res = offline_answer(question, quick_id, ctx, history_today)
    meta = {}
    if isinstance(res, dict):
        meta, res = res["meta"], res["text"]
    return _chunks(res), meta


def _chunks(res: str) -> Iterator[str]:
    import time
    words = re.split(r"(\s+)", res)
    buf = ""
    for w in words:
        buf += w
        if len(buf) >= 18:
            yield buf; buf = ""
            time.sleep(0.012)
    if buf:
        yield buf


# ---- entry point -------------------------------------------------------------------------------
def stream(question: str, quick_id: str | None, ctx: dict, history: list[dict]) -> Iterator[dict]:
    """Yields {'t':'meta'|'delta'|'note', ...}. Falls through the provider chain."""
    tx = _tx()
    style = "detailed"
    if tx:
        try:
            tx.persist_reasons(question)                              # explainable score: attach the reasons to the stored question
            gate = tx.gate_decision(question, quick_id, ctx, history)  # try-first: a hint step before an untried exercise's answer
            if gate["action"] == "gate":
                yield {"t": "meta", "provider": "offline", "model": "try-first hint", "answer_meta": gate["meta"]}
                for chunk in _chunks(gate["text"]):
                    yield {"t": "delta", "x": chunk}
                return
            style = tx.answer_style(ctx)
        except Exception:  # noqa: BLE001 - extras must never stop an answer
            pass
    if quick_id == "more":
        style = "detailed"
    st = status()
    order: list[str] = []
    if st["pref"] != "offline":
        if st["pref"] in PROVIDERS and key(st["pref"]):
            order.append(st["pref"])
        order += [p for p in available() if p not in order]
    context = build_context(ctx)
    ai_question = question
    if quick_id == "more":
        ai_question = "Go deeper on your previous answer about this: " + question
    elif quick_id == "answer_anyway" or ctx.get("gate_override"):
        context += "\n\nThe learner chose to see the full answer now. Give it, then explain it briefly."
    if order:
        context = style_block(style) + "\n\n" + context
    history_msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    for p in order:
        started = False
        try:
            yield {"t": "meta", "provider": p, "model": model(p)}
            for chunk in PROVIDERS[p](history_msgs, ai_question, context):
                started = True
                yield {"t": "delta", "x": chunk}
            return
        except Exception as e:  # noqa: BLE001 - any provider failure falls through
            msg = f"{p} unavailable ({type(e).__name__}: {str(e)[:140]})"
            if started:
                yield {"t": "delta", "x": f"\n\n*(connection to {p} dropped: {str(e)[:100]})*"}
                return
            yield {"t": "note", "x": msg}
    text_stream, meta = offline_stream(question, quick_id, ctx, [m for m in history])
    yield {"t": "meta", "provider": "offline", "model": "built-in tutor", "answer_meta": meta}
    for chunk in text_stream:
        yield {"t": "delta", "x": chunk}


def reflect_prompt(summary: dict) -> str:
    return (f"Here is analytics about a beginner's {track.T['short']} learning (JSON). Write a short, encouraging but honest reflection "
            "(max 220 words): what their question patterns say about how they think, 2 strengths, 2 specific things to try "
            "next, and one learning habit to adjust. No bullet overload.\n\n" + json.dumps(summary, ensure_ascii=False)[:6000])


def llm_reflect(summary: dict) -> tuple[str, str] | None:
    """Returns (provider, text) if an LLM is configured, else None."""
    for p in available():
        try:
            parts = []
            for c in PROVIDERS[p]([], reflect_prompt(summary), "Task: reflect on analytics, no code needed."):
                parts.append(c)
            text = "".join(parts).strip()
            if text:
                return p, text
        except Exception:
            continue
    return None
