// Drills: five short exercise types besides "write code": arrange the lines (Parsons), fill the blanks, predict the output,
// find the bug, and review AI-written code. Backend: portal/ex_drills.py (/api/drills/*). Data: DRILLS.json per day.
// Adds a "Drills" tab to every day that has drills (deep link: #/day/N/drills).
import { wrapJava } from '/static/js/util.js';

let C, summary = { days: {} };
const TYPE_NAME = { parsons: 'Arrange', fill: 'Fill the blanks', predict: 'Predict the output', bug: 'Find the bug', review: 'Review AI code' };

function el(tag, attrs = {}, kids = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else if (k === 'html') e.innerHTML = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of [].concat(kids)) if (c != null) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
}
const hl = (node, text) => { if (window.CodeMirror?.runMode) CodeMirror.runMode(text || ' ', C.TRK.cm_mode, node); else node.textContent = text || ' '; return node; };
/** Syntax-highlighted code with optional line numbers and per-line click handler. */
function codeBox(code, { numbers = true, onPick } = {}) {
  const box = el('div', { class: 'dr-code', role: onPick ? 'group' : null, 'aria-label': onPick ? 'Code. Press a line to select it.' : null });
  const lines = String(code).replace(/\n$/, '').split('\n');
  lines.forEach((ln, i) => {
    const row = el('div', { class: 'dr-line' + (onPick ? ' pick' : ''), 'data-n': i + 1, tabindex: onPick ? 0 : null, role: onPick ? 'button' : null, 'aria-pressed': onPick ? 'false' : null });
    if (numbers) row.append(el('span', { class: 'no', text: String(i + 1) }));
    row.append(hl(el('span', { class: 'tx' }), ln));
    if (onPick) {
      const go = () => onPick(i + 1, row);
      row.addEventListener('click', go);
      row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
    }
    box.append(row);
  });
  return box;
}
const sidOf = () => C.store.sid;

// ---- the tab -------------------------------------------------------------------------------------------------------
async function render(body, d, label) {
  C.tutor.setContext({ dayNo: d.n, tab: 'drills', label: label + ' · Drills' });
  body.innerHTML = '<div class="muted">Loading drills…</div>';
  let data;
  try { data = await C.api(`/drills/${d.n}?session_id=${encodeURIComponent(sidOf() || '')}`); }
  catch (e) { body.innerHTML = `<div class="dr-empty-day">Could not load the drills (${C.esc(e.message)}).</div>`; return; }
  const drills = data.drills;
  if (!drills.length) { body.innerHTML = '<div class="dr-empty-day">No drills for this day yet.</div>'; return; }
  let cur = Math.max(0, drills.findIndex(x => !x.state.solved && !x.state.gave_up));
  const root = el('div', { class: 'dr' });
  body.replaceChildren(root);
  const paint = () => {
    root.replaceChildren(
      el('p', { class: 'sub', style: 'margin-top:0', text: 'Short exercises where you read, arrange, predict and review code instead of writing it from scratch. Wrong answers are fine: they are how you learn what to look for.' }),
      el('div', { class: 'dr-dots', role: 'tablist', 'aria-label': 'Drills' }, drills.map((x, i) => el('button', {
        class: 'dr-dot' + (i === cur ? ' on' : '') + (x.state.solved ? ' solved' : x.state.gave_up ? ' peeked' : ''), type: 'button', role: 'tab',
        'aria-selected': String(i === cur), title: `${TYPE_NAME[x.type]}: ${x.title}${x.state.solved ? ' (solved)' : ''}`, text: String(i + 1),
        onclick: () => { cur = i; paint(); } }))),
      drillCard(d, drills[cur], () => { if (cur < drills.length - 1) { cur++; paint(); } else paint(); }, paint));
  };
  paint();
}

