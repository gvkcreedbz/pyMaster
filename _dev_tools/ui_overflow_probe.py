"""List the elements that stick out past the viewport at a narrow width (diagnostic for the overflow check).

usage: python _dev_tools/ui_overflow_probe.py [base_url] [width] [route]
"""
import asyncio
import json
import os
import random
import subprocess
import sys
import tempfile
import urllib.request

import websockets

sys.path.insert(0, os.path.dirname(__file__))
from ui_regress import CHROME, Page  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777"
W = int(sys.argv[2]) if len(sys.argv) > 2 else 420
ROUTE = sys.argv[3] if len(sys.argv) > 3 else "#/"
PORT = random.randint(9400, 9899)

JS = """(()=>{const vw=document.documentElement.clientWidth;const out=[];
for(const e of document.querySelectorAll('body *')){const r=e.getBoundingClientRect();
 if(r.width&&r.right>vw+2){let p=e,hidden=false;while((p=p.parentElement)){const o=getComputedStyle(p).overflowX;
  if(o!=='visible'&&p!==document.body&&p!==document.documentElement){hidden=true;break}}
  if(!hidden)out.push((e.tagName+'#'+e.id+'.'+(e.className&&e.className.baseVal===undefined?e.className:'')).slice(0,60)+' right='+Math.round(r.right)+' w='+Math.round(r.width))}}
return {vw,sw:document.documentElement.scrollWidth,iw:innerWidth,out:out.slice(0,25)}})()"""


async def main():
    prof = tempfile.mkdtemp(prefix="pm_probe_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             f"--user-data-dir={prof}", "--window-size=1440,900", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            await p.send("Page.enable")
            await p.send("Emulation.setDeviceMetricsOverride", width=W, height=900, deviceScaleFactor=1, mobile=W < 500)
            await p.send("Page.navigate", url=BASE + "/")
            await asyncio.sleep(3)
            await p.eval(f"location.hash = {json.dumps(ROUTE)}")
            await asyncio.sleep(2)
            print(json.dumps(await p.eval(JS), indent=1))
    finally:
        proc.terminate()


asyncio.run(asyncio.wait_for(main(), 60))
