// Practice: mixed, unlabeled problems from every day you have reached, with adaptive difficulty, a 3-step hint ladder,
// a "think out loud" box (with dictation where the browser supports it), confidence ratings and a calibration view.
// Backend: portal/ex_practice.py (/api/practice/*). The problems are the verified drills; the card UI is shared with drills.js.
import { drillCard } from '/static/js/extras/drills.js';

let C;
const newId = () => 'ps' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
const CONF = [[1, 'Not sure'], [2, 'Fairly sure'], [3, 'Certain']];
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function el(tag, attrs = {}, kids = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else if (k === 'html') e.innerHTML = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of [].concat(kids)) if (c != null) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
}

// ---- dictation: the browser's own speech recognition (no key). Chrome/Edge send the audio to their speech service. ----------
function micButton(ta) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  let rec = null, base = '';
  const b = el('button', { class: 'btn ghost sm pr-mic', type: 'button', text: '🎤 Dictate', 'aria-pressed': 'false',
    title: 'Speak your thinking. Uses your browser\'s speech recognition (Chrome and Edge send the audio to their speech service). Review the text before sending.' });
  const stop = () => { try { rec?.stop(); } catch { /* already stopped */ } };
  b.onclick = () => {
    if (rec) { stop(); return; }
    rec = new SR(); rec.lang = navigator.language || 'en-US'; rec.interimResults = true; rec.continuous = true;
    base = ta.value ? ta.value.replace(/\s*$/, ' ') : '';
    rec.onresult = e => { let s = ''; for (let i = 0; i < e.results.length; i++) s += e.results[i][0].transcript; ta.value = base + s; ta.dispatchEvent(new Event('input')); };
    rec.onend = () => { rec = null; b.textContent = '🎤 Dictate'; b.setAttribute('aria-pressed', 'false'); };
    rec.onerror = ev => { C.toast(ev.error === 'not-allowed' ? 'Microphone permission was denied.' : 'Dictation stopped (' + ev.error + ').'); };
    try { rec.start(); b.textContent = '⏹ Stop'; b.setAttribute('aria-pressed', 'true'); } catch { rec = null; }
  };
  b.stopNow = stop;
  return b;
}

// ---- the page --------------------------------------------------------------------------------------------------------------
async function render(view) {
  const sum = await C.api('/practice/summary').catch(() => null);
  const intro = el('div', { class: 'pr' });
  view.replaceChildren(intro);
  const all = sum?.all || { problems: 0, solved: 0 };
  intro.append(
    el('div', { class: 'eyebrow', text: 'After the lessons: can you recognise the idea on your own?' }),
    el('h1', { class: 'page-title', text: 'Practice' }),
    el('p', { class: 'sub', style: 'max-width:64ch', html: 'Following a lesson is one skill. Knowing <b>which idea a problem needs when nothing names it</b> is another, and it is the one that sticks. A practice session mixes problems from every day you have opened, hides the topic, and adjusts to you: harder after three good answers in a row, easier after two misses.' }),
    el('ul', { class: 'pr-how' }, [
      el('li', { html: '<b>Think out loud.</b> Write (or dictate) what you notice and what you are unsure about. It is saved with your answer.' }),
      el('li', { html: '<b>Rate your confidence</b> before you check. Over time you see whether feeling sure means being right.' }),
      el('li', { html: '<b>Smallest hint first.</b> Three hints, from "what area" to a narrow nudge. The solution appears only when the problem ends.' }),
    ]));
  const scopeBox = el('div', { class: 'pr-scope', role: 'radiogroup', 'aria-label': 'Which days to draw from' });
  const days = sum?.reached_days ?? 0;
  let scope = 'reached';
  for (const [v, label] of [['reached', `Days I have opened (${days})`], ['all', 'All 30 days']]) {
    const r = el('input', { type: 'radio', name: 'pr-scope', value: v, ...(v === scope ? { checked: true } : {}), onchange: () => { scope = v; } });
    scopeBox.append(el('label', { class: 'pr-opt' }, [r, ' ', label]));
  }
  intro.append(scopeBox, el('div', { class: 'row', style: 'margin:14px 0 24px' }, [
    el('button', { class: 'btn primary', type: 'button', id: 'pr-start', text: all.problems ? 'Start another session' : 'Start a session', onclick: () => session(view, scope) })]));
  if (all.problems) intro.append(overview(sum));
  else intro.append(el('p', { class: 'muted small', text: 'Nothing here yet. Your first session will start with easier problems and adapt.' }));
}

