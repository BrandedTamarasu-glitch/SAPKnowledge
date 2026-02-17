---
module: sd
content_type: research
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium-high
last_verified: "2026-02-17"
phase: 08-sd-advanced-and-fi-integration
created: 2026-02-17
---

# Phase 8: SD Advanced & FI Integration - Research

**Researched:** 2026-02-17
**Domain:** SAP ECC 6.0 Sales & Distribution — VKOA account determination, SD decision trees (pricing, copy control, partner determination, availability check, credit management), troubleshooting, SD-FI integration
**Confidence:** MEDIUM-HIGH (existing KB provides strong SD foundation from Phase 7; VKOA framework intro exists in fi/account-determination.md from Phase 4; Phase 6 MM Advanced provides the structural template)

---

## Summary

Phase 8 mirrors Phase 6 (MM Advanced & FI Integration) for the SD module. It layers four content types onto the Phase 7 SD foundation: (1) a deep VKOA account determination walkthrough with dual-axis navigation and 8-10 worked billing-to-GL examples, (2) 12 SD configuration decision trees covering pricing, copy control, partner determination, availability check, credit management, and other key SD design decisions, (3) 12 symptom-first troubleshooting entries with SAP message IDs (V1/V2/VF/VK classes), and (4) the first complete SD-FI integration documentation including the VF01 billing-to-FI trace and a full SD-FI integration point catalog.

The VKOA content builds directly on the framework introduction already in `modules/fi/account-determination.md` (Phase 4, Section 4), which covers the KOFI/KOFK condition types, the 5-level access sequence, the key fields (KTGRD, KTGRM, account key), and the diagnostic/setup paths. Phase 8 extends this with the full pricing-to-VKOA chain (pricing procedure to condition type to account key to VKOA lookup to GL account), dual-axis worked examples (by account key AND by condition type), and VKOA debugging procedures.

The SD-FI integration documentation populates the existing placeholder `modules/sd/integration.md` with a comprehensive integration point catalog and transaction traces answering "what happens in FI when I post VF01 billing document."

**Primary recommendation:** Follow the Phase 6 file structure exactly: sd-advanced.md (VKOA walkthrough + decision trees + troubleshooting) and integration.md (SD-FI integration). The VKOA section should use dual-axis navigation by account key AND by condition type. Decision trees should prioritize pricing-related topics (3-4 trees) and include a dedicated copy control tree. Troubleshooting should emphasize SD-specific daily support pain points (incompletion, delivery blocks, billing blocks, credit blocks).

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### VKOA Walkthrough Depth
- Dual-axis approach like OBYC: by account key (ERL, ERS, EVV, ERF, ERU, MWS) AND by condition type (PR00, MWST, KF00, K004, K005, RA00)
- Cross-reference to fi/account-determination.md VKOA intro section — extend, don't duplicate the framework
- 8-10 worked billing-to-GL examples covering: standard revenue (ERL), sales deductions (ERS), cash discount (EVV), freight revenue (ERF), tax (MWS), credit memo, rebate accrual, intercompany
- Full pricing-to-VKOA chain: pricing procedure -> condition type -> account key assignment (V/08) -> VKOA lookup -> GL account. Show how condition type config feeds VKOA determination.
- Full VKOA debugging path: VF03 billing analysis -> VKOA simulation -> check account key assignment -> verify GL account -> common failure points

#### Decision Trees Scope
- 12 decision trees (matching Phase 6 MM count for consistency)
- Multiple pricing-related trees (~3-4): pricing procedure design (which condition types to include), access sequence strategy, condition exclusion groups, pricing determination assignment (OVKK)
- Dedicated copy control decision tree: when to use requirements, data transfer routines, copy control at header vs item, common scenarios (VTAA/VTLA/VTFL/VTAF)
- Remaining trees cover: partner determination, availability check, output determination, credit management, item category determination, and other key SD config decisions
- Q&A routing format with comparison tables and config implications inline (same format as Phase 6)

#### Troubleshooting Format
- 12 troubleshooting entries (matching Phase 6 MM count)
- Include SAP message IDs (V1/V2/VF/VK class) where applicable
- Dedicated entries for SD-specific pain points: incompletion procedure issues, delivery blocks, billing blocks, credit blocks — these are daily SD support topics
- Each entry self-contained with full resolution path inline (same pattern as Phase 6 — no cross-file lookups needed)
- Diagnostic T-codes referenced inline (VF03, VA03, VL03N, V/08, VKOA, etc.)

#### SD-FI Integration Scope
- Full VF01 billing-to-FI trace: billing doc (VBRK/VBRP) -> VKOA determination -> FI document (BKPF/BSEG) -> revenue/COGS/tax postings -> customer open item. Show tables and fields at each step.
- Full SD-FI integration point catalog (like the 20-entry MM-FI catalog): all SD-FI touchpoints with billing types, VKOA keys, document types, GL impact, plus special scenarios (rebate accruals, intercompany, returns)
- Moderate depth on revenue recognition: basic revenue posting via VKOA (ERL), deferred revenue setup, milestone billing basics, relationship between billing plan types and revenue timing. Defer complex revenue recognition (POC) to Phase 12.
- SD period-end FI impacts: rebate settlement (VBO1/VBOF), revenue accruals, billing due list cleanup (VF04), credit management reset, and their FI posting impacts

### Claude's Discretion
- Exact distribution of the 12 decision trees across SD subdomains (beyond the specified pricing and copy control trees)
- Level of detail on intercompany billing in VKOA examples (foundation vs deep-dive)
- Whether to include a separate "common VKOA misconfigurations" section or fold into troubleshooting
- How to organize the sd-advanced.md file sections (VKOA first vs decision trees first)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

---

## Section 1: VKOA Account Determination -- Verified Facts for Expanded Coverage

### 1.1 Existing Foundation (from Phase 4)

The knowledge base already contains in `modules/fi/account-determination.md` (Section 4):
- What VKOA is: the SD-side equivalent of OBYC, mapping billing document line items to revenue, COGS, and freight GL accounts
- KOFI vs KOFK distinction: KOFI for FI account determination, KOFK for CO-PA profitability
- KOFI access sequence: 5 levels from most specific (table 1: Chart of Accounts + Sales Org + Cust AAG + Mat AAG + Account Key) to least specific (table 5: Chart of Accounts + Account Key)
- Key fields: KTGRD (customer account assignment group from KNVV), KTGRM (material account assignment group from MVKE), Account Key (from pricing procedure)
- Standard account keys: ERL (revenue), ERS (sales deductions), ERF (freight revenue), MWS (output tax), EIN (cost posting)
- Diagnostic path: T-code VKOA -> select KOFI -> navigate condition tables
- Setup path: VKOA -> KOFI -> condition table -> New Entries

