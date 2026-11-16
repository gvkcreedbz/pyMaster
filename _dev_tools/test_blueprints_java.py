"""Runs the three Java blueprint demos the way the portal does and checks them against meta.json.

Run: python -m pytest _dev_tools/test_blueprints_java.py -q -p no:cacheprovider

For each blueprint (java/blueprints/*/meta.json) the test copies the folder to a temp dir, compiles every .java file
with javac into _out, runs the demo class with `java -cp _out Demo`, and checks:
  * exit code 0 and finished in under 60 s
  * every "expect" string from meta.json appears in the output
  * every file in "files" exists, and every .java file in the folder is listed
  * BLUEPRINT.md exists and has at least 3 mermaid diagrams
  * two runs print the same text (the demos are deterministic)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import jdk  # noqa: E402  (maintainer helper: finds the JDK exactly like the portal)

BP_DIR = jdk.JAVA_ROOT / "blueprints"
JAVA_FLAGS = ["-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8", "-Xshare:auto"]  # = portal.track.JAVA_FLAGS
TIME_LIMIT = 60
IDS = sorted(p.parent.name for p in BP_DIR.glob("*/meta.json"))


def meta_of(folder: str) -> dict:
    return json.loads((BP_DIR / folder / "meta.json").read_text(encoding="utf-8"))


def run_demo(folder: str, work: Path) -> tuple[int, str, float]:
    """Mirror portal.runner.run_blueprint_demo (Java branch): copy, javac *.java -> _out, java -cp _out <Demo class>."""
    src, dst = BP_DIR / folder, work / folder
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.db", "*.class", "_out"))
    out = dst / "_out"
    out.mkdir()
    javac = subprocess.run([jdk.tool("javac"), "-encoding", "UTF-8", "-d", str(out), *sorted(p.name for p in dst.glob("*.java"))],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=dst, timeout=120)
    assert javac.returncode == 0, f"compile error:\n{javac.stdout}{javac.stderr}"
    cls = meta_of(folder)["demo"].rsplit(".", 1)[0]
    t0 = time.time()
    run = subprocess.run([jdk.tool("java"), *JAVA_FLAGS, "-cp", str(out), cls], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", cwd=dst, timeout=TIME_LIMIT + 30)
    return run.returncode, run.stdout + run.stderr, time.time() - t0


@pytest.fixture(scope="module")
def work():
    d = Path(tempfile.mkdtemp(prefix="jbp_"))
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="module")
def results(work):
    """folder -> (returncode, output, seconds). Each demo runs once per test session, in its own temp copy."""
    return {}


def result(results, work, folder):
    if folder not in results:
        results[folder] = run_demo(folder, work / "a")
    return results[folder]


def test_three_java_blueprints_exist():
    assert IDS == ["01_live_order_tracker", "02_ticket_triage_pipeline", "03_site_watcher"]


@pytest.mark.skipif(jdk.java_home() is None, reason="no JDK 21 found (python _dev_tools/fetch_java_libs.py --jdk)")
class TestJavaBlueprints:
    @pytest.mark.parametrize("folder", IDS)
    def test_demo_exit_code_and_time(self, folder, results, work):
        rc, out, secs = result(results, work, folder)
        assert rc == 0, f"exit code {rc}\n{out}"
        assert secs < TIME_LIMIT, f"demo took {secs:.1f}s"

    @pytest.mark.parametrize("folder", IDS)
    def test_demo_prints_every_expect_line(self, folder, results, work):
        _, out, _ = result(results, work, folder)
        expect = meta_of(folder)["expect"]
        assert expect, "meta.json has no 'expect' lines"
        missing = [e for e in expect if e not in out]
        assert not missing, f"missing from output: {missing}\n--- output ---\n{out}"

    @pytest.mark.parametrize("folder", IDS)
    def test_demo_is_deterministic(self, folder, results, work):
        _, first, _ = result(results, work, folder)
        rc, second, _ = run_demo(folder, work / "b")
        assert rc == 0 and second == first

    @pytest.mark.parametrize("folder", IDS)
    def test_demo_leaves_nothing_behind(self, folder, results, work):
        result(results, work, folder)
        src = BP_DIR / folder
        stray = [p.name for p in src.iterdir() if p.suffix in {".class", ".db"} or p.name == "_out"]
        assert not stray, f"stray files in the source folder: {stray}"


@pytest.mark.parametrize("folder", IDS)
def test_files_list_matches_the_folder(folder):
    meta = meta_of(folder)
    listed = meta["files"]
    assert meta["demo"] in listed
    for name in listed:
        assert (BP_DIR / folder / name).is_file(), f"{name} is listed in meta.json but missing"
    on_disk = {p.name for p in (BP_DIR / folder).glob("*.java")}
    assert on_disk - set(listed) == set(), f"not listed in meta.json: {sorted(on_disk - set(listed))}"
    assert len(listed) == len(set(listed))


@pytest.mark.parametrize("folder", IDS)
def test_guide_and_meta_are_complete(folder):
    meta = meta_of(folder)
    for key in ("id", "title", "emoji", "kind", "tagline", "stack", "patterns", "level", "minutes", "demo", "files", "expect"):
        assert key in meta, f"meta.json lacks '{key}'"
    assert meta["id"].startswith("java-")
    guide = (BP_DIR / folder / "BLUEPRINT.md").read_text(encoding="utf-8")
    assert guide.count("```mermaid") >= 3
    assert not guide.startswith("\ufeff")
    assert 140 <= len(guide.splitlines()) <= 400
    assert "Build it yourself" in guide and "What breaks in production" in guide