function overview(sum) {
  const a = sum.all, cal = sum.calibration;
  const wrap = el('div', { class: 'pr-ov' });
  wrap.append(el('div', { class: 'pr-stats' }, [
    stat(sum.sessions, 'sessions'), stat(a.problems, 'problems'), stat(a.problems ? Math.round(100 * a.solved / a.problems) + '%' : '-', 'solved'),
    stat(a.first_try, 'solved first try, no hints'), stat(a.avg_hints, 'hints per problem')]));
  wrap.append(calibrationCard(cal));
  if (sum.weak?.length) {
    wrap.append(el('div', { class: 'card pad pr-weak' }, [el('h3', { text: 'Worth another look' }),
      el('p', { class: 'small muted', text: 'Ideas that cost you misses or several hints. Open the day, then try its drills.' }),
      ...sum.weak.map(w => el('a', { class: 'chip', href: `#/day/${w.day}/drills`, text: `Day ${w.day} · ${w.concept}` }))]));
  }
  return wrap;
}
const stat = (n, label) => el('div', { class: 'pr-stat' }, [el('b', { text: String(n) }), el('span', { text: label })]);

function calibrationCard(cal) {
  const card = el('div', { class: 'card pad pr-cal' }, [el('h3', { text: 'Does feeling sure mean being right?' })]);
  if (!cal || !cal.rated) { card.append(el('p', { class: 'small muted', text: 'Rate your confidence on a few problems and this fills in.' })); return card; }
  card.append(el('div', { class: 'pr-bars' }, cal.levels.map(l => el('div', { class: 'pr-barrow' }, [
    el('span', { class: 'lbl', text: l.label }),
    el('div', { class: 'track', role: 'img', 'aria-label': `${l.label}: ${l.pct ?? 0}% right of ${l.n}` }, [el('i', { style: `width:${l.pct ?? 0}%` })]),
    el('span', { class: 'val', text: l.n ? `${l.pct}% of ${l.n}` : 'no data' })]))));
  const bits = [];
  if (cal.certain_and_wrong) bits.push(`${cal.certain_and_wrong} time${cal.certain_and_wrong > 1 ? 's' : ''} you were certain and wrong: those hide misconceptions, so they are the most useful ones to review.`);
  if (cal.lucky_guesses) bits.push(`${cal.lucky_guesses} lucky guess${cal.lucky_guesses > 1 ? 'es' : ''} (not sure, but right).`);
  if (cal.note) bits.push(cal.note);
  if (bits.length) card.append(el('p', { class: 'small', text: bits.join(' ') }));
  return card;
}

