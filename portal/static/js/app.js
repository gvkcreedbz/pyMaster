import { $, $$, api, esc, md, enhance, modal, store, toast, fmtMin, TRK } from './util.js';
import { S, hooks } from './state.js';
import * as layout from './layout.js';
import * as sync from './sync.js';
import * as tutor from './tutor.js';
import * as playground from './playground.js';
import { openVisualizer } from './visualizer.js';
import { redrawAll } from './diagram.js';
import { renderHome } from './home.js';
import { renderDay, resetDay, registerDayTab } from './day.js';
import { renderLibrary } from './misc.js';
import { renderInsights } from './insights.js';
import { renderBlueprints } from './blueprints.js';
import { initPalette, open as openPalette } from './palette.js';

const PANE = layout.PANE;
/** Pages added by extensions: { id, title, icon, label, render(view, part2, part3), action: {title, sub, keys} }. Route is #/<id>. */
const extraPages = [];
let extrasReady = false;               // false until the extension modules have been loaded once (they may add routes)
function registerPage(p) { extraPages.push(p); }
const view = () => $('#view');
const LOGO = '<img class="logo" src="/static/logo.svg" alt="" width="26" height="26">';

// ---- top bar ------------------------------------------------------------------------------------
function buildTopbar() {
  $('#topbar').innerHTML = `
    <button class="iconbtn menu" id="btn-menu" title="Menu: days, insights, library">&#9776;</button>
    <a class="brand" href="#/" title="Home">${LOGO}<span>${TRK.name}</span></a>
    <div class="ptoggles" id="ptoggles"></div>
    <span class="grow"></span>
    <span id="topbar-extras" class="topx"></span>
    <button class="searchbtn" id="btn-search" title="Search everything (Ctrl+P, or press /)"><span>&#128269;</span><span class="lbl">Search</span><kbd>Ctrl P</kbd></button>
    <span class="timechip" title="Active time today (tracked while you're working)"><i></i><b id="todaytime">0m</b><span>today</span></span>
    <button class="iconbtn" id="btn-settings" title="Assistant &amp; settings">&#9881;</button>
    <button class="iconbtn" id="btn-theme" title="Light / dark">&#9680;</button>`;
  $('#btn-menu').onclick = () => (drawerOpen() ? closeDrawer() : openDrawer());
  $('#btn-settings').onclick = openSettings;
  $('#btn-search').onclick = openPalette;
  $('#btn-theme').onclick = () => {
    const t = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = t; localStorage.setItem('pj-theme', t); redrawAll();
  };
}

// ---- navigation drawer (closes itself whenever you pick something) -----------------------------------------------
const drawerOpen = () => $('#side').classList.contains('open');
function openDrawer() { paintSide(); $('#side').classList.add('open'); $('#scrim').classList.add('open'); }
function closeDrawer() { $('#side').classList.remove('open'); $('#scrim').classList.remove('open'); }
$('#scrim').addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => { if (e.key === 'Escape' && drawerOpen() && !$('#modal-root').firstChild) closeDrawer(); });

function viewingDay() { return S.area === 'day' ? S.dayNo : 0; }

