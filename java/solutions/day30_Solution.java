// SOLUTION FILE - try the hint ladder first!
/* Day 30 - Practice: a REST API with the JDK's built-in HttpServer ("Mini Shop API").
 *
 * Run:  java Practice.java
 * The program starts the server itself on a free port of this computer (127.0.0.1) and the checker calls it with
 * HttpClient, exactly like a mobile app would. Your job: write the small handler methods. The router (route) and
 * the server (startServer) are given - read them after the tasks.
 * Each handler returns a Response: a status code + the data that becomes JSON.
 * PRODUCTS is an in-memory list: change it (add), never re-assign it.
 */
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.URLDecoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.*;
import java.util.stream.Collectors;

class Practice {

    record Product(int id, String name, double price) {
        Map<String, Object> toJson() {
            return obj("id", id, "name", name, "price", price);
        }
    }

    /** What every handler returns: the HTTP status code and the data that the server turns into JSON text. */
    record Response(int status, Object body) {}

    static final List<Product> ORIGINAL = List.of(new Product(1, "Pen", 10.0), new Product(2, "Notebook", 55.5),
            new Product(3, "Backpack", 799.0));
    static final List<Product> PRODUCTS = new ArrayList<>(ORIGINAL);
    static final Path SALES_CSV = Path.of("../../datasets/sales.csv");

    /** obj("a", 1, "b", "x") builds {"a":1,"b":"x"} with the keys in this order. */
    static Map<String, Object> obj(Object... keysAndValues) {
        Map<String, Object> map = new LinkedHashMap<>();
        for (int i = 0; i < keysAndValues.length; i += 2) {
            map.put((String) keysAndValues[i], keysAndValues[i + 1]);
        }
        return map;
    }

    static double round2(double value) {
        return Math.round(value * 100) / 100.0;
    }

