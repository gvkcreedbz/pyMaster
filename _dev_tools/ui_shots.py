"""Drive headless Chrome over CDP against a running test portal and save screenshots of key UI states.

usage: python _dev_tools/ui_shots.py [base_url] [out_dir]        (needs: pip install websockets)
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
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else Path(tempfile.gettempdir()) / "shots")
OUT.mkdir(parents=True, exist_ok=True)
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
PORT = 9333


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
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:600])
        return r["result"].get("value")

    async def shot(self, name):
        r = await self.send("Page.captureScreenshot", format="png")
        (OUT / f"{name}.png").write_bytes(base64.b64decode(r["data"]))
        print("shot", name)

    async def ready(self, js="!!document.querySelector('#btn-menu') && !!document.querySelector('#view .fade-in')", timeout=20):
        for _ in range(int(timeout * 5)):
            try:
                if await self.eval(js):
                    return
            except Exception:  # noqa: BLE001
                pass
            await asyncio.sleep(0.2)
        raise RuntimeError("timeout waiting for " + js)

    async def sleep(self, s):
        await asyncio.sleep(s)


async def main():
    prof = tempfile.mkdtemp(prefix="pm_chrome_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                             "--window-size=1440,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                page = next(t for t in tabs if t["type"] == "page")
                break
            except Exception:  # noqa: BLE001
                await asyncio.sleep(0.5)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            p = Page(ws)
            asyncio.create_task(p.pump())
            await p.send("Emulation.setDeviceMetricsOverride", width=1440, height=900, deviceScaleFactor=1, mobile=False)
            await p.send("Page.enable")
            await p.send("Runtime.enable")

            async def go(url, wait=0.8):
                await p.send("Page.navigate", url=url)
                await p.sleep(0.4)
                await p.ready()
                await p.sleep(wait)

            await go(BASE + "/")
            await p.eval("localStorage.setItem('pj-theme','light'); localStorage.removeItem('pm-layout'); localStorage.removeItem('pm-play-code')")
            await go(BASE + "/#/day/1/learn")
            await p.eval("location.reload()"); await p.sleep(0.4); await p.ready(); await p.sleep(0.8)
            await p.shot("01_day1_light")

            await p.eval("document.querySelector('#btn-menu').click()"); await p.sleep(0.6)
            await p.shot("02_drawer")
            await p.eval("document.querySelector('#scrim').click()"); await p.sleep(0.4)

            # code in playground + assistant visual
            await p.eval("""(()=>{const cm=document.querySelector('#pg .CodeMirror').CodeMirror;
              cm.setValue('prices = [10, 250, 40, 900]\\ntotal = 0\\nfor p in prices:\\n    if p > 100:\\n        total += p * 0.9\\nprint(total)\\n'); cm.focus();})()""")
            await p.eval("document.querySelector('#askbar').click()"); await p.sleep(0.6)
            await p.eval("document.querySelector('#quick [data-q=visual]').click()"); await p.sleep(4.5)
            await p.shot("03_assistant_visual")

            # visualizer: aliasing + function frame
            await p.eval("""(()=>{document.querySelector('#pane-tutor [data-act=toggle]').click();
              const cm=document.querySelector('#pg .CodeMirror').CodeMirror;
              cm.setValue('a = [1, 2, 3]\\nb = a\\nb.append(4)\\n\\ndef double(n):\\n    return n * 2\\n\\nresult = double(len(a))\\nprint(a, result)\\n');
              [...document.querySelectorAll('#pg .btn')].find(b=>b.textContent.includes('Visualize')).click();})()""")
            await p.sleep(2.5)
            await p.eval("(async()=>{for(let i=0;i<5;i++){document.querySelector('.vz-ctl [data-c=next]').click(); await new Promise(r=>setTimeout(r,80));}})()")
            await p.sleep(0.6)
            await p.shot("04_visualizer_step")
            await p.eval("document.querySelector('#vz-tabs [data-t=flow]').click()"); await p.sleep(2.0)
            await p.shot("05_visualizer_flow")
            await p.eval("document.querySelector('.modal.xl [data-x]').click()"); await p.sleep(0.4)

            # Try from a lesson block lands in the playground
            await go(BASE + "/#/day/4/learn", 2.0)
            await p.eval("document.querySelector('#view .codebar [data-a=try]').click()"); await p.sleep(0.8)
            await p.shot("06_try_to_playground")

            # SQL diagram: find a day with a ```sql block
            for d in (28,):
                await go(f"{BASE}/#/day/{d}/learn", 1.6)
                await p.sleep(0.8)
                has = await p.eval("!![...document.querySelectorAll('#view pre code')].find(c=>/^\\s*select/i.test(c.textContent))")
                if has:
                    await p.eval("[...document.querySelectorAll('#view pre')].find(c=>/^\\s*select/i.test(c.textContent)).querySelector('[data-a=viz]').click()")
                    await p.sleep(2.5)
                    await p.shot(f"07_sql_day{d}")
                    break
            await p.eval("document.querySelector('.modal.xl [data-x]')?.click()")

            # dark theme + stacked layout
            await p.eval("document.querySelector('#btn-theme').click()"); await p.sleep(0.4)
            await go(BASE + "/#/", 2.0)
            await p.shot("08_home_dark")
            print("done ->", OUT)
    finally:
        proc.terminate()


asyncio.run(main())
