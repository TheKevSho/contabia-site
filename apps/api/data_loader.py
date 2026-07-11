"""
Loads exception_register.csv into the shape exceptions.html expects, per
File 18 (Portal & Free Scan Flow) — "the mock data shape IS the API contract."

Real source: Contabia Clients/.../outputs/exception_register.csv (Sonata Mas SAS,
January 2026 RFR review). This loader is generic per-entity — point it at any
client's exception_register.csv and it produces the same shape.
"""
import csv
import re
from pathlib import Path
from typing import Any, Optional

SEVERITY_MAP = {"HIGH": "high", "MED": "medium", "LOW": "low"}

RA_TAG_RE = re.compile(r"\bRA-\d+\b")


def _parse_amount(raw: str) -> Optional[int]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def load_exceptions(csv_path: Path) -> list[dict[str, Any]]:
    exceptions = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            disposition = row["Disposition"].strip()
            ra_match = RA_TAG_RE.search(disposition)
            exceptions.append(
                {
                    "id": row["ID"].strip(),
                    "category": "exception",  # unified queue discriminator, per
                    # Continuation-Portal-and-Repo.md (exception | diagnostic_finding | prior_period_changed)
                    "phase": row["Phase"].strip(),
                    "severity": SEVERITY_MAP.get(row["Severity"].strip(), "medium"),
                    "title": row["Title"].strip(),
                    "amount_cop": _parse_amount(row["Amount_COP"]),
                    "owner": row["Owner"].strip(),
                    "proposed_je_ref": row["Proposed_JE"].strip() or None,
                    "status": row["Status"].strip().lower(),  # open | closed
                    "disposition": disposition,
                    "accepted_risk_tag": ra_match.group(0) if ra_match else None,
                }
            )
    return exceptions


def summarize(exceptions: list[dict[str, Any]]) -> dict[str, Any]:
    open_high = [e for e in exceptions if e["status"] == "open" and e["severity"] == "high"]
    open_med = [e for e in exceptions if e["status"] == "open" and e["severity"] == "medium"]
    open_low = [e for e in exceptions if e["status"] == "open" and e["severity"] == "low"]
    closed = [e for e in exceptions if e["status"] == "closed"]
    return {
        "total": len(exceptions),
        "open_high": len(open_high),
        "open_medium": len(open_med),
        "open_low": len(open_low),
        "closed": len(closed),
    }
