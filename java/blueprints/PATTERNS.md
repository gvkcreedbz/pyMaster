# Pattern catalog — the reusable shapes behind real Java back-ends

> Frameworks come and go; these shapes don't. Each pattern below is **small**, shows up in the three blueprints, and is something you can drop into your own project tomorrow. Everything is plain **Java 21** (records, sealed interfaces, enums, lambdas, streams, `java.util.concurrent`, `java.time`, `java.nio.file`) — no framework needed.
> **How to read an entry:** the *problem* it solves → the *Java shape* (copy it) → *where you've seen it* → *when NOT to use it*.

## The map

| # | Pattern | One-line idea | [Order tracker](#/blueprints/java-live-order-tracker) | [Ticket triage](#/blueprints/java-ticket-triage-pipeline) | [Site watcher](#/blueprints/java-site-watcher) |
|---|---|---|:-:|:-:|:-:|
| 1 | App factory + dependency injection | build the app from a method; pass collaborators in | ✅ | ✅ | ✅ |
| 2 | Validation at the edge | bad data dies at the border | ✅ | ✅ | |
| 3 | Repository | one class owns all SQL | ✅ | ✅ | |
| 4 | State machine | a table of legal moves | ✅ | | ✅ (breaker) |
| 5 | Idempotency | doing it twice = doing it once | ✅ | ✅ | |
| 6 | Pub/Sub (observer) | publishers don't know their listeners | ✅ | | ✅ |
| 7 | Pipeline of streams | stream rows through stages | | ✅ | |
| 8 | Strategy via an `interface` | swap behaviour without a class tree | | ✅ | ✅ |
| 9 | Adapter + fallback chain | hide the vendor, never depend on one | | ✅ | |
| 10 | Retry with backoff + jitter | try again, politely | | ✅ | |
| 11 | Circuit breaker | stop calling what is clearly down | | | ✅ |
| 12 | Plugin registry | register a lambda, add a feature | | | ✅ |
| 13 | Injected clock and network | make time and I/O parameters | ✅ | ✅ | ✅ |
| 14 | Atomic persistence | write to a temp file, then swap | | | ✅ |
| 15 | Alert on transitions | speak only when something changed | | | ✅ |
| 16 | Functional core, imperative shell | rules are pure, I/O is at the edges | | ✅ | ✅ |

---

## 1. App factory + dependency injection

**Problem.** If the app is a global singleton that reads global config, every test shares state and nothing can be swapped.

```java
static HttpServer buildApp(OrderRepo repo) throws IOException {
    var server = HttpServer.create(new InetSocketAddress(0), 0);
    server.createContext("/orders/", ex -> {
        var id = ex.getRequestURI().getPath().substring("/orders/".length());
        var found = repo.get(id);
        var body = found.map(Order::toString).orElse("not found").getBytes(StandardCharsets.UTF_8);
        ex.sendResponseHeaders(found.isPresent() ? 200 : 404, body.length);
        try (var out = ex.getResponseBody()) {
            out.write(body);
        }
    });
    return server;
}
```

```java
var app = buildApp(new InMemoryOrderRepo());     // a brand-new server and an empty store, per test
```

`new InetSocketAddress(0)` asks the OS for a free port, so tests never fight over `8080`. `OrderRepo` is pattern 3. Spring does the same wiring for you with constructor injection; the idea is identical — **collaborators arrive as arguments, never through `static` fields**.

**Seen in:** all three (`buildApp(...)` / `new Watcher(...)` receive their collaborators as arguments). Course: Day 19 (constructors), Day 30 (`HttpServer`).
**Don't overdo it:** for a 40-line program, plain methods are better than a container of factories and `@Inject` annotations.

## 2. Validation at the edge

**Problem.** Bugs multiply when every method re-checks its input "just in case".

```java
record OrderIn(String customer, List<String> items) {
    OrderIn {                                        // compact constructor = the border guard
        if (customer == null || customer.isBlank() || customer.length() > 60) {
            throw new IllegalArgumentException("customer must be 1-60 characters");
        }
        if (items == null || items.isEmpty() || items.size() > 20) {
            throw new IllegalArgumentException("items must hold 1-20 entries");
        }
        items = List.copyOf(items);                  // defensive copy: immutable from here on
    }
}
```

