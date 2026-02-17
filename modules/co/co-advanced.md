---
module: co
content_type: decision-trees-and-troubleshooting
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Controlling — Cost Element Mapping, Decision Trees & Troubleshooting

> ECC 6.0 reference. Cost element mapping walkthrough covers how primary cost elements bridge FI and CO, how secondary cost elements live CO-only, and how to reconcile CO totals with FI. Decision trees guide CO configuration choices. Troubleshooting covers symptom-based diagnosis of common CO issues. For cost element master data and category reference, see `modules/co/master-data.md`. For the OBYC (MM) and VKOA (SD) account determination frameworks, see `modules/fi/account-determination.md`.

---

## Cost Element Mapping and CO-FI Reconciliation

CO-FI integration is fundamentally different from the account determination frameworks in MM and SD:

- **OBYC (MM)** maps movement types to GL accounts — one direction: MM -> FI
- **VKOA (SD)** maps billing conditions to GL accounts — one direction: SD -> FI
- **CO-FI** is BIDIRECTIONAL: FI -> CO automatically via primary cost elements; CO -> FI only via category 22 external settlement

There is no single "account determination" transaction for CO. The integration is architectural, not configuration-based — it is built into the cost element master data and the controlling area assignment. Every P&L GL account that has a corresponding primary cost element automatically flows to CO on every posting. The only configuration decision is OKB9 (default account assignment), which sets the default CO receiver when the user does not enter one.

For the full cost element category table (all 11 categories with descriptions and examples), see `modules/co/master-data.md`. This section adds the **mapping walkthrough**: how each category drives data flow between CO and FI.

### Cost Element Mapping Table — All 11 Categories

| Category | Name | GL Account Required | Direction of Flow | FI Impact | CO Tables Updated |
|----------|------|--------------------|--------------------|-----------|-------------------|
| 1 | Primary costs/revenue | Yes (same number) | FI -> CO (automatic) | Every FI posting to this GL account creates a CO document | COBK, COEP, COSP |
| 3 | Accrual/deferral (FI side) | Yes | FI -> CO | FI accrual posts to this GL/CE; CO may have separate imputed cost via category 4 | COBK, COEP, COSP |
| 4 | Accrual/deferral (CO side) | Yes | CO accrual posting | CO imputed costs (calculated depreciation, calculated interest) | COBK, COEP, COSP |
| 11 | Revenue | Yes | FI -> CO | Revenue postings flow to CO (for cost-of-sales accounting / CO-PA) | COBK, COEP, COSP |
| 12 | Sales deduction | Yes | FI -> CO | Discount/rebate postings flow to CO | COBK, COEP, COSP |
| 22 | External settlement | Yes | CO -> FI | Settlement from order to GL account creates FI document | COBK, COEP, COSP + BKPF, BSEG |
| 21 | Internal settlement | No (CO-only) | CO internal | Settlement from order to cost center/order — no FI impact | COBK, COEP, COSS |
| 31 | Results analysis | No (CO-only) | CO internal | WIP and results analysis — no FI impact (unless posted to FI via RA) | COBK, COEP, COSS |
| 41 | Overhead rates | No (CO-only) | CO internal | Overhead surcharges from KGI2 — no FI impact | COBK, COEP, COSS |
| 42 | Assessment | No (CO-only) | CO internal | Assessment allocations from KSU5 — no FI impact | COBK, COEP, COSS |
| 43 | Activity allocation | No (CO-only) | CO internal | Activity allocations — no FI impact | COBK, COEP, COSS |

**How to read this table:**

- **Categories 1, 3, 4, 11, 12** (primary): These require a GL account with the same number. When FI posts to the GL account, CO automatically creates a corresponding document. Primary postings update COSP (primary totals table).
- **Category 22** (external settlement): The ONLY direction where CO creates an FI posting. When an internal order settles to a GL account (KO88 with receiver type KST), FI documents are created in BKPF/BSEG.
- **Categories 21, 31, 41, 42, 43** (secondary): CO-only. No GL account exists. These postings update COSS (secondary totals table) and never touch FI.

