# SOLUTION FILE - try the hint ladder first!
"""Day 30 - Practice: a FastAPI mini service.

Run the checks:   python practice.py          (needs: fastapi httpx pandas)
Run it as a server:  python -m uvicorn practice:app --reload   -> open http://127.0.0.1:8000/docs
The @app.xxx line and the function signature are given - write each function body.
`PRODUCTS` is an in-memory list: mutate it (append), don't re-assign it.
"""
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Mini Shop API")

PRODUCTS = [
    {"id": 1, "name": "Pen", "price": 10.0},
    {"id": 2, "name": "Notebook", "price": 55.5},
    {"id": 3, "name": "Backpack", "price": 799.0},
]


def _find_sales_csv():
    for parent in Path(__file__).resolve().parents:
        if (parent / "datasets" / "sales.csv").is_file():
            return parent / "datasets" / "sales.csv"


SALES_CSV = _find_sales_csv()


class ProductIn(BaseModel):
    """Body of POST /products: name must not be empty, price must be > 0."""
    name: str = Field(min_length=1)
    price: float = Field(gt=0)


# ---------------------------------------------------------------------------
# L1-1 | GET /health   (Level 1 - Beginner)
# Return {"status": "ok"}
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    # >>> SOLUTION
    return {"status": "ok"}
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | GET /greet/{name}   (Level 1 - Beginner)
# Return {"message": "Hello, <name>!"}
# ---------------------------------------------------------------------------
@app.get("/greet/{name}")
def greet(name: str):
    # >>> SOLUTION
    return {"message": f"Hello, {name}!"}
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | GET /products?min_price=   (Level 2 - Intermediate)
# Return the list of products whose price is >= min_price (default 0 = all).
# ---------------------------------------------------------------------------
@app.get("/products")
def list_products(min_price: float = 0):
    # >>> SOLUTION
    return [p for p in PRODUCTS if p["price"] >= min_price]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | GET /products/{product_id}   (Level 2 - Intermediate)
# Return the product with that id, or raise HTTPException(404, "Product not found").
# ---------------------------------------------------------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):
    # >>> SOLUTION
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | POST /products   (Level 2 - Intermediate)
# Create a product: new id = (largest existing id) + 1; store {"id","name","price"} in
# PRODUCTS (append) and return it. Status 201 is already set in the decorator and the
# ProductIn model above rejects invalid bodies (422) for you.
# ---------------------------------------------------------------------------
@app.post("/products", status_code=201)
def create_product(item: ProductIn):
    # >>> SOLUTION
    new = {"id": max(p["id"] for p in PRODUCTS) + 1, "name": item.name, "price": item.price}
    PRODUCTS.append(new)
    return new
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | GET /sales/summary   (Level 3 - Challenge)
# Read SALES_CSV with pandas. revenue = quantity * unit_price * (1 - discount_pct / 100).
# Return {"orders": int, "total_revenue": float (2 dp),
#         "by_region": {region: revenue (2 dp), ...}}  - plain Python numbers only!
# ---------------------------------------------------------------------------
@app.get("/sales/summary")
def sales_summary():
    # >>> SOLUTION
    df = pd.read_csv(SALES_CSV)
    df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    return {
        "orders": int(len(df)),
        "total_revenue": round(float(df["revenue"].sum()), 2),
        "by_region": {region: round(float(value), 2) for region, value in df.groupby("region")["revenue"].sum().items()},
    }
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | GET /sales/top-products?n=   (Level 3 - Challenge)
# n must be between 1 and 10 (default 3) - the Query(...) in the signature makes FastAPI
# answer 422 otherwise. Return [{"product": name, "revenue": total (2 dp)}, ...], best first.
# ---------------------------------------------------------------------------
@app.get("/sales/top-products")
def top_products(n: int = Query(3, ge=1, le=10)):
    # >>> SOLUTION
    df = pd.read_csv(SALES_CSV)
    df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    totals = df.groupby("product")["revenue"].sum().nlargest(n)
    return [{"product": name, "revenue": round(float(value), 2)} for name, value in totals.items()]
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
from fastapi.testclient import TestClient

_ok = []
_client = TestClient(app)
_ORIGINAL = [dict(p) for p in PRODUCTS]


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


def _reset():
    PRODUCTS[:] = [dict(p) for p in _ORIGINAL]


def _get(url):
    r = _client.get(url)
    return r.status_code, r.json()


def _create_check():
    _reset()
    r = _client.post("/products", json={"name": "Eraser", "price": 5})
    created = (r.status_code, r.json())
    listing = [p["id"] for p in _client.get("/products").json()]
    bad_price = _client.post("/products", json={"name": "Bad", "price": -1}).status_code
    bad_name = _client.post("/products", json={"name": "", "price": 5}).status_code
    second = _client.post("/products", json={"name": "Ruler", "price": 12.5}).json()["id"]
    _reset()
    return created, listing, bad_price, bad_name, second


print("--- Day 30 checks ---")
check("L1-1 GET /health", lambda: _get("/health"), (200, {"status": "ok"}))
check("L1-2 GET /greet/Asha", lambda: _get("/greet/Asha"), (200, {"message": "Hello, Asha!"}))
check("L2-1 GET /products (all)", lambda: [p["id"] for p in _get("/products")[1]], [1, 2, 3])
check("L2-1 GET /products?min_price=50", lambda: [p["id"] for p in _get("/products?min_price=50")[1]], [2, 3])
check("L2-1 GET /products?min_price=1000", lambda: _get("/products?min_price=1000"), (200, []))
check("L2-2 GET /products/2", lambda: _get("/products/2"), (200, {"id": 2, "name": "Notebook", "price": 55.5}))
check("L2-2 GET /products/99 -> 404", lambda: _get("/products/99"), (404, {"detail": "Product not found"}))
check("L2-3 POST /products (201, saved, 422 on bad data, next id)", _create_check,
      ((201, {"id": 4, "name": "Eraser", "price": 5.0}), [1, 2, 3, 4], 422, 422, 5))
check("L3-1 GET /sales/summary", lambda: _get("/sales/summary"), (200, {
    "orders": 300, "total_revenue": 1443241.55,
    "by_region": {"East": 335268.6, "North": 300446.25, "South": 348849.7, "West": 458677.0}}))
check("L3-2 GET /sales/top-products (default 3)", lambda: _get("/sales/top-products"), (200, [
    {"product": "Smartwatch", "revenue": 298814.6}, {"product": "Air Fryer", "revenue": 279194.15},
    {"product": "Running Shoes", "revenue": 143652.1}]))
check("L3-2 top-products?n=1", lambda: len(_get("/sales/top-products?n=1")[1]), 1)
check("L3-2 top-products n=0 and n=11 -> 422", lambda: (_client.get("/sales/top-products?n=0").status_code,
                                                         _client.get("/sales/top-products?n=11").status_code), (422, 422))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
