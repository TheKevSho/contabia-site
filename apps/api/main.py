"""
Contabia portal backend - Sonata Mas slice, v2 (2026-07-24).

v1 (2026-07-10/14): exceptions + journal-entries review, boveda, Alegra
read-only cross-check. v2 adds, per the June-lock/July-live go-live pass:

  - Period reframe: opening balance locked 2026-06-30, live period 2026-07
    (File 28 final decision, 2026-07-17). Jan-June register rows are the
    historical baseline; July exceptions come from live Alegra ingestion.
  - Auth: POST /auth/login (portal user/pass from env) issues the bearer
    token every /entities/* route now requires. CORS locked to contabia.co
    origins. Interim measure per File 28 B2 until Clerk (Stage 1).
  - Company config rules: /entities/:id/rules CRUD, implementing the
    two-bucket rejection-escalation design (client_choice vs motor_fix,
    silent audit tag) from ContabIA-Ingestion-and-Motor-Flow-2026-07-13.
  - Posting: POST /entities/:id/close/:period/post loops JEs whose status
    is approved_by_edwin through AlegraClient.post_journal(). DRY_RUN env
    defaults to true - logs exact payloads, writes nothing. Gate B guard:
    JE ids touching a filed retefuente base are refused regardless of
    approval status or dry-run flag (File 28 A1.3).

Run:
    pip install -r requirements.txt
    PORTAL_PASSWORD=... ALEGRA_EMAIL=... ALEGRA_API_TOKEN=... uvicorn main:app
"""
import json
import logging
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import auth_users
import boveda_data
from alegra_client import AlegraAuthError, AlegraClient
from data_loader import load_exceptions, summarize
from je_data import ACCEPTED_NO_ACTION, JOURNAL_ENTRIES, OPEN_JUDGMENT_CALLS, RECURRING_ROUTINES
from seed_rules import seed_standing_rules

log = logging.getLogger("contabia.api")
logging.basicConfig(level=logging.INFO)

DATA_DIR = Path(os.environ.get("CONTABIA_DATA_DIR", Path(__file__).parent / "data"))
DB_PATH = Path(os.environ.get("CONTABIA_DB_PATH", Path(__file__).parent / "sonata_mas_001.sqlite"))
# Boveda uploads need persistent storage (Railway volume); registers stay in the repo.
BOVEDA_DIR = Path(os.environ.get("CONTABIA_BOVEDA_DIR", DATA_DIR))

# ---------------------------------------------------------------------------
# Auth: named users (Kevin owner / Edwin CPA / Nick owner) via PORTAL_USERS_JSON.
# Falls back to the 2026-07-24 single PORTAL_USER + PORTAL_PASSWORD operator.
# Tokens are deterministic per user so restarts don't log anyone out.
# Cloudflare Access remains the outer identity gate on app.contabia.co (File 28 B2).
# ---------------------------------------------------------------------------
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() != "false"