function paintSide() {
  const o = S.overview; if (!o) return;
  const cur = o.welcome.current_day, viewing = viewingDay();
  const hash = location.hash || '#/';
  const nav = [['#/', '&#8962;', 'Home'], ['#/insights', '&#9684;', 'Insights'], ['#/library', '&#10081;', 'Library'], ['#/blueprints', '&#129513;', 'Blueprints'], ...extraPages.map(p => ['#/' + p.id, p.icon || '&#9679;', p.label])];
  const on = h => (h === '#/' ? hash === '#/' || hash === '' || hash.startsWith('#/day') : hash.startsWith(h));
  $('#side').innerHTML = `
    <div class="row"><div class="brand">${LOGO}<span>${TRK.name}</span></div><span class="grow"></span><button class="iconbtn" id="side-x" title="Close (Esc)">&#10005;</button></div>
    <nav class="nav">${nav.map(([h, i, l]) => `<a href="${h}" class="${on(h) ? 'on' : ''}"><span class="ico">${i}</span>${l}</a>`).join('')}
      <button class="navbtn" id="nav-play"><span class="ico">&#9654;</span>Playground<span class="small muted" style="margin-left:auto">beside the lesson</span></button></nav>
    <div class="pathmap"><h6>Your path</h6>${o.weeks.map(w => `<div class="wk"><span class="l">W${w.n}</span>${o.days.filter(d => d.n >= w.from && d.n <= w.to).map(d =>
      `<button class="dot ${d.status === 'done' ? 'd' : d.pct > 0 ? 'p' : ''} ${d.n === viewing ? 'view' : ''} ${d.n === cur && d.n !== viewing ? 'cur' : ''}" data-day="${d.n}" title="Day ${d.n}: ${esc(d.title)}${d.pct ? ' · ' + d.pct + '%' : ''}${d.n === cur && d.n !== viewing ? ' · where you left off' : ''}">${d.n}</button>`).join('')}</div>`).join('')}
      <div class="legend small muted"><i class="dot view"></i> open now &nbsp; <i class="dot cur"></i> where you left off</div></div>
    <div class="foot"><button class="btn sm" id="side-resume">Resume Day ${cur} &rarr;</button></div>`;
  $$('.dot[data-day]', $('#side')).forEach(b => b.onclick = () => { closeDrawer(); location.hash = '#/day/' + b.dataset.day; });
  $$('.nav a', $('#side')).forEach(a => a.addEventListener('click', () => closeDrawer()));
  $('#side-x').onclick = closeDrawer;
  $('#side-resume').onclick = () => { closeDrawer(); location.hash = '#/day/' + cur; };
  $('#nav-play').onclick = () => { closeDrawer(); layout.showPane('play'); setTimeout(() => $('#pg .CodeMirror')?.CodeMirror?.focus(), 80); };
}

hooks.refreshOverview = async () => {
  S.overview = await api('/overview?sid=' + store.sid);
  S.ovAt = Date.now();
  S.todaySec = Math.max(S.todaySec, Math.round(S.overview.today.minutes * 60));
  const el = $('#todaytime'); if (el) el.textContent = fmtMin(S.todaySec / 60);
  tutor.setAssistant(S.overview.assistant);
  paintSide();
};

