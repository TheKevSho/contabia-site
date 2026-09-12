"""Standing Tayrona / sonata-001 company-config rules.

Idempotent seed. Called from main.py on startup so Configuración → Reglas
lists the real standing decisions instead of the Cantamar mock.
Never overwrites a rule the user already edited (match on rule_id).

BILINGUAL (2026-09-12): every rule carries rule_text_es + rule_text_en. The
legacy `rule_text` column stays in step with the Spanish rendition so anything
reading the old column keeps working. `backfill_rule_translations` repairs rows
that were seeded before the bilingual columns existed — the live Railway volume
already holds 10 Spanish-only rows, so an insert-if-missing seed alone would
leave them unilingual forever.
"""
from __future__ import annotations

STANDING_RULES = [
    {
        "rule_id": "CR-GYG-NET",
        "rule_text_es": (
            "GetYourGuide se factura NETO: comisión ~30% como línea de descuento "
            "en la FE (p.ej. FE8573). No generar documento soporte sobre la comisión. "
            "IVA 0. Standing — no reabrir como excepción cada mes."
        ),
        "rule_text_en": (
            "GetYourGuide is invoiced NET: ~30% commission as a discount line on "
            "the invoice (e.g. FE8573). Do not raise a documento soporte on the "
            "commission. IVA 0. Standing — do not reopen as an exception every month."
        ),
        "category": "treatment",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-J07-14",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-VIATOR-NET",
        "rule_text_es": (
            "Viator se factura NETO: comisión como línea de descuento en la FE "
            "(p.ej. FE8572). No DS sobre comisión. IVA 0. Standing."
        ),
        "rule_text_en": (
            "Viator is invoiced NET: commission as a discount line on the invoice "
            "(e.g. FE8572). No documento soporte on the commission. IVA 0. Standing."
        ),
        "category": "treatment",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-J07-15",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-IVA-EXCLUIDO",
        "rule_text_es": (
            "Actividad de paseos en yate: tratamiento IVA excluido (Art. 476 ET) "
            "para este cliente. IVA de compras se gasta (511570), no se acredita. "
            "Decisión local — no propagar a otros clientes."
        ),
        "rule_text_en": (
            "Yacht-tour activity: IVA-excluded treatment (Art. 476 ET) for this "
            "client. Purchase IVA is expensed (511570), not credited. Local "
            "decision — do not propagate to other clients."
        ),
        "category": "tax",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-5.5",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-ART35-NO",
        "rule_text_es": (
            "No imputar interés presuntivo Art. 35 ET sobre CxC socios "
            "(Kevin / Nicolás). Decisión de compañía #14. Revelar, no postear."
        ),
        "rule_text_en": (
            "Do not impute Art. 35 ET presumptive interest on shareholder "
            "receivables (Kevin / Nicolás). Company decision #14. Disclose, do not post."
        ),
        "category": "tax",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-12.3",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-ART128-NO-PACTO",
        "rule_text_es": (
            "No hay pactos firmados Art. 128 CST para Cristiam/Carlos/Raúl/Ovier. "
            "Bonos son constitutivos de salario por defecto — contingencia a revelar, "
            "no pasivo a postear, hasta que exista pacto."
        ),
        "rule_text_en": (
            "No signed Art. 128 CST agreements for Cristiam/Carlos/Raúl/Ovier. "
            "Bonuses are salary-constitutive by default — a contingency to disclose, "
            "not a liability to post, until an agreement exists."
        ),
        "category": "payroll",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-9.4",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-CC-VESSEL",
        "rule_text_es": (
            "Centro de costos por embarcación (Sonata Mas / Anna Leeza / Dragon Lady) "
            "según muelle o descripción del documento. Default cuando el proveedor "
            "o el ítem lo indiquen. Prerrequisito de P&L por nave."
        ),
        "rule_text_en": (
            "Cost center per vessel (Sonata Mas / Anna Leeza / Dragon Lady) based on "
            "the dock or the document description. Default when the vendor or the "
            "line item indicates it. Prerequisite for P&L by vessel."
        ),
        "category": "cost_center",
        "source": "client_choice",
        "audit_tag": None,
        "linked_exception_id": "EX-J07-08",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-BOLD-PREPAY",
        "rule_text_es": (
            "Link-pago Bold de clientes cuyo viaje es posterior al mes: diferir a "
            "2805 (ingresos recibidos por anticipado) y reconocer ingreso el mes "
            "en que se presta el servicio. Bidireccional, todos los canales. "
            "Datáfono POS del mes se queda en ingreso."
        ),
        "rule_text_en": (
            "Bold payment links from customers whose trip falls after the month: "
            "defer to 2805 (revenue received in advance) and recognise revenue in "
            "the month the service is delivered. Bidirectional, all channels. The "
            "month's POS card terminal stays in revenue."
        ),
        "category": "revenue",
        "source": "motor_fix",
        "audit_tag": None,
        "linked_exception_id": "EX-J07-12",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-ABONO-KEVIN",
        "rule_text_es": (
            "Abonos de Kevin a la embarcación reducen el pasivo con el socio "
            "(decisión #6), no se registran como ingreso ni como aporte de capital."
        ),
        "rule_text_en": (
            "Kevin's payments into the vessel reduce the liability to the partner "
            "(decision #6); they are not recorded as revenue nor as a capital contribution."
        ),
        "category": "classification",
        "source": "client_choice",
        "audit_tag": None,
        "linked_exception_id": "EX-12.7",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-VESSEL-BOOK",
        "rule_text_es": (
            "El valor en libros de las embarcaciones en Alegra no se reexpresa. "
            "La foto económica (FMV / anticipos) vive en la vista sombra "
            "(shadow view), no en los estados estatutarios."
        ),
        "rule_text_en": (
            "The book value of the vessels in Alegra is not restated. The economic "
            "picture (FMV / advances) lives in the shadow view, not in the "
            "statutory statements."
        ),
        "category": "assets",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-12.1",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-CREW-DS-RF",
        "rule_text_es": (
            "Documentos soporte a capitanes / tripulación (Raúl Amaya, Johan Torres, "
            "Ovier Gámez, Víctor Cera, Daniel Alemán y similares) ≥ 10 UVT: aplicar "
            "retefuente de honorarios 10% (precedente enero). Una sola regla, no "
            "una excepción por pago."
        ),
        "rule_text_en": (
            "Documentos soporte to captains / crew (Raúl Amaya, Johan Torres, Ovier "
            "Gámez, Víctor Cera, Daniel Alemán and similar) ≥ 10 UVT: apply 10% "
            "honorarios withholding (January precedent). One single rule, not one "
            "exception per payment."
        ),
        "category": "retention",
        "source": "motor_fix",
        "audit_tag": None,
        "linked_exception_id": "EX-5.1",
        "created_by": "seed",
    },
]


