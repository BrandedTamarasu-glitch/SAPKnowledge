---
module: sd
content_type: integration
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Sales & Distribution — Integration Points

> ECC 6.0 reference. Documents every touchpoint where SD creates FI documents. Covers billing postings (revenue via VKOA), goods issue postings (COGS via OBYC), revenue recognition basics, and period-end SD-FI processes. For VKOA account determination details, see `modules/fi/account-determination.md` (framework) and `modules/sd/sd-advanced.md` (extended examples). For OBYC/COGS details at PGI, see `modules/mm/mm-advanced.md`. For S/4HANA differences, see the S/4HANA Differences section at the end.

---

## 1. SD-FI Integration Point Catalog

Every SD transaction that creates (or explicitly does NOT create) an FI document, with the account determination framework used and key tables updated.

| SD Transaction | Billing/Movement Type | FI Document Created | VKOA/OBYC Keys | Key Tables Updated |
|---------------|----------------------|--------------------|-----------------|--------------------|
| VF01/VF04 (standard invoice) | F2 | Yes | VKOA: ERL (Cr revenue), MWS (Cr tax), Dr Customer | VBRK, VBRP, BKPF, BSEG |
| VF01/VF04 (credit memo) | G2 | Yes | VKOA: ERL (Dr revenue), Cr Customer | VBRK, VBRP, BKPF, BSEG |
| VF01/VF04 (debit memo) | L2 | Yes | VKOA: ERL (Cr revenue), Dr Customer | VBRK, VBRP, BKPF, BSEG |
| VF01 (returns credit) | RE | Yes | VKOA: ERL (Dr revenue), Cr Customer | VBRK, VBRP, BKPF, BSEG |
| VF11 (cancel billing) | S1 | Yes -- reverses original FI doc | Reverse of original | VBRK, VBRP, BKPF, BSEG |
| VF01 (pro forma) | F5/F8 | **No FI posting** | None | VBRK, VBRP only |
| VF01 (invoice list) | LR | Yes | VKOA for invoice list items | VBRK, VBRP, BKPF, BSEG |
| VL02N (PGI -- goods issue) | Mvt type 601 | Yes (via OBYC) | OBYC: GBB/VAX or VAY (Dr COGS), BSX (Cr Inventory) | MKPF, MSEG, LIPS, BKPF, BSEG |
| VL02N (PGI reversal) | Mvt type 602 | Yes -- reverse of 601 | Reverse of GBB/BSX | MKPF, MSEG, LIPS, BKPF, BSEG |
| VL02N (returns GR) | Mvt type 651 | Yes | OBYC: BSX (Dr Inventory), GBB (Cr -- reverses COGS) | MKPF, MSEG, LIPS, BKPF, BSEG |
| VF44/VF45 (rebate settlement) | Rebate credit memo | Yes | VKOA: ERS (Dr, reversing accrual), Cr Customer | VBRK, VBRP, BKPF, BSEG |
| VBO1 (rebate agreement creation) | -- | **No FI posting** | None | KONA (rebate agreement) |
| VBOF (rebate batch settlement) | Multiple rebate CMs | Yes -- multiple FI docs | Same as VF44/VF45 per agreement | Multiple VBRK/BKPF |
| Cash sale (VA01 CS) | F2 (auto) | Yes -- immediate FI doc | VKOA: ERL, MWS; Dr Cash/Bank | VBAK, LIKP, VBRK, BKPF, BSEG |

**Key Notes:**

- **Pro forma billing (F5/F8)** creates VBRK/VBRP records but does NOT create FI documents. Pro forma is for documentation purposes only (quotation confirmation, customs paperwork). It is explicitly excluded from FI posting in VOFA billing type configuration.

- **SD creates FI documents at TWO independent points in the O2C cycle:**
  1. **PGI (VL02N)** -- COGS/inventory posting via **OBYC** (GBB/VAX or VAY for COGS debit, BSX for inventory credit). This is the cost side.
  2. **Billing (VF01/VF04)** -- Revenue/customer/tax posting via **VKOA** (ERL for revenue credit, customer debit from KNB1-AKONT). This is the revenue side.

  These use different account determination frameworks (OBYC vs VKOA) and fire at different process steps. Do not confuse them.

