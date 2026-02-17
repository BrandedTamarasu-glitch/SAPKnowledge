---
module: sd
content_type: decision-trees-and-troubleshooting
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Sales & Distribution — VKOA Walkthrough, Decision Trees & Troubleshooting

> ECC 6.0 reference. VKOA account determination walkthrough covers the SD-side perspective on billing document to GL account mapping. Decision trees guide SD configuration choices. Troubleshooting covers symptom-based diagnosis of common SD issues. For the VKOA framework and FI-side overview (KOFI access sequence, key fields, account keys), see `modules/fi/account-determination.md`.

---

## 1. VKOA Account Determination — SD Perspective

The VKOA framework for SD revenue account determination is documented in `modules/fi/account-determination.md` (Section 4), which covers: KOFI vs KOFK condition types, the 5-level KOFI00 access sequence, key fields (KTGRD, KTGRM, account key), and the diagnostic/setup paths for navigating VKOA.

This section adds the SD-side perspective:
- **Dual-axis navigation** — reference tables organized by account key AND by condition type, with cross-references between the two axes
- **Pricing-to-VKOA chain** — the full end-to-end path from pricing procedure configuration through VKOA to GL account
- **Worked billing-to-GL examples** — 8 scenarios with complete Dr/Cr entries
- **VKOA debugging path** — 5-step diagnostic process specific to billing document analysis

---

### 1a. Dual-Axis Reference — By Account Key

Each VKOA account key maps one or more condition types to a category of GL posting. The table below lists all standard account keys, what they post, which condition types typically carry them, and when the posting fires.

| Account Key | What It Posts | Typical Condition Types | When It Fires | GL Account Category |
|-------------|---------------|------------------------|---------------|---------------------|
| ERL | Revenue (base) | PR00 (base price), net revenue condition types | At billing (VF01/VF04) | Revenue GL accounts (e.g., 800000 domestic, 810000 export — representative example) |
| ERS | Sales deductions / discounts | K004, K005, K007 (discounts), RA00 (rebate accrual) | At billing | Discount/allowance GL accounts |
| EVV | Cash discount (Skonto) | Not a condition type — derived from payment terms | At payment clearing (F-28/F.13), NOT at billing | Cash discount expense GL account |
| ERF | Freight revenue | KF00 (freight), other freight condition types | At billing | Freight revenue GL account |
| ERU | Unbilled receivables / accruals | Used in milestone billing and deferred revenue | At billing (for deferred revenue scenarios) | Accrual/deferred revenue GL account |
| MWS | Output tax (VAT/sales tax) | MWST (output tax condition type) | At billing | Tax GL accounts (output tax payable) |

**Key behavioral notes:**

- **ERL** is the primary revenue key. PR00 (base price) carries ERL, and VKOA resolves ERL to the revenue GL account based on the KOFI access sequence. The combination of KTGRD + KTGRM determines which specific revenue GL account is used (e.g., domestic vs export revenue).

- **ERS** covers all sales deductions that reduce revenue: material discounts, customer discounts, rebate accruals. Different condition types with ERS can post to the same or different GL accounts depending on VKOA table granularity. If VKOA table 1 has separate entries for ERS with different KTGRD/KTGRM combinations, each discount posts to a different GL account.

- **EVV** (cash discount/Skonto) behaves differently from all other keys: it posts at **payment clearing time**, not at billing time. When the customer takes a cash discount during payment (F-28 or automatic clearing F.13), the discount amount posts to the EVV GL account. Many implementations use **OBXI** (FI automatic posting for cash discount granted, at SPRO > Financial Accounting > Accounts Receivable and Accounts Payable > Business Transactions > Incoming Payments > Incoming Payments Global Settings > Define Accounts for Cash Discount Granted) rather than VKOA EVV to determine the cash discount GL account. Both mechanisms achieve the same result; the choice is implementation-specific. See `modules/fi/account-determination.md` Section 5b for OBXI documentation.

- **MWS** is determined by the tax condition type (MWST). The tax GL account is typically driven by the tax code from the tax procedure, though VKOA can also provide the account. In most implementations, the tax procedure determines the tax rate and the tax GL account simultaneously.

---

### 1b. Dual-Axis Reference — By Condition Type

This table is organized by condition type, showing which account key each carries and the GL impact at billing time.

