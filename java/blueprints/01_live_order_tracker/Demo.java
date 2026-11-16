/*
 * Runs the whole Live Order Tracker (real HttpServer on a free port, real HttpClient) and narrates what happens.
 * Run:  javac -d out *.java  &&  java -cp out Demo
 * The printed text contains no ports, timestamps or random ids, so two runs print exactly the same thing.
 */

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Stream;

public class Demo {
    /** What one HTTP call returned. A record: three fields, zero boilerplate. */
    record Reply(int status, String body, String contentType) {
        @SuppressWarnings("unchecked")
        Map<String, Object> obj() {
            return (Map<String, Object>) Json.parse(body);
        }
    }

    private static HttpClient http;
    private static String base;
    /** The SSE listener hands every event it printed to the main thread through this queue (keeps the output ordered). */
    private static final BlockingQueue<String> seen = new LinkedBlockingQueue<>();

    static void say(String title) {
        System.out.println("\n== " + title);
    }

    static Reply call(String method, String path, String jsonBody, String... headers) throws Exception {
        HttpRequest.Builder b = HttpRequest.newBuilder(URI.create(base + path)).timeout(Duration.ofSeconds(5));
        b.method(method, jsonBody == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(jsonBody));
        if (jsonBody != null) b.header("Content-Type", "application/json");
        for (int i = 0; i < headers.length; i += 2) b.header(headers[i], headers[i + 1]);
        HttpResponse<String> r = http.send(b.build(), HttpResponse.BodyHandlers.ofString());
        return new Reply(r.statusCode(), r.body(), r.headers().firstValue("Content-Type").orElse(""));
    }

    /** The "customer's browser": opens the SSE stream and prints every event until the server closes it. */
    static void listen(String path) {
        try {
            HttpRequest req = HttpRequest.newBuilder(URI.create(base + path)).header("Accept", "text/event-stream").build();
            HttpResponse<Stream<String>> res = http.send(req, HttpResponse.BodyHandlers.ofLines());
            String[] type = {""};
            try (Stream<String> lines = res.body()) {
                lines.forEach(line -> {
                    if (line.startsWith("event:")) {
                        type[0] = line.substring(6).trim();
                    } else if (line.startsWith("data:")) {
                        Map<?, ?> data = (Map<?, ?>) Json.parse(line.substring(5).trim());
                        String status = String.valueOf(((Map<?, ?>) data.get("order")).get("status"));
                        if (type[0].equals("snapshot")) {
                            List<String> past = new ArrayList<>();
                            for (Object h : (List<?>) data.get("history")) past.add(String.valueOf(((Map<?, ?>) h).get("status")));
                            System.out.println("  [sse] snapshot  status=" + status + "  history=" + past);
                        } else {
                            System.out.println("  [sse] " + String.format("%-9s", type[0]) + " status=" + status);
                        }
                        seen.add(status);
                    }
                });
            }
            seen.add("closed");                                   // main prints the verdict: keeps the output ordered
        } catch (Exception e) {
            seen.add("error: " + e);
        }
    }

    static String awaitEvent() throws InterruptedException {
        String s = seen.poll(5, TimeUnit.SECONDS);
        if (s == null || s.startsWith("error")) throw new IllegalStateException("SSE listener: " + s);
        return s;
    }

