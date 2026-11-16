"""Site & price watcher: the skeleton of every automation / monitoring service.

    scheduler tick --> for each due target: circuit breaker? --> check plugin --> compare with last state
                                                                                        |
                                    notifiers (console, webhook, ...)  <-- only when something CHANGED

Standard library only (+ fastapi for the optional status page). Time and the network are *injected*, which is why
this whole service can be tested in milliseconds with a fake clock and a fake website:  python demo.py
"""
import hashlib
import json
import logging
import os
import re
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

log = logging.getLogger("watcher")


# ---- 1. PLUGIN REGISTRY: a decorator adds a new kind of check without touching the engine ---------------------------
CHECKS: dict[str, Callable] = {}


def check(kind: str):
    def register(fn):
        CHECKS[kind] = fn
        return fn
    return register


@check("price")
def price_check(target: dict, fetch: Callable[[str], str]):
    """Return the number found by the regex on the page (e.g. 'Price: $1,299.00' -> 1299.0)."""
    html = fetch(target["url"])
    m = re.search(target["pattern"], html)
    if not m:
        raise ValueError("price pattern not found: the site layout probably changed")
    return float(m.group(1).replace(",", ""))


@check("content")
def content_check(target: dict, fetch: Callable[[str], str]):
    """Return a fingerprint of the page: any change in the text changes the hash."""
    html = fetch(target["url"])
    return hashlib.sha256(re.sub(r"\s+", " ", html).encode()).hexdigest()[:12]


@check("uptime")
def uptime_check(target: dict, fetch: Callable[[str], str]):
    fetch(target["url"])                       # raises on timeout / 5xx
    return "up"


# ---- 2. CIRCUIT BREAKER: stop hammering something that is clearly down ---------------------------------------------
@dataclass
class Breaker:
    max_failures: int = 3
    cool_off: float = 300.0
    failures: int = 0
    opened_at: float | None = None

    def allow(self, now: float) -> bool:
        if self.opened_at is None:
            return True
        if now - self.opened_at >= self.cool_off:          # half-open: let ONE probe through
            return True
        return False

    def record(self, ok: bool, now: float) -> None:
        if ok:
            self.failures, self.opened_at = 0, None
        else:
            self.failures += 1
            if self.failures >= self.max_failures:
                self.opened_at = now                       # (re)open: stay quiet for cool_off seconds

    @property
    def state(self) -> str:
        return "open" if self.opened_at is not None else "closed"


# ---- 3. OBSERVER: anything with .send() can receive alerts ---------------------------------------------------------
class Notifier(Protocol):
    def send(self, title: str, body: str) -> None: ...


class ConsoleNotifier:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, title: str, body: str) -> None:
        self.sent.append((title, body))
        print(f"   ALERT  {title}: {body}")


class WebhookNotifier:
    """Slack / Teams / Discord all accept a JSON POST. `post` is injected (requests.post in production)."""

    def __init__(self, url: str, post: Callable[..., object]):
        self.url, self.post = url, post

    def send(self, title: str, body: str) -> None:
        self.post(self.url, json={"text": f"*{title}*\n{body}"}, timeout=5)


# ---- 4. ATOMIC STATE FILE: a crash mid-write must never corrupt what we remember ---------------------------------------
def save_state(path: Path, state: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
    for attempt in range(8):                               # atomic: readers see the old file or the new one, never half
        try:
            os.replace(tmp, path)
            return
        except PermissionError:                            # Windows: antivirus / indexer may hold the file for a few ms
            if attempt == 7:
                raise
            time.sleep(0.02 * (attempt + 1))


def load_state(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


# ---- 5. THE ENGINE ------------------------------------------------------------------------------------------------
@dataclass
class Watcher:
    targets: list[dict]
    fetch: Callable[[str], str]
    notifiers: list[Notifier]
    state_path: Path
    state: dict = field(default_factory=dict)
    breakers: dict[str, Breaker] = field(default_factory=dict)
    due: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        self.state = load_state(self.state_path)           # survive restarts: remember the last value of every target

    def alert(self, title: str, body: str) -> None:
        for n in self.notifiers:
            try:
                n.send(title, body)
            except Exception:                              # noqa: BLE001  (one broken Slack hook must not stop the rest)
                log.exception("notifier %s failed", type(n).__name__)

    def tick(self, now: float) -> int:
        """Run every target that is due at time `now`. Returns how many were checked."""
        ran = 0
        for t in self.targets:
            name = t["name"]
            if self.due.get(name, 0) > now:
                continue
            self.due[name] = now + t.get("every", 60)
            br = self.breakers.setdefault(name, Breaker())
            if not br.allow(now):
                continue
            ran += 1
            try:
                value = CHECKS[t["kind"]](t, self.fetch)
            except Exception as e:                         # noqa: BLE001
                was_open = br.state == "open"
                br.record(False, now)
                if br.state == "open" and not was_open:    # alert on the TRANSITION, not on every failed minute
                    self.alert(f"{name} is failing", f"{br.failures} failures in a row ({type(e).__name__}: {e}). Pausing checks.")
                continue
            if br.state == "open":
                self.alert(f"{name} recovered", "the check works again")
            br.record(True, now)
            self.compare(t, value)
        save_state(self.state_path, self.state)
        return ran

    def compare(self, t: dict, value) -> None:
        name, old = t["name"], self.state.get(t["name"])
        self.state[name] = value
        if old is None or old == value:                    # first sighting, or nothing changed: stay quiet
            return
        if t["kind"] == "price":
            drop = (old - value) / old * 100
            if drop >= t.get("min_drop_pct", 5):
                self.alert(f"{name}: price dropped {drop:.0f}%", f"{old:g} -> {value:g}  {t['url']}")
        else:
            self.alert(f"{name} changed", f"{old} -> {value}")

    def status(self) -> dict:
        return {n: {"last": self.state.get(n), "breaker": b.state, "failures": b.failures} for n, b in self.breakers.items()}


def run_forever(w: Watcher, sleep: Callable[[float], None], clock: Callable[[], float], every: float = 5.0) -> None:
    """The production loop: wake up, run what is due, go back to sleep. Ctrl+C to stop."""
    while True:
        w.tick(clock())
        sleep(every)


# ---- 6. THE WEB LAYER (optional): a read-only status page for humans and uptime monitors ------------------------------
def build_app(w: Watcher):
    from fastapi import FastAPI                # local import: see the note in blueprint 2 about annotations

    app = FastAPI(title="Watcher status")

    @app.get("/status")
    async def status():
        return w.status()

    @app.get("/healthz")
    async def healthz():
        return {"ok": True}

    return app
