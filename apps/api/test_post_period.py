#!/usr/bin/env python3
"""Tests for the hardened posting write path (main.py post_period).

REBUILT 2026-09-18. The original test_post_period.py (written 2026-09-17) was
lost with the rest of ~/src/contabia-site in the Time Machine restore; never
committed, no backup between 2026-08-24 and the restore.

The 2026-09-17 session summary names the original suite's seven cases:
  "double-invoke posts once; wrong-period posts nothing; unbalanced skipped;
   unmapped blocked live; dry-run claims nothing; date = real month-end +
   traceable; month-length/leap-year"
These are behaviourally equivalent, not byte-identical, to the originals.
They exercise the hardened write path (review findings #1/#2/#5/#6/#8):
idempotency ledger, period scoping, balance assert, account-map gate,
real month-end date and traceable observations, dry-run claim hygiene.

Run:  pytest test_post_period.py -v
"""

from __future__ import annotations

import importlib
import json
import sqlite3

import pytest

# Imported lazily inside the fixture: main reads env (DRY_RUN, DB paths,
# PORTAL_USERS_JSON) at import time, so the module must be loaded/reloaded
# with per-test env in place.
import main  # noqa: F401  (first import; fixture reloads with test env)


# ---------------------------------------------------------------------------
# Fakes and helpers
# ---------------------------------------------------------------------------
class FakeAlegraClient:
    """Transport fake: records payloads that 'would have been posted' and
    simulates the error/read-back modes of the real client."""

    def __init__(self) -> None:
        self.posted: list[dict] = []
        self.post_calls = 0
        self.fail_next: str | None = None  # exception message for next call
        self.read_back_journals: list[dict] = []  # what get_journals returns

    def post_journal(self, payload: dict) -> dict:
        self.post_calls += 1
        if self.fail_next is not None:
            msg, self.fail_next = self.fail_next, None
            raise RuntimeError(msg)
        self.posted.append(payload)
        return {"id": 9000 + len(self.posted)}

    def get_journals(self, start=None, end=None):
        return list(self.read_back_journals)


def _je(**over) -> dict:
    """A well-formed, balanced, traceable JE for the test close period."""
    base = {
        "id": "OJ-4",
        "group": "A_ready_to_post",
        "description": "Nick payroll catch-up",
        "period": "2026-07",
        "bucket": "live",
        "status": "pending_edwin_approval",
        "linked_exceptions": ["EX-J07-16", "EX-J07-17"],
        "lines": [
            {"account": "510506 Sueldos", "debit": 5_000_000, "credit": 0},
            {"account": "250505 Salarios", "debit": 0, "credit": 5_000_000},
        ],
    }
    base.update(over)
    return base


ACCT_MAP = {"510506 Sueldos": "1", "250505 Salarios": "2"}


def _approve(db_path, je_id: str) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "INSERT INTO je_status (je_id, status) VALUES (?, 'approved_by_edwin') "
            "ON CONFLICT(je_id) DO UPDATE SET status = 'approved_by_edwin', "
            "rejection_note = NULL, updated_at = CURRENT_TIMESTAMP",
            (je_id,),
        )
        con.commit()
    finally:
        con.close()


def _seed_account_map(db_path, mapping: dict) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "INSERT INTO company_rules (rule_id, entity_id, rule_text, category, "
            "source, active, created_by) VALUES (?, 'sonata-001', ?, 'account_map', "
            "'client_choice', 1, 'test')",
            ("CR-TEST-ACCOUNT-MAP", json.dumps(mapping)),
        )
        con.commit()
    finally:
        con.close()


def _posting_rows(db_path) -> list[tuple]:
    con = sqlite3.connect(db_path)
    try:
        return con.execute(
            "SELECT entity_id, period, je_id, status, alegra_id FROM posted_journals"
        ).fetchall()
    finally:
        con.close()


