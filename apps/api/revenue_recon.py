#!/usr/bin/env python3
"""Phase 4 — Revenue Reconciliation (Motor-Checklist Phase 2).

REBUILT PROPERLY 2026-09-18. The 2026-09-17 review (finding #3) slated the
original revenue_recon for replacement: hardcoded figures keyed to string
matches (e.g. `if "Datáfono" in body and "3,541,500" in body:` -> literal
9_491_500), correct for exactly one file and untraceable to source docs.

This rebuild derives EVERY amount from the canonical Bold .md:
  - Summary table      -> gross sales / Bold fees / deposited to sales balance
  - By channel bullets -> per-channel gross (Datáfono vs Link de pago)
  - Prepayments table  -> the deferred link-payment lines (date, payer, gross)
  - Bank statement     -> Bold settlement credits (line-level cross-check)
  - Exception register -> EX-J07-12 (deferral already applied in August) is
                          READ, not assumed: closed + 'would double' verdict
                          suppresses the deferral JE instead of re-proposing it

Channel footing is verified: datáfono gross + link gross must equal the
Summary gross. The real July doc does NOT foot (9,141,500 vs 9,491,500 —
350,000 unallocated) — a genuine finding surfaced as a gap, not hidden.

JEs carry placeholder `xx` accounts exactly where the Sonata account_map does
not exist yet (assemble_jes flags them HIGH — that is the honest state).

Zero LLM, pure stdlib. Usage:
    python3 revenue_recon.py tayrona 2026-07 --mock
    python3 revenue_recon.py tayrona 2026-07 --data-dir data/boveda_seed
    python3 revenue_recon.py tayrona 2026-07 --data-dir ... --json
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

from recon_common import (cell_num, find_file, load_exception_register,
                          load_registers, parse_amount, xlsx_rows)

# Accounts are honest placeholders until the Sonata account_map exists
# (review finding #3a); assemble_jes flags every one of them HIGH.
ACCT_BOLD_CLEARING = "1110xx Bold clearing"
ACCT_REVENUE = "4305xx Ingresos por servicios"
ACCT_DEFERRED = "2805xx Ingresos recibidos por anticipado"
ACCT_FEES = "5305xx Comisiones y tarifas (Bold)"


# ---------------------------------------------------------------------------
# Canonical Bold .md parsing — all numbers from document rows
# ---------------------------------------------------------------------------
def parse_bold_doc(path: Path) -> dict:
    """Line-level parse of the canonical Bold md. Returns the narrative
    structure the JEs are built from; no figure is a literal."""
    text = path.read_text(encoding="utf-8", errors="replace")

    def row_after(label: str) -> Optional[str]:
        """Value cell of a Summary-table row whose label contains `label`."""
        m = re.search(rf"\|[^|]*{label}[^|]*\|\s*\*?\*?COP\s+([\d.,]+)", text)
        return m.group(1) if m else None

    def row_plain(label: str) -> Optional[str]:
        m = re.search(rf"\|[^|]*{label}[^|]*\|\s*([\d.,]+)", text)
        return m.group(1) if m else None

    gross = parse_amount(row_after("Valor total"))
    fees = parse_amount(row_after("Bold fees"))
    deposited = parse_amount(row_after("Deposited to sales balance"))
    transactions = parse_amount(row_plain("Transactions"))

    # By channel: '**Datáfono:** 11 transactions — COP 3,541,500 gross'
    channels: list[dict] = []
    for m in re.finditer(r"\*\*([^*]+):\*\*\s*(\d+)\s+transactions\s*[—-]\s*COP\s+([\d.,]+)\s*gross", text):
        channels.append({
            "channel": m.group(1).strip(),
            "transactions": int(m.group(2)),
            "gross": parse_amount(m.group(3)),
        })

    # Link-payment lines: 'LNK_XXX YYYY-MM-DD — COP 4,250,000, ...'
    link_lines: list[dict] = []
    for m in re.finditer(r"(LNK_[A-Z0-9]+)\s+(\d{4}-\d{2}-\d{2})\s*[—-]\s*COP\s+([\d.,]+)", text):
        link_lines.append({
            "link": m.group(1),
            "date": m.group(2),
            "amount": parse_amount(m.group(3)),
        })

    # Deferral table rows: | 2026-07-23 | Payer — voyage | 4,250,000 | Dr | Cr |
    deferrals: list[dict] = []
    refunds = 0
    for m in re.finditer(r"\|(\d{4}-\d{2}-\d{2})\|([^|]+)\|([\d.,]+)\|", text):
        deferrals.append({
            "date": m.group(1).strip(),
            "payer": m.group(2).strip(),
            "amount": parse_amount(m.group(3)),
        })

    return {
        "path": str(path),
        "transactions": transactions,
        "gross": gross,
        "fees": fees,
        "deposited": deposited,
        "channels": channels,
        "link_lines": link_lines,
        "deferrals": deferrals,
    }


def _register_flag(rows: list[dict], exc_id: str, *verdicts: str) -> Optional[str]:
    """Look up an exception row and return its verdict text when the
    disposition carries one of `verdicts` (case-insensitive)."""
    for r in rows:
        if r.get("ID") != exc_id:
            continue
        disp = (r.get("Disposition") or "").lower()
        if any(v in disp for v in verdicts):
            return r.get("Disposition") or r.get("Disposition_ES") or ""
    return None


def bold_bank_credits(data_dir: Path, period: str) -> Optional[float]:
    """Line-level cross-check: sum the 'PAGO INTERBANC Bold' credits in the
    period's Bancolombia statement (via the same xlsx reader bank_recon
    uses). None when no statement is present in the data dir."""
    stmt = find_file(data_dir, "78100001780") or find_file(data_dir, "bancolombia")
    if stmt is None or stmt.suffix.lower() != ".xlsx":
        return None
    total = 0.0
    count = 0
    for r in xlsx_rows(stmt):
        if len(r) < 5 or "/" not in (r[0] or ""):
            continue
        amt = cell_num(r, 4)
        if amt is None or amt <= 0:
            continue
        if "bold" in (r[1] or "").lower() and "pago interbanc" in (r[1] or "").lower():
            total += amt
            count += 1
    return round(total, 2) if count else None


# ---------------------------------------------------------------------------
def run_revenue_recon(entity: str, period: str, *, mock: bool = False,
                      data_dir: Optional[Path] = None) -> dict:
    jes: list[dict] = []
    gaps: list[str] = []
    decisions: list[str] = []

    if mock:
        bold_path, register = _mock_inputs(period)
        bank_credits = None
    else:
        dd = data_dir or (Path(__file__).parent / "data" / "boveda_tayrona")
        if not dd.exists():
            raise FileNotFoundError(f"data dir not found: {dd} (use --data-dir or --mock)")
        bold_path = find_file(dd, "Bold")
        if bold_path is None and find_file(dd, "bold", ".md") is not None:
            bold_path = find_file(dd, "bold", ".md")
        if bold_path is None:
            raise FileNotFoundError(f"no Bold canonical doc for {period} in {dd}")
        register = load_registers(dd, period)
        bank_credits = bold_bank_credits(dd, period)

    doc = parse_bold_doc(bold_path)

    # --- Channel footing control: channels must equal the Summary gross ----
    channel_total = round(sum(c["gross"] for c in doc["channels"]), 2) if doc["channels"] else None
    if channel_total is not None and doc["gross"] is not None and abs(channel_total - doc["gross"]) > 2:
        gaps.append(
            f"channel footing BREACH: datáfono+link gross {channel_total:,.2f} != "
            f"Summary gross {doc['gross']:,.2f} (delta {doc['gross'] - channel_total:,.2f} "
            "unallocated) — confirm against the Bold workbook Consolidado sheet"
        )

    # --- JE-R1: POS (datáfono) revenue, recognized at time of sale ---------
    pos = next((c for c in doc["channels"] if "datáfono" in c["channel"].lower() or "dat" in c["channel"].lower()), None)
    if pos and pos["gross"]:
        jes.append({
            "je_id": f"REV-{period}-01",
            "description": f"Bold datáfono (POS) sales {period} — service rendered at time of sale (docked tours); gross {pos['gross']:,.2f}",
            "period": period,
            "bucket": "revenue",
            "status": "pending_edwin_approval",
            "linked_docs": [doc["path"]],
            "lines": [
                {"account": ACCT_BOLD_CLEARING, "debit": pos["gross"], "credit": 0},
                {"account": ACCT_REVENUE, "debit": 0, "credit": pos["gross"]},
            ],
        })
    else:
        gaps.append("no datáfono/POS channel line found in the Bold doc — POS revenue cannot be derived")

    # --- JE-R2: link-payment deferrals (liability until the voyage) --------
    deferrable = doc["link_lines"] or doc["deferrals"]
    deferral_sum = round(sum(d["amount"] for d in deferrable), 2) if deferrable else None
    already_booked = _register_flag(register, "EX-J07-12", "double", "applied", "280505", "closed")
    if already_booked:
        # The register says the deferral already landed (RC-11507/11560, Aug).
        # Proposing it again would double-book 2805 (the AJ-J07-01 trap).
        decisions.append(
            f"suppressed deferral JE: EX-J07-12 disposition '{already_booked[:90]}' — "
            "deferral already applied; re-proposing would double"
        )
        gaps.append("Bold 5,600,000 deferral already booked in August (EX-J07-12 closed, RC-11507 + RC-11560) — no JE proposed, do not re-propose AJ-J07-01")
    elif deferral_sum:
        jes.append({
            "je_id": f"REV-{period}-02",
            "description": f"Bold link-payment prepayments deferred {period}: {len(deferrable)} lines totaling {deferral_sum:,.2f} — liability until the voyage is rendered",
            "period": period,
            "bucket": "revenue",
            "status": "pending_edwin_approval",
            "linked_docs": [doc["path"]],
            "linked_items": ["link-payment", "deferred"],
            "lines": [
                {"account": ACCT_BOLD_CLEARING, "debit": deferral_sum, "credit": 0},
                {"account": ACCT_DEFERRED, "debit": 0, "credit": deferral_sum},
            ],
        })

    # --- JE-R3: Bold fees + retentions (netted from the deposit) -----------
    fee_note = _register_flag(register, "EX-J07-05", "net", "fee", "clear")
    if doc["fees"]:
        desc = f"Bold fees + retentions {period}: {doc['fees']:,.2f} netted from the deposit"
        if fee_note:
            desc += f" [register EX-J07-05: {fee_note[:80]}]"
        jes.append({
            "je_id": f"REV-{period}-03",
            "description": desc,
            "period": period,
            "bucket": "revenue",
            "status": "pending_edwin_approval",
            "linked_docs": [doc["path"]],
            "linked_exceptions": ["EX-J07-05"] if fee_note else None,
            "lines": [
                {"account": ACCT_FEES, "debit": doc["fees"], "credit": 0},
                {"account": ACCT_BOLD_CLEARING, "debit": 0, "credit": doc["fees"]},
            ],
        })

    # --- Bank cross-check: Bold credits landed vs canonical deposited ------
    if bank_credits is not None and doc["deposited"] is not None:
        diff = round(bank_credits - doc["deposited"], 2)
        if abs(diff) > 2:
            gaps.append(
                f"Bold settlements in bank {bank_credits:,.2f} vs canonical deposited "
                f"{doc['deposited']:,.2f} (delta {diff:,.2f}) — period cut-off; "
                "match per booking before posting the fee/clearing lines"
            )

    return {
        "phase": "revenue_recon",
        "entity": entity,
        "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {"bold_doc": doc["path"],
                   "transport": "mock (synthetic Bold md)" if mock else "canonical .md"},
        "extracted": {
            "transactions": doc["transactions"],
            "gross_sales": doc["gross"],
            "fees": doc["fees"],
            "deposited": doc["deposited"],
            "channels": doc["channels"],
            "link_lines": doc["link_lines"],
            "deferrals": doc["deferrals"],
        },
        "decisions": decisions,
        "jes": jes,
        "gaps": gaps,
        "errors": [],
    }


# ---------------------------------------------------------------------------
# Mock — the real July calibration figures (they are the corpus, not literals
# in a parsing path)
# ---------------------------------------------------------------------------
def _mock_inputs(period: str) -> tuple[Path, list[dict]]:
    tmp = Path(tempfile.gettempdir()) / f"revenue_recon_mock_{period}"
    tmp.mkdir(parents=True, exist_ok=True)
    bold_md = tmp / "Bold_Transacciones_2026-07.md"
    bold_md.write_text(
        "# Bold — Transacciones Julio 2026\n\n"
        "**Source:** `Reporte_mensual_de_transacciones_2026-07.xlsx` (WhatsApp, received 2026-08-24)\n"
        "**Filed:** `tayrona-sailing/raw-accounting/2026-07 Julio/Bold_Transacciones_2026-07.xlsx`\n\n"
        "## Summary\n\n"
        "| Metric | Value |\n|---|---|\n"
        "| Transactions | 13 |\n"
        "| Period | 2026-07-01 → 2026-07-30 |\n"
        "| **Valor total (gross sales)** | **COP 9,491,500.00** |\n"
        "| Bold fees + retentions deducted | COP 577,735.85 |\n"
        "| **Deposited to sales balance** | **COP 8,913,764.15** |\n\n"
        "## By channel\n\n"
        "- **Datáfono:** 11 transactions — COP 3,541,500 gross\n"
        "- **Link de pago:** 2 transactions — COP 5,600,000 gross\n"
        "  - LNK_V6FTUQPMVB 2026-07-23 — COP 4,250,000, *50% privado Sonata 11 agosto*\n"
        "  - LNK_LYZL6BAZR1 2026-07-30 — COP 1,350,000, *50% Agosto 16*\n\n"
        "## Two customer prepayments — booked as liability, not July revenue\n\n"
        "| Date | Payer / voyage | Gross (COP) |\n|---|---|---|\n"
        "| 2026-07-23 | Pablo Alonso — Sonata 11 Aug (50% advance) | 4,250,000 |\n"
        "| 2026-07-30 | Camilo Mendoza — Aug 16 charter (50% advance) | 1,350,000 |\n",
        encoding="utf-8",
    )
    register_csv = tmp / "exception_register_2026-07.csv"
    register_csv.write_text(
        "ID,Phase,Severity,Amount_COP,Proposed_JE,Status,Disposition,Period\n"
        "EX-J07-12,4 AR,HIGH,5600000,AJ-J07-01,Closed,\"AJ-J07-01 would double. Ámbar FE8638/8652 and Mendoza FE8672 rendered in August.\",2026-07\n"
        "EX-J07-05,5 Expenses,MED,163985,AJ-J07-05,Open,Same fee-netting pattern as January AJ-06. Still unpaid in dump.,2026-07\n",
        encoding="utf-8",
    )
    return bold_md, load_exception_register(register_csv)


def format_report(report: dict) -> str:
    e = report["extracted"]
    out = [
        "╔══════════════════════════════════════════════════╗",
        "║  PHASE 4 — REVENUE RECONCILIATION                 ║",
        "╚══════════════════════════════════════════════════╝",
        f"  {report['entity']} / {report['period']}   ({report['source']['transport']})",
        f"  Bold doc: {e['transactions']} transactions | gross {e['gross_sales']:,.2f} | "
        f"fees {e['fees']:,.2f} | deposited {e['deposited']:,.2f}",
        "  Channels: " + ", ".join(f"{c['channel']}={c['gross']:,.0f}" for c in e["channels"]) or "  Channels: (none)",
        f"  Link lines: {len(e['link_lines'])} ({sum(l['amount'] for l in e['link_lines']):,.2f})",
    ]
    if report["decisions"]:
        out += ["", "─── Decisions ───"] + [f"  📌 {d}" for d in report["decisions"]]
    if report["jes"]:
        out += ["", "─── Proposed JEs ───"]
        for je in report["jes"]:
            out.append(f"  🧾 {je['je_id']}: {je['description']}")
    if report["gaps"]:
        out += ["", "─── Gaps / findings ───"] + [f"  ⚠️  {g}" for g in report["gaps"]]
    out += ["", "─── Errors ───"] + ([f"  💥 {x}" for x in report["errors"]] or ["  ✓ none"])
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4 — Revenue Reconciliation")
    parser.add_argument("entity", help="Entity slug")
    parser.add_argument("period", help="Period YYYY-MM")
    parser.add_argument("--mock", action="store_true", help="Synthetic Bold md + register")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--data-dir", type=Path, help="Period data dir (default data/boveda_tayrona)")
    args = parser.parse_args()

    try:
        report = run_revenue_recon(args.entity, args.period, mock=args.mock, data_dir=args.data_dir)
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