# Day 30 — A REST API with HttpServer, Spring Boot Explained & The Final Exam 🎓

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Serve your data over HTTP + JSON with the JDK's own `HttpServer`, understand what Spring Boot adds, then prove your "reads code like a pro" skill with a 27-question exam | Upper-intermediate ✅ |

## 🌍 Real-world scenario & trend
**The mobile-app team needs your data.** They cannot open your CSV or call your methods: they speak **HTTP + JSON**. A REST API is a small program that waits for requests like `GET /products/2` and answers with a status code and a JSON body. Delivery apps, UPI apps, shop dashboards and AI chat backends all work this way.

**Why Java?** Java is one of the most used languages for back-end APIs. Most big companies run **Spring Boot** services on the JVM. Today you build the same idea with only the JDK (`com.sun.net.httpserver.HttpServer`, no downloads), so you see exactly what a framework hides: routes, parameters, JSON, status codes. *Coming from Python?* This is the FastAPI day. FastAPI gives you routes by decorators and validation by type hints; in plain Java you write the small `if` for each route yourself, and Spring Boot gives you the decorators back (as annotations).

## ⏱ Suggested schedule
| Time | Activity |
|---|---|
| 0:00–0:10 | Warm-up + read this lesson |
| 0:10–0:25 | Code along (`Examples.java`): start a server, call it, change a route |
| 0:25–1:05 | `Practice.java` (8 tasks) |
| 1:05–1:50 | **Final exam** → `FINAL_EXAM.md` (closed-book, 45 min, no running code!) |
| 1:50–2:00 | Mark it, update the tracker, write your reflection |

## 0. Warm-up (5 min) — Day 29 recap
- What does HTTP status `404` mean?  • What is JSON? (Write one object by hand.)

## 1. Concepts (with tiny code)

### 1.1 HTTP in one minute
A client sends a **request**: a *method* (`GET` read, `POST` create, `PUT` replace, `DELETE` remove), a *path* (`/products/2`), optional *query* (`?min_price=50`), optional *headers* and *body*. The server sends a **response**: a *status code* and usually a JSON body.
| Code | Meaning | Code | Meaning |
|---|---|---|---|
| 200 | OK | 404 | Not found |
| 201 | Created (after a POST) | 405 | Method not allowed |
| 400 | Bad request (broken JSON) | 422 | Valid JSON but wrong data (price -1) |
| 500 | Server bug | 409 | Conflict (duplicate) |

### 1.2 Start a server on a free port
```java
HttpServer server = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0);
server.createContext("/health", exchange -> send(exchange, 200, "{\"status\":\"ok\"}"));
server.start();
int port = server.getAddress().getPort();      // port 0 asked the system for any free port
// ... use it ...
server.stop(0);                                // always stop it (finally block)
```
`getLoopbackAddress()` is `127.0.0.1`: only this computer can reach it, which is exactly right for learning and for tests. A fixed port such as 8080 can already be taken by another program.

### 1.3 A handler: read the request, write the response
```java
static void send(HttpExchange exchange, int status, String json) throws IOException {
    byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
    exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
    exchange.sendResponseHeaders(status, bytes.length);       // status + headers first ...
    try (OutputStream out = exchange.getResponseBody()) {      // ... then the body
        out.write(bytes);
    }
}
```
`exchange.getRequestMethod()`, `getRequestURI().getPath()`, `getRequestURI().getRawQuery()` and `getRequestBody()` tell you what the client asked.

### 1.4 Routes: method + path decide the handler
```java
List<String> p = Arrays.stream(path.split("/")).filter(s -> !s.isEmpty()).toList();   // "/products/2" -> [products, 2]
if (p.equals(List.of("health")))                         return health();
if (p.size() == 2 && p.get(0).equals("products"))        return getProduct(Integer.parseInt(p.get(1)));
return new Response(404, Map.of("error", "no such route"));      // unknown path
```
Keep the **handlers** (`health`, `getProduct`) free of HTTP details: they just return a status and data. Then the router and the server are written once, and every handler can be tested like any other method. That is exactly how today's `Practice.java` is built.

### 1.5 JSON and validation (never trust the client)
The client sends text: `{"name":"Eraser","price":5}`. Parse it (you have the `Json` helper from Day 16), then **check every field** before using it:
```java
if (!(body instanceof Map<?, ?> m)) return new Response(422, ...);
if (!(m.get("price") instanceof Number price) || price.doubleValue() <= 0) bad.add("price");
```
Broken JSON is **400**; JSON that is fine but has wrong values is **422**; a missing item is **404**; a successful POST is **201**. Query parameters arrive as text too (`?n=abc`): convert inside `try/catch (NumberFormatException)` and answer 422, never let it crash.

### 1.6 Calling and testing an API with `HttpClient`
```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + "/products/2")).GET().build();
HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.statusCode() + " " + response.body());     // 200 {"id":2,...}
```
For a POST use `.POST(HttpRequest.BodyPublishers.ofString(json))` and a `Content-Type: application/json` header. Today's auto-checker starts the server, calls every route like this and compares status and JSON. Day 24 skills in action.