| Condition Type | Description | Account Key | GL Impact at Billing | Notes |
|----------------|-------------|-------------|---------------------|-------|
| PR00 | Base price | ERL | Cr Revenue | Primary revenue posting |
| K004 | Material discount | ERS | Dr Sales Deductions (reduces net revenue) | Percentage or fixed amount per material |
| K005 | Customer-specific discount | ERS | Dr Sales Deductions | Per customer-material combination |
| K007 | Material group discount | ERS | Dr Sales Deductions | Per customer-material group |
| KF00 | Freight | ERF | Cr Freight Revenue | Separate revenue line for freight |
| MWST | Output tax | MWS | Cr Output Tax Payable | Tax code determines rate; VKOA determines GL |
| RA00 | Rebate accrual | ERS | Dr Rebate Expense / Cr Rebate Accrual | Statistical at billing; settled via VF44/VF45 |
| RA01 | Rebate accrual (alternative) | ERS | Same as RA00 | Alternative rebate condition type |

**Note:** The account key assignment is configured in the pricing procedure (V/09) at each condition type step, and/or in the condition type definition (V/08) at the AcctKey field. The pricing procedure assignment takes precedence if both exist.

---

### 1c. Pricing-to-VKOA Chain

This is the complete end-to-end chain from pricing procedure configuration through VKOA to GL account — the #1 question SD consultants ask about account determination.

```
Step 1: Pricing Procedure (V/09)
        Defines the calculation schema: which condition types apply, in what order
        Each step has an AcctKey column that assigns the account key to the condition type
        Example: Step 900, Condition Type PR00, AcctKey = ERL (revenue)
                 Step 910, Condition Type K004, AcctKey = ERS (sales deduction)
                 Step 920, Condition Type MWST, AcctKey = MWS (tax)

Step 2: Condition Type Configuration (V/08)
        Each condition type has an AcctKey field (Acct. key column)
        Links the condition type to the VKOA account key
        The pricing procedure AcctKey can override the V/08 AcctKey

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
        Table 2: CoA + Sales Org + Cust AAG + Account Key
        Table 3: CoA + Sales Org + Mat AAG + Account Key
        Table 4: CoA + Sales Org + Account Key
        Table 5: CoA + Account Key (catch-all)

Step 6: FI Document Creation
        GL accounts from VKOA populate the BSEG line items:
        - Revenue line: GL from ERL determination
        - Discount line(s): GL from ERS determination
        - Freight line: GL from ERF determination
        - Tax line: GL from MWS determination
        - Customer line: Reconciliation account from KNB1-AKONT (NOT from VKOA)
```

**Key design principle:** The combination of KTGRD (customer account assignment group from KNVV) and KTGRM (material account assignment group from MVKE) is the primary driver. Two billing documents for different customer/material AAG combinations post to different GL accounts even when using the same account key. This is how SAP separates domestic revenue from export revenue, or finished goods revenue from service revenue.

---

### 1d. Worked Examples — Billing-to-GL

The VKOA framework and access sequence overview are documented in `modules/fi/account-determination.md`. The examples below provide detailed billing-to-GL worked scenarios showing the complete Dr/Cr entries for each billing scenario.

For each example: scenario description, then Dr/Cr table with representative example account numbers.

---

**Example 1: Standard Revenue (ERL) — Domestic Sale**

Scenario: Standard billing document (F2) for domestic customer. Material "PUMP-100" (KTGRM 01 = finished goods), customer (KTGRD 01 = domestic). PR00 base price = 10,000 EUR.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Customer Reconciliation — representative example) | 10,000.00 | Dr | KNB1-AKONT of the payer |
| 800000 (Domestic Revenue — representative example) | 10,000.00 | Cr | VKOA: CoA + Sales Org 1000 + KTGRD 01 + KTGRM 01 + ERL -> GL 800000 |

---

**Example 2: Revenue with Tax (ERL + MWS) — Taxable Sale**

Scenario: Same as Example 1 with 19% output tax (MWST condition type). Two VKOA lookups: ERL for revenue, MWS for tax.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Customer Reconciliation — representative example) | 11,900.00 | Dr | KNB1-AKONT (gross amount including tax) |
| 800000 (Domestic Revenue — representative example) | 10,000.00 | Cr | VKOA: ERL determination |
| 175000 (Output Tax Payable — representative example) | 1,900.00 | Cr | VKOA: MWS determination (tax code drives rate) |

