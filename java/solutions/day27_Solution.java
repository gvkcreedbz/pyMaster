// SOLUTION FILE - try the hint ladder first!
/* Day 27 - Practice: HTTP + JSON (no internet needed!)
 *
 * Run:  java Practice.java
 * The checks start a tiny web server on YOUR computer (127.0.0.1, a free port) and call it with
 * java.net.http.HttpClient. Fill in every TODO. The provided pieces (Json, obj, TestServer) are
 * explained in the lesson - read them, but you do not need to change them.
 */
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.StringJoiner;
import java.util.TreeMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongConsumer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

class Practice {

    /** One shared client for all requests (HTTP/1.1 keeps the tiny local server happy). */
    static final HttpClient CLIENT = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    record Weather(double temp, double wind, String time) {}

    record Book(String title, double price) {}

    // ---- provided: a tiny JSON reader/writer (same one as in Examples.java) ---------------------
    static final class Json {
        private final String s;
        private int i = 0;

        private Json(String s) {
            this.s = s;
        }

        /** JSON text -> Map (object), List (array), String, Long/Double (number), Boolean or null. */
        static Object parse(String text) {
            Json p = new Json(text);
            Object value = p.value();
            p.skipSpaces();
            if (p.i != text.length()) throw p.fail("extra text");
            return value;
        }

        /** Map / List / String / Number / Boolean / null -> JSON text. */
        static String write(Object v) {
            if (v == null) return "null";
            if (v instanceof String str) return quote(str);
            if (v instanceof Number || v instanceof Boolean) return v.toString();
            if (v instanceof Map<?, ?> map) {
                StringJoiner j = new StringJoiner(",", "{", "}");
                for (Map.Entry<?, ?> e : map.entrySet()) j.add(quote(String.valueOf(e.getKey())) + ":" + write(e.getValue()));
                return j.toString();
            }
            if (v instanceof Iterable<?> list) {
                StringJoiner j = new StringJoiner(",", "[", "]");
                for (Object item : list) j.add(write(item));
                return j.toString();
            }
            throw new IllegalArgumentException("cannot write " + v.getClass().getSimpleName());
        }

        /** "text" in double quotes, with " \ and new lines escaped. */
        static String quote(String text) {
            StringBuilder b = new StringBuilder("\"");
            for (char c : text.toCharArray()) {
                switch (c) {
                    case '"' -> b.append("\\\"");
                    case '\\' -> b.append("\\\\");
                    case '\n' -> b.append("\\n");
                    case '\r' -> b.append("\\r");
                    case '\t' -> b.append("\\t");
                    default -> {
                        if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
                        else b.append(c);
                    }
                }
            }
            return b.append('"').toString();
        }

        @SuppressWarnings("unchecked")
        static Map<String, Object> asObject(Object v) {
            return (Map<String, Object>) v;
        }

        @SuppressWarnings("unchecked")
        static List<Object> asArray(Object v) {
            return (List<Object>) v;
        }

        private IllegalArgumentException fail(String why) {
            return new IllegalArgumentException(why + " at position " + i);
        }

        private void skipSpaces() {
            while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++;
        }

        private void expect(char c) {
            if (i >= s.length() || s.charAt(i) != c) throw fail("expected '" + c + "'");
            i++;
        }

        private Object value() {
            skipSpaces();
            if (i >= s.length()) throw fail("unexpected end");
            return switch (s.charAt(i)) {
                case '{' -> object();
                case '[' -> array();
                case '"' -> string();
                case 't' -> word("true", Boolean.TRUE);
                case 'f' -> word("false", Boolean.FALSE);
                case 'n' -> word("null", null);
                default -> number();
            };
        }

        private Object word(String text, Object result) {
            if (!s.startsWith(text, i)) throw fail("unexpected character");
            i += text.length();
            return result;
        }

        private Map<String, Object> object() {
            Map<String, Object> map = new LinkedHashMap<>();
            expect('{');
            skipSpaces();
            if (i < s.length() && s.charAt(i) == '}') {
                i++;
                return map;
            }
            while (true) {
                skipSpaces();
                String key = string();
                skipSpaces();
                expect(':');
                map.put(key, value());
                skipSpaces();
                if (i < s.length() && s.charAt(i) == ',') {
                    i++;
                    continue;
                }
                expect('}');
                return map;
            }
        }

