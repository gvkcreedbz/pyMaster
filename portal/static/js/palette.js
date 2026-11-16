// Command palette (Ctrl+P, or "/" outside text fields): jump to any lesson section, concept, guide, blueprint, or run an action.
import { $, $$, api, esc, debounce } from './util.js';

const ICON = { action: '&#9889;', day: '&#128197;', lesson: '&#128214;', quiz: '&#10067;', concept: '&#10022;', guide: '&#10081;', blueprint: '&#129513;' };
const LABEL = { action: 'Action', day: 'Day', lesson: 'Lesson', quiz: 'Quiz', concept: 'Concept', guide: 'Guide', blueprint: 'Blueprint' };

let actionsFn = () => [];
let go = h => { location.hash = h; };

export function initPalette({ actions, navigate }) {
  actionsFn = actions;
  if (navigate) go = navigate;
  document.addEventListener('keydown', e => {
    const isP = (e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && e.key.toLowerCase() === 'p';
    const t = e.target, typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable || t.closest?.('.CodeMirror'));
    if (isP || (e.key === '/' && !typing && !e.ctrlKey && !e.metaKey)) { e.preventDefault(); open(); }
  }, true);
}

export const isOpen = () => !!$('#palette');
let opener = null;
export function close() {
  const el = $('#palette');
  if (!el) return;
  el.remove();
  if (opener && opener.isConnected && !$('#modal-root')?.firstChild) { try { opener.focus({ preventScroll: true }); } catch { /* gone */ } }
  opener = null;
}

export function open() {
  if (isOpen()) { $('#palette input').focus(); return; }
  opener = document.activeElement;
  const el = document.createElement('div');
  el.id = 'palette'; el.className = 'pal-overlay';
  el.innerHTML = `<div class="pal card" role="dialog" aria-modal="true" aria-label="Search">
      <input type="text" role="combobox" aria-label="Search lessons, concepts and commands" aria-expanded="true" aria-controls="pal-list" aria-autocomplete="list" placeholder="Search lessons, concepts, blueprints, or type a command…" autocomplete="off" spellcheck="false">
      <div class="pal-list" id="pal-list" role="listbox" aria-label="Results"></div>
      <div class="pal-foot"><span><kbd>&uarr;</kbd><kbd>&darr;</kbd> move</span><span><kbd>Enter</kbd> open</span><span><kbd>Esc</kbd> close</span></div></div>`;
  document.body.appendChild(el);
  const input = $('input', el), list = $('.pal-list', el);
  let items = [], sel = 0, seq = 0;

  const paint = () => {
    list.innerHTML = items.length ? items.map((it, i) => `<div class="pal-item ${i === sel ? 'sel' : ''}" id="pal-opt-${i}" data-i="${i}" role="option" aria-selected="${i === sel}">
        <span class="ico">${ICON[it.type] || ''}</span><span class="txt"><b>${esc(it.title)}</b>${it.sub ? `<span>${esc(it.sub)}</span>` : ''}</span><span class="kind">${LABEL[it.type] || ''}</span></div>`).join('')
      : `<div class="pal-empty">${input.value.trim() ? 'No matches. Try fewer or different words.' : 'Type to search.'}</div>`;
    $('.sel', list)?.scrollIntoView({ block: 'nearest' });
    if (items.length) input.setAttribute('aria-activedescendant', 'pal-opt-' + sel); else input.removeAttribute('aria-activedescendant');
  };
  const actions = q => {
    const low = q.toLowerCase().trim();
    return actionsFn().filter(a => !low || (a.title + ' ' + (a.keys || '')).toLowerCase().includes(low)).slice(0, low ? 5 : 8)
      .map(a => ({ type: 'action', title: a.title, sub: a.sub || '', run: a.run }));
  };
  const query = debounce(async () => {
    const q = input.value.trim(), my = ++seq;
    if (!q) { items = actions(''); sel = 0; return paint(); }
    items = actions(q); sel = 0; paint();                       // instant: commands first
    try {
      const r = await api('/search?q=' + encodeURIComponent(q) + '&limit=10');
      if (my !== seq) return;
      items = [...items, ...r.items.map(x => ({ ...x, run: () => go(x.hash) }))];
      sel = 0; paint();
    } catch { /* offline: commands still work */ }
  }, 110);
  const choose = i => { const it = items[i]; if (!it) return; close(); it.run(); };

  input.addEventListener('input', query);
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); sel = Math.min(items.length - 1, sel + 1); paint(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); sel = Math.max(0, sel - 1); paint(); }
    else if (e.key === 'Enter') { e.preventDefault(); choose(sel); }
    else if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'Tab') e.preventDefault();                  // focus stays in the search box; arrows move through results
  });
  list.addEventListener('mousemove', e => { const r = e.target.closest('.pal-item'); if (r && +r.dataset.i !== sel) { sel = +r.dataset.i; $$('.pal-item', list).forEach((x, i) => { x.classList.toggle('sel', i === sel); x.setAttribute('aria-selected', String(i === sel)); }); input.setAttribute('aria-activedescendant', 'pal-opt-' + sel); } });
  list.addEventListener('click', e => { const r = e.target.closest('.pal-item'); if (r) choose(+r.dataset.i); });
  el.addEventListener('mousedown', e => { if (e.target === el) close(); });
  items = actions(''); paint(); input.focus();
}
