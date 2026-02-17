# Phase 4: FI Advanced & Integration Prep — Research

**Researched:** 2026-02-16
**Domain:** SAP ECC 6.0 Financial Accounting — Account Determination, Decision Trees, Troubleshooting
**Confidence:** MEDIUM (web sources cross-verified; no SAP system access to confirm exact OMJJ/OBYC table entries)

---

## Summary

This phase layers three content types on top of Phase 3's FI foundation: (1) account determination logic with full path tracing and worked examples, (2) seven configuration decision trees, and (3) a dual-section troubleshooting guide. The research verified factual accuracy of the locked decisions — the OBYC transaction keys and account modifiers, VKOA access sequence structure, cash discount GL account configuration, and the four priority troubleshooting areas.

The core account determination story is well-confirmed: MM automatic postings flow through OBYC using transaction keys (BSX, WRX, GBB, PRD) combined with valuation class and — for GBB — an account modifier (VBR, VNG, VAX, AUF, etc.). SD revenue flows through VKOA using condition technique (KOFI/KOFK). FI-only postings use separate T-codes (OBA1 for FX, OBXU/OBXI for cash discount).

Two corrections to the planned content are flagged: (a) cash discount GL accounts are NOT in OBB8 — they use OBXU/OBXI/OBXV; (b) the CONTEXT.md referred to "ZDI/SKT" as OBYC/account determination keys for cash discounts, but these are SD pricing condition types, not OBYC keys. The correct FI-side cash discount account determination uses transaction keys SKE (cash discount expense), SKT (cash discount received), and their OBXU/OBXI configuration.

**Primary recommendation:** The CONTEXT.md decisions are factually sound with two corrections needed (cash discount config uses OBXU/OBXI, not OBB8; ZDI is an SD discount condition, not an OBYC key). All other locked decisions are verified as correct for ECC 6.0.

---

## Section 1: OBYC Account Determination — Verified Facts

### 1.1 Transaction Keys and Account Modifiers

#### Which keys have account modifiers

Only THREE transaction event keys support account modifiers in standard SAP:
- **GBB** — offsetting entries for inventory postings (has account modifier)
- **PRD** — price differences (has account modifier)
- **KON** — consignment payables (has account modifier)

**BSX and WRX do NOT use account modifiers.** They determine GL account from valuation class alone.

Confidence: MEDIUM (confirmed by SAP Community consensus, multiple sources)

#### Full determination path

```
Movement type (MIGO)
  → OMJJ lookup: which transaction key fires for this movement type
  → OBYC: Transaction key + Valuation class + Account modifier (if applicable)
  → GL account
```

The valuation class comes from the material master (MM60/MM02, field BKLAS). Plant-level.

#### Movement type 101 — Goods Receipt against PO

| Transaction Key | Dr/Cr | What it posts | Account Modifier |
|----------------|-------|---------------|-----------------|
| BSX | Dr | Inventory / stock account | None (valuation class only) |
| WRX | Cr | GR/IR clearing account | None (valuation class only) |
| PRD | Dr or Cr | Price difference (standard price only) | Optional modifier |
| FRN | Dr | Freight/customs clearing (if freight PO condition) | — |

**PRD fires for movement type 101 ONLY when the material has standard price control (price indicator = S in material master).** If price indicator = V (moving average), no PRD posting — the price difference is absorbed into the stock account (BSX). The PRD amount equals: (PO price - standard price) × quantity.

#### Movement type 102 — GR reversal

Same transaction keys as 101 (BSX, WRX, PRD), but postings are reversed (opposite Dr/Cr signs). The system posts the exact reversal of the 101 document.

#### Movement type 261 — Goods Issue to Production Order

| Transaction Key | Dr/Cr | What it posts | Account Modifier |
|----------------|-------|---------------|-----------------|
| BSX | Cr | Stock account (inventory reduced) | None |
| GBB | Dr | Consumption / expense account | **VBR** (internal goods issue / cost center consumption) |

**GBB/VBR** is the modifier for internal goods issues including goods issues to production orders (261), cost center consumption, and general internal usage.

#### Movement type 262 — GI reversal (reversal of 261)

Same keys as 261 (BSX, GBB/VBR), postings reversed.

#### Movement type 551 — Scrapping / Write-off

| Transaction Key | Dr/Cr | What it posts | Account Modifier |
|----------------|-------|---------------|-----------------|
| BSX | Cr | Stock account (inventory reduced) | None |
| GBB | Dr | Scrapping / loss account | **VNG** (scrapping/destruction) |

