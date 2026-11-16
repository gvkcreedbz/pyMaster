"""Unit tests for the three blueprint reference implementations.   Run: python -m pytest _dev_tools/test_blueprints.py -q"""
import importlib
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pytest

sys.dont_write_bytecode = True      # never litter the blueprint folders with __pycache__
BP = Path(__file__).resolve().parent.parent / "blueprints"


def load(folder, module):
    sys.path.insert(0, str(BP / folder))
    try:
        sys.modules.pop(module, None)
        return importlib.import_module(module)
    finally:
        sys.path.remove(str(BP / folder))


# ---------------------------------------------------------------- blueprint 1: order tracker
@pytest.fixture()
def tracker():
    from fastapi.testclient import TestClient
    mod = load("01_live_order_tracker", "app")
    with TestClient(mod.build_app()) as client:
        yield mod, client


def place(client, key=None, **over):
    body = {"customer": "Asha", "items": ["pizza"], **over}
    return client.post("/orders", json=body, headers={"Idempotency-Key": key} if key else {})


def test_state_machine_table_is_closed(tracker):
    mod, _ = tracker
    for old, nexts in mod.NEXT.items():
        for new in mod.Status:
            assert mod.can_move(old, new) == (new in nexts)
    assert not mod.NEXT[mod.Status.DELIVERED] and not mod.NEXT[mod.Status.CANCELLED]


def test_happy_path_and_history(tracker):
    _, c = tracker
    oid = place(c).json()["id"]
    for s in ("accepted", "preparing", "out_for_delivery", "delivered"):
        assert c.post(f"/orders/{oid}/status", json={"status": s}).status_code == 200
    got = c.get(f"/orders/{oid}").json()
    assert [h["status"] for h in got["history"]] == ["placed", "accepted", "preparing", "out_for_delivery", "delivered"]


def test_illegal_and_unknown(tracker):
    _, c = tracker
    oid = place(c).json()["id"]
    assert c.post(f"/orders/{oid}/status", json={"status": "delivered"}).status_code == 409
    assert c.post(f"/orders/{oid}/status", json={"status": "teleported"}).status_code == 422
    assert c.post("/orders/nope/status", json={"status": "accepted"}).status_code == 404
    assert c.get("/orders/nope").status_code == 404


def test_validation_at_the_edge(tracker):
    _, c = tracker
    assert place(c, customer="").status_code == 422
    assert place(c, items=[]).status_code == 422
    assert place(c, items=["x"] * 21).status_code == 422


def test_idempotency_key_prevents_duplicates(tracker):
    _, c = tracker
    a, b = place(c, "k1"), place(c, "k1")
    assert (a.status_code, b.status_code) == (201, 200) and a.json()["id"] == b.json()["id"]
    assert place(c, "k2").json()["id"] != a.json()["id"]


def test_websocket_gets_snapshot_then_pushes_and_closes(tracker):
    _, c = tracker
    oid = place(c).json()["id"]
    with c.websocket_connect(f"/ws/orders/{oid}") as ws:
        assert ws.receive_json()["type"] == "snapshot"
        c.post(f"/orders/{oid}/status", json={"status": "cancelled"})
        assert ws.receive_json()["order"]["status"] == "cancelled"


def test_websocket_unknown_order_is_rejected(tracker):
    from starlette.websockets import WebSocketDisconnect
    _, c = tracker
    with pytest.raises(WebSocketDisconnect), c.websocket_connect("/ws/orders/nope"):
        pass


def test_hub_drops_for_slow_watchers_and_cleans_up(tracker):
    mod, _ = tracker
    hub = mod.Hub()
    q = hub.subscribe("o")
    sent = sum(hub.publish("o", {"n": i}) for i in range(150))
    assert sent == 100 and q.qsize() == 100            # bounded queue: the rest were dropped, publisher never blocked
    hub.unsubscribe("o", q)
    assert hub.publish("o", {}) == 0


# ---------------------------------------------------------------- blueprint 2: triage pipeline
@pytest.fixture()
def pipe():
    return load("02_ticket_triage_pipeline", "pipeline")


def test_clean_rejects_and_normalises(pipe):
    stats = Counter()
    rows = [{"id": "1", "customer": " asha ", "text": " a   b ", "received": "t"}, {"id": "1", "text": "dup"},
            {"id": "x", "text": "bad id"}, {"id": "3", "text": "  "}, {"id": "4", "text": "ok"}]
    got = list(pipe.clean(rows, stats))
    assert [t.id for t in got] == [1, 4] and got[0].text == "a b" and got[0].customer == "Asha"
    assert (stats["rejected_duplicate"], stats["rejected_bad_id"], stats["rejected_empty"]) == (1, 1, 1)


def test_rule_classifier(pipe):
    r = pipe.RuleClassifier()
    assert r.classify("I was charged twice, refund please")[0] == "billing"
    assert r.classify("can't log in, account locked")[0] == "account"
    assert r.classify("hello there") == ("other", 0.2)


def test_retry_only_retries_transient_errors(pipe):
    waits, calls = [], {"n": 0}

    @pipe.retry(times=3, base=0.1, sleep=waits.append)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise pipe.TransientError("503")
        return "ok"

    assert flaky() == "ok" and calls["n"] == 3 and len(waits) == 2 and waits[1] > waits[0] * 1.5

    @pipe.retry(times=3, sleep=waits.append)
    def broken():
        calls["n"] += 1
        raise ValueError("not transient")

    calls["n"] = 0
    with pytest.raises(ValueError):
        broken()
    assert calls["n"] == 1


