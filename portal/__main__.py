"""Command line entry points.

    python -m portal                    Py Master   (Python course)  http://127.0.0.1:8765/
    python -m portal --track java       Java Master (Java course)    http://127.0.0.1:8766/
    pymaster / javamaster               the same, as commands after `pip install -e .`

Options: --track python|java   --port N   --no-browser
The old way (python portal/run.py [--track java] [--no-browser]) keeps working too.
"""
from __future__ import annotations

import argparse
import os
import sys


def _parse(default_track: str | None, argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="javamaster" if default_track == "java" else "pymaster" if default_track == "python" else "python -m portal",
        description="Start the learning portal (local only, 127.0.0.1).")
    if default_track is None:
        ap.add_argument("--track", choices=("python", "java"), default="python", help="which course to serve (default: python)")
    ap.add_argument("--port", type=int, help="port to listen on (default: 8765 for Python, 8766 for Java)")
    ap.add_argument("--no-browser", action="store_true", help="do not open the browser")
    ns = ap.parse_args(argv)
    if default_track is not None:
        ns.track = default_track
    return ns


def main(default_track: str | None = None, argv: list[str] | None = None) -> None:
    ns = _parse(default_track, argv)
    os.environ["PORTAL_TRACK"] = ns.track                  # must be set before the portal modules are imported
    if ns.port:
        if not 1 <= ns.port <= 65535:
            sys.exit("--port must be between 1 and 65535")
        os.environ["PORTAL_PORT"] = str(ns.port)
    sys.argv = [sys.argv[0]] + (["--no-browser"] if ns.no_browser else [])
    from portal import run
    run.main()


def main_python() -> None:
    main("python")


def main_java() -> None:
    main("java")


if __name__ == "__main__":
    main()