**GBB/VNG** is the correct modifier for scrapping. Confirmed.

### 1.2 Complete GBB Account Modifier Reference

The full list of standard GBB account modifiers (confirmed from SAP Community):

| Modifier | Purpose | Typical Movement Types |
|----------|---------|----------------------|
| AUA | Order settlement | — |
| AUF | GR for orders without account assignment; settlement if AUA not maintained | 101 for internal orders |
| AUI | Subsequent actual price adjustment from cost center to material | — |
| BSA | Initial stock balance entry | 561 (initial entry of stock) |
| INV | Expenditure/income from inventory differences | 701/702 (inventory count) |
| VAX | GI for sales orders WITHOUT account assignment object (COGS, not a CO cost element) | 601 |
| VAY | GI for sales orders WITH account assignment object (CO cost element) | 601 with WBS/order |
| VBO | Consumption from vendor-managed stock (consignment) | 201/202 |
| VBR | Internal goods issues (cost center, production order consumption) | 201, 261 |
| VKA | Sales order account assignment | — |
| VKP | Project/WBS account assignment | — |
| VNG | Scrapping/destruction | 551, 552 |
| VQP | Sample withdrawal without account assignment | — |
| VQY | Sample withdrawal with account assignment | — |
| ZOB | GR without purchase order | 501 |
| ZOF | GR without production order | — |

