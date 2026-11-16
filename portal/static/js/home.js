import { api, esc, fmtDate, fmtMin } from './util.js';
import { S } from './state.js';
import * as tutor from './tutor.js';

/** "Worth a second look": quiz questions you missed (spaced out) and exercises that still fail. Hidden when empty. */
async function loadReview(root) {
  const my = S.seq;
  try {
    const r = await api('/review');
    const host = root.querySelector('#review');
    if (my !== S.seq || !host) return;
    const q = r.quiz.filter(x => x.due).slice(0, 4), ex = r.exercises.slice(0, 3);
    if (!q.length && !ex.length) return;
    const short = s => (s.length > 90 ? s.slice(0, 89) + '…' : s);
    host.innerHTML = `<div class="card pad review"><div class="row" style="margin-bottom:8px"><h3>🔁 Worth a second look</h3>
        <span class="chip accent">${r.counts.quiz_due + r.counts.exercises}</span><span class="grow"></span>
        <span class="small muted">Questions you missed come back after 1 day (partly: 3 days). Re-rate them “Got it” and they leave.</span></div>
      <ul class="revlist">${q.map(x => `<li><a href="#/day/${x.day_no}/quiz"><span class="chip ${x.rating === 0 ? 'bad' : 'warn'}">${x.rating === 0 ? 'missed' : 'partly'}</span>
          <span class="rt"><b>Day ${x.day_no} · Q${x.q_no}</b> ${esc(short(x.q))}</span><span class="small muted">${x.age_days}d ago</span></a></li>`).join('')}
        ${ex.map(x => `<li><a href="#/day/${x.day_no}/practice"><span class="chip bad">failing</span>
          <span class="rt"><b>Day ${x.day_no} · ${esc(x.check_id)}</b> ${esc(x.name)}</span><span class="small muted">${x.fails} fail${x.fails === 1 ? '' : 's'}</span></a></li>`).join('')}</ul></div>`;
  } catch { /* review is a bonus: never break Home */ }
}

export function renderHome(root) {
  const o = S.overview, w = o.welcome;
  tutor.setContext({ dayNo: null, tab: 'home', label: 'Home' });
  const cur = o.days[w.current_day - 1];
  const headline = { start: 'Welcome to your 30 days', recap: 'Welcome back', resume: 'Good to see you', continue: 'Nice rhythm today' }[w.kind];
  const delta = w.delta;
  const pace = delta === 0 ? 'right on the suggested plan'
    : delta > 0 ? `${delta} day${delta > 1 ? 's' : ''} ahead of the suggested plan` : `${-delta} day${delta < -1 ? 's' : ''} behind the suggested plan`;
  const exDone = o.days.reduce((a, d) => a + d.ex_passed, 0), exAll = o.days.reduce((a, d) => a + d.ex_total, 0);
  const done = o.days.filter(d => d.status === 'done').length;

  const weeks = o.weeks.map(wk => {
    const ds = o.days.filter(d => d.n >= wk.from && d.n <= wk.to);
    const avg = Math.round(ds.reduce((a, d) => a + d.pct, 0) / ds.length);
    return `<div class="weekhead"><h3>Week ${wk.n} · ${esc(wk.title)}</h3><span class="sub">${esc(wk.sub)}</span><span class="grow"></span><span class="small muted">${avg}%</span></div>
      <div class="days">${ds.map(card).join('')}</div>`;
  }).join('');

  function card(d) {
    const isPlan = d.planned === o.today_date;
    const state = d.status === 'done' ? '<span class="chip good">✓ done</span>' : d.pct > 0 ? `<span class="chip accent">${d.pct}%</span>` : '';
    return `<button class="daycard ${d.status === 'done' ? 'done' : ''}" data-day="${d.n}">
      <div class="top"><span>${d.is_project ? '🏆 ' : ''}DAY ${String(d.n).padStart(2, '0')}</span>${state}</div>
      <div class="t">${esc(d.title.replace(/^🏆\s*/, ''))}</div>
      <div class="bar ${d.status === 'done' ? 'good' : ''}"><i style="width:${d.pct}%"></i></div>
      <div class="meta"><span>${d.ex_passed}/${d.ex_total} exercises</span><span class="${isPlan ? 'tag-now' : ''}">${isPlan ? 'suggested today' : fmtDate(d.planned)}</span></div>
    </button>`;
  }

  root.innerHTML = `<div class="fade-in">
    <div class="hero">
      <div class="eyebrow">${headline}</div>
      <h2>${esc(w.text)}</h2>
      ${w.recap.length ? `<ul>${w.recap.map(r => `<li>${esc(r)}</li>`).join('')}</ul>` : ''}
      <div class="row" style="margin-top:16px;flex-wrap:wrap">
        <button class="btn primary" data-day="${w.current_day}">${w.kind === 'start' ? 'Start Day 1' : `Continue Day ${w.current_day}`} →</button>
        ${w.kind === 'recap' ? `<button class="btn" id="recapq">Quiz me on the last lesson</button>` : ''}
        <span class="small muted">Suggested plan today: Day ${w.plan_day}. You're ${pace}. Pace is yours; nothing is locked.</span>
      </div>
    </div>
    <div class="stats">
      <div class="card stat"><b>${fmtMin(o.today.minutes)}</b><span>focused time today</span></div>
      <div class="card stat"><b>${w.streak.current}<small style="font-size:14px;font-weight:500"> day${w.streak.current === 1 ? '' : 's'}</small></b><span>current streak · best ${w.streak.best}</span></div>
      <div class="card stat"><b>${done}<small style="font-size:14px;font-weight:500"> / 30</small></b><span>days completed</span></div>
      <div class="card stat"><b>${exDone}<small style="font-size:14px;font-weight:500"> / ${exAll}</small></b><span>exercises passed</span></div>
      <div class="card stat"><b>${o.today.valid_questions}<small style="font-size:14px;font-weight:500"> / ${o.today.typed_questions}</small></b><span>good questions today</span></div>
    </div>
    <div id="review"></div>
    ${weeks}
    <a class="card pad bp-patterns" href="#/blueprints" style="margin-top:30px"><div class="bp-emoji">🧩</div>
      <div style="flex:1"><h3>Blueprints: how real systems are built</h3>
      <p class="sub">A live order tracker, a data + AI pipeline and an automation service, with diagrams, runnable code and 16 reusable patterns. Open them whenever you like; nothing is locked.</p></div><span class="btn sm">Explore &rarr;</span></a>
  </div>`;
  loadReview(root);
  root.querySelectorAll('[data-day]').forEach(b => b.onclick = () => { location.hash = `#/day/${b.dataset.day}`; });
  root.querySelector('#recapq')?.addEventListener('click', () => { tutor.setContext({ dayNo: w.current_day, tab: 'learn', label: `Day ${w.current_day} · ${cur.title}` }); tutor.ask('quiz'); });
}
