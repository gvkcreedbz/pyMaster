"""Live Order Tracker: a small but real full-stack backend (the heart of every delivery / ride / booking app).

    Browser  <--HTTP + WebSocket-->  FastAPI  <-->  Repo (SQLite)
                                        |
                                        +--> Hub (pub/sub): pushes every change to whoever is watching that order

Run for real:    uvicorn app:serve --factory --reload      then open http://127.0.0.1:8000/
Run the demo:    python demo.py                    (no server needed)
"""
from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import time
import uuid
from enum import Enum

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


# ---- 1. DOMAIN: a state machine in a dozen lines -------------------------------------------------------------
class Status(str, Enum):
    PLACED = "placed"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


NEXT = {                                        # the ONLY legal moves; everything else is a bug or an attack
    Status.PLACED: {Status.ACCEPTED, Status.CANCELLED},
    Status.ACCEPTED: {Status.PREPARING, Status.CANCELLED},
    Status.PREPARING: {Status.OUT_FOR_DELIVERY},
    Status.OUT_FOR_DELIVERY: {Status.DELIVERED},
    Status.DELIVERED: set(),
    Status.CANCELLED: set(),
}
FINAL = {Status.DELIVERED, Status.CANCELLED}


def can_move(old: Status, new: Status) -> bool:
    return new in NEXT[old]


# ---- 2. VALIDATION AT THE EDGE: bad data never gets past these classes ---------------------------------------
class OrderIn(BaseModel):
    customer: str = Field(min_length=1, max_length=60)
    items: list[str] = Field(min_length=1, max_length=20)


class MoveIn(BaseModel):
    status: Status                               # "teleported" -> automatic 422, no if-statements needed


