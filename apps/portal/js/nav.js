/* ============================================================
   ContabIA Portal — nav.js
   Renders the shared shell: left nav (12 items, 4 sections,
   role-filtered, collapsible) + topbar (connector strip · help ·
   lang toggle · CTA). Auto-injects on any page that has
   #sidebar-mount + #topbar-mount.

   Depends on data.js (currentRole, currentEntityData, etc.)
   ============================================================ */

/* ------------------------------------------------------------
   Nav model — single source of truth. "Chat con el Agente" sits
   in Principal (alongside Resumen/Seguimiento) — the agent is a
   primary destination, not a system setting.
   glyph: single mono-font character shown when the rail is
   collapsed to icon-only.
   ------------------------------------------------------------ */
/* Entity logos — plain data URIs baked in at build time (replaces the
   Claude-design-canvas <image-slot> component, which isn't part of the
   real portal stack). No baked-in logo for an entity → falls back to a
   terracotta monogram, so adding a new entity needs no code change. */
const ENTITY_LOGOS = {
  'cantamar-001': 'data:image/webp;base64,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',
  'sonata-001':   'data:image/webp;base64,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',
};

/* The period shown in the switcher is the close period that is still OPEN —
   the month the agent is working on, not the last one delivered. It is
   labelled as such so "JUNIO 2026" can't be misread as "already closed".
   Source of truth: DATA.entities_meta[].close_status. */
function openPeriodLabel(meta) {
  const live = (typeof isLiveMode === 'function' && isLiveMode() && window.__liveSummary);
  const status = (live && live.meta && live.meta.close_status)
    || meta.close_status
    || ((typeof DATA !== 'undefined' && DATA.entities_meta || []).find(e => e.id === meta.id) || {}).close_status
    || 'in_progress';
  const suffix = status === 'closed'
    ? (typeof t === 'function' ? t('period_closed') : 'CERRADO')
    : status === 'in_review'
      ? (typeof t === 'function' ? t('period_review') : 'EN REVISIÓN')
      : (typeof t === 'function' ? t('period_in_progress') : 'EN CURSO');
  const period = (live && live.closeSummary && live.closeSummary.period)
    ? String(live.closeSummary.period)
    : (meta.period || '');
  const pretty = period.length === 7
    ? ({ '2026-07': 'JULIO 2026', '2026-06': 'JUNIO 2026' }[period] || period.toUpperCase())
    : period.toUpperCase();
  return `${pretty} · ${suffix}`;
}

function entityLogoHtml(meta, sizeClass) {
  const src = ENTITY_LOGOS[meta.id];
  if (src) {
    return `<img src="${src}" class="${sizeClass}" alt="${meta.name}">`;
  }
  return `<div class="${sizeClass} logo-placeholder">${meta.name.charAt(0)}</div>`;
}

const NAV_MODEL = [
  { section: 'Principal', items: [
    { id: 'resumen',         label: 'Resumen',                 href: 'index.html',           roles: ['owner','accountant'], glyph: 'R' },
    { id: 'chat',            label: 'Chat con el Agente',      href: 'chat.html',            roles: ['owner','accountant','manager'], glyph: 'A' },
    { id: 'tracker',         label: 'Seguimiento de Cierre',   href: 'tracker.html',         roles: ['owner','accountant'], glyph: 'S' },
  ]},
  { section: 'Revisión', items: [
    { id: 'exceptions',      label: 'Excepciones',             href: 'exceptions.html',      roles: ['owner','accountant'], badge: 'exceptions', glyph: '!' },
    { id: 'journal-entries', label: 'Comprobantes (JEs)',      href: 'journal-entries.html', roles: ['owner','accountant'], badge: 'jes', badgeClass: 'warn', glyph: 'J' },
    { id: 'reconciliacion',  label: 'Reconciliación',          href: 'reconciliacion.html',  roles: ['owner','accountant'], glyph: 'C' },
    { id: 'nomina',          label: 'Nómina',                  href: 'nomina.html',          roles: ['owner','accountant','manager'], glyph: 'N' },
    { id: 'tributario',      label: 'Tributario',              href: 'tributario.html',      roles: ['owner','accountant'], glyph: 'T' },
  ]},
  { section: 'Resultados', items: [
    { id: 'boveda',          label: 'Bóveda',                  href: 'boveda.html',          roles: ['owner','accountant','manager'], glyph: 'B' },
    { id: 'deliverables',    label: 'Entregables',             href: 'deliverables.html',    roles: ['owner','accountant','manager'], glyph: 'E' },
    { id: 'auditoria',       label: 'Auditoría',               href: 'auditoria.html',       roles: ['owner','accountant'], glyph: '◷' },
  ]},
  { section: 'Sistema', items: [
    { id: 'configuracion',   label: 'Configuración',           href: 'configuracion.html',   roles: ['owner','accountant'], glyph: '⚙' },
  ]},
];

