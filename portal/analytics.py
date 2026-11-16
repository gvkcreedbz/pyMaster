"""Question-quality scoring, thinking profile, pace and welcome-back logic.

All heuristics are transparent and local. They never block anything; they only coach.
"""
from __future__ import annotations

import re
from collections import Counter, OrderedDict, defaultdict
from datetime import date, timedelta

from . import content, db

# ---- question analysis -------------------------------------------------------------------------
REASONING = re.compile(
    r"\b(why|how come|what if|difference|differ|compare|versus|vs\.?|instead of|trade-?off|"
    r"real[- ]world|in production|used in|use case|best practice|edge case|alternative|"
    r"when (?:would|should|do)|where (?:is|are|do|does|would)|how (?:is|are|do|does|would))\b", re.I)
OWN_THINKING = re.compile(
    r"\b(i think|i thought|i understood|i understand|my understanding|i tried|i expected|i guess|"
    r"so (?:that )?means|does that mean|is it because|because i|i assumed|i got it|makes sense)\b", re.I)
VAGUE = re.compile(r"^\s*(help( me)?|explain( this| it)?|idk|\?+|what|how|why|doesn'?t work|not working|"
                   r"fix( it| this)?|answer|solve( it| this)?|tell me)\W*$", re.I)
GIVE_ANSWER = re.compile(r"\b(give me the (?:answer|solution|code)|just (?:give|show) me the (?:answer|solution))\b", re.I)

TYPE_RULES = [
    ("debug", re.compile(r"\b(error|traceback|exception|bug|crash|fails?|failing|failed|not working|doesn'?t work|"
                         r"wrong output|unexpected|stuck|keyerror|typeerror|valueerror|indexerror|nameerror|"
                         r"syntaxerror|attributeerror|indentationerror)\b", re.I)),
    ("usage", re.compile(r"\b(real[- ]world|real life|where (?:is|are|do|does|would|will)\b.*\b(?:use|used)|"
                         r"how (?:is|are|do|does|will)\b.*\b(?:use|used)|use ?case|in production|"
                         r"companies|industry|at work|practical|in practice|where.*use)\b", re.I)),
    ("compare", re.compile(r"\b(difference|differ|compare|versus|vs\.?|better than|or should i|instead of)\b", re.I)),
    ("review", re.compile(r"\b(review|feedback|improve|clean(er)?|refactor|optimi[sz]e|my code|is this good)\b", re.I)),
    ("confirm", re.compile(r"\b(is (?:this|that|it) (?:right|correct|ok)|am i right|right\?|correct\?|"
                           r"did i (?:get|do)|is my)\b", re.I)),
    ("extend", re.compile(r"\b(what if|edge case|harder|challenge|next level|more advanced|go further|extend)\b", re.I)),
    ("howto", re.compile(r"\b(how (?:do|can|to|would) (?:i|you|we)|how to|write a|make a|build a|create a)\b", re.I)),
    ("concept", re.compile(r"\b(what is|what'?s|what are|explain|meaning|mean|why|define|understand)\b", re.I)),
]
BLOOM_RULES = [
    ("create", re.compile(r"\b(design|build my own|create my own|invent|combine|my own project)\b", re.I)),
    ("evaluate", re.compile(r"\b(better|best|should i|pros and cons|trade-?off|worth|prefer|good practice|"
                            r"best practice)\b", re.I)),
    ("analyze", re.compile(r"\b(difference|compare|versus|vs\.?|why does|why do|why not|what happens (?:if|when)|"
                           r"what if|break down|instead of)\b", re.I)),
    ("apply", re.compile(r"\b(how (?:do|can|to) i|how would i|use (?:this|it) (?:to|for)|write|implement|"
                         r"where (?:is|are|do) .* used|real[- ]world|apply)\b", re.I)),
    ("understand", re.compile(r"\b(explain|why|how does|how do|what does .* mean|meaning|intuition|simply)\b", re.I)),
    ("remember", re.compile(r"\b(what is|what'?s|what are|define|syntax|which)\b", re.I)),
]
BLOOM_ORDER = ["remember", "understand", "apply", "analyze", "evaluate", "create"]


