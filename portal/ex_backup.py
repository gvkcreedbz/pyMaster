"""Safe backups of the learner's progress database (extension "backup").

Never copies the live file: it uses SQLite's online backup API (``Connection.backup``), so a backup taken while
the portal is writing is still a consistent snapshot. Files live in ``<data dir>/backups`` (the data dir is
``PORTAL_DATA`` or ``portal/data`` / ``portal/data-java``, exactly as in ``db.py``):

    progress-YYYYMMDD-HHMMSS.db                a normal backup (automatic daily, or "Back up now")
    progress-YYYYMMDD-HHMMSS-pre-restore.db    safety copy made right before a restore

Retention: the newest backup of each of the 14 most recent days, plus the newest backup of each of the 4 most
recent older weeks. At least 3 backups are always kept. The 3 newest pre-restore copies are kept as well.

Endpoints:  GET /api/backup/list   POST /api/backup/now   POST /api/backup/auto
            POST /api/backup/restore {name, confirm: true}   GET /api/backup/download/{name}
"""
from __future__ import annotations

import logging
import os
import re
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import db

log = logging.getLogger("portal.backup")
router = APIRouter()

KEEP_DAILY, KEEP_WEEKLY, MIN_KEEP, KEEP_PRE = 14, 4, 3, 3
NAME_RE = re.compile(r"^progress-(\d{8})-(\d{6})(-pre-restore)?\.db$")
CHECK_EVERY = 15 * 60          # the background check wakes up this often (seconds)
_lock = threading.RLock()
_thread: threading.Thread | None = None
_stop = threading.Event()


# ---- paths and names ----------------------------------------------------------------------------
def backup_dir() -> Path:
    return Path(db.DATA_DIR) / "backups"


def parse_name(name: str) -> datetime | None:
    """The timestamp encoded in a valid backup name, or None if the name is not one of ours."""
    m = NAME_RE.match(name or "")
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    except ValueError:
        return None


def safe_path(name: str) -> Path:
    """Validated path of an existing backup. Raises ValueError for bad names, FileNotFoundError if missing."""
    if not isinstance(name, str) or len(name) > 64 or parse_name(name) is None:
        raise ValueError("not a valid backup name")
    root = backup_dir().resolve()
    p = (root / name).resolve()
    if p.parent != root:
        raise ValueError("not a valid backup name")
    if not p.is_file():
        raise FileNotFoundError(name)
    return p


def _entries() -> list[dict]:
    d = backup_dir()
    out = []
    if d.is_dir():
        for p in d.iterdir():
            t = parse_name(p.name)
            if t and p.is_file():
                out.append({"name": p.name, "time": t, "pre": p.name.endswith("-pre-restore.db"), "path": p})
    out.sort(key=lambda e: e["name"], reverse=True)       # names sort like their timestamps
    return out


# ---- create ---------------------------------------------------------------------------------------
def create_backup(kind: str = "manual", now: datetime | None = None, protect: tuple = ()) -> dict:
    """Snapshot the live database with the online backup API. kind: 'manual' | 'auto' | 'pre-restore'."""
    if not Path(db.DB_PATH).is_file():
        raise FileNotFoundError("there is no progress database yet")
    with _lock:
        d = backup_dir()
        d.mkdir(parents=True, exist_ok=True)
        t = (now or datetime.now()).replace(microsecond=0)
        suffix = "-pre-restore" if kind == "pre-restore" else ""
        while (d / f"progress-{t:%Y%m%d-%H%M%S}{suffix}.db").exists():
            t += timedelta(seconds=1)                       # two backups in the same second: take the next free one
        final = d / f"progress-{t:%Y%m%d-%H%M%S}{suffix}.db"
        tmp = d / (final.name + ".part")
        src = sqlite3.connect(db.DB_PATH, timeout=30)
        dst = sqlite3.connect(tmp)
        try:
            src.backup(dst)
            dst.execute("PRAGMA journal_mode=DELETE")       # one self-contained file, no -wal/-shm companions
            dst.commit()
        except Exception:
            dst.close()
            src.close()
            tmp.unlink(missing_ok=True)
            raise
        dst.close()
        src.close()
        os.replace(tmp, final)
        pruned = prune(keep_names={final.name, *protect})
        return {"name": final.name, "size": final.stat().st_size, "kind": kind, "pruned": pruned}


# ---- retention ------------------------------------------------------------------------------------
def plan_keep(entries: list[dict]) -> set[str]:
    """Names that survive pruning (entries are normal backups, newest first)."""
    keep: set[str] = set()
    days: dict = {}
    for e in entries:                                       # newest first: first hit per day is that day's newest
        days.setdefault(e["time"].date(), e["name"])
    recent = sorted(days, reverse=True)[:KEEP_DAILY]
    keep.update(days[d] for d in recent)
    older = [e for e in entries if e["time"].date() not in recent]
    weeks: dict = {}
    for e in older:
        weeks.setdefault(tuple(e["time"].isocalendar()[:2]), e["name"])
    for w in sorted(weeks, reverse=True)[:KEEP_WEEKLY]:
        keep.add(weeks[w])
    for e in entries:                                       # never fall below MIN_KEEP
        if len(keep) >= MIN_KEEP:
            break
        keep.add(e["name"])
    return keep


