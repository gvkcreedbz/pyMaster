// Predict before you run: on the Code-along tab, pressing Run first asks "what do you think this prints?" (optional, skippable,
// can be switched off). After the run it shows your prediction next to the real output. Guessing first, then being surprised,
// is how a mental model gets corrected; just watching output scroll by is not.
// Front end only; the result is logged with POST /api/event (type "predict_run") so Insights/XP features can use it.
const LS = 'pm-predict';
const on = () => localStorage.getItem(LS) !== '0';
let C;

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
const norm = s => String(s || '').replace(/\r/g, '').split('\n').map(l => l.replace(/\s+$/, '')).join('\n').trim();

function wire(dayNo) {
  const rp = document.querySelector('#rp');
  const btn = rp?.querySelector('[data-run]');
  if (!rp || !btn || btn.dataset.pmPredict) return;
  btn.dataset.pmPredict = '1';
  let prediction = null, panel = null;

  // the switch, next to the Run button
  const sw = el('label', { class: 'pd-switch', title: 'Ask me what I expect before the code runs' }, [
    el('input', { type: 'checkbox', id: 'pd-on', ...(on() ? { checked: true } : {}), onchange: e => { localStorage.setItem(LS, e.target.checked ? '1' : '0'); if (!e.target.checked) closePanel(); } }),
    ' Predict first']);
  btn.after(sw);

  const closePanel = () => { panel?.remove(); panel = null; };
  const clearCompare = () => rp.querySelector('.pd-compare')?.remove();

  const go = () => { btn.dataset.pmGo = '1'; btn.click(); };

  btn.addEventListener('click', e => {                       // capture phase: runs before the runner's own handler
    if (btn.dataset.pmGo === '1') { delete btn.dataset.pmGo; return; }
    if (!on()) { prediction = null; return; }
    e.stopImmediatePropagation(); e.preventDefault();
    clearCompare(); closePanel();
    const ta = el('textarea', { class: 'dr-area pd-ta', id: 'pd-ta', rows: 3, 'aria-label': 'Your prediction', spellcheck: 'false',
      placeholder: 'What will it print? A rough idea is fine, even "a number" or "an error". Leave it empty to just run.' });
    panel = el('div', { class: 'pd-panel card pad', role: 'group', 'aria-label': 'Predict before you run' }, [
      el('b', { text: 'Before you run it: what do you think happens?' }), ta,
      el('div', { class: 'row', style: 'gap:10px;margin-top:8px' }, [
        el('button', { class: 'btn primary sm', type: 'button', id: 'pd-go', text: 'Run and compare', onclick: () => { prediction = ta.value.trim() || null; closePanel(); go(); } }),
        el('button', { class: 'btn ghost sm', type: 'button', id: 'pd-skip', text: 'Just run it', onclick: () => { prediction = null; closePanel(); go(); } })])]);
    rp.prepend(panel);
    ta.focus({ preventScroll: true });
    ta.addEventListener('keydown', ev => { if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') { ev.preventDefault(); ev.stopPropagation(); $go(); } });
    const $go = () => panel?.querySelector('#pd-go')?.click();
  }, true);

  // after the run: compare
  const onResult = ev => {
    const d = ev.detail || {};
    if (d.kind !== 'examples' || d.dayNo !== dayNo) return;
    const mine = prediction; prediction = null;
    clearCompare();
    if (!mine) return;
    const actual = d.result?.output ?? '';
    const same = norm(mine) === norm(actual);
    const box = el('div', { class: 'pd-compare card pad', 'aria-live': 'polite' });
    box.append(el('b', { text: same ? 'You predicted it exactly.' : 'Compare your prediction with what happened' }));
    if (!same) {
      box.append(el('div', { class: 'pd-cols' }, [
        el('div', {}, [el('div', { class: 'pd-h', text: 'You expected' }), el('pre', { class: 'out', text: mine })]),
        el('div', {}, [el('div', { class: 'pd-h', text: 'It printed' }), el('pre', { class: 'out', text: actual || '(nothing)' })])]));
      box.append(el('p', { class: 'small muted', text: 'Where did they first differ? That is the spot where your mental picture of the code was off. Say it in one sentence before moving on.' }));
    }
    const log = matched => {
      C.api('/event', { method: 'POST', body: { session_id: C.store.sid, type: 'predict_run', day_no: dayNo, payload: { matched, exact: same, chars: mine.length } } }).catch(() => {});
      box.querySelector('.pd-rate')?.remove();
      box.append(el('div', { class: 'small muted', text: 'Saved.' }));
    };
    if (same) log(true);
    else box.append(el('div', { class: 'row pd-rate', style: 'gap:10px' }, [
      el('span', { class: 'small', text: 'Was your idea basically right?' }),
      el('button', { class: 'btn ghost sm', type: 'button', text: 'Yes, close enough', onclick: () => log(true) }),
      el('button', { class: 'btn ghost sm', type: 'button', text: 'No, I had it wrong', onclick: () => log(false) })]));
    rp.querySelector('[data-res]')?.after(box);
  };
  document.addEventListener('pm:runresult', onResult);
  const stale = () => { if (!document.body.contains(rp)) document.removeEventListener('pm:runresult', onResult); };
  document.addEventListener('pm:route', stale, { once: true });
}

export async function init(ctx) {
  C = ctx;
  if (C.PANE && C.PANE !== 'lesson') return;
  document.addEventListener('pm:dayrendered', e => { if (e.detail.tab === 'along') wire(e.detail.dayNo); });
  const again = () => { const m = location.hash.match(/^#\/day\/(\d+)\/along/); if (m) wire(+m[1]); };       // wire() does nothing twice
  again();                                                                       // we may have loaded after the first render
  const view = document.querySelector('#view');
  if (view) new MutationObserver(again).observe(view, { childList: true, subtree: true });   // the day page redraws itself (e.g. when you mark it done)
}