function drillCard(d, v, next, repaint) {
  const card = el('div', { class: 'card dr-card' });
  card.append(el('span', { class: 'dr-type', text: TYPE_NAME[v.type] }), el('h3', { class: 'dr-title', text: v.title }));
  card.append(el('p', { class: 'dr-prompt', html: C.md(v.prompt, true).replace(/^<p>|<\/p>\s*$/g, '') }));
  if (v.state.solved) card.append(el('div', { class: 'dr-fine', text: 'You solved this one before. Try it again if you like.' }));
  const fb = el('div', { 'aria-live': 'polite' });
  const acts = el('div', { class: 'dr-acts' });
  const builders = { parsons, fill, predict, bug, review };
  const q = builders[v.type](card, v);                 // -> { answer(), mark(res), reveal(solution) }
  card.append(acts, fb);

  let tries = 0, done = false;
  const check = el('button', { class: 'btn primary', type: 'button', text: 'Check' });
  const hint = v.hint ? el('button', { class: 'btn ghost sm', type: 'button', text: 'Hint', onclick: () => {
    if (!card.querySelector('.dr-hint')) acts.after(el('p', { class: 'dr-hint', text: 'Hint: ' + v.hint })); } }) : null;
  const give = el('button', { class: 'btn ghost sm', type: 'button', text: 'Show the answer', onclick: async () => {
    try { const r = await C.api(`/drills/${d.n}/${v.id}/giveup`, { method: 'POST', body: { session_id: sidOf() } }); v.state.gave_up = true; finish(r, false); }
    catch (e) { C.toast('Could not load the answer: ' + e.message); } } });
  const ask = el('button', { class: 'btn ghost sm', type: 'button', text: 'Ask the tutor', onclick: () => {
    C.tutor.toggle?.(true);
    C.tutor.ask('', `I'm working on the "${v.title}" drill (${TYPE_NAME[v.type]}) in Day ${d.n}. ${tries ? 'My answer was not right yet. ' : ''}Help me think it through without giving the answer away.`); } });
  acts.append(check, ...(hint ? [hint] : []), give, ask);

  function finish(r, solved) {
    done = true;
    fb.replaceChildren();
    const box = el('div', { class: 'dr-fb ' + (solved ? 'good' : 'peek') });
    box.append(el('b', { text: solved ? (tries === 1 ? 'Correct on the first try.' : `Correct after ${tries} tries.`) : 'Here is the answer.' }));
    if (r.explain) box.append(el('div', { html: C.md(r.explain, true).replace(/^<p>|<\/p>\s*$/g, '') }));
    const sol = el('div', { class: 'dr-sol' });
    q.reveal(r.solution || {}, sol);
    if (sol.childNodes.length) box.append(sol);
    const row = el('div', { class: 'dr-acts' });
    const code = r.solution?.code;
    if (v.viz && code) row.append(el('button', { class: 'btn ghost sm', type: 'button', text: '👁 Visualize', onclick: () => C.openVisualizer({ code: wrapJava(code), lang: C.TRK.fence, dayNo: d.n }) }));
    row.append(el('button', { class: 'btn primary sm', type: 'button', text: 'Next drill →', onclick: () => { refreshSummary(); next(); } }));
    box.append(row);
    fb.append(box);
    if (solved) v.state.solved = true;
    const dot = document.querySelector('.dr-dot.on');                      // show the result on the dot right away
    if (dot && !dot.classList.contains('solved')) { dot.classList.remove('peeked'); dot.classList.add(solved ? 'solved' : 'peeked'); }
    check.disabled = true; give.disabled = true;
    box.scrollIntoView?.({ block: 'nearest', behavior: 'smooth' });
  }
  check.onclick = async () => {
    if (done) return;
    let answer;
    try { answer = q.answer(); } catch (e) { C.toast(e.message); return; }
    check.disabled = true;
    try {
      const r = await C.api(`/drills/${d.n}/${v.id}/check`, { method: 'POST', body: { answer, session_id: sidOf() } });
      tries += 1; v.state.attempts = r.attempts;
      q.mark(r);
      if (r.ok) finish(r, true);
      else {
        fb.replaceChildren(el('div', { class: 'dr-fb try' }, [el('b', { text: `Not quite yet (${Math.round(r.score * 100)}% right).` }), el('div', { text: q.tip(r) }),
          r.explain && tries >= 2 ? el('div', { class: 'dr-fine', text: 'Stuck? Use Hint, Ask the tutor, or Show the answer. All are fine.' }) : null]));
        check.disabled = false;
      }
    } catch (e) { check.disabled = false; C.toast(/stale/.test(e.message) ? 'This drill changed. Reloading it…' : 'Could not check: ' + e.message); if (/stale/.test(e.message)) repaint(); }
  };
  return card;
}

