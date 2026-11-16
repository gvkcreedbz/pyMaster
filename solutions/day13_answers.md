# Day 13 — Quiz answers

1. `json.dumps` returns a **string**; `json.loads` takes a JSON **string** and returns Python data.
2. `null` → `None`, `true` → `True`.
3. `restaurants[0]["cuisines"][1]`.
4. A missing key would raise `KeyError`; `.get(key, {})` returns an empty dict so the chain keeps working and finally returns `None` or a default.
5. `.copy()` copies only the outer container (inner objects are shared); `deepcopy` copies everything recursively.
6. Yes — JSON object keys are always strings (`{1: "a"}` becomes `{"1": "a"}`).
7. `print(json.dumps(data, indent=2))`.
8. It becomes a JSON array (a list when loaded back).
