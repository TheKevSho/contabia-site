/* ============================================================
   ContabIA Portal — sonata-live.js

   Live-data bridge for the Sonata Mas SAS January 2026 RFR review.
   Backed by the FastAPI service in apps/api/ (see apps/api/README.md).

   ADDITIVE BY DESIGN — this file never touches data.js. The sonata-001
   mock block in data.js (period_iso '2026-06', the demo dataset used
   everywhere else in the portal) stays exactly as it is. This file
   layers a real/demo TOGGLE on top of the *same* entity id, scoped to
   exceptions.html and journal-entries.html only, per Kevin's explicit
   instruction not to trash or silently replace the sample data.

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
    period_iso: '2026-01',
    period_label: 'enero 2026',
    // Override from a page by setting window.CONTABIA_API_BASE before this
    // script loads (e.g. once the apps/api service is deployed on Railway).
    api_base: (window.CONTABIA_API_BASE || 'http://localhost:8000'),
  },
};

function liveAvailable(entityId) {
  return !!LIVE_CONFIG[entityId];
}
function isLiveMode() {
  return sessionStorage.getItem('contabia_live') === '1';
}
function setLiveMode(on) {
  sessionStorage.setItem('contabia_live', on ? '1' : '0');
  location.reload();
}

/* ---- fetch helpers ------------------------------------------------- */

async function _liveFetch(entityId, path, opts) {
  const cfg = LIVE_CONFIG[entityId];
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

async function patchLiveJournalEntry(entityId, jeId, status, rejectionNote) {
  return _liveFetch(entityId, `/journal-entries/${jeId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, rejection_note: rejectionNote || null }),
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
  return {
    id: e.id,
    subtype: `Fase ${e.phase}${e.accepted_risk_tag ? ' · ' + e.accepted_risk_tag : ''}`,
    status: e.status,                                   // open | closed | approved | rejected
    priority: SEVERITY_TO_PRIORITY[e.severity] || 'medium',
    title: e.title,
    description: descParts.join(' — ') || '(sin detalle adicional)',
    ai_recommendation: e.disposition || 'Sin disposición registrada.',
    ai_confidence: 1,          // real register, accountant-prepared — not an AI guess
    created_at: null,          // register has no per-row date; period is 2026-01
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
  return {
    id: je.id,
    group,
    subtype: JE_GROUP_LABEL[group] || group,
    status: je.status,        // pending_edwin_approval | approved_by_edwin | rejected | disclosure_only
    priority: JE_GROUP_PRIORITY[group] || 'medium',
    title: je.description,
    description: je.basis || '',
    ai_confidence: 1,
    created_at: null,
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
