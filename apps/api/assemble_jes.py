#!/usr/bin/env python3
"""Phase 8 — JE Assembly + Review Package (Motor-Checklist Phase 8).

Consolidates every proposed JE from phases 4–7 into ONE validated, balanced,
prioritized package the CPA reviews — the join between the motor's per-phase
output and whatever surface posts it (portal, the interim Nick/Sheets review,
or a future SoR adapter). Host- and SoR-agnostic: pure stdlib, no FastAPI, no
network. Emits `review_package.json`.

Validation per JE:
  - debits == credits (±1 COP)                       -> unbalanced = CRITICAL blocker
  - every line has an account and exactly one side   -> malformed line = CRITICAL
  - account resolves in the company_rules account_map -> unmapped/placeholder = HIGH (not postable)
  - JE is backed by an SSOT doc/exception link         -> untraceable = HIGH
  - no duplicate je_id across the batch                -> duplicate = CRITICAL blocker

Priority (review order, most-broken first): CRITICAL > HIGH > MEDIUM > LOW.
A JE is `postable` only when it is balanced, well-formed, account-mapped and
SSOT-backed. `blockers` lists everything that must clear before the close posts.

Usage:
    python3 assemble_jes.py tayrona 2026-07            # runs phases 1-6, assembles
    python3 assemble_jes.py tayrona 2026-07 --mock     # mock mode
    python3 assemble_jes.py tayrona 2026-07 --json     # print package to stdout
    python3 assemble_jes.py tayrona 2026-07 --out review_package.json

To wire into motor_run.py later (after phase 7 exists), add a "phase8" entry
that calls `run_assembly(entity, period, mock)` and prints `format_report`.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(os.environ.get("CONTABIA_DB_PATH", Path(__file__).parent / "sonata_mas_001.sqlite"))
RUN_SHA = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "local")

BALANCE_TOL = 1.0  # COP

PRIORITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


# ---------------------------------------------------------------------------
# account_map — same source of truth as the posting path (company_rules)
# ---------------------------------------------------------------------------
def load_account_map(entity_id: str, db_path: Path = DB_PATH) -> dict[str, str]:
    """Human account name -> SoR account id, from company_rules category
    'account_map'. Stdlib-only mirror of main._account_map so the assembler
    and the poster agree on what 'mapped' means. Missing table/rows -> {}."""
    mapping: dict[str, str] = {}
    if not Path(db_path).exists():
        return mapping
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT rule_text, rule_text_es, rule_text_en FROM company_rules "
                "WHERE entity_id = ? AND category = 'account_map' AND active = 1",
                (entity_id,),
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return mapping
    for r in rows:
        text = (r["rule_text"] or r["rule_text_es"] or r["rule_text_en"] or "").strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                mapping.update({str(k): str(v) for k, v in obj.items()})
                continue
        except (json.JSONDecodeError, ValueError):
            pass
        for line in text.splitlines():
            if "=" in line:
                name, _, aid = line.partition("=")
                if name.strip() and aid.strip():
                    mapping[name.strip()] = aid.strip()
    return mapping


# ---------------------------------------------------------------------------
# Per-JE validation
# ---------------------------------------------------------------------------
def _looks_like_placeholder(account: str) -> bool:
    """A placeholder account string ('1110xx…', 'PENDING:…') — never
    postable, whether it appears as a line account or as a map VALUE. The
    recon phases emit 'xx' stubs on purpose; a map VALUE that is itself a
    placeholder means the map is not resolved, so it does not count as
    'mapped' (fork 2026-09-18-B)."""
    a = str(account).lower()
    return "xx" in a or "pending" in a


def _account_mapped(account: str, acct_map: dict[str, str]) -> bool:
    """A line account is 'mapped' (postable) when it is a map KEY whose VALUE
    resolves to a real SoR account id. A stub key like '1110xx Bold clearing'
    counts as mapped as soon as its map value is a real id. This is the SAME
    predicate the poster's live gate (main._unmapped_accounts) applies, so
    poster and assembler cannot drift on what 'mapped' means."""
    value = acct_map.get(account)
    return value is not None and not _looks_like_placeholder(value)


def _ssot_backed(je: dict) -> bool:
    links = je.get("linked_docs") or je.get("linked_exceptions") or je.get("linked_items") or []
    return bool(links)


def validate_je(je: dict, acct_map: dict[str, str]) -> dict:
    """Return an enriched, validated view of a single JE."""
    lines = je.get("lines", []) or []
    debit_total = round(sum(float(l.get("debit") or 0) for l in lines), 2)
    credit_total = round(sum(float(l.get("credit") or 0) for l in lines), 2)
    balanced = abs(debit_total - credit_total) <= BALANCE_TOL

    issues: list[str] = []

    if not lines:
        issues.append("no lines")
    for i, l in enumerate(lines):
        acct = l.get("account")
        dr = float(l.get("debit") or 0)
        cr = float(l.get("credit") or 0)
        if not acct:
            issues.append(f"line {i}: missing account")
        if (dr > 0) == (cr > 0):  # both sides or neither
            issues.append(f"line {i}: must be exactly one of debit/credit (dr={dr}, cr={cr})")

    if not balanced:
        issues.append(f"unbalanced: Dr {debit_total:,.0f} != Cr {credit_total:,.0f}")

    # account mapping (postability): every line's account must resolve to a
    # REAL SoR id through the map (fork 2026-09-18-B: a stub key is mapped
    # when its VALUE is a real id; a key missing from the map, or mapped to a
    # placeholder value, is not — the poster's _unmapped_accounts agrees)
    unmapped = [
        l.get("account") for l in lines
        if l.get("account") and not _account_mapped(l["account"], acct_map)
    ]
    account_mapped = len(unmapped) == 0 and bool(lines)
    if unmapped:
        issues.append(f"unmapped/placeholder accounts: {sorted(set(map(str, unmapped)))}")

    ssot = _ssot_backed(je)
    if not ssot:
        issues.append("no SSOT doc/exception link (untraceable)")

    malformed = any(x.startswith("line ") or x == "no lines" for x in issues)

    if not balanced or malformed:
        priority = "CRITICAL"
    elif not account_mapped or not ssot:
        priority = "HIGH"
    elif je.get("status") != "approved_by_edwin":
        priority = "MEDIUM"
    else:
        priority = "LOW"

    postable = balanced and not malformed and account_mapped and ssot

    return {
        "je_id": je.get("je_id") or je.get("id"),
        "description": je.get("description", ""),
        "period": je.get("period", ""),
        "bucket": je.get("bucket", ""),
        "status": je.get("status", ""),
        "lines": lines,
        "debit_total": debit_total,
        "credit_total": credit_total,
        "balanced": balanced,
        "account_mapped": account_mapped,
        "ssot_backed": ssot,
        "postable": postable,
        "priority": priority,
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Batch assembly
# ---------------------------------------------------------------------------
def assemble_from_jes(
    jes: list[dict],
    entity: str,
    period: str,
    acct_map: Optional[dict[str, str]] = None,
    *,
    cfd_fired: Optional[list[str]] = None,
    gaps: Optional[list[str]] = None,
) -> dict:
    """Pure assembler: validate + prioritize a list of proposed JEs into one
    review package. No I/O — testable in isolation."""
    acct_map = acct_map or {}
    validated = [validate_je(je, acct_map) for je in jes]

    # Duplicate je_id detection (CRITICAL blocker)
    seen: dict[str, int] = {}
    for v in validated:
        seen[v["je_id"]] = seen.get(v["je_id"], 0) + 1
    dupes = sorted(jid for jid, n in seen.items() if n > 1)
    for v in validated:
        if v["je_id"] in dupes:
            v["issues"].append(f"duplicate je_id '{v['je_id']}'")
            v["priority"] = "CRITICAL"
            v["postable"] = False

    validated.sort(key=lambda v: (PRIORITY_RANK.get(v["priority"], 9), str(v["je_id"])))

    blockers: list[str] = []
    if dupes:
        blockers.append(f"duplicate je_ids: {dupes}")
    for v in validated:
        if not v["balanced"]:
            blockers.append(f"{v['je_id']}: unbalanced (Dr {v['debit_total']:,.0f} / Cr {v['credit_total']:,.0f})")
        if any(x.startswith("line ") or x == "no lines" for x in v["issues"]):
            blockers.append(f"{v['je_id']}: malformed lines")

    summary = {
        "jes": len(validated),
        "postable": sum(1 for v in validated if v["postable"]),
        "balanced": sum(1 for v in validated if v["balanced"]),
        "unbalanced": sum(1 for v in validated if not v["balanced"]),
        "needs_account_map": sum(1 for v in validated if not v["account_mapped"]),
        "untraceable": sum(1 for v in validated if not v["ssot_backed"]),
        "by_priority": {p: sum(1 for v in validated if v["priority"] == p)
                        for p in ("CRITICAL", "HIGH", "MEDIUM", "LOW")},
        "debit_total": round(sum(v["debit_total"] for v in validated), 2),
        "credit_total": round(sum(v["credit_total"] for v in validated), 2),
    }

    return {
        "entity": entity,
        "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_run_sha": RUN_SHA,
        "ready_to_post": len(blockers) == 0 and summary["postable"] == summary["jes"] and summary["jes"] > 0,
        "summary": summary,
        "blockers": blockers,
        "jes": validated,
        "cfd_fired": sorted(set(cfd_fired or [])),
        "gaps": list(gaps or []),
    }


def run_assembly(entity: str, period: str, mock: bool = False) -> dict:
    """Run phases 1–6 via motor_run, then assemble their JEs. motor_run is
    imported lazily so this module stays importable without the phase files
    (e.g. for unit tests of the pure assembler)."""
    from motor_run import run_pipeline  # lazy: pulls the phase modules

    report = run_pipeline(entity, period, mock=mock, stop_at="phase6")
    acct_map = load_account_map(entity)
    return assemble_from_jes(
        report.get("jes_all", []),
        entity, period, acct_map,
        cfd_fired=report.get("cfd_all"),
        gaps=report.get("gaps_all"),
    )


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------
def format_report(pkg: dict) -> str:
    s = pkg["summary"]
    out = [
        "╔══════════════════════════════════════════════════╗",
        "║  PHASE 8 — JE ASSEMBLY + REVIEW PACKAGE           ║",
        f"║  {pkg['entity']} / {pkg['period']}",
        "╚══════════════════════════════════════════════════╝",
        "",
        f"  JEs: {s['jes']}   postable: {s['postable']}   "
        f"unbalanced: {s['unbalanced']}   needs map: {s['needs_account_map']}   "
        f"untraceable: {s['untraceable']}",
        f"  Priority: CRITICAL {s['by_priority']['CRITICAL']}  HIGH {s['by_priority']['HIGH']}  "
        f"MEDIUM {s['by_priority']['MEDIUM']}  LOW {s['by_priority']['LOW']}",
        f"  Totals: Dr {s['debit_total']:,.0f}  Cr {s['credit_total']:,.0f}",
        "",
        "─── JEs (most-broken first) ───",
    ]
    for v in pkg["jes"]:
        mark = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "✅"}.get(v["priority"], "•")
        out.append(f"  {mark} [{v['priority']:8s}] {str(v['je_id']):16s} {v['description'][:44]}")
        for iss in v["issues"]:
            out.append(f"        ⚠️  {iss}")
    out += ["", "─── Blockers (must clear before posting) ───"]
    if pkg["blockers"]:
        out += [f"  ⛔ {b}" for b in pkg["blockers"]]
    else:
        out.append("  ✓ none")
    out += ["", f"  {'✅ READY TO POST' if pkg['ready_to_post'] else '⛔ NOT READY — resolve blockers/HIGHs'}"]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Phase 8 — JE Assembly + Review Package")
    parser.add_argument("entity", help="Entity slug")
    parser.add_argument("period", help="Period YYYY-MM")
    parser.add_argument("--mock", action="store_true", help="Mock mode")
    parser.add_argument("--json", action="store_true", help="Print package JSON to stdout")
    parser.add_argument("--out", help="Write review_package.json to this path")
    args = parser.parse_args()

    pkg = run_assembly(args.entity, args.period, mock=args.mock)

    if args.out:
        Path(args.out).write_text(json.dumps(pkg, indent=2, default=str, ensure_ascii=False))
        print(f"Wrote {args.out} ({pkg['summary']['jes']} JEs, "
              f"{len(pkg['blockers'])} blockers)")
    if args.json:
        print(json.dumps(pkg, indent=2, default=str, ensure_ascii=False))
    elif not args.out:
        print(format_report(pkg))

    return 0 if pkg["ready_to_post"] or pkg["summary"]["jes"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
