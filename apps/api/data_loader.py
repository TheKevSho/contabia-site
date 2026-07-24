"""
Loads the exception register CSVs into the API shape.

2026-07-24 update (June-lock / July-live reframe, per File 28 final decision
2026-07-17): exceptions now carry
  - period:   '2026-01'..'2026-06' rows are the Jan-June historical-baseline
              reconciliation feeding the 2026-06-30 opening-balance lock;
              '2026-07' rows are the live period, generated from July's
              Alegra ingestion.
  - gate_b:   'disclose_forward' for items whose proposed JE touches an
              already-filed retefuente base (AJ-01/AJ-02/AJ-N3 per File 28
              A1.3 / Gate B) - these must never post against a filed period.
              'postable_now' otherwise. First-pass tagging; Kevin/Edwin can
              overrule disposition in review, but the posting guard on the
              blocked JE ids in main.py is independent of this display tag.
"""
import csv
import re
from pathlib import Path

# JE refs that change an already-filed retefuente base (File 28 A1, Gate B).
_GATE_B_JE_RE = re.compile(r"AJ-0?1|AJ-0?2|AJ-N3", re.IGNORECASE)

_SEVERITY = {"HIGH": "high", "MED": "medium", "MEDIUM": "medium", "LOW": "low"}


def load_exceptions(csv_path: Path, period: str = "2026-01") -> list[dict]:
    """Parse one exception_register CSV. `period` is the default period tag
    for rows that don't carry their own Period column."""
    if not Path(csv_path).exists():
        return []
    exceptions = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("ID"):
                continue
            je_ref = (row.get("Proposed_JE") or "").strip() or None
            row_period = (row.get("Period") or "").strip() or period
            gate_b = (
                "disclose_forward"
                if je_ref and _GATE_B_JE_RE.search(je_ref) and row_period < "2026-07"
                else "postable_now"
            )
            exceptions.append(
                {
                    "id": row["ID"].strip(),
                    "category": "exception",
                    "phase": row.get("Phase", "").strip(),
                    "severity": _SEVERITY.get(row.get("Severity", "").strip().upper(), "medium"),
                    "title": row.get("Title", "").strip(),
                    "amount_cop": _amount(row.get("Amount_COP")),
                    "owner": row.get("Owner", "").strip() or None,
                    "proposed_je_ref": je_ref,
                    "status": (row.get("Status") or "open").strip().lower(),
                    "disposition": row.get("Disposition", "").strip() or None,
                    "accepted_risk_tag": (row.get("Accepted_Risk") or "").strip() or None,
                    "period": row_period,
                    "gate_b": gate_b,
                }
            )
    return exceptions


def _amount(raw) -> float | None:
    if raw is None:
        return None
    cleaned = str(raw).replace(",", "").replace("$", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def summarize(exceptions: list[dict]) -> dict:
    """Counts for the summary endpoint, overall and per period bucket."""
    def _bucket(rows):
        out = {"total": len(rows), "open_high": 0, "open_medium": 0, "open_low": 0, "closed": 0}
        for e in rows:
            if e["status"] in ("closed", "approved", "rejected"):
                out["closed"] += 1
            else:
                out[f"open_{e['severity']}"] = out.get(f"open_{e['severity']}", 0) + 1
        return out

    baseline = [e for e in exceptions if e.get("period", "2026-01") < "2026-07"]
    live = [e for e in exceptions if e.get("period", "2026-01") >= "2026-07"]
    result = _bucket(exceptions)
    result["baseline"] = _bucket(baseline)
    result["live_period"] = _bucket(live)
    return result
