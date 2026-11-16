"""Find a JDK and run a single-file Java program the same way the Java portal does (maintainer helper).

Order: JAVA_HOME -> <project>/.tools/jdk21 -> whatever `java` is on PATH.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA_ROOT = ROOT / "java"
EXE = ".exe" if os.name == "nt" else ""


def java_home() -> Path | None:
    for cand in (os.environ.get("JAVA_HOME"), str(ROOT / ".tools" / "jdk21")):
        if cand and (Path(cand) / "bin" / f"javac{EXE}").is_file():
            return Path(cand)
    return None


def tool(name: str = "java") -> str:
    home = java_home()
    if home:
        return str(home / "bin" / f"{name}{EXE}")
    found = shutil.which(name)
    if not found:
        raise SystemExit(f"No JDK found. Run: python _dev_tools/fetch_java_libs.py --jdk   (or install JDK 21 and set JAVA_HOME)")
    return found


def classpath() -> list[str]:
    lib = JAVA_ROOT / "lib"
    return [str(lib / "*")] if lib.is_dir() and any(lib.glob("*.jar")) else []


def command(source: Path) -> list[str]:
    cmd = [tool("java"), "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8", "-Xshare:auto"]
    cp = classpath()
    if cp:
        cmd += ["-cp", os.pathsep.join(cp)]
    return cmd + [str(source)]


def run_file(source: Path, cwd: Path, stdin: str = "", timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run(command(source), input=stdin, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=str(cwd), timeout=timeout)
