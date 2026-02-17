---
module: fi
content_type: processes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Financial Accounting — Business Processes

> ECC 6.0 reference. Each process is documented as a numbered narrative followed by a summary table (Step | Activity | T-code | Role | Output). Roles: GL Accountant, AP Accountant, AR Accountant, Finance Manager, System Administrator.

## 1. Daily GL Posting Cycle

The daily GL posting cycle covers document entry, parking/approval workflows, and basic clearing for the general ledger.

### Narrative

**Step 1 — Determine posting method** (GL Accountant)
Decide whether to use the Enjoy screen (FB50 for simple GL-to-GL postings) or the classic screen (F-02 for complex multi-leg postings requiring explicit posting keys). For vendor invoices, use FB60. For customer invoices, use FB70. FB50 is GL-only.

**Step 2 — Enter document (or park)** (GL Accountant)
If posting immediately: use FB50 (or FB60/FB70 for AP/AR). If posting requires approval: use FBV1 to park the document without creating a financial document. Parked documents can be changed (FBV2) by other users before posting.

**Step 3 — Review parked document** (Finance Manager, if approval required)
Open FBV2 or review in the parking workflow. Verify amounts, cost center assignments, and document completeness.

**Step 4 — Post parked document** (GL Accountant or Finance Manager)
Execute FBV0 to post the parked document. This creates the FI document with a document number and updates the sub-ledgers.

**Step 5 — Verify posting** (GL Accountant)
Use FB03 to display the posted document. Confirm document type, amounts, GL accounts, and account assignment objects (cost center, profit center, business area).

**Step 6 — Handle errors — reverse if needed** (GL Accountant)
For open (not yet cleared) documents: use FB08 to reverse. For cleared documents: first use FBRA to reset clearing, then FB08 to reverse. Never post a manual contra-entry to correct — always reverse the original and re-post correctly.

**Step 7 — Clear open items** (GL Accountant)
For GL accounts managed on open item basis: use F-03 (manual clearing) or F.13 (automatic clearing based on assignment field matching). GR/IR accounts are typically cleared via F.13 automatically.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Determine posting method | — | GL Accountant | Decision: FB50 / F-02 / FB60 / FB70 |
| 2a | Post GL document (direct) | FB50, F-02 | GL Accountant | FI document with document number |
| 2b | Park document (for approval) | FBV1 | GL Accountant | Parked document (no FI doc number yet) |
| 3 | Review parked document | FBV2 | Finance Manager | Reviewed/changed parked document |
| 4 | Post parked document | FBV0 | GL Accountant / Finance Manager | FI document created |
| 5 | Verify posting | FB03 | GL Accountant | Confirmed document details |
| 6 | Reverse if error (open doc) | FB08 | GL Accountant | Reversal document |
| 6a | Reset clearing + reverse (cleared doc) | FBRA → FB08 | GL Accountant | Clearing reset, then reversal document |
| 7 | Clear open items | F-03 (manual), F.13 (auto) | GL Accountant | Open items cleared; cleared items in BSAS |

---

## 2. Month-End Close

Month-end close in FI follows a defined sequence. Steps must be performed in order — several have dependencies (e.g., AFAB must complete before period can close for asset accounting).

### Narrative

**Step 1 — Foreign currency revaluation** (GL Accountant)
Run F.05 to revalue all open items and balances in foreign currency at the current exchange rate. Generates adjustment postings to foreign currency gain/loss accounts. F.05 covers GL, vendor, and customer open items in one run.

**Step 2 — Enter accruals and deferrals** (GL Accountant)
Use FBS1 to enter accrual and deferral documents that require reversal in the following period. FBS1 requires a reversal date; the system automatically creates the reversing document on that date when the period opens.

**Step 3 — GR/IR clearing** (GL Accountant or System Administrator)
Run F.13 automatic clearing to match goods receipts against invoice receipts on the GR/IR clearing account. Items that match (same PO, same quantity) are cleared automatically. Unmatched items remain open for AP investigation.

**Step 4 — Depreciation run** (System Administrator or GL Accountant)
Execute AFAB to post periodic depreciation for all assets. Run in test mode first, fix any errors, then post. Only after AFAB completes successfully can the period close for asset accounting.
- At year-end: AFAB must be 100% complete (no unposted depreciation) before running AJAB (asset year-end close).
- AJRW (fiscal year change) must run to open the new year in asset accounting.

**Step 5 — Close posting period** (System Administrator or Finance Manager)
After all period-end activities, use OB52 to close the period for all account types. Best practice: close materials (M) and assets (A) first, then GL (S), then AP/AR (K/D) after final reporting.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Foreign currency revaluation | F.05 | GL Accountant | Adjustment postings to FX gain/loss accounts |
| 2 | Enter accruals / deferrals | FBS1 | GL Accountant | Accrual documents with auto-reversal date set |
| 3 | GR/IR automatic clearing | F.13 | GL Accountant / Sys Admin | GR/IR open items cleared; matched pairs in BSAS |
| 4a | Depreciation run (test mode) | AFAB | Sys Admin / GL Accountant | Test log — no postings |
| 4b | Depreciation run (post) | AFAB | Sys Admin / GL Accountant | Depreciation documents posted; ANLB values updated |
| 4c | Asset year-end close (year-end only) | AJAB | Sys Admin | Asset year closed; prior year locked |
| 4d | Open new asset year (year-end only) | AJRW | Sys Admin | New year open in asset accounting |
| 5 | Close posting period | OB52 | Sys Admin / Finance Manager | Posting period closed for selected account types |

---

## 3. AP Payment Run (F110)

The F110 Automatic Payment Program is the standard method for mass vendor payment processing. It requires upfront FBZP configuration before execution.

