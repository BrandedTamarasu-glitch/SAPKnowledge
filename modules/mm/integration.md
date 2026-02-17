---
module: mm
content_type: integration
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Materials Management — Integration Points

> ECC 6.0 reference. Documents every touchpoint where MM creates FI documents. Covers goods receipt/issue postings, invoice verification, GR/IR clearing, and period-end MM-FI processes. For OBYC account determination details, see `modules/fi/account-determination.md` (framework) and `modules/mm/mm-advanced.md` (extended examples). For S/4HANA differences, see the S/4HANA Differences section at the end.

---

## 1. MM-FI Integration Point Catalog

Every MM transaction that creates (or does not create) an FI document, with the OBYC transaction keys triggered and key tables updated.

| MM Transaction | Movement Type(s) | FI Document Created | OBYC Keys | Key Tables Updated |
|---------------|------------------|--------------------|-----------|--------------------|
| MIGO (GR against PO) | 101 | Yes | BSX (Dr), WRX (Cr), PRD (S-price) | MKPF, MSEG, EKBE, BSEG, BKPF |
| MIGO (GR reversal) | 102 | Yes — reverse of 101 | BSX, WRX, PRD | MKPF, MSEG, EKBE, BSEG, BKPF |
| MIGO (GI to cost center) | 201 | Yes | GBB/VBR (Dr), BSX (Cr) | MKPF, MSEG, BSEG, BKPF |
| MIGO (GI to production) | 261 | Yes | GBB/VBR (Dr), BSX (Cr) | MKPF, MSEG, BSEG, BKPF |
| MIGO (scrapping) | 551 | Yes | GBB/VNG (Dr), BSX (Cr) | MKPF, MSEG, BSEG, BKPF |
| MIGO (plant transfer) | 301 | Yes | BSX (Dr recv), BSX (Cr issue) | MKPF, MSEG, BSEG, BKPF |
| MIGO (return to vendor) | 122 | Yes — reverse of 101 | BSX, WRX, PRD | MKPF, MSEG, EKBE, BSEG, BKPF |
| MIGO (initial stock load) | 561 | Yes | BSX (Dr), GBB/BSA (Cr) | MKPF, MSEG, BSEG, BKPF |
| MIGO (consignment withdrawal) | 411K | Yes | BSX (Dr), KON (Cr), AKO | MKPF, MSEG, BSEG, BKPF |
| MIGO (GI for delivery) | 601 | Yes | GBB/VAX or VAY (Dr), BSX (Cr) | MKPF, MSEG, LIPS, BSEG, BKPF |
| MIGO (SLoc transfer) | 311 | **No FI posting** | None | MKPF, MSEG only |
| MIGO (to subcontractor) | 541 | **No FI posting** | None | MKPF, MSEG only |
| MIGO (inventory diff — surplus) | 701 | Yes | BSX (Dr), GBB/INV (Cr) | MKPF, MSEG, BSEG, BKPF |
| MIGO (inventory diff — shortage) | 702 | Yes | GBB/INV (Dr), BSX (Cr) | MKPF, MSEG, BSEG, BKPF |
| MIRO (invoice) | — | Yes | WRX (Dr), Vendor (Cr) | RSEG, EKBE, BSEG, BKPF |
| MIRO (credit memo) | — | Yes | Vendor (Dr), WRX (Cr) | RSEG, EKBE, BSEG, BKPF |
| MI07 (physical inventory diff) | 701/702 | Yes | BSX, GBB/INV | MKPF, MSEG, BSEG, BKPF |
| MR21 (price change) | — | Yes | BSX (Dr/Cr), UMB (Cr/Dr) | CKMI1, BSEG, BKPF |
| MR22 (debit/credit) | — | Yes | BSX (Dr/Cr), UMB (Cr/Dr) | CKMI1, BSEG, BKPF |
| MR11 (GR/IR maintenance) | — | Yes | WRX offset | BSEG, BKPF |

**Notes:**

