// Shared helpers: api, escaping, markdown, code highlighting, toasts, modal, editor factory.
export const $ = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => [...r.querySelectorAll(s)];

export const store = { sid: null };

export async function api(path, { method = 'GET', body } = {}) {
  const ctl = method === 'GET' ? new AbortController() : null;      // a hung page load becomes an error card, not an endless "Loading…"
  const timer = ctl && setTimeout(() => ctl.abort(), 30000);
  let r;
  try {
    r = await fetch('/api' + path, {
      method,
      headers: { 'x-portal': '1', ...(body ? { 'content-type': 'application/json' } : {}) },
      body: body ? JSON.stringify(body) : undefined,
      signal: ctl?.signal,
    });
  } catch (e) {
    throw e.name === 'AbortError' ? new Error('The portal did not answer within 30 s. Is it still running? Reload the page.') : e;
  } finally { clearTimeout(timer); }
  if (!r.ok) throw new Error(`${r.status} ${(await r.text()).slice(0, 200)}`);
  return r.json();
}

export function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const BAD_TAGS = new Set(['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'LINK', 'META', 'FORM', 'INPUT', 'BUTTON', 'TEXTAREA']);
function sanitize(html) {
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const walk = n => {
    for (const c of [...n.children]) {
      if (BAD_TAGS.has(c.tagName)) { c.remove(); continue; }
      for (const a of [...c.attributes]) {
        if (a.name.startsWith('on') || /^\s*javascript:/i.test(a.value)) c.removeAttribute(a.name);
      }
      if (c.tagName === 'A') { c.target = '_blank'; c.rel = 'noopener noreferrer'; }
      walk(c);
    }
  };
  walk(doc.body);
  return doc.body.innerHTML;
}

export function md(text, trusted = false) {
  const html = marked.parse(text || '', { gfm: true, breaks: false });
  return trusted ? html : sanitize(html);
}

const looksSql = t => /^\s*(--[^\n]*\n\s*)*(select|with|insert|update|delete|create|alter|drop)\b/i.test(t);

/** Highlight fenced code blocks and add Copy / Try / Visualize buttons; draw ```mermaid blocks as diagrams.
 *  Pass diagrams:false while text is still streaming in (half-written diagrams can't be drawn). */
export function enhance(root, { tryIt = true, diagrams = true, visualize = true } = {}) {
  for (const pre of $$('pre', root)) {
    const code = pre.querySelector('code');
    if (!code || pre.dataset.done) continue;
    const lang = (code.className.match(/language-(\w+)/) || [])[1];
    const text = code.textContent.replace(/\n$/, '');
    if (lang === 'mermaid') {
      if (!diagrams) { pre.innerHTML = '<div class="mmd-wait">Drawing a diagram…</div>'; pre.className = 'mmd-pre'; continue; }
      const holder = document.createElement('div');
      pre.replaceWith(holder);
      import('./diagram.js').then(m => m.draw(holder, text)).catch(() => { holder.textContent = text; });
      continue;
    }
    pre.dataset.done = '1';
    const sql = lang === 'sql' || (!lang && looksSql(text));
    const pythonish = !sql && (!lang || lang === 'python' || lang === 'py');
    if (pythonish && typeof CodeMirror !== 'undefined' && CodeMirror.runMode) {
      code.textContent = '';
      CodeMirror.runMode(text, 'python', code);
    }
    const shellish = /^\s*(>>>|\$ |C:\\|PS )/m.test(text);                      // terminal / REPL transcripts aren't programs
    const canViz = visualize && (pythonish || sql) && !shellish && text.trim().split('\n').length >= 2;
    const canTry = tryIt && pythonish && !shellish;
    const bar = document.createElement('div');
    bar.className = 'codebar';
    bar.innerHTML = `<button data-a="copy">Copy</button>${canViz ? '<button data-a="viz" title="See this code as a diagram / step through it">&#128065; Visualize</button>' : ''}${canTry ? '<button data-a="try" title="Open in the playground beside the lesson">&#9654; Try</button>' : ''}`;
    bar.addEventListener('click', e => {
      const a = e.target.dataset.a;
      if (a === 'copy') { navigator.clipboard?.writeText(text); toast('Copied'); }
      if (a === 'try') document.dispatchEvent(new CustomEvent('pm:try', { detail: { code: text } }));
      if (a === 'viz') document.dispatchEvent(new CustomEvent('pm:visualize', { detail: { code: text, lang: sql ? 'sql' : 'python' } }));
    });
    pre.appendChild(bar);
  }
}

export function toast(msg, ms = 2200) {
  const t = document.createElement('div');
  t.className = 'toast'; t.textContent = msg;
  $('#toasts').appendChild(t);
  setTimeout(() => t.remove(), ms);
}

export function modal(html, { onMount, wide, xl } = {}) {
  const root = $('#modal-root');
  root.innerHTML = `<div class="overlay"><div class="modal card ${xl ? 'xl' : ''}" tabindex="-1" ${wide ? 'style="width:min(760px,calc(100vw - 32px))"' : ''}>${html}</div></div>`;
  const close = () => { root.innerHTML = ''; document.removeEventListener('keydown', onKey); };
  const onKey = e => { if (e.key === 'Escape') close(); };
  document.addEventListener('keydown', onKey);
  $('.overlay', root).addEventListener('mousedown', e => { if (e.target.classList.contains('overlay')) close(); });
  onMount?.($('.modal', root), close);
  return close;
}

export function fmtMin(m) {
  if (!m) return '0m';
  if (m < 60) return `${Math.round(m)}m`;
  return `${Math.floor(m / 60)}h ${Math.round(m % 60)}m`;
}
export function fmtDate(iso) {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });
}

export function editor(container, { value = '', onChange, onRun, onSelection, readOnly = false } = {}) {
  const cm = CodeMirror(container, {
    value, mode: 'python', theme: 'pj', lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false,
    matchBrackets: true, autoCloseBrackets: true, styleActiveLine: false, readOnly, viewportMargin: 30,
    extraKeys: {
      Tab: c => (c.somethingSelected() ? c.indentSelection('add') : c.replaceSelection('    ', 'end')),
      'Shift-Tab': c => c.indentSelection('subtract'),
      'Ctrl-Enter': () => onRun?.(), 'Cmd-Enter': () => onRun?.(),
    },
  });
  cm.on('focus', () => document.dispatchEvent(new CustomEvent('pm:editorfocus', { detail: { pane: container.closest('.pane')?.dataset.pane || 'lesson' } })));
  if (onChange) cm.on('change', () => onChange(cm.getValue()));
  if (onSelection) cm.on('cursorActivity', () => onSelection(cm.somethingSelected() ? cm.getSelection() : ''));
  return cm;
}

export const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
