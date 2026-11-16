# Day 27 — HTTP & JSON (talking to a web server with `HttpClient`)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Call a web API with `java.net.http.HttpClient`, read and write JSON, handle failures, and scrape a little HTML | Intermediate |

## 🌍 Real-world scenario & trend
**Your delivery dashboard needs live data:** today's weather for a route, the status of an order, prices from a web page. Nearly every app today is glued together by **APIs**: you ask a server a question, it answers with JSON. When no API exists, you read the HTML of the page. 

**Trend:** AI apps are API clients too. Calling a language model *is* a `POST` with a JSON body and a secret key in a header. **Why Java?** Spring Boot services call other services all day, and `HttpClient` has been part of the JDK since Java 11, so you need no extra library. *Coming from Python?* `HttpClient` is the `requests` library, `Json` below is `response.json()`, and the regex scraper replaces BeautifulSoup (real projects use the library **jsoup**).

**No internet needed today.** The program starts a tiny web server on your own computer (`127.0.0.1`, a free port) and then calls it. The answers are always the same, so the auto-checker can test everything, including failures and retries.

## 0. Warm-up (5 min) — Day 26 recap
- Name the three steps of a cleaning pipeline.  • What does `Collectors.teeing` do?

## 1. Concepts (with tiny code)

### 1.1 How the web talks (HTTP)
You send a **request** (method + URL + optional headers and body). The server sends a **response** (status code + headers + body).
| Method | Purpose |
|---|---|
| `GET` | read data |
| `POST` | send data (a JSON body) |
| `PUT` / `DELETE` | update / remove |

| Status | Meaning |
|---|---|
| 200 / 201 | OK / created |
| 400 / 401 / 403 / 404 | bad request / not logged in / forbidden / not found |
| 429 | too many requests: slow down! |
| 500 / 503 | the server has a problem: maybe retry |

### 1.2 A server on your own computer
```java
HttpServer server = HttpServer.create(new InetSocketAddress(InetAddress.getByName("127.0.0.1"), 0), 0);
server.createContext("/", exchange -> { /* answer here */ });
server.start();
String base = "http://127.0.0.1:" + server.getAddress().getPort();
```
`127.0.0.1` means "this computer only". Port `0` means "pick any free port". `HttpServer` is in the JDK (`com.sun.net.httpserver`); on Day 30 you will build a whole REST API with it. Always `server.stop(0)` at the end (use `try/finally`).

### 1.3 GET with `HttpClient`
```java
HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
HttpRequest request = HttpRequest.newBuilder(URI.create(base + "/weather"))
        .timeout(Duration.ofSeconds(10))              // ALWAYS set a timeout
        .header("Accept", "application/json")
        .build();                                     // GET is the default
HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
response.statusCode();   // 200
response.body();         // the text the server sent
```
`send` throws `IOException` (network broken) and `InterruptedException`. A **404 or 500 is not an exception**: you get a normal response and must look at `statusCode()` yourself.

### 1.4 JSON text → Java objects
A JSON reader gives you `Map` (object), `List` (array), `String`, `Long` or `Double` (number), `Boolean` and `null`. The JDK has no JSON class, so `Practice.java` and `Examples.java` contain a small `Json` helper (the Day 16 reader plus writer). In real projects use **Jackson** or **Gson**.
```java
Map<String, Object> data = Json.asObject(Json.parse(body));
Map<String, Object> current = Json.asObject(data.get("current"));
double temp = ((Number) current.get("temperature_2m")).doubleValue();
```
**Gotcha:** a JSON number without a decimal point (`30`) comes back as `Long`, with one (`28.5`) as `Double`. Cast to `Number` and call `.doubleValue()`; a direct `(Double)` cast would crash on `30`.

### 1.5 Building URLs and JSON
```java
String url = base + "/search?q=" + URLEncoder.encode("tea & coffee", StandardCharsets.UTF_8);   // ...?q=tea+%26+coffee
String json = Json.write(obj("customer", "Asha", "items", List.of(obj("product", "Pen", "qty", 3))));
```
Never glue user text into a URL without `URLEncoder`: a `&` or a space would change the meaning. `obj("a", 1, "b", true)` is a small helper that builds a `Map` in a fixed order.

### 1.6 POST with a JSON body
```java
HttpRequest post = HttpRequest.newBuilder(URI.create(base + "/orders"))
        .header("Content-Type", "application/json")           // tells the server how to read the body
        .POST(HttpRequest.BodyPublishers.ofString(json))
        .build();
```
A good server answers `201 Created` and a JSON receipt. Without the `Content-Type` header our server answers `415`.

### 1.7 Failures are normal: retry with a growing pause
Networks drop, servers say 503. Retry a few times and wait longer each time (**exponential backoff**: 1 s, 2 s, 4 s). Never retry a **4xx**: asking again will not make a 404 turn into a 200. Never loop forever.
```java
for (int attempt = 0; attempt < attempts; attempt++) {
    // try; on success return; on a 4xx throw at once; on 5xx or IOException wait and continue
    if (attempt < attempts - 1) sleeper.accept(1L << attempt);   // 1, 2, 4 ...
}
```
**Testable code:** the pause is passed in as a parameter (`LongConsumer sleeper`). A test passes `sleeps::add` and finishes instantly; real code passes `s -> Thread.sleep(s * 1000)`. This is *dependency injection*; Python did the same with `get=requests.get`.