def _tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z_][a-z0-9_]{2,}", s.lower())} - {
        "the", "and", "for", "that", "this", "with", "what", "how", "why", "does", "are", "you", "can", "not",
        "have", "from", "when", "where", "which", "its", "your", "about", "would", "will", "please", "tell"}


def classify_type(text: str) -> str:
    for name, rx in TYPE_RULES:
        if rx.search(text):
            return name
    return "other"


def classify_bloom(text: str) -> str:
    for name, rx in BLOOM_RULES:
        if rx.search(text):
            return name
    return "understand"


_STASH: "OrderedDict[str, list]" = OrderedDict()      # question text -> reasons, picked up by ex_tutor when the answer starts
_STASH_MAX = 64


def pop_reasons(text: str) -> list | None:
    """Reasons computed for this exact question text by the last score_question() call (or None)."""
    return _STASH.pop((text or "").strip(), None)


def score_question(text: str, *, day_no: int | None, has_code: bool, has_selection: bool,
                   attempted_first: bool, prior: list[str], source: str = "typed", remember: bool = True) -> dict:
    """Score 0-100. 'valid' = specific, thoughtful and not a repeat.

    Also returns ``reasons``: a list of {points, text} explaining where the score came from (the points add up to
    the score before it is clamped to 0-100). ``remember=False`` (live coach) keeps them out of the stash."""
    t = (text or "").strip()
    words = len(re.findall(r"\w+", t))
    qtype, bloom = classify_type(t), classify_bloom(t)
    flags: list[str] = []
    tips: list[str] = []
    reasons: list[dict] = []

    def why(points: int, msg: str) -> None:
        reasons.append({"points": points, "text": msg})

    if source == "quick":      # one-click prompts: tracked, but not graded (they are not your wording)
        return {"quality": None, "qtype": qtype, "bloom": bloom, "valid": 1, "duplicate": 0, "flags": ["quick-action"],
                "tips": [], "reasons": [{"points": 0, "text": "A quick-action button, so it is logged but not graded."}]}

    score = 30
    why(30, "Every typed question starts at 30.")
    if words < 3:
        score -= 20; flags.append("too-short"); why(-20, "Very short (under 3 words); a few more words help.")
    elif words < 6:
        score -= 5; why(-5, "Quite short (under 6 words).")
    elif words <= 45:
        score += 10; why(10, "A good length: enough detail without rambling.")
    else:
        score += 4; flags.append("long"); why(4, "Long and detailed (consider splitting it into two questions).")
    r_hits = len(set(m.group(0).lower() for m in REASONING.finditer(t)))
    if r_hits:
        pts = min(15, r_hits * 8)
        score += pts; why(pts, "Uses reasoning words (why, difference, what if, where is it used).")

    concept_terms = set()
    if day_no and (d := content.day(day_no)):
        concept_terms = {w for c in d["concepts"] for w in _tokens(c)}
    names_code = bool(re.search(r"`[^`]+`|\b\w+\(\)|\b[a-z_]+\.[a-z_]+\b", t))
    names_concept = bool(_tokens(t) & concept_terms)
    if names_code or names_concept:
        score += 15; flags.append("specific"); why(15, "Names the exact thing you mean (a function, a line or today's concept).")
    else:
        tips.append("Name the exact thing you mean (a function, a line, or a concept from today's lesson).")
    if has_code or has_selection:
        score += 10; why(10, "Includes your code or a highlighted selection.")
    if OWN_THINKING.search(t):
        score += 15; flags.append("shows-own-thinking"); why(15, "Shows your own thinking (\"I think\", \"I expected\").")
    else:
        tips.append("Add what you already think (\"I think X because…\") so I can correct your model, not just give an answer.")
    if attempted_first:
        score += 10; flags.append("tried-first"); why(10, "You ran your code recently before asking.")
    elif qtype in ("debug", "howto", "review", "confirm") and not has_code:
        tips.append("Try it first and paste your code or the error. Questions asked after an attempt teach you far more.")
    if qtype == "debug":
        if re.search(r"(Error|Traceback)", t) or has_code:
            score += 10; why(10, "A debugging question that includes the error or your code.")
        else:
            score -= 10; flags.append("no-error-text"); why(-10, "A debugging question without the error text or your code.")
            tips.append("Paste the full error message; the last line usually names the bug.")
    if VAGUE.match(t):
        score -= 25; flags.append("vague"); why(-25, "Too general to answer well (for example just \"help\").")
    if GIVE_ANSWER.search(t):
        score -= 15; flags.append("asks-for-answer"); why(-15, "Asks for the answer instead of a hint.")
        tips.append("Ask for a hint instead of the answer. You will remember what you work out yourself.")
    if qtype == "usage":
        flags.append("real-world")

    duplicate = 0
    toks = _tokens(t)
    for p in prior:
        pt = _tokens(p)
        if toks and pt and len(toks & pt) / len(toks | pt) >= 0.75:
            duplicate = 1; flags.append("repeat")
            tips.append("You asked something very similar recently. Check your notes or scroll the chat history first.")
            score -= 30; why(-30, "Very similar to a question you asked in the last week.")
            break
    score = max(0, min(100, score))
    valid = int(score >= 45 and "vague" not in flags and not duplicate)
    if remember and t:
        _STASH[t] = reasons
        while len(_STASH) > _STASH_MAX:
            _STASH.popitem(last=False)
    return {"quality": score, "qtype": qtype, "bloom": bloom, "valid": valid, "duplicate": duplicate,
            "flags": flags, "tips": tips[:2], "reasons": reasons}


