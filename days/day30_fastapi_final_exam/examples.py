"""Day 30 - Code along: a tiny FastAPI app.

Option A (no server): python examples.py          -> calls the app in-process and prints responses
Option B (live server): python -m uvicorn examples:app --reload
                        then open http://127.0.0.1:8000/docs   (Ctrl+C to stop)
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="Mini Shop API")

PRODUCTS = [
    {"id": 1, "name": "Pen", "price": 10.0},
    {"id": 2, "name": "Notebook", "price": 55.5},
    {"id": 3, "name": "Backpack", "price": 799.0},
]


class ProductIn(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}


@app.get("/products")
def list_products(min_price: float = 0):
    return [p for p in PRODUCTS if p["price"] >= min_price]


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", status_code=201)
def create_product(item: ProductIn):
    new = {"id": max(p["id"] for p in PRODUCTS) + 1, "name": item.name, "price": item.price}
    PRODUCTS.append(new)
    return new


@app.get("/top")
def top(n: int = Query(2, ge=1, le=3)):
    return sorted(PRODUCTS, key=lambda p: p["price"], reverse=True)[:n]


if __name__ == "__main__":
    client = TestClient(app)
    for method, url, body in [
        ("get", "/health", None),
        ("get", "/greet/Asha", None),
        ("get", "/products?min_price=50", None),
        ("get", "/products/2", None),
        ("get", "/products/99", None),
        ("get", "/products/abc", None),
        ("post", "/products", {"name": "Eraser", "price": 5}),
        ("post", "/products", {"name": "Bad", "price": -1}),
        ("get", "/top?n=5", None),
        ("get", "/top?n=1", None),
    ]:
        response = client.get(url) if method == "get" else client.post(url, json=body)
        shown = response.json()
        if response.status_code == 422:
            shown = "validation error: " + shown["detail"][0]["msg"]
        print(f"{method.upper():4} {url:26} -> {response.status_code} {shown}")
    print("\nWant a live server?  python -m uvicorn examples:app --reload   then open /docs")
