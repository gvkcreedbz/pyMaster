// Blueprints: three real-world full-stack projects + the pattern catalog. Guide (diagrams) | Code | Run the demo.
import { $, $$, api, md, enhance, esc, store } from './util.js';
import { S } from './state.js';
import * as tutor from './tutor.js';

const chips = (arr, cls = '') => arr.map(x => `<span class="chip ${cls}">${esc(x)}</span>`).join('');

export async function renderBlueprints(root, id, tab) {
  S.area = 'blueprints'; S.dayNo = 0;
  const my = S.seq;
  const { items } = await api('/blueprints');
  if (my !== S.seq) return;
  const meta = id && items.find(i => i.id === id);
  if (id && !meta) { root.innerHTML = `<div class="card pad"><b>No blueprint called “${esc(id)}”.</b> <a href="#/blueprints">See all blueprints</a></div>`; return; }
  tutor.setContext({ dayNo: null, tab: 'blueprints', label: meta ? 'Blueprint · ' + meta.title : 'Blueprints' });
  if (!meta) return overview(root, items);

  const projects = items.filter(i => i.id !== 'patterns');
  root.innerHTML = `<div class="fade-in"><div class="eyebrow">Blueprints</div>
    <div class="lib bp-lib" style="margin-top:14px"><nav>
      <h6>Projects</h6>${projects.map(i => `<button data-id="${i.id}" class="${i.id === id ? 'on' : ''}">${i.emoji} ${esc(i.title)}</button>`).join('')}
      <h6>Reference</h6>${items.filter(i => i.id === 'patterns').map(i => `<button data-id="${i.id}" class="${i.id === id ? 'on' : ''}">${i.emoji} ${esc(i.title)}</button>`).join('')}
      <h6>&nbsp;</h6><button data-id="">&larr; All blueprints</button></nav>
    <div style="min-width:0">
      <div class="bp-head"><h1 class="page-title">${meta.emoji} ${esc(meta.title)}</h1>
        <div class="sub">${esc(meta.tagline)}</div>
        <div class="metarow">${chips([meta.kind, meta.level, '≈ ' + meta.minutes + ' min'])}${chips(meta.stack, 'accent')}</div></div>
      ${meta.demo ? `<div class="tabs"><button class="tab on" data-t="guide">Guide</button><button class="tab" data-t="code">Code</button><button class="tab" data-t="run">&#9654; Run the demo</button></div>` : ''}
      <div id="bp-body"></div></div></div></div>`;
  $$('nav button', root).forEach(b => b.onclick = () => { location.hash = '#/blueprints' + (b.dataset.id ? '/' + b.dataset.id : ''); });
  const body = $('#bp-body', root);
  const show = t => {
    $$('.tab', root).forEach(x => x.classList.toggle('on', x.dataset.t === t));
    ({ guide, code, run })[t](body, meta, my);
  };
  $$('.tab', root).forEach(b => b.onclick = () => show(b.dataset.t));
  show(['code', 'run'].includes(tab) ? tab : 'guide');
}

function overview(root, items) {
  const projects = items.filter(i => i.id !== 'patterns'), pat = items.find(i => i.id === 'patterns');
  root.innerHTML = `<div class="fade-in">
    <div class="hero"><div class="eyebrow">After the basics: how real systems are built</div>
      <h2>Blueprints: full-stack Python, explained</h2>
      <p class="sub" style="max-width:62ch;margin-top:6px">Three real-time style projects (a live backend, a data + AI pipeline, an automation service). Each one has an architecture diagram, the data model, the exact Python features used and the days that taught them, a runnable reference implementation, what breaks in production, and milestones to build it yourself.</p></div>
    <div class="bp-grid">${projects.map(p => `
      <a class="card bp-card" href="#/blueprints/${p.id}">
        <div class="bp-emoji">${p.emoji}</div>
        <div class="eyebrow">${esc(p.kind)}</div>
        <h3>${esc(p.title)}</h3>
        <p class="sub">${esc(p.tagline)}</p>
        <div class="bp-chips">${chips(p.stack.slice(0, 5))}</div>
        <div class="bp-pat"><b>Patterns:</b> ${esc(p.patterns.join(' · '))}</div>
        <div class="bp-foot"><span class="small muted">${esc(p.level)} · ≈ ${p.minutes} min</span><span class="btn sm">Open &rarr;</span></div>
      </a>`).join('')}</div>
    ${pat ? `<a class="card pad bp-patterns" href="#/blueprints/patterns"><div class="bp-emoji">${pat.emoji}</div><div style="flex:1"><h3>${esc(pat.title)}</h3><p class="sub">${esc(pat.tagline)}</p></div><span class="btn sm">Open &rarr;</span></a>` : ''}
    <div class="card pad" style="margin-top:18px"><h3 style="margin-bottom:8px">How to use a blueprint</h3>
      <ol class="small" style="margin:0;padding-left:20px;line-height:1.8;color:var(--ink-2)">
        <li><b>Guide:</b> read the picture first (big idea), then the data model, then the Python table.</li>
        <li><b>Run the demo:</b> watch the system behave; every line it prints is explained in the guide.</li>
        <li><b>Code:</b> read the file top to bottom; press <b>&#9654; Try</b> to load it into the playground and change things.</li>
        <li><b>Ask the assistant</b> (Ctrl+K) about any part: highlight code and press <b>Where is this used?</b></li>
        <li><b>Build it yourself:</b> finish the milestones at the end of each guide.</li></ol></div></div>`;
}

async function guide(body, meta, my) {
  body.innerHTML = '<div class="muted">Loading…</div>';
  const r = await api(`/blueprints/${meta.id}?session_id=${encodeURIComponent(store.sid || '')}`);
  if (my !== S.seq) return;
  body.innerHTML = '<div class="md" id="bp-doc" style="max-width:none"></div>';
  const el = $('#bp-doc', body);
  el.innerHTML = md(r.text.replace(/^#\s.*\n/, ''), true);          // the page already shows the title
  enhance(el);
}

async function code(body, meta, my) {
  const file = meta.files[0];
  body.innerHTML = `<div class="row bp-files">${meta.files.map((f, i) => `<button class="btn sm ${i ? '' : 'primary'}" data-f="${f}">${esc(f)}</button>`).join('')}
    <span class="grow"></span><span class="small muted">Read-only here. &#9654; Try copies it into the playground.</span></div><div id="bp-src"></div>`;
  const load = async f => {
    $$('[data-f]', body).forEach(b => b.classList.toggle('primary', b.dataset.f === f));
    const r = await api(`/blueprints/${meta.id}/file/${encodeURIComponent(f)}`);
    if (my !== S.seq) return;
    const src = $('#bp-src', body);
    src.innerHTML = `<div class="md" style="max-width:none"><pre><code class="language-python"></code></pre></div>`;
    $('code', src).textContent = r.text;
    enhance(src, { visualize: false });
  };
  $$('[data-f]', body).forEach(b => b.onclick = () => load(b.dataset.f));
  await load(file);
}

