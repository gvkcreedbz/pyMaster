"""Py Master portal: FastAPI backend.

Local-only (binds to 127.0.0.1). Tracks time, runs, questions and progress, but never locks content.
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import analytics, assistant, content, db, ext, review, runner, search, track, visual

STATIC = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init()
    ext.setup()
    content.load_days()
    runner.prepare()
    yield


app = FastAPI(title=track.T["name"], docs_url=None, redoc_url=None, lifespan=lifespan)


# ---- local-only guard: blocks DNS-rebinding and cross-site POSTs against localhost -------------
@app.middleware("http")
async def guard(request: Request, call_next):
    raw = (request.headers.get("host") or "").strip().lower()
    host = raw[: raw.index("]") + 1] if raw.startswith("[") and "]" in raw else raw.split(":")[0]   # "[::1]:8765" -> "[::1]"
    if host not in ("127.0.0.1", "localhost", "[::1]", "testserver"):
        return JSONResponse({"detail": "local access only"}, status_code=403)
    if request.method in ("POST", "PUT", "DELETE") and request.headers.get("x-portal") != "1":
        # sendBeacon can't set headers, so /api/session/end is exempt (it only closes a session)
        if request.url.path != "/api/session/end":
            return JSONResponse({"detail": "missing x-portal header"}, status_code=403)
    resp = await call_next(request)
    if request.url.path.startswith(("/static", "/api")) or request.url.path == "/":
        resp.headers["Cache-Control"] = "no-store"
    return resp


# ---- models ------------------------------------------------------------------------------------
class SessionIn(BaseModel):
    session_id: str


class HeartbeatIn(BaseModel):
    session_id: str
    day_no: int = 0
    area: str = "home"
    active: bool = True


class RunIn(BaseModel):
    kind: str = "practice"        # practice | examples | playground
    day_no: int | None = None
    code: str
    stdin: str = ""
    session_id: str | None = None


class DraftIn(BaseModel):
    kind: str
    code: str


class NoteIn(BaseModel):
    text: str


class StateIn(BaseModel):
    status: str | None = None
    confidence: int | None = None


class QuizIn(BaseModel):
    rating: int


class EventIn(BaseModel):
    session_id: str | None = None
    type: str
    day_no: int | None = None
    payload: dict = {}


class ChatIn(BaseModel):
    session_id: str | None = None
    text: str = ""
    quick_id: str | None = None
    ctx: dict = {}


class FeedbackIn(BaseModel):
    qid: int
    helpful: int


class SettingsIn(BaseModel):
    values: dict = {}
    clear: list[str] = []


def day_or_404(n: int) -> dict:
    d = content.day(n)
    if not d:
        raise HTTPException(404, "no such day")
    return d


# ---- overview / session --------------------------------------------------------------------------
@app.post("/api/session/start")
def session_start():
    sid = db.start_session()
    db.log_event(sid, "session_start", None)
    return {"session_id": sid, "welcome": analytics.welcome(sid), "today": analytics.today_stats()}


@app.post("/api/session/heartbeat")
def session_heartbeat(h: HeartbeatIn):
    return db.heartbeat(h.session_id, h.day_no, h.area[:20], h.active)


@app.post("/api/session/end")
async def session_end(request: Request):
    try:
        body = json.loads((await request.body()) or b"{}")
        if body.get("session_id"):
            db.end_session(str(body["session_id"]))
    except ValueError:
        pass
    return {"ok": True}


@app.get("/api/overview")
def overview(sid: str | None = None):
    prog = analytics.day_progress()
    start = analytics.start_date()
    days = []
    for n, d in content.load_days().items():
        days.append({**content.public_day(d), **prog[n], "planned": content.planned_date(n, start).isoformat()})
    st = analytics.streak_info()
    welcome = analytics.welcome(sid, prog, st)
    return {
        "days": days, "weeks": [{"n": w, "title": t, "sub": s, "from": a, "to": b} for w, t, s, a, b in content.WEEKS],
        "welcome": welcome, "today": analytics.today_stats(), "assistant": assistant.status(),
        "start_date": start.isoformat(), "today_date": date.today().isoformat(), "track": track.public(),
        "recommendations": analytics.recommendations(prog, {}, [], st, welcome),
    }


# ---- a day ---------------------------------------------------------------------------------------
@app.get("/api/day/{n}")
def get_day(n: int):
    d = day_or_404(n)
    db.touch_day(n)
    prog = analytics.day_progress()[n]
    drafts = {r["kind"]: r["code"] for r in db.rows("SELECT kind, code FROM drafts WHERE day_no=?", (n,))}
    note = db.one("SELECT text FROM notes WHERE day_no=?", (n,))
    quiz = {r["q_no"]: r for r in db.rows("SELECT * FROM quiz WHERE day_no=?", (n,))}
    checks = db.rows("SELECT check_id, name, passed, runs, fails, last_status FROM checks WHERE day_no=?", (n,))
    ex_status = {}
    for c in checks:
        s = ex_status.setdefault(c["check_id"], {"checks": 0, "passed": 0, "last_ok": 0, "runs": 0})
        s["checks"] += 1; s["passed"] += c["passed"]; s["last_ok"] += 1 if c["last_status"] == "PASS" else 0
        s["runs"] = max(s["runs"], c["runs"])
    return {
        "n": n, "title": d["title"], "week": d["week"], "goal": d["goal"], "level": d["level"], "minutes": d["minutes"],
        "scenario": d["scenario"], "concepts": d["concepts"], "lesson": d["lesson"], "hints": len(d["hints"]),
        "exercises": [{**e, "status": ex_status.get(e["id"])} for e in d["exercises"]],
        "quiz": [{"n": q["n"], "q": q["q"], "revealed": quiz.get(q["n"], {}).get("revealed_at") is not None,
                  "rating": quiz.get(q["n"], {}).get("rating")} for q in d["quiz"]],
        "practice_starter": d["practice"], "examples": d["examples"], "drafts": drafts,
        "notes": (note or {}).get("text", ""), "extras": d["extras"], "progress": prog,
        "planned": content.planned_date(n, analytics.start_date()).isoformat(),
        "is_project": d["is_project"],
    }


@app.get("/api/day/{n}/extra/{name}")
def get_extra(n: int, name: str):
    text = content.day_extra(n, name)
    if text is None:
        raise HTTPException(404)
    return {"name": name, "text": text}


@app.get("/api/day/{n}/hint/{i}")
def get_hint(n: int, i: int, session_id: str | None = None):
    d = day_or_404(n)
    if not 1 <= i <= len(d["hints"]):
        raise HTTPException(404)
    db.log_event(session_id, "hint_view", n, {"hint": i})
    return {"hint": d["hints"][i - 1]}


@app.get("/api/day/{n}/solution")
def get_solution(n: int, session_id: str | None = None):
    d = day_or_404(n)
    att = db.one("SELECT COUNT(*) c FROM attempts WHERE day_no=? AND kind='practice'", (n,))["c"]
    db.log_event(session_id, "solution_view", n, {"attempts_before": att})
    return {"solution": d["solution"], "attempts_before": att}


@app.post("/api/day/{n}/draft")
def save_draft(n: int, b: DraftIn):
    day_or_404(n)
    if b.kind not in ("practice", "examples"):
        raise HTTPException(400)
    db.run("INSERT INTO drafts(day_no,kind,code,updated_at) VALUES(?,?,?,?) "
           "ON CONFLICT(day_no,kind) DO UPDATE SET code=excluded.code, updated_at=excluded.updated_at",
           (n, b.kind, b.code[:200_000], db.now_iso()))
    return {"ok": True}


@app.delete("/api/day/{n}/draft/{kind}")
def reset_draft(n: int, kind: str):
    day_or_404(n)
    if kind not in ("practice", "examples"):
        raise HTTPException(400)
    db.run("DELETE FROM drafts WHERE day_no=? AND kind=?", (n, kind))
    db.log_event(None, "draft_reset", n, {"kind": kind})
    return {"ok": True}


@app.post("/api/day/{n}/notes")
def save_notes(n: int, b: NoteIn):
    day_or_404(n)
    db.run("INSERT INTO notes(day_no,text,updated_at) VALUES(?,?,?) "
           "ON CONFLICT(day_no) DO UPDATE SET text=excluded.text, updated_at=excluded.updated_at",
           (n, b.text[:50_000], db.now_iso()))
    return {"ok": True}


@app.post("/api/day/{n}/state")
def day_state(n: int, b: StateIn):
    day_or_404(n)
    db.set_day_state(n, b.status, b.confidence)
    if b.status:
        db.log_event(None, "day_" + b.status, n)
    return {"ok": True, "progress": analytics.day_progress()[n]}


@app.get("/api/day/{n}/quiz/{q}/answer")
def quiz_answer(n: int, q: int, session_id: str | None = None, quiet: int = 0):
    d = day_or_404(n)
    item = next((x for x in d["quiz"] if x["n"] == q), None)
    if not item:
        raise HTTPException(404)
    if not quiet:      # quiet=1 re-shows an answer that was already revealed (no new event)
        db.run("INSERT INTO quiz(day_no,q_no,revealed_at) VALUES(?,?,?) "
               "ON CONFLICT(day_no,q_no) DO UPDATE SET revealed_at=COALESCE(revealed_at, excluded.revealed_at)",
               (n, q, db.now_iso()))
        db.log_event(session_id, "quiz_reveal", n, {"q": q})
    return {"answer": item["a"]}


@app.post("/api/day/{n}/quiz/{q}")
def quiz_rate(n: int, q: int, b: QuizIn):
    d = day_or_404(n)
    if b.rating not in (0, 1, 2) or not any(x["n"] == q for x in d["quiz"]):
        raise HTTPException(400, "bad rating or unknown question")
    db.run("INSERT INTO quiz(day_no,q_no,rating,rated_at) VALUES(?,?,?,?) "
           "ON CONFLICT(day_no,q_no) DO UPDATE SET rating=excluded.rating, rated_at=excluded.rated_at",
           (n, q, b.rating, db.now_iso()))
    return {"ok": True, "progress": analytics.day_progress()[n]}


# ---- run code --------------------------------------------------------------------------------------
@app.post("/api/run")
def run_code(b: RunIn):
    if len(b.code) > 200_000:
        raise HTTPException(413, "code too large")
    if b.kind == "practice" and b.day_no:
        day_or_404(b.day_no)
        res = runner.run_practice(b.day_no, b.code, b.stdin)
        db.run("INSERT INTO drafts(day_no,kind,code,updated_at) VALUES(?,?,?,?) "
               "ON CONFLICT(day_no,kind) DO UPDATE SET code=excluded.code, updated_at=excluded.updated_at",
               (b.day_no, "practice", b.code, db.now_iso()))
        res["progress"] = analytics.day_progress()[b.day_no]
    elif b.kind == "examples" and b.day_no:
        day_or_404(b.day_no)
        res = runner.run_examples(b.day_no, b.code, b.stdin)
    elif b.kind == "playground":
        res = runner.run_playground(b.code, b.stdin)
    else:
        raise HTTPException(400, "bad kind")
    return res


# ---- visual explanations -------------------------------------------------------------------------------
class VisualIn(BaseModel):
    code: str
    lang: str | None = None
    stdin: str = ""
    session_id: str | None = None
    day_no: int | None = None


@app.post("/api/visual/trace")
def visual_trace(b: VisualIn):
    if len(b.code) > 50_000:
        raise HTTPException(413, "code too large")
    db.log_event(b.session_id, "visual_trace", b.day_no, {"chars": len(b.code)})
    return visual.trace(b.code, b.stdin)


@app.post("/api/visual/diagram")
def visual_diagram(b: VisualIn):
    if len(b.code) > 50_000:
        raise HTTPException(413, "code too large")
    db.log_event(b.session_id, "visual_diagram", b.day_no, {"lang": b.lang})
    try:
        return visual.diagram(b.code, b.lang)
    except ValueError as e:
        raise HTTPException(400, str(e)) from None


# ---- search, review queue, blueprints --------------------------------------------------------------------
@app.get("/api/search")
def search_all(q: str = "", limit: int = 12):
    return {"q": q[:100], "items": search.search(q[:100], max(1, min(limit, 30)))}


@app.get("/api/review")
def review_queue(all: int = 0):
    return review.queue(include_not_due=bool(all))


@app.get("/api/blueprints")
def blueprints():
    return {"items": content.blueprint_list()}


@app.get("/api/blueprints/{bid}")
def blueprint_get(bid: str, session_id: str | None = None):
    text = content.blueprint_doc(bid)
    if text is None:
        raise HTTPException(404, "no such blueprint")
    db.log_event(session_id, "blueprint_view", None, {"id": bid})
    meta = next(b for b in content.blueprint_list() if b["id"] == bid)
    return {"meta": meta, "text": text}


@app.get("/api/blueprints/{bid}/file/{name}")
def blueprint_source(bid: str, name: str):
    text = content.blueprint_file(bid, name)
    if text is None:
        raise HTTPException(404)
    return {"name": name, "text": text}


class BlueprintRunIn(BaseModel):
    session_id: str | None = None


@app.post("/api/blueprints/{bid}/run")
def blueprint_run(bid: str, b: BlueprintRunIn | None = None):
    res = runner.run_blueprint_demo(bid)
    if res is None:
        raise HTTPException(404, "no demo for this blueprint")
    db.log_event(b.session_id if b else None, "blueprint_run", None, {"id": bid, "ok": res["ok"], "ms": res["ms"]})
    return res


# ---- tutor chat --------------------------------------------------------------------------------------
def _history(day_no: int | None, limit: int = 8) -> list[dict]:
    qs = db.rows("SELECT text, answer, meta FROM questions WHERE day_no IS ? AND answer IS NOT NULL AND date>=? "
                 "ORDER BY id DESC LIMIT ?", (day_no, (date.today() - timedelta(days=1)).isoformat(), limit))
    out = []
    for q in reversed(qs):
        meta = json.loads(q["meta"] or "{}")
        out.append({"role": "user", "content": q["text"], "intent": meta.get("intent"), "meta": {}})
        out.append({"role": "assistant", "content": q["answer"], "intent": meta.get("intent"), "meta": meta})
    return out


@app.post("/api/chat")
def chat(b: ChatIn):
    ctx = b.ctx or {}
    try:                                   # the browser sends an int, but never trust the client
        day_no = int(ctx.get("day_no") or 0) or None
    except (TypeError, ValueError):
        day_no = None
    if day_no and not content.day(day_no):
        day_no = None
    ctx["day_no"] = day_no
    quick = b.quick_id if b.quick_id in assistant.QUICK else None
    text = (assistant.QUICK[quick] if quick and not b.text.strip() else b.text).strip()
    if not text:
        raise HTTPException(400, "empty question")
    text = text[:4000]
    has_code = bool((ctx.get("code") or "").strip())
    has_sel = bool((ctx.get("selection") or "").strip())
    attempted = False
    if day_no:
        cutoff = (datetime.now() - timedelta(minutes=60)).isoformat(timespec="seconds")
        attempted = db.one("SELECT COUNT(*) c FROM attempts WHERE day_no=? AND ts>=? AND kind IN ('practice','examples')",
                           (day_no, cutoff))["c"] > 0
    prior = [r["text"] for r in db.rows("SELECT text FROM questions WHERE source!='quick' AND date>=? ORDER BY id DESC LIMIT 60",
                                        ((date.today() - timedelta(days=7)).isoformat(),))]
    a = analytics.score_question(text, day_no=day_no, has_code=has_code, has_selection=has_sel,
                                 attempted_first=attempted, prior=prior, source="quick" if quick else "typed")
    history = _history(day_no)
    intent = assistant.detect_intent(text, quick)
    qid = db.run(
        "INSERT INTO questions(ts,date,session_id,day_no,tab,source,text,selection,has_code,attempted_first,quality,qtype,"
        "bloom,valid,duplicate,flags,tips,meta) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (db.now_iso(), db.today(), b.session_id, day_no, ctx.get("tab"), "quick" if quick else "typed", text,
         (ctx.get("selection") or "")[:1500], int(has_code or has_sel), int(attempted), a["quality"], a["qtype"],
         a["bloom"], a["valid"], a["duplicate"], json.dumps(a["flags"]), json.dumps(a["tips"]),
         json.dumps({"intent": intent})))

    def gen():
        answer, provider, meta_extra = [], "offline", {}
        yield json.dumps({"t": "q", "qid": qid, "analysis": a, "intent": intent}) + "\n"
        try:
            for ev in assistant.stream(text, quick, ctx, history):
                if ev["t"] == "meta":
                    provider = ev["provider"]
                    meta_extra = ev.get("answer_meta") or meta_extra
                elif ev["t"] == "delta":
                    answer.append(ev["x"])
                yield json.dumps(ev, ensure_ascii=False) + "\n"
            yield json.dumps({"t": "done"}) + "\n"
        except Exception as e:  # noqa: BLE001
            yield json.dumps({"t": "error", "x": f"{type(e).__name__}: {e}"}) + "\n"
        finally:
            full = "".join(answer)
            db.run("UPDATE questions SET answer=?, provider=?, meta=? WHERE id=?",
                   (full, provider, json.dumps({"intent": intent, **meta_extra}), qid))

    return StreamingResponse(gen(), media_type="application/x-ndjson")


@app.post("/api/chat/feedback")
def chat_feedback(b: FeedbackIn):
    db.run("UPDATE questions SET helpful=? WHERE id=?", (1 if b.helpful > 0 else -1, b.qid))
    return {"ok": True}


@app.get("/api/chat/history")
def chat_history(day: int | None = None, limit: int = 40):
    rows = db.rows("SELECT id, ts, text, answer, provider, quality, valid, qtype, bloom, flags, tips, helpful, source "
                   "FROM questions WHERE day_no IS ? ORDER BY id DESC LIMIT ?", (day or None, max(1, min(limit, 200))))
    for r in rows:
        r["flags"] = json.loads(r["flags"] or "[]")
        r["tips"] = json.loads(r["tips"] or "[]")
    return {"items": list(reversed(rows))}


@app.get("/api/chat/quick")
def chat_quick():
    return {"quick": assistant.QUICK}


# ---- events --------------------------------------------------------------------------------------------
@app.post("/api/event")
def event(e: EventIn):
    if len(e.type) > 40:
        raise HTTPException(400)
    db.log_event(e.session_id, e.type, e.day_no, e.payload)
    return {"ok": True}


# ---- insights --------------------------------------------------------------------------------------------
@app.get("/api/insights")
def get_insights():
    return analytics.insights()


@app.get("/api/questions")
def question_log(limit: int = 200):
    rows = db.rows("SELECT id, ts, day_no, tab, source, text, quality, qtype, bloom, valid, duplicate, attempted_first, "
                   "flags, tips, provider, helpful FROM questions ORDER BY id DESC LIMIT ?", (max(1, min(limit, 1000)),))
    for r in rows:
        r["flags"] = json.loads(r["flags"] or "[]")
        r["tips"] = json.loads(r["tips"] or "[]")
    return {"items": rows}


@app.post("/api/insights/reflect")
def reflect():
    ins = analytics.insights()
    summary = {k: ins[k] for k in ("totals", "streak", "pace", "types", "bloom", "attempt_first_pct", "weak")} | {
        "profile": ins["profile"]}
    got = assistant.llm_reflect(summary)
    if got:
        provider, text = got
    else:
        provider = "rules"
        p = ins["profile"]
        lines = [f"**{p['label']}.** " + (" ".join(p["notes"]))]
        lines.append("\n**Next steps**")
        lines += [f"- {r['text']}" for r in ins["recommendations"][:3]]
        lines.append(f"\n*Pace:* {ins['pace']['note']}")
        text = "\n".join(lines)
    db.run("INSERT INTO reflections(ts,provider,text) VALUES(?,?,?)", (db.now_iso(), provider, text))
    return {"provider": provider, "text": text}


# ---- settings / library / export -----------------------------------------------------------------------
@app.get("/api/settings")
def get_settings():
    return {**assistant.status(), "start_date": analytics.start_date().isoformat()}


@app.post("/api/settings")
def set_settings(b: SettingsIn):
    allowed = {"key_cursor", "key_anthropic", "key_openai", "provider_pref", "model_cursor", "model_anthropic",
               "model_openai", "start_date"}
    for k, v in b.values.items():
        if k not in allowed:
            continue
        v = str(v).strip()
        if k == "start_date":
            try:
                date.fromisoformat(v)
            except ValueError:
                raise HTTPException(400, "start_date must be YYYY-MM-DD") from None
        if k.startswith("key_") and not v:
            continue       # blank means 'unchanged'; use clear[] to remove
        db.set_setting(k, v)
    for k in b.clear:
        if k in allowed:
            db.set_setting(k, None)
    return get_settings()


@app.get("/api/library")
def get_library():
    return {"items": content.library()}


@app.get("/api/library/doc")
def get_library_doc(id: str):
    text = content.library_doc(id)
    if text is None:
        raise HTTPException(404)
    return {"id": id, "text": text}


@app.get("/api/export")
def export():
    body = json.dumps(db.export_all(), indent=2, ensure_ascii=False)
    return Response(body, media_type="application/json",
                    headers={"Content-Disposition": 'attachment; filename="python-journey-progress.json"'})


# ---- static ----------------------------------------------------------------------------------------------
@app.get("/")
def index():
    """index.html with the track (Python/Java) baked in: title, editor mode script, and window.TRACK for the JS."""
    page = (STATIC / "index.html").read_text(encoding="utf-8")
    t = track.public()
    page = (page.replace("<title>Py Master</title>", f"<title>{t['name']}</title>")
            .replace("/static/vendor/python.js", f"/static/vendor/{t['cm_file']}")
            .replace("<!--TRACK-->", f"<script>window.TRACK={json.dumps(t)};</script>"))
    return Response(page, media_type="text/html")


@app.get("/api/track")
def track_info():
    return track.public()


@app.get("/api/extras")
def extras():
    """Front-end extension modules (static/js/extras/*.js) that app.js should load."""
    return {"js": ext.js_files(), "css": ext.css_files()}


ext.mount(app)
app.mount("/static", StaticFiles(directory=STATIC), name="static")
