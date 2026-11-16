"""Maintainer tool: build days/dayNN_*/practice.py from solutions/dayNN_solution.py.

It blanks every block between `# >>> SOLUTION` and `# <<< SOLUTION` markers.
Usage:  python _dev_tools/make_practice.py [day numbers...]
(Learners do NOT need this file.)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
only = {int(a) for a in sys.argv[1:]}

for sol in sorted((ROOT / "solutions").glob("day*_solution.py")):
    n = int(re.match(r"day(\d+)_", sol.name).group(1))
    if only and n not in only:
        continue
    folder = next((ROOT / "days").glob(f"day{n:02d}_*"))
    out, skipping = [], False
    for line in sol.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if "SOLUTION FILE" in s:
            continue
        if s == "# >>> SOLUTION":
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f"{indent}# TODO: write your code here")
            if indent:
                out.append(f"{indent}pass  # delete this line once you add your code")
            skipping = True
            continue
        if s == "# <<< SOLUTION":
            skipping = False
            continue
        if not skipping:
            out.append(line)
    (folder / "practice.py").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"day{n:02d}: practice.py written ({len(out)} lines)")
