# Day 30 — FastAPI Taste & The Final Exam 🎓

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Turn Python into a web API in minutes, then prove your "reads code like a pro" skill with a 27-question exam | Upper-intermediate ✅ |

## 🌍 Real-world scenario & trend
**The mobile-app team needs your data.** They can't open your CSV or call your functions — they speak **HTTP + JSON**. FastAPI turns ordinary Python functions into a documented, validated web API with almost no code. **Trend:** FastAPI is the default way to serve ML models and AI agents in Python (LLM backends, RAG services, automation webhooks). Everything today is built on skills you already have: functions, dicts, type hints, pandas.

## ⏱ Suggested schedule
| Time | Activity |
|---|---|
| 0:00–0:10 | Warm-up + read this lesson |
| 0:10–0:25 | Code along (`examples.py`), run a live server and open `/docs` |
| 0:25–1:05 | `practice.py` (7 routes) |
| 1:05–1:50 | **Final exam** → `FINAL_EXAM.md` (closed-book, 45 min, no running code!) |
| 1:50–2:00 | Mark it, update the tracker, write your reflection |

## 0. Warm-up (5 min)
- What does an HTTP status 404 mean?  • What is JSON? (Write one object by hand.)

## 1. Setup
```powershell
python -m pip install fastapi uvicorn httpx pandas
```

## 2. Concepts

### 2.1 Hello, API
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")                  # decorator = "when someone GETs /health, run this"
def health():
    return {"status": "ok"}          # dict -> JSON automatically
```
Run the server: `python -m uvicorn examples:app --reload` (in this folder) → open <http://127.0.0.1:8000/health> and the **auto-generated docs** at <http://127.0.0.1:8000/docs> (try endpoints right in the browser!). Stop with `Ctrl+C`.

### 2.2 Path & query parameters (type hints do the validation!)
```python
@app.get("/greet/{name}")                       # path parameter
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/products")                           # /products?min_price=50   (query parameter)
def products(min_price: float = 0):
    return [p for p in PRODUCTS if p["price"] >= min_price]
```
Send `min_price=abc` → FastAPI answers **422** automatically. You wrote no validation code!

### 2.3 Errors: `HTTPException`
```python
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Product not found")
```

### 2.4 Request bodies with Pydantic models
```python
from pydantic import BaseModel, Field
class ProductIn(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)               # must be > 0

@app.post("/products", status_code=201)
def create_product(item: ProductIn):         # JSON body is parsed + validated into `item`
    ...
```
A body that breaks the rules → 422 with a precise error message.

### 2.5 Extra validation on query params
```python
from fastapi import Query
def top(n: int = Query(3, ge=1, le=10)): ...   # 1 <= n <= 10, default 3
```

### 2.6 Testing an API without a server
```python
from fastapi.testclient import TestClient
client = TestClient(app)
r = client.get("/health"); r.status_code, r.json()
r = client.post("/products", json={"name": "Pen", "price": 10})
```
This is what today's auto-checker does (Day 24 skills!).

### 2.7 Where to go from here — your 30-60-90 map
- **Data/AI:** scikit-learn (ML basics) → PyTorch or the OpenAI/Anthropic SDKs → build a RAG chatbot over your own documents.
- **Backend:** FastAPI + PostgreSQL + SQLAlchemy → authentication (JWT) → Docker → deploy (Render / Railway / AWS).
- **Automation:** Playwright (browser automation), `schedule`/cron, Excel automation (`openpyxl`), email/Slack bots.
- **Always:** one project a month on GitHub; read other people's code daily; use AI assistants as a *reviewer and tutor* — you now have the skills to verify what they write.

## 3. Common mistakes
- Forgetting `return` (the API answers `null`).
- Rebinding the global list instead of mutating it (`PRODUCTS = [...]` inside a function creates a *local* variable).
- Returning a pandas object instead of plain dicts/lists/numbers.
- Using `async def` everywhere without needing it (plain `def` is fine and safe for now).
- Putting secrets in code; allowing everything with no validation.

## 4. Today's tasks → `practice.py` (the `@app...` decorator and function signature are given)
| ID | Level | Task |
|---|---|---|
| L1-1, L1-2 | 🟢 | `/health`, `/greet/{name}` |
| L2-1…L2-3 | 🟡 | list with filter, get-one with 404, create with validation (201) |
| L3-1, L3-2 | 🔴 | `/sales/summary` from the CSV, `/sales/top-products?n=` with `Query` limits |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Say in words what the endpoint returns, then write the dict. For 404, a <code>for</code> loop over <code>PRODUCTS</code> with an early <code>return</code> and an <code>HTTPException</code> after the loop.</details>
<details><summary>Hint 2</summary>New id: <code>max(p["id"] for p in PRODUCTS) + 1</code>. Use <code>item.name</code> and <code>item.price</code>; <code>PRODUCTS.append(new)</code>. For sales use pandas <code>read_csv(SALES_CSV)</code>, compute <code>revenue</code>, <code>groupby</code>, then <code>.round(2).to_dict()</code>; convert numpy numbers with <code>float(...)</code>/<code>int(...)</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day30_solution.py</code></details>

## 6. 🎓 FINAL EXAM (45 min, closed-book)
Open **`FINAL_EXAM.md`**. 27 questions: *"What does this code print?"* across all 4 weeks, including 3 *"find the bug"* ones. Rules: no running code, no AI, answers on paper or in the tracker; 1 point each. Then check `solutions/day30_exam_answers.md`.

| Score (of 27) | Meaning |
|---|---|
| 24–27 | 🏆 You read Python like a professional. Start a real project this week. |
| 19–23 | ✅ Solid upper-intermediate. Redo the topics of the questions you missed. |
| 13–18 | 🟡 Good foundation — repeat Days of your weak areas (see "Day" tags), then retake in 3 days. |
| < 13 | 🔁 Re-do Weeks 1–2 exercises quickly (they're fast the second time), then retake. |

## 7. Quiz — answers in `solutions/day30_answers.md`
1. What does `@app.get("/x")` do?
2. What returns 422 automatically in FastAPI?
3. Why use a Pydantic model for POST bodies?
4. Where do you find the auto-generated API docs?
5. How do you test an API without starting a server?
6. Why is `status_code=201` used for creating things?

## 8. Wrap-up — you did it! 🎉
Fill the **Weekly Review** and **Dashboard** in the tracker, add your final exam score, and write 3 sentences: *What am I proudest of? What was hardest? What will I build next?*
