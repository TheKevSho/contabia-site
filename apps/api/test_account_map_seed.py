#!/usr/bin/env python3
"""Tests for the Sonata account_map seed (account_map_seed.py).

Covers the fork-2026-09-18-B contract:
  - atomicity: the seeder writes NOTHING while any alegra_id is unresolved
  - round-trip: with ids resolved, the map lands for BOTH entity ids
    ('sonata-001' portal + 'tayrona' CLI) and load_account_map resolves every
    account the phases emit; the assembler predicate agrees
  - resolve_alegra_ids() never invents an id (match by chart code only)

Run:  pytest test_account_map_seed.py -v
"""

from __future__ import annotations

import sqlite3

import pytest

from assemble_jes import _account_mapped, load_account_map
from account_map_seed import SONATA_MAP_ENTRIES, resolve_alegra_ids, seed_account_map

SCHEMA = """
CREATE TABLE IF NOT EXISTS company_rules (
    rule_id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,
    rule_text TEXT NOT NULL,
    rule_text_es TEXT,
    rule_text_en TEXT,
    category TEXT,
    source TEXT,
    audit_tag TEXT,
    linked_exception_id TEXT,
    created_by TEXT,
    active INTEGER
)
"""


def _connect(db):
    def connect():
        return sqlite3.connect(str(db))
    return connect


@pytest.fixture()
def db(tmp_path):
    d = tmp_path / "rules.sqlite"
    with sqlite3.connect(str(d)) as conn:
        conn.execute(SCHEMA)
    return d


def _resolved_entries(prefix: str = "9"):
    """Copy of the seed entries with synthetic (but well-formed) Alegra ids."""
    out = []
    for i, e in enumerate(SONATA_MAP_ENTRIES, start=1):
        c = dict(e)
        c["alegra_id"] = f"{prefix}{i:04d}"
        out.append(c)
    return out


# --- atomicity -------------------------------------------------------------

def test_seed_refuses_to_write_while_any_id_is_pending(db, monkeypatch):
    """The map is atomic: with any alegra_id still None the seeder writes
    NOTHING — a half-resolved map must never reach company_rules. Simulated
    here by forcing one entry back to the pending state (the live seed is
    fully resolved)."""
    entries = [dict(e) for e in SONATA_MAP_ENTRIES]
    entries[0]["alegra_id"] = None
    monkeypatch.setattr("account_map_seed.SONATA_MAP_ENTRIES", entries)
    result = seed_account_map(_connect(db))
    assert result["inserted"] == 0
    assert result["pending"] == 1
    with sqlite3.connect(str(db)) as conn:
        n = conn.execute(
            "SELECT count(*) FROM company_rules WHERE category = 'account_map'"
        ).fetchone()[0]
    assert n == 0


# --- round-trip through both readers ---------------------------------------

def test_seeded_map_round_trips_both_entity_ids_and_both_readers(
        db, monkeypatch):
    monkeypatch.setattr("account_map_seed.SONATA_MAP_ENTRIES", _resolved_entries())
    result = seed_account_map(_connect(db))
    assert result["inserted"] == 2 * len(SONATA_MAP_ENTRIES)  # 10 keys x 2 ids

    map_t = load_account_map("tayrona", db)
    map_s = load_account_map("sonata-001", db)
    assert map_t == map_s, "portal id and CLI slug must resolve the SAME map"
    assert set(map_t) == {e["key"] for e in _resolved_entries()}

    # every phase account resolves through the assembler predicate
    for e in _resolved_entries():
        assert _account_mapped(e["key"], map_t) is True, e["key"]


def test_seed_is_idempotent(db, monkeypatch):
    monkeypatch.setattr("account_map_seed.SONATA_MAP_ENTRIES", _resolved_entries())
    first = seed_account_map(_connect(db))["inserted"]
    second = seed_account_map(_connect(db))["inserted"]
    assert first == 2 * len(SONATA_MAP_ENTRIES)
    assert second == 0  # match-on-rule_id: never duplicate


def test_seed_never_overwrites_an_edited_row(db, monkeypatch):
    monkeypatch.setattr("account_map_seed.SONATA_MAP_ENTRIES", _resolved_entries())
    seed_account_map(_connect(db))
    # user edits one mapped row (portal CRUD) — the seeder must leave it alone
    with sqlite3.connect(str(db)) as conn:
        conn.execute(
            "UPDATE company_rules SET rule_text = '{\"1110xx Bold clearing\": \"777\"}' "
            "WHERE rule_id = 'am-bold-clearing-sonata-001'"
        )
    seed_account_map(_connect(db))
    with sqlite3.connect(str(db)) as conn:
        row = conn.execute(
            "SELECT rule_text FROM company_rules WHERE rule_id = 'am-bold-clearing-sonata-001'"
        ).fetchone()
    assert '"777"' in row[0]


# --- id resolution ----------------------------------------------------------

def test_resolve_alegra_ids_matches_by_chart_code_only():
    """Chart rows are matched by PUC code only — and every seed entry that
    HAS a chart row resolves. Decoy rows (unknown codes) resolve to nothing."""
    entries = SONATA_MAP_ENTRIES
    chart = [
        {"id": str(i), "name": f"cuenta {e['puc']}", "code": e["puc"]}
        for i, e in enumerate(entries, start=1001)
    ]
    chart.append({"id": "9999", "name": "Caja boutique", "code": "999999"})
    resolved = resolve_alegra_ids(chart)
    assert len(resolved) == len(entries)
    assert all(v for v in resolved.values())          # no empty/Nones invented
    assert "9999" not in resolved.values()            # decoy never resolves


def test_resolve_alegra_ids_never_invents_an_id():
    assert resolve_alegra_ids([]) == {}
    assert resolve_alegra_ids([{"id": "77", "name": "spin", "code": "999999"}]) == {}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))