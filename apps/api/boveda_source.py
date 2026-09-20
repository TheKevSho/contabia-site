#!/usr/bin/env python3
"""One canonical source per period — resolve the vault tree, never copy it.

WHY THIS EXISTS
The pre-close gate and every recon phase read a period's evidence from a
"boveda" data dir. In practice a client's evidence is not one flat folder:

    2026-07 Julio/                 <- the month bundle (canonical .md + PDFs)
    bank_statements/               <- topic dir; period files live inside
    payroll/                       <- the July PILA lives here, NOT in the month dir
    _downloads-intake-2026-08-01/  <- staged intake + the exception register
    loans/

Two failure modes followed, both observed on Tayrona July 2026:

  1. COPYING files into one folder to satisfy the reader. The copy becomes a
     second source of truth that drifts from the vault — the "July" OTA .xlsx
     in the July bundle were byte-identical to June's (md5 19b47deb…/6ad4f4d4…)
     and silently passed as July activity.
  2. POINTING the reader at a single dir. Silent misses: the July PILA (in
     payroll/) and the July exception register (in the intake bundle) were
     invisible to a reader scoped to the month folder.

THE RULE: the vault tree IS the canonical source. Resolve it by period at read
time. Nothing is copied; every hit carries the root it came from, so any report
can always say WHERE evidence was found and what was deliberately excluded.

Shapes handled (backward compatible):
  flat_dir       no subdirectories -> one flat corpus (boveda_seed, mock dirs).
                 Byte-for-byte the same results as the old rglob scan.
  month_bundle   '<YYYY-MM> <Month>' dir for the period.
  topic_dir      any other dir holding >=1 file whose path carries the period.
  intake_bundle  a '_'-prefixed staged intake dir holding period files.
  root_files     loose period files sitting directly in the root.
Excluded, with a stated reason: month bundles / bare year dirs for OTHER
periods. Dirs with no period evidence are counted, not listed.

Zero LLM, stdlib only.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Optional

# Spanish month abbreviations — also the prefix of the English names
# ("jul" matches both "julio" and "july"), so one list serves both.
MONTH_NAMES = {
    "01": "ene", "02": "feb", "03": "mar", "04": "abr", "05": "may", "06": "jun",
    "07": "jul", "08": "ago", "09": "sep", "10": "oct", "11": "nov", "12": "dic",
}

_MONTH_BUNDLE_RE = re.compile(r"^\d{4}-\d{2}(?!\d)")
_YEAR_DIR_RE = re.compile(r"^\d{4}$")

DEFAULT_VAULT_ROOT = Path.home() / "vaults" / "_Brain"

# Entity slug -> its raw-accounting dir inside the vault. Both Sonata ids
# ('sonata-001' portal, 'tayrona' CLI) are the same entity and the same books
# — mirroring account_map_seed, which seeds both from one committed source.
ENTITY_VAULT_DIRS = {
    "tayrona": "tayrona-sailing/raw-accounting",
    "sonata-001": "tayrona-sailing/raw-accounting",
    "cantamar": "cantamar/raw-accounting",
}

ROOT_ORDER = {
    "month_bundle": 0,
    "topic_dir": 1,
    "intake_bundle": 2,
    "root_files": 3,
    "flat_dir": 4,
}


# ---------------------------------------------------------------------------
# period / name matching
# ---------------------------------------------------------------------------
def period_tokens(period: str) -> list[str]:
    """Every spelling of a period that can appear in a path.

    '2026-07' -> 202607, 2026-07, 2026_07, 2026/07, 07-2026, 072026,
                 jul, jul26  (matching 'julio', 'july', 'JUL2026', ...)
    """
    yy, mm = period.split("-")
    month = MONTH_NAMES[mm]
    return [
        f"{yy}{mm}", f"{yy}-{mm}", f"{yy}_{mm}", f"{yy}/{mm}",
        f"{mm}-{yy}", f"{mm}{yy}", month, month + yy[-2:],
    ]


def period_in_name(name: str, period: str) -> bool:
    """True when a filename or relative path carries this period."""
    low = str(name).lower()
    return any(t in low for t in period_tokens(period))


def year_in_name(name: str, period: str) -> bool:
    """Year-scoped evidence: any file for the year, regardless of month."""
    return period.split("-")[0] in str(name)


def is_month_bundle(name: str) -> bool:
    """'2026-07 Julio', '2026-06 Junio' — a month bundle dir."""
    return bool(_MONTH_BUNDLE_RE.match(str(name)))


# ---------------------------------------------------------------------------
# root resolution
# ---------------------------------------------------------------------------
def canonical_root(entity: Optional[str] = None) -> Path:
    """The canonical evidence root for an entity.

    Precedence: CONTABIA_DATA_DIR (explicit override) > the vault path for the
    entity slug > <vault>/<entity>/raw-accounting.
    """
    env = os.environ.get("CONTABIA_DATA_DIR")
    if env:
        return Path(env).expanduser()
    vault = Path(os.environ.get("CONTABIA_VAULT_ROOT", DEFAULT_VAULT_ROOT)).expanduser()
    slug = ENTITY_VAULT_DIRS.get((entity or "").strip().lower())
    if slug:
        return vault / slug
    return vault / (entity or "unknown") / "raw-accounting"


def _first_period_hit(d: Path, period: str) -> Optional[str]:
    """Cheapest possible 'does this dir hold period evidence?' — os.walk with
    an early exit on the first hit, so dirs WITH evidence cost almost nothing."""
    for dirpath, dirnames, filenames in os.walk(d):
        dirnames[:] = [x for x in dirnames if not x.startswith(".")]
        for fn in filenames:
            if fn.startswith("."):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, d)
            if period_in_name(fn, period) or period_in_name(rel, period):
                return rel
    return None


def resolve_period_roots(root: Path, period: str) -> dict:
    """Which roots under `root` hold THIS period's evidence, and why.

    Returns {root, period, exists, shape, roots[], excluded[], no_evidence[]}.
    A flat dir (no subdirs) resolves to itself — identical to the legacy scan.
    """
    root = Path(root)
    info: dict[str, Any] = {
        "root": str(root),
        "period": period,
        "exists": root.exists(),
        "shape": "missing",
        "roots": [],
        "excluded": [],
        "no_evidence": [],
    }
    if not root.exists():
        return info

    subdirs = sorted(
        (p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name,
    )
    if not subdirs:
        info["shape"] = "flat_dir"
        info["roots"] = [{
            "root": str(root),
            "kind": "flat_dir",
            "reason": "no subdirectories — single flat corpus",
        }]
        return info

    yy = period.split("-")[0]
    roots: list[dict] = []
    excluded: list[dict] = []
    no_evidence: list[str] = []

    # pass 1 — month bundles for the period, and out-of-scope bundles/years
    deferred: list[Path] = []
    for d in subdirs:
        if is_month_bundle(d.name):
            if period_in_name(d.name, period):
                roots.append({"root": str(d), "kind": "month_bundle",
                              "reason": f"month bundle named for {period}"})
            else:
                excluded.append({"root": str(d),
                                 "reason": f"month bundle for another period (not {period})"})
            continue
        if _YEAR_DIR_RE.match(d.name) and d.name != yy:
            excluded.append({"root": str(d),
                             "reason": f"year dir for another year (not {yy})"})
            continue
        deferred.append(d)

    # pass 2 — topic / intake dirs that actually hold period evidence
    for d in deferred:
        hit = _first_period_hit(d, period)
        if hit:
            kind = "intake_bundle" if d.name.startswith("_") else "topic_dir"
            roots.append({"root": str(d), "kind": kind,
                          "reason": f"holds {period} evidence (e.g. {hit})"})
        else:
            no_evidence.append(d.name)

    # pass 3 — loose period files directly in the root
    if any(period_in_name(p.name, period) for p in root.iterdir() if p.is_file()):
        roots.append({"root": str(root), "kind": "root_files",
                      "reason": f"loose {period} files directly in the root"})

    roots.sort(key=lambda r: (ROOT_ORDER.get(r["kind"], 9), r["root"]))
    info["shape"] = "tree"
    info["roots"] = roots
    info["excluded"] = excluded
    info["no_evidence"] = no_evidence
    return info


# ---------------------------------------------------------------------------
# scanning
# ---------------------------------------------------------------------------
def scan_period_files(root: Path, period: str, *, year_scope: bool = False) -> list[dict]:
    """Every file under `root` that belongs to `period`, with provenance.

    year_scope=False (default): the file's path must carry the period.
    year_scope=True: any file carrying the YEAR — for annual evidence (a PMS
    export, a running register) where the month only exists as rows inside it.

    Each hit: {filename, path, root, kind, rel}. De-duplicated by real path.
    """
    info = resolve_period_roots(root, period)
    out: list[dict] = []
    seen: set[str] = set()
    for r in info["roots"]:
        base = Path(r["root"])
        if r["kind"] == "root_files":
            candidates = sorted(p for p in base.iterdir() if p.is_file())
        else:
            candidates = sorted(p for p in base.rglob("*") if p.is_file())
        for p in candidates:
            if p.name.startswith("."):
                continue
            try:
                rel = str(p.relative_to(base))
            except ValueError:  # pragma: no cover - defensive
                rel = p.name
            ok = year_in_name(rel, period) if year_scope else period_in_name(rel, period)
            if not ok:
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            out.append({"filename": p.name, "path": str(p), "root": r["root"],
                        "kind": r["kind"], "rel": rel})
    return out


def find_period_files(root: Path, period: str, *patterns: str,
                      year_scope: bool = False) -> list[Path]:
    """Period files whose FILENAME matches every pattern (case-insensitive)."""
    pats = [p.lower() for p in patterns if p]
    hits = [
        f for f in scan_period_files(root, period, year_scope=year_scope)
        if all(pat in f["filename"].lower() for pat in pats)
    ]
    return [Path(h["path"]) for h in hits]


def format_provenance(info: dict) -> str:
    """Human-readable provenance block for a report or a memo."""
    if not info.get("exists"):
        return f"data root MISSING: {info['root']}"
    lines = [f"data root: {info['root']}  (shape: {info['shape']})"]
    for r in info.get("roots", []):
        lines.append(f"  + [{r['kind']}] {r['root']}  — {r['reason']}")
    for e in info.get("excluded", []):
        lines.append(f"  - excluded {e['root']}  — {e['reason']}")
    if info.get("no_evidence"):
        lines.append(f"  . scanned, no {info['period']} evidence: "
                     + ", ".join(info["no_evidence"]))
    return "\n".join(lines)