// ---- type: arrange (Parsons, optionally faded) -----------------------------------------------------------------------
function parsons(card, v) {
  const pool = v.items.map(it => ({ ...it, indent: 0, in: false }));
  const placed = [];
  const poolZone = el('div', { class: 'dr-zone', 'data-zone': 'pool', role: 'list', 'aria-label': 'Lines to use' });
  const progZone = el('div', { class: 'dr-zone', 'data-zone': 'prog', role: 'list', 'aria-label': 'Your program' });
  const blankVals = {};
  const marks = { lines: [], blanks: {} };
  const move = (arr, i, d) => { const j = i + d; if (j < 0 || j >= arr.length) return; [arr[i], arr[j]] = [arr[j], arr[i]]; };
  function piece(it, where, idx) {
    const p = el('div', { class: 'dr-piece', draggable: 'true', role: 'listitem', 'data-id': it.id, tabindex: 0 });
    if (where === 'prog') {
      p.style.marginLeft = (v.check_indent ? it.indent * 22 : 0) + 'px';
      const m = marks.lines[idx]; if (m) p.classList.add(m === 'ok' ? 'good' : 'bad');
    }
    const tx = el('span', { class: 'tx' });
    const parts = it.text.split('___');
    parts.forEach((t, k) => {
      tx.append(hl(el('span'), t));
      if (k < parts.length - 1) {
        const b = it.blanks[k];
        const s = el('select', { class: 'dr-blank' + (marks.blanks[b?.id] === true ? ' good' : marks.blanks[b?.id] === false ? ' bad' : ''), 'aria-label': 'Choose the missing part' },
          [el('option', { value: '', text: '…' }), ...(b?.options || []).map(o => el('option', { value: o, text: o }))]);
        s.value = blankVals[b.id] || '';
        s.onchange = () => { blankVals[b.id] = s.value; };
        tx.append(s);
      }
    });
    p.append(tx);
    const btn = (txt, title, fn) => p.append(el('button', { class: 'mini', type: 'button', title, 'aria-label': title, text: txt, onclick: e => { e.stopPropagation(); fn(); } }));
    if (where === 'pool') btn('→', 'Add to your program', () => { it.in = true; placed.push(it); paint(); });
    else {
      if (v.check_indent) { btn('⇤', 'Less indent', () => { it.indent = Math.max(0, it.indent - 1); marks.lines = []; paint(); }); btn('⇥', 'More indent', () => { it.indent = Math.min(6, it.indent + 1); marks.lines = []; paint(); }); }
      btn('↑', 'Move up', () => { move(placed, idx, -1); marks.lines = []; paint(); }); btn('↓', 'Move down', () => { move(placed, idx, 1); marks.lines = []; paint(); });
      btn('✕', 'Remove', () => { it.in = false; it.indent = 0; placed.splice(idx, 1); marks.lines = []; paint(); });
    }
    p.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', it.id); e.dataTransfer.effectAllowed = 'move'; });
    return p;
  }
  function paint() {
    poolZone.replaceChildren(...pool.filter(x => !x.in).map(x => piece(x, 'pool')), ...(pool.every(x => x.in) ? [el('div', { class: 'dr-empty', text: 'All lines are in your program.' })] : []));
    progZone.replaceChildren(...placed.map((x, i) => piece(x, 'prog', i)), ...(placed.length ? [] : [el('div', { class: 'dr-empty', text: 'Add the lines here, in order. Some lines may not belong in the program at all.' })]));
  }
  const dropOn = (zone, fn) => {
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('over'));
    zone.addEventListener('drop', e => { e.preventDefault(); zone.classList.remove('over'); const id = e.dataTransfer.getData('text/plain'); const it = pool.find(x => x.id === id); if (it) { fn(it, e); marks.lines = []; paint(); } });
  };
  dropOn(progZone, (it, e) => {
    const old = placed.indexOf(it); if (old >= 0) placed.splice(old, 1);
    const target = e.target.closest('.dr-piece'); let at = placed.length;
    if (target) { const t = placed.findIndex(x => x.id === target.dataset.id); if (t >= 0) at = t; }
    it.in = true; placed.splice(at, 0, it);
  });
  dropOn(poolZone, it => { const old = placed.indexOf(it); if (old >= 0) placed.splice(old, 1); it.in = false; it.indent = 0; });
  card.append(el('div', { class: 'dr-cols' }, [el('div', { class: 'dr-col' }, [el('h5', { text: 'Lines to use' }), poolZone]), el('div', { class: 'dr-col' }, [el('h5', { text: 'Your program' }), progZone])]));
  card.append(el('div', { class: 'dr-fine', text: 'Drag lines, or use the arrow buttons.' + (v.check_indent ? ' Indentation counts.' : '') }));
  paint();
  return {
    answer() {
      if (!placed.length) throw new Error('Add some lines to your program first.');
      if (v.faded) { const need = placed.flatMap(x => x.blanks.map(b => b.id)); if (need.some(id => !blankVals[id])) throw new Error('Pick a value for every blank.'); }
      return { order: placed.map(x => x.id), indents: placed.map(x => x.indent), blanks: v.faded ? blankVals : undefined };
    },
    mark(r) { marks.lines = r.feedback.lines || []; marks.blanks = r.feedback.blanks || {}; paint(); },
    tip(r) {
      const f = r.feedback, bad = (f.lines || []).filter(m => m !== 'ok');
      if (f.missing) return `${f.missing} line${f.missing > 1 ? 's are' : ' is'} still missing from your program.`;
      if ((f.lines || []).includes('distractor')) return 'One of the lines does not belong in this program. Check the red ones.';
      if ((f.lines || []).includes('indent')) return 'The order is close. Check the indentation of the red lines.';
      return bad.length ? 'Some lines are in the wrong place (red). Think about what has to happen first.' : 'Check the blanks.';
    },
    reveal(s, host) { if (s.code) host.append(codeBox(s.code)); },
  };
}