def prune(keep_names: set[str] | None = None) -> list[str]:
    """Delete backups outside the retention plan. Returns the deleted names."""
    removed = []
    with _lock:
        all_ = _entries()
        normal = [e for e in all_ if not e["pre"]]
        pre = [e for e in all_ if e["pre"]]
        keep = plan_keep(normal) | {e["name"] for e in pre[:KEEP_PRE]} | (keep_names or set())
        for e in all_:
            if e["name"] not in keep:
                try:
                    e["path"].unlink()
                    removed.append(e["name"])
                except OSError:
                    log.warning("could not delete old backup %s", e["name"])
        for p in backup_dir().glob("*.part"):               # leftovers of an interrupted backup
            try:
                p.unlink()
            except OSError:
                pass
    return removed


def ensure_daily(now: datetime | None = None) -> dict | None:
    """Make today's automatic backup unless a normal backup from today already exists."""
    today = (now or datetime.now()).date()
    with _lock:
        if any(e["time"].date() == today and not e["pre"] for e in _entries()):
            return None
        if not Path(db.DB_PATH).is_file():
            return None
        return create_backup("auto", now)


# ---- verify and restore ------------------------------------------------------------------------------
def expected_tables() -> set[str]:
    return set(re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)", db.SCHEMA))


def validate_file(path: Path) -> None:
    """Raise ValueError unless the file is a healthy progress database."""
    try:
        con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True, timeout=10)
    except sqlite3.Error as e:
        raise ValueError(f"cannot open the backup: {e}") from None
    try:
        res = [r[0] for r in con.execute("PRAGMA integrity_check").fetchall()]
        if res != ["ok"]:
            raise ValueError("the backup failed the integrity check: " + "; ".join(map(str, res[:3])))
        have = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing = sorted(expected_tables() - have)
        if missing:
            raise ValueError("the backup is not a progress database (missing tables: " + ", ".join(missing) + ")")
    except sqlite3.Error as e:
        raise ValueError(f"the backup is damaged: {e}") from None
    finally:
        con.close()


def restore(name: str) -> dict:
    """Replace the live data with a backup (after a safety backup), while the server keeps running."""
    path = safe_path(name)
    validate_file(path)                                     # refuse before touching anything
    with _lock:
        safety = create_backup("pre-restore", protect=(name,)) if Path(db.DB_PATH).is_file() else None
        with db._lock:                                      # no other request touches the db during the swap
            src = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True, timeout=30)
            dst = sqlite3.connect(db.DB_PATH, timeout=30)
            try:
                src.backup(dst)                             # reverse direction: the backup is the source
                dst.commit()
            finally:
                dst.close()
                src.close()
        db.init()                                           # WAL mode again + any table the backup predates
        try:
            from . import ext
            ext.setup()                                     # other extensions recreate their (empty) tables
        except Exception:  # noqa: BLE001
            log.exception("extension setup after restore failed")
    return {"restored": name, "safety_backup": safety["name"] if safety else None}


# ---- background daily check ------------------------------------------------------------------------------
def _loop() -> None:
    while not _stop.is_set():
        try:
            ensure_daily()
        except Exception:  # noqa: BLE001
            log.exception("daily backup failed")
        _stop.wait(CHECK_EVERY)


def setup() -> None:
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, name="backup-daily", daemon=True)
    _thread.start()


# ---- API ------------------------------------------------------------------------------------------------
def _describe(e: dict) -> dict:
    return {"name": e["name"], "created": e["time"].isoformat(timespec="seconds"), "size": e["path"].stat().st_size,
            "kind": "pre-restore" if e["pre"] else "backup"}


@router.get("/api/backup/list")
def api_list():
    items = []
    for e in _entries():
        try:
            items.append(_describe(e))
        except OSError:
            continue                                        # deleted between listing and stat
    today = datetime.now().date()
    return {"items": items, "dir": str(backup_dir()),
            "today_done": any(e["time"].date() == today and not e["pre"] for e in _entries()),
            "policy": {"daily": KEEP_DAILY, "weekly": KEEP_WEEKLY, "min": MIN_KEEP}}


@router.post("/api/backup/now")
def api_now():
    try:
        r = create_backup("manual")
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from None
    except (sqlite3.Error, OSError) as e:
        raise HTTPException(500, f"backup failed: {e}") from None
    db.log_event(None, "backup_made", None, {"name": r["name"], "kind": "manual"})
    return r


@router.post("/api/backup/auto")
def api_auto():
    """Called by the page on load: makes today's backup if it is missing (cheap otherwise)."""
    try:
        r = ensure_daily()
    except (sqlite3.Error, OSError) as e:
        raise HTTPException(500, f"backup failed: {e}") from None
    return {"made": bool(r), "name": r["name"] if r else None}


class RestoreIn(BaseModel):
    name: str
    confirm: bool = False


@router.post("/api/backup/restore")
def api_restore(b: RestoreIn):
    if b.confirm is not True:
        raise HTTPException(400, "restore needs confirm: true")
    try:
        r = restore(b.name)
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    except FileNotFoundError:
        raise HTTPException(404, "no such backup") from None
    except (sqlite3.Error, OSError) as e:
        raise HTTPException(500, f"restore failed: {e}") from None
    db.log_event(None, "backup_restored", None, {"name": b.name})
    return r


@router.get("/api/backup/download/{name}")
def api_download(name: str):
    try:
        p = safe_path(name)
    except ValueError:
        raise HTTPException(400, "not a valid backup name") from None
    except FileNotFoundError:
        raise HTTPException(404, "no such backup") from None
    return FileResponse(p, media_type="application/octet-stream", filename=p.name)
