# Drills: authoring guide

A **drill** is a short exercise where you read, arrange, predict or review code instead of writing it from scratch.
Each day can have a `DRILLS.json` next to its `LESSON.md`:

* Python course: `days/dayNN_<topic>/DRILLS.json`
* Java course: `java/days/dayNN_<topic>/DRILLS.json`

Days with a file get a **Drills** tab in the portal (deep link `#/day/N/drills`). Days 1-3 of both courses are done and
are the best examples to copy. Aim for **5 drills per day, one of each type**, using only what that day (and earlier days) taught.

## Check your work

```
python _dev_tools/verify_drills.py 4            # one day, both tracks
python _dev_tools/verify_drills.py 4-6 --track java
python _dev_tools/verify_drills.py 4 --fix      # fill `expected` / `output` from the REAL run instead of typing it
python _dev_tools/verify_drills.py --lint-only  # structure only, instant
python -m pytest _dev_tools/test_ex_drills.py   # backend tests (set PORTAL_TRACK=java for the Java track)
```

`verify_drills.py` **runs your code** (real Python / JDK 21): predict snippets must print exactly `expected`, parsons
programs and filled-in programs must run and print `output`, buggy programs must fail the way `buggy_runs` says, and
wrong fix options must not also repair the program. Never type outputs by hand: write the code, run `--fix`, read the result.
`python _dev_tools/ui_drills_test.py` (via `ui_drills_both.ps1`) solves every drill through the real UI in Chrome.

## File shape

```json
{ "day": 4, "drills": [ { "id": "d04-parsons", "type": "parsons", "title": "...", "prompt": "...", "explain": "...", "concepts": ["..."], ... } ] }
```

Common keys: `id` (`d04-parsons`, unique, `[A-Za-z0-9_-]`), `type`, `title` (<= 80), `prompt` (<= 700, Markdown), `explain` (<= 1500,
shown after an attempt: say **why**, not just what), `concepts` (1-6 short names that match the day's concept headings),
optional `hint` (one nudge, not the answer), `viz: true` (offers the step-through visualizer on the finished code),
`norun: true` (skip execution; only for code that cannot run alone, avoid), `wrap: true` (Java only: wrap bare statements in a class).
Anywhere a multi-line string is expected you may write a **list of lines** instead. Code lines <= 110 chars, spaces not tabs, <= 40 lines.

## The five types

### `parsons`: arrange the lines
```json
{ "type": "parsons", "lines": ["total = 0", "for p in prices:", "total += p", "print(total)"],
  "indent": [0, 0, 1, 0], "distractors": ["total == 0"], "output": "..." }
```
* `lines` = the correct order, no leading spaces (give nesting in `indent`, 0-5). 3-14 lines. Python lines ending in `:` need `indent`.
* Java: indentation is not checked; braces are real lines and must balance. Put `{`/`}` lines in `lines`.
* `distractors` (0-4): plausible wrong lines (typos, wrong case, wrong operator). Never equal to a real line.
* `alternatives`: other valid permutations (lists of indexes into `lines`) when order is genuinely free. verify runs them.
* **Faded** (`"faded": true`): put `___` in some lines and give `blanks` (one per `___`, in order), each with `answers` and `options` (2-6, must contain the first answer).
* `output` = what the finished program prints (`--fix` fills it).

### `fill`: fill the blanks
```json
{ "type": "fill", "code": ["name = ___", "print(___ + name)"],
  "blanks": [ {"answers": ["\"Asha\""]}, {"answers": ["\"Hi \""], "options": ["\"Hi \"", "Hi", "'Hi'"]} ], "output": "..." }
```
* One entry in `blanks` per `___` (1-8). `answers` = accepted strings (whitespace-insensitive). Optional `regex` (must match every answer), optional `options` (dropdown, must include `answers[0]`).
* verify runs the program with every accepted answer, and with every wrong option: a wrong option that also works is reported (ambiguous blank).

### `predict`: what does it print?
```json
{ "type": "predict", "code": ["x = 7", "print(x // 2, x % 2)"], "expected": "3 1" }
```
* Code runs to completion with exit code 0. `expected` is real output (`--fix`). Optional `stdin`. Keep output <= 800 chars.
* Best drills expose a common misconception: integer vs float division, `==` vs `.equals`, off-by-one, mutation through an alias.

### `bug`: find the bug
```json
{ "type": "bug", "code": ["..."], "fixed_code": ["..."], "bug_lines": [2], "options": ["fix A", "fix B", "fix C"], "answer": 0,
  "buggy_runs": {"fails": true, "contains": "NameError"}, "output": "..." }
```
* `fixed_code` has **the same number of lines** as `code`; only the bug lines differ, and `bug_lines` lists exactly those (1-3, 1-based).
* `options`: 3-4 fixes, `options[answer]` equals the fixed line(s). Wrong options must be believable (and must not also fix the program).
* `buggy_runs`: `{"fails": true, "contains": "<text in the error>"}` when the buggy code crashes / fails to compile; `{"fails": false, "output": "<wrong output>"}` when it runs but is wrong.

### `review`: review AI-written code
```json
{ "type": "review", "code": ["..."], "issues": [ {"id": "i1", "text": "...", "why": "...", "lines": [3]} ], "non_issues": [ {"id": "n1", "text": "...", "why": "..."} ] }
```
* Code that an assistant might plausibly produce: it **runs** and looks fine. 2-4 real `issues` (off-by-one, mutable default, unchecked `None`/null, resource leak, SQL built from strings, swallowed exception, O(n^2) in a loop, unsafe `==`), 2-5 `non_issues` that look suspicious but are fine. Every item needs `id`, `text` (<= 200), `why` (<= 600; explains the verdict), optional `lines`.
* Only use problems the learner can understand by this day. Day 1-3 reviews are about naming, magic numbers, wrong types, silent assumptions.

## Quality rules

1. **One idea per drill**, taken from that day's lesson and exercises. Use the lesson's scenario (chai shop, bill splitter, ...).
2. Python and Java versions of a day should teach the same ideas but be written in each language, not translated line by line.
3. Distractors and wrong options must look like mistakes a beginner really makes; avoid trick questions and unfair syntax traps.
4. `explain` names the rule behind the answer and points to what to look for next time.
5. No answers leak into the list endpoint (the tests check this); never rely on secrecy of `id`s.
6. Run `verify_drills.py` for your days **on both tracks** and `test_ex_drills.py`, and fix every report before committing.
