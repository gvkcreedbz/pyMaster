# Day 20 — OOP II: Inheritance, Polymorphism, Dunder Methods, Dataclasses, ABCs

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Reuse code with inheritance, make objects behave like built-ins, use `@dataclass`, enforce interfaces | Intermediate → Upper-intermediate |

## 🌍 Real-world scenario & trend
**An HR/payroll system and a game.** Employees, managers and interns are all “employees” but are paid differently; game characters share `attack()` but each attacks differently. Frameworks (Django, PyTorch `nn.Module`, scikit-learn) ask you to *subclass* and override a method. **Trend:** modern Python favours `@dataclass` for data holders, **composition over deep inheritance**, and type-checked interfaces (`abc`, `Protocol`).

## 0. Warm-up (5 min) — Day 19 recap
- What does `self` mean?  • Why create lists inside `__init__`?

## 1. Concepts

### 1.1 Inheritance & `super()`
```python
class Employee:
    def __init__(self, name, salary):
        self.name, self.salary = name, salary
    def pay(self):
        return self.salary

class Manager(Employee):                       # Manager IS-A Employee
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary)         # reuse the parent's setup
        self.bonus = bonus
    def pay(self):                             # override
        return super().pay() + self.bonus
```

### 1.2 Polymorphism — same call, different behaviour
```python
for person in [Employee("A", 50000), Manager("B", 80000, 20000)]:
    print(person.pay())          # each object does its own version of pay()
```
`isinstance(obj, Employee)` is True for managers too.

### 1.3 Dunder (“magic”) methods make objects feel built-in
| Method | Enables |
|---|---|
| `__repr__` / `__str__` | `repr(x)` / `print(x)` |
| `__eq__`, `__lt__` | `==`, `<` (and sorting) |
| `__add__`, `__mul__` | `a + b`, `a * 3` |
| `__len__`, `__getitem__`, `__contains__`, `__iter__` | `len(x)`, `x[0]`, `y in x`, `for i in x` |
```python
class Vector:
    def __init__(self, x, y): self.x, self.y = x, y
    def __add__(self, other): return Vector(self.x + other.x, self.y + other.y)
    def __repr__(self): return f"Vector({self.x}, {self.y})"
print(Vector(1, 2) + Vector(3, 4))     # Vector(4, 6)
```

### 1.4 `@classmethod` and `@staticmethod`
```python
class Person:
    def __init__(self, name, age): self.name, self.age = name, age
    @classmethod
    def from_string(cls, text):               # alternative constructor
        name, age = text.split("-")
        return cls(name, int(age))
    @staticmethod
    def is_adult(age):                        # no self/cls: just a helper
        return age >= 18
```

### 1.5 `@dataclass` — less boilerplate
```python
from dataclasses import dataclass
@dataclass
class Point:
    x: float
    y: float = 0.0          # default
# __init__, __repr__ and __eq__ are written for you
Point(1, 2) == Point(1, 2)  # True
# @dataclass(frozen=True) -> immutable;  @dataclass(order=True) -> sortable
```

### 1.6 Abstract base classes (ABC) — force subclasses to implement a method
```python
from abc import ABC, abstractmethod
class Shape(ABC):
    @abstractmethod
    def area(self): ...
Shape()                  # TypeError: can't instantiate abstract class
```

### 1.7 `functools.total_ordering` — define `__eq__` and `__lt__`, get all comparisons
```python
from functools import total_ordering
@total_ordering
class Version:
    ...
```

### 1.8 Composition vs inheritance
“IS-A” → inherit (`Dog` is an `Animal`). “HAS-A” → compose (`Car` **has** an `Engine` attribute). Prefer composition when unsure — deep inheritance trees become fragile.

## 2. Code along → `examples.py`

## 3. Common mistakes
- Forgetting `super().__init__(...)` in the child.
- Overriding with a different signature (breaks polymorphism).
- Defining `__eq__` without thinking about `__hash__` (objects become unhashable).
- Inheriting just to reuse one function — a helper function or composition is cleaner.

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Animal sounds, `Point` dataclass, `Vector` maths |
| L2-1…L2-3 | 🟡 | Payroll (polymorphism), `Playlist` behaving like a list, `classmethod` + `staticmethod` |
| L3-1, L3-2 | 🔴 | Abstract `Shape` family, semantic `Version` sorting |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Draw a tiny family tree: who is the parent, what does each child change?</details>
<details><summary>Hint 2</summary>Version: <code>from_text</code> splits on <code>"."</code> and stores a tuple of ints; compare tuples in <code>__eq__</code> and <code>__lt__</code>. Playlist: delegate to the inner list — <code>len(self.songs)</code>, <code>self.songs[i]</code>, <code>item in self.songs</code>, <code>iter(self.songs)</code>. Abstract Shape: <code>class Shape(ABC)</code> with an <code>@abstractmethod</code> <code>area</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day20_solution.py</code></details>

## 6. Quiz — answers in `solutions/day20_answers.md`
1. What does `super().__init__(...)` do?
2. What is polymorphism (one sentence)?
3. Which dunder makes `len(obj)` work? Which makes `a + b` work?
4. Difference between `@classmethod` and `@staticmethod`?
5. What do you get for free with `@dataclass`?
6. What happens if you instantiate a class with an unimplemented `@abstractmethod`?
7. “IS-A” vs “HAS-A” — which means inheritance?
8. What does `isinstance(manager, Employee)` return when `Manager(Employee)`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: **Week-3 project — Library Management System** (OOP + JSON persistence) + review test.