> **Prerequisite:** FBZP configuration must be complete before F110 can run. FBZP defines paying company codes, payment methods, available bank accounts, and bank selection rules. See config-spro.md for FBZP setup detail.

### Narrative

**Step 1 — Pre-configuration in FBZP** (System Administrator / Finance Manager — one-time setup)
Configure via FBZP: paying company codes, payment methods per country and company code, house bank accounts with available amounts, bank selection ranking. Done once; maintained periodically as bank details change.

**Step 2 — Create payment run parameters** (AP Accountant)
Open F110. Enter unique run date and identification (e.g., date = 2026-02-15, ID = RUN1). On the Parameters tab: paying company codes, payment methods, next payment date (due date cutoff), vendors to include/exclude. Save.

**Step 3 — Execute proposal run** (AP Accountant)
On the Proposal tab, click "Start Immediately." The system reads all vendor open items (BSIK) due by the next payment date matching the criteria. Creates a payment proposal — does NOT post any documents yet.

**Step 4 — Review and edit the proposal** (AP Accountant / Finance Manager)
Review the proposal list. Items can be removed, payment methods changed per item, and items added manually. Review with the business before proceeding on large proposals.

**Step 5 — Execute payment run** (AP Accountant / Finance Manager)
On the Payments tab, click "Start Immediately." The system posts payment documents, clears vendor open items (BSIK → BSAK), and creates outgoing payment documents against house bank GL accounts.

**Step 6 — Generate bank file / print checks** (AP Accountant / System Administrator)
On the Printout/DME tab: generate the bank transfer file (DME format) for electronic payments, or trigger check printing for paper payments.

**Step 7 — Reconcile in FBL1N** (AP Accountant)
Verify in FBL1N that vendor open items are now cleared (status = cleared, in BSAK). Investigate any unexpected items still open in BSIK.

**Gotcha — re-runs:** If you delete the proposal and re-run with the same run date + identification, the system picks up newly due items since the original proposal. Use a new identification for a truly fresh run.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Configure payment program (one-time) | FBZP | Sys Admin / Finance Manager | Payment methods, bank accounts configured |
| 2 | Set run parameters | F110 (Parameters tab) | AP Accountant | Run date + ID with company code and method criteria |
| 3 | Execute proposal | F110 (Proposal tab) | AP Accountant | Payment proposal — list of items to pay (no postings) |
| 4 | Review and edit proposal | F110 (Edit Proposal) | AP Accountant / Finance Manager | Reviewed proposal; items added/removed/changed |
| 5 | Execute payment run | F110 (Payments tab) | AP Accountant / Finance Manager | Payment documents posted; BSIK items moved to BSAK |
| 6 | Generate bank file or check print | F110 (Printout/DME tab) | AP Accountant / Sys Admin | DME bank file or printed checks |
| 7 | Reconcile cleared items | FBL1N | AP Accountant | Verified: paid items cleared; open items investigated |

---

## 4. Financial Reporting

FI financial reporting follows a drill-down path from summary reports to document level.

### Narrative

**Step 1 — Run financial statements** (Finance Manager)
Execute F.01 or S_ALR_87012284 to generate the balance sheet and P&L statement. Both call program RFBILA00 and require a Financial Statement Version (FSV — configured in OB58). Select company code, fiscal year, reporting period, and currency type.

**Step 2 — Run trial balance** (GL Accountant / Finance Manager)
Execute S_ALR_87012277 for a GL account balance listing. Shows each GL account with period movements and cumulative balance. Useful for reconciling totals before generating formal financial statements.

**Step 3 — Drill to account line items** (GL Accountant)
From financial statement output, select an account and drill to line items using FBL3N (classic GL) or FAGLL03 (New GL — shows profit center and segment per line). FBL3N reads BSIS (open) and BSAS (cleared). FAGLL03 reads FAGLFLEXT.

**Step 4 — Drill to document** (GL Accountant)
From the line item report, select a line and use FB03 to display the full accounting document. FB03 shows all line items, document header (type, posting date, reference), and links to related documents (original MM or SD document).

**Step 5 — AP / AR balance reports** (AP Accountant / AR Accountant)
- AP: S_ALR_87012082 (vendor balances in local currency) and FBL1N (vendor line items, open/cleared)
- AR: S_ALR_87012168 (due date analysis for aged receivables) and FBL5N (customer line items)

> **CRITICAL reminder:** S_ALR_87012284 = Financial Statements (Balance Sheet/P&L). S_ALR_87012082 = Vendor Balances. These are frequently confused. Running 87012284 when expecting vendor data gives the balance sheet, not vendor balances.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Financial statements (Balance Sheet / P&L) | F.01 or S_ALR_87012284 | Finance Manager | Balance sheet and income statement by FSV |
| 2 | Trial balance (GL account totals) | S_ALR_87012277 | GL Accountant / Finance Manager | All GL accounts with period and cumulative balances |
| 3a | Account line items (Classic GL) | FBL3N | GL Accountant | Line items per account; reads BSIS/BSAS |
| 3b | Account line items (New GL) | FAGLL03 | GL Accountant | Line items with segment/profit center; reads FAGLFLEXT |
| 4 | Display document | FB03 | GL Accountant | Full document header and all line items; links to source document |
| 5a | Vendor balances | S_ALR_87012082 | AP Accountant | Vendor balance totals by company code |
| 5b | Vendor line items | FBL1N | AP Accountant | Open and cleared vendor line items; reads BSIK/BSAK |
| 5c | Customer due date analysis | S_ALR_87012168 | AR Accountant | Aged receivables by days overdue |
| 5d | Customer line items | FBL5N | AR Accountant | Open and cleared customer line items; reads BSID/BSAD |
