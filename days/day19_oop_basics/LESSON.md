# Day 19 — Object-Oriented Programming I: Classes & Objects

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Model real things (account, cart, library) as classes with data + behaviour | Intermediate |

## 🌍 Real-world scenario & trend
**A banking app.** A `BankAccount` *has data* (owner, balance, history) and *can do things* (deposit, withdraw) — and the rules (“no overdraft”) live inside it. Games (characters), shops (products, carts), libraries (books, members), and almost every framework (Django models, pandas DataFrame, scikit-learn estimators) are classes. **Trend:** modern Python mixes OOP with plain functions and `dataclasses`; you must be able to *read* classes fluently to use any big library.

## 0. Warm-up (5 min) — Day 18 recap
- What does `defaultdict(list)` do?  • `date.fromisoformat("2026-11-16").weekday()`?

## 1. Concepts

### 1.1 Class = blueprint, object = a thing built from it
```python
class Product:
    def __init__(self, name, price):     # runs when you create an object
        self.name = name                  # attributes (the object's data)
        self.price = price

    def discounted_price(self, percent):  # method (the object's behaviour)
        return self.price * (1 - percent / 100)

pen = Product("Pen", 10)                  # create an object (an "instance")
book = Product("Book", 120)
print(pen.name, book.discounted_price(25))   # 90.0
```
`self` = “the object I am working on”. Python passes it automatically — never pass it yourself.

### 1.2 Objects keep their own state
```python
class Counter:
    def __init__(self):
        self.count = 0
    def hit(self):
        self.count += 1
a, b = Counter(), Counter()
a.hit(); a.hit(); b.hit()
print(a.count, b.count)     # 2 1
```

### 1.3 `__str__` and `__repr__` — how an object prints
```python
class Rectangle:
    def __init__(self, w, h): self.w, self.h = w, h
    def __str__(self): return f"Rectangle({self.w}x{self.h})"   # for print()
print(Rectangle(3, 4))      # Rectangle(3x4)   (without __str__: <__main__.Rectangle object at 0x...>)
```

### 1.4 Class attributes vs instance attributes
```python
class Account:
    bank_name = "PyBank"            # shared by ALL accounts
    def __init__(self, owner):
        self.owner = owner          # different for each object
```

### 1.5 Encapsulation by convention
`self._balance` (leading underscore) means “internal — please use the methods”. Python does not force privacy; it trusts developers.

### 1.6 `@property` — attribute-looking methods with validation
```python
class Temperature:
    def __init__(self, celsius): self.celsius = celsius        # goes through the setter
    @property
    def celsius(self): return self._celsius
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value
    @property
    def fahrenheit(self): return self._celsius * 9 / 5 + 32     # read-only, computed
```

### 1.7 Methods can call each other and raise errors
Business rules belong **inside** the class (`withdraw` checks the balance), so no outside code can break them.

### 1.8 Design tip — nouns → classes, verbs → methods
“A *library* lets a *member* check out a *book*” → `Library`, `Member`, `Book`; `checkout()`.

## 2. Code along → `examples.py`

## 3. Common mistakes
- Forgetting `self.` before attribute names (`name = name` does nothing).
- Forgetting `self` as the first parameter of a method.
- Mutable class attributes shared by mistake (`items = []` at class level) — create lists in `__init__`.
- Misspelling `__init__` (double underscores both sides).

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | `Product`, `Student`, `Rectangle` |
| L2-1…L2-3 | 🟡 | `BankAccount`, `ShoppingCart`, `Temperature` with `@property` |
| L3-1, L3-2 | 🔴 | A small `Library` class, a `Stack` + balanced-brackets checker |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>For each class write down: what data does it hold (→ <code>__init__</code>) and what can it do (→ methods)?</details>
<details><summary>Hint 2</summary>Cart: keep a dict <code>{name: [price, qty]}</code> in <code>self._items</code>. Library: a dict of copies per title and a list of <code>(title, member)</code> loans. Stack: a list; <code>push</code> = append, <code>pop</code> = list pop. Balanced brackets: push opening brackets; on a closing bracket pop and compare with its partner (<code>{")": "(", "]": "[", "}": "{"}</code>); the stack must be empty at the end.</details>
<details><summary>Hint 3</summary><code>solutions/day19_solution.py</code></details>

## 6. Quiz — answers in `solutions/day19_answers.md`
1. What is the difference between a class and an object?
2. What does `self` refer to?
3. When does `__init__` run?
4. What prints for `print(obj)` if the class has no `__str__`?
5. Class attribute vs instance attribute?
6. Why use `@property` with a setter?
7. What does a leading underscore (`_balance`) signal?
8. Why is `class Cart: items = []` risky?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: OOP II — inheritance, polymorphism, dunder methods, dataclasses, abstract classes.
