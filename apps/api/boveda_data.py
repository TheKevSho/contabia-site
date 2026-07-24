"""
Boveda (document vault) - storage helpers, scoped to sonata-001.

Per File 18 (Portal & Free Scan Flow) boveda.html spec:
  POST /entities/:id/boveda/upload   multipart -> {file_id, filename, folder, tags, processed}
  GET  /entities/:id/boveda          list, optional ?folder= filter
  GET  /entities/:id/boveda/:file_id/download
  PATCH /entities/:id/boveda/:file_id  {folder?, tags?}  ("Reasignar carpeta" / "Agregar etiquetas")

Real for this pass: actual file bytes on disk + real SQLite metadata, no mock
object. NOT real for this pass: the "motor processes asynchronously" step
(webhook/polling -> processed:true + linked_to per File 18) - there is no
rules engine or OCR wired up here, so processing is a manual/stub flip via
POST /entities/:id/boveda/:file_id/mark-processed, documented as a stand-in.
WhatsApp/email auto-ingest (uploaded_by: 'whatsapp'/'email') are also not
implemented - upload is portal/API only in this pass; the uploaded_by field
exists so those sources can be added later without a schema change.
"""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def init_boveda_table(db_connect) -> None:
    with db_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS boveda_files (
                file_id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                folder TEXT NOT NULL DEFAULT 'General',
                tags TEXT NOT NULL DEFAULT '[]',
                linked_exception_id TEXT,
                uploaded_by TEXT NOT NULL DEFAULT 'portal',
                processed INTEGER NOT NULL DEFAULT 0,
                linked_to TEXT,
                stored_path TEXT NOT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def storage_dir(data_dir: Path, entity_id: str) -> Path:
    d = data_dir / "boveda" / entity_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_upload(
    db_connect,
    data_dir: Path,
    entity_id: str,
    filename: str,
    file_bytes: bytes,
    folder: str = "General",
    tags: Optional[list[str]] = None,
    linked_exception_id: Optional[str] = None,
    uploaded_by: str = "portal",
) -> dict:
    file_id = str(uuid.uuid4())
    dest_dir = storage_dir(data_dir, entity_id)
    # Keep the original filename readable on disk; file_id prefix avoids collisions.
    stored_path = dest_dir / f"{file_id}__{filename}"
    stored_path.write_bytes(file_bytes)

    tags = tags or []
    with db_connect() as conn:
        conn.execute(
            """
            INSERT INTO boveda_files
                (file_id, entity_id, filename, folder, tags, linked_exception_id,
                 uploaded_by, processed, linked_to, stored_path, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, ?)
            """,
            (
                file_id,
                entity_id,
                filename,
                folder,
                json.dumps(tags),
                linked_exception_id,
                uploaded_by,
                str(stored_path),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    return {
        "file_id": file_id,
        "filename": filename,
        "folder": folder,
        "tags": tags,
        "linked_exception_id": linked_exception_id,
        "processed": False,
    }


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["tags"] = json.loads(d["tags"]) if d.get("tags") else []
    d["processed"] = bool(d["processed"])
    return d


def list_files(db_connect, entity_id: str, folder: Optional[str] = None) -> list[dict]:
    with db_connect() as conn:
        if folder:
            rows = conn.execute(
                "SELECT * FROM boveda_files WHERE entity_id = ? AND folder = ? ORDER BY uploaded_at DESC",
                (entity_id, folder),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM boveda_files WHERE entity_id = ? ORDER BY uploaded_at DESC",
                (entity_id,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]


def get_file(db_connect, entity_id: str, file_id: str) -> Optional[dict]:
    with db_connect() as conn:
        row = conn.execute(
            "SELECT * FROM boveda_files WHERE entity_id = ? AND file_id = ?",
            (entity_id, file_id),
        ).fetchone()
        return _row_to_dict(row) if row else None


def update_file(
    db_connect,
    entity_id: str,
    file_id: str,
    folder: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Optional[dict]:
    existing = get_file(db_connect, entity_id, file_id)
    if not existing:
        return None
    new_folder = folder if folder is not None else existing["folder"]
    new_tags = tags if tags is not None else existing["tags"]
    with db_connect() as conn:
        conn.execute(
            "UPDATE boveda_files SET folder = ?, tags = ? WHERE entity_id = ? AND file_id = ?",
            (new_folder, json.dumps(new_tags), entity_id, file_id),
        )
    return get_file(db_connect, entity_id, file_id)


def mark_processed(db_connect, entity_id: str, file_id: str, linked_to: Optional[str] = None) -> Optional[dict]:
    existing = get_file(db_connect, entity_id, file_id)
    if not existing:
        return None
    with db_connect() as conn:
        conn.execute(
            "UPDATE boveda_files SET processed = 1, linked_to = ? WHERE entity_id = ? AND file_id = ?",
            (linked_to, entity_id, file_id),
        )
    return get_file(db_connect, entity_id, file_id)
