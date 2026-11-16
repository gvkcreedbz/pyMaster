"""Accessibility smoke check in headless Chrome (CDP), against a running TEST portal (it creates a little activity).
Per view (Home, a Day, Insights, Library) at each width it asserts: every button/link/field has an accessible name,
no tabindex > 0, no JS errors. Plus interaction checks: dialog traps focus and gives it back, the search palette and
the navigation drawer do the same, "?" opens the shortcut list, Esc then Tab leaves a code editor, live regions exist.
usage: python _dev_tools/a11y_check.py [base_url] [--cdp-port=9385] [--widths=1440,420]      (needs: websockets)
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
BASE = (ARGS[0] if ARGS else "http://127.0.0.1:8785").rstrip("/")
OPT = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
CDP_PORT = int(OPT.get("cdp-port", 9385))
WIDTHS = [int(x) for x in OPT.get("widths", "1440,420").split(",")]
CHROME = os.environ.get("CHROME") or os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
VIEWS = [("Home", "#/"), ("Day 3", "#/day/3/learn"), ("Insights", "#/insights"), ("Library", "#/library")]
problems: list[str] = []
n_checks = 0


def check(name, cond, extra=""):
    global n_checks
    n_checks += 1
    if not cond:
        problems.append(f"{name} {extra}")
        print(f"[FAIL] {name} {extra}")


AUDIT = r"""(() => {
  const words = s => /[\p{L}\p{N}]/u.test(s || '');
  const name = el => {
    const al = (el.getAttribute('aria-label') || '').trim(); if (al) return al;
    const lb = el.getAttribute('aria-labelledby');
    if (lb) { const t = lb.split(/\s+/).map(i => document.getElementById(i)?.textContent || '').join(' ').trim(); if (t) return t; }
    if (el.matches('input, select, textarea')) return el.labels && el.labels.length ? [...el.labels].map(l => l.textContent).join(' ').trim() : '';
    const t = (el.innerText || el.textContent || '').trim(); if (words(t)) return t;
    const img = el.querySelector('img[alt]:not([alt=""])'); return img ? img.alt : '';
  };
  const vis = el => el.getClientRects().length > 0 && !el.closest('[inert], [hidden]');
  const sel = 'button, a[href], [role=button], [role=separator][tabindex], input:not([type=hidden]), select, textarea, summary';
  const unnamed = [...document.querySelectorAll(sel)].filter(vis).filter(el => !name(el))
    .map(el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '') + ' ' + (el.outerHTML.slice(0, 90)));
  const posTab = [...document.querySelectorAll('[tabindex]')].filter(el => el.tabIndex > 0).map(el => el.outerHTML.slice(0, 80));
  const noAlt = [...document.querySelectorAll('img:not([alt])')].map(el => el.outerHTML.slice(0, 80));
  const dlg = [...document.querySelectorAll('[role=dialog]')].filter(vis).filter(el => !name(el) && !el.getAttribute('aria-labelledby')).length;
  const ids = {}; document.querySelectorAll('[id]').forEach(e => { ids[e.id] = (ids[e.id] || 0) + 1; });
  const dupIds = Object.keys(ids).filter(k => ids[k] > 1);
  return { unnamed, posTab, noAlt, dlg, dupIds, overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth };
})()"""


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

    async def key(self, key, code=None, vk=0, shift=False, ctrl=False, text=None):
        mod = (8 if shift else 0) | (2 if ctrl else 0)
        base = dict(modifiers=mod, key=key, code=code or key, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
        await self.send("Input.dispatchKeyEvent", type="keyDown", **base, **({"text": text} if text else {}))
        await self.send("Input.dispatchKeyEvent", type="keyUp", **base)
        await asyncio.sleep(0.12)

    def errors(self):
        out = []
        for e in self.events:
            m, p = e["method"], e["params"]
            if m == "Runtime.exceptionThrown":
                d = p["exceptionDetails"]
                out.append("exception: " + (d.get("exception", {}).get("description") or d.get("text", ""))[:250])
            elif m == "Runtime.consoleAPICalled" and p["type"] in ("error", "assert"):
                out.append("console.error: " + " ".join(str(a.get("value", a.get("description", ""))) for a in p["args"])[:250])
            elif m == "Network.responseReceived" and p["response"]["status"] >= 400 and not p["response"]["url"].endswith("/favicon.ico"):
                out.append(f"http {p['response']['status']}: {p['response']['url']}")
        self.events.clear()
        return out


ACTIVE = "(()=>{const a=document.activeElement;return a?{tag:a.tagName,id:a.id,inModal:!!a.closest('.modal'),inPal:!!a.closest('#palette'),inSide:!!a.closest('#side'),inCm:!!a.closest('.CodeMirror')}:{}})()"


async def tab_cycle(p, where, inside_key, times=14, shift=False):
    """Press Tab (or Shift+Tab) repeatedly; focus must never leave the container."""
    left = 0
    for _ in range(times):
        await p.key("Tab", "Tab", 9, shift=shift)
        a = await p.eval(ACTIVE)
        if not a.get(inside_key):
            left += 1
    check(f"{where}: {'Shift+' if shift else ''}Tab keeps focus inside ({times} presses)", left == 0, f"left {left}x")


async def run(p):
    for m in ("Page.enable", "Runtime.enable", "Network.enable"):
        await p.send(m)
    await p.send("Page.navigate", url=BASE + "/")
    await asyncio.sleep(2.5)
    for _ in range(40):
        if await p.eval("document.querySelector('#view') && document.querySelector('#view').innerText.length > 20"):
            break
        await asyncio.sleep(0.25)
    await asyncio.sleep(1.0)                                   # extensions load after the first route
    p.events.clear()
    for w in WIDTHS:
        await p.send("Emulation.setDeviceMetricsOverride", width=w, height=900, deviceScaleFactor=1, mobile=w < 600)
        for label, h in VIEWS:
            await p.eval(f"location.hash = {json.dumps(h)}")
            await asyncio.sleep(0.9)
            for _ in range(30):
                if await p.eval("document.querySelector('#view') && document.querySelector('#view').innerText.trim().length > 40 && !/^Loading/.test(document.querySelector('#view').innerText.trim())"):
                    break
                await asyncio.sleep(0.2)
            await asyncio.sleep(0.5)
            r = await p.eval(AUDIT)
            tag = f"{label} @{w}px"
            check(f"{tag}: every control has an accessible name", not r["unnamed"], "; ".join(r["unnamed"][:4]))
            check(f"{tag}: no tabindex > 0", not r["posTab"], "; ".join(r["posTab"][:3]))
            check(f"{tag}: images have alt", not r["noAlt"], "; ".join(r["noAlt"][:3]))
            check(f"{tag}: dialogs are labelled", r["dlg"] == 0)
            check(f"{tag}: no duplicate ids", not r["dupIds"], ",".join(r["dupIds"][:5]))
            check(f"{tag}: no horizontal page overflow", r["overflow"] <= 2, f"{r['overflow']}px")
            errs = p.errors()
            check(f"{tag}: no JS/network errors", not errs, "; ".join(errs[:3]))

    await p.send("Page.navigate", url=BASE + "/#/")
    await asyncio.sleep(3.0)
    await p.key("Tab", "Tab", 9)
    first = await p.eval("document.activeElement && document.activeElement.className")
    check("first Tab stop on a fresh page is the skip link", first == "skip-link", str(first))
    await p.key("Enter", "Enter", 13)
    f2 = await p.eval("document.activeElement && document.activeElement.id")
    check("activating the skip link focuses the lesson area", f2 == "main", str(f2))

    # ---- interactions (at the narrowest requested width, then the widest) ----------------------------------------
    for w in sorted(set([WIDTHS[0], WIDTHS[-1]])):
        await p.send("Emulation.setDeviceMetricsOverride", width=w, height=900, deviceScaleFactor=1, mobile=w < 600)
        await p.eval("location.hash = '#/'")
        await asyncio.sleep(1.0)
        t = f"@{w}px"
        live = await p.eval("(()=>{const t=document.querySelector('#toasts');return [t&&t.getAttribute('role'), t&&t.getAttribute('aria-live'), !!document.querySelector('#a11y-live'), !!document.querySelector('.skip-link')]})()")
        check(f"live regions + skip link {t}", live == ["status", "polite", True, True], str(live))

        # settings dialog (util.js modal)
        await p.eval("document.querySelector('#btn-settings').focus()")
        await p.eval("document.querySelector('#btn-settings').click()")
        await asyncio.sleep(0.8)
        d = await p.eval("(()=>{const m=document.querySelector('#modal-root .modal');return m?{role:m.getAttribute('role'),modal:m.getAttribute('aria-modal'),lab:m.getAttribute('aria-labelledby'),name:(document.getElementById(m.getAttribute('aria-labelledby')||'x')||{}).textContent,focus:document.activeElement===m}:null})()")
        check(f"modal has role=dialog, aria-modal, labelled heading, focus moved in {t}", bool(d) and d["role"] == "dialog" and d["modal"] == "true" and bool(d["name"]) and d["focus"], str(d))
        await tab_cycle(p, f"settings dialog {t}", "inModal", 16)
        await tab_cycle(p, f"settings dialog {t}", "inModal", 6, shift=True)
        btn = await p.eval("!!document.querySelector('#modal-root [data-bk-open]')")
        check(f"settings dialog offers the Backups button {t}", btn)
        await p.key("Escape", "Escape", 27)
        gone = await p.eval("!document.querySelector('#modal-root .modal')")
        back = await p.eval("document.activeElement && document.activeElement.id")
        check(f"Esc closes the dialog {t}", gone)
        check(f"focus returns to the opener {t}", back == "btn-settings", str(back))

        # backups dialog + shortcut dialog
        await p.eval("document.querySelector('#btn-backups').click()")
        await asyncio.sleep(0.8)
        txt = await p.eval("(document.querySelector('#modal-root .modal')||{}).innerText||''")
        check(f"backups dialog opens and lists copies {t}", "Backups" in txt and "Back up now" in txt and ("Restore" in txt or "No backups" in txt), txt[:80])
        await tab_cycle(p, f"backups dialog {t}", "inModal", 8)
        await p.key("Escape", "Escape", 27)
        await p.eval("document.body.focus()")
        await p.key("?", "Slash", 191, shift=True, text="?")
        txt = await p.eval("(document.querySelector('#modal-root .modal')||{}).innerText||''")
        check(f"'?' opens the shortcut list {t}", "Keyboard shortcuts" in txt and "Ctrl" in txt, txt[:60])
        await p.key("Escape", "Escape", 27)

        # command palette
        await p.eval("document.body.focus()")
        await p.eval("document.querySelector('#btn-search').focus()")
        await p.key("p", "KeyP", 80, ctrl=True)
        await asyncio.sleep(0.4)
        pal = await p.eval("(()=>{const e=document.querySelector('#palette .pal');const i=document.querySelector('#palette input');return e?{role:e.getAttribute('role'),modal:e.getAttribute('aria-modal'),focus:document.activeElement===i,combo:i.getAttribute('role'),opt:document.querySelectorAll('#palette [role=option]').length>0,ad:i.getAttribute('aria-activedescendant')}:null})()")
        check(f"palette: dialog semantics, input focused, options exposed {t}", bool(pal) and pal["role"] == "dialog" and pal["modal"] == "true" and pal["focus"] and pal["opt"] and bool(pal["ad"]), str(pal))
        await tab_cycle(p, f"palette {t}", "inPal", 5)
        await p.key("Escape", "Escape", 27)
        gone = await p.eval("!document.querySelector('#palette')")
        back = await p.eval("document.activeElement && document.activeElement.id")
        check(f"palette closes on Esc {t}", gone)
        check(f"palette gives focus back {t}", back == "btn-search", str(back))

        # navigation drawer
        closed = await p.eval("(()=>{const s=document.querySelector('#side');return s.inert===true})()")
        check(f"closed drawer is inert {t}", closed)
        await p.eval("document.querySelector('#btn-menu').focus()")
        await p.eval("document.querySelector('#btn-menu').click()")
        await asyncio.sleep(0.6)
        a = await p.eval(ACTIVE)
        check(f"opening the drawer moves focus into it {t}", a.get("inSide"), str(a))
        await tab_cycle(p, f"drawer {t}", "inSide", 14)
        await tab_cycle(p, f"drawer {t}", "inSide", 5, shift=True)
        await p.key("Escape", "Escape", 27)
        await asyncio.sleep(0.4)
        a = await p.eval("({open:document.querySelector('#side').classList.contains('open'),id:document.activeElement&&document.activeElement.id,inert:document.querySelector('#side').inert})")
        check(f"Esc closes the drawer, focus back on the menu button {t}", not a["open"] and a["id"] == "btn-menu" and a["inert"], str(a))

    # ---- code editor: Esc then Tab leaves it -----------------------------------------------------------------------
    await p.send("Emulation.setDeviceMetricsOverride", width=1440, height=900, deviceScaleFactor=1, mobile=False)
    await p.eval("location.hash = '#/day/3/practice'")
    await asyncio.sleep(1.8)
    ok = await p.eval("(()=>{const cm=document.querySelector('#view .CodeMirror, .pane .CodeMirror');if(!cm)return false;cm.CodeMirror.focus();return true})()")
    check("a code editor exists on the practice tab", ok)
    if ok:
        await p.key("Tab", "Tab", 9)
        a = await p.eval(ACTIVE)
        check("Tab inside the editor indents and keeps focus (unchanged behaviour)", a.get("inCm"), str(a))
        await p.key("Escape", "Escape", 27)
        await p.key("Tab", "Tab", 9)
        a = await p.eval(ACTIVE)
        check("Esc then Tab leaves the code editor", not a.get("inCm"), str(a))
    errs = p.errors()
    check("no JS/network errors during interaction checks", not errs, "; ".join(errs[:4]))


async def main():
    prof = tempfile.mkdtemp(prefix="pm_a11y_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={CDP_PORT}", f"--user-data-dir={prof}",
                             "--window-size=1440,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        page = None
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json"))
                page = next(t for t in tabs if t["type"] == "page")
                break
            except Exception:  # noqa: BLE001
                await asyncio.sleep(0.5)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            p = Page(ws)
            pump = asyncio.create_task(p.pump())
            await run(p)
            pump.cancel()
    finally:
        proc.terminate()
    print(f"\n{n_checks} checks, {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    asyncio.run(main())
