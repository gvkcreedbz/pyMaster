"""A tiny helper module (imported by examples.py).

A module = a .py file whose functions you can reuse from other files.
"""


def add_gst(price, gst_percent=18):
    """Return the price including GST."""
    return round(price * (1 + gst_percent / 100), 2)


def format_money(amount):
    """Return text like 'Rs. 1,234.50'."""
    return f"Rs. {amount:,.2f}"


def main():
    print("Running shop_utils directly:", format_money(add_gst(999)))


if __name__ == "__main__":      # runs ONLY when you do `python shop_utils.py`
    main()
