"""Pop-out via window.open (button and drag-the-tab-outside-the-window). Needs a user-gesture flag, so it runs through CDP.
usage: python _dev_tools/ui_detach_test.py [base_url]"""
import asyncio, json, os, subprocess, sys, tempfile, urllib.request
import websockets

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777"
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
PORT = 9336
FAILS = []


def check(name, ok, extra=""):
    print(("[ok]   " if ok else "[FAIL] ") + name + (f"   {extra}" if extra and not ok else ""))
    if not ok:
        FAILS.append(name)


async def main():
    prof = tempfile.mkdtemp(prefix="pm_det_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                             "--window-size=1440,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try: urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version"); break
            except Exception: await asyncio.sleep(0.5)
        info = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new", method="PUT")))
        async with websockets.connect(info["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            n = 0
            async def call(method, **params):
                nonlocal n; n += 1; i = n
                await ws.send(json.dumps({"id": i, "method": method, "params": params}))
                while True:
                    d = json.loads(await ws.recv())
                    if d.get("id") == i: return d.get("result", d)
            async def ev(js, gesture=False):
                r = await call("Runtime.evaluate", expression=js, awaitPromise=True, returnByValue=True, userGesture=gesture)
                if "exceptionDetails" in r: raise RuntimeError(json.dumps(r["exceptionDetails"])[:400])
                return r["result"].get("value")
            async def until(js, t=15):
                for _ in range(int(t * 5)):
                    try:
                        if await ev(js): return True
                    except Exception: pass
                    await asyncio.sleep(0.2)
                return False
            def targets(): return [t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json")) if t["type"] == "page"]

            await call("Page.navigate", url=BASE + "/#/day/1/learn")
            check("main loads", await until("!!document.querySelector('#view .fade-in')"))
            await ev("localStorage.removeItem('pm-layout')")
            before = len(targets())

            # 1. button pop-out of the playground
            await ev("document.querySelector('#pane-play [data-act=pop]').click()", gesture=True)
            await asyncio.sleep(2)
            ts = targets()
            check("pop-out button opens a second window", len(ts) == before + 1, f"{before}->{len(ts)}")
            check("it is the playground in solo mode", any("pane=play" in t["url"] for t in ts))
            check("main hides the playground and shows a 'popped' chip", await until("document.querySelector('#pane-play').classList.contains('hide') && !!document.querySelector('.pt.popped[data-t=play]')", 6))

            # 2. bring it back from main (closes the window)
            await ev("document.querySelector('.pt.popped[data-t=play] .dock').click()", gesture=True)
            check("dock button brings the playground back", await until("!document.querySelector('#pane-play').classList.contains('hide')", 6))
            await asyncio.sleep(1.5)
            check("and closes the popped window", not any("pane=play" in t["url"] for t in targets()))

            # 3. drag the Lesson tab out of the browser window
            await ev("""(()=>{const t=document.querySelector('#pane-lesson .ptab'), r=t.getBoundingClientRect();
                const o={bubbles:true,pointerId:7,button:0,pointerType:'mouse'};
                t.dispatchEvent(new PointerEvent('pointerdown',{...o,clientX:r.left+20,clientY:r.top+10}));
                t.dispatchEvent(new PointerEvent('pointermove',{...o,clientX:r.left+60,clientY:r.top+60}));
                const g=document.querySelector('.dragghost')?.innerText||'';
                t.dispatchEvent(new PointerEvent('pointermove',{...o,clientX:-30,clientY:r.top+60}));
                window.__ghost=[g, document.querySelector('.dragghost')?.innerText||''];
                t.dispatchEvent(new PointerEvent('pointerup',{...o,clientX:-30,clientY:r.top+60,screenX:100,screenY:200}));})()""", gesture=True)
            ghost = await ev("window.__ghost")
            check("dragging shows a ghost with the right hint", ghost and "detach" in ghost[0] and "own window" in ghost[1], str(ghost))
            await asyncio.sleep(2)
            check("dropping outside the window opens the lesson in its own window", any("pane=lesson" in t["url"] for t in targets()))
            check("main shows the lesson as popped", await until("!!document.querySelector('.pt.popped[data-t=lesson]')", 6))

            # 4. swap sides by dropping onto the other pane
            await ev("document.querySelector('.pt.popped[data-t=lesson] .dock').click()", gesture=True)
            await until("!document.querySelector('#pane-lesson').classList.contains('hide')", 6)
            await ev("""(()=>{const t=document.querySelector('#pane-lesson .ptab'), r=t.getBoundingClientRect(), p=document.querySelector('#pane-play').getBoundingClientRect();
                const o={bubbles:true,pointerId:8,button:0,pointerType:'mouse'};
                t.dispatchEvent(new PointerEvent('pointerdown',{...o,clientX:r.left+20,clientY:r.top+10}));
                t.dispatchEvent(new PointerEvent('pointermove',{...o,clientX:p.left+200,clientY:p.top+200}));
                t.dispatchEvent(new PointerEvent('pointerup',{...o,clientX:p.left+200,clientY:p.top+200}));})()""", gesture=True)
            await asyncio.sleep(0.4)
            order = await ev("(()=>{const l=document.querySelector('#pane-lesson').getBoundingClientRect().left, p=document.querySelector('#pane-play').getBoundingClientRect().left; return l>p})()")
            check("dropping a tab on the other pane swaps the sides", order is True)
            await ev("document.querySelector('#pane-play .ptab').dispatchEvent(new MouseEvent('dblclick',{bubbles:true}))")
            check("double-clicking a tab maximises it", await ev("document.querySelector('#pane-play').classList.contains('max')"))
            await ev("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))")
            check("Esc restores", await ev("!document.querySelector('#pane-play').classList.contains('max')"))
    finally:
        proc.terminate()
    print("\nALL OK" if not FAILS else f"\n{len(FAILS)} FAILED: {FAILS}")
    sys.exit(1 if FAILS else 0)

asyncio.run(main())
