"""Sonata Mas (Tayrona Sailing) — account_map seed (committed, idempotent).

The account_map is NOT a file: it is rows in `company_rules`
(category = 'account_map', active = 1) that BOTH readers load and must agree
on:

  - main.py `_account_map()` / `_unmapped_accounts()` / `_je_to_alegra_payload()`
    (Phase 9 posting path — portal)
  - assemble_jes.py `load_account_map()` / `validate_je()`
    (Phase 8 assembler — CLI, review package)

Fork decision 2026-09-18 (fork B, agreed with Kevin): both readers key on the
EXACT emitted account string (e.g. '1110xx Bold clearing'), no normalization,
and both treat a line account as MAPPED when its string is a map key whose
VALUE resolves to a real Alegra account id (a value that is itself a
placeholder — 'xx' / 'PENDING' — does NOT count). The `xx` stubs stay in the
phase code by design (revenue_recon.py / expense_recon.py / bank_recon.py);
this seed gives each one its real destination.

TWO entity ids intentionally share the same map:
  - 'sonata-001' — the ENTITIES registry key (main.py), the DB filename, the
    portal routes, and the seed_rules convention.
  - 'tayrona'    — the motor CLI slug (motor_run.py / assemble_jes.py usage).
A mismatch here is the silent-empty-map trap: it yields an EMPTY map on one
side and refuses every JE without a single error. Seeding both ids from this
one source keeps them in lockstep.

Values (alegra_id) come from Sonata's live chart of accounts. The seeder is
ATOMIC: if any entry still has alegra_id = None it writes NOTHING and reports
the pending slots — a half-resolved map must never seed (a poster that sends
a PUC string as an Alegra account id would mistpost silently).

Zero LLM, stdlib-only. Mirrors the seed_standing_rules contract: match on
rule_id, never overwrite a row the user already edited, bilingual
rule_text_es/_en kept in step with the machine `rule_text`.
"""
from __future__ import annotations

import json
from typing import Any, Optional

