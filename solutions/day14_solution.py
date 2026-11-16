# SOLUTION FILE - try the hint ladder first!
"""Day 14 - Week 2 Project: Expense Tracker.

Run the checks:      python practice.py
Play your tracker:   python practice.py play
"""
import sys


# ---------------------------------------------------------------------------
# L1-1 | add_expense   (Level 1 - Beginner)
# Append {"date", "category", "amount", "note"} to the expenses list.
# If amount <= 0 do NOT add anything and return False. Otherwise return True.
# ---------------------------------------------------------------------------
def add_expense(expenses, date, category, amount, note=""):
    """Add an expense; return True when added."""
    # >>> SOLUTION
    if amount <= 0:
        return False
    expenses.append({"date": date, "category": category, "amount": amount, "note": note})
    return True
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | total_spent   (Level 1 - Beginner)
# Sum of all amounts (0 for an empty list).
# ---------------------------------------------------------------------------
def total_spent(expenses):
    """Return the total of all expenses."""
    # >>> SOLUTION
    return sum(e["amount"] for e in expenses)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | format_expense   (Level 1 - Beginner)
# Return one aligned line: date | category (left, width 10) | Rs. amount (right,
# width 9, thousands comma, 2 decimals) | note
#   -> "2026-11-16 | Food       | Rs.    250.00 | Lunch"
# ---------------------------------------------------------------------------
def format_expense(e):
    """Return a printable line for one expense."""
    # >>> SOLUTION
    return f"{e['date']} | {e['category']:<10} | Rs. {e['amount']:>9,.2f} | {e['note']}"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | totals_by_category   (Level 2 - Intermediate)
# Return {category: total amount}.
# ---------------------------------------------------------------------------
def totals_by_category(expenses):
    """Return spending per category."""
    # >>> SOLUTION
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    return totals
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | filter_expenses   (Level 2 - Intermediate)
# Return the expenses (original order) that match: category equals `category`
# (or any category when it is None) AND amount >= min_amount.
# ---------------------------------------------------------------------------
def filter_expenses(expenses, category=None, min_amount=0):
    """Return matching expenses."""
    # >>> SOLUTION
    return [e for e in expenses
            if (category is None or e["category"] == category) and e["amount"] >= min_amount]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | monthly_totals   (Level 2 - Intermediate)
# Return {"YYYY-MM": total}. The date text looks like "2026-11-16".
# ---------------------------------------------------------------------------
def monthly_totals(expenses):
    """Return spending per month."""
    # >>> SOLUTION
    totals = {}
    for e in expenses:
        month = e["date"][:7]
        totals[month] = totals.get(month, 0) + e["amount"]
    return totals
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | budget_report   (Level 3 - Challenge)
# budgets = {"Food": 2000, "Travel": 1000}. Return a list of lines, one per budget
# category, sorted A-Z by category, each formatted like:
#   "Food: spent 1800.00 of 2000.00 (90.0%) WARN"
# Percent = spent / budget * 100 (1 decimal). Status: "OVER" if spent > budget,
# else "WARN" if percent >= 80, else "OK". Categories without expenses = 0 spent.
# Expenses in categories that have no budget are ignored.
# ---------------------------------------------------------------------------
def budget_report(expenses, budgets):
    """Return one status line per budget category."""
    # >>> SOLUTION
    spent_by = totals_by_category(expenses)
    lines = []
    for category in sorted(budgets):
        limit = budgets[category]
        spent = spent_by.get(category, 0)
        percent = spent / limit * 100
        status = "OVER" if spent > limit else "WARN" if percent >= 80 else "OK"
        lines.append(f"{category}: spent {spent:.2f} of {limit:.2f} ({percent:.1f}%) {status}")
    return lines
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | run_tracker   (Level 3 - Challenge)  -> the interactive program
# Keep an `expenses` list. Loop: print "1) Add  2) List  3) Summary  4) Quit" then
# read input("Choose: ").
#  "1": date = input("Date (YYYY-MM-DD): "), category = input("Category: "),
#       amount = float(input("Amount: ")), note = input("Note: ")
#       -> add_expense(...) ; print "Added" if True else "Invalid amount"
#  "2": no expenses -> print "No expenses yet"; else print format_expense(e) for each
#  "3": no expenses -> print "No expenses yet"; else for every category (A-Z) print
#       f"{category}: Rs. {total:,.2f}" and finally f"Total: Rs. {all:,.2f}"
#  "4": print "Goodbye!" and return the expenses list
#  other: print "Invalid option"
# ---------------------------------------------------------------------------
def run_tracker():
    """Run the menu; return the list of expenses."""
    # >>> SOLUTION
    expenses = []
    while True:
        print("1) Add  2) List  3) Summary  4) Quit")
        choice = input("Choose: ")
        if choice == "1":
            date = input("Date (YYYY-MM-DD): ")
            category = input("Category: ")
            amount = float(input("Amount: "))
            note = input("Note: ")
            print("Added" if add_expense(expenses, date, category, amount, note) else "Invalid amount")
        elif choice == "2":
            if not expenses:
                print("No expenses yet")
            for e in expenses:
                print(format_expense(e))
        elif choice == "3":
            if not expenses:
                print("No expenses yet")
            else:
                totals = totals_by_category(expenses)
                for category in sorted(totals):
                    print(f"{category}: Rs. {totals[category]:,.2f}")
                print(f"Total: Rs. {total_spent(expenses):,.2f}")
        elif choice == "4":
            print("Goodbye!")
            return expenses
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
    run_tracker()
    sys.exit()

