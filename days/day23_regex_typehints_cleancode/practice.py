"""Day 23 - Practice: regular expressions, type hints, clean code.

Run:  python practice.py
The sample text is datasets/contacts_messy.txt. Use raw strings: r"..."
"""
import re


# ---------------------------------------------------------------------------
# L1-1 | find_emails   (Level 1 - Beginner)
# Return all valid-looking email addresses in the text, in order. Things like
# "john@@example..com" must NOT match.   (letters/digits/._+- before @, domain with a dot)
# ---------------------------------------------------------------------------
def find_emails(text):
    """Return a list of email addresses."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | find_phone_numbers   (Level 1 - Beginner)
# Indian mobile numbers: 10 digits starting with 6, 7, 8 or 9; may be written as
# "+91 98765 43210", "+91-98765-43210", "98765 43210" or "9876543210".
# Return the plain 10-digit strings in order. Toll-free "1800-123-4567" is NOT a mobile.
# ---------------------------------------------------------------------------
def find_phone_numbers(text):
    """Return normalised 10-digit mobile numbers."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | is_valid_pincode   (Level 1 - Beginner)
# An Indian PIN code is exactly 6 digits and does not start with 0.
#   is_valid_pincode("560001") -> True     "060001" -> False     "56001" -> False
# ---------------------------------------------------------------------------
def is_valid_pincode(text):
    """Return True for a valid PIN code."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | extract_invoices   (Level 2 - Intermediate)
# Lines look like:  Invoice INV-2026-0042 dated 2026-11-03 total Rs. 12,450.50
# Return a list of dicts {"id": text, "date": text (as written), "amount": float}
# (remove the comma in the amount before converting). Use named groups.
# ---------------------------------------------------------------------------
def extract_invoices(text):
    """Return invoice dicts found in text."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | mask_card_numbers   (Level 2 - Intermediate)
# Replace every 16-digit card number (digits may be grouped by 4 with spaces or
# dashes) with "**** **** **** " + its last four digits. Other numbers are untouched.
#   mask_card_numbers("Card 1234 5678 9012 3456 used") -> "Card **** **** **** 3456 used"
# ---------------------------------------------------------------------------
def mask_card_numbers(text):
    """Hide all but the last 4 digits of card numbers."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | normalize_order_ids   (Level 2 - Intermediate)
# Orders are written ORD1001, ord1003 or ORD-1004. Return a SORTED list of the unique
# ids in the standard form "ORD" + digits.
#   -> ["ORD1001", "ORD1002", "ORD1003", "ORD1004"] for the sample file
# ---------------------------------------------------------------------------
def normalize_order_ids(text):
    """Return unique, normalised order ids."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | parse_log_line   (Level 3 - Challenge)
# Line format: 2026-11-01 08:30:00 ERROR user=bob action=db_timeout ip=192.168.1.20
# Return {"date","time","level","user","action","ip"} (all text) or None when the line
# does not follow the format.
# ---------------------------------------------------------------------------
def parse_log_line(line):
    """Return the parsed fields or None."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | group_average with type hints   (Level 3 - Challenge)
# Write the function with COMPLETE type annotations (all parameters AND the return):
#   def group_average(rows: list[dict], key: str, value: str) -> dict[str, float]
# For rows like {"city": "A", "temp": 10} return {group: average of `value`} rounded
# to 2 decimals.   group_average(rows, "city", "temp") -> {"A": 15.0, "B": 5.0}
# ---------------------------------------------------------------------------
# TODO: write your code here


# ======================= AUTO-CHECKER (do not edit below) ====================
from pathlib import Path

_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


def _sample_text():
    for parent in Path(__file__).resolve().parents:
        if (parent / "datasets").is_dir():
            return (parent / "datasets" / "contacts_messy.txt").read_text(encoding="utf-8")


print("--- Day 23 checks ---")
check("L1-1 find_emails (sample file)", lambda: find_emails(_sample_text()), [
    "priya.sharma@example.com", "rahul_v99@mail.co.in", "help@shop-india.com", "meera.iyer@university.edu.in", "cto@startup.io"])
check("L1-1 find_emails (tricky)", lambda: find_emails("a@b.com, bad@@x..com and no-at.com; c.d+e@f-g.org."), ["a@b.com", "c.d+e@f-g.org"])
check("L1-2 find_phone_numbers (sample file)", lambda: find_phone_numbers(_sample_text()), ["9876543210", "9123456780", "9000011111"])
check("L1-2 find_phone_numbers (tricky)", lambda: find_phone_numbers("Call 1800-123-4567 or 5876543210 or 8765432109"), ["8765432109"])
check("L1-3 is_valid_pincode", lambda: [is_valid_pincode(p) for p in ("560001", "060001", "56001", "5600011", "56000a")],
      [True, False, False, False, False])
check("L2-1 extract_invoices", lambda: extract_invoices(_sample_text()), [
    {"id": "INV-2026-0042", "date": "2026-11-03", "amount": 12450.5},
    {"id": "INV-2026-0043", "date": "03/11/2026", "amount": 899.0}])
check("L2-2 mask_card_numbers", lambda: (mask_card_numbers("Card 1234 5678 9012 3456 used"), mask_card_numbers("pay 1234-5678-9012-3456!"),
                                        mask_card_numbers("1234567890123456"), mask_card_numbers("PIN 1234 phone 9876543210")),
      ("Card **** **** **** 3456 used", "pay **** **** **** 3456!", "**** **** **** 3456", "PIN 1234 phone 9876543210"))
check("L2-3 normalize_order_ids", lambda: normalize_order_ids(_sample_text()), ["ORD1001", "ORD1002", "ORD1003", "ORD1004"])
_line = "2026-11-01 08:30:00 ERROR user=bob action=db_timeout ip=192.168.1.20"
check("L3-1 parse_log_line", lambda: parse_log_line(_line), {"date": "2026-11-01", "time": "08:30:00", "level": "ERROR",
                                                           "user": "bob", "action": "db_timeout", "ip": "192.168.1.20"})
check("L3-1 parse_log_line (bad)", lambda: parse_log_line("garbage line"), None)
_rows = [{"city": "A", "temp": 10}, {"city": "A", "temp": 20}, {"city": "B", "temp": 5}]
check("L3-2 group_average values", lambda: group_average(_rows, "city", "temp"), {"A": 15.0, "B": 5.0})
check("L3-2 group_average has full type hints", lambda: sorted(group_average.__annotations__), ["key", "return", "rows", "value"])
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
