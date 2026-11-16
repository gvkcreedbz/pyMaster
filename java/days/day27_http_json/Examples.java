/* Day 27 - Code along: your dashboard needs live data. Today the "internet" is a tiny server that
 * YOUR program starts on your own computer (127.0.0.1), so everything works offline and is repeatable.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * Parts 1-2 (Json, obj) are a ready-made JSON reader/writer: read them AFTER the code along.
 */
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
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
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

class Examples {
    // ---- part 1: a tiny JSON reader/writer (the Day 16 idea, now with Long/Double numbers) ----
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

    // ---- part 2: obj(...) builds a Map in a fixed order, handy for JSON
    /** obj("a", 1, "b", true) -> a Map that remembers the order (handy for building JSON). */
    static Map<String, Object> obj(Object... keysAndValues) {
        Map<String, Object> map = new LinkedHashMap<>();
        for (int k = 0; k < keysAndValues.length; k += 2) map.put((String) keysAndValues[k], keysAndValues[k + 1]);
        return map;
    }

    // ---- part 3: a tiny web server that lives only while this program runs ----
    static final AtomicInteger FLAKY_HITS = new AtomicInteger();

    static void sendText(HttpExchange ex, int status, String contentType, String text) throws IOException {
        byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", contentType);
        ex.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = ex.getResponseBody()) {
            out.write(bytes);
        }
    }

    static void sendJson(HttpExchange ex, int status, Object json) throws IOException {
        sendText(ex, status, "application/json; charset=utf-8", Json.write(json));
    }

    static void handle(HttpExchange ex) throws IOException {
        String method = ex.getRequestMethod();
        String path = ex.getRequestURI().getPath();
        if (method.equals("POST") && path.equals("/orders")) {
            String body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            Map<String, Object> order = Json.asObject(Json.parse(body));
            sendJson(ex, 201, obj("orderId", 1, "customer", order.get("customer"), "status", "received"));
            return;
        }
        switch (path) {
            case "/weather" -> sendJson(ex, 200, obj("latitude", 18.5, "longitude", 73.86,
                    "current", obj("temperature_2m", 28.5, "wind_speed_10m", 12.3, "time", "2026-11-16T10:00")));
            case "/search" -> sendJson(ex, 200, obj("query", ex.getRequestURI().getQuery()));   // text after "?", decoded
            case "/secret" -> {
                if ("Bearer s3cret".equals(ex.getRequestHeaders().getFirst("Authorization"))) {
                    sendJson(ex, 200, obj("user", "asha"));
                } else {
                    sendJson(ex, 401, obj("error", "unauthorized"));
                }
            }
            case "/flaky" -> {
                if (FLAKY_HITS.incrementAndGet() < 3) {
                    sendJson(ex, 503, obj("error", "try again later"));
                } else {
                    sendJson(ex, 200, obj("ok", 1));
                }
            }
            case "/shop" -> sendText(ex, 200, "text/html; charset=utf-8", """
                    <article class="book"><h3><a href="a.html" title="Masala Chai Book">Masala ...</a></h3>
                      <p class="price">Rs 249.00</p></article>
                    <article class="book"><h3><a href="b.html" title="Samosa Secrets">Samosa ...</a></h3>
                      <p class="price">Rs 199.50</p></article>""");
            default -> sendJson(ex, 404, obj("error", "not found"));
        }
    }

    public static void main(String[] args) throws Exception {
        // Port 0 = "pick any free port". 127.0.0.1 = this computer only, nobody else can reach it.
        HttpServer server = HttpServer.create(new InetSocketAddress(InetAddress.getByName("127.0.0.1"), 0), 0);
        server.createContext("/", Examples::handle);
        server.start();
        String base = "http://127.0.0.1:" + server.getAddress().getPort();
        System.out.println("Server started on this computer");
        try {
            demo(base);
        } finally {
            server.stop(0);
            System.out.println("Server stopped");
        }
    }

    // ---- part 4: the client side (this is what you will write in Practice.java) ----
    static void demo(String base) throws Exception {
        HttpClient client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(Duration.ofSeconds(5))
                .build();

        // ---- 1. GET: request -> response (status + headers + body) ----
        HttpRequest request = HttpRequest.newBuilder(URI.create(base + "/weather"))
                .timeout(Duration.ofSeconds(10))              // ALWAYS set a timeout
                .header("Accept", "application/json")
                .GET()
                .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println("Status: " + response.statusCode());                                       // 200
        System.out.println("Type: " + response.headers().firstValue("Content-Type").orElse("?"));    // application/json; charset=utf-8
        System.out.println("Body: " + response.body());

        // ---- 2. JSON text -> Map -> the fields you need ----
        Map<String, Object> data = Json.asObject(Json.parse(response.body()));
        Map<String, Object> current = Json.asObject(data.get("current"));
        double temp = ((Number) current.get("temperature_2m")).doubleValue();   // numbers come back as Long or Double
        System.out.println("Pune is " + temp + " C at " + current.get("time"));

        // ---- 3. Query parameters must be URL-encoded ----
        String url = base + "/search?q=" + URLEncoder.encode("tea & coffee", StandardCharsets.UTF_8) + "&page=2";
        System.out.println(url.substring(url.indexOf("/search")));                // /search?q=tea+%26+coffee&page=2
        HttpResponse<String> found = client.send(HttpRequest.newBuilder(URI.create(url)).build(), HttpResponse.BodyHandlers.ofString());
        System.out.println(found.body());                                          // {"query":"q=tea+&+coffee&page=2"} (in a query string + means a space)

        // ---- 4. A 404 is a normal answer, not an exception: ALWAYS look at the status ----
        HttpResponse<String> missing = client.send(HttpRequest.newBuilder(URI.create(base + "/nope")).build(),
                HttpResponse.BodyHandlers.ofString());
        System.out.println(missing.statusCode() + " -> " + (missing.statusCode() / 100 == 4 ? "client error (our mistake)" : "other"));

        // ---- 5. Secrets go into a header, never into code you share ----
        String token = "s3cret";    // in real life: System.getenv("API_TOKEN")
        for (String sent : new String[]{null, token}) {
            HttpRequest.Builder b = HttpRequest.newBuilder(URI.create(base + "/secret"));
            if (sent != null) b.header("Authorization", "Bearer " + sent);
            System.out.println("with token " + (sent != null) + ": " + client.send(b.build(), HttpResponse.BodyHandlers.ofString()).statusCode());
        }

        // ---- 6. POST with a JSON body ----
        String json = Json.write(obj("customer", "Asha", "items", List.of(obj("product", "Pen", "qty", 3))));
        System.out.println("Sending: " + json);
        HttpRequest post = HttpRequest.newBuilder(URI.create(base + "/orders"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();
        HttpResponse<String> created = client.send(post, HttpResponse.BodyHandlers.ofString());
        System.out.println(created.statusCode() + " " + created.body());           // 201 {"orderId":1,"customer":"Asha","status":"received"}

        // ---- 7. Failures are normal: retry with a growing pause (exponential backoff) ----
        for (int attempt = 0; attempt < 4; attempt++) {
            int status = client.send(HttpRequest.newBuilder(URI.create(base + "/flaky")).build(), HttpResponse.BodyHandlers.ofString()).statusCode();
            System.out.println("try " + (attempt + 1) + " -> " + status);
            if (status == 200) break;
            System.out.println("  waiting " + (1L << attempt) + " s (pretend; Thread.sleep(1000L << attempt) in real life)");
        }

        // ---- 8. No API? The data is inside HTML: scrape it with a regex ----
        String html = client.send(HttpRequest.newBuilder(URI.create(base + "/shop")).build(), HttpResponse.BodyHandlers.ofString()).body();
        Matcher m = Pattern.compile("title=\"([^\"]+)\".*?class=\"price\">Rs\\s*([\\d.]+)</p>", Pattern.DOTALL).matcher(html);
        while (m.find()) {
            System.out.println(m.group(1) + " costs Rs." + m.group(2));
        }

        // ---- 9. Async: start the request, do other work, collect the answer later ----
        var future = client.sendAsync(HttpRequest.newBuilder(URI.create(base + "/weather")).build(), HttpResponse.BodyHandlers.ofString())
                .thenApply(HttpResponse::body);
        System.out.println("(doing other work while we wait...)");
        System.out.println("Async body has " + future.join().length() + " characters");

        // ---- 10. Writing JSON by hand ----
        System.out.println(Json.write(obj("name", "Pen", "price", 10.5, "inStock", true, "note", null, "quote", "say \"hi\"")));
    }
}
