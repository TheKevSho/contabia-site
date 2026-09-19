# CANONICAL_SCHEMA — per-document knowledge graph (.md) spec

**Status:** live — adopted 2026-09-09 (coded-motor build), derived from
[[07-Architecture-of-Record|File 07]] §"Update 2026-08-08 — per-document
knowledge graph (JOHAN_BRIEF_MINIMAL)" + the two design rules that update
landed with. REBUILT 2026-09-18 (file lost in the Time Machine restore; this
is a spec-only reconstruction, not a byte-restore).

**Audience:** the motor (derive_index.py parses this format), sessions that
write canonical docs, and Johan's future R2/git pipeline.

---

## 1. What this is

Every inbound document (invoice, bank line, card statement, receipt, OTA
settlement, payroll planilla, exception-register snapshot) gets **its own
`.md` file** — the canonical, human-editable **system of record**. The files
form a directed graph: each `.md` is a **node**, each wiki-link is a typed
**edge** (the same structure Obsidian's graph view draws; GraphRAG builds
automatically). Search/aggregation live in a **derived, disposable SQLite
index** (`canonical_documents`, built by `derive_index.py`) — never a peer
writer and never hand-repaired; if it corrupts, `rm` it and rebuild from the
`.md` files (File 07 design rule #1: separate storage from search).

**Hard rules:**

1. `.md` = SSOT; SQLite = derived index. No peer writers, no DB→md direction.
2. Agent never overwrites the human's edits — git is the arbiter.
3. Two git identities: agent commits as `contabia-agent <agent@contabia.co>`,
   humans as themselves — `git log`/`git blame` shows provenance.
4. Never `git push --force`. Regeneration is a **merge**, never a clobber.
5. Zip the LLM out: the motor and the indexer are pure stdlib + sqlite3.

---

## 2. File location & naming

```
<client>/raw-accounting/<period>/<SOURCE>_<description>_<YYYY-MM>.md
```

- One file per document object; a batch export (e.g. a bank statement) is ONE
  file with all its lines, not one file per line.
- Filename is human-readable and period-tagged (`Bold_Transacciones_2026-07.md`).
- The machine identity is the `[[doc:…]]` wiki-link (below), not the filename:
  files may be renamed/moved; the id must not.

---

## 3. Frontmatter

Two forms are accepted by `derive_index.py`:

### 3a. Canonical form — YAML block

```yaml
---
vendor: Bold
vendor_nit:            # optional; foreign vendors carry none
amount: 9491500.00     # COP, gross, when the doc has a single headline figure
date: 2026-08-24       # doc date / receipt date
type: card_statement   # see §4
confidence: high       # high | medium | low
flags: []              # string list, e.g. [dedupe_check, ds_pending]
hash: <sha256>         # written by the generator; verified by derive_index
locked_fields: []      # field names the generator must NOT overwrite (§6)
human_reviewed: false
---
```

### 3b. Migrated form — bold-KV header (accepted, legacy)

The first migration pass (migrate_boveda, 2026-09-09) wrote headers as bold
key/value lines above the first `## ` heading; `derive_index` parses both:

```markdown
**Source:** `Reporte_mensual_de_transacciones_2026-07.xlsx` (WhatsApp, received 2026-08-24)
**Filed:** `tayrona-sailing/raw-accounting/2026-07 Julio/Bold_Transacciones_2026-07.xlsx`
**Entity:** Tayrona Sailing (Sonata Mas S.A.S.)
```

Keys map to the YAML fields (`Source`→source, `Filed`→filed, `Entity`→entity,
`Vendor`→vendor, `Amount`→amount, `Type`→type, `Confidence`→confidence,
`Flags`→flags, `Locked fields`→locked_fields, …). New docs should use YAML;
the parser keeps reading both so old docs stay valid SSOT.

---

## 4. Frontmatter field vocabulary

| Field | Values / notes |
|---|---|
| `vendor` | Vendor name as stated by the doc (never normalized silently — normalization is a decision). |
| `vendor_nit` | Colombian NIT when the issuer has one. **Absent = foreign** for the motor's DS logic. |
| `amount` | COP, gross. When a doc carries more structure, the body tables own the figures and `amount` is the headline only. |
| `date` | `YYYY-MM-DD`. For exports, prefer the report's own covered range (see `covered_start/covered_end` extension — CFD-0018). |
| `type` | One of the motor vocabulary: `bank_statement`, `card_statement`, `payroll`, `bill`, `invoice`, `ds`, `settlement`, `register`, `report`, `document`. The recons additionally recognize `doc_type` values like `card_statement` from filenames when the frontmatter omits `type`. |
| `confidence` | `high` / `medium` / `low` — extraction confidence; low-confidence docs ride the exception queue (Checklist Phase 3.1). |
| `flags` | Motor/agent flag names, e.g. `[dedupe_check, ota_phantom]`. |
| `hash` | sha256 of the file content; written/stamped by the generator, compared by `derive_index`. |
| `locked_fields` | Field names the generator refuses to overwrite (§6). |
| `human_reviewed` | Set true by a human after review; generator leaves the doc's values alone. |

Extension keys seen in real docs (all tolerated): `source`, `filed`, `entity`,
`merchant`, `covered_start`, `covered_end`, `period`, `gross`, `fees`,
`deposited`, `account`, `line_count`.

---

## 5. Body sections — the five fixed blocks

After the frontmatter, exactly these `## ` sections (order as below; any may
be empty but the heading stays):

1. **`## Fields`** — the document's own key/value table (issuer, NIT, CUFE,
   dates, account, totals as printed). This is the raw-record block:
   values as the doc states them, before motor interpretation.