Validate once where data enters (HTTP body, CSV row, **LLM reply**), then trust the types inside: an `OrderIn` that exists is a valid `OrderIn`. The handler catches `IllegalArgumentException` once and answers `422` with the message — Java gives you the guard; the status code is one `catch` at the border.
**Seen in:** `OrderIn`, `MoveIn`; `clean()` and `LlmClassifier` (model output is *untrusted input*). Course: Day 13 (records), Day 17 (exceptions).
**Don't:** validate deep inside the core again. It hides where the real boundary is.

## 3. Repository

**Problem.** SQL scattered through handlers makes every database change a treasure hunt.

```java
record Order(String id, String customer, String status) {}

interface OrderRepo {
    Optional<Order> get(String id);
    void save(Order order);
}

final class JdbcOrderRepo implements OrderRepo {
    private final Connection db;

    JdbcOrderRepo(Connection db) { this.db = db; }

    public Optional<Order> get(String id) {
        try (var ps = db.prepareStatement("SELECT id, customer, status FROM orders WHERE id = ?")) {
            ps.setString(1, id);
            try (var rs = ps.executeQuery()) {
                return rs.next()
                        ? Optional.of(new Order(rs.getString(1), rs.getString(2), rs.getString(3)))
                        : Optional.empty();
            }
        } catch (SQLException e) {
            throw new IllegalStateException(e);
        }
    }

    public void save(Order order) {
        var sql = "INSERT OR REPLACE INTO orders(id, customer, status) VALUES(?, ?, ?)";
        try (var ps = db.prepareStatement(sql)) {
            ps.setString(1, order.id());
            ps.setString(2, order.customer());
            ps.setString(3, order.status());
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new IllegalStateException(e);
        }
    }
}

final class InMemoryOrderRepo implements OrderRepo {
    private final Map<String, Order> rows = new ConcurrentHashMap<>();

    public Optional<Order> get(String id) { return Optional.ofNullable(rows.get(id)); }

    public void save(Order order) { rows.put(order.id(), order); }
}
```

Handlers say `repo.get(id)`; they never say `SELECT`. `Optional` makes "not found" part of the type instead of a surprise `null`. Moving to PostgreSQL means rewriting **one class**, and tests pass the in-memory fake. Always use `PreparedStatement` placeholders (`?`) — never glue user text into SQL.
**Seen in:** `OrderRepo` (blueprint 1), `store()` / `report()` (blueprint 2). Course: Day 28 (JDBC).
**Don't:** build a generic "repository framework". One concrete class per aggregate is enough.

## 4. State machine

**Problem.** Status columns drift into impossible combinations (*delivered* → *preparing*).

```java
enum Status {
    PLACED, ACCEPTED, PREPARING, DELIVERED, CANCELLED;

    private static final Map<Status, Set<Status>> NEXT = Map.of(
            PLACED, EnumSet.of(ACCEPTED, CANCELLED),
            ACCEPTED, EnumSet.of(PREPARING, CANCELLED),
            PREPARING, EnumSet.of(DELIVERED));

    boolean canMoveTo(Status next) {
        return NEXT.getOrDefault(this, Set.of()).contains(next);
    }
}
```

A map of sets inside an `enum` can be read by a product manager, tested exhaustively (loop over `Status.values()` twice) and drawn as a diagram. States with no entry (`DELIVERED`, `CANCELLED`) are terminal. Return `409` when a move is illegal. A `switch` expression over the enum is the alternative when each state needs its own logic — the compiler then forces you to handle every state.
**Seen in:** `Status` + `NEXT`; the circuit breaker is a three-state machine (closed / open / half-open). Course: Day 20 (`enum`, `sealed`).
**Don't:** use it for two states. A `boolean` is fine.

## 5. Idempotency

**Problem.** Networks retry. Without protection, retries create duplicates (two pizzas, two charges).