# ---------------------------------------------------------------------------
# The map — one entry per emitted stub account. `puc` is the accounting
# judgment (which PUC code each stub becomes); `alegra_id` is the SoR id
# pulled from the live chart. Evidence column cites where the repo proves it.
# ---------------------------------------------------------------------------
SONATA_MAP_ENTRIES: list[dict[str, Optional[str]]] = [
    {
        "key": "1110xx Bold clearing",
        "puc": "111020",
        "rule_tag": "bold-clearing",
        "alegra_id": "5327",  # verified live chart, 2026-09-18 (Kevin/Opus session): code 111020 'bold', parent 5005
        "label_es": "Bancos — Bold (clearing de ventas por canal)",
        "label_en": "Banks — Bold (sales clearing per channel)",
        "basis_es": "je_data AJ-J07-05 usa '111020 bold'; el clearing recibe el bruto de "
                    "ventas y lo netea contra comisiones/consignaciones (REV-01/03).",
        "basis_en": "je_data AJ-J07-05 books '111020 bold'; the clearing receives gross "
                    "sales and nets fees/settlements (REV-01/03).",
    },
    {
        "key": "1110xx Bancos",
        "puc": "111015",
        "rule_tag": "bank",
        "alegra_id": "5115",  # verified live chart 2026-09-18: BANCOLOMBIA, parent 5005, asset
        "label_es": "Bancos — Bancolombia (CTA 78100001780)",
        "label_en": "Banks — Bancolombia (ACCT 78100001780)",
        "basis_es": "Reclass enero 2026: 'Bancolombia (111015)'. El GMF se causa sobre la "
                    "cuenta principal del extracto (BNK-01).",
        "basis_en": "Jan-2026 reclass: 'Bancolombia (111015)'. GMF true-up is booked "
                    "against the main statement account (BNK-01).",
    },
    {
        "key": "4305xx Ingresos por servicios",
        "puc": "413595",
        "rule_tag": "revenue-services",
        "alegra_id": "5119",  # verified live chart 2026-09-18: VENTAS OTROS PRODUCTOS, parent 5063, income
        "label_es": "Ingresos — VENTAS OTROS PRODUCTOS (413595)",
        "label_en": "Revenue — VENTAS OTROS PRODUCTOS (413595)",
        "basis_es": "El canal datáfono/POS de Bold se acredita aquí en los libros reales "
                    "(asientos BV-POS1685…; enero 2026). El 4305 no existe en el catálogo. "
                    "414515 TRANSPORTE queda reservado para FE de transporte (FV-FE7xxx).",
        "basis_en": "Bold datáfono/POS channel credits this account in the real books "
                    "(BV-POS1685… asientos, Jan 2026). No 4305 family exists in the chart. "
                    "414515 TRANSPORTE stays for FE transport sales (FV-FE7xxx).",
    },
    {
        "key": "2805xx Ingresos recibidos por anticipado",
        "puc": "280505",
        "rule_tag": "deferred-revenue",
        "alegra_id": "5191",  # verified live chart 2026-09-18: Avances y anticipo de clientes, parent 5034, liability
        "label_es": "Ingresos recibidos por anticipado (280505)",
        "label_en": "Deferred revenue received in advance (280505)",
        "basis_es": "EX-J07-12 disposition cita '280505' (RC-11507/11560, diferimiento "
                    "de link-pagos Bold agosto).",
        "basis_en": "EX-J07-12 disposition cites '280505' (RC-11507/11560, Bold "
                    "link-payment deferral booked in August).",
    },
    {
        "key": "5305xx Comisiones y tarifas (Bold)",
        "puc": "530505",
        "rule_tag": "bold-fees",
        "alegra_id": "5166",  # verified live chart 2026-09-18: gastos bancario, parent 5165, expense
        "label_es": "Gastos bancarios — Bold fees neteados (530505)",
        "label_en": "Bank charges — Bold fees netted (530505)",
        "basis_es": "Tratamiento real del neteo mensual Bold: CC-AC-336 (2026-01-31) "
                    "Dr 530505 gastos bancario 642,931 / retefuente e ICA / Cr 111020 "
                    "961,115. No existe cuenta 'comisiones' en el catálogo.",
        "basis_en": "Actual monthly Bold netting: CC-AC-336 (2026-01-31) Dr 530505 "
                    "gastos bancario 642,931 / withholdings / Cr 111020 961,115. No "
                    "'comisiones' account exists in the chart.",
    },
    {
        "key": "5305xx Gastos bancarios (GMF)",
        "puc": "51159505",
        "rule_tag": "gmf",
        "alegra_id": "5171",  # verified live chart 2026-09-18: 4 X 1000 (aux nivel), parent 5170, expense
        "label_es": "GMF 4x1000 (51159505)",
        "label_en": "GMF 4 per 1000 (51159505)",
        "basis_es": "La cuenta real del GMF: '4 X 1000' (51159505), debitada mensualmente "
                    "en los cierres CC-AC-337/338, 348/349, 399, 402, 459… (96 usos). "
                    "El 530515 no existe.",
        "basis_en": "The real GMF account: '4 X 1000' (51159505), debited monthly in the "
                    "CC-AC-337/338, 348/349, 399, 402, 459… closes (96 uses). No 530515.",
    },
    {
        "key": "51xxxx Gastos por clasificar",
        "puc": "519595",
        "rule_tag": "suspense-expense",
        "alegra_id": "5182",  # verified live chart 2026-09-18: otros gastos y ajustes, parent 5106, expense
        "label_es": "Otros gastos y ajustes (519595) — imputación genérica de gastos",
        "label_en": "Other expenses and adjustments (519595) — generic expense imputation",
        "basis_es": "Catch-all real de la empresa para gastos de proveedor sin cuenta "
                    "propia (FP-7542 117,647; FP-8101). 519590 es 'no deducible' "
                    "(no aplica como clasificador); no existe cuenta suspense formal.",
        "basis_en": "The company's real provider-expense catch-all (FP-7542 117,647; "
                    "FP-8101). 519590 is 'non-deductible' (not a classifier); no formal "
                    "suspense account exists in the chart.",
    },
    {
        "key": "2205xx Cuentas por pagar",
        "puc": "2205",
        "rule_tag": "ap",
        "alegra_id": "5033",  # verified live chart 2026-09-18: Cuentas por pagar a proveedores (mayor/grupo), parent 5032, liability — use-field confirm pending
        "label_es": "Cuentas por pagar a proveedores (2205)",
        "label_en": "Accounts payable — suppliers (2205)",
        "basis_es": "Sonata contabiliza en el padre 2205 (2463 usos; FP-7433/7427…); "
                    "el 220505 no tiene ni un uso.",
        "basis_en": "Sonata books to parent 2205 (2463 uses; FP-7433/7427…); 220505 has "
                    "zero uses.",
    },
    {
        "key": "5105xx Sueldos y prestaciones sociales",
        "puc": "510506",
        "rule_tag": "payroll-expense",
        "alegra_id": "5078",  # verified live chart 2026-09-18: Sueldos, parent 5077, expense — also = entry.id in comp 4022 (journals cross-check)
        "label_es": "Sueldos y prestaciones sociales (510506 Sueldos)",
        "label_en": "Salaries and social benefits (510506 Salaries)",
        "basis_es": "je_data OJ-4 contabiliza 510506 Sueldos; la nómina PILA del mes "
                    "(EXP-01) se causa contra este grupo.",
        "basis_en": "je_data OJ-4 books 510506 Sueldos; the month's PILA payroll "
                    "(EXP-01) accrues to this group.",
    },
    {
        "key": "250505xx Salarios y prestaciones por pagar",
        "puc": "250505",
        "rule_tag": "payroll-payable",
        "alegra_id": "5038",  # verified live chart 2026-09-18: Salarios y prestaciones sociales, parent 5037, liability
        "label_es": "Salarios y prestaciones por pagar (250505)",
        "label_en": "Salaries and social benefits payable (250505)",
        "basis_es": "je_data OJ-4 acredita '250505 Salarios y prestaciones sociales' "
                    "(contrapartida del 5105).",
        "basis_en": "je_data OJ-4 credits '250505 Salarios y prestaciones sociales' "
                    "(the 5105 counterpart).",
    },
]