Phase 8 does NOT duplicate this framework. It adds:
- The pricing-to-VKOA chain (how pricing procedure config feeds VKOA determination)
- Dual-axis worked examples by account key AND by condition type
- Additional account keys (EVV for cash discount, ERU for unbilled revenue)
- VKOA debugging path specific to billing document analysis
- 8-10 worked billing-to-GL examples

Confidence: HIGH (existing KB content verified)

### 1.2 VKOA Account Keys -- Complete Reference

The account key is assigned at the condition type level within the pricing procedure (V/08 -> condition type -> AcctKey field, or V/09 -> pricing procedure step -> AcctKey column). Each account key maps to a different GL account category in VKOA.

**Standard VKOA account keys:**

| Account Key | Purpose | Assigned To (Typical Condition Types) | GL Account Category |
|------------|---------|--------------------------------------|---------------------|
| ERL | Revenue | PR00 (base price), condition types representing net revenue | Revenue GL accounts (e.g., 800000 domestic, 810000 export) |
| ERS | Sales deductions / discounts | K004, K005, K007 (discounts), RA00 (rebate accrual), HB00 (rebate basis) | Discount/allowance GL accounts |
| EVV | Cash discount (Skonto) | Derived from payment terms, not a condition type — posts at payment clearing | Cash discount expense GL account |
| ERF | Freight revenue | KF00 (freight), other freight condition types | Freight revenue GL account |
| ERU | Unbilled receivables / accruals | Used in milestone billing and deferred revenue scenarios | Accrual/deferred revenue GL account |
| MWS | Output tax (VAT/sales tax) | MWST (output tax condition type) | Tax GL accounts (output tax payable) |
| EIN | Cost posting | Used for COGS-related condition types in some configurations | Cost/expense GL accounts |

**Key behavioral notes:**
- ERL is the primary revenue key. In a standard pricing procedure, PR00 (base price) carries the ERL account key, and VKOA resolves the ERL entry to determine the revenue GL account.
- ERS is used for all sales deductions that reduce revenue: material discounts, customer discounts, rebate accruals. Each can post to a different GL account if VKOA table 1 (most specific) has differentiated entries.
- EVV (cash discount/Skonto) behaves differently from ERS. EVV posts at the time of payment clearing, not at billing time. When the customer takes a cash discount on an AR open item, the discount amount posts to the EVV GL account.
- MWS is always determined by the tax condition type (MWST). The tax GL account is typically driven by the tax code, not by VKOA directly — but VKOA can provide the account for the output tax posting.

Confidence: HIGH for ERL, ERS, MWS, ERF (these are well-established standard keys consistent with existing KB). MEDIUM for EVV and ERU (behavior verified against SAP standard but specific GL account mapping varies by implementation).

### 1.3 Pricing-to-VKOA Chain

This is the end-to-end chain from pricing procedure configuration through VKOA to GL account. The CONTEXT.md specifically calls this out as "the #1 question SD consultants ask about account determination."

```
Step 1: Pricing Procedure (V/09)
        Defines the calculation schema: which condition types apply, in what order
        Each step in the pricing procedure has: Step, Condition Type, AcctKey column
        The AcctKey column assigns the account key to the condition type's posting
        Example: Step 900, Condition Type PR00, AcctKey = ERL (revenue)
                 Step 910, Condition Type K004, AcctKey = ERS (sales deduction)
                 Step 920, Condition Type MWST, AcctKey = MWS (tax)

Step 2: Condition Type Configuration (V/08)
        Each condition type has an AcctKey field (Acct. key column)
        This links the condition type to the VKOA account key
        The assignment can be at the condition type level OR overridden in the pricing procedure

Step 3: Pricing Procedure Determination (OVKK)
        Sales Area + Document Pricing Procedure (from VOV8) + Customer Pricing Procedure (from KNVV-KALKS)
        -> Pricing Procedure
        If no OVKK entry exists: no pricing procedure, no prices, no VKOA determination

Step 4: Billing Document Creation (VF01/VF04)
        At billing, the system reads the pricing procedure and its condition types
        For each active condition type with an account key:
        -> System executes VKOA (KOFI) determination using:
           - Chart of Accounts (from company code)
           - Sales Organization
           - Customer Account Assignment Group (KTGRD from KNVV)
           - Material Account Assignment Group (KTGRM from MVKE)
           - Account Key (ERL, ERS, MWS, etc.)

Step 5: VKOA Lookup (access sequence KOFI00)
        Searches 5 condition tables from most specific to least specific
        First match found = GL account used for the FI posting
        Table 1: CoA + Sales Org + Cust AAG + Mat AAG + Account Key (most specific)
        Table 5: CoA + Account Key (catch-all)

Step 6: FI Document Creation
        GL accounts from VKOA populate the BSEG line items:
        - Revenue line: GL from ERL determination
        - Discount line(s): GL from ERS determination
        - Tax line: GL from MWS determination
        - Customer line: Reconciliation account from KNB1-AKONT
```

Confidence: HIGH (the pricing-to-VKOA chain is standard SAP architecture, consistent with the existing config-spro.md pricing section and fi/account-determination.md VKOA section)

### 1.4 Worked Example Scenarios (8-10 Required)

Based on CONTEXT.md decisions, the following worked examples are required:

**Example 1: Standard Revenue (ERL) -- Domestic Sale**
Standard billing document (F2) for domestic customer. PR00 base price with ERL account key. VKOA resolves: CoA + Sales Org 1000 + Cust AAG 01 (domestic) + Mat AAG 01 (finished goods) + ERL -> Revenue GL 800000.
- Dr Customer (reconciliation account from KNB1-AKONT)
- Cr Revenue (ERL -> VKOA -> GL 800000)

**Example 2: Standard Revenue with Tax (ERL + MWS) -- Taxable Sale**
Same as Example 1 but with output tax (MWST condition type). Two VKOA lookups: ERL for revenue, MWS for tax.
- Dr Customer (gross amount including tax)
- Cr Revenue (net amount, from ERL)
- Cr Output Tax Payable (tax amount, from MWS)

**Example 3: Sales Deductions (ERS) -- Material Discount**
Billing with K004 (material discount) active in the pricing procedure. K004 carries ERS account key.
- Dr Customer (net of discount)
- Cr Revenue (gross amount from ERL)
- Dr Sales Deductions (discount amount from ERS)

Alternative presentation: net method where revenue posts at net and discount is not separately visible. The deduction account and method depend on VKOA configuration.

**Example 4: Cash Discount (EVV) -- Payment with Discount**
Customer pays within discount period. The cash discount posts at payment clearing time (F-28 or F.13), not at billing time. The EVV account key drives the GL account for the discount expense.
- At billing: Dr Customer (full invoice amount), Cr Revenue (ERL), Cr Tax (MWS)
- At payment: Dr Bank (payment amount), Dr Cash Discount Expense (EVV GL account), Cr Customer (full invoice amount)

