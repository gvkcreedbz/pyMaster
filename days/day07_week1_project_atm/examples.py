"""Day 07 - Code along: the menu-loop pattern (tip calculator)."""

print("=== Tip calculator ===")
bills_done = 0
while True:                                   # keep going until the user quits
    print("\n1) Calculate tip   2) Show count   q) Quit")
    choice = input("Choose: ")

    if choice == "q":
        break                                 # leave the loop
    elif choice == "1":
        bill = float(input("Bill amount: "))
        if bill <= 0:
            print("Bill must be positive")
            continue                          # back to the menu
        tip = bill * 10 / 100
        print(f"Tip (10%): Rs. {tip:.2f} | Total: Rs. {bill + tip:.2f}")
        bills_done += 1
    elif choice == "2":
        print("Bills calculated so far:", bills_done)
    else:
        print("Invalid option, try again")

print("Bye!")
