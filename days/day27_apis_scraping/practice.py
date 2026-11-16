"""Day 27 - Practice: APIs and scraping (all offline, with fake responses).

Run:  python practice.py          (needs: python -m pip install requests beautifulsoup4)
"""
import re
import time
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# L1-1 | build_url   (Level 1 - Beginner)
# Join a base URL and a dict of query parameters:
#   build_url("https://api.x.com/search", {"q": "python", "page": 2})
#   -> "https://api.x.com/search?q=python&page=2"        (no params -> just the base)
# ---------------------------------------------------------------------------
def build_url(base, params):
    """Return base + '?' + encoded params."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | parse_weather   (Level 1 - Beginner)
# The API returns e.g. {"latitude": 18.5, "current": {"temperature_2m": 28.5,
# "wind_speed_10m": 12.3, "time": "2026-11-16T10:00"}}.
# Return {"temp": 28.5, "wind": 12.3, "time": "2026-11-16T10:00"}.
# ---------------------------------------------------------------------------
def parse_weather(data):
    """Pick the useful fields."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | status_category   (Level 1 - Beginner)
# Return "success" for 200-299, "client error" for 400-499, "server error" for 500-599,
# "other" for everything else.
# ---------------------------------------------------------------------------
def status_category(code):
    """Classify an HTTP status code."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | fetch_json   (Level 2 - Intermediate)
# Call get(url, timeout=10). If the response's status_code is not 200 raise
# RuntimeError(f"HTTP {status_code}"). Otherwise return response.json().
# `get` is a parameter so we can pass a FAKE one (no internet needed).
# ---------------------------------------------------------------------------
def fetch_json(url, get=requests.get):
    """Return parsed JSON or raise RuntimeError."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | fetch_with_retry   (Level 2 - Intermediate)
# Try up to `attempts` times. A try FAILS when get() raises ConnectionError/Timeout
# (any Exception) or the status code is 500 or above. After a failed try, if more tries
# remain, call sleep(2 ** attempt_number) (attempt_number starts at 0).
# A 4xx status is NOT retried - raise RuntimeError(f"HTTP {code}") immediately.
# Success (200) -> return response.json(). All tries failed -> raise RuntimeError("giving up").
# ---------------------------------------------------------------------------
def fetch_with_retry(url, get=requests.get, attempts=3, sleep=time.sleep):
    """GET with retries and exponential backoff."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | parse_books   (Level 2 - Intermediate)
# HTML has several  <article class="product_pod">  blocks, each with
#   <h3><a title="Full Title">Short...</a></h3>  and  <p class="price_color">£51.77</p>.
# Return [{"title": "Full Title", "price": 51.77}, ...] (price as float).
# ---------------------------------------------------------------------------
def parse_books(html):
    """Scrape titles and prices."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | posts_per_user   (Level 3 - Challenge)
# posts is a list of dicts like {"userId": 1, "id": 7, "title": "..."} (API output).
# Return {userId: number of posts}, ordered by userId ascending.
# ---------------------------------------------------------------------------
def posts_per_user(posts):
    """Count posts per user."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | scrape_quotes   (Level 3 - Challenge)
# Each quote:  <div class="quote"><span class="text">...</span>
#   <small class="author">Name</small><div class="tags"><a class="tag">x</a>...</div></div>
# Pagination:  <li class="next"><a href="/page/2/">Next</a></li>  (absent on the last page)
# Return {"quotes": [{"text":..., "author":..., "tags": [...]}, ...], "next": "/page/2/" or None}
# ---------------------------------------------------------------------------
def scrape_quotes(html):
    """Scrape one page of quotes plus the next-page link."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ======================= AUTO-CHECKER (do not edit below) ====================
_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


class _FakeResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data


def _fake_get(*responses):
    """Return a fake `get` that yields the given responses/exceptions one by one; records calls."""
    queue = list(responses)
    calls = []

    def get(url, timeout=None):
        calls.append((url, timeout))
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    get.calls = calls
    return get


def _error_of(fn):
    try:
        return ("ok", fn())
    except Exception as e:
        return (type(e).__name__, str(e))