// ---- settings -----------------------------------------------------------------------------------
async function openSettings() {
  const st = await api('/settings');
  const P = st.providers;
  const row = (id, label, hint) => `
    <label class="lab">${label} ${P[id].configured ? `<span class="chip good" style="margin-left:6px">connected${P[id].source === 'env' ? ' (env var)' : ''}</span>` : ''}</label>
    <div class="row"><input type="password" data-key="${id}" placeholder="${P[id].configured ? 'saved, type to replace' : hint}" autocomplete="off">
      <input type="text" data-model="${id}" value="${esc(P[id].model)}" style="max-width:190px" title="model"></div>`;
  modal(`<h3>Assistant &amp; settings</h3>
    <p class="sub small">The assistant works out of the box with the built-in knowledge base. Connect an AI for open-ended, deeper answers. Keys stay on this computer (<span class="mono">portal/data</span>) and are only sent to that provider.</p>
    <label class="lab">Which assistant should answer?</label>
    <select id="pref"><option value="auto">Auto: best connected, else built-in</option><option value="cursor">Cursor agent</option><option value="anthropic">Claude</option><option value="openai">GPT</option><option value="offline">Built-in tutor only</option></select>
    ${row('cursor', 'Cursor API key', 'paste CURSOR_API_KEY (cursor.com/dashboard → Integrations)')}
    ${row('anthropic', 'Anthropic API key', 'paste ANTHROPIC_API_KEY')}
    ${row('openai', 'OpenAI API key', 'paste OPENAI_API_KEY')}
    <label class="lab">Day 1 start date (for the suggested plan only)</label><input type="date" id="start" value="${st.start_date}" style="max-width:200px">
    <div class="row" style="margin-top:20px"><a class="btn sm" href="/api/export" download>&#11015; Export my data</a><span class="grow"></span><button class="btn" data-x>Cancel</button><button class="btn primary" data-save>Save</button></div>`, {
    onMount: (m, close) => {
      $('#pref', m).value = st.pref;
      $('[data-x]', m).onclick = close;
      $('[data-save]', m).onclick = async () => {
        const values = { provider_pref: $('#pref', m).value, start_date: $('#start', m).value };
        for (const id of ['cursor', 'anthropic', 'openai']) {
          const k = $(`[data-key=${id}]`, m).value.trim(); if (k) values['key_' + id] = k;
          const mo = $(`[data-model=${id}]`, m).value.trim(); if (mo) values['model_' + id] = mo;
        }
        try {
          const r = await api('/settings', { method: 'POST', body: { values } });
          close(); await hooks.refreshOverview(); tutor.setAssistant(r); toast('Saved. Assistant is using: ' + ({ cursor: 'Cursor', anthropic: 'Claude', openai: 'GPT', offline: 'the built-in tutor' }[r.active]));
        } catch (e) { toast('Could not save: ' + e.message); }
      };
    },
  });
}
hooks.openSettings = openSettings;

// ---- router -------------------------------------------------------------------------------------
let lastHash = '#/';
function lessonTitle(a, b) {
  if (!a) return 'Home';
  if (a === 'day') return `Day ${b} · ${S.overview?.days[+b - 1]?.title || ''}`;
  return { insights: 'Insights', library: 'Library', blueprints: 'Blueprints' }[a] || extraPages.find(p => p.id === a)?.title || 'Lesson';
}
async function route() {
  const hash = location.hash || '#/';
  if (!S.overview) return;                      // a hash change during start-up: boot() calls route() once the data is in
  closeDrawer();
  if (hash === '#/playground') {                       // old link: the playground is a pane now
    layout.showPane('play'); location.replace(lastHash === '#/playground' ? '#/' : lastHash); return;
  }
  lastHash = hash;
  const parts = (location.hash.slice(2) || '').split('/');
  const [a, b, c] = parts;
  if (!PANE && layout.isPopped('lesson')) { sync.send('nav', { hash }); S.dayNo = a === 'day' ? +b : 0; S.area = a === 'day' ? 'day' : (a || 'home'); paintSide(); return; }
  const my = ++S.seq;
  layout.setTitle('lesson', lessonTitle(a, b));
  $('#main').scrollTop = 0;
  try {
    if (!a) { S.area = 'home'; S.dayNo = 0; if (Date.now() - (S.ovAt || 0) > 2000) await hooks.refreshOverview(); if (my !== S.seq) return; renderHome(view()); }
    else if (a === 'day') {
      const n = Number(b), last = S.overview?.days.length || 30;
      if (!Number.isInteger(n) || n < 1 || n > last) { toast(`There is no Day ${(b || '?').slice(0, 12)}. Taking you home.`); location.replace('#/'); return; }
      await renderDay(view(), n, c || 'learn');
    }
    else if (a === 'insights') await renderInsights(view());
    else if (a === 'library') await renderLibrary(view(), b ? decodeURIComponent(b) : null);
    else if (a === 'blueprints') await renderBlueprints(view(), b ? decodeURIComponent(b) : null, c);
    else if (extraPages.some(p => p.id === a)) { S.area = a; S.dayNo = 0; await extraPages.find(p => p.id === a).render(view(), b ? decodeURIComponent(b) : null, c); }
    else if (!extrasReady) { view().innerHTML = '<div class="muted">Loading…</div>'; return; }      // maybe an extension page: loadExtras() routes again
    else { location.hash = '#/'; return; }
  } catch (e) {
    view().innerHTML = `<div class="card pad"><b>Something went wrong.</b><pre class="out err">${esc(e.stack || e.message)}</pre></div>`;
  }
  if (my !== S.seq) return;
  S.baseArea = S.area;
  if (PANE === 'lesson') sync.send('nav', { hash });
  paintSide();
  document.dispatchEvent(new CustomEvent('pm:route', { detail: { hash, area: S.area, dayNo: S.dayNo } }));
}
window.addEventListener('hashchange', route);
sync.on('nav', m => {
  const owner = PANE === 'lesson' || (!PANE && layout.isPopped('lesson'));
  if (owner && m.hash && (location.hash || '#/') !== m.hash) location.hash = m.hash;
});
sync.on('lessonctx', m => {                            // the lesson lives in another window: follow it for time tracking
  if (PANE ? PANE !== 'lesson' : layout.isPopped('lesson')) { S.dayNo = m.dayNo || 0; S.area = m.dayNo ? 'day' : S.area; S.baseArea = S.area; paintSide(); }
});
layout.onEvent('popped', id => { if (id === 'play') localStorage.setItem('pm-play-code', playground.getCode()); });
layout.onEvent('docked', id => {
  if (id === 'lesson') { resetDay(); route(); }
  if (id === 'play') playground.reload();
  layout.refreshEditors();
});
document.addEventListener('pm:visualize', e => openVisualizer({ ...e.detail, dayNo: S.dayNo }));
document.addEventListener('pm:editorfocus', e => { S.area = e.detail.pane === 'play' ? 'playground' : (S.baseArea || S.area); });

