# Contabia portal backend — Sonata Mas slice (2026-07-10)

## What this is

A real, running FastAPI service that replaces `data.js`'s mock object for
**one entity** (`sonata-001` = Sonata Mas SAS / Tayrona Sailing) and **two
pages** (`exceptions.html`, `journal-entries.html`), so January's exception
review can happen through the portal's real endpoints instead of a static
mock. It implements the exact endpoint contract already specified in [[18-Portal-and-Free-Scan|File 18]]
(`Portal & Free Scan Flow`), so `exceptions.html`/`journal-entries.html`
should need only a data-source swap, not a rewrite.

This is deliberately **not** the full motor (no rules engine, no Inngest
orchestration, no connector scheduling, no posting to Alegra). It is the
review-and-approve slice needed to get January's already-prepared exception
register onto the platform, per `PORTAL_INGESTION_HANDOFF.md`.

Tested in this session with FastAPI's `TestClient` — all endpoints below
were exercised against the real data and return correctly (200s, 404 for
unknown entity, 503 for the Alegra check with no credentials set, PATCH
state changes persist).

## Why I stopped here and didn't push it to `TheKevSho/contabia-site`

I don't have GitHub access in this session — no connector for it was
available. This folder is a standalone, runnable service. Someone with
repo access (you or Johan) needs to either:
1. Drop this folder in as `apps/api/` (or similar) in the monorepo and wire
   `apps/portal/js/data.js` to call it (see "Frontend integration" below), or
2. Tell me to try again in a session where GitHub is connected and I'll do
   the wiring directly.

## Running it

```bash
cd portal-backend
pip install -r requirements.txt
ALEGRA_EMAIL=you@example.com ALEGRA_API_TOKEN=xxx uvicorn main:app --reload
```

`ALEGRA_EMAIL`/`ALEGRA_API_TOKEN` are only needed for the `/alegra-check`
read-only endpoint. Everything else (exceptions, journal-entries) works
without them, reading from `data/exception_register.csv`.

**Alegra credentials are never hardcoded** — `alegra_client.py` reads them
from environment variables only, matching the "no secrets in source" rule.
Requires Alegra Pro or Plus (API is not available on Emprendedor/Pyme, per
[[07-Architecture-of-Record|File 07]]).

## Deploying for real

**Decided 2026-07-10 (Kevin): Railway, not Render, for this slice.** File 07's
Compute/deploy row still names Render as primary (pending Johan's
ratification of the overall stack) and lists Railway as "the close
alternative (better DX) if Johan prefers" — this is a scoped choice for the
Sonata Mas portal-backend deployment specifically, not a change to that
company-wide row. Web service, one process; `sonata_mas_001.sqlite` (the
approval-state store) needs a Railway **volume** mounted (not ephemeral
container storage), or restarts forget every approve/reject click. Matches
the committed "SQLite, one file per client" architecture either way; adding
Cantamar or a beta client later means adding another entity row in
`main.py` + another SQLite file on the same volume, not a schema migration.

Not yet done: Railway project not created, repo not connected, root
directory/start command/volume/env vars not configured. See
[[Continuation-Portal-and-Repo]] §4 for exact next steps.

## Endpoints implemented (subset of [[18-Portal-and-Free-Scan|File 18]]'s full list, scoped to this pass)

```
GET   /entities
GET   /entities/{id}/summary
GET   /entities/{id}/exceptions
PATCH /entities/{id}/exceptions/{exc_id}          { status: approved|rejected, rejection_note? }
GET   /entities/{id}/journal-entries
PATCH /entities/{id}/journal-entries/{je_id}      { status: approved_by_edwin|rejected, rejection_note? }
GET   /entities/{id}/alegra-check                 read-only trial-balance + period-status cross-check
```

Deliberately **not implemented**: `POST /entities/:id/close/:period/post`.
Per your decision this pass stops at an Edwin-ready package — nothing calls
`AlegraClient.post_journal()`. When Edwin has actually signed off, wiring
that endpoint is a ~20-line addition (loop over journal entries whose status
is `approved_by_edwin`, call `post_journal()` once per entry — Alegra has no
bulk-import endpoint for journals, confirmed in [[07-Architecture-of-Record|File 07]]).

## Frontend integration (what changes in the real repo)

`data.js` currently exports a global `DATA` object read by `exceptions.html`
and `journal-entries.html`. Per [[18-Portal-and-Free-Scan|File 18]]: *"the mock data shape IS the API
contract"* — so the swap is: replace the two calls into `DATA.exceptions`
and `DATA.journalEntries` with `fetch()` calls against this service:

```js
const API_BASE = 'http://localhost:8000'; // or wherever this gets deployed

async function getExceptions(entityId) {
  const res = await fetch(`${API_BASE}/entities/${entityId}/exceptions`);
  return res.json();
}

async function patchException(entityId, excId, status, rejectionNote) {
  const res = await fetch(`${API_BASE}/entities/${entityId}/exceptions/${excId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, rejection_note: rejectionNote }),
  });
  return res.json();
}

async function getJournalEntries(entityId) {
  const res = await fetch(`${API_BASE}/entities/${entityId}/journal-entries`);
  return res.json(); // { ready_to_post, estimated, disclosure_only, open_judgment_calls, recurring_routines }
}
```

`exceptions.html`'s approve/reject buttons are currently `alert()` stubs
(per [[18-Portal-and-Free-Scan|File 18]]'s own "Known Issues" table) — replace those stub calls with
`patchException(...)` above. Same for `journal-entries.html`'s stubs with
`patchException`/a `patchJournalEntry` equivalent.

Note the journal-entries response shape is grouped (`ready_to_post` /
`estimated` / `disclosure_only`) to match how `ASIENTOS_PROPUESTOS_CONSOLIDADO`
organizes them for Edwin — this is richer than a flat `journalEntries[]`
array, so `journal-entries.html` will need a small render change (render by
group) rather than a pure re-point. Flagging this rather than quietly
picking a shape that hides the difference.

## Motor housekeeping applied in this pass (scoped to "what blocks January -> Alegra" only)

- `/journals`, not `/journal-entries` — the corrected Alegra endpoint ([[07-Architecture-of-Record|File 07]],
  2026-07-08 correction) is what `alegra_client.py` actually calls.
- No bulk-import assumption — the connector is written as one POST per line,
  matching the confirmed absence of a bulk journals endpoint.
- Exponential backoff on HTTP 429, per the 150 req/min rate limit.

**Explicitly out of scope for this pass** (per your scope decision — these
don't block Sonata Mas's January posting readiness, they're pre-existing
backlog items for later): the incremental-fetch bug in the Alegra sync
script, the `bank_transactions` schema bug, the missing attachment-download
step in email intake, and the FareHarbor parser gap. All four are still
open in [[07-Architecture-of-Record|File 07]]'s Open Items list.

## Files

- `main.py` — the FastAPI app and all routes.
- `alegra_client.py` — Alegra REST connector (read + the two write methods,
  unused by this pass but ready for when posting is authorized).
- `data_loader.py` — parses `exception_register.csv` into the API shape.
- `je_data.py` — the structured proposed journal entries, transcribed from
  `ASIENTOS_PROPUESTOS_CONSOLIDADO_2026-07-06_EN.md`.
- `data/exception_register.csv` — the real January 2026 Sonata Mas exception
  register (43 rows).
