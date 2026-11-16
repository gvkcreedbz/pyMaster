"""Simulates 40 minutes of watching three sites in a few milliseconds, using a fake clock and a fake internet.
Run: python demo.py          (standard library only)
"""
import tempfile
from pathlib import Path

from watcher import ConsoleNotifier, Watcher

TARGETS = [
    {"name": "laptop-price", "kind": "price", "url": "https://shop.example/laptop", "pattern": r"Price: \$([\d,\.]+)", "every": 300, "min_drop_pct": 5},
    {"name": "docs-page", "kind": "content", "url": "https://docs.example/changelog", "every": 600},
    {"name": "payments-api", "kind": "uptime", "url": "https://pay.example/health", "every": 120},
]


class FakeInternet:
    """A pretend web whose pages we can change minute by minute."""

    def __init__(self):
        self.now = 0.0
        self.calls = 0

    def fetch(self, url: str) -> str:
        self.calls += 1
        minute = self.now / 60
        if "shop.example" in url:
            price = 1299 if minute < 10 else 1099 if minute < 20 else 1089      # -15% at minute 10, tiny -1% at minute 20
            return f"<html>Laptop Pro   Price: ${price:,.2f}  In stock</html>"
        if "docs.example" in url:
            return "<h1>Changelog</h1> v1.0" if minute < 25 else "<h1>Changelog</h1> v1.1 released"
        if "pay.example" in url:
            if 12 <= minute < 28:                                                # outage from minute 12 to 28
                raise TimeoutError("connection timed out")
            return "ok"
        raise ValueError(url)


def main():
    net = FakeInternet()
    notifier = ConsoleNotifier()
    state_file = Path(tempfile.mkdtemp()) / "state.json"
    w = Watcher(TARGETS, net.fetch, [notifier], state_file)

    print("== 1. forty minutes pass, one tick per minute (fake clock)")
    for minute in range(0, 41):
        net.now = minute * 60
        before = len(notifier.sent)
        ran = w.tick(net.now)
        if len(notifier.sent) > before:
            print(f"   (minute {minute:>2}: {ran} check(s) ran)")

    print("\n== 2. what the dashboard would show")
    for name, s in w.status().items():
        print(f"   {name:<13} last={s['last']!s:<14} breaker={s['breaker']:<6} consecutive failures={s['failures']}")

    print("\n== 3. efficiency: the schedule and the breaker avoid pointless calls")
    print(f"   fake HTTP calls: {net.calls}  (checking every target every minute would be {41 * 3})")

    print("\n== 4. alerts are transitions, not noise")
    print(f"   {len(notifier.sent)} alerts in 40 minutes:", [t for t, _ in notifier.sent])

    print("\n== 5. restart the service: it remembers (atomic JSON state file)")
    w2 = Watcher(TARGETS, net.fetch, [notifier], state_file)
    print("   after restart, laptop-price last seen =", w2.state["laptop-price"])

    print("\n== 6. a layout change is reported as an error, not a wrong price")
    broken = Watcher([{**TARGETS[0], "pattern": r"Cost: \$([\d\.]+)"}], net.fetch, [notifier],
                     Path(tempfile.mkdtemp()) / "s.json")
    for i in range(3):
        broken.tick(i * 1000.0)
    print("   status:", broken.status())


if __name__ == "__main__":
    main()