---

**Example 3: Sales Deductions (ERS) — Material Discount**

Scenario: Billing with K004 (material discount 5%) active. PR00 = 10,000 EUR, K004 = -500 EUR. K004 carries ERS account key.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Customer Reconciliation — representative example) | 9,500.00 | Dr | KNB1-AKONT (net of discount) |
| 800000 (Domestic Revenue — representative example) | 10,000.00 | Cr | VKOA: ERL (gross revenue) |
| 850000 (Sales Deductions — representative example) | 500.00 | Dr | VKOA: CoA + Sales Org + KTGRD + KTGRM + ERS -> GL 850000 |

**Note:** The gross/net presentation depends on VKOA configuration. In some implementations, revenue posts net and no separate deduction account is used. The example above shows gross revenue with separate deduction posting, which provides visibility into discount amounts in FI reporting.

---

**Example 4: Cash Discount (EVV) — Payment with Discount**

Scenario: Customer pays within 2% discount period. Invoice was 10,000 EUR. Payment terms: 2% 10 days net 30.

At billing (VF01):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Customer Reconciliation — representative example) | 10,000.00 | Dr | KNB1-AKONT |
| 800000 (Revenue — representative example) | 10,000.00 | Cr | VKOA: ERL |

At payment (F-28 or F.13):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 113100 (Bank — representative example) | 9,800.00 | Dr | Incoming payment |
| 860000 (Cash Discount Expense — representative example) | 200.00 | Dr | EVV GL account from VKOA, OR OBXI configuration |
| 140000 (Customer Reconciliation — representative example) | 10,000.00 | Cr | Clears customer open item |

> **CRITICAL:** EVV posts at payment clearing time, NOT at billing time. The billing document does not show the cash discount. The discount only materializes when the customer pays within the discount period. Many implementations use OBXI (FI automatic posting configuration at SPRO > Financial Accounting > AR/AP > Business Transactions > Incoming Payments > Incoming Payments Global Settings > Define Accounts for Cash Discount Granted) rather than VKOA EVV to determine the cash discount GL account. Both mechanisms achieve the same result; the choice is implementation-specific. See `modules/fi/account-determination.md` Section 5b for OBXI documentation.

---

**Example 5: Freight Revenue (ERF) — Freight Charge**

Scenario: Billing with KF00 (freight 500 EUR). KF00 carries ERF account key.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Customer Reconciliation — representative example) | 10,500.00 | Dr | Net product revenue + freight |
| 800000 (Revenue — representative example) | 10,000.00 | Cr | VKOA: ERL |
| 820000 (Freight Revenue — representative example) | 500.00 | Cr | VKOA: CoA + Sales Org + KTGRD + KTGRM + ERF -> GL 820000 |

**Note:** Freight revenue posts to a separate GL account from product revenue because ERF and ERL map to different VKOA entries. This allows FI reporting to distinguish product revenue from freight revenue.

---

**Example 6: Credit Memo**

Scenario: Credit memo (billing type G2) from a credit memo request (VA01 doc type CR). Original invoice was for 5,000 EUR. VKOA runs the same determination but posts Dr/Cr in opposite direction.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 800000 (Revenue — representative example) | 5,000.00 | Dr | VKOA: ERL (same GL account as original billing, reverse side) |
| 140000 (Customer Reconciliation — representative example) | 5,000.00 | Cr | KNB1-AKONT (reduces customer balance) |

**Note:** The VKOA determination for a credit memo uses the same account key (ERL) and the same KTGRD/KTGRM combination as the original billing. The billing type (G2 vs F2) does not change the GL account — only the Dr/Cr direction reverses.

---

**Example 7: Rebate Accrual (RA00/ERS)**

Scenario: Standard billing with rebate accrual. RA00 condition type with ERS account key accrues 2% rebate on 10,000 EUR billing.

At billing (accrual):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 860100 (Rebate Expense — representative example) | 200.00 | Dr | VKOA: ERS (rebate accrual posting) |
| 240000 (Rebate Accrual Liability — representative example) | 200.00 | Cr | VKOA: ERS provision account |

