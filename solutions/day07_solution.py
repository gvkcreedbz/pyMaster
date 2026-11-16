# SOLUTION FILE - try the hint ladder first!
"""Day 07 - Week 1 Project: Mini ATM + Guessing Game.

Run the checks:      python practice.py
Play your ATM:       python practice.py play
"""
import sys


# ---------------------------------------------------------------------------
# L1-1 | deposit   (Level 1 - Beginner)
# Return the new balance after depositing amount. A deposit of 0 or less is
# invalid: return the balance unchanged.   deposit(1000, 500) -> 1500
# ---------------------------------------------------------------------------
def deposit(balance, amount):
    """Return the balance after a deposit."""
    # >>> SOLUTION
    if amount <= 0:
        return balance
    return balance + amount
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | format_balance   (Level 1 - Beginner)
# Return text like  "Balance: Rs. 10,300.00"   (thousands comma, 2 decimals)
# ---------------------------------------------------------------------------
def format_balance(balance):
    """Return a nicely formatted balance line."""
    # >>> SOLUTION
    return f"Balance: Rs. {balance:,.2f}"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | guess_feedback   (Level 1 - Beginner)
# Return "Too high", "Too low" or "Correct!" by comparing guess with secret.
# ---------------------------------------------------------------------------
def guess_feedback(secret, guess):
    """Return feedback for one guess."""
    # >>> SOLUTION
    if guess > secret:
        return "Too high"
    elif guess < secret:
        return "Too low"
    return "Correct!"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | validate_withdrawal   (Level 2 - Intermediate)
# Check IN THIS ORDER and return the first problem found:
#   amount <= 0 or not a multiple of 100 -> "Invalid amount"
#   amount > balance                      -> "Insufficient balance"
#   withdrawn_today + amount > 20000      -> "Daily limit exceeded"
# Otherwise return "OK".
# ---------------------------------------------------------------------------
def validate_withdrawal(balance, amount, withdrawn_today):
    """Return 'OK' or the reason the withdrawal is refused."""
    # >>> SOLUTION
    if amount <= 0 or amount % 100 != 0:
        return "Invalid amount"
    if amount > balance:
        return "Insufficient balance"
    if withdrawn_today + amount > 20000:
        return "Daily limit exceeded"
    return "OK"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | play_guessing_game   (Level 2 - Intermediate)
# guesses_text holds the player's guesses separated by commas ("10,15,12").
# Player gets at most 5 guesses. Return the attempt number on which the secret
# was guessed, or -1 if it was not guessed within 5 attempts.
#   play_guessing_game(12, "10,15,12") -> 3
#   play_guessing_game(12, "1,2,3,4,5,12") -> -1   (the 6th guess is too late)
# ---------------------------------------------------------------------------
def play_guessing_game(secret, guesses_text):
    """Return the winning attempt number or -1."""
    # >>> SOLUTION
    attempt = 0
    for text in guesses_text.split(","):
        attempt += 1
        if attempt > 5:
            break
        if int(text) == secret:
            return attempt
    return -1
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | run_atm   (Level 3 - Challenge)  -> the full interactive program
# 1. PIN: ask with input("Enter PIN: ") up to 3 times. Wrong -> print "Wrong PIN".
#    After 3 wrong tries print "Card blocked" and return the starting balance.
# 2. Menu loop. Each round print:  1) Balance  2) Deposit  3) Withdraw  4) Exit
#    and read input("Choose: ").
#    "1": print(format_balance(balance))
#    "2": amount = int(input("Amount to deposit: ")); use deposit();
#         if it changed the balance print f"Deposited Rs. {amount}" else "Invalid amount"
#    "3": amount = int(input("Amount to withdraw: ")); reason = validate_withdrawal(...)
#         "OK" -> subtract, add to withdrawn_today, print f"Collect your cash: Rs. {amount}"
#         else print the reason
#    "4": print "Thank you!" and return the final balance
#    anything else: print "Invalid option"
# ---------------------------------------------------------------------------
def run_atm(starting_balance, correct_pin):
    """Run the ATM; return the final balance."""
    # >>> SOLUTION
    balance = starting_balance
    withdrawn_today = 0

    pin_ok = False
    attempts = 0
    while attempts < 3:
        if input("Enter PIN: ") == correct_pin:
            pin_ok = True
            break
        attempts += 1
        print("Wrong PIN")
    if not pin_ok:
        print("Card blocked")
        return balance

    while True:
        print("1) Balance  2) Deposit  3) Withdraw  4) Exit")
        choice = input("Choose: ")
        if choice == "1":
            print(format_balance(balance))
        elif choice == "2":
            amount = int(input("Amount to deposit: "))
            new_balance = deposit(balance, amount)
            if new_balance == balance:
                print("Invalid amount")
            else:
                balance = new_balance
                print(f"Deposited Rs. {amount}")
        elif choice == "3":
            amount = int(input("Amount to withdraw: "))
            reason = validate_withdrawal(balance, amount, withdrawn_today)
            if reason == "OK":
                balance -= amount
                withdrawn_today += amount
                print(f"Collect your cash: Rs. {amount}")
            else:
                print(reason)
        elif choice == "4":
            print("Thank you!")
            return balance
        else:
            print("Invalid option")
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
import builtins
import io
from contextlib import redirect_stdout