/* role labels (Spanish) */
const ROLE_LABELS = {
  owner:      'Dueño',
  accountant: 'Contador',
  manager:    'Gerente',
  internal:   'ContabIA',
};

/* collapse state — persisted across pages/sessions, same pattern
   as theme.js's contabia-theme. */
function _getStoredNavCollapsed() {
  try { return localStorage.getItem('contabia-nav-collapsed') === '1'; }
  catch (e) { return false; }
}
function _setStoredNavCollapsed(v) {
  try { localStorage.setItem('contabia-nav-collapsed', v ? '1' : '0'); }
  catch (e) {}
}
let _navCollapsed = _getStoredNavCollapsed();

/* peeking — transient, NOT persisted. True only while the mouse is over
   a currently pinned-collapsed rail (see onSidebarMouseEnter/Leave,
   wired in the DOMContentLoaded handler below). */
let _navPeeking = false;

/* ------------------------------------------------------------
   Sidebar render
   ------------------------------------------------------------ */
function renderSidebar(activeHref) {
  const role = currentRole();
  const e    = currentEntityData();
  const meta = e.meta;
  const badges = navBadgeCounts();
  const entities = listEntitiesForUser();
  const user = currentUser();
  const collapsed = _navCollapsed;
  /* Both the collapsed and expanded markup for every swappable part
     (brand, entity card, item labels, section headers, footer meta)
     are ALWAYS rendered below — which one is visible is decided purely
     by CSS off .nav.collapsed / .nav.collapsed.peeking (see portal.css).
     This function only runs on initial load and on an explicit pin
     toggle click — never on hover — so a hover-triggered peek can never
     replace/detach the very node the user is trying to click (that was
     the bug in the first cut of this feature: re-rendering on
     mouseenter destroyed the collapse button and nav-item links out
     from under in-flight clicks). See onSidebarMouseEnter/Leave. */

  /* nav sections, role-filtered */
  const model = (typeof liveNavFilter === 'function') ? liveNavFilter(NAV_MODEL) : NAV_MODEL;
  const navHtml = model.map(sec => {
    const items = sec.items.filter(i => i.roles.includes(role));
    if (items.length === 0) return '';
    const itemsHtml = items.map(i => {
      const active = (i.href === activeHref) ? ' active' : '';
      let badge = '';
      if (i.badge && badges[i.badge] != null && badges[i.badge] > 0) {
        const cls = i.badgeClass ? ` ${i.badgeClass}` : '';
        badge = `<span class="nav-badge${cls}">${badges[i.badge]}</span>`;
      }
      const label = (typeof navLabel === 'function') ? navLabel(i.id, i.label) : i.label;
      return `<a href="${i.href}" class="nav-item${active}" title="${label}"><span class="item-main"><span class="glyph">${i.glyph || '·'}</span><span class="label">${label}</span></span>${badge}</a>`;
    }).join('');
    const sectionLabel = (typeof navLabel === 'function') ? navLabel(sec.section, sec.section) : sec.section;
    return `<div class="nav-section-label">${sectionLabel}</div>${itemsHtml}`;
  }).join('');

  /* entity dropdown (expanded only) */
  const entitiesHtml = entities.map(ent => {
    const active = (ent.id === currentEntityId()) ? ' active' : '';
    return `
      <div class="entity-option${active}" onclick="event.stopPropagation(); setEntity('${ent.id}')">
        <div class="ent-name">${ent.name}</div>
        <div class="ent-meta">${ent.legal_name} · NIT ${ent.nit}</div>
      </div>`;
  }).join('');

  const brandHtml = `
    <div class="nav-brand">
      <div class="brand-mark" title="ContabIA">C</div>
      <div class="brand-full">
        <div class="logo">Contab<span class="ia">IA</span></div>
      </div>
    </div>`;

  const entityHtml = `
    <div class="es-collapsed-logo-wrap" title="${meta.name}">${entityLogoHtml(meta, 'es-collapsed-logo')}</div>
    <div class="entity-switcher" id="entity-switcher">
        <div class="es-row" onclick="toggleEntityDropdown(event)">
          <div class="es-logo-wrap">${entityLogoHtml(meta, 'es-logo')}</div>
          <div class="es-text">
            <div class="label">${typeof t === 'function' ? t('entity_active') : 'Entidad activa'}</div>
            <div class="name"><span class="name-text" title="${meta.name}">${meta.name}</span></div>
          </div>
          <span class="chevron">▾</span>
        </div>
        <div class="period">${openPeriodLabel(meta)}</div>
      <div class="entity-dropdown" id="entity-dropdown">
        ${entitiesHtml}
      </div>
    </div>`;

  const footerMeta = `
    <div class="meta">
      <div class="name">${user.name}</div>
      <div class="role">${(typeof t === 'function' ? ((t('role') || {})[role] || ROLE_LABELS[role]) : ROLE_LABELS[role])} · ${meta.name.split(' ')[0]}</div>
      <a href="login.html" class="signout" onclick="signOut(event)">${typeof t === 'function' ? t('signout') : 'Cerrar sesión'}</a>
    </div>`;

  return `
  <nav class="nav${collapsed ? ' collapsed' : ''}">
    <div class="nav-collapse-btn" title="Colapsar / expandir" onclick="toggleSidebarCollapse()">${collapsed ? '›' : '‹'}</div>
    ${brandHtml}
    ${entityHtml}
    <div class="nav-scroll">${navHtml}</div>
    <div class="nav-footer">
      <div id="appearance-popover" class="appearance-popover"></div>
      <div class="user-chip" onclick="toggleAppearancePopover(event)">
        <div class="avatar">${user.initials}</div>
        ${footerMeta}
      </div>
    </div>
  </nav>`;
}