- For full VKOA worked examples, see `modules/sd/sd-advanced.md` Section 1. For OBYC GBB/VAX details, see `modules/mm/mm-advanced.md` Section 1.

---

## 2. Transaction Trace -- "What Happens in FI When I Post VF01?"

This section answers the specific question: "I posted a billing document -- what happened in FI?" It traces the complete flow from billing document creation through FI document creation to customer open item.

**Trigger:** Billing Clerk runs VF01 (single billing document) or VF04 (billing due list) referencing a delivery.

### Step 1: Billing Document Creation (SD Side)

- System creates **VBRK** header: billing document number, billing type (F2 for standard invoice), billing date, payer, net value
- System creates **VBRP** items: material, billing quantity, net value per item, condition amounts from pricing
- Billing type determined by copy control (VTFL: delivery type -> billing type)
- Pricing from the sales order is carried over or redetermined based on VTFL pricing type setting (B = carry over and redetermine, C = copy pricing, D = redetermine from scratch, G = copy and redetermine freight)

### Step 2: Account Determination -- VKOA Lookup (For Each Condition Type with Account Key)

- System reads **KNVV-KTGRD** (customer account assignment group) from the payer's sales area data
- System reads **MVKE-KTGRM** (material account assignment group) from the material's sales org data
- For each active condition type step in the pricing procedure that has an account key:
  - **ERL (revenue):** CoA + Sales Org + KTGRD + KTGRM + ERL -> Revenue GL account
  - **ERS (discounts/deductions):** CoA + Sales Org + KTGRD + KTGRM + ERS -> Deduction GL account
  - **ERF (freight):** CoA + Sales Org + KTGRD + KTGRM + ERF -> Freight revenue GL account
  - **MWS (tax):** Tax code determines tax GL account (tax procedure drives this, VKOA can provide the account)

Cross-reference: The full VKOA determination path (5-level KOFI access sequence) is documented in `modules/fi/account-determination.md` (framework) and `modules/sd/sd-advanced.md` (worked examples with debugging).

### Step 3: FI Document Creation (Automatic)

- System creates **BKPF** header: FI document number, company code, document type RV (billing), posting date = billing date
- System creates **BSEG** line items:
  - **Line 1:** Dr Customer account (reconciliation account from KNB1-AKONT of the payer)
    - Amount: Total billing amount including tax
  - **Line 2:** Cr Revenue GL account (from VKOA ERL determination)
    - Amount: Net revenue
  - **Line 3** (if discounts): Dr or Cr Sales Deduction GL account (from VKOA ERS)
    - Amount: Discount/deduction amount
  - **Line 4** (if freight): Cr Freight Revenue GL account (from VKOA ERF)
    - Amount: Freight charge amount
  - **Line 5:** Cr Output Tax GL account (from tax procedure / VKOA MWS)
    - Amount: Tax amount
- FI document always balances: total debits = total credits
- Billing document number cross-referenced in FI document (BSEG-ZUONR assignment field)
- Company code derived from the sales organization assignment (OVXK: sales org -> company code)

**Credit memo variant (billing type G2):** The same 5-step trace applies but with reversed Dr/Cr for the revenue and customer lines. Revenue is debited (reducing revenue) and customer is credited (reducing the receivable). The VKOA lookup uses the same ERL account key -- the system determines the debit/credit direction from the billing type.

### Step 4: Customer Open Item

- The customer debit (Line 1) creates an **open item** in the AR sub-ledger
- Visible in FBL5N (customer line items)
- Picked up by dunning (F150) when overdue
- Cleared by incoming payment (F-28) or automatic clearing (F.13)
- Due date calculated from payment terms: KNVV-ZTERM (SD payment terms override KNB1-ZTERM if both exist)

### Step 5: Document Flow Update

- **VBFA** (document flow table) updated: links billing document back to delivery and sales order
- Complete document flow now traceable:
  ```
  VA01 (VBAK) -> VL01N (LIKP) -> VL02N PGI (MKPF) -> VF01 (VBRK) -> FI Doc (BKPF)
  ```
- Use VF03 -> Environment -> Document Flow to view the complete chain

---

