---
module: fi
content_type: tcodes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Financial Accounting — Transaction Codes

> ECC 6.0 reference. New GL assumed active (standard post-2008 ECC 6.0). Classic GL differences noted inline.

## Workflow Index

| Process Stage | T-code(s) | Submodule | Notes |
|---|---|---|---|
| GL Posting (simple) | FB50 | GL | Enjoy screen; GL accounts only |
| GL Posting (classic/complex) | F-02, FB01 | GL | Requires posting keys; supports all line types |
| Document Parking | FBV1 (GL), FB60/FB70 park flag | GL, AP, AR | No FI doc number until posted via FBV0 |
| Document Reversal | FB08 | GL | Open items only; use FBRA first if cleared |
| Reset Clearing + Reverse | FBRA → FB08 | GL | Two-step; required when doc has been cleared |
| GL Clearing (manual) | F-03 | GL | Manual open item matching |
| GL Clearing (automatic) | F.13 | GL | Program SAPF124; mass-matching (e.g., GR/IR) |
| Post with Clearing | F-04 | GL | Combines posting and clearing in one step |
| Vendor Invoice Entry | FB60, F-43, MIRO | AP | FB60 = Enjoy; F-43 = classic; MIRO = PO-based |
| Vendor Credit Memo | FB65, F-41 | AP | FB65 = Enjoy; F-41 = classic; NOT F-27 |
| Vendor Payment (manual) | F-53, F-58 | AP | F-53 = post only; F-58 = post + print check |
| Vendor Payment (automatic/APP) | F110 | AP | Full sequence: FBZP → params → proposal → edit → pay → DME → FBL1N |
| Customer Invoice Entry | FB70, F-22 | AR | FB70 = Enjoy; F-22 = classic |
| Customer Credit Memo | FB75, F-27 | AR | FB75 = Enjoy; F-27 = classic; NOT F-41 |
| Customer Payment | F-28 | AR | Incoming payment with clearing |
| Clear Customer Account | F-32 | AR | Manual clearing of customer open items |
| Asset Acquisition | F-90, F-91 | AA | F-90 = with vendor; F-91 = to clearing account |
| Asset Transfer | ABUMN | AA | Within company code; creates retirement + acquisition |
| Asset Retirement/Scrapping | F-92, ABAVN | AA | F-92 = sale with revenue; ABAVN = scrapping |
| Depreciation Run | AFAB | AA | Must complete before AJAB year-end close |
| AA Fiscal Year Change | AJRW | AA | Opens new year for AA; run before new-year postings |
| AA Year-End Closing | AJAB | AA | After AFAB complete + AJRW run; closes AA fiscal year |
| GL Balance Display | FAGLB03 (New GL), FS10N (Classic GL) | GL | New GL: FAGLB03 reads FAGLFLEXT; Classic: FS10N reads GLT0 |
| GL Line Items | FAGLL03 (New GL), FBL3N (Classic GL) | GL | FAGLL03 for segment/profit center fields |
| AP Line Items | FBL1N | AP | Reads BSIK (open) + BSAK (cleared) |
| AR Line Items | FBL5N | AR | Reads BSID (open) + BSAD (cleared) |
| Financial Statements | F.01, S_ALR_87012284 | Reporting | Balance Sheet / P&L; runs RFBILA00 |
| Trial Balance | S_ALR_87012277 | Reporting | GL account balances by period |
| Vendor Balances | S_ALR_87012082 | AP | NOT S_ALR_87012284 — see critical note in AP section |
| Due Date Analysis (AR) | S_ALR_87012168 | AR | Aged receivables by customer |
| Posting Period Control | OB52 | GL | Open/close periods by account type |
| Master Data (GL) | FS00 | GL | Creates/changes SKA1 + SKB1 centrally |
| Master Data (Vendor, FI) | FK01, FK02, FK03 | AP | FI-only; use XK01 for MM+FI environments |
| Master Data (Vendor, central) | XK01 | AP/MM | LFA1 + LFB1 + LFM1 in one transaction |
| Master Data (Customer, FI) | FD01, FD02, FD03 | AR | FI-only; use XD01 for SD+FI environments |
| Master Data (Customer, central) | XD01 | AR/SD | KNA1 + KNB1 + KNVV in one transaction |
| Master Data (Asset) | AS01, AS02, AS03 | AA | Creates ANLA + ANLB for each depreciation area |

