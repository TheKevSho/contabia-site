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

# July 2026 live-period JEs (golden month). Nothing posted. Accountant retefuente /
# seg-social / deterioro already in Alegra — do not duplicate those.
JOURNAL_ENTRIES += [
    {
        "id": "R-11-JUL",
        "group": "A_ready_to_post",
        "description": "July 2026 depreciation (43-asset register, excl. Anna Leeza)",
        "lines": [
            {"account": "5160xx Depreciación PPE", "debit": 1038987, "credit": 0},
            {"account": "159215 Depreciación acumulada", "debit": 0, "credit": 1038987},
        ],
        "basis": "Asset register monthly = COP 1,038,987. The accountant posted this exact amount Feb–May; skipped Jan+Jun (catch-up is R-11-CATCHUP) and has not posted July.",
        "linked_exceptions": ["EX-J07-10"],
        "status": "pending_edwin_approval",
        "period": "2026-07",
        "bucket": "live",
    },
    {
        "id": "R-11-CATCHUP",
        "group": "A_ready_to_post",
        "description": "Depreciation catch-up: Jan+Jun skipped (2,077,974) + Anna Leeza 30 months (7,500,000)",
        "lines": [
            {"account": "5160xx Depreciación PPE (Jan+Jun)", "debit": 2077974, "credit": 0},
            {"account": "5160xx Depreciación PPE (Anna Leeza Jan24-Jun26)", "debit": 7500000, "credit": 0},
            {"account": "159215 Depreciación acumulada", "debit": 0, "credit": 9577974},
        ],
        "basis": "The accountant skipped Jan+Jun on the 43-asset register. Anna Leeza (COP 60M, 5% SL = 250k/mo) has never been depreciated; 30 months Jan 2024–Jun 2026 = 7.5M. Going forward add 250k to monthly R-11.",
        "linked_exceptions": ["EX-J07-10", "EX-J07-13"],
        "status": "pending_edwin_approval",
        "period": "2026-07",
        "bucket": "live",
    },
    {
        "id": "R-14-JUL",
        "group": "A_ready_to_post",
        "description": "July 2026 loan interest accrual",
        "lines": [
            {"account": "5305xx Gasto financiero — intereses", "debit": 3549289, "credit": 0},
            {"account": "2410 Intereses por pagar", "debit": 0, "credit": 3549289},
        ],
        "basis": "Bancolombia 7810099111 interest 1,335,748 + BBVA 9638124968 interest 2,213,541. The accountant has not posted July interest.",
        "linked_exceptions": ["EX-J07-10"],
        "status": "pending_edwin_approval",
        "period": "2026-07",
        "bucket": "live",
    },
    {
        "id": "AJ-J07-01",
        "group": "A_ready_to_post",
        "description": "Bold link-pago prepayments deferred to 2805 (voyages after July)",
        "lines": [
            {"account": "1110xx Bold clearing / CxC", "debit": 5600000, "credit": 0},
            {"account": "2805 Ingresos recibidos por anticipado", "debit": 0, "credit": 5600000},
        ],
        "basis": "Pablo Alonso 4,250,000 (Sonata 11 Aug + DragonLady 14 Aug 50%) + Camilo Mendoza 1,350,000 (16 Aug Anna Leeza 50%). Datáfono POS 3,541,500 stays in July revenue.",
        "linked_exceptions": ["EX-J07-12"],
        "status": "pending_edwin_approval",
        "period": "2026-07",
        "bucket": "live",
    },
    {
        "id": "AJ-J06-REVERSE",
        "group": "A_ready_to_post",
        "description": "Recognize June Bold link-pago that rendered in July (2805 reverse)",
        "lines": [
            {"account": "2805 Ingresos recibidos por anticipado", "debit": 3641000, "credit": 0},
            {"account": "4145 Ingresos por servicios", "debit": 0, "credit": 3641000},
        ],
        "basis": "Standing motor rule: every channel, bidirectional. Five June link-pago items totaling COP 3,641,000 whose voyages rendered in July.",
        "linked_exceptions": ["EX-J07-12"],
        "status": "pending_edwin_approval",
        "period": "2026-07",
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