_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


def run_with_inputs(answers, fn, *args):
    """Feed `answers` to input() one by one; return (result, everything printed)."""
    it = iter(answers)

    def fake_input(prompt=""):
        print(prompt, end="")
        try:
            return next(it)
        except StopIteration:
            raise RuntimeError("your program asked for more input than the test supplies")

    real_input, buf = builtins.input, io.StringIO()
    builtins.input = fake_input
    try:
        with redirect_stdout(buf):
            result = fn(*args)
    finally:
        builtins.input = real_input
    return result, buf.getvalue()


if len(sys.argv) > 1 and sys.argv[1] == "play":
    run_atm(10000, "1234")
    sys.exit()

print("--- Day 07 checks ---")
check("L1-1 deposit", lambda: (deposit(1000, 500), deposit(1000, 0), deposit(1000, -5)), (1500, 1000, 1000))
check("L1-2 format_balance", lambda: format_balance(10300), "Balance: Rs. 10,300.00")
check("L1-2 format_balance #2", lambda: format_balance(99.5), "Balance: Rs. 99.50")
check("L1-3 guess_feedback", lambda: [guess_feedback(10, 15), guess_feedback(10, 5), guess_feedback(10, 10)],
      ["Too high", "Too low", "Correct!"])
check("L2-1 validate_withdrawal", lambda: [
    validate_withdrawal(5000, 0, 0), validate_withdrawal(5000, 250, 0), validate_withdrawal(5000, 6000, 0),
    validate_withdrawal(50000, 6000, 15000), validate_withdrawal(5000, 500, 0)],
    ["Invalid amount", "Invalid amount", "Insufficient balance", "Daily limit exceeded", "OK"])
check("L2-2 guessing game win", lambda: play_guessing_game(12, "10,15,12"), 3)
check("L2-2 guessing game too late", lambda: play_guessing_game(12, "1,2,3,4,5,12"), -1)
check("L2-2 guessing game 5th", lambda: play_guessing_game(7, "1,2,3,4,7"), 5)

res = run_with_inputs(["1234", "2", "500", "3", "200", "1", "4"], run_atm, 10000, "1234")
check("L3-1 ATM happy path balance", lambda: res[0], 10300)
check("L3-1 ATM shows balance line", lambda: "Balance: Rs. 10,300.00" in res[1], True)
check("L3-1 ATM messages", lambda: all(t in res[1] for t in ("Deposited Rs. 500", "Collect your cash: Rs. 200", "Thank you!")), True)
res = run_with_inputs(["1", "2", "3"], run_atm, 10000, "1234")
check("L3-1 ATM blocks card after 3 wrong PINs", lambda: (res[0], "Card blocked" in res[1]), (10000, True))
res = run_with_inputs(["9", "1234", "3", "20000", "3", "300", "3", "250", "7", "4"], run_atm, 10000, "1234")
check("L3-1 ATM refusals", lambda: (res[0], "Insufficient balance" in res[1], "Invalid amount" in res[1], "Invalid option" in res[1]),
      (9700, True, True, True))
res = run_with_inputs(["1234", "3", "15000", "3", "6000", "4"], run_atm, 50000, "1234")
check("L3-1 ATM daily limit", lambda: (res[0], "Daily limit exceeded" in res[1]), (35000, True))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