```java
static final class IdempotentPlacer {
    private final Map<String, Order> byKey = new ConcurrentHashMap<>();

    Order place(String idempotencyKey, Supplier<Order> create) {
        return byKey.computeIfAbsent(idempotencyKey, k -> create.get());   // atomic: call 2 gets answer 1
    }
}
```

Same request, same answer, no second order. `computeIfAbsent` is atomic, so two simultaneous retries still create only one order. Two flavours: an **idempotency key** supplied by the client (APIs), and an **upsert** keyed by a natural id (batch jobs).

```sql
INSERT INTO tickets VALUES(...) ON CONFLICT(id) DO UPDATE SET label = excluded.label;
```

In a real database the final guard is a `UNIQUE` index on the key — it protects you even across several server processes.
**Seen in:** `Idempotency-Key` header (1), `ON CONFLICT` upsert (2).
**Rule of thumb:** anything that can be retried or re-run **must** be idempotent.

## 6. Pub/Sub (observer)

**Problem.** The code that changes an order should not know about SSE streams, e-mail or analytics.

```java
static final class Hub<E> {
    private final Map<String, Set<BlockingQueue<E>>> watchers = new ConcurrentHashMap<>();

    BlockingQueue<E> subscribe(String key) {
        var q = new ArrayBlockingQueue<E>(100);
        watchers.computeIfAbsent(key, k -> new CopyOnWriteArraySet<>()).add(q);
        return q;
    }

    void unsubscribe(String key, BlockingQueue<E> q) {
        Optional.ofNullable(watchers.get(key)).ifPresent(set -> set.remove(q));
    }

    void publish(String key, E event) {
        for (var q : watchers.getOrDefault(key, Set.of())) {
            q.offer(event);          // queue full? drop it: a slow listener must never stall the publisher
        }
    }
}
```

Each SSE connection owns one queue and a thread that drains it; `publish` never waits for anybody. `offer` (not `put`) is the whole "drop, never stall" rule.
**Seen in:** `Hub` (1); the `Notifier` list in the watcher is the same idea with a plain loop (3). Course: Day 22 (generics), Day 27 (`HttpServer`).
**Limit:** in-memory pub/sub only works inside one JVM. For several servers, put Redis or a message broker behind the same three methods.

## 7. Pipeline of streams

**Problem.** Loading a whole file into a list makes memory grow with the data.

```java
record Row(String id, String text) {}

record Ticket(String id, String text, String label) {}

static Stream<Row> readRows(String csvText) {
    return csvText.lines()
            .skip(1)
            .map(line -> line.split(",", 2))
            .filter(p -> p.length == 2)
            .map(p -> new Row(p[0].trim(), p[1].trim()));
}

static Stream<Row> clean(Stream<Row> rows) {
    return rows.filter(r -> !r.text().isBlank());
}

static Stream<Ticket> label(Stream<Row> rows) {
    return rows.map(r -> new Ticket(r.id(), r.text(), r.text().contains("refund") ? "billing" : "other"));
}

static int store(Stream<Ticket> tickets, Consumer<Ticket> sink) {
    var stored = new AtomicInteger();
    tickets.forEach(t -> {
        sink.accept(t);
        stored.incrementAndGet();
    });
    return stored.get();
}

static int demoP07(String text, List<Ticket> db) {
    return store(label(clean(readRows(text))), db::add);
}
```

Streams are lazy: nothing runs until the terminal operation (`forEach` in `store`), and then each row travels through *every* stage before the next row is read. Stages are tiny, testable in isolation, and the last line reads like the architecture diagram. For a real file use `Files.lines(path)` inside a try-with-resources so the file is closed.
**Seen in:** `readRows → clean → label → store` (2). Course: Day 12 (streams), Day 25-26 (`Collectors`, reporting).
**Gotcha:** a `Stream` can be consumed **once** (a second use throws `IllegalStateException`); if you need two passes, collect to a list on purpose or build a new stream from a `Supplier<Stream<...>>`.

## 8. Strategy via an `interface`

**Problem.** `if (provider.equals("a")) ... else if (provider.equals("b")) ...` grows forever.