def quality_label(score: int | None) -> str:
    if score is None:
        return "quick action"
    return "great question" if score >= 70 else "good question" if score >= 45 else "could be sharper"


def reasons_from_flags(row: dict) -> list[dict]:
    """Best-effort reasons for questions stored before reasons were persisted (built from the stored flags)."""
    if row.get("quality") is None:
        return [{"points": 0, "text": "A quick-action button, so it is logged but not graded."}]
    fl = set(json_list(row.get("flags")))
    table = [("specific", 15, "Names the exact thing you mean."), ("shows-own-thinking", 15, "Shows your own thinking."),
             ("tried-first", 10, "You ran your code recently before asking."), ("real-world", 0, "Asks about real-world use."),
             ("too-short", -20, "Very short (under 3 words)."), ("vague", -25, "Too general to answer well."),
             ("asks-for-answer", -15, "Asks for the answer instead of a hint."), ("no-error-text", -10, "No error text or code included."),
             ("repeat", -30, "Very similar to a recent question."), ("long", 4, "Long and detailed.")]
    out = [{"points": p, "text": m} for k, p, m in table if k in fl]
    out.append({"points": 0, "text": f"Final score {row['quality']} (older question: shown from its saved flags)."})
    return out


def json_list(v) -> list:
    import json
    try:
        r = json.loads(v) if isinstance(v, str) else (v or [])
        return r if isinstance(r, list) else []
    except ValueError:
        return []


def coach_tips(text: str, res: dict, *, has_code: bool, has_selection: bool) -> list[str]:
    """Gentle, rule-based nudges for the live coach (at most 2). Empty once the question is already good."""
    t = (text or "").strip()
    if not t or (res.get("quality") or 0) >= 70:
        return []
    fl, qtype = set(res.get("flags") or []), res.get("qtype")
    out: list[str] = []
    if qtype in ("debug", "howto", "review", "confirm") and not (has_code or has_selection):
        out.append("Add the code you tried (tick \"include my code\" or paste it).")
    if qtype == "debug" and "no-error-text" in fl:
        out.append("Paste the error message; its last line usually names the problem.")
    if qtype == "debug" and "shows-own-thinking" not in fl:
        out.append("Say what you expected to happen and what happened instead.")
    if "vague" in fl or "too-short" in fl:
        out.append("Add a few more words: what are you trying to do, and where are you stuck?")
    if "specific" not in fl:
        out.append("Name the exact function, line or idea you mean.")
    if "shows-own-thinking" not in fl:
        out.append("Add what you think the answer is, and why. I can then fix the part that is off.")
    if "asks-for-answer" in fl:
        out.append("A hint first helps you remember it longer. You can always ask for more.")
    if "repeat" in fl:
        out.append("You asked something very similar recently; scroll the chat above first.")
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x); uniq.append(x)
    return uniq[:2]


# ---- manual overrides (the learner can mark a question 'valid' or 'low') ---------------------------------------
def overrides() -> dict[int, str]:
    """question id -> 'valid' | 'low'. Table is created by ex_tutor.setup(); absent table means no overrides."""
    try:
        return {r["question_id"]: r["override"] for r in
                db.rows("SELECT question_id, override FROM question_reasons WHERE override IN ('valid','low')")}
    except Exception:  # noqa: BLE001
        return {}


