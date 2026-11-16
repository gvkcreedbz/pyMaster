# 📊 Data & Tools Cheatsheet (Week 4: NumPy · pandas · regex · SQL · APIs · pytest · Git · FastAPI)

## NumPy
```python
import numpy as np
a = np.array([1, 2, 3]);  a * 2;  a + a;  a > 1;  a[a > 1]          # vectorised, boolean mask
np.arange(0, 10, 2);  np.linspace(0, 1, 5);  np.zeros((2, 3));  np.ones(3)
m = np.array([[1, 2, 3], [4, 5, 6]]);  m.shape;  m.T;  m[:, 1];  m.sum(axis=0)   # axis=0 → per column, axis=1 → per row
a.mean() a.std() a.min() a.max() a.argmax()  np.round(a, 2)  np.where(a > 1, "big", "small")
```

## pandas
```python
import pandas as pd
df = pd.read_csv("file.csv", parse_dates=["date"])        # also read_json, read_sql, read_excel
df.shape  df.head()  df.tail()  df.info()  df.describe()  df.dtypes  df.columns  df.isna().sum()

df["col"]  df[["a", "b"]]  df.loc[row_label, "col"]  df.iloc[0]  df.loc[mask, ["a", "b"]]
df[(df.region == "West") & (df.qty >= 5)]                  # & | ~  with brackets!
df[df.city.isin(["A", "B"])]   df[df.name.str.contains("kit", case=False)]
df["revenue"] = df.qty * df.price * (1 - df.disc / 100)    # new column, vectorised
df.sort_values("revenue", ascending=False)   df.nlargest(3, "revenue")   df.value_counts("region")

# cleaning
df.drop_duplicates()   df.dropna(subset=["qty"])   df["x"].fillna(0)   df["t"].str.strip().str.title()
df["p"].astype(str).str.replace(",", "").astype(int)   pd.to_datetime(df["d"])   df.reset_index(drop=True)
df.rename(columns={"old": "new"})   df.drop(columns=["x"])   df["d"].dt.month   df["d"].dt.to_period("M")

# summarising
df.groupby("region")["revenue"].sum()
df.groupby("cat").agg(orders=("id", "count"), revenue=("revenue", "sum"), avg=("revenue", "mean"))
df.groupby(["region", "cat"])["revenue"].sum().reset_index()
df.pivot_table(index="region", columns="cat", values="revenue", aggfunc="sum", fill_value=0)
a.merge(b, on="key", how="left")      # inner · left · right · outer
pd.concat([df1, df2], ignore_index=True)
df.to_csv("out.csv", index=False)     df.to_sql("t", conn, if_exists="replace", index=False)
```
Rules: no row loops · `.copy()` after filtering · methods return new objects (assign them) · clean keys before merging.