```java
@FunctionalInterface
interface Notifier {
    void send(String title, String body);
}

record ConsoleNotifier() implements Notifier {
    public void send(String title, String body) {
        System.out.println(title + " " + body);
    }
}

record WebhookNotifier(HttpClient http, URI url) implements Notifier {
    public void send(String title, String body) {
        var json = "{\"text\":\"" + title + " " + body + "\"}";
        var request = HttpRequest.newBuilder(url).POST(BodyPublishers.ofString(json)).build();
        try {
            http.send(request, BodyHandlers.discarding());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }
}

static void demoP08() {
    Notifier quiet = (title, body) -> { };           // a lambda is a strategy too
    quiet.send("t", "b");
}
```

Anything that implements the one method fits — and because the interface has a single method, a **lambda** fits too. No base class, no registry, no `if` chain. (When the set of strategies is *closed* and you want the compiler to check you handled all of them, use a `sealed interface` — see pattern 9.)
**Seen in:** `Classifier` (2), `Notifier` (3). Course: Day 20 (interfaces), Day 12 (lambdas), Day 22 (`Function`, `Predicate`).
**Don't:** invent an interface for something with a single implementation and no test double.

## 9. Adapter + fallback chain

**Problem.** An AI vendor changes its API, goes down, or costs too much.

```java
record Verdict(String label, double confidence) {}

sealed interface Classifier permits RuleClassifier, LlmClassifier {
    String name();

    Verdict classify(String text) throws Exception;
}

record RuleClassifier() implements Classifier {
    public String name() { return "rules"; }

    public Verdict classify(String text) {
        return text.toLowerCase().contains("refund") ? new Verdict("billing", 0.9) : new Verdict("other", 0.3);
    }
}

interface LlmClient {
    String complete(String prompt) throws IOException;
}

record LlmClassifier(LlmClient client) implements Classifier {
    public String name() { return "llm"; }

    public Verdict classify(String text) throws IOException {
        String[] parts = client.complete("Classify: " + text).split(",");      // vendor detail lives here only
        return new Verdict(parts[0].trim(), Double.parseDouble(parts[1].trim()));   // untrusted: parse, then trust
    }
}

static String decide(List<Classifier> chain, String text, Map<String, Integer> stats) {
    for (Classifier c : chain) {                                  // cheapest first
        try {
            Verdict v = c.classify(text);
            if (v.confidence() >= 0.7) {
                return v.label();
            }
        } catch (Exception e) {
            stats.merge(c.name() + "_failed", 1, Integer::sum);
        }
    }
    return "other";                                               // safe default: a human will look
}
```

The **adapter** (`LlmClassifier`) keeps vendor details in one record. The **chain** guarantees an answer: a thrown exception *or* a low confidence moves on to the next link. Always record *who decided* (`source`). `sealed` means a new classifier must be added to the `permits` list on purpose, so every `switch` over classifiers is re-checked by the compiler.
**Seen in:** blueprint 2. (This very portal uses the same idea for its tutor: Cursor → Claude → GPT → offline.) Course: Day 20 (`sealed`), Day 17 (exceptions).

## 10. Retry with exponential backoff + jitter

**Problem.** Transient errors (timeouts, 429, 503) usually vanish on the second try, but instant retries make outages worse.

```java
static class TransientException extends RuntimeException {
    TransientException(String message) { super(message); }
}

static <T> T retry(int times, Duration base, LongConsumer sleepMillis, Supplier<T> action) {
    for (int attempt = 1; ; attempt++) {
        try {
            return action.get();
        } catch (TransientException e) {
            if (attempt == times) {
                throw e;
            }
            long backoff = base.toMillis() * (1L << (attempt - 1));
            long jitter = (long) (ThreadLocalRandom.current().nextDouble() * base.toMillis());
            sleepMillis.accept(backoff + jitter);
        }
    }
}

static void realSleep(long millis) {
    try {
        Thread.sleep(millis);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        throw new IllegalStateException(e);
    }
}

static String demoP10() {
    return retry(3, Duration.ofMillis(200), Catalog::realSleep, () -> "ok");
}
```

Waits grow 200 ms, 400 ms, 800 ms … plus a random extra, so a thousand clients do not all knock again at the same instant. Retry **only** errors that can heal (`TransientException`). Never retry an `IllegalArgumentException` or a `400`.
**Seen in:** `retry(...)` (2). Course: Day 17 (custom exceptions), Day 11 (recursion/loops).

