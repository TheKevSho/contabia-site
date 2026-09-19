#!/usr/bin/env python3
"""Phase 5 — Expense Reconciliation (Motor-Checklist Phase 3).

REBUILT PROPERLY 2026-09-18. The 2026-09-17 review (finding #3) slated the
original expense_recon for replacement (hardcoded figures keyed to string
matches). This rebuild derives every amount from:

  - the canonical PILA .md (payroll JE: 'Valor total' row, line-level)
  - the exception register rows for the period (Amount_COP column), with the
    row's OWN disposition driving the outcome, not a hardcoded map:
        * open + amount > 0 + no contrary verdict  -> proposed expense JE
        * 'do not expense' / 'would double' / 'not Kevin' / 'park' -> gap
        * a Proposed_JE already exists (e.g. AJ-J07-05) -> gap (never re-propose)
  - foreign-vendor detection for the documento-soporte gap (CFD-0006 family)
  - the CFD rule set over every expense line (CFD-0015 10-UVT retefuente etc.)

JE ids: EXP-<period>-NN. Amounts are COP from the register/PILA — no
string-literal amounts anywhere in a parsing path. Zero LLM, stdlib-only.

Usage:
    python3 expense_recon.py tayrona 2026-07 --mock
    python3 expense_recon.py tayrona 2026-07 --data-dir data/boveda_seed
    python3 expense_recon.py tayrona 2026-07 --data-dir ... --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from recon_common import find_file, load_registers, parse_amount, period_files

ACCT_EXPENSE = "51xxxx Gastos por clasificar"
ACCT_AP = "2205xx Cuentas por pagar"
ACCT_PAYROLL_EXPENSE = "5105xx Sueldos y prestaciones sociales"
ACCT_PAYROLL_PAYABLE = "250505xx Salarios y prestaciones por pagar"

NO_BOOKING_VERDICTS = (
    "do not expense", "do not double", "would double", "not kevin", "park",
    "off queue", "superseded", "not this", "no pague", "no gastar", "no duplicar",
    "cerrada", "collapsed", "retired",
)
FOREIGN_MARKERS = (
    "amazon", "spotify", "netflix", "facebook", "google", "booking.com",
    "airbnb", "hostelworld", "getyourguide", "viator", "paypal", "aws ",
    "microsoft", "apple.com", "dropbox", "slack", "ads",
)
CONCEPT_KW = (
    ("honorarios", "honorarios"), ("comision", "honorarios"), ("comisión", "honorarios"),
    ("arriendo", "arrendamiento"), ("mercado", "bienes"), ("compra", "bienes"),
    ("fuel", "bienes"), ("combustible", "bienes"), ("gasolina", "bienes"),
)


def _concept_for(title: str) -> str:
    t = title.lower()
    for kw, concept in CONCEPT_KW:
        if kw in t:
            return concept
    return "servicios"


def _foreign(title: str, disposition: str) -> bool:
    hay = f"{title} {disposition}".lower()
    return any(m in hay for m in FOREIGN_MARKERS)


def _no_booking(row: dict) -> Optional[str]:
    disp = f"{row.get('Disposition') or ''} {row.get('Title') or ''}".lower()
    for v in NO_BOOKING_VERDICTS:
        if v in disp:
            return row.get("Disposition") or row.get("Title") or v
    return None


def parse_pila(dd: Path, period: str) -> Optional[dict]:
    """Canonical PILA md -> {path, total} (the 'Valor total' Summary row)."""
    md = find_file(dd, "pila") or find_file(dd, "planilla") or find_file(dd, "nomina")
    if md is None or md.suffix.lower() != ".md":
        return None
    text = md.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\|[^|]*Valor total[^|]*\|\s*\*?\*?COP\s+([\d.,]+)", text)
    total = parse_amount(m.group(1)) if m else None
    return {"path": str(md), "total": total}


# ---------------------------------------------------------------------------
def run_expense_recon(entity: str, period: str, *, mock: bool = False,
                      data_dir: Optional[Path] = None) -> dict:
    from cfd_engine import run_rules

    jes: list[dict] = []
    gaps: list[str] = []
    decisions: list[str] = []
    expenses: list[dict] = []  # register rows treated as expense docs

    if mock:
        dd, register, pila = _mock_inputs(period)
    else:
        dd = data_dir or (Path(__file__).parent / "data" / "boveda_tayrona")
        if not dd.exists():
            raise FileNotFoundError(f"data dir not found: {dd} (use --data-dir or --mock)")
        register = load_registers(dd, period)
        md_files = [p for p in period_files(dd, period) if p.suffix.lower() == ".md"]
        pila = parse_pila(dd, period)

    # --- Payroll JE from the canonical PILA doc ----------------------------
    if pila and pila["total"]:
        jes.append({
            "je_id": f"EXP-{period}-01",
            "description": f"Payroll (PILA) {period}: {pila['total']:,.2f} — employer contributions per DetallePlanilla",
            "period": period,
            "bucket": "expense",
            "status": "pending_edwin_approval",
            "linked_docs": [pila["path"]],
            "lines": [
                {"account": ACCT_PAYROLL_EXPENSE, "debit": pila["total"], "credit": 0},
                {"account": ACCT_PAYROLL_PAYABLE, "debit": 0, "credit": pila["total"]},
            ],
        })
    else:
        gaps.append("PILA canonical .md missing for the period — payroll JE cannot be derived (file lives in the corpus when ingested)")

    # --- Expense rows from the register, judged by their own disposition ----
    je_seq = [1]  # EXP-01 taken by payroll when present

    def next_seq() -> int:
        je_seq[0] += 1
        return je_seq[0]

    for row in register:
        phase = (row.get("Phase") or "").lower()
        if "expense" not in phase and "5 " not in phase and not phase.startswith("exp"):
            continue
        amount = parse_amount(row.get("Amount_COP"))
        if not amount or amount <= 0:
            continue
        title = row.get("Title") or row.get("Title_ES") or row["ID"]
        disposition = row.get("Disposition") or row.get("Disposition_ES") or ""

        expenses.append({
            "doc_id": row["ID"],
            "type": "invoice",
            "vendor": title.split(" ")[0],
            "title": title,
            "subTotal": amount, "totalTaxes": 0, "total": amount,
            "concept": _concept_for(title),
            "status": (row.get("Status") or "").lower(),
        })

        if (row.get("Status") or "").lower() != "open":
            continue  # closed rows carry their endings; nothing to propose

        no_book = _no_booking(row)
        if no_book:
            gaps.append(f"{row['ID']} ({title[:50]}): NOT booked — {no_book[:110]}")
            continue
        if row.get("Proposed_JE"):
            gaps.append(
                f"{row['ID']}: proposed JE {row['Proposed_JE']} already exists in the "
                "postable register — never re-propose"
            )
            continue

        je = {
            "je_id": f"EXP-{period}-{next_seq():02d}",
            "description": f"Expense {period}: {title[:70]} — {amount:,.2f} (from exception register {row['ID']})",
            "period": period,
            "bucket": "expense",
            "status": "pending_edwin_approval",
            "linked_exceptions": [row["ID"]],
            "lines": [
                {"account": ACCT_EXPENSE, "debit": amount, "credit": 0},
                {"account": ACCT_AP, "debit": 0, "credit": amount},
            ],
        }
        if _foreign(title, disposition):
            je["description"] = je["description"].replace("— ",
                "— FOREIGN VENDOR (documento soporte path) — ")
            gaps.append(
                f"{row['ID']}: foreign vendor purchase requires documento soporte "
                f"(Res. 000167/2021) for IVA recovery — flag to Edwin"
            )
        jes.append(je)

    # --- CFD rules over the expense lines ----------------------------------
    cfd = run_rules(expenses, {"period": period})

    return {
        "phase": "expense_recon",
        "entity": entity,
        "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {"transport": "mock (synthetic PILA + register)" if mock else "register + corpus"},
        "expense_lines": expenses,
        "pila": pila,
        "decisions": decisions,
        "jes": jes,
        "cfd_fired": cfd["fired"],
        "gaps": gaps,
        "errors": [],
    }


# ---------------------------------------------------------------------------
def _mock_inputs(period: str) -> tuple[Path, list[dict], Optional[dict]]:
    from recon_common import load_exception_register

    tmp = Path(tempfile.gettempdir()) / f"expense_recon_mock_{period}"
    tmp.mkdir(parents=True, exist_ok=True)
    pila_md = tmp / "DetallePlanilla_38244858_2026_07_E.md"
    pila_md.write_text(
        "# PILA — Detalle Planilla Julio 2026\n\n"
        "**Source:** `DetallePlanilla_38244858_2026_07_E.pdf`\n\n"
        "## Summary\n\n"
        "| Metric | Value |\n|---|---|\n"
        "| Period | 2026-07 |\n"
        "| **Valor total** | **COP 2,164,950** |\n",
        encoding="utf-8",
    )
    reg = tmp / "exception_register_2026-07.csv"
    reg.write_text(
        "ID,Phase,Severity,Amount_COP,Proposed_JE,Status,Title,Disposition,Period\n"
        "EX-J07-07,5 Expenses,LOW,449901,,Open,Olímpica COMK5038,\"Not Kevin. Zero on Jul Bancolombia. Do not expense again.\",2026-07\n"
        "EX-HIP-99,5 Expenses,MED,1245300,,Open,Marina fuel July,,2026-07\n"
        "EX-HIP-01,5 Expenses,HIGH,315480,,Open,AWS hosting,\"Foreign vendor; documento soporte required for IVA recovery.\",2026-07\n",
        encoding="utf-8",
    )
    # PILA "md" also lands in period_files() for the gate; the total is
    # parsed back from the file we just wrote (line-level, not a literal)
    return tmp, load_exception_register(reg), parse_pila(tmp, period)


def format_report(report: dict) -> str:
    pila = report["pila"]
    if pila and pila.get("total"):
        pila_line = f"✅ {pila['path']} ({pila['total']:,.2f})"
    else:
        pila_line = "❌ PILA canonical .md missing"
    out = [
        "╔══════════════════════════════════════════════════╗",
        "║  PHASE 5 — EXPENSE RECONCILIATION                 ║",
        "╚══════════════════════════════════════════════════╝",
        f"  {report['entity']} / {report['period']}   ({report['source']['transport']})",
        f"  PILA: {pila_line}",
        f"  Expense lines from register: {len(report['expense_lines'])}",
    ]
    if report["jes"]:
        out += ["", "─── Proposed JEs ───"]
        for je in report["jes"]:
            out.append(f"  🧾 {je['je_id']}: {je['description']}")
    if report["cfd_fired"]:
        out += ["", "─── CFD rules fired ───"]
        for f in report["cfd_fired"]:
            out.append(f"  ⚠️ [{f['rule_id']}] {f['doc_id']}: {f['message']}")
    if report["gaps"]:
        out += ["", "─── Gaps / findings ───"] + [f"  ⚠️  {g}" for g in report["gaps"]]
    out += ["", "─── Errors ───"] + ([f"  💥 {x}" for x in report["errors"]] or ["  ✓ none"])
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 5 — Expense Reconciliation")
    parser.add_argument("entity", help="Entity slug")
    parser.add_argument("period", help="Period YYYY-MM")
    parser.add_argument("--mock", action="store_true", help="Synthetic PILA md + register")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--data-dir", type=Path, help="Period data dir (default data/boveda_tayrona)")
    args = parser.parse_args()

    try:
        report = run_expense_recon(args.entity, args.period, mock=args.mock, data_dir=args.data_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())