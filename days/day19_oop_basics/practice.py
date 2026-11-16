"""Day 19 - Practice: classes and objects.

Run:  python practice.py
Write each class completely: __init__, methods, and the special methods mentioned.
"""


# ---------------------------------------------------------------------------
# L1-1 | Product   (Level 1 - Beginner)
# Product(name, price) stores both as attributes.
# discounted_price(percent) returns the price after the discount, rounded to 2 decimals.
#   Product("Book", 120).discounted_price(25) -> 90.0
# ---------------------------------------------------------------------------
class Product:
    """A product with a name and a price."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | Student   (Level 1 - Beginner)
# Student(name) starts with no marks.
#   add_mark(mark)  -> remember one more mark
#   average()       -> mean of the marks rounded to 2 decimals (0 when no marks)
#   highest()       -> the biggest mark (None when no marks)
# ---------------------------------------------------------------------------
class Student:
    """A student who collects marks."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | Rectangle   (Level 1 - Beginner)
# Rectangle(width, height) with methods area(), perimeter(), is_square()
# and __str__ returning text like "Rectangle(3x4)".
# ---------------------------------------------------------------------------
class Rectangle:
    """A rectangle."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | BankAccount   (Level 2 - Intermediate)
# BankAccount(owner, balance=0). Attributes: owner, balance, history (a list).
#   deposit(amount): amount <= 0 -> raise ValueError("Deposit must be positive");
#                    otherwise add it and append ("deposit", amount) to history.
#   withdraw(amount): if amount > balance return False (nothing changes); otherwise
#                    subtract, append ("withdraw", amount) and return True.
#   __str__ -> "Aarav: Rs. 1,500.00"
# ---------------------------------------------------------------------------
class BankAccount:
    """A simple bank account."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | ShoppingCart   (Level 2 - Intermediate)
#   add(name, price, qty=1): adding an existing name increases its quantity
#   remove(name): remove the item; return True if it existed, else False
#   total(): sum of price * qty, rounded to 2 decimals
#   item_count(): total number of units (sum of quantities)
#   names(): sorted list of item names
# ---------------------------------------------------------------------------
class ShoppingCart:
    """A shopping cart."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | Temperature with @property   (Level 2 - Intermediate)
# Temperature(celsius). `celsius` is a property whose setter raises
# ValueError("Below absolute zero") for values under -273.15 (also when creating
# the object). `fahrenheit` is a READ-ONLY property: celsius * 9 / 5 + 32.
# ---------------------------------------------------------------------------
class Temperature:
    """A temperature with validation."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | Library   (Level 3 - Challenge)
