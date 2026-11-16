"""Day 27 - Code along: a JSON API, a list API, and scraping a practice site.

Needs internet. Offline? Each part catches the error and says so - the script still finishes.
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "python-learning-journey/1.0"}


def section(title):
    print(f"\n=== {title} ===")


# ---- 1. A JSON API with query parameters (no key needed) ----
section("Weather API (Open-Meteo)")
try:
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": 18.52, "longitude": 73.86, "current": "temperature_2m,wind_speed_10m"},
        headers=HEADERS,
        timeout=10,
    )
    print("URL used   :", response.url)
    print("status     :", response.status_code)
    response.raise_for_status()
    current = response.json()["current"]
    print(f"Pune now   : {current['temperature_2m']} C, wind {current['wind_speed_10m']} km/h at {current['time']}")
except requests.RequestException as error:
    print("Could not reach the API (offline?):", type(error).__name__)

# ---- 2. A list API: count posts per user ----
section("Posts API (JSONPlaceholder)")
try:
    posts = requests.get("https://jsonplaceholder.typicode.com/posts", headers=HEADERS, timeout=10).json()
    per_user = {}
    for post in posts:
        per_user[post["userId"]] = per_user.get(post["userId"], 0) + 1
    print("total posts:", len(posts), "| posts per user:", per_user)
    print("first title:", posts[0]["title"])
except requests.RequestException as error:
    print("Could not reach the API (offline?):", type(error).__name__)

# ---- 3. Scraping (a site made for practice) ----
section("Scraping quotes.toscrape.com")
try:
    html = requests.get("http://quotes.toscrape.com/", headers=HEADERS, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    for quote in soup.select("div.quote")[:3]:
        text = quote.select_one("span.text").get_text(strip=True)
        author = quote.select_one("small.author").get_text(strip=True)
        tags = [tag.get_text() for tag in quote.select("a.tag")]
        print(f"- {text[:60]}... | {author} | {tags}")
    next_link = soup.select_one("li.next a")
    print("next page:", next_link["href"] if next_link else None)
except requests.RequestException as error:
    print("Could not reach the site (offline?):", type(error).__name__)

# ---- 4. Always: timeouts + friendly errors ----
section("Error handling demo")
try:
    requests.get("https://httpbin.org/status/503", timeout=10).raise_for_status()
except requests.HTTPError as error:
    print("HTTP problem:", error.response.status_code)
except requests.RequestException as error:
    print("Network problem (offline?):", type(error).__name__)
