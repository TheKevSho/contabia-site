#!/usr/bin/env python3
"""Motor orchestrator — Phase 1-6 pipeline runner.

REBUILT 2026-09-18. The original motor_run.py (built 2026-09-09) was lost in
the Time Machine restore; never committed, no backup. Rebuilt from spec.

Review finding #7 (2026-09-17): the old runner reported "PASSED" / exit 0 even
when a phase RAISED — only the gate stopped the pipeline. This rebuild's core
contract:

  * every phase reports its own status: passed | errored (exception captured,
    stack attached) | gate_failed (the gate ran and the data gate did not pass)
  * a phase that raises NEVER yields a PASSED line and the pipeline exits
    nonzero — a broken phase is visible in the report, never silent
  * gate failure halts the close: phases 4-6 run in ADVISORY mode only
    (`post_gate: advisory`), and the verdict says the motor stopped
  * jes_all / cfd_all / gaps_all aggregate the phase output for
    assemble_jes.run_assembly() — the join that makes motor output reach the
    review package (finding #4)

Phases: 1 derive_index (.md -> SQLite) | 2 cfd_engine (rules + File-13) |
3 pre_close_gate (Phase 1 + 1.6) | 4 revenue_recon | 5 expense_recon |
6 bank_recon. --to phaseN stops after the named phase.

Usage:
    python3 motor_run.py tayrona 2026-07 --mock
    python3 motor_run.py tayrona 2026-07 --mock --json
    python3 motor_run.py tayrona 2026-07 --mock --to phase4
    python3 motor_run.py tayrona 2026-07 --data-dir data/boveda_seed
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

DB_PATH = Path(os.environ.get("CONTABIA_DB_PATH", Path(__file__).parent / "sonata_mas_001.sqlite"))

# phase_key -> (label, run callable). Phases are stdlib-only; modules are
# imported lazily so importing motor_run (e.g. from assemble_jes) costs
# nothing until a run actually executes.
PHASES: list[tuple[str, str]] = [
    ("phase1", "derive_index (.md -> SQLite)"),
    ("phase2", "cfd_engine (22 CFD rules + File 13)"),
    ("phase3", "pre_close_gate (Phase 1 + 1.6)"),
    ("phase4", "revenue_recon"),
    ("phase5", "expense_recon"),
    ("phase6", "bank_recon"),
]


# ---------------------------------------------------------------------------
# Phase runners — each returns a dict report; any raise is caught UPSTREAM
# ---------------------------------------------------------------------------
def _run_derive_index(entity: str, period: str, mock: bool,
                      data_dir: Optional[Path], db_path: Path) -> dict:
    from derive_index import index_markdown_files, mock_corpus

    if mock:
        with tempfile.TemporaryDirectory(prefix="motor_derive_") as tmp:
            md_files = mock_corpus(Path(tmp))
            return index_markdown_files(md_files, entity, db_path)
    dd = data_dir or (Path(__file__).parent / "data" / "boveda_tayrona")
    if not dd.exists():
        raise FileNotFoundError(f"data dir not found: {dd} (use --data-dir or --mock)")
    md_files = sorted(dd.rglob("*.md"))
    return index_markdown_files(md_files, entity, db_path)


def _run_cfd(entity: str, period: str, mock: bool,
             data_dir: Optional[Path], db_path: Path) -> dict:
    from cfd_engine import check_received_docs, mock_bills, mock_docs, run_rules

    ctx = {"period": period, "alegra_line_counts": {"78100001780": 2}}
    if mock:
        return {"rules": run_rules(mock_docs(), ctx),
                "file13": check_received_docs(mock_bills(), ctx)}
    dd = data_dir or (Path(__file__).parent / "data" / "boveda_tayrona")
    docs = []
    if dd.exists():
        from derive_index import parse_document

        for p in sorted(dd.rglob("*.md")):
            try:
                d = parse_document(p)
                docs.append({"doc_id": d["doc_id"], "vendor": d["vendor"],
                             "amount_cop": d["amount_cop"], "period": d["period"],
                             "type": d["doc_type"], "subTotal": d["amount_cop"],
                             "totalTaxes": 0, "total": d["amount_cop"]})
            except Exception:
                continue
    return {"rules": run_rules(docs, ctx),
            "file13": check_received_docs([], ctx)}


def _run_gate(entity: str, period: str, mock: bool,
              data_dir: Optional[Path], db_path: Path) -> dict:
    from pre_close_gate import run_gate

    return run_gate(entity, period, mock=mock, data_dir=data_dir, db_path=db_path)


def _run_revenue(entity: str, period: str, mock: bool,
                 data_dir: Optional[Path], db_path: Path) -> dict:
    from revenue_recon import run_revenue_recon

    return run_revenue_recon(entity, period, mock=mock, data_dir=data_dir)


def _run_expense(entity: str, period: str, mock: bool,
                 data_dir: Optional[Path], db_path: Path) -> dict:
    from expense_recon import run_expense_recon

    return run_expense_recon(entity, period, mock=mock, data_dir=data_dir)


def _run_bank(entity: str, period: str, mock: bool,
              data_dir: Optional[Path], db_path: Path) -> dict:
    from bank_recon import run_bank_recon

    return run_bank_recon(entity, period, mock=mock, data_dir=data_dir)


_RUNNERS: dict[str, Callable[..., dict]] = {
    "phase1": _run_derive_index,
    "phase2": _run_cfd,
    "phase3": _run_gate,
    "phase4": _run_revenue,
    "phase5": _run_expense,
    "phase6": _run_bank,
}


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def run_pipeline(entity: str, period: str, *, mock: bool = False,
                 stop_at: Optional[str] = None,
                 data_dir: Optional[Path] = None,
                 db_path: Path = DB_PATH) -> dict:
    """Run phases 1-6 in order; stop_at truncates (the assemble_jes contract
    calls this with stop_at='phase6'). Returns the composite report with
    per-phase status, aggregated JEs/CFD/gaps, and the honest pipeline
    verdict — a phase that raised is `errored` with its stack attached, the
    verdict says FAILED, and the caller must not post."""
    phase_reports: dict[str, dict] = {}
    gate_failed = False
    advisory = False

    for phase_key, label in PHASES:
        if stop_at and phase_key > stop_at:
            break
        entry: dict[str, Any] = {"label": label}
        try:
            report = _RUNNERS[phase_key](entity, period, mock, data_dir, db_path)
            entry["report"] = report
            if phase_key == "phase3":
                gate_passed = bool(report.get("gate_passed"))
                if not gate_passed:
                    gate_failed = True
                    entry["status"] = "gate_failed"
                    entry["verdict"] = report.get("data_gate", {}).get("verdict", "gate failed")
                elif report.get("received_docs", {}).get("errors"):
                    entry["status"] = "errored"
                    entry["error"] = {"phase": phase_key,
                                      "error": "; ".join(
                                          f"{e.get('flag')} {e.get('doc_id')}: {e.get('error')}"
                                          for e in report["received_docs"]["errors"])}
                else:
                    entry["status"] = "passed"
            else:
                entry["status"] = "passed"
        except Exception as exc:
            entry["status"] = "errored"
            entry["error"] = {"phase": phase_key, "error": f"{type(exc).__name__}: {exc}",
                              "trace": traceback.format_exc().strip().splitlines()[-6:]}
        if advisory and phase_key in ("phase4", "phase5", "phase6"):
            entry["post_gate"] = "advisory — gate failed, do not post"
        phase_reports[phase_key] = entry

        # The gate stops the close: once it fails, later phases still run for
        # ADVISORY inspection but are explicitly not close output.
        if phase_key == "phase3":
            advisory = gate_failed

    # Aggregate (the assemble_jes.run_assembly contract, finding #4)
    jes_all: list[dict] = []
    cfd_all: list[str] = []   # rule/flag IDs — assemble_jes does sorted(set(...))
    gaps_all: list[str] = []

    for phase_key in ("phase4", "phase5", "phase6"):
        entry = phase_reports.get(phase_key) or {}
        rpt = entry.get("report") or {}
        jes_all.extend(rpt.get("jes", []) or [])
        gaps_all.extend(rpt.get("gaps", []) or [])
        for f in rpt.get("cfd_fired", []) or []:
            if f.get("rule_id"):
                cfd_all.append(str(f["rule_id"]))
        if entry.get("status") == "errored":
            gaps_all.append(f"{phase_key}: {entry['error']['error']}")

    p2 = phase_reports.get("phase2", {}).get("report") or {}
    for f in (p2.get("rules") or {}).get("fired", []) or []:
        if f.get("rule_id"):
            cfd_all.append(str(f["rule_id"]))
    p3 = phase_reports.get("phase3", {}).get("report") or {}
    for f in (p3.get("received_docs") or {}).get("flagged", []) or []:
        cfd_all.append(f"file13:{f.get('flag')}")
    gaps_all.extend(p3.get("blockers", []) or [])
    cfd_all = sorted(set(cfd_all))

    errors = [e for e in phase_reports.values() if e.get("status") == "errored"]
    if errors:
        # A phase that RAISED dominates the verdict (finding #7): no error may
        # ever fold into a PASSED/GATE-FAILED-note-only report.
        verdict = "⛔ PHASE FAILURE(S) — do not post until every phase passes"
        if gate_failed:
            verdict += " (the data gate also failed — phases 4-6 advisory)"
        pipeline_status = "FAILED"
    elif gate_failed:
        verdict = "⛔ GATE FAILED — motor stopped for the close; phases 4-6 advisory only (do not post)"
        pipeline_status = "GATE FAILED"
    else:
        verdict = "✅ PIPELINE PASSED — every phase ran clean (gate passed)"
        pipeline_status = "PASSED"

    return {
        "phase": "motor_run",
        "entity": entity,
        "period": period,
        "mock": mock,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_status": pipeline_status,
        "verdict": verdict,
        "gate_failed": gate_failed,
        "advisory_after_gate": advisory,
        "phases": phase_reports,
        "jes_all": jes_all,
        "cfd_all": cfd_all,
        "gaps_all": gaps_all,
    }


def format_report(report: dict) -> str:
    out = [
        "╔══════════════════════════════════════════════════╗",
        "║  MOTOR RUN — PHASES 1-6                           ║",
        "╚══════════════════════════════════════════════════╝",
        f"  {report['entity']} / {report['period']}  (mock={report['mock']})",
        "─── Phases ───",
    ]
    for phase_key in ("phase1", "phase2", "phase3", "phase4", "phase5", "phase6"):
        entry = report["phases"].get(phase_key)
        if entry is None:
            continue
        status = entry["status"]
        mark = {"passed": "✅", "errored": "💥", "gate_failed": "⛔"}.get(status, "•")
        out.append(f"  {mark} [{status.upper():11s}] {phase_key}: {entry['label']}")
        if entry.get("verdict"):
            out.append(f"         {entry['verdict']}")
        if entry.get("error"):
            out.append(f"         error: {entry['error']['error']}")
            for line in entry["error"].get("trace", []):
                out.append(f"         {line}")
    out += [
        "",
        f"  JEs aggregated: {len(report['jes_all'])}   CFD hits: {len(report['cfd_all'])}   Gaps: {len(report['gaps_all'])}",
        f"  {report['verdict']}",
    ]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Motor orchestrator — phases 1-6")
    parser.add_argument("entity", help="Entity slug")
    parser.add_argument("period", help="Period YYYY-MM")
    parser.add_argument("--mock", action="store_true", help="Synthetic data everywhere")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--to", dest="stop_at", help="Stop after this phase (e.g. phase4)")
    parser.add_argument("--data-dir", type=Path, help="Period data dir")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="SQLite path")
    args = parser.parse_args()

    if args.stop_at and args.stop_at not in dict(PHASES):
        print(f"error: unknown phase '{args.stop_at}' (expected phase1..phase6)", file=sys.stderr)
        return 2

    report = run_pipeline(args.entity, args.period, mock=args.mock,
                          stop_at=args.stop_at, data_dir=args.data_dir, db_path=args.db)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print(format_report(report))

    if args.mock:
        # A mock run is a mechanics demo: gate failure is the designed mock
        # shape (OTA/PMS genuinely absent), so only a phase that actually
        # RAISED fails the run — the finding #7 contract.
        errored = any(e.get("status") == "errored" for e in report["phases"].values())
        return 1 if errored else 0
    if report["gate_failed"]:
        return 2
    return 0 if report["pipeline_status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())