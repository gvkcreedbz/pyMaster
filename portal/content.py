"""Course content loader: turns the days/ folders into structured data for the portal.

Everything is parsed from the real course files (LESSON.md, practice.py, examples.py,
solutions/), so editing a lesson on disk updates the portal after a restart.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAYS_DIR = ROOT / "days"
SOL_DIR = ROOT / "solutions"
DATASETS = ROOT / "datasets"
DEFAULT_START = date(2026, 11, 16)

WEEKS = [
    (1, "Foundations", "Think in code: variables, decisions, loops", 1, 7),
    (2, "Data & functions", "Collections, functions, JSON-shaped data", 8, 14),
    (3, "Real-world tools", "Files, errors, modules, objects", 15, 21),
    (4, "Pro toolkit", "Testing, pandas, APIs, SQL, FastAPI", 22, 30),
]


def week_of(n: int) -> int:
    for w, _t, _s, a, b in WEEKS:
        if a <= n <= b:
            return w
    return 4


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def strip_html(s: str) -> str:
    s = re.sub(r"</?code>", "`", s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


_EX_HEADER = re.compile(r"^\s*#\s+(L\d-\d)\s+\|\s+(.+?)\s+\(Level\s+(\d)")


def parse_exercises(practice_text: str) -> list[dict]:
    lines = practice_text.splitlines()
    out: list[dict] = []
    i = 0
    while i < len(lines):
        m = _EX_HEADER.match(lines[i])
        if m:
            desc = []
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith("#") and not re.match(r"^\s*#\s*-{5,}", lines[j]):
                desc.append(re.sub(r"^\s*#\s?", "", lines[j]).rstrip())
                j += 1
            out.append({
                "id": m.group(1), "title": m.group(2).strip(), "level": int(m.group(3)),
                "desc": "\n".join(desc).strip(), "line": i + 1,
            })
            i = j
        else:
            i += 1
    return out


def parse_numbered(block: str) -> dict[int, str]:
    items: dict[int, str] = {}
    cur = None
    for line in block.splitlines():
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m:
            cur = int(m.group(1))
            items[cur] = m.group(2).strip()
        elif cur is not None and line.startswith("#"):
            break                      # a new section (e.g. "Project notes") ends the list
        elif cur is not None and line.strip() and not line.lstrip().startswith(("-", "*")):
            items[cur] += " " + line.strip()
    return items


FALLBACK_CONCEPTS = {
    7: ["Menu-loop pattern", "Input validation", "Small functions", "Week 1 review"],
    14: ["Lists of dictionaries", "Functions with one job", "Comprehensions", "Week 2 review"],
    21: ["Classes and objects", "Saving to JSON files", "Handling errors", "Week 3 review"],
}


def solution_only(text: str) -> str:
    parts = re.findall(r"#\s*>>>\s*SOLUTION[^\n]*\n(.*?)#\s*<<<\s*SOLUTION", text, flags=re.S)
    return "\n".join(p.rstrip() + "\n" for p in parts).strip() + "\n" if parts else text


@lru_cache(maxsize=1)
def load_days() -> dict[int, dict]:
    days: dict[int, dict] = {}
    for folder in sorted(DAYS_DIR.glob("day[0-9][0-9]_*")):
        n = int(folder.name[3:5])
        lesson = read(folder / "LESSON.md")
        title_m = re.search(r"^#\s+Day\s+\d+\s+—\s+(.+)$", lesson, flags=re.M)
        table = re.search(r"\|\s*⏱[^\n]*\n\|[-| ]+\|\n\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", lesson)
        scen_m = re.search(r"^##\s+🌍[^\n]*\n+(.+?)(?:\n\n|\Z)", lesson, flags=re.M | re.S)
        concepts = [c.strip().strip("`") for c in re.findall(r"^###\s+(?:\d+\.\d+\s+)?(.+)$", lesson, flags=re.M)]
        quiz_m = re.search(r"^##\s+\d+\.\s+[^\n]*?(?:Quiz|Review Test)[^\n]*\n(.*?)(?=^##\s|\Z)", lesson, flags=re.M | re.S)
        questions = parse_numbered(quiz_m.group(1)) if quiz_m else {}
        answers = parse_numbered(read(SOL_DIR / f"day{n:02d}_answers.md"))
        hints = [strip_html(h) for h in re.findall(r"<details>\s*<summary>Hint \d[^<]*</summary>(.*?)</details>", lesson, flags=re.S)]
        if not concepts:
            concepts = FALLBACK_CONCEPTS.get(n, [])
        practice = read(folder / "practice.py")
        sol = read(SOL_DIR / f"day{n:02d}_solution.py")
        extras = sorted(p.name for p in folder.glob("*.md") if p.name != "LESSON.md")
        days[n] = {
            "n": n,
            "folder": folder.name,
            "title": title_m.group(1).replace("`", "").strip() if title_m else folder.name,
            "minutes": table.group(1) if table else "2 h",
            "goal": table.group(2) if table else "",
            "level": table.group(3) if table else "",
            "week": week_of(n),
            "scenario": strip_html(scen_m.group(1)) if scen_m else "",
            "concepts": concepts,
            "lesson": lesson,
            "quiz": [{"n": k, "q": v, "a": answers.get(k, "")} for k, v in sorted(questions.items())],
            "hints": hints,
            "exercises": parse_exercises(practice),
            "practice": practice,
            "examples": read(folder / "examples.py"),
            "solution": solution_only(sol),
            "extras": extras,
            "is_project": n in (7, 14, 21, 29, 30),
        }
    return days


def day(n: int) -> dict | None:
    return load_days().get(n)


def planned_date(n: int, start: date = DEFAULT_START) -> date:
    return start + timedelta(days=n - 1)


def plan_day_for(today: date, start: date = DEFAULT_START) -> int:
    return max(1, min(30, (today - start).days + 1))


def public_day(d: dict) -> dict:
    """Day summary without heavy text (for the roadmap)."""
    return {k: d[k] for k in ("n", "title", "week", "goal", "level", "minutes", "is_project")} | {
        "exercise_count": len(d["exercises"]), "quiz_count": len(d["quiz"]),
        "concept_count": len(d["concepts"]),
    }


# ---- library documents (root docs + cheatsheets) ---------------------------------------------
def library() -> list[dict]:
    docs = [("README.md", "Start here"), ("00_GAME_PLAN.md", "Game plan"), ("SETUP.md", "Setup")]
    items = [{"id": f, "title": t, "group": "Plan"} for f, t in docs if (ROOT / f).is_file()]
    for p in sorted((ROOT / "cheatsheets").glob("*.md")):
        items.append({"id": f"cheatsheets/{p.name}", "title": p.stem.replace("_", " ").title(), "group": "Cheatsheets"})
    return items


def library_doc(doc_id: str) -> str | None:
    allowed = {i["id"] for i in library()}
    return read(ROOT / doc_id) if doc_id in allowed else None


# ---- blueprints: full-stack reference projects + the pattern catalog ---------------------------------------------
BP_DIR = ROOT / "blueprints"
BP_PATTERNS = {"id": "patterns", "title": "Pattern catalog", "emoji": "🧩", "kind": "Reusable shapes",
               "tagline": "16 patterns behind real Python back-ends, each with code you can paste and where to spot it.",
               "stack": [], "patterns": [], "level": "All", "minutes": 25, "demo": None, "files": [], "folder": ""}


@lru_cache(maxsize=1)
def load_blueprints() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for meta_file in sorted(BP_DIR.glob("*/meta.json")):
        try:
            meta = json.loads(read(meta_file))
        except ValueError:
            continue
        meta["folder"] = meta_file.parent.name
        out[meta["id"]] = meta
    return out


def blueprint_list() -> list[dict]:
    return list(load_blueprints().values()) + ([BP_PATTERNS] if (BP_DIR / "PATTERNS.md").is_file() else [])


def blueprint_doc(bid: str) -> str | None:
    if bid == "patterns":
        return read(BP_DIR / "PATTERNS.md") or None
    bp = load_blueprints().get(bid)
    return read(BP_DIR / bp["folder"] / "BLUEPRINT.md") if bp else None


def blueprint_file(bid: str, name: str) -> str | None:
    bp = load_blueprints().get(bid)
    if not bp or name not in bp["files"]:           # only files named in meta.json can be read: no path tricks
        return None
    return read(BP_DIR / bp["folder"] / name)


def day_extra(n: int, name: str) -> str | None:
    d = day(n)
    if not d or name not in d["extras"]:
        return None
    return read(DAYS_DIR / d["folder"] / name)
