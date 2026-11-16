# Day 27 — APIs & Web Scraping: Getting Data from the Internet

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Call web APIs with `requests`, handle failures, parse HTML with BeautifulSoup | Upper-intermediate |

## 🌍 Real-world scenario & trend
**Your dashboard needs live data:** today's weather for a delivery route, posts from a service, prices from a web page. Nearly every app is glued together by **APIs** (ask a server a question, get JSON back). When no API exists, analysts **scrape** the page's HTML. **Trend:** AI apps are API clients — calling an LLM *is* a `POST` with JSON and an API key. Master this day and you can talk to almost any service.

## 0. Warm-up (5 min) — Day 26 recap
- What does `groupby("a")["b"].sum()` do?  • Why `plt.close(fig)`?

## 1. Setup (3 min)
```powershell
python -m pip install requests beautifulsoup4
```

## 2. Concepts

### 2.1 How the web talks (HTTP)
You send a **request** (method + URL + optional params/headers/body); the server sends a **response** (status code + headers + body).
| Method | Purpose |
|---|---|
| `GET` | read data |
| `POST` | create/send data (JSON body) |
| `PUT`/`PATCH` | update · `DELETE` removes |

| Status | Meaning |
|---|---|
| 200 / 201 | OK / created |
| 400 / 401 / 403 / 404 | bad request / not logged in / forbidden / not found |
| 429 | too many requests — slow down! |
| 500 / 503 | server error — maybe retry |

### 2.2 `requests` in 6 lines
```python
import requests
r = requests.get("https://api.open-meteo.com/v1/forecast",
                 params={"latitude": 18.52, "longitude": 73.86, "current": "temperature_2m"},
                 timeout=10)                  # ALWAYS set a timeout
r.status_code      # 200
r.raise_for_status()   # raises requests.HTTPError for 4xx/5xx
data = r.json()    # parse JSON into dicts/lists
r.text             # raw text (HTML etc.)
```
POST with JSON: `requests.post(url, json={"title": "Hi"}, headers={"Authorization": f"Bearer {token}"}, timeout=10)`.

### 2.3 Never hard-code secrets
```python
import os
API_KEY = os.environ["WEATHER_API_KEY"]        # set in your terminal / .env file, never in code or Git
```

### 2.4 Failures are normal — design for them
Network down, timeouts, 500s, rate limits. Use `timeout=`, `try/except requests.RequestException`, **retries with a pause** (`time.sleep`, growing delays = *exponential backoff*), and never loop forever.

### 2.5 Making code testable: pass the function in
```python
def fetch_json(url, get=requests.get):      # `get` can be replaced by a fake in tests!
    response = get(url, timeout=10)
    ...
```
Tests (and today's checker) pass a **fake** `get`, so no internet is needed and results are repeatable. Professionals call this *dependency injection*.

### 2.6 Scraping with BeautifulSoup
```python
from bs4 import BeautifulSoup
html = '<div class="quote"><span class="text">Hi</span><small class="author">Ann</small></div>'
soup = BeautifulSoup(html, "html.parser")
for quote in soup.select("div.quote"):            # CSS selectors: tag.class, #id, parent child
    text = quote.select_one("span.text").get_text(strip=True)
    author = quote.select_one(".author").get_text(strip=True)
link = soup.select_one("li.next a")               # None if missing!
link["href"] if link else None                    # attributes work like a dict
```
**Be a good citizen:** read the site's `robots.txt` and terms, rate-limit yourself (sleep between requests), identify yourself with a `User-Agent`, prefer an official API, and never scrape personal data or paywalled content. Practice on sites built for it: `quotes.toscrape.com`, `books.toscrape.com`.

## 3. Code along → `examples.py` (calls 3 live public endpoints; works offline too — it just says so)

## 4. Common mistakes
- No `timeout` → your script hangs forever.
- Ignoring the status code and calling `.json()` on an error page.
- Committing API keys to Git.
- Assuming an element exists (`select_one` returns `None`) → `AttributeError`.
- Hammering a site with thousands of requests per second.
- Scraping JavaScript-rendered pages with `requests` (the data isn't in the HTML — look for the JSON API in the browser's *Network* tab, or use Playwright).

## 5. Today's tasks → `practice.py` (fully offline — fake responses)
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Build a URL with params, read fields from API JSON, classify status codes |
| L2-1…L2-3 | 🟡 | `fetch_json` with error handling, retry logic, scrape book titles & prices |
| L3-1, L3-2 | 🔴 | Aggregate API posts per user, scrape quotes with pagination |

## 6. Stuck? Hint ladder
<details><summary>Hint 1</summary>Draw the data: write the JSON on paper and mark the path to the value (<code>data["current"]["temperature_2m"]</code>). For HTML, find the tag/class that wraps each item.</details>
<details><summary>Hint 2</summary><code>from urllib.parse import urlencode</code> → <code>base + "?" + urlencode(params)</code>. Retry: <code>for attempt in range(attempts):</code> with <code>try/except</code>, remember the last error, call <code>sleep(...)</code> between tries, raise after the loop. Scrape: <code>soup.select("article.product_pod")</code> then <code>.select_one(...)</code> inside each.</details>
<details><summary>Hint 3</summary><code>solutions/day27_solution.py</code></details>

## 7. Quiz — answers in `solutions/day27_answers.md`
1. Difference between `GET` and `POST`?
2. What does status 404 mean? 429? 503?
3. Why must you pass `timeout=` to `requests.get`?
4. What does `raise_for_status()` do?
5. Where should an API key live?
6. Why is `fetch_json(url, get=requests.get)` easier to test?
7. What does `soup.select_one(".x")` return when nothing matches?
8. Name three rules of polite scraping.

## 8. Wrap-up
Tracker + Bug Journal. Tomorrow: databases — SQLite and SQL.
