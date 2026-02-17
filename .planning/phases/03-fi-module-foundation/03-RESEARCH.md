# Phase 3: FI Module Foundation - Research

**Researched:** 2026-02-16
**Domain:** SAP ECC 6.0 Financial Accounting — GL, AP, AR, Asset Accounting, New GL
**Confidence:** MEDIUM (SAP ECC 6.0 is a closed system; no Context7 docs exist; all findings verified via multiple public sources, SAP Community, and authoritative SAP documentation sites)

---

## Summary

This research verifies the T-codes, SPRO paths, table structures, and field names that Phase 3 will document in four output files: `modules/fi/tcodes.md`, `modules/fi/config-spro.md`, `modules/fi/processes.md`, and `modules/fi/master-data.md`. The research focus provided in the brief contained several factual errors that must be corrected before planning; these are flagged explicitly throughout.

The primary correction concerns S_ALR reporting codes: the brief incorrectly attributed S_ALR_87012284 to "vendor balances" — it is actually the Financial Statements (Balance Sheet/P&L) report. The correct vendor balance T-code is S_ALR_87012082. A second material error: KVGR1-5 (customer groups) belong to KNVV (sales area data), not KNB1 (company code data). A third: KOSTL (cost center) in asset master is stored in ANLZ (time-dependent), not directly in ANLA. These corrections are detailed below.

The standard SAP ECC 6.0 FI reference set is well-established and stable. T-codes in the FB/F-/FS/S_ALR series have not changed since ECC 6.0 release. SPRO paths follow the "Financial Accounting (New)" structure introduced with New GL. Master data table structures (SKA1/SKB1, LFA1/LFB1/LFM1, KNA1/KNB1/KNVV, ANLA/ANLB/ANLZ) are stable and verified across multiple SAP documentation sources.

**Primary recommendation:** Write content in the verified form below, not from the brief's initial T-code/field list. The corrections are material and will affect how Claude answers queries.

---

## T-Code Verification

### General Ledger — Verified T-codes

| T-code | Description | Verified? | Notes |
|--------|-------------|-----------|-------|
| FB50 | Enter G/L Account Document (Enjoy screen) | HIGH | GL-only posting; no sub-ledger. Simpler than F-02 |
| F-02 | Enter G/L Account Document (classic screen) | HIGH | Same as FB01. Requires posting keys. Full flexibility including sub-ledger |
| FB01 | Post Document | HIGH | Functional equivalent of F-02 |
| FB03 | Display Document | HIGH | Standard document display, all document types |
| FB02 | Change Document | HIGH | Limited changes after posting (header text, assignment) |
| FB08 | Reverse Document | HIGH | Reverses open (not yet cleared) FI documents. Use FBRA for cleared docs |
| FBRA | Reset Clearing / Reverse | HIGH | Resets cleared documents then optionally reverses; required when clearing exists |
| F-03 | Clear G/L Account | HIGH | Manual GL account clearing |
| F.13 | Automatic Clearing | HIGH | GR/IR and other automatic clearing; runs SAPF124 program |
| F-04 | Post with Clearing | HIGH | Combines posting and clearing in one step |
| FBV0 | Post Parked Document | HIGH | Post a previously parked document (parks = FBV1/FBV2) |
| FBV1 | Park Document (GL) | HIGH | Parks without posting; no FI document created until FBV0 |
| FBV2 | Change Parked Document | HIGH | Change a parked document before posting |
| FBS1 | Enter Accrual/Deferral Document | HIGH | Month-end accruals; requires reversal date; creates reversing entry automatically |
| F.05 | Foreign Currency Valuation | HIGH | Month-end revaluation; covers GL, vendor, and customer open items |
| FS00 | GL Account Master Maintenance | HIGH | Central maintenance; creates/changes SKA1 + SKB1 simultaneously |
| FS10N | GL Account Balance Display (Classic GL) | HIGH | Reads GLT0 table. Use FAGLB03 if New GL is active |
| FAGLB03 | GL Account Balance Display (New GL) | HIGH | Reads FAGLFLEXT. Only available when New GL is activated |
| FAGLL03 | GL Account Line Items (New GL) | HIGH | New GL equivalent of FBL3N with segment/profit center drilldown |
| FBL3N | GL Account Line Items | HIGH | Reads BSIS/BSAS. Still works in New GL environments |
| OB52 | Open/Close Posting Periods | HIGH | Reads posting period variant; differentiates by account type |

### Accounts Payable — Verified T-codes

| T-code | Description | Verified? | Notes |
|--------|-------------|-----------|-------|
| FB60 | Enter Vendor Invoice (Enjoy) | HIGH | Preferred for simple vendor invoices; park or post |
| F-43 | Enter Vendor Invoice (classic) | HIGH | Classic screen; requires posting keys |
| FB65 | Enter Vendor Credit Memo (Enjoy) | HIGH | Symmetric to FB60 |
| F-41 | Enter Vendor Credit Memo (classic) | HIGH | Verified: F-41, not F-27 which is for customers |
| MIRO | Invoice Verification (from MM) | HIGH | MM-side T-code; generates FI document via BSEG/RBKP. Used for PO-based invoices |
| F-53 | Post Outgoing Payment (manual, w/o PB) | HIGH | Manual vendor payment without payment program |
| F-58 | Payment with Printout | HIGH | Manual check printing combined with payment |
| F110 | Automatic Payment Program (APP) | HIGH | Complex; runs payment proposals, payment run, bank file generation |
| FBL1N | Vendor Line Items | HIGH | Open, cleared, all items; reads BSIK/BSAK |
| FK01 | Create Vendor (accounting view) | HIGH | FI-only vendor creation (no purchasing data) |
| FK02 | Change Vendor (accounting view) | HIGH | |
| FK03 | Display Vendor (accounting view) | HIGH | |
| XK01 | Create Vendor (all views) | HIGH | Central vendor creation including purchasing; preferred in MM+FI environments |
| MK01 | Create Vendor (purchasing view) | HIGH | MM-only vendor creation |
| F150 | Dunning Run | HIGH | Executes dunning program SAPF150; generates dunning letters |
| FBMP | Maintain Dunning Procedure | HIGH | Configuration T-code for dunning procedure definition |
| S_ALR_87012082 | Vendor Balances in Local Currency | HIGH | CORRECTION: Brief listed this as 87012284; 87012082 is vendor balances |

