// The assistant, docked at the bottom. It always sees what you're looking at (lesson, code, selection, run output),
// even when the lesson / playground are in other windows (context is gathered over the sync channel).
import { $, api, esc, md, enhance, toast, store, TRK } from './util.js';
import * as layout from './layout.js';
import * as sync from './sync.js';

const QUICKS = [
  ['where_used', 'Where & how is this used?', 'p'], ['visual', '\u{1F441} Show a visual', 'p'], ['explain_simple', 'Explain simply'],
  ['example', 'Real example'], ['why', 'Why does it work?'], ['quiz', 'Quiz me'], ['review', 'Review my code'], ['hint', 'Give me a hint'],
];
let quickText = {};
let ctx = { dayNo: null, tab: 'home', label: 'Home', getCode: null, getOutput: null, exercise: null };
let playCtx = null;
let selection = '';
let focus = { id: 'lesson', ts: 0 };
let busy = false, threadKey = '__init__';
let assistant = { active: 'offline', providers: {} };
let onSettings = () => {};

const lessonHere = () => (layout.PANE ? layout.PANE === 'lesson' : !layout.isPopped('lesson'));
const playHere = () => (layout.PANE ? layout.PANE === 'play' : !layout.isPopped('play'));
const tutorHere = () => (layout.PANE ? layout.PANE === 'tutor' : !layout.isPopped('tutor'));

export function init({ openSettings }) {
  onSettings = openSettings;
  api('/chat/quick').then(r => { quickText = r.quick; }).catch(() => {});
  const root = $('#pane-tutor');
  root.innerHTML = `
    <div class="phead tutor-head">
      <div class="ptab" title="Drag out of the window to open it on its own"><span class="pico">&#10022;</span><span class="ptitle">Assistant</span></div>
      <button class="askbar" id="askbar" title="Open the assistant (Ctrl+K)"><span>Ask anything &mdash; <i>&ldquo;I get the code, but where would I use it?&rdquo;</i></span><kbd>Ctrl K</kbd></button>
      <span class="prov" id="prov" title="Change assistant"></span>
      <span class="tctx" id="tctx"></span>
      <div class="pacts">
        <button class="pbtn" data-act="max" title="Maximise / restore">&#10530;</button>
        <button class="pbtn" data-act="pop" title="Open in its own window">&#10697;</button>
        <button class="pbtn" data-act="toggle" id="tcollapse" title="Collapse (Ctrl+K)">&#9662;</button>
      </div>
    </div>
    <div class="pbody tbody">
      <div class="msgs" id="msgs"></div>
      <div class="quick" id="quick">${QUICKS.map(([id, label, c]) => `<button class="qk ${c || ''}" data-q="${id}">${label}</button>`).join('')}</div>
      <div class="compose">
        <div id="selchip"></div>
        <div class="cbox">
          <textarea id="tin" rows="1" placeholder="Ask anything, e.g. &ldquo;I understood the code, but where would I use this?&rdquo;"></textarea>
          <label class="inc" title="Share your current editor code with the assistant"><input type="checkbox" id="inc-code" checked> include my code</label>
          <button class="send" id="tsend" title="Send (Enter)">&uarr;</button>
        </div>
      </div>
    </div>`;
  layout.attachHead($('.phead', root), 'tutor');

  const tin = $('#tin');
  tin.addEventListener('input', () => { tin.style.height = 'auto'; tin.style.height = Math.min(tin.scrollHeight, 110) + 'px'; });
  tin.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } });
  $('#tsend').onclick = submit;
  $('#quick').onclick = e => { const q = e.target.dataset.q; if (q) send('', q); };
  $('#prov').onclick = () => onSettings();
  $('#askbar').onclick = () => toggle(true);
  $('.phead', root).addEventListener('click', e => { if (root.classList.contains('collapsed') && !e.target.closest('.pacts, .ptab')) toggle(true); });
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); toggle(!tutorOpenNow() || document.activeElement !== $('#tin')); }
  });
  layout.onEvent('tutor-open', () => setTimeout(() => $('#tin')?.focus(), 60));
  document.addEventListener('pm:editorfocus', e => { focus = { id: e.detail.pane === 'play' ? 'play' : 'lesson', ts: Date.now() }; });

  // answers for other windows
  sync.provide('ctx', () => snapshot());
  sync.on('lessonctx', m => {
    if (lessonHere()) return;
    ctx = { ...ctx, dayNo: m.dayNo, tab: m.tab, label: m.label, exercise: m.exercise };
    paintLabel();
  });
  sync.on('clearsel', () => { selection = ''; paintSel(); });
  sync.on('ask', m => { if (tutorHere()) doAsk(m.quick, m.text, m.selection); });
  if (layout.PANE === 'tutor') {                       // popped-out assistant: learn what the lesson is showing
    sync.request('ctx', {}, { wait: 600 }).then(all => {
      const l = all.map(a => a.lesson).find(Boolean); if (l) { ctx = { ...ctx, dayNo: l.dayNo, tab: l.tab, label: l.label, exercise: l.exercise }; paintLabel(); }
    });
  }
  paintProvider();
}

