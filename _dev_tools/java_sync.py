"""Maintainer tool for the Java course: keep the auto-checker in the solutions and (re)build every Practice.java.

Source of truth: java/solutions/dayNN_Solution.java (like solutions/dayNN_solution.py for Python).

  * the line `// @@CHECKER@@` (or an already expanded checker block) is replaced by _dev_tools/java_checker.txt
  * every block between `// >>> SOLUTION [stub: <code>]` and `// <<< SOLUTION` is blanked in Practice.java:
        // TODO: write your code here
        <code>            <- the optional stub, so the unfinished file still compiles
usage:  python _dev_tools/java_sync.py [day numbers...]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "java"
CHECKER = (Path(__file__).resolve().parent / "java_checker.txt").read_text(encoding="utf-8").rstrip() + "\n"
BLOCK = re.compile(r"// ==== CHECKER-BEGIN.*?// ==== CHECKER-END ====\n?", re.S)
START = re.compile(r"^(\s*)//\s*>>>\s*SOLUTION(?:\s+stub:\s*(.*))?\s*$")
END = re.compile(r"^\s*//\s*<<<\s*SOLUTION\s*$")


def expand_checker(text: str) -> str:
    if BLOCK.search(text):
        return BLOCK.sub(lambda _m: CHECKER, text, count=1)
    return text.replace("// @@CHECKER@@\n", CHECKER).replace("// @@CHECKER@@", CHECKER.rstrip("\n"))


def make_practice(solution_text: str) -> str:
    out, skipping = [], False
    for line in solution_text.splitlines():
        if "SOLUTION FILE" in line:
            continue
        m = START.match(line)
        if m:
            indent, stub = m.group(1), m.group(2)
            out.append(f"{indent}// TODO: write your code here")
            if stub:
                out.append(f"{indent}{stub.strip()}")
            skipping = True
            continue
        if END.match(line):
            skipping = False
            continue
        if not skipping:
            out.append(line)
    return "\n".join(out) + "\n"


def main() -> None:
    only = {int(a) for a in sys.argv[1:]}
    for sol in sorted((JAVA / "solutions").glob("day*_Solution.java")):
        n = int(re.match(r"day(\d+)_", sol.name).group(1))
        if only and n not in only:
            continue
        text = expand_checker(sol.read_text(encoding="utf-8"))
        sol.write_text(text, encoding="utf-8", newline="\n")
        folder = next(iter((JAVA / "days").glob(f"day{n:02d}_*")), None)
        if folder is None:
            print(f"day{n:02d}: no folder java/days/day{n:02d}_* yet (solution checker expanded only)")
            continue
        (folder / "Practice.java").write_text(make_practice(text), encoding="utf-8", newline="\n")
        print(f"day{n:02d}: Practice.java written")


if __name__ == "__main__":
    main()
