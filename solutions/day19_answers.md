# Day 19 — Quiz answers

1. A class is the blueprint (definition); an object (instance) is one concrete thing created from it. `Product` is a class; `Product("Pen", 10)` is an object.
2. The specific object the method is being called on (e.g. in `pen.discounted_price(5)`, `self` is `pen`).
3. Automatically, right when you create an object: `Product("Pen", 10)`.
4. Something like `<__main__.Product object at 0x000001...>` — define `__str__` to control it.
5. A class attribute is defined in the class body and shared by all objects; an instance attribute is set on `self` and belongs to one object.
6. To run validation/logic when an attribute is read or assigned while it still looks like a normal attribute (`t.celsius = -300` raises an error).
7. “Internal detail — use the public methods instead.” Python doesn't enforce it.
8. The list is created once and **shared by all carts**, so adding to one cart changes every cart. Create it inside `__init__` (`self.items = []`).