def test_llm_output_is_validated(pipe):
    stats = Counter()
    ok = pipe.LLMClassifier(lambda p: '{"label": "bug", "confidence": 0.9}', stats, sleep=lambda s: None)
    assert ok.classify("x") == ("bug", 0.9)
    for reply in ("Sure! it is a bug", '{"label": "weather"}', "{}"):
        with pytest.raises(ValueError):
            pipe.LLMClassifier(lambda p, r=reply: r, stats, sleep=lambda s: None).classify("x")


def test_chain_falls_back_and_never_crashes(pipe):
    db = sqlite3.connect(":memory:")
    csv_text = "id,customer,text\n1,a,hello world\n2,b,charged twice\n"
    boom = Counter()

    def dead_ai(prompt):
        raise pipe.TransientError("down")

    rep, stats = pipe.run_pipeline(csv_text, db, ai=dead_ai, sleep=lambda s: None)
    assert rep["total"] == 2 and rep["decided_by"] == {"default": 1, "rules": 1}
    assert stats["llm_failed"] == 1 and stats["llm_calls"] == 3 and boom == Counter()


def test_pipeline_is_idempotent_and_rules_skip_the_ai(pipe):
    db = sqlite3.connect(":memory:")
    calls = []
    text = "id,customer,text\n1,a,my card was charged twice\n"
    pipe.run_pipeline(text, db, ai=lambda p: calls.append(p) or '{"label":"bug"}')
    pipe.run_pipeline(text, db)
    assert calls == [] and pipe.report(db)["total"] == 1


# ---------------------------------------------------------------- blueprint 3: watcher
@pytest.fixture()
def wmod():
    return load("03_site_watcher", "watcher")


def test_breaker_lifecycle(wmod):
    b = wmod.Breaker(max_failures=3, cool_off=100)
    for t in (0, 1):
        b.record(False, t)
    assert b.state == "closed" and b.allow(2)
    b.record(False, 2)
    assert b.state == "open" and not b.allow(50) and b.allow(102)       # half-open probe after the cool-off
    b.record(False, 102)
    assert b.state == "open" and not b.allow(150)                      # a failed probe re-opens the window
    b.record(True, 202)
    assert b.state == "closed" and b.failures == 0


def make_watcher(wmod, fetch, targets, notifier=None):
    notifier = notifier or wmod.ConsoleNotifier()
    return wmod.Watcher(targets, fetch, [notifier], Path(tempfile.mkdtemp()) / "s.json"), notifier


def test_price_drop_alerts_only_past_threshold(wmod, capsys):
    page = {"p": "Price: $100.00"}
    t = [{"name": "x", "kind": "price", "url": "u", "pattern": r"Price: \$([\d\.]+)", "every": 1, "min_drop_pct": 5}]
    w, n = make_watcher(wmod, lambda u: page["p"], t)
    w.tick(0)
    page["p"] = "Price: $98.00"
    w.tick(10)
    assert n.sent == []                                  # 2% is noise
    page["p"] = "Price: $90.00"
    w.tick(20)
    assert len(n.sent) == 1 and "dropped" in n.sent[0][0]
    w.tick(30)
    assert len(n.sent) == 1                              # unchanged: silence


def test_schedule_and_failure_alerts_are_transitions(wmod, capsys):
    boom = {"on": True}

    def fetch(u):
        if boom["on"]:
            raise TimeoutError("t")
        return "ok"

    t = [{"name": "api", "kind": "uptime", "url": "u", "every": 10}]
    w, n = make_watcher(wmod, fetch, t)
    assert w.tick(0) == 1 and w.tick(5) == 0             # not due yet
    w.tick(10)
    w.tick(20)
    assert [x[0] for x in n.sent] == ["api is failing"]  # one alert, at the 3rd failure
    for now in range(30, 300, 10):                       # still down, breaker open: no extra alerts
        w.tick(now)
    assert len(n.sent) == 1
    boom["on"] = False
    w.tick(400)
    assert [x[0] for x in n.sent] == ["api is failing", "api recovered"]


def test_state_survives_restart_and_unknown_kind_is_survivable(wmod, capsys):
    path = Path(tempfile.mkdtemp()) / "state.json"
    t = [{"name": "p", "kind": "content", "url": "u", "every": 1}]
    w = wmod.Watcher(t, lambda u: "hello", [wmod.ConsoleNotifier()], path)
    w.tick(0)
    again = wmod.Watcher(t, lambda u: "hello", [wmod.ConsoleNotifier()], path)
    assert again.state == w.state and again.state["p"]
    bad = wmod.Watcher([{"name": "z", "kind": "nope", "url": "u"}], lambda u: "", [], Path(tempfile.mkdtemp()) / "s.json")
    bad.tick(0)                                          # KeyError inside the check is contained like any failure
    assert bad.status()["z"]["failures"] == 1


def test_broken_notifier_does_not_stop_the_others(wmod, capsys):
    class Boom:
        def send(self, *a):
            raise RuntimeError("slack down")

    good = wmod.ConsoleNotifier()
    w = wmod.Watcher([], lambda u: "", [Boom(), good], Path(tempfile.mkdtemp()) / "s.json")
    w.alert("t", "b")
    assert good.sent == [("t", "b")]


def test_state_file_is_never_half_written(wmod):
    d = Path(tempfile.mkdtemp())
    wmod.save_state(d / "s.json", {"a": 1})
    wmod.save_state(d / "s.json", {"a": 2})
    assert wmod.load_state(d / "s.json") == {"a": 2} and [p.name for p in d.iterdir()] == ["s.json"]
    (d / "s.json").write_text("{broken", encoding="utf-8")
    assert wmod.load_state(d / "s.json") == {}           # corrupt file: start fresh instead of crashing
