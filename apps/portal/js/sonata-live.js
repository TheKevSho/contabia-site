/* ============================================================
   ContabIA Portal — sonata-live.js

   Live-data bridge for the Sonata Mas SAS January 2026 RFR review.
   Backed by the FastAPI service in apps/api/ (see apps/api/README.md).

   ADDITIVE BY DESIGN — this file never touches data.js. The mock
   blocks in data.js are the `demo` / Scrooge account only. Real logins
   (kevin, edwin, nick) are always live — there is no toggle.

   Real backend shapes differ from data.js's mock shapes (confirmed by
   reading apps/api/data_loader.py, je_data.py, main.py — not just
   inferred from docs). adaptLiveException() / adaptLiveJournalEntries()
   below normalize the real API response into fields the two pages'
   live-mode render paths use. This is deliberately a *parallel* render
   path in each HTML file, not a re-point of the existing mock render
   path — the shapes are different enough (grouped JEs vs. flat array;
   no AI-confidence concept in a human-prepared register) that forcing
   them through the mock's exact fields would hide real differences
   rather than represent them.
   ============================================================ */

const LIVE_CONFIG = {
  'sonata-001': {
    // June-lock / July-live (File 28 final decision 2026-07-17): opening
    // balance locked 2026-06-30; July 2026 is the live, ingesting period.
    // Jan-June register rows ride along as the historical baseline.
    period_iso: '2026-07',
    period_label: 'julio 2026 (saldo inicial: 30-jun)',
    // Override from a page by setting window.CONTABIA_API_BASE before this
    // script loads. Defaults to the deployed API on https, localhost in dev.
    api_base: (window.CONTABIA_API_BASE ||
      (location.protocol === 'https:' ? 'https://api.contabia.co' : 'http://localhost:8000')),
  },
};

function liveAvailable(entityId) {
  return !!LIVE_CONFIG[entityId];
}
function isDemoSession() {
  return sessionStorage.getItem('contabia_demo') === '1';
}
function isLiveMode() {
  // Real users are always live. Demo account (demo/Scrooge) never is.
  if (isDemoSession()) return false;
  return sessionStorage.getItem('contabia_live') === '1' ||
         !!sessionStorage.getItem('contabia_api_token');
}

/* ---- fetch helpers ------------------------------------------------- */

async function _liveFetch(entityId, path, opts) {
  const cfg = LIVE_CONFIG[entityId];
  opts = opts || {};
  const token = sessionStorage.getItem('contabia_api_token');
  opts.headers = Object.assign({}, opts.headers,
    token ? { 'Authorization': `Bearer ${token}` } : {});
     opts.cache = opts.cache || 'no-store';
  const res = await fetch(`${cfg.api_base}/entities/${entityId}${path}`, opts);
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`Live API ${res.status} on ${path}${detail ? ' — ' + detail : ''}`);
  }
  return res.json();
}

async function fetchLiveSummary(entityId) {
  return _liveFetch(entityId, '/summary');
}

async function fetchLiveExceptions(entityId) {
  const raw = await _liveFetch(entityId, '/exceptions');
  return raw.map(adaptLiveException);
}

async function patchLiveException(entityId, excId, status, rejectionNote) {
  return _liveFetch(entityId, `/exceptions/${excId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, rejection_note: rejectionNote || null }),
  });
}

async function fetchLiveJournalEntries(entityId) {
  const raw = await _liveFetch(entityId, '/journal-entries');
  return adaptLiveJournalEntries(raw);
}

async function fetchLiveBoveda(entityId) {
  return _liveFetch(entityId, '/boveda');
}

async function uploadLiveBoveda(entityId, file, folder) {
  const cfg = LIVE_CONFIG[entityId];
  const token = sessionStorage.getItem('contabia_api_token');
  const fd = new FormData();
  fd.append('file', file);
  fd.append('folder', folder || 'General');
  fd.append('uploaded_by', (JSON.parse(sessionStorage.getItem('contabia_user') || '{}').username) || 'portal');
  const res = await fetch(`${cfg.api_base}/entities/${entityId}/boveda/upload`, {
    method: 'POST',
    headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    body: fd,
  });
  if (!res.ok) throw new Error(`Live API ${res.status} on /boveda/upload`);
  return res.json();
}

async function postLiveChat(entityId, message, lang, sessionId) {
  return _liveFetch(entityId, '/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, lang: lang || 'es', session_id: sessionId || null }),
  });
}

async function fetchLiveChatStatus(entityId) {
  return _liveFetch(entityId, '/chat/status');
}

async function patchLiveJournalEntry(entityId, jeId, status, rejectionNote) {
  return _liveFetch(entityId, `/journal-entries/${jeId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, rejection_note: rejectionNote || null }),
  });
}

