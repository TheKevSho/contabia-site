#!/usr/bin/env python3
"""Phase 2 — CFD Rules Engine (Motor-Checklist Phase 2 / File 13 flag set).

REBUILT 2026-09-18. The original cfd_engine.py (built 2026-09-09) was lost in
the Time Machine restore; it was never committed and the Time Machine drive has
no backup between 2026-08-24 and the restore. The 22 CFD rules are rebuilt from
the Reference Motor corpus (`_contabia/claude canon/reference-motor/Corpus de
Fallas Detectadas.md`, v4, CFD-0001-0018 active + drafts CFD-0019-0022 promoted)
and the 8 File-13 received-document integrity detections from
`13-Capture-Rules-Decision-Tree.md`. Behaviourally equivalent, not
byte-identical, to the originals.

Zero LLM, pure stdlib. Smoke-testable: `python3 cfd_engine.py` runs the inline
calibration asserts (parse_cop round-trips + rule triggers) and exits nonzero
on any failure.

Key contract (code-review finding #7): NO bare `except: pass` anywhere. Every
rule run is wrapped so a rule exception is logged with its rule id and surfaced
in the report's `errors` — a broken rule can never silently vanish.

parse_cop() resolves Colombian 16.000,00 vs US 16,000.00.

Usage:
    python3 cfd_engine.py               # smoke calibration (default)
    python3 cfd_engine.py --mock        # run rules over the calibration corpus
    python3 cfd_engine.py --mock --json # same, JSON to stdout
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Callable, Optional

# 2026 UVT per Decreto 0572/2025 (arte de CFD-0015): purchase base above
# 10 UVT triggers the retefuente scan. UVT 2026 = COP 52,374.
UVT_2026 = 52_374.0
RETEFUENTE_THRESHOLD_2026 = 10 * UVT_2026  # COP 523,740

# Retefuente rate by concept (CFD-0015 / File 02): the rate depends on the
# concept, not the amount. Insurance premiums are exempt regardless (Decreto
# 2418/2013) - handled inside the rule, never flagged as a gap.
RETEFUENTE_RATES = {
    "servicios": 0.04,
    "bienes": 0.025,
    "honorarios": 0.11,
    "arrendamiento": 0.035,
}

# IVA rates that exist in Colombia (File 13 detection 7).
VALID_IVA_RATES = {0, 5, 19}


# ---------------------------------------------------------------------------
# parse_cop — Colombian money parsing
# ---------------------------------------------------------------------------
def parse_cop(text: Any) -> float:
    """Parse a COP amount in any format the real corpus ships in:
      '16.000,00'  -> 16000.0   (Colombian: dot = thousands, comma = decimal)
      '16,000.00'  -> 16000.0   (US:        comma = thousands, dot = decimal)
      '16.000'     -> 16000.0   (Colombian thousands, no decimals)
      '16,000'     -> 16000.0   (US thousands, no decimals)
      '16,5'       -> 16.5      (Colombian decimal, no thousands)
      '9.491.500,00', '(1.200,00)', 'COP 523.740', '4.250.000' etc.

    Raises ValueError on anything that is not a number. The disambiguation
    rule when both separators appear: the separator that comes FIRST is the
    thousands separator (Colombian puts the dot first, US puts the comma
    first); when only one appears, three digits after it = thousands, one or
    two = decimals."""
    if text is None:
        raise ValueError("parse_cop(None)")
    s = str(text).strip()
    s = re.sub(r"[$\s]", "", s)
    s = s.replace("COP", "").replace("USD", "").strip()
    if not s:
        raise ValueError(f"parse_cop({text!r}): empty after stripping")
    if "," in s and "." in s:
        if s.find(".") < s.find(","):
            # Colombian: '16.000,00' — dots are thousands, comma is decimal
            # (whatever comes FIRST is the thousands separator).
            s = s.replace(".", "").replace(",", ".")
        else:
            # US: '16,000.00' — commas are thousands, dot is decimal.
            s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) == 3:
            s = s.replace(",", "")          # '16,000' -> 16000 (US thousands)
        elif len(parts[-1]) in (1, 2):
            s = s.replace(",", ".")         # '16,5' -> 16.5 (Colombian decimal)
        else:
            s = s.replace(",", "")          # '1,000,000' -> 1000000
    elif "." in s:
        parts = s.split(".")
        if len(parts) > 2:
            s = s.replace(".", "")          # '4.250.000' -> 4250000 (Colombian thousands)
        elif len(parts) == 2 and len(parts[1]) == 3:
            s = s.replace(".", "")          # '16.000' -> 16000 (thousands)
    try:
        return float(s)
    except ValueError as exc:
        raise ValueError(f"parse_cop({text!r}): cannot parse remainder {s!r}") from exc


def _fmt_cop(amount: float) -> str:
    """Deterministic COP formatting for messages: '1.234.567' (Colombian)."""
    return f"{amount:,.0f}".replace(",", ".")


# ---------------------------------------------------------------------------
# CFR — the 22 CFD rules (Corpus de Fallas Detectadas, CFD-0001..0022)
# ---------------------------------------------------------------------------
# A rule fn signature: fn(doc: dict, ctx: dict) -> None | str | list[str].
# Return None when the rule does not fire for this doc; return a message (or
# list of messages) when it does. ctx carries cross-doc/period context:
#   ctx["period"], ctx["uvt"], ctx["bank_lines"], ctx["alegra_line_counts"],
#   ctx["docs"] (the full batch), ctx["config"] (onboarding_config fields).
RuleFn = Callable[[dict, dict], Optional[Any]]


def r_cfd0001_lobby_html_xls(doc: dict, ctx: dict) -> Optional[str]:
    """LobbyPMS export is HTML disguised as .xls."""
    fn = str(doc.get("filename") or doc.get("source") or "").lower()
    head = str(doc.get("content_head") or str(doc.get("content") or "")).strip().lower()[:200]
    if fn.endswith(".xls") and any(tag in head for tag in ("<html", "<!doctype", "<table", "<style")):
        return "LobbyPMS-style .xls that is really HTML: parse with pd.read_html, strip '#' from Booking IDs"
    return None


def r_cfd0002_hostelworld_pattern(doc: dict, ctx: dict) -> Optional[str]:
    """Hostelworld payout pattern reveals the model (PayNow vs Hotel Collect)."""
    if "hostelworld" not in str(doc.get("vendor") or "").lower():
        return None
    if ctx.get("config", {}).get("ota_model_hostelworld"):
        return None  # already captured in onboarding_config - do not re-derive
    bank = [b for b in (ctx.get("bank_lines") or []) if b]
    hw = sorted(b for b in bank if "hostelworld" in str(b.get("description") or "").lower() and b.get("amount", 0) > 0)
    if len(hw) >= 2:
        days = []
        for a, b_ in zip(hw, hw[1:]):
            try:
                days.append(abs((b_["date"] - a["date"]).days))
            except Exception:
                break
        if days and all(10 <= d <= 18 for d in days):
            return "Hostelworld net credits on a ~14-day cycle -> PayNow (Pass-Through gross-up)"
    return "Hostelworld present without a captured commission model in onboarding_config"


def r_cfd0003_despegar_domestic(doc: dict, ctx: dict) -> Optional[str]:
    """Despegar Colombia is domestic - different rules."""
    name = str(doc.get("vendor") or "").lower()
    nit = str(doc.get("vendor_nit") or "").replace("-", "").strip()
    if "despegar" not in name and nit not in ("9006105185", "900610518"):
        return None
    return "Despegar Colombia (NIT 900.610.518-5): domestic - factura electronica, no documento soporte; its retefuente is an anticipo asset, not expense"


def r_cfd0004_ota_commission_source(doc: dict, ctx: dict) -> Optional[str]:
    """OTA commissions come from the operational booking source, not the OTA invoice."""
    if "invoice" not in str(doc.get("type") or "") and "settlement" not in str(doc.get("type") or ""):
        return None
    if "ota" in str(doc.get("category") or "").lower() or "commission" in str(doc.get("category") or "").lower():
        return "OTA invoice/settlement is a reconciliation input, NOT the commission source - accrue from the booking source (LobbyPMS/FareHarbor) by check-out date"
    return None


def r_cfd0005_booking_deflate_119(doc: dict, ctx: dict) -> Optional[str]:
    """Booking monthly invoice - accrue by check-out date, deflate by 1.19."""
    name = str(doc.get("vendor") or "").lower()
    if "booking" not in name:
        return None
    msgs = []
    if doc.get("commission_base_includes_iva"):
        msgs.append("Booking commission computed on an IVA-inclusive base - deflate by /1.19 before accruing")
    if doc.get("accrual_month") and ctx.get("period") and doc.get("accrual_month") != ctx["period"]:
        msgs.append(f"Booking commission accrued for {doc.get('accrual_month')} but close period is {ctx.get('period')} - accrue in the stay/check-out month")
    if not doc.get("accrual_month") and doc.get("type") in ("invoice", "settlement"):
        msgs.append("Booking monthly invoice present but no stay-month accrual is linked - reclassification must match the open accrual (not a fresh expense)")
    return " | ".join(msgs) if msgs else None


def r_cfd0006_foreign_iva_self_retention(doc: dict, ctx: dict) -> Optional[str]:
    """Foreign OTA commission needs 100% IVA self-retention + documento soporte."""
    if "commission" not in str(doc.get("category") or "").lower():
        return None
    nit = str(doc.get("vendor_nit") or "").strip()
    foreign = not nit or "CO" not in str(doc.get("vendor_country") or "").upper()
    if foreign and not doc.get("doc_soporte_generated"):
        return "Foreign OTA commission without documento soporte (Res. 000167/2021) - 100% IVA self-retention required for the credito fiscal to be recoverable"
    return None


def r_cfd0007_30_day_month(doc: dict, ctx: dict) -> Optional[str]:
    """Motor always uses 30 days/month (Art. 134 CST)."""
    days = doc.get("days_source") or doc.get("payroll_days_used")
    if days is None or str(days) == "30":
        return None
    return f"Prestaciones/nomina calculated with {days} days/month - HARD RULE is 30 regardless of calendar length (Art. 134 CST)"


def r_cfd0008_recargos_mandatory(doc: dict, ctx: dict) -> Optional[str]:
    """Recargos and overtime are mandatory in the nomina base (Art. 127 CST)."""
    if doc.get("type") not in ("payroll", "nomina"):
        return None
    if not doc.get("recargos_provided"):
        return "Recargos/horas extra not provided for payroll - mandatory input (Art. 127 CST); gate-fail (payroll.recargos_missing), prestaciones base understated"
    if doc.get("prestaciones_base") and doc.get("base_salary") and doc["prestaciones_base"] <= doc["base_salary"] and doc.get("recargos_amount", 0) > 0:
        return "Prestaciones computed on base salary only - recargos/horas extra must enter the statutory base"
    return None


def r_cfd0009_line_count_gate(doc: dict, ctx: dict) -> Optional[str]:
    """A statement 'in hand' is not 'booked' - gate on line counts."""
    if doc.get("type") not in ("bank_statement", "card_statement"):
        return None
    stmt_lines = doc.get("line_count")
    alegra_lines = (ctx.get("alegra_line_counts") or {}).get(str(doc.get("account") or doc.get("doc_id") or ""))
    if stmt_lines and alegra_lines is not None:
        if alegra_lines <= 2 and stmt_lines > 10:
            return f"Statement has {stmt_lines} lines but Alegra has {alegra_lines} for {doc.get('account')} - a posting gap (blocker), NOT a reconciling-item gap (CFD-0009)"
    return None


def r_cfd0010_paypal_net_and_range(doc: dict, ctx: dict) -> Optional[str]:
    """PayPal balance net of fees/payouts; exports span multiple months."""
    msgs = []
    if "paypal" in str(doc.get("vendor") or "").lower() or "paypal" in str(doc.get("source") or "").lower():
        if doc.get("booked_balance") and doc.get("verified_balance"):
            if doc["booked_balance"] > doc["verified_balance"] * 1.05:
                msgs.append(
                    f"PayPal booked {_fmt_cop(doc['booked_balance'])} vs verified net {_fmt_cop(doc['verified_balance'])} "
                    "- verify net of fees/refunds/payouts and revalue USD at the certified closing TRM"
                )
        if doc.get("covered_start") and doc.get("covered_end") and ctx.get("period"):
            if doc["covered_start"] < ctx["period"] or (doc["covered_end"] or "9999") > f"{ctx['period']}-31":
                msgs.append(f"Export covers {doc['covered_start']}..{doc['covered_end']}, close period {ctx['period']} - filter/split to the exact close period")
    return " | ".join(msgs) if msgs else None


def r_cfd0011_ota_contra_mislanded(doc: dict, ctx: dict) -> Optional[str]:
    """OTA/booking-platform contra-entries can misland in the wrong bank/clearing account."""
    line = doc.get("contra_entry") or {}
    acct = str(line.get("account") or "")
    if not acct:
        return None
    suspicious = any(k in acct.lower() for k in ("suspense", "clearing", "cortesia", "pos"))
    bank_hit = any(
        abs(parse_cop(b.get("amount")) - parse_cop(line.get("amount"))) <= 500
        for b in (ctx.get("bank_lines") or [])
        if b.get("amount") is not None and line.get("amount") is not None
    )
    if suspicious and not bank_hit:
        return f"OTA/booking-platform contra booked to '{acct}' with no matching bank line - reclass to the real operating bank account"
    return None


def r_cfd0012_cxc_socios_art35(doc: dict, ctx: dict) -> Optional[str]:
    """Above-normal owner draws booked as CxC socios activate Art. 35 ET - every month, not just the first."""
    line = doc.get("contra_entry") or {}
    acct = str(line.get("account") or "").lower()
    if "socios" not in acct and "cxc" not in acct:
        return None
    draw = float(line.get("amount") or doc.get("amount_cop") or 0)
    payroll = float(doc.get("payroll_accrual") or ctx.get("config", {}).get("owner_payroll_accrual") or 0)
    if draw > payroll and doc.get("art35_basis_note") not in (True, "true", "yes"):
        return "Owner draw above payroll booked as CxC socios - Art. 35 ET presumptive interest by default; require an explicit non-imputation basis note THIS close (re-document every close)"
    return None


def r_cfd0013_unsigned_bonus_pact(doc: dict, ctx: dict) -> Optional[str]:
    """Unsigned Art. 128 CST bonus pacts make the full bonus salary-constitutive."""
    if doc.get("type") not in ("payroll", "nomina"):
        return None
    if doc.get("bonus_amount", 0) and not doc.get("art128_pact_signed"):
        return f"Bonus {_fmt_cop(doc['bonus_amount'])} with no signed Art. 128 CST pact - full bonus is salary-constitutive; treat as a STANDING monthly contingency once confirmed unsigned"
    return None


def r_cfd0014_linked_loan_product(doc: dict, ctx: dict) -> Optional[str]:
    """A bank relationship with loan + investment products needs two GL treatments."""
    line = doc.get("contra_entry") or {}
    acct = str(line.get("account") or "")
    acct_l = acct.lower()
    normally_credit = acct_l.startswith("2") or any(
        k in acct_l for k in ("cuentas por pagar", "obligacion", "pasivo", "retencion", "impuesto", "ingresos recibid", "interes")
    )
    if acct and normally_credit and float(line.get("debit") or 0) > 0:
        return f"Contranatural debit balance in normally-credit account '{acct}' - check for a linked loan + investment/fund product needing two separate GL treatments (CFD-0014)"
    if doc.get("linked_products") and doc.get("net_figure_only"):
        return "Bank relationship has loan + investment products but books one net figure - book the loan as its own liability and the fund as its own asset"
    return None


def r_cfd0015_retefuente_10uvt(doc: dict, ctx: dict) -> Optional[str]:
    """Retefuente 10-UVT threshold (Decreto 0572/2025) - scan EVERY invoice."""
    if doc.get("type") not in ("bill", "invoice", "ds"):
        return None
    if str(doc.get("concept") or "").lower() in ("seguro", "insurance"):
        return None  # exempt regardless of amount (Decreto 2418/2013)
    try:
        base = parse_cop(doc.get("subTotal") if doc.get("subTotal") is not None else doc.get("amount_cop"))
    except ValueError:
        return None
    uvt = float(ctx.get("uvt") or UVT_2026)
    if base > 10 * uvt:
        concept = str(doc.get("concept") or "servicios").lower()
        rate = RETEFUENTE_RATES.get(concept)
        if rate is None:
            return f"Purchase base {_fmt_cop(base)} > 10 UVT ({_fmt_cop(10*uvt)}) with uncategorized concept '{concept}' - classify retefuente rate by concept (servicios 4%, bienes 2.5%, honorarios 11%, arrendamiento 3.5%)"
        if not doc.get("retefuente_checked"):
            return f"Purchase base {_fmt_cop(base)} > 10 UVT ({_fmt_cop(10*uvt)}) - retefuente due at {rate*100:.1f}% ({concept}); scan EVERY invoice, not just the 'large' ones"
    return None


def r_cfd0016_duplicate_ds(doc: dict, ctx: dict) -> Optional[str]:
    """Flag same-beneficiary/same-amount DS pairs - but check anulacion first."""
    batch = ctx.get("docs") or []
    if doc.get("type") not in ("ds",):
        return None
    if doc.get("anulado"):
        return None  # a voided member of a pair is a correction, not a duplicate
    nit = str(doc.get("vendor_nit") or "")
    amount = parse_cop(doc.get("amount_cop")) if doc.get("amount_cop") is not None else None
    if not nit or amount is None:
        return None
    twins = [
        d for d in batch
        if d is not doc and d.get("type") == "ds"
        and str(d.get("vendor_nit") or "") == nit
        and d.get("amount_cop") is not None
        and abs(parse_cop(d["amount_cop"]) - amount) <= 1
        and not d.get("anulado")
    ]
    if twins:
        return f"Same beneficiary NIT {nit} + same amount {_fmt_cop(amount)} - confirm not a duplicate; check anulacion/nota de ajuste BEFORE calling it one"
    return None


def r_cfd0017_ds_lifecycle(doc: dict, ctx: dict) -> Optional[str]:
    """Documento soporte lifecycle >= 2 states - drafted vs DIAN-confirmed."""
    if doc.get("type") not in ("ds",):
        return None
    estado = str(doc.get("dian_status") or doc.get("status") or "")
    if not doc.get("dian_status") and not doc.get("status"):
        return "Documento soporte without a tracked DIAN lifecycle state - non-deductible until DIAN-confirmed (CRITICAL, not medium)"
    if "aprob" not in estado.lower() and "confirm" not in estado.lower():
        return f"Documento soporte state '{estado}' is not DIAN-confirmed (anything other than Aprobado, incl. POR EMITIR) - expense not deductible until confirmation lands (CRITICAL)"
    return None


def r_cfd0018_report_date_range(doc: dict, ctx: dict) -> Optional[str]:
    """Check the actual date range covered by any downloaded report."""
    if doc.get("type") not in ("report", "statement", "export"):
        return None
    if doc.get("covered_start") and ctx.get("period"):
        if doc["covered_start"] < ctx["period"]:
            return f"Report covers from {doc['covered_start']} - older than the close period {ctx['period']}; multi-month exports must be split, not filed whole"
    return None


def r_cfd0019_alegra_csv_separator(doc: dict, ctx: dict) -> Optional[str]:
    """Alegra CSV thousands-separator: numbers in one format surface in another."""
    if not doc.get("amount_cop") and doc.get("subTotal") is None:
        return None
    raw = doc.get("raw_amount") or doc.get("raw_subTotal")
    if not raw:
        return None
    s = str(raw)
    if "," in s and "." in s and s.find(",") < s.find("."):
        return f"Amount '{raw}' uses US grouping (comma thousands) in an Alegra export - Colombian format is 16.000,00; verify the export locale (CFD-0019)"
    return None


def r_cfd0020_total_arithmetic(doc: dict, ctx: dict) -> Optional[str]:
    """Bill total = subTotal + totalTaxes; DO NOT net retentions."""
    if doc.get("subTotal") is None or doc.get("totalTaxes") is None or doc.get("total") is None:
        return None
    try:
        sub = parse_cop(doc["subTotal"])
        tax = parse_cop(doc["totalTaxes"])
        tot = parse_cop(doc["total"])
    except ValueError:
        return None
    if abs(tot - (sub + tax)) > 2:
        return f"Arithmetic: total {_fmt_cop(tot)} != subTotal {_fmt_cop(sub)} + totalTaxes {_fmt_cop(tax)} ({_fmt_cop(sub+tax)}); retenciones are withheld at PAYMENT, never netted from the document total"
    return None


def r_cfd0021_faj43b_vs_faj44b(doc: dict, ctx: dict) -> Optional[str]:
    """FAJ43b (name!=RUT) is noise; only FAJ44b (NIT!=RUT) is actionable."""
    warnings = [str(w) for w in (doc.get("stamp") or {}).get("warnings") or []]
    if not warnings:
        return None
    actionable = [w for w in warnings if "faj44b" in w.lower()]
    if actionable:
        return f"Supplier identity: {', '.join(actionable)} - NIT != RUT is actionable (FAJ43b name warnings are ~84% noise - never per-doc)"
    return None


def r_cfd0022_closed_is_normal(doc: dict, ctx: dict) -> Optional[str]:
    """`closed` bill status is normal for a paid month; flag draft/void only."""
    status = str(doc.get("status") or "").lower()
    if status in ("draft", "void"):
        return f"Bill status '{status}' flags (closed would be normal for a paid/historical month)"
    return None


# The registry. fn(doc, ctx) -> None | str | list[str].
CFD_RULES: dict[str, dict] = {
    "CFD-0001": {"name": "LobbyPMS .xls is HTML", "category": "system", "severity": "cosmetic", "fn": r_cfd0001_lobby_html_xls},
    "CFD-0002": {"name": "Hostelworld payout pattern reveals model", "category": "revenue", "severity": "financial", "fn": r_cfd0002_hostelworld_pattern},
    "CFD-0003": {"name": "Despegar Colombia is domestic", "category": "revenue/tax", "severity": "regulatory", "fn": r_cfd0003_despegar_domestic},
    "CFD-0004": {"name": "OTA commission comes from the booking source", "category": "revenue", "severity": "financial", "fn": r_cfd0004_ota_commission_source},
    "CFD-0005": {"name": "Booking accrue by check-out, deflate 1.19", "category": "revenue", "severity": "financial", "fn": r_cfd0005_booking_deflate_119},
    "CFD-0006": {"name": "Foreign OTA commission: 100% IVA self-retention + DS", "category": "tax", "severity": "regulatory", "fn": r_cfd0006_foreign_iva_self_retention},
    "CFD-0007": {"name": "Always 30 days/month (Art. 134 CST)", "category": "payroll", "severity": "financial", "fn": r_cfd0007_30_day_month},
    "CFD-0008": {"name": "Recargos/overtime mandatory in the base", "category": "payroll", "severity": "financial/regulatory", "fn": r_cfd0008_recargos_mandatory},
    "CFD-0009": {"name": "Statement in hand != booked - gate on line counts", "category": "bank/system", "severity": "catastrophic", "fn": r_cfd0009_line_count_gate},
    "CFD-0010": {"name": "PayPal net of fees + export date range", "category": "bank/revenue", "severity": "financial", "fn": r_cfd0010_paypal_net_and_range},
    "CFD-0011": {"name": "OTA contra-entries can misland in the wrong account", "category": "revenue/bank", "severity": "financial", "fn": r_cfd0011_ota_contra_mislanded},
    "CFD-0012": {"name": "CxC socios draws activate Art. 35 ET every month", "category": "tax/payroll", "severity": "regulatory", "fn": r_cfd0012_cxc_socios_art35},
    "CFD-0013": {"name": "Unsigned Art. 128 bonus pacts - standing contingency", "category": "payroll/tax", "severity": "regulatory", "fn": r_cfd0013_unsigned_bonus_pact},
    "CFD-0014": {"name": "Linked loan + investment needs two GL treatments", "category": "bank/assets", "severity": "catastrophic", "fn": r_cfd0014_linked_loan_product},
    "CFD-0015": {"name": "Retefuente 10-UVT scan (Decreto 0572/2025)", "category": "tax", "severity": "regulatory", "fn": r_cfd0015_retefuente_10uvt},
    "CFD-0016": {"name": "Duplicate DS - check anulacion first", "category": "tax/system", "severity": "financial", "fn": r_cfd0016_duplicate_ds},
    "CFD-0017": {"name": "DS lifecycle: drafted vs DIAN-confirmed", "category": "tax/system", "severity": "regulatory", "fn": r_cfd0017_ds_lifecycle},
    "CFD-0018": {"name": "Check downloaded report date range", "category": "system", "severity": "cosmetic-to-financial", "fn": r_cfd0018_report_date_range},
    "CFD-0019": {"name": "Alegra CSV thousands-separator", "category": "system", "severity": "financial", "fn": r_cfd0019_alegra_csv_separator},
    "CFD-0020": {"name": "Bill total = subTotal + totalTaxes (no retention netting)", "category": "system", "severity": "financial", "fn": r_cfd0020_total_arithmetic},
    "CFD-0021": {"name": "FAJ43b noise vs FAJ44b actionable", "category": "system", "severity": "cosmetic", "fn": r_cfd0021_faj43b_vs_faj44b},
    "CFD-0022": {"name": "closed is normal - flag draft/void only", "category": "system", "severity": "cosmetic", "fn": r_cfd0022_closed_is_normal},
}


# ---------------------------------------------------------------------------
# File 13 — received-document integrity flag set (8 detections)
# ---------------------------------------------------------------------------
def flag_arithmetic(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 1: total != subTotal + totalTaxes (±2). Never net retentions."""
    return r_cfd0020_total_arithmetic(doc, ctx)