---

## General Ledger (GL)

### FB50 — Enter G/L Account Document (Enjoy Screen)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document Entry → Enter G/L Account Document

**Usage:** Preferred entry point for simple GL-to-GL journal entries. Single-screen Enjoy interface allows entering all debit/credit lines before posting. GL accounts only — no sub-ledger (vendor/customer) line items.

**Gotcha:** Use FB60 for vendor invoices and FB70 for customer invoices. FB50 does not create sub-ledger entries; posting to a reconciliation account via FB50 will create a GL line but no corresponding open item in AP/AR.

---

### F-02 — Enter G/L Account Document (Classic Screen)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document Entry → General Posting

**Usage:** Classic multi-screen posting interface requiring explicit posting keys for each line item. Functionally equivalent to FB01. Use when complex posting logic requires explicit control over posting keys, special GL indicators, or payment terms at the line level.

**Gotcha:** Posting key 40 = GL debit, 50 = GL credit. Unlike FB50, posting keys must be entered manually for each line.

---

### FB01 — Post Document

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document Entry → Post Document

**Usage:** Functional equivalent of F-02; same classic interface. Used interchangeably with F-02 for GL postings requiring explicit posting key entry. FB01 is also the underlying program called by other Enjoy transactions.

---

### FB03 — Display Document

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document → Display

**Usage:** Universal document display transaction for all FI document types (GL, vendor, customer, asset). Enter company code and document number to view full document including header data, line items, and document flow.

**Gotcha:** FB03 is not limited to GL documents — it works for AP, AR, and AA documents as well. Use it as your first stop when investigating any FI document number.

---

### FB02 — Change Document

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document → Change

**Usage:** Allows limited changes to posted FI documents. Header-level fields (document header text, reference, assignment) can be changed. Payment terms and dunning data on line items can sometimes be changed.

**Gotcha:** Line item amounts, posting keys, accounts, and amounts cannot be changed after posting. To correct a posting error, reverse the document with FB08 and re-enter.

---

### FB08 — Reverse Document (Individual Reversal)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document → Reverse → Individual Reversal

**Usage:** Reverses a single FI document by creating a mirror-image document with opposite posting signs. Requires the original document to be open (not cleared). Reversal reason and reversal date are required inputs.

**Gotcha:** FB08 fails if the document has been cleared. You must first use FBRA to reset the clearing, then run FB08 to reverse. Two-step process is mandatory when clearing exists.

---

### FBRA — Reset Clearing and Reverse

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document → Reset Cleared Items

**Usage:** Resets the clearing status on a cleared document, reopening the items involved. Required first step when attempting to reverse a document that has been cleared. After FBRA resets the clearing, FB08 can reverse the original document.

**Gotcha:** FBRA resets ALL items in the clearing run, not just the specific document you targeted. If multiple items were cleared together, all become open again. This may require re-clearing the unaffected items afterward.

---

### F-03 — Clear G/L Account

**Menu Path:** Accounting → Financial Accounting → General Ledger → Account → Clear

**Usage:** Manual clearing of GL account open items. Displays open items for a GL account and allows selection of offsetting items to clear. Requires the GL account to be managed on open item basis (OI indicator set in FS00).

---

### F.13 — Automatic Clearing

**Menu Path:** Accounting → Financial Accounting → General Ledger → Periodic Processing → Automatic Clearing

**Usage:** Batch clearing program SAPF124 that matches open items by configurable criteria (amount, assignment field, etc.). Used for automatic GR/IR clearing, bank reconciliation clearing, and other mass-matching scenarios. Can be run in test mode before live execution.

---

### F-04 — Post with Clearing

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document Entry → Post with Clearing

**Usage:** Combines document posting and open item clearing in a single transaction. Useful for scenarios where a new posting should simultaneously clear existing open items, avoiding a separate clearing step.

---

### FBV1 — Park Document (GL)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document Entry → Park Document

**Usage:** Saves a document in parked status without posting. No FI document number is created; the document exists only as a parked entry. Parked documents can be changed, approved via workflow, and posted with FBV0. Used for documents pending approval or completion.