// ---- type: fill the blanks ---------------------------------------------------------------------------------------------
function fill(card, v) {
  const box = el('div', { class: 'dr-code' });
  const inputs = [];
  String(v.code).replace(/\n$/, '').split('\n').forEach((ln, i) => {
    const row = el('div', { class: 'dr-line' }, [el('span', { class: 'no', text: String(i + 1) })]);
    const tx = el('span', { class: 'tx' });
    ln.split('___').forEach((t, k, a) => {
      tx.append(hl(el('span'), t));
      if (k < a.length - 1) {
        const b = v.blanks[inputs.length];
        const inp = b.options ? el('select', { class: 'dr-blank', 'aria-label': `Blank ${inputs.length + 1}` }, [el('option', { value: '', text: '…' }), ...b.options.map(o => el('option', { value: o, text: o }))])
          : el('input', { class: 'dr-blank', type: 'text', 'aria-label': `Blank ${inputs.length + 1}`, size: Math.max(4, b.size + 1), autocomplete: 'off', spellcheck: 'false' });
        inputs.push(inp); tx.append(inp);
      }
    });
    row.append(tx); box.append(row);
  });
  card.append(box);
  return {
    answer() { if (inputs.some(i => !i.value.trim())) throw new Error('Fill in every blank first.'); return { blanks: inputs.map(i => i.value) }; },
    mark(r) { (r.feedback.blanks || []).forEach((ok, i) => { inputs[i].classList.toggle('good', !!ok); inputs[i].classList.toggle('bad', !ok); }); },
    tip(r) { const n = (r.feedback.blanks || []).filter(x => !x).length; return `${n} blank${n === 1 ? ' is' : 's are'} not right yet (red). Read the line out loud: what must go there?`; },
    reveal(s, host) { if (s.code) host.append(codeBox(s.code)); },
  };
}

// ---- type: predict the output ----------------------------------------------------------------------------------------------
function predict(card, v) {
  card.append(codeBox(v.code));
  if (v.stdin) card.append(el('div', { class: 'dr-fine', text: 'The program is given this input: ' + v.stdin.replace(/\n/g, ' ⏎ ') }));
  const ta = el('textarea', { class: 'dr-area', 'aria-label': 'What the program prints, line by line', placeholder: 'Type exactly what it prints, one line per line. Run it in your head first.', spellcheck: 'false' });
  card.append(ta);
  return {
    answer() { if (!ta.value.trim()) throw new Error('Type what you think it prints first.'); return { text: ta.value }; },
    mark() {},
    tip(r) { const l = r.feedback.lines || []; const bad = l.map((ok, i) => (ok ? 0 : i + 1)).filter(Boolean);
      return bad.length ? `Line${bad.length > 1 ? 's' : ''} ${bad.join(', ')} of your answer ${bad.length > 1 ? 'differ' : 'differs'}. Trace the variables one line at a time.`
        : `The program prints ${r.feedback.expected_lines} line${r.feedback.expected_lines === 1 ? '' : 's'}. Check how many yours has.`; },
    reveal(s, host) { if (s.output != null) host.append(el('div', { class: 'dr-fine', text: 'It prints:' }), codeBox(s.output, { numbers: false })); },
  };
}

