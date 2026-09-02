/* ============================================================
   ContabIA Portal — live-shell.js

   A live session (API token present, contabia_demo != 1) must
   NEVER render data.js. This file:
     - forces entity = sonata-001
     - hides cantamar-001 from the switcher
     - replaces nav badges / period chip from GET /summary
     - hides nav items that have no live payload
     - exposes honestStubHtml() for unwired pages
     - swaps currentUser() to the named login (kevin/edwin/nick)

   Load AFTER data.js + sonata-live.js and BEFORE nav.js.
   Demo / Scrooge is untouched — isLiveMode() is false there.
   ============================================================ */

window.RULE_HANDLED_IDS = new Set([
  'EX-J07-08','EX-J07-12','EX-J07-14','EX-5.5','EX-10.3','EX-12.3',
  'EX-12.7','EX-12.1','EX-9.4','EX-11.1',
]);

const LIVE_NAV_VISIBLE = {
  resumen: true,
  exceptions: true,
  'journal-entries': true,
  configuracion: true,
  tracker: true,
  boveda: true,
  chat: true,
  reconciliacion: false,
  nomina: false,
  tributario: false,
  deliverables: true,
  auditoria: false,
};

const LIVE_SONATA_META = {
  id: 'sonata-001',
  name: 'Tayrona Sailing',
  legal_name: 'SONATA MAS S.A.S. (Tayrona Sailing)',
  nit: '901.528.910-3',
  period: 'Julio 2026',
  period_iso: '2026-07',
  close_status: 'in_progress',
  accountant: 'Edwin Montenegro',
  owner: 'Kevin Carey',
  manager: 'Nicolás Giraldo',
  accounting_system: 'Alegra',
  pms: 'FareHarbor',
  bank_primary: 'Bancolombia',
  processed_at: 'en vivo',
};

window.__liveSummary = null;
window.__liveSummaryPromise = null;

