/*
 * Live Order Tracker (Java 21 twin of the FastAPI blueprint): the heart of every delivery / ride / booking app.
 *
 *   Browser / HttpClient  <--HTTP + Server-Sent Events-->  HttpServer  <-->  OrderRepository (in memory)
 *                                                              |
 *                                                              +--> Hub (pub/sub): pushes every change to whoever watches that order
 *
 * Run for real:   javac -d out *.java  &&  java -cp out Server        then open http://127.0.0.1:8000/
 * Run the demo:   java -cp out Demo                                   (starts its own server on a free port)
 *
 * Only the JDK is used: com.sun.net.httpserver, java.util.concurrent, records, sealed interfaces, enums, text blocks.
 */

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;
import java.util.function.Supplier;

// ---- 1. DOMAIN: a state machine in one enum -------------------------------------------------------------------
enum Status {
    PLACED, ACCEPTED, PREPARING, OUT_FOR_DELIVERY, DELIVERED, CANCELLED;

    /** The ONLY legal moves; everything else is a bug or an attack. A switch expression must cover every constant. */
    Set<Status> next() {
        return switch (this) {
            case PLACED -> EnumSet.of(ACCEPTED, CANCELLED);
            case ACCEPTED -> EnumSet.of(PREPARING, CANCELLED);
            case PREPARING -> EnumSet.of(OUT_FOR_DELIVERY);
            case OUT_FOR_DELIVERY -> EnumSet.of(DELIVERED);
            case DELIVERED, CANCELLED -> EnumSet.noneOf(Status.class);
        };
    }

    boolean canMoveTo(Status target) {
        return next().contains(target);
    }

    boolean isFinal() {
        return next().isEmpty();
    }

    /** The "happy path" successor used when the client says "advance" without naming a target. */
    Optional<Status> happyNext() {
        return next().stream().filter(s -> s != CANCELLED).findFirst();
    }

    /** The name used on the wire: "out_for_delivery". */
    String wire() {
        return name().toLowerCase(Locale.ROOT);
    }

    static Optional<Status> parse(String wire) {
        return Arrays.stream(values()).filter(s -> s.wire().equals(wire)).findFirst();
    }
}

// ---- 2. DTOs: records are immutable data carriers (equals / hashCode / toString for free) ----------------------
record Order(String id, String customer, List<String> items, Status status, String idemKey, long created) {
    Order {
        items = List.copyOf(items);                       // compact constructor: defensive copy, the record stays immutable
    }

    Order withStatus(Status next) {
        return new Order(id, customer, items, next, idemKey, created);
    }

    Map<String, Object> toJson() {
        return Json.obj("id", id, "customer", customer, "items", items, "status", status.wire(), "created", created);
    }
}

record HistoryEntry(Status status, long at) {
    Map<String, Object> toJson() {
        return Json.obj("status", status.wire(), "at", at);
    }
}

/** Validation at the edge: the one place that looks at raw, untrusted data. */
record OrderIn(String customer, List<String> items) {
    static OrderIn parse(Object json) {
        if (!(json instanceof Map<?, ?> m)) throw new ValidationException(List.of("body"));
        List<String> bad = new ArrayList<>();
        String customer = null;
        if (m.get("customer") instanceof String s && !s.isBlank() && s.length() <= 60) customer = s;
        else bad.add("customer");
        List<String> items = new ArrayList<>();
        if (m.get("items") instanceof List<?> l && !l.isEmpty() && l.size() <= 20
                && l.stream().allMatch(x -> x instanceof String t && !t.isBlank())) {
            for (Object x : l) items.add((String) x);
        } else {
            bad.add("items");
        }
        if (!bad.isEmpty()) throw new ValidationException(bad);
        return new OrderIn(customer, items);
    }
}

final class ValidationException extends RuntimeException {
    private final List<String> fields;

    ValidationException(List<String> fields) {
        this("validation failed", fields);
    }

    ValidationException(String message, List<String> fields) {
        super(message);
        this.fields = List.copyOf(fields);
    }

    List<String> fields() {
        return fields;
    }
}

/** An error with a status code; the handler turns it into {"error": "..."}. */
final class HttpError extends RuntimeException {
    final int status;

    HttpError(int status, String message) {
        super(message);
        this.status = status;
    }
}

// ---- 3. REPOSITORY: the only code that knows how orders are stored --------------------------------------------
record Created(Order order, boolean created) {}

interface OrderRepository {
    Optional<Order> get(String id);