### 1.7 Spring Boot, explained (no code to run today)
Spring Boot is the most popular Java framework for APIs. It does the boring parts for you: starts an embedded web server, finds your classes, turns JSON into objects and back (with the Jackson library), validates input and handles errors. The `health` and `products` routes look like this in Spring:
```text
@RestController
class ProductController {
    @GetMapping("/products/{id}")                        // route: method + path in one annotation
    Product one(@PathVariable int id) { ... }           // {id} is converted to int; "abc" gives 400 automatically

    @PostMapping("/products") @ResponseStatus(HttpStatus.CREATED)
    Product create(@Valid @RequestBody ProductIn in) { ... }   // JSON body -> record, validated; bad data gives 400 with details
}
```
Mapping to today: annotation = your router `if`; `@PathVariable`/`@RequestParam` = path and query parsing; `@RequestBody` + Jackson = the `Json` helper; `@Valid` = your validation `if`s; `ResponseEntity` = our `Response` record. You start a project at start.spring.io, add "Spring Web", run `./mvnw spring-boot:run` and it listens on port 8080. Because you now know what happens underneath, Spring will feel like shorthand, not magic. It is the logical next step for a Java back-end career (together with Spring Data JPA for databases and Spring Security for logins).

### 1.8 Where to go from here: your 30-60-90 map
- **Back-end:** Spring Boot + PostgreSQL + Spring Data JPA, then authentication (JWT), Docker and deployment (Render, Railway, AWS).
- **Android / mobile:** Kotlin or Java with Android Studio, and call APIs like today's.
- **Data / AI:** Java stream processing (Kafka), or call AI services over HTTP with the same `HttpClient`.
- **Always:** one project a month on GitHub, read other people's code daily, and use AI assistants as a *reviewer and tutor*. You can now verify what they write.

## 2. Code along (30 min)  `Examples.java`
It starts a server on a free port, calls `/health`, `/products` (with a query), `/products/2`, a missing product (404), a POST (201) and a bad POST (422), then stops the server. **Type** it section by section, run it, then add a route of your own (for example `GET /products/count`).

## 3. Common mistakes
- Forgetting `sendResponseHeaders` before writing the body, or writing a different length than you announced.
- Forgetting `server.stop(0)`: the program never ends. Use `try/finally`.
- Hard-coding port 8080 (may be busy). Use port 0 and ask `getAddress().getPort()`.
- Answering 200 for everything. Clients rely on 201, 404, 422.
- Returning HTML or a stack trace for errors. An API should return JSON like `{"error":"..."}`.
- Re-assigning the shared product list inside a handler instead of adding to it.
- Putting secrets (passwords, API keys) in code.

## 4. Today's tasks  `Practice.java`
The router (`route`) and the server (`startServer`) are given. You write the handlers; every handler returns a `Response(status, body)`.
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | `GET /health`, `GET /greet/{name}`, `parseQuery` (the text after `?`) |
| L2-1 … L2-3 | 🟡 Intermediate | list with a price filter, get one with 404, create with validation (201 / 422) |
| L3-1, L3-2 | 🔴 Challenge | `/sales/summary` from the CSV, `/sales/top-products?n=` with limits |

Run `java Practice.java`: the checker starts your server and calls it with `HttpClient`. To explore by hand, keep the server alive (see the comment in `Examples.java`) and open `http://127.0.0.1:<port>/products` in a browser.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Say in words what the endpoint returns, then build the map with <code>obj("key", value, ...)</code>. For a 404 use a <code>for</code> loop over <code>PRODUCTS</code> with an early <code>return</code> and the error <code>Response</code> after the loop.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
parseQuery: split on <code>&amp;</code>, then <code>split("=", 2)</code>, decode both parts with <code>URLDecoder.decode(text, StandardCharsets.UTF_8)</code>. New id: <code>max id + 1</code> (a stream: <code>mapToInt(Product::id).max().orElse(0) + 1</code>). Validation: <code>m.get("name") instanceof String name &amp;&amp; !name.isBlank()</code>. Sales: <code>Files.readAllLines(SALES_CSV)</code>, skip the header, <code>split(",")</code>, <code>Integer.parseInt(c[5]) * Integer.parseInt(c[6]) * (1 - Integer.parseInt(c[7]) / 100.0)</code>, <code>Map.merge(key, revenue, Double::sum)</code>, round with <code>round2</code> at the very end. Top products: sort the entries by value reversed, <code>limit(n)</code>; wrap <code>Integer.parseInt(n)</code> in <code>try/catch</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day30_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. 🎓 FINAL EXAM (45 min, closed-book)
Open **`FINAL_EXAM.md`** (in this folder). 27 questions: *"What does this code print?"* across all four weeks, including 4 *"find the bug"* ones. Rules: no running code, no AI, answers on paper or in the tracker; 1 point each. Then check `java/solutions/day30_ExamKey.md` (every answer there was produced by really running the code).

| Score (of 27) | Meaning |
|---|---|
| 24–27 | 🏆 You read Java like a professional. Start a real project this week. |
| 19–23 | ✅ Solid upper-intermediate. Redo the topics of the questions you missed. |
| 13–18 | 🟡 Good foundation. Repeat the days of your weak areas (see the "Day" tags), then retake in 3 days. |
| < 13 | 🔁 Re-do Weeks 1–2 exercises quickly (they are fast the second time), then retake. |

## 7. Quiz (10 min, no peeking) - answers in `java/solutions/day30_answers.md`
1. What do the status codes 200, 201, 404 and 422 mean?
2. Why start the server on port `0` and read the real port from `getAddress().getPort()`?
3. What is the difference between a **path** parameter and a **query** parameter? Give an example of each.
4. Why must you validate the JSON body of a POST, and which status do you send for bad data?
5. Why does `server.stop(0)` belong in a `finally` block?
6. How can you test an API without a browser?
7. What does Spring Boot add on top of what you wrote today? Name two annotations.
8. Why is it useful to keep handlers free of HTTP details (they only return status + data)?

## 8. Wrap-up — you did it! 🎉
Fill the **Weekly Review** and **Dashboard** in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx`, add your final exam score, and write 3 sentences: *What am I proudest of? What was hardest? What will I build next?*
