/* ============================================================
   ContabIA Portal — data.js
   Mock data layer. Mirrors the eventual API shape so pages can
   be re-pointed at real endpoints without restructuring.

   Two entities:
     cantamar-001  Vamos Navegando S.A.S — hostel
     sonata-001    Sonata Mas S.A.S — Tayrona Sailing tour operator

   Helpers (global):
     currentEntityData()           full block for active entity
     listEntitiesForUser()         entities current user has access to
     roleAt(entityId)              user's role at given entity
     navBadgeCounts()              { exceptions, jes }
     primaryCTA()                  { text, href } based on role + state
   ============================================================ */

const DATA = {
  user: {
    id: 'user-kc',
    name: 'Kevin Carey',
    initials: 'KC',
    email: 'kevin@cantamar.co',
    /* role defaults; overridden by login landing → sessionStorage */
    default_entity: 'cantamar-001',
    default_role: 'owner',
    /* per-entity role mapping. one user, multiple NITs, one role per. */
    roles: {
      'cantamar-001': 'owner',
      'sonata-001':   'owner',
    },
  },

  /* shape returned by /entities */
  entities_meta: [
    { id: 'cantamar-001', name: 'Cantamar Beach Hostel', legal_name: 'Vamos Navegando S.A.S', nit: '901.138.128-0', period: 'Marzo 2026', close_status: 'in_progress' },
    { id: 'sonata-001',   name: 'Tayrona Sailing',       legal_name: 'Sonata Mas S.A.S',       nit: '901.528.910-1', period: 'Marzo 2026', close_status: 'in_progress' },
  ],

  entities: {

  /* ============================================================
     CANTAMAR BEACH HOSTEL (Vamos Navegando S.A.S)
     ============================================================ */
  'cantamar-001': {
    meta: {
      id: 'cantamar-001',
      name: 'Cantamar Beach Hostel',
      legal_name: 'Vamos Navegando S.A.S',
      nit: '901.138.128-0',
      period: 'Marzo 2026',
      period_iso: '2026-03',
      accountant: 'Edwin Restrepo',
      owner: 'Kevin Carey',
      manager: 'Yaritza González',
      accounting_system: 'Alegra',
      pms: 'LobbyPMS',
      bank_primary: 'Bancolombia',
      processed_at: 'hace 2h',
    },

    connectors: [
      { id: 'lobbypms', name: 'LobbyPMS',  status: 'ok',   last_sync: '6:12 a.m.' },
      { id: 'prometeo', name: 'Prometeo',  status: 'ok',   last_sync: '6:08 a.m.' },
      { id: 'alegra',   name: 'Alegra',    status: 'ok',   last_sync: '6:10 a.m.' },
      { id: 'radian',   name: 'RADIAN',    status: 'warn', last_sync: 'ayer 22:00' },
      { id: 'whatsapp', name: 'WhatsApp',  status: 'ok',   last_sync: '5 min' },
    ],

    closeSummary: {
      period: '2026-03',
      pct: 78,
      eta: '5 abr',
      ready: false,
      total_exceptions: 14,
      open_critical: 2, open_high: 5, open_medium: 4, open_low: 3,
      total_jes: 18, jes_pending: 5, jes_approved: 8, jes_posted: 3, jes_blocked: 2,
      blocking_items: ['exc-001', 'exc-004'],
      steps: [
        { name: 'Ingesta',         sub: 'Bancolombia + LobbyPMS', status: 'done' },
        { name: 'Categorización',  sub: '147 transacciones',      status: 'done' },
        { name: 'Reconciliación',  sub: '2 sin resolver',         status: 'review' },
        { name: 'Nómina',          sub: 'true-up pendiente',      status: 'review' },
        { name: 'Informes',        sub: 'bloqueado',              status: 'blocked' },
      ],
    },

    /* "Hacer ahora" / "Tu cola" — role-aware action queue.
       Owner sees urgency + approvals; accountant sees JE/exception queue. */
    action_queue: {
      owner: [
        { id: 'a-1', label: 'Crítico',    label_class: 'urgent', accent: 'urgent',
          title: 'Revisar 2 excepciones críticas',
          meta: 'EXC-001 · retefuente · COP 32K en riesgo<br>EXC-004 · OTA gross-up · Hostelworld',
          cta: 'Resolver →', href: 'exceptions.html' },
        { id: 'a-2', label: 'Por aprobar', label_class: '', accent: '',
          title: 'Aprobar nómina quincenal',
          amount: 'COP 4.218.500',
          meta: '11 empleados · vence 30 mar',
          cta: 'Revisar y aprobar →', href: 'nomina.html' },
        { id: 'a-3', label: 'Por aprobar', label_class: '', accent: 'routine',
          title: 'Aprobar pago IVA',
          amount: 'COP 842.300',
          meta: 'F300 listo · vence 11 abr',
          cta: 'Revisar y aprobar →', href: 'tributario.html' },
      ],
      accountant: [
        { id: 'a-1', label: 'En cola',    label_class: 'urgent', accent: 'urgent',
          title: 'Aprobar 5 comprobantes',
          meta: 'JE-001 GMF · JE-003 Cesantías · JE-004 ICA · +2',
          cta: 'Revisar JEs →', href: 'journal-entries.html' },
        { id: 'a-2', label: 'En cola',    label_class: '', accent: '',
          title: 'Resolver 7 excepciones',
          meta: '2 críticas · 5 altas',
          cta: 'Abrir cola →', href: 'exceptions.html' },
        { id: 'a-3', label: 'Pendiente',  label_class: '', accent: 'routine',
          title: 'Validar conciliación 3 vías',
          meta: 'COP 492.200 sin reconciliar',
          cta: 'Revisar →', href: 'reconciliacion.html' },
      ],
    },

    primary_cta: {
      owner:      { text: 'Revisar pendientes (7)',     href: 'exceptions.html' },
      accountant: { text: 'Aprobar 5 comprobantes',     href: 'journal-entries.html' },
      manager:    { text: 'Aprobar 3 horas extras',     href: 'nomina.html' },
    },

    /* Cifras del mes — three big tiles */
    cifras: {
      plata_en_riesgo: {
        total: 1428500,
        breakdown: [
          { label: 'Documento soporte faltante (3)', value: 912300 },
          { label: 'Retefuente no aplicada (2)',     value: 284500 },
          { label: 'IVA no reclamado',               value: 231700 },
        ],
      },
      recuperacion: {
        total: 1248500,
        breakdown: [
          { label: 'Crédito fiscal IVA',     value: '+842.300' },
          { label: 'Retefuente recibida',    value: '+156.200' },
          { label: 'DS generados',           value: '+250.000' },
        ],
      },
      kpi_usali: {
        primary_value: 42, primary_unit: '%',
        primary_label: 'Operación · GOP%',
        breakdown: [
          { label: 'Ocupación', value: '71%' },
          { label: 'ADR',       value: '128.400' },
          { label: 'RevPAR',    value: '91.200' },
        ],
      },
    },

    tax_summary: [
      { name: 'IVA — Crédito fiscal',         desc: 'Saldo recuperable estimado',     amount: '+842.300', amount_class: 'pos', status: 'computing', status_label: 'En cálculo' },
      { name: 'Retefuente retenida',          desc: 'Como agente retenedor',          amount: '−284.500', amount_class: 'neg', status: 'calc',      status_label: 'Calculado' },
      { name: 'Retefuente recibida',          desc: 'Activo tributario',              amount: '+156.200', amount_class: 'pos', status: 'calc',      status_label: 'Calculado' },
      { name: 'ICA Santa Marta',              desc: '5,5 × 1.000',                    amount: '−412.500', amount_class: 'neg', status: 'review',    status_label: 'Por aprobar' },
      { name: 'GMF',                          desc: '4 × 1.000 sobre movimientos',    amount: '−48.200',  amount_class: 'neg', status: 'review',    status_label: 'Por aprobar' },
      { name: 'Retefuente perdida (alerta)',  desc: 'EXC-001 · corrección requerida', amount: '−32.000',  amount_class: 'neg', status: 'crit',      status_label: 'Crítico' },
    ],

    /* OTA breakdown — rooms-focused, hospitality OTAs */
    ota_breakdown: [
      { code: 'B', cls: 'b-booking',     name: 'Booking.com',    model: 'Monthly invoice · 15%',     reservas: 42, commission: -1224500 },
      { code: 'A', cls: 'b-airbnb',      name: 'Airbnb',         model: 'Pass-through · gross-up',   reservas: 18, commission: -384200  },
      { code: 'H', cls: 'b-hostelworld', name: 'Hostelworld',    model: 'Phantom · gross-up',        reservas: 15, commission: -285500  },
      { code: 'D', cls: 'b-despegar',    name: 'Despegar',       model: 'Doméstica · IVA recup.',    reservas:  9, commission: -168900  },
      { code: 'G', cls: 'b-gyg',         name: 'GetYourGuide',   model: 'Tours · vía Stonex',        reservas:  6, commission: -92300   },
      { code: 'C', cls: 'b-civitatis',   name: 'Civitatis',      model: 'Tours',                     reservas:  4, commission: -54100   },
      { code: 'V', cls: 'b-viator',      name: 'Viator',         model: 'Tours',                     reservas:  3, commission: -42800   },
    ],

    three_way_rec: {
      legs: [
        { label: 'PMS',        value: 38420500, source: 'LobbyPMS · 89 reservas' },
        { label: 'FE Emitida', value: 38420500, source: '87 facturas · 2 pendientes' },
        { label: 'Banco',      value: 37928300, source: 'Bancolombia · 6 sin match' },
      ],
      arrows: ['ok', 'warn'],
      variance: 492200,
      status: 'has-variance',
      message: '⚠ Variance · COP 492.200 sin reconciliar',
      cta: 'Resolver →',
      /* drill-down ledger for /reconciliacion */
      ledger: [
        { res: 'RES-3018', guest: 'Laura M.',  channel: 'Booking',     pms: 620000, fe: 620000, bank: 620000, status: 'ok' },
        { res: 'RES-3019', guest: 'Pedro G.',  channel: 'Direct',      pms: 480000, fe: 480000, bank: 480000, status: 'ok' },
        { res: 'RES-3027', guest: 'Anna K.',   channel: 'Hostelworld', pms: 1500000, fe: 1500000, bank: 1250000, status: 'variance', note: 'Phantom commission gap COP 250K' },
        { res: 'RES-3033', guest: 'Diego R.',  channel: 'Airbnb',      pms: 384000, fe: 0,      bank: 384000, status: 'fe-missing', note: 'Falta FE' },
        { res: 'RES-3041', guest: 'Sara T.',   channel: 'Booking',     pms: 720000, fe: 720000, bank: 0,      status: 'bank-pending', note: 'Settlement abr' },
      ],
    },

    /* Bank reconciliation per account — for /reconciliacion */
    bank_recs: [
      { account: 'Bancolombia · 0123 4567 89',  type: 'Cuenta corriente',  bank_balance: 18420300, gl_balance: 18912500, variance: -492200, items: 6, status: 'has-variance' },
      { account: 'Bancolombia · 9876 5432 10',  type: 'Cuenta de ahorros', bank_balance:  3208000, gl_balance:  3208000, variance: 0,        items: 0, status: 'ok' },
    ],

    /* Plata en riesgo · detalle (item-level) */
    plata_en_riesgo_detalle: [
      { name: 'Booking.com — abril',           why: 'Documento soporte no generado para comisión COP 1.224.500',     amt: 232655, ct: 'deducción en riesgo' },
      { name: 'AWS · Servicios cloud',         why: '3 cargos USD sin documento soporte (USD 240 total)',            amt: 182400, ct: 'deducción en riesgo' },
      { name: 'Pago a "TRANSPORTES SP"',       why: 'COP 1.420.000 — debió retener 11% (10 UVT)',                    amt: 156200, ct: 'retefuente perdida' },
      { name: 'Ferretería El Tornillo',        why: 'IVA recuperable no reclamado por falta de DS',                  amt: 231700, ct: 'IVA no reclamado' },
    ],

    activity: [
      { time: 'hoy 6:12',   desc: 'Procesó <strong>147 transacciones bancarias</strong> de marzo. 6 requieren revisión manual.', pill: 'done',   pill_label: 'Completado' },
      { time: 'hoy 6:08',   desc: 'Cruce LobbyPMS × Alegra completado. <strong>2 reservas sin factura</strong> detectadas.',     pill: 'action', pill_label: 'Acción requerida' },
      { time: 'hoy 5:55',   desc: 'Cálculo de prestaciones sociales completado. <strong>Drift COP 280.000</strong> en cesantías detectado.', pill: 'action', pill_label: 'Acción requerida' },
      { time: 'hoy 5:32',   desc: '<strong>Retefuente perdida</strong> identificada en pago a TRANSPORTES SP por COP 1.420.000.', pill: 'crit',   pill_label: 'Crítico' },
      { time: 'ayer 23:40', desc: 'Ingesta de datos LobbyPMS (marzo 2026): <strong>89 reservas, 5 canales OTA</strong>.',        pill: 'done',   pill_label: 'Completado' },
    ],

    exceptions: [
      { id: 'exc-001', subtype: 'tax.retefuente_missed',           status: 'pending',   priority: 'critical',
        title: 'Retefuente no aplicada — Seguridad Privada XYZ',
        description: 'Pago de COP 800.000 a proveedor de servicios de vigilancia sin aplicar retención en la fuente correspondiente (4%). Exposición fiscal: COP 32.000.',
        ai_recommendation: 'Registrar pasivo por retefuente pendiente de COP 32.000. Notificar al cliente para corrección en próximo pago.',
        ai_confidence: 0.96, created_at: '2026-04-01' },
      { id: 'exc-002', subtype: 'revenue.pms_alegra_gap',          status: 'in_review', priority: 'critical',
        title: 'Reserva Booking sin factura — Laura Martínez',
        description: 'Reserva en LobbyPMS (checkout 28/03/2026) de COP 620.000 sin factura correspondiente en Alegra.',
        ai_recommendation: 'Generar factura de venta en Alegra por COP 620.000 (canal: Booking.com, Modelo Factura Mensual).',
        ai_confidence: 0.91, created_at: '2026-04-01' },
      { id: 'exc-003', subtype: 'receipt.recoverable_candidate',   status: 'pending',   priority: 'high',
        title: 'Documento soporte pendiente — Ferretería El Tornillo',
        description: 'Compra a proveedor no obligado a facturar (COP 215.000). IVA recuperable de COP 34.412 no reclamado.',
        ai_recommendation: 'Generar documento soporte electrónico. IVA recuperable: COP 34.412.',
        ai_confidence: 0.88, created_at: '2026-04-02' },
      { id: 'exc-004', subtype: 'bank_rec.unmatched_credit',       status: 'pending',   priority: 'critical',
        title: 'Crédito bancario sin identificar — COP 1.450.000',
        description: 'Crédito en cuenta Bancolombia el 15/03/2026 de COP 1.450.000. Descripción: "TRANSF MÓVIL". Sin contrapartida en Alegra.',
        ai_recommendation: 'No se pudo identificar automáticamente. Requiere revisión manual.',
        ai_confidence: 0.38, created_at: '2026-04-01' },
      { id: 'exc-005', subtype: 'revenue.phantom_commission_delta', status: 'pending',  priority: 'high',
        title: 'Gross-up requerido — Hostelworld (Modelo Phantom)',
        description: 'Hostelworld retuvo comisión de COP 250.000 del depósito. Ingreso registrado: COP 1.250.000 (neto). Debe registrarse: COP 1.500.000 (bruto) + gasto comisión.',
        ai_recommendation: 'Registrar ingreso bruto COP 1.500.000 + comisión OTA COP 250.000 (con DS).',
        ai_confidence: 0.94, created_at: '2026-04-01' },
      { id: 'exc-006', subtype: 'bank_rec.unmatched_debit',         status: 'in_review', priority: 'high',
        title: 'Débito sin contabilizar — Servicios Públicos',
        description: 'Pago ACH el 18/03/2026 de COP 87.500. Descripción: "PAGO SERV PUBLICOS ACH". Sin entrada contable.',
        ai_recommendation: 'Cuenta sugerida: 5215 (Servicios Públicos). Confianza: 71%.',
        ai_confidence: 0.71, created_at: '2026-04-02' },
      { id: 'exc-007', subtype: 'payroll.provision_drift',          status: 'pending',   priority: 'high',
        title: 'Drift de cesantías — COP 280.000',
        description: 'Suma de provisiones de cesantías difiere del saldo en Alegra en COP 280.000.',
        ai_recommendation: 'Revisar empleado Yaritza González — posible error de divisor en cálculo de marzo (31 vs. 30 días).',
        ai_confidence: 0.82, created_at: '2026-04-03' },
    ],

    journalEntries: [
      { id: 'je-001', subtype: 'je.gmf_trueup',         status: 'pending',  priority: 'medium',
        title: 'Ajuste GMF — Marzo 2026',
        description: 'Ajuste mensual del Gravamen a los Movimientos Financieros.',
        ai_confidence: 0.99, created_at: '2026-04-01',
        lines: [
          { account: '5115', name: 'Gravamen Movimientos Financieros', debit: 48200, credit: null },
          { account: '2365', name: 'GMF por Pagar',                    debit: null,  credit: 48200 },
        ]},
      { id: 'je-002', subtype: 'je.ota_accrual.monthly_invoice', status: 'approved', priority: 'high',
        title: 'Accrual comisión Booking.com — Marzo 2026',
        description: 'Accrual de comisión Booking.com (Modelo Factura Mensual).',
        ai_confidence: 0.97, created_at: '2026-04-01',
        lines: [
          { account: '5305', name: 'Comisiones OTA — Rooms',     debit: 892000, credit: null   },
          { account: '2805', name: 'Comisiones OTA por Pagar',   debit: null,   credit: 892000 },
        ]},
      { id: 'je-003', subtype: 'je.prestaciones_trueup', status: 'pending',  priority: 'high',
        title: 'True-up cesantías — Marzo 2026',
        description: 'Ajuste provisión cesantías. Divisor corregido a 30 (Art. 134 CST).',
        ai_confidence: 0.89, created_at: '2026-04-03',
        lines: [
          { account: '5210', name: 'Gasto Cesantías',     debit: 280000, credit: null   },
          { account: '2610', name: 'Provisión Cesantías', debit: null,   credit: 280000 },
        ]},
      { id: 'je-004', subtype: 'je.ica_accrual',         status: 'pending',  priority: 'medium',
        title: 'Accrual ICA — Marzo 2026',
        description: 'Tarifa: 5.5 × 1000. Base: ingresos brutos del mes.',
        ai_confidence: 0.95, created_at: '2026-04-01',
        lines: [
          { account: '5410', name: 'Impuesto de Industria y Comercio', debit: 412500, credit: null   },
          { account: '2404', name: 'ICA por Pagar',                    debit: null,   credit: 412500 },
        ]},
      { id: 'je-005', subtype: 'je.ota_grossup.phantom_commission', status: 'blocked', priority: 'high',
        title: 'Gross-up Hostelworld — Modelo Phantom',
        description: 'Bloqueado: requiere resolución de EXC-005 primero.',
        ai_confidence: 0.94, created_at: '2026-04-01', blocked_by: 'exc-005',
        lines: [
          { account: '4105', name: 'Ingresos Habitaciones — OTA', debit: null,   credit: 250000 },
          { account: '5305', name: 'Comisiones OTA — Rooms',      debit: 250000, credit: null   },
        ]},
    ],

    months: [
      { month: 'Enero 2026',   status: 'closed',      modules: { bank_feed: 'ok', categorization: 'ok', reconciliation: 'ok',   reports: 'ok' } },
      { month: 'Febrero 2026', status: 'closed',      modules: { bank_feed: 'ok', categorization: 'ok', reconciliation: 'ok',   reports: 'ok' } },
      { month: 'Marzo 2026',   status: 'in_progress', modules: { bank_feed: 'ok', categorization: 'ok', reconciliation: 'warn', reports: 'pending' }, open: 7, critical: 2 },
      { month: 'Abril 2026',   status: 'pending',     modules: {} },
    ],

    deliverables: [
      { name: 'Libro de Cierre — Marzo 2026',         type: 'xlsx', size: '284 KB', period: 'Marzo 2026',   ready: true,  source: 'cierre' },
      { name: 'Resumen P&L USALI — Marzo 2026',       type: 'pdf',  size: '1.2 MB', period: 'Marzo 2026',   ready: true,  source: 'cierre' },
      { name: 'Conciliación Bancaria — Marzo 2026',   type: 'xlsx', size: '96 KB',  period: 'Marzo 2026',   ready: false, source: 'cierre' },
      { name: 'Resumen Tributario — Marzo 2026',      type: 'pdf',  size: '410 KB', period: 'Marzo 2026',   ready: false, source: 'cierre' },
      { name: 'Libro de Cierre — Febrero 2026',       type: 'xlsx', size: '271 KB', period: 'Febrero 2026', ready: true,  source: 'cierre' },
      { name: 'Resumen P&L USALI — Febrero 2026',     type: 'pdf',  size: '1.1 MB', period: 'Febrero 2026', ready: true,  source: 'cierre' },
      { name: 'Conciliación Bancaria — Febrero 2026', type: 'xlsx', size: '88 KB',  period: 'Febrero 2026', ready: true,  source: 'cierre' },
      { name: 'Resumen Tributario — Febrero 2026',    type: 'pdf',  size: '395 KB', period: 'Febrero 2026', ready: true,  source: 'cierre' },
      /* Free-scan artifact — first thing in their archive when they convert */
      { name: 'Escaneo gratuito — abril 2026',         type: 'pdf',  size: '120 KB', period: 'Abril 2026',   ready: true,  source: 'free_scan',
        note: 'Detección inicial de documento soporte faltante en compras al exterior.',
        path: '../../contabia public site/free-scan/escaneo_vamos_navegando_sas_20260404.pdf' },
    ],
  },

  /* ============================================================
     TAYRONA SAILING (Sonata Mas S.A.S)
     Tour-operator structure: vessels, charters, GYG/Civitatis/Viator,
     BBVA primary, vessel utilization KPI. Numbers in normal-business range.
     ============================================================ */
  'sonata-001': {
    meta: {
      id: 'sonata-001',
      name: 'Tayrona Sailing',
      legal_name: 'Sonata Mas S.A.S',
      nit: '901.528.910-1',
      period: 'Marzo 2026',
      period_iso: '2026-03',
      accountant: 'Edwin Restrepo',
      owner: 'Kevin Carey',
      manager: 'Nicolás Giraldo',
      accounting_system: 'Alegra',
      pms: 'LobbyPMS',
      bank_primary: 'BBVA',
      processed_at: 'hace 3h',
    },

    connectors: [
      { id: 'lobbypms', name: 'LobbyPMS',  status: 'ok',   last_sync: '5:42 a.m.' },
      { id: 'prometeo', name: 'Prometeo',  status: 'warn', last_sync: 'ayer 18:00' },
      { id: 'alegra',   name: 'Alegra',    status: 'ok',   last_sync: '5:55 a.m.' },
      { id: 'radian',   name: 'RADIAN',    status: 'ok',   last_sync: '3 h' },
      { id: 'whatsapp', name: 'WhatsApp',  status: 'ok',   last_sync: '12 min' },
    ],

    closeSummary: {
      period: '2026-03',
      pct: 64,
      eta: '7 abr',
      ready: false,
      total_exceptions: 9,
      open_critical: 1, open_high: 4, open_medium: 3, open_low: 1,
      total_jes: 14, jes_pending: 6, jes_approved: 5, jes_posted: 2, jes_blocked: 1,
      blocking_items: ['exc-101'],
      steps: [
        { name: 'Ingesta',         sub: 'BBVA · pendiente',       status: 'review' },
        { name: 'Categorización',  sub: '94 transacciones',       status: 'done' },
        { name: 'Reconciliación',  sub: '3 sin resolver',         status: 'review' },
        { name: 'Nómina',          sub: '4 empleados',            status: 'done' },
        { name: 'Informes',        sub: 'pendiente',              status: 'pending' },
      ],
    },

    action_queue: {
      owner: [
        { id: 'a-1', label: 'Crítico',    label_class: 'urgent', accent: 'urgent',
          title: 'Verificar portal GetYourGuide',
          meta: 'Comisión marzo sin confirmar · 2FA bloqueado',
          cta: 'Verificar →', href: 'reconciliacion.html' },
        { id: 'a-2', label: 'Por aprobar', label_class: '', accent: '',
          title: 'Aprobar nómina quincenal',
          amount: 'COP 3.620.400',
          meta: '4 empleados · vence 30 mar',
          cta: 'Revisar y aprobar →', href: 'nomina.html' },
        { id: 'a-3', label: 'Por aprobar', label_class: '', accent: 'routine',
          title: 'Aprobar pago IVA',
          amount: 'COP 612.800',
          meta: 'F300 listo · vence 11 abr',
          cta: 'Revisar y aprobar →', href: 'tributario.html' },
      ],
      accountant: [
        { id: 'a-1', label: 'En cola',    label_class: 'urgent', accent: 'urgent',
          title: 'Aprobar 6 comprobantes',
          meta: 'JE-101 GMF · JE-103 Depreciación vesselos · +4',
          cta: 'Revisar JEs →', href: 'journal-entries.html' },
        { id: 'a-2', label: 'En cola',    label_class: '', accent: '',
          title: 'Resolver 5 excepciones',
          meta: '1 crítica · 4 altas',
          cta: 'Abrir cola →', href: 'exceptions.html' },
        { id: 'a-3', label: 'Pendiente',  label_class: '', accent: 'routine',
          title: 'Validar P&L por embarcación',
          meta: 'Sonata, Anna Lezah, Dragon Lady',
          cta: 'Revisar →', href: 'tributario.html' },
      ],
    },

    primary_cta: {
      owner:      { text: 'Verificar GYG · 1 crítico',  href: 'exceptions.html' },
      accountant: { text: 'Aprobar 6 comprobantes',     href: 'journal-entries.html' },
      manager:    { text: 'Revisar bitácora 4 charters', href: 'nomina.html' },
    },

    cifras: {
      plata_en_riesgo: {
        total: 824700,
        breakdown: [
          { label: 'Documento soporte faltante (4)', value: 512400 },
          { label: 'Retefuente no aplicada (1)',     value: 184500 },
          { label: 'IVA no reclamado',               value: 127800 },
        ],
      },
      recuperacion: {
        total: 698200,
        breakdown: [
          { label: 'Crédito fiscal IVA',     value: '+412.800' },
          { label: 'Retefuente recibida',    value: '+85.400'  },
          { label: 'DS generados',           value: '+200.000' },
        ],
      },
      kpi_usali: {
        primary_value: 38, primary_unit: '%',
        primary_label: 'Operación · GOP%',
        breakdown: [
          { label: 'Utilización flota',       value: '64%' },
          { label: 'ADR / charter',           value: '1.420.000' },
          { label: 'RevPAV',                  value: '892.000' },
        ],
      },
    },

    tax_summary: [
      { name: 'IVA — Crédito fiscal',         desc: 'Saldo recuperable estimado',     amount: '+612.800', amount_class: 'pos', status: 'computing', status_label: 'En cálculo' },
      { name: 'Retefuente retenida',          desc: 'Como agente retenedor',          amount: '−218.400', amount_class: 'neg', status: 'calc',      status_label: 'Calculado' },
      { name: 'Retefuente recibida',          desc: 'Activo tributario',              amount: '+85.400',  amount_class: 'pos', status: 'calc',      status_label: 'Calculado' },
      { name: 'ICA Santa Marta',              desc: '5,5 × 1.000',                    amount: '−298.300', amount_class: 'neg', status: 'review',    status_label: 'Por aprobar' },
      { name: 'GMF',                          desc: '4 × 1.000 sobre movimientos',    amount: '−39.500',  amount_class: 'neg', status: 'review',    status_label: 'Por aprobar' },
    ],

    /* OTAs — tour operator mix, no Booking/Airbnb/Hostelworld */
    ota_breakdown: [
      { code: 'G', cls: 'b-gyg',         name: 'GetYourGuide',  model: 'Tours · 25%',               reservas: 18, commission: -892400 },
      { code: 'C', cls: 'b-civitatis',   name: 'Civitatis',     model: 'Tours · 22%',               reservas: 11, commission: -428000 },
      { code: 'V', cls: 'b-viator',      name: 'Viator',        model: 'Tours · 20%',               reservas:  8, commission: -312500 },
      { code: 'D', cls: 'b-despegar',    name: 'Despegar',      model: 'Tours doméstica',           reservas:  5, commission: -148200 },
      { code: '·', cls: 'b-direct',      name: 'Directo',       model: 'WhatsApp · web',            reservas:  9, commission: 0       },
    ],

    three_way_rec: {
      legs: [
        { label: 'PMS',        value: 28640500, source: 'LobbyPMS · 51 charters' },
        { label: 'FE Emitida', value: 28420500, source: '49 facturas · 2 pendientes' },
        { label: 'Banco',      value: 28114800, source: 'BBVA · 3 sin match' },
      ],
      arrows: ['warn', 'warn'],
      variance: 525700,
      status: 'has-variance',
      message: '⚠ Variance · COP 525.700 sin reconciliar',
      cta: 'Resolver →',
      ledger: [
        { res: 'CHR-2104', guest: 'Sailing Crew GYG',  channel: 'GetYourGuide', pms: 1420000, fe: 1420000, bank: 1065000, status: 'variance',     note: 'GYG comisión 25% retenida' },
        { res: 'CHR-2108', guest: 'Familia Pérez',     channel: 'Direct',       pms: 1620000, fe: 1620000, bank: 1620000, status: 'ok' },
        { res: 'CHR-2112', guest: 'Civitatis Group',   channel: 'Civitatis',    pms: 1280000, fe: 1280000, bank: 998000,  status: 'variance',     note: 'Civitatis comisión 22%' },
        { res: 'CHR-2117', guest: 'Marco V.',          channel: 'Viator',       pms: 920000,  fe: 0,       bank: 736000,  status: 'fe-missing',   note: 'Falta FE' },
        { res: 'CHR-2120', guest: 'Sara T.',           channel: 'GetYourGuide', pms: 1840000, fe: 1840000, bank: 0,       status: 'bank-pending', note: 'Settlement abr' },
      ],
    },

    bank_recs: [
      { account: 'BBVA · 0011 2233 44',         type: 'Cuenta corriente',  bank_balance: 14820000, gl_balance: 15345700, variance: -525700, items: 3, status: 'has-variance' },
      { account: 'Bancolombia · 5544 3322 11',  type: 'Cuenta de ahorros', bank_balance:  4180000, gl_balance:  4180000, variance: 0,        items: 0, status: 'ok' },
    ],

    plata_en_riesgo_detalle: [
      { name: 'GetYourGuide — marzo',          why: 'Documento soporte no generado para comisión COP 892.400',     amt: 169500, ct: 'deducción en riesgo' },
      { name: 'Stonex · procesador exterior',  why: '5 fees USD sin DS (USD 180 total)',                            amt: 137200, ct: 'deducción en riesgo' },
      { name: 'Pago a "ASTILLEROS DEL CARIBE"', why: 'COP 980.000 mantenimiento Sonata — debió retener 11%',        amt: 107800, ct: 'retefuente perdida' },
      { name: 'Combustibles Marina',           why: 'IVA recuperable no reclamado por falta de DS',                 amt: 127800, ct: 'IVA no reclamado' },
    ],

    activity: [
      { time: 'hoy 5:55',   desc: 'Procesó <strong>94 transacciones bancarias</strong> de marzo. 3 requieren revisión manual.', pill: 'done',   pill_label: 'Completado' },
      { time: 'hoy 5:42',   desc: 'Cruce LobbyPMS × Alegra completado. <strong>2 charters sin factura</strong> detectados.',     pill: 'action', pill_label: 'Acción requerida' },
      { time: 'hoy 5:20',   desc: 'Depreciación calculada para <strong>3 embarcaciones</strong> (Sonata, Anna Lezah, Dragon Lady).', pill: 'done', pill_label: 'Completado' },
      { time: 'hoy 5:05',   desc: '<strong>Portal GetYourGuide</strong> sin acceso (2FA). Comisión sin confirmar.',             pill: 'crit',   pill_label: 'Crítico' },
      { time: 'ayer 22:50', desc: 'Ingesta de datos LobbyPMS (marzo 2026): <strong>51 charters, 4 canales OTA</strong>.',        pill: 'done',   pill_label: 'Completado' },
    ],

    exceptions: [
      { id: 'exc-101', subtype: 'connector.ota_portal_locked',     status: 'pending', priority: 'critical',
        title: 'Portal GetYourGuide bloqueado por 2FA',
        description: 'Sin acceso al portal de GetYourGuide para confirmar comisión de marzo (COP 892.400). 2FA bloqueado.',
        ai_recommendation: 'Coordinar con Nick para resetear 2FA. Mientras tanto, comisión queda en accrual estimado.',
        ai_confidence: 0.99, created_at: '2026-04-01' },
      { id: 'exc-102', subtype: 'revenue.pms_alegra_gap',          status: 'pending', priority: 'high',
        title: 'Charter Viator sin factura — Marco V.',
        description: 'Charter en LobbyPMS (CHR-2117, salida 22/03/2026) de COP 920.000 sin FE en Alegra.',
        ai_recommendation: 'Generar factura de venta en Alegra por COP 920.000 (canal: Viator).',
        ai_confidence: 0.93, created_at: '2026-04-02' },
      { id: 'exc-103', subtype: 'fixed_asset.capitalization_flag', status: 'in_review', priority: 'high',
        title: 'Dragon Lady — capitalización pendiente',
        description: 'Vessel "Dragon Lady" usado para charters pero no aparece en registro de activos fijos.',
        ai_recommendation: 'Verificar con Edwin cómo capitalizar (compra conjunta Kev/Nick).',
        ai_confidence: 0.78, created_at: '2026-04-02' },
      { id: 'exc-104', subtype: 'tax.retefuente_missed',           status: 'pending', priority: 'high',
        title: 'Retefuente no aplicada — Astilleros del Caribe',
        description: 'Pago de COP 980.000 a astillero por mantenimiento Sonata sin retención (11%).',
        ai_recommendation: 'Registrar pasivo retefuente COP 107.800.',
        ai_confidence: 0.94, created_at: '2026-04-02' },
      { id: 'exc-105', subtype: 'bank_rec.unmatched_credit',       status: 'pending', priority: 'high',
        title: 'Crédito BBVA sin identificar — COP 720.000',
        description: 'Crédito en BBVA el 14/03/2026. Descripción: "ABONO CHARTER MARZ". Sin contrapartida.',
        ai_recommendation: 'Posible anticipo de charter grupal. Cruzar con bookings de marzo sin pago.',
        ai_confidence: 0.52, created_at: '2026-04-01' },
    ],

    journalEntries: [
      { id: 'je-101', subtype: 'je.gmf_trueup',           status: 'pending',  priority: 'medium',
        title: 'Ajuste GMF — Marzo 2026',
        description: 'Ajuste mensual del Gravamen a los Movimientos Financieros.',
        ai_confidence: 0.99, created_at: '2026-04-01',
        lines: [
          { account: '5115', name: 'Gravamen Movimientos Financieros', debit: 39500, credit: null  },
          { account: '2365', name: 'GMF por Pagar',                    debit: null,  credit: 39500 },
        ]},
      { id: 'je-102', subtype: 'je.ota_accrual.gyg',      status: 'pending',  priority: 'high',
        title: 'Accrual comisión GetYourGuide — Marzo 2026',
        description: 'Comisión GYG estimada (portal sin acceso).',
        ai_confidence: 0.78, created_at: '2026-04-01',
        lines: [
          { account: '5305', name: 'Comisiones OTA — Tours',     debit: 892400, credit: null   },
          { account: '2805', name: 'Comisiones OTA por Pagar',   debit: null,   credit: 892400 },
        ]},
      { id: 'je-103', subtype: 'je.depreciation.vessels', status: 'pending',  priority: 'high',
        title: 'Depreciación embarcaciones — Marzo 2026',
        description: 'Sonata + Anna Lezah (50%). Dragon Lady excluida (ver EXC-103).',
        ai_confidence: 0.96, created_at: '2026-04-01',
        lines: [
          { account: '5160', name: 'Depreciación Flota',         debit: 1240000, credit: null    },
          { account: '1592', name: 'Depreciación Acumulada',     debit: null,    credit: 1240000 },
        ]},
      { id: 'je-104', subtype: 'je.ica_accrual',          status: 'pending',  priority: 'medium',
        title: 'Accrual ICA — Marzo 2026',
        description: 'Tarifa: 5.5 × 1000.',
        ai_confidence: 0.95, created_at: '2026-04-01',
        lines: [
          { account: '5410', name: 'Impuesto de Industria y Comercio', debit: 298300, credit: null   },
          { account: '2404', name: 'ICA por Pagar',                    debit: null,   credit: 298300 },
        ]},
      { id: 'je-105', subtype: 'je.fixed_asset.flag',     status: 'blocked',  priority: 'high',
        title: 'Capitalización Dragon Lady',
        description: 'Bloqueado: requiere resolución de EXC-103.',
        ai_confidence: 0.62, created_at: '2026-04-02', blocked_by: 'exc-103',
        lines: [] },
    ],

    months: [
      { month: 'Enero 2026',   status: 'closed',      modules: { bank_feed: 'ok',  categorization: 'ok',   reconciliation: 'ok',   reports: 'ok' } },
      { month: 'Febrero 2026', status: 'closed',      modules: { bank_feed: 'ok',  categorization: 'ok',   reconciliation: 'ok',   reports: 'ok' } },
      { month: 'Marzo 2026',   status: 'in_progress', modules: { bank_feed: 'warn', categorization: 'ok', reconciliation: 'warn', reports: 'pending' }, open: 5, critical: 1 },
      { month: 'Abril 2026',   status: 'pending',     modules: {} },
    ],

    deliverables: [
      { name: 'Libro de Cierre — Marzo 2026',           type: 'xlsx', size: '218 KB', period: 'Marzo 2026',   ready: false, source: 'cierre' },
      { name: 'P&L por Embarcación — Marzo 2026',       type: 'pdf',  size: '0.9 MB', period: 'Marzo 2026',   ready: false, source: 'cierre' },
      { name: 'Conciliación Bancaria — Marzo 2026',     type: 'xlsx', size: '74 KB',  period: 'Marzo 2026',   ready: false, source: 'cierre' },
      { name: 'Libro de Cierre — Febrero 2026',         type: 'xlsx', size: '208 KB', period: 'Febrero 2026', ready: true,  source: 'cierre' },
      { name: 'P&L por Embarcación — Febrero 2026',     type: 'pdf',  size: '0.8 MB', period: 'Febrero 2026', ready: true,  source: 'cierre' },
      { name: 'Conciliación Bancaria — Febrero 2026',   type: 'xlsx', size: '69 KB',  period: 'Febrero 2026', ready: true,  source: 'cierre' },
      { name: 'Escaneo gratuito — abril 2026',          type: 'pdf',  size: '120 KB', period: 'Abril 2026',   ready: true,  source: 'free_scan',
        note: 'Detección inicial de documento soporte faltante en compras al exterior.',
        path: '../../contabia public site/free-scan/escaneo_sonata_mas_sas_20260404.pdf' },
    ],
  },

  }, /* end entities */
};

