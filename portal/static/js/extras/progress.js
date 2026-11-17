// Progress extension: XP chip + daily-goal ring, popover (level, streak, goal, badges), quiet toasts,
// and on Home a "Today" card with the 10-minute warm-up. Server side: portal/ex_progress.py (/api/progress/*).
// Everything is optional: "Show XP and badges" (localStorage) hides the chip and all toasts.
const LS_SHOW = 'pm-progress-show';
let C, data = null, badgesAll = null, inflight = null, popEl = null, timer = null;

const shown = () => localStorage.getItem(LS_SHOW) !== '0';
const seenKey = () => 'pm-progress-seen-' + C.TRK.id;
const nm = s => String(s).replace(/`/g, '');
const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

function ring(pct, size = 22, stroke = 3.5) {
  const r = 18 - stroke / 2, c = 2 * Math.PI * r;
  return `<svg class="px-ring" viewBox="0 0 36 36" width="${size}" height="${size}" aria-hidden="true">
    <circle class="bg" cx="18" cy="18" r="${r}" fill="none" stroke-width="${stroke}"/>
    <circle class="fg" cx="18" cy="18" r="${r}" fill="none" stroke-width="${stroke}" stroke-linecap="round"
      stroke-dasharray="${(clamp(pct, 0, 100) / 100 * c).toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 18 18)"/></svg>`;
}
const goalText = g => `${Math.floor(g.done)} of ${g.target} ${g.unit}`;

// ---- chip in the top bar ---------------------------------------------------------------------------------------------
function buildChip() {
  const host = C.$('#topbar-extras');
  if (!host || C.$('#px-chip')) return;
  const b = document.createElement('button');
  b.id = 'px-chip'; b.className = 'px-chip'; b.type = 'button';
  b.setAttribute('aria-haspopup', 'dialog'); b.setAttribute('aria-expanded', 'false');
  b.onclick = e => { e.stopPropagation(); popEl ? closePop() : openPop(); };
  host.appendChild(b);
  paintChip();
}
function paintChip() {
  const b = C.$('#px-chip');
  if (!b) return;
  b.hidden = !shown();
  if (!data) { b.innerHTML = ring(0) + '<span class="px-lv">XP</span>'; return; }
  b.innerHTML = `${ring(data.goal.pct)}<span class="px-lv">Lv ${data.level.n}</span><span class="px-xp">${data.xp.total} XP</span>`;
  b.title = `${data.level.name} · ${data.xp.total} XP · today's goal ${goalText(data.goal)}${data.goal.met ? ' (done!)' : ''}`;
  b.setAttribute('aria-label', `Progress: level ${data.level.n} ${data.level.name}, ${data.xp.total} XP. Open details.`);
  b.classList.toggle('met', data.goal.met);
}

// ---- popover -------------------------------------------------------------------------------------------------------
function closePop() {
  popEl?.remove(); popEl = null;
  C.$('#px-chip')?.setAttribute('aria-expanded', 'false');
  document.removeEventListener('mousedown', outside, true); document.removeEventListener('keydown', onKey);
}
const outside = e => { if (popEl && !popEl.contains(e.target) && !e.target.closest('#px-chip')) closePop(); };
const onKey = e => { if (e.key === 'Escape' && popEl) { closePop(); C.$('#px-chip')?.focus(); } };

async function openPop() {
  if (!data) await refresh();
  if (!data) return;
  popEl = document.createElement('div');
  popEl.className = 'px-pop card'; popEl.setAttribute('role', 'dialog'); popEl.setAttribute('aria-label', 'Your progress');
  document.body.appendChild(popEl);
  C.$('#px-chip').setAttribute('aria-expanded', 'true');
  document.addEventListener('mousedown', outside, true); document.addEventListener('keydown', onKey);
  paintPop();
  loadBadges();
  popEl.querySelector('button, input')?.focus();
}
function loadBadges() {
  return C.api('/progress/badges').then(r => { badgesAll = r.items; paintBadges(); })
    .catch(() => { const h = popEl && C.$('#px-badges', popEl); if (h) h.innerHTML = '<span class="small muted">Could not load badges.</span>'; });
}

