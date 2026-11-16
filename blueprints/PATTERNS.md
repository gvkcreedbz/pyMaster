# Pattern catalog — the reusable shapes behind real Python back-ends

> Frameworks come and go; these shapes don't. Each pattern below is **small**, shows up in the three blueprints, and is something you can drop into your own project tomorrow.
> **How to read an entry:** the *problem* it solves → the *Python shape* (copy it) → *where you've seen it* → *when NOT to use it*.

## The map

| # | Pattern | One-line idea | [Order tracker](#/blueprints/live-order-tracker) | [Ticket triage](#/blueprints/ticket-triage-pipeline) | [Site watcher](#/blueprints/site-watcher) |
|---|---|---|:-:|:-:|:-:|
| 1 | App factory + dependency injection | build the app from a function; pass collaborators in | ✅ | ✅ | ✅ |
| 2 | Validation at the edge | bad data dies at the border | ✅ | ✅ | |
| 3 | Repository | one class owns all SQL | ✅ | ✅ | |
| 4 | State machine | a table of legal moves | ✅ | | ✅ (breaker) |
| 5 | Idempotency | doing it twice = doing it once | ✅ | ✅ | |
| 6 | Pub/Sub (observer) | publishers don't know their listeners | ✅ | | ✅ |
| 7 | Pipeline of generators | stream rows through stages | | ✅ | |
| 8 | Strategy via `Protocol` | swap behaviour without inheritance | | ✅ | ✅ |
| 9 | Adapter + fallback chain | hide the vendor, never depend on one | | ✅ | |
| 10 | Retry with backoff + jitter | try again, politely | | ✅ | |
| 11 | Circuit breaker | stop calling what is clearly down | | | ✅ |
| 12 | Plugin registry | a decorator adds a feature | | | ✅ |
| 13 | Injected clock and network | make time and I/O parameters | ✅ | ✅ | ✅ |
| 14 | Atomic persistence | write to a temp file, then swap | | | ✅ |
| 15 | Alert on transitions | speak only when something changed | | | ✅ |
| 16 | Functional core, imperative shell | rules are pure, I/O is at the edges | | ✅ | ✅ |

---

## 1. App factory + dependency injection

**Problem.** If the app is a global object that reads global config, every test shares state and nothing can be swapped.

```python
def build_app(db_path=":memory:"):
    app = FastAPI()
    app.state.repo = Repo(db_path)

    def repo(request: Request):
        return request.app.state.repo

    @app.get("/orders/{oid}")
    async def read(oid: str, r: Repo = Depends(repo)):
        return r.get(oid)
    return app

client = TestClient(build_app())        # a brand-new app and an empty database, per test
```

**Seen in:** all three (`build_app` / `Watcher(...)` receive their collaborators as arguments).
**Don't overdo it:** for a 40-line script, plain functions are better than a container of factories.

## 2. Validation at the edge

**Problem.** Bugs multiply when every function re-checks its input "just in case".

```python
class OrderIn(BaseModel):
    customer: str = Field(min_length=1, max_length=60)
    items: list[str] = Field(min_length=1, max_length=20)
```

Validate once where data enters (HTTP body, CSV row, **LLM reply**), then trust the types inside. FastAPI answers `422` with the exact failing fields for free.
**Seen in:** `OrderIn`, `MoveIn`; `clean()` and `LLMClassifier` (model output is *untrusted input*).
**Don't:** validate deep inside the core again. It hides where the real boundary is.

## 3. Repository

**Problem.** SQL scattered through handlers makes every database change a treasure hunt.

```python
class Repo:
    def __init__(self, path): self.db = sqlite3.connect(path)
    def get(self, oid):        return self.db.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
    def create(self, order):   ...
```

Handlers say `repo.get(id)`; they never say `SELECT`. Moving to PostgreSQL means rewriting **one class**. Tests can pass a fake repo that stores into a dict.
**Seen in:** `Repo` (blueprint 1), `store()` / `report()` (blueprint 2).
**Don't:** build a generic "repository framework". One concrete class per aggregate is enough.

## 4. State machine

**Problem.** Status columns drift into impossible combinations (*delivered* → *preparing*).