def _posting_log_rows(db_path) -> list[tuple]:
    con = sqlite3.connect(db_path)
    try:
        return con.execute(
            "SELECT entity_id, period, je_id, dry_run FROM posting_log"
        ).fetchall()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Fixture: fresh main module per test (env-scoped, tmp DB + data dir)
# ---------------------------------------------------------------------------
@pytest.fixture()
def api(tmp_path, monkeypatch):
    """Load/reload main with a hermetic env: tmp sqlite + data dirs, one
    portal user, and the requested DRY_RUN mode. Returns a namespace with the
    reloaded module, TestClient, token, and the tmp DB path."""
    monkeypatch.setenv(
        "PORTAL_USERS_JSON",
        json.dumps([{
            "username": "kevin",
            "password": "pw-test",
            "role": "owner",
            "name": "Kevin",
            "email": "kevin@contabia.co",
            "default_entity": "sonata-001",
        }]),
    )
    monkeypatch.setenv("CONTABIA_DB_PATH", str(tmp_path / "test.sqlite"))
    monkeypatch.setenv("CONTABIA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CONTABIA_BOVEDA_DIR", str(tmp_path / "boveda"))
    monkeypatch.setenv("DRY_RUN", "true")  # default; live tests flip before reload

    from fastapi.testclient import TestClient

    mainmod = importlib.import_module("main")
    importlib.reload(mainmod.auth_users)  # re-read PORTAL_USERS_JSON for this test
    mainmod = importlib.reload(mainmod)   # re-read the per-test env

    user = mainmod.auth_users.USERS[0]
    headers = {"Authorization": f"Bearer {user['token']}"}
    client = TestClient(mainmod.app)
    return type(
        "Api", (),
        {
            "main": mainmod,
            "client": client,
            "headers": headers,
            "db": str(tmp_path / "test.sqlite"),
            "tmp": tmp_path,
        },
    )()


def _live(api, fake: FakeAlegraClient) -> None:
    """Flip the reloaded module to LIVE mode with the fake transport."""
    import os

    api.main.DRY_RUN = False  # noqa  (module global read inside post_period)
    api.main.AlegraClient = lambda: fake  # noqa  (module global transport)


def _post(api, period: str = "2026-07", entity: str = "sonata-001"):
    return api.client.post(
        f"/entities/{entity}/close/{period}/post", headers=api.headers
    )


# ---------------------------------------------------------------------------
# The seven cases
# ---------------------------------------------------------------------------
def test_double_invoke_posts_once(api, monkeypatch):
    """Idempotency (finding #1): two POSTs of the same close post the JE once;
    the second call's claim fails and it reports the skip, never a duplicate."""
    fake = FakeAlegraClient()
    monkeypatch.setattr(api.main, "JOURNAL_ENTRIES", [_je()])
    _approve(api.db, "OJ-4")
    _seed_account_map(api.db, ACCT_MAP)
    _live(api, fake)

    first = _post(api).json()
    second = _post(api).json()

    assert fake.post_calls == 1
    assert [r["posted"] for r in first["posted_or_would_post"]] == [True]
    assert second["posted_or_would_post"][0]["posted"] is False
    assert "already posted" in second["posted_or_would_post"][0]["reason"]
    rows = _posting_rows(api.db)
    assert len(rows) == 1
    assert rows[0][:4] == ("sonata-001", "2026-07", "OJ-4", "posted")
    assert rows[0][4] is not None  # alegra_id recorded


def test_wrong_period_posts_nothing(api, monkeypatch):
    """Period scoping (finding #2): an approved JE whose own period is not the
    close being posted is skipped, never pushed into another month's close."""
    fake = FakeAlegraClient()
    monkeypatch.setattr(api.main, "JOURNAL_ENTRIES", [_je(period="2026-08", id="OJ-5")])
    _approve(api.db, "OJ-5")
    _seed_account_map(api.db, ACCT_MAP)
    _live(api, fake)

    resp = _post(api, period="2026-07").json()

    assert fake.post_calls == 0
    assert resp["posted_or_would_post"] == []
    assert any("period" in s["reason"] for s in resp["skipped"])


