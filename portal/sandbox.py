"""Safer process runner for learner code.

This is *damage limitation for accidents* (a runaway loop that eats memory, a fork bomb, a leftover child), not a
security boundary against a determined attacker: the portal only listens on 127.0.0.1 and runs your own code.

* Windows: the child is put in a Job Object with a memory cap, a process-count cap and KILL_ON_JOB_CLOSE, so when the
  run ends (or times out) every process it started dies with it.
* Linux/macOS: the child gets rlimits (CPU seconds, file size, core dumps off) and its own process group, which is
  killed as a whole on timeout.
Both degrade silently to a plain subprocess if the OS refuses (nothing here may ever stop a run from working).
"""
from __future__ import annotations

import os
import subprocess

MEM_LIMIT_MB = int(os.environ.get("PORTAL_RUN_MEM_MB", "2048"))
MAX_PROCS = int(os.environ.get("PORTAL_RUN_MAX_PROCS", "12"))
IS_WIN = os.name == "nt"

if IS_WIN:
    import ctypes
    from ctypes import wintypes

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [(n, ctypes.c_ulonglong) for n in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class _BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class _EXTENDED(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", _BASIC), ("IoInfo", _IO_COUNTERS),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    _ACTIVE_PROCESS, _JOB_MEMORY, _KILL_ON_CLOSE = 0x8, 0x200, 0x2000
    _k32.CreateJobObjectW.restype = wintypes.HANDLE
    _k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    _k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    _k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]

    def _make_job() -> int | None:
        try:
            job = _k32.CreateJobObjectW(None, None)
            if not job:
                return None
            info = _EXTENDED()
            info.BasicLimitInformation.LimitFlags = _ACTIVE_PROCESS | _JOB_MEMORY | _KILL_ON_CLOSE
            info.BasicLimitInformation.ActiveProcessLimit = MAX_PROCS
            info.JobMemoryLimit = MEM_LIMIT_MB * 1024 * 1024
            if not _k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
                _k32.CloseHandle(job)
                return None
            return job
        except Exception:  # noqa: BLE001
            return None

    def _attach(job: int | None, proc: subprocess.Popen) -> bool:
        if not job:
            return False
        try:
            return bool(_k32.AssignProcessToJobObject(job, int(proc._handle)))   # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            return False

    def _close(job: int | None) -> None:
        if job:
            _k32.CloseHandle(job)          # KILL_ON_JOB_CLOSE: everything still alive in the job dies here
else:
    import resource
    import signal

    def _preexec() -> None:                # pragma: no cover - not exercised on Windows
        os.setsid()
        for lim, val in ((resource.RLIMIT_CPU, (120, 120)), (resource.RLIMIT_FSIZE, (64 << 20, 64 << 20)),
                         (resource.RLIMIT_CORE, (0, 0))):
            try:
                resource.setrlimit(lim, val)
            except (ValueError, OSError):
                pass


def run(cmd: list[str], *, cwd: str, stdin: str = "", timeout: int = 25, env: dict | None = None) -> tuple[str, int, bool]:
    """Run ``cmd`` with limits. Returns (stdout + stderr text, returncode, timed_out)."""
    kw: dict = {}
    if not IS_WIN:
        kw["preexec_fn"] = _preexec
    p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", errors="replace", env=env, **kw)
    job = _make_job() if IS_WIN else None
    if IS_WIN:
        _attach(job, p)
    timed_out = False
    try:
        try:
            out, err = p.communicate(stdin, timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill(p)
            out, err = p.communicate()
    finally:
        if IS_WIN:
            _close(job)
    text = (out or "") + (("\n" + err) if err else "")
    return text, (-1 if timed_out else p.returncode), timed_out


def _kill(p: subprocess.Popen) -> None:
    try:
        if IS_WIN:
            p.kill()
        else:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except Exception:  # noqa: BLE001
        try:
            p.kill()
        except Exception:  # noqa: BLE001
            pass
