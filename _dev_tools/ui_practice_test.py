"""Browser test of Practice sessions (#/practice): runs a whole session in headless Chrome the way a learner would.
usage: python _dev_tools/ui_practice_test.py http://127.0.0.1:8780 python|java     (throw-away server only; needs: websockets)
Uses Chrome debugging port 9392.
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
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ui_drills_test as U  # noqa: E402  (shares the CDP page helper and the per-type solvers)
from portal import drills_core as core  # noqa: E402

BASE, TRACK = U.BASE, U.TRACK
PORT = 9392
N_PROBLEMS = 12
problems, checks = [], 0
CHROME = U.CHROME


def check(name, cond, extra=""):
    global checks
    checks += 1
    if not cond:
        problems.append(f"{name} {extra}")
        print(f"[FAIL] {name} {extra}")


def drill_by_pid(pid):
    day, did = pid.split("~")
    folder = next(iter(sorted(U.DAYS_DIR.glob(f"day{int(day):02d}_*"))))
    doc = core.load_doc(folder / "DRILLS.json")
    return int(day), next(d for d in doc["drills"] if d["id"] == did)


WRONG = {
    "predict": lambda d: U.js(U.SOLVERS["predict"], "nope"),
    "fill": lambda d: U.js(U.SOLVERS["fill"], [b["answers"][0] for b in d["blanks"]], True),
    "bug": lambda d: U.js(U.SOLVERS["bug"], [[x for x in range(1, 30) if x not in d["bug_lines"]][0]], d["options"][(d["answer"] + 1) % len(d["options"])]),
    "review": lambda d: U.js(U.SOLVERS["review"], [d["non_issues"][0]["text"]]),
}


async def main():
    prof = tempfile.mkdtemp(prefix="pm_practice_")
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
            p = U.Page(ws)
            asyncio.create_task(p.pump())
            for m in ("Page.enable", "Runtime.enable", "Network.enable"):
                await p.send(m)
            await p.send("Page.navigate", url=BASE + "/")
            await U.wait_boot(p)
            await asyncio.sleep(1.0)

            # 1. the page, and its place in the app
            await p.eval("location.hash = '#/practice'")
            check("practice page renders", await U.wait_for(p, "!!document.querySelector('#pr-start')", 15))
            check("page title is Practice", "Practice" in (await p.eval("document.querySelector('#view h1')?.textContent || ''")))
            await p.eval("document.querySelector('#btn-menu').click()")
            await asyncio.sleep(0.4)
            check("Practice is in the navigation drawer", await p.eval("!!document.querySelector('#side a[href=\"#/practice\"]')"))
            await p.eval("document.querySelector('#scrim').click()")
            await p.eval("document.querySelector('input[name=pr-scope][value=all]').click()")
            await p.eval("document.querySelector('#pr-start').click()")

            # 2. a whole session
            seen_types, solved_n, gave_up_n, hinted = set(), 0, 0, False
            for i in range(N_PROBLEMS):
                ok = await U.wait_for(p, "!!document.querySelector('.dr-card[data-pid]')", 15)
                check(f"problem {i + 1}: card appears", ok)
                if not ok:
                    break
                pid = await p.eval("document.querySelector('.dr-card[data-pid]').dataset.pid")
                day, d = drill_by_pid(pid)
                label = f"problem {i + 1} ({d['type']}, day {day})"
                seen_types.add(d["type"])
                text = await p.eval("document.querySelector('#view').innerText")
                check(f"{label}: topic is hidden (no title, no 'Day')", d["title"] not in text and "Day " + str(day) not in text.replace("Days I have", ""),
                      text[:120].replace("\n", " "))
                check(f"{label}: no drill title element", await p.eval("!document.querySelector('.dr-title')"))
                check(f"{label}: header shows number and level", f"problem {i + 1}" in text.lower() and "level" in text.lower())
                if i == 0:                                              # hint ladder: three steps, one at a time
                    for step in (1, 2, 3):
                        await p.eval("document.querySelector('#pr-hint').click()")
                        check(f"{label}: hint {step} appears", await U.wait_for(p, f"document.querySelectorAll('.pr-hint').length === {step}", 6))
                    check(f"{label}: hint button is disabled after 3", await p.eval("document.querySelector('#pr-hint').disabled"))
                    hinted = True
                    htxt = await p.eval("document.querySelector('.pr-hints').innerText")
                    check(f"{label}: hints do not reveal the title", d["title"] not in htxt)
                await p.eval("(() => { const t = document.querySelector('#pr-think'); t.value = 'my thinking for problem %d'; t.dispatchEvent(new Event('input')); })()" % (i + 1))
                await p.eval("document.querySelector('.pr-conf button[data-c=\"%d\"]').click()" % (1 + i % 3))
                if i == 2:                                              # give up on one
                    await p.eval("[...document.querySelectorAll('.dr-acts .btn')].find(b => /Show the answer/.test(b.textContent)).click()")
                    peeked = await U.wait_for(p, "!!document.querySelector('.dr-fb.peek')", 8)
                    check(f"{label}: 'Show the answer' reveals it", peeked)
                    gave_up_n += 1
                else:
                    if d["type"] in WRONG:
                        await p.eval(WRONG[d["type"]](d))
                        await p.eval("document.querySelector('.dr-acts .btn.primary').click()")
                        check(f"{label}: wrong answer gets 'Not quite'", await U.wait_for(p, "!!document.querySelector('.dr-fb.try')", 8))
                        await p.eval("document.querySelector('#pr-end') && 0")        # (no-op) keep the same card; fix the answer in place
                        if d["type"] in ("predict",):
                            await p.eval("document.querySelector('.dr-area').value = ''")
                        elif d["type"] == "bug":
                            await p.eval("document.querySelectorAll('.dr-line.sel').forEach(l => l.click())")
                        elif d["type"] == "review":
                            await p.eval("document.querySelectorAll('.dr-card .dr-opt input:checked').forEach(c => c.click())")
                    r = await p.eval(U.solver_call(d))
                    check(f"{label}: solver ran", r is True, str(r))
                    await p.eval("document.querySelector('.dr-acts .btn.primary').click()")
                    good = await U.wait_for(p, "!!document.querySelector('.dr-fb.good')", 8)
                    check(f"{label}: right answer accepted", good, (await p.eval("document.querySelector('.dr-card')?.innerText.slice(-240)")) or "")
                    solved_n += 1 if good else 0
                if i < 2 or d["type"] != "bug":
                    pass
                reveal = await p.eval("document.querySelector('.pr-reveal')?.innerText || ''")
                check(f"{label}: topic is revealed only after it ends", f"Day {day}" in reveal and d["title"] in reveal, reveal[:100])
                check(f"{label}: controls lock after it ends", await p.eval("document.querySelector('#pr-think').disabled"))
                for pr in p.problems():
                    check(f"{label}: no console/network problems", False, pr)
                await p.eval("[...document.querySelectorAll('.dr-fb .btn.primary')].pop().click()")
                await asyncio.sleep(0.25)
            check("a mix of problem types appeared", len(seen_types) >= 3, str(seen_types))
            check("hint ladder was exercised", hinted)

            # 3. end the session, read the summary
            check("the next problem loads after the last answer", await U.wait_for(p, "!!document.querySelector('#pr-end')", 15))
            await p.eval("document.querySelector('#pr-end').click()")
            check("summary appears", await U.wait_for(p, "/session finished/i.test(document.querySelector('#view').innerText)", 10))
            s = await p.eval("document.querySelector('#view').innerText")
            check("summary says how many were solved", f"{solved_n} of {N_PROBLEMS}" in s or "solved" in s, s[:200].replace("\n", " "))
            check("summary shows the calibration card", "Does feeling sure mean being right" in s)
            check("summary offers 'To revisit' for the missed one", "To revisit" in s)
            await U.wait_for(p, "true", 1)

            # 4. the same numbers show up elsewhere
            await p.eval("location.hash = '#/'")
            check("Home shows the practice card", await U.wait_for(p, "!!document.querySelector('#pr-home-card')", 12))
            await p.eval("location.hash = '#/insights'")
            check("Insights shows the calibration card", await U.wait_for(p, "!!document.querySelector('#pr-ins-card')", 12))
            await p.eval("location.hash = '#/practice'")
            await U.wait_for(p, "!!document.querySelector('#pr-start')", 10)
            ov = await p.eval("document.querySelector('#view').innerText")
            check("overview lists the session after reload of the page", "sessions" in ov and "problems" in ov, ov[:160].replace("\n", " "))
            for pr in p.problems():
                check("final: no console/network problems", False, pr)
    finally:
        proc.terminate()
    print(f"\n{checks} checks, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