## 3. Transaction Trace -- "What Happens at PGI (VL02N) -- The COGS Side"

PGI is the other major SD-FI handoff. While billing creates the revenue posting (Section 2), PGI creates the COGS posting. These are independent events that typically occur at different times in the O2C cycle.

**Trigger:** Shipping Clerk clicks "Post Goods Issue" in VL02N. Movement type 601.

### Step 1: Material Document Creation

- **MKPF** header + **MSEG** line items created (same as any MIGO goods movement)
- Delivery status updated in **LIPS** (goods issue status = C)
- Stock quantity reduced in **MARD** (storage location) and **MARC** (plant)

### Step 2: OBYC Account Determination (Not VKOA)

- System reads **MBEW-BKLAS** (valuation class) for the material at the delivering plant
- Transaction keys triggered:
  - **GBB/VAX** (Dr): COGS account -- if no CO account assignment on the sales order
  - **GBB/VAY** (Dr): COGS account -- if CO account assignment exists (WBS element, internal order)
  - **BSX** (Cr): Inventory account

### Step 3: FI Document Creation

- Dr COGS (from OBYC GBB/VAX or VAY + valuation class -> GL account)
  - Amount: At standard price (for S-price materials) or moving average price (for V-price materials)
- Cr Inventory (from OBYC BSX + valuation class -> GL account)
  - Amount: Same as COGS debit -- document balances
- Document type WA (goods issue)
- Material document number and FI document number are cross-referenced (MSEG-BELNR_FI)

**PGI reversal (movement type 602):** Reverses the 601 posting with opposite Dr/Cr signs. Inventory is restocked, COGS is reversed. Used when PGI was posted in error -- accessible via VL02N -> Post Goods Issue -> Reverse.

> **CRITICAL DISTINCTION:** The COGS GL account comes from **OBYC** (GBB modifier VAX/VAY + valuation class), NOT from VKOA. VKOA handles the **revenue** side at billing. OBYC handles the **cost** side at PGI. These are independent account determination mechanisms at different points in the O2C cycle. Do not confuse them.

Cross-reference: For OBYC configuration details (transaction keys, valuation class setup chain, debugging path), see `modules/mm/mm-advanced.md` Section 1.

---

## 4. Revenue Recognition -- Moderate Depth

### Basic Revenue Posting

Standard billing (VF01 with billing type F2) posts revenue immediately via VKOA ERL. Revenue is recognized at billing date. No deferral mechanism -- revenue recognized when billing document is created.

### Deferred Revenue Setup

For scenarios requiring revenue deferral (services rendered over time, subscription billing):

- Configure account key **ERU** (unbilled receivables / deferred revenue) in the pricing procedure
- VKOA maps ERU to a deferred revenue GL account (balance sheet liability)
- At billing: Dr Customer / Cr Deferred Revenue (instead of Cr Revenue)
- Periodic journal entry (manual or automated via FBS1) reclassifies deferred revenue to earned revenue: Dr Deferred Revenue / Cr Revenue
- The reclassification frequency (monthly, quarterly) depends on the revenue recognition policy

### Milestone Billing

- Billing plan type in the sales order defines billing milestones (SPRO -> SD -> Billing -> Billing Plan -> Define Billing Plan Types)
- Each milestone triggers a billing document with a percentage of the total order value
- Revenue posts at each milestone billing event via standard VKOA (ERL)
- Milestone billing uses order-related billing (VTAF copy control, not VTFL)
- Key difference from standard billing: billing is triggered by milestone completion dates in the billing plan, not by delivery

### Billing Plan Types

| Plan Type | Trigger | Billing Reference | Revenue Timing |
|-----------|---------|-------------------|----------------|
| Periodic billing | Defined date intervals (monthly, quarterly) | Order-related (VTAF) | Revenue at each billing date |
| Milestone billing | Milestone completion dates | Order-related (VTAF) | Revenue at each milestone percentage |

- **Periodic billing** (e.g., monthly rental): Regular invoices at defined intervals. Each billing creates a standard FI posting via VKOA. The billing plan in the sales order defines the billing dates and amounts.
- **Milestone billing** (e.g., project milestones): Invoices triggered by milestone completion with percentage allocation. Revenue recognized incrementally at each milestone. Milestone dates and percentages are maintained in the billing plan within the sales order item.