app = FastAPI(title="Contabia Portal Backend - Sonata Mas slice", version="2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://([a-z0-9-]+\.)?(contabia\.co|contabia-app\.pages\.dev)|http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_auth(authorization: Optional[str] = Header(None)) -> dict:
    if not auth_users.USERS:
        raise HTTPException(
            status_code=503,
            detail="No portal users configured (set PORTAL_USERS_JSON, or PORTAL_USER+PORTAL_PASSWORD)",
        )
    user = auth_users.user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Missing or invalid token - log in via /auth/login")
    return user


# ---------------------------------------------------------------------------
# Entity registry. Period structure per File 28 final decision 2026-07-17:
# opening balance locks at 2026-06-30; July 2026 is the first live period.
# ---------------------------------------------------------------------------
ENTITIES = {
    "sonata-001": {
        "name": "SONATA MAS S.A.S. (Tayrona Sailing)",
        "nit": "901528910-3",
        "csv": DATA_DIR / "exception_register.csv",          # Jan-June baseline register
        "csv_live": DATA_DIR / "exception_register_2026-07.csv",  # live-period exceptions
        "opening_balance_lock": "2026-06-30",
        "live_period": "2026-07",
        "baseline_periods": "2026-01..2026-06",
    }
}

# JE ids whose entries change an already-filed retefuente base (Gate B,
# File 28 A1.3). Never posted against a filed period - disclosed forward.
GATE_B_BLOCKED_JES = {"AJ-01-02", "AJ-N3"}


def _get_entity_or_404(entity_id: str) -> dict:
    entity = ENTITIES.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Unknown entity '{entity_id}'")
    return entity


def _load_all_exceptions(entity: dict) -> list[dict]:
    rows = load_exceptions(entity["csv"], period="2026-01")
    rows += load_exceptions(entity["csv_live"], period=entity["live_period"])
    return rows


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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS company_rules (
                rule_id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                rule_text TEXT NOT NULL,
                category TEXT,
                source TEXT NOT NULL DEFAULT 'client_choice',
                audit_tag TEXT,
                linked_exception_id TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posting_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                period TEXT NOT NULL,
                je_id TEXT NOT NULL,
                dry_run INTEGER NOT NULL,
                result TEXT,
                payload TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    boveda_data.init_boveda_table(_db)


_init_db()
seed_standing_rules(_db, "sonata-001")


def _status_overrides(table: str) -> dict[str, dict]:
    with _db() as conn:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        return {row["exception_id" if table == "exception_status" else "je_id"]: dict(row) for row in rows}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class LoginBody(BaseModel):
    username: str
    password: str


@app.post("/auth/login")
def login(body: LoginBody):
    if not auth_users.USERS:
        raise HTTPException(
            status_code=503,
            detail="No portal users configured (set PORTAL_USERS_JSON, or PORTAL_USER+PORTAL_PASSWORD)",
        )
    user = auth_users.authenticate(body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {
        "token": user["token"],
        "user": auth_users.public_user(user),
        "entities": [{"id": eid, "name": e["name"]} for eid, e in ENTITIES.items()],
        "default_entity": user["default_entity"],
    }


@app.get("/healthz")
def healthz():
    return {
        "ok": True,
        "dry_run": DRY_RUN,
        "version": "2.1",
        "users_configured": len(auth_users.USERS),
    }


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------
@app.get("/entities", dependencies=[Depends(require_auth)])
def list_entities():
    return [{"id": eid, "name": e["name"], "nit": e["nit"]} for eid, e in ENTITIES.items()]


@app.get("/entities/{entity_id}/summary", dependencies=[Depends(require_auth)])
def get_summary(entity_id: str):
    entity = _get_entity_or_404(entity_id)
    exceptions = _load_all_exceptions(entity)
    overrides = _status_overrides("exception_status")
    for e in exceptions:
        if e["id"] in overrides:
            e["status"] = overrides[e["id"]]["status"]
    ingestion = None
    ingestion_path = DATA_DIR / f"ingestion_{entity['live_period']}.json"
    if ingestion_path.exists():
        ingestion = json.loads(ingestion_path.read_text())
    cifras = summarize(exceptions)
    live_open = (cifras.get("live_period") or {}).get("open_high", 0) + (cifras.get("live_period") or {}).get("open_medium", 0) + (cifras.get("live_period") or {}).get("open_low", 0)
    live_jes = [je for je in JOURNAL_ENTRIES if je.get("bucket") == "live" and je.get("status") == "pending_edwin_approval"]
    return {
        "meta": {
            "id": entity_id,
            "name": "Tayrona Sailing",
            "legal_name": entity["name"],
            "nit": entity["nit"],
            "period": "Julio 2026",
            "period_iso": entity["live_period"],
            "close_status": "in_progress",
        },
        "ingestion": ingestion,
        "closeSummary": {
            "period": entity["live_period"],
            "opening_balance_lock": entity["opening_balance_lock"],
            "baseline_periods": entity["baseline_periods"],
            "rfr_status": "baseline_reconciliation",
            "live_status": "ingesting",
            "nothing_posted": True,
            "dry_run": DRY_RUN,
            "status_label": "EN CURSO",
        },
        "cifras": cifras,
        "nav_badges": {
            "exceptions": live_open,
            "jes": len(live_jes),
        },
        "whatsapp": {
            "mode": "self-chat",
            "hint_es": "Reenvíe documentos a su chat personal con Hermes (el mismo número). El agente los archiva en la bóveda de Tayrona.",
            "hint_en": "Forward documents to your personal Hermes self-chat (same number). The agent files them into the Tayrona vault.",
        },
    }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
@app.get("/entities/{entity_id}/exceptions", dependencies=[Depends(require_auth)])
def get_exceptions(entity_id: str, period: Optional[str] = None):
    entity = _get_entity_or_404(entity_id)
    exceptions = _load_all_exceptions(entity)
    if period:
        exceptions = [e for e in exceptions if e["period"] == period]
    overrides = _status_overrides("exception_status")
    for e in exceptions:
        if e["id"] in overrides:
            e["status"] = overrides[e["id"]]["status"]
            e["rejection_note"] = overrides[e["id"]].get("rejection_note")
    return exceptions


class ExceptionPatch(BaseModel):
    status: Literal["approved", "rejected"]
    rejection_note: Optional[str] = None


@app.patch("/entities/{entity_id}/exceptions/{exc_id}", dependencies=[Depends(require_auth)])
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
# Journal entries
# ---------------------------------------------------------------------------
@app.get("/entities/{entity_id}/journal-entries", dependencies=[Depends(require_auth)])
def get_journal_entries(entity_id: str):
    _get_entity_or_404(entity_id)
    overrides = _status_overrides("je_status")
    entries = [dict(je) for je in JOURNAL_ENTRIES]
    for je in entries:
        if je["id"] in overrides:
            je["status"] = overrides[je["id"]]["status"]
            je["rejection_note"] = overrides[je["id"]].get("rejection_note")
        je["gate_b"] = "disclose_forward" if je["id"] in GATE_B_BLOCKED_JES else "postable_now"
        je.setdefault("period", "2026-01")
        je.setdefault("bucket", "baseline" if je.get("period", "2026-01") < "2026-07" else "live")
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


@app.patch("/entities/{entity_id}/journal-entries/{je_id}", dependencies=[Depends(require_auth)])
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
# Company config rules - two-bucket design per the Ingestion & Motor Flow doc
# (2026-07-13): 'motor_fix' patches global behavior (logged with citation),
# 'client_choice' is the client's own call, stored once, never re-asked.
# audit_tag is the silent backend distinction within client_choice
# ('no_obligation' vs 'informed_decline') - defensibility, never surfaced
# as friction (File 13 Operating Principle 5).
# ---------------------------------------------------------------------------
class RuleCreate(BaseModel):
    rule_text: str
    category: Optional[str] = None          # categorization | retention | payroll | banking | other
    source: Literal["client_choice", "motor_fix"] = "client_choice"
    audit_tag: Optional[Literal["no_obligation", "informed_decline"]] = None
    linked_exception_id: Optional[str] = None
    created_by: Optional[str] = "portal"


class RulePatch(BaseModel):
    rule_text: Optional[str] = None
    category: Optional[str] = None
    active: Optional[bool] = None
    audit_tag: Optional[Literal["no_obligation", "informed_decline"]] = None


@app.get("/entities/{entity_id}/rules", dependencies=[Depends(require_auth)])
def list_rules(entity_id: str, include_inactive: bool = False):
    _get_entity_or_404(entity_id)
    q = "SELECT * FROM company_rules WHERE entity_id = ?"
    if not include_inactive:
        q += " AND active = 1"
    q += " ORDER BY created_at DESC"
    with _db() as conn:
        return [dict(r) for r in conn.execute(q, (entity_id,)).fetchall()]


@app.post("/entities/{entity_id}/rules", dependencies=[Depends(require_auth)])
def create_rule(entity_id: str, body: RuleCreate):
    _get_entity_or_404(entity_id)
    rule_id = f"CR-{uuid.uuid4().hex[:8]}"
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO company_rules
                (rule_id, entity_id, rule_text, category, source, audit_tag,
                 linked_exception_id, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (rule_id, entity_id, body.rule_text, body.category, body.source,
             body.audit_tag, body.linked_exception_id, body.created_by),
        )
        row = conn.execute("SELECT * FROM company_rules WHERE rule_id = ?", (rule_id,)).fetchone()
    return dict(row)


@app.patch("/entities/{entity_id}/rules/{rule_id}", dependencies=[Depends(require_auth)])
def patch_rule(entity_id: str, rule_id: str, body: RulePatch):
    _get_entity_or_404(entity_id)
    sets, vals = [], []
    if body.rule_text is not None:
        sets.append("rule_text = ?"); vals.append(body.rule_text)
    if body.category is not None:
        sets.append("category = ?"); vals.append(body.category)
    if body.active is not None:
        sets.append("active = ?"); vals.append(1 if body.active else 0)
    if body.audit_tag is not None:
        sets.append("audit_tag = ?"); vals.append(body.audit_tag)
    if not sets:
        raise HTTPException(status_code=400, detail="Nothing to update")
    sets.append("updated_at = ?"); vals.append(datetime.now(timezone.utc).isoformat())
    vals += [rule_id, entity_id]
    with _db() as conn:
        cur = conn.execute(
            f"UPDATE company_rules SET {', '.join(sets)} WHERE rule_id = ? AND entity_id = ?", vals
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Unknown rule '{rule_id}'")
        row = conn.execute("SELECT * FROM company_rules WHERE rule_id = ?", (rule_id,)).fetchone()
    return dict(row)


# ---------------------------------------------------------------------------
# Posting - the "~20-line addition" from the 2026-07-10 handoff, plus the
# guards it always needed. DRY_RUN defaults true: nothing writes to Alegra
# until the env flag is flipped at July close (File 28 A2.6).
# ---------------------------------------------------------------------------
def _je_to_alegra_payload(je: dict, period: str) -> dict:
    """Build the /journals payload. Account names here are the register's
    human-readable names; live posting requires an account-id mapping rule
    (company_rules category 'account_map') before the flag ever flips."""
    return {
        "date": f"{period}-31" if period.endswith("-07") else f"{period}-28",
        "observations": f"ContabIA {je['id']}: {je['description']}",
        "entries": [
            {
                "account": line["account"],
                "debit": line.get("debit") or 0,
                "credit": line.get("credit") or 0,
            }
            for line in je.get("lines", [])
        ],
    }


@app.post("/entities/{entity_id}/close/{period}/post", dependencies=[Depends(require_auth)])
def post_period(entity_id: str, period: str):
    _get_entity_or_404(entity_id)
    overrides = _status_overrides("je_status")
    approved, skipped = [], []
    for je in JOURNAL_ENTRIES:
        status = overrides.get(je["id"], {}).get("status", je["status"])
        if status != "approved_by_edwin":
            skipped.append({"je_id": je["id"], "reason": f"status={status}"})
            continue
        if je["id"] in GATE_B_BLOCKED_JES:
            skipped.append({
                "je_id": je["id"],
                "reason": "gate_b: touches an already-filed retefuente base - disclose forward, never post (File 28 A1.3)",
            })
            continue
        approved.append(je)

    results = []
    client = None
    if not DRY_RUN:
        try:
            client = AlegraClient()
        except AlegraAuthError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    for je in approved:
        payload = _je_to_alegra_payload(je, period)
        if DRY_RUN:
            outcome = {"je_id": je["id"], "dry_run": True, "would_post": payload}
        else:
            try:
                resp = client.post_journal(payload)
                outcome = {"je_id": je["id"], "dry_run": False, "posted": True, "alegra_id": resp.get("id")}
            except Exception as exc:  # keep looping; report per-entry
                outcome = {"je_id": je["id"], "dry_run": False, "posted": False, "error": str(exc)}
        results.append(outcome)
        with _db() as conn:
            conn.execute(
                "INSERT INTO posting_log (entity_id, period, je_id, dry_run, result, payload) VALUES (?, ?, ?, ?, ?, ?)",
                (entity_id, period, je["id"], 1 if DRY_RUN else 0,
                 json.dumps(outcome, default=str), json.dumps(payload, default=str)),
            )
        log.info("posting[%s dry_run=%s] %s", period, DRY_RUN, outcome)

    return {
        "period": period,
        "dry_run": DRY_RUN,
        "posted_or_would_post": results,
        "skipped": skipped,
        "note": "DRY_RUN=true: payloads logged, nothing written to Alegra." if DRY_RUN else "LIVE posting.",
    }


@app.get("/entities/{entity_id}/posting-log", dependencies=[Depends(require_auth)])
def get_posting_log(entity_id: str):
    _get_entity_or_404(entity_id)
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM posting_log WHERE entity_id = ? ORDER BY id DESC LIMIT 100", (entity_id,)
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Live Alegra cross-check - read-only.
# ---------------------------------------------------------------------------
@app.get("/entities/{entity_id}/alegra-check", dependencies=[Depends(require_auth)])
def alegra_check(entity_id: str, year: int = 2026, month: int = 7):
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
        "note": "Read-only - nothing posts without accountant approval.",
    }


# ---------------------------------------------------------------------------
# Boveda (document vault) - unchanged from v1 except auth.
# ---------------------------------------------------------------------------
@app.post("/entities/{entity_id}/boveda/upload", dependencies=[Depends(require_auth)])
async def upload_boveda_file(
    entity_id: str,
    file: UploadFile = File(...),
    folder: str = Form("General"),
    tags: str = Form(""),
    linked_exception_id: Optional[str] = Form(None),
    uploaded_by: str = Form("portal"),
):
    _get_entity_or_404(entity_id)
    file_bytes = await file.read()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    return boveda_data.save_upload(
        _db, BOVEDA_DIR, entity_id, file.filename, file_bytes,
        folder=folder, tags=tag_list,
        linked_exception_id=linked_exception_id, uploaded_by=uploaded_by,
    )


@app.get("/entities/{entity_id}/boveda", dependencies=[Depends(require_auth)])
def list_boveda_files(entity_id: str, folder: Optional[str] = None):
    _get_entity_or_404(entity_id)
    return boveda_data.list_files(_db, entity_id, folder=folder)


@app.get("/entities/{entity_id}/boveda/{file_id}/download", dependencies=[Depends(require_auth)])
def download_boveda_file(entity_id: str, file_id: str):
    _get_entity_or_404(entity_id)
    record = boveda_data.get_file(_db, entity_id, file_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Unknown boveda file '{file_id}'")
    path = Path(record["stored_path"])
    if not path.exists():
        raise HTTPException(status_code=410, detail="File metadata exists but bytes are missing on disk")
    return FileResponse(path, filename=record["filename"])


class BovedaPatch(BaseModel):
    folder: Optional[str] = None
    tags: Optional[list[str]] = None


@app.patch("/entities/{entity_id}/boveda/{file_id}", dependencies=[Depends(require_auth)])
def patch_boveda_file(entity_id: str, file_id: str, patch: BovedaPatch):
    _get_entity_or_404(entity_id)
    updated = boveda_data.update_file(_db, entity_id, file_id, folder=patch.folder, tags=patch.tags)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Unknown boveda file '{file_id}'")
    return updated


@app.post("/entities/{entity_id}/boveda/{file_id}/mark-processed", dependencies=[Depends(require_auth)])
def mark_boveda_file_processed(entity_id: str, file_id: str, linked_to: Optional[str] = None):
    _get_entity_or_404(entity_id)
    updated = boveda_data.mark_processed(_db, entity_id, file_id, linked_to=linked_to)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Unknown boveda file '{file_id}'")
    return updated


# ---------------------------------------------------------------------------
# Portal chat → Hermes (business profile, Tayrona source).
# Hermes API server stays on loopback; this proxy is the only public hop.
# WhatsApp self-chat on Kevin's personal number remains the document-forward
# rail — the portal never invents cifras.
# ---------------------------------------------------------------------------
HERMES_CHAT_URL = os.environ.get("HERMES_CHAT_URL", "http://127.0.0.1:8642/p/business/v1/chat/completions")
HERMES_CHAT_KEY = os.environ.get("HERMES_CHAT_KEY", "")
HERMES_CHAT_FALLBACK_URL = os.environ.get("HERMES_CHAT_FALLBACK_URL", "http://127.0.0.1:8642/v1/chat/completions")


class ChatBody(BaseModel):
    message: str
    lang: Optional[str] = "es"
    session_id: Optional[str] = None


@app.get("/entities/{entity_id}/chat/status", dependencies=[Depends(require_auth)])
def chat_status(entity_id: str):
    _get_entity_or_404(entity_id)
    configured = bool(HERMES_CHAT_KEY)
    return {
        "wired": configured,
        "profile": "business",
        "source": "tayrona",
        "whatsapp": {
            "mode": "self-chat",
            "number_hint": "+57 301 441 0022",
            "hint_es": "Reenvíe documentos a su chat personal con Hermes (el mismo número). El agente los archiva en la bóveda de Tayrona.",
            "hint_en": "Forward documents to your personal Hermes self-chat (same number). The agent files them into the Tayrona vault.",
        },
    }


@app.post("/entities/{entity_id}/chat", dependencies=[Depends(require_auth)])
def portal_chat(entity_id: str, body: ChatBody, user: dict = Depends(require_auth)):
    _get_entity_or_404(entity_id)
    if not HERMES_CHAT_KEY:
        raise HTTPException(
            status_code=503,
            detail="Agente no conectado. Reenvíe por WhatsApp a su chat personal con Hermes.",
        )
    lang = (body.lang or "es").lower()
    if lang not in {"es", "en"}:
        lang = "es"
    session_id = body.session_id or f"portal-{entity_id}-{user.get('username', 'user')}"
    system = (
        "You are the ContabIA agent for Tayrona Sailing (Sonata Mas SAS, NIT 901528910, "
        "entity sonata-001). Period in progress: July 2026 (EN CURSO). "
        "Work under Hermes profile `business` with --source tayrona. "
        "Never invent cifras. If you do not have a live number, say so and point to "
        "Excepciones / Comprobantes. Do not offer Cantamar as a live entity. "
        "WhatsApp document intake is Kevin's personal self-chat — tell the user to "
        "forward files there, not to invent a ContabIA business number. "
        f"Reply in {'Spanish' if lang == 'es' else 'English'}."
    )
    payload = {
        "model": "hermes-agent",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": body.message},
        ],
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {HERMES_CHAT_KEY}",
        "Content-Type": "application/json",
        "X-Hermes-Session-Id": session_id,
        "X-Hermes-Session-Key": f"contabia:portal:{entity_id}:{user.get('username', 'user')}",
    }
    import urllib.error
    import urllib.request

    def _post(url: str):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        try:
            data = _post(HERMES_CHAT_URL)
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and HERMES_CHAT_FALLBACK_URL != HERMES_CHAT_URL:
                data = _post(HERMES_CHAT_FALLBACK_URL)
            else:
                raise
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise HTTPException(status_code=502, detail=f"Hermes {exc.code}: {detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Hermes no disponible: {exc}") from exc

    choices = data.get("choices") or []
    text = ""
    if choices:
        text = ((choices[0].get("message") or {}).get("content")) or ""
    return {"reply": text, "session_id": session_id, "source": "tayrona"}
