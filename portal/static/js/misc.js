import { $, $$, api, md, enhance, esc } from './util.js';
import { S } from './state.js';
import * as tutor from './tutor.js';

export async function renderLibrary(root, docId) {
  S.area = 'library'; S.dayNo = 0;
  tutor.setContext({ dayNo: null, tab: 'library', label: 'Library' });
  const my = S.seq;
  const { items } = await api('/library');
  if (my !== S.seq) return;
  docId = docId || items[0].id;
  const groups = [...new Set(items.map(i => i.group))];
  root.innerHTML = `<div class="fade-in"><div class="eyebrow">Library</div><h1 class="page-title">Guides &amp; cheatsheets</h1>
    <div class="lib" style="margin-top:20px"><nav>${groups.map(g => `<h6>${g}</h6>${items.filter(i => i.group === g).map(i => `<button data-id="${esc(i.id)}" class="${i.id === docId ? 'on' : ''}">${esc(i.title)}</button>`).join('')}`).join('')}</nav>
    <div class="md" id="doc" style="max-width:none"></div></div></div>`;
  $$('nav button', root).forEach(b => b.onclick = () => { location.hash = '#/library/' + encodeURIComponent(b.dataset.id); });
  const r = await api('/library/doc?id=' + encodeURIComponent(docId));
  if (my !== S.seq) return;
  const el = $('#doc', root);
  el.innerHTML = md(r.text, true); enhance(el);
  el.querySelector('h1')?.style && (el.querySelector('h1').style.display = 'block');
}
