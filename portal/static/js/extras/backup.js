// Backups & restore: a small dialog (topbar button + a button inside the settings dialog).
// Backend: portal/ex_backup.py. The portal also backs up once a day on its own.
export async function init(ctx) {
  const { api, $, esc, toast, modal, PANE } = ctx;
  const host = $('#topbar-extras');
  if (!host) return;                                   // pop-out panes have no top bar

  const btn = document.createElement('button');
  btn.className = 'iconbtn bk-btn'; btn.id = 'btn-backups'; btn.type = 'button';
  btn.title = 'Backups & restore'; btn.setAttribute('aria-label', 'Backups and restore');
  btn.innerHTML = '&#128190;';
  btn.onclick = openBackups;
  host.appendChild(btn);

  if (!PANE || PANE === 'lesson') api('/backup/auto', { method: 'POST' }).catch(() => { /* never block the page */ });

  // also offer the dialog from the settings dialog (it is built by app.js, so we add a button when it shows up)
  const root = $('#modal-root');
  if (root) new MutationObserver(() => {
    const exp = root.querySelector('a[href="/api/export"]');
    if (!exp || root.querySelector('[data-bk-open]')) return;
    const b = document.createElement('button');
    b.className = 'btn sm'; b.type = 'button'; b.dataset.bkOpen = '1'; b.innerHTML = '&#128190; Backups&hellip;';
    b.title = 'Safe copies of your progress, and restore';
    b.onclick = () => openBackups();
    exp.after(b);
  }).observe(root, { childList: true });

  const fmtSize = n => (n < 1024 * 1024 ? Math.max(1, Math.round(n / 1024)) + ' KB' : (n / 1048576).toFixed(1) + ' MB');
  const fmtWhen = iso => new Date(iso).toLocaleString(undefined, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });

  async function openBackups() {
    let data;
    try { data = await api('/backup/list'); } catch (e) { toast('Could not read the backups: ' + e.message); return; }
    modal(`<h3>Backups &amp; restore</h3>
      <p class="sub small">Everything you have done is stored in one file on this computer. The portal makes a safe copy once a day and keeps the last ${data.policy.daily} days plus ${data.policy.weekly} weekly copies. Copies are saved in <span class="mono bk-dir"></span></p>
      <div class="row bk-top"><button class="btn primary" type="button" data-now>Back up now</button><span class="small muted" data-msg role="status"></span><span class="grow"></span><button class="btn" type="button" data-x>Close</button></div>
      <div class="bk-list" data-list></div>`, {
      label: 'Backups and restore',
      onMount: (m, close) => {
        $('.bk-dir', m).textContent = data.dir;
        $('[data-x]', m).onclick = close;
        const msg = $('[data-msg]', m), list = $('[data-list]', m);
        const paint = items => {
          list.innerHTML = items.length ? items.map(it => `<div class="bk-row" data-name="${esc(it.name)}">
              <div class="bk-main"><b>${esc(fmtWhen(it.created))}</b> ${it.kind === 'pre-restore' ? '<span class="chip warn">before a restore</span>' : ''}<span class="small muted"> ${fmtSize(it.size)}</span></div>
              <div class="bk-acts"><a class="btn sm ghost" href="/api/backup/download/${encodeURIComponent(it.name)}" download title="Download this copy">Download</a><button class="btn sm" type="button" data-restore>Restore</button></div>
              <div class="bk-confirm hide" role="alertdialog" aria-label="Confirm restore">
                <p><b>Replace your current progress with this copy?</b> Everything you did after ${esc(fmtWhen(it.created))} will be replaced. Your current progress is saved first as a &ldquo;before a restore&rdquo; copy, so you can undo this.</p>
                <div class="row"><button class="btn sm primary" type="button" data-yes>Yes, restore this copy</button><button class="btn sm" type="button" data-no>Cancel</button></div>
              </div></div>`).join('')
            : '<p class="muted bk-empty">No backups yet. Press &ldquo;Back up now&rdquo; to make the first one.</p>';
        };
        paint(data.items);
        const refresh = async () => { data = await api('/backup/list'); paint(data.items); };
        $('[data-now]', m).onclick = async ev => {
          const b = ev.currentTarget; b.disabled = true; msg.textContent = 'Saving a copy…';
          try { const r = await api('/backup/now', { method: 'POST' }); await refresh(); msg.textContent = 'Saved ' + r.name; }
          catch (e) { msg.textContent = 'Could not back up: ' + e.message; }
          b.disabled = false;
        };
        list.addEventListener('click', async ev => {
          const row = ev.target.closest('.bk-row'); if (!row) return;
          const conf = $('.bk-confirm', row);
          if (ev.target.closest('[data-restore]')) { list.querySelectorAll('.bk-confirm').forEach(c => c.classList.add('hide')); conf.classList.remove('hide'); $('[data-no]', row).focus(); }
          else if (ev.target.closest('[data-no]')) { conf.classList.add('hide'); $('[data-restore]', row).focus(); }
          else if (ev.target.closest('[data-yes]')) {
            const yes = ev.target.closest('[data-yes]'); yes.disabled = true; msg.textContent = 'Restoring…';
            try {
              await api('/backup/restore', { method: 'POST', body: { name: row.dataset.name, confirm: true } });
              toast('Restored. Reloading…'); setTimeout(() => location.reload(), 600);
            } catch (e) { yes.disabled = false; msg.textContent = 'Restore failed: ' + e.message; }
          }
        });
      },
    });
  }
}