function liveUserRecord() {
  try {
    const raw = sessionStorage.getItem('contabia_user');
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return null;
}

function initialsOf(name) {
  if (!name) return '?';
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map(p => p[0]).join('').toUpperCase();
}

function honestStubHtml(opts) {
  opts = opts || {};
  const title = opts.title || (typeof t === 'function' ? t('not_wired') : 'Aún no conectado');
  const copy = opts.copy || (typeof t === 'function' ? t('not_wired_copy') : 'Esta pantalla no tiene un endpoint en vivo. No se muestran cifras de demostración.');
  const wa = typeof t === 'function' ? t('wa_fwd') : 'Reenvíe documentos a su chat personal de ContabIA.';
  return `
    <div class="alert-banner">
      <div class="alert-text">
        <div class="icon">i</div>
        <div class="copy"><strong>${title}.</strong> ${copy}</div>
      </div>
    </div>
    <div class="panel" style="padding:22px;">
      <p style="margin:0 0 10px;color:var(--charcoal);font-size:14.5px;line-height:1.6;">${copy}</p>
      <p style="margin:0;color:var(--warm-gray);font-size:13px;">${wa}</p>
      <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;">
        <a class="btn btn-primary" href="exceptions.html">Excepciones</a>
        <a class="btn btn-secondary" href="journal-entries.html">Comprobantes</a>
        <a class="btn btn-secondary" href="index.html">Resumen</a>
      </div>
    </div>`;
}

function applyLiveHelpers() {
  if (typeof isLiveMode !== 'function' || !isLiveMode()) return;

  sessionStorage.setItem('contabia_entity', 'sonata-001');
  sessionStorage.removeItem('contabia_demo');

  window.currentEntityId = function () { return 'sonata-001'; };

  window.listEntitiesForUser = function () {
    return [{
      id: 'sonata-001',
      name: LIVE_SONATA_META.name,
      legal_name: LIVE_SONATA_META.legal_name,
      nit: LIVE_SONATA_META.nit,
      period: LIVE_SONATA_META.period,
      close_status: 'in_progress',
    }];
  };

  window.currentUser = function () {
    const rec = liveUserRecord();
    if (rec) {
      return {
        name: rec.name || rec.username || 'Usuario',
        initials: initialsOf(rec.name || rec.username),
        email: rec.email || '',
      };
    }
    return { name: 'Usuario', initials: '?', email: '' };
  };

  window.currentEntityData = function () {
    const s = window.__liveSummary || {};
    const meta = Object.assign({}, LIVE_SONATA_META, s.meta || {});
    const cifras = s.cifras || {};
    const live = cifras.live_period || {};
    const openLive = (live.open_high || 0) + (live.open_medium || 0) + (live.open_low || 0);
    const badges = s.nav_badges || { exceptions: openLive, jes: 0 };
    return {
      meta: meta,
      connectors: [
        { id: 'alegra', name: 'Alegra', status: 'ok', last_sync: 'julio 2026' },
        { id: 'fareharbor', name: 'FareHarbor', status: 'ok', last_sync: 'julio 2026' },
        { id: 'whatsapp', name: 'WhatsApp (ContabIA)', status: 'ok', last_sync: 'agent chat' },
      ],
      closeSummary: {
        period: '2026-07',
        pct: null,
        eta: null,
        ready: false,
        total_exceptions: live.total || cifras.total || 0,
        open_critical: 0,
        open_high: live.open_high || 0,
        open_medium: live.open_medium || 0,
        open_low: live.open_low || 0,
        total_jes: badges.jes || 0,
        jes_pending: badges.jes || 0,
        jes_approved: 0,
        jes_posted: 0,
        jes_blocked: 0,
        blocking_items: [],
        steps: [],
      },
      cifras: cifras,
      ingestion: s.ingestion || null,
      whatsapp: s.whatsapp || null,
      exceptions: [],
      journalEntries: [],
      months: [],
      deliverables: [],
      audit_log: [],
      boveda: [],
      nomina: null,
      tributario: null,
      tax_summary: [],
      ota_breakdown: [],
      three_way_rec: null,
      plata_en_riesgo_detalle: [],
      activity: [],
      action_queue: { owner: [], accountant: [], manager: [] },
      primary_cta: {
        owner: { text: 'Revisar excepciones', href: 'exceptions.html' },
        accountant: { text: 'Revisar comprobantes', href: 'journal-entries.html' },
        manager: { text: 'Abrir bóveda', href: 'boveda.html' },
      },
      config: { rules_client: [], team: [], notifications: [] },
      _live: true,
    };
  };

  window.navBadgeCounts = function () {
    const s = window.__liveSummary;
    if (s && s.nav_badges) return s.nav_badges;
    return { exceptions: 0, jes: 0 };
  };

  window.primaryCTA = function () {
    const role = (typeof currentRole === 'function' ? currentRole() : 'owner');
    return currentEntityData().primary_cta[role] || currentEntityData().primary_cta.owner;
  };

  window.actionQueue = function () { return []; };

  window.buildAgentIntroThread = function (e, user) {
    const first = (user && user.name ? user.name.split(' ')[0] : '');
    const live = (e && e.closeSummary) || {};
    const open = (live.open_high || 0) + (live.open_medium || 0) + (live.open_low || 0);
    const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
    if (lang === 'en') {
      return [{
        who: 'agent',
        text: `Hi${first ? ', ' + first : ''}. I'm the ContabIA agent for Tayrona Sailing. July 2026 is IN PROGRESS. ${open} July exceptions are still open. I will not invent figures. Forward documents to your personal ContabIA WhatsApp chat.`,
      }];
    }
    return [{
      who: 'agent',
      text: `Hola${first ? ', ' + first : ''}. Soy el agente ContabIA de Tayrona Sailing. Julio 2026 está EN CURSO. ${open} excepciones de julio siguen abiertas. No invento cifras. Reenvíe documentos a su chat personal de ContabIA en WhatsApp.`,
    }];
  };
}

function fetchAndCacheLiveSummary() {
  if (typeof isLiveMode !== 'function' || !isLiveMode()) return Promise.resolve(null);
  if (window.__liveSummaryPromise) return window.__liveSummaryPromise;
  if (typeof fetchLiveSummary !== 'function') return Promise.resolve(null);
  window.__liveSummaryPromise = fetchLiveSummary('sonata-001')
    .then(s => { window.__liveSummary = s; return s; })
    .catch(err => { console.error('live summary', err); return null; });
  return window.__liveSummaryPromise;
}

function liveNavFilter(model) {
  if (typeof isLiveMode !== 'function' || !isLiveMode()) return model;
  return model.map(sec => ({
    section: sec.section,
    items: sec.items.filter(i => LIVE_NAV_VISIBLE[i.id] !== false),
  })).filter(sec => sec.items.length);
}

applyLiveHelpers();

if (typeof isLiveMode === 'function' && isLiveMode()) {
  fetchAndCacheLiveSummary();
}
