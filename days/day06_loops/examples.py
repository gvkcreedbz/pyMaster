"""Day 06 - Code along: loops in action."""
import random

# ---- 1. for + range ----
for i in range(1, 6):
    print("Round", i)
print(list(range(0, 10, 2)), list(range(5, 0, -1)))

# ---- 2. Accumulator: cart total and average ----
prices = (499, 1299, 250, 899)
total = 0
for p in prices:
    total += p
print("Cart total:", total, "| average:", total / len(prices))

# ---- 3. Multiplication table ----
n = 7
for k in range(1, 11):
    print(f"{n} x {k:>2} = {n * k:>3}")

# ---- 4. break / continue ----
for x in range(1, 10):
    if x == 3:
        continue
    if x == 6:
        break
    print(x, end=" ")
print()

# ---- 5. Patterns with nested loops ----
for row in range(1, 5):
    print("*" * row)
for row in range(1, 4):
    for col in range(1, 4):
        print(row * col, end=" ")
    print()

# ---- 6. while: guessing game (computer picks 1-20, you get 5 tries) ----
random.seed(2026)                      # remove this line to get a new number each time
secret = random.randint(1, 20)
attempts = 0
while attempts < 5:
    guess = int(input("Guess 1-20: "))
    attempts += 1
    if guess == secret:
        print(f"Correct! You needed {attempts} attempt(s).")
        break
    print("Too high" if guess > secret else "Too low")
else:                                  # runs only when the loop ended WITHOUT break
    print("Out of attempts. The number was", secret)