- Storage location transfers (311) and transfers to subcontractor (541) do NOT create FI postings because no valuation change occurs. Movement type 311 moves stock within the same plant/valuation area. Movement type 541 reclassifies stock from unrestricted to subcontracting stock (special stock O) at the same plant — the accounting event occurs later when components are consumed at GR (movement type 543).
- For full Dr/Cr worked examples of each movement type, see `modules/mm/mm-advanced.md` Section 1.

---

## 2. Transaction Trace — "What Happens in FI When I Post MIGO 101?"

This section answers the single most common MM-FI integration question: tracing the complete accounting flow from goods receipt to FI document creation.

**Trigger:** User posts MIGO with Action = Goods Receipt, Reference = Purchase Order, Movement Type = 101.

### Step 1: Material Document Creation (MM Side)

- System creates **MKPF** header record: material document number, posting date, movement type
- System creates **MSEG** line items: material, plant, storage location, quantity, amount
- PO history updated in **EKBE**: GR record linked to PO line item with movement type and quantity
- Stock quantity updated in **MARD** (storage location stock) and **MARC** (plant stock)

### Step 2: Account Determination (OBYC Lookup)

- System reads material master **MBEW**: BKLAS (valuation class) and VPRSV (price control: S or V)
- For each transaction key triggered by movement type 101:
  - **BSX:** Chart of accounts + valuation grouping code + valuation class --> inventory GL account
  - **WRX:** Chart of accounts + valuation grouping code + valuation class --> GR/IR clearing GL account
  - **PRD** (only if S-price AND PO price differs from standard price): Chart of accounts + valuation grouping code + valuation class --> price difference GL account
- Cross-reference: The full determination path (movement type --> OMJJ --> transaction key --> GL) is documented in `modules/fi/account-determination.md`

### Step 3: FI Document Creation (Automatic)

- System creates **BKPF** header: FI document number, company code, posting date (same as material document), document type WE (goods receipt)
- System creates **BSEG** line items:
  - **Line 1:** BSX --> Dr inventory GL account
    - Amount: Standard price (for S-price materials) or PO price (for V-price materials)
  - **Line 2:** WRX --> Cr GR/IR clearing GL account
    - Amount: Always at PO price
  - **Line 3** (if applicable): PRD --> Dr or Cr price difference GL account
    - Amount: PO price minus standard price (only for S-price materials when prices differ)
- FI document always balances: total debits = total credits
- The FI document number is cross-referenced in the material document (MSEG-BELNR_FI)

### Step 4: GR/IR Clearing Account — Open Item Created

- The WRX posting (Step 3, Line 2) creates an **open item** on the GR/IR clearing account
- This open item persists until the vendor invoice is posted via MIRO
- Assignment field on the open item: typically PO number + PO line item (used by F.13 for matching)
- The GR/IR clearing account **MUST** be open-item managed in FS00 (see `modules/fi/fi-advanced.md` Pitfall 7)

### Step 5: CO Posting (If Account-Assigned PO)

- If the PO has an account assignment category (K = cost center, F = order, P = project, A = asset):
  - The goods receipt creates a **CO document** in addition to the FI document
  - The cost object (cost center, internal order, WBS element) receives the actual cost
  - For standard price materials: the CO posting is at standard price (same as BSX amount)
  - For MAP materials: the CO posting is at PO price
- If the PO has NO account assignment (standard stock PO): only the FI document is created, no CO posting at GR time (CO postings occur when stock is consumed via 201/261)

---

## 3. Transaction Trace — "What Happens in FI When I Post MIRO?"

The invoice verification side of the MM-FI integration — from three-way match to vendor open item creation. This trace complements the MIGO 101 trace above: together they show the full lifecycle of a PO-based procurement from GR through payment.

**Trigger:** AP Accountant posts MIRO referencing the Purchase Order.

> **CRITICAL:** Always use MIRO for PO-based invoices, not FB60. FB60 does not reference PO/GR, does not update MM tables (EKBE, RSEG), and breaks MM-FI reconciliation. See `modules/mm/tcodes.md` MIRO entry.

### Step 1: Three-Way Match Validation

- System reads PO terms (price, quantity) from **EKKO/EKPO**
- System reads GR quantity from **EKBE**
- Compares: invoice qty vs GR qty (DQ), invoice price vs PO price (PP), invoice amount (AN/AP)
- If within OMR6 tolerances: posts automatically. If exceeded: blocks for MRBR release.

