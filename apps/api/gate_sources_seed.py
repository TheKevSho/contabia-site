#!/usr/bin/env python3
"""Per-entity APPLICABLE-SOURCES config for the pre-close gate — seeded like
the account_map.

WHY THIS EXISTS
The gate used to ask one flat question per item: "is a file matching these
patterns anywhere in the data dir?" For Sonata Mas that produced two kinds of
lie, both observed on the July close:

  FALSE MISS — the evidence existed but sat outside the month bundle. July's
  PILA lives in payroll/, the July exception register in the staged intake
  bundle, and the PMS export (RESERVAS 2026.xlsx) in the intake bundle too.
  A month-scoped scan called all three "missing" and blocked the close, so the
  operator was told to go ask the client for documents already in the vault.

  FALSE PASS — ota_booking's pattern is ["booking"], which FareHarbor's
  generic `Custom-bookings-report--*.csv` matches. That file is a
  GetYourGuide/Viator affiliate report (its own `Affiliate` column says so).
  The gate therefore reported Booking.com as present for an entity that has no
  Booking.com account. Likewise pms carries doc_types=["report"], so any
  canonical doc typed "report" satisfied "PMS data export".

Neither is a code bug in the matching loop; both are missing CONFIGURATION.
Per entity, per item, the close needs to record:
  applicable    — does this business even have this source? (client's call)
  file_pats     — what a real signal looks like for THIS entity
  doc_types     — the index-side signal, narrowed when the default is loose
  period_scope  — "period" (a file named for the month) or "year" (a running
                  export such as RESERVAS 2026.xlsx, where the period lives as
                  rows, not in the filename)
  provisional   — the file on disk is present but is NOT this period's data
  basis_es/_en  — why, in one sentence, so the gate can print ⊘ with a reason
                  instead of an unexplained ❌

Seeded into company_rules (category='gate_sources'), one row per item — the
same table and idiom as the account_map: rule_text holds the machine config
(JSON), rule_text_es/_en hold the human basis. An entity with no seeded rows
falls back to strict legacy behaviour (every item applicable, default patterns),
so nothing silently loosens for a client nobody configured.

Stdlib only. Idempotent: INSERT OR REPLACE keyed on rule_id, safe to call on
every app start (main.py seeds it next to seed_account_map).
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Optional

CATEGORY = "gate_sources"
RULE_PREFIX = "gate-src"
SONATA_GATE_ENTITY_IDS = ("sonata-001", "tayrona")
DB_PATH = Path(os.environ.get("CONTABIA_DB_PATH",
                              Path(__file__).parent / "sonata_mas_001.sqlite"))

# Verified 2026-09-19 against _Brain/tayrona-sailing/raw-accounting:
#   booking / airbnb / hostelworld / despegar -> 0 hits in books, statements,
#   ledgers or the vendor sweep. The "booking" hits were FareHarbor's
#   Custom-bookings-report--*.csv (Affiliate: GetYourGuide / TripAdvisor
#   Experiences-Viator), i.e. NOT Booking.com.
#   RESERVAS 2026.xlsx present (intake bundle) -> real PMS signal, year-scoped.
SONATA_GATE_SOURCE_ENTRIES: list[dict[str, Any]] = [
    {
        "item": "bank_statement",
        "applicable": True,
        "period_scope": "period",
        "file_pats": None,
        "doc_types": None,
        "provisional": False,
        "basis_es": ("Cuenta bancaria activa (Bancolombia 78100001780 y fondo "
                     "digital BBVA): el extracto del período es obligatorio."),
        "basis_en": ("Active bank accounts (Bancolombia 78100001780 and the BBVA "
                     "digital fund): the period statement is required."),
    },
    {
        "item": "card_statement",
        "applicable": True,
        "period_scope": "period",
        "file_pats": None,
        "doc_types": None,
        "provisional": False,
        "basis_es": ("Tarjeta corporativa más recaudo por pasarelas (Bold, "
                     "PayPal): el extracto del período es obligatorio."),
        "basis_en": ("Corporate card plus gateway collections (Bold, PayPal): "
                     "the period statement is required."),
    },
    {
        "item": "payroll",
        "applicable": True,
        "period_scope": "period",
        "file_pats": ["planilla", "pila", "nomina", "nómina", "detalleplanilla"],
        "doc_types": None,
        "provisional": False,
        "basis_es": ("Hay nómina: la PILA del período llega en payroll/ "
                     "(DetallePlanilla), fuera del paquete del mes, por eso el "
                     "barrido debe recorrer el árbol y no sólo la carpeta del mes."),
        "basis_en": ("Payroll exists: the period PILA lands in payroll/ "
                     "(DetallePlanilla), outside the month bundle — hence the "
                     "scan must walk the tree, not just the month folder."),
    },
    {
        "item": "ota_booking",
        "applicable": False,
        "period_scope": "period",
        "file_pats": ["booking.com", "booking_com", "bookingcom"],
        "doc_types": [],
        "provisional": False,
        "basis_es": ("No aplica: Sonata no tiene cuenta ni actividad en "
                     "Booking.com (cero coincidencias en libros, extractos y "
                     "barrido de proveedores, 2026-09-19). El patrón antiguo "
                     "'booking' marcaba falso positivo contra el reporte "
                     "genérico de FareHarbor."),
        "basis_en": ("Not applicable: Sonata has no Booking.com account or "
                     "activity (zero hits in books, statements and the vendor "
                     "sweep, 2026-09-19). The old 'booking' pattern was a false "
                     "positive against FareHarbor's generic bookings report."),
    },
    {
        "item": "ota_airbnb",
        "applicable": False,
        "period_scope": "period",
        "file_pats": None,
        "doc_types": [],
        "provisional": False,
        "basis_es": "No aplica: cero coincidencias de Airbnb (2026-09-19).",
        "basis_en": "Not applicable: zero Airbnb hits (2026-09-19).",
    },
    {
        "item": "ota_hostelworld",
        "applicable": False,
        "period_scope": "period",
        "file_pats": None,
        "doc_types": [],
        "provisional": False,
        "basis_es": "No aplica: cero coincidencias de Hostelworld (2026-09-19).",
        "basis_en": "Not applicable: zero Hostelworld hits (2026-09-19).",
    },
    {
        "item": "ota_despegar",
        "applicable": False,
        "period_scope": "period",
        "file_pats": None,
        "doc_types": [],
        "provisional": False,
        "basis_es": "No aplica: cero coincidencias de Despegar (2026-09-19).",
        "basis_en": "Not applicable: zero Despegar hits (2026-09-19).",
    },
    {
        "item": "ota_other",
        "applicable": True,
        "period_scope": "period",
        "file_pats": ["getyourguide", "gyg", "viator", "fareharbor",
                      "settlement"],
        "doc_types": None,
        "provisional": True,
        "basis_es": ("Sí aplica: las OTAs en uso son GetYourGuide y Viator "
                     "(más FareHarbor como motor). PROVISIONAL: los archivos "
                     "OTA-GYG/Viator que están en disco son byte-idénticos a "
                     "los de junio (md5 19b47deb… / 6ad4f4d4…) — el gate pasa "
                     "por presencia, pero los montos NO son de julio. Hay que "
                     "recolectar los reportes reales de julio antes de postear. "
                     "Patrón acotado: se quita el token suelto 'ota' porque hacía "
                     "falso positivo con 'Cuota' "
                     "(Detalle_Cuota_Bancolombia-7810099111_2026-07.xlsx)."),
        "basis_en": ("Applies: the OTAs in use are GetYourGuide and Viator "
                     "(plus FareHarbor as the booking engine). PROVISIONAL: the "
                     "OTA-GYG/Viator files on disk are byte-identical to June's "
                     "(md5 19b47deb… / 6ad4f4d4…) — the gate passes on presence, "
                     "but the amounts are NOT July's. Collect the real July "
                     "reports before posting. Pattern narrowed: the bare token "
                     "'ota' is dropped — it false-positived on 'Cuota' "
                     "(Detalle_Cuota_Bancolombia-7810099111_2026-07.xlsx)."),
    },
    {
        "item": "pms",
        "applicable": True,
        "period_scope": "year",
        "file_pats": ["lobby", "pms", "reservas", "manifest",
                      "availabilities"],
        "doc_types": [],
        "provisional": False,
        "basis_es": ("Sí aplica: no hay LobbyPMS; el sistema de reservas de "
                     "registro es FareHarbor y su export vive en el bundle de "
                     "ingesta (RESERVAS 2026.xlsx), anual — de ahí period_scope "
                     "'year'. Se descarta 'dashboard' (la carpeta dashboard/ "
                     "guarda pnl-data.json, un artefacto financiero, no un "
                     "export de PMS) y doc_types 'report' por demasiado amplio. "
                     "Se quita 'fareharbor' (motor de reservas, no export de "
                     "PMS; PayPal_FareHarbor_Settlements es una liquidación)."),
        "basis_en": ("Applies: there is no LobbyPMS; the booking system of "
                     "record is FareHarbor and its export lives in the intake "
                     "bundle (RESERVAS 2026.xlsx), annual — hence period_scope "
                     "'year'. 'dashboard' is dropped (dashboard/ holds "
                     "pnl-data.json, a financial artifact, not a PMS export) "
                     "and doc_types 'report' is dropped as too broad. "
                     "'fareharbor' is dropped (booking engine, not a PMS "
                     "export; PayPal_FareHarbor_Settlements is a settlement)."),
    },
    {
        "item": "intake_reviewed",
        "applicable": True,
        "period_scope": "period",
        "file_pats": None,
        "doc_types": None,
        "provisional": False,
        "basis_es": ("El registro de excepciones de julio está en el bundle de "
                     "ingesta (_downloads-intake-2026-08-01/exception_register_"
                     "2026-07.csv), fuera del paquete del mes."),
        "basis_en": ("July's exception register sits in the intake bundle "
                     "(_downloads-intake-2026-08-01/exception_register_2026-07"
                     ".csv), outside the month bundle."),
    },
]


def rule_id(entity_id: str, item: str) -> str:
    return f"{RULE_PREFIX}:{entity_id}:{item}"


def entry_payload(entry: dict[str, Any]) -> str:
    """The machine config stored in company_rules.rule_text (compact JSON)."""
    return json.dumps(
        {
            "kind": CATEGORY,
            "item": entry["item"],
            "applicable": bool(entry["applicable"]),
            "period_scope": entry.get("period_scope", "period"),
            "file_pats": entry.get("file_pats"),
            "doc_types": entry.get("doc_types"),
            "provisional": bool(entry.get("provisional")),
        },
        ensure_ascii=False, sort_keys=True,
    )


def entry_text_es(entry: dict[str, Any]) -> str:
    return f"Fuentes aplicables — {entry['item']}: {entry['basis_es']}"


def entry_text_en(entry: dict[str, Any]) -> str:
    return f"Applicable sources — {entry['item']}: {entry['basis_en']}"


def entry_basis(entry: dict[str, Any]) -> str:
    """The bare 'why', without the ES/EN prefix — what the gate cites."""
    return entry.get("basis_en") or entry.get("basis_es") or ""


def seed_gate_sources(db_connect, entity_ids=SONATA_GATE_ENTITY_IDS) -> dict[str, Any]:
    """Idempotent seed of the applicable-sources config, one row per item per
    entity. INSERT OR REPLACE on rule_id, so re-running (e.g. on every app
    start) converges instead of duplicating."""
    inserted = 0
    per_entity: dict[str, int] = {}
    with db_connect() as conn:
        for entity_id in entity_ids:
            n = 0
            for entry in SONATA_GATE_SOURCE_ENTRIES:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO company_rules
                        (rule_id, entity_id, rule_text, rule_text_es, rule_text_en,
                         category, source, audit_tag, linked_exception_id, created_by,
                         active)
                    VALUES (?, ?, ?, ?, ?, ?, 'client_choice', NULL, NULL, 'seed', 1)
                    """,
                    (
                        rule_id(entity_id, entry["item"]),
                        entity_id,
                        entry_payload(entry),
                        entry_text_es(entry),
                        entry_text_en(entry),
                        CATEGORY,
                    ),
                )
                n += 1
            per_entity[entity_id] = n
            inserted += n
    return {"inserted": inserted, "per_entity": per_entity,
            "items": [e["item"] for e in SONATA_GATE_SOURCE_ENTRIES]}


