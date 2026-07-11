"""
Contabia portal backend - minimal real slice.

Scope (per 2026-07-10 session): get Sonata Mas SAS's January 2026 exception
review actually running through real endpoints instead of data.js's mock
object, per File 18 (Portal & Free Scan Flow)'s documented API contract.
This is NOT the full motor - no rules engine, no connector orchestration,
no Inngest. It is the review-and-approve slice: exceptions + journal-entries
+ read-only Alegra cross-check, backed by the client's own SQLite file per
the committed architecture (File 07, "SQLite, one file per client").

Run:
    pip install -r requirements.txt
    ALEGRA_EMAIL=... ALEGRA_API_TOKEN=... uvicorn main:app --reload

Deploy target (2026-07-10 decision, scoped to this slice): Railway web
service, not Render -- see Continuation-Portal-and-Repo.md section 4 and
README.md 'Deploying for real'. Point the portal's API_BASE at wherever
this ends up running.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from alegra_client import AlegraAuthError, AlegraClient
from data_loader import load_exceptions, summarize
from je_data import ACCEPTED_NO_ACTION, JOURNAL_ENTRIES, OPEN_JUDGMENT_CALLS, RECURRING_ROUTINES

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = Path(__file__).parent / "sonata_mas_001.sqlite"  # one file per client, per File 07

app = FastAPI(title="Contabia Portal Backend - Sonata Mas slice")

# ---------------------------------------------------------------------------
# CORS -- the portal frontend (apps/portal/*.html) calls this API cross-origin
# (different host/port, and once deployed, a different domain than Railway's).
# No auth is wired into this minimal slice (see README) -- allow_origins="*"
# is a deliberate scope tradeoff for this pass, not an oversight. Tighten this
# to the real portal domain(s) before this is anything but a single-client,
# time-boxed review tool.
# ---------------------------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Entity registry - single entity for this pass. Adding Cantamar/betas later
# means adding a row here + its own exception_register.csv + its own SQLite
# file (per-client isolation is the committed architecture, not a shortcut).
# ---------------------------------------------------------------------------
ENTITIES = {
    "sonata-001": {
        "name": "SONATA MAS S.A.S. (Tayrona Sailing)",
        "nit": "901528910-3",
        "csv": DATA_DIR / "exception_register.csv",
    }
}


def _get_entity_or_404(entity_id: str) -> dict:
    entity = ENTITIES.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Unknown entity '{entity_id}'")
    return entity


@contextmanager
def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _init_db() -> None:
    with _db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exception_status (
                exception_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                rejection_note TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS je_status (
                je_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                rejection_note TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


_init_db()


def _status_overrides(table: str) -> dict[str, dict]:
    with _db() as conn:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        return {row["exception_id" if table == "exception_status" else "je_id"]: dict(row) for row in rows}


# ---------------------------------------------------------------------------
# GET /entities  (per File 18 core endpoints)
# ---------------------------------------------------------------------------
@app.get("/entities")
def list_entities():
    return [{"id": eid, "name": e["name"], "nit": e["nit"]} for eid, e in ENTITIES.items()]


# ---------------------------------------------------------------------------
# GET /entities/:id/summary
# ---------------------------------------------------------------------------
@app.get("/entities/{entity_id}/summary")
def get_summary(entity_id: str):
    entity = _get_entity_or_404(entity_id)
    exceptions = load_exceptions(entity["csv"])
    overrides = _status_overrides("exception_status")
    for e in exceptions:
        if e["id"] in overrides:
            e["status"] = overrides[e["id"]]["status"]
    return {
        "meta": {"id": entity_id, "name": entity["name"], "nit": entity["nit"]},
        "closeSummary": {
            "period": "2026-01",
            "rfr_status": "full_rfr",  # confirmed 2026-07-06, cross-checked live 2026-07-10
            "nothing_posted": True,
        },
        "cifras": summarize(exceptions),
    }


# ---------------------------------------------------------------------------
# GET /entities/:id/exceptions  +  PATCH /entities/:id/exceptions/:exc_id
# ---------------------------------------------------------------------------
@app.get("/entities/{entity_id}/exceptions")
def get_exceptions(entity_id: str):
    entity = _get_entity_or_404(entity_id)
    exceptions = load_exceptions(entity["csv"])
    overrides = _status_overrides("exception_status")
    for e in exceptions:
        if e["id"] in overrides:
            e["status"] = overrides[e["id"]]["status"]
            e["rejection_note"] = overrides[e["id"]].get("rejection_note")
    return exceptions


class ExceptionPatch(BaseModel):
    status: Literal["approved", "rejected"]
    rejection_note: Optional[str] = None


@app.patch("/entities/{entity_id}/exceptions/{exc_id}")
def patch_exception(entity_id: str, exc_id: str, patch: ExceptionPatch):
    _get_entity_or_404(entity_id)
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO exception_status (exception_id, status, rejection_note)
            VALUES (?, ?, ?)
            ON CONFLICT(exception_id) DO UPDATE SET
                status = excluded.status,
                rejection_note = excluded.rejection_note,
                updated_at = CURRENT_TIMESTAMP
            """,
            (exc_id, patch.status, patch.rejection_note),
        )
    return {"exception_id": exc_id, "status": patch.status}