# Library() starts empty.
#   add_book(title, copies=1): add copies (adding an existing title adds more copies)
#   checkout(title, member): needs a free copy, otherwise raise ValueError("Not available")
#   return_book(title, member): if that member does not have the title raise
#                    ValueError("Not borrowed by this member"), otherwise free the copy
#   available(): sorted list of titles with at least one free copy
#   borrowed_by(member): sorted list of titles the member currently holds
# ---------------------------------------------------------------------------
class Library:
    """A tiny lending library."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | Stack and balanced brackets   (Level 3 - Challenge)
# class Stack: push(item), pop() (raise IndexError("pop from empty stack") when empty),
#   peek() (look at the top without removing; IndexError when empty), is_empty(), size().
# Then is_balanced(text): True when every ( [ { is closed in the right order.
# Other characters are ignored.   is_balanced("{[()]}") -> True   is_balanced("(]") -> False
# ---------------------------------------------------------------------------
class Stack:
    """Last in, first out."""
    # TODO: write your code here
    pass  # delete this line once you add your code


def is_balanced(text):
    """Return True when brackets are balanced."""
    # TODO: write your code here
    pass  # delete this line once you add your code


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


def error_of(fn):
    """Return (ExceptionName, message) if fn() raises, else 'no error'."""
    try:
        fn()
    except Exception as e:
        return type(e).__name__, str(e)
    return "no error"


print("--- Day 19 checks ---")
check("L1-1 Product", lambda: (Product("Book", 120).name, Product("Book", 120).discounted_price(25), Product("Pen", 9.99).discounted_price(10)),
      ("Book", 90.0, 8.99))
def _student():
    s = Student("Aarav")
    for mark in (80, 95, 70):
        s.add_mark(mark)
    return s


check("L1-2 Student empty", lambda: (Student("A").average(), Student("A").highest()), (0, None))
check("L1-2 Student marks", lambda: (_student().average(), _student().highest(), _student().name), (81.67, 95, "Aarav"))
check("L1-3 Rectangle", lambda: (Rectangle(3, 4).area(), Rectangle(3, 4).perimeter(), Rectangle(2, 2).is_square(), Rectangle(2, 3).is_square()),
      (12, 14, True, False))
check("L1-3 Rectangle __str__", lambda: str(Rectangle(3, 4)), "Rectangle(3x4)")


def _account():
    acc = BankAccount("Aarav", 1000)
    acc.deposit(500)
    ok1, ok2 = acc.withdraw(2000), acc.withdraw(300)
    return acc.balance, ok1, ok2, acc.history, str(acc), BankAccount("X").balance


check("L2-1 BankAccount", _account, (1200, False, True, [("deposit", 500), ("withdraw", 300)], "Aarav: Rs. 1,200.00", 0))
check("L2-1 deposit error", lambda: error_of(lambda: BankAccount("A").deposit(-5)), ("ValueError", "Deposit must be positive"))
check("L2-1 histories are separate", lambda: (BankAccount("A").history is not BankAccount("B").history), True)


def _cart():
    c = ShoppingCart()
    c.add("Pen", 10, 3)
    c.add("Book", 120.5)
    c.add("Pen", 10)
    return c.total(), c.item_count(), c.names(), c.remove("Pen"), c.remove("Pen"), c.total()


check("L2-2 ShoppingCart", _cart, (160.5, 5, ["Book", "Pen"], True, False, 120.5))
check("L2-3 Temperature", lambda: (Temperature(100).fahrenheit, Temperature(0).fahrenheit, Temperature(-40).fahrenheit), (212.0, 32.0, -40.0))
check("L2-3 Temperature setter validates", lambda: (error_of(lambda: Temperature(-300)), error_of(lambda: setattr(Temperature(1), "celsius", -274))),
      (("ValueError", "Below absolute zero"), ("ValueError", "Below absolute zero")))
check("L2-3 fahrenheit is read-only", lambda: error_of(lambda: setattr(Temperature(1), "fahrenheit", 5))[0], "AttributeError")


def _library():
    lib = Library()
    lib.add_book("Dune", 2)
    lib.add_book("Emma")
    lib.checkout("Dune", "aarav")
    lib.checkout("Dune", "diya")
    lib.checkout("Emma", "aarav")
    out = [lib.available(), lib.borrowed_by("aarav"), error_of(lambda: lib.checkout("Dune", "kabir")),
           error_of(lambda: lib.return_book("Emma", "diya"))]
    lib.return_book("Dune", "diya")
    out.append(lib.available())
    return out


check("L3-1 Library", _library, [[], ["Dune", "Emma"], ("ValueError", "Not available"),
                                 ("ValueError", "Not borrowed by this member"), ["Dune"]])


def _stack():
    s = Stack()
    first = s.is_empty()
    s.push(1)
    s.push(2)
    return first, s.size(), s.peek(), s.pop(), s.pop(), s.is_empty(), error_of(s.pop)


check("L3-2 Stack", _stack, (True, 2, 2, 2, 1, True, ("IndexError", "pop from empty stack")))
check("L3-2 is_balanced", lambda: [is_balanced(t) for t in ("{[()]}", "(]", "((", "", "a(b)c", ")(")], [True, False, False, True, True, False])
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