const tutorOpenNow = () => layout.tutorOpen();
export function toggle(open) {
  if (layout.PANE === 'tutor') { $('#tin')?.focus(); return; }
  if (layout.isPopped('tutor')) { layout.focusPopped('tutor'); return; }
  layout.setTutorOpen(open ?? !tutorOpenNow());
}

export function setAssistant(st) { assistant = st; paintProvider(); }
function paintProvider() {
  const el = $('#prov'); if (!el) return;
  const a = assistant.active;
  const names = { cursor: 'Cursor', anthropic: 'Claude', openai: 'GPT', offline: 'Built-in' };
  const model = a !== 'offline' ? ' · ' + (assistant.providers?.[a]?.model || '') : '';
  el.textContent = names[a] + model;
  el.className = 'prov' + (a !== 'offline' ? ' live' : '');
  el.title = a === 'offline' ? 'Built-in tutor (no key needed). Click to connect Cursor / Claude / GPT for deeper answers.' : 'Connected. Click to change.';
}

// ---- context -------------------------------------------------------------------------------------------------
function paintLabel() {
  const el = $('#tctx'); if (!el) return;
  el.textContent = ctx.label + (ctx.exercise && ctx.tab === 'practice' ? ' · ' + ctx.exercise : '');
  const key = ctx.dayNo ? 'd' + ctx.dayNo : 'g';
  if (key !== threadKey) { threadKey = key; loadThread(); }
}
const announce = () => sync.send('lessonctx', { dayNo: ctx.dayNo, tab: ctx.tab, label: ctx.label, exercise: ctx.exercise });

/** The lesson pane tells the assistant what it is showing. */
export function setContext(c) {
  ctx = { ...ctx, getCode: null, getOutput: null, exercise: null, ...c };
  paintLabel(); announce();
  setSelection('');
}
export function setExercise(id, label) { ctx.exercise = id; if (label) ctx.exerciseLabel = label; paintLabel(); announce(); }
/** The playground pane registers itself so "my code" can come from it when that is what you last touched. */
export function setPlay(p) { playCtx = p; }
export function markFocus(id) { focus = { id, ts: Date.now() }; }

export function setSelection(text) {
  selection = (text || '').trim().slice(0, 1500);
  paintSel();
}
function paintSel() {
  const box = $('#selchip'); if (!box) return;
  box.innerHTML = selection ? `<div class="selchip"><span>&ldquo;${esc(selection.replace(/\s+/g, ' ').slice(0, 90))}&rdquo;</span><button title="Remove">&#10005;</button></div>` : '';
  if (selection) box.querySelector('button').onclick = () => { setSelection(''); sync.send('clearsel'); };
}