def test_unbalanced_skipped(api, monkeypatch):
    """Balance assert (finding #5): an unbalanced approved JE is skipped with
    a reason; it never reaches the transport, even in live mode."""
    fake = FakeAlegraClient()
    unbalanced = _je(lines=[
        {"account": "510506 Sueldos", "debit": 100, "credit": 0},
        {"account": "250505 Salarios", "debit": 0, "credit": 90},
    ])
    monkeypatch.setattr(api.main, "JOURNAL_ENTRIES", [unbalanced])
    _approve(api.db, "OJ-4")
    _seed_account_map(api.db, ACCT_MAP)
    _live(api, fake)

    resp = _post(api).json()

    assert fake.post_calls == 0
    assert resp["posted_or_would_post"] == []
    assert any("unbalanced" in s["reason"] for s in resp["skipped"])


def test_unmapped_blocked_live(api, monkeypatch):
    """Account-map gate (finding #6): in LIVE mode a JE with a line whose
    account is not in company_rules account_map is refused before posting."""
    fake = FakeAlegraClient()
    unmapped = _je(lines=[
        {"account": "510506 Sueldos", "debit": 5_000_000, "credit": 0},
        {"account": "777777 No existe", "debit": 0, "credit": 5_000_000},
    ])
    monkeypatch.setattr(api.main, "JOURNAL_ENTRIES", [unmapped])
    _approve(api.db, "OJ-4")
    _seed_account_map(api.db, ACCT_MAP)  # does NOT contain 777777
    _live(api, fake)

    resp = _post(api).json()

    assert fake.post_calls == 0
    assert resp["posted_or_would_post"] == []
    assert any("account_map" in s["reason"] and "777777" in s["reason"] for s in resp["skipped"])


def test_dry_run_claims_nothing(api, monkeypatch):
    """Rehearsal hygiene: a dry run logs the exact payload but writes no row
    to posted_journals - it must not consume an idempotency claim."""
    monkeypatch.setattr(api.main, "JOURNAL_ENTRIES", [_je()])
    _approve(api.db, "OJ-4")
    # No account_map seeded - dry run still reports what WOULD post.

    resp = _post(api).json()

    assert resp["dry_run"] is True
    assert len(resp["posted_or_would_post"]) == 1
    assert resp["posted_or_would_post"][0]["dry_run"] is True
    assert "would_post" in resp["posted_or_would_post"][0]
    assert _posting_rows(api.db) == []  # claims nothing
    log_rows = _posting_log_rows(api.db)
    assert len(log_rows) == 1 and log_rows[0][3] == 1  # dry_run=1 logged


def test_date_is_real_month_end_and_traceable(api, monkeypatch):
    """Posting date = real month-end (finding #2 repair) and observations
    carry the linked source doc/exception ids (finding #8)."""
    monkeypatch.setattr(api.main, "JOURNAL_ENTRIES", [_je()])
    _approve(api.db, "OJ-4")

    resp = _post(api).json()
    payload = resp["posted_or_would_post"][0]["would_post"]

    assert payload["date"] == "2026-07-31"  # July has 31 days - no -31/-28 guess
    assert "OJ-4" in payload["observations"]
    assert "EX-J07-16" in payload["observations"]
    assert "EX-J07-17" in payload["observations"]
    for entry in payload["entries"]:
        assert "account_name" in entry  # traceability survives the transport


def test_month_length_and_leap_year(api):
    """_last_day_of_period resolves real month lengths incl. leap February."""
    last = api.main._last_day_of_period
    assert last("2024-02") == "2024-02-29"  # leap year
    assert last("2026-02") == "2026-02-28"  # non-leap
    assert last("2026-04") == "2026-04-30"
    assert last("2026-07") == "2026-07-31"
    assert last("2026-08") == "2026-08-31"
    assert last("2026-12") == "2026-12-31"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))