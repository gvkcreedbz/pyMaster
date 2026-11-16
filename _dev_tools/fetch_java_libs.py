"""Download the optional Java helpers (not committed to git because of their size).

  python _dev_tools/fetch_java_libs.py          -> java/lib/*.jar  (JUnit console, SQLite JDBC, slf4j)
  python _dev_tools/fetch_java_libs.py --jdk    -> also a portable JDK 21 in .tools/jdk21 (no admin rights needed)
"""
import shutil
import sys
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
JDK_URL = "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse"


def get(url: str, dest: Path) -> None:
    print("downloading", dest.name)
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def main() -> None:
    LIB.mkdir(parents=True, exist_ok=True)
    for name, path in JARS.items():
        if not (LIB / name).is_file():
            get(MAVEN + path, LIB / name)
    if "--jdk" in sys.argv:
        tools = ROOT / ".tools"
        if not (tools / "jdk21" / "bin").is_dir():
            tools.mkdir(exist_ok=True)
            z = tools / "jdk21.zip"
            get(JDK_URL, z)
            with zipfile.ZipFile(z) as zf:
                zf.extractall(tools / "_x")
            inner = next((tools / "_x").iterdir())
            inner.rename(tools / "jdk21")
            shutil.rmtree(tools / "_x")
            z.unlink()
    print("done:", ", ".join(p.name for p in LIB.glob("*.jar")))


if __name__ == "__main__":
    main()
