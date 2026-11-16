"""Day 20 - Code along: payroll, shapes, a dataclass and a smart Vector."""
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---- 1. Inheritance + polymorphism ----
class Employee:
    def __init__(self, name, salary):
        self.name, self.salary = name, salary

    def pay(self):
        return self.salary


class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary)
        self.bonus = bonus

    def pay(self):
        return super().pay() + self.bonus


class Intern(Employee):
    def __init__(self, name):
        super().__init__(name, 10000)


team = [Employee("Aarav", 50000), Manager("Diya", 80000, 20000), Intern("Kabir")]
for person in team:
    print(f"{person.name:<6} {type(person).__name__:<9} Rs. {person.pay():>7,}")
print("Payroll:", sum(p.pay() for p in team), "| manager is an Employee?", isinstance(team[1], Employee))


# ---- 2. Abstract base class ----
class Shape(ABC):
    @abstractmethod
    def area(self): ...


class Circle(Shape):
    def __init__(self, r):
        self.r = r

    def area(self):
        return round(math.pi * self.r ** 2, 2)


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2


for s in (Circle(1), Square(3)):
    print(type(s).__name__, s.area())
try:
    Shape()
except TypeError as e:
    print("Cannot build a Shape:", e)


# ---- 3. dataclass ----
@dataclass
class Point:
    x: float
    y: float = 0.0


print(Point(1, 2), Point(1, 2) == Point(1, 2), Point(5))


# ---- 4. dunder methods ----
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


print(Vector(1, 2) + Vector(3, 4), Vector(1, 2) == Vector(1, 2))


# ---- 5. classmethod / staticmethod ----
class Person:
    def __init__(self, name, age):
        self.name, self.age = name, age

    @classmethod
    def from_string(cls, text):
        name, age = text.split("-")
        return cls(name, int(age))

    @staticmethod
    def is_adult(age):
        return age >= 18


p = Person.from_string("Aarav-25")
print(p.name, p.age, Person.is_adult(p.age))