At settlement (VF44/VF45):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 240000 (Rebate Accrual Liability — representative example) | 200.00 | Dr | Reverses accrual |
| 140000 (Customer Reconciliation — representative example) | 200.00 | Cr | Credit memo to customer |

**Note:** The rebate accrual posts during every billing run (RA00 condition type accumulates). At settlement, the accrual is reversed and a credit memo is created for the customer. The settlement process uses VF44 (partial), VF45 (final), or VBOF (batch settlement).

---

**Example 8: Intercompany Billing (Foundation Level)**

Scenario: Company code 1000 (selling CC) takes the customer order. Company code 2000 (delivering CC) ships the goods. Two billing documents are created.

External billing (VF01 — invoice to customer):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Customer Reconciliation, CC 1000 — representative example) | 10,000.00 | Dr | Standard customer billing |
| 800000 (Revenue, CC 1000 — representative example) | 10,000.00 | Cr | VKOA: ERL (selling CC books revenue) |

Intercompany billing (IV billing type):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 196000 (IC Receivable, CC 2000 — representative example) | 8,000.00 | Dr | Delivering CC recovers cost + margin |
| 196000 (IC Payable, CC 1000 — representative example) | 8,000.00 | Cr | Selling CC recognizes intercompany cost |

**Note:** Intercompany billing uses Customer Account Assignment Group 03 (intercompany) on the internal customer master to route VKOA to intercompany-specific GL accounts. The intercompany price (PI/PD condition types) is typically lower than the external customer price. Deep intercompany configuration (IV billing types, PI/PD conditions, intercompany pricing) defers to Phase 12 (Solution Design Intelligence).

---

### 1e. VKOA Debugging Path

When billing documents post to wrong GL accounts or fail to create FI documents, follow this 5-step diagnostic path.

**Step 1: Analyze the billing document (VF03)**

- Open VF03 -> Environment -> Accounting Document (or Account Determination Analysis)
- Review the FI document number and GL accounts posted
- If no FI document created: check for billing block, or check if billing type is pro forma (F5/F8 — pro forma does NOT create FI documents)

**Step 2: Check VKOA simulation**

- T-code VKOA -> select KOFI -> navigate to the relevant condition table
- Enter: Chart of Accounts + Sales Org + Customer AAG (from KNVV-KTGRD) + Material AAG (from MVKE-KTGRM) + Account Key
- If no entry found: this is the missing configuration. Check table 5 (CoA + Account Key) as catch-all fallback

**Step 3: Verify account key assignment**

- Check pricing procedure (V/09): is the AcctKey column populated for the condition type step?
- Check condition type (V/08): does the AcctKey field have a value?
- If no account key on either: the condition type's value will not post separately to FI — it is absorbed into the net amount of the parent subtotal

**Step 4: Verify customer and material account assignment groups**

- Customer: XD03 or VD03 -> Billing tab -> KTGRD (customer account assignment group)
- Material: MM03 -> Sales Org 2 view -> KTGRM (material account assignment group)
- If blank or wrong: VKOA lookup uses the wrong access sequence level or fails entirely

> **CRITICAL:** KTGRD blank on customer master is the #1 VKOA failure cause — it is routinely overlooked during customer creation because KTGRD is on the Billing tab of KNVV, not on the obvious General or Address screens. KTGRM blank on material master is #2 — it requires the Sales Org 2 view to be maintained in MM01/MM02. See CORRECTION blocks in `modules/sd/master-data.md` for exact field locations.

**Step 5: Check common failure points**

