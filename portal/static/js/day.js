import { $, $$, api, esc, md, enhance, toast, modal, editor, debounce, fmtDate, fmtMin, store, TRK } from './util.js';
import { S, hooks } from './state.js';
import { mountRunner } from './runpanel.js';
import * as tutor from './tutor.js';
import { openVisualizer } from './visualizer.js';

let cur = { n: 0, d: null };
export function resetDay() { cur = { n: 0, d: null }; }

/** Visualize + "send to playground" buttons for an editor, placed in its runner toolbar. */
function codeTools(runner, cm, dayNo) {
  const add = (html, title, fn) => { const b = document.createElement('button'); b.className = 'btn ghost sm'; b.innerHTML = html; b.title = title; b.onclick = fn; runner.slot.appendChild(b); };
  add('&#128065; Visualize', 'Step through this code and see it as a diagram (selects only the highlighted part if you highlighted something)',
    () => openVisualizer({ code: cm.somethingSelected() ? cm.getSelection() : cm.getValue(), lang: TRK.fence, dayNo }));
  add('&#8674; Playground', 'Copy this code into the playground pane',
    () => document.dispatchEvent(new CustomEvent('pm:try', { detail: { code: cm.getValue() } })));
}
const celebrated = new Set();
const LEVEL = { 1: 'Beginner', 2: 'Intermediate', 3: 'Challenge' };
const TABS = [['learn', 'Learn'], ['along', 'Code along'], ['practice', 'Practice'], ['quiz', 'Quiz'], ['notes', 'Notes']];
/** Extensions add day tabs here: { id, label, show(day) -> bool, count(day) -> string, render(body, day, label) }. */
const extraTabs = [];
export function registerDayTab(t) { extraTabs.push(t); }

export async function renderDay(root, n, tab = 'learn') {
  if (cur.n !== n) {
    root.innerHTML = '<div class="muted">Loading…</div>';
    const my = S.seq, d = await api('/day/' + n);
    if (my !== S.seq) return;                     // you navigated away while this was loading
    cur = { n, d };
  }
  S.dayNo = n; S.area = 'day';
  shell(root, cur.d, tab);
  document.dispatchEvent(new CustomEvent('pm:dayrendered', { detail: { dayNo: n, tab, root } }));
}

function shell(root, d, tab) {
  const addon = extraTabs.filter(t => { try { return t.show(d); } catch { return false; } });
  const tabs = [...TABS, ...addon.map(t => [t.id, t.label]), ...(d.extras.length ? [['extras', d.extras[0].replace(/\.md$/, '').replace(/_/g, ' ').toLowerCase().replace(/^./, c => c.toUpperCase())]] : [])];
  const p = d.progress;
  const count = { practice: `${p.ex_passed}/${p.ex_total}`, quiz: `${p.quiz_rated}/${p.quiz_total}` };
  for (const t of addon) { try { count[t.id] = t.count?.(d) || ''; } catch { /* a broken extension never breaks the page */ } }
  const wk = S.overview.weeks.find(w => w.n === d.week);
  root.innerHTML = `<div class="fade-in">
    <div class="dayhead">
      <div style="min-width:0;flex:1">
        <div class="eyebrow">Day ${String(d.n).padStart(2, '0')} · Week ${d.week} · ${esc(wk?.title || '')}</div>
        <h1 class="page-title">${esc(d.title)}</h1>
        <div class="sub">${esc(d.goal)}</div>
        <div class="metarow">
          <span class="chip">⏱ ${esc(d.minutes)}</span><span class="chip">🏁 ${esc(d.level)}</span>
          <span class="chip">📅 suggested ${fmtDate(d.planned)}</span>
          <span class="chip accent" title="Active time you've spent on this day">⏳ ${fmtMin(p.minutes)} here</span>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px;align-items:flex-end">
        <div class="seg" id="stseg"><button data-s="open" class="${p.status !== 'done' ? 'on' : ''}">In progress</button><button data-s="done" class="${p.status === 'done' ? 'on' : ''}">Done ✓</button></div>
        <div class="small muted row">How well do I get it? <span class="stars" id="stars">${[1, 2, 3, 4, 5].map(i => `<button data-c="${i}" class="${p.confidence >= i ? 'on' : ''}">★</button>`).join('')}</span></div>
      </div>
    </div>
    <div class="tabs">${tabs.map(([id, label]) => `<button class="tab ${id === tab ? 'on' : ''}" data-t="${id}">${label}${count[id] ? `<span class="n">${count[id]}</span>` : ''}</button>`).join('')}</div>
    <div id="tabbody"></div>
  </div>`;
  $$('.tab', root).forEach(b => b.onclick = () => { location.hash = `#/day/${d.n}/${b.dataset.t}`; });
  $('#stseg', root).onclick = async e => {
    const s = e.target.dataset.s; if (!s) return;
    const r = await api(`/day/${d.n}/state`, { method: 'POST', body: { status: s } });
    d.progress = r.progress; await hooks.refreshOverview(); shell(root, d, tab);
    toast(s === 'done' ? `Day ${d.n} complete. Nice work!` : 'Reopened. Take your time.');
  };
  $('#stars', root).onclick = async e => {
    const c = +e.target.dataset.c; if (!c) return;
    const r = await api(`/day/${d.n}/state`, { method: 'POST', body: { confidence: c } });
    d.progress = r.progress; $$('#stars button', root).forEach(b => b.classList.toggle('on', +b.dataset.c <= c));
  };
  const body = $('#tabbody', root);
  const label = `Day ${d.n} · ${d.title}`;
  const ext = extraTabs.find(t => t.id === tab);
  if (ext && addon.includes(ext)) ext.render(body, d, label);
  else (({ learn, along, practice, quiz, notes, extras })[tab] || learn)(body, d, label);
}

