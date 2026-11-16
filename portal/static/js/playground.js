// The playground pane: always mounted beside the lesson, so copying code from a lesson never means leaving it.
import { $, debounce, editor, toast } from './util.js';
import { mountRunner } from './runpanel.js';
import * as tutor from './tutor.js';
import * as layout from './layout.js';
import * as sync from './sync.js';
import { openVisualizer } from './visualizer.js';

const SAMPLE = `# Playground: try anything. Ctrl+Enter runs it.
# Click "Try" on any code in a lesson and it lands here.
# Course datasets live at ../../datasets/ (e.g. ../../datasets/sales.csv)

orders = [("Priya", 499.0), ("Raj", 1299.5), ("Ana", 89.9)]

total = 0
for name, amount in orders:
    total += amount
    print(f"{name:<8} {amount:>8.2f}")

print("-" * 17)
print(f"{'Total':<8} {total:>8.2f}")
`;

let cm = null, runner = null;
const KEY = 'pm-play-code';

export function mount() {
  const host = $('#pg');
  host.innerHTML = `<div class="pg-ed" id="pg-ed"></div><div class="pg-run" id="pg-rp"></div>`;
  const start = localStorage.getItem(KEY) ?? localStorage.getItem('pj-play-code') ?? SAMPLE;
  const save = debounce(v => localStorage.setItem(KEY, v), 500);
  cm = editor($('#pg-ed'), { value: start, onChange: save, onRun: () => runner.run(), onSelection: t => tutor.setSelection(t) });
  runner = mountRunner($('#pg-rp'), { kind: 'playground', getCode: () => cm.getValue(), label: 'Run' });
  const add = (txt, fn, title) => { const b = document.createElement('button'); b.className = 'btn ghost sm'; b.innerHTML = txt; b.title = title || ''; b.onclick = fn; runner.slot.appendChild(b); };
  add('&#128065; Visualize', () => openVisualizer({ code: cm.somethingSelected() ? cm.getSelection() : cm.getValue(), lang: 'python' }), 'Step through this code and see it as a diagram');
  add('&#10022; Explain', () => { tutor.markFocus('play'); tutor.ask('', 'Explain what this code does, step by step, in simple words, and where code like this is used in real jobs.'); });
  add('Review', () => { tutor.markFocus('play'); tutor.ask('review'); });
  add('New', () => { cm.setValue(''); cm.focus(); });
  tutor.setPlay({ getCode: () => cm.getValue(), getOutput: runner.getOutput });
  cm.refresh();
}

export const getCode = () => cm?.getValue() ?? '';
/** After the playground window is docked back, pick up whatever was typed there. */
export function reload() {
  const v = localStorage.getItem(KEY);
  if (cm && v != null && v !== cm.getValue()) cm.setValue(v);
}
export function setCode(code, { focus = true } = {}) {
  if (!cm) return;
  cm.setValue(code); localStorage.setItem(KEY, code);
  if (focus) { cm.focus(); cm.setCursor(cm.lastLine(), 0); }
  layout.refreshEditors();
}

/** "Try" on a code block anywhere in the app. */
export function tryCode(code) {
  if (layout.PANE !== 'play' && layout.isPopped('play')) {
    sync.send('try', { code }); layout.focusPopped('play'); toast('Sent to the playground window'); return;
  }
  if (layout.PANE === 'lesson' || layout.PANE === 'tutor') {            // this window has no playground: hand it to the main window
    sync.send('try', { code }); toast('Sent to the playground'); return;
  }
  layout.showPane('play'); setCode(code); toast('Code is in the playground. Press Ctrl+Enter to run it.');
}

document.addEventListener('pm:try', e => tryCode(e.detail.code));
sync.on('try', m => {
  if (layout.PANE === 'play' || (!layout.PANE && !layout.isPopped('play'))) {
    layout.showPane('play'); setCode(m.code); toast('Code received in the playground');
  }
});