Note: EVV behavior overlaps with OBXI (cash discount granted) configuration in FI. The VKOA EVV entry may be used instead of or in addition to OBXI depending on whether SD or FI controls the cash discount GL account. This is a common configuration decision point.

**Example 5: Freight Revenue (ERF) -- Freight Charge**
Billing with KF00 (freight) condition type carrying ERF account key.
- Dr Customer
- Cr Revenue (net product revenue from ERL)
- Cr Freight Revenue (freight amount from ERF)

**Example 6: Credit Memo**
Credit memo (billing type G2) from a credit memo request (VA01 doc type CR). The VKOA determination runs in reverse — revenue is debited (reducing revenue) and customer is credited (reducing receivable).
- Dr Revenue (ERL GL account — same account as original billing, reverse side)
- Cr Customer (reconciliation account)

**Example 7: Rebate Accrual (RA00/ERS)**
Rebate accrual posting during standard billing. RA00 condition type with ERS account key accrues the rebate liability. At settlement (VF44/VF45), the accrual is reversed and a credit memo is created.
- At billing (accrual): Dr Rebate Expense (ERS GL account), Cr Rebate Accrual Liability
- At settlement: Reverse accrual, create credit memo (Dr Revenue, Cr Customer)

**Example 8: Intercompany Billing**
Intercompany sales where selling company and delivering company are different. Two billing documents: one to the external customer (standard), one intercompany between the two company codes.
- External billing: Dr Customer (selling CC), Cr Revenue (ERL, selling CC)
- Intercompany billing: Dr Intercompany Receivable (selling CC), Cr Intercompany Payable (delivering CC)

The intercompany VKOA uses Cust AAG 03 (intercompany) to route revenue/cost to intercompany-specific GL accounts.

Confidence: HIGH for examples 1-3, 5-6 (standard VKOA patterns). MEDIUM for examples 4, 7, 8 (EVV cash discount mechanics, rebate accrual posting, and intercompany billing have implementation-specific variations).

### 1.5 VKOA Debugging Path

The diagnostic path for VKOA issues, specific to billing document analysis:

**Step 1: Analyze the billing document (VF03)**
- Open the billing document in VF03
- Go to Environment -> Account Determination Analysis (or use menu path Environment -> Accounting Document)
- Review the FI document number and the GL accounts posted
- If no FI document was created: check for billing blocks or errors in the billing log

**Step 2: Check VKOA simulation**
- T-code VKOA -> Select KOFI -> Navigate to the relevant condition table
- Enter: Chart of Accounts + Sales Org + Customer AAG (from KNVV-KTGRD) + Material AAG (from MVKE-KTGRM) + Account Key
- If no entry found: this is the missing configuration. Check table 5 (catch-all) as fallback.

**Step 3: Verify account key assignment**
- Check the pricing procedure (V/09): is the account key assigned to the condition type step?
- Check the condition type (V/08): does the AcctKey field have a value?
- If no account key: the condition type's value will not post separately to FI — it will be absorbed into the net amount

**Step 4: Verify customer and material account assignment groups**
- Customer: XD03 or VD03 -> Billing tab -> KTGRD (customer account assignment group)
- Material: MM03 -> Sales Org 2 view -> KTGRM (material account assignment group)
- If blank or wrong: VKOA lookup uses the wrong access level or fails

**Step 5: Check common failure points**
- Missing VKOA entry for the specific account key + AAG combination
- KTGRD blank on customer master (most common — overlooked during customer creation)
- KTGRM blank on material master (second most common — Sales Org 2 view not maintained)
- OVKK entry missing (no pricing procedure -> no account keys -> no VKOA determination)
- Wrong chart of accounts in VKOA (multi-company-code setup)

Confidence: HIGH (standard SAP diagnostic approach, consistent with existing KB patterns)

---

## Section 2: SD Decision Trees -- Research Findings

### 2.1 Recommended Distribution of 12 Decision Trees

Based on CONTEXT.md requirements (3-4 pricing trees, dedicated copy control tree, remaining trees for other SD config areas):

**Pricing Trees (4):**
1. Pricing Procedure Design — which condition types to include, step sequence, subtotals, requirements
2. Access Sequence Strategy — how many condition tables, specificity order, exclusive indicators
3. Condition Exclusion Groups — when to use exclusion groups, best-of-N logic vs all-apply
4. Pricing Determination Assignment (OVKK) — how to structure the 3-key determination

**Copy Control Tree (1):**
5. Copy Control Design — VTAA/VTLA/VTFL/VTAF: when to use requirements vs data transfer routines, header vs item level, pricing type at copy, common scenarios

**Other SD Config Trees (7):**
6. Partner Determination — partner functions, mandatory vs optional, determination procedure assignment to document types
7. Availability Check (ATP) — checking groups, checking rules, what stock/supply to include, scope control
8. Output Determination — output types, medium selection (print/fax/EDI/email), timing, partner-based output
9. Credit Management — credit control area setup, credit groups, static vs dynamic checks, credit limit strategy
10. Item Category Determination — understanding the 4-key lookup (doc type + MTPOS + usage + higher-level), common item categories and when to customize
11. Billing Type Selection — F2 vs G2 vs L2 vs RE vs S1, order-related vs delivery-related billing, invoice lists
12. Incompletion Procedure Design — which fields to make mandatory, warning vs error status, separate procedures for header/item/schedule line/partner

Confidence: HIGH (these 12 cover the major SD configuration decision areas identified in the existing config-spro.md and processes.md)

### 2.2 Pricing Procedure Design (Tree 1)

**Key decision factors:**

- Q1: What pricing elements does the business need? (base price, discounts, surcharges, freight, tax, rebates)
- Q2: Are discounts calculated as percentage of base price, net price, or specific subtotals?
- Q3: Do you need manual pricing overrides at order entry?
- Q4: Are there statistical condition types (for reporting only, no price impact)?

**Standard pricing procedure structure (RVAA01 as reference):**

| Step Range | Content | Account Key | Notes |
|-----------|---------|-------------|-------|
| 1-99 | Gross price (PR00) | ERL | Base price determination |
| 100-299 | Material/customer discounts (K004, K005, K007) | ERS | Discount conditions |
| 300-399 | Subtotal (net value 1) | — | KOMP subtotal field |
| 400-499 | Freight (KF00) | ERF | Freight charges |
| 500-599 | Subtotal (net value 2) | — | Before tax |
| 600-699 | Rebate accrual (RA00) | ERS | Statistical or posting |
| 800-899 | Tax (MWST) | MWS | Output tax |
| 900-999 | Total | — | Final total |

**Config implications per approach:**