/* ------------------------------------------------------------
   Topbar render — connector strip + help + lang toggle + CTA
   ------------------------------------------------------------ */
/* connector status strip — collapsed to a single summary pill by
   default, click to expand the per-connector detail row (mirrors
   the approved design's toggleConnectors behavior) */
let _connectorsOpen = false;

/* language — ES (Colombia flag) / EN, shown as a circular toggle
   in the topbar, left of the help icon */
function currentLang() {
  try { return sessionStorage.getItem('contabia_lang') || 'es'; }
  catch (e) { return 'es'; }
}

function renderTopbar() {
  const e = currentEntityData();
  const cta = primaryCTA();
  const lang = currentLang();

  const worst = e.connectors.reduce((acc, c) => {
    if (c.status === 'fail') return 'fail';
    if (c.status === 'warn' && acc !== 'fail') return 'warn';
    return acc;
  }, 'ok');
  const issues = e.connectors.filter(c => c.status !== 'ok').length;
  const pillDot   = worst === 'fail' ? 'var(--critical)' : worst === 'warn' ? 'var(--warning)' : 'var(--success)';
  const pillHalo  = worst === 'fail' ? 'rgba(196,74,58,.22)' : worst === 'warn' ? 'rgba(212,160,74,.25)' : 'rgba(74,139,111,.22)';
  const pillLabel = issues
    ? (issues + (issues === 1
        ? (typeof t === 'function' ? t('connectors_warn_one') : ' conector con aviso')
        : (typeof t === 'function' ? t('connectors_warn_many') : ' conectores con aviso')))
    : (typeof t === 'function' ? t('connectors_ok') : 'Todo conectado');

  const connRows = e.connectors.map(c => {
    const dot = c.status === 'ok' ? 'var(--success)' : c.status === 'warn' ? 'var(--warning)' : 'var(--critical)';
    return `<div class="conn-row"><span class="dot" style="background:${dot};"></span><span class="name">${c.name}</span><span class="last">${c.last_sync}</span></div>`;
  }).join('');

  const ctaHtml = cta ? `<button class="btn btn-primary" onclick="location.href='${cta.href}'">${cta.text}</button>` : '';

  const flagHtml = lang === 'es'
    ? `<div class="co-flag"><span></span><span></span><span></span></div>`
    : `<div class="en-flag">EN</div>`;

  return `
    <div class="topbar">
      <div class="conn-pill" title="Estado de conectores" onclick="toggleConnectorStrip()">
        <span class="dot" style="background:${pillDot}; box-shadow:0 0 0 3px ${pillHalo};"></span>
        <span class="pill-label">${pillLabel}</span>
        <span class="chev">▾</span>
      </div>
      <div class="topbar-right">
        <div class="lang-flag-btn" title="${lang === 'es' ? 'Español' : 'English'}" onclick="toggleLang()">${flagHtml}</div>
        <div class="help-icon-btn" title="Centro de ayuda" onclick="toggleHelpPanel()">?</div>
        ${ctaHtml}
      </div>
    </div>
    <div class="conn-strip${_connectorsOpen ? ' open' : ''}" id="conn-strip">${connRows}</div>`;
}