---

### FBV2 — Change Parked Document

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document → Parked Documents → Change

**Usage:** Modify a previously parked document (created via FBV1) before it is posted. All fields remain editable because no FI document number has been assigned yet.

---

### FBV0 — Post Parked Document

**Menu Path:** Accounting → Financial Accounting → General Ledger → Document → Parked Documents → Post

**Usage:** Posts a parked document, creating the permanent FI document number and updating all relevant tables. This is the step that moves the document from parked status into the financial ledger.

---

### FBS1 — Enter Accrual/Deferral Document

**Menu Path:** Accounting → Financial Accounting → General Ledger → Periodic Processing → Enter Accrual/Deferral Document

**Usage:** Month-end accrual and prepaid entry transaction. The document requires a reversal date; the system automatically creates the reversing entry on that date. Used for accruing expenses not yet invoiced and deferring revenues/expenses across periods.

**Gotcha:** The reversal date must fall in a future open posting period. If the period is not yet open when FBS1 is posted, the automatic reversal will fail when that period arrives — monitor using program RACSB00.

---

### F.05 — Foreign Currency Valuation

**Menu Path:** Accounting → Financial Accounting → General Ledger → Periodic Processing → Closing → Valuate → Foreign Currency Valuation

**Usage:** Month-end revaluation of open items and account balances denominated in foreign currencies. Covers GL accounts, vendor open items, and customer open items simultaneously. Creates valuation postings with automatic reversal on the first day of the next period.

---

### FS00 — GL Account Master Maintenance (Central)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Master Records → G/L Accounts → Individual Processing → Centrally

**Usage:** Creates and changes GL account master records centrally, maintaining both the chart of accounts segment (SKA1 table) and the company code segment (SKB1 table) in one transaction. Key fields: account group, balance sheet/P&L indicator, open item management, line item display, sort key, field status group.

---

### FS10N — GL Account Balance Display (Classic GL)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Account → Display Balances (New)

**Usage:** Displays GL account balances by period for a given company code and fiscal year. Allows drilldown from balance to line items.

**Gotcha:** FS10N reads the GLT0 table, which is the Classic GL totals table. In systems with New GL activated (standard for ECC 6.0 post-2008), GLT0 may not be updated for all accounts — FS10N can show zero balances on accounts that are actively being posted to. Use FAGLB03 instead for New GL-active systems. See also: FAGLB03.

---

### FAGLB03 — GL Account Balance Display (New GL)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Account → Display Balances

**Usage:** Displays GL account balances in New GL-active systems. Reads FAGLFLEXT (New GL totals table), which is the authoritative source when New GL is activated. Supports additional drilldown by profit center, segment, and other New GL dimensions not available in FS10N.

**Gotcha:** FAGLB03 is only available when New GL (ledger FAGL) is activated. In a Classic GL system, FS10N is the correct transaction. See also: FS10N.

---

### FAGLL03 — GL Account Line Items (New GL)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Account → Display Line Items (New)

**Usage:** Line item display for GL accounts in New GL-active systems. Reads FAGLFLEXA (New GL line item table). Equivalent to FBL3N but includes New GL-specific fields: segment, profit center, ledger, and document splitting assignments visible at the line item level.

---

### OB52 — Open and Close Posting Periods

**Menu Path:** IMG path — SPRO → Financial Accounting (New) → Financial Accounting Global Settings (New) → Ledgers → Fiscal Year and Posting Periods → Posting Periods → Open and Close Posting Periods

**Usage:** Controls which fiscal year periods are open for posting, by account type. Account types: A = assets, D = customers, K = vendors, S = GL accounts, M = materials (MM). Periods are controlled per posting period variant, which is assigned to company codes in OBY6.

**Gotcha:** Opening period 1 of the new fiscal year may also require opening a special period (period 13-16 for prior-year adjustments). The "+" wildcard account type row controls all types not explicitly listed.

---

## Accounts Payable (AP)

### FB60 — Enter Vendor Invoice (Enjoy Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Document Entry → Invoice

**Usage:** Preferred entry point for vendor invoices that are not PO-based. Single-screen Enjoy interface; park or post immediately. Creates a vendor open item in AP sub-ledger and a corresponding GL reconciliation account posting.