2. **`## Extraction detail`** — what was pulled from where, incl. per-line
   detail for statement docs (transaction tables, per-channel breakdowns).
   Every number the motor will use must trace here or to the Fields table.
3. **`## Agent analysis`** — the agent's read: classifications, journal-entry
   proposals, CFD rule hits, open questions. **Suggestions live here, never
   in Fields** (Fields is the doc's own record).
4. **`## Related docs`** — wiki-links to the docs this one connects to
   (the graph edges).
5. **`## Decision trail`** — dated entries: what was decided, by whom
   (Kevin / Edwin / Nick / motor), citing the exception id when one exists
   (the register links back: `Proposed_JE`, `Disposition`).

Tables in any section are parsed by `derive_index` for structured fields
(e.g. a Summary row `Valor total` → `amount_cop`); column semantics must be
stated in the header row so the tables stay machine-readable.

---

## 6. Wiki-links (the edges)

- `[[doc:YYYYMMDD-slug]]` — **the document id.** First `[[doc:…]]` in the
  file wins the `doc_id` in `canonical_documents`. Uniqueness is enforced:
  two files claiming one `doc_id` with different content is surfaced as an
  error by derive_index, never last-write-wins.
- `[[vendor:NIT]]` — the vendor node (typed edge to a vendor profile).
- `[[exception:EX-J07-12]]` — links a doc to its register row.
- `[[file:…]]`, `[[note:…]]` — free-form edges.

---

## 7. Locking — the generator never overwrites the human

`locked_fields` (or `human_reviewed: true`) is the contract from File 07
design rule 2c: when the agent's fresh extraction **disagrees** with a locked
value it does NOT silently keep either — it writes its suggestion into
`## Agent analysis / Decision trail` and **raises an exception** (exception
queue), so a human disposition is recorded, not assumed. Field-level locks
(`[cuenta, centro_costo]`) take precedence over whole-doc review.

---

## 8. Derivation contract (derive_index.py)

- Table: `canonical_documents` (doc_id PK, path UNIQUE, hash, run_sha,
  git_author, created_at, updated_at, plus derived columns: entity, vendor,
  amount_cop, period, doc_date, doc_type, confidence, flags, locked_fields,
  frontmatter, sections, wiki_links).
- **Idempotent:** content-hash compare → unchanged files SKIP (no row churn;
  `run_sha` stays pinned to the run that produced the row).
- **Merge, never clobber:** changed content → `ON CONFLICT(doc_id) DO UPDATE`;
  a file that merely MOVED (same content, new path) merges to the new path;
  no DELETE-then-INSERT, no `--force`.
- **Run-pinned:** every row records `run_sha` (`RAILWAY_GIT_COMMIT_SHA` env or
  `git rev-parse HEAD`, else `local`) and `git_author`.
- **Surfaced, never silent:** parse failures and doc_id collisions land in
  the report's `errors` (exit 1), rule: a broken indexer must be visible.
- **Disposable:** the whole table can be `rm` + rebuilt from `.md` at any
  time; never hand-repair rows.

---

## 9. Worked example — the surviving Bold doc (boveda_seed)

`data/boveda_seed/Bold_Transacciones_2026-07.md` (migrated/bold-KV form) is
the reference specimen: `**Source/Filed/Entity:**` header, `## Summary` table
(13 transactions, gross 9,491,500.00, fees 577,735.85, deposited
8,913,764.15), `## By channel` breakdown (datáfono 11 / 3,541,500; link
2 / 5,600,000) and a deferral table identifying the two prepayments. From it
the motor derives: `vendor=Bold`, `amount_cop=9,491,500.00`,
`period=2026-07`, `doc_type=card_statement`; revenue_recon builds the POS /
fees / deferral JEs from the same rows (footing breach between channels and
summary is a motor finding, not a parser failure — see the recon's gaps).

---

## 10. Validation (what the motor checks about your .md)

1. `derive_index` parses it without error and the hash column matches
   content (`python3 derive_index.py --data-dir …` re-run → all `skipped`).
2. One `[[doc:…]]` id per file, unique across the corpus.
3. Every figure the recons cite traces to a `## Fields` / `## Extraction
   detail` row (the recon outputs name the source file in `linked_docs`).
4. Locked fields unchanged since the last human review (git diff discipline).
5. `cash amounts parse with parse_cop` — Colombian `16.000,00` vs US
   `16,000.00` both resolve; literally-formatted figures that don't parse are
   an extraction defect (CFD-0019).

---

> **Agent proposes · CPA approves · Motor commits · Every number traceable to its source**