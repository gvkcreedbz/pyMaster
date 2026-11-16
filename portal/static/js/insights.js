import { $, $$, api, esc, md, enhance, toast, fmtMin } from './util.js';
import { S } from './state.js';
import * as tutor from './tutor.js';

const TYPE_LABEL = { usage: 'real-world use', concept: 'concept', debug: 'debugging', compare: 'compare', howto: 'how-to', review: 'review', confirm: 'confirm', extend: 'what-if / extend', other: 'other' };
const BLOOM_HINT = { remember: 'recall', understand: 'explain', apply: 'use', analyze: 'compare / why', evaluate: 'judge', create: 'design' };

export async function renderInsights(root) {
  S.area = 'insights'; S.dayNo = 0;
  tutor.setContext({ dayNo: null, tab: 'insights', label: 'Insights' });
  root.innerHTML = '<div class="muted">Crunching your journey…</div>';
  const my = S.seq;
  const [ins, ql] = await Promise.all([api('/insights'), api('/questions?limit=300')]);
  if (my !== S.seq) return;                       // you navigated away while this was loading
  const t = ins.totals;
  const kpi = (v, l, s = '') => `<div class="card stat"><b>${v}</b><span>${l}${s ? `<br><small>${s}</small>` : ''}</span></div>`;
  const maxType = Math.max(1, ...Object.values(ins.types)), maxBloom = Math.max(1, ...Object.values(ins.bloom));
  const hbars = (obj, max, labels = {}) => Object.entries(obj).sort((a, b) => b[1] - a[1]).map(([k, v]) =>
    `<div class="hb"><span class="lab">${esc(labels[k] || k)}</span><div class="bar"><i style="width:${100 * v / max}%"></i></div><span class="v">${v}</span></div>`).join('') || '<div class="muted small">Nothing yet. Ask the tutor a question to start.</div>';

  root.innerHTML = `<div class="fade-in">
    <div class="eyebrow">Insights</div><h1 class="page-title">How you're learning</h1>
    <div class="sub">Everything the portal notices: time, practice, questions and thinking patterns. ${esc(ins.pace.note)}</div>

    <div class="stats" style="grid-template-columns:repeat(5,1fr)">
      ${kpi(fmtMin(t.minutes), 'total focused time', `${t.active_days} active day${t.active_days === 1 ? '' : 's'}`)}
      ${kpi(ins.streak.current, 'day streak', `best ${ins.streak.best}`)}
      ${kpi(`${t.days_done}/30`, 'days complete')}
      ${kpi(`${t.ex_passed}/${t.ex_total}`, 'exercises passed', t.ex_per_hour ? `${t.ex_per_hour} per hour` : '')}
      ${kpi(t.questions, 'questions asked', t.valid_pct != null ? `${t.valid_pct}% valid · avg ${t.avg_quality}` : 'ask a few to see quality')}
    </div>

    <div class="grid2 sec">
      <div class="card pad"><h3 style="font-size:15px">Daily focus time</h3><div class="sub small" style="margin-bottom:8px">Last 35 days · minutes of active learning</div>${bars(ins.series)}</div>
      <div class="card pad"><h3 style="font-size:15px">Consistency</h3><div class="sub small" style="margin-bottom:10px">Each square is a day (oldest → today)</div>${heat(ins.series)}
        <div class="small muted" style="margin-top:10px">Skipping days is fine. The portal just welcomes you back with a recap.</div></div>
    </div>

    <div class="sec"><h3>What your questions say about your thinking</h3><div class="sub">${esc(ins.profile.label)}${ins.profile.traits.length ? ' · ' + ins.profile.traits.map(esc).join(' · ') : ''}</div>
      <div class="grid2">
        <div class="card pad"><b style="font-size:14px">Question types</b><div style="margin-top:8px">${hbars(ins.types, maxType, TYPE_LABEL)}</div>
          <hr style="border:none;border-top:1px solid var(--line);margin:14px 0"><b style="font-size:14px">Depth ladder</b><div class="sub small">How deep your questions go (recall → design)</div><div style="margin-top:8px">${Object.entries(ins.bloom).map(([k, v]) => `<div class="hb"><span class="lab">${k}<br><small class="muted">${BLOOM_HINT[k]}</small></span><div class="bar"><i style="width:${100 * v / maxBloom}%"></i></div><span class="v">${v}</span></div>`).join('')}</div></div>
        <div class="card pad"><b style="font-size:14px">Question quality over time</b><div class="sub small" style="margin-bottom:6px">Your typed questions · dashed line = "valid" threshold</div>${spark(ins.qtrend)}
          <div class="row" style="gap:6px;flex-wrap:wrap;margin:10px 0"><span class="chip">tried first: ${ins.attempt_first_pct ?? '–'}%</span><span class="chip">repeats: ${ins.duplicate_pct ?? '–'}%</span><span class="chip">hints used: ${t.hint_views}</span><span class="chip">solutions peeked: ${t.solution_views}</span></div>
          ${ins.profile.notes.map(n => `<div class="insight">${esc(n)}</div>`).join('')}</div>
      </div></div>

    <div class="grid2 sec">
      <div><h3>Suggested next steps</h3><div class="sub small" style="margin-bottom:8px">Suggestions only, you choose.</div>
        ${ins.recommendations.map(r => `<button class="rec" ${r.day ? `data-day="${r.day}"` : ''}><span>${{ next: '➡️', recap: '🧠', review: '🔁', quiz: '📝', habit: '🌱' }[r.kind] || '•'}</span><span>${esc(r.text)}</span></button>`).join('')}</div>
      <div><h3>Where you may need another look</h3><div class="sub small" style="margin-bottom:8px">Based on failing checks, quiz ratings and time spent.</div>
        ${ins.weak.length ? ins.weak.map(w => `<button class="rec" data-day="${w.day}"><span>🔎</span><span><b>Day ${w.day} · ${esc(w.title)}</b><br><span class="small muted">${esc(w.reasons.join(' · '))}</span></span></button>`).join('') : '<div class="insight">No weak spots flagged yet. Keep practising and I\'ll tell you.</div>'}</div>
    </div>

    <div class="sec"><h3>Reflection</h3><div class="sub small" style="margin-bottom:8px">A short read on your learning so far${S.overview.assistant.active !== 'offline' ? ' (written by your connected AI)' : ' (rule-based; connect an AI in ⚙ for a richer one)'}.</div>
      <div class="card pad" id="refl">${ins.last_reflection ? `<div class="md">${md(ins.last_reflection.text)}</div><div class="small muted">${esc(ins.last_reflection.ts.replace('T', ' '))} · ${esc(ins.last_reflection.provider)}</div>` : '<span class="muted">No reflection yet.</span>'}
        <div style="margin-top:12px"><button class="btn sm" id="reflect">✦ Generate a new reflection</button></div></div></div>

    <div class="sec"><h3>Day by day</h3><div class="sub small" style="margin-bottom:8px">Every day, whenever you did it. Order doesn't matter.</div>
      <div class="card scroll-y"><table class="t"><thead><tr><th>Day</th><th>Topic</th><th>Time</th><th style="width:150px">Exercises</th><th>Quiz</th><th>Qs</th><th>Confidence</th><th></th></tr></thead><tbody>
      ${ins.per_day.map(p => `<tr style="${p.started ? '' : 'opacity:.5'}" data-day="${p.n}"><td>${p.n}</td><td><a href="#/day/${p.n}" style="color:inherit;text-decoration:none">${esc(p.title.replace(/^🏆\s*/, ''))}</a></td><td>${fmtMin(p.minutes)}</td>
        <td><div class="bar ${p.ex_passed === p.ex_total && p.ex_total ? 'good' : ''}"><i style="width:${p.ex_total ? 100 * p.ex_passed / p.ex_total : 0}%"></i></div><span class="small muted">${p.ex_passed}/${p.ex_total}</span></td>
        <td>${p.quiz_rated}/${p.quiz_total}${p.quiz_rated ? ` <span class="small muted">(${p.quiz_got} ✓)</span>` : ''}</td><td>${p.questions || ''}</td><td>${p.confidence ? '★'.repeat(p.confidence) : ''}</td><td>${p.status === 'done' ? '<span class="chip good">done</span>' : ''}</td></tr>`).join('')}
      </tbody></table></div></div>

    <div class="sec"><div class="row"><h3>Question log</h3><span class="grow"></span><div class="seg" id="qf"><button data-f="all" class="on">All</button><button data-f="valid">Valid</button><button data-f="weak">Needs work</button></div>
      <a class="btn sm" href="/api/export" download>⬇ Export all data</a></div>
      <div class="sub small" style="margin-bottom:8px">Quality is scored locally from specificity, reasoning words, showing your own thinking and trying first. Quick-action clicks are logged but not graded.</div>
      <div class="card scroll-y"><table class="t"><thead><tr><th>When</th><th>Day</th><th>Question</th><th>Quality</th><th>Type</th><th>Depth</th></tr></thead><tbody id="qlog"></tbody></table></div></div>
  </div>`;

  const logBody = $('#qlog', root);
  const paintLog = f => {
    const items = ql.items.filter(q => f === 'all' || (f === 'valid' && q.quality != null && q.valid) || (f === 'weak' && q.quality != null && !q.valid));
    logBody.innerHTML = items.map(q => {
      const cls = q.quality == null ? '' : q.quality >= 70 ? 'good' : q.quality >= 45 ? 'accent' : 'warn';
      return `<tr><td class="small muted" style="white-space:nowrap">${esc(q.ts.slice(5, 16).replace('T', ' '))}</td><td>${q.day_no || '–'}</td><td>${esc(q.text.slice(0, 160))}${q.tips?.[0] ? `<div class="small muted">💡 ${esc(q.tips[0])}</div>` : ''}</td>
        <td>${q.quality == null ? '<span class="chip">quick</span>' : `<span class="chip ${cls}" title="${esc(q.flags.join(', '))}">${q.quality}</span>`}</td><td class="small">${esc(TYPE_LABEL[q.qtype] || q.qtype)}</td><td class="small">${esc(q.bloom)}</td></tr>`;
    }).join('') || '<tr><td colspan="6" class="muted">Nothing here yet.</td></tr>';
  };
  paintLog('all');
  $('#qf', root).onclick = e => { const f = e.target.dataset.f; if (!f) return; $$('#qf button', root).forEach(b => b.classList.toggle('on', b === e.target)); paintLog(f); };
  $$('[data-day]', root).forEach(b => { if (b.tagName === 'BUTTON') b.onclick = () => { location.hash = '#/day/' + b.dataset.day; }; });
  $('#reflect', root).onclick = async e => {
    e.target.disabled = true; e.target.textContent = 'Thinking…';
    try { const r = await api('/insights/reflect', { method: 'POST' }); $('#refl', root).innerHTML = `<div class="md">${md(r.text)}</div><div class="small muted">just now · ${esc(r.provider)}</div>`; }
    catch { toast('Could not generate a reflection'); }
  };
}