---

### F-43 — Enter Vendor Invoice (Classic Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Document Entry → Invoice - General

**Usage:** Classic multi-screen vendor invoice entry requiring explicit posting keys. Posting key 31 = vendor credit line (creates AP open item); posting key 40 = debit GL expense line. Use when precise control over posting keys or special GL indicators is required.

**Gotcha:** Posting key 31 is required for the vendor line; forgetting it and using 50 will not create an AP open item. The vendor account will not appear in FBL1N as an open item.

---

### FB65 — Enter Vendor Credit Memo (Enjoy Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Document Entry → Credit Memo

**Usage:** Symmetric to FB60; use when a vendor issues a credit memo reducing the amount owed. Creates a vendor open item that can be cleared against invoices during payment (F110) or manually (F-44).

---

### F-41 — Enter Vendor Credit Memo (Classic Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Document Entry → Credit Memo - General

**Usage:** Classic screen equivalent of FB65 for vendor credit memos requiring explicit posting key entry.

**Gotcha:** F-41 = VENDOR credit memo. F-27 = CUSTOMER credit memo. These are frequently confused. If you use F-27 for a vendor credit, no AP open item will be created.

---

### MIRO — Logistics Invoice Verification

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Document Entry → Enter Invoice

**Usage:** MM-side transaction for PO-based vendor invoices. References a purchase order and goods receipt, performs three-way match (PO/GR/invoice), and generates an FI document automatically via MM-FI account determination. Does not require the user to know FI posting keys.

**Gotcha:** MIRO is the correct transaction for PO-based invoices, not FB60. Using FB60 for a PO-based invoice bypasses the three-way match and does not update MM logistics tables (EKBE, RSEG).

---

### F-53 — Post Outgoing Payment (Manual)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Document Entry → Outgoing Payment → Post

**Usage:** Manual vendor payment posting without the Automatic Payment Program. Used for one-off payments, urgent payments, or payments that cannot be batched. Clears the vendor open item(s) selected during the transaction.

---

### F-58 — Payment with Printout

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Document Entry → Outgoing Payment → Post + Print Forms

**Usage:** Combines manual outgoing payment posting (F-53) with immediate check printing. Used for manual check runs where a single check must be printed and the payment posted in one step.

---

### F110 — Automatic Payment Program (APP)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Periodic Processing → Payments

**Usage:** Mass payment run for processing multiple vendor (and optionally customer) payments in a batch. Full execution sequence:
1. **FBZP** — Pre-configuration (payment methods, house banks, company code settings — one-time setup)
2. **F110 Parameters tab** — Enter run date, identification, company codes, payment methods, next payment date
3. **Proposal run** — System generates proposal list of items due for payment
4. **Edit proposal** — Review and optionally exclude individual items
5. **Payment run** — Executes payments, creates FI documents, clears open items
6. **DME/Printout** — Generate payment medium file (bank transfer) or print checks
7. **FBL1N** — Reconcile vendor line items to confirm cleared items

**Gotcha:** Deleting a proposal and re-running with the same run date and identification will pick up newly due items that became due after the original proposal. Use a new identification string for a completely fresh run to avoid confusion.

---

### FBL1N — Vendor Line Items

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Account → Display/Change Line Items

**Usage:** Displays open, cleared, or all line items for a vendor account. Primary reconciliation tool after payment runs (F110) and for resolving vendor account discrepancies. Reads BSIK table for open items and BSAK table for cleared items.

---

### FK01 — Create Vendor Master (Accounting View)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Master Records → Create

**Usage:** Creates a vendor master record with FI accounting data only (LFA1 general data + LFB1 company code data). No purchasing organization data. Use in FI-only environments where the vendor has no purchasing relationship.

**Gotcha:** In environments with both FI and MM active, use XK01 instead. FK01-created vendors cannot be used as PO vendors until purchasing views are added.

---

### FK02 — Change Vendor Master (Accounting View)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Master Records → Change

**Usage:** Changes FI accounting data in a vendor master record (payment terms, bank details, reconciliation account, dunning data). Does not allow changes to purchasing views.

---

### FK03 — Display Vendor Master (Accounting View)

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Master Records → Display

