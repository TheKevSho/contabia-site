/* ============================================================
   ContabIA Portal — i18n.js
   ES/EN chrome for live pages. Data stays as stored.
   Toggle in the topbar writes contabia_lang and reloads.
   ============================================================ */

const I18N = {
  es: {
    /* nav chrome */
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
    /* roles */
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
    /* exceptions table */
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
    'common.all': 'Todas',
    'exc.demo.meta_pending': '{n} excepción{plural} en cola',
    'exc.demo.rejected_alert': 'Rechazo simulado — flujo de Angel pendiente.',
    'exc.demo.approved_alert': 'Aprobación simulada — motor procesa la corrección.',
    'exc.live_pill': 'Datos reales',
    'exc.nada_posteado': 'nada posteado aún',

    /* exception detail panel / buttons */
    'exc.status.pending': 'Pendiente',
    'exc.status.in_review': 'En revisión',
    'exc.status.approved': 'Aprobado',
    'exc.status.rejected': 'Rechazado',
    'exc.status.posted': 'Registrado',
    'exc.status.blocked': 'Bloqueado',
    'exc.status.needs_info': 'Necesita info',
    'exc.status.overridden': 'Modificado',
    'exc.live_status.open': 'Abierta',
    'exc.live_status.closed': 'Cerrada',
    'exc.live_status.approved': 'Aprobada',
    'exc.live_status.rejected': 'Rechazada',
    'exc.filter.criticas': 'Críticas',
    'exc.filter.altas': 'Altas',
    'exc.filter.medias': 'Medias',
    'exc.filter.pendientes': 'Pendientes',
    'exc.filter.en_revision': 'En revisión',
    'exc.filter.julio_vivo': 'Julio (vivo)',
    'exc.filter.linea_base': 'Línea base',
    'exc.filter.abiertas': 'Abiertas',
    'exc.filter.cerradas': 'Cerradas',
    'exc.filter.cubierta_regla': 'Cubierta por regla',
    'exc.panel.descripcion': 'Descripción',
    'exc.panel.recomendacion': 'Recomendación del agente',
    'exc.panel.cerrar': 'Cerrar',
    'exc.panel.rechazar': 'Rechazar',
    'exc.panel.aprobar_resolucion': 'Aprobar resolución',
    'exc.nothing_in_filter': 'Sin items en este filtro.',
    'exc.period_live': 'Julio (vivo)',
    'exc.period_baseline': 'Línea base',
    'exc.rule_tag': 'regla',
    'exc.loading': 'Cargando datos reales…',
    'exc.error_loading': 'Error cargando datos reales.',
    'exc.api_error': 'No se pudo conectar con la API real ({msg}). ¿Está corriendo apps/api en {base}?',
    'exc.block_close': '{n} excepción{plural} crítica{plural2} bloquean el cierre. Resolver antes de generar informes.',
    'exc.high_open': '{n} excepción{plural} de prioridad alta abiertas — línea base ene-jun + julio en vivo. {closed} ya cerradas.',
    'exc.prompt_rejection_note': 'Nota de rechazo (opcional):',
    'exc.save_error': 'No se pudo guardar: {msg}',
    'exc.table.exception': 'Excepción',
    'exc.table.priority': 'Prioridad',
    'exc.table.status': 'Estado',
    'exc.table.period': 'Periodo',
    'exc.table.owner': 'Responsable',

    /* journal-entries chrome */
    'je.filter.todos': 'Todos',
    'je.filter.pendientes': 'Pendientes',
    'je.filter.aprobados': 'Aprobados',
    'je.filter.bloqueados': 'Bloqueados',
    'je.filter.julio_vivo': 'Julio (vivo)',
    'je.filter.linea_base_ene': 'Línea base ene',
    'je.filter.pendientes_edwin': 'Pendientes (Edwin)',
    'je.filter.aprobados_edwin': 'Aprobados',
    'je.table.cuenta': 'Cuenta',
    'je.table.debito': 'Débito',
    'je.table.credito': 'Crédito',
    'je.table.total': 'Total',
    'je.status.pending': 'Pendiente',
    'je.status.approved': 'Aprobado',
    'je.status.rejected': 'Rechazado',
    'je.status.posted': 'Registrado',
    'je.status.blocked': 'Bloqueado',
    'je.status.pending_edwin': 'Pendiente (Edwin)',
    'je.status.approved_edwin': 'Aprobado por Edwin',
    'je.status.disclosure_only': 'Solo revelar',
    'je.nothing_in_filter': 'Sin comprobantes en este filtro.',
    'je.empty_lines': 'Sin líneas (bloqueado)',
    'je.empty_lines_live': 'Sin líneas — pendiente de estructurar',
    'je.blocked_by': 'Bloqueado por {blocker}. Resolver la excepción primero.',
    'je.approved_ready': '✓ Aprobado · listo para postear',
    'je.blocked_status': '⚠ Bloqueado',
    'je.reject_btn': 'Rechazar',
    'je.approve_btn': 'Aprobar',
    'je.rejected_tag': '✕ Rechazado',
    'je.approved_edwin_tag': '✓ Aprobado por Edwin · listo para postear',
    'je.disclosure_only_tag': 'ℹ Solo revelar — no requiere aprobación ni postea',
    'je.linked_exceptions': 'Excepciones vinculadas:',
    'je.bucket_live': 'Cierre julio 2026 (vivo)',
    'je.bucket_baseline': 'Línea base · registro RFR enero 2026',
    'je.panel_judgment_calls': 'D · Decisiones pendientes de Edwin (sin asiento todavía)',
    'je.panel_recurring': 'E · Rutinas recurrentes a activar una vez aprobadas',
    'je.panel_accepted_no_action': 'Ya aceptado, sin acción',
    'je.group_a_ready': 'A · Listo para postear',
    'je.group_b_estimated': 'B · Estimado — Edwin confirma cifra',
    'je.group_c_disclose': 'C · Solo revelar, no postear',
    'je.alert_pending': '{n} comprobante{plural} esperan aprobación. Cada uno se postea a {system} sólo después de su aprobación.',
    'je.alert_pending_edwin': '{n} comprobante{plural} esperan aprobación de Edwin. Nada se postea a Alegra hasta que Edwin apruebe cada uno.',
    'je.loading': 'Cargando datos reales…',
    'je.demo.rejected_alert': 'Rechazo simulado — la excepción se devuelve a Angel.',
    'je.demo.approved_alert': 'Aprobación simulada — el motor postea a {system}.',
    'je.demo.reject_btn': 'Rechazar',
    'je.demo.approve_btn': 'Aprobar',
    'je.error_save': 'No se pudo guardar: {msg}',

    /* tracker chrome */
    'tracker.filter.todos': 'Todos',
    'tracker.status.cerrado': 'Cerrado',
    'tracker.status.en_progreso': 'En progreso',
    'tracker.status.pendiente': 'Pendiente',
    'tracker.module.bank_feed': 'Ingesta bancaria',
    'tracker.module.categorization': 'Categorización OTA',
    'tracker.module.reconciliation': 'Conciliación bancaria',
    'tracker.module.reports': 'Informes generados',
    'tracker.module.bank_feed_ok': 'Sincronizado',
    'tracker.module.bank_feed_warn': 'Con avisos',
    'tracker.module.categorization_ok': 'Cruzada',
    'tracker.module.categorization_warn': 'Por revisar',
    'tracker.module.reconciliation_ok': 'Balanceado',
    'tracker.module.reconciliation_warn': 'Sin resolver',
    'tracker.module.reports_ok': 'Xlsx + PDF',
    'tracker.module.reports_warn': 'En cálculo',
    'tracker.module.blocked': 'Bloqueado',
    'tracker.agent_start': 'El agente iniciará el proceso',
    'tracker.al_finalizar_mes': 'al finalizar el mes',
    'tracker.criticas': 'Excepciones críticas',
    'tracker.criticas_note': '{n} sin resolver',
    'tracker.abiertas': 'Excepciones abiertas',
    'tracker.abiertas_note': '{n} en cola',
    'tracker.section_meses': '2026 — meses',
    'tracker.section_resumen': 'Resumen del año',
    'tracker.table.mes': 'Mes',
    'tracker.table.estado': 'Estado',
    'tracker.table.excepciones': 'Excepciones',
    'tracker.table.jes': 'JEs',
    'tracker.table.recuperacion': 'Recuperación tributaria',
    'tracker.table.entregables': 'Entregables',
    'tracker.action.revisar_excepciones': 'Revisar excepciones',
    'tracker.action.ver_jes': 'Ver JEs',
    'tracker.action.ver_entregables': 'Ver entregables',
    'tracker.action.disponible_fin_mes': 'Disponible al finalizar el mes',
    'tracker.action.descargar': 'Descargar →',
    'tracker.action.pendiente_cierre': 'Pendiente cierre',
    'tracker.cerrado_linea_base': 'Cerrado · línea base',
    'tracker.en_curso': 'EN CURSO',
    'tracker.excepciones_julio': 'Excepciones julio',
    'tracker.comprobantes_julio': 'Comprobantes julio',
    'tracker.posteo_alegra': 'Posteo Alegra',
    'tracker.dry_run': 'DRY_RUN',
    'tracker.linea_base_rfr': 'Línea base RFR',
    'tracker.nada_posteado': 'Nada posteado (DRY_RUN)',
    'tracker.meta.summary': '{name} · {closed} cerrado{closed_p} · {inProg} en progreso · {pending} pendiente{pending_p}',
    'tracker.registro_rfr': 'Registro RFR',
    'tracker.exc_historicas': '{n} excepciones históricas',
    'tracker.abiertas_n': '{n} abiertas',
    'tracker.pendientes_edwin': '{n} pendientes Edwin',
    'tracker.recovery_calc': 'En cálculo…',
    'tracker.acumulado': 'Acumulado 2026 (cerrado)',
    'tracker.exceptions_link': 'Excepciones',
    'tracker.jes_link': 'Comprobantes',
    chat_placeholder: 'Pregúntele a su agente…',
    send: 'Enviar',
    refresh: '↻ Actualizar',
    connectors_ok: 'Todo conectado',
    connectors_warn_one: ' conector con aviso',
    connectors_warn_many: ' conectores con aviso',

    /* ============================================================
       SECTION LABELS — dashboard / sub-page headers
       ============================================================ */
    'section.cifras_mes': 'Cifras del mes',
    'section.hacer_ahora': 'Hacer ahora',
    'section.tu_cola': 'Tu cola',
    'section.estado_cierre': 'Estado del cierre',
    'section.detalle_mes': 'Detalle del mes',
    'section.actividad_reciente': 'Actividad reciente del agente',

    /* ============================================================
       CLOSE STATUS — step names + labels
       ============================================================ */
    'closeSteps.Ingesta': 'Ingesta',
    'closeSteps.Categorización': 'Categorización',
    'closeSteps.Reconciliación': 'Reconciliación',
    'closeSteps.Nómina': 'Nómina',
    'closeSteps.Informes': 'Informes',
    'close_status.completo': '{pct}% completo',
    'close_status.eta': 'Listo para entregar el',

    /* ============================================================
       DASHBOARD CARDS — cifras / money / kpi
       ============================================================ */
    'cifras.plata_riesgo': 'Plata en riesgo este mes',
    'cifras.plata_riesgo_sub': 'Lo que cuesta no actuar antes de cerrar marzo',
    'cifras.recuperacion': 'Recuperación tributaria',
    'cifras.operacion_gop': 'Operación · GOP%',
    'cifras.toque_cifra': 'Toque cualquier cifra para ver el cálculo y el documento que la respalda.',

    /* kpi sub-labels */
    'kpi.ocupacion': 'Ocupación',
    'kpi.adr': 'ADR',
    'kpi.revpar': 'RevPAR',

    /* breakdown labels */
    'breakdown.doc_soporte': 'Documento soporte faltante ({n})',
    'breakdown.retefuente_no_aplicada': 'Retefuente no aplicada ({n})',
    'breakdown.iva_no_reclamado': 'IVA no reclamado',

    /* recovery */
    'recovery.credito_fiscal': 'Crédito fiscal IVA',
    'recovery.retefuente_recibida': 'Retefuente recibida',
    'recovery.ds_generados': 'DS generados',

    /* ============================================================
       PANEL HEADERS
       ============================================================ */
    'panel.resumen_tributario': 'Resumen tributario',
    'panel.otas_mes': 'OTAs del mes',
    'panel.conciliacion_3vias': 'Conciliación 3 vías',
    'panel.plata_riesgo_detalle': 'Plata en riesgo · detalle',

    /* ============================================================
       PANEL LINKS / CTAs
       ============================================================ */
    'link.ver_tributario': 'Ver Tributario →',
    'link.ver_reconciliacion': 'Ver Reconciliación →',
    'link.resolver_todo': 'Resolver todo →',
    'link.ver_pendientes': 'Ver pendientes →',
    'link.ver_detalle': 'Ver detalle →',
    'link.ver_kpis': 'Ver KPIs operativos →',
    'link.resolver_brechas': 'Resolver las brechas',
    'link.recordar_manana': 'recordar mañana',
    'link.salir_demo': 'Salir de la demo',

    /* ============================================================
       ACTION QUEUE — labels & CTAs
       ============================================================ */
    'queue.critico': 'Crítico',
    'queue.por_aprobar': 'Por aprobar',
    'queue.en_cola': 'En cola',
    'queue.pendiente': 'Pendiente',
    'queue.urgente': 'Crítico',

    'cta.resolver': 'Resolver →',
    'cta.revisar_aprobar': 'Revisar y aprobar →',
    'cta.revisar_jes': 'Revisar JEs →',
    'cta.abrir_cola': 'Abrir cola →',
    'cta.revisar': 'Revisar →',
    'cta.revisar_pendientes': 'Revisar pendientes ({n})',
    'cta.verificar': 'Verificar →',

    /* ============================================================
       ACTIVITY LOG
       ============================================================ */
    'activity.completado': 'Completado',
    'activity.accion_requerida': 'Acción requerida',
    'activity.critico': 'Crítico',

    /* ============================================================
       TAX STATUS
       ============================================================ */
    'tax_status.en_calculo': 'En cálculo',
    'tax_status.calculado': 'Calculado',
    'tax_status.por_aprobar': 'Por aprobar',
    'tax_status.critico': 'Crítico',

    /* ============================================================
       DEMO BANNER
       ============================================================ */
    'demo.banner': 'Modo demostración — datos ficticios, no es una cuenta real',

    /* ============================================================
       LOGIN PAGE
       ============================================================ */
    'login.tagline': 'Su agente cierra sus libros.',
    'login.pill_owner': 'Portal del Dueño',
    'login.pill_accountant': 'Portal del Contador',
    'login.pill_manager': 'Portal del Gerente',
    'login.username_label': 'Usuario o correo',
    'login.password_label': 'Contraseña',
    'login.signin': 'Iniciar sesión',
    'login.hermes_chat': 'Chat personal de Hermes',
    'login.hermes_alert': 'Reenvíe documentos a su chat personal de Hermes en WhatsApp.',
    'login.soy': 'Soy',
    'login.owner': 'Dueño',
    'login.accountant': 'Contador',
    'login.manager': 'Gerente',
    'login.divider': 'o',
    'login.error': 'Credenciales incorrectas.',

    /* page meta */
    'page.title_resumen': 'ContabIA — Resumen',
    'page.title_exceptions': 'ContabIA — Excepciones',
    'page.title_journal': 'ContabIA — Comprobantes',
    'page.title_nomina': 'ContabIA — Nómina',
    'page.title_tracker': 'ContabIA — Seguimiento',
    'page.title_reconciliacion': 'ContabIA — Reconciliación',
    'page.title_tributario': 'ContabIA — Tributario',
    'page.title_chat': 'ContabIA — Chat',
    'page.title_boveda': 'ContabIA — Bóveda',
    'page.title_deliverables': 'ContabIA — Entregables',
    'page.title_config': 'ContabIA — Configuración',
    'page.title_auditoria': 'ContabIA — Auditoría',
    'page.login_title': 'ContabIA — Iniciar sesión',
    'page.login_title_accountant': 'ContabIA — Iniciar sesión · Contador',
    'page.login_title_manager': 'ContabIA — Iniciar sesión · Gerente',

    /* alert banner */
    'alert.close_in_progress': 'Cierre de {period} en curso. {crit} excepción{plural} crítica{plural2} y {jes} comprobante{s_jes} esperan aprobación antes de cerrar el mes.',
    'meta.procesado': 'procesado {ago}',

    /* risk detail categories */
    'risk.deduccion': 'deducción en riesgo',
    'risk.retefuente_perdida': 'retefuente perdida',
    'risk.iva_no_reclamado': 'IVA no reclamado',

    /* page titles — static page titles set via DOMContentLoaded */
    'page.title_auditoria': 'ContabIA — Auditoría',
    'page.title_boveda': 'ContabIA — Bóveda',
    'page.title_config': 'ContabIA — Configuración',
    'page.title_deliverables': 'ContabIA — Entregables',
    'page.title_chat': 'ContabIA — Chat con el Agente',
    'page.title_auditoria_en': 'ContabIA — Audit',
    'page.title_boveda_en': 'ContabIA — Vault',
    'page.title_config_en': 'ContabIA — Settings',
    'page.title_deliverables_en': 'ContabIA — Deliverables',
    'page.title_chat_en': 'ContabIA — Chat with the Agent',

    /* static page labels */
    'audit.export': '↓ Exportar paquete',
    'boveda.upload': 'Subir un documento de respaldo',
    'boveda.upload_sub': 'PDF, JPG, XLSX, DOCX hasta 10 MB',
    'boveda.search': 'Buscar documentos…',
    'boveda.btn_subir': 'Subir',
    'boveda.btn_escanear': 'Escaneo gratuito',
    'config.sync': 'Sincronizar ahora',
    'config.reconnect': 'Reconectar',
    'config.reglas_header': 'Reglas que el contador autoriza para este cliente. Se ejecutan en cada cierre.',
    'config.reglas_activas': '{n} activas de {total}',
    'deliverables.download': 'Descargar',
    'deliverables.not_ready': 'Sin datos',

    /* tracker page */
    'tracker.page_title': 'ContabIA — Seguimiento de Cierre',
    'tracker.section_months': '2026 — meses',
    'tracker.section_year_summary': 'Resumen del año',
    'tracker.status.closed': 'Cerrado',
    'tracker.status.in_progress': 'En progreso',
    'tracker.status.pending': 'Pendiente',
    'tracker.th_month': 'Mes',
    'tracker.th_status': 'Estado',
    'tracker.th_exceptions_t': 'Excepciones',
    'tracker.th_jes': 'JEs',
    'tracker.th_recovery': 'Recuperación tributaria',
    'tracker.th_deliverables': 'Entregables',
    'tracker.meta_live': 'Tayrona Sailing · julio 2026 EN CURSO',
    'tracker.live_exc_label': 'Excepciones',
    'je.page_title': 'ContabIA — Comprobantes',
    'je.info_accepted': 'Ya aceptado, sin acción',
    'je.reject_prompt': 'Nota de rechazo (opcional):',
    'je.error_save': 'No se pudo guardar: {msg}',

    /* ============================================================
       RECONCILIACION PAGE
       ============================================================ */
    'rec.h1': 'Reconciliación',
    'rec.section_3vias': 'Conciliación 3 vías · PMS · FE · Banco',
    'rec.section_ledger': 'Detalle por reserva',
    'rec.section_bank': 'Conciliación bancaria por cuenta',
    'rec.th_reserva': 'Reserva',
    'rec.th_huesped': 'Huésped',
    'rec.th_canal': 'Canal',
    'rec.th_pms': 'PMS',
    'rec.th_fe': 'FE',
    'rec.th_banco': 'Banco',
    'rec.th_estado': 'Estado',
    'rec.filter_all': 'Todas',
    'rec.filter_variance': 'Variance',
    'rec.filter_fe_missing': 'FE faltante',
    'rec.filter_bank_pending': 'Banco pendiente',
    'rec.filter_ok': 'OK',
    'rec.hero_title': 'Cruce de {period}',
    'rec.hero_sub': 'Cada peso debe aparecer en las tres fuentes. Variances se resuelven antes de cerrar.',
    'rec.empty_filter': 'Sin items en este filtro.',
    'rec.bank_label_saldo': 'Saldo banco',
    'rec.bank_label_libros': 'Saldo libros (GL)',
    'rec.bank_label_diff': 'Diferencia',
    'rec.bank_no_diff': 'Sin diferencia',
    'rec.bank_ok': 'CRUCE OK',
    'rec.bank_resolve': 'POR RESOLVER',
    'rec.footer_items': '{n} item{plural} sin resolver',
    'rec.footer_resolve': 'Resolver →',
    'rec.footer_reconciled': '✓ Reconciliado',

    /* ============================================================
       NOMINA PAGE
       ============================================================ */
    'nom.h1': 'Nómina',
    'nom.section_kpis': 'KPIs operativos',
    'nom.section_ot': 'Horas extras por aprobar ({n})',
    'nom.section_marcaciones': 'Marcaciones recientes',
    'nom.section_empleado': 'Detalle por empleado',
    'nom.section_acciones': 'Acciones',
    'nom.th_empleado': 'Empleado',
    'nom.th_fecha': 'Fecha',
    'nom.th_entrada': 'Entrada',
    'nom.th_salida': 'Salida',
    'nom.th_horas': 'Horas',
    'nom.th_salario': 'Salario base',
    'nom.th_dias': 'Días',
    'nom.th_he': 'HE',
    'nom.th_recargos': 'Recargos',
    'nom.th_total': 'Total',
    'nom.tile_neto': 'Neto a pagar',
    'nom.tile_parafiscales': 'Parafiscales',
    'nom.tile_prestaciones': 'Prestaciones',
    'nom.alert_quincena': 'Quincena lista para aprobar. Tras su aprobación, el motor genera JE-04 (nómina + parafiscales + prestaciones).',
    'nom.btn_devolver': 'Devolver al gerente',
    'nom.btn_ver_je': 'Ver JE-04 propuesto',
    'nom.btn_aprobar_quincena': 'Aprobar quincena',
    'nom.btn_rechazar': 'Rechazar',
    'nom.btn_aprobar': 'Aprobar',
    'nom.kpi_ocupacion': 'Ocupación promedio',
    'nom.kpi_utilizacion': 'Utilización flota',
    'nom.kpi_productividad': 'Productividad',
    'nom.kpi_rotacion': 'Rotación 30d',
    'nom.kpi_horas_marcadas': 'Horas marcadas',
    'nom.kpi_horas_extras': 'Horas extras',
    'nom.empty_ot': 'No hay horas extras pendientes de aprobación.',
    'nom.total_nomina': 'Total nómina',

    /* ============================================================
       TRIBUTARIO PAGE
       ============================================================ */
    'trib.h1': 'Tributario',
    'trib.btn_paquete': '↓ Paquete completo',
    'trib.alert_banner': 'El motor prepara las declaraciones; su contador las presenta en MUISCA. Borradores listos para revisión y firma.',
    'trib.status_draft': 'Borrador',
    'trib.status_ready': 'Listo para presentar',
    'trib.status_filed': 'Presentada',
    'trib.due': 'Vence',
    'trib.btn_detalle': 'Ver detalle por línea',
    'trib.btn_descargar': '↓ Descargar borrador',
    'trib.btn_marcar': 'Marcar presentado',
    'trib.btn_recalculo': 'Solicitar recálculo',
    'trib.declaraciones': '{n} declaración{plural} en preparación',

    /* ============================================================
       AUDITORIA PAGE
       ============================================================ */
    'aud.h1': 'Auditoría',
    'aud.alert_banner': 'Cada dato del cierre tiene fuente, timestamp y hash. Esta es la trazabilidad que respalda cada cifra.',
    'aud.search_placeholder': 'Buscar por descripción, fuente o hash…',
    'aud.th_timestamp': 'Timestamp',
    'aud.th_fuente': 'Fuente · Tipo',
    'aud.th_desc': 'Descripción',
    'aud.th_hash': 'Hash',
    'aud.th_por': 'Por',
    'aud.empty_filter': 'Sin eventos con este filtro.',
    'aud.eventos': '{n} evento{plural} registrados',

    /* ============================================================
       BOVEDA PAGE
       ============================================================ */
    'bov.h1': 'Bóveda',
    'bov.link_auditoria': 'Auditoría →',
    'bov.alert_banner': 'Aquí vive todo lo que entra al motor — extractos bancarios, recibos, facturas, estados de OTAs. Suba una vez, el agente lo usa para todo.',
    'bov.upload_label': 'Arrastre archivos aquí o haga click para subir',
    'bov.upload_sub': 'PDFs · imágenes · Excel · CSV — el agente los etiqueta automáticamente',
    'bov.btn_whatsapp': '📱 Vía WhatsApp',
    'bov.btn_email': '✉ Vía email',
    'bov.filter_all': 'Todas las carpetas',
    'bov.empty_filter': 'Sin archivos con este filtro.',
    'bov.files_count': '{n} archivo{plural}',
    'bov.processed': '{n} procesado{plural} por el agente',

    /* ============================================================
       CONFIGURACION PAGE
       ============================================================ */
    'conf.h1': 'Configuración',
    'conf.tab_entidad': 'Entidad',
    'conf.tab_conectores': 'Conectores',
    'conf.tab_reglas': 'Reglas del contador',
    'conf.tab_otas': 'OTAs',
    'conf.tab_equipo': 'Equipo',
    'conf.tab_notif': 'Notificaciones',
    'conf.field_razon': 'Razón social',
    'conf.field_comercial': 'Nombre comercial',
    'conf.field_nit': 'NIT',
    'conf.field_regimen': 'Régimen tributario',
    'conf.field_municipio': 'Municipio ICA',
    'conf.field_sistema': 'Sistema contable',
    'conf.field_pms': 'PMS',
    'conf.field_banco': 'Banco principal',
    'conf.field_periodo': 'Periodo activo',
    'conf.btn_editar': 'Editar datos',
    'conf.btn_nueva_regla': '+ Nueva regla',
    'conf.btn_guardar': 'Guardar regla',
    'conf.btn_invitar': '+ Invitar miembro',
    'conf.ultima_sync': 'Última sincronización: {last_sync}',
    'conf.reglas_sistema_header': 'Reglas del sistema',
    'conf.reglas_sistema_sub': '(ley tributaria, USALI, conectores) — read-only, no editables. Transparencia, no opinión.',
    'conf.live_reglas_header': 'Reglas de configuración de la empresa — datos reales. Se aplican en cada cierre; el motor nunca vuelve a preguntar lo que ya está aquí.',
    'conf.no_endpoint_demo': 'Desglose OTA de julio aún no está cableado a un endpoint. No se muestran cifras de demostración.',
    'conf.notif_live': 'Notificaciones: reenvíe documentos a su chat personal de Hermes en WhatsApp.',
    'conf.error_reglas': 'Modo en vivo: no se pudo cargar reglas reales ({msg}). Mostrando mockup.',

    /* ============================================================
       DELIVERABLES PAGE
       ============================================================ */
    'del.h1': 'Entregables',
    'del.link_auditoria': 'Auditoría →',
    'del.btn_todo': '↓ Todo',
    'del.filter_all': 'Todos ({n})',
    'del.filter_cierre': 'Cierres mensuales ({n})',
    'del.filter_free_scan': 'Escaneo gratuito ({n})',
    'del.empty_filter': 'Sin entregables en este filtro.',
    'del.ready_status': '{ready} / {total} listos',
    'del.historic': 'archivo histórico · {ready} de {total} listos para descargar',
    'del.free_scan_title': 'Escaneo gratuito de ContabIA',
  },

  en: {
    /* nav chrome */
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
    /* roles */
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
    /* exceptions table */
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
    'common.all': 'All',
    'exc.demo.meta_pending': '{n} exception{plural} in queue',
    'exc.demo.rejected_alert': 'Simulated rejection — Angel flow pending.',
    'exc.demo.approved_alert': 'Simulated approval — engine processes the correction.',
    'exc.live_pill': 'Live data',
    'exc.nada_posteado': 'nothing posted yet',

    /* exception detail panel / buttons */
    'exc.status.pending': 'Pending',
    'exc.status.in_review': 'In review',
    'exc.status.approved': 'Approved',
    'exc.status.rejected': 'Rejected',
    'exc.status.posted': 'Posted',
    'exc.status.blocked': 'Blocked',
    'exc.status.needs_info': 'Needs info',
    'exc.status.overridden': 'Overridden',
    'exc.live_status.open': 'Open',
    'exc.live_status.closed': 'Closed',
    'exc.live_status.approved': 'Approved',
    'exc.live_status.rejected': 'Rejected',
    'exc.filter.criticas': 'Critical',
    'exc.filter.altas': 'High',
    'exc.filter.medias': 'Medium',
    'exc.filter.pendientes': 'Pending',
    'exc.filter.en_revision': 'In review',
    'exc.filter.julio_vivo': 'July (live)',
    'exc.filter.linea_base': 'Baseline',
    'exc.filter.abiertas': 'Open',
    'exc.filter.cerradas': 'Closed',
    'exc.filter.cubierta_regla': 'Covered by rule',
    'exc.panel.descripcion': 'Description',
    'exc.panel.recomendacion': 'Agent recommendation',
    'exc.panel.cerrar': 'Close',
    'exc.panel.rechazar': 'Reject',
    'exc.panel.aprobar_resolucion': 'Approve resolution',
    'exc.nothing_in_filter': 'Nothing in this filter.',
    'exc.period_live': 'July (live)',
    'exc.period_baseline': 'Baseline',
    'exc.rule_tag': 'rule',
    'exc.loading': 'Loading live data…',
    'exc.error_loading': 'Error loading live data.',
    'exc.api_error': 'Could not connect to the live API ({msg}). Is apps/api running on {base}?',
    'exc.block_close': '{n} critical exception{plural} block closing. Resolve before generating reports.',
    'exc.high_open': '{n} high-priority exception{plural} open — Jan-Jun baseline + July live. {closed} already closed.',
    'exc.prompt_rejection_note': 'Rejection note (optional):',
    'exc.save_error': 'Could not save: {msg}',
    'exc.table.exception': 'Exception',
    'exc.table.priority': 'Priority',
    'exc.table.status': 'Status',
    'exc.table.period': 'Period',
    'exc.table.owner': 'Owner',

    /* journal-entries chrome */
    'je.filter.todos': 'All',
    'je.filter.pendientes': 'Pending',
    'je.filter.aprobados': 'Approved',
    'je.filter.bloqueados': 'Blocked',
    'je.filter.julio_vivo': 'July (live)',
    'je.filter.linea_base_ene': 'Jan baseline',
    'je.filter.pendientes_edwin': 'Pending Edwin',
    'je.filter.aprobados_edwin': 'Approved',
    'je.table.cuenta': 'Account',
    'je.table.debito': 'Debit',
    'je.table.credito': 'Credit',
    'je.table.total': 'Total',
    'je.status.pending': 'Pending',
    'je.status.approved': 'Approved',
    'je.status.rejected': 'Rejected',
    'je.status.posted': 'Posted',
    'je.status.blocked': 'Blocked',
    'je.status.pending_edwin': 'Pending (Edwin)',
    'je.status.approved_edwin': 'Approved by Edwin',
    'je.status.disclosure_only': 'Disclose only',
    'je.nothing_in_filter': 'No journal entries in this filter.',
    'je.empty_lines': 'No lines (blocked)',
    'je.empty_lines_live': 'No lines — pending structuring',
    'je.loading': 'Loading live data…',
    'je.demo.rejected_alert': 'Simulated rejection — the exception goes back to Angel.',
    'je.demo.approved_alert': 'Simulated approval — the engine posts to {system}.',
    'je.demo.reject_btn': 'Reject',
    'je.demo.approve_btn': 'Approve',
    'je.error_save': 'Could not save: {msg}',
    'je.blocked_by': 'Blocked by {blocker}. Resolve the exception first.',
    'je.approved_ready': '✓ Approved · ready to post',
    'je.blocked_status': '⚠ Blocked',
    'je.reject_btn': 'Reject',
    'je.approve_btn': 'Approve',
    'je.rejected_tag': '✕ Rejected',
    'je.approved_edwin_tag': '✓ Approved by Edwin · ready to post',
    'je.disclosure_only_tag': 'ℹ Disclose only — no approval or posting needed',
    'je.linked_exceptions': 'Linked exceptions:',
    'je.bucket_live': 'July 2026 (live) close',
    'je.bucket_baseline': 'Baseline · RFR January 2026 record',
    'je.panel_judgment_calls': 'D · Pending Edwin decisions (no entry yet)',
    'je.panel_recurring': 'E · Recurring routines to activate once approved',
    'je.panel_accepted_no_action': 'Already accepted, no action',
    'je.group_a_ready': 'A · Ready to post',
    'je.group_b_estimated': 'B · Estimated — Edwin confirms figure',
    'je.group_c_disclose': 'C · Disclose only, no posting',
    'je.alert_pending': '{n} journal entr{plural} pending approval. Each is posted to {system} only after approval.',
    'je.alert_pending_edwin': '{n} journal entr{plural} waiting for Edwin approval. Nothing posts to Alegra until Edwin approves each.',

    /* tracker chrome */
    'tracker.filter.todos': 'All',
    'tracker.status.cerrado': 'Closed',
    'tracker.status.en_progreso': 'In progress',
    'tracker.status.pendiente': 'Pending',
    'tracker.module.bank_feed': 'Bank feed',
    'tracker.module.categorization': 'OTA categorization',
    'tracker.module.reconciliation': 'Bank reconciliation',
    'tracker.module.reports': 'Reports generated',
    'tracker.module.bank_feed_ok': 'Synced',
    'tracker.module.bank_feed_warn': 'With warnings',
    'tracker.module.categorization_ok': 'Cross-checked',
    'tracker.module.categorization_warn': 'To review',
    'tracker.module.reconciliation_ok': 'Balanced',
    'tracker.module.reconciliation_warn': 'Unresolved',
    'tracker.module.reports_ok': 'Xlsx + PDF',
    'tracker.module.reports_warn': 'Estimating',
    'tracker.module.blocked': 'Blocked',
    'tracker.agent_start': 'The agent will start the process',
    'tracker.al_finalizar_mes': 'at month end',
    'tracker.criticas': 'Critical exceptions',
    'tracker.criticas_note': '{n} unresolved',
    'tracker.abiertas': 'Open exceptions',
    'tracker.abiertas_note': '{n} in queue',
    'tracker.section_meses': '2026 — months',
    'tracker.section_resumen': 'Year summary',
    'tracker.table.mes': 'Month',
    'tracker.table.estado': 'Status',
    'tracker.table.excepciones': 'Exceptions',
    'tracker.table.jes': 'JEs',
    'tracker.table.recuperacion': 'Tax recovery',
    'tracker.table.entregables': 'Deliverables',
    'tracker.action.revisar_excepciones': 'Review exceptions',
    'tracker.action.ver_jes': 'View JEs',
    'tracker.action.ver_entregables': 'View deliverables',
    'tracker.action.disponible_fin_mes': 'Available at month end',
    'tracker.action.descargar': 'Download →',
    'tracker.action.pendiente_cierre': 'Pending close',
    'tracker.cerrado_linea_base': 'Closed · baseline',
    'tracker.en_curso': 'IN PROGRESS',
    'tracker.excepciones_julio': 'July exceptions',
    'tracker.comprobantes_julio': 'July journal entries',
    'tracker.posteo_alegra': 'Post to Alegra',
    'tracker.dry_run': 'DRY_RUN',
    'tracker.linea_base_rfr': 'RFR baseline',
    'tracker.nada_posteado': 'Nothing posted (DRY_RUN)',
    'tracker.meta.summary': '{name} · {closed} closed{closed_p} · {inProg} in progress · {pending} pending{pending_p}',
    'tracker.registro_rfr': 'RFR record',
    'tracker.exc_historicas': '{n} historical exceptions',
    'tracker.abiertas_n': '{n} open',
    'tracker.pendientes_edwin': '{n} pending Edwin',
    'tracker.recovery_calc': 'Estimating…',
    'tracker.acumulado': 'Accumulated 2026 (closed)',
    'tracker.exceptions_link': 'Exceptions',
    'tracker.jes_link': 'Journal entries',
    chat_placeholder: 'Ask your agent…',
    send: 'Send',
    refresh: '↻ Refresh',
    connectors_ok: 'All connected',
    connectors_warn_one: ' connector with a warning',
    connectors_warn_many: ' connectors with a warning',

    /* ============================================================
       SECTION LABELS
       ============================================================ */
    'section.cifras_mes': 'Monthly figures',
    'section.hacer_ahora': 'Do now',
    'section.tu_cola': 'Your queue',
    'section.estado_cierre': 'Close status',
    'section.detalle_mes': 'Month details',
    'section.actividad_reciente': 'Recent agent activity',

    /* ============================================================
       CLOSE STATUS
       ============================================================ */
    'closeSteps.Ingesta': 'Ingestion',
    'closeSteps.Categorización': 'Categorization',
    'closeSteps.Reconciliación': 'Reconciliation',
    'closeSteps.Nómina': 'Payroll',
    'closeSteps.Informes': 'Reports',
    'close_status.completo': '{pct}% complete',
    'close_status.eta': 'Ready to deliver',

    /* ============================================================
       DASHBOARD CARDS
       ============================================================ */
    'cifras.plata_riesgo': 'Money at risk this month',
    'cifras.plata_riesgo_sub': 'Cost of inaction before closing March',
    'cifras.recuperacion': 'Tax recovery',
    'cifras.operacion_gop': 'Operations · GOP%',
    'cifras.toque_cifra': 'Tap any figure to see the calculation and supporting document.',

    /* kpi sub-labels */
    'kpi.ocupacion': 'Occupancy',
    'kpi.adr': 'ADR',
    'kpi.revpar': 'RevPAR',

    /* breakdown */
    'breakdown.doc_soporte': 'Missing supporting docs ({n})',
    'breakdown.retefuente_no_aplicada': 'Unapplied withholding tax ({n})',
    'breakdown.iva_no_reclamado': 'Unclaimed VAT',

    /* recovery */
    'recovery.credito_fiscal': 'VAT tax credit',
    'recovery.retefuente_recibida': 'Withholding tax received',
    'recovery.ds_generados': 'Supporting docs generated',

    /* ============================================================
       PANEL HEADERS
       ============================================================ */
    'panel.resumen_tributario': 'Tax overview',
    'panel.otas_mes': 'OTAs this month',
    'panel.conciliacion_3vias': '3-way reconciliation',
    'panel.plata_riesgo_detalle': 'Money at risk · details',

    /* ============================================================
       PANEL LINKS / CTAs
       ============================================================ */
    'link.ver_tributario': 'See Tax →',
    'link.ver_reconciliacion': 'See Reconciliation →',
    'link.resolver_todo': 'Resolve all →',
    'link.ver_pendientes': 'See pending →',
    'link.ver_detalle': 'See details →',
    'link.ver_kpis': 'See operational KPIs →',
    'link.resolver_brechas': 'Resolve the gaps',
    'link.recordar_manana': 'remind tomorrow',
    'link.salir_demo': 'Exit demo',

    /* ============================================================
       ACTION QUEUE
       ============================================================ */
    'queue.critico': 'Critical',
    'queue.por_aprobar': 'Pending approval',
    'queue.en_cola': 'In queue',
    'queue.pendiente': 'Pending',
    'queue.urgente': 'Critical',

    'cta.resolver': 'Resolve →',
    'cta.revisar_aprobar': 'Review & approve →',
    'cta.revisar_jes': 'Review JEs →',
    'cta.abrir_cola': 'Open queue →',
    'cta.revisar': 'Review →',
    'cta.revisar_pendientes': 'Review pending ({n})',
    'cta.verificar': 'Verify →',

    /* ============================================================
       ACTIVITY LOG
       ============================================================ */
    'activity.completado': 'Completed',
    'activity.accion_requerida': 'Action required',
    'activity.critico': 'Critical',

    /* ============================================================
       TAX STATUS
       ============================================================ */
    'tax_status.en_calculo': 'Estimating',
    'tax_status.calculado': 'Calculated',
    'tax_status.por_aprobar': 'Pending approval',
    'tax_status.critico': 'Critical',

    /* ============================================================
       DEMO BANNER
       ============================================================ */
    'demo.banner': 'Demo mode — fictitious data, not a real account',

    /* ============================================================
       LOGIN PAGE
       ============================================================ */
    'login.tagline': 'Your agent closes your books.',
    'login.pill_owner': 'Owner Portal',
    'login.pill_accountant': 'Accountant Portal',
    'login.pill_manager': 'Manager Portal',
    'login.username_label': 'Username or email',
    'login.password_label': 'Password',
    'login.signin': 'Sign in',
    'login.hermes_chat': 'Hermes personal chat',
    'login.hermes_alert': 'Forward documents to your personal Hermes chat on WhatsApp.',
    'login.soy': 'I am',
    'login.owner': 'Owner',
    'login.accountant': 'Accountant',
    'login.manager': 'Manager',
    'login.divider': 'or',
    'login.error': 'Incorrect credentials.',

    /* page meta */
    'page.title_resumen': 'ContabIA — Overview',
    'page.title_exceptions': 'ContabIA — Exceptions',
    'page.title_journal': 'ContabIA — Journal entries',
    'page.title_nomina': 'ContabIA — Payroll',
    'page.title_tracker': 'ContabIA — Close tracker',
    'page.title_reconciliacion': 'ContabIA — Reconciliation',
    'page.title_tributario': 'ContabIA — Tax',
    'page.title_chat': 'ContabIA — Chat',
    'page.title_boveda': 'ContabIA — Vault',
    'page.title_deliverables': 'ContabIA — Deliverables',
    'page.title_config': 'ContabIA — Settings',
    'page.title_auditoria': 'ContabIA — Audit',
    'page.login_title': 'ContabIA — Sign in',
    'page.login_title_accountant': 'ContabIA — Sign in · Accountant',
    'page.login_title_manager': 'ContabIA — Sign in · Manager',

    /* alert banner */
    'alert.close_in_progress': '{period} close in progress. {crit} critical exception{plural} and {jes} journal entr{s_jes} waiting for approval before closing the month.',
    'meta.procesado': 'processed {ago}',

    /* risk detail categories */
    'risk.deduccion': 'deduction at risk',
    'risk.retefuente_perdida': 'withholding tax lost',
    'risk.iva_no_reclamado': 'VAT unclaimed',

    /* page titles */
    'page.title_auditoria': 'ContabIA — Audit',
    'page.title_boveda': 'ContabIA — Vault',
    'page.title_config': 'ContabIA — Settings',
    'page.title_deliverables': 'ContabIA — Deliverables',
    'page.title_chat': 'ContabIA — Chat with the Agent',

    /* static page labels */
    'audit.export': '↓ Export package',
    'boveda.upload': 'Upload a supporting document',
    'boveda.upload_sub': 'PDF, JPG, XLSX, DOCX up to 10 MB',
    'boveda.search': 'Search documents…',
    'boveda.btn_subir': 'Upload',
    'boveda.btn_escanear': 'Free scan',
    'config.sync': 'Sync now',
    'config.reconnect': 'Reconnect',
    'config.reglas_header': 'Rules the accountant authorizes for this client. They run every close.',
    'config.reglas_activas': '{n} active of {total}',
    'deliverables.download': 'Download',
    'deliverables.not_ready': 'No data',

    /* ============================================================
       RECONCILIACION PAGE
       ============================================================ */
    'rec.h1': 'Reconciliation',
    'rec.section_3vias': '3-way Reconciliation · PMS · FE · Bank',
    'rec.section_ledger': 'Detail by reservation',
    'rec.section_bank': 'Bank reconciliation by account',
    'rec.th_reserva': 'Reservation',
    'rec.th_huesped': 'Guest',
    'rec.th_canal': 'Channel',
    'rec.th_pms': 'PMS',
    'rec.th_fe': 'FE',
    'rec.th_banco': 'Bank',
    'rec.th_estado': 'Status',
    'rec.filter_all': 'All',
    'rec.filter_variance': 'Variance',
    'rec.filter_fe_missing': 'FE missing',
    'rec.filter_bank_pending': 'Bank pending',
    'rec.filter_ok': 'OK',
    'rec.hero_title': '{period} cross-check',
    'rec.hero_sub': 'Every peso must appear in all three sources. Variances are resolved before closing.',
    'rec.empty_filter': 'No items in this filter.',
    'rec.bank_label_saldo': 'Bank balance',
    'rec.bank_label_libros': 'Book balance (GL)',
    'rec.bank_label_diff': 'Difference',
    'rec.bank_no_diff': 'No difference',
    'rec.bank_ok': 'RECONCILED',
    'rec.bank_resolve': 'TO RESOLVE',
    'rec.footer_items': '{n} unresolved item{plural}',
    'rec.footer_resolve': 'Resolve →',
    'rec.footer_reconciled': '✓ Reconciled',

    /* ============================================================
       NOMINA PAGE
       ============================================================ */
    'nom.h1': 'Payroll',
    'nom.section_kpis': 'Operational KPIs',
    'nom.section_ot': 'Overtime pending approval ({n})',
    'nom.section_marcaciones': 'Recent clock-ins',
    'nom.section_empleado': 'Detail by employee',
    'nom.section_acciones': 'Actions',
    'nom.th_empleado': 'Employee',
    'nom.th_fecha': 'Date',
    'nom.th_entrada': 'Check-in',
    'nom.th_salida': 'Check-out',
    'nom.th_horas': 'Hours',
    'nom.th_salario': 'Base salary',
    'nom.th_dias': 'Days',
    'nom.th_he': 'OT',
    'nom.th_recargos': 'Surcharges',
    'nom.th_total': 'Total',
    'nom.tile_neto': 'Net payable',
    'nom.tile_parafiscales': 'Parafiscal',
    'nom.tile_prestaciones': 'Benefits',
    'nom.alert_quincena': 'Fortnight ready for approval. After approval, the engine generates JE-04 (payroll + parafiscal + benefits).',
    'nom.btn_devolver': 'Return to manager',
    'nom.btn_ver_je': 'See proposed JE-04',
    'nom.btn_aprobar_quincena': 'Approve fortnight',
    'nom.btn_rechazar': 'Reject',
    'nom.btn_aprobar': 'Approve',
    'nom.kpi_ocupacion': 'Avg. occupancy',
    'nom.kpi_utilizacion': 'Fleet utilization',
    'nom.kpi_productividad': 'Productivity',
    'nom.kpi_rotacion': '30d turnover',
    'nom.kpi_horas_marcadas': 'Hours clocked',
    'nom.kpi_horas_extras': 'Overtime hours',
    'nom.empty_ot': 'No overtime pending approval.',
    'nom.total_nomina': 'Total payroll',

    /* tracker page */
    'tracker.page_title': 'ContabIA — Close tracker',
    'tracker.section_months': '2026 — months',
    'tracker.section_year_summary': 'Year summary',
    'tracker.status.closed': 'Closed',
    'tracker.status.in_progress': 'In progress',
    'tracker.status.pending': 'Pending',
    'tracker.th_month': 'Month',
    'tracker.th_status': 'Status',
    'tracker.th_exceptions_t': 'Exceptions',
    'tracker.th_jes': 'JEs',
    'tracker.th_recovery': 'Tax recovery',
    'tracker.th_deliverables': 'Deliverables',
    'tracker.meta_live': 'Tayrona Sailing · July 2026 IN PROGRESS',
    'tracker.live_exc_label': 'Exceptions',
    'je.page_title': 'ContabIA — Journal entries',
    'je.info_accepted': 'Accepted, no action needed',
    'je.reject_prompt': 'Rejection note (optional):',
    'je.error_save': 'Could not save: {msg}',

    /* ============================================================
       TRIBUTARIO PAGE
       ============================================================ */
    'trib.h1': 'Tax',
    'trib.btn_paquete': '↓ Complete package',
    'trib.alert_banner': 'The engine prepares the filings; your accountant submits them in MUISCA. Drafts ready for review and signature.',
    'trib.status_draft': 'Draft',
    'trib.status_ready': 'Ready to file',
    'trib.status_filed': 'Filed',
    'trib.due': 'Due',
    'trib.btn_detalle': 'View by line',
    'trib.btn_descargar': '↓ Download draft',
    'trib.btn_marcar': 'Mark as filed',
    'trib.btn_recalculo': 'Request recalculation',
    'trib.declaraciones': '{n} filing{plural} in preparation',

    /* ============================================================
       AUDITORIA PAGE
       ============================================================ */
    'aud.h1': 'Audit',
    'aud.alert_banner': 'Every close data point has a source, timestamp and hash. This is the traceability backing every figure.',
    'aud.search_placeholder': 'Search by description, source or hash…',
    'aud.th_timestamp': 'Timestamp',
    'aud.th_fuente': 'Source · Type',
    'aud.th_desc': 'Description',
    'aud.th_hash': 'Hash',
    'aud.th_por': 'By',
    'aud.empty_filter': 'No events with this filter.',
    'aud.eventos': '{n} event{plural} logged',

    /* ============================================================
       BOVEDA PAGE
       ============================================================ */
    'bov.h1': 'Vault',
    'bov.link_auditoria': 'Audit →',
    'bov.alert_banner': 'Everything that enters the engine lives here — bank statements, receipts, invoices, OTA statements. Upload once, the agent uses it for everything.',
    'bov.upload_label': 'Drag files here or click to upload',
    'bov.upload_sub': 'PDFs · images · Excel · CSV — the agent auto-tags them',
    'bov.btn_whatsapp': '📱 Via WhatsApp',
    'bov.btn_email': '✉ Via email',
    'bov.filter_all': 'All folders',
    'bov.empty_filter': 'No files with this filter.',
    'bov.files_count': '{n} file{plural}',
    'bov.processed': '{n} processed by the agent',

    /* ============================================================
       CONFIGURACION PAGE
       ============================================================ */
    'conf.h1': 'Settings',
    'conf.tab_entidad': 'Entity',
    'conf.tab_conectores': 'Connectors',
    'conf.tab_reglas': 'Accountant rules',
    'conf.tab_otas': 'OTAs',
    'conf.tab_equipo': 'Team',
    'conf.tab_notif': 'Notifications',
    'conf.field_razon': 'Legal name',
    'conf.field_comercial': 'Trade name',
    'conf.field_nit': 'NIT',
    'conf.field_regimen': 'Tax regime',
    'conf.field_municipio': 'ICA municipality',
    'conf.field_sistema': 'Accounting system',
    'conf.field_pms': 'PMS',
    'conf.field_banco': 'Primary bank',
    'conf.field_periodo': 'Active period',
    'conf.btn_editar': 'Edit data',
    'conf.btn_nueva_regla': '+ New rule',
    'conf.btn_guardar': 'Save rule',
    'conf.btn_invitar': '+ Invite member',
    'conf.ultima_sync': 'Last sync: {last_sync}',
    'conf.reglas_sistema_header': 'System rules',
    'conf.reglas_sistema_sub': '(tax law, USALI, connectors) — read-only, not editable. Transparency, not opinion.',
    'conf.live_reglas_header': 'Company configuration rules — real data. They apply every close; the engine never asks again what is already here.',
    'conf.no_endpoint_demo': 'July OTA breakdown is not wired to an endpoint yet. No demo figures shown.',
    'conf.notif_live': 'Notifications: forward documents to your personal Hermes chat on WhatsApp.',
    'conf.error_reglas': 'Live mode: could not load real rules ({msg}). Showing mockup.',

    /* ============================================================
       DELIVERABLES PAGE
       ============================================================ */
    'del.h1': 'Deliverables',
    'del.link_auditoria': 'Audit →',
    'del.btn_todo': '↓ All',
    'del.filter_all': 'All ({n})',
    'del.filter_cierre': 'Monthly closes ({n})',
    'del.filter_free_scan': 'Free scan ({n})',
    'del.empty_filter': 'No deliverables in this filter.',
    'del.ready_status': '{ready} / {total} ready',
    'del.historic': 'historical archive · {ready} of {total} ready to download',
    'del.free_scan_title': 'Free ContabIA scan',
  },
};

function _resolve(pack, key) {
  if (!pack || key == null) return null;
  // Keys are stored as dotted literals ('exc.live_pill'), not nested objects.
  // Exact match first — splitting on '.' was returning the raw key on every page.
  if (Object.prototype.hasOwnProperty.call(pack, key)) {
    const v = pack[key];
    return typeof v === 'string' ? v : null;
  }
  const parts = String(key).split('.');
  let cur = pack;
  for (const p of parts) {
    if (cur && typeof cur === 'object' && p in cur) cur = cur[p];
    else return null;
  }
  return typeof cur === 'string' ? cur : null;
}

function t(key) {
  const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
  const pack = I18N[lang] || I18N.es;
  const esPack = I18N.es;
  let v = _resolve(pack, key);
  if (v != null) return v;
  v = _resolve(esPack, key);
  return v != null ? v : key;
}

/* Replace {placeholder} tokens in a translated string */
function t_fmt(key, vars) {
  let s = t(key);
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      s = s.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v));
    }
  }
  return s;
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