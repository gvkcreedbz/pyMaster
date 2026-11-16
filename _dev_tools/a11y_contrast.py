"""WCAG contrast check of the portal's colour variables (light + dark), after the a11y.css overrides.
Run:  python _dev_tools/a11y_contrast.py          exit code 1 if any text pair is below 4.5:1 (large/UI pairs: 3:1)
      python _dev_tools/a11y_contrast.py --base   check app.css alone (shows what a11y.css had to fix)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "portal" / "static"

# (foreground var, background var, minimum ratio, what it is)
PAIRS = [
    ("ink", "bg", 4.5, "body text"), ("ink", "panel", 4.5, "text on cards"), ("ink-2", "bg", 4.5, "secondary text"),
    ("ink-2", "panel", 4.5, "secondary text on cards"), ("ink-2", "panel-2", 4.5, "secondary text on chips"),
    ("muted", "bg", 4.5, "hint text"), ("muted", "panel", 4.5, "hint text on cards"), ("muted", "panel-2", 4.5, "hint text on chips/kbd"),
    ("muted", "gutter", 4.5, "line numbers"), ("muted", "code-bg", 4.5, "muted text in code areas"),
    ("accent", "bg", 4.5, "links / accent text"), ("accent", "panel", 4.5, "accent text on cards"),
    ("accent", "accent-soft", 4.5, "accent chip"), ("accent-ink", "accent", 4.5, "primary button label"),
    ("good", "good-soft", 4.5, "good chip"), ("good", "panel", 4.5, "good text on cards"),
    ("warn", "warn-soft", 4.5, "warn chip"), ("warn", "panel", 4.5, "warn text on cards"),
    ("bad", "bad-soft", 4.5, "bad chip"), ("bad", "panel", 4.5, "error text on cards"),
    ("bg", "ink", 4.5, "toast text"),
    ("tk-kw", "code-bg", 4.5, "code: keyword"), ("tk-str", "code-bg", 4.5, "code: string"), ("tk-num", "code-bg", 4.5, "code: number"),
    ("tk-com", "code-bg", 4.5, "code: comment"), ("tk-def", "code-bg", 4.5, "code: definition"), ("tk-bi", "code-bg", 4.5, "code: builtin"),
    ("tk-op", "code-bg", 4.5, "code: operator"),
    ("accent", "bg", 3.0, "focus outline / UI boundary"),
]


def parse_vars(css: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {"light": {}, "dark": {}}
    for m in re.finditer(r"(:root:not\(\[data-theme=\"dark\"\]\)|:root|\[data-theme=\"dark\"\])\s*\{(.*?)\}", css, re.S):
        theme = "dark" if m.group(1).startswith("[") else "light"
        for k, v in re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*[;}\s]", m.group(2) + ";"):
            out[theme][k] = v
    return out


def rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def lum(h: str) -> float:
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def load(base_only: bool) -> dict[str, dict[str, str]]:
    v = parse_vars((STATIC / "app.css").read_text(encoding="utf-8"))
    extra = STATIC / "css" / "extras" / "a11y.css"
    if not base_only and extra.is_file():
        o = parse_vars(extra.read_text(encoding="utf-8"))
        for t in v:
            v[t].update(o[t])
    return v


def check(base_only: bool = False) -> list[str]:
    v = load(base_only)
    bad = []
    for theme, vars_ in v.items():
        for fg, bg, need, what in PAIRS:
            if fg not in vars_ or bg not in vars_:
                continue
            r = ratio(vars_[fg], vars_[bg])
            flag = "" if r >= need else f"   <-- below {need}:1"
            print(f"{theme:5} {fg:10} on {bg:11} {r:5.2f}  {what}{flag}")
            if r < need:
                bad.append(f"{theme}: {fg} {vars_[fg]} on {bg} {vars_[bg]} = {r:.2f} (< {need}) {what}")
    return bad


if __name__ == "__main__":
    problems = check("--base" in sys.argv)
    print(f"\n{len(problems)} pair(s) below the WCAG minimum")
    sys.exit(1 if problems else 0)