> **CRITICAL RECONCILIATION INSIGHT:** Secondary cost elements (categories 21, 31, 41, 42, 43) exist ONLY in CO. They appear in COSP/COSS totals tables but have no corresponding GL posting. This means CO totals for a cost center will always be HIGHER than the FI GL totals for the same cost center's expense accounts, because CO includes both primary postings (from FI) and secondary allocations (CO-internal). **This is not an error — it is by design.** Only primary cost element totals should match between CO and FI.

---

### CO-FI Real-Time Integration Flow

What happens when an FI posting hits a P&L account with a corresponding cost element — the complete 5-step process that executes in real time during every FI document posting:

```
Step 1: User posts FI document (FB50, FB60, MIRO, VF01, AFAB, etc.)
        Document includes a P&L GL account (e.g., 400000 Salaries)

Step 2: System checks — does a primary cost element exist with the same number?
        Lookup: CSKB where KSTAR = GL account number and KOKRS = controlling area
        If YES → CO posting is created automatically
        If NO → No CO posting (GL account is FI-only, e.g., balance sheet accounts)

Step 3: System requires a CO account assignment object
        The CO receiver must be specified: cost center, internal order, WBS element, etc.
        If OKB9 default exists for this GL account → system uses the default
        If OKB9 has no default AND user did not enter one → posting FAILS with
        "Enter a CO account assignment" (this is the most common CO error)

Step 4: CO document created
        COBK header + COEP line items
        The CO document number is DIFFERENT from the FI document number
        COEP-BELNR references the FI document for traceability
        COSP totals table updated (primary postings go to COSP)

Step 5: If the CO object (cost center, order) has a profit center assignment
        PCA separate ledger (GLPCA) is also updated
        This creates the ECC 6-specific PCA data flow
        If the CO object has NO profit center → GLPCA is NOT updated → PCA gap
```

**Worked example:**

A user posts an FI invoice (FB60) for office supplies, GL account 472000, amount 500 EUR, cost center 4100:

1. FI document created in BKPF/BSEG (e.g., doc 1900000100)
2. System finds CSKB entry: KSTAR = 472000, KOKRS = 1000, KATYP = 1 (primary) — YES, cost element exists
3. Cost center 4100 is entered on the invoice line — CO account assignment satisfied (no OKB9 lookup needed)
4. CO document created: COBK/COEP with reference to FI doc 1900000100. COSP updated for cost center 4100, cost element 472000, period posting amount 500 EUR
5. Cost center 4100 has profit center 1010 assigned (CSKS-PRCTR) — GLPCA updated with 500 EUR for profit center 1010

**What triggers Step 2 failure (no CO posting):**
- GL account is a balance sheet account (asset, liability, equity) — no cost element exists
- GL account is a P&L account but no one created the cost element via KA01
- Cost element validity dates do not cover the posting date

**What triggers Step 3 failure (posting error):**
- No OKB9 default for this GL account AND user left cost center blank
- Error message: "Enter a CO account assignment" — the #1 most common CO error in new implementations
- Resolution: either maintain OKB9 default or train users to enter cost center/order on every P&L posting

> **Key principle:** Primary cost elements are the bridge between FI and CO. Every P&L posting that has a corresponding primary cost element automatically flows to CO. Balance sheet postings (asset accounts, liability accounts, equity) do NOT flow to CO because they have no cost element.

> **Exception — Category 22 (External Settlement):** When an internal order settles to a GL account (KO88 with receiver type KST), a category 22 cost element is used. This is the ONLY direction where CO creates an FI posting. All other CO-internal transactions (assessment, distribution, activity allocation) stay within CO and never create FI documents.

---

### CO-FI Reconciliation Walkthrough

This section answers the question: "How do cost center postings reconcile with FI?"

**Scenario:** User wants to verify that cost center 1000 shows the same total costs in CO reports (KSB1 / S_ALR_87013611) as in FI reports (FBL3N / FAGLB03).

