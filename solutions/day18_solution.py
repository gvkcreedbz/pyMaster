# SOLUTION FILE - try the hint ladder first!
"""Day 18 - Practice: the standard library.

Run:  python practice.py
All dates are text in the form "YYYY-MM-DD". 2026-11-16 is a Monday.
"""
import statistics
from collections import Counter, defaultdict
from datetime import date, timedelta
from itertools import combinations


# ---------------------------------------------------------------------------
# L1-1 | days_until   (Level 1 - Beginner)
# Number of days from today_text to event_text (negative if the event is past).
#   days_until("2026-11-16", "2026-12-25") -> 39
# ---------------------------------------------------------------------------
def days_until(today_text, event_text):
    """Return the number of days until the event."""
    # >>> SOLUTION
    return (date.fromisoformat(event_text) - date.fromisoformat(today_text)).days
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-2 | format_date   (Level 1 - Beginner)
# "2026-12-05" -> "05 Dec 2026"   (strftime codes %d %b %Y)
# ---------------------------------------------------------------------------
def format_date(iso_text):
    """Return a human friendly date."""
    # >>> SOLUTION
    return date.fromisoformat(iso_text).strftime("%d %b %Y")
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L1-3 | median_and_mean   (Level 1 - Beginner)
# Return (median, mean) where the mean is rounded to 2 decimals.
#   median_and_mean([3, 1, 2, 10]) -> (2.5, 4.0)
# ---------------------------------------------------------------------------
def median_and_mean(numbers):
    """Return (median, mean)."""
    # >>> SOLUTION
    return statistics.median(numbers), round(statistics.mean(numbers), 2)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-1 | most_common_words   (Level 2 - Intermediate)
# Lowercase the text, split on spaces, count words with Counter and return the n most
# common as (word, count) tuples. Ties -> alphabetical order.
#   most_common_words("the cat and the hat and the bat", 2) -> [("the", 3), ("and", 2)]
# ---------------------------------------------------------------------------
def most_common_words(text, n):
    """Return the n most common words with counts."""
    # >>> SOLUTION
    counts = Counter(text.lower().split())
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-2 | group_by_length   (Level 2 - Intermediate)
# Return a normal dict {length: [words with that length]} (original order inside).
# Use defaultdict(list).   group_by_length(["hi", "yo", "sun"]) -> {2: ["hi", "yo"], 3: ["sun"]}
# ---------------------------------------------------------------------------
def group_by_length(words):
    """Group words by their length."""
    # >>> SOLUTION
    groups = defaultdict(list)
    for w in words:
        groups[len(w)].append(w)
    return dict(groups)
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L2-3 | age_in_years   (Level 2 - Intermediate)
# Completed years between birth date and today (birthday not reached yet -> one less).
#   age_in_years("2000-11-17", "2026-11-16") -> 25     age_in_years("2000-11-16", "2026-11-16") -> 26
# ---------------------------------------------------------------------------
def age_in_years(birth_text, today_text):
    """Return the age in completed years."""
    # >>> SOLUTION
    born, today = date.fromisoformat(birth_text), date.fromisoformat(today_text)
    years = today.year - born.year
    if (today.month, today.day) < (born.month, born.day):
        years -= 1
    return years
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-1 | possible_teams   (Level 3 - Challenge)
# All different teams of `size` players. Return a list of tuples; the players inside
# each tuple and the tuples themselves are in alphabetical order (use itertools).
#   possible_teams(["C", "A", "B"], 2) -> [("A", "B"), ("A", "C"), ("B", "C")]
# ---------------------------------------------------------------------------
def possible_teams(players, size):
    """Return every possible team."""
    # >>> SOLUTION
    return sorted(combinations(sorted(players), size))
    # <<< SOLUTION


# ---------------------------------------------------------------------------
# L3-2 | next_weekday   (Level 3 - Challenge)
# Return the ISO date of the NEXT given weekday strictly AFTER date_text.
# weekday_name is e.g. "friday" (any capitalisation).
#   next_weekday("2026-11-16", "friday") -> "2026-11-20"
#   next_weekday("2026-11-16", "monday") -> "2026-11-23"  (not the same day)
# ---------------------------------------------------------------------------
def next_weekday(date_text, weekday_name):
    """Return the date of the next weekday_name after date_text."""
    # >>> SOLUTION
    names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    target = names.index(weekday_name.lower())
    d = date.fromisoformat(date_text)
    ahead = (target - d.weekday()) % 7 or 7
    return (d + timedelta(days=ahead)).isoformat()
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


print("--- Day 18 checks ---")
check("L1-1 days_until", lambda: (days_until("2026-11-16", "2026-12-25"), days_until("2026-11-16", "2026-11-10")), (39, -6))
check("L1-2 format_date", lambda: (format_date("2026-12-05"), format_date("2026-01-31")), ("05 Dec 2026", "31 Jan 2026"))
check("L1-3 median_and_mean", lambda: (median_and_mean([3, 1, 2, 10]), median_and_mean([5, 1, 3])), ((2.5, 4.0), (3, 3.0)))
check("L2-1 most_common_words", lambda: most_common_words("the cat and the hat and the bat", 2), [("the", 3), ("and", 2)])
check("L2-1 ties alphabetical", lambda: most_common_words("b a c a b", 3), [("a", 2), ("b", 2), ("c", 1)])
check("L2-2 group_by_length", lambda: group_by_length(["hi", "yo", "sun", "a"]), {2: ["hi", "yo"], 3: ["sun"], 1: ["a"]})
check("L2-3 age_in_years", lambda: (age_in_years("2000-11-17", "2026-11-16"), age_in_years("2000-11-16", "2026-11-16"),
                                    age_in_years("2000-01-01", "2026-11-16")), (25, 26, 26))
check("L3-1 possible_teams", lambda: (possible_teams(["C", "A", "B"], 2), len(possible_teams(list("ABCDE"), 3))),
      ([("A", "B"), ("A", "C"), ("B", "C")], 10))
check("L3-2 next_weekday", lambda: (next_weekday("2026-11-16", "friday"), next_weekday("2026-11-16", "Monday"),
                                    next_weekday("2026-11-20", "monday"), next_weekday("2026-12-31", "thursday")),
      ("2026-11-20", "2026-11-23", "2026-11-23", "2027-01-07"))
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
