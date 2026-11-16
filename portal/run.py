"""Start the portal:  python portal/run.py [--track java] [--no-browser]   (opens your browser).

Python track (Py Master) -> http://127.0.0.1:8765/     Java track (Java Master) -> http://127.0.0.1:8766/
Both can run side by side: each has its own progress database.
"""
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if "--track" in sys.argv:                       # must be decided before the portal modules are imported
    i = sys.argv.index("--track")
    os.environ["PORTAL_TRACK"] = sys.argv[i + 1] if i + 1 < len(sys.argv) else "python"

import uvicorn  # noqa: E402

from portal import track  # noqa: E402

HOST, PORT = "127.0.0.1", int(os.environ.get("PORTAL_PORT", str(track.T["port"])))


def _open() -> None:
    time.sleep(1.2)
    webbrowser.open(f"http://{HOST}:{PORT}/")


def main() -> None:
    print(f"\n  {track.T['name']} portal -> http://{HOST}:{PORT}/   (Ctrl+C to stop)\n")
    if "--no-browser" not in sys.argv:
        threading.Thread(target=_open, daemon=True).start()
    uvicorn.run("portal.main:app", host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