// ---- a session -------------------------------------------------------------------------------------------------------------------
async function session(view, scope) {
  const ps = newId();
  let count = 0;
  const top = el('div', { class: 'pr-top' });
  const stage = el('div', { class: 'pr' });
  view.replaceChildren(stage);

  async function nextProblem() {
    stage.replaceChildren(el('div', { class: 'muted', text: 'Picking a problem…' }));
    let r;
    try { r = await C.api('/practice/next', { method: 'POST', body: { psession: ps, session_id: C.store.sid, scope } }); }
    catch (e) { stage.replaceChildren(el('div', { class: 'card pad', text: 'Could not get a problem: ' + e.message })); return; }
    if (r.done) return finish(r.reason);
    count = r.number;
    showProblem(r);
  }

  function showProblem(r) {
    const t0 = Date.now();
    let hintsUsed = 0, conf = null, tryNo = 0;
    const header = el('div', { class: 'pr-top' }, [
      el('div', {}, [el('span', { class: 'pr-num', text: `Problem ${r.number}` }), el('span', { class: 'pr-lvl', title: 'Difficulty of this problem, 1 (easy) to 5 (hard)', text: `Level ${r.level}` })]),
      el('button', { class: 'btn ghost sm', type: 'button', id: 'pr-end', text: 'End session', onclick: () => finish() })]);
    const thinking = el('textarea', { class: 'dr-area pr-think', id: 'pr-think', rows: 3, maxlength: 1500, 'aria-label': 'Think out loud',
      placeholder: 'Think out loud: what do you notice? What is the first thing you would try? What are you unsure about?' });
    const mic = micButton(thinking);
    const confRow = el('div', { class: 'pr-conf', role: 'radiogroup', 'aria-label': 'How sure are you?' }, CONF.map(([v, label]) =>
      el('button', { class: 'btn ghost sm', type: 'button', role: 'radio', 'aria-checked': 'false', 'data-c': v, text: label, onclick: ev => {
        conf = conf === v ? null : v;
        confRow.querySelectorAll('button').forEach(b => { const on = +b.dataset.c === conf; b.classList.toggle('on', on); b.setAttribute('aria-checked', String(on)); });
        ev.currentTarget.blur?.();
      } })));
    const hintBox = el('div', { class: 'pr-hints', 'aria-live': 'polite' });
    const hintBtn = el('button', { class: 'btn ghost sm', type: 'button', id: 'pr-hint', text: `Need a hint? (0 of ${r.hint_steps})`, onclick: async () => {
      if (hintsUsed >= r.hint_steps) return;
      hintBtn.disabled = true;
      try {
        const h = await C.api(`/practice/${r.pid}/hint`, { method: 'POST', body: { step: hintsUsed + 1 } });
        hintsUsed = h.step;
        hintBox.append(el('p', { class: 'pr-hint', html: `<b>Hint ${h.step}:</b> ${esc(h.text)}` }));
        hintBtn.textContent = hintsUsed >= r.hint_steps ? 'No more hints' : `Another hint? (${hintsUsed} of ${r.hint_steps})`;
        hintBtn.disabled = hintsUsed >= r.hint_steps;
      } catch (e) { C.toast('Could not get a hint: ' + e.message); hintBtn.disabled = false; }
    } });
    const common = () => ({ psession: ps, session_id: C.store.sid, thinking: thinking.value, confidence: conf, hints: hintsUsed, seconds: (Date.now() - t0) / 1000 });
    const reveal = el('div', { class: 'pr-reveal', 'aria-live': 'polite' });
    const card = drillCard({ n: 0 }, { ...r.problem, title: '', state: null }, () => nextProblem(), () => nextProblem(), {
      hideTitle: true, noHint: true, noAsk: true, noSummary: true, nextLabel: 'Next problem →',
      checkFn: async (answer, n) => { tryNo = n; return C.api(`/practice/${r.pid}/check`, { method: 'POST', body: { ...common(), answer, tries: n } }); },
      giveupFn: () => C.api(`/practice/${r.pid}/giveup`, { method: 'POST', body: { ...common(), tries: Math.max(1, tryNo) } }),
      onFinish: (res) => {                                   // the problem is over: now it may name itself
        mic?.stopNow?.();
        [thinking, ...confRow.querySelectorAll('button'), hintBtn].forEach(x => { x.disabled = true; });
        reveal.replaceChildren(el('div', { class: 'dr-fine' }, [
          'That was ', el('a', { href: `#/day/${res.day}/learn`, text: `Day ${res.day}` }), ' · ', el('b', { text: res.title || '' }),
          res.concepts?.length ? ' · ' + res.concepts.join(', ') : '']));
      },
    });
    card.dataset.pid = r.pid;                                // read by the browser test; not shown to the learner
    const aids = el('div', { class: 'pr-aids' }, [
      el('label', { class: 'pr-lab', for: 'pr-think', text: 'Your thinking' }), thinking, ...(mic ? [mic] : []),
      el('div', { class: 'pr-confrow' }, [el('span', { class: 'pr-lab', text: 'How sure are you?' }), confRow]),
      el('div', { class: 'pr-hintrow' }, [hintBtn, hintBox])]);
    stage.replaceChildren(header, card, aids, reveal);
    thinking.focus({ preventScroll: true });
  }

  async function finish(reason) {
    stage.replaceChildren(el('div', { class: 'muted', text: 'Wrapping up…' }));
    let s;
    try { s = await C.api('/practice/end', { method: 'POST', body: { psession: ps, session_id: C.store.sid } }); }
    catch (e) { stage.replaceChildren(el('div', { class: 'card pad', text: 'Could not load the summary: ' + e.message })); return; }
    const me = s.session;
    const box = el('div', { class: 'pr' }, [
      el('div', { class: 'eyebrow', text: 'Session finished' }), el('h1', { class: 'page-title', text: me.problems ? `${me.solved} of ${me.problems} solved` : 'No problems this time' }),
      reason ? el('p', { class: 'sub', text: reason }) : null,
      me.problems ? el('div', { class: 'pr-stats' }, [stat(me.first_try, 'first try, no hints'), stat(me.with_hints, 'used a hint'), stat(me.gave_up, 'showed the answer'), stat(s.level ?? '-', 'level you reached')]) : null,
      me.problems ? calibrationCard(s.calibration) : null]);
    const missed = (s.review || []).filter(x => !x.ok || x.hints >= 2);
    if (missed.length) box.append(el('div', { class: 'card pad' }, [el('h3', { text: 'To revisit' }),
      el('p', { class: 'small muted', text: 'These needed help or were missed. The day is where the idea is taught; its Drills tab has more of the same.' }),
      ...missed.map(x => el('a', { class: 'chip', href: `#/day/${x.day}/drills`, text: `Day ${x.day} · ${x.type}` }))]));
    box.append(el('div', { class: 'row', style: 'margin-top:18px;gap:10px' }, [
      el('button', { class: 'btn primary', type: 'button', text: 'Another session', onclick: () => render(view) }),
      el('a', { class: 'btn', href: '#/', text: 'Back to Home' })]));
    view.replaceChildren(box);
  }

  stage.append(top);
  nextProblem();
}