# Exceptions the standing rules already answer — hide from the live July
# "needs a decision" queue. Baseline (Jan–Jun) rows stay visible as history.
RULE_HANDLED_EXCEPTION_IDS = {
    "EX-J07-08",   # CR-CC-VESSEL
    "EX-J07-12",   # CR-BOLD-PREPAY
    "EX-J07-14",   # CR-GYG-NET / explained
    "EX-5.5",
    "EX-10.3",
    "EX-12.3",
    "EX-12.7",
    "EX-12.1",
    "EX-9.4",
    "EX-11.1",
}


def seed_standing_rules(db_connect, entity_id: str = "sonata-001") -> int:
    """Insert missing standing rules, then repair any that predate the
    bilingual columns. Returns the number of rows inserted."""
    inserted = 0
    with db_connect() as conn:
        for rule in STANDING_RULES:
            existing = conn.execute(
                "SELECT rule_id FROM company_rules WHERE rule_id = ?",
                (rule["rule_id"],),
            ).fetchone()
            if existing:
                continue
            conn.execute(
                """
                INSERT INTO company_rules
                    (rule_id, entity_id, rule_text, rule_text_es, rule_text_en,
                     category, source, audit_tag, linked_exception_id, created_by,
                     active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    rule["rule_id"],
                    entity_id,
                    rule["rule_text_es"],   # legacy column mirrors the Spanish
                    rule["rule_text_es"],
                    rule["rule_text_en"],
                    rule["category"],
                    rule["source"],
                    rule["audit_tag"],
                    rule["linked_exception_id"],
                    rule["created_by"],
                ),
            )
            inserted += 1
    backfill_rule_translations(db_connect, entity_id)
    return inserted


def backfill_rule_translations(db_connect, entity_id: str = "sonata-001") -> int:
    """Fill rule_text_es / rule_text_en on seeded rows that predate the
    bilingual columns. A rule the user edited by hand (its text no longer
    matches the seed, or it has no seed entry) is left alone — only a blank
    column on a known seed rule gets filled."""
    filled = 0
    by_id = {r["rule_id"]: r for r in STANDING_RULES}
    with db_connect() as conn:
        rows = conn.execute(
            "SELECT rule_id, rule_text, rule_text_es, rule_text_en "
            "FROM company_rules WHERE entity_id = ?",
            (entity_id,),
        ).fetchall()
        for row in rows:
            seed = by_id.get(row["rule_id"])
            if not seed:
                continue
            sets, vals = [], []
            if not (row["rule_text_es"] or "").strip():
                sets.append("rule_text_es = ?"); vals.append(seed["rule_text_es"])
            if not (row["rule_text_en"] or "").strip():
                sets.append("rule_text_en = ?"); vals.append(seed["rule_text_en"])
            if not sets:
                continue
            vals.append(row["rule_id"])
            conn.execute(
                f"UPDATE company_rules SET {', '.join(sets)} WHERE rule_id = ?", vals
            )
            filled += 1
    return filled