function snapshot() {
  return {
    lesson: lessonHere() ? { dayNo: ctx.dayNo, tab: ctx.tab, label: ctx.label, exercise: ctx.exercise, code: ctx.getCode?.() || '', output: ctx.getOutput?.() || '' } : null,
    play: playCtx && playHere() ? { code: playCtx.getCode() || '', output: playCtx.getOutput?.() || '' } : null,
    focus: focus.id, ts: focus.ts, selection,
  };
}
async function gather() {
  const mine = snapshot(), all = [mine];
  if (layout.PANE || layout.anyPopped()) all.push(...await sync.request('ctx'));
  const lesson = all.map(a => a.lesson).find(Boolean) || null, play = all.map(a => a.play).find(Boolean) || null;
  const top = all.reduce((b, a) => (a.ts > b.ts ? a : b), mine);
  const pick = k => (top.focus === 'play' ? (play?.[k] || lesson?.[k]) : (lesson?.[k] || play?.[k])) || '';
  return { lesson, selection: selection || all.map(a => a.selection).find(Boolean) || '', code: pick('code'), output: pick('output') };
}

// ---- asking ----------------------------------------------------------------------------------------------
/** From the selection popover, quick actions, other panes. Routes to wherever the assistant lives. */
export function ask(quick, text = '', sel) {
  const s = sel ?? selection;
  if (!tutorHere()) {
    sync.send('ask', { quick, text, selection: s });
    if (layout.PANE) toast('Sent to the assistant'); else layout.focusPopped('tutor');
    return;
  }
  doAsk(quick, text, s);
}
function doAsk(quick, text, sel) {
  if (sel) setSelection(sel);
  if (layout.PANE !== 'tutor') layout.setTutorOpen(true);
  send(text, quick);
}

// ---- thread ----------------------------------------------------------------------------------------------
async function loadThread() {
  const box = $('#msgs'); if (!box) return;
  box.innerHTML = '';
  try {
    const { items } = await api('/chat/history?day=' + (ctx.dayNo || 0));
    if (!items.length) return empty();
    for (const it of items) {
      addUser(it.text, { quality: it.quality, valid: it.valid, flags: it.flags, tips: it.tips, source: it.source });
      const b = addBot(); b.text = it.answer || ''; renderBot(b, true); b.provider = it.provider; finishBot(b, it.id, it.helpful);
    }
    scroll(true);
  } catch { empty(); }
}

function empty() {
  const where = ctx.dayNo ? `this lesson (Day ${ctx.dayNo})` : `anything ${TRK.short}`;
  $('#msgs').innerHTML = `<div class="empty-t"><div class="big">&#10022;</div>
    <b>I'm reading ${where} with you.</b><p class="small">Highlight any line and tap <b>Where &amp; how is this used?</b>, or ask for a <b>visual</b> of any code. You can also just ask in your own words.</p></div>`;
}
function scroll(force) {
  const m = $('#msgs');
  if (force || m.scrollHeight - m.scrollTop - m.clientHeight < 140) m.scrollTop = m.scrollHeight;
}
function addUser(text, a) {
  $('#msgs .empty-t')?.remove();
  const el = document.createElement('div');
  el.className = 'msg user';
  el.innerHTML = `<div class="bubble">${esc(text)}</div><div class="qa"></div>`;
  $('#msgs').appendChild(el);
  if (a) paintQA(el, a);
  return el;
}
function paintQA(el, a) {
  const qa = el.querySelector('.qa');
  if (a.quality == null) { qa.innerHTML = ''; return; }
  const cls = a.quality >= 70 ? 'good' : a.quality >= 45 ? 'accent' : 'warn';
  const label = a.quality >= 70 ? 'great question' : a.quality >= 45 ? 'good question' : 'could be sharper';
  qa.innerHTML = `<span class="chip ${cls}" title="Flags: ${esc((a.flags || []).join(', ') || '-')}">${label} · ${a.quality}</span>` +
    (a.tips?.[0] && a.quality < 70 ? `<span class="tip">${esc(a.tips[0])}</span>` : '');
}
function addBot() {
  const el = document.createElement('div');
  el.className = 'msg bot';
  el.innerHTML = `<div class="bubble md"><span class="typing"><i></i><i></i><i></i></span></div><div class="fb"></div>`;
  $('#msgs').appendChild(el);
  return { el, text: '', raf: 0, provider: null };
}
function renderBot(b, final) {
  const bub = b.el.querySelector('.bubble');
  bub.innerHTML = md(b.text);
  enhance(bub, { diagrams: !!final });
}
function finishBot(b, qid, helpful) {
  const label = { cursor: 'via Cursor', anthropic: 'via Claude', openai: 'via GPT', offline: 'built-in tutor' }[b.provider] || '';
  const fb = b.el.querySelector('.fb');
  fb.innerHTML = `<span class="small muted" style="margin-right:4px">${label}</span>
    <button data-v="1" class="${helpful === 1 ? 'on' : ''}" title="Helpful">&#128077;</button><button data-v="-1" class="${helpful === -1 ? 'on' : ''}" title="Not helpful">&#128078;</button>`;
  fb.onclick = async e => {
    const v = +e.target.dataset.v; if (!v || !qid) return;
    await api('/chat/feedback', { method: 'POST', body: { qid, helpful: v } });
    fb.querySelectorAll('button').forEach(x => x.classList.toggle('on', +x.dataset.v === v));
    toast(v > 0 ? 'Thanks! Noted.' : 'Noted, I will try a different angle next time.');
  };
}