// ---- Learn --------------------------------------------------------------------------------------
function learn(body, d, label) {
  tutor.setContext({ dayNo: d.n, tab: 'learn', label: label + ' · Learn' });
  body.innerHTML = `<div class="md">${md(d.lesson, true)}</div>
    <div class="card pad" style="margin-top:34px;display:flex;gap:14px;align-items:center;flex-wrap:wrap">
      <div class="grow"><b>Ready to code?</b><div class="sub small">Type the examples yourself, then take on today's exercises.</div></div>
      <button class="btn" data-go="along">Code along</button><button class="btn primary" data-go="practice">Start practice →</button></div>`;
  const mdEl = $('.md', body);
  mdEl.querySelector('table')?.remove();           // the time/goal/level table is shown as chips above
  enhance(mdEl);
  $$('[data-go]', body).forEach(b => b.onclick = () => { location.hash = `#/day/${d.n}/${b.dataset.go}`; });
}

// ---- Code along ---------------------------------------------------------------------------------
function along(body, d, label) {
  body.innerHTML = `<p class="sub" style="margin-top:0">Type this yourself rather than pasting. Then change values and break things on purpose; that's how it sticks.</p>
    <div class="editor-wrap" id="ed"></div><div id="rp"></div>`;
  let runner;
  const save = debounce(code => api(`/day/${d.n}/draft`, { method: 'POST', body: { kind: 'examples', code } }), 1200);
  const cm = editor($('#ed', body), {
    value: d.drafts.examples ?? d.examples, onChange: v => { d.drafts.examples = v; save(v); },
    onRun: () => runner.run(), onSelection: t => tutor.setSelection(t),
  });
  runner = mountRunner($('#rp', body), { kind: 'examples', dayNo: d.n, getCode: () => cm.getValue(), label: 'Run' });
  const reset = document.createElement('button');
  reset.className = 'btn ghost sm'; reset.textContent = '↺ Reset'; reset.onclick = async () => {
    await api(`/day/${d.n}/draft/examples`, { method: 'DELETE' }); delete d.drafts.examples; cm.setValue(d.examples); toast('Reset to the original example');
  };
  runner.slot.appendChild(reset);
  codeTools(runner, cm, d.n);
  tutor.setContext({ dayNo: d.n, tab: 'code-along', label: label + ' · Code along', getCode: () => cm.getValue(), getOutput: runner.getOutput });
  cm.refresh();
}