/* ------------------------------------------------------------
   Demo-mode banner — shown whenever contabia_demo is set (real
   client logins never set this flag; only the ?demo=1 landings
   in login.html/login-contador.html/login-gerente.html do).
   Keeps demo sessions visually distinct from a real client login.
   ------------------------------------------------------------ */
function renderDemoBanner() {
  let isDemo = false;
  try { isDemo = sessionStorage.getItem('contabia_demo') === '1'; } catch (e) {}
  if (!isDemo) return '';
  return `
    <div class="demo-banner" style="background:var(--terracotta); color:var(--on-dark); font-size:13px; font-weight:600; text-align:center; padding:7px 12px; display:flex; align-items:center; justify-content:center; gap:10px;">
      <span>${typeof t === 'function' ? t('demo.banner') : 'Modo demostración — datos ficticios, no es una cuenta real'}</span>
      <a href="#" style="color:var(--on-dark); text-decoration:underline;" onclick="exitDemo(event)">${typeof t === 'function' ? t('link.salir_demo') : 'Salir de la demo'}</a>
    </div>`;
}
function exitDemo(ev) {
  if (ev) ev.preventDefault();
  try {
    sessionStorage.removeItem('contabia_auth');
    sessionStorage.removeItem('contabia_role');
    sessionStorage.removeItem('contabia_entity');
    sessionStorage.removeItem('contabia_demo');
  } catch (e) {}
  location.href = 'https://contabia.co';
}

function toggleConnectorStrip() {
  _connectorsOpen = !_connectorsOpen;
  const strip = document.getElementById('conn-strip');
  if (strip) strip.classList.toggle('open', _connectorsOpen);
}

/* ------------------------------------------------------------
   Interactions
   ------------------------------------------------------------ */
function toggleSidebarCollapse() {
  _navCollapsed = !_navCollapsed;
  _navPeeking = false; /* always start clean — avoids a stale peek carrying
                          over into the freshly (un)pinned state */
  _setStoredNavCollapsed(_navCollapsed);
  const mount = document.getElementById('sidebar-mount');
  let page = window.location.pathname.split('/').pop() || 'index.html';
  if (page && !page.includes('.')) page += '.html';
  if (mount) mount.innerHTML = renderSidebar(page);
  renderAppearancePopover();
  attachNavHoverListeners();
}

/* ------------------------------------------------------------
   Hover-to-peek on the collapsed rail — a PURE CSS class toggle.
   Both variants of every swappable bit are already in the DOM (see
   renderSidebar), so peeking never touches innerHTML/replaces nodes;
   it just flips .peeking on the existing <nav>, which is cheap and
   can't race with — or eat — an in-flight click on the collapse
   button or a nav-item link.
   ------------------------------------------------------------ */
function onSidebarMouseEnter() {
  if (_navCollapsed) {
    _navPeeking = true;
    const nav = document.querySelector('.nav');
    if (nav) nav.classList.add('peeking');
  }
}
function onSidebarMouseLeave() {
  _navPeeking = false;
  const nav = document.querySelector('.nav');
  if (nav) nav.classList.remove('peeking');
}
function attachNavHoverListeners() {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  nav.addEventListener('mouseenter', onSidebarMouseEnter);
  nav.addEventListener('mouseleave', onSidebarMouseLeave);
}

function toggleEntityDropdown(ev) {
  if (ev) ev.stopPropagation();
  const dd = document.getElementById('entity-dropdown');
  if (dd) dd.classList.toggle('open');
}
function closeEntityDropdown() {
  const dd = document.getElementById('entity-dropdown');
  if (dd) dd.classList.remove('open');
}

