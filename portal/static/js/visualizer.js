// "Show me": step through code line by line (variables, call stack, objects with arrows) or see a flowchart / SQL order diagram.
import { $, $$, api, esc, modal, store, toast, TRK } from './util.js';
import { draw } from './diagram.js';

const looksSql = t => /^\s*(--[^\n]*\n\s*)*(select|with|insert|update|delete|create|alter|drop)\b/i.test(t);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

export function openVisualizer({ code, lang, dayNo }) {
  code = (code || '').replace(/\s+$/, '');
  if (!code.trim()) return toast('Write or select some code first, then press Visualize.');
  const sql = lang === 'sql' || (lang !== TRK.fence && looksSql(code));
  const tabs = sql ? [['sql', 'Query order']] : [['step', 'Step through'], ['flow', 'Flow chart']];

  modal(`<div class="vz">
      <div class="vz-head"><h3>&#128065; Visualize</h3>
        <div class="seg" id="vz-tabs">${tabs.map(([id, l], i) => `<button data-t="${id}" class="${i ? '' : 'on'}">${l}</button>`).join('')}</div>
        <span class="grow"></span><span class="small muted vz-hint">&larr; &rarr; step &middot; space plays</span>
        <button class="btn ghost sm" data-x title="Close (Esc)">&#10005;</button></div>
      <div class="vz-body" id="vz-body"></div></div>`, {
    xl: true,
    onMount: (m, close) => {
      m.focus();
      $('[data-x]', m).onclick = () => { stop(); close(); };
      const body = $('#vz-body', m);
      let stop = () => {};
      const go = async id => {
        stop(); stop = () => {};
        $$('#vz-tabs button', m).forEach(b => b.classList.toggle('on', b.dataset.t === id));
        if (id === 'step') stop = await stepView(body, m, code, dayNo);
        else await diagramView(body, code, id === 'sql' ? 'sql' : TRK.fence, dayNo);
      };
      $('#vz-tabs', m).onclick = e => { const t = e.target.dataset.t; if (t) go(t); };
      go(tabs[0][0]);
    },
  });
}

// ---- diagram tab ------------------------------------------------------------------------------------------------
async function diagramView(body, code, lang, dayNo) {
  body.innerHTML = '<div class="vz-pad muted">Drawing…</div>';
  try {
    const r = await api('/visual/diagram', { method: 'POST', body: { code, lang, session_id: store.sid, day_no: dayNo || null } });
    body.innerHTML = '<div class="vz-pad"><div id="vz-dg"></div></div>';
    await draw($('#vz-dg', body), r.mermaid, r.caption);
  } catch (e) {
    body.innerHTML = `<div class="vz-pad"><div class="mmd-err">Couldn't make a diagram: ${esc(e.message)}</div></div>`;
  }
}