# ---- 3. REPOSITORY: the only code that knows SQL ----------------------------------------------------------------
class Repo:
    """Swap SQLite for PostgreSQL by rewriting this class alone; the rest of the app never sees a query."""

    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS orders(
                id TEXT PRIMARY KEY, customer TEXT NOT NULL, items TEXT NOT NULL,
                status TEXT NOT NULL, idem_key TEXT UNIQUE, created REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS history(
                id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, status TEXT NOT NULL, at REAL NOT NULL);
        """)

    @staticmethod
    def _order(row) -> dict | None:
        return None if row is None else {**dict(row), "items": json.loads(row["items"])}

    def get(self, oid: str) -> dict | None:
        return self._order(self.db.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone())

    def create(self, o: OrderIn, key: str | None) -> tuple[dict, bool]:
        """Returns (order, created). The same Idempotency-Key always returns the same order (safe retries)."""
        if key:
            row = self.db.execute("SELECT * FROM orders WHERE idem_key=?", (key,)).fetchone()
            if row:
                return self._order(row), False
        oid, now = uuid.uuid4().hex[:8], time.time()
        with self.db:                                            # one transaction: both rows or neither
            self.db.execute("INSERT INTO orders VALUES(?,?,?,?,?,?)",
                            (oid, o.customer, json.dumps(o.items), Status.PLACED.value, key, now))
            self.db.execute("INSERT INTO history(order_id,status,at) VALUES(?,?,?)", (oid, Status.PLACED.value, now))
        return self.get(oid), True

    def set_status(self, oid: str, status: Status) -> dict:
        with self.db:
            self.db.execute("UPDATE orders SET status=? WHERE id=?", (status.value, oid))
            self.db.execute("INSERT INTO history(order_id,status,at) VALUES(?,?,?)", (oid, status.value, time.time()))
        return self.get(oid)

    def history(self, oid: str) -> list[dict]:
        rows = self.db.execute("SELECT status, at FROM history WHERE order_id=? ORDER BY id", (oid,)).fetchall()
        return [dict(r) for r in rows]


# ---- 4. PUB/SUB: how one change reaches many open browser tabs ---------------------------------------------------
class Hub:
    """Each watcher owns an asyncio.Queue. Publishing never waits for a slow watcher."""

    def __init__(self):
        self.watchers: dict[str, set[asyncio.Queue]] = {}

    def subscribe(self, oid: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self.watchers.setdefault(oid, set()).add(q)
        return q

    def unsubscribe(self, oid: str, q: asyncio.Queue) -> None:
        self.watchers.get(oid, set()).discard(q)

    def publish(self, oid: str, event: dict) -> int:
        sent = 0
        for q in list(self.watchers.get(oid, ())):
            try:
                q.put_nowait(event)
                sent += 1
            except asyncio.QueueFull:                            # a stuck client must not stall everyone else
                pass
        return sent


# ---- 5. THE APP, built by a factory so every test gets its own clean copy ------------------------------------------
def build_app(db_path: str = ":memory:") -> FastAPI:
    app = FastAPI(title="Live Order Tracker")
    app.state.repo, app.state.hub = Repo(db_path), Hub()

    def repo(request: Request) -> Repo:                          # dependency injection: handlers ask, FastAPI provides
        return request.app.state.repo

    def hub(request: Request) -> Hub:
        return request.app.state.hub

    @app.post("/orders", status_code=201)
    async def place_order(o: OrderIn, response: Response, idempotency_key: str | None = Header(default=None),
                          r: Repo = Depends(repo)):
        order, created = r.create(o, idempotency_key)
        if not created:
            response.status_code = 200                           # "I already did this": same answer, no duplicate
        return order

    @app.get("/orders/{oid}")
    async def read_order(oid: str, r: Repo = Depends(repo)):
        order = r.get(oid)
        if not order:
            raise HTTPException(404, "no such order")
        return {**order, "history": r.history(oid)}

    @app.post("/orders/{oid}/status")
    async def move_order(oid: str, m: MoveIn, r: Repo = Depends(repo), h: Hub = Depends(hub)):
        order = r.get(oid)
        if not order:
            raise HTTPException(404, "no such order")
        old = Status(order["status"])
        if not can_move(old, m.status):
            raise HTTPException(409, f"cannot go from {old.value} to {m.status.value}")
        order = r.set_status(oid, m.status)
        h.publish(oid, {"type": "status", "order": order})       # fan-out to every open tab
        return order

    @app.websocket("/ws/orders/{oid}")
    async def watch_order(ws: WebSocket, oid: str):
        repo_, hub_ = ws.app.state.repo, ws.app.state.hub
        order = repo_.get(oid)
        if not order:
            await ws.close(code=4404)
            return
        await ws.accept()
        q = hub_.subscribe(oid)
        try:
            await ws.send_json({"type": "snapshot", "order": order, "history": repo_.history(oid)})
            while True:
                event = await q.get()
                await ws.send_json(event)
                if Status(event["order"]["status"]) in FINAL:
                    break
            await ws.close()
        except WebSocketDisconnect:
            pass
        finally:
            hub_.unsubscribe(oid, q)                             # always clean up, or memory leaks one queue per visit

    @app.get("/", response_class=HTMLResponse)
    async def page():
        return PAGE

    return app


# ---- 6. THE FRONT END: one HTML file, no build step. Plain JS opens a WebSocket and repaints. -----------------------
PAGE = """<!doctype html><meta charset=utf-8><title>Live Order Tracker</title>
<style>body{font:16px system-ui;max-width:520px;margin:40px auto;padding:0 16px}
li{padding:6px 0}.now{font-weight:700}button{margin:4px 4px 0 0}</style>
<h2>Live Order Tracker</h2>
<form id=f><input id=who placeholder="your name" value="Asha"> <input id=items value="pizza, cola">
<button>Place order</button></form><p id=info></p><ol id=steps></ol><div id=ops></div>
<script>
const ORDER = ["placed","accepted","preparing","out_for_delivery","delivered"];
let oid = null, ws = null;
const paint = o => {
  info.textContent = "Order " + o.id + " for " + o.customer + ": " + o.items.join(", ");
  steps.innerHTML = ORDER.map(s => `<li class="${s === o.status ? "now" : ""}">${s === o.status ? "▶ " : ""}${s}</li>`).join("");
  ops.innerHTML = ORDER.concat("cancelled").map(s => `<button data-s="${s}">${s}</button>`).join("");
};
ops.onclick = async e => { if (e.target.dataset.s) await fetch(`/orders/${oid}/status`,
  {method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify({status: e.target.dataset.s})}); };
f.onsubmit = async e => {
  e.preventDefault();
  const r = await fetch("/orders", {method: "POST", headers: {"content-type": "application/json"},
    body: JSON.stringify({customer: who.value, items: items.value.split(",").map(s => s.trim()).filter(Boolean)})});
  const o = await r.json(); oid = o.id; paint(o);
  ws?.close(); ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws/orders/" + oid);
  ws.onmessage = m => paint(JSON.parse(m.data).order);
};
</script>"""

def serve() -> FastAPI:
    """What `uvicorn app:serve --factory` calls: the real app, backed by a file. Tests call build_app() instead."""
    return build_app(os.environ.get("TRACKER_DB", "tracker.db"))
