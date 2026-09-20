#!/usr/bin/env python3
"""Phase 3 — Pre-Close Gate (Motor-Checklist Phase 1 + Phase 1.6).

REBUILT 2026-09-18. The original pre_close_gate.py (built 2026-09-09) was
lost in the Time Machine restore — never committed; no backup between
2026-08-24 and the restore. Rebuilt from the Motor-Checklist spec.

What it does, in order:
  Phase 1  — data-availability gate: bank statement, payroll variables, OTA
             reports, PMS export, reviewed staged intake. Evidence is pulled
             from the canonical .md corpus (canonical_documents, if indexed)
             AND a filesystem scan of the period's data dir — a file that
             exists but was never indexed still counts, and vice versa.
             Any missing gate item => gate FAILS: "Stop. Don't run the motor.
             Contact client for missing data." (Checklist, Phase 1).
  Phase 1.6 — received-document integrity review for Alegra-SoR clients:
             `GET /bills` paged to EXHAUSTION (the 2026-09-17 review finding
             #7: the original pagination could silently drop bills past the
             first 30 — Alegra caps page size at 30), then the 8 File-13
             detections from cfd_engine. In live mode pulls the real API;
             --mock serves a synthetic 65-doc paged API so the >30 shape is
             exercised on every run. Human disposition only — never auto-fix.

Zero LLM, pure stdlib + sqlite3; the live /bills pull goes through the same
alegra_client the portal uses (requests, already a repo dependency).

Usage:
    python3 pre_close_gate.py tayrona 2026-07 --mock
    python3 pre_close_gate.py tayrona 2026-07 --mock --json
    python3 pre_close_gate.py tayrona 2026-07 --data-dir data/boveda_seed
    python3 pre_close_gate.py tayrona 2026-07                # live /bills

Exit: 0 = phase ran (mock, or live with gate passed / gate failure reported);
      1 = internal error (creds missing in live mode, data dir missing);
      2 = live gate FAILED (stop the motor per Phase 1).
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import boveda_source  # tree-aware period resolution: one canonical source

DB_PATH = Path(os.environ.get("CONTABIA_DB_PATH", Path(__file__).parent / "sonata_mas_001.sqlite"))
GATE_PAGE_SIZE = 30  # Alegra /bills cap (Phase 1.6, File 07: "paginate /bills to exhaustion")


# ---------------------------------------------------------------------------
# Phase 1 — data availability
# ---------------------------------------------------------------------------
# Each gate item: key, human label, and filename/doctype patterns that count
# as evidence the data is in hand. Patterns are matched against lowercased
# filenames and canonical_documents doc_type/vendor values.
GATE_ITEMS: list[dict] = [
    {
        "key": "bank_statement",
        "label": "Bank statement for the month (CSV or API pull)",
        "file_pats": ["bancolombia", "78100001780", "bbva", "9638124968", "extracto", "bank", "statement"],
        "doc_types": ["bank_statement"],
    },
    {
        "key": "card_statement",
        "label": "Card/processor statement (Bold, datáfono, PayPal)",
        "file_pats": ["bold", "datáfono", "dat afono", "paypal", "card"],
        "doc_types": ["card_statement"],
    },
    {
        "key": "payroll",
        "label": "Payroll variables / PILA (hours, overtime, absences)",
        "file_pats": ["planilla", "pila", "nomina", "nómina", "liquidacion", "liquidación"],
        "doc_types": ["payroll"],
    },
    {
        "key": "ota_booking",
        "label": "OTA report — Booking.com invoice (if applicable)",
        "file_pats": ["booking"],
        "doc_types": [],
        "vendor_pats": ["booking"],
    },
    {
        "key": "ota_airbnb",
        "label": "OTA report — Airbnb payout report (if applicable)",
        "file_pats": ["airbnb"],
        "doc_types": [],
        "vendor_pats": ["airbnb"],
    },
    {
        "key": "ota_hostelworld",
        "label": "OTA report — Hostelworld settlement (if applicable)",
        "file_pats": ["hostelworld"],
        "doc_types": [],
        "vendor_pats": ["hostelworld"],
    },
    {
        "key": "ota_despegar",
        "label": "OTA report — Despegar settlement (if applicable)",
        "file_pats": ["despegar"],
        "doc_types": [],
        "vendor_pats": ["despegar"],
    },
    {
        "key": "ota_other",
        "label": "OTA report — any other OTA in use (GYG, Viator, FareHarbor)",
        "file_pats": ["getyourguide", "gyg", "viator", "fareharbor", "ota", "settlement"],
        "doc_types": [],
        "vendor_pats": ["getyourguide", "gyg", "viator", "fareharbor"],
    },
    {
        "key": "pms",
        "label": "PMS data export (LobbyPMS or equivalent)",
        "file_pats": ["lobby", "pms", "dashboard", "reservas"],
        "doc_types": ["report"],
    },
    {
        "key": "intake_reviewed",
        "label": "Continuous intake staged entries reviewed (exception register)",
        "file_pats": ["exception_register"],
        "doc_types": ["register"],
    },
]


def _period_in_name(name: str, period: str) -> bool:
    """Evidence must be for THIS period: '2026-07', 'julio', 'jul2026',
    '2026_07', '07-2026' in the filename/path."""
    yy, mm = period.split("-")
    month_names = {"01": "ene", "02": "feb", "03": "mar", "04": "abr", "05": "may",
                   "06": "jun", "07": "jul", "08": "ago", "09": "sep", "10": "oct",
                   "11": "nov", "12": "dic"}
    tokens = [f"{yy}{mm}", f"{yy}-{mm}", f"{yy}_{mm}", f"{yy}/{mm}",
              f"{mm}-{yy}", month_names[mm], month_names[mm] + yy[-2:]]
    low = name.lower()
    return any(t.lower() in low for t in tokens)


def _scan_dir(data_dir: Path, period: str,
              *, year_scope: bool = False) -> list[dict]:
    """Files carrying `period`, resolved across the WHOLE tree.

    Thin wrapper over boveda_source. The vault tree is the canonical source, so
    a month bundle is not a prerequisite for finding the month's evidence: the
    period's PILA in payroll/, its exception register in a staged intake bundle
    and an annual PMS export all resolve. On a flat dir (the --mock corpus, a
    legacy boveda_seed) the result is exactly what the old rglob produced.
    """
    return boveda_source.scan_period_files(data_dir, period,
                                           year_scope=year_scope)


def _canonical_rows(db_path: Path, period: str) -> tuple[list[dict], list[dict]]:
    """canonical_documents rows for the period, split into (live, stale).

    LIVE  = the row is registered AND the file still exists on disk.
    STALE = the row is registered but its path is gone (deleted mock dirs,
            moved bundles, a cleaned temp volume).

    A registered-but-absent file must NEVER satisfy the gate: counting it as
    present is the same error class as counting a provisional file — the
    evidence does not exist. Stale rows are reported instead of trusted, so a
    derived index can never quietly green a close. (Skip on any DB problem —
    the filesystem scan still runs.)"""
    if not Path(db_path).exists():
        return [], []
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            rows = [dict(r) for r in conn.execute(
                "SELECT doc_id, filename, path, vendor, doc_type, period "
                "FROM canonical_documents WHERE period = ?",
                (period,),
            ).fetchall()]
        finally:
            conn.close()
    except sqlite3.Error:
        return [], []
    live, stale = [], []
    for r in rows:
        (live if r.get("path") and Path(r["path"]).exists() else stale).append(r)
    return live, stale


def _sources_config(entity: str, db_path: Path) -> dict:
    """Per-entity applicable-sources config (company_rules/gate_sources).
    Empty dict == not configured, which means STRICT LEGACY behaviour (every
    item applicable, default patterns) — an unconfigured client must never be
    loosened by accident."""
    try:
        from gate_sources_seed import load_gate_sources

        return load_gate_sources(entity, db_path)
    except Exception as exc:  # a config read must never block a close
        print(f"warning: gate_sources config unavailable ({exc}); "
              "strict legacy gate", file=sys.stderr)
        return {}


def check_data_availability(entity: str, period: str,
                            data_dir: Path, db_path: Path = DB_PATH,
                            sources_config: Optional[dict] = None) -> dict:
    """Phase 1 gate — config-aware.

    Every item carries its evidence AND its applicability. The per-entity
    config (company_rules, category='gate_sources') can say, per item:
      * not applicable   -> reported ⊘ with its basis; never counted missing;
      * narrowed signals -> file_pats/doc_types overridden for this entity
        (kills the false pass where FareHarbor's generic bookings report
        satisfied "Booking.com");
      * period_scope 'year' -> the signal is a running export, so match the
        year rather than the month (RESERVAS 2026.xlsx);
      * provisional      -> the file is present but is NOT this period's data
        (the June-duplicate OTA reports). It does NOT satisfy the gate: it
        blocks with its own reason, because posting June revenue as July is
        exactly the error this gate exists to stop.

    The scan is tree-aware (boveda_source), so evidence outside the month
    folder is FOUND instead of reported missing. Unconfigured entity -> strict
    legacy. Missing applicable item -> gate fails.
    """
    cfg = sources_config if sources_config is not None else _sources_config(entity, db_path)
    docs, stale_docs = _canonical_rows(db_path, period)
    checks = []
    missing: list[str] = []
    not_applicable: list[dict] = []
    provisional: list[dict] = []
    scanned: dict[str, list[dict]] = {}

    def files_for(scope: str) -> list[dict]:
        if scope not in scanned:
            scanned[scope] = _scan_dir(data_dir, period,
                                       year_scope=(scope == "year"))
        return scanned[scope]

    for item in GATE_ITEMS:
        key = item["key"]
        item_cfg = cfg.get(key) or {}
        applicable = bool(item_cfg.get("applicable", True))
        scope = item_cfg.get("period_scope", "period")
        file_pats = item_cfg.get("file_pats")
        if file_pats is None:
            file_pats = item.get("file_pats", [])
        doc_types = item_cfg.get("doc_types")
        if doc_types is None:
            doc_types = item.get("doc_types", [])
        basis = item_cfg.get("basis_en") or item_cfg.get("basis_es") or ""
        is_provisional = bool(item_cfg.get("provisional"))

        if not applicable:
            checks.append({
                "item": key,
                "label": item["label"],
                "status": "not_applicable",
                "available": True,
                "applicable": False,
                "sources": [],
                "basis": basis,
                "period_scope": scope,
                "provisional": False,
            })
            not_applicable.append({"item": key, "basis": basis})
            continue

        files = files_for(scope)
        file_hits = [
            f for f in files
            if any(p in f["filename"].lower() for p in file_pats)
        ]
        doc_hits = [d for d in docs if d.get("doc_type") in doc_types]
        sources = sorted({f["path"] for f in file_hits} | {d["path"] for d in doc_hits})
        # A provisional item is PRESENT but is not this period's data (e.g. the
        # June-duplicate OTA reports). It must never satisfy the gate.
        ok = bool(sources) and not is_provisional
        checks.append({
            "item": key,
            "label": item["label"],
            # Self-describing status so the JSON report is readable without
            # cross-referencing the top-level lists (ok / provisional /
            # missing / not_applicable).
            "status": ("provisional" if (is_provisional and sources)
                       else "ok" if ok else "missing"),
            "available": ok,
            "applicable": True,
            "sources": sources,
            "basis": basis,
            "period_scope": scope,
            "provisional": is_provisional and bool(sources),
            "found_in": sorted({f.get("kind", "dir") for f in file_hits}),
        })
        if is_provisional and sources:
            provisional.append({
                "item": key,
                "note": ("evidence on disk is NOT this period's data — "
                         "collect the real report before posting"),
                "basis": basis,
            })
        if not ok:
            missing.append(key)
    if missing or provisional:
        bits = []
        if missing:
            bits.append("missing data: " + ", ".join(missing))
        if provisional:
            bits.append("evidence present but NOT this period's data: "
                        + ", ".join(p["item"] for p in provisional))
        verdict = ("GATE FAILED — stop, don't run the motor; "
                   + "; ".join(bits) + ".")
    else:
        verdict = "GATE PASSED — data in hand for the close."
        if not_applicable:
            verdict += (f" {len(not_applicable)} item(s) not applicable to this "
                        "entity (config: company_rules/gate_sources).")
    if stale_docs:
        verdict += (f" ⚠️  {len(stale_docs)} registered document(s) ignored — "
                    "their path no longer exists (stale index rows).")

    return {
        "gate": "data_availability",
        "entity": entity,
        "period": period,
        "data_dir": str(data_dir),
        "provenance": boveda_source.resolve_period_roots(data_dir, period),
        "checks": checks,
        "missing": missing,
        "not_applicable": not_applicable,
        "provisional": provisional,
        "stale_index": stale_docs,
        "gate_passed": not missing and not provisional,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Phase 1.6 — received-document integrity (paged to exhaustion)
# ---------------------------------------------------------------------------
def pull_bills(client: Any, period: str, page_size: int = GATE_PAGE_SIZE) -> list[dict]:
    """`GET /bills` paged to EXHAUSTION (Alegra caps page size at 30).
    Fixes the 2026-09-17 finding #7: never drop bills past the first page.
    Stops when a page returns fewer than `page_size` rows. 5000-row safety
    valve against a pagination loop (a bug must fail loudly, never silently
    truncate)."""
    start_date, end_date = f"{period}-01", f"{period}-31"
    bills: list[dict] = []
    start = 0
    while True:
        page = client.get_bills(start_date=start_date, end_date=end_date,
                                start=start, limit=page_size)
        page = [b for b in (page or []) if isinstance(b, dict)]
        bills.extend(page)
        if len(page) < page_size:
            break
        start += page_size
        if start > 5000:
            raise RuntimeError(
                f"pagination runaway: {start} bills fetched with no short page - "
                "the API is not honouring the page size; refusing to loop forever"
            )
    return bills


def check_received_docs(client: Any, period: str,
                        page_size: int = GATE_PAGE_SIZE) -> dict:
    """Phase 1.6 for one period: pull all registered purchase docs (paged to
    exhaustion), run the File-13 flag set, state the completeness caveat."""
    from cfd_engine import check_received_docs as run_flags

    started = datetime.now(timezone.utc).isoformat()
    bills = pull_bills(client, period, page_size=page_size)
    sweep = run_flags(bills, {"period": period})
    return {
        "gate": "received_docs_integrity",
        "period": period,
        "bills_pulled": len(bills),
        "pages_used": max(1, -(-len(bills) // page_size)) if bills else 1,
        "paged_to_exhaustion": True,
        "started_at": started,
        **sweep,
    }


# ---------------------------------------------------------------------------
# Mock transports — deterministic, no network, and the >30 shape is always
# exercised so the pagination fix is proven on every --mock run
# ---------------------------------------------------------------------------
class _PagedBillsAPI:
    """A fake Alegra /bills that honours start/limit and serves 65 docs —
    three pages of 30, 30, 5. Exactly the shape that broke the old gate."""

    def __init__(self) -> None:
        self.pages_served = 0

    def get_bills(self, **kwargs) -> list[dict]:
        self.pages_served += 1
        start = kwargs.get("start", 0)
        limit = kwargs.get("limit", 30)
        from cfd_engine import mock_bills  # synthetic 65-doc set

        all_bills = mock_bills()
        return all_bills[start:start + limit]


def _mock_data_dir(period: str) -> Path:
    """Synthetic July corpus — bank/payroll/intake present, OTA/PMS absent:
    exactly the honest Tayrona-July shape until the OTA/PMS exports land."""
    tmp = Path(tempfile.gettempdir()) / f"pre_close_gate_mock_{period}"
    if tmp.exists():
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True, exist_ok=True)
    year, month = period.split("-")
    month_abbr = datetime.strptime(period, "%Y-%m").strftime("%b").upper()  # JUL for 07
    files = {
        f"Bold_Transacciones_{period}.md": "# Bold — Transacciones\n**Period:** {period}\n",
        f"78100001780_{month_abbr}{year}.xlsx": b"mock",  # bank statement (same name shape as boveda_seed)
        f"DetallePlanilla_38244858_{period}_E.pdf": b"mock",  # PILA
        f"exception_register_{period}.csv": "ID,Period\nEX-J07-01,{period}\n",
    }
    # keep the dir deterministic: rewrite all four each run
    for name, content in files.items():
        p = tmp / name
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content.format(period=period))
    return tmp


# ---------------------------------------------------------------------------
def format_gate(report: dict) -> str:
    out = [
        "╔══════════════════════════════════════════════════╗",
        "║  PHASE 3 — PRE-CLOSE GATE (Phase 1 + 1.6)         ║",
        "╚══════════════════════════════════════════════════╝",
        "─── Phase 1 · data availability ───",
    ]
    dg = report["data_gate"]
    for c in dg["checks"]:
        if not c.get("applicable", True):
            mark = "⊘"
        elif c.get("provisional"):
            mark = "⏳"
        else:
            mark = "✅" if c["available"] else "❌"
        scope = c.get("period_scope")
        suffix = f"   [scope: {scope}]" if scope and scope != "period" else ""
        out.append(f"  {mark} {c['label']}{suffix}")
        for s in c["sources"]:
            out.append(f"        {s}")
        if not c.get("applicable", True):
            out.append(f"        ⊘ not applicable — {c.get('basis') or 'no basis recorded'}")
        elif c.get("provisional"):
            out.append(f"        ⏳ PROVISIONAL — {c.get('basis') or 'evidence is not this period'}")
    if dg.get("not_applicable"):
        out.append(f"  ⊘ {len(dg['not_applicable'])} item(s) not applicable to this entity "
                   "(config: company_rules/gate_sources)")
    if dg.get("provisional"):
        out.append(f"  ⏳ {len(dg['provisional'])} item(s) PROVISIONAL — present but NOT this "
                   "period's data; collect before posting")
    out.append(f"  → {dg['verdict']}")
    prov = dg.get("provenance") or {}
    if prov.get("roots"):
        out.append(f"  ℹ️  source tree: {prov.get('shape')} · {len(prov['roots'])} "
                   "root(s) resolved at read time, nothing copied")
        for r in prov["roots"]:
            out.append(f"        [{r['kind']}] {r['root']} — {r['reason']}")
        for x in prov.get("excluded", []):
            out.append(f"        (skipped) {x['root']} — {x['reason']}")
    out += ["", "─── Phase 1.6 · received-document integrity ───"]
    d = report["received_docs"]
    if d.get("skipped"):
        out.append(f"  ⚠️  SKIPPED — {d.get('reason')}")
    else:
        out.append(f"  Bills pulled: {d['bills_pulled']} (pages: {d['pages_used']}, paged to exhaustion: {d['paged_to_exhaustion']})")
        out.append(f"  Flagged: {d['flagged_count']}")
        for f in d["flagged"]:
            out.append(f"  🚩 [{f['flag']}] {f['doc_id']}: {f['message']}")
        if d["errors"]:
            out += [f"  💥 [{e['flag']}] {e['doc_id']}: {e['error']}" for e in d["errors"]]
        out.append(f"  ℹ️  {d['completeness_caveat']}")
    return "\n".join(out)


def run_gate(entity: str, period: str, *, mock: bool = False,
             data_dir: Optional[Path] = None,
             db_path: Path = DB_PATH,
             skip_docs: bool = False) -> dict:
    """Run Phase 1 + 1.6 and return the composite report. With --mock the
    data dir is synthetic and the /bills pull hits the paged fake.

    A live run resolves the data dir from the VAULT TREE (boveda_source.
    canonical_root) unless --data-dir overrides it — the tree is the canonical
    source, so no second copy is ever made. --skip-docs runs Phase 1 only (no
    Alegra credentials needed) and the report says so explicitly rather than
    implying the integrity check passed.
    """
    if mock:
        dd = _mock_data_dir(period)
        client = _PagedBillsAPI()
        data_report = check_data_availability(entity, period, dd, db_path)
        docs_report = check_received_docs(client, period)
        docs_report["transport"] = "mock (65-doc paged API; >30 exercised)"
    else:
        if data_dir is not None:
            dd = Path(data_dir)
        else:
            dd = boveda_source.canonical_root(entity)
            if not dd.exists():
                legacy = Path(__file__).parent / "data" / "boveda_tayrona"
                if legacy.exists():
                    dd = legacy
        if not dd.exists():
            raise FileNotFoundError(
                f"data dir not found: {dd} (use --data-dir or --mock)"
            )
        data_report = check_data_availability(entity, period, dd, db_path)
        if skip_docs:
            docs_report = {
                "gate": "received_docs_integrity",
                "period": period,
                "skipped": True,
                "reason": ("--skip-docs: Phase 1.6 not run (needs Alegra "
                           "credentials). Registered purchase docs were NOT "
                           "verified for this period."),
                "flagged": [],
                "flagged_count": 0,
                "errors": [],
            }
        else:
            from alegra_client import AlegraAuthError, AlegraClient

            try:
                client = AlegraClient()
            except AlegraAuthError as exc:
                raise RuntimeError(f"Alegra credentials missing for live /bills: {exc}") from exc
            docs_report = check_received_docs(client, period)
            docs_report["transport"] = "live Alegra API"

    return {
        "phase": "pre_close_gate",
        "entity": entity,
        "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_gate": data_report,
        "received_docs": docs_report,
        "gate_passed": data_report["gate_passed"] and not docs_report["errors"],
        "blockers": [
            *(f"data: missing {m}" for m in data_report["missing"]),
            *(f"data: provisional {p['item']} — {p['note']}"
              for p in data_report.get("provisional", [])),
            *(f"docs: {e['flag']} {e['doc_id']}: {e['error']}" for e in docs_report["errors"]),
        ],
        "notices": [
            *(f"not-applicable: {n['item']} — {n['basis']}"
              for n in data_report.get("not_applicable", [])),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 3 — Pre-Close Gate (Phase 1 + 1.6)")
    parser.add_argument("entity", help="Entity slug")
    parser.add_argument("period", help="Period YYYY-MM")
    parser.add_argument("--mock", action="store_true", help="Synthetic data dir + paged /bills fake")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--data-dir", type=Path,
                        help="Period data dir (default: the vault tree, via boveda_source)")
    parser.add_argument("--skip-docs", action="store_true",
                        help="Phase 1 only — skip the Alegra /bills integrity check (no credentials needed)")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="SQLite path for the derived index")
    args = parser.parse_args()

    try:
        report = run_gate(args.entity, args.period, mock=args.mock,
                          data_dir=args.data_dir, db_path=args.db,
                          skip_docs=args.skip_docs)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print(format_gate(report))

    if args.mock:
        return 0  # informational demo run; the gate verdict is in the report
    return 0 if report["gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())