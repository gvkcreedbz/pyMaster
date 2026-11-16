"""Full-text search across everything in the course: lessons (by section), concept notes, guides, blueprints.

Powers the Ctrl+P command palette. No dependencies: a small in-memory index, built on first use.
"""
from __future__ import annotations

import re
from functools import lru_cache

from . import content
from .kb import KB

_HEAD = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.M)
_MD = re.compile(r"[`*_>#|]|\[(.*?)\]\(.*?\)")


def _plain(s: str) -> str:
    return re.sub(r"\s+", " ", _MD.sub(lambda m: m.group(1) or " ", s)).strip()


def _sections(markdown: str):
    """Yield (heading, body) for every ## / ### section (text before the first heading is skipped)."""
    marks = list(_HEAD.finditer(markdown))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(markdown)
        yield _plain(m.group(2)), _plain(markdown[m.end():end])


@lru_cache(maxsize=1)
def index() -> list[dict]:
    docs: list[dict] = []
    for n, d in content.load_days().items():
        title = re.sub(r"^🏆\s*", "", d["title"])
        docs.append({"type": "day", "title": f"Day {n} · {title}", "sub": d["goal"], "hash": f"#/day/{n}/learn",
                     "head": f"day {n} {title} {d['goal']}", "body": d["scenario"]})
        for head, body in _sections(d["lesson"]):
            if len(body) < 20 or head.lower().startswith(("quiz", "wrap", "stuck")):
                continue
            docs.append({"type": "lesson", "title": f"Day {n} · {head}", "sub": f"{title}", "hash": f"#/day/{n}/learn",
                         "head": head, "body": body})
        for q in d["quiz"]:
            docs.append({"type": "quiz", "title": f"Day {n} quiz {q['n']}", "sub": _plain(q["q"])[:90],
                         "hash": f"#/day/{n}/quiz", "head": "quiz question", "body": _plain(q["q"])})
    for e in KB:
        docs.append({"type": "concept", "title": e["name"], "sub": "Where and how it is used",
                     "hash": f"#/day/{e['days'][0]}/learn" if e["days"] else "#/",
                     "head": e["name"] + " " + " ".join(e["keys"]), "body": _plain(e["what"] + " " + e["where"])})
    for it in content.library():
        text = content.library_doc(it["id"]) or ""
        docs.append({"type": "guide", "title": it["title"], "sub": it["group"], "hash": "#/library/" + it["id"],
                     "head": it["title"], "body": _plain(text)})
    for bp in content.blueprint_list():
        text = content.blueprint_doc(bp["id"]) or ""
        docs.append({"type": "blueprint", "title": f"{bp['emoji']} {bp['title']}", "sub": bp["kind"],
                     "hash": "#/blueprints/" + bp["id"],
                     "head": " ".join([bp["title"], bp["kind"], *bp["stack"], *bp["patterns"]]), "body": _plain(text)})
        for head, body in _sections(text):
            if len(body) >= 30:
                docs.append({"type": "blueprint", "title": f"{bp['title']} · {head}", "sub": "Blueprint section",
                             "hash": "#/blueprints/" + bp["id"], "head": head, "body": body})
    for d in docs:
        d["_h"], d["_b"] = d["head"].lower(), d["body"].lower()
    return docs


def _snippet(body: str, low: str, term: str, width: int = 110) -> str:
    i = low.find(term)
    if i < 0:
        return body[:width]
    a = max(0, i - width // 3)
    return ("…" if a else "") + body[a:a + width] + ("…" if a + width < len(body) else "")


TYPE_BONUS = {"day": 4, "concept": 3, "blueprint": 2, "guide": 1, "lesson": 0, "quiz": -1}


def search(q: str, limit: int = 12) -> list[dict]:
    terms = [t for t in re.split(r"\s+", q.lower().strip()) if t]
    if not terms:
        return []
    scored = []
    for d in index():
        sc = 0.0
        for t in terms:
            in_h, in_b = t in d["_h"], t in d["_b"]
            if not (in_h or in_b):
                sc = 0
                break                                   # every word must appear somewhere
            if in_h:
                sc += 10 + (6 if re.search(r"(?<![a-z0-9])" + re.escape(t), d["_h"]) else 0)
            if in_b:
                sc += 1 + min(d["_b"].count(t), 5) * 0.2
        if sc:
            scored.append((sc + TYPE_BONUS.get(d["type"], 0), d))
    scored.sort(key=lambda x: -x[0])
    out, seen = [], set()
    for _sc, d in scored:
        key = (d["hash"], d["title"])
        if key in seen:
            continue
        seen.add(key)
        sub = _snippet(d["body"], d["_b"], terms[0]) if terms[0] in d["_b"] and d["type"] in ("lesson", "guide", "blueprint", "concept") else d["sub"]
        out.append({"type": d["type"], "title": d["title"], "sub": sub, "hash": d["hash"]})
        if len(out) >= limit:
            break
    return out
