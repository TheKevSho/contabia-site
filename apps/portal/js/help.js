/* ============================================================
   ContabIA Portal — help.js
   Shared help center: "?" icon in the topbar (added in nav.js)
   toggles this panel. Content below is filler — see
   "Help Center Content Handoff.md" for the real content plan.
   ============================================================ */

const HELP_DATA = [
  { label: 'Primeros pasos', items: [
    { q: '¿Cómo funciona el cierre mensual?', a: 'Cada mes el agente procesa sus documentos, concilia PMS, banco y OTAs, y arma el borrador del cierre. Su contador revisa y firma; usted solo aprueba lo que le pedimos.' },
    { q: '¿Qué significan los roles Dueño, Contador y Gerente?', a: 'Cada rol ve el portal según lo que necesita decidir: el Dueño ve la plata en juego, el Contador revisa y firma, el Gerente sube soportes y ve la operación.' },
  ]},
  { label: 'Excepciones y comprobantes', items: [
    { q: '¿Qué es una excepción?', a: 'Es un gasto o ingreso que el motor no pudo clasificar solo — por ejemplo, un pago sin documento soporte. Necesita una decisión suya o de su contador.' },
    { q: '¿Qué es el documento soporte?', a: 'Es el respaldo fiscal que exige la DIAN para gastos sin factura electrónica (Resolución 000167/2021). Sin él, el gasto no es deducible — lo generamos automáticamente cuando podemos.' },
  ]},
  { label: 'Nómina y tributario', items: [
    { q: '¿Cómo se calculan las prestaciones y parafiscales?', a: 'El motor aplica las reglas vigentes sobre cesantías, prima e intereses según el tipo de contrato de cada empleado, y lo deja listo para su revisión en Nómina.' },
    { q: '¿Cuándo vencen mis obligaciones DIAN?', a: 'Las fechas dependen de su calendario tributario (IVA, retefuente, renta). Las verá con anticipación en Tributario, con el formulario ya calculado.' },
  ]},
  { label: 'Conectores y datos', items: [
    { q: 'Un conector se desconectó, ¿qué hago?', a: 'Revise el estado en la franja superior del portal. Si sigue en rojo después de reconectar sus credenciales, escríbanos por WhatsApp y lo resolvemos.' },
    { q: '¿Mis datos están seguros?', a: 'Sí. Los datos de su negocio se usan solo para su contabilidad y se manejan con acceso restringido — nunca se comparten con terceros.' },
  ]},
];

let _helpQuery = '';

function mountHelpPanel() {
  if (document.getElementById('help-panel')) return; /* already mounted */
  const panel = document.createElement('div');
  panel.id = 'help-panel';
  panel.className = 'help-panel';
  document.body.appendChild(panel);
  renderHelpPanel();
}

function toggleHelpPanel() {
  const panel = document.getElementById('help-panel');
  if (!panel) return;
  panel.classList.toggle('open');
}

function closeHelpPanel() {
  const panel = document.getElementById('help-panel');
  if (panel) panel.classList.remove('open');
}

function setHelpQuery(v) {
  _helpQuery = (v || '').toLowerCase().trim();
  renderHelpPanel();
}

function toggleHelpItem(el) {
  el.classList.toggle('open');
}

function askAgentFromHelp() {
  closeHelpPanel();
  location.href = 'chat.html';
}

function renderHelpPanel() {
  const panel = document.getElementById('help-panel');
  if (!panel) return;
  const wasOpen = panel.classList.contains('open');

  const catsHtml = HELP_DATA.map(cat => {
    const items = cat.items.filter(it =>
      !_helpQuery || it.q.toLowerCase().includes(_helpQuery) || it.a.toLowerCase().includes(_helpQuery)
    );
    if (items.length === 0) return '';
    const itemsHtml = items.map(it => `
      <div class="help-item" onclick="toggleHelpItem(this)">
        <div class="q-row"><div class="q">${it.q}</div><div class="chev">+</div></div>
        <div class="a">${it.a}</div>
      </div>`).join('');
    return `<div><div class="help-cat-label">${cat.label}</div>${itemsHtml}</div>`;
  }).join('');

  panel.innerHTML = `
    <div class="help-head">
      <h3>Centro de ayuda</h3>
      <div class="help-close" onclick="closeHelpPanel()">✕</div>
    </div>
    <input class="help-search" placeholder="Buscar en la ayuda…" value="${_helpQuery}" oninput="setHelpQuery(this.value)">
    <div class="help-body">${catsHtml || '<div style="text-align:center;color:var(--warm-gray);font-size:13px;padding:20px 0;">Sin resultados.</div>'}</div>
    <div class="help-footer">
      <div class="prompt">¿No encontró lo que buscaba?</div>
      <div class="help-btn ask" onclick="askAgentFromHelp()">Preguntar al agente</div>
      <a class="help-btn wa" href="chat.html">Hablar con un humano por WhatsApp</a>
    </div>`;

  if (wasOpen) panel.classList.add('open');
}

/* close on outside click (but not on the help icon itself, which toggles) */
document.addEventListener('click', (e) => {
  const panel = document.getElementById('help-panel');
  if (!panel || !panel.classList.contains('open')) return;
  if (panel.contains(e.target)) return;
  if (e.target.closest && e.target.closest('.help-icon-btn')) return;
  closeHelpPanel();
});
