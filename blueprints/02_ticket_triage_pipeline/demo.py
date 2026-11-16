"""Runs the triage pipeline end to end on a messy sample file, with a deliberately flaky fake AI.
Run: python demo.py          (standard library only; the optional web layer needs fastapi + httpx)
"""
import json
import sqlite3

import pipeline
from pipeline import TransientError

SAMPLE = '''id,received,customer,text
1,2026-11-16 09:01,  asha  ,"My card was charged TWICE for order 5521!!"
2,2026-11-16 09:04,ravi,"App   crashes when I open settings on Android"
3,2026-11-16 09:09,meera,"I can't log in, my account is locked"
4,2026-11-16 09:15,john,"It would be nice if you could add dark mode"
5,2026-11-16 09:20,sara,"Hello, is the store open on Sunday?"
6,2026-11-16 09:22,lee,"Please send a refund for the January invoice"
6,2026-11-16 09:22,lee,"(duplicate row from a double export)"
x,2026-11-16 09:30,bad,"This row has a broken id"
8,2026-11-16 09:31,ghost,"   "
9,2026-11-16 09:40,kim,"Your delivery estimate widget feels slow and confusing"
'''


def make_flaky_ai():
    """Pretend model: times out on its 1st call, rate-limits on its 3rd, answers in prose once, otherwise returns JSON."""
    calls = {"n": 0}

    def ai(prompt: str) -> str:
        calls["n"] += 1
        text = prompt.split("\n\n", 1)[1].lower()
        if calls["n"] in (1, 3):
            raise TransientError("503 service unavailable")
        if "store open" in text:
            return "Sure! I would say this is a general question."          # not JSON -> ValueError -> fallback
        if "slow" in text:
            return json.dumps({"label": "bug", "confidence": 0.82})
        return json.dumps({"label": "other", "confidence": 0.9})
    return ai, calls


def main():
    db = sqlite3.connect(":memory:")
    ai, calls = make_flaky_ai()
    waits = []
    rep, stats = pipeline.run_pipeline(SAMPLE, db, ai=ai, sleep=waits.append)      # record backoff instead of really sleeping

    print("== 1. cleaning (generators: one row at a time)")
    print({k: v for k, v in stats.items() if k.startswith(("rows", "rejected"))})

    print("\n== 2. who decided each ticket (cheap rules first, AI only when unsure)")
    for row in db.execute("SELECT id, customer, label, source, priority, text FROM tickets ORDER BY id"):
        print(f"  #{row[0]:<2} {row[1]:<6} {row[2]:<8} by {row[3]:<7} {row[4]:<6} {row[5][:44]}")

    print("\n== 3. resilience")
    print("  AI calls made:", stats["llm_calls"], "| retried after backoff:", len(waits), "| AI failures handled:", stats["llm_failed"])
    print("  backoff waits (s):", [round(w, 2) for w in waits])

    print("\n== 4. the report")
    print(json.dumps(rep, indent=2))

    print("\n== 5. run the same file again: nothing duplicates (idempotent upsert)")
    rep2, _ = pipeline.run_pipeline(SAMPLE, db, ai=None)
    print("  total before:", rep["total"], "| total after:", rep2["total"])

    print("\n== 6. the web layer (optional)")
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        print("  (install fastapi and httpx to see this part)")
        return
    client = TestClient(pipeline.build_app(sqlite3.connect(":memory:", check_same_thread=False)))
    out = client.post("/tickets/ingest", content=SAMPLE.encode()).json()
    print("  POST /tickets/ingest ->", out["report"]["total"], "tickets,", out["report"]["by_label"])
    print("  GET /report          ->", client.get("/report").json()["urgent_ids"], "are urgent")


if __name__ == "__main__":
    main()
