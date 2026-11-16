// Mermaid diagrams (vendored, loaded on first use). Used for flowcharts of code, SQL order and tutor explanations.
import { esc, modal, toast, $, $$ } from './util.js';

let loading = null;
export function loadMermaid() {
  if (window.mermaid) return Promise.resolve(window.mermaid);
  return loading ||= new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = '/static/vendor/mermaid.min.js';
    s.onload = () => res(window.mermaid);
    s.onerror = () => { loading = null; rej(new Error('Could not load the diagram engine')); };
    document.head.appendChild(s);
  });
}

function themeVars() {
  const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
  const dark = document.documentElement.dataset.theme === 'dark';
  return {
    darkMode: dark, background: v('--panel'), fontFamily: 'Inter, ui-sans-serif, system-ui, "Segoe UI", sans-serif', fontSize: '14px',
    primaryColor: v('--accent-soft'), primaryBorderColor: v('--accent'), primaryTextColor: v('--ink'),
    secondaryColor: v('--panel-2'), tertiaryColor: v('--panel-2'), lineColor: v('--muted'), textColor: v('--ink'),
    mainBkg: v('--accent-soft'), nodeBorder: v('--accent'), clusterBkg: v('--panel-2'), clusterBorder: v('--line-2'),
    edgeLabelBackground: v('--panel'), noteBkgColor: v('--warn-soft'), noteTextColor: v('--ink'), noteBorderColor: v('--warn'),
    actorBkg: v('--accent-soft'), actorBorder: v('--accent'), actorTextColor: v('--ink'), signalColor: v('--ink-2'), signalTextColor: v('--ink'),
  };
}

let chain = Promise.resolve(), counter = 0;
/** Render Mermaid source to an SVG string. Calls are queued (the engine isn't re-entrant). */
export function renderSvg(src) {
  const job = chain.then(async () => {
    const m = await loadMermaid();
    m.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'base', themeVariables: themeVars(),
      flowchart: { htmlLabels: true, curve: 'basis', useMaxWidth: true, padding: 10 }, sequence: { useMaxWidth: true } });
    const id = 'pmmd' + (++counter);
    try { return (await m.render(id, src)).svg; }
    finally { document.getElementById(id)?.remove(); document.getElementById('d' + id)?.remove(); }
  });
  chain = job.catch(() => {});
  return job;
}

/** Fill `el` with a rendered diagram plus Enlarge / Copy source buttons. */
export async function draw(el, src, caption = '') {
  el.classList.add('mmd'); el.dataset.src = src;
  el.innerHTML = '<div class="mmd-wait">Drawing…</div>';
  try {
    const svg = await renderSvg(src);
    el.innerHTML = `<div class="mmd-svg">${svg}</div>${caption ? `<div class="mmd-cap">${esc(caption)}</div>` : ''}
      <div class="mmd-bar"><button data-a="big" title="Open larger">&#10530; Enlarge</button><button data-a="copy" title="Copy the diagram source">Copy source</button></div>`;
    el.querySelector('.mmd-bar').onclick = e => {
      const a = e.target.dataset.a;
      if (a === 'copy') { navigator.clipboard?.writeText(src); toast('Diagram source copied'); }
      if (a === 'big') modal(`<div class="mmd-big">${el.querySelector('.mmd-svg').innerHTML}</div>${caption ? `<div class="mmd-cap">${esc(caption)}</div>` : ''}
        <div class="row" style="justify-content:flex-end;margin-top:12px"><button class="btn" data-x>Close</button></div>`, { xl: true, onMount: (m, close) => { $('[data-x]', m).onclick = close; } });
    };
  } catch (e) {
    el.innerHTML = `<div class="mmd-err">Couldn't draw this diagram (${esc(String(e.message || e).split('\n')[0].slice(0, 120))}).</div><pre class="out">${esc(src)}</pre>`;
  }
}

/** Re-draw every diagram on screen (after a light/dark switch). */
export function redrawAll() { $$('.mmd[data-src]').forEach(el => draw(el, el.dataset.src, $('.mmd-cap', el)?.textContent || '')); }
