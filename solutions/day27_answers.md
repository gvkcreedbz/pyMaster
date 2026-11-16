# Day 27 — Quiz answers

1. `GET` reads data (parameters in the URL, safe to repeat); `POST` sends data in the body to create/trigger something (e.g. JSON, a login, an LLM prompt).
2. 404 = resource not found; 429 = too many requests (rate-limited — slow down/back off); 503 = service unavailable (server problem, often temporary — retry later).
3. Without it, `requests` can wait forever for a dead server and freeze your program.
4. It raises `requests.HTTPError` if the status code is 4xx or 5xx, so errors can't slip through silently.
5. In an environment variable or a secrets manager / `.env` file that is git-ignored — never in source code or the repository.
6. Tests can pass a fake `get`, so no internet is needed and responses (including failures) are predictable and fast.
7. `None` — so check before using it (`if element:`) or you'll get `AttributeError`.
8. Any three: read `robots.txt`/terms; rate-limit with sleeps; send an honest `User-Agent`; prefer official APIs; cache results; don't collect personal data or bypass paywalls.
