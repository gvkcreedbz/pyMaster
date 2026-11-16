# SOLUTION FILE - try the hint ladder first!
"""Day 04 - Practice: strings.

Run:  python practice.py
"""


# ---------------------------------------------------------------------------
# L1-1 | First name   (Level 1 - Beginner)
# Return the first word.   first_name("Aarav Sharma") -> "Aarav"
# ---------------------------------------------------------------------------
def first_name(full_name):
    """Return the first word of full_name."""
    # >>> SOLUTION
    return full_name.split()[0]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | Initials   (Level 1 - Beginner)
# For a name made of exactly two words, return the initials in capitals,
# each followed by a dot.   initials("aarav sharma") -> "A.S."
# ---------------------------------------------------------------------------
def initials(full_name):
    """Return initials like A.S."""
    # >>> SOLUTION
    first, last = full_name.split()
    return first[0].upper() + "." + last[0].upper() + "."
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | Shout   (Level 1 - Beginner)
# Return the text in UPPERCASE followed by "!".   shout("hello") -> "HELLO!"
# ---------------------------------------------------------------------------
def shout(text):
    """Return text.upper() + '!'."""
    # >>> SOLUTION
    return text.upper() + "!"
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | Username generator   (Level 2 - Intermediate)
# lowercase full name, spaces replaced by dots, plus the last 2 digits of the year.
#   make_username("Aarav Sharma", 2001) -> "aarav.sharma01"
# ---------------------------------------------------------------------------
def make_username(full_name, birth_year):
    """Return a username like aarav.sharma01."""
    # >>> SOLUTION
    return full_name.strip().lower().replace(" ", ".") + str(birth_year)[-2:]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | Simple email validator   (Level 2 - Intermediate)
# Valid when ALL are true: exactly one "@", no spaces, text before the "@",
# and a "." somewhere AFTER the "@" (but not as the very last character).
#   is_valid_email("a@b.com") -> True      is_valid_email("a@@b.com") -> False
#   is_valid_email("a b@c.com") -> False   is_valid_email("a@b.") -> False
# ---------------------------------------------------------------------------
def is_valid_email(email):
    """Return True for a plausible email address."""
    # >>> SOLUTION
    if email.count("@") != 1 or " " in email or email.startswith("@"):
        return False
    domain = email.split("@")[1]
    return "." in domain and not domain.endswith(".")
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | Message cleaner   (Level 2 - Intermediate)
# Remove outer spaces, collapse repeated spaces into one, capitalise the first letter.
#   clean_message("   hello    world  ") -> "Hello world"
# ---------------------------------------------------------------------------
def clean_message(text):
    """Return a tidy one-line message."""
    # >>> SOLUTION
    return " ".join(text.split()).capitalize()
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | CamelCase hashtag   (Level 3 - Challenge)
# Turn a caption into ONE hashtag: remove the characters . , ! ? and the spaces,
# capitalise every word (Title Case), and put # in front.
#   make_hashtag("learning python is fun!") -> "#LearningPythonIsFun"
#   make_hashtag("  new   year, new me ")   -> "#NewYearNewMe"
# ---------------------------------------------------------------------------
def make_hashtag(caption):
    """Return a single CamelCase hashtag."""
    # >>> SOLUTION
    text = caption.replace(".", "").replace(",", "").replace("!", "").replace("?", "")
    return "#" + "".join(text.title().split())
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | Palindrome   (Level 3 - Challenge)
# True if the text reads the same backwards, ignoring upper/lower case and spaces.
#   is_palindrome("Never odd or even") -> True      is_palindrome("Python") -> False
# ---------------------------------------------------------------------------
def is_palindrome(text):
    """Return True if text is a palindrome (ignoring case and spaces)."""
    # >>> SOLUTION
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]
    # <<< SOLUTION


# ======================= AUTO-CHECKER (do not edit below) ====================
_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


print("--- Day 04 checks ---")
check("L1-1 first_name", lambda: first_name("Aarav Sharma"), "Aarav")
check("L1-2 initials", lambda: initials("aarav sharma"), "A.S.")
check("L1-3 shout", lambda: shout("hello"), "HELLO!")
check("L2-1 make_username", lambda: make_username("Aarav Sharma", 2001), "aarav.sharma01")
check("L2-1 make_username #2", lambda: make_username("Diya Rao", 1999), "diya.rao99")
check("L2-2 valid email", lambda: is_valid_email("a@b.com"), True)
check("L2-2 two @", lambda: is_valid_email("a@@b.com"), False)
check("L2-2 space", lambda: is_valid_email("a b@c.com"), False)
check("L2-2 ends with dot", lambda: is_valid_email("a@b."), False)
check("L2-2 no dot after @", lambda: is_valid_email("a.b@c"), False)
check("L2-3 clean_message", lambda: clean_message("   hello    world  "), "Hello world")
check("L3-1 make_hashtag", lambda: make_hashtag("learning python is fun!"), "#LearningPythonIsFun")
check("L3-1 make_hashtag #2", lambda: make_hashtag("  new   year, new me "), "#NewYearNewMe")
check("L3-2 palindrome yes", lambda: is_palindrome("Never odd or even"), True)
check("L3-2 palindrome no", lambda: is_palindrome("Python"), False)
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