def _retry_scenarios():
    results = {}
    sleeps = []
    get = _fake_get(ConnectionError("down"), _FakeResponse(503), _FakeResponse(200, {"ok": 1}))
    results["recovers"] = (fetch_with_retry("u", get, 3, sleeps.append), len(get.calls), sleeps)
    sleeps2 = []
    get2 = _fake_get(_FakeResponse(500), _FakeResponse(500), _FakeResponse(502))
    results["gives_up"] = (_error_of(lambda: fetch_with_retry("u", get2, 3, sleeps2.append)), len(get2.calls), sleeps2)
    get3 = _fake_get(_FakeResponse(404))
    results["client_error"] = (_error_of(lambda: fetch_with_retry("u", get3, 3, lambda s: None)), len(get3.calls))
    return results


_BOOKS_HTML = """
<section>
<article class="product_pod"><h3><a href="a.html" title="A Light in the Attic">A Light in the ...</a></h3>
  <div class="product_price"><p class="price_color">£51.77</p></div></article>
<article class="product_pod"><h3><a href="b.html" title="Tipping the Velvet">Tipping the ...</a></h3>
  <div class="product_price"><p class="price_color">£53.74</p></div></article>
</section>"""

_QUOTES_HTML = """
<div class="quote"><span class="text">Be yourself.</span><span>by <small class="author">Oscar Wilde</small></span>
  <div class="tags"><a class="tag">inspirational</a><a class="tag">life</a></div></div>
<div class="quote"><span class="text">Stay hungry.</span><span>by <small class="author">Steve Jobs</small></span>
  <div class="tags"></div></div>
<nav><ul class="pager"><li class="next"><a href="/page/2/">Next</a></li></ul></nav>"""

_QUOTES_LAST = '<div class="quote"><span class="text">The end.</span><small class="author">Anon</small><div class="tags"></div></div>'

print("--- Day 27 checks ---")
check("L1-1 build_url", lambda: (build_url("https://api.x.com/search", {"q": "python", "page": 2}), build_url("https://x.com", {}),
                                  build_url("https://x.com/s", {"q": "a b"})),
      ("https://api.x.com/search?q=python&page=2", "https://x.com", "https://x.com/s?q=a+b"))
check("L1-2 parse_weather", lambda: parse_weather({"latitude": 18.5, "current": {"temperature_2m": 28.5, "wind_speed_10m": 12.3, "time": "2026-11-16T10:00"}}),
      {"temp": 28.5, "wind": 12.3, "time": "2026-11-16T10:00"})
check("L1-3 status_category", lambda: [status_category(c) for c in (200, 201, 301, 404, 429, 500, 503, 100)],
      ["success", "success", "other", "client error", "client error", "server error", "server error", "other"])
_g = _fake_get(_FakeResponse(200, {"a": 1}))
check("L2-1 fetch_json success + timeout", lambda: (fetch_json("u", _g), _g.calls), ({"a": 1}, [("u", 10)]))
check("L2-1 fetch_json non-200 raises", lambda: _error_of(lambda: fetch_json("u", _fake_get(_FakeResponse(404)))), ("RuntimeError", "HTTP 404"))
_r = _retry_scenarios
check("L2-2 retry recovers (2 failures then success, backoff 1s, 2s)", lambda: _r()["recovers"], ({"ok": 1}, 3, [1, 2]))
check("L2-2 retry gives up after 3 failures", lambda: _r()["gives_up"], (("RuntimeError", "giving up"), 3, [1, 2]))
check("L2-2 retry does NOT retry a 404", lambda: _r()["client_error"], (("RuntimeError", "HTTP 404"), 1))
check("L2-3 parse_books", lambda: parse_books(_BOOKS_HTML),
      [{"title": "A Light in the Attic", "price": 51.77}, {"title": "Tipping the Velvet", "price": 53.74}])
check("L3-1 posts_per_user", lambda: posts_per_user([{"userId": 2, "id": 1}, {"userId": 1, "id": 2}, {"userId": 2, "id": 3}, {"userId": 2, "id": 4}]),
      {1: 1, 2: 3})
check("L3-2 scrape_quotes (with next page)", lambda: scrape_quotes(_QUOTES_HTML), {
    "quotes": [{"text": "Be yourself.", "author": "Oscar Wilde", "tags": ["inspirational", "life"]},
               {"text": "Stay hungry.", "author": "Steve Jobs", "tags": []}],
    "next": "/page/2/"})
check("L3-2 scrape_quotes (last page)", lambda: scrape_quotes(_QUOTES_LAST)["next"], None)
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
