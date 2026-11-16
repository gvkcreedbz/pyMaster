"""Start the Py Master portal:  python portal/run.py   (opens your browser)."""
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn  # noqa: E402

HOST, PORT = "127.0.0.1", int(os.environ.get("PORTAL_PORT", "8765"))


def _open() -> None:
    time.sleep(1.2)
    webbrowser.open(f"http://{HOST}:{PORT}/")


if __name__ == "__main__":
    print(f"\n  Py Master portal -> http://{HOST}:{PORT}/   (Ctrl+C to stop)\n")
    if "--no-browser" not in sys.argv:
        threading.Thread(target=_open, daemon=True).start()
    uvicorn.run("portal.main:app", host=HOST, port=PORT, log_level="warning")