// ---- step-through tab ------------------------------------------------------------------------------------------------
async function stepView(body, modalEl, code, dayNo, stdin = '') {
  body.innerHTML = '<div class="vz-pad muted">Running your code step by step&hellip;</div>';
  let data;
  try { data = await api('/visual/trace', { method: 'POST', body: { code, stdin, session_id: store.sid, day_no: dayNo || null } }); }
  catch (e) { body.innerHTML = `<div class="vz-pad"><div class="mmd-err">${esc(e.message)}</div></div>`; return () => {}; }
  if (!data.ok || !data.steps.length) {
    body.innerHTML = `<div class="vz-pad"><div class="mmd-err">${esc(data.error || 'Nothing ran, so there is nothing to step through.')}</div>
      <p class="small muted">Tip: the <b>Flow chart</b> tab still works on code that can't run yet.</p></div>`;
    return () => {};
  }
  const steps = data.steps, lines = code.split('\n');
  let i = 0, timer = null, speed = 1;

  body.innerHTML = `<div class="vz-step">
      <div class="vz-left"><div class="vz-code" id="vzc">${lines.map((l, n) => `<div class="vz-l" data-n="${n + 1}"><span class="ln">${n + 1}</span><span class="tx"></span></div>`).join('')}</div>
        <details class="vz-in"><summary>Input for <code>input()</code> calls</summary>
          <textarea class="field mono" rows="2" id="vzin" placeholder="one answer per line">${esc(stdin)}</textarea><button class="btn sm" id="vzre" style="margin-top:6px">Run again</button></details></div>
      <div class="vz-right">
        <div class="vz-caption" id="vzcap"></div>
        ${data.truncated ? `<div class="vz-note">Stopped after ${steps.length} steps (is there a loop that never ends?).</div>` : ''}
        <div class="vz-state" id="vzs"><svg class="vz-arrows" id="vza"></svg><div class="vz-cols"><div class="vz-frames" id="vzf"></div><div class="vz-heap" id="vzh"></div></div></div>
        <div class="vz-out"><h6>Output so far</h6><pre id="vzo"></pre></div>
      </div></div>
    <div class="vz-ctl">
      <button class="btn sm" data-c="first" title="First step">&#9198;</button><button class="btn sm" data-c="prev" title="Back">&#9664;</button>
      <button class="btn sm primary" data-c="play" id="vzplay" style="min-width:76px">&#9654; Play</button>
      <button class="btn sm" data-c="next" title="Next">&#9654;&#9654;</button><button class="btn sm" data-c="last" title="Last step">&#9197;</button>
      <input type="range" id="vzr" min="0" max="${steps.length - 1}" value="0" class="grow"><span class="small muted" id="vzn" style="min-width:90px;text-align:right"></span>
      <select id="vzsp" title="Speed"><option value="0.5">0.5&times;</option><option value="1" selected>1&times;</option><option value="2">2&times;</option><option value="4">4&times;</option></select></div>`;

  // syntax-highlight each source line
  $$('.vz-l .tx', body).forEach((el, n) => {
    if (window.CodeMirror?.runMode) CodeMirror.runMode(lines[n] || ' ', TRK.cm_mode, el); else el.textContent = lines[n] || ' ';
  });

  const cellOf = v => v.ref ? `<span class="refdot" data-ref="${v.ref}"></span>` : `<span class="pv k-${esc(v.k)}">${esc(v.p)}</span>`;
  const sig = v => JSON.stringify(v);

  function show(n) {
    i = clamp(n, 0, steps.length - 1);
    const s = steps[i], prev = steps[i - 1];
    $$('.vz-l.cur', body).forEach(x => x.classList.remove('cur'));
    const ln = $(`.vz-l[data-n="${s.line}"]`, body); ln?.classList.add('cur'); ln?.scrollIntoView({ block: 'nearest' });

    const top = s.stack[s.stack.length - 1];
    let cap = `About to run line <b>${s.line}</b>: <code>${esc((lines[s.line - 1] || '').trim())}</code>`;
    if (s.ev === 'return') cap = `<b>${esc(top?.name || 'It')}</b> is finishing${s.ret ? ` and returns <code>${esc(s.ret.p ?? 'an object (see the arrow)')}</code>` : ''}.`;
    if (s.ev === 'exception') cap = `<span class="bad">Error on line ${s.line}: ${esc(s.err || '')}</span>`;
    if (i === steps.length - 1 && data.error) cap += `<div class="bad" style="margin-top:4px">&#9888; ${esc(data.error.type)}: ${esc(data.error.msg)}${data.error.line ? ` (line ${data.error.line})` : ''}</div>`;
    $('#vzcap', body).innerHTML = cap;

    $('#vzf', body).innerHTML = (s.stack.length ? s.stack : [{ name: 'Global', vars: {} }]).map((fr, idx) => {
      const pf = prev?.stack[idx]?.name === fr.name ? prev.stack[idx] : null;
      const rows = Object.entries(fr.vars).map(([k, v]) => {
        const changed = !pf || sig(pf.vars[k]) !== sig(v);
        return `<tr class="${changed && prev ? 'chg' : ''}"><td class="vn">${esc(k)}</td><td class="vv">${cellOf(v)}</td></tr>`;
      }).join('') || '<tr><td class="muted small" colspan="2">no variables yet</td></tr>';
      return `<div class="vz-frame ${idx === s.stack.length - 1 ? 'active' : ''}"><h6>${esc(fr.name)}</h6><table>${rows}</table></div>`;
    }).join('');

    const heap = s.heap || {}, pheap = prev?.heap || {};
    $('#vzh', body).innerHTML = Object.entries(heap).map(([id, h]) => {
      const isNew = prev && !pheap[id], changed = prev && pheap[id] && sig(pheap[id]) !== sig(h);
      let inner;
      if (h.attrs) inner = `<div class="hk">${esc(h.cls)} object</div><table>${Object.entries(h.attrs).map(([k, v]) => `<tr><td class="vn">${esc(k)}</td><td class="vv">${cellOf(v)}</td></tr>`).join('')}</table>`;
      else if (h.k === 'dict') inner = `<div class="hk">dict</div><table>${h.items.map(([k, v]) => `<tr><td class="vn">${cellOf(k)}</td><td class="vv">${cellOf(v)}</td></tr>`).join('')}${h.more ? `<tr><td class="muted small" colspan="2">+${h.more} more</td></tr>` : ''}</table>`;
      else inner = `<div class="hk">${esc(h.k)}</div><div class="cells">${h.items.map((it, ix) => `<div class="cell">${h.k === 'set' || h.k === 'frozenset' ? '' : `<i>${ix}</i>`}<div>${cellOf(it)}</div></div>`).join('')}${h.more ? `<div class="cell more">+${h.more}</div>` : ''}${h.items.length ? '' : '<div class="cell more">empty</div>'}</div>`;
      return `<div class="hbox ${isNew ? 'new' : changed ? 'chg' : ''}" data-hid="${id}">${inner}</div>`;
    }).join('') || '<div class="muted small" style="padding:6px 2px">Lists, dictionaries and objects will appear here as boxes, with arrows from the variables that point at them.</div>';

    $('#vzo', body).textContent = (data.output || '').slice(0, s.out) || '(nothing printed yet)';
    $('#vzr', body).value = i;
    $('#vzn', body).textContent = `Step ${i + 1} / ${steps.length}`;
    requestAnimationFrame(arrows);
  }

  function arrows() {
    const box = $('#vzs', body); if (!box) return;
    const svg = $('#vza', body), br = box.getBoundingClientRect();
    const W = box.scrollWidth, H = box.scrollHeight;
    svg.setAttribute('width', W); svg.setAttribute('height', H);
    let out = '<defs><marker id="vzah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="var(--accent)"/></marker></defs>';
    for (const src of $$('[data-ref]', box)) {
      const tgt = box.querySelector(`[data-hid="${src.dataset.ref}"]`); if (!tgt) continue;
      const a = src.getBoundingClientRect(), b = tgt.getBoundingClientRect();
      const x1 = a.left + a.width / 2 - br.left + box.scrollLeft, y1 = a.top + a.height / 2 - br.top + box.scrollTop;
      const x2 = b.left - br.left + box.scrollLeft - 2, y2 = b.top + 16 - br.top + box.scrollTop;
      const inHeap = !!src.closest('.vz-heap');
      const dx = inHeap ? 46 : Math.max(40, (x2 - x1) / 2);
      out += `<path d="M${x1} ${y1} C${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}" fill="none" stroke="var(--accent)" stroke-width="1.6" marker-end="url(#vzah)" opacity=".85"/>`;
    }
    svg.innerHTML = out;
  }

  const stopPlay = () => { clearInterval(timer); timer = null; $('#vzplay', body).innerHTML = '&#9654; Play'; };
  const startPlay = () => {
    if (i >= steps.length - 1) show(0);
    $('#vzplay', body).innerHTML = '&#10074;&#10074; Pause';
    timer = setInterval(() => { if (i >= steps.length - 1) stopPlay(); else show(i + 1); }, 750 / speed);
  };
  const toggle = () => (timer ? stopPlay() : startPlay());

  $('.vz-ctl', body).onclick = e => {
    const c = e.target.closest('[data-c]')?.dataset.c; if (!c) return;
    if (c === 'play') return toggle();
    stopPlay();
    show({ first: 0, prev: i - 1, next: i + 1, last: steps.length - 1 }[c]);
  };
  $('#vzr', body).oninput = e => { stopPlay(); show(+e.target.value); };
  $('#vzsp', body).onchange = e => { speed = +e.target.value; if (timer) { stopPlay(); startPlay(); } };
  $('#vzre', body).onclick = () => { cleanup(); stepView(body, modalEl, code, dayNo, $('#vzin', body).value ? $('#vzin', body).value + '\n' : ''); };
  $$('.vz-l', body).forEach(l => l.onclick = () => {                     // click a line: jump to the first time it runs
    const k = steps.findIndex(s => s.line === +l.dataset.n); if (k >= 0) { stopPlay(); show(k); }
  });
  const onKey = e => {
    if (e.target.matches('textarea, input[type=text], select')) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); stopPlay(); show(i + 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); stopPlay(); show(i - 1); }
    else if (e.key === ' ') { e.preventDefault(); toggle(); }
    else if (e.key === 'Home') { stopPlay(); show(0); } else if (e.key === 'End') { stopPlay(); show(steps.length - 1); }
  };
  modalEl.addEventListener('keydown', onKey);
  window.addEventListener('resize', arrows);
  const cleanup = () => { stopPlay(); modalEl.removeEventListener('keydown', onKey); window.removeEventListener('resize', arrows); };
  show(0);
  return cleanup;
}