function toggleAppearancePopover(ev) {
  if (ev) ev.stopPropagation();
  const pop = document.getElementById('appearance-popover');
  if (pop) pop.classList.toggle('open');
}
function closeAppearancePopover() {
  const pop = document.getElementById('appearance-popover');
  if (pop) pop.classList.remove('open');
}
function pickTheme(t, ev) {
  if (ev) ev.stopPropagation();
  if (typeof setContabiaTheme === 'function') setContabiaTheme(t);
}
function pickPreviewRole(role, ev) {
  if (ev) ev.stopPropagation();
  sessionStorage.setItem('contabia_role', role);
  location.reload();
}
function renderAppearancePopover() {
  const pop = document.getElementById('appearance-popover');
  if (!pop) return;
  const curTheme = (typeof getContabiaTheme === 'function') ? getContabiaTheme() : 'system';
  const curRole = currentRole();
  const roleOpts = [['owner', 'Dueño'], ['accountant', 'Contador'], ['manager', 'Gerente']];
  const themeOpts = [
    ['light',  '☀ Claro',   'Siempre claro, sin importar el sistema'],
    ['dark',   '☾ Oscuro',  'Siempre oscuro, sin importar el sistema'],
    ['system', '⊙ Sistema', 'Sigue la preferencia de su computador — cambia solo si usted la cambia allá'],
  ];
  pop.innerHTML = `
    <div class="lbl">Ver portal como (rol)</div>
    <div class="role-list">
      ${roleOpts.map(([k, l]) => `<div class="role-row${curRole === k ? ' active' : ''}" onclick="pickPreviewRole('${k}', event)"><span>${l}</span>${curRole === k ? '<span class="check">✓</span>' : ''}</div>`).join('')}
    </div>
    <div class="popover-divider"></div>
    <div class="lbl">Apariencia</div>
    <div class="opts">
      ${themeOpts.map(([k, l, hint]) => `<div class="opt${curTheme === k ? ' active' : ''}" onclick="pickTheme('${k}', event)" title="${hint}">${l}</div>`).join('')}
    </div>`;
}

function toggleLang() {
  const cur = currentLang();
  const next = cur === 'es' ? 'en' : 'es';
  sessionStorage.setItem('contabia_lang', next);
  location.reload();
}
function signOut(ev) {
  ev.preventDefault();
  ['contabia_auth','contabia_role','contabia_entity','contabia_demo',
   'contabia_live','contabia_api_token','contabia_user','contabia_chat_session']
    .forEach(k => sessionStorage.removeItem(k));
  location.href = 'login.html';
}

/* ------------------------------------------------------------
   Auto-inject + mobile hamburger
   ------------------------------------------------------------ */
document.addEventListener('DOMContentLoaded', () => {
  const go = () => mountShell();
  if (typeof isLiveMode === 'function' && isLiveMode() && typeof fetchAndCacheLiveSummary === 'function') {
    fetchAndCacheLiveSummary().then(go).catch(go);
  } else {
    go();
  }
});

function mountShell() {
  const sidebarMount = document.getElementById('sidebar-mount');
  const topbarMount  = document.getElementById('topbar-mount');
  if (!sidebarMount) return;

  /* normalize pretty URLs (Cloudflare Pages strips .html) — always
     compare against the canonical xxx.html form */
  let page = window.location.pathname.split('/').pop() || 'index.html';
  if (page && !page.includes('.')) page += '.html';

  /* manager-only enforcement: redirect off pages they shouldn't see */
  const role = currentRole();
  if (role === 'manager') {
    const allowedHrefs = NAV_MODEL.flatMap(s => s.items)
      .filter(i => i.roles.includes('manager'))
      .map(i => i.href);
    const loginPages = ['login.html', 'login-contador.html', 'login-gerente.html'];
    if (!allowedHrefs.includes(page) && !loginPages.includes(page)) {
      location.replace('nomina.html');
      return;
    }
  }

  sidebarMount.innerHTML = renderSidebar(page);
  if (topbarMount) topbarMount.innerHTML = renderDemoBanner() + renderTopbar();
  renderAppearancePopover();
  attachNavHoverListeners();

  if (typeof mountHelpPanel === 'function') mountHelpPanel();
  if (typeof mountAgentWidget === 'function') mountAgentWidget(page);

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

  /* close entity dropdown / appearance popover on outside click */
  document.addEventListener('click', (ev) => {
    closeEntityDropdown();
    const pop = document.getElementById('appearance-popover');
    if (pop && pop.classList.contains('open') && !pop.contains(ev.target) && !ev.target.closest('.user-chip')) {
      closeAppearancePopover();
    }
  });
}