    /** The same idempotency key always returns the same order (safe retries). */
    Created create(OrderIn in, String idemKey);

    /** Compare-and-set: moves the order only if it is still in the `expected` status. Empty = somebody else won. */
    Optional<Order> transition(String id, Status expected, Status next);

    List<HistoryEntry> history(String id);
}

/** Swap this for JDBC by writing one new class; nothing else in the app changes. Thread-safe: one lock guards all maps. */
final class InMemoryOrderRepository implements OrderRepository {
    private final Object lock = new Object();
    private final Map<String, Order> orders = new HashMap<>();
    private final Map<String, String> byKey = new HashMap<>();
    private final Map<String, List<HistoryEntry>> history = new HashMap<>();
    private final Supplier<String> ids;
    private final LongSupplier clock;

    InMemoryOrderRepository() {
        this(() -> UUID.randomUUID().toString().substring(0, 8), System::currentTimeMillis);
    }

    /** Injected id generator and clock (pattern 13): tests and the demo make them deterministic. */
    InMemoryOrderRepository(Supplier<String> ids, LongSupplier clock) {
        this.ids = ids;
        this.clock = clock;
    }

    @Override
    public Optional<Order> get(String id) {
        synchronized (lock) {
            return Optional.ofNullable(orders.get(id));
        }
    }

    @Override
    public Created create(OrderIn in, String idemKey) {
        String key = (idemKey == null || idemKey.isBlank()) ? null : idemKey;
        synchronized (lock) {                                    // check-then-insert must be one atomic step
            if (key != null && byKey.containsKey(key)) return new Created(orders.get(byKey.get(key)), false);
            String id = ids.get();
            long now = clock.getAsLong();
            Order order = new Order(id, in.customer(), in.items(), Status.PLACED, key, now);
            orders.put(id, order);
            if (key != null) byKey.put(key, id);
            List<HistoryEntry> h = new ArrayList<>();
            h.add(new HistoryEntry(Status.PLACED, now));
            history.put(id, h);
            return new Created(order, true);
        }
    }

    @Override
    public Optional<Order> transition(String id, Status expected, Status next) {
        synchronized (lock) {
            Order current = orders.get(id);
            if (current == null || current.status() != expected) return Optional.empty();
            Order moved = current.withStatus(next);
            orders.put(id, moved);
            history.get(id).add(new HistoryEntry(next, clock.getAsLong()));   // append-only audit trail
            return Optional.of(moved);
        }
    }

    @Override
    public List<HistoryEntry> history(String id) {
        synchronized (lock) {
            return List.copyOf(history.getOrDefault(id, List.of()));          // a snapshot copy, never the live list
        }
    }
}

// ---- 4. PUB/SUB: how one change reaches many open browser tabs -----------------------------------------------
/** What travels through the Hub. Sealed: the compiler knows every kind of event, so every switch must handle all. */
sealed interface Event permits Event.Snapshot, Event.StatusChanged {
    record Snapshot(Order order, List<HistoryEntry> history) implements Event {}

    record StatusChanged(Order order) implements Event {}

    Order order();

    default String name() {
        return switch (this) {
            case Snapshot s -> "snapshot";
            case StatusChanged c -> "status";
        };
    }

    default Map<String, Object> toJson() {
        return switch (this) {
            case Snapshot s -> Json.obj("type", "snapshot", "order", s.order().toJson(),
                    "history", s.history().stream().map(HistoryEntry::toJson).toList());
            case StatusChanged c -> Json.obj("type", "status", "order", c.order().toJson());
        };
    }
}

/** Each watcher owns a bounded queue. Publishing never waits for a slow watcher. */
final class Hub {
    private final Map<String, Set<BlockingQueue<Event>>> watchers = new ConcurrentHashMap<>();
    private final int capacity;

    Hub() {
        this(100);
    }

    Hub(int capacity) {
        this.capacity = capacity;
    }

    /** Close the subscription (try-with-resources) or memory leaks one queue per visit. */
    record Subscription(Hub hub, String key, BlockingQueue<Event> queue) implements AutoCloseable {
        @Override
        public void close() {
            hub.unsubscribe(key, queue);
        }
    }

    Subscription subscribe(String key) {
        BlockingQueue<Event> q = new ArrayBlockingQueue<>(capacity);
        watchers.compute(key, (k, set) -> {                      // atomic with unsubscribe's compute: no lost watcher
            Set<BlockingQueue<Event>> s = set == null ? new CopyOnWriteArraySet<>() : set;
            s.add(q);
            return s;
        });
        return new Subscription(this, key, q);
    }