**Usage:** Read-only display of a vendor master record, FI accounting views. Useful for auditing vendor master data without risk of accidental change.

---

### XK01 — Create Vendor Master (Central, All Views)

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Vendor → Central → Create

**Usage:** Creates a vendor master record with all views in one transaction: LFA1 (general data), LFB1 (company code / FI data), and LFM1 (purchasing organization data). Preferred in environments with both MM and FI active.

---

### F150 — Dunning Run

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Periodic Processing → Dunning

**Usage:** Executes the dunning program SAPF150 to generate dunning notices for overdue customer and/or vendor open items. Requires dunning configuration (dunning procedure, dunning levels, dunning texts) set up via FBMP. The dunning run selects overdue items, assigns dunning levels, and prints or emails dunning letters.

**Gotcha:** F150 can also dun vendors (for credit memos owed by vendors). Ensure dunning procedures are configured separately for customer and vendor accounts if both are used.

---

### S_ALR_87012082 — Vendor Balances in Local Currency

**Menu Path:** Accounting → Financial Accounting → Accounts Payable → Information System → Reports for Accounts Payable Accounting → Vendor Balances → Vendor Balances in Local Currency

**Usage:** Displays vendor account balances summarized by period in local currency. Used for AP sub-ledger reconciliation to GL and for vendor balance analysis.

**Gotcha:** CRITICAL — S_ALR_87012082 = VENDOR BALANCES. S_ALR_87012284 = FINANCIAL STATEMENTS (Balance Sheet/P&L). These two report numbers are frequently confused. S_ALR_87012082 will never show a Balance Sheet; it shows vendor account totals only.

---

## Accounts Receivable (AR)

### FB70 — Enter Customer Invoice (Enjoy Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Document Entry → Invoice

**Usage:** Preferred entry point for customer invoices that are not SD billing-based. Single-screen Enjoy interface; park or post immediately. Creates a customer open item in AR sub-ledger and a corresponding GL reconciliation account posting.

---

### F-22 — Enter Customer Invoice (Classic Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Document Entry → Invoice - General

**Usage:** Classic multi-screen customer invoice entry requiring explicit posting keys. Posting key 01 = customer debit line (creates AR open item); posting key 50 = credit GL revenue line. Use when precise control over posting keys is required.

---

### FB75 — Enter Customer Credit Memo (Enjoy Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Document Entry → Credit Memo

**Usage:** Enjoy screen for entering customer credit memos. Creates a customer credit open item that reduces the customer's balance and can be cleared against invoices during payment matching.

---

### F-27 — Enter Customer Credit Memo (Classic Screen)

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Document Entry → Credit Memo - General

**Usage:** Classic screen equivalent of FB75 for customer credit memos.

**Gotcha:** F-27 = CUSTOMER credit memo. F-41 = VENDOR credit memo. These are frequently confused. If you use F-41 for a customer credit, no AR open item will be created.

---

### F-28 — Post Incoming Payment

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Document Entry → Incoming Payments

**Usage:** Manual customer payment receipt posting. Selects customer open items to clear against the incoming payment amount. Creates a bank/cash debit and clears the customer receivable open item(s).

---

### F-32 — Clear Customer Account

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Account → Clear

**Usage:** Manual clearing of customer open items without a payment posting. Used to clear credit memos against invoices, or to clear debit and credit items that offset each other without a cash movement.

---

### FBL5N — Customer Line Items

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Account → Display/Change Line Items

**Usage:** Displays open, cleared, or all line items for a customer account. Primary tool for AR reconciliation, collections, and dispute investigation. Reads BSID table for open items and BSAD table for cleared items.

---

### FD01 — Create Customer Master (Accounting View)

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Master Records → Create

**Usage:** Creates a customer master record with FI accounting data only (KNA1 general data + KNB1 company code data). No sales organization data. Use in FI-only environments where the customer has no SD sales relationship.

**Gotcha:** In environments with both FI and SD active, use XD01 instead. FD01-created customers cannot be used in SD sales orders until sales views are added.

---

### FD02 — Change Customer Master (Accounting View)

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Master Records → Change

**Usage:** Changes FI accounting data in a customer master record (payment terms, bank details, reconciliation account, dunning data, credit control area). Does not allow changes to SD sales views.

