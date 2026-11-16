# Day 27 - Quiz answers

1. `GET` reads data (parameters in the URL, safe to repeat). `POST` sends data in the body (for example JSON) to create something or trigger an action.
2. 404 = not found; 429 = too many requests (you are rate-limited: slow down and back off); 503 = service unavailable (a server problem, often temporary, so a retry can help).
3. Without a timeout a dead or very slow server can make your program wait forever. Use `HttpRequest.newBuilder(...).timeout(Duration.ofSeconds(10))` and a `connectTimeout` on the client.
4. No. A 404 is a normal response. You must check `response.statusCode()` yourself (for example throw an `IOException("HTTP 404")` when it is not 200) before you parse the body.
5. In an environment variable or a secrets manager (`System.getenv("API_TOKEN")`), never in the source code or Git. It is sent in the `Authorization` header: `Authorization: Bearer <token>`.
6. The pause is a parameter, so a test passes a recorder (`sleeps::add`) and finishes instantly, and it can check the pauses (1, 2, 4 ...). A hidden `Thread.sleep` would make every test wait for real seconds.
7. The JSON reader returns `Long` for numbers without a decimal point and `Double` only for numbers with one, and a `Long` cannot be cast to `Double` (`ClassCastException`). Cast to `Number` and call `.doubleValue()`.
8. Any three: read `robots.txt` and the terms; pause between requests; send an honest `User-Agent`; prefer an official API; cache results; do not collect personal data or bypass paywalls.
