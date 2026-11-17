"""Tests for portal/ex_backup.py (safe SQLite backups) on BOTH tracks.
Run:  python -m pytest _dev_tools/test_ex_backup.py -q -p no:cacheprovider
The file tests the track chosen by PORTAL_TRACK (python by default) and re-runs itself once in a subprocess for the
other track, so a plain pytest run covers both.
"""
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("PORTAL_DATA", tempfile.mkdtemp(prefix="bk_import_"))

from fastapi.testclient import TestClient  # noqa: E402

from portal import db, ex_backup as bk, main, track  # noqa: E402

H = {"x-portal": "1"}


@pytest.fixture()
def env(tmp_path, monkeypatch):
    """A fresh data dir per test, a client WITHOUT lifespan (so no background backup thread interferes)."""
    monkeypatch.setattr(db, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "progress.db")
    db.init()
    c = TestClient(main.app, base_url=f"http://127.0.0.1:{track.T['port']}")
    return c, tmp_path


def seed(n=3):
    for i in range(n):
        db.run("INSERT INTO notes(day_no,text,updated_at) VALUES(?,?,?)", (i + 1, f"note {i + 1}", db.now_iso()))
    db.set_setting("start_date", "2025-01-06")


def notes():
    return [r["text"] for r in db.rows("SELECT text FROM notes ORDER BY day_no")]


def names(tmp):
    return sorted(p.name for p in (tmp / "backups").glob("*.db"))


def test_track_is_the_requested_one():
    assert track.ID == os.environ.get("PORTAL_TRACK", "python")


