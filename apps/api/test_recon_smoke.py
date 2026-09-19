#!/usr/bin/env python3
"""Smoke tests for the rebuilt recon phases P3–P6 (2026-09-18 rebuild added
no unit tests for these — this file closes that gap).

Each test runs the phase IN MOCK MODE (deterministic synthetic corpus) and
asserts the honest-state contract: the phase runs clean, every JE it proposes
is balanced, and its line accounts are exactly the phase's ACCT_* constants
(the strings the account_map resolves — fork 2026-09-18-B).

Run:  pytest test_recon_smoke.py -v
"""

from __future__ import annotations

import pytest

from pre_close_gate import run_gate
from revenue_recon import (ACCT_BOLD_CLEARING, ACCT_DEFERRED, ACCT_FEES,
                           ACCT_REVENUE, run_revenue_recon)
from expense_recon import (ACCT_AP, ACCT_EXPENSE, ACCT_PAYROLL_EXPENSE,
                           ACCT_PAYROLL_PAYABLE, run_expense_recon)
from bank_recon import ACCT_BANK, ACCT_BANK_GMF, run_bank_recon

PERIOD = "2026-07"


def assert_balanced(lines, ctx):
    dr = round(sum(float(l.get("debit") or 0) for l in lines), 2)
    cr = round(sum(float(l.get("credit") or 0) for l in lines), 2)
    assert abs(dr - cr) <= 1.0, f"{ctx}: Dr {dr} != Cr {cr}"


# --- P3: pre-close gate -----------------------------------------------------

def test_pre_close_gate_mock_smoke(tmp_path):
    r = run_gate("tayrona", PERIOD, mock=True, db_path=tmp_path / "db.sqlite")
    assert r["phase"] == "pre_close_gate"
    # the honest Tayrona-July shape: bank/card/payroll/intake IN, OTA/PMS OUT
    assert r["gate_passed"] is False
    blockers = " ".join(r["blockers"]).lower()
    assert "ota" in blockers and "pms" in blockers
    # Phase 1.6 pagination is exercised to exhaustion on every mock run
    docs = r["received_docs"]
    assert docs["bills_pulled"] == 65       # the 65-doc synthetic corpus
    assert docs["pages_used"] == 3          # 30/30/5
    assert docs["paged_to_exhaustion"] is True
    assert docs["transport"].startswith("mock")


# --- P4: revenue recon ------------------------------------------------------

def test_revenue_recon_mock_smoke():
    r = run_revenue_recon("tayrona", PERIOD, mock=True)
    ids = sorted(j["je_id"] for j in r["jes"])
    # EX-J07-12 (deferral already booked) suppresses REV-02 by design
    assert ids == [f"REV-{PERIOD}-01", f"REV-{PERIOD}-03"], ids
    for je in r["jes"]:
        assert_balanced(je["lines"], je["je_id"])
        accts = {l["account"] for l in je["lines"]}
        assert accts <= {ACCT_BOLD_CLEARING, ACCT_REVENUE, ACCT_DEFERRED,
                         ACCT_FEES}, accts
    gap_text = " ".join(r["gaps"]).lower()
    assert "breach" in gap_text              # channel footing: 9,141,500 vs 9,491,500
    assert "deferral" in gap_text            # already-booked deferral surfaced
    assert r["decisions"] and "suppressed" in r["decisions"][0].lower()


# --- P5: expense recon ------------------------------------------------------

def test_expense_recon_mock_smoke():
    r = run_expense_recon("tayrona", PERIOD, mock=True)
    ids = sorted(j["je_id"] for j in r["jes"])
    assert ids == [f"EXP-{PERIOD}-01", f"EXP-{PERIOD}-02", f"EXP-{PERIOD}-03"], ids
    by_id = {j["je_id"]: j for j in r["jes"]}
    assert_balanced(by_id[f"EXP-{PERIOD}-01"]["lines"], "EXP-01")
    assert ({l["account"] for l in by_id[f"EXP-{PERIOD}-01"]["lines"]}
            == {ACCT_PAYROLL_EXPENSE, ACCT_PAYROLL_PAYABLE})
    for jid in (f"EXP-{PERIOD}-02", f"EXP-{PERIOD}-03"):
        assert_balanced(by_id[jid]["lines"], jid)
        assert ({l["account"] for l in by_id[jid]["lines"]}
                == {ACCT_EXPENSE, ACCT_AP})
    gap_text = " ".join(r["gaps"]).lower()
    assert "not booked" in gap_text          # EX-J07-07 'Not Kevin' disposition
    assert "foreign vendor" in gap_text      # AWS documento-soporte path
    assert r["cfd_fired"]                    # CFD rules ran over expense lines


# --- P6: bank recon ---------------------------------------------------------

def test_bank_recon_mock_smoke():
    r = run_bank_recon("tayrona", PERIOD, mock=True)
    assert r["statement"]["line_count"] == 13
    assert len(r["jes"]) == 1
    je = r["jes"][0]
    assert je["je_id"] == f"BNK-{PERIOD}-01"
    assert_balanced(je["lines"], je["je_id"])
    assert {l["account"] for l in je["lines"]} == {ACCT_BANK, ACCT_BANK_GMF}
    # GMF: expected (debits x 0.004) vs recorded — the mock numbers are fixed
    #   debits abs sum = 6,123,936.54 x 0.004 = 24,495.75 vs recorded 49,597.54
    assert r["gmf"]["difference"] == pytest.approx(-25_101.79)
    assert r["bold"]["gap"]  # Bold settlements vs canonical deposited (cut-off)
    # 5305xx GMF is credited only when the difference is negative
    gmf_line = next(l for l in je["lines"] if l["account"] == ACCT_BANK_GMF)
    assert gmf_line["credit"] == pytest.approx(25_101.79)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))