```python
NEXT = {"placed": {"accepted", "cancelled"}, "accepted": {"preparing", "cancelled"}, "preparing": {"delivered"}}
def can_move(old, new): return new in NEXT.get(old, set())
```

A dictionary of sets can be read by a product manager, tested exhaustively and drawn as a diagram. Return `409` when a move is illegal.
**Seen in:** `Status` + `NEXT`; the circuit breaker is a three-state machine (closed / open / half-open).
**Don't:** use it for two states. A boolean is fine.

## 5. Idempotency

**Problem.** Networks retry. Without protection, retries create duplicates (two pizzas, two charges).

```python
row = db.execute("SELECT * FROM orders WHERE idem_key=?", (key,)).fetchone()
if row:
    return row            # same request, same answer, no second order
```

Two flavours: an **idempotency key** supplied by the client (APIs), and an **upsert** keyed by a natural id (batch jobs).

```sql
INSERT INTO tickets VALUES(...) ON CONFLICT(id) DO UPDATE SET label = excluded.label;
```

**Seen in:** `Idempotency-Key` (1), `ON CONFLICT` upsert (2).
**Rule of thumb:** anything that can be retried or re-run **must** be idempotent.

## 6. Pub/Sub (observer)

**Problem.** The code that changes an order should not know about WebSockets, e-mail or analytics.

```python
class Hub:
    def __init__(self): self.watchers = {}
    def subscribe(self, key):
        q = asyncio.Queue(maxsize=100); self.watchers.setdefault(key, set()).add(q); return q
    def publish(self, key, event):
        for q in list(self.watchers.get(key, ())):
            try: q.put_nowait(event)
            except asyncio.QueueFull: pass            # slow listener: drop, never stall the publisher
```

**Seen in:** `Hub` (1); the `Notifier` list in the watcher is the same idea with a plain loop (3).
**Limit:** in-memory pub/sub only works inside one process. For several servers, put Redis or a message broker behind the same two methods.

## 7. Pipeline of generators

**Problem.** Loading a whole file into a list makes memory grow with the data.

```python
def stage_a(rows):
    for r in rows:
        yield transform(r)

result = store(stage_c(stage_b(stage_a(read_rows(text)))))
```

Each stage handles one item and passes it on. Stages are tiny, testable in isolation, and the final line reads like the architecture diagram.
**Seen in:** `read_rows → clean → label → store` (2).
**Gotcha:** a generator can be consumed **once**; if you need two passes, build a list on purpose.

## 8. Strategy via `typing.Protocol`

**Problem.** `if provider == "a": ... elif provider == "b": ...` grows forever.

```python
class Notifier(Protocol):
    def send(self, title: str, body: str) -> None: ...

class ConsoleNotifier:
    def send(self, title, body):
        print(title, body)

class WebhookNotifier:
    def send(self, title, body):
        requests.post(URL, json={"text": title + body})
```

Anything with the right methods fits. No base class, no registration.
**Seen in:** `Classifier` (2), `Notifier` (3).

## 9. Adapter + fallback chain

**Problem.** An AI vendor changes its API, goes down, or costs too much.

```python
for c in [RuleClassifier(), LLMClassifier(client)]:          # cheapest first
    try:
        label, conf = c.classify(text)
    except Exception:
        stats[f"{c.name}_failed"] += 1
        continue
    if conf >= 0.7:
        return label
return "other"                                              # safe default: a human will look
```

The **adapter** (`LLMClassifier`) keeps vendor details in one class. The **chain** guarantees an answer. Always record *who decided* (`source`).
**Seen in:** blueprint 2. (This very portal uses the same idea for its tutor: Cursor → Claude → GPT → offline.)

## 10. Retry with exponential backoff + jitter

**Problem.** Transient errors (timeouts, 429, 503) usually vanish on the second try, but instant retries make outages worse.

```python
def retry(times=3, base=0.2, sleep=time.sleep):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            for attempt in range(1, times + 1):
                try:
                    return fn(*a, **kw)
                except TransientError:
                    if attempt == times: raise
                    sleep(base * 2 ** (attempt - 1) + random.random() * base)
        return wrapper
    return decorate
```

Retry **only** errors that can heal. Never retry a `ValueError` or a `400`.
**Seen in:** `@retry` (2).

