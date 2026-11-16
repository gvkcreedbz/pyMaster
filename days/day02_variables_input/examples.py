"""Day 02 - Code along: a food-delivery bill splitter."""

# ---- 1. Variables and types ----
item_name = "Paneer Pizza"
price = 349
quantity = 2
is_veg = True
rating = 4.5
print(item_name, type(item_name))
print(price, type(price))
print(rating, type(rating))
print(is_veg, type(is_veg))

# ---- 2. Using variables in calculations ----
subtotal = price * quantity
delivery_fee = 40
total = subtotal + delivery_fee
print("Total:", total)

# ---- 3. f-strings: neat output ----
print(f"{quantity} x {item_name} = Rs. {subtotal:.2f}")
print(f"Delivery fee: Rs. {delivery_fee:.2f}")
print(f"TOTAL: Rs. {total:,.2f}")

# ---- 4. The input() trap: it returns TEXT ----
text_number = "25"
print(type(text_number), type(int(text_number)))
print("5" + "3", 5 + 3)          # text joins, numbers add

# ---- 5. Interactive: split the bill ----
print("\n--- Bill splitter ---")
item = input("Item name: ")
unit_price = float(input("Price of one item: "))
qty = int(input("Quantity: "))
friends = int(input("Split between how many people? "))

bill = unit_price * qty + 40
each = bill / friends
print(f"\n{qty} x {item} + Rs. 40 delivery = Rs. {bill:.2f}")
print(f"Each of {friends} people pays Rs. {each:.2f}")