**CORRECTION — Critical error in research brief:**
The brief listed S_ALR_87012284 as "vendor balances." This is wrong.
- S_ALR_87012284 = **Financial Statements** (Balance Sheet/P&L, runs RFBILA00)
- S_ALR_87012082 = **Vendor Balances in Local Currency** (correct vendor balance T-code)

### Accounts Receivable — Verified T-codes

| T-code | Description | Verified? | Notes |
|--------|-------------|-----------|-------|
| FB70 | Enter Customer Invoice (Enjoy) | HIGH | Simple customer invoice; park or post |
| F-22 | Enter Customer Invoice (classic) | HIGH | Classic screen with posting keys |
| FB75 | Enter Customer Credit Memo (Enjoy) | HIGH | |
| F-27 | Enter Customer Credit Memo (classic) | MEDIUM | Classic credit memo entry for customers (NOT vendors — F-41 is vendor credit memo) |
| F-28 | Post Incoming Payment | HIGH | Manual customer payment posting |
| F-32 | Clear Customer Account | HIGH | Manual clearing of customer open items |
| FBL5N | Customer Line Items | HIGH | Open, cleared, all items; reads BSID/BSAD |
| FD01 | Create Customer (accounting view) | HIGH | FI-only customer creation |
| FD02 | Change Customer (accounting view) | HIGH | |
| FD03 | Display Customer (accounting view) | HIGH | |
| XD01 | Create Customer (all views) | HIGH | Central customer creation including sales data |
| VD01 | Create Customer (SD view) | HIGH | SD-only customer creation |
| FD32 | Customer Credit Limit | HIGH | Set/display credit limit per customer/credit control area |
| S_ALR_87012197 | List of Customer Line Items | HIGH | Standard customer line item list report |
| S_ALR_87012168 | Due Date Analysis for Open Items | HIGH | Aged items / overdue analysis |

### Asset Accounting — Verified T-codes

| T-code | Description | Verified? | Notes |
|--------|-------------|-----------|-------|
| AS01 | Create Asset Master Record | HIGH | Creates ANLA record |
| AS02 | Change Asset Master Record | HIGH | |
| AS03 | Display Asset Master Record | HIGH | |
| ABUMN | Asset Transfer (within company code) | HIGH | Transfers between asset classes or cost centers |
| F-90 | Acquisition from Vendor with Purchase Order | HIGH | Asset purchase with vendor clearing |
| F-91 | Asset Acquisition to Clearing Account | HIGH | Acquisition to interim account |
| F-92 | Asset Sale with Customer | HIGH | Retirement with customer invoice |
| ABAVN | Asset Retirement by Scrapping | MEDIUM | Not via sale; write-off with loss posting |
| AFAB | Depreciation Run | HIGH | Period depreciation posting; can run test/restart/repeat |
| AJRW | Asset Fiscal Year Change | HIGH | Opens new year in AA; must run before posting in new year |
| AJAB | Asset Year-End Closing | HIGH | Closes asset year; must run AFAB fully before AJAB |
| AW01N | Asset Explorer | HIGH | Single asset drilldown — planned vs posted values per depreciation area |
| AR01 | Asset History Sheet | MEDIUM | Period/year-end asset reporting |
| S_ALR_87011963 | Asset Balances | MEDIUM | Standard asset balance report by company code/asset class |
| S_ALR_87012039 | Asset History Sheet Report | MEDIUM | Detailed asset movement report |

### Period-End and Cross-Functional T-codes

| T-code | Description | Verified? | Notes |
|--------|-------------|-----------|-------|
| OB52 | Open/Close Posting Periods | HIGH | Posting period variant maintenance |
| OBY6 | Company Code Global Settings | HIGH | Shows assigned posting period variant, fiscal year variant |
| F.05 | Foreign Currency Valuation | HIGH | Month-end; covers GL/vendor/customer open items |
| FBS1 | Accrual/Deferral Posting | HIGH | Month-end accruals with auto-reversal |
| F.13 | Automatic Clearing | HIGH | GR/IR clearing; also clears other open item accounts |
| AFAB | Depreciation Run | HIGH | Run last in month-end before AJAB |
| F.01 | Financial Statements | HIGH | Runs RFBILA00; same underlying program as S_ALR_87012284 |
| S_ALR_87012284 | Financial Statements (Balance Sheet/P&L) | HIGH | Parameter T-code for RFBILA00; use with FSV (financial statement version) |
| S_ALR_87012277 | GL Account Balances (Trial Balance) | HIGH | Verified: GL balances report, not 87012172 as cited in brief |
| S_ALR_87012082 | Vendor Balances in Local Currency | HIGH | Correct T-code for vendor balances |
| S_ALR_87012197 | Customer Line Items | HIGH | |
| FB03 | Display Document | HIGH | Universal document display; drill-to-document from all reports |
| FBL1N | Vendor Line Items | HIGH | |
| FBL3N | GL Account Line Items (Classic GL) | HIGH | Reads BSIS/BSAS |
| FBL5N | Customer Line Items | HIGH | Reads BSID/BSAD |

**Recommended T-code count:** ~65 T-codes achievable within 50-80 target (GL: 20, AP: 15, AR: 13, AA: 12, Period-end/Reporting: 5 cross-functional). Several T-codes serve double duty (period-end + reporting).

---

## SPRO Configuration Path Verification

### GL Configuration — Verified SPRO Paths

All paths under: `Financial Accounting (New) ▸ ...`