    private void unsubscribe(String key, BlockingQueue<Event> q) {
        watchers.computeIfPresent(key, (k, set) -> {
            set.remove(q);
            return set.isEmpty() ? null : set;                   // forget keys nobody listens to
        });
    }

    /** Returns how many watchers got the event. A full queue means a stuck client: drop, never stall the publisher. */
    int publish(String key, Event event) {
        int sent = 0;
        for (BlockingQueue<Event> q : watchers.getOrDefault(key, Set.of())) {
            if (q.offer(event)) sent++;
        }
        return sent;
    }

    int watcherCount() {
        return watchers.values().stream().mapToInt(Set::size).sum();
    }
}

// ---- 5. SERVICE: the rules, with no HTTP in sight (functional core) --------------------------------------------
sealed interface Outcome permits Outcome.Ok, Outcome.NotFound, Outcome.Illegal {
    record Ok(Order order) implements Outcome {}

    record NotFound() implements Outcome {}

    record Illegal(String message) implements Outcome {}
}

final class OrderService {
    private final OrderRepository repo;
    private final Hub hub;

    OrderService(OrderRepository repo, Hub hub) {            // dependency injection: collaborators come in as arguments
        this.repo = repo;
        this.hub = hub;
    }

    Outcome advance(String id, Optional<Status> target) {
        Optional<Order> found = repo.get(id);
        if (found.isEmpty()) return new Outcome.NotFound();
        Status old = found.get().status();
        Optional<Status> to = target.or(old::happyNext);
        if (to.isEmpty()) return new Outcome.Illegal("order is " + old.wire() + ": no further moves");
        if (!old.canMoveTo(to.get())) {
            return new Outcome.Illegal("cannot go from " + old.wire() + " to " + to.get().wire());
        }
        Optional<Order> moved = repo.transition(id, old, to.get());
        if (moved.isEmpty()) return new Outcome.Illegal("order changed concurrently, read it again and retry");
        hub.publish(id, new Event.StatusChanged(moved.get()));   // fan-out to every open tab
        return new Outcome.Ok(moved.get());
    }
}

// ---- 6. HTTP LAYER: thin handlers around the service ----------------------------------------------------------
final class Api implements HttpHandler {
    private static final int MAX_BODY = 64 * 1024;

    private final OrderRepository repo;
    private final Hub hub;
    private final OrderService service;
    private final long keepAliveMillis;

    Api(OrderRepository repo, Hub hub, long keepAliveMillis) {
        this.repo = repo;
        this.hub = hub;
        this.service = new OrderService(repo, hub);
        this.keepAliveMillis = keepAliveMillis;
    }

    @Override
    public void handle(HttpExchange ex) throws IOException {
        try {
            route(ex);
        } catch (HttpError e) {
            json(ex, e.status, Json.obj("error", e.getMessage()));
        } catch (ValidationException e) {
            json(ex, 422, Json.obj("error", e.getMessage(), "fields", e.fields()));
        } catch (Json.ParseException e) {
            json(ex, 400, Json.obj("error", "malformed JSON: " + e.getMessage()));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();                  // server is shutting down
        } catch (IOException e) {
            // the client went away mid-response: nothing to tell anyone
        } catch (RuntimeException e) {
            json(ex, 500, Json.obj("error", "internal error"));
        } finally {
            ex.close();
        }
    }

    private void route(HttpExchange ex) throws IOException, InterruptedException {
        String method = ex.getRequestMethod();
        List<String> p = Arrays.stream(ex.getRequestURI().getPath().split("/")).filter(s -> !s.isEmpty()).toList();
        if (p.isEmpty()) {
            requireMethod(method, "GET");
            page(ex);
        } else if (p.equals(List.of("orders"))) {
            requireMethod(method, "POST");
            place(ex);
        } else if (p.size() == 2 && p.get(0).equals("orders")) {
            requireMethod(method, "GET");
            read(ex, p.get(1));
        } else if (p.size() == 3 && p.get(0).equals("orders")) {
            String id = p.get(1);
            switch (p.get(2)) {
                case "advance" -> {
                    requireMethod(method, "POST");
                    advance(ex, id);
                }
                case "history" -> {
                    requireMethod(method, "GET");
                    history(ex, id);
                }
                case "events" -> {
                    requireMethod(method, "GET");
                    events(ex, id);
                }
                default -> throw new HttpError(404, "no such route");
            }
        } else {
            throw new HttpError(404, "no such route");
        }
    }