---

### FD03 — Display Customer Master (Accounting View)

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Master Records → Display

**Usage:** Read-only display of a customer master record, FI accounting views. Useful for auditing customer master data without risk of accidental change.

---

### XD01 — Create Customer Master (Central, All Views)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Business Partners → Customers → Create → Complete

**Usage:** Creates a customer master record with all views in one transaction: KNA1 (general data), KNB1 (company code / FI data), and KNVV (sales area data). Preferred in environments with both SD and FI active.

---

### FD32 — Customer Credit Limit

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Credit Management → Credit Management → Change

**Usage:** Sets or displays the credit limit, credit control area assignment, and credit exposure for a customer. Used by credit managers to control customer credit risk. Credit exposure is calculated from open orders, deliveries, and open AR items.

---

### S_ALR_87012168 — Due Date Analysis for Open Items

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Information System → Reports → Customer Balances → Due Date Analysis

**Usage:** Aged receivables report showing customer open items grouped by overdue bucket (current, 1-30 days, 31-60 days, etc.). Used by collections teams for prioritizing follow-up and by finance for allowance for doubtful accounts calculations.

---

## Asset Accounting (AA)

### AS01 — Create Asset Master Record

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Asset → Create → Asset

**Usage:** Creates the asset master record, consisting of ANLA (general data segment) and ANLB (depreciation terms) for each active depreciation area. Asset class selection drives the number range, account determination, and depreciation key defaults. Required before any asset acquisition posting can be made.

---

### AS02 — Change Asset Master Record

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Asset → Change

**Usage:** Changes asset master data including description, cost center, location, capitalization date, and depreciation parameters. Some fields (e.g., asset class, company code) cannot be changed after the asset has transactions.

---

### AS03 — Display Asset Master Record

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Asset → Display

**Usage:** Read-only display of asset master data. Shows all general data, depreciation parameters per area, and time-dependent data. Use before AS02 to review current values.

---

### ABUMN — Asset Transfer (Within Company Code)

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Posting → Transfer → Transfer Within Company Code

**Usage:** Transfers an asset between asset classes, cost centers, or business areas within the same company code. Creates both a retirement posting on the source asset and an acquisition posting on the receiving asset, preserving net book value.

---

### F-90 — Asset Acquisition from Vendor (With Purchase Order)

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Posting → Acquisition → External Acquisition → With Vendor

**Usage:** Posts an asset acquisition with simultaneous vendor clearing. Creates both the asset acquisition debit (ANLA/ANLP update) and the vendor open item (AP sub-ledger), which is then paid via F110 or F-53.

---

### F-91 — Asset Acquisition to Clearing Account

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Posting → Acquisition → External Acquisition → Acquis. w/Autom. Offsetting Entry

**Usage:** Posts asset acquisition debiting the asset and crediting a clearing/interim account, when vendor clearing happens separately. Used when the vendor invoice is processed in MM (MIRO) or arrives after the asset is placed in service.

---

### F-92 — Asset Retirement with Customer (Sale)

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Posting → Retirement → Retirement w/Revenue → With Customer

**Usage:** Posts asset retirement from a sale, creating a customer receivable open item and calculating gain or loss on disposal. The net book value is written off and the sale proceeds are recorded, with the gain/loss posted to the configured GL account.

---

### ABAVN — Asset Retirement by Scrapping

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Posting → Retirement → Asset Retirement by Scrapping

**Usage:** Writes off an asset with no sale proceeds (scrapping or abandonment). Posts the net book value as a loss on scrapping to the configured GL account. No customer receivable is created.

---

### AFAB — Depreciation Run

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Periodic Processing → Depreciation Run → Execute

**Usage:** Posts periodic depreciation for all assets in a company code for a specified fiscal year and period. Can run in test mode (no postings) or live mode. Restart capability allows resuming an interrupted run without double-posting.

**Gotcha:** AFAB must be fully completed (all depreciation posted, no error assets) before AJAB can close the asset fiscal year. AJAB checks for unposted depreciation and will fail if any remains. Run AFAB in test mode first to identify error assets.

---

### AJRW — Asset Fiscal Year Change

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Periodic Processing → Fiscal Year Change