// ---- type: find the bug ----------------------------------------------------------------------------------------------------
function bug(card, v) {
  const picked = new Set();
  const box = codeBox(v.code, { onPick: (n, row) => { picked.has(n) ? picked.delete(n) : picked.add(n); row.classList.toggle('sel', picked.has(n)); row.setAttribute('aria-pressed', String(picked.has(n))); } });
  card.append(el('div', { class: 'dr-fine', text: `Select the buggy line${v.n_bugs > 1 ? 's (' + v.n_bugs + ')' : ''}, then pick the right fix.` }), box);
  let option = null;
  const opts = el('div', { class: 'dr-opts', role: 'radiogroup', 'aria-label': 'Which fix is right?' }, v.options.map(o => {
    const r = el('input', { type: 'radio', name: 'opt-' + v.id, value: o.id, onchange: () => { option = o.id; } });
    return el('label', { class: 'dr-opt', 'data-id': o.id }, [r, el('span', { class: 'mono', text: o.text })]);
  }));
  card.append(opts);
  return {
    answer() { if (!picked.size) throw new Error('Select the line you think is wrong.'); if (!option) throw new Error('Pick a fix too.'); return { lines: [...picked], option }; },
    mark(r) {
      const f = r.feedback;
      box.querySelectorAll('.dr-line').forEach(row => { const n = +row.dataset.n; row.classList.remove('good', 'bad'); if (picked.has(n)) row.classList.add((f.right || []).includes(n) ? 'good' : 'bad'); });
      opts.querySelectorAll('.dr-opt').forEach(o => o.classList.remove('good', 'bad'));
      if (option) opts.querySelector(`[data-id="${option}"]`)?.classList.add(f.option_ok ? 'good' : 'bad');
    },
    tip(r) { const f = r.feedback; const a = [];
      if (!f.lines_ok) a.push(f.wrong.length ? 'Some selected lines are fine (red).' : `You have not found all the buggy lines yet (${f.missed} missing).`);
      if (!f.option_ok) a.push('The fix you picked is not the right one.');
      return a.join(' '); },
    reveal(s, host) { host.append(el('div', { class: 'dr-fine', text: `The bug is on line${(s.lines || []).length > 1 ? 's' : ''} ${(s.lines || []).join(', ')}. Right fix: ${s.fix}` })); if (s.code) host.append(el('div', { class: 'dr-fine', text: 'Fixed program:' }), codeBox(s.code)); },
  };
}

// ---- type: review AI-written code -------------------------------------------------------------------------------------------
function review(card, v) {
  card.append(codeBox(v.code), el('div', { class: 'dr-fine', text: `An AI assistant wrote this. It looks plausible. Tick the ${v.n_issues} real problem${v.n_issues > 1 ? 's' : ''}; some items are fine and ticking them costs points.` }));
  const ticked = new Set();
  const list = el('div', { class: 'dr-opts' }, v.items.map(it => {
    const c = el('input', { type: 'checkbox', onchange: () => { c.checked ? ticked.add(it.id) : ticked.delete(it.id); } });
    return el('label', { class: 'dr-opt', 'data-id': it.id }, [c, el('span', {}, [it.text, el('span', { class: 'why', hidden: true })])]);
  }));
  card.append(list);
  return {
    answer() { if (!ticked.size) throw new Error('Tick at least one item (or Show the answer).'); return { picks: [...ticked] }; },
    mark(r) { (r.feedback.items || []).forEach(x => { const lab = list.querySelector(`[data-id="${x.id}"]`); if (!lab || !x.ticked) return;
      lab.classList.add(x.real ? 'good' : 'bad'); const w = lab.querySelector('.why'); if (w && x.why) { w.hidden = false; w.textContent = (x.real ? 'Real problem. ' : 'Not a problem. ') + x.why; } }); },
    tip(r) { const f = r.feedback; return `You found ${f.right} of ${f.total}${f.wrong ? ` and ticked ${f.wrong} that ${f.wrong === 1 ? 'is' : 'are'} fine` : ''}. The red items are not problems; read why.`; },
    reveal(s, host) { (s.items || []).forEach(x => host.append(el('div', { class: 'dr-fine', html: `<b>${x.real ? 'Problem' : 'Fine'}:</b> ${C.esc(x.text)} <span class="muted">— ${C.esc(x.why)}</span>` }))); },
  };
}

// ---- wiring ------------------------------------------------------------------------------------------------------------------
async function refreshSummary() { try { summary = await C.api('/drills/summary'); } catch { /* keep the old numbers */ } }

export async function init(ctx) {
  C = ctx;
  if (C.PANE && C.PANE !== 'lesson') return;
  await refreshSummary();
  C.registerDayTab({
    id: 'drills', label: 'Drills',
    show: d => !!summary.days?.[d.n],
    count: d => { const s = summary.days?.[d.n]; return s ? `${s.done}/${s.total}` : ''; },
    render,
  });
}
