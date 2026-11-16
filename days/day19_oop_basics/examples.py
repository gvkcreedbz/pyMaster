"""Day 19 - Code along: a bank account and a product catalogue."""


class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def discounted_price(self, percent):
        return round(self.price * (1 - percent / 100), 2)

    def __str__(self):
        return f"{self.name} (Rs. {self.price})"


pen, book = Product("Pen", 10), Product("Book", 120)
print(pen, "|", book, "| 25% off the book:", book.discounted_price(25))


class BankAccount:
    bank_name = "PyBank"                       # class attribute: shared

    def __init__(self, owner, balance=0):
        self.owner = owner                     # instance attributes
        self._balance = balance                # underscore: "internal, use methods"
        self.history = []                      # created per object (NOT at class level!)

    @property
    def balance(self):                         # read-only view of _balance
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount > self._balance:
            return False                       # the rule lives INSIDE the class
        self._balance -= amount
        self.history.append(("withdraw", amount))
        return True

    def __str__(self):
        return f"{self.owner}: Rs. {self._balance:,.2f}"


a, b = BankAccount("Aarav", 1000), BankAccount("Diya")
a.deposit(500)
print(a.withdraw(2000), a.withdraw(300))
b.deposit(75)
print(a, "|", b)
print(a.history, b.history, BankAccount.bank_name)

try:
    a.deposit(-5)
except ValueError as e:
    print("Refused:", e)


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius                 # uses the setter below

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32


t = Temperature(100)
print(t.fahrenheit)
t.celsius = 37
print(round(t.fahrenheit, 1))
