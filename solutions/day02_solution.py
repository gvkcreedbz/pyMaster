# SOLUTION FILE - try the hint ladder first!
"""Day 02 - Practice: Variables, types, input and f-strings.

Run:  python practice.py
"""

# ---------------------------------------------------------------------------
# L1-1 | Order variables   (Level 1 - Beginner)
# Create three variables:
#   item_name = "Paneer Pizza" (text), price = 349 (whole number), qty = 2 (whole number)
# ---------------------------------------------------------------------------
item_name = None
price = None
qty = None
# >>> SOLUTION
item_name = "Paneer Pizza"
price = 349
qty = 2
# <<< SOLUTION

# ---------------------------------------------------------------------------
# L1-2 | Order total   (Level 1 - Beginner)
# Using the variables above (not typed numbers!) store price times qty in order_total.
# ---------------------------------------------------------------------------
order_total = None
# >>> SOLUTION
order_total = price * qty
# <<< SOLUTION

# ---------------------------------------------------------------------------
# L1-3 | Text to number   (Level 1 - Beginner)
# price_text is text. Convert it into a whole number and store it in price_number.
# ---------------------------------------------------------------------------
price_text = "349"
price_number = None
# >>> SOLUTION
price_number = int(price_text)
# <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | Order summary   (Level 2 - Intermediate)
# Return text in exactly this format (price always with 2 decimals):
#   order_summary("Paneer Pizza", 349, 2)  ->  "2 x Paneer Pizza = Rs. 698.00"
# ---------------------------------------------------------------------------
def order_summary(item, unit_price, quantity):
    # >>> SOLUTION
    return f"{quantity} x {item} = Rs. {unit_price * quantity:.2f}"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | Split the bill   (Level 2 - Intermediate)
# Return  "Each person pays Rs. X"  with X rounded to 2 decimals.
#   split_bill(1000, 3) -> "Each person pays Rs. 333.33"
# ---------------------------------------------------------------------------
def split_bill(total, people):
    # >>> SOLUTION
    return f"Each person pays Rs. {total / people:.2f}"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | Full invoice   (Level 3 - Challenge)
# Return a 4-line text (lines joined with \n, NO trailing newline):
#   Subtotal: Rs. 698.00
#   Delivery: Rs. 40.00
#   Tip (10%): Rs. 69.80        <- tip is a percentage of the SUBTOTAL
#   TOTAL: Rs. 807.80
# Example call: delivery_invoice("Paneer Pizza", 349, 2, 40, 10)
# ---------------------------------------------------------------------------
def delivery_invoice(item, unit_price, quantity, delivery_fee, tip_percent):
    # >>> SOLUTION
    subtotal = unit_price * quantity
    tip = subtotal * tip_percent / 100
    total = subtotal + delivery_fee + tip
    return (
        f"Subtotal: Rs. {subtotal:.2f}\n"
        f"Delivery: Rs. {delivery_fee:.2f}\n"
        f"Tip ({tip_percent}%): Rs. {tip:.2f}\n"
        f"TOTAL: Rs. {total:.2f}"
    )
    # <<< SOLUTION


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


print("--- Day 02 checks ---")
check("L1-1 item_name", lambda: item_name, "Paneer Pizza")
check("L1-1 price", lambda: price, 349)
check("L1-1 qty", lambda: qty, 2)
check("L1-2 order_total", lambda: order_total, 698)
check("L1-3 price_number", lambda: (price_number, type(price_number).__name__), (349, "int"))
check("L2-1 order_summary", lambda: order_summary("Paneer Pizza", 349, 2), "2 x Paneer Pizza = Rs. 698.00")
check("L2-1 order_summary #2", lambda: order_summary("Chai", 20.5, 4), "4 x Chai = Rs. 82.00")
check("L2-2 split_bill", lambda: split_bill(1000, 3), "Each person pays Rs. 333.33")
check("L3-1 delivery_invoice", lambda: delivery_invoice("Paneer Pizza", 349, 2, 40, 10),
      "Subtotal: Rs. 698.00\nDelivery: Rs. 40.00\nTip (10%): Rs. 69.80\nTOTAL: Rs. 807.80")
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
