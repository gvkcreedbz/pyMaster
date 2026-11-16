# SOLUTION FILE - try the hint ladder first!
"""Day 21 - Week 3 Project: Library Management System.

Run the checks:  python practice.py
Rules: loan period 14 days, late fee Rs. 5 per late day, max 3 active loans per member.
Dates are text "YYYY-MM-DD".
"""
import json
from dataclasses import asdict, dataclass
from datetime import date


class LibraryError(Exception):
    """Raised when a library rule is broken. (given - don't edit)"""


# ---------------------------------------------------------------------------
# L1-1 | Book   (Level 1 - Beginner)
# @dataclass is given. Add the fields:  isbn (str), title (str), author (str),
# copies (int, default 1).
# ---------------------------------------------------------------------------
@dataclass
class Book:
    """A book title in the library."""
    # >>> SOLUTION
    isbn: str
    title: str
    author: str
    copies: int = 1
    # <<< SOLUTION


class Library:
    """The library. __init__ is given - read it, then write the methods."""

    def __init__(self):
        self.books = {}              # isbn -> Book
        self.loans = []              # active loans: {"isbn", "member", "out"}
        self.checkout_counts = {}    # isbn -> how many times it was borrowed

    # -----------------------------------------------------------------------
    # L1-2 | add_book and find   (Level 1 - Beginner)
    # add_book(book): if the isbn is new store the book; if it already exists ADD
    #   book.copies to the stored book's copies.
    # find(text): sorted list of TITLES that contain text (ignore upper/lower case).
    # -----------------------------------------------------------------------
    # >>> SOLUTION
    def add_book(self, book):
        if book.isbn in self.books:
            self.books[book.isbn].copies += book.copies
        else:
            self.books[book.isbn] = Book(book.isbn, book.title, book.author, book.copies)

    def find(self, text):
        text = text.lower()
        return sorted(b.title for b in self.books.values() if text in b.title.lower())
    # <<< SOLUTION

    # -----------------------------------------------------------------------
    # L1-3 | available_copies   (Level 1 - Beginner)
    # copies of the isbn that are NOT currently on loan (0 for an unknown isbn).
    # -----------------------------------------------------------------------
    # >>> SOLUTION
    def available_copies(self, isbn):
        if isbn not in self.books:
            return 0
        on_loan = sum(1 for loan in self.loans if loan["isbn"] == isbn)
        return self.books[isbn].copies - on_loan
    # <<< SOLUTION

    # -----------------------------------------------------------------------
    # L2-1 | checkout   (Level 2 - Intermediate)
    # checkout(isbn, member, date_text). Check in this order and raise LibraryError:
    #   unknown isbn -> "Unknown book" ; no free copy -> "No copies available" ;
    #   member already holds 3 books -> "Loan limit reached".
    # Otherwise record the loan {"isbn", "member", "out": date_text} and add 1 to
    # checkout_counts[isbn].
    # -----------------------------------------------------------------------
    # >>> SOLUTION
    def checkout(self, isbn, member, date_text):
        if isbn not in self.books:
            raise LibraryError("Unknown book")
        if self.available_copies(isbn) < 1:
            raise LibraryError("No copies available")
        if sum(1 for loan in self.loans if loan["member"] == member) >= 3:
            raise LibraryError("Loan limit reached")
        self.loans.append({"isbn": isbn, "member": member, "out": date_text})
        self.checkout_counts[isbn] = self.checkout_counts.get(isbn, 0) + 1
    # <<< SOLUTION

    # -----------------------------------------------------------------------
    # L2-2 | return_book   (Level 2 - Intermediate)
    # return_book(isbn, member, date_text): find that member's loan for the isbn (none ->
    # LibraryError("No such loan")), remove it, and RETURN the late fee:
    # late days = days between out-date and date_text minus 14 (never below 0), 5 per day.
    # -----------------------------------------------------------------------
    # >>> SOLUTION
    def return_book(self, isbn, member, date_text):
        for loan in self.loans:
            if loan["isbn"] == isbn and loan["member"] == member:
                self.loans.remove(loan)
                days_out = (date.fromisoformat(date_text) - date.fromisoformat(loan["out"])).days
                return max(0, days_out - 14) * 5
        raise LibraryError("No such loan")
    # <<< SOLUTION

    # -----------------------------------------------------------------------
    # L2-3 | save and load   (Level 2 - Intermediate)
    # save(path): write books (as list of dicts), loans and checkout_counts to a JSON file.
    # load(path): a @classmethod that returns a NEW Library rebuilt from that file.
    # -----------------------------------------------------------------------
    # >>> SOLUTION
    def save(self, path):
        data = {
            "books": [asdict(b) for b in self.books.values()],
            "loans": self.loans,
            "checkout_counts": self.checkout_counts,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        lib = cls()
        for b in data["books"]:
            lib.books[b["isbn"]] = Book(**b)
        lib.loans = data["loans"]
        lib.checkout_counts = data["checkout_counts"]
        return lib
    # <<< SOLUTION

    # -----------------------------------------------------------------------
    # L3-1 | overdue_report   (Level 3 - Challenge)
    # Sorted list of lines for every ACTIVE loan that is more than 14 days old at
    # today_text, formatted  "member: title (N days late)"  with N = days out - 14.
    # -----------------------------------------------------------------------
    # >>> SOLUTION
    def overdue_report(self, today_text):
        today = date.fromisoformat(today_text)
        lines = []
        for loan in self.loans:
            late = (today - date.fromisoformat(loan["out"])).days - 14
            if late > 0:
                lines.append(f"{loan['member']}: {self.books[loan['isbn']].title} ({late} days late)")
        return sorted(lines)
    # <<< SOLUTION

    # -----------------------------------------------------------------------
    # L3-2 | popular_books   (Level 3 - Challenge)
    # Titles of the n most borrowed books (use checkout_counts), most borrowed first;
    # equal counts -> title A-Z. Only books borrowed at least once.
    # -----------------------------------------------------------------------
    # >>> SOLUTION
    def popular_books(self, n):
        ranked = sorted(
            ((self.books[isbn].title, count) for isbn, count in self.checkout_counts.items() if count > 0),
            key=lambda item: (-item[1], item[0]),
        )
        return [title for title, count in ranked[:n]]
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
import tempfile
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


def error_of(fn):
    """Return (ExceptionName, message) if fn() raises, else 'no error'."""
    try:
        fn()
    except Exception as e:
        return type(e).__name__, str(e)
    return "no error"


def _lib():
    lib = Library()
    lib.add_book(Book("111", "Python 101", "Guido", 2))
    lib.add_book(Book("222", "Learning Data", "Wes"))
    lib.add_book(Book("333", "Python Tricks", "Dan"))
    lib.add_book(Book("444", "Cooking Basics", "Ana"))
    return lib


print("--- Day 21 checks ---")
check("L1-1 Book dataclass", lambda: (Book("1", "T", "A").copies, Book("1", "T", "A", 3).copies, Book("1", "T", "A") == Book("1", "T", "A")),
      (1, 3, True))


def _add_find():
    lib = _lib()
    lib.add_book(Book("111", "Python 101", "Guido", 3))
    return lib.books["111"].copies, lib.find("PYTHON"), lib.find("data"), lib.find("zzz")


check("L1-2 add_book merges copies / find", _add_find, (5, ["Python 101", "Python Tricks"], ["Learning Data"], []))


def _available():
    lib = _lib()
    before = lib.available_copies("111")
    lib.checkout("111", "aarav", "2026-11-01")
    return before, lib.available_copies("111"), lib.available_copies("999")


check("L1-3 available_copies", _available, (2, 1, 0))


def _checkout_rules():
    lib = _lib()
    out = [error_of(lambda: lib.checkout("999", "aarav", "2026-11-01"))]
    lib.checkout("222", "aarav", "2026-11-01")
    out.append(error_of(lambda: lib.checkout("222", "diya", "2026-11-01")))
    lib.checkout("111", "aarav", "2026-11-01")
    lib.checkout("333", "aarav", "2026-11-01")
    out.append(error_of(lambda: lib.checkout("444", "aarav", "2026-11-01")))
    out.append((len(lib.loans), lib.checkout_counts))
    return out


check("L2-1 checkout rules", _checkout_rules, [("LibraryError", "Unknown book"), ("LibraryError", "No copies available"),
                                               ("LibraryError", "Loan limit reached"), (3, {"222": 1, "111": 1, "333": 1})])


def _returns():
    lib = _lib()
    lib.checkout("111", "aarav", "2026-11-01")
    lib.checkout("222", "diya", "2026-11-01")
    on_time = lib.return_book("111", "aarav", "2026-11-15")
    late = lib.return_book("222", "diya", "2026-11-20")
    return on_time, late, len(lib.loans), error_of(lambda: lib.return_book("222", "diya", "2026-11-21")), lib.available_copies("222")


check("L2-2 return_book fees", _returns, (0, 25, 0, ("LibraryError", "No such loan"), 1))


def _persist():
    lib = _lib()
    lib.checkout("111", "aarav", "2026-11-01")
    lib.checkout("222", "diya", "2026-11-02")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "library.json"
        lib.save(path)
        again = Library.load(path)
        return (type(again).__name__, again.books == lib.books, again.loans == lib.loans,
                again.checkout_counts == lib.checkout_counts, again.available_copies("111"))


check("L2-3 save / load round trip", _persist, ("Library", True, True, True, 1))


def _overdue():
    lib = _lib()
    lib.checkout("111", "aarav", "2026-11-01")
    lib.checkout("222", "diya", "2026-11-10")
    lib.checkout("333", "aarav", "2026-10-20")
    return lib.overdue_report("2026-11-20")


check("L3-1 overdue_report", _overdue, ["aarav: Python 101 (5 days late)", "aarav: Python Tricks (17 days late)"])


def _popular():
    lib = _lib()
    for isbn, member in [("111", "a"), ("111", "b"), ("222", "a"), ("333", "c"), ("333", "d")]:
        lib.checkout(isbn, member, "2026-11-01")
        lib.return_book(isbn, member, "2026-11-02")
    return lib.popular_books(2), lib.popular_books(10)


check("L3-2 popular_books", _popular, (["Python 101", "Python Tricks"], ["Python 101", "Python Tricks", "Learning Data"]))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