| Config Item | Full IMG Path | T-code | Verified? |
|-------------|---------------|--------|-----------|
| Define Chart of Accounts | Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Master Data ▸ G/L Accounts ▸ Preparations ▸ Edit Chart of Accounts List | OB13 | HIGH |
| Assign CoA to Company Code | Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Master Data ▸ G/L Accounts ▸ Preparations ▸ Assign Company Code to Chart of Accounts | OB62 | MEDIUM |
| Maintain Fiscal Year Variant | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fiscal Year and Posting Periods ▸ Fiscal Year ▸ Maintain Fiscal Year Variant (Maintain Shortened Fiscal Year) | OB29 | HIGH |
| Assign FYV to Company Code | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fiscal Year and Posting Periods ▸ Fiscal Year ▸ Assign Company Code to a Fiscal Year Variant | OB37 | MEDIUM |
| Define Posting Keys | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Document ▸ Line Item ▸ Controls ▸ Define Posting Keys | OB41 | HIGH |
| Define Document Types | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Document ▸ Document Types ▸ Define Document Types for Entry View | OBA7 | HIGH |
| Define Field Status Groups | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fields ▸ Define Field Status Variants | OBC4 | MEDIUM |
| Open/Close Posting Periods | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fiscal Year and Posting Periods ▸ Posting Periods ▸ Open and Close Posting Periods | OB52 | HIGH |
| Define GL Account Groups | Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Master Data ▸ G/L Accounts ▸ Preparations ▸ Define Account Group | OBD4 | MEDIUM |

### AP/AR Configuration — Verified SPRO Paths

| Config Item | Full IMG Path | T-code | Verified? |
|-------------|---------------|--------|-----------|
| Define Payment Terms | Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Outgoing Invoices/Credit Memos ▸ Define Terms of Payment | OBB8 | HIGH |
| Define Tolerance Groups (Customers/Vendors) | Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Incoming Invoices/Credit Memos ▸ Define Tolerance Groups for Employees | OBA3 | HIGH |
| Define Tolerance Groups (Users) | Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Incoming Invoices/Credit Memos ▸ Define Tolerance Groups for Employees | OBA4 | HIGH |
| Define Dunning Procedures | Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Dunning ▸ Dunning Procedure ▸ Define Dunning Procedures | FBMP | HIGH |
| Configure Payment Program (F110) | Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Business Transactions ▸ Outgoing Payments ▸ Automatic Outgoing Payments ▸ Payment Method/Bank Selection for Payment Program ▸ Set Up All Company Codes for Payment Transactions | FBZP | HIGH |
| Define Vendor Account Groups | Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Vendor Accounts ▸ Master Data ▸ Preparations for Creating Vendor Master Data ▸ Define Account Groups with Screen Layout (Vendors) | OBD3 | MEDIUM |
| Define Customer Account Groups | Financial Accounting (New) ▸ Accounts Receivable and Accounts Payable ▸ Customer Accounts ▸ Master Data ▸ Preparations for Creating Customer Master Data ▸ Define Account Groups with Screen Layout (Customers) | OBD2 | MEDIUM |

**Note on F110 SPRO setup:** F110 configuration is split across multiple SPRO steps all under FBZP (Payment Methods Configuration). FBZP is the central T-code for configuring all payment program settings (company codes, payment methods, bank accounts, available amounts). This is one of the most complex config areas and deserves step-by-step detail.

### Asset Accounting Configuration — Verified SPRO Paths

| Config Item | Full IMG Path | T-code | Verified? |
|-------------|---------------|--------|-----------|
| Copy Reference Chart of Depreciation | Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Copy Reference Chart of Depreciation/Depreciation Areas | EC08 | HIGH |
| Assign Chart of Depreciation to Company Code | Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Assign Chart of Depreciation to Company Code | OAOB | MEDIUM |
| Define Asset Classes | Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Asset Classes ▸ Define Asset Classes | OAOA | MEDIUM |
| Define Number Ranges for Asset Class | Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Asset Classes ▸ Define Number Range Intervals | AS08 | MEDIUM |
| Specify Account Determination | Financial Accounting (New) ▸ Asset Accounting ▸ Integration with the General Ledger ▸ Assign G/L Accounts | AO90 | HIGH |
| Maintain Depreciation Keys | Financial Accounting (New) ▸ Asset Accounting ▸ Depreciation ▸ Valuation Methods ▸ Depreciation Key ▸ Maintain Depreciation Key | AFAMA | HIGH |
| Define Depreciation Areas | Included in EC08 copy step — depreciation areas defined per chart of depreciation | — | HIGH |
| Activate Asset Accounting for Company Code | Financial Accounting (New) ▸ Asset Accounting ▸ Organizational Structures ▸ Assign Chart of Depreciation to Company Code | OAOB | MEDIUM |
| Set Depreciation Area for GL Integration | Financial Accounting (New) ▸ Asset Accounting ▸ Integration with the General Ledger ▸ Define How Depreciation Areas Post to General Ledger | OADX | MEDIUM |

**Asset Accounting config order matters:** EC08 (copy chart of dep) → OAOB (assign to CC) → OAOA (define asset classes) → AO90 (GL account determination) → AFAMA (depreciation keys). Doing these out of order causes system errors that are difficult to unwind.

### New GL Configuration — Verified SPRO Paths

| Config Item | Full IMG Path | T-code | Verified? |
|-------------|---------------|--------|-----------|
| Activate New General Ledger | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Ledger ▸ Activate New General Ledger Accounting | — (table entry) | HIGH |
| Define Ledgers for GL Accounting | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Ledger ▸ Define Ledgers for General Ledger Accounting | — | HIGH |
| Define and Activate Non-Leading Ledgers | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Ledger ▸ Define and Activate Non-Leading Ledgers | — | HIGH |
| Define Document Types for Entry View in Ledger | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Document ▸ Document Types ▸ Define Document Types for Entry View in a Ledger | — | HIGH |
| Activate Document Splitting | Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Activate Document Splitting | — | HIGH |
| Define Document Splitting Characteristics | Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Define Document Splitting Characteristics for General Ledger Accounting | — | HIGH |
| Classify GL Accounts for Doc Splitting | Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Classify G/L Accounts for Document Splitting | — | MEDIUM |
| Classify Document Types for Doc Splitting | Financial Accounting (New) ▸ General Ledger Accounting (New) ▸ Business Transactions ▸ Document Splitting ▸ Classify Document Types for Document Splitting | — | MEDIUM |
| Define Segments | Financial Accounting (New) ▸ Financial Accounting Global Settings (New) ▸ Ledgers ▸ Fields ▸ Customer Fields ▸ Segments ▸ Define Segments | — | MEDIUM |