**Important distinction — VAX vs VBR for SD/COGS:**
- Movement type 601 (GI for delivery) posts GBB/**VAX** when there is no CO account assignment object on the sales order. This is the standard COGS posting for make-to-stock scenarios.
- GBB/**VBR** is for internal consumption (cost center goods issues, production order material staging via 261).

The CONTEXT.md lists "GBB with account modifier VAX for COGS" for MM goods issue scenario 2 — this is partially correct. VAX is for GI against a sales order (SD-driven). For MM-only goods issues to cost centers (movement 201) or production orders (movement 261), the modifier is VBR. The content plan should clarify that GBB/VAX is specifically the SD billing COGS path (movement 601), while GBB/VBR covers MM internal consumption.

### 1.3 PRD — When It Posts

| Price Control | PRD Behavior |
|--------------|-------------|
| S (Standard Price) | PRD **always fires** when PO price ≠ standard price; also at GR if MAP stock and standard price differ |
| V (Moving Average Price) | PRD **does NOT post** — price difference absorbed into BSX (stock account) directly |

PRD can also have account modifiers: PRD without modifier = standard price difference at GR; other modifiers exist for invoice receipt differences.

---

## Section 2: VKOA Framework — Verified Facts

### 2.1 KOFI vs. KOFK

| Condition Type | Purpose | When Active |
|---------------|---------|-------------|
| KOFI | FI account determination — posts to revenue GL accounts | Always used for standard billing |
| KOFK | CO account determination — posts to CO profitability objects | Used when CO-PA (Profitability Analysis) is integrated with SD billing |

Both are condition types in the account determination procedure KOFI00. KOFK is the CO-integrated variant; if COPA is active and CO objects need to receive the posting, KOFK fires. In a standard ECC 6.0 implementation without active COPA integration, only KOFI is relevant.

**CONTEXT.md scope is correct:** Phase 4 establishes the VKOA framework using KOFI. KOFK is CO integration — deferred to Phase 10.

### 2.2 VKOA Access Sequence — KOFI00

The KOFI00 access sequence uses five condition tables searched in this order (most specific to most general):

| Access Level | Fields | Meaning |
|-------------|--------|---------|
| 1 | Chart of Accounts + Sales Org + Cust AAG + Mat AAG + Account Key | Most specific |
| 2 | Chart of Accounts + Sales Org + Cust AAG + Account Key | No material group |
| 3 | Chart of Accounts + Sales Org + Mat AAG + Account Key | No customer group |
| 4 | Chart of Accounts + Cust AAG + Mat AAG + Account Key | No sales org |
| 5 | Chart of Accounts + Account Key | Catch-all / fallback |

The system searches access levels 1 → 5 and uses the first match found.

**Field sources:**
- **Chart of accounts** — from company code configuration
- **Sales organization** — from the billing document header
- **Customer Account Assignment Group (KTGRD)** — from KNVV (customer master, sales area data, Billing Documents tab, "Acct assgt grp" field). Classifies customers as domestic revenue, export revenue, intercompany, etc.
- **Material Account Assignment Group** — from the material master, Sales Org 2 view (field MVGR5 in some documents, but the actual material master field used is "Acct assmt grp material" — displayed in MM60/MM02). Classifies materials as finished goods, services, trading goods, etc.
- **Account Key** — from the pricing procedure condition type (e.g., ERL = revenue, ERS = sales deduction/discount, ERF = freight revenue, MWS = sales tax). Maintained in pricing procedure via transaction V/08.

### 2.3 Account Keys (KTOSL) in Pricing Procedure

Account keys are assigned to condition types in the pricing procedure (V/08):

| Account Key | Standard Use |
|-------------|-------------|
| ERL | Revenue (main revenue condition, typically PR00) |
| ERS | Sales deductions / discounts |
| ERF | Freight revenue / surcharges |
| MWS | Tax (output tax) |
| ERL | Also used for manually-entered price conditions |

Account keys link the pricing procedure to VKOA — the same account key value appears in both places.

### 2.4 VKOA Configuration Path

**T-code:** VKOA
**IMG Path:** Sales and Distribution → Basic Functions → Account Assignment / Costing → Revenue Account Determination → Assign G/L Accounts (VKOA)

Diagnostic path (reading existing config): VKOA → select condition type KOFI → view all five access tables → check what GL account is assigned for a given combination.

---

## Section 3: FI-Only Automatic Postings — Verified Facts

### 3.1 Cash Discount GL Account Configuration

**CORRECTION FROM CONTEXT.MD:** Cash discount GL accounts are NOT configured in OBB8. OBB8 defines payment terms (days, percentages) — the percentage thresholds that trigger a discount. The actual GL account assignment for cash discounts uses separate T-codes.

| T-code | What It Configures |
|--------|-------------------|
| OBXU | GL account for cash discount received (AP — vendor gives discount) |
| OBXI | GL account for cash discount paid (AR — company gives discount to customer) |
| OBXV | Also referenced for "cash discount taken" in some configurations |

These T-codes assign GL accounts using transaction keys (account determination keys), not the OBB8 payment terms definition.

**Configuration path for OBXU:**
SPRO → Financial Accounting (New) → Accounts Receivable and Accounts Payable → Business Transactions → Outgoing Payments → Outgoing Payment Global Settings → Define Accounts for Cash Discount Taken

The GL account entry in OBXU/OBXI is keyed by chart of accounts only (no valuation class or other modifier) — one GL account per chart of accounts for cash discount received, one for cash discount paid.

**CONTEXT.MD reference to "ZDI/SKT":** These appear to be SD pricing condition types (ZDI = a custom discount condition; SKT = cash discount in SD), not OBYC transaction keys for FI cash discount posting. The FI-side cash discount account determination uses transaction keys maintained in OBXU/OBXI directly. This section of the content plan should be revised to reference OBXU/OBXI rather than "ZDI/SKT OBYC keys."

Confidence: MEDIUM (confirmed by multiple SAP Community sources and tutorialkart.com)

### 3.2 FX Valuation (F.05) — GL Account Configuration

**T-code for configuration:** OBA1

OBA1 configures GL accounts for foreign currency valuation automatic postings. Two primary transaction keys:

| Key | What It Covers | GL Accounts Configured |
|-----|---------------|----------------------|
| KDB | Non-open-item-managed GL accounts (balance sheet FX accounts) | FX gain GL, FX loss GL — linked via exchange rate difference key in GL master |
| KDF | Open items — vendor/customer open items AND open-item GL accounts | Realized gain, realized loss, unrealized gain, unrealized loss, balance sheet adjustment GL |

**How KDB works:** The GL account master record (FS00) has a field "Exchange rate difference key" (on the Control Data tab). This key links the GL account to the OBA1/KDB configuration, which then specifies which FX gain/loss accounts receive the valuation postings.

**How KDF works:** Under KDF, you enter the reconciliation account (e.g., vendor reconciliation GL 160000) and then assign the corresponding gain/loss accounts for that reconciliation account grouping.

**F.05 uses OBA1:** When F.05 runs, it reads the OBA1 configuration to determine where to post valuation adjustments. F.05 creates reversible postings (auto-reversal on the first day of the next period).

**IMG Path for OBA1:**
SPRO → Financial Accounting (New) → General Ledger Accounting (New) → Periodic Processing → Valuate → Define Accounts for Foreign Currency Valuation

Confidence: MEDIUM (confirmed by sap96.com post, SAP Community, multiple sources agree on KDB/KDF keys)

---

## Section 4: Decision Tree Factual Verification

### 4.1 Parallel Accounting — Three Approaches in ECC 6.0

The three approaches in ECC 6.0 New GL (CONTEXT.md scenario 1) are correct. Clarifying details:

**Approach 1: Leading ledger only (0L)**
- Single leading ledger (0L) follows one accounting principle (e.g., IFRS)
- Local GAAP differences handled as manual adjustments outside SAP or in non-SAP tools
- Simplest; no parallel ledger config required
- Use when: differences between IFRS and local GAAP are immaterial or handled externally

**Approach 2: Leading ledger + non-leading ledger(s)**
- Leading ledger 0L = primary accounting principle (IFRS or group GAAP)
- Non-leading ledgers (e.g., 2L = local GAAP, TX = tax) carry parallel accounting entries
- Each non-leading ledger can have its own fiscal year variant and posting period variant
- Asset accounting depreciation areas in ANLB map to specific ledgers (via OAOB)
- Use when: material permanent differences exist between reporting frameworks (depreciation methods, lease accounting, pension valuation)

**Approach 3: Document splitting only (no non-leading ledger)**
- Uses document splitting to allocate segment/profit center data across all line items
- NOT a parallel accounting approach in the traditional sense — it enables reporting by segment, not dual-GAAP
- The CONTEXT.MD framing "document splitting only" as a parallel accounting approach may conflate two separate concepts. In ECC 6.0, document splitting is a segment/profit center reporting feature, not a GAAP-parallel feature.

**Correction for content plan:** The third option in the parallel accounting decision tree should be clarified. True parallel accounting in ECC 6.0 has two variants: (a) leading-only (no parallelism), (b) leading + non-leading. Document splitting is a separate feature for segment/profit center balance sheet reporting, not a substitute for non-leading ledgers in parallel GAAP scenarios. The decision tree should address when document splitting alone is sufficient for segment reporting vs. when non-leading ledgers are needed for full GAAP parallelism.

Confidence: MEDIUM (SAP Community consensus; confirmed by SAP online help references)

### 4.2 Reconciliation Account — Multiple per Company Code

**Confirmed:** Yes, multiple reconciliation accounts are supported per company code. This is fundamental to how SAP FI sub-ledgers work.

The reconciliation account number is stored in:
- LFB1.AKONT (vendor master, company code segment) — one per vendor per company code
- KNB1.AKONT (customer master, company code segment) — one per customer per company code

A GL account is flagged as a reconciliation account by field SKB1.MITKZ:
- MITKZ = K → vendor reconciliation account
- MITKZ = D → customer reconciliation account
- MITKZ = A → asset (fixed asset) reconciliation account

**Multiple reconciliation accounts in practice:** A company code commonly has:
- 160000 — Trade payables (domestic vendors)
- 161000 — Intercompany payables
- 162000 — Employee-related payables
- 140000 — Trade receivables (domestic customers)
- 141000 — Intercompany receivables

Each vendor is assigned to one reconciliation account in LFB1.AKONT. Different vendor groups (domestic, intercompany, employee) can point to different reconciliation GL accounts. The assignment is per vendor master record — there is no separate "account group → reconciliation account" config table; the mapping is direct in the vendor master.

**How it is controlled:** The reconciliation account is entered manually in the vendor/customer master record (FK01/FK02 for vendors, FD01/FD02 for customers). There is no automatic assignment from vendor account group to reconciliation account in standard ECC 6.0 — it must be set at the individual master record level.

Confidence: HIGH (direct field reference confirmed via SAP Datasheet; standard FI knowledge)

### 4.3 Asset Class Strategy — Granular vs. Broad

**No hard limit on number of asset classes in ECC 6.0.** SAP does not publish a technical maximum. Performance is not impacted by the number of asset classes themselves — the asset class is a grouping/classification, not a driver of processing volume.

**Configuration implication of more asset classes:**
- Each asset class requires its own account determination key and AO90 GL account assignment
- More asset classes = more AO90 maintenance (potentially beneficial: different COGS/depreciation GL accounts per class)
- Each asset class has its own number range — more classes means more number ranges to maintain (OAOA)
- Depreciation key defaults are set at asset class level — granular classes allow different default useful lives and depreciation methods per class without requiring override at asset level

**When granular helps:**
- Need separate balance sheet GL accounts by asset type (e.g., separate lines for Land, Buildings, Machinery, Vehicles, Furniture, IT Equipment)
- Need to track different useful lives as a default (prevents user error at asset creation)
- Need to report fixed asset rollforward by asset category with separate GL accounts

**When broad helps:**
- Simpler configuration and maintenance
- Fewer number ranges to manage
- Suitable for smaller organizations where granular asset type reporting is not needed
- AO90 maintenance is simpler

Confidence: MEDIUM (training data + SAP Community; no official documentation found setting a maximum)

---

## Section 5: Troubleshooting — Root Cause Verification

### 5.1 FS10N Shows Zero Balances in New GL System

**Root cause confirmed:** FS10N reads the GLT0 table (Classic GL totals table). When New GL is activated, postings go to FAGLFLEXT (New GL totals table) instead of GLT0. GLT0 is NOT updated in a standard New GL-active ECC 6.0 system (unless explicitly configured to continue updating via IMG setting "Deactivate Update of Classic General Ledger" — which, confusingly, is the OFF state).

**Exact mechanism:**
- New GL activation flag is stored in table FAGL_ACTIVEC
- When New GL is active, the posting program updates FAGLFLEXT and FAGLFLEXA (line items) but skips GLT0
- FS10N queries GLT0 → returns zero / shows nothing
- FAGLB03 queries FAGLFLEXT → shows correct balances

**Correct T-code mapping in New GL systems:**

| Need | Classic GL T-code | New GL Replacement |
|------|------------------|-------------------|
| Account balances | FS10N | FAGLB03 |
| Account line items | FBL3N | FAGLL03 |

Note: In newer ECC 6.0 systems, FS10N may automatically redirect to FAGLB03 (system parameter-dependent). If FS10N redirects transparently, the balance display will be correct even though the user typed FS10N.

**Note on FBL3N in New GL systems:** FBL3N still works in New GL systems for basic line item display (reads BSIS/BSAS tables which are still populated). However, FBL3N does NOT show New GL-specific fields: segment, profit center per line, ledger assignment, document splitting results. Use FAGLL03 when those fields are needed.

Confidence: HIGH (multiple SAP Community sources consistent; SAP note 1751173 referenced)

### 5.2 Document Splitting Side Effects

**Zero balance clearing account error:**

Document splitting requires that every document line item carries values for the balancing characteristics (e.g., Profit Center, Segment). When a single document spans multiple profit centers/segments, the system must add additional clearing lines to keep each characteristic-value combination balanced to zero.

These clearing lines post to the "Zero Balance Clearing Account" — a balance sheet GL account (typically configured in SPRO, zero-balance settings for document splitting).

**Root causes of document splitting errors:**

1. **Missing zero balance clearing account configuration:** If the zero balance clearing account is not defined in the IMG (SPRO → Financial Accounting (New) → General Ledger Accounting (New) → Business Transactions → Document Splitting → Define Zero Balance Clearing Account), the system cannot create the balancing lines → error at posting.

2. **GL account not classified for document splitting:** Every GL account used in a posting must have an item category assignment (SPRO → Classify G/L Accounts for Document Splitting). If an account is unclassified, the splitting engine cannot determine the split rule → "incomplete split" error or unexpected behavior.

3. **Document type not classified:** Every document type must be assigned a business transaction and variant for splitting (SPRO → Classify Document Types for Document Splitting). Missing classification → no splitting occurs → balancing fields may be blank → error GLT2201.

4. **Zero-value base lines:** If the base line items used for split calculation sum to zero (e.g., a net-zero AP invoice), the system cannot perform proportional allocation → division by zero error (SAP Note 3035677).

**Error message pattern:** GLT2201 "Balancing field 'Profit Center' in line item 001 not filled" — the most common document splitting error; indicates that a mandatory balancing field was not populated, usually due to missing item category classification or incomplete splitting rule.

Confidence: MEDIUM (SAP Community, SAP Notes 3035677, 2607276 cited in search results)

### 5.3 Asset Accounting Year-End Sequence Errors

**Correct mandatory sequence:**
```
AFAB (depreciation, fully posted for ALL periods in the year)
  → AJRW (open new fiscal year in asset accounting)
    → AJAB (close old fiscal year in asset accounting)
```

**Common errors and root causes:**

1. **AJAB fails with "depreciation not complete":** AFAB has not been run for all periods, or AFAB ran with errors leaving some assets unposted. Fix: Re-run AFAB, clear all errors, post 100% of depreciation, then re-attempt AJAB.

2. **AJRW not run before AJAB:** AJAB requires the new year to be open (AJRW must have run). If AJRW was not run, AJAB fails. Fix: Run AJRW first, then AJAB.

3. **Postings made in old year after AJRW:** If asset postings occur in the old fiscal year AFTER AJRW was run, the carry-forward balances will be incorrect. Fix: Re-run AJRW to re-carry-forward the updated values, then run AJAB.

4. **Multiple years open simultaneously:** In some configurations SAP allows up to two fiscal years to be open simultaneously. If year N-2 was never properly closed, AJAB for year N may fail. Fix: Close years in order (oldest first).

5. **ASKBN required for periodic asset value postings:** In some asset accounting configurations, ASKBN (Post Periodic Asset Value Postings) must run before AJAB. This is relevant for APC values that have not been transferred to the ledger. Fix: Run ASKBN, then retry AJAB.

**Diagnostic T-code:** AW01N (Asset Explorer) — shows planned vs. posted depreciation per period per asset. Use to identify which assets have unposted depreciation before running AJAB.

Confidence: MEDIUM (SAP Community blog, sapsharks.com, consistent with Phase 3 content already in tcodes.md)

### 5.4 F110 Not Picking Up Items / Bank Account Not Selected

**Root causes for items not picked up in proposal (confirmed from techlorean.com and SAP Community):**

1. **Payment block on the open item:** The invoice has a payment block indicator (field BVTYP or blocking reason in the document). Check FB03 on the invoice document. Remove block manually or via invoice verification workflow.

2. **Vendor posting block or deletion flag:** The vendor master (LFA1 or LFB1) has a posting block (SPERR) or deletion flag (LOEVM). Check XK05/FK05. Remove the block or flag before running F110.

3. **Open item not yet due:** The next payment date in F110 parameters is earlier than the invoice due date (calculated from payment terms in LFB1.ZTERM and the invoice baseline date). Verify FBL1N to see due dates.

4. **Payment method not on vendor master:** The payment method in F110 parameters (e.g., "T" for bank transfer) is not in the vendor's LFB1.ZWELS field. Add the payment method to the vendor master.

5. **Missing bank details:** Payment method is configured to require bank details (FBZP → Payment Methods in Country → bank details checkbox). Vendor has no bank account in the vendor master (Payment Transactions tab). Add bank account via FK02/XK02.

6. **Amount below minimum payment threshold:** FBZP → Paying Company Codes sets a minimum payment amount per currency. If the invoice balance is below this threshold, it appears in the exception list but is not paid. Reduce the minimum or aggregate multiple invoices.

7. **Vendor locked by another user (SM12):** Another user is editing the LFB1 record. Check SM12 for locks on LFB1.

8. **Payment method not configured for country:** FBZP → Payment Methods in Country — the payment method selected is not defined for the vendor's country. Configure FBZP.

9. **Payment method not configured for company code:** FBZP → Payment Methods in Company Code — missing configuration for the paying company code + payment method combination.

**Root causes for bank account not selected:**

1. **FBZP bank determination missing or zero available amount:** FBZP → Bank Determination → Bank Accounts tab. If no bank account is ranked for the currency + payment method combination, error FZ671 fires. If the available amount (from S_ALR_87001486) is zero, the bank is skipped.

2. **Incorrect ranking order:** Multiple house banks are ranked in FBZP. The highest-ranked bank is tried first. If its available amount is exhausted, the next-ranked bank is used. Check that the intended bank has the highest rank AND sufficient available amount.

3. **Currency mismatch:** The payment is in a currency not configured under the house bank's bank account in FBZP Bank Determination.

**Diagnostic approach:** Run the F110 payment proposal, then view the payment log (F110 → Edit → Payment Run Log). The log shows exactly why each vendor/item was excluded, with specific message codes (FZ003, FZ019, FZ368, etc.).

Confidence: MEDIUM-HIGH (confirmed by techlorean.com detailed article + SAP Community; consistent with Phase 3 processes.md)

---

## Section 6: Planner Guidance — Content Structure Decisions

These are the areas where Claude has discretion (from CONTEXT.MD). Research-based recommendations:

### 6.1 Q&A Decision Tree Structure

Recommended approach for each of the 7 decision trees:
- **2-4 yes/no branching questions** maximum per tree (more becomes unwieldy in markdown)
- Questions should be binary and answerable by a consultant without system access (e.g., "Does the company file under more than one accounting standard?" not "What is field SKB1.XBILK?")
- End each branch with a named approach label (e.g., "Use Approach B: Leading + Non-Leading Ledger")
- Follow the Q&A section immediately with the comparison table

### 6.2 Dr/Cr Example Format

Recommend using a **two-column table** per example (Account | Amount | Dr/Cr), not sub-sections. Tables are scannable and compact. Keep account numbers labeled inline (e.g., "140000 (Inventory — representative example)").

### 6.3 Decision Tree Ordering

Recommended ordering for fi-advanced.md (most-to-least consulted during implementation):
1. New GL ledger strategy (foundational — affects everything else)
2. Parallel accounting (close second — often asked in project scoping)
3. Document splitting scope (linked to ledger strategy)
4. Reconciliation account assignment (AP/AR master data design)
5. Payment terms design
6. Tolerance group design
7. Asset class strategy (often later in project)

Rationale: Ledger strategy, parallel accounting, and document splitting are decided at project start. Reconciliation account, payment terms, tolerances, and asset classes are configured during detailed design.

### 6.4 Number of Pitfall/Symptom Entries Beyond 4 Priority Areas

Research suggests the four priority areas (New GL confusion, document splitting, AA year-end, F110) cover the highest-frequency issues. Recommend **2-3 additional entries** per section beyond the 4 priority areas to cover:

Additional pitfalls worth including (MEDIUM confidence):
- **Posting period not open (OB52):** Common implementation error; consultants forget to open periods for account type M (materials) separately from S (GL)
- **Tolerance group mismatch:** User assigned to wrong tolerance group; large invoices blocked unexpectedly
- **GR/IR account not set up as open-item managed:** F.13 automatic clearing fails; GR/IR balance grows indefinitely

Additional symptoms worth including:
- **FBL1N shows vendor items but F110 does not pick them up** → leads into the F110 troubleshooting section
- **Balance sheet not balancing in F.01** → FSV (financial statement version OB58) has unassigned accounts

---

## Section 7: Architecture Patterns — File Structure

Phase 4 produces two new files. No architectural surprises; structure follows Phase 3 file patterns.

### account-determination.md

Recommended structure:
```
# Account Determination
## Overview — How OBYC Works (the determination chain)
## MM Goods Receipt (Movement Types 101, 102)
   ### Logic Explanation
   ### Transaction Keys: BSX, WRX, PRD, GBB
   ### Worked Example: GR for PO (Dr Inventory / Cr GR/IR)
   ### Standard Price vs Moving Average Price
## MM Goods Issue (Movement Types 261, 262, 551)
   ### Logic Explanation
   ### GBB Account Modifiers: VBR, VNG, VAX
   ### Worked Example: GI to Production Order (Dr Consumption / Cr Inventory)
   ### Worked Example: Scrapping (Dr Scrapping Loss / Cr Inventory)
## SD Revenue — VKOA Framework
   ### What VKOA Is (condition technique introduction)
   ### KOFI vs KOFK
   ### Five Access Tables in KOFI00
   ### KTGRD and Material Account Assignment Group
   ### Account Keys (ERL, ERS) — link to pricing procedure
## FI-Only Automatic Postings
   ### FX Valuation (F.05 + OBA1: KDB and KDF)
   ### Cash Discount (OBXU/OBXI — not OBB8)
   ### Clearing Account Mechanics
```

### fi-advanced.md

Recommended structure:
```
# FI Advanced — Decision Trees and Troubleshooting
## Decision Trees
   ### [7 trees, each with Q&A routing + comparison table]
## Implementation Pitfalls
   ### [4 priority + 2-3 additional]
## Symptom-Based Troubleshooting
   ### [4 priority + 2-3 additional]
```

---

## Common Pitfalls for Content Authors

### Pitfall 1: Confusing cash discount config location
**What goes wrong:** Writing that cash discount GL accounts are in OBB8
**Correct fact:** OBB8 = payment terms (days, percentages). Cash discount GL accounts = OBXU (received), OBXI (paid)

### Pitfall 2: FS10N vs FAGLB03 explanation
**What goes wrong:** Saying FS10N "doesn't work" in New GL — it may auto-redirect in some systems
**Correct fact:** FS10N reads GLT0 which is not updated in standard New GL-active systems. Redirect behavior depends on system parameter FAGL_READ_GLT0_USER. Safe rule: always use FAGLB03 in New GL systems.

### Pitfall 3: ZDI/SKT as OBYC keys
**What goes wrong:** Treating ZDI and SKT as OBYC transaction keys for cash discount
**Correct fact:** ZDI is an SD pricing condition type. SKT may be used in some custom SD pricing procedures. FI-side cash discount account determination uses OBXU/OBXI. These are completely separate mechanisms.

### Pitfall 4: PRD always posting
**What goes wrong:** Writing that PRD always fires at GR
**Correct fact:** PRD only fires when the material has standard price control (indicator S). For MAP materials (indicator V), price differences go to BSX (stock account), not PRD.

### Pitfall 5: GBB/VAX for all COGS
**What goes wrong:** Using GBB/VAX as the example for "goods issue for production order"
**Correct fact:** Production order GI (261) uses GBB/**VBR**. VAX is for goods issue to a sales order (movement 601) without a CO account assignment object.

---

## Open Questions

1. **FRN transaction key for freight:** The search results mention FRN as a transaction key for freight/customs during GR, but details were limited. The content plan notes "MM goods receipt (BSX = inventory, WRX = GR/IR clearing, PRD = price differences, GBB = offsetting)" — FRN is not listed. For most standard GR scenarios, FRN is only relevant when the PO has freight/delivery cost conditions. Safe to omit from the main worked example and note in a "see also" reference.
   - What we know: FRN fires for freight clearing when MM freight conditions exist on the PO
   - What's unclear: Exact condition for FRN vs. standard BSX/WRX path
   - Recommendation: Focus the GR worked example on the 4 keys mentioned in CONTEXT.MD; note FRN exists for POs with freight conditions

2. **KON (consignment) account modifier details:** KON is one of three OBYC keys with account modifiers, but the content plan does not cover consignment. Confirmed out of scope for Phase 4 (consignment is Phase 6 territory).

3. **VKOA material account assignment group exact field name:** The field is labeled "Acct assmt grp material" in the material master (Sales Org 2 view). The ABAP field name varies by source (MVGR5, MVKE-MVGR5). For content purposes, refer to it by the material master screen label: "Account assignment group of material."

4. **AJRW/AJAB timing relative to FI GL close:** SAP Community discussions mention that AJAB and FAGLGVTR (carry forward balance in New GL) have a recommended order. AJAB closes asset accounting; FAGLGVTR carries forward GL balances. The recommended sequence is AJAB first, then FAGLGVTR. This is relevant to the AA year-end troubleshooting section.

---

## Sources

### Primary (MEDIUM confidence — SAP Community, multiple sources agree)
- SAP Community: "Automatic Account Determination — Transaction keys like BSX, GBB, PRD, WRX" — OBYC key behavior
- SAP Community: "OBYC — GBB — Transaction keys" — GBB modifier list confirmed
- SAP Community: "Account determination — VKOA — KOFI & KOFK" — KOFI vs KOFK distinction
- SAP Community: "General Modification Keys — OBYC" — full GBB modifier list with AUA, AUF, VBR, VNG, VAX, VBO, ZOB confirmed
- TechLorean: "Top 12 Common F110 Payment Run Errors" — F110 troubleshooting root causes
- sap96.com: "Automatic Postings for Foreign Currency Valuation — OBA1" — KDB/KDF keys and account structure
- tutorialkart.com: "Define Accounts for Cash Discount Taken in SAP" — OBXV/OBXU cash discount config path
- SAP Community: "Balance difference in table GLT0 vs FAGLFLEXT" — FS10N/FAGLB03 root cause
- SAP Community: "Document splitting, Zero balance clearing account" — split error root causes
- SAP Community: "Asset Year End Closing AJRW & AJAB" — year-end sequence and error patterns

### Secondary (LOW confidence — single source, confirm before including)
- SAP Community: "Problem with document splitting and zero balance clearing account" — GLT2201 error message
- saplogisticsexpert.com: VKOA five access tables and field combinations
- Revenue Account Determination Configuration wiki (SCN) — KOFI access sequence hierarchy

### Metadata
- **Research date:** 2026-02-16
- **ECC version target:** ECC 6.0 (all findings filtered for ECC 6.0 behavior)
- **S/4HANA content excluded:** Confirmed; sources touching S/4HANA Universal Journal or Fiori ignored
- **Valid until:** ~2026-03-16 (SAP ECC 6.0 configuration does not change; content is stable)