    static void run() throws Exception {
        // Dependency injection in action: sequential ids and a fake clock make the whole run reproducible.
        AtomicInteger nextId = new AtomicInteger();
        AtomicLong fakeClock = new AtomicLong(1_000);
        OrderRepository repo = new InMemoryOrderRepository(() -> "order-" + nextId.incrementAndGet(), () -> fakeClock.addAndGet(10));
        Hub hub = new Hub();

        try (App app = Server.buildApp(repo, hub, 0);
             HttpClient client = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build()) {
            http = client;
            base = "http://127.0.0.1:" + app.port();

            say("1. place an order (with an Idempotency-Key)");
            String body = Json.write(Json.obj("customer", "Asha", "items", List.of("pizza", "cola")));
            Reply first = call("POST", "/orders", body, "Idempotency-Key", "abc-1");
            String oid = (String) first.obj().get("id");
            System.out.println(first.status() + " " + oid + " " + first.obj().get("status"));

            say("2. the phone app retries the same request (bad network): no duplicate order");
            Reply again = call("POST", "/orders", body, "Idempotency-Key", "abc-1");
            System.out.println(again.status() + " same id? " + again.obj().get("id").equals(oid));

            say("3. validation at the edge, and unknown orders");
            Reply bad = call("POST", "/orders", Json.write(Json.obj("customer", "", "items", List.of())));
            System.out.println(bad.status() + " invalid fields: " + bad.obj().get("fields"));
            Reply missing = call("GET", "/orders/nope", null);
            System.out.println(missing.status() + " " + missing.obj().get("error"));

            say("4. a customer watches live over Server-Sent Events while the kitchen moves the order");
            Thread listener = Thread.ofPlatform().name("sse-listener").daemon().start(() -> listen("/orders/" + oid + "/events"));
            awaitEvent();                                                        // the snapshot: we are connected
            String[] moves = {"accepted", null, null, null};                     // first move names its target, the rest just "advance"
            for (String target : moves) {
                Reply r = call("POST", "/orders/" + oid + "/advance", target == null ? null : Json.write(Json.obj("status", target)));
                String pushed = awaitEvent();                                    // ...and the customer sees it instantly
                System.out.println(String.format("  kitchen -> %-17s http %d   customer screen got: %s",
                        r.obj().get("status"), r.status(), pushed));
            }
            awaitEvent();                                                        // "closed"
            listener.join(5_000);
            System.out.println("  [sse] server closed the stream after the final state (no leaked connection)");
            boolean clean = false;
            for (int i = 0; i < 100 && !(clean = hub.watcherCount() == 0); i++) Thread.sleep(20);
            System.out.println("  hub watchers left after the stream ended: " + (clean ? 0 : hub.watcherCount()));

            say("5. illegal moves are refused by the state machine");
            Reply illegal = call("POST", "/orders/" + oid + "/advance", Json.write(Json.obj("status", "preparing")));
            System.out.println(illegal.status() + " " + illegal.obj().get("error"));
            Reply teleport = call("POST", "/orders/" + oid + "/advance", Json.write(Json.obj("status", "teleported")));
            System.out.println(teleport.status() + " " + teleport.obj().get("error"));
            String second = (String) call("POST", "/orders", Json.write(Json.obj("customer", "Ravi", "items", List.of("burger")))).obj().get("id");
            Reply skip = call("POST", "/orders/" + second + "/advance", Json.write(Json.obj("status", "delivered")));
            System.out.println(skip.status() + " " + skip.obj().get("error"));

            say("6. two kitchen taps at the same time: exactly one wins");
            Map<Integer, Long> tally = new TreeMap<>();
            try (ExecutorService pool = Executors.newFixedThreadPool(8)) {
                CountDownLatch go = new CountDownLatch(1);
                List<Future<Integer>> results = new ArrayList<>();
                for (int i = 0; i < 8; i++) {
                    results.add(pool.submit(() -> {
                        go.await();
                        return call("POST", "/orders/" + second + "/advance", Json.write(Json.obj("status", "accepted"))).status();
                    }));
                }
                go.countDown();
                for (Future<Integer> f : results) tally.merge(f.get(10, TimeUnit.SECONDS), 1L, Long::sum);
            }
            System.out.println("  8 simultaneous taps -> " + tally);

            say("7. the audit trail comes for free");
            Reply hist = call("GET", "/orders/" + oid + "/history", null);
            List<String> steps = new ArrayList<>();
            for (Object h : (List<?>) hist.obj().get("history")) steps.add(String.valueOf(((Map<?, ?>) h).get("status")));
            System.out.println(String.join(" -> ", steps));
            Reply whole = call("GET", "/orders/" + oid, null);
            System.out.println("GET /orders/{id} -> " + whole.status() + " status=" + whole.obj().get("status")
                    + " entries=" + ((List<?>) whole.obj().get("history")).size());

            say("8. pub/sub never waits for a slow listener (a queue with room for 2 gets 5 events)");
            Hub tiny = new Hub(2);
            try (Hub.Subscription slow = tiny.subscribe("x")) {
                Order sample = new Order("x", "Asha", List.of("pizza"), Status.ACCEPTED, null, 0);
                int delivered = 0;
                for (int i = 0; i < 5; i++) delivered += tiny.publish("x", new Event.StatusChanged(sample));
                System.out.println("  delivered " + delivered + ", dropped " + (5 - delivered) + ", queued " + slow.queue().size());
            }
            System.out.println("  watchers after close: " + tiny.watcherCount());

            say("9. the single-page front end is served too");
            Reply page = call("GET", "/", null);
            System.out.println("GET / -> " + page.status() + " " + page.contentType().split(";")[0]
                    + ", opens an EventSource: " + page.body().contains("new EventSource"));

            say("10. clean shutdown");
        }                                                                        // closes the client, then server + threads
        boolean quiet = false;
        for (int i = 0; i < 100 && !(quiet = liveThreads() == 0); i++) Thread.sleep(20);
        System.out.println("non-daemon threads left running: " + (quiet ? 0 : liveThreads()));
    }

    static long liveThreads() {
        return Thread.getAllStackTraces().keySet().stream()
                .filter(t -> t.isAlive() && !t.isDaemon() && t != Thread.currentThread()).count();
    }

    public static void main(String[] args) {
        try {
            run();
        } catch (Throwable t) {
            System.err.println("DEMO FAILED: " + t);
            t.printStackTrace();
            System.exit(1);
        }
    }
}