def test_backup_creates_valid_database(env):
    _, tmp = env
    seed()
    r = bk.create_backup("manual")
    p = tmp / "backups" / r["name"]
    assert bk.NAME_RE.match(r["name"]) and p.is_file() and r["size"] > 0
    con = sqlite3.connect(p)
    try:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert con.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        assert [x[0] for x in con.execute("SELECT text FROM notes ORDER BY day_no")] == ["note 1", "note 2", "note 3"]
        have = {x[0] for x in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert bk.expected_tables() <= have
    finally:
        con.close()
    assert not list((tmp / "backups").glob("*-wal")) and not list((tmp / "backups").glob("*.part"))


def test_backup_is_taken_while_the_db_is_busy(env):
    """A writer connection with an open WAL must not corrupt the snapshot (we never copy the raw file)."""
    _, tmp = env
    seed()
    w = sqlite3.connect(db.DB_PATH)
    w.execute("INSERT INTO notes(day_no,text,updated_at) VALUES(9,'in wal',?)", (db.now_iso(),))
    w.commit()
    r = bk.create_backup("manual")
    w.close()
    con = sqlite3.connect(tmp / "backups" / r["name"])
    assert con.execute("SELECT text FROM notes WHERE day_no=9").fetchone()[0] == "in wal"
    con.close()


def test_api_now_list_download(env):
    c, tmp = env
    seed()
    assert c.post("/api/backup/now").status_code == 403                      # the app-wide x-portal guard
    r = c.post("/api/backup/now", headers=H)
    assert r.status_code == 200, r.text
    name = r.json()["name"]
    lst = c.get("/api/backup/list").json()
    assert [i["name"] for i in lst["items"]] == [name]
    assert lst["items"][0]["kind"] == "backup" and lst["today_done"] is True
    d = c.get(f"/api/backup/download/{name}")
    assert d.status_code == 200 and d.content[:15] == b"SQLite format 3"
    out = tmp / "dl.db"
    out.write_bytes(d.content)
    con = sqlite3.connect(out)
    assert con.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 3
    con.close()


def test_list_is_empty_without_backups(env):
    c, _ = env
    r = c.get("/api/backup/list").json()
    assert r["items"] == [] and r["today_done"] is False


def test_daily_backup_runs_once_per_day(env):
    _, tmp = env
    seed()
    t = datetime(2025, 3, 10, 9, 0, 0)
    first = bk.ensure_daily(t)
    assert first and first["name"] == "progress-20250310-090000.db"
    assert bk.ensure_daily(t + timedelta(hours=5)) is None
    assert bk.ensure_daily(t + timedelta(days=1))["name"].startswith("progress-20250311")
    assert len(names(tmp)) == 2


def test_two_backups_in_one_second_do_not_overwrite(env):
    _, tmp = env
    seed()
    t = datetime(2025, 3, 10, 9, 0, 0)
    a = bk.create_backup("manual", t)["name"]
    b = bk.create_backup("manual", t)["name"]
    assert a != b and len(names(tmp)) == 2


def test_prune_keeps_newest_daily_and_weekly(env):
    _, tmp = env
    seed()
    start = datetime(2025, 1, 1, 8, 0, 0)
    for i in range(60):
        bk.create_backup("auto", start + timedelta(days=i))
    left = names(tmp)
    last_days = [f"progress-{(start + timedelta(days=i)):%Y%m%d}-080000.db" for i in range(60 - 14, 60)]
    assert all(n in left for n in last_days), "the 14 newest daily backups must survive"
    older = [n for n in left if n not in last_days]
    assert len(older) == bk.KEEP_WEEKLY and len(left) == 14 + 4
    weeks = {datetime.strptime(n[9:17], "%Y%m%d").isocalendar()[:2] for n in older}
    assert len(weeks) == 4, "one backup per week"
    assert max(n for n in older) < min(last_days)
    assert (tmp / "backups" / left[-1]).is_file() and left[-1] == last_days[-1]


def test_prune_never_goes_below_three():
    mk = lambda s: {"name": s, "time": datetime.strptime(s[9:24], "%Y%m%d-%H%M%S"), "pre": False}  # noqa: E731
    same_day = [mk(f"progress-20250310-{h}0000.db") for h in (23, 22, 21, 20, 19)]
    keep = bk.plan_keep(same_day)
    assert len(keep) == 3 and "progress-20250310-230000.db" in keep           # newest first
    assert bk.plan_keep(same_day[:2]) == {e["name"] for e in same_day[:2]}
    assert bk.plan_keep([]) == set()


def test_only_the_newest_pre_restore_copies_are_kept(env):
    _, tmp = env
    seed()
    t = datetime(2025, 5, 1, 12, 0, 0)
    for i in range(6):
        bk.create_backup("pre-restore", t + timedelta(minutes=i))
    pre = [n for n in names(tmp) if n.endswith("-pre-restore.db")]
    assert len(pre) == bk.KEEP_PRE and pre[-1] == "progress-20250501-120500-pre-restore.db"


def test_restore_round_trip_brings_back_deleted_rows(env):
    c, tmp = env
    seed()
    name = c.post("/api/backup/now", headers=H).json()["name"]
    db.run("DELETE FROM notes")
    db.run("INSERT INTO notes(day_no,text,updated_at) VALUES(20,'written after the backup',?)", (db.now_iso(),))
    assert notes() == ["written after the backup"]
    r = c.post("/api/backup/restore", headers=H, json={"name": name, "confirm": True})
    assert r.status_code == 200, r.text
    assert notes() == ["note 1", "note 2", "note 3"]
    assert db.get_setting("start_date") == "2025-01-06"
    safety = r.json()["safety_backup"]
    assert safety.endswith("-pre-restore.db")                                  # state before the restore is kept
    con = sqlite3.connect(tmp / "backups" / safety)
    assert [x[0] for x in con.execute("SELECT text FROM notes")] == ["written after the backup"]
    con.close()
    db.run("INSERT INTO notes(day_no,text,updated_at) VALUES(21,'still writable',?)", (db.now_iso(),))   # server keeps working
    assert "still writable" in notes()
    with db.conn() as k:
        assert k.execute("PRAGMA journal_mode").fetchone()[0] == "wal"


def test_restore_needs_confirmation(env):
    c, _ = env
    seed()
    name = c.post("/api/backup/now", headers=H).json()["name"]
    db.run("DELETE FROM notes")
    for body in ({"name": name}, {"name": name, "confirm": False}):
        assert c.post("/api/backup/restore", headers=H, json=body).status_code == 400
    assert notes() == []                                                       # nothing was touched


@pytest.mark.parametrize("bad", [
    "../progress-20250101-000000.db", "..\\progress-20250101-000000.db", "progress-20250101-000000.db/../../x",
    "/etc/passwd", "C:\\Windows\\win.ini", "progress.db", "progress-2025.db", "progress-20250101-000000.db.part",
    "progress-20251301-000000.db", "PROGRESS-20250101-000000.db", "progress-20250101-000000.db\x00", "", " ",
    "progress-20250101-000000-evil.db", "x" * 300,
])
def test_bad_names_are_rejected(env, bad):
    c, _ = env
    seed()
    c.post("/api/backup/now", headers=H)
    r = c.post("/api/backup/restore", headers=H, json={"name": bad, "confirm": True})
    assert r.status_code == 400, (bad, r.status_code, r.text)
    with pytest.raises(ValueError):
        bk.safe_path(bad)


def test_unknown_but_wellformed_name_is_404(env):
    c, _ = env
    r = c.post("/api/backup/restore", headers=H, json={"name": "progress-20200101-000000.db", "confirm": True})
    assert r.status_code == 404
    assert c.get("/api/backup/download/progress-20200101-000000.db").status_code == 404


def test_download_rejects_traversal(env):
    c, tmp = env
    seed()
    (tmp / "secret.txt").write_text("nope")
    for bad in ("..%2Fsecret.txt", "..%5Csecret.txt", "secret.txt", "progress.db", "%2e%2e%2fprogress.db"):
        r = c.get(f"/api/backup/download/{bad}")
        assert r.status_code in (400, 404) and b"nope" not in r.content, (bad, r.status_code)


def test_corrupt_file_is_refused_and_nothing_changes(env):
    c, tmp = env
    seed()
    d = tmp / "backups"
    d.mkdir()
    (d / "progress-20250101-000000.db").write_bytes(b"this is definitely not a database" * 50)
    r = c.post("/api/backup/restore", headers=H, json={"name": "progress-20250101-000000.db", "confirm": True})
    assert r.status_code == 400
    assert notes() == ["note 1", "note 2", "note 3"]
    assert not [n for n in names(tmp) if "pre-restore" in n], "validation happens before the safety backup"


def test_damaged_pages_fail_the_integrity_check(env):
    c, tmp = env
    for i in range(400):                                                       # enough rows for several pages
        db.run("INSERT INTO events(ts,date,session_id,type,day_no,payload) VALUES(?,?,?,?,?,?)",
               (db.now_iso(), db.today(), "s", "x", 1, "{\"k\": \"" + "v" * 200 + "\"}"))
    name = bk.create_backup("manual")["name"]
    p = tmp / "backups" / name
    raw = bytearray(p.read_bytes())
    assert len(raw) > 4096 * 6
    for i in range(4096 * 3, 4096 * 5):                                        # wreck two data pages
        raw[i] = 0xFF
    p.write_bytes(bytes(raw))
    before = db.rows("SELECT COUNT(*) c FROM events")[0]["c"]
    r = c.post("/api/backup/restore", headers=H, json={"name": name, "confirm": True})
    assert r.status_code == 400, r.text
    assert db.rows("SELECT COUNT(*) c FROM events")[0]["c"] == before


def test_valid_sqlite_without_our_tables_is_refused(env):
    c, tmp = env
    seed()
    d = tmp / "backups"
    d.mkdir()
    con = sqlite3.connect(d / "progress-20250102-000000.db")
    con.execute("CREATE TABLE other(x)")
    con.commit()
    con.close()
    r = c.post("/api/backup/restore", headers=H, json={"name": "progress-20250102-000000.db", "confirm": True})
    assert r.status_code == 400 and "missing tables" in r.text
    assert notes() == ["note 1", "note 2", "note 3"]


def test_backup_without_database_is_a_clear_404(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "progress.db")
    c = TestClient(main.app, base_url=f"http://127.0.0.1:{track.T['port']}")
    assert c.post("/api/backup/now", headers=H).status_code == 404
    assert bk.ensure_daily() is None


def test_setup_starts_one_daemon_thread(env, monkeypatch):
    monkeypatch.setattr(bk, "CHECK_EVERY", 0.05)
    bk._stop.set()
    bk._thread = None
    seed()
    bk.setup()
    t = bk._thread
    bk.setup()
    assert bk._thread is t and t.daemon
    t.join(0.5)
    bk._stop.set()
    t.join(2)
    assert any(not n.endswith("-pre-restore.db") for n in names(env[1]))


# ---- run the same file for the other track in a child process ---------------------------------------------
@pytest.mark.skipif(os.environ.get("BK_CHILD") == "1", reason="already the child run")
def test_other_track_in_subprocess():
    other = "java" if track.ID == "python" else "python"
    envv = {**os.environ, "PORTAL_TRACK": other, "BK_CHILD": "1", "PYTHONUTF8": "1", "PORTAL_DATA": tempfile.mkdtemp(prefix="bk_child_")}
    r = subprocess.run([sys.executable, "-W", "ignore", "-m", "pytest", str(Path(__file__)), "-q", "-p", "no:cacheprovider", "-x"],
                       env=envv, capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-2500:] + r.stderr[-1500:]
