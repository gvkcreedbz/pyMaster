"""Support-ticket triage pipeline: the shape of most data / AI back-ends.

    CSV or API rows -> clean -> classify (cheap rules first, AI only when unsure, safe default last) -> store -> report

Pure standard library, so it runs anywhere:  python demo.py      (the real AI call is a stub you can swap, see LLMClassifier)
"""
import csv
import functools
import io
import json
import random
import re
import sqlite3
import time
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Protocol

LABELS = ("billing", "bug", "account", "feature", "other")


# ---- 1. DATA SHAPE: one dataclass instead of loose dicts ---------------------------------------------------------
@dataclass
class Ticket:
    id: int
    customer: str
    text: str
    received: str
    label: str | None = None
    confidence: float = 0.0
    source: str = ""                   # which classifier decided: rules | llm | default
    priority: str = "normal"


# ---- 2. PIPELINE STAGES AS GENERATORS: rows flow through one at a time, memory stays flat ---------------------------
def read_rows(csv_text: str) -> Iterator[dict]:
    yield from csv.DictReader(io.StringIO(csv_text))


def clean(rows: Iterable[dict], stats: Counter) -> Iterator[Ticket]:
    seen: set[int] = set()
    for row in rows:
        stats["rows_in"] += 1
        try:
            tid = int(row["id"])
        except (KeyError, TypeError, ValueError):
            stats["rejected_bad_id"] += 1
            continue
        text = re.sub(r"\s+", " ", (row.get("text") or "")).strip()
        if not text:
            stats["rejected_empty"] += 1
            continue
        if tid in seen:                                    # the same ticket exported twice: keep the first
            stats["rejected_duplicate"] += 1
            continue
        seen.add(tid)
        yield Ticket(tid, (row.get("customer") or "").strip().title(), text, (row.get("received") or "").strip())


# ---- 3. STRATEGY: any object with .name and .classify() can join the chain (typing.Protocol) --------------------------
class Classifier(Protocol):
    name: str

    def classify(self, text: str) -> tuple[str, float]: ...


class RuleClassifier:
    """Free, instant, explainable. Handles the obvious 70% so the expensive model only sees the hard 30%."""
    name = "rules"
    RULES = {
        "billing": r"charg|refund|invoice|payment|\bcard\b|billed",
        "bug": r"crash|error|broken|not working|fails?\b|\bbug\b",
        "account": r"password|log ?in|locked|2fa|sign ?in",
        "feature": r"wish|would be nice|please add|feature request|could you add",
    }

    def classify(self, text: str) -> tuple[str, float]:
        low = text.lower()
        hits = {label: len(re.findall(rx, low)) for label, rx in self.RULES.items()}
        label, n = max(hits.items(), key=lambda kv: kv[1])
        return ("other", 0.2) if n == 0 else (label, min(0.55 + 0.2 * n, 0.95))


# ---- 4. DECORATOR: retry with exponential backoff + jitter (networks fail; good code expects it) -----------------------
class TransientError(Exception):
    """Timeouts, 429s, 503s: worth trying again. A ValueError is NOT transient: retrying cannot fix it."""


def retry(times: int = 3, base: float = 0.2, sleep: Callable[[float], None] = time.sleep):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except TransientError:
                    if attempt == times:
                        raise
                    sleep(base * 2 ** (attempt - 1) + random.random() * base)       # 0.2s, 0.4s, 0.8s ... plus jitter
        return wrapper
    return decorate


# ---- 5. ADAPTER: hides one vendor's API behind our Classifier interface -----------------------------------------------
class LLMClassifier:
    """`client` is any callable(prompt) -> str. In production it wraps OpenAI / Anthropic / a local model."""
    name = "llm"

    def __init__(self, client: Callable[[str], str], stats: Counter, sleep: Callable[[float], None] = time.sleep):
        self.client, self.stats = client, stats
        self._ask = retry(times=3, sleep=sleep)(self._ask_once)

    def _ask_once(self, text: str) -> str:
        self.stats["llm_calls"] += 1
        return self.client("Classify this support ticket as one of " + "|".join(LABELS) +
                           '. Reply ONLY with JSON like {"label": "...", "confidence": 0.9}.\n\n' + text)

    def classify(self, text: str) -> tuple[str, float]:
        data = json.loads(self._ask(text))                 # model replied with prose instead of JSON -> ValueError
        if data.get("label") not in LABELS:                # never trust a model's output: validate it like user input
            raise ValueError(f"unknown label {data.get('label')!r}")
        return data["label"], float(data.get("confidence", 0.5))


