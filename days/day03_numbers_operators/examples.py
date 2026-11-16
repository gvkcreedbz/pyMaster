"""Day 03 - Code along: shopping checkout, EMI and BMI."""
import math

# ---- 1. Operators cheat-run ----
print(7 / 2, 7 // 2, 7 % 2, 2 ** 3)
print(2 + 3 * 4 ** 2, (2 + 3) * 4)

# ---- 2. Checkout: discount + GST ----
price = 2499
discount_percent = 20
gst_percent = 18

discount_amount = price * discount_percent / 100
after_discount = price - discount_amount
gst_amount = after_discount * gst_percent / 100
final_price = after_discount + gst_amount
print(f"MRP: {price}  |  Discount: {discount_amount:.2f}  |  GST: {gst_amount:.2f}  |  Pay: {final_price:.2f}")

# ---- 3. Even/odd and time conversion with % and // ----
print("Is 18 even?", 18 % 2 == 0)
hours, minutes = divmod(125, 60)
print(f"125 minutes = {hours}h {minutes}m")

# ---- 4. Bank EMI formula ----
principal = 500_000          # underscores make big numbers readable
annual_rate = 9              # percent
years = 5
r = annual_rate / 12 / 100   # monthly rate
n = years * 12               # number of months
emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
print(f"Monthly EMI: Rs. {emi:,.2f}")
print(f"Total paid:  Rs. {emi * n:,.2f}  (interest = Rs. {emi * n - principal:,.2f})")

# ---- 5. BMI ----
weight_kg, height_cm = 70, 175
bmi = weight_kg / (height_cm / 100) ** 2
print(f"BMI = {bmi:.1f}")

# ---- 6. The float gotcha + math module ----
print(0.1 + 0.2, 0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
print(round(2.5), round(3.5), round(2.567, 2))
print(math.sqrt(16), math.ceil(4.2), math.floor(4.8), round(math.pi, 4))

# ---- 7. += shortcut: a growing cart ----
cart = 0
cart += 499
cart += 1299
cart *= 2
print("Cart (doubled) =", cart)
