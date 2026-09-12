"""
Sonata Mas SAS — journal entries on the portal.

June 30 2026 lock (owner, 2026-09-12): baseline Jan–June exceptions have written
endings. January draft JEs (AJ-N1-N2, AJ-06, RECLASS-*, AJ-N3, AJ-03, AJ-01-02,
AJ-07-R11) are retired — they must not sit in ready_to_post.

Live pending (open period, not posted): OJ-4, OJ-5, AJ-J07-05.
"""

# Only live, still-to-post entries. Baseline drafts are gone from this list.
JOURNAL_ENTRIES = [
    {
        "id": "OJ-4",
        "group": "A_ready_to_post",
        "description": "Nick June 5105 package catch-up (clone CC-AC-453)",
        "lines": [
            {"account": "510506 Sueldos", "debit": 5000000, "credit": 0},
            {"account": "510548 Bonificaciones", "debit": 3760000, "credit": 0},
            {"account": "510530 Cesantías", "debit": 416667, "credit": 0},
            {"account": "510536 Prima de servicios", "debit": 416667, "credit": 0},
            {"account": "510539 Vacaciones", "debit": 208333, "credit": 0},
            {"account": "510533 Intereses sobre cesantías", "debit": 4167, "credit": 0},
            {"account": "250505 Salarios y prestaciones sociales", "debit": 0, "credit": 8360000},
            {"account": "261005 Cesantias.", "debit": 0, "credit": 416667},
            {"account": "261020 Prima de servicios.", "debit": 0, "credit": 416667},
            {"account": "261015 Vacaciones.", "debit": 0, "credit": 208333},
            {"account": "261010 intereses sobre cesantías.", "debit": 0, "credit": 4167},
            {"account": "237005 Aportes E.P.S", "debit": 0, "credit": 200000},
            {"account": "238030 Aportes a pensión", "debit": 0, "credit": 200000},
        ],
        "basis": (
            "Jan–May and July each book 9,805,834 Dr 5105 for Nicolas Giraldo Camargo "
            "CC 79983085. June = 0. Cash already paid June via 250505. Date 2026-08-31 "
            "(open). Do not restate June. August Nick accrual is EX-A08-01 (Edwin) — not this JE."
        ),
        "linked_exceptions": ["EX-J07-16"],
        "status": "pending_edwin_approval",
        "period": "2026-08",
        "bucket": "live",
    },
    {
        "id": "OJ-5",
        "group": "A_ready_to_post",
        "description": "Office PPE dep Jun+Jul catch-up (clone CC-AC-495 × 2)",
        "lines": [
            {"account": "Depreciación de propiedad, planta y equipo", "debit": 2077974, "credit": 0},
            {"account": "159215 Depre equipo de oficina", "debit": 0, "credit": 2077974},
        ],
        "basis": (
            "Office dep 1,038,987 ran Jan–May and August (CC-AC-437…441, 495). June and July = 0. "
            "Do not add August. Do not add Anna Leeza / fleet (EX-12.2)."
        ),
        "linked_exceptions": ["EX-J07-17"],
        "status": "pending_edwin_approval",
        "period": "2026-08",
        "bucket": "live",
    },
    {
        "id": "AJ-J07-05",
        "group": "A_ready_to_post",
        "description": "Clear Bold FEC8056756 phantom AP (fees already netted)",
        "lines": [
            {"account": "2205 Cuentas por pagar a proveedores", "debit": 163985, "credit": 0},
            {"account": "111020 bold", "debit": 0, "credit": 163985},
        ],
        "basis": (
            "FP-8246 already expensed 158,257 + IVA 5,728. Bold nets fees (Jul merchant "
            "deduction 577,735.85). No 163,985 on Jul Bancolombia. Do not pay cash."
        ),
        "linked_exceptions": ["EX-J07-05"],
        "status": "pending_edwin_approval",
        "period": "2026-08",
        "bucket": "live",
    },
]

# Retired January drafts — lock endings, not on the queue.
OPEN_JUDGMENT_CALLS = []

RECURRING_ROUTINES = [
    {
        "id": "R-11",
        "description": "Depreciation",
        "status": "Office monthly 1,038,987 runs (Aug posted). Jun+Jul catch-up = OJ-5. Fleet dep = EX-12.2, not a June queue item.",
    },
    {
        "id": "R-12",
        "description": "FX revaluation",
        "status": "July-forward. Not a June lock hole. No standalone JE this pack.",
    },
    {
        "id": "R-14",
        "description": "Interest accrual",
        "status": "5305 already inside payment asientos. Do not post a standalone 3,549,289.",
    },
]

ACCEPTED_NO_ACTION = [
    "June 30 lock 2026-09-12: 43/43 written endings. Baseline JEs retired.",
    "AJ-N1-N2 retired — EX-9.2 / 12.4 book-net.",
    "AJ-06 / EX-6.3 PayPal closed in books.",
    "RECLASS-FAREHARBOR / EX-8.4 July-forward, off June queue.",
    "RECLASS-1305 / OJ-1 still to post in open period — exception EX-4.6 disposed ending 2.",
    "AJ-N3 / AJ-01-02 / AJ-03-AJV1 retired — disclose-forward or moot.",
    "AJ-07-R11 superseded by OJ-5 (office) + EX-12.2 (fleet).",
    "EX-10.2 ending 3 — accepted Art. 437-2 residual. No AJ-08.",
    "RA-1/RA-6, RA-4, Decision #6, Decision #14, EX-12.1, EX-10.4/10.5.",
]