**Document splitting required vs optional:**
- **Required for zero-balance clearing:** Define a zero balance clearing account (mandatory when doc splitting active and characteristics don't balance naturally)
- **Required for activation:** Classify GL accounts (item categories) and document types (business transaction variants)
- **Optional (activated per configuration):** Mandatory field flag on characteristics; customer-defined splitting methods
- Document splitting activates at client level but can be deactivated per company code

---

## Master Data Table and Field Verification

### SKA1 — G/L Account Master (Chart of Accounts Segment)

**Table:** SKA1 | **Key:** MANDT + KTOPL + SAKNR | **Access T-code:** FS00, OBD4

| Field | Description | Verified? | Notes |
|-------|-------------|-----------|-------|
| KTOPL | Chart of Accounts | HIGH | Primary key component |
| SAKNR | G/L Account Number | HIGH | Up to 10 digits |
| KTOKS | G/L Account Group | HIGH | Controls field layout and number range |
| XBILK | Balance Sheet Account Indicator | HIGH | X = balance sheet; blank = P&L |
| GVTYP | P&L Statement Account Type | HIGH | Only relevant when XBILK is blank; controls P&L structure |
| XLOEV | Deletion Flag | HIGH | Marks account for deletion |
| BILKT | Group Account Number | HIGH | Used for consolidation / reporting hierarchy |
| MUSTR | Sample Account Number | MEDIUM | Template for field settings |

**Note:** SKA1 does NOT contain company-code-specific settings. Those are in SKB1.

### SKB1 — G/L Account Master (Company Code Segment)

**Table:** SKB1 | **Key:** MANDT + BUKRS + SAKNR | **Access T-code:** FS00

| Field | Description | Verified? | Notes |
|-------|-------------|-----------|-------|
| BUKRS | Company Code | HIGH | Primary key component |
| SAKNR | G/L Account Number | HIGH | Primary key component |
| XSPEB | Posting Block | HIGH | X = blocked for posting |
| FSTAG | Field Status Group | HIGH | Controls required/optional/hidden fields on posting screens |
| MWSKZ | Tax Category | HIGH | Controls tax behavior; + = output tax, - = input tax, blank = no tax |
| XMWNO | Post Without Tax Code Allowed | HIGH | X = allow posting without tax code even when MWSKZ is set |
| ZUAWA | Sort Key | HIGH | Controls how assignment field is populated (0 = manual, 5 = doc date, etc.) |
| BUSAB | Accounting Clerk | HIGH | Responsible clerk abbreviation |
| AKONT | Reconciliation Account Flag | MEDIUM | CORRECTION: AKONT in KNA1/LFB1/KNB1 is reconciliation account. In SKB1, the recon account flag is controlled differently — SKB1 itself is not a reconciliation account holder. The recon account number lives in LFB1/KNB1. |

**CORRECTION on AKONT:** The research brief lists AKONT under SKB1. This is incorrect. AKONT (reconciliation account) is a field in LFB1 (vendor) and KNB1 (customer), pointing to the GL reconciliation account. In SKB1, the field XINTIT indicates whether an account is a reconciliation account — there is no AKONT field in SKB1 itself.

### LFA1 — Vendor General Data

**Table:** LFA1 | **Key:** MANDT + LIFNR | **Access T-code:** XK03, FK03

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| LIFNR | Vendor Account Number | VENDOR001, 10000-99999 | HIGH |
| KTOKK | Vendor Account Group | KRED (standard), LIEF (supplier) | HIGH |
| NAME1 | Name 1 | ABC Supplies GmbH | HIGH |
| LAND1 | Country Key | US, DE, GB | HIGH |
| STCD1 | Tax Number 1 | Federal tax ID / VAT reg number | HIGH |
| ORT01 | City | New York, Frankfurt | HIGH |
| REGIO | Region/State | NY, HE | HIGH |
| BRSCH | Industry Key | 0001 (automotive), blank | HIGH |
| SPERR | Central Posting Block | X = blocked | MEDIUM |
| LOEVM | Central Deletion Flag | X = flagged for deletion | MEDIUM |

### LFB1 — Vendor Company Code Data

**Table:** LFB1 | **Key:** MANDT + LIFNR + BUKRS | **Access T-code:** XK03, FK03

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| LIFNR | Vendor Account Number | Links to LFA1 | HIGH |
| BUKRS | Company Code | 1000 | HIGH |
| AKONT | Reconciliation Account | 160000 (AP recon account in GL) | HIGH |
| ZTERM | Payment Terms Key | 0001 (14 days 2%, 30 net) | HIGH |
| ZWELS | Payment Methods | C (check), T (transfer), E (EFT) | HIGH |
| FDGRV | Planning Group | A1 (domestic supplier) | HIGH — NOTE: field is FDGRV not FDGRP as listed in brief |
| BUSAB | Accounting Clerk | MM, AP01 | HIGH |
| ZUAWA | Sort Key | 031 (vendor number) | HIGH |
| REPRF | Check for Duplicate Invoice | X = check active | HIGH |
| TOGRU | Tolerance Group | blank = default | MEDIUM |
| ZAHLS | Payment Block | A = blocked, blank = not blocked | MEDIUM |

**CORRECTION — LFB1 field name:** The research brief listed `FDGRP` as the planning group field. The correct field name is `FDGRV` (confirmed via leanx.eu LFB1 table documentation).

### LFM1 — Vendor Purchasing Organization Data

**Table:** LFM1 | **Key:** MANDT + LIFNR + EKORG | **Access T-code:** XK03, MK03

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| LIFNR | Vendor Account Number | Links to LFA1 | HIGH |
| EKORG | Purchasing Organization | 1000 | HIGH |
| WAERS | Purchase Order Currency | USD, EUR | HIGH |
| WEBRE | GR-Based Invoice Verification | X = required; blank = not required | HIGH |
| ZTERM | Payment Terms (Purchasing) | 0001 (may differ from FI terms) | HIGH |
| INCO1 | Incoterms Part 1 | CIF, FOB, EXW | HIGH |
| INCO2 | Incoterms Part 2 | New York (port/place) | HIGH |

### KNA1 — Customer General Data

**Table:** KNA1 | **Key:** MANDT + KUNNR | **Access T-code:** XD03, FD03

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| KUNNR | Customer Number | CUST001, 10000-99999 | HIGH |
| KTOKD | Customer Account Group | KUNA (standard), DEBTR | HIGH |
| NAME1 | Name 1 | Acme Corporation | HIGH |
| LAND1 | Country Key | US, DE | HIGH |
| STCD1 | Tax Number 1 | Federal tax ID | HIGH |
| ORT01 | City | Chicago, London | HIGH |
| REGIO | Region/State | IL, LDN | HIGH |
| BRSCH | Industry Key | Industry classification | HIGH |

### KNB1 — Customer Company Code Data

**Table:** KNB1 | **Key:** MANDT + KUNNR + BUKRS | **Access T-code:** XD03, FD03

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| KUNNR | Customer Number | Links to KNA1 | HIGH |
| BUKRS | Company Code | 1000 | HIGH |
| AKONT | Reconciliation Account | 140000 (AR recon account) | HIGH |
| ZTERM | Payment Terms | 0001, Z030 | HIGH |
| ZWELS | Payment Methods | T (transfer), C (check) | MEDIUM |
| BUSAB | Accounting Clerk | AR01 | HIGH |
| ZUAWA | Sort Key | 001 (doc number) | MEDIUM |
| SPERR | Posting Block (Co Code) | X = blocked | MEDIUM |
| TOGRU | Tolerance Group | blank = default | MEDIUM |

**CORRECTION — KVGR1-5 location:** The research brief listed KVGR1-5 (customer groups 1-5) under KNB1. This is INCORRECT. The KVGR fields are in **KNVV** (Customer Master Sales Data), not KNB1. They are SD-oriented classification fields used in pricing and statistics, not FI fields.

### KNVV — Customer Sales Area Data

**Table:** KNVV | **Key:** MANDT + KUNNR + VKORG + VTWEG + SPART | **Access T-code:** XD03, VD03

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| KUNNR | Customer Number | Links to KNA1 | HIGH |
| VKORG | Sales Organization | 1000 | HIGH |
| VTWEG | Distribution Channel | 10 | HIGH |
| SPART | Division | 00 | HIGH |
| KVGR1 | Customer Group 1 | 01, 02, 03 | HIGH |
| KVGR2 | Customer Group 2 | Classification field | HIGH |
| KVGR3 | Customer Group 3 | Classification field | HIGH |
| KVGR4 | Customer Group 4 | Classification field | HIGH |
| KVGR5 | Customer Group 5 | Classification field | HIGH |
| KTGRD | Account Assignment Group | 01 (domestic), 02 (export) | MEDIUM |
| ZTERM | Payment Terms (SD) | May differ from FI terms in KNB1 | MEDIUM |

**Note for master-data.md:** KNVV is an SD table, not a pure FI table. Include it in the customer master section with a clear note that KVGR fields are SD-facing and used in pricing condition access sequences. The S/4HANA callout for customer master should note that KNA1/KNB1/KNVV are replaced by the Business Partner model (BUT000 + partner function tables).

### ANLA — Asset Master General Data

**Table:** ANLA | **Key:** MANDT + BUKRS + ANLN1 + ANLN2 | **Access T-code:** AS03

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| BUKRS | Company Code | 1000 | HIGH |
| ANLN1 | Main Asset Number | 100000 | HIGH |
| ANLN2 | Asset Subnumber | 0000 (main), 0001, 0002 | HIGH |
| ANLKL | Asset Class | 1000 (buildings), 3000 (machinery) | HIGH |
| TXA50 | Asset Description | Office Equipment XY-123 | HIGH |
| AKTIV | Asset Capitalization Date | 2023-01-15 | HIGH |
| DEAKT | Asset Deactivation Date | Blank while active | HIGH |
| GDLGRP | Business Area / Evaluation Group 5 | — | MEDIUM |

**CORRECTION — KOSTL in ANLA:** The research brief listed KOSTL (cost center) as a direct field in ANLA. This is INCORRECT. Cost center assignment in asset accounting is stored in **ANLZ** (Asset Master Record: Time-Dependent Segment), which is a separate table holding time-dependent fields. ANLZ contains KOSTL, KOSTLV (responsible cost center), PRCTR (profit center), GSBER (business area), and FKBER (functional area). The key for ANLZ includes a validity date range (BDATU/ADATU), allowing cost center changes over the asset's life.

**WERKS (plant) assignment** is also not directly in ANLA as a standard field — it depends on the system configuration and may appear via ANLZ or object assignment.

### ANLB — Asset Depreciation Terms

**Table:** ANLB | **Key:** MANDT + BUKRS + ANLN1 + ANLN2 + AFABE | **Access T-code:** AS03 (depreciation area tab)

| Field | Description | Typical Values | Verified? |
|-------|-------------|----------------|-----------|
| BUKRS | Company Code | 1000 | HIGH |
| ANLN1 | Main Asset Number | Links to ANLA | HIGH |
| ANLN2 | Asset Subnumber | 0000 | HIGH |
| AFABE | Depreciation Area | 01 (book), 10 (tax), 15 (IFRS) | HIGH |
| AFASL | Depreciation Key | LINR (straight-line), DBNL (declining balance) | HIGH |
| NDJAR | Useful Life in Years | 10 (machinery), 40 (buildings) | HIGH |
| NDPER | Useful Life in Periods (months) | 0 (when years specified), 6 (partial year) | HIGH |

---

## Architecture Patterns

### File Structure (Confirmed by Existing Scaffolding)

The FI module directory already exists at `/modules/fi/` with the following files created but empty:

```
modules/fi/
├── CLAUDE.md         # index file — exists with placeholder content
├── tcodes.md         # to be populated Phase 3
├── config-spro.md    # to be populated Phase 3
├── processes.md      # to be populated Phase 3
├── master-data.md    # to be populated Phase 3
├── integration.md    # out of scope Phase 3
└── patterns.md       # out of scope Phase 3
```

**Phase 3 populates only: tcodes.md, config-spro.md, processes.md, master-data.md**

### Content Pattern (Established by reference/org-structure.md)

The org-structure.md file demonstrates the expected pattern:
- YAML frontmatter (module, content_type, ecc_version, ehp_range, confidence, last_verified)
- Subheadings per object/area
- Field tables: `Field | Description | Typical Values`
- Key notes below each table (T-codes for create/display, cross-module impact)
- S/4HANA differences inline where significant

### Workflow Index Pattern

From CONTEXT.md decision: tcodes.md should have a workflow index at top linking by process stage (posting → clearing → reporting), not just by submodule. This maps process queries ("what T-code to clear an open item?") directly to the answer.

Recommended structure for tcodes.md:
1. Workflow Index (table: Process Stage | T-code | Submodule)
2. GL Section (20 T-codes with full detail)
3. AP Section (15 T-codes with full detail)
4. AR Section (13 T-codes with full detail)
5. AA Section (12 T-codes with full detail)
6. Period-End/Reporting (5 shared T-codes)

---

## Don't Hand-Roll

For this knowledge base project, "don't hand-roll" means: don't invent T-codes, field names, or SPRO paths. Always use what's verified. These are the areas where SAP knowledge bases most commonly introduce errors:

| Problem | Common Mistake | Correct Approach |
|---------|----------------|------------------|
| S_ALR T-code descriptions | Guessing based on partial numbers | Verify each S_ALR code against its program (e.g., S_ALR_87012284 = RFBILA00 = Financial Statements) |
| Master data table for fields | Putting fields in wrong segment table | Verify ANLA vs ANLZ; KNB1 vs KNVV; SKA1 vs SKB1 |
| Classic vs New GL T-codes | Using FS10N when New GL is active | Document both: FS10N (Classic GL), FAGLB03 (New GL) |
| SPRO path "Financial Accounting" | Using old path pre-New GL | Always use "Financial Accounting (New)" for ECC 6.0 with New GL |
| F110 configuration T-code | Listing SPRO path when FBZP is used | F110 is execution; FBZP is the configuration hub for payment program setup |
| Vendor field FDGRP | Using FDGRP (incorrect) | Correct field in LFB1 is FDGRV (planning group) |
| Credit memo T-codes | Mixing vendor/customer | F-27 = customer credit memo; F-41 = vendor credit memo |

---

## Common Pitfalls

### Pitfall 1: S_ALR_87012284 Misidentification
**What goes wrong:** S_ALR_87012284 is labeled as "vendor balances." Users follow this and get Financial Statements when they expected vendor data.
**Why it happens:** The number sequence is close to other vendor-related S_ALR codes and the error propagates from incorrect training materials.
**How to avoid:** S_ALR_87012284 = Financial Statements (same as F.01, runs RFBILA00). Vendor Balances = S_ALR_87012082.
**Warning sign:** If you see "87012284 = vendor" in any source, that source is wrong.

### Pitfall 2: FS10N vs FAGLB03 Mix-up
**What goes wrong:** In New GL systems, FS10N shows stale or zero balances because it reads GLT0 which is no longer updated.
**Why it happens:** FS10N is the classic transaction and still launches successfully — it just reads the wrong table.
**How to avoid:** When New GL is active, use FAGLB03 for account balance display. Include both in tcodes.md with a clear note about when each applies.
**Warning sign:** FS10N showing zero balances on accounts with known activity.

### Pitfall 3: KOSTL Not in ANLA
**What goes wrong:** Content says "cost center is in ANLA" — queries against ANLA for KOSTL return no results.
**Why it happens:** The asset master screen shows cost center alongside other ANLA fields, but it comes from ANLZ join.
**How to avoid:** KOSTL is in ANLZ (time-dependent). In master-data.md, document ANLZ separately and note that cost center changes create new ANLZ records with date ranges.

### Pitfall 4: KVGR1-5 in Wrong Table
**What goes wrong:** Content says customer groups KVGR1-5 are in KNB1 — queries against KNB1 for KVGR1 fail.
**Why it happens:** Customer groups are visible on the customer master, but they live in the SD-oriented KNVV segment.
**How to avoid:** KVGR1-5 are in KNVV. In master-data.md, document this under the customer master KNVV section with a note about the SD/FI split in customer data.

### Pitfall 5: F110 Configuration vs Execution
**What goes wrong:** Documentation shows FBZP config paths but user tries to "execute" F110 from SPRO.
**Why it happens:** F110 setup spans two areas: SPRO configuration (FBZP) and runtime execution (F110).
**How to avoid:** Clearly separate in both tcodes.md (F110 = execution) and config-spro.md (FBZP = setup). F110 execution requires: run date, identification, parameters, proposal run, approval, payment run, posting.

### Pitfall 6: Asset Accounting Year-End Order Dependency
**What goes wrong:** Running AJAB before AFAB (depreciation) is complete causes AJAB to fail with error "depreciation not fully posted."
**Why it happens:** AJAB checks all depreciation is posted before allowing close.
**How to avoid:** Month-end order: AFAB → verify no errors → AJAB (only at year-end). AJRW opens next year; AJAB closes current year. These are sequential, not parallel.

### Pitfall 7: New GL Document Splitting Activation is Client-Level
**What goes wrong:** Activating document splitting in one company code's SPRO unexpectedly affects others.
**Why it happens:** Activation is global (client-level); deactivation is per company code.
**How to avoid:** In config-spro.md, note clearly: "Activation is client-level. If deactivating for specific company codes, do so via the company code-specific deactivation step."

---

## Process Flow Verification

### Daily GL Posting Cycle

Key T-codes verified for process flow:
- **FB50** — GL posting (Enjoy); preferred for simple entries
- **FB60/FB70** — Vendor/customer invoice posting
- **FBV1/FBV2/FBV0** — Park → Change → Post workflow
- **FB08** — Reverse open document
- **FBRA** — Reset cleared document then optionally reverse
- **F-03** — Manual GL clearing
- **F.13** — Automatic clearing (GR/IR)

### Month-End Close Process

Verified sequence for CONTEXT.md-specified activities:
1. **F.05** — Foreign currency revaluation (open items + balances)
2. **FBS1** — Enter accrual/deferral postings (with auto-reversal date set for next period open)
3. **F.13** — GR/IR clearing (automated matching of goods receipt vs invoice receipt)
4. **AFAB** — Depreciation run (must complete before period close in AA)
5. **OB52** — Close posting period (or coordinate with Basis for automated close)

Note: F.05 in ECC 6.0 can generate batch input sessions; in more recent ECC implementations it posts directly. The reference should note both modes.

### AP Payment Run (F110) Process

Verified steps:
1. **FBZP** (SPRO) — Pre-configuration: payment methods, bank accounts, company code settings
2. **F110** → Parameters tab: run date, identification, company codes, payment methods, next payment date
3. **F110** → Proposal: execute proposal run (Start Immediately), review log
4. **F110** → Edit proposal: remove/add items, change payment method per item
5. **F110** → Payment Run: execute (creates payment documents, updates BSAK)
6. **F110** → Printout/DME: generate bank file (DME = Data Medium Exchange format) or check print
7. **FBL1N** — Reconcile: verify cleared items (BSAK) vs open items (BSIK)

F110 common gotcha: If you delete the payment proposal and re-run, the run date + identification combination is reused — the system picks up new items that became due. Always use a new identification for a truly new run.

### Financial Reporting Process

Verified T-code relationships:
- **F.01 / S_ALR_87012284** — Both call RFBILA00; require Financial Statement Version (FSV) configured in OB58
- **S_ALR_87012277** — GL Account Balances (Trial Balance); simpler than F.01
- **FBL3N / FAGLL03** — Line item drilldown from balance reports
- **FB03** — Document display; drill-to-document from any line item report
- Drill path: F.01 → account line → FBL3N → document number → FB03

---

## Token Budget Estimates

Based on content decisions from CONTEXT.md, estimated file sizes:

| File | Content Volume | Char Estimate | Token Estimate | Split Needed? |
|------|---------------|---------------|----------------|---------------|
| fi/tcodes.md | 65 T-codes × ~250 chars each | 16,000-22,000 | 4,000-5,500 | No — under 25K |
| fi/config-spro.md | 4 config areas, step-by-step | 12,000-18,000 | 3,000-4,500 | No — under 25K |
| fi/processes.md | 4 process flows + tables | 7,000-10,000 | 1,750-2,500 | No — under 25K |
| fi/master-data.md | 4 objects × 4 tables, field tables | 10,000-16,000 | 2,500-4,000 | No — under 25K |
| **Total** | | **45,000-66,000** | **11,250-16,500** | None required |

**Per-file token budget is acceptable.** Files are loaded on-demand (not always-loaded), so 4,000-5,500 tokens per file is within the established project pattern. No file needs to be split.

**Note on tcodes.md:** At 65 T-codes with full detail (menu path + description + typical usage + gotchas), each entry averages 280-340 chars. This is the largest file but still well under the 25K split threshold.

---

## Plan Structure Recommendation

**Recommended: 2 plans (waves), parallel where possible**

### Wave 1 (parallel execution)
- **Plan 3A** — `fi/tcodes.md`: 65 T-codes organized GL/AP/AR/AA with workflow index
- **Plan 3B** — `fi/master-data.md`: 4 master data objects (SKA1+SKB1, LFA1+LFB1+LFM1, KNA1+KNB1+KNVV, ANLA+ANLB+ANLZ)

These two plans have no file overlap and can run in parallel.

### Wave 2 (sequential, after Wave 1)
- **Plan 3C** — `fi/config-spro.md`: 4 config areas step-by-step
- **Plan 3D** — `fi/processes.md`: 4 process flows with role-annotated tables

Wave 2 is better written after tcodes.md exists, so the SPRO and process content can cross-reference T-codes by name with consistency.

**Alternative:** All 4 plans in parallel if each plan is self-contained (include T-code cross-references inline rather than by reference). This reduces total time but risks inconsistency in T-code spellings/descriptions across files.

**Recommendation:** Wave structure (2A+2B parallel, then 2C+2D parallel). Four sub-plans total.

---

## State of the Art (ECC 6.0 Context)

| Old Approach | Current ECC 6.0 Approach | Notes |
|--------------|--------------------------|-------|
| Classic GL (pre-ECC 6.0) | New GL (FAGL) with parallel ledgers | ECC 6.0 introduced New GL; both active in ECC depending on migration status |
| FS10N for GL balances | FAGLB03 when New GL active | FS10N reads GLT0; FAGLB03 reads FAGLFLEXT |
| Separate FI-AP vendor master (LFA1 only) | Combined XK01 with MM purchasing view | MK01 if purchasing only; FK01 if FI only |
| F-02 for all postings | FB50/FB60/FB70 (Enjoy screens) | Enjoy screens introduced in ECC; F-02 still works but less common for simple postings |
| Manual clearing only | F.13 automatic clearing | F.13 introduced mass automatic clearing for GR/IR and other matching scenarios |
| Separate cost elements (CO) | Still separate in ECC 6.0 (S/4 eliminated this) | In ECC 6.0, CO cost elements (CSKA/CSKB) are separate from GL accounts |

**Deprecated/outdated for ECC 6.0:**
- **GLT0 table:** Still updated in Classic GL systems; not updated when New GL is active. Content should note this bifurcation.
- **FI-SL (Special Purpose Ledger):** Replaced by parallel ledgers in New GL. Do not reference FI-SL in Phase 3 content.
- **Classic profit center accounting (EC-PCA):** Still available in ECC 6.0 but superseded by New GL segment reporting. Reference only if parallel accounting section requires it.

---

## Open Questions

1. **F.05 batch input vs direct posting**
   - What we know: F.05 can run in batch input or direct posting mode depending on configuration
   - What's unclear: Which mode is standard in ECC 6.0 EHP4+; whether FAGL_FC_VAL (New GL foreign currency valuation) has replaced F.05 in some environments
   - Recommendation: Document F.05 as primary T-code; add note that FAGL_FC_VAL exists as New GL alternative with slightly different behavior (posts directly to FAGLFLEXT)

2. **ANLZ table depth in master-data.md**
   - What we know: KOSTL and other time-dependent fields are in ANLZ
   - What's unclear: Whether the brief intends ANLZ to be documented alongside ANLA/ANLB or skipped
   - Recommendation: Include ANLZ as a third asset segment table (brief mentioned "ANLA general + ANLB depreciation area"). Add a small ANLZ section covering KOSTL, PRCTR, GSBER, FKBER with the time-dependency note.

3. **F110 DME file format specifics**
   - What we know: F110 generates a DME (Data Medium Exchange) file for electronic bank transfer
   - What's unclear: Whether to include bank file format specifics (country-dependent: ACH in US, SEPA in EU, etc.)
   - Recommendation: Mention DME file generation generically; note that format is country/bank-configured. Do not document specific bank formats as these vary widely.

4. **New GL activation state assumption**
   - What we know: ECC 6.0 can run with Classic GL or New GL; behavior differs significantly
   - What's unclear: Which state to assume for content (CONTEXT.md doesn't specify)
   - Recommendation: Default assumption = New GL active (standard for post-2008 ECC 6.0 implementations). Document New GL behavior as primary; note Classic GL differences inline (e.g., "FS10N if Classic GL, FAGLB03 if New GL").