function submit() {
  const tin = $('#tin'); const text = tin.value.trim();
  if (!text) return;
  tin.value = ''; tin.style.height = 'auto';
  send(text, null);
}

async function send(text, quick) {
  if (busy) return;
  busy = true; $('#tsend').disabled = true;
  const g = await gather();
  const include = $('#inc-code')?.checked;
  const sel = g.selection;
  const payload = {
    session_id: store.sid, text, quick_id: quick,
    ctx: {
      day_no: g.lesson?.dayNo ?? ctx.dayNo, tab: g.lesson?.tab || ctx.tab, exercise_id: g.lesson?.exercise || ctx.exercise, selection: sel,
      code: include ? g.code : '', output: g.output,
    },
  };
  const shown = text || quickText[quick] || quick;
  const userEl = addUser(shown + (sel ? `\n\n\u201c${sel.replace(/\s+/g, ' ').slice(0, 80)}${sel.length > 80 ? '\u2026' : ''}\u201d` : ''));
  const bot = addBot();
  scroll(true);
  setSelection(''); sync.send('clearsel');
  let qid = null;
  try {
    const r = await fetch('/api/chat', { method: 'POST', headers: { 'x-portal': '1', 'content-type': 'application/json' }, body: JSON.stringify(payload) });
    if (!r.ok) throw new Error(await r.text());
    const reader = r.body.getReader(); const dec = new TextDecoder(); let buf = '';
    for (;;) {
      const { value, done } = await reader.read(); if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
        if (!line) continue;
        const ev = JSON.parse(line);
        if (ev.t === 'q') { qid = ev.qid; paintQA(userEl, ev.analysis); }
        else if (ev.t === 'meta') bot.provider = ev.provider;
        else if (ev.t === 'note') { const n = document.createElement('div'); n.className = 'note'; n.textContent = ev.x + '; using the next option.'; bot.el.before(n); }
        else if (ev.t === 'delta') {
          bot.text += ev.x;
          if (!bot.raf) bot.raf = requestAnimationFrame(() => { bot.raf = 0; renderBot(bot, false); scroll(false); });
        } else if (ev.t === 'error') { bot.text += `\n\n\u26A0\uFE0F ${ev.x}`; }
      }
    }
    cancelAnimationFrame(bot.raf); renderBot(bot, true); finishBot(bot, qid, null);
  } catch (e) {
    bot.el.querySelector('.bubble').innerHTML = `<span class="muted">Couldn't reach the assistant (${esc(e.message)}).</span>`;
  } finally {
    busy = false; $('#tsend').disabled = false; scroll(true);
  }
}
