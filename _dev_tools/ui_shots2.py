"""Screenshots of the Blueprints / palette / review / narrow-screen UI via headless Chrome.
usage: python _dev_tools/ui_shots2.py [base_url] [out_dir]      (needs: pip install websockets)
"""
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import websockets

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else Path(tempfile.gettempdir()) / "shots2")
OUT.mkdir(parents=True, exist_ok=True)
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
PORT = 9355


class Page:
    def __init__(self, ws):
        self.ws, self.n, self.pending = ws, 0, {}

    async def pump(self):
        async for m in self.ws:
            d = json.loads(m)
            if "id" in d and d["id"] in self.pending:
                self.pending.pop(d["id"]).set_result(d)

    async def send(self, method, **params):
        self.n += 1
        fut = asyncio.get_event_loop().create_future()
        self.pending[self.n] = fut
        await self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        r = await fut
        if "error" in r:
            raise RuntimeError(f"{method}: {r['error']}")
        return r["result"]

    async def eval(self, js):
        r = await self.send("Runtime.evaluate", expression=js, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r:
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:500])
        return r["result"].get("value")

    async def shot(self, name):
        r = await self.send("Page.captureScreenshot", format="png")
        (OUT / f"{name}.png").write_bytes(base64.b64decode(r["data"]))
        print("shot", name)


async def main():
    prof = tempfile.mkdtemp(prefix="pm_shots2_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                             "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json")) if t["type"] == "page")
                break
            except Exception:  # noqa: BLE001
                await asyncio.sleep(0.5)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            p = Page(ws)
            asyncio.create_task(p.pump())
            await p.send("Page.enable")

            async def size(w, h, mobile=False):
                await p.send("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobile)

            async def go(hash_, wait=2.5):
                await p.send("Page.navigate", url=BASE + "/")
                await asyncio.sleep(1.2)
                await p.eval(f"location.hash={json.dumps(hash_)}")
                await asyncio.sleep(min(wait, 1.0))
                for _ in range(60):                  # until the view has content and every diagram is drawn
                    ready = await p.eval("""(()=>{const v=document.querySelector('#view'); if(!v||v.innerText.trim().length<20) return false;
                        const m=document.querySelectorAll('#view .mmd').length; return document.querySelectorAll('#view .mmd .mmd-svg svg').length>=m})()""")
                    if ready:
                        break
                    await asyncio.sleep(0.25)
                await asyncio.sleep(0.4)

            await size(1440, 900)
            await p.send("Page.navigate", url=BASE + "/")
            await asyncio.sleep(1.0)
            await p.eval("localStorage.setItem('pj-theme','light'); localStorage.removeItem('pm-layout')")
            await go("#/blueprints")
            await p.shot("10_blueprints_overview")
            await go("#/blueprints/live-order-tracker", 4.5)
            await p.eval("document.querySelector('#main').scrollTop = 520")
            await asyncio.sleep(0.6)
            await p.shot("11_blueprint_guide_diagram")
            await go("#/blueprints/site-watcher", 4.5)
            await p.eval("document.querySelectorAll('#main .mmd')[1].scrollIntoView({block:'center'})")
            await asyncio.sleep(0.6)
            await p.shot("12_breaker_state_diagram")
            await go("#/blueprints/ticket-triage-pipeline/run", 1.0)
            await p.eval("document.querySelector('#bp-run').click()")
            await asyncio.sleep(4.0)
            await p.shot("13_run_demo")
            await go("#/blueprints/patterns", 1.5)
            await p.shot("14_patterns")
            await go("#/", 1.5)
            await p.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'p',ctrlKey:true,bubbles:true}))")
            await asyncio.sleep(0.4)
            await p.eval("(()=>{const i=document.querySelector('#palette input');i.value='retry backoff';i.dispatchEvent(new Event('input',{bubbles:true}))})()")
            await asyncio.sleep(1.2)
            await p.shot("15_palette_search")
            await p.eval("document.querySelector('#palette input').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
            await size(420, 860, mobile=True)
            await go("#/", 1.5)
            await p.shot("16_narrow_home")
            await go("#/blueprints/live-order-tracker", 3.5)
            await p.shot("17_narrow_blueprint")
            await size(1440, 900)
            await p.eval("localStorage.setItem('pj-theme','dark')")
            await go("#/blueprints/ticket-triage-pipeline", 4.5)
            await p.eval("document.querySelector('#main').scrollTop = 480")
            await asyncio.sleep(0.6)
            await p.shot("18_dark_triage")
            print("done ->", OUT)
    finally:
        proc.terminate()


asyncio.run(main())
