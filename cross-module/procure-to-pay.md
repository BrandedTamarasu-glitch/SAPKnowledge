---
module: cross-module
content_type: e2e-process
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
related_modules:
  - mm
  - fi
---

# Procure-to-Pay (P2P) — End-to-End Process

> ECC 6.0. Traces the complete procurement cycle from purchase requisition through vendor payment, highlighting every integration handoff where a document crosses module boundaries. For S/4HANA differences, see the S/4HANA Differences section below.

## Prerequisites

Read these module files for full detail on individual steps:

- `modules/mm/processes.md` -- P2P 7-step narrative with three-way match logic, tolerance keys, and role assignments
- `modules/mm/integration.md` -- MIGO 101 posting trace (5-step account determination), MIRO posting trace (4-step), GR/IR clearing (F.13/MR11)
- `modules/fi/processes.md` -- AP Payment Run (F110) 7-step sequence
- `modules/mm/mm-advanced.md` -- OBYC account determination walkthrough with worked examples and debugging path

## Document Chain

```
Purchase Req -> Purchase Order -> GR Material Doc -> Invoice (IR) -> FI Invoice Doc -> Payment Doc
  ME51N           ME21N           MIGO (101)        MIRO           (auto)           F110
  [MM]            [MM]            [MM -> FI]        [MM -> FI]     [FI]             [FI]
```

## Process Flow

### Step 1: Purchase Requisition (ME51N)

**Module:** MM
Purchase requisition created with material, quantity, delivery date, and account assignment (cost center, internal order, or WBS element). Account assignment entered here propagates through the entire P2P chain -- wrong assignment here means wrong CO postings at GR and invoice.
See `modules/mm/processes.md` Section 1, Step 1 for full detail.

**Integration handoff:** None -- PR is internal to MM. No FI document created.

---

### Step 2: Purchase Order (ME21N)

**Module:** MM (with CO commitment if active)
Approved PR converted to PO (document type NB). Buyer confirms vendor, price, quantity, and delivery date. PO can also be created via ME59N (automatic conversion requiring source determination).
See `modules/mm/processes.md` Section 1, Steps 2-3 for release strategy and PO creation detail.

**Integration handoff:** If commitment management is active in CO, the PO creates a commitment document in CO (funds reservation against the cost object). This is a CO-only posting -- no FI document at this point.

---

### Step 3: Goods Receipt (MIGO, movement type 101)

**Module:** MM -> FI
Warehouse posts goods receipt in MIGO referencing the PO. Creates material document (MKPF/MSEG) and simultaneously triggers automatic FI document creation via OBYC account determination.

FI posting:
- **Dr BSX** (Inventory) -- stock value at standard price (S) or PO price (V)
- **Cr WRX** (GR/IR Clearing) -- interim account, always at PO price
- **Dr/Cr PRD** (Price Difference) -- only for standard price materials when PO price differs from standard

See `modules/mm/integration.md` Section 2 for the full 5-step MIGO 101 posting trace (material document creation, OBYC lookup, FI document creation, GR/IR open item, CO posting).

**Integration handoff:** This is the first MM-FI boundary crossing. The FI document is created automatically -- no user action in FI. The WRX credit creates an open item on the GR/IR clearing account that persists until MIRO clears it.

---

### Step 4: Invoice Verification (MIRO) -- Three-Way Match

**Module:** MM -> FI
AP Accountant posts vendor invoice in MIRO referencing the PO. System performs three-way match: invoice quantity vs GR quantity (DQ), invoice price vs PO price (PP), invoice amount (AN/AP). If within OMR6 tolerances, posts automatically; if exceeded, blocks for MRBR release.

FI posting:
- **Dr WRX** (GR/IR Clearing -- offsets the GR posting from Step 3)
- **Cr Vendor** (AP sub-ledger, hits reconciliation account in GL)

See `modules/mm/integration.md` Section 3 for the full 4-step MIRO posting trace (three-way match validation, FI document creation, GR/IR match, vendor open item).

**Integration handoff:** This is the second MM-FI boundary crossing. MIRO creates the vendor open item visible in FBL1N. From this point, the open item lives in FI and is picked up by the automatic payment program (F110). The GR/IR clearing account now has both a credit (from MIGO) and a debit (from MIRO) that F.13 can match and clear.

---

### Step 5: Payment Run (F110)

**Module:** FI
Once the vendor open item exists in FBL1N (created by MIRO in Step 4), the automatic payment program picks it up when the due date arrives. F110 creates payment documents and clears vendor open items.
See `modules/fi/processes.md` Section 3 for the full F110 7-step sequence (FBZP config, parameters, proposal, review, payment, DME/print, reconciliation).

**Integration handoff:** None outbound -- payment is FI-internal. The vendor open item transitions from BSIK (open) to BSAK (cleared).

---

### Step 6: Bank Clearing

**Module:** FI
Bank statement reconciliation (FF67 manual or FEBAN electronic) matches the outgoing payment against the bank clearing account. Confirms the payment cleared the bank.
See `modules/fi/processes.md` for bank reconciliation context.

**Integration handoff:** None -- FI-internal bank reconciliation.

---

## Cross-Module Troubleshooting

Common cross-module P2P issues. For module-specific troubleshooting, see `modules/mm/mm-advanced.md` Section 3 and `modules/fi/fi-advanced.md` Troubleshooting.

| Issue | Root Cause | Resolution |
|-------|-----------|------------|
| GR/IR account balance growing -- never clears | GR/IR account missing open-item management flag in FS00, or F.13 not being run | Check FS00 OI indicator; run F.13 in test mode; see `modules/mm/integration.md` Section 4 |
| MIRO blocked -- three-way match tolerance exceeded | Invoice price/qty differs from PO/GR beyond OMR6 limits | Check MRBR blocking reason; verify PO terms (ME23N) and GR qty (MB51); see `modules/mm/mm-advanced.md` Symptom 8 |
| F110 does not pick up vendor invoice | Payment block on item, vendor master block, due date not reached, or missing payment method | Check F110 payment log; verify LFB1 payment method and bank details; see `modules/fi/fi-advanced.md` Symptom 4 |
| MIGO 101 account determination error | Missing OBYC entry for the valuation class + transaction key combination | Check material valuation class (MM03 Accounting 1), run OMWB simulation; see `modules/mm/mm-advanced.md` Symptom 1 |
| GR posted but MIRO says "No GR exists" | GR posted against wrong PO line, or GR-Based IV (LFM1-WEBRE) active and GR references different PO item | Check EKBE PO history; verify PO number + line item match; see `modules/mm/mm-advanced.md` Symptom 9 |

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact on P2P Flow |
|----------------|----------------|-------------------|
| Material documents in MKPF/MSEG | Single MATDOC table | GR creates MATDOC instead of MKPF/MSEG; FI document creation unchanged |
| Vendor master LFA1/LFB1/LFM1 | Business Partner (BP, BUT000) | MIRO posts to BP reconciliation account; vendor maintenance via BP transaction |
| Classic GL or New GL | Universal Journal (ACDOCA) | All P2P FI postings go to ACDOCA; same OBYC determination logic |
| Material Ledger optional | Material Ledger mandatory | CKMLCP always required at period-end; actual cost always available |
| F.13 for GR/IR clearing | Same F.13 process | No change in clearing logic |
| Fiori apps available | Fiori for PO approval, invoice entry | GUI T-codes still work; Fiori provides mobile approval workflows |
