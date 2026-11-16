# Day 30 - Quiz answers

1. `200` OK (the request worked), `201` Created (a POST made something new), `404` Not found (no such product or route), `422` the JSON is well formed but the data is not acceptable (for example price -1).
2. Port `0` asks the operating system for any free port, so the program never clashes with another program that already uses 8080. `server.getAddress().getPort()` tells you which one you got.
3. A path parameter is part of the address and identifies one thing: `/products/2` (the `2`). A query parameter is an optional filter after `?`: `/products?min_price=50`. Both arrive as text and must be converted and checked.
4. A client can send anything: wrong types, empty text, negative numbers or broken JSON. Check every field before you use it. Broken JSON is `400`; valid JSON with bad values is `422` (with a message saying which field).
5. If a check or a handler throws, the code after it is skipped and the server would keep running and the program would never end. `finally` always runs, so the port is released.
6. Start the server in the program (on a free loopback port) and call it with `java.net.http.HttpClient`, then compare the status code and the JSON body. Browsers, `curl` or Postman work for manual tests.
7. Spring Boot starts the web server, finds your classes, maps routes with annotations (`@RestController`, `@GetMapping`, `@PostMapping`, `@PathVariable`, `@RequestBody`), converts JSON to objects with Jackson, validates input (`@Valid`) and handles errors for you.
8. Handlers that only take values and return a `Response` can be tested like normal methods without a server, and the router and server code is written once. This is the same "one method = one job" idea as the Day 29 pipeline.
