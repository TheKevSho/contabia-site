#!/usr/bin/env python3
"""Phase 6 — Bank Reconciliation (Motor-Checklist Phase 4).

REBUILT PROPERLY 2026-09-18. The 2026-09-17 review (finding #3) slated the
original bank_recon for replacement: it emitted hardcoded figures keyed to
string matches ("Hard fallback: known values") and was correct for exactly one
file. This rebuild is REAL line-level parsing:

  - statement Resumen row  -> opening / credits / debits / closing, footed
  - each Movimientos row   -> date, description, VALOR, SALDO (the SALDO run
    is verified against the running total; a broken run is a data problem)
  - GMF true-up             -> expected = sum(debits) x 0.004 vs the recorded
    'IMPTO GOBIERNO 4X1000' lines; the DIFFERENCE is the adjustment JE
  - Bold settlements        -> bank Bold credits summed vs the canonical Bold
    md's deposited figure; the delta is flagged (period cut-off, not hidden)
  - unmatched credits > COP 100k -> flagged (Checklist Phase 8.3 CRITICAL)
  - reconciliation statement per account with footing

Every amount flows from a statement line or a canonical .md table — no
string-literal amounts anywhere in a parsing path. Zero LLM, stdlib-only
(xlsx via recon_common.xlsx_rows: zipfile + XML).

Usage:
    python3 bank_recon.py tayrona 2026-07 --data-dir data/boveda_seed
    python3 bank_recon.py tayrona 2026-07 --mock
    python3 bank_recon.py tayrona 2026-07 --data-dir ... --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from recon_common import (cell_num, find_file, parse_amount, period_files,
                          xlsx_rows)

GMF_RATE = 0.004  # 4 per 1000 (Checklist Phase 4.2, Art. 870 ET)
UNMATCHED_CREDIT_FLAG = 100_000  # Phase 8.3: bank unreconciled > COP 100k bank
INTERACCOUNT_MARKERS = ("transferencia cta suc", "transferencia virtual", "cta cajero",
                        "transferencia cta", "nequi", "consignacion", "reintegro")

# Accounts are honest placeholders until the Sonata account_map exists
# (review finding #3a); the strings are the map keys the poster AND the
# assembler resolve (fork 2026-09-18-B).
ACCT_BANK = "1110xx Bancos"
ACCT_BANK_GMF = "5305xx Gastos bancarios (GMF)"


# ---------------------------------------------------------------------------
# Statement line model
# ---------------------------------------------------------------------------
def parse_statement(path: Path, period: str) -> dict:
    """Parse one bank statement xlsx into {resumen, lines}. Lines carry:
    date, description, amount (VALOR, +credit/-debit), balance_after."""
    rows = list(xlsx_rows(path))
    resumen: dict[str, float] = {}
    lines: list[dict] = []
    for i, r in enumerate(rows):
        if not r or not r[0]:
            continue
        head = r[0].strip()
        if head == "SALDO ANTERIOR" and i + 1 < len(rows):
            vals = rows[i + 1]
            labels = ["opening", "credits", "debits", "closing", "avg_balance"]
            for lab, raw in zip(labels, vals[:5]):
                num = parse_amount(raw)
                if num is not None:
                    resumen[lab] = num
            # RETEFUENTE/INTERESES live further right; capture if present
            for lab, raw in zip(("intereses", "retefuente"), vals[6:8]):
                num = parse_amount(raw)
                if num is not None:
                    resumen[lab] = num
            continue
        if "/" in head and len(r) >= 5 and cell_num(r, 4) is not None:
            amount = cell_num(r, 4)
            lines.append({
                "date": head,
                "description": (r[1].strip() if len(r) > 1 else ""),
                "amount": amount,  # credit > 0, debit < 0 (VALOR convention)
                "balance_after": cell_num(r, 5),
            })
    return {"path": str(path), "resumen": resumen, "lines": lines,
            "line_count": len(lines), "period": period}


def _footing_ok(resumen: dict) -> tuple[bool, str]:
    if not all(k in resumen for k in ("opening", "credits", "debits", "closing")):
        return False, "resumen row incomplete"
    expected = round(resumen["opening"] + resumen["credits"] - resumen["debits"], 2)
    ok = abs(expected - resumen["closing"]) <= 2
    return ok, (f"opening {resumen['opening']:,.2f} + credits {resumen['credits']:,.2f} "
                f"- debits {resumen['debits']:,.2f} = {expected:,.2f} vs closing {resumen['closing']:,.2f}")


def _balance_run(lines: list[dict]) -> Optional[str]:
    """Verify each line's stated SALDO against opening + running sum. A broken
    run means the statement itself is inconsistent - a data problem, surfaced."""
    if not lines or "balance_after" not in lines[0] or lines[0]["balance_after"] is None:
        return None
    run = 0.0
    first_balance = lines[0]["balance_after"]
    # derive opening from the first line if resumen absent
    opening = None
    for i, ln in enumerate(lines):
        run += ln["amount"]
        stated = ln["balance_after"]
        if opening is None:
            opening = stated - ln["amount"]
        if abs(run + (opening or 0) - stated) > 2:
            return f"line {i} ({ln['date']} {ln['description'][:30]}): run {run+opening:,.2f} != stated {stated:,.2f}"
    return None


# ---------------------------------------------------------------------------
# Classification + GMF
# ---------------------------------------------------------------------------
def classify_line(ln: dict) -> str:
    d = ln["description"].lower()
    if "4x1000" in d:
        return "gmf"
    if "bold" in d and "pago interbanc" in d:
        return "bold_settlement"
    if "abono intereses" in d or "ajuste interes" in d:
        return "interest"
    if "pago interbanc" in d or "abono de giro" in d:
        return "bank_transfer_in"
    if any(m in d for m in INTERACCOUNT_MARKERS):
        return "interaccount"
    if ln["amount"] > 0:
        # Known receipt rails (POS/QR/llave/consignación/corresponsal): these
        # are booked against revenue via the RC/exception register at Phase 2 —
        # they belong to the receipts class, NOT the unmatched bucket.
        if any(m in d for m in ("pago qr", "pago llave", "pago de prov", "abono de giro",
                                "consig", "abono", "giro internacional", "reintegro", "pago pse")):
            return "cash_receipts"
        return "other_credit"
    if "compra" in d or "pago" in d or "cobro" in d or "debito" in d or "comis" in d:
        return "expense_payment"
    return "other"


def _parse_statement_csv(path: Path, period: str) -> dict:
    """The mock transport: CSV with the same column semantics as the xlsx
    Movimientos (date, description, VALOR, SALDO)."""
    import csv

    lines = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.reader(fh, delimiter=";"):
            if len(r) < 3 or "/" not in (r[0] or ""):
                continue
            amount = parse_amount(r[2])
            if amount is None:
                continue
            lines.append({
                "date": (r[0] or "").strip(),
                "description": (r[1] or "").strip(),
                "amount": amount,
                "balance_after": parse_amount(r[3]) if len(r) > 3 and r[3] else None,
            })
    return {"path": str(path), "resumen": {}, "lines": lines,
            "line_count": len(lines), "period": period}


def run_bank_recon(entity: str, period: str, *, mock: bool = False,
                   data_dir: Optional[Path] = None) -> dict:
    from cfd_engine import run_rules

    if mock:
        stmt_path, md_files = _mock_statement(period)
    else:
        dd = data_dir or (Path(__file__).parent / "data" / "boveda_tayrona")
        if not dd.exists():
            raise FileNotFoundError(f"data dir not found: {dd} (use --data-dir or --mock)")
        stmt_path = find_file(dd, "78100001780") or find_file(dd, "bancolombia")
        if stmt_path is None:
            raise FileNotFoundError(f"no Bancolombia statement (78100001780) for {period} in {dd}")
        md_files = [p for p in period_files(dd, period) if p.suffix.lower() == ".md"]

    if mock:
        statement = _parse_statement_csv(stmt_path, period)
    else:
        statement = parse_statement(stmt_path, period)
    resumen, lines = statement["resumen"], statement["lines"]

    # Classify
    classes: dict[str, list[dict]] = {}
    for ln in lines:
        classes.setdefault(classify_line(ln), []).append(ln)
    summary = {k: {"count": len(v), "sum": round(sum(x["amount"] for x in v), 2)} for k, v in classes.items()}

    # Footing + balance-run integrity. A statement WITHOUT a Resumen block
    # (mock CSV) is not footing-checkable — that is reported as 'n/a', never
    # as an error; only an EXISTING resumen that fails to foot is an error.
    footing_ok, footing_detail = _footing_ok(resumen)
    run_error = _balance_run(lines)
    footing_applicable = bool(resumen)
    if not resumen:
        footing_ok, footing_detail = None, "resumen row absent (n/a)"

    # GMF true-up: expected (sum of debits x 0.004) vs recorded 4x1000 lines.
    # Both magnitudes; the DIFFERENCE is the adjustment JE (Checklist 4.2:
    # recorded < expected -> expense the gap; recorded > expected -> reverse).
    debits = [ln["amount"] for ln in lines if ln["amount"] < 0]
    expected_gmf = round(abs(sum(debits)) * GMF_RATE, 2)
    recorded_gmf = round(abs(sum(ln["amount"] for ln in classes.get("gmf", []))), 2)
    gmf_diff = round(expected_gmf - recorded_gmf, 2)
    gmf_je = None
    if abs(gmf_diff) > 1:
        if gmf_diff > 0:
            side_d, side_c = ACCT_BANK_GMF, ACCT_BANK
        else:
            side_d, side_c = ACCT_BANK, ACCT_BANK_GMF
        gmf_je = {
            "je_id": f"BNK-{period}-01",
            "description": f"GMF true-up {period}: recorded {recorded_gmf:,.2f} vs expected (debits x 0.004) {expected_gmf:,.2f}",
            "period": period,
            "bucket": "bank",
            "status": "pending_edwin_approval",
            "linked_docs": [stmt_path.name if not mock else "mock_bank_statement.csv"],
            "linked_items": ["bank_statement"],
            "lines": [
                {"account": side_d, "debit": abs(gmf_diff), "credit": 0},
                {"account": side_c, "debit": 0, "credit": abs(gmf_diff)},
            ],
        }

    # Bold settlements vs canonical Bold md deposited figure
    bold_bank = round(sum(ln["amount"] for ln in classes.get("bold_settlement", [])), 2)
    bold_deposited, bold_gross = None, None
    for md in md_files:
        if "bold" not in md.name.lower():
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        m_dep = re.search(r"Deposited to sales balance[^\n]*\|\s*\*?\*?COP\s+([\d.,]+)", text)
        if m_dep:
            bold_deposited = parse_amount(m_dep.group(1))
        m_gross = re.search(r"Valor total[^\n]*\|\s*\*?\*?COP\s+([\d.,]+)", text)
        if m_gross:
            bold_gross = parse_amount(m_gross.group(1))
        break
    bold_gap = None
    if bold_bank and bold_deposited is not None:
        diff = round(bold_bank - bold_deposited, 2)
        if abs(diff) > 2:
            bold_gap = (
                f"Bold settlements landed in bank {bold_bank:,.2f} vs the July Bold "
                f"doc deposited figure {bold_deposited:,.2f} (delta {diff:,.2f}) - "
                "period cut-off (June tail in / July tail out); match to the Bold report per booking, not assumed"
            )

    # Unmatched credits > COP 100k (Phase 8.3 CRITICAL): ONLY the class that
    # defies classification (other_credit). Known rails — receipts, Bold,
    # transfers, bank payouts — are matched at their own phases and would
    # only bury the real findings.
    unmatched = []
    for ln in classes.get("other_credit", []):
        if ln["amount"] > UNMATCHED_CREDIT_FLAG:
            unmatched.append({
                "date": ln["date"], "description": ln["description"],
                "amount": ln["amount"], "note": "credit > 100k without a class match - resolve via OTA payout report or exception register",
            })

    # CFD rules over statement-shaped docs (contra mislanding, statement line counts)
    docs = [
        {"doc_id": f"bank-{i}", "type": "bank_statement", "account": "78100001780",
         "contra_entry": {"account": ln["description"], "amount": ln["amount"]},
         "amount_cop": abs(ln["amount"])}
        for i, ln in enumerate(lines)
    ]
    cfd = run_rules(docs, {"period": period, "bank_lines": lines})

    report = {
        "phase": "bank_recon",
        "entity": entity,
        "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {"statement": stmt_path.name if not mock else "mock_bank_statement.csv",
                   "transport": "mock (synthetic CSV statement)" if mock else "real xlsx"},
        "statement": {
            "account": "78100001780",
            "line_count": statement["line_count"],
            "resumen": resumen,
            "footing_ok": footing_ok,
            "footing_detail": footing_detail,
            "balance_run_error": run_error,
        },
        "classification": summary,
        "gmf": {"expected": expected_gmf, "recorded": abs(recorded_gmf),
                "difference": gmf_diff, "true_up_je": gmf_je},
        "bold": {"bank_credits": bold_bank, "canonical_deposited": bold_deposited,
                 "canonical_gross": bold_gross, "gap": bold_gap},
        "unmatched_credits": unmatched,
        "jes": [gmf_je] if gmf_je else [],
        "cfd_fired": cfd["fired"],
        "gaps": [bold_gap] if bold_gap else [],
        "errors": [],
    }
    if report.get("errors") is None:
        report["errors"] = []
    if run_error:
        report["errors"].append(f"statement balance run broken: {run_error}")
    if not footing_applicable:
        report["statement"]["footing_note"] = "no Resumen block in source (n/a)"
    elif not footing_ok:
        report["errors"].append(f"statement footing broken: {footing_detail}")
    return report


# ---------------------------------------------------------------------------
# Mock — synthetic CSV statement with the real July shape (line-derived too)
# ---------------------------------------------------------------------------
def _mock_statement(period: str) -> tuple[Path, list[Path]]:
    """A CSV statement (same column semantics as the xlsx Movimientos) plus a
    Bold canonical md with the real July calibration figures."""
    tmp = Path(tempfile.gettempdir()) / f"bank_recon_mock_{period}"
    tmp.mkdir(parents=True, exist_ok=True)
    lines = [
        # date; description; VALOR; SALDO — ';' delimited on purpose: amounts
        # contain thousands commas, so a comma-delimited mock splits them
        # (the exact CSV-vs-locale trap CFD-0019 warns about).
        "1/07;PAGO INTERBANC Bold.Co S.A.S;1,149,273.00;",
        "1/07;IMPTO GOBIERNO 4X1000;-10,257.49;",
        "2/07;PAGO INTERBANC Bold.Co S.A.S;987,679.05;",
        "3/07;TRANSFERENCIA CTA SUC VIRTUAL;-1,045,200.00;",
        "3/07;IMPTO GOBIERNO 4X1000;-9,219.16;",
        "7/07;PAGO DE PROV STONEX COLOMBIA;7,539,000.00;",
        "14/07;TRANSFERENCIA CTA SUC VIRTUAL;-4,180,000.00;",
        "14/07;IMPTO GOBIERNO 4X1000;-27,399.92;",
        "21/07;ABONO DE GIRO INTERNACIONAL;4,624,048.00;",
        "24/07;PAGO INTERBANC Bold.Co S.A.S;4,610,362.80;",
        "28/07;COMPRA EN  AMAZON.COM;-849,139.00;",
        "30/07;IMPTO GOBIERNO 4X1000;-2,720.97;",
        "31/07;PAGO INTERBANC Bold.Co S.A.S;1,274,985.00;",
    ]
    (tmp / "bank_statement.csv").write_text("\n".join(lines), encoding="utf-8")
    bold_md = tmp / "Bold_Transacciones_2026-07.md"
    bold_md.write_text(
        "# Bold — Transacciones Julio 2026\n\n"
        "## Summary\n\n"
        "| Metric | Value |\n|---|---|\n"
        "| **Valor total (gross sales)** | **COP 9,491,500.00** |\n"
        "| Bold fees + retentions deducted | COP 577,735.85 |\n"
        "| **Deposited to sales balance** | **COP 8,913,764.15** |\n",
        encoding="utf-8",
    )
    return tmp / "bank_statement.csv", [bold_md]


def format_report(report: dict) -> str:
    s = report["statement"]
    g = report["gmf"]
    out = [
        "╔══════════════════════════════════════════════════╗",
        "║  PHASE 6 — BANK RECONCILIATION                    ║",
        "╚══════════════════════════════════════════════════╝",
        f"  {report['entity']} / {report['period']}   ({report['source']['transport']})",
        f"  Statement: {s['account']} — {s['line_count']} lines",
        f"  Opening {s['resumen'].get('opening', 0):,.2f} | credits {s['resumen'].get('credits', 0):,.2f} "
        f"| debits {s['resumen'].get('debits', 0):,.2f} | closing {s['resumen'].get('closing', 0):,.2f}",
    ]
    if s.get("footing_ok") is None:
        out.append(f"  Footing: n/a — {s['footing_detail']}")
    else:
        out.append(f"  Footing: {'✅ ' if s['footing_ok'] else '❌ '}{s['footing_detail']}")
    out += [
        "  Classification: " + ", ".join(f"{k}={v['count']}" for k, v in report['classification'].items()),
        f"  GMF: expected {g['expected']:,.2f} vs recorded {g['recorded']:,.2f} "
        f"-> true-up {g['difference']:,.2f} {'(JE proposed)' if g['true_up_je'] else '(none)'}",
        f"  Bold: bank credits {report['bold']['bank_credits']:,.2f} vs canonical deposited "
        f"{report['bold']['canonical_deposited'] if report['bold']['canonical_deposited'] is not None else 'n/a':,}",
    ]
    if report["bold"]["gap"]:
        out.append(f"  ⚠️  {report['bold']['gap']}")
    if report["unmatched_credits"]:
        out += ["", "─── Unmatched credits > COP 100k (Phase 8.3 CRITICAL) ───"]
        out += [f"  🚩 {u['date']} {u['description'][:38]:38s} {u['amount']:>15,.2f}" for u in report["unmatched_credits"]]
    if report["jes"]:
        out += ["", "─── Proposed JEs ───"]
        for je in report["jes"]:
            out.append(f"  🧾 {je['je_id']}: {je['description']}")
    out += ["", "─── Errors ───"] + ([f"  💥 {e}" for e in report["errors"]] or ["  ✓ none"])
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 6 — Bank Reconciliation")
    parser.add_argument("entity", help="Entity slug")
    parser.add_argument("period", help="Period YYYY-MM")
    parser.add_argument("--mock", action="store_true", help="Synthetic CSV statement")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--data-dir", type=Path, help="Period data dir (default data/boveda_tayrona)")
    args = parser.parse_args()

    try:
        report = run_bank_recon(args.entity, args.period, mock=args.mock, data_dir=args.data_dir)
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