// ---- Practice -----------------------------------------------------------------------------------
function practice(body, d, label) {
  body.innerHTML = `
    <div class="exstrip" id="exstrip"></div>
    <div class="card exdesc" id="exdesc"></div>
    <div class="editor-wrap" id="ed"></div>
    <div id="rp"></div>
    <div id="hintbox"></div>`;
  let runner, selected = null;
  const save = debounce(code => api(`/day/${d.n}/draft`, { method: 'POST', body: { kind: 'practice', code } }), 1200);
  const cm = editor($('#ed', body), {
    value: d.drafts.practice ?? d.practice_starter, onChange: v => { d.drafts.practice = v; save(v); },
    onRun: () => runner.run(), onSelection: t => tutor.setSelection(t),
  });

  function strip() {
    $('#exstrip', body).innerHTML = d.exercises.map(e => {
      const s = e.status; const all = s && s.checks > 0 && s.passed >= s.checks;
      const st = all ? '✓' : s?.runs ? `${s.passed}/${s.checks}` : '○';
      return `<button class="ex ${selected === e.id ? 'on' : ''} ${all ? 'ok' : ''}" data-id="${e.id}"><i class="lv lv${e.level}"></i>${e.id}<span class="st">${st}</span></button>`;
    }).join('');
    $$('.ex', body).forEach(b => b.onclick = () => select(b.dataset.id, true));
  }
  function select(id, jump = true) {
    selected = id; const e = d.exercises.find(x => x.id === id);
    $('#exdesc', body).innerHTML = `<h4>${e.id} · ${esc(e.title)} <span class="chip ${['', 'good', 'warn', 'bad'][e.level]}" style="margin-left:6px">${LEVEL[e.level]}</span></h4>${esc(e.desc)}`;
    tutor.setExercise(id, `${id} ${e.title}`);
    if (jump) {
      const line = Math.min(e.line + 3, cm.lastLine());
      cm.scrollIntoView({ line, ch: 0 }, 120); cm.setCursor({ line, ch: 0 });
    }
    strip();
  }
  strip();
  if (d.exercises.length) select(d.exercises[0].id, false);
  else $('#exdesc', body).textContent = 'This day is a guided project. Build it in the editor and ask the tutor for review.';

  runner = mountRunner($('#rp', body), {
    kind: 'practice', dayNo: d.n, getCode: () => cm.getValue(), label: 'Run & check',
    onResult: async r => {
      if (r.progress) d.progress = r.progress;
      const fresh = await api('/day/' + d.n); d.exercises = fresh.exercises; d.progress = fresh.progress; strip();
      if (r.total && r.passed === r.total && !celebrated.has(d.n)) {
        celebrated.add(d.n); toast('🎉 All checks pass! Finish the quiz, then mark the day complete.', 4200);
      }
      hooks.refreshOverview();
    },
  });
  const add = (txt, fn, cls = 'btn ghost sm') => { const b = document.createElement('button'); b.className = cls; b.textContent = txt; b.onclick = fn; runner.slot.appendChild(b); };
  codeTools(runner, cm, d.n);
  [1, 2, 3].forEach(i => add(i === 3 ? 'Hint 3 · peek' : `Hint ${i}`, async () => {
    const r = await api(`/day/${d.n}/hint/${i}?session_id=${store.sid}`);
    $('#hintbox', body).innerHTML = `<div class="hintbox md"><b>Hint ${i}</b>${md(r.hint, true)}</div>`; enhance($('#hintbox', body), { tryIt: false });
  }));
  add('Solution', () => modal(`<h3>Peek at the solution?</h3>
    <p class="sub">Struggling for ten minutes is where the learning happens. Opening this is logged so your insights stay honest, and it's perfectly fine to look when you're truly stuck.</p>
    <div class="row" style="justify-content:flex-end;margin-top:16px"><button class="btn" data-x>Keep trying</button><button class="btn primary" data-ok>Show solution</button></div>`, {
    onMount: (m, close) => {
      $('[data-x]', m).onclick = close;
      $('[data-ok]', m).onclick = async () => {
        const r = await api(`/day/${d.n}/solution?session_id=${store.sid}`);
        m.innerHTML = `<h3>Reference solution · Day ${d.n}</h3><p class="sub small">Compare with yours: what did it do differently? Ask the tutor “why did they do it this way?”</p><div class="md">${md('```' + TRK.fence + '\n' + r.solution + '\n```', true)}</div><div class="row" style="justify-content:flex-end"><button class="btn" data-x>Close</button></div>`;
        enhance(m, { tryIt: false }); $('[data-x]', m).onclick = close;
      };
    }, wide: true,
  }), 'btn ghost sm');
  add('↺ Reset', () => modal(`<h3>Reset to the starter code?</h3><p class="sub">Your current code for Day ${d.n} will be replaced.</p>
    <div class="row" style="justify-content:flex-end;margin-top:14px"><button class="btn" data-x>Cancel</button><button class="btn primary" data-ok>Reset</button></div>`, {
    onMount: (m, close) => {
      $('[data-x]', m).onclick = close;
      $('[data-ok]', m).onclick = async () => { await api(`/day/${d.n}/draft/practice`, { method: 'DELETE' }); delete d.drafts.practice; cm.setValue(d.practice_starter); close(); toast('Reset'); };
    },
  }), 'btn ghost sm');
  tutor.setContext({ dayNo: d.n, tab: 'practice', label: label + ' · Practice', getCode: () => cm.getValue(), getOutput: runner.getOutput });
  if (selected) tutor.setExercise(selected, `${selected}`);
  cm.refresh();
}

