/* ============================================================
   ContabIA Portal — nav.js
   Renders the shared shell: left nav (11 items, 4 sections,
   role-filtered) + topbar (connector strip · lang toggle · CTA).
   Auto-injects on any page that has #sidebar-mount + #topbar-mount.

   Depends on data.js (currentRole, currentEntityData, etc.)
   ============================================================ */

/* ------------------------------------------------------------
   Nav model — single source of truth for the 11 items.
   roles: array of roles allowed to see this item.
   ------------------------------------------------------------ */
const NAV_MODEL = [
  { section: 'Principal', items: [
    { id: 'resumen',         label: 'Resumen',                 href: 'index.html',           roles: ['owner','accountant'] },
    { id: 'tracker',         label: 'Seguimiento de Cierre',   href: 'tracker.html',         roles: ['owner','accountant'] },
  ]},
  { section: 'Revisión', items: [
    { id: 'exceptions',      label: 'Excepciones',             href: 'exceptions.html',      roles: ['owner','accountant'], badge: 'exceptions' },
    { id: 'journal-entries', label: 'Comprobantes (JEs)',      href: 'journal-entries.html', roles: ['owner','accountant'], badge: 'jes', badgeClass: 'warn' },
    { id: 'reconciliacion',  label: 'Reconciliación',          href: 'reconciliacion.html',  roles: ['owner','accountant'] },
    { id: 'nomina',          label: 'Nómina',                  href: 'nomina.html',          roles: ['owner','accountant','manager'] },
    { id: 'tributario',      label: 'Tributario',              href: 'tributario.html',      roles: ['owner','accountant'] },
  ]},
  { section: 'Resultados', items: [
    { id: 'deliverables',    label: 'Entregables',             href: 'deliverables.html',    roles: ['owner','accountant'] },
    { id: 'auditoria',       label: 'Auditoría',               href: 'auditoria.html',       roles: ['owner','accountant'] },
  ]},
  { section: 'Sistema', items: [
    { id: 'configuracion',   label: 'Configuración',           href: 'configuracion.html',   roles: ['owner','accountant'] },
    { id: 'chat',            label: 'Chat con el Agente',      href: 'chat.html',            roles: ['owner','accountant','manager'] },
  ]},
];

/* role labels (Spanish) */
const ROLE_LABELS = {
  owner:      'Dueño',
  accountant: 'Contador',
  manager:    'Gerente',
  internal:   'ContabIA',
};

/* ------------------------------------------------------------
   Sidebar render
   ------------------------------------------------------------ */
function renderSidebar(activeHref) {
  const role = currentRole();
  const e    = currentEntityData();
  const meta = e.meta;
  const badges = navBadgeCounts();
  const entities = listEntitiesForUser();
  const user = DATA.user;

  /* nav sections, role-filtered */
  const navHtml = NAV_MODEL.map(sec => {
    const items = sec.items.filter(i => i.roles.includes(role));
    if (items.length === 0) return '';
    const itemsHtml = items.map(i => {
      const active = (i.href === activeHref) ? ' active' : '';
      let badge = '';
      if (i.badge && badges[i.badge] != null && badges[i.badge] > 0) {
        const cls = i.badgeClass ? ` ${i.badgeClass}` : '';
        badge = `<span class="nav-badge${cls}">${badges[i.badge]}</span>`;
      }
      return `<a href="${i.href}" class="nav-item${active}">${i.label}${badge}</a>`;
    }).join('');
    return `
      <div class="nav-section-label">${sec.section}</div>
      ${itemsHtml}`;
  }).join('');

  /* entity dropdown */
  const entitiesHtml = entities.map(ent => {
    const active = (ent.id === currentEntityId()) ? ' active' : '';
    return `
      <div class="entity-option${active}" onclick="event.stopPropagation(); setEntity('${ent.id}')">
        <div class="ent-name">${ent.name}</div>
        <div class="ent-meta">${ent.legal_name} · NIT ${ent.nit}</div>
      </div>`;
  }).join('');

  return `
  <nav class="nav">
    <div class="nav-brand">
      <div class="logo">Contab<span class="ia">IA</span></div>
      <div class="tagline">Su agente cierra sus libros.</div>
    </div>

    <div class="entity-switcher" id="entity-switcher" onclick="toggleEntityDropdown(event)">
      <div class="label">Entidad activa</div>
      <div class="name">${meta.name} <span class="chevron">▾</span></div>
      <div class="period">${meta.period.toUpperCase()}</div>
      <div class="entity-dropdown" id="entity-dropdown">
        ${entitiesHtml}
      </div>
    </div>

    ${navHtml}

    <div class="nav-footer">
      <div class="user-chip">
        <div class="avatar">${user.initials}</div>
        <div class="meta">
          <div class="name">${user.name}</div>
          <div class="role">${ROLE_LABELS[role]} · ${meta.name.split(' ')[0]}</div>
          <a href="login.html" class="signout" onclick="signOut(event)">Cerrar sesión</a>
        </div>
      </div>
    </div>
  </nav>`;
}

