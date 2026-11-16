"""Day 01 - Code along: a cafe receipt printer.

Type each section yourself, run it (python examples.py), then change values and re-run.
"""

# ---- 1. Our first instructions (they run top to bottom) ----
print("Welcome to Chai Point")
print("One masala chai, please")

# ---- 2. Text vs numbers ----
print(2 + 3)      # Python calculates -> 5
print("2 + 3")    # just text -> 2 + 3
print("Total:", 2 * 60 + 3 * 15)   # 2 chai at 60 + 3 samosa at 15 -> Total: 165

# ---- 3. Making the output pretty ----
print("=" * 24)
print("      CHAI POINT")
print("=" * 24)
print("Item\tQty\tPrice")         # \t = tab
print("Chai\t2\t120")
print("Samosa\t3\t45")
print("-" * 24)
print("TOTAL\t\t165")

# ---- 4. sep and end ----
print("2026", "11", "16", sep="-")   # 2026-11-16
print("Loading", end="...")
print("done")

# ---- 5. Variables: labels for values (full lesson tomorrow) ----
shop = "Chai Point"
visitors_today = 128
print(shop, "had", visitors_today, "visitors today")

# ---- 6. Everything together: a tiny receipt ----
print()                 # empty print = blank line
print("Thank you for visiting", shop + "!")
print("See you tomorrow :)")