        private List<Object> array() {
            List<Object> list = new ArrayList<>();
            expect('[');
            skipSpaces();
            if (i < s.length() && s.charAt(i) == ']') {
                i++;
                return list;
            }
            while (true) {
                list.add(value());
                skipSpaces();
                if (i < s.length() && s.charAt(i) == ',') {
                    i++;
                    continue;
                }
                expect(']');
                return list;
            }
        }

        private String string() {
            expect('"');
            StringBuilder b = new StringBuilder();
            while (i < s.length() && s.charAt(i) != '"') {
                char c = s.charAt(i++);
                if (c != '\\') {
                    b.append(c);
                    continue;
                }
                if (i >= s.length()) throw fail("bad escape");
                char e = s.charAt(i++);
                switch (e) {
                    case 'n' -> b.append('\n');
                    case 't' -> b.append('\t');
                    case 'r' -> b.append('\r');
                    case 'b' -> b.append('\b');
                    case 'f' -> b.append('\f');
                    case 'u' -> {
                        b.append((char) Integer.parseInt(s.substring(i, i + 4), 16));
                        i += 4;
                    }
                    default -> b.append(e);
                }
            }
            expect('"');
            return b.toString();
        }

        private Number number() {
            int start = i;
            while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
            String t = s.substring(start, i);
            if (t.isEmpty()) throw fail("unexpected character '" + s.charAt(i) + "'");
            try {
                if (t.matches("-?\\d+")) return Long.valueOf(t);
                return Double.valueOf(t);
            } catch (NumberFormatException e) {
                i = start;
                throw fail("bad number");
            }
        }
    }

    /** obj("a", 1, "b", true) -> a Map that remembers the order (handy for building JSON). */
    static Map<String, Object> obj(Object... keysAndValues) {
        Map<String, Object> map = new LinkedHashMap<>();
        for (int k = 0; k < keysAndValues.length; k += 2) map.put((String) keysAndValues[k], keysAndValues[k + 1]);
        return map;
    }

