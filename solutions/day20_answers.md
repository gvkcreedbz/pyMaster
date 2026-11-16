# Day 20 — Quiz answers

1. It calls the parent class's `__init__`, so the parent's setup (its attributes) happens for the child too.
2. The same method call (`obj.pay()`) works on different kinds of objects, and each object runs its own version.
3. `__len__` makes `len(obj)` work; `__add__` makes `a + b` work.
4. `@classmethod` receives the class (`cls`) — good for alternative constructors; `@staticmethod` receives neither class nor instance — just a function grouped inside the class.
5. `__init__`, `__repr__` and `__eq__` are generated (plus optional ordering/immutability/hash features).
6. `TypeError` — you can't instantiate a class that still has abstract methods.
7. IS-A → inheritance; HAS-A → composition (an attribute holding another object).
8. `True`.
