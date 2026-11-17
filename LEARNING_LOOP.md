# Learning loop: what we took from LearnHarness, and what we left out

[LearnHarness](https://github.com/amosblomqvist/learnharness) is an open-source desktop app (AGPL-3.0) that uses AI agents to
plan and teach any subject. This page compares its documented features with Py Master / Java Master and records what was
built here. Everything below was written from its public descriptions (README, learnharness.ai, "Getting started");
**no LearnHarness code was copied**, so it does not affect this project's licence.

The two projects start from different places. LearnHarness has no fixed course: an agent invents the lesson for any topic.
Py Master / Java Master are fixed, tested 30-day courses that work **fully offline**, and the AI tutor is optional. So ideas
were adopted only where they work without an AI, and an AI makes them better when one is connected.

| LearnHarness feature | Py Master / Java Master | Status |
|---|---|---|
| **Probe**: find where your understanding ends before teaching | Practice sessions measure it per problem (accuracy, hints, confidence); a pre-day check is not built | partly |
| **Plan**: a dependency map from where you are to your goal | 30-day plan, weekly milestones, "Today" card, spaced-review queue; goal-based fast tracks | partly built; goal paths planned |
| **Teach**: predict, then explain, then check, one step at a time | Lessons + code-along. **Predict before you run** on every runnable example | **built** |
| **Check** for understanding, errors repaired immediately | Quiz, drills with explanations, "Not quite" feedback | built (earlier) |
| **Practice**: varied problems where the right knowledge must come to mind *unprompted* | **Practice sessions**: mixed problems from every day you have reached, no concept names shown, no title | **built** |
| Problems adapt: hard enough to struggle, not too hard to progress | Level 1-5 moves up after 3 clean answers in a row, down after 2 misses; missed problems come back | **built** |
| **Smallest hint that unblocks** without replacing your thinking | Three-step hint ladder per problem (which idea, a nudge, a narrowing); using hints is recorded | **built** |
| **Thinking fields**: explain your reasoning, not just the answer | Optional "think out loud" box on every practice problem and drill | **built** |
| Self-reported **confidence** | Not sure / Fairly sure / Certain; **calibration** card in Insights (confident-and-wrong = likely misconception) | **built** |
| **Dictation** (Deepgram key) | Microphone button using the browser's built-in speech recognition; no key | **built** (Chrome/Edge) |
| Result revealed at the end, "Next problem" | The model solution and explanation appear when a problem ends | **built** |
| **Knowledge graph** that carries across sessions | A concept map: every concept of the course, joined by what builds on what, coloured by what you have practised and what is due | planned |
| Import notes into the graph | Import `.md` / `.txt` notes, searchable from `Ctrl+P` | planned |
| Attach files (paperclip, drag and drop) | Attach a text/code file to a tutor question | planned |
| Custom OpenAI-compatible endpoint / local model | Add an endpoint URL + model (Ollama, LM Studio, ...) as a tutor provider | planned |
| Visible, editable **system prompts** | "Tutor instructions" box in Settings, and a "show the full prompt" view | planned |
| **Session stats / cost meter** | Tokens and AI-call count per session in the tutor panel | planned |
| Learning records are plain files you can inspect | `/api/export` (JSON) today; Markdown export planned | partly |
| **Themes** file format | Light / dark today; extra presets planned | partly |
| Keyboard shortcuts doc + rebinding | Shortcuts overlay planned; rebinding not planned | partly |
| **Plugins** (trusted local plugins) | `portal/ext.py`: drop-in extensions (`ex_*.py`, `static/js/extras/*.js`), already used by backups, drills, XP and practice | **built** |
| Interactive demonstrations | Step-through visualizer and flow charts today; small live "change a value" widgets planned | partly |
| Annotated images, show-your-own-images | Not planned (needs a vision model) | skipped |
| Web research subagents, search providers | Not planned: the portal is local-only by design | skipped |
| Desktop installers, in-app updates, subscriptions sign-in | Not applicable: `start_app.bat` runs it from a folder; update with `git pull` | skipped |

Honest limits: LearnHarness builds its picture of you with an AI reading your free-text thinking. Here the thinking text and
confidence are recorded and used by simple, inspectable rules (accuracy, confidence vs. correctness, hint use, time), and are
passed to the AI tutor when one is connected. That is a smaller idea than theirs, not the same one.