function paintPop() {
  if (!popEl) return;
  if (popEl.querySelector('#px-goalform:not([hidden])')) return;      // do not wipe what is being typed
  const d = data, L = d.level, st = d.streak, g = d.goal;
  const keepForm = false;
  const nextTxt = L.next_xp == null ? 'Top level reached. Keep going for the fun of it.' : `${L.to_next} XP to ${C.esc(L.next_name)}`;
  const streakTxt = st.welcome_back ? `<span class="px-wb">${C.esc(st.welcome_back.text)}</span>`
    : st.current > 0 ? `<b>${st.current}-day streak</b> <span class="muted">best ${st.best}</span>${st.today_active ? '' : ' <span class="muted">· practise today to extend it</span>'}`
    : '<span class="muted">No streak yet. Any run, quiz answer or focused minute today starts one.</span>';
  popEl.innerHTML = `
    <div class="px-head"><div><div class="px-lvname">${C.esc(L.name)}</div><div class="small muted">Level ${L.n} · ${d.xp.total} XP · +${d.xp.today} today</div></div>
      <button class="iconbtn" data-x title="Close (Esc)" aria-label="Close">&#10005;</button></div>
    <div class="px-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${L.pct}"><i style="width:${L.pct}%"></i></div>
    <div class="small muted px-next">${nextTxt}</div>
    <div class="px-sec">${streakTxt}</div>
    <div class="px-sec px-goal ${g.met ? 'met' : ''}">${ring(g.pct, 46, 4)}
      <div class="px-goaltxt"><b>${g.met ? 'Goal reached' : "Today's goal"}</b><div class="small muted">${goalText(g)}</div></div>
      <button class="btn sm" data-goal aria-expanded="${keepForm}">Change</button></div>
    <form id="px-goalform" class="px-goalform" ${keepForm ? '' : 'hidden'}>
      <label class="small">Goal per day
        <select name="kind" aria-label="Goal type"><option value="min">minutes of focus</option><option value="xp">XP</option></select></label>
      <input name="target" type="number" inputmode="numeric" aria-label="Goal amount" required>
      <button class="btn sm primary" type="submit">Save</button><span class="small muted" id="px-goalerr" role="alert"></span></form>
    <div class="px-sec"><div class="px-h">Badges <span class="muted">${d.badges_earned.length} / ${d.badges_total}</span></div><div id="px-badges" class="px-badges"></div></div>
    <label class="px-opt small"><input type="checkbox" id="px-show" ${shown() ? 'checked' : ''}> Show XP and badges in the top bar</label>
    <p class="small muted px-fine">XP comes from what you already do: passing checks, quiz answers, finished days, focused minutes, good questions. Nothing is ever taken away.</p>`;
  const form = C.$('#px-goalform', popEl);
  form.kind.value = g.kind; form.target.value = g.target;
  const lim = g.limits[g.kind]; form.target.min = lim[0]; form.target.max = lim[1];
  form.kind.onchange = () => { const l = g.limits[form.kind.value]; form.target.min = l[0]; form.target.max = l[1]; form.target.value = form.kind.value === 'min' ? 30 : 100; };
  C.$('[data-x]', popEl).onclick = () => { closePop(); C.$('#px-chip')?.focus(); };
  C.$('[data-goal]', popEl).onclick = e => { form.hidden = !form.hidden; e.target.setAttribute('aria-expanded', String(!form.hidden)); if (!form.hidden) form.target.focus(); };
  form.onsubmit = async e => {
    e.preventDefault();
    try {
      await C.api('/progress/goal', { method: 'POST', body: { kind: form.kind.value, target: parseInt(form.target.value, 10) } });
      form.hidden = true; await refresh(); C.toast('Daily goal saved');
    } catch (err) { C.$('#px-goalerr', popEl).textContent = /target must be[^"}]*/.exec(err.message)?.[0] || 'Pick a whole number in range.'; }
  };
  C.$('#px-show', popEl).onchange = e => {
    localStorage.setItem(LS_SHOW, e.target.checked ? '1' : '0');
    paintChip(); injectToday(); if (!e.target.checked) closePop();
  };
  paintBadges();
}

function paintBadges() {
  const host = popEl && C.$('#px-badges', popEl);
  if (!host) return;
  if (!badgesAll) { host.innerHTML = '<span class="small muted">Loading…</span>'; return; }
  host.innerHTML = badgesAll.map(b => `<div class="px-badge ${b.earned ? 'on' : 'off'}" role="listitem" title="${C.esc(b.how)}">
      <span class="gl" aria-hidden="true">${C.esc(b.glyph)}</span><b>${C.esc(b.name)}</b>
      <span class="small">${b.earned ? `Earned${b.when ? ' ' + C.esc(b.when) : ''}` : C.esc(b.how)}${!b.earned && b.goal > 1 ? ` (${b.cur}/${b.goal})` : ''}</span></div>`).join('');
  host.setAttribute('role', 'list');
}

// ---- toasts: told once, never for what you had before this browser first looked ---------------------------------------
async function announce(d) {
  let seen = null;
  try { seen = JSON.parse(localStorage.getItem(seenKey()) || 'null'); } catch { /* ignore */ }
  const save = s => localStorage.setItem(seenKey(), JSON.stringify(s));
  if (!seen || !Array.isArray(seen.badges)) { save({ level: d.level.n, badges: d.badges_earned }); return; }   // first look: baseline, no toast
  const fresh = d.badges_earned.filter(b => !seen.badges.includes(b));
  const up = d.level.n > seen.level;
  if (!fresh.length && !up) return;
  save({ level: Math.max(seen.level, d.level.n), badges: [...new Set([...seen.badges, ...d.badges_earned])] });   // remember first: other windows skip it
  if (!shown()) return;
  if (up) C.toast(`Level up! You are now ${/^[AEIOU]/i.test(d.level.name) ? 'an' : 'a'} ${d.level.name} (level ${d.level.n}).`, 4200);
  if (fresh.length) {
    try { if (!badgesAll || fresh.some(id => !badgesAll.find(b => b.id === id))) badgesAll = (await C.api('/progress/badges')).items; } catch { /* names optional */ }
    fresh.slice(0, 3).forEach((id, i) => setTimeout(() => C.toast('Badge earned: ' + (badgesAll?.find(b => b.id === id)?.name || id), 4200), (up ? 1 : 0) * 900 + i * 900));
  }
}

function refresh() {
  inflight = inflight || (async () => {
    try { data = await C.api('/progress/summary'); badgesAll = null; paintChip(); paintPop(); if (popEl) loadBadges(); await announce(data); }
    catch { /* progress is a bonus: stay quiet */ }
    finally { inflight = null; }
  })();
  return inflight;
}
const later = (() => { let t; return ms => { clearTimeout(t); t = setTimeout(refresh, ms); }; })();

// ---- Home: "Today" card ------------------------------------------------------------------------------------------
async function injectToday() {
  const view = C.$('#view');
  C.$('#px-today')?.remove();
  if (!view || location.hash.replace(/^#\/?/, '') !== '') return;
  const wrap = view.querySelector('.fade-in');
  if (!wrap) return;
  const card = document.createElement('div');
  card.id = 'px-today'; card.className = 'card pad px-today';
  const hero = wrap.querySelector('.hero');
  hero ? hero.after(card) : wrap.prepend(card);
  try {
    const [con, sum] = await Promise.all([C.api('/progress/concepts?due_only=1&limit=40'), data ? Promise.resolve(data) : C.api('/progress/summary')]);
    data = data || sum;
    if (!card.isConnected) return;
    const due = con.due, n = con.counts;
    const gl = shown() ? `<span class="small muted">Goal: ${goalText(sum.goal)}${sum.goal.met ? ' · reached' : ''}</span>` : '<a href="#" class="small" data-show>Show XP and badges</a>';
    const wb = shown() && sum.streak.welcome_back ? `<p class="px-wb small">${C.esc(sum.streak.welcome_back.text)}</p>` : '';
    let main;
    if (!n.practised) main = '<p class="sub small">When you pass an exercise check or rate a quiz question, the concepts behind it come back here for a short refresh a day later, then after 3, 7, 14 and 30 days.</p>';
    else main = `<div class="px-warmrow"><button class="btn primary" data-warm>${due.length ? '10-minute warm-up' : 'Quick refresher'}</button>
      <span class="small muted">${due.length ? `${n.due} concept${n.due === 1 ? '' : 's'} due: about 5 short questions and exercises.` : 'Nothing is due right now. Revisit something you learnt recently, just for fun.'}</span></div>
      ${due.length ? `<div class="px-due">${due.slice(0, 6).map(c => `<a class="chip px-concept" href="#/day/${c.day_no}/learn" title="Day ${c.day_no}: ${C.esc(c.day_title)}">Day ${c.day_no} · ${C.esc(nm(c.name))}${c.overdue_days ? ` <span class="muted">${c.overdue_days}d late</span>` : ''}</a>`).join('')}${due.length > 6 ? `<span class="small muted">+${due.length - 6} more</span>` : ''}</div>` : ''}`;
    card.innerHTML = `<div class="row px-trow"><h3>Today</h3><span class="grow"></span>${gl}</div>${wb}${main}`;
    C.$('[data-warm]', card)?.addEventListener('click', openWarmup);
    C.$('[data-show]', card)?.addEventListener('click', e => { e.preventDefault(); localStorage.setItem(LS_SHOW, '1'); paintChip(); injectToday(); });
  } catch { card.remove(); }
}

// ---- warm-up modal -------------------------------------------------------------------------------------------------
async function openWarmup() {
  let w;
  try { w = await C.api('/progress/warmup?size=5'); } catch { C.toast('Could not build the warm-up. Try again in a moment.'); return; }
  if (!w.items.length) { C.toast('Nothing to warm up with yet. Finish an exercise or a quiz question first.'); return; }
  const before = data?.xp.total ?? 0, results = [];
  let i = 0, closeFn = null;
  const sid = C.store.sid;
  C.modal('<div id="px-w"></div>', { onMount: (m, close) => { closeFn = close; step(m); } });

  function step(m) {
    const host = C.$('#px-w', m);
    if (i >= w.items.length) return done(host);
    const it = w.items[i], quiz = it.kind === 'quiz';
    const dots = w.items.map((_, k) => `<i class="${k < i ? 'd' : k === i ? 'c' : ''}"></i>`).join('');
    host.innerHTML = `<div class="row"><h3>${w.light ? 'Quick refresher' : '10-minute warm-up'}</h3><span class="grow"></span><span class="small muted">${i + 1} of ${w.items.length}</span></div>
      <div class="px-dots" aria-hidden="true">${dots}</div>
      <div class="small muted px-ctx">Day ${it.day_no} · ${C.esc(nm(it.concept))}</div>
      ${quiz ? `<div class="px-q md">${C.md(it.text)}</div><div id="px-ans" class="px-ans md" hidden></div>
          <div class="row px-acts"><button class="btn primary" data-show>Show answer</button><span class="grow"></span><a class="small" href="${it.href}" data-link>See the lesson</a></div>`
        : `<p><b>${C.esc(it.title)}</b> <span class="chip">Level ${it.level}</span></p><pre class="px-desc">${C.esc(it.desc || 'Re-run this exercise from scratch and see if all checks pass.')}</pre>
          <p class="small muted">Open it in the Practice tab, run it again, then tell us how it went.</p>
          <div class="row px-acts"><a class="btn" href="${it.href}" data-link>Open the exercise</a><span class="grow"></span></div>`}
      <div class="row px-rate" ${quiz ? 'hidden' : ''}><span class="small muted">How did it go?</span><span class="grow"></span>
        ${quiz ? '<button class="btn sm" data-r="ok">Got it</button><button class="btn sm" data-r="partial">Partly</button><button class="btn sm" data-r="miss">Missed it</button>'
          : '<button class="btn sm" data-r="ok">Solved it</button><button class="btn sm" data-r="partial">With hints</button><button class="btn sm" data-r="miss">Not yet</button>'}</div>
      <div class="row px-foot"><button class="btn ghost sm" data-skip>Skip</button><span class="grow"></span><button class="btn ghost sm" data-close>Stop here</button></div>`;
    C.$('[data-show]', host)?.addEventListener('click', async e => {
      e.target.disabled = true;
      try {
        const a = await C.api(`/progress/warmup/answer?day_no=${it.day_no}&q_no=${it.q_no}`);
        const box = C.$('#px-ans', host); box.innerHTML = C.md(a.answer || '(no answer text)'); box.hidden = false;
        C.$('.px-rate', host).hidden = false; e.target.hidden = true; C.$('[data-r="ok"]', host).focus();
      } catch { e.target.disabled = false; C.toast('Could not load the answer.'); }
    });
    C.$$('[data-link]', host).forEach(a => a.addEventListener('click', () => closeFn()));
    C.$$('[data-r]', host).forEach(b => b.addEventListener('click', async () => {
      C.$$('[data-r]', host).forEach(x => (x.disabled = true));
      try {
        await C.api('/progress/warmup', { method: 'POST', body: { action: 'item', day_no: it.day_no, concept_idx: it.concept_idx, kind: it.kind, ref: quiz ? String(it.q_no) : it.check_id, result: b.dataset.r, session_id: sid } });
        results.push(b.dataset.r); i++; step(m);
      } catch { C.$$('[data-r]', host).forEach(x => (x.disabled = false)); C.toast('Could not save that answer. Try again.'); }
    }));
    C.$('[data-skip]', host).onclick = () => { i++; step(m); };
    C.$('[data-close]', host).onclick = () => finish(m, false);
    (C.$('[data-show]', host) || C.$('[data-link]', host))?.focus();
  }
  async function finish(m, last) {
    if (results.length) {
      try { await C.api('/progress/warmup', { method: 'POST', body: { action: 'finish', items: results.length, ok_count: results.filter(r => r === 'ok').length, session_id: sid } }); } catch { /* ignore */ }
    }
    await refresh(); injectToday();
    if (last) return;
    closeFn();
    if (results.length) C.toast('Nice work. Warm-up saved.');
  }
  async function done(host) {
    await finish(null, true);
    const ok = results.filter(r => r === 'ok').length, gain = (data?.xp.total ?? before) - before;
    host.innerHTML = `<h3>Warm-up done</h3><p>${results.length ? `${ok} of ${results.length} felt solid.` : 'Nothing answered this time, and that is fine.'} ${gain > 0 ? `You earned ${gain} XP.` : ''}</p>
      <p class="sub small">Concepts you got right come back later; ones you missed come back tomorrow. No pressure.</p>
      <div class="row"><span class="grow"></span><button class="btn primary" data-close>Close</button></div>`;
    const b = C.$('[data-close]', host); b.onclick = () => closeFn(); b.focus();
  }
}

// ---- init --------------------------------------------------------------------------------------------------------
export async function init(ctx) {
  C = ctx;
  buildChip();
  document.addEventListener('pm:route', e => { later(350); if (e.detail?.area === 'home') injectToday(); });
  document.addEventListener('pm:runresult', () => later(1500));
  window.addEventListener('storage', e => { if (e.key === LS_SHOW) { paintChip(); injectToday(); } });
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') later(300); });
  timer = setInterval(() => { if (document.visibilityState === 'visible') refresh(); }, 60000);
  await refresh();
  if (location.hash.replace(/^#\/?/, '') === '') injectToday();
}
