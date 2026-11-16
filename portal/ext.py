"""Extension loader. Features live in their own files and plug in without editing main.py / app.js.

Backend: any ``portal/ex_<name>.py`` is imported at start-up. It may define
    router    a fastapi.APIRouter, mounted as-is (use paths like "/api/<name>/...")
    setup()   called once after the database exists (create your tables here with db.run("CREATE TABLE IF NOT EXISTS ..."))
Frontend: any ``portal/static/js/extras/<name>.js`` is imported by app.js after the first route. It may export
    init(ctx)  ctx = { api, $, $$, esc, md, enhance, toast, modal, store, TRK, S, hooks, layout, tutor, track }
and can listen to document events:
    pm:route         detail {hash, area, dayNo}            a view was (re)rendered
    pm:dayrendered   detail {dayNo, tab, root}             the lesson/practice/quiz shell of a day was painted
    pm:runresult     detail {kind, dayNo, result, code}    a Run finished (practice / examples / playground)
Any portal/static/css/extras/<name>.css is linked automatically. Topbar widgets go into the element with id ``topbar-extras``.
A broken extension must never stop the portal: errors are logged and the module is skipped.
"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path

log = logging.getLogger("portal.ext")
HERE = Path(__file__).resolve().parent
EXTRAS_JS = HERE / "static" / "js" / "extras"
EXTRAS_CSS = HERE / "static" / "css" / "extras"
_mods: list = []
_loaded = False


def modules() -> list:
    global _loaded
    if not _loaded:
        _loaded = True
        for p in sorted(HERE.glob("ex_*.py")):
            try:
                _mods.append(importlib.import_module(f"portal.{p.stem}"))
            except Exception:  # noqa: BLE001
                log.exception("extension %s failed to import; skipped", p.stem)
    return _mods


def mount(app) -> None:
    for m in modules():
        r = getattr(m, "router", None)
        if r is not None:
            app.include_router(r)


def setup() -> None:
    for m in modules():
        fn = getattr(m, "setup", None)
        if callable(fn):
            try:
                fn()
            except Exception:  # noqa: BLE001
                log.exception("extension %s setup failed", m.__name__)


def js_files() -> list[str]:
    return sorted(p.name for p in EXTRAS_JS.glob("*.js")) if EXTRAS_JS.is_dir() else []


def css_files() -> list[str]:
    return sorted(p.name for p in EXTRAS_CSS.glob("*.css")) if EXTRAS_CSS.is_dir() else []