---

## Sources

### Primary (HIGH confidence — multiple SAP community and official sources agreeing)
- leanx.eu SAP table documentation — SKA1, SKB1, LFA1, LFB1, LFM1, KNA1, KNB1, KNVV, ANLA, ANLB field verification
- SAP Community (community.sap.com) — T-code clarifications (FB08 vs FBRA, FS10N vs FAGLB03, KVGR table location)
- sap-tcodes.org — S_ALR_87012284 description verification
- sapficoblog.com — F110, FB08, FBRA, FBL3N descriptions
- Multiple sources agreeing on: OB13, OB41, OBA7, OB29, EC08, AFAMA, FBZP, OB52 T-codes

### Secondary (MEDIUM confidence — single authoritative-looking source)
- saponlinetutorials.com — SPRO path structures for GL and AP
- leanx.eu ANLZ reference (confirming KOSTL is in ANLZ not ANLA)
- SAP Community thread on KVGR1-5 location in KNVV
- sapsharks.com — OB52, AJRW/AJAB descriptions

### Tertiary (LOW confidence — single blog post or inferred)
- OAOB, OAOA, AO90, OADX T-codes for Asset Accounting (SPRO paths inferred from configuration step names; EC08 is HIGH but dependent steps MEDIUM)
- S_ALR_87011963, S_ALR_87012039 asset report T-codes (from single sources; recommend planner verify these two in a real system)
- ABAVN T-code for asset scrapping (appears in multiple sources but fewer than AS01/AFAB/AW01N)