/* ---- company config rules (configuracion.html, Reglas tab) ---------- */

async function fetchLiveRules(entityId) {
  return _liveFetch(entityId, '/rules');
}

async function createLiveRule(entityId, ruleText, category, source, linkedExceptionId) {
  return _liveFetch(entityId, '/rules', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      rule_text: ruleText,
      category: category || null,
      source: source || 'client_choice',
      linked_exception_id: linkedExceptionId || null,
      created_by: sessionStorage.getItem('contabia_role') || 'portal',
    }),
  });
}

async function patchLiveRule(entityId, ruleId, patch) {
  return _liveFetch(entityId, `/rules/${ruleId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  });
}

/* ---- shape adapters -------------------------------------------------
   Real backend field names (data_loader.py):
     { id, category, phase, severity, title, amount_cop, owner,
       proposed_je_ref, status, disposition, accepted_risk_tag }
   status here is 'open'/'closed' from the CSV, OR 'approved'/'rejected'
   once a PATCH override has been applied (see main.py get_exceptions()).
   Kept as real values, not remapped to the mock's pending/in_review/etc
   vocabulary — exceptions.html's live render path speaks this vocabulary
   directly (see liveStatusLabel() there) rather than forcing a lossy
   translation into the demo dataset's status set.
   --------------------------------------------------------------------- */

const SEVERITY_TO_PRIORITY = { high: 'high', medium: 'medium', low: 'low' };

function adaptLiveException(e) {
  const descParts = [];
  if (e.amount_cop != null) descParts.push(`Monto: COP ${e.amount_cop.toLocaleString('es-CO')}`);
  if (e.owner) descParts.push(`Responsable: ${e.owner}`);
  if (e.proposed_je_ref) descParts.push(`JE propuesto: ${e.proposed_je_ref}`);
  const isLive = e.period && e.period >= '2026-07';
  const periodTag = e.period ? ` · ${e.period}` : '';
  const gateTag = e.gate_b === 'disclose_forward' ? ' · Gate B' : '';
  const handled = (window.RULE_HANDLED_IDS || new Set()).has(e.id);
  return {
    id: e.id,
    subtype: `${e.phase || ''}${periodTag}${gateTag}${e.accepted_risk_tag ? ' · ' + e.accepted_risk_tag : ''}${handled ? ' · rule' : ''}`,
    status: e.status,
    priority: SEVERITY_TO_PRIORITY[e.severity] || 'medium',
    title: e.title,
    description: descParts.join(' — ') || '',
    ai_recommendation: e.disposition || '',
    ai_confidence: null,
    created_at: null,
    period: e.period || null,
    bucket: isLive ? 'live' : 'baseline',
    handled_by_rule: handled,
    rejection_note: e.rejection_note || null,
    _live: true,
    _raw: e,
  };
}

const JE_GROUP_LABEL = {
  A_ready_to_post:   'A · Listo para postear',
  B_estimated:       'B · Estimado — Edwin confirma cifra',
  C_disclosure_only: 'C · Solo revelar, no postear',
};
const JE_GROUP_PRIORITY = {
  A_ready_to_post: 'high',
  B_estimated: 'medium',
  C_disclosure_only: 'low',
};

function adaptLiveJE(je, group) {
  const period = je.period || '2026-01';
  const bucket = je.bucket || (period >= '2026-07' ? 'live' : 'baseline');
  return {
    id: je.id,
    group,
    subtype: JE_GROUP_LABEL[group] || group,
    status: je.status,
    priority: JE_GROUP_PRIORITY[group] || 'medium',
    title: je.description,
    description: je.basis || '',
    ai_confidence: null,
    created_at: null,
    period,
    bucket,
    lines: (je.lines || []).map(l => ({ account: l.account, name: '', debit: l.debit || null, credit: l.credit || null })),
    linked_exceptions: je.linked_exceptions || [],
    rejection_note: je.rejection_note || null,
    _live: true,
    _raw: je,
  };
}

function adaptLiveJournalEntries(resp) {
  // main.py's response keys are 'ready_to_post'/'estimated'/'disclosure_only'
  // (no letter prefix) -- but each JE object already carries its own
  // 'group' field (A_ready_to_post/B_estimated/C_disclosure_only, set in
  // je_data.py), so read the group off the item itself rather than
  // re-deriving it from the bucket key. Confirmed against a live response,
  // not assumed from the README's abbreviated example.
  const buckets = ['ready_to_post', 'estimated', 'disclosure_only'];
  const items = [];
  buckets.forEach(key => (resp[key] || []).forEach(je => items.push(adaptLiveJE(je, je.group))));
  return {
    items,
    open_judgment_calls: resp.open_judgment_calls || [],
    recurring_routines: resp.recurring_routines || [],
    accepted_no_action: resp.accepted_no_action || [],
  };
}
