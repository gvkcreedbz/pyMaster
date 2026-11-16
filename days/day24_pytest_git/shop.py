"""Mini project for Day 24: a tiny shop module to test with pytest."""


def apply_discount(price, percent):
    """Return price after a percentage discount, rounded to 2 decimals."""
    if price < 0 or not 0 <= percent <= 100:
        raise ValueError("price must be >= 0 and percent between 0 and 100")
    return round(price * (1 - percent / 100), 2)


class Cart:
    """A very small shopping cart."""

    def __init__(self):
        self.items = []          # list of (name, price, qty)

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        self.items.append((name, price, qty))

    def total(self):
        return round(sum(price * qty for _, price, qty in self.items), 2)

    def total_with_coupon(self, code):
        """SAVE10 -> 10% off. Anything else -> no discount."""
        percent = 10 if code == "SAVE10" else 0
        return apply_discount(self.total(), percent)
