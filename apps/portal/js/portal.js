/* ============================================================
   ContabIA Portal — portal.js
   Shared utilities, navigation, mock data
   ============================================================ */

/* ---- Active nav highlighting ---- */
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname.split('/').pop();
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href') || '';
    if (href === path || (path === '' && href === 'index.html')) {
      item.classList.add('active');
    }
  });
});

/* ---- Detail panel (exception / JE slide-in) ---- */
function openPanel(id) {
  const overlay = document.getElementById(id);
  if (overlay) overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closePanel(id) {
  const overlay = document.getElementById(id);
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}
// Close on backdrop click
document.addEventListener('click', e => {
  if (e.target.classList.contains('detail-overlay')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});

/* ---- Filter chips ---- */
function initFilterChips(containerSelector, callback) {
  const chips = document.querySelectorAll(containerSelector + ' .filter-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      if (callback) callback(chip.dataset.filter);
    });
  });
}

/* ---- Tabs ---- */
function initTabs(tabsSelector, panelsSelector) {
  const tabs   = document.querySelectorAll(tabsSelector);
  const panels = document.querySelectorAll(panelsSelector);
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.style.display = 'none');
      tab.classList.add('active');
      if (panels[i]) panels[i].style.display = 'block';
    });
  });
}

/* ---- Format COP ---- */
function fmtCOP(amount, showSign = false) {
  const abs = Math.abs(amount);
  const formatted = abs.toLocaleString('es-CO');
  const sign = amount < 0 ? '−' : (showSign && amount > 0 ? '+' : '');
  return `${sign}COP ${formatted}`;
}

/* ---- Format date (DD/MM/YYYY) ---- */
function fmtDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

/* ---- Confidence bar HTML ---- */
function confidenceBar(score) {
  const pct = Math.round(score * 100);
  const cls = pct >= 85 ? 'high-conf' : pct >= 65 ? 'med-conf' : 'low-conf';
  return `
    <div class="confidence-bar">
      <div class="confidence-track">
        <div class="confidence-fill ${cls}" style="width:${pct}%"></div>
      </div>
      <span class="confidence-pct">${pct}%</span>
    </div>`;
}

/* ---- Badge HTML ---- */
function priorityBadge(p) {
  return `<span class="badge badge-${p}">${p.toUpperCase()}</span>`;
}
function statusBadge(s) {
  const labels = {
    pending:   'Pendiente',
    in_review: 'En revisión',
    approved:  'Aprobado',
    rejected:  'Rechazado',
    posted:    'Registrado',
    blocked:   'Bloqueado',
    needs_info:'Necesita info',
    overridden:'Modificado',
  };
  return `<span class="badge badge-${s}">${labels[s] || s}</span>`;
}