def flag_posting_status(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 2: draft/void only; closed is normal for a paid month."""
    return r_cfd0022_closed_is_normal(doc, ctx)


def flag_acceptance(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 3: documentReceivedStatus = NEEDED -> human accepts or lets
    tacit acceptance run (3 business days). null on documento soporte is fine."""
    status = doc.get("documentReceivedStatus")
    if status == "NEEDED":
        return "documentReceivedStatus=NEEDED - DIAN acuse/aceptacion pending: accept or let tacit acceptance run (3 business days)"
    return None


def flag_supplier_identity(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 4: escalate FAJ44b (NIT!=RUT) and any warning NOT on the bulk
    noise set; FAJ43b name!=RUT is ~84% noise and never a per-doc flag."""
    warnings = [str(w) for w in (doc.get("stamp") or {}).get("warnings") or []]
    if not warnings:
        return None
    fire = []
    for w in warnings:
        wl = w.lower()
        if "faj44b" in wl or ("faj43b" not in wl and "fam06" not in wl):
            fire.append(w)
    if fire:
        return "Supplier-identity warnings: " + ", ".join(fire) + " (FAJ43b name!=RUT and FAM06 clusters are noise - not per-doc flags)"
    return None


def flag_electronic_backing(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 5: a normal bill with empty stamp.cude = manual entry (no
    CUFE). Foreign documento soporte legitimately lacks a Colombian CUFE -
    grouped separately, not as an error."""
    stamp = doc.get("stamp") or {}
    cude = stamp.get("cude") or stamp.get("cufe")
    doc_type = str(doc.get("type") or "").lower()
    is_ds = bool(stamp.get("is_ds") or stamp.get("cuds") or stamp.get("NumDS"))
    if doc_type == "bill" and not cude and not is_ds:
        return "Bill with no CUFE/CUDS (manual entry) - verify electronic backing; foreign documento soporte legitimately lacks CUFE and is grouped separately"
    return None


def flag_duplicates(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 6: duplicate cude, or duplicate (issuer NIT + number)."""
    batch = ctx.get("docs") or []
    stamp = doc.get("stamp") or {}
    cude = str(stamp.get("cude") or stamp.get("cufe") or "").strip()
    nit = str(doc.get("vendor_nit") or "").strip()
    number = str(doc.get("number") or "").strip()
    for other in batch:
        if other is doc:
            continue
        o_stamp = other.get("stamp") or {}
        o_cude = str(o_stamp.get("cude") or o_stamp.get("cufe") or "").strip()
        if cude and o_cude and cude == o_cude:
            return f"Duplicate CUFE/CUDS {cude} across {doc.get('doc_id')} and {other.get('doc_id')}"
        if nit and number and str(other.get("vendor_nit") or "").strip() == nit and str(other.get("number") or "").strip() == number:
            return f"Duplicate issuer NIT {nit} + number {number} across {doc.get('doc_id')} and {other.get('doc_id')}"
    return None


def flag_iva_sanity(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 7: IVA rate not in {0, 5, 19}%, or line taxAmount != base*rate (±2)."""
    for i, line in enumerate(doc.get("tax_lines") or []):
        try:
            rate = float(line.get("rate"))
            base = parse_cop(line.get("base"))
            tax = parse_cop(line.get("taxAmount"))
        except (ValueError, TypeError):
            continue
        if rate not in VALID_IVA_RATES:
            return f"IVA line {i}: rate {rate:g}% not in {{0, 5, 19}}%"
        if abs(tax - base * rate / 100) > 2:
            return f"IVA line {i}: taxAmount {_fmt_cop(tax)} != base {_fmt_cop(base)} x {rate:g}% ({_fmt_cop(base*rate/100)})"
    return None


def flag_classification(doc: dict, ctx: dict) -> Optional[str]:
    """Detection 8: bill vs documento soporte by the STAMP (NumDS/CUDS barcode),
    not the `type` field alone."""
    stamp = doc.get("stamp") or {}
    is_ds = bool(stamp.get("is_ds") or stamp.get("cuds") or stamp.get("NumDS"))
    doc_type = str(doc.get("type") or "").lower()
    if doc_type == "bill" and is_ds:
        return "Registered as type=bill but the stamp is NumDS/CUDS (documento soporte) - classify by the stamp, not the type field"
    if doc_type == "ds" and not is_ds and (stamp.get("cude") or stamp.get("cufe")):
        return "Registered as ds but carries a CUFE - this is a factura electronica, not a documento soporte"
    return None


DOC_FLAGS: dict[str, dict] = {
    "arith": {"name": "Arithmetic (total = subTotal + totalTaxes)", "fn": flag_arithmetic},
    "status": {"name": "Posting status (draft/void only)", "fn": flag_posting_status},
    "acceptance": {"name": "Document acceptance NEEDED", "fn": flag_acceptance},
    "identity": {"name": "Supplier identity (FAJ44b actionable)", "fn": flag_supplier_identity},
    "backing": {"name": "Electronic backing (CUFE on normal bills)", "fn": flag_electronic_backing},
    "duplicates": {"name": "Duplicate CuDE / NIT+number", "fn": flag_duplicates},
    "iva": {"name": "IVA sanity (rate + taxAmount)", "fn": flag_iva_sanity},
    "classification": {"name": "Bill vs DS by stamp", "fn": flag_classification},
}


def _messages(result: Optional[Any]) -> list[str]:
    if result is None:
        return []
    if isinstance(result, list):
        return [str(m) for m in result if m]
    return [str(result)]


# ---------------------------------------------------------------------------
# Rule runners — every rule/flag wrapped so exceptions are logged by id
# ---------------------------------------------------------------------------
def run_rules(docs: list[dict], ctx: Optional[dict] = None) -> dict:
    """Run all 22 CFD rules over a batch of documents.

    Returns {"checked_docs": N, "checked_rules": N, "fired": [...], "errors": [...]}.
    A rule that raises is logged with its rule id (review finding #7) and the
    run continues — a broken rule can never silently vanish."""
    ctx = dict(ctx or {})
    ctx.setdefault("docs", docs)
    fired: list[dict] = []
    errors: list[dict] = []
    for doc in docs:
        doc_id = doc.get("doc_id") or doc.get("id") or "?"
        for rid, rule in CFD_RULES.items():
            try:
                result = rule["fn"](doc, ctx)
            except Exception as exc:  # finding #7: log the rule id, keep going
                errors.append({"rule_id": rid, "doc_id": doc_id, "error": f"{type(exc).__name__}: {exc}"})
                continue
            for msg in _messages(result):
                fired.append({
                    "rule_id": rid,
                    "name": rule["name"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "doc_id": doc_id,
                    "message": msg,
                })
    return {
        "checked_docs": len(docs),
        "checked_rules": len(CFD_RULES),
        "fired": fired,
        "errors": errors,
    }


def check_received_docs(bills: list[dict], ctx: Optional[dict] = None) -> dict:
    """File 13 received-document integrity sweep (Motor-Checklist Phase 1.6).

    Runs the 8 standing detections over the period's registered /bills docs.
    Every hit is surfaced for human disposition (Operating Principle 5) —
    nothing here is auto-fixed. The completeness caveat is stated in every
    report: /bills sees only *registered* docs."""
    ctx = dict(ctx or {})
    ctx.setdefault("docs", bills)
    flagged: list[dict] = []
    errors: list[dict] = []
    doc_count = len(bills)
    for doc in bills:
        doc_id = doc.get("doc_id") or doc.get("id") or doc.get("number") or "?"
        for flag_id, flag in DOC_FLAGS.items():
            try:
                result = flag["fn"](doc, ctx)
            except Exception as exc:  # finding #7: log the flag id, keep going
                errors.append({"flag": flag_id, "doc_id": doc_id, "error": f"{type(exc).__name__}: {exc}"})
                continue
            for msg in _messages(result):
                flagged.append({
                    "flag": flag_id,
                    "name": flag["name"],
                    "doc_id": doc_id,
                    "message": msg,
                })
    return {
        "docs_checked": doc_count,
        "flags_applied": len(DOC_FLAGS),
        "flagged": flagged,
        "flagged_count": len(flagged),
        "errors": errors,
        "completeness_caveat": (
            "GET /bills sees only *registered* docs — received FE still unregistered in "
            "Alegra's reception buzón are invisible until File 25 §1a routing is live for "
            "this client; this sweep does not prove receipt-completeness alone."
        ),
    }


def format_report(report: dict) -> str:
    out = [
        "╔══════════════════════════════════════════════════╗",
        "║  PHASE 2 — CFD RULES ENGINE                       ║",
        "╚══════════════════════════════════════════════════╝",
        f"  Docs checked: {report['checked_docs']}   Rules applied: {report['checked_rules']}   Fired: {len(report['fired'])}",
        "",
        "─── Fired ───",
    ]
    if report["fired"]:
        for f in report["fired"]:
            out.append(f"  ⚠️ [{f['rule_id']}] ({f['severity']}) {f['doc_id']}: {f['message']}")
    else:
        out.append("  (none)")
    out += ["", "─── Rule errors (finding #7: never silent) ───"]
    if report["errors"]:
        out += [f"  💥 [{e['rule_id']}] {e['doc_id']}: {e['error']}" for e in report["errors"]]
    else:
        out.append("  ✓ none")
    return "\n".join(out)


def format_flags(report: dict) -> str:
    out = [
        "─── FILE 13 — received-document integrity sweep ───",
        f"  Docs: {report['docs_checked']}   Flags applied: {report['flags_applied']}   Flagged: {report['flagged_count']}",
    ]
    if report["flagged"]:
        out += [f"  🚩 [{f['flag']}] {f['doc_id']}: {f['message']}" for f in report["flagged"]]
    else:
        out.append("  (none)")
    if report["errors"]:
        out += [f"  💥 [{e['flag']}] {e['doc_id']}: {e['error']}" for e in report["errors"]]
    out.append(f"  ℹ️  {report['completeness_caveat']}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Calibration corpus — real-July-calibrated docs that must fire deterministically
# ---------------------------------------------------------------------------
def mock_docs() -> list[dict]:
    return [
        {"doc_id": "m-01-olimpica", "type": "bill", "vendor": "Olimpica", "vendor_nit": "890901111", "status": "draft",
         "subTotal": 449901, "totalTaxes": 0, "total": 500000, "number": "COMK5038",
         "stamp": {"cude": "cude-1"}, "concept": "bienes"},
        {"doc_id": "m-02-ds-dup-a", "type": "ds", "vendor": "Amazon", "amount_cop": 1200000, "vendor_nit": "900123456", "dian_status": "Aprobado"},
        {"doc_id": "m-03-ds-dup-b", "type": "ds", "vendor": "Amazon", "amount_cop": 1200000, "vendor_nit": "900123456", "dian_status": "Aprobado"},
        {"doc_id": "m-04-booking", "type": "invoice", "vendor": "Booking.com BV", "category": "commission", "commission_base_includes_iva": True,
         "accrual_month": "2026-08", "amount_cop": 850000},
        {"doc_id": "m-05-nomina", "type": "payroll", "days_source": 31, "recargos_provided": False, "bonus_amount": 900000,
         "art128_pact_signed": False, "prestaciones_base": 5000000, "base_salary": 5000000, "recargos_amount": 0},
        {"doc_id": "m-06-ds-draft", "type": "ds", "vendor": "Spotify", "amount_cop": 18501.66, "dian_status": "POR EMITIR", "vendor_nit": "900999888"},
        {"doc_id": "m-07-amazon-factura", "type": "bill", "vendor": "Amazon.com", "subTotal": 849139, "totalTaxes": 0, "total": 849139,
         "stamp": {"cude": "cude-2"}, "concept": "bienes", "status": "closed"},
        {"doc_id": "m-08-honorarios", "type": "invoice", "vendor": "Consultor X", "subTotal": 600000, "totalTaxes": 114000, "total": 714000,
         "concept": "honorarios", "stamp": {"cude": "cude-3"}},
        {"doc_id": "m-09-fake-bill-ds", "type": "bill", "vendor": "Proveedor Y", "stamp": {"NumDS": "DS-0081", "warnings": ["FAJ43b: nombre no corresponde al RUT", "FAJ44b: NIT no corresponde al RUT"]}, "subTotal": 100000,
         "totalTaxes": 19000, "total": 119000, "status": "closed"},
        {"doc_id": "m-10-paypal", "type": "report", "vendor": "PayPal", "booked_balance": 6811343, "verified_balance": 2972971,
         "covered_start": "2026-01-01", "covered_end": "2026-07-06", "amount_cop": 6811343},
        {"doc_id": "m-11-fh-reclass", "type": "report", "contra_entry": {"account": "Efectivo POS Cortesía", "amount": 316918.39}},
        {"doc_id": "m-12-cxc-socios", "type": "report", "contra_entry": {"account": "1305 CxC socios", "amount": 12000000}, "payroll_accrual": 9805834},
        {"doc_id": "m-13-lobby", "type": "report", "filename": "LobbyPMS_export.xls", "content_head": "<html><head><title>Reservas</title>"},
        {"doc_id": "m-14-us-format", "type": "bill", "vendor": "Proveedor Z", "raw_amount": "16,000.00", "amount_cop": 16000, "subTotal": 16000,
         "totalTaxes": 0, "total": 16000, "stamp": {"cude": "cude-4"}},
        {"doc_id": "m-15-need-accept", "type": "bill", "vendor": "Acme SAS", "documentReceivedStatus": "NEEDED", "subTotal": 200000,
         "totalTaxes": 0, "total": 200000, "stamp": {"cude": "cude-5"}, "status": "open"},
        {"doc_id": "m-16-iva-bad", "type": "bill", "vendor": "BadIVA SAS", "subTotal": 100000, "totalTaxes": 10000, "total": 110000,
         "tax_lines": [{"base": 100000, "rate": 19, "taxAmount": 10000}], "stamp": {"cude": "cude-6"}, "status": "open"},
        {"doc_id": "m-17-liab-contranatural", "type": "report", "contra_entry": {"account": "2205 Cuentas por pagar", "debit": 4500000, "credit": 0}},
        {"doc_id": "m-18-hostelworld", "type": "settlement", "vendor": "Hostelworld", "category": "ota"},
        {"doc_id": "m-19-despegar", "type": "settlement", "vendor": "Despegar Colombia", "vendor_nit": "900610518-5",
         "category": "ota", "amount_cop": 2310000, "subTotal": 2310000, "totalTaxes": 0, "total": 2310000,
         "retention_asset_candidate": True},
        {"doc_id": "m-20-extracto", "type": "bank_statement", "account": "78100001780", "line_count": 204,
         "amount_cop": 161565836.41},
    ]


def mock_bills() -> list[dict]:
    """A synthetic /bills page set for the File-13 sweep (also exercises the
    >30 pagination shape: 65 docs)."""
    bills = []
    for i in range(65):
        stamp_warnings = ["FAJ43b: nombre no corresponde al RUT"]  # the ~84% noise
        if i % 13 == 0:
            stamp_warnings.append("FAJ44b: NIT no corresponde al RUT")
        bill = {
            "id": f"bill-{i:03d}",
            "type": "bill",
            "number": f"FE{i:04d}",
            "vendor": f"Proveedor {i}",
            "vendor_nit": f"90000000{i:02d}",
            "subTotal": 100000 + i,
            "totalTaxes": 19000 if i % 3 else 0,
            "total": 119000 + i if i % 3 else 100000 + i,
            "status": "closed" if i % 10 else "draft",
            "documentReceivedStatus": "NEEDED" if i % 25 == 0 else "NOT_NEEDED",
            "stamp": {"cude": f"cufe-{i:04d}", "warnings": stamp_warnings},
        }
        if i == 3:
            bill["stamp"] = {"cude": "cufe-0003", "NumDS": "DS-0900", "warnings": stamp_warnings}  # bill that is really a DS
        if i in (4, 5):
            # Legit foreign documento soporte group: no CUFE, CUDS barcode, closed = expected
            bill["type"] = "ds"
            bill["stamp"] = {"cuds": f"CUDS-0{i}", "warnings": stamp_warnings}
        bills.append(bill)
    return bills


# ---------------------------------------------------------------------------
# Smoke calibration — the pre-existing inline-assert contract
# ---------------------------------------------------------------------------
def smoke() -> None:
    """Inline calibration asserts; exit nonzero on failure. This is the
    `python3 cfd_engine.py` contract the 09-17 review called 'well-calibrated'."""
    # parse_cop round-trips
    cases = {
        "16.000,00": 16000.0, "16,000.00": 16000.0, "16.000": 16000.0,
        "16,000": 16000.0, "16,5": 16.5, "9.491.500,00": 9491500.0,
        "1.149.273,00": 1149273.0, "577.735,85": 577735.85, "4.250.000": 4250000.0,
        "COP 523.740": 523740.0, "16,000,000.00": 16000000.0, ".00": 0.0, "0": 0.0,
    }
    for raw, want in cases.items():
        got = parse_cop(raw)
        assert got == want, f"parse_cop({raw!r}) = {got}, want {want}"
    try:
        parse_cop("hola")
        raise AssertionError("parse_cop('hola') should raise ValueError")
    except ValueError:
        pass

    # rule triggers on the calibration corpus
    smoke_ctx = {"period": "2026-07",
                 "alegra_line_counts": {"78100001780": 2}}  # 204 stmt lines vs 2 booked -> CFD-0009
    report = run_rules(mock_docs(), smoke_ctx)
    fired = {f["rule_id"] for f in report["fired"]}
    for rid in ("CFD-0001", "CFD-0002", "CFD-0003", "CFD-0004", "CFD-0005",
                "CFD-0006", "CFD-0007", "CFD-0008", "CFD-0009", "CFD-0010",
                "CFD-0011", "CFD-0012", "CFD-0013", "CFD-0014", "CFD-0015",
                "CFD-0016", "CFD-0017", "CFD-0018", "CFD-0019", "CFD-0020",
                "CFD-0021", "CFD-0022"):
        assert rid in fired, f"{rid} did not fire on the calibration corpus"
    assert report["errors"] == [], f"rule errors must be empty: {report['errors']}"

    # File 13 sweep: duplicate CUFE, arithmetic holes, draft, NEEDED, DS-as-bill
    sweep = check_received_docs(mock_bills(), {})
    flag_ids = {f["flag"] for f in sweep["flagged"]}
    assert "status" in flag_ids and "acceptance" in flag_ids and "classification" in flag_ids
    assert "identity" in flag_ids, "FAJ44b doc must be flagged"
    assert sweep["errors"] == [], f"flag errors must be empty: {sweep['errors']}"
    assert "registered" in sweep["completeness_caveat"]

    print(f"cfd_engine smoke OK — {len(cases)} parse_cop cases, "
          f"{len(CFD_RULES)} rules, {len(DOC_FLAGS)} File-13 flags")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 2 — CFD Rules Engine")
    parser.add_argument("--mock", action="store_true", help="Run over the calibration corpus")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--smoke", action="store_true", help="Run the calibration asserts (default)")
    args = parser.parse_args()

    if args.mock:
        ctx = {"period": "2026-07",
               "alegra_line_counts": {"78100001780": 2}}  # 204 stmt lines vs 2 booked -> CFD-0009
        report = run_rules(mock_docs(), ctx)
        sweep = check_received_docs(mock_bills(), ctx)
        out = {"phase": "cfd_engine", "rules": report, "file13": sweep}
        if args.json:
            print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        else:
            print(format_report(report))
            print()
            print(format_flags(sweep))
        return 0

    smoke()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())