"""Day 15 - Practice: files and pathlib.

Run:  python practice.py
Remember: always open text files with encoding="utf-8".
"""
from pathlib import Path


# ---------------------------------------------------------------------------
# L1-1 | write_lines   (Level 1 - Beginner)
# Write every item of `lines` to the file at `path`, one per line (each line ends
# with "\n"). Overwrite the file if it exists.
# ---------------------------------------------------------------------------
def write_lines(path, lines):
    """Write lines to a text file."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-2 | read_lines   (Level 1 - Beginner)
# Return the file's lines as a list of strings WITHOUT the trailing "\n".
# ---------------------------------------------------------------------------
def read_lines(path):
    """Return the lines of a text file."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L1-3 | count_lines   (Level 1 - Beginner)
# Return how many lines the file has (0 for an empty file).
# ---------------------------------------------------------------------------
def count_lines(path):
    """Return the number of lines."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-1 | add_todo   (Level 2 - Intermediate)
# Append `task` as a new line at the END of the file (create the file if it does
# not exist, never erase old tasks). Return how many tasks the file now holds.
# ---------------------------------------------------------------------------
def add_todo(path, task):
    """Append a task; return the new task count."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-2 | count_log_levels   (Level 2 - Intermediate)
# Each log line looks like:  2026-11-01 08:30:00 ERROR user=bob action=db_timeout
# Return {level: how many lines} (level = 3rd word). Ignore blank lines.
# ---------------------------------------------------------------------------
def count_log_levels(path):
    """Return a dict of counts per log level."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L2-3 | find_files   (Level 2 - Intermediate)
# Return a sorted list of the NAMES (not full paths) of files directly inside
# `folder` whose name ends with `suffix` (e.g. ".txt"). Ignore sub-folders.
# ---------------------------------------------------------------------------
def find_files(folder, suffix):
    """Return sorted names of matching files in folder."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-1 | error_report   (Level 3 - Challenge)
# Read the log at log_path and write a report file at report_path that contains one
# line per ERROR entry:  "<time> <action> <user>"   e.g. "08:30:00 db_timeout bob"
# (in the original order). Return the number of ERROR lines found.
# ---------------------------------------------------------------------------
def error_report(log_path, report_path):
    """Write the ERROR lines report; return how many."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ---------------------------------------------------------------------------
# L3-2 | busiest_hour   (Level 3 - Challenge)
# Return the hour (an int 0-23, taken from the time part) that has the MOST log
# lines. If several hours tie, return the earliest. Return None for an empty log.
# ---------------------------------------------------------------------------
def busiest_hour(log_path):
    """Return the hour with the most log entries."""
    # TODO: write your code here
    pass  # delete this line once you add your code


# ======================= AUTO-CHECKER (do not edit below) ====================
import tempfile

_ok = []


def check(name, fn, want):
    try:
        got = fn()
        good = abs(got - want) < 1e-6 if isinstance(want, float) and isinstance(got, (int, float)) else got == want
    except Exception as e:  # your code crashed -> show why instead of stopping
        got, good = f"{type(e).__name__}: {e}", False
    _ok.append(good)
    print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f"  (got {got!r}, want {want!r})"))


def _datasets():
    for parent in Path(__file__).resolve().parents:
        if (parent / "datasets").is_dir():
            return parent / "datasets"


SAMPLE_LOG = (
    "2026-11-01 08:00:01 INFO user=alice action=login ip=1.1.1.1\n"
    "2026-11-01 08:30:00 ERROR user=bob action=db_timeout ip=1.1.1.2\n"
    "2026-11-01 09:15:10 WARNING user=alice action=slow_response ip=1.1.1.1\n"
    "2026-11-01 09:20:00 ERROR user=alice action=payment_failed ip=1.1.1.1\n"
    "2026-11-01 09:45:00 INFO user=charu action=logout ip=1.1.1.3\n"
)

print("--- Day 15 checks ---")
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    f1 = tmp / "a.txt"
    write_lines(f1, ["one", "two", "₹three"])
    check("L1-1 write_lines (utf-8, newline per line)", lambda: f1.read_bytes().replace(b"\r\n", b"\n"), "one\ntwo\n₹three\n".encode("utf-8"))
    write_lines(f1, ["only"])
    check("L1-1 write_lines overwrites", lambda: f1.read_text(encoding="utf-8"), "only\n")
    f2 = tmp / "b.txt"
    f2.write_text("x\ny\n\nz\n", encoding="utf-8")
    check("L1-2 read_lines", lambda: read_lines(f2), ["x", "y", "", "z"])
    check("L1-3 count_lines", lambda: count_lines(f2), 4)
    empty = tmp / "empty.txt"
    empty.write_text("", encoding="utf-8")
    check("L1-3 count_lines empty", lambda: count_lines(empty), 0)
    todo = tmp / "todo.txt"
    check("L2-1 add_todo creates file", lambda: add_todo(todo, "Buy milk"), 1)
    check("L2-1 add_todo appends", lambda: (add_todo(todo, "Learn Python"), read_lines(todo)), (2, ["Buy milk", "Learn Python"]))
    log = tmp / "app.log"
    log.write_text(SAMPLE_LOG, encoding="utf-8")
    check("L2-2 count_log_levels", lambda: count_log_levels(log), {"INFO": 2, "ERROR": 2, "WARNING": 1})
    (tmp / "sub.txt").mkdir()
    (tmp / "note.md").write_text("m", encoding="utf-8")
    check("L2-3 find_files", lambda: find_files(tmp, ".txt"), ["a.txt", "b.txt", "empty.txt", "todo.txt"])
    rep = tmp / "report.txt"
    check("L3-1 error_report count", lambda: error_report(log, rep), 2)
    check("L3-1 error_report file", lambda: read_lines(rep), ["08:30:00 db_timeout bob", "09:20:00 payment_failed alice"])
    check("L3-2 busiest_hour", lambda: busiest_hour(log), 9)
    check("L3-2 busiest_hour empty", lambda: busiest_hour(empty), None)
    real = _datasets() / "app.log"
    check("Real app.log: level counts", lambda: count_log_levels(real), {"INFO": 180, "WARNING": 21, "ERROR": 39})
    check("Real app.log: errors in report", lambda: error_report(real, tmp / "real_report.txt"), 39)
print(f"\nScore: {sum(_ok)}/{len(_ok)} checks passed")