### Step 2: FI Document Creation

- **BKPF** header: document type RE (invoice receipt), company code, posting date
- **BSEG** line items:
  - **Line 1:** Dr GR/IR clearing account (WRX — offsets the GR posting from MIGO)
  - **Line 2:** Cr Vendor reconciliation account (AP sub-ledger)
  - **Line 3** (if applicable): Dr or Cr PRD for price differences between invoice and PO (S-price materials only)
- For MAP materials: if invoice price differs from GR price, the MAP on the material master is adjusted (if stock exists) or the difference posts to a price difference account (if stock is zero)

### Step 3: GR/IR Clearing — Match Created

- The MIRO Dr posting to GR/IR (Line 1) offsets the MIGO Cr posting from the goods receipt
- Both items now exist on the GR/IR clearing account: one from MIGO (Cr), one from MIRO (Dr)
- F.13 automatic clearing matches these items by PO number + PO line and clears them

### Step 4: Vendor Open Item

- The vendor credit (Line 2) creates an **open item** in the AP sub-ledger
- Visible in FBL1N (vendor line items)
- Picked up by F110 automatic payment program when due date arrives
- Due date calculated from payment terms: vendor master LFB1-ZTERM (or PO-level override)
- Cross-reference: F110 payment run process documented in `modules/fi/processes.md`

---

## 4. GR/IR Clearing — Complete Coverage

The GR/IR clearing account is the bridge between MM goods receipts and FI invoice postings. Proper setup and maintenance are critical for accurate financial reporting.

### Account Setup (Before Go-Live)

The GR/IR clearing account (e.g., 191100) must be configured in **FS00** with:

- **Open Item Management = X** — **CRITICAL**: without this flag, F.13 cannot clear individual items; the account balance grows indefinitely and cannot be analyzed at the line item level. See `modules/fi/fi-advanced.md` Pitfall 7.
- **Line Item Display = X** — Required for MB5S and FBL3N analysis of individual GR/IR items.
- These flags **MUST** be set BEFORE any postings. Changing the open-item indicator after postings exist requires clearing all items first — a complex remediation project.

OBYC transaction key **WRX** must point to this account for each relevant valuation class.

### Period-End Clearing Sequence

**1. F.13 Automatic Clearing** — runs first

- Matches GR and IR postings on the GR/IR account by assignment field (PO number + PO line)
- Clears matched pairs where both quantity and amount match
- Run in test mode first; review results before live execution
- Configuration: **OB74** defines clearing criteria (which fields must match)

**2. MR11 GR/IR Account Maintenance** — handles residuals

- For one-sided items: GR posted but invoice never arrived (or vice versa)
- MR11 writes off the one-sided balance to a configured offset account
- Creates FI documents that clear the hanging open items
- **Best practice:** Only use MR11 when certain no more invoices or GRs will arrive for the PO
- MR11SHOW: review past MR11 postings for audit

**3. Period-end GR/IR analysis**

- Run **MB5S** (GR/IR balance list) to view remaining uncleared items
- Items that are genuinely one-sided (vendor will never invoice, or GR will never post): clear via MR11
- Items that are timing differences (invoice arriving next period): leave open

### Common GR/IR Problems

| Problem | Cause | Resolution |
|---------|-------|------------|
| F.13 cannot clear — balance grows | OI indicator missing on GR/IR account in FS00 | Set Open Item Management flag; requires clearing all existing items first (see `modules/fi/fi-advanced.md` Pitfall 7) |
| Legitimate open items written off prematurely | MR11 used too aggressively at period-end | Review MB5S before MR11; only write off items where no further GR or invoice is expected |
| Items not matched despite matching amounts | F.13 clearing criteria mismatch in OB74 | Check OB74 configuration — assignment field (ZUONR) must match; verify PO number format consistency |
| Small amount differences prevent clearing | GR at PO price, MIRO at different price (rounding, conditions) | Use BD tolerance in OMR6 for auto-posting small differences; or manual clearing for residuals |

---