def apply_override(q: dict, verdict: str | None) -> dict:
    """Return q with the learner's verdict applied (valid -> valid & quality >= 45; low -> not valid & quality <= 44)."""
    q["override"] = verdict
    if verdict and q.get("quality") is not None:
        if verdict == "valid":
            q["valid"], q["quality"] = 1, max(q["quality"], 45)
        else:
            q["valid"], q["quality"] = 0, min(q["quality"], 44)
    return q


# ---- progress model ----------------------------------------------------------------------------
def start_date() -> date:
    s = db.get_setting("start_date")
    try:
        return date.fromisoformat(s) if s else content.DEFAULT_START
    except ValueError:
        return content.DEFAULT_START


def day_progress() -> dict[int, dict]:
    """Per-day progress: checks, quiz, time, questions. Pure information, nothing is locked."""
    days = content.load_days()
    checks = defaultdict(lambda: [0, 0])
    for r in db.rows("SELECT day_no, check_id, name, passed FROM checks"):
        checks[r["day_no"]][1] += 1
        checks[r["day_no"]][0] += r["passed"]
    quiz = defaultdict(lambda: [0, 0])  # rated, got-it
    for r in db.rows("SELECT day_no, rating FROM quiz WHERE rating IS NOT NULL"):
        quiz[r["day_no"]][0] += 1
        quiz[r["day_no"]][1] += 1 if r["rating"] == 2 else 0
    secs = defaultdict(float)
    for r in db.rows("SELECT day_no, SUM(seconds) s FROM activity GROUP BY day_no"):
        secs[r["day_no"]] = r["s"] or 0
    qcount = Counter({r["day_no"]: r["c"] for r in db.rows("SELECT day_no, COUNT(*) c FROM questions GROUP BY day_no")})
    state = {r["day_no"]: r for r in db.rows("SELECT * FROM day_state")}
    out = {}
    fully_passed = defaultdict(set)              # day -> check_ids whose every check passed (one query, not one per day)
    for r in db.rows("SELECT day_no, check_id, SUM(passed) p, COUNT(*) c FROM checks GROUP BY day_no, check_id"):
        if r["c"] > 0 and r["p"] == r["c"]:
            fully_passed[r["day_no"]].add(r["check_id"])
    for n, d in days.items():
        # distinct checks per day are derived from what has actually been run; use declared exercise count as the base
        total_ex = max(len(d["exercises"]), 1)
        ex_ids = {e["id"] for e in d["exercises"]}
        passed_ids = fully_passed[n] & ex_ids
        quiz_total = len(d["quiz"]) or 1
        st = state.get(n, {})
        ex_pct = len(passed_ids) / total_ex
        qz_pct = quiz[n][0] / quiz_total
        started = bool(st) or secs[n] > 0
        status = st.get("status", "open") if st else "open"
        pct = round(100 * (0.7 * ex_pct + 0.3 * qz_pct)) if started else 0
        if status == "done":
            pct = 100
        out[n] = {
            "n": n, "status": status, "started": started, "pct": pct,
            "ex_passed": len(passed_ids), "ex_total": len(d["exercises"]),
            "quiz_rated": quiz[n][0], "quiz_total": len(d["quiz"]), "quiz_got": quiz[n][1],
            "minutes": round(secs[n] / 60, 1), "questions": qcount[n],
            "confidence": st.get("confidence"), "last_opened": st.get("last_opened_at"),
            "completed_at": st.get("completed_at"),
        }
    return out


def current_day(prog: dict[int, dict]) -> int:
    """First day that isn't done, but prefer the most recently opened unfinished one."""
    unfinished = [n for n, p in prog.items() if p["status"] != "done"]
    if not unfinished:
        return 30
    opened = [(prog[n]["last_opened"], n) for n in unfinished if prog[n]["last_opened"]]
    if opened:
        return max(opened)[1]
    return min(unfinished)


