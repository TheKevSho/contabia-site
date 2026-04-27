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
    /* legacy/default — actual user is now resolved per (entity, role) via USERS table below */
    id: 'user-kc',
    name: 'Kevin Carey',
    initials: 'KC',
    email: 'kevin@cantamar.co',
    default_entity: 'cantamar-001',
    default_role: 'owner',
    /* which entities the OWNER user has access to (entity dropdown filter) */
    roles: {
      'cantamar-001': 'owner',
      'sonata-001':   'owner',
    },
  },

  /* per-(entity, role) user identity. Drives the nav user chip. */
  users: {
    'cantamar-001': {
      owner:      { name: 'Kevin Carey',      initials: 'KC', email: 'kevin@cantamar.co'   },
      accountant: { name: 'Edwin Restrepo',   initials: 'ER', email: 'edwin@balinessa.co'  },
      manager:    { name: 'Yaritza González', initials: 'YG', email: 'yaritza@cantamar.co' },
    },
    'sonata-001': {
      owner:      { name: 'Kevin Carey',      initials: 'KC', email: 'kevin@cantamar.co'        },
      accountant: { name: 'Edwin Restrepo',   initials: 'ER', email: 'edwin@balinessa.co'       },
      manager:    { name: 'Nicolás Giraldo',  initials: 'NG', email: 'nick@tayronasailing.co'   },
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

    /* ---- BÓVEDA — input/upload store. Inverse of Entregables. ---- */
    boveda: [
      { id:'b-1',  filename:'Bancolombia_extracto_marzo_2026.pdf',     folder:'Banco',                type:'pdf',  size:'380 KB', uploaded_by:'agent',   uploaded_at:'2026-04-04 06:12', tags:['banco','cierre'],     processed:true,  linked_to:'JE-05 (concil. bancaria)' },
      { id:'b-2',  filename:'Bancolombia_extracto_febrero_2026.pdf',   folder:'Banco',                type:'pdf',  size:'372 KB', uploaded_by:'agent',   uploaded_at:'2026-03-04 06:00', tags:['banco','cierre'],     processed:true,  linked_to:'Cierre febrero' },
      { id:'b-3',  filename:'ferreteria_el_tornillo_28032026.jpg',     folder:'Recibos',              type:'img',  size:'212 KB', uploaded_by:'whatsapp',uploaded_at:'2026-03-28 14:22', tags:['compras'],            processed:true,  linked_to:'EXC-003' },
      { id:'b-4',  filename:'aws_invoice_marzo_2026.pdf',              folder:'Recibos',              type:'pdf',  size:'48 KB',  uploaded_by:'email',   uploaded_at:'2026-04-01 09:05', tags:['compras','exterior'],processed:false, linked_to:null },
      { id:'b-5',  filename:'taxi_marina_15032026.jpg',                folder:'Recibos',              type:'img',  size:'180 KB', uploaded_by:'whatsapp',uploaded_at:'2026-03-15 18:40', tags:['compras'],            processed:true,  linked_to:null },
      { id:'b-6',  filename:'transportes_sp_factura_22mar2026.pdf',    folder:'Facturas Proveedores', type:'pdf',  size:'92 KB',  uploaded_by:'agent',   uploaded_at:'2026-03-22 11:15', tags:['compras','retefuente'], processed:true, linked_to:'EXC-001' },
      { id:'b-7',  filename:'booking_statement_marzo_2026.xlsx',       folder:'OTAs',                 type:'xls',  size:'140 KB', uploaded_by:'agent',   uploaded_at:'2026-04-02 08:30', tags:['ingresos'],           processed:true,  linked_to:'JE-02' },
      { id:'b-8',  filename:'airbnb_payouts_marzo.pdf',                folder:'OTAs',                 type:'pdf',  size:'88 KB',  uploaded_by:'agent',   uploaded_at:'2026-04-02 08:32', tags:['ingresos'],           processed:true,  linked_to:null },
      { id:'b-9',  filename:'F300_2024_2025.pdf',                      folder:'Onboarding',           type:'pdf',  size:'420 KB', uploaded_by:'kevin',   uploaded_at:'2026-01-15 16:00', tags:['onboarding'],         processed:true,  linked_to:'Posición fiscal base' },
      { id:'b-10', filename:'retefuente_2025.pdf',                     folder:'Onboarding',           type:'pdf',  size:'310 KB', uploaded_by:'kevin',   uploaded_at:'2026-01-15 16:02', tags:['onboarding'],         processed:true,  linked_to:'Posición fiscal base' },
      { id:'b-11', filename:'contrato_arriendo_local.pdf',             folder:'Otros',                type:'pdf',  size:'520 KB', uploaded_by:'kevin',   uploaded_at:'2026-02-01 10:00', tags:[],                     processed:false, linked_to:null },
    ],

    /* ---- NÓMINA ---- */
    nomina: {
      payroll_summary: {
        period: '2da quincena marzo 2026',
        total_nomina:    4218500,
        parafiscales:     169000,
        prestaciones:     782300,
        total_provision: 5169800,
        employee_count: 11,
        due_date: '30 mar',
        status: 'pending_approval',
      },
      employees: [
        { id:'e-1',  name:'Yaritza González', position:'Gerente',         salary_base:1800000, days:30, ot_h:0, recargo_h:0, total:1800000 },
        { id:'e-2',  name:'Carlos Pérez',     position:'Recepcionista',   salary_base:1200000, days:30, ot_h:6, recargo_h:8, total:1320500 },
        { id:'e-3',  name:'María López',      position:'Recepcionista',   salary_base:1200000, days:30, ot_h:0, recargo_h:0, total:1200000 },
        { id:'e-4',  name:'Diana Ramírez',    position:'Housekeeping',    salary_base:1170000, days:30, ot_h:2, recargo_h:0, total:1188400 },
        { id:'e-5',  name:'Sandra Velasco',   position:'Housekeeping',    salary_base:1170000, days:30, ot_h:0, recargo_h:0, total:1170000 },
        { id:'e-6',  name:'Laura Mejía',      position:'Housekeeping',    salary_base:1170000, days:28, ot_h:0, recargo_h:0, total:1092000 },
        { id:'e-7',  name:'Pedro Suárez',     position:'Mantenimiento',   salary_base:1300000, days:30, ot_h:4, recargo_h:0, total:1336500 },
        { id:'e-8',  name:'José Castro',      position:'Mantenimiento',   salary_base:1300000, days:30, ot_h:0, recargo_h:0, total:1300000 },
        { id:'e-9',  name:'Ana Torres',       position:'Cocina',          salary_base:1200000, days:30, ot_h:3, recargo_h:6, total:1295500 },
        { id:'e-10', name:'Camilo Vargas',    position:'Bartender',       salary_base:1200000, days:30, ot_h:5, recargo_h:10,total:1373800 },
        { id:'e-11', name:'Luisa Mendoza',    position:'Recepcionista',   salary_base:1200000, days:30, ot_h:2, recargo_h:0, total:1218300 },
      ],
      ot_pending: [
        { id:'ot-1', employee:'Carlos Pérez',   date:'2026-03-22', hours:3, recargo:'Nocturno', reason:'Cobertura noche sábado',          status:'pending' },
        { id:'ot-2', employee:'Camilo Vargas',  date:'2026-03-23', hours:2, recargo:'Dominical', reason:'Brunch domingo grupo grande',     status:'pending' },
        { id:'ot-3', employee:'Ana Torres',     date:'2026-03-29', hours:4, recargo:'Festivo',   reason:'Servicio especial Semana Santa', status:'pending' },
      ],
      ops_kpis: {
        ocupacion_avg:    71,
        productividad:    82,
        rotacion_30d:      0,
        horas_marcadas: 1680,
        horas_extras:     32,
      },
      recent_marcaciones: [
        { employee:'Yaritza González', date:'2026-03-30', in:'07:50', out:'17:05', hours:9.25 },
        { employee:'Carlos Pérez',     date:'2026-03-30', in:'14:00', out:'23:10', hours:9.17 },
        { employee:'Diana Ramírez',    date:'2026-03-30', in:'06:55', out:'15:00', hours:8.08 },
        { employee:'Camilo Vargas',    date:'2026-03-30', in:'17:00', out:'02:15', hours:9.25, dispute:'Marcación de salida revisada por Yari' },
        { employee:'Ana Torres',       date:'2026-03-30', in:'11:00', out:'21:00', hours:10.00 },
      ],
    },

    /* ---- TRIBUTARIO ---- */
    tributario: {
      filings: [
        { id:'f300-mar', form:'F300', name:'IVA bimestral', period:'Mar–Abr 2026', due:'15 may',
          status:'draft', total: 412300,
          lines: [
            { row:'IVA generado por ventas',     amount: 1254600 },
            { row:'IVA descontable (compras)',   amount: -842300 },
            { row:'Saldo a pagar',               amount:  412300, total:true },
          ] },
        { id:'f350-mar', form:'F350', name:'Retefuente', period:'Marzo 2026', due:'11 abr',
          status:'ready', total: 284500,
          lines: [
            { row:'Honorarios (10%)',  amount: 184500 },
            { row:'Servicios (4%)',    amount:  64000 },
            { row:'Compras (2.5%)',    amount:  36000 },
            { row:'Total a pagar',     amount: 284500, total:true },
          ] },
        { id:'ica-mar', form:'ICA',  name:'Industria y Comercio · Santa Marta', period:'Marzo 2026', due:'15 abr',
          status:'draft', total: 412500,
          lines: [
            { row:'Base gravable (ingresos brutos)', amount: 75000000 },
            { row:'Tarifa 5,5 × 1.000',              amount:   412500, total:true },
          ] },
      ],
    },

    /* ---- AUDIT LOG ---- */
    audit_log: [
      { ts:'2026-04-04 06:12', source:'Bancolombia', type:'bank_pull',  desc:'147 transacciones de marzo extraídas', hash:'a3f7c92d', user:'agent' },
      { ts:'2026-04-04 06:10', source:'Alegra',      type:'fe_check',   desc:'87 facturas verificadas vs DIAN',      hash:'b1e2f08a', user:'agent' },
      { ts:'2026-04-04 06:08', source:'LobbyPMS',    type:'pms_pull',   desc:'89 reservas marzo · 5 canales OTA',    hash:'c9d4a17b', user:'agent' },
      { ts:'2026-04-04 06:05', source:'motor',       type:'rule_apply', desc:'OTA accrual rule R3 · 12 transacciones', hash:'d2e83ba1', user:'system' },
      { ts:'2026-04-04 06:00', source:'motor',       type:'reconcile',  desc:'3-way conciliación ejecutada',         hash:'f1a72c50', user:'system' },
      { ts:'2026-04-03 22:50', source:'WhatsApp',    type:'receipt',    desc:'Recibo Ferretería El Tornillo · OCR 88%', hash:'e7f12219', user:'manager' },
      { ts:'2026-04-03 18:20', source:'RADIAN',      type:'fe_inbound', desc:'12 facturas de proveedores recibidas', hash:'a8b32d11', user:'agent' },
      { ts:'2026-04-02 15:00', source:'motor',       type:'rule_change',desc:'Regla "TRANSPORTES SP → 5215" creada por Edwin', hash:'c3d9e4f2', user:'edwin' },
    ],

    /* ---- CONFIG ---- */
    config: {
      rules_client: [
        { id:'r-1', type:'category',  when:'Vendor = "TRANSPORTES SP"',           action:'Postear a 5215 (Transportes) + retención 4%', enabled:true,  hits_30d:4, author:'Edwin' },
        { id:'r-2', type:'category',  when:'Memo contiene "AWS" o "CLOUD"',       action:'Postear a 5135 (Servicios cloud) + DS automático', enabled:true,  hits_30d:6, author:'Edwin' },
        { id:'r-3', type:'treatment', when:'Booking.com factura mensual recibida', action:'Acreditar accrual 2805 · cargar gasto comisión', enabled:true,  hits_30d:1, author:'sistema' },
        { id:'r-4', type:'threshold', when:'JE > COP 3.000.000',                  action:'Requiere doble aprobación (Dueño + Contador)', enabled:false, hits_30d:0, author:'Edwin (borrador)' },
      ],
      team: [
        { id:'u-1', name:'Kevin Carey',      role:'Dueño',    email:'kevin@cantamar.co',   last_login:'hace 2h' },
        { id:'u-2', name:'Edwin Restrepo',   role:'Contador', email:'edwin@balinessa.co',  last_login:'ayer 18:00' },
        { id:'u-3', name:'Yaritza González', role:'Gerente',  email:'yaritza@cantamar.co', last_login:'hace 30 min' },
      ],
      notifications: [
        { event:'Excepción crítica creada',         email:true,  whatsapp:true,  recipients:'Dueño + Contador' },
        { event:'Cierre listo para revisión',       email:true,  whatsapp:true,  recipients:'Contador' },
        { event:'Pago de nómina por aprobar',       email:true,  whatsapp:true,  recipients:'Dueño' },
        { event:'Drift detectado en provisiones',   email:false, whatsapp:true,  recipients:'Contador' },
        { event:'Documento soporte generado',       email:false, whatsapp:false, recipients:'(silencioso)' },
      ],
    },
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

    /* ---- BÓVEDA ---- */
    boveda: [
      { id:'b-1',  filename:'BBVA_extracto_marzo_2026.pdf',           folder:'Banco',                type:'pdf', size:'420 KB', uploaded_by:'agent',   uploaded_at:'2026-04-04 05:55', tags:['banco','cierre'],       processed:true,  linked_to:'JE-05 (concil. BBVA)' },
      { id:'b-2',  filename:'Bancolombia_extracto_marzo_2026.pdf',    folder:'Banco',                type:'pdf', size:'298 KB', uploaded_by:'agent',   uploaded_at:'2026-04-04 05:56', tags:['banco','cierre'],       processed:true,  linked_to:'JE-05 (concil. Bancol.)' },
      { id:'b-3',  filename:'astilleros_caribe_15mar2026.pdf',        folder:'Facturas Proveedores', type:'pdf', size:'154 KB', uploaded_by:'agent',   uploaded_at:'2026-03-15 11:00', tags:['compras','retefuente'], processed:true,  linked_to:'EXC-104' },
      { id:'b-4',  filename:'combustible_marina_22mar2026.jpg',       folder:'Recibos',              type:'img', size:'240 KB', uploaded_by:'whatsapp',uploaded_at:'2026-03-22 14:30', tags:['compras'],              processed:true,  linked_to:null },
      { id:'b-5',  filename:'repuestos_motor_18mar2026.jpg',          folder:'Recibos',              type:'img', size:'195 KB', uploaded_by:'whatsapp',uploaded_at:'2026-03-18 09:45', tags:['compras'],              processed:false, linked_to:null },
      { id:'b-6',  filename:'civitatis_marzo_2026.xlsx',              folder:'OTAs',                 type:'xls', size:'112 KB', uploaded_by:'agent',   uploaded_at:'2026-04-02 09:00', tags:['ingresos'],             processed:true,  linked_to:null },
      { id:'b-7',  filename:'viator_marzo_2026.pdf',                  folder:'OTAs',                 type:'pdf', size:'76 KB',  uploaded_by:'agent',   uploaded_at:'2026-04-02 09:05', tags:['ingresos'],             processed:true,  linked_to:null },
      { id:'b-8',  filename:'getyourguide_PENDIENTE_2fa.txt',         folder:'OTAs',                 type:'pdf', size:'2 KB',   uploaded_by:'agent',   uploaded_at:'2026-04-04 05:05', tags:['ingresos','bloqueado'],processed:false, linked_to:'EXC-101' },
      { id:'b-9',  filename:'F300_2024_2025_sonata.pdf',              folder:'Onboarding',           type:'pdf', size:'380 KB', uploaded_by:'kevin',   uploaded_at:'2026-01-20 14:30', tags:['onboarding'],           processed:true,  linked_to:'Posición fiscal base' },
      { id:'b-10', filename:'certificado_navegacion_sonata.pdf',      folder:'Otros',                type:'pdf', size:'180 KB', uploaded_by:'nick',    uploaded_at:'2026-02-12 11:00', tags:['legal'],                processed:true,  linked_to:null },
    ],

    /* ---- NÓMINA ---- */
    nomina: {
      payroll_summary: {
        period: '2da quincena marzo 2026',
        total_nomina:    3620400,
        parafiscales:     145000,
        prestaciones:     668700,
        total_provision: 4434100,
        employee_count: 4,
        due_date: '30 mar',
        status: 'pending_approval',
      },
      employees: [
        { id:'e-1', name:'Nicolás Giraldo', position:'Operador / Capitán Sonata', salary_base:2200000, days:30, ot_h:0, recargo_h:0, total:2200000 },
        { id:'e-2', name:'Juan Camilo R.',  position:'Capitán Anna Lezah',        salary_base:1800000, days:30, ot_h:6, recargo_h:4, total:1898400 },
        { id:'e-3', name:'Andrés Mora',     position:'Marinero',                  salary_base:1170000, days:30, ot_h:8, recargo_h:0, total:1248000 },
        { id:'e-4', name:'Esteban Pinto',   position:'Marinero',                  salary_base:1170000, days:28, ot_h:4, recargo_h:0, total:1112000 },
      ],
      ot_pending: [
        { id:'ot-1', employee:'Juan Camilo R.', date:'2026-03-23', hours:4, recargo:'Dominical', reason:'Charter privado domingo', status:'pending' },
        { id:'ot-2', employee:'Andrés Mora',    date:'2026-03-29', hours:6, recargo:'Festivo',   reason:'Charter Semana Santa',   status:'pending' },
      ],
      ops_kpis: {
        utilizacion_flota:  64,
        productividad:      78,
        rotacion_30d:        0,
        horas_marcadas:    640,
        horas_extras:       28,
      },
      recent_marcaciones: [
        { employee:'Nicolás Giraldo', date:'2026-03-30', in:'06:30', out:'18:45', hours:12.25 },
        { employee:'Juan Camilo R.',  date:'2026-03-30', in:'06:45', out:'17:30', hours:10.75 },
        { employee:'Andrés Mora',     date:'2026-03-30', in:'06:45', out:'19:00', hours:12.25, dispute:'Marcación de salida después de retorno tardío' },
        { employee:'Esteban Pinto',   date:'2026-03-29', in:'07:00', out:'17:00', hours:10.00 },
      ],
    },

    /* ---- TRIBUTARIO ---- */
    tributario: {
      filings: [
        { id:'f300-mar', form:'F300', name:'IVA bimestral', period:'Mar–Abr 2026', due:'15 may',
          status:'draft', total: 198400,
          lines: [
            { row:'IVA generado por ventas',     amount:  810800 },
            { row:'IVA descontable (compras)',   amount: -612400 },
            { row:'Saldo a pagar',               amount:  198400, total:true },
          ] },
        { id:'f350-mar', form:'F350', name:'Retefuente', period:'Marzo 2026', due:'11 abr',
          status:'ready', total: 218400,
          lines: [
            { row:'Honorarios (10%)',  amount: 142000 },
            { row:'Servicios (4%)',    amount:  48400 },
            { row:'Compras (2.5%)',    amount:  28000 },
            { row:'Total a pagar',     amount: 218400, total:true },
          ] },
        { id:'ica-mar', form:'ICA',  name:'Industria y Comercio · Santa Marta', period:'Marzo 2026', due:'15 abr',
          status:'draft', total: 298300,
          lines: [
            { row:'Base gravable (ingresos brutos)', amount: 54200000 },
            { row:'Tarifa 5,5 × 1.000',              amount:   298300, total:true },
          ] },
      ],
    },

    /* ---- AUDIT LOG ---- */
    audit_log: [
      { ts:'2026-04-04 05:55', source:'BBVA',        type:'bank_pull',  desc:'94 transacciones de marzo extraídas', hash:'b8c4f217', user:'agent' },
      { ts:'2026-04-04 05:50', source:'Alegra',      type:'fe_check',   desc:'49 facturas verificadas vs DIAN',     hash:'a2d8e305', user:'agent' },
      { ts:'2026-04-04 05:42', source:'LobbyPMS',    type:'pms_pull',   desc:'51 charters marzo · 4 canales OTA',   hash:'c4f1b203', user:'agent' },
      { ts:'2026-04-04 05:30', source:'motor',       type:'depreciation', desc:'Depreciación 3 embarcaciones calculada (Sonata, Anna Lezah, Dragon Lady)', hash:'e9b2a17c', user:'system' },
      { ts:'2026-04-04 05:20', source:'motor',       type:'reconcile',  desc:'3-way conciliación ejecutada',        hash:'f3a91d5e', user:'system' },
      { ts:'2026-04-04 05:05', source:'GetYourGuide', type:'connector_fail', desc:'Portal GYG bloqueado por 2FA — comisión accrual estimada', hash:'d7b18e22', user:'agent' },
      { ts:'2026-04-03 21:10', source:'WhatsApp',    type:'receipt',    desc:'Recibo Combustibles Marina · OCR 92%', hash:'e0c4f917', user:'manager' },
      { ts:'2026-04-02 14:30', source:'motor',       type:'rule_change',desc:'Regla "ASTILLEROS DEL CARIBE → 5160 + retención 4%" creada por Edwin', hash:'a5d2e801', user:'edwin' },
    ],

    /* ---- CONFIG ---- */
    config: {
      rules_client: [
        { id:'r-1', type:'category',  when:'Vendor = "ASTILLEROS DEL CARIBE"',     action:'Postear a 5160 (Mantenimiento embarcaciones) + retención 4%', enabled:true,  hits_30d:2, author:'Edwin' },
        { id:'r-2', type:'category',  when:'Memo contiene "COMBUSTIBLE" o "MARINA"', action:'Postear a 5165 (Combustibles flota)', enabled:true,  hits_30d:5, author:'Edwin' },
        { id:'r-3', type:'treatment', when:'Charter cobrado vía Stonex',           action:'Reclasificar fee como gasto OTA + DS', enabled:true,  hits_30d:9, author:'sistema' },
        { id:'r-4', type:'threshold', when:'JE > COP 5.000.000',                   action:'Requiere doble aprobación (Dueño + Contador)', enabled:false, hits_30d:0, author:'Edwin (borrador)' },
      ],
      team: [
        { id:'u-1', name:'Kevin Carey',     role:'Dueño',    email:'kevin@cantamar.co',         last_login:'hace 3h' },
        { id:'u-2', name:'Edwin Restrepo',  role:'Contador', email:'edwin@balinessa.co',        last_login:'ayer 17:00' },
        { id:'u-3', name:'Nicolás Giraldo', role:'Gerente',  email:'nick@tayronasailing.co',    last_login:'hace 12 min' },
      ],
      notifications: [
        { event:'Excepción crítica creada',         email:true,  whatsapp:true,  recipients:'Dueño + Contador' },
        { event:'Cierre listo para revisión',       email:true,  whatsapp:true,  recipients:'Contador' },
        { event:'Pago de nómina por aprobar',       email:true,  whatsapp:true,  recipients:'Dueño' },
        { event:'Portal OTA inaccesible (2FA)',     email:true,  whatsapp:true,  recipients:'Dueño + Gerente' },
        { event:'Documento soporte generado',       email:false, whatsapp:false, recipients:'(silencioso)' },
      ],
    },
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
function currentUser() {
  const eid  = currentEntityId();
  const role = currentRole();
  return (DATA.users[eid] && DATA.users[eid][role])
      || { name: 'Usuario', initials: '?', email: '' };
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