> Note: Complex revenue recognition (percentage-of-completion / POC, multi-element arrangements) defers to Phase 12 (Solution Design Intelligence).

---

## 5. SD Period-End -- FI Impacts

SD period-end activities that create or affect FI postings. These must be coordinated with the FI period-end close sequence.

### 5a. Rebate Settlement (VBO1/VBOF)

- Rebate agreements (VBO1) accrue rebate amounts during normal billing via **RA00** condition type
- RA00 posts at each billing run: Dr Rebate Expense / Cr Rebate Accrual Liability (via VKOA ERS account key)
- Period-end or agreement-end: run **VF44** (partial settlement) or **VF45** (final settlement) or **VBOF** (batch settlement)
- Settlement creates credit memos: Dr Rebate Accrual Liability (reverses provision), Cr Customer (credit memo to customer)
- **Timing:** Run rebate settlement before FI period close to ensure accruals are reversed and credits posted in the correct period

### 5b. Revenue Accruals for Unbilled Deliveries

- At period-end, any deliveries where PGI is posted but billing has not yet run create a COGS/revenue mismatch
- COGS is already posted (at PGI via OBYC), but revenue is not yet recognized (billing via VKOA hasn't happened)
- Manual accrual entry required: Dr Unbilled Receivables / Cr Accrued Revenue
- Reversed in the next period when billing runs
- Identify unbilled deliveries: **VF04** (billing due list) shows deliveries due for billing; also VL06O with goods issue posted status

> **CRITICAL:** The PGI-billing timing gap is a real period-end issue. If PGI posts COGS in period 3 but billing runs in period 4, period 3 has COGS expense with no offsetting revenue. The accrual entry prevents this mismatch in financial reporting.

### 5c. Billing Due List Cleanup (VF04)

- Run VF04 before period-end close to process all deliveries due for billing
- Reduces the unbilled delivery accrual requirement from 5b
- Any remaining unbilled deliveries need manual accrual treatment per 5b

### 5d. Credit Management Review

- Period-end review of credit exposure via **S_ALR_87012218** (credit overview) or FD32/FD33 per customer
- Review and release stale credit blocks: **VKM1** (order blocks), **VKM4** (delivery blocks), **VKM5** (GI blocks)
- Credit limit adjustments via FD32 based on payment behavior and business changes
- No direct FI posting from credit review -- but releasing blocked documents enables future billing -> FI postings

### 5e. Period-End Sequence Summary

Recommended period-end sequence for SD-FI:

| Step | Activity | T-code | Purpose |
|------|----------|--------|---------|
| 1 | Bill all deliveries due for billing | VF04 | Creates revenue + customer open items |
| 2 | Settle rebate agreements | VF44/VF45/VBOF | Creates credit memos, reverses accruals |
| 3 | Post manual revenue accruals for remaining unbilled deliveries | FBS1 | Dr Unbilled Receivables / Cr Accrued Revenue |
| 4 | Review credit blocks and release stale blocks | VKM1/VKM4/VKM5 | Enables future billing -> FI postings |
| 5 | Review and adjust credit limits | FD32 | Adjust based on payment behavior |
| 6 | Ensure FI posting period is open for billing documents | OB52 | Account type S and D must be open |
| 7 | Reverse prior-period revenue accruals | FBS1 auto-reversal | Reversed when billing runs in the new period |

---

## 6. S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact on Integration |
|----------------|----------------|----------------------|
| VBRK/VBRP for billing documents | Same tables in S/4 | No change to billing-FI interface |
| Customer master KNA1/KNB1/KNVV | Business Partner (BUT000) | Billing posts to BP reconciliation account |
| Classic GL or New GL | Universal Journal (ACDOCA) | All SD-FI postings go to ACDOCA |
| MKPF/MSEG at PGI | Single MATDOC table | Same OBYC determination; different source table |
| Material Ledger optional | Material Ledger mandatory | COGS at PGI may use actual cost instead of standard |
| NACE output for billing | BRF+ output management | Billing output format changes; FI posting unchanged |
| FD32 classic credit management | FSCM/UKM credit management | New credit engine; billing-FI posting unchanged |