| Approach | When to Use | Trade-offs |
|----------|------------|------------|
| Copy SAP standard (RVAA01) and modify | First implementation; standard pricing needs | Fast start; SAP provides tested baseline; may include unneeded condition types |
| Build from scratch | Complex pricing; multi-tier discounts; non-standard requirements | Full control; no inherited complexity; more design effort |
| Multiple pricing procedures | Different business lines need different pricing logic | OVKK routes by sales area + doc pricing proc + cust pricing proc; maintain multiple procedures |

Confidence: HIGH (standard SAP pricing architecture, verified against existing config-spro.md)

### 2.3 Copy Control Design (Tree 5)

**Key decision factors:**

| Copy Control T-code | From -> To | Key Scenarios |
|--------------------|-----------|---------------|
| VTAA | Order -> Order | Quotation -> order, contract -> release order, returns -> credit memo request |
| VTLA | Order -> Delivery | Sales order -> outbound delivery (most common) |
| VTFL | Delivery -> Billing | Delivery -> invoice (delivery-related billing) |
| VTAF | Order -> Billing | Sales order -> invoice (order-related billing, e.g., third-party, credit memo request -> credit memo) |

**Critical fields at item level:**

| Field | Purpose | Common Values |
|-------|---------|---------------|
| Requirement | ABAP routine checked at copy time — WHEN is copying allowed? | 001 (header), 002 (item), 301 (complete reference) |
| Data Transfer Routine | ABAP routine controlling HOW fields are mapped | 001 (header), 002 (item) |
| Pricing Type | Pricing recalculation behavior | B (carry over + redetermine), C (copy pricing), D (redetermine from scratch), G (copy + redetermine freight) |
| Billing Quantity | Source of billing quantity | E (from delivery), blank (from order) |

