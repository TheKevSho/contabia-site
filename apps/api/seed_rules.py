"""Standing Tayrona / sonata-001 company-config rules.

Idempotent seed. Called from main.py on startup so Configuración → Reglas
lists the real standing decisions instead of the Cantamar mock.
Never overwrites a rule the user already edited (match on rule_id).
"""
from __future__ import annotations

STANDING_RULES = [
    {
        "rule_id": "CR-GYG-NET",
        "rule_text": (
            "GetYourGuide se factura NETO: comisión ~30% como línea de descuento "
            "en la FE (p.ej. FE8573). No generar documento soporte sobre la comisión. "
            "IVA 0. Standing — no reabrir como excepción cada mes."
        ),
        "category": "treatment",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-J07-14",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-VIATOR-NET",
        "rule_text": (
            "Viator se factura NETO: comisión como línea de descuento en la FE "
            "(p.ej. FE8572). No DS sobre comisión. IVA 0. Standing."
        ),
        "category": "treatment",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-J07-15",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-IVA-EXCLUIDO",
        "rule_text": (
            "Actividad de paseos en yate: tratamiento IVA excluido (Art. 476 ET) "
            "para este cliente. IVA de compras se gasta (511570), no se acredita. "
            "Decisión local — no propagar a otros clientes."
        ),
        "category": "tax",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-5.5",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-ART35-NO",
        "rule_text": (
            "No imputar interés presuntivo Art. 35 ET sobre CxC socios "
            "(Kevin / Nicolás). Decisión de compañía #14. Revelar, no postear."
        ),
        "category": "tax",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-12.3",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-ART128-NO-PACTO",
        "rule_text": (
            "No hay pactos firmados Art. 128 CST para Cristiam/Carlos/Raúl/Ovier. "
            "Bonos son constitutivos de salario por defecto — contingencia a revelar, "
            "no pasivo a postear, hasta que exista pacto."
        ),
        "category": "payroll",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-9.4",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-CC-VESSEL",
        "rule_text": (
            "Centro de costos por embarcación (Sonata Mas / Anna Leeza / Dragon Lady) "
            "según muelle o descripción del documento. Default cuando el proveedor "
            "o el ítem lo indiquen. Prerrequisito de P&L por nave."
        ),
        "category": "cost_center",
        "source": "client_choice",
        "audit_tag": None,
        "linked_exception_id": "EX-J07-08",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-BOLD-PREPAY",
        "rule_text": (
            "Link-pago Bold de clientes cuyo viaje es posterior al mes: diferir a "
            "2805 (ingresos recibidos por anticipado) y reconocer ingreso el mes "
            "en que se presta el servicio. Bidireccional, todos los canales. "
            "Datáfono POS del mes se queda en ingreso."
        ),
        "category": "revenue",
        "source": "motor_fix",
        "audit_tag": None,
        "linked_exception_id": "EX-J07-12",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-ABONO-KEVIN",
        "rule_text": (
            "Abonos de Kevin a la embarcación reducen el pasivo con el socio "
            "(decisión #6), no se registran como ingreso ni como aporte de capital."
        ),
        "category": "classification",
        "source": "client_choice",
        "audit_tag": None,
        "linked_exception_id": "EX-12.7",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-VESSEL-BOOK",
        "rule_text": (
            "El valor en libros de las embarcaciones en Alegra no se reexpresa. "
            "La foto económica (FMV / anticipos) vive en la vista sombra "
            "(shadow view), no en los estados estatutarios."
        ),
        "category": "assets",
        "source": "client_choice",
        "audit_tag": "informed_decline",
        "linked_exception_id": "EX-12.1",
        "created_by": "seed",
    },
    {
        "rule_id": "CR-CREW-DS-RF",
        "rule_text": (
            "Documentos soporte a capitanes / tripulación (Raúl Amaya, Johan Torres, "
            "Ovier Gámez, Víctor Cera, Daniel Alemán y similares) ≥ 10 UVT: aplicar "
            "retefuente de honorarios 10% (precedente enero). Una sola regla, no "
            "una excepción por pago."
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
                    (rule_id, entity_id, rule_text, category, source, audit_tag,
                     linked_exception_id, created_by, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    rule["rule_id"],
                    entity_id,
                    rule["rule_text"],
                    rule["category"],
                    rule["source"],
                    rule["audit_tag"],
                    rule["linked_exception_id"],
                    rule["created_by"],
                ),
            )
            inserted += 1
    return inserted
