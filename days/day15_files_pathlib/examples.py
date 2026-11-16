"""Day 15 - Code along: a to-do file and a server-log analyser."""
from pathlib import Path

HERE = Path(__file__).resolve().parent              # folder of this script
ROOT = HERE.parents[1]                              # project folder (PY)
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# ---- 1. Write, append, read ----
todo = OUT / "todo.txt"
with open(todo, "w", encoding="utf-8") as f:
    f.write("Learn Python\n")
    f.write("Buy milk for Rs. 60\n")
with open(todo, "a", encoding="utf-8") as f:        # a = add to the end
    f.write("Practice 2 hours\n")

with open(todo, encoding="utf-8") as f:
    for number, line in enumerate(f, start=1):
        print(number, line.rstrip("\n"))

# ---- 2. pathlib facts ----
print(todo.name, "|", todo.stem, "|", todo.suffix, "|", todo.exists(), "|", todo.parent.name)
print("Python files here:", sorted(p.name for p in HERE.glob("*.py")))

# ---- 3. Analyse a real log file ----
log_path = ROOT / "datasets" / "app.log"
levels = {}
errors_by_user = {}
for line in log_path.read_text(encoding="utf-8").splitlines():
    date, time, level, *rest = line.split()
    levels[level] = levels.get(level, 0) + 1
    if level == "ERROR":
        fields = dict(item.split("=") for item in rest)
        errors_by_user[fields["user"]] = errors_by_user.get(fields["user"], 0) + 1
print("Log levels:", levels)
print("Errors per user:", errors_by_user)

# ---- 4. Write a small report file ----
report = OUT / "log_report.txt"
report.write_text(f"Total lines: {sum(levels.values())}\nErrors: {levels.get('ERROR', 0)}\n", encoding="utf-8")
print(report.read_text(encoding="utf-8"))