def _strip_prefix(text: Optional[str]) -> str:
    """'Applicable sources — item: <basis>' -> '<basis>' (keep it human)."""
    if not text:
        return ""
    return text.split(": ", 1)[-1] if ": " in text else text


def _columns(conn) -> set[str]:
    return {r[1] for r in conn.execute("PRAGMA table_info(company_rules)")}


def load_gate_sources(entity: str, db_path: Optional[Path] = None) -> dict[str, dict]:
    """-> {item: config} for one entity. Empty dict means "not configured",
    which the gate must treat as strict legacy behaviour (never as "nothing
    applies"). Never raises: a broken/absent config falls back to legacy."""
    path = Path(db_path or DB_PATH)
    if not path.exists():
        return {}
    try:
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        try:
            cols = _columns(conn)
            if "category" not in cols:
                return {}
            where = "entity_id = ? AND category = ?"
            if "active" in cols:
                where += " AND active = 1"
            rows = list(conn.execute(
                f"SELECT rule_id, rule_text, rule_text_es, rule_text_en "
                f"FROM company_rules WHERE {where}",
                (entity, CATEGORY),
            ))
        finally:
            conn.close()
    except Exception as exc:  # never block a close on a config read
        print(f"warning: gate_sources config unreadable ({exc}); "
              "falling back to strict legacy gate", file=sys.stderr)
        return {}

    out: dict[str, dict] = {}
    for row in rows:
        try:
            cfg = json.loads(row["rule_text"])
        except (TypeError, ValueError):
            continue
        item = cfg.get("item") or str(row["rule_id"]).rsplit(":", 1)[-1]
        cfg["item"] = item
        # the human "why" travels with the machine config so the gate can cite
        # it verbatim in the report instead of a bare key
        cfg["basis_es"] = _strip_prefix(row["rule_text_es"])
        cfg["basis_en"] = _strip_prefix(row["rule_text_en"])
        out[item] = cfg
    return out