    private static void requireMethod(String actual, String wanted) {
        if (!wanted.equals(actual)) throw new HttpError(405, "method not allowed, use " + wanted);
    }

    // POST /orders  (+ Idempotency-Key header)
    private void place(HttpExchange ex) throws IOException {
        OrderIn in = OrderIn.parse(Json.parse(body(ex)));
        Created c = repo.create(in, ex.getRequestHeaders().getFirst("Idempotency-Key"));
        ex.getResponseHeaders().add("Location", "/orders/" + c.order().id());
        json(ex, c.created() ? 201 : 200, c.order().toJson());   // 200 = "I already did this": same answer, no duplicate
    }

    // GET /orders/{id}
    private void read(HttpExchange ex, String id) throws IOException {
        Order order = repo.get(id).orElseThrow(() -> new HttpError(404, "no such order"));
        Map<String, Object> out = new LinkedHashMap<>(order.toJson());
        out.put("history", repo.history(id).stream().map(HistoryEntry::toJson).toList());
        json(ex, 200, out);
    }

    // GET /orders/{id}/history
    private void history(HttpExchange ex, String id) throws IOException {
        if (repo.get(id).isEmpty()) throw new HttpError(404, "no such order");
        json(ex, 200, Json.obj("id", id, "history", repo.history(id).stream().map(HistoryEntry::toJson).toList()));
    }

    // POST /orders/{id}/advance   body optional: {"status": "preparing"}; no body = the next step of the happy path
    private void advance(HttpExchange ex, String id) throws IOException {
        String raw = body(ex);
        Optional<Status> target = Optional.empty();
        if (!raw.isBlank()) {
            if (!(Json.parse(raw) instanceof Map<?, ?> m)) throw new ValidationException(List.of("body"));
            if (m.get("status") != null) {
                String wire = String.valueOf(m.get("status"));
                target = Optional.of(Status.parse(wire).orElseThrow(
                        () -> new ValidationException("unknown status '" + wire + "'", List.of("status"))));
            }
        }
        switch (service.advance(id, target)) {                   // exhaustive over the sealed Outcome
            case Outcome.Ok ok -> json(ex, 200, ok.order().toJson());
            case Outcome.NotFound nf -> throw new HttpError(404, "no such order");
            case Outcome.Illegal bad -> throw new HttpError(409, bad.message());
        }
    }

    // GET /orders/{id}/events   (Server-Sent Events: one long-lived HTTP response that the server keeps writing to)
    private void events(HttpExchange ex, String id) throws IOException, InterruptedException {
        if (repo.get(id).isEmpty()) throw new HttpError(404, "no such order");
        try (Hub.Subscription sub = hub.subscribe(id)) {          // subscribe FIRST so no change slips between snapshot and live
            Order order = repo.get(id).orElseThrow();
            ex.getResponseHeaders().add("Content-Type", "text/event-stream; charset=utf-8");
            ex.getResponseHeaders().add("Cache-Control", "no-cache");
            ex.sendResponseHeaders(200, 0);                      // 0 = chunked: length unknown, stream until we stop
            OutputStream out = ex.getResponseBody();
            sendEvent(out, new Event.Snapshot(order, repo.history(id)));
            boolean done = order.status().isFinal();
            while (!done) {
                Event e = sub.queue().poll(keepAliveMillis, TimeUnit.MILLISECONDS);
                if (e == null) {
                    write(out, ": keepalive\n\n");               // a comment line: keeps proxies open, detects dead clients
                    continue;
                }
                sendEvent(out, e);
                done = e.order().status().isFinal();
            }
        }                                                        // always unsubscribes, even when the client vanished
    }

    private static void sendEvent(OutputStream out, Event e) throws IOException {
        write(out, "event: " + e.name() + "\ndata: " + Json.write(e.toJson()) + "\n\n");
    }

    private static void write(OutputStream out, String text) throws IOException {
        out.write(text.getBytes(StandardCharsets.UTF_8));
        out.flush();
    }

    private static String body(HttpExchange ex) throws IOException {
        byte[] bytes = ex.getRequestBody().readNBytes(MAX_BODY + 1);
        if (bytes.length > MAX_BODY) throw new HttpError(413, "body too large");
        return new String(bytes, StandardCharsets.UTF_8);
    }

