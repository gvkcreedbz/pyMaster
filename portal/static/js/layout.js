// The workspace: lesson | playground side by side, the assistant docked at the bottom.
// Panes can be resized (drag the gutters), maximised, hidden, swapped, and popped out into their own window
// (button, or drag a pane's tab out of the browser window, like detaching a Chrome tab).
import { $, $$, toast, store, TRK } from './util.js';
import * as sync from './sync.js';

export const PANE = (() => {
  const p = new URLSearchParams(location.search).get('pane');
  return ['lesson', 'play', 'tutor'].includes(p) ? p : null;     // set when this window is a popped-out pane
})();

const KEY = 'pm-layout';
const DEF = { split: 50, tutorH: 380, tutorOpen: false, swap: false, play: true };
let L = { ...DEF };
try { L = { ...DEF, ...JSON.parse(localStorage.getItem(KEY) || '{}') }; } catch { /* first run */ }
const save = () => localStorage.setItem(KEY, JSON.stringify(L));

const popped = {};                 // id -> Window handle (or true when adopted after a reload)
const pollers = {};
const listeners = {};
export const onEvent = (t, fn) => { (listeners[t] ||= []).push(fn); };
const emit = (t, d) => (listeners[t] || []).forEach(fn => fn(d));

export const isPopped = id => !!popped[id];
export const anyPopped = () => Object.values(popped).some(Boolean);
export const tutorOpen = () => PANE === 'tutor' || L.tutorOpen;
export const playVisible = () => PANE ? PANE === 'play' : L.play && !popped.play;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const pane = id => $('#pane-' + id);

const NAMES = { lesson: 'Lesson', play: 'Playground', tutor: 'Assistant' };
const ICONS = { lesson: '&#128214;', play: '&#9654;', tutor: '&#10022;' };

// ---- applying state to the DOM -----------------------------------------------------------------------------
export function apply() {
  if (PANE) return paintToggles();
  const lessonVis = !popped.lesson, playVis = L.play && !popped.play, both = lessonVis && playVis;
  const first = L.swap ? 'play' : 'lesson', second = L.swap ? 'lesson' : 'play';
  pane('lesson').classList.toggle('hide', !lessonVis);
  pane('play').classList.toggle('hide', !playVis);
  $('#gut-v').classList.toggle('hide', !both);
  pane(first).style.order = 1; pane(second).style.order = 3; $('#gut-v').style.order = 2;
  pane(first).style.flex = both ? `0 0 calc(${L.split}% - 5px)` : '1 1 0';
  pane(second).style.flex = '1 1 0';
  $('#toprow').classList.toggle('hide', !lessonVis && !playVis);

  const tutorHere = !popped.tutor, open = L.tutorOpen && tutorHere;
  const t = pane('tutor');
  t.classList.toggle('hide', !tutorHere);
  t.classList.toggle('collapsed', !open);
  t.style.height = open ? L.tutorH + 'px' : '';
  $('#gut-h').classList.toggle('hide', !open || (!lessonVis && !playVis));
  t.classList.toggle('fill', open && !lessonVis && !playVis);

  $('#allgone').innerHTML = (!lessonVis && !playVis) ?
    `<div class="card pad"><b>Your panes are in their own windows.</b><div class="sub small">Bring one back to continue here.</div>
     <div class="row" style="margin-top:12px">${['lesson', 'play'].filter(i => popped[i]).map(i => `<button class="btn sm" data-dock="${i}">&#8690; Bring back ${NAMES[i]}</button>`).join('')}</div></div>` : '';
  paintToggles();
}

function paintToggles() {
  const box = $('#ptoggles'); if (!box) return;
  const chip = (id, on, label, extra = '') => `<button class="pt ${popped[id] ? 'popped' : on ? 'on' : ''}" data-t="${id}" title="${popped[id] ? NAMES[id] + ' is in its own window (click to switch to it)' : on ? 'Hide' : 'Show'} ${NAMES[id]}">
      <span class="pico">${ICONS[id]}</span>${label}${popped[id] ? `<span class="dock" data-dock="${id}" title="Bring it back into this window">&#8690;</span>` : extra}</button>`;
  box.innerHTML = chip('lesson', true, 'Lesson') + chip('play', L.play, 'Playground') + chip('tutor', L.tutorOpen, 'Assistant');
  $$('.pt', box).forEach(b => b.onclick = e => {
    const id = b.dataset.t;
    if (e.target.dataset.dock) return dock(id);
    if (popped[id]) { try { popped[id].focus(); } catch { /* ignore */ } return; }
    if (id === 'play') { L.play = !L.play; save(); apply(); }
    else if (id === 'tutor') setTutorOpen(!L.tutorOpen);
    else toggleMax('lesson');
  });
}

