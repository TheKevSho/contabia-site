#!/usr/bin/env python3
"""Tests for the per-entity applicable-sources config (gate_sources_seed.py)
and the config-aware pre-close gate (pre_close_gate.py).

The contract under test:
  - the config covers every gate item, for BOTH entity ids, idempotently;
  - an unconfigured entity keeps STRICT LEGACY behaviour (never loosened);
  - 'not applicable' is reported, never counted missing;
  - narrowed patterns kill the false pass — FareHarbor's generic bookings
    report must NOT satisfy the Booking.com item;
  - a year-scoped signal finds a running export (RESERVAS 2026.xlsx);
  - a provisional item (June data mislabelled July) does NOT satisfy the gate;
  - the scan is tree-aware and byte-equivalent to the old rglob on a flat dir.

Run:  pytest test_gate_sources.py -v
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import pre_close_gate as g
from gate_sources_seed import (CATEGORY, SONATA_GATE_ENTITY_IDS,
                               SONATA_GATE_SOURCE_ENTRIES, load_gate_sources,
                               seed_gate_sources)
from pre_close_gate import (GATE_ITEMS, check_data_availability, format_gate,
                            run_gate)
from test_account_map_seed import SCHEMA

PERIOD = "2026-07"
ITEM_KEYS = [it["key"] for it in GATE_ITEMS]
FILE_CFG = {e["item"]: dict(e) for e in SONATA_GATE_SOURCE_ENTRIES}


# --- fixtures ---------------------------------------------------------------

@pytest.fixture
def seeded_db(tmp_path):
    """A company_rules DB with the real config seeded for both entity ids."""
    p = tmp_path / "cfg.sqlite"
    conn = sqlite3.connect(str(p))
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    res = seed_gate_sources(lambda: sqlite3.connect(str(p)))
    return p, res


@pytest.fixture
def vault_like(tmp_path):
    """A miniature of the real vault tree: month bundle + topic dirs + a staged
    intake bundle + a root-level annual export."""
    d = tmp_path / "raw-accounting"
    (d / "2026-07").mkdir(parents=True)
    (d / "payroll").mkdir()
    (d / "_downloads-intake-2026-08-01").mkdir()
    (d / "2026-07" / "Bancolombia_0992_2026-07.xlsx").write_text("x")
    (d / "payroll" / "DetallePlanilla_38244858_2026_07_E.pdf").write_text("x")
    (d / "_downloads-intake-2026-08-01" / "exception_register_2026-07.csv").write_text("a,b\n")
    (d / "_downloads-intake-2026-08-01" / "RESERVAS 2026.xlsx").write_text("x")
    (d / "Custom-bookings-report--2026-07.csv").write_text("Booking ID,Affiliate\n")
    # the July-named OTA settlement: on disk, but it is June's data (provisional)
    (d / "2026-07" / "GetYourGuide_2026-07.xlsx").write_text("x")
    return d


# --- config shape -----------------------------------------------------------

def test_config_covers_every_gate_item_exactly_once():
    items = [e["item"] for e in SONATA_GATE_SOURCE_ENTRIES]
    assert sorted(items) == sorted(ITEM_KEYS)
    assert len(items) == len(set(items)), "duplicate item in the config"


def test_every_entry_carries_a_basis_and_a_valid_scope():
    for e in SONATA_GATE_SOURCE_ENTRIES:
        assert e.get("period_scope", "period") in ("period", "year"), e["item"]
        assert e["basis_es"].strip() and e["basis_en"].strip(), e["item"]
        assert e["basis_es"] != e["basis_en"], f"{e['item']}: basis not translated"
        if not e["applicable"]:
            assert e["basis_en"].lower().startswith("not applicable"), e["item"]


def test_config_records_the_two_evidence_backed_decisions():
    """The two entries that changed gate behaviour must keep their reason."""
    by_item = {e["item"]: e for e in SONATA_GATE_SOURCE_ENTRIES}
    # Booking.com: not applicable, and the old pattern is named as the defect
    assert by_item["ota_booking"]["applicable"] is False
    assert "booking" in by_item["ota_booking"]["basis_en"]
    assert by_item["ota_booking"]["file_pats"] == ["booking.com", "booking_com", "bookingcom"]
    # PMS is a running export -> year scope, not a month-token match
    assert by_item["pms"]["period_scope"] == "year"
    assert "reservas" in by_item["pms"]["file_pats"]
    # the July OTA reports on disk are June data -> provisional, and it BLOCKS
    assert by_item["ota_other"]["provisional"] is True


# --- seeding ----------------------------------------------------------------

def test_seed_round_trips_for_both_entity_ids(seeded_db):
    p, res = seeded_db
    assert res["inserted"] == len(ITEM_KEYS) * len(SONATA_GATE_ENTITY_IDS)
    for entity in SONATA_GATE_ENTITY_IDS:
        cfg = load_gate_sources(entity, p)
        assert sorted(cfg) == sorted(ITEM_KEYS), entity
        for item, c in cfg.items():
            assert c["kind"] == CATEGORY
            assert c["applicable"] is FILE_CFG[item]["applicable"]
            assert c.get("basis_en"), f"{entity}/{item} lost its basis"
            assert not c["basis_en"].startswith("Applicable sources")


def test_seed_is_idempotent(seeded_db):
    p, first = seeded_db
    before = load_gate_sources("tayrona", p)
    second = seed_gate_sources(lambda: sqlite3.connect(str(p)))
    after = load_gate_sources("tayrona", p)
    assert second["inserted"] == first["inserted"]
    assert before == after
    conn = sqlite3.connect(str(p))
    n = conn.execute("SELECT COUNT(*) FROM company_rules WHERE category = ?",
                     (CATEGORY,)).fetchone()[0]
    conn.close()
    assert n == len(ITEM_KEYS) * len(SONATA_GATE_ENTITY_IDS)


def test_unconfigured_entity_loads_as_empty(seeded_db):
    p, _ = seeded_db
    assert load_gate_sources("cantamar", p) == {}
    assert load_gate_sources("tayrona", p.parent / "nope.sqlite") == {}


# --- gate behaviour ---------------------------------------------------------

def test_legacy_false_pass_is_real(vault_like):
    """Proof the defect existed: unconfigured, FareHarbor's generic bookings
    report satisfies the Booking.com item."""
    r = check_data_availability("cantamar", PERIOD, vault_like,
                                db_path=vault_like.parent / "none.sqlite",
                                sources_config={})
    booking = next(c for c in r["checks"] if c["item"] == "ota_booking")
    assert booking["available"] is True
    assert booking["sources"] and "custom-bookings" in booking["sources"][0].lower()


def test_narrowed_pattern_kills_the_false_pass(vault_like):
    cfg = {"ota_booking": {"applicable": True,
                           "file_pats": ["booking.com", "booking_com", "bookingcom"],
                           "doc_types": []}}
    r = check_data_availability("tayrona", PERIOD, vault_like,
                                db_path=vault_like.parent / "none.sqlite",
                                sources_config=cfg)
    booking = next(c for c in r["checks"] if c["item"] == "ota_booking")
    assert booking["available"] is False
    assert "ota_booking" in r["missing"]


def test_not_applicable_is_reported_never_missing(vault_like):
    r = check_data_availability("tayrona", PERIOD, vault_like,
                                db_path=vault_like.parent / "none.sqlite",
                                sources_config=FILE_CFG)
    na = {n["item"] for n in r["not_applicable"]}
    assert na == {"ota_booking", "ota_airbnb", "ota_hostelworld", "ota_despegar"}
    assert not (na & set(r["missing"])), "a not-applicable item was counted missing"
    for c in r["checks"]:
        if c["item"] in na:
            assert c["available"] is True and c["applicable"] is False
            assert c["basis"], f"{c['item']} not-applicable without a basis"


def test_year_scope_finds_the_running_export(vault_like):
    """RESERVAS 2026.xlsx carries no month token: period scope misses it, the
    configured year scope finds it."""
    no_scope = check_data_availability("tayrona", PERIOD, vault_like,
                                       db_path=vault_like.parent / "none.sqlite",
                                       sources_config={})
    assert "pms" in no_scope["missing"]

    r = check_data_availability("tayrona", PERIOD, vault_like,
                                db_path=vault_like.parent / "none.sqlite",
                                sources_config=FILE_CFG)
    pms = next(c for c in r["checks"] if c["item"] == "pms")
    assert pms["available"] is True
    assert pms["period_scope"] == "year"
    assert "RESERVAS 2026.xlsx" in pms["sources"][0]


def test_provisional_present_file_does_not_satisfy_the_gate(vault_like):
    """The July-named OTA report is on disk, but it is June data: the gate must
    still fail, with its own reason (posting June revenue as July is the error
    the gate exists to stop)."""
    r = check_data_availability("tayrona", PERIOD, vault_like,
                                db_path=vault_like.parent / "none.sqlite",
                                sources_config=FILE_CFG)
    prov = {p["item"] for p in r["provisional"]}
    assert prov == {"ota_other"}
    assert "ota_other" in r["missing"]
    assert r["gate_passed"] is False
    check = next(c for c in r["checks"] if c["item"] == "ota_other")
    assert check["available"] is False and check["provisional"] is True
    assert "NOT this period" in r["verdict"] or "not this period" in r["verdict"]


def test_tree_aware_scan_finds_nested_and_staged_evidence(vault_like):
    r = check_data_availability("tayrona", PERIOD, vault_like,
                                db_path=vault_like.parent / "none.sqlite",
                                sources_config=FILE_CFG)
    pay = next(c for c in r["checks"] if c["item"] == "payroll")
    assert pay["available"] is True
    assert "payroll/DetallePlanilla" in pay["sources"][0]
    intake = next(c for c in r["checks"] if c["item"] == "intake_reviewed")
    assert intake["available"] is True
    assert "_downloads-intake-2026-08-01" in intake["sources"][0]


def test_flat_dir_scan_is_equivalent_to_the_legacy_rglob(vault_like):
    """The wrapper must not change what a flat scan sees."""
    legacy = []
    for p in sorted(Path(vault_like).rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(vault_like)).lower()
        if g._period_in_name(rel, PERIOD):
            legacy.append({"filename": p.name, "path": str(p)})
    new = g._scan_dir(vault_like, PERIOD)
    assert sorted(f["path"] for f in legacy) == sorted(f["path"] for f in new)
    assert sorted(f["filename"] for f in legacy) == sorted(f["filename"] for f in new)


def test_provenance_is_reported(vault_like):
    r = check_data_availability("tayrona", PERIOD, vault_like,
                                db_path=vault_like.parent / "none.sqlite",
                                sources_config=FILE_CFG)
    prov = r["provenance"]
    assert prov["shape"] in ("tree", "flat_dir")
    assert prov["roots"], "no provenance roots recorded"
    assert all({"root", "kind", "reason"} <= set(x) for x in prov["roots"])


def test_format_gate_renders_marks_without_crashing(seeded_db):
    """With the config seeded, the report shows the new marks: ⊘ not-applicable,
    ⏳ provisional, and the usual ✅/❌ availability marks."""
    p, _ = seeded_db
    r = run_gate("tayrona", PERIOD, mock=True, db_path=p)
    text = format_gate(r)
    assert "PHASE 3 — PRE-CLOSE GATE" in text
    for mark in ("⊘", "✅", "❌"):
        assert mark in text, f"missing mark {mark}"
    assert "not applicable —" in text
    assert "nothing copied" in text
    # ⏳ is the provisional mark; the mock corpus has no OTA file on disk, so
    # ota_other is simply missing here — the ⏳ path is covered by
    # test_provisional_present_file_does_not_satisfy_the_gate.
    assert "⏳" not in text or "PROVISIONAL" in text


def test_mock_run_still_fails_with_the_config_seeded(seeded_db):
    """The honest Tayrona-July shape survives the config: OTA/PMS still block."""
    p, _ = seeded_db
    r = run_gate("tayrona", PERIOD, mock=True, db_path=p)
    assert r["phase"] == "pre_close_gate"
    assert r["gate_passed"] is False
    blockers = " ".join(r["blockers"]).lower()
    assert "ota" in blockers and "pms" in blockers
    # the not-applicable items are surfaced as notices, not blockers
    notices = " ".join(r["notices"]).lower()
    assert "not-applicable" in notices and "booking" in notices
    assert "ota_booking" not in blockers


# --------------------------------------------------------------------------
# Registered-but-absent evidence (found by running the real July gate)
# --------------------------------------------------------------------------
CANON_DDL = """
CREATE TABLE IF NOT EXISTS canonical_documents (
    doc_id TEXT PRIMARY KEY, filename TEXT, path TEXT, vendor TEXT,
    doc_type TEXT, period TEXT
)
"""


def _register(p, **kw):
    conn = sqlite3.connect(str(p))
    conn.execute(CANON_DDL)
    conn.execute(
        "INSERT INTO canonical_documents (doc_id, filename, path, vendor, "
        "doc_type, period) VALUES (?,?,?,?,?,?)",
        (kw["doc_id"], kw["filename"], kw["path"], kw.get("vendor", ""),
         kw["doc_type"], kw.get("period", PERIOD)),
    )
    conn.commit()
    conn.close()


def test_registered_but_absent_document_does_not_satisfy_the_gate(tmp_path, seeded_db):
    """A canonical_documents row whose file no longer exists must NOT count as
    present evidence. Three such rows (a deleted mock temp dir) were greening
    card_statement/payroll/register in the real July run — same error class as
    provisional: the evidence does not exist."""
    p, _ = seeded_db
    vault = tmp_path / "vault"
    vault.mkdir()
    ghost = tmp_path / "deleted-mock-dir" / "Bold_Transacciones_2026-07.md"
    _register(p, doc_id="ghost-1", filename=ghost.name, path=str(ghost),
              doc_type="card_statement")

    r = check_data_availability("tayrona", PERIOD, vault, db_path=p)

    assert [d["path"] for d in r["stale_index"]] == [str(ghost)]
    assert "card_statement" in r["missing"], "stale row satisfied the gate"
    assert r["gate_passed"] is False
    assert "stale index rows" in r["verdict"]


def test_live_registered_document_still_satisfies_the_gate(tmp_path, seeded_db):
    """The existence filter must not throw away GOOD index rows."""
    p, _ = seeded_db
    vault = tmp_path / "vault"
    vault.mkdir()
    real = vault / "Bold_Transacciones_2026-07.md"
    real.write_text("ok")
    _register(p, doc_id="live-1", filename=real.name, path=str(real),
              doc_type="card_statement")

    r = check_data_availability("tayrona", PERIOD, vault, db_path=p)

    assert r["stale_index"] == []
    assert "card_statement" not in r["missing"]
    assert str(real) in next(c["sources"] for c in r["checks"]
                             if c["item"] == "card_statement")


def test_bare_ota_token_no_longer_matches_cuota(tmp_path, seeded_db):
    """'ota' as a bare pattern matched the loan file 'Detalle_Cuota_...' and
    claimed an OTA report was in hand. The narrowed list must not."""
    p, _ = seeded_db
    vault = tmp_path / "vault" / "2026-07 Julio"
    vault.mkdir(parents=True)
    (vault / "Detalle_Cuota_Bancolombia-7810099111_2026-07.xlsx").write_bytes(b"x")

    r = check_data_availability("tayrona", PERIOD, tmp_path / "vault", db_path=p)
    ota = next(c for c in r["checks"] if c["item"] == "ota_other")

    assert ota["sources"] == [], f"'Cuota' still satisfies ota_other: {ota['sources']}"
    assert "ota_other" in r["missing"]


def test_pms_ignores_the_fareharbor_settlement(tmp_path, seeded_db):
    """PayPal_FareHarbor_Settlements is a settlement, not a PMS export."""
    p, _ = seeded_db
    vault = tmp_path / "vault" / "2026-07 Julio"
    vault.mkdir(parents=True)
    (vault / "PayPal_FareHarbor_Settlements_2026-07.md").write_text("x")

    r = check_data_availability("tayrona", PERIOD, tmp_path / "vault", db_path=p)
    pms = next(c for c in r["checks"] if c["item"] == "pms")

    assert pms["sources"] == []


def test_every_check_carries_a_status(tmp_path, seeded_db):
    """The JSON report must be self-describing: a consumer should not have to
    cross-reference missing/provisional/not_applicable to render a row."""
    p, _ = seeded_db
    vault = tmp_path / "vault" / "2026-07 Julio"
    vault.mkdir(parents=True)
    (vault / "Extracto_Bancolombia_2026-07.md").write_text("x")

    r = check_data_availability("tayrona", PERIOD, tmp_path / "vault", db_path=p)
    by = {c["item"]: c["status"] for c in r["checks"]}

    assert len(by) == len(r["checks"]), "duplicate item keys"
    assert set(by.values()) <= {"ok", "missing", "provisional", "not_applicable"}
    assert by["ota_booking"] == "not_applicable"
    assert by["ota_other"] == "missing"
    assert by["bank_statement"] == "ok"
    # status must agree with the top-level lists it summarises
    for c in r["checks"]:
        if c["status"] == "missing":
            assert c["item"] in r["missing"]
        if c["status"] == "provisional":
            assert c["item"] in [x["item"] for x in r["provisional"]]
        if c["status"] == "not_applicable":
            assert c["item"] in [x["item"] for x in r["not_applicable"]]