/* ============================================================
   HELPERS — global, called from page scripts
   ============================================================ */

function currentEntityId() {
  return sessionStorage.getItem('contabia_entity') || DATA.user.default_entity;
}
function currentRole() {
  return sessionStorage.getItem('contabia_role') || DATA.user.default_role;
}
function setEntity(id) {
  if (DATA.entities[id]) {
    sessionStorage.setItem('contabia_entity', id);
    location.reload();
  }
}
function setRole(role) {
  sessionStorage.setItem('contabia_role', role);
}
function currentEntityData() {
  return DATA.entities[currentEntityId()];
}
function listEntitiesForUser() {
  return DATA.entities_meta.filter(e => DATA.user.roles[e.id]);
}
function roleAt(entityId) {
  return DATA.user.roles[entityId] || 'owner';
}
function navBadgeCounts() {
  const e = currentEntityData();
  return {
    exceptions: e.closeSummary.total_exceptions - e.closeSummary.open_low,
    jes:        e.closeSummary.jes_pending,
  };
}
function primaryCTA() {
  const e = currentEntityData();
  return e.primary_cta[currentRole()] || null;
}
function actionQueue() {
  const e = currentEntityData();
  return e.action_queue[currentRole()] || e.action_queue.owner;
}

/* COP formatter — periods as thousands separators */
function fmtCOP(amount, opts = {}) {
  const { showSign = false, withCurrency = true } = opts;
  if (amount == null || isNaN(amount)) return '—';
  const abs = Math.abs(amount);
  const formatted = abs.toLocaleString('es-CO');
  const sign = amount < 0 ? '−' : (showSign && amount > 0 ? '+' : '');
  return withCurrency ? `${sign}COP ${formatted}` : `${sign}${formatted}`;
}
function fmtDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