# ---- 6. FALLBACK CHAIN: first confident answer wins, a failure never kills the batch ---------------------------------
class Triage:
    def __init__(self, chain: list[Classifier], stats: Counter, min_conf: float = 0.7):
        self.chain, self.stats, self.min_conf = chain, stats, min_conf

    def label(self, t: Ticket) -> Ticket:
        for c in self.chain:
            try:
                label, conf = c.classify(t.text)
            except Exception:                              # noqa: BLE001  (a batch job must survive one bad ticket)
                self.stats[f"{c.name}_failed"] += 1
                continue
            if conf >= self.min_conf:
                t.label, t.confidence, t.source = label, conf, c.name
                break
        else:
            t.label, t.confidence, t.source = "other", 0.0, "default"      # nothing was sure: park it for a human
        t.priority = priority_of(t)
        self.stats[f"source_{t.source}"] += 1
        return t


def priority_of(t: Ticket) -> str:
    """A pure function: same input, same output, trivial to unit-test."""
    urgent = re.search(r"urgent|asap|twice|locked out|can'?t (log|sign)|charged", t.text, re.I)
    return "high" if urgent or t.label == "bug" and "crash" in t.text.lower() else "normal"


# ---- 7. STORAGE: idempotent upsert, so re-running the same file never duplicates anything ----------------------------
SCHEMA = """CREATE TABLE IF NOT EXISTS tickets(
    id INTEGER PRIMARY KEY, customer TEXT, text TEXT, received TEXT,
    label TEXT, confidence REAL, source TEXT, priority TEXT)"""


def store(db: sqlite3.Connection, tickets: Iterable[Ticket]) -> int:
    db.execute(SCHEMA)
    rows = [(t.id, t.customer, t.text, t.received, t.label, t.confidence, t.source, t.priority) for t in tickets]
    with db:
        db.executemany(
            "INSERT INTO tickets VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
            "label=excluded.label, confidence=excluded.confidence, source=excluded.source, priority=excluded.priority", rows)
    return len(rows)


def report(db: sqlite3.Connection) -> dict:
    db.execute(SCHEMA)
    by_label = dict(db.execute("SELECT label, COUNT(*) FROM tickets GROUP BY label ORDER BY 2 DESC").fetchall())
    by_source = dict(db.execute("SELECT source, COUNT(*) FROM tickets GROUP BY source").fetchall())
    urgent = [r[0] for r in db.execute("SELECT id FROM tickets WHERE priority='high' ORDER BY id")]
    return {"total": sum(by_label.values()), "by_label": by_label, "decided_by": by_source, "urgent_ids": urgent}


# ---- 8. THE WHOLE JOB: five lines that read like the diagram ---------------------------------------------------------
def run_pipeline(csv_text: str, db: sqlite3.Connection, ai: Callable[[str], str] | None = None,
                 sleep: Callable[[float], None] = time.sleep) -> tuple[dict, Counter]:
    stats: Counter = Counter()
    chain: list[Classifier] = [RuleClassifier()]
    if ai:
        chain.append(LLMClassifier(ai, stats, sleep))
    triage = Triage(chain, stats)
    stored = store(db, (triage.label(t) for t in clean(read_rows(csv_text), stats)))
    stats["stored"] = stored
    return report(db), stats


# ---- 9. THE WEB LAYER (optional): upload a CSV, read the report ----------------------------------------------------------
def build_app(db: sqlite3.Connection, ai: Callable[[str], str] | None = None):
    # Imported here so the pipeline itself needs no web library. (That is also why this file does NOT use
    # `from __future__ import annotations`: FastAPI looks parameter types up by name in the module, and a
    # type imported inside a function would not be found, so `request: Request` would silently become a query field.)
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse

    app = FastAPI(title="Ticket triage")

    @app.post("/tickets/ingest")
    async def ingest(request: Request):
        text = (await request.body()).decode("utf-8")
        rep, stats = run_pipeline(text, db, ai, sleep=lambda s: None)
        return {"report": rep, "stats": dict(stats)}

    @app.get("/report")
    async def get_report():
        return report(db)

    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        return ("<!doctype html><meta charset=utf-8><title>Triage</title><h2>Ticket triage</h2><pre id=o>loading...</pre>"
                "<script>fetch('/report').then(r=>r.json()).then(j=>o.textContent=JSON.stringify(j,null,2))</script>")

    return app
