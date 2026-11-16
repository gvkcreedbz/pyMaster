# Day 30 — Quiz answers

1. It registers the function below it as the handler for `GET /x`: when a client requests that path, FastAPI calls the function and converts the returned dict/list to JSON.
2. Requests whose path/query/body don't match the type hints or constraints (e.g. `n=abc`, a negative price with `Field(gt=0)`, a missing required field).
3. It declares the shape and rules of the JSON body once; FastAPI parses, validates, converts types and documents it automatically, giving clear 422 errors.
4. At `/docs` (Swagger UI) and `/redoc` on the running server.
5. Use `fastapi.testclient.TestClient(app)` and call `client.get(...)` / `client.post(...)` in-process (e.g. inside pytest).
6. `201 Created` tells the client a new resource was made successfully (more precise than a generic 200).

The 25-question final exam answers (with explanations) are in `day30_exam_answers.md`.