#: Entity ids that share this map (canonical DB id + CLI slug).
SONATA_MAP_ENTITY_IDS = ("sonata-001", "tayrona")


def pending_slots() -> list[str]:
    """Keys whose alegra_id is still None — the seeder refuses to write while
    any slot is pending (atomic map)."""
    return [str(e["key"]) for e in SONATA_MAP_ENTRIES if not e.get("alegra_id")]


def seed_account_map(db_connect, entity_ids=SONATA_MAP_ENTITY_IDS) -> dict[str, Any]:
    """Idempotent seed of the Sonata account_map (one row per key per entity).

    Atomicity: writes NOTHING while any alegra_id is unresolved — a
    half-real map must never reach company_rules (a poster would then send a
    PUC string as an Alegra account id and mistpost silently). Match on
    rule_id; a row the user already edited is never overwritten.

    Returns {"inserted": n, "pending": m}.
    """
    pending = pending_slots()
    if pending:
        return {"inserted": 0, "pending": len(pending), "pending_keys": pending}

    inserted = 0
    with db_connect() as conn:
        for entity_id in entity_ids:
            for e in SONATA_MAP_ENTRIES:
                rule_id = f"am-{e['rule_tag']}-{entity_id}"
                existing = conn.execute(
                    "SELECT rule_id FROM company_rules WHERE rule_id = ?",
                    (rule_id,),
                ).fetchone()
                if existing:
                    continue
                mapping = json.dumps({e["key"]: e["alegra_id"]}, ensure_ascii=False)
                es = (f"Mapa de cuentas: {e['key']} → {e['alegra_id']} "
                      f"({e['label_es']}). {e['basis_es']}")
                en = (f"Account map: {e['key']} → {e['alegra_id']} "
                      f"({e['label_en']}). {e['basis_en']}")
                conn.execute(
                    """
                    INSERT INTO company_rules
                        (rule_id, entity_id, rule_text, rule_text_es, rule_text_en,
                         category, source, audit_tag, linked_exception_id, created_by,
                         active)
                    VALUES (?, ?, ?, ?, ?, 'account_map', 'seed', NULL, NULL, 'seed', 1)
                    """,
                    (rule_id, entity_id, mapping, es, en),
                )
                inserted += 1
    return {"inserted": inserted, "pending": 0}


def resolve_alegra_ids(chart_rows: list[dict[Any, Any]],
                       entries=SONATA_MAP_ENTRIES) -> dict[str, str]:
    """Fill alegra_id on the entries from a chart-of-accounts payload.

    `chart_rows` is the parsed GET /accounts response (each row: id, name,
    code — whatever the transport returned). Matching is by PUC `code` first,
    then by a normalized `name` contains the code. Returns {key: alegra_id}
    for every socket that resolved; the caller is expected to assign them
    back (or to log the gaps). Never invents an id.
    """
    by_code: dict[str, str] = {}
    names: dict[str, str] = {}
    for row in chart_rows:
        if not isinstance(row, dict):
            continue
        aid = row.get("id")
        if aid is None:
            continue
        code = str(row.get("code") or "").strip()
        if code:
            by_code.setdefault(code, str(aid))
        name = str(row.get("name") or "")
        if name:
            names[str(aid)] = name

    resolved: dict[str, str] = {}
    for e in entries:
        target = str(e.get("puc") or "")
        aid = by_code.get(target)
        if aid is None:
            # chart rows may carry the code inside the name ('1105 111015 …')
            for code, cand in by_code.items():
                if code == target:
                    aid = cand
                    break
            if aid is None:
                for a, name in names.items():
                    if target in name.split():
                        aid = a
                        break
        if aid is not None:
            resolved[e["key"]] = str(aid)
    return resolved


def _pending_report() -> str:
    return ", ".join(pending_slots()) or "none"


if __name__ == "__main__":
    import sqlite3

    db = "sonata_mas_001.sqlite"

    def _connect():
        return sqlite3.connect(db)

    print(f"pending alegra_id slots: {_pending_report()}")
    print(seed_account_map(_connect))