## 11. Circuit breaker

**Problem.** A dead dependency plus a retry loop equals a self-inflicted outage.

```python
def allow(self, now): return self.opened_at is None or now - self.opened_at >= self.cool_off
def record(self, ok, now):
    if ok: self.failures, self.opened_at = 0, None
    else:
        self.failures += 1
        if self.failures >= self.max_failures: self.opened_at = now
```

After N failures, **stop calling** for a cool-off, then let one probe through (half-open).
**Seen in:** `Breaker` (3).

## 12. Plugin registry

**Problem.** Every new feature means editing the engine's `if/elif` chain.

```python
CHECKS = {}
def check(kind):
    def register(fn):
        CHECKS[kind] = fn
        return fn
    return register

@check("price")
def price_check(target, fetch): ...

CHECKS[target["kind"]](target, fetch)       # the engine never changes
```

**Seen in:** `@check(...)` (3). Same trick as Flask `@app.route`, pytest `@fixture`, Click `@command`.

## 13. Injected clock and network

**Problem.** Code that calls `time.time()` and `requests.get()` directly can only be tested slowly, with the internet.

```python
def tick(self, now): ...                  # time comes in as a parameter
Watcher(targets, fetch=fake_fetch)        # so does the network
retry(sleep=lambda s: None)               # and sleeping
```

**Result:** forty simulated minutes run in milliseconds. If a test needs `time.sleep`, the design is asking to be refactored.
**Seen in:** all three (`sleep=`, `ai=`, `fetch=`, `now`).

## 14. Atomic persistence

**Problem.** A crash while writing leaves a half-written, unreadable file.

```python
fd, tmp = tempfile.mkstemp(dir=path.parent)
with os.fdopen(fd, "w") as fh:
    json.dump(state, fh)
os.replace(tmp, path)                     # swap in one atomic step
```

**Seen in:** `save_state` (3). Databases give you this for free through transactions (`with db:`), as in blueprint 1.

## 15. Alert on transitions

**Problem.** A monitor that says "still down" every minute gets muted, then missed.

```python
if old == value:
    return                                # unchanged: silence
if breaker.just_opened:
    alert("payments-api is failing")      # once
```

Notify on *edges* (up→down, down→up, price dropped), keep *levels* for dashboards.
**Seen in:** `Watcher.compare` and the breaker alerts (3).

## 16. Functional core, imperative shell

**Problem.** Business rules tangled with I/O cannot be tested without a database and network.

```python
def priority_of(ticket):                  # pure: no I/O, same input -> same output
    return "high" if re.search(r"urgent|twice|locked out", ticket.text, re.I) else "normal"
```

Keep decisions in pure functions; keep reading, writing and calling at the edges. Your best tests will be one-liners against the core.
**Seen in:** `priority_of`, `can_move`, `price_check`'s parsing, `Breaker.allow`.

---

## Which pattern for which smell?

| You notice... | Reach for |
|---|---|
| "if provider == ..." growing | Strategy / Protocol (8), Plugin registry (12) |
| duplicate rows after a retry | Idempotency (5) |
| a status column with impossible values | State machine (4) |
| tests need the internet or `sleep` | Injected clock/network (13) |
| outage made worse by your own retries | Backoff (10) + Circuit breaker (11) |
| memory grows with file size | Generators (7) |
| SQL in handlers | Repository (3) |
| alerts everyone mutes | Alert on transitions (15) |
| "what if the AI is wrong or down?" | Adapter + fallback chain (9), validation (2) |
| state file sometimes corrupt | Atomic persistence (14) |

## Where these show up in real products

| Product you know | Patterns underneath |
|---|---|
| Food delivery / ride-hailing | state machine (4), pub/sub (6), idempotency (5) |
| Payments (Stripe-style) | idempotency (5), state machine (4), retries (10), validation (2) |
| Slack / chat | pub/sub (6), WebSockets, fallback transports |
| Data platforms and ML pipelines | generators (7), idempotent upserts (5), adapters (9), golden-set tests |
| Monitoring (Datadog / Pingdom-style) | scheduler tick, breaker (11), alert on transitions (15), plugins (12) |
| Anything with "AI inside" | adapter + fallback (9), validate model output (2), cost guard (rules first) |
