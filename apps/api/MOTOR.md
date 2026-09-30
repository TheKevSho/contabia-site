# The motor — what it is, how it runs, what's next

*For Johan. Written 2026-09-29 from the code at `ef4518f` and the vault handoffs
(`_cowork/HANDOFF_2026-09-09_coded-motor-build`, `…09-18_motor-rebuild-complete`,
`…09-19_gate-applicable-sources-and-july-run`). If this file and the code disagree, the code wins.*

> **FROZEN 2026-09-29.** The motor now lives in `contabia_ui/motor/` (fork `TheKevSho/contabia_ui`,
> branch `kevin/portal-port`), copied byte-identical from `d86e536`. Fixes and changes go **there only**;
> do not edit the motor files in `apps/api/` any more. Parity receipt: Tayrona 2026-07, mock and live
> (phases 1–6) give identical reports, apart from the scratch DB path and one line number. Client
> registers (`data/exception_register*.csv`) stay out of the new repo. They are read from
> `CONTABIA_REGISTERS_DIR`, which wins the same way `data/` did here.

## One line

The motor turns **one company's documents for one month** into **exceptions + balanced, proposed journal
entries** that a CPA approves before anything posts. Pure Python stdlib + sqlite3, no LLM, no network except
Alegra `/bills` reads and the (gated) post.

## What it reads — not the scraped Alegra DB

| Input | Where | Notes |
|---|---|---|
| Period documents as canonical `.md` | vault `<client>/raw-accounting/<YYYY-MM Mes>/` (resolved by `boveda_source.py`) | Format: `data/CANONICAL_SCHEMA.md`. `.md` is the source of truth; SQLite is derived. |
| Per-company config | `company_rules` table, seeded at import by `account_map_seed.py` and `gate_sources_seed.py` | account_map = motor account → real Alegra account id. gate_sources = which inputs apply to this company and why. |
| Alegra `/bills` | `alegra_client.py` (paged to exhaustion) | Only the pre-close gate reads it. |

The Alegra DBs you scraped for Cantamar and Sonata are the **ledger** (what's already booked). They're what
the chat should read, and they're the chart of accounts that `account_map` points at. They are not the
motor's input.

## Phases (`motor_run.py <entity> <YYYY-MM>`)

| # | File | Does | Emits |
|---|---|---|---|
| 1 | `derive_index.py` | `.md` → SQLite `canonical_documents`. Hash-skip, merge-never-clobber, doc_id collisions error out. | index rows |
| 2 | `cfd_engine.py` | 22 CFD rules (Corpus de Fallas Detectadas) + 8 received-doc integrity flags, per document. | **exceptions** (rule id + reason) |
| 3 | `pre_close_gate.py` | Is the month's data actually here? Bank, card, PILA, PMS, OTAs, exception register — per `gate_sources`. Stale/mislabeled files fail. | pass / blockers. **If it fails, 4–6 run advisory only.** |
| 4 | `revenue_recon.py` | Card/processor settlements (e.g. Bold): POS vs deferred, channel footing. | revenue JEs + gaps |
| 5 | `expense_recon.py` | PILA, exception register rows, foreign vendor → documento soporte. | expense JEs + gaps |
| 6 | `bank_recon.py` | Bank statement lines, GMF 4x1000 true-up, deposit deltas. | bank JEs + gaps |
| 8 | `assemble_jes.py` | Joins 4–6: balance check, account mapped, traced to a source doc, no dup ids, priority. | `review_package.json`: each JE `postable` or not, plus `blockers` |
| 9 | `main.py` `POST /entities/{id}/close/{period}/post` | Posts approved JEs to Alegra. Claim-before-post, read-back verify, period scoped. `DRY_RUN=true` by default. | posting log |

Not built yet: **7 (tax pass**: ICA, retefuente, IVA, autorretención) and **10 (workbook + archive)**.

## So where do exceptions come from?

Three places, all generic code: CFD rules (phase 2), gate blockers (phase 3), recon gaps (4–6).
What's per-company is **config** (`gate_sources`, `account_map`, later the PUC). Adding a client is config
plus documents, not new code, except when the ledger is a system with no adapter yet (AguaSala = World Office Desktop).

## How often does it run?

On demand, per entity per period. No scheduler. The expected rhythm is `derive_index` whenever new
documents land, and the full run at month close and again after missing data arrives. Nothing is on cron today.

## Run it

```bash
cd apps/api
./.venv/bin/pytest -q                                   # 50 passed at ef4518f per the 09-20 handoff (not re-run for this doc)
./.venv/bin/python motor_run.py tayrona 2026-07 --mock
./.venv/bin/python assemble_jes.py tayrona 2026-07 --mock
./.venv/bin/python pre_close_gate.py tayrona 2026-07    # real vault tree; fails on July OTA (mislabeled June files)
```

## What's next, in order

1. **G1: Tayrona July posted through the motor** (target 09-30). No code missing. It needs the real July
   GYG/Viator exports (the ones on disk are byte-identical to June), two account_map follow-ups
   (`HANDOFF_2026-09-18_sonata-account-map`), and Kevin's explicit `DRY_RUN=false`.
2. **Wire the portal to the motor.** The FastAPI exception/JE endpoints exist in `main.py`. The Reflex app
   needs to show `review_package.json` exceptions + JEs with their source doc, and approve → phase 9.
3. **Phase 7 tax pass** (spec: Motor-Checklist-Hospitality Phase 5, resume prompt in the 09-09 handoff).
4. **AguaSala (G2, October):** `aguasala` in `ENTITIES` and `boveda_source.ENTITY_VAULT_DIRS`, a WO-Desktop
   `gate_sources` entry, and a WO output adapter once PR-2026-09-28-07 (tier / import path) is settled.
   The September corpus already indexes clean.
5. Chat: read the ledger DB + `canonical_documents`, cite source docs, keep history.