// ---- public controls ---------------------------------------------------------------------------------------
export function setTutorOpen(open) { L.tutorOpen = !!open; save(); apply(); if (open) emit('tutor-open'); }
export function showPane(id) {
  if (PANE) return;
  if (popped[id] && popped[id] !== true) { try { popped[id].focus(); } catch { /* ignore */ } return; }
  if (id === 'play') { L.play = true; save(); apply(); }
  if (id === 'tutor') setTutorOpen(true);
  $$('.pane.max').forEach(p => { if (p.id !== 'pane-' + id) p.classList.remove('max'); });
}
export function setTitle(id, text) { const el = $('#title-' + id); if (el) el.textContent = text; }

export function toggleMax(id) {
  const p = pane(id), on = !p.classList.contains('max');
  $$('.pane.max').forEach(x => x.classList.remove('max'));
  p.classList.toggle('max', on);
  $('#work').classList.toggle('has-max', on);
  refreshEditors();
}

// ---- pop out / dock back -----------------------------------------------------------------------------------
export function popOut(id, at) {
  if (PANE || popped[id]) return;
  const p = pane(id), r = p.getBoundingClientRect();
  const w = Math.round(clamp(r.width, 520, 1100)), h = Math.round(clamp(r.height + 70, 460, 900));
  const left = Math.round(at ? at.x - 140 : window.screenX + r.left + 40), top = Math.round(at ? at.y - 16 : window.screenY + r.top + 70);
  const hash = id === 'lesson' ? location.hash : '';
  const url = `/?pane=${id}&sid=${encodeURIComponent(store.sid || '')}${hash}`;
  const win = window.open(url, 'pm-' + id, `popup=yes,width=${w},height=${h},left=${left},top=${top}`);
  if (!win) { toast('The browser blocked the new window. Allow pop-ups for this site and try again.', 4200); return; }
  adopt(id, win);
  emit('popped', id);
}
function adopt(id, win) {
  popped[id] = win;
  pane(id).classList.remove('max');
  clearInterval(pollers[id]);
  if (win !== true) pollers[id] = setInterval(() => { if (win.closed) closed(id); }, 900);
  apply();
}

function closed(id) {                                    // the popped window went away on its own
  if (!popped[id]) return;
  clearInterval(pollers[id]); delete popped[id]; apply(); emit('docked', id);
}
export function dock(id) {                               // bring a pane back and close its window
  const w = popped[id]; if (!w) return;
  if (w === true) sync.send('close-pane', { id }); else { try { w.close(); } catch { /* ignore */ } }
  closed(id);
}
export function dockSelf() {                             // called inside a popped-out window
  sync.send('dock', { id: PANE });
  setTimeout(() => window.close(), 60);
}
export function focusPopped(id) { try { if (popped[id] && popped[id] !== true) popped[id].focus(); } catch { /* ignore */ } }

sync.on('pane-closed', m => closed(m.id));
sync.on('dock', m => { if (!PANE) dock(m.id); });
sync.on('hello', () => { if (PANE) sync.send('pane-alive', { id: PANE }); });
sync.on('pane-alive', m => { if (!PANE && !popped[m.id]) { adopt(m.id, true); emit('popped', m.id); } });
sync.on('close-pane', m => { if (PANE === m.id) window.close(); });

// ---- gutters ---------------------------------------------------------------------------------------------
function dragGutter(el, cursor, onMove, onReset) {
  el.addEventListener('dblclick', () => { onReset(); save(); apply(); });
  el.addEventListener('pointerdown', e => {
    e.preventDefault(); try { el.setPointerCapture(e.pointerId); } catch { /* synthetic pointer */ }
    document.body.classList.add('dragging'); document.body.style.cursor = cursor; el.classList.add('on');
    const mv = ev => { onMove(ev); apply(); };
    const up = () => {
      el.removeEventListener('pointermove', mv); document.body.classList.remove('dragging'); document.body.style.cursor = ''; el.classList.remove('on'); save(); refreshEditors();
    };
    el.addEventListener('pointermove', mv);
    el.addEventListener('pointerup', up, { once: true }); el.addEventListener('pointercancel', up, { once: true });
  });
}

