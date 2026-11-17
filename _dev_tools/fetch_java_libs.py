"""Download the optional Java helpers (not committed to git because of their size).
  python _dev_tools/fetch_java_libs.py          -> java/lib/*.jar  (JUnit console, SQLite JDBC, slf4j)
  python _dev_tools/fetch_java_libs.py --jdk    -> also a portable JDK 21 in .tools/jdk21 (no admin rights needed)
start_app.bat calls this for you the first time you start the Java course.
"""
import platform
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "java" / "lib"
MAVEN = "https://repo1.maven.org/maven2/"
JARS = {
    "junit-platform-console-standalone-1.10.3.jar": "org/junit/platform/junit-platform-console-standalone/1.10.3/junit-platform-console-standalone-1.10.3.jar",
    "sqlite-jdbc-3.46.1.0.jar": "org/xerial/sqlite-jdbc/3.46.1.0/sqlite-jdbc-3.46.1.0.jar",
    "slf4j-api-2.0.13.jar": "org/slf4j/slf4j-api/2.0.13/slf4j-api-2.0.13.jar",
    "slf4j-nop-2.0.13.jar": "org/slf4j/slf4j-nop/2.0.13/slf4j-nop-2.0.13.jar",
}
ARCH = "aarch64" if platform.machine().lower() in ("arm64", "aarch64") else "x64"
JDK_URL = f"https://api.adoptium.net/v3/binary/latest/21/ga/windows/{ARCH}/jdk/hotspot/normal/eclipse"
# Some download servers answer 403 to Python's default user agent, so identify like a normal client.
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PyMaster-setup"}


def get(url: str, dest: Path) -> None:
    print("downloading", dest.name, flush=True)
    part = dest.with_name(dest.name + ".part")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r, open(part, "wb") as f:
            shutil.copyfileobj(r, f)
    except (urllib.error.URLError, OSError) as e:
        part.unlink(missing_ok=True)
        raise SystemExit(f"\n  Could not download {dest.name}: {e}\n  Check your internet connection and run start_app.bat again.")
    part.replace(dest)                                          # never leave a half-downloaded file under the real name


def main() -> None:
    LIB.mkdir(parents=True, exist_ok=True)
    for name, path in JARS.items():
        if not (LIB / name).is_file():
            get(MAVEN + path, LIB / name)
    if "--jdk" in sys.argv:
        tools = ROOT / ".tools"
        if not (tools / "jdk21" / "bin" / "javac.exe").is_file():
            tools.mkdir(exist_ok=True)
            for old in (tools / "_x", tools / "jdk21"):          # leftovers of an interrupted attempt
                shutil.rmtree(old, ignore_errors=True)
            z = tools / "jdk21.zip"
            get(JDK_URL, z)
            print("unpacking the JDK (about a minute) ...", flush=True)
            with zipfile.ZipFile(z) as zf:
                zf.extractall(tools / "_x")
            inner = next((tools / "_x").iterdir())
            inner.rename(tools / "jdk21")
            shutil.rmtree(tools / "_x")
            z.unlink()
    print("done:", ", ".join(p.name for p in LIB.glob("*.jar")))


if __name__ == "__main__":
    main()