/* ------------------------------------------------------------
   Topbar render — connector strip + lang toggle + CTA
   ------------------------------------------------------------ */
function renderTopbar() {
  const e = currentEntityData();
  const cta = primaryCTA();

  const connHtml = e.connectors.map(c => {
    const cls = c.status === 'ok' ? '' : c.status === 'warn' ? ' warn' : ' fail';
    return `<div class="conn" title="Última sincronización: ${c.last_sync}" onclick="location.href='configuracion.html?conn=${c.id}'">
      <span class="dot${cls}"></span><span>${c.name}</span>
    </div>`;
  }).join('');

  const ctaHtml = cta ? `<button class="btn btn-primary" onclick="location.href='${cta.href}'">${cta.text}</button>` : '';

  return `
    <div class="topbar">
      <div class="connector-strip">${connHtml}</div>
      <div class="topbar-right">
        <div class="lang-toggle" onclick="toggleLang()">ES · EN</div>
        ${ctaHtml}
      </div>
    </div>`;
}

/* ------------------------------------------------------------
   Interactions
   ------------------------------------------------------------ */
function toggleEntityDropdown(ev) {
  if (ev) ev.stopPropagation();
  const dd = document.getElementById('entity-dropdown');
  if (dd) dd.classList.toggle('open');
}
function closeEntityDropdown() {
  const dd = document.getElementById('entity-dropdown');
  if (dd) dd.classList.remove('open');
}
function toggleLang() {
  const cur = sessionStorage.getItem('contabia_lang') || 'es';
  const next = cur === 'es' ? 'en' : 'es';
  sessionStorage.setItem('contabia_lang', next);
  /* EN is UI-only; data stays Spanish. v1: visual feedback only. */
  document.querySelectorAll('.lang-toggle').forEach(t => {
    t.textContent = next === 'es' ? 'ES · EN' : 'EN · ES';
  });
}
function signOut(ev) {
  ev.preventDefault();
  sessionStorage.removeItem('contabia_auth');
  sessionStorage.removeItem('contabia_role');
  sessionStorage.removeItem('contabia_entity');
  location.href = 'login.html';
}

/* ------------------------------------------------------------
   Auto-inject + mobile hamburger
   ------------------------------------------------------------ */
document.addEventListener('DOMContentLoaded', () => {
  const sidebarMount = document.getElementById('sidebar-mount');
  const topbarMount  = document.getElementById('topbar-mount');
  if (!sidebarMount) return;

  const page = window.location.pathname.split('/').pop() || 'index.html';

  /* manager-only enforcement: redirect off pages they shouldn't see */
  const role = currentRole();
  if (role === 'manager') {
    const allowedHrefs = NAV_MODEL.flatMap(s => s.items)
      .filter(i => i.roles.includes('manager'))
      .map(i => i.href);
    if (!allowedHrefs.includes(page) && page !== 'login.html' && page !== 'login-contador.html' && page !== 'login-gerente.html') {
      location.replace('nomina.html');
      return;
    }
  }

  sidebarMount.innerHTML = renderSidebar(page);
  if (topbarMount) topbarMount.innerHTML = renderTopbar();

  /* mobile hamburger (hidden on desktop via CSS) */
  if (!document.getElementById('sidebar-toggle')) {
    const toggle = document.createElement('button');
    toggle.id = 'sidebar-toggle';
    toggle.className = 'sidebar-toggle';
    toggle.setAttribute('aria-label', 'Abrir menú');
    toggle.innerHTML = '<span></span><span></span><span></span>';
    document.body.appendChild(toggle);
  }
  if (!document.getElementById('sidebar-backdrop')) {
    const backdrop = document.createElement('div');
    backdrop.id = 'sidebar-backdrop';
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);
  }
  const sidebar  = document.querySelector('.nav');
  const toggleEl = document.getElementById('sidebar-toggle');
  const backdrop = document.getElementById('sidebar-backdrop');
  const open  = () => { sidebar.classList.add('open');  backdrop.classList.add('open');  document.body.classList.add('no-scroll'); };
  const close = () => { sidebar.classList.remove('open'); backdrop.classList.remove('open'); document.body.classList.remove('no-scroll'); };
  toggleEl.addEventListener('click', () => sidebar.classList.contains('open') ? close() : open());
  backdrop.addEventListener('click', close);
  sidebar.querySelectorAll('.nav-item').forEach(a => a.addEventListener('click', close));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

  /* close entity dropdown on outside click */
  document.addEventListener('click', closeEntityDropdown);

  /* restore lang state */
  const lang = sessionStorage.getItem('contabia_lang') || 'es';
  document.querySelectorAll('.lang-toggle').forEach(t => {
    t.textContent = lang === 'es' ? 'ES · EN' : 'EN · ES';
  });
});