**Decision tree Q&A:**
- Q1: Is this delivery-related billing (VTFL) or order-related billing (VTAF)?
- Q2: Should pricing be recalculated at copy? (B = partial redetermine, C = full copy, D = full redetermine)
- Q3: Are custom requirements needed? (When SAP standard requirements don't match business rules)
- Q4: Do you need different copy control for different document type combinations? (e.g., OR->LF uses one set, RE->LR uses another)

Confidence: HIGH (copy control is thoroughly documented in existing config-spro.md Section 4)

### 2.4 Credit Management Design (Tree 9)

Phase 7 kept credit management at foundation level with explicit deferral to Phase 8 for design guidance. The decision tree should cover:

- Q1: Do you need automatic credit checking? (Most implementations = yes)
- Q2: At which points should credit be checked? (Order creation, delivery creation, goods issue — credit groups 01, 02, 03)
- Q3: Static check only (credit limit vs exposure) or dynamic check (include open orders, deliveries, billing docs in exposure)?
- Q4: How should credit blocks be released? (VKM1 manual release, workflow, automatic release rules)

**Credit check types:**

| Check Type | What It Compares | When to Use |
|-----------|-----------------|-------------|
| Static | Credit limit (FD32) vs total receivables (KNKK-SKFOR) | Simple credit control; small customer base |
| Dynamic | Credit limit vs total exposure (open items + open orders + open deliveries + billing docs not yet invoiced) | Most implementations; comprehensive exposure view |
| Maximum document value | Single document value vs max allowed | Catches unusually large orders regardless of overall exposure |

**Configuration path:** OVA8 (central credit check config) -> define credit control area (typically 1:1 with company code) -> assign to company code (OB38) -> define credit groups -> assign to document types (VOV8) -> define automatic credit check rules (static, dynamic, max document value)

Confidence: MEDIUM-HIGH (credit management config is referenced in existing config-spro.md Section 8; deep configuration details verified against SAP standard)

### 2.5 Other Key Decision Areas

**Partner Determination (Tree 6):**
- Key decision: Which partner functions are mandatory per document type?
- Standard functions: AG (sold-to), WE (ship-to), RE (bill-to), RG (payer), VE (sales rep)
- Config: SPRO -> SD -> Basic Functions -> Partner Determination -> Set Up Partner Determination
- Trade-off: Too many mandatory partners = data entry burden; too few = missing critical relationships

**Availability Check (Tree 7):**
- Key decision: What stock and supply elements to include in ATP check
- Checking group (MARC-MTVFP) + checking rule (from document type) = scope
- Trade-off: Include more supply elements = more confirmed, but less accurate promises; include less = more conservative, safer promises

**Item Category Determination (Tree 10):**
- 4-key lookup: doc type + item category group (MVKE-MTPOS) + usage + higher-level item category
- Key decision: When to create custom item categories vs use standard (TAN, TANN, TAX, TAS, REN)
- Critical: MTPOS must be maintained in material master MVKE — missing MTPOS is the #1 item category determination error

Confidence: HIGH for all (these are standard SD configuration areas documented in existing config-spro.md)

---

## Section 3: Troubleshooting -- SAP Message IDs and Diagnostic Patterns

### 3.1 Message Class Reference for SD

Key SAP message classes for SD troubleshooting:

| Class | Area | Description |
|-------|------|-------------|
| V1 | Sales Documents | Sales order creation, change, incompletion |
| V2 | Shipping/Delivery | Delivery creation, PGI, shipping |
| VF | Billing | VF01/VF04 billing document creation and errors |
| VK | Pricing | Condition record maintenance, pricing errors |
| V4 | Output Determination | Output processing, NACE |
| UKM | Credit Management | Credit check (S/4 — ECC uses custom messages) |
| F5 | FI Document Posting | Account determination failures at billing |

### 3.2 Recommended Troubleshooting Entries (12 Target)

**Sales Documents (3 entries):**

1. **Incompletion log blocks save / processing** — Incompletion procedure flags mandatory fields as missing. VA03 -> Incompletion Log shows which fields. Resolution: maintain missing fields or adjust incompletion procedure (V_20/OVA2) if requirements changed.

2. **"Item category not found" or wrong item category proposed** — 4-key determination fails because MVKE-MTPOS (item category group) is blank on material master or wrong combination in OVLP. Resolution: Check MM03 -> Sales Org 1 view -> MTPOS; verify OVLP entry for doc type + MTPOS + usage + higher-level item cat.
   - This is the single most common SD configuration error during implementation.

3. **Pricing not determined / pricing procedure missing** — No OVKK entry for the sales area + document pricing procedure + customer pricing procedure combination. Resolution: Check OVKK for the three-key combination; verify VOV8 doc pricing procedure and KNVV-KALKS customer pricing procedure.

**Delivery (2 entries):**

4. **"Shipping point could not be determined"** — Shipping point determination fails because no entry exists in the determination table for shipping condition (KNVV-VSBED) + loading group (MARC-LADGR) + plant. Resolution: Check customer master shipping condition, material master loading group, and shipping point assignment table (OVXC).

5. **Delivery blocked / cannot create delivery** — Multiple possible causes: delivery block on sales order (VBAK-LIFSK), credit block (VKM4), incomplete schedule lines, or no confirmed quantity. Resolution: Check VA03 for delivery block field; check VKM4 for credit block; verify schedule line confirmed quantity in VBEP.

**Billing (3 entries):**

6. **VF01/VF04 "Account determination error" at billing** — Missing VKOA entry for the account key + customer AAG + material AAG combination. Resolution: Check VKOA for the specific account key; verify KNVV-KTGRD (customer AAG) and MVKE-KTGRM (material AAG) are maintained.
   - SAP message class: F5 errors (account determination), VF class errors
   - Most common cause: KTGRD blank on customer master Billing tab

7. **Billing document created but no FI document** — Billing block exists, or billing type configured to not create FI documents (pro forma billing). Resolution: Check VOFA (billing type config) for accounting relevance; check VFX3 for blocked billing docs.

8. **Billing quantity wrong or zero** — Copy control (VTFL/VTAF) pricing type or billing quantity source misconfigured. Resolution: Check VTFL item-level copy control: billing quantity source (E = from delivery, blank = from order); check delivery quantities in VL03N; verify PGI was posted (billing typically requires PGI for delivery-related billing).

**Credit Management (2 entries):**

9. **Sales order/delivery blocked by credit check** — Customer credit exposure exceeds limit in FD32. Resolution: Check FD32 for credit limit and exposure; review VKM1 (order blocks), VKM4 (delivery blocks), VKM5 (GI blocks); release by removing block or increasing credit limit.

10. **Credit check not executing despite configuration** — Credit group not assigned to document type in VOV8, or automatic credit check rules not defined in OVA8. Resolution: Verify VOV8 credit group assignment; check OVA8 for credit check rules; verify credit control area assignment to company code (OB38).

**Pricing (1 entry):**

11. **Condition record not found / wrong price** — Access sequence searches condition tables but finds no matching record, or finds wrong record. Resolution: Use VA03 -> Pricing Analysis (condition tab -> Analysis button) to see which access sequence steps were searched and which succeeded/failed; check VK13 for condition record existence and validity dates.

**Output (1 entry):**

12. **Output not generated / wrong output** — Output determination procedure not assigned to document type, or output condition records missing. Resolution: Check NACE for the application (V1/V2/V3); verify output determination procedure is assigned to the document type; check VV33 for output condition records; check output processing log in the document (VA03/VL03N/VF03 -> Header -> Output).

Confidence: MEDIUM-HIGH (symptom patterns are standard SD support knowledge; specific message IDs need validation against SAP Datasheet for exact class/number but the patterns are correct)

### 3.3 Key Diagnostic T-Codes for SD Troubleshooting

| T-Code | Purpose | Use In Troubleshooting |
|--------|---------|----------------------|
| VA03 | Display sales order | Check incompletion log, pricing analysis, document flow, blocks |
| VL03N | Display delivery | Check delivery status, PGI status, shipping point |
| VF03 | Display billing document | Check FI document link, account determination analysis, pricing |
| VKM1 | Credit-blocked orders | Review and release credit-blocked sales orders |
| VKM4 | Credit-blocked deliveries | Review and release credit-blocked deliveries |
| VFX3 | Blocked billing documents | Review and release blocked billing documents |
| V/08 | Condition type config | Check account key assignment on condition types |
| V/09 | Pricing procedure config | Check pricing procedure steps and account keys |
| VKOA | Revenue account determination | Check and maintain GL account assignments |
| OVKK | Pricing procedure assignment | Verify 3-key pricing procedure determination |
| OVLP | Item category determination | Check 4-key item category lookup table |
| NACE | Output determination | Check output types, procedures, and assignments |
| OVA8 | Credit check rules | Review automatic credit check configuration |
| FD32 | Customer credit data | Check credit limit and exposure |

---

## Section 4: SD-FI Integration Points -- Verified Facts

### 4.1 SD-FI Integration Point Catalog

Every SD transaction that creates (or does not create) an FI document:

| SD Transaction | Billing/Movement Type | FI Document Created | VKOA/OBYC Keys | Key Tables Updated |
|---------------|----------------------|--------------------|-----------------|--------------------|
| VF01/VF04 (standard invoice) | F2 | Yes | VKOA: ERL (Cr revenue), MWS (Cr tax), Dr Customer | VBRK, VBRP, BKPF, BSEG |
| VF01/VF04 (credit memo) | G2 | Yes | VKOA: ERL (Dr revenue), Cr Customer | VBRK, VBRP, BKPF, BSEG |
| VF01/VF04 (debit memo) | L2 | Yes | VKOA: ERL (Cr revenue), Dr Customer | VBRK, VBRP, BKPF, BSEG |
| VF01 (returns credit) | RE | Yes | VKOA: ERL (Dr revenue), Cr Customer | VBRK, VBRP, BKPF, BSEG |
| VF11 (cancel billing) | S1 | Yes — reverses original FI doc | Reverse of original | VBRK, VBRP, BKPF, BSEG |
| VF01 (pro forma) | F5 | **No FI posting** | None | VBRK, VBRP only |
| VF01 (invoice list) | LR | Yes | VKOA for invoice list items | VBRK, VBRP, BKPF, BSEG |
| VL02N (PGI — goods issue) | Mvt type 601 | Yes (via OBYC) | OBYC: GBB/VAX or VAY (Dr COGS), BSX (Cr Inventory) | MKPF, MSEG, LIPS, BKPF, BSEG |
| VL02N (PGI reversal) | Mvt type 602 | Yes — reverse of 601 | Reverse of GBB/BSX | MKPF, MSEG, LIPS, BKPF, BSEG |
| VL02N (returns GR) | Mvt type 651 | Yes | OBYC: BSX (Dr), GBB (Cr — reverses COGS) | MKPF, MSEG, LIPS, BKPF, BSEG |
| VF44/VF45 (rebate settlement) | Rebate credit memo | Yes | VKOA: ERS (Dr, reversing accrual), Cr Customer | VBRK, VBRP, BKPF, BSEG |
| VBO1 (rebate agreement creation) | — | **No FI posting** | None | KONA (rebate agreement) |
| VBOF (rebate batch settlement) | Multiple rebate CMs | Yes — multiple FI docs | Same as VF44/VF45 per agreement | Multiple VBRK/BKPF |
| Cash sale (VA01 CS) | F2 (auto) | Yes — immediate FI doc | VKOA: ERL, MWS; Dr Cash/Bank | VBAK, LIKP, VBRK, BKPF, BSEG |

**Key distinction: PGI vs Billing**
SD creates FI documents at TWO points in the O2C cycle:
1. **PGI (VL02N)** — COGS posting via OBYC (GBB/VAX or VAY for COGS debit, BSX for inventory credit). This is the cost side.
2. **Billing (VF01)** — Revenue posting via VKOA (ERL for revenue credit, customer debit). This is the revenue side.

The COGS posting uses OBYC (same framework as MM). The revenue posting uses VKOA (SD-specific framework). These are independent account determination mechanisms.

Confidence: HIGH (consistent with existing KB processes.md and fi/account-determination.md)

### 4.2 Transaction Trace: "What Happens in FI When I Post VF01?"

This is the specific success criterion from the phase description.

**Trigger:** Billing Clerk runs VF01 (single billing document) or VF04 (billing due list) referencing a delivery.

**Step 1: Billing Document Creation (SD Side)**
- System creates VBRK header: billing document number, billing type (F2), billing date, payer, net value
- System creates VBRP items: material, billing quantity, net value per item, condition amounts
- Billing type determined by copy control (VTFL: delivery type -> billing type)
- Pricing from the sales order is carried over or redetermined based on VTFL pricing type setting

**Step 2: Account Determination — VKOA Lookup (For Each Condition Type with Account Key)**
- System reads KNVV-KTGRD (customer account assignment group) from the payer's sales area data
- System reads MVKE-KTGRM (material account assignment group) from the material's sales org data
- For each active condition type step in the pricing procedure that has an account key:
  - **ERL (revenue):** CoA + Sales Org + KTGRD + KTGRM + ERL -> Revenue GL account
  - **ERS (discounts/deductions):** CoA + Sales Org + KTGRD + KTGRM + ERS -> Deduction GL account
  - **ERF (freight):** CoA + Sales Org + KTGRD + KTGRM + ERF -> Freight revenue GL account
  - **MWS (tax):** Tax code determines tax GL account (tax procedure drives this)

**Step 3: FI Document Creation (Automatic)**
- System creates BKPF header: FI document number, company code, document type RV (billing), posting date = billing date
- System creates BSEG line items:
  - **Line 1:** Dr Customer account (reconciliation account from KNB1-AKONT of the payer)
    - Amount: Total billing amount (including tax)
  - **Line 2:** Cr Revenue GL account (from VKOA ERL determination)
    - Amount: Net revenue (base price minus deductions, before tax)
  - **Line 3** (if discounts): Dr or Cr Sales Deduction GL account (from VKOA ERS determination)
    - Amount: Discount/deduction amount
  - **Line 4** (if freight): Cr Freight Revenue GL account (from VKOA ERF determination)
    - Amount: Freight charge amount
  - **Line 5:** Cr Output Tax GL account (from tax procedure / VKOA MWS)
    - Amount: Tax amount
- FI document always balances: total debits = total credits

**Step 4: Customer Open Item**
- The customer debit (Line 1) creates an open item in the AR sub-ledger
- Visible in FBL5N (customer line items)
- Picked up by dunning (F150) when overdue
- Cleared by incoming payment (F-28) or automatic clearing (F.13)
- Due date calculated from payment terms: KNVV-ZTERM (SD payment terms) or KNB1-ZTERM (FI payment terms)

**Step 5: Document Flow Update**
- VBFA (document flow table) updated: links billing document back to delivery and sales order
- The complete document flow is now traceable: VA01 -> VL01N -> VL02N (PGI) -> VF01 -> FI Doc

Confidence: HIGH (standard VF01 posting flow, consistent with existing processes.md and fi/account-determination.md)

### 4.3 Transaction Trace: "What Happens at PGI (VL02N) — The COGS Side"

PGI is the other major SD-FI handoff point. While billing creates the revenue posting, PGI creates the COGS posting.

**Trigger:** Shipping Clerk clicks "Post Goods Issue" in VL02N. Movement type 601.

**Step 1: Material Document Creation**
- MKPF header + MSEG line items created (same as any MIGO goods movement)
- Delivery status updated in LIPS (goods issue status = C)

**Step 2: OBYC Account Determination (Not VKOA)**
- System reads MBEW-BKLAS (valuation class) for the material at the delivering plant
- Transaction keys triggered:
  - **GBB/VAX** (Dr): COGS account — if no CO account assignment on the sales order
  - **GBB/VAY** (Dr): COGS account — if CO account assignment exists (WBS, internal order)
  - **BSX** (Cr): Inventory account

**Step 3: FI Document Creation**
- Dr COGS (from OBYC GBB/VAX or VAY)
- Cr Inventory (from OBYC BSX)
- Document type WA (goods issue)

Note: The COGS GL account comes from OBYC (GBB modifier VAX/VAY + valuation class), NOT from VKOA. VKOA handles the revenue side at billing. This is a critical distinction — COGS and revenue use different account determination frameworks.

Confidence: HIGH (consistent with existing processes.md Step 4 and mm-advanced.md OBYC tables)

### 4.4 Revenue Recognition — Moderate Depth

Per CONTEXT.md: moderate depth on revenue recognition, deferring complex POC to Phase 12.

**Basic Revenue Posting:**
Standard billing (VF01 with billing type F2) posts revenue immediately via VKOA ERL. No deferral — revenue recognized at billing date.

**Deferred Revenue Setup:**
For scenarios requiring revenue deferral (services rendered over time, subscription billing):
- Configure account key ERU (unbilled receivables / deferred revenue) in the pricing procedure
- VKOA maps ERU to a deferred revenue GL account (balance sheet liability)
- Periodic journal entry (manual or automated) reclassifies deferred revenue to earned revenue

**Milestone Billing:**
- Billing plan type in the sales order defines billing milestones (SPRO -> SD -> Billing -> Billing Plan -> Define Billing Plan Types)
- Each milestone triggers a billing document with a percentage of the total order value
- Revenue posts at each milestone billing event via standard VKOA (ERL)
- Milestone billing uses order-related billing (VTAF copy control, not VTFL)

**Billing Plan Types:**
- Periodic billing (e.g., monthly rental): Regular invoices at defined intervals
- Milestone billing (e.g., project milestones): Invoices triggered by milestone completion with percentage allocation

Confidence: MEDIUM (basic revenue posting and milestone billing are standard; deferred revenue setup varies significantly by implementation)

### 4.5 SD Period-End FI Impacts

**Rebate Settlement (VBO1/VBOF):**
- Rebate agreements created via VBO1 accrue rebate amounts during normal billing (RA00 condition type posts accrual)
- Period-end or agreement-end: run VF44 (partial settlement) or VF45 (final settlement) or VBOF (batch settlement)
- Settlement creates credit memos that reverse the accrual and credit the customer
- FI impact: Dr Rebate Accrual (liability reversal), Cr Customer (credit memo)

**Revenue Accruals:**
- For unbilled deliveries at period-end (PGI posted but billing not yet run)
- COGS is already posted (at PGI), but revenue is not yet recognized
- Manual accrual entry required: Dr Unbilled Receivables, Cr Accrued Revenue
- Reversed in the next period when billing runs

**Billing Due List Cleanup (VF04):**
- VF04 should be run before period-end close to ensure all deliveries due for billing are processed
- Any deliveries not billed create a revenue/COGS mismatch (COGS posted at PGI but revenue not yet posted)

**Credit Management Reset:**
- Period-end review of credit exposure via S_ALR_87012218 (or custom report)
- Review and release stale credit blocks via VKM1/VKM4/VKM5
- Credit limit adjustments via FD32 based on payment behavior

Confidence: MEDIUM (rebate settlement mechanics are standard; revenue accrual treatment is implementation-specific)

---

## Section 5: File Structure Decisions (Claude's Discretion)

### 5.1 Recommendation: Create sd-advanced.md (Parallel to mm-advanced.md)

**Recommendation:** YES, create `modules/sd/sd-advanced.md` to hold VKOA walkthrough, decision trees, and troubleshooting, paralleling the MM module structure.

**Rationale:**
- Maintains structural consistency across modules (fi-advanced.md, mm-advanced.md, sd-advanced.md)
- The SD CLAUDE.md file index already references integration.md and patterns.md; adding sd-advanced.md is the natural extension
- VKOA walkthrough, decision trees, and troubleshooting are module-internal concerns, not integration topics

**File allocation:**

| Content | File | Rationale |
|---------|------|-----------|
| VKOA walkthrough (dual-axis, worked examples, debugging) | modules/sd/sd-advanced.md (Section 1) | Account determination is SD-internal config; fi/account-determination.md has the framework intro; sd-advanced adds the full deep-dive |
| Decision trees (12 trees across pricing, copy control, partners, ATP, credit, etc.) | modules/sd/sd-advanced.md (Section 2) | Parallel to mm-advanced.md Section 2 |
| Troubleshooting (12 entries, symptom-first) | modules/sd/sd-advanced.md (Section 3) | Parallel to mm-advanced.md Section 3 |
| SD-FI integration point catalog + transaction traces | modules/sd/integration.md | This IS integration — belongs in the integration file |
| VF01 billing-to-FI trace | modules/sd/integration.md | Primary SD-FI handoff documentation |
| PGI COGS trace | modules/sd/integration.md | Secondary SD-FI handoff (cross-references mm-advanced.md OBYC) |
| Revenue recognition basics | modules/sd/integration.md | Revenue recognition is fundamentally an SD-FI boundary topic |
| Period-end FI impacts | modules/sd/integration.md | Period-end activities are SD-FI boundary processes |

### 5.2 Recommendation: VKOA First in sd-advanced.md

**Recommendation:** VKOA walkthrough first (Section 1), then decision trees (Section 2), then troubleshooting (Section 3).

**Rationale:** Mirrors mm-advanced.md structure exactly (OBYC first, decision trees second, troubleshooting third). Maintains cross-module navigability for users who know the MM structure.

### 5.3 Recommendation: Fold Common VKOA Misconfigurations into Troubleshooting

**Recommendation:** Do NOT create a separate "common VKOA misconfigurations" section. Instead, fold VKOA-specific issues into the troubleshooting section entries (Symptom 6: "Account determination error at billing" covers the VKOA misconfiguration cases).

**Rationale:** Keeps troubleshooting as the single lookup point for errors. A separate misconfiguration section would split the user's search path and duplicate content.

### 5.4 Recommendation: Intercompany at Foundation Level

**Recommendation:** Include intercompany billing in the VKOA worked examples at foundation level (Example 8), showing the two-document structure and the use of Cust AAG 03 for intercompany routing. Defer deep intercompany configuration (IV billing types, intercompany pricing, PI/PD condition types) to Phase 12 (solution patterns).

**Rationale:** Intercompany billing is complex enough for its own section but the CONTEXT.md specifies 8-10 examples with intercompany as one. A foundation-level example showing the dual-document structure and VKOA routing is sufficient for the account determination walkthrough.

---

## Section 6: Existing Content Dependencies and Cross-References

### 6.1 Content Already in Knowledge Base That Phase 8 Builds On

| File | What It Contains | How Phase 8 Uses It |
|------|-----------------|---------------------|
| fi/account-determination.md (Section 4) | VKOA framework: KOFI/KOFK, 5-level access sequence, key fields, account keys, diagnostic/setup paths | Phase 8 REFERENCES this (does not duplicate); adds pricing-to-VKOA chain, worked examples, debugging path |
| mm/mm-advanced.md | OBYC walkthrough, decision trees, troubleshooting — structural template | Phase 8 FOLLOWS this exact structure for sd-advanced.md |
| sd/config-spro.md | Pricing (V/06-V/09, OVKK), copy control (VTAA/VTLA/VTFL/VTAF), billing (VOFA), output (NACE), credit (OVA8), partner determination | Phase 8 decision trees provide DESIGN GUIDANCE for the config documented in config-spro.md |
| sd/processes.md | O2C process with FI posting notes at PGI and billing | Phase 8 integration.md provides the DETAILED traces that processes.md references |
| sd/master-data.md | KNVV-KTGRD, MVKE-KTGRM, KONH/KONP condition records | Phase 8 REFERENCES these fields in VKOA context |
| sd/tcodes.md | VF01/VF03/VF04, VKM1/VKM4/VKM5, V/08, VKOA, OVKK | Phase 8 REFERENCES these T-codes in debugging and troubleshooting |
| fi/fi-advanced.md Pitfall 7 | GR/IR account OI indicator requirement | Phase 8 notes same principle applies for AR reconciliation accounts |

### 6.2 Prior Decisions That Constrain Phase 8

From Phase 4 (04-01):
- VKOA section scoped to framework intro in Phase 4; Phase 8 owns the full VKOA deep-dive
- KOFI for FI account determination, KOFK for CO-PA (deferred to Phase 10)
- Cash discount GL accounts = OBXU/OBXI — must be consistent when discussing EVV account key

From Phase 7 (07-03):
- Credit management kept at foundation level with explicit deferral to Phase 8 for design guidance
- Condition technique documented once in Phase 7 Pricing section — Phase 8 references, does not re-explain
- Rebate foundation documented in Phase 7 — Phase 8 adds rebate settlement FI impacts

### 6.3 Files to Be Modified/Created

| File | Action | Content |
|------|--------|---------|
| modules/sd/sd-advanced.md | CREATE | VKOA walkthrough + 12 decision trees + 12 troubleshooting entries |
| modules/sd/integration.md | REPLACE placeholder | SD-FI integration point catalog + VF01 trace + PGI COGS trace + revenue recognition + period-end |
| modules/sd/CLAUDE.md | UPDATE | Add sd-advanced.md and update integration.md entries in File Index |

---

## Common Pitfalls for Content Authors

### Pitfall 1: Duplicating fi/account-determination.md VKOA Content
**What goes wrong:** Rewriting the VKOA framework, KOFI access sequence, and key field explanations
**Prevention:** sd-advanced.md should reference fi/account-determination.md for the framework and focus on the pricing-to-VKOA chain, worked examples, and debugging path

### Pitfall 2: Confusing VKOA (Revenue) with OBYC (COGS)
**What goes wrong:** Saying VKOA determines the COGS account
**Correct fact:** VKOA determines revenue, discount, freight, and tax GL accounts at BILLING. COGS is determined by OBYC (GBB/VAX or VAY) at PGI. These are independent account determination mechanisms at different points in the O2C cycle.

### Pitfall 3: Missing KTGRD/KTGRM as Root Cause
**What goes wrong:** Documenting VKOA errors without emphasizing that blank KTGRD (customer) or blank KTGRM (material) is the most common root cause
**Correct fact:** KTGRD (from KNVV Billing tab) and KTGRM (from MVKE Sales Org 2 view) are the #1 and #2 most common causes of VKOA failures. The CORRECTION blocks in master-data.md already flag these fields' locations.

### Pitfall 4: EVV Cash Discount Confusion with OBXI
**What goes wrong:** Presenting EVV as the only way cash discounts post to GL
**Correct fact:** Cash discount GL accounts can be determined by EVV (via VKOA) OR by OBXI (FI automatic posting). The choice depends on whether the implementation uses SD or FI to control the cash discount GL account. Many implementations use OBXI, not EVV. Document both paths.

### Pitfall 5: Treating Pro Forma Billing as FI-Relevant
**What goes wrong:** Including pro forma billing (F5, F8) in the SD-FI integration point catalog as creating FI documents
**Correct fact:** Pro forma billing creates VBRK/VBRP records but does NOT create FI documents. It is explicitly excluded from FI posting. The catalog must mark this correctly.

### Pitfall 6: Ignoring the PGI-Billing Revenue/COGS Timing Gap
**What goes wrong:** Not addressing the period-end scenario where PGI has posted COGS but billing has not yet posted revenue
**Correct fact:** This is a real period-end issue. At month-end, any deliveries with PGI posted but not yet billed create a COGS charge with no offsetting revenue. This must be addressed in the period-end section (manual accrual or VF04 cleanup).

---

## Open Questions

1. **Exact SAP message IDs for SD troubleshooting entries**
   - What we know: V1, V2, VF, VK message classes are correct; specific message numbers (e.g., V1 302 for incompletion) need verification
   - What's unclear: Exact message numbers for each troubleshooting scenario
   - Recommendation: Document the message CLASS and describe the symptom; include specific message numbers where verified. The pattern is more important than the exact number for a knowledge base.

2. **EVV Account Key Behavior vs OBXI**
   - What we know: EVV is a standard VKOA account key for cash discount; OBXI is the FI-side configuration for cash discount granted
   - What's unclear: Exact priority/interaction when both are configured; whether VKOA EVV overrides OBXI
   - Recommendation: Document both mechanisms; note that many implementations use OBXI rather than EVV; flag the interaction as implementation-specific

3. **ERU Account Key Usage Scope**
   - What we know: ERU is used for unbilled receivables and deferred revenue scenarios
   - What's unclear: Exact standard pricing procedures that use ERU; whether it requires custom configuration
   - Recommendation: Document at conceptual level; note that ERU is used in milestone billing and deferred revenue but specific configuration is implementation-dependent

4. **Intercompany Billing VKOA Configuration Depth**
   - What we know: Intercompany billing uses Cust AAG 03 (intercompany) for routing to intercompany GL accounts
   - What's unclear: Whether to include IV (intercompany) billing type condition types (PI/PD) in the worked example
   - Recommendation: Keep at foundation level per Section 5.4 recommendation; deep intercompany config defers to Phase 12

---

## Sources

### Primary (HIGH confidence -- existing knowledge base, verified in prior phases)
- modules/fi/account-determination.md Section 4 -- VKOA framework, KOFI access sequence, account keys, key fields
- modules/sd/config-spro.md -- Pricing (V/06-V/09, OVKK), copy control (VTAA/VTLA/VTFL/VTAF), billing (VOFA), output (NACE), credit (OVA8)
- modules/sd/processes.md -- O2C process with FI posting notes at PGI and billing steps
- modules/sd/master-data.md -- KNVV-KTGRD, MVKE-KTGRM field locations with CORRECTION blocks
- modules/sd/tcodes.md -- Complete SD T-code reference with pricing, billing, credit, output sections
- modules/mm/mm-advanced.md -- Structural template (OBYC walkthrough + 12 decision trees + 12 troubleshooting)
- modules/mm/integration.md -- Structural template for integration point catalog and transaction traces

### Secondary (MEDIUM confidence -- SAP standard knowledge, cross-verified with existing KB)
- VKOA account keys (ERL, ERS, EVV, ERF, MWS, ERU) -- standard SAP SD account determination, consistent with fi/account-determination.md
- Pricing-to-VKOA chain -- standard SAP architecture, derived from config-spro.md pricing section + fi/account-determination.md VKOA section
- Copy control fields (requirements, data transfer routines, pricing type) -- documented in config-spro.md Section 4
- Credit management configuration (OVA8, credit groups, static/dynamic checks) -- referenced in config-spro.md Section 8
- SD-FI integration points (billing types, movement types at PGI) -- derived from processes.md and tcodes.md

### Tertiary (LOW confidence -- training data, needs validation)
- Exact SAP message IDs (V1 xxx, VF xxx numbers) for specific troubleshooting scenarios
- EVV vs OBXI priority/interaction mechanics
- ERU account key standard configuration details
- Intercompany billing VKOA routing specifics (PI/PD condition types)
- Rebate settlement detailed FI posting mechanics (accrual reversal + credit memo creation flow)

---

## Metadata

**Confidence breakdown:**
- VKOA framework extension (pricing-to-VKOA chain, account keys): HIGH -- builds directly on verified fi/account-determination.md content
- VKOA worked examples (standard revenue, tax, discounts, freight, credit memo): HIGH -- standard VKOA patterns
- VKOA worked examples (cash discount EVV, rebate accrual, intercompany): MEDIUM -- implementation-specific variations
- Decision tree topics: HIGH -- covers standard SD configuration areas from config-spro.md
- Troubleshooting patterns: MEDIUM-HIGH -- symptom patterns are standard; specific message IDs need validation
- SD-FI integration points: HIGH -- consistent with existing KB processes.md and fi/account-determination.md
- VF01 billing-to-FI trace: HIGH -- standard VF01 posting flow
- Revenue recognition: MEDIUM -- basic patterns are standard; deferred revenue varies by implementation
- Period-end impacts: MEDIUM -- rebate settlement standard; revenue accrual treatment is implementation-specific

**Research date:** 2026-02-17
**Valid until:** Stable -- ECC 6.0 SD account determination and integration patterns do not change. Review only if knowledge base scope extends to complex revenue recognition (POC) or deep intercompany billing.
