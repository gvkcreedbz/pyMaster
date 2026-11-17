"""Browser test of the Drills tab: opens #/day/N/drills in headless Chrome and SOLVES every shipped drill through the UI
(clicking, typing, arranging) after first giving one wrong answer. Fails on console errors / failed requests.
usage: python _dev_tools/ui_drills_test.py http://127.0.0.1:8777 python|java [days...]   (needs: websockets)
Use a TEST server with a throw-away data dir: it records attempts. Uses Chrome debugging port 9391.
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import websockets

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from portal import drills_core as core  # noqa: E402
ROOT = Path(__file__).resolve().parent.parent
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8777"
TRACK = sys.argv[2] if len(sys.argv) > 2 else "python"
DAYS = [int(x) for x in sys.argv[3:]] or list(range(1, 31))
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
PORT = 9391
DAYS_DIR = ROOT / ("java/days" if TRACK == "java" else "days")
problems, checks = [], 0


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
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:600])
        return r["result"].get("value")

    def problems(self):
        out = []
        for e in self.events:
            m, p = e["method"], e["params"]
            if m == "Runtime.exceptionThrown":
                out.append("exception: " + (p["exceptionDetails"].get("exception", {}).get("description") or "")[:300])
            elif m == "Runtime.consoleAPICalled" and p["type"] in ("error", "assert"):
                out.append("console.error: " + " ".join(str(a.get("value", a.get("description", ""))) for a in p["args"])[:300])
            elif m == "Network.responseReceived" and p["response"]["status"] >= 400 and not p["response"]["url"].endswith("/favicon.ico"):
                if "/check" not in p["response"]["url"]:
                    out.append(f"http {p['response']['status']}: {p['response']['url']}")
        self.events.clear()
        return out


async def wait_boot(p):
    """Wait like a person would: the first page is drawn and the extensions are loaded (a click during boot would be wiped by the next render)."""
    await wait_for(p, "!!document.querySelector('#topbar-extras') && document.querySelector('#topbar-extras').children.length > 0", 30)
    await wait_for(p, "(document.querySelector('#view')?.innerText || '').trim().length > 30 && !/^Loading/.test(document.querySelector('#view').innerText.trim())", 30)
    await asyncio.sleep(1.2)


async def wait_for(p, js, secs=12):
    for _ in range(int(secs * 10)):
        if await p.eval(js):
            return True
        await asyncio.sleep(0.1)
    return False


# ---- DOM helpers (run inside the page) ----------------------------------------------------------------------------------------
JS_CLICK_DOT = "(i)=>document.querySelectorAll('.dr-dot')[i].click()"


def js(code, *args):
    return f"({code})({', '.join(json.dumps(a) for a in args)})"


SOLVERS = {
    "predict": """(exp) => { const t = document.querySelector('.dr-area'); t.value = exp; t.dispatchEvent(new Event('input', {bubbles: true})); return true; }""",
    "fill": """(vals, wrong) => { const els = [...document.querySelectorAll('.dr-card .dr-blank')];
        if (els.length !== vals.length) return 'blank count ' + els.length + ' vs ' + vals.length;
        els.forEach((e, i) => { let v = vals[i]; if (wrong) { v = 'zzz'; if (e.tagName === 'SELECT') { const o = [...e.options].find(o => o.value && o.value !== vals[i]); v = o ? o.value : v; } } e.value = v; e.dispatchEvent(new Event('change', {bubbles: true})); }); return true; }""",
    "bug": """(lines, fix) => { for (const n of lines) document.querySelector('.dr-line[data-n="' + n + '"]').click();
        const lab = [...document.querySelectorAll('.dr-opt')].find(l => l.textContent.trim() === fix.trim());
        if (!lab) return 'no option ' + fix; lab.querySelector('input').click(); return true; }""",
    "review": """(texts) => { const labs = [...document.querySelectorAll('.dr-card .dr-opt')];
        for (const t of texts) { const lab = labs.find(l => l.textContent.trim().startsWith(t.trim())); if (!lab) return 'no item ' + t.slice(0, 40); lab.querySelector('input').click(); } return true; }""",
    "parsons": """(lines, indents, blanks) => {
        const pool = () => [...document.querySelectorAll('[data-zone="pool"] .dr-piece')];
        for (const ln of lines) {
          const key = ln.split('___').sort((a, b) => b.length - a.length)[0].trim();
          const piece = pool().find(p => p.querySelector('.tx').textContent.trim() === ln.trim()) || pool().find(p => ln.includes('___') && key && p.querySelector('.tx').textContent.includes(key));
          if (!piece) return 'no piece for ' + ln;
          piece.querySelector('button[title="Add to your program"]').click();
        }
        const prog = () => [...document.querySelectorAll('[data-zone="prog"] .dr-piece')];
        indents.forEach((n, i) => { for (let k = 0; k < n; k++) { const b = prog()[i].querySelector('button[title="More indent"]'); if (!b) return 'no indent button'; b.click(); } });
        if (blanks && blanks.length) { const sels = [...document.querySelectorAll('[data-zone="prog"] select.dr-blank')];
          sels.forEach((s, i) => { s.value = blanks[i]; s.dispatchEvent(new Event('change', {bubbles: true})); }); }
        return true; }""",
}


def solver_call(d):
    t = d["type"]
    if t == "predict":
        return js(SOLVERS[t], d["expected"])
    if t == "fill":
        return js(SOLVERS[t], [b["answers"][0] for b in d["blanks"]])
    if t == "bug":
        return js(SOLVERS[t], d["bug_lines"], d["options"][d["answer"]])
    if t == "review":
        return js(SOLVERS[t], [x["text"] for x in d["issues"]])
    return js(SOLVERS[t], d["lines"], list(d.get("indent") or [0] * len(d["lines"])) if "indent" in d else [0] * len(d["lines"]),
              [b["answers"][0] for b in d.get("blanks", [])] if d.get("faded") else [])


async def main():
    prof = tempfile.mkdtemp(prefix="pm_drills_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
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
            p = Page(ws)
            asyncio.create_task(p.pump())
            for m in ("Page.enable", "Runtime.enable", "Network.enable"):
                await p.send(m)
            await p.send("Page.navigate", url=BASE + "/")
            await wait_for(p, "!!document.querySelector('#view') && document.querySelector('#view').innerText.length > 30", 20)
            await wait_boot(p)
            await asyncio.sleep(1.0)
            for n in DAYS:
                f = next(iter(sorted(DAYS_DIR.glob(f"day{n:02d}_*"))), None)
                if not f or not (f / "DRILLS.json").is_file():
                    continue
                drills = core.load_doc(f / "DRILLS.json")["drills"]
                await p.eval(f"location.hash = '#/day/{n}/drills'")
                ok = await wait_for(p, "!!document.querySelector('.dr-card')", 15)
                info = "" if ok else (await p.eval("location.hash + ' | tabs: ' + [...document.querySelectorAll('.tab')].map(t => t.textContent).join(',') + ' | ' + (document.querySelector('#view')?.innerText || '').slice(0, 160).replace(/\\n/g, ' ')") + " | " + "; ".join(p.problems()))
                check(f"day {n}: drills tab renders", ok, info)
                if not ok:
                    continue
                tab = await p.eval("document.querySelector('.tab.on')?.textContent || ''")
                check(f"day {n}: 'Drills' tab is selected", "Drills" in tab, tab)
                check(f"day {n}: one dot per drill", await p.eval("document.querySelectorAll('.dr-dot').length") == len(drills))
                for i, d in enumerate(drills):
                    await p.eval(js(JS_CLICK_DOT, i))
                    await asyncio.sleep(0.15)
                    label = f"day {n} {d['id']} ({d['type']})"
                    check(f"{label}: card shows its type", await p.eval("!!document.querySelector('.dr-type')"))
                    # 1) check with nothing filled in: friendly toast, no request, no crash
                    await p.eval("document.querySelector('.dr-acts .btn.primary').click()")
                    await asyncio.sleep(0.2)
                    # 2) a deliberately wrong answer (not for parsons/review, where 'nothing yet' is the wrong answer)
                    if d["type"] == "predict":
                        await p.eval(js(SOLVERS["predict"], "nope"))
                    elif d["type"] == "fill":
                        await p.eval(js(SOLVERS["fill"], [b["answers"][0] for b in d["blanks"]], True))
                    elif d["type"] == "bug":
                        wrong_opt = d["options"][(d["answer"] + 1) % len(d["options"])]
                        wl = [x for x in range(1, 30) if x not in d["bug_lines"]][0]
                        await p.eval(js(SOLVERS["bug"], [wl], wrong_opt))
                    elif d["type"] == "review":
                        non = d["non_issues"][0]["text"]
                        await p.eval(js(SOLVERS["review"], [non]))
                    if d["type"] != "parsons":
                        await p.eval("document.querySelector('.dr-acts .btn.primary').click()")
                        got = await wait_for(p, "!!document.querySelector('.dr-fb.try')", 6)
                        check(f"{label}: wrong answer gets 'Not quite' feedback", got,
                              "" if got else await p.eval("(document.querySelector('.dr-card')?.innerText || '').slice(-260).replace(/\\n/g, ' | ') + ' || toasts: ' + (document.querySelector('#toasts')?.innerText || '')"))
                        await p.eval("location.hash = '#/day/%d/drills'" % n)             # same hash: no-op; repaint through the dot
                        await p.eval(js(JS_CLICK_DOT, i if i else 1))
                        await asyncio.sleep(0.2)
                        await p.eval(js(JS_CLICK_DOT, i))
                        await asyncio.sleep(0.2)
                    # 3) the right answer
                    r = await p.eval(solver_call(d))
                    check(f"{label}: solver ran", r is True, str(r))
                    await p.eval("document.querySelector('.dr-acts .btn.primary').click()")
                    solved = await wait_for(p, "!!document.querySelector('.dr-fb.good')", 8)
                    check(f"{label}: right answer is accepted", solved,
                          (await p.eval("document.querySelector('.dr-fb')?.innerText || document.querySelector('.dr-card')?.innerText.slice(-300)")) or "")
                    check(f"{label}: explanation shown", solved and len(await p.eval("document.querySelector('.dr-fb.good')?.innerText || ''")) > 30)
                    check(f"{label}: dot turns green", await p.eval(f"document.querySelectorAll('.dr-dot')[{i}].classList.contains('solved')"))
                    for pr in p.problems():
                        check(f"{label}: no console/network problems", False, pr)
                # 4) the tab counter reflects the work after a reload of the day
                # 4) reload while ON the drills page: the deep link must come back (extensions load after the first paint)
                await p.send("Page.reload")
                back = await wait_for(p, "!!document.querySelector('.dr-card')", 20)
                check(f"day {n}: deep link #/day/{n}/drills survives a reload", back,
                      await p.eval("location.hash + ' | ' + (document.querySelector('#view')?.innerText || '').slice(0, 120).replace(/\\n/g, ' ')") if not back else "")
                # 5) the tab counter reflects the finished drills
                await wait_for(p, "[...document.querySelectorAll('.tab')].some(t => t.textContent.startsWith('Drills'))", 10)
                cnt = await p.eval("[...document.querySelectorAll('.tab')].find(t => t.textContent.startsWith('Drills'))?.textContent || ''")
                check(f"day {n}: Drills tab counter", f"{len(drills)}/{len(drills)}" in cnt, cnt)
            for pr in p.problems():
                check("final: no console/network problems", False, pr)
    finally:
        proc.terminate()
    print(f"\n{checks} checks, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
