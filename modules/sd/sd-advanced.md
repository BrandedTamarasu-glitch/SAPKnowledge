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
