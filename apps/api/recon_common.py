#!/usr/bin/env python3
"""Shared line-level plumbing for the recon phases (revenue/expense/bank).

REBUILT 2026-09-18 as part of the motor rebuild. This module exists because
the 2026-09-17 review (finding #3) demanded REAL line-level parsing: the old
recons emitted hardcoded figures keyed to string matches (correct for exactly
one file); the rebuilds derive every amount from the canonical .md fields and
the bank/Bold line data. These helpers are the shared, stdlib-only base:

  xlsx_rows()              — row-major cell values from a .xlsx (zipfile+XML)
  load_exception_register()— exception_register_*.csv -> list of dicts
  period_files()           — files in a data dir whose name carries the period
  canonical_docs()         — canonical .md docs for a period (file scan AND
                             the derived index, whichever exists)
  parse_amount()           — parse_cop wrapper returning None instead of
                             raising (the recon style: bad cell -> None + skip)

Zero LLM, pure stdlib. No literals in parsing paths — every number flows from
a document cell.
"""

from __future__ import annotations

import csv
import sqlite3
import zipfile
from pathlib import Path
from typing import Any, Iterator, Optional
from xml.etree import ElementTree as ET

_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def xlsx_rows(path: Path) -> Iterator[list[str]]:
    """Row-major cell values from the first worksheet of a .xlsx.

    Handles shared strings (t="s"), inline strings (t="inlineStr"), numbers
    and dates-as-strings. Relative order is preserved; empty trailing cells
    render as ''. This is the line-level source for the Bancolombia/Bold
    statements without any non-stdlib dependency."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.iter(f"{{{_NS}}}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{_NS}}}t")))

        sheet_path = next(
            (c for c in ("xl/worksheets/sheet1.xml", "xl/worksheets/sheet.xml") if c in names),
            None,
        )
        if sheet_path is None:
            raise ValueError(f"{path.name}: no worksheet found in archive")

        root = ET.fromstring(z.read(sheet_path))
        for row in root.iter(f"{{{_NS}}}row"):
            cells: list[str] = []
            for c in row.iter(f"{{{_NS}}}c"):
                t = c.get("t")
                v = c.find(f"{{{_NS}}}v")
                if t == "s":
                    idx = int((v.text if v is not None else "0") or "0")
                    cells.append(shared[idx] if idx < len(shared) else "")
                elif t == "inlineStr":
                    is_el = c.find(f"{{{_NS}}}is")
                    if is_el is not None:
                        cells.append("".join(tt.text or "" for tt in is_el.iter(f"{{{_NS}}}t")))
                    else:
                        cells.append("")
                else:
                    cells.append((v.text or "") if v is not None else "")
            if cells:
                yield cells


def load_exception_register(path: Path) -> list[dict]:
    """exception_register_*.csv -> rows as dicts. Never raises on a bad row
    (caught + skipped); the register is a SSOT companion, not a gate."""
    rows: list[dict] = []
    if not path.exists():
        return rows
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            row = {k.strip(): (v or "").strip() for k, v in row.items()}
            if row.get("ID"):
                rows.append(row)
    return rows


def period_files(data_dir: Path, period: str) -> list[Path]:
    """Files under data_dir whose path carries the period (2026-07, JUL2026,
    julio, ...). Same token logic the gate uses — evidence must be for THIS
    period."""
    if not data_dir.exists():
        return []
    yy, mm = period.split("-")
    month_names = {"01": "ene", "02": "feb", "03": "mar", "04": "abr", "05": "may",
                   "06": "jun", "07": "jul", "08": "ago", "09": "sep", "10": "oct",
                   "11": "nov", "12": "dic"}
    tokens = [f"{yy}{mm}", f"{yy}-{mm}", f"{yy}_{mm}", f"{yy}/{mm}", f"{mm}-{yy}",
              month_names[mm], month_names[mm] + yy[-2:]]
    out = []
    for p in sorted(data_dir.rglob("*")):
        if not p.is_file():
            continue
        low = str(p.relative_to(data_dir)).lower()
        if any(t.lower() in low for t in tokens):
            out.append(p)
    return out


def canonical_docs(data_dir: Path, period: str,
                   db_path: Optional[Path] = None) -> list[dict]:
    """Canonical .md docs for the period: files on disk parsed via
    derive_index.parse_document, PLUS rows from the derived index when the DB
    exists (a doc that was indexed from another dir still counts). Each entry
    carries the parsed doc fields and its source path."""
    from derive_index import parse_document  # pure stdlib parser

    docs: dict[str, dict] = {}
    for p in period_files(data_dir, period):
        if p.suffix.lower() != ".md":
            continue
        try:
            d = parse_document(p)
            d["path"] = str(p)
            docs[d["doc_id"]] = d
        except Exception:
            continue
    if db_path and Path(db_path).exists():
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            try:
                for r in conn.execute(
                    "SELECT doc_id, filename, path, vendor, amount_cop, period, "
                    "doc_type, frontmatter FROM canonical_documents WHERE period = ?",
                    (period,),
                ):
                    row = dict(r)
                    row["doc_id"] = row.pop("doc_id") or row["filename"]
                    docs.setdefault(row["doc_id"], row)
            finally:
                conn.close()
        except sqlite3.Error:
            pass
    return list(docs.values())


def parse_amount(value: Any) -> Optional[float]:
    """parse_cop that returns None on garbage (recon style: bad cell -> skip,
    the row still gets classified/footed, never a crash)."""
    if value is None:
        return None
    from cfd_engine import parse_cop

    try:
        return parse_cop(value)
    except ValueError:
        return None


def cell_num(cells: list[str], idx: int) -> Optional[float]:
    if idx >= len(cells):
        return None
    return parse_amount(cells[idx])


def load_registers(data_dir: Path, period: str) -> list[dict]:
    """Exception register rows for the period, merged from the period data
    dir (boveda/corpus copy) AND the deployed repo registers
    (data/exception_register*.csv). Rows are keyed by ID and the deployed
    repo copy WINS — the corpus copy can be a stale upload snapshot (real
    case: boveda_seed has EX-J07-12 'Open / defer 5,600,000' while the live
    register says 'Closed / would double'). The live judgment must drive."""
    merged: dict[str, dict] = {}
    sources: list[Path] = []
    if data_dir is not None:
        dd = find_file(data_dir, "exception_register") or find_file(data_dir, "exception")
        if dd is not None:
            sources.append(dd)
    repo_dir = Path(__file__).parent / "data"
    if repo_dir.exists():
        sources.extend(sorted(repo_dir.glob("exception_register*.csv")))
    for src in sources:
        for r in load_exception_register(src):
            per = r.get("Period") or ""
            if per == period or period in per:
                merged[r["ID"]] = r  # later source wins (deployed repo last)
    return list(merged.values())


def find_file(data_dir: Path, *patterns: str) -> Optional[Path]:
    """First file under data_dir whose name matches all given substrings."""
    for p in sorted(data_dir.rglob("*")):
        if not p.is_file():
            continue
        low = p.name.lower()
        if all(pat.lower() in low for pat in patterns):
            return p
    return None