def streak_info() -> dict:
    ds = sorted({r["date"] for r in db.rows("SELECT date FROM activity WHERE seconds>=60 GROUP BY date")})
    dates = {date.fromisoformat(x) for x in ds}
    t = date.today()
    cur = 0
    d = t if t in dates else t - timedelta(days=1)
    while d in dates:
        cur += 1; d -= timedelta(days=1)
    best = run = 0
    prev = None
    for x in sorted(dates):
        run = run + 1 if prev and (x - prev).days == 1 else 1
        best = max(best, run); prev = x
    return {"current": cur, "best": best, "active_days": len(dates), "last_active": ds[-1] if ds else None}


def welcome(sid: str | None = None, prog: dict | None = None, st: dict | None = None) -> dict:
    """Welcome-back logic. 'Last visit' = the latest *previous* session with real activity."""
    prog = prog if prog is not None else day_progress()
    cur = current_day(prog)
    st = st if st is not None else streak_info()
    t = date.today()
    if sid:
        prev = db.one("SELECT MAX(date) d FROM sessions WHERE active_seconds>=15 AND id!=?", (sid,))
    else:
        prev = db.one("SELECT MAX(date) d FROM sessions WHERE active_seconds>=15")
    last = date.fromisoformat(prev["d"]) if prev and prev["d"] else None
    gap = (t - last).days if last else None
    plan = content.plan_day_for(t, start_date())
    d = content.day(cur)
    last_q = db.one("SELECT text FROM questions WHERE day_no=? ORDER BY id DESC LIMIT 1", (cur,))
    if last is None:
        kind, text = "start", "Welcome. Your first step is Day 1. Take it at your own speed; nothing here ever locks."
    elif gap >= 2:
        kind = "recap"
        text = (f"Welcome back. It's been {gap} days. No problem; pace here is yours. "
                f"You were on Day {cur}: {d['title']}. Let's do a 2-minute recap before moving on.")
    elif gap == 1:
        kind, text = "resume", f"Good to see you again. Pick up Day {cur}: {d['title']}."
    else:
        kind, text = "continue", f"You're on a roll today. Keep going with Day {cur}: {d['title']}."
    recap = []
    if kind == "recap":
        recap = [f"Key ideas from Day {cur}: " + ", ".join(d["concepts"][:4])]
        if last_q:
            recap.append(f"Last thing you asked: “{last_q['text'][:140]}”")
        p = prog[cur]
        recap.append(f"Practice so far: {p['ex_passed']}/{p['ex_total']} exercises passed; quiz {p['quiz_rated']}/{p['quiz_total']} rated.")
    return {"kind": kind, "text": text, "gap_days": gap, "current_day": cur, "plan_day": plan,
            "delta": cur - plan, "recap": recap, "streak": st}


def today_stats() -> dict:
    t = db.today()
    secs = db.one("SELECT COALESCE(SUM(seconds),0) s FROM activity WHERE date=?", (t,))["s"]
    typed_today = db.rows("SELECT id, valid FROM questions WHERE date=? AND source!='quick'", (t,))
    ov = overrides()
    q = {"c": len(typed_today),
         "v": sum(1 if ov.get(r["id"]) == "valid" else 0 if ov.get(r["id"]) == "low" else (r["valid"] or 0) for r in typed_today)}
    qa = db.one("SELECT COUNT(*) c FROM questions WHERE date=?", (t,))["c"]
    a = db.one("SELECT COUNT(*) c, COALESCE(SUM(passed),0) p FROM attempts WHERE date=?", (t,))
    return {"minutes": round(secs / 60, 1), "questions": qa, "typed_questions": q["c"], "valid_questions": q["v"],
            "runs": a["c"]}


