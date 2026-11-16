"""Day 23 - Code along: regex on a messy text file, plus type hints."""
import re
from pathlib import Path

text = (Path(__file__).resolve().parents[2] / "datasets" / "contacts_messy.txt").read_text(encoding="utf-8")

# ---- 1. findall / search ----
emails = re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
print("Emails:", emails)

phones = re.findall(r"(?<!\d)(?:\+91[\s-]?)?([6-9]\d{4})[\s-]?(\d{5})(?!\d)", text)   # tuples of the two groups
print("Mobiles:", ["".join(parts) for parts in phones])

print("Dates:", re.findall(r"\d{4}-\d{2}-\d{2}", text))

# ---- 2. Named groups ----
invoice = re.compile(r"Invoice (?P<id>INV-\d{4}-\d{4}) dated (?P<date>[\d/-]+) total Rs\. (?P<amount>[\d,]+(?:\.\d+)?)")
for m in invoice.finditer(text):
    data = m.groupdict()
    data["amount"] = float(data["amount"].replace(",", ""))
    print(data)

# ---- 3. Validation with fullmatch ----
for pin in ("560001", "060001", "56001", "5600011"):
    print(pin, "->", bool(re.fullmatch(r"[1-9]\d{5}", pin)))

# ---- 4. Substitution: mask a card number before logging ----
sentence = "Paid with card 1234 5678 9012 3456 today"
print(re.sub(r"\b(?:\d{4}[ -]?){3}(\d{4})\b", r"**** **** **** \1", sentence))

# ---- 5. Greedy vs lazy ----
html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.+>", html), re.findall(r"<.+?>", html))


# ---- 6. Type hints (not enforced at run time; tools read them) ----
def average(values: list[float]) -> float:
    """Return the mean of values."""
    return sum(values) / len(values)


def find_user(users: dict[int, str], user_id: int) -> str | None:
    """Return the user's name or None."""
    return users.get(user_id)


print(average([1, 2, 3]), find_user({1: "Aarav"}, 2))
print(average.__annotations__)