## 5. MM Period-End — FI Impacts

MM period-end activities that create or affect FI postings. These must be coordinated with FI period controls.

### 5a. MMPV — MM Period Close

- **T-code:** MMPV (program RMMMPERI)
- **What it does:** Opens the new MM posting period and closes the previous period
- **FI impact:** Controls which MM period allows goods movements. **MMPV does NOT control FI posting periods.** The FI posting date on MM-generated FI documents is governed by OB52 (FI posting periods, account type M). These are independent controls.

> **CRITICAL DISTINCTION:** MMPV and OB52 are separate. MMPV opens/closes MM periods (which period MIGO will use). OB52 opens/closes FI posting periods (which period accepts FI documents). You must manage both independently. A common error: opening the new MM period via MMPV but forgetting to open account type M in OB52 — goods movements post in MM but the FI document fails.

- **Configuration:** OMSY stores the current MM period per company code (table MARV)
- **MMRV:** Allows posting to a previously closed MM period (emergency override — use with caution)

### 5b. CKMLCP — Material Ledger Actual Costing Run (If ML Active)

- **T-code:** CKMLCP
- **Prerequisite:** Material Ledger must be active for the plant (optional in ECC 6; mandatory in S/4HANA)
- **What it does:** Calculates actual material costs for the closed period; determines price differences and distributes variance between inventory and COGS
- **FI impact:** Creates FI documents that redistribute variance:
  - Portion consumed (COGS) --> posted to P&L accounts (adjusts cost of goods sold to actual)
  - Portion remaining in inventory --> adjusts balance sheet inventory accounts (revalues closing stock)
- **Sequence requirement:** CKMLCP runs AFTER all goods movements and invoices for the period are posted. The "post closing" step creates entries with posting date in the new period — both the new MM period (MMPV) and new FI period (OB52) must be open.
- **ECC 6 note:** Material Ledger is optional. CKMLCP is only relevant for plants where ML is activated. Detailed ML-specific OBYC keys (LKW, PKD, etc.) are beyond Phase 6 scope.

### 5c. MR21/MR22 — Balance Sheet Revaluation

- **MR21:** Changes the standard price or MAP of a material. Typically used to release a new cost estimate from CO-PC (CK11N --> CK24 --> MR21 marks new price effective).
- **MR22:** Debits or credits a material's value without changing the price. Used for manual value adjustments.
- **FI impact:** Both create FI documents using BSX (stock adjustment) and UMB (revaluation/price change account)
- See `modules/mm/mm-advanced.md` worked example for MR21 Dr/Cr detail

### 5d. Period-End Sequence Summary

Recommended period-end sequence for MM-FI:

| Step | Activity | T-code | Purpose |
|------|----------|--------|---------|
| 1 | Post all remaining goods movements and invoices | MIGO, MIRO | Complete all transactions for the closing period |
| 2 | Run GR/IR automatic clearing | F.13 | Clear matched GR/IR pairs |
| 3 | Run GR/IR maintenance for one-sided items | MR11 | Write off residual unmatched items (if appropriate) |
| 4 | Run price changes if needed | MR21, MR22 | Adjust standard prices or material values |
| 5 | Open the new MM period | MMPV | Allows goods movements in new period |
| 6 | Open the new FI period (account type M) | OB52 | Allows FI documents from MM in new period |
| 7 | Run Material Ledger actual costing (if ML active) | CKMLCP | Redistributes variance; creates postings in new period |
| 8 | Verify GR/IR clearing account status | MB5S | Confirm remaining open items are expected |

---

## 6. S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact on Integration |
|----------------|----------------|----------------------|
| MKPF/MSEG for material documents | Single MATDOC table | Same FI document creation; different source table |
| Material Ledger optional | Material Ledger mandatory | CKMLCP always required at period-end |
| Vendor master (LFA1/LFB1) | Business Partner (BUT000) | MIRO posts to BP reconciliation account |
| Classic GL or New GL | Universal Journal (ACDOCA) | All MM-FI postings go to ACDOCA |
| F.13 for GR/IR clearing | Same F.13 process | No change in clearing logic |
| MMPV period control | Same MMPV process | No change |
