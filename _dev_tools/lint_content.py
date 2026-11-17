"""Fast static lint of the course content (no code is executed).

    python _dev_tools/lint_content.py [--track python|java|both] [--root DIR] [--quiet]

Checks both courses (python: days/ solutions/ datasets/; java: java/days java/solutions java/datasets):
  * every day 1-30 has exactly one folder, with LESSON.md, examples, practice, solution and answers files
  * LESSON.md: title line, scenario paragraph, 4-8 "### N.M" concept headings, exactly 3 hint <details>,
    8 quiz questions (numbered 1-8) whose numbers match the answers file
  * practice/solution files: exercise headers (portal track.EX_HEADER semantics) are unique, sequential per level,
    the level digit matches "(Level N", practice and solution agree; ">>> SOLUTION" / "<<< SOLUTION" markers balance
  * no UTF-8 BOM, no TAB inside code fences, no mojibake (UTF-8 mangled through cp1252), valid UTF-8
  * relative links in the top-level docs resolve; datasets/ files named in lessons exist
  * DRILLS.json parses and has the keys "day" and "drills"
Exit code 1 when anything is found; every line is ``file:line: message [code]`` (paths relative to --root).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TRACKS = ("python", "java")
DAYS = range(1, 31)
TEXT_SUFFIXES = {".md", ".py", ".java", ".json", ".csv", ".txt", ".log"}

# --- mojibake: UTF-8 bytes that were decoded as cp1252 (e.g. an em dash shows up as a-circumflex + euro + right quote)
_CONT = ("\u0080-\u00bf\u0152\u0153\u0160\u0161\u0178\u017d\u017e\u0192\u02c6\u02dc\u2013\u2014\u2018\u2019\u201a"
         "\u201c\u201d\u201e\u2020\u2021\u2022\u2026\u2030\u2039\u203a\u20ac\u2122")
MOJIBAKE = re.compile(f"[\u00c2-\u00df][{_CONT}]|[\u00e0-\u00ef][{_CONT}]{{2}}|[\u00f0-\u00f4][{_CONT}]{{3}}")

# Intentional troubleshooting quotes ("what garbled text looks like"). (path relative to --root, text that must be on the line).
MOJIBAKE_ALLOW = [
    ("SETUP.md", "Weird characters like"),
    ("java/SETUP.md", "Garbled characters like"),
    ("java/cheatsheets/error_decoder.md", "Characters look wrong"),
]

# Known, reviewed deviations: (path relative to --root, issue code) -> reason. They are NOT counted as failures but are
# always printed as a note, so nothing is hidden. Remove an entry once the content is fixed.
KNOWN_EXCEPTIONS = {
    ("days/day11_functions/LESSON.md", "concepts"):
        "Day 11 teaches 9 function concepts (### 1.1-1.9); the limit is 8. Merge two concepts to remove this entry.",
}

LESSON_TITLE = re.compile(r"^# Day (\d{2}) \u2014 \S.*$")
CONCEPT = re.compile(r"^###\s+\d+\.\d+\s+\S")
QUESTION = re.compile(r"^\s{0,3}(\d+)\.\s+\S")
LEVEL_NAMES = {1: "Beginner", 2: "Intermediate", 3: "Challenge"}
DATASET_REF = re.compile(r"datasets[/\\]+([A-Za-z0-9_][A-Za-z0-9_.\-]*\.[A-Za-z0-9]+)")
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
INLINE_CODE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Issue:
    path: str
    line: int
    code: str
    msg: str

    def __str__(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        return f"{loc}: {self.msg} [{self.code}]"


_track_cache: dict[str, object] = {}


def load_track(track_id: str):
    """Load portal/track.py fresh for one track (it reads PORTAL_TRACK at import time) to reuse its configuration."""
    if track_id not in _track_cache:
        old = os.environ.get("PORTAL_TRACK")
        os.environ["PORTAL_TRACK"] = track_id
        try:
            spec = importlib.util.spec_from_file_location(f"_lint_track_{track_id}", REPO / "portal" / "track.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        finally:
            if old is None:
                os.environ.pop("PORTAL_TRACK", None)
            else:
                os.environ["PORTAL_TRACK"] = old
        _track_cache[track_id] = mod
    return _track_cache[track_id]


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _ascii(s: str, n: int = 70) -> str:
    return s.strip()[:n].encode("ascii", "backslashreplace").decode("ascii")


class Linter:
    def __init__(self, root: Path, track_id: str):
        self.root = Path(root).resolve()
        self.id = track_id
        self.t = load_track(track_id)
        self.cfg = self.t.CONFIGS[track_id]
        self.base = self.root / "java" if track_id == "java" else self.root
        self.days_dir = self.base / "days"
        self.sol_dir = self.base / "solutions"
        self.data_dir = self.base / "datasets"
        self.issues: list[Issue] = []
        self.suppressed: list[tuple[Issue, str]] = []
        self.comment = re.escape(self.cfg["comment"])
        self.ex_header = re.compile(rf"^\s*{self.comment}\s+(L\d-\d)\s+\|\s+(.+?)\s+\(Level\s+(\d)")
        self.open_mark = re.compile(rf"{self.comment}\s*>>>\s*SOLUTION")
        self.close_mark = re.compile(rf"{self.comment}\s*<<<\s*SOLUTION")
        self.seen_files: set[Path] = set()
        self._moji_done: set[Path] = set()

    # ---------------------------------------------------------------- helpers
    def add(self, path: Path, line: int, code: str, msg: str) -> None:
        issue = Issue(_rel(path, self.root), line, code, msg)
        reason = KNOWN_EXCEPTIONS.get((issue.path, code))
        if reason:
            self.suppressed.append((issue, reason))
        else:
            self.issues.append(issue)

    def read(self, path: Path) -> str | None:
        """Read UTF-8 text; reports BOM, bad encoding and mojibake once per file."""
        try:
            raw = path.read_bytes()
        except OSError as e:
            self.add(path, 0, "unreadable", f"cannot read file: {e}")
            return None
        if path not in self.seen_files:
            self.seen_files.add(path)
            if raw.startswith(b"\xef\xbb\xbf"):
                self.add(path, 1, "bom", "file starts with a UTF-8 BOM")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as e:
            self.add(path, 0, "encoding", f"not valid UTF-8 ({e.reason} at byte {e.start})")
            return None
        if path not in self._moji_done:
            self._moji_done.add(path)
            self.check_mojibake(path, text)
        return text

    def check_mojibake(self, path: Path, text: str) -> None:
        rel = _rel(path, self.root)
        for n, line in enumerate(text.splitlines(), 1):
            m = MOJIBAKE.search(line)
            if not m:
                continue
            if any(rel == f and key in line for f, key in MOJIBAKE_ALLOW):
                continue
            self.add(path, n, "mojibake", f"mangled UTF-8 text {m.group(0).encode('unicode_escape').decode()!s} in: {_ascii(line)}")

    @staticmethod
    def fence_flags(lines: list[str]) -> list[bool]:
        """True for every line that is inside (or is a marker of) a ``` code fence."""
        flags, inside = [], False
        for ln in lines:
            if ln.lstrip().startswith("```"):
                flags.append(True)
                inside = not inside
            else:
                flags.append(inside)
        return flags

    def check_fences(self, path: Path, text: str) -> list[bool]:
        lines = text.splitlines()
        flags = self.fence_flags(lines)
        inside = False
        start = 0
        for n, ln in enumerate(lines, 1):
            if ln.lstrip().startswith("```"):
                inside = not inside
                start = n
            elif inside and "\t" in ln:
                self.add(path, n, "tab-in-fence", "TAB character inside a code fence (use spaces)")
        if inside:
            self.add(path, start, "open-fence", "code fence is never closed")
        return flags

    # ---------------------------------------------------------------- per day
    def day_folders(self) -> dict[int, list[Path]]:
        found: dict[int, list[Path]] = {}
        if self.days_dir.is_dir():
            for p in sorted(self.days_dir.iterdir()):
                m = re.match(r"day(\d{2})_", p.name)
                if p.is_dir() and m:
                    found.setdefault(int(m.group(1)), []).append(p)
        return found

    def run(self) -> list[Issue]:
        if not self.days_dir.is_dir():
            self.add(self.days_dir, 0, "missing-dir", "days folder not found")
        found = self.day_folders()
        for n in DAYS:
            folders = found.get(n, [])
            if not folders:
                self.add(self.days_dir, 0, "missing-day", f"no folder for day {n:02d} (expected day{n:02d}_<topic>)")
                continue
            if len(folders) > 1:
                names = ", ".join(f.name for f in folders)
                self.add(folders[1], 0, "duplicate-day", f"more than one folder for day {n:02d}: {names}")
            self.check_day(n, folders[0])
        for n in sorted(set(found) - set(DAYS)):
            self.add(found[n][0], 0, "unexpected-day", f"day folder outside 1-30: {found[n][0].name}")
        self.check_datasets_dir()
        self.check_toplevel_docs()
        return self.issues

    def check_day(self, n: int, folder: Path) -> None:
        cfg = self.cfg
        lesson = folder / "LESSON.md"
        answers = self.sol_dir / cfg["answers"].format(n=n)
        examples = folder / cfg["examples"]
        practice = folder / cfg["practice"]
        solution = self.sol_dir / cfg["solution"].format(n=n)
        for f, what in ((lesson, "lesson"), (examples, "examples file"), (practice, "practice file"),
                        (solution, "solution file"), (answers, "quiz answers file")):
            if not f.is_file():
                self.add(f, 0, "missing-file", f"day {n:02d}: {what} is missing")
        if lesson.is_file():
            self.check_lesson(n, lesson, answers)
        ex_practice = self.check_exercises(n, practice, solution_file=False) if practice.is_file() else None
        ex_solution = self.check_exercises(n, solution, solution_file=True) if solution.is_file() else None
        if ex_practice is not None and ex_solution is not None and ex_practice != ex_solution:
            only_p = sorted(set(ex_practice) - set(ex_solution))
            only_s = sorted(set(ex_solution) - set(ex_practice))
            self.add(practice, 0, "practice-solution-mismatch",
                     f"exercise ids differ from {_rel(solution, self.root)} (only in practice: {only_p}; only in solution: {only_s})"
                     if (only_p or only_s) else f"exercise order/titles differ from {_rel(solution, self.root)}")
        if examples.is_file():
            self.read(examples)
        drills = folder / "DRILLS.json"
        if drills.is_file():
            self.check_drills(n, drills)

    # ---------------------------------------------------------------- lesson
    def quiz_numbers_ok(self, n: int, nums: list[int]) -> bool:
        """8 questions numbered 1-8; project days (weekly review / exam) may have 6 or more, numbered 1..N."""
        if n in self.cfg["project_days"]:
            return len(nums) >= 6 and nums == list(range(1, len(nums) + 1))
        return nums == list(range(1, 9))

    def quiz_rule(self, n: int) -> str:
        return "6 or more questions numbered 1..N (project day)" if n in self.cfg["project_days"] else "8 questions numbered 1-8"

    def check_lesson(self, n: int, path: Path, answers: Path) -> None:
        text = self.read(path)
        if text is None:
            return
        lines = text.splitlines()
        fenced = self.check_fences(path, text)
        prose = [(i + 1, ln) for i, ln in enumerate(lines) if not fenced[i]]

        # title
        first = next(((i + 1, ln) for i, ln in enumerate(lines) if ln.strip()), None)
        if not first or not LESSON_TITLE.match(first[1]):
            self.add(path, first[0] if first else 1, "lesson-title",
                     f"first line must look like '# Day {n:02d} \u2014 Title' (em dash); found: {_ascii(first[1]) if first else '(empty file)'}")
        elif int(LESSON_TITLE.match(first[1]).group(1)) != n:
            self.add(path, first[0], "lesson-title", f"title says day {LESSON_TITLE.match(first[1]).group(1)} but the folder is day {n:02d}")

        # scenario paragraph
        sc = next((k for k, (_, ln) in enumerate(prose) if re.match(r"^##\s+.*[Ss]cenario", ln)), None)
        if sc is None:
            self.add(path, 0, "scenario", "no '## ... scenario' heading")
        else:
            para = ""
            for _, ln in prose[sc + 1:]:
                s = ln.strip()
                if not s:
                    if para:
                        break
                    continue
                if s.startswith("#") or s == "---":
                    break
                para += s + " "
            if len(para.strip()) < 40:
                self.add(path, prose[sc][0], "scenario", "the scenario heading is not followed by a real paragraph (>= 40 characters)")

        # concepts (project days have their own structure: any number up to 8)
        project = n in self.cfg["project_days"]
        concepts = [ln for _, ln in prose if CONCEPT.match(ln)]
        if not (0 if project else 4) <= len(concepts) <= 8:
            self.add(path, 0, "concepts",
                     f"{len(concepts)} concept headings '### N.M Name' (need {'at most 8' if project else '4-8'})")

        # hints
        opens = [(i, ln) for i, ln in prose if "<details" in ln]
        closes = [i for i, ln in prose if "</details>" in ln]
        if len(opens) != 3 or len(closes) != 3:
            self.add(path, opens[0][0] if opens else 0, "hints",
                     f"{len(opens)} <details> blocks and {len(closes)} </details> (need exactly 3 of each)")
        elif any("<summary>" not in ln and "<summary>" not in lines[i] for i, ln in opens):
            self.add(path, opens[0][0], "hints", "a hint <details> has no <summary> on its line or the next")

        # quiz
        qi = next((k for k, (_, ln) in enumerate(prose) if re.match(r"^##\s+\d+\..*(Quiz|Review Test)", ln)), None)
        nums: list[int] = []
        if qi is None:
            self.add(path, 0, "quiz", "no '## N. Quiz' section")
        else:
            for _, ln in prose[qi + 1:]:
                if ln.startswith("## "):
                    break
                m = QUESTION.match(ln)
                if m:
                    nums.append(int(m.group(1)))
            if not self.quiz_numbers_ok(n, nums):
                self.add(path, prose[qi][0], "quiz", f"quiz must have {self.quiz_rule(n)}; found numbers {nums}")
        if answers.is_file():
            atext = self.read(answers)
            if atext is not None:
                afenced = self.fence_flags(atext.splitlines())
                anums = [int(m.group(1)) for i, ln in enumerate(atext.splitlines())
                         if not afenced[i] and (m := re.match(r"^(\d+)\.\s", ln))]
                if not self.quiz_numbers_ok(n, anums):
                    self.add(answers, 0, "answers", f"answers must have {self.quiz_rule(n)}; found {anums}")
                elif nums and nums != anums:
                    self.add(answers, 0, "answers", f"answer numbers {anums} do not match the lesson's quiz numbers {nums}")

        # datasets mentioned
        for i, ln in enumerate(lines, 1):
            for m in DATASET_REF.finditer(ln):
                if not (self.data_dir / m.group(1)).is_file():
                    self.add(path, i, "dataset-missing", f"dataset '{m.group(1)}' is not in {_rel(self.data_dir, self.root)}")

    # ---------------------------------------------------------------- exercises
    def check_exercises(self, n: int, path: Path, solution_file: bool) -> list[tuple[str, str]] | None:
        text = self.read(path)
        if text is None:
            return None
        lines = text.splitlines()
        found: list[tuple[str, str]] = []
        counts: dict[int, int] = {}
        seen: dict[str, int] = {}
        for i, ln in enumerate(lines, 1):
            m = self.ex_header.match(ln)
            if not m:
                continue
            ex_id, title, level = m.group(1), m.group(2), int(m.group(3))
            found.append((ex_id, title))
            lid = int(ex_id[1])
            if lid != level:
                self.add(path, i, "exercise-level", f"{ex_id} says '(Level {level}' but the id is level {lid}")
            if ex_id in seen:
                self.add(path, i, "exercise-duplicate", f"exercise id {ex_id} already used on line {seen[ex_id]}")
                continue
            seen[ex_id] = i
            want = counts.get(lid, 0) + 1
            if int(ex_id.split("-")[1]) != want:
                self.add(path, i, "exercise-sequence", f"expected L{lid}-{want} but found {ex_id}")
            counts[lid] = max(want, int(ex_id.split("-")[1]))
        if not found:
            self.add(path, 0, "exercise-none", f"no exercise headers (format: {self.cfg['comment']} L1-1 | Title   (Level 1 - Beginner))")
        # solution markers
        open_at = 0
        for i, ln in enumerate(lines, 1):
            if self.open_mark.search(ln):
                if open_at:
                    self.add(path, i, "marker", f">>> SOLUTION opened again (previous one on line {open_at} is not closed)")
                open_at = i
            elif self.close_mark.search(ln):
                if not open_at:
                    self.add(path, i, "marker", "<<< SOLUTION without a matching >>> SOLUTION")
                open_at = 0
        if open_at:
            self.add(path, open_at, "marker", ">>> SOLUTION is never closed by <<< SOLUTION")
        if solution_file and not any(self.open_mark.search(ln) for ln in lines):
            self.add(path, 0, "marker", "solution file has no >>> SOLUTION markers (practice file cannot be generated)")
        return found

    # ---------------------------------------------------------------- misc files
    def check_drills(self, n: int, path: Path) -> None:
        text = self.read(path)
        if text is None:
            return
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            self.add(path, e.lineno, "drills-json", f"invalid JSON: {e.msg}")
            return
        if not isinstance(data, dict) or "day" not in data or "drills" not in data:
            self.add(path, 1, "drills-keys", "DRILLS.json must be an object with the keys 'day' and 'drills'")
            return
        if data["day"] != n:
            self.add(path, 1, "drills-day", f"'day' is {data['day']!r} but the folder is day {n:02d}")
        if not isinstance(data["drills"], list):
            self.add(path, 1, "drills-keys", "'drills' must be a list")

    def check_datasets_dir(self) -> None:
        if not self.data_dir.is_dir():
            self.add(self.data_dir, 0, "missing-dir", "datasets folder not found")
            return
        for p in sorted(self.data_dir.iterdir()):
            if p.is_file() and p.suffix in TEXT_SUFFIXES:
                try:
                    if p.read_bytes().startswith(b"\xef\xbb\xbf"):
                        self.add(p, 1, "bom", "file starts with a UTF-8 BOM")
                except OSError:
                    pass

    def check_toplevel_docs(self) -> None:
        docs = sorted(self.base.glob("*.md"))
        cheats = self.base / "cheatsheets"
        extra = sorted(cheats.glob("*.md")) if cheats.is_dir() else []
        for p in docs + extra:
            text = self.read(p)
            if text is not None:
                self.check_fences(p, text)
        for p in docs:
            text = self.read(p)
            if text is None:
                continue
            lines = text.splitlines()
            fenced = self.fence_flags(lines)
            for i, ln in enumerate(lines, 1):
                if fenced[i - 1]:
                    continue
                for m in LINK.finditer(INLINE_CODE.sub(lambda mm: " " * len(mm.group(0)), ln)):
                    target = m.group(1)
                    if re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*:", target) or target.startswith("#"):
                        continue
                    rel = unquote(re.split(r"[#?]", target, maxsplit=1)[0])
                    if rel and not (p.parent / rel).exists():
                        self.add(p, i, "broken-link", f"relative link does not exist: {target}")


def lint(root: Path, tracks: tuple[str, ...] = TRACKS, suppressed: list | None = None) -> list[Issue]:
    issues: list[Issue] = []
    for t in tracks:
        lt = Linter(root, t)
        issues += lt.run()
        if suppressed is not None:
            suppressed += lt.suppressed
    return issues


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Static lint of the Python and Java course content.")
    ap.add_argument("--track", choices=("python", "java", "both"), default="both")
    ap.add_argument("--root", type=Path, default=REPO, help="project root (default: this repository)")
    ap.add_argument("--quiet", action="store_true", help="print only problems")
    a = ap.parse_args(argv)
    tracks = TRACKS if a.track == "both" else (a.track,)
    suppressed: list = []
    issues = lint(a.root, tracks, suppressed)
    for i in issues:
        print(i)
    for i, reason in suppressed:
        print(f"note: known exception, not counted: {i}\n      reason: {reason}")
    if issues:
        print(f"\nlint_content: {len(issues)} problem(s) found")
        return 1
    if not a.quiet:
        print(f"lint_content: OK ({' + '.join(tracks)}: 30 days each, no problems)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
