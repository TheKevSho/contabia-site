# July 2026 Journal Entry Package — Tayrona Sailing (Sonata Mas SAS)

**Prepared:** 2026-08-26 (live session against Alegra)
**Baseline:** 2026-06-30 locked
**Portal:** sonata-001, dry_run mode

---

## R-11: Depreciation — July 2026

**Status:** ⚠️ TO POST (Edwin has NOT posted July depreciation)

| | Amount |
|---|---|
| Asset register | 43 assets (should be 44 — Anna Leeza missing) |
| Monthly | **COP 1,038,987** |
| Anna Leeza catch-up | COP 250,000/mo × 30 months = COP 7,500,000 (Jan 2024–Jun 2026) |
| Jan+Jun catch-up | COP 2,077,974 (2 months Edwin skipped) |

**JE:**
```
CC-AC-xxx  |  2026-07-31
Dr 5160xx  Depreciación propiedad, planta y equipo          1,038,987
Cr 159215  Depreciación acumulada                             1,038,987
```

**Catch-up (separate entry):**
```
Dr 5160xx  Depreciación PPE (Jan+Jun catch-up)              2,077,974
Dr 5160xx  Depreciación PPE (Anna Leeza Jan24-Jun26)        7,500,000
Cr 159215  Depreciación acumulada                             9,577,974
```

---

## R-14: Interest Accrual — July 2026

**Status:** ⚠️ TO POST (Edwin has NOT posted July interest)

| Loan | Opening 30-Jun | Jul interest | Jul principal |
|---|---|---|---|
| Bancolombia 7810099111 | 83,333,344 | 1,335,748 | 4,166,666 |
| BBVA 9638124968 | 125,000,000 | 2,213,541 | 4,166,667 |
| **Total** | **208,333,344** | **3,549,289** | **8,333,333** |

**JE:**
```
CC-AC-xxx  |  2026-07-31
Dr 5305xx  Gasto financiero — intereses                    3,549,289
Cr 2410    Intereses por pagar                               3,549,289
```

---

## AJ-J07-01: Bold Prepayment Deferral

**Status:** ⚠️ TO POST

| Item | Amount |
|---|---|
| Pablo Alonso — Sonata Aug 11 + DragonLady Aug 14 (50%) | 4,250,000 |
| Camilo Mendoza — Aug 16 charter (50%) | 1,350,000 |
| **Total to defer** | **5,600,000** |

**JE:**
```
CC-AC-xxx  |  2026-07-31
Dr 1110xx  Bold clearing account                            5,600,000
Cr 2805    Ingresos recibidos por anticipado                  5,600,000
```

---

## R-12: FX Revaluation — July 2026

**Status:** ⚠️ NEEDS INPUT — TRM Jul 31 + USD balances

USD exposures:
- TC 0992 deferred purchases: ~$3,548
- PayPal USD balance: ~$0 (Braintree settlements net out)
- No on-book USD loans (both COP-denominated)

---

## ALREADY POSTED BY EDWIN (do NOT double-post)

| Date | ID | Description | Amount |
|---|---|---|---|
| 2026-08-26 | #3974 | Retefuente July (Dr 135595 / Cr Retefuente) | 5,555,000 |
| 2026-08-11 | #3936 | Seguridad social July | 2,164,950 |
| 2026-08-25 | #3971 | Deterioro cartera (RUTA CARIBE VIP write-off) | 1,673,000 |
| 2026-08-25 | #3969-70,72 | Descuentos financieros (3 entries) | 3,756,855 |
| 2026-08-08-11 | #3927,29,38,39 | Ajustes anticipos (4 entries) | 2,212,500 |
| 2026-07-15-21 | #3893-96 | Auto anticipo adjustments (4 entries) | 2,916,000 |

---

## July Revenue Summary (from live Alegra)

- 30 invoices, COP 20,429,086
- 0 open AR (all closed)
- 0 July bills in system
- 5 auto journals (anticipo adjustments): COP 2,916,000
- 10 manual journals (Edwin, Aug): COP 15,362,305

## Motor Rule: Cash ≠ Revenue Until Service Renders

**Standing rule for all channels (Bold, PayPal, bank transfers):**
Every deposit → cross-ref FareHarbor booking date. If voyage date > period close → defer to 2805.
At each subsequent close, reverse 2805 → 4145 revenue for voyages now rendered.

**July reverse check:** Check June 2805 opening balance. Any June prepayments for July voyages → Dr 2805 / Cr 4145 now.