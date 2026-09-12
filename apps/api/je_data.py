"""
Sonata Mas SAS — January 2026 proposed journal entries, structured from
ASIENTOS_PROPUESTOS_CONSOLIDADO_2026-07-06_EN.md (the accountant-facing
consolidated draft-entries doc). Grouped exactly as that document groups them:

  A - ready to post as-is (complete entry, verified)
  B - estimated amount, accountant confirms rate/structure before posting
  C - contingencies to disclose, not book
  D - open + quantified, no entry yet, just needs accountant's judgment call
  E - recurring routines to activate once approved

Nothing in this file has been posted to Alegra. `status` is always
"pending_edwin_approval" until an operator (accountant, via the portal) flips it —
see main.py's PATCH /entities/{id}/journal-entries/{je_id}.
"""

JOURNAL_ENTRIES = [
    {
        "id": "AJ-N1-N2",
        "group": "A_ready_to_post",
        "description": "Reclassify above-normal payroll payments (Kevin/Nicolas)",
        "lines": [
            {"account": "CxC Socios - Kevin", "debit": 7898000, "credit": 0},
            {"account": "CxC Socios - Nicolas", "debit": 3305595, "credit": 0},
            {"account": "Suspense / payroll to classify", "debit": 0, "credit": 11203595},
        ],
        "basis": (
            "Cash paid COP 19,563,595 vs. payroll accrual COP 8,360,000 (verified "
            "against NOMINA ENERO 2026.pdf, exact match). Booked as owner loan (CxC), "
            "not a distribution. Art. 35 not imputed - The accountant documents basis (residual R1)."
        ),
        "linked_exceptions": ["EX-9.2"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "AJ-06",
        "group": "A_ready_to_post",
        "description": "PayPal asset write-down",
        "lines": [
            {"account": "TBD by accountant (correction/expense)", "debit": 3838372, "credit": 0},
            {"account": "PayPal cash", "debit": 0, "credit": 3838372},
        ],
        "basis": (
            "Real USD balance at 31-Jan-2026 = 809.97 (verified two independent ways), "
            "revalued at certified TRM 3,670.47 = COP 2,972,971. Books carried "
            "6,811,343 - gross receipts booked without netting fees/payouts. The "
            "accountant picks the offsetting account."
        ),
        "linked_exceptions": ["EX-6.3", "EX-8.2"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "RECLASS-FAREHARBOR",
        "group": "A_ready_to_post",
        "description": "FareHarbor misposting reclass",
        "lines": [
            {"account": "Bancolombia (111015)", "debit": 838025, "credit": 0},
            {"account": "Efectivo POS Cortesia", "debit": 0, "credit": 838025},
        ],
        "basis": "FareHarbor's contra-entry landed in Efectivo POS Cortesia by mistake.",
        "linked_exceptions": ["EX-8.4"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "RECLASS-1305",
        "group": "A_ready_to_post",
        "description": "1305 polluted by non-customers reclass",
        "lines": [
            {"account": "(destination account per accountant)", "debit": 9251376, "credit": 0},
            {"account": "1305 Clientes", "debit": 0, "credit": 9251376},
        ],
        "basis": (
            "SONATA as its own tercero + Cuantias Menores shouldn't be in 1305. "
            "Already approved to reclass; only exact destination account pending."
        ),
        "linked_exceptions": ["EX-4.6"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "AJ-N3",
        "group": "B_estimated",
        "description": "40% rule (Ley 1393/2010) IBC add-back",
        "lines": [
            {"account": "Employer aportes expense (estimate)", "debit": 307152, "credit": 0},
            {"account": "Aportes payable", "debit": 0, "credit": 307152},
        ],
        "basis": (
            "IBC add-back base COP 1,859,050 (Cristiam/Carlos/Raul/Ovier all exceed "
            "40%). Estimated incremental employer aportes @16.522% ~= 307,152. "
            "Pending: accountant confirms exact PILA rates before posting."
        ),
        "linked_exceptions": ["EX-9.6"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "AJ-03-AJV1",
        "group": "B_estimated",
        "description": "Veronica interest - January already booked/verified; withholding estimate open",
        "lines": [],  # January's 400,000 is already booked (1% x 40,000,000) - no new GL entry.
        "basis": (
            "January's 400,000 interest verified consistent with 1%/mo amortization "
            "table - no restatement needed. Withholding ESTIMATED at 28,000 (7% x "
            "400,000, rendimientos financieros) - The accountant confirms rate/Form 350 code "
            "before posting. From March onward, activate as recurring (R-14)."
        ),
        "linked_exceptions": ["EX-5.6", "EX-12.6"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "AJ-01-02",
        "group": "B_estimated",
        "description": "Retefuente remediation (three overlapping figures - accountant to reconcile)",
        "lines": [],  # Likely a Form 350 correction filing, not a pure GL entry.
        "basis": (
            "EX-5.1 (1,174,647) + EX-5.2 (700,000 est.) + EX-10.1 (1,900,000 aggregate) "
            "may be the same underlying shortfall viewed three ways. Recommendation: "
            "The accountant reconciles into one number before structuring the entry."
        ),
        "linked_exceptions": ["EX-5.1", "EX-5.2", "EX-10.1"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "AJ-07-R11",
        "group": "B_estimated",
        "description": "Depreciation (fixed-asset register drafted, useful lives unconfirmed)",
        "lines": [],  # Not booked until the accountant approves the FA register.
        "basis": (
            "Draft FA register prepared from real Alegra cost data + assumed DIAN "
            "standard useful lives. Estimated monthly depreciation ~1,055,951 "
            "(annual ~12,671,412). Not booked until the accountant approves the register; "
            "once approved, activate as recurring."
        ),
        "linked_exceptions": ["EX-12.2", "EX-14.1"],
        "status": "pending_edwin_approval",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "CONTINGENCY-BONUSES",
        "group": "C_disclosure_only",
        "description": "Salary-constitutive bonuses (no signed pact) - disclose, do not book",
        "lines": [],
        "basis": (
            "Kevin confirmed he will not sign Art. 128 CST pacts for Cristiam/Carlos/"
            "Raul/Ovier. Full bonus is salary-constitutive by default: ~2,850,753/mo, "
            "~34,209,037/yr. Standing rule (decision #15) - contingency until a pact "
            "is signed, not a booked liability. Recommend the accountant document as an "
            "explicit accepted-risk decision (same treatment as RA-2/RA-4)."
        ),
        "linked_exceptions": ["EX-9.4", "EX-11.1"],
        "status": "disclosure_only",
        "period": "2026-01",
        "bucket": "baseline",
    },
    {
        "id": "CONTINGENCY-ART35",
        "group": "C_disclosure_only",
        "description": "Art. 35 presumptive interest - not imputed by company decision",
        "lines": [],
        "basis": (
            "Owner-loan booking (AJ-N1-N2) activates Art. 35 by legal default; "
            "company decision #14 is not to impute it. The accountant documents the basis "
            "at review (residual R1)."
        ),
        "linked_exceptions": ["EX-12.3"],
        "status": "disclosure_only",
        "period": "2026-01",
        "bucket": "baseline",
    },
]

# Group D — open, quantified, no entry yet, just needs accountant's judgment call.
# Not journal entries — surfaced as exceptions with status=open, listed here for
# convenience since the consolidated doc treats them as a distinct bucket.
OPEN_JUDGMENT_CALLS = [
    {"ref": "EX-6.1", "title": "Bancolombia unreconciled net gap", "amount_cop": 1616492,
     "needed": "Line-by-line match (data complete, work pending)"},
    {"ref": "EX-12.8", "title": "BBVA January cuota gap", "amount_cop": 215480,
     "needed": "Accountant's explanation (grace period? correction?)"},
    {"ref": "EX-10.6", "title": "Dormant 135595 balance", "amount_cop": 24641000,
     "needed": "Confirm balance's origin"},
    {"ref": "EX-6.2", "title": "BBVA opening adjustment", "amount_cop": 1210212,
     "needed": "Document origin (predates January)"},
    {"ref": "EX-12.4", "title": "Nicolas's 4 roles / 15M in fleet", "amount_cop": 15000000,
     "needed": "Define nature"},
    {"ref": "EX-4.1/4.7", "title": "AR uncollected / no invoice", "amount_cop": 39655000,
     "needed": "Monitor collection / investigate"},
    {"ref": "EX-10.2", "title": "Foreign-OTA IVA self-retention never applied (Art. 437-2) "
     "- REOPENED 2026-07-10", "amount_cop": 3000000,
     "needed": (
        "Was closed as RA-2 (accepted, no remediation); Kevin reopened it 2026-07-10 "
        "because the economics favor revisiting: this is a real DIAN filing gap (Form 350), "
        "not a bookkeeping entry, so fixing the GL doesn't fix the return. Art. 588 ET allows "
        "voluntary correction of a filed declaracion increasing tax owed any time within "
        "firmeza (~3yrs, Art. 714 ET - not close to binding at 6 months old). Interest accrues "
        "from the original due date either way, but a voluntary correction before DIAN opens "
        "an audit carries only the correction penalty, while DIAN finding it first carries the "
        "much larger sancion por inexactitud. ~3.0M/mo unbooked historically (Jan onward per "
        "the Jun-2026 audit pass) - Accountant's call: file the voluntary correction now, or "
        "reaffirm the RA-2 no-remediation disposition with that penalty delta in view."
     )},
]

# Group E — recurring routines to activate once approved.
RECURRING_ROUTINES = [
    {"id": "R-11", "description": "Depreciation", "status": "July amount ready: COP 1,038,987. FA register approved at 5% vessel life."},
    {"id": "R-12", "description": "FX revaluation",
     "status": "TC 0992 ~USD 3,548 × TRM 3,132.42 = COP 11.1M carrying; compute vs Jun-30 TRM before posting"},
    {"id": "R-14", "description": "Interest accrual",
     "status": "July ready: COP 3,549,289 (Bancolombia 1,335,748 + BBVA 2,213,541)"},
]

# July/August open-period JEs (2026-09-12). Nothing posted. Do not duplicate
# Edwin retefuente / seg-social / deterioro. Do not post R-14 (5305 already in
# payment asientos). Do not post AJ-J07-01 (280505 already at cash).
JOURNAL_ENTRIES += [
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

# Already accepted, no further action — context only, not up for review.
# NOTE: RA-2 (OTA reteIVA) was pulled from this list 2026-07-10 and moved to
# OPEN_JUDGMENT_CALLS as EX-10.2 - Kevin reopened it for a second look rather
# than let it settle as silently accepted. See EX-10.2 above for the framing.
ACCEPTED_NO_ACTION = [
    "RA-1/RA-6 (input IVA, excluded treatment)",
    "RA-4 (Velas Sailing Supply, no DS/self-withholding)",
    "Decision #6 (Abono Kevin -> reduces vessel liability)",
    "Decision #14 (Art. 35 not imputed)",
    "EX-12.1 (vessel, reframe confirmed)",
    "EX-10.4/EX-10.5 (INC, regimen ordinario confirmed)",
]
