"""Day 20 - Practice: inheritance, dunder methods, dataclasses, ABCs.

Run:  python practice.py
"""
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import total_ordering


# ---------------------------------------------------------------------------
# L1-1 | Animals   (Level 1 - Beginner)
# Animal is given. Write Dog and Cat (subclasses of Animal) that OVERRIDE speak():
# Dog -> "Woof", Cat -> "Meow". Then write Parrot(Animal): __init__(self, name, phrase)
# must call super().__init__(name) and speak() returns the phrase.
#   Dog("Rex").intro() -> "Rex says Woof"
# ---------------------------------------------------------------------------
class Animal:
    """Base class (given)."""

    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def intro(self):
        return f"{self.name} says {self.speak()}"


# TODO: write your code here


# ---------------------------------------------------------------------------
# L1-2 | Point dataclass   (Level 1 - Beginner)
# The @dataclass decorator is given. Add the fields x (float) and y (float, default 0.0)
# and a method distance_to(other) returning the straight-line distance to another
# Point rounded to 2 decimals (math.dist or Pythagoras).
#   Point(0, 0).distance_to(Point(3, 4)) -> 5.0
# ---------------------------------------------------------------------------
@dataclass
class Point:
    """A point on a plane."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | Vector   (Level 1 - Beginner)
# Vector(x, y) with:  __add__ (adds two vectors), __mul__ (multiply by a number),
# __eq__ (same x and y) and __repr__ returning "Vector(1, 2)".
# ---------------------------------------------------------------------------
class Vector:
    """A 2-D vector."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | Payroll   (Level 2 - Intermediate)
# Employee is given (pay() returns salary). Write:
#   Manager(name, salary, bonus): pay() = salary + bonus
#   Intern(name): always paid 10000 (call super().__init__(name, 10000))
#   total_payroll(employees): the sum of pay() of every employee (polymorphism!)
# ---------------------------------------------------------------------------
class Employee:
    """Base class (given)."""

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def pay(self):
        return self.salary


# TODO: write your code here


# ---------------------------------------------------------------------------
# L2-2 | Playlist   (Level 2 - Intermediate)
# Playlist(songs) keeps a list. Make it behave like a collection:
#   len(p), p[0] / p[-1], "song" in p, `for s in p`, and add(song) appends a song.
# ---------------------------------------------------------------------------
class Playlist:
    """A playlist of songs."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | Person with classmethod and staticmethod   (Level 2 - Intermediate)
# Person(name, age).
#   Person.from_string("Aarav-25") -> Person("Aarav", 25)     (@classmethod, age is an int)
#   Person.is_adult(age) -> age >= 18                          (@staticmethod)
#   can_vote(self) -> uses is_adult with self.age
# ---------------------------------------------------------------------------
class Person:
    """A person."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | Abstract shapes   (Level 3 - Challenge)
# Shape(ABC) with an abstract method area(). Circle(radius).area() -> pi*r*r rounded to
# 2 decimals; Square(side).area() -> side*side. Creating a plain Shape() must raise
# TypeError. largest(shapes) returns the shape object with the biggest area.
# ---------------------------------------------------------------------------
# TODO: write your code here


# ---------------------------------------------------------------------------
# L3-2 | Version numbers   (Level 3 - Challenge)
# Write a class Version (decorate it with @total_ordering - already imported at the
# top) so that versions compare by their integer parts, NOT as text: 1.10.0 is
# bigger than 1.9.5.
#   Version.from_text("1.10.2")  (classmethod; stores the parts as ints)
#   __eq__, __lt__ and __repr__ -> "Version(1.10.2)"
# sorted([...]) and > must work.
# ---------------------------------------------------------------------------
# TODO: write your code here


# ======================= AUTO-CHECKER (do not edit below) ====================
_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


print("--- Day 20 checks ---")
check("L1-1 Dog / Cat", lambda: (Dog("Rex").intro(), Cat("Tom").intro(), isinstance(Dog("a"), Animal)), ("Rex says Woof", "Tom says Meow", True))
check("L1-1 Parrot", lambda: (Parrot("Polly", "Hello!").intro(), Parrot("P", "x").name), ("Polly says Hello!", "P"))
check("L1-2 Point", lambda: (Point(0, 0).distance_to(Point(3, 4)), Point(1, 1).distance_to(Point(2, 2)), Point(5) == Point(5, 0.0), Point(1, 2) == Point(1, 2)),
      (5.0, 1.41, True, True))
check("L1-3 Vector", lambda: (Vector(1, 2) + Vector(3, 4) == Vector(4, 6), Vector(1, 2) * 3 == Vector(3, 6), Vector(1, 2) == Vector(1, 2), Vector(1, 2) == Vector(2, 1)),
      (True, True, True, False))
check("L1-3 Vector repr", lambda: repr(Vector(1, 2)), "Vector(1, 2)")
def _team():
    return [Employee("A", 50000), Manager("B", 80000, 20000), Intern("C")]


def _playlist():
    p = Playlist(["a", "b"])
    p.add("c")
    return p


check("L2-1 pay()", lambda: [e.pay() for e in _team()], [50000, 100000, 10000])
check("L2-1 total_payroll / isinstance", lambda: (total_payroll(_team()), isinstance(_team()[1], Employee), _team()[2].name), (160000, True, "C"))
check("L2-2 Playlist", lambda: (len(_playlist()), _playlist()[0], _playlist()[-1], "b" in _playlist(), "z" in _playlist(), list(_playlist())),
      (3, "a", "c", True, False, ["a", "b", "c"]))
check("L2-3 Person", lambda: (Person.from_string("Aarav-25").name, Person.from_string("Aarav-25").age, type(Person.from_string("A-1")).__name__,
                              Person.is_adult(17), Person.from_string("Aarav-25").can_vote(), Person("K", 10).can_vote()),
      ("Aarav", 25, "Person", False, True, False))
check("L3-1 shapes", lambda: (Circle(1).area(), Square(3).area(), type(largest([Square(1), Circle(2), Square(3)])).__name__),
      (3.14, 9, "Circle"))


def _abstract_error():
    try:
        Shape()
    except TypeError:
        return "TypeError"
    return "no error"


check("L3-1 Shape is abstract", _abstract_error, "TypeError")
def _versions():
    return [Version.from_text(s) for s in ("1.10.0", "1.9.5", "1.9.10")]


check("L3-2 Version sorting", lambda: [repr(v) for v in sorted(_versions())], ["Version(1.9.5)", "Version(1.9.10)", "Version(1.10.0)"])
check("L3-2 Version compare", lambda: (Version.from_text("2.0.0") > Version.from_text("1.99.99"), Version.from_text("1.2") == Version.from_text("1.2"),
                                       max(_versions()) == Version.from_text("1.10.0")), (True, True, True))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
