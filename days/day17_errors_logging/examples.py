"""Day 17 - Code along: surviving errors and writing logs."""
import logging
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# ---- 1. try / except / else / finally ----
for text in ("250", "abc", ""):
    try:
        amount = int(text)
    except ValueError:
        print(f"{text!r}: please type digits only")
    else:
        print(f"{text!r}: OK, amount = {amount}")
    finally:
        print("   (checked)")

# ---- 2. Several error types ----
for func, label in [(lambda: 1 / 0, "divide"), (lambda: {"a": 1}["b"], "key"), (lambda: open("nope.txt"), "file")]:
    try:
        func()
    except ZeroDivisionError:
        print(label, "-> ZeroDivisionError")
    except KeyError as e:
        print(label, "-> missing key", e)
    except FileNotFoundError:
        print(label, "-> file not found")


# ---- 3. Raising and a custom error ----
class InsufficientFundsError(Exception):
    """Raised when a withdrawal is bigger than the balance."""


def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > balance:
        raise InsufficientFundsError(f"Need Rs. {amount - balance} more")
    return balance - amount


for amount in (500, 5000, -1):
    try:
        print("New balance:", withdraw(2000, amount))
    except InsufficientFundsError as e:
        print("Refused:", e)
    except ValueError as e:
        print("Invalid:", e)

# ---- 4. debugging helper ----
total, count = 120, 4
print(f"{total=} {count=} {total / count=}")

# ---- 5. logging to a file ----
logging.basicConfig(filename=OUT / "demo.log", filemode="w", level=logging.INFO, encoding="utf-8",
                    format="%(asctime)s %(levelname)s %(message)s")
logging.debug("this line is hidden at INFO level")
logging.info("order 77 placed")
logging.warning("stock is low")
try:
    withdraw(100, 500)
except InsufficientFundsError:
    logging.exception("withdrawal failed")        # logs the traceback too
print("Log file written to", OUT / "demo.log")
print((OUT / "demo.log").read_text(encoding="utf-8").splitlines()[0][:60], "...")