// ---- time tracking: heartbeat (server credits time on its own clock) ---------------------------------
let lastAct = Date.now();
['mousemove', 'keydown', 'scroll', 'click', 'touchstart', 'wheel'].forEach(ev => addEventListener(ev, () => { lastAct = Date.now(); }, { passive: true, capture: true }));
async function beat() {
  if (!store.sid || document.visibilityState !== 'visible') return;
  if (Date.now() - lastAct >= 120000) return;           // idle: say nothing, so another window can carry the clock
  try {
    const r = await api('/session/heartbeat', { method: 'POST', body: { session_id: store.sid, day_no: S.dayNo || 0, area: S.area, active: true } });
    if (r.today_seconds != null) {
      S.todaySec = r.today_seconds;
      const el = $('#todaytime'); if (el) el.textContent = fmtMin(S.todaySec / 60);
    }
  } catch { /* offline: ignore */ }
}
setInterval(beat, 15000);
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') lastAct = Date.now(); });
if (!PANE) addEventListener('pagehide', () => {
  if (store.sid) navigator.sendBeacon('/api/session/end', new Blob([JSON.stringify({ session_id: store.sid })], { type: 'application/json' }));
});

// ---- selection popover: highlight text in a lesson → ask the assistant ----------------------------------------
const pop = $('#selpop');
function hidePop() { pop.style.display = 'none'; }
document.addEventListener('mousedown', e => { if (!pop.contains(e.target)) hidePop(); });
$('#main').addEventListener('scroll', hidePop, { passive: true });
$('#view').addEventListener('mouseup', e => {
  if (e.target.closest('textarea, input, .CodeMirror, button, .codebar, .mmd')) return;
  setTimeout(() => {
    const sel = getSelection(); const text = sel.toString().trim();
    if (text.length < 3 || text.length > 700 || !sel.rangeCount) return hidePop();
    const r = sel.getRangeAt(0).getBoundingClientRect();
    pop.innerHTML = `<button data-q="where_used">&#10022; Where is this used?</button><button data-q="visual">&#128065; Visual</button><button data-q="explain_simple">Explain</button><button data-q="why">Why?</button>`;
    pop.style.display = 'flex';
    pop.style.left = Math.max(8, Math.min(innerWidth - 400, r.left + r.width / 2 - 170)) + 'px';
    pop.style.top = Math.max(52, r.top - 46) + 'px';
    pop.onclick = ev => {
      const q = ev.target.dataset.q; if (!q) return;
      tutor.ask(q, '', text); hidePop(); sel.removeAllRanges();
    };
  }, 10);
});

