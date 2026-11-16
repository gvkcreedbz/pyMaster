"""Day 05 - Code along: delivery-fee rules and ticket pricing."""

# ---- 1. A grade with if / elif / else ----
marks = 82
if marks >= 90:
    grade = "A"
elif marks >= 75:
    grade = "B"
elif marks >= 50:
    grade = "C"
else:
    grade = "Fail"
print("Marks", marks, "->", grade)

# ---- 2. Delivery-fee rules (real business logic) ----
order_value = 350
distance_km = 5
is_member = False

if is_member or order_value >= 499:
    fee = 0
elif distance_km <= 3:
    fee = 30
elif distance_km <= 7:
    fee = 50
else:
    fee = 80
print(f"Order Rs. {order_value}, {distance_km} km, member={is_member} -> delivery fee Rs. {fee}")

# ---- 3. Truthy / falsy ----
print("0 is", "truthy" if 0 else "falsy")
print("'' (empty text) is", "truthy" if "" else "falsy")
print("'hi' is", "truthy" if "hi" else "falsy")
print("None is", "truthy" if None else "falsy")

# ---- 4. Chained comparison and one-line if ----
age = 34
print("Working-age adult?", 18 <= age < 60)
status = "adult" if age >= 18 else "minor"
print(status)

# ---- 5. Membership test ----
answer = "Yes"
if answer.lower() in ("y", "yes"):
    print("Order confirmed")

# ---- 6. match / case ----
command = "halt"
match command:
    case "go":
        print("Starting")
    case "stop" | "halt":
        print("Stopping")
    case _:
        print("Unknown command")

# ---- 7. Ticket price: nested decisions ----
age, is_weekend = 8, True
if age < 5:
    price = 0
elif age < 12 or age >= 60:
    price = 100
else:
    price = 200
if is_weekend and price > 0:
    price += 50                       # weekend surcharge
print(f"Age {age}, weekend={is_weekend} -> ticket Rs. {price}")