### 1.8 Secrets and scraping
Tokens go into a header (`Authorization: Bearer <token>`) and are read from the environment: `System.getenv("API_TOKEN")`. **Never** write a key in source code or commit it to Git.

No API? The data is inside the HTML. A regex with `Pattern.DOTALL` can pull titles and prices out of simple, regular HTML (Day 23). Be a good citizen: read `robots.txt` and the terms, pause between requests, send an honest `User-Agent`, prefer an official API, never collect personal data or paywalled content.

## 2. Code along (30 min)  `Examples.java`
Open `Examples.java`, **type** (do not copy-paste) the parts from "part 3" down, run it, then change values and re-run. It starts the local server, does a GET, a POST, shows a 404 and a 401, retries a flaky endpoint, scrapes a page and stops the server. Read the `Json` helper at the top **after** the code along.

## 3. Common mistakes
- No timeout: your program may wait forever for a dead server.
- Treating a `404` or `500` as success and parsing the error page as JSON. Check `statusCode()`.
- Casting a JSON number to `Double` when the text was `30` (a `Long`). Use `Number.doubleValue()`.
- Forgetting `Content-Type: application/json` on a POST.
- Putting an API key in the code or in Git.
- Retrying a 4xx, or retrying forever without a pause (you may get blocked: 429).
- Not stopping the server: the program does not end because a server thread is still alive.
- Scraping a page that builds its content with JavaScript: the data is not in the HTML (look for its JSON API instead).

## 4. Today's tasks  `Practice.java`
| ID | Level | Task |
|---|---|---|
| L1-1 … L1-3 | 🟢 Beginner | Build a URL with encoded parameters, classify a status code, write JSON by hand |
| L2-1 … L2-4 | 🟡 Intermediate | Parse a weather answer, `fetchJson` with headers and errors, retry with backoff, scrape book titles and prices |
| L3-1, L3-2 | 🔴 Challenge | Count posts per user from an API, `POST` an order as JSON |

Run `java Practice.java`: the auto-checker starts its own server on your computer and prints `[PASS]` / `[FAIL]`. No internet is used. `Json`, `obj` and `TestServer` are already written; you do not change them.

## 5. Stuck? Hint ladder (use in order, 10 min each)
<details><summary>Hint 1 - Direction</summary>
Draw the data: write the JSON on paper and mark the path to the value (<code>data → "current" → "temperature_2m"</code>). For HTML, find the tag or class that wraps each item. For the client tasks, say the request in words first: method, URL, headers, body, then what you do with each status.
</details>
<details><summary>Hint 2 - Shape of the answer</summary>
URL: a <code>StringJoiner("&amp;", base + "?", "")</code> and <code>URLEncoder.encode(String.valueOf(value), StandardCharsets.UTF_8)</code>. fetchJson: <code>HttpRequest.newBuilder(URI.create(url)).timeout(...).header(...)</code>, then <code>client.send(request, HttpResponse.BodyHandlers.ofString())</code>. Retry: <code>for (int attempt = 0; attempt &lt; attempts; attempt++)</code> with a <code>try/catch (IOException)</code> inside, <code>sleeper.accept(1L &lt;&lt; attempt)</code> after a failed try that is not the last, <code>throw new IOException("giving up")</code> after the loop. Scrape: <code>Pattern.compile("title=\"([^\"]+)\".*?class=\"price\"&gt;Rs\\s*([\\d.]+)&lt;/p&gt;", Pattern.DOTALL)</code> and a <code>while (m.find())</code> loop. POST: <code>.header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(body))</code>.
</details>
<details><summary>Hint 3 - Peek (last resort)</summary>
Open <code>java/solutions/day27_Solution.java</code>, read one task only, close it, then write it yourself from memory.
</details>

## 6. Quiz (10 min, no peeking) - answers in `java/solutions/day27_answers.md`
1. What is the difference between `GET` and `POST`?
2. What do the status codes 404, 429 and 503 mean?
3. Why must every request have a timeout?
4. Does `client.send(...)` throw an exception when the server answers 404? What must you do instead?
5. Where should an API key live, and in which header do you send it?
6. Why is it easier to test `fetchWithRetry(client, url, attempts, sleeper)` than a version that calls `Thread.sleep` inside?
7. A JSON answer contains `"temperature_2m": 30`. Why does `(Double) map.get("temperature_2m")` crash, and what is the fix?
8. Name three rules of polite scraping.

## 7. Wrap-up (5 min)
- Fill today's row in `java/tracker/JAVA_PROGRESS_TRACKER.xlsx` (hours, quiz score, confidence 1-5).
- Add **one** error you hit today to the **Bug Journal** sheet.
- Tomorrow: databases. SQLite and SQL from Java with JDBC.
