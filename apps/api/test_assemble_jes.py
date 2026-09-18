#!/usr/bin/env python3
"""Tests for Phase 8 — assemble_jes.

RECONSTRUCTED 2026-09-18. The original test_assemble_jes.py (written 2026-09-17)
was lost with the rest of ~/src/contabia-site in a Time Machine restore; it was
never committed and the Time Machine drive has no backup between 2026-08-24 and
the restore itself.

These ten cases are rebuilt from the 2026-09-17 session summary, which records the
original suite as: "clean=LOW/postable, unbalanced=CRITICAL blocker,
placeholder/unmapped=HIGH, untraceable=HIGH, malformed=CRITICAL, duplicate-id
blocker, pending=MEDIUM, priority sort, empty batch". They are behaviourally
equivalent, not byte-identical to the originals.

Run:  pytest test_assemble_jes.py -v
"""

from __future__ import annotations

import pytest

from assemble_jes import assemble_from_jes, validate_je


ACCT_MAP = {"510506": "1", "250505": "2", "159215": "3"}


def _je(**over) -> dict:
    """A clean, balanced, mapped, traceable, approved JE."""
    base = {
        "je_id": "OJ-4",
        "description": "Nick June payroll package (missing 5105)",
        "period": "2026-08",
        "bucket": "nomina",
        "status": "approved_by_edwin",
        "linked_docs": ["doc-ssot-1"],
        "lines": [
            {"account": "510506", "debit": 9_805_834, "credit": 0},
            {"account": "250505", "debit": 0, "credit": 9_805_834},
        ],
    }
    base.update(over)
    return base


# --- per-JE validation -----------------------------------------------------

def test_clean_je_is_low_and_postable():
    v = validate_je(_je(), ACCT_MAP)
    assert v["priority"] == "LOW"
    assert v["postable"] is True
    assert v["balanced"] and v["account_mapped"] and v["ssot_backed"]
    assert v["issues"] == []


def test_unbalanced_je_is_critical_and_not_postable():
    v = validate_je(_je(lines=[
        {"account": "510506", "debit": 100, "credit": 0},
        {"account": "250505", "debit": 0, "credit": 90},
    ]), ACCT_MAP)
    assert v["priority"] == "CRITICAL"
    assert v["postable"] is False
    assert any("unbalanced" in i for i in v["issues"])


def test_placeholder_account_is_high_and_not_postable():
    """The 'xx' stubs the recon phases emit must never reach a SoR."""
    v = validate_je(_je(lines=[
        {"account": "1110xx", "debit": 100, "credit": 0},
        {"account": "250505", "debit": 0, "credit": 100},
    ]), {**ACCT_MAP, "1110xx": "99"})  # even if "mapped", xx is a placeholder
    assert v["priority"] == "HIGH"
    assert v["account_mapped"] is False
    assert v["postable"] is False


def test_unmapped_account_is_high_and_not_postable():
    v = validate_je(_je(lines=[
        {"account": "999999", "debit": 100, "credit": 0},
        {"account": "250505", "debit": 0, "credit": 100},
    ]), ACCT_MAP)
    assert v["priority"] == "HIGH"
    assert v["account_mapped"] is False


def test_untraceable_je_is_high():
    je = _je()
    del je["linked_docs"]
    v = validate_je(je, ACCT_MAP)
    assert v["priority"] == "HIGH"
    assert v["ssot_backed"] is False
    assert any("untraceable" in i for i in v["issues"])


def test_malformed_line_is_critical():
    """A line carrying both a debit and a credit is malformed."""
    v = validate_je(_je(lines=[{"account": "510506", "debit": 100, "credit": 100}]), ACCT_MAP)
    assert v["priority"] == "CRITICAL"
    assert v["postable"] is False


def test_pending_approval_is_medium_but_still_postable_shape():
    v = validate_je(_je(status="pending_edwin_approval"), ACCT_MAP)
    assert v["priority"] == "MEDIUM"
    assert v["postable"] is True  # structurally fine; approval is a separate gate


# --- batch assembly --------------------------------------------------------

def test_duplicate_je_id_is_a_blocker():
    pkg = assemble_from_jes([_je(), _je()], "tayrona", "2026-08", ACCT_MAP)
    assert any("duplicate" in b for b in pkg["blockers"])
    assert all(j["priority"] == "CRITICAL" for j in pkg["jes"])
    assert all(j["postable"] is False for j in pkg["jes"])
    assert pkg["ready_to_post"] is False


def test_priority_sort_is_most_broken_first():
    unbalanced = _je(je_id="X1", lines=[
        {"account": "510506", "debit": 100, "credit": 0},
        {"account": "250505", "debit": 0, "credit": 90},
    ])
    placeholder = _je(je_id="X2", lines=[
        {"account": "1110xx", "debit": 100, "credit": 0},
        {"account": "250505", "debit": 0, "credit": 100},
    ])
    pkg = assemble_from_jes([_je(), unbalanced, placeholder], "tayrona", "2026-08", ACCT_MAP)
    assert [j["priority"] for j in pkg["jes"]] == ["CRITICAL", "HIGH", "LOW"]


def test_empty_batch_does_not_crash_and_is_not_ready():
    pkg = assemble_from_jes([], "tayrona", "2026-08", ACCT_MAP)
    assert pkg["summary"]["jes"] == 0
    assert pkg["ready_to_post"] is False
    assert pkg["blockers"] == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
