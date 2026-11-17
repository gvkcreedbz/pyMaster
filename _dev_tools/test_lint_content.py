"""pytest for lint_content.py: the real repository is clean, and fabricated broken fixture trees are caught.

    python -m pytest _dev_tools/test_lint_content.py -q
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint_content as lc  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
EM = "\u2014"
BOTH = pytest.mark.parametrize("track", ["python", "java"])

# ----------------------------------------------------------------------------------------------------- fixture builder


def _lesson(n: int) -> str:
    concepts = "\n".join(f"### 1.{k} Concept {k}\n```text\ncode {k}\n```\n" for k in range(1, 6))
    hints = "\n".join(f"<details><summary>Hint {k}</summary>\ntext\n</details>" for k in range(1, 4))
    quiz = "\n".join(f"{k}. Question {k}?" for k in range(1, 9))
    return (
        f"# Day {n:02d} {EM} Topic {n}\n\n| Time | Goal | Level |\n|---|---|---|\n| 2 h | goal | Beginner |\n\n"
        "## \U0001F30D Real-world scenario & trend\n"
        "**A cafe receipt printer.** Every point-of-sale machine runs instructions from top to bottom.\n\n---\n\n"
        f"## 1. Concepts\n\n{concepts}\n## 2. Code along\nUses datasets/sales.csv for practice.\n\n"
        f"## 5. Stuck? Hint ladder\n{hints}\n\n## 6. Quiz (10 min)\n{quiz}\n\n## 7. Wrap-up\nDone.\n"
    )


def _solution(c: str) -> str:
    return (
        f"{c} ---------------------------------------------\n{c} L1-1 | First   (Level 1 - Beginner)\n{c} ---------------------------------------------\n"
        f"{c} >>> SOLUTION\nanswer one\n{c} <<< SOLUTION\n"
        f"{c} L1-2 | Second   (Level 1 - Beginner)\n{c} >>> SOLUTION\nanswer two\n{c} <<< SOLUTION\n"
        f"{c} L2-1 | Third   (Level 2 - Intermediate)\n{c} >>> SOLUTION\nanswer three\n{c} <<< SOLUTION\n"
        f"{c} L3-1 | Fourth   (Level 3 - Challenge)\n{c} >>> SOLUTION\nanswer four\n{c} <<< SOLUTION\n"
    )


def _practice(c: str) -> str:
    return (
        f"{c} L1-1 | First   (Level 1 - Beginner)\n{c} TODO\n{c} L1-2 | Second   (Level 1 - Beginner)\n{c} TODO\n"
        f"{c} L2-1 | Third   (Level 2 - Intermediate)\n{c} TODO\n{c} L3-1 | Fourth   (Level 3 - Challenge)\n{c} TODO\n"
    )


def _w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def build_track(root: Path, track: str) -> None:
    cfg = lc.load_track(track).CONFIGS[track]
    base = root / "java" if track == "java" else root
    c = cfg["comment"]
    for n in range(1, 31):
        day = base / "days" / f"day{n:02d}_topic"
        _w(day / "LESSON.md", _lesson(n))
        _w(day / cfg["examples"], f"{c} examples\n")
        _w(day / cfg["practice"], _practice(c))
        _w(base / "solutions" / cfg["solution"].format(n=n), _solution(c))
        _w(base / "solutions" / cfg["answers"].format(n=n), f"# Day {n:02d} {EM} Quiz answers\n" + "\n".join(f"{k}. Answer {k}" for k in range(1, 9)) + "\n")
    _w(base / "datasets" / "sales.csv", "a,b\n1,2\n")
    _w(base / "days" / "day01_topic" / "DRILLS.json", json.dumps({"day": 1, "drills": []}))
    _w(base / "README.md", "# Readme\nSee [day one](days/day01_topic/LESSON.md), [setup](SETUP.md#top) and <https://example.com>.\n"
                           "External [site](https://example.com/x.md) and `[code](nope.md)` are fine.\n```\n[fenced](nope.md)\n```\n")
    _w(base / "SETUP.md", "# Setup\nBack to [readme](README.md).\n")


@pytest.fixture(scope="module")
def templates(tmp_path_factory) -> dict[str, Path]:
    out = {}
    for track in ("python", "java"):
        out[track] = tmp_path_factory.mktemp(f"template_{track}")
        build_track(out[track], track)
    return out


@pytest.fixture
def tree(templates, tmp_path, request) -> Path:
    """A fresh valid project tree. Tests parametrized with `track` only get that track copied (faster)."""
    params = getattr(getattr(request.node, "callspec", None), "params", {})
    dst = tmp_path / "proj"
    for track in ([params["track"]] if "track" in params else ["python", "java"]):
        shutil.copytree(templates[track], dst, dirs_exist_ok=True)
    return dst

def base_of(root: Path, track: str) -> Path:
    return root / "java" if track == "java" else root


def lesson_path(root: Path, track: str, n: int = 5) -> Path:
    return base_of(root, track) / "days" / f"day{n:02d}_topic" / "LESSON.md"


def edit(path: Path, fn) -> None:
    path.write_bytes(fn(path.read_bytes().decode("utf-8")).encode("utf-8"))


def codes(root: Path, track: str) -> list[lc.Issue]:
    return lc.lint(root, (track,))


def assert_one(issues, code: str, path_part: str, line: int | None = None):
    hits = [i for i in issues if i.code == code and path_part in i.path]
    assert hits, f"expected {code} in {path_part}, got: {[str(i) for i in issues]}"
    if line is not None:
        assert any(i.line == line for i in hits), [str(i) for i in hits]
    return hits[0]


# ----------------------------------------------------------------------------------------------------- the real repo


def test_real_repo_is_clean():
    suppressed: list = []
    issues = lc.lint(REPO, lc.TRACKS, suppressed)
    assert issues == [], "\n".join(str(i) for i in issues)
    # every reviewed exception must still be needed, otherwise it should be deleted from KNOWN_EXCEPTIONS
    assert {(i.path, i.code) for i, _ in suppressed} == set(lc.KNOWN_EXCEPTIONS)


def test_cli_on_real_repo_exits_zero():
    r = subprocess.run([sys.executable, str(REPO / "_dev_tools" / "lint_content.py"), "--quiet"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr


# ----------------------------------------------------------------------------------------------------- the fixture tree


@BOTH
def test_fixture_tree_is_clean(tree, track):
    assert codes(tree, track) == []


@BOTH
def test_missing_day_folder(tree, track):
    shutil.rmtree(base_of(tree, track) / "days" / "day05_topic")
    assert_one(codes(tree, track), "missing-day", "days")


@BOTH
def test_duplicate_day_folder(tree, track):
    shutil.copytree(base_of(tree, track) / "days" / "day05_topic", base_of(tree, track) / "days" / "day05_other")
    assert_one(codes(tree, track), "duplicate-day", "days/day05")


@BOTH
@pytest.mark.parametrize("which", ["lesson", "examples", "practice", "solution", "answers"])
def test_missing_files(tree, track, which):
    cfg = lc.load_track(track).CONFIGS[track]
    b = base_of(tree, track)
    target = {"lesson": b / "days/day03_topic/LESSON.md", "examples": b / "days/day03_topic" / cfg["examples"],
              "practice": b / "days/day03_topic" / cfg["practice"], "solution": b / "solutions" / cfg["solution"].format(n=3),
              "answers": b / "solutions" / cfg["answers"].format(n=3)}[which]
    target.unlink()
    assert_one(codes(tree, track), "missing-file", target.name)


@BOTH
@pytest.mark.parametrize("title", ["# Day 05 - Topic", "## Day 05 \u2014 Topic", "# Day 5 \u2014 Topic", "# Day 06 \u2014 Topic"])
def test_bad_title(tree, track, title):
    edit(lesson_path(tree, track), lambda t: re.sub(r"^# Day 05 \u2014 Topic 5", title, t, count=1))
    assert_one(codes(tree, track), "lesson-title", "day05_topic", 1)


@BOTH
def test_missing_scenario_paragraph(tree, track):
    edit(lesson_path(tree, track), lambda t: re.sub(r"\*\*A cafe.*\n", "\n", t))
    assert_one(codes(tree, track), "scenario", "day05_topic")


@BOTH
def test_missing_scenario_heading(tree, track):
    edit(lesson_path(tree, track), lambda t: t.replace("Real-world scenario", "Introduction"))
    assert_one(codes(tree, track), "scenario", "day05_topic")


@BOTH
@pytest.mark.parametrize("keep", [3, 9])
def test_concept_count(tree, track, keep):
    def fn(t):
        t = re.sub(r"### 1\.\d Concept \d\n```text\ncode \d\n```\n", "", t)
        return t.replace("## 1. Concepts\n", "## 1. Concepts\n" + "".join(f"### 1.{k} C{k}\n" for k in range(1, keep + 1)))
    edit(lesson_path(tree, track), fn)
    assert_one(codes(tree, track), "concepts", "day05_topic")


@BOTH
def test_concept_headings_inside_fences_do_not_count(tree, track):
    edit(lesson_path(tree, track), lambda t: t.replace("code 1\n", "code 1\n### 9.9 not a heading\n"))
    assert codes(tree, track) == []


@BOTH
def test_project_day_may_have_no_concepts_and_long_quiz(tree, track):
    def fn(t):
        t = re.sub(r"### 1\.\d Concept \d\n```text\ncode \d\n```\n", "", t)
        return t.replace("8. Question 8?", "8. Question 8?\n" + "\n".join(f"{k}. More {k}?" for k in range(9, 16)))
    edit(lesson_path(tree, track, 7), fn)
    answers = base_of(tree, track) / "solutions" / lc.load_track(track).CONFIGS[track]["answers"].format(n=7)
    edit(answers, lambda t: t + "".join(f"{k}. Answer {k}\n" for k in range(9, 16)))
    assert codes(tree, track) == []


@BOTH
@pytest.mark.parametrize("count", [2, 4])
def test_hint_count(tree, track, count):
    def fn(t):
        t = re.sub(r"<details>.*?</details>\n?", "", t, flags=re.S)
        return t.replace("## 5. Stuck? Hint ladder\n", "## 5. Stuck? Hint ladder\n" + "<details><summary>h</summary>x</details>\n" * count)
    edit(lesson_path(tree, track), fn)
    assert_one(codes(tree, track), "hints", "day05_topic")


@BOTH
def test_quiz_with_seven_questions(tree, track):
    edit(lesson_path(tree, track), lambda t: t.replace("8. Question 8?\n", ""))
    assert_one(codes(tree, track), "quiz", "day05_topic")
    assert_one(codes(tree, track), "answers", "answers.md")  # the answers file still has 8 -> mismatch is reported


@BOTH
def test_quiz_numbers_must_match_answers(tree, track):
    answers = base_of(tree, track) / "solutions" / lc.load_track(track).CONFIGS[track]["answers"].format(n=5)
    edit(answers, lambda t: t.replace("8. Answer 8", "9. Answer 9"))
    assert_one(codes(tree, track), "answers", "day05_answers.md")


@BOTH
def test_exercise_duplicate_gap_and_level(tree, track):
    cfg = lc.load_track(track).CONFIGS[track]
    prac = base_of(tree, track) / "days" / "day04_topic" / cfg["practice"]
    sol = base_of(tree, track) / "solutions" / cfg["solution"].format(n=4)
    edit(prac, lambda t: t.replace("L1-2 | Second", "L1-1 | Second"))
    edit(sol, lambda t: t.replace("L2-1 | Third", "L2-3 | Third"))
    edit(sol, lambda t: t.replace("L3-1 | Fourth   (Level 3", "L3-1 | Fourth   (Level 2"))
    found = codes(tree, track)
    assert_one(found, "exercise-duplicate", prac.name)
    assert_one(found, "exercise-sequence", sol.name)
    assert_one(found, "exercise-level", sol.name)
    assert_one(found, "practice-solution-mismatch", prac.name)


@BOTH
def test_no_exercises(tree, track):
    cfg = lc.load_track(track).CONFIGS[track]
    prac = base_of(tree, track) / "days" / "day04_topic" / cfg["practice"]
    prac.write_bytes(b"nothing here\n")
    assert_one(codes(tree, track), "exercise-none", prac.name)


@BOTH
def test_unclosed_and_stray_markers(tree, track):
    cfg = lc.load_track(track).CONFIGS[track]
    c = cfg["comment"]
    sol = base_of(tree, track) / "solutions" / cfg["solution"].format(n=6)
    edit(sol, lambda t: t.replace(f"{c} <<< SOLUTION\n", "", 1))  # first block never closes -> next open is a double open
    found = codes(tree, track)
    assert_one(found, "marker", sol.name)
    edit(sol, lambda t: t + f"{c} <<< SOLUTION\n")
    assert any("without a matching" in i.msg for i in codes(tree, track))


@BOTH
def test_marker_left_open_at_end(tree, track):
    cfg = lc.load_track(track).CONFIGS[track]
    sol = base_of(tree, track) / "solutions" / cfg["solution"].format(n=6)
    edit(sol, lambda t: t + f"{cfg['comment']} >>> SOLUTION\n")
    assert any("never closed" in i.msg for i in codes(tree, track))


@BOTH
def test_bom_is_reported(tree, track):
    p = lesson_path(tree, track)
    p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
    assert_one(codes(tree, track), "bom", "day05_topic/LESSON.md", 1)


@BOTH
def test_bom_in_python_or_java_source(tree, track):
    cfg = lc.load_track(track).CONFIGS[track]
    p = base_of(tree, track) / "days" / "day05_topic" / cfg["practice"]
    p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
    assert_one(codes(tree, track), "bom", cfg["practice"])


@BOTH
def test_tab_in_code_fence_only(tree, track):
    p = lesson_path(tree, track)
    edit(p, lambda t: t.replace("code 2\n", "code\t2\n").replace("## 7. Wrap-up\nDone.", "## 7. Wrap-up\nTabs\there are fine."))
    hits = [i for i in codes(tree, track) if i.code == "tab-in-fence"]
    assert len(hits) == 1 and hits[0].line > 0 and "LESSON.md" in hits[0].path


@BOTH
def test_unclosed_fence(tree, track):
    edit(lesson_path(tree, track), lambda t: t + "```text\nnever closed\n")
    assert_one(codes(tree, track), "open-fence", "day05_topic")


@BOTH
def test_mojibake_in_lesson(tree, track):
    bad = "caf\u00e9 \u00e2\u20ac\u201d dash"  # an em dash that went through cp1252
    edit(lesson_path(tree, track), lambda t: t.replace("Done.", bad))
    hit = assert_one(codes(tree, track), "mojibake", "day05_topic/LESSON.md")
    assert hit.line > 0 and "\\xe2" in str(hit)


@BOTH
def test_legit_accents_and_ellipsis_are_not_mojibake(tree, track):
    edit(lesson_path(tree, track), lambda t: t.replace("Done.", "caf\u00e9\u2026 na\u00efve \u20b9 \U0001F600 \u2014 ok"))
    assert codes(tree, track) == []


@BOTH
def test_mojibake_allowed_only_in_setup_quote_lines(tree, track):
    setup = base_of(tree, track) / "SETUP.md"
    quote = "\u00e2\u20ac\u201d"
    key = "Weird characters like" if track == "python" else "Garbled characters like"
    setup.write_bytes((f"# Setup\n| {key} `{quote}` | fix |\n").encode("utf-8"))
    assert codes(tree, track) == []
    setup.write_bytes((f"# Setup\nAn accidental {quote} dash\n").encode("utf-8"))
    assert_one(codes(tree, track), "mojibake", "SETUP.md", 2)


@BOTH
def test_broken_relative_link(tree, track):
    readme = base_of(tree, track) / "README.md"
    edit(readme, lambda t: t + "[gone](days/day99_nothing/LESSON.md) and ![pic](img/missing.png)\n")
    found = [i for i in codes(tree, track) if i.code == "broken-link"]
    assert len(found) == 2 and all(i.path.endswith("README.md") and i.line > 0 for i in found)


@BOTH
def test_dataset_mentioned_in_lesson_must_exist(tree, track):
    edit(lesson_path(tree, track), lambda t: t.replace("Uses datasets/sales.csv", "Uses ../../datasets/nope.csv"))
    hit = assert_one(codes(tree, track), "dataset-missing", "day05_topic")
    assert "nope.csv" in hit.msg


@BOTH
def test_drills_json(tree, track):
    d = base_of(tree, track) / "days" / "day02_topic" / "DRILLS.json"
    d.write_bytes(b'{"day": 2, "drills": [')
    assert_one(codes(tree, track), "drills-json", "DRILLS.json")
    d.write_bytes(b'{"day": 2}')
    assert_one(codes(tree, track), "drills-keys", "DRILLS.json")
    d.write_bytes(b'{"day": 3, "drills": []}')
    assert_one(codes(tree, track), "drills-day", "DRILLS.json")
    d.write_bytes(b'{"day": 2, "drills": []}')
    assert codes(tree, track) == []


@BOTH
def test_invalid_utf8(tree, track):
    p = lesson_path(tree, track)
    p.write_bytes(p.read_bytes() + b"\xff\xfe")
    assert_one(codes(tree, track), "encoding", "day05_topic")


# ----------------------------------------------------------------------------------------------------- command line


def test_cli_reports_file_line_and_exit_code(tree, capsys):
    edit(lesson_path(tree, "java"), lambda t: t.replace("# Day 05 \u2014", "# Day 05 -"))
    assert lc.main(["--root", str(tree), "--track", "python"]) == 0
    assert lc.main(["--root", str(tree), "--track", "java"]) == 1
    out = capsys.readouterr().out
    assert re.search(r"java/days/day05_topic/LESSON\.md:1: .*\[lesson-title\]", out), out
    assert lc.main(["--root", str(tree)]) == 1


def test_cli_subprocess_with_root(tree):
    script = str(REPO / "_dev_tools" / "lint_content.py")
    ok = subprocess.run([sys.executable, script, "--root", str(tree), "--quiet"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    assert ok.returncode == 0, ok.stdout
    shutil.rmtree(tree / "days" / "day09_topic")
    bad = subprocess.run([sys.executable, script, "--root", str(tree), "--track", "python"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    assert bad.returncode == 1 and "missing-day" in bad.stdout and "day 09" in bad.stdout