    private static void json(HttpExchange ex, int status, Object payload) throws IOException {
        byte[] bytes = Json.write(payload).getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        ex.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = ex.getResponseBody()) {
            out.write(bytes);
        }
    }

    private void page(HttpExchange ex) throws IOException {
        byte[] bytes = PAGE.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
        ex.sendResponseHeaders(200, bytes.length);
        try (OutputStream out = ex.getResponseBody()) {
            out.write(bytes);
        }
    }

    // The front end: one HTML file in a text block, no build step. Plain JS opens an EventSource and repaints.
    private static final String PAGE = """
            <!doctype html><meta charset=utf-8><title>Live Order Tracker</title>
            <style>body{font:16px system-ui;max-width:520px;margin:40px auto;padding:0 16px}
            li{padding:6px 0}.now{font-weight:700}button{margin:4px 4px 0 0}</style>
            <h2>Live Order Tracker (Java)</h2>
            <form id=f><input id=who placeholder="your name" value="Asha"> <input id=items value="pizza, cola">
            <button>Place order</button></form><p id=info></p><ol id=steps></ol><div id=ops></div>
            <script>
            const ORDER = ["placed","accepted","preparing","out_for_delivery","delivered"];
            let oid = null, es = null;
            const paint = o => {
              info.textContent = "Order " + o.id + " for " + o.customer + ": " + o.items.join(", ");
              steps.innerHTML = ORDER.map(s => `<li class="${s === o.status ? "now" : ""}">${s === o.status ? "\u25B6 " : ""}${s}</li>`).join("");
              ops.innerHTML = ORDER.concat("cancelled").map(s => `<button data-s="${s}">${s}</button>`).join("");
            };
            ops.onclick = async e => { if (e.target.dataset.s) await fetch(`/orders/${oid}/advance`,
              {method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify({status: e.target.dataset.s})}); };
            f.onsubmit = async e => {
              e.preventDefault();
              const r = await fetch("/orders", {method: "POST", headers: {"content-type": "application/json"},
                body: JSON.stringify({customer: who.value, items: items.value.split(",").map(s => s.trim()).filter(Boolean)})});
              const o = await r.json();
              if (!r.ok) { info.textContent = JSON.stringify(o); return; }
              oid = o.id; paint(o);
              es?.close(); es = new EventSource("/orders/" + oid + "/events");
              es.addEventListener("snapshot", m => paint(JSON.parse(m.data).order));
              es.addEventListener("status", m => paint(JSON.parse(m.data).order));
              es.onerror = () => es.close();      // the server closes the stream after the final state
            };
            </script>""";
}

// ---- 7. THE APP FACTORY: every test (and the demo) builds its own clean server -------------------------------
/** A running app. AutoCloseable, so try-with-resources shuts the server and its threads down. */
record App(HttpServer http, ExecutorService pool) implements AutoCloseable {
    int port() {
        return http.getAddress().getPort();
    }

    @Override
    public void close() {
        http.stop(0);                                            // stops accepting, closes open connections
        pool.shutdownNow();                                      // interrupts SSE handlers waiting on their queue
        try {
            pool.awaitTermination(3, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

public class Server {
    /** buildApp(repo, hub, port): collaborators are arguments, nothing global. Port 0 = any free port. */
    static App buildApp(OrderRepository repo, Hub hub, int port) throws IOException {
        return buildApp(repo, hub, port, 15_000);
    }

    static App buildApp(OrderRepository repo, Hub hub, int port, long keepAliveMillis) throws IOException {
        HttpServer http = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), port), 0);
        AtomicInteger n = new AtomicInteger();
        ThreadFactory daemons = r -> {
            Thread t = new Thread(r, "tracker-worker-" + n.incrementAndGet());
            t.setDaemon(true);
            return t;
        };
        ExecutorService pool = Executors.newCachedThreadPool(daemons);   // one thread per open SSE stream is fine at this scale
        http.setExecutor(pool);
        http.createContext("/", new Api(repo, hub, keepAliveMillis));
        http.start();
        return new App(http, pool);
    }

    /** What `java -cp out Server` runs: the real app. Tests and the demo call buildApp() instead. */
    public static void main(String[] args) throws Exception {
        int port = args.length > 0 ? Integer.parseInt(args[0]) : 8000;
        try (App app = buildApp(new InMemoryOrderRepository(), new Hub(), port)) {
            System.out.println("Live Order Tracker on http://127.0.0.1:" + app.port() + "/   (Ctrl+C to stop)");
            new CountDownLatch(1).await();
        }
    }
}