function run(body, meta) {
  body.innerHTML = `<div class="card pad"><div class="row"><button class="btn primary" id="bp-run">&#9654; Run ${esc(meta.demo)}</button>
      <span class="small muted" id="bp-status">Runs in a private copy, no network needed. Takes a few seconds.</span></div>
    <div id="bp-out" style="margin-top:12px"></div></div>`;
  $('#bp-run', body).onclick = async () => {
    const btn = $('#bp-run', body), out = $('#bp-out', body), st = $('#bp-status', body);
    btn.disabled = true; st.textContent = 'Running…'; out.innerHTML = '';
    try {
      const r = await api(`/blueprints/${meta.id}/run`, { method: 'POST', body: { session_id: store.sid } });
      st.textContent = `${r.ok ? 'finished' : 'failed'} in ${(r.ms / 1000).toFixed(2)}s`;
      out.innerHTML = `<pre class="out ${r.ok ? '' : 'err'}">${esc(r.output || '(no output)')}</pre>${r.hint ? `<div class="hintbox">💡 ${esc(r.hint)}</div>` : ''}
        <p class="small muted">Not sure what a line means? Highlight it and ask the assistant, or open the <b>Guide</b> tab: every step of this output is explained there.</p>`;
    } catch (e) { out.innerHTML = `<pre class="out err">${esc(e.message)}</pre>`; st.textContent = ''; }
    finally { btn.disabled = false; }
  };
}