**Step 1: Understand What CO Sees vs What FI Sees**

- **FI (FAGLB03 for the GL accounts):** Shows only PRIMARY postings — actual FI document amounts posted to expense GL accounts. These are category 1, 3, 4, 11, 12 cost element postings.
- **CO (KSB1 for the cost center):** Shows primary postings PLUS secondary allocations (categories 21, 31, 41, 42, 43). The CO total is always >= the FI total.

The difference between CO and FI totals = the sum of all secondary cost element postings on that cost center. This difference is expected and correct.

**Worked example:** Cost center 1000 in period 01/2026:

| Source | Cost Element | Category | Amount | Appears in FI? | Appears in CO? |
|--------|-------------|----------|--------|----------------|----------------|
| Salaries posting (FB50) | 400000 | 1 (primary) | 80,000 | YES (FAGLB03) | YES (KSB1) |
| Office supplies (MIRO) | 472000 | 1 (primary) | 5,000 | YES | YES |
| IT assessment received (KSU5) | 690100 | 42 (assessment) | 12,000 | NO | YES |
| Facility overhead received (KGI2) | 691000 | 41 (overhead) | 3,000 | NO | YES |
| **FI total** | | | **85,000** | | |
| **CO total** | | | **100,000** | | |

The 15,000 difference (100,000 - 85,000) is the sum of secondary CE postings (12,000 + 3,000). This is correct — the secondary postings represent allocations that exist only in CO.

**Step 2: Reconcile Primary Postings**

- Run KSB1 for the cost center, filter by primary cost elements only (categories 1, 3, 4, 11, 12)
- Run FBL3N or FAGLB03 for the corresponding GL accounts in the same period
- These totals MUST match. If they do not:
  - Check if all FI postings carry a cost center assignment (OKB9 defaults, manual entry)
  - Check if some FI postings went to a different cost center (posting error)
  - Check if PCA substitution rules (1KEF) are redirecting profit center assignments
  - Check if FI postings to P&L accounts are missing cost elements (KA01 not created for that GL account)

**Step 3: Identify Secondary Postings (CO-Only)**

- Run KSB1 for the cost center, filter by secondary cost elements (categories 21, 31, 41, 42, 43)
- These postings have NO FI counterpart — they exist only in CO
- They represent allocations received from other CO objects:
  - Category 42: Assessment allocations (from KSU5)
  - Category 43: Activity allocations
  - Category 41: Overhead surcharges (from KGI2)
  - Category 21: Internal order settlements (from KO88 with CO receiver)
  - Category 31: Results analysis / WIP postings
- The total of primary + secondary = full cost center costs in CO

**Step 4: Cross-Company-Code Reconciliation (If Applicable)**

If the controlling area spans multiple company codes (OKKP configuration):
- Run KAL1 to display the reconciliation ledger for cross-company-code postings
- Run KALC if reconciliation postings are pending — this creates the FI intercompany entries
- Verify intercompany receivables/payables in FI match the COFIT totals
- See the Reconciliation Ledger section below for the full 3-step process

**Step 5: PCA Reconciliation**

- Compare KE5Z (PCA report, reads GLPCA) totals with FAGLB03 (FI report, reads FAGLFLEXT)
- If PCA totals differ from FI: some FI postings lack profit center assignment
  - Check document splitting configuration (New GL) — is profit center derived for all line items?
  - Check 1KEF substitution rules — are all GL accounts covered?
  - Check that every cost center has a profit center assigned (CSKS-PRCTR)
  - Check for balance sheet items without profit center derivation (common gap in New GL)

### Reconciliation Quick Reference

| What to Compare | CO Source | FI Source | Should Match? | If Not |
|----------------|-----------|-----------|---------------|--------|
| Primary costs only | KSB1 (filter primary CEs) | FBL3N / FAGLB03 | YES — must match exactly | Missing cost elements, wrong CC assignment, missing OKB9 |
| Total costs | KSB1 (all CEs) | FBL3N / FAGLB03 | NO — CO >= FI | Expected: secondary CEs are CO-only |
| PCA vs FI | KE5Z (GLPCA) | FAGLB03 (FAGLFLEXT) | YES — should match | Missing profit center on FI postings |
| Cross-CC | KAL1 (COFIT) | FI intercompany accounts | YES — after KALC run | Pending reconciliation postings |