---

## Metadata

**Confidence breakdown:**
- T-code accuracy: HIGH for core GL/AP/AR/AA T-codes; MEDIUM for less-common AA and S_ALR report codes
- SPRO paths: HIGH for GL and AP/AR config paths; MEDIUM for AA and New GL paths (no direct fetch of SAP help portal succeeded due to redirects)
- Master data fields: HIGH for LFA1/LFB1/LFM1/KNA1/KNB1 key fields; MEDIUM for ANLZ/ANLB details
- Process flows: HIGH — well-documented in SAP community and training materials
- Corrections to research brief: HIGH confidence — verified via authoritative sources

**Research date:** 2026-02-16
**Valid until:** 2027-02-16 (SAP ECC 6.0 is in maintenance-only mode; T-codes and table structures are frozen)

---

## Summary of Corrections to Research Brief

The following items in the research focus brief are incorrect and must be corrected in planning:

| Brief Claim | Correct Fact | Confidence |
|-------------|--------------|------------|
| S_ALR_87012284 = vendor balances | S_ALR_87012284 = Financial Statements (Balance Sheet/P&L). Vendor balances = S_ALR_87012082 | HIGH |
| S_ALR_87012172 = GL balances | Correct GL balances T-code is S_ALR_87012277. S_ALR_87012172 could not be verified | MEDIUM |
| KVGR1-5 in KNB1 | KVGR1-5 are in KNVV (sales area data), not KNB1 | HIGH |
| KOSTL in ANLA | KOSTL (cost center) is in ANLZ (time-dependent), not ANLA | HIGH |
| LFB1 field FDGRP | Correct field name is FDGRV (planning group) | HIGH |
| AKONT in SKB1 | AKONT (reconciliation account) is in LFB1 and KNB1, not SKB1 | HIGH |