// ---- command palette ------------------------------------------------------------------------------------------
initPalette({
  navigate: h => { if (PANE && PANE !== 'lesson') sync.send('nav', { hash: h }); else location.hash = h; },
  actions: () => {
    const cur = S.overview?.welcome.current_day || 1;
    const go = h => () => (PANE && PANE !== 'lesson' ? sync.send('nav', { hash: h }) : (location.hash = h));
    return [
      { title: `Resume Day ${cur}`, sub: S.overview?.days[cur - 1]?.title, keys: 'continue resume current', run: go('#/day/' + cur + '/learn') },
      { title: 'Go to Home', keys: 'dashboard roadmap days', run: go('#/') },
      { title: 'Open Insights', sub: 'how you are learning', keys: 'analytics progress stats', run: go('#/insights') },
      { title: 'Open Library', sub: 'guides and cheatsheets', keys: 'cheatsheet docs', run: go('#/library') },
      { title: 'Open Blueprints', sub: 'real full-stack projects', keys: 'projects architecture full stack', run: go('#/blueprints') },
      { title: 'Open Pattern catalog', sub: '16 reusable patterns', keys: 'design patterns', run: go('#/blueprints/patterns') },
      { title: 'Focus the playground', keys: 'code editor scratch', run: () => { layout.showPane('play'); setTimeout(() => $('#pg .CodeMirror')?.CodeMirror?.focus(), 80); } },
      { title: 'Ask the assistant', sub: 'Ctrl+K', keys: 'ai tutor help', run: () => tutor.toggle(true) },
      { title: 'Switch light / dark theme', keys: 'theme dark light mode', run: () => $('#btn-theme').click() },
      { title: 'Assistant & settings', keys: 'api key provider start date export', run: openSettings },
      ...extraPages.filter(p => p.action).map(p => ({ title: p.action.title, sub: p.action.sub, keys: p.action.keys, run: go('#/' + p.id) })),
    ];
  },
});

// ---- extensions (portal/static/js/extras/*.js, listed by /api/extras; contract in portal/ext.py) -------------------
async function loadExtras() {
  let list = [];
  try {
    const r = await api('/extras'); list = r.js || [];
    for (const href of r.css || []) { const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '/static/css/extras/' + href; document.head.appendChild(l); }
  } catch { extrasReady = true; return; }                       // no extensions available: carry on without them
  const ctx = { api, $, $$, esc, md, enhance, toast, modal, store, TRK, S, hooks, layout, tutor, openVisualizer, openSettings, openPalette, registerDayTab, registerPage, PANE };
  for (const name of list) {
    try { const m = await import('/static/js/extras/' + name); await Promise.race([m.init?.(ctx), new Promise(r => setTimeout(r, 4000))]); }
    catch (e) { console.warn('extension ' + name + ' failed', e); }       // a broken extension never stops the app
  }
  extrasReady = true;
}
// ---- boot -----------------------------------------------------------------------------------------------
(async function boot() {
  buildTopbar();
  layout.init();
  tutor.init({ openSettings });
  if (!PANE || PANE === 'play') playground.mount();
  const urlSid = new URLSearchParams(location.search).get('sid');
  if (PANE && urlSid) store.sid = urlSid;
  else { const s = await api('/session/start', { method: 'POST' }); store.sid = s.session_id; }
  await hooks.refreshOverview();
  await loadExtras();                     // before the first render, so extension pages and day tabs exist from the start
  if (!PANE || PANE === 'lesson') await route();
  layout.apply();
  beat();
})();