def describe(entity: str, db_path: Optional[Path] = None) -> str:
    cfg = load_gate_sources(entity, db_path)
    if not cfg:
        return (f"{entity}: no gate_sources config seeded — the gate runs "
                "strict legacy (every item applicable).")
    out = [f"gate_sources — {entity} ({len(cfg)} items)"]
    for item in sorted(cfg):
        c = cfg[item]
        state = "applies" if c.get("applicable") else "NOT applicable"
        if c.get("provisional"):
            state += " (provisional)"
        pats = c.get("file_pats")
        out.append(f"  {item:18s} {state:26s} scope={c.get('period_scope')}"
                   + (f" pats={pats}" if pats else ""))
    return "\n".join(out)


def _db_connect():
    conn = sqlite3.connect(str(DB_PATH))
    return conn


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed / inspect the pre-close gate's applicable-sources config")
    parser.add_argument("--entity", default=None,
                        help="Inspect one entity (default: all seeded entities)")
    parser.add_argument("--seed", action="store_true",
                        help="Write the config into company_rules (idempotent)")
    parser.add_argument("--print", dest="show", action="store_true",
                        help="Print what the gate will read")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    args = parser.parse_args()

    if args.seed:
        res = seed_gate_sources(_db_connect)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0

    entities = [args.entity] if args.entity else list(SONATA_GATE_ENTITY_IDS)
    for e in entities:
        print(describe(e, args.db))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())