// ---- dragging a pane's tab: swap sides, or drop outside the window to detach ---------------------------------------
export function attachHead(head, id) {
  const tab = $('.ptab', head); if (!tab || PANE) return;
  let st = null, ghost = null;
  const outside = e => e.clientX < 4 || e.clientY < 4 || e.clientX > innerWidth - 4 || e.clientY > innerHeight - 4;
  const overOther = e => {
    if (id === 'tutor') return false;
    const o = pane(id === 'lesson' ? 'play' : 'lesson'); if (o.classList.contains('hide')) return false;
    const r = o.getBoundingClientRect(); return e.clientX > r.left && e.clientX < r.right && e.clientY > r.top && e.clientY < r.bottom;
  };
  tab.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;
    st = { x: e.clientX, y: e.clientY, moved: false }; try { tab.setPointerCapture(e.pointerId); } catch { /* synthetic pointer */ }
  });
  tab.addEventListener('pointermove', e => {
    if (!st) return;
    if (!st.moved && Math.hypot(e.clientX - st.x, e.clientY - st.y) < 8) return;
    if (!st.moved) {
      st.moved = true; document.body.classList.add('dragging', 'tabdrag');
      ghost = document.createElement('div'); ghost.className = 'dragghost'; document.body.appendChild(ghost);
    }
    ghost.style.left = e.clientX + 14 + 'px'; ghost.style.top = e.clientY + 14 + 'px';
    const out = outside(e), sw = overOther(e);
    ghost.innerHTML = `<span class="pico">${ICONS[id]}</span>${NAMES[id]}<small>${out ? 'Release to open in its own window' : sw ? 'Release to swap sides' : 'Drag out of the window to detach'}</small>`;
    ghost.classList.toggle('go', out || sw);
    $$('.pane').forEach(p => p.classList.toggle('droptarget', sw && p.id === 'pane-' + (id === 'lesson' ? 'play' : 'lesson')));
  });
  const end = e => {
    if (!st) return;
    const s = st; st = null;
    ghost?.remove(); ghost = null; document.body.classList.remove('dragging', 'tabdrag'); $$('.droptarget').forEach(p => p.classList.remove('droptarget'));
    if (!s.moved) return;
    if (outside(e)) popOut(id, { x: e.screenX, y: e.screenY });
    else if (overOther(e)) { L.swap = !L.swap; save(); apply(); refreshEditors(); }
  };
  tab.addEventListener('pointerup', end); tab.addEventListener('pointercancel', end);
  tab.addEventListener('dblclick', () => toggleMax(id));
}

// ---- editors need a nudge when their box changes size ---------------------------------------------------------------
let rf = 0;
export function refreshEditors() {
  cancelAnimationFrame(rf);
  rf = requestAnimationFrame(() => $$('.CodeMirror').forEach(e => e.CodeMirror?.refresh()));
}

// ---- boot -----------------------------------------------------------------------------------------------
export function init() {
  const work = $('#work');
  if (PANE) {
    document.body.classList.add('solo', 'solo-' + PANE);
    $$('[data-act=pop]').forEach(b => { b.innerHTML = '&#8690;'; b.title = 'Dock back into the main window'; });
    window.addEventListener('pagehide', () => sync.send('pane-closed', { id: PANE }));
    sync.send('pane-alive', { id: PANE });
    document.title = NAMES[PANE] + ' · ' + TRK.name;
    if (PANE === 'tutor') pane('tutor').classList.remove('collapsed');
  } else {
    dragGutter($('#gut-v'), 'col-resize',
      ev => { const r = $('#toprow').getBoundingClientRect(); L.split = clamp((ev.clientX - r.left) / r.width * 100, 20, 80); },
      () => { L.split = 50; });
    dragGutter($('#gut-h'), 'row-resize',
      ev => { const r = work.getBoundingClientRect(); L.tutorH = Math.round(clamp(r.bottom - 8 - ev.clientY, 170, r.height - 180)); },
      () => { L.tutorH = 380; });
    sync.send('hello');
  }
  $$('.pane').forEach(p => { const h = $('.phead', p); if (h && p.id !== 'pane-tutor') attachHead(h, p.dataset.pane); });

  work.addEventListener('click', e => {
    const dk = e.target.closest('[data-dock]'); if (dk) return dock(dk.dataset.dock);
    const b = e.target.closest('[data-act]'); if (!b) return;
    const id = b.closest('[data-pane]')?.dataset.pane; if (!id) return;
    const act = b.dataset.act;
    if (act === 'max') toggleMax(id);
    else if (act === 'pop') PANE ? dockSelf() : popOut(id);
    else if (act === 'close' && id === 'play') { L.play = false; save(); apply(); }
    else if (act === 'toggle') setTutorOpen(!L.tutorOpen);
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && $('.pane.max') && !$('#modal-root').firstChild) { $$('.pane.max').forEach(p => p.classList.remove('max')); $('#work').classList.remove('has-max'); refreshEditors(); }
  });
  if ('ResizeObserver' in window) { const ro = new ResizeObserver(refreshEditors); $$('.pane').forEach(p => ro.observe(p)); }
  apply();
}
