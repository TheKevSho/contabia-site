#!/usr/bin/env python3
"""Phase 1 — canonical .md → SQLite derived index (Motor-Checklist Phase 1).

REBUILT 2026-09-18. The original derive_index.py (built 2026-09-09) was lost
in the Time Machine restore — never committed; the Time Machine drive has no
backup between 2026-08-24 and the restore. Rebuilt from spec (File 07, 2026-08-08
per-document knowledge graph section + the 09-09 build table): .md files are the
SYSTEM OF RECORD; SQLite (canonical_documents) is a derived, disposable index
that is never a peer writer. Design rule #1: index is always rm-and-rebuildable
from .md; never hand-repaired.

Idempotency contract (code-review finding, 09-17: "genuinely idempotent"):
  - content-hash compare -> unchanged files SKIP (no row churn, run_sha intact)
  - changed files -> ON CONFLICT(path) DO UPDATE (regeneration is a merge,
    never a clobber — File 07 design rule 2b: no --force, no DELETE first)
  - run-pinned: every row records the git SHA that produced it
    (RAILWAY_GIT_COMMIT_SHA env or `git rev-parse HEAD`, else 'local')

Zero LLM, pure stdlib + sqlite3. Parse format: YAML `---` frontmatter OR the
migrated bold-KV form (`**Source:**`, `**Filed:**`, `**Entity:**` lines), H1
title, `## ` body sections (tables parsed for structured fields), wiki-links.

Usage:
    python3 derive_index.py --mock            # synthetic corpus in a tmp dir
    python3 derive_index.py --data-dir data/boveda_seed
    python3 derive_index.py --data-dir data/boveda_tayrona --entity tayrona
    python3 derive_index.py --mock --json     # report as JSON
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(os.environ.get("CONTABIA_DB_PATH", Path(__file__).parent / "sonata_mas_001.sqlite"))


# ---------------------------------------------------------------------------
# Run pinning — every row records which git SHA (or env) produced it
# ---------------------------------------------------------------------------
def _git_sha() -> str:
    env_sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "").strip()
    if env_sha:
        return env_sha
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
            cwd=Path(__file__).parent,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "local"


def _git_author() -> str:
    return os.environ.get("GIT_AUTHOR_NAME", "") or os.environ.get("USER", "unknown")


# ---------------------------------------------------------------------------
# .md parsing — YAML frontmatter OR bold-KV, H1 title, sections, tables
# ---------------------------------------------------------------------------
def _parse_yaml_scalar(raw: str) -> Any:
    """Tiny YAML-subset scalar parser: strings, numbers, true/false, lists,
    and [[wiki-links]]. Full PyYAML is not a dependency — this covers the
    canonical frontmatter vocabulary (File 07: vendor, amount, date, type,
    confidence, flags, hash, locked_fields, ...)."""
    s = raw.strip()
    if not s:
        return None
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    if s.lower() in ("null", "none", "~"):
        return None
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return s
    if re.fullmatch(r"-?\d+(\.\d+)?", s.replace(",", "")):
        try:
            return float(s.replace(",", ""))
        except ValueError:
            pass
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    return s


def _parse_frontmatter(text: str) -> dict:
    """Accept either a YAML `---` block or the migrated bold-KV header
    (`**Key:** value` lines before the first `## ` heading). Never raises."""
    front: dict[str, Any] = {}
    stripped = text.lstrip("\ufeff \t\r\n")

    # YAML block
    if stripped.startswith("---"):
        end = stripped.find("\n---", 3)
        if end != -1:
            block = stripped[3:end]
            key = None
            for line in block.splitlines():
                line = line.rstrip()
                if not line.strip() or line.strip().startswith("#"):
                    continue
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line):
                    key, _, val = line.partition(":")
                    front[key.strip()] = _parse_yaml_scalar(val)
                elif key and line.startswith("  ") or line.startswith("- "):
                    # list continuation under an existing key (best effort)
                    pass
            return front

    # Bold-KV header: **Key:** value lines before the first ## heading.
    header, _, _ = stripped.partition("\n## ")
    for line in header.splitlines():
        m = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", line.strip())
        if m:
            key = m.group(1).strip().lower().replace(" ", "_")
            front[key] = _parse_yaml_scalar(m.group(2).strip())
    return front


def _parse_markdown(text: str) -> dict:
    """Split a canonical .md into its structured parts. Returns:
      {title, frontmatter, sections: {heading: raw}, wiki_links: [...]}"""
    text = text.lstrip("\ufeff")
    frontmatter = _parse_frontmatter(text)
    stripped = text.lstrip("\ufeff \t\r\n")
    if stripped.startswith("---") and stripped.find("\n---", 3) != -1:
        text = stripped[stripped.find("\n---", 3) + 5:]

    title = ""
    sections: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = ""
            continue
        if current and line.strip():
            sections[current] = sections[current] + line + "\n"
        elif not current and line.startswith("**") and ":" in line:
            pass  # bold-KV header line, already consumed via frontmatter
    wiki_links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text)
    return {"title": title, "frontmatter": frontmatter, "sections": sections,
            "wiki_links": wiki_links}


def _parse_table(section: str) -> list[list[str]]:
    """Rows of a markdown table (header + separator skipped)."""
    rows = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s:|-]+\|$", line):
            continue
        cells = [c.strip().strip("`").strip("**").strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def _cell_num(cell: str) -> Optional[float]:
    """parse_cop-lite for cells already stripped of markup: thousands dot +
    comma decimal, US comma thousands, or a plain number."""
    from cfd_engine import parse_cop  # reuse the calibrated parser

    try:
        return parse_cop(cell)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Field derivation from a parsed .md (documents are the SSOT; every column is
# derived, never hand-typed into the DB)
# ---------------------------------------------------------------------------
def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or f"doc-{uuid.uuid4().hex[:8]}"


def _find_period(front: dict, title: str, text: str, path: str) -> str:
    """YYYY-MM: frontmatter period/date, then the Filed/Source path, then
    title, then filename. The migrated docs file under `2026-07 Julio/`."""
    candidates = [
        front.get("period"), front.get("date"), front.get("filed"),
        front.get("source"), title, str(path),
    ]
    for c in candidates:
        if not c:
            continue
        m = re.search(r"(20\d{2})[-/年]?\s*(\d{2})", str(c))
        if m and 1 <= int(m.group(2)) <= 12:
            return f"{m.group(1)}-{m.group(2)}"
    return ""


def _find_amount(front: dict, sections: dict) -> Optional[float]:
    """amount_cop: frontmatter amount, else the first table row whose label
    contains 'Valor total' / 'Amount' / 'Monto' (the Bold specimen's gross
    sales figure). All numbers come from the document, never from literals."""
    if front.get("amount") is not None:
        try:
            return float(front["amount"]) if isinstance(front["amount"], (int, float)) else _cell_num(str(front["amount"]))
        except (TypeError, ValueError):
            pass
    for section in sections.values():
        for row in _parse_table(section):
            if len(row) >= 2 and any(k in row[0].lower() for k in ("valor total", "amount", "monto total", "total valor")):
                num = _cell_num(row[1])
                if num is not None:
                    return num
    return None


def _find_date(front: dict, text: str) -> str:
    for c in (front.get("date"), front.get("source"), front.get("filed")):
        if not c:
            continue
        m = re.search(r"(20\d{2}-\d{2}-\d{2})", str(c))
        if m:
            return m.group(1)
    return ""


def _find_vendor(front: dict, title: str) -> str:
    v = front.get("vendor") or front.get("merchant")
    if v:
        return str(v)
    m = re.match(r"^([^—–\-|]+)", title.strip())
    if m:
        return m.group(1).strip()
    return "unknown"


def _infer_type(filename: str, front: dict) -> str:
    t = front.get("type")
    if t:
        return str(t)
    fn = filename.lower()
    if "transacciones" in fn or "statement" in fn or "extracto" in fn:
        if "bold" in fn:
            return "card_statement"
        return "bank_statement"
    if "planilla" in fn or "pila" in fn:
        return "payroll"
    if "dashboard" in fn:
        return "report"
    return "document"


def parse_document(path: Path) -> dict:
    """Parse one canonical .md into DB-ready derived fields."""
    text = path.read_text(encoding="utf-8", errors="replace")
    parsed = _parse_markdown(text)
    front = parsed["frontmatter"]
    sections = parsed["sections"]

    doc_id_links = [l for l in parsed["wiki_links"] if l.lower().startswith("doc:")]
    doc_id = doc_id_links[0].split(":")[1].strip() if doc_id_links else _slug(path.stem)

    amount = _find_amount(front, sections)
    period = _find_period(front, parsed["title"], text, str(path))
    return {
        "doc_id": doc_id,
        "filename": path.name,
        "path": str(path),
        "title": parsed["title"],
        "vendor": _find_vendor(front, parsed["title"]),
        "amount_cop": amount,
        "period": period,
        "doc_date": _find_date(front, text),
        "doc_type": _infer_type(path.name, front),
        "confidence": str(front.get("confidence") or ""),
        "flags": json.dumps(front.get("flags") or [], ensure_ascii=False),
        "locked_fields": json.dumps(front.get("locked_fields") or [], ensure_ascii=False),
        "hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "frontmatter": json.dumps(front, ensure_ascii=False, default=str),
        "sections": json.dumps(sections, ensure_ascii=False, default=str),
        "wiki_links": json.dumps(parsed["wiki_links"], ensure_ascii=False),
    }


# ---------------------------------------------------------------------------
# SQLite derived index
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS canonical_documents (
    doc_id        TEXT PRIMARY KEY,
    filename      TEXT NOT NULL,
    path          TEXT NOT NULL UNIQUE,
    title         TEXT,
    entity        TEXT,
    vendor        TEXT,
    amount_cop    REAL,
    period        TEXT,
    doc_date      TEXT,
    doc_type      TEXT,
    confidence    TEXT,
    flags         TEXT,
    locked_fields TEXT,
    hash          TEXT NOT NULL,
    frontmatter   TEXT,
    sections      TEXT,
    wiki_links    TEXT,
    run_sha       TEXT,
    git_author    TEXT,
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at    TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def index_one(conn: sqlite3.Connection, path: Path, entity: str,
              run_sha: str, git_author: str) -> str:
    """Index one file. Returns 'new' | 'updated' | 'skipped' | 'error'.
    Hash-compare first: unchanged content skips without touching the row
    (run_sha stays pinned to the run that produced it). Changed content
    merges via ON CONFLICT(doc_id) DO UPDATE — regeneration is a merge, never
    a clobber (File 07 design rule 2b; no DELETE-then-INSERT). A doc_id
    claimed by two files with DIFFERENT content is a genuine collision and is
    surfaced, never last-write-wins; a doc whose file merely MOVED (same
    content, same id, new path) merges cleanly."""
    try:
        doc = parse_document(path)
    except Exception as exc:
        return f"error:parse:{type(exc).__name__}: {exc}"

    by_path = conn.execute(
        "SELECT hash FROM canonical_documents WHERE path = ?", (doc["path"],)
    ).fetchone()
    by_id = conn.execute(
        "SELECT hash, path FROM canonical_documents WHERE doc_id = ?", (doc["doc_id"],)
    ).fetchone()

    if by_path is not None and by_path["hash"] == doc["hash"]:
        return "skipped"  # content-identical: the index is already current

    if by_id is not None and by_id["path"] != doc["path"]:
        if by_id["hash"] != doc["hash"]:
            return (f"error:doc_id_collision: '{doc['doc_id']}' claimed by "
                    f"'{by_id['path']}' and '{doc['path']}' with different content")
        # same content, moved file: falls through to the doc_id merge below

    now = datetime.now(timezone.utc).isoformat()
    row = (doc["doc_id"], doc["filename"], doc["path"], doc["title"], entity,
           doc["vendor"], doc["amount_cop"], doc["period"], doc["doc_date"],
           doc["doc_type"], doc["confidence"], doc["flags"], doc["locked_fields"],
           doc["hash"], doc["frontmatter"], doc["sections"], doc["wiki_links"],
           run_sha, git_author, now, now)
    try:
        conn.execute(
            """
            INSERT INTO canonical_documents
                (doc_id, filename, path, title, entity, vendor, amount_cop,
                 period, doc_date, doc_type, confidence, flags, locked_fields,
                 hash, frontmatter, sections, wiki_links, run_sha, git_author,
                 updated_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(doc_id) DO UPDATE SET
                filename = excluded.filename,
                path = excluded.path,
                title = excluded.title,
                entity = excluded.entity,
                vendor = excluded.vendor,
                amount_cop = excluded.amount_cop,
                period = excluded.period,
                doc_date = excluded.doc_date,
                doc_type = excluded.doc_type,
                confidence = excluded.confidence,
                flags = excluded.flags,
                locked_fields = excluded.locked_fields,
                hash = excluded.hash,
                frontmatter = excluded.frontmatter,
                sections = excluded.sections,
                wiki_links = excluded.wiki_links,
                run_sha = excluded.run_sha,
                git_author = excluded.git_author,
                updated_at = excluded.updated_at
            """,
            row,
        )
        if by_path is not None or by_id is not None:
            return "updated"
        return "new"
    except sqlite3.IntegrityError as exc:
        # Another row already holds this path (two files, one path identity):
        # surfaced, not silently resolved.
        return f"error:path_collision: {exc}"


def index_markdown_files(md_files: list[Path], entity: str,
                         db_path: Path = DB_PATH) -> dict:
    """Index every file that still exists; return the change report. Files no
    longer on disk are NOT deleted from the index (a derived index may be
    rebuilt wholesale from .md — that is the rm-and-rebuild path; an
    incremental run never destroys rows for docs that merely moved)."""
    run_sha, author = _git_sha(), _git_author()
    counts = {"scanned": 0, "new": 0, "updated": 0, "skipped": 0, "errors": []}
    conn = _connect(db_path)
    try:
        for path in sorted(md_files):
            if path.suffix.lower() != ".md":
                continue
            counts["scanned"] += 1
            result = index_one(conn, path, entity, run_sha, author)
            if result == "new":
                counts["new"] += 1
            elif result == "updated":
                counts["updated"] += 1
            elif result == "skipped":
                counts["skipped"] += 1
            else:
                counts["errors"].append(f"{path.name}: {result}")
        conn.commit()
    finally:
        conn.close()
    counts["errors"] = counts["errors"][:20]  # cap pathological corpora
    return {
        "phase": "derive_index",
        "entity": entity,
        "db": str(db_path),
        "run_sha": run_sha,
        "git_author": author,
        **counts,
    }


def format_report(report: dict) -> str:
    return (
        "╔══════════════════════════════════════════════════╗\n"
        "║  PHASE 1 — CANONICAL .md → SQLite DERIVED INDEX   ║\n"
        "╚══════════════════════════════════════════════════╝\n"
        f"  Entity: {report['entity']}   DB: {report['db']}\n"
        f"  Run pinned to: {report['run_sha']}  (git_author: {report['git_author']})\n"
        f"  Scanned: {report['scanned']}   new: {report['new']}   "
        f"updated: {report['updated']}   unchanged (skipped): {report['skipped']}\n"
        + ("  Errors:\n    - " + "\n    - ".join(report["errors"]) if report["errors"] else "  Errors: none")
    )


# ---------------------------------------------------------------------------
# Mock corpus — synthetic canonical .md files in a tmp dir
# ---------------------------------------------------------------------------
MOCK_MD = {
    "Bold_Transacciones_2026-07.md": """# Bold — Transacciones Julio 2026

**Source:** `Reporte_mensual_de_transacciones_2026-07.xlsx` (WhatsApp, received 2026-08-24)
**Filed:** `tayrona-sailing/raw-accounting/2026-07 Julio/Bold_Transacciones_2026-07.xlsx`
**Entity:** Tayrona Sailing (Sonata Mas S.A.S.) · Merchant `OZHEDYEVUL`

## Summary

| Metric | Value |
|---|---|
| Transactions | 13 |
| Period | 2026-07-01 → 2026-07-30 |
| **Valor total (gross sales)** | **COP 9,491,500.00** |
| Bold fees + retentions deducted | COP 577,735.85 |
| **Deposited to sales balance** | **COP 8,913,764.15** |

## Extraction detail

[[doc:202607-bold-transacciones]]

- Datáfono: 11 transactions — COP 3,541,500 gross
- Link de pago: 2 transactions — COP 5,600,000 gross
""",
    "DetallePlanilla_38244858_2026_07_E.md": """# PILA — Detalle Planilla Julio 2026

**Source:** `DetallePlanilla_38244858_2026_07_E.pdf`
**Filed:** `tayrona-sailing/raw-accounting/2026-07 Julio/`
**Entity:** Tayrona Sailing (Sonata Mas S.A.S.)

## Summary

| Metric | Value |
|---|---|
| Period | 2026-07 |
| **Valor total** | **COP 2,164,950** |

## Agent analysis

[[doc:202607-pila]] July payroll contributions.
""",
    "exception_register_2026-07.md": """# Exception register — Julio 2026

**Type:** register
**Amount:** 3092000
**Confidence:** high
**Flags:** [reconciled]
**Locked fields:** [amount_cop]

## Decision trail

[[doc:202607-exceptions]] Register rows survive July — the lock endings are
authoritative (EX-J07-01..EX-J07-18, EX-A08-01..06).
""",
}


def mock_corpus(workdir: Path) -> list[Path]:
    d = workdir / "mock_boveda"
    d.mkdir(exist_ok=True)
    paths = []
    for name, content in MOCK_MD.items():
        p = d / name
        p.write_text(content, encoding="utf-8")
        paths.append(p)
    return paths


# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 1 — canonical .md → SQLite index")
    parser.add_argument("--entity", default="tayrona", help="Entity slug for the rows")
    parser.add_argument("--data-dir", type=Path, help="Directory of canonical .md files (default data/boveda_tayrona)")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="SQLite path (default CONTABIA_DB_PATH)")
    parser.add_argument("--mock", action="store_true", help="Index a synthetic tmp corpus instead")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = parser.parse_args()

    if args.mock:
        # Stable corpus dir (not a fresh tmpdir per run) so a second --mock
        # run hits the real hash-compare path and reports all-skipped.
        corpus_dir = Path(tempfile.gettempdir()) / "derive_index_mock_corpus"
        corpus_dir.mkdir(exist_ok=True)
        md_files = mock_corpus(corpus_dir)
        report = index_markdown_files(md_files, args.entity, args.db)
    else:
        data_dir = args.data_dir or (Path(__file__).parent / "data" / "boveda_tayrona")
        if not data_dir.exists():
            print(f"error: data dir not found: {data_dir} (use --data-dir or --mock)", file=sys.stderr)
            return 2
        md_files = sorted(data_dir.rglob("*.md"))
        report = index_markdown_files(md_files, args.entity, args.db)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print(format_report(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())