# ---- insights ----------------------------------------------------------------------------------
def insights() -> dict:
    prog = day_progress()
    st = streak_info()
    qs = db.rows("SELECT * FROM questions ORDER BY id")
    ov = overrides()
    for q in qs:                                   # the learner's own 'valid' / 'low' verdicts win over the heuristic
        if q["id"] in ov:
            apply_override(q, ov[q["id"]])
    typed = [q for q in qs if q["source"] != "quick" and q["quality"] is not None]
    # time series (last 35 calendar days)
    t = date.today()
    by_date = {r["date"]: r["s"] for r in db.rows("SELECT date, SUM(seconds) s FROM activity GROUP BY date")}
    q_by_date = Counter(q["date"] for q in qs)
    series = []
    for i in range(34, -1, -1):
        d = (t - timedelta(days=i)).isoformat()
        series.append({"date": d, "minutes": round(by_date.get(d, 0) / 60, 1), "questions": q_by_date.get(d, 0)})
    total_min = round(sum(by_date.values()) / 60, 1)
    # question stats
    n_typed = len(typed)
    valid_n = sum(1 for q in typed if q["valid"])
    types = Counter(q["qtype"] for q in qs)
    bloom = Counter(q["bloom"] for q in qs)
    attempt_first = sum(1 for q in typed if q["attempted_first"])
    dup = sum(1 for q in typed if q["duplicate"])
    avg_q = round(sum(q["quality"] for q in typed) / n_typed) if typed else None
    qtrend = [{"id": q["id"], "quality": q["quality"], "date": q["date"]} for q in typed[-30:]]
    # per-day
    per_day = []
    for n, p in prog.items():
        per_day.append({**p, "title": content.day(n)["title"]})
    # attempts
    att = db.rows("SELECT * FROM attempts WHERE kind='practice'")
    runs = len(att)
    first_try = sum(1 for a in att if a["total"] and a["passed"] == a["total"])
    hours = total_min / 60 or 1
    sol_views = db.one("SELECT COUNT(*) c FROM events WHERE type='solution_view'")["c"]
    hint_views = db.one("SELECT COUNT(*) c FROM events WHERE type='hint_view'")["c"]
    done_days = sum(1 for p in prog.values() if p["status"] == "done")
    ex_passed = sum(p["ex_passed"] for p in prog.values())
    ex_total = sum(p["ex_total"] for p in prog.values())
    # weak spots: days where many questions + low pass ratio, or low quiz
    weak = []
    for n, p in prog.items():
        if not p["started"]:
            continue
        reasons = []
        if p["ex_total"] and p["ex_passed"] < p["ex_total"] and p["minutes"] >= 20:
            reasons.append(f"{p['ex_passed']}/{p['ex_total']} exercises passed after {p['minutes']:.0f} min")
        if p["quiz_rated"] and p["quiz_got"] / p["quiz_rated"] < 0.6:
            reasons.append(f"quiz: only {p['quiz_got']}/{p['quiz_rated']} 'got it'")
        if p["questions"] >= 6 and p["ex_passed"] < p["ex_total"]:
            reasons.append(f"{p['questions']} questions asked, still open")
        failing = db.rows("SELECT DISTINCT check_id FROM checks WHERE day_no=? AND last_status='FAIL' ORDER BY check_id LIMIT 3", (n,))
        if failing and p["status"] != "done":
            reasons.append("failing: " + ", ".join(f["check_id"] for f in failing))
        if reasons:
            weak.append({"day": n, "title": content.day(n)["title"], "reasons": reasons})
    profile = thinking_profile(typed, qs, types, bloom, attempt_first, dup, sol_views)
    # simple pace summary (information only)
    cur = current_day(prog)
    plan = content.plan_day_for(t, start_date())
    return {
        "totals": {"minutes": total_min, "hours": round(total_min / 60, 1), "active_days": st["active_days"],
                   "questions": len(qs), "typed_questions": n_typed, "valid_questions": valid_n,
                   "valid_pct": round(100 * valid_n / n_typed) if n_typed else None, "avg_quality": avg_q,
                   "runs": runs, "passes_all": first_try, "days_done": done_days, "ex_passed": ex_passed,
                   "ex_total": ex_total, "solution_views": sol_views, "hint_views": hint_views,
                   "ex_per_hour": round(ex_passed / hours, 1) if total_min >= 10 else None},
        "streak": st,
        "pace": {"current_day": cur, "plan_day": plan, "delta": cur - plan,
                 "note": ("You're ahead of the suggested plan" if cur > plan else "You're on the suggested plan" if cur == plan else "You're behind the suggested plan")
                         + ". That's information, not a deadline."},
        "series": series,
        "types": dict(types), "bloom": {b: bloom.get(b, 0) for b in BLOOM_ORDER},
        "attempt_first_pct": round(100 * attempt_first / n_typed) if n_typed else None,
        "duplicate_pct": round(100 * dup / n_typed) if n_typed else None,
        "qtrend": qtrend, "per_day": per_day, "weak": weak, "profile": profile,
        "recommendations": recommendations(prog, profile, weak, st),
        "last_reflection": db.one("SELECT ts, provider, text FROM reflections ORDER BY id DESC LIMIT 1"),
    }