## 11. Circuit breaker

**Problem.** A dead dependency plus a retry loop equals a self-inflicted outage.

```java
static final class Breaker {
    private final int maxFailures;
    private final Duration coolOff;
    private int failures;
    private Instant openedAt;                              // null means closed

    Breaker(int maxFailures, Duration coolOff) {
        this.maxFailures = maxFailures;
        this.coolOff = coolOff;
    }

    synchronized boolean allow(Instant now) {
        return openedAt == null || !now.isBefore(openedAt.plus(coolOff));    // closed, or cool-off over: probe
    }

    synchronized boolean record(boolean ok, Instant now) {                   // true only when it just opened
        if (ok) {
            failures = 0;
            openedAt = null;
            return false;
        }
        boolean wasClosed = openedAt == null;
        failures++;
        if (failures >= maxFailures) {
            openedAt = now;
        }
        return wasClosed && openedAt != null;
    }
}
```

After N failures, **stop calling** for a cool-off, then let one probe through (half-open). The caller passes `now` in (pattern 13), so a test can jump 31 seconds without waiting. `synchronized` keeps the counters honest when several threads share one breaker.
**Seen in:** `Breaker` (3). Course: Day 18 (`java.time`), Day 19 (encapsulation).

## 12. Plugin registry

**Problem.** Every new feature means editing the engine's `if/else` chain.

```java
record Target(String kind, String url) {}

record CheckResult(boolean ok, String detail) {}

@FunctionalInterface
interface Check {
    CheckResult run(Target target, Function<String, String> fetch);
}

static final class Checks {
    private static final Map<String, Check> REGISTRY = new ConcurrentHashMap<>();

    static void register(String kind, Check check) {
        REGISTRY.put(kind, check);
    }

    static CheckResult run(Target target, Function<String, String> fetch) {
        Check check = REGISTRY.get(target.kind());
        if (check == null) {
            throw new IllegalArgumentException("unknown check kind: " + target.kind());
        }
        return check.run(target, fetch);                          // the engine never changes
    }
}

static void demoP12() {
    Checks.register("price", (target, fetch) -> new CheckResult(fetch.apply(target.url()).contains("99"), "price"));
    Checks.run(new Target("price", "https://example.com"), url -> "price 99");
}
```

Java has no decorators, so the registry is a `Map` from a name to a lambda, and "adding a feature" is one `register(...)` call. For plugins that ship as separate JARs, the JDK's `ServiceLoader` is the same trick with the map filled from `META-INF/services`.
**Seen in:** `Checks.register("price", ...)` (3). Same idea as Spring's `@Component` scanning, JUnit's extensions, and servlet filters.
**Don't:** use a registry for two fixed behaviours; a `switch` is clearer.

## 13. Injected clock and network

**Problem.** Code that calls `Instant.now()`, `Thread.sleep()` and `HttpClient.send()` directly can only be tested slowly, with the internet.

```java
static final class FakeClock extends Clock {
    private Instant now;

    FakeClock(Instant start) { this.now = start; }

    void advance(Duration d) { now = now.plus(d); }

    @Override public Instant instant() { return now; }

    @Override public ZoneId getZone() { return ZoneOffset.UTC; }

    @Override public Clock withZone(ZoneId zone) { return this; }
}

static final class Watcher {
    private final Function<String, String> fetch;
    private final Clock clock;
    private final List<String> log = new ArrayList<>();

    Watcher(Function<String, String> fetch, Clock clock) {
        this.fetch = fetch;
        this.clock = clock;
    }

    void tick() {
        log.add(clock.instant() + " " + fetch.apply("https://example.com").length());
    }

    int ticks() { return log.size(); }
}

static int demoP13() {
    var clock = new FakeClock(Instant.parse("2026-01-01T00:00:00Z"));
    var watcher = new Watcher(url -> "<html>price 99</html>", clock);              // fake network
    for (int i = 0; i < 40; i++) {
        watcher.tick();
        clock.advance(Duration.ofMinutes(1));                                        // forty minutes, instantly
    }
    retry(3, Duration.ofMillis(200), ms -> { }, () -> "no real sleeping");           // and no sleeping
    return watcher.ticks();
}
```

