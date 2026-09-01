# Bold — Transacciones Julio 2026

**Source:** `Reporte_mensual_de_transacciones_2026-07.xlsx` (WhatsApp, received 2026-08-24)
**Filed:** `tayrona-sailing/raw-accounting/2026-07 Julio/Bold_Transacciones_2026-07.xlsx`
**Entity:** Tayrona Sailing (Sonata Mas S.A.S.) · Merchant `OZHEDYEVUL` · Datáfono D202083

## Summary

| Metric | Value |
|---|---|
| Transactions | 13 |
| Period | 2026-07-01 → 2026-07-30 |
| **Valor total (gross sales)** | **COP 9,491,500.00** |
| Bold fees + retentions deducted | COP 577,735.85 |
| **Deposited to sales balance** | **COP 8,913,764.15** |

## By channel

- **Datáfono:** 11 transactions — COP 3,541,500 gross
- **Link de pago:** 2 transactions — COP 5,600,000 gross
  - LNK_V6FTUQPMVB 2026-07-23 — COP 4,250,000, EUR 1,224.26 @ DCC 3,471.47, *"50% privado Sonata 11 agosto y DragonLady 14 agosto"* (Pablo Alonso / ambarviajes) — prepayment for private charter
  - LNK_LYZL6BAZR1 2026-07-30 — COP 1,350,000, *"50% Agosto 16 Anna lezah Camilo MEndoza"* (Camilo Mendoza, cédula 79941044) — prepayment

## Tax retention detail (see Bold worked)

- Retención de fuente declared on all datáfono/link sales (rate varies)
- Full breakdown in source workbook, `Consolidado` sheet

## Two customer prepayments — booked as liability, not July revenue

The two **link de pago** transactions are prepayments for voyages rendered **after** July close. Under accrual accounting these are **not** July revenue — they are customer deposits (liability) until the voyage occurs. **Recorded as proposed JE `AJ-J07-01`:**

| Date | Payer / voyage | Gross (COP) | Dr | Cr |
|---|---|---|---|---|
| 2026-07-23 | Pablo Alonso — Sonata 11 Aug + DragonLady 14 Aug (50% advance) | 4,250,000 | Bold clearing / Ctas x cobrar | **2805 Ingresos recibidos por anticipado** |
| 2026-07-30 | Camilo Mendoza — Aug 16 charter (50% advance) | 1,350,000 | Bold clearing / Ctas x cobrar | **2805 Ingresos recibidos por anticipado** |
| **Total deferred** | | **5,600,000** | | |

- **Recognition:** when each voyage is rendered (Aug/Sep 2026), reverse `2805` and credit the service-revenue account for that month — the cash will already have settled from Bold's sales balance to bank.
- **Datáfono transactions (11, COP 3,541,500)** are point-of-sale — service rendered at time of sale (docked tours), so booked to revenue in July. No deferral.
- Bold commission + retefuente on the link items: fee recognized when the underlying sale earns (i.e., net of the deferred amount), consistent with EX-J07-05's fee-netting treatment.