# ---------------------------------------------------------------------------
# GET /entities/:id/journal-entries  +  PATCH .../journal-entries/:je_id
# ---------------------------------------------------------------------------
@app.get("/entities/{entity_id}/journal-entries")
def get_journal_entries(entity_id: str):
    _get_entity_or_404(entity_id)
    overrides = _status_overrides("je_status")
    entries = [dict(je) for je in JOURNAL_ENTRIES]
    for je in entries:
        if je["id"] in overrides:
            je["status"] = overrides[je["id"]]["status"]
    return {
        "ready_to_post": [je for je in entries if je["group"] == "A_ready_to_post"],
        "estimated": [je for je in entries if je["group"] == "B_estimated"],
        "disclosure_only": [je for je in entries if je["group"] == "C_disclosure_only"],
        "open_judgment_calls": OPEN_JUDGMENT_CALLS,
        "recurring_routines": RECURRING_ROUTINES,
        "accepted_no_action": ACCEPTED_NO_ACTION,
    }


class JEPatch(BaseModel):
    status: Literal["approved_by_edwin", "rejected"]
    rejection_note: Optional[str] = None


@app.patch("/entities/{entity_id}/journal-entries/{je_id}")
def patch_journal_entry(entity_id: str, je_id: str, patch: JEPatch):
    _get_entity_or_404(entity_id)
    valid_ids = {je["id"] for je in JOURNAL_ENTRIES}
    if je_id not in valid_ids:
        raise HTTPException(status_code=404, detail=f"Unknown journal entry '{je_id}'")
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO je_status (je_id, status, rejection_note)
            VALUES (?, ?, ?)
            ON CONFLICT(je_id) DO UPDATE SET
                status = excluded.status,
                rejection_note = excluded.rejection_note,
                updated_at = CURRENT_TIMESTAMP
            """,
            (je_id, patch.status, patch.rejection_note),
        )
    return {"je_id": je_id, "status": patch.status}


# ---------------------------------------------------------------------------
# Live Alegra cross-check - read-only. Confirms period status + pulls the
# trial balance so the portal can show "nothing posted yet" as a live fact,
# not a stale claim from the 2026-07-06 handoff doc.
# ---------------------------------------------------------------------------
@app.get("/entities/{entity_id}/alegra-check")
def alegra_check(entity_id: str, year: int = 2026, month: int = 1):
    _get_entity_or_404(entity_id)
    try:
        client = AlegraClient()
    except AlegraAuthError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    accounts = client.get_accounts()
    journals = client.get_journals()
    return {
        "period_checked": f"{year}-{month:02d}",
        "accounts_count": len(accounts) if isinstance(accounts, list) else None,
        "recent_journals_sample": journals[:5] if isinstance(journals, list) else journals,
        "note": (
            "This endpoint requires ALEGRA_EMAIL / ALEGRA_API_TOKEN to be set for "
            "whichever machine runs this service. It does not post anything - "
            "read-only, matches the 'nothing posts without accountant approval' rule."
        ),
    }


# ---------------------------------------------------------------------------
# POST /entities/:id/close/:period/post -- deliberately NOT implemented here.
# Posting is out of scope for this pass (see task decision: stop at an
# Edwin-ready package, not POST /journals). When Edwin has signed off, wire
# this to loop AlegraClient.post_journal() over every JE whose status is
# 'approved_by_edwin', one entry at a time (no bulk import endpoint exists).
# ---------------------------------------------------------------------------