def thinking_profile(typed, all_q, types, bloom, attempt_first, dup, sol_views) -> dict:
    n = len(typed)
    traits, notes = [], []
    if n < 3:
        return {"label": "Getting to know you", "traits": [], "notes": [
            "Ask a few questions in the tutor and I'll start mapping how you think. Typed questions count most."]}
    tot = max(len(all_q), 1)
    share = {k: types.get(k, 0) / tot for k in types}
    af = attempt_first / n
    avg_bloom = sum(BLOOM_ORDER.index(q["bloom"]) for q in typed if q["bloom"] in BLOOM_ORDER) / n
    own = sum(1 for q in typed if "shows-own-thinking" in (q["flags"] or "")) / n
    top = max(share, key=share.get)
    labels = {"usage": "Applied thinker", "concept": "Concept explorer", "debug": "Hands-on debugger",
              "compare": "Comparer", "howto": "Builder", "extend": "Boundary tester", "review": "Craft-minded",
              "confirm": "Verifier", "other": "Curious generalist"}
    label = labels.get(top, "Curious generalist")
    if share.get("usage", 0) >= 0.2:
        traits.append("connects code to the real world")
        notes.append("You regularly ask where and how code is used. That is exactly how professionals remember syntax: attach it to a purpose.")
    if af >= 0.5:
        traits.append("tries before asking")
        notes.append(f"{round(af*100)}% of your questions come after an attempt. Strong habit: it makes every answer land.")
    elif n >= 5:
        notes.append(f"Only {round(af*100)}% of your questions came after you tried something. Next time run your idea first, then paste the result.")
    if avg_bloom >= 2.5:
        traits.append("asks analytical questions")
        notes.append("Many of your questions ask why, compare options, or test edge cases. That is the thinking that takes people past 'intermediate'.")
    elif avg_bloom < 1.5 and n >= 5:
        notes.append("Most questions are 'what is…' type. Try the next step up: ask 'why does…' or 'what happens if…'.")
    if share.get("confirm", 0) > 0.3:
        notes.append("A lot of questions ask for confirmation. Predict the output before running, then use the tutor to ask why you were off.")
    if share.get("debug", 0) > 0.4 and af < 0.5:
        notes.append("Debug questions dominate. Read the last line of the traceback aloud first. It names the bug surprisingly often.")
    if own >= 0.3:
        traits.append("explains own reasoning")
    if n >= 5 and dup / n >= 0.15:
        notes.append("You re-ask a few things. Add them to the Notes tab; repetition is a sign to write your own one-liner.")
    if sol_views and sol_views > max(3, 0.4 * len(all_q)):
        notes.append("You've opened several solutions. Try the 3-hint ladder first; struggling for 10 minutes is where the learning happens.")
    if not notes:
        notes.append("Balanced, steady questioning so far. Keep going.")
    return {"label": label, "traits": traits, "notes": notes[:5]}


def recommendations(prog, profile, weak, st, w: dict | None = None) -> list[dict]:
    recs = []
    w = w if w is not None else welcome(None, prog, st)
    recs.append({"kind": "next", "text": f"Continue Day {w['current_day']}: {content.day(w['current_day'])['title']}", "day": w["current_day"]})
    if w["kind"] == "recap":
        recs.append({"kind": "recap", "text": "Start with a 2-minute recap: ask the tutor to quiz you on the last lesson.", "day": w["current_day"]})
    for x in weak[:2]:
        recs.append({"kind": "review", "text": f"Revisit Day {x['day']} ({x['title']}): {x['reasons'][0]}", "day": x["day"]})
    unrated = [(n, p) for n, p in prog.items() if p["started"] and p["quiz_total"] and p["quiz_rated"] == 0 and p["ex_passed"] > 0]
    if unrated:
        n = unrated[0][0]
        recs.append({"kind": "quiz", "text": f"Day {n} quiz is untouched. Five minutes cements it.", "day": n})
    if st["current"] == 0 and st["last_active"]:
        recs.append({"kind": "habit", "text": "Even 15 focused minutes today restarts your streak.", "day": None})
    return recs[:5]
