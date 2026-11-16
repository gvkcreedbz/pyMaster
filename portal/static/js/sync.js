// Talk between windows of the app (main window + popped-out panes) over a BroadcastChannel.
//   send(type, data)            fire and forget
//   on(type, fn)                listen
//   provide(name, fn)           answer requests from other windows
//   request(name, data, opts)   ask every other window and collect their answers
const ch = 'BroadcastChannel' in window ? new BroadcastChannel('pymaster') : null;
export const WIN = Math.random().toString(36).slice(2, 9);

const handlers = {}, providers = {}, pending = {};

export const on = (t, fn) => { (handlers[t] ||= []).push(fn); };
export const send = (t, data = {}) => { try { ch?.postMessage({ t, from: WIN, ...data }); } catch { /* closed */ } };
export const provide = (name, fn) => { providers[name] = fn; };

/** Collect replies. Resolves `settle` ms after the last reply, or after `wait` ms if nobody answers. */
export function request(name, data = {}, { wait = 220, settle = 90 } = {}) {
  return new Promise(resolve => {
    if (!ch) return resolve([]);
    const id = WIN + Math.random().toString(36).slice(2, 7);
    const p = pending[id] = { got: [], timer: null, done: false };
    const finish = () => { if (p.done) return; p.done = true; clearTimeout(p.timer); clearTimeout(p.hard); delete pending[id]; resolve(p.got); };
    p.finish = finish; p.settle = settle;
    p.hard = setTimeout(finish, wait);
    send('?' + name, { id, ...data });
  });
}

if (ch) ch.onmessage = e => {
  const m = e.data;
  if (!m || m.from === WIN || typeof m.t !== 'string') return;
  if (m.t[0] === '?') {
    const fn = providers[m.t.slice(1)];
    if (fn) Promise.resolve(fn(m)).then(d => { if (d !== undefined) send('!reply', { id: m.id, data: d }); });
    return;
  }
  if (m.t === '!reply') {
    const p = pending[m.id]; if (!p) return;
    p.got.push(m.data); clearTimeout(p.timer); p.timer = setTimeout(p.finish, p.settle);
    return;
  }
  (handlers[m.t] || []).forEach(fn => fn(m));
};