// ---- small cards in other places ------------------------------------------------------------------------------------------------------
async function decorate(hash) {
  const view = document.querySelector('#view');
  if (!view) return;
  if (hash === '#/' || hash === '') {
    if (view.querySelector('#pr-home-card')) return;
    const card = el('div', { class: 'card pad pr-home', id: 'pr-home-card' }, [
      el('div', { class: 'grow' }, [el('b', { text: 'Practice session' }), el('div', { class: 'sub small', text: 'Mixed problems from the days you have opened, with the topic hidden. It adapts as you go.' })]),
      el('a', { class: 'btn', href: '#/practice', text: 'Start practising' })]);
    view.append(card);
  } else if (hash.startsWith('#/insights')) {
    if (view.querySelector('#pr-ins-card')) return;
    const s = await C.api('/practice/summary').catch(() => null);
    if (!s || !s.calibration?.rated) return;
    const card = calibrationCard(s.calibration); card.id = 'pr-ins-card';
    view.append(card);
  }
}

export async function init(ctx) {
  C = ctx;
  if (C.PANE && C.PANE !== 'lesson') return;
  C.registerPage({ id: 'practice', label: 'Practice', icon: '&#9889;', title: 'Practice', render,
    action: { title: 'Start a practice session', sub: 'mixed problems, topic hidden, adaptive', keys: 'practice mixed review interleaved quiz problems hints confidence' } });
  document.addEventListener('pm:route', e => { decorate(e.detail.hash || '#/'); });
  decorate(location.hash || '#/');
}