SAMPLE = [
    {"date": "2026-11-02", "category": "Food", "amount": 1500.0, "note": "Groceries"},
    {"date": "2026-11-09", "category": "Food", "amount": 300.0, "note": "Dinner"},
    {"date": "2026-11-10", "category": "Travel", "amount": 1200.0, "note": "Cab"},
    {"date": "2026-12-01", "category": "Fun", "amount": 99.5, "note": "Game"},
]

print("--- Day 14 checks ---")


def _add_check():
    lst = []
    first = add_expense(lst, "2026-11-16", "Food", 250, "Lunch")
    bad = add_expense(lst, "2026-11-16", "Food", 0)
    return first, bad, len(lst), lst[0]


check("L1-1 add_expense", _add_check, (True, False, 1, {"date": "2026-11-16", "category": "Food", "amount": 250, "note": "Lunch"}))
check("L1-2 total_spent", lambda: (total_spent(SAMPLE), total_spent([])), (3099.5, 0))
check("L1-3 format_expense", lambda: format_expense({"date": "2026-11-16", "category": "Food", "amount": 250, "note": "Lunch"}),
      "2026-11-16 | Food       | Rs.    250.00 | Lunch")
check("L2-1 totals_by_category", lambda: totals_by_category(SAMPLE), {"Food": 1800.0, "Travel": 1200.0, "Fun": 99.5})
check("L2-2 filter by category", lambda: [e["note"] for e in filter_expenses(SAMPLE, category="Food")], ["Groceries", "Dinner"])
check("L2-2 filter by amount", lambda: [e["note"] for e in filter_expenses(SAMPLE, min_amount=1000)], ["Groceries", "Cab"])
check("L2-2 filter both", lambda: [e["note"] for e in filter_expenses(SAMPLE, "Food", 1000)], ["Groceries"])
check("L2-3 monthly_totals", lambda: monthly_totals(SAMPLE), {"2026-11": 3000.0, "2026-12": 99.5})
check("L3-1 budget_report", lambda: budget_report(SAMPLE, {"Travel": 1000, "Food": 2000, "Movies": 500, "Fun": 100}), [
    "Food: spent 1800.00 of 2000.00 (90.0%) WARN",
    "Fun: spent 99.50 of 100.00 (99.5%) WARN",
    "Movies: spent 0.00 of 500.00 (0.0%) OK",
    "Travel: spent 1200.00 of 1000.00 (120.0%) OVER"])

res = run_with_inputs(["1", "2026-11-16", "Food", "250", "Lunch", "1", "2026-11-17", "Travel", "-5", "x",
                       "1", "2026-11-17", "Travel", "120.5", "Metro", "2", "3", "4"], run_tracker)
check("L3-2 tracker stores 2 expenses", lambda: (len(res[0]), total_spent(res[0])), (2, 370.5))
check("L3-2 tracker messages", lambda: all(t in res[1] for t in ("Added", "Invalid amount", "Goodbye!")), True)
check("L3-2 tracker list + summary", lambda: all(t in res[1] for t in (
    "2026-11-16 | Food       | Rs.    250.00 | Lunch", "Food: Rs. 250.00", "Travel: Rs. 120.50", "Total: Rs. 370.50")), True)
res = run_with_inputs(["2", "3", "9", "4"], run_tracker)
check("L3-2 tracker empty state", lambda: (res[0], res[1].count("No expenses yet"), "Invalid option" in res[1]), ([], 2, True))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