    // ---------------------------------------------------------------------------
    // L1-1 | GET /health   (Level 1 - Beginner)
    // Answer 200 with the JSON {"status":"ok"}.   Tip: obj("status", "ok") builds the map.
    // ---------------------------------------------------------------------------
    static Response health() {
        // >>> SOLUTION stub: return null;
        return new Response(200, obj("status", "ok"));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-2 | GET /greet/{name}   (Level 1 - Beginner)
    // Answer 200 with {"message":"Hello, <name>!"}   (for Asha: Hello, Asha!)
    // ---------------------------------------------------------------------------
    static Response greet(String name) {
        // >>> SOLUTION stub: return null;
        return new Response(200, obj("message", "Hello, " + name + "!"));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L1-3 | parseQuery   (Level 1 - Beginner)
    // The part of a URL after the ? looks like "min_price=50&n=3". Turn it into a Map<String, String>:
    //   null or ""                -> empty map
    //   "min_price=50&n=3"        -> {min_price=50, n=3}
    //   "flag&x="                 -> {flag=, x=}          (no = means an empty value)
    //   "name=Asha%20K"           -> {name=Asha K}        (decode with URLDecoder.decode(text, StandardCharsets.UTF_8))
    //   "n=1&n=2"                 -> {n=2}                (a repeated key: the last value wins)
    // ---------------------------------------------------------------------------
    static Map<String, String> parseQuery(String rawQuery) {
        // >>> SOLUTION stub: return new HashMap<>();
        Map<String, String> map = new LinkedHashMap<>();
        if (rawQuery == null || rawQuery.isEmpty()) {
            return map;
        }
        for (String pair : rawQuery.split("&")) {
            if (pair.isEmpty()) {
                continue;
            }
            String[] kv = pair.split("=", 2);
            String key = URLDecoder.decode(kv[0], StandardCharsets.UTF_8);
            String value = kv.length == 2 ? URLDecoder.decode(kv[1], StandardCharsets.UTF_8) : "";
            map.put(key, value);
        }
        return map;
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-1 | GET /products?min_price=   (Level 2 - Intermediate)
    // Answer 200 with a JSON list of the products whose price is >= minPrice (the router passes 0 when
    // the client sends no min_price, so that means "all"). Each product is product.toJson().
    // ---------------------------------------------------------------------------
    static Response listProducts(double minPrice) {
        // >>> SOLUTION stub: return null;
        List<Map<String, Object>> found = new ArrayList<>();
        for (Product p : PRODUCTS) {
            if (p.price() >= minPrice) {
                found.add(p.toJson());
            }
        }
        return new Response(200, found);
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-2 | GET /products/{id}   (Level 2 - Intermediate)
    // Answer 200 with that product's JSON, or 404 with {"error":"Product not found"}.
    // ---------------------------------------------------------------------------
    static Response getProduct(int id) {
        // >>> SOLUTION stub: return null;
        for (Product p : PRODUCTS) {
            if (p.id() == id) {
                return new Response(200, p.toJson());
            }
        }
        return new Response(404, obj("error", "Product not found"));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L2-3 | POST /products   (Level 2 - Intermediate)
    // `body` is the parsed JSON the client sent (a Map when it is a JSON object, anything else if it is not).
    // Rules: it must be an object with  "name" = a text that is not blank  and  "price" = a number > 0.
    //   * invalid -> 422 with {"error":"validation failed","fields":[...]} listing the bad field names, in the
    //     order "name", "price" (if body is not an object at all, fields = ["body"])
    //   * valid   -> new id = (largest existing id) + 1; add a new Product to PRODUCTS and answer 201 with its JSON.
    //     The price is stored as a double (a JSON 5 becomes 5.0).
    // ---------------------------------------------------------------------------
    static Response createProduct(Object body) {
        // >>> SOLUTION stub: return null;
        if (!(body instanceof Map<?, ?> m)) {
            return new Response(422, obj("error", "validation failed", "fields", List.of("body")));
        }
        List<String> bad = new ArrayList<>();
        if (!(m.get("name") instanceof String name) || name.isBlank()) {
            bad.add("name");
        }
        if (!(m.get("price") instanceof Number price) || price.doubleValue() <= 0) {
            bad.add("price");
        }
        if (!bad.isEmpty()) {
            return new Response(422, obj("error", "validation failed", "fields", bad));
        }
        int newId = PRODUCTS.stream().mapToInt(Product::id).max().orElse(0) + 1;
        Product created = new Product(newId, (String) m.get("name"), ((Number) m.get("price")).doubleValue());
        PRODUCTS.add(created);
        return new Response(201, created.toJson());
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-1 | GET /sales/summary   (Level 3 - Challenge)
    // Read SALES_CSV (header: order_id,order_date,region,category,product,quantity,unit_price,discount_pct,payment_method).
    // revenue = quantity * unit_price * (1 - discount_pct / 100.0)
    // Answer 200 with {"orders": <int>, "total_revenue": <2 decimals>, "by_region": {<region>: <2 decimals>, ...}}
    // by_region is sorted by region name (TreeMap). Round with round2 at the very end.
    // ---------------------------------------------------------------------------
    static Response salesSummary() throws IOException {
        // >>> SOLUTION stub: return null;
        List<String> lines = Files.readAllLines(SALES_CSV);
        double total = 0;
        Map<String, Double> byRegion = new TreeMap<>();
        for (String line : lines.subList(1, lines.size())) {
            String[] c = line.split(",", -1);
            double revenue = Integer.parseInt(c[5]) * Integer.parseInt(c[6]) * (1 - Integer.parseInt(c[7]) / 100.0);
            total += revenue;
            byRegion.merge(c[2], revenue, Double::sum);
        }
        Map<String, Object> regions = new LinkedHashMap<>();
        byRegion.forEach((region, value) -> regions.put(region, round2(value)));
        return new Response(200, obj("orders", lines.size() - 1, "total_revenue", round2(total), "by_region", regions));
        // <<< SOLUTION
    }

    // ---------------------------------------------------------------------------
    // L3-2 | GET /sales/top-products?n=   (Level 3 - Challenge)
    // `n` is the raw text of the n parameter (null when the client did not send it -> default 3).
    // It must be a whole number from 1 to 10, otherwise answer 422 with {"error":"n must be a whole number from 1 to 10"}.
    // Answer 200 with a list of {"product": name, "revenue": total (2 decimals)}, biggest revenue first, n entries.
    // ---------------------------------------------------------------------------
    static Response topProducts(String n) throws IOException {
        // >>> SOLUTION stub: return null;
        int count = 3;
        if (n != null) {
            try {
                count = Integer.parseInt(n.strip());
            } catch (NumberFormatException e) {
                count = -1;
            }
        }
        if (count < 1 || count > 10) {
            return new Response(422, obj("error", "n must be a whole number from 1 to 10"));
        }
        List<String> lines = Files.readAllLines(SALES_CSV);
        Map<String, Double> byProduct = new HashMap<>();
        for (String line : lines.subList(1, lines.size())) {
            String[] c = line.split(",", -1);
            byProduct.merge(c[4], Integer.parseInt(c[5]) * Integer.parseInt(c[6]) * (1 - Integer.parseInt(c[7]) / 100.0), Double::sum);
        }
        List<Map<String, Object>> top = byProduct.entrySet().stream()
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .limit(count)
                .map(e -> obj("product", e.getKey(), "revenue", round2(e.getValue())))
                .collect(Collectors.toList());
        return new Response(200, top);
        // <<< SOLUTION
    }

    // ======================= ready-made: the router and the server (read them after the tasks) ====================

    /** The router: looks at method + path and calls your handler. 404 = no such route, 405 = wrong method. */
    static Response route(String method, String path, String rawQuery, String body) throws Exception {
        List<String> p = Arrays.stream(path.split("/")).filter(s -> !s.isEmpty()).toList();
        Map<String, String> query = parseQuery(rawQuery);
        boolean get = method.equals("GET");
        if (p.equals(List.of("health"))) {
            return get ? health() : notAllowed();
        } else if (p.size() == 2 && p.get(0).equals("greet")) {
            return get ? greet(p.get(1)) : notAllowed();
        } else if (p.equals(List.of("products"))) {
            if (get) {
                double min = 0;
                if (query.containsKey("min_price")) {
                    try {
                        min = Double.parseDouble(query.get("min_price"));
                    } catch (NumberFormatException e) {
                        return new Response(422, obj("error", "min_price must be a number"));
                    }
                }
                return listProducts(min);
            } else if (method.equals("POST")) {
                Object json;
                try {
                    json = Json.parse(body);
                } catch (IllegalArgumentException e) {
                    return new Response(400, obj("error", "malformed JSON: " + e.getMessage()));
                }
                return createProduct(json);
            }
            return notAllowed();
        } else if (p.size() == 2 && p.get(0).equals("products")) {
            if (!get) {
                return notAllowed();
            }
            try {
                return getProduct(Integer.parseInt(p.get(1)));
            } catch (NumberFormatException e) {
                return new Response(422, obj("error", "id must be a whole number"));
            }
        } else if (p.equals(List.of("sales", "summary"))) {
            return get ? salesSummary() : notAllowed();
        } else if (p.equals(List.of("sales", "top-products"))) {
            return get ? topProducts(query.get("n")) : notAllowed();
        }
        return new Response(404, obj("error", "no such route"));
    }

    static Response notAllowed() {
        return new Response(405, obj("error", "method not allowed"));
    }

    /** Start the API on a free port of 127.0.0.1 (port 0 = "any free port"). Call server.stop(0) when you are done. */
    static HttpServer startServer() throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0);
        server.createContext("/", exchange -> {
            Response response;
            try {
                String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
                URI uri = exchange.getRequestURI();
                response = route(exchange.getRequestMethod(), uri.getPath(), uri.getRawQuery(), body);
                if (response == null) {
                    throw new IllegalStateException("the handler returned null (not written yet?)");
                }
            } catch (Throwable e) {                         // a bug in a handler must not kill the server: answer 500
                response = new Response(500, obj("error", "internal error"));
            }
            byte[] bytes = Json.write(response.body()).getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
            exchange.sendResponseHeaders(response.status(), bytes.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(bytes);
            }
        });
        server.start();
        return server;
    }

    // ======================= ready-made JSON helper (used by the server and the checks) ====================
    static final class Json {
        /** Nested data -> compact JSON text (Map, List, String, Number, Boolean, null). */
        static String write(Object value) {
            if (value == null) {
                return "null";
            } else if (value instanceof String s) {
                return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\t", "\\t") + "\"";
            } else if (value instanceof Number || value instanceof Boolean) {
                return value.toString();
            } else if (value instanceof List<?> list) {
                return list.stream().map(Json::write).collect(Collectors.joining(",", "[", "]"));
            } else if (value instanceof Map<?, ?> map) {
                return map.entrySet().stream()
                        .map(e -> write(String.valueOf(e.getKey())) + ":" + write(e.getValue()))
                        .collect(Collectors.joining(",", "{", "}"));
            }
            throw new IllegalArgumentException("cannot write " + value.getClass().getSimpleName());
        }

        /** JSON text -> LinkedHashMap / ArrayList / String / Integer (or Long) / Double / Boolean / null. */
        static Object parse(String text) {
            Reader reader = new Reader(text);
            Object value = reader.value();
            reader.skipSpaces();
            if (reader.pos != text.length()) {
                throw new IllegalArgumentException("extra text after the JSON value at position " + reader.pos);
            }
            return value;
        }

        // A reader walks through the text with a position and reads one value at a time.
        private static final class Reader {
            private final String s;
            private int pos = 0;

            Reader(String s) {
                this.s = s;
            }

            void skipSpaces() {
                while (pos < s.length() && Character.isWhitespace(s.charAt(pos))) {
                    pos++;
                }
            }

            void expect(char c) {
                if (pos >= s.length() || s.charAt(pos) != c) {
                    throw new IllegalArgumentException("expected '" + c + "' at position " + pos);
                }
                pos++;
            }

            Object value() {
                skipSpaces();
                if (pos >= s.length()) {
                    throw new IllegalArgumentException("unexpected end of JSON text");
                }
                char c = s.charAt(pos);
                if (c == '{') {
                    return object();
                } else if (c == '[') {
                    return array();
                } else if (c == '"') {
                    return string();
                } else if (s.startsWith("true", pos)) {
                    pos += 4;
                    return true;
                } else if (s.startsWith("false", pos)) {
                    pos += 5;
                    return false;
                } else if (s.startsWith("null", pos)) {
                    pos += 4;
                    return null;
                }
                return number();
            }

            Map<String, Object> object() {
                Map<String, Object> map = new LinkedHashMap<>();
                expect('{');
                skipSpaces();
                if (pos < s.length() && s.charAt(pos) == '}') {
                    pos++;
                    return map;
                }
                while (true) {
                    skipSpaces();
                    String key = string();
                    skipSpaces();
                    expect(':');
                    map.put(key, value());
                    skipSpaces();
                    if (pos < s.length() && s.charAt(pos) == ',') {
                        pos++;
                    } else {
                        expect('}');
                        return map;
                    }
                }
            }

            List<Object> array() {
                List<Object> list = new ArrayList<>();
                expect('[');
                skipSpaces();
                if (pos < s.length() && s.charAt(pos) == ']') {
                    pos++;
                    return list;
                }
                while (true) {
                    list.add(value());
                    skipSpaces();
                    if (pos < s.length() && s.charAt(pos) == ',') {
                        pos++;
                    } else {
                        expect(']');
                        return list;
                    }
                }
            }

            String string() {
                expect('"');
                StringBuilder sb = new StringBuilder();
                while (pos < s.length() && s.charAt(pos) != '"') {
                    char c = s.charAt(pos++);
                    if (c == '\\') {
                        char next = s.charAt(pos++);
                        switch (next) {
                            case 'n' -> sb.append('\n');
                            case 't' -> sb.append('\t');
                            case 'u' -> {
                                sb.append((char) Integer.parseInt(s.substring(pos, pos + 4), 16));
                                pos += 4;
                            }
                            default -> sb.append(next);
                        }
                    } else {
                        sb.append(c);
                    }
                }
                expect('"');
                return sb.toString();
            }

            Object number() {
                int start = pos;
                while (pos < s.length() && "+-0123456789.eE".indexOf(s.charAt(pos)) >= 0) {
                    pos++;
                }
                String t = s.substring(start, pos);
                if (t.isEmpty()) {
                    throw new IllegalArgumentException("unexpected character at position " + pos);
                }
                if (t.contains(".") || t.contains("e") || t.contains("E")) {
                    return Double.parseDouble(t);
                }
                long n = Long.parseLong(t);
                if (n >= Integer.MIN_VALUE && n <= Integer.MAX_VALUE) {
                    return (int) n;
                }
                return n;
            }
        }
    }

    // ======================= AUTO-CHECKER (do not edit below) ====================
    // The Checker's lambdas cannot throw checked exceptions, so attempt(...) wraps them for the tests.
    interface Action<T> {
        T run() throws Exception;
    }

    static <T> T attempt(Action<T> action) {
        try {
            return action.run();
        } catch (RuntimeException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException(e.getClass().getSimpleName() + ": " + e.getMessage(), e);
        }
    }

    static void reset() {
        PRODUCTS.clear();
        PRODUCTS.addAll(ORIGINAL);
    }

    static HttpClient client;
    static int port;

    /** One HTTP call to our own server. Returns [status code, parsed JSON body]. */
    static List<Object> call(String method, String path, String body) {
        return attempt(() -> {
            HttpRequest.Builder request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                    .timeout(Duration.ofSeconds(5))
                    .header("Content-Type", "application/json")
                    .method(method, body == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(body));
            HttpResponse<String> response = client.send(request.build(), HttpResponse.BodyHandlers.ofString());
            return Arrays.asList(response.statusCode(), Json.parse(response.body()));
        });
    }

    static List<Object> get(String path) {
        return call("GET", path, null);
    }

    static List<Object> ids(String path) {
        List<Object> reply = get(path);
        List<Object> ids = new ArrayList<>();
        for (Object item : (List<?>) reply.get(1)) {
            ids.add(((Map<?, ?>) item).get("id"));
        }
        return ids;
    }

    static List<Object> createChecks() {
        reset();
        List<Object> created = call("POST", "/products", "{\"name\":\"Eraser\",\"price\":5}");
        List<Object> listing = ids("/products");
        Object badPrice = call("POST", "/products", "{\"name\":\"Bad\",\"price\":-1}");
        Object badName = call("POST", "/products", "{\"name\":\"  \",\"price\":5}");
        Object second = ((Map<?, ?>) call("POST", "/products", "{\"name\":\"Ruler\",\"price\":12.5}").get(1)).get("id");
        reset();
        return List.of(created, listing, badPrice, badName, second);
    }

    public static void main(String[] args) throws Exception {
        System.out.println("--- Day 30 checks ---");
        HttpServer server = startServer();
        port = server.getAddress().getPort();
        client = HttpClient.newHttpClient();
        try {
            Checker.check("L1-1 GET /health", () -> get("/health"), List.of(200, Map.of("status", "ok")));
            Checker.check("L1-2 GET /greet/Asha", () -> get("/greet/Asha"), List.of(200, Map.of("message", "Hello, Asha!")));
            Checker.check("L1-3 parseQuery basics", () -> List.of(parseQuery(null), parseQuery(""), parseQuery("min_price=50&n=3")),
                    List.of(Map.of(), Map.of(), Map.of("min_price", "50", "n", "3")));
            Checker.check("L1-3 parseQuery edge cases", () -> List.of(parseQuery("flag&x="), parseQuery("name=Asha%20K"), parseQuery("n=1&n=2")),
                    List.of(Map.of("flag", "", "x", ""), Map.of("name", "Asha K"), Map.of("n", "2")));
            Checker.check("L2-1 GET /products (all)", () -> ids("/products"), List.of(1, 2, 3));
            Checker.check("L2-1 GET /products?min_price=50", () -> ids("/products?min_price=50"), List.of(2, 3));
            Checker.check("L2-1 GET /products?min_price=1000", () -> get("/products?min_price=1000"), List.of(200, List.of()));
            Checker.check("L2-1 GET /products?min_price=abc -> 422", () -> get("/products?min_price=abc").get(0), 422);
            Checker.check("L2-2 GET /products/2", () -> get("/products/2"), List.of(200, Map.of("id", 2, "name", "Notebook", "price", 55.5)));
            Checker.check("L2-2 GET /products/99 -> 404", () -> get("/products/99"), List.of(404, Map.of("error", "Product not found")));
            Checker.check("L2-3 POST /products (201, saved, 422 on bad data, next id)", () -> createChecks(),
                    List.of(List.of(201, Map.of("id", 4, "name", "Eraser", "price", 5.0)), List.of(1, 2, 3, 4),
                            List.of(422, Map.of("error", "validation failed", "fields", List.of("price"))),
                            List.of(422, Map.of("error", "validation failed", "fields", List.of("name"))), 5));
            Checker.check("L3-1 GET /sales/summary", () -> get("/sales/summary"), List.of(200, Map.of(
                    "orders", 300, "total_revenue", 1443241.55,
                    "by_region", Map.of("East", 335268.6, "North", 300446.25, "South", 348849.7, "West", 458677.0))));
            Checker.check("L3-2 GET /sales/top-products (default 3)", () -> get("/sales/top-products"), List.of(200, List.of(
                    Map.of("product", "Smartwatch", "revenue", 298814.6),
                    Map.of("product", "Air Fryer", "revenue", 279194.15),
                    Map.of("product", "Running Shoes", "revenue", 143652.1))));
            Checker.check("L3-2 top-products?n=1", () -> ((List<?>) get("/sales/top-products?n=1").get(1)).size(), 1);
            Checker.check("L3-2 top-products n=0, n=11, n=abc -> 422", () -> List.of(get("/sales/top-products?n=0").get(0),
                    get("/sales/top-products?n=11").get(0), get("/sales/top-products?n=abc").get(0)), List.of(422, 422, 422));
            Checker.check("Router: unknown path 404, wrong method 405, bad JSON 400", () -> List.of(get("/nope").get(0),
                    call("POST", "/health", "{}").get(0), call("DELETE", "/products/1", null).get(0),
                    call("POST", "/products", "{oops").get(0), get("/products/abc").get(0)), List.of(404, 405, 405, 400, 422));
        } finally {
            reset();
            server.stop(0);
        }
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
