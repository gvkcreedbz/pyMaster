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
/** Which course this server is serving (set by the page: window.TRACK). */
export const TRK = window.TRACK || { id: 'python', name: 'Py Master', short: 'Python', fence: 'python', cm_mode: 'python', ext: '.py', input_fn: 'input()', other: 'java', other_port: 8766 };

/** Java lesson snippets are often a few statements: wrap them so Try / Visualize run as a whole program. */
export function wrapJava(code) {
  if (TRK.id !== 'java') return code;
  if (/\b(class|interface|enum|record)\s+\w+/.test(code) && /\bmain\s*\(/.test(code)) return code;
  const lines = code.split('\n');
  const imports = lines.filter(l => /^\s*import\s/.test(l));
  const body = lines.filter(l => !/^\s*import\s/.test(l)).map(l => '        ' + l).join('\n');
  return (imports.length ? imports.join('\n') + '\n\n' : '') + 'class Play {\n    public static void main(String[] args) throws Exception {\n' + body + '\n    }\n}\n';
}

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
    const pythonish = !sql && (TRK.id === 'java' ? lang === 'java' : (!lang || lang === 'python' || lang === 'py'));
    if (pythonish && typeof CodeMirror !== 'undefined' && CodeMirror.runMode) {
      code.textContent = '';
      CodeMirror.runMode(text, TRK.cm_mode, code);
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
      if (a === 'try') document.dispatchEvent(new CustomEvent('pm:try', { detail: { code: wrapJava(text) } }));
      if (a === 'viz') document.dispatchEvent(new CustomEvent('pm:visualize', { detail: { code: wrapJava(text), lang: sql ? 'sql' : TRK.fence } }));
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

let modalSeq = 0, closeActive = null, modalOpener = null;
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]):not([type=hidden]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
/** Open a dialog. Focus management: role=dialog + aria-modal + labelled by its first heading, Tab is trapped inside,
 *  Esc closes, and focus goes back to whatever opened it. */
export function modal(html, { onMount, wide, xl, label } = {}) {
  const root = $('#modal-root');
  if (closeActive) closeActive(false);                                   // a second dialog replaces the first (and frees its key handler)
  else modalOpener = document.activeElement;
  root.innerHTML = `<div class="overlay"><div class="modal card ${xl ? 'xl' : ''}" role="dialog" aria-modal="true" tabindex="-1" ${wide ? 'style="width:min(760px,calc(100vw - 32px))"' : ''}>${html}</div></div>`;
  const box = $('.modal', root);
  const head = $('h1, h2, h3, h4', box);
  if (head) { head.id = head.id || 'modal-title-' + (++modalSeq); box.setAttribute('aria-labelledby', head.id); }
  else box.setAttribute('aria-label', label || 'Dialog');
  const items = () => $$(FOCUSABLE, box).filter(el => el.offsetParent !== null || el === document.activeElement);
  const close = (restore = true) => {
    if (closeActive !== close) return;                                     // already closed or replaced by a newer dialog
    root.innerHTML = '';
    document.removeEventListener('keydown', onKey, true);
    document.removeEventListener('focusin', onFocusIn);
    closeActive = null;
    const back = modalOpener; modalOpener = null;
    if (restore && back && back.isConnected && back !== document.body) { try { back.focus({ preventScroll: true }); } catch { /* element gone */ } }
  };
  const onKey = e => {
    if (e.key === 'Escape' && !e.defaultPrevented && !$('#palette')) { close(); return; }
    if (e.key !== 'Tab' || e.ctrlKey || e.altKey || e.metaKey) return;
    const f = items();
    if (!f.length) { e.preventDefault(); box.focus(); return; }
    const first = f[0], last = f[f.length - 1], a = document.activeElement;
    if (!box.contains(a)) { e.preventDefault(); first.focus(); }
    else if (e.shiftKey && (a === first || a === box)) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && a === last) { e.preventDefault(); first.focus(); }
  };
  const onFocusIn = e => { if (!box.contains(e.target) && !e.target.closest?.('#palette, .toasts')) box.focus(); };
  closeActive = close;
  document.addEventListener('keydown', onKey, true);
  document.addEventListener('focusin', onFocusIn);
  $('.overlay', root).addEventListener('mousedown', e => { if (e.target.classList.contains('overlay')) close(); });
  (box.querySelector('[autofocus]') || box).focus({ preventScroll: true });
  onMount?.(box, close);
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
    value, mode: TRK.cm_mode, theme: 'pj', lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false,
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
