"""Multi-window behaviour: pop-out panes talk to the main window over BroadcastChannel.
Opens the main app and solo windows (?pane=play / lesson / tutor) as separate Chrome tabs and checks the hand-offs.

usage: python _dev_tools/ui_popout_test.py [base_url]     (needs: pip install websockets)
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

import websockets

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777"
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
PORT = 9334
FAILS = []


def check(name, ok, extra=""):
    print(("[ok]   " if ok else "[FAIL] ") + name + (f"   {extra}" if extra and not ok else ""))
    if not ok:
        FAILS.append(name)


class Page:
    def __init__(self, ws):
        self.ws, self.n, self.pending = ws, 0, {}
        asyncio.get_event_loop().create_task(self.pump())

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

    async def until(self, js, timeout=20):
        for _ in range(int(timeout * 5)):
            try:
                if await self.eval(js):
                    return True
            except Exception:  # noqa: BLE001
                pass
            await asyncio.sleep(0.2)
        return False


async def open_tab(url):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new", method="PUT")
    info = json.load(urllib.request.urlopen(req))
    ws = await websockets.connect(info["webSocketDebuggerUrl"], max_size=50_000_000)
    p = Page(ws)
    await p.send("Emulation.setDeviceMetricsOverride", width=1440, height=900, deviceScaleFactor=1, mobile=False)
    # background tabs in headless Chrome still need to count as visible for focus/timers
    await p.send("Emulation.setFocusEmulationEnabled", enabled=True)
    await p.send("Page.navigate", url=url)       # (a '#fragment' can't travel through /json/new)
    return p


async def main():
    prof = tempfile.mkdtemp(prefix="pm_chrome2_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                             "--window-size=1440,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version"); break
            except Exception:  # noqa: BLE001
                await asyncio.sleep(0.5)

        main_ = await open_tab(BASE + "/#/day/4/learn")
        check("main loads", await main_.until("!!document.querySelector('#view .fade-in')"))
        await main_.eval("localStorage.removeItem('pm-layout'); localStorage.removeItem('pm-play-code')")
        sid = await main_.eval("(async()=>{const m=await import('/static/js/util.js'); return m.store.sid})()")
        check("main has a session id", bool(sid))

        # ---- playground window -------------------------------------------------------------------------------------
        play = await open_tab(f"{BASE}/?pane=play&sid={sid}")
        check("play window loads (solo)", await play.until("document.body.classList.contains('solo-play') && !!document.querySelector('#pg .CodeMirror')"))
        check("play window shows only the playground", await play.eval("getComputedStyle(document.querySelector('#pane-lesson')).display==='none' && getComputedStyle(document.querySelector('#pane-play')).display!=='none'"))
        check("main notices play is popped out", await main_.until("document.querySelector('#pane-play').classList.contains('hide') && !!document.querySelector('.pt.popped[data-t=play]')", 8))
        check("main lesson takes the full width", await main_.eval("Math.abs(document.querySelector('#pane-lesson').getBoundingClientRect().width - (innerWidth-16)) < 6"))

        # Try from the lesson goes to the other window
        code = await main_.eval("document.querySelector('#view .codebar [data-a=try]').closest('pre').querySelector('code').textContent.replace(/\\n$/,'')")
        await main_.eval("document.querySelector('#view .codebar [data-a=try]').click()")
        got = await play.until(f"document.querySelector('#pg .CodeMirror').CodeMirror.getValue().trim()===({json.dumps(code)}).trim()", 6)
        check("Try sends the code to the playground window", got)
        check("main did not navigate", (await main_.eval("location.hash")) == "#/day/4/learn")

        # ---- assistant in main uses code from the playground window ------------------------------------------------
        marker = "zebra_total = 0\nfor zebra in [1, 2, 3]:\n    zebra_total += zebra\nprint(zebra_total)\n"
        await play.eval(f"(()=>{{const cm=document.querySelector('#pg .CodeMirror').CodeMirror; cm.setValue({json.dumps(marker)}); cm.focus();}})()")
        await asyncio.sleep(0.4)
        await main_.eval("document.querySelector('#askbar').click()")
        await asyncio.sleep(0.5)
        await main_.eval("document.querySelector('#quick [data-q=visual]').click()")
        ok = await main_.until("(()=>{const b=[...document.querySelectorAll('#msgs .msg.bot')].pop(); return !!b && /zebra_total/.test(b.innerText) && !!b.querySelector('.mmd svg')})()", 15)
        check("assistant drew a diagram of the code that lives in the other window", ok)

        # ---- dock back ------------------------------------------------------------------------------------------
        await play.eval("(async()=>{const m=await import('/static/js/layout.js'); m.dockSelf();})()")
        check("docking restores the playground in main", await main_.until("!document.querySelector('#pane-play').classList.contains('hide')", 8))
        check("docked playground has the text typed in the other window", await main_.until(f"document.querySelector('#pg .CodeMirror').CodeMirror.getValue().includes('zebra_total')", 6))

        # ---- lesson window follows navigation ------------------------------------------------------------------------
        lesson = await open_tab(f"{BASE}/?pane=lesson&sid={sid}#/day/2/learn")
        check("lesson window loads and renders", await lesson.until("!!document.querySelector('#view .fade-in') && document.body.classList.contains('solo-lesson')"))
        check("main hides its lesson pane", await main_.until("document.querySelector('#pane-lesson').classList.contains('hide')", 8))
        await main_.eval("document.querySelector('#btn-menu').click()")
        await asyncio.sleep(0.4)
        await main_.eval("[...document.querySelectorAll('#side .dot')].find(d=>d.textContent==='6').click()")
        check("choosing a day in main navigates the lesson window", await lesson.until("location.hash.startsWith('#/day/6')", 8))
        check("main drawer closed after choosing", await main_.eval("!document.querySelector('#side').classList.contains('open')"))
        check("lesson window shows day 6", await lesson.until("/Day 06/i.test(document.querySelector('#view').innerText)", 8))

        # ask the assistant (in main) a question about the lesson that lives in the lesson window
        await main_.eval("(()=>{document.querySelector('#askbar')?.click();})()")
        await asyncio.sleep(0.4)
        await lesson.eval("(async()=>{const m=await import('/static/js/tutor.js'); m.ask('where_used','', 'for loop');})()")
        ok = await main_.until("(()=>{const m=[...document.querySelectorAll('#msgs .msg.user')].pop(); return !!m && /for loop/.test(m.innerText)})()", 10)
        check("a question asked from the lesson window lands in the assistant", ok)

        await main_.eval("(async()=>{const m=await import('/static/js/layout.js'); m.dock('lesson');})()")
        check("docking lesson brings it back with the current route", await main_.until("!document.querySelector('#pane-lesson').classList.contains('hide') && /Day 06/i.test(document.querySelector('#view').innerText)", 10))

        # ---- assistant window -------------------------------------------------------------------------------------
        tut = await open_tab(f"{BASE}/?pane=tutor&sid={sid}")
        check("assistant window loads", await tut.until("document.body.classList.contains('solo-tutor') && !!document.querySelector('#tin')"))
        check("assistant window learns the lesson context", await tut.until("/Day 6/.test(document.querySelector('#tctx').textContent)", 8))
        await tut.eval("document.querySelector('#quick [data-q=where_used]').click()")
        check("assistant window answers", await tut.until("(()=>{const b=[...document.querySelectorAll('#msgs .msg.bot')].pop(); return !!b && b.innerText.length>80})()", 15))
        check("main notices the assistant is popped", await main_.until("!!document.querySelector('.pt.popped[data-t=tutor]')", 8))

        # ---- layout persistence ------------------------------------------------------------------------------------
        await main_.eval("document.querySelector('#pane-play [data-act=close]').click()")
        saved = await main_.eval("JSON.parse(localStorage.getItem('pm-layout')).play")
        check("hiding the playground is remembered", saved is False)
    finally:
        proc.terminate()
    print("\nALL OK" if not FAILS else f"\n{len(FAILS)} FAILED: {FAILS}")
    sys.exit(1 if FAILS else 0)


asyncio.run(main())