function bars(series) {
  const W = 620, H = 150, pad = 22, max = Math.max(30, ...series.map(s => s.minutes));
  const bw = (W - pad) / series.length;
  const rects = series.map((s, i) => {
    const h = Math.max(s.minutes ? 3 : 0, (H - 34) * s.minutes / max), x = pad + i * bw;
    return `<rect x="${x + 1.5}" y="${H - 22 - h}" width="${bw - 3}" height="${h}" rx="3" fill="var(--accent)" opacity="${s.minutes ? 0.9 : 0.15}"><title>${s.date}: ${s.minutes} min, ${s.questions} question(s)</title></rect>` +
      (s.questions ? `<circle cx="${x + bw / 2}" cy="${H - 22 - h - 6}" r="2.5" fill="var(--good)"/>` : '') +
      (i % 7 === 0 ? `<text x="${x}" y="${H - 6}">${s.date.slice(5)}</text>` : '');
  }).join('');
  return `<svg viewBox="0 0 ${W} ${H}" width="100%"><line x1="${pad}" x2="${W}" y1="${H - 22}" y2="${H - 22}" stroke="var(--line-2)"/><text x="0" y="12">${Math.round(max)}m</text>${rects}</svg>
    <div class="small muted"><span style="color:var(--good)">●</span> day with questions asked</div>`;
}
function heat(series) {
  const today = series[series.length - 1]?.date;
  return `<div class="heat">${series.map(s => `<i class="${s.minutes >= 60 ? 'h3' : s.minutes >= 20 ? 'h2' : s.minutes > 0 ? 'h1' : ''} ${s.date === today ? 'today' : ''}" title="${s.date}: ${s.minutes} min"></i>`).join('')}</div>`;
}
function spark(pts) {
  if (pts.length < 2) return '<div class="muted small" style="padding:14px 0">Ask a few questions to see your trend.</div>';
  const W = 360, H = 90, step = W / (pts.length - 1);
  const y = v => H - 8 - (H - 16) * v / 100;
  const line = pts.map((p, i) => `${i ? 'L' : 'M'}${(i * step).toFixed(1)},${y(p.quality).toFixed(1)}`).join(' ');
  return `<svg viewBox="0 0 ${W} ${H}" width="100%"><line x1="0" x2="${W}" y1="${y(45)}" y2="${y(45)}" stroke="var(--line-2)" stroke-dasharray="4 4"/>
    <path d="${line}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
    ${pts.map((p, i) => `<circle cx="${(i * step).toFixed(1)}" cy="${y(p.quality).toFixed(1)}" r="2.6" fill="${p.quality >= 45 ? 'var(--accent)' : 'var(--warn)'}"><title>Quality ${p.quality}</title></circle>`).join('')}</svg>`;
}
