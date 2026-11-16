"""Concept-level spaced review for the "progress" feature (helper of ex_progress.py).

A concept is a '### N.M Name' heading of a day's lesson. Evidence comes from the day's exercise checks, quiz ratings,
the day being finished, and warm-up answers. Each piece of evidence is mapped to the concepts it mentions (keyword
overlap between the concept name and the exercise title / quiz question); evidence that mentions no concept counts for
all concepts of that day. The schedule is derived from that timeline, so it is retroactive and idempotent.
Separate from portal/review.py (which only looks at missed quiz items); nothing here locks anything.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from . import content

STEPS = [1, 3, 7, 14, 30]          # days between reviews; doubles after the last step
MAX_INTERVAL = 180
MAX_CONCEPTS_PER_DAY = 12
_STOP = {"the", "and", "for", "with", "your", "you", "how", "what", "why", "use", "using", "into", "from", "that",
         "this", "are", "can", "does", "not", "its", "review", "week", "about", "when", "where", "which"}


def interval_for(step: int) -> int:
    if step < len(STEPS):
        return STEPS[step]
    return min(MAX_INTERVAL, STEPS[-1] * 2 ** (step - len(STEPS) + 1))


def tokens(s: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z][a-z0-9_]{2,}", (s or "").lower()):
        if w not in _STOP:
            out.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out


def _day(ts: str | None) -> date | None:
    try:
        return date.fromisoformat((ts or "")[:10])
    except ValueError:
        return None


def schedule(events: list[tuple[str, str]]) -> dict | None:
    """events: (iso timestamp, 'ok' | 'partial' | 'miss'), any order. Returns step / last / due / interval, or None.

    Per calendar day the last event wins. A miss resets to step 0 (1 day). An 'ok' on or after the due date moves up
    one step; an early 'ok' or a 'partial' keeps the step (the clock restarts from that practice)."""
    per_day: dict[date, str] = {}
    for ts, outcome in sorted(events, key=lambda e: e[0] or ""):
        d = _day(ts)
        if d and outcome in ("ok", "partial", "miss"):
            per_day[d] = outcome
    step, due, last = None, None, None
    for d in sorted(per_day):
        o = per_day[d]
        if o == "miss" or step is None:
            step = 0
        elif o == "ok" and d >= due:
            step += 1
        last, due = d, d + timedelta(days=interval_for(step))
    if step is None:
        return None
    return {"step": step, "last": last, "due": due, "interval": interval_for(step), "last_outcome": per_day[last]}


def _targets(ctoks: list[set], text: str) -> list[int]:
    t = tokens(text)
    hit = [i for i, c in enumerate(ctoks) if c & t]
    return hit or list(range(len(ctoks)))


def _status(step: int | None) -> str:
    return "new" if step is None else "learning" if step == 0 else "familiar" if step < 3 else "solid"


def build(f: dict, today: date) -> list[dict]:
    """Every concept with its mastery numbers and review schedule. f = the facts dict from ex_progress.load_facts()."""
    out: list[dict] = []
    for n, d in sorted(content.load_days().items()):
        names = d["concepts"][:MAX_CONCEPTS_PER_DAY]
        if not names:
            continue
        ctoks = [tokens(c) for c in names]
        evs: list[list] = [[] for _ in names]
        ex_of: list[list] = [[] for _ in names]          # per concept: (check_id, fully passed)
        qz_of: list[list] = [[] for _ in names]          # per concept: got-it flags of rated quiz items
        for e in d["exercises"]:
            g = f["ex"].get((n, e["id"]))
            for i in _targets(ctoks, e["title"]):
                ex_of[i].append(bool(g and g["n"] and g["p"] == g["n"]))
                if not g:
                    continue
                if g["n"] and g["p"] == g["n"] and g["pass_at"]:
                    evs[i].append((g["pass_at"], "ok"))
                if g["fail_at"]:
                    evs[i].append((g["fail_at"], "miss"))
        for q in d["quiz"]:
            r = f["quiz"].get((n, q["n"]))
            idx = _targets(ctoks, q["q"])
            for i in idx:
                qz_of[i].append(bool(r and r["rating"] == 2))
                if r and r["rated_at"] and r["rating"] in (0, 1, 2):
                    evs[i].append((r["rated_at"], {2: "ok", 1: "partial", 0: "miss"}[r["rating"]]))
        done_at = f["done"].get(n)
        for i in range(len(names)):
            if done_at:
                evs[i].append((done_at, "ok"))
            evs[i] += f["warm"].get((n, i), [])
        for i, name in enumerate(names):
            s = schedule(evs[i])
            total = len(ex_of[i]) + len(qz_of[i])
            got = sum(ex_of[i]) + sum(qz_of[i])
            rec = {"day_no": n, "idx": i, "name": name, "day_title": d["title"], "status": _status(s and s["step"]),
                   "step": s["step"] if s else None, "mastery": round(100 * got / total) if total else (100 if done_at else 0),
                   "evidence": {"ex_passed": sum(ex_of[i]), "ex_total": len(ex_of[i]),
                                "quiz_got": sum(qz_of[i]), "quiz_total": len(qz_of[i])},
                   "last_practiced": None, "due_date": None, "interval_days": None, "due": False,
                   "overdue_days": 0, "due_in_days": None, "urgency": 0.0, "last_outcome": None,
                   "href": f"#/day/{n}/learn"}
            if s:
                late = (today - s["due"]).days
                rec.update(last_practiced=s["last"].isoformat(), due_date=s["due"].isoformat(), interval_days=s["interval"],
                           due=late >= 0, overdue_days=max(0, late), due_in_days=max(0, -late), last_outcome=s["last_outcome"],
                           urgency=round((max(0, late) + 1) / s["interval"] + (0.5 if s["last_outcome"] == "miss" else 0), 2)
                           if late >= 0 else 0.0)
            out.append(rec)
    return out


def due_sorted(concepts: list[dict]) -> list[dict]:
    return sorted((c for c in concepts if c["due"]), key=lambda c: (-c["urgency"], c["day_no"], c["idx"]))


def _pick_quiz(f: dict, day: dict, c: dict, used: set) -> dict | None:
    ctoks = [tokens(x) for x in day["concepts"][:MAX_CONCEPTS_PER_DAY]]
    cands = [q for q in day["quiz"] if c["idx"] in _targets(ctoks, q["q"]) and ("q", day["n"], q["n"]) not in used]

    def rank(q):                                  # not-yet-"got it" first, then the least recently rated
        r = f["quiz"].get((day["n"], q["n"]))
        return (1 if r and r["rating"] == 2 else 0, (r["rated_at"] or "") if r else "", q["n"])
    cands.sort(key=rank)
    return cands[0] if cands else None


def _pick_ex(f: dict, day: dict, c: dict, used: set) -> dict | None:
    ctoks = [tokens(x) for x in day["concepts"][:MAX_CONCEPTS_PER_DAY]]
    cands = [e for e in day["exercises"] if c["idx"] in _targets(ctoks, e["title"]) and ("e", day["n"], e["id"]) not in used]
    cands.sort(key=lambda e: (0 if (f["ex"].get((day["n"], e["id"])) or {}).get("fail_at") else 1, e["level"], e["id"]))
    return cands[0] if cands else None


def warmup(f: dict, concepts: list[dict], size: int = 5) -> dict:
    """About `size` short items from due concepts (or, if nothing is due, the soonest-due practised ones)."""
    size = max(1, min(size, 8))
    pool, light = due_sorted(concepts), False
    if not pool:
        light = True
        pool = sorted((c for c in concepts if c["due_date"]), key=lambda c: (c["due_date"], c["day_no"], c["idx"]))
    items: list[dict] = []
    used: set = set()
    rounds = 0
    while pool and len(items) < size and rounds < 3:
        added = False
        for c in pool[:size]:
            if len(items) >= size:
                break
            day = content.day(c["day_no"])
            first = "quiz" if len(items) % 2 == 0 else "exercise"
            for kind in (first, "exercise" if first == "quiz" else "quiz"):
                if kind == "quiz":
                    q = _pick_quiz(f, day, c, used)
                    if q:
                        used.add(("q", day["n"], q["n"]))
                        items.append({"id": f"q:{day['n']}:{c['idx']}:{q['n']}", "kind": "quiz", "day_no": day["n"],
                                      "concept_idx": c["idx"], "concept": c["name"], "q_no": q["n"], "text": q["q"],
                                      "href": f"#/day/{day['n']}/quiz", "minutes": 1})
                        added = True
                        break
                else:
                    e = _pick_ex(f, day, c, used)
                    if e:
                        used.add(("e", day["n"], e["id"]))
                        items.append({"id": f"e:{day['n']}:{c['idx']}:{e['id']}", "kind": "exercise", "day_no": day["n"],
                                      "concept_idx": c["idx"], "concept": c["name"], "check_id": e["id"], "title": e["title"],
                                      "level": e["level"], "desc": e["desc"][:240], "href": f"#/day/{day['n']}/practice",
                                      "minutes": 3})
                        added = True
                        break
        rounds += 1
        if not added:
            break
    return {"items": items, "light": light, "due_total": len(due_sorted(concepts)),
            "minutes": sum(i["minutes"] for i in items), "empty": not items}


def validate_item(day_no: int, concept_idx: int, kind: str, ref: str) -> str | None:
    """Return an error text, or None when the (day, concept, kind, ref) points at real course content."""
    d = content.day(day_no)
    if not d:
        return "unknown day"
    if not 0 <= concept_idx < min(len(d["concepts"]), MAX_CONCEPTS_PER_DAY):
        return "unknown concept"
    if kind == "quiz":
        return None if any(str(q["n"]) == str(ref) for q in d["quiz"]) else "unknown quiz item"
    if kind == "exercise":
        return None if any(e["id"] == ref for e in d["exercises"]) else "unknown exercise"
    return "kind must be quiz or exercise"
