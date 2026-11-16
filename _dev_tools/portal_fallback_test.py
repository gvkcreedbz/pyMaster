"""Provider fallback test: bogus keys must never break the tutor. Run: python _dev_tools/portal_fallback_test.py"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["PORTAL_DATA"] = tempfile.mkdtemp(prefix="portal_fb_")
from fastapi.testclient import TestClient  # noqa: E402

from portal import main  # noqa: E402

H = {"x-portal": "1"}
with TestClient(main.app, base_url="http://127.0.0.1:8765") as c:
    sid = c.post("/api/session/start", headers=H).json()["session_id"]
    c.post("/api/settings", headers=H, json={"values": {"key_cursor": "bogus-key", "key_anthropic": "bogus", "key_openai": "bogus"}})
    st = c.get("/api/settings").json()
    print("active provider:", st["active"], {k: v["configured"] for k, v in st["providers"].items()})
    t = time.time()
    r = c.post("/api/chat", headers=H, json={"session_id": sid, "text": "where is a dict used in real life?", "ctx": {"day_no": 10, "tab": "learn"}})
    evs = [json.loads(x) for x in r.text.splitlines() if x.strip()]
    notes = [e["x"] for e in evs if e["t"] == "note"]
    prov = [e["provider"] for e in evs if e["t"] == "meta"]
    ans = "".join(e["x"] for e in evs if e["t"] == "delta")
    print(f"took {time.time()-t:.1f}s")
    print("providers tried:", prov)
    for n in notes:
        print("note:", n[:160])
    print("answer starts:", ans[:80].replace("\n", " "))
    ok = prov[-1] == "offline" and "Dictionaries" in ans and len(notes) >= 1
    print("FALLBACK OK" if ok else "FALLBACK PROBLEM")
    sys.exit(0 if ok else 1)
