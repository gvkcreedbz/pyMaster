// A toolbar + results area wired to POST /api/run. Used by Code-along, Practice and Playground.
import { $, api, esc, store } from './util.js';

export function mountRunner(host, { kind, dayNo, getCode, onResult, label }) {
  host.innerHTML = `
    <div class="toolbar">
      <button class="btn primary" data-run>▶ ${label || 'Run'} <span class="small" style="opacity:.7">Ctrl+Enter</span></button>
      <button class="btn ghost sm" data-stdin title="Provide text for input() calls">⌨ Input</button>
      <span class="row" data-slot></span><span class="grow"></span><span class="small muted" data-status></span>
    </div>
    <textarea class="field mono" data-in rows="3" placeholder="Answers for input() calls, one per line" style="display:none;margin-bottom:8px"></textarea>
    <div class="results" data-res></div>`;
  const btn = $('[data-run]', host), status = $('[data-status]', host), res = $('[data-res]', host), tin = $('[data-in]', host);
  let lastOutput = '';
  $('[data-stdin]', host).onclick = () => { tin.style.display = tin.style.display === 'none' ? 'block' : 'none'; if (tin.style.display === 'block') tin.focus(); };

  async function run() {
    btn.disabled = true; status.textContent = 'Running…';
    try {
      const r = await api('/run', { method: 'POST', body: { kind, day_no: dayNo || null, code: getCode(), stdin: tin.value ? tin.value + '\n' : '', session_id: store.sid } });
      lastOutput = r.output || '';
      paint(r);
      status.textContent = `${(r.ms / 1000).toFixed(2)}s`;
      onResult?.(r);
    } catch (e) {
      res.innerHTML = `<pre class="out err">${esc(e.message)}</pre>`; status.textContent = '';
    } finally { btn.disabled = false; }
  }
  btn.onclick = run;

  function paint(r) {
    let html = '';
    if (r.results?.length) {
      const total = r.total ?? r.results.length, passed = r.passed ?? r.results.filter(x => x.status === 'PASS').length;
      const pct = total ? Math.round(100 * passed / total) : 0;
      html += `<div class="score"><span class="big">${passed}/${total}</span><div class="grow"><div class="bar ${passed === total ? 'good' : ''}"><i style="width:${pct}%"></i></div></div>
        <span class="chip ${passed === total ? 'good' : 'accent'}">${passed === total ? 'all checks pass 🎉' : 'checks passed'}</span></div>`;
      html += '<div class="checks">' + r.results.map(c =>
        `<div class="check ${c.status === 'PASS' ? 'pass' : 'fail'}"><span>${c.status === 'PASS' ? '✓' : '✗'}</span><span><span class="id">${esc(c.id)}</span> ${esc(c.name)}${c.detail ? `<span class="d">${esc(c.detail)}</span>` : ''}</span></div>`).join('') + '</div>';
    }
    const bad = !r.ok || /Traceback/.test(r.output || '');
    const out = `<pre class="out ${bad ? 'err' : ''}">${esc(r.output || '(no output)')}</pre>`;
    html += r.results?.length ? `<details style="margin-top:10px"><summary class="small muted" style="cursor:pointer">Console output</summary>${out}</details>` : out;
    if (r.hint) html += `<div class="hintbox">💡 ${esc(r.hint)}</div>`;
    res.innerHTML = html;
  }
  return { run, slot: $('[data-slot]', host), getOutput: () => lastOutput };
}
