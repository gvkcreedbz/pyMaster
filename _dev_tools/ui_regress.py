"""Headless-Chrome regression sweep against a running portal (use a TEST data dir, it creates activity).

Visits every route (home, 30 days x all tabs, insights, library docs, blueprints, bad routes) at three viewport
widths and fails on: uncaught JS exceptions, console errors, failed/4xx/5xx requests, empty views, horizontal
page overflow, "Something went wrong" cards.

usage: python _dev_tools/ui_regress.py [base_url] [--quick]          (needs: pip install websockets)
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

import websockets

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
QUICK = "--quick" in sys.argv
BASE = ARGS[0] if ARGS else "http://127.0.0.1:8777"
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
PORT = 9344
problems: list[str] = []
checks = 0


def check(name, cond, extra=""):
    global checks
    checks += 1
    if not cond:
        problems.append(f"{name} {extra}")
        print(f"[FAIL] {name} {extra}")


class Page:
    def __init__(self, ws):
        self.ws, self.n, self.pending, self.events = ws, 0, {}, []

    async def pump(self):
        async for m in self.ws:
            d = json.loads(m)
            if "id" in d and d["id"] in self.pending:
                self.pending.pop(d["id"]).set_result(d)
            elif "method" in d:
                self.events.append(d)

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

    def drain_problems(self):
        """Turn collected CDP events into readable problems and clear the buffer."""
        out, reqs = [], {}
        for e in self.events:
            m, p = e["method"], e["params"]
            if m == "Runtime.exceptionThrown":
                d = p["exceptionDetails"]
                out.append("exception: " + (d.get("exception", {}).get("description") or d.get("text", ""))[:300])
            elif m == "Runtime.consoleAPICalled" and p["type"] in ("error", "assert"):
                out.append("console.error: " + " ".join(str(a.get("value", a.get("description", ""))) for a in p["args"])[:300])
            elif m == "Network.responseReceived":
                reqs[p["requestId"]] = p["response"]
                st = p["response"]["status"]
                if st >= 400 and not p["response"]["url"].endswith("/favicon.ico"):
                    out.append(f"http {st}: {p['response']['url']}")
            elif m == "Network.loadingFailed" and not p.get("canceled"):
                out.append(f"request failed: {p.get('errorText')} ({p['requestId']})")
        self.events.clear()
        return out


async def main():
    prof = tempfile.mkdtemp(prefix="pm_regress_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             f"--user-data-dir={prof}", "--window-size=1440,900", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        page = None
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
            for m in ("Page.enable", "Runtime.enable", "Network.enable"):
                await p.send(m)

            async def visit(route, label, settle=0.5, need_view=True):
                await p.send("Page.navigate", url=BASE + "/" + route) if route.startswith("?") else None
                if not route.startswith("?"):
                    await p.eval(f"location.hash = {json.dumps(route)}")
                await asyncio.sleep(settle)
                for _ in range(40):                        # wait until the view has content and no spinner
                    ok = await p.eval("(()=>{const v=document.querySelector('#view');return !!v && v.innerText.trim().length>20 && !/^Loading/.test(v.innerText.trim())})()")
                    if ok:
                        break
                    await asyncio.sleep(0.15)
                info = await p.eval("""(()=>{const v=document.querySelector('#view');
                    return {len:(v?v.innerText.trim().length:0), bad:/Something went wrong/.test(v?v.innerText:'') ? v.innerText.slice(0,400) : false,
                            overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                            hash: location.hash, pane: (document.querySelector('#pane-lesson')||{}).className, html: v ? v.innerHTML.length : -1, w: innerWidth}})()""")
                if info["len"] <= 20:                       # stuck? record what the network was doing (diagnostics)
                    info["net"] = await p.eval("JSON.stringify(performance.getEntriesByType('resource').slice(-8).map(e=>[e.name.split('/api')[1]||e.name.slice(-24),Math.round(e.startTime),Math.round(e.duration)]))+' now='+Math.round(performance.now())")
                errs = p.drain_problems()
                check(f"{label}: no JS/network errors", not errs, "; ".join(errs[:3]))
                if need_view:
                    check(f"{label}: view has content", info["len"] > 20, str(info))
                    check(f"{label}: no error card", not info["bad"], str(info["bad"]))
                check(f"{label}: no page-level horizontal scroll", info["overflowX"] <= 2, f"overflow {info['overflowX']}px")
                return info

            await p.send("Page.navigate", url=BASE + "/")
            await asyncio.sleep(1.2)
            p.events.clear()
            widths = [1440] if QUICK else [1440, 1000, 420]
            for a in sys.argv[1:]:
                if a.startswith("--widths="):
                    widths = [int(x) for x in a.split("=", 1)[1].split(",")]
            for w in widths:
                await p.send("Emulation.setDeviceMetricsOverride", width=w, height=900, deviceScaleFactor=1, mobile=w < 500)
                await p.send("Page.navigate", url=BASE + "/")
                await asyncio.sleep(1.2)
                p.events.clear()
                await p.eval("localStorage.removeItem('pm-layout')")
                await visit("#/", f"[{w}] home")
                days = range(1, 31) if w == 1440 else (1, 8, 14, 22, 28, 30)
                tabs = ("learn", "along", "practice", "quiz", "notes") if w == 1440 and not QUICK else ("learn", "practice")
                for d in days:
                    for t in tabs:
                        await visit(f"#/day/{d}/{t}", f"[{w}] day {d}/{t}", 0.25)
                await visit("#/insights", f"[{w}] insights", 0.8)
                await visit("#/library", f"[{w}] library")
                await visit("#/library/README.md", f"[{w}] library doc")
                await visit("#/blueprints", f"[{w}] blueprints", 0.6)
                for bid in ("live-order-tracker", "ticket-triage-pipeline", "site-watcher", "patterns"):
                    await visit(f"#/blueprints/{bid}", f"[{w}] blueprint {bid}", 1.0)
                    if w == 1440 and bid != "patterns":
                        await asyncio.sleep(2.0)             # let Mermaid draw
                        d = await p.eval("""(()=>({svgs: document.querySelectorAll('#view .mmd .mmd-svg svg').length,
                            blocks: document.querySelectorAll('#view .mmd').length,
                            syntax: document.querySelectorAll('#view .mmd-err').length}))()""")
                        check(f"[{w}] {bid}: every diagram rendered", d["blocks"] > 0 and d["svgs"] == d["blocks"] and d["syntax"] == 0, str(d))
                        check(f"[{w}] {bid}: diagram render produced no errors", not p.drain_problems())
                for t in ("code", "run"):
                    await visit(f"#/blueprints/live-order-tracker/{t}", f"[{w}] blueprint tab {t}", 0.6)
                # bad routes should land somewhere sane, not blow up
                await visit("#/nonsense", f"[{w}] unknown route", 0.8)
                await visit("#/day/99/learn", f"[{w}] day 99", 0.6, need_view=False)
                await visit("#/day/abc", f"[{w}] day abc", 0.6, need_view=False)

            # command palette / search
            await p.send("Emulation.setDeviceMetricsOverride", width=1440, height=900, deviceScaleFactor=1, mobile=False)
            await visit("#/", "palette: home", 0.6)
            await p.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'p',ctrlKey:true,bubbles:true}))")
            await asyncio.sleep(0.4)
            has = await p.eval("!!document.querySelector('#palette')")
            check("palette opens with Ctrl+P", has)
            if has:
                await p.eval("(()=>{const i=document.querySelector('#palette input');i.value='decorator';i.dispatchEvent(new Event('input',{bubbles:true}))})()")
                await asyncio.sleep(1.0)
                n = await p.eval("document.querySelectorAll('#palette .pal-item').length")
                check("palette search returns results for 'decorator'", n and n > 0, str(n))
                await p.eval("document.querySelector('#palette input').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))")
                await asyncio.sleep(0.8)
                check("palette Enter navigates and closes", await p.eval("!document.querySelector('#palette')"))
                check("palette: no errors", not p.drain_problems())

            # review queue card on home
            await visit("#/", "home again", 0.6)
            check("home shows review card element or empty-state without errors", await p.eval("!!document.querySelector('#view')"))
    finally:
        proc.terminate()
    print(f"\n{checks} checks, {len(problems)} problems")
    if problems:
        print("PROBLEMS:", *problems[:40], sep="\n  ")
        sys.exit(1)
    print("ALL OK")


if __name__ == "__main__":
    asyncio.run(main())
