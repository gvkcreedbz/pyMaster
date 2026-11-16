"""Spaced review: what is worth revisiting today, built from what you told the portal you missed.

Leitner-style spacing with no extra bookkeeping: a quiz question you rated "Missed it" comes back after 1 day,
"Partly" after 3 days. Re-rate it "Got it" and it leaves the queue. Exercises whose checks still fail are due immediately.
Nothing here ever locks anything; it is only a suggestion list.
"""
from __future__ import annotations

from datetime import datetime

from . import content, db

INTERVAL_DAYS = {0: 1.0, 1: 3.0}        # rating -> days to wait before it is due again


def _age_days(iso: str | None) -> float:
    try:
        return max(0.0, (datetime.now() - datetime.fromisoformat(iso)).total_seconds() / 86400) if iso else 99.0
    except ValueError:
        return 99.0


def queue(include_not_due: bool = False, limit: int = 40) -> dict:
    quiz = []
    for r in db.rows("SELECT day_no, q_no, rating, rated_at FROM quiz WHERE rating IN (0, 1)"):
        d = content.day(r["day_no"])
        item = next((x for x in d["quiz"] if x["n"] == r["q_no"]), None) if d else None
        if not item:
            continue
        age, wait = _age_days(r["rated_at"]), INTERVAL_DAYS[r["rating"]]
        due = age >= wait
        if due or include_not_due:
            quiz.append({"day_no": r["day_no"], "q_no": r["q_no"], "q": item["q"], "rating": r["rating"], "title": d["title"],
                         "age_days": round(age, 1), "due": due, "due_in_days": 0 if due else round(wait - age, 1)})
    quiz.sort(key=lambda x: (not x["due"], x["rating"], -x["age_days"]))
    exercises = []
    for r in db.rows("SELECT day_no, check_id, name, fails, last_at FROM checks WHERE last_status='FAIL' "
                     "ORDER BY last_at DESC LIMIT 200"):
        d = content.day(r["day_no"])
        if d:
            exercises.append({"day_no": r["day_no"], "check_id": r["check_id"], "name": r["name"], "fails": r["fails"],
                              "title": d["title"]})
    # one line per exercise, not per assertion
    seen, uniq = set(), []
    for e in exercises:
        k = (e["day_no"], e["check_id"])
        if k not in seen:
            seen.add(k)
            uniq.append(e)
    return {"quiz": quiz[:limit], "exercises": uniq[:limit], "counts": {
        "quiz_due": sum(1 for q in quiz if q["due"]), "exercises": len(uniq)}}