/* ---- Mock data ---- */
const MOCK = {
  client: {
    id: 'cantamar-001',
    name: 'Cantamar Beach Hostel',
    nit: '901.528.910-5',
    period: 'Marzo 2026',
    accountant: 'Angel Morales',
    owner: 'Kevin Carey',
    accounting_system: 'Alegra',
    pms: 'LobbyPMS',
  },

  closeSummary: {
    period: '2026-03',
    total_exceptions: 14,
    open_critical: 2,
    open_high: 5,
    open_medium: 4,
    open_low: 3,
    total_jes: 18,
    jes_pending: 7,
    jes_approved: 8,
    jes_posted: 3,
    estimated_tax_recovery: 1_248_500,
    close_ready: false,
    blocking_items: ['exc-001', 'exc-004'],
  },

  exceptions: [
    {
      id: 'exc-001',
      type: 'exception',
      subtype: 'tax.retefuente_missed',
      status: 'pending',
      priority: 'critical',
      title: 'Retefuente no aplicada — Seguridad Privada XYZ',
      description: 'Pago de COP 800.000 a proveedor de servicios de vigilancia sin aplicar retención en la fuente correspondiente (4%). Exposición fiscal: COP 32.000.',
      ai_recommendation: 'Registrar pasivo por retefuente pendiente de COP 32.000. Notificar al cliente para corrección en próximo pago.',
      ai_confidence: 0.96,
      created_at: '2026-04-01',
      payload: { vendor: 'Seguridad Privada XYZ', payment_amount: 800000, rate: 0.04, missed: 32000 }
    },
    {
      id: 'exc-002',
      type: 'exception',
      subtype: 'revenue.pms_alegra_gap',
      status: 'in_review',
      priority: 'critical',
      title: 'Reserva Booking sin factura — Laura Martínez',
      description: 'Reserva en LobbyPMS (checkout 28/03/2026) de COP 620.000 sin factura correspondiente en Alegra.',
      ai_recommendation: 'Generar factura de venta en Alegra por COP 620.000 (canal: Booking.com, Modelo Factura Mensual). Verificar comisión accrual pendiente.',
      ai_confidence: 0.91,
      created_at: '2026-04-01',
      payload: { guest: 'Laura Martínez', amount: 620000, channel: 'booking_com', checkin: '2026-03-25', checkout: '2026-03-28' }
    },
    {
      id: 'exc-003',
      type: 'exception',
      subtype: 'receipt.recoverable_candidate',
      status: 'pending',
      priority: 'high',
      title: 'Documento soporte pendiente — Ferretería El Tornillo',
      description: 'Compra a proveedor no obligado a facturar (COP 215.000). IVA recuperable de COP 34.412 no reclamado. El motor puede generar el documento soporte.',
      ai_recommendation: 'Generar documento soporte electrónico. IVA recuperable: COP 34.412. Impacto fiscal si no se recupera: ~COP 75.250.',
      ai_confidence: 0.88,
      created_at: '2026-04-02',
      payload: { vendor: 'Ferretería El Tornillo', nit: '901234567-1', amount: 215000, iva_recoverable: 34412 }
    },
    {
      id: 'exc-004',
      type: 'exception',
      subtype: 'bank_rec.unmatched_credit',
      status: 'pending',
      priority: 'critical',
      title: 'Crédito bancario sin identificar — COP 1.450.000',
      description: 'Crédito en cuenta Bancolombia el 15/03/2026 de COP 1.450.000. Descripción: "TRANSF MÓVIL". Sin contrapartida en Alegra.',
      ai_recommendation: 'No se pudo identificar automáticamente. Requiere revisión manual. Posible: anticipo de reserva grupal, pago Airbnb no registrado, o transferencia personal del propietario.',
      ai_confidence: 0.38,
      created_at: '2026-04-01',
      payload: { bank: 'Bancolombia', date: '2026-03-15', amount: 1450000, description: 'TRANSF MÓVIL' }
    },
    {
      id: 'exc-005',
      type: 'exception',
      subtype: 'revenue.phantom_commission_delta',
      status: 'pending',
      priority: 'high',
      title: 'Gross-up requerido — Hostelworld (Modelo Phantom)',
      description: 'Hostelworld retuvo comisión de COP 250.000 del depósito. Ingreso registrado: COP 1.250.000 (neto). Debe registrarse: COP 1.500.000 (bruto) + gasto comisión.',
      ai_recommendation: 'Registrar ingreso bruto COP 1.500.000 + comisión OTA COP 250.000 (con documento soporte — Hostelworld es entidad extranjera). Ver JE-007.',
      ai_confidence: 0.94,
      created_at: '2026-04-01',
      payload: { channel: 'hostelworld', gross: 1500000, commission: 250000, net_recorded: 1250000 }
    },
    {
      id: 'exc-006',
      type: 'exception',
      subtype: 'bank_rec.unmatched_debit',
      status: 'in_review',
      priority: 'high',
      title: 'Débito sin contabilizar — Servicios Públicos',
      description: 'Pago ACH el 18/03/2026 de COP 87.500. Descripción: "PAGO SERV PUBLICOS ACH". Sin entrada contable en Alegra.',
      ai_recommendation: 'Cuenta sugerida: 5215 (Servicios Públicos). Confianza: 71%. Revisar transacciones similares: febrero/2026 COP 82.000 → Servicios Públicos.',
      ai_confidence: 0.71,
      created_at: '2026-04-02',
      payload: { bank: 'Bancolombia', date: '2026-03-18', amount: 87500, suggested_account: '5215', suggested_category: 'Servicios Públicos' }
    },
    {
      id: 'exc-007',
      type: 'exception',
      subtype: 'payroll.provision_drift',
      status: 'pending',
      priority: 'high',
      title: 'Drift de cesantías — COP 280.000',
      description: 'Suma de provisiones individuales de cesantías difiere del saldo contable en Alegra en COP 280.000 (por encima del umbral de COP 100.000).',
      ai_recommendation: 'Revisar empleado Yaritza González — posible error de divisor en cálculo de marzo (31 días vs. 30 estatutario). Ver JE-prestaciones.',
      ai_confidence: 0.82,
      created_at: '2026-04-03',
      payload: { concept: 'cesantias', motor_total: 4820000, alegra_balance: 5100000, drift: -280000 }
    },
    {
      id: 'exc-008',
      type: 'exception',
      subtype: 'receipt.ocr_low_confidence',
      status: 'needs_info',
      priority: 'medium',
      title: 'OCR con baja confianza — NIT proveedor',
      description: 'Factura de COP 340.000. NIT extraído con confianza del 61% (umbral: 75%). Total y fecha OK. Se requiere confirmación del NIT.',
      ai_recommendation: 'Confirmar NIT del proveedor. Valor extraído: 890.123.456-7 (puede ser 890.123.456-1).',
      ai_confidence: 0.61,
      created_at: '2026-04-02',
      payload: { amount: 340000, extracted_nit: '890.123.456-7', confidence_nit: 0.61 }
    },
  ],

  journalEntries: [
    {
      id: 'je-001',
      type: 'journal_entry',
      subtype: 'je.gmf_trueup',
      status: 'pending',
      priority: 'medium',
      title: 'Ajuste GMF — Marzo 2026',
      description: 'Ajuste mensual del Gravamen a los Movimientos Financieros. Calculado sobre movimientos totales del mes.',
      ai_confidence: 0.99,
      created_at: '2026-04-01',
      lines: [
        { account: '5115', name: 'Gravamen Movimientos Financieros', debit: 48200, credit: null, desc: 'GMF marzo 2026' },
        { account: '2365', name: 'GMF por Pagar',                   debit: null, credit: 48200, desc: 'GMF marzo 2026' },
      ]
    },
    {
      id: 'je-002',
      type: 'journal_entry',
      subtype: 'je.ota_accrual.monthly_invoice',
      status: 'approved',
      priority: 'high',
      title: 'Accrual comisión Booking.com — Marzo 2026',
      description: 'Accrual de comisión Booking.com (Modelo Factura Mensual). Comisión devengada en el mes de estadía, factura llegará en abril.',
      ai_confidence: 0.97,
      created_at: '2026-04-01',
      lines: [
        { account: '5305', name: 'Comisiones OTA — Rooms',         debit: 892000, credit: null,   desc: 'Comisión Booking.com marzo 2026' },
        { account: '2805', name: 'Comisiones OTA por Pagar',       debit: null,   credit: 892000, desc: 'Comisión Booking.com marzo 2026' },
      ]
    },
    {
      id: 'je-003',
      type: 'journal_entry',
      subtype: 'je.prestaciones_trueup',
      status: 'pending',
      priority: 'high',
      title: 'True-up cesantías — Marzo 2026',
      description: 'Ajuste provisión cesantías. Divisor corregido a 30 (Art. 134 CST). Corrección de COP 280.000 drift detectado por motor.',
      ai_confidence: 0.89,
      created_at: '2026-04-03',
      lines: [
        { account: '5210', name: 'Gasto Cesantías',          debit: 280000, credit: null,   desc: 'Corrección drift cesantías marzo 2026' },
        { account: '2610', name: 'Provisión Cesantías',      debit: null,   credit: 280000, desc: 'Corrección drift cesantías marzo 2026' },
      ]
    },
    {
      id: 'je-004',
      type: 'journal_entry',
      subtype: 'je.ica_accrual',
      status: 'pending',
      priority: 'medium',
      title: 'Accrual ICA — Marzo 2026',
      description: 'Accrual mensual impuesto ICA (Santa Marta). Tarifa: 5.5 x 1000. Base: ingresos brutos del mes.',
      ai_confidence: 0.95,
      created_at: '2026-04-01',
      lines: [
        { account: '5410', name: 'Impuesto de Industria y Comercio', debit: 412500, credit: null,   desc: 'ICA accrual marzo 2026' },
        { account: '2404', name: 'ICA por Pagar',                    debit: null,   credit: 412500, desc: 'ICA accrual marzo 2026' },
      ]
    },
    {
      id: 'je-005',
      type: 'journal_entry',
      subtype: 'je.ota_grossup.phantom_commission',
      status: 'blocked',
      priority: 'high',
      title: 'Gross-up Hostelworld — Modelo Phantom',
      description: 'Bloqueado: requiere resolución de EXC-005 (phantom commission delta) primero.',
      ai_confidence: 0.94,
      created_at: '2026-04-01',
      blocked_by: 'exc-005',
      lines: [
        { account: '4105', name: 'Ingresos Habitaciones — OTA',  debit: null,   credit: 250000, desc: 'Gross-up ingreso bruto Hostelworld' },
        { account: '5305', name: 'Comisiones OTA — Rooms',       debit: 250000, credit: null,   desc: 'Comisión Hostelworld (documento soporte requerido)' },
      ]
    },
  ],

  months: [
    { month: 'Enero 2026',    status: 'closed',   modules: { bank_feed: 'ok', categorization: 'ok', reconciliation: 'ok', reports: 'ok' } },
    { month: 'Febrero 2026',  status: 'closed',   modules: { bank_feed: 'ok', categorization: 'ok', reconciliation: 'ok', reports: 'ok' } },
    { month: 'Marzo 2026',    status: 'in_progress', modules: { bank_feed: 'ok', categorization: 'ok', reconciliation: 'warn', reports: 'pending' }, open: 7, critical: 2 },
    { month: 'Abril 2026',    status: 'pending',  modules: {} },
  ],

  deliverables: [
    { name: 'Libro de Cierre — Marzo 2026',         type: 'xlsx', size: '284 KB', period: 'Marzo 2026', ready: true },
    { name: 'Resumen P&L USALI — Marzo 2026',       type: 'pdf',  size: '1.2 MB', period: 'Marzo 2026', ready: true },
    { name: 'Conciliación Bancaria — Marzo 2026',   type: 'xlsx', size: '96 KB',  period: 'Marzo 2026', ready: false },
    { name: 'Resumen Tributario — Marzo 2026',      type: 'pdf',  size: '410 KB', period: 'Marzo 2026', ready: false },
    { name: 'Libro de Cierre — Febrero 2026',       type: 'xlsx', size: '271 KB', period: 'Febrero 2026', ready: true },
    { name: 'Resumen P&L USALI — Febrero 2026',     type: 'pdf',  size: '1.1 MB', period: 'Febrero 2026', ready: true },
    { name: 'Conciliación Bancaria — Febrero 2026', type: 'xlsx', size: '88 KB',  period: 'Febrero 2026', ready: true },
    { name: 'Resumen Tributario — Febrero 2026',    type: 'pdf',  size: '395 KB', period: 'Febrero 2026', ready: true },
  ],
};
