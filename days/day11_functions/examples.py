"""Day 11 - Code along: a small billing toolkit built from functions."""


def calc_subtotal(prices):
    """Add up all item prices."""
    return sum(prices)


def apply_coupon(amount, code):
    """Return the amount after applying a coupon code."""
    discounts = {"SAVE10": 10, "SAVE20": 20}
    return amount - amount * discounts.get(code, 0) / 100


def add_tax(amount, tax_percent=18):
    """Add GST (default 18%)."""
    return amount * (1 + tax_percent / 100)


def make_invoice(prices, coupon=None, tax_percent=18):
    """Combine the small functions into one invoice (a dict)."""
    subtotal = calc_subtotal(prices)
    after_coupon = apply_coupon(subtotal, coupon)
    total = add_tax(after_coupon, tax_percent)
    return {"subtotal": subtotal, "after_coupon": after_coupon, "total": round(total, 2)}


print(make_invoice([499, 1299, 250]))
print(make_invoice([499, 1299, 250], coupon="SAVE10"))
print(make_invoice([499, 1299, 250], "SAVE20", tax_percent=5))


# ---- *args and **kwargs ----
def average(*numbers):
    return sum(numbers) / len(numbers) if numbers else 0


def show(**fields):
    for key, value in fields.items():
        print(f"  {key} = {value}")


print(average(4, 8, 6), average())
show(name="Aarav", city="Pune")


# ---- multiple return values ----
def min_max_avg(nums):
    return min(nums), max(nums), sum(nums) / len(nums)


low, high, avg = min_max_avg([4, 8, 6])
print(low, high, avg)


# ---- scope ----
rate = 10


def change_locally():
    rate = 99                     # a different, local variable
    return rate


print(change_locally(), rate)     # 99 10


# ---- recursion ----
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


print("5! =", factorial(5))


# ---- the mutable default trap ----
def bad_add(item, items=[]):
    items.append(item)
    return items


def good_add(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items


print(bad_add(1), bad_add(2))      # [1] [1, 2]  <- surprise!
print(good_add(1), good_add(2))    # [1] [2]