**Usage:** Opens the new fiscal year in Asset Accounting, allowing postings in the new year. Must be executed before any asset transactions (acquisitions, retirements, transfers) in the new fiscal year. Does not close the old year.

**Gotcha:** AJRW and AJAB are independent steps. AJRW opens the new year (can be run any time); AJAB closes the old year (requires AFAB complete). Both must be run during year-end, in the sequence: AFAB → AJRW → AJAB.

---

### AJAB — Asset Year-End Closing

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Periodic Processing → Year-End Closing → Execute

**Usage:** Closes the current asset fiscal year. Transfers final depreciation values, closes the depreciation areas for the old year, and sets the fiscal year status to "closed" in ANLA.

**Gotcha:** AJAB will fail if: (1) depreciation (AFAB) is not 100% complete for the year, (2) AJRW has not been run to open the new year, or (3) there are incomplete asset transactions. Fix all error assets via AFAB before attempting AJAB. The year-end close order dependency is: AFAB (complete) → AJRW (run) → AJAB (close).

---

### AW01N — Asset Explorer

**Menu Path:** Accounting → Financial Accounting → Fixed Assets → Asset → Asset Explorer

**Usage:** Single-asset drilldown display showing planned versus posted depreciation values across all depreciation areas for every period of the fiscal year. Displays acquisition value, accumulated depreciation, and net book value. Most useful diagnostic tool for investigating why depreciation amounts are unexpected or an asset has incorrect values.

---

## Period-End and Cross-Functional Reporting

### F.01 — Financial Statements

**Menu Path:** Accounting → Financial Accounting → General Ledger → Information System → General Ledger Reports → Balance Sheet / Profit+Loss Statement / Cash Flow → General → Actual/Actual Comparisons → Financial Statements

**Usage:** Runs program RFBILA00 to produce Balance Sheet and Profit & Loss statement formatted according to a Financial Statement Version (FSV). Requires FSV configured in OB58. Supports comparative period analysis and drilldown to GL account level.

**Gotcha:** The FSV must be correctly configured (accounts assigned to nodes) before meaningful output is produced. An FSV with unassigned accounts will produce an out-of-balance statement — use the "not assigned" node in the FSV to catch gaps.

---

### S_ALR_87012284 — Financial Statements (Balance Sheet / P&L)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Information System → Reports for General Ledger Accounting → Balance Sheet / Profit+Loss Statements → General → Balance Sheet / P+L Statement

**Usage:** Parameter variant report for program RFBILA00. Produces Balance Sheet and Profit & Loss statement using a pre-configured FSV. Functionally equivalent to F.01 but accessed via a parameter variant with predefined report options.

**Gotcha:** CRITICAL IDENTIFICATION — S_ALR_87012284 = FINANCIAL STATEMENTS (Balance Sheet/P&L). This is NOT a vendor balances report. Vendor balances = S_ALR_87012082. These two report numbers are the most commonly confused S_ALR report codes in FI.

---

### S_ALR_87012277 — GL Account Balances (Trial Balance)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Information System → Reports for General Ledger Accounting → General → G/L Account Balances

**Usage:** Trial balance report showing period balances and cumulative balances by GL account. Used for period-end reconciliation, auditor requests, and verifying that the sum of all debit and credit balances nets to zero.

---

### FBL3N — GL Account Line Items (Classic GL)

**Menu Path:** Accounting → Financial Accounting → General Ledger → Account → Display/Change Line Items

**Usage:** Line item display for GL accounts. Reads BSIS (open items) and BSAS (cleared items). Supports multiple selection criteria and ALV list output. Works in New GL environments but does not show New GL-specific fields (segment, profit center per line item, ledger assignment).

**Gotcha:** In New GL-active systems, use FAGLL03 instead of FBL3N when you need segment, profit center, or document splitting information at the line item level. FBL3N will not show those fields even in a New GL environment.

---

### OBY6 — Company Code Global Settings Display

**Menu Path:** IMG path — SPRO → Enterprise Structure → Definition → Financial Accounting → Edit, Copy, Delete, Check Company Code

**Usage:** Displays the global settings assigned to a company code: fiscal year variant, chart of accounts, local currency, and posting period variant. Used to verify configuration and understand the foundational parameters driving FI behavior for a company code.