- Missing VKOA entry for the specific account key + AAG combination (most common)
- KTGRD blank on customer master (#1 root cause)
- KTGRM blank on material master (#2 root cause)
- OVKK entry missing (no pricing procedure -> no account keys -> no VKOA determination)
- Wrong chart of accounts in VKOA (multi-company-code setup with different charts of accounts)
- Condition type without account key assignment (value absorbed into net, not posted separately)

> **Quick check tip:** Most VKOA errors come from Steps 2 and 4 — either a missing VKOA table entry or a blank KTGRD/KTGRM on the master data. Before running traces or debugging ABAP, always check the customer master Billing tab (KTGRD) and material master Sales Org 2 view (KTGRM) first.

---

## Configuration Decision Trees

> Each decision tree has two parts: (1) Q&A routing -- answer questions to reach the recommended approach, then (2) a comparison table with config implications and trade-offs. Decision trees include config paths inline (not just pointers to config-spro.md).

### Decision Tree 1: Pricing Procedure Design

**Q&A Routing:**

- **Q1:** What pricing elements does the business need? (base price, discounts, surcharges, freight, tax, rebates) -> List the elements; each becomes a condition type step in the pricing procedure.
- **Q2:** Are discounts calculated as percentage of base price, net price, or specific subtotals? -> This determines the From/To step references and subtotal fields (KOMP) in V/09.
- **Q3:** Do you need manual pricing overrides at order entry? -> If yes, set the Manual indicator on condition type steps that allow user override. If no, leave Manual blank for system-determined prices.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Copy SAP standard (RVAA01) and modify | First implementation; standard pricing needs | V/09: copy RVAA01 to Z-procedure; modify steps | Fast start; SAP-tested baseline; may include unneeded condition types that cause confusion |
| Build from scratch | Complex pricing; multi-tier discounts; non-standard requirements | V/09: create new procedure; define all steps, subtotals, requirements | Full control; no inherited complexity; more design effort; must define all subtotals manually |
| Multiple pricing procedures | Different business lines need different pricing logic | OVKK routes by sales area + doc pricing proc (VOV8) + cust pricing proc (KNVV-KALKS) | Supports diverse business models; higher maintenance; must maintain OVKK entries for all combinations |

---

### Decision Tree 2: Access Sequence Strategy

**Q&A Routing:**

- **Q1:** For a given condition type, how many levels of specificity does the business need? -> Example for PR00 (base price): customer+material (most specific), price list+material, material+sales org (most general). Each level = one condition table in the access sequence.
- **Q2:** Should the first match end the search (exclusive) or should all matches apply? -> Exclusive = first hit wins (standard for prices). Non-exclusive = all matches accumulate (standard for some discount types).
- **Q3:** How many condition tables do you need? -> 2-4 tables is typical. More than 5 = performance concern and maintenance overhead.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| 2 tables (customer+material, material) | Simple pricing; limited customer-specific prices | V/07: 2 accesses; V/06: 2 tables | Fastest condition record search; limited flexibility; fewer condition records to maintain |
| 3-4 tables (customer+material, price list+material, material group, material) | Standard pricing with customer-specific and list price tiers | V/07: 3-4 accesses with exclusive indicator; V/06: corresponding tables | Good balance of flexibility and performance; covers most pricing scenarios |
| 5+ tables (highly specific to very general) | Complex hierarchical pricing with many override levels | V/07: 5+ accesses; V/06: 5+ tables | Maximum flexibility; more condition records; slower access sequence search; harder to troubleshoot which record was found |

---

### Decision Tree 3: Condition Exclusion Groups

**Q&A Routing:**

- **Q1:** When multiple discounts apply to the same order line, should the customer get the best single discount or all discounts combined? -> Best single = exclusion group needed. All combined = no exclusion needed.
- **Q2:** Which condition types compete against each other? -> Group competing condition types into the same exclusion group (e.g., K004, K005, K007 all in group 0001).
- **Q3:** What is the "best" criterion? -> Most common: best discount rate (%). Can also be: best absolute amount, or custom ABAP routine.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No exclusion groups | All discounts stack / accumulate | Default -- no config needed | Simplest; customer gets all applicable discounts; may result in excessive discounting |
| Best-of-N (single group) | Customer gets the single best discount from competing types | V/09: assign exclusion group to competing condition type steps; configure "best price" determination | Controls discounting; customer gets optimal single discount; requires careful grouping |
| Multiple exclusion groups | Different sets of discounts compete independently | V/09: multiple exclusion groups; each group determines its own best discount | Fine-grained control; complex to maintain; must understand which groups interact |

---

### Decision Tree 4: Pricing Determination Assignment (OVKK)

**Q&A Routing:**

- **Q1:** How many distinct pricing procedures does the business need? -> One procedure per significantly different pricing model (e.g., domestic vs export, standard vs intercompany).
- **Q2:** What drives the procedure selection? -> Customer type (KNVV-KALKS customer pricing procedure), document type (VOV8 document pricing procedure), or both?
- **Q3:** Do you need sales-area-specific pricing procedures? -> If yes, the sales area key in OVKK differentiates. If no, one OVKK entry per doc/customer pricing procedure combination suffices.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Single pricing procedure for all | Simple business; uniform pricing across customers and document types | OVKK: one entry with blank sales area; one Z-procedure | Simplest; one procedure to maintain; cannot differentiate pricing logic by customer type or document type |
| Differentiate by customer pricing procedure | Different customer types need different pricing (e.g., wholesale vs retail) | KNVV-KALKS: assign different cust pricing procs; OVKK: entries per cust proc | Customer-driven pricing differentiation; must set KALKS correctly on every customer master |
| Differentiate by document pricing procedure | Different document types need different pricing (e.g., standard vs returns vs intercompany) | VOV8: assign different doc pricing procs per doc type; OVKK: entries per doc proc | Document-driven differentiation; useful when returns or intercompany use different pricing logic |
| Full matrix (sales area + doc proc + cust proc) | Large enterprise with diverse pricing models per region, customer type, and document type | OVKK: entries for each sales area + doc proc + cust proc combination | Maximum flexibility; high maintenance; risk of missing OVKK entries for new combinations |

---

### Decision Tree 5: Copy Control Design

**Q&A Routing:**

- **Q1:** Is this delivery-related billing (VTFL: delivery -> invoice) or order-related billing (VTAF: order -> invoice)? -> Delivery-related = most common (standard O2C). Order-related = third-party, credit memo request, milestone billing.
- **Q2:** Should pricing be recalculated at copy? -> B = carry over and redetermine (standard); C = copy pricing unchanged; D = redetermine from scratch; G = copy and redetermine freight only.
- **Q3:** Do you need custom requirements (ABAP routines) to control WHEN copying is allowed? -> Standard requirements (001 header, 002 item) cover most scenarios. Custom requirements for business-specific rules (e.g., block billing if quality check pending).

**Comparison Table:**

| Copy Control | T-code | Common Scenarios | Key Settings |
|--------------|--------|-----------------|--------------|
| VTAA (Order -> Order) | VTAA | Quotation -> Order, Contract -> Release order, Returns -> Credit memo request | Pricing type B (redetermine); requirement 001 (header has items) |
| VTLA (Order -> Delivery) | VTLA | Sales order -> Outbound delivery | Delivery qty from order schedule line; partial delivery allowed flag |
| VTFL (Delivery -> Billing) | VTFL | Delivery -> Invoice (MOST COMMON) | Pricing type B or C; billing qty = E (from delivery); requirement 002 (complete reference) |
| VTAF (Order -> Billing) | VTAF | Credit memo request -> Credit memo, Third-party -> Invoice, Milestone billing | Pricing type C (copy pricing); order-related billing relevance |

> **CRITICAL:** Always check BOTH header and item level in copy control. Item-level settings control the actual data transfer for each line item. Missing item-level copy control = "no data available for billing" error even when header-level exists.

---

### Decision Tree 6: Partner Determination

**Q&A Routing:**

- **Q1:** Which partner functions are mandatory for your document types? -> At minimum: AG (sold-to), WE (ship-to), RE (bill-to), RG (payer). Add VE (sales rep) if commission tracking needed.
- **Q2:** Should partner functions be defaulted from customer master or entered manually? -> Customer master KNVP provides defaults; manual override possible at document level.
- **Q3:** Do you need custom partner functions? -> Standard SAP covers most scenarios. Custom needed for: second ship-to, broker, freight forwarder, etc.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Standard 4 partners (AG/WE/RE/RG) | Simple business; sold-to = ship-to = bill-to = payer | Partner determination procedure with 4 mandatory functions; assign to doc type | Minimal data entry; covers single-entity customers |
| Standard 4 + sales rep (VE) | Need commission tracking or sales rep assignment | Add VE to procedure; maintain KNVP partner records for VE | Enables commission reports; requires KNVP maintenance for VE assignments |
| Extended (custom partner functions) | Multi-party scenarios: brokers, freight forwarders, end users | Custom partner function types; extend partner determination procedure | Handles complex scenarios; more data entry; must maintain additional KNVP records |

---

### Decision Tree 7: Availability Check (ATP)

**Q&A Routing:**

- **Q1:** What stock types should be included in availability? -> Unrestricted only (conservative) or also quality inspection, blocked, in-transit?
- **Q2:** What supply elements should be included? -> POs, production orders, planned orders, purchase requisitions? More supply = more optimistic promises.
- **Q3:** Should the check be active at order, delivery, or both? -> Order check = customer gets confirmation at order time. Delivery check = final check before shipping.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No ATP check | MTO environment; always produce to order; or low-value items | MARC-MTVFP blank; or checking rule blank in VOV8 | No stock check overhead; no confirmed dates; risk of over-promising |
| Conservative (unrestricted stock + confirmed POs only) | Customer promises must be reliable; safety stock is maintained | OVZ2: checking group includes unrestricted only; supply = only firm POs | Most accurate promises; may under-confirm when planned supply is reliable |
| Standard (unrestricted + all supply elements) | Balanced approach for most implementations | OVZ2: checking group includes unrestricted + QI stock; supply = POs + production orders + planned orders | Good balance; may confirm based on planned orders that don't materialize |
| Aggressive (include all stock types + all supply + planned receipts) | Maximize order confirmation; backlog management post-sale | OVZ2: include all stock types and all supply elements | Maximum confirmation; risk of over-promising; requires strong supply chain discipline |

---

### Decision Tree 8: Output Determination

**Q&A Routing:**

- **Q1:** What output documents does the business need? -> Order confirmation, delivery note, invoice, packing list, shipping label. Each = one output type in NACE.
- **Q2:** What medium? -> Print, fax, EDI, email (SAPconnect). Can differ by customer or document type.
- **Q3:** When should output be sent? -> Immediately at save, batch (scheduled job), or manually triggered.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Standard output types (BA00, LD00, RD00) | Default documents; standard SAP forms | NACE: assign standard output types to determination procedure; assign procedure to doc type | Fast setup; SAP-provided forms; limited customization |
| Custom output types with SAPscript/Smart Forms | Custom document layout required | NACE: create Z-output types; assign custom SAPscript or Smart Form; maintain condition records | Full layout control; requires ABAP/form development |
| EDI/email output | Electronic document exchange | NACE: output type with medium 5 (EDI) or 7 (email); configure SAPconnect (SCOT) | Eliminates paper; requires technical setup; partner-specific output records |

> **S/4HANA Note:** S/4HANA replaces NACE with BRF+ output management. All guidance above is ECC 6.0.

---

### Decision Tree 9: Credit Management Design

**Q&A Routing:**

- **Q1:** Do you need automatic credit checking? -> Most implementations = yes. If no (e.g., all prepaid customers), skip credit management.
- **Q2:** At which points should credit be checked? -> Order creation (credit group 01), delivery creation (credit group 02), goods issue (credit group 03). Most implementations check at order + delivery.
- **Q3:** Static check only (credit limit vs total receivables) or dynamic check (include open orders, deliveries, billing docs in exposure)? -> Dynamic is recommended for most implementations.

**Comparison Table:**

| Check Type | What It Compares | Config Path | Trade-offs |
|-----------|-----------------|-------------|------------|
| Static only | Credit limit (FD32) vs total receivables (KNKK-SKFOR) | OVA8: static check rule; credit groups in VOV8 | Simple; misses exposure from open orders/deliveries; may allow over-limit |
| Dynamic | Credit limit vs total exposure (open items + open orders + open deliveries + unbilled) | OVA8: dynamic check rule with horizon period; credit groups in VOV8 | Comprehensive exposure view; most accurate; slightly more complex to configure horizon |
| Dynamic + max document value | Dynamic check PLUS single-document ceiling | OVA8: combined rule (dynamic + max document value) | Catches both cumulative over-exposure and individual large orders; recommended for most implementations |

Credit block release workflow: VKM1 (order blocks), VKM4 (delivery blocks), VKM5 (GI blocks). Credit analyst reviews and releases or escalates.

---

### Decision Tree 10: Item Category Determination

**Q&A Routing:**

- **Q1:** Are all your materials standard tangible goods? -> If yes, standard item category TAN with MTPOS = NORM covers most scenarios. If no, continue.
- **Q2:** Do you have service items, text items, free goods, or third-party items? -> Each needs a specific MTPOS: blank/NORM (standard), BANS (third-party), LUMP (value item), TAX (text item).
- **Q3:** Do you need custom item categories? -> Standard categories (TAN, TANN, TAS, TAX, REN, KBN, KEN) cover most scenarios. Custom only for business-specific behavior (e.g., custom billing relevance, custom pricing behavior).

**Comparison Table:**

| MTPOS Value | Item Category Proposed | When to Use | Config Path |
|-------------|----------------------|-------------|-------------|
| NORM | TAN (standard) | Standard tangible goods with delivery and billing | Default in OVLP for OR + NORM |
| BANS | TAS (third-party) | Vendor ships directly to customer; no delivery in SD | OVLP: OR + BANS -> TAS; triggers auto PR creation |
| LUMP | TAP (lump sum) | Value-based items without quantity | OVLP: OR + LUMP -> TAP |
| (blank) | Depends on doc type | If MTPOS is blank, determination uses doc type default | OVLP: check entry with blank MTPOS |
| NORM + usage FREE | TANN (free of charge) | Free goods in same order as charged goods | OVLP: OR + NORM + FREE -> TANN |

> **CRITICAL:** The item category group (MTPOS) comes from **MVKE** (material Sales Org 1 view), NOT from the document type or order data. Missing MTPOS on the material master is the #1 cause of "item category not found" errors. See `modules/sd/master-data.md` for the MVKE field reference.

---

### Decision Tree 11: Billing Type Selection

**Q&A Routing:**

- **Q1:** Is billing based on delivery (delivery-related) or based on the sales order directly (order-related)? -> Delivery-related (VTFL copy control) = most common for physical goods. Order-related (VTAF) = services, third-party, credit/debit memos.
- **Q2:** Is this a standard invoice, credit memo, debit memo, or cancellation? -> Each has a specific billing type: F2/G2/L2/S1.
- **Q3:** Do you need invoice lists (consolidated invoicing)? -> If yes, billing type LR combines multiple billing documents for one payer.

**Comparison Table:**

| Billing Type | Description | Billing Relevance | When to Use | FI Impact |
|-------------|-------------|------------------|-------------|-----------|
| F2 | Standard invoice | A (delivery-related) | Normal O2C; delivery-based billing | Dr Customer / Cr Revenue |
| G2 | Credit memo | B (order-related) | Credit memo request -> credit; returns | Dr Revenue / Cr Customer |
| L2 | Debit memo | B (order-related) | Additional charge to customer | Dr Customer / Cr Revenue |
| RE | Returns credit | A (delivery-related) | Returns delivery -> credit | Dr Revenue / Cr Customer |
| S1 | Cancellation | -- | Cancel existing billing document (VF11) | Reverses original FI document |
| F5 | Pro forma | -- | Quotation docs, customs paperwork | **No FI posting** |
| LR | Invoice list | -- | Consolidated invoicing per payer per period | Aggregated FI posting |

---

### Decision Tree 12: Incompletion Procedure Design

**Q&A Routing:**

- **Q1:** Which fields must be filled before the document can be saved? -> Mandatory fields get Error status. Fields that should be filled but don't block save get Warning status.
- **Q2:** Do header, item, schedule line, and partner data need different incompletion rules? -> Yes -- configure separate procedures for each level. Assign all four to the document type.
- **Q3:** Should incompletion block further processing (delivery, billing) or just flag the document? -> Configure the incompletion log to block processing if critical fields are missing, or allow processing with warnings.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Minimal (PO number, payment terms, shipping condition) | Fast order entry; minimal mandatory fields | V_20: assign procedure to doc type; OVA2: define procedure with few Error-status fields | Fastest order entry; risk of incomplete documents reaching delivery/billing |
| Standard (PO number, payment terms, incoterms, shipping condition, partner functions) | Balanced approach for most implementations | OVA2: define procedure with standard mandatory fields at header and item | Good data quality; reasonable entry overhead; catches common omissions |
| Strict (all business-critical fields mandatory at order entry) | Regulated industry; zero-tolerance for incomplete data | OVA2: extensive mandatory fields with Error status; consider separate strict procedures for different doc types | Highest data quality; may slow order entry; requires all data available at order creation time |

> **Best practice:** Start with Standard approach. Add fields incrementally based on downstream processing failures (e.g., if delivery creation frequently fails due to missing shipping condition, make it mandatory in the incompletion procedure).