    // ---------------------------------------------------------------------------
    // L1-1 | buildUrl   (Level 1 - Beginner)
    // Join a base URL and some query parameters (in the order of the map):
    //   buildUrl("https://api.x.com/search", {q=python, page=2})
    //       -> "https://api.x.com/search?q=python&page=2"
    // No parameters -> just the base. Values must be URL-encoded with URLEncoder.encode(text, UTF_8):
    //   {q="tea & coffee"} -> "...?q=tea+%26+coffee".   (Use String.valueOf(value) for numbers.)
    // ---------------------------------------------------------------------------
    static String buildUrl(String base, Map<String, Object> params) {
        // >>> SOLUTION stub: return null;
        if (params.isEmpty()) return base;
        StringJoiner query = new StringJoiner("&", base + "?", "");
        for (Map.Entry<String, Object> e : params.entrySet()) {
            query.add(URLEncoder.encode(e.getKey(), StandardCharsets.UTF_8) + "="
                    + URLEncoder.encode(String.valueOf(e.getValue()), StandardCharsets.UTF_8));
        }
        return query.toString();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | statusCategory   (Level 1 - Beginner)
    // Return "success" for 200-299, "client error" for 400-499, "server error" for 500-599,
    // and "other" for everything else (100, 301, ...).
    // ---------------------------------------------------------------------------
    static String statusCategory(int code) {
        // >>> SOLUTION stub: return null;
        if (code >= 200 && code <= 299) return "success";
        if (code >= 400 && code <= 499) return "client error";
        if (code >= 500 && code <= 599) return "server error";
        return "other";
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | jsonObject   (Level 1 - Beginner)
    // Write JSON by hand, once, so the magic is gone. Turn a FLAT map into JSON text, keeping
    // the map's order, with no spaces:
    //   {name=Pen, price=10.5, inStock=true, note=null} -> {"name":"Pen","price":10.5,"inStock":true,"note":null}
    // Strings get quotes (use Json.quote, which also escapes " and new lines); numbers, booleans
    // and null are written as they are. An empty map gives {}.
    // (Json.write(map) does the same - but build it yourself here with a StringJoiner.)
    // ---------------------------------------------------------------------------
    static String jsonObject(Map<String, Object> map) {
        // >>> SOLUTION stub: return null;
        StringJoiner json = new StringJoiner(",", "{", "}");
        for (Map.Entry<String, Object> e : map.entrySet()) {
            Object value = e.getValue();
            String text = value instanceof String s ? Json.quote(s) : String.valueOf(value);
            json.add(Json.quote(e.getKey()) + ":" + text);
        }
        return json.toString();
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | parseWeather   (Level 2 - Intermediate)
    // A weather API answers e.g.
    //   {"latitude": 18.5, "current": {"temperature_2m": 28.5, "wind_speed_10m": 12.3, "time": "2026-11-16T10:00"}}
    // Parse the text with Json.parse and return new Weather(temp, wind, time).
    // Careful: a number like 30 (no decimal point) is parsed as a Long, not a Double - cast to Number
    // and call .doubleValue(). Json.asObject(x) turns a parsed object into a Map<String, Object>.
    // ---------------------------------------------------------------------------
    static Weather parseWeather(String json) {
        // >>> SOLUTION stub: return null;
        Map<String, Object> data = Json.asObject(Json.parse(json));
        Map<String, Object> current = Json.asObject(data.get("current"));
        return new Weather(((Number) current.get("temperature_2m")).doubleValue(),
                ((Number) current.get("wind_speed_10m")).doubleValue(),
                (String) current.get("time"));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | fetchJson   (Level 2 - Intermediate)
    // GET the url with client.send(...). The request must
    //   * have a timeout of 10 seconds,
    //   * send the header  Accept: application/json,
    //   * and, when token is not null, also  Authorization: Bearer <token>.
    // Status 200 -> return Json.parse(body). Any other status -> throw new IOException("HTTP " + status).
    // ---------------------------------------------------------------------------
    static Object fetchJson(HttpClient client, String url, String token) throws IOException, InterruptedException {
        // >>> SOLUTION stub: return null;
        HttpRequest.Builder builder = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(10))
                .header("Accept", "application/json");
        if (token != null) builder.header("Authorization", "Bearer " + token);
        HttpResponse<String> response = client.send(builder.build(), HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200) throw new IOException("HTTP " + response.statusCode());
        return Json.parse(response.body());
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | fetchWithRetry   (Level 2 - Intermediate)
    // GET the url up to `attempts` times. A try FAILS when the network breaks (client.send throws
    // an IOException, e.g. the server is down) or the status is 500 or more.
    // After a failed try, if more tries remain, call sleeper.accept(1L << attemptNumber)
    // (attemptNumber starts at 0 -> sleeps of 1, 2, 4 ... seconds; the sleeper is a parameter so
    // tests do not really wait). A 4xx status is NOT retried: throw new IOException("HTTP " + status)
    // at once. Status 200 -> return Json.parse(body). Every try failed -> throw new IOException("giving up").
    // ---------------------------------------------------------------------------
    static Object fetchWithRetry(HttpClient client, String url, int attempts, LongConsumer sleeper)
            throws IOException, InterruptedException {
        // >>> SOLUTION stub: return null;
        for (int attempt = 0; attempt < attempts; attempt++) {
            int status = -1;
            String body = null;
            try {
                HttpRequest request = HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofSeconds(10)).build();
                HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
                status = response.statusCode();
                body = response.body();
            } catch (IOException networkProblem) {
                // status stays -1: counts as a failed try
            }
            if (status == 200) return Json.parse(body);
            if (status >= 400 && status < 500) throw new IOException("HTTP " + status);
            if (attempt < attempts - 1) sleeper.accept(1L << attempt);
        }
        throw new IOException("giving up");
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-4 | scrapeBooks   (Level 2 - Intermediate)
    // No API? Then the data sits inside HTML. Each book looks like
    //   <article class="book"><h3><a href="a.html" title="Full Title">Short...</a></h3>
    //     <p class="price">Rs 519.50</p></article>
    // Use a regex (Pattern + Matcher, with Pattern.DOTALL because the pieces may be on different
    // lines) and return a List<Book> in page order, price as a double. No books -> empty list.
    // ---------------------------------------------------------------------------
    static List<Book> scrapeBooks(String html) {
        // >>> SOLUTION stub: return List.of();
        Pattern card = Pattern.compile("title=\"([^\"]+)\".*?class=\"price\">Rs\\s*([\\d.]+)</p>", Pattern.DOTALL);
        Matcher m = card.matcher(html);
        List<Book> books = new ArrayList<>();
        while (m.find()) books.add(new Book(m.group(1), Double.parseDouble(m.group(2))));
        return books;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | postsPerUser   (Level 3 - Challenge)
    // GET <base>/posts - a JSON array like [{"userId": 2, "id": 1, "title": "..."}, ...].
    // Return how many posts each user wrote, as a Map<Integer, Integer> ordered by userId
    // (a TreeMap). You may reuse your fetchJson (token null). Json.asArray(x) gives a List<Object>.
    // ---------------------------------------------------------------------------
    static Map<Integer, Integer> postsPerUser(HttpClient client, String base) throws IOException, InterruptedException {
        // >>> SOLUTION stub: return null;
        Map<Integer, Integer> counts = new TreeMap<>();
        for (Object item : Json.asArray(fetchJson(client, base + "/posts", null))) {
            int userId = ((Number) Json.asObject(item).get("userId")).intValue();
            counts.merge(userId, 1, Integer::sum);
        }
        return counts;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | placeOrder   (Level 3 - Challenge)
    // POST <base>/orders with this JSON body (build it with obj(...) + Json.write):
    //   {"customer": "Asha", "items": [{"product": "Pen", "qty": 3}, {"product": "Notebook", "qty": 2}]}
    // The request needs the header  Content-Type: application/json  (the server answers 415 without it).
    // The server replies 201 and {"orderId": 1, "customer": "Asha", "total": 141.0}.
    // Return that total as a double. Any other status -> throw new IOException("HTTP " + status).
    // `items` maps product name -> quantity (in order).
    // ---------------------------------------------------------------------------
    static double placeOrder(HttpClient client, String base, String customer, Map<String, Integer> items)
            throws IOException, InterruptedException {
        // >>> SOLUTION stub: return 0;
        List<Object> lines = new ArrayList<>();
        for (Map.Entry<String, Integer> e : items.entrySet()) lines.add(obj("product", e.getKey(), "qty", e.getValue()));
        String body = Json.write(obj("customer", customer, "items", lines));
        HttpRequest request = HttpRequest.newBuilder(URI.create(base + "/orders"))
                .timeout(Duration.ofSeconds(10))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 201) throw new IOException("HTTP " + response.statusCode());
        return ((Number) Json.asObject(Json.parse(response.body())).get("total")).doubleValue();
        // <<< SOLUTION
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================

    /** A tiny web server on 127.0.0.1 + a free port, started just for the checks. */
    static final class TestServer implements AutoCloseable {
        final HttpServer server;
        final String base;
        final AtomicInteger hits = new AtomicInteger();
        private final int flakyFailures;
        private int nextOrderId = 1;

        TestServer(int flakyFailures) throws IOException {
            this.flakyFailures = flakyFailures;
            server = HttpServer.create(new InetSocketAddress(InetAddress.getByName("127.0.0.1"), 0), 0);
            server.createContext("/", this::handle);
            server.start();
            base = "http://127.0.0.1:" + server.getAddress().getPort();
        }

        @Override
        public void close() {
            server.stop(0);
        }

        private void handle(HttpExchange ex) throws IOException {
            hits.incrementAndGet();
            try {
                route(ex);
            } catch (RuntimeException e) {
                send(ex, 500, obj("error", String.valueOf(e)));
            }
        }

        private void route(HttpExchange ex) throws IOException {
            String method = ex.getRequestMethod();
            String path = ex.getRequestURI().getPath();
            if (method.equals("POST") && path.equals("/orders")) {
                postOrder(ex);
                return;
            }
            if (!method.equals("GET")) {
                send(ex, 405, obj("error", "method not allowed"));
                return;
            }
            switch (path) {
                case "/health" -> send(ex, 200, obj("status", "ok"));
                case "/weather" -> send(ex, 200, obj("latitude", 18.5, "longitude", 73.86,
                        "current", obj("temperature_2m", 28.5, "wind_speed_10m", 12.3, "time", "2026-11-16T10:00")));
                case "/posts" -> {
                    int[] users = {2, 1, 2, 3, 2, 1};
                    List<Object> posts = new ArrayList<>();
                    for (int k = 0; k < users.length; k++) posts.add(obj("userId", users[k], "id", k + 1, "title", "Post " + (k + 1)));
                    send(ex, 200, posts);
                }
                case "/headers" -> send(ex, 200, obj("accept", ex.getRequestHeaders().getFirst("Accept"),
                        "authorization", ex.getRequestHeaders().getFirst("Authorization")));
                case "/private" -> {
                    if ("Bearer s3cret".equals(ex.getRequestHeaders().getFirst("Authorization"))) send(ex, 200, obj("user", "asha"));
                    else send(ex, 401, obj("error", "unauthorized"));
                }
                case "/flaky" -> {
                    if (hits.get() <= flakyFailures) send(ex, 503, obj("error", "try again later"));
                    else send(ex, 200, obj("ok", 1));
                }
                default -> send(ex, 404, obj("error", "not found"));
            }
        }

        private void postOrder(HttpExchange ex) throws IOException {
            String type = ex.getRequestHeaders().getFirst("Content-Type");
            String body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            if (type == null || !type.startsWith("application/json")) {
                send(ex, 415, obj("error", "send application/json"));
                return;
            }
            Map<String, Double> prices = Map.of("Pen", 10.0, "Notebook", 55.5, "Backpack", 799.0);
            double total = 0;
            try {
                Map<String, Object> order = Json.asObject(Json.parse(body));
                for (Object line : Json.asArray(order.get("items"))) {
                    Map<String, Object> item = Json.asObject(line);
                    String product = (String) item.get("product");
                    if (!prices.containsKey(product)) {
                        send(ex, 400, obj("error", "unknown product: " + product));
                        return;
                    }
                    total += prices.get(product) * ((Number) item.get("qty")).intValue();
                }
                send(ex, 201, obj("orderId", nextOrderId++, "customer", order.get("customer"), "total", total));
            } catch (IllegalArgumentException | ClassCastException | NullPointerException bad) {
                send(ex, 400, obj("error", "bad order"));
            }
        }

        private static void send(HttpExchange ex, int status, Object json) throws IOException {
            byte[] bytes = Json.write(json).getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
            ex.sendResponseHeaders(status, bytes.length);
            try (OutputStream out = ex.getResponseBody()) {
                out.write(bytes);
            }
        }
    }

    /** Code that may throw checked exceptions (the checker turns a crash into a readable text). */
    interface Risky {
        Object get() throws Exception;
    }

    interface Scenario {
        Object run(TestServer server) throws Exception;
    }

    static Object attempt(Risky r) {
        try {
            return r.get();
        } catch (Exception e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
    }

    static Object serve(int flakyFailures, Scenario scenario) {
        try (TestServer server = new TestServer(flakyFailures)) {
            return scenario.run(server);
        } catch (Exception e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
    }

    /** A URL where nobody is listening (we grab a free port and close it again). */
    static String deadUrl() throws IOException {
        try (ServerSocket socket = new ServerSocket(0, 1, InetAddress.getByName("127.0.0.1"))) {
            return "http://127.0.0.1:" + socket.getLocalPort() + "/health";
        }
    }

    static String retryReport(String url, int attempts) {
        List<Long> sleeps = new ArrayList<>();
        Object result = attempt(() -> fetchWithRetry(CLIENT, url, attempts, sleeps::add));
        return result + " sleeps=" + sleeps;
    }

    static final String WEATHER = """
            {"latitude": 18.5, "current": {"temperature_2m": 28.5, "wind_speed_10m": 12.3, "time": "2026-11-16T10:00"}}""";

    static final String WEATHER_WHOLE = """
            {"current": {"temperature_2m": 30, "wind_speed_10m": 7, "time": "t"}}""";

    static final String BOOKS_HTML = """
            <section>
            <article class="book"><h3><a href="a.html" title="A Light in the Attic">A Light in the ...</a></h3>
              <div><p class="price">Rs 519.50</p></div></article>
            <article class="book"><h3><a href="b.html" title="Tipping the Velvet">Tipping the ...</a></h3>
              <div><p class="price">Rs 53.74</p></div></article>
            </section>""";

    public static void main(String[] args) {
        System.out.println("--- Day 27 checks ---");
        Checker.check("L1-1 buildUrl", () -> List.of(
                        buildUrl("https://api.x.com/search", obj("q", "python", "page", 2)),
                        buildUrl("https://x.com", obj()),
                        buildUrl("https://x.com/s", obj("q", "tea & coffee"))),
                List.of("https://api.x.com/search?q=python&page=2", "https://x.com", "https://x.com/s?q=tea+%26+coffee"));
        Checker.check("L1-2 statusCategory", () -> {
            List<String> out = new ArrayList<>();
            for (int code : new int[]{200, 201, 301, 404, 429, 500, 503, 100}) out.add(statusCategory(code));
            return out;
        }, List.of("success", "success", "other", "client error", "client error", "server error", "server error", "other"));
        Checker.check("L1-3 jsonObject", () -> List.of(
                        jsonObject(obj("name", "Pen", "price", 10.5, "inStock", true, "note", null)),
                        jsonObject(obj()),
                        jsonObject(obj("quote", "say \"hi\"\n"))),
                List.of("{\"name\":\"Pen\",\"price\":10.5,\"inStock\":true,\"note\":null}", "{}",
                        "{\"quote\":\"say \\\"hi\\\"\\n\"}"));
        Checker.check("L2-1 parseWeather", () -> parseWeather(WEATHER), new Weather(28.5, 12.3, "2026-11-16T10:00"));
        Checker.check("L2-1 parseWeather (whole numbers are Longs!)", () -> attempt(() -> parseWeather(WEATHER_WHOLE)),
                new Weather(30.0, 7.0, "t"));
        Checker.check("L2-2 fetchJson (200 -> parsed JSON)", () -> serve(0, s -> fetchJson(CLIENT, s.base + "/health", null)),
                obj("status", "ok"));
        Checker.check("L2-2 fetchJson sends Accept + Authorization headers",
                () -> serve(0, s -> fetchJson(CLIENT, s.base + "/headers", "abc")),
                obj("accept", "application/json", "authorization", "Bearer abc"));
        Checker.check("L2-2 fetchJson with the right token", () -> serve(0, s -> fetchJson(CLIENT, s.base + "/private", "s3cret")),
                obj("user", "asha"));
        Checker.check("L2-2 fetchJson 401 and 404 raise IOException", () -> serve(0, s -> List.of(
                        attempt(() -> fetchJson(CLIENT, s.base + "/private", "wrong")),
                        attempt(() -> fetchJson(CLIENT, s.base + "/nope", null)))),
                List.of("IOException: HTTP 401", "IOException: HTTP 404"));
        Checker.check("L2-3 retry recovers (2 failures, then success; sleeps 1s, 2s)",
                () -> serve(2, s -> retryReport(s.base + "/flaky", 3) + " hits=" + s.hits.get()),
                "{ok=1} sleeps=[1, 2] hits=3");
        Checker.check("L2-3 retry gives up after 3 failed tries",
                () -> serve(9, s -> retryReport(s.base + "/flaky", 3) + " hits=" + s.hits.get()),
                "IOException: giving up sleeps=[1, 2] hits=3");
        Checker.check("L2-3 retry does NOT repeat a 404",
                () -> serve(0, s -> retryReport(s.base + "/nope", 3) + " hits=" + s.hits.get()),
                "IOException: HTTP 404 sleeps=[] hits=1");
        Checker.check("L2-3 retry when the server is down", () -> attempt(() -> retryReport(deadUrl(), 3)),
                "IOException: giving up sleeps=[1, 2]");
        Checker.check("L2-4 scrapeBooks", () -> scrapeBooks(BOOKS_HTML),
                List.of(new Book("A Light in the Attic", 519.5), new Book("Tipping the Velvet", 53.74)));
        Checker.check("L2-4 scrapeBooks (no books)", () -> scrapeBooks("<p>nothing here</p>"), List.of());
        Checker.check("L3-1 postsPerUser", () -> serve(0, s -> String.valueOf(postsPerUser(CLIENT, s.base))), "{1=2, 2=3, 3=1}");
        Checker.check("L3-2 placeOrder (201 and the total)", () -> serve(0, s -> {
            Map<String, Integer> items = new LinkedHashMap<>();
            items.put("Pen", 3);
            items.put("Notebook", 2);
            return placeOrder(CLIENT, s.base, "Asha", items);
        }), 141.0);
        Checker.check("L3-2 placeOrder (unknown product -> HTTP 400)",
                () -> serve(0, s -> attempt(() -> placeOrder(CLIENT, s.base, "Ben", Map.of("Unicorn", 1)))),
                "IOException: HTTP 400");
        Checker.done();
    }
}

// ==== CHECKER-BEGIN (generated by _dev_tools/java_sync.py - do not edit) ====
final class Checker {
    private static int passed = 0, total = 0;

    /** Compare what your code produced with what we expect and print [PASS] / [FAIL]. */
    static void check(String name, java.util.function.Supplier<Object> fn, Object want) {
        Object got;
        boolean good;
        try {
            got = fn.get();
            good = same(got, want);
        } catch (Throwable e) {              // your code crashed: show why instead of stopping
            got = e.getClass().getSimpleName() + ": " + e.getMessage();
            good = false;
        }
        total++;
        if (good) passed++;
        System.out.println("[" + (good ? "PASS" : "FAIL") + "] " + name
                + (good ? "" : "  (got " + show(got) + ", want " + show(want) + ")"));
    }

    /** Everything that run() prints, as one string (new lines normalised to \n). */
    static String printed(Runnable run) {
        java.io.PrintStream old = System.out;
        java.io.ByteArrayOutputStream buf = new java.io.ByteArrayOutputStream();
        System.setOut(new java.io.PrintStream(buf, true, java.nio.charset.StandardCharsets.UTF_8));
        try {
            run.run();
        } finally {
            System.setOut(old);
        }
        return buf.toString(java.nio.charset.StandardCharsets.UTF_8).replace("\r\n", "\n");
    }

    /** Run fn while System.in contains text (to test code that uses Scanner). */
    static <T> T withInput(String text, java.util.function.Supplier<T> fn) {
        java.io.InputStream old = System.in;
        System.setIn(new java.io.ByteArrayInputStream(text.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        try {
            return fn.get();
        } finally {
            System.setIn(old);
        }
    }

    /** Print the final score line (the portal reads this). */
    static void done() {
        System.out.println("\nScore: " + passed + "/" + total + " checks passed");
    }

    private static boolean same(Object got, Object want) {
        if (got instanceof Number g && want instanceof Number w) {
            boolean floating = got instanceof Double || got instanceof Float || want instanceof Double || want instanceof Float;
            return floating ? Math.abs(g.doubleValue() - w.doubleValue()) < 1e-6 : g.longValue() == w.longValue();
        }
        return java.util.Objects.deepEquals(got, want);
    }

    private static String show(Object o) {
        if (o == null) return "null";
        if (o instanceof String s) {
            return "\"" + s.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t").replace("\"", "\\\"") + "\"";
        }
        if (o instanceof Object[] a) return java.util.Arrays.deepToString(a);
        if (o instanceof int[] a) return java.util.Arrays.toString(a);
        if (o instanceof long[] a) return java.util.Arrays.toString(a);
        if (o instanceof double[] a) return java.util.Arrays.toString(a);
        if (o instanceof char[] a) return java.util.Arrays.toString(a);
        if (o instanceof boolean[] a) return java.util.Arrays.toString(a);
        return String.valueOf(o);
    }
}
// ==== CHECKER-END ====
