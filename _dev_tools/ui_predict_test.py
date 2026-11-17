"""Browser test of "predict before you run" on the Code-along tab. Uses Chrome debugging port 9393.
usage: python _dev_tools/ui_predict_test.py http://127.0.0.1:8780 python|java     (throw-away server only)
"""
import asyncio
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import websockets

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ui_drills_test as U  # noqa: E402

BASE, TRACK = U.BASE, U.TRACK
PORT = 9393
problems, checks = [], 0


def check(name, cond, extra=""):
    global checks
    checks += 1
    if not cond:
        problems.append(f"{name} {extra}")
        print(f"[FAIL] {name} {extra}")


RUN = "document.querySelector('#rp [data-run]').click()"


async def main():
    prof = tempfile.mkdtemp(prefix="pm_predict_")
    proc = subprocess.Popen([U.CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                             "--window-size=1440,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        page = None
        for _ in range(60):
            try:
                page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json")) if t["type"] == "page")
                break
            except Exception:  # noqa: BLE001
                await asyncio.sleep(0.5)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            p = U.Page(ws)
            asyncio.create_task(p.pump())
            for m in ("Page.enable", "Runtime.enable", "Network.enable"):
                await p.send(m)
            await p.send("Page.navigate", url=BASE + "/")
            await U.wait_boot(p)
            await p.eval("localStorage.removeItem('pm-predict')")
            await p.eval("location.hash = '#/day/1/along'")
            check("code-along renders with a Run button", await U.wait_for(p, "!!document.querySelector('#rp [data-run]')", 15))
            check("'Predict first' switch is there and on", await U.wait_for(p, "!!document.querySelector('#pd-on') && document.querySelector('#pd-on').checked", 6))

            # 1. Run asks first; "Just run it" runs without a comparison
            await p.eval(RUN)
            check("pressing Run opens the prediction box", await U.wait_for(p, "!!document.querySelector('#pd-ta')", 6))
            check("the code has not run yet", await p.eval("!document.querySelector('#rp .results .score, #rp [data-res] pre')"))
            await p.eval("document.querySelector('#pd-skip').click()")
            ran = await U.wait_for(p, "!!document.querySelector('#rp [data-res] pre')", 25)
            check("'Just run it' runs the code", ran, "" if ran else (await p.eval("document.querySelector('#rp').innerHTML.slice(-700)") + " || " + "; ".join(p.problems())))
            check("...with no comparison box", await p.eval("!document.querySelector('.pd-compare')"))
            actual = await p.eval("document.querySelector('#rp [data-res] pre').innerText")
            check("the example printed something", len((actual or '').strip()) > 0, repr(actual)[:80])

            # 2. a wrong prediction shows both sides and asks whether it was close
            await p.eval(RUN)
            await U.wait_for(p, "!!document.querySelector('#pd-ta')", 6)
            await p.eval("(() => { const t = document.querySelector('#pd-ta'); t.value = 'totally different text'; })()")
            await p.eval("document.querySelector('#pd-go').click()")
            check("a wrong prediction shows the comparison", await U.wait_for(p, "!!document.querySelector('.pd-compare .pd-cols')", 25))
            cmp_txt = await p.eval("document.querySelector('.pd-compare').innerText")
            check("it shows what you expected and what happened", "totally different text" in cmp_txt and "you expected" in cmp_txt.lower() and "it printed" in cmp_txt.lower(), cmp_txt[:200].replace(chr(10), " | "))
            await p.eval("document.querySelector('.pd-rate .btn:last-child').click()")
            check("rating it saves", await U.wait_for(p, "/Saved/.test(document.querySelector('.pd-compare').innerText)", 6))

            # 3. an exact prediction is recognised
            await p.eval(RUN)
            await U.wait_for(p, "!!document.querySelector('#pd-ta')", 6)
            await p.eval("(txt => { document.querySelector('#pd-ta').value = txt; })(%s)" % json.dumps(actual))
            await p.eval("document.querySelector('#pd-go').click()")
            check("an exact prediction is recognised", await U.wait_for(p, "/predicted it exactly/i.test(document.querySelector('.pd-compare')?.innerText || '')", 25))

            # 4. the event reached the server
            ev = await p.eval("fetch('/api/export').then(r => r.json()).then(j => (j.events || []).filter(e => e.type === 'predict_run').map(e => e.payload))")
            check("predict_run events were logged (one wrong, one exact)", isinstance(ev, list) and len(ev) >= 2, str(ev)[:200])

            # 5. switch it off: Run goes straight through
            await p.eval("document.querySelector('#pd-on').click()")
            await p.eval(RUN)
            await asyncio.sleep(1.0)
            check("with the switch off no box appears", await p.eval("!document.querySelector('#pd-ta')"))
            await p.eval("document.querySelector('#pd-on').click()")                                     # back on

            # 6. survives the page redrawing itself (marking the day done re-renders the tabs)
            await p.eval("document.querySelector('#stseg [data-s=done]').click()")
            await asyncio.sleep(1.2)
            await p.eval("document.querySelector('#stseg [data-s=open]').click()")
            await asyncio.sleep(1.2)
            await p.eval(RUN)
            check("still asks after the page redraws itself", await U.wait_for(p, "!!document.querySelector('#pd-ta')", 6))
            for pr in p.problems():
                check("no console/network problems", False, pr)
    finally:
        proc.terminate()
    print(f"\n{checks} checks, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