// ---- Quiz ---------------------------------------------------------------------------------------
function quiz(body, d, label) {
  tutor.setContext({ dayNo: d.n, tab: 'quiz', label: label + ' · Quiz' });
  body.innerHTML = `<p class="sub" style="margin-top:0">Answer in your head (or on paper) first, <b>then</b> reveal. Rate yourself honestly. It's data for you, not a grade.</p>` +
    d.quiz.map(q => `<div class="card qcard" data-q="${q.n}">
      <div class="q"><span class="no">${q.n}</span>${md(q.q, true).replace(/^<p>|<\/p>\n?$/g, '')}</div>
      <div class="qbody"></div></div>`).join('');
  $$('.qcard', body).forEach(card => {
    const q = d.quiz.find(x => x.n === +card.dataset.q);
    const box = $('.qbody', card);
    const showButton = () => {
      box.innerHTML = '<button class="btn sm" data-r>Reveal answer</button>';
      $('[data-r]', box).onclick = async () => {
        const r = await api(`/day/${d.n}/quiz/${q.n}/answer?session_id=${store.sid}`);
        q.revealed = true; showAnswer(r.answer);
      };
    };
    const showAnswer = (answer) => {
      box.innerHTML = `<div class="qans md">${md(answer, true)}</div>
        <div class="rate"><span class="small muted" style="align-self:center">Did you get it?</span>
        ${[[0, 'Missed it'], [1, 'Partly'], [2, 'Got it']].map(([v, t]) => `<button class="btn sm ${q.rating === v ? 'sel' : ''}" data-v="${v}">${t}</button>`).join('')}</div>`;
      enhance($('.qans', box), { tryIt: false });
      $$('[data-v]', box).forEach(b => b.onclick = async () => {
        q.rating = +b.dataset.v;
        const r = await api(`/day/${d.n}/quiz/${q.n}`, { method: 'POST', body: { rating: q.rating } });
        d.progress = r.progress; $$('[data-v]', box).forEach(x => x.classList.toggle('sel', +x.dataset.v === q.rating));
        const t = $$('.tab', body.closest('.fade-in')).find(x => x.dataset.t === 'quiz'); if (t) t.querySelector('.n').textContent = `${r.progress.quiz_rated}/${r.progress.quiz_total}`;
        hooks.refreshOverview();
      });
    };
    if (q.revealed) api(`/day/${d.n}/quiz/${q.n}/answer?quiet=1`).then(r => showAnswer(r.answer)).catch(() => showAnswer(''));
    else showButton();
  });
}

// ---- Notes --------------------------------------------------------------------------------------
function notes(body, d, label) {
  tutor.setContext({ dayNo: d.n, tab: 'notes', label: label + ' · Notes' });
  body.innerHTML = `<p class="sub" style="margin-top:0">Write the one-liner you'd tell a friend about today. Also: what confused you, what clicked, and where you'd use it.</p>
    <textarea class="notes" id="nt" placeholder="• Today I learned…&#10;• Where I'd use it…&#10;• Still fuzzy…">${esc(d.notes)}</textarea>
    <div class="small muted" id="ns" style="margin-top:6px">Saved automatically</div>`;
  const save = debounce(async v => { await api(`/day/${d.n}/notes`, { method: 'POST', body: { text: v } }); $('#ns').textContent = 'Saved ✓'; }, 800);
  $('#nt').oninput = e => { d.notes = e.target.value; $('#ns').textContent = 'Saving…'; save(e.target.value); };
}

// ---- Extras (e.g., Day 30 final exam) -----------------------------------------------------------------
async function extras(body, d, label) {
  tutor.setContext({ dayNo: d.n, tab: 'extras', label });
  body.innerHTML = '<div class="muted">Loading…</div>';
  const r = await api(`/day/${d.n}/extra/${encodeURIComponent(d.extras[0])}`);
  body.innerHTML = `<div class="md">${md(r.text, true)}</div>`; enhance($('.md', body));
}