---

### Reconciliation Ledger (COFIT/COFIS) — ECC 6 Specific

**What it is:** The reconciliation ledger tracks CO postings that cross company code boundaries within a single controlling area. In ECC 6, a controlling area can span multiple company codes (OKKP configuration). When CO allocates costs from a cost center in company code 1000 to a cost center in company code 2000, FI needs an intercompany entry to balance the books.

**How it works (3-step process):**

```
Step 1: CO posting crosses company code boundary
        Example: Assessment cycle allocates from CC 1000 (company code 1000)
                 to CC 2000 (company code 2000)
        CO documents posted in COEP — CO is balanced

Step 2: Reconciliation ledger records the cross-CC posting
        Tables: COFIT (totals), COFIS (single records)
        Records: sending company code, receiving company code, amount, cost element

Step 3: Periodic reconciliation posting
        T-code: KALC
        Creates FI intercompany documents:
          Dr Intercompany Receivable (sending company code)
          Cr Intercompany Payable (receiving company code)
        The FI documents balance the cross-CC cost flow in the general ledger
```

**When reconciliation is needed:**

- Controlling area spans multiple company codes (1:many CA:CC relationship in OKKP)
- CO allocations (assessment, distribution, activity allocation) cross company code boundaries
- If all CO objects are in the same company code, reconciliation ledger postings are zero — KALC produces no output

**When reconciliation is NOT needed:**

- 1:1 controlling area to company code — no cross-CC scenario possible
- CO allocations stay within one company code — no intercompany impact
- Settlement to GL account (category 22) — this already creates FI documents directly

**Key T-codes:**

| T-code | Purpose | When to Run |
|--------|---------|-------------|
| KALC | Execute reconciliation posting | Period-end, after all CO allocations complete |
| KAL1 | Display reconciliation ledger | Anytime — review cross-CC CO postings |
| KAL2 | Reconciliation ledger report | Anytime — detailed reconciliation analysis |

**Tables:**

| Table | Content | Key Fields |
|-------|---------|------------|
| COFIT | Reconciliation ledger totals | KOKRS, GJAHR, PERIO, BUKRS (sender), BUKRS_R (receiver) |
| COFIS | Reconciliation ledger single records | KOKRS, BELNR, BUZEI |

**Worked example:** Assessment cycle allocates 10,000 EUR from CC 1000 (company code 1000) to CC 5000 (company code 2000):

1. CO posting: Dr CC 5000 / Cr CC 1000 (CE cat 42) — CO documents in COEP
2. COFIT records: sender CC = 1000, receiver CC = 2000, amount = 10,000 EUR
3. KALC run creates FI documents:
   - In company code 1000: Dr Intercompany Receivable from 2000, amount 10,000
   - In company code 2000: Cr Intercompany Payable to 1000, amount 10,000
4. After KALC: both company codes are balanced in FI, matching the CO allocation

**Period-end timing:** KALC should run after all CO allocations (KSU5, KSV5) and settlements (KO88, CO88) are complete but before the CO period is locked. See `modules/co/processes.md` for the full period-end sequence.

**Configuration prerequisite:** The intercompany GL accounts used by KALC (receivable and payable) must be configured in OKC1 (or SPRO > Controlling > Organization > Define Reconciliation Posting Accounts). Without this configuration, KALC will error.

> **S/4HANA Differences:** The reconciliation ledger is ELIMINATED in S/4HANA. The Universal Journal (ACDOCA) records all CO postings with full FI account assignment, so cross-company-code CO postings automatically create intercompany FI entries in real time. KALC is no longer needed. Additionally, S/4HANA strongly recommends 1:1 controlling area to company code, further reducing cross-CC scenarios. COFIT and COFIS tables are not used in S/4HANA.
