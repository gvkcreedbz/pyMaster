"""Day 21 - Code along: the ideas behind the library system (read, run, then build your own)."""
import json
from dataclasses import asdict, dataclass
from datetime import date


# ---- 1. A dataclass: data holder with free __init__/__repr__/__eq__ ----
@dataclass
class Book:
    isbn: str
    title: str
    author: str
    copies: int = 1


b = Book("111", "Python 101", "Guido", 2)
print(b)
print(asdict(b))                       # dataclass -> dict (handy for JSON)

# ---- 2. Late-fee maths with dates ----
out_date = date.fromisoformat("2026-11-01")
back_date = date.fromisoformat("2026-11-20")
days_out = (back_date - out_date).days          # 19 days
late_days = max(0, days_out - 14)               # 5 days late
print(f"Out {days_out} days -> {late_days} late days -> fee Rs. {late_days * 5}")

# ---- 3. Counting how many active loans a member has ----
loans = [
    {"isbn": "111", "member": "aarav", "out": "2026-11-01"},
    {"isbn": "222", "member": "aarav", "out": "2026-11-05"},
    {"isbn": "111", "member": "diya", "out": "2026-11-07"},
]
print("aarav holds", sum(1 for loan in loans if loan["member"] == "aarav"), "books")
print("copies of 111 on loan:", sum(1 for loan in loans if loan["isbn"] == "111"))

# ---- 4. Saving and loading JSON state ----
state = {"books": [asdict(b)], "loans": loans}
text = json.dumps(state, indent=2)
print(text[:70], "...")
restored = json.loads(text)
print("Round trip OK:", restored == state, "|", Book(**restored["books"][0]) == b)

# ---- 5. Custom exception for business-rule violations ----


class LibraryError(Exception):
    pass


try:
    raise LibraryError("Loan limit reached")
except LibraryError as e:
    print("Refused:", e)