In production you pass `Clock.systemUTC()` and a real `HttpClient`-backed function; in tests a `FakeClock` and a lambda. `java.time.Clock` was designed for exactly this.
**Result:** forty simulated minutes run in milliseconds. If a test needs `Thread.sleep`, the design is asking to be refactored.
**Seen in:** all three (`Clock`, `fetch`, the `sleepMillis` parameter of `retry`). Course: Day 18 (`java.time`), Day 24 (testing).

## 14. Atomic persistence

**Problem.** A crash while writing leaves a half-written, unreadable file.

```java
static void saveState(Path path, String json) throws IOException {
    Path tmp = Files.createTempFile(path.toAbsolutePath().getParent(), "state", ".tmp");   // same folder = same disk
    try {
        Files.writeString(tmp, json);
        Files.move(tmp, path, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
    } finally {
        Files.deleteIfExists(tmp);                           // already gone after a successful move
    }
}
```

Readers see either the old file or the new one, never half of each. The temp file must live in the **same directory**, otherwise the move is a copy and stops being atomic. If the power cut itself matters, also call `FileChannel.force(true)` before the move.
**Seen in:** `saveState` (3). Databases give you this for free through transactions (`connection.setAutoCommit(false)` … `commit()`), as in blueprint 1. Course: Day 15 (`java.nio.file`).

## 15. Alert on transitions

**Problem.** A monitor that says "still down" every minute gets muted, then missed.

```java
static final class TransitionAlerts {
    private final Map<String, String> last = new HashMap<>();
    private final Notifier notifier;

    TransitionAlerts(Notifier notifier) { this.notifier = notifier; }

    void observe(String target, String value) {
        String old = last.put(target, value);
        if (Objects.equals(old, value)) {
            return;                                          // unchanged: silence
        }
        notifier.send(target, old == null ? "now " + value : old + " -> " + value);
    }
}

static void demoP15(Breaker breaker, Notifier notifier) {
    if (breaker.record(false, Instant.now())) {              // true only on the closed -> open edge
        notifier.send("payments-api", "is failing");         // once
    }
}
```

Notify on *edges* (up→down, down→up, price dropped), keep *levels* for dashboards. `Map.put` returns the previous value, which makes "what was it before?" a one-liner.
**Seen in:** `Watcher.compare` and the breaker alerts (3).

## 16. Functional core, imperative shell

**Problem.** Business rules tangled with I/O cannot be tested without a database and network.

```java
private static final Pattern URGENT = Pattern.compile("urgent|twice|locked out", Pattern.CASE_INSENSITIVE);

static String priorityOf(Ticket ticket) {                    // pure: no I/O, same input -> same output
    return URGENT.matcher(ticket.text()).find() ? "high" : "normal";
}
```

Keep decisions in pure methods (static, no fields, no I/O); keep reading, writing and calling at the edges. Records help: immutable inputs cannot be changed behind your back. Your best tests will be one-liners against the core.
**Seen in:** `priorityOf`, `Status.canMoveTo`, `price` check's parsing, `Breaker.allow`. Course: Day 23 (regex, clean code).

---

## Which pattern for which smell?

| You notice... | Reach for |
|---|---|
| `if (provider.equals(...))` growing | Strategy / interface (8), Plugin registry (12) |
| duplicate rows after a retry | Idempotency (5) |
| a status column with impossible values | State machine (4) |
| tests need the internet or `Thread.sleep` | Injected clock/network (13) |
| outage made worse by your own retries | Backoff (10) + Circuit breaker (11) |
| memory grows with file size | Streams (7) |
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
| Data platforms and ML pipelines | streams (7), idempotent upserts (5), adapters (9), golden-set tests |
| Monitoring (Datadog / Pingdom-style) | scheduler tick, breaker (11), alert on transitions (15), plugins (12) |
| Anything with "AI inside" | adapter + fallback (9), validate model output (2), cost guard (rules first) |