## matplotlib
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(names, values)        # compare categories      ax.plot(x, y, marker="o")  # trends
ax.hist(values, bins=10)     # distribution            ax.scatter(x, y)           # relationship
ax.set_title("…"); ax.set_xlabel("…"); ax.set_ylabel("…"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig("chart.png", dpi=120); plt.show(); plt.close(fig)
df.plot(kind="bar", x="region", y="revenue")               # pandas shortcut
```

## Regex (`import re`, always raw strings)
| Pattern | Meaning | | Function | Use |
|---|---|---|---|---|
| `\d \w \s` | digit / word / space (caps = opposite) | | `re.search(p, s)` | first match anywhere (or `None`) |
| `. [abc] [^abc] [a-z]` | any / set / not / range | | `re.findall(p, s)` | list of all matches |
| `* + ? {3} {2,5}` | repeat (add `?` = lazy) | | `re.fullmatch(p, s)` | whole-string validation |
| `^ $ \b` | start / end / word edge | | `re.sub(p, repl, s)` | replace (`\1` = group 1) |
| `(…) (?:…) (?P<n>…) \|` | group / no-capture / named / or | | `re.split(p, s)` | split on pattern |
| flags: `re.I` ignore case | | | `m.group() m.groups() m.groupdict()` | read a match |

## SQL (SQLite via `sqlite3`)
```sql
CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL);
INSERT INTO t (name, price) VALUES (?, ?);   UPDATE t SET price = ? WHERE id = ?;   DELETE FROM t WHERE id = ?;
SELECT region, SUM(qty * price) AS revenue          -- 5. what to show
FROM orders                                         -- 1. table
WHERE order_date >= '2026-06-01'                    -- 2. filter rows
GROUP BY region                                     -- 3. groups
HAVING SUM(qty * price) > 1000                      -- 4. filter groups
ORDER BY revenue DESC  LIMIT 5;                     -- 6/7.
SELECT c.name, COALESCE(SUM(p.amount), 0) FROM customers c LEFT JOIN purchases p ON p.customer_id = c.id GROUP BY c.id;
-- strftime('%Y-%m', date)  ROUND(x, 2)  COUNT(DISTINCT col)  LIKE '%kit%'  IN (...)  BETWEEN a AND b  IS NULL
```
```python
import sqlite3
conn = sqlite3.connect("shop.db")                    # ":memory:" for a temp DB
conn.execute("INSERT INTO t (name) VALUES (?)", ("Pen",));  conn.commit()      # ALWAYS ? placeholders, a tuple
rows = conn.execute("SELECT * FROM t WHERE price > ?", (10,)).fetchall()       # list of tuples
with conn:  ...                                      # commit on success, rollback on error
```

## HTTP & scraping
```python
import requests
r = requests.get(url, params={"q": "x"}, headers={"User-Agent": "me"}, timeout=10)
r.status_code;  r.raise_for_status();  r.json();  r.text
requests.post(url, json={"a": 1}, headers={"Authorization": f"Bearer {token}"}, timeout=10)
import os;  KEY = os.environ["API_KEY"]               # never hard-code secrets
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
soup.select("div.quote");  soup.select_one("a.next")["href"];  el.get_text(strip=True)
```
Status codes: **200** OK · **201** created · **400** bad request · **401** unauthorised · **403** forbidden · **404** not found · **422** invalid data · **429** slow down · **500/503** server trouble (retry with backoff).

## pytest
```python
import pytest
def test_add():  assert add(2, 3) == 5
def test_error():
    with pytest.raises(ValueError): withdraw(-5)
@pytest.mark.parametrize("a, b, want", [(1, 2, 3), (0, 0, 0)])
def test_table(a, b, want):  assert add(a, b) == want
@pytest.fixture
def cart():  return Cart()
assert 0.1 + 0.2 == pytest.approx(0.3)
```
Run: `python -m pytest -v` · one test `-k name` · stop at first failure `-x`. Files `test_*.py`, functions `test_*`.

## Git
```powershell
git config --global user.name "Name";  git config --global user.email "you@example.com"
git init;  git status;  git add .;  git commit -m "message";  git log --oneline;  git diff
git switch -c feature/x;  git switch main;  git merge feature/x
git remote add origin <url>;  git push -u origin main;  git pull
```
`.gitignore`: `.venv/  __pycache__/  .env  *.pyc  output/` — never commit secrets.

## FastAPI
```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
app = FastAPI()
class ItemIn(BaseModel):  name: str = Field(min_length=1);  price: float = Field(gt=0)
@app.get("/items/{item_id}")
def get_item(item_id: int, verbose: bool = False): ...            # path + query params
@app.post("/items", status_code=201)
def create(item: ItemIn): ...                                     # validated JSON body
@app.get("/top")
def top(n: int = Query(3, ge=1, le=10)): ...
raise HTTPException(status_code=404, detail="Not found")
```
Run: `python -m uvicorn myfile:app --reload` → `http://127.0.0.1:8000/docs`. Test: `TestClient(app).get("/items/1")`.

## argparse & logging skeleton for scripts
```python
import argparse, logging
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="…");  p.add_argument("--input", required=True);  p.add_argument("--out", default="output")
    args = p.parse_args(argv);  logging.basicConfig(level=logging.INFO)
    ...;  return 0
if __name__ == "__main__":  raise SystemExit(main())
```
