/* ============================================================
   ContabIA Portal — i18n.js
   ES/EN chrome for live pages. Data stays as stored.
   Toggle in the topbar writes contabia_lang and reloads.
   ============================================================ */

const I18N = {
  es: {
    nav: {
      Principal: 'Principal',
      Revisión: 'Revisión',
      Resultados: 'Resultados',
      Sistema: 'Sistema',
      resumen: 'Resumen',
      chat: 'Chat con el Agente',
      tracker: 'Seguimiento de Cierre',
      exceptions: 'Excepciones',
      'journal-entries': 'Comprobantes (JEs)',
      reconciliacion: 'Reconciliación',
      nomina: 'Nómina',
      tributario: 'Tributario',
      boveda: 'Bóveda',
      deliverables: 'Entregables',
      auditoria: 'Auditoría',
      configuracion: 'Configuración',
    },
    role: { owner: 'Dueño', accountant: 'Contador', manager: 'Gerente', internal: 'ContabIA' },
    entity_active: 'Entidad activa',
    signout: 'Cerrar sesión',
    period_in_progress: 'EN CURSO',
    period_closed: 'CERRADO',
    period_review: 'EN REVISIÓN',
    live_data: 'Datos reales',
    baseline: 'Línea base',
    live_july: 'Julio (vivo)',
    handled_by_rule: 'Cubierta por regla',
    not_wired: 'Aún no conectado',
    not_wired_copy: 'Esta pantalla no tiene un endpoint en vivo. No se muestran cifras de demostración.',
    exceptions_col: 'Excepción',
    priority: 'Prioridad',
    status: 'Estado',
    created: 'Creada',
    all: 'Todas',
    high: 'Altas',
    medium: 'Medias',
    low: 'Bajas',
    open: 'Abiertas',
    closed: 'Cerradas',
    pending_edwin: 'Pendiente (Edwin)',
    ready: 'A · Listos (julio)',
    estimated: 'B · Estimados',
    disclose: 'C · Solo revelar',
    baseline_jes: 'Línea base ene–jun',
    wa_fwd: 'Reenvíe documentos a su chat personal con Hermes (el mismo número).',
    chat_placeholder: 'Pregúntele a su agente…',
    send: 'Enviar',
    refresh: '↻ Actualizar',
    connectors_ok: 'Todo conectado',
    connectors_warn_one: ' conector con aviso',
    connectors_warn_many: ' conectores con aviso',
  },
  en: {
    nav: {
      Principal: 'Home',
      Revisión: 'Review',
      Resultados: 'Results',
      Sistema: 'System',
      resumen: 'Overview',
      chat: 'Chat with the Agent',
      tracker: 'Close tracker',
      exceptions: 'Exceptions',
      'journal-entries': 'Journal entries',
      reconciliacion: 'Reconciliation',
      nomina: 'Payroll',
      tributario: 'Tax',
      boveda: 'Vault',
      deliverables: 'Deliverables',
      auditoria: 'Audit',
      configuracion: 'Settings',
    },
    role: { owner: 'Owner', accountant: 'Accountant', manager: 'Manager', internal: 'ContabIA' },
    entity_active: 'Active entity',
    signout: 'Sign out',
    period_in_progress: 'IN PROGRESS',
    period_closed: 'CLOSED',
    period_review: 'IN REVIEW',
    live_data: 'Live data',
    baseline: 'Baseline',
    live_july: 'July (live)',
    handled_by_rule: 'Covered by rule',
    not_wired: 'Not connected yet',
    not_wired_copy: 'This screen has no live endpoint. Demo figures are not shown.',
    exceptions_col: 'Exception',
    priority: 'Priority',
    status: 'Status',
    created: 'Created',
    all: 'All',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    open: 'Open',
    closed: 'Closed',
    pending_edwin: 'Pending (Edwin)',
    ready: 'A · Ready (July)',
    estimated: 'B · Estimated',
    disclose: 'C · Disclose only',
    baseline_jes: 'Jan–Jun baseline',
    wa_fwd: 'Forward documents to your personal Hermes self-chat (same number).',
    chat_placeholder: 'Ask your agent…',
    send: 'Send',
    refresh: '↻ Refresh',
    connectors_ok: 'All connected',
    connectors_warn_one: ' connector with a warning',
    connectors_warn_many: ' connectors with a warning',
  },
};

function t(key) {
  const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
  const pack = I18N[lang] || I18N.es;
  const parts = key.split('.');
  let cur = pack;
  for (const p of parts) {
    if (cur && typeof cur === 'object' && p in cur) cur = cur[p];
    else return (I18N.es[key] != null ? I18N.es[key] : key);
  }
  return cur;
}

function navLabel(id, fallback) {
  const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
  const pack = I18N[lang] || I18N.es;
  return (pack.nav && pack.nav[id]) || fallback;
}

function statusLabelI18n(s) {
  const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
  const es = {
    open: 'Abierta', closed: 'Cerrada', approved: 'Aprobada', rejected: 'Rechazada',
    pending: 'Pendiente', pending_edwin_approval: 'Pendiente (Edwin)',
    approved_by_edwin: 'Aprobado por Edwin', disclosure_only: 'Solo revelar',
    in_review: 'En revisión',
  };
  const en = {
    open: 'Open', closed: 'Closed', approved: 'Approved', rejected: 'Rejected',
    pending: 'Pending', pending_edwin_approval: 'Pending (Edwin)',
    approved_by_edwin: 'Approved by Edwin', disclosure_only: 'Disclose only',
    in_review: 'In review',
  };
  return (lang === 'en' ? en : es)[s] || s;
}

function priorityLabelI18n(p) {
  const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
  const map = {
    es: { high: 'ALTA', medium: 'MEDIA', low: 'BAJA', critical: 'CRÍTICA' },
    en: { high: 'HIGH', medium: 'MEDIUM', low: 'LOW', critical: 'CRITICAL' },
  };
  return (map[lang] || map.es)[p] || (p || '').toUpperCase();
}
