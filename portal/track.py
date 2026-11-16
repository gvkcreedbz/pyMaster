"""Track configuration: the portal serves ONE course track per process (Python or Java).

Pick it with the PORTAL_TRACK environment variable (``python`` by default, ``java`` for the Java twin).
Everything that differs between the courses (folders, file names, comment syntax, run commands, editor mode,
ports, display strings) lives here, so the rest of the portal stays language-neutral.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
_EXE = ".exe" if os.name == "nt" else ""


def _find_jdk() -> Path | None:
    """JAVA_HOME -> <project>/.tools/jdk21 -> the folder of whatever `javac` is on PATH."""
    cands = [os.environ.get("JAVA_HOME"), str(PROJECT / ".tools" / "jdk21")]
    found = shutil.which("javac")
    if found:
        cands.append(str(Path(found).resolve().parent.parent))
    for c in cands:
        if c and (Path(c) / "bin" / f"javac{_EXE}").is_file():
            return Path(c)
    return None


def jtool(name: str) -> str | None:
    home = _find_jdk()
    return str(home / "bin" / f"{name}{_EXE}") if home else None


def jar_classpath() -> list[str]:
    lib = PROJECT / "java" / "lib"
    return [str(lib / "*")] if lib.is_dir() and any(lib.glob("*.jar")) else []


JAVA_FLAGS = ["-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8", "-Xshare:auto"]


def java_run_cmd(source: str) -> list[str]:
    """Run one source file the way `java File.java` does (JDK source-launcher mode)."""
    exe = jtool("java")
    if not exe:
        raise FileNotFoundError("No JDK found. Install JDK 21 (see java/SETUP.md) or run: python _dev_tools/fetch_java_libs.py --jdk")
    cmd = [exe, *JAVA_FLAGS]
    cp = jar_classpath()
    if cp:
        cmd += ["-cp", os.pathsep.join(cp)]
    return cmd + [source]


def python_run_cmd(source: str) -> list[str]:
    return [sys.executable, "-u", source]


PY_PLAY = "# Playground: write anything, press Run (Ctrl+Enter).\nprint('Hello from Py Master!')\n"
JAVA_PLAY = ('// Playground: write anything, press Run (Ctrl+Enter).\n'
             'class Play {\n    public static void main(String[] args) {\n'
             '        System.out.println("Hello from Java Master!");\n    }\n}\n')

CONFIGS = {
    "python": dict(
        id="python", name="Py Master", short="Python", other="java",
        root=PROJECT, port=8765, data_dir=Path(__file__).resolve().parent / "data",
        ext=".py", comment="#", cm_mode="python", fence="python", cm_file="python.js",
        practice="practice.py", examples="examples.py", play="play.py",
        solution="day{n:02d}_solution.py", answers="day{n:02d}_answers.md",
        blueprint_demo="python", tracer=True, play_starter=PY_PLAY, input_fn="input()",
        tagline="30 days: zero to automation, data and back-end Python",
        project_days=(7, 14, 21, 29, 30), slow_days=(25, 26, 27, 28, 29, 30),
        weeks=[
            (1, "Foundations", "Think in code: variables, decisions, loops", 1, 7),
            (2, "Data & functions", "Collections, functions, JSON-shaped data", 8, 14),
            (3, "Real-world tools", "Files, errors, modules, objects", 15, 21),
            (4, "Pro toolkit", "Testing, pandas, APIs, SQL, FastAPI", 22, 30),
        ],
    ),
    "java": dict(
        id="java", name="Java Master", short="Java", other="python",
        root=PROJECT / "java", port=8766, data_dir=Path(__file__).resolve().parent / "data-java",
        ext=".java", comment="//", cm_mode="text/x-java", fence="java", cm_file="clike.js",
        practice="Practice.java", examples="Examples.java", play="Play.java",
        solution="day{n:02d}_Solution.java", answers="day{n:02d}_answers.md",
        blueprint_demo="java", tracer=True, play_starter=JAVA_PLAY, input_fn="Scanner",
        tagline="30 days: zero to modern Java, tests, JDBC and REST",
        project_days=(7, 14, 21, 29, 30), slow_days=(24, 27, 28, 29, 30),
        weeks=[
            (1, "Foundations", "Types, decisions, loops, methods", 1, 7),
            (2, "Data & functions", "Arrays, collections, lambdas, streams", 8, 14),
            (3, "Real-world tools", "Files, exceptions, time, objects", 15, 21),
            (4, "Pro toolkit", "Generics, JUnit, JDBC, HTTP, REST", 22, 30),
        ],
    ),
}

ID = os.environ.get("PORTAL_TRACK", "python").strip().lower()
if ID not in CONFIGS:
    raise SystemExit(f"Unknown PORTAL_TRACK={ID!r}. Use one of: {', '.join(CONFIGS)}")
T = CONFIGS[ID]
IS_JAVA = ID == "java"

ROOT: Path = T["root"]
DAYS_DIR = ROOT / "days"
SOL_DIR = ROOT / "solutions"
DATASETS = ROOT / "datasets"
BP_DIR = ROOT / "blueprints"

_c = re.escape(T["comment"])
EX_HEADER = re.compile(rf"^\s*{_c}\s+(L\d-\d)\s+\|\s+(.+?)\s+\(Level\s+(\d)")
COMMENT_PREFIX = re.compile(rf"^\s*{_c}\s?")
SEPARATOR = re.compile(rf"^\s*{_c}\s*-{{5,}}")
SOLUTION_BLOCK = re.compile(rf"{_c}\s*>>>\s*SOLUTION[^\n]*\n(.*?){_c}\s*<<<\s*SOLUTION", re.S)


def run_cmd(source: str) -> list[str]:
    return java_run_cmd(source) if IS_JAVA else python_run_cmd(source)


def public() -> dict:
    """What the browser needs to know to adapt itself to this track."""
    return {k: T[k] for k in ("id", "name", "short", "other", "port", "cm_mode", "fence", "cm_file", "tagline",
                              "play_starter", "input_fn", "ext")} | {
        "other_port": CONFIGS[T["other"]]["port"], "has_jdk": (not IS_JAVA) or _find_jdk() is not None}
